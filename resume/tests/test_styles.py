"""
Unit tests for Styling & Design System helpers
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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


class TestStylesSystem(unittest.TestCase):

    def test_get_css(self):
        css = get_css()
        self.assertIsInstance(css, str)
        self.assertIn("<style>", css)
        self.assertIn("--color-primary", css)
        self.assertIn("tiq-kpi-card", css)

    def test_get_logo_svg(self):
        logo = get_logo_svg()
        self.assertIn("<svg", logo)
        self.assertIn("TalentIQ", logo)
        self.assertIn(".AI", logo)

    def test_render_header(self):
        header_html = render_header("Test Title", "Test Subtitle", "Beta")
        self.assertIn("Test Title", header_html)
        self.assertIn("Test Subtitle", header_html)
        self.assertIn("Beta", header_html)

    def test_render_hero(self):
        hero_html = render_hero()
        self.assertIn("Find the Right Talent, Faster.", hero_html)
        self.assertIn("tiq-hero", hero_html)

    def test_render_kpi_card(self):
        card = render_kpi_card("Total Resumes", "42", "+5%", subtitle="Active pool")
        self.assertIn("Total Resumes", card)
        self.assertIn("42", card)
        self.assertIn("+5%", card)

    def test_render_score_badge(self):
        high = render_score_badge(95.0)
        self.assertIn("High Match", high)
        self.assertIn("95.0%", high)

        med = render_score_badge(70.0)
        self.assertIn("Moderate Match", med)

        low = render_score_badge(40.0)
        self.assertIn("Low Alignment", low)

    def test_render_skill_badge(self):
        badge = render_skill_badge("Python", "tech")
        self.assertIn("Python", badge)
        self.assertIn("tiq-badge", badge)

    def test_render_empty_state(self):
        empty = render_empty_state(title="No Resumes", description="Upload resumes to begin.")
        self.assertIn("No Resumes", empty)
        self.assertIn("Upload resumes to begin.", empty)

    def test_render_evidence_card(self):
        ev = render_evidence_card("Matches 5 skills.", "Fast-track interview", 85.0)
        self.assertIn("Matches 5 skills.", ev)
        self.assertIn("Fast-track interview", ev)

    def test_render_staged_file_badge(self):
        badge = render_staged_file_badge("resume.pdf", 20480, "Ready")
        self.assertIn("resume.pdf", badge)
        self.assertIn("PDF", badge)
        self.assertIn("20.0 KB", badge)

    def test_clean_html(self):
        dirty = "  \n  <div>\n    <span>Hello</span>\n  </div>\n  "
        cleaned = clean_html(dirty)
        self.assertEqual(cleaned, "<div>\n<span>Hello</span>\n</div>")

    def test_render_shortlist_badge(self):
        shortlisted = render_shortlist_badge(True)
        self.assertIn("Shortlisted", shortlisted)
        not_shortlisted = render_shortlist_badge(False)
        self.assertIn("Standard Pool", not_shortlisted)

    def test_render_user_profile_pill(self):
        pill = render_user_profile_pill("Alex Recruiter", "Senior Talent Acquisition")
        self.assertIn("Alex Recruiter", pill)
        self.assertIn("Senior Talent Acquisition", pill)
        self.assertIn("AR", pill)

    def test_render_admin_header(self):
        admin_h = render_admin_header("System Operations", "Telemetry")
        self.assertIn("System Operations", admin_h)
        self.assertIn("Administrator Privileged Console", admin_h)

    def test_render_portal_card(self):
        card = render_portal_card("user", "User Portal", "Screening", ["Feature 1", "Feature 2"], "Candidate Suite")
        self.assertIn("User Portal", card)
        self.assertIn("Feature 1", card)
        self.assertIn("Candidate Suite", card)


if __name__ == "__main__":
    unittest.main()
