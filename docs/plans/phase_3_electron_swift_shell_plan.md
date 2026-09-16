---
plan: phase_3_electron_swift_shell
status: planned
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_2_authored_motion_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
blueprint: docs/blueprints/2026-09-16_desktopfly.md
---

# Phase 3: Electron overlay + Swift DesktopContext

## 1. Objective

Build the macOS desktop-pet shell: frameless transparent click-through Electron window, Swift helper for read-only Accessibility / optional ScreenCaptureKit, menus, tray, and host lease — driven by the **authored-animation** controller. Neural / LIF worker stays unstarted; `real_graph_enabled` stays `false`.

## 2. Relation to project end-state

This is the first native-feeling product surface. Pose comes from phase-2 authored motion (or later a gated LIF worker). Health dashboard and workbench open only on request.

## 3. Entry criteria and inherited evidence

- Phase 2 complete: `clock` / `world` / `authored` / inert `lif`; `reports/authored-motion.json`; pytest + node tests green on Linux.
- Q-012 still open → no neural enable.

## 4. Scope

- `desktop/main.ts`, `preload.ts`, `menus.ts`, `focus.ts`, `layers.ts`, `scene.ts` (handover contracts)
- Transparent pet `BrowserWindow` (256pt overlay, click-through, no focus steal)
- `native/DesktopContext/` Swift helper scaffold + IPC contract
- Wire `src/pet/` to display authored poses; Find fly without neural worker
- Host lease independent of `/health` / `/workbench` visibility
- `config/desktop-pet.json` already expanded — keep capture flags false by default
- macOS-only validation gates; Linux keeps foundations + unit tests

## 5. Non-goals

- Starting LIF / enabling real graph
- Supervisor recovery recipes (phase 4)
- Vendoring full cobanov template assets without license check
- Claiming Mac results from Linux CI

## 6. Assumptions and risks

| Item | Note |
|---|---|
| This agent environment is Linux | Implement code + Linux-safe unit tests; Mac gates deferred or run on Cam’s machine |
| Template assets | Pin remains; do not strip attribution |
| Accessibility | Read-only geometry; denial → open-space fallback |

## 7. Dependencies

Phase 2 authored controller → this shell → phase 4 supervisor/health → final checklist.

## 8. Validation (when implemented)

- Pet window creates with click-through and no focus steal (macOS)
- Find fly reveals without neural worker
- Host lease loss pauses; closing health does not
- Policy still `real_graph_enabled: false`; LIF start still refused
- Linux: typecheck/unit tests that do not require AppKit

## 9. Deferred human actions

- Run Mac acceptance on Apple Silicon
- Grant Accessibility if testing focus-follow
- Template license legal review before bundling meshes
- Q-012 reframing before neural enable

## 10. Acceptance criteria

- Electron + Swift scaffolding merged with authored pose driver
- Default path is pet + authored animation, not workbench
- No LIF worker start
- Foundations check still passes; Mac gates recorded separately

## 11. Completion evidence

_Not started — plan only._

## 12. Next Plan Generation Prompt

After phase 3 is verified, generate exactly one plan at `docs/plans/phase_4_supervisor_health_plan.md` for plain-language health, independent supervisor, stop latch, and bounded recovery recipes — still with neural sim off unless Q-012 is withdrawn. Do not implement until that plan exists.
