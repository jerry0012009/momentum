#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank110_psar_preflip_reclaim_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank110_psar_preflip_reclaim_15m'
READING_DIR = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout'
TRADE_LOG_PATH = ART_DIR / 'trade_log.csv'
OVERALL_PATH = ART_DIR / 'overall_summary.csv'
WINDOW_PATH = ART_DIR / 'time_stability_window_summary.csv'
ASSET_WINDOW_PATH = ART_DIR / 'time_stability_asset_window_summary.csv'
VERDICT_PATH = ART_DIR / 'time_stability_verdict_summary.csv'
SUMMARY_JSON = ART_DIR / 'time_stability_summary.json'
HTML_PATH = SITE_DIR / 'time_stability_check.html'
READING_PATH = READING_DIR / 'rank110_psar_preflip_reclaim_time_stability.html'
PRIMARY_VARIANT = 'preflip_reclaim_long_only'
SECONDARY_VARIANT = 'preflip_reclaim_symmetric'
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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding='utf-8',
    )


def assign_half(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('signal_time').reset_index(drop=True).copy()
    labels = [None] * len(group)
    for idx, rows in enumerate(np.array_split(np.arange(len(group)), 2), start=1):
        label = 'older_half' if idx == 1 else 'recent_half'
        for row_idx in rows:
            labels[int(row_idx)] = label
    group['time_half'] = labels
    return group


def choose_verdict(primary_verdict: pd.Series, sym_verdict: pd.Series | None) -> tuple[str, str]:
    if (
        float(primary_verdict['older_half_mean_total_return']) > 0
        and float(primary_verdict['recent_half_mean_total_return']) > 0
        and float(primary_verdict['min_half_positive_asset_ratio']) >= 2 / 3
        and float(primary_verdict['recent_half_mean_false_follow_4bars']) <= 0.52
        and float(primary_verdict['overall_trade_count_retention']) >= 0.35
    ):
        return 'promote_to_P2 / paper candidate', 'long-only 版本两半窗都站住脚，且 retention 没塌到失真，可以升到 paper candidate。'
    if (
        float(primary_verdict['recent_half_mean_total_return']) <= 0
        or float(primary_verdict['recent_half_positive_asset_ratio']) == 0.0
        or float(primary_verdict['bucket_return_spread']) < -0.02
    ):
        return 'park / evidence pool', 'long-only 改善只剩 older-half pocket；recent half 已回到 0/3 正资产、跨资产平均总收益转负，时间稳定性不过关。'
    if sym_verdict is not None and float(sym_verdict['overall_trade_count_retention']) < 0.20:
        return 'park / evidence pool', '对称版本只剩极薄样本，连 cheap time-stability 都不够诚实；这条线应直接压回 park。'
    return 'keep_P1 / evidence_pool', 'long-only 还有一点过滤味道，但时间维度没站稳；保留证据即可，不再继续占默认主资源位。'


def summarize_variant(trades: pd.DataFrame, overall_row: pd.Series, variant: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    subset = trades[trades['variant'] == variant].copy()
    subset = subset.groupby('asset', group_keys=False).apply(assign_half).reset_index(drop=True)

    per_asset_half = (
        subset.groupby(['asset', 'time_half'], as_index=False)
        .agg(
            trades=('net_return', 'size'),
            total_return=('net_return', 'sum'),
            mean_net_return=('net_return', 'mean'),
            median_net_return=('net_return', 'median'),
            win_rate=('net_return', lambda s: float((s > 0).mean())),
            false_follow_4bars_rate=('false_follow_through_4bars', 'mean'),
            first_signal=('signal_time', 'min'),
            last_signal=('signal_time', 'max'),
        )
        .sort_values(['time_half', 'asset'])
        .reset_index(drop=True)
    )
    per_asset_half['positive_half'] = per_asset_half['total_return'] > 0

    half_summary = (
        per_asset_half.groupby('time_half', as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('positive_half', 'mean'),
            mean_trade_count=('trades', 'mean'),
            mean_net_return=('mean_net_return', 'mean'),
            median_net_return=('median_net_return', 'mean'),
            mean_win_rate=('win_rate', 'mean'),
            mean_false_follow_4bars=('false_follow_4bars_rate', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
        )
        .sort_values('time_half')
        .reset_index(drop=True)
    )

    older = half_summary[half_summary['time_half'] == 'older_half'].iloc[0]
    recent = half_summary[half_summary['time_half'] == 'recent_half'].iloc[0]
    verdict = pd.Series({
        'variant': variant,
        'overall_mean_net_return': float(overall_row['mean_net_return']),
        'overall_mean_total_return': float(overall_row['mean_total_return']),
        'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
        'overall_trade_count_retention': float(overall_row['trade_count_retention']),
        'overall_false_follow_4bars_rate': float(overall_row['false_follow_through_4bars']),
        'older_half_mean_total_return': float(older['mean_total_return']),
        'recent_half_mean_total_return': float(recent['mean_total_return']),
        'older_half_positive_asset_ratio': float(older['positive_asset_ratio']),
        'recent_half_positive_asset_ratio': float(recent['positive_asset_ratio']),
        'older_half_mean_false_follow_4bars': float(older['mean_false_follow_4bars']),
        'recent_half_mean_false_follow_4bars': float(recent['mean_false_follow_4bars']),
        'min_half_positive_asset_ratio': float(min(older['positive_asset_ratio'], recent['positive_asset_ratio'])),
        'bucket_return_spread': float(recent['mean_total_return'] - older['mean_total_return']),
    })
    return per_asset_half, half_summary, verdict


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    trades = pd.read_csv(TRADE_LOG_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    trades['signal_time'] = pd.to_datetime(trades['signal_time'], utc=True)

    primary_overall = overall[overall['variant'] == PRIMARY_VARIANT].iloc[0]
    sym_overall = overall[overall['variant'] == SECONDARY_VARIANT].iloc[0]

    primary_asset_half, primary_half, primary_verdict = summarize_variant(trades, primary_overall, PRIMARY_VARIANT)
    sym_asset_half, sym_half, sym_verdict = summarize_variant(trades, sym_overall, SECONDARY_VARIANT)

    asset_window = pd.concat([
        primary_asset_half.assign(variant=PRIMARY_VARIANT),
        sym_asset_half.assign(variant=SECONDARY_VARIANT),
    ], ignore_index=True)
    asset_window.to_csv(ASSET_WINDOW_PATH, index=False)

    half_window = pd.concat([
        primary_half.assign(variant=PRIMARY_VARIANT),
        sym_half.assign(variant=SECONDARY_VARIANT),
    ], ignore_index=True)
    half_window = half_window[['variant', 'time_half', 'mean_total_return', 'positive_asset_ratio', 'mean_trade_count', 'mean_net_return', 'median_net_return', 'mean_win_rate', 'mean_false_follow_4bars', 'min_asset_return', 'max_asset_return']]
    half_window.to_csv(WINDOW_PATH, index=False)

    verdict_df = pd.DataFrame([primary_verdict.to_dict(), sym_verdict.to_dict()]).sort_values('variant').reset_index(drop=True)
    verdict_df.to_csv(VERDICT_PATH, index=False)

    hard_verdict, why = choose_verdict(primary_verdict, sym_verdict)
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'candidate': 'Rank 110 / PSAR pre-flip SAR dot reclaim gate',
        'light_stability_pack_check': 'time_stability_recent_vs_older_half',
        'hard_verdict': hard_verdict,
        'why': why,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    title = 'Rank 110 · PSAR pre-flip SAR dot reclaim gate（time stability check）'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(summary['generated_at_utc'])}</p>
<div class='card'>
  <span class='pill'>Run 2</span><span class='pill'>Light Stability Pack</span><span class='pill'>time stability</span>
  <p><strong>desk verdict：</strong><code>{escape(hard_verdict)}</code></p>
  <p><strong>一句话原因：</strong>{escape(why)}</p>
  <ul>
    <li><code>{PRIMARY_VARIANT}</code>：older half 跨资产平均总收益 <strong>{pct(primary_verdict['older_half_mean_total_return'])}</strong>，recent half 直接回到 <strong>{pct(primary_verdict['recent_half_mean_total_return'])}</strong>，而且 recent half 正资产占比只有 <strong>{pct(primary_verdict['recent_half_positive_asset_ratio'])}</strong>。</li>
    <li><code>{SECONDARY_VARIANT}</code>：看上去还有一点正收益，但总 retention 只剩 <strong>{pct(sym_verdict['overall_trade_count_retention'])}</strong>，更像样本被砍薄后的 pocket，不够拿来救主 verdict。</li>
    <li>翻成人话：这条线不是完全没料，但“有料”的部分主要停留在 older-half + long-side pocket；一到 recent half 就失真，不够继续占 active Scout 主资源位。</li>
  </ul>
</div>
<div class='card'>
  <h2>time-half summary</h2>
  {render_table(half_window, percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate','mean_false_follow_4bars','min_asset_return','max_asset_return'}, bps_cols={'mean_net_return','median_net_return'}, digits_cols={'mean_trade_count':1})}
</div>
<div class='card'>
  <h2>per-asset half summary</h2>
  {render_table(asset_window[['variant','asset','time_half','trades','total_return','mean_net_return','win_rate','false_follow_4bars_rate']], percent_cols={'total_return','win_rate','false_follow_4bars_rate'}, bps_cols={'mean_net_return'}, digits_cols={'trades':0})}
</div>
<div class='card'>
  <h2>verdict summary</h2>
  {render_table(verdict_df, percent_cols={'overall_mean_net_return','overall_mean_total_return','overall_positive_asset_ratio','overall_trade_count_retention','overall_false_follow_4bars_rate','older_half_mean_total_return','recent_half_mean_total_return','older_half_positive_asset_ratio','recent_half_positive_asset_ratio','older_half_mean_false_follow_4bars','recent_half_mean_false_follow_4bars','min_half_positive_asset_ratio','bucket_return_spread'})}
</div>
<div class='card'>
  <h2>reader-facing 结论</h2>
  <ul>
    <li>long-only 版本不是完全虚假：older half 的 BTC / SOL 还留下了过滤改善味道。</li>
    <li>但 recent half 三个币的总收益全部转负，说明它并不是能稳定穿过时间切片的 admission gate。</li>
    <li>因此这轮 cheap check 做完后，Rank 110 默认应直接压回 <code>park / evidence pool</code>，下一手回 fresh paper / repo intake reserve，而不是继续磨第三轮近义检查。</li>
  </ul>
  <p><a href='report.html'>返回主报告</a> · <a href='../../reading/repo_scout/rank110_psar_preflip_reclaim_time_stability.html'>阅读版说明</a></p>
</div>
"""
    write_html(HTML_PATH, title, body)

    reading_body = f"""
<h1>Rank 110 · PSAR pre-flip SAR dot reclaim gate · time stability check</h1>
<p class='muted'>这轮不追新 bar、不改规则，只复用上轮 clean replication 的同一份样本，检查 `pre-flip reclaim` 的 long-only 改善是不是稳定的。</p>
<div class='card'>
  <p><strong>Hard verdict：</strong><code>{escape(hard_verdict)}</code></p>
  <p>{escape(why)}</p>
  <ul>
    <li><code>{PRIMARY_VARIANT}</code>：older half 还有点过滤味道，但 recent half 已经掉回 0/3 正资产，跨资产平均总收益约 {pct(primary_verdict['recent_half_mean_total_return'])}。</li>
    <li><code>{SECONDARY_VARIANT}</code>：表面结果更好看，但 retention 只剩 {pct(sym_verdict['overall_trade_count_retention'])}，本质上还是过薄样本。</li>
    <li>所以这条线当前更适合留成 long-side note / evidence，而不是继续占 Scout fast lane。</li>
  </ul>
</div>
<div class='card'>
  <h2>关键表格</h2>
  {render_table(half_window[['variant','time_half','mean_total_return','positive_asset_ratio','mean_trade_count','mean_net_return','mean_false_follow_4bars']], percent_cols={'mean_total_return','positive_asset_ratio','mean_false_follow_4bars'}, bps_cols={'mean_net_return'}, digits_cols={'mean_trade_count':1})}
</div>
"""
    write_html(READING_PATH, 'Rank 110 PSAR pre-flip reclaim time stability', reading_body)

    print(f"desk_verdict={hard_verdict}")
    print(f"window_summary={WINDOW_PATH.relative_to(ROOT)}")
    print(f"asset_window_summary={ASSET_WINDOW_PATH.relative_to(ROOT)}")
    print(f"verdict_summary={VERDICT_PATH.relative_to(ROOT)}")
    print(f"html={HTML_PATH.relative_to(ROOT)}")
    print(f"reading={READING_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
