"""Explicitly authored animation controller (live path while Q-012 is open)."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from flysim.clock import PresentationClock
from flysim.world import (
    DesktopBounds,
    WorldPose,
    ease_smoothstep,
    integrate_pose,
    wrap_heading,
)

Mode = Literal["follow_my_window", "explore_and_hide"]


@dataclass(frozen=True)
class AuthoredMotionConfig:
    physics_dt_s: float = 0.005
    cruise_speed_points_s: float = 80.0
    max_speed_points_s: float = 160.0
    wander_turn_rad_s: float = 0.35
    cursor_yield_radius_points: float = 40.0
    cursor_yield_max_speed_points_s: float = 40.0
    cursor_yield_duration_s: float = 0.25
    cursor_yield_cooldown_s: float = 0.75
    depth_transition_s: float = 0.8
    wing_beat_hz: float = 8.0

    @classmethod
    def from_desktop_pet(cls, data: dict[str, Any]) -> AuthoredMotionConfig:
        return cls(
            cruise_speed_points_s=float(data.get("cruise_speed_points_s", 80.0)),
            max_speed_points_s=float(data.get("max_speed_points_s", 160.0)),
            cursor_yield_radius_points=float(
                data.get("cursor_yield_radius_points", 40.0)
            ),
            cursor_yield_max_speed_points_s=float(
                data.get("cursor_yield_max_speed_points_s", 40.0)
            ),
            cursor_yield_duration_s=float(data.get("cursor_yield_duration_ms", 250))
            / 1000.0,
            cursor_yield_cooldown_s=float(data.get("cursor_yield_cooldown_ms", 750))
            / 1000.0,
            depth_transition_s=float(data.get("depth_transition_ms", 800)) / 1000.0,
            wing_beat_hz=float(data.get("wing_beat_hz", 8.0)),
        )


def load_desktop_pet_config(path: Path | None = None) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    config_path = path or (root / "config" / "desktop-pet.json")
    return json.loads(config_path.read_text(encoding="utf-8"))


class AuthoredAnimationController:
    """Deterministic presentation controller. Not a neural or affect model."""

    def __init__(
        self,
        *,
        clock: PresentationClock | None = None,
        config: AuthoredMotionConfig | None = None,
        bounds: DesktopBounds | None = None,
        mode: Mode = "follow_my_window",
    ) -> None:
        self.clock = clock or PresentationClock()
        self.config = config or AuthoredMotionConfig()
        self.bounds = bounds or DesktopBounds(0.0, 0.0, 1440.0, 900.0)
        self.mode: Mode = mode
        self.pose = WorldPose(
            x=self.bounds.x + self.bounds.width * 0.5,
            y=self.bounds.y + self.bounds.height * 0.5,
            heading_rad=0.0,
            speed_points_s=0.0,
            depth01=0.0,
            locomotion="idle",
            visible=True,
            transition_source="authored",
        )
        self._host_rect: tuple[float, float, float, float] | None = None
        self._cursor: tuple[float, float] | None = None
        self._cursor_moving = False
        self._yield_until_s = -1.0
        self._yield_cooldown_until_s = -1.0
        self._depth_from = 0.0
        self._depth_to = 0.0
        self._depth_t0 = 0.0
        self._depth_active = False
        self._hidden = False
        self._accumulator_s = 0.0

    def set_host_window(self, rect: tuple[float, float, float, float] | None) -> None:
        self._host_rect = rect

    def set_cursor(self, point: tuple[float, float] | None, *, moving: bool) -> None:
        self._cursor = point
        self._cursor_moving = moving

    def find_fly(self) -> WorldPose:
        """Reveal at a validated visible position without starting a neural worker."""
        self._hidden = False
        self._depth_active = False
        if self._host_rect is not None:
            x = self._host_rect[0] + self._host_rect[2] * 0.5
            y = self._host_rect[1] + self._host_rect[3] * 0.15
            host_id = "host-window"
        else:
            x = self.bounds.x + self.bounds.width * 0.5
            y = self.bounds.y + self.bounds.height * 0.5
            host_id = None
        x, y = self.bounds.clamp_point(x, y)
        self.pose = WorldPose(
            x=x,
            y=y,
            heading_rad=self.pose.heading_rad,
            speed_points_s=0.0,
            depth01=0.0,
            locomotion="idle",
            host_surface_id=host_id,
            visible=True,
            transition_source="operator",
        )
        return self.pose

    def begin_hide_flight(self) -> None:
        if self.mode != "explore_and_hide":
            return
        self._hidden = True
        self._depth_from = self.pose.depth01
        self._depth_to = 1.0
        self._depth_t0 = self.clock.sim_time_s
        self._depth_active = True

    def step(self) -> WorldPose:
        dt = self.clock.advance()
        self._accumulator_s += dt
        while self._accumulator_s >= self.config.physics_dt_s:
            self._integrate(self.config.physics_dt_s)
            self._accumulator_s -= self.config.physics_dt_s
        return self.pose

    def wing_phase(self) -> float:
        """Presentation-only wing cycle in [0, 1). Not neural evidence."""
        return (self.clock.sim_time_s * self.config.wing_beat_hz) % 1.0

    def _integrate(self, dt_s: float) -> None:
        speed = 0.0
        turn = 0.0
        locomotion = self.pose.locomotion
        source = "authored"

        if self._hidden and self.mode == "explore_and_hide":
            locomotion = "flight"
            speed = self.config.cruise_speed_points_s * 0.5
            turn = self.config.wander_turn_rad_s
        elif self.mode == "follow_my_window" and self._host_rect is not None:
            tx = self._host_rect[0] + self._host_rect[2] * 0.5
            ty = self._host_rect[1] + self._host_rect[3] * 0.12
            dx = tx - self.pose.x
            dy = ty - self.pose.y
            dist = math.hypot(dx, dy)
            if dist > 4.0:
                desired = math.atan2(dy, dx)
                err = wrap_heading(desired - self.pose.heading_rad)
                turn = max(-2.0, min(2.0, err / max(dt_s, 1e-6)))
                speed = min(self.config.cruise_speed_points_s, dist * 2.0)
                locomotion = "crawl" if self.pose.depth01 < 0.15 else "flight"
            else:
                locomotion = "idle"
                speed = 0.0
            source = "geometry"
        else:
            locomotion = "idle" if self.pose.speed_points_s < 1.0 else "flight"
            speed = 0.0

        yield_vx, yield_vy = self._cursor_yield_velocity()
        if yield_vx or yield_vy:
            source = "geometry"
            speed = min(
                self.config.max_speed_points_s,
                math.hypot(
                    math.cos(self.pose.heading_rad) * speed + yield_vx,
                    math.sin(self.pose.heading_rad) * speed + yield_vy,
                ),
            )
            if speed > 0:
                turn = wrap_heading(
                    math.atan2(
                        math.sin(self.pose.heading_rad) * speed + yield_vy,
                        math.cos(self.pose.heading_rad) * speed + yield_vx,
                    )
                    - self.pose.heading_rad
                ) / max(dt_s, 1e-6)

        depth = self._update_depth()
        host_id = "host-window" if self._host_rect is not None else None
        self.pose = integrate_pose(
            self.pose,
            dt_s=dt_s,
            speed_points_s=speed,
            turn_rate_rad_s=turn,
            bounds=self.bounds,
            locomotion=locomotion,
            depth01=depth,
            transition_source=source,
        )
        self.pose = replace(self.pose, host_surface_id=host_id)
        if self._hidden and depth >= 0.99:
            self.pose = WorldPose(
                x=self.pose.x,
                y=self.pose.y,
                heading_rad=self.pose.heading_rad,
                speed_points_s=0.0,
                depth01=1.0,
                locomotion="idle",
                host_surface_id=self.pose.host_surface_id,
                visible=False,
                transition_source="operator",
            )

    def _update_depth(self) -> float:
        if not self._depth_active:
            return self.pose.depth01
        dur = max(0.4, min(1.2, self.config.depth_transition_s))
        t = (self.clock.sim_time_s - self._depth_t0) / dur
        if t >= 1.0:
            self._depth_active = False
            return self._depth_to
        return self._depth_from + (self._depth_to - self._depth_from) * ease_smoothstep(t)

    def _cursor_yield_velocity(self) -> tuple[float, float]:
        cfg = self.config
        now = self.clock.sim_time_s
        if self._cursor is None or not self._cursor_moving:
            return (0.0, 0.0)
        cx, cy = self._cursor
        dx = self.pose.x - cx
        dy = self.pose.y - cy
        dist = math.hypot(dx, dy)
        if dist > cfg.cursor_yield_radius_points or dist == 0.0:
            return (0.0, 0.0)
        if now < self._yield_cooldown_until_s:
            return (0.0, 0.0)
        if now > self._yield_until_s:
            self._yield_until_s = now + cfg.cursor_yield_duration_s
            self._yield_cooldown_until_s = self._yield_until_s + cfg.cursor_yield_cooldown_s
        if now > self._yield_until_s:
            return (0.0, 0.0)
        # Tangential drift away from the cursor.
        nx, ny = dx / dist, dy / dist
        # Rotate 90° for tangential preference, then bias outward.
        tx, ty = -ny, nx
        vx = (tx * 0.35 + nx) * cfg.cursor_yield_max_speed_points_s
        vy = (ty * 0.35 + ny) * cfg.cursor_yield_max_speed_points_s
        speed = math.hypot(vx, vy)
        if speed > cfg.cursor_yield_max_speed_points_s:
            scale = cfg.cursor_yield_max_speed_points_s / speed
            vx *= scale
            vy *= scale
        return (vx, vy)

    def snapshot(self) -> dict[str, Any]:
        return {
            "sim_time_s": self.clock.sim_time_s,
            "mode": self.mode,
            "wing_phase": self.wing_phase(),
            "pose": {
                "x": self.pose.x,
                "y": self.pose.y,
                "headingRad": self.pose.heading_rad,
                "speedPointsS": self.pose.speed_points_s,
                "depth01": self.pose.depth01,
                "locomotion": self.pose.locomotion,
                "displayId": self.pose.display_id,
                "hostSurfaceId": self.pose.host_surface_id,
                "visible": self.pose.visible,
                "transitionSource": self.pose.transition_source,
            },
            "controller": "authored-animation",
            "neural_worker": "stopped",
        }
