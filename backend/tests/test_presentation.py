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


def test_connectome_stays_still_until_an_eye_is_stimulated():
    import json
    from pathlib import Path

    engine = ConnectomePresentationEngine.create(load_policy_dict())
    quiet = [engine.step(0.005, {})["motor"]["speed"] for _ in range(8)]
    assert max(quiet) == 0.0
    meta = json.loads(
        (Path(__file__).resolve().parents[2] / "data/derived/malecns-live-meta.json").read_text()
    )
    feat = {
        r["feature_name"]: 1.0
        for r in meta["sensory_map"]
        if str(r["feature_name"]).startswith("hex_R_")
    }
    driven = [engine.step(0.005, feat)["motor"] for _ in range(30)]
    assert any(m["speed"] > 0 or m["takeoff"] > 0 for m in driven)


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


def test_connectome_motor_reports_a_bounded_turn_from_the_right_eye():
    import json
    from pathlib import Path

    meta = json.loads(
        (Path(__file__).resolve().parents[2] / "data/derived/malecns-live-meta.json").read_text()
    )
    feat = {
        r["feature_name"]: 1.0
        for r in meta["sensory_map"]
        if str(r["feature_name"]).startswith("hex_R_")
    }
    engine = ConnectomePresentationEngine.create(load_policy_dict())
    turns = [engine.step(0.005, feat)["motor"]["turn"] for _ in range(30)]
    assert all(abs(t) <= 3.0 for t in turns)
    assert any(t != 0 for t in turns)


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


def test_fused_kernel_engine_selection_matches_numpy_engine():
    import numpy as np

    policy = load_policy_dict()
    fused = ConnectomePresentationEngine.create({**policy, "fused_lif_min_neurons": 1, "fused_lif_threads": 2})
    plain = ConnectomePresentationEngine.create({**policy, "fused_lif_min_neurons": 0})
    assert fused.status()["lif_backend"] == "numba-fused-2t"
    assert plain.status()["lif_backend"] == "numpy-lif"
    assert fused.parallel_kernel is True and plain.parallel_kernel is False
    assert fused.status()["committed_tick"] == 0  # warm-up does not advance the clock
    meta = json.loads((REPO_ROOT / "data/derived/malecns-live-meta.json").read_text())
    feat = {r["feature_name"]: 1.0 for r in meta["sensory_map"] if r["feature_name"].startswith("hex_R_")}
    for _ in range(40):
        a = fused.step(0.005, feat)
        b = plain.step(0.005, feat)
        assert a["technical"]["spike_count"] == b["technical"]["spike_count"]
        assert np.isclose(a["motor"]["speed"], b["motor"]["speed"], atol=1e-3)
        assert np.isclose(a["motor"]["turn"], b["motor"]["turn"], atol=1e-3)
    fused.scheduled_reset()  # runs the full weight fingerprint check
    plain.scheduled_reset()
    assert fused.status()["committed_tick"] == plain.status()["committed_tick"]
    assert fused.step(0.005, {})["technical"]["spike_count"] == plain.step(0.005, {})["technical"]["spike_count"]


@pytest.mark.skipif(
    not (REPO_ROOT / "data/derived/malecns-fullbrain-meta.json").is_file()
    or __import__("os").environ.get("DESKTOPFLY_FULLBRAIN_TESTS") != "1",
    reason="whole-brain tables take ~20 s to compile; set DESKTOPFLY_FULLBRAIN_TESTS=1",
)
def test_fullbrain_tables_compile_with_agreed_signs_and_reach_motor_neurons():
    policy = {**load_policy_dict(), "reviewed_subset_name": "fullbrain", "fused_lif_min_neurons": 100_000}
    engine = ConnectomePresentationEngine.create(policy)
    st = engine.status()
    assert st["lif_backend"].startswith("numba-fused-")
    assert st["sim_neuron_count"] > 150_000
    assert engine.report["sensory_to_readout_reachability"] is True
    assert engine.report["orphan_readouts"] == []
    out = engine.step(0.005, {})
    assert out["technical"]["spike_count"] == 0  # no input, no spikes
