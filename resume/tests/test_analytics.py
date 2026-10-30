"""
Unit tests for Advanced Analytics Dashboard Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analytics import (
    compute_analytics_summary,
    create_score_distribution_chart,
    create_top_skills_chart,
    create_skill_demand_vs_missing_chart,
    create_job_wise_results_chart
)


class TestAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        self.sample_candidates = [
            {
                "id": "c1",
                "candidate_name": "Alice Cooper",
                "all_skills": ["Python", "Docker", "AWS", "SQL"],
                "shortlisted": True
            },
            {
                "id": "c2",
                "candidate_name": "Bob Smith",
                "all_skills": ["Python", "React", "TypeScript", "Docker"],
                "shortlisted": False
            },
            {
                "id": "c3",
                "candidate_name": "Carol Danvers",
                "all_skills": ["Java", "Spring Boot", "AWS"],
                "shortlisted": True
            }
        ]

        self.sample_history = [
            {"candidate_name": "Alice", "job_title": "Backend Dev", "composite_score": 85.0},
            {"candidate_name": "Bob", "job_title": "Backend Dev", "composite_score": 68.0},
            {"candidate_name": "Carol", "job_title": "Cloud Dev", "composite_score": 48.0}
        ]

        self.sample_last_results = [
            {
                "candidate_id": "c1",
                "candidate_name": "Alice Cooper",
                "composite_score": 88.0,
                "missing_skills": ["Kubernetes"]
            },
            {
                "candidate_id": "c2",
                "candidate_name": "Bob Smith",
                "composite_score": 72.0,
                "missing_skills": ["AWS", "Kubernetes"]
            }
        ]

        self.sample_jobs = [
            {
                "id": "j1",
                "title": "Backend Dev",
                "required_skills": ["Python", "Docker", "Kubernetes", "AWS"]
            },
            {
                "id": "j2",
                "title": "Cloud Dev",
                "required_skills": ["AWS", "Terraform", "Docker"]
            }
        ]

    def test_compute_analytics_summary_empty(self):
        summary = compute_analytics_summary([], [], [], [])
        self.assertEqual(summary["total_resumes"], 0)
        self.assertEqual(summary["total_jobs_analyzed"], 0)
        self.assertEqual(summary["avg_match_score"], 0.0)
        self.assertEqual(summary["shortlisted_count"], 0)
        self.assertFalse(summary["has_evaluations"])

    def test_compute_analytics_summary_real_data(self):
        summary = compute_analytics_summary(
            self.sample_candidates,
            self.sample_history,
            self.sample_last_results,
            self.sample_jobs
        )

        self.assertEqual(summary["total_resumes"], 3)
        self.assertEqual(summary["shortlisted_count"], 2)
        self.assertEqual(summary["total_jobs_analyzed"], 2)
        # Average of 85.0, 68.0, 48.0 is 67.0
        self.assertAlmostEqual(summary["avg_match_score"], 67.0, places=1)
        self.assertTrue(summary["has_evaluations"])

        # Check score ranges
        score_ranges = summary["score_ranges"]
        self.assertIn("High Match (80-100%)", score_ranges)
        self.assertIn("Good Match (65-79%)", score_ranges)

        # Check skill frequencies
        top_skills = dict(summary["top_skills"])
        self.assertEqual(top_skills.get("Python"), 2)
        self.assertEqual(top_skills.get("Docker"), 2)
        self.assertEqual(top_skills.get("AWS"), 2)

        # Check job demands and missing skills
        self.assertEqual(summary["job_demand_counts"].get("AWS"), 2)
        self.assertEqual(summary["job_demand_counts"].get("Docker"), 2)
        self.assertEqual(summary["missing_skill_counts"].get("Kubernetes"), 2)

    def test_create_score_distribution_chart(self):
        ranges = {
            "High Match (80-100%)": 3,
            "Good Match (65-79%)": 5,
            "Review Needed (50-64%)": 2,
            "Low Alignment (<50%)": 1
        }
        fig = create_score_distribution_chart(ranges)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

    def test_create_top_skills_chart(self):
        top_skills = [("Python", 10), ("Docker", 8), ("React", 5)]
        fig = create_top_skills_chart(top_skills)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 1)

        # Test empty skills
        fig_empty = create_top_skills_chart([])
        self.assertIsNotNone(fig_empty)

    def test_create_skill_demand_vs_missing_chart(self):
        demands = {"Python": 4, "Docker": 3, "Kubernetes": 2}
        missings = {"Kubernetes": 5, "Terraform": 3}
        fig = create_skill_demand_vs_missing_chart(demands, missings)
        self.assertIsNotNone(fig)
        self.assertEqual(len(fig.data), 2)

    def test_create_job_wise_results_chart(self):
        fig = create_job_wise_results_chart(self.sample_history, self.sample_last_results, "Backend Dev")
        self.assertIsNotNone(fig)
        self.assertGreater(len(fig.data), 0)


if __name__ == "__main__":
    unittest.main()

