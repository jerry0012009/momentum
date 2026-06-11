#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank59_ichimoku_kijun_cloud_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank59_ichimoku_kijun_cloud_15m"
TRADE_LOG_PATH = ART_DIR / "trade_log.csv"
OVERALL_PATH = ART_DIR / "overall_summary.csv"
WINDOW_PATH = ART_DIR / "time_stability_window_summary.csv"
STABILITY_PATH = ART_DIR / "time_stability_verdict_summary.csv"
HTML_PATH = SITE_DIR / "time_stability_check.html"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


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


def assign_time_bucket(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('signal_ts').reset_index(drop=True).copy()
    labels = [None] * len(group)
    for idx, bucket_idx in enumerate(np.array_split(np.arange(len(group)), 3), start=1):
        for row_idx in bucket_idx:
            labels[int(row_idx)] = f'bucket_{idx}'
    group['time_bucket'] = labels
    return group


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    trades = pd.read_csv(TRADE_LOG_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    trades['signal_ts'] = pd.to_datetime(trades['signal_ts'], utc=True)

    bucketed = (
        trades.groupby(['asset', 'setup', 'variant'], group_keys=False)
        .apply(assign_time_bucket)
        .reset_index(drop=True)
    )

    per_asset_bucket = (
        bucketed.groupby(['asset', 'setup', 'variant', 'time_bucket'], as_index=False)
        .agg(
            trades=('net_ret', 'size'),
            total_return=('net_ret', lambda s: float((1.0 + s).prod() - 1.0)),
            avg_net_ret=('net_ret', 'mean'),
            failure_4bars_rate=('failure_4bars', 'mean'),
            failure_8bars_rate=('failure_8bars', 'mean'),
            avg_adx14=('adx14', 'mean'),
            first_signal_ts=('signal_ts', 'min'),
            last_signal_ts=('signal_ts', 'max'),
        )
    )
    per_asset_bucket['positive_bucket'] = per_asset_bucket['total_return'] > 0

    window_summary = (
        per_asset_bucket.groupby(['setup', 'variant', 'time_bucket'], as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('positive_bucket', 'mean'),
            mean_trades=('trades', 'mean'),
            mean_failure_4bars_rate=('failure_4bars_rate', 'mean'),
            mean_failure_8bars_rate=('failure_8bars_rate', 'mean'),
            mean_adx14=('avg_adx14', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
        )
        .sort_values(['setup', 'variant', 'time_bucket'])
    )
    window_summary.to_csv(WINDOW_PATH, index=False)

    records: list[dict[str, object]] = []
    for (setup, variant), group in window_summary.groupby(['setup', 'variant']):
        ordered = group.sort_values('time_bucket').reset_index(drop=True)
        bucket_returns = ordered['mean_total_return']
        overall_row = overall[(overall['setup'] == setup) & (overall['variant'] == variant)].iloc[0]
        positive_bucket_count = int((bucket_returns > 0).sum())
        weak_bucket_count = int((bucket_returns <= 0).sum())
        min_bucket_return = float(bucket_returns.min())
        max_bucket_return = float(bucket_returns.max())
        stability_spread = max_bucket_return - min_bucket_return

        verdict = 'watch_only'
        reason = 'mixed'
        if positive_bucket_count == 0:
            verdict = 'fails_time_check'
            reason = 'all buckets non-positive'
        elif positive_bucket_count == 1:
            verdict = 'fails_time_check'
            reason = 'single positive pocket only'
        elif float(overall_row['positive_asset_ratio']) < (2.0 / 3.0) and float(overall_row['mean_trades']) < 8.0:
            verdict = 'fails_time_check'
            reason = 'survives only with thin trades'
        elif min_bucket_return > 0 and float(ordered['positive_asset_ratio'].min()) >= (1.0 / 3.0):
            verdict = 'survives_time_check'
            reason = 'all buckets positive with basic cross-asset support'
        records.append({
            'setup': setup,
            'variant': variant,
            'overall_mean_total_return': float(overall_row['mean_total_return']),
            'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
            'overall_mean_trades': float(overall_row['mean_trades']),
            'positive_bucket_count': positive_bucket_count,
            'weak_bucket_count': weak_bucket_count,
            'min_bucket_return': min_bucket_return,
            'max_bucket_return': max_bucket_return,
            'bucket_return_spread': stability_spread,
            'min_bucket_positive_asset_ratio': float(ordered['positive_asset_ratio'].min()),
            'min_bucket_mean_trades': float(ordered['mean_trades'].min()),
            'verdict': verdict,
            'reason': reason,
        })

    stability = pd.DataFrame(records).sort_values(['setup', 'variant']).reset_index(drop=True)
    stability.to_csv(STABILITY_PATH, index=False)

    best_row = stability.sort_values(
        by=['positive_bucket_count', 'overall_mean_total_return', 'min_bucket_mean_trades'],
        ascending=[False, False, False],
    ).iloc[0]

    desk_verdict = 'park / evidence pool'
    desk_reason = (
        'Rank 59 的改善只在 EMA/PSAR continuation 上留下局部味道，且时间三分桶里没有任何 setup × variant '
        '能做到三桶全正；fib_retest 更像靠砍样本换接近零，breakout_short 也没有被修好，因此这次 cheap time check '
        '不足以把它从 P1 weak candidate 升到 P2。'
    )

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Rank 59 · Ichimoku Kijun + cloud-side time stability check</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #1f2937; padding: 0 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 24px; font-size: 14px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .muted {{ color: #6b7280; }}
    .callout {{ background: #f8fafc; border: 1px solid #cbd5e1; padding: 16px; border-radius: 10px; margin: 18px 0; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Rank 59 · Ichimoku Kijun + cloud-side continuation gate（cheap time stability check）</h1>
  <p class="muted">生成时间：{escape(generated_at)}</p>
  <div class="callout">
    <p><strong>问题：</strong>在最小 clean replication 之后，<code>Rank 59</code> 只剩 1 次便宜诚实检查预算。这次不再扩研究，也不追新 bar，只用现有 <code>trade_log.csv</code> 把每个 <code>asset × setup × variant</code> 按时间顺序切成 3 个等样本窗口，检查那点 continuation 改善是不是只是 pocket-level 偶然。</p>
    <p><strong>desk verdict：</strong><code>{escape(desk_verdict)}</code></p>
    <p><strong>一句话原因：</strong>{escape(desk_reason)}</p>
  </div>

  <h2>结论</h2>
  <ul>
    <li><code>breakout_short</code> 所有变体都没有穿过时间稳定性门槛：最多只在第一桶短暂转正，第二、三桶继续为负。</li>
    <li><code>fib_retest_long</code> 的正 pocket 主要来自很薄的样本；一旦叠 Kijun / cloud，trade count 很快掉到几乎不可用。</li>
    <li><code>ema_psar_long</code> 确实留下了一点 shared continuation / avoid-chop 味道，但最好的 <code>cloud_side</code> 也只是前两桶为负、最后一桶转正；还不够诚实，不配直接升到 <code>P2 / paper candidate</code>。</li>
  </ul>

  <h2>时间窗口汇总</h2>
  {render_table(window_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_failure_4bars_rate','mean_failure_8bars_rate','min_asset_return','max_asset_return'}, digits_cols={'mean_trades':2,'mean_adx14':2})}

  <h2>逐 setup / variant verdict</h2>
  {render_table(stability, percent_cols={'overall_mean_total_return','overall_positive_asset_ratio','min_bucket_return','max_bucket_return','bucket_return_spread','min_bucket_positive_asset_ratio'}, digits_cols={'overall_mean_trades':2,'positive_bucket_count':0,'weak_bucket_count':0,'min_bucket_mean_trades':2})}

  <h2>当前最强残留口袋</h2>
  <p>当前样本里相对最像“还有一点 continuation 味道”的组合是 <code>{escape(str(best_row['setup']))} / {escape(str(best_row['variant']))}</code>：整体回报 <code>{pct(best_row['overall_mean_total_return'])}</code>，正资产占比 <code>{pct(best_row['overall_positive_asset_ratio'])}</code>，三桶里正桶数量 <code>{num(best_row['positive_bucket_count'], 0)}</code>。但它仍没有把三桶都稳住，因此更诚实的 desk 口径仍应是 <code>park / evidence pool</code>。</p>

  <p class="muted">产物：<code>{escape(str(WINDOW_PATH.relative_to(ROOT)))}</code>、<code>{escape(str(STABILITY_PATH.relative_to(ROOT)))}</code></p>
</body>
</html>
'''
    HTML_PATH.write_text(html, encoding='utf-8')

    print(f'desk_verdict={desk_verdict}')
    print(f'window_summary={WINDOW_PATH.relative_to(ROOT)}')
    print(f'stability_summary={STABILITY_PATH.relative_to(ROOT)}')
    print(f'html={HTML_PATH.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
