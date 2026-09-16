import json
from pathlib import Path

import numpy as np
import pytest

from flysim.ingest import build_static_graph

REPO = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "synthetic-three-node.json"


def test_policy_keeps_real_graph_disabled():
    policy = json.loads((REPO / "config" / "policy.json").read_text())
    assert policy["real_graph_enabled"] is False


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
