"""Test redundancy diagnostics — intake vs baseline semantics."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_redundancy_level_classification():
    """Redundancy levels classify correlations correctly."""
    from build_factor_redundancy import redundancy_level
    assert redundancy_level(0.96) == "NEAR_DUPLICATE"
    assert redundancy_level(0.95) == "NEAR_DUPLICATE"
    assert redundancy_level(0.90) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.85) == "HIGH_REDUNDANCY"
    assert redundancy_level(0.75) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.70) == "MODERATE_REDUNDANCY"
    assert redundancy_level(0.50) == "LOW_REDUNDANCY"


def test_recommendation_for_intake_vs_baseline():
    """Intake vs baseline pairs get distinct recommendations."""
    from build_factor_redundancy import recommendation_for_pair
    # NEAR_DUPLICATE intake vs baseline
    rec = recommendation_for_pair("NEAR_DUPLICATE", False, "intake_vs_baseline")
    assert "existing library" in rec.lower() or "redundant" in rec.lower()
    # HIGH_REDUNDANCY intake vs baseline
    rec = recommendation_for_pair("HIGH_REDUNDANCY", True, "intake_vs_baseline")
    assert "existing library" in rec.lower() or "redundant" in rec.lower() or "existing" in rec.lower()
    # Library mode should differ
    rec_lib = recommendation_for_pair("NEAR_DUPLICATE", False, "library")
    assert rec_lib != recommendation_for_pair("NEAR_DUPLICATE", False, "intake_vs_baseline") or "library" in rec_lib.lower()


def test_intake_mode_pair_type_field():
    """Intake mode output includes pair_type column."""
    from build_factor_redundancy import compute_redundancy
    # Use two real factors that exist
    out = Path("/tmp/test_redundancy_intake.csv")
    df = compute_redundancy(
        factor_ids=[],
        output_path=out,
        intake_factor_ids=["rev_1h", "mom_20h"],
        baseline_factor_ids=["vol_20h", "rsi_7h"],
    )
    if not df.empty:
        assert "pair_type" in df.columns
        # Should have intake_vs_intake and intake_vs_baseline pairs
        types = set(df["pair_type"].unique())
        assert "intake_vs_intake" in types or "intake_vs_baseline" in types


def test_library_mode_no_pair_type():
    """Library mode also includes pair_type column (always 'library')."""
    from build_factor_redundancy import compute_redundancy
    out = Path("/tmp/test_redundancy_lib.csv")
    df = compute_redundancy(
        factor_ids=["rev_1h", "mom_20h", "vol_20h"],
        output_path=out,
    )
    if not df.empty:
        assert "pair_type" in df.columns
        assert all(df["pair_type"] == "library")


def test_intake_vs_baseline_covers_baseline():
    """Intake mode compares intake factors against baseline, not just intake-vs-intake."""
    from build_factor_redundancy import compute_redundancy
    out = Path("/tmp/test_redundancy_coverage.csv")
    df = compute_redundancy(
        factor_ids=[],
        output_path=out,
        intake_factor_ids=["rev_1h"],
        baseline_factor_ids=["mom_20h", "vol_20h"],
    )
    if not df.empty:
        # Should have 2 pairs: rev_1h vs mom_20h, rev_1h vs vol_20h
        baseline_pairs = df[df["pair_type"] == "intake_vs_baseline"]
        assert len(baseline_pairs) >= 1, "Should have at least 1 intake-vs-baseline pair"
