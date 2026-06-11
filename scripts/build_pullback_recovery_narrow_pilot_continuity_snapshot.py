#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_pullback_recovery_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_pullback_recovery_confirmation_15m"

HISTORY_PATH = ART_DIR / "narrow_paper_pilot_ethsol_refresh_history.csv"
QUEUE_PATH = ART_DIR / "narrow_paper_pilot_ethsol_weekly_review_queue.csv"
MONITOR_PATH = ART_DIR / "narrow_paper_pilot_ethsol_monitoring_board.csv"
OUT_CSV = ART_DIR / "narrow_paper_pilot_ethsol_continuity_snapshot.csv"
OUT_HTML = SITE_DIR / "continuity_snapshot_report.html"


def pct(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.2f}%"


def iso(ts) -> str:
    if ts is None or pd.isna(ts):
        return "-"
    return pd.Timestamp(ts).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def build() -> pd.DataFrame:
    history = pd.read_csv(HISTORY_PATH)
    queue = pd.read_csv(QUEUE_PATH)
    monitor = pd.read_csv(MONITOR_PATH)

    history["sample_end_utc"] = pd.to_datetime(history["sample_end_utc"], utc=True)
    history["last_exit_ts_utc"] = pd.to_datetime(history["last_exit_ts_utc"], utc=True)
    queue["latest_sample_end_utc"] = pd.to_datetime(queue["latest_sample_end_utc"], utc=True)
    queue["last_exit_ts_utc"] = pd.to_datetime(queue["last_exit_ts_utc"], utc=True)

    sample_end = history["sample_end_utc"].max()
    next_review_due = sample_end + timedelta(days=7)
    watch_components = set(
        monitor.loc[monitor["status"].isin(["watch", "red_watch"]), "component"].astype(str)
    )

    rows = []
    for _, row in history.sort_values(["scope_tag", "asset"]).iterrows():
        asset_queue = queue[queue["asset"] == row["asset"]].copy()
        review_bucket_list = ", ".join(asset_queue["review_bucket"].astype(str).tolist()) if not asset_queue.empty else "none"
        review_status = "queued_weekly_review" if not asset_queue.empty else "no_open_review_queue"
        review_priority = ", ".join(asset_queue["review_priority"].astype(str).tolist()) if not asset_queue.empty else "none"

        continuity_status = str(row["continuity_status"])
        if continuity_status == "append_ready_green_narrow_pilot":
            continuity_bucket = "append_ready_green"
            gate_action = "continue_paper_and_append_refresh_review"
        elif continuity_status == "parked_red_watch":
            continuity_bucket = "excluded_red_watch"
            gate_action = "keep_btc_excluded_and_require_new_honest_evidence"
        else:
            continuity_bucket = "append_ready_with_followup"
            gate_action = "append_with_followup"

        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "scope_tag": row["scope_tag"],
                "asset": row["asset"],
                "timeframe": row["timeframe"],
                "venue_mode": row["venue_mode"],
                "signal_family": row["signal_family"],
                "sample_end_utc": iso(row["sample_end_utc"]),
                "last_exit_ts_utc": iso(row["last_exit_ts_utc"]),
                "days_since_last_trade": round(float(row["days_since_last_trade"]), 1),
                "lifetime_total_return_6bps": round(float(row["lifetime_total_return_6bps"]), 6),
                "weekly_review_status": row["weekly_review_status"],
                "review_queue_status": review_status,
                "review_bucket_queue": review_bucket_list,
                "review_priority": review_priority,
                "watch_components": ", ".join(sorted(watch_components)),
                "continuity_status": continuity_bucket,
                "operator_action": row["operator_action"],
                "gate_action": gate_action,
                "next_review_due_utc": next_review_due.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "promotion_boundary": row["promotion_boundary"],
                "writeback_note": row["writeback_note"],
            }
        )

    return pd.DataFrame(rows)


def render_html(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    green = int((df["continuity_status"] == "append_ready_green").sum()) if not df.empty else 0
    red = int((df["continuity_status"] == "excluded_red_watch").sum()) if not df.empty else 0

    body_rows = []
    for _, row in df.iterrows():
        body_rows.append(
            "<tr>"
            f"<td>{escape(str(row['asset']))}</td>"
            f"<td>{escape(str(row['scope_tag']))}</td>"
            f"<td>{escape(str(row['continuity_status']))}</td>"
            f"<td>{pct(row['lifetime_total_return_6bps'])}</td>"
            f"<td>{escape(str(row['weekly_review_status']))}</td>"
            f"<td>{escape(str(row['review_bucket_queue']))}</td>"
            f"<td>{escape(str(row['gate_action']))}</td>"
            f"<td><code>{escape(str(row['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank17 narrow paper continuity snapshot</title>
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
  <h1>Rank17 narrow paper continuity snapshot</h1>
  <p class="muted">生成时间：{generated_at}</p>

  <div class="card">
    <p><b>hard verdict：</b>已把 Rank 17 的 ETH+SOL narrow-paper refresh history、weekly review queue 与 monitoring watch 合并成一份可直接续写的 continuity snapshot。当前 green append-ready={green}，BTC excluded red-watch={red}；reader-facing 边界仍保持 <code>paper_only_narrow_pilot_until_new_live_clearance</code>。</p>
    <p class="muted">artifact：<code>reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_continuity_snapshot.csv</code></p>
  </div>

  <div class="card">
    <h2>按资产 continuity 快照</h2>
    <table>
      <thead><tr><th>asset</th><th>scope_tag</th><th>continuity_status</th><th>lifetime_total_return_6bps</th><th>weekly_review_status</th><th>review_bucket_queue</th><th>gate_action</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(body_rows)}</tbody>
    </table>
  </div>
</body>
</html>
'''
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    missing = [str(p) for p in [HISTORY_PATH, QUEUE_PATH, MONITOR_PATH] if not p.exists()]
    if missing:
        raise SystemExit("missing input csv: " + ", ".join(missing))
    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render_html(df)
    print("[ok] rank17 narrow paper continuity snapshot generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
