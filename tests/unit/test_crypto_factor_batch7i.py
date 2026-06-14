"""Phase 7I-A: validation tests for Batch-2 PM-approved factors."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY, REGISTRY_BY_ID

# PM-approved 9 factors
APPROVED = {
    "ema_12_26_gap": ("technical_indicators", "positive"),
    "rsi_7h": ("technical_indicators", "negative"),
    "rsi_28h": ("technical_indicators", "negative"),
    "williams_r_14h": ("technical_indicators", "negative"),
    "downside_vol_20h": ("realized_skew_kurtosis", "negative"),
    "vol_of_vol_20h": ("realized_skew_kurtosis", "negative"),
    "mom_accel_20h": ("momentum", "positive"),
    "qvol_ma_ratio_5_20": ("quote_volume_liquidity", "positive"),
    "ma_gap_20_80": ("trend_ma", "positive"),
}

# Server SELECT_NOW factors NOT approved by PM
REJECTED_SELECT_NOW = {
    "mom_80h", "rev_48h", "vol_ma_ratio_5_20", "ema_gap_12_26",
    "range_breakout_20h", "range_breakdown_20h", "breakout_dist_72h",
    "breakout_high_20h", "wq101_alpha23",
}

BANNED_STATUS = {"ALPHA", "CANDIDATE_REVIEW", "TRADEABLE", "LIVE", "DEPLOY", "PORTFOLIO"}

# ── Test data fixture ──────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_df() -> pd.DataFrame:
    """Synthetic OHLCV + quote_volume data for smoke tests."""
    np.random.seed(42)
    n = 200
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    high = close + np.abs(np.random.randn(n) * 0.3)
    low = close - np.abs(np.random.randn(n) * 0.3)
    opn = close + np.random.randn(n) * 0.1
    vol = np.abs(np.random.randn(n)) * 1000 + 500
    qvol = vol * close * (1 + np.random.randn(n) * 0.01)
    return pd.DataFrame({
        "open": opn, "high": high, "low": low, "close": close,
        "volume": vol, "quote_volume": qvol,
    })


# ── Registry tests ─────────────────────────────────────────────────

def test_all_9_approved_factors_in_registry():
    for fid in APPROVED:
        assert fid in REGISTRY_BY_ID, f"{fid} not in REGISTRY"


def test_no_rejected_select_now_in_registry():
    for fid in REJECTED_SELECT_NOW:
        assert fid not in REGISTRY_BY_ID, f"Rejected factor {fid} found in REGISTRY"


def test_no_wq101_batch2_in_registry():
    wq_batch2 = {f"wq101_alpha{a}" for a in [
        "01","02","03","06","08","09","15","18","21","23","24","26","28","33","34","41","44","45"
    ]}
    for fid in wq_batch2:
        assert fid not in REGISTRY_BY_ID, f"WQ101 factor {fid} should not be in registry"


def test_all_9_have_correct_family_and_direction():
    for fid, (family, direction) in APPROVED.items():
        spec = REGISTRY_BY_ID[fid]
        assert spec.family == family, f"{fid}: expected family={family}, got {spec.family}"
        assert spec.expected_direction == direction, f"{fid}: expected dir={direction}, got {spec.expected_direction}"


def test_no_forbidden_status_in_registry():
    for spec in REGISTRY:
        # Check notes for banned language
        for banned in BANNED_STATUS:
            assert banned not in (spec.notes or "").upper(), f"{spec.factor_id} has banned status '{banned}' in notes"


# ── Compute function smoke tests ──────────────────────────────────

def test_rsi_7h_bounded(sample_df):
    """RSI should be in [0, 100]."""
    spec = REGISTRY_BY_ID["rsi_7h"]
    out = spec.compute_fn(sample_df)
    out_clean = out.dropna()
    assert (out_clean >= 0).all() and (out_clean <= 100).all(), f"RSI 7h out of [0,100]: min={out_clean.min()}, max={out_clean.max()}"


def test_rsi_28h_bounded(sample_df):
    spec = REGISTRY_BY_ID["rsi_28h"]
    out = spec.compute_fn(sample_df)
    out_clean = out.dropna()
    assert (out_clean >= 0).all() and (out_clean <= 100).all(), f"RSI 28h out of [0,100]"


def test_williams_r_14h_bounded(sample_df):
    """Williams %R should be in [0, 1] (0-1 scale)."""
    spec = REGISTRY_BY_ID["williams_r_14h"]
    out = spec.compute_fn(sample_df)
    out_clean = out.dropna()
    assert (out_clean >= 0).all() and (out_clean <= 1).all(), f"Williams %R out of [0,1]: min={out_clean.min()}, max={out_clean.max()}"


def test_downside_vol_uses_only_past_returns(sample_df):
    """downside_vol_20h must not use future data — verify by checking NaN at start."""
    spec = REGISTRY_BY_ID["downside_vol_20h"]
    out = spec.compute_fn(sample_df)
    # First 20 rows should be NaN (pct_change loses 1, rolling_std loses 19 more)
    assert out.iloc[:20].isna().all(), "downside_vol_20h should have NaN for first 20 rows"


def test_vol_of_vol_nested_rolling(sample_df):
    """vol_of_vol_20h should have NaN for first ~25 bars (pct_change + std(5) + std(20))."""
    spec = REGISTRY_BY_ID["vol_of_vol_20h"]
    out = spec.compute_fn(sample_df)
    assert out.iloc[:24].isna().all(), "vol_of_vol_20h should have NaN for first ~25 rows"


def test_qvol_ma_ratio_uses_quote_volume(sample_df):
    """qvol_ma_ratio_5_20 must use quote_volume, not volume."""
    spec = REGISTRY_BY_ID["qvol_ma_ratio_5_20"]
    assert "quote_volume" in spec.required_columns, "qvol_ma_ratio must require quote_volume"
    out = spec.compute_fn(sample_df)
    assert out.notna().any(), "qvol_ma_ratio_5_20 should produce non-NaN values"


def test_ma_gap_20_80_uses_correct_windows(sample_df):
    """ma_gap_20_80 should use SMA20 and SMA80."""
    spec = REGISTRY_BY_ID["ma_gap_20_80"]
    assert spec.lookback_window == 80, f"Expected lookback=80, got {spec.lookback_window}"
    out = spec.compute_fn(sample_df)
    # First 79 rows should be NaN (SMA80 needs 80 points)
    assert out.iloc[:79].isna().all(), "ma_gap_20_80 should have NaN for first 79 rows"
    assert out.iloc[80:].notna().any(), "ma_gap_20_80 should produce values after warmup"


def test_mom_accel_20h_formula(sample_df):
    """mom_accel_20h = mom_20h - delay(mom_20h, 5)."""
    spec = REGISTRY_BY_ID["mom_accel_20h"]
    out = spec.compute_fn(sample_df)
    # Manual check: mom_20h = close / delay(close, 20) - 1
    from factor_ops import delay as _delay
    mom_20h = sample_df["close"] / _delay(sample_df["close"], 20) - 1.0
    expected = mom_20h - _delay(mom_20h, 5)
    pd.testing.assert_series_equal(out, expected, check_names=False, check_exact=False, rtol=1e-10)
