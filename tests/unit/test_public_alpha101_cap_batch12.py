"""Tests for public Alpha101 market-cap panel batch 12 factor."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha56,
    rolling_sum_wide,
    to_wide,
    xs_rank,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402


def _make_panel(n: int = 40) -> pd.DataFrame:
    timestamps = pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        close = pd.Series(80 + i * 8 + idx * (0.12 + i * 0.02) + np.sin(idx / 5 + i) * 1.4)
        cap = pd.Series(1_000_000_000 * (i + 1) + idx * (2_500_000 + i * 500_000))
        frames.append(pd.DataFrame({
            "timestamp": timestamps,
            "symbol": symbol,
            "close": close.astype(float),
            "cap": cap.astype(float),
        }))
    return pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])


def _series_from_long(df: pd.DataFrame, fid: str, symbol: str) -> pd.Series:
    out = df[df["symbol"] == symbol].sort_values("timestamp")
    return out.set_index("timestamp")[fid]


def test_alpha56_spec_registered_with_cap_source_metadata():
    spec = REGISTRY_BY_ID["wq101_alpha56"]

    assert spec.family == "wq101"
    assert spec.required_columns == ["close", "cap"]
    assert spec.lookback_window == 11
    assert spec.expected_direction == "conditional"
    assert spec.compute_scope == "panel"
    assert spec.panel_compute_fn is not None


def test_alpha56_formula_matches_wide_reference():
    panel = _make_panel()
    close = to_wide(panel, "close")
    cap = to_wide(panel, "cap")
    returns = close / close.shift(1) - 1.0
    denom = rolling_sum_wide(rolling_sum_wide(returns, 2), 3).replace(0, np.nan)
    expected = -1 * xs_rank(rolling_sum_wide(returns, 10) / denom) * xs_rank(returns * cap)

    actual = _series_from_long(compute_wq101_alpha56(panel), "wq101_alpha56", "BTCUSDT")
    pd.testing.assert_series_equal(actual, expected["BTCUSDT"].dropna(), check_names=False)


def test_alpha56_requires_cap_column():
    panel = _make_panel().drop(columns=["cap"])

    try:
        compute_wq101_alpha56(panel)
    except ValueError as exc:
        assert "cap" in str(exc)
    else:
        raise AssertionError("compute_wq101_alpha56 should require cap")
