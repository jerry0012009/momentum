#!/usr/bin/env python3
"""
v1.6a Out-of-Sample Validation: Run V4 momentum ignition signals on FULL hourly data
=====================================================
Purpose: Test whether the V4 signal (vol_ratio > 3x, ret_1h > 1%) generates alpha
on ALL hourly bars across the full history of Binance perpetual contracts,
NOT just the pre-filtered rank450 (涨跌幅榜) event windows.

Two approaches:
  A) Use the SAME 436 rank450 symbols, but scan their ENTIRE history (not just event windows)
  B) Download ~80 random symbols NOT in rank450, scan their full history

This tests: "Is the signal genuinely predictive, or does it only work on pre-selected winners?"
"""
import pandas as pd
import numpy as np
import zipfile, os, glob, json, time, sys
from pathlib import Path

CACHE_DIR = '/root/clawd/jerry/momentum/data/binance_vision_1h_v1_6/klines'
FUNDING_DIR = '/root/clawd/jerry/momentum/data/binance_vision_rank154/data/futures/um/monthly/fundingRate'
OUT_DIR = '/root/clawd/jerry/momentum/reports/artifacts/binance_event_study_v1_6a_oos'
os.makedirs(OUT_DIR, exist_ok=True)

COST_PER_TRADE = 0.0013  # 0.13% round trip
S3_BASE = "https://data.binance.vision"

# ── Helpers ────────────────────────────────────────────────────

def load_symbol_full(sym):
    """Load all cached 1h klines for a symbol (full history, not event windows)."""
    sym_dir = os.path.join(CACHE_DIR, sym)
    if not os.path.exists(sym_dir):
        return None
    files = sorted(glob.glob(os.path.join(sym_dir, f'{sym}-1h-*.zip')))
    if not files:
        return None
    frames = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith('.csv')]
                if names:
                    with zf.open(names[0]) as fh:
                        df = pd.read_csv(fh)
                        df = df.rename(columns={'count': 'trades', 'taker_buy_volume': 'taker_buy_base'})
                        out = pd.DataFrame({
                            'ts': pd.to_datetime(pd.to_numeric(df['open_time'], errors='coerce'), unit='ms', utc=True),
                            'open': pd.to_numeric(df['open'], errors='coerce'),
                            'high': pd.to_numeric(df['high'], errors='coerce'),
                            'low': pd.to_numeric(df['low'], errors='coerce'),
                            'close': pd.to_numeric(df['close'], errors='coerce'),
                            'volume': pd.to_numeric(df['volume'], errors='coerce'),
                            'quote_volume': pd.to_numeric(df['quote_volume'], errors='coerce'),
                            'taker_buy_quote_volume': pd.to_numeric(df.get('taker_buy_quote_volume', df.get('taker_buy_quote', pd.Series(dtype=float))), errors='coerce'),
                        }).dropna(subset=['ts', 'close'])
                        frames.append(out)
        except:
            continue
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True).sort_values('ts').drop_duplicates('ts')


def load_funding(sym):
    """Load funding rate history for a symbol."""
    sym_dir = os.path.join(FUNDING_DIR, sym)
    if not os.path.exists(sym_dir):
        return None
    files = sorted(glob.glob(os.path.join(sym_dir, f'{sym}-fundingRate-*.zip')))
    if not files:
        return None
    frames = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith('.csv')]
                if names:
                    with zf.open(names[0]) as fh:
                        frames.append(pd.read_csv(fh))
        except:
            continue
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df['ts'] = pd.to_datetime(pd.to_numeric(df['calc_time'], errors='coerce'), unit='ms', utc=True)
    df['funding_rate'] = pd.to_numeric(df['last_funding_rate'], errors='coerce')
    df = df.dropna(subset=['ts', 'funding_rate']).sort_values('ts').drop_duplicates('ts')
    return df[['ts', 'funding_rate']]


def detect_signals_full_history(df, vol_thresh=3.0, ret_thresh=0.01, vol_window=20):
    """Detect V4 signals across ALL bars in the dataframe (not event-filtered)."""
    n = len(df)
    if n < vol_window + 5:
        return []

    rets = df['ret_1h'].values
    vols = df['quote_volume'].values
    closes = df['close'].values
    highs = df['high'].values
    lows = df['low'].values

    # Trailing volume mean
    tv = pd.Series(vols).rolling(vol_window, min_periods=vol_window // 2).mean().values

    signals = []
    prev_bar = -999

    for i in range(vol_window, n - 1):
        # Cooldown: don't re-trigger within 4 bars
        if i - prev_bar < 4:
            continue
        if np.isnan(tv[i]) or tv[i] <= 0:
            continue

        vr = vols[i] / tv[i]
        if vr < vol_thresh:
            continue
        if rets[i] < ret_thresh:
            continue

        signals.append({
            'bar': i,
            'entry_price': closes[i],
            'vol_ratio': vr,
            'ret_at_signal': rets[i],
            'ts': df['ts'].iloc[i],
            'year': df['ts'].iloc[i].year,
        })
        prev_bar = i

    return signals


def simulate_trade_arrays(closes, highs, lows, rets, sig, hold_hours=4):
    """Simulate a trade from signal bar, return net return."""
    bi = sig['bar']
    ep = sig['entry_price']

    cum_ret = 0.0
    exit_bar = bi

    for ho in range(1, hold_hours + 1):
        bar = bi + ho
        if bar >= len(closes):
            exit_bar = bar - 1
            break
        cum_ret = (1 + cum_ret) * (1 + rets[bar]) - 1
        exit_bar = bar

    return cum_ret - COST_PER_TRADE


# ── Main ──────────────────────────────────────────────────────

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'rank450_full'

    if mode == 'rank450_full':
        # Approach A: scan full history of rank450 symbols (non-event windows)
        symbols = sorted(os.listdir(CACHE_DIR))
        print(f"[Approach A] Scanning FULL history of {len(symbols)} rank450 symbols")
    elif mode == 'random_non450':
        # Approach B: download + scan random non-rank450 symbols
        with open('/tmp/not_rank450_symbols.json') as f:
            not_cached = json.load(f)
        # Filter for symbols that likely have enough history (no 1000xxx meme coins for now)
        symbols = [s for s in not_cached if not s.startswith('1000')]
        np.random.seed(42)
        symbols = list(np.random.choice(symbols, min(80, len(symbols)), replace=False))
        print(f"[Approach B] Downloading + scanning {len(symbols)} non-rank450 symbols")
        # Need to download first
        download_klines(symbols)
    else:
        print(f"Unknown mode: {mode}")
        return

    # ── Scan each symbol ──
    all_trades = []
    symbol_stats = []
    t_start = time.time()

    for si, sym in enumerate(symbols):
        df = load_symbol_full(sym)
        if df is None or len(df) < 500:
            continue

        # Compute returns
        df = df.copy()
        df['ret_1h'] = df['close'].pct_change()

        # Load funding (optional - for funding split analysis)
        funding = load_funding(sym)
        has_funding = funding is not None and len(funding) > 0

        # Detect signals: vol>3x, ret>1%
        signals = detect_signals_full_history(df, vol_thresh=3.0, ret_thresh=0.01, vol_window=20)

        if not signals:
            symbol_stats.append({'symbol': sym, 'n_bars': len(df), 'n_signals': 0, 'years': 0})
            continue

        # Simulate trades
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        rets = df['ret_1h'].values

        for sig in signals:
            net_4h = simulate_trade_arrays(closes, highs, lows, rets, sig, hold_hours=4)
            net_8h = simulate_trade_arrays(closes, highs, lows, rets, sig, hold_hours=8)

            # Get funding at signal time if available
            fund_at_sig = np.nan
            if has_funding:
                sig_ts = sig['ts']
                fund_before = funding[funding['ts'] <= sig_ts]
                if len(fund_before) > 0:
                    fund_at_sig = fund_before.iloc[-1]['funding_rate']

            all_trades.append({
                'symbol': sym,
                'ts': sig['ts'],
                'year': sig['year'],
                'vol_ratio': sig['vol_ratio'],
                'ret_at_signal': sig['ret_at_signal'],
                'entry_price': sig['entry_price'],
                'net_4h': net_4h,
                'net_8h': net_8h,
                'funding_at_signal': fund_at_sig,
            })

        n_sig = len(signals)
        years = df['ts'].dt.year.nunique()
        symbol_stats.append({'symbol': sym, 'n_bars': len(df), 'n_signals': n_sig, 'years': years})

        if (si + 1) % 20 == 0:
            elapsed = time.time() - t_start
            print(f"  {si+1}/{len(symbols)} symbols done ({elapsed:.0f}s), {len(all_trades)} total signals")

    elapsed = time.time() - t_start
    print(f"\nScan complete: {len(all_trades)} trades across {len(symbol_stats)} symbols in {elapsed:.0f}s")

    if not all_trades:
        print("No trades found!")
        return

    # ── Analyze results ──
    td = pd.DataFrame(all_trades)
    ss = pd.DataFrame(symbol_stats)

    print(f"\n{'='*70}")
    print(f"OUT-OF-SAMPLE VALIDATION RESULTS (mode={mode})")
    print(f"{'='*70}")

    for horizon in ['net_4h', 'net_8h']:
        h = td[horizon]
        h_clean = h.dropna()
        print(f"\n--- {horizon} ---")
        print(f"  N trades:     {len(h_clean):,}")
        print(f"  Mean return:  {h_clean.mean()*100:+.3f}%")
        print(f"  Median:       {h_clean.median()*100:+.3f}%")
        print(f"  Std:          {h_clean.std()*100:.3f}%")
        print(f"  Win rate:     {(h_clean > 0).mean()*100:.1f}%")
        print(f"  Avg win:      {h_clean[h_clean > 0].mean()*100:+.3f}%" if (h_clean > 0).any() else "")
        print(f"  Avg loss:     {h_clean[h_clean <= 0].mean()*100:+.3f}%" if (h_clean <= 0).any() else "")
        pf_num = h_clean[h_clean > 0].sum()
        pf_den = abs(h_clean[h_clean <= 0].sum())
        pf = pf_num / pf_den if pf_den > 0 else 999
        print(f"  Profit Factor: {pf:.2f}")
        sharpe = h_clean.mean() / h_clean.std() * np.sqrt(252 * 6) if h_clean.std() > 0 else 0
        print(f"  Sharpe (ann): {sharpe:.2f}")

    # ── By year ──
    print(f"\n--- Yearly breakdown (4h hold) ---")
    for yr, yg in td.groupby('year'):
        n = yg['net_4h']
        if len(yg) < 5:
            continue
        print(f"  {yr}: n={len(yg):>6,} net={n.mean()*100:+.3f}% wr={(n>0).mean()*100:.1f}% pf={abs(n[n>0].sum()/n[n<=0].sum()):.2f}" if n[n<=0].sum() != 0 else f"  {yr}: n={len(yg):>6,} net={n.mean()*100:+.3f}% wr={(n>0).mean()*100:.1f}%")

    # ── By funding split ──
    td_fund = td.dropna(subset=['funding_at_signal'])
    if len(td_fund) > 50:
        print(f"\n--- Funding split (4h hold) ---")
        neg = td_fund[td_fund['funding_at_signal'] < 0]
        pos = td_fund[td_fund['funding_at_signal'] >= 0]
        if len(neg) >= 10:
            n4 = neg['net_4h']
            print(f"  neg_fund: n={len(neg):>6,} net={n4.mean()*100:+.3f}% wr={(n4>0).mean()*100:.1f}%")
        if len(pos) >= 10:
            n4 = pos['net_4h']
            print(f"  pos_fund: n={len(pos):>6,} net={n4.mean()*100:+.3f}% wr={(n4>0).mean()*100:.1f}%")

    # ── Top / bottom symbols ──
    print(f"\n--- Per-symbol average net return (4h, top 15) ---")
    sym_avg = td.groupby('symbol')['net_4h'].agg(['mean', 'count']).reset_index()
    sym_avg = sym_avg[sym_avg['count'] >= 5].sort_values('mean', ascending=False)
    for _, r in sym_avg.head(15).iterrows():
        print(f"  {r['symbol']:20s} net={r['mean']*100:+.3f}% n={int(r['count'])}")

    print(f"\n--- Per-symbol average net return (4h, bottom 15) ---")
    for _, r in sym_avg.tail(15).iterrows():
        print(f"  {r['symbol']:20s} net={r['mean']*100:+.3f}% n={int(r['count'])}")

    # ── Comparison with v1.6a rank450 results ──
    print(f"\n{'='*70}")
    print("COMPARISON WITH v1.6a RANK450 PANEL")
    print(f"{'='*70}")
    print(f"  v1.6a rank450 (vol>3, ret>1%, 4h hold): net=+1.21% n=12,831 wr=52.2%")
    print(f"  v1.6a rank450 (vol>3, ret>1%, 8h hold): net=+1.97% n=12,831 wr=55.1%")
    n4 = td['net_4h'].dropna()
    n8 = td['net_8h'].dropna()
    print(f"  OOS full-data  (vol>3, ret>1%, 4h hold): net={n4.mean()*100:+.3f}% n={len(n4):,} wr={(n4>0).mean()*100:.1f}%")
    print(f"  OOS full-data  (vol>3, ret>1%, 8h hold): net={n8.mean()*100:+.3f}% n={len(n8):,} wr={(n8>0).mean()*100:.1f}%")

    # ── Save everything ──
    td.to_csv(f'{OUT_DIR}/all_trades_{mode}.csv', index=False)
    ss.to_csv(f'{OUT_DIR}/symbol_stats_{mode}.csv', index=False)

    # Save summary JSON
    summary = {
        'mode': mode,
        'n_symbols': len(ss),
        'n_symbols_with_signals': len(ss[ss['n_signals'] > 0]),
        'n_trades': len(td),
        'net_4h_mean': float(n4.mean()),
        'net_4h_median': float(n4.median()),
        'net_4h_std': float(n4.std()),
        'net_4h_winrate': float((n4 > 0).mean()),
        'net_8h_mean': float(n8.mean()),
        'net_8h_median': float(n8.median()),
        'net_8h_std': float(n8.std()),
        'net_8h_winrate': float((n8 > 0).mean()),
        'rank450_4h_mean': 0.0121,
        'rank450_4h_winrate': 0.522,
        'rank450_8h_mean': 0.0197,
        'rank450_8h_winrate': 0.551,
        'alpha_decay_4h': float(n4.mean() - 0.0121),
        'alpha_decay_8h': float(n8.mean() - 0.0197),
    }
    with open(f'{OUT_DIR}/summary_{mode}.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Results saved to {OUT_DIR}/")


def download_klines(symbols):
    """Download 1h kline data for non-cached symbols."""
    import urllib.request, io

    # Figure out which months to download (from 2022-01 to latest)
    months = []
    for y in range(2022, 2027):
        for m in range(1, 13):
            months.append(f"{y}-{m:02d}")
            if y == 2026 and m >= 5:
                break

    to_dl = []
    for sym in symbols:
        for month in months:
            cache_path = os.path.join(CACHE_DIR, sym, f"{sym}-1h-{month}.zip")
            if not os.path.exists(cache_path):
                to_dl.append((sym, month, cache_path))

    print(f"  Need to download {len(to_dl)} kline files for {len(symbols)} symbols")

    ok = 0
    fail = 0
    for i, (sym, month, path) in enumerate(to_dl):
        url = f"{S3_BASE}/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            req = urllib.request.Request(url, headers={"User-Agent": "v1.6a-oos/1.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            if data and not data.startswith(b"<Error>"):
                with open(path, 'wb') as f:
                    f.write(data)
                ok += 1
            else:
                fail += 1
        except:
            fail += 1

        if (i + 1) % 100 == 0:
            print(f"  Download: {i+1}/{len(to_dl)} (ok={ok}, fail={fail})")

    print(f"  Download complete: ok={ok}, fail={fail}")


if __name__ == '__main__':
    main()
