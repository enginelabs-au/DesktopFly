# STATE.md

## Current Objective

- DesktopFly handover is merged to `main` ([PR #2](https://github.com/enginelabs-au/DesktopFly/pull/2)). Neural enabled. Remaining work is owner-only.
- Context-loading R2 (selective activation, pack v1.4) is on `main` via PR #3 and is maintained as a separate workstream.

## Current Status

- **Product merged.** Mac GUI/AppKit/MPS proof is recorded in `reports/mac-verification.json`.
- Context-optimization: implementation complete. Security gate PASS. Project lead CONDITIONAL (fresh-session W1 + owner W5).
- Hook fix [PR #6](https://github.com/enginelabs-au/DesktopFly/pull/6) is on `main`: read-only `merge-base`/`merge-tree` and paths containing `-merge-` no longer trip the identity check.

## Project Phase

- Product phases 0-4 + handover closeout are on `main`.

## Active Plan

- `docs/plans/final_implementation_checklist.md`
- Context-optimization plan: `docs/plans/context-optimization/phase_0_foundations_plan.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`
- `docs/workstreams/20260917-context-optimization/`

## Active Role and Gate

- Product validation on `main` (2026-10-06): backend pytest 52 passed / 2 skipped; node 45 passed; foundations PASS; launch validation PASS.
- Context-optimization: `project-lead-subagent` CONDITIONAL. Owner decision pending.

## Owner Decision

- Neural enabled (Cam).
- MPS unavailable on Linux CI; documented in `reports/device.json`.
- Commits must use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Secrets must never enter the repository.
- Branch ruleset deleted by the owner; `.github/CODEOWNERS` is `* @cam-douglas`.

## Core Files Loaded

- `/instructions/LAUNCH.md`
- `/instructions/PROJECT_PLANNING.md`
- `/instructions/SUBAGENTS.md`
- `/instructions/ROLES.md`

## Active Items

- Pack v1.4: `docs/handover/agentic-context-runbook/` and `GPT-REVIEW-PROMPT.md`.
- Owner handoff: `docs/workstreams/20260917-context-optimization/delivery/owner-handoff.md`
- Cost operator setup: `docs/handover/cursor-cost-operator-setup.md`
- All former project branches are merged or superseded and have been removed from the remote.

## Open Blockers

- Cam-only: optional Screen Recording, template license legal review.
- Context-optimization: W1 native injection unverified until a fresh session.

## Next Actions

- Owner: fresh chat W1; W5 if needed; GPT review of pack v1.4.

## Last Updated

- 2026-10-06: PRs #2, #6, and #7 merged; all former project branches removed; `main` re-validated.
