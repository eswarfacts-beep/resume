"""
TalentIQ AI - Authentication & Role-Based Access Control Module
Provides enterprise-grade authentication, bcrypt password hashing, input validation,
rate-limiting, password recovery, and strict role-based authorization for User & Admin portals.
"""

import re
import time
import bcrypt
import datetime
from typing import Dict, Any, Optional, Tuple
import streamlit as st

from src.database import (
    init_db,
    get_user_by_email,
    get_user_by_id,
    create_user,
    record_login_success,
    record_login_failure,
    is_account_locked,
    create_password_reset_code,
    verify_and_use_reset_code,
    log_audit_event,
    update_user_profile
)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Demo user credentials map for backward compatibility and test evaluations
DEMO_USERS = {
    "recruiter": {
        "password": "talentiq2026",
        "name": "Sarah Jenkins",
        "role": "Lead Talent Partner",
        "email": "sarah.jenkins@talentiq.ai"
    },
    "admin": {
        "password": "Admin@TalentIQ2026",
        "name": "System Administrator",
        "role": "admin",
        "email": "admin@talentiq.ai"
    },
    "user": {
        "password": "User@TalentIQ2026",
        "name": "Sarah Jenkins (Recruiter)",
        "role": "user",
        "email": "user@talentiq.ai"
    }
}

DEMO_ALIASES = {
    "recruiter": "sarah.jenkins@talentiq.ai",
    "admin": "admin@talentiq.ai",
    "user": "user@talentiq.ai"
}


def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt with 12 salt rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Enforces strong password policy:
    - Minimum 8 characters
    - At least one alphabet character
    - At least one numeric digit
    """
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, "Password meets security requirements."


def validate_email_format(email: str) -> bool:
    """Validates RFC standard email syntax."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def init_auth_state():
    """Initializes and verifies authentication state against SQLite database."""
    init_db()

    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "current_user" not in st.session_state:
        st.session_state.current_user = None

    if "role" not in st.session_state:
        st.session_state.role = None

    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "landing"

    # Strict Session Tamper Verification:
    # If the session claims to be authenticated, verify against DB that user exists and is active
    if st.session_state.get("is_authenticated") and st.session_state.get("current_user"):
        user_info = st.session_state.current_user
        uid = user_info.get("id")
        if uid:
            db_user = get_user_by_id(uid)
            if not db_user or db_user["is_active"] != 1:
                # User was deactivated or deleted
                sign_out_user()
            else:
                # Sync verified role from database to prevent state tampering
                st.session_state.role = db_user["role"]
                st.session_state.current_user["role"] = db_user["role"]
                st.session_state.current_user["name"] = db_user["full_name"]


def authenticate_user(
    email_or_user: str,
    password: str,
    expected_role: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticates user credentials against the persistent SQLite database.
    Enforces account lockouts, bcrypt verification, active status, and role checking.
    """
    clean_input = email_or_user.strip().lower() if email_or_user else ""
    clean_pass = password.strip() if password else ""

    if not clean_input:
        return False, "Username or email is required.", None
    if not clean_pass:
        return False, "Password is required.", None

    # Resolve demo usernames/aliases to emails
    lookup_email = DEMO_ALIASES.get(clean_input, clean_input)

    # Check for active lockout
    is_locked, lock_msg = is_account_locked(lookup_email)
    if is_locked:
        log_audit_event(None, lookup_email, "LOGIN_BLOCKED", "Account locked due to excessive failed attempts.", "BLOCKED")
        return False, lock_msg, None

    user = get_user_by_email(lookup_email)

    # Check DEMO_USERS fallback/auto-provisioning
    if not user:
        demo_match = None
        for k, prof in DEMO_USERS.items():
            if clean_input == k or clean_input == prof["email"].lower():
                demo_match = (k, prof)
                break
        if demo_match:
            k, prof = demo_match
            if clean_pass == prof["password"]:
                # Auto-provision this user into SQLite with bcrypt
                from src.database import create_user
                pwd_h = hash_password(prof["password"])
                assigned_role = "admin" if prof.get("role") == "admin" else "user"
                create_user(prof["email"], pwd_h, prof["name"], role=assigned_role, is_active=1)
                user = get_user_by_email(prof["email"])

    if not user:
        record_login_failure(lookup_email)
        log_audit_event(None, lookup_email, "LOGIN_FAILED", "User not found.", "FAILED")
        return False, "Invalid credentials.", None

    if user["is_active"] != 1:
        log_audit_event(user["id"], lookup_email, "LOGIN_FAILED", "Account deactivated.", "INACTIVE")
        return False, "Your account has been deactivated. Please contact a system administrator.", None

    # Verify bcrypt hash
    if not verify_password(clean_pass, user["password_hash"]):
        record_login_failure(lookup_email)
        log_audit_event(user["id"], lookup_email, "LOGIN_FAILED", "Password mismatch.", "FAILED")
        return False, "Invalid credentials.", None

    # Role-Based Portal Verification
    user_role = user["role"]
    if expected_role:
        if expected_role == "admin" and user_role != "admin":
            log_audit_event(
                user["id"],
                lookup_email,
                "UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT",
                "Non-admin user attempted to log in via Admin Portal.",
                "DENIED"
            )
            return False, "Access Denied: This account does not possess Administrator privileges. Please use the User Login Portal.", None

    # Success: Reset failure count and log event
    record_login_success(user["id"])
    log_audit_event(user["id"], lookup_email, "LOGIN_SUCCESS", f"Portal: {expected_role or user_role}", "SUCCESS")

    user_record = {
        "id": user["id"],
        "username": clean_input,
        "email": user["email"],
        "name": user["full_name"],
        "role": user["role"],
        "created_at": user["created_at"],
        "last_login": user.get("last_login")
    }
    return True, "Authentication successful.", user_record


def register_user(
    email: str,
    password: str,
    confirm_password: str,
    full_name: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Registers a new regular user with role 'user'.
    Enforces email syntax, password matching, complexity requirements, and uniqueness.
    """
    clean_email = email.strip().lower() if email else ""
    clean_name = full_name.strip() if full_name else ""

    if not clean_email or not validate_email_format(clean_email):
        return False, "Please enter a valid email address.", None

    if not clean_name:
        return False, "Full name is required.", None

    if password != confirm_password:
        return False, "Passwords do not match. Please re-enter.", None

    valid_pass, pass_err = validate_password_strength(password)
    if not valid_pass:
        return False, pass_err, None

    # Check if user already exists
    existing = get_user_by_email(clean_email)
    if existing:
        return False, "An account with this email address already exists. Please sign in.", None

    # Hash with bcrypt and insert
    pwd_hash = hash_password(password)
    ok, msg, user_dict = create_user(
        email=clean_email,
        password_hash=pwd_hash,
        full_name=clean_name,
        role="user",
        is_active=1
    )
    return ok, msg, user_dict


def request_password_reset(email: str) -> Tuple[bool, str, Optional[str]]:
    """
    Initiates password recovery for an account.
    Returns (success, message, verification_code).
    """
    clean_email = email.strip().lower() if email else ""
    if not clean_email or not validate_email_format(clean_email):
        return False, "Please enter a valid email address.", None

    code = create_password_reset_code(clean_email)
    if not code:
        # Return generic success message to prevent user enumeration
        return True, "If an account exists for this email, a verification code has been generated.", None

    return True, "Verification reset code generated successfully.", code


def complete_password_reset(
    email: str,
    code: str,
    new_password: str,
    confirm_password: str
) -> Tuple[bool, str]:
    """Validates verification reset code and updates password."""
    clean_email = email.strip().lower() if email else ""
    clean_code = code.strip().upper() if code else ""

    if not clean_email or not clean_code:
        return False, "Email and verification code are required."

    if new_password != confirm_password:
        return False, "Passwords do not match."

    valid_pass, pass_err = validate_password_strength(new_password)
    if not valid_pass:
        return False, pass_err

    new_hash = hash_password(new_password)
    return verify_and_use_reset_code(clean_email, clean_code, new_hash)


def sign_in_user(user_record: Dict[str, Any]):
    """Activates authenticated session for user and loads user-isolated data."""
    st.session_state.is_authenticated = True
    st.session_state.current_user = user_record
    st.session_state.role = user_record.get("role", "user")
    st.session_state.auth_view = None

    # Switch default landing nav based on role
    if st.session_state.role == "admin":
        st.session_state.admin_nav = "Admin Overview"
    else:
        st.session_state.current_nav = "Dashboard"

    # Synchronize candidate pool for this specific user
    from src.storage import sync_user_data_on_login
    sync_user_data_on_login(user_record.get("id"))


def sign_out_user():
    """Terminates active session and resets memory state safely."""
    curr = st.session_state.get("current_user")
    if curr and curr.get("id"):
        log_audit_event(curr.get("id"), curr.get("email"), "LOGOUT", "User signed out.", "SUCCESS")

    st.session_state.is_authenticated = False
    st.session_state.current_user = None
    st.session_state.role = None
    st.session_state.auth_view = "landing"

    # Reset candidates and active screening memory
    from src.storage import clear_all_candidates
    clear_all_candidates()


def get_current_user() -> Dict[str, Any]:
    """Returns currently active user record or safe placeholder."""
    init_auth_state()
    return st.session_state.get("current_user") or {
        "id": None,
        "name": "Guest Visitor",
        "role": "guest",
        "email": "guest@talentiq.ai"
    }


def is_authenticated() -> bool:
    """Returns True if the current session has a validated active user."""
    init_auth_state()
    return bool(st.session_state.get("is_authenticated") and st.session_state.get("current_user"))


def require_role(required_role: str) -> bool:
    """
    Strict backend authorization barrier.
    Validates that the current active user possesses the exact required role.
    If unauthorized, logs an audit alert and returns False.
    """
    if not is_authenticated():
        return False
    curr = st.session_state.get("current_user")
    if not curr:
        return False

    actual_role = curr.get("role")
    if actual_role != required_role:
        log_audit_event(
            curr.get("id"),
            curr.get("email"),
            "AUTHORIZATION_VIOLATION",
            f"Required: {required_role}, Possessed: {actual_role}",
            "DENIED"
        )
        return False

    # Also verify role in SQLite database to prevent memory tampering
    db_user = get_user_by_id(curr.get("id"))
    if not db_user or db_user["role"] != required_role or db_user["is_active"] != 1:
        log_audit_event(
            curr.get("id"),
            curr.get("email"),
            "AUTHORIZATION_DATABASE_MISMATCH",
            "Session role does not match persistent database role.",
            "DENIED"
        )
        sign_out_user()
        return False

    return True
