"""
Unit tests for Candidate Management, Search & Multi-Criteria Filtering Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.candidate_manager import filter_and_sort_candidates


class TestCandidateManagement(unittest.TestCase):

    def setUp(self):
        self.candidates = [
            {
                "id": "c1",
                "candidate_name": "Alex Chen",
                "filename": "Alex_Chen_FullStack.docx",
                "all_skills": ["React", "TypeScript", "Node.js", "Docker", "PostgreSQL"],
                "years_of_experience": 5.0,
                "shortlisted": True,
                "raw_text": "Senior React and Node.js developer with Docker experience."
            },
            {
                "id": "c2",
                "candidate_name": "Sophia Rodriguez",
                "filename": "Sophia_ML_AI.pdf",
                "all_skills": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Docker"],
                "years_of_experience": 4.0,
                "shortlisted": False,
                "raw_text": "Machine learning specialist proficient in Python, PyTorch, and Docker."
            },
            {
                "id": "c3",
                "candidate_name": "Marcus Vance",
                "filename": "Marcus_Cloud_DevOps.txt",
                "all_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "Linux"],
                "years_of_experience": 6.0,
                "shortlisted": True,
                "raw_text": "DevOps expert managing Kubernetes and AWS infrastructure."
            }
        ]

        self.job = {
            "id": "job_1",
            "title": "Senior Full-Stack Engineer",
            "required_skills": ["React", "Node.js", "Docker"],
            "min_experience": 4.0,
            "description": "Looking for a React and Node.js engineer."
        }

    def test_search_by_name(self):
        res = filter_and_sort_candidates(self.candidates, search_query="Sophia")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["candidate_name"], "Sophia Rodriguez")

    def test_search_by_filename(self):
        res = filter_and_sort_candidates(self.candidates, search_query="DevOps.txt")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["candidate_name"], "Marcus Vance")

    def test_filter_by_shortlist_status(self):
        res_sl = filter_and_sort_candidates(self.candidates, shortlist_filter="SHORTLISTED_ONLY")
        self.assertEqual(len(res_sl), 2)
        self.assertTrue(all(c["shortlisted"] for c in res_sl))

        res_unsl = filter_and_sort_candidates(self.candidates, shortlist_filter="UNSHORTLISTED_ONLY")
        self.assertEqual(len(res_unsl), 1)
        self.assertEqual(res_unsl[0]["candidate_name"], "Sophia Rodriguez")

    def test_filter_by_required_skills_any(self):
        res = filter_and_sort_candidates(
            self.candidates,
            required_skills=["Kubernetes", "PyTorch"],
            skill_mode="ANY"
        )
        self.assertEqual(len(res), 2)
        names = [c["candidate_name"] for c in res]
        self.assertIn("Sophia Rodriguez", names)
        self.assertIn("Marcus Vance", names)
        self.assertNotIn("Alex Chen", names)

    def test_filter_by_required_skills_all(self):
        res = filter_and_sort_candidates(
            self.candidates,
            required_skills=["Docker", "React"],
            skill_mode="ALL"
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["candidate_name"], "Alex Chen")

    def test_filter_by_score_range_and_sort(self):
        res = filter_and_sort_candidates(
            self.candidates,
            target_job=self.job,
            min_score=50.0,
            max_score=100.0,
            sort_by="Highest Match Score"
        )
        self.assertGreater(len(res), 0)
        # Top candidate for FullStack job should be Alex Chen
        self.assertEqual(res[0]["candidate_name"], "Alex Chen")
        self.assertGreaterEqual(res[0]["match_score"], res[-1]["match_score"])

    def test_sort_by_name(self):
        res_az = filter_and_sort_candidates(self.candidates, sort_by="Name (A-Z)")
        self.assertEqual(res_az[0]["candidate_name"], "Alex Chen")
        self.assertEqual(res_az[-1]["candidate_name"], "Sophia Rodriguez")

        res_za = filter_and_sort_candidates(self.candidates, sort_by="Name (Z-A)")
        self.assertEqual(res_za[0]["candidate_name"], "Sophia Rodriguez")
        self.assertEqual(res_za[-1]["candidate_name"], "Alex Chen")

    def test_no_matches_returns_empty_list(self):
        res = filter_and_sort_candidates(self.candidates, search_query="NonExistentNameXYZ")
        self.assertEqual(len(res), 0)


if __name__ == "__main__":
    unittest.main()

