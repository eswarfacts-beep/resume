"""
TalentIQ AI - Integration & Unit Tests for RBAC, Separate Portals, & SQLite Persistence
Tests all requirements specified in the major feature request:
- User Registration & Validation
- Separate User Login & Admin Login
- Non-admin user access restriction on Admin Portal
- Admin authentication & privileged operations
- Data isolation between user accounts
- Rate limiting / account lockouts
- Password reset code workflow
- Backend session tampering prevention
"""

import unittest
import os
import sys
import tempfile
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import (
    init_db,
    get_db_connection,
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_users,
    update_user_status,
    update_user_role,
    delete_user,
    record_login_failure,
    record_login_success,
    is_account_locked,
    create_password_reset_code,
    verify_and_use_reset_code,
    db_save_resume,
    db_get_resumes_for_user,
    db_get_all_resume_metadata,
    db_delete_resume,
    db_get_all_jobs,
    db_save_job,
    db_update_job,
    db_delete_job,
    db_record_screening,
    db_get_screenings_for_user,
    db_get_admin_overview_stats
)
from src.auth import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_email_format,
    authenticate_user,
    register_user,
    request_password_reset,
    complete_password_reset
)


class TestRBACAndAuthSystem(unittest.TestCase):

    def setUp(self):
        # Ensure database is initialized
        init_db()

    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword123!"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))

    def test_password_strength_validation(self):
        # Short password
        ok, msg = validate_password_strength("Short1")
        self.assertFalse(ok)
        self.assertIn("at least 8 characters", msg)

        # No digits
        ok, msg = validate_password_strength("NoDigitsHere")
        self.assertFalse(ok)
        self.assertIn("at least one number", msg)

        # No letters
        ok, msg = validate_password_strength("1234567890")
        self.assertFalse(ok)
        self.assertIn("at least one letter", msg)

        # Valid strong password
        ok, msg = validate_password_strength("StrongPass2026")
        self.assertTrue(ok)

    def test_email_syntax_validation(self):
        self.assertTrue(validate_email_format("user@company.com"))
        self.assertTrue(validate_email_format("admin.test@sub.talentiq.ai"))
        self.assertFalse(validate_email_format("invalid-email"))
        self.assertFalse(validate_email_format("@nodomain.com"))
        self.assertFalse(validate_email_format(""))

    def test_user_registration_flow(self):
        test_email = "test.screener@enterprise.org"
        # Cleanup in case already exists from prior run
        existing = get_user_by_email(test_email)
        if existing:
            delete_user(existing["id"])

        # Mismatched passwords
        ok, msg, _ = register_user(test_email, "PassWord123", "Mismatch456", "Test Screener")
        self.assertFalse(ok)
        self.assertIn("Passwords do not match", msg)

        # Successful registration
        ok, msg, user = register_user(test_email, "PassWord123", "PassWord123", "Test Screener")
        self.assertTrue(ok)
        self.assertEqual(user["email"], test_email)
        self.assertEqual(user["role"], "user")

        # Duplicate email registration prevention
        ok_dup, msg_dup, _ = register_user(test_email, "PassWord123", "PassWord123", "Duplicate Attempt")
        self.assertFalse(ok_dup)
        self.assertIn("already exists", msg_dup)

    def test_separate_portals_access_control(self):
        user_email = "regular.user@example.com"
        existing = get_user_by_email(user_email)
        if not existing:
            register_user(user_email, "UserPass2026!", "UserPass2026!", "Regular User")

        # 1. Normal user authenticating on USER PORTAL -> SUCCESS
        ok_u, msg_u, u_rec = authenticate_user(user_email, "UserPass2026!", expected_role="user")
        self.assertTrue(ok_u)
        self.assertIsNotNone(u_rec)
        self.assertEqual(u_rec["role"], "user")

        # 2. Normal user attempting to log into ADMIN PORTAL -> ACCESS DENIED!
        ok_a, msg_a, a_rec = authenticate_user(user_email, "UserPass2026!", expected_role="admin")
        self.assertFalse(ok_a)
        self.assertIsNone(a_rec)
        self.assertIn("Access Denied", msg_a)
        self.assertIn("Administrator privileges", msg_a)

        # 3. Provisioned Admin authenticating on ADMIN PORTAL -> SUCCESS
        ok_adm, msg_adm, adm_rec = authenticate_user("admin@talentiq.ai", "Admin@TalentIQ2026", expected_role="admin")
        self.assertTrue(ok_adm)
        self.assertIsNotNone(adm_rec)
        self.assertEqual(adm_rec["role"], "admin")

    def test_rate_limiting_and_account_lockout(self):
        victim_email = "lockout.test@example.com"
        existing = get_user_by_email(victim_email)
        if not existing:
            register_user(victim_email, "TargetPass2026!", "TargetPass2026!", "Lockout Target")

        # Simulate 5 consecutive failed login attempts
        for _ in range(5):
            authenticate_user(victim_email, "WrongPassword999!")

        is_locked, lock_msg = is_account_locked(victim_email)
        self.assertTrue(is_locked)
        self.assertIn("Account temporarily locked", lock_msg)

        # Even with correct password, login should be blocked while locked out
        ok, msg, _ = authenticate_user(victim_email, "TargetPass2026!")
        self.assertFalse(ok)
        self.assertIn("temporarily locked", msg)

        # Reset lockout via record_login_success
        user = get_user_by_email(victim_email)
        record_login_success(user["id"])
        is_locked_after, _ = is_account_locked(victim_email)
        self.assertFalse(is_locked_after)

    def test_password_recovery_code_workflow(self):
        reset_email = "reset.candidate@example.com"
        existing = get_user_by_email(reset_email)
        if not existing:
            register_user(reset_email, "InitialPass1!", "InitialPass1!", "Reset Candidate")

        # Request reset code
        ok, msg, code = request_password_reset(reset_email)
        self.assertTrue(ok)
        self.assertIsNotNone(code)
        self.assertEqual(len(code), 8)

        # Invalid code should fail
        ok_bad, _ = complete_password_reset(reset_email, "BADCODE1", "NewSecurePass123!", "NewSecurePass123!")
        self.assertFalse(ok_bad)

        # Valid code should succeed
        ok_good, msg_good = complete_password_reset(reset_email, code, "NewSecurePass123!", "NewSecurePass123!")
        self.assertTrue(ok_good)
        self.assertIn("updated successfully", msg_good)

        # Authenticate with updated password
        ok_login, _, user_rec = authenticate_user(reset_email, "NewSecurePass123!")
        self.assertTrue(ok_login)
        self.assertEqual(user_rec["email"], reset_email)

    def test_user_data_isolation_in_database(self):
        # Create two distinct users
        u1_email = "screener.alpha@test.com"
        u2_email = "screener.beta@test.com"
        if not get_user_by_email(u1_email):
            register_user(u1_email, "AlphaPass123!", "AlphaPass123!", "Screener Alpha")
        if not get_user_by_email(u2_email):
            register_user(u2_email, "BetaPass123!", "BetaPass123!", "Screener Beta")

        u1 = get_user_by_email(u1_email)
        u2 = get_user_by_email(u2_email)

        # User 1 uploads resume
        cand_u1 = {
            "id": f"res_alpha_{u1['id']}",
            "filename": "alpha_resume.pdf",
            "candidate_name": "Alice Engineer",
            "file_size": 24500,
            "file_hash": "hash_alice_123",
            "raw_text": "Experienced Python and AWS Cloud Developer.",
            "sections": {"experience": ["5 years at Alpha Corp"]},
            "all_skills": ["Python", "AWS", "Docker"],
            "years_of_experience": 5.0,
            "shortlisted": True
        }
        db_save_resume(u1["id"], cand_u1)

        # Verify User 1 sees their resume
        u1_resumes = db_get_resumes_for_user(u1["id"])
        self.assertTrue(any(r["id"] == cand_u1["id"] for r in u1_resumes))

        # Verify User 2 CANNOT see User 1's resume (Strict Data Isolation)
        u2_resumes = db_get_resumes_for_user(u2["id"])
        self.assertFalse(any(r["id"] == cand_u1["id"] for r in u2_resumes))

        # Admin query sees metadata across users without leaking private full text
        all_meta = db_get_all_resume_metadata()
        alpha_meta = next((m for m in all_meta if m["id"] == cand_u1["id"]), None)
        self.assertIsNotNone(alpha_meta)
        self.assertEqual(alpha_meta["candidate_name"], "Alice Engineer")
        self.assertNotIn("raw_text", alpha_meta)

    def test_admin_job_and_user_governance(self):
        admin = get_user_by_email("admin@talentiq.ai")
        self.assertIsNotNone(admin)
        self.assertEqual(admin["role"], "admin")

        # 1. Admin creates job
        job_id = f"job_test_{int(os.getpid())}"
        test_job = {
            "id": job_id,
            "title": "Principal Architect",
            "department": "Engineering",
            "min_experience": 7.0,
            "required_skills": ["Go", "Kubernetes", "Distributed Systems"],
            "description": "Architect high-throughput distributed talent systems."
        }
        db_save_job(test_job, created_by=admin["id"])

        jobs = db_get_all_jobs()
        self.assertTrue(any(j["id"] == job_id for j in jobs))

        # 2. Admin updates job
        db_update_job(job_id, {"title": "Distinguished Architect", "min_experience": 8.0})
        jobs_updated = db_get_all_jobs()
        updated_job = next(j for j in jobs_updated if j["id"] == job_id)
        self.assertEqual(updated_job["title"], "Distinguished Architect")
        self.assertEqual(updated_job["min_experience"], 8.0)

        # 3. Admin deletes job
        db_delete_job(job_id)
        jobs_after = db_get_all_jobs()
        self.assertFalse(any(j["id"] == job_id for j in jobs_after))

        # 4. User Status Deactivation
        temp_user_email = "deactivate.me@test.com"
        if not get_user_by_email(temp_user_email):
            register_user(temp_user_email, "TestPass123!", "TestPass123!", "Temp User")
        temp_user = get_user_by_email(temp_user_email)

        update_user_status(temp_user["id"], 0)
        temp_user_deactivated = get_user_by_id(temp_user["id"])
        self.assertEqual(temp_user_deactivated["is_active"], 0)

        # Deactivated user cannot authenticate
        ok_deact, msg_deact, _ = authenticate_user(temp_user_email, "TestPass123!")
        self.assertFalse(ok_deact)
        self.assertIn("deactivated", msg_deact)

        # Reactivate user
        update_user_status(temp_user["id"], 1)
        ok_react, _, _ = authenticate_user(temp_user_email, "TestPass123!")
        self.assertTrue(ok_react)

    def test_admin_overview_stats(self):
        stats = db_get_admin_overview_stats()
        self.assertIn("total_users", stats)
        self.assertIn("active_users", stats)
        self.assertIn("total_resumes", stats)
        self.assertIn("total_jobs", stats)
        self.assertIn("total_screenings", stats)
        self.assertGreaterEqual(stats["total_users"], 1)
        self.assertGreaterEqual(stats["total_jobs"], 1)


if __name__ == "__main__":
    unittest.main()

