#!/usr/bin/env python3
"""Download funding rate data from Binance Vision S3 for all symbols in trades.

Saves per-symbol CSVs to data/binance_funding_rate/<SYMBOL>/.
Then computes cumulative funding PnL per trade and saves enriched trades CSV.

Usage:
  python3 scripts/download_funding_rate.py          # download only
  python3 scripts/download_funding_rate.py --compute # download + compute
"""

import os, sys, zipfile, io, time, glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
import pandas as pd
import numpy as np

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_funding_rate'
KLINE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
OUT_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_funding.csv'

S3_BASE = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/data/futures/um/monthly/fundingRate'

# Get unique symbols from trades
def get_symbols():
    trades = pd.read_csv(TRADES_F)
    symbols = sorted(trades['symbol'].unique())
    return symbols

def get_month_files(symbol):
    """List available monthly funding rate files for a symbol."""
    url = f'{S3_BASE}/{symbol}/?delimiter=/&prefix={symbol}/'
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req, timeout=15).read().decode('utf-8')
        # Extract filenames from XML
        import re
        files = re.findall(r'<Key>([^<]*\.zip)</Key>', data)
        return files
    except Exception as e:
        return []

def download_and_extract(key):
    """Download a single funding rate zip and return DataFrame."""
    url = f'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision/{key}'
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urlopen(req, timeout=30)
        data = resp.read()
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = [n for n in zf.namelist() if n.endswith('.csv')]
            if not names:
                return None
            with zf.open(names[0]) as f:
                df = pd.read_csv(f)
                # Expected columns: symbol, fundingTime, fundingRate
                if 'calc_time' in df.columns and 'last_funding_rate' in df.columns:
                    # Normalize column names
                    df = df.rename(columns={
                        'calc_time': 'fundingTime',
                        'last_funding_rate': 'fundingRate',
                        'funding_interval_hours': 'interval_hours',
                    })
                    return df[['fundingTime', 'fundingRate']]
                elif 'fundingTime' in df.columns and 'fundingRate' in df.columns:
                    return df[['fundingTime', 'fundingRate']]
                return None
    except Exception as e:
        return None

def download_symbol_funding(symbol, max_workers=4):
    """Download all funding rate data for a symbol."""
    sym_dir = CACHE_DIR / symbol
    if sym_dir.exists():
        # Check if already downloaded
        existing = list(sym_dir.glob('*.csv'))
        if len(existing) > 0:
            return symbol, 'cached', len(existing)

    sym_dir.mkdir(parents=True, exist_ok=True)

    # Get list of monthly files
    keys = get_month_files(symbol)
    if not keys:
        return symbol, 'no_data', 0

    # Download each month
    saved = 0
    for key in keys:
        fname = key.split('/')[-1].replace('.csv.zip', '.csv')
        out_path = sym_dir / fname
        if out_path.exists():
            saved += 1
            continue

        df = download_and_extract(key)
        if df is not None and len(df) > 0:
            df.to_csv(out_path, index=False)
            saved += 1

    return symbol, 'ok', saved

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--compute', action='store_true', help='Compute funding PnL after download')
    parser.add_argument('--workers', type=int, default=8, help='Parallel download workers')
    args = parser.parse_args()

    symbols = get_symbols()
    print(f'Need funding data for {len(symbols)} symbols')

    # Download
    print('Downloading funding rate data from Binance Vision S3...')
    cache_hits = 0
    downloads = 0
    no_data = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_symbol_funding, sym): sym for sym in symbols}
        done = 0
        for future in as_completed(futures):
            sym, status, count = future.result()
            done += 1
            if status == 'cached':
                cache_hits += 1
            elif status == 'ok':
                downloads += 1
            elif status == 'no_data':
                no_data += 1

            if done % 50 == 0 or done == len(symbols):
                print(f'  [{done}/{len(symbols)}] cached={cache_hits} downloaded={downloads} no_data={no_data}')

    print(f'Done. cached={cache_hits} downloaded={downloads} no_data={no_data}')

    if not args.compute:
        print('Pass --compute to compute funding PnL.')
        return

    # Compute funding PnL
    print('\nComputing funding PnL per trade...')
    compute_funding_pnl(symbols)

def compute_funding_pnl(symbols):
    """Load all funding data and compute cumulative funding for each trade."""
    # Load all funding data into memory
    print('Loading funding rate data...')
    funding_data = {}
    for sym in symbols:
        sym_dir = CACHE_DIR / sym
        if not sym_dir.exists():
            continue
        frames = []
        for csv_f in sorted(sym_dir.glob('*.csv')):
            try:
                df = pd.read_csv(csv_f)
                if 'fundingTime' in df.columns and 'fundingRate' in df.columns:
                    frames.append(df[['fundingTime', 'fundingRate']])
                elif 'calc_time' in df.columns and 'last_funding_rate' in df.columns:
                    df = df.rename(columns={'calc_time': 'fundingTime', 'last_funding_rate': 'fundingRate'})
                    frames.append(df[['fundingTime', 'fundingRate']])
            except:
                continue
        if frames:
            all_fr = pd.concat(frames, ignore_index=True)
            all_fr['fundingTime'] = pd.to_numeric(all_fr['fundingTime'], errors='coerce')
            all_fr['fundingRate'] = pd.to_numeric(all_fr['fundingRate'], errors='coerce')
            all_fr = all_fr.dropna().sort_values('fundingTime').drop_duplicates(subset=['fundingTime'])
            funding_data[sym] = all_fr

    print(f'Loaded funding data for {len(funding_data)} symbols')

    # Load kline data for close prices at funding settlement times
    print('Loading kline data for mark price approximation...')
    kline_cache = {}
    for sym in symbols:
        sym_dir = KLINE_DIR / sym
        files = sorted(glob.glob(str(sym_dir / f'{sym}-1h-*.zip')))
        if not files:
            continue
        frames = []
        for f in files:
            try:
                with zipfile.ZipFile(f) as zf:
                    names = [n for n in zf.namelist() if n.endswith('.csv')]
                    if names:
                        with zf.open(names[0]) as fh:
                            df = pd.read_csv(fh, header=None, usecols=[0, 4])
                            df.columns = ['open_time', 'close']
                            frames.append(df)
            except:
                continue
        if frames:
            kdf = pd.concat(frames, ignore_index=True)
            kdf['open_time'] = pd.to_numeric(kdf['open_time'], errors='coerce')
            kdf = kdf.dropna().sort_values('open_time')
            kline_cache[sym] = kdf

    print(f'Loaded kline data for {len(kline_cache)} symbols')

    # Load trades
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()

    # Compute funding PnL for each trade
    print(f'Computing funding PnL for {len(valid)} trades...')
    funding_pnls = []
    funding_events_counts = []

    for idx, row in valid.iterrows():
        sym = row['symbol']
        entry_ts = int(row['signal_ts'].timestamp() * 1000)

        # Determine exit time
        if pd.notna(row.get('trail_3pct_ts')):
            exit_ts = int(pd.Timestamp(row['trail_3pct_ts']).timestamp() * 1000)
        else:
            exit_ts = entry_ts + 96 * 3600 * 1000  # timeout

        # Get funding events during holding period
        if sym not in funding_data:
            funding_pnls.append(0.0)
            funding_events_counts.append(0)
            continue

        fd = funding_data[sym]
        mask = (fd['fundingTime'] >= entry_ts) & (fd['fundingTime'] <= exit_ts)
        events = fd[mask]

        if len(events) == 0:
            funding_pnls.append(0.0)
            funding_events_counts.append(0)
            continue

        # Get close price at each funding settlement time (approximate mark price)
        # For simplicity, use entry_price as approximation (errors are small)
        entry_price = float(row['entry_price'])

        # For LONG: positive rate = we pay, negative rate = we receive
        # funding_pnl_pct = -sum(funding_rate) * (mark_price / entry_price)
        # Since we're using 1x position: funding_pnl_pct ≈ -sum(funding_rate)
        # (because mark_price ≈ entry_price over short periods)

        # More accurate: use close price at each funding time
        total_funding = 0.0
        if sym in kline_cache:
            kdf = kline_cache[sym]
            for _, evt in events.iterrows():
                ft = evt['fundingTime']
                # Find closest kline
                kidx = np.searchsorted(kdf['open_time'].values, ft, side='left')
                if kidx < len(kdf):
                    mark_price = float(kdf['close'].values[kidx])
                else:
                    mark_price = entry_price
                # For long: we pay positive funding, receive negative
                total_funding += -float(evt['fundingRate']) * (mark_price / entry_price)
        else:
            # Fallback: use entry price
            total_funding = -events['fundingRate'].sum()

        funding_pnls.append(total_funding)
        funding_events_counts.append(len(events))

    valid = valid.copy()
    valid['funding_pnl_pct'] = funding_pnls
    valid['funding_events'] = funding_events_counts

    # Save
    valid.to_csv(OUT_F, index=False)
    print(f'Saved enriched trades: {OUT_F}')

    # Summary
    print(f'\n=== Funding Rate Summary ===')
    print(f'Trades with funding data: {sum(1 for p in funding_pnls if p != 0)}')
    print(f'Trades with 0 funding events: {sum(1 for c in funding_events_counts if c == 0)}')
    print(f'Mean funding PnL: {np.mean(funding_pnls)*100:.3f}%')
    print(f'Median funding PnL: {np.median(funding_pnls)*100:.3f}%')
    print(f'Total funding PnL: {np.sum(funding_pnls)*100:.1f}%')
    print(f'Mean funding events per trade: {np.mean(funding_events_counts):.1f}')

    # By year
    valid['year'] = valid['signal_ts'].dt.year
    print(f'\n=== Funding PnL by Year ===')
    for yr in sorted(valid['year'].unique()):
        yr_data = valid[valid['year'] == yr]
        print(f'{yr}: mean={yr_data["funding_pnl_pct"].mean()*100:.3f}%  '
              f'total={yr_data["funding_pnl_pct"].sum()*100:.1f}%  '
              f'events={yr_data["funding_events"].mean():.1f}/trade')

if __name__ == '__main__':
    main()
