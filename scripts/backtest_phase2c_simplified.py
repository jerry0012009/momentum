#!/usr/bin/env python3
"""
Phase 2c Carry Harvest Backtest (Simplified)
============================================
使用 v1.6a OOS 数据进行简化回测。

核心逻辑：
1. 基于 funding_at_signal 识别极端负 funding 信号
2. 测试不同 funding 阈值和退出规则
3. 分析 funding carry 收益

输出：
- 参数扫描结果 CSV
- 最优信号推荐
"""
import pandas as pd
import numpy as np
import os, time, json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
V1_6A_TRADES = ROOT / "reports" / "artifacts" / "binance_event_study_v1_6a_oos" / "all_trades_rank450_full.csv"
V1_5_EVENTS = ROOT / "jerry" / "wlfi" / "FR_Monitor" / "reports" / "artifacts" / "binance_daily_event_study_v1_5" / "enriched_gainer_events_v1_5.csv"
OUT_DIR = ROOT / "reports" / "artifacts" / "binance_event_study_phase2c"
os.makedirs(OUT_DIR, exist_ok=True)

COST_PER_TRADE = 0.0013  # 0.13% round trip (baseline)

# ── Load data ──────────────────────────────────────────────────────────────
print("=" * 70)
print("PHASE 2C CARRY HARVEST BACKTEST (SIMPLIFIED)")
print("=" * 70)

print("\n[1/3] Loading v1.6a trades...")
t0 = time.time()
trades = pd.read_csv(V1_6A_TRADES)
print(f"  {len(trades):,} trades, {time.time()-t0:.1f}s")

print("\n[2/3] Loading v1.5 event classification...")
v15 = pd.read_csv(V1_5_EVENTS)
v15['event_date'] = v15['event_date'].astype(str)
print(f"  {len(v15):,} events")

# Merge v1.5 structure classification into trades
# First, extract event_date from ts (format: 2022-01-01 00:00:00+00:00)
trades['event_date'] = trades['ts'].str[:10]
trades = trades.merge(
    v15[['event_date', 'symbol', 'structure', 'carry_raw', 'funding_bucket']],
    on=['event_date', 'symbol'],
    how='left',
    suffixes=('', '_v15')
)
print(f"  Merged structure classification: {trades['structure'].notna().sum():,} trades with structure")

print("\n[3/3] Calculating funding percentiles...")
# Calculate funding percentile across all trades
trades['funding_pctl'] = trades['funding_at_signal'].rank(pct=True)
print(f"  Funding percentile range: {trades['funding_pctl'].min():.3f} to {trades['funding_pctl'].max():.3f}")

# ── Signal detection functions ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("RUNNING PARAMETER SCAN")
print("=" * 70)

def scan_funding_threshold(funding_pctl_thresh, exit_rule='net_4h'):
    """
    扫描不同 funding 阈值的收益
    """
    # Filter trades with extreme negative funding
    mask = trades['funding_pctl'] <= funding_pctl_thresh
    filtered = trades[mask]

    if len(filtered) < 50:
        return None

    # Calculate metrics
    net = filtered[exit_rule]
    win_rate = (net > 0).mean()
    sharpe = net.mean() / net.std() * np.sqrt(365 * 24) if net.std() > 0 else 0

    # Year breakdown
    year_stats = {}
    for yr in sorted(filtered['year'].unique()):
        yr_mask = filtered['year'] == yr
        yr_net = net[yr_mask]
        if len(yr_net) >= 10:
            year_stats[int(yr)] = {
                'n': int(yr_mask.sum()),
                'mean': float(yr_net.mean()),
                'win_rate': float((yr_net > 0).mean()),
            }

    # Structure breakdown
    struct_stats = {}
    for struct in filtered['structure'].dropna().unique():
        struct_mask = filtered['structure'] == struct
        struct_net = net[struct_mask]
        if len(struct_net) >= 10:
            struct_stats[struct] = {
                'n': int(struct_mask.sum()),
                'mean': float(struct_net.mean()),
                'win_rate': float((struct_net > 0).mean()),
            }

    return {
        'funding_pctl_thresh': funding_pctl_thresh,
        'exit_rule': exit_rule,
        'n_trades': len(filtered),
        'net_mean': float(net.mean()),
        'net_median': float(net.median()),
        'win_rate': float(win_rate),
        'sharpe': float(sharpe),
        'funding_mean': float(filtered['funding_at_signal'].mean()),
        'vol_ratio_mean': float(filtered['vol_ratio'].mean()),
        'ret_at_signal_mean': float(filtered['ret_at_signal'].mean()),
        'year_stats': year_stats,
        'struct_stats': struct_stats,
    }


# ── Parameter grid ─────────────────────────────────────────────────────────
FUNDING_THRESHOLDS = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
EXIT_RULES = ['net_4h', 'net_8h']

all_results = []
t_start = time.time()

for ft in FUNDING_THRESHOLDS:
    for er in EXIT_RULES:
        result = scan_funding_threshold(ft, er)
        if result:
            all_results.append(result)

print(f"\nScan complete: {len(all_results)} variants, {time.time()-t_start:.1f}s")

# ── Save results ───────────────────────────────────────────────────────────
print("\nSaving results...")

# Save full results as JSON
results_path = OUT_DIR / "param_scan_results.json"
with open(results_path, 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"  Saved: {results_path}")

# Create summary DataFrame
summary_rows = []
for r in all_results:
    summary_rows.append({
        'funding_pctl_thresh': r['funding_pctl_thresh'],
        'exit_rule': r['exit_rule'],
        'n_trades': r['n_trades'],
        'net_mean': r['net_mean'],
        'win_rate': r['win_rate'],
        'sharpe': r['sharpe'],
        'funding_mean': r['funding_mean'],
        'vol_ratio_mean': r['vol_ratio_mean'],
        'ret_at_signal_mean': r['ret_at_signal_mean'],
    })

summary_df = pd.DataFrame(summary_rows)
summary_path = OUT_DIR / "param_scan_summary.csv"
summary_df.to_csv(summary_path, index=False)
print(f"  Saved: {summary_path}")

# Find top variants
print("\n" + "=" * 70)
print("TOP VARIANTS BY NET MEAN")
print("=" * 70)

top_variants = summary_df.sort_values('net_mean', ascending=False).head(10)
for i, row in top_variants.iterrows():
    print(f"\n#{i+1}: funding_pctl < {row['funding_pctl_thresh']:.2f} + {row['exit_rule']}")
    print(f"  Net mean: {row['net_mean']*100:.2f}%")
    print(f"  Win rate: {row['win_rate']*100:.1f}%")
    print(f"  Sharpe: {row['sharpe']:.2f}")
    print(f"  Trades: {row['n_trades']}")
    print(f"  Funding mean: {row['funding_mean']*100:.3f}%")
    print(f"  Vol ratio mean: {row['vol_ratio_mean']:.2f}")
    print(f"  Ret at signal mean: {row['ret_at_signal_mean']*100:.2f}%")

# ── Detailed analysis of best variant ──────────────────────────────────────
print("\n" + "=" * 70)
print("DETAILED ANALYSIS OF BEST VARIANT")
print("=" * 70)

if len(top_variants) > 0:
    best = top_variants.iloc[0]
    best_result = None
    for r in all_results:
        if (r['funding_pctl_thresh'] == best['funding_pctl_thresh'] and
            r['exit_rule'] == best['exit_rule']):
            best_result = r
            break

    if best_result:
        print(f"\nBest variant: funding_pctl < {best['funding_pctl_thresh']:.2f} + {best['exit_rule']}")
        print(f"Net mean: {best['net_mean']*100:.2f}%")
        print(f"Win rate: {best['win_rate']*100:.1f}%")
        print(f"Sharpe: {best['sharpe']:.2f}")
        print(f"Trades: {best['n_trades']}")

        # Year breakdown
        if 'year_stats' in best_result and best_result['year_stats']:
            print("\nYear breakdown:")
            for yr, stats in sorted(best_result['year_stats'].items()):
                print(f"  {yr}: {stats['n']} trades, {stats['mean']*100:.2f}% net, {stats['win_rate']*100:.1f}% win")

        # Structure breakdown
        if 'struct_stats' in best_result and best_result['struct_stats']:
            print("\nStructure breakdown:")
            for struct, stats in best_result['struct_stats'].items():
                print(f"  {struct}: {stats['n']} trades, {stats['mean']*100:.2f}% net, {stats['win_rate']*100:.1f}% win")

# ── Funding carry analysis ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("FUNDING CARRY ANALYSIS")
print("=" * 70)

# Analyze funding carry by funding bucket
funding_buckets = trades['funding_bucket'].dropna().unique()
for bucket in sorted(funding_buckets):
    bucket_trades = trades[trades['funding_bucket'] == bucket]
    if len(bucket_trades) < 50:
        continue

    net_4h = bucket_trades['net_4h']
    net_8h = bucket_trades['net_8h']
    funding = bucket_trades['funding_at_signal']

    print(f"\n{bucket}:")
    print(f"  Trades: {len(bucket_trades)}")
    print(f"  Funding mean: {funding.mean()*100:.3f}%")
    print(f"  Net 4h mean: {net_4h.mean()*100:.2f}%")
    print(f"  Net 8h mean: {net_8h.mean()*100:.2f}%")
    print(f"  Win rate 4h: {(net_4h > 0).mean()*100:.1f}%")
    print(f"  Win rate 8h: {(net_8h > 0).mean()*100:.1f}%")

# ── Structure analysis ──────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("STRUCTURE ANALYSIS")
print("=" * 70)

structures = trades['structure'].dropna().unique()
for struct in sorted(structures):
    struct_trades = trades[trades['structure'] == struct]
    if len(struct_trades) < 50:
        continue

    net_4h = struct_trades['net_4h']
    net_8h = struct_trades['net_8h']
    funding = struct_trades['funding_at_signal']

    print(f"\n{struct}:")
    print(f"  Trades: {len(struct_trades)}")
    print(f"  Funding mean: {funding.mean()*100:.3f}%")
    print(f"  Net 4h mean: {net_4h.mean()*100:.2f}%")
    print(f"  Net 8h mean: {net_8h.mean()*100:.2f}%")
    print(f"  Win rate 4h: {(net_4h > 0).mean()*100:.1f}%")
    print(f"  Win rate 8h: {(net_8h > 0).mean()*100:.1f}%")

print(f"\n{'=' * 70}")
print("NEXT STEPS")
print(f"{'=' * 70}")
print("1. Run build_phase2c_report.py to generate HTML report")
print("2. Review top variants for overfitting")
print("3. Test on out-of-sample data")
print("4. Consider paper lane promotion")
