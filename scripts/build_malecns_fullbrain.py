#!/usr/bin/env python3
"""Build the whole-MaleCNS live tables: every neuron with an agreed sign.

Neurons: all 211,577 MaleCNS bodies. A neuron is included when its
``consensus_nt`` labels agree on one sign (flysim.nt_signs); anything
unclear, conflicting, or modulatory is excluded, and so are its synapses.
Edges are written as integer arrays (``.npz``) because 23 million string rows
cannot be loaded in time at start-up.

Retina: lamina monopolar cells L1, L2, L3 with an assigned hex position
receive ``hex_{side}_{h1}_{h2}``. hex1 is read as bearing within that eye and
hex2 as distance; that axis orientation is a model assumption. Photoreceptors
are not driven directly: the photoreceptor-to-lamina synapse is sign-inverting
(histamine onto chloride channels), so the lamina feature is light decrement.

Motor readout: leg-nerve motor neurons (ProLN, MesoLN, MetaLN) set forward and
same-side turn; wing-nerve motor neurons (ADMN, PDMNa, PDMNp) and DNp01 set the
takeoff number only. Not an anatomical muscle map.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from flysim.nt_signs import SIGN_RULE, agreed_sign_map  # noqa: E402

DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw"
FULL_META = DERIVED / "malecns-full-meta.json"
FULL_NEURONS = DERIVED / "malecns-full-neurons.parquet"
FULL_EDGES = DERIVED / "malecns-full-edges.parquet"
ANNOTATIONS = RAW / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTERS = RAW / "body-neurotransmitters-male-cns-v1.0.feather"

LAMINA_TYPES = frozenset({"L1", "L2", "L3"})
LEG_NERVES = frozenset({"ProLN", "MesoLN", "MetaLN"})
WING_NERVES = frozenset({"ADMN", "PDMNa", "PDMNp"})
LAMINA_GAIN = 2.0
LEG_FORWARD_GAIN = 0.6
LEG_TURN_GAIN = 0.15
WING_GAIN = 0.02
TAKEOFF_GAIN = 0.025
EVIDENCE_LAMINA = (
    "lamina monopolar cell (L1/L2/L3) at assignedOlHex; feature is light decrement "
    "because the photoreceptor synapse is sign-inverting (histamine-gated chloride); "
    "hex1 as bearing and hex2 as distance is a model assumption"
)
EVIDENCE_LEG = (
    "leg-nerve motor neuron (ProLN, MesoLN, or MetaLN); somaSide is the same "
    "screen side; not an anatomical muscle map"
)
EVIDENCE_WING = (
    "wing-nerve motor neuron (ADMN, PDMNa, or PDMNp) contributes to the takeoff "
    "number only; not a speed command"
)
EVIDENCE_GF = "DNp01 giant fiber takeoff command (von Reyn 2017; Ache 2019)"


def _int_ids(column: pa.ChunkedArray) -> np.ndarray:
    return pc.cast(pc.utf8_slice_codeunits(column, 9), pa.int64()).to_numpy()


def build() -> Path:
    ann = feather.read_table(
        ANNOTATIONS,
        columns=["bodyId", "type", "superclass", "somaSide", "assignedOlHex1", "assignedOlHex2", "exitNerve"],
    ).to_pydict()
    annotations: dict[int, dict] = {}
    for body, cell_type, superclass, side, h1, h2, nerve in zip(
        ann["bodyId"], ann["type"], ann["superclass"], ann["somaSide"],
        ann["assignedOlHex1"], ann["assignedOlHex2"], ann["exitNerve"], strict=True,
    ):
        annotations[int(body)] = {
            "type": cell_type,
            "superclass": superclass,
            "side": side,
            "h1": None if h1 is None else int(h1),
            "h2": None if h2 is None else int(h2),
            "nerve": nerve,
        }

    nt = feather.read_table(NEUROTRANSMITTERS, columns=["body", "consensus_nt"])
    nt_bodies = [int(b) for b in nt.column("body").to_numpy().tolist()]
    nt_labels = [str(x) for x in nt.column("consensus_nt").to_pylist()]
    signs = agreed_sign_map(nt_bodies, nt_labels)
    modulatory = {
        b for b, lab in zip(nt_bodies, nt_labels, strict=True)
        if any(tok in lab.lower() for tok in ("dopamine", "serotonin", "octopamine", "histamine"))
    }

    neurons = pq.read_table(FULL_NEURONS)
    all_ids = _int_ids(neurons.column("neuron_id"))
    review_rows = []
    included = 0
    for body in all_ids.tolist():
        sign = signs.get(body)
        if sign is None:
            review_rows.append(
                {
                    "neuron_id": f"male-cns:{body}",
                    "decision": "exclude",
                    "modulatory_status": "yes" if body in modulatory else "no",
                    "fixed_sign": 0,
                    "role": "none",
                    "evidence": "fullbrain review: no agreed neurotransmitter sign (fail closed)",
                }
            )
            continue
        included += 1
        info = annotations.get(body, {})
        if info.get("type") in LAMINA_TYPES and info.get("h1") is not None and info.get("side") in ("L", "R"):
            role = "sensory"
        elif info.get("superclass") == "vnc_motor" or info.get("type") == "DNp01":
            role = "readout"
        else:
            role = "interneuron"
        review_rows.append(
            {
                "neuron_id": f"male-cns:{body}",
                "decision": "include",
                "modulatory_status": "no",
                "fixed_sign": int(sign),
                "role": role,
                "evidence": f"fullbrain review: {SIGN_RULE}",
            }
        )

    edges = pq.read_table(FULL_EDGES)
    pre = _int_ids(edges.column("pre_id"))
    post = _int_ids(edges.column("post_id"))
    count = edges.column("synapse_count").to_numpy().astype(np.int64)
    out = {
        "neurons": DERIVED / "malecns-fullbrain-neurons.parquet",
        "edges": DERIVED / "malecns-fullbrain-edges.npz",
        "review": DERIVED / "malecns-fullbrain-review.parquet",
        "meta": DERIVED / "malecns-fullbrain-meta.json",
    }
    pq.write_table(neurons, out["neurons"])
    pq.write_table(pa.Table.from_pylist(review_rows), out["review"])
    np.savez(out["edges"], pre_body=pre, post_body=post, synapse_count=count)
    edge_hash = hashlib.sha256()
    for arr in (pre, post, count):
        edge_hash.update(np.ascontiguousarray(arr).tobytes())

    sensory_map = []
    h1_max = h2_max = 1
    lamina_by_type: dict[str, int] = {}
    for body in all_ids.tolist():
        if body not in signs:
            continue
        info = annotations.get(body, {})
        if info.get("type") in LAMINA_TYPES and info.get("h1") is not None and info.get("side") in ("L", "R"):
            h1_max = max(h1_max, info["h1"])
            h2_max = max(h2_max, info["h2"])
            lamina_by_type[info["type"]] = lamina_by_type.get(info["type"], 0) + 1
            sensory_map.append(
                {
                    "feature_name": f"hex_{info['side']}_{info['h1']}_{info['h2']}",
                    "neuron_id": f"male-cns:{body}",
                    "fixed_gain": LAMINA_GAIN,
                    "evidence": EVIDENCE_LAMINA,
                    "mapping_kind": "engineered",
                }
            )
    motor_map = []
    leg_n = wing_n = gf_n = 0
    for body in all_ids.tolist():
        if body not in signs:
            continue
        info = annotations.get(body, {})
        nid = f"male-cns:{body}"
        if info.get("type") == "DNp01":
            gf_n += 1
            motor_map.append({"neuron_id": nid, "output_channel": "takeoff", "fixed_gain": TAKEOFF_GAIN,
                              "evidence": EVIDENCE_GF, "mapping_kind": "anatomical"})
            continue
        if info.get("superclass") != "vnc_motor":
            continue
        nerve = info.get("nerve")
        side = info.get("side")
        if nerve in WING_NERVES:
            wing_n += 1
            motor_map.append({"neuron_id": nid, "output_channel": "takeoff", "fixed_gain": WING_GAIN,
                              "evidence": EVIDENCE_WING, "mapping_kind": "engineered"})
        elif nerve in LEG_NERVES and side in ("L", "R"):
            leg_n += 1
            motor_map.append({"neuron_id": nid, "output_channel": "forward", "fixed_gain": LEG_FORWARD_GAIN,
                              "evidence": EVIDENCE_LEG, "mapping_kind": "engineered"})
            motor_map.append({"neuron_id": nid, "output_channel": "left" if side == "L" else "right",
                              "fixed_gain": LEG_TURN_GAIN, "evidence": EVIDENCE_LEG, "mapping_kind": "engineered"})

    meta = json.loads(FULL_META.read_text(encoding="utf-8"))
    selection = {
        "method": "all MaleCNS neurons with an agreed neurotransmitter sign; lamina retina; VNC motor readout",
        "neuron_count_total": int(len(all_ids)),
        "neuron_count_included": included,
        "lamina_by_type": lamina_by_type,
        "retina_h1_max": h1_max,
        "retina_h2_max": h2_max,
        "leg_motor_readout": leg_n,
        "wing_motor_readout": wing_n,
        "giant_fiber_readout": gf_n,
        "sign_rule": SIGN_RULE,
        "edge_count_raw": int(len(pre)),
        "edge_hash": edge_hash.hexdigest(),
    }
    out["meta"].write_text(
        json.dumps(
            {
                "dataset": meta["dataset"],
                "source_annotation_revision": meta["source_annotation_revision"],
                "fixture_kind": "malecns-reviewed-subset",
                "neuron_count": neurons.num_rows,
                "edge_count": int(len(pre)),
                "sensory_map": sensory_map,
                "motor_map": motor_map,
                "provenance": meta.get("provenance", {}),
                "selection": selection,
                "neurons_path": out["neurons"].name,
                "edges_path": out["edges"].name,
                "review_path": out["review"].name,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"meta": str(out["meta"].relative_to(ROOT)), **selection}, indent=2))
    return out["meta"]


if __name__ == "__main__":
    build()
