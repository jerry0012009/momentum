#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank102_impulse_rebreak_continuation_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank102_impulse_rebreak_continuation_15m'
READING_DIR = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout'
TRADE_LOG_PATH = ART_DIR / 'trade_log.csv'
OVERALL_PATH = ART_DIR / 'overall_summary.csv'
WINDOW_PATH = ART_DIR / 'time_stability_window_summary.csv'
ASSET_WINDOW_PATH = ART_DIR / 'time_stability_asset_window_summary.csv'
VERDICT_PATH = ART_DIR / 'time_stability_verdict_summary.csv'
SUMMARY_JSON = ART_DIR / 'time_stability_summary.json'
HTML_PATH = SITE_DIR / 'time_stability_check.html'
READING_PATH = READING_DIR / 'rank102_impulse_rebreak_continuation_time_stability.html'
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px 48px; line-height:1.7; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f"{float(v) * 100:.{digits}f}%"


def bps(v: float | int | None) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f"{float(v) * 10000:.2f} bps"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in bps_cols:
                text = bps(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def assign_half(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('signal_time').reset_index(drop=True).copy()
    labels = [None] * len(group)
    for idx, rows in enumerate(np.array_split(np.arange(len(group)), 2), start=1):
        label = 'older_half' if idx == 1 else 'recent_half'
        for row_idx in rows:
            labels[int(row_idx)] = label
    group['time_half'] = labels
    return group


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding='utf-8',
    )


def choose_verdict(verdict_df: pd.DataFrame) -> tuple[str, str]:
    if verdict_df.empty:
        return 'park / evidence pool', '关键 time-stability 数据不完整，不能继续占用 Scout 主资源位。'
    row = verdict_df.iloc[0]
    if (
        float(row['overall_mean_avg_net_ret']) > 0
        and float(row['older_half_mean_total_return']) > 0
        and float(row['recent_half_mean_total_return']) > 0
        and float(row['min_half_positive_asset_ratio']) >= 2 / 3
        and float(row['min_half_mean_false_follow_4bars']) <= 0.48
    ):
        return 'promote_to_P2 / paper candidate', '两半窗都转正，且跨资产与 false-follow-through 都过了最小升格线。'
    return 'park / evidence pool', 'older half 仍没穿过时间稳定性，跨资产也不是两半都够硬；按 desk 规则应直接收口为 park。'


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    trades = pd.read_csv(TRADE_LOG_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    trades['signal_time'] = pd.to_datetime(trades['signal_time'], utc=True)

    gate = trades[(trades['setup'] == 'breakout_short_signal') & (trades['variant'] == 'impulse_rebreak_gate')].copy()
    gate = (
        gate.groupby('asset', group_keys=False)
        .apply(assign_half)
        .reset_index(drop=True)
    )

    per_asset_half = (
        gate.groupby(['asset', 'time_half'], as_index=False)
        .agg(
            trades=('net_ret', 'size'),
            total_return=('net_ret', lambda s: float((1.0 + s).prod() - 1.0)),
            avg_net_ret=('net_ret', 'mean'),
            median_net_ret=('net_ret', 'median'),
            win_rate=('net_ret', lambda s: float((s > 0).mean())),
            false_follow_4bars_rate=('false_follow_4bars', 'mean'),
            first_signal=('signal_time', 'min'),
            last_signal=('signal_time', 'max'),
        )
        .sort_values(['time_half', 'asset'])
        .reset_index(drop=True)
    )
    per_asset_half['positive_half'] = per_asset_half['total_return'] > 0
    ASSET_WINDOW_PATH.write_text(per_asset_half.to_csv(index=False), encoding='utf-8')

    half_summary = (
        per_asset_half.groupby('time_half', as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('positive_half', 'mean'),
            mean_trade_count=('trades', 'mean'),
            mean_avg_net_ret=('avg_net_ret', 'mean'),
            mean_median_net_ret=('median_net_ret', 'mean'),
            mean_win_rate=('win_rate', 'mean'),
            mean_false_follow_4bars=('false_follow_4bars_rate', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
        )
        .sort_values('time_half')
        .reset_index(drop=True)
    )
    WINDOW_PATH.write_text(half_summary.to_csv(index=False), encoding='utf-8')

    overall_row = overall[(overall['setup'] == 'breakout_short_signal') & (overall['variant'] == 'impulse_rebreak_gate')].iloc[0]
    older = half_summary[half_summary['time_half'] == 'older_half'].iloc[0]
    recent = half_summary[half_summary['time_half'] == 'recent_half'].iloc[0]
    verdict_df = pd.DataFrame([
        {
            'variant': 'impulse_rebreak_gate',
            'overall_mean_avg_net_ret': float(overall_row['avg_net_ret']),
            'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
            'overall_trade_count_retention': float(overall_row['trade_count_retention']),
            'overall_false_follow_4bars_rate': float(overall_row['false_follow_4bars_rate']),
            'older_half_mean_total_return': float(older['mean_total_return']),
            'recent_half_mean_total_return': float(recent['mean_total_return']),
            'older_half_positive_asset_ratio': float(older['positive_asset_ratio']),
            'recent_half_positive_asset_ratio': float(recent['positive_asset_ratio']),
            'older_half_mean_false_follow_4bars': float(older['mean_false_follow_4bars']),
            'recent_half_mean_false_follow_4bars': float(recent['mean_false_follow_4bars']),
            'min_half_positive_asset_ratio': float(min(older['positive_asset_ratio'], recent['positive_asset_ratio'])),
            'bucket_return_spread': float(recent['mean_total_return'] - older['mean_total_return']),
        }
    ])
    VERDICT_PATH.write_text(verdict_df.to_csv(index=False), encoding='utf-8')

    verdict, why = choose_verdict(verdict_df)
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'candidate': 'Rank 102 / retest 后重破 impulse extreme continuation gate',
        'light_stability_pack_check': 'time_stability_recent_vs_older_half',
        'hard_verdict': verdict,
        'why': why,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    title = 'Rank 102 · retest 后重破 impulse extreme continuation gate（time stability check）'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(summary['generated_at_utc'])}</p>
<div class='card'>
  <span class='pill'>Run 2</span><span class='pill'>Light Stability Pack</span><span class='pill'>time stability</span>
  <p><strong>desk verdict：</strong><code>{escape(verdict)}</code></p>
  <p><strong>一句话原因：</strong>{escape(why)}</p>
  <ul>
    <li>older half：跨资产平均总收益 <strong>{pct(older['mean_total_return'])}</strong>，正资产占比 <strong>{pct(older['positive_asset_ratio'])}</strong>，false-follow-through <strong>{pct(older['mean_false_follow_4bars'])}</strong>。</li>
    <li>recent half：跨资产平均总收益 <strong>{pct(recent['mean_total_return'])}</strong>，正资产占比 <strong>{pct(recent['positive_asset_ratio'])}</strong>，false-follow-through <strong>{pct(recent['mean_false_follow_4bars'])}</strong>。</li>
    <li>换成人话：这条 gate 不是完全没料，但明显更像后半窗 pocket；older half 还没有稳定穿门。</li>
  </ul>
</div>
<div class='card'>
  <h2>half summary</h2>
  {render_table(half_summary[['time_half','mean_total_return','positive_asset_ratio','mean_trade_count','mean_avg_net_ret','mean_win_rate','mean_false_follow_4bars','min_asset_return','max_asset_return']], percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_false_follow_4bars','min_asset_return','max_asset_return'}, bps_cols={'mean_avg_net_ret'}, digits_cols={'mean_trade_count':1})}
</div>
<div class='card'>
  <h2>per-asset half summary</h2>
  {render_table(per_asset_half[['asset','time_half','trades','total_return','avg_net_ret','win_rate','false_follow_4bars_rate']], percent_cols={'total_return','win_rate','false_follow_4bars_rate'}, bps_cols={'avg_net_ret'}, digits_cols={'trades':0})}
</div>
<div class='card'>
  <h2>verdict summary</h2>
  {render_table(verdict_df, percent_cols={'overall_positive_asset_ratio','overall_trade_count_retention','overall_false_follow_4bars_rate','older_half_mean_total_return','recent_half_mean_total_return','older_half_positive_asset_ratio','recent_half_positive_asset_ratio','older_half_mean_false_follow_4bars','recent_half_mean_false_follow_4bars','min_half_positive_asset_ratio','bucket_return_spread'}, bps_cols={'overall_mean_avg_net_ret'})}
</div>
<div class='card'>
  <h2>reader-facing 结论</h2>
  <ul>
    <li>`impulse re-break` 在 `breakout_short` 上确实留下了改良味道，但 improvement 主要集中在 recent half，不够稳定。</li>
    <li>older half 里只有 `ETH` 转正，`BTC / SOL` 仍为负；这不足以支撑 shared gate 继续升格为 paper candidate。</li>
    <li>因此这次 cheap honesty check 做完后，按 desk 规则应直接收口为 <code>park / evidence pool</code>，下一手切 Rank 103，而不是继续给 Rank 102 第三轮近义检查。</li>
  </ul>
  <p><a href='report.html'>返回主报告</a> · <a href='../../reading/repo_scout/rank102_impulse_rebreak_continuation_time_stability.html'>阅读版说明</a></p>
</div>
"""
    write_html(HTML_PATH, title, body)

    reading_body = f"""
<h1>Rank 102 · retest 后重破 impulse extreme continuation gate · time stability check</h1>
<p class='muted'>这轮不追新 bar、不改规则，只复用上轮 clean replication 的 `breakout_short + impulse_rebreak_gate` 样本，按 older/recent 两半窗检查它是不是稳定 shared gate。</p>
<div class='card'>
  <p><strong>Hard verdict：</strong><code>{escape(verdict)}</code></p>
  <p>{escape(why)}</p>
  <ul>
    <li>older half：均值仍未真正转强，跨资产只有 1/3 为正，说明最早一半样本还没稳定过门。</li>
    <li>recent half：确实改善明显，但更像后段 pocket，而不是两半都一致的 shared gate。</li>
    <li>因此本轮 cheap check 做完后，应直接把 Rank 102 压回 <code>park / evidence pool</code>，然后切 fresh repo reserve，而不是再磨第三轮近义检查。</li>
  </ul>
</div>
<div class='card'>
  <h2>关键表格</h2>
  {render_table(half_summary[['time_half','mean_total_return','positive_asset_ratio','mean_trade_count','mean_avg_net_ret','mean_false_follow_4bars']], percent_cols={'mean_total_return','positive_asset_ratio','mean_false_follow_4bars'}, bps_cols={'mean_avg_net_ret'}, digits_cols={'mean_trade_count':1})}
</div>
"""
    write_html(READING_PATH, 'Rank 102 impulse re-break time stability', reading_body)

    print(f"desk_verdict={verdict}")
    print(f"window_summary={WINDOW_PATH.relative_to(ROOT)}")
    print(f"asset_window_summary={ASSET_WINDOW_PATH.relative_to(ROOT)}")
    print(f"verdict_summary={VERDICT_PATH.relative_to(ROOT)}")
    print(f"html={HTML_PATH.relative_to(ROOT)}")
    print(f"reading={READING_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
