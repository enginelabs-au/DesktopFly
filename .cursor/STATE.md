# STATE.md

## Current Objective

- Complete DesktopFly phase 0 foundations and continue the launch pipeline with the neural simulation disabled while Q-012 is a release requirement.

## Current Status

- Phase 0 planning and foundations are implemented on `cursor/phase-0-foundations-a5d1`. Bootstrap followed; preflight `READY`; `node scripts/check-foundations.mjs` passed.

## Project Phase

- Phase 0 foundations — implementing / verifying. Product pet/LIF code has not started.

## Active Plan

- `docs/plans/phase_0_foundations_plan.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## Active Role and Gate

- `project-lead-subagent` reconciled CONDITIONAL pending PR.
- Last integrated validation: foundations check PASS; launch validation 91 files.

## Predecessor Handoff

- Previous owner `bc-dab50473` archived; `cursor/phase-0-foundations-6edd` was never pushed. Reran launch-pipeline from `main` @ `61c436f`.

## Pending Remediation

- None recorded.

## Owner Decision

- Git writes use `Cursor Agent <cursoragent@noreply.github.com>`.
- Neural simulation stays disabled while Q-012 is a release requirement.
- MaleCNS v1.0 default. Electron + Swift shell.

## Active Instructions

- `/instructions/LAUNCH.md`
- `/instructions/STRATEGY.md`
- `/instructions/PROJECT_PLANNING.md`
- `/instructions/ROLES.md`
- `/instructions/SUBAGENTS.md`

## Active Items

- Open PR for phase-0 foundations.
- After phase 0 is marked complete, generate `docs/plans/phase_1_safe_ingest_plan.md` only.
- Do not enable `real_graph_enabled`.

## Files in Active Use

- `docs/plans/phase_0_foundations_plan.md`
- `docs/blueprints/2026-09-16_desktopfly.md`
- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`
- `.cursor/rules/fly-simulation.mdc`
- `config/policy.json`
- `scripts/check-foundations.mjs`
- `docs/handover/fruit-fly-cursor-handover.md`

## Open Blockers

- None for phase 0. Q-012 blocks neural *enable*, not authored-animation work.

## Attempts Performed

- Fetched `origin/main` (`61c436f` LAUNCH.md rename). Confirmed no usable phase-0 remote branch.
- Preflight `MATERIALIZATION_REQUIRED` (missing `docs/blueprints`).
- `bash .cursor/scripts/bootstrap.sh` → READY.
- Wrote blueprint, phase-0 plan, decisions, workstream, fly rule, layout, policy, provenance, check script.

## Decisions and Assumptions

- Resume from current main rather than a missing prior branch.
- Lead materialized role artifacts in-repo.
- Template SHA `38f55332055328d38c29e72474c4ad5b6876101f` is a pin, not a legal review.

## Current Working State

- Branch `cursor/phase-0-foundations-a5d1`.
- Policy `real_graph_enabled: false`.

## Next Actions

- Commit, push, open PR.
- Mark phase 0 complete after PR + recorded evidence.
- Generate phase 1 ingest plan; keep the graph disabled.

## Last Updated

- 2026-09-16 — phase 0 foundations implemented after authorized bootstrap.
