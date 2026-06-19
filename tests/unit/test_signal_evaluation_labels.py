"""Tests for label adapter integration with rank_ic and quantile_spread."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.labels import select_forward_return
from momentum.signal_evaluation.rank_ic import compute_rank_ic
from momentum.signal_evaluation.quantile_spread import compute_quantile_spread


def _make_toy_data():
    """Create toy signal + wide label data for integration tests."""
    ts = pd.Timestamp("2025-01-01")
    symbols = ["A", "B", "C", "D", "E"]
    signal_vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    ret_1h = [0.01, 0.02, 0.03, 0.04, 0.05]  # perfectly correlated
    ret_4h = [0.05, 0.04, 0.03, 0.02, 0.01]  # perfectly anti-correlated

    signal_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "signal_name": "test_signal", "signal_value": signal_vals,
    })
    label_df = pd.DataFrame({
        "timestamp": ts, "symbol": symbols,
        "ret_fwd_1h": ret_1h, "ret_fwd_4h": ret_4h,
    })
    return signal_df, label_df


class TestAdapterRankICIntegration:
    def test_perfect_positive_1h(self):
        sig, lab = _make_toy_data()
        label_1h = select_forward_return(lab, "1h")
        result = compute_rank_ic(sig, label_1h)
        assert result["rank_ic"].iloc[0] == pytest.approx(1.0, abs=1e-10)

    def test_perfect_negative_4h(self):
        sig, lab = _make_toy_data()
        label_4h = select_forward_return(lab, "4h")
        result = compute_rank_ic(sig, label_4h)
        assert result["rank_ic"].iloc[0] == pytest.approx(-1.0, abs=1e-10)


class TestAdapterQuantileSpreadIntegration:
    def test_positive_spread_1h(self):
        sig, lab = _make_toy_data()
        label_1h = select_forward_return(lab, "1h")
        result = compute_quantile_spread(sig, label_1h, n_quantiles=2)
        # top bucket (E,D) avg = 0.045, bottom (A,B) avg = 0.015
        assert result["spread"].iloc[0] > 0

    def test_negative_spread_4h(self):
        sig, lab = _make_toy_data()
        label_4h = select_forward_return(lab, "4h")
        result = compute_quantile_spread(sig, label_4h, n_quantiles=2)
        # top signal (E,D) has lower return in 4h
        assert result["spread"].iloc[0] < 0
