"""FlyWire v783 adapter scaffold (separate from MaleCNS; no ID remapping)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FlyWireAdapter:
    """Pinned FlyWire connectivity adapter.

    FlyWire FAFB is a female brain dataset and must not silently remap into
    the MaleCNS atlas. Provide matching annotations before enabling.
    """

    dataset: str = "flywire:v783"
    raw_dir: Path | None = None

    def require_files(self) -> list[Path]:
        root = self.raw_dir or Path(__file__).resolve().parents[3] / "data" / "raw"
        expected = [
            root / "flywire-v783-connectivity.parquet",
            root / "flywire-v783-annotations.parquet",
        ]
        missing = [p for p in expected if not p.is_file()]
        if missing:
            raise FileNotFoundError(
                "FlyWire technical blocker: missing "
                + ", ".join(p.name for p in missing)
                + ". Download a pinned v783 release before enabling this adapter."
            )
        return expected

    def to_canonical(self) -> dict[str, Any]:
        paths = self.require_files()
        return {
            "dataset": self.dataset,
            "status": "files_present_not_auto_merged",
            "paths": [str(p) for p in paths],
            "note": "Do not mix FlyWire IDs into MaleCNS tables",
        }
