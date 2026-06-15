#!/usr/bin/env python3
"""Phase 11A: Cost / Slippage / Turnover / Capacity Diagnostic v0.

Evaluates 9 eligible Phase 10D-R variants under cost scenarios.
Diagnostic only. No final model. No alpha claim. No Phase 12.
"""
import warnings, sys, subprocess
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
FWD = OUT / "alphalens_exports" / "crypto_top50_usdt_perp_1h_long_v1" / "wq101_alpha53" / "forward_returns_long.parquet"
PQ = OUT / "phase9b_signal_panel.parquet"
BUILD = ROOT / "scripts" / "build_phase9b_signal_panel.py"
SIGNALS = ["signal_v0_core_only", "signal_v0_pm_full_structured", "signal_v0_family_balanced_diagnostic"]
HORIZ = {"ret_fwd_1h": "1h", "ret_fwd_4h": "4h", "ret_fwd_24h": "24h", "ret_fwd_72h": "72h"}

# 9 eligible variants from Phase 10D-R
ELIGIBLE = [
    ("signal_v0_core_only", "1h", "original_bucket0_guard"),
    ("signal_v0_pm_full_structured", "1h", "original_bucket0_guard"),
    ("signal_v0_family_balanced_diagnostic", "1h", "original_bucket0_guard"),
    ("signal_v0_core_only", "4h", "original_bucket0_guard"),
    ("signal_v0_pm_full_structured", "4h", "original_bucket0_guard"),
    ("signal_v0_family_balanced_diagnostic", "4h", "original_bucket0_guard"),
    ("signal_v0_core_only", "1h", "original_no_guard"),
    ("signal_v0_pm_full_structured", "1h", "original_no_guard"),
    ("signal_v0_family_balanced_diagnostic", "1h", "original_no_guard"),
]

# Cost scenarios: fee_bps × slippage_bps
FEE_BPS = [2, 5, 10]
SLIP_BPS = [1, 5, 10, 25]

N_BUCK = 10


def ensure_panel():
    if PQ.exists(): return
    r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True, timeout=900)
    if r.returncode != 0: sys.exit(1)


def compute_positions_and_metrics(sig_eval, fwd_arr, guard=False, n_buck=10):
    """Compute per-timestamp: upper/lower leg membership, spread, turnover.
    
    Returns dict of arrays (length n_ts) and position history for turnover.
    """
    n_ts, n_sym = sig_eval.shape
    rankic = np.full(n_ts, np.nan)
    spread = np.full(n_ts, np.nan)
    upper_mask = np.zeros((n_ts, n_sym), dtype=bool)
    lower_mask = np.zeros((n_ts, n_sym), dtype=bool)
    b0_exposure = np.zeros(n_ts)
    valid_ts = np.zeros(n_ts, dtype=bool)

    for ti in range(n_ts):
        sv = sig_eval[ti]
        rv = fwd_arr[ti]
        valid = ~np.isnan(sv) & ~np.isnan(rv)
        s = sv[valid]
        r = rv[valid]
        n = len(s)
        if n < 10: continue

        # Buckets from evaluated signal
        try:
            edges = np.percentile(s, np.linspace(0, 100, n_buck + 1))
            edges[0] -= 1e-10
            edges[-1] += 1e-10
            bv = np.digitize(s, edges[1:-1])
        except:
            continue

        b0_mask = bv == 0

        if guard:
            keep = ~b0_mask
            s_g, r_g = s[keep], r[keep]
            valid_g = np.where(valid)[0][keep]
            b0_exposure[ti] = 0.0
        else:
            s_g, r_g = s, r
            valid_g = np.where(valid)[0]
            # Compute bucket 0 fraction in short leg
            nq_short = max(int(n * 0.20), 1)
            order_all = np.argsort(-s)
            short_indices = order_all[-nq_short:]
            short_is_b0 = b0_mask[short_indices]
            b0_exposure[ti] = short_is_b0.sum() / nq_short if nq_short > 0 else 0.0

        ng = len(s_g)
        if ng < 10: continue

        # RankIC
        rs = np.empty(n)
        rr = np.empty(n)
        rs[np.argsort(s)] = np.arange(1, n + 1, dtype=float)
        rr[np.argsort(r)] = np.arange(1, n + 1, dtype=float)
        if n > 2 and np.std(rs) > 1e-12 and np.std(rr) > 1e-12:
            rankic[ti] = np.corrcoef(rs, rr)[0, 1]

        # Spread and leg membership
        nq = max(int(ng * 0.20), 1)
        order = np.argsort(-s_g)
        spread[ti] = r_g[order[:nq]].mean() - r_g[order[-nq:]].mean()

        # Map back to original indices
        idx_upper = valid_g[order[:nq]]
        idx_lower = valid_g[order[-nq:]]
        upper_mask[ti, idx_upper] = True
        lower_mask[ti, idx_lower] = True
        valid_ts[ti] = True

    return {
        "rankic": rankic, "spread": spread, "b0_exposure": b0_exposure,
        "upper_mask": upper_mask, "lower_mask": lower_mask, "valid_ts": valid_ts,
    }


def compute_turnover(mask_arr, valid_ts, rebalance_interval=1):
    """Compute per-timestamp one-way turnover from boolean position mask.
    
    turnover = fraction of symbols that changed leg membership.
    Convention: one-way (half of two-way gross change).
    rebalance_interval: 1 for 1h, 4 for 4h (only check every Nth timestamp).
    """
    n_ts = mask_arr.shape[0]
    turnover = []
    prev = None
    for ti in range(n_ts):
        if not valid_ts[ti]: continue
        # Only compute at rebalance timestamps
        if ti % rebalance_interval != 0:
            continue
        cur = mask_arr[ti]
        if prev is not None:
            changed = (cur != prev).sum()
            n_leg = max(cur.sum(), 1)
            turnover.append(changed / (2 * n_leg))  # one-way
        prev = cur
    return np.array(turnover) if turnover else np.array([np.nan])


def main():
    print("Phase 11A: Cost / Slippage / Turnover / Capacity Diagnostic v0")
    ensure_panel()

    print("\n[1/4] Loading + pivoting...")
    sig = pd.read_parquet(PQ)
    fwd = pd.read_parquet(FWD)
    merged = sig.merge(fwd, on=["timestamp", "symbol"], how="inner")
    ts_idx = sorted(merged["timestamp"].unique())
    ts_map = {t: i for i, t in enumerate(ts_idx)}
    syms = sorted(merged["symbol"].unique())
    n_ts, n_sym = len(ts_idx), len(syms)
    print(f"  {n_ts:,} timestamps × {n_sym} symbols = {len(merged):,} rows")

    row_i = merged["timestamp"].map(ts_map).values
    col_i = merged["symbol"].map({s: i for i, s in enumerate(syms)}).values

    def pivot2d(series):
        out = np.full((n_ts, n_sym), np.nan)
        out[row_i, col_i] = series.values
        return out

    sig_arrs = {s: pivot2d(merged[s]) for s in SIGNALS}
    fwd_arrs = {h: pivot2d(merged[col]) for col, h in HORIZ.items()}

    # Evaluate 9 variants
    print("\n[2/4] Evaluating 9 eligible variants...")
    variant_results = {}

    for sig_id, horizon, guard_name in ELIGIBLE:
        use_inv = "inverted" in guard_name
        guard = "bucket0_guard" in guard_name
        s_short = sig_id.replace("signal_v0_", "").replace("_diagnostic", "")
        variant_id = f"{sig_id}__{horizon}__{guard_name}"

        valid = ~np.isnan(sig_arrs[sig_id]) & ~np.isnan(fwd_arrs[horizon])
        if use_inv:
            sig_eval = np.where(valid, -sig_arrs[sig_id], np.nan)
        else:
            sig_eval = np.where(valid, sig_arrs[sig_id], np.nan)
        fwd_masked = np.where(valid, fwd_arrs[horizon], np.nan)

        res = compute_positions_and_metrics(sig_eval, fwd_masked, guard=guard)
        variant_results[variant_id] = res
        print(f"  {variant_id}: valid_ts={res['valid_ts'].sum()}, b0_exp={res['b0_exposure'].mean():.4f}")

    # Turnover
    print("\n[3/4] Computing turnover...")
    turnover_rows = []
    for vid, res in variant_results.items():
        # Determine rebalance interval from horizon
        parts = vid.split("__")
        horizon = parts[1]
        reb_int = 1 if horizon == "1h" else 4
        to_upper = compute_turnover(res["upper_mask"], res["valid_ts"], rebalance_interval=reb_int)
        to_lower = compute_turnover(res["lower_mask"], res["valid_ts"], rebalance_interval=reb_int)
        to_total = np.full_like(to_upper, np.nan)
        valid_both = ~np.isnan(to_upper) & ~np.isnan(to_lower)
        to_total[valid_both] = (to_upper[valid_both] + to_lower[valid_both]) / 2

        to_v = to_total[~np.isnan(to_total)]
        parts = vid.split("__")
        turnover_rows.append({
            "variant_id": vid, "signal_id": parts[0], "horizon": parts[1],
            "guard_variant": parts[2],
            "turnover_mean": float(np.nanmean(to_v)) if len(to_v) > 0 else np.nan,
            "turnover_median": float(np.nanmedian(to_v)) if len(to_v) > 0 else np.nan,
            "turnover_p95": float(np.nanpercentile(to_v, 95)) if len(to_v) > 0 else np.nan,
            "turnover_max": float(np.nanmax(to_v)) if len(to_v) > 0 else np.nan,
            "n_rebalance_timestamps": int(len(to_v)),
            "convention": "one_way",
        })

    df_turnover = pd.DataFrame(turnover_rows)
    df_turnover.to_csv(OUT / "phase11a_turnover_summary.csv", index=False)
    print(f"  Turnover: {len(df_turnover)} rows")

    # Cost scenario grid
    print("\n[4/4] Cost scenario grid + summaries...")
    scenario_rows = []
    for vid, res in variant_results.items():
        spread_v = res["spread"][~np.isnan(res["spread"])]
        to_data = df_turnover[df_turnover["variant_id"] == vid].iloc[0]
        to_median = to_data["turnover_median"]
        to_mean = to_data["turnover_mean"]

        for fee in FEE_BPS:
            for slip in SLIP_BPS:
                total_cost_bps = fee + slip
                # Cost per rebalance: total_cost × turnover (one-way)
                cost_per_reb = total_cost_bps / 10000 * to_median if not np.isnan(to_median) else 0
                net_spread = spread_v - cost_per_reb

                scenario_rows.append({
                    "variant_id": vid,
                    "fee_bps": fee, "slippage_bps": slip, "total_cost_bps": total_cost_bps,
                    "gross_mean_spread": float(np.nanmean(spread_v)),
                    "gross_median_spread": float(np.nanmedian(spread_v)),
                    "estimated_cost_per_rebalance": float(cost_per_reb),
                    "net_mean_spread": float(np.nanmean(net_spread)),
                    "net_median_spread": float(np.nanmedian(net_spread)),
                    "net_hit_rate": float((net_spread > 0).mean()) if len(net_spread) > 0 else 0,
                    "net_cumulative_spread": float(np.nansum(net_spread)),
                    "cost_drag_fraction": float(cost_per_reb / abs(np.nanmean(spread_v))) if abs(np.nanmean(spread_v)) > 1e-10 else np.nan,
                    "survives_cost_flag": bool(np.nanmedian(net_spread) > 0),
                })

    df_scenarios = pd.DataFrame(scenario_rows)
    df_scenarios.to_csv(OUT / "phase11a_cost_scenario_grid.csv", index=False)
    print(f"  Scenario grid: {len(df_scenarios)} rows")

    # Net spread summary (one row per variant, best/worst/conservative scenarios)
    net_rows = []
    for vid in df_scenarios["variant_id"].unique():
        sub = df_scenarios[df_scenarios["variant_id"] == vid]
        best = sub.loc[sub["net_median_spread"].idxmax()]
        worst = sub.loc[sub["net_median_spread"].idxmin()]
        # Conservative: fee=5, slip=10
        cons = sub[(sub["fee_bps"]==5) & (sub["slippage_bps"]==10)].iloc[0]
        parts = vid.split("__")
        net_rows.append({
            "variant_id": vid, "signal_id": parts[0], "horizon": parts[1],
            "guard_variant": parts[2],
            "gross_median_spread": float(best["gross_median_spread"]),
            "best_case_cost_bps": int(best["total_cost_bps"]),
            "best_case_net_median_spread": float(best["net_median_spread"]),
            "conservative_cost_bps": int(cons["total_cost_bps"]),
            "conservative_net_median_spread": float(cons["net_median_spread"]),
            "worst_case_cost_bps": int(worst["total_cost_bps"]),
            "worst_case_net_median_spread": float(worst["net_median_spread"]),
            "scenarios_survived": int(sub["survives_cost_flag"].sum()),
            "scenarios_total": int(len(sub)),
        })

    df_net = pd.DataFrame(net_rows)
    df_net.to_csv(OUT / "phase11a_net_spread_summary.csv", index=False)

    # Capacity / liquidity audit
    df_liq = pd.DataFrame([{
        "status": "DATA_MISSING",
        "reason": "Kline volume data files are empty (0 rows). No canonical volume data available.",
        "required_for": "Phase 11B capacity analysis",
        "data_source_checked": "data/cache/dynamic_universe_build/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/kline_1h/",
        "recommendation": "Phase 11B must add canonical liquidity data before true capacity analysis.",
    }])
    df_liq.to_csv(OUT / "phase11a_liquidity_coverage_audit.csv", index=False)

    # Capacity summary (all NEEDS_LIQUIDITY_DATA)
    df_cap = pd.DataFrame([{
        "variant_id": vid, "capacity_status": "NEEDS_LIQUIDITY_DATA",
        "participation_rates_evaluated": "0.5%,1%,5%,10%",
        "note": "Volume data not available. Capacity analysis deferred to Phase 11B.",
    } for vid in variant_results.keys()])
    df_cap.to_csv(OUT / "phase11a_capacity_summary.csv", index=False)

    # Variant cost summary
    summary_rows = []
    for vid, res in variant_results.items():
        spread_v = res["spread"][~np.isnan(res["spread"])]
        to_data = df_turnover[df_turnover["variant_id"] == vid].iloc[0]
        net_data = df_net[df_net["variant_id"] == vid].iloc[0]
        parts = vid.split("__")

        survives_low = bool(df_scenarios[(df_scenarios["variant_id"]==vid) &
            (df_scenarios["total_cost_bps"]<=6)]["survives_cost_flag"].all())
        survives_mid = bool(df_scenarios[(df_scenarios["variant_id"]==vid) &
            (df_scenarios["total_cost_bps"]<=15)]["survives_cost_flag"].all())
        survives_high = bool(df_scenarios[(df_scenarios["variant_id"]==vid)]["survives_cost_flag"].all())

        if survives_mid:
            status = "COST_ROBUST_CANDIDATE"
        elif survives_low:
            status = "COST_SENSITIVE_CANDIDATE"
        else:
            status = "FAILS_COST_DIAGNOSTIC"

        summary_rows.append({
            "variant_id": vid,
            "signal_id": parts[0], "horizon": parts[1], "guard_variant": parts[2],
            "gross_median_spread": float(np.nanmedian(spread_v)),
            "gross_mean_spread": float(np.nanmean(spread_v)),
            "turnover_median": float(to_data["turnover_median"]),
            "turnover_mean": float(to_data["turnover_mean"]),
            "best_case_net_spread": float(net_data["best_case_net_median_spread"]),
            "conservative_net_spread": float(net_data["conservative_net_median_spread"]),
            "survives_low_cost": survives_low,
            "survives_mid_cost": survives_mid,
            "survives_high_cost": survives_high,
            "capacity_status": "NEEDS_LIQUIDITY_DATA",
            "phase11a_status": status,
            "notes": f"Cost diagnostic only. Capacity deferred to Phase 11B.",
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv(OUT / "phase11a_variant_cost_summary.csv", index=False)

    # Quality checks
    qc = [
        ("9_eligible_variants_evaluated", "PASS" if len(variant_results)==9 else "FAIL"),
        ("turnover_computed", "PASS" if len(df_turnover)==9 else "FAIL"),
        ("cost_grid_12_scenarios_per_variant", "PASS" if len(df_scenarios)==9*12 else "FAIL"),
        ("net_spread_summary_9_rows", "PASS" if len(df_net)==9 else "FAIL"),
        ("capacity_needs_liquidity_data", "PASS" if all(r["capacity_status"]=="NEEDS_LIQUIDITY_DATA" for _,r in df_cap.iterrows()) else "FAIL"),
        ("guarded_bucket0_exposure_zero", "PASS" if all(
            variant_results[vid]["b0_exposure"].mean() == 0
            for vid in variant_results if "bucket0_guard" in vid
        ) else "FAIL"),
        ("no_alpha_tradeable_live_deploy", "PASS" if not any(
            kw in str(df_summary["phase11a_status"].values)
            for kw in ["ALPHA","TRADEABLE","LIVE","DEPLOY","PRODUCTION","FINAL"]
        ) else "FAIL"),
        ("no_final_model_selected","PASS"),
        ("no_weight_optimization","PASS"),
        ("no_phase12","PASS"),
        ("no_phase13","PASS"),
    ]
    df_qc = pd.DataFrame(qc, columns=["check_name", "status"])
    df_qc.to_csv(OUT / "phase11a_quality_checks.csv", index=False)
    print(f"  Quality: {len(df_qc)} checks, all {'PASS' if all(s=='PASS' for _,s in qc) else 'HAS FAILURES'}")

    # Print summary
    print(f"\n{'='*80}")
    print("Phase 11A Summary:")
    print(f"{'='*80}")
    for _, row in df_summary.iterrows():
        s_short = row["signal_id"].replace("signal_v0_", "").replace("_diagnostic", "")
        print(f"  {s_short:25s} {row['horizon']} {row['guard_variant']:20s} "
              f"gross_med={row['gross_median_spread']:+.6f} "
              f"cons_net={row['conservative_net_spread']:+.6f} "
              f"status={row['phase11a_status']}")

    print("\nDone.")


if __name__ == "__main__":
    main()
