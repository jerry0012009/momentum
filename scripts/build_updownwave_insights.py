#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.analytics.updownwave_insights import (
    build_q1_q3_insights,
    build_q4_q6_insights,
    build_q7_q9_insights,
    build_q10_q14_insights,
    build_q_insights,
    insights_to_dict,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build Q1~Q14 textual insights from updownwave artifacts.")
    p.add_argument(
        "--artifact-dir",
        default=str(ROOT / "reports" / "artifacts" / "updownwave"),
        help="Artifacts directory",
    )
    p.add_argument(
        "--stage",
        choices=["all", "q1_q3", "q4_q6", "q7_q9", "q10_q14"],
        default="all",
        help="Generate all insights or a decoupled stage group",
    )
    p.add_argument(
        "--out-json",
        default="insights_q1_q14.json",
        help="Output json filename under artifact-dir",
    )
    p.add_argument(
        "--out-md",
        default="insights_q1_q14.md",
        help="Output markdown filename under artifact-dir",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    stage_funcs = {
        "q1_q3": build_q1_q3_insights,
        "q4_q6": build_q4_q6_insights,
        "q7_q9": build_q7_q9_insights,
        "q10_q14": build_q10_q14_insights,
    }

    if args.stage == "all":
        q = build_q_insights(artifact_dir)
    else:
        q = stage_funcs[args.stage](artifact_dir)

    data = insights_to_dict(q)

    if args.stage == "all":
        out_json = artifact_dir / args.out_json
        out_md = artifact_dir / args.out_md
    else:
        out_json = artifact_dir / f"insights_{args.stage}.json"
        out_md = artifact_dir / f"insights_{args.stage}.md"

    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [f"# UpDownWave Insights ({args.stage})", ""]
    for k in sorted(q.keys(), key=lambda x: int(x[1:])):
        v = q[k]
        lines.append(f"## {k}")
        lines.append(f"- 问题：{v.question}")
        lines.append(f"- 结论：{v.conclusion}")
        lines.append(f"- 实盘动作：{v.action}")
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(f"[ok] wrote {out_json}")
    print(f"[ok] wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
