"""Connectome LIF loop → motor command for the desktop pet."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from flysim.lif import LifWorkerHandle, start_lif_worker
from flysim.lif_torch import prefer_torch_for_graph, start_torch_lif_worker
from flysim.motor import MotorCommand
from flysim.runtime_loader import load_compiled_runtime
from flysim.sensory import FixedSensoryEncoder, build_sensory_map


def decode_schema_motor(
    neuron_ids: tuple[str, ...],
    motor_rows: list[dict[str, Any]],
    activity: np.ndarray,
    *,
    max_speed_points_s: float = 120.0,
) -> MotorCommand:
    """Decode rate/spike activity using schema channels left/right/forward."""
    index = {nid: i for i, nid in enumerate(neuron_ids)}
    activity = np.asarray(activity, dtype=np.float32)
    if activity.shape != (len(neuron_ids),):
        raise ValueError("activity shape mismatch")
    dx = 0.0
    dy = 0.0
    speed = 0.0
    heading = 0.0
    for row in motor_rows:
        nid = str(row["neuron_id"])
        if nid not in index:
            continue
        gain = float(row["fixed_gain"])
        val = float(activity[index[nid]]) * gain
        channel = str(row["output_channel"])
        if channel == "left":
            dx -= val
        elif channel == "right":
            dx += val
        elif channel == "forward":
            speed += val
        elif channel == "backward":
            speed -= val
        else:
            raise ValueError(f"unsupported motor channel {channel!r}")
    speed = float(np.clip(speed, 0.0, max_speed_points_s))
    mag = math.hypot(dx, dy)
    if mag > 1e-6 and speed > 0:
        scale = speed / mag
        dx *= scale
        dy *= scale
    elif speed > 0 and mag <= 1e-6:
        heading = 0.0
        dx = speed
        dy = 0.0
    return MotorCommand(dx=dx, dy=dy, heading=heading, speed=speed)


@dataclass
class ConnectomePresentationEngine:
    """Steps numpy LIF on a reviewed graph and exposes motor readouts."""

    worker: LifWorkerHandle
    encoder: FixedSensoryEncoder
    neuron_ids: tuple[str, ...]
    motor_rows: list[dict[str, Any]]
    graph_source: str
    report: dict[str, Any]
    steps_per_block: int
    external_max: float
    _phase: float = 0.0

    @classmethod
    def create(cls, policy: dict[str, Any] | None = None) -> ConnectomePresentationEngine:
        policy = policy or {}
        compiled, tables, graph_source, report = load_compiled_runtime(policy)
        n = len(compiled.selected_ids)
        if prefer_torch_for_graph(n, policy):
            lif = start_torch_lif_worker(
                policy,
                graph=compiled.graph,
                graph_source=graph_source,
            )
        else:
            lif = start_lif_worker(
                policy,
                graph=compiled.graph,
                graph_source=graph_source,
            )
        sensory = build_sensory_map(compiled.selected_ids, tables.get("sensory_map", []))
        encoder = FixedSensoryEncoder(sensory, external_max=float(policy.get("external_input_max", 2.0)))
        steps = int(policy.get("neural_steps_per_block", 5))
        return cls(
            worker=lif,
            encoder=encoder,
            neuron_ids=compiled.selected_ids,
            motor_rows=list(tables.get("motor_map", [])),
            graph_source=graph_source,
            report=report,
            steps_per_block=max(1, steps),
            external_max=float(policy.get("external_input_max", 2.0)),
        )

    def _rate_ema_numpy(self) -> np.ndarray:
        state = self.worker.state
        if hasattr(state, "as_numpy"):
            return state.as_numpy().rate_ema
        return np.asarray(state.rate_ema, dtype=np.float32)

    def status(self) -> dict[str, Any]:
        n = len(self.neuron_ids)
        e = int(len(self.worker.lif._src))
        backend = "numpy-lif"
        if hasattr(self.worker.lif, "device"):
            backend = f"torch-{self.worker.lif.device.type}"
        return {
            "graph_source": self.graph_source,
            "connectome_mode": bool(self.report.get("connectome_mode")),
            "motion_driver": self.report.get("motion_driver", "connectome-lif"),
            "lif_backend": backend,
            "neuron_count": n,
            "synapse_count": e,
            "dataset": self.report.get("dataset"),
            "fixture_kind": self.report.get("fixture_kind"),
            "committed_tick": self.worker.lif.n,  # placeholder; ticks tracked in step
        }

    def step(
        self,
        dt_s: float,
        features: Mapping[str, float] | None = None,
    ) -> dict[str, Any]:
        if dt_s <= 0 or not math.isfinite(dt_s):
            raise ValueError("invalid dt_s")
        self._phase += dt_s
        feat = dict(features or {})
        # Weak autonomous drive so open-space motion is visible without screen capture.
        feat.setdefault("ambient_drive", 1.4 + 0.35 * math.sin(self._phase * 0.7))
        feat.setdefault("turn_bias", 0.45 * math.sin(self._phase * 1.3))
        external = self.encoder.encode(feat)
        diag_last: dict[str, Any] = {}
        for _ in range(self.steps_per_block):
            self.worker.state, diag_last = self.worker.step(external)
        activity = self._rate_ema_numpy()
        motor = decode_schema_motor(
            self.neuron_ids,
            self.motor_rows,
            activity,
            max_speed_points_s=120.0,
        )
        st = self.status()
        st["spike_count"] = int(diag_last.get("spike_count", 0))
        return {
            "motor": motor.as_dict(),
            "transition_source": "connectome",
            "technical": st,
        }
