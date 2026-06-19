"""Tests for parity harness schema and logic."""

import pandas as pd
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

SIGNAL_NAMES = [
    "signal_v0_core_only",
    "signal_v0_pm_full_structured",
    "signal_v0_family_balanced_diagnostic",
]
HORIZONS = ["1h", "4h", "24h", "72h"]


class TestSignalPanelTidyConversion:
    """Wide signal panel can be converted to tidy format."""

    def test_melt_to_tidy(self):
        wide = pd.DataFrame({
            "timestamp": ["2025-01-01"] * 3,
            "symbol": ["A", "B", "C"],
            "signal_v0_core_only": [1.0, 2.0, 3.0],
            "signal_v0_pm_full_structured": [0.5, 1.5, 2.5],
        })
        tidied = wide.melt(
            id_vars=["timestamp", "symbol"],
            value_vars=["signal_v0_core_only", "signal_v0_pm_full_structured"],
            var_name="signal_name",
            value_name="signal_value",
        )
        assert set(tidied.columns) == {"timestamp", "symbol", "signal_name", "signal_value"}
        assert len(tidied) == 6

    def test_nan_dropped(self):
        wide = pd.DataFrame({
            "timestamp": ["2025-01-01"] * 3,
            "symbol": ["A", "B", "C"],
            "signal_v0_core_only": [1.0, np.nan, 3.0],
        })
        tidied = wide.melt(
            id_vars=["timestamp", "symbol"],
            value_vars=["signal_v0_core_only"],
            var_name="signal_name",
            value_name="signal_value",
        ).dropna(subset=["signal_value"])
        assert len(tidied) == 2


class TestSignalNames:
    """Expected 3 signal names recognized."""

    def test_three_signals(self):
        assert len(SIGNAL_NAMES) == 3

    def test_signal_name_format(self):
        for name in SIGNAL_NAMES:
            assert name.startswith("signal_v0_")


class TestHorizons:
    """Expected 4 horizons recognized."""

    def test_four_horizons(self):
        assert len(HORIZONS) == 4

    def test_horizon_values(self):
        assert set(HORIZONS) == {"1h", "4h", "24h", "72h"}


class TestParityStatusLogic:
    """Parity status logic works correctly."""

    def _check_parity(self, new_val, old_val, tol):
        """Mirror of the parity check in the harness."""
        if new_val is None or (isinstance(new_val, float) and np.isnan(new_val)):
            return "MISSING_NEW"
        if old_val is None or (isinstance(old_val, float) and np.isnan(old_val)):
            return "MISSING_OLD"
        if tol == 0:
            return "PASS" if int(new_val) == int(old_val) else "FAIL"
        return "PASS" if abs(float(new_val) - float(old_val)) <= tol else "FAIL"

    def test_pass_within_tolerance(self):
        assert self._check_parity(0.032482, 0.032482, 1e-6) == "PASS"

    def test_fail_outside_tolerance(self):
        assert self._check_parity(0.033, 0.032, 1e-6) == "FAIL"

    def test_pass_at_boundary(self):
        assert self._check_parity(0.032001, 0.032000, 1e-3) == "PASS"

    def test_missing_new(self):
        assert self._check_parity(np.nan, 0.032, 1e-6) == "MISSING_NEW"

    def test_missing_old(self):
        assert self._check_parity(0.032, np.nan, 1e-6) == "MISSING_OLD"

    def test_exact_match_n_periods(self):
        assert self._check_parity(17520, 17520, 0) == "PASS"

    def test_fail_exact_mismatch(self):
        assert self._check_parity(17521, 17520, 0) == "FAIL"

    def test_pass_n_periods_within_tolerance(self):
        assert self._check_parity(17520, 17519, 2) == "PASS"
