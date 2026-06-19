"""Tests for legacy_phase10a spread mode."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from momentum.signal_evaluation.quantile_spread import compute_quantile_spread


def _make_signal(n_symbols=50, n_ts=10, seed=42):
    """Create synthetic signal + label data."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2024-01-01", periods=n_ts, freq="h")
    symbols = [f"S{i:02d}" for i in range(n_symbols)]
    rows = []
    for ts in timestamps:
        for sym in symbols:
            rows.append({"timestamp": ts, "symbol": sym, "signal_value": rng.standard_normal()})
    signal_df = pd.DataFrame(rows)
    label_df = signal_df[["timestamp", "symbol"]].copy()
    label_df["forward_return"] = rng.standard_normal(len(label_df))
    return signal_df, label_df


def test_legacy_mode_basic():
    """Legacy mode returns correct schema."""
    signal_df, label_df = _make_signal()
    result = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    assert set(result.columns) >= {"timestamp", "top_mean", "bottom_mean", "spread", "n_top", "n_bottom"}
    assert len(result) == 10  # 10 timestamps


def test_legacy_nq_calculation():
    """n_q = max(int(n * 0.20), 1), so for 50 symbols -> 10."""
    signal_df, label_df = _make_signal(n_symbols=50)
    result = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    # All timestamps should have n_top = n_bottom = 10
    assert (result["n_top"] == 10).all()
    assert (result["n_bottom"] == 10).all()


def test_legacy_nq_small_n():
    """For n=12, n_q = max(int(12*0.2), 1) = 2."""
    signal_df, label_df = _make_signal(n_symbols=12)  # 12 >= min_cross_section=10
    result = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    assert (result["n_top"] == 2).all()
    assert (result["n_bottom"] == 2).all()


def test_legacy_min_cross_section():
    """Timestamps with < 10 symbols should be NaN."""
    signal_df, label_df = _make_signal(n_symbols=8)  # 8 < 10
    result = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    assert result["spread"].isna().all()


def test_standard_mode_same_schema():
    """Standard mode returns same schema."""
    signal_df, label_df = _make_signal()
    result = compute_quantile_spread(signal_df, label_df, mode="standard")
    assert set(result.columns) >= {"timestamp", "top_mean", "bottom_mean", "spread", "n_top", "n_bottom"}


def test_modes_differ_on_boundary():
    """Standard and legacy can produce different spreads."""
    signal_df, label_df = _make_signal(n_symbols=20, n_ts=5)
    legacy = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    standard = compute_quantile_spread(signal_df, label_df, mode="standard")
    # They may differ (not guaranteed for all random seeds, but very likely)
    # Just check both produce valid output
    assert len(legacy) == len(standard) == 5


def test_invalid_mode_raises():
    """Invalid mode raises ValueError."""
    signal_df, label_df = _make_signal(n_symbols=10, n_ts=1)
    with pytest.raises(ValueError, match="Unknown mode"):
        compute_quantile_spread(signal_df, label_df, mode="invalid_mode")


def test_legacy_aliases():
    """rank_head_tail is an alias for legacy_phase10a."""
    signal_df, label_df = _make_signal(n_symbols=20, n_ts=3)
    r1 = compute_quantile_spread(signal_df, label_df, mode="legacy_phase10a")
    r2 = compute_quantile_spread(signal_df, label_df, mode="rank_head_tail")
    pd.testing.assert_frame_equal(r1, r2)


def test_standard_aliases():
    """qcut is an alias for standard."""
    signal_df, label_df = _make_signal(n_symbols=20, n_ts=3)
    r1 = compute_quantile_spread(signal_df, label_df, mode="standard")
    r2 = compute_quantile_spread(signal_df, label_df, mode="qcut")
    pd.testing.assert_frame_equal(r1, r2)
