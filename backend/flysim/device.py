"""Device selection and MPS probe (handover §2.1)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DeviceReport:
    requested: str
    selected: str
    mps_built: bool
    mps_available: bool
    allow_cpu_fallback: bool
    probe_ok: bool
    detail: str


def select_device(requested: str = "mps", allow_cpu_fallback: bool = False):
    import torch

    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") == "1":
        raise RuntimeError("Disable hidden per-operation CPU fallback")
    if requested == "cpu":
        return torch.device("cpu")
    if requested != "mps":
        raise ValueError("Only mps and cpu profiles are supported")
    if torch.backends.mps.is_built() and torch.backends.mps.is_available():
        return torch.device("mps")
    if allow_cpu_fallback:
        return torch.device("cpu")
    raise RuntimeError("MPS unavailable: choose an explicit verified CPU profile")


def probe_edge_operator(device) -> None:
    import torch

    src = torch.tensor([0, 1, 2], dtype=torch.long, device=device)
    dst = torch.tensor([2, 2, 0], dtype=torch.long, device=device)
    weight = torch.tensor([0.25, -0.50, 0.75], device=device)
    spike = torch.tensor([1.0, 1.0, 0.0], device=device)
    output = torch.zeros(3, dtype=torch.float32, device=device)
    output.index_add_(0, dst, weight * spike.index_select(0, src))
    if device.type == "mps":
        torch.mps.synchronize()
    torch.testing.assert_close(
        output.cpu(), torch.tensor([0.0, 0.0, -0.25]), rtol=1e-5, atol=1e-6
    )


def report_device(policy: dict[str, Any]) -> DeviceReport:
    import torch

    requested = str(policy.get("device", "mps"))
    allow = bool(policy.get("allow_cpu_fallback", False))
    mps_built = bool(torch.backends.mps.is_built())
    mps_available = bool(torch.backends.mps.is_available())
    try:
        device = select_device(requested, allow_cpu_fallback=allow)
        probe_edge_operator(device)
        return DeviceReport(
            requested=requested,
            selected=str(device),
            mps_built=mps_built,
            mps_available=mps_available,
            allow_cpu_fallback=allow,
            probe_ok=True,
            detail="edge operator probe passed",
        )
    except Exception as exc:  # noqa: BLE001 — report path
        # Explicit CPU profile when policy allows, else record blocker.
        if allow or requested == "cpu":
            device = torch.device("cpu")
            try:
                probe_edge_operator(device)
                return DeviceReport(
                    requested=requested,
                    selected="cpu",
                    mps_built=mps_built,
                    mps_available=mps_available,
                    allow_cpu_fallback=allow,
                    probe_ok=True,
                    detail=f"mps unavailable ({exc}); using explicit cpu profile",
                )
            except Exception as cpu_exc:  # noqa: BLE001
                return DeviceReport(
                    requested=requested,
                    selected="none",
                    mps_built=mps_built,
                    mps_available=mps_available,
                    allow_cpu_fallback=allow,
                    probe_ok=False,
                    detail=str(cpu_exc),
                )
        return DeviceReport(
            requested=requested,
            selected="none",
            mps_built=mps_built,
            mps_available=mps_available,
            allow_cpu_fallback=allow,
            probe_ok=False,
            detail=str(exc),
        )
