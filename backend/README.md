# backend

Python 3.12 flysim package. `flysim/__init__.py` is empty so importing the supervisor later does not initialize PyTorch.

Phase 1 adds `flysim/ingest.py` and a synthetic three-node fixture. `real_graph_enabled` stays false. Do not start a LIF worker until Q-012 is withdrawn.

```bash
python3 -m venv .venv
.venv/bin/pip install 'numpy>=2,<3' 'pytest>=8,<10'
cd backend && ../.venv/bin/python -m pytest -q
```
