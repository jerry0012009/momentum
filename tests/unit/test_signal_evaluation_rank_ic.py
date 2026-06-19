"""Tests for rank_ic module using toy data."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.rank_ic import compute_rank_ic, summarize_rank_ic


def _make_signal_return(perfect="positive"):
    """Create toy signal + return data."""
    symbols = ["A", "B", "C", "D", "E"]
    ts = pd.Timestamp("2025-01-01")

    if perfect == "positive":
        signal_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        return_vals = [0.01, 0.02, 0.03, 0.04, 0.05]
    elif perfect == "negative":
        signal_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        return_vals = [0.05, 0.04, 0.03, 0.02, 0.01]
    else:
        signal_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        return_vals = [0.03, 0.01, 0.05, 0.02, 0.04]

    signal_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "signal_value": signal_vals,
    })
    label_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "forward_return": return_vals,
    })
    return signal_df, label_df


class TestComputeRankIC:
    def test_perfect_positive(self):
        sig, lab = _make_signal_return("positive")
        result = compute_rank_ic(sig, lab)
        assert len(result) == 1
        assert result["rank_ic"].iloc[0] == pytest.approx(1.0, abs=1e-10)

    def test_perfect_negative(self):
        sig, lab = _make_signal_return("negative")
        result = compute_rank_ic(sig, lab)
        assert result["rank_ic"].iloc[0] == pytest.approx(-1.0, abs=1e-10)

    def test_n_symbols(self):
        sig, lab = _make_signal_return("positive")
        result = compute_rank_ic(sig, lab)
        assert result["n_symbols"].iloc[0] == 5

    def test_nan_dropped(self):
        sig, lab = _make_signal_return("positive")
        lab.loc[0, "forward_return"] = np.nan
        result = compute_rank_ic(sig, lab)
        assert result["n_symbols"].iloc[0] == 4
        assert not np.isnan(result["rank_ic"].iloc[0])

    def test_multiple_timestamps(self):
        sig1, lab1 = _make_signal_return("positive")
        sig2, lab2 = _make_signal_return("negative")
        sig2["timestamp"] = pd.Timestamp("2025-01-02")
        lab2["timestamp"] = pd.Timestamp("2025-01-02")

        sig = pd.concat([sig1, sig2])
        lab = pd.concat([lab1, lab2])
        result = compute_rank_ic(sig, lab)
        assert len(result) == 2

    def test_min_symbols_filter(self):
        sig, lab = _make_signal_return("positive")
        sig = sig.iloc[:2]
        lab = lab.iloc[:2]
        result = compute_rank_ic(sig, lab, min_symbols=5)
        assert np.isnan(result["rank_ic"].iloc[0])


class TestSummarizeRankIC:
    def test_summary_keys(self):
        df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=100, freq="h"),
            "rank_ic": np.random.randn(100) * 0.01 + 0.03,
            "n_symbols": 50,
        })
        s = summarize_rank_ic(df)
        assert "mean_rank_ic" in s
        assert "t_stat" in s
        assert "positive_fraction" in s
        assert s["n_periods"] == 100

    def test_positive_t_stat(self):
        rng = np.random.default_rng(42)
        df = pd.DataFrame({
            "timestamp": pd.date_range("2025-01-01", periods=200, freq="h"),
            "rank_ic": rng.normal(0.03, 0.02, 200),
            "n_symbols": 50,
        })
        s = summarize_rank_ic(df)
        assert s["t_stat"] > 5  # should be highly significant
