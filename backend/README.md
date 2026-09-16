# backend

Python 3.12 flysim package. `flysim/__init__.py` is empty so importing the supervisor later does not initialize PyTorch.

Phase 1 adds ingest/review for an explicitly synthetic fixture. Phase 2 adds the authored animation controller (`authored.py` / `world.py` / `clock.py`) and an inert LIF gate (`lif.py`) that refuses to start while `real_graph_enabled` is false. MaleCNS/FlyWire loaders refuse to run. Do not start a LIF worker until Q-012 is withdrawn.

```bash
python3 -m venv .venv
.venv/bin/pip install 'numpy>=2,<3' 'pytest>=8,<10'
PYTHONPATH=backend python3 -m pytest -q backend/tests
PYTHONPATH=backend python3 scripts/write_ingestion_report.py
```
