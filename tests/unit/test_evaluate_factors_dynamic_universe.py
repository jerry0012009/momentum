"""Unit tests for evaluate_factors_dynamic_universe.py (Phase 6G).

All tests use synthetic data.
"""
import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from evaluate_factors_dynamic_universe import apply_universe_membership_filter
from evaluate_factors import evaluate_one_label, clean_float


# ── Helpers ────────────────────────────────────────────────────────

def _make_data(n_symbols: int = 5, n_months: int = 2, rows_per_month: int = 720):
    """Create synthetic factor values, labels, and snapshots."""
    symbols = [f"S{i}" for i in range(n_symbols)]
    months = ["2024-07", "2024-08"][:n_months]
    rows = []
    for sym in symbols:
        for m in months:
            timestamps = pd.date_range(f"{m}-01", periods=rows_per_month, freq="h", tz="UTC")
            for ts in timestamps:
                rows.append({"timestamp": ts, "symbol": sym,
                             "factor_name": "test", "factor_value": np.random.randn(),
                             "known_at": ts, "source_timeframe": "1h", "computed_at": "x"})
    fv = pd.DataFrame(rows)
    labels = fv[["timestamp", "symbol"]].copy()
    for h in [1, 4, 24, 72]:
        labels[f"ret_fwd_{h}h"] = np.random.randn(len(labels))
    return fv, labels, symbols, months


def _make_snapshots(symbols, months):
    rows = []
    for sym in symbols:
        for m in months:
            rows.append({"symbol": sym, "asof_time": pd.Timestamp(f"{m}-01", tz="UTC")})
    return pd.DataFrame(rows)


# ── Universe membership filter ─────────────────────────────────────

class TestUniverseMembershipFilter:
    def test_keeps_only_selected_symbol_months(self):
        fv, labels, syms, months = _make_data(n_symbols=3, n_months=2)
        # Only select S0 and S1 in month 1, S0 in month 2
        snapshots = _make_snapshots(["S0", "S1"], ["2024-07"]) 
        snap2 = _make_snapshots(["S0"], ["2024-08"])
        snapshots = pd.concat([snapshots, snap2])
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        filtered, n_before, n_after, n_sym, n_mon = apply_universe_membership_filter(fv, labels, snapshots)
        # S2 should be excluded entirely
        assert "S2" not in filtered["symbol"].unique()
        assert n_after < n_before

    def test_rows_outside_universe_excluded(self):
        fv, labels, syms, months = _make_data(n_symbols=2, n_months=2, rows_per_month=100)
        # Only select month 1
        snapshots = _make_snapshots(["S0", "S1"], ["2024-07"])
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        filtered, _, n_after, _, _ = apply_universe_membership_filter(fv, labels, snapshots)
        # All filtered rows should be in July
        assert filtered["timestamp"].dt.strftime("%Y-%m").unique().tolist() == ["2024-07"]

    def test_no_global_missing_rate_exclusion(self):
        """Global missing-rate exclusion must NOT be applied."""
        fv, labels, syms, months = _make_data(n_symbols=2, n_months=1, rows_per_month=100)
        snapshots = _make_snapshots(["S0", "S1"], ["2024-07"])
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        _, n_before, n_after, _, _ = apply_universe_membership_filter(fv, labels, snapshots)
        # All rows should pass — no symbol excluded by missing rate
        assert n_after == n_before


# ── evaluate_one_label receives only selected rows ─────────────────

class TestEvaluateOneLabel:
    def test_receives_only_selected_rows(self):
        fv, labels, syms, months = _make_data(n_symbols=3, n_months=1, rows_per_month=100)
        snapshots = _make_snapshots(["S0", "S1"], ["2024-07"])
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        filtered, _, _, _, _ = apply_universe_membership_filter(fv, labels, snapshots)
        m = evaluate_one_label(filtered, "ret_fwd_1h", "positive")
        # Should not crash and should have valid metrics
        assert m["n_merged_rows"] > 0
        assert "S2" not in filtered["symbol"].unique()

    def test_timestamp_month_convention(self):
        """signal_time = timestamp month = universe_month."""
        fv, labels, syms, months = _make_data(n_symbols=2, n_months=2, rows_per_month=100)
        # Only select July
        snapshots = _make_snapshots(["S0", "S1"], ["2024-07"])
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        filtered, _, _, _, _ = apply_universe_membership_filter(fv, labels, snapshots)
        # All timestamps should be in July
        assert (filtered["timestamp"].dt.strftime("%Y-%m") == "2024-07").all()


# ── Summary schema ─────────────────────────────────────────────────

class TestSummarySchema:
    def test_conditional_direction_no_direction_adjusted_spread(self):
        """conditional expected_direction should not produce direction_adjusted_spread."""
        fv, labels, syms, months = _make_data(n_symbols=3, n_months=1, rows_per_month=100)
        snapshots = _make_snapshots(syms, months)
        snapshots["asof_time"] = pd.to_datetime(snapshots["asof_time"], utc=True)
        snapshots["month_str"] = snapshots["asof_time"].dt.strftime("%Y-%m")

        filtered, _, _, _, _ = apply_universe_membership_filter(fv, labels, snapshots)
        m = evaluate_one_label(filtered, "ret_fwd_1h", "conditional")
        assert m["direction_adjusted_spread"] is None
        assert m["direction_adjusted_tstat"] is None
