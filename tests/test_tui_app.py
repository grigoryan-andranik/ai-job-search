import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from textual.widgets import Button, DataTable, Input, ListView, Static, TabbedContent

from job_search_tui.app import HelpScreen, JobSearchApp
from job_search_tui.workflows import WORKFLOWS


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
                await pilot.press("j", "j")
                self.assertEqual(str(app.query_one("#workflow-title", Static).content), "Prepare application")
                self.assertIn("Job URL", app.query_one("#workflow-arguments", Input).placeholder)

                await pilot.press("/")
                await pilot.press("j", "k", "h", "l", "g", "1", "2", "3", "?")
                self.assertEqual(app.query_one("#workflow-arguments", Input).value, "jkhlg123?")

                await pilot.press("escape")
                await pilot.press("shift+g")
                self.assertEqual(app.query_one("#workflow-list", ListView).index, len(WORKFLOWS) - 1)
                await pilot.press("l")
                self.assertEqual(app.query_one("#tables", TabbedContent).active, "applications-tab")
                await pilot.press("l")
                self.assertEqual(app.query_one("#tables", TabbedContent).active, "jobs-tab")
                await pilot.press("h")
                self.assertEqual(app.query_one("#tables", TabbedContent).active, "applications-tab")
                await pilot.press("2")
                self.assertEqual(app.query_one("#tables", TabbedContent).active, "jobs-tab")
                await pilot.press("3")
                self.assertEqual(app.query_one("#tables", TabbedContent).active, "output-tab")

    async def test_workflow_runs_inside_dashboard_and_keeps_session_for_replies(self):
        async def fake_run(_root, _workflow, _arguments, **callbacks):
            callbacks["on_session"]("session-1")
            callbacks["on_output"]("Workflow answer")
            return 0

        with tempfile.TemporaryDirectory() as directory:
            app = JobSearchApp(Path(directory))
            with patch("job_search_tui.app.run_workflow", new=AsyncMock(side_effect=fake_run)):
                async with app.run_test(size=(140, 44)) as pilot:
                    await pilot.press("ctrl+r")
                    await pilot.pause()
                    self.assertEqual(app.query_one("#tables", TabbedContent).active, "output-tab")
                    self.assertEqual(app.workflow_session_id, "session-1")
                    self.assertEqual(str(app.query_one("#run", Button).label), "Continue workflow")
                    self.assertIn("turn complete", str(app.query_one("#status-line", Static).content))

    async def test_enter_runs_highlighted_workflow_and_help_is_available(self):
        async def fake_run(_root, _workflow, _arguments, **_callbacks):
            return 0

        with tempfile.TemporaryDirectory() as directory:
            app = JobSearchApp(Path(directory))
            mocked_run = AsyncMock(side_effect=fake_run)
            with patch("job_search_tui.app.run_workflow", new=mocked_run):
                async with app.run_test(size=(100, 36)) as pilot:
                    await pilot.press("j", "enter")
                    await pilot.pause()
                    mocked_run.assert_awaited_once()
                    self.assertEqual(mocked_run.await_args.args[1], "rank")

                    await pilot.press("?")
                    self.assertIsInstance(app.screen, HelpScreen)
                    await pilot.press("escape")
                    self.assertNotIsInstance(app.screen, HelpScreen)


if __name__ == "__main__":
    unittest.main()
