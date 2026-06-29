"""Tests for point-in-time taxonomy attachment in build_factor_values.py."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_factor_values import (  # noqa: E402
    load_skipped_public_factor_ids,
    merge_point_in_time_taxonomy,
    validate_not_skipped_public_factor_ids,
)


def _bars() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-01 00:00Z",
            "2026-01-02 00:00Z",
            "2026-01-03 00:00Z",
            "2026-01-03 00:00Z",
        ]),
        "symbol": ["AAAUSDT", "AAAUSDT", "AAAUSDT", "BBBUSDT"],
        "close": [1.0, 2.0, 3.0, 4.0],
    })


def _taxonomy() -> pd.DataFrame:
    return pd.DataFrame({
        "symbol": ["AAAUSDT", "AAAUSDT", "AAAUSDT", "BBBUSDT"],
        "known_at": pd.to_datetime([
            "2025-12-31 00:00Z",
            "2026-01-02 00:00Z",
            "2026-01-04 00:00Z",
            "2026-01-01 00:00Z",
        ]),
        "effective_from": pd.to_datetime([
            "2025-12-01 00:00Z",
            "2026-01-02 00:00Z",
            "2026-01-03 00:00Z",
            "2026-01-01 00:00Z",
        ]),
        "effective_to": [pd.NaT, pd.NaT, pd.NaT, pd.NaT],
        "sector": ["old_sector", "new_sector", "future_known_sector", "bad_sector"],
        "industry": ["old_industry", "new_industry", "future_known_industry", "bad_industry"],
        "subindustry": ["old_sub", "new_sub", "future_known_sub", "bad_sub"],
        "taxonomy_version": ["v1", "v2", "v3", "v1"],
        "source": ["manual", "manual", "manual", "manual"],
        "quality_flag": ["OK", "OK", "OK", "REVIEW"],
    })


def test_merge_point_in_time_taxonomy_uses_latest_known_valid_mapping():
    out = merge_point_in_time_taxonomy(_bars(), _taxonomy())

    assert out.loc[0, "sector"] == "old_sector"
    assert out.loc[1, "sector"] == "new_sector"
    assert out.loc[2, "sector"] == "new_sector"
    assert out.loc[2, "taxonomy_version"] == "v2"


def test_merge_point_in_time_taxonomy_ignores_future_known_and_non_ok_rows():
    out = merge_point_in_time_taxonomy(_bars(), _taxonomy())

    assert "future_known_sector" not in set(out["sector"].dropna())
    assert pd.isna(out.loc[3, "sector"])
    assert pd.isna(out.loc[3, "industry"])
    assert pd.isna(out.loc[3, "subindustry"])


def test_merge_point_in_time_taxonomy_respects_effective_to():
    taxonomy = _taxonomy()
    taxonomy["effective_to"] = pd.to_datetime(taxonomy["effective_to"], utc=True)
    taxonomy.loc[0, "effective_to"] = pd.Timestamp("2026-01-02 00:00Z")
    taxonomy = taxonomy[taxonomy["taxonomy_version"] != "v2"]

    out = merge_point_in_time_taxonomy(_bars(), taxonomy)

    assert out.loc[0, "sector"] == "old_sector"
    assert pd.isna(out.loc[1, "sector"])


def test_merge_point_in_time_taxonomy_requires_contract_columns():
    taxonomy = _taxonomy().drop(columns=["known_at"])

    with pytest.raises(ValueError, match="taxonomy missing required columns"):
        merge_point_in_time_taxonomy(_bars(), taxonomy)


def test_build_factor_values_loads_skipped_public_factor_ids():
    skipped = load_skipped_public_factor_ids()

    assert "wq101_alpha58_indneutralize_skipped" in skipped
    assert "q158_roc_5h_skipped" in skipped
    assert "wq101_alpha56" not in skipped


def test_build_factor_values_rejects_skipped_public_factor_ids():
    with pytest.raises(ValueError, match="Public manifest skipped factor IDs cannot be built"):
        validate_not_skipped_public_factor_ids(
            ["rev_1h", "wq101_alpha58_indneutralize_skipped"],
            {"wq101_alpha58_indneutralize_skipped"},
        )
