"""Tests for Phase 12C Grand Transparency Closeout."""
import os
import pandas as pd
import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
BASE = os.path.join(ROOT, "research", "factor_runs", "crypto_top50_factor_library")
TRANS = os.path.join(ROOT, "docs", "factor_library_transparency")


def _f(name, base=BASE):
    return os.path.join(base, name)


# --- Grand closeout ---
def test_closeout_exists():
    assert os.path.exists(_f("PHASE_12C_GRAND_TRANSPARENCY_CLOSEOUT.md"))


def test_closeout_negative_declarations():
    t = open(_f("PHASE_12C_GRAND_TRANSPARENCY_CLOSEOUT.md")).read().lower()
    for kw in ["phase 13 not started", "no real execution", "no alpha claim", "no final production model"]:
        assert kw in t, f"Missing: {kw}"


# --- Transparency docs ---
def test_transparency_readme_exists():
    assert os.path.exists(_f("README.md", TRANS))


def test_data_lineage_exists():
    assert os.path.exists(_f("data_lineage.md", TRANS))


def test_workflow_map_exists():
    assert os.path.exists(_f("workflow_map.md", TRANS))


def test_factor_handbook_exists():
    assert os.path.exists(_f("factor_handbook.md", TRANS))


def test_signal_handbook_exists():
    assert os.path.exists(_f("signal_construction_handbook.md", TRANS))


def test_evaluation_methodology_exists():
    assert os.path.exists(_f("evaluation_methodology.md", TRANS))


def test_phase_summary_table_exists():
    assert os.path.exists(_f("phase_summary_table.csv", TRANS))


def test_phase_decision_log_exists():
    assert os.path.exists(_f("phase_decision_log.md", TRANS))


def test_risk_register_exists():
    assert os.path.exists(_f("risk_register.csv", TRANS))


def test_pm_decision_memo_exists():
    assert os.path.exists(_f("pm_decision_memo_phase13_readiness.md", TRANS))


def test_phase13_checklist_exists():
    assert os.path.exists(_f("phase13_readiness_checklist.csv", TRANS))


def test_index_html_exists():
    assert os.path.exists(_f("index.html", TRANS))


# --- Content checks ---
def test_factor_handbook_covers_all_10():
    t = open(_f("factor_handbook.md", TRANS)).read().lower()
    for factor in ["vol_5h", "vol_40h", "downside_vol_20h", "vol_of_vol_20h",
                   "rsi_7h", "rsi_28h", "xs_rank_vol", "range_1h", "range_4h", "price_pos_24h"]:
        assert factor in t, f"Factor not documented: {factor}"


def test_phase_summary_has_all_phases():
    df = pd.read_csv(_f("phase_summary_table.csv", TRANS))
    phases = df["phase_name"].tolist()
    for p in ["Phase 7", "Phase 9B", "Phase 10A", "Phase 10D-R", "Phase 11A",
              "Phase 11B", "Phase 12A", "Phase 12B", "Phase 12C"]:
        assert p in phases, f"Missing phase: {p}"


def test_risk_register_has_minimum_risks():
    df = pd.read_csv(_f("risk_register.csv", TRANS))
    assert len(df) >= 10, f"Only {len(df)} risks (need >= 10)"


def test_risk_register_has_required_columns():
    df = pd.read_csv(_f("risk_register.csv", TRANS))
    for col in ["risk_id", "severity", "likelihood", "evidence", "mitigation"]:
        assert col in df, f"Missing column: {col}"


# --- Negative checks ---
def test_phase13_not_started():
    import glob
    p13 = glob.glob(os.path.join(BASE, "phase13_*.csv"))
    p13 += glob.glob(os.path.join(BASE, "PHASE_13_*.md"))
    assert len(p13) == 0, f"Phase 13 artifacts found: {p13}"


# --- Quality checks ---
def test_quality_checks_exist():
    assert os.path.exists(_f("phase12c_transparency_quality_checks.csv"))


def test_quality_checks_all_pass():
    df = pd.read_csv(_f("phase12c_transparency_quality_checks.csv"))
    failed = df[df["status"] != "PASS"]
    assert len(failed) == 0, f"Failed checks: {failed['check_name'].tolist()}"
