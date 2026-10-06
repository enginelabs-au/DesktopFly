#!/usr/bin/env python3
"""Measure the configured desktop neural block on the local host."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

from flysim.config import load_policy_dict
from flysim.presentation import ConnectomePresentationEngine

ROOT = Path(__file__).resolve().parents[1]


def measure(samples: int) -> dict:
    policy = load_policy_dict()
    started = time.perf_counter()
    engine = ConnectomePresentationEngine.create(policy)
    cold_start_s = time.perf_counter() - started
    elapsed: list[float] = []
    for _ in range(samples):
        block_started = time.perf_counter()
        engine.step(
            float(policy["physics_dt_s"]),
            {"ambient_drive": 1.4, "turn_bias": 0.0},
        )
        elapsed.append(time.perf_counter() - block_started)
    engine.worker.stop()
    budget = float(policy["max_block_compute_s"])
    sorted_elapsed = sorted(elapsed)
    p95 = sorted_elapsed[max(0, int(len(sorted_elapsed) * 0.95) - 1)]
    return {
        "schema_version": 1,
        "measured_at_unix_s": time.time(),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "policy": {
            "dataset": policy["dataset"],
            "graph_mode": policy["graph_mode"],
            "max_neurons_initial": policy["max_neurons_initial"],
            "max_edges_initial": policy["max_edges_initial"],
            "max_block_compute_s": budget,
            "torch_lif_min_neurons": policy["torch_lif_min_neurons"],
        },
        "engine": engine.status(),
        "cold_start_s": cold_start_s,
        "samples": samples,
        "block_compute_s": {
            "min": min(elapsed),
            "median": statistics.median(elapsed),
            "p95": p95,
            "max": max(elapsed),
        },
        "within_budget": max(elapsed) <= budget,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=40)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reports" / "connectome-timing.json",
    )
    args = parser.parse_args()
    if args.samples < 1:
        raise SystemExit("--samples must be positive")
    report = measure(args.samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["within_budget"]:
        raise SystemExit("configured neural block missed its compute budget")


if __name__ == "__main__":
    main()
