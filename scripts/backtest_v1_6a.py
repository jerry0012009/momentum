#!/usr/bin/env python3
"""
v1.6a Momentum Ignition Backtest Engine
=======================================
Phase 1: Detect signals once per signal-param combo, cache them.
Phase 2: For each exit rule, simulate trades from cached signals.
Phase 3: Factor correlation analysis.
Phase 4: Time stability.
"""
import pandas as pd
import numpy as np
import os, time, json
from itertools import product

PANEL = '/root/clawd/jerry/momentum/reports/artifacts/binance_hourly_event_study_v1_6/hourly_event_panel.pkl'
OUT_DIR = '/root/clawd/jerry/momentum/reports/artifacts/binance_event_study_v1_6a'
os.makedirs(OUT_DIR, exist_ok=True)

COST_PER_TRADE = 0.0013  # 0.13% round trip

# ── Load panel ───────────────────────────────────────────────────
print("Loading panel...")
t0 = time.time()
panel = pd.read_pickle(PANEL)
panel = panel.sort_values(['symbol', 'event_date', 'ts']).reset_index(drop=True)
panel['ret_1h'] = panel.groupby(['symbol', 'event_date'])['close'].pct_change()
print(f"  {len(panel):,} rows, {time.time()-t0:.1f}s")

# ── Pre-process: extract arrays per event ────────────────────────
print("Building event arrays...")
t0 = time.time()

event_metas = []   # symbol, event_date, year
event_arrays = []  # dict of numpy arrays

for (sym, ed), ev_data in panel.groupby(['symbol', 'event_date']):
    ev = ev_data.sort_values('ts').reset_index(drop=True)
    n = len(ev)
    if n < 30:
        continue

    rets = ev['ret_1h'].values.astype(np.float64)
    vols = ev['quote_volume'].values.astype(np.float64)

    # Trailing vol means
    s = pd.Series(vols)
    tv12 = s.rolling(12, min_periods=6).mean().values
    tv20 = s.rolling(20, min_periods=10).mean().values

    # Cumulative returns (3h, 6h rolling)
    rs = pd.Series(rets)
    cr3 = ((1 + rs).rolling(3).apply(np.prod, raw=True) - 1).values
    cr6 = ((1 + rs).rolling(6).apply(np.prod, raw=True) - 1).values

    event_metas.append({'symbol': sym, 'event_date': ed, 'year': int(str(ed)[:4])})
    event_arrays.append({
        'hfe': ev['hours_from_event'].values.astype(np.float64),
        'closes': ev['close'].values.astype(np.float64),
        'highs': ev['high'].values.astype(np.float64),
        'lows': ev['low'].values.astype(np.float64),
        'vols': vols, 'rets': rets,
        'funding': ev['funding_rate'].values.astype(np.float64),
        'tbr': ev['taker_buy_ratio'].values.astype(np.float64),
        'tv12': tv12, 'tv20': tv20,
        'cr3': cr3, 'cr6': cr6,
    })

N_EVENTS = len(event_metas)
print(f"  {N_EVENTS} events, {time.time()-t0:.1f}s")

# ── Signal detection (vectorized-ish) ────────────────────────────
def detect_signals(vol_thresh, ret_thresh, vol_window=20,
                   require_ret_accel=False, require_vol_accel=False):
    """Return list of (event_idx, signal_dict) for all events."""
    tv_key = f'tv{vol_window}'
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']
        rets = ev['rets']
        vols = ev['vols']
        tv = ev[tv_key]

        prev_bar = -999
        for i in range(max(vol_window, 2), len(hfe) - 1):
            h = hfe[i]
            if h < -20 or h > 16:
                continue
            if i - prev_bar < 4:
                continue
            if np.isnan(tv[i]) or tv[i] <= 0:
                continue
            vr = vols[i] / tv[i]
            if vr < vol_thresh:
                continue
            if rets[i] < ret_thresh:
                continue
            if require_ret_accel and i >= 1 and rets[i] <= rets[i-1]:
                continue
            if require_vol_accel and i >= 1 and vols[i] <= vols[i-1]:
                continue

            results.append((ei, {
                'bar': i, 'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'vol_ratio': vr,
                'ret_at_signal': rets[i],
                'cumret_3h': 0.0 if np.isnan(ev['cr3'][i]) else ev['cr3'][i],
                'cumret_6h': 0.0 if np.isnan(ev['cr6'][i]) else ev['cr6'][i],
                'tbr_at_signal': ev['tbr'][i],
                'funding_at_signal': ev['funding'][i],
                'vol_at_signal': vols[i],
            }))
            prev_bar = i
    return results


# ── Trade simulation ─────────────────────────────────────────────
def simulate_trade(ev, sig, exit_rule):
    """Simulate one trade. Returns dict."""
    bi = sig['bar']
    ep = sig['entry_price']
    etype = exit_rule['type']
    max_h = exit_rule.get('hold_hours', 8)
    sl = exit_rule.get('sl_pct')
    tp = exit_rule.get('tp_pct')

    cum_ret = 0.0
    cum_fund = 0.0
    exit_reason = 'max_hold'
    exit_bar = bi

    for ho in range(1, max_h + 1):
        bar = bi + ho
        if bar >= len(ev['closes']):
            exit_bar = bar - 1
            exit_reason = 'data_end'
            break

        h_ret = ev['rets'][bar]
        h_fund = ev['funding'][bar]

        # SL check (hourly low)
        if sl is not None:
            if (ev['lows'][bar] / ep) - 1 <= -sl:
                cum_ret += -sl
                cum_fund += h_fund * 0.5
                exit_bar = bar
                exit_reason = 'stop_loss'
                break

        # TP check (hourly high)
        if tp is not None:
            if (ev['highs'][bar] / ep) - 1 >= tp:
                cum_ret += tp
                cum_fund += h_fund * 0.5
                exit_bar = bar
                exit_reason = 'take_profit'
                break

        # Funding flip check
        if etype == 'funding_flip' and h_fund > 0:
            cum_ret = (1 + cum_ret) * (1 + h_ret) - 1
            cum_fund += h_fund
            exit_bar = bar
            exit_reason = 'funding_flip'
            break

        cum_ret = (1 + cum_ret) * (1 + h_ret) - 1
        cum_fund += h_fund
        exit_bar = bar

    total = cum_ret - cum_fund
    return {
        'hold_hours': exit_bar - bi,
        'price_return': cum_ret,
        'funding_sum': cum_fund,
        'total_return': total,
        'net_return': total - COST_PER_TRADE,
        'exit_reason': exit_reason,
    }


# ── Parameter grid ───────────────────────────────────────────────
VOL_THRESHOLDS = [2.0, 3.0, 4.0, 5.0, 7.0]
RET_THRESHOLDS = [0.005, 0.01, 0.02, 0.03, 0.05]
VOL_WINDOWS = [12, 20]

EXIT_RULES = [
    {'type': 'fixed_hold', 'hold_hours': 1, 'label': 'hold_1h'},
    {'type': 'fixed_hold', 'hold_hours': 2, 'label': 'hold_2h'},
    {'type': 'fixed_hold', 'hold_hours': 4, 'label': 'hold_4h'},
    {'type': 'fixed_hold', 'hold_hours': 8, 'label': 'hold_8h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.02, 'label': 'sl_2pct_8h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.03, 'label': 'sl_3pct_8h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.05, 'label': 'sl_5pct_8h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.08, 'label': 'sl_8pct_8h'},
    {'type': 'take_profit', 'hold_hours': 8, 'tp_pct': 0.02, 'label': 'tp_2pct_8h'},
    {'type': 'take_profit', 'hold_hours': 8, 'tp_pct': 0.05, 'label': 'tp_5pct_8h'},
    {'type': 'take_profit', 'hold_hours': 8, 'tp_pct': 0.10, 'label': 'tp_10pct_8h'},
    {'type': 'sl_tp_hold', 'hold_hours': 4, 'sl_pct': 0.03, 'tp_pct': 0.05, 'label': 'sl3_tp5_4h'},
    {'type': 'sl_tp_hold', 'hold_hours': 4, 'sl_pct': 0.05, 'tp_pct': 0.10, 'label': 'sl5_tp10_4h'},
    {'type': 'sl_tp_hold', 'hold_hours': 8, 'sl_pct': 0.03, 'tp_pct': 0.05, 'label': 'sl3_tp5_8h'},
    {'type': 'sl_tp_hold', 'hold_hours': 8, 'sl_pct': 0.05, 'tp_pct': 0.10, 'label': 'sl5_tp10_8h'},
    {'type': 'sl_tp_hold', 'hold_hours': 8, 'sl_pct': 0.05, 'tp_pct': 0.08, 'label': 'sl5_tp8_8h'},
    {'type': 'sl_tp_hold', 'hold_hours': 12, 'sl_pct': 0.05, 'tp_pct': 0.10, 'label': 'sl5_tp10_12h'},
    {'type': 'funding_flip', 'hold_hours': 24, 'label': 'funding_flip'},
]

# ── Main loop: detect signals once, simulate per exit rule ───────
print("\n" + "="*70)
print("RUNNING PARAMETER SCAN")
print("="*70)

all_results = []
sig_combos = list(product(VOL_THRESHOLDS, RET_THRESHOLDS, VOL_WINDOWS))
total = len(sig_combos) * len(EXIT_RULES)
count = 0
t_start = time.time()

for si, (vt, rt, vw) in enumerate(sig_combos):
    # Phase 1: detect signals once
    signals = detect_signals(vt, rt, vw)
    n_sigs = len(signals)

    if n_sigs == 0:
        count += len(EXIT_RULES)
        continue

    # Phase 2: simulate each exit rule
    for er in EXIT_RULES:
        count += 1
        trades = []
        for ei, sig in signals:
            tr = simulate_trade(event_arrays[ei], sig, er)
            tr['trigger_hour'] = sig['trigger_hour']
            tr['vol_ratio'] = sig['vol_ratio']
            tr['ret_at_signal'] = sig['ret_at_signal']
            tr['cumret_3h'] = sig['cumret_3h']
            tr['cumret_6h'] = sig['cumret_6h']
            tr['tbr_at_signal'] = sig['tbr_at_signal']
            tr['funding_at_signal'] = sig['funding_at_signal']
            tr['year'] = event_metas[ei]['year']
            trades.append(tr)

        td = pd.DataFrame(trades)
        net = td['net_return']

        # Skip if too few trades
        if len(trades) < 50:
            continue

        r = {
            'vol_thresh': vt, 'ret_thresh': rt, 'vol_window': vw,
            'exit_rule': er['label'], 'exit_type': er['type'],
            'hold_hours_max': er.get('hold_hours', 0),
            'sl_pct': er.get('sl_pct'), 'tp_pct': er.get('tp_pct'),
            'n_trades': len(trades),
            'price_mean': td['price_return'].mean(),
            'total_mean': td['total_return'].mean(),
            'net_mean': net.mean(),
            'net_std': net.std(),
            'win_rate': (net > 0).mean(),
            'avg_win': net[net > 0].mean() if (net > 0).any() else 0,
            'avg_loss': net[net <= 0].mean() if (net <= 0).any() else 0,
            'profit_factor': abs(net[net > 0].sum() / net[net <= 0].sum()) if net[net <= 0].sum() != 0 else 999,
            'median_hold': td['hold_hours'].median(),
            'pct_sl': (td['exit_reason'] == 'stop_loss').mean(),
            'pct_tp': (td['exit_reason'] == 'take_profit').mean(),
            'pct_max_hold': (td['exit_reason'] == 'max_hold').mean(),
        }

        if net.std() > 0:
            r['sharpe'] = net.mean() / net.std() * np.sqrt(252 * 6)
        else:
            r['sharpe'] = 0

        # Funding split
        neg = td[td['funding_at_signal'] < 0]
        pos = td[td['funding_at_signal'] >= 0]
        if len(neg) >= 10:
            r['neg_fund_n'] = len(neg)
            r['neg_fund_net'] = neg['net_return'].mean()
            r['neg_fund_win'] = (neg['net_return'] > 0).mean()
        if len(pos) >= 10:
            r['pos_fund_n'] = len(pos)
            r['pos_fund_net'] = pos['net_return'].mean()
            r['pos_fund_win'] = (pos['net_return'] > 0).mean()

        # Trigger hour split
        for hlo, hhi in [(-20,-12),(-12,-6),(-6,0),(0,4),(4,8),(8,12),(12,17)]:
            mask = (td['trigger_hour'] >= hlo) & (td['trigger_hour'] < hhi)
            g = td[mask]
            if len(g) >= 10:
                k = f'h{hlo}_{hhi}'
                r[f'{k}_n'] = len(g)
                r[f'{k}_net'] = g['net_return'].mean()
                r[f'{k}_win'] = (g['net_return'] > 0).mean()

        # Yearly
        for yr, yg in td.groupby('year'):
            if len(yg) >= 10:
                r[f'yr{yr}_n'] = len(yg)
                r[f'yr{yr}_net'] = yg['net_return'].mean()
                r[f'yr{yr}_win'] = (yg['net_return'] > 0).mean()

        all_results.append(r)

    elapsed = time.time() - t_start
    rate = count / elapsed if elapsed > 0 else 0
    eta = (len(sig_combos) * len(EXIT_RULES) - count) / rate if rate > 0 else 0
    if (si + 1) % 2 == 0 or si == 0:
        print(f"  sig({vt},{rt},{vw}) signals={n_sigs:>5d} | {count}/{total} done "
              f"({elapsed:.0f}s elapsed, ETA {eta:.0f}s)")

print(f"\nScan complete: {len(all_results)} valid combos in {time.time()-t_start:.0f}s")

# ── Save ─────────────────────────────────────────────────────────
rdf = pd.DataFrame(all_results)
rdf.to_csv(f'{OUT_DIR}/param_scan_results.csv', index=False)
print(f"Saved {OUT_DIR}/param_scan_results.csv")

# ── Top results ──────────────────────────────────────────────────
def show_top(df, sort_col, title, n=20, min_trades=100):
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    sub = df[df['n_trades'] >= min_trades].nlargest(n, sort_col)
    for _, r in sub.iterrows():
        nf = f"neg={r.get('neg_fund_net',0)*100:+.2f}%" if 'neg_fund_net' in r else ""
        print(f"  v>{r.vol_thresh} r>{r.ret_thresh*100:.1f}% w={r.vol_window:>2d} {r.exit_rule:18s} | "
              f"n={r.n_trades:>5d} net={r.net_mean*100:+.3f}% wr={r.win_rate*100:.1f}% "
              f"pf={r.profit_factor:.2f} {nf}")

show_top(rdf, 'net_mean', 'TOP 20 BY NET RETURN')
show_top(rdf, 'win_rate', 'TOP 20 BY WIN RATE')
show_top(rdf, 'profit_factor', 'TOP 20 BY PROFIT FACTOR', min_trades=200)

# ── Signal stability: same signal config, all exit rules ─────────
print(f"\n{'='*70}")
print("SIGNAL STABILITY: vol>3 ret>1% w=20 — all exit rules")
print(f"{'='*70}")
stab = rdf[(rdf['vol_thresh']==3) & (rdf['ret_thresh']==0.01) & (rdf['vol_window']==20)]
stab = stab.sort_values('net_mean', ascending=False)
for _, r in stab.iterrows():
    print(f"  {r.exit_rule:20s}: n={r.n_trades:>5d} net={r.net_mean*100:+.3f}% "
          f"wr={r.win_rate*100:.1f}% pf={r.profit_factor:.2f} sharpe={r.sharpe:.2f}")

# ── Best combo deep dive ─────────────────────────────────────────
if len(rdf) > 0:
    best = rdf[rdf['n_trades']>=100].nlargest(1, 'net_mean').iloc[0]
    print(f"\n{'='*70}")
    print(f"BEST COMBO: v>{best.vol_thresh} r>{best.ret_thresh*100:.1f}% w={best.vol_window} {best.exit_rule}")
    print(f"{'='*70}")
    print(f"  n={best.n_trades} net={best.net_mean*100:+.3f}% wr={best.win_rate*100:.1f}%")
    print(f"  avg_win={best.avg_win*100:+.3f}% avg_loss={best.avg_loss*100:+.3f}% pf={best.profit_factor:.2f}")
    print(f"  sharpe={best.sharpe:.2f}")
    print(f"  exits: SL={best.pct_sl*100:.1f}% TP={best.pct_tp*100:.1f}% hold={best.pct_max_hold*100:.1f}%")

    print(f"\n  By funding:")
    for d in ['neg', 'pos']:
        nk = f'{d}_fund_n'
        if nk in best and best[nk] > 0:
            print(f"    {d}: n={int(best[nk])} net={best[f'{d}_fund_net']*100:+.3f}% wr={best[f'{d}_fund_win']*100:.1f}%")

    print(f"\n  By trigger hour:")
    for hlo, hhi in [(-20,-12),(-12,-6),(-6,0),(0,4),(4,8),(8,12),(12,17)]:
        k = f'h{hlo}_{hhi}'
        nk = f'{k}_n'
        if nk in best and best[nk] > 0:
            print(f"    h=[{hlo:+d},{hhi:+d}): n={int(best[nk])} net={best[f'{k}_net']*100:+.3f}% wr={best[f'{k}_win']*100:.1f}%")

    print(f"\n  By year:")
    for yr in range(2022, 2027):
        nk = f'yr{yr}_n'
        if nk in best and best[nk] > 0:
            print(f"    {yr}: n={int(best[nk])} net={best[f'yr{yr}_net']*100:+.3f}% wr={best[f'yr{yr}_win']*100:.1f}%")

# ── Factor correlation ───────────────────────────────────────────
print(f"\n{'='*70}")
print("FACTOR CORRELATION ANALYSIS")
print(f"{'='*70}")

# Use medium signal config, 4h hold for factor analysis
fac_signals = detect_signals(3.0, 0.01, 20)
fac_trades = []
er4h = {'type': 'fixed_hold', 'hold_hours': 4}
for ei, sig in fac_signals:
    tr = simulate_trade(event_arrays[ei], sig, er4h)
    tr.update({
        'trigger_hour': sig['trigger_hour'],
        'vol_ratio': sig['vol_ratio'],
        'ret_at_signal': sig['ret_at_signal'],
        'cumret_3h': sig['cumret_3h'],
        'cumret_6h': sig['cumret_6h'],
        'tbr_at_signal': sig['tbr_at_signal'],
        'funding_at_signal': sig['funding_at_signal'],
        'vol_at_signal': sig['vol_at_signal'],
    })
    fac_trades.append(tr)

ft = pd.DataFrame(fac_trades)
ft['net'] = ft['total_return'] - COST_PER_TRADE
ft['is_win'] = (ft['net'] > 0).astype(int)

features = ['vol_ratio', 'ret_at_signal', 'cumret_3h', 'cumret_6h',
            'tbr_at_signal', 'funding_at_signal', 'trigger_hour',
            'vol_at_signal']

print(f"\n{len(ft)} trades (vol>3 ret>1% w=20, 4h hold)")
print(f"{'Feature':>20s} {'Corr':>8s}  Quintile returns (Q1→Q5)")
print("-" * 80)

factor_quintiles = {}
for feat in features:
    corr = ft[feat].corr(ft['net'])
    try:
        lo = ft[feat].quantile(0.01)
        hi = ft[feat].quantile(0.99)
        ft[f'{feat}_q'] = pd.qcut(ft[feat].clip(lo, hi), 5, duplicates='drop')
        qm = ft.groupby(f'{feat}_q', observed=True)['net'].mean()
        qs = ' | '.join([f"{v*100:+.2f}%" for v in qm])
        factor_quintiles[feat] = list(qm.values)
    except:
        qs = "N/A"
    print(f"{feat:>20s} {corr:>+8.4f}  {qs}")

# Combined factor scoring
print(f"\n--- Combined factor scoring ---")
ft['funding_score'] = ft['funding_at_signal'].rank(pct=True)  # lower funding = better for longs → invert
ft['vol_score'] = ft['vol_ratio'].rank(pct=True)
ft['ret_score'] = ft['ret_at_signal'].rank(pct=True)
ft['combo_score'] = (1 - ft['funding_score']) * 0.4 + ft['vol_score'] * 0.3 + ft['ret_score'] * 0.3
ft['combo_q'] = pd.qcut(ft['combo_score'], 5, duplicates='drop')
for q, g in ft.groupby('combo_q', observed=True):
    n = g['net']
    print(f"  {q}: n={len(g):>5d} net={n.mean()*100:+.3f}% wr={(n>0).mean()*100:.1f}%")

# ── Save factor data ─────────────────────────────────────────────
ft.drop(columns=[c for c in ft.columns if c.endswith('_q')], errors='ignore').to_csv(
    f'{OUT_DIR}/factor_analysis_trades.csv', index=False)

print(f"\n✓ All done. Results in {OUT_DIR}/")
