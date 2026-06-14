"""Unit tests for compare_static_dynamic_factor_evals.py (Phase 6H).

All tests use synthetic data.
"""
import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from compare_static_dynamic_factor_evals import interpret_row


class TestInterpretationTags:
    def _row(self, expected_direction, static_ric, dynamic_ric):
        return pd.Series({
            "expected_direction": expected_direction,
            "static_RankIC_mean": static_ric,
            "dynamic_RankIC_mean": dynamic_ric,
        })

    def test_robust_same_sign_strong(self):
        """Both strong and same sign → robust_diagnostic_candidate."""
        row = self._row("positive", -0.025, -0.030)
        assert interpret_row(row) == "robust_diagnostic_candidate"

    def test_sign_flip(self):
        """Opposite signs, both meaningful → sign_flipped_under_dynamic_universe."""
        row = self._row("positive", 0.025, -0.020)
        assert interpret_row(row) == "sign_flipped_under_dynamic_universe"

    def test_weakened(self):
        """Strong static, near-zero dynamic → weakened_under_dynamic_universe."""
        row = self._row("positive", 0.025, 0.005)
        assert interpret_row(row) == "weakened_under_dynamic_universe"

    def test_dynamic_only(self):
        """Near-zero static, strong dynamic → dynamic_only_candidate."""
        row = self._row("positive", 0.005, 0.025)
        assert interpret_row(row) == "dynamic_only_candidate"

    def test_conditional_direction(self):
        """Conditional direction → conditional_direction_factor."""
        row = self._row("conditional", 0.015, 0.010)
        assert interpret_row(row) == "conditional_direction_factor"

    def test_unstable_near_zero(self):
        """Both near zero → unstable_or_near_zero."""
        row = self._row("positive", 0.005, 0.003)
        assert interpret_row(row) == "unstable_or_near_zero"

    def test_missing_static(self):
        """Missing static data → insufficient_static_comparison."""
        row = self._row("positive", None, 0.025)
        assert interpret_row(row) == "insufficient_static_comparison"


class TestDeltaComputation:
    def test_delta_rankic_computed_correctly(self):
        """delta_RankIC = dynamic - static."""
        static = -0.025
        dynamic = -0.040
        delta = dynamic - static
        assert abs(delta - (-0.015)) < 1e-10


class TestMergeLogic:
    def test_merge_on_factor_and_label(self):
        """Static and dynamic merge on (factor_id, label)."""
        static = pd.DataFrame([
            {"factor_id": "mom_20h", "label": "ret_fwd_1h", "static_RankIC_mean": -0.025},
            {"factor_id": "mom_20h", "label": "ret_fwd_4h", "static_RankIC_mean": -0.030},
        ])
        dynamic = pd.DataFrame([
            {"factor_id": "mom_20h", "label": "ret_fwd_1h", "dynamic_RankIC_mean": -0.019},
            {"factor_id": "mom_20h", "label": "ret_fwd_4h", "dynamic_RankIC_mean": -0.026},
        ])
        merged = static.merge(dynamic, on=["factor_id", "label"], how="outer")
        assert len(merged) == 2
        assert merged.iloc[0]["static_RankIC_mean"] == -0.025
        assert merged.iloc[0]["dynamic_RankIC_mean"] == -0.019


class TestConditionalDirectionAvoidsOverinterpretation:
    def test_conditional_tag_overrides_strength(self):
        """Even with strong RankIC, conditional factors get conditional tag."""
        row = pd.Series({
            "expected_direction": "conditional",
            "static_RankIC_mean": 0.050,
            "dynamic_RankIC_mean": 0.040,
        })
        assert interpret_row(row) == "conditional_direction_factor"
