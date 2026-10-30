"""
Unit tests for Authentication & Recruiter Session Management Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.auth import (
    authenticate_user,
    sign_in_user,
    sign_out_user,
    get_current_user,
    init_auth_state,
    DEMO_USERS
)


class TestAuthModule(unittest.TestCase):

    def test_authenticate_user_valid(self):
        ok, msg, user = authenticate_user("recruiter", "talentiq2026")
        self.assertTrue(ok)
        self.assertEqual(user["username"], "recruiter")
        self.assertEqual(user["name"], "Sarah Jenkins")
        self.assertIn("Authentication successful", msg)

        # Test email authentication
        ok_email, _, user_email = authenticate_user("sarah.jenkins@talentiq.ai", "talentiq2026")
        self.assertTrue(ok_email)
        self.assertEqual(user_email["name"], "Sarah Jenkins")

    def test_authenticate_user_invalid(self):
        ok, msg, user = authenticate_user("recruiter", "wrong_password")
        self.assertFalse(ok)
        self.assertIsNone(user)
        self.assertIn("Invalid credentials", msg)

        ok_bad_user, _, _ = authenticate_user("nonexistent_user", "password")
        self.assertFalse(ok_bad_user)

    def test_authenticate_user_empty(self):
        ok, msg, _ = authenticate_user("", "")
        self.assertFalse(ok)
        self.assertIn("Username or email is required", msg)

        ok_p, msg_p, _ = authenticate_user("recruiter", "")
        self.assertFalse(ok_p)
        self.assertIn("Password is required", msg_p)


if __name__ == "__main__":
    unittest.main()

