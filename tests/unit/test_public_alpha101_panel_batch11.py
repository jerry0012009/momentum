"""Tests for public Alpha101 OHLCV/VWAP/ADV panel batch 11 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha73,
    compute_wq101_alpha81,
    compute_wq101_alpha84,
    compute_wq101_alpha98,
    decay_linear_wide,
    rolling_corr_wide,
    rolling_idxmin_wide,
    rolling_max_wide,
    rolling_mean_wide,
    rolling_product_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha73",
    "wq101_alpha81",
    "wq101_alpha84",
    "wq101_alpha98",
]


def _make_panel(n: int = 180) -> pd.DataFrame:
    timestamps = pd.date_range("2026-06-20", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 0.61
        close = pd.Series(
            85
            + i * 9
            + idx * (0.032 + i * 0.003)
            + np.sin(idx / (7.5 + i * 0.25) + phase) * (2.4 + i * 0.22)
            + np.cos(idx / 19 + phase) * 0.75
        )
        open_ = close.shift(1).fillna(close.iloc[0] - 0.28) + np.cos(idx / 10 + phase) * 0.18
        high = np.maximum(open_, close) + 0.72 + (idx % (5 + i)) * 0.038
        low = np.minimum(open_, close) - 0.64 - (idx % (6 + i)) * 0.031
        volume = pd.Series(
            1250
            + i * 135
            + idx * (2.0 + i * 0.35)
            + np.cos(idx / 6 + phase) * (185 + i * 22)
            + (idx % (7 + i)) * 13
        )
        vwap = close * (1 + np.sin(idx / 9 + phase) * (0.0045 + i * 0.0004))
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


def _signed_power_wide(base: pd.DataFrame, exponent: pd.DataFrame) -> pd.DataFrame:
    base, exponent = base.align(exponent, join="inner", axis=None)
    values = np.full(base.shape, np.nan, dtype=float)
    base_values = base.to_numpy(dtype=float)
    exp_values = exponent.to_numpy(dtype=float)
    valid = np.isfinite(base_values) & np.isfinite(exp_values) & ((base_values != 0) | (exp_values > 0))
    values[valid] = np.sign(base_values[valid]) * np.power(np.abs(base_values[valid]), exp_values[valid])
    return pd.DataFrame(values, index=base.index, columns=base.columns)


def test_batch11_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha73": (["open", "low", "volume", "quote_volume"], 26),
        "wq101_alpha81": (["volume", "quote_volume"], 82),
        "wq101_alpha84": (["close", "volume", "quote_volume"], 35),
        "wq101_alpha98": (["open", "volume", "quote_volume"], 55),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_panel_batch11_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)

    left73 = xs_rank(decay_linear_wide(vwap - vwap.shift(5), 3))
    blend73 = open_w * 0.147155 + low * (1 - 0.147155)
    right73 = ts_rank_wide(decay_linear_wide(((blend73 - blend73.shift(2)) / blend73.replace(0, np.nan)) * -1, 3), 17)
    expected73 = -1 * _max_wide(left73, right73)

    adv10 = rolling_mean_wide(volume, 10)
    corr81 = rolling_corr_wide(vwap, rolling_sum_wide(adv10, 50), 8)
    product81 = rolling_product_wide(xs_rank(xs_rank(corr81).pow(4)), 15)
    left81 = xs_rank(np.log(product81.replace(0, np.nan)))
    right81 = xs_rank(rolling_corr_wide(xs_rank(vwap), xs_rank(volume), 5))
    expected81 = -1 * (left81 < right81).astype(float)
    expected81[left81.isna() | right81.isna()] = np.nan

    expected84 = _signed_power_wide(
        ts_rank_wide(vwap - rolling_max_wide(vwap, 15), 21),
        close - close.shift(5),
    )

    adv5 = rolling_mean_wide(volume, 5)
    adv15 = rolling_mean_wide(volume, 15)
    left98 = xs_rank(decay_linear_wide(rolling_corr_wide(vwap, rolling_sum_wide(adv5, 26), 5), 7))
    right98_corr = rolling_corr_wide(xs_rank(open_w), xs_rank(adv15), 21)
    right98 = xs_rank(decay_linear_wide(ts_rank_wide(rolling_idxmin_wide(right98_corr, 9), 7), 8))
    expected98 = left98 - right98
    expected98[left98.isna() | right98.isna()] = np.nan

    outputs = {
        "wq101_alpha73": (compute_wq101_alpha73(panel), expected73),
        "wq101_alpha81": (compute_wq101_alpha81(panel), expected81),
        "wq101_alpha84": (compute_wq101_alpha84(panel), expected84),
        "wq101_alpha98": (compute_wq101_alpha98(panel), expected98),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_alpha81_boolean_gate_outputs_negative_or_zero_only():
    out = compute_wq101_alpha81(_make_panel())
    values = set(out["wq101_alpha81"].dropna().unique())
    assert values
    assert values <= {-1.0, 0.0}


def test_batch11_panel_computes_are_timestamp_isolated_by_symbol_order():
    panel = _make_panel()
    shuffled = panel.sort_values(["timestamp", "symbol"], ascending=[True, False]).reset_index(drop=True)
    for fid, compute in {
        "wq101_alpha73": compute_wq101_alpha73,
        "wq101_alpha81": compute_wq101_alpha81,
        "wq101_alpha84": compute_wq101_alpha84,
        "wq101_alpha98": compute_wq101_alpha98,
    }.items():
        base = compute(panel).sort_values(["timestamp", "symbol"]).reset_index(drop=True)
        alt = compute(shuffled).sort_values(["timestamp", "symbol"]).reset_index(drop=True)
        pd.testing.assert_frame_equal(base, alt)
