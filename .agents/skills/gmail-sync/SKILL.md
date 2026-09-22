---
name: gmail-sync
description: Read connected Gmail to propose status updates for tracked job applications, then record approved changes. Does not send email.
metadata:
  canonical-source: .claude/commands/gmail-sync.md
---

# gmail-sync

Read [Codex runtime guidance](../../../CODEX.md) and [the candidate profile](../../../CLAUDE.md) from the repository root before executing this workflow.
Then read and follow [the canonical specification](../../../.claude/commands/gmail-sync.md), applying the runtime mappings in `CODEX.md`.

Use the user's supplied arguments as `$ARGUMENTS`. Resolve data and output paths from the repository root and bare reference filenames from the canonical specification's directory. Keep workflow and profile edits in the canonical files; do not copy them into this adapter.
