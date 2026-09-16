---
plan: phase_2_authored_motion
status: complete
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_1_safe_ingest_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
blueprint: docs/blueprints/2026-09-16_desktopfly.md
---

# Phase 2: Authored pet motion (LIF inert)

## 1. Objective

Ship the **authored-animation live path** while Q-012 keeps the neural simulation disabled: a presentation clock, world pose / locomotion FSM, cursor-yield kinematics, Find-fly, and an inert LIF module that **cannot start**. `real_graph_enabled` stays `false`.

## 2. Relation to project end-state

Version-1 motion for the desktop pet does not require a connectome controller. Electron/Swift (phase 3) will render poses from this controller. Enabling LIF remains an owner decision after Q-012 is withdrawn or reframed.

## 3. Entry criteria and inherited evidence

- Phase 0 complete on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2).
- Phase 1 complete: `backend/flysim/ingest.py`, `review.py`, synthetic fixture, `reports/ingestion.json`, pytest green, `real_graph_enabled: false`.
- Decision: `docs/decisions/2026-09-16-neural-sim-disabled-q012.md`.

## 4. Scope

- `backend/flysim/clock.py` — monotonic presentation clock; fake clock for tests; no unbounded catch-up
- `backend/flysim/world.py` — pose (`x`, `y`, `headingRad`, `speedPointsS`, `depth01`, locomotion), surface attach, open-space fallback
- `backend/flysim/authored.py` — explicit authored animation policy (modes, wing/gait presentation params as data only, Find fly, cursor yield)
- `backend/flysim/lif.py` — LIF policy/state surface + `refuse_lif_start` / blocked worker start while graph disabled; optional numpy one-neuron math for unit checks only
- Expand `config/desktop-pet.json` with handover cursor-yield / depth / overlay engineering values
- `src/pet/` portable authored-motion module (Node-testable; no Electron yet)
- Tests: clock catch-up refusal, locomotion FSM, cursor-yield bounds, Find fly without neural worker, LIF start refusal, policy flag still false
- Update foundations check and reports

## 5. Non-goals

- Starting a LIF worker or setting `real_graph_enabled: true`
- Electron overlay, Swift helper, Accessibility, ScreenCapture (phase 3)
- Supervisor / health recipes (phase 4)
- Torch / MPS / real MaleCNS load
- Claiming connectome-driven motion

## 6. Assumptions, constraints, risks

| Item | Kind | Note |
|---|---|---|
| Q-012 still open | verified | Neural enable blocked |
| Linux host | verified | No Mac overlay proof this phase |
| Authored motion ≠ neural evidence | verified | Log transition source as `authored` / `geometry` / `operator` |
| Torch deferred | provisional | Inert LIF uses numpy or raise-on-import until enable gate |

## 7. Dependencies

Phase 1 ingest/fixture → this phase → phase 3 Electron/Swift → phase 4 supervisor/health → final checklist.

## 8. Architecture

```text
AuthoredAnimationController ──► WorldPose (presentation clock)
        │
        ├── cursor yield (post-decode kinematic courtesy)
        ├── Find fly (operator; works with LIF stopped)
        └── refuse_lif_start(policy) ── blocks FrozenLIF / worker
```

One presentation clock only. No second production neural clock.

## 9. Files and paths

- `docs/plans/phase_2_authored_motion_plan.md` (this file)
- `backend/flysim/clock.py`, `world.py`, `authored.py`, `lif.py`
- `backend/tests/test_authored_motion.py`, `test_lif_inert.py`
- `config/desktop-pet.json`
- `src/pet/authored-motion.mjs`, `src/pet/authored-motion.test.mjs`
- `scripts/check-foundations.mjs`
- `reports/authored-motion.json`
- `.cursor/STATE.md`, memory continuation

## 10. Ordered tasks

1. Mark phase 1 plan complete with evidence.
2. Implement clock + world + authored controller + inert LIF gate.
3. Expand desktop-pet config; keep policy graph flag false.
4. Add Python and Node tests; write `reports/authored-motion.json`.
5. Update foundations check; validate; push PR #2.

## 11. Adaptive role map

Same workstream. Growth skipped. SWE implements; SEC confirms LIF cannot start and flag stays false; PL reconciles after tests.

## 12. Validation matrix

| Check | Evidence |
|---|---|
| Policy graph off | `check-foundations.mjs` + pytest |
| LIF start refused | `test_lif_inert.py` |
| Clock no unbounded catch-up | `test_authored_motion.py` |
| Cursor yield bounded | pytest + node test |
| Find fly without neural | pytest |
| Authored report written | `reports/authored-motion.json` |

## 13. Deferred human actions

Mac overlay, template license review, MaleCNS download, Q-012 reframing — unchanged.

## 14. Acceptance criteria

- Authored controller produces finite poses on the presentation clock
- LIF / worker start raises while `real_graph_enabled` is false
- No torch/MPS requirement for this phase’s green checks
- Foundations check and pytest + node tests pass on Linux
- PR #2 updated on `cursor/phase-0-foundations-a5d1`

## 15. Completion evidence

- `backend/flysim/clock.py`, `world.py`, `authored.py`, `lif.py`
- `backend/tests/test_authored_motion.py`, `test_lif_inert.py`
- `src/pet/authored-motion.mjs` + node tests
- Expanded `config/desktop-pet.json` (cursor yield / depth / authored flags)
- `reports/authored-motion.json` (`lif_start_refused: true`, neural worker not started)
- Validation 2026-09-16: `pytest` 26 passed; `node --test src/pet/authored-motion.test.mjs` 3 passed; `node scripts/check-foundations.mjs` passed
- `real_graph_enabled` remains false; Q-012 unchanged

## 16. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, `docs/plans/phase_0_foundations_plan.md`, this completed phase-2 plan, the active workstream manifest and role handoffs, all completion evidence, current repository state, and active blockers. Confirm phase 2 and every required role gate are implemented and validated. Then generate exactly one exhaustive next phase plan at `docs/plans/phase_3_electron_swift_shell_plan.md` for the Electron overlay, Swift DesktopContext helper, menus, click-through, and host lease — still with `real_graph_enabled: false` and LIF unstarted. Do not implement phase 3 until that plan is written.
