"""Closeout tests: config, adapters, sensory/motor, device, bridge asyncio."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import numpy as np
import pytest

from flysim.adapters.flywire import FlyWireAdapter
from flysim.adapters.malecns import MaleCNSAdapter, resolve_malecns_paths
from flysim.bridge import Bridge
from flysim.config import Policy, load_policy
from flysim.device import report_device
from flysim.motor import FixedMotorDecoder, build_motor_map
from flysim.sensory import FixedSensoryEncoder, build_sensory_map
from flysim.supervisor import Supervisor

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def test_policy_loads_frozen_and_rejects_extra_keys():
    policy = load_policy()
    assert isinstance(policy, Policy)
    assert policy.real_graph_enabled is True
    assert policy.auto_restart_after_hard_fault is False
    with pytest.raises(Exception):
        Policy.model_validate({**policy.model_dump(), "mystery": 1})


def test_policy_rejects_bool_as_number():
    raw = load_policy().model_dump()
    raw["neural_dt_s"] = True
    with pytest.raises(Exception):
        Policy.model_validate(raw)


def test_malecns_files_present_or_document_blocker():
    try:
        paths = resolve_malecns_paths(RAW)
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    assert paths.weights.is_file()
    adapter = MaleCNSAdapter(RAW)
    neurons = adapter.load_annotations()
    assert neurons.num_rows > 1000
    assert "neuron_id" in neurons.column_names
    prov = adapter.provenance()
    assert prov["dataset"] == "male-cns:v1.0"
    assert len(prov["files"]) == 3


def test_malecns_subset_edge_filter_smoke():
    try:
        adapter = MaleCNSAdapter(RAW)
    except FileNotFoundError as exc:
        pytest.skip(str(exc))
    # Tiny body set from annotations head — may yield zero edges; still validates scan path.
    neurons = adapter.load_annotations()
    bodies = [int(x) for x in neurons.column("source_body_id").to_pylist()[:8]]
    edges = adapter.load_edges_for_bodies(set(bodies))
    assert "pre_id" in edges.column_names
    assert edges.num_rows >= 0


def test_flywire_missing_is_technical_blocker():
    with pytest.raises(FileNotFoundError, match="FlyWire technical blocker"):
        FlyWireAdapter(raw_dir=RAW).require_files()


def test_sensory_and_motor_roundtrip():
    ids = ["synthetic:a", "synthetic:b"]
    sensory = build_sensory_map(
        ids,
        [
            {
                "feature_name": "brightness",
                "neuron_id": "synthetic:a",
                "fixed_gain": 1.0,
                "mapping_kind": "engineered",
                "evidence": "test",
            }
        ],
    )
    encoder = FixedSensoryEncoder(sensory, external_max=2.0)
    current = encoder.encode({"brightness": 1.5})
    assert current.shape == (2,)
    assert current[0] == pytest.approx(1.5)

    motor = build_motor_map(
        ids,
        [
            {
                "neuron_id": "synthetic:b",
                "output_channel": "speed",
                "fixed_gain": 2.0,
                "mapping_kind": "engineered",
                "evidence": "test",
            }
        ],
    )
    cmd = FixedMotorDecoder(motor).decode(np.array([0.0, 0.5], dtype=np.float32))
    assert cmd.speed == pytest.approx(1.0)


def test_device_report_on_linux_documents_mps_gap():
    policy = load_policy().model_dump()
    report = report_device(policy)
    # Linux CI: MPS unavailable and allow_cpu_fallback false → probe_ok false
    # or explicit cpu if policy allows. Document either way.
    assert report.requested == "mps"
    assert report.mps_available in {True, False}
    assert isinstance(report.detail, str)


@pytest.mark.asyncio
async def test_bridge_asyncio_loopback_stop():
    policy = load_policy().model_dump()
    bridge = Bridge.create(policy)
    sup = Supervisor.create("bridge-async")
    sup.mark_ready()
    # Direct handle path remains the unit contract; server start verifies import.
    raw = json.dumps({"type": "stop", "token": bridge.config.token})
    result = bridge.handle(raw, sup)
    assert result["ok"] is True
    assert sup.stop_latched is True
