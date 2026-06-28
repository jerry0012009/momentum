"""Tests for public Alpha101 panel OHLCV/VWAP batch 03 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha32,
    compute_wq101_alpha33,
    compute_wq101_alpha37,
    compute_wq101_alpha38,
    compute_wq101_alpha44,
    compute_wq101_alpha45,
    rolling_corr_wide,
    rolling_mean_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
    xs_scale,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402
from build_factor_values import combine_factor_parts  # noqa: E402

BATCH = [
    "wq101_alpha32",
    "wq101_alpha33",
    "wq101_alpha37",
    "wq101_alpha38",
    "wq101_alpha44",
    "wq101_alpha45",
]


def _make_panel(n: int = 260) -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT"]):
        idx = np.arange(n, dtype=float)
        close = pd.Series(100 + i * 25 + idx * (0.08 + i * 0.01) + np.sin(idx / (6 + i)) * (1.5 + i))
        open_ = close.shift(1).fillna(close.iloc[0] - 0.3) + 0.15 * (i + 1)
        high = np.maximum(open_, close) + 1.2 + (idx % (3 + i)) * 0.07
        low = np.minimum(open_, close) - 1.1 - (idx % (4 + i)) * 0.05
        volume = pd.Series(1000 + i * 350 + idx * (2 + i) + (idx % (5 + i)) * 19)
        vwap = close * (1 + np.sin(idx / (9 + i)) * 0.001)
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
        "wq101_alpha32": (["close", "volume", "quote_volume"], 235),
        "wq101_alpha33": (["open", "close"], 1),
        "wq101_alpha37": (["open", "close"], 201),
        "wq101_alpha38": (["open", "close"], 10),
        "wq101_alpha44": (["high", "volume"], 5),
        "wq101_alpha45": (["close", "volume"], 25),
    }

    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_alpha33_uses_cross_sectional_rank_per_timestamp():
    panel = pd.DataFrame({
        "timestamp": pd.to_datetime(["2026-01-01"] * 3, utc=True),
        "symbol": ["A", "B", "C"],
        "open": [9.0, 10.0, 12.0],
        "close": [10.0, 10.0, 10.0],
        "high": [10.5, 11.0, 12.5],
        "low": [8.5, 9.5, 9.8],
        "volume": [100.0, 200.0, 300.0],
        "quote_volume": [950.0, 2000.0, 3300.0],
    })
    out = compute_wq101_alpha33(panel).sort_values("symbol")
    assert out["wq101_alpha33"].tolist() == [1 / 3, 2 / 3, 1.0]


def test_panel_batch_formulas_match_wide_reference():
    panel = _make_panel()
    close = to_wide(panel, "close")
    open_w = to_wide(panel, "open")
    high = to_wide(panel, "high")
    volume = to_wide(panel, "volume")
    vwap_panel = panel.copy()
    vwap_panel["_vwap"] = vwap_panel["quote_volume"] / vwap_panel["volume"]
    vwap = to_wide(vwap_panel, "_vwap")

    expected32 = xs_scale(rolling_mean_wide(close, 7) - close) + 20 * xs_scale(rolling_corr_wide(vwap, close.shift(5), 230))
    expected37 = xs_rank(rolling_corr_wide((open_w - close).shift(1), close, 200)) + xs_rank(open_w - close)
    expected38 = -1 * xs_rank(ts_rank_wide(close, 10)) * xs_rank(close / open_w)
    expected44 = -1 * rolling_corr_wide(high, xs_rank(volume), 5)
    expected45 = -1 * (
        xs_rank(rolling_mean_wide(close.shift(5), 20))
        * rolling_corr_wide(close, volume, 2)
        * xs_rank(rolling_corr_wide(rolling_sum_wide(close, 5), rolling_sum_wide(close, 20), 2))
    )

    outputs = {
        "wq101_alpha32": (compute_wq101_alpha32(panel), expected32),
        "wq101_alpha37": (compute_wq101_alpha37(panel), expected37),
        "wq101_alpha38": (compute_wq101_alpha38(panel), expected38),
        "wq101_alpha44": (compute_wq101_alpha44(panel), expected44),
        "wq101_alpha45": (compute_wq101_alpha45(panel), expected45),
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


def test_combine_factor_parts_merges_panel_outputs_by_key():
    ts = pd.to_datetime(["2026-01-01", "2026-01-02"], utc=True)
    part_a = pd.DataFrame({
        "timestamp": ts,
        "symbol": ["BTCUSDT", "BTCUSDT"],
        "wq101_alpha33": [0.5, 1.0],
    })
    part_b = pd.DataFrame({
        "timestamp": ts,
        "symbol": ["BTCUSDT", "BTCUSDT"],
        "wq101_alpha44": [-0.2, -0.1],
    })

    wide = combine_factor_parts([part_a, part_b])

    assert len(wide) == 2
    assert wide["wq101_alpha33"].tolist() == [0.5, 1.0]
    assert wide["wq101_alpha44"].tolist() == [-0.2, -0.1]
