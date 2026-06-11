#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_pullback_recovery_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_pullback_recovery_confirmation_15m"

QUEUE_PATH = ART_DIR / "narrow_paper_pilot_ethsol_weekly_review_queue.csv"
CONTINUITY_PATH = ART_DIR / "narrow_paper_pilot_ethsol_continuity_snapshot.csv"
OUT_CSV = ART_DIR / "narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv"
OUT_HTML = SITE_DIR / "weekly_review_writeback_seed.html"


def pct(v: float | int | str | None) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.2f}%"


def build() -> pd.DataFrame:
    queue = pd.read_csv(QUEUE_PATH)
    continuity = pd.read_csv(CONTINUITY_PATH)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    green_rows = continuity[continuity["continuity_status"] == "append_ready_green"].copy()
    merged = queue.merge(
        green_rows[
            [
                "asset",
                "review_queue_status",
                "watch_components",
                "gate_action",
                "next_review_due_utc",
                "writeback_note",
            ]
        ],
        on="asset",
        how="left",
        validate="many_to_one",
    )

    rows = []
    for _, row in merged.sort_values(["asset", "review_bucket"]).iterrows():
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "asset": row["asset"],
                "scope_tag": row["scope_tag"],
                "review_bucket": row["review_bucket"],
                "review_priority": row["review_priority"],
                "latest_sample_end_utc": row["latest_sample_end_utc"],
                "last_exit_ts_utc": row["last_exit_ts_utc"],
                "lifetime_total_return_6bps": round(float(row["lifetime_total_return_6bps"]), 6),
                "weekly_review_status": row["weekly_review_status"],
                "review_focus": row["review_focus"],
                "review_queue_status": row.get("review_queue_status", "queued_weekly_review"),
                "watch_components": row.get("watch_components", "time_pocket_watch"),
                "gate_action": row.get("gate_action", "continue_paper_and_append_refresh_review"),
                "operator_action": "append_weekly_review_writeback_seed",
                "writeback_target": "narrow_paper_pilot_ethsol_refresh_history.csv",
                "writeback_summary": (
                    f"keep_ethsol_narrow_pilot | {row['asset']} | {row['review_bucket']} | "
                    f"{row['review_focus']}"
                ),
                "next_review_due_utc": row.get("next_review_due_utc", row["latest_sample_end_utc"]),
                "promotion_boundary": row["promotion_boundary"],
                "generated_at_utc": generated_at,
                "writeback_note": row.get("writeback_note", "historical seed row only; no new bar fetched"),
            }
        )

    return pd.DataFrame(rows)


def render_html(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows_html = []
    for _, row in df.iterrows():
        rows_html.append(
            "<tr>"
            f"<td>{escape(str(row['asset']))}</td>"
            f"<td>{escape(str(row['review_bucket']))}</td>"
            f"<td>{escape(str(row['review_focus']))}</td>"
            f"<td>{pct(row['lifetime_total_return_6bps'])}</td>"
            f"<td>{escape(str(row['watch_components']))}</td>"
            f"<td>{escape(str(row['writeback_summary']))}</td>"
            f"<td><code>{escape(str(row['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank17 weekly review writeback seed</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 980px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:12px; background:#fff; padding:16px 18px; margin:14px 0; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:2px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; text-align:left; padding:8px 10px; vertical-align:top; }}
  </style>
</head>
<body>
  <p><a href="report.html">← 返回 Rank17 factor 主页</a></p>
  <h1>Rank17 weekly review writeback seed</h1>
  <p class="muted">生成时间：{generated_at}</p>

  <div class="card">
    <p><b>hard verdict：</b>这轮没有追新 bar，也没有改策略规则；只是把 Rank 17 已经排进队列的 weekly review need，压成可直接 append 的 writeback seed rows。当前只覆盖 <code>ETH-USD / SOL-USD</code> 两条 narrow-paper pilot 绿腿，<code>BTC-USD</code> 继续留在 excluded red-watch，不进入这份 writeback。</p>
    <p class="muted">artifact：<code>reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv</code></p>
  </div>

  <div class="card">
    <h2>append-ready writeback rows</h2>
    <table>
      <thead><tr><th>asset</th><th>review_bucket</th><th>review_focus</th><th>lifetime_total_return_6bps</th><th>watch_components</th><th>writeback_summary</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(rows_html)}</tbody>
    </table>
  </div>
</body>
</html>
'''
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    missing = [str(p) for p in [QUEUE_PATH, CONTINUITY_PATH] if not p.exists()]
    if missing:
        raise SystemExit("missing input csv: " + ", ".join(missing))
    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render_html(df)
    print("[ok] rank17 weekly review writeback seed generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
