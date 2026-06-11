#!/usr/bin/env python3
"""v1.5: Optimized event study — multi-class structure, relaxed stall, trajectory analysis.

Key improvements over v1.4:
1. Multi-class structure (not binary stall/other)
2. Relaxed stall definitions (3 levels)
3. Volume + funding trajectory cross-analysis
4. Sample size diagnosis with funnel breakdown
"""
from __future__ import annotations
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = Path("/root/clawd/jerry/momentum/reports/artifacts/rank154_long_history/daily_panel.pkl")
EVENTS_V0 = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v0" / "events_v0.csv"
OUT_DIR = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_5"
HORIZONS = (1, 3, 5, 10)


def safe_float(x):
    try:
        v = float(x)
    except Exception:
        return None
    return v if math.isfinite(v) else None


def enrich_panel_new_cols(panel: pd.DataFrame) -> pd.DataFrame:
    """Add ONLY new columns not in v0 events: per-step returns, vol ratios, funding trajectory."""
    p = panel.sort_values(["symbol", "date"]).copy()

    # Per-step forward returns (T+1, T+2 only, T+3 only, T+4 only, T+5 only)
    p["fwd_ret_t1"] = p.groupby("symbol")["close"].shift(-1) / p["close"] - 1.0
    p["fwd_ret_t2_only"] = p.groupby("symbol")["close"].shift(-2) / p.groupby("symbol")["close"].shift(-1) - 1.0
    p["fwd_ret_t3_only"] = p.groupby("symbol")["close"].shift(-3) / p.groupby("symbol")["close"].shift(-2) - 1.0
    p["fwd_ret_t4_only"] = p.groupby("symbol")["close"].shift(-4) / p.groupby("symbol")["close"].shift(-3) - 1.0
    p["fwd_ret_t5_only"] = p.groupby("symbol")["close"].shift(-5) / p.groupby("symbol")["close"].shift(-4) - 1.0

    # Volume trajectory
    p["vol_t1"] = p.groupby("symbol")["quote_volume"].shift(-1)
    p["vol_t2"] = p.groupby("symbol")["quote_volume"].shift(-2)
    p["vol_ratio_t1"] = p["vol_t1"] / p["quote_volume"].clip(lower=1)
    p["vol_ratio_t2"] = p["vol_t2"] / p["quote_volume"].clip(lower=1)

    # Funding trajectory
    p["funding_rate_sum_t1"] = p.groupby("symbol")["funding_rate_sum"].shift(-1)
    p["funding_rate_sum_t2"] = p.groupby("symbol")["funding_rate_sum"].shift(-2)
    p["funding_rate_sum_t3"] = p.groupby("symbol")["funding_rate_sum"].shift(-3)

    # Event-day high/low proxy: use max/min of T+0 and T+1 closes
    # (we only have close, so this is approximate)
    p["close_t1"] = p.groupby("symbol")["close"].shift(-1)
    p["max_close_2d"] = p[["close", "close_t1"]].max(axis=1)
    p["min_close_2d"] = p[["close", "close_t1"]].min(axis=1)
    p["range_2d_pct"] = (p["max_close_2d"] - p["min_close_2d"]) / p["close"]

    return p


def classify_structure(row):
    """Multi-class structure classification based on T+1, T+2, T+3 trajectory."""
    t1 = row.get("fwd_ret_t1")
    t2 = row.get("fwd_ret_t2_only")
    t3 = row.get("fwd_ret_t3_only")

    if pd.isna(t1):
        return "no_data"

    if t1 <= 0:
        return "immediate_reversal"

    # T+1 is positive
    if pd.notna(t2) and t2 < 0:
        return "stall_t2"

    # T+1 up, T+2 up
    if pd.notna(t2) and t2 >= 0 and pd.notna(t3) and t3 < 0:
        return "stall_t3"

    # T+1 up, T+2 up, T+3 up
    if pd.notna(t2) and t2 >= 0 and pd.notna(t3) and t3 >= 0:
        return "continuation"

    return "unknown"


def classify_structure_relaxed(row):
    """Relaxed stall: T+1 up AND (T+2 down OR T+2 momentum < 30% of T+1)."""
    t1 = row.get("fwd_ret_t1")
    t2 = row.get("fwd_ret_t2_only")

    if pd.isna(t1):
        return "no_data"

    if t1 <= 0:
        return "immediate_reversal"

    if pd.isna(t2):
        return "no_data"

    # Relaxed stall: T+2 down OR T+2 momentum fraction < 30%
    if t1 > 0.01:  # meaningful T+1 move
        mom_frac = t2 / t1 if t1 != 0 else 0
        if t2 < 0 or mom_frac < 0.3:
            return "stall_relaxed"

    if t2 >= 0:
        return "continuation"

    return "stall_relaxed"


def classify_vol_structure(row):
    """Volume-based structure: did volume contract or expand after event?"""
    vr1 = row.get("vol_ratio_t1")

    if pd.isna(vr1):
        return "no_vol_data"

    if vr1 < 0.5:
        return "vol_collapse"
    elif vr1 < 0.8:
        return "vol_contraction"
    elif vr1 < 1.2:
        return "vol_stable"
    else:
        return "vol_expansion"


def classify_funding_trajectory(row):
    """How does funding change after the event?"""
    fr_t0 = row.get("carry_raw")
    fr_t1 = row.get("funding_rate_sum_t1")

    if pd.isna(fr_t0) or pd.isna(fr_t1):
        return "no_fund_data"

    if fr_t0 < 0 and fr_t1 < 0:
        return "neg_stays_neg"
    if fr_t0 < 0 and fr_t1 >= 0:
        return "neg_flips_pos"
    if fr_t0 >= 0 and fr_t1 >= 0:
        return "pos_stays_pos"
    if fr_t0 >= 0 and fr_t1 < 0:
        return "pos_flips_neg"

    return "other"


def summarize_bucket(df: pd.DataFrame, label: str) -> dict:
    """Compute standard summary stats for a bucket."""
    n = len(df)
    if n == 0:
        return {"bucket": label, "n": 0}
    row = {"bucket": label, "n": n}
    for h in HORIZONS:
        ret_col = f"fwd_ret_{h}d"
        if ret_col in df.columns:
            g = df[ret_col].dropna()
            if len(g) > 0:
                row[f"price_{h}d_mean"] = float(g.mean())
                row[f"price_{h}d_median"] = float(g.median())
                row[f"price_{h}d_winrate"] = float((g > 0).mean())
        # Total returns
        lt_col = f"long_total_ret_{h}d"
        if lt_col in df.columns:
            g = df[lt_col].dropna()
            if len(g) > 0:
                row[f"long_total_{h}d_mean"] = float(g.mean())
        st_col = f"short_total_ret_{h}d"
        if st_col in df.columns:
            g = df[st_col].dropna()
            if len(g) > 0:
                row[f"short_total_{h}d_mean"] = float(g.mean())
        # Funding sum
        fs_col = f"fwd_funding_sum_{h}d"
        if fs_col in df.columns:
            g = df[fs_col].dropna()
            if len(g) > 0:
                row[f"funding_{h}d_mean"] = float(g.mean())
    # MAE/MFE
    for h in (5, 10):
        mae_col = f"mae_long_{h}d"
        mfe_col = f"mfe_long_{h}d"
        if mae_col in df.columns:
            g = df[mae_col].dropna()
            if len(g) > 0:
                row[f"mae_{h}d_median"] = float(g.median())
                row[f"mae_{h}d_p10"] = float(g.quantile(0.10))
        if mfe_col in df.columns:
            g = df[mfe_col].dropna()
            if len(g) > 0:
                row[f"mfe_{h}d_median"] = float(g.median())
                row[f"mfe_{h}d_p90"] = float(g.quantile(0.90))
    return row


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading panel...")
    panel = pd.read_pickle(PANEL_PATH)
    print(f"Panel: {len(panel)} rows, {panel['symbol'].nunique()} symbols")

    print("Enriching panel with new columns (per-step returns, vol, funding trajectory)...")
    enriched = enrich_panel_new_cols(panel)

    # Only keep new columns for merge (avoid duplicating v0 columns)
    new_cols = ["symbol", "date",
                "fwd_ret_t1", "fwd_ret_t2_only", "fwd_ret_t3_only", "fwd_ret_t4_only", "fwd_ret_t5_only",
                "vol_ratio_t1", "vol_ratio_t2",
                "funding_rate_sum_t1", "funding_rate_sum_t2", "funding_rate_sum_t3",
                "range_2d_pct"]
    enriched["date_str"] = enriched["date"].astype(str).str[:10]

    print("Loading v0 events...")
    events = pd.read_csv(EVENTS_V0)
    gainer_events = events[events["is_top_gainer"]].copy()
    loser_events = events[events["is_top_loser"]].copy()
    print(f"Gainer events: {len(gainer_events)}, Loser events: {len(loser_events)}")

    # Merge only new columns
    merge_cols = ["symbol", "date_str"] + [c for c in new_cols if c not in ("symbol", "date")]
    gainer_events = gainer_events.merge(
        enriched[merge_cols].rename(columns={"date_str": "event_date"}),
        on=["symbol", "event_date"],
        how="left"
    )
    print(f"Gainer events enriched: {len(gainer_events)}")
    print(f"  with fwd_ret_t1: {gainer_events['fwd_ret_t1'].notna().sum()}")
    print(f"  with fwd_ret_5d (from v0): {gainer_events['fwd_ret_5d'].notna().sum()}")

    # ========== CLASSIFY ==========
    print("\nClassifying structure...")
    gainer_events["structure"] = gainer_events.apply(classify_structure, axis=1)
    gainer_events["structure_relaxed"] = gainer_events.apply(classify_structure_relaxed, axis=1)
    gainer_events["vol_structure"] = gainer_events.apply(classify_vol_structure, axis=1)
    gainer_events["funding_traj"] = gainer_events.apply(classify_funding_trajectory, axis=1)

    # Define funding buckets
    carry_p5 = gainer_events["carry_raw"].quantile(0.05)
    carry_p95 = gainer_events["carry_raw"].quantile(0.95)
    carry_p25 = gainer_events["carry_raw"].quantile(0.25)
    carry_p75 = gainer_events["carry_raw"].quantile(0.75)

    gainer_events["funding_bucket"] = "mid"
    gainer_events.loc[gainer_events["carry_raw"] <= carry_p5, "funding_bucket"] = "neg_extreme"
    gainer_events.loc[(gainer_events["carry_raw"] > carry_p5) & (gainer_events["carry_raw"] <= carry_p25), "funding_bucket"] = "neg_moderate"
    gainer_events.loc[gainer_events["carry_raw"] >= carry_p95, "funding_bucket"] = "pos_extreme"
    gainer_events.loc[(gainer_events["carry_raw"] < carry_p95) & (gainer_events["carry_raw"] >= carry_p75), "funding_bucket"] = "pos_moderate"

    # ========== DIAGNOSTIC FUNNEL ==========
    print("\n" + "=" * 60)
    print("DIAGNOSTIC FUNNEL: Why G_neg_extreme_stall is small")
    print("=" * 60)

    ne = gainer_events[gainer_events["funding_bucket"] == "neg_extreme"]
    total_ne = len(ne)
    t1_up = ne["fwd_ret_t1"] > 0
    t2_down = ne["fwd_ret_t2_only"] < 0

    funnel = [
        ("Total gainer events", len(gainer_events)),
        (f"Neg extreme (carry_raw <= p5 = {carry_p5:.6f})", total_ne),
        (f"  T+1 up (pass step 1)", int(t1_up.sum())),
        (f"  T+1 down (FILTERED OUT)", int((~t1_up).sum())),
        (f"  Among T+1 up: T+2 down (stall_t2)", int((t1_up & t2_down).sum())),
        (f"  Among T+1 up: T+2 up (continuation starts)", int((t1_up & ~t2_down).sum())),
    ]
    for label, count in funnel:
        pct = count / len(gainer_events) * 100 if "Total" in label else count / total_ne * 100 if total_ne > 0 else 0
        print(f"  {label}: {count} ({pct:.1f}%)")

    # ========== BUILD SUMMARIES ==========
    print("\n" + "=" * 60)
    print("SUMMARY TABLES")
    print("=" * 60)

    rows = []

    # 1. By structure (all gainers)
    print("\n--- Table 1: Structure breakdown (all gainers) ---")
    for s in ["immediate_reversal", "stall_t2", "stall_t3", "continuation", "melt_up", "no_data", "unknown"]:
        grp = gainer_events[gainer_events["structure"] == s]
        if len(grp) == 0:
            continue
        r = summarize_bucket(grp, f"G_{s}")
        rows.append(r)
        print(f"  {r['bucket']}: n={r['n']}, "
              f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
              f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
              f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%, "
              f"5d short_total={r.get('short_total_5d_mean', 0)*100:.2f}%")

    # 2. By funding_bucket x structure
    print("\n--- Table 2: Funding x Structure ---")
    for fb in ["neg_extreme", "neg_moderate", "mid", "pos_moderate", "pos_extreme"]:
        subset = gainer_events[gainer_events["funding_bucket"] == fb]
        if len(subset) == 0:
            continue
        for s in ["immediate_reversal", "stall_t2", "stall_t3", "continuation", "melt_up", "no_data", "unknown"]:
            grp = subset[subset["structure"] == s]
            if len(grp) == 0:
                continue
            r = summarize_bucket(grp, f"G_{fb}_{s}")
            rows.append(r)
            if len(grp) >= 10:
                print(f"  {r['bucket']}: n={r['n']}, "
                      f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                      f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                      f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%, "
                      f"5d short_total={r.get('short_total_5d_mean', 0)*100:.2f}%")

    # 3. Relaxed stall
    print("\n--- Table 3: Relaxed stall definition ---")
    for fb in ["neg_extreme", "neg_moderate"]:
        subset = gainer_events[gainer_events["funding_bucket"] == fb]
        for s in ["immediate_reversal", "stall_relaxed", "continuation", "no_data"]:
            grp = subset[subset["structure_relaxed"] == s]
            if len(grp) == 0:
                continue
            r = summarize_bucket(grp, f"G_{fb}_relaxed_{s}")
            rows.append(r)
            if len(grp) >= 10:
                print(f"  {r['bucket']}: n={r['n']}, "
                      f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                      f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                      f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%")

    # 4. Volume structure
    print("\n--- Table 4: Volume structure x Funding ---")
    for fb in ["neg_extreme", "mid", "pos_extreme"]:
        subset = gainer_events[gainer_events["funding_bucket"] == fb]
        for vs in ["vol_collapse", "vol_contraction", "vol_stable", "vol_expansion"]:
            grp = subset[subset["vol_structure"] == vs]
            if len(grp) == 0:
                continue
            r = summarize_bucket(grp, f"G_{fb}_{vs}")
            rows.append(r)
            if len(grp) >= 20:
                print(f"  {r['bucket']}: n={r['n']}, "
                      f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                      f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                      f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%")

    # 5. Funding trajectory
    print("\n--- Table 5: Funding trajectory x Funding bucket ---")
    for fb in ["neg_extreme", "pos_extreme"]:
        subset = gainer_events[gainer_events["funding_bucket"] == fb]
        for ft in ["neg_stays_neg", "neg_flips_pos", "pos_stays_pos", "pos_flips_neg"]:
            grp = subset[subset["funding_traj"] == ft]
            if len(grp) == 0:
                continue
            r = summarize_bucket(grp, f"G_{fb}_{ft}")
            rows.append(r)
            if len(grp) >= 20:
                print(f"  {r['bucket']}: n={r['n']}, "
                      f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                      f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                      f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%")

    # 6. Combined: neg_extreme x structure x vol_structure
    print("\n--- Table 6: Combined buckets (neg_extreme + structure + vol_structure) ---")
    ne = gainer_events[gainer_events["funding_bucket"] == "neg_extreme"]
    for (s, vs), grp in ne.groupby(["structure", "vol_structure"]):
        if len(grp) >= 10:
            r = summarize_bucket(grp, f"G_ne_{s}_{vs}")
            rows.append(r)
            print(f"  {r['bucket']}: n={r['n']}, "
                  f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                  f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                  f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%")

    # 7. LOSERS for comparison
    print("\n--- Table 7: Loser events x funding ---")
    loser_events = loser_events.merge(
        enriched[merge_cols].rename(columns={"date_str": "event_date"}),
        on=["symbol", "event_date"],
        how="left"
    )
    loser_events["structure"] = loser_events.apply(classify_structure, axis=1)
    loser_events["funding_bucket"] = "mid"
    loser_events.loc[loser_events["carry_raw"] <= loser_events["carry_raw"].quantile(0.05), "funding_bucket"] = "neg_extreme"
    loser_events.loc[loser_events["carry_raw"] >= loser_events["carry_raw"].quantile(0.95), "funding_bucket"] = "pos_extreme"

    for fb in ["neg_extreme", "mid", "pos_extreme"]:
        for s in ["immediate_reversal", "stall_t2", "stall_t3", "continuation"]:
            grp = loser_events[(loser_events["funding_bucket"] == fb) & (loser_events["structure"] == s)]
            if len(grp) == 0:
                continue
            r = summarize_bucket(grp, f"L_{fb}_{s}")
            rows.append(r)
            if len(grp) >= 20:
                print(f"  {r['bucket']}: n={r['n']}, "
                      f"5d price={r.get('price_5d_mean', 0)*100:.2f}%, "
                      f"5d winrate={r.get('price_5d_winrate', 0)*100:.1f}%, "
                      f"5d long_total={r.get('long_total_5d_mean', 0)*100:.2f}%")

    # ========== SAVE ==========
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(OUT_DIR / "summary_v1_5.csv", index=False)

    # Save enriched events
    sample_cols = ["event_date", "symbol", "tags", "carry_raw", "funding_bucket", "structure",
                   "structure_relaxed", "vol_structure", "funding_traj",
                   "ret_1d", "fwd_ret_t1", "fwd_ret_t2_only", "fwd_ret_t3_only",
                   "vol_ratio_t1", "vol_ratio_t2", "range_2d_pct",
                   "funding_rate_sum", "funding_rate_sum_t1", "funding_rate_sum_t2",
                   "fwd_ret_1d", "fwd_ret_3d", "fwd_ret_5d", "fwd_ret_10d",
                   "long_total_ret_1d", "long_total_ret_5d", "short_total_ret_5d",
                   "mae_long_5d", "mfe_long_5d"]
    save_cols = [c for c in sample_cols if c in gainer_events.columns]
    gainer_events[save_cols].to_csv(OUT_DIR / "enriched_gainer_events_v1_5.csv", index=False)

    # Manifest
    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "version": "v1_5",
        "improvements": [
            "Multi-class structure: immediate_reversal, stall_t2, stall_t3, continuation, melt_up",
            "Relaxed stall definition: stall_relaxed (T+2 down OR momentum fraction < 30%)",
            "Volume structure: collapse, contraction, stable, expansion",
            "Funding trajectory: neg_stays_neg, neg_flips_pos, pos_stays_pos, pos_flips_neg",
            "Diagnostic funnel: why G_neg_extreme_stall has only 101 samples",
            "Combined buckets: funding x structure x vol_structure",
        ],
        "panel_rows": len(panel),
        "gainer_events": len(gainer_events),
        "funding_bucket_thresholds": {
            "neg_extreme": f"carry_raw <= p5 ({carry_p5:.6f})",
            "neg_moderate": f"p5 < carry_raw <= p25 ({carry_p25:.6f})",
            "mid": f"p25 < carry_raw < p75",
            "pos_moderate": f"p75 <= carry_raw < p95",
            "pos_extreme": f"carry_raw >= p95 ({carry_p95:.6f})",
        },
        "data_limitations": [
            "Daily close only: no high/low/open, so intraday patterns (pump+dump within same day) are invisible",
            "No per-settlement funding data: only daily sum, so 4h/8h/1h interval patterns are aggregated",
            "MAE/MFE uses daily closes: intraday risk is understated",
        ],
    }
    (OUT_DIR / "manifest_v1_5.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

    # Diagnostic funnel CSV
    funnel_df = pd.DataFrame(funnel, columns=["step", "count"])
    funnel_df.to_csv(OUT_DIR / "diagnostic_funnel_v1_5.csv", index=False)

    print(f"\n[ok] wrote {OUT_DIR}")
    print(f"  summary_v1_5.csv: {len(summary_df)} buckets")
    print(f"  enriched_gainer_events_v1_5.csv: {len(gainer_events)} rows")
    print(f"  diagnostic_funnel_v1_5.csv: {len(funnel_df)} steps")


if __name__ == "__main__":
    main()
