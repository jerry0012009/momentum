#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.report_pipeline import ReportPipelineConfig, run_pipeline


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run momentum report pipeline with stage control.")
    p.add_argument(
        "--stage",
        choices=["all", "build", "insights", "q1_q3", "q4_q6", "q7_q9", "q10_q14", "publish"],
        default="all",
        help="Pipeline stage to run. all=build+insights+publish; q-groups are decoupled insight units",
    )
    p.add_argument("--python-bin", default=sys.executable, help="Python binary for build stage")
    p.add_argument(
        "--callback-text",
        default=None,
        help="Optional completion callback text via `openclaw system event`",
    )
    p.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    p.add_argument("--use-cache", action="store_true", help="Skip stage when expected outputs already exist")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = ReportPipelineConfig(
        root=ROOT,
        python_bin=args.python_bin,
        callback_text=args.callback_text,
        dry_run=args.dry_run,
        use_cache=args.use_cache,
    )
    return run_pipeline(cfg, stage=args.stage)


if __name__ == "__main__":
    raise SystemExit(main())
