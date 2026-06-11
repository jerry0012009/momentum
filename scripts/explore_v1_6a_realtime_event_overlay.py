#!/usr/bin/env python3
"""
Causal real-time top-gainer detector overlay for v1.6a V4 full-history signals.

Question: if a symbol first appears in a real-time top-gainer/24h-return event
using only completed hourly bars, and THEN a V4 1h price+volume ignition fires,
does the full-history V4 signal become positive?

This reuses the existing full-universe V4 signal trade file:
  reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv
and annotates each signal with the latest prior causal event detector timestamp.

Event detector at hour t (completed bar):
  - symbol's 24h close-to-close return >= threshold
  - symbol is rank <= N by 24h return among available symbols at t
  - trailing 24h quote volume >= threshold
  - dedup: first event only if previous event for same rule/symbol was >24h ago

Entry rule:
  - V4 signal must occur AFTER event appearance: lag_hours in configured window,
    e.g. 1..24h. lag=0 is excluded by default.
"""
from __future__ import annotations

import glob
import json
import math
import os
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
V4_TRADES = ROOT / 'reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay'
OUT.mkdir(parents=True, exist_ok=True)

COST = 0.0013
EVENT_COOLDOWN_HOURS = 24
MIN_CROSS_SECTION_SYMBOLS = 100

RULES = [
    {'rule': 'rank20_ret10_vol5m',  'rank_max': 20, 'ret24_min': 0.10, 'vol24_min': 5_000_000},
    {'rule': 'rank20_ret20_vol5m',  'rank_max': 20, 'ret24_min': 0.20, 'vol24_min': 5_000_000},
    {'rule': 'rank10_ret10_vol5m',  'rank_max': 10, 'ret24_min': 0.10, 'vol24_min': 5_000_000},
    {'rule': 'rank50_ret10_vol5m',  'rank_max': 50, 'ret24_min': 0.10, 'vol24_min': 5_000_000},
    {'rule': 'rank20_ret10_vol20m', 'rank_max': 20, 'ret24_min': 0.10, 'vol24_min': 20_000_000},
    {'rule': 'rank20_ret30_vol5m',  'rank_max': 20, 'ret24_min': 0.30, 'vol24_min': 5_000_000},
]
LAG_WINDOWS = [
    ('same_hour_0', 0, 0),
    ('after_1_4h', 1, 4),
    ('after_1_8h', 1, 8),
    ('after_1_24h', 1, 24),
    ('after_4_24h', 4, 24),
    ('after_8_24h', 8, 24),
    ('after_24_48h', 24, 48),
]


def load_symbol_features(sym: str) -> pd.DataFrame | None:
    sym_dir = CACHE_DIR / sym
    files = sorted(glob.glob(str(sym_dir / f'{sym}-1h-*.zip')))
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
                    df = pd.read_csv(fh, usecols=lambda c: c in {'open_time','close','quote_volume'})
                out = pd.DataFrame({
                    'ts': pd.to_datetime(pd.to_numeric(df['open_time'], errors='coerce'), unit='ms', utc=True),
                    'symbol': sym,
                    'close': pd.to_numeric(df['close'], errors='coerce').astype('float64'),
                    'quote_volume': pd.to_numeric(df['quote_volume'], errors='coerce').astype('float64'),
                }).dropna(subset=['ts', 'close'])
                frames.append(out)
        except Exception:
            continue
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True).sort_values('ts').drop_duplicates('ts')
    if len(df) < 200:
        return None
    df['ret24'] = df['close'].pct_change(24)
    df['vol24'] = df['quote_volume'].rolling(24, min_periods=12).sum()
    df = df.dropna(subset=['ret24', 'vol24'])
    if df.empty:
        return None
    return df[['ts','symbol','ret24','vol24']]


def summarize(df: pd.DataFrame) -> dict:
    if df.empty:
        return {'n': 0, 'net4_mean': np.nan, 'net4_median': np.nan, 'net4_winrate': np.nan, 'net4_pf': np.nan,
                'net8_mean': np.nan, 'net8_median': np.nan, 'net8_winrate': np.nan, 'net8_pf': np.nan}
    def pf(x):
        x = x.dropna().to_numpy()
        wins = x[x > 0].sum(); losses = -x[x < 0].sum()
        if losses <= 0:
            return np.inf if wins > 0 else np.nan
        return wins / losses
    return {
        'n': int(len(df)),
        'net4_mean': float(df['net_4h'].mean()),
        'net4_median': float(df['net_4h'].median()),
        'net4_winrate': float((df['net_4h'] > 0).mean()),
        'net4_pf': float(pf(df['net_4h'])),
        'net8_mean': float(df['net_8h'].mean()),
        'net8_median': float(df['net_8h'].median()),
        'net8_winrate': float((df['net_8h'] > 0).mean()),
        'net8_pf': float(pf(df['net_8h'])),
    }


def dedup_events(rule_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sym, g in rule_df.sort_values(['symbol','ts']).groupby('symbol', sort=False):
        last = pd.Timestamp('1970-01-01', tz='UTC')
        for r in g.itertuples(index=False):
            ts = r.ts
            if (ts - last).total_seconds() / 3600.0 >= EVENT_COOLDOWN_HOURS:
                rows.append({
                    'symbol': sym, 'event_ts': ts,
                    'event_ret24': float(r.ret24),
                    'event_rank_ret24': int(r.rank_ret24),
                    'event_vol24': float(r.vol24),
                    'xsec_symbols': int(r.xsec_symbols),
                })
                last = ts
    return pd.DataFrame(rows)


def to_ns_int(s: pd.Series) -> pd.Series:
    """Convert any timezone-aware/naive datetime series to UTC nanosecond int64."""
    return pd.to_datetime(s, utc=True).dt.as_unit('ns').astype('int64')


def annotate_with_latest_event(trades: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        out = trades.copy()
        out['event_ts'] = pd.NaT; out['lag_hours'] = np.nan
        return out
    parts = []
    events = events.copy()
    # Pandas 3 may keep datetime64[us]/[ms]; merge on uniform ns integers.
    events['_event_ns'] = to_ns_int(events['event_ts'])
    ev_by_sym = {sym: g.sort_values('_event_ns') for sym, g in events.groupby('symbol')}
    for sym, tg in trades.groupby('symbol', sort=False):
        tg = tg.sort_values('ts').copy()
        tg['_ts_ns'] = to_ns_int(tg['ts'])
        ev = ev_by_sym.get(sym)
        if ev is None or ev.empty:
            tg['event_ts'] = pd.NaT
            tg['event_ret24'] = np.nan
            tg['event_rank_ret24'] = np.nan
            tg['event_vol24'] = np.nan
            tg['lag_hours'] = np.nan
        else:
            merged = pd.merge_asof(
                tg.sort_values('_ts_ns'),
                ev.sort_values('_event_ns'),
                left_on='_ts_ns', right_on='_event_ns', by='symbol', direction='backward', allow_exact_matches=True,
            )
            merged['lag_hours'] = (merged['_ts_ns'] - merged['_event_ns']) / 3_600_000_000_000.0
            tg = merged
        parts.append(tg)
    out = pd.concat(parts, ignore_index=True)
    return out.drop(columns=[c for c in ['_ts_ns', '_event_ns'] if c in out.columns])


def main():
    t0 = time.time()
    symbols = sorted([p.name for p in CACHE_DIR.iterdir() if p.is_dir()])
    print(f'[load features] symbols={len(symbols)}')
    frames = []
    for i, sym in enumerate(symbols, 1):
        df = load_symbol_features(sym)
        if df is not None and not df.empty:
            frames.append(df)
        if i % 50 == 0:
            print(f'  loaded {i}/{len(symbols)}, frames={len(frames)}, elapsed={time.time()-t0:.1f}s')
    panel = pd.concat(frames, ignore_index=True)
    # reduce memory after concat
    panel['ret24'] = panel['ret24'].astype('float32')
    panel['vol24'] = panel['vol24'].astype('float32')
    print(f'[panel] rows={len(panel):,}, symbols={panel.symbol.nunique()}, ts={panel.ts.min()}..{panel.ts.max()}, elapsed={time.time()-t0:.1f}s')

    # Cross-sectional ranks by hour. rank_ret24=1 is biggest 24h gainer.
    xsec = panel.groupby('ts')['symbol'].transform('count').astype('int16')
    panel['xsec_symbols'] = xsec
    panel = panel[panel['xsec_symbols'] >= MIN_CROSS_SECTION_SYMBOLS].copy()
    panel['rank_ret24'] = panel.groupby('ts')['ret24'].rank(method='first', ascending=False).astype('int16')
    # Avoid parquet dependency (pyarrow/fastparquet may not be installed in this venv).
    # The event CSVs and summary CSVs below are the durable artifacts we need.
    print(f'[ranked] rows={len(panel):,}, elapsed={time.time()-t0:.1f}s')

    trades = pd.read_csv(V4_TRADES)
    trades['ts'] = pd.to_datetime(trades['ts'], utc=True)
    trades['year'] = trades['ts'].dt.year
    print(f'[trades] full V4 trades={len(trades):,}, standalone net4={trades.net_4h.mean()*100:.3f}%, net8={trades.net_8h.mean()*100:.3f}%')

    all_summary = []
    sample_trades = []
    event_counts = []

    for rule in RULES:
        mask = (
            (panel['rank_ret24'] <= rule['rank_max']) &
            (panel['ret24'] >= rule['ret24_min']) &
            (panel['vol24'] >= rule['vol24_min'])
        )
        raw = panel.loc[mask, ['ts','symbol','ret24','rank_ret24','vol24','xsec_symbols']].copy()
        events = dedup_events(raw)
        events['rule'] = rule['rule']
        events.to_csv(OUT / f"events_{rule['rule']}.csv", index=False)
        event_counts.append({'rule': rule['rule'], 'raw_hours': int(len(raw)), 'events': int(len(events)), 'symbols': int(events.symbol.nunique() if not events.empty else 0)})
        print(f"[rule] {rule['rule']} raw_hours={len(raw):,}, events={len(events):,}")

        ann = annotate_with_latest_event(trades, events)
        ann['rule'] = rule['rule']
        for lag_label, lag_min, lag_max in LAG_WINDOWS:
            sel = ann[(ann['lag_hours'] >= lag_min) & (ann['lag_hours'] <= lag_max)].copy()
            s = summarize(sel)
            all_summary.append({**rule, 'lag_window': lag_label, 'lag_min': lag_min, 'lag_max': lag_max, **s})
            if len(sel):
                yy = sel.groupby('year').agg(n=('net_4h','size'), net4=('net_4h','mean'), wr4=('net_4h', lambda x:(x>0).mean()), net8=('net_8h','mean'), wr8=('net_8h', lambda x:(x>0).mean())).reset_index()
                yy['rule'] = rule['rule']; yy['lag_window'] = lag_label
                yy.to_csv(OUT / f"year_{rule['rule']}_{lag_label}.csv", index=False)
        # keep one compact annotated trade file for most important rule
        if rule['rule'] == 'rank20_ret10_vol5m':
            ann.to_csv(OUT / 'annotated_v4_trades_rank20_ret10_vol5m.csv', index=False)

    summary = pd.DataFrame(all_summary)
    summary.to_csv(OUT / 'realtime_event_overlay_summary.csv', index=False)
    pd.DataFrame(event_counts).to_csv(OUT / 'realtime_event_counts.csv', index=False)

    top = summary[summary['n'] >= 100].sort_values('net4_mean', ascending=False).head(30)
    print('\n[Top overlay summaries n>=100]')
    cols = ['rule','lag_window','n','net4_mean','net4_median','net4_winrate','net4_pf','net8_mean','net8_winrate']
    print(top[cols].to_string(index=False, float_format=lambda x: f'{x:.4f}'))

    exact = summary[(summary['rule']=='rank20_ret10_vol5m')]
    print('\n[Main rule rank20_ret10_vol5m]')
    print(exact[cols].to_string(index=False, float_format=lambda x: f'{x:.4f}'))

    meta = {
        'generated_at': pd.Timestamp.utcnow().isoformat(),
        'panel_rows': int(len(panel)),
        'panel_symbols': int(panel.symbol.nunique()),
        'time_min': str(panel.ts.min()),
        'time_max': str(panel.ts.max()),
        'v4_trades': int(len(trades)),
        'standalone_v4_net4_mean': float(trades.net_4h.mean()),
        'standalone_v4_net8_mean': float(trades.net_8h.mean()),
        'event_cooldown_hours': EVENT_COOLDOWN_HOURS,
        'min_cross_section_symbols': MIN_CROSS_SECTION_SYMBOLS,
        'rules': RULES,
        'lag_windows': LAG_WINDOWS,
    }
    with open(OUT / 'realtime_event_overlay_meta.json', 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'\n[done] {OUT}, elapsed={time.time()-t0:.1f}s')

if __name__ == '__main__':
    main()
