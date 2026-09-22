---
name: source-command-expand
description: Compatibility alias for the expand job-search workflow. Prefer $expand for new requests.
metadata:
  canonical-source: .claude/commands/expand.md
---

# source-command-expand

Read [Codex runtime guidance](../../../CODEX.md) and [the candidate profile](../../../CLAUDE.md) from the repository root before executing this workflow.
Then read and follow [the canonical specification](../../../.claude/commands/expand.md), applying the runtime mappings in `CODEX.md`.

Use the user's supplied arguments as `$ARGUMENTS`. Resolve data and output paths from the repository root and bare reference filenames from the canonical specification's directory. Keep workflow and profile edits in the canonical files; do not copy them into this adapter.
