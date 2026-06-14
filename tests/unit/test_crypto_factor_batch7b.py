"""Unit tests for Phase 7B factor batch (27 factors).

Tests verify:
- All 27 selected_for_7B factors are in REGISTRY
- Each has complete FactorSpec metadata
- required_columns and lookback_window match candidate CSV
- expected_direction matches candidate CSV
- Formula correctness on synthetic data
- Rolling warmup produces NaN
- Zero denominator produces no inf
- Cross-sectional rank factors: per-symbol prep only, rank by caller
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "scripts"))
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID
from factor_specs import FactorSpec

# 27 selected_for_7B factors
SELECTED_7B = [
    "mom_5h", "mom_10h", "mom_40h",
    "rev_3h", "rev_10h", "rev_24h",
    "vol_5h", "vol_40h", "vol_ratio_5_20",
    "range_1h", "range_4h", "range_24h",
    "price_pos_24h", "price_pos_72h",
    "vol_zscore_20h", "vol_zscore_48h",
    "qvol_zscore_20h", "qvol_zscore_48h",
    "ma_gap_5_20", "ma_gap_10_40",
    "breakout_dist_20h", "breakout_dist_48h",
    "candle_body", "candle_wick_upper", "candle_wick_lower",
    "xs_rank_ret_1h", "xs_rank_vol",
]

# Expected metadata from candidate CSV
EXPECTED_META = {
    "mom_5h": {"family": "momentum", "required_columns": ["close"], "lookback_window": 5, "expected_direction": "positive"},
    "mom_10h": {"family": "momentum", "required_columns": ["close"], "lookback_window": 10, "expected_direction": "positive"},
    "mom_40h": {"family": "momentum", "required_columns": ["close"], "lookback_window": 40, "expected_direction": "positive"},
    "rev_3h": {"family": "reversal", "required_columns": ["close"], "lookback_window": 3, "expected_direction": "negative"},
    "rev_10h": {"family": "reversal", "required_columns": ["close"], "lookback_window": 10, "expected_direction": "negative"},
    "rev_24h": {"family": "reversal", "required_columns": ["close"], "lookback_window": 24, "expected_direction": "negative"},
    "vol_5h": {"family": "volatility", "required_columns": ["close"], "lookback_window": 6, "expected_direction": "negative"},
    "vol_40h": {"family": "volatility", "required_columns": ["close"], "lookback_window": 41, "expected_direction": "negative"},
    "vol_ratio_5_20": {"family": "volatility", "required_columns": ["close"], "lookback_window": 21, "expected_direction": "conditional"},
    "range_1h": {"family": "range_position", "required_columns": ["high", "low", "close"], "lookback_window": 1, "expected_direction": "conditional"},
    "range_4h": {"family": "range_position", "required_columns": ["high", "low", "close"], "lookback_window": 4, "expected_direction": "conditional"},
    "range_24h": {"family": "range_position", "required_columns": ["high", "low", "close"], "lookback_window": 24, "expected_direction": "conditional"},
    "price_pos_24h": {"family": "price_position", "required_columns": ["high", "low", "close"], "lookback_window": 24, "expected_direction": "conditional"},
    "price_pos_72h": {"family": "price_position", "required_columns": ["high", "low", "close"], "lookback_window": 72, "expected_direction": "conditional"},
    "vol_zscore_20h": {"family": "volume_liquidity", "required_columns": ["volume"], "lookback_window": 20, "expected_direction": "positive"},
    "vol_zscore_48h": {"family": "volume_liquidity", "required_columns": ["volume"], "lookback_window": 48, "expected_direction": "positive"},
    "qvol_zscore_20h": {"family": "quote_volume_liquidity", "required_columns": ["quote_volume"], "lookback_window": 20, "expected_direction": "positive"},
    "qvol_zscore_48h": {"family": "quote_volume_liquidity", "required_columns": ["quote_volume"], "lookback_window": 48, "expected_direction": "positive"},
    "ma_gap_5_20": {"family": "trend_ma", "required_columns": ["close"], "lookback_window": 20, "expected_direction": "positive"},
    "ma_gap_10_40": {"family": "trend_ma", "required_columns": ["close"], "lookback_window": 40, "expected_direction": "positive"},
    "breakout_dist_20h": {"family": "breakout", "required_columns": ["high", "low", "close"], "lookback_window": 20, "expected_direction": "positive"},
    "breakout_dist_48h": {"family": "breakout", "required_columns": ["high", "low", "close"], "lookback_window": 48, "expected_direction": "positive"},
    "candle_body": {"family": "intraday_candle", "required_columns": ["open", "high", "low", "close"], "lookback_window": 1, "expected_direction": "conditional"},
    "candle_wick_upper": {"family": "intraday_candle", "required_columns": ["open", "high", "low", "close"], "lookback_window": 1, "expected_direction": "negative"},
    "candle_wick_lower": {"family": "intraday_candle", "required_columns": ["open", "high", "low", "close"], "lookback_window": 1, "expected_direction": "positive"},
    "xs_rank_ret_1h": {"family": "cross_sectional_normalized", "required_columns": ["close"], "lookback_window": 2, "expected_direction": "conditional"},
    "xs_rank_vol": {"family": "cross_sectional_normalized", "required_columns": ["volume"], "lookback_window": 20, "expected_direction": "conditional"},
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 80, symbol: str = "BTCUSDT") -> pd.DataFrame:
    """Synthetic OHLCV with enough rows for all lookback windows."""
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0, 0.5, n))
    high = close + rng.uniform(0.5, 2.0, n)
    low = close - rng.uniform(0.5, 2.0, n)
    opn = close + rng.uniform(-1, 1, n)
    vol = rng.uniform(100, 1000, n)
    qvol = vol * close
    return pd.DataFrame({
        "symbol": [symbol] * n,
        "timestamp": pd.date_range("2026-01-01", periods=n, freq="h", tz="UTC"),
        "open": opn, "high": high, "low": low, "close": close,
        "volume": vol, "quote_volume": qvol,
    })


# ---------------------------------------------------------------------------
# Registry metadata tests
# ---------------------------------------------------------------------------

class Test7BRegistry:
    def test_all_27_in_registry(self):
        ids = {fs.factor_id for fs in REGISTRY}
        for fid in SELECTED_7B:
            assert fid in ids, f"{fid} not in REGISTRY"

    def test_registry_count_includes_7b(self):
        """At least 27 + 11 original = 38 total."""
        assert len(REGISTRY) >= 38

    def test_each_has_factor_spec(self):
        for fid in SELECTED_7B:
            fs = REGISTRY_BY_ID[fid]
            assert isinstance(fs, FactorSpec)

    def test_metadata_complete(self):
        for fid in SELECTED_7B:
            fs = REGISTRY_BY_ID[fid]
            assert fs.factor_id == fid
            assert fs.family, f"{fid} missing family"
            assert fs.required_columns, f"{fid} missing required_columns"
            assert fs.lookback_window > 0, f"{fid} invalid lookback_window"
            assert fs.expected_direction, f"{fid} missing expected_direction"
            assert fs.compute_fn is not None, f"{fid} missing compute_fn"

    def test_required_columns_match_csv(self):
        for fid in SELECTED_7B:
            fs = REGISTRY_BY_ID[fid]
            expected = EXPECTED_META[fid]["required_columns"]
            assert sorted(fs.required_columns) == sorted(expected), \
                f"{fid}: expected {expected}, got {fs.required_columns}"

    def test_lookback_window_matches_csv(self):
        for fid in SELECTED_7B:
            fs = REGISTRY_BY_ID[fid]
            expected = EXPECTED_META[fid]["lookback_window"]
            assert fs.lookback_window == expected, \
                f"{fid}: expected lookback={expected}, got {fs.lookback_window}"

    def test_expected_direction_matches_csv(self):
        for fid in SELECTED_7B:
            fs = REGISTRY_BY_ID[fid]
            expected = EXPECTED_META[fid]["expected_direction"]
            assert fs.expected_direction == expected, \
                f"{fid}: expected {expected}, got {fs.expected_direction}"


# ---------------------------------------------------------------------------
# Formula tests — momentum
# ---------------------------------------------------------------------------

class TestMomentum:
    def test_mom_5h_rising(self):
        """Rising prices → positive momentum."""
        df = pd.DataFrame({"close": np.linspace(100, 120, 10)})
        result = REGISTRY_BY_ID["mom_5h"].compute_fn(df)
        assert result.iloc[5] > 0

    def test_mom_10h_warmup_nan(self):
        df = _make_ohlcv(15)
        result = REGISTRY_BY_ID["mom_10h"].compute_fn(df)
        assert result.iloc[:9].isna().all()

    def test_mom_40h_warmup_nan(self):
        df = _make_ohlcv(50)
        result = REGISTRY_BY_ID["mom_40h"].compute_fn(df)
        assert result.iloc[:39].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — reversal
# ---------------------------------------------------------------------------

class TestReversal:
    def test_rev_3h_opposite_of_mom(self):
        df = _make_ohlcv(10)
        mom = df["close"] / df["close"].shift(3) - 1
        rev = REGISTRY_BY_ID["rev_3h"].compute_fn(df)
        pd.testing.assert_series_equal(rev, -mom, check_names=False, atol=1e-10)

    def test_rev_10h_warmup_nan(self):
        df = _make_ohlcv(15)
        result = REGISTRY_BY_ID["rev_10h"].compute_fn(df)
        assert result.iloc[:9].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — volatility
# ---------------------------------------------------------------------------

class TestVolatility:
    def test_vol_5h_non_negative(self):
        df = _make_ohlcv(20)
        result = REGISTRY_BY_ID["vol_5h"].compute_fn(df)
        assert (result.dropna() >= 0).all()

    def test_vol_40h_warmup_nan(self):
        df = _make_ohlcv(50)
        result = REGISTRY_BY_ID["vol_40h"].compute_fn(df)
        assert result.iloc[:40].isna().all()

    def test_vol_ratio_no_inf(self):
        """Constant price → ret=0 → std=0 → no inf (replaced with NaN)."""
        df = pd.DataFrame({
            "close": [100.0] * 30,
        })
        result = REGISTRY_BY_ID["vol_ratio_5_20"].compute_fn(df)
        assert np.isfinite(result.dropna()).all() or result.dropna().isna().all()


# ---------------------------------------------------------------------------
# Formula tests — range_position
# ---------------------------------------------------------------------------

class TestRangePosition:
    def test_range_1h_non_negative(self):
        df = _make_ohlcv(5)
        result = REGISTRY_BY_ID["range_1h"].compute_fn(df)
        assert (result >= 0).all()

    def test_range_4h_warmup(self):
        df = _make_ohlcv(6)
        result = REGISTRY_BY_ID["range_4h"].compute_fn(df)
        assert result.iloc[:3].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — price_position
# ---------------------------------------------------------------------------

class TestPricePosition:
    def test_price_pos_24h_bounded_0_1(self):
        df = _make_ohlcv(30)
        result = REGISTRY_BY_ID["price_pos_24h"].compute_fn(df)
        valid = result.dropna()
        assert (valid >= 0).all() and (valid <= 1).all()

    def test_price_pos_72h_warmup(self):
        df = _make_ohlcv(80)
        result = REGISTRY_BY_ID["price_pos_72h"].compute_fn(df)
        assert result.iloc[:71].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — volume/quote_volume zscore
# ---------------------------------------------------------------------------

class TestVolumeZscore:
    def test_vol_zscore_20h_warmup(self):
        df = _make_ohlcv(25)
        result = REGISTRY_BY_ID["vol_zscore_20h"].compute_fn(df)
        assert result.iloc[:19].isna().all()

    def test_qvol_zscore_48h_warmup(self):
        df = _make_ohlcv(55)
        result = REGISTRY_BY_ID["qvol_zscore_48h"].compute_fn(df)
        assert result.iloc[:47].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — trend_ma
# ---------------------------------------------------------------------------

class TestTrendMA:
    def test_ma_gap_5_20_rising_positive(self):
        """Rising prices → SMA5 > SMA20 → positive gap."""
        df = _make_ohlcv(25)
        result = REGISTRY_BY_ID["ma_gap_5_20"].compute_fn(df)
        assert result.iloc[20] > 0

    def test_ma_gap_10_40_no_inf(self):
        """Zero price → no inf."""
        df = pd.DataFrame({"close": [0.0] * 50})
        result = REGISTRY_BY_ID["ma_gap_10_40"].compute_fn(df)
        assert np.isfinite(result.dropna()).all() or result.dropna().isna().all()


# ---------------------------------------------------------------------------
# Formula tests — breakout
# ---------------------------------------------------------------------------

class TestBreakout:
    def test_breakout_dist_20h_at_high_zero(self):
        """Close at HH20 → breakout distance = 0."""
        df = pd.DataFrame({
            "high": [110.0] * 25,
            "low": [90.0] * 25,
            "close": [110.0] * 25,
        })
        result = REGISTRY_BY_ID["breakout_dist_20h"].compute_fn(df)
        assert abs(result.iloc[-1]) < 1e-6

    def test_breakout_dist_48h_warmup(self):
        df = _make_ohlcv(55)
        result = REGISTRY_BY_ID["breakout_dist_48h"].compute_fn(df)
        assert result.iloc[:47].isna().all()


# ---------------------------------------------------------------------------
# Formula tests — intraday_candle
# ---------------------------------------------------------------------------

class TestIntradayCandle:
    def test_candle_body_bullish(self):
        """close > open → positive body."""
        df = pd.DataFrame({"open": [100.0], "high": [110.0], "low": [95.0], "close": [108.0]})
        result = REGISTRY_BY_ID["candle_body"].compute_fn(df)
        assert result.iloc[0] > 0

    def test_candle_wick_upper_no_inf(self):
        """h == l (flat bar) → no inf."""
        df = pd.DataFrame({"open": [100.0], "high": [100.0], "low": [100.0], "close": [100.0]})
        result = REGISTRY_BY_ID["candle_wick_upper"].compute_fn(df)
        assert np.isfinite(result.iloc[0]) or np.isnan(result.iloc[0])

    def test_candle_wick_lower_bounded(self):
        df = _make_ohlcv(5)
        result = REGISTRY_BY_ID["candle_wick_lower"].compute_fn(df)
        valid = result.dropna()
        assert (valid >= -1e-6).all() and (valid <= 1 + 1e-6).all()


# ---------------------------------------------------------------------------
# Cross-sectional rank tests
# ---------------------------------------------------------------------------

class TestCrossSectionalRank:
    def test_xs_rank_ret_1h_returns_pct_change(self):
        """compute_fn returns per-symbol pct_change (rank done by postprocess)."""
        df = _make_ohlcv(5)
        result = REGISTRY_BY_ID["xs_rank_ret_1h"].compute_fn(df)
        expected = df["close"].pct_change()
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_xs_rank_vol_rolling_mean(self):
        df = _make_ohlcv(25)
        result = REGISTRY_BY_ID["xs_rank_vol"].compute_fn(df)
        assert result.iloc[:19].isna().all()

    def test_postprocess_rank_basic(self):
        """3 symbols at same timestamp → rank assigns percentile 0.33/0.67/1.0."""
        from build_factor_values import apply_cross_sectional_postprocess
        ts = pd.Timestamp("2026-01-01", tz="UTC")
        wide = pd.DataFrame({
            "timestamp": [ts] * 3,
            "symbol": ["A", "B", "C"],
            "xs_rank_ret_1h": [0.01, 0.03, 0.02],
            "xs_rank_vol": [100.0, 300.0, 200.0],
        })
        result = apply_cross_sectional_postprocess(wide)
        # A=0.01→0.333, B=0.03→1.0, C=0.02→0.667
        assert abs(result["xs_rank_ret_1h"].iloc[0] - 1 / 3) < 0.01
        assert abs(result["xs_rank_ret_1h"].iloc[1] - 1.0) < 0.01
        assert abs(result["xs_rank_ret_1h"].iloc[2] - 2 / 3) < 0.01
        # Same pattern for volume
        assert abs(result["xs_rank_vol"].iloc[0] - 1 / 3) < 0.01
        assert abs(result["xs_rank_vol"].iloc[1] - 1.0) < 0.01
        assert abs(result["xs_rank_vol"].iloc[2] - 2 / 3) < 0.01

    def test_postprocess_rank_nan_preserved(self):
        """NaN inputs stay NaN after ranking."""
        from build_factor_values import apply_cross_sectional_postprocess
        ts = pd.Timestamp("2026-01-01", tz="UTC")
        wide = pd.DataFrame({
            "timestamp": [ts] * 3,
            "symbol": ["A", "B", "C"],
            "xs_rank_ret_1h": [0.01, float("nan"), 0.02],
            "xs_rank_vol": [100.0, 200.0, float("nan")],
        })
        result = apply_cross_sectional_postprocess(wide)
        assert pd.isna(result["xs_rank_ret_1h"].iloc[1])
        assert pd.isna(result["xs_rank_vol"].iloc[2])

    def test_postprocess_does_not_touch_other_factors(self):
        """Non-xs factors must be unchanged."""
        from build_factor_values import apply_cross_sectional_postprocess
        ts = pd.Timestamp("2026-01-01", tz="UTC")
        wide = pd.DataFrame({
            "timestamp": [ts] * 2,
            "symbol": ["A", "B"],
            "xs_rank_ret_1h": [0.01, 0.03],
            "mom_5h": [0.05, -0.02],
        })
        result = apply_cross_sectional_postprocess(wide)
        pd.testing.assert_series_equal(result["mom_5h"], wide["mom_5h"])


# ---------------------------------------------------------------------------
# Zero-denominator / inf protection
# ---------------------------------------------------------------------------

class TestNoInf:
    def test_range_1h_zero_close(self):
        df = pd.DataFrame({"high": [110.0], "low": [90.0], "close": [0.0]})
        result = REGISTRY_BY_ID["range_1h"].compute_fn(df)
        assert np.isfinite(result.iloc[0]) or np.isnan(result.iloc[0])

    def test_candle_body_flat_bar(self):
        df = pd.DataFrame({"open": [100.0], "high": [100.0], "low": [100.0], "close": [100.0]})
        result = REGISTRY_BY_ID["candle_body"].compute_fn(df)
        assert np.isfinite(result.iloc[0]) or np.isnan(result.iloc[0])

    def test_ma_gap_5_20_zero_sma(self):
        df = pd.DataFrame({"close": [0.0] * 25})
        result = REGISTRY_BY_ID["ma_gap_5_20"].compute_fn(df)
        assert np.isfinite(result.dropna()).all() or result.dropna().isna().all()

    def test_breakout_flat_hl(self):
        """HH == LL → denominator is eps, not zero."""
        df = pd.DataFrame({"high": [100.0] * 25, "low": [100.0] * 25, "close": [100.0] * 25})
        result = REGISTRY_BY_ID["breakout_dist_20h"].compute_fn(df)
        assert np.isfinite(result.dropna()).all()
