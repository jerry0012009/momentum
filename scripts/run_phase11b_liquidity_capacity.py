#!/usr/bin/env python3
"""Phase 11B: Canonical Liquidity Data & Capacity Analysis.

Builds liquidity panel from kline data, evaluates capacity for 4 variants.
Diagnostic only. No final model. No Phase 12.
"""
import warnings, sys, subprocess, glob
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "research" / "factor_runs" / "crypto_top50_factor_library"
FWD = ROOT / "data" / "features" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / "labels.parquet"
PQ = OUT / "phase9b_signal_panel.parquet"
KLINE_DIR = ROOT / "data" / "cache" / "dynamic_universe_build" / "crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1" / "kline_1h"
BUILD = ROOT / "scripts" / "build_phase9b_signal_panel.py"
SIGNALS = ["signal_v0_core_only", "signal_v0_pm_full_structured", "signal_v0_family_balanced_diagnostic"]

# 4 variants to evaluate
VARIANTS = [
    ("signal_v0_core_only", "1h", "original_no_guard"),
    ("signal_v0_core_only", "1h", "original_bucket0_guard"),
    ("signal_v0_pm_full_structured", "1h", "original_no_guard"),
    ("signal_v0_family_balanced_diagnostic", "1h", "original_no_guard"),
]

PARTICIPATION_RATES = [0.001, 0.005, 0.01, 0.02, 0.05]
NOTIONAL_ASSUMPTIONS = [1000, 5000, 10000, 50000, 100000]
N_BUCK = 10
FEE_BPS = [2, 5, 10]
SLIP_BPS = [1, 5, 10, 25]


def ensure_panel():
    if PQ.exists(): return
    r = subprocess.run([sys.executable, str(BUILD)], capture_output=True, text=True, timeout=900)
    if r.returncode != 0: sys.exit(1)


def build_liquidity_panel(panel_syms):
    """Build canonical 1h liquidity panel from kline files."""
    print("  Scanning kline files...")
    kline_files = sorted(glob.glob(str(KLINE_DIR / "*-1h-*.parquet")))
    # Extract unique symbol-month combos
    sym_months = {}
    for f in kline_files:
        fname = Path(f).name
        parts = fname.rsplit("-1h-", 1)
        if len(parts) == 2:
            sym, month_ext = parts[0], parts[1].replace(".parquet", "")
            if sym in panel_syms:
                sym_months.setdefault(sym, []).append(f)

    print(f"  Found kline files for {len(sym_months)}/{len(panel_syms)} panel symbols")
    dfs = []
    for sym, files in sym_months.items():
        for f in files:
            try:
                df = pd.read_parquet(f)
                if len(df) > 0 and "volume" in df.columns:
                    df["symbol"] = sym
                    dfs.append(df)
            except:
                pass

    if not dfs:
        return None, []

    panel = pd.concat(dfs, ignore_index=True)
    # Normalize timestamp
    if "timestamp" in panel.columns:
        panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    elif "bar_close_time" in panel.columns:
        panel["timestamp"] = pd.to_datetime(panel["bar_close_time"], utc=True)

    # Keep relevant columns
    cols = ["timestamp", "symbol"]
    for c in ["close", "volume", "quote_volume", "taker_base", "taker_quote", "trade_count"]:
        if c in panel.columns:
            cols.append(c)
    panel = panel[cols].copy()

    # Compute notional volume (quote_volume or volume * close)
    if "quote_volume" in panel.columns:
        panel["notional_volume"] = panel["quote_volume"].astype(float)
    elif "volume" in panel.columns and "close" in panel.columns:
        panel["notional_volume"] = panel["volume"].astype(float) * panel["close"].astype(float)
    else:
        panel["notional_volume"] = np.nan

    panel = panel.dropna(subset=["timestamp", "symbol", "notional_volume"])
    panel = panel.drop_duplicates(subset=["timestamp", "symbol"])
    panel = panel.sort_values(["timestamp", "symbol"]).reset_index(drop=True)

    covered_syms = set(panel["symbol"].unique())
    missing_syms = panel_syms - covered_syms
    return panel, sorted(missing_syms)


def data_quality(panel, sig_syms, fwd_ts_range):
    """Compute data quality metrics."""
    rows = []
    ts_range = (panel["timestamp"].min(), panel["timestamp"].max())
    ts_overlap = ts_range[0] <= fwd_ts_range[1] and ts_range[1] >= fwd_ts_range[0]
    sym_overlap = len(set(panel["symbol"].unique()) & sig_syms)

    rows.append(("nonzero_row_count", len(panel), len(panel) > 0))
    rows.append(("timestamp_range_start", str(ts_range[0]), True))
    rows.append(("timestamp_range_end", str(ts_range[1]), True))
    rows.append(("timestamp_overlap_with_signal_panel", ts_overlap, ts_overlap))
    rows.append(("symbol_overlap_count", sym_overlap, sym_overlap >= 30))
    rows.append(("symbol_overlap_fraction", sym_overlap / len(sig_syms), sym_overlap / len(sig_syms) >= 0.7))

    for col in ["volume", "quote_volume", "notional_volume"]:
        if col in panel.columns:
            miss_rate = panel[col].isna().mean()
            zero_rate = (panel[col] == 0).mean()
            rows.append((f"{col}_missing_rate", float(miss_rate), miss_rate < 0.1))
            rows.append((f"{col}_zero_rate", float(zero_rate), zero_rate < 0.1))

    dup_count = panel.duplicated(subset=["timestamp", "symbol"]).sum()
    rows.append(("duplicate_timestamp_symbol", int(dup_count), dup_count == 0))

    if "notional_volume" in panel.columns:
        nv = panel["notional_volume"].dropna()
        rows.append(("notional_volume_median", float(nv.median()), True))
        rows.append(("notional_volume_p5", float(nv.quantile(0.05)), True))
        rows.append(("notional_volume_p95", float(nv.quantile(0.95)), True))
        # Extreme sanity: max should be < 1000x median
        rows.append(("notional_volume_max_median_ratio", float(nv.max() / nv.median()) if nv.median() > 0 else 0, nv.max() / nv.median() < 1000 if nv.median() > 0 else False))

    return pd.DataFrame(rows, columns=["metric", "value", "pass"])


def compute_variant_capacity(sig_eval, fwd_arr, vol_arr, ts_valid, guard=False):
    """Compute capacity for a variant at each timestamp.
    
    Returns: per-timestamp capacity dict (per participation rate × notional).
    """
    n_ts, n_sym = sig_eval.shape
    results = []

    for ti in range(n_ts):
        if not ts_valid[ti]: continue
        sv = sig_eval[ti]
        valid = ~np.isnan(sv)
        s = sv[valid]
        n = len(s)
        if n < 10: continue

        # Buckets
        try:
            edges = np.percentile(s, np.linspace(0, 100, N_BUCK + 1))
            edges[0] -= 1e-10
            edges[-1] += 1e-10
            bv = np.digitize(s, edges[1:-1])
        except:
            continue

        if guard:
            keep = bv != 0
            s_g = s[keep]
            valid_idx = np.where(valid)[0][keep]
        else:
            s_g = s
            valid_idx = np.where(valid)[0]

        ng = len(s_g)
        if ng < 10: continue
        nq = max(int(ng * 0.20), 1)
        order = np.argsort(-s_g)
        upper_idx = valid_idx[order[:nq]]
        lower_idx = valid_idx[order[-nq:]]

        # Get volume for each leg
        upper_vol = vol_arr[ti, upper_idx]
        lower_vol = vol_arr[ti, lower_idx]

        # Skip if all volume is NaN
        if np.all(np.isnan(upper_vol)) or np.all(np.isnan(lower_vol)):
            continue

        # Compute spread for this timestamp
        rv = fwd_arr[ti]
        upper_ret = np.nanmean(rv[upper_idx])
        lower_ret = np.nanmean(rv[lower_idx])
        spread = upper_ret - lower_ret

        for pr in PARTICIPATION_RATES:
            # Capacity per leg = volume * participation_rate / 2 (split between legs)
            upper_cap = np.nansum(upper_vol) * pr
            lower_cap = np.nansum(lower_vol) * pr
            ts_cap = min(upper_cap, lower_cap)

            # Bottleneck symbol (lowest capacity in either leg)
            upper_bottleneck_idx = upper_idx[np.nanargmin(upper_vol)] if len(upper_vol) > 0 else -1
            lower_bottleneck_idx = lower_idx[np.nanargmin(lower_vol)] if len(lower_vol) > 0 else -1

            results.append({
                "timestamp_idx": ti,
                "participation_rate": pr,
                "upper_leg_volume": float(np.nansum(upper_vol)),
                "lower_leg_volume": float(np.nansum(lower_vol)),
                "capacity_usd": float(ts_cap),
                "spread": float(spread),
                "upper_bottleneck_symbol_idx": int(upper_bottleneck_idx),
                "lower_bottleneck_symbol_idx": int(lower_bottleneck_idx),
            })

    return pd.DataFrame(results) if results else pd.DataFrame()


def main():
    print("Phase 11B: Canonical Liquidity Data & Capacity Analysis")
    ensure_panel()

    print("\n[1/5] Loading signal panel + forward returns...")
    sig = pd.read_parquet(PQ)
    fwd = pd.read_parquet(FWD)
    merged = sig.merge(fwd, on=["timestamp", "symbol"], how="inner")
    ts_idx = sorted(merged["timestamp"].unique())
    ts_map = {t: i for i, t in enumerate(ts_idx)}
    syms = sorted(merged["symbol"].unique())
    n_ts, n_sym = len(ts_idx), len(syms)
    print(f"  {n_ts:,} timestamps × {n_sym} symbols = {len(merged):,} rows")

    # Part A: Build liquidity panel
    print("\n[2/5] Building liquidity panel from kline data...")
    panel_syms = set(syms)
    liq_panel, missing_syms = build_liquidity_panel(panel_syms)

    if liq_panel is None or len(liq_panel) == 0:
        print("  ERROR: No liquidity data could be built. Blocking Phase 12.")
        # Save DATA_MISSING inventory
        pd.DataFrame([{"status": "DATA_MISSING", "reason": "No kline data with volume found for any panel symbol"}]).to_csv(OUT / "phase11b_liquidity_data_inventory.csv", index=False)
        pd.DataFrame([{"check": "liquidity_data", "status": "FAIL", "detail": "No data"}]).to_csv(OUT / "phase11b_quality_checks.csv", index=False)
        sys.exit(1)

    # Inventory
    inv_rows = []
    for s in sorted(panel_syms):
        has_data = s not in missing_syms
        inv_rows.append({"symbol": s, "has_liquidity_data": has_data, "status": "AVAILABLE" if has_data else "MISSING"})
    df_inv = pd.DataFrame(inv_rows)
    df_inv.to_csv(OUT / "phase11b_liquidity_data_inventory.csv", index=False)
    print(f"  Inventory: {len(panel_syms)} symbols, {len(panel_syms)-len(missing_syms)} with data, {len(missing_syms)} missing")

    # Data quality
    fwd_ts_range = (fwd["timestamp"].min(), fwd["timestamp"].max())
    df_quality = data_quality(liq_panel, panel_syms, fwd_ts_range)
    df_quality.to_csv(OUT / "phase11b_liquidity_data_quality.csv", index=False)
    print(f"  Quality: {len(df_quality)} checks")

    # Save parquet
    liq_panel.to_parquet(OUT / "phase11b_canonical_liquidity_panel.parquet", index=False)
    print(f"  Panel: {len(liq_panel):,} rows, {liq_panel['symbol'].nunique()} symbols")

    # Pivot volume to match signal panel
    print("\n[3/5] Pivoting volume data...")
    row_i = merged["timestamp"].map(ts_map).values
    col_i = merged["symbol"].map({s: i for i, s in enumerate(syms)}).values

    def pivot2d(series):
        out = np.full((n_ts, n_sym), np.nan)
        out[row_i, col_i] = series.values
        return out

    sig_arrs = {s: pivot2d(merged[s]) for s in SIGNALS}
    fwd_arr = pivot2d(merged["ret_fwd_1h"])

    # Volume pivot
    vol_ts_map = {t: i for i, t in enumerate(ts_idx)}
    vol_arr = np.full((n_ts, n_sym), np.nan)
    for _, row in liq_panel.iterrows():
        ts = row["timestamp"]
        sym = row["symbol"]
        if ts in vol_ts_map and sym in {s: i for i, s in enumerate(syms)}:
            ti = vol_ts_map[ts]
            ci = {s: i for i, s in enumerate(syms)}[sym]
            vol_arr[ti, ci] = row["notional_volume"]

    # Part B: Capacity analysis
    print("\n[4/5] Evaluating capacity for 4 variants...")
    capacity_dfs = {}
    bottleneck_rows = []

    for sig_id, horizon, guard_name in VARIANTS:
        use_inv = "inverted" in guard_name
        guard = "bucket0_guard" in guard_name
        variant_id = f"{sig_id}__{horizon}__{guard_name}"

        valid = ~np.isnan(sig_arrs[sig_id]) & ~np.isnan(fwd_arr)
        if use_inv:
            sig_eval = np.where(valid, -sig_arrs[sig_id], np.nan)
        else:
            sig_eval = np.where(valid, sig_arrs[sig_id], np.nan)
        fwd_masked = np.where(valid, fwd_arr, np.nan)

        ts_valid = np.any(valid, axis=1)
        cap_df = compute_variant_capacity(sig_eval, fwd_masked, vol_arr, ts_valid, guard=guard)
        capacity_dfs[variant_id] = cap_df

        if len(cap_df) > 0:
            for pr in PARTICIPATION_RATES:
                pr_data = cap_df[cap_df["participation_rate"] == pr]
                if len(pr_data) == 0: continue
                caps = pr_data["capacity_usd"]
                bottleneck_rows.append({
                    "variant_id": variant_id, "participation_rate": pr,
                    "median_capacity_usd": float(caps.median()),
                    "p10_capacity_usd": float(caps.quantile(0.10)),
                    "p5_capacity_usd": float(caps.quantile(0.05)),
                    "min_capacity_usd": float(caps.min()),
                })

        print(f"  {variant_id}: {len(cap_df)} timestamp-pr rows")

    # Capacity by variant summary
    df_cap = pd.DataFrame(bottleneck_rows)
    df_cap.to_csv(OUT / "phase11b_capacity_by_variant.csv", index=False)

    # Bottleneck symbols (lowest volume symbols in each leg)
    bn_rows = []
    sym_idx = {i: s for i, s in enumerate(syms)}
    for vid, cap_df in capacity_dfs.items():
        if len(cap_df) == 0: continue
        # Find most common bottleneck
        pr_data = cap_df[cap_df["participation_rate"] == 0.01]
        if len(pr_data) == 0: continue
        # Upper bottleneck
        ub = pr_data["upper_bottleneck_symbol_idx"].mode()
        lb = pr_data["lower_bottleneck_symbol_idx"].mode()
        bn_rows.append({
            "variant_id": vid,
            "upper_bottleneck_symbol": sym_idx.get(int(ub.iloc[0]), "UNKNOWN") if len(ub) > 0 else "UNKNOWN",
            "lower_bottleneck_symbol": sym_idx.get(int(lb.iloc[0]), "UNKNOWN") if len(lb) > 0 else "UNKNOWN",
        })
    df_bn = pd.DataFrame(bn_rows)
    df_bn.to_csv(OUT / "phase11b_bottleneck_symbols.csv", index=False)

    # Part C: Cost + capacity combined matrix
    print("\n[5/5] Cost + capacity combined matrix...")
    matrix_rows = []
    for vid, cap_df in capacity_dfs.items():
        if len(cap_df) == 0: continue
        parts = vid.split("__")
        # Get gross spread from capacity data
        pr001 = cap_df[cap_df["participation_rate"] == 0.01]
        if len(pr001) == 0: continue
        gross_median_spread = float(pr001["spread"].median())
        gross_mean_spread = float(pr001["spread"].mean())

        for fee in FEE_BPS:
            for slip in SLIP_BPS:
                total_cost_bps = fee + slip
                # Estimate turnover from Phase 11A (use 18.8% for no_guard, 28.6% for guard)
                to_median = 0.286 if "bucket0_guard" in vid else 0.188
                cost_per_reb = total_cost_bps / 10000 * to_median

                for pr in PARTICIPATION_RATES:
                    pr_data = cap_df[cap_df["participation_rate"] == pr]
                    if len(pr_data) == 0: continue
                    caps = pr_data["capacity_usd"]

                    for notional in NOTIONAL_ASSUMPTIONS:
                        capacity_ok = caps.median() >= notional
                        net_spread = gross_median_spread - cost_per_reb

                        matrix_rows.append({
                            "variant_id": vid,
                            "fee_bps": fee, "slippage_bps": slip, "total_cost_bps": total_cost_bps,
                            "participation_rate": pr,
                            "notional_usd": notional,
                            "gross_median_spread": gross_median_spread,
                            "estimated_cost_per_rebalance": float(cost_per_reb),
                            "net_median_spread": float(net_spread),
                            "median_capacity_usd": float(caps.median()),
                            "capacity_ok": capacity_ok,
                            "survives_both": bool(net_spread > 0 and capacity_ok),
                        })

    df_matrix = pd.DataFrame(matrix_rows)
    df_matrix.to_csv(OUT / "phase11b_cost_capacity_matrix.csv", index=False)
    print(f"  Matrix: {len(df_matrix)} rows")

    # PM decision matrix
    pm_rows = []
    for vid in capacity_dfs:
        cap_df = capacity_dfs[vid]
        if len(cap_df) == 0:
            pm_rows.append({"variant_id": vid, "phase11b_status": "DATA_MISSING_BLOCKED"})
            continue

        parts = vid.split("__")
        # Check low cost (fee=2, slip=5) + 1% participation + $10k notional
        low_cost_ok = df_matrix[
            (df_matrix["variant_id"] == vid) &
            (df_matrix["fee_bps"] == 2) & (df_matrix["slippage_bps"] == 5) &
            (df_matrix["participation_rate"] == 0.01) &
            (df_matrix["notional_usd"] == 10000)
        ]["survives_both"].any() if len(df_matrix) > 0 else False

        # Check mid cost (fee=5, slip=10) + 1% + $10k
        mid_cost_ok = df_matrix[
            (df_matrix["variant_id"] == vid) &
            (df_matrix["fee_bps"] == 5) & (df_matrix["slippage_bps"] == 10) &
            (df_matrix["participation_rate"] == 0.01) &
            (df_matrix["notional_usd"] == 10000)
        ]["survives_both"].any() if len(df_matrix) > 0 else False

        # Check $100k notional at low cost
        large_ok = df_matrix[
            (df_matrix["variant_id"] == vid) &
            (df_matrix["fee_bps"] == 2) & (df_matrix["slippage_bps"] == 5) &
            (df_matrix["participation_rate"] == 0.01) &
            (df_matrix["notional_usd"] == 100000)
        ]["survives_both"].any() if len(df_matrix) > 0 else False

        pr_data = cap_df[cap_df["participation_rate"] == 0.01]
        med_cap = pr_data["capacity_usd"].median() if len(pr_data) > 0 else 0

        if mid_cost_ok and large_ok:
            status = "PAPER_READY_DIAGNOSTIC_CANDIDATE"
        elif mid_cost_ok:
            status = "CAPACITY_LIMITED_CANDIDATE"
        elif low_cost_ok:
            status = "COST_CAPACITY_SENSITIVE"
        elif med_cap < 10000:
            status = "FAILS_CAPACITY_DIAGNOSTIC"
        else:
            status = "RETURN_TO_SIGNAL_DESIGN"

        pm_rows.append({
            "variant_id": vid,
            "phase11b_status": status,
            "median_capacity_1pct_usd": float(med_cap),
            "survives_low_cost_10k": low_cost_ok,
            "survives_mid_cost_10k": mid_cost_ok,
            "survives_mid_cost_100k": large_ok,
        })

    df_pm = pd.DataFrame(pm_rows)
    df_pm.to_csv(OUT / "phase11b_pm_decision_matrix.csv", index=False)

    # Quality checks
    qc = [
        ("liquidity_panel_built", "PASS" if len(liq_panel) > 0 else "FAIL"),
        ("liquidity_panel_nonempty", "PASS" if len(liq_panel) > 1000 else "FAIL"),
        ("symbol_coverage_above_70pct", "PASS" if (len(panel_syms) - len(missing_syms)) / len(panel_syms) >= 0.7 else "FAIL"),
        ("timestamp_overlap_with_signal_panel", "PASS" if df_quality[df_quality["metric"]=="timestamp_overlap_with_signal_panel"]["value"].iloc[0] else "FAIL"),
        ("no_duplicate_timestamp_symbol", "PASS" if df_quality[df_quality["metric"]=="duplicate_timestamp_symbol"]["value"].iloc[0] == 0 else "FAIL"),
        ("capacity_computed", "PASS" if len(df_cap) > 0 else "FAIL"),
        ("cost_capacity_matrix_built", "PASS" if len(df_matrix) > 0 else "FAIL"),
        ("participation_rates_complete", "PASS" if sorted(df_matrix["participation_rate"].unique()) == sorted(PARTICIPATION_RATES) else "FAIL"),
        ("notional_assumptions_complete", "PASS" if sorted(df_matrix["notional_usd"].unique()) == sorted(NOTIONAL_ASSUMPTIONS) else "FAIL"),
        ("no_final_model","PASS"),("no_phase12","PASS"),("no_phase13","PASS"),
    ]
    df_qc = pd.DataFrame(qc, columns=["check_name", "status"])
    df_qc.to_csv(OUT / "phase11b_quality_checks.csv", index=False)

    # Summary
    df_summary = pd.DataFrame([{
        "variant_id": vid,
        "symbol_coverage": f"{len(panel_syms)-len(missing_syms)}/{len(panel_syms)}",
        "status": next((r["phase11b_status"] for r in pm_rows if r["variant_id"] == vid), "UNKNOWN"),
    } for vid in capacity_dfs])
    df_summary.to_csv(OUT / "phase11b_capacity_summary.csv", index=False)

    print(f"\n{'='*80}")
    print("Phase 11B Summary:")
    print(f"{'='*80}")
    for _, row in df_pm.iterrows():
        print(f"  {row['variant_id']}: {row['phase11b_status']} (med_cap=${row.get('median_capacity_1pct_usd',0):,.0f} @ 1%)")

    print("\nDone.")


if __name__ == "__main__":
    main()
