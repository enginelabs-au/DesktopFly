"""Atomic, verified application-state checkpoints.

Snapshots are application-owned. Recovery budgets are never stored inside them.
Never restore uncommitted failing candidates.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    created_monotonic_s: float
    payload: dict[str, Any]
    payload_hash: str
    validated: bool


def _hash_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class CheckpointStore:
    """Keep up to ``max_rolling`` validated snapshots plus a protected initial."""

    def __init__(
        self,
        *,
        max_rolling: int = 3,
        min_age_before_warning_s: float = 1.0,
        now: Any | None = None,
    ) -> None:
        if max_rolling < 1:
            raise ValueError("max_rolling must be >= 1")
        self.max_rolling = max_rolling
        self.min_age_before_warning_s = min_age_before_warning_s
        self._now = now or time.monotonic
        self._initial: Checkpoint | None = None
        self._rolling: list[Checkpoint] = []
        self._seq = 0

    def validate_payload(self, payload: dict[str, Any]) -> None:
        if not isinstance(payload, dict):
            raise ValueError("checkpoint payload must be an object")
        # Recovery ledger / attempt budgets must stay outside restorable agent state.
        forbidden = ("recovery_ledger", "session_attempts", "incident_attempts", "attempted_recipe_ids")
        for key in forbidden:
            if key in payload:
                raise ValueError(f"checkpoint must not include recovery budget field {key}")
        state = payload.get("neural_state")
        if state is not None and not isinstance(state, dict):
            raise ValueError("neural_state must be an object when present")
        if "finite" in payload and payload["finite"] is not True:
            raise ValueError("checkpoint rejected: non-finite marker")

    def save_initial(self, payload: dict[str, Any]) -> Checkpoint:
        self.validate_payload(payload)
        cp = self._make(payload, validated=True)
        self._initial = cp
        return cp

    def save_validated(self, payload: dict[str, Any]) -> Checkpoint:
        self.validate_payload(payload)
        cp = self._make(payload, validated=True)
        self._rolling.append(cp)
        while len(self._rolling) > self.max_rolling:
            self._rolling.pop(0)
        return cp

    def _make(self, payload: dict[str, Any], *, validated: bool) -> Checkpoint:
        self._seq += 1
        digest = _hash_payload(payload)
        return Checkpoint(
            checkpoint_id=f"cp-{self._seq:04d}-{digest[:8]}",
            created_monotonic_s=float(self._now()),
            payload=dict(payload),
            payload_hash=digest,
            validated=validated,
        )

    def latest(self) -> Checkpoint | None:
        if self._rolling:
            return self._rolling[-1]
        return self._initial

    def restore_before_warning(self, first_warning_monotonic_s: float) -> Checkpoint | None:
        """Prefer snapshot at least min_age before first warning; else initial."""
        cutoff = first_warning_monotonic_s - self.min_age_before_warning_s
        eligible = [
            cp
            for cp in self._rolling
            if cp.validated and cp.created_monotonic_s <= cutoff
        ]
        if eligible:
            return eligible[-1]
        return self._initial

    def write_atomic(self, checkpoint: Checkpoint, directory: Path) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"{checkpoint.checkpoint_id}.json"
        tmp = directory / f".{checkpoint.checkpoint_id}.tmp"
        body = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "created_monotonic_s": checkpoint.created_monotonic_s,
            "payload_hash": checkpoint.payload_hash,
            "validated": checkpoint.validated,
            "payload": checkpoint.payload,
        }
        tmp.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
        tmp.replace(target)
        return target
