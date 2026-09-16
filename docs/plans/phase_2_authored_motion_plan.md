---
plan: phase_2_authored_motion
status: complete
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_1_safe_ingest_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Phase 2: Authored motion and inert LIF gate

## 1. Objective

Ship the live controller while Q-012 keeps the neural sim off: a finite authored locomotion state machine (`idle` / `crawl` / `flight`), presentation clock, Find-fly reveal, and an LIF module that exists but **cannot start** when `real_graph_enabled` is false.

## 2. Relation to project end-state

This is the first shippable motion path (DF-P06). Electron/Swift (phase 3) will consume the same pose DTO. Enabling a real LIF worker remains blocked by Q-012.

## 3. Entry criteria and inherited evidence

Phase 1 complete on [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2): 15 pytest passed, `reports/ingestion.json` synthetic, policy `real_graph_enabled: false`.

## 4. Scope

- `backend/flysim/clock.py` — monotonic presentation clock; no catch-up after stalls
- `backend/flysim/world.py` — pose + locomotion + Find fly; geometry courtesy; no reward/needs
- `backend/flysim/authored.py` — authored animation controller driven by the presentation clock
- `backend/flysim/lif.py` — device probe stubs + `start_lif_worker` that refuses when the graph flag is false
- Tests for locomotion transitions, Find fly without a neural worker, and LIF start refusal
- Update foundations check + phase-1 plan completion evidence

## 5. Non-goals

Electron overlay, Swift helper, MPS timing certification, real-graph enable, invented aversion blacklist, food/sleep/affect.

## 6. Current-state audit

Phase 1 ingest/review compiler present. No world/clock/LIF modules yet. `config/desktop-pet.json` already declares authored animation as the live path.

## 7. Assumptions, constraints, risks, and decisions

- Authored motion is presentation, not connectome control (record in operator copy later).
- Linux validates logic only; Mac overlay remains deferred.
- LIF code may exist behind the flag; starting it must raise while Q-012 holds.

## 8. Dependencies

Phase 1 ingest. Phase 3 depends on the pose contract from this phase.

## 9. Architecture and affected systems

Presentation clock owns authored ticks. World pose fields match the handover LiveFrame pose subset: `x`, `y`, `headingRad`, `speedPointsS`, `displayId`, `hostSurfaceId`, `depth01`, `locomotion`. Neural worker remains unstarted.

## 10. Files and paths in scope

- `backend/flysim/clock.py`, `world.py`, `authored.py`, `lif.py`
- `backend/tests/test_authored_motion.py`
- `docs/plans/phase_1_safe_ingest_plan.md` (complete)
- `docs/plans/phase_2_authored_motion_plan.md`
- `.cursor/STATE.md`, continuation memory
- `scripts/check-foundations.mjs`

## 11. Supporting documents

This plan; phase-1 completion evidence; workstream status update.

## 12. Ordered implementation tasks

1. Write this plan (done when committed).
2. Implement clock / world / authored / lif gate.
3. Add tests; run pytest + foundations check.
4. Mark phase 1 complete; update STATE.
5. Commit and push to the same PR branch.

## 13. Adaptive role map

| Role ID | Required or skipped | Reason | Status |
|---|---|---|---|
| `product-manager-subagent` | required | DF-P06 authored path | inherited from phase 0 |
| `ui-ux-developer-subagent` | required | Find-fly / locomotion language | inherited |
| `software-engineer-subagent` | required | implement modules | active |
| `security-engineer-subagent` | required | LIF cannot start; no neural authority | review after tests |
| `growth-marketing-subagent` | skipped | no launch/acquisition | skipped |
| `project-lead-subagent` | required | reconcile on PR | after push |

## 14. Test and validation matrix

| Requirement | Method | Expected |
|---|---|---|
| Policy stays false | pytest | `real_graph_enabled is False` |
| Idle→crawl→flight | pytest | finite states only |
| Find fly | pytest | works with worker stopped |
| LIF start | pytest | raises while flag false |
| Foundations | `node scripts/check-foundations.mjs` | pass |

## 15. Security / privacy / reliability

No screen capture. No neural tool authority. Hard refusal to start LIF. No affect/needs variables.

## 16. Environment-variable registry

| Variable | Purpose | Status |
|---|---|---|
| `PYTORCH_ENABLE_MPS_FALLBACK` | must stay unset if LIF ever runs | deferred; not required for authored path |

## 17. Deferred human-action queue

| Action | Blocking now? |
|---|---|
| Mac overlay verification | no |
| Q-012 reframing | no for authored path |
| Template license review | no |

## 18. Rollback

Revert this commit on the PR branch; policy remains false either way.

## 19. Acceptance criteria

- Authored controller advances pose on the presentation clock
- Find fly reveals without starting LIF
- `start_lif_worker` refuses while `real_graph_enabled` is false
- Tests + foundations check pass on Linux

## 20. Completion evidence

- `PYTHONPATH=backend python3 -m pytest -q backend/tests` → **23 passed**
- `node scripts/check-foundations.mjs` → passed
- `node .cursor/skills/launch-pipeline/scripts/preflight.mjs` → READY
- `start_lif_worker()` raises while `real_graph_enabled` is false
- Find fly reveals without `neural_worker_running`

## 21. Deviations and follow-ups

Electron/Swift deferred to phase 3. Inert LIF is a gate stub, not a full MPS kernel. ManagePullRequest updates failed in this multi-repo agent workspace; commits still push to PR #2.

## 22. Next Plan Generation Prompt

After this phase is verified, generate exactly one plan at `docs/plans/phase_3_electron_swift_shell_plan.md` for the Electron overlay and Swift DesktopContext helper. Do not implement it until that plan exists. Keep `real_graph_enabled` false.
