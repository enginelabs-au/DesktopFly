#!/usr/bin/env python3
"""Build the reviewed MaleCNS looming-escape circuit subset.

Owner-approved 2026-10-06. Seeds are the published looming detectors and the
giant fiber: LC4 and LPLC2 (visual projection neurons) and DNp01 (the giant
fiber descending neuron). The subset adds their strongest reviewed partners and
the descending neurons they feed. Everything here is deterministic.

Attribution for the seed circuit: Wu et al. 2016 (LC neurons), Klapoetke et al.
2017 (LPLC2 looming), von Reyn et al. 2017 and Ache et al. 2019 (looming drive
of the giant fiber escape). The left/right assignment comes from the MaleCNS
``somaSide`` annotation. Neurotransmitter signs come from the MaleCNS
``consensus_nt`` label: acetylcholine = +1; GABA and glutamate = -1 (glutamate
inhibition through GluCl is a model assumption); anything unresolved or
modulatory is excluded (fail closed). The left/right/forward readout over the
descending neurons is engineered, not an anatomical claim.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "data" / "derived"
RAW = ROOT / "data" / "raw"
FULL_META = DERIVED / "malecns-full-meta.json"
FULL_NEURONS = DERIVED / "malecns-full-neurons.parquet"
FULL_EDGES = DERIVED / "malecns-full-edges.parquet"
ANNOTATIONS = RAW / "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NEUROTRANSMITTERS = RAW / "body-neurotransmitters-male-cns-v1.0.feather"

SEED_TYPES = ("LC4", "LPLC2", "DNp01")
LOOM_TYPES = ("LC4", "LPLC2")
GIANT_FIBER = "DNp01"
NT_SIGN = {"acetylcholine": 1, "gaba": -1, "glutamate": -1}
MODULATORY_NT = {"dopamine", "serotonin", "octopamine", "histamine"}

LOOM_GAIN = 2.0
EVIDENCE_LOOM = (
    "LC4/LPLC2 looming detector, eye by somaSide "
    "(Wu 2016; Klapoetke 2017; von Reyn 2017; Ache 2019)"
)
EVIDENCE_GF = "DNp01 giant fiber takeoff command (von Reyn 2017; Ache 2019)"
EVIDENCE_DN = (
    "engineered descending-neuron readout by somaSide (contralateral steering convention, "
    "chosen so that looming on one eye turns the body away, cf. Card & Dickinson 2008); "
    "not an anatomical claim"
)


def _int_ids(column: pa.ChunkedArray) -> np.ndarray:
    return pc.cast(pc.utf8_slice_codeunits(column, 9), pa.int64()).to_numpy()


def _load_annotations() -> dict[str, dict]:
    table = feather.read_table(
        ANNOTATIONS, columns=["bodyId", "type", "somaSide", "superclass"]
    ).to_pydict()
    return {
        int(b): {"type": t, "side": s, "superclass": sc}
        for b, t, s, sc in zip(
            table["bodyId"], table["type"], table["somaSide"], table["superclass"], strict=True
        )
    }


def _load_signs() -> dict[int, int]:
    table = feather.read_table(NEUROTRANSMITTERS, columns=["body", "consensus_nt"]).to_pydict()
    signs: dict[int, int] = {}
    for body, nt in zip(table["body"], table["consensus_nt"], strict=True):
        label = str(nt).lower()
        if label in NT_SIGN:
            signs[int(body)] = NT_SIGN[label]
    return signs


def build(max_partners: int, max_descending: int) -> Path:
    annotations = _load_annotations()
    signs = _load_signs()
    full_neurons = pq.read_table(FULL_NEURONS)
    known = {int(str(i)[9:]) for i in full_neurons.column("neuron_id").to_pylist()}

    def resolved(body: int) -> bool:
        return body in known and body in signs

    seeds = sorted(
        b for b, a in annotations.items() if a["type"] in SEED_TYPES and resolved(b)
    )
    seed_set = set(seeds)
    if not seed_set:
        raise SystemExit("no resolved LC4/LPLC2/DNp01 seeds found")

    edges = pq.read_table(FULL_EDGES)
    pre = _int_ids(edges.column("pre_id"))
    post = _int_ids(edges.column("post_id"))
    count = edges.column("synapse_count").to_numpy()
    seed_arr = np.array(seeds, dtype=np.int64)
    pre_in = np.isin(pre, seed_arr)
    post_in = np.isin(post, seed_arr)

    # Partner strength = synapses to or from the seeds; only resolved, non-seed partners.
    score: Counter[int] = Counter()
    for other, weight in zip(
        np.concatenate([post[pre_in & ~post_in], pre[post_in & ~pre_in]]).tolist(),
        np.concatenate([count[pre_in & ~post_in], count[post_in & ~pre_in]]).tolist(),
        strict=True,
    ):
        if resolved(other) and other not in seed_set:
            score[other] += int(weight)
    partners = [b for b, _ in sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))][:max_partners]
    first = seed_set | set(partners)

    # Descending neurons fed by the first layer (the readout population).
    first_arr = np.array(sorted(first), dtype=np.int64)
    feed_mask = np.isin(pre, first_arr)
    dn_score: Counter[int] = Counter()
    for target, weight in zip(post[feed_mask].tolist(), count[feed_mask].tolist(), strict=True):
        if (
            target not in first
            and resolved(target)
            and annotations.get(target, {}).get("superclass") == "descending_neuron"
        ):
            dn_score[target] += int(weight)
    descending = [b for b, _ in sorted(dn_score.items(), key=lambda kv: (-kv[1], kv[0]))][
        :max_descending
    ]
    selected = sorted(first | set(descending))
    selected_arr = np.array(selected, dtype=np.int64)

    keep = np.isin(pre, selected_arr) & np.isin(post, selected_arr)
    sub_edges = pa.table(
        {
            "pre_id": pa.array([f"male-cns:{v}" for v in pre[keep].tolist()]),
            "post_id": pa.array([f"male-cns:{v}" for v in post[keep].tolist()]),
            "synapse_count": pa.array(count[keep].astype(np.int64)),
        }
    )

    ids = [f"male-cns:{b}" for b in selected]
    neurons = full_neurons.filter(pc.is_in(full_neurons.column("neuron_id"), value_set=pa.array(ids)))

    def role(body: int) -> str:
        a = annotations.get(body, {})
        if a.get("type") in LOOM_TYPES:
            return "sensory"
        if a.get("superclass") == "descending_neuron":
            return "readout"
        return "interneuron"

    review_rows = [
        {
            "neuron_id": f"male-cns:{b}",
            "decision": "include",
            "modulatory_status": "no",
            "fixed_sign": signs[b],
            "role": role(b),
            "evidence": "escape-circuit review: sign from consensus_nt; seeds per Ache 2019/von Reyn 2017",
        }
        for b in selected
    ]

    sensory_map = []
    motor_map = []
    side_counts: Counter[str] = Counter()
    for b in selected:
        a = annotations.get(b, {})
        nid = f"male-cns:{b}"
        if a.get("type") in LOOM_TYPES and a.get("side") in ("L", "R"):
            feature = "loom_left" if a["side"] == "L" else "loom_right"
            side_counts[feature] += 1
            sensory_map.append(
                {
                    "feature_name": feature,
                    "neuron_id": nid,
                    "fixed_gain": LOOM_GAIN,
                    "evidence": EVIDENCE_LOOM,
                    "mapping_kind": "anatomical",
                }
            )
    dn_ids = [b for b in selected if annotations.get(b, {}).get("superclass") == "descending_neuron"]
    return _write(
        selected=selected,
        neurons=neurons,
        sub_edges=sub_edges,
        review_rows=review_rows,
        sensory_map=sensory_map,
        dn_ids=dn_ids,
        annotations=annotations,
        selection={
            "method": "LC4/LPLC2/DNp01 seeds, strongest resolved partners, descending targets",
            "seed_count": len(seeds),
            "partner_count": len(partners),
            "descending_count": len(descending),
            "selected_count": len(selected),
            "loom_neurons_by_eye": dict(side_counts),
            "sign_rule": "consensus_nt: acetylcholine +1; gaba -1; glutamate -1 (assumption); else excluded",
            "edge_count": int(keep.sum()),
        },
        gf_ids=[b for b in selected if annotations.get(b, {}).get("type") == GIANT_FIBER],
        motor_map=motor_map,
    )


def _write(
    *, selected, neurons, sub_edges, review_rows, sensory_map, dn_ids, annotations,
    selection, gf_ids, motor_map,
) -> Path:
    meta = json.loads(FULL_META.read_text(encoding="utf-8"))
    out = {
        "neurons": DERIVED / "malecns-escape-neurons.parquet",
        "edges": DERIVED / "malecns-escape-edges.parquet",
        "review": DERIVED / "malecns-escape-review.parquet",
        "meta": DERIVED / "malecns-escape-meta.json",
    }
    pq.write_table(neurons, out["neurons"])
    pq.write_table(sub_edges, out["edges"])
    pq.write_table(pa.Table.from_pylist(review_rows), out["review"])
    motor_map = _motor_rows(gf_ids, dn_ids, annotations)
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


def _motor_rows(gf_ids, dn_ids, annotations) -> list[dict]:
    rows: list[dict] = []
    gf = set(gf_ids)
    for b in gf_ids:
        nid = f"male-cns:{b}"
        rows.append({"neuron_id": nid, "output_channel": "takeoff", "fixed_gain": TAKEOFF_GAIN,
                     "evidence": EVIDENCE_GF, "mapping_kind": "anatomical"})
        rows.append({"neuron_id": nid, "output_channel": "forward", "fixed_gain": FLIGHT_SPEED_GAIN,
                     "evidence": EVIDENCE_GF, "mapping_kind": "anatomical"})
    for b in dn_ids:
        if b in gf:
            continue
        nid = f"male-cns:{b}"
        side = annotations.get(b, {}).get("side")
        rows.append({"neuron_id": nid, "output_channel": "forward", "fixed_gain": FORWARD_GAIN,
                     "evidence": EVIDENCE_DN, "mapping_kind": "engineered"})
        # Contralateral convention: a left-side descending neuron steers the body right.
        steer = {"L": "right", "R": "left"}.get(side) if STEERING == "contralateral" else {
            "L": "left", "R": "right"
        }.get(side)
        if steer:
            rows.append({"neuron_id": nid, "output_channel": steer, "fixed_gain": TURN_GAIN,
                         "evidence": EVIDENCE_DN, "mapping_kind": "engineered"})
    return rows


# Fixed readout scales (transducer units, set once from the measured activity range).
# rate_ema is in Hz. takeoff = sum of giant-fiber rates / 40 Hz, clipped to 0..1.
TAKEOFF_GAIN = 0.025
# Points per second per Hz of giant-fiber rate, so takeoff is also a fast departure.
FLIGHT_SPEED_GAIN = 3.0
FORWARD_GAIN = 0.15
TURN_GAIN = 0.15
STEERING = "contralateral"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-partners", type=int, default=600)
    parser.add_argument("--max-descending", type=int, default=150)
    args = parser.parse_args()
    build(args.max_partners, args.max_descending)


if __name__ == "__main__":
    main()
