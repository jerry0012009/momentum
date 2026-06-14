"""Unit tests for Phase 7C-A: Dynamic Evaluation Adapter Hardening.

Tests verify:
- load_selected_factor_ids returns exactly 27 selected_for_7B factors
- load_candidate_directions has correct directions for all families
- build_factor_values --factor-ids only builds specified factors
- evaluate_factors_dynamic_universe direction lookup uses candidate CSV first
- Invalid factor_ids fail fast
- Cross-sectional postprocess still applies to xs_rank_* factors
- No fallback positive for any selected_for_7B factor
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

import pandas as pd
import pytest

_scripts = str(_Path(__file__).resolve().parents[2] / "scripts")
_sys.path.insert(0, _scripts)

from build_factor_values import (
    load_selected_factor_ids,
    validate_factor_ids,
    apply_cross_sectional_postprocess,
    calc_group,
)
from evaluate_factors_dynamic_universe import (
    load_selected_factor_ids as load_ids_eval,
    load_candidate_directions,
)
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID

RUN = _Path(__file__).resolve().parents[2] / "research" / "factor_runs" / "crypto_top50_factor_library"
CANDIDATE_CSV = RUN / "factor_mining_candidates_v0_1.csv"


# ---------------------------------------------------------------------------
# Candidate CSV loading
# ---------------------------------------------------------------------------

class TestCandidateCSQLoading:
    def test_load_selected_27(self):
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        assert len(ids) == 27

    def test_all_27_in_registry(self):
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        registry_ids = set(REGISTRY_BY_ID.keys())
        for fid in ids:
            assert fid in registry_ids, f"{fid} not in REGISTRY"

    def test_exact_27_ids(self):
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        expected = {
            "mom_5h", "mom_10h", "mom_40h",
            "rev_3h", "rev_10h", "rev_24h",
            "vol_5h", "vol_40h", "vol_ratio_5_20",
            "range_1h", "range_4h", "range_24h",
            "price_pos_24h", "price_pos_72h",
            "vol_zscore_20h", "vol_zscore_48h",
            "qvol_zscore_20h", "qvol_zscore_48h",
            "ma_gap_5_20", "ma_gap_10_40",
            "breakout_dist_20h", "breakout_dist_48h",
            "candle_body", "candle_wick_upper", "candle_wick_lower",
            "xs_rank_ret_1h", "xs_rank_vol",
        }
        assert set(ids) == expected


# ---------------------------------------------------------------------------
# Direction loading
# ---------------------------------------------------------------------------

class TestCandidateDirections:
    def test_all_27_have_direction(self):
        directions = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            assert fid in directions, f"{fid} missing from candidate directions"
            assert directions[fid] in ("positive", "negative", "conditional"), \
                f"{fid} has invalid direction: {directions[fid]}"

    def test_reversal_is_negative(self):
        directions = load_candidate_directions(CANDIDATE_CSV)
        for fid in ["rev_3h", "rev_10h", "rev_24h"]:
            assert directions[fid] == "negative", f"{fid} should be negative"

    def test_volatility_negative_or_conditional(self):
        directions = load_candidate_directions(CANDIDATE_CSV)
        assert directions["vol_5h"] == "negative"
        assert directions["vol_40h"] == "negative"
        assert directions["vol_ratio_5_20"] == "conditional"

    def test_momentum_is_positive(self):
        directions = load_candidate_directions(CANDIDATE_CSV)
        for fid in ["mom_5h", "mom_10h", "mom_40h"]:
            assert directions[fid] == "positive", f"{fid} should be positive"

    def test_xs_rank_is_conditional(self):
        directions = load_candidate_directions(CANDIDATE_CSV)
        assert directions["xs_rank_ret_1h"] == "conditional"
        assert directions["xs_rank_vol"] == "conditional"


# ---------------------------------------------------------------------------
# Factor subset filtering
# ---------------------------------------------------------------------------

class TestFactorSubset:
    def test_validate_factor_ids_valid(self):
        """All 27 selected_for_7B should pass validation."""
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        validate_factor_ids(ids)  # should not raise

    def test_validate_factor_ids_invalid(self):
        """Non-existent factor_id should fail fast."""
        with pytest.raises(ValueError, match="not in REGISTRY"):
            validate_factor_ids(["nonexistent_factor_xyz"])

    def test_calc_group_subset(self):
        """calc_group with subset should only produce specified columns."""
        df = pd.DataFrame({
            "symbol": ["BTCUSDT"] * 5,
            "timestamp": pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC"),
            "open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [105.0, 106.0, 107.0, 108.0, 109.0],
            "low": [95.0, 96.0, 97.0, 98.0, 99.0],
            "close": [102.0, 103.0, 104.0, 105.0, 106.0],
            "volume": [1000.0] * 5,
            "quote_volume": [100000.0] * 5,
        })
        result = calc_group(df, ["mom_5h", "candle_body"])
        assert "mom_5h" in result.columns
        assert "candle_body" in result.columns
        # Should NOT have other factors
        assert "vol_5h" not in result.columns
        assert "range_1h" not in result.columns

    def test_calc_group_none_is_all(self):
        """calc_group with None should produce all REGISTRY factors."""
        df = pd.DataFrame({
            "symbol": ["BTCUSDT"] * 80,
            "timestamp": pd.date_range("2026-01-01", periods=80, freq="h", tz="UTC"),
            "open": [100.0] * 80,
            "high": [105.0] * 80,
            "low": [95.0] * 80,
            "close": [102.0] * 80,
            "volume": [1000.0] * 80,
            "quote_volume": [100000.0] * 80,
        })
        result = calc_group(df, None)
        for spec in REGISTRY:
            assert spec.factor_id in result.columns


# ---------------------------------------------------------------------------
# Direction source (no fallback positive for 7B)
# ---------------------------------------------------------------------------

class TestDirectionSource:
    def test_no_fallback_for_selected_7b(self):
        """All 27 selected_for_7B should have direction from candidate CSV,
        not fallback positive."""
        candidate_directions = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            assert fid in candidate_directions, \
                f"{fid} would fall back — not in candidate CSV"


# ---------------------------------------------------------------------------
# Cross-sectional postprocess
# ---------------------------------------------------------------------------

class TestCrossSectionalPostprocess:
    def test_xs_factors_ranked_in_subset(self):
        """Even when building a subset, xs_rank factors get postprocessed."""
        ts = pd.Timestamp("2026-01-01", tz="UTC")
        wide = pd.DataFrame({
            "timestamp": [ts] * 3,
            "symbol": ["A", "B", "C"],
            "xs_rank_ret_1h": [0.01, 0.03, 0.02],
            "mom_5h": [0.05, -0.02, 0.01],
        })
        result = apply_cross_sectional_postprocess(wide)
        # xs_rank should be percentile ranks
        assert abs(result["xs_rank_ret_1h"].iloc[0] - 1 / 3) < 0.01
        assert abs(result["xs_rank_ret_1h"].iloc[1] - 1.0) < 0.01
        # mom_5h should be unchanged
        assert result["mom_5h"].iloc[0] == 0.05


# ---------------------------------------------------------------------------
# Consistency: build and eval use same direction source
# ---------------------------------------------------------------------------

class TestBuildEvalConsistency:
    def test_eval_loads_same_ids(self):
        """build_factor_values and evaluate use the same load function."""
        ids_build = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        ids_eval = load_ids_eval(CANDIDATE_CSV, "selected_for_7B")
        assert ids_build == ids_eval

    def test_eval_loads_same_directions(self):
        """evaluate loads candidate directions matching REGISTRY expected_direction."""
        cand_dirs = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            reg = REGISTRY_BY_ID[fid]
            cand_dir = cand_dirs[fid]
            assert reg.expected_direction == cand_dir, \
                f"{fid}: REGISTRY says {reg.expected_direction}, CSV says {cand_dir}"


# ---------------------------------------------------------------------------
# Fail-fast: missing factor_values in explicit/candidate mode
# ---------------------------------------------------------------------------

class TestFailFast:
    def test_validate_rejects_unknown_factor(self):
        """Factor not in REGISTRY must raise ValueError."""
        with pytest.raises(ValueError, match="not in REGISTRY"):
            validate_factor_ids(["mom_5h", "nonexistent_xyz"])

    def test_selected_count_exactly_27(self):
        """selected_for_7B must parse to exactly 27 factors."""
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        assert len(ids) == 27, f"Expected 27 selected_for_7B, got {len(ids)}"

    def test_all_27_have_candidate_direction(self):
        """Every selected_for_7B factor must have explicit direction in candidate CSV.
        If this fails, evaluate would fallback to positive — which is not allowed."""
        cand_dirs = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        missing = [fid for fid in ids if fid not in cand_dirs]
        assert missing == [], f"Factors missing from candidate directions: {missing}"

    def test_no_fallback_positive_in_candidate_directions(self):
        """All selected_for_7B directions must be positive/negative/conditional,
        never a fallback to positive."""
        cand_dirs = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            d = cand_dirs[fid]
            assert d in ("positive", "negative", "conditional"), \
                f"{fid} has invalid direction: {d}"

    def test_calc_group_subset_does_not_leak(self):
        """When building a subset, other factors must not appear in output."""
        df = pd.DataFrame({
            "symbol": ["BTCUSDT"] * 5,
            "timestamp": pd.date_range("2026-01-01", periods=5, freq="h", tz="UTC"),
            "open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [105.0, 106.0, 107.0, 108.0, 109.0],
            "low": [95.0, 96.0, 97.0, 98.0, 99.0],
            "close": [102.0, 103.0, 104.0, 105.0, 106.0],
            "volume": [1000.0] * 5,
            "quote_volume": [100000.0] * 5,
        })
        result = calc_group(df, ["candle_body"])
        # Only candle_body + timestamp + symbol
        assert list(result.columns) == ["timestamp", "symbol", "candle_body"]
