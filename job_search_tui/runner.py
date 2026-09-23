"""Run canonical Codex workflows and stream their output into the TUI."""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .workflows import WORKFLOW_BY_NAME


class RunnerError(RuntimeError):
    """Raised when a workflow cannot be launched."""


OutputHandler = Callable[[str], None]
ProcessHandler = Callable[[asyncio.subprocess.Process], None]
SessionHandler = Callable[[str], None]


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


def build_codex_command(
    root: Path,
    prompt: str,
    disabled_mcps: tuple[str, ...] = (),
) -> list[str]:
    mcp_overrides = [
        option
        for name in disabled_mcps
        for option in ("-c", f"mcp_servers.{name}.enabled=false")
    ]
    return [
        "codex",
        "--search",
        *mcp_overrides,
        "exec",
        "--json",
        "--approve-for-me",
        "-C",
        str(root.resolve()),
        prompt,
    ]


def build_resume_command(
    root: Path,
    session_id: str,
    reply: str,
    disabled_mcps: tuple[str, ...] = (),
) -> list[str]:
    return [
        *build_codex_command(root, "", disabled_mcps)[:-1],
        "resume",
        session_id,
        reply,
    ]


def discover_unavailable_remote_mcps() -> tuple[str, ...]:
    """Find enabled remote MCP servers with no configured authentication."""
    try:
        completed = subprocess.run(
            ["codex", "mcp", "list", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        servers = json.loads(completed.stdout) if completed.returncode == 0 else []
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return ()

    unavailable: list[str] = []
    for server in servers:
        transport = server.get("transport", {})
        name = server.get("name", "")
        if (
            server.get("enabled")
            and transport.get("type") != "stdio"
            and server.get("auth_status") in {"unknown", "not_authenticated"}
            and not transport.get("bearer_token_env_var")
            and re.fullmatch(r"[A-Za-z0-9_-]+", name)
        ):
            unavailable.append(name)
    return tuple(unavailable)


def format_codex_event(line: str) -> str | None:
    """Turn one Codex JSONL event into concise, readable dashboard output."""
    stripped = line.strip()
    if not stripped:
        return None
    try:
        event: dict[str, Any] = json.loads(stripped)
    except (json.JSONDecodeError, TypeError):
        return stripped

    event_type = event.get("type", "event")
    if event_type == "thread.started":
        return f"Session {event.get('thread_id', 'started')}"
    if event_type in {"turn.started", "turn.completed"}:
        return "Working…" if event_type == "turn.started" else "Workflow response complete"
    if event_type in {"error", "turn.failed"}:
        error = event.get("error")
        if isinstance(error, dict):
            error = error.get("message") or error
        return f"Error: {error or event.get('message', 'Codex workflow failed')}"

    item = event.get("item")
    if not isinstance(item, dict):
        return None
    item_type = item.get("type")
    if item_type in {"agent_message", "reasoning"}:
        return item.get("text") or item.get("content")
    if item_type == "command_execution":
        command = item.get("command", "command")
        if event_type == "item.started":
            return f"$ {command}"
        output = str(item.get("aggregated_output", "")).rstrip()
        status = item.get("status", "completed")
        return "\n".join(part for part in (output, f"[{status}] $ {command}") if part)
    if item_type in {"mcp_tool_call", "web_search"}:
        name = item.get("name") or item.get("query") or item_type.replace("_", " ")
        status = item.get("status") or event_type.removeprefix("item.")
        return f"[{status}] {name}"
    return None


async def run_workflow(
    root: Path,
    workflow_name: str,
    arguments: str = "",
    *,
    on_output: OutputHandler,
    on_process: ProcessHandler | None = None,
    on_session: SessionHandler | None = None,
    session_id: str | None = None,
) -> int:
    """Run a workflow headlessly and stream readable events to ``on_output``."""
    if shutil.which("codex") is None:
        raise RunnerError("Codex CLI not found on PATH. Install it, sign in, then retry.")
    disabled_mcps = discover_unavailable_remote_mcps()
    if session_id:
        reply = arguments.strip()
        if not reply:
            raise RunnerError("Enter a reply before continuing the workflow.")
        command = build_resume_command(root, session_id, reply, disabled_mcps)
    else:
        command = build_codex_command(root, build_prompt(workflow_name, arguments), disabled_mcps)
    if disabled_mcps:
        on_output("Skipped unavailable MCP integrations: " + ", ".join(disabled_mcps))
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except OSError as exc:
        raise RunnerError(f"Could not launch Codex: {exc}") from exc
    if on_process is not None:
        on_process(process)
    if process.stdout is None:
        process.terminate()
        await process.wait()
        raise RunnerError("Codex did not provide an output stream.")
    async for raw_line in process.stdout:
        line = raw_line.decode(errors="replace")
        if on_session is not None:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                event = {}
            if event.get("type") == "thread.started" and event.get("thread_id"):
                on_session(event["thread_id"])
        rendered = format_codex_event(line)
        if rendered:
            on_output(rendered)
    return await process.wait()
