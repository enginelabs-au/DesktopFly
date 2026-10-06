"""Compiled LIF step for large graphs.

Same mathematics as :class:`flysim.lif.FrozenLIF`, fused into two compiled
passes so a 5 ms slice of a 150k-neuron graph can finish inside the block
budget. Pass one walks the outgoing synapses of neurons that fired, each
thread into its own partial sum. Pass two validates the input, folds the
partial sums, and advances every membrane. Weights are read-only and the full
fingerprint is re-checked between requests, not inside the timed step.
No learning, no runtime weight change, no optimizer.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from flysim.ingest import StaticGraph
from flysim.lif import (
    LIFPolicy,
    LifWorkerHandle,
    NeuralState,
    assert_lif_may_start,
    lif_policy_from_dict,
)

try:  # numba is an optional accelerator; the numpy kernel remains the reference.
    import numba
    from numba import njit, prange

    NUMBA_AVAILABLE = True
except Exception:  # noqa: BLE001
    NUMBA_AVAILABLE = False

    def njit(*_args, **_kwargs):  # type: ignore[no-redef]
        def wrap(fn):
            return fn

        return wrap

    prange = range  # type: ignore[assignment]


ERR_NONE = 0
ERR_NONFINITE = 1
ERR_RANGE = 2
ERR_BLOCKED = 3


@njit(cache=True, nogil=True)
def _compact(spikes, allowed, out):
    k = 0
    for i in range(spikes.shape[0]):
        if spikes[i] != 0.0 and allowed[i]:
            out[k] = i
            k += 1
    return k


@njit(cache=True, nogil=True, parallel=True)
def _propagate(active, spikes, csr_ptr, csr_dst, csr_w, partial):
    # Each thread accumulates into its own row; rows are folded in _update.
    for k in prange(active.shape[0]):
        row = partial[numba.get_thread_id()]
        i = active[k]
        s = spikes[i]
        for e in range(csr_ptr[i], csr_ptr[i + 1]):
            row[csr_dst[e]] += csr_w[e] * s


@njit(cache=True, nogil=True, parallel=True)
def _update(
    v, refractory, rate_ema, external, partial, allowed, external_max,
    alpha, one_minus_alpha, beta, one_minus_beta, inv_dt,
    v_min, v_max, threshold, isi,
    out_v, out_ref, out_spikes, out_rate,
):
    code = 0
    count = 0
    rows = partial.shape[0]
    for i in prange(v.shape[0]):
        ok = allowed[i]
        x = external[i]
        c = 0
        if not np.isfinite(x):
            c = 1
        elif x < 0.0 or x > external_max:
            c = 2
        elif (not ok) and x != 0.0:
            c = 3
        code = max(code, c)
        syn = 0.0
        for t in range(rows):
            syn += partial[t, i]
            partial[t, i] = 0.0
        if not ok:
            x = np.float32(0.0)
        u = alpha * v[i] + one_minus_alpha * x + np.float32(syn)
        if u < v_min:
            u = v_min
        elif u > v_max:
            u = v_max
        r = refractory[i] - 1
        if r < 0:
            r = 0
        fire = ok and r == 0 and u >= threshold
        s = np.float32(1.0) if fire else np.float32(0.0)
        out_spikes[i] = s
        out_v[i] = np.float32(0.0) if fire else u
        out_ref[i] = isi if fire else r
        re = beta * rate_ema[i] + one_minus_beta * (s * inv_dt)
        out_rate[i] = re if ok else np.float32(0.0)
        if fire:
            count += 1
    return code, count


class FusedLIF:
    """Drop-in for FrozenLIF on graphs too large for per-step numpy temporaries."""

    def __init__(self, graph: StaticGraph, policy: LIFPolicy | None = None, threads: int | None = None):
        if not NUMBA_AVAILABLE:
            raise RuntimeError("fused LIF requires numba")
        if threads:
            numba.set_num_threads(int(threads))
        self.threads = int(numba.get_num_threads())
        self.p = policy or LIFPolicy()
        self.n = len(graph.ids)
        self.ids = graph.ids
        self._src = np.asarray(graph.src, dtype=np.int64)
        self._dst = np.asarray(graph.dst, dtype=np.int64)
        self._w = np.asarray(graph.weights, dtype=np.float32)
        self._allowed = np.ascontiguousarray(np.asarray(graph.allowed, dtype=np.bool_))
        self._alpha = math.exp(-self.p.dt / self.p.tau_m)
        self._beta = math.exp(-self.p.dt / self.p.rate_tau)
        self._isi = int(math.ceil(1 / (self.p.max_hz * self.p.dt)))
        order = np.argsort(self._src, kind="stable")
        self._csr_dst = np.ascontiguousarray(self._dst[order].astype(np.int32))
        self._csr_w = np.ascontiguousarray(self._w[order])
        self._csr_ptr = np.concatenate(
            [[0], np.cumsum(np.bincount(self._src, minlength=self.n))]
        ).astype(np.int64)
        for arr in (self._csr_dst, self._csr_w, self._csr_ptr, self._allowed):
            arr.setflags(write=False)
        self._weight_fingerprint = self._csr_w.tobytes()
        self._partial = np.zeros((self.threads, self.n), dtype=np.float64)
        self._active_buf = np.empty(self.n, dtype=np.int64)
        self._f32 = {
            "external_max": np.float32(self.p.external_max),
            "alpha": np.float32(self._alpha),
            "one_minus_alpha": np.float32(1.0 - self._alpha),
            "beta": np.float32(self._beta),
            "one_minus_beta": np.float32(1.0 - self._beta),
            "inv_dt": np.float32(1.0 / self.p.dt),
            "v_min": np.float32(self.p.v_min),
            "v_max": np.float32(self.p.v_max),
            "threshold": np.float32(self.p.threshold),
        }

    def initial_state(self) -> NeuralState:
        z = np.zeros(self.n, dtype=np.float32)
        return NeuralState(
            v=z.copy(),
            refractory=np.zeros(self.n, dtype=np.int32),
            spikes=z.copy(),
            rate_ema=z.copy(),
        )

    def verify_weights(self) -> None:
        """Full fingerprint check. Runs between requests, never inside a timed block."""
        if self._csr_w.tobytes() != self._weight_fingerprint:
            raise RuntimeError("GRAPH_MUTATION")

    def candidate(self, old: NeuralState, external: np.ndarray) -> tuple[NeuralState, dict[str, Any]]:
        external = np.ascontiguousarray(external, dtype=np.float32)
        if external.shape != (self.n,):
            raise ValueError("Invalid input shape")
        for arr in (self._csr_dst, self._csr_w, self._csr_ptr):
            if arr.flags.writeable:
                raise RuntimeError("GRAPH_MUTATION")
        if numba.get_num_threads() != self.threads:
            raise RuntimeError("fused LIF thread count changed at runtime")

        prior = np.ascontiguousarray(old.spikes, dtype=np.float32)
        # Blocked neurons never propagate (same as FrozenLIF's masked spikes).
        k = _compact(prior, self._allowed, self._active_buf)
        if k:
            # Small chunks only here: outgoing fan-out varies by orders of magnitude.
            with numba.parallel_chunksize(8):
                _propagate(
                    self._active_buf[:k], prior, self._csr_ptr, self._csr_dst, self._csr_w, self._partial
                )

        out_v = np.empty(self.n, dtype=np.float32)
        out_ref = np.empty(self.n, dtype=np.int32)
        out_spikes = np.empty(self.n, dtype=np.float32)
        out_rate = np.empty(self.n, dtype=np.float32)
        f = self._f32
        code, count = _update(
            np.ascontiguousarray(old.v, dtype=np.float32),
            np.ascontiguousarray(old.refractory, dtype=np.int32),
            np.ascontiguousarray(old.rate_ema, dtype=np.float32),
            external,
            self._partial,
            self._allowed,
            f["external_max"],
            f["alpha"], f["one_minus_alpha"], f["beta"], f["one_minus_beta"], f["inv_dt"],
            f["v_min"], f["v_max"], f["threshold"], np.int32(self._isi),
            out_v, out_ref, out_spikes, out_rate,
        )
        if code == ERR_NONFINITE:
            raise ValueError("Non-finite input")
        if code == ERR_RANGE:
            raise ValueError("Input out of range")
        if code == ERR_BLOCKED:
            raise ValueError("Blocked neuron received input")
        diag = {"spike_count": int(count), "live_controller": True}
        return NeuralState(v=out_v, refractory=out_ref, spikes=out_spikes, rate_ema=out_rate), diag


def start_fused_lif_worker(
    policy: dict[str, Any] | None = None,
    *,
    graph: StaticGraph | None = None,
    graph_source: str = "synthetic-fixture",
) -> LifWorkerHandle:
    """Start the compiled kernel under the same policy gate as the numpy worker."""
    policy = assert_lif_may_start(policy)
    if graph is None:
        raise RuntimeError("fused LIF technical blocker: no StaticGraph provided")
    lif = FusedLIF(
        graph,
        policy=lif_policy_from_dict(policy),
        threads=int(policy.get("fused_lif_threads", 8)),
    )
    return LifWorkerHandle(
        policy=policy,
        lif=lif,
        state=lif.initial_state(),
        graph_source=graph_source,
        running=True,
    )
