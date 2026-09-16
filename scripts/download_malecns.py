#!/usr/bin/env python3
"""Download and pin MaleCNS v1.0 feathers (setup only; not runtime)."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROVENANCE = ROOT / "provenance" / "malecns-v1.0.json"

FILES = [
    {
        "filename": "body-annotations-male-cns-v1.0-minconf-0.5.feather",
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather",
    },
    {
        "filename": "body-neurotransmitters-male-cns-v1.0.feather",
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather",
    },
    {
        "filename": "connectome-weights-male-cns-v1.0-minconf-0.5.feather",
        "url": "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        print(f"skip existing {dest.name}")
        return
    print(f"download {dest.name} …")
    urllib.request.urlretrieve(url, dest)  # noqa: S310 — pinned public GCS URL


def main() -> int:
    records = []
    for item in FILES:
        dest = RAW / item["filename"]
        download(item["url"], dest)
        records.append(
            {
                "filename": item["filename"],
                "url": item["url"],
                "bytes": dest.stat().st_size,
                "sha256": sha256_file(dest),
                "dataset_version": "male-cns:v1.0",
                "license": "CC-BY-4.0",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "dataset": "male-cns:v1.0",
        "source_page": "https://male-cns.janelia.org/download/",
        "files": records,
    }
    PROVENANCE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {PROVENANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
