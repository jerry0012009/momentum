"""Focused tests for post-intake all-active PM-58 integrity helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import check_post_intake_workflow_integrity as workflow  # noqa: E402


def _write_pm58b_inputs(
    tmp_path: Path,
    *,
    monthly_mean: float,
    annualized_return: float,
) -> None:
    eval_dir = tmp_path / "eval"
    diag_dir = tmp_path / "diag"
    eval_dir.mkdir()
    diag_dir.mkdir()

    pd.DataFrame([
        {
            "factor_name": "factor_a",
            "horizon": "1h",
            "long_short_spread_mean": monthly_mean,
            "long_short_spread_annualized_return": annualized_return,
            "annualization_method": "per_bar_mean_x_bars_per_year",
        }
    ]).to_csv(eval_dir / "factor_level_long_short_summary.csv", index=False)
    pd.DataFrame([
        {
            "factor_id": "factor_a",
            "horizon": "1h",
            "long_short_return": monthly_mean,
        }
    ]).to_csv(diag_dir / "factor_monthly_long_short_series.csv", index=False)

    workflow.EVAL_DIR = eval_dir
    workflow.DIAG_DIR = diag_dir


def test_has_non_pass_result_flags_all_non_ok_statuses() -> None:
    assert workflow._has_non_pass_result([{"status": "OK"}, {"status": "PASS"}]) is False
    assert workflow._has_non_pass_result([{"status": "OK"}, {"status": "FAIL"}]) is True
    assert workflow._has_non_pass_result([{"status": "MISSING"}]) is True


def test_pm58b_allows_horizon_scaled_csv_rounding(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workflow, "EVAL_DIR", tmp_path / "eval")
    monkeypatch.setattr(workflow, "DIAG_DIR", tmp_path / "diag")
    monthly_mean = 0.0000429196
    _write_pm58b_inputs(
        tmp_path,
        monthly_mean=monthly_mean,
        annualized_return=monthly_mean * 8760 + 0.00003,
    )

    results = workflow._check_pm58b_ls_annualization_consistency()

    assert [row["status"] for row in results] == ["OK", "OK"]


def test_pm58b_rejects_material_annualization_mismatch(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(workflow, "EVAL_DIR", tmp_path / "eval")
    monkeypatch.setattr(workflow, "DIAG_DIR", tmp_path / "diag")
    monthly_mean = 0.0000429196
    _write_pm58b_inputs(
        tmp_path,
        monthly_mean=monthly_mean,
        annualized_return=monthly_mean * 8760 + 0.001,
    )

    results = workflow._check_pm58b_ls_annualization_consistency()

    assert results[0]["status"] == "OK"
    assert results[1]["status"] == "FAIL"
    assert "ann_ret != monthly_mean" in results[1]["detail"]
