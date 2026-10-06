# 02 · Baseline, provenance, and active-loading graph

Read when: R0, validating configuration drift, or checking what the R1 first pass changed. Pair with [contract](01-CONTRACT.md) and the baseline sections of [evaluation](06-EVALUATION-AND-RECOVERY.md). Evidence classes follow [01](01-CONTRACT.md). Everything marked `OBSERVED` below was inspected directly on the local machine on 2026-09-17 by the first-pass agent (Claude Code 2.1.117); the v1.1 pack's "reported local observation" wording is superseded where a direct observation now exists.

## Shared source (OBSERVED)

- Canonical checkout: `/Users/camdouglas/agent-instructions`, Git remote `github.com/cam-douglas/agent-instructions`, HEAD `cc2f6cd`, working tree dirty before this pass (28 modified files versus HEAD, `.agents/` and `.cursor/README.md` untracked). The v1.1 [baseline source manifest](baseline-source-manifest.json) hashes matched the working tree 25/25 before any change.
- Pre-change always-on surface: 15 `.cursor/rules/*.mdc`, all `alwaysApply: true`, 6,843 bytes. `.cursor/AGENTS.md` §2 required, at session start, reading `BOOTSTRAP.md` (8.1 KB) and every file under `instructions/` (ROLES 57.3 KB, LAUNCH 15.8 KB, STRATEGY 8.8 KB, PROJECT_PLANNING 6.3 KB, SUBAGENTS 4.1 KB) and `rules/` (already native). §3 required, on every substantive turn, re-reading seven core files totalling 45,966 bytes. Five rules restated those mandates. Six subagent adapters and `ROLES.md` §3.2 required every activated role to read the seven core files, all of `ROLES.md`, `SUBAGENTS.md`, every rule, and every matching skill body.
- `.cursor/skills/git-safety/payloads/` holds byte-identical copies of `hooks/policy.mjs`, `hooks/policy.test.mjs`, `scripts/bootstrap.sh`, `scripts/validate-agent-config.mjs`, `cli.json`, and `rules/git-privacy-and-secrets.mdc` (install payloads; not loaded unless read).
- `.agents/skills/` (untracked) duplicates `vercel-deploy-workflow` and `supabase-linked-migrations` from `.cursor/skills/` with two-line differences. Cursor scans both directories (documented and confirmed in the installed build), so the template workspace exposes duplicate skill entries.
- The template repository is not itself a valid consumer: its validators fail on missing repository-root `AGENTS.md`, `.cursorignore`, `docs/`, and CI workflow, and `bootstrap.sh` required those files without seeding them. A fresh copy of the shared tree therefore could not pass its own bootstrap.

## Consumers of the shared source (OBSERVED)

Copies are made by hand; no synchronization mechanism exists. Twelve repositories under the home directory contain a `.cursor/AGENTS.md`:

| Generation | Repositories | Root `AGENTS.md` | `hooks.json` | Rules matching template |
|---|---|---|---|---|
| Current (Aug–Sep 2026) | `DesktopFly`, `papership` | yes | yes | 15/15 (DesktopFly adds `fly-simulation.mdc`; papership lacks `git-privacy-and-secrets.mdc`) |
| Current, drifted | `puffpuffstop`, `context` | yes (refers to `LAUCH.md`, a typo) | yes | 14/15 |
| Older | `implemento`, `secretauth`, `z0rb-ai`, `ginzcoin`, `yournewhandle`, `sidequest`, `cc-dashboard-experimental`, `hertzlabs/binauralbeats` | mostly no | no | 0–10/15 |

Consumers carry project-local state (`STATE.md`, workstreams, extra runbooks). `puffpuffstop` fails `validate-launch.mjs` on an unlinked project-local runbook, an example of validator coupling that rejects legitimate local additions. Changing the shared source changes nothing in a consumer until it is propagated; propagation is deferred work (see [12](12-REMAINING-WORK.md)).

## Installed clients and global state (OBSERVED)

- Cursor desktop 3.20.21; `cursor-agent` CLI 2026.07.23 (`agent status` reports logged in but print mode demanded a fresh `agent login`). Installed-build strings confirm: rule modes always/agent/auto/manual; skill frontmatter `description`, `globs`, `disable-model-invocation`; skill discovery from `.cursor/skills`, `.agents/skills`, `.claude/skills`, `.codex/skills` (workspace and home); root `AGENTS.md` and `CLAUDE.md` recognized; `hooks.json` read from project `.cursor/`, `~/.cursor/`, and an enterprise path; hook events include `preToolUse`, `beforeReadFile`, `beforeShellExecution`, `beforeMCPExecution`, `subagentStart`, `sessionStart`, `preCompact`.
- `~/.cursor/rules/` contains only a Markdown README (not a native rule). `~/.cursor/skills/` holds four symlinks into an npx cache (`paperclip*`, `para-memory-files`). `~/.cursor/skills-cursor/` and `~/.agents/skills/` hold Cursor-managed built-in skills. `~/.cursor/agents/`, `commands/`, `hooks/` are empty or absent.
- `~/.cursor/mcp.json`: eleven global servers (`filesystem`, `base44-superagent`, `fetch`, `memory`, `figma`, `context7`, `cline`, `github`, `time`, `xcodebuild`, `Vercel`). `filesystem` and `cline` are bound to `/Users/camdouglas/quark` regardless of workspace (the "fixed workspace binding" lead is current). Plugin cache lists dozens of marketplace plugins; enabled state is UI-managed and was not inspected.
- Cursor User `settings.json` selects profile `cam-douglas-default`; one profile directory exists.
- Claude Code 2.1.117: no global `CLAUDE.md`, rules, skills, or agents. Codex: `~/.codex/config.toml` sets `model = "gpt-6-astra"`, `model_reasoning_effort = "ultra"`; the `codex` CLI binary is broken (ENOENT on its vendored executable); no `~/.codex/AGENTS.md`. Gemini CLI 0.29.5 with an empty `~/.gemini/GEMINI.md`.
- Credential hygiene (OBSERVED, not reproduced): an API key for one MCP server is stored as a plaintext command-line argument in both `~/.cursor/mcp.json` and `~/.codex/config.toml`, and other servers keep tokens in `env` blocks. Rotation is an owner action; see [12](12-REMAINING-WORK.md).

## Byte accounting (OBSERVED; bytes, not tokens)

| Surface | Baseline | Candidate after R1 |
|---|---|---|
| Always-on rule bytes injected each turn | 6,843 (15 rules) | 4,027 (3 rules) + 2,295 in 5 Agent-Requested rules loaded only on selection |
| Repository-root `AGENTS.md` (native) | 968–2,131 in consumers (router only) | 2,582 (compact core + routing index, seeded) |
| Mandated per-turn tool re-reads | 45,966 (seven files) | 0 mandated; `.cursor/AGENTS.md` once per session (12,196) |
| Mandated session-start reads beyond the above | ~101 KB (`BOOTSTRAP.md` + all `instructions/` + `rules/`) | 0 mandated; bodies load by route |
| Subagent mandated preload | ~110 KB per role start | charter + `ROLES.md` §1–3 (~31 KB) + own role section (~4–5 KB) |

`.cursor/AGENTS.md` grew by 419 bytes because the reread policy replaced the shorter read-all list. `STATE.md` shrank from 4,467 to 1,275 bytes (template skeleton). These are authored-byte deltas; effective injection and billed tokens were not measured (see [11](11-IMPLEMENTATION-RECEIPT.md)).

## Local configuration locations (OBSERVED)

- `/Users/camdouglas/agent-instructions/.cursor/`: canonical shared source; `.agents/` untracked duplicates.
- `/Users/camdouglas/.cursor/`: `mcp.json`, `cli-config.json`, `settings.json`, `agent-cli-state.json`, plugin caches, per-project state under `projects/`.
- `/Users/camdouglas/Library/Application Support/Cursor/User/`: editor settings and one profile. Internal state databases were not opened.

## R0 procedure and gate

The v1.1 R0 procedure (resolve checkout, inventory capability IDs, build the loading graph, trace consumers, capture traces, separate startup/metadata/body/tool-output, predeclare the intervention) was executed for the shared source and consumer wiring. Fresh-session traces (step 5) were **not** captured: the headless CLI needed an interactive login and the desktop client offers no exported context trace; this is the first item for Cursor's native pass. Gate R0 outcome: active source/consumer relationship established; shared files are copied templates, so the canary is a disposable fixture, not a live consumer.
