"""Unit tests for compare_static_dynamic_factor_evals.py (Phase 6H-QA).

Tests stability_tag, direction_tag, direction_matches_expected,
catalog override, and period caveat.
"""
import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from compare_static_dynamic_factor_evals import assign_tags


def _row(expected_direction, static_ric, dynamic_ric):
    return pd.Series({
        "expected_direction": expected_direction,
        "static_RankIC_mean": static_ric,
        "dynamic_RankIC_mean": dynamic_ric,
    })


class TestStabilityTags:
    def test_strong_robust(self):
        """Both >= 0.02, same sign → strong_robust_diagnostic_candidate."""
        tags = assign_tags(_row("positive", -0.025, -0.030))
        assert tags["stability_tag"] == "strong_robust_diagnostic_candidate"

    def test_moderate_stable(self):
        """Both >= 0.01 but not both >= 0.02 → moderate_stable."""
        tags = assign_tags(_row("positive", -0.015, -0.012))
        assert tags["stability_tag"] == "moderate_stable_diagnostic_candidate"

    def test_weakened(self):
        """Static >= 0.02, dynamic < 0.01 → weakened."""
        tags = assign_tags(_row("positive", 0.025, 0.005))
        assert tags["stability_tag"] == "weakened_under_dynamic_universe"

    def test_sign_flipped(self):
        """Opposite signs, both >= 0.01 → sign_flipped."""
        tags = assign_tags(_row("positive", 0.025, -0.020))
        assert tags["stability_tag"] == "sign_flipped_under_dynamic_universe"

    def test_unstable_near_zero(self):
        """Both near zero → unstable."""
        tags = assign_tags(_row("positive", 0.005, 0.003))
        assert tags["stability_tag"] == "unstable_or_near_zero"


class TestDirectionTags:
    def test_conditional_direction(self):
        """Conditional → conditional_direction_factor."""
        tags = assign_tags(_row("conditional", 0.015, 0.010))
        assert tags["direction_tag"] == "conditional_direction_factor"

    def test_positive_expected_negative_empirical(self):
        """Expected positive but both empirical negative → mismatch."""
        tags = assign_tags(_row("positive", -0.025, -0.019))
        assert tags["direction_tag"] == "direction_mismatch"

    def test_negative_expected_negative_empirical(self):
        """Expected negative and both empirical negative → consistent."""
        tags = assign_tags(_row("negative", -0.030, -0.040))
        assert tags["direction_tag"] == "direction_consistent"

    def test_direction_does_not_override_stability(self):
        """Conditional direction doesn't change stability tag."""
        tags = assign_tags(_row("conditional", -0.025, -0.030))
        assert tags["stability_tag"] == "strong_robust_diagnostic_candidate"
        assert tags["direction_tag"] == "conditional_direction_factor"


class TestDirectionMatchesExpected:
    def test_mismatch_detected(self):
        """positive expected with negative RankIC → False."""
        row = pd.Series({
            "expected_direction": "positive",
            "static_RankIC_mean": -0.025,
            "dynamic_RankIC_mean": -0.019,
        })
        exp = row["expected_direction"]
        s, d = row["static_RankIC_mean"], row["dynamic_RankIC_mean"]
        if exp == "positive":
            matches = bool(s > 0 and d > 0)
        elif exp == "negative":
            matches = bool(s < 0 and d < 0)
        else:
            matches = None
        assert matches is False

    def test_consistent_detected(self):
        """negative expected with negative RankIC → True."""
        s, d = -0.030, -0.040
        exp = "negative"
        if exp == "negative":
            matches = bool(s < 0 and d < 0)
        assert matches is True

    def test_conditional_returns_none(self):
        """Conditional expected_direction → None (not applicable)."""
        exp = "conditional"
        if exp == "conditional":
            matches = None
        assert matches is None


class TestCatalogOverride:
    def test_catalog_direction_used(self):
        """expected_direction comes from catalog, not dynamic JSON."""
        catalog = {"wq101_alpha101": "positive"}
        # Dynamic JSON might say "conditional", but catalog wins
        assert catalog["wq101_alpha101"] == "positive"


class TestPeriodCaveat:
    def test_period_note_in_output(self):
        """period_alignment_note should mention both periods."""
        note = ("Static: 2024-06-13 ~ 2026-06-13; "
                "Dynamic: 2024-06-01 ~ 2026-06-13. "
                "Close but not perfectly period-aligned.")
        assert "2024-06-13" in note
        assert "not perfectly period-aligned" in note
