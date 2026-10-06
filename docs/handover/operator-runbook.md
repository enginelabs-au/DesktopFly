# Operator runbook (DesktopFly)

Connectome-informed macOS desktop pet. **Healthy** means software checks pass — not feelings or consciousness.

## Setup

```bash
# Backend
cd backend && uv sync --frozen --group dev
python ../scripts/download_malecns.py   # MaleCNS feathers → data/raw/ (gitignored)

# Checks (Linux or Mac)
node ../scripts/check-foundations.mjs
PYTHONPATH=. uv run pytest -q
node --test ../src/pet/*.test.mjs ../src/live/*.test.mjs ../src/telemetry/*.test.mjs ../src/workbench/*.test.mjs ../desktop/desktop.test.mjs ../desktop/capabilities/*.test.mjs
```

## Start / pause / stop

- **Start:** Electron main (`desktop/`) starts the session; neural worker starts when `real_graph_enabled` and a graph are available.
- **Pause:** Tray/menu Pause or bridge `pause` — no modeled deterioration while paused.
- **Stop:** Tray STOP sets the supervisor stop latch immediately (not via React). No auto-restart after hard fault.
- **Late timing moments (owner-approved 2026-10-06):** the 4 ms per-block budget is unchanged. On macOS an idle background process is occasionally woken late, so an isolated slow block (measured: about 1 in 1,500-6,000) is counted and shown on the Health card ("on time, with N brief late moments") instead of stopping the fly. Simulated time is not caught up for it. The fly still stops permanently, with no automatic resume, if more than 2 blocks in a row are late, more than 6 are late within one second, or any single block is stalled for over 250 ms (the same limit as the app's own separate supervisor). Real compute is checked separately and strictly: if a block actually uses more than 4 ms of CPU time the fly stops immediately, with no tolerance. Measured on this Mac: 41 of 44,250 blocks were slow on the wall clock, and every one had under 2.3 ms of CPU time, so they were the OS pausing the process, not neural compute. These are fixed values in `config/policy.json` (`late_block_*`); nothing adjusts them at runtime, and `recovery.allow_threshold_relaxation` stays `false`. Setting them to `0` restores the strict "any late block stops the fly" rule.
- **Slow blocks are logged, not fatal; planned 5-minute clean start (owner-approved 2026-10-06, second decision):** a 5-minute test on a busy Mac (load about 6) still stopped the fly after 3 slow blocks in a row (10 ms against 4 ms) while compute time was fine. The owner chose to remove the wall-clock stop. `config/policy.json` now sets `late_block_wall_fault: false`: slow blocks are still counted and shown on the Health card ("only logged, not a stop"), but the count, in-a-row and per-second limits no longer stop the fly. Two stops stay in force: the strict CPU-time check (a block that really uses more than 4 ms of compute stops the fly at once) and the app's separate supervisor, which stops the fly if one tick takes over 0.25 s. Setting `late_block_wall_fault` back to `true` restores the earlier limits. Separately, `scheduled_state_reset_s: 300` gives the neurons a planned clean start from the reviewed initial state after each 5 minutes of the fly's own simulated time. It does not change any weight, does not run after a fault, never clears a stop, and is not a recovery step; the Health technical details show how many planned restarts have happened.

## Find fly / Find cursor

Authored presentation path works even if the neural worker is stopped. Find fly recenters on the focused window or open space.

## Health

Open **Health…** → `src/telemetry/health.html`. Menu-bar status should mirror supervisor plain-language titles. Technical details are expandable.

## Permissions

- Accessibility: only for precise window geometry; denial → open-space / simpler scene.
- Screen Recording: off by default (`screen_capture_enabled: false`).
- Local vision is enabled only after the explicit menu action **Enable local
  vision…**. It samples a small screen thumbnail in Electron's main process
  and forwards only bounded brightness, color-bias, and motion numbers.
  Denial or staleness returns to geometry-only behavior.
- Screen pixels, OCR, window titles, URLs, arbitrary text, and plugin output
  never enter neural state. “Neutral contact” means a bounded landing/
  inspection presentation state, not eating, reward, need, or collection.
- No microphone/camera/contacts.

## Dataset

Default **MaleCNS v1.0**. FlyWire is a separate adapter and must not mix IDs. Synthetic fixtures remain for CI.

## Recovery

Recognized conditions only; budgets outside restorable agent state. Unknown → **Paused — needs review**.

## Mac proof

See `docs/handover/mac-verification-runbook.md`.
- **Behaviour comes from the network (owner-approved 2026-10-06, third decision):** in connectome mode no code decides where or how the fly moves. Removed: the sine-wave drive, walk onset and inertia shaping, edge steering, the cursor flee rule, and the flight label. What remains in code is only: the screen clamp, a speed ceiling (`max_speed_points_s`), the stop latch and supervisors, and the constant inputs in `config/policy.json` (`resting_drive: 1.0`, `intrinsic_noise_amplitude: 1.0`, `intrinsic_noise_seed: 7`, recorded model assumptions; with both at 0 the network is silent and the fly does not move). Distances to the cursor and screen edges, on the fly's left and right, are measured as plain numbers (0 to 1) and fed into the network through a fixed, engineered, non-anatomical wiring (`backend/flysim/sensory.py`, `world_bridge_rows`). The wiring was not tuned for any behaviour. The left/right/forward readout is also engineered, not real motor neurons. Measured on this subset (256 neurons): with no world input the fly walks at a steady 55 to 60 points/s on a gently curving path and never pauses; a cursor on one side speeds it up and turns it away (cursor on its left turns it right; on its right turns it left); a left screen edge turns it right, while a right edge speeds it up and also turns it right. This is what the reviewed subset does, not a designed fly-like repertoire. The authored (non-connectome) mode is unchanged and still uses its bounded cursor-yield geometry rule.
