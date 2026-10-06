"""JSON-line desktop neural worker (stdio). Used by Electron main via src/neural/."""

from __future__ import annotations

import json
import sys
from typing import Any

from flysim.config import load_policy_dict
from flysim.presentation import ConnectomePresentationEngine


def _reply(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main() -> None:
    policy = load_policy_dict()
    if policy.get("real_graph_enabled") is not True:
        _reply({"ok": False, "error": "real_graph_enabled is false"})
        return
    try:
        engine = ConnectomePresentationEngine.create(policy)
    except Exception as exc:  # noqa: BLE001 — surface to desktop host
        _reply({"ok": False, "error": str(exc)})
        return
    _reply({"ok": True, "event": "ready", "technical": engine.status()})
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            _reply({"ok": False, "error": "invalid json"})
            continue
        op = msg.get("op")
        if op == "shutdown":
            engine.worker.stop()
            _reply({"ok": True, "event": "stopped"})
            break
        if op == "status":
            _reply({"ok": True, "technical": engine.status()})
            continue
        if op == "step":
            dt = float(msg.get("dt_s", 0.005))
            features = msg.get("features") if isinstance(msg.get("features"), dict) else {}
            try:
                result = engine.step(dt, features)
            except Exception as exc:  # noqa: BLE001
                _reply({"ok": False, "error": str(exc)})
                continue
            _reply({"ok": True, **result})
            continue
        _reply({"ok": False, "error": f"unknown op {op!r}"})


if __name__ == "__main__":
    main()
