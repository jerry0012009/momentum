#!/usr/bin/env python3
"""Backtest SHORT version of Event+V4 trailing stop strategy.

Logic:
- Same event signal (momentum ignition detection)
- Same V4 entry signal
- But SHORT instead of LONG
- Trailing stop follows price DOWN (LWM = lowest price seen)
- Exit when price rises back by trail_pct from the LWM
"""

import csv
import glob
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'

FEE_BPS = 4.0
FEE_RATE = FEE_BPS / 10000.0

def load_data():
    """Load trades and candle cache."""
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    trades['event_ts'] = pd.to_datetime(trades['event_ts'], utc=True)
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()
    print(f'Loaded {len(trades):,} trades, {len(valid):,} valid')

    symbols = valid['symbol'].unique()
    print(f'Loading candles for {len(symbols)} symbols...')
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
    """Find the bar index closest to (but >=) target timestamp."""
    mask = candles['open_time'] >= target_ts_ms
    if mask.any():
        return mask.idxmax()
    return None


def sim_long_trail(candles, entry_idx, entry_px, trail_pct, max_hold=48):
    """Long trailing stop (baseline for comparison)."""
    hwm = entry_px
    for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
        bar = candles.iloc[i]
        high = float(bar['high'])
        low = float(bar['low'])

        if high > hwm:
            hwm = high

        trail_stop = hwm * (1 - trail_pct)

        if low <= trail_stop:
            exit_px = trail_stop
            gross_ret = (exit_px - entry_px) / entry_px
            return gross_ret, i, "trailing_stop"

    exit_idx = min(entry_idx + max_hold, len(candles) - 1)
    exit_px = float(candles.iloc[exit_idx]['close'])
    gross_ret = (exit_px - entry_px) / entry_px
    return gross_ret, exit_idx, "timeout"


def sim_short_trail(candles, entry_idx, entry_px, trail_pct, max_hold=48):
    """Short trailing stop:
    - Enter short at entry_px
    - Track Low Water Mark (LWM) = lowest price since entry
    - Trail stop = LWM * (1 + trail_pct) — exit when price recovers too much
    - Profit when price goes DOWN from entry
    """
    lwm = entry_px
    for i in range(entry_idx, min(entry_idx + max_hold, len(candles))):
        bar = candles.iloc[i]
        low = float(bar['low'])
        high = float(bar['high'])

        # Update LWM with bar low (price going down = good for short)
        if low < lwm:
            lwm = low

        # Trail stop: if price rises back by trail_pct from LWM
        trail_stop = lwm * (1 + trail_pct)

        # Check if high breaks trail stop (price recovered too much)
        if high >= trail_stop:
            exit_px = trail_stop
            gross_ret = (entry_px - exit_px) / entry_px
            return gross_ret, i, "trailing_stop"

    # Timeout: exit at close
    exit_idx = min(entry_idx + max_hold, len(candles) - 1)
    exit_px = float(candles.iloc[exit_idx]['close'])
    gross_ret = (entry_px - exit_px) / entry_px
    return gross_ret, exit_idx, "timeout"


def sim_short_fixed_hold(candles, entry_idx, entry_px, hold_bars=4):
    """Short with fixed holding period."""
    exit_idx = min(entry_idx + hold_bars, len(candles) - 1)
    exit_px = float(candles.iloc[exit_idx]['close'])
    gross_ret = (entry_px - exit_px) / entry_px
    return gross_ret, exit_idx, "fixed_hold"


def run_backtest(valid, candle_cache, sim_fn, name, **kwargs):
    """Run a simulation and return stats."""
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

        # Skip first bar (lag 1h for entry)
        idx = idx + 1
        if idx >= len(candles):
            continue

        ret, _, reason = sim_fn(candles, idx, entry_px, **kwargs)
        if ret is not None:
            net = (1 + ret) * (1 - FEE_RATE)**2 - 1
            rets.append(net)
            reasons[reason] = reasons.get(reason, 0) + 1

    rets = np.array(rets)
    if len(rets) == 0:
        return None

    wins = rets[rets > 0].sum()
    losses = -rets[rets < 0].sum()
    pf = float(wins / losses) if losses > 0 else float('inf')

    return {
        'name': name,
        'n': len(rets),
        'mean': float(np.mean(rets) * 100),
        'median': float(np.median(rets) * 100),
        'winrate': float(np.mean(rets > 0) * 100),
        'pf': pf,
        'reasons': reasons,
    }


def main():
    valid, candle_cache = load_data()

    print('\n' + '='*80)
    print('SHORT vs LONG Trailing Stop Backtest')
    print('='*80)

    # Test different trail percentages for SHORT
    print('\n--- SHORT Strategy ---')
    short_results = []
    for trail_pct in [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10]:
        r = run_backtest(valid, candle_cache, sim_short_trail, f'short_trail_{int(trail_pct*100)}%', trail_pct=trail_pct)
        if r:
            short_results.append(r)
            print(f'trail {trail_pct*100:.0f}%: n={r["n"]:,}, mean={r["mean"]:.2f}%, median={r["median"]:.2f}%, WR={r["winrate"]:.1f}%, PF={r["pf"]:.2f}')
            for reason, count in sorted(r['reasons'].items()):
                print(f'  {reason}: {count} ({count/r["n"]*100:.1f}%)')

    # Also test SHORT with fixed hold periods
    print('\n--- SHORT Fixed Hold ---')
    for hold in [2, 4, 8, 12, 24, 48]:
        r = run_backtest(valid, candle_cache, sim_short_fixed_hold, f'short_fixed_{hold}h', hold_bars=hold)
        if r:
            print(f'fixed {hold}h: n={r["n"]:,}, mean={r["mean"]:.2f}%, median={r["median"]:.2f}%, WR={r["winrate"]:.1f}%, PF={r["pf"]:.2f}')

    # LONG baseline for comparison
    print('\n--- LONG Strategy (baseline) ---')
    long_results = []
    for trail_pct in [0.02, 0.03, 0.04, 0.05]:
        r = run_backtest(valid, candle_cache, sim_long_trail, f'long_trail_{int(trail_pct*100)}%', trail_pct=trail_pct)
        if r:
            long_results.append(r)
            print(f'trail {trail_pct*100:.0f}%: n={r["n"]:,}, mean={r["mean"]:.2f}%, median={r["median"]:.2f}%, WR={r["winrate"]:.1f}%, PF={r["pf"]:.2f}')
            for reason, count in sorted(r['reasons'].items()):
                print(f'  {reason}: {count} ({count/r["n"]*100:.1f}%)')

    # Summary table
    print('\n' + '='*80)
    print('SUMMARY: LONG vs SHORT')
    print('='*80)
    print(f'{"Config":<25s} {"N":>6s} {"Mean":>8s} {"Median":>8s} {"WR":>6s} {"PF":>6s}')
    print('-'*60)
    for r in long_results:
        print(f'{r["name"]:<25s} {r["n"]:>6d} {r["mean"]:>+7.2f}% {r["median"]:>+7.2f}% {r["winrate"]:>5.1f}% {r["pf"]:>5.2f}')
    print('---')
    for r in short_results:
        print(f'{r["name"]:<25s} {r["n"]:>6d} {r["mean"]:>+7.2f}% {r["median"]:>+7.2f}% {r["winrate"]:>5.1f}% {r["pf"]:>5.2f}')


if __name__ == '__main__':
    main()
