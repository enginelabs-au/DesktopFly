from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

Locomotion = Literal["idle", "crawl", "flight"]
TransitionSource = Literal["geometry_rule", "operator_command", "authored_policy"]

VALID_LOCOMOTION = frozenset({"idle", "crawl", "flight"})
MAX_SPEED_POINTS_S = 160.0
CURSOR_YIELD_RADIUS = 40.0
CURSOR_YIELD_SPEED = 40.0
CURSOR_YIELD_DURATION_S = 0.25
CURSOR_YIELD_COOLDOWN_S = 0.75


@dataclass
class WorldPose:
    x: float
    y: float
    heading_rad: float
    speed_points_s: float
    display_id: str
    host_surface_id: str | None
    depth01: float
    locomotion: Locomotion
    visible: bool = True

    def as_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "headingRad": self.heading_rad,
            "speedPointsS": self.speed_points_s,
            "displayId": self.display_id,
            "hostSurfaceId": self.host_surface_id,
            "depth01": self.depth01,
            "locomotion": self.locomotion,
            "visible": self.visible,
        }


@dataclass
class TransitionRecord:
    from_state: Locomotion
    to_state: Locomotion
    source: TransitionSource
    sim_time_s: float


class DesktopWorld:
    """Geometry/presentation world. No reward, needs, or neural authority."""

    def __init__(
        self,
        *,
        display_id: str = "primary",
        x: float = 200.0,
        y: float = 200.0,
        heading_rad: float = 0.0,
    ) -> None:
        self.pose = WorldPose(
            x=x,
            y=y,
            heading_rad=heading_rad,
            speed_points_s=0.0,
            display_id=display_id,
            host_surface_id=None,
            depth01=0.0,
            locomotion="idle",
            visible=True,
        )
        self.transitions: list[TransitionRecord] = []
        self._yield_until_s = -1.0
        self._yield_cooldown_until_s = -1.0

    def set_locomotion(
        self,
        next_state: Locomotion,
        *,
        source: TransitionSource,
        sim_time_s: float,
    ) -> None:
        if next_state not in VALID_LOCOMOTION:
            raise ValueError(f"Invalid locomotion state {next_state!r}")
        if next_state == self.pose.locomotion:
            return
        self.transitions.append(
            TransitionRecord(self.pose.locomotion, next_state, source, sim_time_s)
        )
        self.pose.locomotion = next_state
        if next_state == "idle":
            self.pose.speed_points_s = 0.0
            self.pose.depth01 = 0.0
        elif next_state == "crawl":
            self.pose.depth01 = 0.0
        elif next_state == "flight":
            self.pose.depth01 = min(1.0, max(self.pose.depth01, 0.35))

    def attach_surface(self, surface_id: str | None) -> None:
        self.pose.host_surface_id = surface_id

    def integrate(self, dt_s: float, commanded_speed: float, turn_rate: float) -> None:
        if dt_s < 0:
            raise ValueError("dt_s must be non-negative")
        speed = max(0.0, min(float(commanded_speed), MAX_SPEED_POINTS_S))
        self.pose.speed_points_s = speed
        self.pose.heading_rad += float(turn_rate) * dt_s
        self.pose.x += speed * math.cos(self.pose.heading_rad) * dt_s
        self.pose.y += speed * math.sin(self.pose.heading_rad) * dt_s
        if self.pose.locomotion == "flight":
            # Authored visual depth only; not physical distance in another app.
            self.pose.depth01 = min(1.0, self.pose.depth01 + 0.5 * dt_s)
        scale = 1.0 - 0.35 * self.pose.depth01
        if scale <= 0:
            raise ValueError("Invalid depth scale")

    def apply_cursor_yield(
        self,
        *,
        cursor_x: float,
        cursor_y: float,
        cursor_moving: bool,
        sim_time_s: float,
    ) -> float:
        """Bounded kinematic courtesy outside any neural path. Returns speed contribution."""
        dx = self.pose.x - cursor_x
        dy = self.pose.y - cursor_y
        dist = (dx * dx + dy * dy) ** 0.5
        if dist > CURSOR_YIELD_RADIUS or not cursor_moving:
            return 0.0
        if sim_time_s < self._yield_cooldown_until_s:
            return 0.0
        if self._yield_until_s < 0:
            self._yield_until_s = sim_time_s + CURSOR_YIELD_DURATION_S
        if sim_time_s > self._yield_until_s:
            self._yield_until_s = -1.0
            self._yield_cooldown_until_s = sim_time_s + CURSOR_YIELD_COOLDOWN_S
            return 0.0
        # Tangential nudge; never moves the real cursor.
        return CURSOR_YIELD_SPEED

    def find_fly(
        self,
        *,
        x: float,
        y: float,
        host_surface_id: str | None,
        sim_time_s: float,
    ) -> WorldPose:
        """Reveal without starting a neural worker or clearing faults."""
        self.pose.visible = True
        self.pose.x = float(x)
        self.pose.y = float(y)
        self.pose.host_surface_id = host_surface_id
        self.pose.depth01 = 0.0
        self.set_locomotion("idle", source="operator_command", sim_time_s=sim_time_s)
        self.pose.speed_points_s = 0.0
        return self.pose

    def hide(self, *, sim_time_s: float) -> None:
        self.pose.visible = False
        self.set_locomotion("flight", source="operator_command", sim_time_s=sim_time_s)
