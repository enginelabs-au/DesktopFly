# backend

Python 3.12 flysim package. `flysim/__init__.py` is empty so importing the supervisor later does not initialize PyTorch.

Neural enabled: `real_graph_enabled: true`. LIF starts with a provided `StaticGraph` (synthetic in CI). MaleCNS feather load fails with `FileNotFoundError` until downloaded.

```bash
python3 -m venv .venv
.venv/bin/pip install 'numpy>=2,<3' 'pytest>=8,<10'
PYTHONPATH=backend .venv/bin/python -m pytest -q
```
