#!/usr/bin/env python3
"""Write reports/supervisor-health.json for Phase 4 completion evidence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from flysim.recovery import load_recovery_profiles  # noqa: E402
from flysim.supervisor import Supervisor  # noqa: E402


def main() -> int:
    policy = json.loads((ROOT / "config" / "policy.json").read_text(encoding="utf-8"))
    profiles = load_recovery_profiles()
    sup = Supervisor.create("report-session")
    sup.mark_ready()
    # Do not auto-start neural in the report writer; record capability only.
    health = sup.health_view().as_dict()
    report = {
        "phase": 4,
        "real_graph_enabled": policy.get("real_graph_enabled"),
        "auto_restart_after_hard_fault": policy.get("auto_restart_after_hard_fault"),
        "recovery_enabled": (policy.get("recovery") or {}).get("enabled"),
        "known_conditions_only": (policy.get("recovery") or {}).get("known_conditions_only"),
        "profiles_count": len(profiles.get("profiles") or []),
        "profiles_hash": profiles.get("profiles_hash"),
        "lifecycle": sup.lifecycle.value,
        "stop_latched": sup.stop_latched,
        "health_title": health.get("title"),
        "disclaimer": health.get("disclaimer"),
        "modules": [
            "backend/flysim/supervisor.py",
            "backend/flysim/health.py",
            "backend/flysim/recovery.py",
            "backend/flysim/checkpoints.py",
            "backend/flysim/bridge.py",
            "backend/flysim/worker.py",
        ],
        "neural_output_may_invoke_connectors": False,
    }
    out = ROOT / "reports" / "supervisor-health.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
