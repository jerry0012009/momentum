"""Unit tests for audit_dynamic_universe_data_coverage.py (Phase 6C).

All tests use synthetic data — no real dataset access required.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from audit_dynamic_universe_data_coverage import (
    build_monthly_coverage,
    audit,
)


# ── Helpers ───────────────────────────────────────────────────────

def _make_universe_snap(symbols: list[str], months: list[str]) -> pd.DataFrame:
    """Create synthetic universe_snapshots.parquet."""
    rows = []
    for month in months:
        ms = pd.Timestamp(month + "-01", tz="UTC")
        for rank, sym in enumerate(symbols, 1):
            rows.append({
                "universe_id": "test",
                "asof_time": ms.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "selection_time_start": (ms - pd.offsets.MonthBegin(1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "selection_time_end": ms.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "symbol": sym,
                "rank": rank,
                "rank_metric": "prev_full_month_quote_volume_sum",
                "rank_metric_value": float(rank * 1e8),
                "eligible": True,
                "known_at": ms.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "source": "test",
                "universe_mode": "dynamic_from_current_listed_pool",
                "notes": "",
            })
    return pd.DataFrame(rows)


def _make_bars(symbols: list[str]) -> pd.DataFrame:
    """Create synthetic bars_1h.parquet."""
    rng = np.random.default_rng(42)
    timestamps = pd.date_range("2024-01-01", periods=100, freq="h", tz="UTC")
    rows = []
    for sym in symbols:
        for ts in timestamps:
            rows.append({
                "timestamp": ts,
                "symbol": sym,
                "close": rng.uniform(10, 100),
            })
    return pd.DataFrame(rows)


def _make_labels(symbols: list[str]) -> pd.DataFrame:
    """Create synthetic labels.parquet."""
    rng = np.random.default_rng(42)
    timestamps = pd.date_range("2024-01-01", periods=100, freq="h", tz="UTC")
    rows = []
    for sym in symbols:
        for ts in timestamps:
            rows.append({
                "timestamp": ts,
                "symbol": sym,
                "ret_fwd_1h": rng.normal(0, 0.01),
                "ret_fwd_4h": rng.normal(0, 0.02),
                "ret_fwd_24h": rng.normal(0, 0.05),
                "ret_fwd_72h": rng.normal(0, 0.1),
            })
    return pd.DataFrame(rows)


def _setup_dataset(tmp_path: Path, bars_syms: list[str], labels_syms: list[str] | None = None):
    """Write synthetic bars + labels to the expected paths."""
    dataset_dir = tmp_path / "data" / "cache" / "test_dataset"
    dataset_dir.mkdir(parents=True)
    _make_bars(bars_syms).to_parquet(dataset_dir / "bars_1h.parquet", index=False)

    features_dir = tmp_path / "data" / "features" / "test_dataset"
    features_dir.mkdir(parents=True)
    _make_labels(labels_syms or bars_syms).to_parquet(features_dir / "labels.parquet", index=False)


def _setup_universe(tmp_path: Path, symbols: list[str], months: list[str]):
    """Write synthetic universe snapshots."""
    uni_dir = tmp_path / "data" / "universe" / "test_universe"
    uni_dir.mkdir(parents=True)
    _make_universe_snap(symbols, months).to_parquet(uni_dir / "universe_snapshots.parquet", index=False)


# ── Monthly coverage ──────────────────────────────────────────────

class TestMonthlyCoverage:
    def test_computed_correctly(self):
        """Monthly coverage should compute intersection/missing per month."""
        snap = _make_universe_snap(["A", "B", "C"], ["2024-07", "2024-08"])
        bars_symbols = {"A", "B", "D"}
        monthly = build_monthly_coverage(snap, bars_symbols)

        assert len(monthly) == 2
        assert monthly.iloc[0]["universe_symbols"] == 3
        assert monthly.iloc[0]["intersection"] == 2  # A, B
        assert monthly.iloc[0]["missing_from_bars"] == 1  # C
        assert monthly.iloc[0]["coverage_rate"] == pytest.approx(2 / 3)

    def test_full_coverage(self):
        """When all symbols are in bars, coverage = 1.0."""
        snap = _make_universe_snap(["A", "B"], ["2024-07"])
        bars_symbols = {"A", "B", "C"}
        monthly = build_monthly_coverage(snap, bars_symbols)
        assert monthly.iloc[0]["coverage_rate"] == 1.0


# ── Intersection / missing ────────────────────────────────────────

class TestIntersectionMissing:
    def test_fully_covered(self, tmp_path):
        """All dynamic universe symbols present in bars → ALLOWED."""
        uni_syms = ["A", "B", "C"]
        _setup_universe(tmp_path, uni_syms, ["2024-07"])
        _setup_dataset(tmp_path, bars_syms=["A", "B", "C", "D"])

        # Monkey-patch paths
        import audit_dynamic_universe_data_coverage as mod
        old_root = mod.ROOT
        mod.ROOT = tmp_path
        try:
            summary, monthly, missing = audit("test_universe", "test_dataset")
            assert summary["decision"] == "ALLOWED"
            assert summary["missing_from_bars_count"] == 0
            assert len(missing) == 0
        finally:
            mod.ROOT = old_root

    def test_partially_missing(self, tmp_path):
        """Some dynamic universe symbols missing from bars → NOT_ALLOWED."""
        uni_syms = ["A", "B", "C"]
        _setup_universe(tmp_path, uni_syms, ["2024-07"])
        _setup_dataset(tmp_path, bars_syms=["A", "D"])  # B, C missing

        import audit_dynamic_universe_data_coverage as mod
        old_root = mod.ROOT
        mod.ROOT = tmp_path
        try:
            summary, monthly, missing = audit("test_universe", "test_dataset")
            assert summary["decision"] == "NOT_ALLOWED"
            assert summary["missing_from_bars_count"] == 2
            assert set(missing) == {"B", "C"}
        finally:
            mod.ROOT = old_root


# ── Coverage prevents/allows evaluation ───────────────────────────

class TestDecision:
    def test_missing_bars_prevents_approval(self, tmp_path):
        """Any missing symbol → NOT_ALLOWED."""
        _setup_universe(tmp_path, ["A", "B", "MISSING"], ["2024-07"])
        _setup_dataset(tmp_path, bars_syms=["A", "B"])

        import audit_dynamic_universe_data_coverage as mod
        old_root = mod.ROOT
        mod.ROOT = tmp_path
        try:
            summary, _, _ = audit("test_universe", "test_dataset")
            assert summary["decision"] == "NOT_ALLOWED"
            assert "NOT YET allowed" in summary["decision_text"]
        finally:
            mod.ROOT = old_root

    def test_full_coverage_allows_approval(self, tmp_path):
        """All symbols present → ALLOWED."""
        _setup_universe(tmp_path, ["A", "B"], ["2024-07"])
        _setup_dataset(tmp_path, bars_syms=["A", "B", "C"])

        import audit_dynamic_universe_data_coverage as mod
        old_root = mod.ROOT
        mod.ROOT = tmp_path
        try:
            summary, _, _ = audit("test_universe", "test_dataset")
            assert summary["decision"] == "ALLOWED"
        finally:
            mod.ROOT = old_root


# ── Recommendation ────────────────────────────────────────────────

class TestRecommendation:
    def test_recommends_option_b(self, tmp_path):
        """Report should recommend Option B."""
        _setup_universe(tmp_path, ["A"], ["2024-07"])
        _setup_dataset(tmp_path, bars_syms=["A"])

        import audit_dynamic_universe_data_coverage as mod
        old_root = mod.ROOT
        mod.ROOT = tmp_path
        try:
            summary, _, _ = audit("test_universe", "test_dataset")
            assert "Option B" in summary["recommendation"]
        finally:
            mod.ROOT = old_root
