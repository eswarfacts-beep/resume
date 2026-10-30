"""
Unit tests for Reporting Engine, CSV Sanitization, and Dossier Generation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.reports import (
    sanitize_csv_value,
    generate_candidate_ranking_csv,
    generate_job_screening_summary_csv,
    generate_shortlisted_candidates_csv,
    generate_candidate_analysis_report
)


class TestReportsEngine(unittest.TestCase):

    def test_sanitize_csv_value_formula_injection(self):
        # Neutralizes formula trigger symbols
        self.assertEqual(sanitize_csv_value("=1+1"), "'=1+1")
        self.assertEqual(sanitize_csv_value("+SUM(A1:A10)"), "'+SUM(A1:A10)")
        self.assertEqual(sanitize_csv_value("@dangerous"), "'@dangerous")
        self.assertEqual(sanitize_csv_value("-cmd|' /C calc'!A0"), "'-cmd|' /C calc'!A0")
        self.assertEqual(sanitize_csv_value("\tTAB_INJECT"), "'\tTAB_INJECT")

        # Valid negative number remains numeric
        self.assertEqual(sanitize_csv_value("-4.5"), "-4.5")
        self.assertEqual(sanitize_csv_value(-10), "-10")
        self.assertEqual(sanitize_csv_value(99.5), "99.5")

        # Normal text remains unaltered
        self.assertEqual(sanitize_csv_value("Alex Chen"), "Alex Chen")
        self.assertEqual(sanitize_csv_value(None), "")
        self.assertEqual(sanitize_csv_value(True), "YES")
        self.assertEqual(sanitize_csv_value(False), "NO")

    def test_generate_candidate_ranking_csv(self):
        results = [
            {
                "rank": 1,
                "candidate_name": "Sarah Connor",
                "composite_score": 92.5,
                "badge_level": "High Match",
                "skill_score": 90.0,
                "semantic_score": 85.0,
                "exp_score": 100.0,
                "candidate_experience": 5.0,
                "required_experience": 4.0,
                "matched_skills": ["Python", "Docker"],
                "missing_skills": [],
                "shortlisted": True,
                "filename": "sarah.pdf",
                "contact": {"email": "sarah@cyberdyne.org", "phone": "555-1234"},
                "recommendation": "Top Match."
            }
        ]
        csv_text = generate_candidate_ranking_csv(results, "Lead Engineer")
        self.assertIn("Sarah Connor", csv_text)
        self.assertIn("92.5", csv_text)
        self.assertIn("Lead Engineer", csv_text)
        self.assertIn("sarah@cyberdyne.org", csv_text)

    def test_generate_job_screening_summary_csv(self):
        job = {
            "title": "Cloud Architect",
            "department": "Platform",
            "min_experience": 5.0,
            "required_skills": ["AWS", "Kubernetes", "Terraform"]
        }
        results = [
            {
                "rank": 1,
                "candidate_name": "Marcus Vance",
                "composite_score": 88.0,
                "badge_level": "High Match",
                "matched_skills": ["AWS", "Kubernetes"],
                "missing_skills": ["Terraform"],
                "candidate_experience": 6.0,
                "shortlisted": True,
                "recommendation": "Interview recommended."
            }
        ]
        summary = generate_job_screening_summary_csv(job, results, [])
        self.assertIn("Cloud Architect", summary)
        self.assertIn("Platform", summary)
        self.assertIn("Marcus Vance", summary)
        self.assertIn("Average Match Score", summary)

    def test_generate_shortlisted_candidates_csv(self):
        candidates = [
            {
                "id": "c1",
                "candidate_name": "John Doe",
                "filename": "john.pdf",
                "shortlisted": True,
                "years_of_experience": 4.0,
                "education": ["B.S. in CS"],
                "contact": {"email": "john@doe.com", "phone": "123-456"},
                "all_skills": ["React", "TypeScript"]
            },
            {
                "id": "c2",
                "candidate_name": "Jane Smith",
                "filename": "jane.pdf",
                "shortlisted": False,
                "years_of_experience": 2.0,
                "all_skills": ["Java"]
            }
        ]
        csv_text = generate_shortlisted_candidates_csv(candidates)
        self.assertIn("John Doe", csv_text)
        self.assertIn("john@doe.com", csv_text)
        self.assertNotIn("Jane Smith", csv_text)

    def test_generate_candidate_analysis_report(self):
        candidate = {
            "candidate_name": "Alex Mercer",
            "filename": "alex.pdf",
            "years_of_experience": 6.0,
            "education": ["M.S. in Software Engineering"],
            "contact": {"email": "alex@mercer.dev", "phone": "555-9876"},
            "all_skills": ["Python", "Docker", "AWS"],
            "shortlisted": True,
            "sections": {
                "projects": "Autonomous Kubernetes Operator.",
                "certifications": "CKA Certified."
            }
        }
        report = generate_candidate_analysis_report(candidate)
        self.assertIn("ALEX MERCER", report)
        self.assertIn("6.0 Years", report)
        self.assertIn("SHORTLISTED", report)
        self.assertIn("Autonomous Kubernetes Operator", report)


if __name__ == "__main__":
    unittest.main()

