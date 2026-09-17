# Cursor implementation prompt (second pass)

You are Cursor, the second implementation agent for the attached context-optimization pack (`agentic-context-runbook`, v1.2). GPT prepared the initial proposal (v1.1). Claude reviewed and revised it and made a bounded first implementation pass (R0→R1) on the shared source `/Users/camdouglas/agent-instructions`. You review Claude's design revisions **and** its actual implementation, correct supported defects, complete the validation Claude could not perform natively, and implement justified remaining work. GPT will then review both passes against the objective and the evidence. Do not claim final acceptance.

## Objective

Reduce irrelevant and repeated context per accepted change while preserving capability availability, reliable discovery, correct execution, and necessary safeguards, through selective activation rather than deletion. Optimize outcomes, not file length or tool counts. Subscriptions: Cursor US$200/month, ChatGPT Plus US$20, Claude Pro US$28, Gemini free; no new paid API spend; distinguish plan allowances from API billing.

## Read first

1. `INDEX.md` (status and reading order), then `10-CHANGE-LOG.md`, `11-IMPLEMENTATION-RECEIPT.md`, `12-REMAINING-WORK.md`.
2. `03-LOADING-EXPERIMENT.md` and `02-BASELINE.md` for what changed and why; `diffs/agent-instructions-r1.patch` for the exact diff.
3. `04`–`08` only for the sections a task touches. Do not follow every external link.

## What Claude changed (summary; verify on disk, do not trust this list)

- Fifteen always-on rules → three always-on (`00-core-routing.mdc`, `git-privacy-and-secrets.mdc`, `karpathy-guidelines.mdc`) plus five Agent-Requested rules (`alwaysApply: false` with descriptions; bodies unchanged).
- `.cursor/AGENTS.md` §2–3: read once per session, run read-only preflight, inspect `STATE.md`; reuse instructions in context; re-read only after change, context loss/compaction, newly relevant scope, or when exact wording matters. The session-start "read every file under `instructions/` and `rules/`" step is gone.
- Bootstrap now seeds repository-root `AGENTS.md` (new compact template with routing index), `.cursorignore`, `.githooks/`, the operator-setup handover and the governance CI workflow when absent.
- Subagent adapters and `ROLES.md` §3.2 read the charter, manifest, predecessor handoff, `ROLES.md` §1–3 and the role's own section; other core files on demand.
- `validate-agent-config.mjs` accepts rule modes, requires the core and git-safety rules always-on, rejects retired rule files, and fails on reintroduced per-turn read-all phrasing. `validate-launch.mjs` ignores OS metadata files.
- Coupled docs updated; template `STATE.md` reset to a skeleton. No hook, permission, sandbox, skill body, consumer repository, global client config, or credential was changed. Working tree is uncommitted; rollback snapshot and procedure are in `11-IMPLEMENTATION-RECEIPT.md`.

## Evidence Claude produced and its limits

Deterministic evidence: validators and 23 tests pass in a fresh fixture; bootstrap seeding and idempotence proven; seeded git hooks block a private-email commit; rollback tarball reproduces all 102 pre-change hashes. Primary sources verified for rule modes, `alwaysApply` precedence, root `AGENTS.md`, skill discovery locations, `disable-model-invocation`, and hook fields (`evidence/primary-source-verification-2026-09-17.json`).

Not done: no live Cursor session observed the candidate; the headless CLI needed an interactive login; subagent rule injection is undocumented; three adversarial review agents failed to start (Claude plan spend limit), so the adversarial review was performed inline. Token/cash savings are UNKNOWN and were not inferred from bytes.

## Your phases and gates

**Phase 1 — Independent review (no edits).** Inspect the current state of `/Users/camdouglas/agent-instructions` before accepting any reported completion: run the validators and tests yourself; diff against `candidate-source-manifest.json`; confirm the files listed in the change log exist as described. Review the design revisions (change-log ledger A, including the five recorded disagreements with the v1.1 proposal) and the implementation (ledger B). Report defects with location, evidence, consequence, smallest correction. Preserve sound decisions; do not restart or duplicate completed work.

**Phase 2 — Native validation (W1, W2 in `12-REMAINING-WORK.md`).** In a fresh Cursor chat on the candidate fixture (recreate it: fresh copy of the shared tree into a disposable directory, `git init`, `bash .cursor/scripts/bootstrap.sh`) or an owner-selected canary workspace, run the acceptance cases exactly as written: always-on set observed; routine edit without unrelated bodies; no per-turn re-read on the second turn; natural-language positive trigger for planning; negative trigger; `/launch-pipeline` explicit-only; one read-only subagent run. Use the Customize panel and the chat's rule/skill indicators as observation surfaces; label any model self-report as a proxy. Record verbatim observations under `evidence/`. Gate: promote nothing to consumers until these pass; if a trigger fails, strengthen the cue (description wording or a line in root `AGENTS.md`) rather than reverting to always-on, and re-test.

**Phase 3 — Corrections and justified remaining work.** Fix supported defects from Phase 1. Then take items in priority order from `12-REMAINING-WORK.md` (W3 propagation to one owner-selected consumer, W4 validator false-failure, W7/W8/W9 only if evidence from Phase 2 supports them). Each item is its own coherent batch with its own validation and rollback note. Stop when the next item lacks evidence or cannot be verified. Do not build registries, runners, adapters, gateways, or memory services (R3–R4 remain conditional). No purchases, account changes, deployments, credential handling, or permission broadening; W5 (key rotation) is owner-only, so surface it, do not perform it.

## Constraints specific to your environment

- The repository's fail-closed hooks deny agent edits to `AGENTS.md`, `.cursor/AGENTS.md`, `.cursor/INSTRUCTIONS.md`, `.cursor/instructions/ROLES.md`, `.cursor/agents/**`, `.cursor/rules/**`, `.cursor/hooks*`, `.cursor/scripts/{bootstrap.sh,validate-agent-config.mjs}` and related paths. Prepare exact patches and use the owner-authorized apply route recorded in the repository's history; do not weaken or bypass hooks.
- Hold model, reasoning, MCP set, hooks and permissions constant during Phase 2. Do not change plans or models.
- Keep secrets, raw logs and the private rollback snapshot out of the pack.

## Deliverables (consolidated pack v1.3 for GPT)

- Updated `INDEX.md` status and reading order; a change log entry set for your pass (proposal revisions vs applied changes); an updated implementation receipt (paths, versions, sanitized diffs or hashes, validation commands and outcomes, measured vs estimated, limitations, rollback); Phase 2 observations under `evidence/`; an updated remaining-work register; preserved research references and working relative links; regenerated `pack-manifest.json`.
- Label every item implemented / validated / proposed / deferred / blocked. Do not claim savings not measured. Do not initiate another research cycle or provider handoff; the user transfers the artifacts to GPT.
