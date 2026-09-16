"""Independent supervisor: stop latch, lifecycle, recovery decision, child stop.

Does not import torch. Does not depend on Electron renderer or WebSocket loops.
Neural output never authorizes connectors from this module.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from flysim.checkpoints import CheckpointStore
from flysim.health import HealthView, build_health_view
from flysim.recovery import RecoveryController, load_recovery_profiles

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "policy.json"


class Lifecycle(str, Enum):
    STARTING = "STARTING"
    READY = "READY"
    RUNNING = "RUNNING"
    RECOVERING = "RECOVERING"
    CHECKING = "CHECKING"
    PAUSED = "PAUSED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    FAULT = "FAULT"
    STOPPED = "STOPPED"


TERMINAL = frozenset({Lifecycle.FAULT, Lifecycle.STOPPED, Lifecycle.REVIEW_REQUIRED})


@dataclass
class ProgressSignal:
    session_id: str
    committed_tick: int
    status: str
    received_monotonic_s: float


@dataclass
class Supervisor:
    """Owns the permanent stop latch and recovery decision."""

    session_id: str
    policy: dict[str, Any]
    recovery: RecoveryController
    checkpoints: CheckpointStore
    lifecycle: Lifecycle = Lifecycle.STARTING
    stop_latched: bool = False
    segment_pause: bool = False
    fault_reason: str | None = None
    last_progress: ProgressSignal | None = None
    host_lease_fresh: bool = False
    quiet: bool = False
    approaching_limit: bool = False
    _events: list[dict[str, Any]] = field(default_factory=list)
    _now: Any = field(default=time.monotonic, repr=False)

    @classmethod
    def create(
        cls,
        session_id: str,
        *,
        policy_path: Path | None = None,
        profiles_path: Path | None = None,
        now: Any | None = None,
    ) -> Supervisor:
        policy = json.loads((policy_path or POLICY_PATH).read_text(encoding="utf-8"))
        if policy.get("auto_restart_after_hard_fault") is not False:
            raise ValueError("auto_restart_after_hard_fault must be false")
        profiles = load_recovery_profiles(profiles_path)
        clock = now or time.monotonic
        recovery = RecoveryController(
            policy.get("recovery") or {},
            profiles,
            session_id,
            now=clock,
        )
        store = CheckpointStore(
            min_age_before_warning_s=float(
                (policy.get("recovery") or {}).get("checkpoint_min_age_before_warning_s", 1.0)
            ),
            now=clock,
        )
        return cls(
            session_id=session_id,
            policy=policy,
            recovery=recovery,
            checkpoints=store,
            _now=clock,
        )

    def _emit(self, kind: str, **detail: Any) -> None:
        self._events.append({"kind": kind, "at": self._now(), **detail})

    def mark_ready(self) -> None:
        if self.stop_latched:
            return
        self.lifecycle = Lifecycle.READY
        self._emit("ready")

    def start(self) -> None:
        if self.stop_latched or self.lifecycle is not Lifecycle.READY:
            raise RuntimeError("start requires READY and no stop latch")
        if self.policy.get("real_graph_enabled") is not True:
            raise RuntimeError("neural start requires real_graph_enabled true")
        self.lifecycle = Lifecycle.RUNNING
        self.segment_pause = False
        self._emit("start")

    def set_host_lease(self, fresh: bool) -> None:
        self.host_lease_fresh = fresh
        if not fresh and self.lifecycle is Lifecycle.RUNNING:
            self.lifecycle = Lifecycle.PAUSED
            self.segment_pause = True
            self._emit("host_lease_stale")

    def note_progress(self, committed_tick: int, status: str) -> None:
        self.last_progress = ProgressSignal(
            session_id=self.session_id,
            committed_tick=committed_tick,
            status=status,
            received_monotonic_s=self._now(),
        )

    def check_heartbeat(self) -> None:
        """Hard-stop if progress stalls while RUNNING or CHECKING."""
        if self.lifecycle not in {Lifecycle.RUNNING, Lifecycle.CHECKING}:
            return
        timeout = float(self.policy.get("heartbeat_timeout_s", 0.25))
        if self.last_progress is None:
            self.hard_fault("missing_progress")
            return
        age = self._now() - self.last_progress.received_monotonic_s
        if age > timeout:
            self.hard_fault("heartbeat_timeout")

    def request_stop(self, reason: str = "operator_stop") -> None:
        """Permanent stop latch. Independent of Electron renderer."""
        self.stop_latched = True
        self.segment_pause = True
        self.lifecycle = Lifecycle.STOPPED
        self.fault_reason = reason
        self._emit("stop_latched", reason=reason)

    def hard_fault(self, reason: str) -> None:
        self.stop_latched = True
        self.segment_pause = True
        self.lifecycle = Lifecycle.FAULT
        self.fault_reason = reason
        self._emit("hard_fault", reason=reason)

    def user_pause(self) -> None:
        if self.stop_latched:
            return
        self.lifecycle = Lifecycle.PAUSED
        self.segment_pause = True
        self._emit("user_pause")

    def handle_condition(
        self,
        signature: str | None,
        *,
        evidence_ok: bool,
        incident_id: str,
    ) -> str:
        """Classify a condition. Returns recover|review_required|fault|ignored."""
        if self.stop_latched:
            return "ignored"
        if signature is None and not evidence_ok:
            self.lifecycle = Lifecycle.REVIEW_REQUIRED
            self.segment_pause = True
            self._emit("review_required", reason="unknown_or_incomplete")
            return "review_required"

        action = self.recovery.classify(signature, evidence_ok=evidence_ok)
        if action == "review_required":
            self.lifecycle = Lifecycle.REVIEW_REQUIRED
            self.segment_pause = True
            self._emit("review_required", reason=signature or "unknown")
            return "review_required"

        assert signature is not None
        self.lifecycle = Lifecycle.RECOVERING
        self.segment_pause = True
        self.recovery.begin_incident(signature, incident_id)
        recipe = self.recovery.next_recipe(signature)
        if recipe is None:
            self.lifecycle = Lifecycle.REVIEW_REQUIRED
            self._emit("review_required", reason="no_recipe")
            return "review_required"
        reserved = self.recovery.reserve_attempt(recipe)
        if not reserved["ok"]:
            self.lifecycle = Lifecycle.REVIEW_REQUIRED
            self._emit("review_required", reason=reserved["reason"])
            return "review_required"
        self._emit("recovery_reserved", recipe_id=recipe.recipe_id, signature=signature)
        return "recover"

    def complete_recovery(self, recipe_id: str, *, success: bool) -> None:
        if self.stop_latched:
            return
        if success:
            self.recovery.mark_outcome(recipe_id, "verified")
            self.lifecycle = Lifecycle.CHECKING
            self._emit("checking", recipe_id=recipe_id)
        else:
            self.recovery.mark_outcome(recipe_id, "failed")
            # Distinct remaining recipe may still be eligible; else review.
            signature = self.recovery.ledger.signature
            if signature and self.recovery.next_recipe(signature):
                self.lifecycle = Lifecycle.RECOVERING
                self._emit("recovery_retry_available", signature=signature)
            else:
                self.lifecycle = Lifecycle.REVIEW_REQUIRED
                self._emit("review_required", reason="recovery_failed")

    def finish_checking(self, *, passed: bool) -> None:
        if self.stop_latched:
            return
        if passed:
            self.lifecycle = Lifecycle.RUNNING
            self.segment_pause = False
            self.approaching_limit = False
            self._emit("running_after_check")
        else:
            self.lifecycle = Lifecycle.REVIEW_REQUIRED
            self.segment_pause = True
            self._emit("review_required", reason="verification_failed")

    def health_view(self) -> HealthView:
        return build_health_view(
            self.lifecycle.value,
            quiet=self.quiet,
            approaching_limit=self.approaching_limit,
            technical={
                "lifecycle": self.lifecycle.value,
                "stop_latched": self.stop_latched,
                "segment_pause": self.segment_pause,
                "fault_reason": self.fault_reason,
                "session_id": self.session_id,
                "real_graph_enabled": self.policy.get("real_graph_enabled"),
                "recovery_ledger": self.recovery.ledger.as_dict(),
                "host_lease_fresh": self.host_lease_fresh,
            },
        )

    def status(self) -> dict[str, Any]:
        view = self.health_view()
        return {
            "session_id": self.session_id,
            "lifecycle": self.lifecycle.value,
            "stop_latched": self.stop_latched,
            "segment_pause": self.segment_pause,
            "fault_reason": self.fault_reason,
            "health": view.as_dict(),
            "events": list(self._events),
        }


def stop_children_bounded(
    children: list[Any],
    stop_event: Any,
    grace_s: float = 0.2,
    term_s: float = 0.2,
) -> None:
    """Bounded cooperative → terminate → kill. From handover §4.3."""
    stop_event.set()
    cooperative_deadline = time.monotonic() + grace_s
    for child in children:
        child.join(timeout=max(0.0, cooperative_deadline - time.monotonic()))
    alive = [child for child in children if child.is_alive()]
    for child in alive:
        child.terminate()
    terminate_deadline = time.monotonic() + term_s
    for child in alive:
        child.join(timeout=max(0.0, terminate_deadline - time.monotonic()))
    remaining = [child for child in alive if child.is_alive()]
    for child in remaining:
        child.kill()
    for child in remaining:
        child.join(timeout=0.2)
    if any(child.is_alive() for child in children):
        raise RuntimeError("PROCESS_TERMINATION_FAILED")
