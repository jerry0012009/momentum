#!/usr/bin/env python3
"""
v1.6a Second Squeeze — Slippage Sensitivity + Parameter Stability.

Tests:
1. Slippage robustness: add 0/5/10/20/30/50 bps one-way slippage to trail_3pct
2. Trailing stop parameter sweep: 1%/2%/3%/4%/5%/7%/10% under various slippage
3. Yearly stability for each (trail%, slippage) combo
4. Ret bucket breakdown for best combos
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TPSL_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_slippage_sensitivity'
OUT.mkdir(parents=True, exist_ok=True)

TRADES_F = TPSL_ART / 'all_trades_tpsl.csv'


def pf(x: np.ndarray) -> float:
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return float('inf') if wins > 0 else float('nan')
    return float(wins / losses)


def stats(rets: np.ndarray) -> dict:
    """Compute summary statistics for a return array."""
    if len(rets) == 0:
        return {}
    return {
        'n': int(len(rets)),
        'mean': float(np.mean(rets)),
        'median': float(np.median(rets)),
        'winrate': float(np.mean(rets > 0)),
        'pf': pf(rets),
        'p5': float(np.percentile(rets, 5)),
        'p25': float(np.percentile(rets, 25)),
        'p75': float(np.percentile(rets, 75)),
        'p95': float(np.percentile(rets, 95)),
    }


def main():
    print('=' * 70)
    print('SLIPPAGE SENSITIVITY + TRAILING STOP PARAMETER SWEEP')
    print('=' * 70)

    # Load trades
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    trades['event_ts'] = pd.to_datetime(trades['event_ts'], utc=True)
    print(f'Loaded {len(trades):,} trades')

    # Filter to trades with valid trail_3pct_ret
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()
    print(f'Valid trail_3pct trades: {len(valid):,}')

    # --- Part 1: Slippage on trail_3pct ---
    print('\n' + '=' * 70)
    print('PART 1: Slippage robustness (trail_3pct)')
    print('=' * 70)

    slippage_levels = [0, 0.0005, 0.001, 0.002, 0.003, 0.005]  # 0, 5, 10, 20, 30, 50 bps one-way
    slippage_labels = ['0bps', '5bps', '10bps', '20bps', '30bps', '50bps']

    base_rets = valid['trail_3pct_ret'].values

    slip_rows = []
    for slip, label in zip(slippage_levels, slippage_labels):
        adj = base_rets - 2 * slip  # round-trip slippage
        s = stats(adj)
        s['slippage'] = label
        s['slippage_bps'] = int(slip * 10000)
        slip_rows.append(s)
        print(f'  {label:>6s}: n={s["n"]:,}  mean={s["mean"]*100:+.2f}%  median={s["median"]*100:+.2f}%  '
              f'wr={s["winrate"]*100:.1f}%  pf={s["pf"]:.2f}  p5={s["p5"]*100:.2f}%  p95={s["p95"]*100:.2f}%')

    slip_df = pd.DataFrame(slip_rows)
    slip_df.to_csv(OUT / 'slippage_robustness.csv', index=False)

    # --- Part 2: Trailing stop parameter sweep ---
    print('\n' + '=' * 70)
    print('PART 2: Trailing stop parameter sweep')
    print('=' * 70)

    # We need to re-simulate trailing stops with different percentages.
    # We don't have the candles here, but we can approximate from the
    # existing data: trail_3pct_ret is already computed. For other trailing
    # stop percentages, we need the per-candle data.
    #
    # Alternative: load from the TP/SL script's all_trades_tpsl.csv which has
    # entry_price and we can re-simulate. But we need candles.
    #
    # Simplest: use the candle cache. Let's load it.

    CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
    import glob
    import zipfile

    # Get unique symbols from valid trades
    symbols = valid['symbol'].unique()
    print(f'Loading candles for {len(symbols)} symbols...')

    candle_cache = {}
    loaded = 0
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
            c = pd.concat(frames).sort_values('ts').drop_duplicates('ts').reset_index(drop=True)
            candle_cache[sym] = c
            loaded += 1

    print(f'Loaded candles for {loaded} symbols')

    # Re-simulate trailing stops with different percentages
    trail_pcts = [0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.10]
    trail_labels = ['trail_1pct', 'trail_2pct', 'trail_3pct', 'trail_4pct',
                    'trail_5pct', 'trail_7pct', 'trail_10pct']
    MAX_HOLD = 48
    BASE_COST = 0.0013

    # For each trade, re-simulate all trailing stop percentages
    trail_results = {label: [] for label in trail_labels}
    re_sim_count = 0
    skip_count = 0

    for idx, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            skip_count += 1
            continue

        candles = candle_cache[sym]
        signal_ts = row['signal_ts']
        entry_price = row['entry_price']

        if pd.isna(entry_price) or entry_price <= 0:
            skip_count += 1
            continue

        # Find entry index
        candle_ns = candles['ts'].dt.as_unit('ns').astype('int64').to_numpy()
        signal_ns = np.int64(signal_ts.value)
        pos = int(np.searchsorted(candle_ns, signal_ns))
        best_idx = None
        best_diff = np.inf
        for candidate in [pos - 1, pos, pos + 1]:
            if 0 <= candidate < len(candle_ns):
                diff = abs(candle_ns[candidate] - signal_ns)
                if diff < best_diff:
                    best_diff = diff
                    best_idx = candidate
        if best_idx is None or best_diff > 3_600_000_000_000:
            skip_count += 1
            continue

        entry_idx = best_idx
        future = candles.iloc[entry_idx + 1:entry_idx + 1 + MAX_HOLD]
        if future.empty:
            skip_count += 1
            continue

        re_sim_count += 1

        # Simulate each trailing stop percentage
        for label, trail_pct in zip(trail_labels, trail_pcts):
            highest = entry_price
            result = None
            for i, (_, bar) in enumerate(future.iterrows()):
                if bar['high'] > highest:
                    highest = bar['high']
                trail_stop = highest * (1 - trail_pct)
                if bar['low'] <= trail_stop:
                    exit_ret = (trail_stop / entry_price - 1) - BASE_COST
                    result = exit_ret
                    break
            if result is None:
                last_bar = future.iloc[-1]
                result = (last_bar['close'] / entry_price - 1) - BASE_COST
            trail_results[label].append(result)

    print(f'Re-simulated {re_sim_count:,} trades ({skip_count:,} skipped)')

    # Summary for all trail% × slippage combos
    print('\n' + '=' * 70)
    print('PART 2: Trail% × Slippage combo table')
    print('=' * 70)

    combo_rows = []
    for label, trail_pct in zip(trail_labels, trail_pcts):
        rets = np.array(trail_results[label])
        for slip, slip_label in zip(slippage_levels, slippage_labels):
            adj = rets - 2 * slip
            s = stats(adj)
            s['trail_pct'] = trail_pct
            s['trail_label'] = label
            s['slippage'] = slip_label
            s['slippage_bps'] = int(slip * 10000)
            combo_rows.append(s)

    combo_df = pd.DataFrame(combo_rows)
    combo_df.to_csv(OUT / 'trail_slippage_combos.csv', index=False)

    # Print the matrix
    print(f'\n{"":>12s}', end='')
    for sl in slippage_labels:
        print(f'  {sl:>6s}', end='')
    print()

    for label, trail_pct in zip(trail_labels, trail_pcts):
        print(f'{label:>12s}', end='')
        for slip in slippage_levels:
            row = combo_df[(combo_df['trail_label'] == label) & (combo_df['slippage_bps'] == int(slip * 10000))]
            if not row.empty:
                r = row.iloc[0]
                print(f'  {r["mean"]*100:+5.2f}%', end='')
            else:
                print(f'    N/A', end='')
        print(f'  (trail {trail_pct*100:.0f}%)')

    print(f'\n{"Median":>12s}')
    for label, trail_pct in zip(trail_labels, trail_pcts):
        print(f'{label:>12s}', end='')
        for slip in slippage_levels:
            row = combo_df[(combo_df['trail_label'] == label) & (combo_df['slippage_bps'] == int(slip * 10000))]
            if not row.empty:
                r = row.iloc[0]
                print(f'  {r["median"]*100:+5.2f}%', end='')
            else:
                print(f'    N/A', end='')
        print(f'  (trail {trail_pct*100:.0f}%)')

    print(f'\n{"PF":>12s}')
    for label, trail_pct in zip(trail_labels, trail_pcts):
        print(f'{label:>12s}', end='')
        for slip in slippage_levels:
            row = combo_df[(combo_df['trail_label'] == label) & (combo_df['slippage_bps'] == int(slip * 10000))]
            if not row.empty:
                r = row.iloc[0]
                print(f'  {r["pf"]:6.2f}', end='')
            else:
                print(f'    N/A', end='')
        print(f'  (trail {trail_pct*100:.0f}%)')

    print(f'\n{"Winrate":>12s}')
    for label, trail_pct in zip(trail_labels, trail_pcts):
        print(f'{label:>12s}', end='')
        for slip in slippage_levels:
            row = combo_df[(combo_df['trail_label'] == label) & (combo_df['slippage_bps'] == int(slip * 10000))]
            if not row.empty:
                r = row.iloc[0]
                print(f'  {r["winrate"]*100:5.1f}%', end='')
            else:
                print(f'    N/A', end='')
        print(f'  (trail {trail_pct*100:.0f}%)')

    # --- Part 3: Yearly stability for key combos ---
    print('\n' + '=' * 70)
    print('PART 3: Yearly stability for key combos')
    print('=' * 70)

    # Key combos: trail 2/3/5% × 0/10/30 bps slippage
    key_trails = ['trail_2pct', 'trail_3pct', 'trail_5pct']
    key_slips = [0, 0.001, 0.003]  # 0, 10, 30 bps

    yearly_rows = []
    years = sorted(valid['year'].unique())

    for label, trail_pct in zip(trail_labels, trail_pcts):
        if label not in key_trails:
            continue
        rets_arr = np.array(trail_results[label])
        for slip, slip_bps in zip(key_slips, [0, 10, 30]):
            adj = rets_arr - 2 * slip
            for year in years:
                mask = valid['year'].values == year
                yr_rets = adj[mask]
                if len(yr_rets) == 0:
                    continue
                s = stats(yr_rets)
                s['trail_label'] = label
                s['trail_pct'] = trail_pct
                s['slippage_bps'] = slip_bps
                s['year'] = int(year)
                yearly_rows.append(s)

    yearly_df = pd.DataFrame(yearly_rows)
    yearly_df.to_csv(OUT / 'yearly_stability.csv', index=False)

    for label in key_trails:
        for slip_bps in [0, 10, 30]:
            print(f'\n  {label} + {slip_bps}bps slippage:')
            subset = yearly_df[(yearly_df['trail_label'] == label) & (yearly_df['slippage_bps'] == slip_bps)]
            for _, r in subset.iterrows():
                print(f'    {int(r["year"])}  n={int(r["n"]):>4d}  mean={r["mean"]*100:+.2f}%  '
                      f'median={r["median"]*100:+.2f}%  wr={r["winrate"]*100:.1f}%  pf={r["pf"]:.2f}')

    # --- Part 4: Ret bucket breakdown for best combos ---
    print('\n' + '=' * 70)
    print('PART 4: Ret bucket breakdown (best combos)')
    print('=' * 70)

    ret_buckets = ['30-40%', '40-50%', '50%+']
    bucket_rows = []

    for label, trail_pct in zip(trail_labels, trail_pcts):
        if label not in key_trails:
            continue
        rets_arr = np.array(trail_results[label])
        for slip_bps in [0, 10, 30]:
            slip = slip_bps / 10000
            adj = rets_arr - 2 * slip
            for bucket in ret_buckets:
                mask = valid['ret_bucket'].values == bucket
                bk_rets = adj[mask]
                if len(bk_rets) == 0:
                    continue
                s = stats(bk_rets)
                s['trail_label'] = label
                s['trail_pct'] = trail_pct
                s['slippage_bps'] = slip_bps
                s['ret_bucket'] = bucket
                bucket_rows.append(s)

    bucket_df = pd.DataFrame(bucket_rows)
    bucket_df.to_csv(OUT / 'ret_bucket_breakdown.csv', index=False)

    for label in key_trails:
        for slip_bps in [0, 10, 30]:
            print(f'\n  {label} + {slip_bps}bps:')
            subset = bucket_df[(bucket_df['trail_label'] == label) & (bucket_df['slippage_bps'] == slip_bps)]
            for _, r in subset.iterrows():
                print(f'    {r["ret_bucket"]:>8s}  n={int(r["n"]):>4d}  mean={r["mean"]*100:+.2f}%  '
                      f'median={r["median"]*100:+.2f}%  wr={r["winrate"]*100:.1f}%  pf={r["pf"]:.2f}')

    # --- Part 5: Best config ranking ---
    print('\n' + '=' * 70)
    print('PART 5: Config ranking (all combos, sorted by PF with n>=30)')
    print('=' * 70)

    ranked = combo_df[combo_df['n'] >= 30].sort_values('pf', ascending=False).head(20)
    for i, (_, r) in enumerate(ranked.iterrows()):
        print(f'  {i+1:2d}. {r["trail_label"]:>12s} + {r["slippage"]:>6s}  '
              f'mean={r["mean"]*100:+.2f}%  median={r["median"]*100:+.2f}%  '
              f'wr={r["winrate"]*100:.1f}%  pf={r["pf"]:.2f}  n={int(r["n"]):,}')

    # Save ranking
    ranked.to_csv(OUT / 'config_ranking.csv', index=False)

    # --- Save summary JSON ---
    summary = {
        'total_trades': int(len(trades)),
        'valid_trail_trades': int(len(valid)),
        're_simulated_trades': int(re_sim_count),
        'trail_pcts_tested': [float(t) for t in trail_pcts],
        'slippage_levels_bps': [int(s * 10000) for s in slippage_levels],
        'best_config': {
            'trail_pct': float(ranked.iloc[0]['trail_pct']) if len(ranked) > 0 else None,
            'slippage': ranked.iloc[0]['slippage'] if len(ranked) > 0 else None,
            'mean': float(ranked.iloc[0]['mean']) if len(ranked) > 0 else None,
            'median': float(ranked.iloc[0]['median']) if len(ranked) > 0 else None,
            'pf': float(ranked.iloc[0]['pf']) if len(ranked) > 0 else None,
            'winrate': float(ranked.iloc[0]['winrate']) if len(ranked) > 0 else None,
        },
        'trail_3pct_0bps': stats(np.array(trail_results['trail_3pct'])),
        'trail_3pct_30bps': {
            k: v for k, v in stats(np.array(trail_results['trail_3pct']) - 2 * 0.003).items()
        },
    }

    with open(OUT / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f'\nSaved outputs to {OUT}')
    print('Done.')


if __name__ == '__main__':
    main()
