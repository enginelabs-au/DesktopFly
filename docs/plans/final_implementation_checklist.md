---
checklist: final_implementation
status: open
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_4_supervisor_health_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
---

# Final implementation checklist (DesktopFly)

Phases 0–4 code paths are on `cursor/phase-0-foundations-a5d1` with **neural / LIF enabled**. Remaining items are Mac-only, human, or download prerequisites.

## Done in-repo

- [x] Phase 0 foundations + policy (`real_graph_enabled: true`)
- [x] Phase 1 synthetic ingest / review compile
- [x] Phase 2 authored animation
- [x] Phase 3 Electron shell + Swift DesktopContext scaffold
- [x] Phase 4 supervisor, plain-language health, recovery budgets, checkpoints, bridge/worker scaffolds
- [x] Linux CI: foundations check, pytest, node unit tests

## Human / Mac actions (deferred)

- [ ] Download MaleCNS v1.0 feather into `data/raw/` and record hash in provenance
- [ ] Run Electron pet GUI on macOS; verify click-through and host lease
- [ ] Build/run `native/DesktopContext` with AppKit; Accessibility permission when geometry profile enabled
- [ ] Confirm Torch MPS availability on Cam’s Mac (`device: mps`, `allow_cpu_fallback: false`)
- [ ] Optional: Screen Recording only if screen-vision profile is explicitly enabled later
- [ ] Legal/license review of cobanov template (recorded, not reviewed)
- [ ] Owner merge of [DesktopFly#2](https://github.com/enginelabs-au/DesktopFly/pull/2)

## Environment variables (names only)

| Name | Purpose | Required |
|---|---|---|
| `HERMES_HOME` | N/A for DesktopFly | no |
| (none secret for Phase 0–4 CI) | Loopback token is generated per launch, not env | — |

## Technical blockers (not policy)

- MaleCNS weights file missing under `data/raw/`
- Electron GUI / AppKit not executable on Linux CI host

## Neural policy (Cam)

- Enabled. Refuse start only for hard technical blockers.
- Neural output must not authorize connectors (`capabilities.json`).
