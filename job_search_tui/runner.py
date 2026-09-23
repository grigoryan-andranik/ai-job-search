"""Launch canonical Codex workflows in an interactive terminal session."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .workflows import WORKFLOW_BY_NAME


class RunnerError(RuntimeError):
    """Raised when a workflow cannot be launched."""


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "CODEX.md").is_file() and (candidate / ".agents" / "skills").is_dir():
            return candidate
    raise RunnerError("Repository root not found. Run inside ai-job-search or pass --repo.")


def build_prompt(workflow_name: str, arguments: str = "") -> str:
    if workflow_name not in WORKFLOW_BY_NAME:
        raise RunnerError(f"Unknown workflow: {workflow_name}")
    clean_arguments = arguments.strip()
    return f"${workflow_name}" + (f" {clean_arguments}" if clean_arguments else "")


def build_codex_command(root: Path, prompt: str) -> list[str]:
    return ["codex", "--search", "-C", str(root.resolve()), prompt]


def run_workflow(root: Path, workflow_name: str, arguments: str = "") -> int:
    if shutil.which("codex") is None:
        raise RunnerError("Codex CLI not found on PATH. Install it, sign in, then retry.")
    prompt = build_prompt(workflow_name, arguments)
    command = build_codex_command(root, prompt)
    try:
        completed = subprocess.run(command, cwd=root, check=False)
    except OSError as exc:
        raise RunnerError(f"Could not launch Codex: {exc}") from exc
    return completed.returncode

