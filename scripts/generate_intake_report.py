#!/usr/bin/env python3
"""Generate readable intake report from a factor intake run.

Usage:
    python scripts/generate_intake_report.py --run-dir <path>

Phase 13A-P3. Not production. Not live trading.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_json(path: Path) -> dict | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def generate_report(run_dir: Path) -> str:
    """Generate a markdown report from an intake run directory."""
    lines = []

    # Load all inputs
    manifest = load_json(run_dir / "manifest.json")
    inventory_df = load_csv(run_dir / "factor_inventory.csv")
    review_df = load_csv(run_dir / "factor_candidate_review.csv")
    metric_df = load_csv(run_dir / "factor_metric_panel.csv")
    redundancy_df = load_csv(run_dir / "factor_redundancy.csv")
    cards_df = load_csv(run_dir / "factor_conclusion_cards.csv")
    quality_df = load_csv(run_dir / "quality_checks.csv")

    # Header
    run_id = manifest.get("run_id", "unknown") if manifest else "unknown"
    generated_at = manifest.get("generated_at", "") if manifest else ""
    factor_ids = manifest.get("factor_ids", []) if manifest else []

    run_status = manifest.get("status", "unknown") if manifest else "unknown"
    status_icon = "✅" if run_status == "COMPLETE" else "❌" if run_status == "FAILED" else "❓"

    lines.append(f"# Factor Intake Report: {run_id}")
    lines.append("")
    lines.append(f"**Run status:** {status_icon} {run_status}")
    lines.append(f"**Generated:** {generated_at}")
    lines.append(f"**Factors evaluated:** {len(factor_ids)}")
    lines.append(f"**Factor IDs:** {', '.join(factor_ids)}")

    # Show failed steps for FAILED runs
    if run_status == "FAILED" and manifest:
        cmd_log = manifest.get("command_log", [])
        failed = [e for e in cmd_log if e.get("exit_code", 0) not in (0, -1)]
        if failed:
            lines.append("")
            lines.append("**Failed steps:**")
            for e in failed:
                lines.append(f"- ❌ {e['step']}: exit_code={e['exit_code']}")
                tail = e.get("output_tail", "").strip()
                if tail:
                    # Show last 200 chars of error
                    lines.append(f"  ```")
                    lines.append(f"  {tail[-200:]}")
                    lines.append(f"  ```")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Factor Inventory
    if not inventory_df.empty:
        lines.append("## Factor Inventory")
        lines.append("")
        lines.append("| factor_id | family | direction | lookback | fv_exists |")
        lines.append("|-----------|--------|-----------|----------|-----------|")
        for _, row in inventory_df.iterrows():
            lines.append(f"| {row['factor_id']} | {row['family']} | {row['expected_direction']} | {row.get('lookback_window', '')} | {row.get('fv_exists', '')} |")
        lines.append("")

    # Quality Checks
    if not quality_df.empty:
        lines.append("## Quality Checks")
        lines.append("")
        pass_count = (quality_df["status"] == "PASS").sum()
        fail_count = (quality_df["status"] == "FAIL").sum()
        lines.append(f"**Result: {pass_count} PASS, {fail_count} FAIL**")
        lines.append("")
        for _, row in quality_df.iterrows():
            icon = "✅" if row["status"] == "PASS" else "❌"
            lines.append(f"- {icon} {row['check_name']}: {row['status']}")
        lines.append("")

    # Key Metrics Table
    if not review_df.empty:
        lines.append("## Key Metrics")
        lines.append("")
        lines.append("| factor_id | best_adj_ic | horizon | best_icir | best_ls_spread | ls_t | consistency | review_bucket |")
        lines.append("|-----------|-------------|---------|-----------|----------------|------|-------------|---------------|")
        for _, row in review_df.iterrows():
            adj_ic = row.get("best_adj_ic")
            adj_ic_str = f"{float(adj_ic):+.6f}" if pd.notna(adj_ic) else "—"
            hz = row.get("best_adj_ic_horizon", "—")
            icir = row.get("best_direction_adjusted_icir")
            icir_str = f"{float(icir):+.4f}" if pd.notna(icir) else "—"
            ls = row.get("best_long_short_spread")
            ls_str = f"{float(ls):+.6f}" if pd.notna(ls) else "—"
            ls_t = row.get("best_long_short_t_stat")
            ls_t_str = f"{float(ls_t):.2f}" if pd.notna(ls_t) else "—"
            consistency = row.get("rankic_longshort_consistency", "—")
            bucket = row.get("review_bucket", "—")
            lines.append(f"| {row['factor_name']} | {adj_ic_str} | {hz} | {icir_str} | {ls_str} | {ls_t_str} | {consistency} | {bucket} |")
        lines.append("")

    # Conclusion Cards
    if not cards_df.empty:
        lines.append("## Conclusion Cards")
        lines.append("")
        for _, card in cards_df.iterrows():
            fid = card["factor_id"]
            lines.append(f"### {fid}")
            lines.append("")
            lines.append(f"- **Family:** {card.get('family', '—')}")
            lines.append(f"- **Expected direction:** {card.get('expected_direction', '—')}")
            lines.append(f"- **Best horizon:** {card.get('best_horizon', '—')}")
            adj_ic = card.get("best_adj_ic")
            if pd.notna(adj_ic):
                lines.append(f"- **Best adj IC:** {float(adj_ic):+.6f}")
            ls_t = card.get("best_long_short_t_stat")
            if pd.notna(ls_t):
                lines.append(f"- **Best LS t-stat:** {float(ls_t):.2f}")
            lines.append(f"- **Monthly stability:** {card.get('monthly_stability_summary', '—')}")
            lines.append(f"- **Quantile monotonicity:** {card.get('quantile_monotonicity_summary', '—')}")
            lines.append(f"- **RankIC-LS consistency:** {card.get('rankic_longshort_consistency', '—')}")
            lines.append(f"- **Redundancy:** {card.get('redundancy_level', '—')}")
            nearest = card.get("nearest_existing_factors", "")
            if nearest:
                lines.append(f"- **Nearest existing:** {nearest}")
            lines.append(f"- **Decision bucket:** {card.get('decision_bucket', '—')}")
            lines.append(f"- **Recommended action:** {card.get('recommended_action', '—')}")
            caveats = card.get("caveats", "")
            if caveats:
                lines.append(f"- **Caveats:** {caveats}")
            lines.append("")

    # Redundancy Warnings
    if not redundancy_df.empty:
        high_red = redundancy_df[redundancy_df["redundancy_level"].isin(["NEAR_DUPLICATE", "HIGH_REDUNDANCY"])]
        if len(high_red) > 0:
            lines.append("## Redundancy Warnings")
            lines.append("")
            for _, row in high_red.iterrows():
                lines.append(f"- **{row['factor_i']} ↔ {row['factor_j']}**: {row['redundancy_level']} (|ρ| = {row['abs_spearman_corr']:.3f})")
            lines.append("")

    # Disclaimer
    lines.append("---")
    lines.append("")
    lines.append("**Disclaimer:** This is a factor intake diagnostic report. It is NOT production. "
                 "It is NOT live trading. It is NOT signal promotion. "
                 "Factors listed here are under research evaluation only.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", required=True,
                        help="Intake run directory")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(f"  ERROR: run directory not found: {run_dir}")
        sys.exit(1)

    print(f"Generating intake report")
    print(f"  Run dir: {run_dir}")

    report = generate_report(run_dir)
    report_path = run_dir / "report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"  Output: {report_path}")
    print(f"  Length: {len(report)} chars, {report.count(chr(10))} lines")


if __name__ == "__main__":
    main()
