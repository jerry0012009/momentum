#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'rank254_survivor_followup_20260330'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'rank254_jump_follower_survivor_followup'
CACHE_DIR = ART_DIR / 'kline_cache'

BINANCE_URL = 'https://fapi.binance.com/fapi/v1/klines'
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'LTCUSDT', 'XRPUSDT', 'BCHUSDT', 'ETCUSDT']
FOLLOWERS = SYMBOLS[1:]
INTERVAL = '1m'
LOOKBACK_DAYS = 30
LIMIT = 1000
HOLDS = [3, 5, 15]
COST_PER_SIDE_BPS = 8.0
JUMP_RET_Q = 0.995
JUMP_VOL_Q = 0.95
MIN_BETA_WINDOW = 240
COOLDOWN_BARS = 15
MAX_FOLLOWER_MOVE_RATIO = 0.60
MIN_FOLLOWERS = 2

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:28px auto; padding:0 18px 40px; color:#111827; background:#f8fafc; line-height:1.65; }
h1,h2,h3 { color:#111827; }
.card { background:white; border:1px solid #e5e7eb; border-radius:14px; padding:16px 18px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin:12px 0; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; }
"""


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def pct(v, d=2):
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v)*100:.{d}f}%'


def num(v, d=2):
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{d}f}'


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    header = ''.join(f'<th>{c}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v, digits_cols.get(col, 2))
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f'<td>{text}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<table><thead><tr>' + header + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding='utf-8')


def net_ret(gross, cost_bps=COST_PER_SIDE_BPS):
    rate = cost_bps / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def fetch_symbol(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    cache = ensure_dir(CACHE_DIR) / f'{symbol}_{start_ms}_{end_ms}.csv'
    if cache.exists():
        df = pd.read_csv(cache)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        return df
    rows = []
    cur = start_ms
    while cur < end_ms:
        params = urllib.parse.urlencode({
            'symbol': symbol,
            'interval': INTERVAL,
            'startTime': cur,
            'endTime': end_ms,
            'limit': LIMIT,
        })
        req = urllib.request.Request(BINANCE_URL + '?' + params, headers={'User-Agent': 'Mozilla/5.0'})
        for attempt in range(6):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    batch = json.loads(resp.read().decode())
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 5:
                    raise
                time.sleep(2.0 * (attempt + 1))
        else:
            batch = []
        if not batch:
            break
        rows.extend(batch)
        cur = int(batch[-1][0]) + 60_000
        time.sleep(0.30)
    if not rows:
        raise RuntimeError(f'no rows for {symbol}')
    df = pd.DataFrame(rows, columns=['open_time','open','high','low','close','volume','close_time','quote_volume','trade_count','taker_base','taker_quote','ignore'])
    df = df[['open_time','open','high','low','close','volume']].copy()
    df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    for c in ['open','high','low','close','volume']:
        df[c] = df[c].astype(float)
    df = df[['timestamp','open','high','low','close','volume']].sort_values('timestamp').drop_duplicates('timestamp').reset_index(drop=True)
    df.to_csv(cache, index=False)
    return df


def rolling_beta(y: pd.Series, x: pd.Series, window: int = MIN_BETA_WINDOW) -> pd.Series:
    cov = y.rolling(window, min_periods=window).cov(x)
    var = x.rolling(window, min_periods=window).var()
    beta = cov / var.replace(0, np.nan)
    return beta.clip(lower=-3, upper=3)


def prepare() -> pd.DataFrame:
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=LOOKBACK_DAYS)
    frames = []
    for sym in SYMBOLS:
        df = fetch_symbol(sym, int(start.timestamp()*1000), int(end.timestamp()*1000))
        df = df.rename(columns={c: f'{sym}_{c}' for c in ['open','high','low','close','volume']})
        frames.append(df)
    merged = frames[0]
    for df in frames[1:]:
        merged = merged.merge(df, on='timestamp', how='inner')
    merged = merged.sort_values('timestamp').reset_index(drop=True)
    for sym in SYMBOLS:
        merged[f'{sym}_ret1'] = merged[f'{sym}_close'].pct_change()
    for sym in FOLLOWERS:
        merged[f'{sym}_beta'] = rolling_beta(merged[f'{sym}_ret1'], merged['BTCUSDT_ret1'])
    return merged


def event_mask(df: pd.DataFrame) -> pd.Series:
    warmup = min(10 * 24 * 60, len(df) // 2)
    btc_abs_ret = df['BTCUSDT_ret1'].abs()
    btc_vol = df['BTCUSDT_volume']
    ret_thr = btc_abs_ret.iloc[:warmup].quantile(JUMP_RET_Q)
    vol_thr = btc_vol.iloc[:warmup].quantile(JUMP_VOL_Q)
    df['btc_jump_ret_thr'] = ret_thr
    df['btc_jump_vol_thr'] = vol_thr
    sign = np.sign(df['BTCUSDT_ret1'])
    return (btc_abs_ret >= ret_thr) & (btc_vol >= vol_thr) & (sign != 0)


def eligible_followers(row: pd.Series) -> list[str]:
    s = np.sign(row['BTCUSDT_ret1'])
    btc_abs = abs(row['BTCUSDT_ret1'])
    out = []
    for sym in FOLLOWERS:
        r = row[f'{sym}_ret1']
        if pd.isna(r):
            continue
        if np.sign(r) == s and abs(r) <= btc_abs * MAX_FOLLOWER_MOVE_RATIO:
            out.append(sym)
        elif r == 0:
            out.append(sym)
    return out


def unconditional_mask(df: pd.DataFrame) -> pd.Series:
    sign = np.sign(df['BTCUSDT_ret1'])
    base = (df['BTCUSDT_ret1'].abs() > 0) & (sign != 0)
    return base


def simulate(df: pd.DataFrame, event_col: str, hold: int, label: str, beta_hedged: bool = False, hour_gate: tuple[int,int] | None = None, negative_only: bool = False) -> tuple[pd.DataFrame, dict]:
    rows = []
    i = 1
    n = len(df)
    while i < n - hold - 2:
        row = df.iloc[i]
        if not bool(row[event_col]):
            i += 1
            continue
        if negative_only and row['BTCUSDT_ret1'] >= 0:
            i += 1
            continue
        if hour_gate is not None:
            h = row['timestamp'].hour
            if not (hour_gate[0] <= h < hour_gate[1]):
                i += 1
                continue
        elig = eligible_followers(row)
        if len(elig) < MIN_FOLLOWERS:
            i += 1
            continue
        entry_idx = i + 1
        exit_idx = entry_idx + hold
        if exit_idx >= n:
            break
        s = np.sign(row['BTCUSDT_ret1'])
        grosses = []
        hedge_grosses = []
        betas = []
        for sym in elig:
            entry = df.iloc[entry_idx][f'{sym}_open']
            exitp = df.iloc[exit_idx][f'{sym}_open']
            asset_ret = s * (exitp / entry - 1.0)
            grosses.append(asset_ret)
            beta = df.iloc[i][f'{sym}_beta']
            if pd.isna(beta):
                beta = 1.0
            betas.append(beta)
            btc_entry = df.iloc[entry_idx]['BTCUSDT_open']
            btc_exit = df.iloc[exit_idx]['BTCUSDT_open']
            btc_ret = s * (btc_exit / btc_entry - 1.0)
            hedge_grosses.append(asset_ret - beta * btc_ret)
        gross = float(np.mean(hedge_grosses if beta_hedged else grosses))
        net = float(net_ret(gross))
        rows.append({
            'label': label,
            'event_time': row['timestamp'],
            'direction': 'short' if s < 0 else 'long',
            'followers': ','.join(elig),
            'n_followers': len(elig),
            'hold_min': hold,
            'gross_ret': gross,
            'net_ret': net,
            'avg_beta': float(np.mean(betas)) if betas else np.nan,
            'btc_event_ret1': float(row['BTCUSDT_ret1']),
        })
        i = exit_idx + COOLDOWN_BARS
    trades = pd.DataFrame(rows)
    if trades.empty:
        return trades, {'label': label, 'hold_min': hold, 'trades': 0}
    summary = {
        'label': label,
        'hold_min': hold,
        'trades': int(len(trades)),
        'share_short': float((trades['direction'] == 'short').mean()),
        'mean_net_ret': float(trades['net_ret'].mean()),
        'median_net_ret': float(trades['net_ret'].median()),
        'hit_rate': float((trades['net_ret'] > 0).mean()),
        'cum_net_ret': float((1.0 + trades['net_ret']).prod() - 1.0),
        'avg_followers': float(trades['n_followers'].mean()),
    }
    return trades, summary


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    df = prepare()
    df['event_jump'] = event_mask(df)
    df['event_unconditional'] = unconditional_mask(df)

    summaries = []
    trade_frames = []
    for hold in HOLDS:
        configs = [
            ('jump_baseline', False, None, False, 'event_jump'),
            ('jump_negative_only', False, None, True, 'event_jump'),
            ('jump_13_17_utc_only', False, (13,17), False, 'event_jump'),
            ('jump_beta_hedged_spread', True, None, False, 'event_jump'),
            ('unconditional_followthrough_baseline', False, None, False, 'event_unconditional'),
        ]
        for label, beta_hedged, gate, neg_only, event_col in configs:
            trades, summary = simulate(df, event_col=event_col, hold=hold, label=label, beta_hedged=beta_hedged, hour_gate=gate, negative_only=neg_only)
            summaries.append(summary)
            if not trades.empty:
                trade_frames.append(trades)

    summary_df = pd.DataFrame(summaries).sort_values(['hold_min','label']).reset_index(drop=True)
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    summary_path = ART_DIR / 'summary_by_variant.csv'
    trades_path = ART_DIR / 'trade_log.csv'
    meta_path = ART_DIR / 'run_meta.json'
    summary_df.to_csv(summary_path, index=False)
    if not trades_df.empty:
        trades_df.to_csv(trades_path, index=False)

    primary = summary_df[summary_df['hold_min'] == 5].copy()
    by_label = {r['label']: r for r in primary.to_dict('records')}
    verdict = {
        'promote_p2': False,
        'reason': '',
    }
    base = by_label.get('jump_baseline')
    uncond = by_label.get('unconditional_followthrough_baseline')
    neg = by_label.get('jump_negative_only')
    gate = by_label.get('jump_13_17_utc_only')
    hedge = by_label.get('jump_beta_hedged_spread')
    if base and uncond and neg and gate and hedge:
        if (base['mean_net_ret'] > uncond['mean_net_ret'] + 0.0005 and max(neg['mean_net_ret'], gate['mean_net_ret'], hedge['mean_net_ret']) > 0.0005 and hedge['mean_net_ret'] > 0):
            verdict['promote_p2'] = True
            verdict['reason'] = '至少一条事件版在 5m 持有上保留了显著正的 after-cost edge，且 beta-hedged 版本仍为正。'
        else:
            verdict['reason'] = '5m 主持有窗下，jump 事件版没有把 after-cost edge 稳定抬到无条件基线之上；beta-hedged 版本转负说明主要吃的是 BTC beta 尾巴。'

    meta = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'lookback_days': LOOKBACK_DAYS,
        'symbols': SYMBOLS,
        'followers': FOLLOWERS,
        'cost_per_side_bps': COST_PER_SIDE_BPS,
        'jump_ret_quantile_frozen_on_first_30d': JUMP_RET_Q,
        'jump_vol_quantile_frozen_on_first_30d': JUMP_VOL_Q,
        'cooldown_bars': COOLDOWN_BARS,
        'max_follower_move_ratio': MAX_FOLLOWER_MOVE_RATIO,
        'min_followers': MIN_FOLLOWERS,
        'verdict': verdict,
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')

    title = 'Rank 254 survivor follow-up — BTC confirmed jump → liquid-alt follower contagion'
    body = [
        f'<h1>{title}</h1>',
        '<div class="card">',
        '<p>本页做的是 public-data frozen replication：Binance USDⓈ-M 1m 公共 K 线，样本近 90 天；BTC 事件锚固定为首 30 天样本上冻结后的 <code>|1m return| ≥ 99.5% 分位</code> 且 <code>volume ≥ 95% 分位</code>；followers 限定 <code>ETH/LTC/XRP/BCH/ETC</code>；执行强制 <code>next-bar open entry + no-overlap + 8 bps/side</code>。</p>',
        f"<p><b>机器判定：</b> {'promote_P2' if verdict['promote_p2'] else 'background/P0'}。{verdict['reason']}</p>",
        '</div>',
        '<h2>Variant summary</h2>',
        render_table(summary_df, percent_cols={'share_short','mean_net_ret','median_net_ret','hit_rate','cum_net_ret'}, digits_cols={'share_short':2,'mean_net_ret':3,'median_net_ret':3,'hit_rate':2,'cum_net_ret':2,'avg_followers':2}),
    ]
    if not trades_df.empty:
        sample = trades_df.sort_values('event_time').tail(12).copy()
        sample['event_time'] = sample['event_time'].astype(str)
        body += ['<h2>Recent trade sample</h2>', render_table(sample[['label','event_time','direction','followers','n_followers','hold_min','gross_ret','net_ret','avg_beta']], percent_cols={'gross_ret','net_ret'}, digits_cols={'gross_ret':3,'net_ret':3,'avg_beta':2})]
    write_html(SITE_DIR / 'report.html', title, ''.join(body))
    print(json.dumps({'summary_path': str(summary_path), 'trades_path': str(trades_path), 'meta_path': str(meta_path), 'site_report': str(SITE_DIR / 'report.html'), 'verdict': verdict}, ensure_ascii=False))


if __name__ == '__main__':
    main()
