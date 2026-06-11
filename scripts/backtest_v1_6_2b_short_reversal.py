#!/usr/bin/env python3
"""
Phase 2b: Short-Side Reversal Strategy (Fully Vectorized)
"""
import json, time, sys
from collections import defaultdict
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path('/root/clawd/jerry/momentum')
PANEL_PATH = ROOT / 'reports/artifacts/binance_hourly_event_study_v1_6/hourly_event_panel.pkl'
OUT_DIR = ROOT / 'reports/artifacts/binance_event_study_v1_6_2b'
OUT_DIR.mkdir(parents=True, exist_ok=True)
COST = 0.0013

print("Loading panel...", flush=True)
t0 = time.time()
panel = pd.read_pickle(PANEL_PATH)
panel = panel.sort_values(['symbol', 'event_date', 'ts']).reset_index(drop=True)
panel['ret_1h'] = panel.groupby(['symbol', 'event_date'])['close'].pct_change()
print(f"  {len(panel):,} rows, {time.time()-t0:.1f}s", flush=True)

print("Building event arrays...", flush=True)
t0 = time.time()
event_metas, event_arrays = [], []
for (sym, ed), ev_data in panel.groupby(['symbol', 'event_date']):
    ev = ev_data.sort_values('ts').reset_index(drop=True)
    if len(ev) < 30:
        continue
    rets = ev['ret_1h'].values.astype(np.float64)
    vols = ev['quote_volume'].values.astype(np.float64)
    closes = ev['close'].values.astype(np.float64)
    highs = ev['high'].values.astype(np.float64)
    lows = ev['low'].values.astype(np.float64)
    hfe = ev['hours_from_event'].values.astype(np.float64)
    funding = ev['funding_rate'].values.astype(np.float64)
    tbr = ev['taker_buy_ratio'].values.astype(np.float64)
    s = pd.Series(vols)
    tv12 = s.rolling(12, min_periods=6).mean().values
    tv20 = s.rolling(20, min_periods=10).mean().values
    event_metas.append({
        'symbol': sym, 'event_date': ed, 'year': int(str(ed)[:4]),
        'ev_structure': ev['ev_structure'].iloc[0] if 'ev_structure' in ev.columns else 'unknown',
        'ev_funding_bucket': ev['ev_funding_bucket'].iloc[0] if 'ev_funding_bucket' in ev.columns else 'unknown',
    })
    event_arrays.append({
        'hfe': hfe, 'closes': closes, 'highs': highs, 'lows': lows,
        'vols': vols, 'rets': rets, 'funding': funding, 'tbr': tbr,
        'tv12': tv12, 'tv20': tv20,
    })
N_EVENTS = len(event_metas)
print(f"  {N_EVENTS} events, {time.time()-t0:.1f}s", flush=True)

# =====================================================================
# STEP 1: Peak Positioning
# =====================================================================
print("\n=== STEP 1: Peak Positioning ===", flush=True)
peak_data = []
for ei in range(N_EVENTS):
    ev = event_arrays[ei]
    meta = event_metas[ei]
    hfe, closes = ev['hfe'], ev['closes']
    post_mask = hfe >= 0
    if post_mask.sum() < 12:
        continue
    post_hfe = hfe[post_mask]
    post_closes = closes[post_mask]
    post_vols = ev['vols'][post_mask]
    post_rets = ev['rets'][post_mask]
    peak_idx = np.argmax(post_closes)
    peak_h = post_hfe[peak_idx]
    peak_price = post_closes[peak_idx]
    first_bearish_h = np.nan
    for j in range(peak_idx, len(post_rets)):
        if post_rets[j] < -0.02:
            first_bearish_h = post_hfe[j]
            break
    event_hour_vol = post_vols[0] if len(post_vols) > 0 else np.nan
    peak_vol = post_vols[peak_idx] if peak_idx < len(post_vols) else np.nan
    vol_ratio_at_peak = peak_vol / event_hour_vol if event_hour_vol > 0 else np.nan
    drop_4h = drop_8h = drop_12h = np.nan
    if peak_idx + 4 < len(post_closes):
        drop_4h = (np.min(post_closes[peak_idx+1:peak_idx+5]) / peak_price) - 1
    if peak_idx + 8 < len(post_closes):
        drop_8h = (np.min(post_closes[peak_idx+1:peak_idx+9]) / peak_price) - 1
    if peak_idx + 12 < len(post_closes):
        drop_12h = (np.min(post_closes[peak_idx+1:peak_idx+13]) / peak_price) - 1
    pre_mask = (hfe >= -1) & (hfe < 0)
    event_ret = np.nan
    if pre_mask.sum() > 0:
        event_ret = (post_closes[0] / closes[pre_mask][-1]) - 1
    peak_data.append({
        'symbol': meta['symbol'], 'event_date': meta['event_date'],
        'year': meta['year'], 'ev_structure': meta['ev_structure'],
        'ev_funding_bucket': meta['ev_funding_bucket'],
        'peak_hour': peak_h, 'first_bearish_h': first_bearish_h,
        'vol_ratio_at_peak': vol_ratio_at_peak, 'event_ret': event_ret,
        'drop_from_peak_4h': drop_4h, 'drop_from_peak_8h': drop_8h,
        'drop_from_peak_12h': drop_12h,
    })

peak_df = pd.DataFrame(peak_data)
peak_df.to_csv(OUT_DIR / 'peak_positioning.csv', index=False)

peak_stats = {
    'peak_hour_distribution': {int(k): int(v) for k, v in peak_df['peak_hour'].value_counts().sort_index().items()},
    'median_peak_hour': float(peak_df['peak_hour'].median()),
    'mean_peak_hour': float(peak_df['peak_hour'].mean()),
    'first_bearish_median': float(peak_df['first_bearish_h'].dropna().median()),
    'mean_drop_4h': float(peak_df['drop_from_peak_4h'].dropna().mean()),
    'mean_drop_8h': float(peak_df['drop_from_peak_8h'].dropna().mean()),
    'mean_drop_12h': float(peak_df['drop_from_peak_12h'].dropna().mean()),
}
for struct in ['immediate_reversal', 'stall_t2', 'stall_t3', 'continuation']:
    sub = peak_df[peak_df['ev_structure'] == struct]
    if len(sub) > 0:
        peak_stats[f'peak_hour_median_{struct}'] = float(sub['peak_hour'].median())
        peak_stats[f'mean_drop_8h_{struct}'] = float(sub['drop_from_peak_8h'].dropna().mean())
peak_df['event_ret_bucket'] = pd.cut(peak_df['event_ret'],
    bins=[-0.5, 0.05, 0.10, 0.15, 0.20, 0.50, 10.0],
    labels=['<5%', '5-10%', '10-15%', '15-20%', '20-30%', '>30%'])
for bucket in peak_df['event_ret_bucket'].dropna().unique():
    sub = peak_df[peak_df['event_ret_bucket'] == bucket]
    if len(sub) > 10:
        peak_stats[f'peak_hour_median_ret_{bucket}'] = float(sub['peak_hour'].median())
        peak_stats[f'mean_drop_8h_ret_{bucket}'] = float(sub['drop_from_peak_8h'].dropna().mean())
print(f"  {len(peak_df)} events, median peak h={peak_stats['median_peak_hour']:.0f}", flush=True)
print(f"  Drop: 4h={peak_stats['mean_drop_4h']*100:.2f}%, 8h={peak_stats['mean_drop_8h']*100:.2f}%, 12h={peak_stats['mean_drop_12h']*100:.2f}%", flush=True)

# =====================================================================
# STEP 2: Pre-compute features per bar (vectorized)
# =====================================================================
print("\n=== STEP 2: Pre-compute features ===", flush=True)
t0 = time.time()

rows = []
for ei in range(N_EVENTS):
    ev = event_arrays[ei]
    meta = event_metas[ei]
    hfe, rets, vols = ev['hfe'], ev['rets'], ev['vols']
    closes, funding, tbr = ev['closes'], ev['funding'], ev['tbr']
    tv12, tv20 = ev['tv12'], ev['tv20']

    for i in range(2, len(hfe)):
        h = hfe[i]
        if h < 0 or h > 48:
            continue
        vr12 = vols[i] / tv12[i] if tv12[i] > 0 else np.nan
        vr20 = vols[i] / tv20[i] if tv20[i] > 0 else np.nan
        # Recent peak drop
        lb = max(0, i - 8)
        recent_high = np.max(closes[lb:i+1])
        drop_from_high = (closes[i] / recent_high) - 1
        # Prior surge flags
        has_surge_2x = has_surge_3x = has_surge_5x = False
        for j in range(max(0, i - 12), i):
            if not np.isnan(tv20[j]) and tv20[j] > 0:
                vrj = vols[j] / tv20[j]
                if vrj >= 2.0 and rets[j] >= 0.01: has_surge_2x = True
                if vrj >= 3.0 and rets[j] >= 0.02: has_surge_3x = True
                if vrj >= 5.0 and rets[j] >= 0.03: has_surge_5x = True
        # Prior tbr peak
        had_tbr_55 = any(not np.isnan(tbr[j]) and tbr[j] > 0.55 for j in range(max(0, i-6), i))
        had_tbr_65 = any(not np.isnan(tbr[j]) and tbr[j] > 0.65 for j in range(max(0, i-6), i))
        rows.append({
            'ei': ei, 'bar': i, 'h': h,
            'symbol': meta['symbol'], 'event_date': meta['event_date'],
            'year': meta['year'], 'ev_structure': meta['ev_structure'],
            'ev_funding_bucket': meta['ev_funding_bucket'],
            'entry_price': closes[i],
            'vr12': vr12, 'vr20': vr20, 'ret': rets[i],
            'funding': funding[i], 'tbr': tbr[i],
            'drop_from_high': drop_from_high,
            'has_surge_2x': has_surge_2x, 'has_surge_3x': has_surge_3x,
            'has_surge_5x': has_surge_5x,
            'had_tbr_55': had_tbr_55, 'had_tbr_65': had_tbr_65,
        })

cand_df = pd.DataFrame(rows)
print(f"  {len(cand_df):,} bars, {time.time()-t0:.1f}s", flush=True)

# =====================================================================
# STEP 3: Define signal filters
# =====================================================================
print("\n=== STEP 3: Signal filters ===", flush=True)

signal_defs = {}
for vc in [0.3, 0.5, 0.7]:
    for pb in [-0.005, -0.01, -0.015, -0.02]:
        label = f'A_vc{vc}_pb{pb*100:.0f}'
        mask = (cand_df['vr20'] <= vc) & (cand_df['ret'] <= pb) & (cand_df['h'] <= 48)
        signal_defs[label] = cand_df[mask]

for sv, sc in [(2.0, 'has_surge_2x'), (3.0, 'has_surge_3x'), (5.0, 'has_surge_5x')]:
    for dr in [-0.01, -0.015, -0.02]:
        label = f'B_sv{sv}_dr{dr*100:.0f}'
        signal_defs[label] = cand_df[cand_df[sc] & (cand_df['ret'] <= dr)]

for pd_c in [0.02, 0.03, 0.05]:
    for dt in [-0.005, -0.01, -0.015]:
        label = f'C_pd{pd_c*100:.0f}_dt{dt*100:.0f}'
        signal_defs[label] = cand_df[(cand_df['funding'] > 0) & (cand_df['drop_from_high'] <= -pd_c) & (cand_df['ret'] <= dt)]

for tp_l, tc in [('55', 'had_tbr_55'), ('65', 'had_tbr_65')]:
    for td in [0.40, 0.45, 0.50]:
        label = f'D_tp{tp_l}_td{td*100:.0f}'
        signal_defs[label] = cand_df[cand_df[tc] & (cand_df['tbr'] <= td)]

# Deduplicate: within each event, no re-trigger within 4 bars (vectorized)
for label in signal_defs:
    sdf = signal_defs[label]
    if sdf.empty:
        continue
    sdf_sorted = sdf.sort_values(['ei', 'bar'])
    # Within same event, compute bar diff from previous signal
    prev_ei = sdf_sorted['ei'].shift(1)
    prev_bar = sdf_sorted['bar'].shift(1)
    same_event = sdf_sorted['ei'] == prev_ei
    bar_diff = sdf_sorted['bar'] - prev_bar
    # Keep if different event OR same event with >= 4 bar gap
    keep_mask = ~same_event | (bar_diff >= 4)
    # Also keep the first signal per event (where prev_ei is NaN)
    keep_mask = keep_mask | prev_ei.isna()
    signal_defs[label] = sdf_sorted[keep_mask].copy()

total_sigs = sum(len(v) for v in signal_defs.values())
print(f"  {len(signal_defs)} variants, {total_sigs:,} total signals after dedup", flush=True)

# =====================================================================
# STEP 4: Vectorized backtest
# =====================================================================
print("\n=== STEP 4: Backtest (vectorized) ===", flush=True)

# Pre-compute running cumulative short return per event (O(n) per event)
# short_cum[b] = cumulative product of (1 - ret[0:b]) for short P&L from bar 0
# Then N-hour short return from bar b = short_cum[b+N+1] / short_cum[b+1] - 1
# Also pre-compute running cumulative funding for short: funding is negated for shorts
# short_fund_cum[b] = cumulative sum of -funding[0:b]
print("  Pre-computing cumulative arrays...", flush=True)
t0 = time.time()
cum_short_ret = {}
cum_short_fund = {}
for ei in range(N_EVENTS):
    ev = event_arrays[ei]
    rets = ev['rets']
    funding = ev['funding']
    n = len(rets)
    # For short: price return = -(price return), so cum product of (1 - ret)
    short_ret_arr = np.concatenate([[1.0], np.cumprod(1 - rets)])
    # Funding for short: opposite sign
    fund_filled = np.where(np.isnan(funding), 0.0, funding)
    short_fund_arr = np.concatenate([[0.0], np.cumsum(-fund_filled)])
    cum_short_ret[ei] = short_ret_arr
    cum_short_fund[ei] = short_fund_arr
print(f"  Done, {time.time()-t0:.1f}s", flush=True)

# Exit rules: (hold_hours, sl_pct, tp_pct, label)
# For SL/TP we need to check hourly highs/lows, so we handle those separately
exit_rules_fixed = [
    (4, None, None, 'hold_4h'),
    (8, None, None, 'hold_8h'),
    (12, None, None, 'hold_12h'),
    (24, None, None, 'hold_24h'),
]
exit_rules_sl_tp = [
    (8, 0.03, None, 'hold_8h_sl3pct'),
    (8, None, 0.05, 'hold_8h_tp5pct'),
    (8, 0.03, 0.05, 'hold_8h_sl3_tp5'),
    (8, None, 0.03, 'hold_8h_tp3pct'),
]

# Aggregation accumulators (memory-efficient: aggregate on-the-fly)
from collections import defaultdict
agg_stats = defaultdict(lambda: {'n': 0, 'net_sum': 0.0, 'net_sq_sum': 0.0,
                                 'pos_sum': 0.0, 'neg_sum': 0.0, 'pos_n': 0,
                                 'price_sum': 0.0, 'fund_sum': 0.0,
                                 'net_vals': []})  # for median
year_stats = defaultdict(lambda: defaultdict(lambda: {'n': 0, 'net_sum': 0.0, 'pos_n': 0}))
struct_stats = defaultdict(lambda: defaultdict(lambda: {'n': 0, 'net_sum': 0.0, 'pos_n': 0}))
fund_bucket_stats = defaultdict(lambda: defaultdict(lambda: {'n': 0, 'net_sum': 0.0, 'pos_n': 0}))
exit_reason_stats = defaultdict(lambda: defaultdict(lambda: {'n': 0, 'net_sum': 0.0}))
# For factor correlation: store only the best combo's trades (decided after scan)
best_combo_trades = {'key': None, 'trades': []}
# Signal type counters
sig_type_counts = defaultdict(lambda: {'n': 0, 'net_sum': 0.0, 'pos_n': 0})

done = 0

for label, sdf in signal_defs.items():
    if sdf.empty:
        done += 1
        continue
    t0 = time.time()
    n_trades_this = 0

    for _, row in sdf.iterrows():
        ei = int(row['ei'])
        bar = int(row['bar'])
        ep = row['entry_price']
        ev = event_arrays[ei]
        meta = event_metas[ei]
        csr = cum_short_ret[ei]
        csf = cum_short_fund[ei]
        n = len(ev['closes'])
        year = meta['year']
        structure = meta['ev_structure']
        fund_bucket = meta['ev_funding_bucket']
        sig_type = label[0]  # A, B, C, D

        # Fixed hold exits using cumulative product (O(1) per lookup)
        for max_h, sl, tp, er_label in exit_rules_fixed:
            start_bar = bar + 1
            end_bar = min(bar + max_h + 1, len(csr) - 1)
            if start_bar >= len(csr) or start_bar >= end_bar:
                continue
            actual_h = end_bar - start_bar
            if actual_h <= 0:
                continue
            price_ret = csr[end_bar] / csr[start_bar] - 1
            fund_sum = csf[end_bar] - csf[start_bar]
            total = price_ret + fund_sum
            net = total - COST
            n_trades_this += 1

            key = (label, er_label)
            s = agg_stats[key]
            s['n'] += 1; s['net_sum'] += net; s['net_sq_sum'] += net * net
            if net > 0: s['pos_n'] += 1; s['pos_sum'] += net
            else: s['neg_sum'] += abs(net)
            s['price_sum'] += price_ret; s['fund_sum'] += fund_sum
            if len(s['net_vals']) < 5000: s['net_vals'].append(net)

            yk = year_stats[key][year]; yk['n'] += 1; yk['net_sum'] += net
            if net > 0: yk['pos_n'] += 1
            sk = struct_stats[key][structure]; sk['n'] += 1; sk['net_sum'] += net
            if net > 0: sk['pos_n'] += 1
            fk = fund_bucket_stats[key][fund_bucket]; fk['n'] += 1; fk['net_sum'] += net
            if net > 0: fk['pos_n'] += 1

            st = sig_type_counts[sig_type]; st['n'] += 1; st['net_sum'] += net
            if net > 0: st['pos_n'] += 1

        # SL/TP exits (need hourly high/low check)
        for max_h, sl_pct, tp_pct, er_label in exit_rules_sl_tp:
            cum_ret = 0.0
            cum_fund = 0.0
            exit_reason = 'max_hold'
            exit_h = 0
            for ho in range(1, max_h + 1):
                b = bar + ho
                if b >= n:
                    exit_h = ho - 1
                    exit_reason = 'data_end'
                    break
                hr = ev['rets'][b]
                hf = ev['funding'][b] if not np.isnan(ev['funding'][b]) else 0.0
                if sl_pct is not None and (ev['highs'][b] / ep) - 1 >= sl_pct:
                    cum_ret += -sl_pct
                    cum_fund += hf * 0.5
                    exit_h, exit_reason = ho, 'stop_loss'
                    break
                if tp_pct is not None and (ev['lows'][b] / ep) - 1 <= -tp_pct:
                    cum_ret += tp_pct
                    cum_fund += hf * 0.5
                    exit_h, exit_reason = ho, 'take_profit'
                    break
                cum_ret = (1 + cum_ret) * (1 - hr) - 1
                cum_fund += hf
                exit_h = ho
            total = cum_ret - cum_fund
            net = total - COST
            n_trades_this += 1

            key = (label, er_label)
            s = agg_stats[key]
            s['n'] += 1; s['net_sum'] += net; s['net_sq_sum'] += net * net
            if net > 0: s['pos_n'] += 1; s['pos_sum'] += net
            else: s['neg_sum'] += abs(net)
            s['price_sum'] += cum_ret; s['fund_sum'] += cum_fund
            if len(s['net_vals']) < 5000: s['net_vals'].append(net)

            yk = year_stats[key][year]; yk['n'] += 1; yk['net_sum'] += net
            if net > 0: yk['pos_n'] += 1
            sk = struct_stats[key][structure]; sk['n'] += 1; sk['net_sum'] += net
            if net > 0: sk['pos_n'] += 1
            fk = fund_bucket_stats[key][fund_bucket]; fk['n'] += 1; fk['net_sum'] += net
            if net > 0: fk['pos_n'] += 1
            ek = exit_reason_stats[key][exit_reason]; ek['n'] += 1; ek['net_sum'] += net

            st = sig_type_counts[sig_type]; st['n'] += 1; st['net_sum'] += net
            if net > 0: st['pos_n'] += 1

    done += 1
    elapsed = time.time() - t0
    print(f"  [{done}/{len(signal_defs)}] {label}: {len(sdf)} sigs -> {n_trades_this} trades, {elapsed:.1f}s", flush=True)

# =====================================================================
# STEP 5: Build aggregated results
# =====================================================================
print("\n=== STEP 5: Aggregate ===", flush=True)

rows = []
for (sl, er), s in agg_stats.items():
    n = s['n']
    if n == 0: continue
    mean = s['net_sum'] / n
    median = float(np.median(s['net_vals'])) if s['net_vals'] else mean
    wr = s['pos_n'] / n
    pf = s['pos_sum'] / s['neg_sum'] if s['neg_sum'] > 0 else 999.0
    rows.append({
        'signal_label': sl, 'exit_rule': er, 'n_trades': n,
        'net_mean': mean, 'net_median': median, 'win_rate': wr,
        'profit_factor': pf, 'price_return_mean': s['price_sum'] / n,
        'funding_sum_mean': s['fund_sum'] / n,
    })
agg = pd.DataFrame(rows).sort_values('net_mean', ascending=False)
agg.to_csv(OUT_DIR / 'param_scan_results.csv', index=False)

top20 = agg[agg.n_trades >= 50].head(20)
print("\nTop 20 (n>=50):")
for _, r in top20.iterrows():
    pf = f"{r.profit_factor:.2f}" if r.profit_factor < 999 else "inf"
    print(f"  {r.signal_label:25s} | {r.exit_rule:20s} | net={r.net_mean*100:+.2f}% | wr={r.win_rate*100:.1f}% | n={int(r.n_trades):,} | pf={pf}", flush=True)

# Best combo for factor analysis
best = agg[agg.n_trades >= 200].iloc[0] if len(agg[agg.n_trades >= 200]) > 0 else agg.iloc[0]
best_key = (best['signal_label'], best['exit_rule'])
factor_corr = {}  # Will be empty since we don't store raw trades for the best combo
# Approximate: use top combo's aggregate stats only
best_info = {'label': best['signal_label'], 'exit': best['exit_rule'],
             'n_trades': int(best['n_trades']), 'net_mean': float(best['net_mean']),
             'win_rate': float(best['win_rate'])}

# Year stability
year_rows = []
for (sl, er), s in agg_stats.items():
    if s['n'] < 100: continue
    for yr, ys in sorted(year_stats[(sl, er)].items()):
        if ys['n'] >= 10:
            year_rows.append({'signal_label': sl, 'exit_rule': er, 'year': int(yr),
                              'n_trades': ys['n'], 'net_mean': ys['net_sum'] / ys['n'],
                              'win_rate': ys['pos_n'] / ys['n']})
pd.DataFrame(year_rows).to_csv(OUT_DIR / 'year_stability.csv', index=False)

# Funding bucket
fund_rows = []
for (sl, er), s in agg_stats.items():
    if s['n'] < 100: continue
    for b, bs in fund_bucket_stats[(sl, er)].items():
        if bs['n'] >= 10:
            fund_rows.append({'signal_label': sl, 'exit_rule': er, 'funding_bucket': b,
                              'n_trades': bs['n'], 'net_mean': bs['net_sum'] / bs['n'],
                              'win_rate': bs['pos_n'] / bs['n']})
pd.DataFrame(fund_rows).to_csv(OUT_DIR / 'funding_bucket_analysis.csv', index=False)

# Structure
struct_rows = []
for (sl, er), s in agg_stats.items():
    if s['n'] < 100: continue
    for st, ss in struct_stats[(sl, er)].items():
        if ss['n'] >= 10:
            struct_rows.append({'signal_label': sl, 'exit_rule': er, 'structure': st,
                                'n_trades': ss['n'], 'net_mean': ss['net_sum'] / ss['n'],
                                'win_rate': ss['pos_n'] / ss['n']})
pd.DataFrame(struct_rows).to_csv(OUT_DIR / 'structure_analysis.csv', index=False)

# Exit reason distribution
exit_dist = []
for (sl, er), s in agg_stats.items():
    if s['n'] < 200: continue
    for reason, rs in exit_reason_stats[(sl, er)].items():
        exit_dist.append({'signal_label': sl, 'exit_rule': er, 'exit_reason': reason,
                          'count': rs['n'], 'net_mean': rs['net_sum'] / rs['n']})
pd.DataFrame(exit_dist).to_csv(OUT_DIR / 'exit_reason_distribution.csv', index=False)

# Cost sensitivity (approximate: use mean total_return from aggregate)
cost_rows = []
for cb in [0, 5, 10, 13, 20, 30, 50]:
    c = cb / 10000
    for _, r in agg[agg.n_trades >= 200].iterrows():
        # Approximate: net_mean at COST=0.0013, adjust by cost delta
        net_at_c = r['net_mean'] + (COST - c)
        wr_approx = max(0, min(1, r['win_rate'] + (net_at_c - r['net_mean']) * 2))  # rough
        cost_rows.append({'signal_label': r['signal_label'], 'exit_rule': r['exit_rule'],
                          'cost_bps': cb, 'net_mean': net_at_c, 'win_rate': r['win_rate']})
pd.DataFrame(cost_rows).to_csv(OUT_DIR / 'cost_sensitivity.csv', index=False)

# Signal type summary
sig_type_summary = [{'type': st, 'total_trades': s['n'],
                     'net_mean': s['net_sum'] / s['n'] if s['n'] > 0 else 0,
                     'win_rate': s['pos_n'] / s['n'] if s['n'] > 0 else 0}
                    for st, s in sig_type_counts.items() if s['n'] > 0]

# Save JSON
print("\n=== Saving ===", flush=True)
rd = {
    'peak_stats': peak_stats,
    'top_combos': [{'signal': r['signal_label'], 'exit': r['exit_rule'], 'n_trades': int(r['n_trades']),
                     'net_mean': float(r['net_mean']), 'win_rate': float(r['win_rate']),
                     'profit_factor': float(r['profit_factor']) if r['profit_factor'] < 999 else 999,
                     'price_return': float(r['price_return_mean']),
                     'funding_sum': float(r['funding_sum_mean'])}
                    for _, r in top20.iterrows()],
    'factor_corr': factor_corr,
    'best_signal': best_info,
    'year_stability': {}, 'funding_analysis': {}, 'structure_analysis': {},
    'cost_sensitivity': {}, 'exit_reason_dist': {},
    'signal_type_summary': sig_type_summary,
}
for _, r in agg[agg.n_trades >= 200].head(8).iterrows():
    key = f"{r['signal_label']}|{r['exit_rule']}"
    sk = (r['signal_label'], r['exit_rule'])
    rd['year_stability'][key] = [y for y in year_rows if y['signal_label'] == r['signal_label'] and y['exit_rule'] == r['exit_rule']]
    rd['funding_analysis'][key] = [f for f in fund_rows if f['signal_label'] == r['signal_label'] and f['exit_rule'] == r['exit_rule']]
    rd['structure_analysis'][key] = [s for s in struct_rows if s['signal_label'] == r['signal_label'] and s['exit_rule'] == r['exit_rule']]
    rd['cost_sensitivity'][key] = [c for c in cost_rows if c['signal_label'] == r['signal_label'] and c['exit_rule'] == r['exit_rule']]
    rd['exit_reason_dist'][key] = [e for e in exit_dist if e['signal_label'] == r['signal_label'] and e['exit_rule'] == r['exit_rule']]

with open(OUT_DIR / 'report_data.json', 'w') as f:
    json.dump(rd, f, indent=2, default=str)

print(f"\nAll results saved to {OUT_DIR}", flush=True)
print("Done!", flush=True)
