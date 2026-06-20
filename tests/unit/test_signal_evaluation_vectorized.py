"""Tests for vectorized RankIC and Spread parity with reference."""

import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.rank_ic import compute_rank_ic, _compute_rank_ic_reference
from momentum.signal_evaluation.quantile_spread import compute_quantile_spread, _compute_quantile_spread_reference
from momentum.signal_evaluation._vectorized import (
    compute_rank_ic_vectorized,
    compute_quantile_spread_legacy_vectorized,
    _rank_rows,
    _row_pearson,
)


def _make_data(n_ts=100, n_sym=50, seed=42):
    """Generate toy signal + label data."""
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range("2025-01-01", periods=n_ts, freq="h")
    symbols = [f"S{i:03d}" for i in range(n_sym)]
    rows = []
    for ts in timestamps:
        for sym in symbols:
            rows.append({
                "timestamp": ts, "symbol": sym,
                "signal_value": rng.normal(),
                "forward_return": rng.normal() * 0.01,
            })
    df = pd.DataFrame(rows)
    sig = df[["timestamp", "symbol", "signal_value"]]
    lab = df[["timestamp", "symbol", "forward_return"]]
    return sig, lab


class TestRankRows:
    def test_basic(self):
        mat = np.array([[3.0, 1.0, 2.0], [5.0, 4.0, 6.0]])
        ranked = _rank_rows(mat)
        np.testing.assert_array_equal(ranked[0], [3.0, 1.0, 2.0])
        np.testing.assert_array_equal(ranked[1], [2.0, 1.0, 3.0])

    def test_nan_handling(self):
        mat = np.array([[3.0, np.nan, 2.0], [np.nan, np.nan, np.nan]])
        ranked = _rank_rows(mat)
        assert not np.isnan(ranked[0, 0])
        assert np.isnan(ranked[0, 1])
        assert not np.isnan(ranked[0, 2])
        assert all(np.isnan(ranked[1]))

    def test_constant_row(self):
        mat = np.array([[5.0, 5.0, 5.0]])
        ranked = _rank_rows(mat)
        # All same value → ranks should be average: (1+2+3)/3 = 2.0
        np.testing.assert_allclose(ranked[0], [2.0, 2.0, 2.0])

    def test_ties_average_rank(self):
        """Tied values must get average rank, matching scipy.stats.rankdata(method='average')."""
        mat = np.array([[3.0, 1.0, 3.0, 2.0, 1.0]])
        ranked = _rank_rows(mat)
        # Sorted: 1,1,2,3,3 → ranks: (1+2)/2=1.5, 1.5, 3, (4+5)/2=4.5, 4.5
        # Original order: 3→4.5, 1→1.5, 3→4.5, 2→3, 1→1.5
        expected = np.array([[4.5, 1.5, 4.5, 3.0, 1.5]])
        np.testing.assert_allclose(ranked, expected, atol=1e-10)


class TestRowPearson:
    def test_perfect_correlation(self):
        x = np.array([[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]], dtype=float)
        y = np.array([[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]], dtype=float)
        corr = _row_pearson(x, y)
        np.testing.assert_allclose(corr, [1.0, 1.0], atol=1e-10)

    def test_negative_correlation(self):
        x = np.array([[1, 2, 3, 4, 5]], dtype=float)
        y = np.array([[5, 4, 3, 2, 1]], dtype=float)
        corr = _row_pearson(x, y)
        np.testing.assert_allclose(corr, [-1.0], atol=1e-10)

    def test_with_nan(self):
        x = np.array([[1, 2, np.nan, 4, 5]], dtype=float)
        y = np.array([[1, 2, 3, 4, 5]], dtype=float)
        corr = _row_pearson(x, y)
        assert not np.isnan(corr[0])


class TestRankICParity:
    def test_vectorized_equals_reference(self):
        sig, lab = _make_data(n_ts=50, n_sym=30)
        ref = _compute_rank_ic_reference(sig, lab)
        vec = compute_rank_ic_vectorized(sig, lab)
        # Merge on timestamp
        merged = ref.merge(vec, on="timestamp", suffixes=("_ref", "_vec"))
        diff = (merged["rank_ic_ref"] - merged["rank_ic_vec"]).abs()
        assert diff.max() < 1e-10, f"Max diff: {diff.max()}"

    def test_public_api_uses_vectorized(self):
        """Public API should return same result as vectorized."""
        sig, lab = _make_data(n_ts=20, n_sym=20)
        pub = compute_rank_ic(sig, lab)
        vec = compute_rank_ic_vectorized(sig, lab)
        merged = pub.merge(vec, on="timestamp", suffixes=("_pub", "_vec"))
        diff = (merged["rank_ic_pub"] - merged["rank_ic_vec"]).abs()
        assert diff.max() < 1e-10

    def test_handles_mismatched_symbols(self):
        """Some timestamps have different symbol sets."""
        rng = np.random.default_rng(123)
        rows = []
        for i, ts in enumerate(pd.date_range("2025-01-01", periods=10, freq="h")):
            syms = [f"S{j}" for j in range(20 + i % 5)]
            for s in syms:
                rows.append({"timestamp": ts, "symbol": s, "signal_value": rng.normal(), "forward_return": rng.normal() * 0.01})
        df = pd.DataFrame(rows)
        sig = df[["timestamp", "symbol", "signal_value"]]
        lab = df[["timestamp", "symbol", "forward_return"]]
        ref = _compute_rank_ic_reference(sig, lab)
        vec = compute_rank_ic_vectorized(sig, lab)
        merged = ref.merge(vec, on="timestamp", suffixes=("_ref", "_vec"))
        diff = (merged["rank_ic_ref"] - merged["rank_ic_vec"]).abs()
        assert diff.max() < 1e-10


class TestLegacySpreadParity:
    def test_vectorized_equals_reference(self):
        sig, lab = _make_data(n_ts=50, n_sym=50)
        ref = _compute_quantile_spread_reference(sig, lab, is_legacy=True, quantile_frac=0.20, min_cross_section=10)
        vec = compute_quantile_spread_legacy_vectorized(sig, lab, quantile_frac=0.20, min_cross_section=10)
        merged = ref.merge(vec, on="timestamp", suffixes=("_ref", "_vec"))
        diff = (merged["spread_ref"] - merged["spread_vec"]).abs()
        assert diff.max() < 1e-12, f"Max spread diff: {diff.max()}"

    def test_public_api_uses_vectorized_for_legacy(self):
        sig, lab = _make_data(n_ts=20, n_sym=20)
        pub = compute_quantile_spread(sig, lab, mode="legacy_phase10a")
        vec = compute_quantile_spread_legacy_vectorized(sig, lab)
        merged = pub.merge(vec, on="timestamp", suffixes=("_pub", "_vec"))
        diff = (merged["spread_pub"] - merged["spread_vec"]).abs()
        assert diff.max() < 1e-12

    def test_standard_mode_unchanged(self):
        """Standard mode should still use reference path."""
        sig, lab = _make_data(n_ts=20, n_sym=20)
        std = compute_quantile_spread(sig, lab, mode="standard")
        assert len(std) == 20
        assert "spread" in std.columns


class TestPerformanceContract:
    def test_no_active_phase10_in_src(self):
        """Verify no Phase 10 scripts restored."""
        src = Path(__file__).resolve().parents[2] / "src" / "momentum" / "signal_evaluation"
        for f in src.glob("*.py"):
            content = f.read_text()
            assert "run_phase10" not in content
