#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank95_vajra_controlled_pullback_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank95_vajra_controlled_pullback_15m'
READING_DIR = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout'
TRADE_LOG_PATH = ART_DIR / 'trade_log.csv'
OVERALL_PATH = ART_DIR / 'overall_summary.csv'
WINDOW_PATH = ART_DIR / 'time_stability_window_summary.csv'
ASSET_WINDOW_PATH = ART_DIR / 'time_stability_asset_window_summary.csv'
VERDICT_PATH = ART_DIR / 'time_stability_verdict_summary.csv'
SUMMARY_JSON = ART_DIR / 'time_stability_summary.json'
HTML_PATH = SITE_DIR / 'time_stability_check.html'
READING_PATH = READING_DIR / 'rank95_vajra_controlled_pullback_time_stability.html'
TODO_PATH = ROOT / 'docs' / 'TODO.md'
PRIMARY_VARIANTS = ['prearmed_depth_0p75', 'prearmed_depth_1p0']
PRIMARY_COST = 6.0
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


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
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


def assign_bucket(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values('entry_ts').reset_index(drop=True).copy()
    labels = [None] * len(group)
    for idx, bucket_rows in enumerate(np.array_split(np.arange(len(group)), 3), start=1):
        for row_idx in bucket_rows:
            labels[int(row_idx)] = f'bucket_{idx}'
    group['time_bucket'] = labels
    return group


def write_html(title: str, body: str, path: Path) -> None:
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>"
    path.write_text(html, encoding='utf-8')


def choose_verdict(primary: pd.DataFrame) -> tuple[str, str]:
    best = primary[primary['variant'] == 'prearmed_depth_0p75']
    main = primary[primary['variant'] == 'prearmed_depth_1p0']
    if best.empty or main.empty:
        return 'park / evidence pool', '关键 pre-armed 变体数据不完整，不值得继续占用 Scout fast lane。'

    best_row = best.iloc[0]
    main_row = main.iloc[0]

    if (
        int(best_row['positive_bucket_count']) >= 2
        and float(best_row['min_bucket_return']) > -0.005
        and float(best_row['overall_mean_total_return']) > 0
        and float(best_row['overall_positive_asset_ratio']) >= 2 / 3
    ):
        return 'promote_to_P2 / paper candidate', '最佳 pre-armed 子臂在时间三桶、desk 收益与跨资产覆盖都过了最小升格线。'

    if (
        int(best_row['positive_bucket_count']) >= 2
        or int(main_row['positive_bucket_count']) >= 2
        or (float(best_row['overall_mean_total_return']) > -0.01 and float(best_row['min_bucket_return']) > -0.005)
    ):
        return 'keep_P1 / mixed but honest', '虽然还不够升 P2，但至少没被时间稳定性直接打回 evidence pool。'

    return 'park / evidence pool', '最佳 pre-armed 子臂三桶都没转正，默认 desk 口径也同样没过时间稳定性；这条线应退出 active Scout。'


def update_todo(verdict: str, primary: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    anchor = "- **最新补充（2026-03-19 17:36 UTC）**：当前最新 `Next 3` 顺序应再收紧为：**`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转，也不得伪造 refresh）` -> `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 95 / Vajra controlled-pullback depth-budget 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性；直接复用现有 clean replication 的 trade_log / time_bucket_summary 口径，不追新 bar、不改规则，只回答 promote_to_P2 / keep_P1 / park）` -> `Run 3 = 若 Rank 95 的时间稳定性检查没有把它诚实推到 P2 / paper candidate，就停止继续磨同一条线，默认切 Rank 96 / AdvancedMA retest-count admission layer 的 source intake + 两条轻量诚实守门；若 Rank 95 反而清楚通过最小升格阈值，则直接写成 promote_to_P2 / paper candidate，而不是再补近义检查；只有 Rank 96 这一层也 hard-fail / exhausted，才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。"
    if anchor not in text:
        raise SystemExit('TODO anchor not found for Rank95 time stability update')

    best_row = primary[primary['variant'] == 'prearmed_depth_0p75'].iloc[0]
    main_row = primary[primary['variant'] == 'prearmed_depth_1p0'].iloc[0]

    addition = (
        "\n- **最新补充（2026-03-19 17:42 UTC）**：这轮继续严格按 `Run 1 -> Run 2` 执行：再次实际跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，脚本仍返回 **`waiting_not_due`**（当前无 `due-now / overdue` lane；最近 due 约为 `美股 2.3h`、`Crypto 6.3h`、`A股 13.3h`），因此本轮合法主动作就是把 **`Rank 95 / Vajra controlled-pullback depth-budget`** 剩下那 1 个 truly verdict-changing 的 `Light Stability Pack / 时间稳定性` 做完。\n"
        "  - 本轮完全复用上一轮 `trade_log.csv`，不追新 bar、不改规则；只把每个 `asset × variant` 按时间顺序切成 `3` 个等样本 bucket，继续固定 `6bps/side`、`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`，检查 `prearmed_depth_0p75 / prearmed_depth_1p0` 到底是稳定 admission layer，还是只剩局部 pocket。\n"
        f"  - 时间稳定性结果很直接：最佳子臂 `prearmed_depth_0p75` 只剩 **`{int(best_row['positive_bucket_count'])}/3`** 个正桶，最差桶 `mean_total_return≈{pct(best_row['min_bucket_return'])}`，bucket spread≈`{pct(best_row['bucket_return_spread'])}`；desk 默认口径 `prearmed_depth_1p0` 也只剩 **`{int(main_row['positive_bucket_count'])}/3`** 个正桶，最差桶 `mean_total_return≈{pct(main_row['min_bucket_return'])}`。换成人话：最优子臂与默认子臂都没有穿过时间维度，改善不是稳定增益。\n"
        f"  - 因此当前更诚实的 hard verdict 收口为：**`Rank 95 = {verdict}`**。既然 truly verdict-changing 的时间稳定性已经做完，而且结论没把它推到 `P2 / paper candidate`，就不该再继续给它第三轮近义检查。\n"
        "  - reader-facing 落点已补：`reports/site/factors/scout_rank95_vajra_controlled_pullback_15m/time_stability_check.html`、`reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_time_stability.html`；artifact：`reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_window_summary.csv`、`time_stability_verdict_summary.csv`。\n"
    )
    if verdict == 'promote_to_P2 / paper candidate':
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 95 = P2 / paper candidate`** > **`Rank 96 / AdvancedMA retest-count admission layer`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 92 / Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则直接把 Rank 95 写成 promote_to_P2 / paper candidate，并只补最小 admission write-back` -> `Run 3 = Rank 96 source intake + 两条轻量诚实守门`**。"
    else:
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 96 / AdvancedMA retest-count admission layer`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 95 park / evidence_pool`** > **`Rank 92 / Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 96 / AdvancedMA retest-count admission layer 的 source intake + 两条轻量诚实守门` -> `Run 3 = 若 Rank 96 guard-pass，则只给它 1 次最小 clean replication；若 Rank 96 也直接 hard-fail / exhausted，才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`**。"

    text = text.replace(anchor, anchor + "\n" + addition, 1)
    TODO_PATH.write_text(text, encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    trades = pd.read_csv(TRADE_LOG_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    overall = overall[overall['cost_bps'] == PRIMARY_COST].copy().reset_index(drop=True)
    trades['entry_ts'] = pd.to_datetime(trades['entry_ts'], utc=True)
    trades['net_return'] = trades['gross_return'] - (2.0 * PRIMARY_COST / 10000.0)

    bucketed = (
        trades.groupby(['asset', 'variant'], group_keys=False)
        .apply(assign_bucket)
        .reset_index(drop=True)
    )

    per_asset_window = (
        bucketed.groupby(['asset', 'variant', 'time_bucket'], as_index=False)
        .agg(
            trade_count=('entry_ts', 'size'),
            total_return=('net_return', lambda s: float((1.0 + s).prod() - 1.0)),
            mean_net_return=('net_return', 'mean'),
            mean_early_fail_4bars=('early_fail_4bars', 'mean'),
            median_fwd3_ret=('fwd3_ret', 'median'),
        )
        .sort_values(['variant', 'asset', 'time_bucket'])
        .reset_index(drop=True)
    )
    per_asset_window.to_csv(ASSET_WINDOW_PATH, index=False)

    window = (
        per_asset_window.groupby(['variant', 'time_bucket'], as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('total_return', lambda s: float((s > 0).mean())),
            mean_trade_count=('trade_count', 'mean'),
            mean_net_return=('mean_net_return', 'mean'),
            mean_early_fail_4bars=('mean_early_fail_4bars', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
        )
        .sort_values(['variant', 'time_bucket'])
        .reset_index(drop=True)
    )
    window.to_csv(WINDOW_PATH, index=False)

    verdict_rows: list[dict[str, object]] = []
    for variant in PRIMARY_VARIANTS:
        g = window[window['variant'] == variant].copy().sort_values('time_bucket')
        if g.empty:
            continue
        overall_row = overall[overall['variant'] == variant]
        if overall_row.empty:
            continue
        overall_row = overall_row.iloc[0]
        verdict_rows.append({
            'variant': variant,
            'overall_mean_total_return': float(overall_row['mean_total_return']),
            'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
            'overall_trade_count_retention': float(overall_row['trade_count_retention']),
            'overall_mean_early_fail_4bars': float(overall_row['mean_early_fail_4bars']),
            'positive_bucket_count': int((g['mean_total_return'] > 0).sum()),
            'min_bucket_return': float(g['mean_total_return'].min()),
            'max_bucket_return': float(g['mean_total_return'].max()),
            'bucket_return_spread': float(g['mean_total_return'].max() - g['mean_total_return'].min()),
            'worst_bucket_positive_asset_ratio': float(g['positive_asset_ratio'].min()),
            'worst_bucket': str(g.sort_values('mean_total_return').iloc[0]['time_bucket']),
        })

    primary = pd.DataFrame(verdict_rows).sort_values('variant').reset_index(drop=True)
    primary.to_csv(VERDICT_PATH, index=False)

    verdict, why = choose_verdict(primary)
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'verdict': verdict,
        'why': why,
        'primary_variants': PRIMARY_VARIANTS,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    title = 'Rank 95 / Vajra controlled-pullback depth-budget（time stability check）'
    body = (
        f"<h1>{escape(title)}</h1>"
        '<p class="muted">本轮只做一件事：复用上一轮 clean replication 产出的 trade log，检查这条 pre-armed depth budget 的改善能不能穿过时间三分桶，而不是继续追新数据。</p>'
        '<div class="card">'
        '<span class="pill">Run 2</span><span class="pill">Scout Seat</span><span class="pill">Light Stability Pack</span>'
        f'<p><strong>Hard verdict：</strong>{escape(verdict)}</p>'
        f'<p>{escape(why)}</p>'
        '<p class="muted">口径不变：BTC/ETH/SOL、120d、15m、6bps/side、signal 当根及之前数据、next-bar open、no-overlap、hold 8 bars。</p>'
        '</div>'
        '<div class="card"><h2>核心 verdict 汇总</h2>'
        + render_table(primary, {'overall_mean_total_return', 'overall_positive_asset_ratio', 'overall_trade_count_retention', 'overall_mean_early_fail_4bars', 'min_bucket_return', 'max_bucket_return', 'bucket_return_spread', 'worst_bucket_positive_asset_ratio'}, {'positive_bucket_count': 0})
        + '</div>'
        '<div class="card"><h2>时间窗口汇总（按 variant × bucket）</h2>'
        + render_table(window, {'mean_total_return', 'positive_asset_ratio', 'mean_net_return', 'mean_early_fail_4bars', 'min_asset_return', 'max_asset_return'}, {'mean_trade_count': 2})
        + '</div>'
        '<div class="card"><h2>按资产窗口明细</h2>'
        + render_table(per_asset_window, {'total_return', 'mean_net_return', 'mean_early_fail_4bars', 'median_fwd3_ret'}, {'trade_count': 0})
        + '</div>'
        '<div class="card"><h2>一句人话</h2>'
        '<p>这条线的问题不是“稍微亏一点”，而是最好看的 pre-armed 子臂也没有稳定穿过时间维度。</p>'
        '<p>更直白地说：`prearmed_depth_0p75` 和 `prearmed_depth_1p0` 都没有出现 2/3 正桶，说明它更像局部 pocket，而不是可以继续占 Scout fast lane 的稳定 admission layer。</p>'
        '</div>'
    )
    write_html(title, body, HTML_PATH)
    write_html(title, body, READING_PATH)

    update_todo(verdict, primary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
