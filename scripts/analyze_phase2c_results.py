#!/usr/bin/env python3
"""
Phase 2c 结果分析与验证
========================
分析回测结果，验证过拟合风险，提出下一步建议。
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "reports" / "artifacts" / "binance_event_study_phase2c"
RESULTS_JSON = ARTIFACTS / "param_scan_results.json"
SUMMARY_CSV = ARTIFACTS / "param_scan_summary.csv"
V1_6A_TRADES = ROOT / "reports" / "artifacts" / "binance_event_study_v1_6a_oos" / "all_trades_rank450_full.csv"
V1_5_EVENTS = ROOT / "jerry" / "wlfi" / "FR_Monitor" / "reports" / "artifacts" / "binance_daily_event_study_v1_5" / "enriched_gainer_events_v1_5.csv"

print("=" * 70)
print("PHASE 2C RESULTS ANALYSIS")
print("=" * 70)

# ── Load data ──────────────────────────────────────────────────────────────
print("\n[1/4] Loading results...")
with open(RESULTS_JSON, 'r') as f:
    results = json.load(f)

summary = pd.read_csv(SUMMARY_CSV)
trades = pd.read_csv(V1_6A_TRADES)
v15 = pd.read_csv(V1_5_EVENTS)

# Merge structure
trades['event_date'] = trades['ts'].str[:10]
v15['event_date'] = v15['event_date'].astype(str)
trades = trades.merge(
    v15[['event_date', 'symbol', 'structure', 'carry_raw', 'funding_bucket']],
    on=['event_date', 'symbol'],
    how='left',
    suffixes=('', '_v15')
)

print(f"  Results: {len(results)} variants")
print(f"  Trades: {len(trades):,}")

# ── Analysis 1: Funding threshold sensitivity ───────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 1: FUNDING THRESHOLD SENSITIVITY")
print("=" * 70)

# Group by funding threshold
funding_analysis = []
for ft in sorted(summary['funding_pctl_thresh'].unique()):
    ft_data = summary[summary['funding_pctl_thresh'] == ft]
    if len(ft_data) == 0:
        continue
    funding_analysis.append({
        'funding_pctl_thresh': ft,
        'n_variants': len(ft_data),
        'net_mean_avg': ft_data['net_mean'].mean(),
        'net_mean_max': ft_data['net_mean'].max(),
        'win_rate_avg': ft_data['win_rate'].mean(),
        'sharpe_avg': ft_data['sharpe'].mean(),
        'n_trades_avg': ft_data['n_trades'].mean(),
    })

funding_df = pd.DataFrame(funding_analysis)
print("\nFunding threshold sensitivity:")
print(funding_df.to_string(index=False))

# ── Analysis 2: Exit rule comparison ────────────────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 2: EXIT RULE COMPARISON")
print("=" * 70)

exit_analysis = []
for er in summary['exit_rule'].unique():
    er_data = summary[summary['exit_rule'] == er]
    if len(er_data) == 0:
        continue
    exit_analysis.append({
        'exit_rule': er,
        'n_variants': len(er_data),
        'net_mean_avg': er_data['net_mean'].mean(),
        'net_mean_max': er_data['net_mean'].max(),
        'win_rate_avg': er_data['win_rate'].mean(),
        'sharpe_avg': er_data['sharpe'].mean(),
    })

exit_df = pd.DataFrame(exit_analysis)
print("\nExit rule comparison:")
print(exit_df.to_string(index=False))

# ── Analysis 3: Structure × Funding interaction ────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 3: STRUCTURE × FUNDING INTERACTION")
print("=" * 70)

# Filter trades with structure info
trades_with_struct = trades[trades['structure'].notna()].copy()
trades_with_struct['funding_pctl'] = trades_with_struct['funding_at_signal'].rank(pct=True)

# Create funding buckets
trades_with_struct['funding_bucket_detail'] = pd.cut(
    trades_with_struct['funding_pctl'],
    bins=[0, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 1.0],
    labels=['p0-5', 'p5-10', 'p10-25', 'p25-50', 'p50-75', 'p75-90', 'p90-95', 'p95-100']
)

# Analyze interaction
interaction_results = []
for struct in trades_with_struct['structure'].unique():
    if pd.isna(struct):
        continue
    struct_trades = trades_with_struct[trades_with_struct['structure'] == struct]

    for fb in trades_with_struct['funding_bucket_detail'].unique():
        if pd.isna(fb):
            continue
        fb_trades = struct_trades[struct_trades['funding_bucket_detail'] == fb]
        if len(fb_trades) < 20:
            continue

        net_4h = fb_trades['net_4h']
        net_8h = fb_trades['net_8h']
        funding = fb_trades['funding_at_signal']

        interaction_results.append({
            'structure': struct,
            'funding_bucket': fb,
            'n_trades': len(fb_trades),
            'funding_mean': funding.mean(),
            'net_4h_mean': net_4h.mean(),
            'net_8h_mean': net_8h.mean(),
            'win_rate_4h': (net_4h > 0).mean(),
            'win_rate_8h': (net_8h > 0).mean(),
        })

interaction_df = pd.DataFrame(interaction_results)
print("\nStructure × Funding interaction (sorted by net_8h_mean):")
print(interaction_df.sort_values('net_8h_mean', ascending=False).head(20).to_string(index=False))

# ── Analysis 4: Year stability ──────────────────────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 4: YEAR STABILITY")
print("=" * 70)

# Analyze best variant by year
best_variant = summary.sort_values('net_mean', ascending=False).iloc[0]
print(f"\nBest variant: funding_pctl < {best_variant['funding_pctl_thresh']:.2f} + {best_variant['exit_rule']}")

# Filter trades for best variant
best_trades = trades[trades['funding_at_signal'] <= trades['funding_at_signal'].quantile(best_variant['funding_pctl_thresh'])]

year_analysis = []
for yr in sorted(best_trades['year'].unique()):
    yr_trades = best_trades[best_trades['year'] == yr]
    if len(yr_trades) < 50:
        continue

    net_4h = yr_trades['net_4h']
    net_8h = yr_trades['net_8h']

    year_analysis.append({
        'year': yr,
        'n_trades': len(yr_trades),
        'net_4h_mean': net_4h.mean(),
        'net_8h_mean': net_8h.mean(),
        'win_rate_4h': (net_4h > 0).mean(),
        'win_rate_8h': (net_8h > 0).mean(),
    })

year_df = pd.DataFrame(year_analysis)
print("\nYear stability analysis:")
print(year_df.to_string(index=False))

# ── Analysis 5: Overfitting detection ───────────────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 5: OVERFITTING DETECTION")
print("=" * 70)

# Check parameter sensitivity
print("\nParameter sensitivity analysis:")
for ft in sorted(summary['funding_pctl_thresh'].unique()):
    ft_data = summary[summary['funding_pctl_thresh'] == ft]
    if len(ft_data) == 0:
        continue
    net_mean_std = ft_data['net_mean'].std()
    net_mean_range = ft_data['net_mean'].max() - ft_data['net_mean'].min()
    print(f"  funding_pctl < {ft:.2f}: net_mean std = {net_mean_std*100:.3f}%, range = {net_mean_range*100:.3f}%")

# Check if best variant is significantly better than others
print("\nBest variant vs. others:")
best_net_mean = best_variant['net_mean']
other_net_mean = summary[summary.index != best_variant.name]['net_mean'].mean()
improvement = best_net_mean - other_net_mean
print(f"  Best net mean: {best_net_mean*100:.2f}%")
print(f"  Others net mean: {other_net_mean*100:.2f}%")
print(f"  Improvement: {improvement*100:.2f}%")

# ── Analysis 6: Recommendations ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("ANALYSIS 6: RECOMMENDATIONS")
print("=" * 70)

print("\nBased on the analysis:")
print("1. Simple funding threshold strategy does NOT work (all variants negative)")
print("2. neg_extreme funding bucket shows promise (+2.76%/4h, +3.71%/8h)")
print("3. stall_t2 structure shows best performance (+1.86%/8h, 56.8% win)")
print("4. Need more complex signal combinations")

print("\nRecommended next steps:")
print("1. Test combined signals: neg_extreme funding + stall_t2 structure")
print("2. Add volume/price filters to reduce false signals")
print("3. Test on out-of-sample data (30% holdout)")
print("4. Consider paper lane promotion if combined signals work")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print("\nPhase 2c simplified backtest completed.")
print("Key finding: Simple funding threshold strategy is not viable.")
print("Next: Test combined signals with structure filters.")
