import unittest
from pathlib import Path

from textual.widgets import DataTable, Input, Static

from job_search_tui.app import JobSearchApp


class AppTests(unittest.IsolatedAsyncioTestCase):
    async def test_dashboard_mounts_and_workflow_selection_updates_form(self):
        app = JobSearchApp(Path(__file__).resolve().parent.parent)
        async with app.run_test(size=(140, 44)) as pilot:
            self.assertGreater(app.query_one("#applications", DataTable).row_count, 0)
            self.assertEqual(str(app.query_one("#workflow-title", Static).content), "Search jobs")
            await pilot.press("down", "down")
            await pilot.press("enter")
            self.assertEqual(str(app.query_one("#workflow-title", Static).content), "Prepare application")
            self.assertIn("Job URL", app.query_one("#workflow-arguments", Input).placeholder)


if __name__ == "__main__":
    unittest.main()

