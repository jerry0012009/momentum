"""Tests for public Alpha101 panel OHLCV/VWAP/ADV decay batch 07 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha77,
    compute_wq101_alpha78,
    compute_wq101_alpha83,
    compute_wq101_alpha85,
    compute_wq101_alpha86,
    compute_wq101_alpha88,
    compute_wq101_alpha92,
    compute_wq101_alpha94,
    compute_wq101_alpha95,
    compute_wq101_alpha99,
    decay_linear_wide,
    rolling_corr_wide,
    rolling_mean_wide,
    rolling_min_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha77",
    "wq101_alpha78",
    "wq101_alpha83",
    "wq101_alpha85",
    "wq101_alpha86",
    "wq101_alpha88",
    "wq101_alpha92",
    "wq101_alpha94",
    "wq101_alpha95",
    "wq101_alpha99",
]


def _make_panel(n: int = 180) -> pd.DataFrame:
    timestamps = pd.date_range("2026-05-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 0.9
        close = pd.Series(100 + i * 4 + idx * (0.035 + i * 0.004) + np.sin(idx / 7 + phase) * (2.7 + i * 0.2))
        open_ = close.shift(1).fillna(close.iloc[0] - 0.3) + np.cos(idx / 11 + phase) * 0.15
        high = np.maximum(open_, close) + 0.9 + (idx % (5 + i)) * 0.05
        low = np.minimum(open_, close) - 0.7 - (idx % (6 + i)) * 0.04
        volume = pd.Series(1500 + i * 80 + idx * (1.6 + i * 0.3) + np.cos(idx / 6 + phase) * (190 + i * 15))
        vwap = close * (1 + np.sin(idx / 9 + phase) * (0.006 + i * 0.0004))
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


def _min_wide(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    left, right = left.align(right, join="inner", axis=None)
    result = left.where(left <= right, right)
    result[left.isna() | right.isna()] = np.nan
    return result


def test_batch07_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha77": (["high", "low", "volume", "quote_volume"], 47),
        "wq101_alpha78": (["low", "volume", "quote_volume"], 65),
        "wq101_alpha83": (["high", "low", "close", "volume", "quote_volume"], 7),
        "wq101_alpha85": (["high", "low", "close", "volume"], 39),
        "wq101_alpha86": (["open", "close", "volume", "quote_volume"], 58),
        "wq101_alpha88": (["open", "high", "low", "close", "volume"], 95),
        "wq101_alpha92": (["open", "high", "low", "close", "volume"], 49),
        "wq101_alpha94": (["volume", "quote_volume"], 82),
        "wq101_alpha95": (["open", "high", "low", "volume"], 81),
        "wq101_alpha99": (["high", "low", "volume"], 87),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_decay_linear_wide_uses_recent_highest_weight():
    wide = pd.DataFrame({"A": [1.0, 2.0, 4.0], "B": [2.0, 4.0, 8.0]})
    out = decay_linear_wide(wide, 3)
    assert np.isclose(out["A"].iloc[-1], (1 * 1 + 2 * 2 + 4 * 3) / 6)
    assert np.isclose(out["B"].iloc[-1], (2 * 1 + 4 * 2 + 8 * 3) / 6)


def test_panel_batch07_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)
    mid = (high + low) / 2

    adv40 = rolling_mean_wide(volume, 40)
    expected77 = _min_wide(
        xs_rank(decay_linear_wide((mid + high) - (vwap + high), 20)),
        xs_rank(decay_linear_wide(rolling_corr_wide(mid, adv40, 3), 6)),
    )

    blend78 = low * 0.352233 + vwap * (1 - 0.352233)
    left78 = xs_rank(rolling_corr_wide(rolling_sum_wide(blend78, 20), rolling_sum_wide(adv40, 20), 7))
    right78 = xs_rank(rolling_corr_wide(xs_rank(vwap), xs_rank(volume), 6))
    expected78 = left78.pow(right78)
    expected78[left78.isna() | right78.isna()] = np.nan

    range_scaled = (high - low) / (rolling_sum_wide(close, 5) / 5)
    expected83 = (xs_rank(range_scaled.shift(2)) * xs_rank(xs_rank(volume))) / (range_scaled / (vwap - close))

    adv30 = rolling_mean_wide(volume, 30)
    blend85 = high * 0.876703 + close * (1 - 0.876703)
    left85 = xs_rank(rolling_corr_wide(blend85, adv30, 10))
    right85 = xs_rank(rolling_corr_wide(ts_rank_wide(mid, 4), ts_rank_wide(volume, 10), 7))
    expected85 = left85.pow(right85)
    expected85[left85.isna() | right85.isna()] = np.nan

    adv20 = rolling_mean_wide(volume, 20)
    left86 = ts_rank_wide(rolling_corr_wide(close, rolling_sum_wide(adv20, 15), 6), 20)
    right86 = xs_rank(close - vwap)
    expected86 = -1 * (left86 < right86).astype(float)
    expected86[left86.isna() | right86.isna()] = np.nan

    adv60 = rolling_mean_wide(volume, 60)
    left88 = xs_rank(decay_linear_wide((xs_rank(open_w) + xs_rank(low)) - (xs_rank(high) + xs_rank(close)), 8))
    right88 = ts_rank_wide(
        decay_linear_wide(rolling_corr_wide(ts_rank_wide(close, 8), ts_rank_wide(adv60, 21), 8), 7),
        3,
    )
    expected88 = _min_wide(left88, right88)

    cond92 = (mid + close < low + open_w).astype(float)
    cond92[open_w.isna() | close.isna() | high.isna() | low.isna()] = np.nan
    left92 = ts_rank_wide(decay_linear_wide(cond92, 15), 19)
    right92 = ts_rank_wide(decay_linear_wide(rolling_corr_wide(xs_rank(low), xs_rank(adv30), 8), 7), 7)
    expected92 = _min_wide(left92, right92)

    left94 = xs_rank(vwap - rolling_min_wide(vwap, 12))
    right94 = ts_rank_wide(rolling_corr_wide(ts_rank_wide(vwap, 20), ts_rank_wide(adv60, 4), 18), 3)
    expected94 = -1 * left94.pow(right94)
    expected94[left94.isna() | right94.isna()] = np.nan

    left95 = xs_rank(open_w - rolling_min_wide(open_w, 12))
    corr95 = rolling_corr_wide(rolling_sum_wide(mid, 19), rolling_sum_wide(adv40, 19), 13)
    right95 = ts_rank_wide(xs_rank(corr95).pow(5), 12)
    expected95 = (left95 < right95).astype(float)
    expected95[left95.isna() | right95.isna()] = np.nan

    left99 = xs_rank(rolling_corr_wide(rolling_sum_wide(mid, 20), rolling_sum_wide(adv60, 20), 9))
    right99 = xs_rank(rolling_corr_wide(low, volume, 6))
    expected99 = -1 * (left99 < right99).astype(float)
    expected99[left99.isna() | right99.isna()] = np.nan

    outputs = {
        "wq101_alpha77": (compute_wq101_alpha77(panel), expected77),
        "wq101_alpha78": (compute_wq101_alpha78(panel), expected78),
        "wq101_alpha83": (compute_wq101_alpha83(panel), expected83),
        "wq101_alpha85": (compute_wq101_alpha85(panel), expected85),
        "wq101_alpha86": (compute_wq101_alpha86(panel), expected86),
        "wq101_alpha88": (compute_wq101_alpha88(panel), expected88),
        "wq101_alpha92": (compute_wq101_alpha92(panel), expected92),
        "wq101_alpha94": (compute_wq101_alpha94(panel), expected94),
        "wq101_alpha95": (compute_wq101_alpha95(panel), expected95),
        "wq101_alpha99": (compute_wq101_alpha99(panel), expected99),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_boolean_factors_emit_only_discrete_values():
    panel = _make_panel()
    expected_values = {
        "wq101_alpha86": {-1.0, 0.0},
        "wq101_alpha95": {0.0, 1.0},
        "wq101_alpha99": {-1.0, 0.0},
    }
    for fid, values in expected_values.items():
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        assert set(out[fid].dropna().unique()) <= values


def test_batch07_warmups_are_not_cross_symbol_bleeding():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        if eth.empty:
            continue
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        first_valid_pos = panel[panel["symbol"] == "ETHUSDT"].iloc[warmup]["timestamp"]
        assert eth.index.min() >= first_valid_pos
