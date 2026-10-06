"""Connectome presentation loop drives motor readouts (not authored wander)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flysim.config import load_policy_dict
from flysim.presentation import ConnectomePresentationEngine, decode_schema_motor
from flysim.runtime_loader import load_compiled_runtime

REPO_ROOT = Path(__file__).resolve().parents[2]
MALECNS_FULL_DEV = REPO_ROOT / "backend" / "fixtures" / "malecns-full-dev.json"


def test_runtime_loader_uses_reviewed_malecns_subset_when_enabled():
    policy = load_policy_dict()
    assert policy["real_graph_enabled"] is True
    assert policy.get("graph_mode") == "reviewed_subset"
    compiled, tables, source, report = load_compiled_runtime(policy)
    assert source == "malecns-reviewed-subset"
    assert report["connectome_mode"] is True
    assert compiled.graph.ids[0].startswith("male-cns:")


def test_connectome_engine_steps_produce_motion():
    policy = load_policy_dict()
    engine = ConnectomePresentationEngine.create(policy)
    st = engine.status()
    assert st["connectome_mode"] is True
    assert st["neuron_count"] >= 3
    assert st["synapse_count"] >= 2
    out = engine.step(0.05)
    assert out["transition_source"] == "connectome"
    motor = out["motor"]
    assert motor["speed"] >= 0


def test_connectome_engine_reports_committed_neural_ticks():
    engine = ConnectomePresentationEngine.create(load_policy_dict())
    assert engine.status()["committed_tick"] == 0
    engine.step(0.005)
    assert engine.status()["committed_tick"] == engine.steps_per_block


def test_connectome_motion_changes_over_ticks():
    policy = load_policy_dict()
    engine = ConnectomePresentationEngine.create(policy)
    last = None
    for _ in range(40):
        last = engine.step(0.05)["motor"]
    assert last["speed"] > 0
    a = engine.step(0.05)["motor"]
    b = engine.step(0.05)["motor"]
    assert a != b or a["speed"] > 0


def test_malecns_fixture_is_not_synthetic_ids():
    tables = json.loads(MALECNS_FULL_DEV.read_text(encoding="utf-8"))
    for neuron in tables["neurons"]:
        assert neuron["neuron_id"].startswith("male-cns:")


def _steering_rows():
    return [
        {"neuron_id": "a", "output_channel": "left", "fixed_gain": 1.0},
        {"neuron_id": "b", "output_channel": "right", "fixed_gain": 1.0},
        {"neuron_id": "c", "output_channel": "forward", "fixed_gain": 1.0},
    ]


def test_decode_turn_is_bounded_signed_steering_from_left_right():
    import numpy as np

    ids = ("a", "b", "c")
    rows = _steering_rows()
    right = decode_schema_motor(ids, rows, np.array([0.1, 0.9, 0.5], dtype=np.float32))
    left = decode_schema_motor(ids, rows, np.array([0.9, 0.1, 0.5], dtype=np.float32))
    balanced = decode_schema_motor(ids, rows, np.array([0.5, 0.5, 0.5], dtype=np.float32))
    assert right.turn > 0 > left.turn
    assert balanced.turn == 0.0
    assert abs(right.turn) <= 3.0 and abs(left.turn) <= 3.0
    assert "turn" in right.as_dict()


def test_connectome_motor_reports_steering_over_time():
    engine = ConnectomePresentationEngine.create(load_policy_dict())
    turns = []
    for _ in range(600):
        turns.append(engine.step(0.005)["motor"]["turn"])
    assert max(turns) - min(turns) > 0.0
    assert all(abs(t) <= 3.0 for t in turns)


def test_worker_gc_is_configured_outside_timed_blocks():
    import gc

    from flysim.desktop_neural import configure_realtime_gc

    was_enabled = gc.isenabled()
    try:
        configure_realtime_gc()
        assert gc.isenabled() is False
    finally:
        if was_enabled:
            gc.enable()
