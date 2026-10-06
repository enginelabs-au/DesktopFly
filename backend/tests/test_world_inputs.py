"""Looming-escape circuit and fixed intrinsic activity (owner decisions 2026-10-06)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest

from flysim.config import Policy, load_policy_dict
from flysim.presentation import ConnectomePresentationEngine

DERIVED = Path(__file__).resolve().parents[2] / "data" / "derived"
META = DERIVED / "malecns-escape-meta.json"

pytestmark = pytest.mark.skipif(
    not META.is_file(), reason="run scripts/build_malecns_escape_subset.py first"
)


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def test_committed_policy_selects_the_escape_subset_on_numpy():
    policy = load_policy_dict()
    assert policy["reviewed_subset_name"] == "escape"
    assert policy["resting_drive"] == 0.0
    assert policy["intrinsic_noise_amplitude"] == 1.6
    assert policy["torch_lif_min_neurons"] >= 5000  # measured: numpy is faster at this size
    status = ConnectomePresentationEngine.create(policy).status()
    assert status["lif_backend"] == "numpy-lif"
    assert status["sim_neuron_count"] > 1000
    assert policy["recovery"]["allow_runtime_weight_updates"] is False


def test_reviewed_signs_come_from_neurotransmitters_and_include_inhibition():
    review = pq.read_table(DERIVED / _meta()["review_path"]).to_pylist()
    signs = {r["fixed_sign"] for r in review}
    assert signs == {-1, 1}, "network must contain both excitation and inhibition"
    assert all(r["decision"] == "include" and r["modulatory_status"] == "no" for r in review)
    assert all(isinstance(r["neuron_id"], str) and r["neuron_id"].startswith("male-cns:") for r in review)


def test_seed_circuit_is_cholinergic_looming_detectors_and_two_giant_fibers():
    meta = _meta()
    neurons = pq.read_table(DERIVED / meta["neurons_path"]).to_pylist()
    types = {r["neuron_id"]: r["cell_type"] for r in neurons}
    sign = {r["neuron_id"]: r["fixed_sign"] for r in pq.read_table(DERIVED / meta["review_path"]).to_pylist()}
    gf = [n for n, t in types.items() if t == "DNp01"]
    assert len(gf) == 2
    for n, t in types.items():
        if t in ("LC4", "LPLC2", "DNp01"):
            assert sign[n] == 1, f"{t} is cholinergic (excitatory)"
    sensory = meta["sensory_map"]
    assert {r["feature_name"] for r in sensory} == {"loom_left", "loom_right"}
    assert all(r["mapping_kind"] == "anatomical" for r in sensory)
    assert all(types[r["neuron_id"]] in ("LC4", "LPLC2") for r in sensory)
    assert len({r["neuron_id"] for r in sensory}) == len(sensory), "each neuron has one eye"
    motor = meta["motor_map"]
    takeoff = [r for r in motor if r["output_channel"] == "takeoff"]
    assert {r["neuron_id"] for r in takeoff} == set(gf)
    assert all(r["mapping_kind"] == "anatomical" for r in takeoff)
    engineered = [r for r in motor if r["output_channel"] in ("left", "right")]
    assert engineered and all(r["mapping_kind"] == "engineered" for r in engineered)
    assert all("not an anatomical claim" in r["evidence"] for r in engineered)


def test_policy_rejects_out_of_range_or_bool_settings():
    raw = load_policy_dict()
    for field, bad in (
        ("intrinsic_noise_amplitude", -0.1),
        ("intrinsic_noise_amplitude", 5.0),
        ("intrinsic_noise_amplitude", True),
        ("resting_drive", 3.0),
        ("intrinsic_noise_seed", -1),
        ("reviewed_subset_name", "../x"),
    ):
        with pytest.raises(Exception):
            Policy.model_validate({**raw, field: bad})


def _run(features, *, pre=400, on=300, policy=None):
    engine = ConnectomePresentationEngine.create(policy or load_policy_dict())
    rows = []
    for i in range(pre + on):
        m = engine.step(0.005, features if i >= pre else {})["motor"]
        rows.append((m["speed"], m["turn"], m["takeoff"]))
    a = np.array(rows)
    return a[:pre], a[pre:]


def test_same_seed_repeats_exactly():
    a = _run({})
    b = _run({})
    assert np.array_equal(a[1], b[1])


def test_giant_fiber_never_fires_from_intrinsic_noise_alone():
    quiet_before, quiet_during = _run({}, pre=800, on=800)
    assert quiet_before[:, 2].max() == 0.0 and quiet_during[:, 2].max() == 0.0
    assert quiet_before[:, 0].mean() > 5, "wanders spontaneously from its own activity"


def test_a_looming_eye_drives_a_graded_escape_with_takeoff_and_a_turn_away():
    base_before, _ = _run({})
    _, weak = _run({"loom_left": 0.4})
    _, mid = _run({"loom_left": 0.6})
    _, left = _run({"loom_left": 0.9})
    _, right = _run({"loom_right": 0.9})
    assert weak[:, 2].max() == 0.0 and weak[:, 0].mean() < 60, "below threshold: no escape"
    assert mid[:, 2].mean() < left[:, 2].mean(), "response grows with stimulus strength"
    for resp in (left, right):
        assert resp[:, 2].mean() > 0.3, "giant-fiber takeoff readout"
        assert resp[:, 0].mean() > 3 * base_before[:, 0].mean(), "fast departure"
        assert resp[:, 0].max() <= 120.0 and abs(resp[:, 1]).max() <= 3.0
    # Contralateral steering convention: looming on the left turns the body right.
    assert left[:, 1].mean() > 0.5
    assert right[:, 1].mean() < -0.5


def test_looming_on_both_eyes_runs_straight_and_faster_than_one_eye():
    _, one = _run({"loom_left": 0.8})
    _, both = _run({"loom_left": 0.8, "loom_right": 0.8})
    assert both[:, 2].mean() > one[:, 2].mean()
    assert abs(both[:, 1].mean()) < abs(one[:, 1].mean())
