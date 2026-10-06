"""Bounded recovery recipes and attempt budgets.

Recovery budgets and failed-attempt history live outside restorable agent state.
Unknown causes never enter automatic trial-and-error.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = REPO_ROOT / "config" / "recovery-profiles.json"


KNOWN_SIGNATURES = frozenset(
    {
        "boundary_geometry",
        "excessive_input_variation",
        "render_capture_load",
        "screen_source_lost",
        "host_presentation_disconnect",
    }
)


@dataclass(frozen=True)
class RecoveryRecipe:
    recipe_id: str
    signature: str
    step_index: int
    description: str
    effects: tuple[str, ...]
    preconditions: tuple[str, ...]
    test_report: str


@dataclass
class RecoveryLedger:
    """Supervisor-owned ledger; never restored into neural state."""

    session_id: str
    incident_id: str | None = None
    signature: str | None = None
    attempted_recipe_ids: list[str] = field(default_factory=list)
    session_attempts: int = 0
    incident_attempts: int = 0
    outcomes: list[dict[str, Any]] = field(default_factory=list)
    first_warning_monotonic_s: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "incident_id": self.incident_id,
            "signature": self.signature,
            "attempted_recipe_ids": list(self.attempted_recipe_ids),
            "session_attempts": self.session_attempts,
            "incident_attempts": self.incident_attempts,
            "outcomes": list(self.outcomes),
            "first_warning_monotonic_s": self.first_warning_monotonic_s,
        }


def _hash_payload(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_recovery_profiles(path: Path | None = None) -> dict[str, Any]:
    data = json.loads((path or PROFILES_PATH).read_text(encoding="utf-8"))
    if data.get("allow_runtime_weight_updates") is not False:
        raise ValueError("recovery profiles must forbid runtime weight updates")
    if data.get("allow_threshold_relaxation") is not False:
        raise ValueError("recovery profiles must forbid threshold relaxation")
    if data.get("allow_automatic_resume_after_hard_fault") is not False:
        raise ValueError("recovery profiles must forbid auto-resume after hard fault")
    profiles = data.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("profiles must be a list")
    for profile in profiles:
        if not isinstance(profile, dict):
            raise ValueError("profile rows must be objects")
        if not profile.get("test_report"):
            raise ValueError(f"recipe {profile.get('recipe_id')} missing test_report")
        if profile.get("signature") not in KNOWN_SIGNATURES:
            raise ValueError(f"unknown recovery signature {profile.get('signature')}")
    data = dict(data)
    data["profiles_hash"] = _hash_payload(profiles)
    return data


def recipes_for_signature(profiles: dict[str, Any], signature: str) -> list[RecoveryRecipe]:
    if signature not in KNOWN_SIGNATURES:
        return []
    rows = [
        p
        for p in profiles.get("profiles", [])
        if p.get("signature") == signature
    ]
    rows.sort(key=lambda row: int(row.get("step_index", 0)))
    return [
        RecoveryRecipe(
            recipe_id=str(row["recipe_id"]),
            signature=str(row["signature"]),
            step_index=int(row["step_index"]),
            description=str(row["description"]),
            effects=tuple(row.get("effects") or ()),
            preconditions=tuple(row.get("preconditions") or ()),
            test_report=str(row["test_report"]),
        )
        for row in rows
    ]


class RecoveryController:
    """Select and budget fixed recipes. Unknown → review_required."""

    def __init__(
        self,
        policy_recovery: dict[str, Any],
        profiles: dict[str, Any],
        session_id: str,
        *,
        now: Any | None = None,
    ) -> None:
        self.policy = policy_recovery
        self.profiles = profiles
        self.ledger = RecoveryLedger(session_id=session_id)
        self._now = now or time.monotonic
        self.enabled = bool(policy_recovery.get("enabled", True))
        self.known_only = bool(policy_recovery.get("known_conditions_only", True))
        self.max_per_incident = int(policy_recovery.get("max_attempts_per_incident", 2))
        self.max_per_session = int(policy_recovery.get("max_attempts_per_operator_session", 4))

    def classify(self, signature: str | None, *, evidence_ok: bool) -> str:
        """Return next action: recover | review_required | disabled."""
        if not self.enabled:
            return "review_required"
        if not evidence_ok or not signature:
            return "review_required"
        if self.known_only and signature not in KNOWN_SIGNATURES:
            return "review_required"
        if not recipes_for_signature(self.profiles, signature):
            return "review_required"
        return "recover"

    def begin_incident(self, signature: str, incident_id: str) -> None:
        self.ledger.signature = signature
        self.ledger.incident_id = incident_id
        self.ledger.incident_attempts = 0
        self.ledger.first_warning_monotonic_s = self._now()

    def reserve_attempt(self, recipe: RecoveryRecipe) -> dict[str, Any]:
        """Atomically reserve before apply. Exceeded budget → review_required."""
        if self.ledger.session_attempts >= self.max_per_session:
            return {"ok": False, "reason": "session_budget_exhausted", "action": "review_required"}
        if self.ledger.incident_attempts >= self.max_per_incident:
            return {"ok": False, "reason": "incident_budget_exhausted", "action": "review_required"}
        if recipe.recipe_id in self.ledger.attempted_recipe_ids:
            if not self.policy.get("allow_repeated_failed_recipe", False):
                return {"ok": False, "reason": "recipe_already_attempted", "action": "review_required"}

        self.ledger.session_attempts += 1
        self.ledger.incident_attempts += 1
        self.ledger.attempted_recipe_ids.append(recipe.recipe_id)
        record = {
            "recipe_id": recipe.recipe_id,
            "signature": recipe.signature,
            "reserved_at": self._now(),
            "status": "reserved",
        }
        self.ledger.outcomes.append(record)
        return {"ok": True, "recipe": recipe, "action": "apply", "record": record}

    def next_recipe(self, signature: str) -> RecoveryRecipe | None:
        attempted = set(self.ledger.attempted_recipe_ids)
        for recipe in recipes_for_signature(self.profiles, signature):
            if recipe.recipe_id not in attempted:
                return recipe
        return None

    def mark_outcome(self, recipe_id: str, status: str, detail: str | None = None) -> None:
        for row in reversed(self.ledger.outcomes):
            if row.get("recipe_id") == recipe_id and row.get("status") == "reserved":
                row["status"] = status
                if detail:
                    row["detail"] = detail
                row["completed_at"] = self._now()
                return
        self.ledger.outcomes.append(
            {
                "recipe_id": recipe_id,
                "status": status,
                "detail": detail,
                "completed_at": self._now(),
            }
        )
