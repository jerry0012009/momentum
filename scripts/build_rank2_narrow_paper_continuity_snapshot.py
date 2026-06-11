#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"

LEDGER_TEMPLATE_PATH = ART_DIR / "combo_all_narrow_paper_pilot_ledger_template.csv"
REFRESH_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_refresh_seed_rows.csv"
WEEKLY_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv"
WRITEBACK_SEED_PATH = ART_DIR / "combo_all_narrow_paper_pilot_refresh_writeback_seed_rows.csv"
OUT_CSV = ART_DIR / "combo_all_narrow_paper_pilot_continuity_snapshot.csv"
OUT_HTML = SITE_DIR / "continuity_snapshot_report.html"


PLACEHOLDER_MAP = {
    "<fill_on_signal>": None,
    "<source_breakout_bar>": None,
    "<next_bar_open_ts>": None,
    "<fill_on_exit>": None,
    "<fill>": None,
    "<0_or_1>": None,
    "<fill_current_gap>": None,
    "green|yellow|red": None,
}


def _clean(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    return PLACEHOLDER_MAP.get(text, value)


def _first_present(*values):
    for value in values:
        cleaned = _clean(value)
        if cleaned is not None:
            return cleaned
    return None


def build() -> pd.DataFrame:
    ledger_df = pd.read_csv(LEDGER_TEMPLATE_PATH)
    refresh_df = pd.read_csv(REFRESH_SEED_PATH)
    weekly_df = pd.read_csv(WEEKLY_SEED_PATH)
    writeback_df = pd.read_csv(WRITEBACK_SEED_PATH)

    key_cols = ["candidate_id", "scope_tag", "asset", "timeframe"]
    merged = (
        ledger_df.merge(refresh_df, on=key_cols, how="left", suffixes=("_template", ""))
        .merge(
            weekly_df[
                key_cols
                + [
                    "sample_end_utc",
                    "last_trade_exit_ts_utc",
                    "days_since_last_trade",
                    "lifetime_total_return",
                    "lifetime_false_break_ratio",
                    "weekly_review_status",
                    "primary_watch",
                    "operator_action",
                    "promotion_boundary",
                ]
            ].rename(
                columns={
                    "sample_end_utc": "sample_end_utc_weekly",
                    "last_trade_exit_ts_utc": "last_trade_exit_ts_utc_weekly",
                    "days_since_last_trade": "days_since_last_trade_weekly",
                    "lifetime_total_return": "lifetime_total_return_weekly",
                    "lifetime_false_break_ratio": "lifetime_false_break_ratio_weekly",
                    "weekly_review_status": "weekly_review_status_weekly",
                    "primary_watch": "primary_watch_weekly",
                    "operator_action": "operator_action_weekly",
                    "promotion_boundary": "promotion_boundary_weekly",
                }
            ),
            on=key_cols,
            how="left",
        )
        .merge(
            writeback_df[
                key_cols
                + [
                    "writeback_status",
                    "gate_action",
                    "writeback_operator_action",
                    "refresh_cycle_id",
                    "review_sample_end_utc",
                    "next_review_due_utc",
                ]
            ],
            on=key_cols,
            how="left",
        )
    )

    rows = []
    for _, r in merged.iterrows():
        weekly_status = _first_present(r.get("weekly_review_status_weekly"), r.get("weekly_review_status"), "yellow")
        writeback_status = _first_present(r.get("writeback_status"), "yellow_watch_followup")
        if weekly_status == "red":
            continuity_status = "blocked_by_red_watch"
        elif writeback_status == "green_watch_continue":
            continuity_status = "append_ready_green"
        else:
            continuity_status = "append_ready_with_followup"

        operator_action = _first_present(
            r.get("writeback_operator_action"),
            r.get("operator_action_weekly"),
            r.get("operator_action"),
            "append_refresh_and_weekly_review",
        )

        rows.append(
            {
                "candidate_id": _first_present(r.get("candidate_id"), "rank2_combo_all"),
                "scope_tag": _first_present(r.get("scope_tag"), "narrow_paper_pilot_approved"),
                "asset": _first_present(r.get("asset"), "-"),
                "timeframe": _first_present(r.get("timeframe"), "15m"),
                "venue_mode": _first_present(r.get("venue_mode"), "paper_binance_spot"),
                "signal_family": _first_present(r.get("signal_family"), "volume_supportflip_higherlow_combo_all"),
                "signal_ts_utc": _clean(r.get("signal_ts_utc")),
                "breakout_ts_utc": _clean(r.get("breakout_ts_utc")),
                "entry_ts_utc": _clean(r.get("entry_ts_utc")),
                "exit_ts_utc": _first_present(r.get("exit_ts_utc"), r.get("last_trade_exit_ts_utc_weekly"), r.get("last_trade_exit_ts_utc")),
                "entry_price": _clean(r.get("entry_price")),
                "exit_price": _clean(r.get("exit_price")),
                "cost_bps_roundtrip": _clean(r.get("cost_bps_roundtrip")),
                "hold_bars": _clean(r.get("hold_bars")),
                "net_ret": _clean(r.get("net_ret")),
                "false_break_flag": _clean(r.get("false_break_flag")),
                "days_since_last_trade": _first_present(r.get("days_since_last_trade_weekly"), r.get("days_since_last_trade")),
                "sample_end_utc": _first_present(r.get("sample_end_utc_weekly"), r.get("sample_end_utc"), r.get("review_sample_end_utc")),
                "weekly_review_status": weekly_status,
                "primary_watch": _first_present(r.get("primary_watch_weekly"), r.get("primary_watch"), "routine_weekly_review"),
                "writeback_status": writeback_status,
                "gate_action": _first_present(r.get("gate_action"), "continue_paper_with_followup_note"),
                "operator_action": operator_action,
                "refresh_cycle_id": _clean(r.get("refresh_cycle_id")),
                "next_review_due_utc": _clean(r.get("next_review_due_utc")),
                "continuity_status": continuity_status,
                "promotion_boundary": _first_present(r.get("promotion_boundary_weekly"), r.get("promotion_boundary"), "paper_only_until_new_evidence"),
            }
        )

    return pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)



def _fmt_pct(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.2f}%"



def render_html(df: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    gen = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    green = int((df["continuity_status"] == "append_ready_green").sum()) if not df.empty else 0
    blocked = int((df["continuity_status"] == "blocked_by_red_watch").sum()) if not df.empty else 0

    row_html = []
    for _, r in df.iterrows():
        row_html.append(
            "<tr>"
            f"<td>{escape(str(r['asset']))}</td>"
            f"<td>{escape(str(r['continuity_status']))}</td>"
            f"<td>{escape(str(r['weekly_review_status']))}</td>"
            f"<td>{escape(str(r['writeback_status']))}</td>"
            f"<td>{_fmt_pct(r['net_ret'])}</td>"
            f"<td>{escape(str(r['primary_watch']))}</td>"
            f"<td>{escape(str(r['gate_action']))}</td>"
            f"<td><code>{escape(str(r['next_review_due_utc']))}</code></td>"
            "</tr>"
        )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank2 narrow paper continuity snapshot</title>
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
  <h1>Rank2 narrow paper continuity snapshot</h1>
  <p class="muted">生成时间：{gen}</p>

  <div class="card">
    <p><b>hard verdict：</b>已把 Rank 2 的 ledger template、refresh seed、weekly review seed 与 writeback seed 合并成一份可直接 append 的 continuity snapshot。当前 green append-ready={green}，red-watch blocked={blocked}；reader-facing 口径仍保持 <code>paper_only_until_new_evidence</code>。</p>
    <p class="muted">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_continuity_snapshot.csv</code></p>
  </div>

  <div class="card">
    <h2>按资产 continuity 快照</h2>
    <table>
      <thead><tr><th>asset</th><th>continuity_status</th><th>weekly_status</th><th>writeback_status</th><th>net_ret</th><th>primary_watch</th><th>gate_action</th><th>next_review_due_utc</th></tr></thead>
      <tbody>{''.join(row_html)}</tbody>
    </table>
  </div>
</body>
</html>
'''
    OUT_HTML.write_text(html, encoding="utf-8")



def main() -> int:
    missing = [
        str(p)
        for p in [LEDGER_TEMPLATE_PATH, REFRESH_SEED_PATH, WEEKLY_SEED_PATH, WRITEBACK_SEED_PATH]
        if not p.exists()
    ]
    if missing:
        raise SystemExit("missing input csv: " + ", ".join(missing))

    ART_DIR.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(OUT_CSV, index=False)
    render_html(df)
    print("[ok] rank2 narrow paper continuity snapshot generated")
    print("[artifact]", OUT_CSV)
    print("[site]", OUT_HTML)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
