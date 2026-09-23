import tempfile
import unittest
from pathlib import Path

from textual.widgets import DataTable, Input, Static

from job_search_tui.app import JobSearchApp


class AppTests(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_mounts_and_workflow_selection_updates_form(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "job_search_tracker.csv").write_text(
                "date,company,role,status,fit_rating,deadline,source,notes\n"
                "2026-01-01,Example,Platform Engineer,applied,88,,,\n",
                encoding="utf-8",
            )
            app = JobSearchApp(root)
            async with app.run_test(size=(140, 44)) as pilot:
                self.assertEqual(app.query_one("#applications", DataTable).row_count, 1)
                self.assertEqual(str(app.query_one("#workflow-title", Static).content), "Search jobs")
                await pilot.press("down", "down")
                await pilot.press("enter")
                self.assertEqual(str(app.query_one("#workflow-title", Static).content), "Prepare application")
                self.assertIn("Job URL", app.query_one("#workflow-arguments", Input).placeholder)


if __name__ == "__main__":
    unittest.main()
