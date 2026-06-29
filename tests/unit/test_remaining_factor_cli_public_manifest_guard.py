"""Public manifest skip guards for remaining factor-library CLIs."""
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


def test_overlapping_sleeve_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "build_factor_overlapping_sleeve_strategy_diagnostics.py",
        ["--factor-ids", SKIPPED_ID, "--dry-run"],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be overlapping-sleeve diagnosed" in combined
    assert "[1/5] Loading metadata" not in combined


def test_legacy_single_factor_paper_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "run_single_factor_paper_diagnostics.py",
        [
            "--factor-ids",
            SKIPPED_ID,
            "--output-dir",
            str(tmp_path),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be legacy single-factor paper diagnosed" in combined
    assert "Loading labels" not in combined
    assert not (tmp_path / "paper_portfolio_leaderboard.csv").exists()


def test_factor_library_refresh_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "run_factor_library_refresh.py",
        [
            "--stage",
            "overlapping-sleeve-strategy",
            "--factor-ids",
            SKIPPED_ID,
            "--dry-run",
            "--expensive-ok",
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be factor-library refreshed" in combined
    assert "Passthrough args" not in combined
