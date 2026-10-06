#!/usr/bin/env python3
"""Download and materialize the pinned FlyWire v783 proofread tables.

The source files remain under data/raw (gitignored). The smaller canonical
tables used by the separate FlyWire adapter are written under data/derived.
FlyWire IDs are never merged into the default MaleCNS graph.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
DERIVED = ROOT / "data" / "derived"
PROVENANCE = ROOT / "provenance" / "flywire-v783.json"

CONNECTIONS_URL = (
    "https://zenodo.org/api/records/10676866/files/"
    "proofread_connections_783.feather/content"
)
CONNECTIONS_MD5 = "f48f972d262323a102aed49af1396b8a"
ANNOTATIONS_URL = (
    "https://raw.githubusercontent.com/flyconnectome/flywire_annotations/"
    "v3.2.0/supplemental_files/Supplemental_file1_neuron_annotations.tsv"
)

RAW_CONNECTIONS = RAW / "flywire-proofread_connections_783.feather"
RAW_ANNOTATIONS = RAW / "flywire-v783-neuron-annotations.tsv"
DERIVED_CONNECTIONS = DERIVED / "flywire-v783-connectivity.parquet"
DERIVED_ANNOTATIONS = DERIVED / "flywire-v783-annotations.parquet"


def digest(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 0:
        print(f"skip existing {dest.name}", flush=True)
        return
    partial = dest.with_suffix(dest.suffix + ".part")
    print(f"download {dest.name} …", flush=True)
    urllib.request.urlretrieve(url, partial)  # noqa: S310 — pinned public URLs
    partial.replace(dest)


def materialize_connections() -> None:
    if DERIVED_CONNECTIONS.is_file() and DERIVED_CONNECTIONS.stat().st_size > 0:
        print(f"skip existing {DERIVED_CONNECTIONS.name}", flush=True)
        return
    print("materialize FlyWire connectivity parquet …", flush=True)
    table = feather.read_table(RAW_CONNECTIONS)
    required = {"pre_pt_root_id", "post_pt_root_id", "syn_count"}
    missing = required - set(table.column_names)
    if missing:
        raise ValueError(f"FlyWire connections missing columns: {sorted(missing)}")
    table = table.group_by(["pre_pt_root_id", "post_pt_root_id"]).aggregate(
        [("syn_count", "sum")]
    )
    columns = {
        "dataset": pa.array(["flywire:v783"] * table.num_rows),
        "pre_id": pa.array(
            [
                f"flywire:{value}"
                for value in table.column("pre_pt_root_id").to_pylist()
            ]
        ),
        "post_id": pa.array(
            [
                f"flywire:{value}"
                for value in table.column("post_pt_root_id").to_pylist()
            ]
        ),
        "synapse_count": table.column("syn_count_sum"),
    }
    DERIVED.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(columns), DERIVED_CONNECTIONS)


def materialize_annotations() -> None:
    if DERIVED_ANNOTATIONS.is_file() and DERIVED_ANNOTATIONS.stat().st_size > 0:
        print(f"skip existing {DERIVED_ANNOTATIONS.name}", flush=True)
        return
    print("materialize FlyWire annotations parquet …", flush=True)
    table = csv.read_csv(
        RAW_ANNOTATIONS,
        parse_options=csv.ParseOptions(delimiter="\t"),
        read_options=csv.ReadOptions(autogenerate_column_names=False),
    )
    if "root_id" not in table.column_names:
        raise ValueError("FlyWire annotations missing root_id")
    columns = {
        "dataset": pa.array(["flywire:v783"] * table.num_rows),
        "neuron_id": pa.array(
            [f"flywire:{value}" for value in table.column("root_id").to_pylist()]
        ),
    }
    for source, target in (
        ("cell_type", "cell_type"),
        ("super_class", "superclass"),
        ("flow", "flow"),
        ("nerve", "nerve"),
        ("top_nt", "transmitter_label"),
        ("status", "status"),
    ):
        if source in table.column_names:
            columns[target] = table.column(source)
    DERIVED.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.table(columns), DERIVED_ANNOTATIONS)


def main() -> int:
    download(CONNECTIONS_URL, RAW_CONNECTIONS)
    actual_md5 = digest(RAW_CONNECTIONS, "md5")
    if actual_md5 != CONNECTIONS_MD5:
        raise RuntimeError(
            f"FlyWire connection checksum mismatch: {actual_md5} != {CONNECTIONS_MD5}"
        )
    download(ANNOTATIONS_URL, RAW_ANNOTATIONS)
    materialize_connections()
    materialize_annotations()
    files = []
    for path, url in (
        (RAW_CONNECTIONS, CONNECTIONS_URL),
        (RAW_ANNOTATIONS, ANNOTATIONS_URL),
        (DERIVED_CONNECTIONS, "derived from proofread_connections_783.feather"),
        (DERIVED_ANNOTATIONS, "derived from Supplemental_file1_neuron_annotations.tsv"),
    ):
        files.append(
            {
                "filename": str(path.relative_to(ROOT)),
                "url": url,
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )
    PROVENANCE.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "dataset": "flywire:v783",
                "source_release": "FlyWire v783.0",
                "annotation_release": "flywire_annotations v3.2.0",
                "license": "CC-BY-4.0",
                "source_page": "https://zenodo.org/records/10676866",
                "annotation_page": "https://github.com/flyconnectome/flywire_annotations/releases/tag/v3.2.0",
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "files": files,
                "integration": {
                    "default_runtime": False,
                    "id_namespace": "flywire:",
                    "male_cns_mix_allowed": False,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {PROVENANCE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
