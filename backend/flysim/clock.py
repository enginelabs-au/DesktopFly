"""Monotonic presentation clock. One clock only while neural sim is off."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class PresentationClock:
    """Authoritative presentation clock for authored motion.

    Wall catch-up after stalls is bounded: at most ``max_catch_up_s`` of
    simulated time advances per ``advance`` call. Fake clocks support tests.
    """

    max_catch_up_s: float = 0.05
    _sim_time_s: float = 0.0
    _last_wall_s: float | None = None
    _stopped: bool = False
    _paused: bool = False
    _fake_wall_s: float | None = None

    def now_wall_s(self) -> float:
        if self._fake_wall_s is not None:
            return self._fake_wall_s
        return time.monotonic()

    def set_fake_wall_s(self, wall_s: float) -> None:
        self._fake_wall_s = wall_s

    def advance_fake_wall(self, delta_s: float) -> None:
        if self._fake_wall_s is None:
            self._fake_wall_s = 0.0
        self._fake_wall_s += delta_s

    @property
    def sim_time_s(self) -> float:
        return self._sim_time_s

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True
        self._last_wall_s = None

    def resume(self) -> None:
        if self._stopped:
            raise RuntimeError("cannot resume a stopped clock")
        self._paused = False
        self._last_wall_s = self.now_wall_s()

    def stop(self) -> None:
        self._stopped = True
        self._paused = False
        self._last_wall_s = None

    def advance(self) -> float:
        """Advance sim time; return dt applied (0 if paused/stopped)."""
        if self._stopped or self._paused:
            return 0.0
        wall = self.now_wall_s()
        if self._last_wall_s is None:
            self._last_wall_s = wall
            return 0.0
        raw = wall - self._last_wall_s
        self._last_wall_s = wall
        if raw < 0:
            return 0.0
        dt = min(raw, self.max_catch_up_s)
        self._sim_time_s += dt
        return dt
