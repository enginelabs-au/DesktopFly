# STATE.md

## Current Objective

- Finish DesktopFly phase 1 synthetic ingest and phase 2 authored-animation path on [PR #2](https://github.com/enginelabs-au/DesktopFly/pull/2), keeping the neural simulation disabled while Q-012 remains a release requirement.

## Current Status

- Phase 0–2 complete on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2): synthetic ingest + authored animation + inert LIF gate. Neural graph still disabled. Electron/Swift not started.

## Project Phase

- Phase 2 authored motion — complete. Next plan only: phase 3 Electron/Swift (not implemented yet).

## Active Plan

- `docs/plans/phase_2_authored_motion_plan.md` (complete; next prompt points at phase 3)

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## Active Role and Gate

- `project-lead-subagent` pending PR description tool fix.
- Last integrated validation: pytest 23 passed; foundations PASS; preflight READY.

## Predecessor Handoff

- Continued from owner `bc-f11a4081` after messaging failed; same PR branch `cursor/phase-0-foundations-a5d1`.

## Pending Remediation

- None recorded.

## Owner Decision

- Git writes use `Cursor Agent <cursoragent@noreply.github.com>`.
- Neural simulation stays disabled while Q-012 is a release requirement.
- MaleCNS v1.0 default. Electron + Swift shell.
- Do not open a second PR while #2 can take commits.

## Active Instructions

- `/instructions/LAUNCH.md`
- `/instructions/STRATEGY.md`
- `/instructions/PROJECT_PLANNING.md`
- `/instructions/ROLES.md`
- `/instructions/SUBAGENTS.md`

## Active Items

- Generate phase-3 plan only when ready; do not implement Electron/Swift until that plan exists.
- Do not enable `real_graph_enabled`.
- Do not flag Cam unless blocked.

## Files in Active Use

- `docs/plans/phase_2_authored_motion_plan.md`
- `docs/plans/phase_1_safe_ingest_plan.md`
- `backend/flysim/authored.py`
- `backend/flysim/world.py`
- `backend/flysim/clock.py`
- `backend/flysim/lif.py`
- `backend/flysim/review.py`
- `config/policy.json`
- `scripts/check-foundations.mjs`

## Open Blockers

- None for authored path. Q-012 blocks neural *enable* only.
- ManagePullRequest tool rejected updates for this multi-repo workspace (`PR URL must belong to the current repository`); commits still push to the PR branch.

## Attempts Performed

- Fetched PR branch; completed phase-1 review compiler + report.
- Implemented phase-2 authored/LIF modules; 23 pytest passed.

## Decisions and Assumptions

- Phase 1 parquet adapters deferred; JSON synthetic tables are sufficient while the real graph is off.
- Authored locomotion uses finite `idle|crawl|flight` only.
- LIF module may exist but `start_lif_worker` must raise while the flag is false.

## Current Working State

- Branch `cursor/phase-0-foundations-a5d1` tracking origin.
- Policy `real_graph_enabled: false`.

## Next Actions

- After phase 2 is on the PR, write only `docs/plans/phase_3_electron_swift_shell_plan.md` when Cam wants shell work (do not implement until planned).
- Retry PR title/body update when ManagePullRequest accepts this repo.

## Last Updated

- 2026-09-16 — phase 1–2 complete on PR #2; neural sim still off.
