"""World inputs, fixed noise, and no scripted drive (owner decision 2026-10-06)."""

from __future__ import annotations

import numpy as np
import pytest

from flysim.config import Policy, load_policy_dict
from flysim.presentation import ConnectomePresentationEngine
from flysim.sensory import WORLD_FEATURES, world_bridge_rows


def _base_rows() -> list[dict[str, object]]:
    return [
        {"feature_name": "ambient_drive", "neuron_id": f"male-cns:{i}", "fixed_gain": 1.0,
         "evidence": "x", "mapping_kind": "engineered"}
        for i in (30, 4, 22, 9, 17, 1, 50, 8)
    ]


def test_world_bridge_is_fixed_engineered_and_covers_the_input_pool_once():
    rows = world_bridge_rows(_base_rows())
    assert rows == world_bridge_rows(list(reversed(_base_rows())))  # order independent
    assert len(rows) == 8
    assert {r["neuron_id"] for r in rows} == {r["neuron_id"] for r in _base_rows()}
    assert {r["feature_name"] for r in rows} == set(WORLD_FEATURES)
    assert all(r["mapping_kind"] == "engineered" for r in rows)
    assert all("not anatomical" in str(r["evidence"]) for r in rows)
    assert world_bridge_rows([]) == []


def test_committed_policy_sets_resting_input_and_noise_as_fixed_values():
    policy = load_policy_dict()
    assert policy["resting_drive"] == 1.0
    assert policy["intrinsic_noise_amplitude"] == 1.0
    assert isinstance(policy["intrinsic_noise_seed"], int)
    assert policy["recovery"]["allow_runtime_weight_updates"] is False


def test_policy_rejects_out_of_range_or_bool_noise_settings():
    raw = load_policy_dict()
    for field, bad in (
        ("intrinsic_noise_amplitude", -0.1),
        ("intrinsic_noise_amplitude", 5.0),
        ("intrinsic_noise_amplitude", True),
        ("resting_drive", 3.0),
        ("intrinsic_noise_seed", -1),
    ):
        with pytest.raises(Exception):
            Policy.model_validate({**raw, field: bad})


def _speeds(policy: dict, features: dict | None = None, n: int = 300) -> np.ndarray:
    engine = ConnectomePresentationEngine.create(policy)
    return np.array([engine.step(0.005, features or {})["motor"]["speed"] for _ in range(n)])


def test_same_seed_repeats_exactly_and_a_different_seed_differs():
    policy = load_policy_dict()
    a = _speeds(policy)
    b = _speeds(policy)
    c = _speeds({**policy, "intrinsic_noise_seed": policy["intrinsic_noise_seed"] + 1})
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_no_scripted_time_dependence_when_noise_is_off():
    policy = {**load_policy_dict(), "intrinsic_noise_amplitude": 0.0}
    engine = ConnectomePresentationEngine.create(policy)
    first = [engine.step(0.005, {})["motor"] for _ in range(400)]
    late = [engine.step(0.005, {})["motor"] for _ in range(400)]
    # A constant input settles to a constant output; nothing in code oscillates it.
    assert late[-1] == late[-2] == late[-50]
    assert first[-1] == pytest.approx(late[-1])


def test_without_resting_input_or_noise_the_network_is_silent():
    policy = {**load_policy_dict(), "resting_drive": 0.0, "intrinsic_noise_amplitude": 0.0}
    assert _speeds(policy).max() == 0.0


def test_world_inputs_change_the_network_output_and_stay_bounded():
    policy = load_policy_dict()
    quiet = _speeds(policy)
    near = _speeds(policy, {"cursor_right": 1.0, "edge_right": 1.0})
    assert near.mean() > quiet.mean()
    assert near.max() <= 120.0 and near.min() >= 0.0


def test_noise_never_pushes_input_outside_the_validated_range():
    policy = {**load_policy_dict(), "intrinsic_noise_amplitude": 2.0, "resting_drive": 2.0}
    engine = ConnectomePresentationEngine.create(policy)
    for _ in range(50):
        out = engine.step(0.005, {"cursor_left": 1.0})
        assert 0.0 <= out["motor"]["speed"] <= 120.0
        assert abs(out["motor"]["turn"]) <= 3.0
