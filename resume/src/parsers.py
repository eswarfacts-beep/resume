"""
TalentIQ AI - Parsers Module (Compatibility Alias for parser.py)
"""

from src.parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    clean_text,
    extract_contact_info,
    extract_candidate_name,
    extract_education,
    extract_sections,
    parse_resume
)

__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_docx",
    "clean_text",
    "extract_contact_info",
    "extract_candidate_name",
    "extract_education",
    "extract_sections",
    "parse_resume"
]

