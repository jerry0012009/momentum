"""Public manifest skip guards for incremental factor diagnostics."""
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


def test_shape_stability_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "build_factor_shape_stability_diagnostics.py",
        ["--factor-ids", SKIPPED_ID],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be shape/stability diagnosed" in combined
    assert "Loading data..." not in combined


def test_decile_shape_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "build_factor_decile_shape_diagnostics.py",
        ["--factor-ids", SKIPPED_ID],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be decile-shape diagnosed" in combined
    assert "Loading labels" not in combined


def test_capacity_liquidity_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "build_factor_capacity_liquidity_diagnostics.py",
        ["--factor-ids", SKIPPED_ID],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be capacity/liquidity diagnosed" in combined
    assert "Loaded turnover data" not in combined
