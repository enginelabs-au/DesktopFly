# STATE.md

## Current Objective

- DesktopFly handover is merged to `main` ([PR #2](https://github.com/enginelabs-au/DesktopFly/pull/2)). Neural enabled. Remaining work is owner-only.
- Context-loading R2 (selective activation, pack v1.4) is on `main` via PR #3 and is maintained as a separate workstream.

## Current Status

- **Product merged.** Mac GUI/AppKit/MPS proof is recorded in `reports/mac-verification.json`.
- MaleCNS v1.0 and FlyWire v783 data are downloaded locally, checksummed, materialized, and covered by the separate adapters.
- Context-optimization: implementation complete. Security gate PASS. Project lead CONDITIONAL (fresh-session W1 + owner W5).
- Hook fix [PR #6](https://github.com/enginelabs-au/DesktopFly/pull/6) is on `main`: read-only `merge-base`/`merge-tree` and paths containing `-merge-` no longer trip the identity check.
- Screen-aware fly interaction is implemented locally: opt-in coarse screen features, bounded surface contact, and an attributed fly renderer are wired into the desktop shell.
- Motion fix: the connectome motor readout now includes a bounded `turn` steering command from the existing fixed left/right gains, so the fly walks curved 2D tracks (previously a 1-D left/right rail). Cursor flee is visible but bounded (140 pt radius, 150 pt/s cap, 0.6 s bursts).
- Owner decision (2026-10-06, approved): isolated late neural blocks are tolerated and reported instead of permanently stopping the fly. Fixed policy values: more than 2 late in a row, more than 6 late within one second, or any block over 50 ms still hard-faults permanently. The 4 ms budget, no-auto-resume, and `allow_threshold_relaxation=false` are unchanged. A 120 s live run survived 1 real late block (4.7 ms).
- Owner decisions (2026-10-06, second round): late-block hard cap raised to 250 ms, then wall-clock lateness made non-fatal (`late_block_wall_fault=false`; slow blocks are counted and shown, not a stop) after a 172 s test stopped on 3 slow blocks (10 ms) under host load about 6. Kept: strict CPU-time check (over 4 ms of real compute stops the fly), the app's separate 0.25 s tick supervisor, permanent stop latch, no auto-resume. Added a planned clean start of neuron state every 300 s of simulated time (`scheduled_state_reset_s`), from the reviewed initial state, weights untouched, never after a fault. 330 s live run: no fault, 13 slow blocks (worst 7 ms) logged.
- Motion realism: neural blocks are batched per tick, motor output shaped (walk onset, inertia, rate-limited flee), window glides at about 60 Hz between 20 Hz poses, renderer has tripod gait, wing beat, and idle grooming (cosmetic only).
- Cursor interaction is now wired through bounded native cursor polling outside the neural tick; the existing cursor-yield rule applies to connectome-driven presentation without granting app-action authority.

## Project Phase

- Product phases 0-4 + handover closeout are on `main`.

## Active Plan

- `docs/plans/final_implementation_checklist.md`
- Context-optimization plan: `docs/plans/context-optimization/phase_0_foundations_plan.md`

## Active Workstream

- `docs/workstreams/20260916-desktopfly-foundations/manifest.md`
- `docs/workstreams/20260917-context-optimization/`

## Active Role and Gate

- Product validation on `main` after PR #9 (2026-10-06): backend pytest 56 passed; Node 30 passed after cursor wiring; foundations PASS; launch validation PASS; policy tests 19 passed; Electron 5-second smoke launch PASS.
- Context-optimization: `project-lead-subagent` CONDITIONAL. Owner decision pending.

## Owner Decision

- Neural enabled (Cam).
- MPS unavailable on Linux CI; documented in `reports/device.json`.
- Commits must use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Secrets must never enter the repository.
- Branch ruleset deleted by the owner; `.github/CODEOWNERS` is `* @cam-douglas`.

## Core Files Loaded

- `/instructions/LAUNCH.md`
- `/instructions/PROJECT_PLANNING.md`
- `/instructions/SUBAGENTS.md`
- `/instructions/ROLES.md`

## Active Items

- Pack v1.4: `docs/handover/agentic-context-runbook/` and `GPT-REVIEW-PROMPT.md`.
- Owner handoff: `docs/workstreams/20260917-context-optimization/delivery/owner-handoff.md`
- Cost operator setup: `docs/handover/cursor-cost-operator-setup.md`
- Dataset setup: `scripts/download_malecns.py`, `scripts/download_flywire.py`, `scripts/build_malecns_subset.py`, and `provenance/flywire-v783.json`.
- Default runtime: reviewed MaleCNS subset, 256 neurons / 2,021 edges; timing evidence is `reports/connectome-timing.json`. Full MaleCNS remains an offline graph until optimized and biologically validated.
- Full-connectome launcher: `scripts/run-full-sim.sh`; verified 211,577 neurons / 25,074,842 synapses, 86.77 s load, 178.97 ms first block, and 4 ms budget miss. It is diagnostic-only.
- Full MPS sparse-matvec optimization was measured: steady-state blocks improved to about 43–46 ms, but still miss the 4 ms budget. Full real-time execution remains unachieved; the desktop app stays on the reviewed subset.
- All former project branches are merged or superseded and have been removed from the remote.
- Screen vision is disabled by default and remains permission-gated; coarse numeric features fail closed on denial, staleness, oversize input, or invalid data. macOS Screen Recording verification is still owner-only.

## Open Blockers

- Cam-only: optional Screen Recording, template license legal review.
- Context-optimization: W1 native injection unverified until a fresh session.

## Next Actions

- Owner: fresh chat W1; W5 if needed; GPT review of pack v1.4; optional template-license legal review.

## Last Updated

- 2026-10-06: PRs #2, #6, #7, #8, and #9 merged; dataset branch removed; `main` re-validated. Guarded reviewed-subset simulation is ready for a bounded local run.
- 2026-10-06: Screen-aware interaction implementation validated locally: backend 56 passed, Node 28 passed, foundations/launch/config validation passed, policy tests 19 passed, and Electron smoke launch exited 0.
- 2026-10-06: Cursor wiring fix `f9ec613` validated with Node 30 passed and the updated Electron app restarted successfully; cursor polling remains geometry-only and bounded to a 40-point yield radius.
- 2026-10-06: backend 80 passed, Node 36 passed, foundations and launch validation PASS; 330 s soak no fault; app restarted. Visual cursor-chase feel on the real display is not yet owner-confirmed.
