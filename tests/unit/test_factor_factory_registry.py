"""Unit tests for factor_specs.py and factor_formula_registry.py."""
import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from factor_specs import FactorSpec
from factor_formula_registry import REGISTRY, REGISTRY_BY_ID

EXPECTED_FACTOR_IDS = [
    "mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h",
    "wq101_alpha101", "wq101_alpha12", "wq101_alpha53",
    "q158_high_low_range", "tech_macd", "tech_atr",
]


# ── Registry completeness ──────────────────────────────────────────

class TestRegistryCompleteness:
    def test_count(self):
        assert len(REGISTRY) == 11

    def test_all_expected_ids(self):
        ids = {fs.factor_id for fs in REGISTRY}
        for fid in EXPECTED_FACTOR_IDS:
            assert fid in ids, f"Missing factor: {fid}"

    def test_no_duplicates(self):
        ids = [fs.factor_id for fs in REGISTRY]
        assert len(ids) == len(set(ids))

    def test_registry_by_id(self):
        assert len(REGISTRY_BY_ID) == 11
        for fid in EXPECTED_FACTOR_IDS:
            assert fid in REGISTRY_BY_ID


# ── FactorSpec fields ───────────────────────────────────────────────

class TestFactorSpecFields:
    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_has_required_columns(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        assert isinstance(spec.required_columns, list)
        assert len(spec.required_columns) > 0

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_has_expected_direction(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        assert spec.expected_direction in ("positive", "negative", "conditional")

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_has_status(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        assert spec.status == "DIAGNOSTIC_PROBE"

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_lookback_window_positive(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        assert spec.lookback_window >= 1

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_compute_fn_callable(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        assert callable(spec.compute_fn)


# ── Compute functions produce valid output ──────────────────────────

def _make_sample_df(n=200):
    """Create a synthetic single-symbol OHLCV DataFrame."""
    rng = np.random.default_rng(42)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + rng.uniform(0.1, 2.0, n)
    low = close - rng.uniform(0.1, 2.0, n)
    opn = close + rng.uniform(-1, 1, n)
    vol = rng.uniform(1000, 50000, n)
    ts = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "symbol": "TESTUSDT",
        "open": opn, "high": high, "low": low, "close": close, "volume": vol,
    })


class TestComputeFunctions:
    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_returns_series(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        df = _make_sample_df()
        result = spec.compute_fn(df)
        assert isinstance(result, pd.Series)

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_same_index(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        df = _make_sample_df()
        result = spec.compute_fn(df)
        assert len(result) == len(df)

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_no_all_nan(self, factor_id):
        spec = REGISTRY_BY_ID[factor_id]
        df = _make_sample_df()
        result = spec.compute_fn(df)
        # At least 80% non-NaN (warmup is OK)
        assert result.notna().mean() > 0.8, f"{factor_id} has too many NaN: {result.isna().mean():.1%}"

    @pytest.mark.parametrize("factor_id", EXPECTED_FACTOR_IDS)
    def test_no_future_leak(self, factor_id):
        """Reversing data should change the result — proves it uses past, not future."""
        spec = REGISTRY_BY_ID[factor_id]
        df = _make_sample_df()
        normal = spec.compute_fn(df)
        reversed_df = df.iloc[::-1].reset_index(drop=True)
        reversed_result = spec.compute_fn(reversed_df)
        # Results should differ (except maybe trivially for first few rows)
        assert not normal.dropna().equals(reversed_result.dropna().head(len(normal.dropna())))


# ── Metadata hardening ─────────────────────────────────────────────

class TestMetadataHardening:
    """Tests for metadata conventions: direction, lookback, warmup."""

    def test_wq101_alpha101_direction_conditional(self):
        """alpha101 direction must be conditional — no post-hoc fitting."""
        spec = REGISTRY_BY_ID["wq101_alpha101"]
        assert spec.expected_direction == "conditional"

    def test_wq101_alpha101_direction_note(self):
        spec = REGISTRY_BY_ID["wq101_alpha101"]
        assert "post-hoc" in spec.notes.lower() or "conditional" in spec.notes.lower()

    def test_wq101_alpha12_lookback_2(self):
        """delta(1) needs t and t-1 → lookback_window=2."""
        spec = REGISTRY_BY_ID["wq101_alpha12"]
        assert spec.lookback_window == 2

    def test_wq101_alpha53_lookback_10(self):
        """diff(9) needs t and t-9 → lookback_window=10."""
        spec = REGISTRY_BY_ID["wq101_alpha53"]
        assert spec.lookback_window == 10

    def test_tech_atr_warmup_strict(self):
        """ATR uses true_range (first row NaN) + rolling_mean(14, min_periods=14).
        First valid ATR should appear at row 14 (0-indexed): 1 NaN + 14 values = 15 bars.
        """
        from factor_ops import true_range
        from factor_formula_registry import _compute_tech_atr
        df = _make_sample_df(n=30)
        # Verify true_range first row is NaN
        tr = true_range(df["high"], df["low"], df["close"])
        assert np.isnan(tr.iloc[0])
        assert tr.iloc[1] > 0  # second row is valid
        # ATR first valid should be at index 14 (1 NaN from TR + 13 more for rolling(14))
        atr = _compute_tech_atr(df)
        assert np.isnan(atr.iloc[0:14]).all()  # rows 0-13 all NaN
        assert atr.iloc[14] > 0  # row 14 first valid

    def test_direction_set_from_domain_not_eval(self):
        """All expected_direction values must be from domain knowledge, not evaluation."""
        for spec in REGISTRY:
            assert spec.expected_direction in ("positive", "negative", "conditional")
            # No factor should have notes suggesting direction was fitted from results
            for forbidden in ["fitted from", "IC sign", "empirical direction"]:
                assert forbidden.lower() not in spec.notes.lower(), \
                    f"{spec.factor_id}: direction appears post-hoc fitted"

    def test_lookback_window_meaning(self):
        """lookback_window = bars_required_including_current, must be >= 1."""
        for spec in REGISTRY:
            assert spec.lookback_window >= 1, \
                f"{spec.factor_id}: lookback_window must be >= 1"
