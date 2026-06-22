#!/usr/bin/env python3
"""Post-Intake Workflow Completion Runner — PM-43A.

Runs the post-intake workflow completion pipeline for specific factors,
ensuring all downstream diagnostics are computed without triggering a full
expensive refresh.

Usage:
    python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h,mom_vol_adjusted_20h
    python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h --skip-expensive
    python scripts/run_post_intake_workflow_completion.py --only-missing

Stages (in pipeline order):
    1. factor-level evaluation (EXPENSIVE)
    2. paper portfolio diagnostics (EXPENSIVE)
    3. paper page payload
    4. pairwise redundancy (EXPENSIVE)
    5. redundancy cluster + marginal information
    6. regime/BTC diagnostics (with canonical IC merge)
    7. scorecard refresh
    8. unified profile refresh
    9. page build
    10. page completeness QA
    11. post-intake workflow integrity QA

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"

# ── Stage definitions ──────────────────────────────────────────────────────

STAGES = [
    {
        "name": "evaluate",
        "description": "Factor-level RankIC evaluation (EXPENSIVE)",
        "expensive": True,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "evaluate_factors.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "paper-diagnostics",
        "description": "Single-factor paper portfolio diagnostics (EXPENSIVE)",
        "expensive": True,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_single_factor_paper_portfolio_diagnostics.py"),
        ],
    },
    {
        "name": "paper-page-payload",
        "description": "Build single-factor paper page payload",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_single_factor_paper_page_payload.py"),
        ],
    },
    {
        "name": "redundancy",
        "description": "Pairwise redundancy matrix (EXPENSIVE)",
        "expensive": True,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_factor_pairwise_redundancy_matrix.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "cluster",
        "description": "Redundancy cluster + marginal information",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_factor_redundancy_cluster_diagnostics.py"),
        ],
    },
    {
        "name": "regime",
        "description": "BTC market regime diagnostics (with canonical IC merge)",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_factor_market_regime_diagnostics.py"),
            "--btc-symbol", "auto",
            "--fee-bps", "10",
            "--canonical-ic-path", str(EVAL_DIR / "factor_level_period_ic_summary.csv"),
        ],
    },
    {
        "name": "scorecard",
        "description": "Quality scorecard refresh (with canonical fallback)",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_factor_quality_scorecard.py"),
        ],
    },
    {
        "name": "profile",
        "description": "Unified factor profile refresh",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "build_unified_factor_profile.py"),
        ],
    },
    {
        "name": "page",
        "description": "Rebuild factor-evaluation.html",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "_build_factor_eval_html.py"),
        ],
    },
    {
        "name": "page-qa",
        "description": "Page completeness QA",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "check_factor_evaluation_page_completeness.py"),
        ],
    },
    {
        "name": "integrity-qa",
        "description": "Post-intake workflow integrity QA",
        "expensive": False,
        "build_cmd": lambda fids: [
            "python", str(SCRIPTS / "check_post_intake_workflow_integrity.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
]

STAGE_NAMES = [s["name"] for s in STAGES]
STAGE_MAP = {s["name"]: s for s in STAGES}

SKIP_EXPENSIVE_STAGES = {"evaluate", "paper-diagnostics", "redundancy"}


def run_command(label: str, cmd: list[str], dry_run: bool) -> int:
    """Run a single command. Returns exit code."""
    cmd_display = " ".join(cmd)
    print(f"\n{'='*60}")
    print(f"[{label}] {cmd_display}")
    print(f"{'='*60}")

    if dry_run:
        print("  (dry-run — not executing)")
        return 0

    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(ROOT))
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"\nFAILED: {label} (exit code {result.returncode}, {elapsed:.1f}s)")
    else:
        print(f"\nOK: {label} ({elapsed:.1f}s)")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-Intake Workflow Completion Runner — PM-43A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--factor-ids", type=str, default=None,
        help="Comma-separated factor IDs to process",
    )
    parser.add_argument(
        "--only-missing", action="store_true",
        help="Auto-detect factors with incomplete workflow and process them",
    )
    parser.add_argument(
        "--skip-expensive", action="store_true",
        help="Skip expensive stages (evaluate, paper-diagnostics, redundancy)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands without executing them",
    )
    parser.add_argument(
        "--start-from", type=str, default=None,
        help="Start from a specific stage (skip earlier stages)",
    )
    args = parser.parse_args()

    # Resolve factor IDs
    if args.factor_ids:
        fids = [f.strip() for f in args.factor_ids.split(",") if f.strip()]
    elif args.only_missing:
        # Auto-detect factors with incomplete workflow
        fids = detect_missing_factors()
        if not fids:
            print("All factors have complete workflow. Nothing to do.")
            return 0
        print(f"Auto-detected {len(fids)} factors with incomplete workflow: {fids}")
    else:
        print("ERROR: Must specify --factor-ids or --only-missing")
        return 1

    # Resolve stages
    stages = STAGE_NAMES
    if args.start_from:
        if args.start_from not in STAGE_NAMES:
            print(f"ERROR: Unknown stage: {args.start_from}")
            return 1
        idx = STAGE_NAMES.index(args.start_from)
        stages = STAGE_NAMES[idx:]

    if args.skip_expensive:
        stages = [s for s in stages if s not in SKIP_EXPENSIVE_STAGES]

    print(f"Factors: {fids}")
    print(f"Stages: {' → '.join(stages)}")
    print(f"Skip expensive: {args.skip_expensive}")
    print(f"Dry run: {args.dry_run}")

    total_start = time.time()
    for stage_name in stages:
        stage = STAGE_MAP[stage_name]
        print(f"\n{'#'*60}")
        print(f"# Stage: {stage_name} — {stage['description']}")
        print(f"{'#'*60}")

        cmd = stage["build_cmd"](fids)
        rc = run_command(stage_name, cmd, args.dry_run)
        if rc != 0:
            print(f"\nABORTED: stage '{stage_name}' failed.")
            print(f"Fix the error and re-run with --start-from {stage_name}")
            return rc

    elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"All {len(stages)} stage(s) completed successfully ({elapsed:.1f}s)")
    print(f"{'='*60}")
    return 0


def detect_missing_factors() -> list[str]:
    """Detect factors with incomplete post-intake workflow."""
    import pandas as pd

    # Load factor library state
    state_path = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
    if not state_path.exists():
        return []
    import json
    state = json.loads(state_path.read_text())
    all_fids = state.get("registered_factor_ids", [])

    missing = []
    for fid in all_fids:
        # Check if factor has pairwise redundancy
        try:
            pairwise = pd.read_csv(DIAG_DIR / "factor_pairwise_redundancy.csv")
            has_pairwise = fid in set(pairwise["factor_i"].unique()) | set(pairwise["factor_j"].unique())
        except Exception:
            has_pairwise = False

        if not has_pairwise:
            missing.append(fid)

    return sorted(missing)


if __name__ == "__main__":
    sys.exit(main())
