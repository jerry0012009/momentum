import pandas as pd
import numpy as np
from pathlib import Path

df = pd.read_csv("reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv")
print(f"Total trades: {len(df)}")
print(f"Years: {sorted(df['year'].unique())}")
print()

trail_cols = [c for c in df.columns if 'trail' in c.lower()]
print(f"Trail columns: {trail_cols}")
print()

# ---- Strategy comparison ----
strategies = {}

# Trail 3%
s = df[df["trail_3pct_ret"].notna()]
strategies["trail_3pct"] = {
    "n": len(s),
    "mean": s["trail_3pct_ret"].mean(),
    "median": s["trail_3pct_ret"].median(),
    "win_rate": (s["trail_3pct_ret"] > 0).mean(),
    "pf": s.loc[s["trail_3pct_ret"] > 0, "trail_3pct_ret"].sum() / abs(s.loc[s["trail_3pct_ret"] <= 0, "trail_3pct_ret"].sum()),
    "type_counts": s["trail_3pct_type"].value_counts().to_dict(),
}

# TP5 SL3
s = df[df["tp5_sl3_ret"].notna()]
strategies["tp5_sl3"] = {
    "n": len(s),
    "mean": s["tp5_sl3_ret"].mean(),
    "median": s["tp5_sl3_ret"].median(),
    "win_rate": (s["tp5_sl3_ret"] > 0).mean(),
    "pf": s.loc[s["tp5_sl3_ret"] > 0, "tp5_sl3_ret"].sum() / abs(s.loc[s["tp5_sl3_ret"] <= 0, "tp5_sl3_ret"].sum()),
    "type_counts": s["tp5_sl3_type"].value_counts().to_dict(),
}

# TP3 SL2
s = df[df["tp3_sl2_ret"].notna()]
strategies["tp3_sl2"] = {
    "n": len(s),
    "mean": s["tp3_sl2_ret"].mean(),
    "median": s["tp3_sl2_ret"].median(),
    "win_rate": (s["tp3_sl2_ret"] > 0).mean(),
    "pf": s.loc[s["tp3_sl2_ret"] > 0, "tp3_sl2_ret"].sum() / abs(s.loc[s["tp3_sl2_ret"] <= 0, "tp3_sl2_ret"].sum()),
    "type_counts": s["tp3_sl2_type"].value_counts().to_dict(),
}

# TP8 SL3
s = df[df["tp8_sl3_ret"].notna()]
strategies["tp8_sl3"] = {
    "n": len(s),
    "mean": s["tp8_sl3_ret"].mean(),
    "median": s["tp8_sl3_ret"].median(),
    "win_rate": (s["tp8_sl3_ret"] > 0).mean(),
    "pf": s.loc[s["tp8_sl3_ret"] > 0, "tp8_sl3_ret"].sum() / abs(s.loc[s["tp8_sl3_ret"] <= 0, "tp8_sl3_ret"].sum()),
    "type_counts": s["tp8_sl3_type"].value_counts().to_dict(),
}

# Fixed 4h
s = df[df["fixed_4h_ret"].notna()]
denom = abs(s.loc[s["fixed_4h_ret"] <= 0, "fixed_4h_ret"].sum())
strategies["fixed_4h"] = {
    "n": len(s),
    "mean": s["fixed_4h_ret"].mean(),
    "median": s["fixed_4h_ret"].median(),
    "win_rate": (s["fixed_4h_ret"] > 0).mean(),
    "pf": s.loc[s["fixed_4h_ret"] > 0, "fixed_4h_ret"].sum() / denom if denom > 0 else float('inf'),
}

print("=" * 90)
print(f"{'Strategy':<15} {'N':>5} {'Mean%':>7} {'Median%':>8} {'WinRate':>8} {'PF':>6}  Exit Types")
print("=" * 90)
for name, d in strategies.items():
    tc = ", ".join(f"{k}:{v}" for k, v in d.get("type_counts", {}).items())
    print(f"{name:<15} {d['n']:>5} {d['mean']*100:>6.2f}% {d['median']*100:>7.2f}% {d['win_rate']*100:>6.1f}% {d['pf']:>6.2f}  {tc}")

print()
print("=" * 90)
print("RETURN DISTRIBUTION: trail_3pct")
print("=" * 90)
s = df[df["trail_3pct_ret"].notna()]
print(f"  < -3%: {(s['trail_3pct_ret'] < -0.03).sum()} ({(s['trail_3pct_ret'] < -0.03).mean()*100:.1f}%)")
print(f"  -3% to 0%: {((s['trail_3pct_ret'] >= -0.03) & (s['trail_3pct_ret'] < 0)).sum()} ({((s['trail_3pct_ret'] >= -0.03) & (s['trail_3pct_ret'] < 0)).mean()*100:.1f}%)")
print(f"  0% to 3%: {((s['trail_3pct_ret'] >= 0) & (s['trail_3pct_ret'] < 0.03)).sum()} ({((s['trail_3pct_ret'] >= 0) & (s['trail_3pct_ret'] < 0.03)).mean()*100:.1f}%)")
print(f"  > 3%: {(s['trail_3pct_ret'] >= 0.03).sum()} ({(s['trail_3pct_ret'] >= 0.03).mean()*100:.1f}%)")

print()
print("=" * 90)
print("YEARLY BREAKDOWN: trail_3pct")
print("=" * 90)
for yr in sorted(s['year'].unique()):
    sy = s[s['year'] == yr]
    wr = (sy['trail_3pct_ret'] > 0).mean()
    print(f"  {yr}: n={len(sy)}, mean={sy['trail_3pct_ret'].mean()*100:.2f}%, median={sy['trail_3pct_ret'].median()*100:.2f}%, win_rate={wr*100:.1f}%")

print()
print("=" * 90)
print("EXIT TYPE BREAKDOWN: trail_3pct")
print("=" * 90)
for t in s['trail_3pct_type'].unique():
    st = s[s['trail_3pct_type'] == t]
    print(f"  {t}: n={len(st)}, mean={st['trail_3pct_ret'].mean()*100:.2f}%, median={st['trail_3pct_ret'].median()*100:.2f}%, win_rate={(st['trail_3pct_ret']>0).mean()*100:.1f}%")

print()
print("=" * 90)
print("HOLD TIME vs RETURN: trail_3pct")
print("=" * 90)
hold_groups = s.groupby("trail_3pct_hold")["trail_3pct_ret"].agg(["count", "mean", "median"])
hold_groups["win_rate"] = s.groupby("trail_3pct_hold")["trail_3pct_ret"].apply(lambda x: (x > 0).mean())
print(hold_groups.to_string())
