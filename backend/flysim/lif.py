from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "policy.json"


def load_policy(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or POLICY_PATH).read_text())


def select_device(requested: str = "mps", allow_cpu_fallback: bool = False) -> str:
    """Return a device label. Does not start a neural worker."""
    if requested == "cpu":
        return "cpu"
    if requested != "mps":
        raise ValueError("Only mps and cpu profiles are supported")
    if allow_cpu_fallback:
        return "cpu"
    # Linux CI and Q-012 path: do not pretend MPS is available here.
    raise RuntimeError("MPS unavailable: choose an explicit verified CPU profile")


def start_lif_worker(policy: dict[str, Any] | None = None) -> None:
    """LIF module exists for later phases but cannot start while Q-012 holds."""
    policy = policy or load_policy()
    if policy.get("real_graph_enabled") is not True:
        raise RuntimeError(
            "LIF worker refuses to start while real_graph_enabled is false (Q-012)"
        )
    raise RuntimeError("LIF worker start is not implemented in this phase")


def lif_module_is_inert(policy: dict[str, Any] | None = None) -> bool:
    policy = policy or load_policy()
    return policy.get("real_graph_enabled") is not True
