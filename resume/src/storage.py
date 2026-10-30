"""
TalentIQ AI - State Management & Storage Module
Maintains candidate pool, job postings, screening history, and real KPI metrics in session state
with automatic persistent SQLite database synchronization and per-user data isolation.
"""

from typing import Dict, List, Any, Optional, Tuple
import time
import streamlit as st
from src.skills import extract_skills
from src.parser import parse_resume
from src.database import (
    db_save_resume,
    db_get_resumes_for_user,
    db_delete_resume,
    db_toggle_shortlist,
    db_get_all_jobs,
    db_save_job,
    db_update_job,
    db_delete_job,
    db_record_screening,
    db_get_screenings_for_user
)

DEFAULT_JOBS = [
    {
        "id": "job_1",
        "title": "Senior Full-Stack Engineer",
        "department": "Engineering",
        "min_experience": 4.0,
        "required_skills": ["React", "TypeScript", "Node.js", "PostgreSQL", "Docker", "AWS", "REST API", "Git"],
        "description": """We are seeking an experienced Senior Full-Stack Engineer to architect and build scalable cloud SaaS applications.
You will work across the stack utilizing React, TypeScript, Next.js, and Node.js with PostgreSQL and Redis backends.
Experience containerizing microservices with Docker and deploying to AWS (ECS, Lambda, RDS) with CI/CD automation is required.
Minimum 4 years of hands-on software development experience."""
    },
    {
        "id": "job_2",
        "title": "AI / Machine Learning Engineer",
        "department": "AI Research & Development",
        "min_experience": 3.0,
        "required_skills": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "NLP", "LLMs", "Docker", "Machine Learning"],
        "description": """TalentIQ AI is hiring an AI / ML Engineer to design state-of-the-art information retrieval, natural language processing,
and semantic matching algorithms. Required proficiency in Python, PyTorch or TensorFlow, Scikit-Learn, and fine-tuning LLMs.
Experience building retrieval-augmented generation (RAG) pipelines, vector databases, and containerized model inference.
Minimum 3 years of ML research or production experience."""
    },
    {
        "id": "job_3",
        "title": "Cloud DevOps & Platform Engineer",
        "department": "Infrastructure & SecOps",
        "min_experience": 3.0,
        "required_skills": ["Kubernetes", "Docker", "AWS", "Terraform", "CI/CD", "Linux", "Python", "Prometheus"],
        "description": """Looking for a talented Cloud DevOps Engineer to scale our zero-downtime infrastructure.
You will manage multi-cluster Kubernetes on AWS (EKS), write infrastructure-as-code using Terraform,
maintain GitHub Actions CI/CD deployment pipelines, and configure observability using Prometheus and Grafana.
Minimum 3 years of DevOps/SRE experience."""
    },
    {
        "id": "job_4",
        "title": "Data Scientist",
        "department": "Data & Analytics",
        "min_experience": 2.0,
        "required_skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Machine Learning", "Tableau", "Data Science", "Statistics"],
        "description": """Seeking a Data Scientist to extract predictive insights from high-dimensional talent data.
Core requirements include strong proficiency in SQL, Python data stacks (Pandas, NumPy, Scikit-Learn),
statistical modeling, hypothesis testing, and building executive dashboards with Tableau or Power BI.
Minimum 2 years of relevant data science experience."""
    }
]


def init_session_state():
    """Initializes TalentIQ AI session state variables if not present."""
    if "candidates" not in st.session_state:
        st.session_state.candidates = []

    if "job_descriptions" not in st.session_state:
        try:
            persisted_jobs = db_get_all_jobs()
            st.session_state.job_descriptions = persisted_jobs if persisted_jobs else list(DEFAULT_JOBS)
        except Exception:
            st.session_state.job_descriptions = list(DEFAULT_JOBS)

    if "selected_job_id" not in st.session_state:
        st.session_state.selected_job_id = (
            st.session_state.job_descriptions[0]["id"]
            if st.session_state.job_descriptions
            else DEFAULT_JOBS[0]["id"]
        )

    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "Dashboard"

    if "admin_nav" not in st.session_state:
        st.session_state.admin_nav = "Admin Overview"

    if "screening_history" not in st.session_state:
        st.session_state.screening_history = []

    if "last_results" not in st.session_state:
        st.session_state.last_results = []

    if "selected_candidate_id" not in st.session_state:
        st.session_state.selected_candidate_id = None

    if "weights" not in st.session_state:
        st.session_state.weights = {
            "skills": 0.50,
            "semantic": 0.35,
            "experience": 0.15
        }

    if "comparison_candidates" not in st.session_state:
        st.session_state.comparison_candidates = []

    # Ensure all candidates have a shortlisted flag
    for c in st.session_state.candidates:
        if "shortlisted" not in c:
            c["shortlisted"] = False


def sync_user_data_on_login(user_id: Optional[int]):
    """Loads and isolates the candidate pool and screening history for the logged-in user from SQLite."""
    init_session_state()
    if not user_id:
        return

    try:
        # Load user-specific resumes
        user_resumes = db_get_resumes_for_user(user_id)
        st.session_state.candidates = user_resumes

        # Load user-specific screenings
        screenings = db_get_screenings_for_user(user_id)
        st.session_state.screening_history = [
            {
                "candidate_name": s["candidate_name"],
                "job_title": s["job_title"],
                "composite_score": s["composite_score"],
                "skill_score": s["skill_score"],
                "semantic_score": s["semantic_score"],
                "matched_skills_count": s["matched_skills_count"],
                "missing_skills_count": s["missing_skills_count"],
                "recommendation": s.get("recommendation", "")
            }
            for s in screenings
        ]
        st.session_state.last_results = []
        st.session_state.comparison_candidates = []
        st.session_state.selected_candidate_id = None
    except Exception:
        pass


def add_candidate_from_file(file_bytes: bytes, filename: str) -> Tuple[Optional[Dict[str, Any]], str, bool]:
    """
    Parses resume, extracts skills & education, registers candidate into session state,
    and persists into SQLite database isolated to current user.
    Returns (candidate_record, message, is_success).
    """
    init_session_state()

    parsed = parse_resume(file_bytes, filename)
    if not parsed["is_valid"]:
        return None, parsed.get("error_message") or "Document validation failed.", False

    # Check for existing candidate by file hash or filename to prevent duplicates
    for cand in st.session_state.candidates:
        if cand.get("file_hash") and cand.get("file_hash") == parsed.get("file_hash"):
            return cand, f"'{filename}' has already been processed and indexed (cached).", True
        if cand.get("filename") == filename:
            return cand, f"'{filename}' is already in the candidate pool.", True

    skills_data = extract_skills(parsed["raw_text"])
    from src.ranker import extract_years_of_experience
    exp_years = extract_years_of_experience(parsed["raw_text"])

    candidate_record = {
        "id": f"cand_{len(st.session_state.candidates) + 1}_{int(time.time())}",
        "candidate_name": parsed["candidate_name"],
        "filename": filename,
        "contact": parsed["contact"],
        "education": parsed.get("education", []),
        "raw_text": parsed["raw_text"],
        "sections": parsed["sections"],
        "word_count": parsed["word_count"],
        "char_count": parsed["char_count"],
        "file_size": parsed["file_size"],
        "file_hash": parsed["file_hash"],
        "status": "Indexed",
        "skills_data": skills_data,
        "all_skills": skills_data["all_skills"],
        "years_of_experience": exp_years,
        "shortlisted": False,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Persist in SQLite for active authenticated user
    curr_user = st.session_state.get("current_user")
    if curr_user and curr_user.get("id"):
        db_save_resume(curr_user["id"], candidate_record)

    st.session_state.candidates.append(candidate_record)
    return candidate_record, f"Successfully parsed and indexed {parsed['candidate_name']} ({len(skills_data['all_skills'])} skills detected).", True


def remove_candidate_by_id(candidate_id: str) -> bool:
    """Removes a candidate from memory and persistent SQLite database."""
    init_session_state()
    initial_len = len(st.session_state.candidates)
    st.session_state.candidates = [c for c in st.session_state.candidates if c.get("id") != candidate_id]
    if "last_results" in st.session_state and st.session_state.last_results:
        st.session_state.last_results = [r for r in st.session_state.last_results if r.get("candidate_id") != candidate_id]

    curr_user = st.session_state.get("current_user")
    uid = curr_user.get("id") if curr_user else None
    db_delete_resume(candidate_id, user_id=uid)

    return len(st.session_state.candidates) < initial_len


def get_candidate_by_id(candidate_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a candidate by ID."""
    init_session_state()
    for c in st.session_state.candidates:
        if c.get("id") == candidate_id:
            return c
    return None


def clear_all_candidates():
    """Wipes the candidate talent pool and associated match logs from memory."""
    init_session_state()
    st.session_state.candidates = []
    st.session_state.screening_history = []
    st.session_state.last_results = []
    st.session_state.selected_candidate_id = None
    st.session_state.comparison_candidates = []


def toggle_candidate_shortlist(candidate_id: str) -> bool:
    """Toggles the shortlisted status for a candidate and updates SQLite."""
    init_session_state()
    for c in st.session_state.candidates:
        if c.get("id") == candidate_id:
            c["shortlisted"] = not c.get("shortlisted", False)
            for r in st.session_state.get("last_results", []):
                if r.get("candidate_id") == candidate_id:
                    r["shortlisted"] = c["shortlisted"]

            curr_user = st.session_state.get("current_user")
            uid = curr_user.get("id") if curr_user else None
            db_toggle_shortlist(candidate_id, user_id=uid)
            return c["shortlisted"]
    return False


def set_candidate_shortlist(candidate_id: str, shortlisted: bool) -> bool:
    """Sets the shortlisted status for a candidate."""
    init_session_state()
    for c in st.session_state.candidates:
        if c.get("id") == candidate_id:
            c["shortlisted"] = shortlisted
            for r in st.session_state.get("last_results", []):
                if r.get("candidate_id") == candidate_id:
                    r["shortlisted"] = shortlisted
            curr_user = st.session_state.get("current_user")
            uid = curr_user.get("id") if curr_user else None
            curr_val = db_toggle_shortlist(candidate_id, user_id=uid)
            if curr_val != shortlisted:
                db_toggle_shortlist(candidate_id, user_id=uid)
            return True
    return False


def get_shortlisted_candidates() -> List[Dict[str, Any]]:
    """Returns all shortlisted candidates."""
    init_session_state()
    return [c for c in st.session_state.candidates if c.get("shortlisted", False)]


def get_total_jobs_analyzed() -> int:
    """Returns number of unique jobs analyzed across history and current state."""
    init_session_state()
    history = st.session_state.screening_history
    unique_history_jobs = set(h.get("job_title") for h in history if h.get("job_title"))
    if unique_history_jobs:
        return len(unique_history_jobs)
    if st.session_state.get("last_results"):
        return 1
    return 0


def get_kpis() -> Dict[str, Any]:
    """Calculates real KPI statistics from current candidate data and screening history."""
    init_session_state()
    candidates = st.session_state.candidates
    total_candidates = len(candidates)
    history = st.session_state.screening_history
    screenings_count = len(history)

    # Real average match score
    if history:
        avg_score = round(sum(h.get("composite_score", 0.0) for h in history) / len(history), 1)
    elif st.session_state.get("last_results"):
        avg_score = round(sum(r.get("composite_score", 0.0) for r in st.session_state.last_results) / len(st.session_state.last_results), 1)
    else:
        avg_score = 0.0

    # Shortlisted count
    shortlisted_count = len([c for c in candidates if c.get("shortlisted", False)])

    # Real top skill frequency across all candidates
    skill_counts: Dict[str, int] = {}
    for c in candidates:
        for sk in c.get("all_skills", []):
            skill_counts[sk] = skill_counts.get(sk, 0) + 1

    top_skill = "None yet"
    top_skill_count = 0
    if skill_counts:
        top_skill, top_skill_count = max(skill_counts.items(), key=lambda x: x[1])

    total_jobs_analyzed = get_total_jobs_analyzed()

    return {
        "total_candidates": total_candidates,
        "screenings_count": screenings_count,
        "avg_match_score": avg_score,
        "top_skill": top_skill,
        "top_skill_count": top_skill_count,
        "active_jobs_count": len(st.session_state.job_descriptions),
        "shortlisted_count": shortlisted_count,
        "total_jobs_analyzed": total_jobs_analyzed
    }


def record_screening_event(results: List[Dict[str, Any]], job_title: str):
    """Appends match screening run to history log and persists to SQLite."""
    init_session_state()
    curr_user = st.session_state.get("current_user")
    uid = curr_user.get("id") if curr_user else None

    for res in results:
        event = {
            "candidate_name": res["candidate_name"],
            "job_title": job_title,
            "composite_score": res["composite_score"],
            "skill_score": res["skill_score"],
            "semantic_score": res["semantic_score"],
            "matched_skills_count": len(res.get("matched_skills", [])),
            "missing_skills_count": len(res.get("missing_skills", []))
        }
        st.session_state.screening_history.append(event)
        if uid:
            db_record_screening(uid, event)


def get_current_job() -> Dict[str, Any]:
    """Returns currently selected job object."""
    init_session_state()
    sel_id = st.session_state.selected_job_id
    for j in st.session_state.job_descriptions:
        if j["id"] == sel_id:
            return j
    return st.session_state.job_descriptions[0]


def update_job_description(job_id: str, new_desc: str):
    """Updates job description text in session state and SQLite database."""
    init_session_state()
    for j in st.session_state.job_descriptions:
        if j["id"] == job_id:
            j["description"] = new_desc
            break
    db_update_job(job_id, {"description": new_desc})


def add_new_job_description(job_dict: Dict[str, Any], created_by: Optional[int] = None) -> bool:
    """Adds a new job description to memory and persistent SQLite database."""
    init_session_state()
    st.session_state.job_descriptions.append(job_dict)
    return db_save_job(job_dict, created_by=created_by)


def delete_job_description(job_id: str) -> bool:
    """Removes a job description from memory and SQLite."""
    init_session_state()
    st.session_state.job_descriptions = [j for j in st.session_state.job_descriptions if j["id"] != job_id]
    if st.session_state.selected_job_id == job_id and st.session_state.job_descriptions:
        st.session_state.selected_job_id = st.session_state.job_descriptions[0]["id"]
    return db_delete_job(job_id)
