"""
TalentIQ AI - Candidate Comparison Engine
Performs side-by-side comparative analysis of 2 to 3 candidate profiles against a target job role,
evaluating overall match score, matched and missing skills, education, work experience,
projects, certifications, and objective strengths and improvement areas.
"""

from typing import Dict, List, Any, Optional, Tuple
from src.matcher import match_candidate_to_job


def derive_strengths_and_improvements(
    match_data: Dict[str, Any],
    candidate: Dict[str, Any],
    job: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    """
    Computes grounded strengths and improvement areas based strictly on
    extracted facts and algorithmic alignment scores. Never invents details.
    """
    strengths = []
    improvements = []

    matched_skills = match_data.get("matched_skills", [])
    missing_skills = match_data.get("missing_skills", [])
    skill_score = match_data.get("skill_score", 0.0)
    sem_score = match_data.get("semantic_score", 0.0)
    cand_exp = match_data.get("candidate_experience", 0.0)
    req_exp = match_data.get("required_experience", 0.0)
    sections = candidate.get("sections", {})
    education = candidate.get("education", [])

    # 1. Skill evaluation
    if not missing_skills and matched_skills:
        strengths.append(f"100% Core Skill Coverage: Holds all {len(matched_skills)} required role skills.")
    elif skill_score >= 70.0:
        strengths.append(f"High Skill Overlap: Matched {len(matched_skills)} of {len(matched_skills) + len(missing_skills)} required skills ({skill_score:.0f}%).")
    
    if missing_skills:
        gap_preview = ", ".join(missing_skills[:3])
        if len(missing_skills) > 3:
            gap_preview += f" (+{len(missing_skills) - 3} more)"
        improvements.append(f"Skill Gap: Missing {len(missing_skills)} required skill(s) ({gap_preview}).")

    # 2. Experience evaluation
    if req_exp > 0:
        if cand_exp >= req_exp:
            surplus = cand_exp - req_exp
            if surplus >= 1.0:
                strengths.append(f"Experience Surplus: {cand_exp:.1f} years vs {req_exp:.1f} years required (+{surplus:.1f} yrs above minimum).")
            else:
                strengths.append(f"Meets Experience Threshold: {cand_exp:.1f} years matches the {req_exp:.1f} years required.")
        else:
            deficit = req_exp - cand_exp
            improvements.append(f"Experience Deficit: {cand_exp:.1f} years vs {req_exp:.1f} years required (-{deficit:.1f} yrs gap).")
    elif cand_exp > 0:
        strengths.append(f"Documented Tenure: Demonstrates {cand_exp:.1f} years of relevant industry experience.")

    # 3. Semantic Alignment
    if sem_score >= 70.0:
        strengths.append(f"High Contextual Alignment: Semantic score of {sem_score:.0f}% shows close domain proximity.")
    elif sem_score < 45.0:
        improvements.append(f"Lower Domain Convergence: Semantic similarity score of {sem_score:.0f}% suggests limited technical vocabulary overlap.")

    # 4. Education
    if education:
        strengths.append(f"Verified Academic Credentials: {', '.join(education[:2])}.")
    else:
        improvements.append("No explicit degree keywords parsed from academic sections.")

    # 5. Projects & Certifications
    if sections.get("projects"):
        strengths.append("Contains documented technical projects section.")
    if sections.get("certifications"):
        strengths.append("Verified industry certifications section detected.")

    # Fallbacks if empty
    if not strengths:
        strengths.append("Baseline qualifications documented in resume.")
    if not improvements:
        improvements.append("No critical gaps identified for this role.")

    return strengths, improvements


def extract_candidate_comparison_data(
    candidate: Dict[str, Any],
    job: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Constructs a complete comparison dataset for one candidate against the specified job.
    """
    match_data = match_candidate_to_job(candidate, job, weights)
    strengths, improvements = derive_strengths_and_improvements(match_data, candidate, job)

    sections = candidate.get("sections", {})
    projects_text = sections.get("projects", "").strip()
    certs_text = sections.get("certifications", "").strip()
    experience_text = sections.get("experience", "").strip()

    return {
        "candidate_id": candidate.get("id"),
        "candidate_name": candidate.get("candidate_name", "Unknown Candidate"),
        "filename": candidate.get("filename", ""),
        "shortlisted": candidate.get("shortlisted", False),
        "composite_score": match_data.get("composite_score", 0.0),
        "skill_score": match_data.get("skill_score", 0.0),
        "semantic_score": match_data.get("semantic_score", 0.0),
        "exp_score": match_data.get("exp_score", 0.0),
        "badge_level": match_data.get("badge_level", "N/A"),
        "status_category": match_data.get("status_category", "N/A"),
        "matched_skills": match_data.get("matched_skills", []),
        "missing_skills": match_data.get("missing_skills", []),
        "all_skills": candidate.get("all_skills", []),
        "candidate_experience": candidate.get("years_of_experience", 0.0),
        "required_experience": job.get("min_experience", 0.0),
        "education": candidate.get("education", []),
        "education_display": ", ".join(candidate.get("education", [])) if candidate.get("education") else "Not explicitly specified",
        "work_experience_summary": experience_text[:350] + ("..." if len(experience_text) > 350 else "") if experience_text else "Extracted in document body",
        "projects_summary": projects_text[:350] + ("..." if len(projects_text) > 350 else "") if projects_text else "Not specified in resume",
        "certifications_summary": certs_text[:350] + ("..." if len(certs_text) > 350 else "") if certs_text else "Not specified in resume",
        "strengths": strengths,
        "improvements": improvements,
        "recommendation": match_data.get("recommendation", "")
    }


def build_comparison_matrix(
    candidates: List[Dict[str, Any]],
    job: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> List[Dict[str, Any]]:
    """
    Constructs comparison data for a list of 2 to 3 candidates.
    """
    matrix = []
    for cand in candidates:
        matrix.append(extract_candidate_comparison_data(cand, job, weights))
    return matrix

