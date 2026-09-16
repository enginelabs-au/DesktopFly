"""World pose and locomotion state for the authored-animation path."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Literal

Locomotion = Literal["idle", "crawl", "flight"]
TransitionSource = Literal["authored", "geometry", "operator"]


@dataclass(frozen=True)
class WorldPose:
    x: float
    y: float
    heading_rad: float
    speed_points_s: float
    depth01: float
    locomotion: Locomotion
    display_id: str = "primary"
    host_surface_id: str | None = None
    visible: bool = True
    transition_source: TransitionSource = "authored"

    def __post_init__(self) -> None:
        for name in ("x", "y", "heading_rad", "speed_points_s", "depth01"):
            value = getattr(self, name)
            if not math.isfinite(value):
                raise ValueError(f"non-finite {name}")
        if not 0.0 <= self.depth01 <= 1.0:
            raise ValueError("depth01 must be in [0, 1]")
        if self.speed_points_s < 0:
            raise ValueError("speed must be non-negative")


@dataclass(frozen=True)
class DesktopBounds:
    x: float
    y: float
    width: float
    height: float

    def clamp_point(self, x: float, y: float) -> tuple[float, float]:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("invalid bounds")
        return (
            min(max(x, self.x), self.x + self.width),
            min(max(y, self.y), self.y + self.height),
        )


def scale_for_depth(depth01: float) -> float:
    """Visual scale only; never affects neural dt."""
    if not 0.0 <= depth01 <= 1.0 or not math.isfinite(depth01):
        raise ValueError("invalid depth01")
    return 1.0 - 0.35 * depth01


def ease_smoothstep(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def wrap_heading(heading_rad: float) -> float:
    return (heading_rad + math.pi) % (2.0 * math.pi) - math.pi


def integrate_pose(
    pose: WorldPose,
    *,
    dt_s: float,
    speed_points_s: float,
    turn_rate_rad_s: float,
    bounds: DesktopBounds,
    locomotion: Locomotion | None = None,
    depth01: float | None = None,
    transition_source: TransitionSource = "authored",
) -> WorldPose:
    if dt_s < 0 or not math.isfinite(dt_s):
        raise ValueError("invalid dt")
    speed = max(0.0, float(speed_points_s))
    heading = wrap_heading(pose.heading_rad + turn_rate_rad_s * dt_s)
    x = pose.x + math.cos(heading) * speed * dt_s
    y = pose.y + math.sin(heading) * speed * dt_s
    x, y = bounds.clamp_point(x, y)
    return replace(
        pose,
        x=x,
        y=y,
        heading_rad=heading,
        speed_points_s=speed,
        depth01=pose.depth01 if depth01 is None else depth01,
        locomotion=pose.locomotion if locomotion is None else locomotion,
        transition_source=transition_source,
    )
