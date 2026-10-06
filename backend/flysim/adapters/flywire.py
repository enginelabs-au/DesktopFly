"""FlyWire v783 adapter (separate from MaleCNS; no ID remapping)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


@dataclass(frozen=True)
class FlyWireAdapter:
    """Pinned FlyWire connectivity adapter.

    FlyWire FAFB is a female brain dataset and must not silently remap into
    the MaleCNS atlas. The downloader writes canonical parquet tables under
    data/derived while preserving immutable source files under data/raw.
    """

    dataset: str = "flywire:v783"
    raw_dir: Path | None = None
    derived_dir: Path | None = None

    @property
    def _root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    def _paths(self) -> list[Path]:
        if self.raw_dir is not None:
            root = self.raw_dir
            names = (
                "flywire-v783-connectivity.parquet",
                "flywire-v783-annotations.parquet",
            )
        else:
            root = self.derived_dir or self._root / "data" / "derived"
            names = (
                "flywire-v783-connectivity.parquet",
                "flywire-v783-annotations.parquet",
            )
        return [root / name for name in names]

    def require_files(self) -> list[Path]:
        expected = self._paths()
        missing = [p for p in expected if not p.is_file()]
        if missing:
            raise FileNotFoundError(
                "FlyWire technical blocker: missing "
                + ", ".join(p.name for p in missing)
                + ". Run: python scripts/download_flywire.py"
            )
        return expected

    def load_connectivity(self):
        paths = self.require_files()
        table = pq.read_table(paths[0])
        required = {"dataset", "pre_id", "post_id", "synapse_count"}
        missing = required - set(table.column_names)
        if missing:
            raise ValueError(f"FlyWire connectivity missing columns {sorted(missing)}")
        return table

    def load_annotations(self):
        paths = self.require_files()
        table = pq.read_table(paths[1])
        required = {"dataset", "neuron_id"}
        missing = required - set(table.column_names)
        if missing:
            raise ValueError(f"FlyWire annotations missing columns {sorted(missing)}")
        return table

    def to_canonical(self) -> dict[str, Any]:
        paths = self.require_files()
        return {
            "dataset": self.dataset,
            "status": "files_present_separate_namespace",
            "paths": [str(p) for p in paths],
            "note": "Do not mix FlyWire IDs into MaleCNS tables",
        }
