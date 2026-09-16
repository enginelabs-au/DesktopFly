# STATE.md

## Current Objective

- Continue DesktopFly (P-011) on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2) with neural simulation disabled while Q-012 is a release requirement.

## Current Status

- Phase 0–2 complete on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2). Phase 3 Electron/Swift plan written (not implemented). LIF cannot start; `real_graph_enabled: false`.

## Project Phase

- Phase 2 authored motion — complete. Phase 3 plan ready at `docs/plans/phase_3_electron_swift_shell_plan.md`.

## Active Plan

- Completed: `docs/plans/phase_2_authored_motion_plan.md`
- Planned (do not implement until executing): `docs/plans/phase_3_electron_swift_shell_plan.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## Active Role and Gate

- Continuation owner `bc-a5af2fcb` (prior `bc-f11a4081` unreachable).
- Last integrated validation: pytest 26 passed; node pet tests 3 passed; foundations check PASS.

## Predecessor Handoff

- Previous owner `bc-f11a4081` left Phase 1 at `cb556da`. This owner continues authored animation.

## Pending Remediation

- None recorded.

## Owner Decision

- Git writes use `Cursor Agent <cursoragent@noreply.github.com>`.
- Neural simulation stays disabled while Q-012 is a release requirement.
- MaleCNS v1.0 default. Electron + Swift shell.

## Active Instructions

- `/instructions/LAUNCH.md`
- `/instructions/PROJECT_PLANNING.md`
- `/instructions/ROLES.md`

## Active Items

- After PR update: generate phase-3 Electron/Swift plan only.
- Do not enable `real_graph_enabled`.
- Do not start LIF worker.

## Files in Active Use

- `docs/plans/phase_2_authored_motion_plan.md`
- `backend/flysim/clock.py`
- `backend/flysim/world.py`
- `backend/flysim/authored.py`
- `backend/flysim/lif.py`
- `src/pet/authored-motion.mjs`
- `config/desktop-pet.json`
- `config/policy.json`
- `reports/authored-motion.json`
- `scripts/check-foundations.mjs`

## Open Blockers

- None for authored path. Q-012 blocks neural *enable*, not authored-animation or Electron shell work.
- Flag Cam only if blocked (none this turn).

## Attempts Performed

- Checked out `cursor/phase-0-foundations-a5d1` @ `cb556da`.
- Marked phase 1 complete; wrote and implemented phase 2 authored motion + inert LIF.
- Validated on Linux (no Mac overlay claim).

## Decisions and Assumptions

- Authored motion is the live controller; LIF module is offline reference + start refusal only.
- Torch/MPS deferred until neural enable is authorized.
- Linux CI does not certify Electron/Swift/MPS.

## Current Working State

- Branch `cursor/phase-0-foundations-a5d1`.
- Policy `real_graph_enabled: false`.
- Reports: `reports/ingestion.json`, `reports/authored-motion.json`.

## Next Actions

- Push phase-2 (+ phase-3 plan) to PR #2.
- Implement phase 3 on Mac-capable follow-up; keep neural sim off.

## Last Updated

- 2026-09-16 — phase 2 complete; phase 3 plan authored (unimplemented).
