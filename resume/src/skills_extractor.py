"""
TalentIQ AI - Skills Extractor Module
Compatibility wrapper and interface for skills extraction engine.
"""

from src.skills import (
    extract_skills,
    normalize_skill_name,
    get_skill_category,
    build_skill_pattern,
    SKILL_TAXONOMY,
    SKILL_ALIASES
)

__all__ = [
    "extract_skills",
    "normalize_skill_name",
    "get_skill_category",
    "build_skill_pattern",
    "SKILL_TAXONOMY",
    "SKILL_ALIASES"
]

