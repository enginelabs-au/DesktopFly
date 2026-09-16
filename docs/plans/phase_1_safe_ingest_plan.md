---
plan: phase_1_safe_ingest
status: complete
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_0_foundations_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Phase 1: Safe ingest and synthetic fixture

## 1. Objective

Implement handover Phase 1 **without enabling a real graph**: canonical static-graph builder, review compiler, explicitly synthetic fixtures, and tests. `real_graph_enabled` stays false.

## 2. Relation to project end-state

Later MaleCNS ingest can call this builder. This phase does not start LIF, download weights, or claim biological IDs.

## 3. Entry criteria and inherited evidence

Phase 0 complete: [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2), bootstrap + foundations check passed, Q-012 disable in force.

## 4. Scope (completed)

- `backend/pyproject.toml` + empty `flysim/__init__.py`
- `backend/flysim/ingest.py` (`StaticGraph`, `build_static_graph`)
- `backend/flysim/schema.py` + `backend/flysim/review.py` (table compile + refuse real loads)
- Synthetic fixtures under `backend/tests/fixtures/`
- `reports/ingestion.json` from the synthetic tables
- Pytest for ID validity, blocked edges, duplicate pairs, hand-calculated weights, JS-safe ID round-trip, mismatched revisions, clamp gains zeroed

## 5. Non-goals

Real-graph enable, LIF, Electron, MPS, FlyWire adapter, invented aversion blacklist.

## 14–20. Validation and completion evidence

- `PYTHONPATH=backend python3 -m pytest -q backend/tests` → **15 passed** (ingest suite) before phase-2 modules; full suite expanded in phase 2
- Fixture IDs use `synthetic:` prefix only
- `config/policy.json` still `real_graph_enabled: false`
- No connectome payload committed
- Foundations check includes ingest/review paths

## 21. Deviations

Full MaleCNS download/adapters deferred. Review compiler operates on JSON tables rather than parquet for the synthetic path.

## 22. Next Plan Generation Prompt

Executed: `docs/plans/phase_2_authored_motion_plan.md` written after this phase verified.
