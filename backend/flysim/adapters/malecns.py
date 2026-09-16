"""MaleCNS v1.0 source adapter (explicit column maps only)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW = REPO_ROOT / "data" / "raw"
DEFAULT_DERIVED = REPO_ROOT / "data" / "derived"

WEIGHTS_NAME = "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
ANNOT_NAME = "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NT_NAME = "body-neurotransmitters-male-cns-v1.0.feather"

# Explicit MaleCNS → canonical column maps (no fuzzy heuristics).
ANNOT_MAP = {
    "bodyId": "source_body_id",
    "type": "cell_type",
    "superclass": "region",
    "status": "trace_status",
}
WEIGHT_MAP = {
    "body_pre": "pre_id",
    "body_post": "post_id",
    "weight": "synapse_count",
}
NT_MAP = {
    "body": "source_body_id",
    "consensus_nt": "transmitter_label",
}


@dataclass(frozen=True)
class MaleCNSPaths:
    weights: Path
    annotations: Path
    neurotransmitters: Path


def resolve_malecns_paths(raw_dir: Path | None = None) -> MaleCNSPaths:
    root = raw_dir or DEFAULT_RAW
    paths = MaleCNSPaths(
        weights=root / WEIGHTS_NAME,
        annotations=root / ANNOT_NAME,
        neurotransmitters=root / NT_NAME,
    )
    missing = [p.name for p in (paths.weights, paths.annotations, paths.neurotransmitters) if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "MaleCNS technical blocker: missing "
            + ", ".join(missing)
            + f" under {root}. Run: python scripts/download_malecns.py"
        )
    return paths


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


class MaleCNSAdapter:
    """Convert MaleCNS feather exports into canonical neuron/edge rows."""

    dataset = "male-cns:v1.0"
    source_annotation_revision = "male-cns-v1.0-minconf-0.5"

    def __init__(self, raw_dir: Path | None = None) -> None:
        self.paths = resolve_malecns_paths(raw_dir)

    def provenance(self) -> dict[str, Any]:
        files = []
        for path in (self.paths.annotations, self.paths.neurotransmitters, self.paths.weights):
            files.append(
                {
                    "filename": path.name,
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
        return {
            "dataset": self.dataset,
            "source_annotation_revision": self.source_annotation_revision,
            "license": "CC-BY (MaleCNS / Janelia FlyEM — verify on download page)",
            "files": files,
        }

    def load_annotations(self) -> pa.Table:
        table = feather.read_table(self.paths.annotations)
        required = list(ANNOT_MAP)
        missing = [c for c in required if c not in table.column_names]
        if missing:
            raise ValueError(f"MaleCNS annotations missing columns {missing}")
        body = table.column("bodyId")
        cell_type = table.column("type")
        region = table.column("superclass")
        neuron_id = pc.binary_join_element_wise(
            pa.array(["male-cns:"] * table.num_rows),
            pc.cast(body, pa.string()),
            "",
        )
        return pa.table(
            {
                "dataset": pa.array([self.dataset] * table.num_rows),
                "neuron_id": neuron_id,
                "cell_type": cell_type,
                "region": region,
                "source_annotation_revision": pa.array(
                    [self.source_annotation_revision] * table.num_rows
                ),
                "source_body_id": body,
            }
        )

    def load_edges_for_bodies(self, body_ids: set[int]) -> pa.Table:
        """Memory-map scan weights feather; keep edges whose endpoints are in body_ids."""
        if not body_ids:
            raise ValueError("body_ids required")
        allowed = np.fromiter(body_ids, dtype=np.int64)
        allowed.sort()
        pre_parts: list[np.ndarray] = []
        post_parts: list[np.ndarray] = []
        weight_parts: list[np.ndarray] = []
        with pa.memory_map(str(self.paths.weights), "r") as source:
            try:
                reader = pa.ipc.open_file(source)
                batches = [reader.get_batch(i) for i in range(reader.num_record_batches)]
            except (pa.ArrowInvalid, ValueError):
                # Some feathers are stream-format; fall back to full column read.
                table = feather.read_table(self.paths.weights, columns=list(WEIGHT_MAP))
                batches = [table.to_batches()[i] for i in range(table.to_batches().__len__())] if False else table.to_batches()
            for batch in batches:
                names = set(batch.schema.names)
                if not {"body_pre", "body_post", "weight"} <= names:
                    raise ValueError(f"MaleCNS weights missing columns in batch {batch.schema.names}")
                pre = batch.column("body_pre").to_numpy()
                post = batch.column("body_post").to_numpy()
                weight = batch.column("weight").to_numpy()
                keep = np.isin(pre, allowed) & np.isin(post, allowed) & (weight > 0)
                if not np.any(keep):
                    continue
                pre_parts.append(pre[keep])
                post_parts.append(post[keep])
                weight_parts.append(weight[keep].astype(np.int64))
        if not pre_parts:
            return pa.table(
                {
                    "pre_id": pa.array([], type=pa.string()),
                    "post_id": pa.array([], type=pa.string()),
                    "synapse_count": pa.array([], type=pa.int64()),
                }
            )
        pre_k = np.concatenate(pre_parts)
        post_k = np.concatenate(post_parts)
        w_k = np.concatenate(weight_parts)
        return pa.table(
            {
                "pre_id": pa.array([f"male-cns:{int(x)}" for x in pre_k]),
                "post_id": pa.array([f"male-cns:{int(x)}" for x in post_k]),
                "synapse_count": pa.array(w_k),
            }
        )

    def export_canonical_subset(
        self,
        selected_body_ids: list[int],
        *,
        derived_dir: Path | None = None,
        max_edges: int = 100_000,
    ) -> dict[str, Path]:
        """Write canonical parquet tables for a reviewed body-id subset."""
        bodies = {int(x) for x in selected_body_ids}
        if not bodies:
            raise ValueError("selected_body_ids empty")
        neurons = self.load_annotations()
        body_col = neurons.column("source_body_id").to_numpy()
        mask = np.isin(body_col, np.fromiter(bodies, dtype=np.int64))
        neurons = neurons.filter(pa.array(mask))
        edges = self.load_edges_for_bodies(bodies)
        if edges.num_rows > max_edges:
            raise ValueError(
                f"subset has {edges.num_rows} edges > max_edges_initial={max_edges}; shrink review set"
            )
        out = derived_dir or DEFAULT_DERIVED
        out.mkdir(parents=True, exist_ok=True)
        neuron_path = out / "neurons.parquet"
        edge_path = out / "edges.parquet"
        feather.write_feather(neurons, out / "neurons.feather")
        # Prefer parquet names from handover canonical tables
        import pyarrow.parquet as pq

        pq.write_table(neurons, neuron_path)
        pq.write_table(edges, edge_path)
        meta = {
            "dataset": self.dataset,
            "source_annotation_revision": self.source_annotation_revision,
            "selected_body_ids": sorted(bodies),
            "neuron_count": neurons.num_rows,
            "edge_count": edges.num_rows,
            "provenance": self.provenance(),
        }
        meta_path = out / "malecns-subset-meta.json"
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        return {"neurons": neuron_path, "edges": edge_path, "meta": meta_path}
