#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_slope_floor_continuation_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_slope_floor_continuation_15m'
OUTPUT_HTML = SITE_DIR / 'universe_admission.html'
OUTPUT_CSV = ART_DIR / 'universe_admission_table.csv'
OUTPUT_JSON = ART_DIR / 'universe_admission_summary.json'
REPORT_PATH = SITE_DIR / 'report.html'
READING_REPORT = ROOT / 'reports' / 'site' / 'reading' / 'trendline_alpha_scout' / 'rank32b_slope_floor_continuation_clean_replication.html'
MARKER_ID = 'rank32b-universe-admission'

TIER1 = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'LTCUSDT', 'NEARUSDT', 'UNIUSDT',
    'XRPUSDT', 'DOGEUSDT', 'ADAUSDT', 'AVAXUSDT', 'LINKUSDT', 'DOTUSDT',
]
TIER2 = ['BNBUSDT', 'BCHUSDT', 'ZECUSDT', 'AAVEUSDT', 'SUIUSDT', 'WLDUSDT']
WATCHLIST = ['FILUSDT', 'WIFUSDT']

CUSTOM_NOTES = {
    'BTCUSDT': '核心腿；流动性最高；已在当前实盘白名单。',
    'ETHUSDT': '核心腿；流动性高；已在当前实盘白名单。',
    'SOLUSDT': '核心腿；5y 结果最强之一；已在当前实盘白名单。',
    'LTCUSDT': '已完成 5y 候选稳定性；适合作为扩池第一批。',
    'NEARUSDT': '已完成 5y 候选稳定性；当前也有实盘运行经验。',
    'UNIUSDT': '已完成 5y 候选稳定性；研究链条完整。',
    'XRPUSDT': '长窗口 5/5 年窗为正；流动性和交易密度都足够。',
    'DOGEUSDT': '长窗口 5/5 年窗为正；高流动性 meme 主流腿。',
    'ADAUSDT': '长窗口 5/5 年窗为正；成交量稳定。',
    'AVAXUSDT': '长窗口 5/5 年窗为正；收益和交易密度都较强。',
    'LINKUSDT': '长窗口 5/5 年窗为正；Batch B 中最强之一。',
    'DOTUSDT': '长窗口 5/5 年窗为正；研究表现稳而不激进。',
    'BNBUSDT': '长窗口全正，但 1y 横截面收益相对保守，建议先轻仓 / paper。',
    'BCHUSDT': '长窗口全正，但收益弹性不如 Tier 1，建议第二批。',
    'ZECUSDT': '1y 与 5y 都很强，但真实盘口深度/微结构需要先 paper 验证。',
    'AAVEUSDT': 'Batch A 长窗口全正；适合小规模上线前再做一段 paper。',
    'SUIUSDT': '历史较短但 older/middle/recent 三段全正；先 paper 再放量。',
    'WLDUSDT': '历史较短但三段全正；高波动新主流，建议轻仓试运行。',
    'FILUSDT': '1y 首筛 10bps 已转负，成本敏感，先放 watchlist。',
    'WIFUSDT': '1y 首筛到 20bps 转负；口袋存在但对成本更敏感。',
}


def pct(value: float | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return '-'
    return f'{float(value) * 100:.{digits}f}%'


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = ''.join(f'<td>{escape(str(v))}</td>' for v in row.tolist())
        rows.append(f'<tr>{cells}</tr>')
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_cost_pivot() -> pd.DataFrame:
    paths = [
        ART_DIR / 'universe_shortlist18_1y_asset_summary.csv',
        ART_DIR / 'universe_batch_a_1y_asset_summary.csv',
    ]
    frames = [pd.read_csv(p) for p in paths if p.exists()]
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=['asset', 'cost_bps_per_side'], keep='first')
    pivot = (
        df.pivot_table(index='asset', columns='cost_bps_per_side', values='total_return', aggfunc='first')
        .rename(columns={6.0: 'ret_6bps', 10.0: 'ret_10bps', 15.0: 'ret_15bps', 20.0: 'ret_20bps'})
        .reset_index()
    )
    win = (
        df[df['cost_bps_per_side'] == 6.0][['asset', 'trades', 'win_rate', 'no_trade_ratio']]
        .drop_duplicates(subset=['asset'])
        .rename(columns={'trades': 'trades_1y', 'win_rate': 'win_rate_1y', 'no_trade_ratio': 'no_trade_ratio_1y'})
    )
    return pivot.merge(win, on='asset', how='left')


def load_long_window_ratios() -> dict[str, tuple[int, int]]:
    paths = [
        ART_DIR / 'candidate_5y_stability_yearly_summary.csv',
        ART_DIR / 'universe_batch_a_long_window_yearly_summary.csv',
        ART_DIR / 'universe_batch_b_long_window_yearly_summary.csv',
    ]
    out: dict[str, tuple[int, int]] = {}
    for path in paths:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for asset, grp in df.groupby('asset'):
            out[asset] = (int((grp['total_return'] > 0).sum()), int(len(grp)))
    return out


def choose_tier(symbol: str) -> str:
    if symbol in TIER1:
        return 'Tier 1 · 优先扩池'
    if symbol in TIER2:
        return 'Tier 2 · paper/轻仓'
    if symbol in WATCHLIST:
        return 'Tier 3 · watchlist'
    return 'Excluded'


def build_rows() -> tuple[pd.DataFrame, dict[str, object]]:
    pool = pd.read_csv(ART_DIR / 'universe_candidate_pool.csv')
    cost = load_cost_pivot()
    long_ratios = load_long_window_ratios()

    pool['research_asset'] = pool['symbol'].map(lambda s: str(s).replace('USDT', '-USD'))
    merged = pool.merge(cost, left_on='research_asset', right_on='asset', how='left')
    merged['long_window_positive'] = merged['research_asset'].map(lambda a: long_ratios.get(a, (0, 0))[0])
    merged['long_window_total'] = merged['research_asset'].map(lambda a: long_ratios.get(a, (0, 0))[1])
    merged['long_window_score'] = merged.apply(
        lambda r: f"{int(r['long_window_positive'])}/{int(r['long_window_total'])}" if pd.notna(r['long_window_total']) and int(r['long_window_total']) > 0 else '-',
        axis=1,
    )
    merged['tier'] = merged['symbol'].map(choose_tier)
    merged['custom_note'] = merged['symbol'].map(lambda s: CUSTOM_NOTES.get(s, ''))

    shortlist = merged[merged['symbol'].isin(TIER1 + TIER2 + WATCHLIST)].copy()
    shortlist['tier_rank'] = shortlist['symbol'].map(lambda s: 1 if s in TIER1 else 2 if s in TIER2 else 3)
    shortlist['phase'] = shortlist['symbol'].map(lambda s: 'Phase 1' if s in TIER1 else 'Phase 2' if s in TIER2 else 'Watchlist')
    shortlist.sort_values(['tier_rank', 'rank_median_30d', 'symbol'], inplace=True)

    display = shortlist[
        [
            'phase', 'tier', 'symbol', 'rank_median_30d', 'ret_6bps', 'ret_15bps', 'ret_20bps',
            'trades_1y', 'win_rate_1y', 'long_window_score', 'in_current_canary', 'custom_note'
        ]
    ].copy()
    display.rename(
        columns={
            'rank_median_30d': 'liq_rank_30d',
            'ret_6bps': 'ret_1y_6bps',
            'ret_15bps': 'ret_1y_15bps',
            'ret_20bps': 'ret_1y_20bps',
            'trades_1y': 'trades_1y',
            'win_rate_1y': 'win_rate_1y',
            'in_current_canary': 'current_live',
        },
        inplace=True,
    )
    for col in ['ret_1y_6bps', 'ret_1y_15bps', 'ret_1y_20bps', 'win_rate_1y']:
        display[col] = display[col].map(lambda x: pct(x, 1))
    display['current_live'] = display['current_live'].map(lambda x: 'yes' if bool(x) else '-')
    display['liq_rank_30d'] = display['liq_rank_30d'].map(lambda x: int(x) if pd.notna(x) else '-')
    display['trades_1y'] = display['trades_1y'].map(lambda x: int(x) if pd.notna(x) else '-')

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tier1_symbols': TIER1,
        'tier2_symbols': TIER2,
        'watchlist_symbols': WATCHLIST,
        'tier1_count': len(TIER1),
        'tier2_count': len(TIER2),
        'watchlist_count': len(WATCHLIST),
        'shortlist18_mean_total_return_6bps': float(pd.read_csv(ART_DIR / 'universe_shortlist18_1y_cost_summary.csv').query('cost_bps_per_side == 6')['mean_total_return'].iloc[0]),
        'shortlist18_positive_asset_ratio_6bps': float(pd.read_csv(ART_DIR / 'universe_shortlist18_1y_cost_summary.csv').query('cost_bps_per_side == 6')['positive_asset_ratio'].iloc[0]),
    }
    return display, summary


def build_html(display: pd.DataFrame, summary: dict[str, object]) -> str:
    tier1 = display[display['phase'] == 'Phase 1']
    tier2 = display[display['phase'] == 'Phase 2']
    watch = display[display['phase'] == 'Watchlist']
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · universe admission</title>
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
  <h1>Rank 32b · universe admission</h1>
  <p class='muted'>生成时间：{escape(summary['generated_at_utc'])} ｜ 目的：把现有 universe 研究整理成可执行的准入分层表，而不是只停留在“看起来都不错”。</p>

  <div class='card'>
    <h2>hard read</h2>
    <p><span class='pill'>Tier 1 = {summary['tier1_count']} 个</span><span class='pill'>Tier 2 = {summary['tier2_count']} 个</span><span class='pill'>Watchlist = {summary['watchlist_count']} 个</span></p>
    <p><b>18 币 shortlist 在 1 年 / 6bps 下的组合层结果是：mean_total_return≈{pct(summary['shortlist18_mean_total_return_6bps'])}、positive_asset_ratio≈{pct(summary['shortlist18_positive_asset_ratio_6bps'])}。</b></p>
    <p class='muted'>这说明当前不是“扩池会把质量打坏”的局面，更像是可以进入分层上线阶段。Tier 1 先看流动性、已有实盘经验、5y/长窗口稳定性；Tier 2 则是研究证据足够，但需要先过一段 paper 或轻仓验证真实微结构。</p>
  </div>

  <div class='card'>
    <h2>怎么读这张准入表</h2>
    <ul>
      <li><b>Tier 1 · 优先扩池：</b>研究证据已经足够完整，且更适合先纳入下一版白名单。</li>
      <li><b>Tier 2 · paper/轻仓：</b>回测很强，但还想先看一下真实盘口、滑点、挂单行为，再决定是否提到主白名单。</li>
      <li><b>Tier 3 · watchlist：</b>不是完全不行，而是当前对成本更敏感，先不急着纳入。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Phase 1：优先扩池（建议先上的 12 个币）</h2>
    {render_table(tier1)}
  </div>

  <div class='card'>
    <h2>Phase 2：paper / 轻仓验证（建议第二批的 6 个币）</h2>
    {render_table(tier2)}
  </div>

  <div class='card'>
    <h2>Watchlist：先观察，不急着进主白名单</h2>
    {render_table(watch)}
  </div>

  <div class='card'>
    <h2>配套研究入口</h2>
    <ul>
      <li><a href='./universe_candidates.html'>20 币候选池</a></li>
      <li><a href='./universe_batch_a_1y.html'>Batch A · 1y 首筛</a></li>
      <li><a href='./universe_batch_a_long_window.html'>Batch A · 长窗口稳定性</a></li>
      <li><a href='./universe_batch_b_long_window.html'>Batch B · 长窗口稳定性</a></li>
      <li><a href='./universe_shortlist18_1y.html'>18 币组合层结果</a></li>
    </ul>
  </div>
</body>
</html>
"""


def inject_report_summary(report_path: Path, generated_at: str) -> None:
    if not report_path.exists():
        return
    block = f"""
  <div class='card'>
    <h2>universe admission（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 目标：把 universe 研究结果整理成可执行的准入分层表。</p>
    <p><span class='pill'>Tier 1 = 12</span><span class='pill'>Tier 2 = 6</span><span class='pill'>Watchlist = 2</span></p>
    <p><b>当前 18 币 shortlist 在 1 年 / 6bps 下并没有被稀释，反而比之前 17 币版本更强；因此现在更合理的问题已经不是“要不要扩池”，而是“先上哪 12 个、哪 6 个先 paper / 轻仓”。</b></p>
    <p><a href='./universe_admission.html'>查看 18 币准入分层表</a> ｜ <a href='./universe_shortlist18_1y.html'>查看 18 币组合层结果</a></p>
  </div>"""
    html = report_path.read_text(encoding='utf-8')
    start_marker = f"<!-- {MARKER_ID}:start -->"
    end_marker = f"<!-- {MARKER_ID}:end -->"
    wrapped = f"{start_marker}\n{block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace('</body>', wrapped + '\n</body>')
    report_path.write_text(html, encoding='utf-8')


def main() -> None:
    display, summary = build_rows()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    display.to_csv(OUTPUT_CSV, index=False)
    OUTPUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    OUTPUT_HTML.write_text(build_html(display, summary), encoding='utf-8')
    inject_report_summary(REPORT_PATH, summary['generated_at_utc'])
    inject_report_summary(READING_REPORT, summary['generated_at_utc'])
    print(json.dumps({'html': str(OUTPUT_HTML), 'csv': str(OUTPUT_CSV), 'json': str(OUTPUT_JSON), 'generated_at_utc': summary['generated_at_utc']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
