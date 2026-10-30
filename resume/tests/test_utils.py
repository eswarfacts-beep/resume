"""
Unit tests for Utilities and Parsers Compatibility Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import compute_file_hash, format_file_size, safe_truncate
import src.parsers as parsers_alias


class TestUtilsAndParsers(unittest.TestCase):

    def test_compute_file_hash(self):
        h = compute_file_hash(b"hello world")
        self.assertEqual(len(h), 64)
        self.assertEqual(compute_file_hash(b""), "")

    def test_format_file_size(self):
        self.assertEqual(format_file_size(0), "0 KB")
        self.assertEqual(format_file_size(2048), "2.0 KB")
        self.assertEqual(format_file_size(2 * 1024 * 1024), "2.00 MB")

    def test_safe_truncate(self):
        self.assertEqual(safe_truncate("short text", 20), "short text")
        long_text = "This is a very long string that should be truncated safely with dots."
        truncated = safe_truncate(long_text, 15)
        self.assertTrue(truncated.endswith("..."))
        self.assertLessEqual(len(truncated), 18)

    def test_parsers_alias_exports(self):
        self.assertTrue(hasattr(parsers_alias, "parse_resume"))
        self.assertTrue(hasattr(parsers_alias, "clean_text"))
        self.assertTrue(hasattr(parsers_alias, "extract_contact_info"))


if __name__ == "__main__":
    unittest.main()

