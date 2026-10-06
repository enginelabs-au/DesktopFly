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
    """The reviewed counts and 250 ms cap with wall faults switched on."""
    return LateBlockGuard.from_policy({**load_policy_dict(), "late_block_wall_fault": True})


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
    assert guard.hard_cap_s == 0.25
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
        guard.observe(0.251)


def test_strict_guard_has_no_tolerance_even_for_one_block():
    with pytest.raises(BlockDeadlineExceeded):
        _strict().observe(LATE)


def test_policy_rejects_out_of_range_or_inconsistent_tolerances():
    base = load_policy().model_dump()
    for patch in (
        {"late_block_max_consecutive": 5},
        {"late_block_max_consecutive": -1},
        {"late_block_max_per_second": 13},
        {"late_block_hard_cap_s": 0.26},
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


def test_blocks_per_request_is_bounded_and_defaults_to_one():
    from flysim.desktop_neural import _MAX_BLOCKS_PER_REQUEST, _clamp_blocks

    assert _clamp_blocks(None) == 1
    assert _clamp_blocks("nope") == 1
    assert _clamp_blocks(0) == 1
    assert _clamp_blocks(-5) == 1
    assert _clamp_blocks(10) == 10
    assert _clamp_blocks(10_000) == _MAX_BLOCKS_PER_REQUEST


def test_worker_process_runs_a_batched_request_and_reports_every_block():
    import json
    import subprocess
    import sys
    from pathlib import Path

    backend = Path(__file__).resolve().parents[1]
    proc = subprocess.Popen(
        [sys.executable, "-m", "flysim.desktop_neural"],
        cwd=backend,
        env={"PYTHONPATH": str(backend), "PATH": "/usr/bin:/bin"},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        ready = json.loads(proc.stdout.readline())
        assert ready["ok"] and ready["event"] == "ready"
        proc.stdin.write(json.dumps({"op": "step", "dt_s": 0.005, "blocks": 10}) + "\n")
        proc.stdin.flush()
        reply = json.loads(proc.stdout.readline())
        assert reply["ok"] is True
        assert len(reply["motors"]) == 10
        assert reply["motor"] == reply["motors"][-1]
        assert all("turn" in m for m in reply["motors"])
        assert reply["technical"]["committed_tick"] == 10 * 5
        assert "late_blocks_total" in reply["technical"]["timing"]
    finally:
        try:
            proc.stdin.write(json.dumps({"op": "shutdown"}) + "\n")
            proc.stdin.flush()
        except Exception:
            pass
        proc.kill()
        proc.wait(timeout=10)


def test_real_compute_over_budget_is_always_a_hard_fault_with_no_tolerance():
    guard = _approved()
    # Wall time is within the cap, but the CPU actually spent computing is over budget.
    with pytest.raises(BlockDeadlineExceeded, match="too much compute"):
        guard.observe(0.006, cpu_s=0.0045)


def test_paused_process_is_late_but_not_a_compute_overrun():
    guard = _approved()
    assert guard.observe(0.030, cpu_s=0.0012) is True
    assert guard.status()["worst_block_cpu_s"] == pytest.approx(0.0012)
    assert guard.status()["late_blocks_total"] == 1


def test_a_long_os_stall_under_the_cap_is_tolerated_once_but_over_it_is_fatal():
    guard = _approved()
    assert guard.observe(0.054, cpu_s=0.0011) is True
    guard.observe(0.0005, cpu_s=0.0004)
    with pytest.raises(BlockDeadlineExceeded, match="hard time cap"):
        guard.observe(0.26, cpu_s=0.0011)


def test_committed_policy_makes_host_stalls_non_fatal_but_still_counted():
    policy = load_policy_dict()
    assert policy["late_block_wall_fault"] is False
    guard = LateBlockGuard.from_policy(policy)
    for _ in range(50):
        assert guard.observe(0.5, cpu_s=0.001) is True  # far past any cap, long run
    status = guard.status()
    assert status["late_blocks_total"] == 50
    assert status["late_blocks_are_fatal"] is False
    assert status["worst_late_block_s"] == pytest.approx(0.5)


def test_real_compute_over_budget_is_fatal_even_when_stalls_are_not():
    guard = LateBlockGuard.from_policy(load_policy_dict())
    with pytest.raises(BlockDeadlineExceeded, match="too much compute"):
        guard.observe(0.006, cpu_s=0.0045)


def test_policy_wall_fault_flag_must_be_a_real_boolean():
    raw = load_policy_dict()
    for bad in ("no", 0, None):
        with pytest.raises(Exception):
            Policy.model_validate({**raw, "late_block_wall_fault": bad})


def test_scheduled_reset_returns_to_initial_state_and_keeps_weights():
    import numpy as np

    from flysim.presentation import ConnectomePresentationEngine

    policy = load_policy_dict()
    assert policy["scheduled_state_reset_s"] == 300
    engine = ConnectomePresentationEngine.create(policy)
    initial = engine.worker.lif.initial_state()
    src_before = np.array(engine.worker.lif._src, copy=True)
    for _ in range(40):
        engine.step(0.005, {"ambient_drive": 2.0})
    engine.scheduled_reset()
    state = engine.worker.state
    state = state.as_numpy() if hasattr(state, "as_numpy") else state
    init = initial.as_numpy() if hasattr(initial, "as_numpy") else initial
    assert np.array_equal(np.asarray(state.v), np.asarray(init.v))
    assert np.array_equal(np.asarray(engine.worker.lif._src), src_before)
    assert engine.worker.running is True


def test_worker_runs_a_planned_reset_after_300_simulated_seconds():
    import json
    import subprocess
    import sys
    from pathlib import Path

    backend = Path(__file__).resolve().parents[1]
    proc = subprocess.Popen(
        [sys.executable, "-m", "flysim.desktop_neural"],
        cwd=backend,
        env={"PYTHONPATH": str(backend), "PATH": "/usr/bin:/bin"},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert json.loads(proc.stdout.readline())["event"] == "ready"
        resets_seen = []
        # 20 blocks x 5 ms = 0.1 s of fly time per request; 3,010 requests > 300 s.
        for _ in range(3010):
            proc.stdin.write(json.dumps({"op": "step", "dt_s": 0.005, "blocks": 20}) + "\n")
            proc.stdin.flush()
            reply = json.loads(proc.stdout.readline())
            assert reply["ok"] is True, reply
            resets_seen.append(reply["technical"]["scheduled_state_resets"])
        assert resets_seen[0] == 0
        assert resets_seen[-1] == 1
        # The planned reset never stops or faults the worker.
        assert resets_seen.count(0) < len(resets_seen)
    finally:
        try:
            proc.stdin.write(json.dumps({"op": "shutdown"}) + "\n")
            proc.stdin.flush()
        except Exception:
            pass
        proc.kill()
        proc.wait(timeout=10)
