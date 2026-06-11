#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BREAKOUT_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_breakout_short_family_honest_gate_15m'
FIB_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_fib_retest_family_honest_gate_15m'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_ewmac_breakout_bandpass_gate_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank151_ewmac_breakout_bandpass_gate_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank151_ewmac_breakout_bandpass_gate_rolling_split.html'
PRIMARY_COST = 6.0
CSS = "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:1180px;margin:32px auto;padding:0 18px 48px;line-height:1.68;color:#111827;background:#f8fafc}.card{border:1px solid #e5e7eb;border-radius:14px;background:#fff;padding:18px 20px;margin:16px 0}.muted{color:#6b7280}.good{color:#065f46;font-weight:600}.warn{color:#92400e;font-weight:600}.bad{color:#991b1b;font-weight:600}code{background:#f3f4f6;padding:1px 5px;border-radius:6px}table{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;background:#fff}th,td{border-bottom:1px solid #e5e7eb;padding:8px 10px;text-align:left;vertical-align:top}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding='utf-8')


def load_family(name: str, art_dir: Path) -> pd.DataFrame:
    trades = pd.read_csv(art_dir / 'trades.csv', parse_dates=['ts'])
    trades = trades[trades['cost_bps_per_side'] == PRIMARY_COST].copy()
    if 'asset' not in trades.columns and 'symbol' in trades.columns:
        trades['asset'] = trades['symbol']
    trades['family'] = name
    return trades[['ts', 'asset', 'variant', 'net_bps', 'family']]


def summarize_split(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values('ts').reset_index(drop=True).copy()
    mid = len(df) // 2
    df['time_split'] = 'back_half'
    if mid > 0:
        df.loc[: mid - 1, 'time_split'] = 'front_half'
    out = (
        df.groupby(['family', 'time_split', 'variant'])
        .agg(
            trades=('net_bps', 'size'),
            mean_net_bps=('net_bps', 'mean'),
            median_net_bps=('net_bps', 'median'),
            win_rate=('net_bps', lambda s: float((s > 0).mean())),
            total_net_bps=('net_bps', 'sum'),
        )
        .reset_index()
    )
    return out


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    breakout = load_family('breakout_short', BREAKOUT_DIR)
    fib = load_family('fib_retest_long', FIB_DIR)
    all_trades = pd.concat([breakout, fib], ignore_index=True)

    split_summary = summarize_split(all_trades)
    split_summary.to_csv(ART_DIR / 'rolling_split_summary.csv', index=False)

    pooled_rows = []
    for family, g in split_summary.groupby('family'):
        base = g[g['variant'] == 'baseline'].set_index('time_split')
        band = g[g['variant'] == 'band_pass'].set_index('time_split')
        for split in ['front_half', 'back_half']:
            if split not in base.index or split not in band.index:
                continue
            pooled_rows.append({
                'family': family,
                'time_split': split,
                'baseline_mean_net_bps': float(base.loc[split, 'mean_net_bps']),
                'band_pass_mean_net_bps': float(band.loc[split, 'mean_net_bps']),
                'band_pass_uplift_vs_baseline_bps': float(band.loc[split, 'mean_net_bps'] - base.loc[split, 'mean_net_bps']),
                'band_pass_trades': int(band.loc[split, 'trades']),
                'baseline_trades': int(base.loc[split, 'trades']),
            })
    uplift_df = pd.DataFrame(pooled_rows)
    uplift_df.to_csv(ART_DIR / 'rolling_split_uplift.csv', index=False)

    family_score_rows = []
    pass_count = 0
    for family in sorted(uplift_df['family'].unique()):
        sub = uplift_df[uplift_df['family'] == family].copy()
        positive_splits = int((sub['band_pass_uplift_vs_baseline_bps'] > 0).sum())
        band_positive_splits = int((sub['band_pass_mean_net_bps'] > 0).sum())
        family_pass = positive_splits == 2 and band_positive_splits >= 1
        pass_count += int(family_pass)
        family_score_rows.append({
            'family': family,
            'positive_uplift_splits': positive_splits,
            'positive_bandpass_splits': band_positive_splits,
            'family_pass': family_pass,
        })
    family_score = pd.DataFrame(family_score_rows)
    family_score.to_csv(ART_DIR / 'rolling_split_family_score.csv', index=False)

    breakout_monthly = pd.read_csv(BREAKOUT_DIR / 'monthly_uplift_vs_baseline_primary_cost.csv')
    breakout_uplift_positive = int((breakout_monthly['band_pass_uplift_vs_baseline_bps'] > 0).sum())
    breakout_months = int(len(breakout_monthly))

    total_band_trades = int(len(all_trades[all_trades['variant'] == 'band_pass']))
    total_base_trades = int(len(all_trades[all_trades['variant'] == 'baseline']))

    usefulness = 3
    time_stability = 3 if pass_count == 2 else (2 if pass_count == 1 else 1)
    cross_asset_stability = 3
    cost_trade_stability = 3
    deployability = 2 if pass_count == 2 else 1

    if pass_count == 2 and breakout_uplift_positive >= 5:
        recommended_action = 'promote_P2_discussion'
        verdict = 'Rank 151 已完成顶板要求的 rolling/split 稳定性，足以进入 P2 discussion。'
    else:
        recommended_action = 'keep_P1_but_stronger'
        verdict = 'Rank 151 仍保留为 keep_P1 but stronger；rolling/split 还不足以正式进 P2。'

    scorecard = pd.DataFrame([
        {
            'candidate': 'Rank 151 / EWMAC breakout band-pass gate',
            'usefulness': usefulness,
            'time_stability': time_stability,
            'cross_asset_stability': cross_asset_stability,
            'cost_trade_stability': cost_trade_stability,
            'deployability': deployability,
            'recommended_action': recommended_action,
            'why_now': '顶板 Run 1 已明确要求在两条 family replication 之后，优先用 rolling/split 稳定性回答它是否真有资格进 P2 discussion。',
            'main_weakness': 'fib retest 样本仍偏小；这次裁决更像 shared-gate 预审通过，不是直接进入 Paper 的 deploy 证据。',
        }
    ])
    scorecard.to_csv(ART_DIR / 'rolling_split_scorecard.csv', index=False)

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'primary_cost_bps_per_side': PRIMARY_COST,
        'breakout_monthly_positive_uplift': breakout_uplift_positive,
        'breakout_month_count': breakout_months,
        'families_passing_split_check': pass_count,
        'total_families_checked': 2,
        'band_pass_total_trades': total_band_trades,
        'baseline_total_trades': total_base_trades,
        'recommended_action': recommended_action,
        'verdict': verdict,
    }
    (ART_DIR / 'rolling_split_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    title = 'Rank 151 · rolling / split stability verdict'
    family_pass_map = {row['family']: bool(row['family_pass']) for _, row in family_score.iterrows()}
    verdict_class = 'good' if recommended_action == 'promote_P2_discussion' else 'warn'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(summary['generated_at_utc'])} ｜ 只复用 Rank 151 已经完成的两条 family 结果，不新开第三 family，不重跑重型优化。</p>
<div class='card'>
  <h2>一句话结论</h2>
  <p><span class='{verdict_class}'>{escape(verdict)}</span></p>
  <ul>
    <li>breakout-short：月度 uplift 为正 <b>{breakout_uplift_positive}/{breakout_months}</b>；split 检查通过 = <b>{'是' if family_pass_map.get('breakout_short') else '否'}</b></li>
    <li>fib_retest_long：split 检查通过 = <b>{'是' if family_pass_map.get('fib_retest_long') else '否'}</b></li>
    <li>两条 family 合计：band-pass 样本 <b>{total_band_trades}</b>，baseline 样本 <b>{total_base_trades}</b></li>
  </ul>
</div>
<div class='card'><h2>Rolling / split uplift by family</h2>{render_table(uplift_df, digits_cols={'baseline_mean_net_bps':2,'band_pass_mean_net_bps':2,'band_pass_uplift_vs_baseline_bps':2})}</div>
<div class='card'><h2>Family pass/fail</h2>{render_table(family_score)}</div>
<div class='card'><h2>Detailed split summary</h2>{render_table(split_summary[['family','time_split','variant','trades','mean_net_bps','median_net_bps','win_rate','total_net_bps']], percent_cols={'win_rate'}, digits_cols={'mean_net_bps':2,'median_net_bps':2,'total_net_bps':2})}</div>
<div class='card'><h2>轻量 scorecard</h2>{render_table(scorecard)}</div>
<div class='card'><h2>读法提醒</h2><ul>
<li>这轮只回答一个问题：<code>band_pass</code> 在两条已完成 family 上，是否前后半程都还能维持对 baseline 的 uplift。</li>
<li>如果这个最小 split 检查也站住，那么 desk 该把它从 <code>keep_P1 but stronger</code> 推进到 <code>P2 discussion</code>，而不是继续补第三条 family。</li>
<li>即便升到 P2，也仍不是 Paper launch；后面还要回答更严格 holdout / deploy 边界。</li>
</ul></div>
"""
    write_html(SITE_DIR / 'rolling_split_verdict.html', title, body)
    write_html(READING_PATH, title, body)
    write_html(SITE_DIR / 'report.html', title, body)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
