---
plan: phase_3_electron_swift_shell
status: complete
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: docs/plans/phase_2_authored_motion_plan.md
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
blueprint: docs/blueprints/2026-09-16_desktopfly.md
---

# Phase 3: Electron overlay + Swift DesktopContext

## 1. Objective

Build the macOS desktop-pet shell: frameless transparent click-through Electron window, Swift helper scaffold, menus, tray, and host lease — with **neural / LIF enabled** (Cam override of Q-012 gate, 2026-09-16).

## 2. Cam override

`real_graph_enabled: true`. LIF start refused only for technical blockers (missing graph/weights), not policy.

## 3. Completion evidence

- `desktop/main.mjs`, `preload.cjs`, `pet-window.mjs`, `host-lease.mjs`, `menus.mjs`, `focus.mjs`, `policy-gate.mjs`, `renderer/pet.*`
- `native/DesktopContext/` Swift package + `ipc-protocol.json`
- `reports/desktop-shell.json`
- Decision: `docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md`
- Validation: pytest 28; node desktop+pet 10; foundations check passed
- Technical blockers recorded: MaleCNS feather not downloaded; Electron GUI / AppKit not run on Linux CI

## 4. Next Plan Generation Prompt

Read `/AGENTS.md`, core agent context, `/instructions/PROJECT_PLANNING.md`, this completed phase-3 plan, workstream, and current repo state. Generate exactly one next plan at `docs/plans/phase_4_supervisor_health_plan.md` for plain-language health, independent supervisor, stop latch, and bounded recovery — with neural enabled. Do not implement until that plan is written.
