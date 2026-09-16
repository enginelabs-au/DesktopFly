"""Build full MaleCNS v1.0 connectome tables for runtime (all annotated neurons)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.feather as feather
import pyarrow.parquet as pq

from flysim.adapters.malecns import MaleCNSAdapter, REPO_ROOT as ADAPTER_ROOT

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DERIVED = REPO_ROOT / "data" / "derived"
FULL_META = DEFAULT_DERIVED / "malecns-full-meta.json"

MODULATORY_NT = frozenset({"dopamine", "serotonin", "octopamine", "histamine"})


def _load_nt_modulatory(adapter: MaleCNSAdapter) -> set[int]:
    table = feather.read_table(adapter.paths.neurotransmitters)
    if "body" not in table.column_names or "consensus_nt" not in table.column_names:
        return set()
    bodies = table.column("body").to_numpy()
    labels = [str(x).lower() for x in table.column("consensus_nt").to_pylist()]
    mod: set[int] = set()
    for body, label in zip(bodies, labels, strict=True):
        if any(token in label for token in MODULATORY_NT):
            mod.add(int(body))
    return mod


def _region_role(region: str | None, cell_type: str | None) -> str:
    text = f"{region or ''} {cell_type or ''}".lower()
    if any(k in text for k in ("optic", "visual", "olfactory", "sensory", "photoreceptor")):
        return "sensory"
    if any(k in text for k in ("motor", "leg", "wing", "haltere", "muscle", "vnc")):
        return "readout"
    return "interneuron"


def auto_review_and_maps(
    neurons: list[dict[str, Any]],
    modulatory_bodies: set[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    reviews: list[dict[str, Any]] = []
    sensory_map: list[dict[str, Any]] = []
    motor_map: list[dict[str, Any]] = []
    sensory_ids: list[str] = []
    readout_ids: list[str] = []

    for row in neurons:
        nid = row["neuron_id"]
        body = int(row.get("source_body_id", 0))
        is_mod = body in modulatory_bodies
        role = _region_role(row.get("region"), row.get("cell_type"))
        if is_mod:
            reviews.append(
                {
                    "neuron_id": nid,
                    "decision": "exclude",
                    "modulatory_status": "yes",
                    "fixed_sign": 1,
                    "role": "none",
                    "evidence": "full-graph: consensus_nt modulatory filter",
                }
            )
            continue
        reviews.append(
            {
                "neuron_id": nid,
                "decision": "include",
                "modulatory_status": "no",
                "fixed_sign": 1,
                "role": role,
                "evidence": "full-graph: auto-review (Cam full CNS)",
            }
        )
        if role == "sensory":
            sensory_ids.append(nid)
        elif role == "readout":
            readout_ids.append(nid)

    if not sensory_ids:
        sensory_ids = [n["neuron_id"] for n in neurons[: min(512, len(neurons))]]
    if not readout_ids:
        readout_ids = [n["neuron_id"] for n in neurons[-min(512, len(neurons)) :]]

    stride = max(1, len(sensory_ids) // 64)
    for i, nid in enumerate(sensory_ids[::stride][:64]):
        sensory_map.append(
            {
                "feature_name": "ambient_drive" if i % 2 == 0 else "turn_bias",
                "neuron_id": nid,
                "fixed_gain": 0.02,
                "evidence": "full-graph engineered sensory pool",
                "mapping_kind": "engineered",
            }
        )

    channels = ("left", "right", "forward")
    stride_m = max(1, len(readout_ids) // 96)
    for i, nid in enumerate(readout_ids[::stride_m][:96]):
        motor_map.append(
            {
                "neuron_id": nid,
                "output_channel": channels[i % 3],
                "fixed_gain": 0.15,
                "evidence": "full-graph engineered motor pool",
                "mapping_kind": "engineered",
            }
        )
    return reviews, sensory_map, motor_map


def load_all_edges(adapter: MaleCNSAdapter, allowed_bodies: np.ndarray) -> pa.Table:
    """Scan connectome weights; keep edges with both endpoints in allowed_bodies."""
    allowed = np.sort(allowed_bodies.astype(np.int64, copy=False))
    pre_parts: list[np.ndarray] = []
    post_parts: list[np.ndarray] = []
    weight_parts: list[np.ndarray] = []
    table = feather.read_table(
        adapter.paths.weights, columns=["body_pre", "body_post", "weight"]
    )
    for batch in table.to_batches():
        pre = batch.column("body_pre").to_numpy(zero_copy_only=False)
        post = batch.column("body_post").to_numpy(zero_copy_only=False)
        weight = batch.column("weight").to_numpy(zero_copy_only=False)
        keep = (
            np.isin(pre, allowed)
            & np.isin(post, allowed)
            & (weight > 0)
        )
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


def _canonical_neurons(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "dataset": row["dataset"],
                "neuron_id": row["neuron_id"],
                "cell_type": row.get("cell_type"),
                "region": row.get("region"),
                "source_annotation_revision": row["source_annotation_revision"],
            }
        )
    return out


def build_full_tables(raw_dir: Path | None = None) -> dict[str, Any]:
    adapter = MaleCNSAdapter(raw_dir)
    neuron_table = adapter.load_annotations()
    neuron_rows = neuron_table.to_pylist()
    bodies = neuron_table.column("source_body_id").to_numpy()
    modulatory = _load_nt_modulatory(adapter)
    edges = load_all_edges(adapter, bodies)
    review, sensory_map, motor_map = auto_review_and_maps(neuron_rows, modulatory)
    neurons = _canonical_neurons(neuron_rows)
    return {
        "fixture_kind": "malecns-full",
        "dataset": adapter.dataset,
        "source_annotation_revision": adapter.source_annotation_revision,
        "neurons": neurons,
        "edges": edges.to_pylist(),
        "review": review,
        "sensory_map": sensory_map,
        "motor_map": motor_map,
    }


def write_full_derived(
    raw_dir: Path | None = None,
    derived_dir: Path | None = None,
) -> Path:
    derived = derived_dir or DEFAULT_DERIVED
    derived.mkdir(parents=True, exist_ok=True)
    tables = build_full_tables(raw_dir)
    neurons = pa.Table.from_pylist(tables["neurons"])
    edges = pa.Table.from_pylist(tables["edges"])
    pq.write_table(neurons, derived / "malecns-full-neurons.parquet")
    pq.write_table(edges, derived / "malecns-full-edges.parquet")
    meta = {
        "dataset": tables["dataset"],
        "source_annotation_revision": tables["source_annotation_revision"],
        "fixture_kind": "malecns-full",
        "neuron_count": neurons.num_rows,
        "edge_count": edges.num_rows,
        "review": tables["review"],
        "sensory_map": tables["sensory_map"],
        "motor_map": tables["motor_map"],
        "provenance": MaleCNSAdapter(raw_dir).provenance(),
    }
    meta_path = derived / "malecns-full-meta.json"
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta_path


def tables_from_full_meta(meta_path: Path = FULL_META) -> dict[str, Any]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    derived = meta_path.parent
    neurons = pq.read_table(derived / "malecns-full-neurons.parquet").to_pylist()
    edges = pq.read_table(derived / "malecns-full-edges.parquet").to_pylist()
    return {
        "fixture_kind": "malecns-full",
        "dataset": meta.get("dataset", "male-cns:v1.0"),
        "source_annotation_revision": meta.get(
            "source_annotation_revision", "male-cns-v1.0-minconf-0.5"
        ),
        "neurons": neurons,
        "edges": edges,
        "review": meta.get("review") or [],
        "sensory_map": meta.get("sensory_map") or [],
        "motor_map": meta.get("motor_map") or [],
    }
