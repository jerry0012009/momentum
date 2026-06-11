#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import render_metric_cards, render_note, render_page, render_section, render_table, write_page  # noqa: E402

DOC = ROOT / "docs" / "RANK213_ARCHIVE_CLOSEOUT.md"
RECEIPT = ROOT / "reports" / "artifacts" / "rank213_age90_live_canary_shell" / "rank213_archive_closeout_receipt.json"
OUT = ROOT / "reports" / "site" / "paper" / "rank213_archive_closeout.html"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', text)
    return text


def md_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            close_lists()
            continue
        if stripped.startswith("# "):
            close_lists()
            continue
        if stripped.startswith("## "):
            close_lists()
            out.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            continue
        if stripped.startswith("### "):
            close_lists()
            out.append(f"<h3>{inline_md(stripped[4:])}</h3>")
            continue
        if stripped.startswith("- "):
            if not in_ul:
                close_lists()
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md(stripped[2:])}</li>")
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            if not in_ol:
                close_lists()
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_md(m.group(2))}</li>")
            continue
        close_lists()
        out.append(f"<p>{inline_md(stripped)}</p>")
    close_lists()
    return "\n".join(out)


def money(value: Any) -> str:
    try:
        return f"{float(value):.3f} USDT"
    except Exception:
        return "-"


def main() -> None:
    receipt = read_json(RECEIPT)
    pre = receipt.get("pre_close_metrics", {}) if isinstance(receipt.get("pre_close_metrics"), dict) else {}
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = [
        {"label": "Rank213 age90", "value": "ARCHIVED", "subtitle": "live canary stopped", "kind": "bad"},
        {"label": "Pre-close Snapshot", "value": money(pre.get("snapshot_total_pnl")), "subtitle": f"realized={money(pre.get('realized_net_pnl'))} · open mtm={money(pre.get('open_unrealized_pnl'))}", "kind": "bad"},
        {"label": "Flatten Result", "value": str(int(receipt.get("remaining_position_count_after_flatten") or 0)), "subtitle": "remaining positions after flatten", "kind": "good" if int(receipt.get('remaining_position_count_after_flatten') or 0) == 0 else "warn"},
        {"label": "Timers", "value": str(receipt.get("timers_disable_status") or "-"), "subtitle": f"disabled at {receipt.get('timers_disabled_at_utc') or '-'}", "kind": "good" if str(receipt.get('timers_disable_status') or '') == 'all_disabled' else "warn"},
    ]

    orders_rows = []
    for row in receipt.get("flatten_orders", []) if isinstance(receipt.get("flatten_orders"), list) else []:
        result = row.get("result", {}) if isinstance(row.get("result"), dict) else {}
        orders_rows.append({
            "symbol": row.get("symbol"),
            "side": row.get("side"),
            "qty": row.get("current_exchange_qty"),
            "avg_price": result.get("avg_price"),
            "status": result.get("status") or row.get("status"),
            "client_order_id": result.get("client_order_id") or row.get("client_order_id"),
        })
    orders_df = pd.DataFrame(orders_rows)

    timer_rows = []
    for row in receipt.get("timer_results", []) if isinstance(receipt.get("timer_results"), list) else []:
        timer_rows.append({
            "unit": row.get("unit"),
            "ok": row.get("ok"),
            "returncode": row.get("returncode"),
            "stderr": row.get("stderr"),
        })
    timer_df = pd.DataFrame(timer_rows)

    body = ""
    body += render_metric_cards(cards)
    body += render_note(
        "<b>最终收口：</b>rank213 age90 钱柜 canary 已平仓并停调度；今后不应把旧 live shell 或旧 checklist 误读为仍在运行。",
        kind="bad",
    )
    if not orders_df.empty:
        body += render_section(
            "Flatten Orders",
            render_table(
                orders_df,
                columns=["symbol", "side", "qty", "avg_price", "status", "client_order_id"],
                col_labels={"symbol": "Symbol", "side": "Side", "qty": "Qty", "avg_price": "Avg Fill", "status": "Status", "client_order_id": "Client Order ID"},
            ),
        )
    if not timer_df.empty:
        body += render_section(
            "Timer Stop Receipt",
            render_table(
                timer_df,
                columns=["unit", "ok", "returncode", "stderr"],
                col_labels={"unit": "Unit", "ok": "OK", "returncode": "RC", "stderr": "stderr"},
            ),
        )
    body += render_section("完整归档说明", md_to_html(DOC.read_text(encoding="utf-8")))

    page = render_page(
        title="Rank213 age90 · Archive Close-out",
        subtitle="sustained-loss stop · live flatten complete · timers disabled",
        body_html=body,
        generated_at=generated,
        nav_links=[
            {"href": "/momentum/factors/rank213_live_vs_backtest_checklist/report.html", "label": "Live Checklist"},
            {"href": "/momentum/paper/rank213_age90_daily_shadow_runner.html", "label": "Daily Shadow"},
            {"href": "/momentum/paper/rank213_evidence_map.html", "label": "Evidence Map"},
        ],
    )
    out = write_page(OUT, page)
    print(f"[ok] wrote {out} ({out.stat().st_size:,} bytes)")
    print("[url] https://jp.jerrypsy.top/momentum/paper/rank213_archive_closeout.html")


if __name__ == "__main__":
    main()
