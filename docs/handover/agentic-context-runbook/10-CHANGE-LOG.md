# 10 · Change log (v1.1 → v1.2)

Two ledgers: **A** proposal revisions to this pack; **B** changes applied to the shared source on disk. Entries are tagged retain / correct / simplify / add / defer. Evidence for B is in [11](11-IMPLEMENTATION-RECEIPT.md).

## A. Proposal revisions (documents only)

| # | Where | Tag | Change | Why |
|---|---|---|---|---|
| A1 | [INDEX](INDEX.md) | correct | Status moved from "review only, implementation not performed" to "R0→R1 first pass applied to the shared source; native validation pending". Reading order updated; rounds R2–R6 unchanged as conditional. | The user's request superseded the review-only restriction. |
| A2 | [02](02-BASELINE.md) | correct | "Reported local observations" replaced by direct `OBSERVED` facts: consumer inventory (12 repos, 4 current-generation), client versions, global Cursor/Codex/Claude/Gemini state, MCP bindings, byte accounting. | The v1.1 pack could not distinguish reported from verified; the first pass had filesystem access. |
| A3 | [02](02-BASELINE.md) | correct | Baseline corrected: the seven-file sum (45,966) understated the mandated load; session start also required ~101 KB of instruction bodies and each subagent ~110 KB. | Direct reading of `AGENTS.md` §2, `ROLES.md` §3.2 and the adapters. |
| A4 | [02](02-BASELINE.md), [03](03-LOADING-EXPERIMENT.md) | add | The template repository is not a valid consumer and a fresh copy could not pass its own bootstrap (missing seeded root files). | Observed by running the validators in the template and in a fresh fixture. Blocked the canary path, so it was fixed in B. |
| A5 | [03](03-LOADING-EXPERIMENT.md) | simplify | Fifteen-rule table now records final dispositions and the fallback design (Agent-Requested rules duplicate obligations that remain in `AGENTS.md`/`INSTRUCTIONS.md`). | Makes the discovery-miss risk explicit and bounded. |
| A6 | [04](04-CAPABILITY-SURFACES.md) §6, §7 | correct | MCP: the fixed workspace bindings are current, not historical. Hooks: `beforeShellExecution` also accepts `ask`; exit code 2 blocks, other non-zero codes fail open unless `failClosed`. | Primary-source verification (E07) and `~/.cursor/mcp.json` inspection. |
| A7 | [04](04-CAPABILITY-SURFACES.md) §4 | add | Cursor discovers skills from `.agents/skills`, `.cursor/skills`, `.claude/skills`, `.codex/skills` (workspace and home, in that priority); the template's untracked `.agents/` duplicates two skills. | Docs (E05) and installed build strings. |
| A8 | [05](05-ROUTING-AND-AUTOMATION.md) | correct | Provider facts: Codex CLI binary broken; Codex desktop default `gpt-6-astra`/`ultra`; Claude Code and Gemini have no global instruction files; `agent` CLI print mode needs a fresh login. R3 adapter work has nothing to clean up yet. | Observed. |
| A9 | [06](06-EVALUATION-AND-RECOVERY.md) | retain | Gates unchanged; added a note that deterministic cases passed and live cases are outstanding. | Gates were sound. |
| A10 | [07](07-REVIEW-AND-CONTRACTS.md) | correct | "Current task: review only" replaced with the three-stage sequence (Claude first pass → Cursor second pass → GPT review). Future-implementation-review section now points at the receipt. | Reflects the actual process. |
| A11 | [08](08-EVIDENCE.md) | add | Ledger delta E43–E45: primary-source verification results (six pages), installed-build evidence, fixture evidence; E07 and E04/E05 annotated. | Verification performed 2026-09-17. |
| A12 | [09](09-HISTORICAL-EVIDENCE-AND-COVERAGE.md) | retain | Unchanged except the coverage table gains rows for 10–12 and the Cursor prompt. | Historical material stays historical. |
| A13 | [01](01-CONTRACT.md) | correct | "Current review mode" paragraph replaced with the staged-handoff statement; scope sentence notes consumers are hand-copied. | Consistency. |
| A14 | pack | add | `diffs/`, `evidence/`, `candidate-source-manifest.json`, chapters 10–12, `CURSOR-IMPLEMENTATION-PROMPT.md`. | Required deliverables. |
| A15 | pack | defer | No new infrastructure documents (registry, runner, adapters) were added; R2–R6 remain proposals. | No evidence yet justifies them. |

**Disagreements with the v1.1 proposal.** (1) It treated shared-source changes as possibly affecting live consumers; consumers are hand copies, so a shared-source change is inert until propagated, and the canary had to be a fixture. (2) It counted only the seven core files as the baseline; the larger session-start and subagent loads were the bigger avoidable cost. (3) It kept onboarding/seeding in R4; seeding was pulled forward because the fixture canary could not exist without it. (4) Its `~/.cursor/rules` and User Rules lead is closed: nothing native is there. (5) Provider routing (R3) is further away than implied: two of the four alternative clients have no working instruction adapter at all.

## B. Applied changes to `/Users/camdouglas/agent-instructions` (working tree, uncommitted)

| # | Path(s) | Tag | Change |
|---|---|---|---|
| B1 | `.cursor/rules/00-core-routing.mdc` (new); eight rule files removed | simplify | Merged routing/state rules into one always-on rule. |
| B2 | `.cursor/rules/{project-planning,subagent-orchestration,blocker-governance,memory-governance,runbook-governance}.mdc` | simplify | `alwaysApply: false` with a discovery description; bodies unchanged. |
| B3 | `.cursor/AGENTS.md` §2–3 | correct | Session-start read-once and reuse/refresh policy replaced read-all and per-turn contracts. |
| B4 | `.cursor/INSTRUCTIONS.md`, `.cursor/BOOTSTRAP.md` §2, §3, §5, §8 | correct | Removed per-turn/startup read-all wording; documented rule modes and seeded files. |
| B5 | `.cursor/templates/{root-agents.md,cursorignore,agent-governance-operator-setup.md}` (new); `.cursor/scripts/bootstrap.sh` | add | Seed root `AGENTS.md`, `.cursorignore`, handover, `.githooks/` and CI workflow when absent. |
| B6 | `.cursor/agents/*.md` (6), `.cursor/instructions/ROLES.md` §3.2 | simplify | Role preload limited to charter, manifest, handoff, `ROLES.md` §1–3 and own section. |
| B7 | `.cursor/scripts/validate-agent-config.mjs` | correct | Rule-mode validation, always-on requirements, retired-file rejection, eager-load guard. |
| B8 | `.cursor/skills/launch-pipeline/scripts/validate-launch.mjs` | correct | Ignore `.DS_Store`/`Thumbs.db` in reachability walk. |
| B9 | `README.md`, `.cursor/README.md`, `.cursor/memory/MEMORY.md`, `.cursor/memory/runbooks/agent-workspace.md`, `.cursor/instructions/{LAUNCH,PROJECT_PLANNING}.md`, `.cursor/skills/launch-pipeline/SKILL.md`, `.cursor/templates/phase-plan-template.md` | correct | Coupled wording: loading model, rename advice, stale "run the bootstrap" step, "complete core context" prompts. |
| B10 | `.cursor/STATE.md` | simplify | Reset to a template skeleton. |
| B11 | `.cursor/memory/memories/2026-09-17-continuation.md` (new) | add | Continuation entry per the control plane's own discipline. |

Not changed: hooks, `cli.json`, `sandbox.json`, `permissions.json`, `hooks/policy.mjs`, tests, skills bodies, `TOOLS.md`, `USER.md`, `SKILLS.md`, `STRATEGY.md`, `SUBAGENTS.md`, git-safety payloads, `.agents/`, any consumer repository, any global client configuration, any credential.

## C. Cursor second pass (v1.2 → v1.3) — proposal / review

| # | Where | Tag | Change | Why |
|---|---|---|---|---|
| C1 | Phase 1 review | retain | Claude ledger A disagreements 1–5 kept | Independent reconstruction supported them |
| C2 | W1 | defer | Customize-panel injection not observed | Cloud Agent has no Rules panel; session prompt was pre-R1 |
| C3 | W8/W9/W7 | defer | No ROLE-CONTRACT extract; no TOOLS/SKILLS prose trim; no `.agents` dedupe | Phase 2 did not produce evidence that those batches would improve outcomes |
| C4 | Home-directory workspace | defer | `/camdouglas` as single root **not** implemented | Indexing/search would likely expand, not shrink, context |

## D. Cursor second pass — applied (DesktopFly canary)

| # | Path(s) | Tag | Change |
|---|---|---|---|
| D1 | `.cursor/scripts/validate-agent-config.mjs` | correct | `karpathy-guidelines.mdc` required always-on; eager-load scan includes `SUBAGENTS.md` and launch skill |
| D2 | `.cursor/instructions/SUBAGENTS.md` | correct | Preload aligned with ROLES §3.2; subagents only if user permits or launch requires a named role |
| D3 | git-safety payloads `bootstrap.sh`, `validate-agent-config.mjs` | correct | Resynced to canonical R2 scripts so `apply-git-safety.sh` cannot revert loading policy |
| D4 | repository-root `AGENTS.md`, `.cursorignore` | add | Compact router + Ask skip; merged secret ignores |
| D5 | `.cursor/AGENTS.md`, `.cursor/rules/00-core-routing.mdc` | correct | Ask/acknowledgment skip preflight; cost defaults in always-on core |
| D6 | `.cursor/skills/launch-pipeline/scripts/validate-launch.mjs` | correct | Unlinked `memory/runbooks/` are `project-local` warnings (W4) |
| D7 | `.cursor/rules/cost-and-session.mdc`, `.cursor/USER.md` | add | Requestable cost rule + standing cost directives |
| D8 | `.cursor/rules/project-planning.mdc`, root routing table | add | Stronger natural-language planning cue |
| D9 | DesktopFly consumer | add | R1+R2 propagated via `docs/handover/apply-context-optimization-r2.sh` |

Hooks, permissions, sandbox, and `policy.mjs` still unchanged. No credentials rotated. Token savings not claimed.

## E. Pack completeness (v1.3 → v1.4)

| # | Where | Tag | Change | Why |
|---|---|---|---|---|
| E1 | [this-pass/](this-pass/) | add | Snapshot every in-repo artefact from the DesktopFly canary that lived outside this pack: live control-plane copies, apply script, payloads, workstream, plans, decision, operator note. Retired rules restored from `origin/main` into `this-pass/retired-rules/`. Unified diff of non-pack PR files in `this-pass/desktopfly-outside-pack.patch`. | Owner asked for one folder containing everything Cursor worked on. Live canary files were copied, not moved. |
| E2 | [INDEX](INDEX.md), [13](13-CURSOR-RECEIPT.md), `pack-manifest.json` | correct | Pack version 1.4; reading order includes `this-pass/README.md`; out-of-repo items remain explicit. | Completeness without claiming Mac/global artefacts that were never on this VM. |
