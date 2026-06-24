#!/usr/bin/env python3
"""Build factor diagnostics metrics from canonical evaluation outputs.

PM-13: Converts factor-level evaluation artifacts into decision-grade
diagnostic outputs. Read-only with respect to factor_values.

Outputs:
  factor_diagnostics_summary.csv/json  — one row per factor (best horizon)
  factor_monthly_ic_series.csv         — one row per factor × horizon × month
  factor_monthly_long_short_series.csv — one row per factor × horizon × month (if available)
  factor_cumulative_long_short_curve.csv — cumulative LS curve (if available)
  manifest.json

Diagnostic only. Not production. Not live trading.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Column name mappings (canonical evaluation uses 'factor_name', not 'factor_id')
# ---------------------------------------------------------------------------
FACTOR_COL_CANDIDATES = ["factor_name", "factor_id"]
HORIZON_COL = "horizon"
PERIOD_COL = "period"


def _find_factor_col(df: pd.DataFrame) -> str:
    for c in FACTOR_COL_CANDIDATES:
        if c in df.columns:
            return c
    raise ValueError(f"No factor column found. Columns: {list(df.columns)}")


def _safe_float(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    return round(float(v), 8)


# ---------------------------------------------------------------------------
# 1. Monthly IC series
# ---------------------------------------------------------------------------
def build_monthly_ic_series(input_dir: Path) -> tuple[pd.DataFrame, bool]:
    """Build monthly IC series from period_ic_summary."""
    path = input_dir / "factor_level_period_ic_summary.csv"
    if not path.exists():
        print(f"  WARNING: {path} not found", flush=True)
        return pd.DataFrame(), False

    df = pd.read_csv(path)
    fcol = _find_factor_col(df)

    # Filter to factor × horizon rows with valid period data
    rows = []
    for _, r in df.iterrows():
        period = r.get(PERIOD_COL)
        if pd.isna(period):
            continue
        rows.append({
            "factor_id": r[fcol],
            "horizon": str(r[HORIZON_COL]),
            "month": str(period),
            "rank_ic": _safe_float(r.get("raw_mean_rank_ic")),
            "rank_ic_adj": _safe_float(r.get("direction_adjusted_mean_rank_ic")),
            "n_obs": int(r["n_periods"]) if pd.notna(r.get("n_periods")) else None,
            "positive_ic": bool(r.get("ic_win_rate_adjusted", 0) > 0.5) if pd.notna(r.get("ic_win_rate_adjusted")) else None,
        })

    out = pd.DataFrame(rows)
    if len(out) > 0:
        out = out.sort_values(["factor_id", "horizon", "month"]).reset_index(drop=True)
    return out, len(out) > 0


# ---------------------------------------------------------------------------
# 2. Monthly long-short series (from quantile returns if period-level available)
# ---------------------------------------------------------------------------
def build_monthly_ls_series(input_dir: Path) -> tuple[pd.DataFrame, bool]:
    """Build monthly LS series from period_long_short_summary."""
    path = input_dir / "factor_level_period_long_short_summary.csv"
    if not path.exists():
        print(f"  WARNING: {path} not found", flush=True)
        return pd.DataFrame(), False

    df = pd.read_csv(path)
    if len(df) == 0:
        return pd.DataFrame(), False

    fcol = _find_factor_col(df)

    rows = []
    for _, r in df.iterrows():
        ls_ret = r.get("long_short_return")
        if pd.isna(ls_ret):
            continue
        rows.append({
            "factor_id": r[fcol],
            "horizon": str(r[HORIZON_COL]),
            "month": str(r["period"]),
            "long_short_return": _safe_float(ls_ret),
            "long_leg_return": _safe_float(r.get("long_leg_return")),
            "short_leg_return": _safe_float(r.get("short_leg_return")),
            "n_long": int(r["n_timestamps"]) if pd.notna(r.get("n_timestamps")) else None,
            "n_short": int(r["n_timestamps"]) if pd.notna(r.get("n_timestamps")) else None,
            "positive_ls": bool(r.get("positive_ls", False)),
        })

    out = pd.DataFrame(rows)
    if len(out) > 0:
        out = out.sort_values(["factor_id", "horizon", "month"]).reset_index(drop=True)
    return out, len(out) > 0


# ---------------------------------------------------------------------------
# 3. Cumulative long-short curve (depends on monthly LS)
# ---------------------------------------------------------------------------
def build_cumulative_ls_curve(monthly_ls: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    """Build cumulative LS curve from monthly LS series."""
    if monthly_ls.empty:
        return pd.DataFrame(), False

    rows = []
    for (fid, hz), grp in monthly_ls.groupby(["factor_id", "horizon"]):
        grp = grp.sort_values("month")
        cum_ret = 1.0
        peak = 1.0
        for _, r in grp.iterrows():
            ls_ret = r["long_short_return"]
            if pd.isna(ls_ret):
                continue
            cum_ret *= (1 + ls_ret)
            peak = max(peak, cum_ret)
            dd = cum_ret / peak - 1 if peak > 0 else 0.0
            rows.append({
                "factor_id": fid,
                "horizon": hz,
                "month": r["month"],
                "long_short_return": _safe_float(ls_ret),
                "cum_long_short_return": _safe_float(cum_ret - 1),
                "drawdown": _safe_float(dd),
            })

    out = pd.DataFrame(rows)
    if len(out) > 0:
        out = out.sort_values(["factor_id", "horizon", "month"]).reset_index(drop=True)
    return out, len(out) > 0


# ---------------------------------------------------------------------------
# 4. Factor diagnostics summary (one row per factor)
# ---------------------------------------------------------------------------
def build_diagnostics_summary(
    input_dir: Path,
    state: dict,
    monthly_ic: pd.DataFrame,
    monthly_ls: pd.DataFrame,
    cumulative_ls: pd.DataFrame,
) -> pd.DataFrame:
    """Build per-factor diagnostics summary."""
    # Load source artifacts
    mp_path = input_dir / "factor_level_metric_panel.csv"
    mp = pd.read_csv(mp_path) if mp_path.exists() else pd.DataFrame()
    fcol_mp = _find_factor_col(mp) if len(mp) > 0 else None

    cov_path = input_dir / "factor_level_coverage_summary.csv"
    cov = pd.read_csv(cov_path) if cov_path.exists() else pd.DataFrame()
    fcol_cov = _find_factor_col(cov) if len(cov) > 0 else None

    rd_path = input_dir / "factor_redundancy.csv"
    rd = pd.read_csv(rd_path) if rd_path.exists() else pd.DataFrame()

    cr_path = input_dir / "factor_level_candidate_review.csv"
    cr = pd.read_csv(cr_path) if cr_path.exists() else pd.DataFrame()
    fcol_cr = _find_factor_col(cr) if len(cr) > 0 else None

    # Registry for metadata
    registry = {r["factor_id"]: r for r in state.get("factor_registry", [])}
    # Fallback: load from catalog
    cat_path = Path(state.get("canonical_paths", {}).get("catalog_json", ""))
    if cat_path.exists():
        cat = json.loads(cat_path.read_text())
        for f in cat.get("factors", []):
            if f["factor_id"] not in registry:
                registry[f["factor_id"]] = f

    # Build redundancy lookup
    rd_lookup = {}
    if len(rd) > 0 and "factor_i" in rd.columns:
        for _, r in rd.iterrows():
            fi, fj = r["factor_i"], r["factor_j"]
            level = r.get("redundancy_level", "UNKNOWN")
            if fi not in rd_lookup or level in ("HIGH", "MODERATE"):
                rd_lookup[fi] = {"level": level, "nearest": fj}
            if fj not in rd_lookup or level in ("HIGH", "MODERATE"):
                rd_lookup[fj] = {"level": level, "nearest": fi}

    # Build candidate review lookup
    cr_lookup = {}
    if len(cr) > 0 and fcol_cr:
        for _, r in cr.iterrows():
            cr_lookup[r[fcol_cr]] = {
                "bucket": r.get("review_bucket", r.get("candidate_review_bucket", "")),
                "action": r.get("recommended_action", ""),
            }

    # All registered factors
    factor_ids = state.get("registered_factor_ids", [])
    rows = []
    for fid in factor_ids:
        reg = registry.get(fid, {})
        # Metric panel: find best horizon by highest abs adj IC
        best_hz = None
        best_adj_ic = None
        best_row = None
        if len(mp) > 0 and fcol_mp:
            frows = mp[mp[fcol_mp] == fid]
            if len(frows) > 0:
                for _, r in frows.iterrows():
                    adj = r.get("direction_adjusted_mean_rank_ic")
                    if pd.notna(adj) and (best_adj_ic is None or abs(adj) > abs(best_adj_ic)):
                        best_adj_ic = adj
                        best_hz = str(r[HORIZON_COL])
                        best_row = r

        # Coverage (from metric_panel — coverage is row count, convert to rate)
        TOTAL_ROWS = 3_316_259  # canonical bars row count
        cov_rate = None
        if len(mp) > 0 and fcol_mp and "coverage" in mp.columns:
            frows_all = mp[mp[fcol_mp] == fid]
            if len(frows_all) > 0:
                raw_cov = frows_all["coverage"].max()
                if pd.notna(raw_cov):
                    cov_rate = _safe_float(raw_cov / TOTAL_ROWS)
        if len(cov) > 0 and fcol_cov:
            crow = cov[cov[fcol_cov] == fid]
            if len(crow) > 0:
                if best_hz is None:
                    best_hz = str(crow.iloc[0].get("best_adj_ic_horizon", ""))

        # Monthly IC stats for best horizon
        ic_positive_rate = None
        if len(monthly_ic) > 0 and best_hz:
            mic = monthly_ic[(monthly_ic["factor_id"] == fid) & (monthly_ic["horizon"] == best_hz)]
            if len(mic) > 0:
                ic_positive_rate = _safe_float(mic["positive_ic"].mean())

        # Monthly LS stats (if available)
        # NOTE: ls_mean = mean(per-bar LS returns), NOT a cumulative monthly return.
        # - Ann Return: multiply by bars-per-year (horizon-aware)
        # - Sharpe/Vol: annualize from monthly aggregates using ×√12 (standard monthly annualization)
        _BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}
        ls_mean = ls_std = ls_sharpe = ls_ann_ret = ls_ann_vol = ls_max_dd = ls_pos_rate = None
        if len(monthly_ls) > 0 and best_hz:
            mls = monthly_ls[(monthly_ls["factor_id"] == fid) & (monthly_ls["horizon"] == best_hz)]
            if len(mls) > 0:
                ls_arr = mls["long_short_return"].dropna().values
                if len(ls_arr) > 0:
                    ls_mean = _safe_float(np.mean(ls_arr))
                    ls_std = _safe_float(np.std(ls_arr, ddof=1)) if len(ls_arr) > 1 else 0.0
                    bpy = _BARS_PER_YEAR.get(best_hz, 8760)
                    if ls_std and ls_std > 0:
                        ls_sharpe = _safe_float(ls_mean / ls_std * np.sqrt(12))
                    ls_ann_ret = _safe_float(ls_mean * bpy)
                    ls_ann_vol = _safe_float(ls_std * np.sqrt(12)) if ls_std else None
                    ls_pos_rate = _safe_float(np.mean(ls_arr > 0))

        # Max drawdown from cumulative curve
        if len(cumulative_ls) > 0 and best_hz:
            cls = cumulative_ls[(cumulative_ls["factor_id"] == fid) & (cumulative_ls["horizon"] == best_hz)]
            if len(cls) > 0 and "drawdown" in cls.columns:
                ls_max_dd = _safe_float(cls["drawdown"].min())

        # Redundancy
        rd_level = rd_lookup.get(fid, {}).get("level", "UNKNOWN")
        rd_nearest = rd_lookup.get(fid, {}).get("nearest", "")

        # Decision bucket
        cr_info = cr_lookup.get(fid, {})
        decision_bucket = cr_info.get("bucket", "UNKNOWN")
        recommended_action = cr_info.get("action", "")

        # Source warning
        warnings = []
        if not best_hz:
            warnings.append("no_horizon_data")
        if ls_mean is None:
            warnings.append("monthly_ls_unavailable")

        rows.append({
            "factor_id": fid,
            "family": reg.get("category", reg.get("family", "")),
            "lifecycle_status": reg.get("lifecycle_status", ""),
            "required_columns": ",".join(reg.get("required_columns", [])),
            "expected_direction": reg.get("expected_direction", ""),
            "best_horizon": best_hz or "",
            "rankic_mean": _safe_float(best_row.get("direction_adjusted_mean_rank_ic")) if best_row is not None else None,
            "rankic_std": _safe_float(best_row.get("direction_adjusted_rank_ic_std")) if best_row is not None else None,
            "rankic_ir": _safe_float(best_row.get("direction_adjusted_icir")) if best_row is not None else None,
            "rankic_t_stat": _safe_float(best_row.get("t_stat")) if best_row is not None else None,
            "monthly_ic_positive_rate": ic_positive_rate,
            "long_short_mean": ls_mean,
            "long_short_std": ls_std,
            "long_short_sharpe": ls_sharpe,
            "long_short_annualized_return": ls_ann_ret,
            "long_short_annualized_vol": ls_ann_vol,
            "long_short_max_drawdown": ls_max_dd,
            "long_short_positive_month_rate": ls_pos_rate,
            "coverage_rate": cov_rate,
            "redundancy_level": rd_level,
            "nearest_redundant_factor": rd_nearest,
            "decision_bucket": decision_bucket,
            "recommended_action": recommended_action,
            "source_warning": ";".join(warnings) if warnings else "",
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(description="Build factor diagnostics metrics")
    p.add_argument("--input-dir", required=True, help="Factor level evaluation directory")
    p.add_argument("--state-path", required=True, help="Factor library state JSON")
    p.add_argument("--output-dir", required=True, help="Output directory for diagnostics")
    args = p.parse_args()

    input_dir = Path(args.input_dir)
    state_path = Path(args.state_path)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"ERROR: input dir not found: {input_dir}")
        sys.exit(1)
    if not state_path.exists():
        print(f"ERROR: state file not found: {state_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    state = json.loads(state_path.read_text())
    n_registered = state.get("registered_factors", 0)
    n_computed = state.get("computed_factor_values", 0)
    print(f"Factor library state: {n_registered} registered, {n_computed} computed", flush=True)

    # 1. Monthly IC series
    print("Building monthly IC series...", flush=True)
    monthly_ic, ic_available = build_monthly_ic_series(input_dir)
    if ic_available:
        out_path = output_dir / "factor_monthly_ic_series.csv"
        monthly_ic.to_csv(out_path, index=False)
        print(f"  Wrote {out_path} ({len(monthly_ic)} rows, {monthly_ic['factor_id'].nunique()} factors)", flush=True)
    else:
        print("  WARNING: monthly IC not available", flush=True)

    # 2. Monthly LS series
    print("Building monthly LS series...", flush=True)
    monthly_ls, ls_available = build_monthly_ls_series(input_dir)
    if ls_available:
        out_path = output_dir / "factor_monthly_long_short_series.csv"
        monthly_ls.to_csv(out_path, index=False)
        print(f"  Wrote {out_path} ({len(monthly_ls)} rows)", flush=True)
    else:
        print("  INFO: monthly LS not available (quantile returns lack period column)", flush=True)
        # Write empty file with headers for consistency
        empty_ls = pd.DataFrame(columns=["factor_id", "horizon", "month", "long_short_return",
                                          "long_leg_return", "short_leg_return", "n_long", "n_short", "positive_ls"])
        empty_ls.to_csv(output_dir / "factor_monthly_long_short_series.csv", index=False)

    # 3. Cumulative LS curve
    print("Building cumulative LS curve...", flush=True)
    cumulative_ls, cum_available = build_cumulative_ls_curve(monthly_ls)
    if cum_available:
        out_path = output_dir / "factor_cumulative_long_short_curve.csv"
        cumulative_ls.to_csv(out_path, index=False)
        print(f"  Wrote {out_path} ({len(cumulative_ls)} rows)", flush=True)
    else:
        print("  INFO: cumulative LS not available (depends on monthly LS)", flush=True)
        empty_cum = pd.DataFrame(columns=["factor_id", "horizon", "month", "long_short_return",
                                           "cum_long_short_return", "drawdown"])
        empty_cum.to_csv(output_dir / "factor_cumulative_long_short_curve.csv", index=False)

    # 4. Diagnostics summary
    print("Building diagnostics summary...", flush=True)
    summary = build_diagnostics_summary(input_dir, state, monthly_ic, monthly_ls, cumulative_ls)
    csv_path = output_dir / "factor_diagnostics_summary.csv"
    summary.to_csv(csv_path, index=False)
    print(f"  Wrote {csv_path} ({len(summary)} factors)", flush=True)

    json_path = output_dir / "factor_diagnostics_summary.json"
    json_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "factor_count": len(summary),
        "factors": summary.to_dict(orient="records"),
        "disclaimer": "Factor diagnostics summary. Diagnostic only. Not production. Not live trading.",
    }
    json_path.write_text(json.dumps(json_data, indent=2, default=str))
    print(f"  Wrote {json_path}", flush=True)

    # 5. Manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": {
            "metric_panel": str(input_dir / "factor_level_metric_panel.csv"),
            "rankic_summary": str(input_dir / "factor_level_rankic_summary.csv"),
            "period_ic_summary": str(input_dir / "factor_level_period_ic_summary.csv"),
            "quantile_return_summary": str(input_dir / "factor_level_quantile_return_summary.csv"),
            "long_short_summary": str(input_dir / "factor_level_long_short_summary.csv"),
            "candidate_review": str(input_dir / "factor_level_candidate_review.csv"),
            "coverage_summary": str(input_dir / "factor_level_coverage_summary.csv"),
            "redundancy": str(input_dir / "factor_redundancy.csv"),
            "state": str(state_path),
        },
        "output_files": [
            "factor_diagnostics_summary.csv",
            "factor_diagnostics_summary.json",
            "factor_monthly_ic_series.csv",
            "factor_monthly_long_short_series.csv",
            "factor_cumulative_long_short_curve.csv",
        ],
        "factor_count": n_registered,
        "horizon_count": len(state.get("horizons", [])),
        "evaluation_refreshed": False,
        "monthly_ic_available": ic_available,
        "monthly_ls_available": ls_available,
        "cumulative_ls_available": cum_available,
        "warnings": [],
        "metric_formula_definitions": {
            "monthly_ic": "Monthly mean of daily rank IC from period_ic_summary",
            "monthly_ic_positive_rate": "Fraction of months with positive direction-adjusted IC",
            "long_short_sharpe": "mean(monthly_LS) / std(monthly_LS) * sqrt(12) — monthly annualization (not per-bar)",
            "long_short_annualized_return": "mean(per-bar_LS) * bars_per_year — bars_per_year = {1h:8760, 4h:2190, 24h:365, 72h:122}",
            "long_short_annualized_vol": "std(monthly_LS) * sqrt(12) — monthly annualization (not per-bar)",
            "long_short_max_drawdown": "min(cum_LS / rolling_peak - 1) — requires monthly LS",
            "cumulative_ls": "cumulative product of (1 + monthly_LS) - 1 — requires monthly LS",
        },
        "disclaimer": "Factor diagnostics metrics. Diagnostic only. Not production. Not live trading.",
    }

    if not ls_available:
        manifest["warnings"].append("monthly_long_short_unavailable=true")
        manifest["warnings"].append("quantile_return_summary lacks period/month column; PM-13B or evaluator extension needed")

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  Wrote {manifest_path}", flush=True)

    # Summary
    print(f"\n=== Diagnostics Metrics Complete ===", flush=True)
    print(f"  Factors: {n_registered}", flush=True)
    print(f"  Monthly IC: {'available' if ic_available else 'UNAVAILABLE'}", flush=True)
    print(f"  Monthly LS: {'available' if ls_available else 'UNAVAILABLE (needs evaluator extension)'}", flush=True)
    print(f"  Cumulative LS: {'available' if cum_available else 'UNAVAILABLE'}", flush=True)


if __name__ == "__main__":
    main()
