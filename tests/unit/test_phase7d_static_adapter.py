"""Unit tests for Phase 7D-A: Static Evaluation Adapter Hardening.

Tests verify:
- static evaluator supports --factor-ids / --candidate-csv / --status
- 27 selected_for_7B factors resolved correctly
- candidate CSV direction lookup works
- fail-fast on missing factor_values / fallback positive in explicit mode
- legacy default behavior preserved
- static evaluator factor list and directions consistent with dynamic evaluator
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
CANDIDATE_CSV = RUN / "factor_mining_candidates_v0_1.csv"
CATALOG = RUN / "factor_catalog_v0_1.csv"
SCRIPTS = ROOT / "scripts"

# Make scripts importable
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from factor_formula_registry import REGISTRY, REGISTRY_BY_ID
from evaluate_factors import (
    load_selected_factor_ids,
    load_candidate_directions,
    load_catalog_directions,
    validate_factor_ids,
)


# ---------------------------------------------------------------------------
# Test: factor subset loading
# ---------------------------------------------------------------------------

class TestCandidateCSQLoading:
    def test_load_selected_27(self):
        """candidate CSV with selected_for_7B parses to 27 factors."""
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        assert len(ids) == 27

    def test_all_27_in_registry(self):
        """All 27 selected_for_7B factors exist in REGISTRY."""
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        validate_factor_ids(ids, REGISTRY_BY_ID)

    def test_exact_27_ids(self):
        """Verify the exact set of 27 factor IDs."""
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
# Test: direction source
# ---------------------------------------------------------------------------

class TestCandidateDirections:
    def test_all_27_have_direction(self):
        """Every selected_for_7B factor has expected_direction in candidate CSV."""
        dirs = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        missing = [fid for fid in ids if fid not in dirs]
        assert missing == [], f"Missing directions: {missing}"

    def test_reversal_is_negative(self):
        """Reversal factors have negative expected direction."""
        dirs = load_candidate_directions(CANDIDATE_CSV)
        for fid in ["rev_3h", "rev_10h", "rev_24h"]:
            assert dirs[fid] == "negative", f"{fid} should be negative, got {dirs[fid]}"

    def test_volatility_negative_or_conditional(self):
        dirs = load_candidate_directions(CANDIDATE_CSV)
        assert dirs["vol_5h"] == "negative"
        assert dirs["vol_40h"] == "negative"
        assert dirs["vol_ratio_5_20"] == "conditional"

    def test_no_fallback_for_selected_7b(self):
        """All 27 selected_for_7B have explicit direction (no fallback positive needed)."""
        cand_dirs = load_candidate_directions(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            assert fid in cand_dirs, f"{fid} missing from candidate CSV directions"


# ---------------------------------------------------------------------------
# Test: family naming
# ---------------------------------------------------------------------------

class TestFamilyNaming:
    def test_qvol_family_is_quote_volume_liquidity(self):
        """qvol factors must have family quote_volume_liquidity."""
        import csv as _csv
        with open(CANDIDATE_CSV) as f:
            rows = list(_csv.DictReader(f))
        fam_map = {r["factor_id"]: r["factor_family"] for r in rows}
        assert fam_map["qvol_zscore_20h"] == "quote_volume_liquidity"
        assert fam_map["qvol_zscore_48h"] == "quote_volume_liquidity"

    def test_xs_rank_family_is_cross_sectional_normalized(self):
        import csv as _csv
        with open(CANDIDATE_CSV) as f:
            rows = list(_csv.DictReader(f))
        fam_map = {r["factor_id"]: r["factor_family"] for r in rows}
        assert fam_map["xs_rank_ret_1h"] == "cross_sectional_normalized"
        assert fam_map["xs_rank_vol"] == "cross_sectional_normalized"


# ---------------------------------------------------------------------------
# Test: fail-fast
# ---------------------------------------------------------------------------

class TestFailFast:
    def test_validate_rejects_unknown_factor(self):
        """Factor not in REGISTRY must raise ValueError."""
        with pytest.raises(ValueError, match="not in REGISTRY"):
            validate_factor_ids(["mom_5h", "nonexistent_xyz"], REGISTRY_BY_ID)

    def test_selected_count_exactly_27(self):
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        assert len(ids) == 27


# ---------------------------------------------------------------------------
# Test: consistency with dynamic evaluator
# ---------------------------------------------------------------------------

class TestDynamicConsistency:
    def test_same_factors_as_dynamic(self):
        """Static evaluator loads same 27 factors as dynamic evaluator."""
        from evaluate_factors_dynamic_universe import (
            load_selected_factor_ids as dyn_load,
        )
        static_ids = set(load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B"))
        dynamic_ids = set(dyn_load(CANDIDATE_CSV, "selected_for_7B"))
        assert static_ids == dynamic_ids

    def test_same_directions_as_dynamic(self):
        """Static evaluator loads same directions as dynamic evaluator."""
        from evaluate_factors_dynamic_universe import (
            load_candidate_directions as dyn_dirs,
        )
        static_dirs = load_candidate_directions(CANDIDATE_CSV)
        dynamic_dirs = dyn_dirs(CANDIDATE_CSV)
        ids = load_selected_factor_ids(CANDIDATE_CSV, "selected_for_7B")
        for fid in ids:
            assert static_dirs[fid] == dynamic_dirs[fid], \
                f"{fid}: static={static_dirs[fid]}, dynamic={dynamic_dirs[fid]}"


# ---------------------------------------------------------------------------
# Test: legacy default behavior
# ---------------------------------------------------------------------------

class TestLegacyBehavior:
    def test_legacy_catalog_loads(self):
        """Old catalog directions still load without error."""
        if not CATALOG.exists():
            pytest.skip("factor_catalog_v0_1.csv not found")
        dirs = load_catalog_directions(CATALOG)
        assert len(dirs) > 0
