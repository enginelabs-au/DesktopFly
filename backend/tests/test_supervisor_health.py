"""Phase 4 supervisor, health, recovery, checkpoint, bridge tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from flysim.bridge import Bridge
from flysim.checkpoints import CheckpointStore
from flysim.health import HEALTH_DISCLAIMER, OperatorStatus, build_health_view
from flysim.ingest import build_static_graph
from flysim.recovery import load_recovery_profiles
from flysim.supervisor import Lifecycle, Supervisor, stop_children_bounded
from flysim.worker import run_worker

ROOT = Path(__file__).resolve().parents[2]


class _FakeChild:
    def __init__(self) -> None:
        self._alive = True
        self.terminated = False
        self.killed = False

    def is_alive(self) -> bool:
        return self._alive

    def join(self, timeout: float | None = None) -> None:
        del timeout
        if self.terminated or self.killed:
            self._alive = False

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True
        self._alive = False


class _StopEvent:
    def __init__(self) -> None:
        self.is_set = False

    def set(self) -> None:
        self.is_set = True


def _supervisor() -> Supervisor:
    clock = {"t": 0.0}

    def now() -> float:
        return clock["t"]

    return Supervisor.create("sess-test", now=now)


def test_healthy_copy_is_plain_language():
    view = build_health_view("RUNNING", quiet=True)
    assert view.status is OperatorStatus.HEALTHY_QUIET
    assert view.title.startswith("Healthy")
    assert HEALTH_DISCLAIMER in view.disclaimer
    assert "food" in (view.quiet_note or "").lower()
    assert "suffering" not in view.title.lower()


def test_stop_latch_is_permanent_and_independent():
    sup = _supervisor()
    sup.mark_ready()
    sup.start()
    assert sup.lifecycle is Lifecycle.RUNNING
    sup.request_stop("tray_stop")
    assert sup.stop_latched is True
    assert sup.lifecycle is Lifecycle.STOPPED
    # Recovery cannot clear a hard/stop latch.
    action = sup.handle_condition("boundary_geometry", evidence_ok=True, incident_id="i1")
    assert action == "ignored"
    assert sup.stop_latched is True


def test_unknown_condition_requires_review():
    sup = _supervisor()
    sup.mark_ready()
    sup.start()
    action = sup.handle_condition("mysterious_new_fault", evidence_ok=True, incident_id="i2")
    assert action == "review_required"
    assert sup.lifecycle is Lifecycle.REVIEW_REQUIRED
    assert sup.health_view().status is OperatorStatus.REVIEW_REQUIRED


def test_known_recovery_reserves_budget_outside_checkpoint():
    sup = _supervisor()
    sup.mark_ready()
    sup.start()
    action = sup.handle_condition("boundary_geometry", evidence_ok=True, incident_id="inc-1")
    assert action == "recover"
    assert sup.lifecycle is Lifecycle.RECOVERING
    assert sup.recovery.ledger.session_attempts == 1
    assert "boundary_open_position" in sup.recovery.ledger.attempted_recipe_ids

    store = CheckpointStore()
    with pytest.raises(ValueError, match="recovery budget"):
        store.save_validated(
            {
                "neural_state": {"v": [0.0]},
                "recovery_ledger": sup.recovery.ledger.as_dict(),
            }
        )
    cp = store.save_validated({"neural_state": {"v": [0.0]}, "finite": True})
    assert cp.validated is True
    assert "recovery_ledger" not in cp.payload


def test_recovery_budget_exhaustion_goes_to_review():
    from flysim.recovery import RecoveryRecipe

    sup = _supervisor()
    sup.mark_ready()
    sup.start()
    assert (
        sup.handle_condition("boundary_geometry", evidence_ok=True, incident_id="inc-a")
        == "recover"
    )
    first = sup.recovery.ledger.attempted_recipe_ids[0]
    sup.complete_recovery(first, success=False)
    assert sup.lifecycle is Lifecycle.RECOVERING
    second = sup.recovery.next_recipe("boundary_geometry")
    assert second is not None
    assert sup.recovery.reserve_attempt(second)["ok"] is True
    # max_attempts_per_incident == 2 → further reserve requires review
    fake = RecoveryRecipe(
        recipe_id="extra",
        signature="boundary_geometry",
        step_index=3,
        description="should not run",
        effects=(),
        preconditions=(),
        test_report="n/a",
    )
    again = sup.recovery.reserve_attempt(fake)
    assert again["ok"] is False
    assert again["action"] == "review_required"


def test_heartbeat_timeout_hard_faults():
    t = [0.0]

    def now() -> float:
        return t[0]

    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    profiles = load_recovery_profiles()
    from flysim.recovery import RecoveryController
    from flysim.checkpoints import CheckpointStore

    recovery = RecoveryController(policy["recovery"], profiles, "sess-hb", now=now)
    store = CheckpointStore(now=now)
    sup = Supervisor(
        session_id="sess-hb",
        policy=policy,
        recovery=recovery,
        checkpoints=store,
        lifecycle=Lifecycle.RUNNING,
        _now=now,
    )
    sup.note_progress(1, "RUNNING")
    t[0] = 0.3
    sup.check_heartbeat()
    assert sup.stop_latched is True
    assert sup.lifecycle is Lifecycle.FAULT


def test_bridge_stop_sets_supervisor_latch():
    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    bridge = Bridge.create(policy)
    sup = _supervisor()
    sup.mark_ready()
    sup.start()
    raw = json.dumps({"type": "stop", "token": bridge.config.token})
    result = bridge.handle(raw, sup)
    assert result["ok"] is True
    assert sup.stop_latched is True


def test_bridge_rejects_non_loopback_bind():
    with pytest.raises(ValueError, match="127.0.0.1"):
        Bridge.create({"network_bind": "0.0.0.0", "max_ws_message_bytes": 1024})


def test_worker_starts_with_synthetic_graph_when_neural_enabled():
    policy = {"real_graph_enabled": True}
    graph = build_static_graph(
        ids=["synthetic:a", "synthetic:b"],
        src=[0],
        dst=[1],
        counts=[1],
        signs=[1.0, 1.0],
        blocked=[False, False],
    )
    handle = run_worker("sess-w", policy, graph=graph)
    out = handle.step(np.array([2.0, 0.0], dtype=np.float32))
    assert out["tick"] == 1
    assert handle.heartbeat_payload()["committed_tick"] == 1


def test_stop_children_bounded_escalates():
    child = _FakeChild()
    event = _StopEvent()
    stop_children_bounded([child], event, grace_s=0.0, term_s=0.0)
    assert event.is_set is True
    assert child.terminated or child.killed
    assert child.is_alive() is False


def test_recovery_profiles_load_and_hash():
    profiles = load_recovery_profiles()
    assert profiles["allow_runtime_weight_updates"] is False
    assert len(profiles["profiles"]) >= 8
    assert len(profiles["profiles_hash"]) == 64


def test_state_contract_lists_recovery_outside_agent_state():
    contract = json.loads((ROOT / "config" / "state-contract.json").read_text(encoding="utf-8"))
    ledger = next(f for f in contract["fields"] if f["name"] == "recovery_ledger")
    assert ledger["owner"] == "supervisor"
    assert ledger["reset_rule"] == "outside_restorable_agent_state"
    assert contract["ui_may_write_weights"] is False
