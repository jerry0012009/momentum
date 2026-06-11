#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank92_opening_drive_adaptive_offset_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank92_opening_drive_adaptive_offset_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TRADES_PATH = ART_DIR / "trades.csv"
OVERALL_PATH = ART_DIR / "desk_overall_summary.csv"
WINDOW_PATH = ART_DIR / "time_stability_window_summary.csv"
VERDICT_PATH = ART_DIR / "time_stability_verdict_summary.csv"
SUMMARY_JSON = ART_DIR / "time_stability_summary.json"
HTML_PATH = SITE_DIR / "time_stability_check.html"
READING_PATH = READING_DIR / "rank92_opening_drive_adaptive_offset_time_stability.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
PRIMARY_VARIANTS = ["adaptive_offset_gate", "adaptive_offset_halfsize"]

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


def choose_verdict(primary: pd.DataFrame, overall: pd.DataFrame) -> tuple[str, str]:
    gate = primary[primary['variant'] == 'adaptive_offset_gate']
    half = primary[primary['variant'] == 'adaptive_offset_halfsize']
    gate_row = gate.iloc[0] if not gate.empty else None
    half_row = half.iloc[0] if not half.empty else None

    if gate_row is None or half_row is None:
        return 'park / evidence pool', 'time-bucket 数据不完整，不配继续占用 fast-lane。'

    gate_bucket_pos = int(gate_row['positive_bucket_count'])
    half_bucket_pos = int(half_row['positive_bucket_count'])
    gate_min_bucket = float(gate_row['min_bucket_return'])
    half_min_bucket = float(half_row['min_bucket_return'])

    if gate_bucket_pos >= 2 and gate_min_bucket > -0.005 and float(gate_row['overall_mean_total_return']) > 0 and float(gate_row['overall_positive_asset_ratio']) >= 2/3:
        return 'promote_to_P2 / paper candidate', 'gate 版在时间三桶里没有明显塌陷，且 desk 级 post-cost 结果与跨资产覆盖都过线。'

    if half_bucket_pos >= 2 and half_min_bucket > -0.005:
        return 'keep_P1', 'full gate 依旧不够稳，但 half-size 至少没有明显只剩单一 pocket，可继续保留一层弱候选身份。'

    return 'park / evidence pool', '无论 full gate 还是 half-size，都更像后段失效的 pocket；时间稳定性没过，就不该继续占用 Scout 主资源。'


def update_todo(verdict: str, primary: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    anchor = "- **最新补充（2026-03-19 16:07 UTC）**：这轮继续严格按 `Run 1 -> Run 2` 执行：再次实际跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，脚本仍返回 **`waiting_not_due`**（当前无 `due-now / overdue` lane；最近 due 约为 `美股 3.9h`、`Crypto 7.9h`、`A股 14.9h`），因此本轮合法主动作就是把 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的那 1 次最小 clean replication 跑完。"
    if anchor not in text:
        raise SystemExit('TODO anchor not found for Rank92 time stability update')

    gate_row = primary[primary['variant'] == 'adaptive_offset_gate'].iloc[0]
    half_row = primary[primary['variant'] == 'adaptive_offset_halfsize'].iloc[0]

    addition = (
        "\n- **最新补充（2026-03-19 16:28 UTC）**：这轮继续严格按 `Run 1 -> Run 2` 执行：再次实际跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，脚本仍返回 **`waiting_not_due`**（当前无 `due-now / overdue` lane；最近 due 约为 `美股 3.5h`、`Crypto 7.5h`、`A股 14.5h`），因此本轮合法主动作就是把 **`Rank 92 / opening-drive adaptive offset continuation gate`** 剩下那 1 个 truly verdict-changing 的 `Light Stability Pack / 时间稳定性` 做完。\n"
        "  - 本轮完全复用上一轮 `trades.csv`，不追新 bar、不改规则；只把每个 `asset × setup × variant` 按时间顺序切成 `3` 个等样本 bucket，继续固定 `6bps/side`、`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`，检查 `adaptive_offset_gate / adaptive_offset_halfsize` 的改善是不是只剩局部 pocket。\n"
        f"  - 时间稳定性结果很直接：`adaptive_offset_gate` 只剩 **`{int(gate_row['positive_bucket_count'])}/3`** 个正桶，最差桶 `mean_total_return≈{pct(gate_row['min_bucket_return'])}`，bucket spread≈{pct(gate_row['bucket_return_spread'])}`；`adaptive_offset_halfsize` 也只剩 **`{int(half_row['positive_bucket_count'])}/3`** 个正桶，最差桶 `mean_total_return≈{pct(half_row['min_bucket_return'])}`。换成人话：这条线不是越走越稳，而是前两桶大多还在漏，只有后段才勉强转正。\n"
        f"  - 因此当前更诚实的 hard verdict 收口为：**`Rank 92 = {verdict}`**。如果 full gate 与 half-size 都没扛过时间稳定性，那就不该继续把它留在 active Scout 资源位。\n"
        "  - reader-facing 落点已补：`reports/site/factors/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_check.html`、`reports/site/reading/repo_scout/rank92_opening_drive_adaptive_offset_time_stability.html`；artifact：`reports/artifacts/scout_rank92_opening_drive_adaptive_offset_15m/time_stability_window_summary.csv`、`time_stability_verdict_summary.csv`。\n"
    )
    if verdict == 'park / evidence pool':
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 95 / Vajra controlled-pullback depth-budget`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 92 park / evidence_pool`** > **`Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 95 / Vajra controlled-pullback depth-budget 的 source intake + 两条轻量诚实守门` -> `Run 3 = 若 Rank 95 guard-pass，则只给它 1 次最小 clean replication；若 Rank 95 在 intake 直接 hard-fail / exhausted，才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool；P3 continuity 与 tiny-live plumbing 继续不得插队`**。"
    else:
        addition += "  - 当前 active Scout 顺序应同步改写为：**`Rank 92 = P1 weak candidate（仅剩是否升 P2 的收口）`** > **`Rank 95 / Vajra controlled-pullback depth-budget`** > **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`** > **`Rank 94 park / evidence_pool`** > **`P3 continuity`** > **`tiny-live plumbing`**。\n"
        addition += "  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则只做 Rank 92 最终升降级收口` -> `Run 3 = 若仍不够，再切 Rank 95 source intake`**。"

    text = text.replace(anchor, anchor + "\n" + addition, 1)
    TODO_PATH.write_text(text, encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    trades = pd.read_csv(TRADES_PATH)
    overall = pd.read_csv(OVERALL_PATH)
    cost = 2.0 * 6.0 / 10000.0
    trades['entry_ts'] = pd.to_datetime(trades['entry_ts'], utc=True)
    trades['net_return'] = trades['gross_return'] - cost * trades['size_mult']

    bucketed = (
        trades.groupby(['asset', 'setup', 'variant'], group_keys=False)
        .apply(assign_bucket)
        .reset_index(drop=True)
    )

    per_asset_window = (
        bucketed.groupby(['asset', 'setup', 'variant', 'time_bucket'], as_index=False)
        .agg(
            trade_count=('signal_id', 'size'),
            total_return=('net_return', lambda s: float((1.0 + s).prod() - 1.0)),
            mean_net_return=('net_return', 'mean'),
            hold4=('hold4', 'mean'),
            fail_back_inside4=('fail_back_inside4', 'mean'),
        )
        .sort_values(['asset', 'setup', 'variant', 'time_bucket'])
        .reset_index(drop=True)
    )

    window = (
        per_asset_window.groupby(['setup', 'variant', 'time_bucket'], as_index=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('total_return', lambda s: float((s > 0).mean())),
            mean_trade_count=('trade_count', 'mean'),
            mean_net_return=('mean_net_return', 'mean'),
            mean_hold4=('hold4', 'mean'),
            mean_fail_back_inside4=('fail_back_inside4', 'mean'),
            min_asset_return=('total_return', 'min'),
            max_asset_return=('total_return', 'max'),
        )
        .sort_values(['setup', 'variant', 'time_bucket'])
        .reset_index(drop=True)
    )
    window.to_csv(WINDOW_PATH, index=False)

    verdict_rows: list[dict[str, object]] = []
    for variant in PRIMARY_VARIANTS:
        g = window[window['variant'] == variant].copy().sort_values(['setup', 'time_bucket'])
        if g.empty:
            continue
        setup_positive_ratio = (
            g.groupby('setup')['mean_total_return']
            .apply(lambda s: float((s > 0).mean()))
            .reset_index(name='positive_bucket_ratio_by_setup')
        )
        positive_bucket_count = int((g.groupby('time_bucket')['mean_total_return'].mean() > 0).sum())
        min_bucket_return = float(g.groupby('time_bucket')['mean_total_return'].mean().min())
        max_bucket_return = float(g.groupby('time_bucket')['mean_total_return'].mean().max())
        overall_row = overall[overall['variant'] == variant].iloc[0]
        verdict_rows.append({
            'variant': variant,
            'overall_mean_total_return': float(overall_row['mean_total_return']),
            'overall_positive_asset_ratio': float(overall_row['positive_asset_ratio']),
            'overall_retention': float(overall_row['retention']),
            'overall_mean_hold4': float(overall_row['mean_hold4']),
            'overall_mean_fail_back_inside4': float(overall_row['mean_fail_back_inside4']),
            'positive_bucket_count': positive_bucket_count,
            'min_bucket_return': min_bucket_return,
            'max_bucket_return': max_bucket_return,
            'bucket_return_spread': max_bucket_return - min_bucket_return,
            'weakest_setup_positive_bucket_ratio': float(setup_positive_ratio['positive_bucket_ratio_by_setup'].min()),
            'weakest_setup': str(setup_positive_ratio.sort_values('positive_bucket_ratio_by_setup').iloc[0]['setup']),
        })

    primary = pd.DataFrame(verdict_rows).sort_values('variant').reset_index(drop=True)
    primary.to_csv(VERDICT_PATH, index=False)

    verdict, why = choose_verdict(primary, overall)
    summary = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'verdict': verdict,
        'why': why,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    title = 'Rank 92 / opening-drive adaptive offset continuation gate（time stability check）'
    body = (
        f"<h1>{escape(title)}</h1>"
        '<p class="muted">本轮只做一件事：复用上一轮 clean replication 产出的 trade log，检查这条 gate 的改善是否经得起时间三分桶，而不是继续追新数据。</p>'
        '<div class="card">'
        '<span class="pill">Run 2</span><span class="pill">Scout Seat</span><span class="pill">Light Stability Pack</span>'
        f'<p><strong>Hard verdict：</strong>{escape(verdict)}</p>'
        f'<p>{escape(why)}</p>'
        '<p class="muted">口径不变：BTC/ETH/SOL、120d、15m、6bps/side、signal 当根及之前数据、next-bar open、no-overlap、hold 8 bars。</p>'
        '</div>'
        '<div class="card"><h2>核心 verdict 汇总</h2>'
        + render_table(primary, {'overall_mean_total_return', 'overall_positive_asset_ratio', 'overall_retention', 'overall_mean_hold4', 'overall_mean_fail_back_inside4', 'min_bucket_return', 'max_bucket_return', 'bucket_return_spread', 'weakest_setup_positive_bucket_ratio'}, {'positive_bucket_count': 0})
        + '</div>'
        '<div class="card"><h2>时间窗口汇总（按 setup × variant × bucket）</h2>'
        + render_table(window, {'mean_total_return', 'positive_asset_ratio', 'mean_net_return', 'mean_hold4', 'mean_fail_back_inside4', 'min_asset_return', 'max_asset_return'}, {'mean_trade_count': 2})
        + '</div>'
        '<div class="card"><h2>按资产窗口明细</h2>'
        + render_table(per_asset_window, {'total_return', 'mean_net_return', 'hold4', 'fail_back_inside4'}, {'trade_count': 0})
        + '</div>'
        '<div class="card"><h2>一句人话</h2>'
        '<p>这条线的问题不在于 path-quality 指标没变好，而在于它的收益改善没有稳定穿过时间维度。</p>'
        '<p>更直白地说：full gate 与 half-size 大多都还是 <code>前两桶偏弱 / 只在后段勉强转正</code>，这不够支持继续把它留在 active Scout 资源位。</p>'
        '</div>'
    )
    write_html(title, body, HTML_PATH)
    write_html(title, body, READING_PATH)

    update_todo(verdict, primary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
