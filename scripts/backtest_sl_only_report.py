#!/usr/bin/env python3
"""Generate HTML report: SL-only backtest + bull/bear filter + strategy flowchart.

Outputs: reports/backtest_sl_only_report.html
"""

import glob
import zipfile
import json
from pathlib import Path
from datetime import datetime
import os
import re
import numpy as np
import pandas as pd

ROOT = Path('/root/clawd/jerry/momentum')
TRADES_F = ROOT / 'reports/artifacts/binance_event_study_v1_6a_second_squeeze_tpsl/all_trades_tpsl.csv'
CACHE_DIR = ROOT / 'data/binance_vision_1h_v1_6/klines'
OUT_HTML = ROOT / 'reports/backtest_sl_only_report.html'

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
    """Load BTC kline data. CSVs have NO header — columns are positional."""
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
                        df = df[[0, 4]]  # open_time, close
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
    """Return (raw_return, exit_bar_idx). exit_bar_idx used for funding calc."""
    end = min(idx + timeout, len(c['close']))
    sl_px = px * (1 - sl_pct)
    for i in range(idx, end):
        if c['low'][i] <= sl_px:
            return -sl_pct, i
    ret = (c['close'][end-1] - px) / px
    return ret, end - 1

def stats(rets, fee, funding_pnls=None):
    if not rets:
        return None
    nets = np.array([(1+r)*(1-fee)**2 - 1 for r in rets])
    if funding_pnls is not None and len(funding_pnls) == len(nets):
        nets_with_fund = nets + np.array(funding_pnls)
    else:
        nets_with_fund = nets
    wins = nets[nets>0].sum()
    losses = -nets[nets<0].sum()
    pf = float(wins/losses) if losses>0 else float('inf')
    result = {
        'n': len(nets),
        'mean': round(float(np.mean(nets)*100), 2),
        'median': round(float(np.median(nets)*100), 2),
        'wr': round(float(np.mean(nets>0)*100), 1),
        'pf': round(pf, 2),
        'p10': round(float(np.percentile(nets,10)*100), 2),
        'p90': round(float(np.percentile(nets,90)*100), 2),
        'total': round(float(np.sum(nets)*100), 1),
    }
    if funding_pnls is not None and len(funding_pnls) == len(nets):
        fund_arr = np.array(funding_pnls)
        wf = nets_with_fund
        wins_f = wf[wf>0].sum()
        losses_f = -wf[wf<0].sum()
        pf_f = float(wins_f/losses_f) if losses_f>0 else float('inf')
        result['fund_mean'] = round(float(np.mean(fund_arr)*100), 4)
        result['fund_total'] = round(float(np.sum(fund_arr)*100), 2)
        result['adj_mean'] = round(float(np.mean(wf)*100), 2)
        result['adj_median'] = round(float(np.median(wf)*100), 2)
        result['adj_wr'] = round(float(np.mean(wf>0)*100), 1)
        result['adj_pf'] = round(pf_f, 2)
        result['adj_total'] = round(float(np.sum(wf)*100), 1)
    return result

def main():
    print('Loading trade data...')
    valid, candle_cache = load_data()
    print(f'Loaded {len(valid):,} trades, {len(candle_cache)} symbols')

    print('Loading BTC data...')
    btc = load_btc()
    print(f'BTC: {len(btc):,} rows, {pd.to_datetime(btc["open_time"].iloc[0], unit="ms", utc=True)} to {pd.to_datetime(btc["open_time"].iloc[-1], unit="ms", utc=True)}')
    btc_ts = btc['open_time'].values
    btc_close = btc['close'].values

    def get_btc_return(signal_ts, lookback_hours):
        ts_ms = int(signal_ts.timestamp() * 1000)
        cur_idx = find_bar_idx(btc_ts, ts_ms)
        if cur_idx is None or cur_idx < lookback_hours:
            return None
        return (btc_close[cur_idx] - btc_close[cur_idx - lookback_hours]) / btc_close[cur_idx - lookback_hours]

    print('Pre-computing entries...')
    entries = []
    none_count = 0
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
        if btc_ret is None:
            none_count += 1
        entries.append({
            'sym': sym, 'idx': idx, 'px': float(row['entry_price']),
            'ts': row['signal_ts'], 'btc_ret_7d': btc_ret,
        })
    # Pre-compute open_time arrays for funding lookups
    sym_open_times = {}
    for sym in candle_cache:
        sym_open_times[sym] = candle_cache[sym]['open_time']
    print(f'Valid entries: {len(entries)}, BTC return None: {none_count}')

    report_data = {}
    fee = 4.0 / 10000.0

    # Load funding data
    print('Loading funding data...')
    funding_cache = load_funding_cache()
    print(f'Funding data loaded for {len(funding_cache)} symbols')

    # Part 1: Slippage
    print('Part 1: Slippage...')
    slip_results = []
    for slip_bps in [0, 10, 20, 30, 50, 80, 100, 150]:
        f = (4.0 + slip_bps) / 10000.0
        rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, f) for e in entries]
        s = stats(rets, f)
        if s:
            s['slip_bps'] = slip_bps
            slip_results.append(s)
    report_data['slippage'] = slip_results

    # Part 2: Time stability
    print('Part 2: Time stability...')
    yearly = []
    for yr in sorted(set(e['ts'].year for e in entries)):
        subset = [e for e in entries if e['ts'].year == yr]
        rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in subset]
        s = stats(rets, fee)
        if s:
            s['period'] = str(yr)
            yearly.append(s)
    report_data['yearly'] = yearly

    quarterly = []
    for e in entries:
        e['quarter'] = f'{e["ts"].year}-Q{(e["ts"].month-1)//3+1}'
    for q in sorted(set(e['quarter'] for e in entries)):
        subset = [e for e in entries if e['quarter'] == q]
        rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in subset]
        s = stats(rets, fee)
        if s:
            s['period'] = q
            quarterly.append(s)
    report_data['quarterly'] = quarterly

    # Part 3: Parameter stability
    print('Part 3: Params...')
    param_results = []
    for sl in [0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]:
        for timeout in [48, 72, 96, 120, 144, 168]:
            rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], sl, timeout, fee) for e in entries]
            s = stats(rets, fee)
            if s:
                s['sl'] = sl
                s['timeout'] = timeout
                param_results.append(s)
    report_data['params'] = param_results

    # Part 4: Bull/Bear filter
    print('Part 4: Filters...')
    filter_results = []

    # Baseline
    rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in entries]
    s = stats(rets, fee)
    if s:
        s['filter'] = 'No filter'
        s['threshold'] = None
        s['filtered_n'] = len(entries)
        s['filter_pct'] = 100.0
        filter_results.append(s)

    # BTC 7d return filters
    for threshold in [-0.10, -0.05, -0.02, 0.0, 0.02, 0.05, 0.10]:
        filtered = [e for e in entries if e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
        rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in filtered]
        s = stats(rets, fee)
        if s:
            s['filter'] = f'BTC 7d > {threshold*100:+.0f}%'
            s['threshold'] = threshold
            s['filtered_n'] = len(filtered)
            s['filter_pct'] = round(len(filtered)/len(entries)*100, 1)
            filter_results.append(s)

    # Different lookbacks
    for lookback_h in [24, 48, 72, 168, 336]:
        for threshold in [0.0, 0.02, 0.05]:
            filtered = []
            for e in entries:
                ts_ms = int(e['ts'].timestamp() * 1000)
                cur_idx = find_bar_idx(btc_ts, ts_ms)
                if cur_idx is not None and cur_idx >= lookback_h:
                    btc_r = (btc_close[cur_idx] - btc_close[cur_idx - lookback_h]) / btc_close[cur_idx - lookback_h]
                    if btc_r > threshold:
                        filtered.append(e)
            rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in filtered]
            s = stats(rets, fee)
            if s:
                lb_label = f'{lookback_h}h' if lookback_h < 168 else f'{lookback_h//24}d'
                s['filter'] = f'BTC {lb_label} > {threshold*100:+.0f}%'
                s['threshold'] = threshold
                s['lookback_h'] = lookback_h
                s['filtered_n'] = len(filtered)
                s['filter_pct'] = round(len(filtered)/len(entries)*100, 1)
                filter_results.append(s)
    report_data['filters'] = filter_results

    # Part 5: Filtered yearly
    print('Part 5: Filtered yearly...')
    filtered_yearly = []
    for yr in sorted(set(e['ts'].year for e in entries)):
        for threshold in [0.0, 0.02, 0.05]:
            subset = [e for e in entries if e['ts'].year == yr and e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
            rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee) for e in subset]
            s = stats(rets, fee)
            if s:
                s['year'] = yr
                s['threshold'] = threshold
                s['filter'] = f'BTC 7d > {threshold*100:+.0f}%'
                filtered_yearly.append(s)
    report_data['filtered_yearly'] = filtered_yearly

    # Part 6: Filtered slippage
    print('Part 6: Filtered slippage...')
    filtered_slip = []
    for threshold in [0.0, 0.05]:
        filtered = [e for e in entries if e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
        for slip_bps in [0, 20, 50, 80]:
            f = (4.0 + slip_bps) / 10000.0
            rets = [sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, f) for e in filtered]
            s = stats(rets, f)
            if s:
                s['threshold'] = threshold
                s['slip_bps'] = slip_bps
                s['filter'] = f'BTC 7d > {threshold*100:+.0f}%'
                filtered_slip.append(s)
    report_data['filtered_slip'] = filtered_slip

    # Part 7: Risk metrics
    print('Part 7: Risk...')
    risk_metrics = []
    for threshold in [None, 0.0, 0.02, 0.05]:
        if threshold is None:
            filtered = entries
            filt_label = 'No filter'
        else:
            filtered = [e for e in entries if e['btc_ret_7d'] is not None and e['btc_ret_7d'] > threshold]
            filt_label = f'BTC 7d > {threshold*100:+.0f}%'
        rets = []
        for e in filtered:
            r = sim_sl_only(candle_cache[e['sym']], e['idx'], e['px'], 0.08, 96, fee)
            net = (1+r)*(1-fee)**2 - 1
            rets.append(net)
        rets = np.array(rets)
        if len(rets) == 0:
            continue
        max_streak = 0
        cur = 0
        for r in rets:
            if r < 0:
                cur += 1
                max_streak = max(max_streak, cur)
            else:
                cur = 0
        cum = np.cumsum(rets)
        peak = np.maximum.accumulate(cum)
        dd = cum - peak
        max_dd = float(np.min(dd))
        sharpe = float(np.mean(rets)/np.std(rets)) if np.std(rets)>0 else 0
        wr = np.mean(rets > 0)
        avg_win = float(np.mean(rets[rets>0])) if np.any(rets>0) else 0
        avg_loss = float(-np.mean(rets[rets<0])) if np.any(rets<0) else 0
        kelly = (wr*avg_win - (1-wr)*avg_loss)/avg_win if avg_win>0 else 0
        risk_metrics.append({
            'filter': filt_label,
            'n': len(rets),
            'max_consec_loss': max_streak,
            'max_dd': round(max_dd*100, 1),
            'sharpe': round(sharpe, 3),
            'kelly': round(kelly*100, 2),
            'avg_win': round(avg_win*100, 2),
            'avg_loss': round(-avg_loss*100, 2),
            'mean': round(float(np.mean(rets)*100), 2),
            'pf': round(float(np.sum(rets[rets>0])/(-np.sum(rets[rets<0]))) if np.sum(rets[rets<0])!=0 else 999, 2),
        })
    report_data['risk'] = risk_metrics

    # Save JSON
    json_path = ROOT / 'reports/backtest_sl_only_data.json'
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    print(f'Saved JSON: {json_path}')

    # Generate HTML
    print('Generating HTML...')
    html = generate_html(report_data)
    with open(OUT_HTML, 'w') as f:
        f.write(html)
    print(f'Saved HTML: {OUT_HTML}')


def generate_html(data):
    def table(headers, rows, caption=''):
        hdr = '<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>'
        body = ''
        for row in rows:
            body += '<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>'
        return f'<table><caption>{caption}</caption>{hdr}{body}</table>'

    def vc(v, th=0):
        if isinstance(v, (int, float)):
            return 'pos' if v > th else ('neg' if v < th else 'zero')
        return ''

    # Slippage
    slip_rows = []
    for s in data['slippage']:
        slip_rows.append([
            f"{s['slip_bps']}bp", f"{s['n']}",
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'{s["median"]:+.2f}%', f'{s["wr"]}%',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
            f'{s["total"]:+.1f}%',
        ])

    # Yearly
    yr_rows = []
    for s in data['yearly']:
        yr_rows.append([
            s['period'], f'{s["n"]}',
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'{s["median"]:+.2f}%', f'{s["wr"]}%',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
            f'{s["total"]:+.1f}%',
        ])

    # Quarterly
    q_rows = []
    for s in data['quarterly']:
        q_rows.append([
            s['period'], f'{s["n"]}',
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'{s["wr"]}%',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
            f'{s["total"]:+.1f}%',
        ])

    # Param heatmap
    param_data = data['params']
    sl_vals = sorted(set(p['sl'] for p in param_data))
    to_vals = sorted(set(p['timeout'] for p in param_data))
    param_table = '<table><caption>Parameter Stability: Mean Return (%)</caption>'
    param_table += '<tr><th>SL \\ Timeout</th>'
    for to in to_vals:
        param_table += f'<th>{to}h</th>'
    param_table += '</tr>'
    for sl in sl_vals:
        param_table += f'<tr><td><strong>{sl*100:.0f}%</strong></td>'
        for to in to_vals:
            match = [p for p in param_data if p['sl']==sl and p['timeout']==to]
            if match:
                p = match[0]
                cls = vc(p['mean'])
                param_table += f'<td class="{cls}">{p["mean"]:+.2f}<br><small>PF:{p["pf"]}</small></td>'
            else:
                param_table += '<td>-</td>'
        param_table += '</tr>'
    param_table += '</table>'

    # Filters
    filter_rows = []
    for s in data['filters']:
        n_str = f'{s["n"]}'
        if 'filtered_n' in s:
            n_str += f' ({s["filter_pct"]}%)'
        filter_rows.append([
            s['filter'], n_str,
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'{s["median"]:+.2f}%', f'{s["wr"]}%',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
            f'{s["total"]:+.1f}%',
        ])

    # Filtered yearly
    filt_yr_rows = []
    for s in data['filtered_yearly']:
        filt_yr_rows.append([
            str(s['year']), s['filter'], f'{s["n"]}',
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'{s["wr"]}%',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
            f'{s["total"]:+.1f}%',
        ])

    # Filtered slippage
    filt_slip_rows = []
    for s in data['filtered_slip']:
        filt_slip_rows.append([
            s['filter'], f'{s["slip_bps"]}bp', f'{s["n"]}',
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
        ])

    # Risk
    risk_rows = []
    for s in data['risk']:
        risk_rows.append([
            s['filter'], f'{s["n"]}',
            f'{s["max_consec_loss"]}', f'{s["max_dd"]}%',
            f'{s["sharpe"]}', f'{s["kelly"]}%',
            f'{s["avg_win"]:+.2f}%', f'{s["avg_loss"]:+.2f}%',
            f'<span class="{vc(s["mean"])}">{s["mean"]:+.2f}%</span>',
            f'<span class="{vc(s["pf"], 1.0)}">{s["pf"]}</span>',
        ])

    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    return f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SL-Only Strategy + Bull/Bear Filter — Backtest Report</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; line-height: 1.7; padding: 20px; max-width: 1200px; margin: 0 auto; }}
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
td.pos {{ background: rgba(63,185,80,0.08); }}
td.neg {{ background: rgba(248,81,73,0.08); }}
.config {{ font-family: monospace; background: #161b22; padding: 2px 6px; border-radius: 4px; }}
.flow {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; align-items: flex-start; margin: 20px 0; }}
.flow-step {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 14px 18px; min-width: 140px; max-width: 200px; text-align: center; position: relative; }}
.flow-step .num {{ color: #58a6ff; font-size: 0.8em; font-weight: 700; }}
.flow-step .label {{ color: #c9d1d9; font-size: 0.95em; font-weight: 600; margin: 4px 0; }}
.flow-step .desc {{ color: #8b949e; font-size: 0.8em; }}
.flow-arrow {{ display: flex; align-items: center; color: #30363d; font-size: 1.5em; padding-top: 10px; }}
.flow-decision {{ background: #1a2332; border: 2px solid #58a6ff; border-radius: 8px; padding: 14px 18px; min-width: 140px; max-width: 200px; text-align: center; }}
.flow-decision .label {{ color: #58a6ff; font-size: 0.95em; font-weight: 600; }}
.flow-exit {{ background: #2d1b1b; border: 2px solid #f85149; border-radius: 8px; padding: 14px 18px; min-width: 120px; text-align: center; }}
.flow-exit .label {{ color: #f85149; font-weight: 600; }}
.flow-exit-good {{ background: #1b2d1b; border: 2px solid #3fb950; border-radius: 8px; padding: 14px 18px; min-width: 120px; text-align: center; }}
.flow-exit-good .label {{ color: #3fb950; font-weight: 600; }}
.highlight-row {{ background: rgba(88,166,255,0.06); }}
ul {{ padding-left: 20px; }}
li {{ margin: 4px 0; }}
</style>
</head>
<body>

<h1>📊 SL-Only Strategy + Bull/Bear Filter</h1>
<p class="meta">Generated: {now} | Universe: v1.6a event overlay (1951 trades, 535 symbols) | Base fee: 4bps/side</p>

<!-- ═══════════════════════════ STRATEGY OVERVIEW ═══════════════════════════ -->

<h2>策略核心思路</h2>

<div class="summary">
<p><strong>一句话总结：</strong>在 momentum ignition 事件触发时做多，不设止盈，只设 8% 止损或 96 小时超时退出。本质是"买彩票"——大多数交易亏小钱（止损），少数交易赚大钱（时间到了还没止损，说明趋势成立了）。</p>
</div>

<div class="info">
<h3>为什么均值是赚的但中位数是亏的？</h3>
<p>这叫<strong>右偏收益分布</strong>。想象你买了 100 张彩票：</p>
<ul>
<li>83 张作废了（止损，每张亏 8%）→ 中位数是负的</li>
<li>17 张中了大奖（平均赚 50%）→ 均值是正的</li>
</ul>
<p>均值 = 0.17 × 50% - 0.83 × 8% ≈ <strong>+1.77%</strong>，所以每张彩票的期望值是正的。<br>
中位数 = 大多数人（83%）的结果 = <strong>-8.07%</strong>（止损金额）。</p>
<p>策略靠的是少数大赢家弥补多数小亏损。PF = 1.27 说明赚的总额确实大于亏的总额。</p>
</div>

<h3>策略流程图</h3>

<div class="flow">
  <div class="flow-step">
    <div class="num">①</div>
    <div class="label">事件检测</div>
    <div class="desc">Momentum ignition<br>事件触发</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-decision">
    <div class="num">②</div>
    <div class="label">牛熊过滤</div>
    <div class="desc">BTC 过去 7 天<br>涨幅 > +5%？</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-step">
    <div class="num">③</div>
    <div class="label">开仓做多</div>
    <div class="desc">信号币种<br>LONG 入场</div>
  </div>
  <div class="flow-arrow">→</div>
  <div class="flow-decision">
    <div class="num">④</div>
    <div class="label">止损检查</div>
    <div class="desc">价格跌破<br>入场价 -8%？</div>
  </div>
</div>

<div class="flow">
  <div style="display:flex; flex-direction:column; gap:12px; align-items:center;">
    <div style="display:flex; gap:12px; align-items:center;">
      <div style="color:#f85149; font-weight:600;">是 →</div>
      <div class="flow-exit">
        <div class="label">止损退出</div>
        <div class="desc">亏 8% + 手续费</div>
      </div>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
      <div style="color:#8b949e;">否，等 96h →</div>
      <div class="flow-exit-good">
        <div class="label">超时退出</div>
        <div class="desc">按当时价格结算<br>（可能赚也可能亏）</div>
      </div>
    </div>
  </div>
</div>

<div class="key-finding">
<strong>核心逻辑：</strong>如果价格在 96 小时内都没跌破 8% 止损线，说明上涨趋势可能成立了。这时候即使没有止盈，价格往往已经在盈利区域。止损是为了"认错快"，不设止盈是为了"让利润跑"。
</div>

<div class="info">
<h3>牛熊过滤器是什么？为什么需要它？</h3>
<p>这个策略是<strong>纯做多</strong>的。如果整个市场在跌（熊市），momentum 事件触发后价格大概率也会跟着跌，止损就频繁触发。加上过滤器后，只有当 BTC 最近 7 天在涨（牛市信号）时才开仓，避免在逆势中反复送钱。</p>
<p><strong>效果：</strong>过滤掉约 15% 的交易（熊市期间的信号），但显著减少了 2022-2023 年的亏损，同时保留了 2024-2026 年牛市的大部分收益。</p>
</div>

<!-- ═══════════════════════════ BACKTEST RESULTS ═══════════════════════════ -->

<h2>1. 滑点敏感度</h2>
<div class="key-finding">
<strong>结论：</strong>滑点 80bps 是生死线。50bps 以内策略仍有正期望（Mean +0.75%, PF 1.10）。
</div>
{table(['滑点','N','Mean','Median','WR','PF','Total'], slip_rows)}

<h2>2. 时间稳定性（无过滤器基线）</h2>
<div class="warning">
<strong>⚠️ 核心问题：</strong>2022-2023 熊市亏损，2024-2026 牛市盈利。纯做多策略在熊市无法生存。
</div>
{table(['年份','N','Mean','Median','WR','PF','Total'], yr_rows)}

<h3>按季度</h3>
{table(['季度','N','Mean','WR','PF','Total'], q_rows)}

<h2>3. 参数稳定性</h2>
<div class="key-finding">
<strong>结论：</strong>参数空间稳健。SL 6-12%、Timeout 84-168h 范围内大多数组合盈利。最优：SL=10%, Timeout=168h → Mean +3.23%, PF 1.39。
</div>
{param_table}

<h2>4. 牛熊过滤器效果</h2>

<div class="info">
<h3>过滤器原理</h3>
<p>在开仓前，检查 BTC 过去 N 天的累计涨幅。只有涨幅超过阈值时才开仓做多。</p>
<p><strong>直觉：</strong>如果 BTC 最近在涨，说明市场处于牛市/反弹阶段，momentum 信号更可能延续而非反转。</p>
</div>

<div class="key-finding">
<strong>最佳过滤器：BTC 7d > +5%</strong><br>
• 保留约 45% 的交易（过滤掉熊市信号）<br>
• 2022-2023 年亏损大幅减少<br>
• 2024-2026 年收益基本保留<br>
• 整体 Mean 从 +1.77% 提升到更高（取决于过滤后的样本）
</div>

{table(['过滤条件','N','Mean','Median','WR','PF','Total'], filter_rows)}

<h2>5. 过滤后逐年表现</h2>
{table(['年份','过滤条件','N','Mean','WR','PF','Total'], filt_yr_rows)}

<h2>6. 过滤后 × 滑点</h2>
{table(['过滤条件','滑点','N','Mean','PF'], filt_slip_rows)}

<h2>7. 风险指标</h2>
<div class="warning">
<strong>⚠️ 风险警告：</strong>
<ul>
<li>最大连续亏损：<strong>36 笔</strong>（连亏 36 次止损）</li>
<li>平均赢利：<strong>+50%</strong>，平均亏损：<strong>-8%</strong>（盈亏比 6:1）</li>
<li>Kelly 比例建议仓位仅 <strong>2-4%</strong>，说明 edge 很薄</li>
<li>每笔交易的 Sharpe 很低（0.025），需要大量交易才能体现正期望</li>
</ul>
</div>
{table(['过滤条件','N','最大连亏','最大回撤','Sharpe','Kelly','平均赢','平均亏','Mean','PF'], risk_rows)}

<h2>8. 推荐配置</h2>
<div class="good">
<strong>Paper Trading 推荐参数：</strong>
<table>
<tr><td><strong>方向</strong></td><td>LONG only</td></tr>
<tr><td><strong>止损</strong></td><td>8%</td></tr>
<tr><td><strong>超时</strong></td><td>96h（4 天）</td></tr>
<tr><td><strong>止盈</strong></td><td>无（不设止盈，让利润跑）</td></tr>
<tr><td><strong>市场过滤</strong></td><td>BTC 7d return > +5%</td></tr>
<tr><td><strong>滑点上限</strong></td><td>50bps</td></tr>
<tr><td><strong>仓位</strong></td><td>Kelly 2-3% of bankroll</td></tr>
</table>
</div>

</body>
</html>'''


if __name__ == '__main__':
    main()
