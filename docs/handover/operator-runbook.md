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
