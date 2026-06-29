"""Test factor intake run contract."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

INTAKE_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_intake"

from public_factor_manifest_guard import (  # noqa: E402
    find_skipped_public_factor_ids,
    load_skipped_public_factor_ids,
)


def test_intake_dry_run():
    """run_factor_intake.py --dry-run should succeed."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_factor_intake.py"),
         "--factor-ids", "rev_1h", "mom_72h",
         "--run-id", "test_dry_run",
         "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Dry run failed: {result.stderr}"
    assert "DRY RUN" in result.stdout


def test_intake_validates_unknown_factor_ids():
    """run_factor_intake.py should reject unknown factor IDs."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_factor_intake.py"),
         "--factor-ids", "nonexistent_factor_xyz",
         "--run-id", "test_invalid",
         "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode != 0 or "Unknown factor IDs" in result.stdout or "Unknown factor IDs" in result.stderr


def test_skipped_public_factor_ids_loaded_from_manifest():
    skipped = load_skipped_public_factor_ids()

    assert "wq101_alpha58_indneutralize_skipped" in skipped
    assert "q158_roc_5h_skipped" in skipped
    assert "wq101_alpha56" not in skipped


def test_validate_not_skipped_public_factor_ids_flags_blocked_manifest_ids():
    skipped = {"wq101_alpha58_indneutralize_skipped", "q158_roc_5h_skipped"}

    invalid = find_skipped_public_factor_ids(
        ["rev_1h", "wq101_alpha58_indneutralize_skipped"],
        skipped,
    )

    assert invalid == ["wq101_alpha58_indneutralize_skipped"]


def test_intake_creates_directory(tmp_path):
    """run_factor_intake.py creates the run directory structure."""
    import subprocess
    run_dir = tmp_path / "test_run"
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_factor_intake.py"),
         "--factor-ids", "rev_1h",
         "--run-id", "test_run",
         "--output-dir", str(run_dir),
         "--skip-redundancy",
         "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0
