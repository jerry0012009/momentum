#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BREAKOUT_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_breakout_short_family_honest_gate_15m'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank151_ewmac_breakout_bandpass_gate_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank151_ewmac_breakout_bandpass_gate_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank151_ewmac_breakout_bandpass_gate_launch_admission_bar.html'
PRIMARY_COST = 6.0
WINDOWS = [30, 60, 90]
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


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    trades = pd.read_csv(BREAKOUT_DIR / 'trades.csv', parse_dates=['ts'])
    trades = trades[trades['cost_bps_per_side'] == PRIMARY_COST].copy()
    trades['day'] = trades['ts'].dt.floor('D')
    max_ts = trades['ts'].max()

    rows = []
    asset_rows = []
    density_rows = []
    pass_flags = []
    for days in WINDOWS:
        cutoff = max_ts - pd.Timedelta(days=days)
        win = trades[trades['ts'] >= cutoff].copy()
        pooled = (
            win.groupby('variant')
            .agg(
                trades=('net_bps', 'size'),
                mean_net_bps=('net_bps', 'mean'),
                total_net_bps=('net_bps', 'sum'),
                active_days=('day', 'nunique'),
            )
            .reset_index()
        )
        pooled['window_days'] = days
        rows.append(pooled)

        band = pooled[pooled['variant'] == 'band_pass'].iloc[0]
        base = pooled[pooled['variant'] == 'baseline'].iloc[0]
        uplift = float(band['mean_net_bps'] - base['mean_net_bps'])
        trades_per_active_day = float(band['trades'] / max(1, band['active_days']))
        coverage = win[win['variant'] == 'band_pass']['symbol'].nunique()
        pass_flag = uplift > 0 and band['mean_net_bps'] > 0 and trades_per_active_day >= 4.0 and coverage == 3
        pass_flags.append(pass_flag)
        density_rows.append({
            'window_days': days,
            'band_pass_mean_net_bps': float(band['mean_net_bps']),
            'baseline_mean_net_bps': float(base['mean_net_bps']),
            'band_pass_uplift_vs_baseline_bps': uplift,
            'band_pass_trades': int(band['trades']),
            'baseline_trades': int(base['trades']),
            'band_pass_active_days': int(band['active_days']),
            'band_pass_trades_per_active_day': trades_per_active_day,
            'band_pass_asset_coverage': int(coverage),
            'admission_slice_pass': pass_flag,
        })

        asset = (
            win[win['variant'] == 'band_pass']
            .groupby('symbol')
            .agg(
                band_pass_trades=('net_bps', 'size'),
                band_pass_mean_net_bps=('net_bps', 'mean'),
                band_pass_total_net_bps=('net_bps', 'sum'),
                band_pass_active_days=('day', 'nunique'),
            )
            .reset_index()
        )
        asset['window_days'] = days
        asset_rows.append(asset)

    pooled_summary = pd.concat(rows, ignore_index=True)
    asset_summary = pd.concat(asset_rows, ignore_index=True)
    density_summary = pd.DataFrame(density_rows)

    pooled_summary.to_csv(ART_DIR / 'launch_admission_recent_slice_summary.csv', index=False)
    asset_summary.to_csv(ART_DIR / 'launch_admission_recent_slice_asset_summary.csv', index=False)
    density_summary.to_csv(ART_DIR / 'launch_admission_density_scorecard.csv', index=False)

    promote_p3 = bool(all(pass_flags))
    recommended_action = 'promote_P3_launch_queue' if promote_p3 else 'stay_P2_with_blocker'
    verdict = (
        'Rank 151 已通过面向 launch 的最小 admission bar：breakout-short 在 recent slices 上继续保留正 uplift、正 band-pass 均值、足够 trade density 与 3/3 资产覆盖，可升到 P3 / Paper launch queue。'
        if promote_p3
        else 'Rank 151 仍停留在 P2：recent-slice uplift / density / asset coverage 至少有一项没有站稳，不建议现在送入 Paper launch queue。'
    )

    scorecard = pd.DataFrame([
        {
            'candidate': 'Rank 151 / EWMAC breakout band-pass gate',
            'shared_gate_evidence': 3,
            'recent_slice_honesty': 3 if promote_p3 else 2,
            'trade_density': 3 if promote_p3 else 2,
            'runner_feasibility': 3 if promote_p3 else 2,
            'recommended_action': recommended_action,
            'why_now': '顶板 Run 1 要求用一个贴近 Paper launch 的最小检查回答 Rank 151 是否值得进 P3 / launch queue。',
            'main_weakness': '当前 admission bar 只在 breakout-short 承载 family 上做 recent-slice / density 裁决；runner 真正接线前仍要补最小 operating spec。',
        }
    ])
    scorecard.to_csv(ART_DIR / 'launch_admission_scorecard.csv', index=False)

    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'primary_cost_bps_per_side': PRIMARY_COST,
        'anchor_family': 'breakout_short',
        'windows_days': WINDOWS,
        'all_recent_slices_pass': promote_p3,
        'recommended_action': recommended_action,
        'verdict': verdict,
    }
    (ART_DIR / 'launch_admission_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    title = 'Rank 151 · launch admission bar'
    cls = 'good' if promote_p3 else 'warn'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(summary['generated_at_utc'])} ｜ 只检查一个最贴近 launch 的窄问题：默认承载 family <code>breakout-short</code> 在 recent slices 下，band-pass 还剩不剩正 uplift + 可运行密度。</p>
<div class='card'>
  <h2>一句话结论</h2>
  <p><span class='{cls}'>{escape(verdict)}</span></p>
  <ul>
    <li>判据固定：<code>uplift &gt; 0</code>、<code>band_pass mean_net_bps &gt; 0</code>、<code>trades/active_day &gt;= 4</code>、<code>asset coverage = 3/3</code></li>
    <li>只看 primary 成本层：<b>6 bps / side</b></li>
    <li>窗口：<b>30 / 60 / 90 天</b></li>
  </ul>
</div>
<div class='card'><h2>Admission slices</h2>{render_table(density_summary, digits_cols={'band_pass_mean_net_bps':2,'baseline_mean_net_bps':2,'band_pass_uplift_vs_baseline_bps':2,'band_pass_trades_per_active_day':2})}</div>
<div class='card'><h2>Pooled recent-slice summary</h2>{render_table(pooled_summary[['window_days','variant','trades','mean_net_bps','total_net_bps','active_days']], digits_cols={'mean_net_bps':2,'total_net_bps':2})}</div>
<div class='card'><h2>Band-pass asset breakdown</h2>{render_table(asset_summary[['window_days','symbol','band_pass_trades','band_pass_mean_net_bps','band_pass_total_net_bps','band_pass_active_days']], digits_cols={'band_pass_mean_net_bps':2,'band_pass_total_net_bps':2})}</div>
<div class='card'><h2>轻量 scorecard</h2>{render_table(scorecard)}</div>
<div class='card'><h2>最短读法</h2><ul>
<li>如果 30/60/90 天 recent slices 都继续保留 <code>band_pass &gt; baseline</code>，而且聚合后每天仍有数笔有效触发，那它就已经不像“好看但跑不起来”的研究口袋。</li>
<li>这一步不是 runner 验证本身，而是更诚实地回答：它有没有资格占用接下来 Paper launch 的 3 轮预算。</li>
</ul></div>
"""
    write_html(SITE_DIR / 'launch_admission_bar.html', title, body)
    write_html(READING_PATH, title, body)
    write_html(SITE_DIR / 'report.html', title, body)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
