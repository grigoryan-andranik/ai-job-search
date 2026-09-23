import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from job_search_tui.runner import (
    RunnerError,
    build_codex_command,
    build_prompt,
    find_repo_root,
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
        self.assertEqual(command, ["codex", "--search", "-C", "/tmp/repo", "$scrape"])

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

    @patch("job_search_tui.runner.subprocess.run")
    @patch("job_search_tui.runner.shutil.which", return_value="/usr/bin/codex")
    def test_run_workflow_inherits_terminal_and_returns_status(self, _which, run):
        run.return_value.returncode = 7
        root = Path("/tmp/repo")
        self.assertEqual(run_workflow(root, "rank"), 7)
        run.assert_called_once_with(
            ["codex", "--search", "-C", "/tmp/repo", "$rank"],
            cwd=root,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
