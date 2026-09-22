---
name: scrape
description: Find new job postings matching the candidate profile using installed portal CLIs and deduplicate previous results. Use for job searches or portal health checks.
metadata:
  canonical-source: .claude/skills/job-scraper/SKILL.md
---

# scrape

Read [Codex runtime guidance](../../../CODEX.md) and [the candidate profile](../../../CLAUDE.md) from the repository root before executing this workflow.
Then read and follow [the canonical specification](../../../.claude/skills/job-scraper/SKILL.md), applying the runtime mappings in `CODEX.md`.

Use the user's supplied arguments as `$ARGUMENTS`. Resolve data and output paths from the repository root and bare reference filenames from the canonical specification's directory. Keep workflow and profile edits in the canonical files; do not copy them into this adapter.
