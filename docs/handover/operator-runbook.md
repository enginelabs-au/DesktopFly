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
- **Late timing moments (owner-approved 2026-10-06):** the 4 ms per-block budget is unchanged. On macOS an idle background process is occasionally woken late, so an isolated slow block (measured: about 1 in 1,500-6,000) is counted and shown on the Health card ("on time, with N brief late moments") instead of stopping the fly. Simulated time is not caught up for it. The fly still stops permanently, with no automatic resume, if more than 2 blocks in a row are late, more than 6 are late within one second, or any single block takes over 50 ms. These are fixed values in `config/policy.json` (`late_block_*`); nothing adjusts them at runtime, and `recovery.allow_threshold_relaxation` stays `false`. Setting them to `0` restores the strict "any late block stops the fly" rule.

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
