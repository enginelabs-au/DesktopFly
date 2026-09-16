# STATE.md

## Current Objective

- Complete DesktopFly phase 0 foundations and continue the launch pipeline with the neural simulation disabled while Q-012 is a release requirement.

## Current Status

- Phase 0 complete on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2). Phase 1 ingest started: synthetic fixture + `build_static_graph`; 7 pytest passed. Neural graph still disabled.

## Project Phase

- Phase 1 safe ingest — in progress. LIF/pet not started.

## Active Plan

- `docs/plans/phase_1_safe_ingest_plan.md`

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

- Finish remaining Phase 1 ingest tests/docs on the same PR.
- Do not enable `real_graph_enabled`.

## Files in Active Use

- `docs/plans/phase_1_safe_ingest_plan.md`
- `backend/flysim/ingest.py`
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

- Continue Phase 1 ingest (adapters, review schema) on this branch; keep the graph disabled.
- After Phase 1 verifies, write `docs/plans/phase_2_authored_motion_plan.md` only.

## Last Updated

- 2026-09-16 — phase 0 complete (PR #2); phase 1 ingest tests passing.
