#!/usr/bin/env python3
"""Run a bounded full MaleCNS connectome diagnostic."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

from flysim.config import load_policy_dict
from flysim.presentation import ConnectomePresentationEngine

ROOT = Path(__file__).resolve().parents[1]


def run(blocks: int) -> dict:
    policy = load_policy_dict()
    policy.update(
        {
            "graph_mode": "full",
            "require_reviewed_subset": False,
            "max_neurons_initial": 300_000,
            "max_edges_initial": 30_000_000,
            "allow_cpu_fallback": False,
            "device": "mps",
        }
    )

    print("Loading full MaleCNS graph...", flush=True)
    started = time.perf_counter()
    engine = ConnectomePresentationEngine.create(policy)
    load_s = time.perf_counter() - started
    print(
        json.dumps(
            {
                "mode": "full-connectome-diagnostic",
                "host": platform.platform(),
                "load_seconds": load_s,
                "technical": engine.status(),
                "warning": (
                    "This is a bounded diagnostic, not a real-time health claim. "
                    "The desktop safety deadline remains 4 ms per block."
                ),
            },
            indent=2,
        ),
        flush=True,
    )

    samples: list[float] = []
    try:
        for index in range(blocks):
            started = time.perf_counter()
            result = engine.step(
                float(policy["physics_dt_s"]),
                {"ambient_drive": 1.4, "turn_bias": 0.0},
            )
            elapsed_s = time.perf_counter() - started
            samples.append(elapsed_s)
            print(
                json.dumps(
                    {
                        "block": index + 1,
                        "compute_seconds": elapsed_s,
                        "within_4ms_budget": elapsed_s
                        <= float(policy["max_block_compute_s"]),
                        "spike_count": result["technical"].get("spike_count", 0),
                        "motor": result["motor"],
                    }
                ),
                flush=True,
            )
    finally:
        engine.worker.stop()

    return {
        "blocks": blocks,
        "min_seconds": min(samples),
        "max_seconds": max(samples),
        "within_4ms_budget": max(samples) <= float(policy["max_block_compute_s"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a bounded full MaleCNS diagnostic without changing policy.json."
    )
    parser.add_argument(
        "--blocks",
        type=int,
        default=5,
        help="number of 5 ms simulation blocks to run (1-120)",
    )
    args = parser.parse_args()
    if not 1 <= args.blocks <= 120:
        raise SystemExit("--blocks must be between 1 and 120")

    summary = run(args.blocks)
    print(json.dumps({"summary": summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
