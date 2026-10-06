"""Live MaleCNS slice: retina, agreed signs, motor-neuron readout."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
import pytest

from flysim.config import Policy, load_policy_dict
from flysim.presentation import ConnectomePresentationEngine

DERIVED = Path(__file__).resolve().parents[2] / "data" / "derived"
META = DERIVED / "malecns-live-meta.json"

pytestmark = pytest.mark.skipif(
    not META.is_file(), reason="run scripts/build_malecns_live_subset.py first"
)


def _meta() -> dict:
    return json.loads(META.read_text(encoding="utf-8"))


def test_committed_policy_selects_the_live_subset_on_numpy():
    policy = load_policy_dict()
    assert policy["reviewed_subset_name"] == "live"
    assert policy["resting_drive"] == 0.0
    assert policy["intrinsic_noise_amplitude"] == 0.0
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
    assert sensory and all(r["feature_name"].startswith("hex_") for r in sensory)
    assert all(r["mapping_kind"] == "engineered" for r in sensory)
    motor = meta["motor_map"]
    takeoff = [r for r in motor if r["output_channel"] == "takeoff" and r["mapping_kind"] == "anatomical"]
    assert {r["neuron_id"] for r in takeoff} == set(gf)
    leg = [r for r in motor if r["output_channel"] in ("left", "right")]
    assert leg and all("not an anatomical muscle map" in r["evidence"] for r in leg)
    assert all(r["neuron_id"] not in set(gf) for r in leg)


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


def test_without_input_the_network_stays_still():
    quiet_before, quiet_during = _run({}, pre=200, on=200)
    assert quiet_before[:, 2].max() == 0.0 and quiet_during[:, 2].max() == 0.0
    assert quiet_before[:, 0].max() == 0.0


def _eye(prefix: str) -> dict:
    meta = _meta()
    return {r["feature_name"]: 1.0 for r in meta["sensory_map"] if r["feature_name"].startswith(prefix)}


def test_one_eye_changes_the_motor_readout_and_stays_inside_the_caps():
    _, quiet = _run({}, pre=5, on=20)
    _, right = _run(_eye("hex_R_"), pre=10, on=40)
    assert quiet[:, 0].max() == 0.0
    assert right[:, 0].max() > 0.0 or right[:, 2].max() > 0.0
    assert right[:, 0].max() <= 120.0 and abs(right[:, 1]).max() <= 3.0
