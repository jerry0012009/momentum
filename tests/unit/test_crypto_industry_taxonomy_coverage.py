"""Tests for taxonomy coverage QA."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_crypto_industry_taxonomy_coverage import summarize_taxonomy_coverage  # noqa: E402


def _bars() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-01-02 00:00Z",
            "2026-01-01 00:00Z",
            "2026-01-02 00:00Z",
        ]),
        "symbol": ["AAAUSDT", "AAAUSDT", "BBBUSDT", "BBBUSDT"],
    })


def _taxonomy() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "BBBUSDT"],
        "known_at": pd.to_datetime(["2025-12-31 00:00Z", "2025-12-31 00:00Z"]),
        "effective_from": pd.to_datetime(["2025-12-01 00:00Z", "2025-12-01 00:00Z"]),
        "effective_to": [pd.NaT, pd.NaT],
        "sector": ["L1", "L2"],
        "industry": ["L1a", "L2a"],
        "subindustry": ["L1a1", "L2a1"],
        "taxonomy_version": ["v1", "v1"],
        "source": ["reviewed", "reviewed"],
        "quality_flag": ["OK", "OK"],
    })


def _passed(checks, name: str) -> bool:
    return next(c for c in checks if c["check"] == name)["passed"]


def test_taxonomy_coverage_passes_when_all_bars_have_groups():
    summary, checks, symbol_coverage = summarize_taxonomy_coverage(
        _bars(),
        _taxonomy(),
        min_full_coverage=1.0,
    )

    assert summary["full_group_coverage_rate"] == 1.0
    assert summary["symbol_coverage_rate"] == 1.0
    assert _passed(checks, "taxonomy_full_group_coverage")
    assert set(symbol_coverage["symbol"]) == {"AAAUSDT", "BBBUSDT"}


def test_taxonomy_coverage_fails_when_symbol_missing():
    taxonomy = _taxonomy()
    taxonomy = taxonomy[taxonomy["symbol"] != "BBBUSDT"]

    summary, checks, symbol_coverage = summarize_taxonomy_coverage(
        _bars(),
        taxonomy,
        min_full_coverage=0.98,
    )

    assert summary["full_group_coverage_rate"] == 0.5
    assert summary["covered_symbols"] == 1
    assert not _passed(checks, "taxonomy_symbol_coverage")
    assert not _passed(checks, "taxonomy_full_group_coverage")
    bbb = symbol_coverage[symbol_coverage["symbol"] == "BBBUSDT"].iloc[0]
    assert bbb["full_group_coverage_rate"] == 0.0


def test_taxonomy_coverage_does_not_count_future_known_rows():
    taxonomy = _taxonomy()
    taxonomy.loc[taxonomy["symbol"] == "BBBUSDT", "known_at"] = pd.Timestamp("2026-01-03 00:00Z")

    summary, checks, _symbol_coverage = summarize_taxonomy_coverage(
        _bars(),
        taxonomy,
        min_full_coverage=0.98,
    )

    assert summary["full_group_coverage_rate"] == 0.5
    assert not _passed(checks, "taxonomy_full_group_coverage")
