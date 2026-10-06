"""Plain-language software health mapping.

Healthy means checked software operation within declared limits.
It never means proven absence of experience, feelings, or consciousness.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


HEALTH_DISCLAIMER = (
    "Health describes software operation, not feelings or consciousness."
)

QUIET_NOTE = "No food, sleep, reward, or attention is needed."


class OperatorStatus(str, Enum):
    HEALTHY_RUNNING = "healthy_running"
    HEALTHY_QUIET = "healthy_quiet"
    ATTENTION = "attention"
    RECOVERING = "recovering"
    CHECKING = "checking"
    PAUSED = "paused"
    REVIEW_REQUIRED = "review_required"
    STOPPED = "stopped"


_COPY: dict[OperatorStatus, dict[str, str]] = {
    OperatorStatus.HEALTHY_RUNNING: {
        "title": "Healthy — running normally",
        "explanation": "Current operating checks pass.",
        "doing": "Continuing as configured.",
        "operator_action": "No action needed.",
    },
    OperatorStatus.HEALTHY_QUIET: {
        "title": "Healthy — quiet and idle",
        "explanation": "The fly is inactive and the checks still pass.",
        "doing": "Remaining idle; quiet input is valid.",
        "operator_action": "No action needed.",
    },
    OperatorStatus.ATTENTION: {
        "title": "Attention — approaching a limit",
        "explanation": "A measured condition is nearing its operating limit.",
        "doing": "Preparing an approved remedy.",
        "operator_action": "No action needed unless recovery fails.",
    },
    OperatorStatus.RECOVERING: {
        "title": "Recovering — fixing a problem",
        "explanation": "The cause matches a recognized software issue.",
        "doing": "Applying a bounded recovery recipe.",
        "operator_action": "No action needed.",
    },
    OperatorStatus.CHECKING: {
        "title": "Checking the fix",
        "explanation": "The repair is installed and passing initial checks.",
        "doing": "Running the supervised verification period.",
        "operator_action": "No action needed.",
    },
    OperatorStatus.PAUSED: {
        "title": "Paused",
        "explanation": "Execution is paused by the operator or a protective condition.",
        "doing": "Holding state; no deterioration is modeled.",
        "operator_action": "Resume when ready, or Stop to end the session.",
    },
    OperatorStatus.REVIEW_REQUIRED: {
        "title": "Paused — needs review",
        "explanation": "The cause is unknown, monitoring is incomplete, or recovery failed.",
        "doing": "Model execution is stopped; evidence is preserved.",
        "operator_action": "Review the recorded problem before starting a new session.",
    },
    OperatorStatus.STOPPED: {
        "title": "Stopped",
        "explanation": "The operator stopped or a hard fault ended the session.",
        "doing": "Session is terminal; no automatic restart.",
        "operator_action": "Start a new session only after review if a fault occurred.",
    },
}


FORBIDDEN_PHRASES = (
    "suffering",
    "frightened",
    "hungry",
    "tired",
    "lonely",
    "consciousness",
    "feelings",
    "needs care",
    "neglected",
)


@dataclass(frozen=True)
class HealthView:
    status: OperatorStatus
    title: str
    explanation: str
    doing: str
    operator_action: str
    disclaimer: str
    cards: dict[str, str]
    quiet_note: str | None = None
    technical: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "status": self.status.value,
            "title": self.title,
            "explanation": self.explanation,
            "doing": self.doing,
            "operator_action": self.operator_action,
            "disclaimer": self.disclaimer,
            "cards": dict(self.cards),
            "technical": dict(self.technical or {}),
        }
        if self.quiet_note:
            payload["quiet_note"] = self.quiet_note
        return payload


def _assert_plain_language(text: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered and phrase not in HEALTH_DISCLAIMER.lower():
            # Disclaimer may mention consciousness/feelings to deny them.
            if phrase in ("consciousness", "feelings") and "not" in lowered:
                continue
            raise ValueError(f"health copy must not claim {phrase!r}: {text}")


def map_lifecycle_to_status(
    lifecycle: str,
    *,
    quiet: bool = False,
    approaching_limit: bool = False,
) -> OperatorStatus:
    key = lifecycle.lower()
    if key in {"fault", "stopped"}:
        return OperatorStatus.STOPPED
    if key in {"review_required"}:
        return OperatorStatus.REVIEW_REQUIRED
    if key in {"paused"}:
        return OperatorStatus.PAUSED
    if key in {"recovering"}:
        return OperatorStatus.RECOVERING
    if key in {"checking"}:
        return OperatorStatus.CHECKING
    if key in {"running", "ready", "starting"}:
        if approaching_limit:
            return OperatorStatus.ATTENTION
        if quiet:
            return OperatorStatus.HEALTHY_QUIET
        return OperatorStatus.HEALTHY_RUNNING
    return OperatorStatus.REVIEW_REQUIRED


def build_health_view(
    lifecycle: str,
    *,
    quiet: bool = False,
    approaching_limit: bool = False,
    cards: dict[str, str] | None = None,
    technical: dict[str, Any] | None = None,
) -> HealthView:
    status = map_lifecycle_to_status(
        lifecycle, quiet=quiet, approaching_limit=approaching_limit
    )
    copy = _COPY[status]
    for value in copy.values():
        _assert_plain_language(value)

    default_cards = {
        "signal_activity": "within limits",
        "movement": "quietly idle" if quiet else "moving as intended",
        "surroundings": "input current",
        "keeping_up": "on time",
        "rules_intact": "checked",
        "automatic_recovery": "no action needed",
    }
    if status is OperatorStatus.REVIEW_REQUIRED:
        default_cards["automatic_recovery"] = "paused for review"
    elif status in {OperatorStatus.RECOVERING, OperatorStatus.CHECKING, OperatorStatus.ATTENTION}:
        default_cards["automatic_recovery"] = "action and attempt"

    merged = {**default_cards, **(cards or {})}
    quiet_note = QUIET_NOTE if status is OperatorStatus.HEALTHY_QUIET else None
    return HealthView(
        status=status,
        title=copy["title"],
        explanation=copy["explanation"],
        doing=copy["doing"],
        operator_action=copy["operator_action"],
        disclaimer=HEALTH_DISCLAIMER,
        cards=merged,
        quiet_note=quiet_note,
        technical=technical or {},
    )


def warning_message(
    what_happened: str,
    what_i_did: str,
    what_happens_next: str,
    what_you_need_to_do: str,
) -> dict[str, str]:
    parts = {
        "what_happened": what_happened,
        "what_i_did": what_i_did,
        "what_happens_next": what_happens_next,
        "what_you_need_to_do": what_you_need_to_do,
    }
    for value in parts.values():
        _assert_plain_language(value)
    return parts
