"""JSON-line desktop neural worker (stdio). Used by Electron main via src/neural/."""

from __future__ import annotations

import gc
import json
import sys
import time
from typing import Any

from flysim.config import load_policy_dict
from flysim.presentation import BlockDeadlineExceeded, ConnectomePresentationEngine

# Young-generation collection between (never inside) timed blocks, bounded and cheap.
_GC_YOUNG_COLLECT_EVERY_BLOCKS = 200


def configure_realtime_gc() -> None:
    """Keep the cyclic collector from pausing inside a timed neural block.

    Measured: with the collector enabled a single block spiked to ~82 ms and
    tripped the 4 ms deadline; with it disabled 20k blocks peaked near 1 ms.
    This removes a pause source only; the deadline guard is unchanged.
    """
    gc.collect()
    gc.freeze()
    gc.disable()


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
    configure_realtime_gc()
    blocks_since_collect = 0
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
                started = time.perf_counter()
                result = engine.step(dt, features)
                elapsed_s = time.perf_counter() - started
                budget_s = float(policy["max_block_compute_s"])
                result["technical"]["last_block_compute_s"] = elapsed_s
                if elapsed_s > budget_s:
                    engine.worker.stop()
                    raise BlockDeadlineExceeded(elapsed_s, budget_s)
            except BlockDeadlineExceeded as exc:
                _reply(
                    {
                        "ok": False,
                        "error": str(exc),
                        "fault": "deadline_exceeded",
                        "faulted": True,
                        "technical": engine.status(),
                    }
                )
                break
            except Exception as exc:  # noqa: BLE001
                engine.worker.stop()
                _reply(
                    {
                        "ok": False,
                        "error": str(exc),
                        "fault": "neural_worker_error",
                        "faulted": True,
                        "technical": engine.status(),
                    }
                )
                break
            _reply({"ok": True, **result})
            blocks_since_collect += 1
            if blocks_since_collect >= _GC_YOUNG_COLLECT_EVERY_BLOCKS:
                blocks_since_collect = 0
                gc.collect(0)
            continue
        _reply({"ok": False, "error": f"unknown op {op!r}"})


if __name__ == "__main__":
    main()
