#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m'
REPORT_PATH = SITE_DIR / 'report.html'
READING_REPORT = ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'rank32b_slope_floor_continuation_clean_replication.html'
OUTPUT_HTML = SITE_DIR / 'live_parity_compare_1y.html'
OUTPUT_JSON = ART_DIR / 'live_parity_compare_1y_summary.json'
MARKER_ID = 'rank32b-live-parity-compare'


def pct(v: float | None, digits: int = 1) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = ''.join(f'<td>{escape(str(v))}</td>' for v in row.tolist())
        rows.append(f'<tr>{cells}</tr>')
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_summary(name: str) -> dict:
    return json.loads((ART_DIR / name).read_text())


def build_html(compare_df: pd.DataFrame, funnel_df: pd.DataFrame, window_df: pd.DataFrame, generated_at: str) -> str:
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · live parity compare</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · live parity compare</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 口径：market/taker 入场 + TP 1.25 ATR + SL 1.00 ATR + timeout 8x15m + strongest-signal-only + max_concurrent=1。</p>

  <div class='card'>
    <h2>hard read</h2>
    <p><b>在“当前实盘同构”的筛选规则下，18 币 shortlist 相比 core3：真实入选交易数显著增加，但加权胜率只小幅下降，而且单笔平均净收益反而更高。</b></p>
    <p class='muted'>注意：<code>portfolio_total_return</code> 是单位资金连续复利的理论值，主要用于同口径比较，不适合直接拿来当现实年化。</p>
  </div>

  <div class='card'>
    <h2>core3 vs shortlist18</h2>
    {render_table(compare_df)}
  </div>

  <div class='card'>
    <h2>selection funnel</h2>
    <p class='muted'>这张表回答的是：扩池后，候选信号到底被 strongest-only 和并发限制砍掉了多少。</p>
    {render_table(funnel_df)}
  </div>

  <div class='card'>
    <h2>time split under live parity</h2>
    <p class='muted'>如果 older / middle / recent 三段都还能为正，就说明不是只靠某一段幸运行情撑起来。</p>
    {render_table(window_df)}
  </div>

  <div class='card'>
    <h2>怎么读这页</h2>
    <ul>
      <li><b>看交易数：</b>shortlist18 的真实入选交易数显著高于 core3，说明扩池在 strongest-only + 单并发限制下依然有增频价值。</li>
      <li><b>看胜率：</b>胜率确实比 core3 略低，但没有明显崩坏。</li>
      <li><b>看 avg_net_ret：</b>如果单笔平均净收益没变差，甚至略升，那说明不是纯加噪音。</li>
      <li><b>看 funnel：</b>如果 rejection 很大，说明扩池后更依赖组合层筛选，而不是每个币都应该无脑独立开仓。</li>
    </ul>
  </div>
</body>
</html>
"""


def inject_report(generated_at: str) -> None:
    block = f"""
  <div class='card'>
    <h2>live parity compare（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 目标：把 core3 和 shortlist18 放到当前实盘口径下做一比一对照。</p>
    <p><b>当前结论：</b>扩到 shortlist18 后，真实入选交易数明显增加，胜率仅小幅回落，单笔平均净收益没有变差。</p>
    <p><a href='./live_parity_compare_1y.html'>查看 live parity 对照页</a></p>
  </div>"""
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{block}\n{end_marker}"
    for path in [REPORT_PATH, READING_REPORT]:
        if not path.exists():
            continue
        html = path.read_text(encoding='utf-8')
        if start_marker in html and end_marker in html:
            left = html.split(start_marker)[0]
            right = html.split(end_marker, 1)[1]
            html = left + wrapped + right
        else:
            html = html.replace('</body>', wrapped + '\n</body>')
        path.write_text(html, encoding='utf-8')


def main() -> None:
    core = load_summary('live_parity_core3_1y_summary.json')
    short = load_summary('live_parity_shortlist18_1y_summary.json')
    compare = pd.DataFrame([
        {
            'universe': 'core3',
            'selected_trades': core['selected_trades'],
            'candidate_signal_times': core['candidate_signal_times'],
            'win_rate': pct(core['win_rate']),
            'avg_net_ret': pct(core['avg_net_ret']),
            'avg_hold_minutes': round(float(core['avg_hold_minutes']), 1),
            'target_hit_rate': pct(core['target_hit_rate']),
            'stop_hit_rate': pct(core['stop_hit_rate']),
            'timeout_rate': pct(core['timeout_rate']),
        },
        {
            'universe': 'shortlist18',
            'selected_trades': short['selected_trades'],
            'candidate_signal_times': short['candidate_signal_times'],
            'win_rate': pct(short['win_rate']),
            'avg_net_ret': pct(short['avg_net_ret']),
            'avg_hold_minutes': round(float(short['avg_hold_minutes']), 1),
            'target_hit_rate': pct(short['target_hit_rate']),
            'stop_hit_rate': pct(short['stop_hit_rate']),
            'timeout_rate': pct(short['timeout_rate']),
        },
        {
            'universe': 'delta(short/core)',
            'selected_trades': f"+{(short['selected_trades'] - core['selected_trades']) / core['selected_trades'] * 100:.1f}%",
            'candidate_signal_times': f"+{(short['candidate_signal_times'] - core['candidate_signal_times']) / core['candidate_signal_times'] * 100:.1f}%",
            'win_rate': f"{(short['win_rate'] - core['win_rate']) * 100:.1f}pp",
            'avg_net_ret': f"{(short['avg_net_ret'] - core['avg_net_ret']) * 100:.2f}pp",
            'avg_hold_minutes': round(float(short['avg_hold_minutes'] - core['avg_hold_minutes']), 1),
            'target_hit_rate': f"{(short['target_hit_rate'] - core['target_hit_rate']) * 100:.1f}pp",
            'stop_hit_rate': f"{(short['stop_hit_rate'] - core['stop_hit_rate']) * 100:.1f}pp",
            'timeout_rate': f"{(short['timeout_rate'] - core['timeout_rate']) * 100:.1f}pp",
        },
    ])

    core_funnel = pd.DataFrame(core['selection_stats'])
    short_funnel = pd.DataFrame(short['selection_stats'])
    funnel = core_funnel.merge(short_funnel, on='reason', how='outer', suffixes=('_core3', '_short18')).fillna(0)
    funnel['core3_to_selected_ratio'] = funnel['count_core3'].map(lambda x: '-' if x == 0 else f'{x}')
    funnel['short18_to_selected_ratio'] = funnel['count_short18'].map(lambda x: '-' if x == 0 else f'{x}')
    funnel = funnel[['reason', 'count_core3', 'count_short18']]

    core_windows = pd.read_csv(ART_DIR / 'live_parity_core3_1y_window_summary.csv')
    short_windows = pd.read_csv(ART_DIR / 'live_parity_shortlist18_1y_window_summary.csv')
    window = core_windows.merge(short_windows, on='window', how='outer', suffixes=('_core3', '_short18'))
    for col in ['total_return_core3','win_rate_core3','total_return_short18','win_rate_short18']:
        if col in window.columns:
            window[col] = window[col].map(lambda x: pct(x))
    for col in ['avg_hold_minutes_core3','avg_hold_minutes_short18']:
        if col in window.columns:
            window[col] = window[col].map(lambda x: '-' if pd.isna(x) else f'{float(x):.1f}')
    for col in ['trades_core3','trades_short18']:
        if col in window.columns:
            window[col] = window[col].map(lambda x: '-' if pd.isna(x) else int(x))

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    html = build_html(compare, funnel, window, generated_at)
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    OUTPUT_JSON.write_text(json.dumps({'generated_at_utc': generated_at, 'core3_selected_trades': core['selected_trades'], 'short18_selected_trades': short['selected_trades'], 'trade_increase_pct': (short['selected_trades'] - core['selected_trades']) / core['selected_trades'], 'win_rate_delta': short['win_rate'] - core['win_rate'], 'avg_net_ret_delta': short['avg_net_ret'] - core['avg_net_ret']}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    inject_report(generated_at)
    print(json.dumps({'html': str(OUTPUT_HTML), 'json': str(OUTPUT_JSON), 'generated_at_utc': generated_at}, ensure_ascii=False))


if __name__ == '__main__':
    main()
