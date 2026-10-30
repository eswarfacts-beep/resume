"""
TalentIQ AI - Administrative Dashboard & System Operations Module
Provides centralized administration: User Management, Global Resume Metadata,
Job Taxonomy Management, Real-time Audit Logs, System Analytics, and Security Controls.
Guarded strictly by backend role-based access control (RBAC).
"""

import time
import html
import json
import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.styles import (
    clean_html,
    render_admin_header,
    render_kpi_card,
    render_score_badge,
    render_empty_state
)
from src.auth import (
    require_role,
    sign_out_user,
    get_current_user,
    hash_password,
    verify_password,
    validate_password_strength
)
from src.database import (
    get_db_connection,
    list_users,
    update_user_status,
    update_user_role,
    delete_user,
    update_user_profile,
    get_audit_logs,
    log_audit_event,
    db_get_admin_overview_stats,
    db_get_all_resume_metadata,
    db_delete_resume,
    db_get_all_jobs,
    db_save_job,
    db_update_job,
    db_delete_job,
    db_get_all_screenings,
    get_user_by_id
)
from src.storage import add_new_job_description, delete_job_description


def render_admin_dashboard():
    """
    Renders the complete Administrative Dashboard.
    Strictly verifies admin role before displaying any data or processing any request.
    """
    # Strict Backend RBAC Verification
    if not require_role("admin"):
        st.error("⛔ Access Denied: Administrator privileges required to access this resource.")
        st.info("You do not have permission to view the administrative portal. Please return to the User Portal.")
        if st.button("← Return to User Portal", key="admin_forbidden_return"):
            st.session_state.current_nav = "Dashboard"
            st.rerun()
        st.stop()

    curr_admin = get_current_user()

    ADMIN_NAV_OPTIONS = [
        "Admin Overview",
        "User Management",
        "Resume Management",
        "Job Management",
        "Reports & Analytics",
        "System Settings"
    ]

    # Sidebar for Admin Portal
    with st.sidebar:
        st.markdown(
            clean_html(f"""
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid rgba(239, 68, 68, 0.25); margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #7C3AED 0%, #EF4444 100%); display: flex; align-items: center; justify-content: center;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    </div>
                    <div>
                        <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">TalentIQ <span style="color: #EF4444;">Admin</span></div>
                        <div style="font-size: 0.7rem; color: #FCA5A5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Operations Console</div>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        # Admin Profile Indicator
        st.markdown(
            clean_html(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 12px 14px; margin-bottom: 16px;">
                <div style="font-size: 0.84rem; font-weight: 700; color: #FFFFFF;">{html.escape(curr_admin.get('name', 'Administrator'))}</div>
                <div style="font-size: 0.72rem; color: #FCA5A5;">{html.escape(curr_admin.get('email', 'admin@talentiq.ai'))}</div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #34D399; margin-top: 6px; font-weight: 600;">
                    <span>●</span> Privileged Session Active
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        col_adm_out, col_adm_u = st.columns([1.5, 1.3])
        with col_adm_out:
            if st.button("🔒 Sign Out", key="admin_sidebar_logout_btn", use_container_width=True):
                sign_out_user()
                st.rerun()
        with col_adm_u:
            if st.button("👥 User App", key="admin_jump_user_app", use_container_width=True):
                st.session_state.role = "user"
                st.session_state.current_nav = "Dashboard"
                st.rerun()

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        current_admin_nav = st.session_state.get("admin_nav", "Admin Overview")
        if current_admin_nav not in ADMIN_NAV_OPTIONS:
            current_admin_nav = "Admin Overview"
            st.session_state.admin_nav = "Admin Overview"

        selected_admin_nav = st.radio(
            "Admin Navigation",
            ADMIN_NAV_OPTIONS,
            index=ADMIN_NAV_OPTIONS.index(current_admin_nav),
            key="admin_sidebar_nav_radio",
            label_visibility="collapsed"
        )

        if selected_admin_nav != st.session_state.admin_nav:
            st.session_state.admin_nav = selected_admin_nav
            st.rerun()

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(
            clean_html("""
            <div style="font-size: 0.72rem; color: #64748B; text-align: center;">
                TalentIQ AI &middot; Administrative Console<br/>
                Strict RBAC &amp; Audit Active
            </div>
            """),
            unsafe_allow_html=True
        )

    # Main Admin Content Router
    view = st.session_state.admin_nav

    if view == "Admin Overview":
        _render_admin_overview()
    elif view == "User Management":
        _render_user_management(curr_admin)
    elif view == "Resume Management":
        _render_resume_management()
    elif view == "Job Management":
        _render_job_management(curr_admin)
    elif view == "Reports & Analytics":
        _render_reports_and_analytics()
    elif view == "System Settings":
        _render_system_settings(curr_admin)


# ==============================================================================
# SUB-VIEW A: ADMIN OVERVIEW
# ==============================================================================

def _render_admin_overview():
    st.markdown(
        render_admin_header(
            title="System Operations & Platform Health",
            subtitle="Real-time administrative telemetry, registered user metrics, screening volumes, and audit logs."
        ),
        unsafe_allow_html=True
    )

    stats = db_get_admin_overview_stats()

    # Top Row: 4 Primary Admin KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    user_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
    active_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
    doc_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>'
    screen_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'

    with col1:
        st.markdown(
            render_kpi_card(
                title="Total Users",
                value=str(stats["total_users"]),
                delta=f"{stats['active_users']} Active",
                icon=user_icon,
                subtitle="Accounts registered"
            ),
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            render_kpi_card(
                title="Resumes Uploaded",
                value=str(stats["total_resumes"]),
                delta="Platform total",
                icon=doc_icon,
                subtitle="Across all user pools"
            ),
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            render_kpi_card(
                title="Active Jobs",
                value=str(stats["total_jobs"]),
                delta="Taxonomy catalog",
                icon=active_icon,
                subtitle="Published job definitions"
            ),
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            render_kpi_card(
                title="AI Screenings",
                value=str(stats["total_screenings"]),
                delta=f"Avg Score: {stats['avg_score']}%" if stats['avg_score'] > 0 else "Ready",
                icon=screen_icon,
                subtitle="Matches computed"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Middle Section: System Status & Quick Actions
    col_stat, col_act = st.columns([1.5, 1.2])

    with col_stat:
        st.markdown(
            clean_html("""
            <div class="tiq-card">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #818CF8; margin-bottom: 14px;">
                    🛡️ System Security &amp; Platform Status
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                        <div style="font-size: 0.74rem; color: #94A3B8;">Authentication Engine</div>
                        <div style="font-weight: 700; color: #34D399; font-size: 0.88rem; margin-top: 2px;">Bcrypt (12 Rounds)</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                        <div style="font-size: 0.74rem; color: #94A3B8;">Persistent Database</div>
                        <div style="font-weight: 700; color: #38BDF8; font-size: 0.88rem; margin-top: 2px;">SQLite WAL Mode</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                        <div style="font-size: 0.74rem; color: #94A3B8;">Access Control</div>
                        <div style="font-weight: 700; color: #A78BFA; font-size: 0.88rem; margin-top: 2px;">Role-Based (RBAC)</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.06);">
                        <div style="font-size: 0.74rem; color: #94A3B8;">Brute Force Protection</div>
                        <div style="font-weight: 700; color: #FBBF24; font-size: 0.88rem; margin-top: 2px;">5-Attempt Lockout</div>
                    </div>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.5;">
                    TalentIQ AI operates under strict per-account data isolation. Normal users cannot view another user's candidate records or private resume content.
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    with col_act:
        st.markdown(
            clean_html("""
            <div class="tiq-card">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.88rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #EF4444; margin-bottom: 14px;">
                    ⚡ Quick Operations
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
        if st.button("👥 Manage Registered Users", use_container_width=True):
            st.session_state.admin_nav = "User Management"
            st.rerun()
        if st.button("📄 Inspect Resume Metadata", use_container_width=True):
            st.session_state.admin_nav = "Resume Management"
            st.rerun()
        if st.button("💼 Add or Edit Job Taxonomy", use_container_width=True):
            st.session_state.admin_nav = "Job Management"
            st.rerun()
        if st.button("📊 View Platform Reports", use_container_width=True):
            st.session_state.admin_nav = "Reports & Analytics"
            st.rerun()

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # Real-time System Audit Stream
    st.subheader("📋 Recent Security & Administrative Audit Events")
    logs = get_audit_logs(limit=15)
    if logs:
        df_logs = pd.DataFrame(logs)
        df_logs = df_logs[["timestamp", "user_email", "action", "details", "status"]]
        df_logs.columns = ["Timestamp", "User Email", "Action", "Details", "Status"]
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No audit events recorded yet.")


# ==============================================================================
# SUB-VIEW B: USER MANAGEMENT
# ==============================================================================

def _render_user_management(curr_admin: dict):
    st.markdown(
        render_admin_header(
            title="User Account Management",
            subtitle="Inspect registered user credentials, toggle account activation, modify assigned roles, and manage permissions."
        ),
        unsafe_allow_html=True
    )

    col_s1, col_s2 = st.columns([2.5, 1.2])
    with col_s1:
        search_q = st.text_input("🔍 Search users by name or email address", placeholder="e.g. sarah, admin@talentiq.ai...", key="user_mgmt_search")
    with col_s2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh User Roster", key="refresh_users_btn", use_container_width=True):
            st.rerun()

    users = list_users(search_query=search_q)

    if not users:
        st.markdown(render_empty_state(title="No Users Found", description="No user accounts matched your search criteria."), unsafe_allow_html=True)
        return

    # Display Summary Pills
    active_count = len([u for u in users if u["is_active"] == 1])
    admin_count = len([u for u in users if u["role"] == "admin"])
    user_count = len([u for u in users if u["role"] == "user"])

    st.markdown(
        clean_html(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 18px; flex-wrap: wrap;">
            <span style="background: rgba(79, 70, 229, 0.15); border: 1px solid rgba(99, 102, 241, 0.35); padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #C7D2FE;">
                Total: <strong>{len(users)}</strong>
            </span>
            <span style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #6EE7B7;">
                Active: <strong>{active_count}</strong>
            </span>
            <span style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.35); padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #FCA5A5;">
                Admins: <strong>{admin_count}</strong>
            </span>
            <span style="background: rgba(6, 182, 212, 0.15); border: 1px solid rgba(6, 182, 212, 0.35); padding: 6px 14px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; color: #67E8F9;">
                Standard Users: <strong>{user_count}</strong>
            </span>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Detailed Interactive User Cards & Controls
    for u in users:
        u_id = u["id"]
        is_active = bool(u["is_active"])
        role = u["role"]
        is_self = (curr_admin.get("id") == u_id) or (curr_admin.get("email") == u["email"])

        status_badge = '<span style="color: #34D399; font-weight: 700;">● Active</span>' if is_active else '<span style="color: #EF4444; font-weight: 700;">○ Deactivated</span>'
        role_badge = '<span style="background: rgba(239, 68, 68, 0.2); color: #FCA5A5; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.74rem;">ADMIN</span>' if role == "admin" else '<span style="background: rgba(6, 182, 212, 0.2); color: #67E8F9; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 0.74rem;">USER</span>'

        with st.expander(f"{u['full_name']} ({u['email']}) — {role.upper()}", expanded=False):
            col_info, col_ctrl = st.columns([1.6, 1.4])
            with col_info:
                st.markdown(f"**User ID:** `{u_id}`")
                st.markdown(f"**Full Name:** {u['full_name']}")
                st.markdown(f"**Email:** `{u['email']}`")
                st.markdown(f"**Assigned Role:** {role_badge}", unsafe_allow_html=True)
                st.markdown(f"**Account Status:** {status_badge}", unsafe_allow_html=True)
                st.markdown(f"**Registered:** {u.get('created_at', 'N/A')}")
                st.markdown(f"**Last Sign In:** {u.get('last_login') or 'Never'}")
                if u.get("failed_login_attempts"):
                    st.markdown(f"**Failed Attempts:** `{u['failed_login_attempts']}`")

            with col_ctrl:
                st.markdown("##### Administrative Actions")
                if is_self:
                    st.info("ℹ️ This is your active administrator account. To modify your own password, use System Settings.")
                else:
                    # Toggle Status
                    toggle_label = "🔴 Deactivate Account" if is_active else "🟢 Activate Account"
                    if st.button(toggle_label, key=f"toggle_user_status_{u_id}", use_container_width=True):
                        new_state = 0 if is_active else 1
                        update_user_status(u_id, new_state)
                        log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "USER_STATUS_CHANGE", f"Target User ID {u_id} set to active={new_state}", "SUCCESS")
                        st.success(f"Updated status for {u['full_name']}.")
                        st.rerun()

                    # Change Role
                    new_target_role = "user" if role == "admin" else "admin"
                    role_btn_label = f"Switch to {new_target_role.upper()}"
                    if st.button(f"🛡️ {role_btn_label}", key=f"toggle_role_{u_id}", use_container_width=True):
                        update_user_role(u_id, new_target_role)
                        log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "USER_ROLE_CHANGE", f"Target User ID {u_id} role updated to {new_target_role}", "SUCCESS")
                        st.success(f"Role updated to {new_target_role.upper()} for {u['full_name']}.")
                        st.rerun()

                    # Delete Account with Confirmation
                    del_confirm = st.checkbox("Confirm permanent account deletion", key=f"del_confirm_check_{u_id}")
                    if del_confirm:
                        if st.button("🗑️ Permanently Delete User", key=f"del_user_btn_{u_id}", type="primary", use_container_width=True):
                            ok = delete_user(u_id)
                            if ok:
                                log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "USER_DELETED", f"Target User ID {u_id} ({u['email']}) deleted.", "SUCCESS")
                                st.success(f"User account {u['email']} and associated data permanently deleted.")
                                st.rerun()
                            else:
                                st.error("Failed to delete user. The system requires at least one active administrator.")


# ==============================================================================
# SUB-VIEW C: RESUME MANAGEMENT
# ==============================================================================

def _render_resume_management():
    st.markdown(
        render_admin_header(
            title="Global Resume & Candidate Pool Metadata",
            subtitle="Monitor uploaded resumes across all accounts, inspect processing status, and protect candidate privacy."
        ),
        unsafe_allow_html=True
    )

    metadata = db_get_all_resume_metadata()

    if not metadata:
        st.markdown(
            render_empty_state(
                title="No Resumes Uploaded Yet",
                description="When normal users upload resumes to the platform, their metadata and processing status will appear here."
            ),
            unsafe_allow_html=True
        )
        return

    st.markdown(
        clean_html(f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div style="font-size: 0.88rem; color: #CBD5E1;">
                    Total Uploaded Documents: <strong style="color: #38BDF8;">{len(metadata)}</strong>
                </div>
                <div style="font-size: 0.78rem; color: #94A3B8;">
                    🔒 <strong>Privacy Assurance:</strong> Raw resume content is strictly isolated to candidate owners.
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    df_meta = pd.DataFrame(metadata)
    # Format file size in KB
    df_meta["Size (KB)"] = (df_meta["file_size"] / 1024).round(1)
    df_meta["Shortlisted"] = df_meta["shortlisted"].apply(lambda s: "★ Yes" if s else "No")

    display_cols = ["id", "candidate_name", "filename", "user_email", "Size (KB)", "years_of_experience", "Shortlisted", "status", "created_at"]
    df_display = df_meta[display_cols]
    df_display.columns = ["Resume ID", "Candidate Name", "Filename", "Owner Account", "Size (KB)", "Experience (Yrs)", "Shortlist", "Status", "Uploaded At"]

    st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Resume Administrative Cleanup
    st.markdown("##### Administrative Record Cleanup")
    resume_ids = [r["id"] for r in metadata]
    col_sel, col_act = st.columns([2, 1.2])
    with col_sel:
        target_res_id = st.selectbox("Select Resume Record to Delete", resume_ids, format_func=lambda x: f"{x} ({next((r['filename'] for r in metadata if r['id'] == x), '')})")
    with col_act:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Remove Resume Record", key="admin_del_res_btn", use_container_width=True):
            if target_res_id:
                db_delete_resume(target_res_id)
                st.success(f"Resume {target_res_id} successfully deleted from database.")
                st.rerun()


# ==============================================================================
# SUB-VIEW D: JOB MANAGEMENT
# ==============================================================================

def _render_job_management(curr_admin: dict):
    st.markdown(
        render_admin_header(
            title="Job Description & Taxonomy Management",
            subtitle="Publish new job roles, modify required skill sets, and manage available positions for AI screening."
        ),
        unsafe_allow_html=True
    )

    jobs = db_get_all_jobs()

    tab_list, tab_add, tab_edit = st.tabs(["📋 Published Roles Catalog", "➕ Publish New Job Role", "✏️ Edit Existing Job"])

    with tab_list:
        if not jobs:
            st.info("No active job descriptions published yet.")
        else:
            for j in jobs:
                jid = j["id"]
                with st.expander(f"{j['title']} &middot; {j['department']} ({j['min_experience']} yrs exp)", expanded=False):
                    st.markdown(f"**Job ID:** `{jid}`")
                    st.markdown(f"**Department:** {j['department']}")
                    st.markdown(f"**Minimum Experience:** {j['min_experience']} years")
                    skills = j.get("required_skills", [])
                    st.markdown(f"**Required Skills ({len(skills)}):** " + ", ".join([f"`{s}`" for s in skills]))
                    st.markdown(f"**Description:**\n{j['description']}")

                    col_del1, col_del2 = st.columns([3, 1])
                    with col_del2:
                        del_job_confirm = st.checkbox("Confirm delete", key=f"del_job_chk_{jid}")
                        if del_job_confirm:
                            if st.button("🗑️ Delete Job", key=f"del_job_btn_{jid}", type="primary", use_container_width=True):
                                delete_job_description(jid)
                                log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "JOB_DELETED", f"Job {jid} ({j['title']}) deleted.", "SUCCESS")
                                st.success(f"Job '{j['title']}' deleted successfully.")
                                st.rerun()

    with tab_add:
        st.markdown("##### Create a New Job Posting")
        with st.form("admin_create_job_form"):
            new_title = st.text_input("Job Title *", placeholder="e.g. Lead Cloud Architect")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                new_dept = st.text_input("Department *", placeholder="e.g. Cloud Infrastructure")
            with col_d2:
                new_exp = st.number_input("Minimum Experience (Years) *", min_value=0.0, max_value=25.0, value=3.0, step=0.5)
            new_skills_raw = st.text_input("Required Skills (Comma separated) *", placeholder="e.g. AWS, Kubernetes, Terraform, Docker, Python, CI/CD")
            new_desc = st.text_area("Full Job Description *", placeholder="Enter comprehensive job expectations, qualifications, responsibilities...", height=150)

            submit_job = st.form_submit_button("🚀 Publish Job to Platform", use_container_width=True)

        if submit_job:
            if not new_title.strip() or not new_dept.strip() or not new_desc.strip():
                st.error("Please fill out all required fields.")
            else:
                skills_list = [s.strip() for s in new_skills_raw.split(",") if s.strip()]
                generated_id = f"job_custom_{int(time.time())}"
                new_job_dict = {
                    "id": generated_id,
                    "title": new_title.strip(),
                    "department": new_dept.strip(),
                    "min_experience": float(new_exp),
                    "required_skills": skills_list,
                    "description": new_desc.strip()
                }
                ok = add_new_job_description(new_job_dict, created_by=curr_admin.get("id"))
                if ok:
                    log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "JOB_CREATED", f"Job {generated_id} ({new_title}) published.", "SUCCESS")
                    st.success(f"Job '{new_title}' successfully published to the platform!")
                    time.sleep(0.1)
                    st.rerun()
                else:
                    st.error("Failed to persist job into database.")

    with tab_edit:
        st.markdown("##### Edit an Existing Job Posting")
        if not jobs:
            st.info("No jobs available to edit.")
        else:
            job_opts = {f"{j['title']} ({j['id']})": j for j in jobs}
            chosen_key = st.selectbox("Select Job to Edit", list(job_opts.keys()))
            chosen_job = job_opts[chosen_key]

            with st.form(f"edit_job_form_{chosen_job['id']}"):
                edit_title = st.text_input("Job Title", value=chosen_job["title"])
                col_ed1, col_ed2 = st.columns(2)
                with col_ed1:
                    edit_dept = st.text_input("Department", value=chosen_job["department"])
                with col_ed2:
                    edit_exp = st.number_input("Minimum Experience (Years)", min_value=0.0, max_value=25.0, value=float(chosen_job["min_experience"]), step=0.5)
                edit_skills_str = st.text_input("Required Skills (Comma separated)", value=", ".join(chosen_job.get("required_skills", [])))
                edit_desc = st.text_area("Full Job Description", value=chosen_job["description"], height=160)

                save_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if save_edit:
                updated_skills = [s.strip() for s in edit_skills_str.split(",") if s.strip()]
                updates = {
                    "title": edit_title.strip(),
                    "department": edit_dept.strip(),
                    "min_experience": float(edit_exp),
                    "required_skills": updated_skills,
                    "description": edit_desc.strip()
                }
                db_update_job(chosen_job["id"], updates)
                # Sync in session state
                for idx, sj in enumerate(st.session_state.job_descriptions):
                    if sj["id"] == chosen_job["id"]:
                        st.session_state.job_descriptions[idx].update(updates)
                log_audit_event(curr_admin.get("id"), curr_admin.get("email"), "JOB_UPDATED", f"Job {chosen_job['id']} updated.", "SUCCESS")
                st.success(f"Job '{edit_title}' updated successfully!")
                time.sleep(0.1)
                st.rerun()


# ==============================================================================
# SUB-VIEW E: REPORTS & ANALYTICS
# ==============================================================================

def _render_reports_and_analytics():
    st.markdown(
        render_admin_header(
            title="Platform Intelligence & System Analytics",
            subtitle="Aggregated telemetry across all user registrations, screening activities, and downloadable audit reports."
        ),
        unsafe_allow_html=True
    )

    users = list_users()
    screenings = db_get_all_screenings(limit=500)
    jobs = db_get_all_jobs()
    logs = get_audit_logs(limit=200)

    # 1. User Role Distribution Chart & Job Department Chart
    col_ch1, col_ch2 = st.columns(2)

    with col_ch1:
        st.markdown("##### User Roles & Status Breakdown")
        if users:
            df_u = pd.DataFrame(users)
            role_counts = df_u["role"].value_counts().reset_index()
            role_counts.columns = ["Role", "Count"]
            fig_role = px.pie(
                role_counts,
                names="Role",
                values="Count",
                color="Role",
                color_discrete_map={"admin": "#EF4444", "user": "#4F46E5"},
                hole=0.45
            )
            fig_role.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E1"),
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig_role, use_container_width=True)
        else:
            st.info("No user data recorded yet.")

    with col_ch2:
        st.markdown("##### Job Taxonomy by Department")
        if jobs:
            df_j = pd.DataFrame(jobs)
            dept_counts = df_j["department"].value_counts().reset_index()
            dept_counts.columns = ["Department", "Job Count"]
            fig_dept = px.bar(
                dept_counts,
                x="Department",
                y="Job Count",
                color="Job Count",
                color_continuous_scale="Blues"
            )
            fig_dept.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#CBD5E1"),
                margin=dict(l=10, r=10, t=20, b=10)
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        else:
            st.info("No job descriptions available.")

    # 2. System Screening Score Distribution
    st.markdown("##### System-Wide Candidate Match Score Distribution")
    if screenings:
        df_scr = pd.DataFrame(screenings)
        fig_hist = px.histogram(
            df_scr,
            x="composite_score",
            nbins=10,
            color_discrete_sequence=["#06B6D4"],
            labels={"composite_score": "Composite Match Score (%)"}
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            margin=dict(l=10, r=10, t=20, b=10)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Screening operations will populate match score distribution charts once users run screenings.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # 3. Downloadable Administrative Reports
    st.markdown("##### 📥 Export Administrative Records & Reports")
    col_dl1, col_dl2, col_dl3 = st.columns(3)

    with col_dl1:
        if users:
            df_u_export = pd.DataFrame(users)
            csv_users = df_u_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Registered Users CSV",
                csv_users,
                file_name="talentiq_registered_users.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_dl2:
        res_meta = db_get_all_resume_metadata()
        if res_meta:
            df_res_export = pd.DataFrame(res_meta)
            csv_res = df_res_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Resumes Metadata CSV",
                csv_res,
                file_name="talentiq_resumes_metadata.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_dl3:
        if logs:
            df_logs_export = pd.DataFrame(logs)
            csv_logs = df_logs_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Audit Trail CSV",
                csv_logs,
                file_name="talentiq_security_audit_logs.csv",
                mime="text/csv",
                use_container_width=True
            )


# ==============================================================================
# SUB-VIEW F: SYSTEM SETTINGS
# ==============================================================================

def _render_system_settings(curr_admin: dict):
    st.markdown(
        render_admin_header(
            title="System Settings & Admin Security",
            subtitle="Manage administrator credentials, inspect infrastructure configuration, and control security parameters."
        ),
        unsafe_allow_html=True
    )

    col_set1, col_set2 = st.columns(2)

    with col_set1:
        st.markdown(
            clean_html("""
            <div class="tiq-card">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
                    🔑 Update Administrator Password
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        with st.form("admin_password_change_form"):
            current_pwd = st.text_input("Current Admin Password", type="password")
            new_pwd = st.text_input("New Admin Password (8+ chars, letters & digits)", type="password")
            confirm_new_pwd = st.text_input("Confirm New Admin Password", type="password")
            submit_pwd = st.form_submit_button("Update Password", use_container_width=True)

        if submit_pwd:
            db_admin = get_user_by_id(curr_admin["id"])
            if not db_admin or not verify_password(current_pwd, db_admin["password_hash"]):
                st.error("Incorrect current admin password.")
            elif new_pwd != confirm_new_pwd:
                st.error("New passwords do not match.")
            else:
                valid_p, p_err = validate_password_strength(new_pwd)
                if not valid_p:
                    st.error(p_err)
                else:
                    new_hash = hash_password(new_pwd)
                    update_user_profile(curr_admin["id"], password_hash=new_hash)
                    log_audit_event(curr_admin["id"], curr_admin["email"], "ADMIN_PASSWORD_UPDATED", "Administrator password changed successfully.", "SUCCESS")
                    st.success("Admin password successfully updated!")

    with col_set2:
        st.markdown(
            clean_html("""
            <div class="tiq-card">
                <div class="tiq-card-accent-top"></div>
                <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; margin-bottom: 12px;">
                    ⚙️ Platform Architecture Details
                </div>
                <table style="width: 100%; font-size: 0.82rem; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 8px 0; color: #94A3B8;">Database Engine</td>
                        <td style="padding: 8px 0; font-weight: 600; color: #FFFFFF; text-align: right;">SQLite (data/talentiq.db)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 8px 0; color: #94A3B8;">Hashing Algorithm</td>
                        <td style="padding: 8px 0; font-weight: 600; color: #FFFFFF; text-align: right;">Bcrypt (Blowfish, cost=12)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 8px 0; color: #94A3B8;">Authorization</td>
                        <td style="padding: 8px 0; font-weight: 600; color: #34D399; text-align: right;">Role-Based (User / Admin)</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 8px 0; color: #94A3B8;">Screening NLP</td>
                        <td style="padding: 8px 0; font-weight: 600; color: #38BDF8; text-align: right;">TF-IDF + Cosine Vectors</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.06);">
                        <td style="padding: 8px 0; color: #94A3B8;">Data Isolation</td>
                        <td style="padding: 8px 0; font-weight: 600; color: #FBBF24; text-align: right;">Per-Account Foreign Keys</td>
                    </tr>
                </table>
            </div>
            """),
            unsafe_allow_html=True
        )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        if st.button("🔒 Sign Out Administrator Session", key="admin_settings_signout", use_container_width=True):
            sign_out_user()
            st.rerun()

