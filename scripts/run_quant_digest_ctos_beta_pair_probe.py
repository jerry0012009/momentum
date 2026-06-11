import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import requests

BASE = Path('/root/clawd/jerry/momentum')
OUTDIR = BASE / 'reports/artifacts/quant_digests/ctos_beta_pairs_probe_20260420_0448'
OUTDIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','XRPUSDT','ADAUSDT','DOGEUSDT','LINKUSDT','AVAXUSDT','LTCUSDT','DOTUSDT','TRXUSDT']
INTERVAL = '15m'
LIMIT = 1500
TRAIN_BARS = 1000
ENTRY_Z = 2.0
EXIT_Z = 0.5
SPIKE_Z = 3.5
TIME_STOP = 32
COST_BPS = [4, 8, 12]

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})


def fetch_klines(symbol, interval='15m', limit=1500):
    r = session.get('https://fapi.binance.com/fapi/v1/klines', params={'symbol': symbol, 'interval': interval, 'limit': limit}, timeout=30)
    r.raise_for_status()
    cols = ['open_time','open','high','low','close','volume','close_time','qav','trades','tbav','tqav','ignore']
    df = pd.DataFrame(r.json(), columns=cols)
    for c in ['open','high','low','close','volume']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    return df[['open_time','close']]


def beta_from_returns(a, b):
    ra = a.pct_change().dropna()
    rb = b.pct_change().dropna()
    n = min(len(ra), len(rb))
    if n < 20:
        return np.nan, np.nan
    ra = ra.iloc[-n:]
    rb = rb.iloc[-n:]
    corr = np.corrcoef(ra, rb)[0, 1]
    den = np.var(rb)
    beta = np.cov(ra, rb, ddof=0)[0, 1] / den if den > 0 else np.nan
    return float(beta), float(corr)


def run_pair(df, train_beta, train_corr):
    ratio = df['a'] / df['b']
    train_ratio = ratio.iloc[:TRAIN_BARS]
    mean = float(train_ratio.mean())
    std = float(train_ratio.std(ddof=0))
    if not np.isfinite(std) or std <= 0:
        return []

    zthr = ENTRY_Z * (0.90 if train_corr >= 0.95 else 1.15 if train_corr < 0.85 else 1.0)
    beta = abs(train_beta)
    weight_a = 1 / (1 + beta)
    weight_b = beta / (1 + beta)
    weight_a = max(0.30, min(0.70, weight_a))
    weight_b = 1 - weight_a

    trades = []
    pos = 0
    entry_idx = None
    entry_a = entry_b = None
    entry_z = None
    for i in range(TRAIN_BARS, len(df)):
        z = (ratio.iat[i] - mean) / std
        prev_z = (ratio.iat[i - 1] - mean) / std if i - 1 >= TRAIN_BARS else 0.0
        if pos == 0:
            if abs(z) >= zthr and abs(z) < SPIKE_Z and abs(z - prev_z) <= 1.2:
                pos = -1 if z > 0 else 1  # +1 long spread(long a short b), -1 short spread
                entry_idx = i
                entry_a = df['a'].iat[i]
                entry_b = df['b'].iat[i]
                entry_z = z
        else:
            hold = i - entry_idx
            should_exit = abs(z) <= EXIT_Z or abs(z) >= SPIKE_Z or hold >= TIME_STOP
            if should_exit:
                exit_a = df['a'].iat[i]
                exit_b = df['b'].iat[i]
                ret_a = exit_a / entry_a - 1.0
                ret_b = exit_b / entry_b - 1.0
                gross = (weight_a * ret_a - weight_b * ret_b) if pos == 1 else (-weight_a * ret_a + weight_b * ret_b)
                trades.append({
                    'entry_time': df['open_time'].iat[entry_idx],
                    'exit_time': df['open_time'].iat[i],
                    'entry_z': float(entry_z),
                    'exit_z': float(z),
                    'hold_bars': int(hold),
                    'side': 'long_spread' if pos == 1 else 'short_spread',
                    'gross_ret': float(gross),
                    'weight_a': float(weight_a),
                    'weight_b': float(weight_b),
                    'beta': float(beta),
                    'corr': float(train_corr),
                    'entry_threshold': float(zthr),
                })
                pos = 0
                entry_idx = None
                entry_a = entry_b = None
                entry_z = None
    return trades


print('fetching data...')
raw = {s: fetch_klines(s, INTERVAL, LIMIT) for s in SYMBOLS}
common = sorted(set.intersection(*[set(df['open_time']) for df in raw.values()]))
for s in SYMBOLS:
    raw[s] = raw[s][raw[s]['open_time'].isin(common)].sort_values('open_time').reset_index(drop=True)
min_len = min(len(v) for v in raw.values())
for s in SYMBOLS:
    raw[s] = raw[s].tail(min_len).reset_index(drop=True)

pair_rows = []
all_trades = []
for a, b in combinations(SYMBOLS, 2):
    df = pd.DataFrame({'open_time': raw[a]['open_time'], 'a': raw[a]['close'], 'b': raw[b]['close']}).dropna().reset_index(drop=True)
    beta, corr = beta_from_returns(df['a'].iloc[:TRAIN_BARS], df['b'].iloc[:TRAIN_BARS])
    if not np.isfinite(beta) or not np.isfinite(corr) or beta <= 0 or corr < 0.85:
        continue
    trades = run_pair(df, beta, corr)
    rets = np.array([t['gross_ret'] for t in trades], dtype=float) if trades else np.array([])
    row = {
        'pair': f'{a}-{b}',
        'a': a,
        'b': b,
        'beta': float(beta),
        'corr': float(corr),
        'n_trades': int(len(trades)),
        'gross_mean_bps': float(rets.mean() * 1e4) if len(rets) else np.nan,
        'gross_total_bps': float(rets.sum() * 1e4) if len(rets) else np.nan,
        'hit_rate': float((rets > 0).mean()) if len(rets) else np.nan,
        'avg_hold_bars': float(np.mean([t['hold_bars'] for t in trades])) if trades else np.nan,
    }
    for c in COST_BPS:
        row[f'net_total_bps_rt{c}'] = row['gross_total_bps'] - c * row['n_trades'] if len(rets) else np.nan
        row[f'net_mean_bps_rt{c}'] = row['gross_mean_bps'] - c if len(rets) else np.nan
    pair_rows.append(row)
    for t in trades:
        x = dict(t)
        x['pair'] = row['pair']
        x['a'] = a
        x['b'] = b
        all_trades.append(x)

pair_df = pd.DataFrame(pair_rows).sort_values(['net_total_bps_rt8', 'gross_total_bps'], ascending=[False, False])
pair_df.to_csv(OUTDIR / 'pair_summary.csv', index=False)

# portfolio shell with asset exclusivity
selected = []
open_until = {}
for trade in sorted(all_trades, key=lambda x: x['entry_time']):
    a, b = trade['a'], trade['b']
    et = trade['entry_time']
    if open_until.get(a, pd.Timestamp.min.tz_localize('UTC')) > et or open_until.get(b, pd.Timestamp.min.tz_localize('UTC')) > et:
        continue
    selected.append(trade)
    open_until[a] = trade['exit_time']
    open_until[b] = trade['exit_time']

sel = pd.DataFrame(selected)
portfolio = {}
if len(sel):
    gross = sel['gross_ret'].to_numpy()
    portfolio = {
        'selected_trades': int(len(sel)),
        'distinct_pairs': int(sel['pair'].nunique()),
        'gross_mean_bps': float(gross.mean() * 1e4),
        'gross_total_bps': float(gross.sum() * 1e4),
        'hit_rate': float((gross > 0).mean()),
        'avg_hold_bars': float(sel['hold_bars'].mean()),
        'top_pairs': sel['pair'].value_counts().head(8).to_dict(),
    }
    for c in COST_BPS:
        portfolio[f'net_total_bps_rt{c}'] = float(gross.sum() * 1e4 - c * len(sel))
        portfolio[f'net_mean_bps_rt{c}'] = float(gross.mean() * 1e4 - c)
else:
    portfolio = {'selected_trades': 0}

sel.to_csv(OUTDIR / 'portfolio_selected_trades.csv', index=False)
summary = {
    'config': {
        'symbols': SYMBOLS,
        'interval': INTERVAL,
        'limit': LIMIT,
        'train_bars': TRAIN_BARS,
        'entry_z': ENTRY_Z,
        'exit_z': EXIT_Z,
        'spike_z': SPIKE_Z,
        'time_stop_bars': TIME_STOP,
        'corr_min': 0.85,
        'dynamic_threshold': 'corr>=0.95 => 0.9x entry; corr<0.85 => 1.15x entry',
        'asset_exclusivity': True,
        'beta_weight_clamp': '[0.30, 0.70]',
        'cost_bps': COST_BPS,
    },
    'n_eligible_pairs': int(len(pair_df)),
    'top_pairs': pair_df.head(10).to_dict(orient='records'),
    'portfolio_shell': portfolio,
}
with open(OUTDIR / 'summary.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(json.dumps(summary, indent=2, default=str))
print(f'Wrote artifacts to {OUTDIR}')
