# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. Health and workbench open only on request.

**Neural / LIF simulation is enabled** (`real_graph_enabled: true`). Authored animation remains for Find fly / presentation fallback. MaleCNS feathers download via `scripts/download_malecns.py` (gitignored under `data/raw/`).

Default dataset: **MaleCNS v1.0**. Shell: **Electron + Swift helper**.

## Licenses and attribution

DesktopFly is a **modified** derivative of [fly-connectome-template](https://github.com/cobanov/fly-connectome-template) by [Mert Cobanov](https://github.com/cobanov), licensed under the **Cobanov Template Attribution License 1.0** ([`LICENSE.fly-connectome-template`](LICENSE.fly-connectome-template), [upstream LICENSE](https://github.com/cobanov/fly-connectome-template/blob/main/LICENSE)).

**Required template credit** (README and workbench UI):

Built with [fly-connectome-template](https://github.com/cobanov/fly-connectome-template) by [Mert Cobanov](https://github.com/cobanov).

Connectome tables downloaded for the default graph path come from **Male CNS v1.0**, **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** ([`LICENSE.maleCNS`](LICENSE.maleCNS), [official download page](https://male-cns.janelia.org/download/)). Provenance: [`provenance/malecns-v1.0.json`](provenance/malecns-v1.0.json).

Full index: [`docs/attribution-and-licenses.md`](docs/attribution-and-licenses.md) and [`NOTICE`](NOTICE).

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
