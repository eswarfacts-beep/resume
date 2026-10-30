import unittest
import html
from src.styles import render_kpi_card

class TestKPIRendering(unittest.TestCase):
    def test_kpi_card_output_has_no_leading_spaces_or_blank_lines(self):
        icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
        card_html = render_kpi_card(
            title="Total Candidates",
            value="12",
            subtitle="12 parsed profiles",
            icon=icon
        )
        # Check that there are no lines indented with 4+ spaces which trigger markdown code blocks
        for i, line in enumerate(card_html.splitlines()):
            if line.strip():
                # Line should not start with 4 spaces or tabs
                self.assertFalse(line.startswith("    "), f"Line {i} has 4-space indent causing Markdown code block: {line!r}")
                self.assertFalse(line.startswith("\t"), f"Line {i} has tab indent causing Markdown code block: {line!r}")

if __name__ == "__main__":
    unittest.main()

