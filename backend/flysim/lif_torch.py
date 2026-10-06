"""Torch/MPS LIF kernel for large connectomes (edge-list gather/scatter)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from flysim.device import select_device
from flysim.ingest import StaticGraph
from flysim.lif import (
    LIFPolicy,
    LifStartRefused,
    NeuralState,
    assert_lif_may_start,
    lif_policy_from_dict,
)


@dataclass(frozen=True)
class TorchNeuralState:
    v: Any
    refractory: Any
    spikes: Any
    rate_ema: Any

    def as_numpy(self) -> NeuralState:
        import torch

        return NeuralState(
            v=self.v.detach().cpu().numpy(),
            refractory=self.refractory.detach().cpu().numpy(),
            spikes=self.spikes.detach().cpu().numpy(),
            rate_ema=self.rate_ema.detach().cpu().numpy(),
        )


class TorchLIF:
    """O(E) edge-list LIF on torch device (MPS on Mac when available)."""

    def __init__(
        self,
        graph: StaticGraph,
        policy: LIFPolicy | None = None,
        *,
        device_name: str = "mps",
        allow_cpu_fallback: bool = False,
    ):
        import torch

        self.p = policy or LIFPolicy()
        self.n = len(graph.ids)
        self.ids = graph.ids
        self.device = select_device(device_name, allow_cpu_fallback=allow_cpu_fallback)
        self._src = torch.tensor(graph.src, dtype=torch.long, device=self.device)
        self._dst = torch.tensor(graph.dst, dtype=torch.long, device=self.device)
        self._w = torch.tensor(graph.weights, dtype=torch.float32, device=self.device)
        self._allowed = torch.tensor(graph.allowed, dtype=torch.bool, device=self.device)
        self._allowed_host = np.asarray(graph.allowed, dtype=np.bool_)
        self.operator = "edge-index"
        self._sparse_matrix = None
        if self.device.type == "mps" and len(graph.src) >= 1_000_000:
            try:
                indices = torch.from_numpy(
                    np.vstack((graph.dst, graph.src)).astype(np.int64, copy=False)
                ).to(self.device)
                values = torch.from_numpy(
                    np.array(graph.weights, dtype=np.float32, copy=True)
                ).to(self.device)
                self._sparse_matrix = torch.sparse_coo_tensor(
                    indices,
                    values,
                    (self.n, self.n),
                    device=self.device,
                ).coalesce()
                self.operator = "sparse-matvec"
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    f"MPS sparse connectome operator unavailable: {exc}"
                ) from exc
        self._alpha = math.exp(-self.p.dt / self.p.tau_m)
        self._beta = math.exp(-self.p.dt / self.p.rate_tau)
        self._isi = int(math.ceil(1 / (self.p.max_hz * self.p.dt)))
        self._weight_fingerprint = graph.weights.tobytes()

    def initial_state(self) -> TorchNeuralState:
        import torch

        z = torch.zeros(self.n, dtype=torch.float32, device=self.device)
        return TorchNeuralState(
            v=z.clone(),
            refractory=torch.zeros(self.n, dtype=torch.int32, device=self.device),
            spikes=z.clone(),
            rate_ema=z.clone(),
        )

    def candidate(
        self, old: TorchNeuralState, external: np.ndarray
    ) -> tuple[TorchNeuralState, dict[str, Any]]:
        import torch

        if external.shape != (self.n,):
            raise ValueError("Invalid input shape")
        if not np.isfinite(external).all():
            raise ValueError("Non-finite input")
        if np.any(external < 0) or np.any(external > self.p.external_max):
            raise ValueError("Input out of range")
        if np.any((~self._allowed_host) & (external != 0)):
            raise ValueError("Blocked neuron received input")

        ext = torch.tensor(external, dtype=torch.float32, device=self.device)
        safe_input = torch.where(self._allowed, ext, 0.0)
        prior_spikes = torch.where(self._allowed, old.spikes, 0.0)
        if self._sparse_matrix is not None:
            synaptic = torch.sparse.mm(
                self._sparse_matrix, prior_spikes.unsqueeze(1)
            ).squeeze(1)
        else:
            synaptic = torch.zeros_like(old.v)
        if self._sparse_matrix is None and len(self._src):
            synaptic.index_add_(0, self._dst, self._w * prior_spikes.index_select(0, self._src))
        u = self._alpha * old.v + (1.0 - self._alpha) * safe_input + synaptic
        u = torch.clamp(u, self.p.v_min, self.p.v_max)
        refractory = torch.maximum(old.refractory - 1, torch.zeros_like(old.refractory))
        can_fire = self._allowed & (refractory == 0) & (u >= self.p.threshold)
        spikes = can_fire.to(torch.float32)
        v = torch.where(can_fire, torch.zeros_like(u), u)
        refractory = torch.where(
            can_fire,
            torch.full_like(refractory, self._isi),
            refractory,
        )
        rate_ema = self._beta * old.rate_ema + (1.0 - self._beta) * (spikes / self.p.dt)
        rate_ema = torch.where(self._allowed, rate_ema, 0.0)
        diag = {
            # The presentation layer counts spikes after its single state
            # transfer per physics block. Avoid synchronizing MPS five times
            # for one published block.
            "spike_count": 0,
            "live_controller": True,
            "backend": f"torch-{self.device.type}",
        }
        return TorchNeuralState(v=v, refractory=refractory, spikes=spikes, rate_ema=rate_ema), diag


@dataclass
class TorchLifWorkerHandle:
    policy: dict[str, Any]
    lif: TorchLIF
    state: TorchNeuralState
    graph_source: str
    running: bool = True
    committed_tick: int = 0

    def step(self, external: np.ndarray | None = None) -> tuple[Any, dict[str, Any]]:
        if not self.running:
            raise RuntimeError("LIF worker is stopped")
        if external is None:
            external = np.zeros(self.lif.n, dtype=np.float32)
        self.state, diag = self.lif.candidate(self.state, external)
        self.committed_tick += 1
        return self.state, diag

    def stop(self) -> None:
        self.running = False


def start_torch_lif_worker(
    policy: dict[str, Any] | None = None,
    *,
    graph: StaticGraph,
    graph_source: str = "malecns-full",
) -> TorchLifWorkerHandle:
    policy = assert_lif_may_start(policy)
    device = str(policy.get("device", "mps"))
    allow = bool(policy.get("allow_cpu_fallback", False))
    try:
        lif = TorchLIF(
            graph,
            policy=lif_policy_from_dict(policy),
            device_name=device,
            allow_cpu_fallback=allow,
        )
    except Exception as exc:  # noqa: BLE001
        raise LifStartRefused(f"Torch LIF technical blocker: {exc}") from exc
    return TorchLifWorkerHandle(
        policy=policy,
        lif=lif,
        state=lif.initial_state(),
        graph_source=graph_source,
        running=True,
    )


def prefer_torch_for_graph(n_neurons: int, policy: dict[str, Any]) -> bool:
    threshold = int(policy.get("torch_lif_min_neurons", 256))
    return n_neurons >= threshold
