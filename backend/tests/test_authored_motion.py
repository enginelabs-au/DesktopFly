"""Tests for the authored-animation live path."""

from __future__ import annotations

import json
import math
from pathlib import Path

from flysim.authored import AuthoredAnimationController, AuthoredMotionConfig, load_desktop_pet_config
from flysim.clock import PresentationClock
from flysim.world import DesktopBounds, WorldPose, scale_for_depth

ROOT = Path(__file__).resolve().parents[2]


def test_clock_bounds_catch_up_after_stall():
    clock = PresentationClock(max_catch_up_s=0.05)
    clock.set_fake_wall_s(0.0)
    assert clock.advance() == 0.0
    clock.advance_fake_wall(10.0)
    dt = clock.advance()
    assert math.isclose(dt, 0.05)
    assert math.isclose(clock.sim_time_s, 0.05)


def test_clock_does_not_advance_when_stopped():
    clock = PresentationClock()
    clock.set_fake_wall_s(1.0)
    clock.advance()
    clock.advance_fake_wall(0.1)
    clock.stop()
    assert clock.advance() == 0.0


def test_scale_for_depth():
    assert math.isclose(scale_for_depth(0.0), 1.0)
    assert math.isclose(scale_for_depth(1.0), 0.65)


def test_follow_window_moves_toward_host():
    clock = PresentationClock(max_catch_up_s=0.05)
    clock.set_fake_wall_s(0.0)
    ctrl = AuthoredAnimationController(
        clock=clock,
        config=AuthoredMotionConfig(cruise_speed_points_s=120.0),
        bounds=DesktopBounds(0, 0, 1000, 800),
        mode="follow_my_window",
    )
    ctrl.set_host_window((800, 100, 200, 400))
    start = ctrl.pose
    for _ in range(40):
        clock.advance_fake_wall(0.05)
        ctrl.step()
    assert ctrl.pose.x > start.x
    assert math.isfinite(ctrl.pose.heading_rad)
    assert ctrl.pose.transition_source in {"authored", "geometry", "operator"}


def test_find_fly_works_without_neural_worker():
    ctrl = AuthoredAnimationController(mode="explore_and_hide")
    ctrl.begin_hide_flight()
    pose = ctrl.find_fly()
    assert pose.visible is True
    assert pose.depth01 == 0.0
    assert pose.transition_source == "operator"
    assert pose.locomotion == "idle"


def test_cursor_yield_is_bounded():
    clock = PresentationClock(max_catch_up_s=0.05)
    clock.set_fake_wall_s(0.0)
    cfg = AuthoredMotionConfig(cursor_yield_max_speed_points_s=40.0)
    ctrl = AuthoredAnimationController(clock=clock, config=cfg)
    ctrl.pose = WorldPose(
        x=100.0,
        y=100.0,
        heading_rad=0.0,
        speed_points_s=0.0,
        depth01=0.0,
        locomotion="idle",
    )
    ctrl.set_cursor((100.0, 100.0), moving=True)
    # Coincident cursor uses deterministic outward path via zero-dist guard.
    ctrl.set_cursor((90.0, 100.0), moving=True)
    for _ in range(5):
        clock.advance_fake_wall(0.05)
        ctrl.step()
    assert ctrl.pose.speed_points_s <= cfg.max_speed_points_s + 1e-6
    assert ctrl.pose.x >= 100.0 - 1e-6


def test_desktop_pet_config_enables_authored_path():
    data = load_desktop_pet_config(ROOT / "config" / "desktop-pet.json")
    assert data["authored_animation_when_graph_disabled"] is True
    assert data["find_fly_available_without_neural_worker"] is True
    assert data["cursor_yield_radius_points"] == 40
    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    assert policy["real_graph_enabled"] is False
