"""Test conclusion cards schema guards — missing review CSV, missing columns."""
import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_missing_review_csv_returns_empty(tmp_path):
    """When factor_candidate_review.csv is missing, build_cards should not crash."""
    from build_factor_conclusion_cards import build_cards
    # Create a run dir with only inventory (no review CSV)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    inv = pd.DataFrame({"factor_id": ["rev_1h"], "family": ["reversal"], "fv_exists": [True]})
    inv.to_csv(run_dir / "factor_inventory.csv", index=False)
    result = build_cards(run_dir, factor_ids=["rev_1h"])
    # Should return a DataFrame (not crash), with UNKNOWN or default values
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert result.iloc[0]["factor_id"] == "rev_1h"


def test_empty_review_csv_returns_empty(tmp_path):
    """When factor_candidate_review.csv is empty, build_cards should not crash."""
    from build_factor_conclusion_cards import build_cards
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    # Empty review CSV (header only or truly empty)
    (run_dir / "factor_candidate_review.csv").write_text("")
    inv = pd.DataFrame({"factor_id": ["rev_1h"], "family": ["reversal"], "fv_exists": [True]})
    inv.to_csv(run_dir / "factor_inventory.csv", index=False)
    result = build_cards(run_dir, factor_ids=["rev_1h"])
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_review_missing_factor_name_column(tmp_path):
    """When review CSV exists but lacks factor_name column, should not KeyError."""
    from build_factor_conclusion_cards import build_cards
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    # Review CSV with wrong columns
    review = pd.DataFrame({"wrong_col": ["rev_1h"], "some_value": [0.5]})
    review.to_csv(run_dir / "factor_candidate_review.csv", index=False)
    inv = pd.DataFrame({"factor_id": ["rev_1h"], "family": ["reversal"], "fv_exists": [True]})
    inv.to_csv(run_dir / "factor_inventory.csv", index=False)
    result = build_cards(run_dir, factor_ids=["rev_1h"])
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1


def test_inventory_missing_factor_id_column(tmp_path):
    """When inventory CSV exists but lacks factor_id column, should not KeyError."""
    from build_factor_conclusion_cards import build_cards
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    # Inventory with wrong columns
    inv = pd.DataFrame({"wrong_col": ["rev_1h"]})
    inv.to_csv(run_dir / "factor_inventory.csv", index=False)
    # No review CSV, no explicit factor_ids — should return empty gracefully
    result = build_cards(run_dir, factor_ids=None)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_no_files_at_all(tmp_path):
    """When run dir is empty, build_cards should return empty DataFrame."""
    from build_factor_conclusion_cards import build_cards
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    result = build_cards(run_dir, factor_ids=None)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
