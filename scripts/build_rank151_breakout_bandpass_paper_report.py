#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank151_breakout_bandpass_gate"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "paper_rank151_breakout_bandpass_gate"
OUT_PATH = SITE_DIR / "report.html"

STATUS_PATH = ART_DIR / "rank151_paper_status.csv"
LEDGER_PATH = ART_DIR / "rank151_paper_closed_trades.csv"
RUN_SUMMARY_PATH = ART_DIR / "rank151_paper_last_run_summary.json"
STATE_PATH = ART_DIR / "rank151_paper_state.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


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
                text = pct(v, digits_cols.get(col, 2))
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
    ledger_df = read_csv(LEDGER_PATH)
    run_summary = json.loads(RUN_SUMMARY_PATH.read_text()) if RUN_SUMMARY_PATH.exists() else {}
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    last_run = run_summary.get("run_at_utc", "-")
    mode = run_summary.get("mode", "-")
    initialized_at = state.get("initialized_at_utc", "-")
    new_closed = int(run_summary.get("new_closed_trades_appended", 0) or 0)

    status_view = status_df.copy()
    if not status_view.empty:
        keep = [
            "candidate_rank",
            "candidate_id",
            "stage",
            "family",
            "variant",
            "venue_mode",
            "runner_mode",
            "refresh_cadence",
            "sample_start_utc",
            "sample_end_utc",
            "closed_trades",
            "new_trades_appended",
            "lifetime_total_return_6bps",
            "mean_net_bps",
            "win_rate",
            "asset_coverage",
            "open_position",
            "watermark_exit_ts_utc",
            "updated_at_utc",
            "note",
        ]
        status_view = status_view[[c for c in keep if c in status_view.columns]]

    recent_ledger = ledger_df.copy()
    if not recent_ledger.empty and "exit_ts" in recent_ledger.columns:
        recent_ledger = recent_ledger.sort_values("exit_ts", ascending=False).head(40)
        keep = [c for c in ["symbol", "entry_ts", "exit_ts", "side", "align_score", "gross_bps", "net_bps", "hold_bars"] if c in recent_ledger.columns]
        recent_ledger = recent_ledger[keep]

    summary_cards = []
    if not status_df.empty:
        row = status_df.iloc[0]
        summary_cards = [
            ("Last run", str(last_run), f"mode={mode} · init={initialized_at}"),
            ("Closed trades in frozen digest", str(int(row.get("closed_trades", 0) or 0)), "current source sample size"),
            ("Last refresh delta", str(new_closed), "new rows appended on last run"),
            ("Lifetime total return (6bps)", pct(row.get("lifetime_total_return_6bps")), f"mean_net_bps={num(row.get('mean_net_bps'), 2)} · win_rate={pct(row.get('win_rate'))}"),
            ("Asset coverage", str(int(row.get("asset_coverage", 0) or 0)), "frozen digest coverage"),
            ("Watermark", fmt(row.get("watermark_exit_ts_utc")), "closed-trade append boundary"),
        ]
    else:
        summary_cards = [
            ("Last run", str(last_run), f"mode={mode} · init={initialized_at}"),
            ("Status", "暂无数据", "runner 尚未写出 status.csv"),
        ]

    cards_html = "".join(
        f'<div class="card"><div class="k">{escape(k)}</div><div class="v">{escape(v)}</div><div class="s">{escape(s)}</div></div>'
        for k, v, s in summary_cards
    )

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 151 · Breakout Band-pass Gate Paper Runner</title>
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
    <h1>Rank 151 · EWMAC breakout short · band-pass gate</h1>
    <p class=\"muted\">Current mode: <code>paper_digest_seed</code> · Source: frozen honest-gate digest · This is a launch-plumbing runner, not a live/raw-bar recomputation engine.</p>

    <div class=\"grid\">{cards_html}</div>

    <div class=\"card\">
      <p><b>What this page means</b></p>
      <ul class=\"muted\">
        <li>这条线已经完成 launch queue 接线，并已进入 <code>Paper / 正在自动运行</code> 的 host-side autonomous paper lane。</li>
        <li>本 runner 目前读的是冻结 event digest，所以 refresh 的职责主要是保持 <code>state / summary / status page</code> 一致可见，而不是重算 raw-bar 信号。</li>
        <li>当前 handoff 结论：cron 正常刷新、网页可见、状态时间戳自然推进；后续只有在 <code>stale / error / refresh drift</code> 或 scope 变更时才需要抢占处理。</li>
      </ul>
    </div>

    <h2>Status</h2>
    {render_table(status_view, percent_cols={"lifetime_total_return_6bps", "win_rate"}, digits_cols={"mean_net_bps": 2})}

    <h2>Recent closed trades ledger (tail)</h2>
    {render_table(recent_ledger, digits_cols={"align_score": 4, "gross_bps": 2, "net_bps": 2})}

    <div class=\"card\">
      <p><b>Operator boundary</b></p>
      <ul class=\"muted\">
        <li>cron 里只允许 refresh + publish；不要在自动运行里偷偷改参数、扩 scope 或切换数据源。</li>
        <li>如果后续要从 frozen digest 升到 raw-bar runner，那是单独的 scope 变化，不能伪装成 routine refresh。</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
