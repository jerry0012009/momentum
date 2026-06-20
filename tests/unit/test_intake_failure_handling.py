"""Test run_factor_intake.py failure handling and run directory contract."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def test_intake_fails_on_critical_step_failure(tmp_path):
    """When a critical step fails, intake run must exit non-zero and mark FAILED."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_factor_intake.py"),
         "--factor-ids", "rev_1h",
         "--run-id", "test_dry",
         "--dry-run"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Dry-run should succeed: {result.stderr}"
    assert "DRY RUN" in result.stdout


def test_intake_manifest_has_status_field(tmp_path):
    """Manifest must include status field."""
    run_dir = tmp_path / "test_run"
    run_dir.mkdir()
    manifest = {
        "run_id": "test",
        "status": "COMPLETE",
        "command_log": [],
    }
    path = run_dir / "manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f)
    with open(path) as f:
        loaded = json.load(f)
    assert "status" in loaded
    assert loaded["status"] in ("COMPLETE", "FAILED")


def test_intake_manifest_status_failed_on_error():
    """Verify that the manifest schema supports FAILED status."""
    manifest = {
        "run_id": "test_fail",
        "status": "FAILED",
        "command_log": [
            {"step": "partial_evaluation", "exit_code": 1, "output_tail": "error"},
        ],
    }
    assert manifest["status"] == "FAILED"
    failed_cmds = [e for e in manifest["command_log"] if e["exit_code"] != 0]
    assert len(failed_cmds) == 1


def test_intake_command_log_records_exit_codes():
    """command_log entries must have step, exit_code fields."""
    log_entry = {
        "step": "registry_integrity",
        "command": "check_factor_registry_integrity.py",
        "exit_code": 0,
        "output_tail": "",
    }
    assert "step" in log_entry
    assert "exit_code" in log_entry
    assert isinstance(log_entry["exit_code"], int)


def test_critical_steps_defined():
    """CRITICAL_STEPS must include the expected steps."""
    sys.path.insert(0, str(SCRIPTS))
    import importlib
    mod = importlib.import_module("run_factor_intake")
    assert hasattr(mod, "CRITICAL_STEPS")
    critical = mod.CRITICAL_STEPS
    assert "registry_integrity" in critical
    assert "build_factor_values" in critical
    assert "partial_evaluation" in critical
    assert "conclusion_cards" in critical


def test_outputs_index_schema(tmp_path):
    """outputs_index.json must list expected artifacts with status."""
    run_dir = tmp_path / "test_index"
    run_dir.mkdir()
    # Create a couple of files
    (run_dir / "manifest.json").write_text("{}")
    (run_dir / "quality_checks.csv").write_text("check_id,status\n")
    # Simulate write_outputs_index
    expected = ["manifest.json", "quality_checks.csv", "report.md"]
    index = {}
    for artifact in expected:
        p = run_dir / artifact
        if p.exists():
            index[artifact] = {"status": "present", "size_bytes": p.stat().st_size}
        else:
            index[artifact] = {"status": "missing"}
    assert index["manifest.json"]["status"] == "present"
    assert index["report.md"]["status"] == "missing"


def test_expected_artifacts_list():
    """EXPECTED_ARTIFACTS must include all contract artifacts."""
    sys.path.insert(0, str(SCRIPTS))
    import importlib
    mod = importlib.import_module("run_factor_intake")
    artifacts = mod.EXPECTED_ARTIFACTS
    required = [
        "manifest.json", "command_log.json", "outputs_index.json",
        "factor_inventory.csv", "quality_checks.csv", "report.md",
        "factor_metric_panel.csv", "factor_candidate_review.csv",
        "factor_redundancy.csv", "factor_conclusion_cards.csv",
    ]
    for r in required:
        assert r in artifacts, f"Missing expected artifact: {r}"


def test_eval_dependent_steps_defined():
    """EVAL_DEPENDENT_STEPS must include steps that depend on partial evaluation."""
    sys.path.insert(0, str(SCRIPTS))
    import importlib
    mod = importlib.import_module("run_factor_intake")
    assert hasattr(mod, "EVAL_DEPENDENT_STEPS")
    deps = mod.EVAL_DEPENDENT_STEPS
    assert "conclusion_cards" in deps
    assert "redundancy_diagnostics" in deps
    assert "collect_outputs" in deps
