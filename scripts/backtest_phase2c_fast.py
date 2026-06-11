#!/usr/bin/env python3
"""
Phase 2c Carry Harvest Backtest (Fast Version)
===============================================
使用 hourly event panel 进行快速回测。

核心逻辑：
1. 基于 funding 和结构筛选信号
2. 测试关键参数组合
3. 分析 funding carry 收益

输出：
- 参数扫描结果 JSON
- 参数扫描摘要 CSV
"""
import pandas as pd
import numpy as np
import os, time, json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "artifacts" / "binance_hourly_event_study_v1_6" / "hourly_event_panel.pkl"
OUT_DIR = ROOT / "reports" / "artifacts" / "binance_event_study_phase2c"
os.makedirs(OUT_DIR, exist_ok=True)

COST_PER_TRADE = 0.0013  # 0.13% round trip (baseline)

# ── Load data ──────────────────────────────────────────────────────────────
print("=" * 70)
print("PHASE 2C CARRY HARVEST BACKTEST (FAST)")
print("=" * 70)

print("\n[1/3] Loading hourly event panel...")
t0 = time.time()
panel = pd.read_pickle(PANEL)
print(f"  {len(panel):,} rows, {time.time()-t0:.1f}s")

print("\n[2/3] Preparing data...")
# Filter for event window (h=0 to h=24)
panel = panel[(panel['hours_from_event'] >= 0) & (panel['hours_from_event'] <= 24)]
print(f"  Event window rows: {len(panel):,}")

# Calculate returns
panel['ret_1h'] = panel.groupby(['symbol', 'event_date'])['close'].pct_change()

# Calculate funding percentile per event
panel['funding_pctl'] = panel.groupby('event_date')['funding_rate'].transform(lambda x: x.rank(pct=True))

print("\n[3/3] Running parameter scan...")
t_start = time.time()

# ── Signal detection functions ──────────────────────────────────────────────
def scan_funding_structure(funding_pctl_thresh, structure_filter=None, hold_hours=8):
    """
    扫描不同 funding 阈值和结构过滤的收益
    """
    # Filter by funding percentile
    mask = panel['funding_pctl'] <= funding_pctl_thresh

    # Filter by structure if specified
    if structure_filter:
        mask = mask & (panel['ev_structure'] == structure_filter)

    filtered = panel[mask].copy()

    if len(filtered) < 100:
        return None

    # Calculate forward returns
    # Group by event and calculate cumulative returns
    results = []
    for (sym, ed), group in filtered.groupby(['symbol', 'event_date']):
        group = group.sort_values('hours_from_event')
        if len(group) < hold_hours:
            continue

        # Entry at first signal bar
        entry_idx = group.index[0]
        entry_price = group.loc[entry_idx, 'close']
        entry_funding = group.loc[entry_idx, 'funding_rate']

        # Exit after hold_hours
        exit_idx = group.index[min(hold_hours, len(group)-1)]
        exit_price = group.loc[exit_idx, 'close']

        # Calculate returns
        price_return = (exit_price / entry_price) - 1

        # Calculate funding carry (sum of funding during hold)
        funding_sum = group.loc[entry_idx:exit_idx, 'funding_rate'].sum()

        total_return = price_return + funding_sum
        net_return = total_return - COST_PER_TRADE

        results.append({
            'symbol': sym,
            'event_date': ed,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'price_return': price_return,
            'funding_sum': funding_sum,
            'total_return': total_return,
            'net_return': net_return,
            'funding_at_entry': entry_funding,
            'structure': group.loc[entry_idx, 'ev_structure'],
            'funding_bucket': group.loc[entry_idx, 'ev_funding_bucket'],
            'year': int(str(ed)[:4]),
        })

    if len(results) < 50:
        return None

    td = pd.DataFrame(results)
    net = td['net_return']

    # Year breakdown
    year_stats = {}
    for yr in sorted(td['year'].unique()):
        yr_mask = td['year'] == yr
        yr_net = net[yr_mask]
        if len(yr_net) >= 10:
            year_stats[int(yr)] = {
                'n': int(yr_mask.sum()),
                'mean': float(yr_net.mean()),
                'win_rate': float((yr_net > 0).mean()),
            }

    # Structure breakdown
    struct_stats = {}
    for struct in td['structure'].dropna().unique():
        struct_mask = td['structure'] == struct
        struct_net = net[struct_mask]
        if len(struct_net) >= 10:
            struct_stats[str(struct)] = {
                'n': int(struct_mask.sum()),
                'mean': float(struct_net.mean()),
                'win_rate': float((struct_net > 0).mean()),
            }

    # Funding bucket breakdown
    bucket_stats = {}
    for bucket in td['funding_bucket'].dropna().unique():
        bucket_mask = td['funding_bucket'] == bucket
        bucket_net = net[bucket_mask]
        if len(bucket_net) >= 10:
            bucket_stats[str(bucket)] = {
                'n': int(bucket_mask.sum()),
                'mean': float(bucket_net.mean()),
                'win_rate': float((bucket_net > 0).mean()),
            }

    return {
        'funding_pctl_thresh': funding_pctl_thresh,
        'structure_filter': structure_filter,
        'hold_hours': hold_hours,
        'n_trades': len(net),
        'net_mean': float(net.mean()),
        'net_median': float(net.median()),
        'win_rate': float((net > 0).mean()),
        'sharpe': float(net.mean() / net.std() * np.sqrt(365 * 24)) if net.std() > 0 else 0,
        'funding_mean': float(td['funding_at_entry'].mean()),
        'year_stats': year_stats,
        'struct_stats': struct_stats,
        'bucket_stats': bucket_stats,
    }


# ── Parameter grid ─────────────────────────────────────────────────────────
FUNDING_THRESHOLDS = [0.05, 0.10, 0.20, 0.30, 0.50]
STRUCTURES = [None, 'stall_t2', 'stall_t3', 'continuation', 'immediate_reversal']
HOLD_HOURS = [4, 8, 12, 24]

all_results = []
total_combos = len(FUNDING_THRESHOLDS) * len(STRUCTURES) * len(HOLD_HOURS)
combo_count = 0

for ft in FUNDING_THRESHOLDS:
    for struct in STRUCTURES:
        for hh in HOLD_HOURS:
            combo_count += 1
            result = scan_funding_structure(ft, struct, hh)
            if result:
                all_results.append(result)

            if combo_count % 20 == 0:
                elapsed = time.time() - t_start
                eta = elapsed / combo_count * (total_combos - combo_count)
                print(f"  [{combo_count}/{total_combos}] {elapsed:.0f}s elapsed, {eta:.0f}s remaining")

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
        'structure_filter': r['structure_filter'] if r['structure_filter'] else 'all',
        'hold_hours': r['hold_hours'],
        'n_trades': r['n_trades'],
        'net_mean': r['net_mean'],
        'win_rate': r['win_rate'],
        'sharpe': r['sharpe'],
        'funding_mean': r['funding_mean'],
    })

summary_df = pd.DataFrame(summary_rows)
summary_path = OUT_DIR / "param_scan_summary.csv"
summary_df.to_csv(summary_path, index=False)
print(f"  Saved: {summary_path}")

# Find top variants
print("\n" + "=" * 70)
print("TOP VARIANTS BY NET MEAN")
print("=" * 70)

top_variants = summary_df.sort_values('net_mean', ascending=False).head(15)
for i, row in top_variants.iterrows():
    print(f"\n#{i+1}: funding_pctl < {row['funding_pctl_thresh']:.2f} + {row['structure_filter']} + {row['hold_hours']}h")
    print(f"  Net mean: {row['net_mean']*100:.2f}%")
    print(f"  Win rate: {row['win_rate']*100:.1f}%")
    print(f"  Sharpe: {row['sharpe']:.2f}")
    print(f"  Trades: {row['n_trades']}")
    print(f"  Funding mean: {row['funding_mean']*100:.3f}%")

# ── Detailed analysis of best variant ──────────────────────────────────────
print("\n" + "=" * 70)
print("DETAILED ANALYSIS OF BEST VARIANT")
print("=" * 70)

if len(top_variants) > 0:
    best = top_variants.iloc[0]
    best_result = None
    for r in all_results:
        if (r['funding_pctl_thresh'] == best['funding_pctl_thresh'] and
            (r['structure_filter'] if r['structure_filter'] else 'all') == best['structure_filter'] and
            r['hold_hours'] == best['hold_hours']):
            best_result = r
            break

    if best_result:
        print(f"\nBest variant: funding_pctl < {best['funding_pctl_thresh']:.2f} + {best['structure_filter']} + {best['hold_hours']}h")
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

        # Funding bucket breakdown
        if 'bucket_stats' in best_result and best_result['bucket_stats']:
            print("\nFunding bucket breakdown:")
            for bucket, stats in best_result['bucket_stats'].items():
                print(f"  {bucket}: {stats['n']} trades, {stats['mean']*100:.2f}% net, {stats['win_rate']*100:.1f}% win")

print(f"\n{'=' * 70}")
print("NEXT STEPS")
print(f"{'=' * 70}")
print("1. Run build_phase2c_report.py to generate HTML report")
print("2. Review top variants for overfitting")
print("3. Test on out-of-sample data")
print("4. Consider paper lane promotion")
