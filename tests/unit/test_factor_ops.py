"""Unit tests for factor_ops.py — pure-function building blocks."""
import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from factor_ops import (
    delay, delta, rolling_mean, rolling_std, rolling_min, rolling_max,
    rolling_corr, ts_rank, zscore, signed_power, ema, true_range,
)


# ── Helpers ─────────────────────────────────────────────────────────

def _series(data):
    return pd.Series(data, dtype=float)


# ── delay / delta ───────────────────────────────────────────────────

class TestDelay:
    def test_basic(self):
        s = _series([10, 20, 30, 40])
        result = delay(s, 1)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == 10
        assert result.iloc[3] == 30

    def test_delay_2(self):
        s = _series([10, 20, 30, 40, 50])
        result = delay(s, 2)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == 10
        assert result.iloc[4] == 30

    def test_no_future(self):
        """delay should only access past values, not future."""
        s = _series([1, 2, 3, 4, 5])
        result = delay(s, 1)
        for i in range(len(s)):
            if i == 0:
                assert np.isnan(result.iloc[i])
            else:
                assert result.iloc[i] == s.iloc[i - 1]


class TestDelta:
    def test_basic(self):
        s = _series([10, 15, 20, 25])
        result = delta(s, 1)
        assert np.isnan(result.iloc[0])
        assert result.iloc[1] == 5
        assert result.iloc[3] == 5

    def test_delta_2(self):
        s = _series([10, 15, 20, 25, 30])
        result = delta(s, 2)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == 10  # 20 - 10
        assert result.iloc[4] == 10  # 30 - 20


# ── Rolling stats ───────────────────────────────────────────────────

class TestRollingMean:
    def test_basic(self):
        s = _series([1, 2, 3, 4, 5])
        result = rolling_mean(s, 3)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == pytest.approx(2.0)
        assert result.iloc[4] == pytest.approx(4.0)


class TestRollingStd:
    def test_basic(self):
        s = _series([1, 1, 1, 1, 5])
        result = rolling_std(s, 3)
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        assert result.iloc[2] == pytest.approx(0.0)
        assert result.iloc[4] > 0


class TestRollingMinMax:
    def test_min(self):
        s = _series([5, 3, 1, 4, 2])
        result = rolling_min(s, 3)
        assert np.isnan(result.iloc[0])
        assert result.iloc[2] == 1
        assert result.iloc[4] == 1

    def test_max(self):
        s = _series([5, 3, 1, 4, 2])
        result = rolling_max(s, 3)
        assert np.isnan(result.iloc[0])
        assert result.iloc[2] == 5
        assert result.iloc[4] == 4


class TestRollingCorr:
    def test_perfect_corr(self):
        x = _series([1, 2, 3, 4, 5])
        y = _series([2, 4, 6, 8, 10])
        result = rolling_corr(x, y, 5)
        assert result.iloc[4] == pytest.approx(1.0)

    def test_negative_corr(self):
        x = _series([1, 2, 3, 4, 5])
        y = _series([10, 8, 6, 4, 2])
        result = rolling_corr(x, y, 5)
        assert result.iloc[4] == pytest.approx(-1.0)


# ── ts_rank ─────────────────────────────────────────────────────────

class TestTsRank:
    def test_monotonic(self):
        s = _series([1, 2, 3, 4, 5])
        result = ts_rank(s, 5)
        assert result.iloc[4] == pytest.approx(1.0)  # max rank

    def test_constant(self):
        s = _series([5, 5, 5, 5, 5])
        result = ts_rank(s, 5)
        # All equal → rank(pct=True) returns average rank / n = 3/5 = 0.6
        assert result.iloc[4] == pytest.approx(0.6)


# ── zscore ──────────────────────────────────────────────────────────

class TestZscore:
    def test_mean_zero(self):
        # zscore of the mean value of the window should be 0
        # window [10,20,30,40,25] → mean=25, last=25 → z=0
        s = _series([10, 20, 30, 40, 25])
        result = zscore(s, 5)
        assert result.iloc[4] == pytest.approx(0.0, abs=1e-10)

    def test_constant_zero_std(self):
        s = _series([5, 5, 5, 5])
        result = zscore(s, 4)
        # Constant → std=0 → NaN
        assert np.isnan(result.iloc[3])


# ── signed_power ────────────────────────────────────────────────────

class TestSignedPower:
    def test_positive(self):
        s = _series([4, -4, 0])
        result = signed_power(s, 0.5)
        assert result.iloc[0] == pytest.approx(2.0)
        assert result.iloc[1] == pytest.approx(-2.0)
        assert result.iloc[2] == pytest.approx(0.0)

    def test_preserves_sign(self):
        s = _series([-8, 8])
        result = signed_power(s, 1 / 3)
        assert result.iloc[0] < 0
        assert result.iloc[1] > 0


# ── ema ─────────────────────────────────────────────────────────────

class TestEma:
    def test_converges(self):
        s = pd.Series([1.0] * 100)
        result = ema(s, 10)
        assert result.iloc[99] == pytest.approx(1.0)

    def test_responds_to_change(self):
        s = pd.Series([1.0] * 50 + [2.0] * 50)
        result = ema(s, 10)
        # After 50 bars at 2.0, EMA should be close to 2.0
        assert result.iloc[99] > 1.9


# ── true_range ──────────────────────────────────────────────────────

class TestTrueRange:
    def test_basic(self):
        h = _series([12, 15, 14])
        l = _series([10, 11, 12])
        c = _series([11, 13, 13])
        result = true_range(h, l, c)
        # TR[0] = NaN because prev_close is unavailable
        assert np.isnan(result.iloc[0])
        # TR[1] = max(15-11, |15-11|, |11-11|) = max(4, 4, 0) = 4
        assert result.iloc[1] == pytest.approx(4.0)
        # TR[2] = max(14-12, |14-13|, |12-13|) = max(2, 1, 1) = 2
        assert result.iloc[2] == pytest.approx(2.0)

    def test_always_positive(self):
        h = _series([10, 10, 10])
        l = _series([10, 10, 10])
        c = _series([10, 10, 10])
        result = true_range(h, l, c)
        assert np.isnan(result.iloc[0])  # first row NaN
        assert result.iloc[1] >= 0
        assert result.iloc[2] >= 0
