#!/usr/bin/env python3
"""SL-Only backtest WITH funding rate impact.

Adds per-trade funding PnL to the SL-only backtest report.
Reuses same data/logic as backtest_sl_only_report.py but includes funding.
"""

import glob
import zipfile
import json
import os
import re
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
FUNDING_DIR = ROOT / 'data/binance_funding_rate'
OUT_HTML = ROOT / 'reports/backtest_sl_only_with_funding.html'

FEE_RATE = 4.0 / 10000.0

# ── Funding data loader ──────────────────────────────────────────────

_funding_cache = {}

def load_funding_cache():
    """Load all funding data into memory. Key: symbol -> sorted DataFrame."""
    global _funding_cache
    if _funding_cache:
        return _funding_cache

    for sym in os.listdir(FUNDING_DIR):
        sym_dir = os.path.join(FUNDING_DIR, sym)
        if not os.path.isdir(sym_dir):
            continue
        frames = []
        for zf_path in sorted(glob.glob(os.path.join(sym_dir, '*.zip'))):
            try:
                with zipfile.ZipFile(zf_path) as z:
                    for name in z.namelist():
                        if name.endswith('.csv'):
                            with z.open(name) as f:
                                df = pd.read_csv(f)
                                if 'last_funding_rate' in df.columns:
                                    df['timestamp'] = pd.to_datetime(df['calc_time'], unit='ms', utc=True)
                                    df['funding_rate'] = df['last_funding_rate'].astype(float)
                                elif 'fundingRate' in df.columns:
                                    ts_col = [c for c in df.columns if 'time' in c.lower() or 'calc' in c.lower()][0]
                                    df = df.rename(columns={ts_col: 'timestamp', 'fundingRate': 'funding_rate'})
                                    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                                df = df[['timestamp', 'funding_rate']].dropna()
                                frames.append(df)
            except Exception:
                continue
        if frames:
            result = pd.concat(frames, ignore_index=True).drop_duplicates('timestamp').sort_values('timestamp').reset_index(drop=True)
            _funding_cache[sym] = result

    return _funding_cache


def calc_funding_pnl(symbol, entry_ts, exit_ts, fc):
    """Sum funding rates between entry and exit for a LONG position.

    For LONG: funding > 0 means longs PAY (negative PnL), funding < 0 means longs RECEIVE (positive PnL).
    So PnL = -sum(funding_rates)
    """
    if symbol not in fc:
        return 0.0, 0
    fd = fc[symbol]
    mask = (fd['timestamp'] >= entry_ts) & (fd['timestamp'] <= exit_ts)
    events = fd[mask]
    if len(events) == 0:
        return 0.0, 0
    total = events['funding_rate'].sum()
    return -float(total), len(events)


# ── Data loaders ─────────────────────────────────────────────────────

def load_data():
    trades = pd.read_csv(TRADES_F)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)
    valid = trades.dropna(subset=['trail_3pct_ret']).copy()
    symbols = valid['symbol'].unique()
    candle_cache = {}
    for sym in sorted(symbols):
        sym_dir = CACHE_DIR / sym
        files = sorted(glob.glob(str(sym_dir / f'{sym}-1h-*.zip')))
        if not files:
            continue
        frames = []
        for f in files:
            try:
                with zipfile.ZipFile(f) as zf:
                    names = [n for n in zf.namelist() if n.endswith('.csv')]
                    if not names:
                        continue
                    with zf.open(names[0]) as fh:
                        df = pd.read_csv(fh, usecols=[0,1,2,3,4,5])
                        frames.append(df)
            except Exception:
                continue
        if frames:
            df = pd.concat(frames, ignore_index=True)
            df['open_time'] = pd.to_numeric(df['open_time'], errors='coerce')
            df = df.dropna(subset=['open_time']).sort_values('open_time').reset_index(drop=True)
            candle_cache[sym] = {
                'open_time': df['open_time'].values,
                'high': df['high'].values.astype(float),
                'low': df['low'].values.astype(float),
                'close': df['close'].values.astype(float),
            }
    return valid, candle_cache


def load_btc():
    btc_dir = CACHE_DIR / 'BTCUSDT'
    btc_files = sorted(glob.glob(str(btc_dir / 'BTCUSDT-1h-*.zip')))
    btc_frames = []
    for f in btc_files:
        try:
            with zipfile.ZipFile(f) as zf:
                names = [n for n in zf.namelist() if n.endswith('.csv')]
                if names:
                    with zf.open(names[0]) as fh:
                        df = pd.read_csv(fh, header=None)
                        df = df[[0, 4]]
                        df.columns = ['open_time', 'close']
                        btc_frames.append(df)
        except:
            continue
    btc = pd.concat(btc_frames, ignore_index=True)
    btc['open_time'] = pd.to_numeric(btc['open_time'], errors='coerce')
    btc = btc.dropna().sort_values('open_time').reset_index(drop=True)
    btc['close'] = btc['close'].astype(float)
    return btc


def find_bar_idx(open_times, target_ts_ms):
    idx = np.searchsorted(open_times, target_ts_ms, side='left')
    return int(idx) if idx < len(open_times) else None


def sim_sl_only(c, idx, px, sl_pct, timeout, fee):
    end = min(idx + timeout, len(c['close']))
    sl_px = px * (1 - sl_pct)
    for i in range(idx, end):
        if c['low'][i] <= sl_px:
            return -sl_pct, i
    ret = (c['close'][end-1] - px) / px
    return ret, end - 1


# ── Stats with funding ───────────────────────────────────────────────

def stats_with_funding(rets, fee, funding_pnls):
    if not rets:
        return None
    nets = np.array([(1+r)*(1-fee)**2 - 1 for r in rets])
    fund = np.array(funding_pnls)
    nets_adj = nets + fund

    def _calc(arr):
        wins = arr[arr>0].sum()
        losses = -arr[arr<0].sum()
        pf = float(wins/losses) if losses>0 else float('inf')
        return {
            'n': len(arr),
            'mean': round(float(np.mean(arr)*100), 2),
            'median': round(float(np.median(arr)*100), 2),
            'wr': round(float(np.mean(arr>0)*100), 1),
            'pf': round(pf, 2),
            'total': round(float(np.sum(arr)*100), 1),
        }

    base = _calc(nets)
    adj = _calc(nets_adj)
    return {
        'base': base,
        'funding_mean': round(float(np.mean(fund)*100), 4),
        'funding_total': round(float(np.sum(fund)*100), 2),
        'adj': adj,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print('Loading trade data...')
    valid, candle_cache = load_data()
    print(f'Loaded {len(valid):,} trades, {len(candle_cache)} symbols')

    print('Loading BTC data...')
    btc = load_btc()
    btc_ts = btc['open_time'].values
    btc_close = btc['close'].values

    print('Loading funding data...')
    fc = load_funding_cache()
    print(f'Funding data for {len(fc)} symbols')

    def get_btc_return(signal_ts, lookback_hours):
        ts_ms = int(signal_ts.timestamp() * 1000)
        cur_idx = find_bar_idx(btc_ts, ts_ms)
        if cur_idx is None or cur_idx < lookback_hours:
            return None
        return (btc_close[cur_idx] - btc_close[cur_idx - lookback_hours]) / btc_close[cur_idx - lookback_hours]

    print('Pre-computing entries...')
    entries = []
    for _, row in valid.iterrows():
        sym = row['symbol']
        if sym not in candle_cache:
            continue
        c = candle_cache[sym]
        entry_ts_ms = int(row['signal_ts'].timestamp() * 1000)
        idx = find_bar_idx(c['open_time'], entry_ts_ms)
        if idx is None:
            continue
        idx += 1
        if idx >= len(c['close']):
            continue
        btc_ret = get_btc_return(row['signal_ts'], 168)
        entries.append({
            'sym': sym, 'idx': idx, 'px': float(row['entry_price']),
            'ts': row['signal_ts'], 'btc_ret_7d': btc_ret,
        })
    print(f'Valid entries: {len(entries)}')

    # ── Run simulations with funding ──
    report = {}

    def run_sim(subset, sl=0.08, timeout=96, fee=FEE_RATE, label=''):
        rets = []
        fund_pnls = []
        for e in subset:
            c = candle_cache[e['sym']]
            r, exit_idx = sim_sl_only(c, e['idx'], e['px'], sl, timeout, fee)
            # Compute exit timestamp from candle open_time
            exit_ts_ms = int(c['open_time'][exit_idx])
            exit_ts = pd.Timestamp(exit_ts_ms, unit='ms', tz='UTC')
            fpnl, _ = calc_funding_pnl(e['sym'], e['ts'], exit_ts, fc)
            rets.append(r)
            fund_pnls.append(fpnl)
        return stats_with_funding(rets, fee, fund_pnls)

    # 1. Slippage
    print('Part 1: Slippage + Funding...')
    slip_results = []
    for slip_bps in [0, 10, 20, 30, 50, 80, 100, 150]:
        f = (4.0 + slip_bps) / 10000.0
        s = run_sim(entries, sl=0.08, timeout=96, fee=f)
        if s:
            s['slip_bps'] = slip_bps
            slip_results.append(s)
    report['slippage'] = slip_results

    # 2. Yearly
    print('Part 2: Yearly + Funding...')
    yearly = []
    for yr in sorted(set(e['ts'].year for e in entries)):
        subset = [e for e in entries if e['ts'].year == yr]
        s = run_sim(subset)
        if s:
            s['period'] = str(yr)
            yearly.append(s)
    report['yearly'] = yearly

    # 3. Quarterly
    print('Part 3: Quarterly + Funding...')
    for e in entries:
        e['quarter'] = f'{e["ts"].year}-Q{(e["ts"].month-1)//3+1}'
    quarterly = []
    for q in sorted(set(e['quarter'] for e in entries)):
        subset = [e for e in entries if e['quarter'] == q]
        s = run_sim(subset)
        if s:
            s['period'] = q
            quarterly.append(s)
    report['quarterly'] = quarterly

    # 4. Parameter stability
    print('Part 4: Params + Funding...')
    param_results = []
    for sl in [0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]:
        for timeout in [48, 72, 96, 120, 144, 168]:
            s = run_sim(entries, sl=sl, timeout=timeout)
            if s:
                s['sl'] = sl
                s['timeout'] = timeout
                param_results.append(s)
    report['params'] = param_results

    # 5. Filters
    print('Part 5: Filters + Funding...')
    filter_results = []
    # Baseline
    s = run_sim(entries)
    if s:
        s['filter'] = 'No filter'
        s['threshold'] = None
        filter_results.append(s)

    for threshold in [-0.10, -0.05, -0.02, 0.0, 0.02, 0.05, 0.10]:
        filtered = [e for e in entries if e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
        s = run_sim(filtered)
        if s:
            s['filter'] = f'BTC 7d > {threshold*100:+.0f}%'
            s['threshold'] = threshold
            s['filtered_n'] = len(filtered)
            s['filter_pct'] = round(len(filtered)/len(entries)*100, 1)
            filter_results.append(s)
    report['filters'] = filter_results

    # 6. Filtered yearly
    print('Part 6: Filtered yearly + Funding...')
    filtered_yearly = []
    for yr in sorted(set(e['ts'].year for e in entries)):
        for threshold in [0.0, 0.02, 0.05]:
            subset = [e for e in entries if e['ts'].year == yr and e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
            s = run_sim(subset)
            if s:
                s['year'] = yr
                s['threshold'] = threshold
                s['filter'] = f'BTC 7d > {threshold*100:+.0f}%'
                filtered_yearly.append(s)
    report['filtered_yearly'] = filtered_yearly

    # Save JSON
    json_path = ROOT / 'reports/backtest_sl_only_funding_data.json'
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'Saved JSON: {json_path}')

    # Generate HTML
    print('Generating HTML...')
    html = generate_html(report)
    with open(OUT_HTML, 'w') as f:
        f.write(html)
    print(f'Saved HTML: {OUT_HTML}')


# ── HTML Generator ───────────────────────────────────────────────────

def generate_html(data):
    def vc(v, th=0):
        if isinstance(v, (int, float)):
            return 'pos' if v > th else ('neg' if v < th else 'zero')
        return ''

    def fund_vc(v):
        if isinstance(v, (int, float)):
            return 'pos' if v > 0.001 else ('neg' if v < -0.001 else 'zero')
        return ''

    def dual_cell(base_val, adj_val, fmt='{:+.2f}%', threshold=0):
        """Show base value → adjusted value with arrow."""
        b = fmt.format(base_val)
        a = fmt.format(adj_val)
        cls = vc(adj_val, threshold)
        if abs(adj_val - base_val) > 0.001:
            return f'<span class="{cls}">{b} → {a}</span>'
        return f'<span class="{cls}">{a}</span>'

    def funding_cell(val):
        cls = fund_vc(val)
        return f'<span class="{cls}">{val:+.3f}%</span>'

    # ── Slippage table ──
    slip_rows = []
    for s in data['slippage']:
        b, a = s['base'], s['adj']
        slip_rows.append([
            f"{s['slip_bps']}bp", f"{b['n']}",
            dual_cell(b['mean'], a['mean']),
            dual_cell(b['median'], a['median']),
            dual_cell(b['wr'], a['wr'], fmt='{:.1f}%'),
            dual_cell(b['pf'], a['pf'], fmt='{:.2f}', threshold=1.0),
            funding_cell(s['funding_mean']),
            f'{s["funding_total"]:+.1f}%',
        ])

    # ── Yearly table ──
    yr_rows = []
    for s in data['yearly']:
        b, a = s['base'], s['adj']
        yr_rows.append([
            s['period'], f'{b["n"]}',
            dual_cell(b['mean'], a['mean']),
            dual_cell(b['median'], a['median']),
            dual_cell(b['wr'], a['wr'], fmt='{:.1f}%'),
            dual_cell(b['pf'], a['pf'], fmt='{:.2f}', threshold=1.0),
            funding_cell(s['funding_mean']),
            f'{s["funding_total"]:+.1f}%',
        ])

    # ── Quarterly table ──
    q_rows = []
    for s in data['quarterly']:
        b, a = s['base'], s['adj']
        q_rows.append([
            s['period'], f'{b["n"]}',
            dual_cell(b['mean'], a['mean']),
            dual_cell(b['wr'], a['wr'], fmt='{:.1f}%'),
            dual_cell(b['pf'], a['pf'], fmt='{:.2f}', threshold=1.0),
            funding_cell(s['funding_mean']),
            f'{s["funding_total"]:+.1f}%',
        ])

    # ── Param heatmap (funding-adjusted) ──
    param_data = data['params']
    sl_vals = sorted(set(p['sl'] for p in param_data))
    to_vals = sorted(set(p['timeout'] for p in param_data))
    param_table = '<table><caption>Parameter Stability: Funding-Adjusted Mean Return (%)</caption>'
    param_table += '<tr><th>SL \\\\ Timeout</th>'
    for to in to_vals:
        param_table += f'<th>{to}h</th>'
    param_table += '</tr>'
    for sl in sl_vals:
        param_table += f'<tr><td><strong>{sl*100:.0f}%</strong></td>'
        for to in to_vals:
            match = [p for p in param_data if p['sl']==sl and p['timeout']==to]
            if match:
                p = match[0]
                adj_mean = p['adj']['mean']
                cls = vc(adj_mean)
                fund = p['funding_mean']
                param_table += f'<td class="{cls}">{adj_mean:+.2f}<br><small>F:{fund:+.3f}</small></td>'
            else:
                param_table += '<td>-</td>'
        param_table += '</tr>'
    param_table += '</table>'

    # ── Filter table ──
    filter_rows = []
    for s in data['filters']:
        b, a = s['base'], s['adj']
        n_str = f'{b["n"]}'
        if 'filtered_n' in s:
            n_str += f' ({s["filter_pct"]}%)'
        filter_rows.append([
            s['filter'], n_str,
            dual_cell(b['mean'], a['mean']),
            dual_cell(b['median'], a['median']),
            dual_cell(b['wr'], a['wr'], fmt='{:.1f}%'),
            dual_cell(b['pf'], a['pf'], fmt='{:.2f}', threshold=1.0),
            funding_cell(s['funding_mean']),
            f'{s["funding_total"]:+.1f}%',
        ])

    # ── Filtered yearly ──
    filt_yr_rows = []
    for s in data['filtered_yearly']:
        b, a = s['base'], s['adj']
        filt_yr_rows.append([
            str(s['year']), s['filter'], f'{b["n"]}',
            dual_cell(b['mean'], a['mean']),
            dual_cell(b['wr'], a['wr'], fmt='{:.1f}%'),
            dual_cell(b['pf'], a['pf'], fmt='{:.2f}', threshold=1.0),
            funding_cell(s['funding_mean']),
            f'{s["funding_total"]:+.1f}%',
        ])

    # ── Funding summary ──
    baseline = [s for s in data['filters'] if s['filter'] == 'No filter']
    if baseline:
        bl = baseline[0]
        fund_summary = f'''
<div class="key-finding">
<strong>资金费率影响：</strong>
<ul>
<li>平均每笔交易 funding: {bl["funding_mean"]:+.4f}%</li>
<li>累计 funding 收益: {bl["funding_total"]:+.1f}%</li>
<li>原始 Mean: {bl["base"]["mean"]:+.2f}% → 含 funding Mean: {bl["adj"]["mean"]:+.2f}%</li>
<li>原始 PF: {bl["base"]["pf"]} → 含 funding PF: {bl["adj"]["pf"]}</li>
</ul>
<p><em>正值 = 多头从负 funding 中获益（空头付费给多头）</em></p>
</div>'''
    else:
        fund_summary = ''

    # ── Funding by year detail ──
    fund_yr_detail = '<table><caption>资金费率逐年影响</caption>'
    fund_yr_detail += '<tr><th>年份</th><th>交易数</th><th>平均 Funding</th><th>累计 Funding</th><th>原始 Mean</th><th>含 Funding Mean</th><th>差值</th></tr>'
    for s in data['yearly']:
        b, a = s['base'], s['adj']
        diff = a['mean'] - b['mean']
        fund_yr_detail += f'<tr><td>{s["period"]}</td><td>{b["n"]}</td>'
        fund_yr_detail += f'<td>{funding_cell(s["funding_mean"])}</td>'
        fund_yr_detail += f'<td>{s["funding_total"]:+.1f}%</td>'
        fund_yr_detail += f'<td>{b["mean"]:+.2f}%</td>'
        fund_yr_detail += f'<td class="{vc(a["mean"])}">{a["mean"]:+.2f}%</td>'
        fund_yr_detail += f'<td class="{vc(diff)}">{diff:+.3f}%</td></tr>'
    fund_yr_detail += '</table>'

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    headers = ['指标','N','Mean','Median','WR','PF','Funding/trade','累计Funding']
    q_headers = ['季度','N','Mean','WR','PF','Funding/trade','累计Funding']
    fy_headers = ['年份','过滤条件','N','Mean','WR','PF','Funding/trade','累计Funding']

    def table(hdrs, rows, caption=''):
        hdr = '<tr>' + ''.join(f'<th>{h}</th>' for h in hdrs) + '</tr>'
        body = ''
        for row in rows:
            body += '<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>'
        return f'<table><caption>{caption}</caption>{hdr}{body}</table>'

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SL-Only + Funding Rate — Backtest Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.7; padding: 20px; max-width: 1400px; margin: 0 auto; }}
h1 {{ color: #58a6ff; margin: 20px 0 10px; font-size: 1.8em; }}
h2 {{ color: #79c0ff; margin: 30px 0 10px; font-size: 1.3em; border-bottom: 1px solid #21262d; padding-bottom: 5px; }}
h3 {{ color: #d2a8ff; margin: 20px 0 8px; font-size: 1.1em; }}
.summary {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin: 10px 0; }}
.key-finding {{ background: #1a1f2e; border-left: 4px solid #58a6ff; padding: 12px 16px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
.warning {{ background: #2d1b1b; border-left: 4px solid #f85149; padding: 12px 16px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
.good {{ background: #1b2d1b; border-left: 4px solid #3fb950; padding: 12px 16px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
.info {{ background: #1a2332; border-left: 4px solid #58a6ff; padding: 12px 16px; margin: 10px 0; border-radius: 0 8px 8px 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 0.9em; }}
th {{ background: #161b22; color: #8b949e; padding: 8px 12px; text-align: left; border-bottom: 2px solid #30363d; font-weight: 600; }}
td {{ padding: 6px 12px; border-bottom: 1px solid #21262d; }}
tr:hover {{ background: #161b22; }}
caption {{ text-align: left; font-weight: 600; color: #8b949e; padding: 8px 0; font-size: 0.95em; }}
.pos {{ color: #3fb950; font-weight: 600; }}
.neg {{ color: #f85149; font-weight: 600; }}
.zero {{ color: #8b949e; }}
small {{ color: #8b949e; font-size: 0.85em; }}
.meta {{ color: #8b949e; font-size: 0.85em; margin: 5px 0; }}
ul {{ padding-left: 20px; }}
li {{ margin: 4px 0; }}
</style>
</head>
<body>

<h1>📊 SL-Only Strategy + Funding Rate Impact</h1>
<p class="meta">Generated: {now} | Universe: v1.6a event overlay (1951 trades, 535 symbols) | Base fee: 4bps/side | Funding: Binance 8h rate</p>

<div class="summary">
<p><strong>说明：</strong>所有表格中 <strong>Mean/PF/WR</strong> 列显示 <code>原始值 → 含Funding值</code>。Funding/trade 列显示每笔交易平均 funding 收益（正值=多头获益）。策略为 LONG only，8% 止损，96h 超时退出。</p>
</div>

{fund_summary}

<h2>1. 资金费率逐年影响</h2>
{fund_yr_detail}

<h2>2. 滑点敏感度（含 Funding）</h2>
{table(headers, slip_rows)}

<h2>3. 时间稳定性（含 Funding）</h2>
{table(headers, yr_rows)}

<h3>按季度</h3>
{table(q_headers, q_rows)}

<h2>4. 参数稳定性（Funding 调整后 Mean）</h2>
{param_table}

<h2>5. 牛熊过滤器（含 Funding）</h2>
{table(headers, filter_rows)}

<h2>6. 过滤后逐年（含 Funding）</h2>
{table(fy_headers, filt_yr_rows)}

</body>
</html>'''


if __name__ == '__main__':
    main()
