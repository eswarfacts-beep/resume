"""
TalentIQ AI - Shared Styling & Design System
Commercial-grade SaaS design system for Streamlit.
Colors: Deep navy, royal blue, electric indigo, violet, and subtle cyan accents.
"""

import html

__all__ = [
    "clean_html",
    "get_css",
    "get_logo_svg",
    "render_header",
    "render_hero",
    "render_kpi_card",
    "render_score_badge",
    "render_skill_badge",
    "render_empty_state",
    "render_progress_bar",
    "render_evidence_card",
    "render_staged_file_badge",
    "render_shortlist_badge",
    "render_user_profile_pill",
    "render_admin_header",
    "render_portal_card",
]


def clean_html(html_str: str) -> str:
    """Strips leading/trailing whitespace from each line and removes empty lines,
    ensuring Markdown/CommonMark parsers never treat HTML tags or indented blocks
    as markdown code blocks (<pre><code>).
    """
    if not html_str:
        return ""
    lines = [line.strip() for line in str(html_str).splitlines() if line.strip()]
    return "\n".join(lines)


def get_logo_svg(width: int = 40, height: int = 40, show_text: bool = True) -> str:
    """Returns an inline SVG logo for TalentIQ AI with neural node optics."""
    text_part = (
        "<div>"
        "<span style='font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(135deg, #FFFFFF 30%, #C7D2FE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>TalentIQ</span>"
        "<span style='font-size: 1.35rem; font-weight: 800; color: #06B6D4;'>.AI</span>"
        "<div style='font-size: 0.68rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; color: #818CF8;'>Autonomous Talent Intelligence</div>"
        "</div>"
    ) if show_text else ""

    svg_icon = (
        f'<svg width="{width}" height="{height}" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="tiq-grad-primary" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#4F46E5"/><stop offset="50%" stop-color="#7C3AED"/><stop offset="100%" stop-color="#06B6D4"/></linearGradient>'
        f'<linearGradient id="tiq-grad-glow" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#2563EB" stop-opacity="0.8"/><stop offset="100%" stop-color="#06B6D4" stop-opacity="0.2"/></linearGradient>'
        f'<filter id="tiq-glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="blur"/><feComposite in="SourceGraphic" in2="blur" operator="over"/></filter>'
        f'</defs>'
        f'<rect x="4" y="4" width="40" height="40" rx="12" fill="#0F172A" stroke="url(#tiq-grad-primary)" stroke-width="2"/>'
        f'<circle cx="24" cy="24" r="8" fill="url(#tiq-grad-primary)" filter="url(#tiq-glow)"/>'
        f'<circle cx="14" cy="18" r="2.5" fill="#22D3EE"/>'
        f'<circle cx="34" cy="18" r="2.5" fill="#818CF8"/>'
        f'<circle cx="24" cy="36" r="2.5" fill="#A78BFA"/>'
        f'<path d="M14 18L24 24M34 18L24 24M24 36L24 24" stroke="rgba(255, 255, 255, 0.4)" stroke-width="1.5" stroke-linecap="round"/>'
        f'<circle cx="24" cy="24" r="3.5" fill="#FFFFFF"/>'
        f'</svg>'
    )

    logo_html = (
        f'<div style="display: inline-flex; align-items: center; gap: 12px; font-family: \'Plus Jakarta Sans\', \'Inter\', -apple-system, sans-serif;">'
        f'{svg_icon}'
        f'{text_part}'
        f'</div>'
    )
    return clean_html(logo_html)


def get_css() -> str:
    """Returns the master CSS stylesheet for TalentIQ AI."""
    return """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --color-bg-main: #0A0F1D;
        --color-bg-card: #0F172A;
        --color-bg-elevated: #162035;
        --color-border: rgba(255, 255, 255, 0.08);
        --color-border-glow: rgba(79, 70, 229, 0.35);
        --color-primary: #4F46E5;
        --color-primary-light: #6366F1;
        --color-royal: #2563EB;
        --color-violet: #7C3AED;
        --color-cyan: #06B6D4;
        --color-cyan-glow: rgba(6, 182, 212, 0.3);
        --color-text-main: #F8FAFC;
        --color-text-secondary: #94A3B8;
        --color-text-muted: #64748B;
        --color-success: #10B981;
        --color-warning: #F59E0B;
        --color-danger: #EF4444;
        --radius-sm: 8px;
        --radius-md: 14px;
        --radius-lg: 20px;
        --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 25px rgba(79, 70, 229, 0.25);
    }

    /* Core Document Styling */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--color-text-main);
        background-color: var(--color-bg-main);
    }

    /* Streamlit App Container */
    .stApp {
        background-color: var(--color-bg-main);
        background-image:
            radial-gradient(ellipse at 50% 0%, rgba(79, 70, 229, 0.12) 0%, rgba(10, 15, 29, 0) 65%),
            radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.06) 0%, rgba(10, 15, 29, 0) 50%);
        background-attachment: fixed;
    }

    /* Remove excessive top padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1240px;
    }

    /* Top Navigation / App Header */
    header[data-testid="stHeader"] {
        background: rgba(10, 15, 29, 0.75) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid var(--color-border) !important;
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: #0B1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem !important;
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }

    /* Custom Radio Buttons as Clean Nav Tabs */
    div[data-testid="stRadio"] > div {
        background: transparent;
        gap: 6px;
    }

    div[data-testid="stRadio"] label {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid transparent;
        padding: 9px 14px;
        border-radius: var(--radius-sm);
        transition: all 0.2s ease;
        cursor: pointer;
        color: var(--color-text-secondary);
        font-weight: 500;
        font-size: 0.92rem;
    }

    div[data-testid="stRadio"] label:hover {
        background: rgba(79, 70, 229, 0.12);
        color: #FFFFFF;
        border-color: rgba(79, 70, 229, 0.25);
    }

    div[data-testid="stRadio"] label[data-checked="true"] {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.25) 0%, rgba(37, 99, 235, 0.2) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.45) !important;
        color: #FFFFFF !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }

    /* Buttons Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #2563EB 100%);
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        padding: 0.65rem 1.4rem;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.01em;
        font-size: 0.92rem;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #6366F1 0%, #3B82F6 100%);
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
        transform: translateY(-1px);
    }

    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* Secondary Action Button (when using secondary type) */
    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #CBD5E1 !important;
        box-shadow: none !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.25) !important;
        color: #FFFFFF !important;
    }

    /* Form Inputs & Text Areas */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: var(--color-bg-card) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-sm) !important;
        transition: all 0.2s ease;
    }

    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: var(--color-primary-light) !important;
        box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.25) !important;
    }

    /* File Uploader Custom Styling */
    div[data-testid="stFileUploader"] {
        background: rgba(15, 23, 42, 0.6);
        border: 2px dashed rgba(79, 70, 229, 0.35);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        transition: all 0.2s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: var(--color-cyan);
        background: rgba(15, 23, 42, 0.85);
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.15);
    }

    /* Custom Modern Cards */
    .tiq-card {
        background: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: 1.4rem;
        box-shadow: var(--shadow-card);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }

    .tiq-card:hover {
        border-color: var(--color-border-glow);
        transform: translateY(-2px);
        box-shadow: 0 14px 30px -8px rgba(0, 0, 0, 0.5), 0 0 15px rgba(79, 70, 229, 0.15);
    }

    .tiq-card-accent-top {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4F46E5, #7C3AED, #06B6D4);
    }

    /* KPI Cards */
    .tiq-kpi-card {
        background: linear-gradient(180deg, rgba(22, 32, 53, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }

    .tiq-kpi-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }

    .tiq-kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--color-text-secondary);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .tiq-kpi-val {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #FFFFFF;
        margin: 0.35rem 0 0.2rem 0;
        line-height: 1.1;
    }

    .tiq-kpi-sub {
        font-size: 0.78rem;
        color: var(--color-text-muted);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Hero Section */
    .tiq-hero {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(30, 27, 75, 0.4) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 2.2rem 2.4rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .tiq-hero::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.18) 0%, rgba(79, 70, 229, 0) 70%);
        pointer-events: none;
    }

    .tiq-hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(79, 70, 229, 0.18);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #A5B4FC;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 4px 12px;
        border-radius: 9999px;
        margin-bottom: 1rem;
    }

    .tiq-hero-title {
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 20%, #E2E8F0 60%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.75rem;
    }

    .tiq-hero-desc {
        font-size: 1.05rem;
        color: #94A3B8;
        max-width: 680px;
        line-height: 1.55;
        margin-bottom: 1.5rem;
    }

    /* Skill Badges */
    .tiq-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin: 2px 4px 2px 0;
        transition: all 0.15s ease;
    }

    .tiq-badge-tech {
        background: rgba(37, 99, 235, 0.15);
        color: #93C5FD;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .tiq-badge-violet {
        background: rgba(124, 58, 237, 0.15);
        color: #C4B5FD;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    .tiq-badge-cyan {
        background: rgba(6, 182, 212, 0.15);
        color: #67E8F9;
        border: 1px solid rgba(6, 182, 212, 0.3);
    }

    .tiq-badge-soft {
        background: rgba(16, 185, 129, 0.15);
        color: #6EE7B7;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .tiq-badge-missing {
        background: rgba(239, 68, 68, 0.12);
        color: #FCA5A5;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Match Score Badges */
    .tiq-score-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .tiq-score-high {
        background: rgba(16, 185, 129, 0.16);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .tiq-score-med {
        background: rgba(245, 158, 11, 0.16);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .tiq-score-low {
        background: rgba(239, 68, 68, 0.16);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Empty State Container */
    .tiq-empty-state {
        background: rgba(15, 23, 42, 0.5);
        border: 1px dashed rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }

    .tiq-empty-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F1F5F9;
        margin-top: 1rem;
        margin-bottom: 0.4rem;
    }

    .tiq-empty-desc {
        font-size: 0.9rem;
        color: #94A3B8;
        max-width: 440px;
        margin: 0 auto 1.25rem auto;
        line-height: 1.5;
    }

    /* Candidate Detail Card */
    .tiq-candidate-item {
        background: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: 12px;
        padding: 1.15rem 1.3rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }

    .tiq-candidate-item:hover {
        background: rgba(22, 32, 53, 0.9);
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateX(3px);
    }

    /* Glassmorphic Login Container */
    .tiq-login-card {
        background: linear-gradient(135deg, rgba(22, 32, 53, 0.9) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 30px rgba(79, 70, 229, 0.2);
        max-width: 520px;
        margin: 1.5rem auto;
    }

    /* Recruiter User Profile Card */
    .tiq-user-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-bottom: 14px;
        transition: all 0.2s ease;
    }

    .tiq-user-pill:hover {
        background: rgba(79, 70, 229, 0.12);
        border-color: rgba(99, 102, 241, 0.3);
    }

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .tiq-hero {
            padding: 1.5rem;
        }
        .tiq-hero-title {
            font-size: 1.75rem;
        }
        .tiq-kpi-val {
            font-size: 1.75rem;
        }
        .tiq-login-card {
            padding: 1.5rem;
            margin: 0.5rem auto;
        }
    }

    /* Portal Selection Cards on Landing Page */
    .tiq-portal-card {
        background: linear-gradient(180deg, rgba(22, 32, 53, 0.85) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(255, 255, 255, 0.09);
        border-radius: 18px;
        padding: 2.2rem 2rem;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .tiq-portal-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 36px -10px rgba(0, 0, 0, 0.65);
    }
    .tiq-portal-user:hover {
        border-color: rgba(6, 182, 212, 0.55);
        box-shadow: 0 0 30px rgba(6, 182, 212, 0.22);
    }
    .tiq-portal-admin:hover {
        border-color: rgba(239, 68, 68, 0.55);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.22);
    }
    .tiq-admin-banner {
        background: linear-gradient(90deg, rgba(124, 58, 237, 0.2) 0%, rgba(239, 68, 68, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 10px;
        padding: 8px 16px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: #FCA5A5;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    </style>
    """


def render_header(title: str, subtitle: str = None, badge: str = None) -> str:
    """Renders a modern page header with optional badge and subtitle."""
    badge_html = f'<span class="tiq-hero-badge" style="margin-bottom: 0.5rem;">{html.escape(badge)}</span>' if badge else ""
    sub_html = f'<div style="font-size: 0.95rem; color: #94A3B8; margin-top: 0.25rem;">{html.escape(subtitle)}</div>' if subtitle else ""
    header_html = (
        f'<div style="margin-bottom: 1.6rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255, 255, 255, 0.06);">'
        f'{badge_html}'
        f'<h1 style="font-size: 1.85rem; font-weight: 800; letter-spacing: -0.025em; margin: 0; color: #FFFFFF;">'
        f'{html.escape(title)}'
        f'</h1>'
        f'{sub_html}'
        f'</div>'
    )
    return clean_html(header_html)


def render_hero(
    title: str = "Find the Right Talent, Faster.",
    subtitle: str = "Automate resume screening, extract skills, and rank candidate-job alignment using enterprise-grade semantic matching and contextual AI.",
    badge_text: str = "AI-Powered Talent Matching v2.5"
) -> str:
    """Renders the visually impressive SaaS Hero section."""
    hero_html = (
        f'<div class="tiq-hero">'
        f'<div class="tiq-hero-badge">'
        f'<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
        f'<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
        f'</svg>'
        f'{html.escape(badge_text)}'
        f'</div>'
        f'<div class="tiq-hero-title">{html.escape(title)}</div>'
        f'<div class="tiq-hero-desc">{html.escape(subtitle)}</div>'
        f'<div style="display: flex; gap: 16px; flex-wrap: wrap; margin-top: 0.5rem;">'
        f'<div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #CBD5E1;">'
        f'<span style="color: #34D399; font-weight: bold;">✓</span> Multi-Format (PDF &amp; DOCX)'
        f'</div>'
        f'<div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #CBD5E1;">'
        f'<span style="color: #38BDF8; font-weight: bold;">✓</span> 300+ Tech Skill Ontology'
        f'</div>'
        f'<div style="display: flex; align-items: center; gap: 8px; font-size: 0.82rem; color: #CBD5E1;">'
        f'<span style="color: #A78BFA; font-weight: bold;">✓</span> Semantic TF-IDF &amp; Cosine AI'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    return clean_html(hero_html)


def render_kpi_card(
    title: str,
    value: str,
    delta: str = None,
    icon: str = None,
    subtitle: str = None,
    glow_color: str = "indigo"
) -> str:
    """Renders a professional KPI card with real data."""
    delta_html = ""
    if delta:
        color = "#34D399" if not str(delta).startswith("-") else "#F87171"
        delta_html = f'<span style="font-size: 0.74rem; font-weight: 700; color: {color}; margin-right: 6px;">{html.escape(str(delta))}</span>'

    default_icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818CF8" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
    icon_svg = (icon.strip() if icon else default_icon)

    sub_html = f'<div class="tiq-kpi-sub">{html.escape(str(subtitle))}</div>' if subtitle else ""
    badge_right = f'<span style="display: flex; align-items: center; gap: 4px;">{delta_html}{icon_svg}</span>'

    card_html = (
        f'<div class="tiq-kpi-card">'
        f'<div class="tiq-kpi-label">'
        f'<span>{html.escape(str(title))}</span>'
        f'{badge_right}'
        f'</div>'
        f'<div class="tiq-kpi-val">{html.escape(str(value))}</div>'
        f'{sub_html}'
        f'</div>'
    )
    return clean_html(card_html)


def render_score_badge(score: float, size: str = "normal") -> str:
    """Returns an HTML score pill badge with color-coded confidence."""
    if score >= 80:
        cls = "tiq-score-high"
        label = "High Match"
        icon = "●"
    elif score >= 60:
        cls = "tiq-score-med"
        label = "Moderate Match"
        icon = "●"
    else:
        cls = "tiq-score-low"
        label = "Low Alignment"
        icon = "○"

    font_size = "0.78rem" if size == "small" else "0.85rem"
    badge_html = f'<span class="tiq-score-badge {cls}" style="font-size: {font_size};"><span>{icon}</span> {score:.1f}% &middot; {label}</span>'
    return clean_html(badge_html)


def render_skill_badge(skill: str, category: str = "tech") -> str:
    """Renders a styled skill badge."""
    cat_class_map = {
        "tech": "tiq-badge-tech",
        "cloud": "tiq-badge-cyan",
        "soft": "tiq-badge-soft",
        "ai": "tiq-badge-violet",
        "missing": "tiq-badge-missing"
    }
    cls = cat_class_map.get(category, "tiq-badge-tech")
    return f'<span class="tiq-badge {cls}">{html.escape(skill)}</span>'


def render_empty_state(
    icon: str = None,
    title: str = "No Data Found",
    description: str = "Upload resumes or choose a sample job to begin intelligent matching.",
    action_text: str = None
) -> str:
    """Renders a clean, polished empty state."""
    default_icon = (
        '<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.5">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
        '<polyline points="14 2 14 8 20 8"></polyline>'
        '<line x1="16" y1="13" x2="8" y2="13"></line>'
        '<line x1="16" y1="17" x2="8" y2="17"></line>'
        '<polyline points="10 9 9 9 8 9"></polyline>'
        '</svg>'
    )
    icon_svg = (icon.strip() if icon else default_icon)
    action_html = f'<div style="font-size: 0.8rem; font-weight: 600; color: #818CF8; margin-top: 0.5rem;">{html.escape(action_text)}</div>' if action_text else ""

    state_html = (
        f'<div class="tiq-empty-state">'
        f'<div style="display: inline-flex; padding: 14px; background: rgba(79, 70, 229, 0.1); border-radius: 50%;">'
        f'{icon_svg}'
        f'</div>'
        f'<div class="tiq-empty-title">{html.escape(title)}</div>'
        f'<div class="tiq-empty-desc">{html.escape(description)}</div>'
        f'{action_html}'
        f'</div>'
    )
    return clean_html(state_html)


def render_progress_bar(percentage: float, label: str = None, color: str = "#4F46E5") -> str:
    """Renders an SVG/HTML progress bar with gradient."""
    pct = max(0.0, min(100.0, percentage))
    label_html = f'<div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: #94A3B8; margin-bottom: 4px;"><span>{html.escape(label)}</span><span>{pct:.1f}%</span></div>' if label else ""
    bar_html = (
        f'<div style="margin: 6px 0;">'
        f'{label_html}'
        f'<div style="width: 100%; height: 8px; background: rgba(255, 255, 255, 0.08); border-radius: 9999px; overflow: hidden;">'
        f'<div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, {color}, #06B6D4); border-radius: 9999px; transition: width 0.4s ease;"></div>'
        f'</div>'
        f'</div>'
    )
    return clean_html(bar_html)



def render_evidence_card(evidence_text: str, recommendation: str = "", score: float = 0.0) -> str:
    """Renders a glowing match evidence card explaining why candidate matched."""
    rec_html = f'<div style="font-size: 0.84rem; font-weight: 700; color: #34D399; margin-bottom: 6px;">🎯 Recruiter Recommendation: {html.escape(recommendation)}</div>' if recommendation else ""
    card_html = (
        f'<div style="background: rgba(79, 70, 229, 0.08); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 12px; padding: 14px 18px; margin: 10px 0;">'
        f'<div style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #818CF8; margin-bottom: 6px;">'
        f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'
        f'AI Match Evidence &amp; Context'
        f'</div>'
        f'{rec_html}'
        f'<div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.55;">'
        f'{html.escape(evidence_text)}'
        f'</div>'
        f'</div>'
    )
    return clean_html(card_html)


def render_staged_file_badge(filename: str, size_bytes: int, status: str = "Ready to screen") -> str:
    """Renders a visual indicator for an uploaded or staged resume file."""
    ext = filename.split(".")[-1].upper() if "." in filename else "FILE"
    kb = size_bytes / 1024 if size_bytes else 0
    color_map = {"PDF": "#F87171", "DOCX": "#60A5FA", "TXT": "#34D399"}
    badge_bg = color_map.get(ext, "#818CF8")
    status_color = "#34D399" if "indexed" in status.lower() or "ready" in status.lower() else "#FBBF24"

    badge_html = (
        f'<div style="display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">'
        f'<div style="display: flex; align-items: center; gap: 10px;">'
        f'<span style="background: {badge_bg}; color: #0F172A; font-weight: 800; font-size: 0.68rem; padding: 2px 6px; border-radius: 4px;">{ext}</span>'
        f'<span style="font-size: 0.86rem; font-weight: 600; color: #FFFFFF;">{html.escape(filename)}</span>'
        f'<span style="font-size: 0.76rem; color: #64748B;">({kb:.1f} KB)</span>'
        f'</div>'
        f'<span style="font-size: 0.76rem; font-weight: 600; color: {status_color};">{html.escape(status)}</span>'
        f'</div>'
    )
    return clean_html(badge_html)


def render_shortlist_badge(is_shortlisted: bool) -> str:
    """Renders a star badge indicator for shortlist status."""
    if is_shortlisted:
        return '<span style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.35); font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px;">★ Shortlisted</span>'
    return '<span style="background: rgba(148, 163, 184, 0.08); color: #94A3B8; border: 1px solid rgba(148, 163, 184, 0.2); font-size: 0.72rem; font-weight: 500; padding: 2px 8px; border-radius: 9999px;">Standard Pool</span>'


def render_user_profile_pill(name: str, role: str, email: str = "") -> str:
    """Renders the recruiter profile indicator for the sidebar."""
    initials = "".join([part[0] for part in name.split() if part])[:2].upper() if name else "US"
    pill_html = (
        f'<div class="tiq-user-pill">'
        f'<div style="background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%); width: 34px; height: 34px; border-radius: 9999px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.84rem; color: #FFFFFF; flex-shrink: 0;">'
        f'{initials}'
        f'</div>'
        f'<div style="overflow: hidden;">'
        f'<div style="font-size: 0.86rem; font-weight: 700; color: #FFFFFF; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">'
        f'{html.escape(name)}'
        f'</div>'
        f'<div style="font-size: 0.72rem; color: #94A3B8; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">'
        f'{html.escape(role)} &middot; <span style="color: #34D399;">Active</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    return clean_html(pill_html)


def render_admin_header(title: str, subtitle: str = None) -> str:
    """Renders a distinguished header for the Admin Privileged Console."""
    sub_html = f'<div style="font-size: 0.92rem; color: #94A3B8; margin-top: 0.35rem;">{html.escape(subtitle)}</div>' if subtitle else ""
    header_html = (
        f'<div style="margin-bottom: 1.6rem; padding-bottom: 1.2rem; border-bottom: 1px solid rgba(239, 68, 68, 0.2);">'
        f'<div style="margin-bottom: 0.6rem;">'
        f'<span class="tiq-admin-banner">'
        f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
        f'Administrator Privileged Console'
        f'</span>'
        f'</div>'
        f'<h1 style="font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; margin: 0; color: #FFFFFF;">'
        f'{html.escape(title)}'
        f'</h1>'
        f'{sub_html}'
        f'</div>'
    )
    return clean_html(header_html)


def render_portal_card(portal_type: str, title: str, subtitle: str, features: list, badge_text: str = "") -> str:
    """Renders a styled interactive portal card for the landing page."""
    is_admin = portal_type.lower() == "admin"
    card_cls = "tiq-portal-admin" if is_admin else "tiq-portal-user"
    accent_color = "#EF4444" if is_admin else "#06B6D4"
    bg_gradient = "linear-gradient(135deg, #7C3AED 0%, #EF4444 100%)" if is_admin else "linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%)"
    
    icon_svg = (
        '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#FCA5A5" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
        if is_admin else
        '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#67E8F9" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>'
    )
    
    items_html = "".join([
        f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 0.86rem; color: #CBD5E1;">'
        f'<span style="color: {accent_color}; font-weight: bold;">✓</span> {html.escape(feat)}'
        f'</div>'
        for feat in features
    ])

    badge_html = f'<div style="display: inline-block; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 10px; border-radius: 9999px; background: rgba(255, 255, 255, 0.08); color: {accent_color}; margin-bottom: 12px;">{html.escape(badge_text)}</div>' if badge_text else ""

    card_html = (
        f'<div class="tiq-portal-card {card_cls}">'
        f'<div>'
        f'{badge_html}'
        f'<div style="width: 52px; height: 52px; border-radius: 14px; background: {bg_gradient}; display: flex; align-items: center; justify-content: center; margin-bottom: 18px; box-shadow: 0 8px 20px -4px rgba(0,0,0,0.5);">'
        f'{icon_svg}'
        f'</div>'
        f'<h3 style="font-size: 1.45rem; font-weight: 800; color: #FFFFFF; margin: 0 0 8px 0; letter-spacing: -0.02em;">{html.escape(title)}</h3>'
        f'<p style="font-size: 0.9rem; color: #94A3B8; margin-bottom: 20px; line-height: 1.5;">{html.escape(subtitle)}</p>'
        f'<div style="border-top: 1px solid rgba(255, 255, 255, 0.06); padding-top: 16px; margin-bottom: 20px;">'
        f'{items_html}'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    return clean_html(card_html)



