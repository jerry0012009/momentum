#!/usr/bin/env python3
"""Compare static and dynamic universe factor evaluations.

Reads static evaluation from result_summary markdown table,
dynamic evaluation from per-factor JSON files,
and expected_direction from factor_catalog_v0_1.csv (authoritative).

Usage:
    python scripts/compare_static_dynamic_factor_evals.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
DYNAMIC_DIR = ROOT / "reports" / "artifacts" / "factor_eval_dynamic" / \
    "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / \
    "crypto_usdt_perp_monthly_volume_top50_current_listed_v1"
STATIC_MD = RUN / "result_summary_crypto_top50_usdt_perp_1h_long_v1.md"
CATALOG_CSV = RUN / "factor_catalog_v0_1.csv"
LABELS = ["ret_fwd_1h", "ret_fwd_4h", "ret_fwd_24h", "ret_fwd_72h"]
FACTORS = [
    "mom_20h", "reversal_5h", "volatility_20h", "rsi_14h", "bb_zscore_20h",
    "wq101_alpha101", "wq101_alpha12", "wq101_alpha53",
    "q158_high_low_range", "tech_macd", "tech_atr",
]

STATIC_PERIOD = "2024-06-13 ~ 2026-06-13"
DYNAMIC_PERIOD = "2024-06-01 ~ 2026-06-13"


def load_catalog_directions(catalog_path: Path) -> dict[str, str]:
    """Load expected_direction from factor_catalog_v0_1.csv (authoritative)."""
    df = pd.read_csv(catalog_path)
    return dict(zip(df["factor_id"], df["expected_direction"]))


def parse_static_summary(md_path: Path) -> pd.DataFrame:
    """Parse the static evaluation markdown table."""
    text = md_path.read_text(encoding="utf-8")
    lines = [l.strip() for l in text.split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return pd.DataFrame()
    header = [c.strip() for c in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
    df = pd.DataFrame(rows)
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


def assign_tags(row: pd.Series) -> pd.Series:
    """Assign stability_tag and direction_tag."""
    exp_dir = row.get("expected_direction", "positive")
    s_ric = row.get("static_RankIC_mean")
    d_ric = row.get("dynamic_RankIC_mean")

    # Stability tag
    if pd.isna(s_ric) or pd.isna(d_ric):
        stability = "insufficient_data"
    else:
        s_abs = abs(s_ric)
        d_abs = abs(d_ric)
        same_sign = (s_ric * d_ric > 0)

        if not same_sign and s_abs >= 0.01 and d_abs >= 0.01:
            stability = "sign_flipped_under_dynamic_universe"
        elif s_abs >= 0.02 and d_abs >= 0.02 and same_sign:
            stability = "strong_robust_diagnostic_candidate"
        elif s_abs >= 0.01 and d_abs >= 0.01 and same_sign:
            stability = "moderate_stable_diagnostic_candidate"
        elif s_abs >= 0.02 and d_abs < 0.01:
            stability = "weakened_under_dynamic_universe"
        else:
            stability = "unstable_or_near_zero"

    # Direction tag
    if exp_dir == "conditional":
        direction = "conditional_direction_factor"
    elif pd.isna(s_ric) or pd.isna(d_ric):
        direction = "unknown"
    else:
        # Check if empirical sign matches expected
        if exp_dir == "positive":
            direction = "direction_consistent" if (s_ric > 0 and d_ric > 0) else "direction_mismatch"
        elif exp_dir == "negative":
            direction = "direction_consistent" if (s_ric < 0 and d_ric < 0) else "direction_mismatch"
        else:
            direction = "unknown_expected_direction"

    return pd.Series({"stability_tag": stability, "direction_tag": direction})


def main():
    # Load catalog directions (authoritative)
    if CATALOG_CSV.exists():
        catalog_dirs = load_catalog_directions(CATALOG_CSV)
        print(f"Loaded {len(catalog_dirs)} factor directions from catalog")
    else:
        print(f"WARNING: Catalog not found: {CATALOG_CSV}")
        catalog_dirs = {}

    # Load static
    if not STATIC_MD.exists():
        print(f"Static summary not found: {STATIC_MD}")
        return
    static_df = parse_static_summary(STATIC_MD)
    print(f"Parsed {len(static_df)} rows from static summary")

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

    # Merge
    merged = static_df.merge(dynamic_df, on=["factor_id", "label"], how="outer")

    # Set expected_direction from catalog (authoritative)
    merged["expected_direction"] = merged["factor_id"].map(catalog_dirs)
    # Check for mismatches with dynamic JSON
    for _, row in merged.iterrows():
        fid = row["factor_id"]
        if fid in catalog_dirs:
            json_dir = row.get("expected_direction_json")
            if json_dir and json_dir != catalog_dirs[fid]:
                print(f"  WARNING: {fid} catalog={catalog_dirs[fid]} vs json={json_dir}; using catalog")

    # Compute deltas
    merged["delta_RankIC"] = merged.apply(
        lambda r: r["dynamic_RankIC_mean"] - r["static_RankIC_mean"]
        if pd.notna(r.get("dynamic_RankIC_mean")) and pd.notna(r.get("static_RankIC_mean"))
        else None, axis=1)
    merged["delta_direction_adjusted_spread"] = merged.apply(
        lambda r: r["dynamic_direction_adjusted_spread"] - r["static_direction_adjusted_spread"]
        if pd.notna(r.get("dynamic_direction_adjusted_spread")) and pd.notna(r.get("static_direction_adjusted_spread"))
        else None, axis=1)

    # Empirical signs
    merged["empirical_static_rankic_sign"] = merged["static_RankIC_mean"].apply(
        lambda x: "positive" if x > 0 else ("negative" if x < 0 else "zero") if pd.notna(x) else None)
    merged["empirical_dynamic_rankic_sign"] = merged["dynamic_RankIC_mean"].apply(
        lambda x: "positive" if x > 0 else ("negative" if x < 0 else "zero") if pd.notna(x) else None)

    # Direction matches expected
    def direction_matches(row):
        exp = row.get("expected_direction")
        s_ric = row.get("static_RankIC_mean")
        d_ric = row.get("dynamic_RankIC_mean")
        if pd.isna(s_ric) or pd.isna(d_ric) or not exp or exp == "conditional":
            return None
        if exp == "positive":
            return bool(s_ric > 0 and d_ric > 0)
        elif exp == "negative":
            return bool(s_ric < 0 and d_ric < 0)
        return None

    merged["direction_matches_expected"] = merged.apply(direction_matches, axis=1)

    # Assign tags
    tags = merged.apply(assign_tags, axis=1)
    merged["stability_tag"] = tags["stability_tag"]
    merged["direction_tag"] = tags["direction_tag"]

    # Period alignment note
    merged["period_alignment_note"] = (
        f"Static: {STATIC_PERIOD}; Dynamic: {DYNAMIC_PERIOD}. "
        "Close but not perfectly period-aligned."
    )

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
        "empirical_static_rankic_sign", "empirical_dynamic_rankic_sign",
        "direction_matches_expected",
        "stability_tag", "direction_tag",
        "period_alignment_note",
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
    json_path.write_text(
        json.dumps(result.to_dict(orient="records"), indent=2, default=str) + "\n",
        encoding="utf-8")
    print(f"Wrote: {json_path}")

    # Print summary
    print("\n=== Stability Tag Summary (ret_fwd_1h) ===")
    r1h = result[result["label"] == "ret_fwd_1h"]
    for tag, count in r1h["stability_tag"].value_counts().items():
        print(f"  {tag}: {count}")

    print("\n=== Direction Mismatch Factors (ret_fwd_1h) ===")
    mismatches = r1h[r1h["direction_matches_expected"] == False]
    for _, row in mismatches.iterrows():
        print(f"  {row['factor_id']}: expected={row['expected_direction']} "
              f"static={row['static_RankIC_mean']:+.4f} dynamic={row['dynamic_RankIC_mean']:+.4f}")

    print("\n=== ret_fwd_1h Full Comparison ===")
    for _, row in r1h.sort_values("delta_RankIC", key=abs, ascending=False).iterrows():
        s = row.get("static_RankIC_mean") or 0
        d = row.get("dynamic_RankIC_mean") or 0
        delta = row.get("delta_RankIC") or 0
        st = row.get("stability_tag", "")
        dt = row.get("direction_tag", "")
        print(f"  {row['factor_id']:25s} static={s:+.4f} dynamic={d:+.4f} delta={delta:+.4f}  [{st}] [{dt}]")


if __name__ == "__main__":
    main()
