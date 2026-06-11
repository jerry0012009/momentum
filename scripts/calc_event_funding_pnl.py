"""
Calculate per-trade funding PnL for the v1_6 event study trades.

Binance perpetual funding is charged every 8h at 00:00, 08:00, 16:00 UTC.
For LONG positions: funding > 0 means longs PAY shorts (negative for us)
                    funding < 0 means shorts PAY longs (positive for us)
So funding_pnl_pct = -sum(funding_rates_during_hold)

Input: all_trades_funding.csv + raw monthly funding zips
Output: all_trades_with_funding_pnl.csv
"""

import pandas as pd
import numpy as np
import os
import zipfile
import glob
from datetime import datetime, timezone

RAW_DIR = 'data/binance_funding_rate'
FUNDING_8H_HOURS = 8  # funding every 8h
FUNDING_TIMES = [0, 8, 16]  # UTC hours

# Map of symbol -> DataFrame with funding data
_funding_cache = {}

def load_funding_data(symbol):
    """Load all funding data for a symbol from monthly zips."""
    if symbol in _funding_cache:
        return _funding_cache[symbol]

    sym_dir = os.path.join(RAW_DIR, symbol)
    if not os.path.isdir(sym_dir):
        _funding_cache[symbol] = None
        return None

    frames = []
    for zf in sorted(glob.glob(os.path.join(sym_dir, '*.zip'))):
        try:
            with zipfile.ZipFile(zf) as z:
                for name in z.namelist():
                    if name.endswith('.csv'):
                        with z.open(name) as f:
                            df = pd.read_csv(f)
                            # Binance monthly format: calc_time (Unix ms), funding_interval_hours, last_funding_rate
                            if 'last_funding_rate' in df.columns:
                                df['timestamp'] = pd.to_datetime(df['calc_time'], unit='ms', utc=True)
                                df['funding_rate'] = df['last_funding_rate'].astype(float)
                            elif 'fundingRate' in df.columns:
                                ts_col = [c for c in df.columns if 'time' in c.lower() or 'calc' in c.lower()][0]
                                df = df.rename(columns={ts_col: 'timestamp', 'fundingRate': 'funding_rate'})
                                df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                            df = df.sort_values('timestamp')
                            frames.append(df[['timestamp', 'funding_rate']])
        except Exception:
            continue

    if not frames:
        _funding_cache[symbol] = None
        return None

    result = pd.concat(frames, ignore_index=True).drop_duplicates('timestamp').sort_values('timestamp')
    result = result.reset_index(drop=True)
    _funding_cache[symbol] = result
    return result


def calc_funding_pnl(symbol, signal_ts, exit_ts):
    """
    Calculate total funding PnL for a long position held from signal_ts to exit_ts.

    Returns:
        (funding_pnl_pct, num_funding_events)
    """
    if pd.isna(exit_ts) or pd.isna(signal_ts):
        return 0.0, 0

    fd = load_funding_data(symbol)
    if fd is None or len(fd) == 0:
        return np.nan, 0

    # Find funding events between signal and exit
    mask = (fd['timestamp'] >= signal_ts) & (fd['timestamp'] <= exit_ts)
    events = fd[mask]

    if len(events) == 0:
        return 0.0, 0

    # For long positions:
    # funding > 0 (longs pay shorts) = negative PnL for us
    # funding < 0 (shorts pay longs) = positive PnL for us
    total_funding = events['funding_rate'].sum()
    funding_pnl = -total_funding  # negate because we're long

    return funding_pnl, len(events)


def main():
    # Load trades
    trades_path = 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_funding.csv'
    trades = pd.read_csv(trades_path)

    # Parse timestamps
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)

    # For trailing stop trades, compute exit_ts from hold periods
    # Use tp5_sl3 as the main strategy (similar to live config)
    hold_col = 'tp5_sl3_hold'  # hours
    if hold_col not in trades.columns:
        # Try trailing stop
        hold_col = 'trail_3pct_hold'

    trades['exit_ts'] = trades['signal_ts'] + pd.to_timedelta(trades[hold_col], unit='h')

    # Calculate funding PnL for each trade
    print(f'Calculating funding PnL for {len(trades)} trades...')
    results = trades.apply(
        lambda r: calc_funding_pnl(r['symbol'], r['signal_ts'], r['exit_ts']),
        axis=1, result_type='expand'
    )
    results.columns = ['funding_pnl_pct', 'funding_events']

    trades['funding_pnl_pct'] = results['funding_pnl_pct']
    trades['funding_events'] = results['funding_events']

    # Save
    out_path = 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_with_funding_pnl.csv'
    trades.to_csv(out_path, index=False)

    # Summary
    valid = trades.dropna(subset=['funding_pnl_pct'])
    na_count = trades['funding_pnl_pct'].isna().sum()

    print(f'\n=== Funding PnL Summary ===')
    print(f'Total trades: {len(trades)}')
    print(f'Trades with funding data: {len(valid)}')
    print(f'Trades without funding data: {na_count}')
    print(f'Mean funding PnL: {valid["funding_pnl_pct"].mean()*100:.3f}%')
    print(f'Total funding PnL: {valid["funding_pnl_pct"].sum()*100:.1f}%')
    print(f'Mean funding events per trade: {valid["funding_events"].mean():.1f}')

    # By year
    valid['year'] = pd.to_datetime(valid['signal_ts']).dt.year
    print(f'\n=== By Year ===')
    for yr in sorted(valid['year'].unique()):
        yr_data = valid[valid['year'] == yr]
        print(f'{yr}: n={len(yr_data)}  mean={yr_data["funding_pnl_pct"].mean()*100:.3f}%  total={yr_data["funding_pnl_pct"].sum()*100:.1f}%')

    # Compare with price returns
    for col in ['trail_3pct_ret', 'tp5_sl3_ret', 'fixed_8h_ret']:
        if col in trades.columns:
            ret = valid[col].mean() * 100
            fund = valid['funding_pnl_pct'].mean() * 100
            print(f'\n{col}: mean_price_ret={ret:.3f}%  mean_funding={fund:.3f}%  net={ret+fund:.3f}%')

    print(f'\nSaved to: {out_path}')


if __name__ == '__main__':
    main()
