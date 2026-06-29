"""Public manifest skip guards for pairwise and paper diagnostics."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
SKIPPED_ID = "wq101_alpha58_indneutralize_skipped"


def _run(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)] + args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=30,
    )


def test_pairwise_redundancy_matrix_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "build_factor_pairwise_redundancy_matrix.py",
        [
            "--factor-ids",
            SKIPPED_ID,
            "--output-dir",
            str(tmp_path),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be pairwise-redundancy diagnosed" in combined
    assert "Loading and sampling factors" not in combined
    assert not (tmp_path / "factor_pairwise_redundancy.csv").exists()


def test_single_factor_paper_diagnostics_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "build_single_factor_paper_portfolio_diagnostics.py",
        [
            "--factor-ids",
            SKIPPED_ID,
            "--output-dir",
            str(tmp_path),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be single-factor paper diagnosed" in combined
    assert "Loading labels" not in combined
    assert not (tmp_path / "single_factor_paper_summary.csv").exists()
