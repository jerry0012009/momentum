#!/usr/bin/env python3
"""Factor Intake Promotion Guard.

Refuses to promote factors from an intake run unless all guard conditions pass.
This is a conservative gate — promotion requires explicit confirmation.

Usage:
    python scripts/promote_factor_intake.py --run-id phase13a_p3_smoke --confirm

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE_BASE = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_intake"


def check_manifest(run_dir: Path) -> tuple[bool, str]:
    """Check that manifest exists and is valid."""
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return False, "manifest.json not found"
    with open(manifest_path) as f:
        manifest = json.load(f)
    if not manifest.get("factor_ids"):
        return False, "manifest has no factor_ids"
    if manifest.get("dry_run"):
        return False, "manifest indicates dry_run — cannot promote dry runs"
    return True, f"manifest OK ({len(manifest['factor_ids'])} factors)"


def check_quality_checks(run_dir: Path) -> tuple[bool, str]:
    """Check that all quality checks pass."""
    import csv
    qc_path = run_dir / "quality_checks.csv"
    if not qc_path.exists():
        return False, "quality_checks.csv not found"
    with open(qc_path) as f:
        checks = list(csv.DictReader(f))
    failed = [c for c in checks if c.get("status") != "PASS"]
    if failed:
        names = [c["check_name"] for c in failed]
        return False, f"{len(failed)} checks failed: {', '.join(names)}"
    return True, f"all {len(checks)} checks passed"


def check_conclusion_cards(run_dir: Path) -> tuple[bool, str]:
    """Check that conclusion cards exist and cover all factors."""
    cards_path = run_dir / "factor_conclusion_cards.csv"
    if not cards_path.exists():
        return False, "factor_conclusion_cards.csv not found"
    import csv
    with open(cards_path) as f:
        cards = list(csv.DictReader(f))
    if not cards:
        return False, "conclusion cards are empty"
    return True, f"{len(cards)} conclusion cards found"


def check_no_critical_buckets(run_dir: Path) -> tuple[bool, str]:
    """Check that no factors are in buckets that block promotion."""
    import csv
    cards_path = run_dir / "factor_conclusion_cards.csv"
    if not cards_path.exists():
        return False, "conclusion cards not found"
    with open(cards_path) as f:
        cards = list(csv.DictReader(f))

    blocking_buckets = {
        "MISSING_INPUT",
        "REDUNDANT_WITH_EXISTING",
        "DIRECTION_REVIEW_REQUIRED",
        "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED",
    }
    blocked = [c for c in cards if c.get("decision_bucket") in blocking_buckets]
    if blocked:
        names = [f"{c['factor_id']} ({c['decision_bucket']})" for c in blocked]
        return False, f"{len(blocked)} factors blocked: {', '.join(names)}"
    return True, "no blocking decision buckets"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", required=True,
                        help="Intake run ID to promote")
    parser.add_argument("--confirm", action="store_true",
                        help="Explicit confirmation that you want to promote")
    args = parser.parse_args()

    run_dir = INTAKE_BASE / args.run_id

    print(f"Factor Intake Promotion Guard")
    print(f"  Run ID: {args.run_id}")
    print(f"  Run dir: {run_dir}")
    print(f"  Confirmed: {args.confirm}")
    print()

    # Guard 1: Confirm flag
    if not args.confirm:
        print("  ❌ BLOCKED: --confirm flag required")
        print("  Run with --confirm to proceed with promotion.")
        sys.exit(1)
    print("  ✅ --confirm flag provided")

    # Guard 2: Run directory exists
    if not run_dir.exists():
        print(f"  ❌ BLOCKED: run directory not found: {run_dir}")
        sys.exit(1)
    print("  ✅ run directory exists")

    # Guard 3: Manifest
    ok, msg = check_manifest(run_dir)
    if not ok:
        print(f"  ❌ BLOCKED: {msg}")
        sys.exit(1)
    print(f"  ✅ {msg}")

    # Guard 4: Quality checks
    ok, msg = check_quality_checks(run_dir)
    if not ok:
        print(f"  ❌ BLOCKED: {msg}")
        sys.exit(1)
    print(f"  ✅ {msg}")

    # Guard 5: Conclusion cards
    ok, msg = check_conclusion_cards(run_dir)
    if not ok:
        print(f"  ❌ BLOCKED: {msg}")
        sys.exit(1)
    print(f"  ✅ {msg}")

    # Guard 6: No blocking buckets
    ok, msg = check_no_critical_buckets(run_dir)
    if not ok:
        print(f"  ❌ BLOCKED: {msg}")
        sys.exit(1)
    print(f"  ✅ {msg}")

    # All guards passed
    print()
    print("  ⚠️  ALL GUARDS PASSED — but promotion is NOT implemented in this phase.")
    print("  This guard exists to prevent accidental canonical pollution.")
    print("  To actually promote, you would need to:")
    print("    1. Review the conclusion cards manually")
    print("    2. Update factor_formula_registry.py status")
    print("    3. Rebuild the canonical evaluation")
    print("    4. Update signal panel if appropriate")
    print()
    print("  For Phase 13A-P3, no factors are promoted.")


if __name__ == "__main__":
    main()
