#!/usr/bin/env python3
"""Build the largest MaleCNS slice that has stayed inside the 4 ms block budget.

The slice is the retinal hex neurons that synapse onto LC4/LPLC2, those looming
detectors, the giant fiber, the descending neurons those detectors contact, and
the motor neurons those descending neurons contact. The full 211,577-neuron
graph does not finish a 5 ms slice in 4 ms on this machine once neurons are
firing; this builder does not include it.

Signs come from flysim.nt_signs. The retinal feature name is hex_{side}_{h1}_{h2}.
Hex axes are a model assumption: hex1 is bearing within that eye, hex2 is distance.
Leg-nerve motor neurons (ProLN, MesoLN, MetaLN) drive forward and same-side turn.
Wing-nerve motor neurons (ADMN, PDMNa, PDMNp) drive the takeoff number only.
Other nerves are not given a channel.
"""

from __future__ import annotations

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

LEG_NERVES = frozenset({"ProLN", "MesoLN", "MetaLN"})
WING_NERVES = frozenset({"ADMN", "PDMNa", "PDMNp"})
HEX_GAIN = 1.5
LEG_FORWARD_GAIN = 0.6
LEG_TURN_GAIN = 0.15
WING_GAIN = 0.02
TAKEOFF_GAIN = 0.025
EVIDENCE_HEX = (
    "optic-lobe neuron with assignedOlHex; hex1 is bearing within the eye and "
    "hex2 is distance (axis orientation is a model assumption, not a published "
    "column-to-angle table in this dataset)"
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
    hex_ids: set[int] = set()
    motor_ids: set[int] = set()
    for body, cell_type, superclass, side, h1, h2, nerve in zip(
        ann["bodyId"],
        ann["type"],
        ann["superclass"],
        ann["somaSide"],
        ann["assignedOlHex1"],
        ann["assignedOlHex2"],
        ann["exitNerve"],
        strict=True,
    ):
        body = int(body)
        annotations[body] = {
            "type": cell_type,
            "superclass": superclass,
            "side": side,
            "h1": None if h1 is None else int(h1),
            "h2": None if h2 is None else int(h2),
            "nerve": nerve,
        }
        if h1 is not None and h2 is not None and side in ("L", "R"):
            hex_ids.add(body)
        if superclass == "vnc_motor":
            motor_ids.add(body)

    nt = feather.read_table(NEUROTRANSMITTERS, columns=["body", "consensus_nt"])
    signs = agreed_sign_map(
        [int(b) for b in nt.column("body").to_numpy().tolist()],
        [str(x) for x in nt.column("consensus_nt").to_pylist()],
    )

    detectors = {b for b, info in annotations.items() if info["type"] in ("LC4", "LPLC2") and b in signs}
    giant = {b for b, info in annotations.items() if info["type"] == "DNp01" and b in signs}
    if not detectors or len(giant) != 2:
        raise SystemExit("resolved LC4/LPLC2 or DNp01 set is incomplete")

    edges = pq.read_table(FULL_EDGES)
    pre = _int_ids(edges.column("pre_id"))
    post = _int_ids(edges.column("post_id"))
    count = edges.column("synapse_count").to_numpy()
    sign_of_pre = np.zeros(len(pre), dtype=np.int8)
    # Vectorized lookup: sorted keys.
    keys = np.fromiter(signs.keys(), dtype=np.int64, count=len(signs))
    vals = np.fromiter(signs.values(), dtype=np.int8, count=len(signs))
    order = np.argsort(keys)
    keys = keys[order]
    vals = vals[order]
    pos = np.searchsorted(keys, pre)
    ok = pos < len(keys)
    ok[ok] = keys[pos[ok]] == pre[ok]
    sign_of_pre[ok] = vals[pos[ok]]
    signed_pre = sign_of_pre != 0

    det_arr = np.array(sorted(detectors), dtype=np.int64)
    hex_arr = np.array(sorted(hex_ids & set(signs)), dtype=np.int64)
    onto_det = signed_pre & np.isin(post, det_arr) & np.isin(pre, hex_arr)
    retina = set(np.unique(pre[onto_det]).tolist())
    # Descending neurons the detectors actually contact, then the motor neurons
    # those descending neurons (and the giant fiber) contact.
    det_pre = signed_pre & np.isin(pre, det_arr)
    dn_ids = {
        int(b)
        for b in np.unique(post[det_pre]).tolist()
        if annotations.get(int(b), {}).get("superclass") == "descending_neuron" and int(b) in signs
    }
    drive = np.array(sorted(dn_ids | giant), dtype=np.int64)
    mn_post = signed_pre & np.isin(pre, drive)
    mn_ids = {
        int(b)
        for b in np.unique(post[mn_post]).tolist()
        if int(b) in motor_ids and int(b) in signs
    }
    selected = sorted(detectors | giant | retina | dn_ids | mn_ids)
    selected_arr = np.array(selected, dtype=np.int64)
    keep = signed_pre & np.isin(pre, selected_arr) & np.isin(post, selected_arr)

    ids = [f"male-cns:{b}" for b in selected]
    neurons = pq.read_table(FULL_NEURONS)
    neurons = neurons.filter(pc.is_in(neurons.column("neuron_id"), value_set=pa.array(ids)))
    sub_edges = pa.table(
        {
            "pre_id": pa.array([f"male-cns:{int(v)}" for v in pre[keep].tolist()]),
            "post_id": pa.array([f"male-cns:{int(v)}" for v in post[keep].tolist()]),
            "synapse_count": pa.array(count[keep].astype(np.int64)),
        }
    )

    def role(body: int) -> str:
        info = annotations.get(body, {})
        if body in retina:
            return "sensory"
        if info.get("superclass") == "vnc_motor" or info.get("type") == "DNp01":
            return "readout"
        return "interneuron"

    review_rows = [
        {
            "neuron_id": f"male-cns:{b}",
            "decision": "include",
            "modulatory_status": "no",
            "fixed_sign": int(signs[b]),
            "role": role(b),
            "evidence": f"live-slice review: {SIGN_RULE}",
        }
        for b in selected
    ]
    sensory_map = []
    h1_max = 1
    h2_max = 1
    for body in sorted(retina):
        info = annotations[body]
        h1_max = max(h1_max, info["h1"])
        h2_max = max(h2_max, info["h2"])
        sensory_map.append(
            {
                "feature_name": f"hex_{info['side']}_{info['h1']}_{info['h2']}",
                "neuron_id": f"male-cns:{body}",
                "fixed_gain": HEX_GAIN,
                "evidence": EVIDENCE_HEX,
                "mapping_kind": "engineered",
            }
        )
    motor_map = []
    leg_n = wing_n = 0
    for body in selected:
        info = annotations.get(body, {})
        nid = f"male-cns:{body}"
        if info.get("type") == "DNp01":
            motor_map.append(
                {
                    "neuron_id": nid,
                    "output_channel": "takeoff",
                    "fixed_gain": TAKEOFF_GAIN,
                    "evidence": EVIDENCE_GF,
                    "mapping_kind": "anatomical",
                }
            )
            continue
        nerve = info.get("nerve")
        side = info.get("side")
        if info.get("superclass") != "vnc_motor":
            continue
        if nerve in WING_NERVES:
            wing_n += 1
            motor_map.append(
                {
                    "neuron_id": nid,
                    "output_channel": "takeoff",
                    "fixed_gain": WING_GAIN,
                    "evidence": EVIDENCE_WING,
                    "mapping_kind": "engineered",
                }
            )
        elif nerve in LEG_NERVES and side in ("L", "R"):
            leg_n += 1
            motor_map.append(
                {
                    "neuron_id": nid,
                    "output_channel": "forward",
                    "fixed_gain": LEG_FORWARD_GAIN,
                    "evidence": EVIDENCE_LEG,
                    "mapping_kind": "engineered",
                }
            )
            motor_map.append(
                {
                    "neuron_id": nid,
                    "output_channel": "left" if side == "L" else "right",
                    "fixed_gain": LEG_TURN_GAIN,
                    "evidence": EVIDENCE_LEG,
                    "mapping_kind": "engineered",
                }
            )

    meta = json.loads(FULL_META.read_text(encoding="utf-8"))
    out = {
        "neurons": DERIVED / "malecns-live-neurons.parquet",
        "edges": DERIVED / "malecns-live-edges.parquet",
        "review": DERIVED / "malecns-live-review.parquet",
        "meta": DERIVED / "malecns-live-meta.json",
    }
    pq.write_table(neurons, out["neurons"])
    pq.write_table(sub_edges, out["edges"])
    pq.write_table(pa.Table.from_pylist(review_rows), out["review"])
    selection = {
        "method": "hex neurons onto LC4/LPLC2, those detectors, their descending targets, and the motor neurons those targets contact",
        "detector_count": len(detectors),
        "descending_count": len(dn_ids),
        "motor_count": len(mn_ids),
        "retina_count": len(retina),
        "selected_count": len(selected),
        "leg_motor_readout": leg_n,
        "wing_motor_readout": wing_n,
        "retina_h1_max": h1_max,
        "retina_h2_max": h2_max,
        "sign_rule": SIGN_RULE,
        "edge_count": int(keep.sum()),
        "full_brain_live": False,
    }
    out["meta"].write_text(
        json.dumps(
            {
                "dataset": meta["dataset"],
                "source_annotation_revision": meta["source_annotation_revision"],
                "fixture_kind": "malecns-reviewed-subset",
                "neuron_count": neurons.num_rows,
                "edge_count": sub_edges.num_rows,
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
