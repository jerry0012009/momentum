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
