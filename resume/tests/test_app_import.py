import unittest
import subprocess
import sys
import os

class TestAppStartupAndImports(unittest.TestCase):
    def test_import_from_external_cwd(self):
        resume_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        home_dir = os.path.expanduser("~")
        cmd = [
            sys.executable,
            "-c",
            f"import sys; sys.path.insert(0, {repr(resume_dir)}); import app; print('READY')"
        ]
        res = subprocess.run(cmd, cwd=home_dir, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Startup failed with error:\n{res.stderr}")
        self.assertIn("READY", res.stdout)

    def test_styles_module_exports_all(self):
        import src.styles as styles
        expected_symbols = [
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
        for sym in expected_symbols:
            self.assertTrue(hasattr(styles, sym), f"styles missing expected symbol: {sym}")

if __name__ == "__main__":
    unittest.main()

