# Mac verification runbook (Cam-blocked on Linux CI)

This cloud agent host is **Linux x86_64**. Electron GUI, AppKit, and MPS cannot be proven here.
Everything below is prepared on the branch; Cam runs it on a Mac.

## Prerequisites

1. macOS with Apple Silicon (or Intel + verified CPU profile).
2. Clone `cursor/phase-0-foundations-a5d1` / PR #2.
3. Node 20+, Python 3.12, `uv`, Xcode CLT.

## Backend

```bash
cd backend
uv sync --frozen --group dev
uv run python ../scripts/download_malecns.py   # if data/raw empty
uv run python ../scripts/build_malecns_full.py   # fills data/derived (~200k neurons; first run is slow)
uv run python -c "from flysim.presentation import ConnectomePresentationEngine; from flysim.config import load_policy_dict; e=ConnectomePresentationEngine.create(load_policy_dict()); print(e.status())"
uv run python -c "from flysim.device import report_device; from flysim.config import load_policy_dict; print(report_device(load_policy_dict()))"
PYTHONPATH=. uv run pytest -q
```

Expected on Mac with MPS: `selected` contains `mps`, `probe_ok: true`.  
If MPS unavailable: set an **explicit** CPU profile in a local override (do not enable hidden `PYTORCH_ENABLE_MPS_FALLBACK=1`).

## Electron pet

```bash
cd desktop
npm install electron --no-save   # or project-local install
npx electron .
```

Checklist:

- [ ] Frameless transparent click-through pet visible
- [ ] Click/drag passes through to apps beneath
- [ ] Host lease survives closing Health/Workbench
- [ ] Tray **Stop** latches supervisor independently of renderer
- [ ] Find fly works with neural worker stopped or running
- [ ] Health… opens `src/telemetry/health.html`

## Swift DesktopContext

```bash
cd native/DesktopContext
swift build
swift run DesktopContext
```

Checklist:

- [ ] Helper starts and speaks IPC protocol v1
- [ ] Accessibility only when geometry profile enabled; denial falls back to open-space
- [ ] Screen Recording never requested unless screen-vision enabled

## Sign-off

Record macOS version, chip, PyTorch version, MPS probe JSON, and Electron version in `reports/mac-verification.json` (Cam creates after run).
