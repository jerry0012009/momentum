"""Tests for quantile_spread module using toy data."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.quantile_spread import (
    compute_quantile_spread, summarize_quantile_spread,
)


def _make_spread_data(direction="positive"):
    """Create toy data where top bucket outperforms bottom."""
    n = 100
    ts = pd.Timestamp("2025-01-01")
    rng = np.random.default_rng(42)

    signal_vals = rng.uniform(0, 1, n)
    if direction == "positive":
        return_vals = signal_vals * 0.1 + rng.normal(0, 0.01, n)
    else:
        return_vals = -signal_vals * 0.1 + rng.normal(0, 0.01, n)

    symbols = [f"S{i:03d}" for i in range(n)]
    signal_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "signal_value": signal_vals,
    })
    label_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "forward_return": return_vals,
    })
    return signal_df, label_df


class TestComputeQuantileSpread:
    def test_positive_spread(self):
        sig, lab = _make_spread_data("positive")
        result = compute_quantile_spread(sig, lab, n_quantiles=5)
        assert len(result) == 1
        assert result["spread"].iloc[0] > 0

    def test_negative_spread(self):
        sig, lab = _make_spread_data("negative")
        result = compute_quantile_spread(sig, lab, n_quantiles=5)
        assert result["spread"].iloc[0] < 0

    def test_n_top_bottom(self):
        sig, lab = _make_spread_data("positive")
        result = compute_quantile_spread(sig, lab, n_quantiles=5)
        assert result["n_top"].iloc[0] == 20
        assert result["n_bottom"].iloc[0] == 20

    def test_multiple_timestamps(self):
        sig1, lab1 = _make_spread_data("positive")
        sig2, lab2 = _make_spread_data("negative")
        sig2["timestamp"] = pd.Timestamp("2025-01-02")
        lab2["timestamp"] = pd.Timestamp("2025-01-02")

        sig = pd.concat([sig1, sig2])
        lab = pd.concat([lab1, lab2])
        result = compute_quantile_spread(sig, lab, n_quantiles=5)
        assert len(result) == 2


class TestSummarizeQuantileSpread:
    def test_summary_keys(self):
        df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=50, freq="h"),
            "top_mean": 0.05, "bottom_mean": 0.02,
            "spread": 0.03, "n_top": 20, "n_bottom": 20,
        })
        s = summarize_quantile_spread(df)
        assert "mean_spread" in s
        assert "median_spread" in s
        assert "positive_fraction" in s
        assert s["n_periods"] == 50
