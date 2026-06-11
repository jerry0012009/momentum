import json, math, os, time
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from statsmodels.tsa.stattools import coint

BASE = Path('/root/clawd/jerry/momentum')
OUTDIR = BASE / 'reports/artifacts/quant_digests/ghe_pairs_selection_20260404_0218'
OUTDIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','LINKUSDT','AVAXUSDT','LTCUSDT','DOTUSDT','TRXUSDT']
INTERVAL = '15m'
LIMIT = 1500  # ~15.6d
TRAIN_BARS = 960  # 10d
TEST_BARS = LIMIT - TRAIN_BARS
ENTRY_Z = 1.5
MAX_Z = 4.0
EXIT_Z = 0.25
TIME_STOP_BARS = 32  # 8h on 15m
COSTS_BPS = [8,12,16]
TOP_N = 6

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})


def fetch_klines(symbol, interval='15m', limit=1500):
    url = 'https://fapi.binance.com/fapi/v1/klines'
    r = session.get(url, params={'symbol': symbol, 'interval': interval, 'limit': limit}, timeout=30)
    r.raise_for_status()
    data = r.json()
    cols = ['open_time','open','high','low','close','volume','close_time','qav','trades','tbav','tqav','ignore']
    df = pd.DataFrame(data, columns=cols)
    for c in ['open','high','low','close','volume']:
        df[c] = df[c].astype(float)
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms', utc=True)
    return df[['open_time','close_time','close','volume']]


def generalized_hurst(series, q=1.0, max_lag=20):
    x = np.asarray(series, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) < max_lag + 5:
        return np.nan
    lags = np.arange(2, max_lag + 1)
    k = []
    for lag in lags:
        diff = np.abs(x[lag:] - x[:-lag]) ** q
        m = np.nanmean(diff)
        if not np.isfinite(m) or m <= 0:
            return np.nan
        k.append(m)
    slope = np.polyfit(np.log(lags), np.log(k), 1)[0]
    return float(slope / q)


def half_life(spread):
    s = pd.Series(spread).dropna()
    if len(s) < 10:
        return np.nan
    lag = s.shift(1).dropna()
    ret = (s - lag).dropna()
    lag = lag.loc[ret.index]
    X = np.vstack([np.ones(len(lag)), lag.values]).T
    beta = np.linalg.lstsq(X, ret.values, rcond=None)[0][1]
    if beta >= 0:
        return np.inf
    hl = -np.log(2) / beta
    return float(hl)


def fit_pair(px_a, px_b):
    x = np.log(px_b.values)
    y = np.log(px_a.values)
    X = np.vstack([np.ones(len(x)), x]).T
    alpha, beta = np.linalg.lstsq(X, y, rcond=None)[0]
    spread = y - (alpha + beta * x)
    return float(alpha), float(beta), spread


def zscore(x, mean, std):
    if std <= 0 or not np.isfinite(std):
        return np.nan
    return (x - mean) / std


def simulate_pair(test_df, alpha, beta, train_mean, train_std):
    px_a = np.log(test_df['a'].values)
    px_b = np.log(test_df['b'].values)
    spread = px_a - (alpha + beta * px_b)
    z = (spread - train_mean) / train_std
    pos = 0  # 1 long spread, -1 short spread
    entry_idx = None
    entry_a = entry_b = None
    trades = []
    for i in range(len(test_df)):
        zi = z[i]
        if not np.isfinite(zi):
            continue
        if pos == 0:
            if abs(zi) >= ENTRY_Z and abs(zi) <= MAX_Z:
                if zi > 0:
                    pos = -1  # short a long b
                elif zi < 0:
                    pos = 1   # long a short b
                if pos != 0:
                    entry_idx = i
                    entry_a = test_df['a'].iat[i]
                    entry_b = test_df['b'].iat[i]
        else:
            hold = i - entry_idx
            should_exit = (pos == 1 and zi >= -EXIT_Z) or (pos == -1 and zi <= EXIT_Z) or hold >= TIME_STOP_BARS or abs(zi) > MAX_Z * 1.25
            if should_exit:
                exit_a = test_df['a'].iat[i]
                exit_b = test_df['b'].iat[i]
                if pos == 1:
                    gross = (exit_a / entry_a - 1.0) - (exit_b / entry_b - 1.0)
                else:
                    gross = -(exit_a / entry_a - 1.0) + (exit_b / entry_b - 1.0)
                trades.append({
                    'entry_time': test_df['open_time'].iat[entry_idx].isoformat(),
                    'exit_time': test_df['open_time'].iat[i].isoformat(),
                    'side': 'long_spread' if pos == 1 else 'short_spread',
                    'hold_bars': hold,
                    'entry_z': float(z[entry_idx]),
                    'exit_z': float(zi),
                    'gross_ret': float(gross),
                })
                pos = 0
                entry_idx = None
                entry_a = entry_b = None
    return trades

print('fetching data...')
raw = {s: fetch_klines(s, INTERVAL, LIMIT) for s in SYMBOLS}
common_times = set(raw[SYMBOLS[0]]['open_time'])
for s in SYMBOLS[1:]:
    common_times &= set(raw[s]['open_time'])
common_times = sorted(common_times)
for s in SYMBOLS:
    raw[s] = raw[s][raw[s]['open_time'].isin(common_times)].sort_values('open_time').reset_index(drop=True)
min_len = min(len(df) for df in raw.values())
for s in SYMBOLS:
    raw[s] = raw[s].tail(min_len).reset_index(drop=True)
print('bars per symbol', min_len)

pair_rows = []
for a, b in combinations(SYMBOLS, 2):
    df = pd.DataFrame({
        'open_time': raw[a]['open_time'],
        'a': raw[a]['close'],
        'b': raw[b]['close'],
    }).dropna()
    train = df.iloc[:TRAIN_BARS].copy()
    test = df.iloc[TRAIN_BARS:].copy()
    alpha, beta, spread_train = fit_pair(train['a'], train['b'])
    spread_train = pd.Series(spread_train)
    train_mean = float(spread_train.mean())
    train_std = float(spread_train.std(ddof=0))
    a_norm = train['a'] / train['a'].iloc[0]
    b_norm = train['b'] / train['b'].iloc[0]
    distance = float(((a_norm - b_norm) ** 2).sum())
    corr = float(np.corrcoef(np.log(train['a']).diff().dropna(), np.log(train['b']).diff().dropna())[0,1])
    try:
        coint_p = float(coint(np.log(train['a']), np.log(train['b']))[1])
    except Exception:
        coint_p = np.nan
    ghe = generalized_hurst(spread_train.values, q=1.0, max_lag=24)
    hl = half_life(spread_train.values)
    trades = simulate_pair(test, alpha, beta, train_mean, train_std)
    gross_rets = [t['gross_ret'] for t in trades]
    pair_rows.append({
        'pair': f'{a}-{b}',
        'a': a,
        'b': b,
        'corr': corr,
        'distance': distance,
        'coint_p': coint_p,
        'ghe': ghe,
        'half_life_bars': hl,
        'n_trades': len(trades),
        'gross_mean_bps': (np.mean(gross_rets) * 1e4) if gross_rets else np.nan,
        'gross_total_bps': (np.sum(gross_rets) * 1e4) if gross_rets else np.nan,
        'gross_hit_rate': (np.mean(np.array(gross_rets) > 0)) if gross_rets else np.nan,
        'avg_hold_bars': np.mean([t['hold_bars'] for t in trades]) if trades else np.nan,
        'train_mean': train_mean,
        'train_std': train_std,
        'alpha': alpha,
        'beta': beta,
        'trades': trades,
    })

pair_df = pd.DataFrame(pair_rows)
pair_df.to_csv(OUTDIR / 'pair_metrics_full.csv', index=False)

strategies = {
    'ghe_low': pair_df.dropna(subset=['ghe']).sort_values(['ghe','coint_p','distance'], ascending=[True,True,True]).head(TOP_N),
    'corr_high': pair_df.dropna(subset=['corr']).sort_values(['corr','coint_p'], ascending=[False,True]).head(TOP_N),
    'coint_lowp': pair_df.dropna(subset=['coint_p']).sort_values(['coint_p','corr'], ascending=[True,False]).head(TOP_N),
    'distance_low': pair_df.dropna(subset=['distance']).sort_values(['distance','corr'], ascending=[True,False]).head(TOP_N),
}
summary_rows = []
selected_pairs = {}
for name, sdf in strategies.items():
    selected_pairs[name] = sdf[['pair','ghe','corr','coint_p','distance','n_trades','gross_mean_bps','gross_total_bps','gross_hit_rate','half_life_bars']].to_dict(orient='records')
    rets = []
    trade_count = 0
    holds = []
    for _, row in sdf.iterrows():
        for t in row['trades']:
            rets.append(t['gross_ret'])
            holds.append(t['hold_bars'])
        trade_count += int(row['n_trades'])
    gross_mean_bps = float(np.mean(rets) * 1e4) if rets else np.nan
    gross_total_bps = float(np.sum(rets) * 1e4) if rets else np.nan
    hit_rate = float(np.mean(np.array(rets) > 0)) if rets else np.nan
    out = {
        'strategy': name,
        'pairs': ', '.join(sdf['pair'].tolist()),
        'n_pairs': int(len(sdf)),
        'n_trades': int(trade_count),
        'gross_mean_bps': gross_mean_bps,
        'gross_total_bps': gross_total_bps,
        'gross_hit_rate': hit_rate,
        'avg_hold_bars': float(np.mean(holds)) if holds else np.nan,
        'avg_ghe': float(sdf['ghe'].mean()) if 'ghe' in sdf else np.nan,
        'avg_corr': float(sdf['corr'].mean()) if 'corr' in sdf else np.nan,
        'avg_coint_p': float(sdf['coint_p'].mean()) if 'coint_p' in sdf else np.nan,
    }
    for cost in COSTS_BPS:
        out[f'net_mean_bps_rt{cost}'] = gross_mean_bps - cost if np.isfinite(gross_mean_bps) else np.nan
        out[f'net_total_bps_rt{cost}'] = gross_total_bps - cost * trade_count if np.isfinite(gross_total_bps) else np.nan
    summary_rows.append(out)

summary_df = pd.DataFrame(summary_rows).sort_values('gross_total_bps', ascending=False)
summary_df.to_csv(OUTDIR / 'strategy_summary.csv', index=False)
with open(OUTDIR / 'selected_pairs.json', 'w') as f:
    json.dump(selected_pairs, f, indent=2)

best = summary_df.iloc[0].to_dict()
report = {
    'config': {
        'symbols': SYMBOLS,
        'interval': INTERVAL,
        'limit': LIMIT,
        'train_bars': TRAIN_BARS,
        'test_bars': TEST_BARS,
        'entry_z': ENTRY_Z,
        'exit_z': EXIT_Z,
        'max_z': MAX_Z,
        'time_stop_bars': TIME_STOP_BARS,
        'costs_bps': COSTS_BPS,
        'top_n_pairs': TOP_N,
    },
    'best_strategy': best,
}
with open(OUTDIR / 'summary.json', 'w') as f:
    json.dump(report, f, indent=2)

print('\n=== strategy summary ===')
print(summary_df.to_string(index=False))
print('\nArtifacts written to', OUTDIR)
