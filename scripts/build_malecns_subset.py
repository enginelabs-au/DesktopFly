#!/usr/bin/env python3
"""Build a bounded, reviewed MaleCNS runtime subset from the full export.

The desktop controller must not silently fall back from a full graph to an
arbitrary sample. This builder records the exact deterministic selection in
the subset metadata and keeps every runtime neuron in the source review table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
FULL_META = DERIVED / "malecns-full-meta.json"
FULL_NEURONS = DERIVED / "malecns-full-neurons.parquet"
FULL_EDGES = DERIVED / "malecns-full-edges.parquet"
FULL_REVIEW = DERIVED / "malecns-full-review.parquet"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _chunks(values: list[str], size: int) -> Iterable[set[str]]:
    for offset in range(0, len(values), size):
        yield set(values[offset : offset + size])


def _require_inputs() -> None:
    missing = [
        path
        for path in (FULL_META, FULL_NEURONS, FULL_EDGES, FULL_REVIEW)
        if not path.is_file()
    ]
    if missing:
        names = ", ".join(str(path.relative_to(ROOT)) for path in missing)
        raise FileNotFoundError(
            f"full MaleCNS export is incomplete; missing: {names}. "
            "Run scripts/download_malecns.py and scripts/build_malecns_full.py."
        )


def _reviewed_ids() -> set[str]:
    table = pq.read_table(FULL_REVIEW, columns=["neuron_id", "decision"])
    return {
        str(neuron_id)
        for neuron_id, decision in zip(
            table.column("neuron_id").to_pylist(),
            table.column("decision").to_pylist(),
            strict=True,
        )
        if decision == "include"
    }


def _select_ids(max_neurons: int, hops: int) -> tuple[list[str], dict]:
    meta = _read_json(FULL_META)
    reviewed = _reviewed_ids()
    seeds = sorted(
        {
            str(row["neuron_id"])
            for row in [*meta.get("sensory_map", []), *meta.get("motor_map", [])]
            if str(row["neuron_id"]) in reviewed
        }
    )
    if not seeds:
        raise ValueError("full graph has no reviewed sensory or motor seed IDs")
    if len(seeds) > max_neurons:
        raise ValueError("max_neurons is smaller than the reviewed seed pool")

    selected = list(seeds)
    selected_set = set(selected)
    parquet = pq.ParquetFile(FULL_EDGES)
    for hop in range(1, hops + 1):
        if len(selected) >= max_neurons:
            break
        candidates: set[str] = set()
        for batch in parquet.iter_batches(
            batch_size=1_000_000, columns=["pre_id", "post_id"]
        ):
            pre = batch.column("pre_id").to_pylist()
            post = batch.column("post_id").to_pylist()
            for pre_id, post_id in zip(pre, post, strict=True):
                pre_id = str(pre_id)
                post_id = str(post_id)
                if pre_id in selected_set and post_id in reviewed:
                    candidates.add(post_id)
                elif post_id in selected_set and pre_id in reviewed:
                    candidates.add(pre_id)
        for neuron_id in sorted(candidates):
            if neuron_id not in selected_set:
                selected.append(neuron_id)
                selected_set.add(neuron_id)
                if len(selected) >= max_neurons:
                    break

    selection = {
        "method": "reviewed sensory/motor seeds plus bounded undirected edge hops",
        "hops": hops,
        "max_neurons": max_neurons,
        "seed_count": len(seeds),
        "selected_count": len(selected),
        "source_full_meta": str(FULL_META.relative_to(ROOT)),
        "review_filter": "decision == include",
    }
    return selected, selection


def build_subset(max_neurons: int, hops: int) -> Path:
    _require_inputs()
    selected, selection = _select_ids(max_neurons, hops)
    selected_set = set(selected)
    neuron_table = pq.read_table(FULL_NEURONS)
    neuron_mask = pc.is_in(
        neuron_table.column("neuron_id"), value_set=pa.array(selected)
    )
    neurons = neuron_table.filter(neuron_mask)

    edge_table = pq.read_table(FULL_EDGES)
    edge_mask = pc.and_(
        pc.is_in(edge_table.column("pre_id"), value_set=pa.array(selected)),
        pc.is_in(edge_table.column("post_id"), value_set=pa.array(selected)),
    )
    edges = edge_table.filter(edge_mask)

    review_table = pq.read_table(FULL_REVIEW)
    review_mask = pc.is_in(
        review_table.column("neuron_id"), value_set=pa.array(selected)
    )
    review = review_table.filter(review_mask)

    meta = _read_json(FULL_META)
    sensory_map = [
        row for row in meta.get("sensory_map", []) if row["neuron_id"] in selected_set
    ]
    motor_map = [
        row for row in meta.get("motor_map", []) if row["neuron_id"] in selected_set
    ]

    out_neurons = DERIVED / "malecns-subset-neurons.parquet"
    out_edges = DERIVED / "malecns-subset-edges.parquet"
    out_review = DERIVED / "malecns-subset-review.parquet"
    out_meta = DERIVED / "malecns-subset-meta.json"
    pq.write_table(neurons, out_neurons)
    pq.write_table(edges, out_edges)
    pq.write_table(review, out_review)
    out_meta.write_text(
        json.dumps(
            {
                "dataset": meta["dataset"],
                "source_annotation_revision": meta["source_annotation_revision"],
                "fixture_kind": "malecns-reviewed-subset",
                "neuron_count": neurons.num_rows,
                "edge_count": edges.num_rows,
                "sensory_map": sensory_map,
                "motor_map": motor_map,
                "provenance": meta.get("provenance", {}),
                "selection": selection,
                "neurons_path": out_neurons.name,
                "edges_path": out_edges.name,
                "review_path": out_review.name,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "meta": str(out_meta.relative_to(ROOT)),
                "neuron_count": neurons.num_rows,
                "edge_count": edges.num_rows,
                "selection": selection,
            },
            indent=2,
        )
    )
    return out_meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-neurons", type=int, default=1024)
    parser.add_argument("--hops", type=int, default=1)
    args = parser.parse_args()
    if args.max_neurons < 1 or args.hops < 1:
        raise SystemExit("--max-neurons and --hops must be positive")
    build_subset(args.max_neurons, args.hops)


if __name__ == "__main__":
    main()
