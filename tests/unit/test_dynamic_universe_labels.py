"""Unit tests for build_labels.py and audit_dynamic_universe_labels.py (Phase 6E).

All tests use synthetic data.
"""
import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from build_labels import build_labels
from audit_dynamic_universe_labels import (
    compute_global_coverage,
    compute_membership_aware_coverage,
    compute_qa_decision,
)


# ── Helpers ────────────────────────────────────────────────────────

def _make_bars(symbol: str, start: str, hours: int, close_start: float = 100.0) -> pd.DataFrame:
    """Create synthetic hourly bars for one symbol."""
    timestamps = pd.date_range(start, periods=hours, freq="h", tz="UTC")
    close = close_start + np.cumsum(np.random.randn(hours) * 0.5)
    close = np.maximum(close, 1.0)  # keep positive
    return pd.DataFrame({
        "timestamp": timestamps,
        "symbol": symbol,
        "close": close,
    })


def _make_snapshots(symbol_months: dict[str, list[str]]) -> pd.DataFrame:
    """Create synthetic universe snapshots."""
    rows = []
    for sym, months in symbol_months.items():
        for m in months:
            rows.append({"symbol": sym, "asof_time": pd.Timestamp(f"{m}-01", tz="UTC")})
    return pd.DataFrame(rows)


# ── Calendar-time join ─────────────────────────────────────────────

class TestCalendarTimeJoin:
    def test_exact_match_1h(self):
        """ret_fwd_1h should be close[t+1]/close[t] - 1."""
        bars = _make_bars("SYM", "2024-07-01", 10)
        labels = build_labels(bars, [1])
        # Manual check for first row
        expected = bars.iloc[1]["close"] / bars.iloc[0]["close"] - 1
        assert abs(labels.iloc[0]["ret_fwd_1h"] - expected) < 1e-10

    def test_gap_causes_nan_not_shift(self):
        """Gap in bars should produce NaN, not row-shift fallback."""
        # Create bars with a gap at hour 5
        timestamps = pd.date_range("2024-07-01", periods=10, freq="h", tz="UTC")
        # Remove hour 5
        keep = [i for i in range(10) if i != 5]
        bars = pd.DataFrame({
            "timestamp": [timestamps[i] for i in keep],
            "symbol": "SYM",
            "close": [100.0 + i for i in keep],
        })
        labels = build_labels(bars, [1])
        # Row at hour 4 should have NaN for ret_fwd_1h (hour 5 missing)
        row_4 = labels[labels["timestamp"] == timestamps[4]]
        assert len(row_4) == 1
        assert pd.isna(row_4.iloc[0]["ret_fwd_1h"])

    def test_all_horizons_created(self):
        """All 4 horizons should be created."""
        bars = _make_bars("SYM", "2024-07-01", 100)
        labels = build_labels(bars, [1, 4, 24, 72])
        for h in [1, 4, 24, 72]:
            assert f"ret_fwd_{h}h" in labels.columns

    def test_tail_horizon_missing(self):
        """Last N rows should have NaN for ret_fwd_Nh."""
        bars = _make_bars("SYM", "2024-07-01", 100)
        labels = build_labels(bars, [1, 4, 24, 72])
        # Last row: all horizons NaN
        last = labels.iloc[-1]
        assert pd.isna(last["ret_fwd_1h"])
        assert pd.isna(last["ret_fwd_72h"])
        # Second-to-last: 1h has data, 72h is NaN
        second_last = labels.iloc[-2]
        assert not pd.isna(second_last["ret_fwd_1h"])
        assert pd.isna(second_last["ret_fwd_72h"])

    def test_multiple_symbols(self):
        """Labels should handle multiple symbols independently."""
        bars_a = _make_bars("A", "2024-07-01", 10)
        bars_b = _make_bars("B", "2024-07-01", 10)
        bars = pd.concat([bars_a, bars_b], ignore_index=True)
        labels = build_labels(bars, [1])
        assert labels["symbol"].nunique() == 2
        assert len(labels) == 20


# ── Membership-aware label coverage ────────────────────────────────

class TestMembershipAwareLabelCoverage:
    def test_selected_coverage_computed(self):
        """Membership-aware coverage should filter to selected months."""
        bars = _make_bars("SYM", "2024-07-01", 744)  # July
        labels = build_labels(bars, [1])
        snapshots = _make_snapshots({"SYM": ["2024-07"]})

        summary, _, _ = compute_membership_aware_coverage(labels, snapshots)
        assert summary["selected_label_rows"] > 0
        assert summary["selected_ret_fwd_1h_missing_rate"] < 0.01

    def test_tail_missing_counted(self):
        """Tail horizon missing should be counted in missing rate."""
        bars = _make_bars("SYM", "2024-07-01", 100)
        labels = build_labels(bars, [72])
        snapshots = _make_snapshots({"SYM": ["2024-07"]})

        summary, _, _ = compute_membership_aware_coverage(labels, snapshots)
        # 72h missing should be ~72/100 = 72% (tail)
        assert summary["selected_ret_fwd_72h_missing_rate"] > 0.5

    def test_high_selected_missing_blocks(self):
        """High selected missing rate should block Phase 6F."""
        summary = {
            "selected_ret_fwd_1h_missing_rate": 0.05,  # 5% > 1% threshold
            "selected_ret_fwd_4h_missing_rate": 0.0,
            "selected_ret_fwd_24h_missing_rate": 0.0,
            "selected_ret_fwd_72h_missing_rate": 0.0,
        }
        qa = compute_qa_decision(summary)
        assert qa["decision"] == "BLOCKED"

    def test_acceptable_missing_allows(self):
        """Low missing rates should allow Phase 6F."""
        summary = {
            "selected_ret_fwd_1h_missing_rate": 0.0001,
            "selected_ret_fwd_4h_missing_rate": 0.0003,
            "selected_ret_fwd_24h_missing_rate": 0.002,
            "selected_ret_fwd_72h_missing_rate": 0.01,
        }
        qa = compute_qa_decision(summary)
        assert qa["decision"] == "ALLOWED"

    def test_global_coverage_schema(self):
        """Global coverage should have required keys."""
        bars = _make_bars("SYM", "2024-07-01", 100)
        labels = build_labels(bars, [1, 4, 24, 72])
        global_cov = compute_global_coverage(labels)
        assert "n_label_rows" in global_cov
        for h in [1, 4, 24, 72]:
            assert f"ret_fwd_{h}h_missing_rate" in global_cov
