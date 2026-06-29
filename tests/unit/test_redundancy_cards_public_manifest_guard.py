"""Public manifest skip guards for redundancy and conclusion-card CLIs."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _run(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)] + args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=30,
    )


def test_redundancy_library_mode_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "build_factor_redundancy.py",
        [
            "--factor-ids",
            "rev_1h",
            "wq101_alpha58_indneutralize_skipped",
            "--output",
            str(tmp_path / "redundancy.csv"),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be redundancy checked" in combined
    assert not (tmp_path / "redundancy.csv").exists()


def test_redundancy_intake_mode_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "build_factor_redundancy.py",
        [
            "--intake-factor-ids",
            "wq101_alpha58_indneutralize_skipped",
            "--baseline-factor-ids",
            "rev_1h",
            "--output",
            str(tmp_path / "redundancy.csv"),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be redundancy checked" in combined
    assert not (tmp_path / "redundancy.csv").exists()


def test_conclusion_cards_explicit_factor_ids_reject_skipped_public_factor_id(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    result = _run(
        "build_factor_conclusion_cards.py",
        [
            "--run-dir",
            str(run_dir),
            "--factor-ids",
            "wq101_alpha58_indneutralize_skipped",
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be conclusion-carded" in combined
    assert not (run_dir / "factor_conclusion_cards.csv").exists()


def test_conclusion_cards_inventory_inferred_ids_reject_skipped_public_factor_id(tmp_path: Path) -> None:
    from build_factor_conclusion_cards import build_cards

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    pd.DataFrame(
        {
            "factor_id": ["wq101_alpha58_indneutralize_skipped"],
            "family": ["alpha101"],
            "fv_exists": [False],
        }
    ).to_csv(run_dir / "factor_inventory.csv", index=False)

    with pytest.raises(ValueError, match="Public manifest skipped factor IDs cannot be conclusion-carded"):
        build_cards(run_dir, factor_ids=None)
