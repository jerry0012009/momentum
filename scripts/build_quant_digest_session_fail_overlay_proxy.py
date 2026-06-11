#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'quant_digests' / 'session_fail_overlay_proxy'
ART_DIR.mkdir(parents=True, exist_ok=True)

ASSETS = {
    'BTC-USD': 'BTCUSDT',
    'ETH-USD': 'ETHUSDT',
    'SOL-USD': 'SOLUSDT',
}
SETUPS = ['ema_psar_long', 'fib_retest_long', 'breakout_short']
LONG_SETUPS = {'ema_psar_long', 'fib_retest_long'}
VARIANTS = ['baseline', 'fail2_halfsize', 'fail2_veto', 'fail3_veto']
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 3
LOOKBACK = 30
ATR_PERIOD = 14
VOL_PERIOD = 20
EPS = 1e-9
SESSION_HOURS = 8


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f'{symbol}__120d__15m.csv'
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df['asset'] = asset
    return df.sort_values('timestamp').reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df['close'].shift(1)
    tr = pd.concat(
        [
            (df['high'] - df['low']).abs(),
            (df['high'] - prev_close).abs(),
            (df['low'] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df['high'].to_numpy(dtype=float)
    low = df['low'].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema15'] = df['close'].ewm(span=15, adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_slope'] = df['ema9'].pct_change(3)
    df['vol_ma20'] = df['volume'].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df['atr14'] = atr(df)
    df['psar'] = compute_psar(df)
    df['rolling_low20'] = df['low'].rolling(20, min_periods=20).min().shift(1)
    df['swing_high_30'] = df['high'].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df['swing_low_30'] = df['low'].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    rng = df['swing_high_30'] - df['swing_low_30']
    df['fib_50'] = df['swing_high_30'] - 0.5 * rng
    df['fib_618'] = df['swing_high_30'] - 0.618 * rng
    df['ema_psar_long_signal'] = (
        (df['ema9'] > df['ema15'])
        & (df['ema_slope'] > 0.0003)
        & (df['psar'] < df['close'])
        & (df['close'] > df['high'].shift(1))
        & (df['close'].shift(1) < df['ema9'].shift(1))
        & (df['volume'] > df['vol_ma20'])
    ).fillna(False)
    df['fib_retest_long_signal'] = (
        df['fib_618'].notna()
        & (df['ema9'] > df['ema15'])
        & (df['ema_slope'] > 0)
        & (df['close'] > df['fib_618'])
        & (df['close'].shift(1) <= df['fib_618'].shift(1))
        & (df['low'] <= df['fib_618'] + 0.2 * df['atr14'])
        & (df['close'] > df['fib_50'])
        & (df['volume'] > df['vol_ma20'])
    ).fillna(False)
    low = df['rolling_low20']
    atr14 = df['atr14']
    df['breakout_short_signal'] = (
        low.notna()
        & (df['ema9'] < df['ema15'])
        & (df['ema_slope'] < -0.0003)
        & (df['close'].shift(1) > low.shift(1))
        & (df['close'].shift(2) > low.shift(2))
        & (df['close'] < low - 0.1 * atr14)
        & (df['high'] <= low + 0.3 * atr14)
        & (df['volume'] > df['vol_ma20'])
    ).fillna(False)
    return df


def trigger_level(frame: pd.DataFrame, idx: int, setup: str) -> float:
    row = frame.iloc[idx]
    if setup == 'ema_psar_long':
        return float(row['ema9'])
    if setup == 'fib_retest_long':
        return float(row['fib_50'])
    if setup == 'breakout_short':
        return float(row['rolling_low20'])
    raise ValueError(setup)


def setup_direction(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def session_key(ts: pd.Timestamp) -> str:
    bucket = ts.floor(f'{SESSION_HOURS}h')
    return bucket.strftime('%Y-%m-%dT%H:%M:%SZ')


def build_candidates(frame: pd.DataFrame) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    asset = str(frame.iloc[0]['asset'])
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        row = frame.iloc[idx]
        for setup in SETUPS:
            if not bool(row[f'{setup}_signal']):
                continue
            direction = setup_direction(setup)
            entry_idx = idx + 1
            exit_idx = entry_idx + HOLD_BARS
            if exit_idx >= len(frame):
                continue
            entry_px = float(frame.iloc[entry_idx]['open'])
            exit_px = float(frame.iloc[exit_idx]['open'])
            gross_ret = direction * (exit_px / entry_px - 1.0)
            lvl = trigger_level(frame, idx, setup)
            path = frame.iloc[entry_idx: entry_idx + EARLY_FAIL_BARS + 1]
            if direction == 1:
                flip_fail = bool((path['close'] < lvl).any())
                early_move = direction * (float(path.iloc[-1]['close']) / entry_px - 1.0)
                mae = float((path['low'] / entry_px - 1.0).min())
            else:
                flip_fail = bool((path['close'] > lvl).any())
                early_move = direction * (float(path.iloc[-1]['close']) / entry_px - 1.0)
                mae = float((1.0 - path['high'] / entry_px).min())
            early_pass = (not flip_fail) and (early_move > 0)
            ts = pd.to_datetime(row['timestamp'], utc=True)
            events.append(
                {
                    'asset': asset,
                    'setup': setup,
                    'idx': idx,
                    'signal_ts': ts,
                    'session_key': session_key(ts),
                    'entry_idx': entry_idx,
                    'exit_idx': exit_idx,
                    'entry_ts': pd.to_datetime(frame.iloc[entry_idx]['timestamp'], utc=True),
                    'exit_ts': pd.to_datetime(frame.iloc[exit_idx]['timestamp'], utc=True),
                    'direction': direction,
                    'entry_price': entry_px,
                    'exit_price': exit_px,
                    'gross_ret': gross_ret,
                    'flip_to_fail_3bars': int(flip_fail),
                    'early_pass': int(early_pass),
                    'mae_3bars': mae,
                }
            )
    events.sort(key=lambda x: (x['signal_ts'], x['setup']))
    return events


def variant_size(variant: str, fail_count: int, pass_count: int) -> float:
    if variant == 'baseline':
        return 1.0
    if variant == 'fail2_halfsize':
        return 0.5 if fail_count >= 2 and pass_count == 0 else 1.0
    if variant == 'fail2_veto':
        return 0.0 if fail_count >= 2 and pass_count == 0 else 1.0
    if variant == 'fail3_veto':
        return 0.0 if fail_count >= 3 and pass_count == 0 else 1.0
    raise ValueError(variant)


def simulate(events_by_asset: dict[str, list[dict[str, object]]], cost_bps: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    cost_rate = float(cost_bps) / 10000.0
    trade_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for variant in VARIANTS:
        for asset, events in events_by_asset.items():
            last_exit_by_setup = {setup: -1 for setup in SETUPS}
            raw_counts = defaultdict(int)
            blocked_counts = defaultdict(int)
            session_state: dict[str, dict[str, int]] = defaultdict(lambda: {'fail': 0, 'pass': 0})
            accepted: dict[str, list[dict[str, object]]] = defaultdict(list)

            for ev in events:
                setup = str(ev['setup'])
                idx = int(ev['idx'])
                if idx <= last_exit_by_setup[setup]:
                    continue
                raw_counts[setup] += 1
                st = session_state[str(ev['session_key'])]
                size = variant_size(variant, st['fail'], st['pass'])
                if size <= 0:
                    blocked_counts[setup] += 1
                    continue
                gross_ret = float(ev['gross_ret']) * size
                net_ret = gross_ret - 2.0 * cost_rate * size
                row = dict(ev)
                row.update(
                    {
                        'variant': variant,
                        'cost_bps_per_side': float(cost_bps),
                        'size': size,
                        'net_ret': net_ret,
                        'prior_session_fail_count': st['fail'],
                        'prior_session_pass_count': st['pass'],
                    }
                )
                accepted[setup].append(row)
                trade_rows.append(row)
                last_exit_by_setup[setup] = int(ev['exit_idx'])
                if int(ev['flip_to_fail_3bars']) == 1:
                    st['fail'] += 1
                elif int(ev['early_pass']) == 1:
                    st['pass'] += 1

            for setup in SETUPS:
                trades = pd.DataFrame(accepted[setup])
                raw = int(raw_counts[setup])
                blocked = int(blocked_counts[setup])
                summary_rows.append(
                    {
                        'asset': asset,
                        'setup': setup,
                        'variant': variant,
                        'cost_bps_per_side': float(cost_bps),
                        'raw_signal_count': raw,
                        'blocked_signals': blocked,
                        'blocked_ratio': (blocked / raw) if raw else np.nan,
                        'trades': int(len(trades)),
                        'trade_count_retention': (len(trades) / raw) if raw else np.nan,
                        'total_return': float((1.0 + trades['net_ret']).prod() - 1.0) if not trades.empty else 0.0,
                        'avg_net_ret': float(trades['net_ret'].mean()) if not trades.empty else np.nan,
                        'flip_to_fail_3bars_rate': float(trades['flip_to_fail_3bars'].mean()) if not trades.empty else np.nan,
                        'mean_mae_3bars': float(trades['mae_3bars'].mean()) if not trades.empty else np.nan,
                        'mean_size': float(trades['size'].mean()) if not trades.empty else np.nan,
                    }
                )

    return pd.DataFrame(trade_rows), pd.DataFrame(summary_rows)


def aggregate(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    by_setup_rows = []
    for (variant, cost), grp in summary.groupby(['variant', 'cost_bps_per_side'], sort=False):
        overall_rows.append(
            {
                'variant': variant,
                'cost_bps_per_side': float(cost),
                'mean_total_return': float(grp['total_return'].mean()),
                'positive_cell_ratio': float((grp['total_return'] > 0).mean()),
                'mean_trades': float(grp['trades'].mean()),
                'mean_trade_count_retention': float(grp['trade_count_retention'].mean()),
                'mean_avg_net_ret': float(grp['avg_net_ret'].mean()),
                'mean_flip_to_fail_3bars_rate': float(grp['flip_to_fail_3bars_rate'].mean()),
                'mean_blocked_ratio': float(grp['blocked_ratio'].mean()),
                'mean_size': float(grp['mean_size'].mean()),
            }
        )
    for (setup, variant, cost), grp in summary.groupby(['setup', 'variant', 'cost_bps_per_side'], sort=False):
        by_setup_rows.append(
            {
                'setup': setup,
                'variant': variant,
                'cost_bps_per_side': float(cost),
                'mean_total_return': float(grp['total_return'].mean()),
                'positive_asset_ratio': float((grp['total_return'] > 0).mean()),
                'mean_trades': float(grp['trades'].mean()),
                'mean_trade_count_retention': float(grp['trade_count_retention'].mean()),
                'mean_avg_net_ret': float(grp['avg_net_ret'].mean()),
                'mean_flip_to_fail_3bars_rate': float(grp['flip_to_fail_3bars_rate'].mean()),
                'mean_blocked_ratio': float(grp['blocked_ratio'].mean()),
                'mean_size': float(grp['mean_size'].mean()),
            }
        )
    return pd.DataFrame(overall_rows), pd.DataFrame(by_setup_rows)


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return '-'
    return f'{100 * float(x):.2f}%'


def main() -> None:
    events_by_asset = {}
    candidate_rows = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        events = build_candidates(frame)
        events_by_asset[asset] = events
        for ev in events:
            candidate_rows.append({k: v for k, v in ev.items() if k not in {'signal_ts', 'entry_ts', 'exit_ts'}} | {
                'signal_ts': ev['signal_ts'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                'entry_ts': ev['entry_ts'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                'exit_ts': ev['exit_ts'].strftime('%Y-%m-%dT%H:%M:%SZ'),
            })

    trades_all = []
    summaries_all = []
    for cost in COSTS:
        trades, summary = simulate(events_by_asset, cost)
        trades_all.append(trades)
        summaries_all.append(summary)
    trades = pd.concat(trades_all, ignore_index=True)
    summary = pd.concat(summaries_all, ignore_index=True)
    overall, by_setup = aggregate(summary)

    candidate_path = ART_DIR / 'candidate_events.csv'
    trades_path = ART_DIR / 'trade_log.csv'
    summary_path = ART_DIR / 'asset_summary.csv'
    overall_path = ART_DIR / 'overall_summary.csv'
    by_setup_path = ART_DIR / 'by_setup_summary.csv'
    json_path = ART_DIR / 'summary_snapshot.json'

    pd.DataFrame(candidate_rows).to_csv(candidate_path, index=False)
    trades.assign(
        signal_ts=trades['signal_ts'].dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        entry_ts=trades['entry_ts'].dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
        exit_ts=trades['exit_ts'].dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
    ).to_csv(trades_path, index=False)
    summary.to_csv(summary_path, index=False)
    overall.to_csv(overall_path, index=False)
    by_setup.to_csv(by_setup_path, index=False)

    primary = overall[overall['cost_bps_per_side'] == PRIMARY_COST].copy()
    base = primary[primary['variant'] == 'baseline'].iloc[0]
    fail2h = primary[primary['variant'] == 'fail2_halfsize'].iloc[0]
    fail2v = primary[primary['variant'] == 'fail2_veto'].iloc[0]
    fail3v = primary[primary['variant'] == 'fail3_veto'].iloc[0]

    snapshot = {
        'session_hours': SESSION_HOURS,
        'cost_bps_per_side': PRIMARY_COST,
        'overall': {
            'baseline': base.to_dict(),
            'fail2_halfsize': fail2h.to_dict(),
            'fail2_veto': fail2v.to_dict(),
            'fail3_veto': fail3v.to_dict(),
        },
        'primary_takeaway': {
            'baseline_mean_total_return': pct(base['mean_total_return']),
            'fail2_halfsize_mean_total_return': pct(fail2h['mean_total_return']),
            'fail2_veto_mean_total_return': pct(fail2v['mean_total_return']),
            'fail3_veto_mean_total_return': pct(fail3v['mean_total_return']),
            'baseline_flip_to_fail': pct(base['mean_flip_to_fail_3bars_rate']),
            'fail2_halfsize_flip_to_fail': pct(fail2h['mean_flip_to_fail_3bars_rate']),
            'fail2_veto_flip_to_fail': pct(fail2v['mean_flip_to_fail_3bars_rate']),
            'fail3_veto_flip_to_fail': pct(fail3v['mean_flip_to_fail_3bars_rate']),
            'baseline_retention': pct(base['mean_trade_count_retention']),
            'fail2_halfsize_retention': pct(fail2h['mean_trade_count_retention']),
            'fail2_veto_retention': pct(fail2v['mean_trade_count_retention']),
            'fail3_veto_retention': pct(fail3v['mean_trade_count_retention']),
        },
        'files': {
            'candidate_events': str(candidate_path.relative_to(ROOT)),
            'trade_log': str(trades_path.relative_to(ROOT)),
            'asset_summary': str(summary_path.relative_to(ROOT)),
            'overall_summary': str(overall_path.relative_to(ROOT)),
            'by_setup_summary': str(by_setup_path.relative_to(ROOT)),
        },
    }
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
