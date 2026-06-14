"""Phase 7I-E: curated library v0.3 validation tests."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"

BATCH2_IDS = {
    "ema_12_26_gap", "rsi_28h", "rsi_7h", "williams_r_14h",
    "downside_vol_20h", "vol_of_vol_20h", "mom_accel_20h",
    "qvol_ma_ratio_5_20", "ma_gap_20_80",
}

BANNED = {"ALPHA", "CANDIDATE_REVIEW", "TRADEABLE", "LIVE", "DEPLOY"}

@pytest.fixture
def b2():
    return pd.read_csv(RUN / "phase7i_e_curated_batch2_library.csv")

@pytest.fixture
def v03():
    return pd.read_csv(RUN / "phase7i_e_curated_factor_library_v0_3.csv")

@pytest.fixture
def fam():
    return pd.read_csv(RUN / "phase7i_e_family_catalog_summary_v0_3.csv")

@pytest.fixture
def rq():
    return pd.read_csv(RUN / "phase7i_e_redundancy_review_queue_v0_3.csv")

def test_batch2_curated_has_9_rows(b2):
    assert len(b2) == 9

def test_combined_v03_has_36_rows(v03):
    assert len(v03) == 36

def test_no_banned_status(b2, v03):
    for df, name in [(b2, "batch2"), (v03, "v03")]:
        for col in ["registry_status", "recommended_research_use", "diagnostic_tier"]:
            if col in df.columns:
                for val in df[col].dropna().unique():
                    for banned in BANNED:
                        assert banned not in str(val).upper(), f"{banned} found in {name}.{col}: {val}"

def test_batch2_ids_exactly_once(b2):
    assert set(b2["factor_id"]) == BATCH2_IDS
    assert b2["factor_id"].nunique() == 9

def test_redundancy_groups_mapped(b2):
    rg = b2[b2["redundancy_group_id"].notna()]
    assert len(rg) == 4  # ema_12_26_gap, rsi_28h (RG_B2_1); rsi_7h, williams_r_14h (RG_B2_2)
    reps = rg[rg["redundancy_role"] == "REPRESENTATIVE_CANDIDATE"]
    assert len(reps) == 2
    members = rg[rg["redundancy_role"] == "REDUNDANT_GROUP_MEMBER"]
    assert len(members) == 2
    for _, r in rg.iterrows():
        assert r["representative_candidate_flag"] in ("YES", "NO")

def test_source_batch_values(b2, v03):
    assert (b2["source_batch"] == "PHASE_7I_BATCH2").all()
    b1_in_v03 = v03[v03["source_batch"] == "PHASE_7B_BATCH1"]
    b2_in_v03 = v03[v03["source_batch"] == "PHASE_7I_BATCH2"]
    assert len(b1_in_v03) == 27
    assert len(b2_in_v03) == 9

def test_family_summary_exists(fam):
    assert len(fam) >= 11  # at least 11 families
    assert "n_factors" in fam.columns
    assert "n_batch1" in fam.columns
    assert "n_batch2" in fam.columns

def test_redundancy_review_queue(rq):
    assert len(rq) >= 8  # 6 Batch-1 + 2 Batch-2
    allowed = {"KEEP_ALL_FOR_NOW", "REVIEW_DUPLICATE_FORMULAS", "REVIEW_DIRECTION_SYMMETRY",
               "REVIEW_LOOKBACK_REDUNDANCY", "REVIEW_CROSS_FAMILY_EQUIVALENCE"}
    for val in rq["recommended_review"]:
        assert val in allowed, f"Unexpected review: {val}"
