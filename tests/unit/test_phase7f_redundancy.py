"""Phase 7F: tests for analyze_factor_redundancy.py"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_factor_redundancy import (
    redundancy_level,
    compute_pairwise,
    find_redundancy_groups,
    aggregate_phase7f,
    _rep_score,
    NEAR_DUPLICATE,
    HIGH_REDUNDANCY,
    MODERATE_REDUNDANCY,
)

# ─── Fixtures ──────────────────────────────────────────────────────────────

FACTOR_IDS = [f"f{i}" for i in range(27)]
META = {fid: {"family": f"fam{i % 5}", "tier": "TIER_1_STABLE_DIAGNOSTIC",
              "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"}
        for i, fid in enumerate(FACTOR_IDS)}


def _make_wide(n_rows: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    data = {"timestamp": rng.integers(1, 100, n_rows), "symbol": rng.choice(["BTC", "ETH", "SOL"], n_rows)}
    for fid in FACTOR_IDS:
        data[fid] = rng.standard_normal(n_rows)
    return pd.DataFrame(data)


# ─── redundancy_level ──────────────────────────────────────────────────────

def test_redundancy_level_thresholds():
    assert redundancy_level(0.96) == "NEAR_DUPLICATE"
    assert redundancy_level(0.95) == "NEAR_DUPLICATE"
    assert redundancy_level(0.90) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.85) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.75) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.70) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.50) == "LOW_REDUNDANCY"
    assert redundancy_level(0.0) == "LOW_REDUNDANCY"


# ─── compute_pairwise ──────────────────────────────────────────────────────

def test_pairwise_row_count_27_factors():
    wide = _make_wide()
    pairs = compute_pairwise(wide, FACTOR_IDS, META)
    assert len(pairs) == 351, f"27 choose 2 = 351, got {len(pairs)}"


def test_pairwise_row_count_5_factors():
    ids = FACTOR_IDS[:5]
    wide = _make_wide()
    pairs = compute_pairwise(wide, ids, META)
    assert len(pairs) == 10, f"5 choose 2 = 10, got {len(pairs)}"


def test_pairwise_same_family_flag():
    wide = _make_wide()
    pairs = compute_pairwise(wide, FACTOR_IDS[:6], META)
    for p in pairs:
        expected = META[p["factor_i"]]["family"] == META[p["factor_j"]]["family"]
        assert p["same_family"] == expected


def test_pairwise_insufficient_obs():
    wide = pd.DataFrame({
        "timestamp": list(range(10)),
        "symbol": ["X"] * 10,
        "f0": list(range(10)),
        "f1": list(range(10)),
    })
    meta = {"f0": {"family": "a"}, "f1": {"family": "b"}}
    pairs = compute_pairwise(wide, ["f0", "f1"], meta)
    assert pairs[0]["redundancy_level"] == "INSUFFICIENT_DATA"


def test_pairwise_perfect_correlation():
    wide = pd.DataFrame({
        "timestamp": list(range(50)),
        "symbol": ["X"] * 50,
        "f0": list(range(50)),
        "f1": list(range(50)),
    })
    meta = {"f0": {"family": "a"}, "f1": {"family": "b"}}
    pairs = compute_pairwise(wide, ["f0", "f1"], meta)
    assert abs(pairs[0]["spearman_corr"] - 1.0) < 0.01


# ─── Representative selection ──────────────────────────────────────────────

def test_rep_score_prefers_tier1():
    meta = {
        "a": {"tier": "TIER_2_PROMISING_BUT_NEEDS_REVIEW", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
        "b": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.5", "min_coverage_1h": "0.95"},
    }
    assert _rep_score("a", meta) > _rep_score("b", meta)


def test_rep_score_prefers_low_turnover():
    meta = {
        "a": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.5", "min_coverage_1h": "0.99"},
        "b": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
    }
    assert _rep_score("a", meta) > _rep_score("b", meta)


def test_rep_score_prefers_high_coverage():
    meta = {
        "a": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.95"},
        "b": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
    }
    assert _rep_score("a", meta) > _rep_score("b", meta)


def test_rep_score_uses_alphabetical_tiebreak():
    meta = {
        "z_factor": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
        "a_factor": {"tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
    }
    assert _rep_score("a_factor", meta) < _rep_score("z_factor", meta)


def test_rep_score_no_pnl_or_returns():
    """_rep_score signature must not accept or use PnL/returns/IC/RankIC."""
    import inspect
    sig = inspect.signature(_rep_score)
    params = list(sig.parameters.keys())
    assert "pnl" not in params
    assert "returns" not in params
    assert "ic" not in params
    assert "rankic" not in params


# ─── find_redundancy_groups ───────────────────────────────────────────────

def test_groups_connected_component():
    pairs_s = [
        {"factor_i": "f0", "factor_j": "f1", "abs_spearman_corr": 0.90, "family_i": "a", "family_j": "a"},
        {"factor_i": "f1", "factor_j": "f2", "abs_spearman_corr": 0.87, "family_i": "a", "family_j": "b"},
        {"factor_i": "f0", "factor_j": "f3", "abs_spearman_corr": 0.20, "family_i": "a", "family_j": "c"},
        {"factor_i": "f0", "factor_j": "f2", "abs_spearman_corr": 0.50, "family_i": "a", "family_j": "b"},
        {"factor_i": "f1", "factor_j": "f3", "abs_spearman_corr": 0.10, "family_i": "a", "family_j": "c"},
        {"factor_i": "f2", "factor_j": "f3", "abs_spearman_corr": 0.05, "family_i": "b", "family_j": "c"},
    ]
    meta = {
        "f0": {"family": "a", "tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
        "f1": {"family": "a", "tier": "TIER_2_PROMISING_BUT_NEEDS_REVIEW", "max_turnover_1h": "0.3", "min_coverage_1h": "0.98"},
        "f2": {"family": "b", "tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.2", "min_coverage_1h": "0.97"},
        "f3": {"family": "c", "tier": "TIER_1_STABLE_DIAGNOSTIC", "max_turnover_1h": "0.1", "min_coverage_1h": "0.99"},
    }
    groups = find_redundancy_groups(pairs_s, [], ["f0", "f1", "f2", "f3"], meta)
    assert len(groups) == 1
    assert set(groups[0]["factors"].split("; ")) == {"f0", "f1", "f2"}
    # f0 is TIER_1, turnover 0.1, coverage 0.99 → best
    assert groups[0]["representative_candidate"] == "f0"


def test_groups_no_alpha_fields():
    groups = find_redundancy_groups([], [], FACTOR_IDS[:5], META)
    for g in groups:
        for key in g:
            for forbidden in ["alpha", "trade", "pnl", "deploy"]:
                assert forbidden not in key.lower()


# ─── Family summary: same-family only ──────────────────────────────────────

def test_family_summary_same_family_only():
    """family_redundancy_summary_from_pairwise must only use same_family == True pairs."""
    from analyze_factor_redundancy import family_redundancy_summary_from_pairwise
    # Create a pairwise DataFrame with mixed same/cross family
    rows = [
        {"factor_i": "a1", "factor_j": "a2", "family_i": "alpha", "family_j": "alpha", "same_family": True,
         "abs_spearman_corr": 0.90, "redundancy_level": "HIGH_REDUNDANCY"},
        {"factor_i": "a1", "factor_j": "b1", "family_i": "alpha", "family_j": "beta", "same_family": False,
         "abs_spearman_corr": 0.95, "redundancy_level": "NEAR_DUPLICATE"},
    ]
    df = pd.DataFrame(rows)
    result = family_redundancy_summary_from_pairwise(df)
    assert len(result) == 1  # only alpha family (beta is cross-family)
    assert result[0]["family"] == "alpha"
    assert result[0]["n_pairs"] == 1


def test_family_summary_n_pairs_equals_choose2():
    """n_pairs must equal n_factors choose 2."""
    from analyze_factor_redundancy import family_redundancy_summary_from_pairwise
    # 3 factors → 3 pairs
    rows = [
        {"factor_i": "a", "factor_j": "b", "family_i": "f", "family_j": "f", "same_family": True,
         "abs_spearman_corr": 0.5, "redundancy_level": "LOW_REDUNDANCY"},
        {"factor_i": "a", "factor_j": "c", "family_i": "f", "family_j": "f", "same_family": True,
         "abs_spearman_corr": 0.6, "redundancy_level": "LOW_REDUNDANCY"},
        {"factor_i": "b", "factor_j": "c", "family_i": "f", "family_j": "f", "same_family": True,
         "abs_spearman_corr": 0.7, "redundancy_level": "MODERATE_REDUNDANCY"},
    ]
    df = pd.DataFrame(rows)
    result = family_redundancy_summary_from_pairwise(df)
    assert result[0]["n_pairs"] == 3
    assert result[0]["n_factors"] == 3


# ─── Output CSV validation ────────────────────────────────────────────────

def test_static_pairwise_csv_351():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_static_pairwise_correlation.csv"
    if not csv_path.exists():
        pytest.skip("Static pairwise CSV not found")
    df = pd.read_csv(csv_path)
    assert len(df) == 351
    required = {"factor_i", "factor_j", "spearman_corr", "abs_spearman_corr", "redundancy_level", "same_family"}
    assert required.issubset(set(df.columns))


def test_dynamic_pairwise_csv_351():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_dynamic_pairwise_correlation.csv"
    if not csv_path.exists():
        pytest.skip("Dynamic pairwise CSV not found")
    df = pd.read_csv(csv_path)
    assert len(df) == 351


def test_redundancy_groups_csv_no_forbidden_fields():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_redundancy_groups.csv"
    if not csv_path.exists():
        pytest.skip("Groups CSV not found")
    df = pd.read_csv(csv_path)
    for col in df.columns:
        for forbidden in ["alpha", "pnl", "trade", "deploy"]:
            assert forbidden not in col.lower()


def test_family_summary_csv_same_family():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_family_redundancy_summary.csv"
    if not csv_path.exists():
        pytest.skip("Family summary CSV not found")
    df = pd.read_csv(csv_path)
    # momentum has 3 factors → 3 pairs
    mom = df[df["family"] == "momentum"]
    if len(mom) > 0:
        assert mom.iloc[0]["n_pairs"] == 3
    # quote_volume_liquidity has 2 factors → 1 pair
    qvol = df[df["family"] == "quote_volume_liquidity"]
    if len(qvol) > 0:
        assert qvol.iloc[0]["n_pairs"] == 1
