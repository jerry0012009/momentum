#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / 'reports' / 'artifacts' / 'scout_tau_band_breakout_15m' / 'cache'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'quant_digests' / 'vajra_controlled_pullback_proxy'
ART_DIR.mkdir(parents=True, exist_ok=True)

ASSETS = {
    'BTC-USD': 'BTCUSDT',
    'ETH-USD': 'ETHUSDT',
    'SOL-USD': 'SOLUSDT',
}
VARIANTS = ['baseline', 'depth15', 'depth15_touch_green', 'repo_branch']
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
ATR_PERIOD = 14
VOL_PERIOD = 20
ADX_PERIOD = 14
PULLBACK_LOOKBACK = 5
PULLBACK_MAX_PCT = 1.5


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


def compute_adx(df: pd.DataFrame, period: int = ADX_PERIOD) -> pd.Series:
    high = df['high']
    low = df['low']
    close = df['close']
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr_rma = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_rma
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr_rma
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema15'] = df['close'].ewm(span=15, adjust=False).mean()
    df['ema_slope'] = df['ema9'].pct_change(3)
    df['ema_angle_deg'] = np.degrees(np.arctan(df['ema9'].diff().fillna(0.0)))
    df['vol_ma20'] = df['volume'].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df['atr14'] = atr(df)
    df['adx14'] = compute_adx(df)
    df['psar'] = compute_psar(df)
    df['highest_recent'] = df['high'].rolling(PULLBACK_LOOKBACK, min_periods=PULLBACK_LOOKBACK).max()
    df['pullback_depth_pct'] = ((df['highest_recent'] - df['close']) / df['highest_recent']) * 100.0
    df['controlled_pullback'] = df['pullback_depth_pct'] <= PULLBACK_MAX_PCT
    df['near_ema_touch'] = (df['low'] <= df['ema9']) | (df['low'] <= df['ema15'])
    df['green_candle'] = df['close'] > df['open']
    df['vol_spike_12'] = df['volume'] > 1.2 * df['vol_ma20']
    df['ema_psar_long_signal'] = (
        (df['ema9'] > df['ema15'])
        & (df['ema_slope'] > 0.0003)
        & (df['psar'] < df['close'])
        & (df['close'] > df['high'].shift(1))
        & (df['close'].shift(1) < df['ema9'].shift(1))
        & (df['volume'] > df['vol_ma20'])
    ).fillna(False)
    return df


def passes_variant(row: pd.Series, variant: str) -> bool:
    if variant == 'baseline':
        return bool(row['ema_psar_long_signal'])
    if variant == 'depth15':
        return bool(row['ema_psar_long_signal'] and row['controlled_pullback'])
    if variant == 'depth15_touch_green':
        return bool(row['ema_psar_long_signal'] and row['controlled_pullback'] and row['near_ema_touch'] and row['green_candle'])
    if variant == 'repo_branch':
        return bool(
            row['ema_psar_long_signal']
            and row['controlled_pullback']
            and row['near_ema_touch']
            and row['green_candle']
            and row['vol_spike_12']
            and (row['adx14'] >= 25.0)
        )
    raise ValueError(variant)


def build_candidates(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    asset = str(frame.iloc[0]['asset'])
    for idx in range(40, len(frame) - HOLD_BARS - 2):
        row = frame.iloc[idx]
        if not bool(row['ema_psar_long_signal']):
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        entry_px = float(frame.iloc[entry_idx]['open'])
        exit_px = float(frame.iloc[exit_idx]['open'])
        path = frame.iloc[entry_idx: entry_idx + 4]
        lvl = float(row['ema9'])
        rows.append(
            {
                'asset': asset,
                'idx': idx,
                'signal_ts': pd.to_datetime(row['timestamp'], utc=True),
                'entry_ts': pd.to_datetime(frame.iloc[entry_idx]['timestamp'], utc=True),
                'exit_ts': pd.to_datetime(frame.iloc[exit_idx]['timestamp'], utc=True),
                'entry_price': entry_px,
                'exit_price': exit_px,
                'gross_ret': float(exit_px / entry_px - 1.0),
                'flip_to_fail_3bars': int((path['close'] < lvl).any()),
                'fwd3_ret': float(path.iloc[-1]['close'] / entry_px - 1.0) if len(path) >= 4 else np.nan,
                'pullback_depth_pct': float(row['pullback_depth_pct']) if pd.notna(row['pullback_depth_pct']) else np.nan,
                'near_ema_touch': int(bool(row['near_ema_touch'])),
                'green_candle': int(bool(row['green_candle'])),
                'vol_spike_12': int(bool(row['vol_spike_12'])),
                'adx14': float(row['adx14']) if pd.notna(row['adx14']) else np.nan,
                'ema_angle_deg': float(row['ema_angle_deg']) if pd.notna(row['ema_angle_deg']) else np.nan,
                'controlled_pullback': int(bool(row['controlled_pullback'])),
            }
        )
    out = pd.DataFrame(rows)
    out.sort_values(['asset', 'signal_ts'], inplace=True)
    return out


def simulate(frame_by_asset: dict[str, pd.DataFrame], candidates: pd.DataFrame, cost_bps: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    trade_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    cost_rate = cost_bps / 10000.0

    for variant in VARIANTS:
        for asset, frame in frame_by_asset.items():
            last_exit_idx = -1
            raw = 0
            trades = []
            asset_candidates = candidates[candidates['asset'] == asset]
            for _, c in asset_candidates.iterrows():
                idx = int(c['idx'])
                row = frame.iloc[idx]
                if not passes_variant(row, variant):
                    continue
                raw += 1
                entry_idx = idx + 1
                exit_idx = entry_idx + HOLD_BARS
                if idx <= last_exit_idx or exit_idx >= len(frame):
                    continue
                last_exit_idx = exit_idx
                gross_ret = float(c['gross_ret'])
                net_ret = gross_ret - 2.0 * cost_rate
                trade = {
                    **c.to_dict(),
                    'variant': variant,
                    'cost_bps_per_side': cost_bps,
                    'net_ret': net_ret,
                    'mae_8bar': float((frame.iloc[entry_idx: exit_idx + 1]['low'] / c['entry_price'] - 1.0).min()),
                    'mfe_8bar': float((frame.iloc[entry_idx: exit_idx + 1]['high'] / c['entry_price'] - 1.0).max()),
                }
                trades.append(trade)
                trade_rows.append(trade)
            trade_df = pd.DataFrame(trades)
            summary_rows.append(
                {
                    'variant': variant,
                    'asset': asset,
                    'cost_bps_per_side': cost_bps,
                    'raw_signal_count': int(raw),
                    'trade_count': int(len(trade_df)),
                    'mean_total_return': float(trade_df['net_ret'].sum()) if not trade_df.empty else 0.0,
                    'mean_trade_return': float(trade_df['net_ret'].mean()) if not trade_df.empty else 0.0,
                    'win_rate': float((trade_df['net_ret'] > 0).mean()) if not trade_df.empty else 0.0,
                    'flip_to_fail_3bars_rate': float(trade_df['flip_to_fail_3bars'].mean()) if not trade_df.empty else 0.0,
                    'median_fwd3_ret': float(trade_df['fwd3_ret'].median()) if not trade_df.empty else 0.0,
                    'median_pullback_depth_pct': float(trade_df['pullback_depth_pct'].median()) if not trade_df.empty else 0.0,
                    'median_adx14': float(trade_df['adx14'].median()) if not trade_df.empty else 0.0,
                }
            )
    trades = pd.DataFrame(trade_rows)
    summary = pd.DataFrame(summary_rows)
    base = summary[(summary['variant'] == 'baseline')][['asset', 'cost_bps_per_side', 'trade_count']].rename(columns={'trade_count': 'baseline_trade_count'})
    summary = summary.merge(base, on=['asset', 'cost_bps_per_side'], how='left')
    summary['trade_count_retention'] = np.where(summary['baseline_trade_count'] > 0, summary['trade_count'] / summary['baseline_trade_count'], np.nan)
    return trades, summary


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), grp in asset_summary.groupby(['variant', 'cost_bps_per_side']):
        rows.append(
            {
                'variant': variant,
                'cost_bps_per_side': cost_bps,
                'mean_total_return': float(grp['mean_total_return'].mean()),
                'positive_asset_ratio': float((grp['mean_total_return'] > 0).mean()),
                'mean_trade_return': float(grp['mean_trade_return'].mean()),
                'mean_win_rate': float(grp['win_rate'].mean()),
                'mean_flip_to_fail_3bars_rate': float(grp['flip_to_fail_3bars_rate'].mean()),
                'mean_trade_count_retention': float(grp['trade_count_retention'].mean()),
                'mean_trade_count': float(grp['trade_count'].mean()),
                'median_pullback_depth_pct': float(grp['median_pullback_depth_pct'].mean()),
                'median_adx14': float(grp['median_adx14'].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(['cost_bps_per_side', 'variant']).reset_index(drop=True)


def build_depth_threshold_sweep(candidates: pd.DataFrame, cost_bps: float = PRIMARY_COST) -> pd.DataFrame:
    thresholds = [0.10, 0.15, 0.20, 0.25, 0.30, 0.50, 0.75, 1.00, 1.50]
    baseline_mean_count = candidates.groupby('asset').size().mean()
    rows = []
    cost_rate = cost_bps / 10000.0
    for thr in thresholds:
        per_asset = []
        for asset, grp in candidates.groupby('asset'):
            grp = grp.sort_values('signal_ts')
            last_exit_idx = -1
            accepted = []
            for _, row in grp.iterrows():
                if row['pullback_depth_pct'] > thr:
                    continue
                idx = int(row['idx'])
                if idx <= last_exit_idx:
                    continue
                last_exit_idx = idx + 1 + HOLD_BARS
                accepted.append(row)
            accepted_df = pd.DataFrame(accepted)
            if accepted_df.empty:
                per_asset.append(
                    {
                        'trade_count': 0,
                        'mean_total_return': 0.0,
                        'win_rate': 0.0,
                        'flip_to_fail_3bars_rate': 0.0,
                    }
                )
                continue
            net = accepted_df['gross_ret'] - 2.0 * cost_rate
            per_asset.append(
                {
                    'trade_count': int(len(accepted_df)),
                    'mean_total_return': float(net.sum()),
                    'win_rate': float((net > 0).mean()),
                    'flip_to_fail_3bars_rate': float(accepted_df['flip_to_fail_3bars'].mean()),
                }
            )
        frame = pd.DataFrame(per_asset)
        rows.append(
            {
                'pullback_depth_threshold_pct': thr,
                'cost_bps_per_side': cost_bps,
                'mean_total_return': float(frame['mean_total_return'].mean()),
                'mean_trade_count': float(frame['trade_count'].mean()),
                'mean_trade_count_retention': float(frame['trade_count'].mean() / baseline_mean_count),
                'mean_win_rate': float(frame['win_rate'].mean()),
                'mean_flip_to_fail_3bars_rate': float(frame['flip_to_fail_3bars_rate'].mean()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    candidates = pd.concat([build_candidates(frame) for frame in frames.values()], ignore_index=True)
    candidates.to_csv(ART_DIR / 'candidate_events.csv', index=False)

    asset_summaries = []
    overall_summaries = []
    trade_logs = []
    for cost in COSTS:
        trades, asset_summary = simulate(frames, candidates, cost)
        overall = build_overall(asset_summary)
        asset_summaries.append(asset_summary)
        overall_summaries.append(overall)
        trade_logs.append(trades)

    asset_summary = pd.concat(asset_summaries, ignore_index=True)
    overall_summary = pd.concat(overall_summaries, ignore_index=True)
    trade_log = pd.concat(trade_logs, ignore_index=True)

    depth_threshold_sweep = build_depth_threshold_sweep(candidates, PRIMARY_COST)

    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall_summary.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    trade_log.to_csv(ART_DIR / 'trade_log.csv', index=False)
    depth_threshold_sweep.to_csv(ART_DIR / 'depth_threshold_sweep.csv', index=False)

    snapshot = {
        'generated_at': pd.Timestamp.utcnow().isoformat(),
        'primary_cost_bps_per_side': PRIMARY_COST,
        'pullback_lookback_bars': PULLBACK_LOOKBACK,
        'pullback_max_pct': PULLBACK_MAX_PCT,
        'hold_bars': HOLD_BARS,
        'overall_primary': overall_summary[overall_summary['cost_bps_per_side'] == PRIMARY_COST].to_dict(orient='records'),
        'depth_threshold_sweep_primary': depth_threshold_sweep.to_dict(orient='records'),
    }
    (ART_DIR / 'summary_snapshot.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')

    print('Wrote artifacts to', ART_DIR)
    print('\nPrimary cost summary:')
    print(overall_summary[overall_summary['cost_bps_per_side'] == PRIMARY_COST].to_string(index=False))


if __name__ == '__main__':
    main()
