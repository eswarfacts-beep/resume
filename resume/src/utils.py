"""
TalentIQ AI - Common Utilities Module
Provides text cleaning, sanitization, hashing, and formatting helper functions.
"""

import hashlib
import re
from typing import Any, List, Dict
from src.parser import clean_text
from src.reports import sanitize_csv_value


def compute_file_hash(file_bytes: bytes) -> str:
    """Computes SHA-256 hash for document bytes."""
    if not file_bytes:
        return ""
    return hashlib.sha256(file_bytes).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Formats raw byte counts into human-readable KB/MB strings."""
    if not size_bytes:
        return "0 KB"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def safe_truncate(text: str, max_chars: int = 200) -> str:
    """Truncates text safely with trailing ellipsis."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


__all__ = [
    "clean_text",
    "sanitize_csv_value",
    "compute_file_hash",
    "format_file_size",
    "safe_truncate"
]

