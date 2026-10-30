"""
End-to-End Integration Tests for Prompt 3 Features:
- Resume parsing & deduplication
- Job matching & scoring
- Candidate Management & multi-criteria filtering
- Candidate Comparison side-by-side matrix
- Downloadable sanitized reports & formula injection protection
- Screening session persistence & restoration
- Resume Builder & ReportLab PDF compilation
- Analytics metrics & Plotly chart generation
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import parse_resume
from src.matcher import match_candidate_to_job, rank_candidates_for_job
from src.candidate_manager import filter_and_sort_candidates
from src.comparison import build_comparison_matrix, extract_candidate_comparison_data
from src.reports import (
    sanitize_csv_value,
    generate_candidate_ranking_csv,
    generate_job_screening_summary_csv,
    generate_shortlisted_candidates_csv,
    generate_candidate_analysis_report
)
from src.persistence import (
    save_session,
    load_session,
    list_sessions,
    delete_session,
    export_session_json,
    import_session_json
)
from src.builder import prefill_resume_from_candidate, generate_resume_pdf
from src.analytics import (
    compute_analytics_summary,
    create_score_distribution_chart,
    create_top_skills_chart,
    create_skill_demand_vs_missing_chart,
    create_job_wise_results_chart
)


class TestTalentIQPrompt3Integration(unittest.TestCase):

    def setUp(self):
        # Sample realistic candidates
        self.c1 = {
            "id": "cand_1",
            "candidate_name": "Alex Chen",
            "filename": "Alex_Chen_Senior_FullStack.docx",
            "contact": {"email": "alex.chen@example.com", "phone": "+1 555-0182", "linkedin": "linkedin.com/in/alexchen", "github": "github.com/alexchen"},
            "education": ["B.S. in Computer Science"],
            "raw_text": "Alex Chen. Senior Full-Stack Engineer with 6 years experience in React, TypeScript, Node.js, PostgreSQL, Docker, AWS, REST API, Git.",
            "sections": {
                "summary": "Full-Stack Engineer with 6+ years building microservices and cloud web platforms.",
                "experience": "Lead Full-Stack Engineer at Apex Cloud. Built microservices with Docker, AWS, and React.",
                "projects": "Scalable REST APIs and cloud containerized platforms.",
                "certifications": "AWS Certified Solutions Architect"
            },
            "all_skills": ["React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "AWS", "REST API", "Git"],
            "years_of_experience": 6.0,
            "shortlisted": True
        }

        self.c2 = {
            "id": "cand_2",
            "candidate_name": "Sophia Rodriguez",
            "filename": "Sophia_Rodriguez_AI_ML_Engineer.pdf",
            "contact": {"email": "sophia.rodriguez@example.com", "phone": "+1 555-0145", "linkedin": "linkedin.com/in/sophiarodriguez", "github": "github.com/sophiarodriguez"},
            "education": ["M.S. in Artificial Intelligence"],
            "raw_text": "Sophia Rodriguez. AI / Machine Learning Engineer with 4 years experience in Python, PyTorch, TensorFlow, Scikit-Learn, NLP, LLMs, Docker, Machine Learning.",
            "sections": {
                "summary": "AI/ML Engineer specializing in LLMs, PyTorch, RAG pipelines, and NLP.",
                "experience": "ML Engineer at NeuroTech. Trained transformer models with PyTorch and Scikit-Learn.",
                "projects": "Retrieval Augmented Generation with Vector DB.",
                "certifications": "Deep Learning Specialization"
            },
            "all_skills": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "LLMs", "Docker", "Machine Learning"],
            "years_of_experience": 4.0,
            "shortlisted": False
        }

        self.c3 = {
            "id": "cand_3",
            "candidate_name": "Marcus Vance",
            "filename": "Marcus_Vance_Cloud_DevOps.txt",
            "contact": {"email": "marcus.vance@example.com", "phone": "+1 555-0199", "linkedin": "linkedin.com/in/marcusvance", "github": "github.com/marcusvance"},
            "education": ["B.S. in Network Engineering"],
            "raw_text": "Marcus Vance. Cloud DevOps Engineer with 5 years experience in Kubernetes, Docker, AWS, Terraform, CI/CD, Linux, Python, Prometheus.",
            "sections": {
                "summary": "DevOps & Infrastructure Engineer scaling AWS Kubernetes multi-cluster environments.",
                "experience": "Senior Platform Engineer at CloudForge managing Terraform and Kubernetes pipelines.",
                "projects": "Zero-downtime deployment pipelines with GitHub Actions.",
                "certifications": "CKA Certified Kubernetes Administrator"
            },
            "all_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Linux", "Python", "Prometheus"],
            "years_of_experience": 5.0,
            "shortlisted": True
        }

        self.candidates = [self.c1, self.c2, self.c3]

        self.job_fullstack = {
            "id": "job_1",
            "title": "Senior Full-Stack Engineer",
            "department": "Engineering",
            "min_experience": 4.0,
            "required_skills": ["React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "AWS"],
            "description": "Seeking Full-Stack Engineer with React, TypeScript, Node.js, PostgreSQL, Docker, and AWS."
        }

    def test_e2e_ranking_and_evidence(self):
        ranked = rank_candidates_for_job(self.candidates, self.job_fullstack)
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0]["candidate_name"], "Alex Chen")
        self.assertGreater(ranked[0]["composite_score"], 80.0)
        self.assertIn("React", ranked[0]["matched_skills"])
        self.assertIn("evidence_text", ranked[0])

    def test_e2e_candidate_filtering_and_sorting(self):
        # 1. Search by name
        res = filter_and_sort_candidates(self.candidates, search_query="Marcus")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["candidate_name"], "Marcus Vance")

        # 2. Filter by shortlist
        res_sl = filter_and_sort_candidates(self.candidates, shortlist_filter="SHORTLISTED_ONLY")
        self.assertEqual(len(res_sl), 2)

        # 3. Filter by required skills
        res_skills = filter_and_sort_candidates(self.candidates, required_skills=["PyTorch"])
        self.assertEqual(len(res_skills), 1)
        self.assertEqual(res_skills[0]["candidate_name"], "Sophia Rodriguez")

        # 4. Sort by highest score for fullstack
        res_ranked = filter_and_sort_candidates(self.candidates, target_job=self.job_fullstack, sort_by="Highest Match Score")
        self.assertEqual(res_ranked[0]["candidate_name"], "Alex Chen")

    def test_e2e_candidate_comparison_matrix(self):
        matrix = build_comparison_matrix([self.c1, self.c2], self.job_fullstack)
        self.assertEqual(len(matrix), 2)
        # Alex has all required skills
        self.assertEqual(len(matrix[0]["missing_skills"]), 0)
        self.assertGreater(matrix[0]["composite_score"], matrix[1]["composite_score"])
        self.assertTrue(len(matrix[0]["strengths"]) > 0)
        self.assertTrue(len(matrix[1]["improvements"]) > 0)

    def test_e2e_report_generation_and_csv_sanitization(self):
        # Test formula injection protection
        self.assertEqual(sanitize_csv_value("=cmd|' /C calc'!A0"), "'=cmd|' /C calc'!A0")
        self.assertEqual(sanitize_csv_value("+SUM(1,2)"), "'+SUM(1,2)")
        self.assertEqual(sanitize_csv_value("@SUM"), "'@SUM")

        # Generate ranking CSV
        ranked = rank_candidates_for_job(self.candidates, self.job_fullstack)
        ranking_csv = generate_candidate_ranking_csv(ranked, self.job_fullstack["title"])
        self.assertIn("Alex Chen", ranking_csv)
        self.assertIn("alex.chen@example.com", ranking_csv)

        # Generate job summary CSV
        summary_csv = generate_job_screening_summary_csv(self.job_fullstack, ranked, self.candidates)
        self.assertIn("Senior Full-Stack Engineer", summary_csv)
        self.assertIn("Engineering", summary_csv)

        # Generate shortlisted CSV
        sl_csv = generate_shortlisted_candidates_csv(self.candidates, ranked)
        self.assertIn("Alex Chen", sl_csv)
        self.assertIn("Marcus Vance", sl_csv)
        self.assertNotIn("Sophia Rodriguez", sl_csv)

        # Generate individual analysis dossier
        dossier = generate_candidate_analysis_report(self.c1, ranked[0], self.job_fullstack)
        self.assertIn("ALEX CHEN", dossier)
        self.assertIn("6.0 Years", dossier)
        self.assertIn("SHORTLISTED", dossier)

    def test_e2e_session_persistence_lifecycle(self):
        test_sid = "sess_e2e_integration_test_123"
        saved = save_session(
            name="E2E Integration Test Session",
            job=self.job_fullstack,
            candidates=self.candidates,
            last_results=[{"candidate_id": "cand_1", "composite_score": 90.0}],
            session_id=test_sid
        )
        self.assertEqual(saved["session_id"], test_sid)

        loaded = load_session(test_sid)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["job"]["title"], "Senior Full-Stack Engineer")
        self.assertEqual(len(loaded["candidates"]), 3)
        self.assertEqual(loaded["metadata"]["shortlisted_count"], 2)

        # Export and Import
        json_str = export_session_json(test_sid)
        self.assertIsNotNone(json_str)

        ok, msg, imported = import_session_json(json_str)
        self.assertTrue(ok)
        if imported and "session_id" in imported:
            delete_session(imported["session_id"])

        # Clean up
        self.assertTrue(delete_session(test_sid))
        self.assertIsNone(load_session(test_sid))

    def test_e2e_resume_builder_and_pdf(self):
        prefilled = prefill_resume_from_candidate(self.c1)
        self.assertEqual(prefilled["full_name"], "Alex Chen")
        self.assertEqual(prefilled["email"], "alex.chen@example.com")
        self.assertIn("React", prefilled["skills"])

        pdf_bytes = generate_resume_pdf(prefilled)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 1500)

    def test_e2e_analytics_computation_and_charts(self):
        ranked = rank_candidates_for_job(self.candidates, self.job_fullstack)
        analytics_data = compute_analytics_summary(
            self.candidates,
            [{"candidate_name": "Alex", "job_title": "Full-Stack", "composite_score": 92.0}],
            ranked,
            [self.job_fullstack]
        )

        self.assertEqual(analytics_data["total_resumes"], 3)
        self.assertEqual(analytics_data["shortlisted_count"], 2)
        self.assertTrue(analytics_data["has_evaluations"])
        self.assertGreater(analytics_data["avg_match_score"], 0)

        # Check charts
        fig_score = create_score_distribution_chart(analytics_data["score_ranges"])
        self.assertIsNotNone(fig_score)

        fig_skills = create_top_skills_chart(analytics_data["top_skills"])
        self.assertIsNotNone(fig_skills)

        fig_demand = create_skill_demand_vs_missing_chart(
            analytics_data["job_demand_counts"],
            analytics_data["missing_skill_counts"]
        )
        self.assertIsNotNone(fig_demand)

        fig_jobs = create_job_wise_results_chart(
            [{"job_title": "Full-Stack", "composite_score": 92.0}],
            ranked,
            "Senior Full-Stack Engineer"
        )
        self.assertIsNotNone(fig_jobs)


if __name__ == "__main__":
    unittest.main()

