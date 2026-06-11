#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank6_btc_equity_proxy_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank6_btc_equity_proxy_15m'
TODO_PATH = ROOT / 'docs' / 'TODO.md'
PROBE_CSV = ROOT / 'reports' / 'artifacts' / 'external_data_probes' / 'rank6_btc_equity_proxy_probe_metrics.csv'

YAHOO_HEADERS = {'User-Agent': 'Mozilla/5.0'}
ASSETS = ['COIN', 'MSTR']
COSTS = [6.0, 10.0, 15.0, 20.0]
ROLL_Z = 48
BIG_MOVE_Z = 1.25
HOLD_BARS = 1

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def fetch_json(url: str, *, headers: dict | None = None, timeout: int = 30):
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_binance_klines(symbol: str = 'BTCUSDT', interval: str = '15m', days: int = 60) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    rows: list[list] = []
    cur = start_ms
    while cur < end_ms:
        params = urllib.parse.urlencode({'symbol': symbol, 'interval': interval, 'startTime': cur, 'endTime': end_ms, 'limit': 1000})
        with urllib.request.urlopen(f'https://api.binance.com/api/v3/klines?{params}', timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        if not data:
            break
        rows.extend(data)
        cur = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(rows, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q', 'n', 'tb', 'tq', 'ignore'])
    out = pd.DataFrame({
        'timestamp': pd.to_datetime(df['open_time'], unit='ms', utc=True).dt.floor('15min'),
        'btc_open': pd.to_numeric(df['open'], errors='coerce'),
        'btc_close': pd.to_numeric(df['close'], errors='coerce'),
    })
    return out.dropna().groupby('timestamp', as_index=False).last().sort_values('timestamp').reset_index(drop=True)


def fetch_yahoo_chart(symbol: str, interval: str = '15m', range_: str = '60d') -> pd.DataFrame:
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}&includePrePost=false'
    payload = fetch_json(url, headers=YAHOO_HEADERS)
    result = payload['chart']['result'][0]
    quote = result['indicators']['quote'][0]
    ts = pd.to_datetime(result['timestamp'], unit='s', utc=True).floor('15min')
    out = pd.DataFrame({
        'timestamp': ts,
        'eq_open': pd.to_numeric(quote['open'], errors='coerce'),
        'eq_close': pd.to_numeric(quote['close'], errors='coerce'),
    })
    out = out.dropna().groupby('timestamp', as_index=False).last().sort_values('timestamp').reset_index(drop=True)
    return out


def zscore(series: pd.Series, window: int) -> pd.Series:
    mean = series.rolling(window, min_periods=window).mean()
    std = series.rolling(window, min_periods=window).std(ddof=0).replace(0, np.nan)
    return (series - mean) / std


def build_frame(symbol: str, btc: pd.DataFrame) -> pd.DataFrame:
    eq = fetch_yahoo_chart(symbol)
    merged = btc.merge(eq, on='timestamp', how='inner').sort_values('timestamp').reset_index(drop=True)
    merged['btc_ret'] = np.log(merged['btc_close']).diff()
    merged['eq_ret'] = np.log(merged['eq_close']).diff()
    merged['btc_ret_prev1'] = merged['btc_ret'].shift(1)
    merged['btc_ret_prev2'] = np.log(merged['btc_close'] / merged['btc_close'].shift(2)).shift(1)
    merged['eq_ret_prev1'] = merged['eq_ret'].shift(1)
    merged['btc_z1'] = zscore(merged['btc_ret_prev1'], ROLL_Z)
    merged['btc_z2'] = zscore(merged['btc_ret_prev2'], ROLL_Z)
    merged['proxy_gap'] = merged['btc_ret_prev1'] - merged['eq_ret_prev1']
    merged['proxy_gap_z'] = zscore(merged['proxy_gap'], ROLL_Z)

    merged['signal_large_move_follow'] = np.where(merged['btc_z1'].abs() >= BIG_MOVE_Z, np.sign(merged['btc_ret_prev1']), 0.0)
    merged['signal_two_bar_follow'] = np.where(merged['btc_z2'].abs() >= BIG_MOVE_Z, np.sign(merged['btc_ret_prev2']), 0.0)
    merged['signal_gap_catchup'] = np.where(merged['proxy_gap_z'].abs() >= BIG_MOVE_Z, np.sign(merged['proxy_gap']), 0.0)
    return merged.dropna().reset_index(drop=True)


def build_trades(frame: pd.DataFrame, symbol: str, rule: str, cost: float) -> pd.DataFrame:
    signal_col = {
        'btc_large_move_follow_proxy': 'signal_large_move_follow',
        'btc_two_bar_follow_proxy': 'signal_two_bar_follow',
        'btc_proxy_gap_catchup': 'signal_gap_catchup',
    }[rule]
    rows = []
    cost_rate = cost / 10000.0
    for idx in range(len(frame) - HOLD_BARS):
        signal = float(frame.iloc[idx][signal_col])
        if signal == 0 or not math.isfinite(signal):
            continue
        entry_idx = idx
        exit_idx = min(idx + HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]['eq_open'])
        exit_price = float(frame.iloc[exit_idx]['eq_close'])
        gross_ret = (exit_price / entry_price - 1.0) * signal
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        btc_driver = float(frame.iloc[idx]['btc_ret_prev1'])
        rows.append({
            'symbol': symbol,
            'rule': rule,
            'cost_bps_per_side': float(cost),
            'timestamp': pd.to_datetime(frame.iloc[idx]['timestamp'], utc=True).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'direction': 'long' if signal > 0 else 'short',
            'entry_price': entry_price,
            'exit_price': exit_price,
            'gross_ret': gross_ret,
            'net_ret': net_ret,
            'btc_driver_ret': btc_driver,
            'eq_same_bar_ret': float(frame.iloc[idx]['eq_ret']) if pd.notna(frame.iloc[idx]['eq_ret']) else np.nan,
            'driver_z': float(frame.iloc[idx]['btc_z1']) if rule == 'btc_large_move_follow_proxy' else (float(frame.iloc[idx]['btc_z2']) if rule == 'btc_two_bar_follow_proxy' else float(frame.iloc[idx]['proxy_gap_z'])),
            'sign_hit': int(np.sign(gross_ret) > 0),
        })
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, symbol: str, rule: str, cost: float) -> dict[str, object]:
    if trades.empty:
        return {'symbol': symbol, 'rule': rule, 'cost_bps_per_side': float(cost), 'trades': 0, 'total_return': 0.0, 'avg_net_ret': np.nan, 'win_rate': np.nan, 'sign_hit_rate': np.nan}
    return {
        'symbol': symbol,
        'rule': rule,
        'cost_bps_per_side': float(cost),
        'trades': int(len(trades)),
        'total_return': float((1.0 + trades['net_ret']).prod() - 1.0),
        'avg_net_ret': float(trades['net_ret'].mean()),
        'win_rate': float((trades['net_ret'] > 0).mean()),
        'sign_hit_rate': float(trades['sign_hit'].mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (rule, cost), grp in asset_summary.groupby(['rule', 'cost_bps_per_side'], sort=False):
        total = grp['total_return'].to_numpy(dtype=float)
        rows.append({
            'rule': rule,
            'cost_bps_per_side': float(cost),
            'mean_total_return': float(np.nanmean(total)) if len(total) else np.nan,
            'positive_asset_ratio': float(np.nanmean(total > 0)) if len(total) else np.nan,
            'mean_trades': float(grp['trades'].mean()),
            'mean_win_rate': float(grp['win_rate'].mean()),
            'mean_sign_hit_rate': float(grp['sign_hit_rate'].mean()),
        })
    return pd.DataFrame(rows)


def build_time_buckets(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 6:
        return pd.DataFrame()
    out = []
    for symbol, grp in primary_trades.groupby('symbol', sort=False):
        grp = grp.sort_values('timestamp').reset_index(drop=True)
        grp['time_bucket'] = pd.qcut(grp.index + 1, q=3, labels=['bucket_1', 'bucket_2', 'bucket_3'])
        for bucket, sub in grp.groupby('time_bucket', sort=False, observed=False):
            out.append({
                'symbol': symbol,
                'time_bucket': str(bucket),
                'total_return': float((1.0 + sub['net_ret']).prod() - 1.0),
                'trades': int(len(sub)),
                'win_rate': float((sub['net_ret'] > 0).mean()),
            })
    return pd.DataFrame(out)


def build_verdict(overall: pd.DataFrame, time_buckets: pd.DataFrame) -> tuple[str, str, str]:
    focus = overall[overall['cost_bps_per_side'] == 6.0].copy()
    if focus.empty:
        return 'park / evidence pool', '没有形成足够样本，连最小 clean replication 都不够站住。', 'btc_large_move_follow_proxy'
    best = focus.sort_values(['mean_total_return', 'positive_asset_ratio', 'mean_trades'], ascending=False).iloc[0]
    primary_rule = str(best['rule'])
    bucket_ok = True
    tb = pd.DataFrame()
    if not time_buckets.empty and 'symbol' in time_buckets.columns:
        tb = time_buckets[time_buckets['symbol'].isin(ASSETS)]
    if not tb.empty:
        pos = tb.groupby('symbol')['total_return'].apply(lambda s: int((s > 0).sum()))
        bucket_ok = bool((pos >= 2).all())
    if float(best['mean_total_return']) > 0.03 and float(best['positive_asset_ratio']) >= 1.0 and float(best['mean_trades']) >= 20 and float(best['mean_sign_hit_rate']) >= 0.55 and bucket_ok:
        return 'P1 weak candidate / evidence pool', '最小 clean replication 至少没直接塌掉：COIN 和 MSTR 同时为正、交易数不算太薄、sign-hit 也不是纯随机。', primary_rule
    reason = (
        f"当前最不差的规则是 `{primary_rule}`，但 6bps/side 下跨资产也只到 mean_total_return≈{pct(best['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(best['positive_asset_ratio'])}、mean_trades≈{num(best['mean_trades'],1)}；还不够干净，先压回 park 更诚实。"
    )
    return 'park / evidence pool', reason, primary_rule


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_buckets: pd.DataFrame, primary_rule: str) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    probe_line = '- `Rank 6 / BTC -> COIN / MSTR proxy` 当前 probe 结论：**值得继续**；下一刀只允许做 `BTC lead -> COIN` 与 `BTC lead -> MSTR` 的最小 clean replication，不扩成全美股 proxy 宇宙。'
    focus = overall[overall['cost_bps_per_side'] == 6.0].sort_values(['mean_total_return', 'positive_asset_ratio'], ascending=False)
    stats = '；'.join(
        f"`{row['rule']} -> mean_total_return≈{pct(row['mean_total_return'])} / positive_asset_ratio≈{pct(row['positive_asset_ratio'])} / mean_trades≈{num(row['mean_trades'],1)}`"
        for _, row in focus.iterrows()
    )
    if time_buckets.empty:
        time_note = 'time-pocket honesty 当前样本偏薄；这本身也不支持直接升格。'
    else:
        time_note = 'time-pocket honesty：' + '；'.join(
            f"{row['symbol']}/{row['time_bucket']}≈{pct(row['total_return'])} / trades≈{int(row['trades'])}"
            for _, row in time_buckets.iterrows()
        ) + '。'
    new_probe = (
        '- `Rank 6 / BTC -> COIN / MSTR proxy` 当前 probe 结论：**已完成下一刀最小 clean replication**；固定 regular-session overlap，只做 '
        '`BTC -> COIN` 与 `BTC -> MSTR`，只比较 `btc_large_move_follow_proxy / btc_two_bar_follow_proxy / btc_proxy_gap_catchup` 三档最小规则，不扩成全美股 proxy 宇宙。\n'
        f'  - **最新补充（{generated_at}）**：这轮 hard verdict 是 **`{verdict}`**。当前 6bps/side 下的规则摘要：{stats}。{time_note} 网页落点：`reports/site/factors/scout_rank6_btc_equity_proxy_15m/report.html`。'
    )
    if probe_line in text:
        text = text.replace(probe_line, new_probe, 1)

    waiting_line = '本地 fast-intake shortlist 里剩余的 `Rank 5 / Rank 6` 仍偏外部数据依赖，不适合作为这一轮默认 Scout 主资源。'
    if waiting_line in text:
        new_waiting = '本地 fast-intake shortlist 已基本耗尽；`Rank 6` 的最小 clean replication 也已如实落地，当前更诚实口径 = `' + verdict + '`，`Rank 5` 仍停在 external-data probe。若没有新的本地 paper/repo 候选补进来，下一优先动作应转去 `Run 3 / tiny-live plumbing fallback`，而不是继续磨同一条 external-data 线。'
        text = text.replace(waiting_line, new_waiting, 1)

    TODO_PATH.write_text(text, encoding='utf-8')


def build_html(probe: pd.DataFrame, overall: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, verdict: str, verdict_reason: str, primary_rule: str, generated_at: str) -> str:
    headline = verdict_reason
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 6 · BTC -> COIN / MSTR proxy clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <h1>Rank 6 · BTC -> COIN / MSTR proxy spread</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：external-data fallback scout（本地 fast-intake 耗尽后的 1 刀诚实检查）</p>

  <div class="card">
    <h2>为什么轮到它</h2>
    <ul>
      <li><code>EMA</code> 当前处于 <code>waiting_not_due</code>。</li>
      <li><code>Rank 17 / Rank 2 / Rank 29</code> 的 P3 continuity 已交给 cron + 状态页托管，本轮不再占默认主资源。</li>
      <li>本地 <code>paper / repo based 5m / 15m crypto</code> shortlist 这一轮已基本耗尽，所以只给 external-data 线 1 次最小 clean replication 预算。</li>
    </ul>
  </div>

  <div class="card">
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定 regular-session overlap，只做 <code>BTC -> COIN</code> 与 <code>BTC -> MSTR</code>。</li>
      <li>只比较三档最小规则：<code>btc_large_move_follow_proxy</code>、<code>btc_two_bar_follow_proxy</code>、<code>btc_proxy_gap_catchup</code>。</li>
      <li>执行口径固定：信号只用上一根已完成的 BTC/equity overlap bar，交易发生在下一根 equity bar 的 <code>open -> close</code>。</li>
      <li>先回答 <code>post_cost_return / trade_count / sign-hit / time-pocket honesty</code>，不扩成完整 stat-arb 宇宙。</li>
    </ul>
  </div>

  <div class="card">
    <h2>probe 继承证据</h2>
    {render_table(probe[['symbol','overlap_bars','same_bar_corr','btc_leads_1bar_corr','best_nonzero_lag_bars','best_nonzero_lag_corr','top20pct_sign_hit_next_eq_bar']], percent_cols=set(), digits_cols={'overlap_bars':0,'same_bar_corr':3,'btc_leads_1bar_corr':3,'best_nonzero_lag_bars':0,'best_nonzero_lag_corr':3,'top20pct_sign_hit_next_eq_bar':3}) if not probe.empty else '<p class="muted">probe 文件缺失。</p>'}
  </div>

  <div class="card">
    <h2>hard verdict</h2>
    <p><span class="pill">{escape(verdict)}</span> 主规则：<code>{escape(primary_rule)}</code></p>
    <p><b>{escape(headline)}</b></p>
  </div>

  <div class="card">
    <h2>跨规则总表</h2>
    {render_table(overall[['rule','cost_bps_per_side','mean_total_return','positive_asset_ratio','mean_trades','mean_win_rate','mean_sign_hit_rate']], percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_sign_hit_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class="card">
    <h2>分资产摘要</h2>
    {render_table(asset_summary[['symbol','rule','cost_bps_per_side','trades','total_return','avg_net_ret','win_rate','sign_hit_rate']], percent_cols={'total_return','avg_net_ret','win_rate','sign_hit_rate'}, digits_cols={'cost_bps_per_side':0,'trades':0})}
  </div>

  <div class="card">
    <h2>time-pocket honesty（主规则 6bps）</h2>
    {render_table(time_buckets[['symbol','time_bucket','total_return','trades','win_rate']] if not time_buckets.empty else pd.DataFrame(), percent_cols={'total_return','win_rate'}, digits_cols={'trades':0})}
  </div>

  <div class="card">
    <h2>artifact</h2>
    <ul>
      <li><a href="../../../artifacts/scout_rank6_btc_equity_proxy_15m/overall_summary.csv">overall_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank6_btc_equity_proxy_15m/asset_summary.csv">asset_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank6_btc_equity_proxy_15m/primary_trades_6bps.csv">primary_trades_6bps.csv</a></li>
      <li><a href="../../../artifacts/scout_rank6_btc_equity_proxy_15m/time_bucket_summary.csv">time_bucket_summary.csv</a></li>
    </ul>
  </div>
</body>
</html>'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    btc = fetch_binance_klines(days=60)
    probe = pd.read_csv(PROBE_CSV) if PROBE_CSV.exists() else pd.DataFrame()
    asset_rows = []
    all_trades = []
    frames = {}
    rules = ['btc_large_move_follow_proxy', 'btc_two_bar_follow_proxy', 'btc_proxy_gap_catchup']

    for symbol in ASSETS:
        frame = build_frame(symbol, btc)
        frames[symbol] = frame
        frame.to_csv(ART_DIR / f'{symbol.lower()}_merged_frame.csv', index=False)
        for rule in rules:
            for cost in COSTS:
                trades = build_trades(frame, symbol, rule, cost)
                if not trades.empty:
                    all_trades.append(trades)
                asset_rows.append(summarize_asset(trades, symbol, rule, cost))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    verdict, verdict_reason, primary_rule = build_verdict(overall, pd.DataFrame())
    primary_trades = pd.DataFrame()
    if not trades_df.empty:
        primary_trades = trades_df[(trades_df['rule'] == primary_rule) & (trades_df['cost_bps_per_side'] == 6.0)].copy()
    time_buckets = build_time_buckets(primary_trades)
    verdict, verdict_reason, primary_rule = build_verdict(overall, time_buckets)
    if not trades_df.empty:
        primary_trades = trades_df[(trades_df['rule'] == primary_rule) & (trades_df['cost_bps_per_side'] == 6.0)].copy()
        time_buckets = build_time_buckets(primary_trades)

    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    primary_trades.to_csv(ART_DIR / 'primary_trades_6bps.csv', index=False)
    time_buckets.to_csv(ART_DIR / 'time_bucket_summary.csv', index=False)
    pd.DataFrame([{'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'hard_verdict': verdict, 'primary_rule': primary_rule, 'verdict_reason': verdict_reason}]).to_csv(ART_DIR / 'meta.csv', index=False)

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = build_html(probe, overall, asset_summary, time_buckets, verdict, verdict_reason, primary_rule, generated_at)
    (SITE_DIR / 'report.html').write_text(html, encoding='utf-8')
    update_todo(verdict, generated_at, overall, time_buckets, primary_rule)

    print(f'verdict={verdict}')
    print(overall[overall['cost_bps_per_side'] == 6.0].to_dict(orient='records'))


if __name__ == '__main__':
    main()
