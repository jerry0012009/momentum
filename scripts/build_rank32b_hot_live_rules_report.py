#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_hot_fee_vip0_compare_15m'
POOL_META_PATH = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_hot_universe_volume_phase_15m' / 'pool_meta.csv'
OUT_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank32b_hot_live_rules_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank32b_hot_live_rules_15m'
REPORT_PATH = SITE_DIR / 'report.html'
SUMMARY_PATH = OUT_DIR / 'summary.json'
TIER_PATH = OUT_DIR / 'tier_recommendations.csv'

A_RULES = {
    'base_trades_min': 45,
    'base_total_return_min': 0.15,
    'base_avg_net_ret_min': 0.0028,
    'cold_trades_min': 15,
    'cold_total_return_min': 0.0,
    'cold_avg_net_ret_min': 0.0025,
}


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v, digits: int = 2) -> str:
    if pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


def num(v, digits: int = 2) -> str:
    if pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def money_m(v) -> str:
    if pd.isna(v):
        return '-'
    return f'{float(v)/1e6:.1f}M'


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None, money_cols: set[str] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    money_cols = money_cols or set()
    header = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if col in percent_cols:
                text = pct(val)
            elif col in money_cols:
                text = money_m(val)
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                text = num(val, digits_cols.get(col, 2))
            else:
                text = str(val)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    asset = pd.read_csv(SRC_DIR / 'strict_universe_asset_summary.csv')
    pool = pd.read_csv(POOL_META_PATH)
    return asset, pool


def build_tiers(asset: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    base = asset[asset.variant == 'baseline_all'][['asset', 'trades', 'total_return', 'win_rate', 'avg_net_ret']].rename(columns={
        'trades': 'base_trades', 'total_return': 'base_total_return', 'win_rate': 'base_win_rate', 'avg_net_ret': 'base_avg_net_ret'
    })
    hot = asset[asset.variant == 'hot_phase_only'][['asset', 'trades', 'total_return', 'win_rate', 'avg_net_ret']].rename(columns={
        'trades': 'hot_trades', 'total_return': 'hot_total_return', 'win_rate': 'hot_win_rate', 'avg_net_ret': 'hot_avg_net_ret'
    })
    cold = asset[asset.variant == 'cold_phase_only'][['asset', 'trades', 'total_return', 'win_rate', 'avg_net_ret']].rename(columns={
        'trades': 'cold_trades', 'total_return': 'cold_total_return', 'win_rate': 'cold_win_rate', 'avg_net_ret': 'cold_avg_net_ret'
    })
    df = base.merge(hot, on='asset').merge(cold, on='asset')
    df['symbol'] = df['asset'].str.replace('-USD', 'USDT', regex=False)
    df = df.merge(pool[['symbol', 'listing_days', 'quote_volume_median_120d', 'heat_ratio_120d']], on='symbol', how='left')

    def tier(row):
        if (
            row['base_trades'] >= A_RULES['base_trades_min'] and
            row['base_total_return'] >= A_RULES['base_total_return_min'] and
            row['base_avg_net_ret'] >= A_RULES['base_avg_net_ret_min'] and
            row['cold_trades'] >= A_RULES['cold_trades_min'] and
            row['cold_total_return'] > A_RULES['cold_total_return_min'] and
            row['cold_avg_net_ret'] >= A_RULES['cold_avg_net_ret_min']
        ):
            return 'Tier A · 可考虑纳入 live exploratory'
        if row['hot_total_return'] >= 0.10 and row['hot_avg_net_ret'] >= 0.004:
            return 'Tier B1 · 只建议热期提权'
        if row['cold_total_return'] > 0 and row['cold_avg_net_ret'] >= 0.003 and row['cold_trades'] >= 12:
            return 'Tier B2 · 次级候选/继续观察'
        return 'Tier C · 暂不建议纳入'

    def rationale(row):
        tier_name = row['tier']
        if tier_name.startswith('Tier A'):
            return '整体强、冷期也站得住，适合进入 hot exploratory universe。'
        if tier_name.startswith('Tier B1'):
            return '热期很强，但退潮后更脆，需要 activity/vol/trend 过滤后再提权。'
        if tier_name.startswith('Tier B2'):
            return '整体不差，但 edge 更薄，建议先 shadow 观察。'
        return '当前证据不足或退潮后过弱，不建议直接放进 live。'

    df['tier'] = df.apply(tier, axis=1)
    df['rationale'] = df.apply(rationale, axis=1)
    return df.sort_values(['tier', 'base_total_return'], ascending=[True, False]).reset_index(drop=True)


def build_html(df: pd.DataFrame, summary: dict[str, object]) -> str:
    tier_a = df[df['tier'].str.startswith('Tier A')].copy()
    tier_b1 = df[df['tier'].str.startswith('Tier B1')].copy()
    tier_b2 = df[df['tier'].str.startswith('Tier B2')].copy()
    tier_c = df[df['tier'].str.startswith('Tier C')].copy()

    tier_a_symbols = ', '.join(tier_a['symbol'].tolist())
    tier_b1_symbols = ', '.join(tier_b1['symbol'].tolist())
    tier_b2_symbols = ', '.join(tier_b2['symbol'].tolist())

    rules_html = """
    <ol>
      <li><b>不要把这些小币直接并入主 18 币白名单。</b> 建议单独建一个 <code>hot exploratory universe</code>，与主 18 币分开管理。</li>
      <li><b>Tier A</b> 可以考虑进入可交易观察池，但仍要加 phase / volatility 过滤；<b>Tier B1</b> 只在热期提权；<b>Tier B2</b> 先做 shadow / 继续观察；<b>Tier C</b> 先不纳入。</li>
      <li><b>Activity filter（建议必加）</b>：按每个币自己的历史活跃度看，最近 7D 中位日成交额分位数若低于自己 120D 历史的 <b>35%</b>，默认不交易。这样可以直接规避最冷的 bottom third。</li>
      <li><b>Volatility filter（建议必加）</b>：只在 <code>ATR14 / close</code> 高于该币自己过去 120D 的 <b>40% 分位数</b> 时允许交易。这是研究里最平衡、最容易提纯冷期质量的 gate。</li>
      <li><b>Trend gate（建议条件触发）</b>：如果币当前 activity 处在 35%~70% 的中间区，或者它属于 Tier B1 这种“热期型”标的，则额外要求：<code>|close/close[-36]-1| &gt; 1.5%</code> 且 <code>regime_score_36 &gt; 2.0</code>。</li>
      <li><b>组合层约束保留不动</b>：继续保留 <code>strongest_signal_only</code> 和 <code>max_concurrent_positions = 1</code>。对这批币不建议先把并发开大。</li>
      <li><b>仓位建议（不是信号过滤，但建议一起落地）</b>：小币不要一上来就沿用主白名单的 300U；更稳妥的是先从 <b>150U</b> 起，整组 hot exploratory universe 的总敞口先控在 <b>300~450U</b>。</li>
    </ol>
    """

    why_html = f"""
    <ul>
      <li><b>最适合先纳入的 Tier A：</b> {escape(tier_a_symbols or '无')}</li>
      <li><b>热期很强、但建议只在热期提权的 Tier B1：</b> {escape(tier_b1_symbols or '无')}</li>
      <li><b>可继续 shadow 的 Tier B2：</b> {escape(tier_b2_symbols or '无')}</li>
      <li><b>为什么这么分：</b>我们不是只看总体收益，而是同时看 <b>整体表现 + 热期表现 + 冷期韧性</b>。真正值得上 live 的，不是“热的时候很猛”这一条，而是 <b>退潮后也不至于立刻塌</b>。</li>
    </ul>
    """

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · hot smallcap live rules</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1220px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; margin-bottom:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <h1>Rank 32b · 热门/小币可落地实盘过滤规则</h1>
  <p class='muted'>生成时间：{escape(summary['generated_at_utc'])} ｜ 基于 VIP0 双边万5/万5 的 23 币热门池研究，目标是把“研究结论”压成可落地的 live 规则：哪些币可以加、哪些只建议热期提权、以及需要加什么额外过滤器。</p>

  <div class='card'>
    <h2>一句话结论</h2>
    <p>
      <span class='pill'>Tier A = {int(summary['tier_counts']['Tier A'])}</span>
      <span class='pill'>Tier B1 = {int(summary['tier_counts']['Tier B1'])}</span>
      <span class='pill'>Tier B2 = {int(summary['tier_counts']['Tier B2'])}</span>
      <span class='pill'>Tier C = {int(summary['tier_counts']['Tier C'])}</span>
    </p>
    {why_html}
  </div>

  <div class='card'>
    <h2>建议的 live 规则</h2>
    {rules_html}
  </div>

  <div class='card'>
    <h2>完整 Tier 分层</h2>
    {render_table(df[['tier', 'symbol', 'base_trades', 'base_total_return', 'base_avg_net_ret', 'hot_total_return', 'hot_avg_net_ret', 'cold_trades', 'cold_total_return', 'cold_avg_net_ret', 'quote_volume_median_120d', 'heat_ratio_120d', 'rationale']], percent_cols={'base_total_return', 'base_avg_net_ret', 'hot_total_return', 'hot_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret'}, digits_cols={'base_trades': 0, 'cold_trades': 0, 'heat_ratio_120d': 1}, money_cols={'quote_volume_median_120d'})}
  </div>

  <div class='card'>
    <h2>我建议你优先考虑加到实盘探索池的币</h2>
    {render_table(tier_a[['symbol', 'base_trades', 'base_total_return', 'base_avg_net_ret', 'cold_trades', 'cold_total_return', 'cold_avg_net_ret']], percent_cols={'base_total_return', 'base_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret'}, digits_cols={'base_trades': 0, 'cold_trades': 0})}
    <p class='muted'>这批币的共同特点是：整体强、冷期也没明显塌掉，所以更适合做第一批 exploratory live additions。</p>
  </div>

  <div class='card'>
    <h2>只建议热期提权的币</h2>
    {render_table(tier_b1[['symbol', 'base_trades', 'base_total_return', 'hot_total_return', 'hot_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret']], percent_cols={'base_total_return', 'hot_total_return', 'hot_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret'}, digits_cols={'base_trades': 0})}
    <p class='muted'>这批币不是不能做，而是明显更依赖热点阶段。如果你要放进 live，请默认绑定 activity / volatility / trend 三层门。</p>
  </div>

  <div class='card'>
    <h2>建议先 shadow 的次级候选</h2>
    {render_table(tier_b2[['symbol', 'base_trades', 'base_total_return', 'base_avg_net_ret', 'cold_trades', 'cold_total_return', 'cold_avg_net_ret']], percent_cols={'base_total_return', 'base_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret'}, digits_cols={'base_trades': 0, 'cold_trades': 0})}
  </div>

  <div class='card'>
    <h2>暂不建议直接纳入</h2>
    {render_table(tier_c[['symbol', 'base_trades', 'base_total_return', 'base_avg_net_ret', 'cold_trades', 'cold_total_return', 'cold_avg_net_ret']], percent_cols={'base_total_return', 'base_avg_net_ret', 'cold_total_return', 'cold_avg_net_ret'}, digits_cols={'base_trades': 0, 'cold_trades': 0})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(OUT_DIR)
    ensure_dir(SITE_DIR)
    asset, pool = load_frames()
    df = build_tiers(asset, pool)
    df.to_csv(TIER_PATH, index=False)

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tier_counts': {
            'Tier A': int((df['tier'].str.startswith('Tier A')).sum()),
            'Tier B1': int((df['tier'].str.startswith('Tier B1')).sum()),
            'Tier B2': int((df['tier'].str.startswith('Tier B2')).sum()),
            'Tier C': int((df['tier'].str.startswith('Tier C')).sum()),
        },
        'tier_a_symbols': df.loc[df['tier'].str.startswith('Tier A'), 'symbol'].tolist(),
        'tier_b1_symbols': df.loc[df['tier'].str.startswith('Tier B1'), 'symbol'].tolist(),
        'tier_b2_symbols': df.loc[df['tier'].str.startswith('Tier B2'), 'symbol'].tolist(),
        'tier_c_symbols': df.loc[df['tier'].str.startswith('Tier C'), 'symbol'].tolist(),
        'rules': {
            'activity_filter': 'recent 7D median daily quote-volume percentile vs own 120D history must be >= 35%; if <35%, default block.',
            'volatility_filter': 'ATR14/close must be above own trailing 120D 40th percentile.',
            'trend_filter': 'for Tier B1 or mid-activity states, require abs(close/close[-36]-1) > 1.5% and regime_score_36 > 2.0.',
            'portfolio_filter': 'keep strongest_signal_only and max_concurrent_positions = 1 for hot smallcaps.',
            'sizing_suggestion': 'start at 150U per smallcap, total hot-exploratory exposure capped at 300-450U.',
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    REPORT_PATH.write_text(build_html(df, summary), encoding='utf-8')
    print(json.dumps({'report_html': str(REPORT_PATH), 'tier_csv': str(TIER_PATH), 'summary_json': str(SUMMARY_PATH)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
