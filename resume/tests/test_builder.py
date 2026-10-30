"""
Unit tests for Resume Builder and ReportLab PDF Generation Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.builder import (
    prefill_resume_from_candidate,
    generate_resume_pdf,
    sanitize_xml
)


class TestResumeBuilder(unittest.TestCase):

    def test_sanitize_xml(self):
        self.assertEqual(sanitize_xml("Tom & Jerry"), "Tom &amp; Jerry")
        self.assertEqual(sanitize_xml("<script>alert(1)</script>"), "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertEqual(sanitize_xml(None), "")

    def test_prefill_resume_from_candidate(self):
        candidate = {
            "candidate_name": "Jordan Lee",
            "contact": {
                "email": "jordan.lee@example.com",
                "phone": "+1 555-0192",
                "linkedin": "linkedin.com/in/jordanlee",
                "github": "github.com/jordanlee"
            },
            "education": ["B.S. in Computer Science"],
            "all_skills": ["Python", "Docker", "AWS", "FastAPI"],
            "years_of_experience": 4.5,
            "sections": {
                "summary": "Cloud backend engineer with 4+ years building APIs.",
                "experience": "Senior Backend Developer at CloudScale.\nSpearheaded migration to microservices.",
                "projects": "Distributed message queue broker.",
                "certifications": "AWS Certified Developer"
            }
        }

        prefilled = prefill_resume_from_candidate(candidate)
        self.assertEqual(prefilled["full_name"], "Jordan Lee")
        self.assertEqual(prefilled["email"], "jordan.lee@example.com")
        self.assertIn("Python", prefilled["skills"])
        self.assertEqual(prefilled["education"][0]["degree"], "B.S. in Computer Science")
        self.assertEqual(len(prefilled["experience"]), 1)
        self.assertIn("AWS Certified Developer", prefilled["certifications"])

    def test_generate_resume_pdf_compilation(self):
        resume_data = {
            "full_name": "Jordan Lee",
            "job_title": "Senior Cloud Engineer",
            "email": "jordan.lee@example.com",
            "phone": "+1 555-0192",
            "location": "Seattle, WA",
            "linkedin": "linkedin.com/in/jordanlee",
            "github": "github.com/jordanlee",
            "summary": "Senior engineer with deep expertise in cloud architecture and microservices.",
            "skills": "Python, Docker, Kubernetes, AWS, PostgreSQL, Redis",
            "experience": [
                {
                    "role": "Staff Engineer",
                    "company": "Tech Innovations LLC",
                    "duration": "2021 - Present",
                    "bullets": "Led cloud microservices team.\nReduced latency by 35% using caching."
                }
            ],
            "education": [
                {
                    "degree": "B.S. in Computer Engineering",
                    "institution": "University of Washington",
                    "year": "2019"
                }
            ],
            "projects": [
                {
                    "name": "High-Throughput Messaging Bus",
                    "description": "Engineered real-time message processor handling 100k events/sec."
                }
            ],
            "certifications": ["AWS Certified Solutions Architect"]
        }

        pdf_bytes = generate_resume_pdf(resume_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        # Check PDF header magic bytes
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()

