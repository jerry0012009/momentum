"""Tests for crypto industry taxonomy review-priority reports."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_crypto_industry_taxonomy_review_priority import (  # noqa: E402
    build_review_priority,
    summarize_bars_by_symbol,
    write_priority_reports,
)


def _taxonomy() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT", "CCCUSDT"],
        "known_at": ["2026-06-28T00:00:00Z"] * 3,
        "effective_from": ["2026-01-01T00:00:00Z"] * 3,
        "effective_to": ["", "", ""],
        "sector": ["Layer1", "", "Meme"],
        "industry": ["Layer1", "", "Meme"],
        "subindustry": ["Layer1", "", "Meme"],
        "taxonomy_version": ["reviewed_v1"] * 3,
        "source": ["manual_review"] * 3,
        "quality_flag": ["OK", "REVIEW", "OK"],
    })


def _bars() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-01-01 01:00Z",
            "2026-01-01 00:00Z",
            "2026-01-01 00:00Z",
            "2026-01-01 01:00Z",
            "2026-01-01 00:00Z",
        ]),
        "symbol": ["AAAUSDT", "AAAUSDT", "BBBUSDT", "CCCUSDT", "CCCUSDT", "DDDUSDT"],
        "quote_volume": [100.0, 200.0, 500.0, 25.0, 25.0, 175.0],
    })


def test_summarize_bars_by_symbol_uses_quote_volume_and_timestamps():
    stats = summarize_bars_by_symbol(_bars())

    aaa = stats[stats["symbol"] == "AAAUSDT"].iloc[0]
    assert aaa["bar_count"] == 2
    assert aaa["quote_volume_sum"] == 300.0
    assert str(aaa["first_seen"]) == "2026-01-01 00:00:00+00:00"
    assert str(aaa["last_seen"]) == "2026-01-01 01:00:00+00:00"


def test_review_priority_ranks_by_quote_volume_and_marks_actions():
    priority, summary = build_review_priority(_taxonomy(), _bars())

    assert priority["symbol"].tolist() == ["BBBUSDT", "AAAUSDT", "DDDUSDT", "CCCUSDT"]
    assert priority["review_priority_rank"].tolist() == [1, 2, 3, 4]
    assert priority.loc[priority["symbol"] == "BBBUSDT", "review_action"].iloc[0] == "review_groups"
    assert priority.loc[priority["symbol"] == "AAAUSDT", "review_action"].iloc[0] == "already_ok"
    assert priority.loc[priority["symbol"] == "DDDUSDT", "review_action"].iloc[0] == "add_taxonomy_row"
    assert priority.loc[priority["symbol"] == "BBBUSDT", "missing_group_count"].iloc[0] == 3
    assert summary["row_count"] == 4
    assert summary["taxonomy_rows"] == 3
    assert summary["bar_symbols"] == 4
    assert summary["symbols_missing_from_taxonomy"] == 1
    assert summary["symbols_needing_review"] == 2
    assert summary["top_symbol"] == "BBBUSDT"
    assert summary["quote_volume_sum"] == 1025.0


def test_review_priority_does_not_fill_taxonomy_groups():
    priority, _summary = build_review_priority(_taxonomy(), _bars())

    bbb = priority[priority["symbol"] == "BBBUSDT"].iloc[0]
    assert bool(bbb["missing_sector"])
    assert bool(bbb["missing_industry"])
    assert bool(bbb["missing_subindustry"])


def test_missing_quote_volume_column_fails():
    bars = _bars().drop(columns=["quote_volume"])

    with pytest.raises(ValueError, match="quote_volume"):
        build_review_priority(_taxonomy(), bars)


def test_priority_reports_are_written(tmp_path: Path):
    priority, summary = build_review_priority(_taxonomy(), _bars())

    out_json, out_csv = write_priority_reports(
        priority,
        summary,
        tmp_path / "out",
        tmp_path / "symbol_taxonomy.csv",
        tmp_path / "bars.parquet",
    )

    assert out_json.exists()
    assert out_csv.exists()
    assert "no taxonomy groups are inferred" in out_json.read_text()
