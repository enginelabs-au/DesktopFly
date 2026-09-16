# backend

Python 3.12 flysim package. `flysim/__init__.py` is empty so importing the supervisor later does not initialize PyTorch.

Phase 1: ingest + review compiler + synthetic fixture.  
Phase 2: authored animation (`clock`, `world`, `authored`) and inert `lif` that cannot start while `real_graph_enabled` is false.

```bash
python3 -m venv .venv
.venv/bin/pip install 'numpy>=2,<3' 'pytest>=8,<10'
PYTHONPATH=backend .venv/bin/python -m pytest -q
PYTHONPATH=backend .venv/bin/python ../scripts/write_ingestion_report.py
PYTHONPATH=backend .venv/bin/python ../scripts/write_authored_motion_report.py
```
