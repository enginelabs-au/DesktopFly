#!/usr/bin/env python3
"""Refresh authored-motion + LIF enablement report."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from flysim.authored import AuthoredAnimationController, AuthoredMotionConfig
from flysim.clock import PresentationClock
from flysim.ingest import build_static_graph
from flysim.lif import LifStartRefused, start_lif_worker
from flysim.world import DesktopBounds

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    clock = PresentationClock(max_catch_up_s=0.05)
    clock.set_fake_wall_s(0.0)
    ctrl = AuthoredAnimationController(
        clock=clock,
        config=AuthoredMotionConfig(),
        bounds=DesktopBounds(0, 0, 1440, 900),
        mode="follow_my_window",
    )
    ctrl.set_host_window((900, 120, 400, 500))
    for _ in range(30):
        clock.advance_fake_wall(0.05)
        ctrl.step()

    graph = build_static_graph(
        ids=["synthetic:a", "synthetic:b", "synthetic:c"],
        src=[0, 1],
        dst=[1, 2],
        counts=[2, 3],
        signs=[1.0, -1.0, 1.0],
        blocked=[False, False, False],
    )
    lif_started = False
    lif_error = None
    try:
        handle = start_lif_worker(
            {"real_graph_enabled": True},
            graph=graph,
            graph_source="synthetic",
        )
        handle.step(np.array([1.5, 0.0, 0.0], dtype=np.float32))
        lif_started = True
    except LifStartRefused as err:
        lif_error = str(err)

    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    report = {
        "schema_version": 1,
        "controller": "authored-animation+lif",
        "real_graph_enabled": policy.get("real_graph_enabled") is True,
        "neural_worker_started": lif_started,
        "lif_start_refused": not lif_started,
        "lif_error": lif_error,
        "snapshot": ctrl.snapshot(),
        "notes": (
            "Cam enabled neural sim. Authored motion remains for presentation/Find fly. "
            "LIF starts on synthetic graph in CI; MaleCNS feather download is still pending."
        ),
    }
    out = ROOT / "reports" / "authored-motion.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
