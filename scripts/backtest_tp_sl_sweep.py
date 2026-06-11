#!/usr/bin/env python3
"""Optimized TP/SL sweep with smaller grid and batched processing."""

import glob
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import sys

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
FEE_RATE = 4.0 / 10000.0

def load_data():
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()
    symbols = valid['symbol'].unique()
    candle_cache = {}
    for sym in sorted(symbols):
        sym_dir = CACHE_DIR / sym
        files = sorted(glob.glob(str(sym_dir / f'{sym}-1h-*.zip')))
        if not files:
            continue
        frames = []
        for f in files:
            try:
                with zipfile.ZipFile(f) as zf:
                    names = [n for n in zf.namelist() if n.endswith('.csv')]
                    if not names:
                        continue
                    with zf.open(names[0]) as fh:
                        df = pd.read_csv(fh, usecols=[0,1,2,3,4,5])
                        frames.append(df)
            except Exception:
                continue
        if frames:
            df = pd.concat(frames, ignore_index=True)
            df['open_time'] = pd.to_numeric(df['open_time'], errors='coerce')
            df = df.dropna(subset=['open_time']).sort_values('open_time').reset_index(drop=True)
            # Convert to numpy for speed
            candle_cache[sym] = {
                'open_time': df['open_time'].values,
                'open': df['open'].values.astype(float),
                'high': df['high'].values.astype(float),
                'low': df['low'].values.astype(float),
                'close': df['close'].values.astype(float),
            }
    print(f'Loaded {len(valid):,} trades, {len(candle_cache)} symbols')
    return valid, candle_cache

def find_bar_idx_fast(open_times, target_ts_ms):
    idx = np.searchsorted(open_times, target_ts_ms, side='left')
    if idx < len(open_times):
        return int(idx)
    return None

def sim_tp_sl_fast(highs, lows, closes, entry_idx, entry_px, direction, tp_pct, sl_pct, max_hold=48):
    """Vectorized-ish TP/SL simulation."""
    end = min(entry_idx + max_hold, len(highs))
    if direction == 'long':
        tp_px = entry_px * (1 + tp_pct)
        sl_px = entry_px * (1 - sl_pct)
        for i in range(entry_idx, end):
            if lows[i] <= sl_px:
                return -sl_pct
            if highs[i] >= tp_px:
                return tp_pct
        exit_px = closes[end - 1]
        return (exit_px - entry_px) / entry_px
    else:
        tp_px = entry_px * (1 - tp_pct)
        sl_px = entry_px * (1 + sl_pct)
        for i in range(entry_idx, end):
            if highs[i] >= sl_px:
                return -sl_pct
            if lows[i] <= tp_px:
                return tp_pct
        exit_px = closes[end - 1]
        return (entry_px - exit_px) / entry_px

def sim_fixed_hold_fast(closes, entry_idx, entry_px, direction, hold_bars):
    exit_idx = min(entry_idx + hold_bars, len(closes) - 1)
    exit_px = closes[exit_idx]
    if direction == 'long':
        return (exit_px - entry_px) / entry_px
    else:
        return (entry_px - exit_px) / entry_px

def run_bt(valid, candle_cache, sim_fn, **kwargs):
    rets = []
    for _, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        c = candle_cache[sym]
        entry_ts_ms = int(row['signal_ts'].timestamp() * 1000)
        entry_px = float(row['entry_price'])
        idx = find_bar_idx_fast(c['open_time'], entry_ts_ms)
        if idx is None:
            continue
        idx += 1
        if idx >= len(c['close']):
            continue
        ret = sim_fn(c, idx, entry_px, **kwargs)
        if ret is not None:
            net = (1 + ret) * (1 - FEE_RATE)**2 - 1
            rets.append(net)
    if not rets:
        return None
    rets = np.array(rets)
    wins = rets[rets > 0].sum()
    losses = -rets[rets < 0].sum()
    pf = float(wins / losses) if losses > 0 else float('inf')
    return {
        'n': len(rets),
        'mean': float(np.mean(rets) * 100),
        'median': float(np.median(rets) * 100),
        'wr': float(np.mean(rets > 0) * 100),
        'pf': pf,
        'p10': float(np.percentile(rets, 10) * 100),
        'p25': float(np.percentile(rets, 25) * 100),
        'p75': float(np.percentile(rets, 75) * 100),
        'p90': float(np.percentile(rets, 90) * 100),
    }


def main():
    valid, candle_cache = load_data()

    # Pre-compute entry data for speed
    print('Pre-computing entry points...')
    entries = []
    for _, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        c = candle_cache[sym]
        entry_ts_ms = int(row['signal_ts'].timestamp() * 1000)
        idx = find_bar_idx_fast(c['open_time'], entry_ts_ms)
        if idx is None:
            continue
        idx += 1
        if idx >= len(c['close']):
            continue
        entries.append({
            'sym': sym,
            'idx': idx,
            'px': float(row['entry_price']),
        })
    print(f'Valid entries: {len(entries)}')

    # ── Part 1: Fixed hold ──
    print('\n' + '='*120)
    print('PART 1: Fixed Holding Period — Mean vs Median')
    print('='*120)
    print(f'{"Hold":>6s}  {"Dir":>6s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"P10":>8s}  {"P25":>8s}  {"P75":>8s}  {"P90":>8s}')
    print('-'*120)
    for hold in [1, 2, 4, 8, 12, 24, 48]:
        for d in ['long', 'short']:
            rets = []
            for e in entries:
                c = candle_cache[e['sym']]
                ret = sim_fixed_hold_fast(c['close'], e['idx'], e['px'], d, hold)
                net = (1 + ret) * (1 - FEE_RATE)**2 - 1
                rets.append(net)
            rets = np.array(rets)
            wins = rets[rets > 0].sum()
            losses = -rets[rets < 0].sum()
            pf = float(wins / losses) if losses > 0 else float('inf')
            print(f'{hold:>5d}h  {d:>6s}  {len(rets):>5d}  {np.mean(rets)*100:>+7.2f}%  {np.median(rets)*100:>+7.2f}%  {np.mean(rets>0)*100:>5.1f}%  {pf:>5.2f}  {np.percentile(rets,10)*100:>+7.2f}%  {np.percentile(rets,25)*100:>+7.2f}%  {np.percentile(rets,75)*100:>+7.2f}%  {np.percentile(rets,90)*100:>+7.2f}%')

    # ── Part 2: TP/SL grid (coarser) ──
    print('\n' + '='*120)
    print('PART 2: TP/SL Grid')
    print('='*120)

    tp_vals = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20]
    sl_vals = [0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30]

    for d in ['long', 'short']:
        # Collect all grid results
        grid = []
        total_combos = len(tp_vals) * len(sl_vals)
        done = 0
        for tp in tp_vals:
            for sl in sl_vals:
                done += 1
                rets = []
                for e in entries:
                    c = candle_cache[e['sym']]
                    ret = sim_tp_sl_fast(c['high'], c['low'], c['close'], e['idx'], e['px'], d, tp, sl)
                    net = (1 + ret) * (1 - FEE_RATE)**2 - 1
                    rets.append(net)
                rets = np.array(rets)
                wins = rets[rets > 0].sum()
                losses = -rets[rets < 0].sum()
                pf = float(wins / losses) if losses > 0 else float('inf')
                r = {
                    'tp': tp, 'sl': sl,
                    'n': len(rets),
                    'mean': float(np.mean(rets) * 100),
                    'median': float(np.median(rets) * 100),
                    'wr': float(np.mean(rets > 0) * 100),
                    'pf': pf,
                    'p10': float(np.percentile(rets, 10) * 100),
                    'p90': float(np.percentile(rets, 90) * 100),
                }
                grid.append(r)
                sys.stderr.write(f'\r  {d.upper()}: {done}/{total_combos}  TP{tp*100:.0f}/SL{sl*100:.0f} mean={r["mean"]:+.2f}%')
                sys.stderr.flush()
        print(f'\r{" " * 80}')

        # Top 15 by mean
        grid.sort(key=lambda x: x['mean'], reverse=True)
        print(f'\n  {d.upper()} — Top 15 by Mean:')
        print(f'  {"TP":>5s}  {"SL":>5s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"P10":>8s}  {"P90":>8s}')
        for g in grid[:15]:
            tag = ' ***' if g['mean'] > 0 and g['pf'] > 1.0 else ''
            print(f'  {g["tp"]*100:>4.0f}%  {g["sl"]*100:>4.0f}%  {g["n"]:>5d}  {g["mean"]:>+7.2f}%  {g["median"]:>+7.2f}%  {g["wr"]:>5.1f}%  {g["pf"]:>5.2f}  {g["p10"]:>+7.2f}%  {g["p90"]:>+7.2f}%{tag}')

        # Mean return heatmap
        print(f'\n  {d.upper()} Mean Return Heatmap (rows=TP, cols=SL):')
        print(f'  {"":>6s}', end='')
        for sl in sl_vals:
            print(f'  SL{sl*100:.0f}%', end='')
        print()
        for tp in tp_vals:
            print(f'  TP{tp*100:.0f}%', end='')
            for sl in sl_vals:
                g = [x for x in grid if x['tp'] == tp and x['sl'] == sl][0]
                val = g['mean']
                if val > 0:
                    print(f'  \033[92m{val:>+5.1f}\033[0m', end='')
                else:
                    print(f'  \033[91m{val:>+5.1f}\033[0m', end='')
            print()

    # ── Part 3: Asymmetric focus ──
    print('\n' + '='*120)
    print('PART 3: Asymmetric — Wide SL + Narrow TP (survive dip, capture mean reversion)')
    print('='*120)

    asym_configs = [
        (0.01, 0.05), (0.01, 0.08), (0.01, 0.10), (0.01, 0.15), (0.01, 0.20), (0.01, 0.30),
        (0.02, 0.05), (0.02, 0.08), (0.02, 0.10), (0.02, 0.15), (0.02, 0.20), (0.02, 0.30),
        (0.03, 0.08), (0.03, 0.10), (0.03, 0.15), (0.03, 0.20), (0.03, 0.30),
        (0.05, 0.10), (0.05, 0.15), (0.05, 0.20), (0.05, 0.30),
        # Also narrow SL + wide TP (the other direction)
        (0.10, 0.02), (0.10, 0.03), (0.15, 0.03), (0.15, 0.05), (0.20, 0.05),
    ]

    for d in ['long', 'short']:
        print(f'\n  {d.upper()}:')
        print(f'  {"TP":>5s}  {"SL":>5s}  {"Ratio":>7s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"P10":>8s}  {"P90":>8s}  {"Note"}')
        print(f'  {"-"*100}')
        results_asym = []
        for tp, sl in asym_configs:
            rets = []
            for e in entries:
                c = candle_cache[e['sym']]
                ret = sim_tp_sl_fast(c['high'], c['low'], c['close'], e['idx'], e['px'], d, tp, sl)
                net = (1 + ret) * (1 - FEE_RATE)**2 - 1
                rets.append(net)
            rets = np.array(rets)
            wins = rets[rets > 0].sum()
            losses = -rets[rets < 0].sum()
            pf = float(wins / losses) if losses > 0 else float('inf')
            ratio = sl / tp if tp > 0 else 999
            r = {'tp': tp, 'sl': sl, 'mean': float(np.mean(rets)*100), 'median': float(np.median(rets)*100),
                 'wr': float(np.mean(rets>0)*100), 'pf': pf, 'p10': float(np.percentile(rets,10)*100),
                 'p90': float(np.percentile(rets,90)*100), 'n': len(rets), 'ratio': ratio}
            results_asym.append(r)
            tag = ' ★★' if r['mean'] > 0 and r['pf'] > 1.2 else (' ★' if r['mean'] > 0 and r['pf'] > 1 else '')
            print(f'  {tp*100:>4.0f}%  {sl*100:>4.0f}%  {ratio:>6.1f}x  {r["n"]:>5d}  {r["mean"]:>+7.2f}%  {r["median"]:>+7.2f}%  {r["wr"]:>5.1f}%  {r["pf"]:>5.2f}  {r["p10"]:>+7.2f}%  {r["p90"]:>+7.2f}%{tag}')

    # ── Part 4: SL-only with long timeouts ──
    print('\n' + '='*120)
    print('PART 4: SL Only — Long Timeout (trailing/take-profit = pure hold with stop-loss floor)')
    print('='*120)
    print(f'{"SL":>5s}  {"Timeout":>8s}  {"Dir":>6s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"P10":>8s}  {"P90":>8s}')
    print('-'*100)

    for d in ['long', 'short']:
        for sl in [0.03, 0.05, 0.08, 0.10, 0.15, 0.20]:
            for timeout in [12, 24, 48, 72, 96]:
                rets = []
                for e in entries:
                    c = candle_cache[e['sym']]
                    highs, lows, closes = c['high'], c['low'], c['close']
                    idx, px = e['idx'], e['px']
                    end = min(idx + timeout, len(closes))
                    if d == 'long':
                        sl_px = px * (1 - sl)
                        hit_sl = False
                        for i in range(idx, end):
                            if lows[i] <= sl_px:
                                net = (1 + (-sl)) * (1 - FEE_RATE)**2 - 1
                                rets.append(net)
                                hit_sl = True
                                break
                        if not hit_sl:
                            ret = (closes[end-1] - px) / px
                            net = (1 + ret) * (1 - FEE_RATE)**2 - 1
                            rets.append(net)
                    else:
                        sl_px = px * (1 + sl)
                        hit_sl = False
                        for i in range(idx, end):
                            if highs[i] >= sl_px:
                                net = (1 + (-sl)) * (1 - FEE_RATE)**2 - 1
                                rets.append(net)
                                hit_sl = True
                                break
                        if not hit_sl:
                            ret = (px - closes[end-1]) / px
                            net = (1 + ret) * (1 - FEE_RATE)**2 - 1
                            rets.append(net)
                rets = np.array(rets)
                wins = rets[rets > 0].sum()
                losses = -rets[rets < 0].sum()
                pf = float(wins / losses) if losses > 0 else float('inf')
                mean_r = np.mean(rets) * 100
                tag = ' ★★' if mean_r > 0 and pf > 1.2 else (' ★' if mean_r > 0 and pf > 1 else '')
                print(f'{sl*100:>4.0f}%  {timeout:>7d}h  {d:>6s}  {len(rets):>5d}  {mean_r:>+7.2f}%  {np.median(rets)*100:>+7.2f}%  {np.mean(rets>0)*100:>5.1f}%  {pf:>5.2f}  {np.percentile(rets,10)*100:>+7.2f}%  {np.percentile(rets,90)*100:>+7.2f}%{tag}')


if __name__ == '__main__':
    main()
