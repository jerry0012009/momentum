#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'rank32b_slope_floor_continuation_clean_replication.html'
EXEC_SCRIPT = ROOT / 'scripts' / 'build_rank32b_execution_probe.py'
EXT_SCRIPT = ROOT / 'scripts' / 'build_rank32b_extended_history_probe.py'

DEFAULT_SYMBOLS = [
    'BTCUSDT','ETHUSDT','SOLUSDT','LTCUSDT','NEARUSDT','UNIUSDT','XRPUSDT','DOGEUSDT','BNBUSDT',
    'ADAUSDT','AVAXUSDT','LINKUSDT','BCHUSDT','DOTUSDT','ZECUSDT','AAVEUSDT','SUIUSDT','WLDUSDT'
]
DEFAULT_DAYS = 365
DEFAULT_TAG = 'live_parity_shortlist18_1y'
DEFAULT_TP = 1.25
DEFAULT_SL = 1.0
DEFAULT_TIMEOUT_15M = 8
DEFAULT_MAX_CONCURRENT = 1
MARKER_ID = 'rank32b-live-parity-universe'


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


exec_mod = load_module(EXEC_SCRIPT, 'rank32b_exec_mod_live_parity')
ext_mod = load_module(EXT_SCRIPT, 'rank32b_ext_mod_live_parity')


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def num(v: float | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
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


def build_asset_map(symbols_csv: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in symbols_csv.split(','):
        symbol = raw.strip().upper()
        if not symbol:
            continue
        if not symbol.endswith('USDT'):
            raise ValueError(f'unsupported symbol {symbol}: expected *USDT perpetual symbol')
        out[symbol.replace('USDT', '-USD')] = symbol
    if not out:
        raise ValueError('no symbols provided')
    return out


def simulate_atr_oco_exit(sub_df: pd.DataFrame, fill_idx: int, fill_px: float, direction_sign: int, atr_value: float, tp_mult: float, sl_mult: float, timeout_15m_bars: int) -> dict[str, object] | None:
    if not np.isfinite(atr_value) or atr_value <= 0:
        return None
    timeout_5m_bars = int(timeout_15m_bars * 3)
    end_idx = min(len(sub_df) - 1, fill_idx + timeout_5m_bars - 1)
    target_px = float(fill_px + direction_sign * tp_mult * atr_value)
    stop_px = float(fill_px - direction_sign * sl_mult * atr_value)

    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        if direction_sign > 0:
            hit_tp = float(bar['high']) >= target_px
            hit_sl = float(bar['low']) <= stop_px
        else:
            hit_tp = float(bar['low']) <= target_px
            hit_sl = float(bar['high']) >= stop_px

        if hit_tp and hit_sl:
            return {
                'exit_idx': int(idx),
                'exit_ts': pd.to_datetime(bar['timestamp'], utc=True),
                'exit_px': stop_px,
                'exit_fee_bps': exec_mod.TAKER_FEE_BPS,
                'exit_maker': 0,
                'exit_type': 'conflict_stop_first',
                'target_hit': 0,
                'stop_hit': 1,
                'same_bar_conflict': 1,
                'hold_minutes': int((idx - fill_idx + 1) * 5),
            }
        if hit_tp:
            return {
                'exit_idx': int(idx),
                'exit_ts': pd.to_datetime(bar['timestamp'], utc=True),
                'exit_px': target_px,
                'exit_fee_bps': exec_mod.MAKER_FEE_BPS,
                'exit_maker': 1,
                'exit_type': 'target_limit',
                'target_hit': 1,
                'stop_hit': 0,
                'same_bar_conflict': 0,
                'hold_minutes': int((idx - fill_idx + 1) * 5),
            }
        if hit_sl:
            return {
                'exit_idx': int(idx),
                'exit_ts': pd.to_datetime(bar['timestamp'], utc=True),
                'exit_px': stop_px,
                'exit_fee_bps': exec_mod.TAKER_FEE_BPS,
                'exit_maker': 0,
                'exit_type': 'stop_loss',
                'target_hit': 0,
                'stop_hit': 1,
                'same_bar_conflict': 0,
                'hold_minutes': int((idx - fill_idx + 1) * 5),
            }

    bar = sub_df.iloc[end_idx]
    return {
        'exit_idx': int(end_idx),
        'exit_ts': pd.to_datetime(bar['timestamp'], utc=True),
        'exit_px': float(bar['close']),
        'exit_fee_bps': exec_mod.TAKER_FEE_BPS,
        'exit_maker': 0,
        'exit_type': 'timeout_close',
        'target_hit': 0,
        'stop_hit': 0,
        'same_bar_conflict': 0,
        'hold_minutes': int((end_idx - fill_idx + 1) * 5),
    }


def simulate_candidates(asset_map: dict[str, str], days: int, tp_mult: float, sl_mult: float, timeout_15m: int, refresh: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidate_rows: list[dict[str, object]] = []
    meta_rows: list[dict[str, object]] = []
    for asset, symbol in asset_map.items():
        bars_15m = exec_mod.perp_mod.load_or_fetch_perp_bars(symbol, days=days, refresh=refresh)
        bars_5m = exec_mod.load_or_fetch_perp_5m(symbol, days=days, refresh=refresh)
        frame = ext_mod.build_rank32b_frame_from_bars(asset, bars_15m)
        frame['atr14'] = exec_mod.compute_atr(frame)
        signals = exec_mod.build_signal_trades(frame, asset)
        sub_df = bars_5m.copy().sort_values('timestamp').reset_index(drop=True)
        ts_array = sub_df['timestamp'].to_numpy(dtype='datetime64[ns]')
        kept = 0
        for _, trade in signals.iterrows():
            entry_ts = pd.to_datetime(trade['entry_ts'], utc=True)
            direction_sign = int(trade['direction_sign'])
            entry_res = exec_mod.simulate_entry(sub_df, ts_array, entry_ts, direction_sign, entry_style='taker', entry_offset_bps=0.0, ttl_bars=exec_mod.ENTRY_TTL_5M_BARS)
            if entry_res is None:
                continue
            exit_res = simulate_atr_oco_exit(sub_df, int(entry_res['fill_idx']), float(entry_res['fill_px']), direction_sign, float(trade['atr14_entry']), tp_mult, sl_mult, timeout_15m)
            if exit_res is None:
                continue
            gross_ret = exec_mod.gross_return(float(entry_res['fill_px']), float(exit_res['exit_px']), direction_sign)
            candidate_rows.append({
                'asset': asset,
                'symbol': symbol,
                'event_ts': pd.to_datetime(trade['event_ts'], utc=True),
                'entry_ts': pd.to_datetime(entry_res['fill_ts'], utc=True),
                'exit_ts': pd.to_datetime(exit_res['exit_ts'], utc=True),
                'direction': str(trade['direction']),
                'direction_sign': direction_sign,
                'slope_strength': float(frame.iloc[int(trade['signal_idx'])]['slope_strength']) if 'slope_strength' in frame.columns else np.nan,
                'atr14_entry': float(trade['atr14_entry']),
                'entry_price': float(entry_res['fill_px']),
                'exit_price': float(exit_res['exit_px']),
                'gross_ret': gross_ret,
                'net_ret': exec_mod.apply_fees(gross_ret, float(entry_res['entry_fee_bps']), float(exit_res['exit_fee_bps'])),
                'entry_maker': int(entry_res['entry_maker']),
                'exit_maker': int(exit_res['exit_maker']),
                'target_hit': int(exit_res['target_hit']),
                'stop_hit': int(exit_res['stop_hit']),
                'same_bar_conflict': int(exit_res['same_bar_conflict']),
                'hold_minutes': int(exit_res['hold_minutes']),
                'exit_type': str(exit_res['exit_type']),
            })
            kept += 1
        meta_rows.append({'asset': asset, 'symbol': symbol, 'signals': int(len(signals)), 'simulated_candidates': kept, 'bars_15m': int(len(bars_15m)), 'bars_5m': int(len(bars_5m))})
    return pd.DataFrame(candidate_rows), pd.DataFrame(meta_rows)


def apply_live_selection(candidates: pd.DataFrame, strongest_only_per_bar: bool = True, max_concurrent_positions: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        return candidates.copy(), pd.DataFrame(columns=['reason', 'count'])
    work = candidates.copy().sort_values(['event_ts', 'slope_strength', 'asset'], ascending=[True, False, True]).reset_index(drop=True)
    if strongest_only_per_bar:
        keep_idx = work.groupby('event_ts', sort=False)['slope_strength'].idxmax().tolist()
        bar_selected = work.loc[sorted(keep_idx)].copy().sort_values(['event_ts', 'slope_strength'], ascending=[True, False]).reset_index(drop=True)
        rejected_bar = len(work) - len(bar_selected)
    else:
        bar_selected = work.copy()
        rejected_bar = 0

    active_until: list[pd.Timestamp] = []
    picked_rows: list[dict[str, object]] = []
    rejected_concurrent = 0
    for _, row in bar_selected.iterrows():
        active_until = [ts for ts in active_until if ts > row['entry_ts']]
        if len(active_until) >= max_concurrent_positions:
            rejected_concurrent += 1
            continue
        picked_rows.append(row.to_dict())
        active_until.append(pd.to_datetime(row['exit_ts'], utc=True))
        active_until.sort()

    selected = pd.DataFrame(picked_rows)
    stats = pd.DataFrame([
        {'reason': 'candidate_trades', 'count': int(len(work))},
        {'reason': 'after_strongest_per_bar', 'count': int(len(bar_selected))},
        {'reason': 'selected_live_parity', 'count': int(len(selected))},
        {'reason': 'rejected_by_bar_competition', 'count': int(rejected_bar)},
        {'reason': 'rejected_by_max_concurrent', 'count': int(rejected_concurrent)},
    ])
    return selected, stats


def summarize_assets(df: pd.DataFrame, asset_map: dict[str, str]) -> pd.DataFrame:
    rows = []
    for asset, symbol in asset_map.items():
        part = df[df['asset'] == asset].copy()
        if part.empty:
            rows.append({'asset': asset, 'symbol': symbol, 'trades': 0, 'total_return': 0.0, 'win_rate': np.nan, 'avg_net_ret': np.nan, 'avg_hold_minutes': np.nan, 'target_hit_rate': np.nan, 'stop_hit_rate': np.nan, 'timeout_rate': np.nan})
            continue
        rows.append({
            'asset': asset,
            'symbol': symbol,
            'trades': int(len(part)),
            'total_return': float((1.0 + part['net_ret']).prod() - 1.0),
            'win_rate': float((part['net_ret'] > 0).mean()),
            'avg_net_ret': float(part['net_ret'].mean()),
            'avg_hold_minutes': float(part['hold_minutes'].mean()),
            'target_hit_rate': float(part['target_hit'].mean()),
            'stop_hit_rate': float(part['stop_hit'].mean()),
            'timeout_rate': float((part['exit_type'] == 'timeout_close').mean()),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(['total_return', 'trades'], ascending=[False, False]).reset_index(drop=True)


def summarize_portfolio(df: pd.DataFrame, selection_stats: pd.DataFrame, candidate_df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {'portfolio_total_return': np.nan, 'selected_trades': 0, 'win_rate': np.nan}
    counts = candidate_df.groupby('event_ts')['asset'].nunique() if not candidate_df.empty else pd.Series(dtype=int)
    return {
        'portfolio_total_return': float((1.0 + df['net_ret']).prod() - 1.0),
        'selected_trades': int(len(df)),
        'win_rate': float((df['net_ret'] > 0).mean()),
        'avg_net_ret': float(df['net_ret'].mean()),
        'avg_hold_minutes': float(df['hold_minutes'].mean()),
        'target_hit_rate': float(df['target_hit'].mean()),
        'stop_hit_rate': float(df['stop_hit'].mean()),
        'timeout_rate': float((df['exit_type'] == 'timeout_close').mean()),
        'candidate_signal_times': int(counts.shape[0]),
        'overlap_timestamp_ratio': float((counts > 1).mean()) if len(counts) else np.nan,
        'max_same_bar_assets': int(counts.max()) if len(counts) else 0,
        'selection_stats': selection_stats.to_dict(orient='records'),
    }


def build_window_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['window', 'trades', 'total_return', 'win_rate', 'avg_hold_minutes'])
    work = df.copy()
    work['entry_ts'] = pd.to_datetime(work['entry_ts'], utc=True)
    end = work['entry_ts'].max()
    cut_recent = end - pd.Timedelta(days=120)
    cut_mid = end - pd.Timedelta(days=240)
    windows = [
        ('older_365d_to_240d', work[work['entry_ts'] < cut_mid]),
        ('middle_240d_to_120d', work[(work['entry_ts'] >= cut_mid) & (work['entry_ts'] < cut_recent)]),
        ('recent_120d', work[work['entry_ts'] >= cut_recent]),
    ]
    rows = []
    for name, part in windows:
        if part.empty:
            continue
        rows.append({
            'window': name,
            'trades': int(len(part)),
            'total_return': float((1.0 + part['net_ret']).prod() - 1.0),
            'win_rate': float((part['net_ret'] > 0).mean()),
            'avg_hold_minutes': float(part['hold_minutes'].mean()),
        })
    return pd.DataFrame(rows)


def build_html(tag: str, generated_at: str, symbols: list[str], portfolio: dict[str, object], selection_stats: pd.DataFrame, asset_summary: pd.DataFrame, window_summary: pd.DataFrame) -> str:
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · live parity universe</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · live parity universe</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 目标：把当前实盘口径尽量一比一搬到更大币池里。标签：<code>{escape(tag)}</code></p>
  <div class='card'>
    <h2>simulation assumptions</h2>
    <ul>
      <li>Universe：<code>{escape(', '.join(symbols))}</code></li>
      <li>Entry：<b>market / taker</b></li>
      <li>Exit：<b>TP 1.25 ATR + SL 1.00 ATR + timeout 8x15m</b></li>
      <li>Selection：<b>strongest_signal_only per bar</b></li>
      <li>Risk：<b>max_concurrent_positions = 1</b></li>
      <li>读法：这比“每个币各跑各的”更接近当前 canary 真正会做的事。</li>
    </ul>
  </div>
  <div class='card'>
    <h2>portfolio read</h2>
    <p><span class='pill'>selected trades = {portfolio['selected_trades']}</span><span class='pill'>portfolio total return = {pct(portfolio['portfolio_total_return'])}</span><span class='pill'>win rate = {pct(portfolio['win_rate'])}</span></p>
    <p class='muted'>候选信号时间点：{portfolio['candidate_signal_times']} ｜ 多币同一时间触发占比：{pct(portfolio['overlap_timestamp_ratio'])} ｜ 单根 bar 最多同时触发：{portfolio['max_same_bar_assets']} 个币。</p>
    <p class='muted'>TP hit：{pct(portfolio['target_hit_rate'])} ｜ SL hit：{pct(portfolio['stop_hit_rate'])} ｜ timeout：{pct(portfolio['timeout_rate'])} ｜ 平均持有：{num(portfolio['avg_hold_minutes'], 1)} 分钟</p>
  </div>
  <div class='card'>
    <h2>selection funnel</h2>
    {render_table(selection_stats)}
  </div>
  <div class='card'>
    <h2>selected trades by asset</h2>
    {render_table(asset_summary[['asset','trades','total_return','win_rate','avg_net_ret','avg_hold_minutes','target_hit_rate','stop_hit_rate','timeout_rate']], percent_cols={'total_return','win_rate','avg_net_ret','target_hit_rate','stop_hit_rate','timeout_rate'}, digits_cols={'trades':0,'avg_hold_minutes':1})}
  </div>
  <div class='card'>
    <h2>time-split stability inside the selected portfolio</h2>
    {render_table(window_summary, percent_cols={'total_return','win_rate'}, digits_cols={'trades':0,'avg_hold_minutes':1})}
  </div>
</body>
</html>
"""


def inject_report_summary(report_path: Path, generated_at: str, html_name: str) -> None:
    if not report_path.exists():
        return
    block = f"""
  <div class='card'>
    <h2>live parity universe（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 目标：把当前 32b 实盘口径（TP/SL/timeout/selection/risk）搬到更大币池里，检验它是否仍然站得住。</p>
    <p><a href='./{escape(html_name)}'>查看 live parity 回测结果</a></p>
  </div>"""
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{block}\n{end_marker}"
    html = report_path.read_text(encoding='utf-8')
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace('</body>', wrapped + '\n</body>')
    report_path.write_text(html, encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run live-parity universe backtest for Rank 32b.')
    parser.add_argument('--symbols', type=str, default=','.join(DEFAULT_SYMBOLS))
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS)
    parser.add_argument('--tag', type=str, default=DEFAULT_TAG)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--tp', type=float, default=DEFAULT_TP)
    parser.add_argument('--sl', type=float, default=DEFAULT_SL)
    parser.add_argument('--timeout15m', type=int, default=DEFAULT_TIMEOUT_15M)
    parser.add_argument('--max-concurrent', type=int, default=DEFAULT_MAX_CONCURRENT)
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    asset_map = build_asset_map(args.symbols)
    tag = str(args.tag).strip() or DEFAULT_TAG

    candidates, meta = simulate_candidates(asset_map, int(args.days), float(args.tp), float(args.sl), int(args.timeout15m), refresh=bool(args.refresh))
    selected, selection_stats = apply_live_selection(candidates, strongest_only_per_bar=True, max_concurrent_positions=int(args.max_concurrent))
    asset_summary = summarize_assets(selected, asset_map)
    portfolio = summarize_portfolio(selected, selection_stats, candidates)
    window_summary = build_window_summary(selected)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    # persist
    cands_out = candidates.copy()
    sel_out = selected.copy()
    for df in [cands_out, sel_out]:
        for col in ['event_ts','entry_ts','exit_ts']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    (ART_DIR / f'{tag}_meta.csv').write_text(meta.to_csv(index=False), encoding='utf-8')
    (ART_DIR / f'{tag}_candidate_trades.csv').write_text(cands_out.to_csv(index=False), encoding='utf-8')
    (ART_DIR / f'{tag}_selected_trades.csv').write_text(sel_out.to_csv(index=False), encoding='utf-8')
    (ART_DIR / f'{tag}_selection_stats.csv').write_text(selection_stats.to_csv(index=False), encoding='utf-8')
    (ART_DIR / f'{tag}_asset_summary.csv').write_text(asset_summary.to_csv(index=False), encoding='utf-8')
    (ART_DIR / f'{tag}_window_summary.csv').write_text(window_summary.to_csv(index=False), encoding='utf-8')
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tag': tag,
        'symbols': list(asset_map.values()),
        'days': int(args.days),
        'tp_atr_mult': float(args.tp),
        'sl_atr_mult': float(args.sl),
        'timeout_15m': int(args.timeout15m),
        'max_concurrent': int(args.max_concurrent),
        **portfolio,
    }
    (ART_DIR / f'{tag}_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    html_path = SITE_DIR / f'{tag}.html'
    html_path.write_text(build_html(tag, generated_at, list(asset_map.values()), portfolio, selection_stats, asset_summary, window_summary), encoding='utf-8')
    inject_report_summary(SITE_DIR / 'report.html', generated_at, html_path.name)
    inject_report_summary(READING_PATH, generated_at, html_path.name)

    print(json.dumps({'html': str(html_path), 'summary_json': str(ART_DIR / f'{tag}_summary.json'), 'asset_summary_csv': str(ART_DIR / f'{tag}_asset_summary.csv'), 'selected_trades_csv': str(ART_DIR / f'{tag}_selected_trades.csv'), 'generated_at_utc': summary['generated_at_utc'], 'portfolio_total_return': summary['portfolio_total_return'], 'selected_trades': summary['selected_trades']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
