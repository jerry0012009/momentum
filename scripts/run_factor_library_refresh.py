#!/usr/bin/env python3
"""Factor Library Refresh Orchestrator — PM-20.

Lightweight orchestration script that runs the factor library pipeline
in the correct dependency order, with dry-run support and expensive-step
guardrails.

Usage:
    python scripts/run_factor_library_refresh.py --dry-run
    python scripts/run_factor_library_refresh.py --stage page
    python scripts/run_factor_library_refresh.py --stage scorecard
    python scripts/run_factor_library_refresh.py --stage metadata
    python scripts/run_factor_library_refresh.py --stage diagnostics
    python scripts/run_factor_library_refresh.py --stage redundancy --expensive-ok
    python scripts/run_factor_library_refresh.py --stage all --expensive-ok

Stages (in pipeline order):
    registry-integrity   Check factor registry integrity (cheap)
    catalog              Build factor catalog + integrity check (cheap)
    values               Compute factor values (cheap if already computed)
    direction-audit      Audit factor direction semantics (cheap)
    evaluate             Factor-level RankIC evaluation (EXPENSIVE)
    diagnostics          Build diagnostics metrics (cheap)
    metadata             Build bilingual factor cards (cheap)
    scorecard            Build quality scorecard (cheap)
    redundancy           Pairwise redundancy matrix (EXPENSIVE)
    cluster              Redundancy cluster + marginal information diagnostics (PM-31) (cheap)
    paper-diagnostics    Single-factor paper portfolio diagnostics (EXPENSIVE)
    paper-page-payload   Build single-factor paper page payload (cheap)
    regime               BTC market regime diagnostics (PM-23) (cheap)
    shape-stability      Quantile shape + rolling stability diagnostics (cheap)
    decile-shape         Decile shape diagnostics (cheap)
    capacity-liquidity   Capacity & liquidity diagnostics (cheap)
    profile              Unified factor evaluation workflow profile (PM-32) (cheap)
    staleness            Check factor library staleness (cheap)
    page                 Rebuild factor-evaluation.html (cheap)
    state                Regenerate factor_library_state.json/md (cheap)

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

# ── Stage definitions ──────────────────────────────────────────────────────
# Each stage: (name, description, expensive, commands)
# commands is a list of (label, cmd_list) tuples.

STAGES: list[dict] = [
    {
        "name": "registry-integrity",
        "description": "Check factor registry integrity",
        "expensive": False,
        "commands": [
            ("check_factor_registry_integrity", ["python", str(SCRIPTS / "check_factor_registry_integrity.py")]),
        ],
    },
    {
        "name": "catalog",
        "description": "Build factor catalog + integrity check",
        "expensive": False,
        "commands": [
            ("build_factor_catalog", ["python", str(SCRIPTS / "build_factor_catalog.py")]),
            ("check_factor_catalog_integrity", ["python", str(SCRIPTS / "check_factor_catalog_integrity.py")]),
        ],
    },
    {
        "name": "values",
        "description": "Compute factor values from registry",
        "expensive": False,
        "commands": [
            ("build_factor_values", ["python", str(SCRIPTS / "build_factor_values.py")]),
        ],
    },
    {
        "name": "direction-audit",
        "description": "Audit factor direction semantics",
        "expensive": False,
        "commands": [
            ("audit_factor_direction_semantics", ["python", str(SCRIPTS / "audit_factor_direction_semantics.py")]),
        ],
    },
    {
        "name": "evaluate",
        "description": "Factor-level RankIC evaluation (EXPENSIVE)",
        "expensive": True,
        "commands": [
            ("evaluate_factors", ["python", str(SCRIPTS / "evaluate_factors.py")]),
        ],
    },
    {
        "name": "diagnostics",
        "description": "Build diagnostics metrics from evaluation outputs",
        "expensive": False,
        "commands": [
            ("build_factor_diagnostics_metrics", [
                "python", str(SCRIPTS / "build_factor_diagnostics_metrics.py"),
                "--input-dir", str(ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_level_evaluation"),
                "--state-path", str(ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"),
                "--output-dir", str(ROOT / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"),
            ]),
        ],
    },
    {
        "name": "metadata",
        "description": "Build bilingual factor cards",
        "expensive": False,
        "commands": [
            ("build_factor_bilingual_cards", ["python", str(SCRIPTS / "build_factor_bilingual_cards.py")]),
        ],
    },
    {
        "name": "scorecard",
        "description": "Build quality scorecard",
        "expensive": False,
        "commands": [
            ("build_factor_quality_scorecard", ["python", str(SCRIPTS / "build_factor_quality_scorecard.py")]),
        ],
    },
    {
        "name": "redundancy",
        "description": "Full pairwise redundancy matrix (EXPENSIVE)",
        "expensive": True,
        "commands": [
            ("build_factor_pairwise_redundancy_matrix", [
                "python", str(SCRIPTS / "build_factor_pairwise_redundancy_matrix.py"),
            ]),
        ],
    },
    {
        "name": "cluster",
        "description": "Redundancy cluster and marginal information diagnostics (PM-31)",
        "expensive": False,
        "commands": [
            ("build_factor_redundancy_cluster_diagnostics", [
                "python", str(SCRIPTS / "build_factor_redundancy_cluster_diagnostics.py"),
            ]),
        ],
    },
    {
        "name": "paper-diagnostics",
        "description": "Single-factor paper portfolio diagnostics (EXPENSIVE)",
        "expensive": True,
        "commands": [
            ("build_single_factor_paper_portfolio_diagnostics", [
                "python", str(SCRIPTS / "build_single_factor_paper_portfolio_diagnostics.py"),
            ]),
        ],
    },
    {
        "name": "paper-page-payload",
        "description": "Build single-factor paper page payload",
        "expensive": False,
        "commands": [
            ("build_single_factor_paper_page_payload", [
                "python", str(SCRIPTS / "build_single_factor_paper_page_payload.py"),
            ]),
        ],
    },
    {
        "name": "regime",
        "description": "BTC market regime diagnostics (PM-23)",
        "expensive": False,
        "commands": [
            ("build_factor_market_regime_diagnostics", [
                "python", str(SCRIPTS / "build_factor_market_regime_diagnostics.py"),
                "--btc-symbol", "auto",
                "--fee-bps", "10",
            ]),
        ],
    },
    {
        "name": "shape-stability",
        "description": "Quantile shape + rolling stability diagnostics",
        "expensive": False,
        "commands": [
            ("build_factor_shape_stability_diagnostics", [
                "python", str(SCRIPTS / "build_factor_shape_stability_diagnostics.py"),
            ]),
        ],
    },
    {
        "name": "decile-shape",
        "description": "Decile shape diagnostics",
        "expensive": False,
        "commands": [
            ("build_factor_decile_shape_diagnostics", [
                "python", str(SCRIPTS / "build_factor_decile_shape_diagnostics.py"),
            ]),
        ],
    },
    {
        "name": "capacity-liquidity",
        "description": "Capacity & liquidity diagnostics",
        "expensive": False,
        "commands": [
            ("build_factor_capacity_liquidity_diagnostics", [
                "python", str(SCRIPTS / "build_factor_capacity_liquidity_diagnostics.py"),
            ]),
        ],
    },
    {
        "name": "profile",
        "description": "Unified factor evaluation workflow profile (PM-32)",
        "expensive": False,
        "commands": [
            ("build_unified_factor_profile", [
                "python", str(SCRIPTS / "build_unified_factor_profile.py"),
            ]),
        ],
    },
    {
        "name": "staleness",
        "description": "Check factor library staleness",
        "expensive": False,
        "commands": [
            ("check_factor_library_staleness", [
                "python", str(SCRIPTS / "check_factor_library_staleness.py"),
            ]),
        ],
    },
    {
        "name": "page",
        "description": "Rebuild factor-evaluation.html",
        "expensive": False,
        "commands": [
            ("build_factor_eval_html", ["python", str(SCRIPTS / "_build_factor_eval_html.py")]),
        ],
    },
    {
        "name": "state",
        "description": "Regenerate factor_library_state.json/md",
        "expensive": False,
        "commands": [
            ("build_factor_library_state", ["python", str(SCRIPTS / "build_factor_library_state.py")]),
        ],
    },
]

STAGE_NAMES = [s["name"] for s in STAGES]
STAGE_MAP = {s["name"]: s for s in STAGES}

# Multi-stage presets
PRESETS = {
    "all": STAGE_NAMES,
    "cheap": [s["name"] for s in STAGES if not s["expensive"]],
    "page-only": ["page"],
    "scorecard-only": ["scorecard"],
    "metadata-only": ["metadata"],
    "diagnostics-only": ["diagnostics"],
    "redundancy-only": ["redundancy"],
}


def resolve_stages(stage_arg: str) -> list[str]:
    """Resolve --stage argument to a list of stage names."""
    if stage_arg in PRESETS:
        return PRESETS[stage_arg]
    if stage_arg in STAGE_MAP:
        return [stage_arg]
    print(f"ERROR: Unknown stage or preset: {stage_arg!r}")
    print(f"Available stages: {', '.join(STAGE_NAMES)}")
    print(f"Available presets: {', '.join(sorted(PRESETS.keys()))}")
    sys.exit(1)


def check_expensive(stages: list[str], expensive_ok: bool) -> None:
    """Fail if any requested stage is expensive and --expensive-ok not set."""
    expensive_requested = [s for s in stages if STAGE_MAP[s]["expensive"]]
    if expensive_requested and not expensive_ok:
        print("ERROR: The following stages are expensive and require --expensive-ok:")
        for s in expensive_requested:
            print(f"  - {s}: {STAGE_MAP[s]['description']}")
        print("\nRe-run with --expensive-ok to proceed.")
        sys.exit(1)


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
        description="Factor Library Refresh Orchestrator — PM-20",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--stage",
        type=str,
        default=None,
        help=f"Stage to run (one of: {', '.join(STAGE_NAMES)}) or preset ({', '.join(sorted(PRESETS.keys()))}). "
             "If omitted, prints available stages and exits.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    parser.add_argument(
        "--expensive-ok",
        action="store_true",
        help="Allow expensive stages (evaluate, redundancy) to run.",
    )
    args = parser.parse_args()

    if args.stage is None:
        print("Factor Library Refresh Orchestrator — PM-20")
        print("=" * 50)
        print("\nAvailable stages:")
        for s in STAGES:
            marker = " [EXPENSIVE]" if s["expensive"] else ""
            print(f"  {s['name']:24s} {s['description']}{marker}")
        print("\nAvailable presets:")
        for name, members in sorted(PRESETS.items()):
            print(f"  {name:24s} → {', '.join(members)}")
        print(f"\nUsage: python {Path(__file__).name} --stage <stage|preset> [--dry-run] [--expensive-ok]")
        return 0

    stages = resolve_stages(args.stage)
    check_expensive(stages, args.expensive_ok)

    if args.dry_run:
        print("DRY RUN — commands will be printed but not executed.\n")

    print(f"Stages to run: {' → '.join(stages)}")
    print(f"Expensive OK: {args.expensive_ok}")

    total_start = time.time()
    for stage_name in stages:
        stage = STAGE_MAP[stage_name]
        print(f"\n{'#'*60}")
        print(f"# Stage: {stage_name} — {stage['description']}")
        print(f"{'#'*60}")

        for label, cmd in stage["commands"]:
            rc = run_command(label, cmd, args.dry_run)
            if rc != 0:
                print(f"\nABORTED: stage '{stage_name}' failed at '{label}'.")
                print(f"Fix the error and re-run from this stage.")
                return rc

    elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"All {len(stages)} stage(s) completed successfully ({elapsed:.1f}s)")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
