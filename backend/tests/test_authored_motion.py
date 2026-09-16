import json
from pathlib import Path

import pytest

from flysim.authored import AuthoredAnimationController, AuthoredMotionConfig
from flysim.clock import PresentationClock
from flysim.lif import lif_module_is_inert, start_lif_worker
from flysim.world import CURSOR_YIELD_SPEED, DesktopWorld

REPO = Path(__file__).resolve().parents[2]


def test_policy_still_disables_real_graph():
    policy = json.loads((REPO / "config" / "policy.json").read_text())
    assert policy["real_graph_enabled"] is False
    assert lif_module_is_inert(policy) is True


def test_presentation_clock_does_not_catch_up_after_stall():
    clock = PresentationClock(dt_s=0.005)
    clock.tick(0.0)
    advanced = clock.tick(2.0)
    assert advanced <= 0.05 + 1e-9
    assert clock.sim_time_s <= 0.06 + 1e-9


def test_presentation_clock_stops():
    clock = PresentationClock(dt_s=0.005)
    clock.tick(0.0)
    clock.stop()
    assert clock.tick(1.0) == 0.0


def test_authored_controller_cycles_finite_locomotion():
    controller = AuthoredAnimationController(
        config=AuthoredMotionConfig(idle_hold_s=0.01, crawl_hold_s=0.01, flight_hold_s=0.01)
    )
    t = 0.0
    seen = set()
    for _ in range(40):
        t += 0.02
        pose = controller.step(t)
        seen.add(pose.locomotion)
    assert seen == {"idle", "crawl", "flight"}
    assert controller.status()["controller"] == "authored_animation"
    assert controller.status()["neural_worker_running"] is False
    assert all(item["source"] in {"authored_policy", "operator_command", "geometry_rule"} for item in controller.status()["transitions"])


def test_find_fly_works_without_neural_worker():
    controller = AuthoredAnimationController()
    controller.world.hide(sim_time_s=0.0)
    assert controller.world.pose.visible is False
    pose = controller.find_fly(100.0, 150.0, host_surface_id="host-1")
    assert pose.visible is True
    assert pose.x == 100.0
    assert pose.y == 150.0
    assert pose.locomotion == "idle"
    assert pose.host_surface_id == "host-1"
    assert controller.neural_worker_running is False


def test_cursor_yield_is_bounded_and_cools_down():
    world = DesktopWorld(x=0.0, y=0.0)
    first = world.apply_cursor_yield(cursor_x=1.0, cursor_y=0.0, cursor_moving=True, sim_time_s=0.0)
    assert first == CURSOR_YIELD_SPEED
    during = world.apply_cursor_yield(cursor_x=1.0, cursor_y=0.0, cursor_moving=True, sim_time_s=0.1)
    assert during == CURSOR_YIELD_SPEED
    ended = world.apply_cursor_yield(cursor_x=1.0, cursor_y=0.0, cursor_moving=True, sim_time_s=0.26)
    assert ended == 0.0
    assert world.apply_cursor_yield(cursor_x=1.0, cursor_y=0.0, cursor_moving=True, sim_time_s=0.5) == 0.0


def test_lif_worker_refuses_to_start_while_disabled():
    with pytest.raises(RuntimeError, match="real_graph_enabled is false"):
        start_lif_worker()


def test_invalid_locomotion_rejected():
    world = DesktopWorld()
    with pytest.raises(ValueError, match="Invalid locomotion"):
        world.set_locomotion("seek", source="authored_policy", sim_time_s=0.0)  # type: ignore[arg-type]
