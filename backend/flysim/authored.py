from __future__ import annotations

from dataclasses import dataclass

from flysim.clock import PresentationClock
from flysim.world import DesktopWorld, WorldPose


@dataclass
class AuthoredMotionConfig:
    crawl_speed_points_s: float = 40.0
    flight_speed_points_s: float = 120.0
    idle_hold_s: float = 0.5
    crawl_hold_s: float = 1.0
    flight_hold_s: float = 0.8


class AuthoredAnimationController:
    """Explicitly authored pet motion. Not a connectome controller."""

    def __init__(
        self,
        world: DesktopWorld | None = None,
        clock: PresentationClock | None = None,
        config: AuthoredMotionConfig | None = None,
    ) -> None:
        self.world = world or DesktopWorld()
        self.clock = clock or PresentationClock()
        self.config = config or AuthoredMotionConfig()
        self._phase_started_s = 0.0
        self.claim = "authored_animation"
        self.neural_worker_running = False

    def step(self, now_s: float | None = None) -> WorldPose:
        advanced = self.clock.tick(now_s)
        if advanced <= 0 and self.clock.stopped:
            return self.world.pose
        sim = self.clock.sim_time_s
        elapsed = sim - self._phase_started_s
        locomotion = self.world.pose.locomotion
        if locomotion == "idle" and elapsed >= self.config.idle_hold_s:
            self.world.attach_surface("synthetic:window-edge")
            self.world.set_locomotion("crawl", source="authored_policy", sim_time_s=sim)
            self._phase_started_s = sim
        elif locomotion == "crawl" and elapsed >= self.config.crawl_hold_s:
            self.world.set_locomotion("flight", source="authored_policy", sim_time_s=sim)
            self._phase_started_s = sim
        elif locomotion == "flight" and elapsed >= self.config.flight_hold_s:
            self.world.set_locomotion("idle", source="authored_policy", sim_time_s=sim)
            self.world.attach_surface(None)
            self._phase_started_s = sim

        if self.world.pose.locomotion == "crawl":
            self.world.integrate(advanced or self.clock.dt_s, self.config.crawl_speed_points_s, 0.4)
        elif self.world.pose.locomotion == "flight":
            self.world.integrate(advanced or self.clock.dt_s, self.config.flight_speed_points_s, -0.2)
        else:
            self.world.integrate(advanced or self.clock.dt_s, 0.0, 0.0)
        return self.world.pose

    def find_fly(self, x: float, y: float, host_surface_id: str | None = None) -> WorldPose:
        pose = self.world.find_fly(
            x=x,
            y=y,
            host_surface_id=host_surface_id,
            sim_time_s=self.clock.sim_time_s,
        )
        self._phase_started_s = self.clock.sim_time_s
        return pose

    def status(self) -> dict:
        return {
            "controller": self.claim,
            "neural_worker_running": self.neural_worker_running,
            "sim_time_s": self.clock.sim_time_s,
            "pose": self.world.pose.as_dict(),
            "transitions": [
                {
                    "from": item.from_state,
                    "to": item.to_state,
                    "source": item.source,
                    "sim_time_s": item.sim_time_s,
                }
                for item in self.world.transitions
            ],
        }
