# STATE.md

## Current Objective

- Own DesktopFly (P-011) on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2). Neural / LIF **enabled** (Cam override). Continue launch pipeline.

## Current Status

- Phase 0–3 complete on branch `cursor/phase-0-foundations-a5d1`. Phase 4 supervisor/health plan written (not implemented).

## Project Phase

- Phase 3 Electron/Swift shell — complete.
- Next: `docs/plans/phase_4_supervisor_health_plan.md` (plan only until implementing).

## Active Plan

- Completed: `docs/plans/phase_3_electron_swift_shell_plan.md`
- Planned: `docs/plans/phase_4_supervisor_health_plan.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## Active Role and Gate

- Sole DesktopFly owner: `bc-a5af2fcb` (ignore archived chats).
- Last validation: pytest 28; node 10; foundations PASS.

## Owner Decision

- Git: `Cursor Agent <cursoragent@noreply.github.com>`.
- **Neural enabled** — Cam overruled Q-012 keep-off gate (`docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md`).
- MaleCNS v1.0; Electron + Swift.
- Phase-transition pings required before implement / after complete.

## Active Instructions

- `/instructions/PROJECT_PLANNING.md`
- `/instructions/LAUNCH.md`

## Active Items

- Implement phase 4 when continuing.
- MaleCNS feather download is a **technical** blocker for full connectome, not a policy lock — synthetic LIF OK in CI.
- Do not wait on archived DesktopFly agents.

## Files in Active Use

- `config/policy.json` (`real_graph_enabled: true`)
- `desktop/**`
- `native/DesktopContext/**`
- `backend/flysim/lif.py`
- `reports/desktop-shell.json`
- `docs/plans/phase_3_electron_swift_shell_plan.md`
- `docs/plans/phase_4_supervisor_health_plan.md`

## Open Blockers

- Technical: MaleCNS weights file not present under `data/raw/`.
- Technical: Electron GUI / AppKit not executable on this Linux host (scaffold + unit tests only).
- No Cam policy blocker.

## Attempts Performed

- Applied Cam neural enable; removed Q-012 refuse-start lock.
- Implemented Electron shell modules + Swift scaffold + tests.
- Regenerated reports; foundations check updated for enabled flag.

## Decisions and Assumptions

- Synthetic graph is acceptable for CI LIF until weights land.
- Authored animation remains Find-fly / presentation fallback.
- Neural output still cannot invoke connectors.

## Current Working State

- Branch `cursor/phase-0-foundations-a5d1`.
- Policy `real_graph_enabled: true`.

## Next Actions

- Push phase-3 + neural-enable commit to PR #2.
- Status ping: phase 3 complete → phase 4 plan ready.
- On next turn: implement phase 4 after a planning→implementing ping.

## Last Updated

- 2026-09-16 — phase 3 complete; neural enabled per Cam.
