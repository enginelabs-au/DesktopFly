"""The compiled LIF step matches the numpy reference step for step."""

from __future__ import annotations

import numpy as np
import pytest

from flysim.config import load_policy_dict
from flysim.ingest import build_static_graph
from flysim.lif import FrozenLIF, lif_policy_from_dict

numba = pytest.importorskip("numba")

from flysim.lif_fused import FusedLIF  # noqa: E402


def _graph(n=400, e=6000, seed=5, blocked_every=0):
    rng = np.random.default_rng(seed)
    src = rng.integers(0, n, e)
    dst = rng.integers(0, n, e)
    keep = src != dst
    pairs = sorted(set(zip(src[keep].tolist(), dst[keep].tolist())))
    counts = rng.integers(1, 30, len(pairs)).tolist()
    signs = rng.choice([-1.0, 1.0], n).tolist()
    blocked = np.zeros(n, dtype=np.bool_)
    if blocked_every:
        blocked[::blocked_every] = True
    return build_static_graph(
        [f"male-cns:{i}" for i in range(n)],
        [p[0] for p in pairs],
        [p[1] for p in pairs],
        counts,
        signs,
        blocked,
    )


def _same(a, b):
    assert np.array_equal(a.spikes, b.spikes)
    assert np.array_equal(a.refractory, b.refractory)
    assert np.allclose(a.v, b.v, rtol=1e-5, atol=1e-6)
    assert np.allclose(a.rate_ema, b.rate_ema, rtol=1e-5, atol=1e-4)


@pytest.mark.parametrize("blocked_every", [0, 7])
def test_fused_step_tracks_the_numpy_reference_over_many_steps(blocked_every):
    graph = _graph(blocked_every=blocked_every)
    policy = lif_policy_from_dict(load_policy_dict())
    ref = FrozenLIF(graph, policy)
    fused = FusedLIF(graph, policy)
    rng = np.random.default_rng(2)
    a = ref.initial_state()
    b = fused.initial_state()
    allowed = np.asarray(graph.allowed)
    total = 0
    for step in range(120):
        on = step % 40 < 25
        drive = (rng.random(ref.n) * 0.6 + (1.2 if on else 0.0)).astype(np.float32)
        drive[~allowed] = 0.0
        a, da = ref.candidate(a, drive)
        b, db = fused.candidate(b, drive)
        assert da["spike_count"] == db["spike_count"]
        total += da["spike_count"]
        _same(a, b)
    assert total > 0, "the test exercised firing"


def test_fused_rejects_bad_input_like_the_reference():
    graph = _graph(blocked_every=5)
    policy = lif_policy_from_dict(load_policy_dict())
    fused = FusedLIF(graph, policy)
    state = fused.initial_state()
    bad = np.zeros(fused.n, dtype=np.float32)
    bad[0] = np.nan
    with pytest.raises(ValueError, match="Non-finite"):
        fused.candidate(state, bad)
    bad = np.zeros(fused.n, dtype=np.float32)
    bad[1] = 99.0
    with pytest.raises(ValueError, match="out of range"):
        fused.candidate(state, bad)
    bad = np.zeros(fused.n, dtype=np.float32)
    bad[0] = 0.5  # index 0 is blocked
    with pytest.raises(ValueError, match="Blocked"):
        fused.candidate(state, bad)


def test_fused_graph_arrays_are_read_only_and_fingerprinted():
    fused = FusedLIF(_graph(), lif_policy_from_dict(load_policy_dict()))
    for arr in (fused._csr_dst, fused._csr_w, fused._csr_ptr):
        assert not arr.flags.writeable
    fused.verify_weights()
