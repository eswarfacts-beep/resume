"""
Unit tests for Candidate Comparison Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.comparison import (
    extract_candidate_comparison_data,
    build_comparison_matrix,
    derive_strengths_and_improvements
)


class TestCandidateComparison(unittest.TestCase):

    def setUp(self):
        self.cand_1 = {
            "id": "c1",
            "candidate_name": "Maya Patel",
            "filename": "maya.pdf",
            "all_skills": ["Python", "PyTorch", "TensorFlow", "Docker", "NLP"],
            "years_of_experience": 5.0,
            "education": ["M.S. in Computer Science"],
            "sections": {
                "projects": "Neural search retrieval engine using PyTorch transformers.",
                "certifications": "Deep Learning Specialization",
                "experience": "Senior ML Engineer at AI Labs building high-throughput inference."
            },
            "raw_text": "Senior ML Engineer with 5 years experience in Python, PyTorch, TensorFlow, Docker, NLP."
        }

        self.cand_2 = {
            "id": "c2",
            "candidate_name": "David Kim",
            "filename": "david.docx",
            "all_skills": ["Python", "Scikit-Learn"],
            "years_of_experience": 1.5,
            "education": [],
            "sections": {},
            "raw_text": "Junior Python developer with 1.5 years experience in Scikit-Learn."
        }

        self.job = {
            "id": "j_ml",
            "title": "Machine Learning Engineer",
            "min_experience": 3.0,
            "required_skills": ["Python", "PyTorch", "NLP", "Docker"],
            "description": "Seeking ML Engineer with Python and PyTorch experience."
        }

    def test_extract_candidate_comparison_data(self):
        data = extract_candidate_comparison_data(self.cand_1, self.job)
        self.assertEqual(data["candidate_name"], "Maya Patel")
        self.assertGreater(data["composite_score"], 70.0)
        self.assertIn("Python", data["matched_skills"])
        self.assertIn("PyTorch", data["matched_skills"])
        self.assertEqual(data["education_display"], "M.S. in Computer Science")
        self.assertIn("Neural search retrieval", data["projects_summary"])
        self.assertIn("Deep Learning", data["certifications_summary"])
        self.assertTrue(len(data["strengths"]) > 0)

    def test_absent_sections_fallback(self):
        data = extract_candidate_comparison_data(self.cand_2, self.job)
        self.assertEqual(data["education_display"], "Not explicitly specified")
        self.assertEqual(data["projects_summary"], "Not specified in resume")
        self.assertEqual(data["certifications_summary"], "Not specified in resume")
        self.assertTrue(any("Experience Deficit" in imp for imp in data["improvements"]))

    def test_build_comparison_matrix(self):
        matrix = build_comparison_matrix([self.cand_1, self.cand_2], self.job)
        self.assertEqual(len(matrix), 2)
        self.assertGreater(matrix[0]["composite_score"], matrix[1]["composite_score"])
        self.assertEqual(matrix[0]["candidate_name"], "Maya Patel")
        self.assertEqual(matrix[1]["candidate_name"], "David Kim")


if __name__ == "__main__":
    unittest.main()
