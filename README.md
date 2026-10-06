# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. Health and workbench open only on request.

**Neural / LIF simulation is enabled** (`real_graph_enabled: true`) with a
bounded, reviewed MaleCNS runtime subset. Authored animation remains for Find
fly / presentation fallback. The full MaleCNS export is retained locally, but
its measured full-graph block time is not suitable for the 4 ms desktop
deadline. The guarded desktop worker stops permanently on a missed deadline;
it does not silently fall back to CPU or catch up. MaleCNS feathers download
via `scripts/download_malecns.py` (gitignored under `data/raw/`).

Default dataset: **MaleCNS v1.0**. Shell: **Electron + Swift helper**.

## Licenses and attribution

DesktopFly is a **modified** derivative of [fly-connectome-template](https://github.com/cobanov/fly-connectome-template) by [Mert Cobanov](https://github.com/cobanov), licensed under the **Cobanov Template Attribution License 1.0** ([`LICENSE.fly-connectome-template`](LICENSE.fly-connectome-template), [upstream LICENSE](https://github.com/cobanov/fly-connectome-template/blob/main/LICENSE)).

**Required template credit** (README and workbench UI):

Built with [fly-connectome-template](https://github.com/cobanov/fly-connectome-template) by [Mert Cobanov](https://github.com/cobanov).

Connectome tables downloaded for the default graph path come from **Male CNS v1.0**, **[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)** ([`LICENSE.maleCNS`](LICENSE.maleCNS), [official download page](https://male-cns.janelia.org/download/)). Provenance: [`provenance/malecns-v1.0.json`](provenance/malecns-v1.0.json). FlyWire v783 is also available as a separate, non-default female-brain adapter; its IDs are never mixed into MaleCNS.

Full index: [`docs/attribution-and-licenses.md`](docs/attribution-and-licenses.md) and [`NOTICE`](NOTICE).

## Start here

- Product spec: [`docs/handover/fruit-fly-cursor-handover.md`](docs/handover/fruit-fly-cursor-handover.md)
- Operator runbook: [`docs/handover/operator-runbook.md`](docs/handover/operator-runbook.md)
- Mac verification (Cam): [`docs/handover/mac-verification-runbook.md`](docs/handover/mac-verification-runbook.md)
- Final checklist: [`docs/plans/final_implementation_checklist.md`](docs/plans/final_implementation_checklist.md)
- Timing evidence: [`reports/connectome-timing.json`](reports/connectome-timing.json)

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

## FlyWire setup

```bash
python scripts/download_flywire.py
# writes source files to data/raw/, canonical parquet to data/derived/,
# and provenance/flywire-v783.json
```

## Runtime graph

The default policy uses `graph_mode: "reviewed_subset"` with 256 reviewed
MaleCNS neurons and 2,021 retained edges. Rebuild it reproducibly after
refreshing the full export:

```bash
cd backend
uv run python ../scripts/build_malecns_subset.py --max-neurons 256 --hops 1
uv run python ../scripts/measure_connectome_timing.py --samples 40
```

This is a connectome-informed bounded controller, not a complete or
biologically faithful fly nervous system. Full-graph execution remains an
offline experiment until it has separate timing evidence.

To run a bounded full-connectome diagnostic without changing the safe desktop
policy:

```bash
./scripts/run-full-sim.sh --blocks 5
```

The launcher uses the local full MaleCNS graph, keeps CPU fallback disabled,
limits the run to 120 blocks, and reports when blocks exceed the 4 ms desktop
budget. It is an offline diagnostic; it does not claim real-time behavior.

The desktop menu includes **Enable local vision…** as an explicit opt-in.
When permitted, Electron reduces a small screen thumbnail to bounded
brightness, color-bias, and motion features before the neural step. Screen
pixels, OCR, text, and window metadata are not forwarded to neural state.
