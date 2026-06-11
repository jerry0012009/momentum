#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"

WEEKLY_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv"
CONTINUITY_PATH = ART_DIR / "combo_all_narrow_paper_pilot_continuity_snapshot.csv"
OUT_CSV = ART_DIR / "combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv"
OUT_HTML = SITE_DIR / "weekly_review_writeback_seed.html"


def _pick(*values):
    for value in values:
        if value is None or pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return value
    return None


def _pct(value: float | int | str | None) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.2f}%"


def build() -> pd.DataFrame:
    weekly_df = pd.read_csv(WEEKLY_SEED_PATH)
    continuity_df = pd.read_csv(CONTINUITY_PATH)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    merged = weekly_df.merge(
        continuity_df[
            [
                "asset",
                "weekly_review_status",
                "continuity_status",
                "writeback_status",
                "gate_action",
                "operator_action",
                "next_review_due_utc",
                "promotion_boundary",
            ]
        ].rename(columns={"weekly_review_status": "continuity_weekly_review_status"}),
        on="asset",
        how="left",
        validate="one_to_one",
    )

    rows = []
    for _, row in merged.sort_values(["weekly_review_status", "asset"], ascending=[True, True]).iterrows():
        weekly_status = str(_pick(row.get("continuity_weekly_review_status"), row.get("weekly_review_status"), "yellow"))
        continuity_status = str(_pick(row.get("continuity_status"), "append_ready_with_followup"))
        if continuity_status == "blocked_by_red_watch":
            review_bucket = "red_watch_hold"
            writeback_summary = f"keep_red_watch | {row['asset']} | false_break_watch"
        else:
            review_bucket = "routine_weekly_review"
            writeback_summary = f"keep_narrow_paper | {row['asset']} | {weekly_status}_weekly_review"

        rows.append(
            {
                "candidate_id": _pick(row.get("candidate_id"), "rank2_combo_all"),
                "asset": _pick(row.get("asset"), "-"),
                "scope_tag": _pick(row.get("scope_tag"), "narrow_paper_pilot_approved"),
                "timeframe": _pick(row.get("timeframe"), "15m"),
                "review_bucket": review_bucket,
                "latest_sample_end_utc": _pick(row.get("sample_end_utc"), "-"),
                "last_trade_exit_ts_utc": _pick(row.get("last_trade_exit_ts_utc"), "-"),
                "days_since_last_trade": row.get("days_since_last_trade"),
                "lifetime_total_return": round(float(row.get("lifetime_total_return", float("nan"))), 6),
                "lifetime_false_break_ratio": row.get("lifetime_false_break_ratio"),
                "weekly_review_status": weekly_status,
                "continuity_status": continuity_status,
                "primary_watch": _pick(row.get("primary_watch"), "routine_weekly_review"),
                "gate_action": _pick(row.get("gate_action"), "continue_paper_and_log_review"),
                "operator_action": "append_weekly_review_writeback_seed",
                "writeback_target": "combo_all_narrow_paper_pilot_refresh_history.csv",
                "writeback_status": _pick(row.get("writeback_status"), "green_watch_continue"),
                "writeback_summary": writeback_summary,
                "next_review_due_utc": _pick(row.get("next_review_due_utc"), row.get("sample_end_utc")),
                "promotion_boundary": _pick(row.get("promotion_boundary"), "paper_only_until_new_evidence"),
                "generated_at_utc": generated_at,
                "writeback_note": (
                    "historical seed row only; no new bar fetched; btc leg stays blocked"
                    if continuity_status == "blocked_by_red_watch"
                    else "historical seed row only; no new bar fetched; green leg ready for weekly append"
                ),
            }
        )

    return pd.DataFrame(rows)


def render_html(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    green_rows = int(df["continuity_status"].eq("append_ready_green").sum()) if not df.empty else 0
    blocked_rows = int(df["continuity_status"].eq("blocked_by_red_watch").sum()) if not df.empty else 0

    rows_html = []
    for _, row in df.iterrows():
        rows_html.append(
            "<tr>"
            f"<td>{escape(str(row['asset']))}</td>"
            f"<td>{escape(str(row['review_bucket']))}</td>"
            f"<td>{escape(str(row['weekly_review_status']))}</td>"
            f"<td>{_pct(row['lifetime_total_return'])}</td>"
            f"<td>{_pct(row['lifetime_false_break_ratio'])}</td>"
            f"<td>{escape(str(row['primary_watch']))}</td>"
            f"<td>{escape(str(row['writeback_summary']))}</td>"
            f"<td><code>{escape(str(row['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank2 weekly review writeback seed</title>
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
  <p><a href="report.html">← 返回 Rank2 factor 主页</a></p>
  <h1>Rank2 weekly review writeback seed</h1>
  <p class="muted">生成时间：{generated_at}</p>

  <div class="card">
    <p><b>hard verdict：</b>这轮没有追新 bar，也没有改 `combo_all` 规则；只是把 Rank 2 当前真实存在的 weekly review need 压成可直接 append 的 writeback rows。当前仅有 <code>{green_rows}</code> 条 green leg 可直接续写，而 <code>{blocked_rows}</code> 条 BTC red-watch 继续保持 blocked，不借由 writeback seed 偷洗白。</p>
    <p class="muted">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_writeback_seed.csv</code></p>
  </div>

  <div class="card">
    <h2>append-ready weekly review rows</h2>
    <table>
      <thead><tr><th>asset</th><th>review_bucket</th><th>weekly_status</th><th>lifetime_total_return</th><th>false_break_ratio</th><th>primary_watch</th><th>writeback_summary</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(rows_html)}</tbody>
    </table>
  </div>
</body>
</html>
'''
    OUT_HTML.write_text(html, encoding="utf-8")


def main() -> int:
    missing = [str(p) for p in [WEEKLY_SEED_PATH, CONTINUITY_PATH] if not p.exists()]
    if missing:
        raise SystemExit("missing input csv: " + ", ".join(missing))
    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render_html(df)
    print("[ok] rank2 weekly review writeback seed generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
