"""Tests for public Alpha101 panel OHLCV/VWAP batch 05 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha25,
    compute_wq101_alpha28,
    compute_wq101_alpha30,
    compute_wq101_alpha35,
    compute_wq101_alpha43,
    compute_wq101_alpha52,
    rolling_corr_wide,
    rolling_mean_wide,
    rolling_min_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
    xs_scale,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha25",
    "wq101_alpha28",
    "wq101_alpha30",
    "wq101_alpha35",
    "wq101_alpha43",
    "wq101_alpha52",
]


def _make_panel(n: int = 320) -> pd.DataFrame:
    timestamps = pd.date_range("2026-03-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 1.3
        close = pd.Series(80 + i * 4 + idx * 0.035 + np.sin(idx / 5 + phase) * (3.0 + i * 0.2))
        open_ = close.shift(1).fillna(close.iloc[0] - 0.3) + 0.08 * (i + 1)
        high = np.maximum(open_, close) + 1.2 + (idx % (4 + i)) * 0.05
        low = np.minimum(open_, close) - 0.9 - (idx % (5 + i)) * 0.04
        volume = pd.Series(900 + i * 70 + idx * (1.5 + i * 0.2) + np.sin(idx / 4 + phase) * (160 + i * 15))
        vwap = close * (1 + np.cos(idx / 7 + phase) * (0.004 + i * 0.0004))
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


def test_batch05_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha25": (["high", "close", "volume", "quote_volume"], 20),
        "wq101_alpha28": (["high", "low", "close", "volume"], 24),
        "wq101_alpha30": (["close", "volume"], 20),
        "wq101_alpha35": (["high", "low", "close", "volume"], 33),
        "wq101_alpha43": (["close", "volume"], 39),
        "wq101_alpha52": (["low", "close", "volume"], 241),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_alpha25_uses_cross_sectional_rank_per_timestamp():
    panel = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-03-01 20:00"] * 3, utc=True),
        "symbol": ["A", "B", "C"],
        "open": [10.0, 10.0, 10.0],
        "high": [12.0, 13.0, 14.0],
        "low": [9.0, 9.0, 9.0],
        "close": [11.0, 11.0, 11.0],
        "volume": [100.0, 200.0, 300.0],
        "quote_volume": [1100.0, 2200.0, 3300.0],
    })
    history = []
    for h in range(20):
        step = panel.copy()
        step["timestamp"] = pd.Timestamp("2026-03-01", tz="UTC") + pd.Timedelta(hours=h)
        step["close"] = step["close"] - (20 - h) * 0.1
        step["high"] = step["high"] - (20 - h) * 0.1
        history.append(step)
    out = compute_wq101_alpha25(pd.concat(history, ignore_index=True)).sort_values(["timestamp", "symbol"])
    latest = out[out["timestamp"] == out["timestamp"].max()].sort_values("symbol")
    assert latest["wq101_alpha25"].tolist() == [1.0, 2 / 3, 1 / 3]


def test_panel_batch05_formulas_match_wide_reference():
    panel = _make_panel()
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap_panel = panel.copy()
    vwap_panel["_vwap"] = vwap_panel["quote_volume"] / vwap_panel["volume"]
    vwap = to_wide(vwap_panel, "_vwap")

    returns = close / close.shift(1) - 1.0
    adv20 = rolling_mean_wide(volume, 20)
    expected25 = xs_rank((-1 * returns * adv20 * vwap) * (high - close))
    expected28 = xs_scale(rolling_corr_wide(adv20, low, 5) + ((high + low) / 2) - close)
    close_delta = close - close.shift(1)
    sign_sum = np.sign(close_delta) + np.sign(close_delta.shift(1)) + np.sign(close_delta.shift(2))
    expected30 = ((1 - xs_rank(sign_sum)) * rolling_sum_wide(volume, 5)) / rolling_sum_wide(volume, 20)
    expected35 = ts_rank_wide(volume, 32) * (1 - ts_rank_wide(close + high - low, 16)) * (1 - ts_rank_wide(returns, 32))
    expected43 = ts_rank_wide(volume / adv20, 20) * ts_rank_wide(-1 * (close - close.shift(7)), 8)
    min_low_5 = rolling_min_wide(low, 5)
    ret_mean_gap = (rolling_sum_wide(returns, 240) - rolling_sum_wide(returns, 20)) / 220
    expected52 = -1 * (min_low_5 - min_low_5.shift(5)) * xs_rank(ret_mean_gap) * ts_rank_wide(volume, 5)

    outputs = {
        "wq101_alpha25": (compute_wq101_alpha25(panel), expected25),
        "wq101_alpha28": (compute_wq101_alpha28(panel), expected28),
        "wq101_alpha30": (compute_wq101_alpha30(panel), expected30),
        "wq101_alpha35": (compute_wq101_alpha35(panel), expected35),
        "wq101_alpha43": (compute_wq101_alpha43(panel), expected43),
        "wq101_alpha52": (compute_wq101_alpha52(panel), expected52),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_batch05_warmups_are_not_cross_symbol_bleeding():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        sol = _series_from_long(out, fid, "SOLUSDT")
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        if warmup > 0:
            first_valid_pos = panel[panel["symbol"] == "SOLUSDT"].iloc[warmup]["timestamp"]
            assert sol.index.min() >= first_valid_pos
