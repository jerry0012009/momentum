"""Tests for public Alpha101 OHLCV batch 02 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha23",
    "wq101_alpha24",
    "wq101_alpha46",
    "wq101_alpha49",
    "wq101_alpha51",
]


def _make_df(n: int = 240, symbol: str = "BTCUSDT") -> pd.DataFrame:
    idx = np.arange(n, dtype=float)
    close = pd.Series(100 + idx * 0.12 + np.sin(idx / 5) * 1.7)
    high = close + 2.5 + (idx % 3) * 0.1
    low = close - 2.0 - (idx % 4) * 0.08
    open_ = close.shift(1).fillna(close.iloc[0] - 0.5) + 0.2
    volume = pd.Series(1000 + idx * 3 + (idx % 11) * 41)
    return pd.DataFrame({
        "symbol": [symbol] * n,
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open": open_.astype(float),
        "high": high.astype(float),
        "low": low.astype(float),
        "close": close.astype(float),
        "volume": volume.astype(float),
        "quote_volume": (volume * close).astype(float),
    })


def _compute(fid: str, df: pd.DataFrame) -> pd.Series:
    return REGISTRY_BY_ID[fid].compute_fn(df)


def test_batch_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha23": (["high"], 20),
        "wq101_alpha24": (["close"], 200),
        "wq101_alpha46": (["close"], 21),
        "wq101_alpha49": (["close"], 21),
        "wq101_alpha51": (["close"], 21),
    }

    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "single_symbol"


def test_alpha23_formula_breakout_and_zero_branches():
    df = _make_df(40)
    out = _compute("wq101_alpha23", df)
    high_mean_20 = df["high"].rolling(20, min_periods=20).mean()
    expected = pd.Series(np.nan, index=df.index, dtype=float)
    breakout = high_mean_20 < df["high"]
    expected.loc[high_mean_20.notna() & breakout] = (-(df["high"] - df["high"].shift(2))).loc[high_mean_20.notna() & breakout]
    expected.loc[high_mean_20.notna() & ~breakout] = 0.0

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:19].isna().all()


def test_alpha24_formula_branch_output():
    df = _make_df(240)
    out = _compute("wq101_alpha24", df)
    mean_close_100 = df["close"].rolling(100, min_periods=100).mean()
    drift = (mean_close_100 - mean_close_100.shift(100)) / df["close"].shift(100)
    low_100 = df["close"].rolling(100, min_periods=100).min()
    expected = pd.Series(np.nan, index=df.index, dtype=float)
    expected.loc[drift <= 0.05] = (-(df["close"] - low_100)).loc[drift <= 0.05]
    expected.loc[drift > 0.05] = (-(df["close"] - df["close"].shift(3))).loc[drift > 0.05]

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:198].isna().all()


def test_alpha46_formula():
    df = _make_df(40)
    out = _compute("wq101_alpha46", df)
    close = df["close"]
    slope_gap = ((close.shift(20) - close.shift(10)) / 10) - ((close.shift(10) - close) / 10)
    expected = pd.Series(np.nan, index=df.index, dtype=float)
    expected.loc[slope_gap > 0.25] = -1.0
    expected.loc[slope_gap < 0] = 1.0
    middle = (slope_gap <= 0.25) & (slope_gap >= 0)
    expected.loc[middle] = (-(close - close.shift(1))).loc[middle]

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:20].isna().all()


def test_alpha49_formula():
    df = _make_df(40)
    out = _compute("wq101_alpha49", df)
    close = df["close"]
    slope_gap = ((close.shift(20) - close.shift(10)) / 10) - ((close.shift(10) - close) / 10)
    expected = pd.Series(np.nan, index=df.index, dtype=float)
    expected.loc[slope_gap < -0.1] = 1.0
    expected.loc[slope_gap >= -0.1] = (-(close - close.shift(1))).loc[slope_gap >= -0.1]

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:20].isna().all()


def test_alpha51_formula():
    df = _make_df(40)
    out = _compute("wq101_alpha51", df)
    close = df["close"]
    slope_gap = ((close.shift(20) - close.shift(10)) / 10) - ((close.shift(10) - close) / 10)
    expected = pd.Series(np.nan, index=df.index, dtype=float)
    expected.loc[slope_gap < -0.05] = 1.0
    expected.loc[slope_gap >= -0.05] = (-(close - close.shift(1))).loc[slope_gap >= -0.05]

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:20].isna().all()


def test_no_cross_symbol_bleed_for_warmup_factors():
    btc = _make_df(240, "BTCUSDT")
    eth = _make_df(240, "ETHUSDT")
    eth["close"] = eth["close"].iloc[::-1].to_numpy() + 200
    eth["high"] = eth["close"] + 3
    eth["low"] = eth["close"] - 2
    eth["volume"] = np.linspace(5000, 800, len(eth))
    df = pd.concat([btc, eth], ignore_index=True).sort_values(["symbol", "timestamp"])

    for fid in BATCH:
        out = pd.concat([
            _compute(fid, g.sort_values("timestamp"))
            for _sym, g in df.groupby("symbol", sort=False)
        ])
        eth_out = out[df["symbol"] == "ETHUSDT"]
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        assert eth_out.iloc[:warmup].isna().all(), fid
