from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from flysim.ingest import StaticGraph, build_static_graph
from flysim.schema import (
    DECISIONS,
    EDGE_FIELDS,
    MAPPING_KINDS,
    MODULATORY,
    MOTOR_FIELDS,
    NEURON_FIELDS,
    OUTPUT_CHANNELS,
    REVIEW_FIELDS,
    ROLES,
    SENSORY_FIELDS,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "policy.json"


def load_policy(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or POLICY_PATH).read_text())


def refuse_real_graph_load(kind: str, policy: dict[str, Any] | None = None) -> None:
    """Legacy helper: prefer ``require_weights_file`` for technical blockers."""
    policy = policy or load_policy()
    if policy.get("real_graph_enabled") is not True:
        raise RuntimeError(
            f"{kind} is not loaded while real_graph_enabled is false; enable the flag or use a synthetic fixture"
        )
    raise RuntimeError(
        f"{kind} technical blocker: file not provided (download MaleCNS weights under data/raw/)"
    )


def require_weights_file(path: Path, kind: str = "MaleCNS weights") -> Path:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"{kind} technical blocker: missing file at {path} "
            "(real_graph_enabled is true; place the feather under data/raw/ or use synthetic LIF)"
        )
    return path


def load_malecns_weights(path: Path, policy: dict[str, Any] | None = None) -> Path:
    policy = policy or load_policy()
    if policy.get("real_graph_enabled") is not True:
        raise RuntimeError("MaleCNS weights require real_graph_enabled true")
    return require_weights_file(path, "MaleCNS weights")


def load_flywire_adapter(path: Path, policy: dict[str, Any] | None = None) -> Path:
    policy = policy or load_policy()
    if policy.get("real_graph_enabled") is not True:
        raise RuntimeError("FlyWire adapter require real_graph_enabled true")
    return require_weights_file(path, "FlyWire adapter")


def assert_namespace(neuron_id: str, dataset: str) -> None:
    if not isinstance(neuron_id, str) or not neuron_id:
        raise ValueError("neuron_id must be a non-empty string")
    if dataset.startswith("male-cns") and neuron_id.startswith("flywire:"):
        raise ValueError("Do not mix FlyWire IDs into MaleCNS tables")
    if dataset.startswith("flywire") and neuron_id.startswith("male-cns:"):
        raise ValueError("Do not mix MaleCNS IDs into FlyWire tables")


def _require_fields(row: dict[str, Any], fields: tuple[str, ...], table: str) -> None:
    missing = [field for field in fields if field not in row]
    if missing:
        raise ValueError(f"{table} missing fields {missing}")


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _as_rows(table: list[dict[str, Any]], fields: tuple[str, ...], name: str) -> list[dict[str, Any]]:
    if not isinstance(table, list):
        raise ValueError(f"{name} must be a list of objects")
    rows = []
    for row in table:
        if not isinstance(row, dict):
            raise ValueError(f"{name} rows must be objects")
        _require_fields(row, fields, name)
        rows.append(row)
    return rows


@dataclass(frozen=True)
class CompiledIngest:
    graph: StaticGraph
    selected_ids: tuple[str, ...]
    exclusion_counts: dict[str, int]
    blocked_ids: tuple[str, ...]
    sensory_gains: dict[str, float]
    motor_gains: dict[str, float]
    report: dict[str, Any]


def compile_reviewed_graph(tables: dict[str, Any], policy: dict[str, Any] | None = None) -> CompiledIngest:
    policy = policy or load_policy()
    # Synthetic and reviewed tables may compile whether or not the live flag is true.
    _ = policy.get("real_graph_enabled")

    expected_dataset = tables.get("dataset") or policy["dataset"]
    expected_revision = tables.get("source_annotation_revision")
    if not expected_revision:
        raise ValueError("tables.source_annotation_revision is required")

    neurons = _as_rows(tables.get("neurons", []), NEURON_FIELDS, "neurons")
    edges = _as_rows(tables.get("edges", []), EDGE_FIELDS, "edges")
    reviews = _as_rows(tables.get("review", []), REVIEW_FIELDS, "review")
    sensory = _as_rows(tables.get("sensory_map", []), SENSORY_FIELDS, "sensory_map")
    motor = _as_rows(tables.get("motor_map", []), MOTOR_FIELDS, "motor_map")

    review_by_id = {}
    for row in reviews:
        neuron_id = row["neuron_id"]
        if neuron_id in review_by_id:
            raise ValueError(f"duplicate review for {neuron_id}")
        review_by_id[neuron_id] = row

    exclusion_counts: dict[str, int] = defaultdict(int)
    selected: list[dict[str, Any]] = []
    blocked_ids: list[str] = []
    seen_ids: set[str] = set()

    for neuron in neurons:
        neuron_id = neuron["neuron_id"]
        if type(neuron_id) is not str:
            raise ValueError("neuron_id must remain a string")
        if neuron_id in seen_ids:
            raise ValueError(f"duplicate neuron_id {neuron_id}")
        seen_ids.add(neuron_id)
        if neuron["dataset"] != expected_dataset:
            raise ValueError("mismatched dataset/review versions")
        if neuron["source_annotation_revision"] != expected_revision:
            raise ValueError("mismatched dataset/review versions")
        assert_namespace(neuron_id, expected_dataset)

        review = review_by_id.get(neuron_id)
        if review is None:
            exclusion_counts["missing_review"] += 1
            continue
        if review["decision"] not in DECISIONS:
            raise ValueError("invalid review decision")
        if review["modulatory_status"] not in MODULATORY:
            raise ValueError("invalid modulatory_status")
        if review["role"] not in ROLES:
            raise ValueError("invalid role")
        if review["modulatory_status"] != "no":
            exclusion_counts["modulatory"] += 1
            continue
        if review["decision"] == "exclude":
            exclusion_counts["exclude"] += 1
            continue
        sign = review["fixed_sign"]
        if sign not in (-1, 1, -1.0, 1.0):
            exclusion_counts["unresolved_sign"] += 1
            continue
        selected.append(
            {
                "neuron_id": neuron_id,
                "sign": float(sign),
                "blocked": review["decision"] == "clamp",
                "role": review["role"],
            }
        )
        if review["decision"] == "clamp":
            blocked_ids.append(neuron_id)

    if not selected:
        raise ValueError("No eligible neurons; use an explicit synthetic fixture")

    index = {row["neuron_id"]: i for i, row in enumerate(selected)}
    aggregated: dict[tuple[int, int], int] = {}
    dropped_unknown = 0
    for edge in edges:
        pre_id, post_id = edge["pre_id"], edge["post_id"]
        count = edge["synapse_count"]
        if type(count) is not int or count <= 0:
            raise ValueError("synapse_count must be a positive integer")
        if type(pre_id) is not str or type(post_id) is not str:
            raise ValueError("edge IDs must be strings")
        if pre_id not in index or post_id not in index:
            dropped_unknown += 1
            continue
        key = (index[pre_id], index[post_id])
        aggregated[key] = aggregated.get(key, 0) + count
    exclusion_counts["edges_not_in_subset"] = dropped_unknown

    src = [pair[0] for pair in aggregated]
    dst = [pair[1] for pair in aggregated]
    counts = [aggregated[pair] for pair in aggregated]
    ids = [row["neuron_id"] for row in selected]
    signs = [row["sign"] for row in selected]
    blocked = np.array([row["blocked"] for row in selected], dtype=np.bool_)
    graph = build_static_graph(ids, src, dst, counts, signs, blocked)

    sensory_gains: dict[str, float] = {neuron_id: 0.0 for neuron_id in ids}
    motor_gains: dict[str, float] = {neuron_id: 0.0 for neuron_id in ids}
    for row in sensory:
        if row["mapping_kind"] not in MAPPING_KINDS:
            raise ValueError("invalid sensory mapping_kind")
        neuron_id = row["neuron_id"]
        gain = float(row["fixed_gain"])
        if neuron_id in sensory_gains:
            sensory_gains[neuron_id] = 0.0 if neuron_id in blocked_ids else gain
    for row in motor:
        if row["mapping_kind"] not in MAPPING_KINDS:
            raise ValueError("invalid motor mapping_kind")
        if row["output_channel"] not in OUTPUT_CHANNELS:
            raise ValueError("invalid output_channel")
        neuron_id = row["neuron_id"]
        gain = float(row["fixed_gain"])
        if neuron_id in motor_gains:
            motor_gains[neuron_id] = 0.0 if neuron_id in blocked_ids else gain

    n = len(ids)
    adjacency = [[] for _ in range(n)]
    for source, dest in zip(graph.src.tolist(), graph.dst.tolist(), strict=True):
        adjacency[source].append(dest)

    def reachable(starts: list[int]) -> set[int]:
        seen: set[int] = set()
        stack = list(starts)
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(adjacency[node])
        return seen

    sensory_idx = [i for i, row in enumerate(selected) if row["role"] == "sensory" and not row["blocked"]]
    readout_idx = [i for i, row in enumerate(selected) if row["role"] == "readout" and not row["blocked"]]
    reached = reachable(sensory_idx) if sensory_idx else set()
    orphan_readouts = [ids[i] for i in readout_idx if i not in reached]
    components = _undirected_components(n, graph.src.tolist(), graph.dst.tolist())

    incoming = np.bincount(graph.dst, weights=np.abs(graph.weights), minlength=n)
    report = {
        "dataset": expected_dataset,
        "source_annotation_revision": expected_revision,
        "real_graph_enabled": bool(policy.get("real_graph_enabled")),
        "fixture_kind": tables.get("fixture_kind") or "reviewed",
        "input_neuron_count": len(neurons),
        "input_edge_count": len(edges),
        "output_neuron_count": len(ids),
        "output_edge_count": int(len(graph.src)),
        "selected_ids": ids,
        "exclusion_counts": dict(exclusion_counts),
        "unresolved_review_coverage": exclusion_counts.get("missing_review", 0)
        + exclusion_counts.get("unresolved_sign", 0),
        "blocked_nodes": blocked_ids,
        "disconnected_component_count": len(components),
        "orphan_readouts": orphan_readouts,
        "sensory_to_readout_reachability": bool(readout_idx) and not orphan_readouts,
        "weight_normalization": {
            "gain": 1.1,
            "incoming_abs_max": float(incoming.max(initial=0.0)),
            "weight_min": float(graph.weights.min()) if len(graph.weights) else 0.0,
            "weight_max": float(graph.weights.max()) if len(graph.weights) else 0.0,
        },
        "source_hash": _hash_payload({"neurons": neurons, "edges": edges}),
        "review_hash": _hash_payload(reviews),
        "fixture_kind": tables.get("fixture_kind", "synthetic"),
    }
    allowed_kinds = frozenset(
        {"synthetic", "malecns-reviewed-subset", "malecns-derived", "malecns-full"}
    )
    if report["fixture_kind"] not in allowed_kinds:
        raise ValueError(f"unsupported fixture_kind for ingest report: {report['fixture_kind']!r}")

    return CompiledIngest(
        graph=graph,
        selected_ids=tuple(ids),
        exclusion_counts=dict(exclusion_counts),
        blocked_ids=tuple(blocked_ids),
        sensory_gains=sensory_gains,
        motor_gains=motor_gains,
        report=report,
    )


def _undirected_components(n: int, src: list[int], dst: list[int]) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for a, b in zip(src, dst, strict=True):
        adj[a].append(b)
        adj[b].append(a)
    seen = [False] * n
    components: list[list[int]] = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        group: list[int] = []
        seen[start] = True
        while stack:
            node = stack.pop()
            group.append(node)
            for nxt in adj[node]:
                if not seen[nxt]:
                    seen[nxt] = True
                    stack.append(nxt)
        components.append(group)
    return components


def write_ingestion_report(compiled: CompiledIngest, path: Path | None = None) -> Path:
    destination = path or (REPO_ROOT / "reports" / "ingestion.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(compiled.report, indent=2) + "\n")
    return destination
