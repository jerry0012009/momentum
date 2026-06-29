"""Tests for applying reviewed taxonomy batch packets."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from apply_crypto_industry_taxonomy_review_packet import (  # noqa: E402
    apply_review_packet,
    apply_review_packet_from_paths,
    apply_review_packets,
    apply_review_packets_from_paths,
    packet_paths_from_glob,
)


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


def _packet() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT"],
        "target_sector": ["Layer1", ""],
        "target_industry": ["Layer1.Network", ""],
        "target_subindustry": ["Layer1.Network.Native", ""],
        "target_quality_flag": ["OK", "REVIEW"],
        "target_known_at": ["2025-12-31T00:00:00Z", ""],
        "target_effective_from": ["2024-06-01T01:00:00Z", ""],
    })


def test_apply_review_packet_updates_only_explicit_ok_rows():
    updated, summary = apply_review_packet(_source(), _packet())

    aaa = updated[updated["symbol"] == "AAAUSDT"].iloc[0]
    bbb = updated[updated["symbol"] == "BBBUSDT"].iloc[0]
    assert aaa["sector"] == "Layer1"
    assert aaa["industry"] == "Layer1.Network"
    assert aaa["subindustry"] == "Layer1.Network.Native"
    assert aaa["quality_flag"] == "OK"
    assert aaa["known_at"] == "2025-12-31T00:00:00Z"
    assert aaa["effective_from"] == "2024-06-01T01:00:00Z"
    assert bbb["quality_flag"] == "REVIEW"
    assert bbb["sector"] == ""
    assert summary["approved_packet_rows"] == 1
    assert summary["updated_symbols"] == "AAAUSDT"
    assert summary["skipped_packet_rows"] == 1


def test_apply_review_packet_no_ok_rows_is_noop():
    packet = _packet()
    packet["target_quality_flag"] = "REVIEW"

    updated, summary = apply_review_packet(_source(), packet)

    assert updated.equals(_source())
    assert summary["approved_packet_rows"] == 0
    assert summary["updated_rows"] == 0


def test_apply_review_packet_requires_complete_ok_targets():
    packet = _packet()
    packet.loc[0, "target_industry"] = ""

    with pytest.raises(ValueError, match="target_industry"):
        apply_review_packet(_source(), packet)


def test_apply_review_packet_rejects_invalid_target_quality_flag():
    packet = _packet()
    packet.loc[0, "target_quality_flag"] = "APPROVED"

    with pytest.raises(ValueError, match="invalid target_quality_flag"):
        apply_review_packet(_source(), packet)


def test_apply_review_packet_from_paths_writes_output(tmp_path: Path):
    source_csv = tmp_path / "source.csv"
    packet_csv = tmp_path / "packet.csv"
    output_csv = tmp_path / "out" / "symbol_taxonomy.csv"
    _source().to_csv(source_csv, index=False)
    _packet().to_csv(packet_csv, index=False)

    summary = apply_review_packet_from_paths(source_csv, packet_csv, output_csv)
    written = pd.read_csv(output_csv).fillna("")

    assert output_csv.exists()
    assert summary["updated_rows"] == 1
    assert written.loc[written["symbol"] == "AAAUSDT", "quality_flag"].iloc[0] == "OK"


def test_apply_review_packets_applies_multiple_packets_in_order():
    second = _packet()
    second["target_quality_flag"] = ["REVIEW", "OK"]
    second["target_sector"] = ["", "DeFi"]
    second["target_industry"] = ["", "DeFi.Protocol"]
    second["target_subindustry"] = ["", "DeFi.Protocol.Utility"]
    second["target_known_at"] = ["", "2025-12-30T00:00:00Z"]
    second["target_effective_from"] = ["", "2024-06-01T01:00:00Z"]

    updated, summary = apply_review_packets(_source(), [_packet(), second])

    aaa = updated[updated["symbol"] == "AAAUSDT"].iloc[0]
    bbb = updated[updated["symbol"] == "BBBUSDT"].iloc[0]
    assert aaa["quality_flag"] == "OK"
    assert bbb["sector"] == "DeFi"
    assert bbb["quality_flag"] == "OK"
    assert summary["packet_count"] == 2
    assert summary["packet_rows"] == 4
    assert summary["approved_packet_rows"] == 2
    assert summary["updated_rows"] == 2
    assert summary["updated_symbols"] == "AAAUSDT|BBBUSDT"
    assert len(summary["packet_summaries"]) == 2


def test_apply_review_packets_rejects_empty_packet_list():
    with pytest.raises(ValueError, match="at least one packet"):
        apply_review_packets(_source(), [])


def test_apply_review_packets_from_paths_writes_output_for_multiple_packets(tmp_path: Path):
    source_csv = tmp_path / "source.csv"
    first_csv = tmp_path / "packet_001.csv"
    second_csv = tmp_path / "packet_002.csv"
    output_csv = tmp_path / "out" / "symbol_taxonomy.csv"
    second = _packet()
    second["target_quality_flag"] = ["REVIEW", "OK"]
    second["target_sector"] = ["", "DeFi"]
    second["target_industry"] = ["", "DeFi.Protocol"]
    second["target_subindustry"] = ["", "DeFi.Protocol.Utility"]
    second["target_known_at"] = ["", "2025-12-30T00:00:00Z"]
    second["target_effective_from"] = ["", "2024-06-01T01:00:00Z"]

    _source().to_csv(source_csv, index=False)
    _packet().to_csv(first_csv, index=False)
    second.to_csv(second_csv, index=False)

    summary = apply_review_packets_from_paths(source_csv, [first_csv, second_csv], output_csv)
    written = pd.read_csv(output_csv).fillna("")

    assert summary["packet_count"] == 2
    assert summary["updated_rows"] == 2
    assert summary["packet_csv"] == f"{first_csv}|{second_csv}"
    assert written.loc[written["symbol"] == "AAAUSDT", "quality_flag"].iloc[0] == "OK"
    assert written.loc[written["symbol"] == "BBBUSDT", "quality_flag"].iloc[0] == "OK"


def test_packet_paths_from_glob_filters_and_sorts_batch_packets(tmp_path: Path):
    diag = tmp_path / "diag"
    diag.mkdir()
    for name in [
        "industry_taxonomy_review_batch_010.csv",
        "industry_taxonomy_review_batch_002_validation_checks.csv",
        "industry_taxonomy_review_batch_002.csv",
        "industry_taxonomy_review_batch_validation_rollup.csv",
    ]:
        (diag / name).write_text("symbol\n")

    paths = packet_paths_from_glob(str(diag / "industry_taxonomy_review_batch_*.csv"))

    assert [path.name for path in paths] == [
        "industry_taxonomy_review_batch_002.csv",
        "industry_taxonomy_review_batch_010.csv",
    ]


def test_apply_review_packets_from_glob_output_matches_noop_source(tmp_path: Path):
    source_csv = tmp_path / "source.csv"
    first_csv = tmp_path / "industry_taxonomy_review_batch_001.csv"
    second_csv = tmp_path / "industry_taxonomy_review_batch_002.csv"
    output_csv = tmp_path / "out" / "symbol_taxonomy.csv"
    packet = _packet()
    packet["target_quality_flag"] = "REVIEW"
    _source().to_csv(source_csv, index=False)
    packet.to_csv(first_csv, index=False)
    packet.to_csv(second_csv, index=False)

    paths = packet_paths_from_glob(str(tmp_path / "industry_taxonomy_review_batch_*.csv"))
    summary = apply_review_packets_from_paths(source_csv, paths, output_csv)
    written = pd.read_csv(output_csv).fillna("")

    assert summary["packet_count"] == 2
    assert summary["approved_packet_rows"] == 0
    assert summary["updated_rows"] == 0
    assert written.equals(_source())
