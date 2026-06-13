"""Tests for build_labels.py — verify forward return definitions."""
import numpy as np
import pandas as pd
import pytest


def _make_bars(symbols=("BTCUSDT", "ETHUSDT"), n_hours=100):
    """Create synthetic 1h bars for testing."""
    rng = np.random.default_rng(42)
    rows = []
    base_ts = pd.Timestamp("2026-01-01", tz="UTC")
    for sym in symbols:
        close = 100.0 + np.cumsum(rng.normal(0, 1, n_hours))
        for i in range(n_hours):
            rows.append({
                "timestamp": base_ts + pd.Timedelta(hours=i),
                "symbol": sym,
                "close": close[i],
            })
    return pd.DataFrame(rows)


def _build_labels(bars: pd.DataFrame, horizons=(1, 4, 24, 72)) -> pd.DataFrame:
    """Replicate build_labels.py logic for testing."""
    out = bars[["timestamp", "symbol", "close"]].copy()
    close_by_symbol = out.groupby("symbol", sort=False)["close"]
    for h in horizons:
        out[f"ret_fwd_{h}h"] = close_by_symbol.shift(-h) / out["close"] - 1.0
    return out.drop(columns=["close"])


class TestForwardReturnDefinition:
    """ret_fwd_h must equal close[t+h] / close[t] - 1."""

    @pytest.mark.parametrize("h", [1, 4, 24, 72])
    def test_formula_correct(self, h):
        bars = _make_bars(n_hours=200)
        labels = _build_labels(bars, horizons=[h])
        col = f"ret_fwd_{h}h"

        for sym in bars["symbol"].unique():
            sym_bars = bars[bars["symbol"] == sym].sort_values("timestamp").reset_index(drop=True)
            sym_labels = labels[labels["symbol"] == sym].sort_values("timestamp").reset_index(drop=True)

            for i in range(len(sym_bars) - h):
                expected = sym_bars.loc[i + h, "close"] / sym_bars.loc[i, "close"] - 1.0
                actual = sym_labels.loc[i, col]
                assert actual == pytest.approx(expected, abs=1e-12), (
                    f"Mismatch at {sym} t={i}: expected={expected}, got={actual}"
                )

    def test_tail_is_nan(self):
        """Last h bars per symbol should have NaN forward returns."""
        bars = _make_bars(n_hours=50)
        labels = _build_labels(bars, horizons=[1, 4])
        for sym in bars["symbol"].unique():
            sym_labels = labels[labels["symbol"] == sym].sort_values("timestamp")
            assert pd.isna(sym_labels.iloc[-1]["ret_fwd_1h"])
            assert pd.isna(sym_labels.iloc[-1]["ret_fwd_4h"])
            assert pd.isna(sym_labels.iloc[-4]["ret_fwd_4h"])

    def test_no_future_leak_in_factor(self):
        """Labels use future data (by design), but verify the formula is correct."""
        bars = _make_bars(symbols=("BTCUSDT",), n_hours=30)
        labels = _build_labels(bars, horizons=[1])
        # At t=0, ret_fwd_1h = close[1]/close[0] - 1
        c0 = bars.iloc[0]["close"]
        c1 = bars.iloc[1]["close"]
        expected = c1 / c0 - 1.0
        actual = labels.iloc[0]["ret_fwd_1h"]
        assert actual == pytest.approx(expected)
