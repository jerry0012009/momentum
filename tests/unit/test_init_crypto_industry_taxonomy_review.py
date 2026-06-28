"""Tests for taxonomy review CSV initialization."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from init_crypto_industry_taxonomy_review import (  # noqa: E402
    TAXONOMY_COLUMNS,
    init_review_csv,
    initialize_review_taxonomy,
)


def _bars() -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-01-02 00:00Z",
            "2026-01-01 00:00Z",
            "2026-01-03 00:00Z",
            "2026-01-01 05:00Z",
        ]),
        "symbol": ["BBBUSDT", "AAAUSDT", "AAAUSDT", "BBBUSDT"],
        "close": [1.0, 2.0, 3.0, 4.0],
    })


def test_initialize_review_taxonomy_creates_review_rows_by_symbol():
    out = initialize_review_taxonomy(
        _bars(),
        known_at="2026-06-28T00:00:00Z",
        taxonomy_version="review_v1",
        source="manual_review",
    )

    assert list(out.columns) == TAXONOMY_COLUMNS
    assert list(out["symbol"]) == ["AAAUSDT", "BBBUSDT"]
    assert set(out["quality_flag"]) == {"REVIEW"}
    assert set(out["sector"]) == {""}
    assert out.loc[out["symbol"] == "AAAUSDT", "effective_from"].iloc[0] == "2026-01-01T00:00:00Z"
    assert out.loc[out["symbol"] == "BBBUSDT", "effective_from"].iloc[0] == "2026-01-01T05:00:00Z"


def test_initialize_review_taxonomy_requires_bars_columns():
    with pytest.raises(ValueError, match="bars missing required columns"):
        initialize_review_taxonomy(
            pd.DataFrame({"symbol": ["AAAUSDT"]}),
            known_at="2026-06-28T00:00:00Z",
            taxonomy_version="review_v1",
            source="manual_review",
        )


def test_init_review_csv_refuses_to_overwrite_existing_output(tmp_path: Path):
    bars_path = tmp_path / "bars.parquet"
    output_csv = tmp_path / "symbol_taxonomy.csv"
    _bars().to_parquet(bars_path, index=False)
    output_csv.write_text("existing\n")

    with pytest.raises(FileExistsError):
        init_review_csv(
            bars_path,
            output_csv,
            known_at="2026-06-28T00:00:00Z",
            taxonomy_version="review_v1",
            source="manual_review",
        )


def test_init_review_csv_writes_output_when_overwrite_enabled(tmp_path: Path):
    bars_path = tmp_path / "bars.parquet"
    output_csv = tmp_path / "symbol_taxonomy.csv"
    _bars().to_parquet(bars_path, index=False)
    output_csv.write_text("existing\n")

    out = init_review_csv(
        bars_path,
        output_csv,
        known_at="2026-06-28T00:00:00Z",
        taxonomy_version="review_v1",
        source="manual_review",
        overwrite=True,
    )

    assert len(out) == 2
    written = pd.read_csv(output_csv)
    assert list(written.columns) == TAXONOMY_COLUMNS
    assert set(written["quality_flag"]) == {"REVIEW"}
