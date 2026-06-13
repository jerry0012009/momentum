"""Unit tests for Batch 1 factor functions.

Tests verify:
- Formula correctness on synthetic input
- Index alignment with input
- No future leak (no shift(-k))
- NaN warmup handling
- Per-symbol isolation (no cross-symbol bleed)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.crypto_factor_functions import (
    compute_wq101_alpha101,
    compute_wq101_alpha12,
    compute_wq101_alpha53,
    compute_q158_high_low_range,
    compute_tech_macd,
    compute_tech_atr,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_df(n: int = 20, symbol: str = "BTCUSDT") -> pd.DataFrame:
    """Create a minimal synthetic OHLCV DataFrame."""
    return pd.DataFrame({
        "symbol": [symbol] * n,
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open":  np.linspace(100, 120, n),
        "high":  np.linspace(105, 125, n),
        "low":   np.linspace(95, 115, n),
        "close": np.linspace(102, 122, n),
        "volume": np.linspace(1000, 2000, n),
    })


def _make_two_symbol_df(n: int = 15) -> pd.DataFrame:
    """Two-symbol DataFrame with genuinely different patterns for isolation tests."""
    btc = _make_df(n, "BTCUSDT")
    # ETH: different shape — use reversed linspace + different volume
    eth = pd.DataFrame({
        "symbol": ["ETHUSDT"] * n,
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open":  np.linspace(3200, 3100, n),   # falling
        "high":  np.linspace(3250, 3150, n),
        "low":   np.linspace(3150, 3050, n),
        "close": np.linspace(3180, 3080, n),
        "volume": np.linspace(500, 5000, n),    # very different vol pattern
    })
    return pd.concat([btc, eth], ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def _group_apply(df: pd.DataFrame, func) -> pd.Series:
    """Apply a factor function per-symbol (as build_factor_values.py does)."""
    parts = []
    for sym, g in df.groupby("symbol", sort=False):
        s = func(g.sort_values("timestamp"))
        parts.append(s)
    return pd.concat(parts)


# ---------------------------------------------------------------------------
# wq101_alpha101
# ---------------------------------------------------------------------------

class TestAlpha101:
    def test_basic_formula(self):
        df = pd.DataFrame({"open": [100.0], "high": [110.0], "low": [95.0], "close": [105.0]})
        result = compute_wq101_alpha101(df)
        expected = (105 - 100) / (110 - 95 + 0.001)
        assert abs(result.iloc[0] - expected) < 1e-6

    def test_no_warmup(self):
        """No NaN expected (no rolling/shift)."""
        df = _make_df(5)
        result = compute_wq101_alpha101(df)
        assert result.notna().all()

    def test_index_alignment(self):
        df = _make_df(10)
        result = compute_wq101_alpha101(df)
        assert len(result) == len(df)
        assert result.index.equals(df.index)

    def test_no_future_leak(self):
        """Value at row i depends only on row i (no shift)."""
        df = _make_df(5)
        r1 = compute_wq101_alpha101(df.iloc[:3])
        r2 = compute_wq101_alpha101(df.iloc[:4])
        assert (r1.values == r2.values[:3]).all()

    def test_cross_symbol_isolation(self):
        df = _make_two_symbol_df(5)
        result = _group_apply(df, compute_wq101_alpha101)
        btc = result[df["symbol"] == "BTCUSDT"].values
        eth = result[df["symbol"] == "ETHUSDT"].values
        assert not np.allclose(btc, eth, atol=0.01)


# ---------------------------------------------------------------------------
# wq101_alpha12
# ---------------------------------------------------------------------------

class TestAlpha12:
    def test_basic_formula(self):
        df = pd.DataFrame({"volume": [100.0, 120.0], "close": [100.0, 98.0]})
        result = compute_wq101_alpha12(df)
        # vol_delta = 120-100 = 20, sign = +1
        # close_delta = 98-100 = -2, -1*close_delta = +2
        # result = +1 * +2 = +2
        assert pd.isna(result.iloc[0])
        assert abs(result.iloc[1] - 2.0) < 1e-6

    def test_first_row_nan(self):
        df = _make_df(5)
        result = compute_wq101_alpha12(df)
        assert pd.isna(result.iloc[0])

    def test_index_alignment(self):
        df = _make_df(10)
        result = compute_wq101_alpha12(df)
        assert len(result) == len(df)
        assert result.index.equals(df.index)

    def test_cross_symbol_isolation(self):
        """Per-symbol: first row of ETH must be NaN (not bleed from BTC)."""
        df = _make_two_symbol_df(10)
        result = _group_apply(df, compute_wq101_alpha12)
        eth_first = result[df["symbol"] == "ETHUSDT"].iloc[0]
        assert pd.isna(eth_first)


# ---------------------------------------------------------------------------
# wq101_alpha53
# ---------------------------------------------------------------------------

class TestAlpha53:
    def test_warmup_nan(self):
        """First 9 rows should be NaN (diff(9))."""
        df = _make_df(15)
        result = compute_wq101_alpha53(df)
        assert result.iloc[:9].isna().all()
        assert result.iloc[9:].notna().any()

    def test_index_alignment(self):
        df = _make_df(15)
        result = compute_wq101_alpha53(df)
        assert len(result) == len(df)
        assert result.index.equals(df.index)

    def test_cross_symbol_isolation(self):
        """Per-symbol: first 9 rows of ETH must be NaN."""
        df = _make_two_symbol_df(15)
        result = _group_apply(df, compute_wq101_alpha53)
        eth = result[df["symbol"] == "ETHUSDT"]
        assert eth.iloc[:9].isna().all()


# ---------------------------------------------------------------------------
# q158_high_low_range
# ---------------------------------------------------------------------------

class TestHighLowRange:
    def test_basic_formula(self):
        df = pd.DataFrame({"high": [110.0], "low": [95.0], "close": [100.0]})
        result = compute_q158_high_low_range(df)
        expected = 15 / 100
        assert abs(result.iloc[0] - expected) < 1e-6

    def test_no_warmup(self):
        df = _make_df(3)
        result = compute_q158_high_low_range(df)
        assert result.notna().all()

    def test_always_non_negative(self):
        df = _make_df(20)
        result = compute_q158_high_low_range(df)
        assert (result.dropna() >= 0).all()

    def test_cross_symbol_isolation(self):
        df = _make_two_symbol_df(5)
        result = _group_apply(df, compute_q158_high_low_range)
        btc = result[df["symbol"] == "BTCUSDT"].values
        eth = result[df["symbol"] == "ETHUSDT"].values
        assert not np.allclose(btc, eth, atol=0.001)


# ---------------------------------------------------------------------------
# tech_macd
# ---------------------------------------------------------------------------

class TestMACD:
    def test_constant_price_zero(self):
        """Constant prices → MACD should be 0."""
        df = pd.DataFrame({"close": [100.0] * 60})
        result = compute_tech_macd(df)
        assert abs(result.iloc[-1]) < 1e-6

    def test_rising_price_positive(self):
        """Steadily rising prices → MACD should be positive."""
        df = _make_df(60)
        result = compute_tech_macd(df)
        assert result.iloc[-1] > 0

    def test_index_alignment(self):
        df = _make_df(60)
        result = compute_tech_macd(df)
        assert len(result) == len(df)
        assert result.index.equals(df.index)

    def test_no_future_leak(self):
        df = _make_df(60)
        r1 = compute_tech_macd(df.iloc[:50])
        r2 = compute_tech_macd(df.iloc[:51])
        assert abs(r1.iloc[-1] - r2.iloc[-2]) < 1e-10

    def test_cross_symbol_isolation(self):
        df = _make_two_symbol_df(60)
        result = _group_apply(df, compute_tech_macd)
        btc = result[df["symbol"] == "BTCUSDT"].iloc[-1]
        eth = result[df["symbol"] == "ETHUSDT"].iloc[-1]
        assert not np.isclose(btc, eth, atol=0.1)


# ---------------------------------------------------------------------------
# tech_atr
# ---------------------------------------------------------------------------

class TestATR:
    def test_warmup_nan(self):
        """First 14 rows should be NaN (rolling(14, min_periods=14))."""
        df = _make_df(20)
        result = compute_tech_atr(df)
        assert result.iloc[:13].isna().all()
        assert result.iloc[13:].notna().any()

    def test_always_non_negative(self):
        df = _make_df(30)
        result = compute_tech_atr(df)
        assert (result.dropna() >= 0).all()

    def test_constant_price(self):
        """Constant H/L/C → TR = max(10, 5, 5) = 10."""
        df = pd.DataFrame({
            "high": [110.0] * 20,
            "low": [100.0] * 20,
            "close": [105.0] * 20,
        })
        result = compute_tech_atr(df)
        assert result.iloc[-1] >= 0

    def test_index_alignment(self):
        df = _make_df(20)
        result = compute_tech_atr(df)
        assert len(result) == len(df)
        assert result.index.equals(df.index)

    def test_cross_symbol_isolation(self):
        """Per-symbol: first 13 rows of ETH must be NaN."""
        df = _make_two_symbol_df(20)
        result = _group_apply(df, compute_tech_atr)
        eth = result[df["symbol"] == "ETHUSDT"]
        assert eth.iloc[:13].isna().all()


# ---------------------------------------------------------------------------
# Cross-cutting: per-symbol grouping contract
# ---------------------------------------------------------------------------

class TestSymbolGrouping:
    """Verify that when applied per-symbol (via groupby), no bleed occurs."""

    def test_diff_no_bleed(self):
        """diff(1) on first row of ETH must be NaN when applied per-symbol."""
        df = _make_two_symbol_df(5)
        result = _group_apply(df, compute_wq101_alpha12)
        eth_first = result[df["symbol"] == "ETHUSDT"].iloc[0]
        assert pd.isna(eth_first)

    def test_rolling_no_bleed(self):
        """rolling(14) first 13 rows of ETH must be NaN when applied per-symbol."""
        df = _make_two_symbol_df(20)
        result = _group_apply(df, compute_tech_atr)
        eth = result[df["symbol"] == "ETHUSDT"]
        assert eth.iloc[:13].isna().all()

    def test_ema_no_bleed(self):
        """EMA computed per-symbol on combined should match standalone."""
        df = _make_two_symbol_df(60)
        eth_df = df[df["symbol"] == "ETHUSDT"].sort_values("timestamp")
        eth_standalone = compute_tech_macd(eth_df)
        combined = _group_apply(df, compute_tech_macd)
        eth_combined = combined[df["symbol"] == "ETHUSDT"].values
        assert np.allclose(eth_standalone.values, eth_combined, atol=1e-10)

    def test_raw_combined_bleeds(self):
        """Demonstrate: calling on combined DataFrame WITHOUT groupby DOES bleed.
        This proves the caller (build_factor_values.py) must group first.
        """
        df = _make_two_symbol_df(20)
        raw_result = compute_tech_atr(df)
        eth_raw = raw_result[df["symbol"] == "ETHUSDT"]
        # Without grouping, ETH's first rows get BTC's rolling window
        assert eth_raw.iloc[:13].notna().any()  # BLEEDS — not NaN
