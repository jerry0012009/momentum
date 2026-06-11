#!/usr/bin/env python3
"""Backtest LONG vs SHORT with NO future function exit methods.

Exit methods tested (all set at entry time, no HWM, no trailing):
1. Fixed holding period: exit at close after T hours
2. Fixed TP/SL: exit when TP or SL price is reached (limit orders)
3. Fixed TP only (no SL): exit at target or timeout
4. Fixed SL only (no TP): exit at stop or timeout

All methods use bar high/low only to check if a LIMIT ORDER price was reached.
This is standard and honest - in live trading you'd place limit orders at these prices.
"""

import glob
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'

FEE_RATE = 4.0 / 10000.0  # 4bps each side


def load_data():
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()
    print(f'Loaded {len(valid):,} valid trades')

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
            candle_cache[sym] = df

    print(f'Loaded candles for {len(candle_cache)} symbols')
    return valid, candle_cache


def find_bar_idx(candles, target_ts_ms):
    mask = candles['open_time'] >= target_ts_ms
    if mask.any():
        return mask.idxmax()
    return None


# ── Exit methods (NO future function) ────────────────────────────────

def exit_fixed_hold(candles, entry_idx, entry_px, direction, hold_bars):
    """Exit at close after hold_bars hours. Simplest possible exit."""
    exit_idx = min(entry_idx + hold_bars, len(candles) - 1)
    exit_px = float(candles.iloc[exit_idx]['close'])
    if direction == 'long':
        return (exit_px - entry_px) / entry_px, exit_idx, 'timeout'
    else:
        return (entry_px - exit_px) / entry_px, exit_idx, 'timeout'


def exit_fixed_tp_sl(candles, entry_idx, entry_px, direction, tp_pct, sl_pct, max_hold=48):
    """Fixed TP/SL from entry. Uses limit orders - no future function.

    TP and SL prices are set at entry time.
    Checks bar high/low to see if limit orders would have been filled.
    Conservative: if both TP and SL hit in same bar, assumes SL first.
    """
    if direction == 'long':
        tp_px = entry_px * (1 + tp_pct)
        sl_px = entry_px * (1 - sl_pct)
        for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
            bar = candles.iloc[i]
            low = float(bar['low'])
            high = float(bar['high'])
            if low <= sl_px:
                return -sl_pct, i, 'stop_loss'
            if high >= tp_px:
                return tp_pct, i, 'take_profit'
        exit_idx = min(entry_idx + max_hold, len(candles) - 1)
        exit_px = float(candles.iloc[exit_idx]['close'])
        return (exit_px - entry_px) / entry_px, exit_idx, 'timeout'
    else:  # short
        tp_px = entry_px * (1 - tp_pct)  # price goes down = profit for short
        sl_px = entry_px * (1 + sl_pct)  # price goes up = loss for short
        for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
            bar = candles.iloc[i]
            low = float(bar['low'])
            high = float(bar['high'])
            if high >= sl_px:
                return -sl_pct, i, 'stop_loss'
            if low <= tp_px:
                return tp_pct, i, 'take_profit'
        exit_idx = min(entry_idx + max_hold, len(candles) - 1)
        exit_px = float(candles.iloc[exit_idx]['close'])
        return (entry_px - exit_px) / entry_px, exit_idx, 'timeout'


def exit_sl_only(candles, entry_idx, entry_px, direction, sl_pct, max_hold=48):
    """Fixed SL from entry, exit at close after max_hold if not stopped out."""
    if direction == 'long':
        sl_px = entry_px * (1 - sl_pct)
        for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
            bar = candles.iloc[i]
            if float(bar['low']) <= sl_px:
                return -sl_pct, i, 'stop_loss'
        exit_idx = min(entry_idx + max_hold, len(candles) - 1)
        exit_px = float(candles.iloc[exit_idx]['close'])
        return (exit_px - entry_px) / entry_px, exit_idx, 'timeout'
    else:
        sl_px = entry_px * (1 + sl_pct)
        for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
            bar = candles.iloc[i]
            if float(bar['high']) >= sl_px:
                return -sl_pct, i, 'stop_loss'
        exit_idx = min(entry_idx + max_hold, len(candles) - 1)
        exit_px = float(candles.iloc[exit_idx]['close'])
        return (entry_px - exit_px) / entry_px, exit_idx, 'timeout'


# ── Run backtest ─────────────────────────────────────────────────────

def run_backtest(valid, candle_cache, sim_fn, **kwargs):
    rets = []
    reasons = {}
    for _, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        candles = candle_cache[sym]
        entry_ts = row['signal_ts']
        entry_ts_ms = int(entry_ts.timestamp() * 1000)
        entry_px = float(row['entry_price'])
        idx = find_bar_idx(candles, entry_ts_ms)
        if idx is None:
            continue
        idx += 1  # lag 1h
        if idx >= len(candles):
            continue
        ret, _, reason = sim_fn(candles, idx, entry_px, **kwargs)
        if ret is not None:
            net = (1 + ret) * (1 - FEE_RATE)**2 - 1
            rets.append(net)
            reasons[reason] = reasons.get(reason, 0) + 1
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
        'reasons': reasons,
    }


def fmt(r):
    if r is None:
        return 'N/A'
    return f'n={r["n"]:>4d}  mean={r["mean"]:>+6.2f}%  med={r["median"]:>+6.2f}%  WR={r["wr"]:>5.1f}%  PF={r["pf"]:>5.2f}'


def main():
    valid, candle_cache = load_data()

    print('\n' + '='*100)
    print('NO-FUTURE-FUNCTION BACKTEST: LONG vs SHORT')
    print('='*100)

    # ── 1. Fixed holding period ──
    print('\n━━━ 1. Fixed Holding Period (exit at close after T hours) ━━━')
    print(f'{"":>20s}  {"LONG":>55s}  {"SHORT":>55s}')
    print(f'{"Hold":>20s}  {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}    {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}')
    print('-'*140)
    for hold in [1, 2, 4, 8, 12, 24, 48]:
        lr = run_backtest(valid, candle_cache, exit_fixed_hold, direction='long', hold_bars=hold)
        sr = run_backtest(valid, candle_cache, exit_fixed_hold, direction='short', hold_bars=hold)
        l = f'{lr["n"]:>5d} {lr["mean"]:>+7.2f}% {lr["median"]:>+7.2f}% {lr["wr"]:>5.1f}% {lr["pf"]:>5.2f}' if lr else 'N/A'
        s = f'{sr["n"]:>5d} {sr["mean"]:>+7.2f}% {sr["median"]:>+7.2f}% {sr["wr"]:>5.1f}% {sr["pf"]:>5.2f}' if sr else 'N/A'
        print(f'{hold:>17d}h  {l}    {s}')

    # ── 2. Fixed TP/SL ──
    print('\n━━━ 2. Fixed TP/SL (limit orders at entry, max 48h) ━━━')
    print(f'{"":>20s}  {"LONG":>55s}  {"SHORT":>55s}')
    print(f'{"TP/SL":>20s}  {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}    {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}')
    print('-'*140)
    for tp, sl in [(0.02, 0.02), (0.03, 0.02), (0.05, 0.03), (0.03, 0.03), (0.05, 0.05),
                   (0.02, 0.01), (0.03, 0.01), (0.05, 0.02), (0.08, 0.03), (0.10, 0.05)]:
        lr = run_backtest(valid, candle_cache, exit_fixed_tp_sl, direction='long', tp_pct=tp, sl_pct=sl)
        sr = run_backtest(valid, candle_cache, exit_fixed_tp_sl, direction='short', tp_pct=tp, sl_pct=sl)
        l = f'{lr["n"]:>5d} {lr["mean"]:>+7.2f}% {lr["median"]:>+7.2f}% {lr["wr"]:>5.1f}% {lr["pf"]:>5.2f}' if lr else 'N/A'
        s = f'{sr["n"]:>5d} {sr["mean"]:>+7.2f}% {sr["median"]:>+7.2f}% {sr["wr"]:>5.1f}% {sr["pf"]:>5.2f}' if sr else 'N/A'
        print(f'TP{tp*100:.0f}/SL{sl*100:.0f}{"":>14s}  {l}    {s}')

    # ── 3. SL only (no TP, timeout at 48h) ──
    print('\n━━━ 3. SL Only (no TP, exit at close after 48h if not stopped) ━━━')
    print(f'{"":>20s}  {"LONG":>55s}  {"SHORT":>55s}')
    print(f'{"SL":>20s}  {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}    {"N":>5s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}')
    print('-'*140)
    for sl in [0.01, 0.02, 0.03, 0.05, 0.08, 0.10]:
        lr = run_backtest(valid, candle_cache, exit_sl_only, direction='long', sl_pct=sl)
        sr = run_backtest(valid, candle_cache, exit_sl_only, direction='short', sl_pct=sl)
        l = f'{lr["n"]:>5d} {lr["mean"]:>+7.2f}% {lr["median"]:>+7.2f}% {lr["wr"]:>5.1f}% {lr["pf"]:>5.2f}' if lr else 'N/A'
        s = f'{sr["n"]:>5d} {sr["mean"]:>+7.2f}% {sr["median"]:>+7.2f}% {sr["wr"]:>5.1f}% {sr["pf"]:>5.2f}' if sr else 'N/A'
        print(f'SL{sl*100:.0f}%{"":>16s}  {l}    {s}')

    # ── Summary: best configs per method ──
    print('\n' + '='*100)
    print('SUMMARY: Best config per method (by median return)')
    print('='*100)
    print(f'{"Method":>30s}  {"Direction":>8s}  {"Config":>12s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"N":>5s}')
    print('-'*85)

    bests = []

    # Best fixed hold
    for d in ['long', 'short']:
        for hold in [1, 2, 4, 8, 12, 24, 48]:
            r = run_backtest(valid, candle_cache, exit_fixed_hold, direction=d, hold_bars=hold)
            if r:
                bests.append(('Fixed Hold', d, f'{hold}h', r['median'], r['wr'], r['pf'], r['n']))
    bests.sort(key=lambda x: x[3], reverse=True)
    for b in bests[:6]:
        print(f'{b[0]:>30s}  {b[1]:>8s}  {b[2]:>12s}  {b[3]:>+7.2f}%  {b[4]:>5.1f}%  {b[5]:>5.2f}  {b[6]:>5d}')

    print()

    # Best TP/SL
    tpsl_bests = []
    for d in ['long', 'short']:
        for tp, sl in [(0.02, 0.02), (0.03, 0.02), (0.05, 0.03), (0.03, 0.03), (0.05, 0.05),
                       (0.02, 0.01), (0.03, 0.01), (0.05, 0.02), (0.08, 0.03), (0.10, 0.05)]:
            r = run_backtest(valid, candle_cache, exit_fixed_tp_sl, direction=d, tp_pct=tp, sl_pct=sl)
            if r:
                tpsl_bests.append(('Fixed TP/SL', d, f'TP{tp*100:.0f}/SL{sl*100:.0f}', r['median'], r['wr'], r['pf'], r['n']))
    tpsl_bests.sort(key=lambda x: x[3], reverse=True)
    for b in tpsl_bests[:6]:
        print(f'{b[0]:>30s}  {b[1]:>8s}  {b[2]:>12s}  {b[3]:>+7.2f}%  {b[4]:>5.1f}%  {b[5]:>5.2f}  {b[6]:>5d}')

    print()

    # Direction comparison
    print('\n' + '='*100)
    print('DIRECTION COMPARISON: Is the market biased LONG or SHORT after events?')
    print('='*100)

    # Use fixed hold as the cleanest measure
    for hold in [4, 8, 24, 48]:
        lr = run_backtest(valid, candle_cache, exit_fixed_hold, direction='long', hold_bars=hold)
        sr = run_backtest(valid, candle_cache, exit_fixed_hold, direction='short', hold_bars=hold)
        if lr and sr:
            diff = lr['median'] - sr['median']
            bias = 'LONG' if diff > 0 else 'SHORT'
            print(f'Fixed {hold}h: LONG median={lr["median"]:+.2f}%, SHORT median={sr["median"]:+.2f}%, diff={diff:+.2f}pp → bias={bias}')


if __name__ == '__main__':
    main()
