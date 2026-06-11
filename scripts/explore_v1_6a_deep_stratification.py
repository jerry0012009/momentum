#!/usr/bin/env python3
"""
Deep stratification of v1.6a second-squeeze hypothesis.

Goal: Find the narrowest tradable subset where "extreme event → later V4" has
a robust edge after costs. Cross-stratify by rank × ret24 × funding × BTC regime.

Criteria for GO:
  - n >= 80 (first-signal-per-event)
  - 4h mean > 0 after 25bps cost
  - 4h median > -0.02 (not deeply negative)
  - winrate >= 48%
  - PF >= 1.3
  - drop_top5% mean > 0
  - yearly: at least 3/4 years positive 4h mean
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
SQ_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_extreme_second_squeeze'
RT_ART = ROOT / 'reports/artifacts/binance_event_study_v1_6a_realtime_event_overlay'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_deep_stratification'
OUT.mkdir(parents=True, exist_ok=True)

BASE_COST = 0.0013
COST_25BP = 0.0025
COST_50BP = 0.0050

# ── Load trades annotated with events ────────────────────────────────────────
TRADES = ROOT / 'reports/artifacts/binance_event_study_v1_6a_oos/all_trades_full_universe.csv'
EVENTS_FILE = RT_ART / 'events_rank20_ret30_vol5m.csv'


def pf(x: pd.Series) -> float:
    vals = x.dropna().to_numpy(dtype='float64')
    wins = vals[vals > 0].sum()
    losses = -vals[vals < 0].sum()
    if losses <= 0:
        return float('inf') if wins > 0 else np.nan
    return float(wins / losses)


def drop_top_pct_mean(x: pd.Series, pct: float) -> float:
    vals = x.dropna().sort_values(ascending=False)
    if len(vals) == 0:
        return np.nan
    k = max(1, int(math.ceil(len(vals) * pct)))
    rest = vals.iloc[k:]
    return float(rest.mean()) if len(rest) else np.nan


def top_concentration(x: pd.Series) -> float:
    """Fraction of total PnL captured by top 5 trades."""
    vals = x.dropna().sort_values(ascending=False)
    total = vals.sum()
    if len(vals) == 0 or abs(total) < 1e-12:
        return np.nan
    return float(vals.head(min(5, len(vals))).sum() / total)


def to_ns(s: pd.Series) -> pd.Series:
    """Convert datetime to int64 nanoseconds, robust to us/ns resolution."""
    return pd.to_datetime(s, utc=True).dt.as_unit('ns').astype('int64')


def load_and_annotate() -> pd.DataFrame:
    """Load V4 trades and annotate with events (first signal per event only)."""
    trades = pd.read_csv(TRADES)
    trades['ts'] = pd.to_datetime(trades['ts'], utc=True)

    events = pd.read_csv(EVENTS_FILE)
    events['event_ts'] = pd.to_datetime(events['event_ts'], utc=True)
    events['_event_ns'] = to_ns(events['event_ts'])

    # Annotate trades with latest event per symbol
    parts = []
    ev_by_sym = {sym: g.sort_values('_event_ns') for sym, g in events.groupby('symbol')}
    for sym, tg in trades.groupby('symbol', sort=False):
        tg = tg.sort_values('ts').copy()
        tg['_ts_ns'] = to_ns(tg['ts'])
        ev = ev_by_sym.get(sym)
        if ev is None or ev.empty:
            tg['event_ts'] = pd.NaT
            tg['event_ret24'] = np.nan
            tg['event_rank_ret24'] = np.nan
            tg['event_vol24'] = np.nan
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

    df = pd.concat(parts, ignore_index=True)
    df = df.drop(columns=[c for c in ['_ts_ns', '_event_ns'] if c in df.columns])
    return df


def add_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """Add stratification buckets."""
    out = df.copy()
    out['year'] = out['ts'].dt.year

    # Rank bucket: rank1, rank2-5, rank6-10, rank11-20
    out['rank_bucket'] = pd.cut(
        out['event_rank_ret24'],
        bins=[0, 1.5, 5.5, 10.5, 20.5],
        labels=['rank1', 'rank2-5', 'rank6-10', 'rank11-20'],
    ).astype(str)

    # Ret24 bucket
    out['ret_bucket'] = pd.cut(
        out['event_ret24'],
        bins=[-np.inf, 0.30, 0.40, 0.60, np.inf],
        labels=['<30%', '30-40%', '40-60%', '60+%'],
    ).astype(str)

    # Funding bucket
    out['fund_bucket'] = np.select(
        [out['funding_at_signal'] < 0,
         out['funding_at_signal'] <= 0.00005,
         out['funding_at_signal'] <= 0.0002],
        ['neg', 'near_zero', 'pos_5_20bps'],
        default='pos_gt20bps',
    )

    return out


def cell_stats(g: pd.DataFrame, cost_adj: float = 0.0) -> dict:
    """Compute full stats for a cell."""
    if len(g) < 10:
        return {}
    x4 = g['net_4h'] - cost_adj
    x8 = g['net_8h'] - cost_adj
    sym_mean = g.assign(net4_adj=x4).groupby('symbol')['net4_adj'].mean()
    return {
        'n': int(len(g)),
        'symbols': int(g['symbol'].nunique()),
        'events': int(g[['symbol', 'event_ts']].drop_duplicates().shape[0]),
        'net4_mean': float(x4.mean()),
        'net4_median': float(x4.median()),
        'net4_winrate': float((x4 > 0).mean()),
        'net4_pf': pf(x4),
        'net4_p10': float(x4.quantile(0.10)),
        'net4_p25': float(x4.quantile(0.25)),
        'net4_p75': float(x4.quantile(0.75)),
        'net4_p90': float(x4.quantile(0.90)),
        'net4_drop_top1pct': drop_top_pct_mean(x4, 0.01),
        'net4_drop_top5pct': drop_top_pct_mean(x4, 0.05),
        'net4_top5_conc': top_concentration(x4),
        'net8_mean': float(x8.mean()),
        'net8_median': float(x8.median()),
        'net8_winrate': float((x8 > 0).mean()),
        'net8_pf': pf(x8),
        'sym_eq_mean': float(sym_mean.mean()),
        'sym_eq_median': float(sym_mean.median()),
    }


def stratify(df: pd.DataFrame, group_cols: list[str], cost_adj: float = 0.0) -> list[dict]:
    """Stratify by group_cols and compute stats."""
    rows = []
    for key, g in df.groupby(group_cols, dropna=False, observed=True):
        stats = cell_stats(g, cost_adj)
        if not stats:
            continue
        if not isinstance(key, tuple):
            key = (key,)
        for col, val in zip(group_cols, key):
            stats[col] = str(val)
        rows.append(stats)
    return rows


def yearly_stability(df: pd.DataFrame, group_cols: list[str]) -> list[dict]:
    """Check year-by-year stability of each stratum."""
    rows = []
    for key, g in df.groupby(group_cols, dropna=False, observed=True):
        if len(g) < 40:
            continue
        if not isinstance(key, tuple):
            key = (key,)
        for yr, yg in g.groupby('year'):
            if len(yg) < 5:
                continue
            x4 = yg['net_4h']
            row = {
                'year': int(yr),
                'n': int(len(yg)),
                'net4_mean': float(x4.mean()),
                'net4_winrate': float((x4 > 0).mean()),
                'net4_pf': pf(x4),
            }
            for col, val in zip(group_cols, key):
                row[col] = str(val)
            rows.append(row)
    return rows


def main():
    print('[1/6] Loading and annotating trades...')
    df = load_and_annotate()
    print(f'  Total trades: {len(df):,}')

    # Filter to after_8_24h and after_24_48h windows (the interesting ones)
    df_8_24 = df[(df['lag_hours'] >= 8) & (df['lag_hours'] <= 24)].copy()
    df_24_48 = df[(df['lag_hours'] >= 24) & (df['lag_hours'] <= 48)].copy()

    # First signal per event only
    def first_signal(d):
        return d.sort_values(['symbol', 'event_ts', 'ts']).groupby(
            ['symbol', 'event_ts'], as_index=False, sort=False
        ).head(1)

    fs_8_24 = first_signal(df_8_24)
    fs_24_48 = first_signal(df_24_48)

    print(f'  8-24h first signals: {len(fs_8_24):,}')
    print(f'  24-48h first signals: {len(fs_24_48):,}')

    # Add buckets
    fs_8_24 = add_buckets(fs_8_24)
    fs_24_48 = add_buckets(fs_24_48)

    print('[2/6] Cross-stratification: rank × ret × funding...')

    STRATA_COLS = ['rank_bucket', 'ret_bucket', 'fund_bucket']

    # Raw (13bps)
    raw_8_24 = pd.DataFrame(stratify(fs_8_24, STRATA_COLS))
    raw_24_48 = pd.DataFrame(stratify(fs_24_48, STRATA_COLS))

    # With 25bps cost
    cost_8_24 = pd.DataFrame(stratify(fs_8_24, STRATA_COLS, COST_25BP - BASE_COST))
    cost_24_48 = pd.DataFrame(stratify(fs_24_48, STRATA_COLS, COST_25BP - BASE_COST))

    # With 50bps cost
    cost50_8_24 = pd.DataFrame(stratify(fs_8_24, STRATA_COLS, COST_50BP - BASE_COST))
    cost50_24_48 = pd.DataFrame(stratify(fs_24_48, STRATA_COLS, COST_50BP - BASE_COST))

    for df_ in [raw_8_24, raw_24_48, cost_8_24, cost_24_48, cost50_8_24, cost50_24_48]:
        if not df_.empty:
            df_['strata_key'] = df_.apply(lambda r: f"{r.get('rank_bucket','?')}|{r.get('ret_bucket','?')}|{r.get('fund_bucket','?')}", axis=1)

    # Save all
    raw_8_24.to_csv(OUT / 'cross_strata_8_24h_raw.csv', index=False)
    raw_24_48.to_csv(OUT / 'cross_strata_24_48h_raw.csv', index=False)
    cost_8_24.to_csv(OUT / 'cross_strata_8_24h_25bps.csv', index=False)
    cost_24_48.to_csv(OUT / 'cross_strata_24_48h_25bps.csv', index=False)
    cost50_8_24.to_csv(OUT / 'cross_strata_8_24h_50bps.csv', index=False)
    cost50_24_48.to_csv(OUT / 'cross_strata_24_48h_50bps.csv', index=False)

    print(f'  8-24h cells: {len(raw_8_24)}, 24-48h cells: {len(raw_24_48)}')

    print('[3/6] Finding best subsets...')

    # Combine both windows and find best
    all_raw = pd.concat([
        raw_8_24.assign(window='8-24h'),
        raw_24_48.assign(window='24-48h'),
    ], ignore_index=True)
    all_cost = pd.concat([
        cost_8_24.assign(window='8-24h'),
        cost_24_48.assign(window='24-48h'),
    ], ignore_index=True)
    all_cost50 = pd.concat([
        cost50_8_24.assign(window='8-24h'),
        cost50_24_48.assign(window='24-48h'),
    ], ignore_index=True)

    # Rank by: n>=40, cost25 net4_mean > 0, drop_top5 > 0, winrate >= 0.45, PF >= 1.2
    candidates = all_cost[
        (all_cost['n'] >= 40) &
        (all_cost['net4_mean'] > 0) &
        (all_cost['net4_drop_top5pct'] > 0) &
        (all_cost['net4_winrate'] >= 0.45) &
        (all_cost['net4_pf'] >= 1.2)
    ].copy()

    if not candidates.empty:
        candidates = candidates.sort_values('net4_pf', ascending=False)
        candidates.to_csv(OUT / 'best_candidates_25bps.csv', index=False)
        print(f'  Candidates passing 25bps gate (n>=40, mean>0, drop5>0, wr>=45%, PF>=1.2): {len(candidates)}')
        print(candidates[['strata_key', 'window', 'n', 'symbols', 'net4_mean', 'net4_median',
                          'net4_winrate', 'net4_pf', 'net4_drop_top5pct']].head(20).to_string(index=False))
    else:
        print('  NO candidates pass the 25bps gate.')
        # Try relaxed gate
        candidates_relaxed = all_cost[
            (all_cost['n'] >= 30) &
            (all_cost['net4_mean'] > -0.005) &
            (all_cost['net4_pf'] >= 1.1)
        ].copy()
        if not candidates_relaxed.empty:
            candidates_relaxed = candidates_relaxed.sort_values('net4_pf', ascending=False)
            candidates_relaxed.to_csv(OUT / 'best_candidates_relaxed.csv', index=False)
            print(f'  Relaxed gate (n>=30, mean>-0.5%, PF>=1.1): {len(candidates_relaxed)}')
            print(candidates_relaxed[['strata_key', 'window', 'n', 'net4_mean', 'net4_pf']].head(10).to_string(index=False))
        candidates = candidates_relaxed

    print('[4/6] Two-way stratification (simpler, more data per cell)...')

    # rank × ret (most data)
    for pair_cols in [['rank_bucket', 'ret_bucket'], ['rank_bucket', 'fund_bucket'], ['ret_bucket', 'fund_bucket']]:
        label = '_x_'.join(pair_cols)
        r8 = pd.DataFrame(stratify(fs_8_24, pair_cols))
        r24 = pd.DataFrame(stratify(fs_24_48, pair_cols))
        c8 = pd.DataFrame(stratify(fs_8_24, pair_cols, COST_25BP - BASE_COST))
        c24 = pd.DataFrame(stratify(fs_24_48, pair_cols, COST_25BP - BASE_COST))
        for d in [r8, r24, c8, c24]:
            if not d.empty:
                d['strata_key'] = d.apply(lambda r: '|'.join(str(r.get(c, '?')) for c in pair_cols), axis=1)
        r8.to_csv(OUT / f'twoway_{label}_8_24h_raw.csv', index=False)
        r24.to_csv(OUT / f'twoway_{label}_24_48h_raw.csv', index=False)
        c8.to_csv(OUT / f'twoway_{label}_8_24h_25bps.csv', index=False)
        c24.to_csv(OUT / f'twoway_{label}_24_48h_25bps.csv', index=False)

        # Best from 2-way
        all2 = pd.concat([c8.assign(window='8-24h'), c24.assign(window='24-48h')], ignore_index=True)
        best2 = all2[
            (all2['n'] >= 80) &
            (all2['net4_mean'] > 0) &
            (all2['net4_winrate'] >= 0.45)
        ].sort_values('net4_pf', ascending=False)
        if not best2.empty:
            best2.to_csv(OUT / f'twoway_{label}_best_25bps.csv', index=False)
            print(f'\n  [{label}] Best 2-way cells (25bps, n>=80, mean>0, wr>=45%):')
            print(best2[['strata_key', 'window', 'n', 'net4_mean', 'net4_winrate', 'net4_pf',
                         'net4_drop_top5pct']].head(10).to_string(index=False))

    print('\n[5/6] Yearly stability of top candidates...')

    # Take top 5 candidates from 3-way or 2-way
    top_candidates = []
    if not candidates.empty and len(candidates) > 0:
        for _, row in candidates.head(5).iterrows():
            top_candidates.append({
                'rank_bucket': row.get('rank_bucket', ''),
                'ret_bucket': row.get('ret_bucket', ''),
                'fund_bucket': row.get('fund_bucket', ''),
                'window': row.get('window', ''),
            })

    # Also check rank_bucket × ret_bucket best
    for label in ['rank_bucket_x_ret_bucket', 'rank_bucket_x_fund_bucket', 'ret_bucket_x_fund_bucket']:
        fp = OUT / f'twoway_{label}_best_25bps.csv'
        if fp.exists():
            tmp = pd.read_csv(fp)
            for _, row in tmp.head(3).iterrows():
                parts = row['strata_key'].split('|')
                cols = label.split('_x_')
                entry = {'window': row.get('window', '')}
                for c, v in zip(cols, parts):
                    entry[c] = v
                top_candidates.append(entry)

    # Deduplicate
    seen = set()
    unique_candidates = []
    for c in top_candidates:
        key = tuple(sorted(c.items()))
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)

    yearly_rows = []
    for cand in unique_candidates[:10]:
        filt_cols = [c for c in ['rank_bucket', 'ret_bucket', 'fund_bucket'] if c in cand and cand[c]]
        if not filt_cols:
            continue
        data = fs_8_24 if cand.get('window') == '8-24h' else fs_24_48 if cand.get('window') == '24-48h' else fs_8_24
        mask = pd.Series(True, index=data.index)
        for col in filt_cols:
            mask = mask & (data[col] == cand[col])
        subset = data[mask]
        if len(subset) < 30:
            continue

        label = '|'.join(f"{c}={cand[c]}" for c in filt_cols)
        for yr, yg in subset.groupby('year'):
            if len(yg) < 5:
                continue
            x4 = yg['net_4h'] - (COST_25BP - BASE_COST)
            yearly_rows.append({
                'candidate': label,
                'window': cand.get('window', ''),
                'year': int(yr),
                'n': int(len(yg)),
                'net4_mean': float(x4.mean()),
                'net4_winrate': float((x4 > 0).mean()),
                'net4_pf': pf(x4),
            })

    yearly = pd.DataFrame(yearly_rows)
    if not yearly.empty:
        yearly.to_csv(OUT / 'yearly_stability.csv', index=False)
        print('\n  Yearly stability (25bps cost):')
        print(yearly.to_string(index=False))

        # Summarize: how many years positive per candidate
        yr_summary = yearly.groupby('candidate').agg(
            years_positive=('net4_mean', lambda x: (x > 0).sum()),
            years_total=('net4_mean', 'size'),
            mean_across_years=('net4_mean', 'mean'),
            min_year_mean=('net4_mean', 'min'),
        ).reset_index()
        yr_summary.to_csv(OUT / 'yearly_stability_summary.csv', index=False)
        print('\n  Yearly summary:')
        print(yr_summary.to_string(index=False))

    print('\n[6/6] Final verdict...')

    # Verdict logic
    verdict = 'CLOSE'
    verdict_reasons = []

    # Check if any 3-way candidate passes strict gate
    strict_pass = []
    if not candidates.empty:
        strict = candidates[
            (candidates['n'] >= 80) &
            (candidates['net4_mean'] > 0.005) &
            (candidates['net4_winrate'] >= 0.48) &
            (candidates['net4_pf'] >= 1.3) &
            (candidates['net4_drop_top5pct'] > 0)
        ]
        if not strict.empty:
            strict_pass = strict.to_dict('records')
            verdict = 'GO'
            verdict_reasons.append(f'{len(strict_pass)} cells pass strict gate (n>=80, mean>0.5%, wr>=48%, PF>=1.3, drop5>0)')
        else:
            # Check relaxed
            relaxed = candidates[
                (candidates['n'] >= 60) &
                (candidates['net4_mean'] > 0) &
                (candidates['net4_pf'] >= 1.2)
            ]
            if not relaxed.empty:
                verdict = 'WATCH'
                verdict_reasons.append(f'{len(relaxed)} cells pass relaxed gate but none pass strict gate')
            else:
                verdict_reasons.append('No cells pass even relaxed gate at 25bps cost')

    # Check yearly stability
    if not yearly.empty:
        yr_sum = yearly.groupby('candidate')['net4_mean'].agg(['mean', 'min', 'count'])
        stable = yr_sum[(yr_sum['mean'] > 0) & (yr_sum['count'] >= 3) & (yr_sum['min'] > -0.02)]
        if len(stable) > 0:
            verdict_reasons.append(f'{len(stable)} candidates have stable yearly returns')
            if verdict == 'CLOSE':
                verdict = 'WATCH'
        else:
            verdict_reasons.append('No candidates show stable yearly returns')

    verdict_data = {
        'verdict': verdict,
        'reasons': verdict_reasons,
        'strict_pass_count': len(strict_pass),
        'generated_at': pd.Timestamp.now('UTC').isoformat(),
    }
    (OUT / 'verdict.json').write_text(json.dumps(verdict_data, indent=2, default=str))
    print(f'\n  VERDICT: {verdict}')
    for r in verdict_reasons:
        print(f'    - {r}')

    print(f'\n[done] {OUT}')


if __name__ == '__main__':
    main()
