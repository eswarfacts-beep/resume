import unittest
from src.styles import (
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

class TestAllStyleHelpersIndentation(unittest.TestCase):
    def check_no_markdown_codeblock_indents(self, name, html_str):
        # A line starting with 4 spaces or tabs triggers markdown code block
        for i, line in enumerate(html_str.splitlines()):
            if line.strip():
                self.assertFalse(
                    line.startswith("    ") or line.startswith("\t"),
                    f"[{name}] Line {i} has >=4 leading spaces or tab which triggers Markdown code block: {line!r}"
                )

    def test_all_helpers(self):
        self.check_no_markdown_codeblock_indents("render_header", render_header("Title", "Subtitle", "Badge"))
        self.check_no_markdown_codeblock_indents("render_hero", render_hero())
        self.check_no_markdown_codeblock_indents("render_kpi_card", render_kpi_card("Total", "10", subtitle="Sub"))
        self.check_no_markdown_codeblock_indents("render_score_badge", render_score_badge(85.0))
        self.check_no_markdown_codeblock_indents("render_skill_badge", render_skill_badge("Python", "tech"))
        self.check_no_markdown_codeblock_indents("render_empty_state", render_empty_state())
        self.check_no_markdown_codeblock_indents("render_progress_bar", render_progress_bar(50.0, "Progress"))
        self.check_no_markdown_codeblock_indents("render_evidence_card", render_evidence_card("Matches Python", "Recommend", 80))
        self.check_no_markdown_codeblock_indents("render_staged_file_badge", render_staged_file_badge("resume.pdf", 1024))
        self.check_no_markdown_codeblock_indents("render_shortlist_badge", render_shortlist_badge(True))
        self.check_no_markdown_codeblock_indents("render_user_profile_pill", render_user_profile_pill("Jane Doe", "Recruiter"))
        self.check_no_markdown_codeblock_indents("render_admin_header", render_admin_header("Admin Title", "Admin Subtitle"))
        self.check_no_markdown_codeblock_indents("render_portal_card", render_portal_card("user", "Title", "Subtitle", ["F1", "F2"]))

if __name__ == "__main__":
    unittest.main()

