"""Tests for public Alpha101 OHLCV/VWAP/ADV panel batch 10 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha29,
    compute_wq101_alpha31,
    compute_wq101_alpha36,
    compute_wq101_alpha39,
    compute_wq101_alpha57,
    compute_wq101_alpha62,
    compute_wq101_alpha64,
    compute_wq101_alpha66,
    compute_wq101_alpha71,
    compute_wq101_alpha72,
    decay_linear_wide,
    rolling_corr_wide,
    rolling_idxmax_wide,
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
    "wq101_alpha29",
    "wq101_alpha31",
    "wq101_alpha36",
    "wq101_alpha39",
    "wq101_alpha57",
    "wq101_alpha62",
    "wq101_alpha64",
    "wq101_alpha66",
    "wq101_alpha71",
    "wq101_alpha72",
]


def _make_panel(n: int = 340) -> pd.DataFrame:
    timestamps = pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 0.73
        close = pd.Series(
            70
            + i * 11
            + idx * (0.028 + i * 0.004)
            + np.sin(idx / (8.5 + i * 0.3) + phase) * (2.9 + i * 0.25)
            + np.cos(idx / 23 + phase) * 0.9
        )
        open_ = close.shift(1).fillna(close.iloc[0] - 0.35) + np.cos(idx / 12 + phase) * 0.22
        high = np.maximum(open_, close) + 0.85 + (idx % (5 + i)) * 0.045
        low = np.minimum(open_, close) - 0.72 - (idx % (6 + i)) * 0.035
        volume = pd.Series(
            1400
            + i * 145
            + idx * (2.2 + i * 0.4)
            + np.cos(idx / 6.5 + phase) * (210 + i * 25)
            + (idx % (7 + i)) * 15
        )
        vwap = close * (1 + np.sin(idx / 10 + phase) * (0.005 + i * 0.0005))
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


def _max_wide(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
    left, right = left.align(right, join="inner", axis=None)
    result = left.where(left >= right, right)
    result[left.isna() | right.isna()] = np.nan
    return result


def test_batch10_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha29": (["close"], 11),
        "wq101_alpha31": (["close", "low", "volume"], 31),
        "wq101_alpha36": (["open", "close", "volume", "quote_volume"], 200),
        "wq101_alpha39": (["close", "volume"], 251),
        "wq101_alpha57": (["close", "volume", "quote_volume"], 31),
        "wq101_alpha62": (["open", "high", "low", "volume", "quote_volume"], 51),
        "wq101_alpha64": (["open", "high", "low", "volume", "quote_volume"], 149),
        "wq101_alpha66": (["open", "high", "low", "volume", "quote_volume"], 17),
        "wq101_alpha71": (["open", "low", "close", "volume", "quote_volume"], 229),
        "wq101_alpha72": (["high", "low", "volume", "quote_volume"], 49),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_panel_batch10_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)
    returns = close / close.shift(1) - 1.0

    ranked_delta29 = xs_rank(xs_rank(-1 * xs_rank(close - close.shift(5))))
    expected29 = (
        rolling_min_wide(xs_rank(xs_rank(xs_scale(np.log(rolling_min_wide(ranked_delta29, 2).replace(0, np.nan))))), 5)
        + ts_rank_wide((-1 * returns).shift(6), 5)
    )

    expected31 = (
        xs_rank(xs_rank(xs_rank(decay_linear_wide(-1 * xs_rank(xs_rank(close - close.shift(10))), 10))))
        + xs_rank(-1 * (close - close.shift(3)))
        + np.sign(xs_scale(rolling_corr_wide(rolling_mean_wide(volume, 20), low, 12)))
    )

    adv20 = rolling_mean_wide(volume, 20)
    expected36 = (
        2.21 * xs_rank(rolling_corr_wide(close - open_w, volume.shift(1), 15))
        + 0.7 * xs_rank(open_w - close)
        + 0.73 * xs_rank(ts_rank_wide((-1 * returns).shift(6), 5))
        + xs_rank(rolling_corr_wide(vwap, adv20, 6).abs())
        + 0.6 * xs_rank((rolling_sum_wide(close, 200) / 200 - open_w) * (close - open_w))
    )

    rel_vol_decay = decay_linear_wide(volume / adv20.replace(0, np.nan), 9)
    expected39 = (
        -1
        * xs_rank((close - close.shift(7)) * (1 - xs_rank(rel_vol_decay)))
        * (1 + xs_rank(rolling_sum_wide(returns, 250)))
    )

    expected57 = -1 * (close - vwap) / decay_linear_wide(xs_rank(rolling_idxmax_wide(close, 30)), 2).replace(0, np.nan)

    left62 = xs_rank(rolling_corr_wide(vwap, rolling_sum_wide(adv20, 22), 10))
    condition62 = ((xs_rank(open_w) + xs_rank(open_w)) < (xs_rank((high + low) / 2) + xs_rank(high))).astype(float)
    condition62[open_w.isna() | high.isna() | low.isna()] = np.nan
    right62 = xs_rank(condition62)
    expected62 = -1 * (left62 < right62).astype(float)
    expected62[left62.isna() | right62.isna()] = np.nan

    adv120 = rolling_mean_wide(volume, 120)
    blend64_left = open_w * 0.178404 + low * (1 - 0.178404)
    left64 = xs_rank(rolling_corr_wide(rolling_sum_wide(blend64_left, 13), rolling_sum_wide(adv120, 13), 17))
    blend64_right = ((high + low) / 2) * 0.178404 + vwap * (1 - 0.178404)
    right64 = xs_rank(blend64_right - blend64_right.shift(4))
    expected64 = -1 * (left64 < right64).astype(float)
    expected64[left64.isna() | right64.isna()] = np.nan

    left66 = xs_rank(decay_linear_wide(vwap - vwap.shift(4), 7))
    right66 = ts_rank_wide(decay_linear_wide((low - vwap) / (open_w - ((high + low) / 2)).replace(0, np.nan), 11), 7)
    expected66 = -1 * (left66 + right66)
    expected66[left66.isna() | right66.isna()] = np.nan

    adv180 = rolling_mean_wide(volume, 180)
    left71 = ts_rank_wide(
        decay_linear_wide(rolling_corr_wide(ts_rank_wide(close, 3), ts_rank_wide(adv180, 12), 18), 4),
        16,
    )
    right71 = ts_rank_wide(decay_linear_wide(xs_rank((low + open_w) - (vwap + vwap)).pow(2), 16), 4)
    expected71 = _max_wide(left71, right71)

    adv40 = rolling_mean_wide(volume, 40)
    left72 = xs_rank(decay_linear_wide(rolling_corr_wide((high + low) / 2, adv40, 9), 10))
    right72 = xs_rank(decay_linear_wide(rolling_corr_wide(ts_rank_wide(vwap, 4), ts_rank_wide(volume, 19), 7), 3))
    expected72 = left72 / right72.replace(0, np.nan)
    expected72[left72.isna() | right72.isna()] = np.nan

    outputs = {
        "wq101_alpha29": (compute_wq101_alpha29(panel), expected29),
        "wq101_alpha31": (compute_wq101_alpha31(panel), expected31),
        "wq101_alpha36": (compute_wq101_alpha36(panel), expected36),
        "wq101_alpha39": (compute_wq101_alpha39(panel), expected39),
        "wq101_alpha57": (compute_wq101_alpha57(panel), expected57),
        "wq101_alpha62": (compute_wq101_alpha62(panel), expected62),
        "wq101_alpha64": (compute_wq101_alpha64(panel), expected64),
        "wq101_alpha66": (compute_wq101_alpha66(panel), expected66),
        "wq101_alpha71": (compute_wq101_alpha71(panel), expected71),
        "wq101_alpha72": (compute_wq101_alpha72(panel), expected72),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_boolean_batch10_factors_emit_discrete_gate_values():
    panel = _make_panel()
    for fid in ["wq101_alpha62", "wq101_alpha64"]:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        assert set(out[fid].dropna().unique()) <= {-1.0, 0.0}


def test_batch10_outputs_stay_on_source_symbol_timestamps():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        if eth.empty:
            continue
        eth_source = panel[panel["symbol"] == "ETHUSDT"]["timestamp"]
        assert set(eth.index) <= set(eth_source)
        assert eth.index.min() >= eth_source.min()
