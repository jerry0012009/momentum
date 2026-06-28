"""Tests for public Alpha101 early OHLCV/VWAP panel batch 09 factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from alpha101_panel_ops import (  # noqa: E402
    compute_wq101_alpha14,
    compute_wq101_alpha15,
    compute_wq101_alpha16,
    compute_wq101_alpha17,
    compute_wq101_alpha18,
    compute_wq101_alpha19,
    compute_wq101_alpha20,
    compute_wq101_alpha22,
    compute_wq101_alpha26,
    compute_wq101_alpha27,
    rolling_corr_wide,
    rolling_cov_wide,
    rolling_max_wide,
    rolling_mean_wide,
    rolling_std_wide,
    rolling_sum_wide,
    to_wide,
    ts_rank_wide,
    xs_rank,
)
from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402

BATCH = [
    "wq101_alpha14",
    "wq101_alpha15",
    "wq101_alpha16",
    "wq101_alpha17",
    "wq101_alpha18",
    "wq101_alpha19",
    "wq101_alpha20",
    "wq101_alpha22",
    "wq101_alpha26",
    "wq101_alpha27",
]


def _make_panel(n: int = 300) -> pd.DataFrame:
    timestamps = pd.date_range("2026-06-01", periods=n, freq="h", tz="UTC")
    frames = []
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]):
        idx = np.arange(n, dtype=float)
        phase = i * 0.65
        close = pd.Series(
            80
            + i * 9
            + idx * (0.035 + i * 0.005)
            + np.sin(idx / (8.0 + i * 0.2) + phase) * (2.5 + i * 0.25)
            + np.cos(idx / 19 + phase) * 0.7
        )
        open_ = close.shift(1).fillna(close.iloc[0] - 0.25) + np.cos(idx / 10 + phase) * 0.2
        high = np.maximum(open_, close) + 0.75 + (idx % (4 + i)) * 0.05
        low = np.minimum(open_, close) - 0.65 - (idx % (5 + i)) * 0.04
        volume = pd.Series(
            1600
            + i * 130
            + idx * (2.0 + i * 0.35)
            + np.cos(idx / 6 + phase) * (220 + i * 25)
            + (idx % (6 + i)) * 16
        )
        vwap = close * (1 + np.sin(idx / 9 + phase) * (0.0055 + i * 0.0004))
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


def test_batch09_specs_registered_with_expected_metadata():
    expected = {
        "wq101_alpha14": (["open", "close", "volume"], 10),
        "wq101_alpha15": (["high", "volume"], 5),
        "wq101_alpha16": (["high", "volume"], 5),
        "wq101_alpha17": (["close", "volume"], 24),
        "wq101_alpha18": (["open", "close"], 10),
        "wq101_alpha19": (["close"], 251),
        "wq101_alpha20": (["open", "high", "low", "close"], 2),
        "wq101_alpha22": (["high", "close", "volume"], 20),
        "wq101_alpha26": (["high", "volume"], 11),
        "wq101_alpha27": (["volume", "quote_volume"], 7),
    }
    for fid, (columns, lookback) in expected.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == "wq101"
        assert spec.required_columns == columns
        assert spec.lookback_window == lookback
        assert spec.expected_direction == "conditional"
        assert spec.compute_scope == "panel"
        assert spec.panel_compute_fn is not None


def test_panel_batch09_formulas_match_wide_reference():
    panel = _make_panel()
    open_w = to_wide(panel, "open")
    close = to_wide(panel, "close")
    high = to_wide(panel, "high")
    low = to_wide(panel, "low")
    volume = to_wide(panel, "volume")
    vwap = _wide_vwap(panel)
    returns = close / close.shift(1) - 1.0

    expected14 = -1 * xs_rank(returns - returns.shift(3)) * rolling_corr_wide(open_w, volume, 10)

    corr15 = rolling_corr_wide(xs_rank(high), xs_rank(volume), 3)
    expected15 = -1 * rolling_sum_wide(xs_rank(corr15), 3)

    expected16 = -1 * xs_rank(rolling_cov_wide(xs_rank(high), xs_rank(volume), 5))

    close_delta = close - close.shift(1)
    adv20 = rolling_mean_wide(volume, 20)
    expected17 = (
        -1
        * xs_rank(ts_rank_wide(close, 10))
        * xs_rank(close_delta - close_delta.shift(1))
        * xs_rank(ts_rank_wide(volume / adv20.replace(0, np.nan), 5))
    )

    spread = close - open_w
    expected18 = -1 * xs_rank(rolling_std_wide(spread.abs(), 5) + spread + rolling_corr_wide(close, open_w, 10))

    close_delta7 = close - close.shift(7)
    expected19 = (-1 * np.sign(close_delta7 + close_delta7)) * (1 + xs_rank(1 + rolling_sum_wide(returns, 250)))

    expected20 = -1 * xs_rank(open_w - high.shift(1)) * xs_rank(open_w - close.shift(1)) * xs_rank(open_w - low.shift(1))

    corr22 = rolling_corr_wide(high, volume, 5)
    expected22 = -1 * (corr22 - corr22.shift(5)) * xs_rank(rolling_std_wide(close, 20))

    corr26 = rolling_corr_wide(ts_rank_wide(volume, 5), ts_rank_wide(high, 5), 5)
    expected26 = -1 * rolling_max_wide(corr26, 3)

    raw27 = rolling_sum_wide(rolling_corr_wide(xs_rank(volume), xs_rank(vwap), 6), 2) / 2.0
    ranked27 = xs_rank(raw27)
    expected27 = pd.DataFrame(np.nan, index=ranked27.index, columns=ranked27.columns, dtype=float)
    expected27[ranked27.notna() & (ranked27 > 0.5)] = -1.0
    expected27[ranked27.notna() & (ranked27 <= 0.5)] = 1.0

    outputs = {
        "wq101_alpha14": (compute_wq101_alpha14(panel), expected14),
        "wq101_alpha15": (compute_wq101_alpha15(panel), expected15),
        "wq101_alpha16": (compute_wq101_alpha16(panel), expected16),
        "wq101_alpha17": (compute_wq101_alpha17(panel), expected17),
        "wq101_alpha18": (compute_wq101_alpha18(panel), expected18),
        "wq101_alpha19": (compute_wq101_alpha19(panel), expected19),
        "wq101_alpha20": (compute_wq101_alpha20(panel), expected20),
        "wq101_alpha22": (compute_wq101_alpha22(panel), expected22),
        "wq101_alpha26": (compute_wq101_alpha26(panel), expected26),
        "wq101_alpha27": (compute_wq101_alpha27(panel), expected27),
    }
    for fid, (actual_long, expected_wide) in outputs.items():
        actual = _series_from_long(actual_long, fid, "BTCUSDT")
        expected = expected_wide["BTCUSDT"].dropna()
        pd.testing.assert_series_equal(actual, expected, check_names=False)


def test_alpha27_emits_only_discrete_gate_values():
    panel = _make_panel()
    out = compute_wq101_alpha27(panel)
    assert set(out["wq101_alpha27"].dropna().unique()) <= {-1.0, 1.0}


def test_batch09_outputs_stay_on_source_symbol_timestamps():
    panel = _make_panel()
    for fid in BATCH:
        out = REGISTRY_BY_ID[fid].panel_compute_fn(panel)
        eth = _series_from_long(out, fid, "ETHUSDT")
        if eth.empty:
            continue
        eth_source = panel[panel["symbol"] == "ETHUSDT"]["timestamp"]
        assert set(eth.index) <= set(eth_source)
        assert eth.index.min() >= eth_source.min()
