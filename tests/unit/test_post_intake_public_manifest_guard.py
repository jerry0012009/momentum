"""Public manifest skip guards for post-intake CLIs."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def _run(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script_name)] + args,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=30,
    )


def test_post_intake_completion_rejects_skipped_public_factor_id() -> None:
    result = _run(
        "run_post_intake_workflow_completion.py",
        [
            "--factor-ids",
            "wq101_alpha58_indneutralize_skipped",
            "--dry-run",
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be post-intake processed" in combined


def test_post_intake_integrity_rejects_skipped_public_factor_id(tmp_path: Path) -> None:
    result = _run(
        "check_post_intake_workflow_integrity.py",
        [
            "--factor-ids",
            "wq101_alpha58_indneutralize_skipped",
            "--output-dir",
            str(tmp_path),
        ],
    )

    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Public manifest skipped factor IDs cannot be post-intake integrity checked" in combined
    assert not (tmp_path / "post_intake_workflow_integrity_report.csv").exists()
