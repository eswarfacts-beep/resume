"""
TalentIQ AI - Persistent Database & Role-Based Access Control Module
Provides SQLite-backed persistence for Users, Roles, Audit Logs, Resumes, Jobs,
and Screenings with parameterized queries, bcrypt hash validation, and data isolation.
"""

import os
import sqlite3
import json
import time
import datetime
import secrets
from typing import Dict, List, Any, Optional, Tuple

DB_FILENAME = "talentiq.db"


def get_db_path() -> str:
    """Returns the absolute path to the SQLite database file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, DB_FILENAME)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a thread-safe connection to the SQLite database with row factory and WAL mode."""
    target_path = db_path or get_db_path()
    conn = sqlite3.connect(target_path, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    return conn


def init_db(db_path: Optional[str] = None):
    """Initializes the database schema and provisions initial admin & seed data if needed."""
    conn = get_db_connection(db_path)
    with conn:
        # 1. Users Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TEXT
            );
        """)

        # 2. Jobs Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                department TEXT NOT NULL,
                min_experience REAL NOT NULL,
                required_skills_json TEXT NOT NULL,
                description TEXT NOT NULL,
                created_by INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );
        """)

        # 3. Resumes Table (isolated per user)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT NOT NULL,
                contact_email TEXT,
                contact_phone TEXT,
                raw_text TEXT NOT NULL,
                parsed_data_json TEXT NOT NULL,
                skills_json TEXT NOT NULL,
                years_of_experience REAL DEFAULT 0.0,
                shortlisted INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Indexed',
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 4. Screenings Table (isolated per user)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS screenings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id TEXT NOT NULL,
                job_title TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                composite_score REAL NOT NULL,
                skill_score REAL NOT NULL,
                semantic_score REAL NOT NULL,
                matched_skills_count INTEGER NOT NULL,
                missing_skills_count INTEGER NOT NULL,
                recommendation TEXT,
                screened_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 5. Audit Logs Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_email TEXT,
                action TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'SUCCESS',
                timestamp TEXT NOT NULL
            );
        """)

        # 6. Password Resets Table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                reset_code TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0
            );
        """)

    # Seed initial jobs if empty
    _seed_default_jobs(conn)

    # Provision initial accounts if needed
    _provision_initial_accounts(conn)

    conn.close()


def _seed_default_jobs(conn: sqlite3.Connection):
    """Seeds default job descriptions if jobs table is empty."""
    cursor = conn.execute("SELECT COUNT(*) FROM jobs;")
    count = cursor.fetchone()[0]
    if count == 0:
        from src.storage import DEFAULT_JOBS
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for job in DEFAULT_JOBS:
            conn.execute(
                """
                INSERT OR IGNORE INTO jobs 
                (id, title, department, min_experience, required_skills_json, description, created_by, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?);
                """,
                (
                    job["id"],
                    job["title"],
                    job["department"],
                    float(job.get("min_experience", 2.0)),
                    json.dumps(job.get("required_skills", [])),
                    job["description"],
                    None,
                    now_str
                )
            )
        conn.commit()


def _hash_password_internal(password: str) -> str:
    """Internal helper to hash passwords using bcrypt."""
    import bcrypt
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def _provision_initial_accounts(conn: sqlite3.Connection):
    """Provisions default Admin and User accounts with bcrypt hashing if none exist."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if admin exists
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';")
    admin_count = cursor.fetchone()[0]
    if admin_count == 0:
        admin_email = os.environ.get("TALENTIQ_ADMIN_EMAIL", "admin@talentiq.ai").strip().lower()
        admin_password = os.environ.get("TALENTIQ_ADMIN_PASSWORD", "Admin@TalentIQ2026")
        admin_hash = _hash_password_internal(admin_password)

        conn.execute(
            """
            INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
            VALUES (?, ?, ?, 'admin', 1, ?);
            """,
            (admin_email, admin_hash, "System Administrator", now_str)
        )
        # Log provisioning event
        conn.execute(
            """
            INSERT INTO audit_logs (user_id, user_email, action, details, status, timestamp)
            VALUES (1, ?, 'PROVISION_ADMIN', 'Initial administrator provisioned securely with bcrypt.', 'SUCCESS', ?);
            """,
            (admin_email, now_str)
        )
        conn.commit()

    # Check if demo user exists
    cursor = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'user';")
    user_count = cursor.fetchone()[0]
    if user_count == 0:
        user_email = "user@talentiq.ai"
        user_password = "User@TalentIQ2026"
        user_hash = _hash_password_internal(user_password)

        conn.execute(
            """
            INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
            VALUES (?, ?, ?, 'user', 1, ?);
            """,
            (user_email, user_hash, "Sarah Jenkins (Recruiter)", now_str)
        )

        # Also provision recruiter alias for backwards compatibility
        recruiter_email = "sarah.jenkins@talentiq.ai"
        recruiter_hash = _hash_password_internal("talentiq2026")
        conn.execute(
            """
            INSERT OR IGNORE INTO users (email, password_hash, full_name, role, is_active, created_at)
            VALUES (?, ?, ?, 'user', 1, ?);
            """,
            (recruiter_email, recruiter_hash, "Sarah Jenkins", now_str)
        )
        conn.commit()


# ==============================================================================
# USER MANAGEMENT & AUTHENTICATION CRUD
# ==============================================================================

def create_user(
    email: str,
    password_hash: str,
    full_name: str,
    role: str = "user",
    is_active: int = 1,
    conn: Optional[sqlite3.Connection] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Creates a new user record in the database."""
    email_clean = email.strip().lower()
    if role not in ("user", "admin"):
        return False, "Invalid role specified. Must be 'user' or 'admin'.", None

    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor = conn.execute(
            """
            INSERT INTO users (email, password_hash, full_name, role, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (email_clean, password_hash, full_name.strip(), role, is_active, now_str)
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Log audit
        log_audit_event(user_id, email_clean, "USER_REGISTERED", f"Role: {role}", "SUCCESS", conn)

        user_dict = {
            "id": user_id,
            "email": email_clean,
            "full_name": full_name.strip(),
            "role": role,
            "is_active": is_active,
            "created_at": now_str
        }
        return True, "User registered successfully.", user_dict
    except sqlite3.IntegrityError:
        return False, "An account with this email address already exists.", None
    except Exception as e:
        return False, f"Failed to create user: {str(e)}", None
    finally:
        if should_close:
            conn.close()


def get_user_by_email(email: str, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user row by email."""
    if not email:
        return None
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute("SELECT * FROM users WHERE email = ?;", (email.strip().lower(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        if should_close:
            conn.close()


def get_user_by_id(user_id: int, conn: Optional[sqlite3.Connection] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user row by ID."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        if should_close:
            conn.close()


def list_users(search_query: Optional[str] = None, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Lists registered users (excluding password hashes) with optional search filter."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        if search_query and search_query.strip():
            q = f"%{search_query.strip().lower()}%"
            cursor = conn.execute(
                """
                SELECT id, email, full_name, role, is_active, created_at, last_login, failed_login_attempts
                FROM users
                WHERE lower(email) LIKE ? OR lower(full_name) LIKE ?
                ORDER BY created_at DESC;
                """,
                (q, q)
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, email, full_name, role, is_active, created_at, last_login, failed_login_attempts
                FROM users
                ORDER BY created_at DESC;
                """
            )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if should_close:
            conn.close()


def update_user_status(user_id: int, is_active: int, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Activates (1) or deactivates (0) a user account."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?;", (1 if is_active else 0, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def update_user_role(user_id: int, new_role: str, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Updates a user's role to 'user' or 'admin'."""
    if new_role not in ("user", "admin"):
        return False
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        conn.execute("UPDATE users SET role = ? WHERE id = ?;", (new_role, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def delete_user(user_id: int, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Permanently deletes a user and cascades deletion to their resumes and screenings."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        # Prevent deleting the last remaining admin
        cursor = conn.execute("SELECT role FROM users WHERE id = ?;", (user_id,))
        row = cursor.fetchone()
        if row and row["role"] == "admin":
            admin_count = conn.execute("SELECT COUNT(*) FROM users WHERE role = 'admin';").fetchone()[0]
            if admin_count <= 1:
                return False

        conn.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def update_user_profile(
    user_id: int,
    full_name: Optional[str] = None,
    password_hash: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None
) -> bool:
    """Updates full name and/or password hash for a user."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        if full_name and password_hash:
            conn.execute("UPDATE users SET full_name = ?, password_hash = ? WHERE id = ?;", (full_name.strip(), password_hash, user_id))
        elif full_name:
            conn.execute("UPDATE users SET full_name = ? WHERE id = ?;", (full_name.strip(), user_id))
        elif password_hash:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?;", (password_hash, user_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


# ==============================================================================
# RATE LIMITING & LOGIN TRACKING
# ==============================================================================

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 10


def record_login_success(user_id: int, conn: Optional[sqlite3.Connection] = None):
    """Resets failed login count and updates last_login timestamp."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            UPDATE users 
            SET last_login = ?, failed_login_attempts = 0, locked_until = NULL 
            WHERE id = ?;
            """,
            (now_str, user_id)
        )
        conn.commit()
    finally:
        if should_close:
            conn.close()


def record_login_failure(email: str, conn: Optional[sqlite3.Connection] = None):
    """Increments failed login attempts and applies temporary lockout if threshold reached."""
    if not email:
        return
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        user = get_user_by_email(email, conn)
        if not user:
            return
        attempts = (user.get("failed_login_attempts") or 0) + 1
        locked_until = None
        if attempts >= MAX_FAILED_ATTEMPTS:
            locked_dt = datetime.datetime.now() + datetime.timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            locked_until = locked_dt.strftime("%Y-%m-%d %H:%M:%S")

        conn.execute(
            """
            UPDATE users 
            SET failed_login_attempts = ?, locked_until = ? 
            WHERE email = ?;
            """,
            (attempts, locked_until, email.strip().lower())
        )
        conn.commit()
    finally:
        if should_close:
            conn.close()


def is_account_locked(email: str, conn: Optional[sqlite3.Connection] = None) -> Tuple[bool, str]:
    """Checks if an account is currently locked out due to excessive failed attempts."""
    user = get_user_by_email(email, conn)
    if not user:
        return False, ""
    locked_until_str = user.get("locked_until")
    if not locked_until_str:
        return False, ""
    try:
        locked_dt = datetime.datetime.strptime(locked_until_str, "%Y-%m-%d %H:%M:%S")
        if datetime.datetime.now() < locked_dt:
            rem_min = max(1, int((locked_dt - datetime.datetime.now()).total_seconds() / 60))
            return True, f"Account temporarily locked due to excessive failed attempts. Please retry in {rem_min} minute(s)."
    except Exception:
        pass
    return False, ""


# ==============================================================================
# AUDIT LOGGING
# ==============================================================================

def log_audit_event(
    user_id: Optional[int],
    user_email: Optional[str],
    action: str,
    details: Optional[str] = None,
    status: str = "SUCCESS",
    conn: Optional[sqlite3.Connection] = None
):
    """Records an administrative or security event into audit_logs."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            INSERT INTO audit_logs (user_id, user_email, action, details, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (user_id, user_email, action, details, status, now_str)
        )
        conn.commit()
    except Exception:
        pass
    finally:
        if should_close:
            conn.close()


def get_audit_logs(limit: int = 50, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Fetches recent audit log entries."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute(
            """
            SELECT id, user_id, user_email, action, details, status, timestamp
            FROM audit_logs
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if should_close:
            conn.close()


# ==============================================================================
# PASSWORD RESET WORKFLOW
# ==============================================================================

def create_password_reset_code(email: str, conn: Optional[sqlite3.Connection] = None) -> Optional[str]:
    """Generates an 8-character cryptographic verification code valid for 15 minutes."""
    user = get_user_by_email(email, conn)
    if not user:
        return None
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        code = secrets.token_hex(4).upper()  # 8 character hex code
        expires_dt = datetime.datetime.now() + datetime.timedelta(minutes=15)
        expires_str = expires_dt.strftime("%Y-%m-%d %H:%M:%S")

        conn.execute(
            """
            INSERT INTO password_resets (email, reset_code, expires_at, used)
            VALUES (?, ?, ?, 0);
            """,
            (email.strip().lower(), code, expires_str)
        )
        conn.commit()
        return code
    finally:
        if should_close:
            conn.close()


def verify_and_use_reset_code(
    email: str,
    code: str,
    new_password_hash: str,
    conn: Optional[sqlite3.Connection] = None
) -> Tuple[bool, str]:
    """Validates reset code, updates password, and marks code as used."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        clean_email = email.strip().lower()
        clean_code = code.strip().upper()
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor = conn.execute(
            """
            SELECT id, expires_at, used 
            FROM password_resets 
            WHERE email = ? AND reset_code = ? AND used = 0
            ORDER BY id DESC LIMIT 1;
            """,
            (clean_email, clean_code)
        )
        record = cursor.fetchone()
        if not record:
            return False, "Invalid or expired verification reset code."

        if now_str > record["expires_at"]:
            return False, "This verification reset code has expired. Please request a new one."

        # Mark code as used
        conn.execute("UPDATE password_resets SET used = 1 WHERE id = ?;", (record["id"],))

        # Update password for user
        user = get_user_by_email(clean_email, conn)
        if user:
            conn.execute("UPDATE users SET password_hash = ?, failed_login_attempts = 0, locked_until = NULL WHERE id = ?;", (new_password_hash, user["id"]))
            log_audit_event(user["id"], clean_email, "PASSWORD_RESET", "Password reset successfully via verified code.", "SUCCESS", conn)

        conn.commit()
        return True, "Password has been updated successfully. You can now sign in with your new password."
    except Exception as e:
        return False, f"Password reset failed: {str(e)}"
    finally:
        if should_close:
            conn.close()


# ==============================================================================
# RESUME STORAGE & DATA ISOLATION CRUD
# ==============================================================================

def db_save_resume(user_id: int, candidate: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> bool:
    """Saves or updates a candidate resume belonging to a specific user."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        now_str = candidate.get("created_at") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parsed_json = json.dumps(candidate.get("sections", {}))
        skills_json = json.dumps(candidate.get("all_skills", []))
        contact = candidate.get("contact", {})

        conn.execute(
            """
            INSERT OR REPLACE INTO resumes (
                id, user_id, filename, candidate_name, file_size, file_hash,
                contact_email, contact_phone, raw_text, parsed_data_json, skills_json,
                years_of_experience, shortlisted, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                candidate["id"],
                user_id,
                candidate.get("filename", "resume.pdf"),
                candidate.get("candidate_name", "Unknown Candidate"),
                int(candidate.get("file_size", 0)),
                candidate.get("file_hash", ""),
                contact.get("email", ""),
                contact.get("phone", ""),
                candidate.get("raw_text", ""),
                parsed_json,
                skills_json,
                float(candidate.get("years_of_experience", 0.0)),
                1 if candidate.get("shortlisted") else 0,
                candidate.get("status", "Indexed"),
                now_str
            )
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def db_get_resumes_for_user(user_id: int, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Loads all candidates belonging strictly to user_id."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute(
            """
            SELECT * FROM resumes 
            WHERE user_id = ? 
            ORDER BY created_at DESC;
            """,
            (user_id,)
        )
        candidates = []
        for row in cursor.fetchall():
            c = dict(row)
            try:
                sections = json.loads(c.get("parsed_data_json") or "{}")
            except Exception:
                sections = {}
            try:
                all_skills = json.loads(c.get("skills_json") or "[]")
            except Exception:
                all_skills = []

            from src.skills import extract_skills
            skills_data = extract_skills(c.get("raw_text", ""))

            candidate_dict = {
                "id": c["id"],
                "candidate_name": c["candidate_name"],
                "filename": c["filename"],
                "contact": {
                    "email": c.get("contact_email") or "",
                    "phone": c.get("contact_phone") or ""
                },
                "education": sections.get("education", []),
                "raw_text": c["raw_text"],
                "sections": sections,
                "word_count": len(c["raw_text"].split()),
                "char_count": len(c["raw_text"]),
                "file_size": c["file_size"],
                "file_hash": c["file_hash"],
                "status": c["status"],
                "skills_data": skills_data,
                "all_skills": all_skills if all_skills else skills_data["all_skills"],
                "years_of_experience": c["years_of_experience"],
                "shortlisted": bool(c["shortlisted"]),
                "created_at": c["created_at"]
            }
            candidates.append(candidate_dict)
        return candidates
    finally:
        if should_close:
            conn.close()


def db_get_all_resume_metadata(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Administrative query: returns resume metadata across all users without exposing private text."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute(
            """
            SELECT r.id, r.user_id, u.email as user_email, u.full_name as user_name,
                   r.filename, r.candidate_name, r.file_size, r.years_of_experience,
                   r.shortlisted, r.status, r.created_at
            FROM resumes r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC;
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if should_close:
            conn.close()


def db_delete_resume(resume_id: str, user_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Deletes resume record. If user_id is provided, enforces that the caller owns the record."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        if user_id is not None:
            conn.execute("DELETE FROM resumes WHERE id = ? AND user_id = ?;", (resume_id, user_id))
        else:
            conn.execute("DELETE FROM resumes WHERE id = ?;", (resume_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def db_toggle_shortlist(resume_id: str, user_id: Optional[int] = None, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Toggles shortlisted status for a resume in SQLite."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        if user_id is not None:
            cursor = conn.execute("SELECT shortlisted FROM resumes WHERE id = ? AND user_id = ?;", (resume_id, user_id))
        else:
            cursor = conn.execute("SELECT shortlisted FROM resumes WHERE id = ?;", (resume_id,))
        row = cursor.fetchone()
        if not row:
            return False
        new_val = 0 if row["shortlisted"] else 1
        conn.execute("UPDATE resumes SET shortlisted = ? WHERE id = ?;", (new_val, resume_id))
        conn.commit()
        return bool(new_val)
    finally:
        if should_close:
            conn.close()


# ==============================================================================
# JOB MANAGEMENT CRUD
# ==============================================================================

def db_get_all_jobs(conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Retrieves all active jobs from SQLite."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute("SELECT * FROM jobs WHERE is_active = 1 ORDER BY created_at ASC;")
        jobs = []
        for row in cursor.fetchall():
            j = dict(row)
            try:
                req_skills = json.loads(j.get("required_skills_json") or "[]")
            except Exception:
                req_skills = []
            jobs.append({
                "id": j["id"],
                "title": j["title"],
                "department": j["department"],
                "min_experience": j["min_experience"],
                "required_skills": req_skills,
                "description": j["description"],
                "is_active": j["is_active"],
                "created_at": j["created_at"]
            })
        return jobs
    finally:
        if should_close:
            conn.close()


def db_save_job(job: Dict[str, Any], created_by: Optional[int] = None, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Adds a new job description to the database."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        skills_json = json.dumps(job.get("required_skills", []))
        conn.execute(
            """
            INSERT OR REPLACE INTO jobs 
            (id, title, department, min_experience, required_skills_json, description, created_by, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?);
            """,
            (
                job["id"],
                job["title"],
                job["department"],
                float(job.get("min_experience", 2.0)),
                skills_json,
                job["description"],
                created_by,
                now_str
            )
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def db_update_job(job_id: str, updates: Dict[str, Any], conn: Optional[sqlite3.Connection] = None) -> bool:
    """Updates an existing job description."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        title = updates.get("title")
        dept = updates.get("department")
        min_exp = updates.get("min_experience")
        desc = updates.get("description")
        skills = updates.get("required_skills")

        fields = []
        vals = []
        if title:
            fields.append("title = ?")
            vals.append(title)
        if dept:
            fields.append("department = ?")
            vals.append(dept)
        if min_exp is not None:
            fields.append("min_experience = ?")
            vals.append(float(min_exp))
        if desc:
            fields.append("description = ?")
            vals.append(desc)
        if skills is not None:
            fields.append("required_skills_json = ?")
            vals.append(json.dumps(skills))

        if not fields:
            return True

        vals.append(job_id)
        conn.execute(f"UPDATE jobs SET {', '.join(fields)} WHERE id = ?;", tuple(vals))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


def db_delete_job(job_id: str, conn: Optional[sqlite3.Connection] = None) -> bool:
    """Soft deletes or removes a job."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        conn.execute("DELETE FROM jobs WHERE id = ?;", (job_id,))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if should_close:
            conn.close()


# ==============================================================================
# SCREENING LOGS & AUDIT CRUD
# ==============================================================================

def db_record_screening(user_id: int, event: Dict[str, Any], conn: Optional[sqlite3.Connection] = None):
    """Records a candidate screening match run into SQLite."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """
            INSERT INTO screenings (
                user_id, job_id, job_title, candidate_name, composite_score,
                skill_score, semantic_score, matched_skills_count, missing_skills_count,
                recommendation, screened_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                user_id,
                event.get("job_id", "job_custom"),
                event.get("job_title", "Custom Job"),
                event.get("candidate_name", "Candidate"),
                float(event.get("composite_score", 0.0)),
                float(event.get("skill_score", 0.0)),
                float(event.get("semantic_score", 0.0)),
                int(event.get("matched_skills_count", 0)),
                int(event.get("missing_skills_count", 0)),
                event.get("recommendation", ""),
                now_str
            )
        )
        conn.commit()
    except Exception:
        pass
    finally:
        if should_close:
            conn.close()


def db_get_screenings_for_user(user_id: int, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Loads screening events for a specific user."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute(
            """
            SELECT * FROM screenings 
            WHERE user_id = ? 
            ORDER BY id DESC;
            """,
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if should_close:
            conn.close()


def db_get_all_screenings(limit: int = 100, conn: Optional[sqlite3.Connection] = None) -> List[Dict[str, Any]]:
    """Admin query: gets recent system-wide screenings."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        cursor = conn.execute(
            """
            SELECT s.*, u.email as user_email 
            FROM screenings s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.id DESC
            LIMIT ?;
            """,
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if should_close:
            conn.close()


def db_get_admin_overview_stats(conn: Optional[sqlite3.Connection] = None) -> Dict[str, Any]:
    """Calculates administrative overview KPIs based on real database records."""
    should_close = False
    if conn is None:
        conn = get_db_connection()
        should_close = True
    try:
        total_users = conn.execute("SELECT COUNT(*) FROM users;").fetchone()[0]
        active_users = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1;").fetchone()[0]
        total_resumes = conn.execute("SELECT COUNT(*) FROM resumes;").fetchone()[0]
        total_jobs = conn.execute("SELECT COUNT(*) FROM jobs;").fetchone()[0]
        total_screenings = conn.execute("SELECT COUNT(*) FROM screenings;").fetchone()[0]
        
        avg_score_row = conn.execute("SELECT AVG(composite_score) FROM screenings;").fetchone()
        avg_score = round(avg_score_row[0], 1) if avg_score_row and avg_score_row[0] is not None else 0.0

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_resumes": total_resumes,
            "total_jobs": total_jobs,
            "total_screenings": total_screenings,
            "avg_score": avg_score
        }
    finally:
        if should_close:
            conn.close()
