# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. Health and workbench open only on request.

**Neural / LIF simulation is enabled** (`real_graph_enabled: true`). Authored animation remains for Find fly / presentation fallback. MaleCNS feathers download via `scripts/download_malecns.py` (gitignored under `data/raw/`).

Default dataset: **MaleCNS v1.0**. Shell: **Electron + Swift helper**.

## Start here

- Product spec: [`docs/handover/fruit-fly-cursor-handover.md`](docs/handover/fruit-fly-cursor-handover.md)
- Operator runbook: [`docs/handover/operator-runbook.md`](docs/handover/operator-runbook.md)
- Mac verification (Cam): [`docs/handover/mac-verification-runbook.md`](docs/handover/mac-verification-runbook.md)
- Final checklist: [`docs/plans/final_implementation_checklist.md`](docs/plans/final_implementation_checklist.md)

## Local checks

```bash
node .cursor/skills/launch-pipeline/scripts/preflight.mjs
bash .cursor/scripts/bootstrap.sh
node scripts/check-foundations.mjs
cd backend && uv sync --frozen --group dev
PYTHONPATH=. uv run pytest -q
cd ..
node --test src/pet/*.test.mjs src/live/*.test.mjs src/telemetry/*.test.mjs src/workbench/*.test.mjs desktop/desktop.test.mjs desktop/capabilities/*.test.mjs
```

## MaleCNS setup

```bash
python scripts/download_malecns.py
# writes data/raw/*.feather + provenance/malecns-v1.0.json
```
