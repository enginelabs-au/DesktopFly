"""Fixed sensory feature encoder (no reward / needs)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np


@dataclass(frozen=True)
class SensoryMap:
    feature_names: tuple[str, ...]
    neuron_ids: tuple[str, ...]
    gains: np.ndarray  # shape (n_features, n_neurons)


def build_sensory_map(
    neuron_ids: list[str] | tuple[str, ...],
    rows: list[Mapping[str, object]],
) -> SensoryMap:
    """Build a fixed gain matrix from canonical sensory_map rows."""
    index = {nid: i for i, nid in enumerate(neuron_ids)}
    features: list[str] = []
    seen: set[str] = set()
    for row in rows:
        name = str(row["feature_name"])
        if name not in seen:
            seen.add(name)
            features.append(name)
        kind = row.get("mapping_kind")
        if kind not in {"anatomical", "engineered"}:
            raise ValueError(f"invalid sensory mapping_kind {kind!r}")
    gains = np.zeros((len(features), len(neuron_ids)), dtype=np.float32)
    feat_index = {name: i for i, name in enumerate(features)}
    for row in rows:
        nid = str(row["neuron_id"])
        if nid not in index:
            continue
        f_i = feat_index[str(row["feature_name"])]
        gain = float(row["fixed_gain"])
        if not np.isfinite(gain):
            raise ValueError("non-finite sensory gain")
        gains[f_i, index[nid]] = gain
    gains.setflags(write=False)
    return SensoryMap(tuple(features), tuple(neuron_ids), gains)


# Owner-approved (2026-10-06): the pet's surroundings are measured as plain
# numbers relative to the fly's heading and fed to the network. The wiring below
# is ENGINEERED, not anatomical: it assigns existing input-pool neurons to the
# four world features in a fixed round-robin by sorted neuron ID. It makes no
# claim that these neurons sense the cursor or edges in a real fly, and it is
# not tuned toward any behaviour.
WORLD_FEATURES: tuple[str, ...] = ("cursor_left", "cursor_right", "edge_left", "edge_right")
WORLD_FIXED_GAIN = 2.0


def world_bridge_rows(base_rows: list[Mapping[str, object]]) -> list[dict[str, object]]:
    """Fixed engineered sensory rows for world features; empty if no input pool."""
    pool = sorted({str(row["neuron_id"]) for row in base_rows})
    return [
        {
            "feature_name": WORLD_FEATURES[i % len(WORLD_FEATURES)],
            "neuron_id": neuron_id,
            "fixed_gain": WORLD_FIXED_GAIN,
            "evidence": "engineered world-input bridge; fixed round-robin over the input pool; not anatomical",
            "mapping_kind": "engineered",
        }
        for i, neuron_id in enumerate(pool)
    ]


class FixedSensoryEncoder:
    """Map a feature vector to external current. Quiet zeros are valid forever."""

    def __init__(self, sensory_map: SensoryMap, external_max: float = 2.0) -> None:
        self.map = sensory_map
        self.external_max = float(external_max)

    def encode(self, features: Mapping[str, float] | np.ndarray) -> np.ndarray:
        if isinstance(features, np.ndarray):
            vec = np.asarray(features, dtype=np.float32)
            if vec.shape != (len(self.map.feature_names),):
                raise ValueError("feature vector shape mismatch")
        else:
            vec = np.zeros(len(self.map.feature_names), dtype=np.float32)
            for i, name in enumerate(self.map.feature_names):
                if name in features:
                    value = float(features[name])
                    if not np.isfinite(value):
                        raise ValueError("non-finite feature")
                    vec[i] = value
        if not np.isfinite(vec).all():
            raise ValueError("non-finite features")
        current = self.map.gains.T @ vec
        return np.clip(current, 0.0, self.external_max).astype(np.float32)
