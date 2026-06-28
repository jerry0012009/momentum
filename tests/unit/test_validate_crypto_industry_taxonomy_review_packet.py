"""Tests for manually reviewed taxonomy batch packet validation."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from validate_crypto_industry_taxonomy_review_packet import (  # noqa: E402
    validate_review_packet,
    validate_review_packet_from_paths,
    write_packet_validation_reports,
)


def _packet() -> pd.DataFrame:
    return pd.DataFrame({
        "review_batch_id": [1, 1],
        "symbol": ["AAAUSDT", "BBBUSDT"],
        "bar_count_share": [0.10, 0.05],
        "quote_volume_share": [0.25, 0.10],
        "target_sector": ["Layer1", ""],
        "target_industry": ["Layer1.Network", ""],
        "target_subindustry": ["Layer1.Network.Native", ""],
        "target_quality_flag": ["OK", "REVIEW"],
        "target_known_at": ["2025-12-31T00:00:00Z", ""],
        "target_effective_from": ["2024-06-01T01:00:00Z", ""],
    })


def _source() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT"],
        "known_at": ["2026-06-28T00:00:00Z", "2026-06-28T00:00:00Z"],
        "effective_from": ["2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"],
        "effective_to": ["", ""],
        "sector": ["", ""],
        "industry": ["", ""],
        "subindustry": ["", ""],
        "taxonomy_version": ["reviewed_v1", "reviewed_v1"],
        "source": ["manual_review", "manual_review"],
        "quality_flag": ["REVIEW", "REVIEW"],
    })


def _write_bars(path: Path) -> Path:
    pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01 00:00Z", "2026-01-02 00:00Z"]),
        "symbol": ["AAAUSDT", "BBBUSDT"],
    }).to_parquet(path, index=False)
    return path


def _status(report: dict[str, object], check: str) -> bool:
    return next(row for row in report["checks"] if row["check"] == check)["passed"]


def test_valid_review_packet_passes_with_source_and_bars(tmp_path: Path):
    packet_csv = tmp_path / "packet.csv"
    source_csv = tmp_path / "source.csv"
    _packet().to_csv(packet_csv, index=False)
    _source().to_csv(source_csv, index=False)

    report = validate_review_packet_from_paths(
        packet_csv,
        source_csv=source_csv,
        bars_path=_write_bars(tmp_path / "bars.parquet"),
    )

    assert report["overall_pass"] is True
    assert report["blocker"] == ""
    assert report["approved_packet_rows"] == 1
    assert report["approved_symbols"] == "AAAUSDT"
    assert report["approved_bar_count_share"] == 0.10
    assert report["approved_quote_volume_share"] == 0.25
    assert report["latest_bar_timestamp"] == "2026-01-02T00:00:00Z"


def test_no_ok_rows_fail_by_default_but_can_be_allowed_for_structure_check():
    packet = _packet()
    packet["target_quality_flag"] = "REVIEW"

    report = validate_review_packet(packet, allow_no_ok=False)
    allowed = validate_review_packet(packet, allow_no_ok=True)

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_has_no_ok_target_rows"
    assert _status(report, "has_ok_target_rows") is False
    assert allowed["overall_pass"] is True


def test_ok_rows_missing_target_field_fail():
    packet = _packet()
    packet.loc[0, "target_industry"] = ""

    report = validate_review_packet(packet)

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_validation_checks_failed"
    assert _status(report, "ok_rows_have_target_industry") is False


def test_known_at_after_latest_bar_fails(tmp_path: Path):
    packet = _packet()
    packet.loc[0, "target_known_at"] = "2026-06-28T00:00:00Z"

    report = validate_review_packet(packet, latest_bar=pd.Timestamp("2026-01-02T00:00:00Z"))

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_ok_known_at_after_latest_bar"
    assert _status(report, "ok_known_at_not_after_latest_bar") is False


def test_packet_symbol_missing_from_source_fails():
    source = _source()
    source = source[source["symbol"] != "AAAUSDT"]

    report = validate_review_packet(_packet(), source=source)

    assert report["overall_pass"] is False
    assert report["blocker"] == "packet_symbols_missing_from_source"
    assert _status(report, "packet_symbols_exist_in_source") is False


def test_packet_validation_reports_are_written(tmp_path: Path):
    report = validate_review_packet(_packet())

    out_json, out_csv = write_packet_validation_reports(report, tmp_path)

    assert out_json.exists()
    assert out_csv.exists()
    assert out_json.name == "industry_taxonomy_review_packet_validation.json"
    assert out_csv.name == "industry_taxonomy_review_packet_validation_checks.csv"


def test_packet_validation_reports_support_custom_stem(tmp_path: Path):
    report = validate_review_packet(_packet())

    out_json, out_csv = write_packet_validation_reports(
        report,
        tmp_path,
        report_stem="industry_taxonomy_review_batch_002_validation",
    )

    assert out_json.name == "industry_taxonomy_review_batch_002_validation.json"
    assert out_csv.name == "industry_taxonomy_review_batch_002_validation_checks.csv"


def test_packet_validation_report_stem_must_not_be_path(tmp_path: Path):
    report = validate_review_packet(_packet())

    try:
        write_packet_validation_reports(report, tmp_path, report_stem="bad/name")
    except ValueError as exc:
        assert "file stem" in str(exc)
    else:
        raise AssertionError("expected report_stem path to be rejected")
