"""Phase 7F: tests for analyze_factor_redundancy.py"""
from __future__ import annotations

import itertools
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
    NEAR_DUPLICATE,
    HIGH_REDUNDANCY,
    MODERATE_REDUNDANCY,
)

# ─── Fixtures ──────────────────────────────────────────────────────────────

FACTOR_IDS = [f"f{i}" for i in range(27)]
META = {fid: {"family": f"fam{i%5}", "tier": "TIER_1_STABLE_DIAGNOSTIC"} for i, fid in enumerate(FACTOR_IDS)}


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


def test_pairwise_needs_minimum_obs():
    wide = pd.DataFrame({
        "timestamp": list(range(10)),
        "symbol": ["X"] * 10,
        "f0": list(range(10)),
        "f1": list(range(10)),
    })
    meta = {"f0": {"family": "a"}, "f1": {"family": "b"}}
    pairs = compute_pairwise(wide, ["f0", "f1"], meta)
    assert len(pairs) == 1
    assert pairs[0]["redundancy_level"] == "INSUFFICIENT_DATA"  # n=10 < 30 threshold
    wide2 = pd.DataFrame({
        "timestamp": list(range(50)),
        "symbol": ["X"] * 50,
        "f0": list(range(50)),
        "f1": list(range(50)),
    })
    pairs2 = compute_pairwise(wide2, ["f0", "f1"], meta)
    assert pairs2[0]["spearman_corr"] is not None
    assert abs(pairs2[0]["spearman_corr"] - 1.0) < 0.01  # perfect correlation


# ─── find_redundancy_groups ───────────────────────────────────────────────

def test_groups_no_pnl_or_returns():
    """representative_candidate must not use PnL or returns."""
    pairs_s = [
        {"factor_i": "f0", "factor_j": "f1", "abs_spearman_corr": 0.90, "family_i": "a", "family_j": "a"},
    ]
    pairs_d = [
        {"factor_i": "f0", "factor_j": "f1", "abs_spearman_corr": 0.88, "family_i": "a", "family_j": "a"},
    ]
    meta = {"f0": {"family": "a", "tier": "TIER_2_PROMISING_BUT_NEEDS_REVIEW"}, "f1": {"family": "a", "tier": "TIER_1_STABLE_DIAGNOSTIC"}}
    groups = find_redundancy_groups(pairs_s, pairs_d, ["f0", "f1"], meta)
    assert len(groups) == 1
    # Representative should be f1 (TIER_1 preferred)
    assert groups[0]["representative_candidate"] == "f1"


def test_groups_no_alpha_fields():
    """No alpha/tradeable/deploy fields in group output."""
    groups = find_redundancy_groups([], [], FACTOR_IDS[:5], META)
    for g in groups:
        for key in g:
            assert "alpha" not in key.lower()
            assert "trade" not in key.lower()
            assert "pnl" not in key.lower()
            assert "deploy" not in key.lower()


def test_groups_connected_component():
    """f0-f1 high corr, f1-f2 high corr, f3 isolated -> one group of 3."""
    pairs_s = [
        {"factor_i": "f0", "factor_j": "f1", "abs_spearman_corr": 0.90, "family_i": "a", "family_j": "a"},
        {"factor_i": "f1", "factor_j": "f2", "abs_spearman_corr": 0.87, "family_i": "a", "family_j": "b"},
        {"factor_i": "f0", "factor_j": "f3", "abs_spearman_corr": 0.20, "family_i": "a", "family_j": "c"},
        {"factor_i": "f0", "factor_j": "f2", "abs_spearman_corr": 0.50, "family_i": "a", "family_j": "b"},
        {"factor_i": "f1", "factor_j": "f3", "abs_spearman_corr": 0.10, "family_i": "a", "family_j": "c"},
        {"factor_i": "f2", "factor_j": "f3", "abs_spearman_corr": 0.05, "family_i": "b", "family_j": "c"},
    ]
    meta = {"f0": {"family": "a", "tier": "TIER_1_STABLE_DIAGNOSTIC"}, "f1": {"family": "a", "tier": "TIER_2_PROMISING_BUT_NEEDS_REVIEW"},
            "f2": {"family": "b", "tier": "TIER_1_STABLE_DIAGNOSTIC"}, "f3": {"family": "c", "tier": "TIER_1_STABLE_DIAGNOSTIC"}}
    groups = find_redundancy_groups(pairs_s, [], ["f0", "f1", "f2", "f3"], meta)
    assert len(groups) == 1
    assert set(groups[0]["factors"].split("; ")) == {"f0", "f1", "f2"}


# ─── Output CSV validation ────────────────────────────────────────────────

def test_static_pairwise_csv_exists_and_351():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_static_pairwise_correlation.csv"
    if not csv_path.exists():
        pytest.skip("Static pairwise CSV not found (run analysis first)")
    df = pd.read_csv(csv_path)
    assert len(df) == 351
    required = {"factor_i", "factor_j", "spearman_corr", "abs_spearman_corr", "redundancy_level", "same_family"}
    assert required.issubset(set(df.columns))


def test_dynamic_pairwise_csv_exists_and_351():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_dynamic_pairwise_correlation.csv"
    if not csv_path.exists():
        pytest.skip("Dynamic pairwise CSV not found (run analysis first)")
    df = pd.read_csv(csv_path)
    assert len(df) == 351


def test_redundancy_groups_csv():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_redundancy_groups.csv"
    if not csv_path.exists():
        pytest.skip("Redundancy groups CSV not found")
    df = pd.read_csv(csv_path)
    assert "representative_candidate" in df.columns
    assert "group_id" in df.columns
    # No alpha/PnL columns
    for col in df.columns:
        assert "alpha" not in col.lower()
        assert "pnl" not in col.lower()


def test_family_summary_csv():
    csv_path = ROOT / "research/factor_runs/crypto_top50_factor_library/phase7f_family_redundancy_summary.csv"
    if not csv_path.exists():
        pytest.skip("Family summary CSV not found")
    df = pd.read_csv(csv_path)
    assert "redundancy_assessment" in df.columns
    assert "max_abs_spearman_static" in df.columns
