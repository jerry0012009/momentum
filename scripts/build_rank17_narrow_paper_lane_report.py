#!/usr/bin/env python3
from __future__ import annotations

"""Build a small reader-facing status page for the dedicated Rank 17 paper lane."""

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank17_pullback_ethsol_narrow_pilot"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "paper_rank17_pullback_ethsol_narrow_pilot"
OUT_PATH = SITE_DIR / "report.html"

STATUS_PATH = ART_DIR / "rank17_paper_status.csv"
OPEN_POSITIONS_PATH = ART_DIR / "rank17_paper_open_positions.csv"
LEDGER_PATH = ART_DIR / "rank17_paper_closed_trades.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank17_paper_last_run_summary.json"
STATE_PATH = ART_DIR / "rank17_paper_state.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def pct(v) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.2f}%"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def fmt(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    s = str(v).strip()
    return s or "-"


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v)
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = fmt(v)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def main() -> int:
    ensure_dir(SITE_DIR)

    status_df = read_csv(STATUS_PATH)
    open_df = read_csv(OPEN_POSITIONS_PATH)
    ledger_df = read_csv(LEDGER_PATH)
    run_summary = json.loads(RUN_SUMMARY_PATH.read_text()) if RUN_SUMMARY_PATH.exists() else {}
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    last_run = run_summary.get("run_at_utc", "-")
    mode = run_summary.get("mode", "-")
    new_closed = int(run_summary.get("new_closed_trades_appended", 0) or 0)
    initialized_at = state.get("initialized_at_utc", "-")

    open_positions = int((status_df.get("open_position") == "open").sum()) if not status_df.empty and "open_position" in status_df.columns else 0

    status_view = status_df.copy()
    if not status_view.empty:
        keep = [
            "candidate_rank",
            "candidate_id",
            "asset",
            "stage",
            "scope_tag",
            "sample_end_utc",
            "latest_closed_exit_ts_utc",
            "lifetime_total_return_6bps",
            "new_trades_appended",
            "open_position",
            "open_entry_ts_utc",
            "open_side",
            "watermark_exit_ts_utc",
        ]
        status_view = status_view[[c for c in keep if c in status_view.columns]]

    recent_ledger = ledger_df.copy()
    if not recent_ledger.empty and "exit_ts" in recent_ledger.columns:
        recent_ledger = recent_ledger.sort_values("exit_ts", ascending=False).head(40)
        keep = [c for c in ["asset", "entry_ts", "exit_ts", "side", "net_ret", "hold_bars", "exit_reason"] if c in recent_ledger.columns]
        recent_ledger = recent_ledger[keep]

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 17 · Narrow Paper Lane</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 32px 18px 56px; }}
    h1,h2 {{ margin: 0 0 12px; }}
    p {{ line-height: 1.6; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 24px; font-weight: 700; margin-top: 8px; word-break: break-word; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; position: sticky; top: 0; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
    a {{ color: #60a5fa; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p class=\"muted\">Generated: {escape(generated_at)}</p>
    <h1>Rank 17 · Pullback Recovery Confirmation · Narrow Paper Lane</h1>
    <p class=\"muted\">Scope: <code>ETH-USD + SOL-USD</code> only · Venue: <code>paper_binance_spot</code> · This page is paper-only (no live orders).</p>

    <div class=\"grid\">
      <div class=\"card\"><div class=\"k\">Last run</div><div class=\"v\">{escape(str(last_run))}</div><div class=\"s\">mode={escape(str(mode))} · init={escape(str(initialized_at))}</div></div>
      <div class=\"card\"><div class=\"k\">New closed trades</div><div class=\"v\">{new_closed}</div><div class=\"s\">appended on last refresh</div></div>
      <div class=\"card\"><div class=\"k\">Open positions</div><div class=\"v\">{open_positions}</div><div class=\"s\">inferred from incomplete sample tail</div></div>
      <div class=\"card\"><div class=\"k\">Tracked legs</div><div class=\"v\">{0 if status_df.empty else len(status_df)}</div><div class=\"s\">ETH-USD / SOL-USD</div></div>
    </div>

    <h2>Status</h2>
    {render_table(status_view, digits_cols={"lifetime_total_return_6bps": 4})}

    <h2>Open positions (if any)</h2>
    {render_table(open_df)}

    <h2>Recent closed trades ledger (tail)</h2>
    {render_table(recent_ledger, digits_cols={"net_ret": 6})}

    <div class=\"card\">
      <p><b>Operator boundary</b></p>
      <ul class=\"muted\">
        <li>只允许 follow 现有 Rank 17 narrow pilot 规则做 refresh；不要在 cron 里改参数/扩 scope。</li>
        <li>若 Binance API / 网络失败：保持报错短，方便排查；不要写入部分坏数据。</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""

    OUT_PATH.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
