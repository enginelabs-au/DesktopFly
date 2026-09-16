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
- [x] Asyncio loopback WebSocket bridge
- [x] Device report (`reports/device.json`) — MPS unavailable on Linux CI
- [x] Mac verification runbook: `docs/handover/mac-verification-runbook.md`
- [x] Linux tests green

## Cam-only remaining

- [x] Run Mac Electron pet GUI per runbook (click-through, host lease, tray Stop) — verified 2026-09-16; reports/mac-verification.json
- [x] Build/run `native/DesktopContext` with AppKit — `swift build`/`swift run` PASS; AX off until geometry profile enabled
- [x] Confirm Torch **MPS** probe on Cam’s Mac (`reports/mac-verification.json`) — mps selected, probe_ok
- [ ] Optional: Screen Recording only if screen-vision profile enabled later
- [ ] Legal/license review of cobanov template (recorded, not lawyer-reviewed)
- [ ] Owner merge of [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2)

## Not Cam-blocked

- MaleCNS feathers downloaded on agent host and hashed; re-run `python scripts/download_malecns.py` on Cam’s machine if `data/raw/` empty.
- FlyWire files not downloaded (separate adapter; missing files correctly hard-fail until pinned).

## Neural policy

- Enabled. Refuse start only for hard technical blockers.
- Neural output must not authorize connectors.
