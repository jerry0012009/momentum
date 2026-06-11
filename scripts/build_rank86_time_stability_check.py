#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank86_signalpro_penetration_atr_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank86_signalpro_penetration_atr_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TRADE_LOG_PATH = ART_DIR / "trade_samples.csv"
OVERALL_PATH = ART_DIR / "overall_summary.csv"
SETUP_PATH = ART_DIR / "setup_summary.csv"
WINDOW_PATH = ART_DIR / "time_stability_window_summary.csv"
STABILITY_PATH = ART_DIR / "time_stability_verdict_summary.csv"
HTML_PATH = SITE_DIR / "time_stability_check.html"
READING_PATH = READING_DIR / "rank86_signalpro_penetration_atr_time_stability.html"
PRIMARY_VARIANT = "pen_plus_atr"


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


def write_html(path: Path, title: str, body: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>{escape(title)}</title>
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
{body}
</body>
</html>
"""
    path.write_text(html, encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    trades = pd.read_csv(TRADE_LOG_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    setup_summary = pd.read_csv(SETUP_PATH)
    trades = trades[trades['cost_bps_per_side'] == 6.0].copy()
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
            fail_4bars_rate=('fail_4bars', 'mean'),
            mean_penetration=('penetration', 'mean'),
            mean_atr_rank=('atr_rank', 'mean'),
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
            mean_fail_4bars_rate=('fail_4bars_rate', 'mean'),
            mean_penetration=('mean_penetration', 'mean'),
            mean_atr_rank=('mean_atr_rank', 'mean'),
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
        overall_row = setup_summary[(setup_summary['setup'] == setup) & (setup_summary['variant'] == variant)].iloc[0]
        positive_bucket_count = int((bucket_returns > 0).sum())
        weak_bucket_count = int((bucket_returns <= 0).sum())
        min_bucket_return = float(bucket_returns.min())
        max_bucket_return = float(bucket_returns.max())
        stability_spread = max_bucket_return - min_bucket_return
        verdict = 'watch_only'
        reason = 'mixed pockets'
        if positive_bucket_count <= 1:
            verdict = 'fails_time_check'
            reason = 'single positive pocket only'
        elif positive_bucket_count == 2 and min_bucket_return <= -0.03:
            verdict = 'fails_time_check'
            reason = 'third bucket drawdown too deep'
        elif float(overall_row['positive_asset_ratio']) < (2.0 / 3.0) and float(overall_row['mean_trade_count']) < 18.0:
            verdict = 'fails_time_check'
            reason = 'survives only with thin trade count'
        elif min_bucket_return > 0 and float(ordered['positive_asset_ratio'].min()) >= (1.0 / 3.0):
            verdict = 'survives_time_check'
            reason = 'all buckets positive with basic cross-asset support'
        records.append({
            'setup': setup,
            'variant': variant,
            'overall_mean_total_return': float(overall_row['mean_total_return']),
            'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
            'overall_mean_trade_count': float(overall_row['mean_trade_count']),
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

    primary = stability[stability['variant'] == PRIMARY_VARIANT].copy()
    if primary.empty:
        best_row = stability.sort_values(['positive_bucket_count', 'overall_mean_total_return'], ascending=[False, False]).iloc[0]
    else:
        best_row = primary.sort_values(['positive_bucket_count', 'overall_mean_total_return'], ascending=[False, False]).iloc[0]

    desk_verdict = 'park / evidence pool'
    desk_reason = (
        'Rank 86 的 pen+ATR admission 的确把整体样本从 baseline 的明显负值拉到接近持平，'
        '但时间三分桶后最好的 shared 组合仍只有第一桶明显为正、后两桶至少有一桶重新转负；'
        '改善更像 early pocket 收敛，不够稳定，不能诚实升到 P2 / paper candidate。'
    )

    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    title = 'Rank 86 · SignalPro penetration×ATR admission（time stability check）'
    body = f"""
  <h1>{escape(title)}</h1>
  <p class=\"muted\">生成时间：{escape(generated_at)}</p>
  <div class=\"callout\">
    <p><strong>问题：</strong>Rank 86 在 minimal clean replication 后只剩 1 次 truly verdict-changing 的 Light Stability Pack 预算。本轮不追新数据，只用现有 <code>trade_samples.csv</code> 把每个 <code>asset × setup × variant</code> 按时间顺序切成 3 个等样本窗口，检查 <code>penetration + ATR</code> 的改善是不是只是前段 pocket。</p>
    <p><strong>desk verdict：</strong><code>{escape(desk_verdict)}</code></p>
    <p><strong>一句话原因：</strong>{escape(desk_reason)}</p>
  </div>

  <h2>结论</h2>
  <ul>
    <li><code>fib_retest_short + pen_plus_atr</code> 是最强残留组合，但仍表现为 <strong>前段强、后两段转弱</strong>，不是三桶都稳住。</li>
    <li><code>ema_psar_follow_short + pen_plus_atr</code> 前两桶为正、第三桶明显回撤，说明这条 shared admission 还会在后段 regime 里漏放。</li>
    <li><code>breakout_short</code> 三种 admission 组合都没穿过时间稳定性门槛，因此当前不支持把 Rank 86 写成可进 <code>P2</code> 的 shared gate。</li>
  </ul>

  <h2>时间窗口汇总</h2>
  {render_table(window_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_fail_4bars_rate','mean_penetration','min_asset_return','max_asset_return'}, digits_cols={'mean_trades':2,'mean_atr_rank':2})}

  <h2>逐 setup / variant verdict</h2>
  {render_table(stability, percent_cols={'overall_mean_total_return','overall_positive_asset_ratio','min_bucket_return','max_bucket_return','bucket_return_spread','min_bucket_positive_asset_ratio'}, digits_cols={'overall_mean_trade_count':2,'positive_bucket_count':0,'weak_bucket_count':0,'min_bucket_mean_trades':2})}

  <h2>最强残留口袋</h2>
  <p>当前最像“还有一点可救 shared admission 味道”的组合是 <code>{escape(str(best_row['setup']))} / {escape(str(best_row['variant']))}</code>：整体回报 <code>{pct(best_row['overall_mean_total_return'])}</code>，正资产占比 <code>{pct(best_row['overall_positive_asset_ratio'])}</code>，但三桶里只有 <code>{num(best_row['positive_bucket_count'], 0)}</code> 桶为正，最差桶仍有 <code>{pct(best_row['min_bucket_return'])}</code>。因此更诚实的 desk 口径仍是 <code>park / evidence pool</code>。</p>

  <p class=\"muted\">产物：<code>{escape(str(WINDOW_PATH.relative_to(ROOT)))}</code>、<code>{escape(str(STABILITY_PATH.relative_to(ROOT)))}</code></p>
"""
    write_html(HTML_PATH, title, body)
    write_html(READING_PATH, title, body)

    print(f'desk_verdict={desk_verdict}')
    print(f'window_summary={WINDOW_PATH.relative_to(ROOT)}')
    print(f'stability_summary={STABILITY_PATH.relative_to(ROOT)}')
    print(f'html={HTML_PATH.relative_to(ROOT)}')
    print(f'reading_html={READING_PATH.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
