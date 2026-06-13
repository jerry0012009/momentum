"""Unit tests for run_alphalens_smoke_check.py."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from run_alphalens_smoke_check import (
    build_comparison_table,
    build_factor_data,
    load_local_results,
    run_alphalens_analysis,
)


# ── Fixtures ──────────────────────────────────────────────────────

def _make_exported_data(n=200, n_symbols=5):
    """Create synthetic alphalens_factor_data.parquet-style data."""
    timestamps = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    symbols = [f"S{i:02d}USDT" for i in range(n_symbols)]
    rows = []
    rng = np.random.default_rng(42)
    for sym in symbols:
        for ts in timestamps:
            rows.append({
                "timestamp": ts,
                "symbol": sym,
                "factor": rng.standard_normal(),
                "forward_return_1h": rng.standard_normal() * 0.01,
                "forward_return_4h": rng.standard_normal() * 0.02,
                "forward_return_24h": rng.standard_normal() * 0.05,
                "forward_return_72h": rng.standard_normal() * 0.1,
                "factor_quantile": int(rng.integers(1, 6)),
            })
    return pd.DataFrame(rows)


def _make_local_results_df():
    """Create synthetic local evaluation results with both IC_mean and RankIC_mean."""
    rows = []
    for fid in ["mom_20h", "wq101_alpha53"]:
        for h in ["1h", "4h", "24h", "72h"]:
            rows.append({
                "factor_id": fid,
                "label": f"ret_fwd_{h}",
                "direction": "positive",
                "IC_mean": 0.01,
                "RankIC_mean": 0.015,
            })
    return pd.DataFrame(rows)


# ── Tests ─────────────────────────────────────────────────────────

class TestBuildFactorData:
    def test_output_columns(self):
        afd = _make_exported_data()
        horizons = ["1h", "4h", "24h", "72h"]
        result = build_factor_data(afd, horizons)
        assert "factor" in result.columns
        assert "factor_quantile" in result.columns
        for h in horizons:
            assert h in result.columns

    def test_multiindex_names(self):
        afd = _make_exported_data()
        result = build_factor_data(afd, ["1h"])
        assert result.index.names == ["date", "asset"]

    def test_row_count(self):
        afd = _make_exported_data(n=50, n_symbols=3)
        result = build_factor_data(afd, ["1h"])
        assert len(result) == 50 * 3


class TestRunAlphalensAnalysis:
    def test_ic_computed(self):
        afd = _make_exported_data(n=100, n_symbols=3)
        factor_data = build_factor_data(afd, ["1h", "4h"])
        result = run_alphalens_analysis(factor_data, ["1h", "4h"])
        assert result["status"] == "ok"
        assert "1h" in result["ic"]
        assert "4h" in result["ic"]
        assert "mean" in result["ic"]["1h"]

    def test_quantile_returns_computed(self):
        afd = _make_exported_data(n=100, n_symbols=3)
        factor_data = build_factor_data(afd, ["1h"])
        result = run_alphalens_analysis(factor_data, ["1h"])
        assert "1h" in result["mean_return_by_quantile"]
        qr = result["mean_return_by_quantile"]["1h"]
        assert len(qr) == 5  # 5 quantiles

    def test_missing_horizon(self):
        afd = _make_exported_data(n=50, n_symbols=3)
        factor_data = build_factor_data(afd, ["1h"])
        result = run_alphalens_analysis(factor_data, ["99h"])
        assert result["status"] == "error"


class TestBuildComparisonTable:
    def test_match_when_exact(self):
        """rankic_abs_diff <= 1e-6 → match."""
        local_df = _make_local_results_df()
        # alphalens_ic == local RankIC_mean (0.015)
        comp = build_comparison_table("mom_20h", "1h", 0.015, local_df)
        assert comp["status"] == "match"
        assert comp["rankic_abs_diff"] == 0.0

    def test_near_match_when_small_diff(self):
        """1e-6 < rankic_abs_diff <= 1e-4 → near_match."""
        local_df = _make_local_results_df()
        # alphalens_ic slightly off from RankIC_mean (0.015)
        comp = build_comparison_table("mom_20h", "1h", 0.01505, local_df)
        assert comp["status"] == "near_match"

    def test_mismatch_when_large_diff(self):
        """rankic_abs_diff > 1e-4 → mismatch."""
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.05, local_df)
        assert comp["status"] == "mismatch"
        assert "rankic_abs_diff" in comp["note"]

    def test_local_not_found(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("unknown_factor", "1h", 0.01, local_df)
        assert comp["status"] == "local_result_not_found"


class TestComparisonTableSchema:
    def test_required_keys(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.01, local_df)
        required = {
            "factor_id", "horizon",
            "local_Pearson_IC", "local_RankIC", "alphalens_Spearman_IC",
            "rankic_abs_diff", "pearson_abs_diff",
            "status", "note",
        }
        assert required.issubset(comp.keys())

    def test_primary_comparison_uses_rankic(self):
        """Primary diff must be rankic_abs_diff, not pearson_abs_diff."""
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.015, local_df)
        # RankIC_mean=0.015, alphalens_ic=0.015 → rankic_abs_diff=0
        assert comp["rankic_abs_diff"] == 0.0
        assert comp["status"] == "match"
        # Pearson IC_mean=0.015 → pearson_abs_diff should be 0.005
        assert comp["pearson_abs_diff"] == 0.005

    def test_status_based_on_rankic_diff(self):
        """Status must be determined by rankic_abs_diff, not pearson_abs_diff."""
        local_df = _make_local_results_df()
        # RankIC_mean=0.015, alphalens=0.01505 → near_match
        comp = build_comparison_table("mom_20h", "1h", 0.01505, local_df)
        assert comp["status"] == "near_match"
        # pearson_abs_diff would be |0.01505-0.01| = 0.00505 → mismatch if used
        assert comp["pearson_abs_diff"] > 1e-4


class TestDependencyHandling:
    def test_alphalens_importable(self):
        """Verify alphalens is installed (smoke check prerequisite)."""
        try:
            import alphalens
            assert hasattr(alphalens, "__version__")
        except ImportError:
            pytest.skip("alphalens not installed")


class TestNoFutureLeak:
    def test_no_shift_in_source(self):
        """Verify the smoke check script does not use shift(-k)."""
        src = Path(__file__).resolve().parents[2] / "scripts" / "run_alphalens_smoke_check.py"
        code = src.read_text()
        assert "shift(-" not in code
        assert "shift(-1)" not in code
