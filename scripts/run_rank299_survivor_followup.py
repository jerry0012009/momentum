#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'reports' / 'artifacts' / 'rank299_survivor_followup'
ART.mkdir(parents=True, exist_ok=True)

DATASETS = {
    '15m': ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m' / 'perp_cache' / 'BTCUSDT__120d__15m__perp.csv',
    '5m': ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m' / 'exec_cache' / 'BTCUSDT__120d__5m__perp.csv',
}

COSTS = [6.0, 10.0]
HOLDS = [1, 2, 4]
VARIANTS = ['baseline', 'gate7', 'gate7_psar', 'gate9', 'gate9_psar']


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - (100 / (1 + rs))
    out = out.fillna(50.0)
    return out


def psar(df: pd.DataFrame, af_step: float = 0.02, af_max: float = 0.2) -> pd.Series:
    high = df['high'].to_numpy(float)
    low = df['low'].to_numpy(float)
    close = df['close'].to_numpy(float)
    n = len(df)
    out = np.full(n, np.nan)
    if n < 3:
        return pd.Series(out, index=df.index)
    bull = True if close[1] >= close[0] else False
    sar = low[0] if bull else high[0]
    ep = max(high[0], high[1]) if bull else min(low[0], low[1])
    af = af_step
    out[0] = sar
    out[1] = sar
    for i in range(2, n):
        sar = sar + af * (ep - sar)
        if bull:
            sar = min(sar, low[i-1], low[i-2])
            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = af_step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + af_step, af_max)
        else:
            sar = max(sar, high[i-1], high[i-2])
            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = af_step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + af_step, af_max)
        out[i] = sar
    return pd.Series(out, index=df.index)


def load_bars(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x['ema9'] = x['close'].ewm(span=9, adjust=False).mean()
    x['ema20'] = x['close'].ewm(span=20, adjust=False).mean()
    x['rsi14'] = rsi(x['close'], 14)
    x['rsi_ema7'] = x['rsi14'].ewm(span=7, adjust=False).mean()
    x['rsi_ema9'] = x['rsi14'].ewm(span=9, adjust=False).mean()
    x['psar'] = psar(x)
    x['cross_up'] = (x['ema9'] > x['ema20']) & (x['ema9'].shift(1) <= x['ema20'].shift(1))
    x['psar_bull'] = x['close'] > x['psar']
    return x


def signal_mask(x: pd.DataFrame, variant: str) -> pd.Series:
    gate7 = x['rsi_ema7'] > 60
    gate9 = x['rsi_ema9'] > 60
    trend_on = x['ema9'] > x['ema20']
    psar_bull = x['psar_bull']
    if variant == 'baseline':
        raw = trend_on
    elif variant == 'gate7':
        raw = trend_on & gate7
    elif variant == 'gate7_psar':
        raw = trend_on & gate7 & psar_bull
    elif variant == 'gate9':
        raw = trend_on & gate9
    elif variant == 'gate9_psar':
        raw = trend_on & gate9 & psar_bull
    else:
        raise ValueError(variant)
    return raw & (~raw.shift(1).fillna(False))


def backtest(x: pd.DataFrame, variant: str, hold: int, cost_bps_side: float) -> dict:
    sig = signal_mask(x, variant)
    rets = []
    gross_rets = []
    rows = []
    for idx in np.where(sig.to_numpy())[0]:
        exit_idx = idx + hold
        if exit_idx >= len(x):
            continue
        entry = float(x.at[idx, 'close'])
        exitp = float(x.at[exit_idx, 'close'])
        gross = exitp / entry - 1.0
        net = gross - 2 * cost_bps_side / 10000.0
        gross_rets.append(gross)
        rets.append(net)
        rows.append({
            'timestamp': x.at[idx, 'timestamp'].isoformat(),
            'variant': variant,
            'hold_bars': hold,
            'gross_ret': gross,
            'net_ret': net,
            'rsi_ema7': float(x.at[idx, 'rsi_ema7']),
            'rsi_ema9': float(x.at[idx, 'rsi_ema9']),
        })
    arr = np.array(rets, dtype=float)
    gross_arr = np.array(gross_rets, dtype=float)
    total_net = float(np.prod(1 + arr) - 1) if len(arr) else 0.0
    total_gross = float(np.prod(1 + gross_arr) - 1) if len(gross_arr) else 0.0
    return {
        'variant': variant,
        'hold_bars': hold,
        'cost_bps_side': cost_bps_side,
        'trades': int(len(arr)),
        'win_rate': float((arr > 0).mean()) if len(arr) else math.nan,
        'avg_net_ret': float(arr.mean()) if len(arr) else math.nan,
        'avg_gross_ret': float(gross_arr.mean()) if len(gross_arr) else math.nan,
        'total_net_return': total_net,
        'total_gross_return': total_gross,
        'trade_cut_ratio_vs_baseline': math.nan,
        'rows': rows,
    }


def main() -> None:
    all_summary = []
    all_trades = []
    for tf, path in DATASETS.items():
        x = build_features(load_bars(path))
        baseline_counts = {hold: int(backtest(x, 'baseline', hold, COSTS[0])['trades']) for hold in HOLDS}
        for cost in COSTS:
            for hold in HOLDS:
                for variant in VARIANTS:
                    res = backtest(x, variant, hold, cost)
                    base_trades = baseline_counts[hold] or 1
                    res['trade_cut_ratio_vs_baseline'] = 1.0 - res['trades'] / base_trades
                    res['timeframe'] = tf
                    all_trades.extend([{**r, 'timeframe': tf, 'cost_bps_side': cost} for r in res.pop('rows')])
                    all_summary.append(res)
    summary = pd.DataFrame(all_summary)
    trades = pd.DataFrame(all_trades)
    summary.to_csv(ART / 'summary.csv', index=False)
    trades.to_csv(ART / 'trades.csv', index=False)

    focus = summary[(summary['cost_bps_side'] == 6.0) & (summary['hold_bars'].isin([1, 2, 4]))].copy()
    verdict = {
        'generated_at_utc': pd.Timestamp.utcnow().isoformat(),
        'best_15m': focus[focus['timeframe'] == '15m'].sort_values('avg_net_ret', ascending=False).head(5).to_dict(orient='records'),
        'best_5m': focus[focus['timeframe'] == '5m'].sort_values('avg_net_ret', ascending=False).head(5).to_dict(orient='records'),
    }
    (ART / 'verdict.json').write_text(json.dumps(verdict, indent=2), encoding='utf-8')
    print(ART / 'summary.csv')


if __name__ == '__main__':
    main()
