"""Per-block deadline guard with a fixed, reviewed late-block tolerance.

The 4 ms per-block compute budget is unchanged. This guard decides what a
block that exceeds it means:

* any block over ``hard_cap_s`` is a hard fault;
* a late block is counted and reported, never hidden;
* ``max_consecutive`` late blocks in a row, or more than ``max_per_window``
  late blocks inside the last ``window_blocks`` blocks, is a hard fault.

Tolerance values come only from the validated static policy file. Nothing here
adapts at runtime, learns, or widens a limit after a fault, and a raised
``BlockDeadlineExceeded`` is a permanent stop (no automatic resume). Simulated
time is never caught up for a late block: the clock owner caps catch-up.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Mapping


class BlockDeadlineExceeded(RuntimeError):
    """Raised when neural block timing breaks the configured safety limits."""

    def __init__(
        self,
        elapsed_s: float,
        budget_s: float,
        *,
        reason: str = "budget",
        detail: str = "",
    ) -> None:
        self.elapsed_s = elapsed_s
        self.budget_s = budget_s
        self.reason = reason
        if reason == "budget":
            message = (
                f"neural block exceeded compute budget: "
                f"{elapsed_s:.6f}s > {budget_s:.6f}s"
            )
        elif reason == "hard_cap":
            message = (
                f"neural block exceeded hard time cap: "
                f"{elapsed_s:.6f}s > {budget_s:.6f}s"
            )
        else:
            message = (
                f"neural blocks were repeatedly late ({detail}); "
                f"latest {elapsed_s:.6f}s > budget {budget_s:.6f}s"
            )
        super().__init__(message)


@dataclass
class LateBlockGuard:
    budget_s: float
    hard_cap_s: float
    max_consecutive: int
    max_per_window: int
    window_blocks: int
    total_late: int = 0
    consecutive_late: int = 0
    worst_late_s: float = 0.0
    _recent: deque[bool] = field(default_factory=deque, repr=False)

    @classmethod
    def from_policy(cls, policy: Mapping[str, Any]) -> LateBlockGuard:
        budget = float(policy["max_block_compute_s"])
        physics = float(policy["physics_dt_s"])
        cap = policy.get("late_block_hard_cap_s")
        return cls(
            budget_s=budget,
            hard_cap_s=budget if cap is None else float(cap),
            max_consecutive=int(policy.get("late_block_max_consecutive", 0)),
            max_per_window=int(policy.get("late_block_max_per_second", 0)),
            window_blocks=max(1, round(1.0 / physics)),
        )

    def __post_init__(self) -> None:
        if self.budget_s <= 0 or self.hard_cap_s < self.budget_s:
            raise ValueError("hard cap must be at least the block budget")
        if self.max_consecutive < 0 or self.max_per_window < 0:
            raise ValueError("late-block tolerances must not be negative")
        self._recent = deque(maxlen=self.window_blocks)

    def observe(self, elapsed_s: float) -> bool:
        """Record one committed block. Returns True if it was late.

        Raises ``BlockDeadlineExceeded`` when a fixed limit is broken.
        """
        if elapsed_s > self.hard_cap_s:
            reason = "budget" if self.hard_cap_s == self.budget_s else "hard_cap"
            raise BlockDeadlineExceeded(elapsed_s, self.hard_cap_s, reason=reason)
        late = elapsed_s > self.budget_s
        self._recent.append(late)
        if late:
            self.total_late += 1
            self.consecutive_late += 1
            self.worst_late_s = max(self.worst_late_s, elapsed_s)
        else:
            self.consecutive_late = 0
        if late and self.consecutive_late > self.max_consecutive:
            if self.max_consecutive == 0 and self.max_per_window == 0:
                raise BlockDeadlineExceeded(elapsed_s, self.budget_s)
            raise BlockDeadlineExceeded(
                elapsed_s,
                self.budget_s,
                reason="sustained",
                detail=f"{self.consecutive_late} in a row",
            )
        recent_late = sum(self._recent)
        if recent_late > self.max_per_window:
            raise BlockDeadlineExceeded(
                elapsed_s,
                self.budget_s,
                reason="sustained",
                detail=f"{recent_late} in the last second",
            )
        return late

    def status(self) -> dict[str, Any]:
        return {
            "late_blocks_total": self.total_late,
            "late_blocks_in_a_row": self.consecutive_late,
            "late_blocks_last_second": int(sum(self._recent)),
            "worst_late_block_s": self.worst_late_s,
            "late_block_max_in_a_row": self.max_consecutive,
            "late_block_max_per_second": self.max_per_window,
            "late_block_hard_cap_s": self.hard_cap_s,
        }
