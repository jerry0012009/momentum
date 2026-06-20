"""Test factor redundancy diagnostics."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_redundancy_level_classification():
    """redundancy_level() classifies correlations correctly."""
    from build_factor_redundancy import redundancy_level
    assert redundancy_level(0.96) == "NEAR_DUPLICATE"
    assert redundancy_level(0.95) == "NEAR_DUPLICATE"
    assert redundancy_level(0.90) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.85) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.80) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.70) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.50) == "LOW_REDUNDANCY"
    assert redundancy_level(0.0) == "LOW_REDUNDANCY"


def test_redundancy_level_boundary_values():
    """Boundary values should be classified correctly."""
    from build_factor_redundancy import redundancy_level
    # Exactly at threshold = that level
    assert redundancy_level(0.95) == "NEAR_DUPLICATE"
    assert redundancy_level(0.949) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.85) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.849) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.70) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.699) == "LOW_REDUNDANCY"


def test_recommendation_for_pair():
    """recommendation_for_pair returns appropriate text."""
    from build_factor_redundancy import recommendation_for_pair
    rec = recommendation_for_pair("NEAR_DUPLICATE", True)
    assert "Drop" in rec
    rec = recommendation_for_pair("HIGH_REDUNDANCY", True)
    assert "Same-family" in rec
    rec = recommendation_for_pair("HIGH_REDUNDANCY", False)
    assert "Cross-family" in rec
    rec = recommendation_for_pair("LOW_REDUNDANCY", False)
    assert "Low redundancy" in rec


def test_compute_redundancy_with_real_data():
    """build_factor_redundancy works with real factor_values."""
    from build_factor_redundancy import compute_redundancy
    output_path = Path("/tmp/test_redundancy.csv")
    df = compute_redundancy(["rev_1h", "mom_72h", "vol_5h"], output_path)
    assert len(df) == 3  # 3 pairs from 3 factors
    assert "factor_i" in df.columns
    assert "redundancy_level" in df.columns
    assert "spearman_corr" in df.columns
    # Cleanup
    output_path.unlink(missing_ok=True)
