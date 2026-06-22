#!/usr/bin/env python3
"""Build compact JSON payload for single-factor paper diagnostics page (PM-21B).

Reads PM-21B compact outputs:
  - single_factor_paper_summary.csv
  - single_factor_paper_monthly_returns.csv
  - single_factor_fee_sensitivity.csv
  - single_factor_paper_turnover.csv (already monthly from PM-21B)
  - single_factor_paper_leg_decomposition.csv
  - single_factor_paper_drawdown_curve.csv

Produces:
  - factor_diagnostics/single_factor_paper_page_payload.json
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
TURNOVER_CSV = DIAG_DIR / "single_factor_paper_turnover.csv"
LEG_CSV = DIAG_DIR / "single_factor_paper_leg_decomposition.csv"
DRAWDOWN_CSV = DIAG_DIR / "single_factor_paper_drawdown_curve.csv"

OUT_PAYLOAD = DIAG_DIR / "single_factor_paper_page_payload.json"

TARGET_FEE_BPS = [0, 5, 10, 20]


def sf(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return round(float(v), 6)


def build_payload():
    summary = pd.read_csv(SUMMARY_CSV)
    monthly = pd.read_csv(MONTHLY_CSV)
    fee_sens = pd.read_csv(FEE_CSV)
    turnover_mo = pd.read_csv(TURNOVER_CSV)
    leg = pd.read_csv(LEG_CSV)
    drawdown = pd.read_csv(DRAWDOWN_CSV)

    factors = []
    for _, row in summary.iterrows():
        fid = str(row["factor_id"])

        # Monthly returns for this factor
        fmo = monthly[monthly["factor_id"] == fid]

        # Build monthly_nav_series_compact
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

        # Turnover series (already monthly)
        fturn = turnover_mo[turnover_mo["factor_id"] == fid].sort_values("month")
        turnover_series = []
        for _, r in fturn.iterrows():
            turnover_series.append({
                "month": str(r["month"]),
                "avg_turnover": sf(r["avg_turnover"]),
                "median_turnover": sf(r["median_turnover"]),
            })

        # Leg decomposition series (at fee_bps=10)
        fleg = leg[(leg["factor_id"] == fid) & (leg["fee_bps"] == 10)].sort_values("month")
        leg_series = []
        for _, r in fleg.iterrows():
            leg_series.append({
                "month": str(r["month"]),
                "long_leg_return": sf(r["long_leg_return"]),
                "short_leg_return": sf(r["short_leg_return"]),
                "net_long_short_return": sf(r["net_long_short_return"]),
            })

        # Drawdown series (at fee_bps=10)
        fdd = drawdown[(drawdown["factor_id"] == fid) & (drawdown["fee_bps"] == 10)].sort_values("month")
        drawdown_series = []
        for _, r in fdd.iterrows():
            drawdown_series.append({
                "month": str(r["month"]),
                "nav": sf(r["nav"]),
                "drawdown": sf(r["drawdown"]),
                "monthly_return": sf(r["monthly_return"]),
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
            "turnover_series": turnover_series,
            "leg_decomposition_series": leg_series,
            "drawdown_series": drawdown_series,
        })

    payload = {
        "pm": "PM-21B",
        "description": "Single-factor paper portfolio page payload (reproducible)",
        "factor_count": len(factors),
        "factors": factors,
    }
    OUT_PAYLOAD.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  Wrote {OUT_PAYLOAD} ({len(factors)} factors, {OUT_PAYLOAD.stat().st_size:,} bytes)")


if __name__ == "__main__":
    print("Building single-factor paper page payload (PM-21B)...")
    build_payload()
    print("Done.")
