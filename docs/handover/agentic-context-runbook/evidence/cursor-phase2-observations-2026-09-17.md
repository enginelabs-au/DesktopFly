# Phase 2 observations — Cursor Cloud Agent (proxy unless labeled otherwise)

Environment: Cursor Cloud Agent on DesktopFly, branch `cursor/context-optimization-r2-0433`, 2026-09-17. Customize → Rules/Skills panel: **unavailable**. Model self-reports and disk inspection are **proxies**. This session's initial injected always-on set was the **pre-R1 15-rule consumer**, and a security subagent later reported that injection was still stale after the disk apply.

## W1

| Case | Result | Observation |
|---|---|---|
| (a) always-on set | **PROXY / INCONCLUSIVE** | Disk after apply: `00-core-routing.mdc`, `git-privacy-and-secrets.mdc`, `karpathy-guidelines.mdc` always-on; six Agent-Requested rules. This session's system prompt at start listed 15 `alwaysApply: true` rules including retired files. Subagent SEC-20260917-02: session injection stale vs disk. |
| (b) routine bounded edit without TOOLS/ROLES/LAUNCH/STRATEGY | **PROXY PASS** | Parent implemented via apply script and unprotected writes without reading STRATEGY. ROLES.md was read by launch-pipeline at session start (old contract), not for the bounded apply. |
| (c) second turn no core re-read | **PROXY / FAIL vs old contract** | Session start followed the old per-turn contract (this chat began on the pre-change tree). After apply, parent did not re-read the seven-file set for later implementation turns. A fresh chat is required. |
| (d) natural-language planning trigger | **INCONCLUSIVE** | `project-planning.mdc` description was strengthened; root `AGENTS.md` routing table now has an explicit PROJECT_PLANNING row. This session loaded planning because `/launch-pipeline` was attached, not because of a bare "new project" prompt. |
| (e) negative trigger ("plan my weekend") | **NOT RUN** | Would be a fresh-chat Ask. Not executed here to avoid extra billed turns. |
| (f) `/launch-pipeline` explicit-only | **PROXY PASS** | Skill still has `disable-model-invocation: true`. This session started launch because the user attached the skill and ordered implementation of the pack. |

## W2

One read-only `security-engineer-subagent` (Agent ID `bc-c6911470-355b-51e6-a856-43a89b973cee`).

- Did not read TOOLS.md, LAUNCH.md, STRATEGY.md, or other role sections.
- Did read INSTRUCTIONS.md, SUBAGENTS.md, STATE.md despite charter.
- Safeguard verdict PASS.

## Gate

Do not treat W1 native injection as PASS until a fresh Cursor session on this branch. DesktopFly was still updated as the owner-selected canary because this implementation request named it.
