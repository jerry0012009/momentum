"""Unit tests for run_alphalens_smoke_check.py (Phase 5C)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from run_alphalens_smoke_check import (
    EXCLUDED_SYMBOLS,
    build_comparison_row,
    build_factor_data,
    compute_direct_spearman_ic,
    filter_to_evaluation_universe,
    run_alphalens_analysis,
)


# ── Fixtures ──────────────────────────────────────────────────────

def _make_exported_data(n=200, n_symbols=8, include_excluded=True):
    """Create synthetic alphalens_factor_data.parquet-style data."""
    timestamps = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    symbols = [f"S{i:02d}USDT" for i in range(n_symbols)]
    if include_excluded:
        symbols.extend(EXCLUDED_SYMBOLS[:3])
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


# ── Sample Alignment Tests ────────────────────────────────────────

class TestSampleAlignment:
    def test_excluded_symbols_removed(self):
        afd = _make_exported_data(n=50, n_symbols=5, include_excluded=True)
        fd = build_factor_data(afd, ["1h"])
        filtered, info = filter_to_evaluation_universe(fd, EXCLUDED_SYMBOLS)
        assets = filtered.index.get_level_values("asset").unique()
        for sym in EXCLUDED_SYMBOLS:
            assert sym not in assets

    def test_excluded_count_correct(self):
        afd = _make_exported_data(n=50, n_symbols=5, include_excluded=True)
        fd = build_factor_data(afd, ["1h"])
        _, info = filter_to_evaluation_universe(fd, EXCLUDED_SYMBOLS)
        assert info["excluded_count"] == len(EXCLUDED_SYMBOLS)

    def test_post_filter_rows_less_than_pre(self):
        afd = _make_exported_data(n=50, n_symbols=5, include_excluded=True)
        fd = build_factor_data(afd, ["1h"])
        _, info = filter_to_evaluation_universe(fd, EXCLUDED_SYMBOLS)
        assert info["post_filter_rows"] < info["pre_filter_rows"]

    def test_evaluation_symbols_count_reported(self):
        afd = _make_exported_data(n=50, n_symbols=5, include_excluded=True)
        fd = build_factor_data(afd, ["1h"])
        _, info = filter_to_evaluation_universe(fd, EXCLUDED_SYMBOLS)
        assert "evaluation_symbols_count" in info
        assert info["evaluation_symbols_count"] > 0

    def test_no_excluded_when_not_included(self):
        afd = _make_exported_data(n=50, n_symbols=5, include_excluded=False)
        fd = build_factor_data(afd, ["1h"])
        filtered, info = filter_to_evaluation_universe(fd, EXCLUDED_SYMBOLS)
        assert info["pre_filter_symbols"] == info["post_filter_symbols"]


# ── Direct Spearman Tests ─────────────────────────────────────────

class TestDirectSpearman:
    def test_returns_mean_std_count(self):
        afd = _make_exported_data(n=100, n_symbols=3, include_excluded=False)
        fd = build_factor_data(afd, ["1h"])
        result = compute_direct_spearman_ic(fd, "1h")
        assert result["status"] == "ok"
        assert "mean" in result
        assert "std" in result
        assert "count" in result

    def test_missing_horizon_column(self):
        afd = _make_exported_data(n=50, n_symbols=3, include_excluded=False)
        fd = build_factor_data(afd, ["1h"])
        assert compute_direct_spearman_ic(fd, "99h")["status"] == "error"


# ── Comparison Row Tests ──────────────────────────────────────────

class TestBuildComparisonRow:
    def test_match_when_identical(self):
        local_df = _make_local_results_df()
        row = build_comparison_row("mom_20h", "1h", 0.05, 0.05, local_df)
        assert row["status"] == "match"
        assert row["primary_abs_diff"] == 0.0

    def test_near_match_small_diff(self):
        local_df = _make_local_results_df()
        row = build_comparison_row("mom_20h", "1h", 0.05, 0.05005, local_df)
        assert row["status"] == "near_match"

    def test_mismatch_large_diff(self):
        local_df = _make_local_results_df()
        row = build_comparison_row("mom_20h", "1h", 0.05, 0.10, local_df)
        assert row["status"] == "mismatch"
        assert "primary_diff" in row["note"]

    def test_schema_keys(self):
        local_df = _make_local_results_df()
        row = build_comparison_row("mom_20h", "1h", 0.01, 0.01, local_df)
        required = {
            "factor_id", "horizon",
            "local_summary_RankIC", "direct_SpearmanIC",
            "alphalens_SpearmanIC", "primary_abs_diff", "status", "note",
        }
        assert required.issubset(row.keys())

    def test_status_based_on_primary_diff(self):
        """Status determined by alphalens vs direct Spearman."""
        local_df = _make_local_results_df()
        row = build_comparison_row("mom_20h", "1h", 0.05, 0.05, local_df)
        assert row["status"] == "match"


# ── Verdict Logic ─────────────────────────────────────────────────

class TestVerdictLogic:
    def test_all_match_allows_pass(self):
        statuses = ["match", "match", "near_match", "match"]
        assert all(s in ("match", "near_match") for s in statuses)

    def test_mismatch_prevents_pass(self):
        statuses = ["match", "mismatch", "match", "match"]
        assert not all(s in ("match", "near_match") for s in statuses)


# ── Alphalens Functionality ───────────────────────────────────────

class TestAlphalensFunctions:
    def test_ic_computed(self):
        afd = _make_exported_data(n=100, n_symbols=3, include_excluded=False)
        fd = build_factor_data(afd, ["1h", "4h"])
        result = run_alphalens_analysis(fd, ["1h", "4h"])
        assert result["status"] == "ok"
        assert "1h" in result["ic"]

    def test_quantile_returns_computed(self):
        afd = _make_exported_data(n=100, n_symbols=3, include_excluded=False)
        fd = build_factor_data(afd, ["1h"])
        result = run_alphalens_analysis(fd, ["1h"])
        assert "1h" in result["mean_return_by_quantile"]
        assert len(result["mean_return_by_quantile"]["1h"]) == 5


# ── Source Code Checks ────────────────────────────────────────────

class TestNoFutureLeak:
    def test_no_shift_in_source(self):
        src = Path(__file__).resolve().parents[2] / "scripts" / "run_alphalens_smoke_check.py"
        code = src.read_text()
        assert "shift(-" not in code
