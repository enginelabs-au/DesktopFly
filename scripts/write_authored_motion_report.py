#!/usr/bin/env python3
"""Write reports/authored-motion.json from a short authored controller run."""

from __future__ import annotations

import json
from pathlib import Path

from flysim.authored import AuthoredAnimationController, AuthoredMotionConfig
from flysim.clock import PresentationClock
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

    lif_refused = False
    try:
        start_lif_worker({"real_graph_enabled": False})
    except LifStartRefused:
        lif_refused = True

    report = {
        "schema_version": 1,
        "controller": "authored-animation",
        "real_graph_enabled": False,
        "neural_worker_started": False,
        "lif_start_refused": lif_refused,
        "snapshot": ctrl.snapshot(),
        "notes": (
            "Authored presentation path only. LIF remains inert while Q-012 is open. "
            "Not connectome-driven motion."
        ),
    }
    out = ROOT / "reports" / "authored-motion.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
