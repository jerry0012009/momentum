"""Tests for source-level crypto industry taxonomy review checks."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_crypto_industry_taxonomy_review_source import (  # noqa: E402
    DEFAULT_SOURCE,
    summarize_review_source,
    write_review_source_reports,
)


def _rows() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "known_at": ["2026-06-28T00:00:00Z"] * 3,
        "effective_from": ["2026-01-01T00:00:00Z"] * 3,
        "effective_to": ["", "", ""],
        "sector": ["L1", "L2", ""],
        "industry": ["L1a", "L2a", ""],
        "subindustry": ["L1a1", "L2a1", ""],
        "taxonomy_version": ["reviewed_v1"] * 3,
        "source": ["manual_review"] * 3,
        "quality_flag": ["OK", "OK", "REVIEW"],
    })


def _write(df: pd.DataFrame, path: Path) -> Path:
    df.to_csv(path, index=False)
    return path


def _write_bars(path: Path) -> Path:
    pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-01-02 00:00Z",
        ]),
        "symbol": ["AAAUSDT", "BBBUSDT"],
    }).to_parquet(path, index=False)
    return path


def _status(report: dict[str, object], check: str) -> bool:
    return next(row for row in report["checks"] if row["check"] == check)["passed"]


def test_valid_review_source_is_ready_to_build_artifact(tmp_path: Path):
    df = _rows()
    df["known_at"] = "2025-12-31T00:00:00Z"
    report = summarize_review_source(
        _write(df, tmp_path / "symbol_taxonomy.csv"),
        required_groups={"sector", "industry", "subindustry"},
        bars_path=_write_bars(tmp_path / "bars.parquet"),
    )

    assert report["ready_to_build_artifact"] is True
    assert report["blocker"] == ""
    assert report["ok_row_count"] == 2
    assert report["ok_groups_present"] == "industry|sector|subindustry"
    assert report["bar_last_timestamp"] == "2026-01-02T00:00:00Z"
    assert report["ok_rows_known_by_last_bar"] == 2
    assert report["ok_known_at_blocks_bars"] is False


def test_review_only_committed_workbook_is_not_ready():
    report = summarize_review_source(DEFAULT_SOURCE, bars_path=Path("data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet"))

    assert report["row_count"] == 266
    assert report["quality_counts"] == {"REVIEW": 266}
    assert report["ready_to_build_artifact"] is False
    assert report["blocker"] == "taxonomy_review_has_no_ok_rows"
    assert report["missing_required_ok_groups"] == "industry|sector|subindustry"
    assert report["ok_rows_known_by_last_bar"] == 0
    assert report["ok_known_at_blocks_bars"] is False


def test_ok_rows_known_after_bars_are_not_ready(tmp_path: Path):
    report = summarize_review_source(
        _write(_rows(), tmp_path / "symbol_taxonomy.csv"),
        required_groups={"sector", "industry", "subindustry"},
        bars_path=_write_bars(tmp_path / "bars.parquet"),
    )

    assert report["ready_to_build_artifact"] is False
    assert report["blocker"] == "taxonomy_review_ok_known_at_after_bars"
    assert report["bar_last_timestamp"] == "2026-01-02T00:00:00Z"
    assert report["ok_rows_known_by_last_bar"] == 0
    assert report["ok_symbols_known_by_last_bar"] == 0
    assert report["ok_rows_known_after_last_bar"] == 2
    assert report["ok_known_at_blocks_bars"] is True
    assert not _status(report, "ok_rows_known_by_latest_bar")


def test_ok_rows_missing_required_group_are_not_ready(tmp_path: Path):
    df = _rows()
    df.loc[df["quality_flag"] == "OK", "industry"] = ""

    report = summarize_review_source(
        _write(df, tmp_path / "symbol_taxonomy.csv"),
        required_groups={"sector", "industry", "subindustry"},
    )

    assert report["ready_to_build_artifact"] is False
    assert report["blocker"] == "taxonomy_review_missing_required_ok_groups"
    assert report["missing_required_ok_groups"] == "industry"
    assert not _status(report, "ok_rows_have_industry")


def test_bad_quality_flag_fails_source_check(tmp_path: Path):
    df = _rows()
    df.loc[0, "quality_flag"] = "APPROVED"

    report = summarize_review_source(_write(df, tmp_path / "symbol_taxonomy.csv"))

    assert report["ready_to_build_artifact"] is False
    assert not _status(report, "quality_flag_domain")


def test_review_source_reports_are_written(tmp_path: Path):
    report = summarize_review_source(
        _write(_rows(), tmp_path / "symbol_taxonomy.csv"),
        required_groups={"sector", "industry", "subindustry"},
    )

    out_json, out_csv = write_review_source_reports(report, tmp_path / "out")

    assert out_json.exists()
    assert out_csv.exists()
