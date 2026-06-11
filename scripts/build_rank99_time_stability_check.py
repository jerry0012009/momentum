#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'reports' / 'artifacts' / 'quant_digests' / 'zenoclaw_clv_proxy'
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank99_clv_asymmetric_admission_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank99_clv_asymmetric_admission_15m'
READING_DIR = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout'
WINDOW_PATH = ART_DIR / 'time_stability_window_summary.csv'
ASSET_WINDOW_PATH = ART_DIR / 'time_stability_asset_window_summary.csv'
VERDICT_PATH = ART_DIR / 'time_stability_verdict_summary.csv'
SUMMARY_JSON = ART_DIR / 'time_stability_summary.json'
HTML_PATH = SITE_DIR / 'time_stability_check.html'
READING_PATH = READING_DIR / 'rank99_clv_asymmetric_admission_time_stability.html'
PRIMARY_VARIANTS = ['short_clv080', 'short_clv070_plus_volume', 'long_volume_only', 'long_volume_plus_clv']
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
VARIANT_MAP = {
    ('short', 'baseline'): 'short_baseline',
    ('short', 'clv70'): 'short_clv070',
    ('short', 'clv80'): 'short_clv080',
    ('short', 'clv70_vol15'): 'short_clv070_plus_volume',
    ('short', 'vol15'): 'short_volume_only',
    ('long', 'baseline'): 'long_baseline',
    ('long', 'clv70'): 'long_clv070_only',
    ('long', 'clv80'): 'long_clv080_only',
    ('long', 'vol15'): 'long_volume_only',
    ('long', 'clv70_vol15'): 'long_volume_plus_clv',
}


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


def assign_bucket(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('timestamp').reset_index(drop=True).copy()
    labels = [None] * len(group)
    for idx, bucket_rows in enumerate(np.array_split(np.arange(len(group)), 3), start=1):
        for row_idx in bucket_rows:
            labels[int(row_idx)] = f'bucket_{idx}'
    group['time_bucket'] = labels
    return group


def choose_verdict(primary: pd.DataFrame) -> tuple[str, str]:
    short80 = primary[primary['variant'] == 'short_clv080']
    short_combo = primary[primary['variant'] == 'short_clv070_plus_volume']
    long_vol = primary[primary['variant'] == 'long_volume_only']
    long_combo = primary[primary['variant'] == 'long_volume_plus_clv']
    if short80.empty or short_combo.empty or long_vol.empty or long_combo.empty:
        return 'park / evidence pool', '关键 CLV 变体数据不完整，不值得继续占用 Scout fast lane。'

    s80 = short80.iloc[0]
    scombo = short_combo.iloc[0]
    lvol = long_vol.iloc[0]
    lcombo = long_combo.iloc[0]

    if (
        int(s80['positive_bucket_count']) >= 2
        and float(s80['min_bucket_return']) > -0.002
        and float(s80['overall_mean_avg_net_ret_h4']) > 0
        and float(s80['overall_positive_asset_ratio']) >= 2 / 3
        and int(lvol['positive_bucket_count']) >= 2
    ):
        return 'promote_to_P2 / paper candidate', 'short strict-CLV 与 long volume/acceptance 臂都通过时间稳定性，够资格升到 P2。'

    if (
        int(s80['positive_bucket_count']) >= 2
        and float(s80['min_bucket_return']) > -0.002
        and float(s80['overall_mean_avg_net_ret_h4']) > -0.0002
    ):
        return 'keep_P1 / evidence_pool', 'short strict-CLV 至少穿过了时间稳定性底线，但 long 侧仍不足以共同升格。'

    return 'park / evidence pool', 'short strict-CLV 只剩单一时间 pocket，long 侧各臂三桶全负；时间稳定性已把它打回 park。'


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    events = pd.read_csv(SOURCE_DIR / 'event_log.csv')
    overall_raw = pd.read_csv(SOURCE_DIR / 'overall_summary.csv')
    events['timestamp'] = pd.to_datetime(events['timestamp'], utc=True)
    events['variant'] = events.apply(lambda r: VARIANT_MAP.get((r['side'], r['filter']), 'other'), axis=1)
    overall_raw['variant'] = overall_raw.apply(lambda r: VARIANT_MAP.get((r['side'], r['filter']), 'other'), axis=1)

    events = events[events['variant'].isin(PRIMARY_VARIANTS + ['short_baseline', 'long_baseline'])].copy()
    overall = overall_raw[overall_raw['variant'].isin(PRIMARY_VARIANTS + ['short_baseline', 'long_baseline'])].copy()
    overall = overall.rename(columns={
        'mean_n': 'overall_mean_trades',
        'mean_retention': 'overall_trade_count_retention',
        'mean_net_ret_h4': 'overall_mean_avg_net_ret_h4',
        'mean_median_net_ret_h4': 'overall_median_net_ret_h4',
        'mean_win_rate_h4': 'overall_mean_win_rate_h4',
    })

    bucketed = (
        events.groupby(['symbol', 'variant'], group_keys=False)
        .apply(assign_bucket)
        .reset_index(drop=True)
    )

    per_asset_window = (
        bucketed.groupby(['symbol', 'variant', 'time_bucket'], as_index=False)
        .agg(
            trades=('net_ret_h4', 'size'),
            total_return=('net_ret_h4', lambda s: float((1.0 + s).prod() - 1.0)),
            mean_net_ret_h4=('net_ret_h4', 'mean'),
            median_net_ret_h4=('net_ret_h4', 'median'),
            win_rate_h4=('net_ret_h4', lambda s: float((s > 0).mean())),
            avg_aligned_clv=('aligned_clv', 'mean'),
            avg_vol_ratio=('vol_ratio', 'mean'),
            first_ts=('timestamp', 'min'),
            last_ts=('timestamp', 'max'),
        )
        .sort_values(['variant', 'symbol', 'time_bucket'])
        .reset_index(drop=True)
    )
    per_asset_window['positive_bucket'] = per_asset_window['total_return'] > 0
    per_asset_window = per_asset_window.rename(columns={'symbol': 'asset'})
    ASSET_WINDOW_PATH.write_text(per_asset_window.to_csv(index=False), encoding='utf-8')

    window = (
        per_asset_window.groupby(['variant', 'time_bucket'], as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('positive_bucket', 'mean'),
            mean_trade_count=('trades', 'mean'),
            mean_net_ret_h4=('mean_net_ret_h4', 'mean'),
            median_net_ret_h4=('median_net_ret_h4', 'mean'),
            mean_win_rate_h4=('win_rate_h4', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
            mean_aligned_clv=('avg_aligned_clv', 'mean'),
            mean_vol_ratio=('avg_vol_ratio', 'mean'),
        )
        .sort_values(['variant', 'time_bucket'])
        .reset_index(drop=True)
    )
    WINDOW_PATH.write_text(window.to_csv(index=False), encoding='utf-8')

    verdict_rows: list[dict[str, object]] = []
    for variant in PRIMARY_VARIANTS:
        g = window[window['variant'] == variant].copy().sort_values('time_bucket')
        o = overall[overall['variant'] == variant]
        if g.empty or o.empty:
            continue
        o = o.iloc[0]
        verdict_rows.append({
            'variant': variant,
            'overall_mean_avg_net_ret_h4': float(o['overall_mean_avg_net_ret_h4']),
            'overall_positive_asset_ratio': float(o['positive_asset_ratio']),
            'overall_trade_count_retention': float(o['overall_trade_count_retention']),
            'overall_mean_trades': float(o['overall_mean_trades']),
            'positive_bucket_count': int((g['mean_total_return'] > 0).sum()),
            'min_bucket_return': float(g['mean_total_return'].min()),
            'max_bucket_return': float(g['mean_total_return'].max()),
            'bucket_return_spread': float(g['mean_total_return'].max() - g['mean_total_return'].min()),
            'worst_bucket_positive_asset_ratio': float(g['positive_asset_ratio'].min()),
            'worst_bucket': str(g.sort_values('mean_total_return').iloc[0]['time_bucket']),
        })
    verdict_df = pd.DataFrame(verdict_rows).sort_values('variant').reset_index(drop=True)
    VERDICT_PATH.write_text(verdict_df.to_csv(index=False), encoding='utf-8')

    verdict, why = choose_verdict(verdict_df)
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'candidate': 'Rank 99 / CLV asymmetric admission layer',
        'light_stability_pack_check': 'time_stability',
        'hard_verdict': verdict,
        'why': why,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    short80 = verdict_df[verdict_df['variant'] == 'short_clv080'].iloc[0]
    short_combo = verdict_df[verdict_df['variant'] == 'short_clv070_plus_volume'].iloc[0]
    long_vol = verdict_df[verdict_df['variant'] == 'long_volume_only'].iloc[0]
    long_combo = verdict_df[verdict_df['variant'] == 'long_volume_plus_clv'].iloc[0]

    title = 'Rank 99 · CLV asymmetric admission layer（time stability check）'
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(summary['generated_at_utc'])}</p>
<div class='card'>
  <span class='pill'>Run 2</span><span class='pill'>Light Stability Pack</span><span class='pill'>time stability</span>
  <p><strong>desk verdict：</strong><code>{escape(verdict)}</code></p>
  <p><strong>一句话原因：</strong>{escape(why)}</p>
  <ul>
    <li><code>short_clv080</code> 只有 <strong>{int(short80['positive_bucket_count'])}/3</strong> 个正桶，最差桶 <strong>{pct(short80['min_bucket_return'])}</strong>。</li>
    <li><code>short_clv070_plus_volume</code> 也只有 <strong>{int(short_combo['positive_bucket_count'])}/3</strong> 个正桶，最差桶 <strong>{pct(short_combo['min_bucket_return'])}</strong>。</li>
    <li><code>long_volume_only</code> 与 <code>long_volume_plus_clv</code> 都是 <strong>0/3</strong> 正桶，说明 long 侧依旧没被时间维度救回来。</li>
  </ul>
</div>
<div class='card'>
  <h2>time-bucket summary</h2>
  {render_table(window[['variant','time_bucket','mean_total_return','positive_asset_ratio','mean_trade_count','mean_net_ret_h4','mean_win_rate_h4','min_asset_return','max_asset_return']], percent_cols={'mean_total_return','positive_asset_ratio','mean_win_rate_h4','min_asset_return','max_asset_return'}, bps_cols={'mean_net_ret_h4'}, digits_cols={'mean_trade_count':1})}
</div>
<div class='card'>
  <h2>per-asset bucket summary</h2>
  {render_table(per_asset_window[['asset','variant','time_bucket','trades','total_return','mean_net_ret_h4','win_rate_h4','avg_aligned_clv','avg_vol_ratio']], percent_cols={'total_return','win_rate_h4','avg_aligned_clv'}, bps_cols={'mean_net_ret_h4'}, digits_cols={'trades':0,'avg_vol_ratio':2})}
</div>
<div class='card'>
  <h2>逐变体 verdict</h2>
  {render_table(verdict_df, percent_cols={'overall_positive_asset_ratio','overall_trade_count_retention','min_bucket_return','max_bucket_return','bucket_return_spread','worst_bucket_positive_asset_ratio'}, bps_cols={'overall_mean_avg_net_ret_h4'}, digits_cols={'overall_mean_trades':1,'positive_bucket_count':0})}
</div>
<div class='card'>
  <h2>reader-facing 结论</h2>
  <ul>
    <li>strict CLV 的 short 改善不是完全虚假，但更像前段 pocket：一进中段 bucket 就重新转负。</li>
    <li>long 侧不管只看 volume 还是 volume+CLV，三桶都没转正，因此不能把 high-close 包装成 long continuation 充分条件。</li>
    <li>这次 truly verdict-changing 检查做完后，Rank 99 就不该继续占 active Scout 主资源位；下一手应切 fresh intake，而不是再磨同一条线。</li>
  </ul>
  <p><a href='report.html'>返回主报告</a> · <a href='../../reading/repo_scout/rank99_clv_asymmetric_admission_time_stability.html'>阅读版说明</a></p>
</div>
"""
    write_html(HTML_PATH, title, body)

    reading_body = f"""
<h1>Rank 99 · CLV asymmetric admission layer · time stability check</h1>
<p class='muted'>这轮不追新 bar、不改规则，只复用上轮 clean replication 同一份代理事件样本，检查 strict CLV 的 short 改善是不是只是局部 pocket。</p>
<div class='card'>
  <p><strong>Hard verdict：</strong><code>{escape(verdict)}</code></p>
  <p>{escape(why)}</p>
  <ul>
    <li><code>short_clv080</code>：只有 1/3 时间桶为正；第二桶重新明显转负，最差桶约 {pct(short80['min_bucket_return'])}。</li>
    <li><code>short_clv070_plus_volume</code>：同样只有 1/3 时间桶为正；volume 没把中段稳定救回来。</li>
    <li><code>long_volume_only / long_volume_plus_clv</code>：三桶全负，long 侧仍不支持把 CLV-only 或 volume+CLV 写成 continuation 充分条件。</li>
  </ul>
  <p>换成人话：Rank 99 留下的是 short-biased bar-quality 线索，不是能穿过时间稳定性的 shared hard gate。因此这轮应把它压回 <code>park / evidence pool</code>，然后切 fresh repo intake。</p>
</div>
<div class='card'>
  <h2>关键表格</h2>
  {render_table(window[['variant','time_bucket','mean_total_return','positive_asset_ratio','mean_trade_count','mean_net_ret_h4']], percent_cols={'mean_total_return','positive_asset_ratio'}, bps_cols={'mean_net_ret_h4'}, digits_cols={'mean_trade_count':1})}
</div>
"""
    write_html(READING_PATH, 'Rank 99 CLV time stability', reading_body)

    print(f"desk_verdict={verdict}")
    print(f"window_summary={WINDOW_PATH.relative_to(ROOT)}")
    print(f"asset_window_summary={ASSET_WINDOW_PATH.relative_to(ROOT)}")
    print(f"verdict_summary={VERDICT_PATH.relative_to(ROOT)}")
    print(f"html={HTML_PATH.relative_to(ROOT)}")
    print(f"reading={READING_PATH.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
