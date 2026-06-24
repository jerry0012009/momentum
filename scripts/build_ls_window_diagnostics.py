#!/usr/bin/env python3
"""PM-58C/58D: Build Period-Level LS Window Diagnostics.

Reads factor_level_period_long_short_summary.csv and computes
per-factor, per-horizon monthly period-level LS statistics.
Each row in the period summary is a monthly period-level aggregate.
This is NOT raw per-bar investment-window data.

These are RESEARCH DIAGNOSTICS, not portfolio metrics.
For 24h/72h horizons sampled at 1h, evaluation windows overlap heavily.
Monthly aggregation already smooths per-bar noise.

Overlap levels:
  1h: LOW_OVERLAP (~720 windows/month, monthly mean is well-sampled)
  4h: MODERATE_OVERLAP (~180 windows/month)
  24h: HIGH_OVERLAP (~30 windows/month)
  72h: VERY_HIGH_OVERLAP (~10 windows/month)
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}
OVERLAP_LEVEL = {
    "1h": "LOW_OVERLAP",
    "4h": "MODERATE_OVERLAP",
    "24h": "HIGH_OVERLAP",
    "72h": "VERY_HIGH_OVERLAP",
}


def _safe(v):
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return None
    return round(float(v), 10)


def build_window_diagnostics(period_path: str, output_dir: str):
    period = pd.read_csv(period_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for (fid, hz), grp in period.groupby(["factor_name", "horizon"]):
        ls = grp["long_short_return"].dropna()
        n = len(ls)
        if n < 2:
            rows.append({
                "factor_id": fid, "horizon": hz, "n_windows": n,
                "window_ls_mean": None, "window_ls_std": None,
                "window_ls_win_rate": None,
                "window_ls_ann_edge": None, "window_ls_ann_vol": None,
                "window_ls_sharpe": None,
                "bars_per_year": BARS_PER_YEAR.get(hz, 8760),
                "overlap_warning": OVERLAP_LEVEL.get(hz, "UNKNOWN"),
                "nonoverlap_available": False,
                "nonoverlap_n_windows": None,
                "nonoverlap_window_ls_win_rate": None,
            })
            continue

        ls_arr = ls.values
        bpy = BARS_PER_YEAR.get(hz, 8760)
        w_mean = _safe(np.mean(ls_arr))
        w_std = _safe(np.std(ls_arr, ddof=1))
        w_win = _safe(np.mean(ls_arr > 0))
        w_ann_edge = _safe(w_mean * bpy) if w_mean is not None else None
        w_ann_vol = _safe(w_std * np.sqrt(bpy)) if w_std is not None and w_std > 0 else None
        w_sharpe = _safe(w_mean / w_std * np.sqrt(bpy)) if w_mean is not None and w_std and w_std > 0 else None

        # Non-overlapping: for monthly data, take every ceil(horizon_hours / 720) months
        # This is approximate since we have monthly aggregates, not per-bar data.
        horizon_hours = {"1h": 1, "4h": 4, "24h": 24, "72h": 72}.get(hz, 1)
        step = max(1, int(np.ceil(horizon_hours / 24)))  # step in months
        nonoverlap = ls_arr[::step]
        n_no = len(nonoverlap)
        w_no_win = _safe(np.mean(nonoverlap > 0)) if n_no >= 2 else None

        rows.append({
            "factor_id": fid, "horizon": hz, "n_windows": n,
            "window_ls_mean": w_mean, "window_ls_std": w_std,
            "window_ls_win_rate": w_win,
            "window_ls_ann_edge": w_ann_edge, "window_ls_ann_vol": w_ann_vol,
            "window_ls_sharpe": w_sharpe,
            "bars_per_year": bpy,
            "overlap_warning": OVERLAP_LEVEL.get(hz, "UNKNOWN"),
            "nonoverlap_available": n_no >= 2,
            "nonoverlap_n_windows": n_no if n_no >= 2 else None,
            "nonoverlap_window_ls_win_rate": w_no_win,
        })

    df = pd.DataFrame(rows)
    csv_path = out_dir / "factor_ls_window_diagnostics.csv"
    json_path = out_dir / "factor_ls_window_diagnostics.json"
    df.to_csv(csv_path, index=False)

    meta = {
        "description": "PM-58C: LS window diagnostics from monthly period summary",
        "disclaimer": "Research diagnostics only. Not portfolio metrics. Not trading signals.",
        "source": str(period_path),
        "n_factors": df["factor_id"].nunique(),
        "n_rows": len(df),
        "overlap_warnings": {
            "1h": "~720 evaluation windows/month. LOW_OVERLAP.",
            "4h": "~180 evaluation windows/month. MODERATE_OVERLAP.",
            "24h": "~30 evaluation windows/month. HIGH_OVERLAP.",
            "72h": "~10 evaluation windows/month. VERY_HIGH_OVERLAP.",
        },
        "nonoverlap_note": (
            "Non-overlapping uses monthly subsampling at horizon step. "
            "True non-overlapping requires per-bar data; monthly aggregates are approximate."
        ),
    }
    with open(json_path, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Window diagnostics: {len(df)} rows ({df['factor_id'].nunique()} factors)")
    print(f"  CSV: {csv_path}")
    print(f"  JSON: {json_path}")
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period-path", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    build_window_diagnostics(args.period_path, args.output_dir)


if __name__ == "__main__":
    main()
