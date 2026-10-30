"""
Unit tests for Skills Extraction & Normalization Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.skills import (
    extract_skills,
    normalize_skill_name,
    get_skill_category
)


class TestSkillsEngine(unittest.TestCase):

    def test_extract_skills_basic(self):
        text = "Experienced with Python, React, PostgreSQL, Docker, and AWS."
        result = extract_skills(text)
        all_skills = result["all_skills"]
        self.assertIn("Python", all_skills)
        self.assertIn("React", all_skills)
        self.assertIn("PostgreSQL", all_skills)
        self.assertIn("Docker", all_skills)
        self.assertIn("AWS", all_skills)

    def test_extract_skills_boundary_cases(self):
        # C++, C#, .NET, Go
        text = "Proficient in C++, C#, and .NET Core. Also built microservices in Go and Rust."
        result = extract_skills(text)
        all_skills = result["all_skills"]
        self.assertIn("C++", all_skills)
        self.assertIn("C#", all_skills)
        self.assertIn(".NET Core", all_skills)
        self.assertIn("Go", all_skills)
        self.assertIn("Rust", all_skills)

    def test_skill_aliases(self):
        self.assertEqual(normalize_skill_name("k8s"), "Kubernetes")
        self.assertEqual(normalize_skill_name("react.js"), "React")
        self.assertEqual(normalize_skill_name("postgres"), "PostgreSQL")
        self.assertEqual(normalize_skill_name("amazon web services"), "AWS")
        self.assertEqual(normalize_skill_name("golang"), "Go")

    def test_skill_categories(self):
        self.assertEqual(get_skill_category("Python"), "tech")
        self.assertEqual(get_skill_category("Kubernetes"), "cloud")
        self.assertEqual(get_skill_category("Machine Learning"), "ai")
        self.assertEqual(get_skill_category("Communication"), "soft")


if __name__ == "__main__":
    unittest.main()
