---
checklist: final_implementation
status: ready_for_cam_review
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_4_supervisor_health_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Final implementation checklist (DesktopFly)

Neural / LIF **enabled**. Agent closeout finished everything that does not need Cam.

## Done in-repo (agent)

- [x] Phase 0–4 Linux scaffolds + handover closeout modules
- [x] `backend/flysim/config.py` (Pydantic frozen policy)
- [x] `backend/flysim/adapters/` MaleCNS + FlyWire blocker adapter
- [x] `sensory.py` + `motor.py`
- [x] Full Torch/pandas/pyarrow/websockets/pydantic/safetensors + committed `uv.lock`
- [x] `src/live/`, `src/telemetry/` (health UI), `src/workbench/`
- [x] `desktop/capabilities/`, `desktop/connectors/`, `layers.mjs`, `scene.mjs`
- [x] MaleCNS download script + local feathers + `provenance/malecns-v1.0.json` (feathers gitignored)
- [x] MaleCNS v1.0 downloaded locally and full derived graph built — 211,577 neurons / 26,028,386 edges; `data/derived/malecns-full-meta.json`
- [x] Bounded reviewed MaleCNS runtime subset built — 256 neurons / 2,021 edges; `data/derived/malecns-subset-meta.json`
- [x] Local timing report passes the 4 ms block budget on the configured subset; full-graph timing remains unsuitable — `reports/connectome-timing.json`
- [x] Bounded full-connectome diagnostic launcher — `scripts/run-full-sim.sh`
- [x] FlyWire v783 proofread connectivity and v3.2.0 annotations downloaded, checksummed, and materialized — 15,091,983 aggregated pairs / 139,248 annotations; separate `flywire:` namespace
- [x] Asyncio loopback WebSocket bridge
- [x] Device report (`reports/device.json`) — MPS unavailable on Linux CI
- [x] CPU fallback disabled for the desktop profile; missed neural deadlines permanently stop the worker
- [x] Mac verification runbook: `docs/handover/mac-verification-runbook.md`
- [x] Linux tests green

## Cam-only remaining

- [x] Run Mac Electron pet GUI per runbook (click-through, host lease, tray Stop) — verified 2026-09-16; reports/mac-verification.json
- [x] Build/run `native/DesktopContext` with AppKit — `swift build`/`swift run` PASS; AX off until geometry profile enabled
- [x] Confirm Torch **MPS** probe on Cam’s Mac (`reports/mac-verification.json`) — mps selected, probe_ok
- [ ] Optional: Screen Recording only if screen-vision profile enabled later
- [ ] Legal/license review of cobanov template (recorded, not lawyer-reviewed)
- [ ] Full MaleCNS graph performance optimization and biological circuit validation

## Not Cam-blocked

- Raw MaleCNS and FlyWire files remain gitignored and are reproducible through the two downloader scripts.
- FlyWire remains a separate adapter and is not mixed into the default MaleCNS runtime graph.

## Neural policy

- Enabled. Refuse start only for hard technical blockers.
- Neural output must not authorize connectors.
