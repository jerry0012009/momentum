"""Tests for taxonomy review workbook generation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_crypto_industry_taxonomy_review_workbook import (  # noqa: E402
    build_review_workbook,
    write_review_workbook,
)


def _packet(batch_id: int, ranks: list[int], symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame({
        "review_batch_id": [batch_id] * len(symbols),
        "review_priority_rank": ranks,
        "symbol": symbols,
        "quality_flag": ["REVIEW"] * len(symbols),
        "bar_count": [10] * len(symbols),
        "bar_count_share": [0.1] * len(symbols),
        "quote_volume_sum": [100.0] * len(symbols),
        "quote_volume_share": [0.1] * len(symbols),
        "target_sector": [""] * len(symbols),
        "target_industry": [""] * len(symbols),
        "target_subindustry": [""] * len(symbols),
        "target_quality_flag": ["REVIEW"] * len(symbols),
        "target_known_at": [""] * len(symbols),
        "target_effective_from": [""] * len(symbols),
    })


def test_build_review_workbook_merges_only_batch_packets_in_order(tmp_path: Path):
    diag = tmp_path / "diag"
    diag.mkdir()
    _packet(2, [3], ["CCCUSDT"]).to_csv(diag / "industry_taxonomy_review_batch_002.csv", index=False)
    _packet(1, [2, 1], ["BBBUSDT", "AAAUSDT"]).to_csv(diag / "industry_taxonomy_review_batch_001.csv", index=False)
    pd.DataFrame({"check": ["not_packet"]}).to_csv(
        diag / "industry_taxonomy_review_batch_001_validation_checks.csv",
        index=False,
    )

    workbook, status = build_review_workbook(diag)

    assert workbook["symbol"].tolist() == ["AAAUSDT", "BBBUSDT", "CCCUSDT"]
    assert workbook["packet_file_batch_id"].tolist() == [1, 1, 2]
    assert status["packet_file_count"] == 2
    assert status["workbook_rows"] == 3
    assert status["unique_symbols"] == 3
    assert status["overall_pass"] is True


def test_build_review_workbook_flags_duplicate_symbols(tmp_path: Path):
    diag = tmp_path / "diag"
    diag.mkdir()
    _packet(1, [1], ["AAAUSDT"]).to_csv(diag / "industry_taxonomy_review_batch_001.csv", index=False)
    _packet(2, [2], ["AAAUSDT"]).to_csv(diag / "industry_taxonomy_review_batch_002.csv", index=False)

    _workbook, status = build_review_workbook(diag)

    assert status["overall_pass"] is False
    assert status["duplicate_symbols"] == "AAAUSDT"


def test_write_review_workbook_outputs_csv_and_status(tmp_path: Path):
    diag = tmp_path / "diag"
    diag.mkdir()
    _packet(1, [1], ["AAAUSDT"]).to_csv(diag / "industry_taxonomy_review_batch_001.csv", index=False)
    workbook, status = build_review_workbook(diag)

    out_csv, out_json = write_review_workbook(
        workbook,
        status,
        tmp_path / "out" / "workbook.csv",
        tmp_path / "out" / "status.json",
    )

    assert out_csv.exists()
    assert out_json.exists()
    payload = json.loads(out_json.read_text())
    assert payload["output_csv"] == str(out_csv)
    assert payload["workbook_rows"] == 1
