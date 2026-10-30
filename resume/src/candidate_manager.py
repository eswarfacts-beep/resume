"""
TalentIQ AI - Candidate Search, Filtering & Management Engine
Supports multi-criteria filtering across names, filenames, target job roles,
score thresholds, skill taxonomies, and shortlist status with real-time responsive updates.
"""

from typing import Dict, List, Any, Optional
from src.matcher import match_candidate_to_job


def filter_and_sort_candidates(
    candidates: List[Dict[str, Any]],
    search_query: str = "",
    target_job: Optional[Dict[str, Any]] = None,
    min_score: float = 0.0,
    max_score: float = 100.0,
    required_skills: Optional[List[str]] = None,
    skill_mode: str = "ANY",  # "ANY" or "ALL"
    shortlist_filter: str = "ALL",  # "ALL", "SHORTLISTED_ONLY", "UNSHORTLISTED_ONLY"
    sort_by: str = "Highest Match Score",
    weights: Optional[Dict[str, float]] = None,
    match_cache: Optional[Dict[str, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Filters and sorts candidate list based on multiple simultaneous criteria.
    Returns enriched list with match scores for target job.
    """
    if not candidates:
        return []

    if match_cache is None:
        match_cache = {}

    filtered = []
    sq = search_query.strip().lower() if search_query else ""
    req_skills_set = set(s.lower() for s in (required_skills or []))

    for cand in candidates:
        cand_id = cand.get("id", "")
        cand_name = cand.get("candidate_name", "")
        filename = cand.get("filename", "")
        cand_skills = cand.get("all_skills", [])
        cand_skills_lower = set(s.lower() for s in cand_skills)
        shortlisted = cand.get("shortlisted", False)

        # 1. Search Query Filter (Name or Filename)
        if sq:
            if sq not in cand_name.lower() and sq not in filename.lower():
                continue

        # 2. Shortlist Filter
        if shortlist_filter == "SHORTLISTED_ONLY" and not shortlisted:
            continue
        elif shortlist_filter == "UNSHORTLISTED_ONLY" and shortlisted:
            continue

        # 3. Required Skills Filter
        if req_skills_set:
            if skill_mode == "ALL":
                if not req_skills_set.issubset(cand_skills_lower):
                    continue
            else:  # "ANY"
                if not req_skills_set.intersection(cand_skills_lower):
                    continue

        # 4. Job Match Evaluation (Calculate or retrieve from cache)
        match_info = None
        if target_job:
            cache_key = f"{cand_id}_{target_job.get('id', 'default')}"
            if cache_key in match_cache:
                match_info = match_cache[cache_key]
            else:
                match_info = match_candidate_to_job(cand, target_job, weights)
                match_cache[cache_key] = match_info
            
            comp_score = match_info.get("composite_score", 0.0)
            if not (min_score <= comp_score <= max_score):
                continue

        # Create combined view record
        cand_view = dict(cand)
        if match_info:
            cand_view["match_score"] = match_info.get("composite_score", 0.0)
            cand_view["matched_skills"] = match_info.get("matched_skills", [])
            cand_view["missing_skills"] = match_info.get("missing_skills", [])
            cand_view["badge_level"] = match_info.get("badge_level", "Evaluated")
            cand_view["recommendation"] = match_info.get("recommendation", "")
        else:
            cand_view["match_score"] = 0.0
            cand_view["matched_skills"] = []
            cand_view["missing_skills"] = []
            cand_view["badge_level"] = "Not Evaluated"
            cand_view["recommendation"] = "Awaiting job evaluation."

        filtered.append(cand_view)

    # Sorting
    if sort_by == "Highest Match Score":
        filtered.sort(key=lambda c: (c.get("match_score", 0.0), c.get("candidate_name", "")), reverse=True)
    elif sort_by == "Lowest Match Score":
        filtered.sort(key=lambda c: (c.get("match_score", 0.0), c.get("candidate_name", "")))
    elif sort_by == "Name (A-Z)":
        filtered.sort(key=lambda c: c.get("candidate_name", "").lower())
    elif sort_by == "Name (Z-A)":
        filtered.sort(key=lambda c: c.get("candidate_name", "").lower(), reverse=True)
    elif sort_by == "Experience (Highest First)":
        filtered.sort(key=lambda c: c.get("years_of_experience", 0.0), reverse=True)
    elif sort_by == "Upload Order (Newest First)":
        filtered.sort(key=lambda c: c.get("created_at", c.get("id", "")), reverse=True)

    return filtered

