#!/usr/bin/env python3
"""
Canonical Signal Evaluation Pipeline.

Single active entrypoint for evaluating signals against forward returns.
Uses the public momentum.signal_evaluation API.

Usage:
    python scripts/evaluate_signals.py \
        --signal-panel <path> \
        --labels <path> \
        --signals signal_v0_core_only signal_v0_pm_full_structured \
        --horizons 1h 4h 24h 72h \
        --output-dir <dir> \
        [--spread-mode standard|legacy_phase10a]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from momentum.signal_evaluation import (
    select_forward_return,
    compute_rank_ic,
    summarize_rank_ic,
    compute_quantile_spread,
    summarize_quantile_spread,
    check_rankic_spread_consistency,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate signals against forward returns.")
    parser.add_argument("--signal-panel", required=True, help="Path to signal panel parquet")
    parser.add_argument("--labels", required=True, help="Path to labels parquet")
    parser.add_argument("--signals", required=True, nargs="+", help="Signal column names")
    parser.add_argument("--horizons", required=True, nargs="+", help="Forward return horizons (e.g. 1h 4h 24h 72h)")
    parser.add_argument("--output-dir", required=True, help="Output directory for results")
    parser.add_argument("--spread-mode", default="standard", choices=["standard", "legacy_phase10a"],
                        help="Quantile spread mode (default: standard)")
    return parser.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    signal_cols = ["timestamp", "symbol"] + args.signals
    sp = pd.read_parquet(args.signal_panel, columns=signal_cols)
    labels = pd.read_parquet(args.labels)

    # Prepare label dict
    label_dict = {}
    for hz in args.horizons:
        label_dict[hz] = select_forward_return(labels, hz)

    # Evaluate each signal × horizon
    rankic_rows = []
    spread_rows = []
    consistency_rows = []

    for sig in args.signals:
        sig_df = sp[["timestamp", "symbol", sig]].rename(
            columns={sig: "signal_value"}
        ).dropna(subset=["signal_value"])
        sig_df["signal_name"] = sig

        for hz in args.horizons:
            label_h = label_dict[hz]

            # RankIC
            ric_ts = compute_rank_ic(sig_df, label_h)
            ric_s = summarize_rank_ic(ric_ts)
            rankic_rows.append({
                "signal_id": sig, "horizon": hz,
                "mean_rankic": ric_s["mean_rank_ic"],
                "t_stat": ric_s["t_stat"],
                "n_timestamps": ric_s["n_periods"],
            })

            # Quantile Spread
            spread_ts = compute_quantile_spread(sig_df, label_h, mode=args.spread_mode)
            spread_s = summarize_quantile_spread(spread_ts)
            spread_rows.append({
                "signal_id": sig, "horizon": hz,
                "mean_spread": spread_s["mean_spread"],
                "median_spread": spread_s["median_spread"],
                "std_spread": spread_s["std_spread"],
                "hit_rate": spread_s["positive_fraction"],
                "n_timestamps": spread_s["n_periods"],
                "spread_mode": args.spread_mode,
            })

            # Consistency
            consistency = check_rankic_spread_consistency(ric_s, spread_s)
            consistency_rows.append({
                "signal_id": sig, "horizon": hz,
                "consistency": consistency,
                "mean_rankic": ric_s["mean_rank_ic"],
                "mean_spread": spread_s["mean_spread"],
            })

        print(f"  {sig}: done ({len(args.horizons)} horizons)")

    # Write outputs
    rankic_df = pd.DataFrame(rankic_rows)
    rankic_df.to_csv(out_dir / "signal_evaluation_rankic_summary.csv", index=False)

    spread_df = pd.DataFrame(spread_rows)
    spread_df.to_csv(out_dir / "signal_evaluation_quantile_spread_summary.csv", index=False)

    consistency_df = pd.DataFrame(consistency_rows)
    consistency_df.to_csv(out_dir / "signal_evaluation_consistency_summary.csv", index=False)

    # Manifest
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signal_panel": str(args.signal_panel),
        "labels": str(args.labels),
        "signals": args.signals,
        "horizons": args.horizons,
        "spread_mode": args.spread_mode,
        "n_signals": len(args.signals),
        "n_horizons": len(args.horizons),
        "total_evaluations": len(rankic_rows),
        "api_version": "momentum.signal_evaluation",
    }
    with open(out_dir / "signal_evaluation_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nOutputs written to {out_dir}/")
    print(f"  signal_evaluation_rankic_summary.csv ({len(rankic_df)} rows)")
    print(f"  signal_evaluation_quantile_spread_summary.csv ({len(spread_df)} rows)")
    print(f"  signal_evaluation_consistency_summary.csv ({len(consistency_df)} rows)")
    print(f"  signal_evaluation_manifest.json")


if __name__ == "__main__":
    main()
