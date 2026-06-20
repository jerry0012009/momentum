"""Test factor conclusion cards."""
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"

REQUIRED_CARD_FIELDS = [
    "factor_id", "family", "expected_direction", "best_horizon",
    "best_adj_ic", "monthly_stability_summary", "quantile_monotonicity_summary",
    "rankic_longshort_consistency", "decision_bucket", "recommended_action",
]


@pytest.fixture
def sample_run_dir(tmp_path):
    """Create a minimal run directory with required files for conclusion cards."""
    run_dir = tmp_path / "test_run"
    run_dir.mkdir()

    # Copy the canonical candidate review for rev_1h
    review_path = EVAL_DIR / "factor_level_candidate_review.csv"
    if review_path.exists():
        df = pd.read_csv(review_path)
        df = df[df["factor_name"] == "rev_1h"]
        df.to_csv(run_dir / "factor_candidate_review.csv", index=False)

    # Copy metric panel for rev_1h
    mp_path = EVAL_DIR / "factor_level_metric_panel.csv"
    if mp_path.exists():
        df = pd.read_csv(mp_path)
        df = df[df["factor_name"] == "rev_1h"]
        df.to_csv(run_dir / "factor_metric_panel.csv", index=False)

    # Copy period IC summary for rev_1h
    period_path = EVAL_DIR / "factor_level_period_ic_summary.csv"
    if period_path.exists():
        df = pd.read_csv(period_path)
        df = df[df["factor_name"] == "rev_1h"]
        df.to_csv(run_dir / "factor_period_ic_summary.csv", index=False)

    # Copy quantile return summary for rev_1h
    qr_path = EVAL_DIR / "factor_level_quantile_return_summary.csv"
    if qr_path.exists():
        df = pd.read_csv(qr_path)
        df = df[df["factor_name"] == "rev_1h"]
        df.to_csv(run_dir / "factor_quantile_return_summary.csv", index=False)

    # Create inventory
    inv = pd.DataFrame([{
        "factor_id": "rev_1h",
        "family": "reversal",
        "expected_direction": "positive",
        "required_columns": "close",
        "lookback_window": 1,
        "formula_proxy": "very short-term reversal",
        "fv_exists": True,
    }])
    inv.to_csv(run_dir / "factor_inventory.csv", index=False)

    return run_dir


def test_conclusion_cards_build(sample_run_dir):
    """build_factor_conclusion_cards.py produces valid output."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "build_factor_conclusion_cards.py"),
         "--run-dir", str(sample_run_dir),
         "--factor-ids", "rev_1h"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert (sample_run_dir / "factor_conclusion_cards.csv").exists()
    assert (sample_run_dir / "factor_conclusion_cards.json").exists()


def test_conclusion_cards_have_required_fields(sample_run_dir):
    """Conclusion cards should contain all required fields."""
    import subprocess
    subprocess.run(
        [sys.executable, str(SCRIPTS / "build_factor_conclusion_cards.py"),
         "--run-dir", str(sample_run_dir),
         "--factor-ids", "rev_1h"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    cards_path = sample_run_dir / "factor_conclusion_cards.csv"
    if not cards_path.exists():
        pytest.skip("Cards not generated")
    df = pd.read_csv(cards_path)
    for field in REQUIRED_CARD_FIELDS:
        assert field in df.columns, f"Missing required field: {field}"


def test_conclusion_cards_no_auto_promotion(sample_run_dir):
    """No conclusion card should have decision_bucket = 'AUTO_PROMOTED'."""
    import subprocess
    subprocess.run(
        [sys.executable, str(SCRIPTS / "build_factor_conclusion_cards.py"),
         "--run-dir", str(sample_run_dir),
         "--factor-ids", "rev_1h"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    cards_path = sample_run_dir / "factor_conclusion_cards.csv"
    if not cards_path.exists():
        pytest.skip("Cards not generated")
    df = pd.read_csv(cards_path)
    assert "AUTO_PROMOTED" not in df["decision_bucket"].values, "No factor should be auto-promoted"
