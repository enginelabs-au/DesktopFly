---
plan: phase_4_supervisor_health
status: planned
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_3_electron_swift_shell_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Phase 4: Supervisor, health language, recovery

## 1. Objective

Implement the independent supervisor, plain-language health mapping, stop latch, and bounded recovery recipes from the handover. Neural / LIF remains **enabled** (`real_graph_enabled: true`). Neural output still must not authorize connectors.

## 2. Entry criteria

- Phase 3 complete: Electron modules + Swift scaffold + host lease; Linux unit tests green.
- Cam neural enable in force.

## 3. Scope

- `backend/flysim/supervisor.py`, `health.py`, `recovery.py`, `checkpoints.py`, `bridge.py`, `worker.py` (handover contracts)
- `config/recovery-profiles.json`, `config/state-contract.json` already present — wire them
- Plain-language operator strings (“Healthy — checks look normal”)
- Hard fault → latched stop; no auto-restart
- Bounded known-condition recovery only
- Reports under `reports/`

## 4. Non-goals

- Inventing affect/reward/needs
- Relaxing connector authority
- Claiming Mac MPS certification from Linux
- Downloading MaleCNS without recording hash (do that as a technical prerequisite if needed)

## 5. Technical blockers to surface

- Missing MaleCNS feather under `data/raw/`
- Torch/MPS availability on target Mac
- AppKit compile / Accessibility permission on Cam’s machine

## 6. Acceptance criteria

- Supervisor owns stop latch independently of Electron renderer
- Health copy is plain language; no sentience claims
- Recovery budgets outside restorable agent state
- Tests for latch, known recovery, unknown → review-required
- Foundations + pytest + node checks remain green

## 7. Completion evidence

_Not started — plan only._

## 8. Next

After verification, create `docs/plans/final_implementation_checklist.md` for remaining Mac-only and human actions.
