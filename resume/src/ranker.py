"""
TalentIQ AI - Candidate Ranker & Evidence Generation Engine
Calculates multi-dimensional alignment scores, ranks candidate pools,
and constructs evidence-based recruiter explanations.
"""

import re
from typing import Dict, List, Any, Optional
from src.embeddings import calculate_semantic_similarity, extract_key_semantic_terms
from src.skills import extract_skills, normalize_skill_name


def extract_years_of_experience(text: str) -> float:
    """Estimates years of professional experience mentioned in text."""
    if not text:
        return 0.0
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:relevant\s+)?experience",
        r"(?:experience|worked\s+for)\s*(?:of)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
        r"(\d{1,2})\s*\+\s*(?:years?|yrs?)"
    ]
    max_years = 0.0
    for pat in patterns:
        matches = re.findall(pat, text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if 0 < val < 45 and val > max_years:
                    max_years = val
            except ValueError:
                pass
    return max_years


def generate_match_evidence(match_res: Dict[str, Any]) -> str:
    """
    Constructs a concise, evidence-grounded explanation for why the candidate matches the role.
    Uses actual extracted skills, experience numbers, and semantic overlap terms.
    """
    matched = match_res.get("matched_skills", [])
    missing = match_res.get("missing_skills", [])
    cand_exp = match_res.get("candidate_experience", 0.0)
    req_exp = match_res.get("required_experience", 0.0)
    sem_score = match_res.get("semantic_score", 0.0)
    comp_score = match_res.get("composite_score", 0.0)
    semantic_terms = match_res.get("semantic_terms", [])

    points = []

    # 1. Skill alignment evidence
    if matched:
        top_m = ", ".join(matched[:5])
        if len(matched) > 5:
            top_m += f" (+{len(matched) - 5} more)"
        points.append(f"Demonstrates strong capability in {len(matched)} core required skill(s): {top_m}.")
    else:
        points.append("Limited direct match with specified primary skill requirements.")

    # 2. Missing skill note
    if missing:
        missing_preview = ", ".join(missing[:4])
        points.append(f"Skill gap identified in: {missing_preview}.")
    else:
        points.append("Comprehensive coverage with zero missing required skills.")

    # 3. Experience alignment evidence
    if req_exp > 0:
        if cand_exp >= req_exp:
            diff = cand_exp - req_exp
            extra = f" (+{diff:.1f} yrs above requirement)" if diff > 0 else " (exactly meets minimum)"
            points.append(f"Has {cand_exp:.1f} years professional experience, satisfying the {req_exp:.1f} year requirement{extra}.")
        else:
            deficit = req_exp - cand_exp
            points.append(f"Has {cand_exp:.1f} years of experience vs {req_exp:.1f} years required (-{deficit:.1f} yrs gap).")
    elif cand_exp > 0:
        points.append(f"Demonstrates {cand_exp:.1f} years of professional background.")

    # 4. Semantic contextual evidence
    if semantic_terms:
        terms_str = ", ".join(semantic_terms[:4])
        points.append(f"High semantic convergence on key terms: {terms_str}.")

    return " ".join(points)


def match_candidate_to_job(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Evaluates a single candidate against a job description.
    Returns detailed match breakdown, matched skills, missing skills, composite score,
    and actual evidence text.
    """
    if weights is None:
        weights = {"skills": 0.50, "semantic": 0.35, "experience": 0.15}

    resume_text = candidate.get("raw_text", "")
    job_text = job.get("description", "")

    # Extract skills
    candidate_skills_data = candidate.get("skills_data") or extract_skills(resume_text)
    candidate_skills = set(candidate_skills_data.get("all_skills", []))

    # Job required skills: either explicit or extracted
    job_skills_data = job.get("skills_data") or extract_skills(job_text)
    explicit_req = job.get("required_skills", [])
    if explicit_req:
        job_skills = set([normalize_skill_name(s) for s in explicit_req])
    else:
        job_skills = set(job_skills_data.get("all_skills", []))

    # Match skill overlap
    if job_skills:
        matched_skills = sorted(list(candidate_skills.intersection(job_skills)))
        missing_skills = sorted(list(job_skills.difference(candidate_skills)))
        skill_score = (len(matched_skills) / len(job_skills)) * 100.0
    else:
        matched_skills = sorted(list(candidate_skills))
        missing_skills = []
        skill_score = 75.0 if candidate_skills else 50.0

    # Semantic similarity & key terms
    semantic_score = calculate_semantic_similarity(resume_text, job_text)
    semantic_terms = extract_key_semantic_terms(resume_text, job_text, top_n=5)

    # Experience alignment
    cand_exp = candidate.get("years_of_experience")
    if cand_exp is None:
        cand_exp = extract_years_of_experience(resume_text)

    req_exp = float(job.get("min_experience", 0.0))
    if req_exp > 0:
        if cand_exp >= req_exp:
            exp_score = 100.0
        else:
            exp_score = (cand_exp / req_exp) * 100.0
    else:
        exp_score = 100.0 if cand_exp > 0 else 85.0

    # Composite weighted score
    w_s = weights.get("skills", 0.50)
    w_sem = weights.get("semantic", 0.35)
    w_e = weights.get("experience", 0.15)
    total_w = w_s + w_sem + w_e

    composite_score = round(
        (skill_score * w_s + semantic_score * w_sem + exp_score * w_e) / total_w, 1
    )
    composite_score = min(100.0, max(0.0, composite_score))

    # Actionable recommendation & badge level
    if composite_score >= 80.0:
        recommendation = "Top Match: Fast-track to recruiter phone interview."
        badge_level = "High Match"
        status_category = "High"
    elif composite_score >= 65.0:
        recommendation = "Strong Candidate: Suitable for technical evaluation."
        badge_level = "Good Match"
        status_category = "Good"
    elif composite_score >= 48.0:
        recommendation = "Moderate Alignment: Assess missing skills in screening."
        badge_level = "Review Needed"
        status_category = "Review"
    else:
        recommendation = "Low Alignment: Critical role requirements not met."
        badge_level = "Low Alignment"
        status_category = "Low"

    match_result = {
        "candidate_id": candidate.get("id", ""),
        "candidate_name": candidate.get("candidate_name", "Unknown Candidate"),
        "filename": candidate.get("filename", ""),
        "contact": candidate.get("contact", {}),
        "education": candidate.get("education", []),
        "sections": candidate.get("sections", {}),
        "raw_text": resume_text,
        "composite_score": composite_score,
        "skill_score": round(skill_score, 1),
        "semantic_score": round(semantic_score, 1),
        "exp_score": round(exp_score, 1),
        "candidate_experience": cand_exp,
        "required_experience": req_exp,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "candidate_skills": sorted(list(candidate_skills)),
        "job_skills": sorted(list(job_skills)),
        "semantic_terms": semantic_terms,
        "recommendation": recommendation,
        "badge_level": badge_level,
        "status_category": status_category
    }

    # Generate evidence explanation
    match_result["evidence_text"] = generate_match_evidence(match_result)
    return match_result


def rank_candidates_for_job(
    candidates: List[Dict[str, Any]],
    job: Dict[str, Any],
    weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """Ranks all candidates against a job description in descending order of match."""
    results = []
    for cand in candidates:
        match_res = match_candidate_to_job(cand, job, weights)
        results.append(match_res)

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    for idx, r in enumerate(results, 1):
        r["rank"] = idx

    return results

