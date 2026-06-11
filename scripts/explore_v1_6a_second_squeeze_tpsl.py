#!/usr/bin/env python3
"""
v1.6a Second Squeeze: TP/SL simulation + event intensity stratification.

Premise: After a leaderboard event (rank<=20, 24h ret>=30%), wait for V4 signal
(vol>3x avg + ret>1%) to enter. Then simulate TP/SL exits bar-by-bar.

Two research questions:
  1. Can TP/SL turn the negative median positive?
  2. Are 50%+ gain events more reliable for second squeeze?

Data: Binance 1h candles from zip cache.
"""
from __future__ import annotations

import glob
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
RT_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
V4_TRADES = ROOT / 'reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl'
OUT.mkdir(parents=True, exist_ok=True)

BASE_COST = 0.0013  # 13bps round-trip

# TP/SL configs to test
TP_SL_CONFIGS = [
    ('tp5_sl3', 0.05, 0.03),
    ('tp3_sl2', 0.03, 0.02),
    ('tp8_sl3', 0.08, 0.03),
    ('tp10_sl5', 0.10, 0.05),
    ('tp5_sl2', 0.05, 0.02),
    ('tp3_sl3', 0.03, 0.03),
    # Trailing stops
    ('trail_3pct', None, None),  # special: trailing stop
]

# Max hold hours for TP/SL simulation
MAX_HOLD = 48

# Event rules to test
EVENT_RULES = {
    'rank20_ret30_vol5m': RT_ART / 'events_rank20_ret30_vol5m.csv',
}


def load_candles(symbol: str) -> pd.DataFrame | None:
    """Load 1h candles for a symbol from Binance Vision zip cache."""
    files = sorted(glob.glob(str(CACHE_DIR / symbol / f'{symbol}-1h-*.zip')))
    if not files:
        return None
    frames = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith('.csv')]
                if not names:
                    continue
                with zf.open(names[0]) as fh:
                    df = pd.read_csv(fh, usecols=['open_time', 'open', 'high', 'low', 'close'])
            frames.append(df)
        except Exception:
            continue
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df['ts'] = pd.to_datetime(pd.to_numeric(df['open_time'], errors='coerce'), unit='ms', utc=True)
    for c in ['open', 'high', 'low', 'close']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['ts', 'close']).sort_values('ts').drop_duplicates('ts')
    df = df.reset_index(drop=True)
    return df


def simulate_tpsl(candles: pd.DataFrame, entry_idx: int, entry_price: float,
                  tp_pct: float, sl_pct: float, cost: float) -> dict | None:
    """Simulate TP/SL exit. Returns exit info or None if data insufficient."""
    if entry_idx is None or entry_price is None or entry_price <= 0:
        return None

    tp_price = entry_price * (1 + tp_pct)
    sl_price = entry_price * (1 - sl_pct)

    # Look at bars after entry (entry bar is the signal bar, we enter at close)
    future = candles.iloc[entry_idx + 1:entry_idx + 1 + MAX_HOLD]
    if future.empty:
        return None

    for i, (_, bar) in enumerate(future.iterrows()):
        # Check if SL hit (low touches SL)
        if bar['low'] <= sl_price:
            exit_ret = (sl_price / entry_price - 1) - cost
            return {'exit_bar': i + 1, 'exit_type': 'sl', 'exit_ret': exit_ret,
                    'exit_price': sl_price, 'hold_hours': i + 1}
        # Check if TP hit (high touches TP)
        if bar['high'] >= tp_price:
            exit_ret = (tp_price / entry_price - 1) - cost
            return {'exit_bar': i + 1, 'exit_type': 'tp', 'exit_ret': exit_ret,
                    'exit_price': tp_price, 'hold_hours': i + 1}

    # Neither hit: exit at last bar close
    last_bar = future.iloc[-1]
    exit_ret = (last_bar['close'] / entry_price - 1) - cost
    return {'exit_bar': len(future), 'exit_type': 'timeout', 'exit_ret': exit_ret,
            'exit_price': last_bar['close'], 'hold_hours': len(future)}


def simulate_trailing_stop(candles: pd.DataFrame, entry_idx: int, entry_price: float,
                           trail_pct: float, cost: float) -> dict | None:
    """Simulate trailing stop exit."""
    if entry_idx is None or entry_price is None or entry_price <= 0:
        return None

    future = candles.iloc[entry_idx + 1:entry_idx + 1 + MAX_HOLD]
    if future.empty:
        return None

    highest = entry_price
    for i, (_, bar) in enumerate(future.iterrows()):
        # Update highest price seen
        if bar['high'] > highest:
            highest = bar['high']
        # Check if trailing stop hit
        trail_stop = highest * (1 - trail_pct)
        if bar['low'] <= trail_stop:
            exit_ret = (trail_stop / entry_price - 1) - cost
            return {'exit_bar': i + 1, 'exit_type': 'trail', 'exit_ret': exit_ret,
                    'exit_price': trail_stop, 'hold_hours': i + 1}

    # Never stopped out
    last_bar = future.iloc[-1]
    exit_ret = (last_bar['close'] / entry_price - 1) - cost
    return {'exit_bar': len(future), 'exit_type': 'timeout', 'exit_ret': exit_ret,
            'exit_price': last_bar['close'], 'hold_hours': len(future)}


def pf(x: np.ndarray) -> float:
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return float('inf') if wins > 0 else float('nan')
    return float(wins / losses)


def main():
    # Load events
    events_dfs = {}
    for rule, fp in EVENT_RULES.items():
        df = pd.read_csv(fp)
        df['event_ts'] = pd.to_datetime(df['event_ts'], utc=True)
        events_dfs[rule] = df
        print(f'[events] {rule}: {len(df):,} events, {df.symbol.nunique()} symbols')

    # Load V4 trades
    trades = pd.read_csv(V4_TRADES)
    trades['ts'] = pd.to_datetime(trades['ts'], utc=True)
    print(f'[trades] V4: {len(trades):,} trades, {trades.symbol.nunique()} symbols')

    # For each event rule, find V4 signals post-event
    all_results = []

    for rule, events in events_dfs.items():
        print(f'\n=== Processing {rule} ===')

        # Get unique symbols that appear in events
        event_symbols = set(events['symbol'].unique())
        # Get unique symbols that appear in trades
        trade_symbols = set(trades['symbol'].unique())
        # Intersection
        common_symbols = event_symbols & trade_symbols
        print(f'  Symbols with both events and trades: {len(common_symbols)}')

        # Pre-load candles for all relevant symbols
        candle_cache = {}
        loaded = 0
        for sym in sorted(common_symbols):
            c = load_candles(sym)
            if c is not None and len(c) > 0:
                candle_cache[sym] = c
                loaded += 1
        print(f'  Loaded candles for {loaded} symbols')

        # For each symbol, match events to V4 signals
        sym_count = 0
        trade_count = 0
        skip_no_trade = 0
        skip_no_candle = 0
        skip_no_price = 0

        for sym in sorted(candle_cache.keys()):
            candles = candle_cache[sym]
            sym_events = events[events['symbol'] == sym].sort_values('event_ts')
            sym_trades = trades[trades['symbol'] == sym].sort_values('ts')

            if sym_events.empty or sym_trades.empty:
                continue

            sym_count += 1

            # Build candle timestamp lookup (all in nanoseconds)
            candle_ns = candles['ts'].dt.as_unit('ns').astype('int64').to_numpy()

            for _, ev in sym_events.iterrows():
                ev_ts = pd.Timestamp(ev['event_ts'])

                # Find V4 signals after event (1-48h window)
                mask = (sym_trades['ts'] > ev_ts) & (sym_trades['ts'] <= ev_ts + pd.Timedelta(hours=48))
                post_trades = sym_trades.loc[mask]

                if post_trades.empty:
                    skip_no_trade += 1
                    continue

                # Take first signal per event
                first_trade = post_trades.iloc[0]
                signal_ts = pd.Timestamp(first_trade['ts'])
                entry_price = float(first_trade['entry_price'])

                if pd.isna(entry_price) or entry_price <= 0:
                    skip_no_price += 1
                    continue

                # Find entry index in candles using searchsorted
                signal_ns_val = np.int64(signal_ts.value)
                pos = int(np.searchsorted(candle_ns, signal_ns_val))
                # Check nearest neighbors
                best_idx = None
                best_diff = np.inf
                for candidate in [pos - 1, pos, pos + 1]:
                    if 0 <= candidate < len(candle_ns):
                        diff = abs(candle_ns[candidate] - signal_ns_val)
                        if diff < best_diff:
                            best_diff = diff
                            best_idx = candidate
                if best_idx is None or best_diff > 3_600_000_000_000:
                    skip_no_candle += 1
                    continue
                entry_idx = best_idx

                # Compute fixed-hold returns for comparison
                fixed_4h_ret = None
                fixed_8h_ret = None
                if entry_idx + 4 < len(candles):
                    fixed_4h_ret = (candles.iloc[entry_idx + 4]['close'] / entry_price - 1) - BASE_COST
                if entry_idx + 8 < len(candles):
                    fixed_8h_ret = (candles.iloc[entry_idx + 8]['close'] / entry_price - 1) - BASE_COST

                # Event metadata
                lag_hours = (signal_ts - ev_ts).total_seconds() / 3600
                event_ret24 = ev.get('event_ret24', np.nan)
                event_rank = ev.get('event_rank_ret24', np.nan)
                event_vol24 = ev.get('event_vol24', np.nan)

                # Event intensity bucket
                if pd.notna(event_ret24):
                    if event_ret24 >= 0.50:
                        ret_bucket = '50%+'
                    elif event_ret24 >= 0.40:
                        ret_bucket = '40-50%'
                    elif event_ret24 >= 0.30:
                        ret_bucket = '30-40%'
                    else:
                        ret_bucket = '<30%'
                else:
                    ret_bucket = 'unknown'

                # Rank bucket
                if pd.notna(event_rank):
                    if event_rank <= 1:
                        rank_bucket = 'rank1'
                    elif event_rank <= 5:
                        rank_bucket = 'rank2-5'
                    elif event_rank <= 10:
                        rank_bucket = 'rank6-10'
                    elif event_rank <= 20:
                        rank_bucket = 'rank11-20'
                    else:
                        rank_bucket = 'rank21+'
                else:
                    rank_bucket = 'unknown'

                row = {
                    'symbol': sym,
                    'event_ts': ev_ts,
                    'signal_ts': signal_ts,
                    'entry_price': entry_price,
                    'lag_hours': lag_hours,
                    'event_ret24': event_ret24,
                    'event_rank_ret24': event_rank,
                    'event_vol24': event_vol24,
                    'ret_bucket': ret_bucket,
                    'rank_bucket': rank_bucket,
                    'year': signal_ts.year,
                    'funding': first_trade.get('funding_at_signal', np.nan),
                    'fixed_4h_ret': fixed_4h_ret,
                    'fixed_8h_ret': fixed_8h_ret,
                }

                # Simulate TP/SL configs
                for name, tp, sl in TP_SL_CONFIGS:
                    if name == 'trail_3pct':
                        result = simulate_trailing_stop(candles, entry_idx, entry_price, 0.03, BASE_COST)
                    else:
                        result = simulate_tpsl(candles, entry_idx, entry_price, tp, sl, BASE_COST)
                    if result:
                        row[f'{name}_ret'] = result['exit_ret']
                        row[f'{name}_type'] = result['exit_type']
                        row[f'{name}_hold'] = result['hold_hours']
                    else:
                        row[f'{name}_ret'] = np.nan
                        row[f'{name}_type'] = 'no_data'
                        row[f'{name}_hold'] = np.nan

                all_results.append(row)
                trade_count += 1
        print(f'  Symbols processed: {sym_count}, matched trades: {trade_count}')
        print(f'  Skipped: no_trade={skip_no_trade}, no_candle={skip_no_candle}, no_price={skip_no_price}')

    if not all_results:
        print('[ERROR] No results generated!')
        return

    df = pd.DataFrame(all_results)
    df.to_csv(OUT / 'all_trades_tpsl.csv', index=False)
    print(f'\n[total] {len(df)} trades saved')

    # =========================================================
    # Analysis 1: TP/SL effectiveness
    # =========================================================
    print('\n' + '=' * 70)
    print('ANALYSIS 1: TP/SL Effectiveness')
    print('=' * 70)

    tpsl_summary = []
    ret_cols = [c for c in df.columns if c.endswith('_ret')]

    for col in ret_cols:
        vals = df[col].dropna()
        if len(vals) < 20:
            continue
        config_name = col.replace('_ret', '')
        exit_type_col = f'{config_name}_type'
        hold_col = f'{config_name}_hold'

        tp_pct = (df[exit_type_col] == 'tp').mean() if exit_type_col in df else np.nan
        sl_pct = (df[exit_type_col] == 'sl').mean() if exit_type_col in df else np.nan
        timeout_pct = (df[exit_type_col] == 'timeout').mean() if exit_type_col in df else np.nan
        trail_pct = (df[exit_type_col] == 'trail').mean() if exit_type_col in df else np.nan

        row = {
            'config': config_name,
            'n': len(vals),
            'mean': float(vals.mean()),
            'median': float(vals.median()),
            'std': float(vals.std()),
            'winrate': float((vals > 0).mean()),
            'pf': pf(vals.values),
            'p10': float(vals.quantile(0.10)),
            'p25': float(vals.quantile(0.25)),
            'p75': float(vals.quantile(0.75)),
            'p90': float(vals.quantile(0.90)),
            'tp_pct': float(tp_pct) if not np.isnan(tp_pct) else np.nan,
            'sl_pct': float(sl_pct) if not np.isnan(sl_pct) else np.nan,
            'timeout_pct': float(timeout_pct) if not np.isnan(timeout_pct) else np.nan,
            'trail_pct': float(trail_pct) if not np.isnan(trail_pct) else np.nan,
            'avg_hold_h': float(df[hold_col].mean()) if hold_col in df else np.nan,
        }
        tpsl_summary.append(row)
        sign = '+' if row['mean'] > 0 else ''
        med_sign = '+' if row['median'] > 0 else ''
        print(f"  {config_name:15s}  n={row['n']:4d}  mean={sign}{row['mean']:.4f}  "
              f"median={med_sign}{row['median']:.4f}  wr={row['winrate']:.1%}  "
              f"pf={row['pf']:.2f}  tp={row['tp_pct']:.1%} sl={row['sl_pct']:.1%}  "
              f"hold={row['avg_hold_h']:.1f}h")

    tpsl_df = pd.DataFrame(tpsl_summary)
    tpsl_df.to_csv(OUT / 'tpsl_summary.csv', index=False)

    # =========================================================
    # Analysis 2: Event intensity stratification
    # =========================================================
    print('\n' + '=' * 70)
    print('ANALYSIS 2: Event Intensity Stratification')
    print('=' * 70)

    # Fixed-hold baseline by ret_bucket
    print('\n--- Fixed 4h hold by event ret bucket ---')
    for bucket in ['30-40%', '40-50%', '50%+']:
        sub = df[df['ret_bucket'] == bucket]
        if len(sub) < 10:
            continue
        v = sub['fixed_4h_ret'].dropna()
        print(f"  {bucket:10s}  n={len(v):4d}  mean={v.mean():+.4f}  median={v.median():+.4f}  "
              f"wr={((v > 0).mean()):.1%}  pf={pf(v.values):.2f}")

    # Best TP/SL config by ret_bucket
    print('\n--- Best TP/SL (tp5_sl3) by event ret bucket ---')
    best_col = 'tp5_sl3_ret'
    for bucket in ['30-40%', '40-50%', '50%+']:
        sub = df[df['ret_bucket'] == bucket]
        if len(sub) < 10:
            continue
        v = sub[best_col].dropna()
        if len(v) < 10:
            continue
        exit_types = sub['tp5_sl3_type'].value_counts(normalize=True)
        tp_pct = exit_types.get('tp', 0)
        sl_pct = exit_types.get('sl', 0)
        print(f"  {bucket:10s}  n={len(v):4d}  mean={v.mean():+.4f}  median={v.median():+.4f}  "
              f"wr={((v > 0).mean()):.1%}  pf={pf(v.values):.2f}  tp={tp_pct:.1%} sl={sl_pct:.1%}")

    # =========================================================
    # Analysis 3: Cross-stratification (ret_bucket × rank_bucket)
    # =========================================================
    print('\n' + '=' * 70)
    print('ANALYSIS 3: ret_bucket × rank_bucket (tp5_sl3)')
    print('=' * 70)

    cross_rows = []
    for ret_b in ['30-40%', '40-50%', '50%+']:
        for rank_b in ['rank1', 'rank2-5', 'rank6-10', 'rank11-20']:
            sub = df[(df['ret_bucket'] == ret_b) & (df['rank_bucket'] == rank_b)]
            if len(sub) < 10:
                continue
            v = sub[best_col].dropna()
            if len(v) < 10:
                continue
            cross_rows.append({
                'ret_bucket': ret_b,
                'rank_bucket': rank_b,
                'n': len(v),
                'mean': float(v.mean()),
                'median': float(v.median()),
                'winrate': float((v > 0).mean()),
                'pf': pf(v.values),
            })
            med_sign = '+' if v.median() > 0 else ''
            print(f"  {ret_b:10s} × {rank_b:10s}  n={len(v):4d}  "
                  f"mean={v.mean():+.4f}  median={med_sign}{v.median():+.4f}  "
                  f"wr={((v > 0).mean()):.1%}  pf={pf(v.values):.2f}")

    if cross_rows:
        pd.DataFrame(cross_rows).to_csv(OUT / 'cross_ret_rank_tpsl.csv', index=False)

    # =========================================================
    # Analysis 4: Yearly stability of best config
    # =========================================================
    print('\n' + '=' * 70)
    print('ANALYSIS 4: Yearly stability (tp5_sl3, all events)')
    print('=' * 70)

    yearly_rows = []
    for year in sorted(df['year'].unique()):
        sub = df[df['year'] == year]
        v = sub[best_col].dropna()
        if len(v) < 5:
            continue
        exit_types = sub['tp5_sl3_type'].value_counts(normalize=True)
        yearly_rows.append({
            'year': year,
            'n': len(v),
            'mean': float(v.mean()),
            'median': float(v.median()),
            'winrate': float((v > 0).mean()),
            'pf': pf(v.values),
            'tp_pct': float(exit_types.get('tp', 0)),
            'sl_pct': float(exit_types.get('sl', 0)),
        })
        med_sign = '+' if v.median() > 0 else ''
        print(f"  {year}  n={len(v):4d}  mean={v.mean():+.4f}  median={med_sign}{v.median():+.4f}  "
              f"wr={((v > 0).mean()):.1%}  pf={pf(v.values):.2f}  "
              f"tp={exit_types.get('tp', 0):.1%} sl={exit_types.get('sl', 0):.1%}")

    if yearly_rows:
        pd.DataFrame(yearly_rows).to_csv(OUT / 'yearly_tpsl.csv', index=False)

    # =========================================================
    # Analysis 5: 50%+ events deep dive
    # =========================================================
    print('\n' + '=' * 70)
    print('ANALYSIS 5: 50%+ events deep dive (all configs)')
    print('=' * 70)

    strong = df[df['ret_bucket'] == '50%+']
    print(f'  Total 50%+ events with V4 signal: {len(strong)}')

    strong_rows = []
    for col in ret_cols:
        config_name = col.replace('_ret', '')
        v = strong[col].dropna()
        if len(v) < 5:
            continue
        exit_type_col = f'{config_name}_type'
        exit_types = strong[exit_type_col].value_counts(normalize=True) if exit_type_col in strong else {}
        row = {
            'config': config_name,
            'n': len(v),
            'mean': float(v.mean()),
            'median': float(v.median()),
            'winrate': float((v > 0).mean()),
            'pf': pf(v.values),
            'tp_pct': float(exit_types.get('tp', 0)),
            'sl_pct': float(exit_types.get('sl', 0)),
        }
        strong_rows.append(row)
        med_sign = '+' if row['median'] > 0 else ''
        print(f"  {config_name:15s}  n={row['n']:4d}  mean={row['mean']:+.4f}  "
              f"median={med_sign}{row['median']:.4f}  wr={row['winrate']:.1%}  "
              f"pf={row['pf']:.2f}  tp={row['tp_pct']:.1%} sl={row['sl_pct']:.1%}")

    if strong_rows:
        pd.DataFrame(strong_rows).to_csv(OUT / 'strong_events_tpsl.csv', index=False)

    # =========================================================
    # Save verdict
    # =========================================================
    # Find best config: highest PF with median > 0 (or closest to 0)
    best_config = None
    best_pf = 0
    for row in tpsl_summary:
        if row['n'] < 50:
            continue
        # Prefer configs where median is positive
        if row['median'] > 0 and row['pf'] > best_pf:
            best_pf = row['pf']
            best_config = row

    # If no config has positive median, find the one with median closest to 0
    if best_config is None:
        for row in tpsl_summary:
            if row['n'] < 50:
                continue
            if best_config is None or abs(row['median']) < abs(best_config['median']):
                best_config = row

    verdict = {
        'question_1_tpsl': {
            'answer': 'See tpsl_summary.csv',
            'best_config': best_config,
            'any_positive_median': any(r['median'] > 0 for r in tpsl_summary if r['n'] >= 50),
        },
        'question_2_event_intensity': {
            'answer': 'See strong_events_tpsl.csv and cross_ret_rank_tpsl.csv',
            'n_50plus_events': int(len(df[df['ret_bucket'] == '50%+'])),
            'n_30_40_events': int(len(df[df['ret_bucket'] == '30-40%'])),
            'n_40_50_events': int(len(df[df['ret_bucket'] == '40-50%'])),
        },
        'total_trades': int(len(df)),
        'generated_at': pd.Timestamp.now('UTC').isoformat(),
    }

    (OUT / 'verdict.json').write_text(json.dumps(verdict, indent=2, default=str), encoding='utf-8')
    print(f'\n[done] Results saved to {OUT}')


if __name__ == '__main__':
    main()
