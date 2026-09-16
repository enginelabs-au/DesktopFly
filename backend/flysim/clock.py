from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class PresentationClock:
    """Single authoritative presentation clock. No unbounded catch-up after stalls."""

    dt_s: float = 0.005
    _sim_time_s: float = 0.0
    _last_wall_s: float | None = None
    _max_step_s: float = 0.05
    _stopped: bool = False

    @property
    def sim_time_s(self) -> float:
        return self._sim_time_s

    @property
    def stopped(self) -> bool:
        return self._stopped

    def stop(self) -> None:
        self._stopped = True

    def tick(self, now_s: float | None = None) -> float:
        if self._stopped:
            return 0.0
        wall = time.monotonic() if now_s is None else now_s
        if self._last_wall_s is None:
            self._last_wall_s = wall
            self._sim_time_s += self.dt_s
            return self.dt_s
        elapsed = wall - self._last_wall_s
        self._last_wall_s = wall
        if elapsed < 0:
            raise ValueError("Presentation clock moved backwards")
        step = min(elapsed, self._max_step_s)
        # Advance in fixed dt slices; discard excess rather than catch up.
        advanced = 0.0
        while advanced + self.dt_s <= step + 1e-12:
            self._sim_time_s += self.dt_s
            advanced += self.dt_s
        return advanced
