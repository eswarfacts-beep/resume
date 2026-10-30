"""
TalentIQ AI - Reporting & Data Export Engine
Generates sanitized CSV reports, job screening summaries, shortlisted talent rosters,
and detailed individual candidate analytical dossiers with formula injection protection.
"""

import io
import csv
import re
from typing import Dict, List, Any, Optional


def sanitize_csv_value(val: Any) -> str:
    """
    Sanitizes values against CSV Formula Injection (Spreadsheet Formula Injection).
    Prepends a single quote if string starts with formula operators '=', '+', '-', '@', '\t', '\r'.
    Handles None and empty values gracefully.
    """
    if val is None:
        return ""
    
    # If it is a boolean, return TRUE or FALSE
    if isinstance(val, bool):
        return "YES" if val else "NO"

    # If it's a numeric type (int, float), it is safe
    if isinstance(val, (int, float)):
        return str(val)

    s = str(val)
    if not s:
        return ""

    # Formula injection trigger characters
    dangerous_starts = ("=", "+", "@", "\t", "\r")
    if s.startswith(dangerous_starts):
        return "'" + s

    s = s.strip()
    if not s:
        return ""

    if s.startswith(dangerous_starts):
        return "'" + s
    
    # If starts with '-', check if it is a valid negative number; if not, sanitize
    if s.startswith("-"):
        try:
            float(s)
            return s
        except ValueError:
            return "'" + s

    return s


def generate_candidate_ranking_csv(results: List[Dict[str, Any]], job_title: str = "") -> str:
    """
    Generates a sanitized CSV string of the candidate leaderboard ranking.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    # Header row
    headers = [
        "Rank",
        "Candidate Name",
        "Match Score (%)",
        "Status Level",
        "Skill Alignment (%)",
        "Semantic Score (%)",
        "Experience Score (%)",
        "Candidate Experience (Yrs)",
        "Required Experience (Yrs)",
        "Target Role",
        "Matched Skills Count",
        "Matched Skills",
        "Missing Skills Count",
        "Missing Skills",
        "Shortlisted",
        "Source Filename",
        "Email",
        "Phone",
        "Recommendation"
    ]
    writer.writerow([sanitize_csv_value(h) for h in headers])

    if not results:
        return output.getvalue()

    for idx, r in enumerate(results, 1):
        rank = r.get("rank", idx)
        name = r.get("candidate_name", "Unknown")
        score = r.get("composite_score", 0.0)
        badge = r.get("badge_level", "N/A")
        s_score = r.get("skill_score", 0.0)
        sem_score = r.get("semantic_score", 0.0)
        e_score = r.get("exp_score", 0.0)
        cand_exp = r.get("candidate_experience", 0.0)
        req_exp = r.get("required_experience", 0.0)
        role = job_title or r.get("job_title", "Evaluated Role")
        
        matched_sks = r.get("matched_skills", [])
        missing_sks = r.get("missing_skills", [])
        shortlisted = r.get("shortlisted", False)
        filename = r.get("filename", "")
        
        contact = r.get("contact", {})
        email = contact.get("email") if isinstance(contact, dict) else ""
        phone = contact.get("phone") if isinstance(contact, dict) else ""
        rec = r.get("recommendation", "")

        row = [
            sanitize_csv_value(rank),
            sanitize_csv_value(name),
            sanitize_csv_value(score),
            sanitize_csv_value(badge),
            sanitize_csv_value(s_score),
            sanitize_csv_value(sem_score),
            sanitize_csv_value(e_score),
            sanitize_csv_value(cand_exp),
            sanitize_csv_value(req_exp),
            sanitize_csv_value(role),
            sanitize_csv_value(len(matched_sks)),
            sanitize_csv_value("; ".join(matched_sks)),
            sanitize_csv_value(len(missing_sks)),
            sanitize_csv_value("; ".join(missing_sks)),
            sanitize_csv_value(shortlisted),
            sanitize_csv_value(filename),
            sanitize_csv_value(email),
            sanitize_csv_value(phone),
            sanitize_csv_value(rec)
        ]
        writer.writerow(row)

    return output.getvalue()


def generate_job_screening_summary_csv(
    job: Dict[str, Any],
    results: List[Dict[str, Any]],
    candidates: List[Dict[str, Any]]
) -> str:
    """
    Generates a comprehensive job-wise screening summary CSV with KPI summary block
    and candidate breakdown.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    # Section 1: Executive Role Summary
    writer.writerow([sanitize_csv_value("=== TALENTIQ AI - JOB SCREENING EXECUTIVE SUMMARY ===")])
    writer.writerow([sanitize_csv_value("Job Title"), sanitize_csv_value(job.get("title", "N/A"))])
    writer.writerow([sanitize_csv_value("Department"), sanitize_csv_value(job.get("department", "General"))])
    writer.writerow([sanitize_csv_value("Minimum Required Experience"), sanitize_csv_value(f"{job.get('min_experience', 0)} Years")])
    writer.writerow([sanitize_csv_value("Required Skills"), sanitize_csv_value("; ".join(job.get("required_skills", [])))])
    writer.writerow([sanitize_csv_value("Total Candidates Evaluated"), sanitize_csv_value(len(results))])

    if results:
        avg_score = round(sum(r.get("composite_score", 0.0) for r in results) / len(results), 1)
        top_cand = results[0]
        high_matches = len([r for r in results if r.get("composite_score", 0.0) >= 80.0])
        shortlisted_cands = len([r for r in results if r.get("shortlisted", False)])
        
        writer.writerow([sanitize_csv_value("Average Match Score (%)"), sanitize_csv_value(avg_score)])
        writer.writerow([sanitize_csv_value("Top Candidate"), sanitize_csv_value(f"{top_cand.get('candidate_name')} ({top_cand.get('composite_score')}%)")])
        writer.writerow([sanitize_csv_value("High Match Candidates (>=80%)"), sanitize_csv_value(high_matches)])
        writer.writerow([sanitize_csv_value("Shortlisted Candidates"), sanitize_csv_value(shortlisted_cands)])
    else:
        writer.writerow([sanitize_csv_value("Screening Status"), sanitize_csv_value("No match results recorded yet")])

    writer.writerow([])
    writer.writerow([sanitize_csv_value("=== CANDIDATE RANKING BREAKDOWN ===")])

    # Section 2: Candidate Rankings
    headers = [
        "Rank", "Candidate Name", "Match Score (%)", "Status",
        "Matched Skills", "Missing Skills", "Experience (Yrs)", "Shortlisted", "Recommendation"
    ]
    writer.writerow([sanitize_csv_value(h) for h in headers])

    for idx, r in enumerate(results, 1):
        row = [
            sanitize_csv_value(r.get("rank", idx)),
            sanitize_csv_value(r.get("candidate_name", "N/A")),
            sanitize_csv_value(r.get("composite_score", 0.0)),
            sanitize_csv_value(r.get("badge_level", "N/A")),
            sanitize_csv_value("; ".join(r.get("matched_skills", []))),
            sanitize_csv_value("; ".join(r.get("missing_skills", []))),
            sanitize_csv_value(r.get("candidate_experience", 0.0)),
            sanitize_csv_value(r.get("shortlisted", False)),
            sanitize_csv_value(r.get("recommendation", ""))
        ]
        writer.writerow(row)

    return output.getvalue()


def generate_shortlisted_candidates_csv(
    candidates: List[Dict[str, Any]],
    results: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generates a targeted CSV roster containing only shortlisted candidates.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")

    headers = [
        "Candidate Name",
        "Filename",
        "Match Score (%)",
        "Status Level",
        "Experience (Yrs)",
        "Education",
        "Email",
        "Phone",
        "LinkedIn",
        "GitHub",
        "Total Detected Skills",
        "Key Skills",
        "Recommendation"
    ]
    writer.writerow([sanitize_csv_value(h) for h in headers])

    # Build results lookup map
    results_map = {}
    if results:
        for r in results:
            cid = r.get("candidate_id") or r.get("id")
            if cid:
                results_map[cid] = r
            if r.get("candidate_name"):
                results_map[r["candidate_name"].lower()] = r

    shortlisted = [c for c in candidates if c.get("shortlisted", False)]

    for c in shortlisted:
        res = results_map.get(c.get("id")) or results_map.get(c.get("candidate_name", "").lower(), {})
        contact = c.get("contact", {})
        edu = "; ".join(c.get("education", [])) if c.get("education") else "Extracted in text"
        skills = "; ".join(c.get("all_skills", [])[:12])

        row = [
            sanitize_csv_value(c.get("candidate_name", "Unknown")),
            sanitize_csv_value(c.get("filename", "")),
            sanitize_csv_value(res.get("composite_score", "Pending Evaluation")),
            sanitize_csv_value(res.get("badge_level", "Shortlisted")),
            sanitize_csv_value(c.get("years_of_experience", 0.0)),
            sanitize_csv_value(edu),
            sanitize_csv_value(contact.get("email", "")),
            sanitize_csv_value(contact.get("phone", "")),
            sanitize_csv_value(contact.get("linkedin", "")),
            sanitize_csv_value(contact.get("github", "")),
            sanitize_csv_value(len(c.get("all_skills", []))),
            sanitize_csv_value(skills),
            sanitize_csv_value(res.get("recommendation", "Selected for interview shortlist."))
        ]
        writer.writerow(row)

    return output.getvalue()


def generate_candidate_analysis_report(
    candidate: Dict[str, Any],
    match_result: Optional[Dict[str, Any]] = None,
    job: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a detailed text/markdown assessment dossier for an individual candidate.
    """
    name = candidate.get("candidate_name", "Candidate")
    contact = candidate.get("contact", {})
    edu = ", ".join(candidate.get("education", [])) if candidate.get("education") else "Extracted in resume text"
    exp = candidate.get("years_of_experience", 0.0)
    skills = candidate.get("all_skills", [])

    lines = []
    lines.append("=" * 70)
    lines.append(f"TALENTIQ AI — CANDIDATE INTELLIGENCE DOSSIER: {name.upper()}")
    lines.append("=" * 70)
    lines.append("")
    lines.append("1. CANDIDATE PROFILE OVERVIEW")
    lines.append(f"• Name:                {name}")
    lines.append(f"• Source Document:     {candidate.get('filename', 'N/A')}")
    lines.append(f"• Estimated Tenure:    {exp:.1f} Years of Professional Experience")
    lines.append(f"• Education:           {edu}")
    lines.append(f"• Email:               {contact.get('email') or 'Not specified'}")
    lines.append(f"• Phone:               {contact.get('phone') or 'Not specified'}")
    lines.append(f"• LinkedIn:            {contact.get('linkedin') or 'Not specified'}")
    lines.append(f"• GitHub:              {contact.get('github') or 'Not specified'}")
    lines.append(f"• Shortlist Status:    {'⭐ SHORTLISTED' if candidate.get('shortlisted') else 'Standard Pool'}")
    lines.append("")

    if match_result and job:
        lines.append("2. JOB ALIGNMENT EVALUATION")
        lines.append(f"• Target Role:         {job.get('title', 'N/A')} ({job.get('department', 'General')})")
        lines.append(f"• Overall Match Score: {match_result.get('composite_score', 0.0)}% ({match_result.get('badge_level', 'N/A')})")
        lines.append(f"• Skill Overlap Score: {match_result.get('skill_score', 0.0)}%")
        lines.append(f"• Semantic Alignment:  {match_result.get('semantic_score', 0.0)}%")
        lines.append(f"• Experience Match:    {match_result.get('exp_score', 0.0)}%")
        lines.append("")

        matched_sks = match_result.get("matched_skills", [])
        missing_sks = match_result.get("missing_skills", [])
        lines.append(f"• Matched Required Skills ({len(matched_sks)}):")
        lines.append("  " + (", ".join(matched_sks) if matched_sks else "None"))
        lines.append(f"• Missing Required Skills ({len(missing_sks)}):")
        lines.append("  " + (", ".join(missing_sks) if missing_sks else "Zero missing skills"))
        lines.append("")
        lines.append("3. RECRUITER EVIDENCE & RECOMMENDATION")
        lines.append(f"• Recommendation:      {match_result.get('recommendation', 'N/A')}")
        lines.append(f"• Evidence Narrative:  {match_result.get('evidence_text', 'N/A')}")
        lines.append("")

    lines.append("4. DETECTED SKILL TAXONOMY")
    lines.append(f"• Total Skills Detected: {len(skills)}")
    if skills:
        lines.append("• Skills List: " + ", ".join(skills))
    lines.append("")

    sections = candidate.get("sections", {})
    if sections.get("projects"):
        lines.append("5. RELEVANT PROJECTS (EXTRACTED)")
        lines.append(sections["projects"][:600] + ("..." if len(sections["projects"]) > 600 else ""))
        lines.append("")

    if sections.get("certifications"):
        lines.append("6. CERTIFICATIONS & LICENSES (EXTRACTED)")
        lines.append(sections["certifications"][:600] + ("..." if len(sections["certifications"]) > 600 else ""))
        lines.append("")

    lines.append("=" * 70)
    lines.append("Report generated by TalentIQ AI Autonomous Screening System")
    lines.append("=" * 70)

    return "\n".join(lines)
