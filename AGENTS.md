---
framework_version: 1.1.0
---

# Agent Guidelines: AI Job Search

This workspace is structured to manage job search activities, scraper tools, CVs, cover letters, and interview preparation.

## Thin-Pointer Design (Single Source of Truth)

To prevent duplication and configuration drift across different AI agent frameworks (Claude Code, Google Antigravity, Codex, Cursor, Gemini CLI, etc.), this workspace uses a unified thin-pointer design. All agent runtimes should load the canonical specifications and candidate profiles from the files and directories below:

1. **Personal Candidate Profile:**
   - The candidate profile, contact details, education, and target preferences are defined in [CLAUDE.md](CLAUDE.md) and the individual profile methodology files under [.claude/skills/job-application-assistant/](.claude/skills/job-application-assistant/) (specifically `01-*.md` etc.).
2. **Canonical Workflow Specifications:**
   - The step-by-step instructions and triggers for tasks (setup, scrape, rank, apply, upskill, interview) are defined in the [.claude/](.claude/) directory (specifically under `.claude/skills/` and `.claude/commands/`).
   - Do not duplicate these rules or specifications. Treat `.claude/` files as the single source of truth.
3. **Portal Search Skills:**
   - Job-portal search CLIs live under [.agents/skills/](.agents/skills/) in the portable Agent Skills format (with a `SKILL.md` per portal). Codex and Antigravity discover these automatically; the `/scrape` workflow in [.claude/skills/job-scraper/](.claude/skills/job-scraper/) orchestrates them.

## Codex Runtime

Before executing a job-search workflow, read [CODEX.md](CODEX.md) for tool and path mappings, then read `CLAUDE.md` for the candidate profile and verification requirements. The `.claude/` directory is shared workflow data; its name does not require running Claude.

Codex entry points live in `.agents/skills/`. Use `$setup`, `$scrape`, `$rank`, `$apply`, `$interview`, `$outcome`, `$upskill`, `$expand`, `$price`, `$html-report`, `$gmail-sync`, `$notion-sync`, `$add-portal`, `$add-template`, or `$reset`. Each points to its canonical specification. Slash-command examples in those specifications are Claude syntax; use the corresponding `$skill` in Codex. When a legacy command name arrives as ordinary message text, resolve it to the same workflow.

Keep candidate facts and workflow edits in the canonical files. Never copy profiles or command bodies into Codex adapters, create a `.Codex/` tree, or rename factual mentions of Claude Code in the candidate's experience.
