"""
TalentIQ AI - AI Job Matching & Multi-Candidate Ranking Engine
Calculates semantic similarity (TF-IDF & Cosine Similarity), skill overlap,
experience alignment, weighted composite scores, and evidence explanations.
"""

from src.embeddings import calculate_semantic_similarity, extract_key_semantic_terms
from src.ranker import (
    extract_years_of_experience,
    match_candidate_to_job,
    rank_candidates_for_job,
    generate_match_evidence
)

__all__ = [
    "calculate_semantic_similarity",
    "extract_key_semantic_terms",
    "extract_years_of_experience",
    "match_candidate_to_job",
    "rank_candidates_for_job",
    "generate_match_evidence"
]
