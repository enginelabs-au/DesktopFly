"""LIF start and kernel tests with neural simulation enabled."""

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
    assert_lif_may_start,
    start_lif_worker,
)
from flysim.review import load_malecns_weights

ROOT = Path(__file__).resolve().parents[2]


def _graph():
    return build_static_graph(
        ids=["synthetic:a", "synthetic:b"],
        src=[0],
        dst=[1],
        counts=[1],
        signs=[1.0, 1.0],
        blocked=[False, False],
    )


def test_policy_enables_real_graph():
    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    assert policy["real_graph_enabled"] is True


def test_lif_starts_when_enabled_with_graph():
    policy = {"real_graph_enabled": True}
    handle = start_lif_worker(policy, graph=_graph(), graph_source="synthetic")
    assert handle.running is True
    state, diag = handle.step(np.array([2.0, 0.0], dtype=np.float32))
    assert diag["live_controller"] is True
    assert state.v.shape == (2,)


def test_lif_refuses_only_when_flag_false():
    with pytest.raises(LifStartRefused, match="real_graph_enabled is false"):
        assert_lif_may_start({"real_graph_enabled": False})


def test_lif_start_requires_graph_as_technical_blocker():
    with pytest.raises(LifStartRefused, match="no StaticGraph"):
        start_lif_worker({"real_graph_enabled": True})


def test_missing_malecns_weights_is_technical_blocker():
    with pytest.raises(FileNotFoundError, match="missing file"):
        load_malecns_weights(ROOT / "data" / "raw" / "missing-weights.feather")


def test_one_neuron_threshold_live_kernel():
    lif = FrozenLIF(_graph(), LIFPolicy())
    state = lif.initial_state()
    external = np.zeros(2, dtype=np.float32)
    external[0] = 2.0
    spiked = False
    for _ in range(50):
        state, diag = lif.candidate(state, external)
        assert diag["live_controller"] is True
        if state.spikes[0] > 0:
            spiked = True
            assert state.v[0] == 0.0
            break
    assert spiked
