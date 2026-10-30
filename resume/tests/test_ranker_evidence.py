"""
Unit tests for Ranker, Evidence Generation, and State Storage Operations
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ranker import (
    generate_match_evidence,
    match_candidate_to_job,
    rank_candidates_for_job
)
from src.embeddings import extract_key_semantic_terms
from src.storage import (
    init_session_state,
    add_candidate_from_file,
    remove_candidate_by_id,
    get_candidate_by_id,
    clear_all_candidates
)


class TestRankerEvidence(unittest.TestCase):

    def test_generate_match_evidence_high_alignment(self):
        match_data = {
            "matched_skills": ["Python", "PyTorch", "Docker"],
            "missing_skills": [],
            "candidate_experience": 5.0,
            "required_experience": 3.0,
            "semantic_score": 85.0,
            "composite_score": 92.0,
            "semantic_terms": ["Machine Learning", "Neural Networks"]
        }
        evidence = generate_match_evidence(match_data)
        self.assertIn("3 core required skill(s)", evidence)
        self.assertIn("zero missing", evidence)
        self.assertIn("5.0 years", evidence)
        self.assertIn("Machine Learning", evidence)

    def test_generate_match_evidence_with_gaps(self):
        match_data = {
            "matched_skills": ["Python"],
            "missing_skills": ["Kubernetes", "Terraform", "AWS"],
            "candidate_experience": 1.5,
            "required_experience": 4.0,
            "semantic_score": 35.0,
            "composite_score": 42.0,
            "semantic_terms": []
        }
        evidence = generate_match_evidence(match_data)
        self.assertIn("Skill gap identified in: Kubernetes, Terraform, AWS", evidence)
        self.assertIn("gap", evidence.lower())

    def test_extract_key_semantic_terms(self):
        doc1 = "Full stack engineer specializing in React, Next.js, Node.js, and distributed microservices."
        doc2 = "Seeking a developer experienced with React microservices architecture."
        terms = extract_key_semantic_terms(doc1, doc2, top_n=2)
        self.assertIsInstance(terms, list)
        self.assertTrue(any("React" in t or "Microservices" in t for t in terms))

    def test_storage_add_and_remove_candidate(self):
        clear_all_candidates()
        sample_text = b"David Kim\nEmail: david@kim.io\nSummary: Python developer with 4 years experience in Docker and AWS.\nSkills: Python, Docker, AWS"
        cand, msg, ok = add_candidate_from_file(sample_text, "David_Kim.txt")
        self.assertTrue(ok)
        self.assertIsNotNone(cand)
        cand_id = cand["id"]

        retrieved = get_candidate_by_id(cand_id)
        self.assertEqual(retrieved["candidate_name"], "David Kim")

        removed = remove_candidate_by_id(cand_id)
        self.assertTrue(removed)
        self.assertIsNone(get_candidate_by_id(cand_id))


if __name__ == "__main__":
    unittest.main()

