#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_global_live"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_global_live"
OUT_PATH = SITE_DIR / "report.html"

STATUS_PATH = ART_DIR / "live_status.json"
RUN_SUMMARY_PATH = ART_DIR / "live_last_run_summary.json"
ORDERS_PATH = ART_DIR / "live_recent_orders.json"
REJECTIONS_PATH = ART_DIR / "live_recent_rejections.json"
POSITIONS_PATH = ART_DIR / "live_recent_positions.json"
WARNINGS_PATH = ART_DIR / "live_warnings.json"
COMPARE_PATH = ART_DIR / "live_vs_shadow.csv"
COMPARE_SUMMARY_PATH = ART_DIR / "live_vs_shadow_summary.json"
SHADOW_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "rank32b_shadow_global_winner" / "paper_summary.json"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def fmt(v: Any) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "-"
    return str(v)


def money(v: Any, digits: int = 3) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f} USDT"


def num(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def pct(v: Any, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def fmt_ts(v: Any) -> str:
    if v is None or v == "" or pd.isna(v):
        return "-"
    try:
        return pd.to_datetime(v, utc=True).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return str(v)


def render_table(df: pd.DataFrame, *, money_cols: set[str] | None = None, pct_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    money_cols = money_cols or set()
    pct_cols = pct_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        tds: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in money_cols:
                text = money(value, digits_cols.get(col, 3))
            elif col in pct_cols:
                text = pct(value, digits_cols.get(col, 2))
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = fmt(value)
            tds.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def card(title: str, value: str, sub: str) -> str:
    return f"<div class='card stat'><div class='k'>{escape(title)}</div><div class='v'>{escape(value)}</div><div class='s'>{sub}</div></div>"


def main() -> int:
    ensure_dir(SITE_DIR)
    status = read_json(STATUS_PATH, {}) or {}
    run_summary = read_json(RUN_SUMMARY_PATH, {}) or {}
    orders = pd.DataFrame(read_json(ORDERS_PATH, []) or [])
    rejections = pd.DataFrame(read_json(REJECTIONS_PATH, []) or [])
    positions = pd.DataFrame(read_json(POSITIONS_PATH, []) or [])
    warnings = pd.DataFrame(read_json(WARNINGS_PATH, []) or [])
    compare = read_csv(COMPARE_PATH)
    compare_summary = read_json(COMPARE_SUMMARY_PATH, {}) or {}
    shadow_summary = read_json(SHADOW_SUMMARY_PATH, {}) or {}

    for df, cols in [
        (orders, ["timestamp"]),
        (rejections, ["timestamp", "signal_confirmed_at", "timestamp"]),
        (positions, ["entry_time", "exit_time", "timeout_at"]),
        (warnings, ["timestamp"]),
        (compare, ["live_entry_time", "live_exit_time"]),
    ]:
        for col in cols:
            if col in df.columns:
                df[col] = df[col].map(fmt_ts)

    compare_live_net = pd.to_numeric(compare.get("live_net_pnl_usdt"), errors="coerce").fillna(0.0).sum() if not compare.empty else 0.0
    compare_shadow_net = pd.to_numeric(compare.get("shadow_proxy_net_pnl_usdt"), errors="coerce").fillna(0.0).sum() if not compare.empty else 0.0
    compare_delta = pd.to_numeric(compare.get("delta_vs_shadow_usdt"), errors="coerce").fillna(0.0).sum() if not compare.empty else 0.0

    cards = [
        card("recent finished run", fmt_ts(run_summary.get("run_finished_at") or status.get("last_run_utc")), "runner 最近一次完成时间"),
        card("allow live orders", "yes" if bool(run_summary.get("allow_live_orders")) else "no", f"mode={fmt(status.get('mode'))}"),
        card("open / closed", f"{int(run_summary.get('live_positions', 0) or 0)} / {int(run_summary.get('closed_trades_total', 0) or 0)}", f"risk rejects={int(run_summary.get('risk_rejections', 0) or 0)} · warnings={int(run_summary.get('warnings', 0) or 0)}"),
        card("live vs 1m audit", money(compare_live_net), f"shadow replay={money(compare_shadow_net)} · delta={money(compare_delta)}"),
        card("audit matches", f"{int(compare_summary.get('close_match_count', 0) or 0)} / {int(compare_summary.get('closed_trades', 0) or 0)}", f"exit-bucket match={int(compare_summary.get('exit_bucket_match_count', 0) or 0)}"),
        card("cross-lane busy watch", str(len(run_summary.get("conflict_busy_symbols", run_summary.get("core3_busy_symbols", [])) or [])), f"symbols={escape(', '.join((run_summary.get('conflict_busy_symbols', run_summary.get('core3_busy_symbols', [])) or [])[:8]) or 'none')}"),
        card("shadow reference", pct(shadow_summary.get("paper_marked_total_return"), 2), f"shadow closed={int(shadow_summary.get('paper_closed_trades', 0) or 0)}"),
    ]

    compare_view = compare[[c for c in ["signal_id", "symbol", "side", "live_entry_time", "live_exit_time", "live_exit_reason", "shadow_proxy_exit_time", "shadow_proxy_exit_reason", "live_net_pnl_usdt", "shadow_proxy_net_pnl_usdt", "delta_vs_shadow_usdt", "exit_bucket_match", "close_match"] if c in compare.columns]].tail(24).iloc[::-1] if not compare.empty else pd.DataFrame()
    orders_view = orders[[c for c in ["timestamp", "symbol", "order_role", "side", "price", "qty", "status", "client_order_id"] if c in orders.columns]].tail(24).iloc[::-1] if not orders.empty else pd.DataFrame()
    rejections_view = rejections[[c for c in ["timestamp", "symbol", "reason", "bar_key", "risk"] if c in rejections.columns]].tail(24).iloc[::-1] if not rejections.empty else pd.DataFrame()
    positions_view = positions[[c for c in ["symbol", "side", "entry_time", "exit_time", "exit_reason", "net_pnl"] if c in positions.columns]].tail(24).iloc[::-1] if not positions.empty else pd.DataFrame()
    warnings_view = warnings[[c for c in ["timestamp", "symbol", "message"] if c in warnings.columns]].tail(24).iloc[::-1] if not warnings.empty else pd.DataFrame()

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>rank32b global live</title>
  <style>
    body {{ font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #0b1220; color: #e5e7eb; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; padding: 32px 20px 64px; }}
    h1,h2 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.65; }}
    a {{ color: #60a5fa; }}
    .muted {{ color: #94a3b8; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }}
    .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px; }}
    .hero {{ background: linear-gradient(180deg, #111827 0%, #0f172a 100%); }}
    .k {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }}
    .v {{ font-size: 26px; font-weight: 800; margin-top: 8px; }}
    .s {{ margin-top: 8px; color: #9ca3af; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 28px; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }}
    th {{ background: #0f172a; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class='wrap'>
    <p class='muted'>Generated: {escape(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'))}</p>
    <p><a href='/momentum/factors/rank32b_canary/report.html'>← 回到 32b canary 主看板</a> ｜ <a href='/momentum/factors/rank32b_shadow_global_winner/report.html'>打开 global strongest-only shadow</a></p>
    <h1>global32b_live</h1>
    <p>这页盯的是 32b 的 <b>global strongest-only official-close live lane</b>。当前主版本已经关闭 <code>preview</code>，改为 <b>15m official close only</b>；新开仓只在 <code>00/15/30/45</code> 分钟的 <code>:05</code> 触发窗口内扫描，不在窗口内时只托管已有仓位。</p>

    <div class='card hero'>
      <h2>读法</h2>
      <ul>
        <li><b>official-close only</b>：当前 live 主线只接受 15m 收盘确认后的 official 信号，不再使用 preview。</li>
        <li><b>live vs 1m audit</b>：从 <b>live 实际入场价/入场时间/实际 qty</b> 出发，用当前 global shadow 的 <b>1m TP/SL/timeout</b> 规则复盘 exit，再和真钱 closed trades 对照。</li>
        <li><b>audit matches</b>：<code>close_match</code> 表示 exit bucket 一致，且时间差 ≤ 60 秒、PnL 差 ≤ 0.25 USDT。</li>
        <li><b>cross-lane busy watch</b>：最近这轮如果别的 lane 已占某个 symbol，global32b_live 会直接 skip。</li>
        <li><b>history reset</b>：2026-04-05 10:10 UTC 已归档旧版 preview/live 历史账本并清空 closed ledger，当前页面从 official 版本重新开始累计。</li>
      </ul>
      <p class='muted'>latest bar = {escape(fmt_ts(status.get('latest_evaluated_bar_time')))} · latest observed signal = {escape(fmt_ts(status.get('last_signal_time')))}</p>
    </div>

    <div class='grid'>{''.join(cards)}</div>

    <h2>1) live vs 1m audit 对比</h2>
    {render_table(compare_view, money_cols={'live_net_pnl_usdt','shadow_proxy_net_pnl_usdt','delta_vs_shadow_usdt'})}

    <h2>2) recent orders</h2>
    {render_table(orders_view, money_cols={'price'}, digits_cols={'qty': 6})}

    <h2>3) recent rejections</h2>
    {render_table(rejections_view)}

    <h2>4) recent positions / closed trades</h2>
    {render_table(positions_view, money_cols={'net_pnl'})}

    <h2>5) warnings</h2>
    {render_table(warnings_view)}

    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/rank32b_global_live/live_status.json'>live_status.json</a></li>
      <li><a href='../../artifacts/rank32b_global_live/live_last_run_summary.json'>live_last_run_summary.json</a></li>
      <li><a href='../../artifacts/rank32b_global_live/live_vs_shadow.csv'>live_vs_shadow.csv</a></li>
      <li><a href='../../artifacts/rank32b_global_live/live_vs_shadow_summary.json'>live_vs_shadow_summary.json</a></li>
      <li><a href='../../artifacts/rank32b_global_live/live_recent_orders.json'>live_recent_orders.json</a></li>
      <li><a href='../../artifacts/rank32b_global_live/live_recent_rejections.json'>live_recent_rejections.json</a></li>
      <li><a href='../../artifacts/rank32b_global_live/archive/official_transition_20260405T101057Z/live_recent_closed_trades.json'>archived preview/live closed ledger</a></li>
    </ul>
  </div>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
