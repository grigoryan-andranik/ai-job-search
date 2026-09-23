# Running AI Job Search with Codex

Open this repository in Codex, or run `codex` from its root. Codex reads `AGENTS.md` and discovers the skills in `.agents/skills/`. No Claude installation, Anthropic account, or Gemini CLI is required for the job-search workflows.

Type `$` to select a skill, or ask for the task in plain language. For example:

```text
$scrape
$rank
$apply https://example.com/careers/devops
$interview Example Company
$upskill
```

## Terminal dashboard

Install and run the optional Textual interface from the repository root:

```bash
python3 -m pip install -e .
job-search
```

The dashboard reads `job_search_tracker.csv` and `job_scraper/seen_jobs.json`
without changing them. Choosing a workflow suspends the dashboard and starts an
interactive Codex session with the corresponding `$skill` prompt. Codex keeps
ownership of tool approvals, clarification questions, document generation, and
all workflow state. Exit that Codex session to return to the refreshed dashboard.

Keyboard shortcuts: `r` refreshes repository data, `/` focuses workflow
arguments, `Ctrl+R` runs the selected workflow, and `q` exits.

Use `$setup` only when onboarding or updating your profile; this workspace already has a populated profile. For a targeted update, use `$setup --section skills`.

| Task | Codex skill | Canonical specification |
| --- | --- | --- |
| Profile onboarding or updates | `$setup` | `.claude/commands/setup.md` |
| Search and deduplicate jobs | `$scrape` | `.claude/skills/job-scraper/SKILL.md` |
| Rank saved jobs | `$rank` | `.claude/commands/rank.md` |
| Evaluate and prepare an application | `$apply` | `.claude/commands/apply.md` |
| Prepare for an interview | `$interview` | `.claude/commands/interview.md` |
| Record application outcomes | `$outcome` | `.claude/commands/outcome.md` |
| Identify skill gaps and learning resources | `$upskill` | `.claude/skills/upskill/SKILL.md` |
| Enrich a profile from evidence | `$expand` | `.claude/commands/expand.md` |
| Benchmark compensation | `$price` | `.claude/commands/price.md` |
| Build an offline dashboard | `$html-report` | `.claude/commands/html-report.md` |
| Propose status updates from Gmail | `$gmail-sync` | `.claude/commands/gmail-sync.md` |
| Publish a view in Notion | `$notion-sync` | `.claude/commands/notion-sync.md` |
| Add a job portal | `$add-portal` | `.claude/commands/add-portal.md` |
| Register a document template | `$add-template` | `.claude/commands/add-template.md` |
| Reset selected personal data | `$reset` | `.claude/commands/reset.md` |

The existing `$job-application-assistant` skill handles individual evaluation, CV, letter, and career tasks. `$source-command-expand` and `$source-command-html-report` remain compatibility aliases.

## Shared source and paths

Read `CLAUDE.md` before any candidate-specific work. It contains profile facts and document requirements, including the plain-text letter and application kit. Keep it and `.claude/skills/` as the single source of truth. The adapters contain pointers, not separate copies of the profile or workflow.

Run shell commands from the repository root. Resolve `.claude/...`, `.agents/...`, `tools/...`, `cv/...`, `documents/...`, `company_research/...`, `job_scraper/...`, `upskill/...`, and the tracker against that root. There is one shared `job_scraper/seen_jobs.json` and one `job_search_tracker.csv`; do not create separate state under a skill directory.

Resolve bare reference filenames such as `01-candidate-profile.md` and `search-queries.md`, and phrases such as "this directory", against the **canonical specification's directory**, not the adapter directory. Update the canonical target when editing a profile or search strategy. The reference files under `.agents/skills/` are compatibility pointers.

## Translate Claude runtime instructions

Apply these mappings while following the canonical workflow's steps and output contracts. They adapt runtime mechanics; they do not change candidate facts, evaluation rules, or submission status.

| Canonical instruction | Codex equivalent |
| --- | --- |
| `/apply <arguments>` and other workflow commands | Invoke `$apply <arguments>` or the corresponding skill. These are prompts, not shell commands. |
| `$ARGUMENTS` | The actual URL, text, flags, or paths supplied with the user's request. It is not an environment variable. |
| `Read`, `Glob`, `Grep` | Available file-reading tools or shell commands such as `rg --files`, `rg`, and `cat`. |
| `Write`, `Edit`, `Bash` | Available file-editing and shell tools, subject to the session's permissions. |
| `WebSearch`, `WebFetch` | Available web search and page-opening tools. Search snippets alone do not verify a claim. |
| `AskUserQuestion` | An available user-input tool, or a concise chat question when required. Honor answers and authorization already given. |
| `Agent` / `Task`, `general-purpose` reviewer | Available Codex delegation tools when authorized. If unavailable, perform a separate critique pass and disclose that it was not an independent review. |
| Read a PDF visually | Render every page to images and inspect them using image-viewing tools. Text extraction alone does not satisfy visual verification. |
| Session `SCRATCHPAD` | Create a temporary directory with `mktemp -d` or Python's `tempfile`; use that path for temporary downloads and renders. |

For PDFs, use `pdftoppm -png -r 120 <file.pdf> <temporary-directory>/page`, then inspect all resulting images. Continue to use `tools/verify_pdf.py` and `tools/verify_layout.py` where prescribed. If rendering or image viewing is unavailable, report visual verification as incomplete rather than claiming it passed.

Claude's `allowed-tools` metadata and `.claude/settings.json` are not Codex permission grants. Use the active sandbox and approval controls; do not import Claude allowlists or disable sandboxing. A permission denial is not a missing executable or an expired job posting.

The `Claude-User` descriptions in `09-web-research.md` describe Claude's client, not Codex's identity. Preserve its trust boundary and robots gate. Do not use shell retries to bypass a denial from the active web tool or a site's access restrictions; find an accessible employer source or request the posting text instead.

Preserve reviewer critique, factual verification, and the final application kit even when delegation is unavailable. Do not substitute a Gemini subprocess for missing Codex tools. Label generated report footers with the runtime actually used (Codex), while keeping factual mentions of Claude Code in the candidate's history unchanged.

## Optional connectors

Discover Gmail and Notion tools from the active session by capability, not by Claude-specific tool prefixes. Map the workflow's operations to the connected tool's actual schema; do not invent method names or assume its pagination and response format match Claude's connector.

For Gmail, preserve label discovery when supported, paginated message search, full-body retrieval, stable message-ID deduplication, and the preview/approval step before writing tracker changes. If labels are unavailable, retain company and ATS-domain searches. Never send email as part of this workflow. If full bodies, stable IDs, or required pagination are unavailable, explain the missing capability and stop without recording guessed results.

For Notion, use connected search and page/database tools with the source's upsert and deduplication rules. If either connector is missing or unauthenticated, name the missing integration and stop that optional workflow. Direct the user to their Codex Apps/MCP connection settings; do not run `claude mcp ...`, initiate an authentication flow, or fall back to mailbox shell access.

`$reset` retains its exact scope preview and typed `RESET` confirmation. Preparing an application never means it has been submitted; preserve the `drafted` status until submission is recorded.

## Validation

```bash
python3 tools/lint_skills.py
python3 -m unittest tests.test_codex_workflows
```

See [SETUP.md](SETUP.md) for Python, Bun, LaTeX, and optional PDF tooling. Skill discovery and invocation follow the [official OpenAI documentation](https://learn.chatgpt.com/docs/build-skills).
