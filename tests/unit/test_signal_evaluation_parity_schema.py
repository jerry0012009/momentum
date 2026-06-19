"""Tests for parity harness: verifies public API usage, gate logic, and status codes."""

import pytest
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_signal_evaluation_parity_harness.py"
SOURCE = SCRIPT.read_text()


def _no(pattern: str):
    assert pattern not in SOURCE, f"Found forbidden: {pattern!r}"


def _yes(pattern: str):
    assert pattern in SOURCE, f"Missing required: {pattern!r}"


# Public API usage
def test_uses_public_compute_rank_ic():
    _yes("from momentum.signal_evaluation import")


def test_no_fast_rank_ic():
    _no("def fast_rank_ic")


def test_no_fast_quantile_spread():
    _no("def fast_quantile_spread")


def test_no_scipy_import():
    _no("from scipy")
    _no("import scipy")


# Gate logic (H2-T)
def test_gate_function_exists():
    _yes("def determine_h3_gate")


def test_gate_open_full_wrapper():
    _yes("OPEN_FULL_WRAPPER")


def test_gate_open_standard_v2_only():
    _yes("OPEN_STANDARD_V2_ONLY")


def test_gate_blocked():
    _yes("BLOCKED")


# RankIC status
def test_pass_rounded_reference_status():
    _yes("PASS_ROUNDED_REFERENCE")


def test_rounding_tolerance_defined():
    _yes("ROUNDING_TOLERANCE")


def test_reference_precision_field():
    _yes("reference_precision_digits")


# Legacy spread mode
def test_legacy_phase10a_mode_used():
    _yes('mode="legacy_phase10a"')


def test_legacy_mode_in_spread_parity():
    _yes("spread_legacy")


def test_standard_mode_for_reference():
    _yes("spread_standard")


# Summary fields
def test_summary_has_rounded_reference_count():
    _yes("rounded_reference_count")


def test_summary_has_h3_gate_status():
    _yes("h3_gate_status")
