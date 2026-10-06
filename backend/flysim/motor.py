"""Fixed motor decoder (no reward / success debt)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

OUTPUT_CHANNELS = ("dx", "dy", "heading", "speed")


@dataclass(frozen=True)
class MotorMap:
    neuron_ids: tuple[str, ...]
    channels: tuple[str, ...]
    gains: np.ndarray  # shape (n_channels, n_neurons)


def build_motor_map(
    neuron_ids: list[str] | tuple[str, ...],
    rows: list[Mapping[str, object]],
) -> MotorMap:
    index = {nid: i for i, nid in enumerate(neuron_ids)}
    channels = list(OUTPUT_CHANNELS)
    gains = np.zeros((len(channels), len(neuron_ids)), dtype=np.float32)
    chan_index = {name: i for i, name in enumerate(channels)}
    for row in rows:
        kind = row.get("mapping_kind")
        if kind not in {"anatomical", "engineered"}:
            raise ValueError(f"invalid motor mapping_kind {kind!r}")
        channel = str(row["output_channel"])
        if channel not in chan_index:
            raise ValueError(f"invalid output_channel {channel!r}")
        nid = str(row["neuron_id"])
        if nid not in index:
            continue
        gain = float(row["fixed_gain"])
        if not np.isfinite(gain):
            raise ValueError("non-finite motor gain")
        gains[chan_index[channel], index[nid]] = gain
    gains.setflags(write=False)
    return MotorMap(tuple(neuron_ids), tuple(channels), gains)


@dataclass(frozen=True)
class MotorCommand:
    dx: float
    dy: float
    heading: float
    speed: float

    def as_dict(self) -> dict[str, float]:
        return {
            "dx": self.dx,
            "dy": self.dy,
            "heading": self.heading,
            "speed": self.speed,
        }


class FixedMotorDecoder:
    """Decode spike/rate vector to a 2D motion command."""

    def __init__(self, motor_map: MotorMap, max_speed_points_s: float = 30.0) -> None:
        self.map = motor_map
        self.max_speed = float(max_speed_points_s)

    def decode(self, activity: np.ndarray) -> MotorCommand:
        activity = np.asarray(activity, dtype=np.float32)
        if activity.shape != (len(self.map.neuron_ids),):
            raise ValueError("activity shape mismatch")
        if not np.isfinite(activity).all():
            raise ValueError("non-finite activity")
        raw = self.map.gains @ activity
        dx, dy, heading, speed = (float(x) for x in raw)
        speed = float(np.clip(speed, 0.0, self.max_speed))
        return MotorCommand(dx=dx, dy=dy, heading=heading, speed=speed)
