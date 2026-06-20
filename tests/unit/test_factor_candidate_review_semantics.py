"""Test candidate review semantics — DIVERGENT factors not labeled STRONG."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"


def test_divergent_not_strong():
    """DIVERGENT factors should not be STRONG_DIAGNOSTIC_CANDIDATE."""
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if not review_path.exists():
        pytest.skip("Candidate review not available")
    df = pd.read_csv(review_path)
    divergent = df[df["rankic_longshort_consistency"] == "DIVERGENT"]
    for _, row in divergent.iterrows():
        bucket = row["review_bucket"]
        assert bucket != "STRONG_DIAGNOSTIC_CANDIDATE", (
            f"{row['factor_name']} is DIVERGENT but labeled STRONG_DIAGNOSTIC_CANDIDATE. "
            f"Should be DIRECTION_REVIEW_REQUIRED or TAIL_OR_MONOTONICITY_REVIEW_REQUIRED."
        )


def test_review_bucket_values():
    """All review_bucket values should be from the known set."""
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if not review_path.exists():
        pytest.skip("Candidate review not available")
    df = pd.read_csv(review_path)
    valid_buckets = {
        "MISSING_INPUT",
        "ACTIVE_IN_SIGNAL_REVIEW",
        "CONDITIONAL_DIRECTION_REVIEW",
        "DIRECTION_REVIEW_REQUIRED",
        "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED",
        "STRONG_DIAGNOSTIC_CANDIDATE",
        "RANKIC_STRONG_LONGSHORT_WEAK",
        "LONGSHORT_STRONG_RANKIC_WEAK",
        "WEAK_OR_NOISY",
        "METADATA_REVIEW",
    }
    for _, row in df.iterrows():
        bucket = row["review_bucket"]
        assert bucket in valid_buckets, (
            f"{row['factor_name']} has unknown review_bucket: {bucket}"
        )


def test_strong_candidates_are_consistent():
    """STRONG_DIAGNOSTIC_CANDIDATE factors should have CONSISTENT or N/A consistency."""
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if not review_path.exists():
        pytest.skip("Candidate review not available")
    df = pd.read_csv(review_path)
    strong = df[df["review_bucket"] == "STRONG_DIAGNOSTIC_CANDIDATE"]
    for _, row in strong.iterrows():
        cons = row["rankic_longshort_consistency"]
        assert cons in ("CONSISTENT", "N/A"), (
            f"{row['factor_name']} is STRONG_DIAGNOSTIC_CANDIDATE but consistency={cons}. "
            f"Should be CONSISTENT or N/A."
        )


def test_missing_input_factors_have_correct_bucket():
    """Factors with missing factor_values should have MISSING_INPUT bucket."""
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if not review_path.exists():
        pytest.skip("Candidate review not available")
    df = pd.read_csv(review_path)
    missing = df[df["status"] == "MISSING_FACTOR_VALUES"]
    for _, row in missing.iterrows():
        assert row["review_bucket"] == "MISSING_INPUT", (
            f"{row['factor_name']} has missing FV but bucket={row['review_bucket']}"
        )


def test_signal_factors_have_correct_bucket():
    """Active signal factors should have ACTIVE_IN_SIGNAL_REVIEW bucket."""
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if not review_path.exists():
        pytest.skip("Candidate review not available")
    df = pd.read_csv(review_path)
    signal = df[df["used_in_current_signal"] == True]
    for _, row in signal.iterrows():
        assert row["review_bucket"] == "ACTIVE_IN_SIGNAL_REVIEW", (
            f"{row['factor_name']} is in signal but bucket={row['review_bucket']}"
        )
