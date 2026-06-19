"""Tests for consistency module using toy data."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from momentum.signal_evaluation.consistency import (
    check_rankic_spread_consistency,
    CONSISTENT_POSITIVE,
    CONSISTENT_NEGATIVE,
    DIRECTION_CONFLICT,
    WEAK_SIGNAL,
)


class TestConsistency:
    def test_consistent_positive(self):
        ic = {"mean_rank_ic": 0.03}
        sp = {"mean_spread": 0.005}
        assert check_rankic_spread_consistency(ic, sp) == CONSISTENT_POSITIVE

    def test_consistent_negative(self):
        ic = {"mean_rank_ic": -0.03}
        sp = {"mean_spread": -0.005}
        assert check_rankic_spread_consistency(ic, sp) == CONSISTENT_NEGATIVE

    def test_direction_conflict_ic_pos_spread_neg(self):
        ic = {"mean_rank_ic": 0.03}
        sp = {"mean_spread": -0.005}
        assert check_rankic_spread_consistency(ic, sp) == DIRECTION_CONFLICT

    def test_direction_conflict_ic_neg_spread_pos(self):
        ic = {"mean_rank_ic": -0.03}
        sp = {"mean_spread": 0.005}
        assert check_rankic_spread_consistency(ic, sp) == DIRECTION_CONFLICT

    def test_weak_signal_both_near_zero(self):
        ic = {"mean_rank_ic": 0.0}
        sp = {"mean_spread": 0.0}
        assert check_rankic_spread_consistency(ic, sp) == WEAK_SIGNAL

    def test_weak_signal_one_near_zero(self):
        ic = {"mean_rank_ic": 0.03}
        sp = {"mean_spread": 0.0}
        result = check_rankic_spread_consistency(ic, sp)
        assert result in [WEAK_SIGNAL, CONSISTENT_POSITIVE]

    def test_custom_threshold(self):
        ic = {"mean_rank_ic": 0.001}
        sp = {"mean_spread": 0.001}
        # With high threshold, both are "near zero"
        result = check_rankic_spread_consistency(ic, sp, threshold=0.01)
        assert result == WEAK_SIGNAL

    def test_missing_keys_default_zero(self):
        ic = {}
        sp = {}
        assert check_rankic_spread_consistency(ic, sp) == WEAK_SIGNAL
