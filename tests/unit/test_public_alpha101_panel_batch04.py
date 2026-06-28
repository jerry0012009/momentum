"""Tests for public Alpha101 panel OHLCV/VWAP batch 04 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha34,
    compute_wq101_alpha40,
    compute_wq101_alpha42,
    compute_wq101_alpha50,
    compute_wq101_alpha55,
    compute_wq101_alpha60,
    rolling_corr_wide,
    rolling_max_wide,
    rolling_min_wide,
    rolling_std_wide,
    to_wide,
    xs_rank,
    xs_scale,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha34",
    "wq101_alpha40",
    "wq101_alpha42",
    "wq101_alpha50",
    "wq101_alpha55",
    "wq101_alpha60",
]


def _make_panel(n: int = 80) -> pd.DataFrame:
    timestamps = pd.date_range("2026-02-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 1.7
        close = pd.Series(100 + i * 2 + idx * 0.05 + np.sin(idx / 4 + phase) * (4.5 + i * 0.3))
        open_ = close.shift(1).fillna(close.iloc[0] - 0.4) + 0.1 * (i + 1)
        high = np.maximum(open_, close) + 1.4 + (idx % (3 + i)) * 0.08
        low = np.minimum(open_, close) - 1.0 - (idx % (4 + i)) * 0.04
        volume = pd.Series(1000 + i * 30 + idx * 2 + np.sin(idx / 3 + phase) * (180 + i * 20))
        vwap = close * (1 + np.sin(idx / 4 + phase) * (0.006 + i * 0.0005))
        frames.append(pd.DataFrame({
            "timestamp": timestamps,
            "symbol": symbol,
            "open": open_.astype(float),
            "high": pd.Series(high).astype(float),
            "low": pd.Series(low).astype(float),
            "close": close.astype(float),
            "volume": volume.astype(float),
            "quote_volume": (volume * vwap).astype(float),
        }))
    return pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"])


def _series_from_long(df: pd.DataFrame, fid: str, symbol: str) -> pd.Series:
    out = df[df["symbol"] == symbol].sort_values("timestamp")
    return out.set_index("timestamp")[fid]


def test_batch_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha34": (["close"], 6),
        "wq101_alpha40": (["high", "volume"], 10),
        "wq101_alpha42": (["close", "volume", "quote_volume"], 1),
        "wq101_alpha50": (["volume", "quote_volume"], 9),
        "wq101_alpha55": (["high", "low", "close", "volume"], 17),
        "wq101_alpha60": (["high", "low", "close", "volume"], 10),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_alpha42_uses_cross_sectional_rank_ratio_per_timestamp():
    panel = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-02-01"] * 3, utc=True),
        "symbol": ["A", "B", "C"],
        "open": [10.0, 10.0, 10.0],
        "high": [11.0, 11.0, 11.0],
        "low": [9.0, 9.0, 9.0],
        "close": [10.0, 12.0, 14.0],
        "volume": [100.0, 100.0, 100.0],
        "quote_volume": [1100.0, 1200.0, 1300.0],
    })
    out = compute_wq101_alpha42(panel).sort_values("symbol")
    expected = [1.0 / (1 / 3), (2 / 3) / (2 / 3), (1 / 3) / 1.0]
    assert np.allclose(out["wq101_alpha42"], expected)


def test_panel_batch04_formulas_match_wide_reference():
    panel = _make_panel()
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap_panel = panel.copy()
    vwap_panel["_vwap"] = vwap_panel["quote_volume"] / vwap_panel["volume"]
    vwap = to_wide(vwap_panel, "_vwap")

    returns = close / close.shift(1) - 1.0
    vol_ratio = rolling_std_wide(returns, 2) / rolling_std_wide(returns, 5)
    expected34 = xs_rank((1 - xs_rank(vol_ratio)) + (1 - xs_rank(close - close.shift(1))))
    expected40 = -1 * xs_rank(rolling_std_wide(high, 10)) * rolling_corr_wide(high, volume, 10)
    expected42 = xs_rank(vwap - close) / xs_rank(vwap + close)
    expected50 = -1 * rolling_max_wide(xs_rank(rolling_corr_wide(xs_rank(volume), xs_rank(vwap), 5)), 5)
    low_12 = rolling_min_wide(low, 12)
    position = (close - low_12) / (rolling_max_wide(high, 12) - low_12)
    expected55 = -1 * rolling_corr_wide(xs_rank(position), xs_rank(volume), 6)
    clv = ((close - low) - (high - close)) / (high - low)
    argmax_close = close.rolling(window=10, min_periods=10).apply(lambda x: int(np.nanargmax(x[::-1])), raw=True)
    expected60 = -1 * ((2 * xs_scale(xs_rank(clv * volume))) - xs_scale(xs_rank(argmax_close)))

    outputs = {
        "wq101_alpha34": (compute_wq101_alpha34(panel), expected34),
        "wq101_alpha40": (compute_wq101_alpha40(panel), expected40),
        "wq101_alpha42": (compute_wq101_alpha42(panel), expected42),
        "wq101_alpha50": (compute_wq101_alpha50(panel), expected50),
        "wq101_alpha55": (compute_wq101_alpha55(panel), expected55),
        "wq101_alpha60": (compute_wq101_alpha60(panel), expected60),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_warmups_are_not_cross_symbol_bleeding():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        if warmup > 0:
            first_valid_pos = panel[panel["symbol"] == "ETHUSDT"].iloc[warmup]["timestamp"]
            assert eth.index.min() >= first_valid_pos
