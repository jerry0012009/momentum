#!/usr/bin/env python3
"""Compare static and dynamic universe factor evaluations.

Reads static evaluation from result_summary markdown table and
dynamic evaluation from per-factor JSON files.

Usage:
    python scripts/compare_static_dynamic_factor_evals.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DYNAMIC_DIR = ROOT / "reports" / "artifacts" / "factor_eval_dynamic" / \
    "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / \
    "crypto_usdt_perp_monthly_volume_top50_current_listed_v1"
STATIC_MD = RUN / "result_summary_crypto_top50_usdt_perp_1h_long_v1.md"
LABELS = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
FACTORS = [
    "mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h",
    "wq101_alpha101", "wq101_alpha12", "wq101_alpha53",
    "q158_high_low_range", "tech_macd", "tech_atr",
]


def parse_static_summary(md_path: Path) -> pd.DataFrame:
    """Parse the static evaluation markdown table."""
    text = md_path.read_text(encoding="utf-8")
    # Find the table rows (lines starting with |)
    lines = [l.strip() for l in text.split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return pd.DataFrame()

    # Parse header
    header = [c.strip() for c in lines[0].split("|")[1:-1]]
    # Skip separator line
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))

    df = pd.DataFrame(rows)
    # Convert numeric columns
    numeric_cols = ["IC_mean", "ICIR", "RankIC_mean", "RankICIR",
                    "raw_spread", "raw_spread_t", "dir_adj_spread", "dir_adj_t",
                    "turnover", "coverage", "n_ts"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_dynamic_evaluations(dynamic_dir: Path) -> pd.DataFrame:
    """Load all dynamic evaluation JSON files into a DataFrame."""
    rows = []
    for fid in FACTORS:
        json_path = dynamic_dir / f"{fid}_dynamic_eval.json"
        if not json_path.exists():
            continue
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for label in LABELS:
            m = data.get("label_metrics", {}).get(label, {})
            rows.append({
                "factor_id": fid,
                "label": label,
                "expected_direction": m.get("expected_direction", "positive"),
                "dynamic_IC_mean": m.get("IC_mean"),
                "dynamic_ICIR": m.get("ICIR"),
                "dynamic_RankIC_mean": m.get("RankIC_mean"),
                "dynamic_RankICIR": m.get("RankICIR"),
                "dynamic_direction_adjusted_spread": m.get("direction_adjusted_spread"),
                "dynamic_direction_adjusted_tstat": m.get("direction_adjusted_tstat"),
                "dynamic_turnover": m.get("turnover"),
                "dynamic_coverage": m.get("coverage"),
                "dynamic_n_symbols_avg": m.get("n_symbols_avg"),
                "dynamic_n_timestamps": m.get("n_timestamps"),
                "dynamic_n_valid_rows": m.get("n_valid_rows"),
            })
    return pd.DataFrame(rows)


def interpret_row(row: pd.Series) -> str:
    """Assign interpretation tag based on static vs dynamic RankIC."""
    exp_dir = row.get("expected_direction", "positive")
    s_ric = row.get("static_RankIC_mean")
    d_ric = row.get("dynamic_RankIC_mean")

    if exp_dir == "conditional":
        return "conditional_direction_factor"

    if pd.isna(s_ric) or pd.isna(d_ric):
        return "insufficient_static_comparison"

    s_abs = abs(s_ric)
    d_abs = abs(d_ric)

    # Sign flip
    if s_ric * d_ric < 0 and s_abs >= 0.01 and d_abs >= 0.01:
        return "sign_flipped_under_dynamic_universe"

    # Both robust
    if s_abs >= 0.02 and d_abs >= 0.02 and (s_ric * d_ric > 0):
        return "robust_diagnostic_candidate"

    # Weakened
    if s_abs >= 0.02 and d_abs < 0.01:
        return "weakened_under_dynamic_universe"

    # Dynamic only
    if s_abs < 0.01 and d_abs >= 0.02:
        return "dynamic_only_candidate"

    # Both near zero
    if s_abs < 0.01 and d_abs < 0.01:
        return "unstable_or_near_zero"

    # Moderate change
    if s_abs >= 0.01 and d_abs >= 0.01 and (s_ric * d_ric > 0):
        return "robust_diagnostic_candidate"

    return "unstable_or_near_zero"


def main():
    # Load static
    if not STATIC_MD.exists():
        print(f"Static summary not found: {STATIC_MD}")
        print("Comparison partially deferred.")
        return

    static_df = parse_static_summary(STATIC_MD)
    print(f"Parsed {len(static_df)} rows from static summary")

    # Rename static columns
    static_df = static_df.rename(columns={
        "factor": "factor_id",
        "RankIC_mean": "static_RankIC_mean",
        "RankICIR": "static_RankICIR",
        "IC_mean": "static_IC_mean",
        "ICIR": "static_ICIR",
        "dir_adj_spread": "static_direction_adjusted_spread",
        "dir_adj_t": "static_direction_adjusted_tstat",
        "turnover": "static_turnover",
        "coverage": "static_coverage",
        "n_ts": "static_n_timestamps",
    })

    # Load dynamic
    dynamic_df = load_dynamic_evaluations(DYNAMIC_DIR)
    print(f"Loaded {len(dynamic_df)} rows from dynamic evaluations")

    # Merge on (factor_id, label)
    merged = static_df.merge(dynamic_df, on=["factor_id", "label"], how="outer")
    print(f"Merged: {len(merged)} rows")

    # Compute deltas
    merged["delta_RankIC"] = merged.apply(
        lambda r: r["dynamic_RankIC_mean"] - r["static_RankIC_mean"]
        if pd.notna(r.get("dynamic_RankIC_mean")) and pd.notna(r.get("static_RankIC_mean"))
        else None, axis=1)
    merged["delta_direction_adjusted_spread"] = merged.apply(
        lambda r: r["dynamic_direction_adjusted_spread"] - r["static_direction_adjusted_spread"]
        if pd.notna(r.get("dynamic_direction_adjusted_spread")) and pd.notna(r.get("static_direction_adjusted_spread"))
        else None, axis=1)

    # Interpretation tags
    merged["interpretation_tag"] = merged.apply(interpret_row, axis=1)

    # Select output columns
    out_cols = [
        "factor_id", "label", "expected_direction",
        "static_RankIC_mean", "dynamic_RankIC_mean", "delta_RankIC",
        "static_RankICIR", "dynamic_RankICIR",
        "static_IC_mean", "dynamic_IC_mean",
        "static_direction_adjusted_spread", "dynamic_direction_adjusted_spread",
        "delta_direction_adjusted_spread",
        "static_turnover", "dynamic_turnover",
        "static_coverage", "dynamic_coverage",
        "static_n_timestamps", "dynamic_n_timestamps",
        "interpretation_tag",
    ]
    for col in out_cols:
        if col not in merged.columns:
            merged[col] = None

    result = merged[out_cols].copy()

    # Write outputs
    csv_path = RUN / "phase6h_static_vs_dynamic_comparison.csv"
    result.to_csv(csv_path, index=False)
    print(f"Wrote: {csv_path}")

    json_path = RUN / "phase6h_static_vs_dynamic_comparison.json"
    json_path.write_text(json.dumps(result.to_dict(orient="records"), indent=2, default=str) + "\n", encoding="utf-8")
    print(f"Wrote: {json_path}")

    # Print summary
    print("\n=== Interpretation Tag Summary ===")
    for tag, count in result["interpretation_tag"].value_counts().items():
        print(f"  {tag}: {count}")

    print("\n=== ret_fwd_1h Comparison ===")
    r1h = result[result["label"] == "ret_fwd_1h"].sort_values("delta_RankIC", key=abs, ascending=False)
    for _, row in r1h.iterrows():
        s = row.get("static_RankIC_mean")
        d = row.get("dynamic_RankIC_mean")
        delta = row.get("delta_RankIC")
        tag = row.get("interpretation_tag")
        print(f"  {row['factor_id']:25s} static={s:+.4f}  dynamic={d:+.4f}  delta={delta:+.4f}  [{tag}]")


if __name__ == "__main__":
    main()
