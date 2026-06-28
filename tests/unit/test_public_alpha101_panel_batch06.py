"""Tests for public Alpha101 panel OHLCV/VWAP batch 06 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha47,
    compute_wq101_alpha61,
    compute_wq101_alpha65,
    compute_wq101_alpha68,
    compute_wq101_alpha74,
    compute_wq101_alpha75,
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
    "wq101_alpha47",
    "wq101_alpha61",
    "wq101_alpha65",
    "wq101_alpha68",
    "wq101_alpha74",
    "wq101_alpha75",
]


def _make_panel(n: int = 260) -> pd.DataFrame:
    timestamps = pd.date_range("2026-04-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 1.1
        close = pd.Series(90 + i * 3 + idx * 0.04 + np.sin(idx / 6 + phase) * (3.2 + i * 0.25))
        open_ = close.shift(1).fillna(close.iloc[0] - 0.2) + 0.06 * (i + 1)
        high = np.maximum(open_, close) + 1.1 + (idx % (4 + i)) * 0.06
        low = np.minimum(open_, close) - 0.8 - (idx % (5 + i)) * 0.05
        volume = pd.Series(1200 + i * 60 + idx * (1.3 + i * 0.25) + np.cos(idx / 5 + phase) * (170 + i * 20))
        vwap = close * (1 + np.sin(idx / 8 + phase) * (0.005 + i * 0.0003))
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


def test_batch06_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha47": (["high", "close", "volume", "quote_volume"], 20),
        "wq101_alpha61": (["volume", "quote_volume"], 197),
        "wq101_alpha65": (["open", "volume", "quote_volume"], 73),
        "wq101_alpha68": (["high", "low", "close", "volume"], 37),
        "wq101_alpha74": (["high", "close", "volume", "quote_volume"], 80),
        "wq101_alpha75": (["low", "volume", "quote_volume"], 61),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_panel_batch06_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)

    adv20 = rolling_mean_wide(volume, 20)
    part47 = xs_rank(1 / close) * (volume / adv20) * high * xs_rank(high - close)
    expected47 = (part47 / (rolling_sum_wide(high, 5) / 5)) - xs_rank(vwap - vwap.shift(5))

    adv180 = rolling_mean_wide(volume, 180)
    left61 = xs_rank(vwap - rolling_min_wide(vwap, 16))
    right61 = xs_rank(rolling_corr_wide(vwap, adv180, 18))
    expected61 = (left61 < right61).astype(float)
    expected61[left61.isna() | right61.isna()] = np.nan

    adv60 = rolling_mean_wide(volume, 60)
    blended65 = open_w * 0.00817205 + vwap * (1 - 0.00817205)
    left65 = xs_rank(rolling_corr_wide(blended65, rolling_sum_wide(adv60, 9), 6))
    right65 = xs_rank(open_w - rolling_min_wide(open_w, 14))
    expected65 = -1 * (left65 < right65).astype(float)
    expected65[left65.isna() | right65.isna()] = np.nan

    adv15 = rolling_mean_wide(volume, 15)
    left68 = ts_rank_wide(rolling_corr_wide(xs_rank(high), xs_rank(adv15), 9), 14)
    blended68 = close * 0.518371 + low * (1 - 0.518371)
    right68 = xs_rank(blended68 - blended68.shift(1))
    expected68 = -1 * (left68 < right68).astype(float)
    expected68[left68.isna() | right68.isna()] = np.nan

    adv30 = rolling_mean_wide(volume, 30)
    blended74 = high * 0.0261661 + vwap * (1 - 0.0261661)
    left74 = xs_rank(rolling_corr_wide(close, rolling_sum_wide(adv30, 37), 15))
    right74 = xs_rank(rolling_corr_wide(xs_rank(blended74), xs_rank(volume), 11))
    expected74 = -1 * (left74 < right74).astype(float)
    expected74[left74.isna() | right74.isna()] = np.nan

    adv50 = rolling_mean_wide(volume, 50)
    left75 = xs_rank(rolling_corr_wide(vwap, volume, 4))
    right75 = xs_rank(rolling_corr_wide(xs_rank(low), xs_rank(adv50), 12))
    expected75 = (left75 < right75).astype(float)
    expected75[left75.isna() | right75.isna()] = np.nan

    outputs = {
        "wq101_alpha47": (compute_wq101_alpha47(panel), expected47),
        "wq101_alpha61": (compute_wq101_alpha61(panel), expected61),
        "wq101_alpha65": (compute_wq101_alpha65(panel), expected65),
        "wq101_alpha68": (compute_wq101_alpha68(panel), expected68),
        "wq101_alpha74": (compute_wq101_alpha74(panel), expected74),
        "wq101_alpha75": (compute_wq101_alpha75(panel), expected75),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_boolean_factors_emit_only_discrete_values():
    panel = _make_panel()
    expected_values = {
        "wq101_alpha61": {0.0, 1.0},
        "wq101_alpha65": {-1.0, 0.0},
        "wq101_alpha68": {-1.0, 0.0},
        "wq101_alpha74": {-1.0, 0.0},
        "wq101_alpha75": {0.0, 1.0},
    }
    for fid, values in expected_values.items():
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        assert set(out[fid].dropna().unique()) <= values


def test_batch06_warmups_are_not_cross_symbol_bleeding():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        if eth.empty:
            continue
        warmup = REGISTRY_BY_ID[fid].lookback_window - 1
        if warmup > 0:
            first_valid_pos = panel[panel["symbol"] == "ETHUSDT"].iloc[warmup]["timestamp"]
            assert eth.index.min() >= first_valid_pos
