#!/usr/bin/env python3
"""
Explore whether v1.6a survives as a SECOND-STAGE timing filter:
"after a top-gainer event appears, wait for 1h price+volume confirmation, then long".

This is NOT a standalone full-market signal validation. It conditions on the existing
v1/v1.6 top-gainer event panel and stratifies by trigger timing:
- h<0: pre-event control / not tradable after event
- h=0..16: intraday/event-day approximation (only causal if a real-time event detector exists)
- h>=24: strict daily-close version (top-gainer day is known only after the daily bar closes)

Artifacts:
  reports/artifacts/binance_event_study_v1_6a_post_event/
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
PANEL = ROOT / 'reports/artifacts/binance_hourly_event_study_v1_6/hourly_event_panel.pkl'
OUT = ROOT / 'reports/artifacts/binance_event_study_v1_6a_post_event'
OUT.mkdir(parents=True, exist_ok=True)

COST = 0.0013  # 0.13% round-trip, same as v1.6a
VOL_THRESHOLDS = [2.0, 3.0, 5.0, 7.0]
RET_THRESHOLDS = [0.005, 0.01, 0.02, 0.03, 0.05]
VOL_WINDOWS = [12, 20]

# Timing interpretation:
# event_date h=0 = start of the top-gainer event day in the event panel.
# Daily top-gainer is strictly known only after h=24. h=0..16 needs a causal real-time detector.
WINDOWS = [
    ('pre_control_h-20_0', -20.0, -1e-9, '事前窗口：不能当事件后交易，只看原 alpha 是否主要来自预判'),
    ('event_day_h0_16', 0.0, 16.0, '事件日内：若有实时榜单/异动检测器，可能可交易'),
    ('event_day_late_h8_24', 8.0, 24.0, '事件日后半段：更接近已经被市场看到后的追涨'),
    ('strict_after_daily_close_h24_48', 24.0, 48.0, '严格日线确认后第 1 天'),
    ('strict_after_daily_close_h24_72', 24.0, 72.0, '严格日线确认后 1-3 天'),
    ('strict_late_h48_120', 48.0, 120.0, '更晚的事件后观察窗口'),
]

V4 = dict(vol_thresh=3.0, ret_thresh=0.01, vol_window=20)


def profit_factor(x: np.ndarray) -> float:
    if len(x) == 0:
        return np.nan
    wins = x[x > 0].sum()
    losses = -x[x < 0].sum()
    if losses <= 0:
        return np.inf if wins > 0 else np.nan
    return float(wins / losses)


def summarize_returns(rets4_gross, rets8_gross, cost=COST) -> dict:
    r4 = np.asarray(rets4_gross, dtype='float64') - cost
    r8 = np.asarray(rets8_gross, dtype='float64') - cost
    if len(r4) == 0:
        return {
            'n': 0, 'net4_mean': np.nan, 'net4_median': np.nan, 'net4_winrate': np.nan, 'net4_pf': np.nan,
            'net8_mean': np.nan, 'net8_median': np.nan, 'net8_winrate': np.nan, 'net8_pf': np.nan,
            'gross4_mean': np.nan, 'gross8_mean': np.nan,
        }
    return {
        'n': int(len(r4)),
        'net4_mean': float(np.nanmean(r4)),
        'net4_median': float(np.nanmedian(r4)),
        'net4_winrate': float(np.nanmean(r4 > 0)),
        'net4_pf': profit_factor(r4),
        'net8_mean': float(np.nanmean(r8)),
        'net8_median': float(np.nanmedian(r8)),
        'net8_winrate': float(np.nanmean(r8 > 0)),
        'net8_pf': profit_factor(r8),
        'gross4_mean': float(np.nanmean(rets4_gross)),
        'gross8_mean': float(np.nanmean(rets8_gross)),
    }


def cooldown_positions(pos: np.ndarray, min_gap: int = 4) -> list[int]:
    kept = []
    prev = -10**9
    for i in pos:
        if int(i) - prev >= min_gap:
            kept.append(int(i))
            prev = int(i)
    return kept


def safe_fwd(closes: np.ndarray, i: int, hold: int) -> float:
    j = i + hold
    if j >= len(closes):
        return np.nan
    ep = closes[i]
    if not np.isfinite(ep) or ep <= 0:
        return np.nan
    return float(closes[j] / ep - 1.0)


def pct(x):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return float(x)


def main():
    t0 = time.time()
    print(f'[load] {PANEL}')
    panel = pd.read_pickle(PANEL)
    panel = panel[panel['ev_tags'].astype(str).str.contains('top_gainer_1d', na=False)].copy()
    panel = panel.sort_values(['symbol', 'event_date', 'ts']).reset_index(drop=True)
    panel['ret_1h'] = panel.groupby(['symbol', 'event_date'])['close'].pct_change()
    print(f'[load] top_gainer rows={len(panel):,}, events={panel.groupby(["symbol","event_date"]).ngroups:,}, time={time.time()-t0:.1f}s')

    # Basic panel profile
    profile = {
        'rows': int(len(panel)),
        'events': int(panel.groupby(['symbol', 'event_date']).ngroups),
        'symbols': int(panel['symbol'].nunique()),
        'event_date_min': str(panel['event_date'].min()),
        'event_date_max': str(panel['event_date'].max()),
        'hours_from_event_min': float(panel['hours_from_event'].min()),
        'hours_from_event_max': float(panel['hours_from_event'].max()),
        'cost_round_trip': COST,
    }

    arrays = []
    for (sym, ed), ev in panel.groupby(['symbol', 'event_date'], sort=False):
        ev = ev.sort_values('ts').reset_index(drop=True)
        if len(ev) < 40:
            continue
        closes = ev['close'].to_numpy('float64')
        vols = ev['quote_volume'].to_numpy('float64')
        rets = ev['ret_1h'].to_numpy('float64')
        hfe = ev['hours_from_event'].to_numpy('float64')
        # Original v1.6a style: rolling mean includes current bar.
        # Keep this for comparability; note in output.
        s = pd.Series(vols)
        tv = {
            12: s.rolling(12, min_periods=6).mean().to_numpy('float64'),
            20: s.rolling(20, min_periods=10).mean().to_numpy('float64'),
        }
        meta = {
            'symbol': sym,
            'event_date': str(pd.Timestamp(ed).date()),
            'year': int(pd.Timestamp(ed).year),
            'structure': str(ev['ev_structure'].iloc[0]) if 'ev_structure' in ev else 'NA',
            'vol_structure': str(ev['ev_vol_structure'].iloc[0]) if 'ev_vol_structure' in ev else 'NA',
            'funding_traj': str(ev['ev_funding_traj'].iloc[0]) if 'ev_funding_traj' in ev else 'NA',
            'funding_bucket': str(ev['ev_funding_bucket'].iloc[0]) if 'ev_funding_bucket' in ev else 'NA',
        }
        arrays.append({'meta': meta, 'closes': closes, 'vols': vols, 'rets': rets, 'hfe': hfe,
                       'funding': ev['funding_rate'].to_numpy('float64'), 'tv': tv})
    print(f'[arrays] usable_events={len(arrays):,}, time={time.time()-t0:.1f}s')

    param_rows = []
    v4_trades = []
    top_combo_trades = []

    # To inspect cost sensitivity later, collect gross returns for each combo/window in compact form.
    for wlabel, hmin, hmax, wdesc in WINDOWS:
        print(f'[scan] {wlabel} h=[{hmin},{hmax}]')
        for vw in VOL_WINDOWS:
            for vt in VOL_THRESHOLDS:
                for rt in RET_THRESHOLDS:
                    g4, g8 = [], []
                    n_events_with_signal = 0
                    for ev in arrays:
                        hfe = ev['hfe']; rets = ev['rets']; tv = ev['tv'][vw]; vols = ev['vols']
                        valid = (
                            (hfe >= hmin) & (hfe <= hmax) &
                            np.isfinite(tv) & (tv > 0) & np.isfinite(rets) &
                            ((vols / tv) >= vt) & (rets >= rt)
                        )
                        pos = np.where(valid)[0]
                        if len(pos) == 0:
                            continue
                        kept = cooldown_positions(pos, 4)
                        if kept:
                            n_events_with_signal += 1
                        for i in kept:
                            r4 = safe_fwd(ev['closes'], i, 4)
                            r8 = safe_fwd(ev['closes'], i, 8)
                            if np.isfinite(r4) and np.isfinite(r8):
                                g4.append(r4); g8.append(r8)
                                if (vw == V4['vol_window'] and abs(vt - V4['vol_thresh']) < 1e-12 and abs(rt - V4['ret_thresh']) < 1e-12):
                                    vr = ev['vols'][i] / ev['tv'][vw][i]
                                    v4_trades.append({
                                        **ev['meta'], 'window': wlabel, 'window_desc': wdesc,
                                        'trigger_hour': float(ev['hfe'][i]),
                                        'vol_ratio': float(vr), 'ret_at_signal': float(ev['rets'][i]),
                                        'funding_at_signal': float(ev['funding'][i]) if np.isfinite(ev['funding'][i]) else np.nan,
                                        'gross4': float(r4), 'gross8': float(r8),
                                        'net4': float(r4 - COST), 'net8': float(r8 - COST),
                                    })
                    summ = summarize_returns(g4, g8, COST)
                    param_rows.append({
                        'window': wlabel, 'window_desc': wdesc,
                        'h_min': hmin, 'h_max': hmax,
                        'vol_window': vw, 'vol_thresh': vt, 'ret_thresh': rt,
                        'n_events_with_signal': n_events_with_signal,
                        **summ,
                        'net4_at_cost_0bps': float(np.nanmean(g4)) if g4 else np.nan,
                        'net4_at_cost_13bps': (float(np.nanmean(g4)) - 0.0013) if g4 else np.nan,
                        'net4_at_cost_25bps': (float(np.nanmean(g4)) - 0.0025) if g4 else np.nan,
                        'net4_at_cost_50bps': (float(np.nanmean(g4)) - 0.0050) if g4 else np.nan,
                    })

    param = pd.DataFrame(param_rows)
    param.to_csv(OUT / 'post_event_param_summary.csv', index=False)
    v4 = pd.DataFrame(v4_trades)
    v4.to_csv(OUT / 'v4_post_event_trades.csv', index=False)

    # Strata for exact V4 signal.
    strata_rows = []
    if not v4.empty:
        def add_strata(group_col):
            for keys, g in v4.groupby(['window', group_col], dropna=False):
                window, val = keys
                s = summarize_returns(g['gross4'].to_numpy(), g['gross8'].to_numpy(), COST)
                strata_rows.append({'kind': group_col, 'window': window, 'bucket': str(val), **s})
        for col in ['year', 'structure', 'vol_structure', 'funding_traj', 'funding_bucket']:
            add_strata(col)
        v4['funding_sign'] = np.select(
            [v4['funding_at_signal'] < 0, v4['funding_at_signal'] > 0],
            ['negative', 'positive'], default='zero_or_nan')
        add_strata('funding_sign')
        v4['trigger_hour_bucket'] = pd.cut(
            v4['trigger_hour'],
            bins=[-999, -20, -12, -6, 0, 4, 8, 12, 16, 24, 48, 72, 120, 999],
            labels=['<-20','-20~-12','-12~-6','-6~0','0~4','4~8','8~12','12~16','16~24','24~48','48~72','72~120','>120'],
            right=False,
        )
        add_strata('trigger_hour_bucket')
    strata = pd.DataFrame(strata_rows)
    strata.to_csv(OUT / 'v4_post_event_strata.csv', index=False)

    # Top combos per window with minimum samples.
    eligible = param[param['n'] >= 100].copy()
    top_by_4 = (eligible.sort_values(['window', 'net4_mean'], ascending=[True, False])
                .groupby('window').head(8).reset_index(drop=True))
    top_by_8 = (eligible.sort_values(['window', 'net8_mean'], ascending=[True, False])
                .groupby('window').head(8).reset_index(drop=True))
    top_by_4.to_csv(OUT / 'top_combos_by_net4.csv', index=False)
    top_by_8.to_csv(OUT / 'top_combos_by_net8.csv', index=False)

    # Exact V4 summary by timing window.
    v4_summary = []
    if not v4.empty:
        for window, g in v4.groupby('window'):
            v4_summary.append({'window': window, **summarize_returns(g['gross4'].to_numpy(), g['gross8'].to_numpy(), COST)})
    v4s = pd.DataFrame(v4_summary).sort_values('window') if v4_summary else pd.DataFrame()
    v4s.to_csv(OUT / 'v4_summary_by_window.csv', index=False)

    # Generate compact JSON with headline tables.
    def records(df, cols=None, n=None):
        if cols is not None:
            df = df[cols]
        if n is not None:
            df = df.head(n)
        # clean nan/inf
        recs = []
        for r in df.to_dict(orient='records'):
            recs.append({k: (None if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else v) for k,v in r.items()})
        return recs

    summary = {
        'profile': profile,
        'method_notes': [
            'vol_ratio follows original v1.6a implementation: current hour quote_volume / rolling mean including current bar; this keeps comparability but is slightly dampened versus prior-only baseline.',
            'ret_1h is close-to-close pct_change inside each event window; entry is at signal hour close; fixed hold uses future close after 4h/8h; net subtracts 0.13% round-trip cost.',
            'h=0 is start of event_date; a daily top-gainer event is strictly observable only after h=24. h=0..16 should be interpreted as tradable only if a separate real-time event detector exists.',
        ],
        'v4_exact_by_window': records(v4s),
        'top_combos_by_net4_n_ge_100': records(top_by_4, n=40),
        'top_combos_by_net8_n_ge_100': records(top_by_8, n=40),
    }
    with open(OUT / 'post_event_exploration_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print('\n[V4 exact by window]')
    if not v4s.empty:
        show = v4s[['window','n','net4_mean','net4_winrate','net8_mean','net8_winrate','net4_pf','net8_pf']]
        print(show.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print('\n[Top combos by 4h net, n>=100]')
    print(top_by_4[['window','vol_window','vol_thresh','ret_thresh','n','net4_mean','net4_winrate','net8_mean','net8_winrate','net4_at_cost_25bps','net4_at_cost_50bps']]
          .head(48).to_string(index=False, float_format=lambda x: f'{x:.4f}'))
    print(f'\n[done] {OUT}, time={time.time()-t0:.1f}s')

if __name__ == '__main__':
    main()
