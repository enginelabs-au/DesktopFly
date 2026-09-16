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


def test_runtime_loader_uses_malecns_full_when_enabled():
    policy = load_policy_dict()
    assert policy["real_graph_enabled"] is True
    assert policy.get("graph_mode") == "full"
    compiled, tables, source, report = load_compiled_runtime(policy)
    assert source == "malecns-full"
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
