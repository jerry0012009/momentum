"""Tests for public Alpha101 early OHLCV/VWAP panel batch 08 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha1,
    compute_wq101_alpha2,
    compute_wq101_alpha3,
    compute_wq101_alpha4,
    compute_wq101_alpha5,
    compute_wq101_alpha7,
    compute_wq101_alpha8,
    compute_wq101_alpha10,
    compute_wq101_alpha11,
    compute_wq101_alpha13,
    rolling_cov_wide,
    rolling_corr_wide,
    rolling_idxmax_wide,
    rolling_max_wide,
    rolling_mean_wide,
    rolling_min_wide,
    rolling_std_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha1",
    "wq101_alpha2",
    "wq101_alpha3",
    "wq101_alpha4",
    "wq101_alpha5",
    "wq101_alpha7",
    "wq101_alpha8",
    "wq101_alpha10",
    "wq101_alpha11",
    "wq101_alpha13",
]


def _make_panel(n: int = 120) -> pd.DataFrame:
    timestamps = pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 0.75
        close = pd.Series(
            90
            + i * 7
            + idx * (0.045 + i * 0.006)
            + np.sin(idx / (6.5 + i * 0.3) + phase) * (2.3 + i * 0.25)
        )
        open_ = close.shift(1).fillna(close.iloc[0] - 0.2) + np.cos(idx / 9 + phase) * 0.22
        high = np.maximum(open_, close) + 0.8 + (idx % (4 + i)) * 0.06
        low = np.minimum(open_, close) - 0.6 - (idx % (5 + i)) * 0.05
        volume = pd.Series(
            1800
            + i * 140
            + idx * (2.1 + i * 0.4)
            + np.cos(idx / 5.5 + phase) * (260 + i * 30)
            + (idx % (7 + i)) * 18
        )
        vwap = close * (1 + np.sin(idx / 8 + phase) * (0.005 + i * 0.0005))
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


def _wide_vwap(panel: pd.DataFrame) -> pd.DataFrame:
    work = panel.copy()
    work["_vwap"] = work["quote_volume"] / work["volume"]
    return to_wide(work, "_vwap")


def test_batch08_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha1": (["close"], 25),
        "wq101_alpha2": (["open", "close", "volume"], 8),
        "wq101_alpha3": (["open", "volume"], 10),
        "wq101_alpha4": (["low"], 9),
        "wq101_alpha5": (["open", "close", "volume", "quote_volume"], 10),
        "wq101_alpha7": (["close", "volume"], 67),
        "wq101_alpha8": (["open", "close"], 15),
        "wq101_alpha10": (["close"], 5),
        "wq101_alpha11": (["close", "volume", "quote_volume"], 4),
        "wq101_alpha13": (["close", "volume"], 5),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_rolling_idxmax_wide_returns_bars_since_latest_max():
    wide = pd.DataFrame({"A": [1.0, 4.0, 2.0, 4.0], "B": [3.0, 2.0, 1.0, 0.0]})
    out = rolling_idxmax_wide(wide, 4)
    assert out["A"].iloc[-1] == 0
    assert out["B"].iloc[-1] == 3


def test_rolling_cov_wide_matches_pandas_reference():
    x = pd.DataFrame({"A": [1.0, 2.0, 4.0, 8.0]})
    y = pd.DataFrame({"A": [2.0, 1.0, 3.0, 5.0]})
    out = rolling_cov_wide(x, y, 3)
    expected = x["A"].rolling(3, min_periods=3).cov(y["A"])
    pd.testing.assert_series_equal(out["A"], expected, check_names=False)


def test_panel_batch08_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)
    returns = close / close.shift(1) - 1.0

    volatility = rolling_std_wide(returns, 20)
    base = close.where(returns >= 0, volatility)
    powered = np.sign(base) * (base.abs() ** 2)
    expected1 = xs_rank(rolling_idxmax_wide(powered, 5)) - 0.5

    log_volume = np.log(volume.replace(0, np.nan))
    intrabar_return = (close - open_w) / open_w.replace(0, np.nan)
    expected2 = -1 * rolling_corr_wide(xs_rank(log_volume - log_volume.shift(2)), xs_rank(intrabar_return), 6)

    expected3 = -1 * rolling_corr_wide(xs_rank(open_w), xs_rank(volume), 10)
    expected4 = -1 * ts_rank_wide(xs_rank(low), 9)
    expected5 = xs_rank(open_w - rolling_sum_wide(vwap, 10) / 10) * (-1 * xs_rank(close - vwap).abs())

    adv20 = rolling_mean_wide(volume, 20)
    close_delta7 = close - close.shift(7)
    active = adv20 < volume
    branch7 = -1 * ts_rank_wide(close_delta7.abs(), 60) * np.sign(close_delta7)
    expected7 = pd.DataFrame(np.nan, index=close.index, columns=close.columns, dtype=float)
    expected7[active] = branch7[active]
    expected7[~active & adv20.notna() & volume.notna()] = -1.0

    raw8 = rolling_sum_wide(open_w, 5) * rolling_sum_wide(returns, 5)
    expected8 = -1 * xs_rank(raw8 - raw8.shift(10))

    close_delta1 = close - close.shift(1)
    min_delta = rolling_min_wide(close_delta1, 4)
    max_delta = rolling_max_wide(close_delta1, 4)
    valid10 = min_delta.notna() & max_delta.notna()
    trend_agrees = (min_delta > 0) | (max_delta < 0)
    raw10 = pd.DataFrame(np.nan, index=close.index, columns=close.columns, dtype=float)
    raw10[valid10 & trend_agrees] = close_delta1[valid10 & trend_agrees]
    raw10[valid10 & ~trend_agrees] = -close_delta1[valid10 & ~trend_agrees]
    expected10 = xs_rank(raw10)

    spread = vwap - close
    expected11 = (xs_rank(rolling_max_wide(spread, 3)) + xs_rank(rolling_min_wide(spread, 3))) * xs_rank(volume - volume.shift(3))
    expected13 = -1 * xs_rank(rolling_cov_wide(xs_rank(close), xs_rank(volume), 5))

    outputs = {
        "wq101_alpha1": (compute_wq101_alpha1(panel), expected1),
        "wq101_alpha2": (compute_wq101_alpha2(panel), expected2),
        "wq101_alpha3": (compute_wq101_alpha3(panel), expected3),
        "wq101_alpha4": (compute_wq101_alpha4(panel), expected4),
        "wq101_alpha5": (compute_wq101_alpha5(panel), expected5),
        "wq101_alpha7": (compute_wq101_alpha7(panel), expected7),
        "wq101_alpha8": (compute_wq101_alpha8(panel), expected8),
        "wq101_alpha10": (compute_wq101_alpha10(panel), expected10),
        "wq101_alpha11": (compute_wq101_alpha11(panel), expected11),
        "wq101_alpha13": (compute_wq101_alpha13(panel), expected13),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_alpha7_emits_minus_one_for_inactive_relative_volume_gate():
    panel = _make_panel(80)
    panel["volume"] = 1000.0
    panel["quote_volume"] = panel["volume"] * panel["close"]
    out = compute_wq101_alpha7(panel)
    values = out["wq101_alpha7"].dropna().unique()
    assert set(values) == {-1.0}


def test_batch08_warmups_are_not_cross_symbol_bleeding():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        if eth.empty:
            continue
        eth_source = panel[panel["symbol"] == "ETHUSDT"]["timestamp"]
        assert set(eth.index) <= set(eth_source)
        assert eth.index.min() >= eth_source.min()
