"""
TalentIQ AI - Advanced Analytics & Charting Engine
Calculates recruitment intelligence metrics, score segmentations, skill demand/gap analytics,
and renders Plotly data visualizations using actual application data.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.skills import get_skill_category


# Global Dark Theme Palette for TalentIQ AI Plotly charts
THEME_BG = "#0F172A"
THEME_PAPER = "#0B1120"
THEME_TEXT = "#F8FAFC"
THEME_GRID = "rgba(255, 255, 255, 0.08)"
COLOR_PRIMARY = "#4F46E5"
COLOR_ROYAL = "#2563EB"
COLOR_CYAN = "#06B6D4"
COLOR_VIOLET = "#7C3AED"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#EF4444"


def apply_talentiq_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Applies the commercial dark SaaS aesthetic to a Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Plus Jakarta Sans, sans-serif", size=15, color="#FFFFFF"),
            x=0.02,
            y=0.96
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.6)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=THEME_TEXT, size=12),
        margin=dict(l=40, r=30, t=50, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor=THEME_GRID,
            zeroline=False,
            color="#94A3B8"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=THEME_GRID,
            zeroline=False,
            color="#94A3B8"
        ),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(color="#CBD5E1", size=11)
        )
    )
    return fig


def compute_analytics_summary(
    candidates: List[Dict[str, Any]],
    screening_history: List[Dict[str, Any]],
    last_results: List[Dict[str, Any]],
    jobs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes accurate, un-fabricated analytics summary metrics from real app state.
    """
    total_candidates = len(candidates)
    shortlisted_candidates = len([c for c in candidates if c.get("shortlisted", False)])

    # All match events (either from history or current results)
    all_scores = [h["composite_score"] for h in screening_history if "composite_score" in h]
    if not all_scores and last_results:
        all_scores = [r["composite_score"] for r in last_results if "composite_score" in r]

    avg_match_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    # Total jobs analyzed
    unique_jobs_analyzed = set(h.get("job_title") for h in screening_history if h.get("job_title"))
    if not unique_jobs_analyzed and last_results:
        unique_jobs_analyzed = {jobs[0].get("title", "Role")} if jobs else {"Current Role"}
    total_jobs_analyzed = len(unique_jobs_analyzed)

    # Score buckets / ranges
    score_ranges = {
        "High Match (80-100%)": 0,
        "Good Match (65-79%)": 0,
        "Review Needed (50-64%)": 0,
        "Low Alignment (<50%)": 0
    }
    
    # Bucket from active results or history
    score_source = last_results if last_results else screening_history
    for item in score_source:
        score = item.get("composite_score", 0.0)
        if score >= 80.0:
            score_ranges["High Match (80-100%)"] += 1
        elif score >= 65.0:
            score_ranges["Good Match (65-79%)"] += 1
        elif score >= 50.0:
            score_ranges["Review Needed (50-64%)"] += 1
        else:
            score_ranges["Low Alignment (<50%)"] += 1

    # Detected skills frequency
    skill_counts: Dict[str, int] = {}
    for c in candidates:
        for s in c.get("all_skills", []):
            skill_counts[s] = skill_counts.get(s, 0) + 1

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

    # In-demand skills across job definitions
    job_demand_counts: Dict[str, int] = {}
    for j in jobs:
        for s in j.get("required_skills", []):
            job_demand_counts[s] = job_demand_counts.get(s, 0) + 1

    # Missing skills across evaluated candidates
    missing_skill_counts: Dict[str, int] = {}
    for r in last_results:
        for ms in r.get("missing_skills", []):
            missing_skill_counts[ms] = missing_skill_counts.get(ms, 0) + 1

    return {
        "total_resumes": total_candidates,
        "total_jobs_analyzed": total_jobs_analyzed,
        "avg_match_score": avg_match_score,
        "shortlisted_count": shortlisted_candidates,
        "score_ranges": score_ranges,
        "top_skills": top_skills,
        "job_demand_counts": job_demand_counts,
        "missing_skill_counts": missing_skill_counts,
        "has_evaluations": len(all_scores) > 0
    }


def create_score_distribution_chart(score_ranges: Dict[str, int]) -> go.Figure:
    """Builds a bar chart showing candidate distribution across match-score ranges."""
    categories = list(score_ranges.keys())
    counts = list(score_ranges.values())
    colors = [COLOR_SUCCESS, COLOR_ROYAL, COLOR_WARNING, COLOR_DANGER]

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=counts,
                marker=dict(
                    color=colors,
                    line=dict(color="rgba(255,255,255,0.2)", width=1.5)
                ),
                text=counts,
                textposition="auto",
                textfont=dict(color="#FFFFFF", size=13, family="Plus Jakarta Sans"),
                hoverinfo="x+y"
            )
        ]
    )
    fig.update_layout(
        yaxis_title="Candidates",
        xaxis_title="Match Alignment Tier",
        height=320
    )
    return apply_talentiq_theme(fig, "Candidate Distribution by Match-Score Ranges")


def create_top_skills_chart(top_skills: List[Tuple[str, int]], max_items: int = 12) -> go.Figure:
    """Builds a horizontal bar chart of the most frequently detected skills."""
    if not top_skills:
        fig = go.Figure()
        return apply_talentiq_theme(fig, "Top Detected Skills (No Data)")

    items = top_skills[:max_items][::-1]
    skills = [item[0] for item in items]
    counts = [item[1] for item in items]

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts,
                y=skills,
                orientation="h",
                marker=dict(
                    color="#4F46E5",
                    line=dict(color="#818CF8", width=1.2)
                ),
                text=counts,
                textposition="auto",
                textfont=dict(color="#FFFFFF", size=11),
                hovertemplate="<b>%{y}</b>: %{x} candidates<extra></extra>"
            )
        ]
    )
    fig.update_layout(
        xaxis_title="Candidate Count",
        height=340
    )
    return apply_talentiq_theme(fig, f"Top {len(items)} Skills Detected in Talent Pool")


def create_skill_demand_vs_missing_chart(
    demand_counts: Dict[str, int],
    missing_counts: Dict[str, int],
    max_items: int = 8
) -> go.Figure:
    """
    Builds a grouped bar chart comparing in-demand job skills against
    candidate skill gap occurrences.
    """
    all_keys = set(demand_counts.keys()).union(set(missing_counts.keys()))
    if not all_keys:
        fig = go.Figure()
        return apply_talentiq_theme(fig, "In-Demand vs Missing Skills (No Data)")

    # Sort by demand first, then by missing
    sorted_keys = sorted(all_keys, key=lambda k: (demand_counts.get(k, 0), missing_counts.get(k, 0)), reverse=True)[:max_items]

    demands = [demand_counts.get(k, 0) for k in sorted_keys]
    missings = [missing_counts.get(k, 0) for k in sorted_keys]

    fig = go.Figure(
        data=[
            go.Bar(
                name="Job Role In-Demand",
                x=sorted_keys,
                y=demands,
                marker=dict(color=COLOR_CYAN, line=dict(color="#22D3EE", width=1))
            ),
            go.Bar(
                name="Candidate Skill Gap (Missing)",
                x=sorted_keys,
                y=missings,
                marker=dict(color=COLOR_DANGER, line=dict(color="#F87171", width=1))
            )
        ]
    )
    fig.update_layout(
        barmode="group",
        yaxis_title="Frequency",
        xaxis_title="Skill",
        height=320
    )
    return apply_talentiq_theme(fig, "In-Demand Skills vs Talent Pool Gaps")


def create_job_wise_results_chart(
    screening_history: List[Dict[str, Any]],
    last_results: List[Dict[str, Any]],
    current_job_title: str = ""
) -> go.Figure:
    """
    Builds a chart showing job-wise screening performance (average match score & candidates screened).
    """
    job_stats: Dict[str, List[float]] = {}
    
    for h in screening_history:
        jt = h.get("job_title", "Unknown Role")
        score = h.get("composite_score")
        if score is not None:
            if jt not in job_stats:
                job_stats[jt] = []
            job_stats[jt].append(score)

    if not job_stats and last_results:
        jt = current_job_title or "Current Target Role"
        job_stats[jt] = [r["composite_score"] for r in last_results if "composite_score" in r]

    if not job_stats:
        fig = go.Figure()
        return apply_talentiq_theme(fig, "Job-Wise Screening Results (No Match Data)")

    roles = []
    avg_scores = []
    cand_counts = []

    for role, scores in job_stats.items():
        roles.append(role)
        avg_scores.append(round(sum(scores) / len(scores), 1))
        cand_counts.append(len(scores))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=roles,
            y=avg_scores,
            name="Average Match Score (%)",
            marker=dict(color=COLOR_VIOLET, line=dict(color="#A78BFA", width=1.2)),
            text=[f"{s}%" for s in avg_scores],
            textposition="auto"
        )
    )
    fig.update_layout(
        yaxis_title="Average Match Score (%)",
        yaxis=dict(range=[0, 100]),
        height=320
    )
    return apply_talentiq_theme(fig, "Job-Wise Average Match Scores")

