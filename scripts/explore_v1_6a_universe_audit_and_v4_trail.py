"""
Audit & new analysis for v1.6a strategy:

Q1: Universe audit — do results differ between:
  (a) Rank450-based event overlay (pre-filtered universe)
  (b) Full-universe event detection (683 symbols, all timestamps)

Q2: Can V4 signal alone (no event filter) become profitable with trailing stop?
  Original: V4 full-universe 4h fixed → mean -0.16%, 41.7% wr (NEGATIVE)
  New: V4 full-universe + trailing stop 1-5%

Output: JSON + CSV for report generation
"""

import pandas as pd
import numpy as np
import os, glob, json
from datetime import timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(SCRIPT_DIR, '..')
OUTDIR = os.path.join(BASE, 'reports', 'artifacts', 'binance_event_study_v1_6a_audit')
os.makedirs(OUTDIR, exist_ok=True)

CACHE = os.path.join(BASE, 'data', 'binance_1h_candles_cache')
EVENT_FILE = os.path.join(BASE, 'reports', 'artifacts',
    'binance_event_study_v1_6a_realtime_event_overlay', 'events_rank20_ret30_vol5m.csv')
OOS_TRADES = os.path.join(BASE, 'reports', 'artifacts',
    'binance_event_study_v1_6a_oos', 'all_trades_full_universe.csv')

print("=" * 60)
print("V1.6A AUDIT: Universe Bias + V4 Trailing Stop")
print("=" * 60)

# ── Load event overlay ──────────────────────────────────────
print("\n[1/6] Loading event overlay...")
events = pd.read_csv(EVENT_FILE, parse_dates=['event_ts'])
print(f"  Events: {len(events)}, symbols: {events['symbol'].nunique()}")

# ── Q1: Re-detect events from full 1h data ─────────────────
print("\n[2/6] Q1: Re-detecting events from full 1h universe...")

cache_files = sorted(glob.glob(os.path.join(CACHE, '*.parquet')))
# Exclude BTC and ETH (reference data, not tradeable altcoins in rank context)
symbols = [os.path.basename(f).replace('_1h.parquet', '') for f in cache_files
           if 'BTCUSDT' not in f and 'ETHUSDT' not in f]

RANK_THRESHOLD = 20
RET_THRESHOLD = 0.30
VOL_THRESHOLD = 5_000_000
LOOKBACK_H = 24

all_detected_events = []
symbols_processed = 0

for cache_file in cache_files:
    sym = os.path.basename(cache_file).replace('_1h.parquet', '')
    if sym in ('BTCUSDT', 'ETHUSDT'):
        continue
    try:
        df = pd.read_parquet(cache_file)
    except:
        continue
    if len(df) < LOOKBACK_H + 2:
        continue

    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    ts = pd.to_datetime(df['timestamp'], utc=True)
    close = df['close'].astype(float).values
    volume = (df['close'] * df['volume']).values  # quote volume

    symbols_processed += 1

    # Rolling 24h stats (no lookahead — uses [T-23, T])
    for i in range(LOOKBACK_H, len(ts)):
        if close[i - LOOKBACK_H] <= 0:
            continue
        ret24 = (close[i] / close[i - LOOKBACK_H]) - 1.0
        vol24 = volume[i - LOOKBACK_H + 1:i + 1].sum()

        if ret24 >= RET_THRESHOLD and vol24 >= VOL_THRESHOLD:
            all_detected_events.append({
                'symbol': sym,
                'event_ts': ts.iloc[i].isoformat(),
                'ret24': ret24,
                'vol24': vol24,
            })

full_events_df = pd.DataFrame(all_detected_events)
if len(full_events_df) > 0:
    full_events_df['event_ts'] = pd.to_datetime(full_events_df['event_ts'], utc=True)
print(f"  Full-universe detection: {len(full_events_df)} events across {full_events_df['symbol'].nunique()} symbols")
print(f"  Event overlay: {len(events)} events across {events['symbol'].nunique()} symbols")

# Compare
overlay_syms = set(events['symbol'].unique())
full_syms = set(full_events_df['symbol'].unique()) if len(full_events_df) > 0 else set()
missing_from_full = overlay_syms - full_syms
extra_in_full = full_syms - overlay_syms

print(f"\n  Overlay symbols not in full detection: {len(missing_from_full)}")
if missing_from_full:
    print(f"    Examples: {list(missing_from_full)[:10]}")
print(f"  Full detection symbols not in overlay: {len(extra_in_full)}")
if extra_in_full:
    print(f"    Examples: {list(extra_in_full)[:10]}")

# ── Load V4 signals from OOS trades ─────────────────────────
print("\n[3/6] Loading V4 signals from OOS trades...")
v4 = pd.read_csv(OOS_TRADES, parse_dates=['signal_ts'])
v4['signal_ts'] = pd.to_datetime(v4['signal_ts'], utc=True)
# Filter to altcoins only
v4 = v4[~v4['symbol'].isin(['BTCUSDT', 'ETHUSDT'])]
v4['signal_ts_ns'] = v4['signal_ts'].dt.as_unit('ns').astype(np.int64)
print(f"  V4 signals (altcoins): {len(v4)}")

# ── Q1b: For each event source, find V4 signals in [T+1, T+48h] ──
print("\n[4/6] Q1: Matching V4 signals to events from both sources...")

def match_events_to_v4(events_df, v4_df, label):
    """For each event, find V4 signals in [event_ts + 1h, event_ts + 48h]"""
    if len(events_df) == 0:
        return pd.DataFrame()

    matched = []
    for sym in events_df['symbol'].unique():
        sym_events = events_df[events_df['symbol'] == sym].sort_values('event_ts')
        sym_v4 = v4_df[v4_df['symbol'] == sym].sort_values('signal_ts')
        if len(sym_v4) == 0:
            continue

        v4_ts = sym_v4['signal_ts'].values

        for _, ev in sym_events.iterrows():
            ev_ts = ev['event_ts']
            t_lo = ev_ts + pd.Timedelta(hours=1)
            t_hi = ev_ts + pd.Timedelta(hours=48)

            mask = (v4_ts >= t_lo) & (v4_ts <= t_hi)
            idxs = np.where(mask)[0]

            for idx in idxs:
                row = sym_v4.iloc[idx]
                matched.append({
                    'symbol': sym,
                    'event_ts': ev_ts,
                    'event_ret24': ev.get('ret24', np.nan),
                    'signal_ts': row['signal_ts'],
                    'pnl_4h': row['pnl_4h'],
                    'ret_4h': row['ret_4h'],
                })

    df = pd.DataFrame(matched)
    print(f"  {label}: {len(df)} matched trades")
    if len(df) > 0:
        wins = (df['ret_4h'] > 0).sum()
        print(f"    4h fixed: mean={df['ret_4h'].mean()*100:.2f}%, "
              f"median={df['ret_4h'].median()*100:.2f}%, "
              f"wr={wins/len(df)*100:.1f}%")
    return df

overlay_matched = match_events_to_v4(events, v4, "Event overlay (rank450-derived)")
full_matched = match_events_to_v4(full_events_df, v4, "Full-universe detection")

# ── Q2: V4 full universe + trailing stop ────────────────────
print("\n[5/6] Q2: V4 full-universe + trailing stop simulation...")

# Load candles for ALL symbols that have V4 signals
v4_syms = set(v4['symbol'].unique())
print(f"  V4 symbols: {len(v4_syms)}")

# Cache: load all candles for V4 symbols
sym_candles = {}
for cache_file in cache_files:
    sym = os.path.basename(cache_file).replace('_1h.parquet', '')
    if sym not in v4_syms:
        continue
    try:
        df = pd.read_parquet(cache_file)
        df = df.sort_values('timestamp').reset_index(drop=True)
        df['ts'] = pd.to_datetime(df['timestamp'], utc=True)
        df['ts_ns'] = df['ts'].dt.as_unit('ns').astype(np.int64)
        for c in ['open', 'high', 'low', 'close']:
            df[c] = df[c].astype(float)
        sym_candles[sym] = df[['ts', 'ts_ns', 'open', 'high', 'low', 'close']]
    except:
        continue

print(f"  Loaded candle data for {len(sym_candles)} symbols")

# Trailing stop simulation
trail_pcts = [0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05]

def simulate_trail_stop_on_signals(v4_df, sym_candles_dict, trail_pct, max_hold=48):
    """For each V4 signal, enter at signal close, use trailing stop."""
    results = []

    for _, row in v4_df.iterrows():
        sym = row['symbol']
        sig_ns = row['signal_ts_ns']

        if sym not in sym_candles_dict:
            continue
        candles = sym_candles_dict[sym]

        # Find signal candle index
        idx_arr = np.searchsorted(candles['ts_ns'].values, sig_ns, side='right') - 1
        if idx_arr < 0 or idx_arr >= len(candles) - 1:
            continue

        # Entry at signal candle close
        entry_price = candles['close'].iloc[idx_arr]
        if entry_price <= 0:
            continue

        trail_stop = entry_price * (1.0 - trail_pct)
        peak = entry_price
        exit_ret = None
        bars_held = 0

        for j in range(idx_arr + 1, min(idx_arr + 1 + max_hold, len(candles))):
            bar = candles.iloc[j]
            bars_held += 1

            # Update peak
            if bar['high'] > peak:
                peak = bar['high']
                trail_stop = peak * (1.0 - trail_pct)

            # Check if low breaches trail stop
            if bar['low'] <= trail_stop:
                # Exit at trail stop price (or open if it gaps below)
                exit_price = max(trail_stop, bar['open'])
                exit_price = min(exit_price, bar['high'])
                exit_price = max(exit_price, bar['low'])
                exit_ret = (exit_price / entry_price) - 1.0
                break

            # Check max hold
            if bars_held >= max_hold:
                exit_ret = (bar['close'] / entry_price) - 1.0
                break

        if exit_ret is None:
            # Use last available candle close
            last_idx = min(idx_arr + max_hold, len(candles) - 1)
            exit_ret = (candles['close'].iloc[last_idx] / entry_price) - 1.0

        results.append({
            'symbol': sym,
            'signal_ts': row['signal_ts'],
            'ret_trail': exit_ret,
            'trail_pct': trail_pct,
        })

    return pd.DataFrame(results)

v4_trail_results = {}
for tp in trail_pcts:
    print(f"    Trail {tp*100:.1f}%...", end=' ')
    df = simulate_trail_stop_on_signals(v4, sym_candles, tp, max_hold=48)
    v4_trail_results[tp] = df
    if len(df) > 0:
        wins = (df['ret_trail'] > 0).sum()
        wins_excl = (df['ret_trail'] > 0.001).sum()
        gains = df.loc[df['ret_trail'] > 0, 'ret_trail']
        losses = df.loc[df['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        print(f"n={len(df):,}, mean={df['ret_trail'].mean()*100:.2f}%, "
              f"median={df['ret_trail'].median()*100:.2f}%, "
              f"wr={wins/len(df)*100:.1f}%, "
              f"PF={gross_gains/gross_losses:.2f}")
    else:
        print("no trades")

# ── Also simulate trailing stop on event+V4 matched trades ──
print("\n[5b/6] Event+V4 with trailing stop (for comparison)...")
def match_and_trail(events_df, v4_df, sym_candles_dict, trail_pct, max_hold=48, label=""):
    """Match events to V4, then apply trailing stop."""
    matched = []
    v4_by_sym = {}
    for sym in v4_df['symbol'].unique():
        v4_by_sym[sym] = v4_df[v4_df['symbol'] == sym].sort_values('signal_ts')

    for sym in events_df['symbol'].unique():
        if sym not in v4_by_sym:
            continue
        sym_events = events_df[events_df['symbol'] == sym].sort_values('event_ts')
        sym_v4 = v4_by_sym[sym]
        v4_ts = sym_v4['signal_ts'].values

        for _, ev in sym_events.iterrows():
            ev_ts = ev['event_ts']
            t_lo = ev_ts + pd.Timedelta(hours=1)
            t_hi = ev_ts + pd.Timedelta(hours=48)

            mask = (v4_ts >= t_lo) & (v4_ts <= t_hi)
            idxs = np.where(mask)[0]

            for idx in idxs:
                row = sym_v4.iloc[idx]
                matched.append({
                    'symbol': sym,
                    'signal_ts': row['signal_ts'],
                    'signal_ts_ns': row['signal_ts_ns'],
                    'event_ts': ev_ts,
                    'event_ret24': ev.get('ret24', np.nan),
                    'ret_4h': row['ret_4h'],
                })

    if not matched:
        return pd.DataFrame()

    matched_df = pd.DataFrame(matched)
    # Apply trailing stop
    results = []
    for _, row in matched_df.iterrows():
        sym = row['symbol']
        sig_ns = row['signal_ts_ns']
        if sym not in sym_candles_dict:
            continue
        candles = sym_candles_dict[sym]
        idx_arr = np.searchsorted(candles['ts_ns'].values, sig_ns, side='right') - 1
        if idx_arr < 0 or idx_arr >= len(candles) - 1:
            continue

        entry_price = candles['close'].iloc[idx_arr]
        if entry_price <= 0:
            continue

        trail_stop = entry_price * (1.0 - trail_pct)
        peak = entry_price
        exit_ret = None
        bars_held = 0

        for j in range(idx_arr + 1, min(idx_arr + 1 + max_hold, len(candles))):
            bar = candles.iloc[j]
            bars_held += 1
            if bar['high'] > peak:
                peak = bar['high']
                trail_stop = peak * (1.0 - trail_pct)
            if bar['low'] <= trail_stop:
                exit_price = max(trail_stop, bar['open'])
                exit_price = min(exit_price, bar['high'])
                exit_price = max(exit_price, bar['low'])
                exit_ret = (exit_price / entry_price) - 1.0
                break
            if bars_held >= max_hold:
                exit_ret = (bar['close'] / entry_price) - 1.0
                break

        if exit_ret is None:
            last_idx = min(idx_arr + max_hold, len(candles) - 1)
            exit_ret = (candles['close'].iloc[last_idx] / entry_price) - 1.0

        results.append({
            'symbol': sym,
            'signal_ts': row['signal_ts'],
            'event_ts': row['event_ts'],
            'event_ret24': row['event_ret24'],
            'ret_4h': row['ret_4h'],
            'ret_trail': exit_ret,
        })

    return pd.DataFrame(results)

# Compare event+V4 trail 2% between overlay and full-universe
event_trail_comparison = {}
for source_name, source_df in [("overlay", events), ("full_universe", full_events_df)]:
    if len(source_df) == 0:
        continue
    print(f"  Event+V4 trail 2% ({source_name})...", end=' ')
    df = match_and_trail(source_df, v4, sym_candles, 0.02, 48, source_name)
    event_trail_comparison[source_name] = df
    if len(df) > 0:
        wins = (df['ret_trail'] > 0).sum()
        gains = df.loc[df['ret_trail'] > 0, 'ret_trail']
        losses = df.loc[df['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        print(f"n={len(df):,}, mean={df['ret_trail'].mean()*100:.2f}%, "
              f"median={df['ret_trail'].median()*100:.2f}%, "
              f"wr={wins/len(df)*100:.1f}%, "
              f"PF={gross_gains/gross_losses:.2f}")
    else:
        print("no trades")

# ── Yearly breakdown for V4 trail 2% ────────────────────────
print("\n[6/6] V4 trail 2% yearly breakdown...")
v4_trail_2pct = v4_trail_results.get(0.02, pd.DataFrame())
if len(v4_trail_2pct) > 0:
    v4_trail_2pct['year'] = pd.to_datetime(v4_trail_2pct['signal_ts']).dt.year
    for yr, grp in v4_trail_2pct.groupby('year'):
        wins = (grp['ret_trail'] > 0).sum()
        gains = grp.loc[grp['ret_trail'] > 0, 'ret_trail']
        losses = grp.loc[grp['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        print(f"  {yr}: n={len(grp):,}, mean={grp['ret_trail'].mean()*100:.2f}%, "
              f"median={grp['ret_trail'].median()*100:.2f}%, "
              f"wr={wins/len(grp)*100:.1f}%, PF={gross_gains/gross_losses:.2f}")

# ── Save outputs ────────────────────────────────────────────
print("\n" + "=" * 60)
print("SAVING OUTPUTS...")

# Q1 comparison
q1_summary = {
    'event_overlay': {
        'events': len(events),
        'symbols': events['symbol'].nunique(),
        'matched_v4_4h': len(overlay_matched),
        'mean_4h': float(overlay_matched['ret_4h'].mean()) if len(overlay_matched) > 0 else None,
        'median_4h': float(overlay_matched['ret_4h'].median()) if len(overlay_matched) > 0 else None,
    },
    'full_universe_detection': {
        'events': len(full_events_df),
        'symbols': full_events_df['symbol'].nunique() if len(full_events_df) > 0 else 0,
        'matched_v4_4h': len(full_matched),
        'mean_4h': float(full_matched['ret_4h'].mean()) if len(full_matched) > 0 else None,
        'median_4h': float(full_matched['ret_4h'].median()) if len(full_matched) > 0 else None,
    },
    'missing_from_full': list(missing_from_full)[:20],
    'extra_in_full': list(extra_in_full)[:20],
}

# Event+V4 trail comparison
for src, df in event_trail_comparison.items():
    if len(df) > 0:
        wins = (df['ret_trail'] > 0).sum()
        gains = df.loc[df['ret_trail'] > 0, 'ret_trail']
        losses = df.loc[df['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        q1_summary[f'{src}_trail_2pct'] = {
            'trades': len(df),
            'mean': float(df['ret_trail'].mean()),
            'median': float(df['ret_trail'].median()),
            'winrate': float(wins / len(df)),
            'pf': float(gross_gains / gross_losses),
        }

with open(os.path.join(OUTDIR, 'q1_universe_audit.json'), 'w') as f:
    json.dump(q1_summary, f, indent=2, default=str)
print(f"  q1_universe_audit.json saved")

# Q2 V4 trail results
q2_summary = {'v4_full_universe_trailing_stop': {}}
for tp, df in v4_trail_results.items():
    if len(df) > 0:
        wins = (df['ret_trail'] > 0).sum()
        wins_excl = (df['ret_trail'] > 0.001).sum()
        gains = df.loc[df['ret_trail'] > 0, 'ret_trail']
        losses = df.loc[df['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        q2_summary['v4_full_universe_trailing_stop'][f'trail_{tp*100:.1f}pct'] = {
            'trades': len(df),
            'mean': float(df['ret_trail'].mean()),
            'median': float(df['ret_trail'].median()),
            'winrate': float(wins / len(df)),
            'winrate_excl': float(wins_excl / len(df)),
            'pf': float(gross_gains / gross_losses),
        }

# V4 trail 2% yearly
if len(v4_trail_2pct) > 0:
    yearly = {}
    for yr, grp in v4_trail_2pct.groupby('year'):
        wins = (grp['ret_trail'] > 0).sum()
        gains = grp.loc[grp['ret_trail'] > 0, 'ret_trail']
        losses = grp.loc[grp['ret_trail'] <= 0, 'ret_trail']
        gross_gains = gains.sum() if len(gains) > 0 else 0
        gross_losses = abs(losses.sum()) if len(losses) > 0 else 1e-9
        yearly[str(yr)] = {
            'trades': len(grp),
            'mean': float(grp['ret_trail'].mean()),
            'median': float(grp['ret_trail'].median()),
            'winrate': float(wins / len(grp)),
            'pf': float(gross_gains / gross_losses),
        }
    q2_summary['v4_trail_2pct_yearly'] = yearly

with open(os.path.join(OUTDIR, 'q2_v4_trailing_stop.json'), 'w') as f:
    json.dump(q2_summary, f, indent=2, default=str)
print(f"  q2_v4_trailing_stop.json saved")

# Save V4 trail 2% trades CSV
if len(v4_trail_2pct) > 0:
    v4_trail_2pct.to_csv(os.path.join(OUTDIR, 'v4_trail_2pct_trades.csv'), index=False)
    print(f"  v4_trail_2pct_trades.csv saved ({len(v4_trail_2pct)} trades)")

# Save full-universe detected events
if len(full_events_df) > 0:
    full_events_df.to_csv(os.path.join(OUTDIR, 'full_universe_events_detected.csv'), index=False)
    print(f"  full_universe_events_detected.csv saved ({len(full_events_df)} events)")

print(f"\n{'='*60}")
print("AUDIT COMPLETE")
print(f"{'='*60}")
