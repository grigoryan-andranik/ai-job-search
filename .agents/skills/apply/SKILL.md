---
name: apply
description: Evaluate a job posting and prepare a tailored CV, cover letters, and application kit. Use when the user wants to prepare a job application.
metadata:
  canonical-source: .claude/commands/apply.md
---

# apply

Read [Codex runtime guidance](../../../CODEX.md) and [the candidate profile](../../../CLAUDE.md) from the repository root before executing this workflow.
Then read and follow [the canonical specification](../../../.claude/commands/apply.md), applying the runtime mappings in `CODEX.md`.

Use the user's supplied arguments as `$ARGUMENTS`. Resolve data and output paths from the repository root and bare reference filenames from the canonical specification's directory. Keep workflow and profile edits in the canonical files; do not copy them into this adapter.
