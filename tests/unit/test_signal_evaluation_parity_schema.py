"""Tests for parity harness: verifies public API usage and schema."""

import pytest
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_signal_evaluation_parity_harness.py"
SOURCE = SCRIPT.read_text()


class TestPublicAPIUsage:
    """Harness must use public signal_evaluation API."""

    def test_imports_compute_rank_ic(self):
        assert "from momentum.signal_evaluation" in SOURCE
        assert "compute_rank_ic" in SOURCE

    def test_imports_compute_quantile_spread(self):
        assert "compute_quantile_spread" in SOURCE

    def test_imports_summarize_rank_ic(self):
        assert "summarize_rank_ic" in SOURCE

    def test_imports_summarize_quantile_spread(self):
        assert "summarize_quantile_spread" in SOURCE

    def test_imports_select_forward_return(self):
        assert "select_forward_return" in SOURCE

    def test_imports_check_consistency(self):
        assert "check_rankic_spread_consistency" in SOURCE

    def test_no_fast_rank_ic(self):
        assert "def fast_rank_ic" not in SOURCE, "Must not define inline fast_rank_ic"

    def test_no_fast_quantile_spread(self):
        assert "def fast_quantile_spread" not in SOURCE, "Must not define inline fast_quantile_spread"

    def test_no_scipy_import(self):
        assert "from scipy" not in SOURCE, "Must not import scipy directly — use public API"


class TestParityLevels:
    """Parity output must include parity_level field."""

    def test_rankic_has_parity_level(self):
        assert '"parity_level"' in SOURCE

    def test_spread_has_difference_reason(self):
        assert '"difference_reason"' in SOURCE

    def test_spread_has_behavioral_level(self):
        assert "BEHAVIORAL" in SOURCE


class TestSignalNames:
    """Expected 3 signal names."""

    def test_three_signals(self):
        for name in ["signal_v0_core_only", "signal_v0_pm_full_structured", "signal_v0_family_balanced_diagnostic"]:
            assert name in SOURCE


class TestHorizons:
    """Expected 4 horizons."""

    def test_four_horizons(self):
        for hz in ["1h", "4h", "24h", "72h"]:
            assert f'"{hz}"' in SOURCE
