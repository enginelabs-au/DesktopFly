"""Neural worker entry (spawn child).

Owns MPS/neural context only after spawn. Supervisor must not import this
module's torch path at process start — keep heavy init inside ``run_worker``.
CI uses the numpy LIF path via ``start_lif_worker``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from flysim.lif import LifStartRefused, assert_lif_may_start, start_lif_worker


@dataclass
class WorkerHandle:
    """In-process stand-in for the spawned neural worker (Linux CI)."""

    session_id: str
    lif: Any
    running: bool = True
    committed_tick: int = 0

    def heartbeat_payload(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "committed_tick": self.committed_tick,
            "status": "RUNNING" if self.running else "STOPPED",
        }

    def step(self, external_input: Any) -> dict[str, Any]:
        if not self.running:
            raise RuntimeError("worker stopped")
        state, diag = self.lif.step(external_input)
        self.committed_tick += 1
        return {
            "tick": self.committed_tick,
            "diag": diag,
            "spike_count": int(state.spikes.sum()) if hasattr(state, "spikes") else 0,
        }

    def stop(self) -> None:
        self.running = False


def run_worker(
    session_id: str,
    policy: dict[str, Any],
    *,
    graph: Any | None = None,
    graph_source: str = "synthetic",
) -> WorkerHandle:
    """Start neural worker when policy allows; technical blockers raise."""
    assert_lif_may_start(policy)
    if graph is None:
        raise LifStartRefused("worker technical blocker: no StaticGraph provided")
    lif = start_lif_worker(policy, graph=graph, graph_source=graph_source)
    return WorkerHandle(session_id=session_id, lif=lif)


def load_policy(path: Path | None = None) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    return json.loads((path or (root / "config" / "policy.json")).read_text(encoding="utf-8"))
