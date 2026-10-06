"""JSON-line desktop neural worker (stdio). Used by Electron main via src/neural/."""

from __future__ import annotations

import gc
import json
import sys
import time
from typing import Any

from flysim.config import load_policy_dict
from flysim.deadline import BlockDeadlineExceeded, LateBlockGuard
from flysim.presentation import ConnectomePresentationEngine

# Young-generation collection between (never inside) timed blocks, bounded and cheap.
_GC_YOUNG_COLLECT_EVERY_BLOCKS = 200


_MAX_BLOCKS_PER_REQUEST = 20


def _clamp_blocks(value: Any) -> int:
    """Blocks per request: default 1, bounded so one request cannot run long."""
    try:
        n = int(value) if value is not None else 1
    except (TypeError, ValueError):
        return 1
    return max(1, min(_MAX_BLOCKS_PER_REQUEST, n))


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
    guard = LateBlockGuard.from_policy(policy)
    blocks_since_collect = 0
    physics_dt_s = float(policy["physics_dt_s"])
    reset_every_s = float(policy.get("scheduled_state_reset_s", 0.0))
    sim_since_reset_s = 0.0
    scheduled_resets = 0
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
            blocks = _clamp_blocks(msg.get("blocks"))
            motors: list[dict[str, float]] = []
            try:
                # Run the tick's blocks back-to-back (hot) instead of one cold
                # wake per block. Every block is still timed and checked on its own.
                for _ in range(blocks):
                    started = time.perf_counter()
                    cpu_started = time.thread_time()
                    result = engine.step(dt, features)
                    elapsed_s = time.perf_counter() - started
                    cpu_s = time.thread_time() - cpu_started
                    if getattr(engine, "parallel_kernel", False):
                        # Worker threads do most of the compute; the main
                        # thread's CPU time under-measures it. Use wall time
                        # for the strict budget check instead of hiding that.
                        cpu_s = elapsed_s
                    result["technical"]["last_block_compute_s"] = elapsed_s
                    guard.observe(elapsed_s, cpu_s)
                    motors.append(result["motor"])
                result["technical"]["timing"] = guard.status()
                sim_since_reset_s += blocks * physics_dt_s
                if reset_every_s > 0 and sim_since_reset_s >= reset_every_s:
                    # Planned clean start between requests, from the reviewed
                    # initial state. Never runs after a fault (the loop exits).
                    engine.scheduled_reset()
                    sim_since_reset_s = 0.0
                    scheduled_resets += 1
                result["technical"]["scheduled_state_resets"] = scheduled_resets
                result["technical"]["scheduled_state_reset_s"] = reset_every_s
                result["motors"] = motors
            except BlockDeadlineExceeded as exc:
                engine.worker.stop()
                technical = engine.status()
                technical["timing"] = guard.status()
                _reply(
                    {
                        "ok": False,
                        "error": str(exc),
                        "fault": "deadline_exceeded",
                        "faulted": True,
                        "technical": technical,
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
            blocks_since_collect += blocks
            if blocks_since_collect >= _GC_YOUNG_COLLECT_EVERY_BLOCKS:
                blocks_since_collect = 0
                gc.collect(0)
            continue
        _reply({"ok": False, "error": f"unknown op {op!r}"})


if __name__ == "__main__":
    main()
