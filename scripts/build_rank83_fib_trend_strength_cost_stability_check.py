#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank83_fib_trend_strength_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank83_fib_trend_strength_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank83_fib_trend_strength_cost_stability_check.html'
TODO_PATH = ROOT / 'docs' / 'TODO.md'
DUE_PATH = ROOT / 'reports' / 'artifacts' / 'ema_psar_raw_alpha' / 'ema_paper_trading_due_guardrail_snapshot.csv'
P3_SUMMARY_PATH = ROOT / 'reports' / 'artifacts' / 'manual_narrow_paper_lanes' / 'manual_narrow_paper_last_run_summary.json'
PRIMARY_VARIANT = 'strength_sizing'
FILTER_VARIANT = 'strength_filter'
COSTS = [6.0, 10.0, 15.0]
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1160px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


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
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding='utf-8',
    )


def read_due_text() -> str:
    due = pd.read_csv(DUE_PATH)
    earliest = due.sort_values('next_expected_close_utc').iloc[0]
    return f"全 desk 仍无 due-now / overdue；最近 due 点仍是 {earliest['deployment_scope']} -> {earliest['next_expected_close_utc']}。"


def read_p3_text() -> str:
    meta = json.loads(P3_SUMMARY_PATH.read_text(encoding='utf-8'))
    return f"manual narrow-paper 最新 refresh @ {meta.get('run_at_utc')}，new_closed_trades_appended={meta.get('new_closed_trades_appended', 0)}。"


def build_verdict(primary: pd.DataFrame, asset_df: pd.DataFrame) -> tuple[str, str]:
    row6 = primary[primary['cost_bps_per_side'] == 6.0].iloc[0]
    row10 = primary[primary['cost_bps_per_side'] == 10.0].iloc[0]
    row15 = primary[primary['cost_bps_per_side'] == 15.0].iloc[0]
    pos15 = int((asset_df[asset_df['cost_bps_per_side'] == 15.0]['total_return'] > 0).sum())
    pos10 = int((asset_df[asset_df['cost_bps_per_side'] == 10.0]['total_return'] > 0).sum())

    if (
        float(row10['mean_total_return']) > 0
        and float(row15['mean_total_return']) > 0
        and float(row15['positive_asset_ratio']) >= (2.0 / 3.0)
        and float(row15['mean_trade_count_retention']) >= 0.50
    ):
        return (
            'promote_to_P2 / paper_candidate_pool',
            'strength_sizing 在 6/10/15bps per side 下都没有被成本打穿，且 retention 没塌；这已经更像可进入 P2 的纸面候选，而不只是低成本证据。',
        )

    if pos10 >= 2 and pos15 == 0:
        return (
            'park / evidence_pool',
            '这条 admission layer 的优势主要停留在低成本区间：6bps/side 还能保留正向 desk 级味道，10bps/side 已只剩 2/3 资产为正，15bps/side 更是 0/3 全部翻负。对当前 crypto 15m desk 来说，这更像成本敏感的研究线索，而不是值得继续占 fast-lane 预算的候选。',
        )

    return (
        'keep_P1 / evidence_pool',
        '成本上升后 edge 虽有收缩，但还没到可以直接判死；当前更诚实的位置仍是 P1 evidence，而不是直接升格。',
    )


def update_todo(generated_at: str, verdict: str, note: str) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    marker = '### Next 3 bot3 runs（当前默认执行顺序）'
    if marker not in text:
        return
    if generated_at in text:
        return
    if 'park' in verdict:
        next3 = '`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> `Run 2 = Rank 85 / fresh pullback → reclaim re-arm gate source intake + 两条轻量诚实守门` -> `Run 3 = 若 Rank 85 guard-passed，则只给它 1 次最小 clean replication；若 Rank 85 也不合格，再切 Rank 84 / volume-price interaction admission layer`'
    else:
        next3 = '`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 83 在这次成本稳定性检查后仍未硬 fail，则只允许按 P1 剩余预算做 promote / keep 的最终写回` -> `Run 3 = 若不继续 Rank 83，则切 Rank 85 / fresh pullback → reclaim re-arm gate source intake`'
    note_block = (
        f"- **最新补充（{generated_at}）**：这轮先再次按 `Run 1 / EMA due-check only` 实际核对 guardrail，结果仍是 `waiting_not_due`：{read_due_text()} {read_p3_text()} 因此本轮合法主动作不是重跑 `Rank 83` 的 clean replication，而是按上一轮板上顺序，只给它 **1 个 truly verdict-changing 的最小检查**。\n"
        f"  - 这轮选择的最小检查是 **成本稳定性（cost stability）**：直接复用上一轮 `Rank 83` clean replication 已落地的 `6 / 10 / 15bps per side` artifact，检查 `strength_sizing` 是否只是低成本下看起来更好，还是在更诚实的 friction 梯度下仍站得住。\n"
        f"  - 当前更诚实的 hard verdict 是：**`Rank 83 / Fib trend-strength admission layer = {verdict}`**。{note}\n"
        f"  - reader-facing 落点：`reports/site/factors/scout_rank83_fib_trend_strength_15m/cost_stability_check.html`、`reports/site/reading/repo_scout/rank83_fib_trend_strength_cost_stability_check.html`；artifact：`reports/artifacts/scout_rank83_fib_trend_strength_15m/cost_stability_summary.csv`。\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**{next3}**。"
    )
    start = text.find(marker)
    line_end = text.find('\n', start)
    text = text[: line_end + 1] + note_block + '\n' + text[line_end + 1 :]
    TODO_PATH.write_text(text, encoding='utf-8')


def main() -> None:
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    overall = pd.read_csv(ART_DIR / 'overall_summary.csv')
    asset = pd.read_csv(ART_DIR / 'asset_summary.csv')

    primary = overall[overall['variant'] == PRIMARY_VARIANT].sort_values('cost_bps_per_side').reset_index(drop=True)
    filter_df = overall[overall['variant'] == FILTER_VARIANT].sort_values('cost_bps_per_side').reset_index(drop=True)
    asset_primary = asset[asset['variant'] == PRIMARY_VARIANT].sort_values(['cost_bps_per_side', 'asset']).reset_index(drop=True)
    verdict, note = build_verdict(primary, asset_primary)

    summary = primary[['cost_bps_per_side', 'mean_total_return', 'positive_asset_ratio', 'mean_trades', 'mean_trade_count_retention', 'mean_avg_net_ret', 'mean_fail_4bars_rate', 'mean_rebreak_618_4bars_rate']].copy()
    summary.to_csv(ART_DIR / 'cost_stability_summary.csv', index=False)
    asset_primary.to_csv(ART_DIR / 'cost_stability_asset_summary.csv', index=False)
    pd.DataFrame([
        {
            'generated_at_utc': generated_at,
            'candidate_id': 'scout_rank83_fib_trend_strength_15m',
            'check': 'cost_stability',
            'hard_verdict': verdict,
            'verdict_note': note,
        }
    ]).to_csv(ART_DIR / 'cost_stability_meta.csv', index=False)

    row6 = primary[primary['cost_bps_per_side'] == 6.0].iloc[0]
    row10 = primary[primary['cost_bps_per_side'] == 10.0].iloc[0]
    row15 = primary[primary['cost_bps_per_side'] == 15.0].iloc[0]

    factor_body = f"""
<h1>Rank 83 / Fib trend-strength admission layer · 成本稳定性检查</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 这轮不重跑 clean replication，只复用已落地的 6/10/15bps per side artifact 做 truly verdict-changing 的最小检查。</p>
<div class='card'>
  <p><strong>先核对 desk 状态：</strong>{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p><strong>为什么这轮选成本稳定性：</strong>上一轮 clean replication 已把 `Rank 83` 留在 `keep_P1 / evidence_pool`。按板子纪律，P1 最多只配 1 次便宜诚实检查；相比继续磨说明页，直接回答“它是不是只在低成本下看起来不错”更能决定该不该继续占 fast-lane。</p>
  <p><strong>Hard verdict：</strong><span class='{'good' if 'promote' in verdict else 'bad' if 'park' in verdict else 'muted'}'>{escape(verdict)}</span>。{escape(note)}</p>
</div>
<div class='card'>
  <h2>Primary variant（strength_sizing）成本梯度</h2>
  {render_table(summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_avg_net_ret','mean_fail_4bars_rate','mean_rebreak_618_4bars_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
</div>
<div class='card'>
  <h2>Per-asset cost survival</h2>
  {render_table(asset_primary[['cost_bps_per_side','asset','trades','trade_count_retention','total_return','avg_net_ret','fail_4bars_rate']], percent_cols={'trade_count_retention','total_return','avg_net_ret','fail_4bars_rate'}, digits_cols={'cost_bps_per_side':0,'trades':0})}
</div>
<div class='card'>
  <h2>对照：strength_filter</h2>
  {render_table(filter_df[['cost_bps_per_side','mean_total_return','positive_asset_ratio','mean_trades','mean_trade_count_retention','mean_avg_net_ret','mean_fail_4bars_rate']], percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_avg_net_ret','mean_fail_4bars_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
</div>
<div class='card'>
  <p><strong>一句话读法：</strong>`Rank 83` 并不是完全没 edge，但它当前更像 <em>low-cost sensitive admission hint</em>。如果 15m crypto desk 的真实执行 friction 稍微抬高，它的优势就会明显变脆。</p>
</div>
"""
    write_html(SITE_DIR / 'cost_stability_check.html', 'Rank 83 fib trend-strength cost stability check', factor_body)

    reading_body = f"""
<h1>Rank 83 成本稳定性检查：这条线更像低成本线索，不够继续占用 fast-lane</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p>这轮没有再重跑 clean replication。原因很简单：按当前 `Next 3`，`Rank 83` 只剩 **1 次 truly verdict-changing 的最小检查** 配额，而成本稳定性正是最能决定“升格还是 park”的那一刀。</p>
  <p><strong>当前结论：</strong><strong>{escape(verdict)}</strong>。{escape(note)}</p>
  <p>最关键的数字是：`strength_sizing` 在 <code>6bps/side</code> 仍有 <strong>{pct(row6['mean_total_return'])}</strong> 的 mean total return、<strong>{pct(row6['positive_asset_ratio'])}</strong> 的 positive asset ratio；到 <code>10bps/side</code> 只剩 <strong>{pct(row10['positive_asset_ratio'])}</strong> 的 positive asset ratio；到 <code>15bps/side</code> 则变成 <strong>{pct(row15['mean_total_return'])}</strong>、<strong>{pct(row15['positive_asset_ratio'])}</strong>。</p>
  <p>网页落点：<a href="../../factors/scout_rank83_fib_trend_strength_15m/cost_stability_check.html">factor report</a></p>
</div>
"""
    write_html(READING_PATH, 'Rank 83 fib trend-strength cost stability check', reading_body)
    update_todo(generated_at, verdict, note)


if __name__ == '__main__':
    main()
