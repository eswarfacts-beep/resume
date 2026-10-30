"""
TalentIQ AI - Persistence & Session Storage Module
Provides local file-based persistence for screening sessions, candidate pools,
job definitions, match scores, and shortlist states.
"""

import os
import json
import time
import uuid
import datetime
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st


def get_storage_dir() -> str:
    """Returns the absolute path to the sessions storage directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage_dir = os.path.join(base_dir, "data", "sessions")
    os.makedirs(storage_dir, exist_ok=True)
    return storage_dir


def _clean_for_json(data: Any) -> Any:
    """Recursively converts sets, bytes, or non-serializable objects into JSON-safe formats."""
    if isinstance(data, dict):
        return {k: _clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [_clean_for_json(v) for v in data]
    elif isinstance(data, set):
        return sorted(list(data))
    elif isinstance(data, bytes):
        return data.decode("utf-8", errors="ignore")
    elif isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    return data


def save_session(
    name: str,
    job: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    last_results: List[Dict[str, Any]],
    weights: Optional[Dict[str, float]] = None,
    screening_history: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Saves a screening session to disk as a JSON file.
    Returns the saved session metadata dictionary.
    """
    storage_dir = get_storage_dir()
    now_iso = datetime.datetime.now().isoformat()
    
    if not session_id:
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_suffix = uuid.uuid4().hex[:6]
        session_id = f"sess_{timestamp_str}_{rand_suffix}"

    display_name = name.strip() if name and name.strip() else f"Screening - {job.get('title', 'Role')} ({datetime.datetime.now().strftime('%b %d, %Y')})"

    # Calculate summary metadata
    cand_count = len(candidates)
    shortlisted_count = len([c for c in candidates if c.get("shortlisted", False)])
    if last_results:
        avg_score = round(sum(r.get("composite_score", 0.0) for r in last_results) / len(last_results), 1)
        top_score = max(r.get("composite_score", 0.0) for r in last_results)
    else:
        avg_score = 0.0
        top_score = 0.0

    session_record = {
        "session_id": session_id,
        "name": display_name,
        "created_at": now_iso,
        "updated_at": now_iso,
        "job": _clean_for_json(job),
        "candidates": _clean_for_json(candidates),
        "last_results": _clean_for_json(last_results),
        "weights": weights or {"skills": 0.50, "semantic": 0.35, "experience": 0.15},
        "screening_history": _clean_for_json(screening_history or []),
        "metadata": {
            "candidate_count": cand_count,
            "shortlisted_count": shortlisted_count,
            "avg_score": avg_score,
            "top_score": top_score,
            "job_title": job.get("title", "Untitled Role")
        }
    }

    file_path = os.path.join(storage_dir, f"{session_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(session_record, f, indent=2, ensure_ascii=False)

    return session_record


def load_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Loads and returns a saved session by ID, or None if not found."""
    storage_dir = get_storage_dir()
    file_path = os.path.join(storage_dir, f"{session_id}.json")
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def list_sessions() -> List[Dict[str, Any]]:
    """Lists all saved sessions metadata sorted from newest to oldest."""
    storage_dir = get_storage_dir()
    sessions = []
    
    if not os.path.exists(storage_dir):
        return []

    for fname in os.listdir(storage_dir):
        if fname.endswith(".json"):
            file_path = os.path.join(storage_dir, fname)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions.append({
                        "session_id": data.get("session_id", fname[:-5]),
                        "name": data.get("name", "Untitled Session"),
                        "created_at": data.get("created_at", ""),
                        "updated_at": data.get("updated_at", ""),
                        "job_title": data.get("metadata", {}).get("job_title") or data.get("job", {}).get("title", "Role"),
                        "candidate_count": data.get("metadata", {}).get("candidate_count", len(data.get("candidates", []))),
                        "shortlisted_count": data.get("metadata", {}).get("shortlisted_count", 0),
                        "avg_score": data.get("metadata", {}).get("avg_score", 0.0),
                        "top_score": data.get("metadata", {}).get("top_score", 0.0),
                        "file_size": os.path.getsize(file_path)
                    })
            except Exception:
                continue

    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    """Deletes a saved session file by ID."""
    storage_dir = get_storage_dir()
    file_path = os.path.join(storage_dir, f"{session_id}.json")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except OSError:
            return False
    return False


def export_session_json(session_id: str) -> Optional[str]:
    """Returns JSON string for exporting session."""
    data = load_session(session_id)
    if data:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return None


def import_session_json(json_content: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Validates and imports a session JSON string into storage."""
    try:
        data = json.loads(json_content)
        if not isinstance(data, dict) or "candidates" not in data or "job" not in data:
            return False, "Invalid session format: missing required candidate or job data.", None

        # Re-assign unique ID to avoid accidental overwrite
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_suffix = uuid.uuid4().hex[:6]
        new_session_id = f"sess_imported_{timestamp_str}_{rand_suffix}"
        data["session_id"] = new_session_id
        data["name"] = f"[Imported] {data.get('name', 'Screening Session')}"

        storage_dir = get_storage_dir()
        file_path = os.path.join(storage_dir, f"{new_session_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True, "Session imported successfully.", data
    except Exception as e:
        return False, f"Failed to parse session JSON: {str(e)}", None


def restore_session_to_memory(session_data: Dict[str, Any]) -> bool:
    """Restores saved session state into active Streamlit session state."""
    try:
        from src.storage import init_session_state
        init_session_state()

        if "candidates" in session_data:
            st.session_state.candidates = list(session_data["candidates"])

        if "last_results" in session_data:
            st.session_state.last_results = list(session_data["last_results"])

        if "weights" in session_data:
            st.session_state.weights = dict(session_data["weights"])

        if "screening_history" in session_data:
            st.session_state.screening_history = list(session_data["screening_history"])

        # Restore target job if present
        saved_job = session_data.get("job")
        if saved_job and "id" in saved_job:
            # Check if this job exists in job_descriptions, else insert/update
            job_found = False
            for j in st.session_state.job_descriptions:
                if j["id"] == saved_job["id"]:
                    j.update(saved_job)
                    job_found = True
                    break
            if not job_found:
                st.session_state.job_descriptions.append(saved_job)
            st.session_state.selected_job_id = saved_job["id"]

        st.session_state.selected_candidate_id = None
        st.session_state.active_session_name = session_data.get("name", "Screening Session")
        st.session_state.active_session_id = session_data.get("session_id")
        return True
    except Exception:
        return False

