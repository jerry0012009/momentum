#!/usr/bin/env python3
"""
Fast validation of v1.6a extreme second-squeeze hypothesis.

This version intentionally reuses already-built causal realtime event CSVs from
`binance_event_study_v1_6a_realtime_event_overlay/` to avoid rescanning the full
Binance Vision 1h zip cache. The heavy anti-lookahead realtime detector was
already built there; here we run tail/robustness diagnostics.

Core question:
  After a causal realtime extreme event (rank<=20, 24h ret>=30%, vol24>=5m),
  does a later V4 ignition have a tradable right-tail edge?
"""
from __future__ import annotations

import glob
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
RT_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
V4_TRADES = ROOT / 'reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze'
OUT.mkdir(parents=True, exist_ok=True)

BASE_COST = 0.0013
COSTS = [0.0013, 0.0025, 0.0050, 0.0100]

BASE_RULE_FILES = {
    # exact precomputed causal event definitions
    'rank20_ret20_vol5m': RT_ART / 'events_rank20_ret20_vol5m.csv',
    'rank20_ret30_vol5m': RT_ART / 'events_rank20_ret30_vol5m.csv',
}

# Derived stricter subsets from the exact rank20_ret30 event file. These are
# conservative diagnostics, not a fresh dedup pass; report labels disclose this.
DERIVED_RULES = [
    {'rule': 'derived_rank10_ret30_vol5m', 'source': 'rank20_ret30_vol5m', 'rank_max': 10, 'ret24_min': 0.30, 'vol24_min': 5_000_000},
    {'rule': 'derived_rank20_ret40_vol5m', 'source': 'rank20_ret30_vol5m', 'rank_max': 20, 'ret24_min': 0.40, 'vol24_min': 5_000_000},
    {'rule': 'derived_rank20_ret50_vol5m', 'source': 'rank20_ret30_vol5m', 'rank_max': 20, 'ret24_min': 0.50, 'vol24_min': 5_000_000},
    {'rule': 'derived_rank20_ret30_vol20m', 'source': 'rank20_ret30_vol5m', 'rank_max': 20, 'ret24_min': 0.30, 'vol24_min': 20_000_000},
    {'rule': 'derived_rank20_ret30_vol50m', 'source': 'rank20_ret30_vol5m', 'rank_max': 20, 'ret24_min': 0.30, 'vol24_min': 50_000_000},
]

LAG_WINDOWS = [
    ('after_1_4h', 1, 4),
    ('after_1_8h', 1, 8),
    ('after_1_24h', 1, 24),
    ('after_4_24h', 4, 24),
    ('after_8_24h', 8, 24),
    ('after_24_48h', 24, 48),
]


def to_ns_int(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, utc=True).dt.as_unit('ns').astype('int64')


def load_events() -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for rule, fp in BASE_RULE_FILES.items():
        df = pd.read_csv(fp)
        df['event_ts'] = pd.to_datetime(df['event_ts'], utc=True)
        df['rule'] = rule
        df['rule_type'] = 'exact_precomputed_causal'
        out[rule] = df
    src = out['rank20_ret30_vol5m']
    for spec in DERIVED_RULES:
        df = src[
            (src['event_rank_ret24'] <= spec['rank_max']) &
            (src['event_ret24'] >= spec['ret24_min']) &
            (src['event_vol24'] >= spec['vol24_min'])
        ].copy()
        df['rule'] = spec['rule']
        df['rule_type'] = 'derived_subset_from_rank20_ret30_events'
        out[spec['rule']] = df
    return out


def annotate_with_latest_event(trades: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        out = trades.copy()
        out['event_ts'] = pd.NaT
        out['lag_hours'] = np.nan
        return out
    parts = []
    events = events.copy()
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
            tg['xsec_symbols'] = np.nan
            tg['lag_hours'] = np.nan
        else:
            merged = pd.merge_asof(
                tg.sort_values('_ts_ns'), ev.sort_values('_event_ns'),
                left_on='_ts_ns', right_on='_event_ns', by='symbol',
                direction='backward', allow_exact_matches=True,
            )
            merged['lag_hours'] = (merged['_ts_ns'] - merged['_event_ns']) / 3_600_000_000_000.0
            tg = merged
        parts.append(tg)
    out = pd.concat(parts, ignore_index=True)
    return out.drop(columns=[c for c in ['_ts_ns', '_event_ns'] if c in out.columns])


def pf(x: pd.Series) -> float:
    vals = x.dropna().to_numpy(dtype='float64')
    wins = vals[vals > 0].sum()
    losses = -vals[vals < 0].sum()
    if losses <= 0:
        return float('inf') if wins > 0 else np.nan
    return float(wins / losses)


def top_contribution(x: pd.Series, k: int) -> float:
    vals = x.dropna().sort_values(ascending=False)
    total = vals.sum()
    if len(vals) == 0 or abs(total) < 1e-12:
        return np.nan
    return float(vals.head(k).sum() / total)


def drop_top_pct_mean(x: pd.Series, pct: float) -> float:
    vals = x.dropna().sort_values(ascending=False)
    if len(vals) == 0:
        return np.nan
    k = max(1, int(math.ceil(len(vals) * pct)))
    rest = vals.iloc[k:]
    return float(rest.mean()) if len(rest) else np.nan


def summarize(df: pd.DataFrame, mode: str) -> dict:
    if df.empty:
        return {'mode': mode, 'n': 0}
    x4 = df['net_4h']
    x8 = df['net_8h']
    sym_mean = df.groupby('symbol')['net_4h'].mean()
    return {
        'mode': mode,
        'n': int(len(df)),
        'symbols': int(df['symbol'].nunique()),
        'events': int(df[['symbol', 'event_ts']].drop_duplicates().shape[0]),
        'net4_mean': float(x4.mean()),
        'net4_median': float(x4.median()),
        'net4_winrate': float((x4 > 0).mean()),
        'net4_pf': pf(x4),
        'net4_p10': float(x4.quantile(0.10)),
        'net4_p25': float(x4.quantile(0.25)),
        'net4_p75': float(x4.quantile(0.75)),
        'net4_p90': float(x4.quantile(0.90)),
        'net4_p95': float(x4.quantile(0.95)),
        'net4_min': float(x4.min()),
        'net4_max': float(x4.max()),
        'net4_drop_top1pct_mean': drop_top_pct_mean(x4, 0.01),
        'net4_drop_top5pct_mean': drop_top_pct_mean(x4, 0.05),
        'top1_trade_contrib_sum4': top_contribution(x4, 1),
        'top5_trade_contrib_sum4': top_contribution(x4, min(5, len(x4))),
        'top10_trade_contrib_sum4': top_contribution(x4, min(10, len(x4))),
        'symbol_equal_net4_mean': float(sym_mean.mean()),
        'symbol_equal_net4_median': float(sym_mean.median()),
        'net8_mean': float(x8.mean()),
        'net8_median': float(x8.median()),
        'net8_winrate': float((x8 > 0).mean()),
        'net8_pf': pf(x8),
    }


def load_btc_regime() -> pd.DataFrame:
    sym = 'BTCUSDT'
    files = sorted(glob.glob(str(CACHE_DIR / sym / f'{sym}-1h-*.zip')))
    frames = []
    for f in files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith('.csv')]
                if not names:
                    continue
                with zf.open(names[0]) as fh:
                    df = pd.read_csv(fh, usecols=lambda c: c in {'open_time', 'close'})
            frames.append(pd.DataFrame({
                'ts': pd.to_datetime(pd.to_numeric(df['open_time'], errors='coerce'), unit='ms', utc=True),
                'close': pd.to_numeric(df['close'], errors='coerce'),
            }).dropna())
        except Exception:
            continue
    if not frames:
        return pd.DataFrame(columns=['_ts_ns', 'btc_ret24', 'btc_regime'])
    btc = pd.concat(frames, ignore_index=True).sort_values('ts').drop_duplicates('ts')
    btc['btc_ret24'] = btc['close'].pct_change(24)
    btc = btc.dropna(subset=['btc_ret24']).copy()
    btc['btc_regime'] = np.select(
        [btc['btc_ret24'] <= -0.03, btc['btc_ret24'] < 0, btc['btc_ret24'] < 0.03, btc['btc_ret24'] >= 0.03],
        ['btc_down_gt3%', 'btc_down_0_3%', 'btc_up_0_3%', 'btc_up_gt3%'],
        default='unknown',
    )
    btc['_ts_ns'] = to_ns_int(btc['ts'])
    return btc[['_ts_ns', 'btc_ret24', 'btc_regime']]


def attach_buckets(df: pd.DataFrame, btc: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if not btc.empty:
        out['_ts_ns'] = to_ns_int(out['ts'])
        out = pd.merge_asof(out.sort_values('_ts_ns'), btc.sort_values('_ts_ns'), on='_ts_ns', direction='backward', tolerance=3_600_000_000_000)
        out = out.drop(columns=['_ts_ns'])
    else:
        out['btc_ret24'] = np.nan
        out['btc_regime'] = 'unknown'
    out['funding_bucket'] = np.select(
        [out['funding_at_signal'] < 0, out['funding_at_signal'] <= 0.00005, out['funding_at_signal'] <= 0.0002],
        ['negative', 'near_zero_0_5bps', 'positive_5_20bps'],
        default='positive_gt20bps',
    )
    out['event_ret24_bucket'] = pd.cut(
        out['event_ret24'], [-np.inf, 0.30, 0.40, 0.60, 1.00, np.inf],
        labels=['<30%', '30-40%', '40-60%', '60-100%', '>100%'],
    ).astype(str)
    out['event_rank_bucket'] = pd.cut(
        out['event_rank_ret24'], [0, 1, 5, 10, 20, 50],
        labels=['rank1', 'rank2-5', 'rank6-10', 'rank11-20', 'rank21+'],
    ).astype(str)
    return out


def stratify(df: pd.DataFrame, base: dict, by: str) -> list[dict]:
    rows = []
    if df.empty or by not in df.columns:
        return rows
    for key, g in df.groupby(by, dropna=False, observed=True):
        if len(g) < 20:
            continue
        rows.append({**base, 'strata_type': by, 'bucket': str(key), **summarize(g, 'all_signals')})
    return rows


def main() -> None:
    trades = pd.read_csv(V4_TRADES)
    trades['ts'] = pd.to_datetime(trades['ts'], utc=True)
    trades['year'] = trades['ts'].dt.year
    trades['month'] = trades['ts'].dt.strftime('%Y-%m')
    btc = load_btc_regime()
    events_by_rule = load_events()

    print(f'[trades] n={len(trades):,}, symbols={trades.symbol.nunique()}, time={trades.ts.min()}..{trades.ts.max()}')
    print(f'[btc] rows={len(btc):,}')

    summary_rows = []
    cost_rows = []
    year_rows = []
    month_rows = []
    strata_rows = []
    event_counts = []
    selected_parts = []

    for rule, events in events_by_rule.items():
        rule_type = events['rule_type'].iloc[0] if not events.empty and 'rule_type' in events else 'unknown'
        event_counts.append({
            'rule': rule, 'rule_type': rule_type, 'events': int(len(events)),
            'symbols': int(events.symbol.nunique() if not events.empty else 0),
            'event_ret24_mean': float(events.event_ret24.mean()) if not events.empty else np.nan,
            'event_ret24_median': float(events.event_ret24.median()) if not events.empty else np.nan,
            'event_vol24_median': float(events.event_vol24.median()) if not events.empty else np.nan,
        })
        print(f'[rule] {rule} type={rule_type} events={len(events):,} symbols={events.symbol.nunique() if not events.empty else 0}')
        ann = annotate_with_latest_event(trades, events)
        ann['rule'] = rule
        ann['rule_type'] = rule_type
        ann = attach_buckets(ann, btc)

        for lag_label, lag_min, lag_max in LAG_WINDOWS:
            sel = ann[(ann['lag_hours'] >= lag_min) & (ann['lag_hours'] <= lag_max)].copy()
            base = {'rule': rule, 'rule_type': rule_type, 'lag_window': lag_label, 'lag_min': lag_min, 'lag_max': lag_max}
            summary_rows.append({**base, **summarize(sel, 'all_signals')})
            if sel.empty:
                continue
            first = sel.sort_values(['symbol', 'event_ts', 'ts']).groupby(['symbol', 'event_ts'], as_index=False, sort=False).head(1).copy()
            summary_rows.append({**base, **summarize(first, 'first_signal_per_event')})

            for mode, d in [('all_signals', sel), ('first_signal_per_event', first)]:
                for cost in COSTS:
                    delta = cost - BASE_COST
                    cost_rows.append({
                        **base, 'mode': mode, 'cost': cost, 'n': int(len(d)),
                        'net4_mean': float((d['net_4h'] - delta).mean()),
                        'net8_mean': float((d['net_8h'] - delta).mean()),
                        'net4_winrate': float(((d['net_4h'] - delta) > 0).mean()),
                        'net4_pf': pf(d['net_4h'] - delta),
                    })
                yy = d.groupby('year').agg(
                    n=('net_4h', 'size'), symbols=('symbol', 'nunique'), events=('event_ts', 'nunique'),
                    net4=('net_4h', 'mean'), med4=('net_4h', 'median'), wr4=('net_4h', lambda x: (x > 0).mean()),
                    net8=('net_8h', 'mean'), wr8=('net_8h', lambda x: (x > 0).mean()),
                ).reset_index()
                for r in yy.to_dict('records'):
                    year_rows.append({**base, 'mode': mode, **r})
                mm = d.groupby('month').agg(
                    n=('net_4h', 'size'), symbols=('symbol', 'nunique'), net4=('net_4h', 'mean'), wr4=('net_4h', lambda x: (x > 0).mean()),
                ).reset_index()
                for r in mm.to_dict('records'):
                    month_rows.append({**base, 'mode': mode, **r})

            for by in ['funding_bucket', 'btc_regime', 'event_ret24_bucket', 'event_rank_bucket']:
                strata_rows.extend(stratify(sel, base, by))

            if rule == 'rank20_ret30_vol5m' and lag_label in {'after_4_24h', 'after_8_24h', 'after_24_48h'}:
                tmp = sel.copy()
                tmp['lag_window'] = lag_label
                selected_parts.append(tmp)

    summary = pd.DataFrame(summary_rows)
    costs = pd.DataFrame(cost_rows)
    years = pd.DataFrame(year_rows)
    months = pd.DataFrame(month_rows)
    strata = pd.DataFrame(strata_rows)
    counts = pd.DataFrame(event_counts)
    selected = pd.concat(selected_parts, ignore_index=True) if selected_parts else pd.DataFrame()

    summary.to_csv(OUT / 'second_squeeze_summary.csv', index=False)
    costs.to_csv(OUT / 'second_squeeze_cost_curve.csv', index=False)
    years.to_csv(OUT / 'second_squeeze_by_year.csv', index=False)
    months.to_csv(OUT / 'second_squeeze_by_month.csv', index=False)
    strata.to_csv(OUT / 'second_squeeze_strata.csv', index=False)
    counts.to_csv(OUT / 'second_squeeze_event_counts.csv', index=False)
    if not selected.empty:
        selected.to_csv(OUT / 'second_squeeze_selected_trades.csv', index=False)
        selected.sort_values('net_4h', ascending=False).head(100).to_csv(OUT / 'second_squeeze_top100_trades.csv', index=False)

    shortlist = summary[(summary['mode'] == 'first_signal_per_event') & (summary['n'] >= 100)].copy()
    shortlist = shortlist.sort_values(['net4_mean', 'net4_drop_top1pct_mean'], ascending=False)
    shortlist.to_csv(OUT / 'second_squeeze_shortlist_first_signal.csv', index=False)

    main = summary[
        (summary['rule'].eq('rank20_ret30_vol5m')) &
        (summary['lag_window'].isin(['after_4_24h', 'after_8_24h', 'after_24_48h']))
    ].copy()
    main.to_csv(OUT / 'second_squeeze_main_candidates.csv', index=False)

    meta = {
        'generated_at': pd.Timestamp.now('UTC').isoformat(),
        'base_cost': BASE_COST,
        'costs': COSTS,
        'v4_trades': int(len(trades)),
        'v4_symbols': int(trades.symbol.nunique()),
        'v4_time_min': str(trades.ts.min()),
        'v4_time_max': str(trades.ts.max()),
        'note': 'Derived_* rules are conservative subsets of the precomputed exact rank20_ret30 events, not fresh cooldown/dedup event passes.',
        'best_first_signal_n_ge_100': shortlist.head(10).replace({np.nan: None}).to_dict('records'),
    }
    (OUT / 'second_squeeze_verdict_summary.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

    print('\n[Top first-signal candidates n>=100]')
    cols = ['rule', 'rule_type', 'lag_window', 'mode', 'n', 'symbols', 'events', 'net4_mean', 'net4_median', 'net4_winrate', 'net4_pf', 'net4_drop_top1pct_mean', 'net4_drop_top5pct_mean', 'net8_mean']
    print(shortlist[cols].head(20).to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print(f'\n[done] {OUT}')


if __name__ == '__main__':
    main()
