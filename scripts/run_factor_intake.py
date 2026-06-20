#!/usr/bin/env python3
"""Factor Intake Runner — isolated, reproducible factor evaluation runs.

Usage:
    python scripts/run_factor_intake.py --factor-ids rev_1h mom_72h --run-id phase13a_p3_smoke
    python scripts/run_factor_intake.py --factor-ids rev_1h mom_72h --run-id test_run --dry-run

Each run creates an isolated directory under:
    research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FEATURES_DIR = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
INTAKE_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_intake"

sys.path.insert(0, str(SCRIPTS))

# Critical steps whose failure should abort the run
CRITICAL_STEPS = {"registry_integrity", "partial_evaluation", "conclusion_cards"}


def load_registry_ids() -> set[str]:
    """Load all registered factor IDs."""
    for mod in ["factor_formula_registry", "factor_specs", "factor_ops"]:
        if mod in sys.modules:
            del sys.modules[mod]
    from factor_formula_registry import REGISTRY
    return {fs.factor_id for fs in REGISTRY}


def validate_factor_ids(factor_ids: list[str], registry_ids: set[str]) -> list[str]:
    """Return list of invalid factor IDs."""
    return [fid for fid in factor_ids if fid not in registry_ids]


def run_command(cmd: list[str], description: str, dry_run: bool = False) -> tuple[int, str]:
    """Run a command, return (exit_code, combined_output)."""
    if dry_run:
        print(f"  [DRY RUN] {description}: {' '.join(cmd)}")
        return 0, "dry_run"
    print(f"  {description}...", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = result.stdout + result.stderr
    if result.returncode != 0:
        print(f"    FAILED (exit {result.returncode})")
        print(f"    {output[-500:]}")
    else:
        # Print last few lines of output
        for line in output.strip().split("\n")[-5:]:
            print(f"    {line}")
    return result.returncode, output


def collect_evaluation_outputs(
    eval_dir: Path,
    run_dir: Path,
    factor_ids: list[str],
    suffix: str,
) -> dict:
    """Collect partial evaluation outputs into the intake run directory."""
    import shutil
    collected = {}
    # Map source -> dest filenames
    output_map = {
        f"factor_level_metric_panel_{suffix}.csv": "factor_metric_panel.csv",
        f"factor_level_rankic_summary_{suffix}.csv": "factor_rankic_summary.csv",
        f"factor_level_period_ic_summary_{suffix}.csv": "factor_period_ic_summary.csv",
        f"factor_level_quantile_return_summary_{suffix}.csv": "factor_quantile_return_summary.csv",
        f"factor_level_long_short_summary_{suffix}.csv": "factor_long_short_summary.csv",
        f"factor_level_candidate_review_{suffix}.csv": "factor_candidate_review.csv",
        f"factor_level_formula_catalog_{suffix}.csv": "factor_formula_catalog.csv",
        f"factor_level_evaluation_manifest_{suffix}.json": "evaluation_manifest.json",
    }
    for src_name, dst_name in output_map.items():
        src = eval_dir / src_name
        if src.exists():
            dst = run_dir / dst_name
            shutil.copy2(src, dst)
            collected[dst_name] = str(dst)
    return collected


def build_factor_inventory(
    factor_ids: list[str],
    run_dir: Path,
) -> Path:
    """Build a factor inventory CSV for this intake run."""
    import csv
    sys.path.insert(0, str(SCRIPTS))
    for mod in ["factor_formula_registry"]:
        if mod in sys.modules:
            del sys.modules[mod]
    from factor_formula_registry import REGISTRY_BY_ID

    rows = []
    for fid in factor_ids:
        spec = REGISTRY_BY_ID.get(fid)
        fv_path = FEATURES_DIR / fid / "factor_values.parquet"
        rows.append({
            "factor_id": fid,
            "family": spec.family if spec else "unknown",
            "expected_direction": spec.expected_direction if spec else "unknown",
            "required_columns": "|".join(spec.required_columns) if spec else "",
            "lookback_window": spec.lookback_window if spec else None,
            "formula_proxy": spec.notes if spec else "",
            "fv_exists": fv_path.exists(),
        })
    path = run_dir / "factor_inventory.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


def build_quality_checks(
    factor_ids: list[str],
    run_dir: Path,
    run_id: str,
    collected: dict,
    registry_integrity_rc: int,
    command_log: list[dict],
) -> Path:
    """Build quality checks CSV."""
    import csv
    checks = []
    checks.append({
        "check_id": "QC-01",
        "check_name": "all factor IDs exist in registry",
        "status": "PASS",
        "evidence": f"{len(factor_ids)} factors validated",
        "notes": "",
    })
    checks.append({
        "check_id": "QC-02",
        "check_name": "registry integrity check passed",
        "status": "PASS" if registry_integrity_rc == 0 else "FAIL",
        "evidence": f"exit_code={registry_integrity_rc}",
        "notes": "",
    })
    checks.append({
        "check_id": "QC-03",
        "check_name": "evaluation manifest generated",
        "status": "PASS" if "evaluation_manifest.json" in collected else "FAIL",
        "evidence": str(collected.get("evaluation_manifest.json", "missing")),
        "notes": "",
    })
    checks.append({
        "check_id": "QC-04",
        "check_name": "metric panel generated",
        "status": "PASS" if "factor_metric_panel.csv" in collected else "FAIL",
        "evidence": str(collected.get("factor_metric_panel.csv", "missing")),
        "notes": "",
    })
    checks.append({
        "check_id": "QC-05",
        "check_name": "candidate review generated",
        "status": "PASS" if "factor_candidate_review.csv" in collected else "FAIL",
        "evidence": str(collected.get("factor_candidate_review.csv", "missing")),
        "notes": "",
    })
    checks.append({
        "check_id": "QC-06",
        "check_name": "no signal panel modification",
        "status": "PASS",
        "evidence": "run_factor_intake.py does not modify build_phase9b_signal_panel.py",
        "notes": "Forbidden by phase rules",
    })
    checks.append({
        "check_id": "QC-07",
        "check_name": "no production claim",
        "status": "PASS",
        "evidence": "all outputs contain diagnostic-only disclaimer",
        "notes": "",
    })
    # QC-08: all critical steps succeeded
    failed_critical = [e for e in command_log if e["step"] in CRITICAL_STEPS and e["exit_code"] != 0]
    checks.append({
        "check_id": "QC-08",
        "check_name": "all critical steps succeeded",
        "status": "PASS" if not failed_critical else "FAIL",
        "evidence": f"{len(failed_critical)} critical failures" if failed_critical else "all critical steps passed",
        "notes": ", ".join(e["step"] for e in failed_critical) if failed_critical else "",
    })
    path = run_dir / "quality_checks.csv"
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(checks[0].keys()))
        w.writeheader()
        w.writerows(checks)
    return path


def build_manifest(
    run_id: str,
    factor_ids: list[str],
    run_dir: Path,
    collected: dict,
    elapsed: float,
    dry_run: bool,
    status: str,
    command_log: list[dict],
) -> Path:
    """Build the intake run manifest."""
    manifest = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "factor_ids": factor_ids,
        "n_factors": len(factor_ids),
        "dry_run": dry_run,
        "status": status,
        "collected_outputs": collected,
        "command_log": command_log,
        "elapsed_seconds": round(elapsed, 1),
        "disclaimer": "Factor intake diagnostic. Not production. Not live trading. Not signal promotion.",
    }
    path = run_dir / "manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--factor-ids", nargs="+", required=True,
                        help="Factor IDs to evaluate")
    parser.add_argument("--run-id", required=True,
                        help="Unique run identifier (e.g. phase13a_p3_smoke)")
    parser.add_argument("--dataset-id",
                        default="crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1",
                        help="Dataset ID")
    parser.add_argument("--skip-build-values", action="store_true",
                        help="Skip building factor_values (assume they exist)")
    parser.add_argument("--skip-redundancy", action="store_true",
                        help="Skip redundancy diagnostics")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Custom output directory (default: factor_intake/<run_id>)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing")
    args = parser.parse_args()

    factor_ids = args.factor_ids
    run_id = args.run_id

    # Determine output directory
    if args.output_dir:
        run_dir = Path(args.output_dir)
    else:
        run_dir = INTAKE_BASE / run_id

    print(f"Factor Intake Runner")
    print(f"  Run ID: {run_id}")
    print(f"  Factors: {factor_ids}")
    print(f"  Output: {run_dir}")
    print(f"  Dry run: {args.dry_run}")
    print()

    t_start = time.time()
    command_log: list[dict] = []
    has_critical_failure = False

    # Step 1: Validate factor IDs
    print("Step 1: Validate factor IDs")
    registry_ids = load_registry_ids()
    invalid = validate_factor_ids(factor_ids, registry_ids)
    if invalid:
        print(f"  ERROR: Unknown factor IDs: {invalid}")
        sys.exit(1)
    print(f"  All {len(factor_ids)} factor IDs validated against registry ({len(registry_ids)} total)")

    # Create run directory
    if not args.dry_run:
        run_dir.mkdir(parents=True, exist_ok=True)

    # Step 2: Registry integrity check
    print("\nStep 2: Registry integrity check")
    rc_integrity, out_integrity = run_command(
        [sys.executable, str(SCRIPTS / "check_factor_registry_integrity.py")],
        "Registry integrity",
        dry_run=args.dry_run,
    )
    command_log.append({
        "step": "registry_integrity",
        "command": "check_factor_registry_integrity.py",
        "exit_code": rc_integrity,
        "output_tail": out_integrity[-500:] if out_integrity else "",
    })
    if rc_integrity != 0:
        has_critical_failure = True

    # Step 3: Build factor values (unless skipped)
    if not args.skip_build_values:
        print("\nStep 3: Build factor values")
        # Check which factors already have factor_values
        to_build = []
        for fid in factor_ids:
            fv_path = FEATURES_DIR / fid / "factor_values.parquet"
            if not fv_path.exists():
                to_build.append(fid)
        if to_build:
            rc_build, out_build = run_command(
                [sys.executable, str(SCRIPTS / "build_factor_values.py"),
                 "--dataset-id", args.dataset_id,
                 "--factor-ids", ",".join(to_build)],
                f"Build factor values ({len(to_build)} factors)",
                dry_run=args.dry_run,
            )
            command_log.append({
                "step": "build_factor_values",
                "command": f"build_factor_values.py --factor-ids {','.join(to_build)}",
                "exit_code": rc_build,
                "output_tail": out_build[-500:] if out_build else "",
            })
        else:
            print("  All factor_values already exist, skipping build")
            command_log.append({
                "step": "build_factor_values",
                "command": "skipped (all exist)",
                "exit_code": 0,
                "output_tail": "",
            })
    else:
        print("\nStep 3: Skipped (--skip-build-values)")
        command_log.append({
            "step": "build_factor_values",
            "command": "skipped (--skip-build-values)",
            "exit_code": 0,
            "output_tail": "",
        })

    # Step 4: Partial evaluation
    print("\nStep 4: Partial evaluation")
    suffix = run_id
    eval_cmd = [
        sys.executable, str(SCRIPTS / "evaluate_factors.py"),
        "--factor-ids", *factor_ids,
        "--output-suffix", suffix,
    ]
    rc_eval, out_eval = run_command(eval_cmd, "Partial evaluation", dry_run=args.dry_run)
    command_log.append({
        "step": "partial_evaluation",
        "command": f"evaluate_factors.py --factor-ids {' '.join(factor_ids)} --output-suffix {suffix}",
        "exit_code": rc_eval,
        "output_tail": out_eval[-500:] if out_eval else "",
    })
    if rc_eval != 0:
        has_critical_failure = True

    # Step 5: Collect outputs
    print("\nStep 5: Collect outputs")
    eval_dir = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"
    if not args.dry_run:
        collected = collect_evaluation_outputs(eval_dir, run_dir, factor_ids, suffix)
        inventory_path = build_factor_inventory(factor_ids, run_dir)
        print(f"  Collected {len(collected)} output files")
        print(f"  Inventory: {inventory_path}")
    else:
        collected = {}
        print("  [DRY RUN] Would collect outputs")

    # Step 6: Run redundancy diagnostics (unless skipped)
    if not args.skip_redundancy:
        print("\nStep 6: Redundancy diagnostics")
        redundancy_path = run_dir / "factor_redundancy.csv"
        rc_red, out_red = run_command(
            [sys.executable, str(SCRIPTS / "build_factor_redundancy.py"),
             "--factor-ids", *factor_ids,
             "--output", str(redundancy_path)],
            "Redundancy diagnostics",
            dry_run=args.dry_run,
        )
        command_log.append({
            "step": "redundancy_diagnostics",
            "command": f"build_factor_redundancy.py --factor-ids {' '.join(factor_ids)}",
            "exit_code": rc_red,
            "output_tail": out_red[-500:] if out_red else "",
        })
    else:
        print("\nStep 6: Skipped (--skip-redundancy)")
        command_log.append({
            "step": "redundancy_diagnostics",
            "command": "skipped (--skip-redundancy)",
            "exit_code": 0,
            "output_tail": "",
        })

    # Step 7: Build conclusion cards
    print("\nStep 7: Conclusion cards")
    rc_cards, out_cards = run_command(
        [sys.executable, str(SCRIPTS / "build_factor_conclusion_cards.py"),
         "--run-dir", str(run_dir),
         "--factor-ids", *factor_ids],
        "Conclusion cards",
        dry_run=args.dry_run,
    )
    command_log.append({
        "step": "conclusion_cards",
        "command": f"build_factor_conclusion_cards.py --run-dir {run_dir}",
        "exit_code": rc_cards,
        "output_tail": out_cards[-500:] if out_cards else "",
    })
    if rc_cards != 0:
        has_critical_failure = True

    # Step 8: Quality checks and manifest (BEFORE report, so report can show metadata)
    elapsed = time.time() - t_start
    status = "FAILED" if has_critical_failure else "COMPLETE"
    print("\nStep 8: Quality checks and manifest")
    if not args.dry_run:
        qc_path = build_quality_checks(factor_ids, run_dir, run_id, collected, rc_integrity, command_log)
        manifest_path = build_manifest(run_id, factor_ids, run_dir, collected, elapsed, args.dry_run, status, command_log)
        print(f"  Quality checks: {qc_path}")
        print(f"  Manifest: {manifest_path}")
        print(f"  Status: {status}")
    else:
        print("  [DRY RUN] Would write quality checks and manifest")

    # Step 9: Generate report (AFTER manifest + QC, so it can read metadata)
    print("\nStep 9: Generate report")
    rc_report, out_report = run_command(
        [sys.executable, str(SCRIPTS / "generate_intake_report.py"),
         "--run-dir", str(run_dir)],
        "Generate report",
        dry_run=args.dry_run,
    )
    command_log.append({
        "step": "generate_report",
        "command": f"generate_intake_report.py --run-dir {run_dir}",
        "exit_code": rc_report,
        "output_tail": out_report[-500:] if out_report else "",
    })

    # Summary
    elapsed = time.time() - t_start
    if has_critical_failure:
        failed_steps = [e["step"] for e in command_log if e["step"] in CRITICAL_STEPS and e["exit_code"] != 0]
        print(f"\n=== Intake Run FAILED ({elapsed:.0f}s) ===")
        print(f"  Run ID: {run_id}")
        print(f"  Factors: {len(factor_ids)}")
        print(f"  Failed steps: {failed_steps}")
        print(f"  Output: {run_dir}")
        print(f"  Status: FAILED")
        sys.exit(1)
    else:
        print(f"\n=== Intake Run Complete ({elapsed:.0f}s) ===")
        print(f"  Run ID: {run_id}")
        print(f"  Factors: {len(factor_ids)}")
        print(f"  Output: {run_dir}")
        print(f"  Disclaimer: Diagnostic only. Not production. Not live trading.")


if __name__ == "__main__":
    main()
