"""Late-block deadline guard: bounded, fixed tolerance; hard faults stay hard."""

from __future__ import annotations

import pytest

from flysim.config import Policy, load_policy, load_policy_dict
from flysim.deadline import BlockDeadlineExceeded, LateBlockGuard

BUDGET = 0.004
OK = 0.0005
LATE = 0.0045


def _strict() -> LateBlockGuard:
    return LateBlockGuard(
        budget_s=BUDGET, hard_cap_s=BUDGET, max_consecutive=0, max_per_window=0, window_blocks=200
    )


def _approved() -> LateBlockGuard:
    return LateBlockGuard.from_policy(load_policy_dict())


def test_missing_tolerance_is_strict_any_late_block_faults():
    guard = LateBlockGuard.from_policy(
        {"max_block_compute_s": BUDGET, "physics_dt_s": 0.005}
    )
    assert guard.observe(OK) is False
    with pytest.raises(BlockDeadlineExceeded, match="exceeded compute budget"):
        guard.observe(LATE)


def test_committed_policy_uses_the_reviewed_values():
    guard = _approved()
    assert guard.budget_s == BUDGET
    assert guard.max_consecutive == 2
    assert guard.max_per_window == 6
    assert guard.hard_cap_s == 0.05
    assert guard.window_blocks == 200


def test_isolated_late_block_is_counted_and_not_hidden():
    guard = _approved()
    for _ in range(10):
        guard.observe(OK)
    assert guard.observe(LATE) is True
    for _ in range(10):
        guard.observe(OK)
    status = guard.status()
    assert status["late_blocks_total"] == 1
    assert status["late_blocks_in_a_row"] == 0
    assert status["worst_late_block_s"] == pytest.approx(LATE)


def test_three_late_blocks_in_a_row_is_a_hard_fault():
    guard = _approved()
    guard.observe(LATE)
    guard.observe(LATE)
    with pytest.raises(BlockDeadlineExceeded, match="repeatedly late"):
        guard.observe(LATE)


def test_consecutive_run_resets_after_an_on_time_block():
    guard = _approved()
    for _ in range(50):
        guard.observe(LATE)
        guard.observe(LATE)
        guard.observe(OK)
        # Re-create when the per-second rate would trip; this loop only checks reset.
        guard._recent.clear()
    assert guard.consecutive_late == 0


def test_too_many_late_blocks_inside_one_second_is_a_hard_fault():
    guard = _approved()
    with pytest.raises(BlockDeadlineExceeded, match="in the last second"):
        for _ in range(7):
            guard.observe(LATE)
            guard.observe(OK)


def test_late_blocks_age_out_of_the_one_second_window():
    guard = _approved()
    for _ in range(6):
        guard.observe(LATE)
        guard.observe(OK)
    for _ in range(guard.window_blocks):
        guard.observe(OK)
    assert guard.status()["late_blocks_last_second"] == 0
    assert guard.observe(LATE) is True


def test_single_block_over_hard_cap_is_always_a_hard_fault():
    guard = _approved()
    with pytest.raises(BlockDeadlineExceeded, match="hard time cap"):
        guard.observe(0.051)


def test_strict_guard_has_no_tolerance_even_for_one_block():
    with pytest.raises(BlockDeadlineExceeded):
        _strict().observe(LATE)


def test_policy_rejects_out_of_range_or_inconsistent_tolerances():
    base = load_policy().model_dump()
    for patch in (
        {"late_block_max_consecutive": 5},
        {"late_block_max_consecutive": -1},
        {"late_block_max_per_second": 13},
        {"late_block_hard_cap_s": 0.5},
        {"late_block_hard_cap_s": 0.001},
        {"late_block_max_consecutive": True},
        {"late_block_max_per_second": 1, "late_block_max_consecutive": 2},
    ):
        with pytest.raises(Exception):
            Policy.model_validate({**base, **patch})


def test_recovery_still_forbids_threshold_relaxation_and_auto_resume():
    policy = load_policy()
    assert policy.recovery.allow_threshold_relaxation is False
    assert policy.auto_restart_after_hard_fault is False
    assert policy.max_block_compute_s == BUDGET
