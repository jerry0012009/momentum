"""Unit tests for audit_dynamic_universe_factor_values.py (Phase 6F).

All tests use synthetic data.
"""
import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from audit_dynamic_universe_factor_values import (
    compute_global_coverage,
    compute_membership_aware_coverage,
    MISSING_RATE_THRESHOLD,
)


# ── Helpers ────────────────────────────────────────────────────────

def _make_factor_values(symbol: str, months: list[str], rows_per_month: int = 720,
                        missing_rate: float = 0.0) -> pd.DataFrame:
    """Create synthetic factor values for one symbol across months."""
    rows = []
    for m in months:
        timestamps = pd.date_range(f"{m}-01", periods=rows_per_month, freq="h", tz="UTC")
        for ts in timestamps:
            val = np.random.randn() if np.random.random() > missing_rate else np.nan
            rows.append({
                "timestamp": ts,
                "symbol": symbol,
                "factor_name": "test_factor",
                "factor_value": val,
                "known_at": ts,
                "source_timeframe": "1h",
                "computed_at": "2026-01-01T00:00:00Z",
            })
    return pd.DataFrame(rows)


def _make_snapshots(symbol_months: dict[str, list[str]]) -> pd.DataFrame:
    """Create synthetic universe snapshots."""
    rows = []
    for sym, months in symbol_months.items():
        for m in months:
            rows.append({"symbol": sym, "asof_time": pd.Timestamp(f"{m}-01", tz="UTC")})
    return pd.DataFrame(rows)


# ── Membership-aware coverage ──────────────────────────────────────

class TestMembershipAwareFactorCoverage:
    def test_filters_selected_symbol_months(self):
        """Only selected symbol-months should be included."""
        fv = _make_factor_values("SYM", ["2024-07", "2024-08"], rows_per_month=100)
        snapshots = _make_snapshots({"SYM": ["2024-07"]})  # only July selected

        summary, _, _ = compute_membership_aware_coverage(fv, snapshots, "test_factor")
        # Only July rows should be selected
        assert summary["selected_rows"] == 100

    def test_global_high_selected_acceptable(self):
        """Global missing can be high while selected missing is acceptable."""
        # SYM has 50% missing globally, but only July is selected with 0% missing
        fv_july = _make_factor_values("SYM", ["2024-07"], rows_per_month=100, missing_rate=0.0)
        fv_aug = _make_factor_values("SYM", ["2024-08"], rows_per_month=100, missing_rate=1.0)
        fv = pd.concat([fv_july, fv_aug], ignore_index=True)

        snapshots = _make_snapshots({"SYM": ["2024-07"]})
        global_cov = compute_global_coverage(fv, "test_factor")
        selected_summary, _, _ = compute_membership_aware_coverage(fv, snapshots, "test_factor")

        assert global_cov["global_missing_rate"] > 0.4  # ~50% global
        assert selected_summary["selected_missing_rate"] == 0.0  # 0% in selected month

    def test_high_selected_missing_blocks(self):
        """selected_missing_rate > threshold should result in FAIL."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=100, missing_rate=0.10)
        snapshots = _make_snapshots({"SYM": ["2024-07"]})

        summary, _, _ = compute_membership_aware_coverage(fv, snapshots, "test_factor")
        assert summary["qa_status"] == "FAIL"

    def test_low_selected_missing_passes(self):
        """selected_missing_rate <= threshold should result in PASS."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=100, missing_rate=0.01)
        snapshots = _make_snapshots({"SYM": ["2024-07"]})

        summary, _, _ = compute_membership_aware_coverage(fv, snapshots, "test_factor")
        assert summary["qa_status"] == "PASS"


# ── Schema checks ─────────────────────────────────────────────────

class TestFactorValuesSchema:
    def test_schema_exact(self):
        """factor_values must have exact 7 columns."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=10)
        expected_cols = ["timestamp", "symbol", "factor_name", "factor_value",
                         "known_at", "source_timeframe", "computed_at"]
        assert list(fv.columns) == expected_cols

    def test_known_at_equals_timestamp(self):
        """known_at must equal timestamp."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=10)
        assert (fv["known_at"] == fv["timestamp"]).all()

    def test_source_timeframe_is_1h(self):
        """source_timeframe must be '1h'."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=10)
        assert (fv["source_timeframe"] == "1h").all()


# ── Global coverage ───────────────────────────────────────────────

class TestGlobalCoverage:
    def test_schema_keys(self):
        """Global coverage must have required keys."""
        fv = _make_factor_values("SYM", ["2024-07"], rows_per_month=10)
        cov = compute_global_coverage(fv, "test_factor")
        for key in ["factor_id", "n_rows", "n_symbols", "global_non_null_rate", "global_missing_rate"]:
            assert key in cov
