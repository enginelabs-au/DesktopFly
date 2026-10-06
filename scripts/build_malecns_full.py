#!/usr/bin/env python3
"""Build data/derived full MaleCNS connectome (all annotated neurons)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from flysim.malecns_full_build import write_full_derived  # noqa: E402


def main() -> int:
    try:
        meta = write_full_derived()
    except FileNotFoundError as exc:
        print(f"blocker: {exc}", file=sys.stderr)
        print("Run: python scripts/download_malecns.py", file=sys.stderr)
        return 1
    print(f"wrote {meta}")
    payload = meta.read_text(encoding="utf-8")
    if "neuron_count" in payload:
        import json

        data = json.loads(payload)
        print(f"neuron_count={data.get('neuron_count')} edge_count={data.get('edge_count')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
