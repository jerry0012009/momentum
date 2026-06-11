#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank143_orb_phase_retest_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank143_orb_phase_retest_15m'

ASSETS = {
    'BTC-USD': 'BTCUSDT',
    'ETH-USD': 'ETHUSDT',
    'SOL-USD': 'SOLUSDT',
}
PSEUDO_OPENS = {(0, 0), (8, 0), (13, 30)}
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
RANGE_BARS = 2
TAU_ATR = 0.10
WAIT_BARS = 12
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 24
ARMS = ['A_binary_retest', 'B_phase_only', 'C_phase_score60', 'D_phase_score70']


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f'{symbol}__120d__15m.csv'
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    return df.sort_values('timestamp').reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        (df['high'] - df['low']).abs(),
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def prepare(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol).copy()
    df['asset'] = asset
    df['atr'] = atr(df)
    tp = (df['high'] + df['low'] + df['close']) / 3.0
    vol = df['volume'].replace(0, np.nan)
    df['vwap48'] = (tp.mul(vol).rolling(48, min_periods=12).sum() / vol.rolling(48, min_periods=12).sum())
    df['rvol48'] = df['volume'] / df['volume'].rolling(48, min_periods=12).mean()
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = (-delta).clip(lower=0)
    rs = up.ewm(alpha=1/14, adjust=False).mean() / down.ewm(alpha=1/14, adjust=False).mean().replace(0, np.nan)
    df['rsi14'] = 100 - (100 / (1 + rs))
    return df


def pseudo_starts(df: pd.DataFrame) -> list[int]:
    out = []
    for i, ts in enumerate(df['timestamp']):
        ts = pd.Timestamp(ts)
        if (int(ts.hour), int(ts.minute)) in PSEUDO_OPENS:
            out.append(i)
    return out


def score_row(row: pd.Series, range_high: float) -> float:
    score = 0.0
    if pd.notna(row['vwap48']) and row['close'] > row['vwap48']:
        score += 25
    rvol = float(row['rvol48']) if pd.notna(row['rvol48']) else 0.0
    if rvol >= 2.0:
        score += 25
    elif rvol >= 1.5:
        score += 18
    elif rvol >= 1.2:
        score += 10
    if pd.notna(row['ema20']) and pd.notna(row['ema50']) and row['close'] > row['ema20'] > row['ema50']:
        score += 20
    if pd.notna(row['rsi14']) and 52 <= row['rsi14'] <= 72:
        score += 15
    if row['close'] > range_high and row['high'] >= row['close']:
        score += 10
    return float(score)


def build_events(df: pd.DataFrame) -> pd.DataFrame:
    starts = pseudo_starts(df)
    rows = []
    for s_idx, start_idx in enumerate(starts):
        next_start = starts[s_idx + 1] if s_idx + 1 < len(starts) else len(df)
        range_end = start_idx + RANGE_BARS - 1
        if range_end + 1 >= next_start:
            continue
        rg = df.iloc[start_idx:range_end+1]
        range_high = float(rg['high'].max())
        range_low = float(rg['low'].min())
        range_mid = 0.5 * (range_high + range_low)
        breakout_idx = None
        for i in range(range_end + 1, next_start):
            row = df.iloc[i]
            a = float(row['atr']) if pd.notna(row['atr']) else float('nan')
            if not math.isfinite(a) or a <= 0:
                continue
            if float(row['close']) > range_high + TAU_ATR * a:
                breakout_idx = i
                break
        if breakout_idx is None:
            continue
        bounce_idx = None
        timeout_idx = min(next_start - 1, breakout_idx + WAIT_BARS)
        invalid = False
        continue_shares = {arm: 0 for arm in ARMS}
        fail_shares = {arm: 0 for arm in ARMS}
        timeout_shares = {arm: 0 for arm in ARMS}
        for i in range(breakout_idx + 1, timeout_idx + 1):
            row = df.iloc[i]
            a = float(row['atr']) if pd.notna(row['atr']) else float(df.iloc[breakout_idx]['atr'])
            if float(row['close']) < range_mid:
                invalid = True
                break
            touch = float(row['low']) <= range_high + 0.05 * a
            hold = float(row['close']) >= range_high + 0.03 * a
            bounce = float(row['close']) > range_high + TAU_ATR * a
            score = score_row(row, range_high)
            if touch and hold and bounce_idx is None:
                bounce_idx = i
                rows.append({
                    'asset': df.iloc[0]['asset'], 'session_start_ts': df.iloc[start_idx]['timestamp'],
                    'range_high': range_high, 'range_low': range_low, 'range_mid': range_mid,
                    'breakout_idx': breakout_idx, 'signal_idx': i, 'signal_ts': df.iloc[i]['timestamp'],
                    'atr_at_signal': float(df.iloc[i]['atr']), 'score': score, 'arm': 'A_binary_retest',
                    'continue_share': 1 if bounce else 0, 'fail_share': 0, 'timeout_share': 0,
                    'invalidation_12': np.nan, 'invalidation_24': np.nan,
                })
            if touch and bounce:
                phase_score = score
                rows.append({
                    'asset': df.iloc[0]['asset'], 'session_start_ts': df.iloc[start_idx]['timestamp'],
                    'range_high': range_high, 'range_low': range_low, 'range_mid': range_mid,
                    'breakout_idx': breakout_idx, 'signal_idx': i, 'signal_ts': df.iloc[i]['timestamp'],
                    'atr_at_signal': float(df.iloc[i]['atr']), 'score': phase_score, 'arm': 'B_phase_only',
                    'continue_share': 1, 'fail_share': 0, 'timeout_share': 0,
                    'invalidation_12': np.nan, 'invalidation_24': np.nan,
                })
                if phase_score >= 60:
                    rows.append({
                        'asset': df.iloc[0]['asset'], 'session_start_ts': df.iloc[start_idx]['timestamp'],
                        'range_high': range_high, 'range_low': range_low, 'range_mid': range_mid,
                        'breakout_idx': breakout_idx, 'signal_idx': i, 'signal_ts': df.iloc[i]['timestamp'],
                        'atr_at_signal': float(df.iloc[i]['atr']), 'score': phase_score, 'arm': 'C_phase_score60',
                        'continue_share': 1, 'fail_share': 0, 'timeout_share': 0,
                        'invalidation_12': np.nan, 'invalidation_24': np.nan,
                    })
                if phase_score >= 70:
                    rows.append({
                        'asset': df.iloc[0]['asset'], 'session_start_ts': df.iloc[start_idx]['timestamp'],
                        'range_high': range_high, 'range_low': range_low, 'range_mid': range_mid,
                        'breakout_idx': breakout_idx, 'signal_idx': i, 'signal_ts': df.iloc[i]['timestamp'],
                        'atr_at_signal': float(df.iloc[i]['atr']), 'score': phase_score, 'arm': 'D_phase_score70',
                        'continue_share': 1, 'fail_share': 0, 'timeout_share': 0,
                        'invalidation_12': np.nan, 'invalidation_24': np.nan,
                    })
                break
        if invalid or bounce_idx is None:
            for arm in ARMS:
                rows.append({
                    'asset': df.iloc[0]['asset'], 'session_start_ts': df.iloc[start_idx]['timestamp'],
                    'range_high': range_high, 'range_low': range_low, 'range_mid': range_mid,
                    'breakout_idx': breakout_idx, 'signal_idx': np.nan, 'signal_ts': pd.NaT,
                    'atr_at_signal': np.nan, 'score': np.nan, 'arm': arm,
                    'continue_share': 0, 'fail_share': 1 if invalid else 0, 'timeout_share': 0 if invalid else 1,
                    'invalidation_12': np.nan, 'invalidation_24': np.nan,
                })
    events = pd.DataFrame(rows)
    # keep first row per session/arm where signal exists; fallback to fail/timeout row
    if events.empty:
        return events
    events['session_key'] = events['asset'] + '|' + events['session_start_ts'].astype(str) + '|' + events['arm']
    events = events.sort_values(['session_key', 'signal_idx'], na_position='last').groupby('session_key', as_index=False).first()
    return events.drop(columns=['session_key'])


def simulate(df: pd.DataFrame, events: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    trades = []
    cost_rate = cost_bps / 10000.0
    last_exit = {arm: -1 for arm in ARMS}
    for _, e in events.sort_values(['arm', 'signal_idx'], na_position='last').iterrows():
        if pd.isna(e['signal_idx']):
            continue
        arm = e['arm']
        signal_idx = int(e['signal_idx'])
        if signal_idx <= last_exit[arm]:
            continue
        entry_idx = signal_idx + 1
        if entry_idx >= len(df):
            continue
        entry = float(df.iloc[entry_idx]['open'])
        a = float(e['atr_at_signal']) if pd.notna(e['atr_at_signal']) else float('nan')
        if not math.isfinite(entry) or not math.isfinite(a) or a <= 0:
            continue
        stop = entry - STOP_ATR * a
        target = entry + TARGET_ATR * a
        last_bar = min(len(df) - 1, entry_idx + TIME_STOP_BARS - 1)
        exit_idx, exit_price, reason = None, None, None
        inv12, inv24 = 0, 0
        for i in range(entry_idx, last_bar + 1):
            row = df.iloc[i]
            if i <= min(last_bar, entry_idx + 11) and float(row['low']) <= stop:
                inv12 = 1
            if i <= min(last_bar, entry_idx + 23) and float(row['low']) <= stop:
                inv24 = 1
            if float(row['low']) <= stop:
                exit_idx, exit_price, reason = i, stop, 'atr_stop'
                break
            if float(row['high']) >= target:
                exit_idx, exit_price, reason = i, target, 'atr_target'
                break
        if exit_idx is None:
            exit_idx, exit_price, reason = last_bar, float(df.iloc[last_bar]['close']), 'time_stop'
        gross = exit_price / entry - 1.0
        net_mult = (exit_price / entry) * (1 - cost_rate) * (1 - cost_rate)
        net = net_mult - 1.0
        trades.append({
            'asset': e['asset'], 'arm': arm, 'cost_bps_per_side': cost_bps,
            'session_start_ts': pd.Timestamp(e['session_start_ts']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'signal_ts': pd.Timestamp(e['signal_ts']).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'entry_ts': df.iloc[entry_idx]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'exit_ts': df.iloc[exit_idx]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            'score': e['score'], 'gross_ret': gross, 'net_ret': net, 'hold_bars': exit_idx - entry_idx + 1,
            'exit_reason': reason, 'win': int(net > 0), 'invalidation_12': inv12, 'invalidation_24': inv24,
        })
        last_exit[arm] = exit_idx
    return pd.DataFrame(trades)


def summarize(events: pd.DataFrame, trades: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    rows = []
    for arm in ARMS:
        e = events[events['arm'] == arm].copy()
        t = trades[trades['arm'] == arm].copy() if not trades.empty else pd.DataFrame()
        by_asset = []
        for asset in ASSETS:
            ea = e[e['asset'] == asset]
            ta = t[t['asset'] == asset] if not t.empty else pd.DataFrame()
            total_ret = float(np.prod(1.0 + ta['net_ret'].to_numpy()) - 1.0) if not ta.empty else 0.0
            by_asset.append({
                'asset': asset, 'arm': arm, 'cost_bps_per_side': cost_bps,
                'events': len(ea), 'trades': len(ta),
                'trade_count_retention': (len(ta) / len(ea)) if len(ea) else np.nan,
                'continue_share': float(ea['continue_share'].mean()) if len(ea) else np.nan,
                'fail_share': float(ea['fail_share'].mean()) if len(ea) else np.nan,
                'timeout_share': float(ea['timeout_share'].mean()) if len(ea) else np.nan,
                'post_cost_expectancy': float(ta['net_ret'].mean()) if not ta.empty else np.nan,
                'total_return': total_ret,
                'win_rate': float(ta['win'].mean()) if not ta.empty else np.nan,
                'invalidation_12_ratio': float(ta['invalidation_12'].mean()) if not ta.empty else np.nan,
                'invalidation_24_ratio': float(ta['invalidation_24'].mean()) if not ta.empty else np.nan,
                'avg_score': float(ta['score'].mean()) if not ta.empty else np.nan,
            })
        asset_df = pd.DataFrame(by_asset)
        rows.append({
            'arm': arm, 'cost_bps_per_side': cost_bps,
            'mean_total_return': float(asset_df['total_return'].mean()),
            'positive_asset_ratio': float((asset_df['total_return'] > 0).mean()),
            'mean_trade_count_retention': float(asset_df['trade_count_retention'].mean()),
            'mean_continue_share': float(asset_df['continue_share'].mean()),
            'mean_fail_share': float(asset_df['fail_share'].mean()),
            'mean_timeout_share': float(asset_df['timeout_share'].mean()),
            'mean_post_cost_expectancy': float(asset_df['post_cost_expectancy'].mean()),
            'mean_invalidation_12_ratio': float(asset_df['invalidation_12_ratio'].mean()),
            'mean_invalidation_24_ratio': float(asset_df['invalidation_24_ratio'].mean()),
            'mean_trades': float(asset_df['trades'].mean()),
        })
    return pd.DataFrame(rows)


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    events_all = []
    trade_frames = []
    summary_frames = []
    asset_summaries = []
    for asset, symbol in ASSETS.items():
        df = prepare(asset, symbol)
        events = build_events(df)
        events_all.append(events)
        for cost in COSTS:
            trades = simulate(df, events, cost)
            if not trades.empty:
                trade_frames.append(trades)
            # asset summary per arm
            for arm in ARMS:
                e = events[events['arm'] == arm]
                t = trades[trades['arm'] == arm] if not trades.empty else pd.DataFrame()
                asset_summaries.append({
                    'asset': asset, 'arm': arm, 'cost_bps_per_side': cost,
                    'events': len(e), 'trades': len(t),
                    'trade_count_retention': (len(t)/len(e)) if len(e) else np.nan,
                    'continue_share': float(e['continue_share'].mean()) if len(e) else np.nan,
                    'fail_share': float(e['fail_share'].mean()) if len(e) else np.nan,
                    'timeout_share': float(e['timeout_share'].mean()) if len(e) else np.nan,
                    'post_cost_expectancy': float(t['net_ret'].mean()) if not t.empty else np.nan,
                    'total_return': float(np.prod(1.0 + t['net_ret'].to_numpy()) - 1.0) if not t.empty else 0.0,
                    'invalidation_12_ratio': float(t['invalidation_12'].mean()) if not t.empty else np.nan,
                    'invalidation_24_ratio': float(t['invalidation_24'].mean()) if not t.empty else np.nan,
                })
    events_df = pd.concat(events_all, ignore_index=True) if events_all else pd.DataFrame()
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_df = pd.DataFrame(asset_summaries)
    overall = []
    for cost in COSTS:
        overall.append(summarize(events_df, trades_df[trades_df['cost_bps_per_side'] == cost] if not trades_df.empty else pd.DataFrame(), cost))
    overall_df = pd.concat(overall, ignore_index=True)
    primary = overall_df[overall_df['cost_bps_per_side'] == PRIMARY_COST].sort_values('mean_total_return', ascending=False).reset_index(drop=True)
    events_df.to_csv(ART_DIR / 'events.csv', index=False)
    trades_df.to_csv(ART_DIR / 'trades.csv', index=False)
    asset_df.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall_df.to_csv(ART_DIR / 'summary.csv', index=False)
    (ART_DIR / 'meta.txt').write_text(f'generated_at_utc={datetime.now(timezone.utc).isoformat()}\n', encoding='utf-8')
    print(primary.to_csv(index=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
