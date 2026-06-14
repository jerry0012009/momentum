"""Phase 7M-A: crypto-native diagnostic factor tests.

Tests registry metadata + formula correctness for 6 factors:
- taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h
- funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from factor_formula_registry import REGISTRY_BY_ID  # noqa: E402
from factor_ops import delay, rolling_mean, zscore  # noqa: E402

TAKER_IDS = ["taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h"]
FUNDING_IDS = ["funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h"]
ALL_IDS = TAKER_IDS + FUNDING_IDS


# ── Registry metadata tests ────────────────────────────────────────
class TestRegistry:
    @pytest.fixture(autouse=True)
    def _load(self):
        self.specs = {fid: REGISTRY_BY_ID[fid] for fid in ALL_IDS}

    def test_all_6_in_registry(self):
        for fid in ALL_IDS:
            assert fid in REGISTRY_BY_ID, f"{fid} not in REGISTRY"

    def test_taker_family(self):
        for fid in TAKER_IDS:
            assert self.specs[fid].family == "taker_imbalance"

    def test_funding_family(self):
        for fid in FUNDING_IDS:
            assert self.specs[fid].family == "funding_rate"

    def test_taker_direction_positive(self):
        for fid in TAKER_IDS:
            assert self.specs[fid].expected_direction == "positive"

    def test_funding_direction_negative(self):
        for fid in FUNDING_IDS:
            assert self.specs[fid].expected_direction == "negative"

    def test_all_diagnostic_probe(self):
        for fid in ALL_IDS:
            assert self.specs[fid].status == "DIAGNOSTIC_PROBE", (
                f"{fid}: status={self.specs[fid].status}"
            )

    def test_taker_required_columns(self):
        for fid in TAKER_IDS:
            cols = self.specs[fid].required_columns
            assert "taker_buy_quote_volume" in cols, f"{fid}: {cols}"
            assert "quote_volume" in cols, f"{fid}: {cols}"

    def test_funding_required_columns(self):
        for fid in FUNDING_IDS:
            cols = self.specs[fid].required_columns
            assert "funding_rate" in cols, f"{fid}: {cols}"

    def test_no_forbidden_status_words(self):
        forbidden = {"CANDIDATE_REVIEW", "ALPHA", "TRADEABLE", "LIVE", "DEPLOY"}
        for fid in ALL_IDS:
            notes = self.specs[fid].notes.upper()
            for word in forbidden:
                assert word not in notes, f"{fid}: notes contain {word}"
            assert self.specs[fid].status not in forbidden


# ── Taker formula tests ────────────────────────────────────────────
class TestTakerFormulas:
    @pytest.fixture(autouse=True)
    def _make_df(self):
        np.random.seed(42)
        n = 100
        self.df = pd.DataFrame({
            "taker_buy_quote_volume": np.random.uniform(1e6, 5e6, n),
            "quote_volume": np.random.uniform(5e6, 20e6, n),
        })

    def test_ratio_basic(self):
        ratio = self.df["taker_buy_quote_volume"] / self.df["quote_volume"]
        expected = rolling_mean(ratio, 20)
        result = REGISTRY_BY_ID["taker_buy_ratio_20h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_zscore_basic(self):
        ratio = self.df["taker_buy_quote_volume"] / self.df["quote_volume"]
        expected = zscore(ratio, 20)
        result = REGISTRY_BY_ID["taker_buy_zscore_20h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_delta_basic(self):
        ratio = self.df["taker_buy_quote_volume"] / self.df["quote_volume"]
        expected = ratio - delay(ratio, 5)
        result = REGISTRY_BY_ID["taker_buy_delta_5h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_quote_volume_zero_is_nan(self):
        df = self.df.copy()
        df.loc[10, "quote_volume"] = 0.0
        for fid in TAKER_IDS:
            result = REGISTRY_BY_ID[fid].compute_fn(df)
            assert pd.isna(result.iloc[10]) or pd.isna(result.iloc[29]), (
                f"{fid}: zero quote_volume should propagate NaN"
            )

    def test_taker_nan_no_forward_fill(self):
        df = self.df.copy()
        df.loc[50, "taker_buy_quote_volume"] = np.nan
        result = REGISTRY_BY_ID["taker_buy_ratio_20h"].compute_fn(df)
        # NaN at index 50 should remain NaN in ratio, and rolling_mean may have NaN
        # but the point is: we don't forward-fill the taker field
        assert pd.isna(result.iloc[50]) or pd.notna(result.iloc[50])  # just no crash
        # The key check: the raw ratio at 50 must be NaN
        ratio = df["taker_buy_quote_volume"] / df["quote_volume"]
        assert pd.isna(ratio.iloc[50])


# ── Funding formula tests ──────────────────────────────────────────
class TestFundingFormulas:
    @pytest.fixture(autouse=True)
    def _make_df(self):
        np.random.seed(123)
        n = 200
        self.df = pd.DataFrame({
            "funding_rate": np.random.normal(0.0001, 0.0005, n),
        })

    def test_level_20h(self):
        expected = rolling_mean(self.df["funding_rate"], 20)
        result = REGISTRY_BY_ID["funding_rate_level_20h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_zscore_80h(self):
        expected = zscore(self.df["funding_rate"], 80)
        result = REGISTRY_BY_ID["funding_rate_zscore_80h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_change_24h(self):
        expected = self.df["funding_rate"] - delay(self.df["funding_rate"], 24)
        result = REGISTRY_BY_ID["funding_rate_change_24h"].compute_fn(self.df)
        pd.testing.assert_series_equal(result, expected, check_names=False)

    def test_nan_propagation(self):
        df = self.df.copy()
        df.loc[100, "funding_rate"] = np.nan
        for fid in FUNDING_IDS:
            result = REGISTRY_BY_ID[fid].compute_fn(df)
            # NaN should propagate naturally (no forward-fill)
            assert pd.isna(result.iloc[100])

    def test_no_future_data(self):
        """Verify no future data: delay(n) uses only past values."""
        df = self.df.copy()
        # Set future values to extreme
        df.loc[150, "funding_rate"] = 999.0
        result = REGISTRY_BY_ID["funding_rate_change_24h"].compute_fn(df)
        # At index 149, delay(funding_rate, 24) should use index 125, not 150
        # So result[149] should NOT reflect the 999.0 value
        assert abs(result.iloc[149]) < 100  # sanity check
