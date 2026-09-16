---
plan: phase_1_safe_ingest
status: implementing
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_0_foundations_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Phase 1: Safe ingest and synthetic fixture

## 1. Objective

Implement handover Phase 1 **without enabling a real graph**: canonical static-graph builder, an explicitly synthetic three-node fixture, and tests. `real_graph_enabled` stays false.

## 2. Relation to project end-state

Later MaleCNS ingest can call this builder. This phase does not start LIF, download weights, or claim biological IDs.

## 3. Entry criteria and inherited evidence

Phase 0 complete: [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2), bootstrap + foundations check passed, Q-012 disable in force.

## 4. Scope

- `backend/pyproject.toml` + empty `flysim/__init__.py`
- `backend/flysim/ingest.py` (`StaticGraph`, `build_static_graph` from the handover)
- Synthetic fixture under `data/reviews/` or `backend/tests/fixtures/`
- Pytest for ID validity, blocked edges, duplicate pairs, hand-calculated weights
- Keep policy flag false; no MaleCNS download

## 5. Non-goals

Real-graph enable, LIF, Electron, MPS, FlyWire adapter, invented aversion blacklist.

## 6–8. Audit, assumptions, dependencies

Python 3.12 is on this host; `uv` is not. Use a local venv + pip with the same version floors as the handover TOML. Linux cannot certify Mac ingest of a real feather file (deferred).

## 9–12. Architecture, files, tasks

Same ingest function as the handover. Tasks: package skeleton → ingest → tests → run pytest → no policy change.

## 13. Adaptive role map

Same as phase 0. Growth remains skipped. SWE implements; SEC reviews that the flag stays false.

## 14–19. Validation and acceptance

- Tests pass on Linux
- Fixture IDs are not MaleCNS/FlyWire IDs
- `config/policy.json` still `real_graph_enabled: false`
- No connectome payload committed

## 22. Next Plan Generation Prompt

After this phase is verified, generate exactly one plan at `docs/plans/phase_2_authored_motion_plan.md` for authored pet motion plus inert LIF module. Do not implement it until that plan exists. Keep the neural worker unstarted.
