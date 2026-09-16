"""Full-graph loader must not fall back to the 4-neuron dev fixture when raw exists."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from flysim.malecns_full_build import FULL_META
from flysim.runtime_loader import MALECNS_FULL_DEV_FIXTURE, resolve_runtime_tables

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_raw_present_never_uses_dev_fixture(monkeypatch):
    policy = {
        "real_graph_enabled": True,
        "graph_mode": "full",
        "require_reviewed_subset": False,
        "dataset": "male-cns:v1.0",
    }
    fake_tables = {
        "fixture_kind": "malecns-full",
        "dataset": "male-cns:v1.0",
        "source_annotation_revision": "male-cns-v1.0-minconf-0.5",
        "neurons": [{"dataset": "male-cns:v1.0", "neuron_id": "male-cns:1", "cell_type": None, "region": None, "source_annotation_revision": "male-cns-v1.0-minconf-0.5"}],
        "edges": [],
        "review": [],
        "sensory_map": [],
        "motor_map": [],
    }

    with patch("flysim.malecns_full_build.raw_malecns_available", return_value=True):
        with patch(
            "flysim.malecns_full_build.ensure_full_derived_from_raw",
            return_value=FULL_META,
        ):
            with patch(
                "flysim.malecns_full_build.tables_from_full_meta",
                return_value=fake_tables,
            ):
                tables, source = resolve_runtime_tables(policy)
    assert source == "malecns-full"
    assert tables["fixture_kind"] == "malecns-full"
    dev = MALECNS_FULL_DEV_FIXTURE.read_text(encoding="utf-8")
    assert tables["neurons"][0]["neuron_id"] != "male-cns:1730100001" or len(tables["neurons"]) > 4


def test_no_raw_uses_dev_fixture():
    policy = {
        "real_graph_enabled": True,
        "graph_mode": "full",
        "require_reviewed_subset": False,
        "dataset": "male-cns:v1.0",
    }
    with patch("flysim.malecns_full_build.raw_malecns_available", return_value=False):
        if not FULL_META.is_file():
            tables, source = resolve_runtime_tables(policy)
            assert source == "malecns-full"
            assert len(tables["neurons"]) == 4
