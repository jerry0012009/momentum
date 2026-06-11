#!/usr/bin/env python3
"""Stability analysis for SL-only strategy.

Tests:
1. Slippage sensitivity (0, 10, 20, 30, 50, 80 bps)
2. Time stability (year-by-year, half-year-by-half-year)
3. Parameter stability (small perturbations around SL=8%, timeout=96h)
"""

import glob
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from collections import defaultdict

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'

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
            candle_cache[sym] = {
                'open_time': df['open_time'].values,
                'high': df['high'].values.astype(float),
                'low': df['low'].values.astype(float),
                'close': df['close'].values.astype(float),
            }
    print(f'Loaded {len(valid):,} trades, {len(candle_cache)} symbols')
    return valid, candle_cache

def find_bar_idx(open_times, target_ts_ms):
    idx = np.searchsorted(open_times, target_ts_ms, side='left')
    return int(idx) if idx < len(open_times) else None

def sim_sl_only(c, idx, px, sl_pct, timeout, fee_rate):
    highs, lows, closes = c['high'], c['low'], c['close']
    end = min(idx + timeout, len(closes))
    sl_px = px * (1 - sl_pct)
    for i in range(idx, end):
        if lows[i] <= sl_px:
            return -sl_pct
    ret = (closes[end-1] - px) / px
    return ret

def compute_stats(rets, fee_rate):
    if not rets:
        return None
    # Apply fees
    nets = np.array([(1 + r) * (1 - fee_rate)**2 - 1 for r in rets])
    wins = nets[nets > 0].sum()
    losses = -nets[nets < 0].sum()
    pf = float(wins / losses) if losses > 0 else float('inf')
    return {
        'n': len(nets),
        'mean': float(np.mean(nets) * 100),
        'median': float(np.median(nets) * 100),
        'wr': float(np.mean(nets > 0) * 100),
        'pf': pf,
        'p10': float(np.percentile(nets, 10) * 100),
        'p90': float(np.percentile(nets, 90) * 100),
        'total': float(np.sum(nets) * 100),
    }


def main():
    valid, candle_cache = load_data()

    # Pre-compute entries with timestamps
    print('Pre-computing entries...')
    entries = []
    for _, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        c = candle_cache[sym]
        entry_ts_ms = int(row['signal_ts'].timestamp() * 1000)
        idx = find_bar_idx(c['open_time'], entry_ts_ms)
        if idx is None:
            continue
        idx += 1
        if idx >= len(c['close']):
            continue
        entries.append({
            'sym': sym, 'idx': idx, 'px': float(row['entry_price']),
            'ts': row['signal_ts'],
        })
    print(f'Valid entries: {len(entries)}')

    # ── Part 1: Slippage sensitivity ──
    print('\n' + '='*120)
    print('PART 1: SLIPPAGE SENSITIVITY — SL=8%, Timeout=96h, LONG only')
    print('='*120)
    print(f'{"Slippage":>10s}  {"Fee Rate":>10s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"Total":>10s}  {"P10":>8s}  {"P90":>8s}')
    print('-'*120)

    for slip_bps in [0, 10, 20, 30, 50, 80, 100, 150]:
        fee = (4.0 + slip_bps) / 10000.0  # base fee + slippage
        rets = []
        for e in entries:
            c = candle_cache[e['sym']]
            ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
            rets.append(ret)
        s = compute_stats(rets, fee)
        if s:
            print(f'{slip_bps:>8d}bp  {fee*10000:>8.0f}bp  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["median"]:>+7.2f}%  {s["wr"]:>5.1f}%  {s["pf"]:>5.2f}  {s["total"]:>+9.1f}%  {s["p10"]:>+7.2f}%  {s["p90"]:>+7.2f}%')

    # ── Part 2: Time stability ──
    print('\n' + '='*120)
    print('PART 2: TIME STABILITY — SL=8%, Timeout=96h, LONG only, 4bp fee')
    print('='*120)
    fee = 4.0 / 10000.0

    # By year
    print('\n  By Year:')
    print(f'  {"Year":>6s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"Total":>10s}')
    print(f'  {"-"*70}')
    years = sorted(set(e['ts'].year for e in entries))
    for yr in years:
        subset = [e for e in entries if e['ts'].year == yr]
        rets = []
        for e in subset:
            c = candle_cache[e['sym']]
            ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
            rets.append(ret)
        s = compute_stats(rets, fee)
        if s:
            print(f'  {yr:>6d}  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["median"]:>+7.2f}%  {s["wr"]:>5.1f}%  {s["pf"]:>5.2f}  {s["total"]:>+9.1f}%')

    # By half-year
    print('\n  By Half-Year:')
    print(f'  {"Period":>12s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"Total":>10s}')
    print(f'  {"-"*70}')
    half_years = sorted(set(
        f'{e["ts"].year}-H{1 if e["ts"].month <= 6 else 2}'
        for e in entries
    ))
    for hy in half_years:
        yr, h = hy.split('-H')
        yr = int(yr)
        h = int(h)
        subset = [e for e in entries if e['ts'].year == yr and ((e['ts'].month <= 6) if h == 1 else (e['ts'].month > 6))]
        rets = []
        for e in subset:
            c = candle_cache[e['sym']]
            ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
            rets.append(ret)
        s = compute_stats(rets, fee)
        if s:
            print(f'  {hy:>12s}  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["median"]:>+7.2f}%  {s["wr"]:>5.1f}%  {s["pf"]:>5.2f}  {s["total"]:>+9.1f}%')

    # By quarter
    print('\n  By Quarter:')
    print(f'  {"Quarter":>10s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"Total":>10s}')
    print(f'  {"-"*70}')
    quarters = sorted(set(
        f'{e["ts"].year}-Q{(e["ts"].month-1)//3+1}'
        for e in entries
    ))
    for q in quarters:
        yr, qn = q.split('-Q')
        yr, qn = int(yr), int(qn)
        m_start = (qn - 1) * 3 + 1
        m_end = m_start + 2
        subset = [e for e in entries if e['ts'].year == yr and m_start <= e['ts'].month <= m_end]
        rets = []
        for e in subset:
            c = candle_cache[e['sym']]
            ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
            rets.append(ret)
        s = compute_stats(rets, fee)
        if s:
            print(f'  {q:>10s}  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["median"]:>+7.2f}%  {s["wr"]:>5.1f}%  {s["pf"]:>5.2f}  {s["total"]:>+9.1f}%')

    # ── Part 3: Parameter stability ──
    print('\n' + '='*120)
    print('PART 3: PARAMETER STABILITY — Small perturbations around SL=8%, Timeout=96h')
    print('='*120)
    print(f'{"SL":>6s}  {"Timeout":>8s}  {"N":>5s}  {"Mean":>8s}  {"Median":>8s}  {"WR":>6s}  {"PF":>6s}  {"Total":>10s}  {"P10":>8s}  {"P90":>8s}')
    print('-'*120)

    # Fine-grained SL sweep around 8%
    for sl in [0.04, 0.05, 0.06, 0.07, 0.075, 0.08, 0.085, 0.09, 0.10, 0.11, 0.12]:
        for timeout in [48, 72, 84, 96, 108, 120, 144, 168]:
            rets = []
            for e in entries:
                c = candle_cache[e['sym']]
                ret = sim_sl_only(c, e['idx'], e['px'], sl, timeout, fee)
                rets.append(ret)
            s = compute_stats(rets, fee)
            if s:
                print(f'{sl*100:>5.1f}%  {timeout:>7d}h  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["median"]:>+7.2f}%  {s["wr"]:>5.1f}%  {s["pf"]:>5.2f}  {s["total"]:>+9.1f}%  {s["p10"]:>+7.2f}%  {s["p90"]:>+7.2f}%')

    # ── Part 4: Slippage × Time interaction ──
    print('\n' + '='*120)
    print('PART 4: SLIPPAGE × TIME — SL=8%, Timeout=96h, by Year + Slippage')
    print('='*120)
    print(f'{"Year":>6s}  {"Slip":>6s}  {"N":>5s}  {"Mean":>8s}  {"PF":>6s}  {"WR":>6s}  {"Total":>10s}')
    print('-'*100)
    for yr in years:
        for slip_bps in [0, 20, 50, 80]:
            fee = (4.0 + slip_bps) / 10000.0
            subset = [e for e in entries if e['ts'].year == yr]
            rets = []
            for e in subset:
                c = candle_cache[e['sym']]
                ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
                rets.append(ret)
            s = compute_stats(rets, fee)
            if s:
                print(f'{yr:>6d}  {slip_bps:>4d}bp  {s["n"]:>5d}  {s["mean"]:>+7.2f}%  {s["pf"]:>5.2f}  {s["wr"]:>5.1f}%  {s["total"]:>+9.1f}%')

    # ── Part 5: Maximum consecutive losses ──
    print('\n' + '='*120)
    print('PART 5: RISK METRICS — SL=8%, Timeout=96h, various slippage levels')
    print('='*120)
    for slip_bps in [0, 20, 50, 80]:
        fee = (4.0 + slip_bps) / 10000.0
        rets = []
        for e in entries:
            c = candle_cache[e['sym']]
            ret = sim_sl_only(c, e['idx'], e['px'], 0.08, 96, fee)
            net = (1 + ret) * (1 - fee)**2 - 1
            rets.append(net)
        rets = np.array(rets)

        # Max consecutive losses
        max_streak = 0
        cur_streak = 0
        for r in rets:
            if r < 0:
                cur_streak += 1
                max_streak = max(max_streak, cur_streak)
            else:
                cur_streak = 0

        # Max drawdown (cumulative)
        cum = np.cumsum(rets)
        peak = np.maximum.accumulate(cum)
        dd = cum - peak
        max_dd = float(np.min(dd))

        # Sharpe-like (per-trade)
        sharpe = float(np.mean(rets) / np.std(rets)) if np.std(rets) > 0 else 0

        # Kelly fraction
        win_rate = np.mean(rets > 0)
        avg_win = np.mean(rets[rets > 0]) if np.any(rets > 0) else 0
        avg_loss = -np.mean(rets[rets < 0]) if np.any(rets < 0) else 0
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win if avg_win > 0 else 0

        print(f'\n  Slippage={slip_bps}bp (fee={fee*10000:.0f}bp):')
        print(f'    Max consecutive losses: {max_streak}')
        print(f'    Cumulative drawdown:    {max_dd*100:+.1f}%')
        print(f'    Per-trade Sharpe:       {sharpe:.3f}')
        print(f'    Kelly fraction:         {kelly:.2%}')
        print(f'    Avg win:                {avg_win*100:+.2f}%')
        print(f'    Avg loss:               {-avg_loss*100:+.2f}%')


if __name__ == '__main__':
    main()
