"""
Unit tests for AI Matcher, Embeddings, and Ranking Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.matcher import (
    extract_years_of_experience,
    calculate_semantic_similarity,
    extract_key_semantic_terms,
    match_candidate_to_job,
    rank_candidates_for_job,
    generate_match_evidence
)


class TestMatcherEngine(unittest.TestCase):

    def test_extract_years_of_experience(self):
        text1 = "Senior Developer with 6+ years of experience in distributed systems."
        self.assertEqual(extract_years_of_experience(text1), 6.0)

        text2 = "Worked for 3.5 years in fintech environments."
        self.assertEqual(extract_years_of_experience(text2), 3.5)

        text3 = "No experience stated."
        self.assertEqual(extract_years_of_experience(text3), 0.0)

    def test_calculate_semantic_similarity(self):
        resume = "Experienced Python developer with machine learning, deep learning, PyTorch, and NLP."
        job_match = "We are seeking a Machine Learning Engineer with Python and PyTorch NLP expertise."
        job_diff = "Experienced registered nurse with clinical patient care certification."

        sim_high = calculate_semantic_similarity(resume, job_match)
        sim_low = calculate_semantic_similarity(resume, job_diff)

        self.assertGreater(sim_high, sim_low)
        self.assertGreater(sim_high, 20.0)

    def test_extract_key_semantic_terms(self):
        resume = "Python developer specializing in PyTorch deep learning and neural network transformers."
        job = "Seeking PyTorch engineer to train transformers and deep learning neural architectures."
        terms = extract_key_semantic_terms(resume, job, top_n=3)
        self.assertIsInstance(terms, list)
        self.assertGreater(len(terms), 0)

    def test_match_candidate_to_job_and_evidence(self):
        cand = {
            "id": "cand_1",
            "candidate_name": "Maya Lin",
            "filename": "maya.pdf",
            "raw_text": "Full stack engineer with 4+ years experience. Expert in React, TypeScript, Node.js, PostgreSQL, Docker.",
            "years_of_experience": 4.0
        }
        job = {
            "title": "Full-Stack Engineer",
            "min_experience": 3.0,
            "required_skills": ["React", "TypeScript", "Node.js", "PostgreSQL", "AWS"],
            "description": "Building web apps with React, TypeScript, and Node.js on PostgreSQL database."
        }

        result = match_candidate_to_job(cand, job)
        self.assertIn("React", result["matched_skills"])
        self.assertIn("AWS", result["missing_skills"])
        self.assertGreater(result["composite_score"], 60.0)
        self.assertIn("recommendation", result)
        self.assertIn("evidence_text", result)
        self.assertTrue(len(result["evidence_text"]) > 20)

    def test_rank_candidates_for_job(self):
        c1 = {
            "id": "c1",
            "candidate_name": "Top Candidate",
            "filename": "c1.pdf",
            "raw_text": "Python, PyTorch, TensorFlow, Docker, NLP, Machine Learning with 5 years experience.",
            "years_of_experience": 5.0
        }
        c2 = {
            "id": "c2",
            "candidate_name": "Unrelated Candidate",
            "filename": "c2.pdf",
            "raw_text": "Sales manager with 10 years experience in real estate and customer negotiations.",
            "years_of_experience": 10.0
        }
        job = {
            "title": "AI Engineer",
            "min_experience": 3.0,
            "required_skills": ["Python", "PyTorch", "Machine Learning"],
            "description": "AI and Machine learning engineer with Python and PyTorch."
        }

        ranked = rank_candidates_for_job([c2, c1], job)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["candidate_name"], "Top Candidate")
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertGreater(ranked[0]["composite_score"], ranked[1]["composite_score"])


if __name__ == "__main__":
    unittest.main()
