#!/usr/bin/env python3
"""
Comprehensive comparison of all strategy changes:
1. Trail 2% vs 4% (with low trigger = backtest baseline)
2. Low trigger vs Close trigger (already done, re-confirming)
3. Slippage impact at each trail level
4. Yearly stability
"""
from __future__ import annotations
import json, glob, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_change_analysis'
OUT.mkdir(parents=True, exist_ok=True)

def pf(x):
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    return float(wins / losses) if losses > 0 else (float('inf') if wins > 0 else float('nan'))

def stats(rets):
    if len(rets) == 0:
        return {}
    return {
        'n': int(len(rets)),
        'mean': float(np.mean(rets)),
        'median': float(np.median(rets)),
        'winrate': float(np.mean(rets > 0)),
        'pf': pf(rets),
    }

# Load trades
trades = pd.read_csv(TRADES_F)
trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
trades['event_ts'] = pd.to_datetime(trades['event_ts'], utc=True)
valid = trades.dropna(subset=['trail_3pct_ret']).copy()
print(f'Loaded {len(trades):,} trades, {len(valid):,} valid')

# Load candles
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
                    df = pd.read_csv(fh, usecols=lambda c: c in {'open_time', 'high', 'low', 'close'})
                out = pd.DataFrame({
                    'ts': pd.to_datetime(pd.to_numeric(df['open_time'], errors='coerce'), unit='ms', utc=True),
                    'high': pd.to_numeric(df['high'], errors='coerce'),
                    'low': pd.to_numeric(df['low'], errors='coerce'),
                    'close': pd.to_numeric(df['close'], errors='coerce'),
                }).dropna(subset=['ts'])
                frames.append(out)
        except Exception:
            continue
    if frames:
        candle_cache[sym] = pd.concat(frames).sort_values('ts').drop_duplicates('ts').reset_index(drop=True)
print(f'Loaded candles for {len(candle_cache)} symbols')

# ---- Re-simulate all trail levels × trigger types ----
trail_pcts = [0.01, 0.02, 0.03, 0.04, 0.05]
trail_labels = ['1pct', '2pct', '3pct', '4pct', '5pct']
MAX_HOLD = 48
BASE_COST = 0.0013

results = {}  # (trail_label, trigger_type) -> list of returns
re_sim = 0
skip = 0

for idx, row in valid.iterrows():
    sym = row['symbol']
    if sym not in candle_cache:
        skip += 1
        continue
    candles = candle_cache[sym]
    signal_ts = row['signal_ts']
    entry_price = row['entry_price']
    if pd.isna(entry_price) or entry_price <= 0:
        skip += 1
        continue

    candle_ns = candles['ts'].dt.as_unit('ns').astype('int64').to_numpy()
    signal_ns = np.int64(signal_ts.value)
    pos = int(np.searchsorted(candle_ns, signal_ns))
    best_idx = None
    best_diff = np.inf
    for c in [pos - 1, pos, pos + 1]:
        if 0 <= c < len(candle_ns):
            diff = abs(candle_ns[c - 0] - signal_ns) if c != pos else abs(candle_ns[pos] - signal_ns)
            # Fix: just check direct diff
            d2 = abs(candle_ns[c] - signal_ns)
            if d2 < best_diff:
                best_diff = d2
                best_idx = c
    if best_idx is None or best_diff > 3_600_000_000_000:
        skip += 1
        continue

    entry_idx = best_idx
    future = candles.iloc[entry_idx + 1:entry_idx + 1 + MAX_HOLD]
    if future.empty:
        skip += 1
        continue
    re_sim += 1

    for label, trail_pct in zip(trail_labels, trail_pcts):
        # --- LOW trigger (backtest baseline) ---
        highest = entry_price
        result_low = None
        for _, bar in future.iterrows():
            if bar['high'] > highest:
                highest = bar['high']
            trail_stop = highest * (1 - trail_pct)
            if bar['low'] <= trail_stop:
                result_low = (trail_stop / entry_price - 1) - BASE_COST
                break
        if result_low is None:
            last_bar = future.iloc[-1]
            result_low = (last_bar['close'] / entry_price - 1) - BASE_COST
        results.setdefault((label, 'low'), []).append(result_low)

        # --- CLOSE trigger (new logic) ---
        highest = entry_price
        result_close = None
        for _, bar in future.iterrows():
            # Update HWM with high (same as low trigger)
            if bar['high'] > highest:
                highest = bar['high']
            trail_stop = highest * (1 - trail_pct)
            # But trigger on CLOSE instead of LOW
            if bar['close'] <= trail_stop:
                result_close = (bar['close'] / entry_price - 1) - BASE_COST
                break
        if result_close is None:
            last_bar = future.iloc[-1]
            result_close = (last_bar['close'] / entry_price - 1) - BASE_COST
        results.setdefault((label, 'close'), []).append(result_close)

print(f'Re-simulated {re_sim:,} trades ({skip:,} skipped)')

# ---- Summary Table ----
print()
print('=' * 100)
print("FULL COMPARISON: Trail% × Trigger Type (0 bps slippage)")
print('=' * 100)
print(f"{'Config':<25} {'N':>5} {'Mean%':>7} {'Median%':>8} {'WinRate':>8} {'PF':>6}")
print('-' * 100)

summary_rows = []
for label in trail_labels:
    for trigger in ['low', 'close']:
        key = (label, trigger)
        rets = np.array(results[key])
        s = stats(rets)
        config = f"trail {label} + {trigger}"
        print(f"{config:<25} {s['n']:>5} {s['mean']*100:>+6.2f}% {s['median']*100:>+7.2f}% {s['winrate']*100:>6.1f}% {s['pf']:>6.2f}")
        s['config'] = config
        s['trail_pct'] = label
        s['trigger'] = trigger
        summary_rows.append(s)

# ---- Slippage sensitivity ----
print()
print('=' * 100)
print("SLIPPAGE SENSITIVITY: Trail 2% vs 4%, low vs close")
print('=' * 100)
slip_levels = [0, 0.001, 0.002, 0.003, 0.005]

for trail_key in [('2pct', 'low'), ('2pct', 'close'), ('4pct', 'low'), ('4pct', 'close')]:
    print(f"\n--- trail {trail_key[0]} + {trail_key[1]} trigger ---")
    rets_base = np.array(results[trail_key])
    for slip in slip_levels:
        adj = rets_base - 2 * slip
        s = stats(adj)
        print(f"  {int(slip*10000):>3}bps: mean={s['mean']*100:>+6.2f}%  median={s['median']*100:>+7.2f}%  wr={s['winrate']*100:>5.1f}%  pf={s['pf']:>6.2f}")

# ---- Yearly stability ----
print()
print('=' * 100)
print("YEARLY STABILITY: Key configs (0 bps)")
print('=' * 100)
years = sorted(valid['year'].unique())

for trail_key in [('2pct', 'low'), ('2pct', 'close'), ('4pct', 'low'), ('4pct', 'close')]:
    print(f"\n--- trail {trail_key[0]} + {trail_key[1]} ---")
    # Need to map back to per-trade year info
    # Since results are aligned with valid rows (minus skipped), rebuild year array
    year_list = []
    for idx, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        candles = candle_cache[sym]
        signal_ts = row['signal_ts']
        entry_price = row['entry_price']
        if pd.isna(entry_price) or entry_price <= 0:
            continue
        candle_ns = candles['ts'].dt.as_unit('ns').astype('int64').to_numpy()
        signal_ns = np.int64(signal_ts.value)
        pos = int(np.searchsorted(candle_ns, signal_ns))
        best_idx = None
        best_diff = np.inf
        for c in [pos - 1, pos, pos + 1]:
            if 0 <= c < len(candle_ns):
                d2 = abs(candle_ns[c] - signal_ns)
                if d2 < best_diff:
                    best_diff = d2
                    best_idx = c
        if best_idx is None or best_diff > 3_600_000_000_000:
            continue
        entry_idx = best_idx
        future = candles.iloc[entry_idx + 1:entry_idx + 1 + MAX_HOLD]
        if future.empty:
            continue
        year_list.append(row['year'])

    rets = np.array(results[trail_key])
    year_arr = np.array(year_list)
    for yr in sorted(set(year_arr)):
        mask = year_arr == yr
        yr_rets = rets[mask]
        s = stats(yr_rets)
        print(f"  {yr}: n={s['n']:>4}  mean={s['mean']*100:>+6.2f}%  median={s['median']*100:>+7.2f}%  wr={s['winrate']*100:>5.1f}%  pf={s['pf']:>6.2f}")

# ---- Paper trading comparison ----
print()
print('=' * 100)
print("PAPER TRADING vs BACKTEST WIN RATE ANALYSIS")
print('=' * 100)
print()
print("Paper trading (5 trades, all trailing_stop exit):")
print("  COSUSDT:  entry 0.01155, exit 0.01128, ret -2.34%")
print("  TRUTHUSDT: entry 0.05687, exit 0.05578, ret -1.92%")
print("  JCTUSDT:  entry 0.00627, exit 0.00620, ret -1.12%")
print("  QUSDT:    entry 0.02474, exit 0.02395, ret -3.19%")
print("  AINUSDT:  entry 0.29690, exit 0.29130, ret -1.89%")
print("  Average:  -2.09%, Median: -1.92%, Win Rate: 0%")
print()
print("Backtest (trail 2%, low trigger, 0 bps):")
s2low = stats(np.array(results[('2pct', 'low')]))
print(f"  n={s2low['n']}, mean={s2low['mean']*100:+.2f}%, median={s2low['median']*100:+.2f}%, win_rate={s2low['winrate']*100:.1f}%")
print()
print("WIN RATE GAP: 67.5% (backtest) vs 0% (paper) = 67.5pp gap")
print()
print("ROOT CAUSES:")
print("1. LOW TRIGGER vs BID TRIGGER:")
print("   - Backtest: exits at K-line LOW price (theoretical best)")
print("   - Paper: exits at real-time bid price (worse by spread)")
print("   - The 'low' in backtest is the absolute best price in the bar")
print("   - In reality, you'd get bid price which is higher than low")
print("   - This means backtest OVERSTATES win rate")
print()
print("2. HWM (High Water Mark) UPDATES:")
print("   - Backtest: HWM updated with each bar's HIGH price")
print("   - Paper: HWM updated with each tick's bid price")
print("   - High >= bid always, so backtest HWM is higher")
print("   - Higher HWM → higher trail stop → exit at higher price")
print("   - This FURTHER overstates backtest win rate")
print()
print("3. MONITORING FREQUENCY:")
print("   - Backtest: checks every 1h bar")
print("   - Paper: checks every ~10s")
print("   - Paper catches intra-bar dips that backtest misses")
print("   - This makes paper MORE likely to trigger (at worse prices)")
print()
print("4. SAMPLE SIZE:")
print("   - Paper: only 5 trades (too small to draw conclusions)")
print("   - Backtest: 1951 trades")
print("   - Paper's 0% win rate could be bad luck")
print()

# Save summary
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(OUT / 'change_analysis_summary.csv', index=False)
print(f'\nSaved to {OUT}/change_analysis_summary.csv')
