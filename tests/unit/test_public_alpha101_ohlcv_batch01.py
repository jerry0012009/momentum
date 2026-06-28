"""Tests for public Alpha101 OHLCV/VWAP batch 01 factors."""
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
    "wq101_alpha6",
    "wq101_alpha9",
    "wq101_alpha21",
    "wq101_alpha41",
    "wq101_alpha54",
]


def _make_df(n: int = 30, symbol: str = "BTCUSDT") -> pd.DataFrame:
    close = pd.Series(np.linspace(100, 115, n) + np.sin(np.arange(n)) * 2)
    high = close + 3
    low = close - 2
    open_ = close.shift(1).fillna(close.iloc[0] - 1) + 0.5
    volume = pd.Series(np.linspace(1000, 1600, n) + (np.arange(n) % 5) * 25)
    vwap = close * (1 + np.sin(np.arange(n) / 3) * 0.001)
    return pd.DataFrame({
        "symbol": [symbol] * n,
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open": open_.astype(float),
        "high": high.astype(float),
        "low": low.astype(float),
        "close": close.astype(float),
        "volume": volume.astype(float),
        "quote_volume": (volume * vwap).astype(float),
    })


def _make_two_symbol_df(n: int = 30) -> pd.DataFrame:
    btc = _make_df(n, "BTCUSDT")
    eth = _make_df(n, "ETHUSDT")
    eth["open"] = eth["open"].iloc[::-1].to_numpy() + 200
    eth["high"] = eth["high"].iloc[::-1].to_numpy() + 205
    eth["low"] = eth["low"].iloc[::-1].to_numpy() + 195
    eth["close"] = eth["close"].iloc[::-1].to_numpy() + 200
    eth["volume"] = np.linspace(2500, 900, n)
    eth["quote_volume"] = eth["volume"] * eth["close"] * 1.0005
    return pd.concat([btc, eth], ignore_index=True).sort_values(["symbol", "timestamp"])


def _compute(fid: str, df: pd.DataFrame) -> pd.Series:
    return REGISTRY_BY_ID[fid].compute_fn(df)


def _group_apply(fid: str, df: pd.DataFrame) -> pd.Series:
    return pd.concat([
        _compute(fid, g.sort_values("timestamp"))
        for _sym, g in df.groupby("symbol", sort=False)
    ])


def test_batch_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha6": (["open", "volume"], 10),
        "wq101_alpha9": (["close"], 6),
        "wq101_alpha21": (["close", "volume"], 20),
        "wq101_alpha41": (["high", "low", "volume", "quote_volume"], 1),
        "wq101_alpha54": (["open", "high", "low", "close"], 1),
    }

    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "single_symbol"


def test_alpha6_formula():
    df = _make_df(14)
    out = _compute("wq101_alpha6", df)
    expected = -df["open"].rolling(10, min_periods=10).corr(df["volume"])

    pd.testing.assert_series_equal(out, expected, check_names=False)
    assert out.iloc[:9].isna().all()


def test_alpha9_formula_branches():
    df = pd.DataFrame({"close": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 14.0, 16.0]})
    out = _compute("wq101_alpha9", df)

    assert out.iloc[:5].isna().all()
    assert out.iloc[5] == pytest.approx(1.0)
    assert out.iloc[6] == pytest.approx(1.0)


def test_alpha21_outputs_only_signed_states_after_warmup():
    df = _make_df(30)
    out = _compute("wq101_alpha21", df)
    clean = out.dropna()

    assert out.iloc[:19].isna().all()
    assert set(clean.unique()) <= {-1.0, 1.0}


def test_alpha41_uses_quote_volume_vwap():
    df = _make_df(5)
    out = _compute("wq101_alpha41", df)
    expected = np.sqrt(df["high"] * df["low"]) - (df["quote_volume"] / df["volume"])

    pd.testing.assert_series_equal(out, expected, check_names=False)


def test_alpha54_formula():
    df = pd.DataFrame({
        "open": [100.0],
        "high": [110.0],
        "low": [95.0],
        "close": [104.0],
    })
    out = _compute("wq101_alpha54", df)
    expected = (-1 * ((95 - 104) * (100 ** 5))) / ((95 - 110) * (104 ** 5))

    assert out.iloc[0] == pytest.approx(expected)


def test_no_cross_symbol_bleed_for_warmup_factors():
    df = _make_two_symbol_df(30)

    for fid in ["wq101_alpha6", "wq101_alpha9", "wq101_alpha21"]:
        out = _group_apply(fid, df)
        eth = out[df["symbol"] == "ETHUSDT"]
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        assert eth.iloc[:warmup].isna().all(), fid
