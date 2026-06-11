#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

ROOT = Path('/root/clawd/jerry/momentum')
OUT_DIR = ROOT / 'reports' / 'artifacts' / 'cross_market_clock_scan'
BTC_15M_PATH = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m' / 'perp_cache' / 'BTCUSDT__1825d__15m__perp.csv'

ASSETS = [
    {'symbol': 'QQQ', 'label': 'US tech ETF', 'group': 'us'},
    {'symbol': 'SPY', 'label': 'US broad ETF', 'group': 'us'},
    {'symbol': 'GLD', 'label': 'Gold ETF', 'group': 'gold'},
    {'symbol': 'GC=F', 'label': 'Gold futures', 'group': 'gold'},
    {'symbol': '2800.HK', 'label': 'HK broad ETF', 'group': 'hk'},
    {'symbol': '3033.HK', 'label': 'HK tech ETF', 'group': 'hk'},
    {'symbol': '0700.HK', 'label': 'Tencent', 'group': 'hk'},
]

YAHOO_HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://finance.yahoo.com/',
}


@dataclass
class SlotChoice:
    slot: str
    train_mean: float
    test_total: float
    test_max_dd: float
    positive_months: int
    total_months: int


def compounded_return(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float((1.0 + series).prod() - 1.0)


def max_drawdown_from_returns(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    equity = (1.0 + returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def fetch_yahoo_60m(symbol: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}'
    resp = requests.get(
        url,
        params={
            'range': '730d',
            'interval': '60m',
            'includePrePost': 'false',
            'events': 'div,splits',
        },
        headers=YAHOO_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()['chart']
    if payload.get('error'):
        raise RuntimeError(payload['error'])
    result = payload['result'][0]
    meta = result['meta']
    quote = result['indicators']['quote'][0]
    adjclose = result['indicators'].get('adjclose', [{}])[0].get('adjclose')
    frame = pd.DataFrame(
        {
            'timestamp': pd.to_datetime(result['timestamp'], unit='s', utc=True),
            'open': quote.get('open'),
            'high': quote.get('high'),
            'low': quote.get('low'),
            'close': quote.get('close'),
            'volume': quote.get('volume'),
            'adjclose': adjclose if adjclose is not None else quote.get('close'),
        }
    )
    frame = frame.dropna(subset=['timestamp', 'open', 'close']).sort_values('timestamp').reset_index(drop=True)
    frame['symbol'] = symbol
    return frame, meta


def load_btc_daily() -> pd.DataFrame:
    df = pd.read_csv(BTC_15M_PATH, usecols=['timestamp', 'close'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['date'] = df['timestamp'].dt.floor('D')
    daily = df.groupby('date', as_index=False)['close'].last().rename(columns={'date': 'timestamp', 'close': 'btc_close'})
    daily['btc_ret_1d'] = daily['btc_close'].pct_change()
    return daily


def split_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    midpoint = df['timestamp'].min() + (df['timestamp'].max() - df['timestamp'].min()) / 2
    train = df[df['timestamp'] < midpoint].copy()
    test = df[df['timestamp'] >= midpoint].copy()
    return train, test


def choose_slots(train: pd.DataFrame) -> tuple[str, float, str, float]:
    slot_stats = train.groupby('slot_local')['bar_ret'].agg(['mean', 'count']).reset_index()
    slot_stats = slot_stats[slot_stats['count'] >= 80].copy()
    if slot_stats.empty:
        raise RuntimeError('no usable slots after min-count filter')
    best = slot_stats.sort_values('mean', ascending=False).iloc[0]
    worst = slot_stats.sort_values('mean', ascending=True).iloc[0]
    return str(best['slot_local']), float(best['mean']), str(worst['slot_local']), float(worst['mean'])


def evaluate_slot(test: pd.DataFrame, slot: str, side: str) -> SlotChoice:
    picked = test[test['slot_local'] == slot].copy().sort_values('timestamp')
    if side == 'long':
        picked['trade_ret'] = picked['bar_ret']
    elif side == 'short':
        picked['trade_ret'] = -picked['bar_ret']
    else:
        raise ValueError(side)
    picked['month'] = picked['timestamp'].dt.tz_localize(None).dt.to_period('M').astype(str)
    monthly = picked.groupby('month')['trade_ret'].apply(compounded_return)
    return SlotChoice(
        slot=slot,
        train_mean=0.0,
        test_total=compounded_return(picked['trade_ret']),
        test_max_dd=max_drawdown_from_returns(picked['trade_ret']),
        positive_months=int((monthly > 0).sum()),
        total_months=int(len(monthly)),
    )


def analyze_asset(asset: dict[str, str], btc_daily: pd.DataFrame) -> dict[str, Any]:
    bars, meta = fetch_yahoo_60m(asset['symbol'])
    local_ts = bars['timestamp'].dt.tz_convert(meta['exchangeTimezoneName'])
    bars['slot_local'] = local_ts.dt.strftime('%H:%M')
    bars['trade_date_local'] = local_ts.dt.strftime('%Y-%m-%d')
    bars['bar_ret'] = bars['adjclose'] / bars['open'] - 1.0
    train, test = split_train_test(bars)
    best_slot, best_mean, worst_slot, worst_mean = choose_slots(train)

    long_eval = evaluate_slot(test, best_slot, 'long')
    long_eval.train_mean = best_mean
    short_eval = evaluate_slot(test, worst_slot, 'short')
    short_eval.train_mean = worst_mean

    test['month'] = test['timestamp'].dt.tz_localize(None).dt.to_period('M').astype(str)
    combined = test[test['slot_local'].isin([best_slot, worst_slot])].copy().sort_values('timestamp')
    combined['trade_ret'] = combined['bar_ret']
    combined.loc[combined['slot_local'] == worst_slot, 'trade_ret'] *= -1.0
    combined_monthly = combined.groupby('month')['trade_ret'].apply(compounded_return)

    daily = bars.copy()
    daily['date'] = daily['timestamp'].dt.floor('D')
    daily_close = daily.groupby('date', as_index=False)['adjclose'].last().rename(columns={'date': 'timestamp', 'adjclose': 'asset_close'})
    daily_close['asset_ret_1d'] = daily_close['asset_close'].pct_change()
    merged = daily_close.merge(btc_daily, on='timestamp', how='inner').dropna()
    if len(merged) >= 80:
        merged['corr_60d'] = merged['asset_ret_1d'].rolling(60).corr(merged['btc_ret_1d'])
        latest_corr_60d = float(merged['corr_60d'].dropna().iloc[-1]) if merged['corr_60d'].dropna().shape[0] else None
        median_corr_60d = float(merged['corr_60d'].dropna().median()) if merged['corr_60d'].dropna().shape[0] else None
        full_corr = float(merged['asset_ret_1d'].corr(merged['btc_ret_1d']))
    else:
        latest_corr_60d = None
        median_corr_60d = None
        full_corr = None

    slot_table = (
        bars.groupby('slot_local')['bar_ret']
        .agg(mean_ret='mean', obs='count')
        .reset_index()
        .sort_values('slot_local')
    )
    slot_table.to_csv(OUT_DIR / f"{asset['symbol'].replace('=','_').replace('.','_')}_slot_table.csv", index=False)

    test_slot_table = (
        test.groupby('slot_local')['bar_ret']
        .agg(mean_ret='mean', obs='count')
        .reset_index()
        .sort_values('slot_local')
    )
    test_slot_table.to_csv(OUT_DIR / f"{asset['symbol'].replace('=','_').replace('.','_')}_test_slot_table.csv", index=False)

    return {
        'symbol': asset['symbol'],
        'label': asset['label'],
        'group': asset['group'],
        'timezone': meta.get('exchangeTimezoneName'),
        'rows': int(len(bars)),
        'train_start_utc': train['timestamp'].min().isoformat(),
        'train_end_utc': train['timestamp'].max().isoformat(),
        'test_start_utc': test['timestamp'].min().isoformat(),
        'test_end_utc': test['timestamp'].max().isoformat(),
        'best_long_slot_local': best_slot,
        'best_long_train_mean_bps': best_mean * 10000.0,
        'best_long_test_total_return': long_eval.test_total,
        'best_long_test_max_drawdown': long_eval.test_max_dd,
        'best_long_positive_months': long_eval.positive_months,
        'best_long_total_months': long_eval.total_months,
        'worst_short_slot_local': worst_slot,
        'worst_short_train_mean_bps': worst_mean * 10000.0,
        'worst_short_test_total_return': short_eval.test_total,
        'worst_short_test_max_drawdown': short_eval.test_max_dd,
        'worst_short_positive_months': short_eval.positive_months,
        'worst_short_total_months': short_eval.total_months,
        'combined_test_total_return': compounded_return(combined['trade_ret']),
        'combined_test_max_drawdown': max_drawdown_from_returns(combined['trade_ret']),
        'combined_positive_months': int((combined_monthly > 0).sum()),
        'combined_total_months': int(len(combined_monthly)),
        'btc_daily_corr_full': full_corr,
        'btc_daily_corr_60d_median': median_corr_60d,
        'btc_daily_corr_60d_latest': latest_corr_60d,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    btc_daily = load_btc_daily()
    results = [analyze_asset(asset, btc_daily) for asset in ASSETS]
    summary = pd.DataFrame(results).sort_values(['group', 'symbol']).reset_index(drop=True)
    summary.to_csv(OUT_DIR / 'cross_market_clock_summary.csv', index=False)
    (OUT_DIR / 'cross_market_clock_summary.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    print(summary.to_string(index=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
