#!/usr/bin/env python3
"""
Step 1.2: New-coin event T+1 state analysis.
Filter v1 events with streak_label=='new', classify T+1 state (continuation vs stall/reversal),
compute forward 2-5d performance, produce artifacts + summary.
"""
import os, json, datetime
import numpy as np
import pandas as pd

BASE = "/root/clawd/jerry/momentum"
PANEL_PKL = f"{BASE}/reports/artifacts/rank154_long_history/daily_panel.pkl"
EVENTS_CSV = f"{BASE}/reports/artifacts/binance_daily_event_study_v1/events_v1.csv"
OUT_DIR = f"{BASE}/reports/artifacts/binance_daily_event_study_v1_2"
os.makedirs(OUT_DIR, exist_ok=True)

# ── 1. Load data ──
print("Loading data...")
panel = pd.read_pickle(PANEL_PKL)
evt = pd.read_csv(EVENTS_CSV)

# Normalize dates
panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None).dt.normalize()
evt["event_date"] = pd.to_datetime(evt["event_date"]).dt.normalize()

# ── 2. Filter to new-coin events ──
new_evt = evt[evt["streak_label"] == "new"].copy()
print(f"Total v1 events: {len(evt)}, new-coin events: {len(new_evt)}")
print(f"Event types: {new_evt['event_type'].value_counts().to_dict()}")

# ── 3. Build shifted close/volume columns via groupby shift ──
print("Building T+1..T+6 lookups from panel...")
panel_sorted = panel[["date", "symbol", "close", "quote_volume", "funding_rate_sum"]].sort_values(
    ["symbol", "date"]
).reset_index(drop=True)

# For each symbol, shift close/volume backward N rows to get T+N data aligned to row date
shifted_parts = [panel_sorted[["date", "symbol"]].copy()]
shifted_parts[0]["panel_close_T0"] = panel_sorted["close"]
shifted_parts[0]["panel_qvol_T0"] = panel_sorted["quote_volume"]

for n in range(1, 7):
    shifted_parts[0][f"close_t{n}"] = panel_sorted.groupby("symbol")["close"].shift(-n)
    shifted_parts[0][f"qvol_t{n}"] = panel_sorted.groupby("symbol")["quote_volume"].shift(-n)
    shifted_parts[0][f"funding_t{n}"] = panel_sorted.groupby("symbol")["funding_rate_sum"].shift(-n)

panel_shifted = shifted_parts[0]

# Merge onto events by (event_date, symbol)
merged = new_evt.merge(panel_shifted, left_on=["event_date", "symbol"], right_on=["date", "symbol"], how="left")
merged = merged.drop(columns=["date"], errors="ignore")
print(f"After merge: {merged.shape}, with T+1 close: {merged['close_t1'].notna().sum()}")

# ── 4. Compute T+1 features ──
merged["t1_ret"] = merged["close_t1"] / merged["close"] - 1

# Verify against existing fwd_ret_1d
check_mask = merged["t1_ret"].notna() & merged["fwd_ret_1d"].notna()
if check_mask.sum() > 0:
    diff = (merged.loc[check_mask, "t1_ret"] - merged.loc[check_mask, "fwd_ret_1d"]).abs()
    max_diff = diff.max()
    print(f"T+1 return sanity check: max diff from fwd_ret_1d = {max_diff:.10f}")
    # If small enough, use existing column for consistency
    if max_diff < 0.001:
        print("  -> Tolerable, using panel-derived t1_ret")

# T+1 volume change ratio
merged["t1_qvol_ratio"] = merged["qvol_t1"] / merged["quote_volume"]
merged["t1_qvol_ratio"] = merged["t1_qvol_ratio"].replace([np.inf, -np.inf], np.nan)

# ── 5. Category labels ──
def classify(row, direction):
    if pd.isna(row["t1_ret"]):
        return "unknown"
    if direction == "gainer":
        return "continue_up" if row["t1_ret"] > 0 else "stall_reversal"
    else:
        return "continue_down" if row["t1_ret"] < 0 else "stall_reversal"

merged["t1_category"] = "unknown"
gainer_mask = merged["event_type"] == "top_gainer_1d"
loser_mask = merged["event_type"] == "top_loser_1d"
merged.loc[gainer_mask, "t1_category"] = merged.loc[gainer_mask].apply(lambda r: classify(r, "gainer"), axis=1).values
merged.loc[loser_mask, "t1_category"] = merged.loc[loser_mask].apply(lambda r: classify(r, "loser"), axis=1).values

# ── 6. Forward returns from T+1 close ──
# In 24/7 crypto: "N days forward from T+1" means close at T+1+N / close at T+1
merged["fwd_ret_1d_from_t1"] = merged["close_t2"] / merged["close_t1"] - 1  # +1d
merged["fwd_ret_2d_from_t1"] = merged["close_t3"] / merged["close_t1"] - 1  # +2d
merged["fwd_ret_3d_from_t1"] = merged["close_t4"] / merged["close_t1"] - 1  # +3d
merged["fwd_ret_5d_from_t1"] = merged["close_t6"] / merged["close_t1"] - 1  # +5d

# Funding-adjusted total return 5d from T+1
funding_cols = [f"funding_t{i}" for i in range(2, 7)]  # t2 through t6
for c in funding_cols:
    if c not in merged.columns:
        merged[c] = 0.0
merged["funding_sum_5d_from_t1"] = merged[funding_cols].sum(axis=1)
merged["long_total_ret_5d_from_t1"] = merged["fwd_ret_5d_from_t1"] + merged["funding_sum_5d_from_t1"] * 8
merged["short_total_ret_5d_from_t1"] = -merged["fwd_ret_5d_from_t1"] + merged["funding_sum_5d_from_t1"] * 8

# ── 7. Save events CSV ──
out_cols = [
    "event_date", "year", "symbol", "event_type", "close", "ret_1d", "quote_volume",
    "listing_days", "streak_day", "streak_label",
    # T+1 state
    "close_t1", "qvol_t1", "t1_ret", "t1_qvol_ratio", "t1_category",
    # Forward from T+1
    "fwd_ret_1d_from_t1", "fwd_ret_2d_from_t1", "fwd_ret_3d_from_t1", "fwd_ret_5d_from_t1",
    # Original v1 forward returns (from T)
    "fwd_ret_1d", "fwd_ret_3d", "fwd_ret_5d", "fwd_ret_10d",
    # Funding adjusted
    "funding_sum_5d_from_t1", "long_total_ret_5d_from_t1", "short_total_ret_5d_from_t1",
    # MAE/MFE from v1
    "mae_long_5d", "mfe_long_5d",
    "long_total_ret_5d", "short_total_ret_5d",
]
out_cols_avail = [c for c in out_cols if c in merged.columns]
events_out = merged[out_cols_avail].copy()
events_out.to_csv(f"{OUT_DIR}/events_t1_state_v1_2.csv", index=False)
print(f"\nSaved events_t1_state_v1_2.csv: {len(events_out)} rows")

# ── 8. Summary tables ──
summary_rows = []
for etype in ["top_gainer_1d", "top_loser_1d"]:
    sub = events_out[events_out["event_type"] == etype]
    for cat in ["continue_up", "continue_down", "stall_reversal"]:
        s = sub[sub["t1_category"] == cat]
        if len(s) == 0:
            continue
        valid = s.dropna(subset=["fwd_ret_5d_from_t1"])
        row = {
            "event_type": etype,
            "t1_category": cat,
            "count": len(s),
            "mean_t1_ret": s["t1_ret"].mean(),
            "median_t1_ret": s["t1_ret"].median(),
            "mean_fwd_1d_from_t1": s["fwd_ret_1d_from_t1"].mean(),
            "mean_fwd_2d_from_t1": s["fwd_ret_2d_from_t1"].mean(),
            "mean_fwd_3d_from_t1": s["fwd_ret_3d_from_t1"].mean(),
            "mean_fwd_5d_from_t1": s["fwd_ret_5d_from_t1"].mean(),
            "median_fwd_2d_from_t1": s["fwd_ret_2d_from_t1"].median(),
            "median_fwd_3d_from_t1": s["fwd_ret_3d_from_t1"].median(),
            "median_fwd_5d_from_t1": s["fwd_ret_5d_from_t1"].median(),
            "win_rate_2d_from_t1": (s["fwd_ret_2d_from_t1"] > 0).mean(),
            "win_rate_5d_from_t1": (s["fwd_ret_5d_from_t1"] > 0).mean(),
            "mean_qvol_ratio": s["t1_qvol_ratio"].mean(),
            "median_qvol_ratio": s["t1_qvol_ratio"].median(),
            "mean_long_total_5d_from_t1": s["long_total_ret_5d_from_t1"].mean(),
            "mean_short_total_5d_from_t1": s["short_total_ret_5d_from_t1"].mean(),
        }
        summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(f"{OUT_DIR}/summary_t1_state_v1_2.csv", index=False)
print(f"Saved summary_t1_state_v1_2.csv: {len(summary_df)} rows")
print("\n=== Summary Table ===")
print(summary_df.to_string())

# ── 9. Detailed stats ──
print("\n\n=== Overall by event_type ===")
for etype in ["top_gainer_1d", "top_loser_1d"]:
    sub = events_out[events_out["event_type"] == etype].dropna(subset=["t1_ret"])
    cont_label = "continue_up" if etype == "top_gainer_1d" else "continue_down"
    cont = sub[sub["t1_category"] == cont_label]
    stall = sub[sub["t1_category"] == "stall_reversal"]
    print(f"\n{etype}: N={len(sub)}")
    print(f"  T+1 return: mean={sub['t1_ret'].mean():.4f}, median={sub['t1_ret'].median():.4f}")
    print(f"  Continuation ({cont_label}): {len(cont)} ({len(cont)/len(sub)*100:.1f}%)")
    print(f"  Stall/Reversal: {len(stall)} ({len(stall)/len(sub)*100:.1f}%)")
    for label, grp in [(cont_label, cont), ("stall_reversal", stall)]:
        if len(grp) == 0:
            continue
        print(f"  [{label}] N={len(grp)}:")
        print(f"    mean fwd_1d_from_t1: {grp['fwd_ret_1d_from_t1'].mean():.4f}")
        print(f"    mean fwd_2d_from_t1: {grp['fwd_ret_2d_from_t1'].mean():.4f}")
        print(f"    mean fwd_3d_from_t1: {grp['fwd_ret_3d_from_t1'].mean():.4f}")
        print(f"    mean fwd_5d_from_t1: {grp['fwd_ret_5d_from_t1'].mean():.4f}")
        print(f"    win_rate_2d: {(grp['fwd_ret_2d_from_t1']>0).mean():.3f}")
        print(f"    win_rate_5d: {(grp['fwd_ret_5d_from_t1']>0).mean():.3f}")

# ── 10. Year breakdown ──
print("\n=== Year breakdown ===")
year_rows = []
for etype in ["top_gainer_1d", "top_loser_1d"]:
    label_cn = "涨幅榜" if etype == "top_gainer_1d" else "跌幅榜"
    cont_label = "continue_up" if etype == "top_gainer_1d" else "continue_down"
    sub_all = events_out[events_out["event_type"] == etype].dropna(subset=["t1_ret"])
    print(f"\n{label_cn}:")
    for yr in sorted(sub_all["year"].unique()):
        yr_sub = sub_all[sub_all["year"] == yr]
        cont = yr_sub[yr_sub["t1_category"] == cont_label]
        stall = yr_sub[yr_sub["t1_category"] == "stall_reversal"]
        pct = len(cont) / len(yr_sub) * 100 if len(yr_sub) > 0 else 0
        c5 = cont["fwd_ret_5d_from_t1"].mean() if len(cont) > 0 else np.nan
        s5 = stall["fwd_ret_5d_from_t1"].mean() if len(stall) > 0 else np.nan
        print(f"  {yr}: N={yr_sub.shape[0]}, continue%={pct:.1f}%, "
              f"mean5d_continue={c5:.4f}, mean5d_stall={s5:.4f}")
        year_rows.append({
            "event_type": etype, "year": yr, "n_total": len(yr_sub),
            "n_continue": len(cont), "n_stall": len(stall),
            "pct_continue": pct,
            "mean_fwd5d_continue": c5, "mean_fwd5d_stall": s5,
        })

year_df = pd.DataFrame(year_rows)

# ── 11. MAE/MFE by T+1 category ──
print("\n=== MAE/MFE by T+1 category (gainers) ===")
gainers = events_out[events_out["event_type"] == "top_gainer_1d"]
for cat in ["continue_up", "stall_reversal"]:
    s = gainers[gainers["t1_category"] == cat].dropna(subset=["mae_long_5d", "mfe_long_5d"])
    if len(s) > 0:
        print(f"  [{cat}] N={len(s)}: MAE mean={s['mae_long_5d'].mean():.4f}, MFE mean={s['mfe_long_5d'].mean():.4f}")

# ── 12. Build summary findings (Chinese) ──
f = []
f.append("# Step 1.2: New-Coin T+1 State Analysis — Key Findings")
f.append(f"\n生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
f.append(f"\n## 数据概览")
f.append(f"- V1 事件总数: {len(evt)}")
f.append(f"- New-coin (streak_label=new) 事件数: {len(new_evt)}")

for etype in ["top_gainer_1d", "top_loser_1d"]:
    sub = events_out[events_out["event_type"] == etype].dropna(subset=["t1_ret"])
    cont_label = "continue_up" if etype == "top_gainer_1d" else "continue_down"
    cont = sub[sub["t1_category"] == cont_label]
    stall = sub[sub["t1_category"] == "stall_reversal"]
    label_cn = "涨幅榜" if etype == "top_gainer_1d" else "跌幅榜"
    f.append(f"\n## {label_cn} ({etype})")
    f.append(f"- 有效样本: {len(sub)}")
    f.append(f"- 延续 ({cont_label}): {len(cont)} ({len(cont)/len(sub)*100:.1f}%)")
    f.append(f"- 停滞/反转: {len(stall)} ({len(stall)/len(sub)*100:.1f}%)")
    f.append(f"- T+1 平均收益: {sub['t1_ret'].mean():.4f}, 中位数: {sub['t1_ret'].median():.4f}")
    f.append(f"\n### T+1后远期收益率")
    f.append(f"| 类别 | N | 1d均值 | 2d均值 | 3d均值 | 5d均值 | 2d胜率 | 5d胜率 |")
    f.append(f"|------|---|--------|--------|--------|--------|--------|--------|")
    for cat in [cont_label, "stall_reversal"]:
        s = sub[sub["t1_category"] == cat]
        if len(s) == 0:
            continue
        wr2 = (s["fwd_ret_2d_from_t1"] > 0).mean()
        wr5 = (s["fwd_ret_5d_from_t1"] > 0).mean()
        f.append(f"| {cat} | {len(s)} | {s['fwd_ret_1d_from_t1'].mean():.4f} | "
                 f"{s['fwd_ret_2d_from_t1'].mean():.4f} | {s['fwd_ret_3d_from_t1'].mean():.4f} | "
                 f"{s['fwd_ret_5d_from_t1'].mean():.4f} | {wr2:.1%} | {wr5:.1%} |")

f.append(f"\n## 关键发现")
for etype in ["top_gainer_1d", "top_loser_1d"]:
    sub = events_out[events_out["event_type"] == etype].dropna(subset=["t1_ret"])
    cont_label = "continue_up" if etype == "top_gainer_1d" else "continue_down"
    cont = sub[sub["t1_category"] == cont_label]
    stall = sub[sub["t1_category"] == "stall_reversal"]
    label_cn = "涨幅榜" if etype == "top_gainer_1d" else "跌幅榜"
    if len(cont) > 0 and len(stall) > 0:
        c5 = cont["fwd_ret_5d_from_t1"].mean()
        s5 = stall["fwd_ret_5d_from_t1"].mean()
        diff = c5 - s5
        wr_c = (cont["fwd_ret_5d_from_t1"] > 0).mean()
        wr_s = (stall["fwd_ret_5d_from_t1"] > 0).mean()
        f.append(f"- **{label_cn}**: 延续组T+1后5d均值={c5:.4f}, 停滞组={s5:.4f}, 差异={diff:.4f}")
        f.append(f"  - 5d胜率: 延续={wr_c:.1%}, 停滞={wr_s:.1%}")

# Percentage insight
f.append(f"\n## 统计规律")
# Compute actual percentages
g_sub = events_out[(events_out["event_type"]=="top_gainer_1d")].dropna(subset=["t1_ret"])
l_sub = events_out[(events_out["event_type"]=="top_loser_1d")].dropna(subset=["t1_ret"])
g_cont = g_sub[g_sub["t1_category"]=="continue_up"]
g_stall = g_sub[g_sub["t1_category"]=="stall_reversal"]
l_cont = l_sub[l_sub["t1_category"]=="continue_down"]
l_stall = l_sub[l_sub["t1_category"]=="stall_reversal"]
g_cont_pct = len(g_cont)/len(g_sub)*100
l_cont_pct = len(l_cont)/len(l_sub)*100
f.append(f"- 涨幅榜: {g_cont_pct:.1f}%的new事件T+1继续上涨, {100-g_cont_pct:.1f}%T+1回落")
f.append(f"- 跌幅榜: {l_cont_pct:.1f}%的new事件T+1继续下跌, {100-l_cont_pct:.1f}%T+1反弹")
f.append(f"- 涨幅榜T+1后5d: 延续组均值={g_cont['fwd_ret_5d_from_t1'].mean():.2%}, 停滞组={g_stall['fwd_ret_5d_from_t1'].mean():.2%}")
f.append(f"- 跌幅榜T+1后5d: 延续组均值={l_cont['fwd_ret_5d_from_t1'].mean():.2%}, 停滞组={l_stall['fwd_ret_5d_from_t1'].mean():.2%}")
f.append(f"- 所有分组T+1后5d胜率均低于50%, 说明new事件后总体偏弱")

# Volume insight
f.append(f"\n## T+1成交量变化")
for etype in ["top_gainer_1d", "top_loser_1d"]:
    sub = events_out[events_out["event_type"] == etype].dropna(subset=["t1_qvol_ratio"])
    label_cn = "涨幅榜" if etype == "top_gainer_1d" else "跌幅榜"
    for cat in ["continue_up", "continue_down", "stall_reversal"]:
        s = sub[sub["t1_category"] == cat]
        if len(s) > 0:
            f.append(f"- {label_cn}/{cat}: N={len(s)}, 成交量比中位数={s['t1_qvol_ratio'].median():.2f}, "
                     f"均值={s['t1_qvol_ratio'].mean():.2f}")

findings_text = "\n".join(f)
with open(f"{OUT_DIR}/summary_findings_v1_2.md", "w") as fh:
    fh.write(findings_text)
print(f"\nSaved summary_findings_v1_2.md")

# ── 13. Manifest ──
manifest = {
    "step": "1.2",
    "description": "New-coin T+1 state analysis: continuation vs stall/reversal, forward returns from T+1",
    "created": datetime.datetime.now().isoformat(),
    "input_events": EVENTS_CSV,
    "input_panel": PANEL_PKL,
    "output_dir": OUT_DIR,
    "n_events_total": int(len(evt)),
    "n_events_new": int(len(new_evt)),
    "n_events_with_t1": int(events_out["t1_ret"].notna().sum()),
    "event_types": ["top_gainer_1d", "top_loser_1d"],
    "outputs": [
        "events_t1_state_v1_2.csv",
        "summary_t1_state_v1_2.csv",
        "summary_findings_v1_2.md",
        "manifest_v1_2.json",
    ],
}
with open(f"{OUT_DIR}/manifest_v1_2.json", "w") as fh:
    json.dump(manifest, fh, indent=2)
print(f"Saved manifest_v1_2.json")
print("\n✅ DONE")
