from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StaticGraph:
    ids: tuple[str, ...]
    src: np.ndarray
    dst: np.ndarray
    weights: np.ndarray
    allowed: np.ndarray


def build_static_graph(ids, src, dst, counts, signs, blocked, gain=1.1):
    ids = tuple(ids)
    n = len(ids)
    if not n or len(set(ids)) != n or any(type(x) is not str for x in ids):
        raise ValueError("Invalid or duplicate string neuron IDs")
    if not np.isfinite(gain) or not 0 < gain <= 1.1:
        raise ValueError("Invalid incoming weight cap")
    src0, dst0 = np.asarray(src), np.asarray(dst)
    count0 = np.asarray(counts)
    if any(x.dtype.kind not in "iu" for x in (src0, dst0, count0)):
        raise ValueError("Indices and synapse counts must be integers")
    if src0.ndim != 1 or dst0.shape != src0.shape or count0.shape != src0.shape:
        raise ValueError("Invalid edge shapes")
    if np.any(src0 >= n) or np.any(dst0 >= n) or np.any(src0 < 0) or np.any(dst0 < 0):
        raise ValueError("Out-of-range edge index")
    if np.any(count0 <= 0):
        raise ValueError("Synapse counts must be positive")
    signs = np.asarray(signs, dtype=np.float64)
    blocked = np.asarray(blocked)
    if signs.shape != (n,) or blocked.shape != (n,) or blocked.dtype != np.bool_:
        raise ValueError("Invalid node arrays")
    if not np.isin(signs, [-1.0, 1.0]).all():
        raise ValueError("Unresolved fixed sign")
    src = src0.astype(np.int64, copy=True)
    dst = dst0.astype(np.int64, copy=True)
    keep = ~(blocked[src] | blocked[dst])
    src, dst = src[keep], dst[keep]
    count = count0[keep].astype(np.float64)
    if len(src) == 0:
        raise ValueError("No eligible edges; use an explicit synthetic fixture")
    pairs = np.stack([src, dst], axis=1)
    if len(np.unique(pairs, axis=0)) != len(src):
        raise ValueError("Aggregate duplicate source/destination pairs first")
    magnitude = np.log1p(count)
    denominator = np.bincount(dst, weights=magnitude, minlength=n)
    weights = (gain * magnitude / denominator[dst] * signs[src]).astype(np.float32)
    allowed = ~blocked
    incoming = np.bincount(dst, weights=np.abs(weights), minlength=n)
    if not np.isfinite(weights).all() or np.any(incoming > gain + 1e-6):
        raise ValueError("Weight normalization failed")
    for array in (src, dst, weights, allowed):
        array.flags.writeable = False
    return StaticGraph(ids, src, dst, weights, allowed)
