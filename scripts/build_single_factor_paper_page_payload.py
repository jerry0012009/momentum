#!/usr/bin/env python3
"""Build compact JSON payload for single-factor paper diagnostics page (PM-22).

Reads PM-21 outputs:
  - single_factor_paper_summary.csv
  - single_factor_paper_monthly_returns.csv
  - single_factor_fee_sensitivity.csv
  - single_factor_paper_turnover.csv (timestamp-level)

Produces:
  - factor_diagnostics/single_factor_paper_page_payload.json
  - factor_diagnostics/single_factor_paper_turnover.csv (monthly aggregated)
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG_DIR = BASE / "factor_diagnostics"

SUMMARY_CSV = DIAG_DIR / "single_factor_paper_summary.csv"
MONTHLY_CSV = DIAG_DIR / "single_factor_paper_monthly_returns.csv"
FEE_CSV = DIAG_DIR / "single_factor_fee_sensitivity.csv"
TURNOVER_TS_CSV = DIAG_DIR / "single_factor_paper_turnover.csv"

OUT_PAYLOAD = DIAG_DIR / "single_factor_paper_page_payload.json"
OUT_TURNOVER = DIAG_DIR / "single_factor_paper_turnover.csv"

TARGET_FEE_BPS = [0, 5, 10, 20]


def sf(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return round(float(v), 6)


def build_turnover_monthly():
    """Aggregate timestamp-level turnover into monthly stats."""
    df = pd.read_csv(TURNOVER_TS_CSV)
    df["month"] = pd.to_datetime(df["timestamp"]).dt.to_period("M").astype(str)
    monthly = (
        df.groupby(["factor_id", "month"])["turnover"]
        .agg(avg_turnover="mean", median_turnover="median", max_turnover="max", n_observations="count")
        .reset_index()
    )
    monthly.to_csv(OUT_TURNOVER, index=False)
    print(f"  Wrote {OUT_TURNOVER} ({len(monthly)} rows)")
    return monthly


def build_payload():
    summary = pd.read_csv(SUMMARY_CSV)
    monthly = pd.read_csv(MONTHLY_CSV)
    fee_sens = pd.read_csv(FEE_CSV)
    turnover_mo = build_turnover_monthly()

    factors = []
    for _, row in summary.iterrows():
        fid = str(row["factor_id"])

        # Monthly returns for this factor, fee_bps in TARGET_FEE_BPS
        fmo = monthly[monthly["factor_id"] == fid]

        # Build monthly_nav_series_compact: compound monthly returns to NAV
        # for each target fee level
        nav_series = {}
        for fb in TARGET_FEE_BPS:
            sub = fmo[fmo["fee_bps"] == fb].sort_values("month")
            if sub.empty:
                nav_series[str(fb)] = []
                continue
            nav = 1.0
            points = []
            for _, r in sub.iterrows():
                nav *= (1.0 + float(r["monthly_return"]))
                points.append({"month": str(r["month"]), "nav": sf(nav)})
            nav_series[str(fb)] = points

        # Fee sensitivity series
        ffee = fee_sens[fee_sens["factor_id"] == fid].sort_values("fee_bps")
        fee_sensitivity_series = []
        for _, r in ffee.iterrows():
            fee_sensitivity_series.append({
                "fee_bps": int(r["fee_bps"]),
                "total_return": sf(r["total_return"]),
                "sharpe": sf(r["sharpe"]),
            })

        # Monthly return series for fee_bps=10
        fmo10 = fmo[fmo["fee_bps"] == 10].sort_values("month")
        monthly_return_series = []
        for _, r in fmo10.iterrows():
            monthly_return_series.append({
                "month": str(r["month"]),
                "monthly_return": sf(r["monthly_return"]),
                "fee_bps": 10,
            })

        # Fee-specific total returns
        fee_map = {}
        for _, r in ffee.iterrows():
            fee_map[int(r["fee_bps"])] = sf(r["total_return"])

        factors.append({
            "factor_id": fid,
            "paper_viability_class": str(row.get("paper_viability_class", "")),
            "cost_sensitivity_class": str(row.get("cost_sensitivity_class", "")),
            "gross_sharpe": sf(row.get("gross_sharpe")),
            "gross_total_return": sf(row.get("gross_total_return")),
            "max_drawdown": sf(row.get("max_drawdown")),
            "positive_month_rate": sf(row.get("positive_month_rate")),
            "avg_turnover": sf(row.get("avg_turnover")),
            "median_turnover": sf(row.get("median_turnover")),
            "break_even_fee_bps": sf(row.get("break_even_fee_bps")),
            "fee_0bps_total_return": fee_map.get(0),
            "fee_5bps_total_return": fee_map.get(5),
            "fee_10bps_total_return": fee_map.get(10),
            "fee_20bps_total_return": fee_map.get(20),
            "main_diagnostic_note_zh": str(row.get("main_diagnostic_note_zh", "")),
            "main_diagnostic_note_en": str(row.get("main_diagnostic_note_en", "")),
            "monthly_nav_series_compact": nav_series,
            "fee_sensitivity_series": fee_sensitivity_series,
            "monthly_return_series": monthly_return_series,
        })

    payload = {
        "pm": "PM-22",
        "description": "Single-factor paper portfolio page payload",
        "factor_count": len(factors),
        "factors": factors,
    }
    OUT_PAYLOAD.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  Wrote {OUT_PAYLOAD} ({len(factors)} factors, {OUT_PAYLOAD.stat().st_size:,} bytes)")


if __name__ == "__main__":
    print("Building single-factor paper page payload...")
    build_payload()
    print("Done.")
