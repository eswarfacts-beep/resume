import unittest
import html

def clean_html(html_str: str) -> str:
    if not html_str:
        return ""
    lines = [line.strip() for line in str(html_str).splitlines() if line.strip()]
    return "\n".join(lines)

class TestCleanHTML(unittest.TestCase):
    def test_clean_html_removes_all_indentation_and_blank_lines(self):
        sample = """
        <div class="tiq-kpi-card">
            <div class="tiq-kpi-label">
                <span>Total Candidates</span>
                <span style="display: flex;">
                    
                    <svg width="18" height="18"><circle cx="12" cy="12" r="10"/></svg>
                </span>
            </div>
            <div class="tiq-kpi-val">12</div>
            <div class="tiq-kpi-sub">Profiles</div>
        </div>
        """
        cleaned = clean_html(sample)
        for i, line in enumerate(cleaned.splitlines()):
            self.assertFalse(line.startswith(" "), f"Line {i} starts with space: {line!r}")
            self.assertFalse(line.startswith("\t"), f"Line {i} starts with tab: {line!r}")
            self.assertTrue(len(line) > 0, f"Line {i} is empty")

if __name__ == "__main__":
    unittest.main()

