"""
Unit tests for Resume Parser module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parser import (
    clean_text,
    extract_contact_info,
    extract_candidate_name,
    extract_sections,
    extract_education,
    parse_resume
)


class TestResumeParser(unittest.TestCase):

    def test_clean_text(self):
        sample = "  Hello   World \r\n\t  Test   Line  \n\n\n\nNew Paragraph  "
        cleaned = clean_text(sample)
        self.assertIn("Hello World", cleaned)
        self.assertNotIn("   ", cleaned)
        self.assertIn("Test Line\n\nNew Paragraph", cleaned)

    def test_extract_contact_info(self):
        text = """
        Johnathan Doe
        Email: john.doe@example.com
        Phone: (555) 123-4567
        LinkedIn: https://linkedin.com/in/johndoe
        GitHub: https://github.com/johndoe
        """
        contact = extract_contact_info(text)
        self.assertEqual(contact["email"], "john.doe@example.com")
        self.assertTrue("555" in contact["phone"] and "123" in contact["phone"])
        self.assertIn("linkedin.com/in/johndoe", contact["linkedin"])
        self.assertIn("github.com/johndoe", contact["github"])

    def test_extract_candidate_name(self):
        text = "Alex Mercer\nSenior Software Architect\nalex@mercer.dev\n"
        name = extract_candidate_name(text, "Alex_Mercer_Resume.pdf")
        self.assertEqual(name, "Alex Mercer")

        text_no_name = "Resume\nalex@mercer.dev"
        fallback_name = extract_candidate_name(text_no_name, "Sarah_Connor_CV.pdf")
        self.assertEqual(fallback_name, "Sarah Connor")

    def test_extract_education(self):
        text = """
        Education
        M.S. in Artificial Intelligence, Stanford University.
        B.S. in Computer Science from UC Berkeley.
        """
        degrees = extract_education(text)
        self.assertTrue(any("M.S." in d or "Master" in d for d in degrees))
        self.assertTrue(any("B.S." in d or "Bachelor" in d for d in degrees))

    def test_extract_sections(self):
        text = """
        Alex Mercer
        Professional Summary
        Passionate full-stack developer with 5+ years experience building cloud services.
        Technical Skills
        Python, React, Docker, AWS, PostgreSQL
        Work Experience
        Staff Engineer at TechCorp from 2021 to 2024.
        Education
        B.S. in Computer Science from State University.
        """
        sections = extract_sections(text)
        self.assertIn("summary", sections)
        self.assertIn("skills", sections)
        self.assertIn("experience", sections)
        self.assertIn("education", sections)
        self.assertIn("Passionate full-stack developer", sections["summary"])
        self.assertIn("Python, React", sections["skills"])

    def test_empty_and_corrupt_file_handling(self):
        res = parse_resume(b"", "empty.pdf")
        self.assertFalse(res["is_valid"])
        self.assertEqual(res["status"], "Failed")
        self.assertIn("empty", res["error_message"].lower())

    def test_real_docx_parsing(self):
        docx_path = os.path.join(os.path.dirname(__file__), "..", "sample_resumes", "Alex_Chen_Senior_FullStack.docx")
        if os.path.exists(docx_path):
            with open(docx_path, "rb") as f:
                res = parse_resume(f.read(), "Alex_Chen_Senior_FullStack.docx")
            self.assertTrue(res["is_valid"])
            self.assertIn("Alex Chen", res["candidate_name"])
            self.assertIn("React", res["raw_text"])

    def test_real_pdf_parsing(self):
        pdf_path = os.path.join(os.path.dirname(__file__), "..", "sample_resumes", "Sophia_Rodriguez_AI_ML_Engineer.pdf")
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                res = parse_resume(f.read(), "Sophia_Rodriguez_AI_ML_Engineer.pdf")
            self.assertTrue(res["is_valid"])
            self.assertIn("Sophia", res["candidate_name"])
            self.assertIn("Python", res["raw_text"])


if __name__ == "__main__":
    unittest.main()
