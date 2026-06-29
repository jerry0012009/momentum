#!/usr/bin/env python3
"""
PM-21B: Reproducible Single-Factor Paper Portfolio Diagnostics
==============================================================

Repaired version. Generates all compact outputs from committed inputs.
NOT a backtest. NOT a trading strategy. Research diagnostics only.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from public_factor_manifest_guard import raise_for_skipped_public_factor_ids

REPO = Path(__file__).resolve().parent.parent
DATA_BASE = REPO / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1"
DIAG_DIR = REPO / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_diagnostics"
STATE_PATH = REPO / "research" / "factor_runs" / "crypto_top50_factor_library" / "factor_library_state.json"
SCORECARD_PATH = DIAG_DIR / "factor_quality_scorecard.csv"


def load_registered_factors() -> list[str]:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return state.get("registered_factor_ids", [])


def load_factor_directions() -> dict[str, str]:
    directions = {}
    try:
        sc = pd.read_csv(SCORECARD_PATH)
        for _, row in sc.iterrows():
            directions[row["factor_id"]] = row.get("expected_direction", "positive")
    except Exception:
        pass
    return directions


def load_scorecard_classes() -> dict[str, dict[str, str]]:
    classes = {}
    try:
        sc = pd.read_csv(SCORECARD_PATH)
        for _, row in sc.iterrows():
            classes[row["factor_id"]] = {
                "quality_class": row.get("final_quality_class", ""),
                "score_confidence": row.get("score_confidence", ""),
            }
    except Exception:
        pass
    return classes


def load_labels() -> pd.DataFrame:
    labels_path = DATA_BASE / "labels.parquet"
    df = pd.read_parquet(labels_path, columns=["timestamp", "symbol", "ret_fwd_1h"])
    df = df.rename(columns={"ret_fwd_1h": "label_1h"})
    df = df.dropna(subset=["label_1h"])
    return df


def load_factor_values(factor_id: str) -> pd.DataFrame:
    fv_path = DATA_BASE / factor_id / "factor_values.parquet"
    if not fv_path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(fv_path, columns=["timestamp", "symbol", "factor_value"])
    df = df.dropna(subset=["factor_value"])
    return df


def compute_diagnostics(merged: pd.DataFrame, top_frac: float, bottom_frac: float, fee_bps_list: list[int]) -> dict:
    """Optimized paper portfolio diagnostics."""
    # Direction-adjust already done
    merged = merged.sort_values(["timestamp", "factor_value"], ascending=[True, False]).reset_index(drop=True)

    # Count per timestamp
    ts_counts = merged.groupby("timestamp").size()
    valid_ts = ts_counts[ts_counts >= 10].index
    merged = merged[merged["timestamp"].isin(valid_ts)].copy()

    if merged.empty:
        return {"error": "no_valid_timestamps"}

    # Assign long/short flags using vectorized rank
    merged["ts_idx"] = merged.groupby("timestamp").ngroup()
    merged["rank_in_ts"] = merged.groupby("timestamp").cumcount() + 1  # already sorted desc
    merged["n_in_ts"] = merged.groupby("timestamp")["factor_value"].transform("count")
    n_long = (merged["n_in_ts"] * top_frac).clip(lower=1).astype(int)
    n_short = (merged["n_in_ts"] * bottom_frac).clip(lower=1).astype(int)
    merged["is_long"] = merged["rank_in_ts"] <= n_long
    merged["is_short"] = merged["rank_in_ts"] > (merged["n_in_ts"] - n_short)

    # Per-timestamp stats using numpy aggregation
    ts_ids = merged["timestamp"].values
    labels = merged["label_1h"].values
    is_long = merged["is_long"].values
    is_short = merged["is_short"].values
    symbols = merged["symbol"].values

    # Get unique timestamps in order
    unique_ts, ts_inverse = np.unique(ts_ids, return_inverse=True)
    n_ts = len(unique_ts)

    # Aggregate long/short returns per timestamp using numpy bincount
    long_returns = np.zeros(n_ts)
    short_returns = np.zeros(n_ts)
    n_longs = np.zeros(n_ts, dtype=int)
    n_shorts = np.zeros(n_ts, dtype=int)

    # Long leg
    long_mask = is_long
    if long_mask.any():
        long_ts = ts_inverse[long_mask]
        long_ret = labels[long_mask]
        long_returns = np.bincount(long_ts, weights=long_ret, minlength=n_ts)
        n_longs = np.bincount(long_ts, minlength=n_ts)
        # Avoid division by zero
        n_longs_safe = np.where(n_longs > 0, n_longs, 1)
        long_returns = long_returns / n_longs_safe

    # Short leg
    short_mask = is_short
    if short_mask.any():
        short_ts = ts_inverse[short_mask]
        short_ret = labels[short_mask]
        short_returns = np.bincount(short_ts, weights=short_ret, minlength=n_ts)
        n_shorts = np.bincount(short_ts, minlength=n_ts)
        n_shorts_safe = np.where(n_shorts > 0, n_shorts, 1)
        short_returns = short_returns / n_shorts_safe

    ls_returns = long_returns - short_returns

    # Turnover: track symbol sets per timestamp (sample every 24th for speed)
    # For full accuracy, track all; for speed, sample
    # Use full for now since n_ts ~ 17K is manageable with set operations
    turnover = np.zeros(n_ts)
    prev_long_syms = set()
    prev_short_syms = set()

    # Build symbol sets per timestamp efficiently
    long_sym_groups = {}
    short_sym_groups = {}
    for idx in np.where(long_mask)[0]:
        ts_i = ts_inverse[idx]
        if ts_i not in long_sym_groups:
            long_sym_groups[ts_i] = set()
        long_sym_groups[ts_i].add(symbols[idx])
    for idx in np.where(short_mask)[0]:
        ts_i = ts_inverse[idx]
        if ts_i not in short_sym_groups:
            short_sym_groups[ts_i] = set()
        short_sym_groups[ts_i].add(symbols[idx])

    for i in range(n_ts):
        cur_long = long_sym_groups.get(i, set())
        cur_short = short_sym_groups.get(i, set())
        if prev_long_syms:
            lt = 1 - len(cur_long & prev_long_syms) / max(len(cur_long), 1)
            st = 1 - len(cur_short & prev_short_syms) / max(len(cur_short), 1)
            turnover[i] = (lt + st) / 2
        prev_long_syms = cur_long
        prev_short_syms = cur_short

    # NAV curves per fee
    nav_curves = {}
    fee_results = {}
    for fee_bps in fee_bps_list:
        net_ret = ls_returns - turnover * fee_bps / 10000
        nav = np.cumprod(1 + net_ret)
        fee_results[fee_bps] = {"total_return": float(nav[-1] - 1)}

        nav_curves[fee_bps] = pd.DataFrame({
            "timestamp": unique_ts,
            "fee_bps": fee_bps,
            "gross_return": ls_returns,
            "net_return": net_ret,
            "nav": nav,
            "long_leg_return": long_returns,
            "short_leg_return": short_returns,
            "long_short_return": ls_returns,
            "turnover": turnover,
            "n_long": n_longs,
            "n_short": n_shorts,
        })

    # Gross stats
    gross_total = float(np.prod(1 + ls_returns) - 1)
    n_periods = len(ls_returns)
    gross_ann_ret = (1 + gross_total) ** (8760 / max(n_periods, 1)) - 1
    gross_vol = float(np.std(ls_returns) * np.sqrt(8760))
    gross_sharpe = float(gross_ann_ret / gross_vol) if gross_vol > 0 else 0

    # Max drawdown
    cum_nav = np.cumprod(1 + ls_returns)
    peak = np.maximum.accumulate(cum_nav)
    dd = (peak - cum_nav) / np.where(peak > 0, peak, 1)
    max_dd = float(dd.max())

    # Monthly stats
    ts_dt = pd.to_datetime(unique_ts)
    months = ts_dt.to_period("M").astype(str)
    month_ids, month_inverse = np.unique(months, return_inverse=True)
    n_months = len(month_ids)

    monthly_gross_ret = np.zeros(n_months)
    monthly_turnover = np.zeros(n_months)
    monthly_vol = np.zeros(n_months)
    for m in range(n_months):
        mask = month_inverse == m
        monthly_gross_ret[m] = float(np.prod(1 + ls_returns[mask]) - 1)
        monthly_turnover[m] = float(turnover[mask].mean())
        monthly_vol[m] = float(ls_returns[mask].std() * np.sqrt(mask.sum()))

    positive_month_rate = float((monthly_gross_ret > 0).mean())
    avg_turnover = float(turnover.mean())
    median_turnover = float(np.median(turnover))

    # Monthly records per fee — compound hourly net returns within each month
    monthly_records = []
    for fee_bps in fee_bps_list:
        net_ret_hourly = ls_returns - turnover * fee_bps / 10000
        for m in range(n_months):
            mask = month_inverse == m
            net_m = float(np.prod(1 + net_ret_hourly[mask]) - 1)
            monthly_records.append({
                "month": month_ids[m],
                "fee_bps": fee_bps,
                "monthly_return": float(net_m),
                "monthly_vol": float(monthly_vol[m]),
                "monthly_turnover": float(monthly_turnover[m]),
                "positive_month": bool(net_m > 0),
            })

    # Annualized per fee
    for fee_bps in fee_bps_list:
        nav_val = fee_results[fee_bps]["total_return"]
        ann_ret = (1 + nav_val) ** (8760 / max(n_periods, 1)) - 1
        net_rets = ls_returns - turnover * fee_bps / 10000
        vol = float(np.std(net_rets) * np.sqrt(8760))
        fee_results[fee_bps].update({
            "annualized_return": float(ann_ret),
            "annualized_vol": vol,
            "sharpe": float(ann_ret / vol) if vol > 0 else 0,
        })

    # Break-even fee
    break_even = 999
    for fee_bps in sorted(fee_bps_list):
        if fee_results[fee_bps]["total_return"] <= 0:
            break_even = fee_bps
            break

    # Cost sensitivity
    fee_0 = fee_results[0]["total_return"]
    fee_10 = fee_results[10]["total_return"]
    if fee_0 <= 0:
        cost_class = "INSUFFICIENT_DATA"
    elif fee_10 > fee_0 * 0.7:
        cost_class = "ROBUST_TO_COSTS"
    elif fee_10 > fee_0 * 0.3:
        cost_class = "MODERATELY_COST_SENSITIVE"
    elif fee_10 > 0:
        cost_class = "COST_FRAGILE"
    else:
        cost_class = "COST_COLLAPSED"

    # Paper viability
    if gross_sharpe > 1.5 and fee_results[10]["sharpe"] > 0.8:
        viability = "PAPER_STRONG"
    elif gross_sharpe > 1.0 and fee_results[10]["sharpe"] > 0.3:
        viability = "PAPER_PROMISING"
    elif gross_sharpe > 0.5:
        viability = "PAPER_MIXED"
    elif gross_sharpe > 0:
        viability = "PAPER_WEAK"
    else:
        viability = "PAPER_REVIEW_REQUIRED"

    if cost_class == "COST_COLLAPSED":
        note_zh = "毛收益尚可但费用敏感，10bps下收益崩溃"
        note_en = "Gross returns acceptable but cost-sensitive; collapses at 10bps"
    elif viability == "PAPER_STRONG":
        note_zh = "毛收益和费用调整后收益均表现良好"
        note_en = "Strong gross and fee-adjusted returns"
    elif viability == "PAPER_WEAK":
        note_zh = "毛收益较弱，需进一步研究"
        note_en = "Weak gross returns, needs further research"
    else:
        note_zh = "中等表现，需结合其他指标评估"
        note_en = "Moderate performance, evaluate with other metrics"

    # Monthly turnover records
    turnover_records = []
    for m in range(n_months):
        mask = month_inverse == m
        t = turnover[mask]
        turnover_records.append({
            "month": month_ids[m],
            "avg_turnover": float(t.mean()),
            "median_turnover": float(np.median(t)),
            "max_turnover": float(t.max()),
            "n_observations": int(mask.sum()),
        })

    # Monthly leg decomposition per fee — compound hourly returns within month
    leg_records = []
    for fee_bps in fee_bps_list:
        net_ret_hourly = ls_returns - turnover * fee_bps / 10000
        for m in range(n_months):
            mask = month_inverse == m
            long_m = float(np.prod(1 + long_returns[mask]) - 1)
            short_m = float(np.prod(1 + short_returns[mask]) - 1)
            ls_m = float(np.prod(1 + ls_returns[mask]) - 1)
            net_m = float(np.prod(1 + net_ret_hourly[mask]) - 1)
            leg_records.append({
                "month": month_ids[m],
                "fee_bps": fee_bps,
                "long_leg_return": long_m,
                "short_leg_return": short_m,
                "long_short_return": ls_m,
                "gross_long_short_return": ls_m,
                "net_long_short_return": net_m,
            })

    # Monthly drawdown curve per fee
    drawdown_records = []
    for fee_bps in fee_bps_list:
        net_ret_hourly = ls_returns - turnover * fee_bps / 10000
        nav = 1.0
        peak = 1.0
        for m in range(n_months):
            mask = month_inverse == m
            monthly_net = float(np.prod(1 + net_ret_hourly[mask]) - 1)
            nav *= (1 + monthly_net)
            peak = max(peak, nav)
            dd = (peak - nav) / peak if peak > 0 else 0.0
            drawdown_records.append({
                "month": month_ids[m],
                "fee_bps": fee_bps,
                "nav": nav,
                "drawdown": dd,
                "monthly_return": monthly_net,
            })

    return {
        "n_timestamps": n_ts,
        "avg_long_count": int(n_longs.mean()),
        "avg_short_count": int(n_shorts.mean()),
        "gross_total_return": gross_total,
        "gross_annualized_return": float(gross_ann_ret),
        "gross_annualized_vol": gross_vol,
        "gross_sharpe": gross_sharpe,
        "max_drawdown": max_dd,
        "positive_month_rate": positive_month_rate,
        "avg_turnover": avg_turnover,
        "median_turnover": median_turnover,
        "fee_0bps_total_return": fee_results[0]["total_return"],
        "fee_2bps_total_return": fee_results[2]["total_return"],
        "fee_5bps_total_return": fee_results[5]["total_return"],
        "fee_10bps_total_return": fee_results[10]["total_return"],
        "fee_20bps_total_return": fee_results[20]["total_return"],
        "break_even_fee_bps": break_even,
        "cost_sensitivity_class": cost_class,
        "paper_viability_class": viability,
        "main_diagnostic_note_zh": note_zh,
        "main_diagnostic_note_en": note_en,
        "nav_curves": nav_curves,
        "monthly_records": monthly_records,
        "fee_results": fee_results,
        "turnover_records": turnover_records,
        "leg_records": leg_records,
        "drawdown_records": drawdown_records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="PM-21: Single-factor paper portfolio diagnostics")
    parser.add_argument("--horizon", default="1h")
    parser.add_argument("--top-frac", type=float, default=0.20)
    parser.add_argument("--bottom-frac", type=float, default=0.20)
    parser.add_argument("--fee-bps-list", default="0,2,5,10,20")
    parser.add_argument("--max-factors", type=int, default=0)
    parser.add_argument("--factor-ids", default="")
    parser.add_argument("--output-dir", default=str(DIAG_DIR))
    args = parser.parse_args()

    fee_bps_list = [int(x) for x in args.fee_bps_list.split(",")]

    if args.factor_ids:
        factor_ids = [x.strip() for x in args.factor_ids.split(",") if x.strip()]
        try:
            raise_for_skipped_public_factor_ids(
                factor_ids,
                action="single-factor paper diagnosed",
            )
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 1
    else:
        factor_ids = load_registered_factors()

    if args.max_factors > 0:
        factor_ids = factor_ids[:args.max_factors]

    print(f"[PM-21] Loading labels...")
    t0 = time.time()
    labels = load_labels()
    print(f"[PM-21] Labels: {len(labels)} rows in {time.time()-t0:.1f}s")

    directions = load_factor_directions()
    scorecard_classes = load_scorecard_classes()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[PM-21] Processing {len(factor_ids)} factors, horizon={args.horizon}, fees={fee_bps_list}")

    summary_rows = []
    nav_curves_all = []
    monthly_all = []
    fee_sensitivity_all = []
    turnover_all = []
    leg_all = []
    drawdown_all = []
    processed = 0
    errors = 0

    t0 = time.time()
    for i, fid in enumerate(factor_ids):
        fv = load_factor_values(fid)
        if fv.empty:
            errors += 1
            continue

        direction = directions.get(fid, "positive")
        if direction == "negative":
            fv["factor_value"] = -fv["factor_value"]

        merged = fv.merge(labels, on=["timestamp", "symbol"], how="inner")
        if merged.empty:
            errors += 1
            continue

        result = compute_diagnostics(merged, args.top_frac, args.bottom_frac, fee_bps_list)

        if "error" in result:
            errors += 1
            continue

        sc = scorecard_classes.get(fid, {})
        summary_rows.append({
            "factor_id": fid,
            "family": fid.rsplit("_", 1)[0] if "_" in fid else fid,
            "final_quality_class": sc.get("quality_class", ""),
            "score_confidence": sc.get("score_confidence", ""),
            "horizon": args.horizon,
            **{k: v for k, v in result.items() if k not in ["nav_curves", "monthly_records", "fee_results"]},
        })

        for fee_bps, nav_df in result["nav_curves"].items():
            nav_df["factor_id"] = fid
            nav_curves_all.append(nav_df)

        for rec in result["monthly_records"]:
            monthly_all.append({"factor_id": fid, **rec})

        for fee_bps, stats in result["fee_results"].items():
            fee_sensitivity_all.append({
                "factor_id": fid, "fee_bps": fee_bps, **stats,
                "max_drawdown": result["max_drawdown"],
                "positive_month_rate": result["positive_month_rate"],
                "avg_turnover": result["avg_turnover"],
            })

        for rec in result["turnover_records"]:
            turnover_all.append({"factor_id": fid, **rec})

        for rec in result["leg_records"]:
            leg_all.append({"factor_id": fid, **rec})

        for rec in result["drawdown_records"]:
            drawdown_all.append({"factor_id": fid, **rec})

        processed += 1
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(factor_ids)}] {processed} processed, {time.time()-t0:.1f}s")

    elapsed = time.time() - t0
    print(f"[PM-21] Done: {processed} factors in {elapsed:.1f}s, {errors} errors")

    # Write outputs
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_dir / "single_factor_paper_summary.csv", index=False)
    summary_df.to_json(output_dir / "single_factor_paper_summary.json", orient="records", indent=2)

    if nav_curves_all:
        nav_df = pd.concat(nav_curves_all, ignore_index=True)
        nav_df.to_csv(output_dir / "single_factor_paper_nav_curves.csv", index=False)
    else:
        nav_df = pd.DataFrame()

    monthly_df = pd.DataFrame(monthly_all)
    monthly_df.to_csv(output_dir / "single_factor_paper_monthly_returns.csv", index=False)

    fee_df = pd.DataFrame(fee_sensitivity_all)
    fee_df.to_csv(output_dir / "single_factor_fee_sensitivity.csv", index=False)

    turnover_df = pd.DataFrame(turnover_all)
    turnover_df.to_csv(output_dir / "single_factor_paper_turnover.csv", index=False)

    leg_df = pd.DataFrame(leg_all)
    leg_df.to_csv(output_dir / "single_factor_paper_leg_decomposition.csv", index=False)

    drawdown_df = pd.DataFrame(drawdown_all)
    drawdown_df.to_csv(output_dir / "single_factor_paper_drawdown_curve.csv", index=False)

    manifest = {
        "pm": "PM-21B",
        "description": "Reproducible single-factor paper portfolio diagnostics",
        "horizon": args.horizon,
        "top_frac": args.top_frac,
        "bottom_frac": args.bottom_frac,
        "fee_bps_list": fee_bps_list,
        "factors_processed": processed,
        "factors_with_errors": errors,
        "total_nav_rows": len(nav_df),
        "total_monthly_rows": len(monthly_all),
        "total_fee_rows": len(fee_sensitivity_all),
        "runtime_seconds": round(elapsed, 1),
        "outputs": [
            "single_factor_paper_summary.csv",
            "single_factor_paper_summary.json",
            "single_factor_paper_monthly_returns.csv",
            "single_factor_fee_sensitivity.csv",
            "single_factor_paper_turnover.csv",
            "single_factor_paper_leg_decomposition.csv",
            "single_factor_paper_drawdown_curve.csv",
            "single_factor_paper_manifest.json",
        ],
        "warnings": [
            "Research diagnostics only. NOT a backtest. NOT a trading strategy.",
            "1h horizon avoids overlapping returns but limits holding period.",
            "No order book / slippage modeling.",
            "Equal-weight long/short legs, not market-cap weighted.",
        ],
    }
    (output_dir / "single_factor_paper_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n[PM-21B] Outputs: summary={len(summary_rows)}, monthly={len(monthly_all)}, fee={len(fee_sensitivity_all)}, turnover={len(turnover_all)}, leg={len(leg_all)}, drawdown={len(drawdown_all)}")

    if not summary_df.empty:
        print(f"\nViability:\n{summary_df['paper_viability_class'].value_counts().to_string()}")
        print(f"\nCost sensitivity:\n{summary_df['cost_sensitivity_class'].value_counts().to_string()}")
        print(f"\nTop 10 by gross Sharpe:")
        for _, r in summary_df.nlargest(10, "gross_sharpe").iterrows():
            print(f"  {r['factor_id']:30s} gross_sharpe={r['gross_sharpe']:.3f} 10bps_ret={r['fee_10bps_total_return']:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
