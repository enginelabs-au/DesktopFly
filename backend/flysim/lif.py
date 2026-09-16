"""Inert LIF surface while Q-012 keeps the real graph disabled.

The mathematical kernel may exist for unit checks, but the worker must not start
and must not claim connectome control while ``real_graph_enabled`` is false.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from flysim.ingest import StaticGraph


class LifStartRefused(RuntimeError):
    """Raised when a caller attempts to start LIF while the graph is disabled."""


def load_policy(path: Path | None = None) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    policy_path = path or (root / "config" / "policy.json")
    return json.loads(policy_path.read_text(encoding="utf-8"))


def refuse_lif_start(policy: dict[str, Any] | None = None, *, reason: str = "worker") -> None:
    policy = policy if policy is not None else load_policy()
    if policy.get("real_graph_enabled") is True:
        raise LifStartRefused(
            f"{reason} start is gated until Q-012 is withdrawn and real_graph_enabled is reviewed"
        )
    raise LifStartRefused(
        f"{reason} cannot start while real_graph_enabled is false (Q-012); use authored animation"
    )


def assert_lif_may_not_run(policy: dict[str, Any] | None = None) -> None:
    """Idempotent gate used by supervisors and tests."""
    refuse_lif_start(policy, reason="LIF")


@dataclass(frozen=True)
class LIFPolicy:
    dt: float = 0.001
    tau_m: float = 0.020
    rate_tau: float = 0.050
    max_hz: float = 100.0
    external_max: float = 2.0
    v_min: float = -4.0
    v_max: float = 4.0
    threshold: float = 1.0

    def __post_init__(self) -> None:
        values = tuple(self.__dict__.values())
        if not all(math.isfinite(x) for x in values):
            raise ValueError("Non-finite policy")
        if not (0 < self.dt <= self.tau_m and self.rate_tau > 0):
            raise ValueError("Invalid time constants")
        if not (0 < self.max_hz <= 1 / self.dt and self.external_max > 0):
            raise ValueError("Invalid rate/input cap")
        if not self.v_min < 0 < self.threshold < self.v_max:
            raise ValueError("Invalid voltage bounds")


@dataclass(frozen=True)
class NeuralState:
    v: np.ndarray
    refractory: np.ndarray
    spikes: np.ndarray
    rate_ema: np.ndarray


class FrozenLIF:
    """Numpy reference LIF for offline unit checks only.

    Construction and ``candidate`` are available for tests. Production start
    paths must call ``refuse_lif_start`` first and never publish these states
    as live connectome control while the graph flag is false.
    """

    def __init__(self, graph: StaticGraph, policy: LIFPolicy | None = None):
        self.p = policy or LIFPolicy()
        self.n = len(graph.ids)
        self._src = np.asarray(graph.src, dtype=np.int64).copy()
        self._dst = np.asarray(graph.dst, dtype=np.int64).copy()
        self._w = np.asarray(graph.weights, dtype=np.float32).copy()
        self._allowed = np.asarray(graph.allowed, dtype=np.bool_).copy()
        self._alpha = math.exp(-self.p.dt / self.p.tau_m)
        self._beta = math.exp(-self.p.dt / self.p.rate_tau)
        self._isi = int(math.ceil(1 / (self.p.max_hz * self.p.dt)))
        self._weight_fingerprint = self._w.tobytes()

    def initial_state(self) -> NeuralState:
        z = np.zeros(self.n, dtype=np.float32)
        return NeuralState(
            v=z.copy(),
            refractory=np.zeros(self.n, dtype=np.int32),
            spikes=z.copy(),
            rate_ema=z.copy(),
        )

    def candidate(self, old: NeuralState, external: np.ndarray) -> tuple[NeuralState, dict[str, Any]]:
        external = np.asarray(external, dtype=np.float32)
        if external.shape != (self.n,):
            raise ValueError("Invalid input shape")
        if self._w.tobytes() != self._weight_fingerprint:
            raise RuntimeError("GRAPH_MUTATION")
        if not np.isfinite(external).all():
            raise ValueError("Non-finite input")
        if np.any(external < 0) or np.any(external > self.p.external_max):
            raise ValueError("Input out of range")
        if np.any((~self._allowed) & (external != 0)):
            raise ValueError("Blocked neuron received input")

        safe_input = np.where(self._allowed, external, 0.0).astype(np.float32)
        prior_spikes = np.where(self._allowed, old.spikes, 0.0).astype(np.float32)
        synaptic = np.zeros_like(old.v)
        if len(self._src):
            np.add.at(synaptic, self._dst, self._w * prior_spikes[self._src])
        u = self._alpha * old.v + (1.0 - self._alpha) * safe_input + synaptic
        u = np.clip(u, self.p.v_min, self.p.v_max)
        refractory = np.maximum(old.refractory - 1, 0)
        can_fire = self._allowed & (refractory == 0) & (u >= self.p.threshold)
        spikes = can_fire.astype(np.float32)
        v = np.where(can_fire, 0.0, u).astype(np.float32)
        refractory = np.where(can_fire, self._isi, refractory).astype(np.int32)
        rate_ema = (
            self._beta * old.rate_ema + (1.0 - self._beta) * (spikes / self.p.dt)
        ).astype(np.float32)
        rate_ema = np.where(self._allowed, rate_ema, 0.0)
        diag = {
            "spike_count": int(spikes.sum()),
            "inert_reference": True,
            "not_live_controller": True,
        }
        return NeuralState(v=v, refractory=refractory, spikes=spikes, rate_ema=rate_ema), diag


def start_lif_worker(policy: dict[str, Any] | None = None) -> None:
    """Production entry: always refuse while the graph flag is false."""
    refuse_lif_start(policy, reason="LIF worker")
