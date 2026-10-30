"""
TalentIQ AI - AI-Powered Resume Screening & Job Matching System
Enterprise-grade Streamlit application.
Commercial SaaS Design System: Deep Navy, Royal Blue, Electric Indigo, Violet, Cyan.
"""

import time
import json
import os
import sys
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path so 'src' packages always resolve regardless of launch directory
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Streamlit Page Configuration must be the first command
st.set_page_config(
    page_title="TalentIQ AI | Autonomous Resume Screening & Job Matching",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.styles import (
    clean_html,
    get_css,
    get_logo_svg,
    render_header,
    render_hero,
    render_kpi_card,
    render_score_badge,
    render_skill_badge,
    render_empty_state,
    render_progress_bar,
    render_evidence_card,
    render_staged_file_badge,
    render_shortlist_badge,
    render_user_profile_pill,
    render_admin_header,
    render_portal_card
)
from src.auth import (
    init_auth_state,
    authenticate_user,
    register_user,
    request_password_reset,
    complete_password_reset,
    sign_in_user,
    sign_out_user,
    get_current_user,
    is_authenticated,
    require_role,
    validate_password_strength,
    validate_email_format,
    hash_password,
    verify_password
)
from src.admin import render_admin_dashboard
from src.database import get_user_by_id, update_user_profile
from src.parser import parse_resume, clean_text, extract_sections
from src.skills import extract_skills, get_skill_category, normalize_skill_name
from src.matcher import (
    rank_candidates_for_job,
    match_candidate_to_job,
    generate_match_evidence,
    extract_key_semantic_terms
)
from src.storage import (
    init_session_state,
    add_candidate_from_file,
    remove_candidate_by_id,
    get_candidate_by_id,
    clear_all_candidates,
    get_kpis,
    record_screening_event,
    get_current_job,
    update_job_description,
    toggle_candidate_shortlist,
    set_candidate_shortlist,
    get_shortlisted_candidates,
    get_total_jobs_analyzed,
    DEFAULT_JOBS
)
from src.candidate_manager import filter_and_sort_candidates
from src.comparison import build_comparison_matrix, extract_candidate_comparison_data
from src.analytics import (
    compute_analytics_summary,
    create_score_distribution_chart,
    create_top_skills_chart,
    create_skill_demand_vs_missing_chart,
    create_job_wise_results_chart
)
from src.reports import (
    sanitize_csv_value,
    generate_candidate_ranking_csv,
    generate_job_screening_summary_csv,
    generate_shortlisted_candidates_csv,
    generate_candidate_analysis_report
)
from src.persistence import (
    save_session,
    load_session,
    list_sessions,
    delete_session,
    export_session_json,
    import_session_json,
    restore_session_to_memory
)
from src.builder import (
    prefill_resume_from_candidate,
    generate_resume_pdf
)

# Apply global master CSS
st.markdown(get_css(), unsafe_allow_html=True)

# Initialize Session State
init_session_state()
init_auth_state()

# ==============================================================================
# AUTHENTICATION & PORTAL SELECTION GATEWAY
# ==============================================================================
if not is_authenticated():
    auth_view = st.session_state.get("auth_view", "landing")

    # --------------------------------------------------------------------------
    # VIEW A: MAIN LANDING PAGE
    # --------------------------------------------------------------------------
    if auth_view == "landing":
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

        # Header / Brand Hero
        st.markdown(
            clean_html(f"""
            <div style="text-align: center; margin-bottom: 2.5rem;">
                <div style="display: inline-block; margin-bottom: 12px;">
                    {get_logo_svg(width=58, height=58, show_text=True)}
                </div>
                <h1 style="font-size: 2.45rem; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; margin: 16px 0 10px 0;">
                    AI Resume Screening &amp; Job Matching System
                </h1>
                <p style="font-size: 1.05rem; color: #94A3B8; max-width: 720px; margin: 0 auto; line-height: 1.6;">
                    Enterprise talent intelligence engineered with TF-IDF semantic cosine vectors and automated skill ontology extraction. Select your authorized portal below to proceed.
                </p>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Dual Portal Cards
        c_left, c_right = st.columns(2, gap="large")

        with c_left:
            st.markdown(
                render_portal_card(
                    portal_type="user",
                    title="User Portal",
                    subtitle="Designed for talent partners, recruiters, and hiring managers evaluating candidates against open positions.",
                    features=[
                        "Upload and process resumes in PDF & DOCX formats",
                        "Extract 300+ technical, cloud, AI, and soft skills",
                        "Compute semantic job match scores & ranking",
                        "Side-by-side multi-candidate comparison matrix",
                        "Tailored Resume Builder & PDF export suite",
                        "Download comprehensive CSV screening reports"
                    ],
                    badge_text="Candidate Screening Workspace"
                ),
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            col_u_btn1, col_u_btn2 = st.columns(2)
            with col_u_btn1:
                if st.button("👤 User Login", key="btn_goto_user_login", use_container_width=True):
                    st.session_state.auth_view = "user_login"
                    st.rerun()
            with col_u_btn2:
                if st.button("📝 Register Account", key="btn_goto_user_register", use_container_width=True):
                    st.session_state.auth_view = "user_register"
                    st.rerun()

        with c_right:
            st.markdown(
                render_portal_card(
                    portal_type="admin",
                    title="Admin Portal",
                    subtitle="Dedicated administrative console for system governance, user permissions, audit monitoring, and taxonomy.",
                    features=[
                        "Strict role-based authorization & tamper verification",
                        "User account administration (Activate / Deactivate / Roles)",
                        "Monitor global resume processing & metadata telemetry",
                        "Publish, edit, and maintain active job postings",
                        "System security audit trail & activity logging",
                        "Real-time platform KPI analytics & administrative exports"
                    ],
                    badge_text="Privileged System Controls"
                ),
                unsafe_allow_html=True
            )
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("🛡️ Admin Login", key="btn_goto_admin_login", use_container_width=True):
                st.session_state.auth_view = "admin_login"
                st.rerun()

        st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

        # Evaluation & Architecture Banner
        st.markdown(
            clean_html("""
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 18px 22px; max-width: 900px; margin: 0 auto;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <div style="font-size: 0.82rem; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.06em;">
                            ⚡ Rapid Hackathon Evaluation Credentials
                        </div>
                        <div style="font-size: 0.85rem; color: #CBD5E1; margin-top: 4px;">
                            <strong>User Portal:</strong> <code>user@talentiq.ai</code> / <code>User@TalentIQ2026</code> &middot; 
                            <strong>Admin Portal:</strong> <code>admin@talentiq.ai</code> / <code>Admin@TalentIQ2026</code>
                        </div>
                    </div>
                    <div style="font-size: 0.75rem; color: #94A3B8; text-align: right;">
                        🔒 Bcrypt 12-Round Hashes &middot; SQLite WAL Engine &middot; Strict RBAC
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        st.stop()

    # --------------------------------------------------------------------------
    # VIEW B: USER LOGIN
    # --------------------------------------------------------------------------
    elif auth_view == "user_login":
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        _, col_box, _ = st.columns([1.1, 1.8, 1.1])
        with col_box:
            st.markdown(
                clean_html(f"""
                <div class="tiq-login-card">
                    <div style="text-align: center; margin-bottom: 20px;">
                        {get_logo_svg(width=50, height=50, show_text=True)}
                        <h2 style="font-size: 1.55rem; font-weight: 800; color: #FFFFFF; margin: 16px 0 6px 0;">User Portal Sign In</h2>
                        <div style="font-size: 0.84rem; color: #94A3B8;">Candidate Screening &amp; Talent Intelligence Workspace</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            show_pwd_u = st.checkbox("Show password", key="chk_show_user_pwd")
            pwd_type_u = "default" if show_pwd_u else "password"

            with st.form("user_login_form"):
                u_email = st.text_input("User Email Address", placeholder="e.g. user@talentiq.ai", key="u_login_email_input")
                u_pass = st.text_input("Password", type=pwd_type_u, placeholder="Enter your password...", key="u_login_password_input")
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                col_ub1, col_ub2 = st.columns([1.4, 1.6])
                with col_ub1:
                    u_submit = st.form_submit_button("👤 Sign In", use_container_width=True)
                with col_ub2:
                    u_demo = st.form_submit_button("⚡ One-Click Demo User", use_container_width=True)

            if u_submit:
                ok, msg, u_record = authenticate_user(u_email, u_pass, expected_role="user")
                if ok and u_record:
                    sign_in_user(u_record)
                    st.success(f"Welcome back, {u_record['name']}! Opening User Dashboard...")
                    time.sleep(0.1)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

            if u_demo:
                ok, msg, u_record = authenticate_user("user@talentiq.ai", "User@TalentIQ2026", expected_role="user")
                if ok and u_record:
                    sign_in_user(u_record)
                    st.success("Signed in with Evaluator Demo Account!")
                    time.sleep(0.1)
                    st.rerun()

            col_link1, col_link2 = st.columns(2)
            with col_link1:
                if st.button("🔑 Forgot Password?", key="user_forgot_pwd_btn", use_container_width=True):
                    st.session_state.auth_view = "forgot_password"
                    st.rerun()
            with col_link2:
                if st.button("📝 Register New Account", key="user_to_register_btn", use_container_width=True):
                    st.session_state.auth_view = "user_register"
                    st.rerun()

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to Portal Selection", key="user_back_to_landing", use_container_width=True):
                st.session_state.auth_view = "landing"
                st.rerun()

        st.stop()

    # --------------------------------------------------------------------------
    # VIEW C: USER REGISTRATION
    # --------------------------------------------------------------------------
    elif auth_view == "user_register":
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        _, col_box, _ = st.columns([1.1, 1.8, 1.1])
        with col_box:
            st.markdown(
                clean_html(f"""
                <div class="tiq-login-card">
                    <div style="text-align: center; margin-bottom: 20px;">
                        {get_logo_svg(width=50, height=50, show_text=True)}
                        <h2 style="font-size: 1.55rem; font-weight: 800; color: #FFFFFF; margin: 16px 0 6px 0;">Create User Account</h2>
                        <div style="font-size: 0.84rem; color: #94A3B8;">Register for autonomous resume screening &amp; job matching</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            show_pwd_r = st.checkbox("Show password", key="chk_show_reg_pwd")
            pwd_type_r = "default" if show_pwd_r else "password"

            with st.form("user_registration_form"):
                reg_name = st.text_input("Full Name *", placeholder="e.g. Alex Mercer", key="reg_name_input")
                reg_email = st.text_input("Work or Personal Email *", placeholder="e.g. alex.mercer@company.com", key="reg_email_input")
                reg_pwd = st.text_input("Password * (8+ chars, letters & numbers)", type=pwd_type_r, placeholder="Enter secure password...", key="reg_pwd_input")
                reg_pwd_confirm = st.text_input("Confirm Password *", type=pwd_type_r, placeholder="Re-enter password...", key="reg_pwd_confirm_input")
                
                st.markdown(
                    clean_html("""
                    <div style="font-size: 0.74rem; color: #94A3B8; margin: 4px 0 10px 0;">
                        Password requirements: At least 8 characters, at least 1 alphabet character, and at least 1 number.
                    </div>
                    """),
                    unsafe_allow_html=True
                )
                reg_submit = st.form_submit_button("🚀 Create Account", use_container_width=True)

            if reg_submit:
                ok, msg, new_user = register_user(
                    email=reg_email,
                    password=reg_pwd,
                    confirm_password=reg_pwd_confirm,
                    full_name=reg_name
                )
                if ok and new_user:
                    sign_in_user(new_user)
                    st.success("🎉 Account created successfully! Launching your workspace...")
                    time.sleep(0.1)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("Already have an account? Sign In", key="reg_to_signin_btn", use_container_width=True):
                    st.session_state.auth_view = "user_login"
                    st.rerun()
            with col_r2:
                if st.button("← Back to Portal Selection", key="reg_back_to_landing", use_container_width=True):
                    st.session_state.auth_view = "landing"
                    st.rerun()

        st.stop()

    # --------------------------------------------------------------------------
    # VIEW D: ADMIN LOGIN (DEDICATED SEPARATE PORTAL)
    # --------------------------------------------------------------------------
    elif auth_view == "admin_login":
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        _, col_box, _ = st.columns([1.1, 1.8, 1.1])
        with col_box:
            st.markdown(
                clean_html(f"""
                <div class="tiq-login-card" style="border-color: rgba(239, 68, 68, 0.45); box-shadow: 0 0 35px rgba(239, 68, 68, 0.15);">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 14px; background: linear-gradient(135deg, #7C3AED 0%, #EF4444 100%); margin-bottom: 12px; box-shadow: 0 8px 20px rgba(239, 68, 68, 0.35);">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        </div>
                        <h2 style="font-size: 1.6rem; font-weight: 800; color: #FFFFFF; margin: 4px 0 6px 0;">Admin Portal Sign In</h2>
                        <div style="font-size: 0.82rem; color: #FCA5A5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">
                            Restricted Privileged Gateway
                        </div>
                    </div>
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 10px; padding: 10px 14px; font-size: 0.78rem; color: #FCA5A5; line-height: 1.5; margin-bottom: 16px;">
                        ⚠️ <strong>Restricted Security Zone:</strong> Only verified administrator accounts can authenticate here. Unauthorized access attempts are monitored and recorded in the audit trail.
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            show_pwd_a = st.checkbox("Show password", key="chk_show_admin_pwd")
            pwd_type_a = "default" if show_pwd_a else "password"

            with st.form("admin_login_form"):
                a_email = st.text_input("Administrator Email", placeholder="e.g. admin@talentiq.ai", key="a_login_email_input")
                a_pass = st.text_input("Administrator Password", type=pwd_type_a, placeholder="Enter administrator password...", key="a_login_password_input")
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                col_ab1, col_ab2 = st.columns([1.5, 1.5])
                with col_ab1:
                    a_submit = st.form_submit_button("🛡️ Authenticate Admin", use_container_width=True)
                with col_ab2:
                    a_demo = st.form_submit_button("⚡ One-Click Demo Admin", use_container_width=True)

            if a_submit:
                ok, msg, a_record = authenticate_user(a_email, a_pass, expected_role="admin")
                if ok and a_record:
                    sign_in_user(a_record)
                    st.success("Administrator authenticated! Launching Operations Console...")
                    time.sleep(0.1)
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

            if a_demo:
                ok, msg, a_record = authenticate_user("admin@talentiq.ai", "Admin@TalentIQ2026", expected_role="admin")
                if ok and a_record:
                    sign_in_user(a_record)
                    st.success("Signed in with Evaluator Demo Administrator Account!")
                    time.sleep(0.1)
                    st.rerun()

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if st.button("← Back to Portal Selection", key="admin_back_to_landing", use_container_width=True):
                st.session_state.auth_view = "landing"
                st.rerun()

        st.stop()

    # --------------------------------------------------------------------------
    # VIEW E: FORGOT PASSWORD
    # --------------------------------------------------------------------------
    elif auth_view == "forgot_password":
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        _, col_box, _ = st.columns([1.1, 1.8, 1.1])
        with col_box:
            st.markdown(
                clean_html(f"""
                <div class="tiq-login-card">
                    <div style="text-align: center; margin-bottom: 20px;">
                        {get_logo_svg(width=50, height=50, show_text=True)}
                        <h2 style="font-size: 1.55rem; font-weight: 800; color: #FFFFFF; margin: 16px 0 6px 0;">Password Recovery</h2>
                        <div style="font-size: 0.84rem; color: #94A3B8;">Reset account credentials securely via verification code</div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Step 1: Request Code
            st.markdown("##### Step 1: Generate Verification Code")
            col_req1, col_req2 = st.columns([2.2, 1.2])
            with col_req1:
                reset_email = st.text_input("Account Email", placeholder="e.g. user@talentiq.ai", key="reset_email_input")
            with col_req2:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                send_code_btn = st.button("Send Code", key="btn_send_reset_code", use_container_width=True)

            if send_code_btn:
                ok, msg, gen_code = request_password_reset(reset_email)
                if ok and gen_code:
                    st.session_state.active_reset_code = gen_code
                    st.session_state.active_reset_email = reset_email.strip().lower()
                    st.success(f"Verification code generated: **`{gen_code}`** (Valid for 15 minutes)")
                elif ok:
                    st.info(msg)
                else:
                    st.error(msg)

            # Step 2: Enter code & new password
            st.markdown("---")
            st.markdown("##### Step 2: Set New Password")
            prefill_code = st.session_state.get("active_reset_code", "")
            with st.form("complete_password_reset_form"):
                code_entered = st.text_input("8-Character Verification Code", value=prefill_code, key="reset_code_input")
                new_pw = st.text_input("New Password (8+ characters, letters & digits)", type="password", key="new_pw_input")
                confirm_new_pw = st.text_input("Confirm New Password", type="password", key="confirm_new_pw_input")
                submit_new_pw = st.form_submit_button("Reset Password", use_container_width=True)

            if submit_new_pw:
                target_email = reset_email or st.session_state.get("active_reset_email", "")
                ok, msg = complete_password_reset(target_email, code_entered, new_pw, confirm_new_pw)
                if ok:
                    st.success(f"✅ {msg}")
                    st.info("You can now sign in using your updated password.")
                    if st.button("Proceed to Sign In", key="goto_signin_after_reset"):
                        st.session_state.auth_view = "user_login"
                        st.rerun()
                else:
                    st.error(f"❌ {msg}")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("← Return to Sign In", key="forgot_pw_back_to_login", use_container_width=True):
                st.session_state.auth_view = "user_login"
                st.rerun()

        st.stop()


# ==============================================================================
# ROLE-BASED DASHBOARD DISPATCH
# ==============================================================================
active_role = st.session_state.get("role", "user")

# If Admin: execute dedicated Admin Dashboard and stop
if active_role == "admin":
    render_admin_dashboard()
    st.stop()

# Otherwise: Normal User Dashboard continues below


# Navigation options
NAV_OPTIONS = [
    "Dashboard",
    "Resume Screening",
    "Job Matching",
    "Candidate Management",
    "Candidate Comparison",
    "Resume Builder",
    "Analytics",
    "Saved Sessions",
    "Settings"
]

# Ensure current nav index exists with backward compatibility for legacy names
current_nav = st.session_state.get("current_nav", "Dashboard")
if current_nav == "Overview":
    current_nav = "Dashboard"
    st.session_state.current_nav = "Dashboard"
elif current_nav == "Candidates":
    current_nav = "Candidate Management"
    st.session_state.current_nav = "Candidate Management"

default_nav_idx = NAV_OPTIONS.index(current_nav) if current_nav in NAV_OPTIONS else 0


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(get_logo_svg(width=42, height=42, show_text=True), unsafe_allow_html=True)
    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Active Recruiter Profile Card
    curr_user = get_current_user()
    st.markdown(render_user_profile_pill(curr_user.get("name", "Recruiter"), curr_user.get("role", "Lead Recruiter"), curr_user.get("email", "")), unsafe_allow_html=True)

    col_so1, col_so2 = st.columns([1.5, 1.2])
    with col_so1:
        if st.button("🔒 Sign Out", key="sidebar_sign_out_btn", use_container_width=True):
            sign_out_user()
            st.rerun()
    with col_so2:
        st.markdown(f"<div style='font-size: 0.72rem; color: #34D399; padding-top: 8px;'>● Online</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Navigation Radio
    selected_nav = st.radio(
        "Navigation",
        NAV_OPTIONS,
        index=default_nav_idx,
        key="sidebar_nav_radio",
        label_visibility="collapsed"
    )

    if selected_nav != st.session_state.current_nav:
        st.session_state.current_nav = selected_nav
        st.session_state.selected_candidate_id = None
        st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Real-time System Status Card in Sidebar
    kpis = get_kpis()
    shortlisted_count = kpis.get("shortlisted_count", 0)
    st.markdown(
        clean_html(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 16px;">
            <div style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #818CF8; margin-bottom: 8px;">
                System Health &amp; Roster
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 5px;">
                <span style="color: #94A3B8;">Candidate Pool</span>
                <span style="font-weight: 700; color: #FFFFFF;">{kpis['total_candidates']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 5px;">
                <span style="color: #94A3B8;">Shortlisted</span>
                <span style="font-weight: 700; color: #FBBF24;">★ {shortlisted_count}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 5px;">
                <span style="color: #94A3B8;">Active Roles</span>
                <span style="font-weight: 700; color: #FFFFFF;">{kpis['active_jobs_count']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.82rem;">
                <span style="color: #94A3B8;">AI Model</span>
                <span style="font-weight: 700; color: #34D399;">TF-IDF + Cosine</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Quick Jump to Comparison Tray
    comp_cands = st.session_state.get("comparison_candidates", [])
    if comp_cands:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown(
            clean_html(f"""
            <div style="background: rgba(79, 70, 229, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 8px; padding: 8px 12px; font-size: 0.8rem; color: #C7D2FE;">
                ⚖️ <strong>{len(comp_cands)}</strong> candidates in comparison tray
            </div>
            """),
            unsafe_allow_html=True
        )
        if st.button("Open Comparison Matrix", key="sidebar_jump_comparison", use_container_width=True):
            st.session_state.current_nav = "Candidate Comparison"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        clean_html("""
        <div style="font-size: 0.72rem; color: #64748B; text-align: center;">
            TalentIQ AI v2.5 &middot; Commercial Edition<br/>
            Engineered with Precision
        </div>
        """),
        unsafe_allow_html=True
    )


# ==============================================================================
# VIEW 1: DASHBOARD
# ==============================================================================
if st.session_state.current_nav == "Dashboard":
    # Hero Section
    st.markdown(
        render_hero(
            title="Find the Right Talent, Faster.",
            subtitle="Autonomous resume parsing, multi-category skill taxonomy extraction, and semantic candidate-job matching powered by high-dimensional NLP vectors.",
            badge_text="TalentIQ AI v2.5 &middot; Commercial Edition"
        ),
        unsafe_allow_html=True
    )

    # Hero Action Buttons
    col_cta1, col_cta2, col_cta3, col_spacer = st.columns([1.6, 1.8, 1.6, 2.0])
    with col_cta1:
        if st.button("🚀 Start Screening", key="hero_start_screening", use_container_width=True):
            st.session_state.current_nav = "Resume Screening"
            st.rerun()
    with col_cta2:
        if st.button("🎯 Explore Job Matching", key="hero_job_matching", use_container_width=True):
            st.session_state.current_nav = "Job Matching"
            st.rerun()
    with col_cta3:
        if st.button("📊 View Analytics", key="hero_analytics", use_container_width=True):
            st.session_state.current_nav = "Analytics"
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Real KPI Dashboard Cards
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(
            render_kpi_card(
                title="Total Candidates",
                value=str(kpis["total_candidates"]),
                subtitle=f"{kpis['total_candidates']} parsed profiles" if kpis['total_candidates'] > 0 else "No profiles loaded",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with kpi_col2:
        st.markdown(
            render_kpi_card(
                title="Shortlisted",
                value=str(kpis.get("shortlisted_count", 0)),
                subtitle="Bookmarked talent" if kpis.get("shortlisted_count", 0) > 0 else "0 shortlisted yet",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with kpi_col3:
        avg_display = f"{kpis['avg_match_score']}%" if (kpis['screenings_count'] > 0 or st.session_state.get('last_results')) else "N/A"
        st.markdown(
            render_kpi_card(
                title="Avg Match Score",
                value=avg_display,
                subtitle="Across completed screenings" if avg_display != "N/A" else "Pending match execution",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with kpi_col4:
        st.markdown(
            render_kpi_card(
                title="Jobs Analyzed",
                value=str(kpis.get("total_jobs_analyzed", 0)),
                subtitle=f"{kpis['active_jobs_count']} configured roles",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Main Grid: Recent Candidates & Quick Match
    grid_left, grid_right = st.columns([1.1, 1.0])

    with grid_left:
        st.markdown(
            clean_html("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin: 0;">Candidate Pool</h3>
                <span style="font-size: 0.8rem; color: #94A3B8;">Real-time memory</span>
            </div>
            """),
            unsafe_allow_html=True
        )

        candidates = st.session_state.candidates
        if not candidates:
            st.markdown(
                render_empty_state(
                    title="No Candidates in Pool",
                    description="Upload resumes in PDF or DOCX format to populate candidate talent profiles and extract skill ontologies.",
                    action_text="Click 'Start Screening' above to upload"
                ),
                unsafe_allow_html=True
            )
        else:
            for cand in candidates[:4]:
                skills_preview = "".join([render_skill_badge(s, get_skill_category(s)) for s in cand["all_skills"][:5]])
                shortlist_badge = render_shortlist_badge(cand.get("shortlisted", False))
                st.markdown(
                    clean_html(f"""
                    <div class="tiq-candidate-item">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; width: 100%;">
                            <div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="font-size: 0.98rem; font-weight: 700; color: #FFFFFF;">
                                        {cand['candidate_name']}
                                    </span>
                                    {shortlist_badge}
                                </div>
                                <div style="font-size: 0.78rem; color: #94A3B8; margin: 3px 0 6px 0;">
                                    {cand['filename']} &middot; {cand['word_count']} words &middot; {cand['years_of_experience']} yrs exp
                                </div>
                                <div>{skills_preview}</div>
                            </div>
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )
            if len(candidates) > 4:
                st.info(f"+ {len(candidates) - 4} more candidate(s) loaded. View all in Candidate Management.")

    with grid_right:
        st.markdown(
            clean_html("""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <h3 style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin: 0;">Active Role & Fast Match</h3>
                <span style="font-size: 0.8rem; color: #94A3B8;">Instant Evaluation</span>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Job quick selector
        job_options = {j["title"]: j["id"] for j in st.session_state.job_descriptions}
        current_job = get_current_job()
        selected_job_title = st.selectbox(
            "Select Target Role",
            list(job_options.keys()),
            index=list(job_options.keys()).index(current_job["title"]) if current_job["title"] in job_options else 0,
            key="overview_job_select"
        )
        st.session_state.selected_job_id = job_options[selected_job_title]
        chosen_job = get_current_job()

        # Display job details card
        req_skills_html = "".join([render_skill_badge(s, "cloud") for s in chosen_job["required_skills"]])
        st.markdown(
            clean_html(f"""
            <div class="tiq-card" style="margin-top: 10px; margin-bottom: 14px;">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #06B6D4; text-transform: uppercase; letter-spacing: 0.05em;">
                    {chosen_job['department']} &middot; Min {chosen_job['min_experience']} Years Experience
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #FFFFFF; margin: 4px 0 8px 0;">
                    {chosen_job['title']}
                </div>
                <div style="margin-bottom: 10px;">{req_skills_html}</div>
                <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.4;">
                    {chosen_job['description'].strip()[:200]}...
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        if st.button("⚡ Evaluate Candidates for this Role", use_container_width=True, key="overview_eval_btn"):
            if not st.session_state.candidates:
                st.warning("Please upload candidate resumes first under 'Resume Screening' before running matching.")
            else:
                st.session_state.current_nav = "Job Matching"
                st.rerun()


# ==============================================================================
# VIEW 2: ADVANCED RESUME SCREENING
# ==============================================================================
elif st.session_state.current_nav == "Resume Screening":
    st.markdown(
        render_header(
            title="Resume Screening & Skill Extraction",
            subtitle="Upload resumes in PDF, DOCX, or TXT format for section segmentation, contact detection, and 300+ skill ontology extraction.",
            badge="Parser Engine v2.5"
        ),
        unsafe_allow_html=True
    )

    upload_col1, upload_col2 = st.columns([1.7, 1.3])

    with upload_col1:
        # Multi-file uploader
        st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;'>Resume File Ingestion</h4>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Select Resume Files (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="resume_file_uploader",
            help="Upload PDF, Word (DOCX), or Text resumes. Files are validated and parsed into structured candidate profiles."
        )

        if uploaded_files:
            st.markdown(f"<div style='font-size: 0.82rem; font-weight: 600; color: #94A3B8; margin: 8px 0;'>Staged Files ({len(uploaded_files)}):</div>", unsafe_allow_html=True)
            for f in uploaded_files:
                st.markdown(render_staged_file_badge(f.name, f.size, "Ready to parse"), unsafe_allow_html=True)

            # Prominent Action Button
            col_b1, col_b2 = st.columns([2, 1])
            with col_b1:
                start_btn = st.button("⚡ Start Screening & Parse Uploads", key="start_screening_action_btn", use_container_width=True)
            with col_b2:
                if st.button("Cancel", key="clear_upload_staging", use_container_width=True):
                    st.rerun()

            if start_btn:
                progress_bar = st.progress(0, text="Initializing parsing engine...")
                success_count = 0
                error_messages = []

                for idx, uf in enumerate(uploaded_files):
                    f_bytes = uf.read()
                    progress_pct = int(((idx + 0.5) / len(uploaded_files)) * 100)
                    progress_bar.progress(progress_pct, text=f"Processing {uf.name} (Extracting sections and skills)...")
                    time.sleep(0.04)

                    record, msg, ok = add_candidate_from_file(f_bytes, uf.name)
                    if ok:
                        success_count += 1
                    else:
                        error_messages.append(f"{uf.name}: {msg}")

                progress_bar.progress(100, text="Processing completed!")
                time.sleep(0.1)
                progress_bar.empty()

                if success_count > 0:
                    st.success(f"Successfully processed and indexed {success_count} candidate resume(s)!")
                if error_messages:
                    for err in error_messages:
                        st.error(err)
                st.rerun()

        # Hackathon / Demo Helper
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        col_demo, col_clear = st.columns([2.2, 1.2])
        with col_demo:
            if st.button("🧪 Quick-Load Sample Demo Resumes", key="load_demo_resumes_btn", use_container_width=True, help="Loads 3 realistic candidate resumes (Alex Chen - FullStack, Sophia Rodriguez - AI/ML, Marcus Vance - DevOps) for instant evaluation."):
                demo_dir = os.path.join(os.path.dirname(__file__), "sample_resumes")
                if os.path.exists(demo_dir):
                    loaded_c = 0
                    with st.spinner("Loading sample resumes into talent pool..."):
                        for fname in os.listdir(demo_dir):
                            fpath = os.path.join(demo_dir, fname)
                            if os.path.isfile(fpath):
                                with open(fpath, "rb") as f:
                                    rec, msg, ok = add_candidate_from_file(f.read(), fname)
                                    if ok:
                                        loaded_c += 1
                    if loaded_c > 0:
                        st.success(f"Loaded {loaded_c} sample candidates into pool!")
                        st.rerun()
        with col_clear:
            if st.session_state.candidates:
                if st.button("Clear Pool", key="clear_pool_screening_btn", use_container_width=True):
                    clear_all_candidates()
                    st.rerun()

    with upload_col2:
        st.markdown(
            clean_html(f"""
            <div class="tiq-card">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.82rem; font-weight: 700; color: #818CF8; text-transform: uppercase;">
                    Screening &amp; Parser Engine
                </div>
                <ul style="font-size: 0.84rem; color: #CBD5E1; padding-left: 18px; margin-top: 8px; line-height: 1.6;">
                    <li><strong>Multi-Format Support:</strong> Native high-fidelity PDF, DOCX, and TXT parsing.</li>
                    <li><strong>300+ Skill Taxonomy:</strong> Exact &amp; boundary-safe regex pattern detection.</li>
                    <li><strong>Entity Extraction:</strong> Email, phone numbers, LinkedIn, and GitHub links.</li>
                    <li><strong>Education Parsing:</strong> Identifies degrees (B.S., M.S., Ph.D.) &amp; institutions.</li>
                    <li><strong>Experience Analysis:</strong> Automatically estimates professional tenure.</li>
                    <li><strong>Deduplication:</strong> Prevents duplicate processing via SHA-256 file hashing.</li>
                </ul>
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Candidate Profile Cards
    candidates = st.session_state.candidates
    if not candidates:
        st.markdown(
            render_empty_state(
                title="No Resumes Uploaded Yet",
                description="Upload PDF, DOCX, or TXT files above or click 'Quick-Load Sample Demo Resumes' to view parsed profile cards."
            ),
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            clean_html(f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                <h3 style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin: 0;">
                    Indexed Candidates ({len(candidates)})
                </h3>
                <span style="font-size: 0.82rem; color: #94A3B8;">All profiles in memory</span>
            </div>
            """),
            unsafe_allow_html=True
        )

        for idx, cand in enumerate(candidates):
            contact = cand["contact"]
            initials = "".join([part[0] for part in cand["candidate_name"].split() if part])[:2].upper() or "CA"
            is_sl = cand.get("shortlisted", False)

            # Build contact pills
            contact_pills = []
            if contact.get("email"):
                contact_pills.append(f"📧 <a href='mailto:{contact['email']}' style='color: #93C5FD; text-decoration: none;'>{contact['email']}</a>")
            if contact.get("phone"):
                contact_pills.append(f"📞 {contact['phone']}")
            if contact.get("linkedin"):
                contact_pills.append(f"🔗 <a href='{contact['linkedin']}' target='_blank' style='color: #67E8F9; text-decoration: none;'>LinkedIn</a>")
            if contact.get("github"):
                contact_pills.append(f"💻 <a href='{contact['github']}' target='_blank' style='color: #A78BFA; text-decoration: none;'>GitHub</a>")

            contact_html = " &middot; ".join(contact_pills) if contact_pills else "<span style='color: #64748B;'>Contact info not detected</span>"

            # Education line
            edu_list = cand.get("education", [])
            edu_str = ", ".join(edu_list) if edu_list else "Extracted in raw sections"

            # Skill badges
            skill_badges_html = "".join([render_skill_badge(s, get_skill_category(s)) for s in cand["all_skills"][:14]])
            if len(cand["all_skills"]) > 14:
                skill_badges_html += f"<span style='font-size: 0.74rem; color: #94A3B8; margin-left: 6px;'>+{len(cand['all_skills']) - 14} more</span>"

            st.markdown(
                clean_html(f"""
                <div class="tiq-card" style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div style="background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; color: #FFFFFF; box-shadow: 0 4px 10px rgba(79, 70, 229, 0.4);">
                                {initials}
                            </div>
                            <div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <span style="font-size: 1.2rem; font-weight: 800; color: #FFFFFF;">{cand['candidate_name']}</span>
                                    {render_shortlist_badge(is_sl)}
                                </div>
                                <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 2px;">
                                    {cand['filename']} &middot; {cand.get('file_size', 0)/1024:.1f} KB &middot; {cand['word_count']} words &middot; <strong>{cand['years_of_experience']} Years Experience</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div style="margin: 10px 0 6px 0; font-size: 0.82rem; color: #CBD5E1;">
                        {contact_html}
                    </div>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 8px;">
                        <strong>Education:</strong> {edu_str}
                    </div>
                    <div>
                        {skill_badges_html}
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Candidate card action buttons
            col_act1, col_act2, col_act3, col_act_spacer = st.columns([1.5, 1.8, 1.5, 3.2])
            with col_act1:
                sl_label = "★ Unshortlist" if is_sl else "☆ Shortlist"
                if st.button(sl_label, key=f"sl_cand_btn_{cand['id']}", use_container_width=True):
                    toggle_candidate_shortlist(cand["id"])
                    st.rerun()
            with col_act2:
                with st.expander("📄 View Extracted Text", expanded=False):
                    st.text_area("Full Document Text", cand["raw_text"], height=220, key=f"raw_text_view_{cand['id']}")
            with col_act3:
                if st.button(f"🗑 Remove", key=f"del_cand_btn_{cand['id']}", use_container_width=True):
                    remove_candidate_by_id(cand["id"])
                    st.success(f"Removed {cand['candidate_name']} from pool.")
                    st.rerun()


# ==============================================================================
# VIEW 3: JOB MATCHING & EVALUATION
# ==============================================================================
elif st.session_state.current_nav == "Job Matching":
    st.markdown(
        render_header(
            title="AI Semantic Job Matching & Candidate Ranking",
            subtitle="Evaluate talent pool alignment using high-dimensional TF-IDF vectors, skill overlap ratios, and experience heuristics.",
            badge="Semantic Matcher v2.5"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates

    if not candidates:
        st.markdown(
            render_empty_state(
                title="Candidate Talent Pool is Empty",
                description="Upload resumes in 'Resume Screening' before ranking candidates against job postings.",
                action_text="Go to Resume Screening"
            ),
            unsafe_allow_html=True
        )
        if st.button("Go to Resume Screening", key="empty_go_screening_btn"):
            st.session_state.current_nav = "Resume Screening"
            st.rerun()

    # Detailed Candidate Inspection Panel
    elif st.session_state.get("selected_candidate_id"):
        cand_id = st.session_state.selected_candidate_id
        cand_record = get_candidate_by_id(cand_id)
        match_record = None
        for r in st.session_state.get("last_results", []):
            if r.get("candidate_id") == cand_id:
                match_record = r
                break

        if st.button("← Back to Match Results Leaderboard", key="back_to_results_btn"):
            st.session_state.selected_candidate_id = None
            st.rerun()

        if cand_record:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            comp_score = match_record["composite_score"] if match_record else 0.0
            rank_label = f"#{match_record['rank']} Ranked Candidate" if match_record and "rank" in match_record else "Candidate Profile"

            st.markdown(
                clean_html(f"""
                <div class="tiq-card" style="margin-bottom: 1.25rem;">
                    <div class="tiq-card-accent-top"></div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                        <div>
                            <div style="font-size: 0.8rem; font-weight: 700; color: #818CF8; text-transform: uppercase; letter-spacing: 0.06em;">
                                {rank_label} &middot; Detailed Assessment
                            </div>
                            <h2 style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin: 4px 0;">
                                {cand_record['candidate_name']}
                            </h2>
                            <div style="font-size: 0.84rem; color: #94A3B8;">
                                Source: {cand_record['filename']} &middot; {cand_record.get('years_of_experience', 0)} Years Experience &middot; {cand_record.get('word_count', 0)} words
                            </div>
                        </div>
                        <div>
                            {render_score_badge(comp_score) if match_record else ""}
                        </div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Three Pillars & Evidence Breakdown
            if match_record:
                col_m1, col_m2 = st.columns([1.2, 1.8])
                with col_m1:
                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card">
                            <div style="font-size: 0.86rem; font-weight: 700; color: #FFFFFF; margin-bottom: 8px;">
                                Alignment Score Breakdown
                            </div>
                            {render_progress_bar(match_record['skill_score'], "Skill Overlap (50%)", "#2563EB")}
                            {render_progress_bar(match_record['semantic_score'], "Semantic Text Alignment (35%)", "#7C3AED")}
                            {render_progress_bar(match_record['exp_score'], "Experience Match (15%)", "#06B6D4")}
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                with col_m2:
                    st.markdown(
                        render_evidence_card(
                            match_record.get("evidence_text", "No detailed evidence generated."),
                            match_record.get("recommendation", ""),
                            comp_score
                        ),
                        unsafe_allow_html=True
                    )

                # Required Skills vs Missing Skills Comparison Matrix
                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
                col_sk1, col_sk2 = st.columns(2)
                with col_sk1:
                    matched_sks = match_record.get("matched_skills", [])
                    matched_html = "".join([render_skill_badge(s, "tech") for s in matched_sks]) if matched_sks else "<span style='color: #64748B;'>No required skills matched.</span>"
                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card">
                            <div style="font-size: 0.86rem; font-weight: 700; color: #34D399; margin-bottom: 8px;">
                                ✓ Matched Required Skills ({len(matched_sks)})
                            </div>
                            <div>{matched_html}</div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )
                with col_sk2:
                    missing_sks = match_record.get("missing_skills", [])
                    missing_html = "".join([render_skill_badge(s, "missing") for s in missing_sks]) if missing_sks else "<span style='color: #34D399; font-weight: 600;'>None! Candidate has all required skills.</span>"
                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card">
                            <div style="font-size: 0.86rem; font-weight: 700; color: #F87171; margin-bottom: 8px;">
                                ⚠ Missing Required Skills ({len(missing_sks)})
                            </div>
                            <div>{missing_html}</div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

            # Education & Sections Details
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            col_sec1, col_sec2 = st.columns(2)
            with col_sec1:
                st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>Extracted Qualifications</h4>", unsafe_allow_html=True)
                edu_items = cand_record.get("education", [])
                if edu_items:
                    for e in edu_items:
                        st.markdown(f"🎓 **{e}**")
                else:
                    st.write("No explicit degrees identified in document.")
                st.write(f"⏱ **Years of Experience:** {cand_record.get('years_of_experience', 0)} Years")
                contact = cand_record.get("contact", {})
                st.write(f"📧 **Email:** {contact.get('email') or 'Not specified'}")
                st.write(f"📞 **Phone:** {contact.get('phone') or 'Not specified'}")

                # Download individual report button
                curr_j = get_current_job()
                cand_report_text = generate_candidate_analysis_report(cand_record, match_record, curr_j)
                st.download_button(
                    label=f"📥 Download {cand_record['candidate_name']} Analysis Report",
                    data=cand_report_text,
                    file_name=f"{cand_record['candidate_name'].replace(' ', '_')}_Analysis_Report.txt",
                    mime="text/plain",
                    key="deep_dive_dl_report_btn"
                )

            with col_sec2:
                st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>All Candidate Skills Detected</h4>", unsafe_allow_html=True)
                all_sks_html = "".join([render_skill_badge(s, get_skill_category(s)) for s in cand_record.get("all_skills", [])])
                st.markdown(f"<div>{all_sks_html}</div>", unsafe_allow_html=True)

            with st.expander("📄 Full Resume Raw Text"):
                st.text_area("Resume Text", cand_record.get("raw_text", ""), height=250, key="deep_dive_raw_text")

    # Job Matching Interface & Results Leaderboard
    else:
        match_col1, match_col2 = st.columns([1.6, 1.4])

        with match_col1:
            st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #FFFFFF;'>1. Select or Configure Target Job Role</h4>", unsafe_allow_html=True)
            job_titles = [j["title"] for j in st.session_state.job_descriptions]
            current_job = get_current_job()
            current_idx = job_titles.index(current_job["title"]) if current_job["title"] in job_titles else 0

            chosen_title = st.selectbox(
                "Select Role Template",
                job_titles,
                index=current_idx,
                key="jm_role_select",
                help="Select an existing industry benchmark template or customize the text below."
            )
            for j in st.session_state.job_descriptions:
                if j["title"] == chosen_title:
                    st.session_state.selected_job_id = j["id"]
                    break

            active_job = get_current_job()

            # Job description text area with pre-population & editing
            custom_jd_text = st.text_area(
                "Job Description Requirements",
                value=active_job["description"].strip(),
                height=150,
                key=f"jd_editor_{active_job['id']}",
                help="You can edit or paste any custom job description here to immediately match against."
            )
            update_job_description(active_job["id"], custom_jd_text)

        with match_col2:
            st.markdown("<h4 style='font-size: 1.05rem; font-weight: 700; color: #FFFFFF;'>2. Role Specifications & Weights</h4>", unsafe_allow_html=True)
            req_badges = "".join([render_skill_badge(s, "cloud") for s in active_job["required_skills"]])
            st.markdown(
                clean_html(f"""
                <div class="tiq-card">
                    <div class="tiq-card-accent-top"></div>
                    <div style="font-size: 0.8rem; font-weight: 700; color: #06B6D4; text-transform: uppercase;">
                        {active_job['department']} &middot; Min {active_job['min_experience']} Yrs Experience
                    </div>
                    <div style="margin: 8px 0 6px 0;"><strong>Required Skills ({len(active_job['required_skills'])}):</strong><br/>{req_badges}</div>
                    <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 8px;">
                        Weighting: Skills ({int(st.session_state.weights['skills']*100)}%) &middot; Semantic ({int(st.session_state.weights['semantic']*100)}%) &middot; Experience ({int(st.session_state.weights['experience']*100)}%)
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Match Action Button
        if st.button("⚡ Match Candidates Against Role", key="run_match_btn", use_container_width=True):
            with st.spinner("Computing high-dimensional TF-IDF vectors, skill overlap, and ranking candidate pool..."):
                time.sleep(0.08)
                ranked_results = rank_candidates_for_job(candidates, active_job, st.session_state.weights)
                record_screening_event(ranked_results, active_job["title"])
                st.session_state.last_results = ranked_results
            st.success(f"Evaluated {len(ranked_results)} candidate(s) against '{active_job['title']}'!")

        # Results Leaderboard & Table
        results_to_display = st.session_state.get("last_results")

        if results_to_display:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown(
                clean_html(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                    <h3 style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; margin: 0;">
                        Candidate Match Leaderboard &amp; Comparison
                    </h3>
                    <span style="font-size: 0.84rem; color: #818CF8; font-weight: 600;">
                        {len(results_to_display)} Candidates Ranked
                    </span>
                </div>
                """),
                unsafe_allow_html=True
            )

            # Interactive Filter Bar
            with st.expander("🔍 Filter Results & Leaderboard", expanded=True):
                f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 1.5, 1.5])
                with f_col1:
                    name_filter = st.text_input("Filter Candidate Name", "", placeholder="Search name...")
                with f_col2:
                    min_score_filter = st.slider("Minimum Match Score", 0, 100, 0, 5)
                with f_col3:
                    status_filter = st.multiselect(
                        "Status Category",
                        ["High", "Good", "Review", "Low"],
                        default=["High", "Good", "Review", "Low"]
                    )
                with f_col4:
                    view_mode = st.radio("Display View", ["Card Leaderboard", "Comparison Table"], horizontal=True)

            # Apply filters
            filtered_results = []
            for r in results_to_display:
                if name_filter.strip() and name_filter.strip().lower() not in r["candidate_name"].lower():
                    continue
                if r["composite_score"] < min_score_filter:
                    continue
                if status_filter and r.get("status_category") not in status_filter:
                    continue
                filtered_results.append(r)

            st.markdown(f"<div style='font-size: 0.82rem; color: #94A3B8; margin-bottom: 12px;'>Showing {len(filtered_results)} of {len(results_to_display)} candidate(s)</div>", unsafe_allow_html=True)

            # Report Downloads Bar
            col_rep1, col_rep2, col_rep3 = st.columns([1.5, 1.5, 1.5])
            with col_rep1:
                ranking_csv = generate_candidate_ranking_csv(results_to_display, active_job["title"])
                st.download_button(
                    label="📥 Download Ranking CSV",
                    data=ranking_csv,
                    file_name=f"{active_job['title'].replace(' ', '_')}_Rankings.csv",
                    mime="text/csv",
                    key="jm_dl_rankings_btn",
                    use_container_width=True
                )
            with col_rep2:
                summary_csv = generate_job_screening_summary_csv(active_job, results_to_display, candidates)
                st.download_button(
                    label="📥 Download Job Summary CSV",
                    data=summary_csv,
                    file_name=f"{active_job['title'].replace(' ', '_')}_Summary.csv",
                    mime="text/csv",
                    key="jm_dl_summary_btn",
                    use_container_width=True
                )
            with col_rep3:
                shortlisted_csv = generate_shortlisted_candidates_csv(candidates, results_to_display)
                st.download_button(
                    label="📥 Download Shortlisted CSV",
                    data=shortlisted_csv,
                    file_name="Shortlisted_Candidates.csv",
                    mime="text/csv",
                    key="jm_dl_shortlisted_btn",
                    use_container_width=True
                )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # View Mode: Comparison Table
            if view_mode == "Comparison Table":
                table_rows = []
                for item in filtered_results:
                    cand_rec = get_candidate_by_id(item["candidate_id"])
                    is_sl = cand_rec.get("shortlisted", False) if cand_rec else False
                    table_rows.append({
                        "Rank": f"#{item['rank']}",
                        "Candidate Name": item["candidate_name"],
                        "Shortlisted": "★ YES" if is_sl else "No",
                        "Match Score": f"{item['composite_score']}%",
                        "Status": item["badge_level"],
                        "Skill Score": f"{item['skill_score']}%",
                        "Semantic Score": f"{item['semantic_score']}%",
                        "Experience": f"{item['candidate_experience']} yrs",
                        "Matched Skills": ", ".join(item["matched_skills"][:4]),
                        "Missing Skills": ", ".join(item["missing_skills"][:3]) if item["missing_skills"] else "None",
                        "Filename": item["filename"]
                    })
                df_results = pd.DataFrame(table_rows)
                st.dataframe(df_results, use_container_width=True)

            # View Mode: Card Leaderboard
            else:
                for item in filtered_results:
                    rank_badge_color = "#34D399" if item["rank"] == 1 else ("#38BDF8" if item["rank"] == 2 else "#818CF8")
                    matched_badges = "".join([render_skill_badge(s, "tech") for s in item["matched_skills"]]) if item["matched_skills"] else "<span style='color: #64748B; font-size: 0.78rem;'>None</span>"
                    missing_badges = "".join([render_skill_badge(s, "missing") for s in item["missing_skills"]]) if item["missing_skills"] else "<span style='color: #34D399; font-size: 0.78rem;'>No missing skills!</span>"

                    cand_rec = get_candidate_by_id(item["candidate_id"])
                    is_sl = cand_rec.get("shortlisted", False) if cand_rec else False

                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card" style="margin-bottom: 1.1rem;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="background: rgba(79, 70, 229, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.15rem; color: {rank_badge_color};">
                                        #{item['rank']}
                                    </div>
                                    <div>
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <span style="font-size: 1.2rem; font-weight: 800; color: #FFFFFF;">{item['candidate_name']}</span>
                                            {render_shortlist_badge(is_sl)}
                                        </div>
                                        <div style="font-size: 0.78rem; color: #94A3B8;">Source: {item['filename']} &middot; {item['candidate_experience']} yrs exp (Required: {item['required_experience']} yrs)</div>
                                    </div>
                                </div>
                                <div>
                                    {render_score_badge(item['composite_score'])}
                                </div>
                            </div>
                            <div style="margin-top: 14px; display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px;">
                                <div>
                                    {render_progress_bar(item['skill_score'], "Skill Overlap Score", "#2563EB")}
                                    {render_progress_bar(item['semantic_score'], "Semantic Text Alignment", "#7C3AED")}
                                    {render_progress_bar(item['exp_score'], "Experience Match", "#06B6D4")}
                                </div>
                                <div style="font-size: 0.82rem; line-height: 1.6;">
                                    <div style="margin-top: 2px;"><strong>Matched Skills ({len(item['matched_skills'])}):</strong><br/>{matched_badges}</div>
                                    <div style="margin-top: 6px;"><strong>Missing Skills ({len(item['missing_skills'])}):</strong><br/>{missing_badges}</div>
                                </div>
                            </div>
                            {render_evidence_card(item.get('evidence_text', ''), item.get('recommendation', ''), item['composite_score'])}
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    col_inspect, col_sl, col_comp, col_space = st.columns([1.6, 1.2, 1.4, 2.8])
                    with col_inspect:
                        if st.button(f"🔍 Inspect Deep-Dive", key=f"inspect_cand_{item['candidate_id']}", use_container_width=True):
                            st.session_state.selected_candidate_id = item["candidate_id"]
                            st.rerun()
                    with col_sl:
                        sl_text = "★ Unshortlist" if is_sl else "☆ Shortlist"
                        if st.button(sl_text, key=f"sl_toggle_res_{item['candidate_id']}", use_container_width=True):
                            toggle_candidate_shortlist(item["candidate_id"])
                            st.rerun()
                    with col_comp:
                        in_comp = item["candidate_id"] in st.session_state.get("comparison_candidates", [])
                        btn_comp_label = "Remove Compare" if in_comp else "+ Compare"
                        if st.button(btn_comp_label, key=f"comp_toggle_res_{item['candidate_id']}", use_container_width=True):
                            if in_comp:
                                st.session_state.comparison_candidates.remove(item["candidate_id"])
                            else:
                                if len(st.session_state.comparison_candidates) >= 3:
                                    st.warning("Comparison tray holds max 3 candidates.")
                                else:
                                    st.session_state.comparison_candidates.append(item["candidate_id"])
                            st.rerun()


# ==============================================================================
# VIEW 4: CANDIDATE MANAGEMENT (SMART SEARCH & FILTERS)
# ==============================================================================
elif st.session_state.current_nav == "Candidate Management":
    st.markdown(
        render_header(
            title="Candidate Talent Management & Smart Search",
            subtitle="Search, filter, categorize, shortlist, and organize candidates across multidimensional criteria.",
            badge="Candidate Hub"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates
    if not candidates:
        st.markdown(
            render_empty_state(
                title="Talent Database is Empty",
                description="Upload resumes in 'Resume Screening' to begin managing and filtering candidate profiles."
            ),
            unsafe_allow_html=True
        )
    else:
        # Collect all unique detected skills in candidate pool for skill filter
        all_skills_set = set()
        for c in candidates:
            all_skills_set.update(c.get("all_skills", []))
        all_skills_list = sorted(list(all_skills_set))

        # Filter Controls Bar
        with st.expander("🔍 Smart Search & Multi-Criteria Filters", expanded=True):
            fc1, fc2 = st.columns([2.0, 1.5])
            with fc1:
                search_query = st.text_input("Candidate Name or Resume Filename", "", placeholder="e.g. Alex, Sophia, devops.docx...", key="cm_search_query")
            with fc2:
                # Target Role Selector
                job_dict = {j["title"]: j for j in st.session_state.job_descriptions}
                selected_job_title = st.selectbox("Evaluate Against Role", list(job_dict.keys()), key="cm_job_select")
                target_job = job_dict[selected_job_title]

            fc3, fc4, fc5, fc6 = st.columns([1.5, 1.5, 1.2, 1.2])
            with fc3:
                score_range = st.slider("Match Score Range (%)", 0, 100, (0, 100), key="cm_score_slider")
            with fc4:
                selected_skills = st.multiselect("Required Skills Filter", all_skills_list, key="cm_skills_multiselect")
            with fc5:
                skill_mode = st.radio("Skills Mode", ["Match ANY", "Match ALL"], horizontal=True, key="cm_skill_mode")
            with fc6:
                shortlist_filter = st.selectbox(
                    "Shortlist Status",
                    ["All Candidates", "Shortlisted Only", "Not Shortlisted"],
                    key="cm_shortlist_filter"
                )

            fc7, fc8 = st.columns([1.8, 1.2])
            with fc7:
                sort_option = st.selectbox(
                    "Sort Candidates By",
                    [
                        "Highest Match Score",
                        "Lowest Match Score",
                        "Name (A-Z)",
                        "Name (Z-A)",
                        "Experience (Highest First)",
                        "Upload Order (Newest First)"
                    ],
                    key="cm_sort_select"
                )
            with fc8:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("Reset All Filters", key="cm_reset_filters_btn", use_container_width=True):
                    st.session_state.cm_search_query = ""
                    st.session_state.cm_score_slider = (0, 100)
                    st.session_state.cm_skills_multiselect = []
                    st.rerun()

        # Translate filter states
        sl_mode = "ALL"
        if shortlist_filter == "Shortlisted Only":
            sl_mode = "SHORTLISTED_ONLY"
        elif shortlist_filter == "Not Shortlisted":
            sl_mode = "UNSHORTLISTED_ONLY"

        skill_m = "ALL" if skill_mode == "Match ALL" else "ANY"

        # Apply filtering & sorting
        filtered_cands = filter_and_sort_candidates(
            candidates=candidates,
            search_query=search_query,
            target_job=target_job,
            min_score=float(score_range[0]),
            max_score=float(score_range[1]),
            required_skills=selected_skills,
            skill_mode=skill_m,
            shortlist_filter=sl_mode,
            sort_by=sort_option,
            weights=st.session_state.weights
        )

        # Batch actions & summary header
        b_col1, b_col2, b_col3, b_col4 = st.columns([2.5, 1.5, 1.5, 1.8])
        with b_col1:
            st.markdown(
                f"<div style='font-size: 0.92rem; font-weight: 600; color: #FFFFFF; padding-top: 6px;'>"
                f"Showing <span style='color: #818CF8;'>{len(filtered_cands)}</span> of {len(candidates)} candidate(s) for <i>{selected_job_title}</i>"
                f"</div>",
                unsafe_allow_html=True
            )
        with b_col2:
            if filtered_cands and st.button("★ Shortlist All Filtered", key="cm_shortlist_all_btn", use_container_width=True):
                for fc in filtered_cands:
                    set_candidate_shortlist(fc["id"], True)
                st.success(f"Shortlisted {len(filtered_cands)} candidate(s)!")
                st.rerun()
        with b_col3:
            if st.session_state.get("comparison_candidates"):
                if st.button(f"⚖️ Compare ({len(st.session_state.comparison_candidates)})", key="cm_go_compare_btn", use_container_width=True):
                    st.session_state.current_nav = "Candidate Comparison"
                    st.rerun()
        with b_col4:
            if any(c.get("shortlisted") for c in candidates):
                if st.button("Clear All Shortlists", key="cm_clear_all_sl_btn", use_container_width=True):
                    for c in candidates:
                        set_candidate_shortlist(c["id"], False)
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if not filtered_cands:
            st.markdown(
                render_empty_state(
                    title="No Candidates Match Filter Criteria",
                    description="Try broadening your search term, adjusting the match score slider, or relaxing the skill filters to view candidate profiles.",
                    action_text="Use 'Reset All Filters' above to view the complete talent pool."
                ),
                unsafe_allow_html=True
            )
        else:
            for c in filtered_cands:
                initials = "".join([p[0] for p in c["candidate_name"].split() if p])[:2].upper() or "CA"
                is_sl = c.get("shortlisted", False)
                comp_score = c.get("match_score", 0.0)
                in_compare = c["id"] in st.session_state.get("comparison_candidates", [])

                contact = c.get("contact", {})
                contact_pills = []
                if contact.get("email"):
                    contact_pills.append(f"📧 <a href='mailto:{contact['email']}' style='color: #93C5FD; text-decoration: none;'>{contact['email']}</a>")
                if contact.get("phone"):
                    contact_pills.append(f"📞 {contact['phone']}")
                if contact.get("linkedin"):
                    contact_pills.append(f"🔗 <a href='{contact['linkedin']}' target='_blank' style='color: #67E8F9; text-decoration: none;'>LinkedIn</a>")
                if contact.get("github"):
                    contact_pills.append(f"💻 <a href='{contact['github']}' target='_blank' style='color: #A78BFA; text-decoration: none;'>GitHub</a>")
                contact_html = " &middot; ".join(contact_pills) if contact_pills else "<span style='color: #64748B;'>Contact info not specified</span>"

                edu_str = ", ".join(c.get("education", [])) if c.get("education") else "Extracted in text"

                # Skills preview with matched skills highlighted
                matched_set = set(c.get("matched_skills", []))
                skill_badges = []
                for s in c.get("all_skills", [])[:14]:
                    if s in matched_set:
                        skill_badges.append(f'<span class="tiq-badge tiq-badge-tech" style="border-color: #34D399; font-weight: 700;">✓ {s}</span>')
                    else:
                        skill_badges.append(render_skill_badge(s, get_skill_category(s)))
                skills_html = "".join(skill_badges)

                st.markdown(
                    clean_html(f"""
                    <div class="tiq-card" style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                            <div style="display: flex; align-items: center; gap: 14px;">
                                <div style="background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">
                                    {initials}
                                </div>
                                <div>
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;">{c['candidate_name']}</span>
                                        {render_shortlist_badge(is_sl)}
                                    </div>
                                    <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 2px;">
                                        {c['filename']} &middot; <strong>{c.get('years_of_experience', 0)} Yrs Exp</strong> &middot; Education: {edu_str}
                                    </div>
                                </div>
                            </div>
                            <div>
                                {render_score_badge(comp_score)}
                            </div>
                        </div>
                        <div style="font-size: 0.8rem; color: #CBD5E1; margin: 8px 0 6px 0;">{contact_html}</div>
                        <div style="margin-top: 6px;">{skills_html}</div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

                col_a1, col_a2, col_a3, col_a4, col_a_spacer = st.columns([1.4, 1.4, 1.8, 1.2, 2.2])
                with col_a1:
                    sl_label = "★ Unshortlist" if is_sl else "☆ Shortlist"
                    if st.button(sl_label, key=f"cm_sl_toggle_{c['id']}", use_container_width=True):
                        toggle_candidate_shortlist(c["id"])
                        st.rerun()
                with col_a2:
                    comp_label = "Remove Compare" if in_compare else "+ Compare"
                    if st.button(comp_label, key=f"cm_comp_toggle_{c['id']}", use_container_width=True):
                        if in_compare:
                            st.session_state.comparison_candidates.remove(c["id"])
                        else:
                            if len(st.session_state.comparison_candidates) >= 3:
                                st.warning("Comparison tray holds max 3 candidates.")
                            else:
                                st.session_state.comparison_candidates.append(c["id"])
                        st.rerun()
                with col_a3:
                    cand_dossier = generate_candidate_analysis_report(c, {"composite_score": comp_score, "matched_skills": c.get("matched_skills", []), "missing_skills": c.get("missing_skills", [])}, target_job)
                    st.download_button(
                        label="📥 Download Dossier",
                        data=cand_dossier,
                        file_name=f"{c['candidate_name'].replace(' ', '_')}_Dossier.txt",
                        mime="text/plain",
                        key=f"cm_dl_dossier_{c['id']}",
                        use_container_width=True
                    )
                with col_a4:
                    if st.button("🗑 Remove", key=f"cm_del_{c['id']}", use_container_width=True):
                        remove_candidate_by_id(c["id"])
                        st.rerun()

        # Candidate Management Export Options
        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>Export Talent Records</h4>", unsafe_allow_html=True)
        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            filtered_ranking_csv = generate_candidate_ranking_csv(filtered_cands, selected_job_title)
            st.download_button(
                label=f"📥 Export Filtered Candidates ({len(filtered_cands)}) (CSV)",
                data=filtered_ranking_csv,
                file_name=f"TalentIQ_Filtered_{selected_job_title.replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="cm_export_filtered_csv_btn"
            )
        with exp_col2:
            sl_cands = get_shortlisted_candidates()
            shortlisted_csv = generate_shortlisted_candidates_csv(sl_cands)
            st.download_button(
                label=f"📥 Export All Shortlisted Candidates ({len(sl_cands)}) (CSV)",
                data=shortlisted_csv,
                file_name="TalentIQ_Shortlisted_Candidates.csv",
                mime="text/csv",
                use_container_width=True,
                key="cm_export_shortlisted_csv_btn"
            )


# ==============================================================================
# VIEW 5: CANDIDATE COMPARISON
# ==============================================================================
elif st.session_state.current_nav == "Candidate Comparison":
    st.markdown(
        render_header(
            title="Candidate Comparative Analysis Matrix",
            subtitle="Side-by-side comparative evaluation of 2 to 3 candidate profiles against target role specifications, skill overlaps, and qualification evidence.",
            badge="Comparative Matrix"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates
    if len(candidates) < 2:
        st.markdown(
            render_empty_state(
                title="At least 2 candidates required for comparison",
                description="Upload 2 or more resumes in 'Resume Screening' to unlock side-by-side comparative evaluations.",
                action_text="Upload resumes to get started."
            ),
            unsafe_allow_html=True
        )
    else:
        # Comparison Configuration Controls
        col_c_job, col_c_pick = st.columns([1.5, 2.5])
        with col_c_job:
            job_dict = {j["title"]: j for j in st.session_state.job_descriptions}
            curr_j = get_current_job()
            c_job_title = st.selectbox(
                "Benchmark Target Role",
                list(job_dict.keys()),
                index=list(job_dict.keys()).index(curr_j["title"]) if curr_j["title"] in job_dict else 0,
                key="comp_job_selector"
            )
            benchmark_job = job_dict[c_job_title]

        with col_c_pick:
            cand_name_map = {f"{c['candidate_name']} ({c['filename']})": c["id"] for c in candidates}
            # Pre-select based on session state comparison tray or first 2
            current_tray_ids = st.session_state.get("comparison_candidates", [])
            default_labels = []
            for label, cid in cand_name_map.items():
                if cid in current_tray_ids:
                    default_labels.append(label)
            if not default_labels and len(cand_name_map) >= 2:
                default_labels = list(cand_name_map.keys())[:2]

            selected_labels = st.multiselect(
                "Select 2 or 3 Candidates to Compare",
                list(cand_name_map.keys()),
                default=default_labels[:3],
                max_selections=3,
                key="comp_multiselect"
            )
            st.session_state.comparison_candidates = [cand_name_map[lbl] for lbl in selected_labels]

        # Quick action buttons
        col_quick1, col_quick2, col_quick_space = st.columns([1.4, 1.4, 4.0])
        with col_quick1:
            if len(candidates) >= 2 and st.button("Compare Top 2 Candidates", key="comp_top2_btn"):
                # Run quick match to find top 2
                ranked = rank_candidates_for_job(candidates, benchmark_job, st.session_state.weights)
                st.session_state.comparison_candidates = [ranked[0]["candidate_id"], ranked[1]["candidate_id"]]
                st.rerun()
        with col_quick2:
            if len(candidates) >= 3 and st.button("Compare Top 3 Candidates", key="comp_top3_btn"):
                ranked = rank_candidates_for_job(candidates, benchmark_job, st.session_state.weights)
                st.session_state.comparison_candidates = [ranked[0]["candidate_id"], ranked[1]["candidate_id"], ranked[2]["candidate_id"]]
                st.rerun()

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        selected_cands = [c for c in candidates if c["id"] in st.session_state.get("comparison_candidates", [])]

        if len(selected_cands) < 2:
            st.info("💡 Please select 2 or 3 candidates using the selector above to display the side-by-side comparison matrix.")
        else:
            # Build matrix
            comp_matrix = build_comparison_matrix(selected_cands, benchmark_job, st.session_state.weights)

            # Side-by-side comparative column rendering
            comp_cols = st.columns(len(comp_matrix))
            for idx, c_data in enumerate(comp_matrix):
                with comp_cols[idx]:
                    initials = "".join([p[0] for p in c_data["candidate_name"].split() if p])[:2].upper() or "CA"
                    is_sl = c_data.get("shortlisted", False)

                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card" style="border-top: 4px solid #4F46E5; margin-bottom: 14px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1rem; color: #FFFFFF;">
                                        {initials}
                                    </div>
                                    <div>
                                        <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;">{c_data['candidate_name']}</div>
                                        <div style="font-size: 0.74rem; color: #94A3B8;">{c_data['filename']}</div>
                                    </div>
                                </div>
                                {render_shortlist_badge(is_sl)}
                            </div>
                            <div style="text-align: center; margin: 12px 0;">
                                {render_score_badge(c_data['composite_score'])}
                            </div>
                            <div style="margin-top: 10px;">
                                {render_progress_bar(c_data['skill_score'], "Skill Overlap (50%)", "#2563EB")}
                                {render_progress_bar(c_data['semantic_score'], "Semantic Context (35%)", "#7C3AED")}
                                {render_progress_bar(c_data['exp_score'], "Experience Alignment (15%)", "#06B6D4")}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    # Matched Skills & Missing Skills
                    matched_html = "".join([render_skill_badge(s, "tech") for s in c_data["matched_skills"]]) if c_data["matched_skills"] else "<span style='color: #64748B;'>None</span>"
                    missing_html = "".join([render_skill_badge(s, "missing") for s in c_data["missing_skills"]]) if c_data["missing_skills"] else "<span style='color: #34D399; font-weight: 600;'>Zero missing skills!</span>"

                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card" style="margin-bottom: 12px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #34D399; margin-bottom: 6px;">
                                ✓ Matched Required Skills ({len(c_data['matched_skills'])})
                            </div>
                            <div style="margin-bottom: 10px;">{matched_html}</div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #F87171; margin-bottom: 6px;">
                                ⚠ Missing Required Skills ({len(c_data['missing_skills'])})
                            </div>
                            <div>{missing_html}</div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    # Qualifications & Work Experience
                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card" style="margin-bottom: 12px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #818CF8; margin-bottom: 6px;">
                                🎓 Academic Education
                            </div>
                            <div style="font-size: 0.84rem; color: #F8FAFC; margin-bottom: 8px;">
                                {c_data['education_display']}
                            </div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #818CF8; margin-bottom: 6px;">
                                ⏱ Work Experience ({c_data['candidate_experience']} Yrs)
                            </div>
                            <div style="font-size: 0.8rem; color: #CBD5E1; line-height: 1.45;">
                                {c_data['work_experience_summary']}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    # Projects & Certifications
                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card" style="margin-bottom: 12px;">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #06B6D4; margin-bottom: 6px;">
                                🚀 Documented Projects
                            </div>
                            <div style="font-size: 0.8rem; color: #CBD5E1; margin-bottom: 8px; line-height: 1.45;">
                                {c_data['projects_summary']}
                            </div>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #06B6D4; margin-bottom: 6px;">
                                📜 Certifications &amp; Licenses
                            </div>
                            <div style="font-size: 0.8rem; color: #CBD5E1; line-height: 1.45;">
                                {c_data['certifications_summary']}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )

                    # Grounded Strengths & Improvement Areas
                    strengths_html = "".join([f"<li style='margin-bottom: 4px; color: #D1FAE5;'>✓ {s}</li>" for s in c_data["strengths"]])
                    improvements_html = "".join([f"<li style='margin-bottom: 4px; color: #FEE2E2;'>⚠ {imp}</li>" for imp in c_data["improvements"]])

                    st.markdown(
                        clean_html(f"""
                        <div class="tiq-card">
                            <div style="font-size: 0.82rem; font-weight: 700; color: #10B981; margin-bottom: 6px;">
                                🌟 Key Competitive Strengths
                            </div>
                            <ul style="font-size: 0.8rem; padding-left: 16px; margin: 0 0 10px 0;">{strengths_html}</ul>
                            <div style="font-size: 0.82rem; font-weight: 700; color: #F59E0B; margin-bottom: 6px;">
                                🛠 Candidate Improvement Areas
                            </div>
                            <ul style="font-size: 0.8rem; padding-left: 16px; margin: 0 0 10px 0;">{improvements_html}</ul>
                            <div style="font-size: 0.78rem; font-weight: 600; color: #818CF8; margin-top: 8px;">
                                Recommendation: {c_data['recommendation']}
                            </div>
                        </div>
                        """),
                        unsafe_allow_html=True
                    )


# ==============================================================================
# VIEW 6: RESUME BUILDER & PDF GENERATION
# ==============================================================================
elif st.session_state.current_nav == "Resume Builder":
    st.markdown(
        render_header(
            title="Enterprise Resume Builder & PDF Generation Engine",
            subtitle="Compose, format, and generate publication-quality PDF resumes with ReportLab typography, verified skill taxonomies, and custom layouts.",
            badge="Resume Builder v2.5"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates

    # Pre-population helper
    rb_col_pre, rb_col_actions = st.columns([2.5, 1.5])
    with rb_col_pre:
        if candidates:
            cand_names = {f"{c['candidate_name']} ({c['filename']})": c for c in candidates}
            selected_prefill = st.selectbox(
                "⚡ Prefill from Candidate Pool",
                ["-- Select Candidate to Import --"] + list(cand_names.keys()),
                key="rb_prefill_select"
            )
            if selected_prefill != "-- Select Candidate to Import --":
                source_cand = cand_names[selected_prefill]
                prefilled = prefill_resume_from_candidate(source_cand)
                st.session_state.rb_full_name = prefilled["full_name"]
                st.session_state.rb_job_title = prefilled["job_title"]
                st.session_state.rb_email = prefilled["email"]
                st.session_state.rb_phone = prefilled["phone"]
                st.session_state.rb_location = prefilled["location"]
                st.session_state.rb_linkedin = prefilled["linkedin"]
                st.session_state.rb_github = prefilled["github"]
                st.session_state.rb_summary = prefilled["summary"]
                st.session_state.rb_skills = prefilled["skills"]
                st.session_state.rb_exp_role = prefilled["experience"][0]["role"]
                st.session_state.rb_exp_company = prefilled["experience"][0]["company"]
                st.session_state.rb_exp_dates = prefilled["experience"][0]["duration"]
                st.session_state.rb_exp_bullets = prefilled["experience"][0]["bullets"]
                st.session_state.rb_edu_degree = prefilled["education"][0]["degree"]
                st.session_state.rb_edu_inst = prefilled["education"][0]["institution"]
                st.session_state.rb_edu_year = prefilled["education"][0]["year"]
                st.session_state.rb_proj_name = prefilled["projects"][0]["name"] if prefilled["projects"] else "Microservices Platform"
                st.session_state.rb_proj_desc = prefilled["projects"][0]["description"] if prefilled["projects"] else "Architected distributed cloud APIs."
                st.session_state.rb_certs = "\n".join(prefilled["certifications"]) if prefilled["certifications"] else "AWS Certified Solutions Architect"
                st.success(f"Prefilled details from '{source_cand['candidate_name']}'!")

    with rb_col_actions:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Reset Form to Template", key="rb_reset_btn", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("rb_") and k != "rb_prefill_select":
                    del st.session_state[k]
            st.rerun()

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2-Column Interface: Builder Form on Left, Live Preview on Right
    b_col_form, b_col_preview = st.columns([1.5, 1.5])

    with b_col_form:
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>1. Personal Information & Contact</h4>", unsafe_allow_html=True)
        r_name = st.text_input("Full Legal Name", value=st.session_state.get("rb_full_name", "Alex Chen"), key="rb_input_name")
        r_title = st.text_input("Professional Headline / Role", value=st.session_state.get("rb_job_title", "Senior Full-Stack Engineer"), key="rb_input_title")

        c1, c2 = st.columns(2)
        with c1:
            r_email = st.text_input("Email Address", value=st.session_state.get("rb_email", "alex.chen@example.com"), key="rb_input_email")
            r_location = st.text_input("Location / City, Country", value=st.session_state.get("rb_location", "San Francisco, CA"), key="rb_input_loc")
        with c2:
            r_phone = st.text_input("Phone Number", value=st.session_state.get("rb_phone", "+1 (415) 555-0182"), key="rb_input_phone")
            r_linkedin = st.text_input("LinkedIn Profile", value=st.session_state.get("rb_linkedin", "linkedin.com/in/alexchen"), key="rb_input_li")

        r_github = st.text_input("GitHub or Portfolio URL", value=st.session_state.get("rb_github", "github.com/alexchen"), key="rb_input_gh")

        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem; margin-top: 14px;'>2. Executive Summary</h4>", unsafe_allow_html=True)
        r_summary = st.text_area(
            "Professional Summary",
            value=st.session_state.get("rb_summary", "High-impact Senior Full-Stack Engineer with 6+ years experience architecting fault-tolerant cloud platforms, low-latency microservices, and reactive web applications."),
            height=90,
            key="rb_input_summary"
        )

        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem; margin-top: 14px;'>3. Technical Skills Taxonomy</h4>", unsafe_allow_html=True)
        r_skills = st.text_area(
            "Skills (Comma-separated)",
            value=st.session_state.get("rb_skills", "React, TypeScript, Node.js, Python, PostgreSQL, Docker, Kubernetes, AWS, REST API, Git, Redis, GraphQL"),
            height=70,
            key="rb_input_skills"
        )

        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem; margin-top: 14px;'>4. Work Experience</h4>", unsafe_allow_html=True)
        r_exp_role = st.text_input("Recent Role", value=st.session_state.get("rb_exp_role", "Lead Full-Stack Engineer"), key="rb_input_exp_role")
        e_c1, e_c2 = st.columns(2)
        with e_c1:
            r_exp_company = st.text_input("Company", value=st.session_state.get("rb_exp_company", "Apex Cloud Systems"), key="rb_input_exp_comp")
        with e_c2:
            r_exp_dates = st.text_input("Duration", value=st.session_state.get("rb_exp_dates", "2021 - Present"), key="rb_input_exp_dates")

        r_exp_bullets = st.text_area(
            "Responsibilities & Key Achievements (One per line)",
            value=st.session_state.get("rb_exp_bullets", "Spearheaded the migration of core monolith to containerized Docker & ECS microservices.\nOptimized PostgreSQL database query latencies by 42% via indexing and Redis caching.\nMentored 8 mid-level software engineers across agile software delivery sprints."),
            height=100,
            key="rb_input_exp_bullets"
        )

        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem; margin-top: 14px;'>5. Education & Academics</h4>", unsafe_allow_html=True)
        ed_c1, ed_c2, ed_c3 = st.columns([1.5, 1.5, 1.0])
        with ed_c1:
            r_edu_degree = st.text_input("Degree / Major", value=st.session_state.get("rb_edu_degree", "B.S. in Computer Science"), key="rb_input_edu_deg")
        with ed_c2:
            r_edu_inst = st.text_input("Institution", value=st.session_state.get("rb_edu_inst", "University of California, Berkeley"), key="rb_input_edu_inst")
        with ed_c3:
            r_edu_year = st.text_input("Grad Year", value=st.session_state.get("rb_edu_year", "2018"), key="rb_input_edu_yr")

        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem; margin-top: 14px;'>6. Projects & Certifications</h4>", unsafe_allow_html=True)
        r_proj_name = st.text_input("Featured Project Title", value=st.session_state.get("rb_proj_name", "Autonomous AI Resume Matcher"), key="rb_input_pname")
        r_proj_desc = st.text_input("Project Description & Technologies", value=st.session_state.get("rb_proj_desc", "Built vector similarity ranking engine using Python, Scikit-Learn, and Streamlit."), key="rb_input_pdesc")
        r_certs = st.text_input("Certifications", value=st.session_state.get("rb_certs", "AWS Certified Solutions Architect &middot; Kubernetes Certified Administrator (CKA)"), key="rb_input_certs")

    # Assemble resume data structure
    resume_payload = {
        "full_name": r_name,
        "job_title": r_title,
        "email": r_email,
        "phone": r_phone,
        "location": r_location,
        "linkedin": r_linkedin,
        "github": r_github,
        "summary": r_summary,
        "skills": r_skills,
        "experience": [
            {
                "role": r_exp_role,
                "company": r_exp_company,
                "duration": r_exp_dates,
                "bullets": r_exp_bullets
            }
        ],
        "education": [
            {
                "degree": r_edu_degree,
                "institution": r_edu_inst,
                "year": r_edu_year
            }
        ],
        "projects": [
            {
                "name": r_proj_name,
                "description": r_proj_desc
            }
        ] if r_proj_name else [],
        "certifications": [c.strip() for c in r_certs.split("·") if c.strip()] if r_certs else []
    }

    with b_col_preview:
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>Document Output & Live Preview</h4>", unsafe_allow_html=True)

        # PDF Compilation and Download
        try:
            pdf_bytes = generate_resume_pdf(resume_payload)
            clean_filename = f"{r_name.replace(' ', '_')}_Resume.pdf" if r_name else "TalentIQ_Resume.pdf"

            st.download_button(
                label=f"📄 Generate & Download Professional PDF Resume",
                data=pdf_bytes,
                file_name=clean_filename,
                mime="application/pdf",
                use_container_width=True,
                key="rb_download_pdf_btn"
            )
        except Exception as e:
            st.error(f"Error compiling PDF: {str(e)}")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # High-Fidelity Formatted HTML Resume Sheet Preview
        bullets_preview_html = "".join([f"<li style='margin-bottom: 4px;'>{b.strip('-•* ')}</li>" for b in r_exp_bullets.split('\n') if b.strip()])
        contact_line_preview = " &middot; ".join(filter(None, [r_email, r_phone, r_location, r_linkedin, r_github]))

        st.markdown(
            clean_html(f"""
            <div style="background: #FFFFFF; color: #0F172A; border-radius: 12px; padding: 28px 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.45;">
                <div style="border-bottom: 2px solid #4F46E5; padding-bottom: 10px; margin-bottom: 14px;">
                    <h2 style="font-size: 1.55rem; font-weight: 800; color: #1E3A8A; margin: 0;">{r_name}</h2>
                    <div style="font-size: 0.92rem; font-weight: 700; color: #4F46E5; text-transform: uppercase; margin-top: 2px;">{r_title}</div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 6px;">{contact_line_preview}</div>
                </div>

                <div style="margin-bottom: 14px;">
                    <div style="font-size: 0.85rem; font-weight: 800; color: #1E3A8A; text-transform: uppercase; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px;">
                        Professional Summary
                    </div>
                    <div style="font-size: 0.82rem; color: #334155;">{r_summary}</div>
                </div>

                <div style="margin-bottom: 14px;">
                    <div style="font-size: 0.85rem; font-weight: 800; color: #1E3A8A; text-transform: uppercase; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px;">
                        Technical Skills
                    </div>
                    <div style="font-size: 0.82rem; color: #334155;"><strong>Core Competencies:</strong> {r_skills}</div>
                </div>

                <div style="margin-bottom: 14px;">
                    <div style="font-size: 0.85rem; font-weight: 800; color: #1E3A8A; text-transform: uppercase; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px;">
                        Experience
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.84rem; font-weight: 700; color: #0F172A;">
                        <span>{r_exp_role} &mdash; <i>{r_exp_company}</i></span>
                        <span style="color: #64748B; font-weight: 500;">{r_exp_dates}</span>
                    </div>
                    <ul style="font-size: 0.8rem; color: #334155; padding-left: 18px; margin-top: 4px;">
                        {bullets_preview_html}
                    </ul>
                </div>

                <div style="margin-bottom: 14px;">
                    <div style="font-size: 0.85rem; font-weight: 800; color: #1E3A8A; text-transform: uppercase; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px;">
                        Education
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #334155;">
                        <span><strong>{r_edu_degree}</strong> &mdash; {r_edu_inst}</span>
                        <span style="color: #64748B;">{r_edu_year}</span>
                    </div>
                </div>

                {f'''
                <div>
                    <div style="font-size: 0.85rem; font-weight: 800; color: #1E3A8A; text-transform: uppercase; border-bottom: 1px solid #E2E8F0; padding-bottom: 3px; margin-bottom: 6px;">
                        Key Projects & Certifications
                    </div>
                    <div style="font-size: 0.82rem; color: #334155;"><strong>{r_proj_name}:</strong> {r_proj_desc}</div>
                    <div style="font-size: 0.8rem; color: #64748B; margin-top: 4px;">{r_certs}</div>
                </div>
                ''' if r_proj_name or r_certs else ''}
            </div>
            """),
            unsafe_allow_html=True
        )


# ==============================================================================
# VIEW 7: ADVANCED ANALYTICS DASHBOARD
# ==============================================================================
elif st.session_state.current_nav == "Analytics":
    st.markdown(
        render_header(
            title="Recruitment Intelligence & Advanced Analytics",
            subtitle="Quantitative metrics on candidate skill distributions, match score patterns, talent density, and in-demand role requirements.",
            badge="Executive Analytics"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates
    history = st.session_state.screening_history
    last_results = st.session_state.get("last_results", [])
    jobs = st.session_state.job_descriptions

    # Compute un-fabricated analytics summary
    analytics_data = compute_analytics_summary(candidates, history, last_results, jobs)

    # 4 Key Metrics Bar
    an_c1, an_c2, an_c3, an_c4 = st.columns(4)
    with an_c1:
        st.markdown(
            render_kpi_card(
                title="Total Resumes Processed",
                value=str(analytics_data["total_resumes"]),
                subtitle=f"{analytics_data['total_resumes']} active candidate profiles",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with an_c2:
        st.markdown(
            render_kpi_card(
                title="Jobs Analyzed",
                value=str(analytics_data["total_jobs_analyzed"]),
                subtitle=f"{len(jobs)} active job templates",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with an_c3:
        avg_score_disp = f"{analytics_data['avg_match_score']}%" if analytics_data["has_evaluations"] else "N/A"
        st.markdown(
            render_kpi_card(
                title="Average Match Score",
                value=avg_score_disp,
                subtitle="Across evaluated candidates" if analytics_data["has_evaluations"] else "No evaluations yet",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
            ),
            unsafe_allow_html=True
        )
    with an_c4:
        st.markdown(
            render_kpi_card(
                title="Shortlisted Candidates",
                value=str(analytics_data["shortlisted_count"]),
                subtitle="Bookmarked talent profiles",
                icon='<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if not candidates:
        st.markdown(
            render_empty_state(
                title="No Candidate Data for Analytics",
                description="Upload resumes in 'Resume Screening' and evaluate them in 'Job Matching' to generate interactive score distribution charts and skill intelligence plots.",
                action_text="Start by uploading resumes."
            ),
            unsafe_allow_html=True
        )
    else:
        # Row 1 Charts: Match Score Ranges & Detected Skills
        chart_r1_c1, chart_r1_c2 = st.columns(2)
        with chart_r1_c1:
            if analytics_data["has_evaluations"]:
                fig_scores = create_score_distribution_chart(analytics_data["score_ranges"])
                st.plotly_chart(fig_scores, use_container_width=True)
            else:
                st.info("💡 Run candidate matching under 'Job Matching' to view the Match-Score Range Distribution.")

        with chart_r1_c2:
            fig_skills = create_top_skills_chart(analytics_data["top_skills"], max_items=10)
            st.plotly_chart(fig_skills, use_container_width=True)

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        # Row 2 Charts: In-Demand Skills vs Talent Pool Gaps & Job-Wise Results
        chart_r2_c1, chart_r2_c2 = st.columns(2)
        with chart_r2_c1:
            fig_demand = create_skill_demand_vs_missing_chart(
                analytics_data["job_demand_counts"],
                analytics_data["missing_skill_counts"],
                max_items=8
            )
            st.plotly_chart(fig_demand, use_container_width=True)

        with chart_r2_c2:
            curr_job = get_current_job()
            fig_jobs = create_job_wise_results_chart(history, last_results, curr_job.get("title", ""))
            st.plotly_chart(fig_jobs, use_container_width=True)

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Recent Screening History Log
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>Recent Screening Event Audit Log</h4>", unsafe_allow_html=True)
        if not history:
            st.info("No historical screening runs recorded yet in this session. Results appear here after running evaluations in Job Matching.")
        else:
            df_hist = pd.DataFrame(history)
            st.dataframe(df_hist, use_container_width=True)


# ==============================================================================
# VIEW 8: SAVED SESSIONS (STATE PERSISTENCE)
# ==============================================================================
elif st.session_state.current_nav == "Saved Sessions":
    st.markdown(
        render_header(
            title="Screening Sessions & Local State Persistence",
            subtitle="Persist screening runs, candidate rosters, target roles, and match evaluations to disk, and restore them anytime.",
            badge="Persistence Engine"
        ),
        unsafe_allow_html=True
    )

    candidates = st.session_state.candidates
    last_results = st.session_state.get("last_results", [])
    active_job = get_current_job()

    save_col1, save_col2 = st.columns([1.6, 1.4])

    with save_col1:
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>1. Save Current Session</h4>", unsafe_allow_html=True)
        default_sess_name = f"Screening - {active_job.get('title', 'Role')} ({time.strftime('%b %d, %Y')})"
        session_name_input = st.text_input("Session Name / Label", value=default_sess_name, key="sess_name_input")

        st.caption(f"Will save {len(candidates)} candidate(s), {len(last_results)} evaluation result(s), and role '{active_job.get('title')}' to local disk.")

        if st.button("💾 Save Session to Disk", key="save_session_btn", use_container_width=True):
            if not candidates and not last_results:
                st.warning("Cannot save an entirely empty session. Upload candidates or evaluate roles first.")
            else:
                saved = save_session(
                    name=session_name_input,
                    job=active_job,
                    candidates=candidates,
                    last_results=last_results,
                    weights=st.session_state.weights,
                    screening_history=st.session_state.screening_history
                )
                st.success(f"Successfully saved session '{saved['name']}' to local storage!")
                st.rerun()

    with save_col2:
        st.markdown("<h4 style='color: #FFFFFF; font-size: 1.05rem;'>2. Import Session from JSON</h4>", unsafe_allow_html=True)
        uploaded_json = st.file_uploader("Upload Saved Session File (.json)", type=["json"], key="session_json_uploader")
        if uploaded_json:
            if st.button("📥 Import & Restore Session", key="import_session_btn", use_container_width=True):
                content = uploaded_json.read().decode("utf-8", errors="ignore")
                ok, msg, imported_data = import_session_json(content)
                if ok and imported_data:
                    restore_session_to_memory(imported_data)
                    st.success(f"Session imported and restored! Loaded {len(imported_data.get('candidates', []))} candidates.")
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Saved Sessions Table & Roster
    st.markdown("<h4 style='color: #FFFFFF; font-size: 1.1rem;'>Saved Sessions on Local Disk</h4>", unsafe_allow_html=True)
    saved_list = list_sessions()

    if not saved_list:
        st.markdown(
            render_empty_state(
                title="No Saved Sessions Found",
                description="Use the 'Save Current Session' form above to persist your candidate rankings and evaluations for future sessions.",
                action_text="Saved sessions are permanently retained in the data/sessions directory."
            ),
            unsafe_allow_html=True
        )
    else:
        for s in saved_list:
            sid = s["session_id"]
            created_disp = s["created_at"][:19].replace("T", " ") if "T" in s["created_at"] else s["created_at"]

            st.markdown(
                clean_html(f"""
                <div class="tiq-card" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                        <div>
                            <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">{s['name']}</div>
                            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 2px;">
                                Target Role: <strong>{s['job_title']}</strong> &middot; Saved: {created_disp} &middot; Size: {s.get('file_size', 0)/1024:.1f} KB
                            </div>
                            <div style="font-size: 0.82rem; color: #CBD5E1; margin-top: 6px;">
                                👥 <strong>{s['candidate_count']}</strong> Candidates &middot; ★ <strong>{s['shortlisted_count']}</strong> Shortlisted &middot; Avg Score: <strong>{s['avg_score']}%</strong> &middot; Top: <strong>{s['top_score']}%</strong>
                            </div>
                        </div>
                    </div>
                </div>
                """),
                unsafe_allow_html=True
            )

            s_act1, s_act2, s_act3, s_act_space = st.columns([1.8, 1.4, 1.2, 2.6])
            with s_act1:
                if st.button(f"📂 Restore Session", key=f"restore_btn_{sid}", use_container_width=True):
                    loaded_sess = load_session(sid)
                    if loaded_sess:
                        restore_session_to_memory(loaded_sess)
                        st.success(f"Restored session '{loaded_sess.get('name')}'! Navigating to Job Matching...")
                        st.session_state.current_nav = "Job Matching"
                        st.rerun()
            with s_act2:
                json_data = export_session_json(sid)
                if json_data:
                    st.download_button(
                        label="📥 Export JSON",
                        data=json_data,
                        file_name=f"{sid}.json",
                        mime="application/json",
                        key=f"dl_json_{sid}",
                        use_container_width=True
                    )
            with s_act3:
                if st.button("🗑 Delete", key=f"del_sess_{sid}", use_container_width=True):
                    delete_session(sid)
                    st.success("Session deleted from disk.")
                    st.rerun()


# ==============================================================================
# VIEW 9: SETTINGS & CONFIGURATION
# ==============================================================================
elif st.session_state.current_nav == "Settings":
    st.markdown(
        render_header(
            title="System & Matching Configuration",
            subtitle="Configure algorithm weights, threshold parameters, and active role descriptions.",
            badge="Settings"
        ),
        unsafe_allow_html=True
    )

    w_col1, w_col2 = st.columns([1.5, 1.5])

    with w_col1:
        st.markdown("<h4 style='color: #FFFFFF;'>Match Score Weight Distribution</h4>", unsafe_allow_html=True)
        s_weight = st.slider("Skill Overlap Weight", 0.0, 1.0, float(st.session_state.weights["skills"]), 0.05)
        sem_weight = st.slider("Semantic Similarity Weight", 0.0, 1.0, float(st.session_state.weights["semantic"]), 0.05)
        exp_weight = st.slider("Experience Alignment Weight", 0.0, 1.0, float(st.session_state.weights["experience"]), 0.05)

        total = s_weight + sem_weight + exp_weight
        if total > 0:
            st.session_state.weights = {
                "skills": s_weight / total,
                "semantic": sem_weight / total,
                "experience": exp_weight / total
            }
            st.caption(f"Normalized weights: Skills ({int(st.session_state.weights['skills']*100)}%), Semantic ({int(st.session_state.weights['semantic']*100)}%), Exp ({int(st.session_state.weights['experience']*100)}%)")

    with w_col2:
        st.markdown("<h4 style='color: #FFFFFF;'>Data Management</h4>", unsafe_allow_html=True)
        if st.button("🗑 Clear In-Memory Candidate Pool", use_container_width=True):
            clear_all_candidates()
            st.success("Candidate pool cleared successfully!")
            st.rerun()

        st.markdown(
            clean_html("""
            <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 14px;">
                Clearing memory resets active candidates and current evaluation history without affecting saved sessions on disk.
            </div>
            """),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #FFFFFF;'>User Account &amp; Profile Security</h4>", unsafe_allow_html=True)
    curr_u = get_current_user()
    p_col1, p_col2 = st.columns([1.5, 1.5])
    with p_col1:
        st.markdown(
            clean_html(f"""
            <div class="tiq-card">
                <div style="font-size: 0.82rem; font-weight: 700; color: #818CF8; text-transform: uppercase;">Authenticated Account</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin: 6px 0 2px 0;">{curr_u.get('name', 'User')}</div>
                <div style="font-size: 0.84rem; color: #94A3B8;">Role: {curr_u.get('role', 'user').title()} &middot; Email: {curr_u.get('email', '')}</div>
                <div style="font-size: 0.76rem; color: #34D399; margin-top: 8px;">● Isolated User Session Verified</div>
            </div>
            """),
            unsafe_allow_html=True
        )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        if st.button("🔒 Sign Out Session", key="settings_user_sign_out_btn", use_container_width=True):
            sign_out_user()
            st.rerun()

    with p_col2:
        with st.expander("🔑 Change Account Password", expanded=False):
            with st.form("user_change_pwd_form"):
                cur_pw = st.text_input("Current Password", type="password")
                new_pw_val = st.text_input("New Password (8+ chars, letters & digits)", type="password")
                conf_new_pw_val = st.text_input("Confirm New Password", type="password")
                chg_submit = st.form_submit_button("Update Password", use_container_width=True)

            if chg_submit:
                if curr_u.get("id"):
                    db_u = get_user_by_id(curr_u["id"])
                    if not db_u or not verify_password(cur_pw, db_u["password_hash"]):
                        st.error("Incorrect current password.")
                    elif new_pw_val != conf_new_pw_val:
                        st.error("New passwords do not match.")
                    else:
                        valid_p, p_err = validate_password_strength(new_pw_val)
                        if not valid_p:
                            st.error(p_err)
                        else:
                            new_h = hash_password(new_pw_val)
                            update_user_profile(curr_u["id"], password_hash=new_h)
                            st.success("Password updated successfully!")
                else:
                    st.info("Demo sessions without persistent database IDs cannot change password.")
