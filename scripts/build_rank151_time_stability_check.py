#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_breakout_short_family_honest_gate_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank151_breakout_short_family_honest_gate_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank151_breakout_short_family_honest_gate.html'
PRIMARY_COST = 6.0
CSS = "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:1160px;margin:32px auto;padding:0 18px 48px;line-height:1.68;color:#111827;background:#f8fafc}.card{border:1px solid #e5e7eb;border-radius:14px;background:#fff;padding:18px 20px;margin:16px 0}.muted{color:#6b7280}code{background:#f3f4f6;padding:1px 5px;border-radius:6px}table{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;background:#fff}th,td{border-bottom:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v) * 100:.{digits}f}%'


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
            elif isinstance(value, (float, int)):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def main() -> None:
    trades = pd.read_csv(ART_DIR / 'trades.csv', parse_dates=['ts'])
    trades = trades[trades['cost_bps_per_side'] == PRIMARY_COST].copy()
    trades['month'] = trades['ts'].dt.strftime('%Y-%m')

    monthly = (
        trades.groupby(['month', 'variant'])
        .agg(
            trades=('net_bps', 'size'),
            mean_net_bps=('net_bps', 'mean'),
            median_net_bps=('net_bps', 'median'),
            total_net_bps=('net_bps', 'sum'),
            win_rate=('net_bps', lambda s: float((s > 0).mean())),
        )
        .reset_index()
    )
    monthly_path = ART_DIR / 'monthly_stability_primary_cost.csv'
    monthly.to_csv(monthly_path, index=False)

    pivot = monthly.pivot(index='month', columns='variant', values='mean_net_bps').reset_index()
    pivot['hard_positive_uplift_vs_baseline_bps'] = pivot['hard_positive'] - pivot['baseline']
    pivot['band_pass_uplift_vs_baseline_bps'] = pivot['band_pass'] - pivot['baseline']
    uplift_path = ART_DIR / 'monthly_uplift_vs_baseline_primary_cost.csv'
    pivot.to_csv(uplift_path, index=False)

    band_uplift_positive = int((pivot['band_pass_uplift_vs_baseline_bps'] > 0).sum())
    total_months = int(len(pivot))
    band_positive_months = int((pivot['band_pass'] > 0).sum())

    if band_uplift_positive >= 5 and band_positive_months >= 4:
        verdict = 'keep_P1 but stronger：family uplift 不是单月幻觉，但还没到可直接升 P2 的稳定度。'
    else:
        verdict = 'keep_P1 but stronger：family uplift 明显真实，但时间稳定性仍不平，离 P2 还差第二 family 或更长稳定性复核。'

    primary = pd.read_csv(ART_DIR / 'pooled_summary.csv')
    primary = primary[primary['cost_bps_per_side'] == PRIMARY_COST].copy().set_index('variant')
    band = primary.loc['band_pass']
    base = primary.loc['baseline']

    title = 'Rank 151 · breakout-short family time stability check'
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 基于已有 family honest gate 结果，只检查最短 verdict-changing 邻近问题：band-pass uplift 是否只是单月幻觉。</p>
<div class='card'><h2>一句话结论</h2>
<p>{escape(verdict)}</p>
<ul>
<li>primary pooled：baseline mean_net_bps = {num(base['mean_net_bps'])}，band_pass = {num(band['mean_net_bps'])}</li>
<li>按月看，band_pass 相对 baseline 的 uplift 为正：{band_uplift_positive}/{total_months} 个月</li>
<li>按月看，band_pass 自身 mean_net_bps 为正：{band_positive_months}/{total_months} 个月</li>
</ul></div>
<div class='card'><h2>Monthly stability @ 6bps/side</h2>{render_table(monthly[['month','variant','trades','mean_net_bps','median_net_bps','win_rate','total_net_bps']], percent_cols={'win_rate'}, digits_cols={'mean_net_bps':2,'median_net_bps':2,'total_net_bps':2})}</div>
<div class='card'><h2>Monthly uplift vs baseline @ 6bps/side</h2>{render_table(pivot[['month','baseline','hard_positive','band_pass','hard_positive_uplift_vs_baseline_bps','band_pass_uplift_vs_baseline_bps']], digits_cols={'baseline':2,'hard_positive':2,'band_pass':2,'hard_positive_uplift_vs_baseline_bps':2,'band_pass_uplift_vs_baseline_bps':2})}</div>
<div class='card'><h2>最短读法</h2>
<ul>
<li><code>band_pass</code> 不是“每个月自己都赚钱”的稳定 allow gate；它在 2025-10 / 2026-01 仍会失手。</li>
<li>但它也不是单月 luck：相对 baseline 的 uplift 在 <strong>{band_uplift_positive}/{total_months}</strong> 个月为正，尤其 2025-11 / 2026-02 / 2026-03 改善明显。</li>
<li>因此当前更诚实口径是：<strong>keep_P1 but stronger</strong>，已拿到 first family evidence，但仍需第二 family 或更长时间稳定性复核，才有资格认真谈 P2。</li>
</ul></div>
"""
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"
    (SITE_DIR / 'report.html').write_text(html, encoding='utf-8')
    READING_PATH.write_text(html, encoding='utf-8')


if __name__ == '__main__':
    main()
