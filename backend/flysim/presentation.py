"""Connectome LIF loop → motor command for the desktop pet."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from flysim.deadline import BlockDeadlineExceeded  # noqa: F401  (re-exported)
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
    max_turn_rad_s: float = 3.0,
    turn_gain: float = 8.0,
) -> MotorCommand:
    """Decode rate/spike activity using schema channels left/right/forward.

    ``left``/``right`` also yield a bounded steering readout (``turn``): the
    normalized right-minus-left imbalance scaled by a fixed gain and clipped.
    It reuses the existing fixed gains; no new circuit mapping is introduced.
    """
    index = {nid: i for i, nid in enumerate(neuron_ids)}
    activity = np.asarray(activity, dtype=np.float32)
    if activity.shape != (len(neuron_ids),):
        raise ValueError("activity shape mismatch")
    dx = 0.0
    dy = 0.0
    speed = 0.0
    heading = 0.0
    left_sum = 0.0
    right_sum = 0.0
    takeoff_sum = 0.0
    for row in motor_rows:
        nid = str(row["neuron_id"])
        if nid not in index:
            continue
        gain = float(row["fixed_gain"])
        val = float(activity[index[nid]]) * gain
        channel = str(row["output_channel"])
        if channel == "left":
            dx -= val
            left_sum += val
        elif channel == "right":
            dx += val
            right_sum += val
        elif channel == "forward":
            speed += val
        elif channel == "takeoff":
            takeoff_sum += val
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
    total = left_sum + right_sum
    turn = 0.0
    if total > 1e-6:
        turn = float(
            np.clip(turn_gain * (right_sum - left_sum) / total, -max_turn_rad_s, max_turn_rad_s)
        )
    takeoff = float(np.clip(takeoff_sum, 0.0, 1.0))
    return MotorCommand(
        dx=dx, dy=dy, heading=heading, speed=speed, turn=turn, takeoff=takeoff
    )


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
    max_block_compute_s: float
    resting_drive: float = 0.0
    noise_amplitude: float = 0.0
    _rng: Any = None
    # 1.0 where intrinsic baseline/noise applies (central neurons); 0.0 for the
    # visual detectors and the takeoff command, which respond only to input.
    _intrinsic_mask: Any = None
    _last_block_compute_s: float = 0.0
    _last_spike_count: int = 0

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
        driven_only = {str(r["neuron_id"]) for r in tables.get("sensory_map", [])} | {
            str(r["neuron_id"])
            for r in tables.get("motor_map", [])
            if r.get("output_channel") == "takeoff"
        }
        intrinsic_mask = np.array(
            [0.0 if nid in driven_only else 1.0 for nid in compiled.selected_ids],
            dtype=np.float32,
        )
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
            max_block_compute_s=float(policy["max_block_compute_s"]),
            resting_drive=float(policy.get("resting_drive", 0.0)),
            noise_amplitude=float(policy.get("intrinsic_noise_amplitude", 0.0)),
            _rng=np.random.default_rng(int(policy.get("intrinsic_noise_seed", 0))),
            _intrinsic_mask=intrinsic_mask,
        )

    def scheduled_reset(self) -> None:
        """Return neurons to the reviewed initial state. Weights are not touched."""
        self.worker.reset_to_initial_state()
        self._last_spike_count = 0

    def _rate_ema_numpy(self) -> np.ndarray:
        state = self.worker.state
        if hasattr(state, "as_numpy"):
            state = state.as_numpy()
        self._last_spike_count = int(np.asarray(state.spikes).sum())
        return np.asarray(state.rate_ema, dtype=np.float32)

    def status(self) -> dict[str, Any]:
        n = len(self.neuron_ids)
        e = int(len(self.worker.lif._src))
        backend = "numpy-lif"
        if hasattr(self.worker.lif, "device"):
            operator = getattr(self.worker.lif, "operator", "edge-index")
            backend = f"torch-{self.worker.lif.device.type}-{operator}"
        input_n = int(self.report.get("input_neuron_count", n))
        return {
            "graph_source": self.graph_source,
            "connectome_mode": bool(self.report.get("connectome_mode")),
            "motion_driver": self.report.get("motion_driver", "connectome-lif"),
            "lif_backend": backend,
            "neuron_count": input_n,
            "sim_neuron_count": n,
            "synapse_count": e,
            "dataset": self.report.get("dataset"),
            "fixture_kind": self.report.get("fixture_kind"),
            "committed_tick": int(getattr(self.worker, "committed_tick", 0)),
            "max_block_compute_s": self.max_block_compute_s,
            "resting_drive": self.resting_drive,
            "intrinsic_noise_amplitude": self.noise_amplitude,
            "last_block_compute_s": self._last_block_compute_s,
        }

    def step(
        self,
        dt_s: float,
        features: Mapping[str, float] | None = None,
    ) -> dict[str, Any]:
        if dt_s <= 0 or not math.isfinite(dt_s):
            raise ValueError("invalid dt_s")
        started = time.perf_counter()
        feat = dict(features or {})
        # No scripted drive. Inputs: measured loom features, plus fixed baseline and noise.
        external = self.encoder.encode(feat)
        mask = self._intrinsic_mask
        if self.resting_drive > 0:
            external = np.clip(
                external + self.resting_drive * mask, 0.0, self.external_max
            ).astype(np.float32)
        diag_last: dict[str, Any] = {}
        for _ in range(self.steps_per_block):
            step_input = external
            if self.noise_amplitude > 0:
                noise = (
                    self._rng.random(external.shape, dtype=np.float32)
                    * self.noise_amplitude
                    * mask
                )
                step_input = np.clip(external + noise, 0.0, self.external_max).astype(np.float32)
            self.worker.state, diag_last = self.worker.step(step_input)
        activity = self._rate_ema_numpy()
        motor = decode_schema_motor(
            self.neuron_ids,
            self.motor_rows,
            activity,
            max_speed_points_s=120.0,
        )
        elapsed_s = time.perf_counter() - started
        self._last_block_compute_s = elapsed_s
        st = self.status()
        st["spike_count"] = self._last_spike_count
        return {
            "motor": motor.as_dict(),
            "transition_source": "connectome",
            "technical": st,
        }
