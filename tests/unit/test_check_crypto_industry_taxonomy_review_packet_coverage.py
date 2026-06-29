"""Tests for taxonomy review packet coverage checks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_crypto_industry_taxonomy_review_packet_coverage import (  # noqa: E402
    check_review_packet_coverage,
    write_packet_coverage_reports,
)


def _source() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "known_at": ["2026-06-28T00:00:00Z"] * 3,
        "effective_from": ["2026-01-01T00:00:00Z"] * 3,
        "effective_to": ["", "", ""],
        "sector": ["", "", ""],
        "industry": ["", "", ""],
        "subindustry": ["", "", ""],
        "taxonomy_version": ["reviewed_v1"] * 3,
        "source": ["manual_review"] * 3,
        "quality_flag": ["REVIEW"] * 3,
    })


def _packet(batch_id: int, symbols: list[str]) -> pd.DataFrame:
    return pd.DataFrame({
        "review_batch_id": [batch_id] * len(symbols),
        "review_priority_rank": list(range(1, len(symbols) + 1)),
        "symbol": symbols,
        "target_sector": [""] * len(symbols),
        "target_industry": [""] * len(symbols),
        "target_subindustry": [""] * len(symbols),
        "target_quality_flag": ["REVIEW"] * len(symbols),
        "target_known_at": [""] * len(symbols),
        "target_effective_from": [""] * len(symbols),
    })


def _write_fixture(tmp_path: Path, packets: dict[int, list[str]]) -> tuple[Path, Path]:
    source_csv = tmp_path / "source.csv"
    diag_dir = tmp_path / "diag"
    diag_dir.mkdir()
    _source().to_csv(source_csv, index=False)
    for batch_id, symbols in packets.items():
        _packet(batch_id, symbols).to_csv(
            diag_dir / f"industry_taxonomy_review_batch_{batch_id:03d}.csv",
            index=False,
        )
    return source_csv, diag_dir


def _status(report: dict[str, object], check: str) -> bool:
    return next(row for row in report["checks"] if row["check"] == check)["passed"]


def test_review_packet_coverage_passes_for_complete_packet_set(tmp_path: Path):
    source_csv, diag_dir = _write_fixture(tmp_path, {1: ["AAAUSDT", "BBBUSDT"], 2: ["CCCUSDT"]})
    pd.DataFrame({"check": ["not_a_packet"], "passed": [True]}).to_csv(
        diag_dir / "industry_taxonomy_review_batch_001_validation_checks.csv",
        index=False,
    )

    report = check_review_packet_coverage(source_csv, diag_dir)

    assert report["overall_pass"] is True
    assert report["blocker"] == ""
    assert report["candidate_file_count"] == 3
    assert report["source_rows"] == 3
    assert report["packet_file_count"] == 2
    assert report["packet_rows"] == 3
    assert report["unique_packet_symbols"] == 3
    assert report["missing_source_symbols"] == ""
    assert report["extra_packet_symbols"] == ""


def test_review_packet_coverage_fails_when_source_symbol_is_missing(tmp_path: Path):
    source_csv, diag_dir = _write_fixture(tmp_path, {1: ["AAAUSDT", "BBBUSDT"]})

    report = check_review_packet_coverage(source_csv, diag_dir)

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_coverage_missing_source_symbols"
    assert report["missing_source_symbols"] == "CCCUSDT"
    assert _status(report, "all_source_symbols_in_packets") is False


def test_review_packet_coverage_fails_on_duplicate_packet_symbols(tmp_path: Path):
    source_csv, diag_dir = _write_fixture(tmp_path, {1: ["AAAUSDT", "BBBUSDT"], 2: ["BBBUSDT", "CCCUSDT"]})

    report = check_review_packet_coverage(source_csv, diag_dir)

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_coverage_duplicate_symbols"
    assert report["duplicate_packet_symbols"] == "BBBUSDT"
    assert _status(report, "packet_symbols_unique_across_batches") is False


def test_review_packet_coverage_reports_are_written(tmp_path: Path):
    source_csv, diag_dir = _write_fixture(tmp_path, {1: ["AAAUSDT", "BBBUSDT"], 2: ["CCCUSDT"]})
    report = check_review_packet_coverage(source_csv, diag_dir)

    out_json, out_csv = write_packet_coverage_reports(report, tmp_path)

    assert out_json.exists()
    assert out_csv.exists()
    assert json.loads(out_json.read_text())["overall_pass"] is True
    assert out_csv.name == "industry_taxonomy_review_packet_coverage_checks.csv"
