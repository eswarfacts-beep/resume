"""
TalentIQ AI - Embeddings & Semantic Similarity Engine
Computes TF-IDF vector embeddings and cosine similarity between textual documents.
"""

import re
import functools
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@functools.lru_cache(maxsize=1024)
def calculate_semantic_similarity(resume_text: str, job_text: str) -> float:
    """
    Computes cosine similarity of TF-IDF vectors between resume and job description.
    Returns score between 0.0 and 100.0.
    """
    if not resume_text or not resume_text.strip() or not job_text or not job_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
            max_features=2500
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        scaled_sim = min(100.0, max(0.0, float(sim) * 100.0))
        return round(scaled_sim, 2)
    except Exception:
        # Fallback to token overlap
        r_words = set(re.findall(r"\w+", resume_text.lower()))
        j_words = set(re.findall(r"\w+", job_text.lower()))
        if not j_words:
            return 0.0
        overlap = len(r_words.intersection(j_words)) / len(j_words)
        return round(overlap * 100.0, 2)


@functools.lru_cache(maxsize=1024)
def extract_key_semantic_terms(resume_text: str, job_text: str, top_n: int = 5) -> List[str]:
    """
    Identifies the top overlapping high-value keywords between resume and job description
    to provide actual textual evidence for match explanations.
    """
    if not resume_text.strip() or not job_text.strip():
        return []

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=1000
        )
        matrix = vectorizer.fit_transform([resume_text, job_text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Product of TF-IDF weights gives mutual importance
        v1 = matrix[0].toarray()[0]
        v2 = matrix[1].toarray()[0]
        overlap_scores = v1 * v2

        top_indices = overlap_scores.argsort()[::-1]
        top_terms = []
        for idx in top_indices:
            if overlap_scores[idx] > 0 and len(feature_names[idx]) > 2:
                top_terms.append(feature_names[idx].title())
            if len(top_terms) >= top_n:
                break
        return top_terms
    except Exception:
        return []

