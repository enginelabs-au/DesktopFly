"""The spike-sparse synaptic sum matches the reference full-edge sum."""

from __future__ import annotations

import numpy as np

from flysim.ingest import build_static_graph
from flysim.lif import FrozenLIF, NeuralState, lif_policy_from_dict
from flysim.config import load_policy_dict


def _graph(n=300, e=4000, seed=3):
    rng = np.random.default_rng(seed)
    src = rng.integers(0, n, e)
    dst = rng.integers(0, n, e)
    keep = src != dst
    pairs = sorted(set(zip(src[keep].tolist(), dst[keep].tolist())))
    counts = rng.integers(1, 20, len(pairs)).tolist()
    signs = rng.choice([-1.0, 1.0], n).tolist()
    return build_static_graph(
        [f"male-cns:{i}" for i in range(n)],
        [p[0] for p in pairs],
        [p[1] for p in pairs],
        counts,
        signs,
        np.zeros(n, dtype=np.bool_),
    )


def test_sparse_sum_matches_full_edge_reference_over_many_spike_patterns():
    graph = _graph()
    lif = FrozenLIF(graph, lif_policy_from_dict(load_policy_dict()))
    rng = np.random.default_rng(1)
    for density in (0.0, 0.01, 0.05, 0.3, 1.0):
        for _ in range(10):
            spikes = (rng.random(lif.n) < density).astype(np.float32)
            reference = np.zeros(lif.n, dtype=np.float32)
            np.add.at(reference, lif._dst, lif._w * spikes[lif._src])
            old = NeuralState(
                v=np.zeros(lif.n, dtype=np.float32),
                refractory=np.zeros(lif.n, dtype=np.int32),
                spikes=spikes,
                rate_ema=np.zeros(lif.n, dtype=np.float32),
            )
            new, _ = lif.candidate(old, np.zeros(lif.n, dtype=np.float32))
            expected_u = np.clip(reference, lif.p.v_min, lif.p.v_max)
            fired = expected_u >= lif.p.threshold
            margin = np.abs(expected_u - lif.p.threshold) > 1e-5  # skip exact ties
            assert np.array_equal(new.spikes.astype(bool)[margin], fired[margin])
            quiet = ~fired & margin
            assert np.allclose(new.v[quiet], expected_u[quiet], rtol=1e-5, atol=1e-6)


def test_graph_arrays_used_for_propagation_are_read_only():
    lif = FrozenLIF(_graph(), lif_policy_from_dict(load_policy_dict()))
    for arr in (lif._csr_dst, lif._csr_w, lif._csr_ptr):
        assert not arr.flags.writeable
