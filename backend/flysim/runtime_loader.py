"""Resolve which reviewed graph tables back the live desktop LIF loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flysim.review import compile_reviewed_graph, load_policy

REPO_ROOT = Path(__file__).resolve().parents[2]
DERIVED_META = REPO_ROOT / "data" / "derived" / "malecns-subset-meta.json"
MALECNS_SUBSET_FIXTURE = REPO_ROOT / "backend" / "fixtures" / "malecns-motor-circuit-subset.json"
SYNTHETIC_FIXTURE = (
    REPO_ROOT / "backend" / "tests" / "fixtures" / "synthetic-tables.json"
)

ALLOWED_FIXTURE_KINDS = frozenset(
    {"synthetic", "malecns-reviewed-subset", "malecns-derived"}
)


def _load_tables(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _tables_from_derived_meta(meta_path: Path) -> tuple[dict[str, Any], str]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    derived = meta_path.parent
    neuron_path = derived / "neurons.parquet"
    edge_path = derived / "edges.parquet"
    if not neuron_path.is_file() or not edge_path.is_file():
        raise FileNotFoundError("derived subset meta present but parquet tables missing")
    import pyarrow.parquet as pq

    neurons_table = pq.read_table(neuron_path)
    edges_table = pq.read_table(edge_path)
    neurons = neurons_table.to_pylist()
    edges = edges_table.to_pylist()
    review = meta.get("review") or []
    sensory_map = meta.get("sensory_map") or []
    motor_map = meta.get("motor_map") or []
    tables = {
        "fixture_kind": "malecns-derived",
        "dataset": meta.get("dataset", "male-cns:v1.0"),
        "source_annotation_revision": meta.get(
            "source_annotation_revision", "male-cns-v1.0-minconf-0.5"
        ),
        "neurons": neurons,
        "edges": edges,
        "review": review,
        "sensory_map": sensory_map,
        "motor_map": motor_map,
    }
    return tables, "malecns-derived"


def resolve_runtime_tables(
    policy: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    """Pick tables for the live loop. Never silently label synthetic as MaleCNS."""
    policy = policy or load_policy()
    if policy.get("real_graph_enabled") is not True:
        tables = _load_tables(SYNTHETIC_FIXTURE)
        return tables, "authored-policy-off"

    if DERIVED_META.is_file():
        try:
            return _tables_from_derived_meta(DERIVED_META)
        except FileNotFoundError:
            pass

    if MALECNS_SUBSET_FIXTURE.is_file():
        tables = _load_tables(MALECNS_SUBSET_FIXTURE)
        kind = tables.get("fixture_kind", "malecns-reviewed-subset")
        return tables, str(kind)

    raise RuntimeError(
        "real_graph_enabled but no MaleCNS reviewed subset found "
        f"(expected {MALECNS_SUBSET_FIXTURE} or {DERIVED_META})"
    )


def load_compiled_runtime(policy: dict[str, Any] | None = None):
    tables, graph_source = resolve_runtime_tables(policy)
    compiled = compile_reviewed_graph(tables, policy)
    fixture_kind = tables.get("fixture_kind", graph_source)
    if fixture_kind not in ALLOWED_FIXTURE_KINDS and graph_source not in ALLOWED_FIXTURE_KINDS:
        raise ValueError(f"unsupported runtime fixture_kind {fixture_kind!r}")
    report = dict(compiled.report)
    report["graph_source"] = graph_source
    report["motion_driver"] = (
        "connectome-lif"
        if graph_source in {"malecns-reviewed-subset", "malecns-derived"}
        else "synthetic-lif-ci-only"
        if graph_source == "synthetic"
        else "unavailable"
    )
    report["connectome_mode"] = graph_source in {
        "malecns-reviewed-subset",
        "malecns-derived",
    }
    return compiled, tables, graph_source, report
