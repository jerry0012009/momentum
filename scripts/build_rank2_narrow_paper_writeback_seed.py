#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"

REFRESH_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_refresh_seed_rows.csv"
WEEKLY_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv"
OUT_CSV = ART_DIR / "combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv"
OUT_HTML = SITE_DIR / "writeback_seed_report.html"


def _to_utc(ts: str) -> pd.Timestamp:
    return pd.to_datetime(ts, utc=True, errors="coerce")


def build() -> pd.DataFrame:
    refresh_df = pd.read_csv(REFRESH_SEED_PATH)
    weekly_df = pd.read_csv(WEEKLY_SEED_PATH)

    key_cols = ["candidate_id", "scope_tag", "asset", "timeframe"]
    merged = refresh_df.merge(
        weekly_df[
            [
                "candidate_id",
                "scope_tag",
                "asset",
                "timeframe",
                "sample_end_utc",
                "days_since_last_trade",
                "weekly_review_status",
                "primary_watch",
                "operator_action",
                "promotion_boundary",
            ]
        ],
        on=key_cols,
        how="left",
    )

    now_utc = datetime.now(timezone.utc)
    rows = []
    for _, r in merged.iterrows():
        sample_end = _to_utc(str(r.get("sample_end_utc", "")))
        if pd.isna(sample_end):
            sample_end = _to_utc(str(r.get("exit_ts_utc", "")))
        if pd.isna(sample_end):
            sample_end = pd.Timestamp(now_utc)
        next_due = sample_end + pd.Timedelta(days=7)

        review_status = str(r.get("weekly_review_status", "yellow"))
        primary_watch = str(r.get("primary_watch", "routine_weekly_review"))
        if review_status == "red":
            writeback_status = "red_watch_hold"
            gate_action = "hold_narrow_paper_and_escalate_weekly_ticket"
        elif review_status == "yellow":
            writeback_status = "yellow_watch_followup"
            gate_action = "continue_paper_with_followup_note"
        else:
            writeback_status = "green_watch_continue"
            gate_action = "continue_paper_and_log_review"

        rows.append(
            {
                "candidate_id": str(r.get("candidate_id", "rank2_combo_all")),
                "scope_tag": str(r.get("scope_tag", "narrow_paper_pilot_approved")),
                "asset": str(r.get("asset", "-")),
                "timeframe": str(r.get("timeframe", "15m")),
                "signal_ts_utc": str(r.get("signal_ts_utc", "-")),
                "entry_ts_utc": str(r.get("entry_ts_utc", "-")),
                "exit_ts_utc": str(r.get("exit_ts_utc", "-")),
                "net_ret": float(r.get("net_ret", float("nan"))),
                "days_since_last_trade": float(r.get("days_since_last_trade", float("nan"))),
                "weekly_review_status": review_status,
                "primary_watch": primary_watch,
                "writeback_status": writeback_status,
                "gate_action": gate_action,
                "writeback_operator_action": "append_weekly_review_and_refresh_writeback",
                "refresh_cycle_id": f"rank2-writeback-{str(r.get('asset','x')).lower()}-{sample_end.strftime('%Y%m%d')}",
                "review_sample_end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "next_review_due_utc": next_due.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "promotion_boundary": str(r.get("promotion_boundary", "paper_only_until_new_evidence")),
            }
        )

    out = pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)
    return out


def render_html(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    red = int((df["weekly_review_status"] == "red").sum()) if not df.empty else 0
    yellow = int((df["weekly_review_status"] == "yellow").sum()) if not df.empty else 0
    green = int((df["weekly_review_status"] == "green").sum()) if not df.empty else 0

    rows = []
    for _, r in df.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(r['asset']))}</td>"
            f"<td>{escape(str(r['weekly_review_status']))}</td>"
            f"<td>{escape(str(r['primary_watch']))}</td>"
            f"<td>{escape(str(r['writeback_status']))}</td>"
            f"<td>{escape(str(r['gate_action']))}</td>"
            f"<td><code>{escape(str(r['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank2 narrow paper refresh writeback seed</title>
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
  <p><a href=\"report.html\">← 返回 Rank2 factor 主页</a></p>
  <h1>Rank2 narrow paper refresh writeback seed</h1>
  <p class=\"muted\">生成时间：{gen}</p>

  <div class=\"card\">
    <p><b>hard verdict：</b>已把 Rank2 的 `weekly review seed` 接成可直接执行的 `refresh writeback seed`。当前状态分布：red={red} / yellow={yellow} / green={green}；默认仍是 paper-only 边界，不做 live admission。</p>
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>按资产 writeback 种子行</h2>
    <table>
      <thead><tr><th>asset</th><th>weekly_status</th><th>primary_watch</th><th>writeback_status</th><th>gate_action</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    if not REFRESH_SEED_PATH.exists() or not WEEKLY_SEED_PATH.exists():
        raise SystemExit("missing input seed csv")

    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render_html(df)

    print("[ok] rank2 refresh writeback seed generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
