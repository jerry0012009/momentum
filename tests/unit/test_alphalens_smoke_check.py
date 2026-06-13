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
    """Create synthetic local evaluation results."""
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
    def test_match_when_close(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.01, local_df)
        assert comp["status"] == "match"
        assert comp["abs_diff"] == 0.0

    def test_explainable_when_large_diff(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.05, local_df)
        assert comp["status"] == "explainable"
        assert "Pearson" in comp["note"]
        assert "Spearman" in comp["note"]

    def test_local_not_found(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("unknown_factor", "1h", 0.01, local_df)
        assert comp["status"] == "local_result_not_found"


class TestComparisonTableSchema:
    def test_required_keys(self):
        local_df = _make_local_results_df()
        comp = build_comparison_table("mom_20h", "1h", 0.01, local_df)
        required = {"factor_id", "horizon", "local_IC", "alphalens_IC", "abs_diff", "status", "note"}
        assert required.issubset(comp.keys())


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
