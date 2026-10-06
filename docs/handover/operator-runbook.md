# Operator runbook (DesktopFly)

Connectome-informed macOS desktop pet. **Healthy** means software checks pass — not feelings or consciousness.

## Setup

```bash
# Backend
cd backend && uv sync --frozen --group dev
python ../scripts/download_malecns.py   # MaleCNS feathers → data/raw/ (gitignored)
PYTHONPATH=. uv run python ../scripts/build_malecns_live_subset.py   # live slice tables → data/derived/ (gitignored; required by policy "live")
PYTHONPATH=. uv run python ../scripts/build_malecns_fullbrain.py     # optional whole-brain tables (596 MB) for reviewed_subset_name "fullbrain"

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
- **Body model (2026-10-07, owner request):** the pet runs a bout model, not the connectome readout and not a fixed timer. Walk, turn, stop, groom, and flight each draw a new length from a heavy-tailed distribution when the bout starts (flights about 0.6–20 s). A cursor inside `cursor_yield_radius_points`, or one closing inside 1.6× that radius, starts a flight; the screen edge can end it early. Stops often become a groom. Contrast in the thumbnail biases turns. The connectome still receives the cursor as eye numbers. This is geometry, not a claim of experience.
- **Whole brain measured (2026-10-07):** the whole MaleCNS graph now runs as a compiled, spike-sparse kernel (`backend/flysim/lif_fused.py`, 155,802 neurons with an agreed sign, 23.5 M edges, `reviewed_subset_name: "fullbrain"`, cold start about 19 s, 8 threads). A 5 ms slice takes about 2 ms in the dark and 3.5–3.8 ms with a whole eye darkened, with worst blocks over 4 ms during strong stimulation. It is **not** the default because it does not behave: with the reviewed weight normalisation the motor neurons never fire; with the published per-synapse weights the brain is silent until any stimulus and then about 1.5 % of neurons fire forever with every motor channel saturated. No stimulus-driven regime was found without inventing cell-specific parameters (`reports/full-brain-spike-timing.json`). For the parallel kernel the 4 ms check uses wall time, because the main thread's CPU time does not include the worker threads.
- **Live slice, not the whole brain (2026-10-06):** this Mac (M2 Max, 64 GB) cannot run the full MaleCNS graph in real time. A spike-only step of all 211,577 neurons stays under 4 ms only while almost nothing is firing; at half a percent of neurons firing a 5 ms slice takes 6.8 ms (report: `reports/full-brain-spike-timing.json`). The live pet uses a 4,714-neuron, 55,733-edge slice (`reviewed_subset_name: "live"`): retinal hex neurons that synapse onto LC4/LPLC2, those detectors, the descending neurons they contact, and the motor neurons those contact. Signs are included only when the neurotransmitter label agrees (glutamate inhibitory is an assumption; unclear, conflicting, and modulatory labels are left out). The cursor, and the screen thumbnail when vision is on, is a retinal grid (`hex_side_h1_h2`): hex1 is bearing, hex2 is distance. Leg-nerve motor neurons set speed and same-side turn. Wing-nerve motor neurons and the giant fiber set the wing number only. Measured: still with no input; a full right-eye image reaches about 22–33 points/s, turn about −1.25 rad/s, takeoff near 1; a full left-eye image does not recruit the motor neurons in this slice. Quiet blocks are about 0.6 ms. The picture of legs and wings is a drawing.
