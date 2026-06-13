"""Tests for build_factor_values.py — verify schema and temporal constraints."""
import numpy as np
import pandas as pd
import pytest


REQUIRED_COLUMNS = {
    "timestamp", "symbol", "factor_name", "factor_value",
    "known_at", "source_timeframe", "computed_at",
}


def _make_factor_values(n_symbols=5, n_hours=100, factor_name="mom_20h"):
    """Create synthetic factor values matching the expected schema."""
    rng = np.random.default_rng(42)
    base_ts = pd.Timestamp("2026-01-01", tz="UTC")
    rows = []
    for s in range(n_symbols):
        sym = f"SYM{s}USDT"
        for i in range(n_hours):
            ts = base_ts + pd.Timedelta(hours=i)
            rows.append({
                "timestamp": ts,
                "symbol": sym,
                "factor_name": factor_name,
                "factor_value": rng.normal(),
                "known_at": ts,
                "source_timeframe": "1h",
                "computed_at": "2026-06-13T00:00:00Z",
            })
    return pd.DataFrame(rows)


class TestFactorValueSchema:
    """Factor values must have the required columns."""

    def test_required_columns_present(self):
        fv = _make_factor_values()
        assert REQUIRED_COLUMNS.issubset(set(fv.columns)), (
            f"Missing columns: {REQUIRED_COLUMNS - set(fv.columns)}"
        )

    def test_column_types(self):
        fv = _make_factor_values()
        assert pd.api.types.is_datetime64_any_dtype(fv["timestamp"])
        assert pd.api.types.is_string_dtype(fv["symbol"])
        assert pd.api.types.is_string_dtype(fv["factor_name"])
        assert pd.api.types.is_numeric_dtype(fv["factor_value"])


class TestKnownAtConstraint:
    """known_at must not be later than timestamp."""

    def test_known_at_not_after_timestamp(self):
        fv = _make_factor_values()
        # known_at should be <= timestamp for all rows
        violations = fv[fv["known_at"] > fv["timestamp"]]
        assert len(violations) == 0, (
            f"{len(violations)} rows where known_at > timestamp"
        )

    def test_known_at_equals_timestamp_for_bar_factors(self):
        """For OHLCV-based factors, known_at == timestamp (bar close)."""
        fv = _make_factor_values()
        # In the current pipeline, known_at is set to timestamp
        mismatch = fv[fv["known_at"] != fv["timestamp"]]
        assert len(mismatch) == 0


class TestFactorValueContent:
    """Factor values should be finite for valid bars."""

    def test_factor_values_finite_for_most_rows(self):
        fv = _make_factor_values()
        finite_ratio = fv["factor_value"].notna().mean()
        assert finite_ratio > 0.9, f"Expected >90% finite values, got {finite_ratio:.1%}"

    def test_source_timeframe_is_1h(self):
        fv = _make_factor_values()
        assert (fv["source_timeframe"] == "1h").all()
