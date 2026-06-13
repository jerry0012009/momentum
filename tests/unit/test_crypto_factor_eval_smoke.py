"""Smoke test for evaluate_factors.py — verify direction-adjusted spread and gap handling.

Tests:
- IC / RankIC / spread fields are present and finite
- direction_adjusted_spread flips sign for negative expected_direction
- direction_adjusted_spread is None for conditional direction
- Gap symbols (missing_bar_rate > 5%) are excluded from evaluation
- Synthetic signal produces positive IC
"""
import math
import numpy as np
import pandas as pd
import pytest

# Import the evaluation functions directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from evaluate_factors import (
    evaluate_one_label,
    compute_missing_bar_rates,
    get_excluded_symbols,
    load_catalog_directions,
    clean_float,
    MISSING_BAR_RATE_THRESHOLD,
)


def _make_synthetic_panel(n_symbols=20, n_timestamps=200, seed=42):
    """Create a synthetic merged panel of factor_value + forward returns."""
    rng = np.random.default_rng(seed)
    rows = []
    base_ts = pd.Timestamp("2026-01-01T01:00:00", tz="UTC")
    for t in range(n_timestamps):
        ts = base_ts + pd.Timedelta(hours=t)
        for s in range(n_symbols):
            fv = rng.normal()
            noise = rng.normal(0, 0.01)
            ret = 0.001 * fv + noise
            rows.append({
                "timestamp": ts,
                "symbol": f"SYM{s}",
                "factor_value": fv,
                "ret_fwd_1h": ret,
            })
    return pd.DataFrame(rows)


class TestEvaluationSmoke:
    """evaluate_factors.py logic must produce valid IC / RankIC / spread on synthetic data."""

    def test_ic_fields_present(self):
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        for key in ["IC_mean", "IC_std", "ICIR", "RankIC_mean", "RankIC_std", "RankICIR",
                     "quantile_spread_mean", "quantile_spread_tstat",
                     "direction_adjusted_spread", "direction_adjusted_tstat",
                     "coverage", "n_timestamps"]:
            assert key in m, f"Missing key: {key}"

    def test_ic_values_finite(self):
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        for key in ["IC_mean", "RankIC_mean", "quantile_spread_mean", "coverage"]:
            v = m[key]
            assert v is not None, f"{key} is None"
            assert not math.isnan(v), f"{key} is NaN"
            assert not math.isinf(v), f"{key} is Inf"

    def test_ic_positive_for_synthetic_signal(self):
        """Synthetic data has positive factor-return correlation → IC should be positive."""
        df = _make_synthetic_panel(n_symbols=20, n_timestamps=500, seed=42)
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        assert m["IC_mean"] > 0, f"Expected positive IC, got {m['IC_mean']}"

    def test_coverage_near_one(self):
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        assert m["coverage"] > 0.95

    def test_empty_panel_returns_none_metrics(self):
        df = pd.DataFrame(columns=["timestamp", "symbol", "factor_value", "ret_fwd_1h"])
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        assert m["IC_mean"] is None
        assert m["coverage"] == 0.0


class TestDirectionAdjustedSpread:
    """direction_adjusted_spread must respect expected_direction."""

    def test_positive_direction_spread_unchanged(self):
        """For expected_direction=positive, dir_adj = Q5 - Q1 (same as raw)."""
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        raw = m["quantile_spread_mean"]
        adj = m["direction_adjusted_spread"]
        if raw is not None and adj is not None:
            assert adj == pytest.approx(raw, abs=1e-12), (
                f"positive: dir_adj ({adj}) should equal raw ({raw})"
            )

    def test_negative_direction_spread_flipped(self):
        """For expected_direction=negative, dir_adj = Q1 - Q5 (negated raw)."""
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="negative")
        raw = m["quantile_spread_mean"]
        adj = m["direction_adjusted_spread"]
        if raw is not None and adj is not None:
            assert adj == pytest.approx(-raw, abs=1e-12), (
                f"negative: dir_adj ({adj}) should equal -raw ({-raw})"
            )

    def test_conditional_direction_spread_is_none(self):
        """For expected_direction=conditional, dir_adj should be None."""
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="conditional")
        assert m["direction_adjusted_spread"] is None, (
            "conditional: dir_adj should be None"
        )
        assert m["direction_adjusted_tstat"] is None

    def test_direction_passed_through_to_metrics(self):
        """expected_direction should appear in the metrics dict."""
        for d in ["positive", "negative", "conditional"]:
            df = _make_synthetic_panel()
            m = evaluate_one_label(df, "ret_fwd_1h", expected_direction=d)
            assert m["expected_direction"] == d


class TestGapSymbolExclusion:
    """Symbols with missing_bar_rate > 5% should be excluded."""

    def test_excluded_symbols_identified(self):
        """Test that get_excluded_symbols correctly identifies high-gap symbols."""
        rates = {
            "BTCUSDT": 0.01,   # 1% — ok
            "ETHUSDT": 0.02,   # 2% — ok
            "SPACEUSDT": 0.22,  # 22% — exclude
            "RAREUSDT": 0.08,   # 8% — exclude
        }
        excluded = get_excluded_symbols(rates, threshold=0.05)
        assert excluded == {"SPACEUSDT", "RAREUSDT"}

    def test_no_exclusion_when_all_ok(self):
        rates = {"BTCUSDT": 0.01, "ETHUSDT": 0.02}
        excluded = get_excluded_symbols(rates, threshold=0.05)
        assert excluded == set()

    def test_threshold_boundary(self):
        """Exactly 5% should NOT be excluded (threshold is >, not >=)."""
        rates = {"BTCUSDT": 0.05}
        excluded = get_excluded_symbols(rates, threshold=0.05)
        assert "BTCUSDT" not in excluded

    def test_missing_rate_in_metrics(self):
        """metrics dict should include missing_rate field."""
        df = _make_synthetic_panel()
        m = evaluate_one_label(df, "ret_fwd_1h", expected_direction="positive")
        assert "missing_rate" in m
        assert m["missing_rate"] is not None
        assert m["missing_rate"] >= 0


class TestCatalogDirectionLoading:
    """Test direction loading from catalog."""

    def test_load_directions_from_csv(self, tmp_path):
        csv = tmp_path / "test_catalog.csv"
        csv.write_text(
            "factor_id,factor_name,expected_direction\n"
            "mom_20h,Momentum,positive\n"
            "reversal_5h,Reversal,negative\n"
            "custom_1,Custom,conditional\n"
        )
        dirs = load_catalog_directions(csv)
        assert dirs == {"mom_20h": "positive", "reversal_5h": "negative", "custom_1": "conditional"}

    def test_missing_direction_defaults_to_positive(self, tmp_path):
        csv = tmp_path / "test_catalog.csv"
        csv.write_text(
            "factor_id,factor_name\n"
            "mom_20h,Momentum\n"
        )
        dirs = load_catalog_directions(csv)
        assert dirs["mom_20h"] == "positive"
