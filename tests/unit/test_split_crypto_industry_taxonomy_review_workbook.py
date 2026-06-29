"""Tests for splitting taxonomy review workbooks into reviewed batch packets."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from split_crypto_industry_taxonomy_review_workbook import (  # noqa: E402
    split_review_workbook,
    split_review_workbook_from_paths,
    write_split_packets,
)


def _workbook() -> pd.DataFrame:
    return pd.DataFrame({
        "review_batch_id": [2, 1, 1],
        "review_priority_rank": [3, 2, 1],
        "symbol": ["CCCUSDT", "BBBUSDT", "AAAUSDT"],
        "target_sector": ["", "Layer1", ""],
        "target_industry": ["", "Layer1.Network", ""],
        "target_subindustry": ["", "Layer1.Network.Native", ""],
        "target_quality_flag": ["REVIEW", "OK", "REVIEW"],
        "target_known_at": ["", "2025-12-31T00:00:00Z", ""],
        "target_effective_from": ["", "2024-06-01T01:00:00Z", ""],
    })


def test_split_review_workbook_groups_and_sorts_batches():
    packets, status = split_review_workbook(_workbook())

    assert sorted(packets) == [1, 2]
    assert packets[1]["symbol"].tolist() == ["AAAUSDT", "BBBUSDT"]
    assert packets[2]["symbol"].tolist() == ["CCCUSDT"]
    assert status["batch_count"] == 2
    assert status["workbook_rows"] == 3
    assert status["unique_symbols"] == 3
    assert status["batch_ids"] == "001|002"
    assert status["missing_batch_ids"] == ""
    assert status["overall_pass"] is True


def test_split_review_workbook_rejects_duplicate_symbols():
    workbook = _workbook()
    workbook.loc[0, "symbol"] = "AAAUSDT"

    try:
        split_review_workbook(workbook)
    except ValueError as exc:
        assert "duplicate symbols" in str(exc)
    else:
        raise AssertionError("expected duplicate symbols to be rejected")


def test_write_split_packets_outputs_batch_csvs_and_status(tmp_path: Path):
    packets, status = split_review_workbook(_workbook())

    output_paths, status_json = write_split_packets(
        packets,
        status,
        tmp_path / "reviewed_packets",
        tmp_path / "status.json",
    )

    assert [path.name for path in output_paths] == [
        "industry_taxonomy_review_batch_001.csv",
        "industry_taxonomy_review_batch_002.csv",
    ]
    assert output_paths[0].exists()
    assert output_paths[1].exists()
    payload = json.loads(status_json.read_text())
    assert payload["output_dir"] == str(tmp_path / "reviewed_packets")
    assert payload["overall_pass"] is True


def test_split_review_workbook_from_paths(tmp_path: Path):
    workbook_csv = tmp_path / "workbook.csv"
    _workbook().to_csv(workbook_csv, index=False)

    status = split_review_workbook_from_paths(
        workbook_csv,
        tmp_path / "reviewed_packets",
        tmp_path / "status.json",
    )

    assert status["batch_count"] == 2
    assert (tmp_path / "reviewed_packets" / "industry_taxonomy_review_batch_001.csv").exists()
    assert (tmp_path / "reviewed_packets" / "industry_taxonomy_review_batch_002.csv").exists()
