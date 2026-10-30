"""
Unit tests for Persistence, Session Saving & Restoration Engine
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.persistence import (
    save_session,
    load_session,
    list_sessions,
    delete_session,
    export_session_json,
    import_session_json,
    restore_session_to_memory
)


class TestPersistenceEngine(unittest.TestCase):

    def setUp(self):
        self.test_session_id = "sess_unit_test_9999"
        self.job = {
            "id": "job_test",
            "title": "Platform Reliability Engineer",
            "department": "Infrastructure",
            "min_experience": 3.0,
            "required_skills": ["Linux", "Kubernetes", "Python"]
        }
        self.candidates = [
            {
                "id": "c1",
                "candidate_name": "Test Candidate",
                "filename": "test.pdf",
                "all_skills": ["Linux", "Python"],
                "shortlisted": True
            }
        ]
        self.last_results = [
            {
                "candidate_id": "c1",
                "candidate_name": "Test Candidate",
                "composite_score": 85.0
            }
        ]

    def tearDown(self):
        delete_session(self.test_session_id)

    def test_save_and_load_session(self):
        saved = save_session(
            name="Unit Test Session",
            job=self.job,
            candidates=self.candidates,
            last_results=self.last_results,
            session_id=self.test_session_id
        )
        self.assertEqual(saved["session_id"], self.test_session_id)
        self.assertEqual(saved["name"], "Unit Test Session")

        # Load from disk
        loaded = load_session(self.test_session_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["job"]["title"], "Platform Reliability Engineer")
        self.assertEqual(len(loaded["candidates"]), 1)
        self.assertEqual(loaded["metadata"]["shortlisted_count"], 1)

    def test_list_and_delete_session(self):
        save_session(
            name="List Test Session",
            job=self.job,
            candidates=self.candidates,
            last_results=self.last_results,
            session_id=self.test_session_id
        )

        sessions = list_sessions()
        ids = [s["session_id"] for s in sessions]
        self.assertIn(self.test_session_id, ids)

        deleted = delete_session(self.test_session_id)
        self.assertTrue(deleted)
        self.assertIsNone(load_session(self.test_session_id))

    def test_export_and_import_session_json(self):
        save_session(
            name="Export Test Session",
            job=self.job,
            candidates=self.candidates,
            last_results=self.last_results,
            session_id=self.test_session_id
        )

        json_str = export_session_json(self.test_session_id)
        self.assertIsNotNone(json_str)

        ok, msg, imported = import_session_json(json_str)
        self.assertTrue(ok)
        self.assertIsNotNone(imported)
        self.assertIn("Imported", imported["name"])

        # Clean up imported
        if imported and "session_id" in imported:
            delete_session(imported["session_id"])


if __name__ == "__main__":
    unittest.main()

