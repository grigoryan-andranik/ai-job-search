"""Command-line entry point for the job-search TUI."""

from __future__ import annotations

import argparse
from pathlib import Path

from .app import JobSearchApp
from .runner import RunnerError, find_repo_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Open the AI Job Search terminal dashboard.")
    parser.add_argument(
        "--repo",
        type=Path,
        help="Repository root. Defaults to the nearest parent containing CODEX.md.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        root = find_repo_root(args.repo.resolve() if args.repo else Path.cwd())
    except RunnerError as exc:
        parser.error(str(exc))
    JobSearchApp(root).run()


if __name__ == "__main__":
    main()
