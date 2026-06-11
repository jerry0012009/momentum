#!/usr/bin/env python3
"""Build Rank154 final archive close-out page."""
from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (  # noqa: E402
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

DOC = ROOT / "docs" / "RANK154_ARCHIVE_CLOSEOUT.md"
OUT = ROOT / "reports" / "site" / "paper" / "rank154_archive_closeout.html"


def inline_md(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', s)
    return s


def md_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False
    in_code = False
    code_buf: list[str] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for line in lines:
        raw = line.rstrip("\n")
        stripped = raw.strip()
        if stripped.startswith("```"):
            if not in_code:
                close_lists()
                in_code = True
                code_buf = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                in_code = False
            continue
        if in_code:
            code_buf.append(raw)
            continue
        if not stripped:
            close_lists()
            continue
        if stripped.startswith("# "):
            close_lists()
            # Page title is rendered separately.
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
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    return "\n".join(out)


def main() -> None:
    text = DOC.read_text(encoding="utf-8")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cards = [
        {"label": "Rank154", "value": "ARCHIVED", "subtitle": "failed release candidate", "kind": "bad"},
        {"label": "Rank154b", "value": "NO PAPER", "subtitle": "research lead only", "kind": "bad"},
        {"label": "154b core return", "value": "-4.3%", "subtitle": "20bps · 5d staggered", "kind": "bad"},
        {"label": "154b MaxDD", "value": "-63.1%", "subtitle": "not live-grade", "kind": "bad"},
        {"label": "5d price IC", "value": "+0.0195", "subtitle": "gross continuation exists", "kind": "warn"},
        {"label": "5d long-total IC", "value": "-0.0089", "subtitle": "after funding turns negative", "kind": "bad"},
    ]

    links = pd.DataFrame([
        {"page": "Rank154 Hub", "url": "https://jp.jerrypsy.top/momentum/paper/rank154_hub.html", "purpose": "目录入口，已改为归档导向"},
        {"page": "Rank154 Postmortem", "url": "https://jp.jerrypsy.top/momentum/paper/rank154_postmortem.html", "purpose": "原 combined 策略失败归因"},
        {"page": "Rank154b strict backtest", "url": "https://jp.jerrypsy.top/momentum/paper/rank154b_young_funding_backtest.html", "purpose": "young funding lead 的严格 no-go 审计"},
    ])
    link_html = render_table(
        links,
        columns=["page", "url", "purpose"],
        col_labels={"page": "页面", "url": "URL", "purpose": "用途"},
        col_formats={"url": lambda u: f'<a href="{html.escape(str(u))}">{html.escape(str(u))}</a>'},
    )

    body = ""
    body += render_metric_cards(cards)
    body += render_note(
        "<b>最终收口：</b>Rank154 原策略和 Rank154b 都不再进入 paper / release queue。旧 runner、旧网页、旧 paper PnL 只保留为历史证据。",
        kind="bad",
    )
    body += render_section("网页入口", link_html)
    body += render_section("完整归档说明", md_to_html(text))

    page = render_page(
        title="Rank154 / 154b · Final Archive Close-out",
        subtitle="failed release candidate · research lead only · no paper lane",
        body_html=body,
        generated_at=generated,
        nav_links=[
            {"href": "/momentum/paper/rank154_hub.html", "label": "Rank154 Hub"},
            {"href": "/momentum/paper/rank154_postmortem.html", "label": "Postmortem"},
            {"href": "/momentum/paper/rank154b_young_funding_backtest.html", "label": "154b Backtest"},
        ],
    )
    out = write_page(OUT, page)
    print(f"[ok] wrote {out} ({out.stat().st_size:,} bytes)")
    print("[url] https://jp.jerrypsy.top/momentum/paper/rank154_archive_closeout.html")


if __name__ == "__main__":
    main()
