# STATE.md

## Current Objective

- Own DesktopFly (P-011) on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2). Neural / LIF **enabled**. Phase 4 complete; final checklist open for Mac/human items.

## Current Status

- Phases 0–4 complete on branch `cursor/phase-0-foundations-a5d1`.
- PR title/body updated for neural-enabled phases 0–3; Phase 4 commit follows.

## Project Phase

- Phase 4 supervisor/health — complete.
- Closure: `docs/plans/final_implementation_checklist.md`

## Active Plan

- Completed: `docs/plans/phase_4_supervisor_health_plan.md`
- Checklist: `docs/plans/final_implementation_checklist.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## Active Role and Gate

- Sole DesktopFly owner: `bc-a5af2fcb` (ignore archived chats).
- Last validation: pytest 40; node 10; foundations PASS.

## Owner Decision

- Git: `Cursor Agent <cursoragent@noreply.github.com>`.
- **Neural enabled** — Cam overruled Q-012 keep-off gate.
- Phase-transition pings required.

## Active Instructions

- `/instructions/PROJECT_PLANNING.md`
- `/instructions/LAUNCH.md`

## Active Items

- Mac/human checklist items (MaleCNS download, Electron GUI, AppKit, MPS).
- Do not wait on archived DesktopFly agents.

## Files in Active Use

- `backend/flysim/supervisor.py`, `health.py`, `recovery.py`, `checkpoints.py`, `bridge.py`, `worker.py`
- `config/policy.json`, `recovery-profiles.json`, `state-contract.json`
- `reports/supervisor-health.json`
- `docs/plans/final_implementation_checklist.md`

## Open Blockers

- Technical: MaleCNS weights file not present under `data/raw/`.
- Technical: Electron GUI / AppKit not executable on this Linux host.
- No Cam policy blocker.

## Attempts Performed

- Updated PR #2 title/body for neural-enabled phases 0–3.
- Implemented Phase 4 supervisor/health/recovery; tests green.

## Decisions and Assumptions

- Synthetic graph acceptable for CI LIF until weights land.
- Bridge/worker Mac asyncio+MPS deferred; Linux scaffolds + unit tests ship now.

## Current Working State

- Branch `cursor/phase-0-foundations-a5d1`.
- Policy `real_graph_enabled: true`.

## Next Actions

- Commit/push Phase 4; update PR body for phases 0–4.
- Status ping: Phase 4 complete → final checklist.

## Last Updated

- 2026-09-16 — phase 4 complete; neural enabled.
