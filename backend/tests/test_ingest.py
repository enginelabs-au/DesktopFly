import json
from pathlib import Path

import numpy as np
import pytest

from flysim.ingest import build_static_graph
from flysim.review import (
    assert_namespace,
    compile_reviewed_graph,
    load_flywire_adapter,
    load_malecns_weights,
    write_ingestion_report,
)
from flysim.schema import JS_SAFE_INTEGER_MAX

REPO = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "synthetic-three-node.json"
TABLES = Path(__file__).resolve().parent / "fixtures" / "synthetic-tables.json"


def _tables():
    return json.loads(TABLES.read_text())


def test_policy_enables_real_graph():
    policy = json.loads((REPO / "config" / "policy.json").read_text())
    assert policy["real_graph_enabled"] is True


def test_synthetic_ids_are_not_connectome_ids():
    fixture = json.loads(FIXTURE.read_text())
    for neuron_id in fixture["ids"]:
        assert neuron_id.startswith("synthetic:")
        assert neuron_id.isascii()


def test_three_node_hand_calculated_weights():
    fixture = json.loads(FIXTURE.read_text())
    graph = build_static_graph(
        fixture["ids"],
        fixture["src"],
        fixture["dst"],
        fixture["counts"],
        fixture["signs"],
        np.array(fixture["blocked"], dtype=np.bool_),
        gain=fixture["gain"],
    )
    expected = np.array(fixture["expected_weights"], dtype=np.float32)
    assert graph.ids == tuple(fixture["ids"])
    np.testing.assert_allclose(graph.weights, expected, rtol=0, atol=1e-6)
    assert graph.allowed.tolist() == [True, True, True]


def test_rejects_duplicate_ids():
    with pytest.raises(ValueError, match="Invalid or duplicate"):
        build_static_graph(
            ["synthetic:a", "synthetic:a"],
            [0],
            [1],
            [1],
            [1.0, 1.0],
            np.array([False, False]),
        )


def test_rejects_unresolved_sign():
    with pytest.raises(ValueError, match="Unresolved fixed sign"):
        build_static_graph(
            ["synthetic:a", "synthetic:b"],
            [0],
            [1],
            [1],
            [1.0, 0.0],
            np.array([False, False]),
        )


def test_blocked_nodes_drop_incident_edges():
    with pytest.raises(ValueError, match="No eligible edges"):
        build_static_graph(
            ["synthetic:a", "synthetic:b"],
            [0],
            [1],
            [3],
            [1.0, -1.0],
            np.array([True, False]),
        )


def test_blocked_destination_also_drops_incoming_edges():
    with pytest.raises(ValueError, match="No eligible edges"):
        build_static_graph(
            ["synthetic:a", "synthetic:b"],
            [0],
            [1],
            [3],
            [1.0, -1.0],
            np.array([False, True]),
        )


def test_rejects_duplicate_pairs():
    with pytest.raises(ValueError, match="Aggregate duplicate"):
        build_static_graph(
            ["synthetic:a", "synthetic:b"],
            [0, 0],
            [1, 1],
            [1, 2],
            [1.0, 1.0],
            np.array([False, False]),
        )


def test_rejects_non_finite_gain():
    with pytest.raises(ValueError, match="Invalid incoming weight cap"):
        build_static_graph(
            ["synthetic:a", "synthetic:b"],
            [0],
            [1],
            [1],
            [1.0, 1.0],
            np.array([False, False]),
            gain=float("nan"),
        )


def test_string_ids_round_trip_above_js_safe_integer():
    oversized = str(JS_SAFE_INTEGER_MAX + 2)
    neuron_id = f"synthetic:{oversized}"
    assert int(oversized) > JS_SAFE_INTEGER_MAX
    payload = json.loads(json.dumps({"neuron_id": neuron_id}))
    assert payload["neuron_id"] == neuron_id
    assert payload["neuron_id"] != str(float(oversized))


def test_compile_synthetic_tables_and_report(tmp_path):
    compiled = compile_reviewed_graph(_tables())
    assert compiled.selected_ids == (
        "synthetic:pre",
        "synthetic:mid",
        "synthetic:post",
        "synthetic:clamped",
    )
    assert compiled.blocked_ids == ("synthetic:clamped",)
    np.testing.assert_allclose(compiled.graph.weights, np.array([1.1, -1.1], dtype=np.float32))
    assert compiled.graph.ids == compiled.selected_ids
    assert compiled.sensory_gains["synthetic:pre"] == 0.5
    assert compiled.sensory_gains["synthetic:clamped"] == 0.0
    assert compiled.motor_gains["synthetic:post"] == 0.8
    assert compiled.motor_gains["synthetic:clamped"] == 0.0
    assert compiled.report["sensory_to_readout_reachability"] is True
    assert compiled.report["exclusion_counts"]["modulatory"] == 1
    path = write_ingestion_report(compiled, tmp_path / "ingestion.json")
    report = json.loads(path.read_text())
    assert report["real_graph_enabled"] is True
    assert report["fixture_kind"] == "synthetic"
    assert "synthetic:9007199254740993" not in report["selected_ids"]
    assert report["selected_ids"] == list(compiled.selected_ids)


def test_rejects_mismatched_dataset_revision():
    tables = _tables()
    tables["neurons"][1]["source_annotation_revision"] = "other"
    with pytest.raises(ValueError, match="mismatched dataset/review versions"):
        compile_reviewed_graph(tables)


def test_missing_review_excludes_without_inventing_ids():
    tables = _tables()
    tables["neurons"].append(
        {
            "dataset": "synthetic:phase1",
            "neuron_id": "synthetic:unreviewed",
            "cell_type": None,
            "region": None,
            "source_annotation_revision": "synthetic-review-1",
        }
    )
    compiled = compile_reviewed_graph(tables)
    assert "synthetic:unreviewed" not in compiled.selected_ids
    assert compiled.exclusion_counts["missing_review"] == 1


def test_missing_real_connectome_files_are_technical_blockers():
    with pytest.raises(FileNotFoundError, match="missing file"):
        load_malecns_weights(Path("/tmp/missing-male-cns.feather"))
    with pytest.raises(FileNotFoundError, match="missing file"):
        load_flywire_adapter(Path("/tmp/missing-flywire.parquet"))


def test_refuses_mixed_identifier_namespaces():
    with pytest.raises(ValueError, match="Do not mix FlyWire"):
        assert_namespace("flywire:1", "male-cns:v1.0")


def _numeric_tables():
    """Synthetic tables with numeric ids so the integer edge-array path applies."""
    tables = _tables()
    rename = {
        "synthetic:pre": "synthetic:11",
        "synthetic:mid": "synthetic:12",
        "synthetic:post": "synthetic:13",
        "synthetic:clamped": "synthetic:14",
        "synthetic:9007199254740993": "synthetic:9007199254740993",
        "synthetic:excluded-mod": "synthetic:15",
    }
    for key in ("neurons", "review", "sensory_map", "motor_map"):
        for row in tables[key]:
            row["neuron_id"] = rename.get(row["neuron_id"], row["neuron_id"])
    for row in tables["edges"]:
        row["pre_id"] = rename.get(row["pre_id"], row["pre_id"])
        row["post_id"] = rename.get(row["post_id"], row["post_id"])
    return tables


def test_edge_arrays_compile_matches_row_edges():
    rows = _numeric_tables()
    arrays = _numeric_tables()
    body = lambda nid: int(nid.split(":")[1])  # noqa: E731
    arrays["edge_arrays"] = {
        "pre_body": np.array([body(e["pre_id"]) for e in arrays["edges"]] + [999_999], dtype=np.int64),
        "post_body": np.array([body(e["post_id"]) for e in arrays["edges"]] + [12], dtype=np.int64),
        "synapse_count": np.array([e["synapse_count"] for e in arrays["edges"]] + [5], dtype=np.int64),
    }
    arrays["edges"] = []
    a = compile_reviewed_graph(rows)
    b = compile_reviewed_graph(arrays)
    assert a.selected_ids == b.selected_ids
    np.testing.assert_array_equal(a.graph.src, b.graph.src)
    np.testing.assert_array_equal(a.graph.dst, b.graph.dst)
    np.testing.assert_allclose(a.graph.weights, b.graph.weights)
    assert b.report["sensory_to_readout_reachability"] is True
    assert b.report["orphan_readouts"] == a.report["orphan_readouts"]
    assert b.report["disconnected_component_count"] == a.report["disconnected_component_count"]
    assert b.report["input_edge_count"] == len(rows["edges"]) + 1  # unknown body counted then dropped
    assert b.exclusion_counts["edges_not_in_subset"] == a.exclusion_counts["edges_not_in_subset"] + 1


def test_edge_arrays_reject_non_positive_counts_and_mixed_sources():
    tables = _numeric_tables()
    tables["edge_arrays"] = {
        "pre_body": np.array([11], dtype=np.int64),
        "post_body": np.array([12], dtype=np.int64),
        "synapse_count": np.array([0], dtype=np.int64),
    }
    with pytest.raises(ValueError, match="edge rows or edge arrays"):
        compile_reviewed_graph(tables)
    tables["edges"] = []
    with pytest.raises(ValueError, match="positive integer"):
        compile_reviewed_graph(tables)
