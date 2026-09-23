import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from job_search_tui.runner import (
    RunnerError,
    build_codex_command,
    build_prompt,
    build_resume_command,
    find_repo_root,
    format_codex_event,
    run_workflow,
)


class RunnerTests(unittest.TestCase):
    def test_builds_skill_prompt_without_shell_quoting(self):
        self.assertEqual(build_prompt("apply", " https://example.com/job?a=1 "), "$apply https://example.com/job?a=1")

    def test_rejects_unknown_workflow(self):
        with self.assertRaisesRegex(RunnerError, "Unknown workflow"):
            build_prompt("delete-everything")

    def test_codex_command_uses_repo_and_web_search(self):
        command = build_codex_command(Path("/tmp/repo"), "$scrape")
        self.assertEqual(
            command,
            [
                "codex",
                "--search",
                "exec",
                "--json",
                "--approve-for-me",
                "--sandbox",
                "workspace-write",
                "-C",
                "/tmp/repo",
                "$scrape",
            ],
        )

    def test_formats_agent_and_command_events(self):
        self.assertEqual(
            format_codex_event('{"type":"item.completed","item":{"type":"agent_message","text":"Done"}}'),
            "Done",
        )
        rendered = format_codex_event(
            '{"type":"item.completed","item":{"type":"command_execution",'
            '"command":"make test","aggregated_output":"ok\\n","status":"completed"}}'
        )
        self.assertEqual(rendered, "ok\n[completed] $ make test")

    def test_resume_command_keeps_workflow_inside_existing_session(self):
        command = build_resume_command(Path("/tmp/repo"), "session-1", "yes, continue")
        self.assertEqual(command[-3:], ["resume", "session-1", "yes, continue"])
        self.assertIn("--json", command)

    def test_finds_repository_from_nested_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CODEX.md").touch()
            (root / ".agents" / "skills").mkdir(parents=True)
            nested = root / "one" / "two"
            nested.mkdir(parents=True)
            self.assertEqual(find_repo_root(nested), root.resolve())

    def test_missing_repository_has_actionable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RunnerError, "pass --repo"):
                find_repo_root(Path(directory))


class AsyncRunnerTests(unittest.IsolatedAsyncioTestCase):
    @patch("job_search_tui.runner.asyncio.create_subprocess_exec", new_callable=AsyncMock)
    @patch("job_search_tui.runner.shutil.which", return_value="/usr/bin/codex")
    async def test_run_workflow_streams_output_and_returns_status(self, _which, create_process):
        class Output:
            def __init__(self):
                self.lines = iter(
                    [b'{"type":"item.completed","item":{"type":"agent_message","text":"Done"}}\n']
                )

            def __aiter__(self):
                return self

            async def __anext__(self):
                try:
                    return next(self.lines)
                except StopIteration as exc:
                    raise StopAsyncIteration from exc

        class Process:
            stdout = Output()

            async def wait(self):
                return 7

        create_process.return_value = Process()
        messages: list[str] = []
        root = Path("/tmp/repo")
        self.assertEqual(
            await run_workflow(root, "rank", on_output=messages.append),
            7,
        )
        self.assertEqual(messages, ["Done"])
        create_process.assert_awaited_once_with(
            "codex",
            "--search",
            "exec",
            "--json",
            "--approve-for-me",
            "--sandbox",
            "workspace-write",
            "-C",
            "/tmp/repo",
            "$rank",
            cwd=root,
            stdout=-1,
            stderr=-2,
        )


if __name__ == "__main__":
    unittest.main()
