#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"

SNAPSHOT_PATH = ART_DIR / "combo_all_narrow_paper_pilot_continuity_snapshot.csv"
WRITEBACK_PATH = ART_DIR / "combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv"
OUT_CSV = ART_DIR / "combo_all_narrow_paper_pilot_refresh_history.csv"
OUT_HTML = SITE_DIR / "refresh_history_report.html"


def _choose(*values):
    for value in values:
        if pd.isna(value):
            continue
        if value is None:
            continue
        text = str(value).strip()
        if text == "":
            continue
        return value
    return None


def build() -> pd.DataFrame:
    snapshot_df = pd.read_csv(SNAPSHOT_PATH)
    writeback_df = pd.read_csv(WRITEBACK_PATH)

    key_cols = ["candidate_id", "scope_tag", "asset", "timeframe"]
    merged = snapshot_df.merge(
        writeback_df[
            key_cols
            + [
                "writeback_operator_action",
                "review_sample_end_utc",
                "next_review_due_utc",
                "writeback_status",
                "gate_action",
            ]
        ],
        on=key_cols,
        how="left",
        suffixes=("", "_seed"),
    )

    rows = []
    for _, r in merged.iterrows():
        continuity_status = str(_choose(r.get("continuity_status"), "append_ready_with_followup"))
        if continuity_status == "blocked_by_red_watch":
            append_status = "seed_blocked_red_watch"
        elif continuity_status == "append_ready_green":
            append_status = "seed_append_ready_green"
        else:
            append_status = "seed_append_ready_followup"

        rows.append(
            {
                "candidate_id": _choose(r.get("candidate_id"), "rank2_combo_all"),
                "scope_tag": _choose(r.get("scope_tag"), "narrow_paper_pilot_approved"),
                "asset": _choose(r.get("asset"), "-"),
                "timeframe": _choose(r.get("timeframe"), "15m"),
                "refresh_cycle_id": _choose(r.get("refresh_cycle_id"), f"rank2-history-{str(r.get('asset')).lower()}"),
                "history_row_kind": "seed_from_continuity_snapshot",
                "completed_review_ts_utc": _choose(r.get("review_sample_end_utc"), r.get("sample_end_utc")),
                "next_review_due_utc": _choose(r.get("next_review_due_utc_seed"), r.get("next_review_due_utc")),
                "weekly_review_status": _choose(r.get("weekly_review_status"), "yellow"),
                "writeback_status": _choose(r.get("writeback_status_seed"), r.get("writeback_status"), "yellow_watch_followup"),
                "continuity_status": continuity_status,
                "append_status": append_status,
                "gate_action": _choose(r.get("gate_action_seed"), r.get("gate_action"), "continue_paper_with_followup_note"),
                "operator_action": _choose(r.get("writeback_operator_action"), r.get("operator_action"), "append_refresh_and_weekly_review"),
                "primary_watch": _choose(r.get("primary_watch"), "routine_weekly_review"),
                "net_ret": r.get("net_ret"),
                "days_since_last_trade": r.get("days_since_last_trade"),
                "promotion_boundary": _choose(r.get("promotion_boundary"), "paper_only_until_new_evidence"),
                "history_note": (
                    "red_watch_seed_kept_blocked"
                    if continuity_status == "blocked_by_red_watch"
                    else "seed_ready_for_first_append_cycle"
                ),
            }
        )

    df = pd.DataFrame(rows).sort_values(["append_status", "asset"]).reset_index(drop=True)
    return df


def _fmt_pct(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.2f}%"


def _fmt_float(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.1f}"


def render(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ready_count = int(df["append_status"].eq("seed_append_ready_green").sum()) if not df.empty else 0
    blocked_count = int(df["append_status"].eq("seed_blocked_red_watch").sum()) if not df.empty else 0

    rows = []
    for _, r in df.iterrows():
        rows.append(
            "<tr>"
            f"<td>{escape(str(r['asset']))}</td>"
            f"<td><code>{escape(str(r['completed_review_ts_utc']))}</code></td>"
            f"<td>{escape(str(r['append_status']))}</td>"
            f"<td>{escape(str(r['weekly_review_status']))}</td>"
            f"<td>{escape(str(r['writeback_status']))}</td>"
            f"<td>{escape(str(r['primary_watch']))}</td>"
            f"<td>{_fmt_pct(r['net_ret'])}</td>"
            f"<td>{_fmt_float(r['days_since_last_trade'])}</td>"
            f"<td>{escape(str(r['gate_action']))}</td>"
            f"<td><code>{escape(str(r['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank2 narrow paper refresh history</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 980px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:12px; background:#fff; padding:16px 18px; margin:14px 0; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:2px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; text-align:left; padding:8px 10px; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="report.html">← 返回 Rank2 factor 主页</a></p>
  <h1>Rank2 narrow paper refresh history</h1>
  <p class="muted">生成时间：{generated_at}</p>

  <div class="card">
    <p><b>hard verdict：</b>已把 Rank 2 从 continuity snapshot 再推进半步，落成一份可 append 的 refresh history 种子链。当前 green append-ready={ready_count}，red-watch blocked={blocked_count}；reader-facing 口径仍保持 <code>paper_only_until_new_evidence</code>，不越级写成 live-ready。</p>
    <p class="muted">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_history.csv</code></p>
  </div>

  <div class="card">
    <h2>按资产 first append history</h2>
    <table>
      <thead><tr><th>asset</th><th>completed_review_ts_utc</th><th>append_status</th><th>weekly_status</th><th>writeback_status</th><th>primary_watch</th><th>net_ret</th><th>days_since_last_trade</th><th>gate_action</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
  </div>
</body>
</html>
'''
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    missing = [str(p) for p in [SNAPSHOT_PATH, WRITEBACK_PATH] if not p.exists()]
    if missing:
        raise SystemExit("missing input csv: " + ", ".join(missing))

    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render(df)
    print("[ok] rank2 narrow paper refresh history generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
