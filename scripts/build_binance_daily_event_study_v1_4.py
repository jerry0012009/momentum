#!/usr/bin/env python3
"""
Step 1.4: Daily-side taxonomy of post-event structures.
Builds a taxonomy of post-event structures for new top-gainer / top-loser events,
with special focus on negative funding extremes / squeeze-like structures.

Artifacts produced:
  - taxonomy_summary_v1_4.csv
  - findings_v1_4.md (Chinese)
  - manifest_v1_4.json
"""
import json, os, sys, warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── paths ──────────────────────────────────────────────────────────────────
ROOT = Path("/root/clawd/jerry/momentum")
OUT = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_4"
OUT.mkdir(parents=True, exist_ok=True)

PANEL_PKL   = ROOT / "reports" / "artifacts" / "rank154_long_history" / "daily_panel.pkl"
V1_CSV      = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1" / "events_v1.csv"
V13_CSV     = ROOT / "reports" / "artifacts" / "binance_daily_event_study_v1_3" / "daily_stall_candidates_v1_3.csv"

# ── 1. Load data ───────────────────────────────────────────────────────────
print("[1/8] Loading data...")
panel = pd.read_pickle(PANEL_PKL)
events_v1 = pd.read_csv(V1_CSV, parse_dates=["event_date"])
v13 = pd.read_csv(V13_CSV, parse_dates=["event_date"])

# Normalize date columns for merge
panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
events_v1["event_date"] = pd.to_datetime(events_v1["event_date"]).dt.tz_localize(None)
v13["event_date"] = pd.to_datetime(v13["event_date"]).dt.tz_localize(None)

# Ensure symbol is string type everywhere
panel["symbol"] = panel["symbol"].astype(str)
events_v1["symbol"] = events_v1["symbol"].astype(str)
v13["symbol"] = v13["symbol"].astype(str)

# ── 2. Merge funding onto events ───────────────────────────────────────────
print("[2/8] Merging funding data onto events...")
# Filter to new streak events
new_events = events_v1[events_v1["streak_label"] == "new"].copy()
print(f"  Total new events: {len(new_events)}")

# Merge funding from panel on (event_date, symbol)
new_events = new_events.merge(
    panel[["date", "symbol", "funding_rate_last", "funding_rate_sum", "funding_count"]],
    left_on=["event_date", "symbol"],
    right_on=["date", "symbol"],
    how="left",
)
new_events.drop(columns=["date"], inplace=True)
print(f"  After funding merge: {len(new_events)} rows, "
      f"funding_rate_last non-null: {new_events['funding_rate_last'].notna().sum()}")

# ── 3. Compute derived features for taxonomy ──────────────────────────────
print("[3/8] Computing derived features...")

# 3a. Funding normalization: funding_rate_sum / funding_count → avg per-interval rate
new_events["funding_avg"] = np.where(
    new_events["funding_count"] > 0,
    new_events["funding_rate_sum"] / new_events["funding_count"],
    0.0,
)

# 3b. Funding extreme flags (daily-panel level percentiles)
frl = new_events["funding_rate_last"].dropna()
frl_neg_mask = frl < 0
frl_pos_mask = frl > 0

p5_neg  = frl[frl_neg_mask].quantile(0.05) if frl_neg_mask.any() else -0.01
p10_neg = frl[frl_neg_mask].quantile(0.10) if frl_neg_mask.any() else -0.005
p90_pos = frl[frl_pos_mask].quantile(0.90) if frl_pos_mask.any() else 0.005
p95_pos = frl[frl_pos_mask].quantile(0.95) if frl_pos_mask.any() else 0.01

print(f"  Funding last: p5_neg={p5_neg:.6f}, p10_neg={p10_neg:.6f}, p90_pos={p90_pos:.6f}, p95_pos={p95_pos:.6f}")

# Normalized funding extremes (per-interval)
fav = new_events["funding_avg"].dropna()
fav_neg = fav[fav < 0]
fav_pos = fav[fav > 0]
fav_p5_neg  = fav_neg.quantile(0.05) if len(fav_neg) > 0 else -0.01
fav_p10_neg = fav_neg.quantile(0.10) if len(fav_neg) > 0 else -0.005
fav_p90_pos = fav_pos.quantile(0.90) if len(fav_pos) > 0 else 0.005
fav_p95_pos = fav_pos.quantile(0.95) if len(fav_pos) > 0 else 0.01
print(f"  Funding avg: p5_neg={fav_p5_neg:.6f}, p10_neg={fav_p10_neg:.6f}, p90_pos={fav_p90_pos:.6f}, p95_pos={fav_p95_pos:.6f}")

# Funding extreme flags
new_events["funding_neg_extreme"] = new_events["funding_rate_last"] <= p5_neg
new_events["funding_neg_moderate"] = (new_events["funding_rate_last"] < 0) & ~new_events["funding_neg_extreme"]
new_events["funding_pos_extreme"] = new_events["funding_rate_last"] >= p95_pos
new_events["funding_pos_moderate"] = (new_events["funding_rate_last"] > 0) & ~new_events["funding_pos_extreme"]
new_events["funding_zero_or_tiny"] = new_events["funding_rate_last"].abs() < 1e-5
new_events["funding_neg_norm_extreme"] = new_events["funding_avg"] <= fav_p5_neg
new_events["funding_pos_norm_extreme"] = new_events["funding_avg"] >= fav_p95_pos

# Simple sign
new_events["funding_sign"] = np.where(
    new_events["funding_rate_last"] < -1e-6, "negative",
    np.where(new_events["funding_rate_last"] > 1e-6, "positive", "zero")
)

# 3c. Pre-event runup (from panel: compute prior 3d/5d return for each event)
print("[3/8b] Computing pre-event runup...")
# Build a symbol->date->close lookup
panel_close = panel.set_index(["symbol", "date"])["close"].sort_index()

def get_prior_return(row, n_days):
    """Get close-to-close return over prior n_days for the event symbol/date."""
    sym, dt = row["symbol"], row["event_date"]
    try:
        idx = panel_close.index.get_loc((sym, dt))
        if idx >= n_days:
            c0 = panel_close.iloc[idx - n_days]
            c1 = panel_close.iloc[idx]
            if c0 > 0:
                return (c1 - c0) / c0
    except (KeyError, IndexError):
        pass
    return np.nan

# Vectorized approach: shift within each symbol group
print("  Computing prior returns (vectorized)...")
panel_sorted = panel.sort_values(["symbol", "date"]).copy()
panel_sorted["close_shift3"] = panel_sorted.groupby("symbol")["close"].shift(3)
panel_sorted["close_shift5"] = panel_sorted.groupby("symbol")["close"].shift(5)
panel_sorted["prior_ret_3d"] = (panel_sorted["close"] - panel_sorted["close_shift3"]) / panel_sorted["close_shift3"]
panel_sorted["prior_ret_5d"] = (panel_sorted["close"] - panel_sorted["close_shift5"]) / panel_sorted["close_shift5"]

# Also compute volume ratio (event day vs prior 5d avg)
panel_sorted["vol_shift_avg5"] = panel_sorted.groupby("symbol")["quote_volume"].transform(
    lambda x: x.rolling(5, min_periods=1).mean().shift(1)
)
panel_sorted["vol_ratio_vs_5d"] = panel_sorted["quote_volume"] / panel_sorted["vol_shift_avg5"]

# Merge prior returns onto new_events
new_events = new_events.merge(
    panel_sorted[["date", "symbol", "prior_ret_3d", "prior_ret_5d", "vol_ratio_vs_5d"]],
    left_on=["event_date", "symbol"],
    right_on=["date", "symbol"],
    how="left",
)
new_events.drop(columns=["date"], inplace=True)

# 3d. Prior runup flags
for horizon in [3, 5]:
    col = f"prior_ret_{horizon}d"
    p75 = new_events[col].quantile(0.75)
    p90 = new_events[col].quantile(0.90)
    p25 = new_events[col].quantile(0.25)
    p10 = new_events[col].quantile(0.10)
    print(f"  {horizon}d prior return: p10={p10:.4f}, p25={p25:.4f}, p75={p75:.4f}, p90={p90:.4f}")
    new_events[f"prior_runup_{horizon}d"] = new_events[col] >= p75
    new_events[f"prior_strong_runup_{horizon}d"] = new_events[col] >= p90
    new_events[f"prior_drawdown_{horizon}d"] = new_events[col] <= p25

# 3e. Volume shock flag
vol_p75 = new_events["vol_ratio_vs_5d"].quantile(0.75)
vol_p90 = new_events["vol_ratio_vs_5d"].quantile(0.90)
vol_p25 = new_events["vol_ratio_vs_5d"].quantile(0.25)
print(f"  Volume ratio vs 5d avg: p25={vol_p25:.2f}, p75={vol_p75:.2f}, p90={vol_p90:.2f}")
new_events["vol_shock"] = new_events["vol_ratio_vs_5d"] >= vol_p90
new_events["vol_contraction"] = new_events["vol_ratio_vs_5d"] <= vol_p25

# 3f. Cluster flag: is this event within 3 days of another new event for the same symbol?
print("[3/8c] Computing event clustering...")
new_events_sorted = new_events.sort_values(["symbol", "event_date"]).copy()
new_events_sorted["prev_event_date"] = new_events_sorted.groupby("symbol")["event_date"].shift(1)
new_events_sorted["days_since_prev_event"] = (
    new_events_sorted["event_date"] - new_events_sorted["prev_event_date"]
).dt.days
new_events_sorted["in_cluster"] = new_events_sorted["days_since_prev_event"] <= 3
new_events_sorted["next_event_date"] = new_events_sorted.groupby("symbol")["event_date"].shift(-1)
new_events_sorted["days_to_next_event"] = (
    new_events_sorted["next_event_date"] - new_events_sorted["event_date"]
).dt.days
new_events_sorted["leads_cluster"] = new_events_sorted["days_to_next_event"] <= 3

new_events = new_events_sorted.copy()

# ── 4. Merge v1.3 stall patterns ──────────────────────────────────────────
print("[4/8] Merging v1.3 stall patterns...")
pat_cols = [c for c in v13.columns if c.startswith("pat_")]
baseline_cols = [c for c in v13.columns if c.startswith("baseline_")]
merge_cols = ["event_date", "symbol"] + pat_cols + baseline_cols
new_events = new_events.merge(
    v13[merge_cols],
    on=["event_date", "symbol"],
    how="left",
)
# Fill NaN patterns with False
for c in pat_cols + baseline_cols:
    new_events[c] = new_events[c].fillna(False)

# ── 5. Define taxonomy buckets ─────────────────────────────────────────────
print("[5/8] Defining taxonomy buckets...")

# We'll create a primary "bucket_label" for each event
# The taxonomy is multi-dimensional; we'll compute stats for cross-sections

def classify_bucket(row):
    """Assign a primary taxonomy label based on event type + funding + stall."""
    etype = row["event_type"]
    is_gainer = etype == "top_gainer_1d"
    prefix = "G" if is_gainer else "L"

    # Funding dimension
    if row["funding_neg_extreme"]:
        fund = "neg_extreme"
    elif row["funding_neg_moderate"]:
        fund = "neg_moderate"
    elif row["funding_pos_extreme"]:
        fund = "pos_extreme"
    elif row["funding_pos_moderate"]:
        fund = "pos_moderate"
    else:
        fund = "zero"

    # Stall dimension (for gainers: check G patterns; for losers: check L patterns)
    if is_gainer:
        has_stall = any([row.get("pat_G1_t1up_t2stall", False),
                        row.get("pat_G2_vol_contraction", False),
                        row.get("pat_G3_exhaustion", False),
                        row.get("pat_G4_decel", False)])
        has_cont = row.get("pat_G5_cont_then_rev", False)
    else:
        has_stall = any([row.get("pat_L1_tdown_t2bounce", False),
                        row.get("pat_L2_vol_contraction", False),
                        row.get("pat_L3_bounce_exhaust", False),
                        row.get("pat_L4_decel", False)])
        has_cont = row.get("pat_L5_cont_then_bounce", False)

    if has_stall:
        struct = "stall"
    elif has_cont:
        struct = "continuation"
    else:
        struct = "other"

    return f"{prefix}_{fund}_{struct}"

new_events["bucket"] = new_events.apply(classify_bucket, axis=1)

# Also create a simpler funding-only bucket
new_events["fund_bucket"] = new_events.apply(
    lambda r: f"{'G' if r['event_type']=='top_gainer_1d' else 'L'}_"
              + ("neg_extreme" if r["funding_neg_extreme"] else
                 "neg_moderate" if r["funding_neg_moderate"] else
                 "pos_extreme" if r["funding_pos_extreme"] else
                 "pos_moderate" if r["funding_pos_moderate"] else "zero"),
    axis=1
)

# Squeeze-specific bucket: negative funding + volume shock
new_events["squeeze_candidate"] = (
    new_events["funding_neg_extreme"] &
    (new_events["vol_shock"] | (new_events["vol_ratio_vs_5d"] >= 2.0))
)

# Negative funding + no stall (potential squeeze continuation)
new_events["neg_nostall"] = (
    new_events["funding_rate_last"] < -1e-6
)

# ── 6. Compute bucket statistics ───────────────────────────────────────────
print("[6/8] Computing bucket statistics...")

def bucket_stats(df, label_col, min_count=5):
    """Compute summary stats for each bucket."""
    rows = []
    for bucket, grp in df.groupby(label_col):
        if len(grp) < min_count:
            continue
        n = len(grp)
        r = {
            "bucket": bucket,
            "n": n,
            "fwd_ret_1d_mean": grp["fwd_ret_1d"].mean(),
            "fwd_ret_1d_median": grp["fwd_ret_1d"].median(),
            "fwd_ret_3d_mean": grp["fwd_ret_3d"].mean(),
            "fwd_ret_3d_median": grp["fwd_ret_3d"].median(),
            "fwd_ret_5d_mean": grp["fwd_ret_5d"].mean(),
            "fwd_ret_5d_median": grp["fwd_ret_5d"].median(),
            "win_rate_1d": (grp["fwd_ret_1d"] > 0).mean(),
            "win_rate_3d": (grp["fwd_ret_3d"] > 0).mean(),
            "win_rate_5d": (grp["fwd_ret_5d"] > 0).mean(),
        }
        # MAE / MFE
        if "mae_long_5d" in grp.columns:
            r["mae_long_5d_mean"] = grp["mae_long_5d"].mean()
            r["mfe_long_5d_mean"] = grp["mfe_long_5d"].mean()
        if "long_total_ret_5d" in grp.columns:
            r["long_total_ret_5d_mean"] = grp["long_total_ret_5d"].mean()
            r["short_total_ret_5d_mean"] = grp["short_total_ret_5d"].mean()

        # Funding stats
        if "funding_rate_last" in grp.columns:
            r["funding_rate_last_mean"] = grp["funding_rate_last"].mean()
            r["funding_rate_last_median"] = grp["funding_rate_last"].median()
            r["funding_avg_mean"] = grp["funding_avg"].mean()

        rows.append(r)
    return pd.DataFrame(rows)

# Main taxonomy (3-way: type × funding × structure)
tax_main = bucket_stats(new_events, "bucket")
tax_main = tax_main.sort_values("n", ascending=False).reset_index(drop=True)

# Funding-only bucket
tax_fund = bucket_stats(new_events, "fund_bucket")
tax_fund = tax_fund.sort_values("n", ascending=False).reset_index(drop=True)

# Event type only
tax_type = bucket_stats(new_events, "event_type")

# Squeeze candidates
squeeze_df = new_events[new_events["squeeze_candidate"]]
squeeze_stats = bucket_stats(squeeze_df, "event_type") if len(squeeze_df) > 0 else pd.DataFrame()

# Negative funding breakdown by stall vs no-stall (gainers only)
gainers_neg = new_events[
    (new_events["event_type"] == "top_gainer_1d") &
    (new_events["funding_rate_last"] < -1e-6)
].copy()
if len(gainers_neg) > 0:
    gainers_neg["neg_stall_type"] = np.where(
        gainers_neg["pat_G1_t1up_t2stall"] | gainers_neg["pat_G2_vol_contraction"] |
        gainers_neg["pat_G3_exhaustion"] | gainers_neg["pat_G4_decel"],
        "neg_stall",
        np.where(gainers_neg["pat_G5_cont_then_rev"], "neg_continuation", "neg_other")
    )
    tax_neg_stall = bucket_stats(gainers_neg, "neg_stall_type")
else:
    tax_neg_stall = pd.DataFrame()

# Negative funding for losers
losers_neg = new_events[
    (new_events["event_type"] == "top_loser_1d") &
    (new_events["funding_rate_last"] < -1e-6)
].copy()
if len(losers_neg) > 0:
    losers_neg["neg_stall_type"] = np.where(
        losers_neg["pat_L1_tdown_t2bounce"] | losers_neg["pat_L2_vol_contraction"] |
        losers_neg["pat_L3_bounce_exhaust"] | losers_neg["pat_L4_decel"],
        "neg_bounce",
        np.where(losers_neg["pat_L5_cont_then_bounce"], "neg_continuation", "neg_other")
    )
    tax_neg_losers = bucket_stats(losers_neg, "neg_stall_type")
else:
    tax_neg_losers = pd.DataFrame()

# ── 6b. Detailed squeeze analysis ─────────────────────────────────────────
print("[6/8b] Squeeze hypothesis deep-dive...")

# For gainers: compare negative funding extreme vs all others
gainers = new_events[new_events["event_type"] == "top_gainer_1d"].copy()
gainers["neg_extreme_flag"] = gainers["funding_neg_extreme"]
squeeze_gainer = bucket_stats(gainers, "neg_extreme_flag")
squeeze_gainer["bucket"] = squeeze_gainer["bucket"].map({True: "G_neg_extreme", False: "G_not_neg_extreme"})

# For gainers: compare across funding quantiles (10 bins)
gainers["funding_bin"] = pd.qcut(gainers["funding_rate_last"], q=10, duplicates="drop")
tax_funding_decile_g = bucket_stats(gainers, "funding_bin")
tax_funding_decile_g = tax_funding_decile_g.sort_values("funding_rate_last_median").reset_index(drop=True)

# Volume shock interaction with funding
gainers["vol_fund_bucket"] = np.where(
    gainers["squeeze_candidate"], "G_squeeze_candidate",
    np.where(gainers["funding_neg_extreme"] & ~gainers["vol_shock"], "G_neg_ext_low_vol",
    np.where(gainers["funding_neg_moderate"], "G_neg_mod",
    np.where(gainers["funding_pos_extreme"], "G_pos_extreme",
    np.where(gainers["funding_pos_moderate"], "G_pos_moderate", "G_zero")))))
tax_vol_fund = bucket_stats(gainers, "vol_fund_bucket")

# ── 6c. Prior runup interaction ────────────────────────────────────────────
print("[6/8c] Prior runup interaction...")
gainers["runup_fund_bucket"] = np.where(
    gainers["funding_neg_extreme"] & gainers["prior_runup_5d"],
    "G_neg_ext_after_runup",
    np.where(gainers["funding_neg_extreme"] & gainers["prior_drawdown_5d"],
    "G_neg_ext_after_drawdown",
    np.where(gainers["funding_neg_extreme"],
    "G_neg_ext_neutral",
    "G_other")))
tax_runup = bucket_stats(gainers, "runup_fund_bucket")

# ── 6d. Cluster interaction ───────────────────────────────────────────────
print("[6/8d] Cluster interaction...")
gainers["cluster_fund"] = np.where(
    gainers["funding_neg_extreme"] & gainers["in_cluster"],
    "G_neg_ext_in_cluster",
    np.where(gainers["funding_neg_extreme"] & ~gainers["in_cluster"],
    "G_neg_ext_isolated",
    np.where(gainers["in_cluster"],
    "G_other_in_cluster",
    "G_other_isolated")))
tax_cluster = bucket_stats(gainers, "cluster_fund")

# ── 7. Save artifacts ─────────────────────────────────────────────────────
print("[7/8] Saving artifacts...")

# Combine all taxonomies into one CSV with section labels
all_sections = []
for label, df in [
    ("main_taxonomy", tax_main),
    ("funding_only", tax_fund),
    ("event_type", tax_type),
    ("squeeze_candidates", squeeze_stats),
    ("gainer_neg_stall_split", tax_neg_stall),
    ("loser_neg_stall_split", tax_neg_losers),
    ("squeeze_hypothesis", squeeze_gainer),
    ("funding_decile_gainer", tax_funding_decile_g),
    ("vol_fund_interaction", tax_vol_fund),
    ("runup_fund_interaction", tax_runup),
    ("cluster_fund_interaction", tax_cluster),
]:
    if len(df) > 0:
        df2 = df.copy()
        df2.insert(0, "section", label)
        all_sections.append(df2)

summary = pd.concat(all_sections, ignore_index=True)
summary.to_csv(OUT / "taxonomy_summary_v1_4.csv", index=False)
print(f"  Saved taxonomy_summary_v1_4.csv ({len(summary)} rows)")

# ── 7b. Build findings (Chinese) ──────────────────────────────────────────
print("[7/8b] Writing findings...")

def fmt_pct(v):
    if pd.isna(v):
        return "N/A"
    return f"{v*100:+.2f}%"

def fmt_pct_plain(v):
    if pd.isna(v):
        return "N/A"
    return f"{v*100:.2f}%"

# Key findings
findings = []
findings.append("# Step 1.4 日线事件结构分类分析报告")
findings.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
findings.append(f"样本总量: {len(new_events)} 个 new 事件 (非连续事件)")
findings.append(f"其中 top_gainer_1d: {(new_events['event_type']=='top_gainer_1d').sum()}, top_loser_1d: {(new_events['event_type']=='top_loser_1d').sum()}")

findings.append("\n## 一、资金费率分布概览")
findings.append(f"- funding_rate_last 有效率: {new_events['funding_rate_last'].notna().mean()*100:.1f}%")
findings.append(f"- 负费率事件占比: {(new_events['funding_rate_last'] < -1e-6).mean()*100:.1f}%")
findings.append(f"- 极端负费率 (≤ p5) 阈值: {p5_neg:.6f}")
findings.append(f"- 极端正费率 (≥ p95) 阈值: {p95_pos:.6f}")

findings.append("\n## 二、主要分类结果 (funding × 结构)")

# Gainer summary
findings.append("\n### 2.1 Gainer (涨幅第一) 各 funding 分桶表现")
g_fund = tax_fund[tax_fund["bucket"].str.startswith("G_")].copy()
for _, row in g_fund.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d平均={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d平均={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d平均={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"1d胜率={fmt_pct_plain(row['win_rate_1d'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n### 2.2 Loser (跌幅第一) 各 funding 分桶表现")
l_fund = tax_fund[tax_fund["bucket"].str.startswith("L_")].copy()
for _, row in l_fund.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d平均={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d平均={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d平均={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"1d胜率={fmt_pct_plain(row['win_rate_1d'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n## 三、做空挤压 (Squeeze) 假设检验")

# Gainer: negative extreme vs not
findings.append("\n### 3.1 涨幅第一: 极端负费率 vs 非极端负费率")
for _, row in squeeze_gainer.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

# Squeeze candidates
if len(squeeze_stats) > 0:
    findings.append("\n### 3.2 挤压候选事件 (极端负费率 + 成交量激增)")
    for _, row in squeeze_stats.iterrows():
        findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                       f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                       f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                       f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                       f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

# Neg funding: stall vs continuation
findings.append("\n### 3.3 极端负费率 Gainer: 停滞 vs 延续结构")
for _, row in tax_neg_stall.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n### 3.4 极端负费率 Loser: 反弹 vs 延续结构")
for _, row in tax_neg_losers.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n## 四、成交量 × 费率 交互效应")
for _, row in tax_vol_fund.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n## 五、前期走势 × 费率 交互效应")
for _, row in tax_runup.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

findings.append("\n## 六、事件聚集 × 费率 交互效应")
for _, row in tax_cluster.iterrows():
    findings.append(f"- **{row['bucket']}** (n={int(row['n'])}): "
                   f"1d={fmt_pct(row['fwd_ret_1d_mean'])}, "
                   f"3d={fmt_pct(row['fwd_ret_3d_mean'])}, "
                   f"5d={fmt_pct(row['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(row['win_rate_5d'])}")

# ── 7c. Determine most interesting bucket ──────────────────────────────────
findings.append("\n## 七、关键发现与推荐")

# Find the best bucket for gainers by 5d mean return
gainer_main = tax_main[tax_main["bucket"].str.startswith("G_")].copy()
if len(gainer_main) > 0:
    best_gainer = gainer_main.loc[gainer_main["fwd_ret_5d_mean"].idxmax()]
    findings.append(f"\n### 最优 Gainer 分桶 (按5d平均收益):")
    findings.append(f"- **{best_gainer['bucket']}**: n={int(best_gainer['n'])}, "
                   f"5d平均={fmt_pct(best_gainer['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(best_gainer['win_rate_5d'])}")

# Find best loser bucket
loser_main = tax_main[tax_main["bucket"].str.startswith("L_")].copy()
if len(loser_main) > 0:
    best_loser = loser_main.loc[loser_main["fwd_ret_5d_mean"].idxmax()]
    findings.append(f"\n### 最优 Loser 分桶 (按5d平均收益):")
    findings.append(f"- **{best_loser['bucket']}**: n={int(best_loser['n'])}, "
                   f"5d平均={fmt_pct(best_loser['fwd_ret_5d_mean'])}, "
                   f"5d胜率={fmt_pct_plain(best_loser['win_rate_5d'])}")

# Neg funding squeeze hypothesis verdict
findings.append("\n### 挤压假设结论")
# Compare neg extreme gainers vs other gainers
g_neg = gainers[gainers["funding_neg_extreme"]]
g_other = gainers[~gainers["funding_neg_extreme"]]
if len(g_neg) > 0 and len(g_other) > 0:
    neg_5d = g_neg["fwd_ret_5d"].mean()
    other_5d = g_other["fwd_ret_5d"].mean()
    findings.append(f"- 极端负费率 Gainer (n={len(g_neg)}): 5d平均={fmt_pct(neg_5d)}")
    findings.append(f"- 其他费率 Gainer (n={len(g_other)}): 5d平均={fmt_pct(other_5d)}")
    if neg_5d > other_5d:
        findings.append("- **结论: 极端负费率 Gainer 确实表现更优，支持挤压假设。**")
    else:
        findings.append("- **结论: 极端负费率 Gainer 并未明显优于其他，挤压假设在日线层面证据不足。**")

# Squeeze candidates
if len(squeeze_df) > 0:
    sq_5d = squeeze_df["fwd_ret_5d"].mean()
    findings.append(f"- 挤压候选事件 (负费率+量增, n={len(squeeze_df)}): 5d平均={fmt_pct(sq_5d)}")

# Final recommendation
findings.append("\n## 八、下一步建议")

# Build recommendation based on data
recommendations = []
if len(gainer_main) > 0:
    top3 = gainer_main.nlargest(3, "fwd_ret_5d_mean")
    for _, row in top3.iterrows():
        if int(row["n"]) >= 20:
            recommendations.append(row["bucket"])

# Also check if any neg-extreme buckets look promising
if len(tax_neg_stall) > 0:
    best_neg = tax_neg_stall.loc[tax_neg_stall["fwd_ret_5d_mean"].idxmax()]
    if best_neg["fwd_ret_5d_mean"] > 0 and int(best_neg["n"]) >= 10:
        recommendations.append(f"{best_neg['bucket']} (neg funding split)")

if len(recommendations) > 0:
    findings.append(f"- 最值得深入研究的分桶: {', '.join(set(recommendations))}")
else:
    findings.append("- 各分桶均无显著 alpha，建议扩展至更细粒度的 1h 数据做进一步验证")

findings.append("- **推荐下一步**: 对最优分桶执行 1h 级别回测，验证日线层面的信号是否在更细粒度上仍然成立")
findings.append("- 最小 1h 跟进建议: 选择 n≥30 且 5d_mean 最高的 1-2 个分桶，提取其事件列表，在 1h k线上计算入场/止损/止盈点位")

# Write findings
with open(OUT / "findings_v1_4.md", "w") as f:
    f.write("\n".join(findings))
print("  Saved findings_v1_4.md")

# ── 8. Manifest ────────────────────────────────────────────────────────────
print("[8/8] Saving manifest...")
manifest = {
    "step": "1.4",
    "version": "v1_4",
    "description": "Daily-side taxonomy of post-event structures with funding/squeeze analysis",
    "created_at": datetime.now().isoformat(),
    "input_artifacts": [
        str(PANEL_PKL),
        str(V1_CSV),
        str(V13_CSV),
    ],
    "output_artifacts": [
        str(OUT / "taxonomy_summary_v1_4.csv"),
        str(OUT / "findings_v1_4.md"),
        str(OUT / "manifest_v1_4.json"),
    ],
    "key_stats": {
        "total_new_events": int(len(new_events)),
        "gainer_events": int((new_events["event_type"] == "top_gainer_1d").sum()),
        "loser_events": int((new_events["event_type"] == "top_loser_1d").sum()),
        "events_with_funding": int(new_events["funding_rate_last"].notna().sum()),
        "squeeze_candidates": int(len(squeeze_df)),
        "n_buckets_main": int(len(tax_main)),
        "funding_neg_extreme_threshold": float(p5_neg),
        "funding_pos_extreme_threshold": float(p95_pos),
    },
}

# Add best bucket recommendation
if len(gainer_main) > 0:
    best = gainer_main.loc[gainer_main["fwd_ret_5d_mean"].idxmax()]
    manifest["best_gainer_bucket"] = {
        "bucket": str(best["bucket"]),
        "n": int(best["n"]),
        "fwd_ret_5d_mean": float(best["fwd_ret_5d_mean"]),
        "win_rate_5d": float(best["win_rate_5d"]),
    }

with open(OUT / "manifest_v1_4.json", "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("  Saved manifest_v1_4.json")

print("\n=== DONE ===")
print(f"Output directory: {OUT}")
print(f"Total buckets in main taxonomy: {len(tax_main)}")
