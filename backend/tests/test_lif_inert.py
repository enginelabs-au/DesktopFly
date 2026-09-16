"""LIF remains inert while real_graph_enabled is false."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from flysim.ingest import build_static_graph
from flysim.lif import (
    FrozenLIF,
    LIFPolicy,
    LifStartRefused,
    refuse_lif_start,
    start_lif_worker,
)

ROOT = Path(__file__).resolve().parents[2]


def test_policy_keeps_graph_disabled():
    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    assert policy["real_graph_enabled"] is False


def test_refuse_lif_start_while_disabled():
    policy = {"real_graph_enabled": False}
    with pytest.raises(LifStartRefused, match="authored animation"):
        refuse_lif_start(policy)
    with pytest.raises(LifStartRefused, match="LIF worker"):
        start_lif_worker(policy)


def test_refuse_even_if_flag_true_without_q012_review_path():
    """True flag alone is not enough in this phase — still refuse start."""
    with pytest.raises(LifStartRefused, match="Q-012"):
        refuse_lif_start({"real_graph_enabled": True})


def test_one_neuron_threshold_reference_offline_only():
    graph = build_static_graph(
        ids=["synthetic:a", "synthetic:b"],
        src=[0],
        dst=[1],
        counts=[1],
        signs=[1.0, 1.0],
        blocked=[False, False],
    )
    lif = FrozenLIF(graph, LIFPolicy())
    state = lif.initial_state()
    # Drive neuron 0 with constant input until threshold.
    external = np.zeros(2, dtype=np.float32)
    external[0] = 2.0
    spiked = False
    for _ in range(50):
        state, diag = lif.candidate(state, external)
        assert diag["not_live_controller"] is True
        if state.spikes[0] > 0:
            spiked = True
            assert state.v[0] == 0.0
            break
    assert spiked
