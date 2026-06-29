#!/usr/bin/env python3
"""Post-Intake Workflow Completion Runner — PM-46 (batch02 workflow gap repair).

Runs the post-intake workflow completion pipeline for specific factors,
ensuring all downstream diagnostics are computed without triggering a full
expensive refresh.

Usage:
    python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h,mom_vol_adjusted_20h
    python scripts/run_post_intake_workflow_completion.py --factor-ids rev_2h --skip-expensive
    python scripts/run_post_intake_workflow_completion.py --only-missing

Stages (in pipeline order):
    1.  factor-level evaluation (EXPENSIVE) — temp output + auto-merge
    2.  paper portfolio diagnostics (EXPENSIVE) — temp output + auto-merge
    3.  paper page payload
    4.  state refresh
    5.  diagnostics metrics (cumulative LS curve, etc.)
    6.  pairwise redundancy (EXPENSIVE)
    7.  redundancy cluster + marginal information
    8.  regime/BTC diagnostics (with canonical IC merge)
    9.  shape + stability diagnostics (quantile shape, rolling stability)
    10. decile shape diagnostics
    11. capacity/liquidity diagnostics
    12. scorecard refresh
    13. robust significance refresh
    14. unified profile refresh
    15. page build
    16. page completeness QA
    17. post-intake workflow integrity QA

NOT production. NOT live trading. Research diagnostics only.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
DIAG_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
EVAL_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"
STATE_PATH = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
META_DIR = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_metadata"
TMP_EVAL = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "_tmp_evaluate"
TMP_PAPER = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "_tmp_paper"

# ── Merge helpers ────────────────────────────────────────────────────────

def _merge_csv(tmp_path: Path, canon_path: Path, key_col: str = "factor_name") -> int:
    """Merge rows for new factors from tmp CSV into canonical CSV.
    Returns number of rows added."""
    import pandas as pd
    if not tmp_path.exists():
        return 0
    df_tmp = pd.read_csv(tmp_path)
    if df_tmp.empty:
        return 0
    # Determine key column
    if key_col not in df_tmp.columns:
        alt = "factor_id" if "factor_id" in df_tmp.columns else None
        if alt:
            key_col = alt
        else:
            return 0
    new_ids = set(df_tmp[key_col].unique())
    if canon_path.exists():
        df_canon = pd.read_csv(canon_path)
        if key_col in df_canon.columns:
            existing_ids = set(df_canon[key_col].unique())
            overlap = new_ids & existing_ids
            if overlap:
                # Remove existing rows for these factors before merge
                df_canon = df_canon[~df_canon[key_col].isin(overlap)]
            df_merged = pd.concat([df_canon, df_tmp], ignore_index=True)
        else:
            df_merged = df_tmp
    else:
        df_merged = df_tmp
    df_merged.to_csv(canon_path, index=False)
    added = len(new_ids)
    return added


def _merge_evaluate_outputs(suffix: str) -> int:
    """Merge evaluation batch outputs into canonical CSVs."""
    import pandas as pd
    tmp = EVAL_DIR
    files = [
        ("factor_level_rankic_summary", "factor_name"),
        ("factor_level_coverage_summary", "factor_name"),
        ("factor_level_metric_panel", "factor_name"),
        ("factor_level_period_ic_summary", "factor_name"),
        ("factor_level_quantile_return_summary", "factor_name"),
        ("factor_level_long_short_summary", "factor_name"),
        ("factor_level_period_quantile_return_summary", "factor_name"),
        ("factor_level_period_long_short_summary", "factor_name"),
        ("factor_level_formula_catalog", "factor_id"),
    ]
    total = 0
    for base, key in files:
        src = tmp / f"{base}_{suffix}.csv"
        dst = tmp / f"{base}.csv"
        n = _merge_csv(src, dst, key)
        if n > 0:
            print(f"    merged {base}: +{n} factors")
        total += n
        # Clean up temp file
        if src.exists():
            src.unlink()
    # Clean up manifest
    manifest = tmp / f"factor_level_evaluation_manifest_{suffix}.json"
    if manifest.exists():
        manifest.unlink()
    # Clean up json variants
    for base in ["factor_level_rankic_summary", "factor_level_metric_panel"]:
        src_json = tmp / f"{base}_{suffix}.json"
        if src_json.exists():
            src_json.unlink()
    return total


def _merge_paper_outputs() -> int:
    """Merge paper diagnostics temp outputs into canonical files."""
    import pandas as pd
    files = [
        ("single_factor_paper_summary.csv", "factor_id"),
        ("single_factor_paper_monthly_returns.csv", "factor_id"),
        ("single_factor_fee_sensitivity.csv", "factor_id"),
        ("single_factor_paper_turnover.csv", "factor_id"),
        ("single_factor_paper_leg_decomposition.csv", "factor_id"),
        ("single_factor_paper_drawdown_curve.csv", "factor_id"),
    ]
    total = 0
    for fname, key in files:
        src = TMP_PAPER / fname
        dst = DIAG_DIR / fname
        n = _merge_csv(src, dst, key)
        if n > 0:
            print(f"    merged {fname}: +{n} factors")
        total += n
    # Clean up temp dir
    if TMP_PAPER.exists():
        shutil.rmtree(TMP_PAPER)
    return total


# ── Stage definitions ──────────────────────────────────────────────────────

STAGES = [
    {
        "name": "evaluate",
        "description": "Factor-level RankIC evaluation (EXPENSIVE, temp output + merge)",
        "expensive": True,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "evaluate_factors.py"),
            "--factor-ids", ",".join(fids),
            "--output-suffix", "batch",
        ],
        "post_action": lambda fids: _merge_evaluate_outputs("batch"),
    },
    {
        "name": "paper-diagnostics",
        "description": "Single-factor paper portfolio diagnostics (EXPENSIVE, temp output + merge)",
        "expensive": True,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_single_factor_paper_portfolio_diagnostics.py"),
            "--factor-ids", ",".join(fids),
            "--output-dir", str(TMP_PAPER),
        ],
        "post_action": lambda fids: _merge_paper_outputs(),
    },
    {
        "name": "paper-page-payload",
        "description": "Build single-factor paper page payload",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_single_factor_paper_page_payload.py"),
        ],
    },
    {
        "name": "state",
        "description": "Refresh factor library state before state-dependent diagnostics",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_library_state.py"),
        ],
    },
    {
        "name": "diagnostics-metrics",
        "description": "Build diagnostics metrics (cumulative LS curve, etc.)",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_diagnostics_metrics.py"),
            "--input-dir", str(EVAL_DIR),
            "--state-path", str(STATE_PATH),
            "--output-dir", str(DIAG_DIR),
        ],
    },
    {
        "name": "redundancy",
        "description": "Pairwise redundancy matrix (EXPENSIVE)",
        "expensive": True,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_pairwise_redundancy_matrix.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "cluster",
        "description": "Redundancy cluster + marginal information",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_redundancy_cluster_diagnostics.py"),
        ],
    },
    {
        "name": "regime",
        "description": "BTC market regime diagnostics (with canonical IC merge)",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_market_regime_diagnostics.py"),
            "--btc-symbol", "auto",
            "--fee-bps", "10",
            "--canonical-ic-path", str(EVAL_DIR / "factor_level_period_ic_summary.csv"),
        ],
    },
    {
        "name": "shape-stability",
        "description": "Quantile shape + rolling stability diagnostics",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_shape_stability_diagnostics.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "decile",
        "description": "Direction-aware decile shape diagnostics",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_decile_shape_diagnostics.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "capacity",
        "description": "Capacity/liquidity proxy diagnostics",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_capacity_liquidity_diagnostics.py"),
            "--factor-ids", ",".join(fids),
        ],
    },
    {
        "name": "scorecard",
        "description": "Quality scorecard refresh (with canonical fallback)",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_factor_quality_scorecard.py"),
        ],
    },
    {
        "name": "rankic-robust-significance",
        "description": "PM-54: RankIC robust significance (Newey-West + bootstrap)",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "compute_rankic_robust_significance.py"),
        ],
    },
    {
        "name": "return-robust-significance",
        "description": "PM-56: Return-side robust significance (LS + paper + fee)",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "compute_return_robust_significance.py"),
        ],
    },
    {
        "name": "profile",
        "description": "Unified factor profile refresh",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "build_unified_factor_profile.py"),
        ],
    },
    {
        "name": "page",
        "description": "Rebuild factor-evaluation.html",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "_build_factor_eval_html.py"),
        ],
    },
    {
        "name": "page-qa",
        "description": "Page completeness QA",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "check_factor_evaluation_page_completeness.py"),
        ],
    },
    {
        "name": "integrity-qa",
        "description": "Post-intake workflow integrity QA",
        "expensive": False,
        "build_cmd": lambda fids: [
            sys.executable, str(SCRIPTS / "check_post_intake_workflow_integrity.py"),
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
    venv_bin = str(ROOT / ".venv" / "bin")
    env = {**os.environ, "VIRTUAL_ENV": str(ROOT / ".venv"),
           "PATH": venv_bin + ":" + os.environ.get("PATH", "")}
    # Use momentum venv python, not the one that launched this script
    venv_python = str(ROOT / ".venv" / "bin" / "python")
    cmd[0] = venv_python
    result = subprocess.run(cmd, cwd=str(ROOT), env=env)
    elapsed = time.time() - t0

    if result.returncode != 0:
        print(f"\nFAILED: {label} (exit code {result.returncode}, {elapsed:.1f}s)")
    else:
        print(f"\nOK: {label} ({elapsed:.1f}s)")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Post-Intake Workflow Completion Runner — PM-46",
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
        fids = detect_missing_factors()
        if not fids:
            print("All factors have complete workflow. Nothing to do.")
            return 0
        print(f"Auto-detected {len(fids)} factors with incomplete workflow: {fids}")
    else:
        print("ERROR: Must specify --factor-ids or --only-missing")
        return 1

    try:
        raise_for_skipped_public_factor_ids(fids, action="post-intake processed")
    except ValueError as exc:
        print(f"ERROR: {exc}")
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

        # Run post-action (merge) if defined
        post_action = stage.get("post_action")
        if post_action and not args.dry_run:
            print(f"  [merge] Running post-action for {stage_name}...")
            post_action(fids)

    elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"All {len(stages)} stage(s) completed successfully ({elapsed:.1f}s)")
    print(f"{'='*60}")
    return 0


def detect_missing_factors() -> list[str]:
    """Detect factors with incomplete post-intake workflow — PM-53B.

    Checks each active factor against ALL required downstream outputs:
      - rankic, long_short, diagnostics_summary, shape, rolling_stability,
        decile, capacity, scorecard, profile, bilingual card, page payload.

    A factor is "missing" if it is absent from ANY required output.
    Unavailable-but-accepted optional fields are NOT treated as failure.
    Blocked factors in the active list trigger a hard failure.
    """
    import csv as _csv
    import re as _re

    import pandas as pd

    if not STATE_PATH.exists():
        return []
    state = json.loads(STATE_PATH.read_text())
    all_fids = state.get("registered_factor_ids", [])
    if not all_fids:
        return []

    active_set = set(all_fids)
    missing_set = set(all_fids)  # start with all, remove as we find them

    # Required CSV checks: (path, key_column)
    required_csvs = [
        (EVAL_DIR / "factor_level_rankic_summary.csv", "factor_name"),
        (EVAL_DIR / "factor_level_long_short_summary.csv", "factor_name"),
        (DIAG_DIR / "factor_diagnostics_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_quantile_shape_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_rolling_stability_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_decile_shape_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_capacity_liquidity_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_quality_scorecard.csv", "factor_id"),
        (DIAG_DIR / "factor_unified_profile_summary.csv", "factor_id"),
        (META_DIR / "factor_bilingual_cards.csv", "factor_id"),
        # PM-54/56: Robust diagnostics (full-universe required)
        (DIAG_DIR / "factor_rankic_robust_significance_summary.csv", "factor_id"),
        (DIAG_DIR / "factor_ls_robust_significance_summary.csv", "factor_id"),
        # Paper diagnostics: workflow-required artifacts (display is optional/deep-dive)
        # 纸面诊断是 workflow required evidence，但页面展示属于 optional deep-dive
        (DIAG_DIR / "single_factor_paper_summary.csv", "factor_id"),
        (DIAG_DIR / "single_factor_fee_sensitivity.csv", "factor_id"),
    ]

    # Accumulate per-factor: which tables it's missing from
    factor_missing_tables: dict[str, list[str]] = {fid: [] for fid in all_fids}

    for path, key_col in required_csvs:
        if not path.exists():
            # All factors missing from this table
            for fid in all_fids:
                factor_missing_tables[fid].append(path.stem)
            continue
        try:
            ids_in_file = set()
            with open(path, newline="", encoding="utf-8") as f:
                reader = _csv.DictReader(f)
                actual_key = key_col
                if actual_key not in (reader.fieldnames or []):
                    actual_key = "factor_id" if "factor_id" in (reader.fieldnames or []) else "factor_name"
                for row in reader:
                    val = row.get(actual_key, "").strip()
                    if val:
                        ids_in_file.add(val)
            for fid in all_fids:
                if fid not in ids_in_file:
                    factor_missing_tables[fid].append(path.stem)
        except Exception:
            for fid in all_fids:
                factor_missing_tables[fid].append(path.stem)

    # Check page payload
    html_path = ROOT / "reports" / "site" / "factor-library" / "factor-evaluation.html"
    if html_path.exists():
        try:
            text = html_path.read_text(encoding="utf-8", errors="replace")
            m = _re.search(
                r'<script id="factorPayload" type="application/json">(.*?)</script>',
                text, _re.DOTALL,
            )
            if m:
                data = json.loads(m.group(1))
                page_fids = {f.get("factor_id", "") for f in data.get("factors", []) if f.get("factor_id")}
                for fid in all_fids:
                    if fid not in page_fids:
                        factor_missing_tables[fid].append("html_payload")
            else:
                for fid in all_fids:
                    factor_missing_tables[fid].append("html_payload")
        except Exception:
            for fid in all_fids:
                factor_missing_tables[fid].append("html_payload")
    else:
        for fid in all_fids:
            factor_missing_tables[fid].append("html_payload")

    # Check paper page payload
    paper_payload_path = DIAG_DIR / "single_factor_paper_page_payload.json"
    if paper_payload_path.exists():
        try:
            payload = json.loads(paper_payload_path.read_text())
            factors = payload.get("factors", [])
            if isinstance(factors, list):
                fids_in_payload = {f["factor_id"] for f in factors if "factor_id" in f}
            elif isinstance(factors, dict):
                fids_in_payload = set(factors.keys())
            else:
                fids_in_payload = set()
            for fid in all_fids:
                if fid not in fids_in_payload:
                    factor_missing_tables[fid].append("single_factor_paper_page_payload")
        except Exception:
            for fid in all_fids:
                factor_missing_tables[fid].append("single_factor_paper_page_payload")
    else:
        for fid in all_fids:
            factor_missing_tables[fid].append("single_factor_paper_page_payload")

    # Collect factors with any missing table
    missing = sorted(fid for fid in all_fids if factor_missing_tables[fid])

    if missing:
        print(f"\n  Missing-factor details ({len(missing)} factors):")
        for fid in missing[:20]:
            tables = factor_missing_tables[fid]
            print(f"    {fid}: missing from {', '.join(tables)}")
        if len(missing) > 20:
            print(f"    ... and {len(missing) - 20} more")

    return missing


if __name__ == "__main__":
    sys.exit(main())
