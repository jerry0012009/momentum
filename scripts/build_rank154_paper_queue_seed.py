#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_queue_seed"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "paper_rank154_crypto_stat_arb_queue_seed"
STATUS_PATH = ART_DIR / "rank154_queue_status.csv"
STATE_PATH = ART_DIR / "rank154_queue_state.json"
REPORT_PATH = SITE_DIR / "report.html"

STATUS_FIELDS = [
    "candidate_id",
    "candidate_rank",
    "stage",
    "queue_state",
    "entry_mode",
    "runner_mode",
    "runner_scope",
    "source_record",
    "latest_admission_record",
    "promotion_record",
    "launch_entry",
    "factor_page_anchor",
    "script_anchor",
    "review_boundary",
    "rollback_boundary",
    "next_operator_action",
    "updated_at_utc",
    "note",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=STATUS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def render_report(row: dict[str, str], generated_at: str) -> None:
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 154 · Crypto-Stat-Arb Paper Queue Seed</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 32px 18px 56px; }}
    h1,h2 {{ margin: 0 0 12px; }}
    p {{ line-height: 1.6; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 22px; font-weight: 700; margin-top: 8px; word-break: break-word; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    a {{ color: #60a5fa; }}
  </style>
</head>
<body>
  <div class="wrap">
    <p class="muted">Generated: {escape(generated_at)}</p>
    <h1>Rank 154 · Crypto-Stat-Arb · Paper launch queue seed</h1>
    <p class="muted">Current mode: <code>{escape(row['entry_mode'])}</code> · Runner mode: <code>{escape(row['runner_mode'])}</code> · This page only fixes queue scope / runner boundary. It does not claim autonomous paper is already live.</p>

    <div class="grid">
      <div class="card"><div class="k">Stage</div><div class="v">{escape(row['stage'])}</div><div class="s">Rank 154 stays in P3</div></div>
      <div class="card"><div class="k">Queue state</div><div class="v">{escape(row['queue_state'])}</div><div class="s">scope defined, not running</div></div>
      <div class="card"><div class="k">Launch entry</div><div class="v"><code>{escape(row['launch_entry'])}</code></div><div class="s">authoritative intake page</div></div>
      <div class="card"><div class="k">Factor anchor</div><div class="v"><code>{escape(row['factor_page_anchor'])}</code></div><div class="s">closest visible surface, not equal to dedicated runner</div></div>
      <div class="card"><div class="k">Script anchor</div><div class="v"><code>{escape(row['script_anchor'])}</code></div><div class="s">current workspace build anchor</div></div>
      <div class="card"><div class="k">Updated</div><div class="v">{escape(row['updated_at_utc'])}</div><div class="s">queue seed timestamp</div></div>
    </div>

    <div class="card">
      <p><b>Hard verdict</b></p>
      <ul class="muted">
        <li><b>Rank 154 继续留在 <code>P3 / Paper launch queue</code>。</b> 本轮完成的是 queue 接线范围锁定，不是回头补 admission，也不是假装 runner 已经开始自动运行。</li>
        <li>当前最小 launch 入口仍是 <code>fresh intake + latest admission + promotion record</code> 三段证据链，外加已有 intake 页面 / factor surface / build anchor。</li>
        <li>下一位认领 queue 的执行者，应该先做 dedicated paper runner 的 <code>init/refresh</code> 骨架，再决定是沿 repo 骨架做 raw-bar 重算，还是明确采用 frozen-source seed；这一步不能伪装成 routine refresh。</li>
      </ul>
    </div>

    <h2>Authoritative queue packet</h2>
    <table>
      <thead><tr><th>field</th><th>value</th></tr></thead>
      <tbody>
        <tr><td>candidate_id</td><td>{escape(row['candidate_id'])}</td></tr>
        <tr><td>candidate_rank</td><td>{escape(row['candidate_rank'])}</td></tr>
        <tr><td>source_record</td><td><code>{escape(row['source_record'])}</code></td></tr>
        <tr><td>latest_admission_record</td><td><code>{escape(row['latest_admission_record'])}</code></td></tr>
        <tr><td>promotion_record</td><td><code>{escape(row['promotion_record'])}</code></td></tr>
        <tr><td>launch_entry</td><td><code>{escape(row['launch_entry'])}</code></td></tr>
        <tr><td>factor_page_anchor</td><td><code>{escape(row['factor_page_anchor'])}</code></td></tr>
        <tr><td>script_anchor</td><td><code>{escape(row['script_anchor'])}</code></td></tr>
        <tr><td>runner_scope</td><td>{escape(row['runner_scope'])}</td></tr>
        <tr><td>next_operator_action</td><td>{escape(row['next_operator_action'])}</td></tr>
      </tbody>
    </table>

    <div class="card">
      <p><b>Review / rollback boundary</b></p>
      <ul class="muted">
        <li><b>Review boundary:</b> {escape(row['review_boundary'])}</li>
        <li><b>Rollback boundary:</b> {escape(row['rollback_boundary'])}</li>
        <li><b>Why this matters:</b> 这些边界写死之后，后续 queue 执行若没有出现新的单一决定性失败，就不应再把 Rank 154 拉回开放式 admission compare。</li>
      </ul>
    </div>

    <div class="card">
      <p><b>Operator note</b></p>
      <ul class="muted">
        <li>本页只做 queue seed：把入口、运行骨架和 review/rollback 约束压成单一可引用页面。</li>
        <li>它不代表已经存在专属 cron、stateful paper runner 或自动下单能力。</li>
        <li>如果后续 scope 从 design-only 升到 running paper lane，必须新增 dedicated runner/state/refresh 流，而不是在本页上偷改文案。</li>
      </ul>
    </div>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    generated_at = utc_now_text()

    row = {
        "candidate_id": "rank154_crypto_stat_arb_queue_seed",
        "candidate_rank": "154",
        "stage": "P3_paper_launch_queue",
        "queue_state": "scope_defined_not_running",
        "entry_mode": "paper_launch_queue_seed",
        "runner_mode": "design_only_not_running",
        "runner_scope": "Keep the current authoritative packet intact; next claimer must build a dedicated init/refresh paper runner skeleton before any autonomous cadence exists.",
        "source_record": "research/optimization_loop/2026-03-24_0922_crypto-stat-arb-fresh-intake.md",
        "latest_admission_record": "research/optimization_loop/2026-03-24_1046_crypto-stat-arb-p2-honesty-execution.md",
        "promotion_record": "research/strategy_review/2026-03-24_1219_strategy-review.md",
        "launch_entry": "reports/site/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html",
        "factor_page_anchor": "reports/site/factors/scout_crypto_pairs_stat_arb_15m/report.html",
        "script_anchor": "scripts/build_crypto_pairs_stat_arb_first_verdict.py",
        "review_boundary": "Only reopen review if queue implementation cannot preserve the positive read under lagged weights + lagged funding, or if a new execution-realism flaw appears.",
        "rollback_boundary": "Rollback from P3 queue only on one decisive queue-stage failure; do not reopen admission because of generic parameter/time curiosity.",
        "next_operator_action": "Create a dedicated Rank 154 paper runner with explicit init/refresh split and queue-state ledger; do not treat the current factor page as already-live runner status.",
        "updated_at_utc": generated_at,
        "note": "Queue scope is now explicit: entry and boundaries are fixed, but autonomous paper execution does not exist yet.",
    }

    write_csv(STATUS_PATH, [row])
    STATE_PATH.write_text(
        json.dumps(
            {
                "initialized_at_utc": generated_at,
                "mode": row["entry_mode"],
                "queue_state": row["queue_state"],
                "runner_mode": row["runner_mode"],
                "note": row["note"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    render_report(row, generated_at)

    print("[ok] rank154 paper queue seed generated")
    print(f"[artifact] {STATUS_PATH.relative_to(ROOT)}")
    print(f"[site] {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
