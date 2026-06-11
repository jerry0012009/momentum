#!/usr/bin/env python3
"""Build Rank 154 research hub / index page linking all published rank154 content.

Generates a single-page directory with quick links, research timeline,
live status metrics, and key artifact references.

Usage:
    python scripts/build_rank154_hub.py
    python scripts/build_rank154_hub.py --open
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from momentum.html_render import (
    PAGE_CSS_DARK,
    fmt_num,
    fmt_pct,
    fmt_usd,
    read_artifact_json,
    render_metric_cards,
    render_note,
    render_page,
    render_section,
    render_table,
    write_page,
)

# --- Paths ---
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank154_crypto_stat_arb_runner"
STATE_PATH = ART_DIR / "rank154_paper_state.json"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank154_hub.html"

# --- Quick links ---
QUICK_LINKS = [
    {
        "label": "Final Archive Close-out",
        "desc": "最终收口 · Rank154 failed release candidate · 154b research lead only",
        "href": "/momentum/paper/rank154_archive_closeout.html",
    },
    {
        "label": "Postmortem / Archive",
        "desc": "原 Rank154 失败归因：IC、分位 spread、long/short leg、age bucket",
        "href": "/momentum/paper/rank154_postmortem.html",
    },
    {
        "label": "Rank154b Strict Backtest",
        "desc": "young funding lead：price IC 有，但 after funding/cost 不过关",
        "href": "/momentum/paper/rank154b_young_funding_backtest.html",
    },
    {
        "label": "历史策略总览",
        "desc": "Overview · 旧策略架构、回测审计、持仓详情（仅历史证据）",
        "href": "/momentum/paper/rank154_overview.html",
    },
    {
        "label": "Historical Paper Report",
        "desc": "旧每日 forward paper 跑单报告（已停止作为 release evidence）",
        "href": "/momentum/factors/paper_rank154_crypto_stat_arb_runner/report.html",
    },
    {
        "label": "Intake Digest / Admission Notes",
        "desc": "旧 intake 与 P2/P3 admission 记录（历史脉络）",
        "href": "/momentum/reading/optimization_loop/rank154_admission_notes.html",
    },
]

# --- Research timeline ---
TIMELINE = pd.DataFrame(
    {
        "time": [
            "2026-03-24 09:22",
            "2026-03-24 09:50",
            "2026-03-24 10:46",
            "2026-03-24 12:49",
            "2026-03-24 13:00–16:04",
            "2026-03-25 → 2026-05-10",
            "2026-05-09",
            "2026-05-09",
            "2026-05-10",
        ],
        "stage": [
            "Fresh Intake",
            "Surviving Follow-up",
            "P2 Admission",
            "P3 Handoff",
            "Engineering",
            "Paper Running (Historical)",
            "Postmortem",
            "154b Lead Audit",
            "Final Archive",
        ],
        "description": [
            "carry+momo+breakout intake from ryanczm/Crypto-Stat-Arb",
            "Cost sensitivity & buffer analysis",
            "Honesty audit: lagged execution survives",
            "Paper launch queue readiness",
            "Runner skeleton, scheduler, sidecar offload",
            "Daily forward paper retained as historical evidence, not release evidence",
            "Original combined signal failed long-history IC/spread/leg attribution",
            "Young funding lead failed after funding + realistic turnover cost",
            "Rank154 and 154b archived / no paper lane",
        ],
        "link": [
            '<a href="/momentum/reading/quant_digests/2026-03-24_0922_crypto-stat-arb-carry-momo-breakout-intake.html">Digest</a>',
            '<a href="/momentum/reading/optimization_loop/rank154_admission_notes.html">Admission Notes</a>',
            '<a href="/momentum/reading/optimization_loop/rank154_admission_notes.html">Admission Notes</a>',
            "—",
            "—",
            '<a href="/momentum/factors/paper_rank154_crypto_stat_arb_runner/report.html">Historical Report</a>',
            '<a href="/momentum/paper/rank154_postmortem.html">Postmortem</a>',
            '<a href="/momentum/paper/rank154b_young_funding_backtest.html">154b Backtest</a>',
            '<a href="/momentum/paper/rank154_archive_closeout.html">Close-out</a>',
        ],
    }
)

# --- Key artifacts ---
ARTIFACTS = [
    ("Equity Curve CSV", "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_equity_curve.csv"),
    ("Paper State JSON", "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_state.json"),
    ("Paper Status CSV", "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_status.csv"),
    ("Open Positions CSV", "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_open_positions.csv"),
    ("Rebalance Trades CSV", "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_rebalance_trades.csv"),
    ("Strategy Source", "src/momentum/strategies/rank154_crypto_stat_arb.py"),
    ("Paper Runner Script", "scripts/run_rank154_crypto_stat_arb_paper_runner.py"),
    ("Live Config YAML", "config/strategies/rank154_crypto_stat_arb_tiny_live.yaml"),
]


def build_hero() -> str:
    """Extra description below the render_page hero."""
    return """
<p style="color:#94a3b8; margin:-8px 0 20px; font-size:14px;">
  日频横截面 carry + momentum + breakout 多空组合 · Binance USDT-M Perpetuals · <b style="color:#f87171">已归档，不再作为 release candidate</b>
</p>
"""


def build_quick_links() -> str:
    """Render quick-link cards in a responsive grid."""
    cards = []
    for lnk in QUICK_LINKS:
        cards.append(
            f'<div class="card" style="cursor:pointer" onclick="location.href=\'{lnk["href"]}\'">'
            f'<div class="k">{lnk["label"]}</div>'
            f'<div class="v" style="font-size:16px"><a href="{lnk["href"]}">{lnk["desc"]}</a></div>'
            f"</div>"
        )
    return '<div class="grid">\n' + "\n".join(cards) + "\n</div>"


def build_timeline() -> str:
    """Render the research timeline as an HTML table (manual for link column)."""
    header = "<tr><th>Time</th><th>Stage</th><th>Description</th><th>Link</th></tr>"
    rows = []
    for _, r in TIMELINE.iterrows():
        rows.append(
            f"<tr><td>{r['time']}</td>"
            f"<td><b>{r['stage']}</b></td>"
            f"<td>{r['description']}</td>"
            f"<td>{r['link']}</td></tr>"
        )
    return f"<table><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def build_status(state: dict) -> str:
    """Final archive status section."""
    # Historical paper metrics are kept only to make clear why they are not release evidence.
    equity = state.get("current_equity", state.get("current_equity_usd", 11712.38))
    initial = state.get("initial_equity_usd", state.get("config", {}).get("initial_equity_usd", 10000.0))
    ret = (equity / initial - 1) if initial else 0.1712
    n_days = state.get("n_days", 45)

    cards = [
        {
            "label": "Final Status",
            "value": "ARCHIVED",
            "subtitle": "failed release candidate / no paper lane",
            "kind": "bad",
        },
        {
            "label": "Rank154b Verdict",
            "value": "NO-GO",
            "subtitle": "price IC exists; after funding/cost fails",
            "kind": "bad",
        },
        {
            "label": "Historical Paper Equity",
            "value": fmt_usd(equity),
            "subtitle": f"Return: {fmt_pct(ret)} · historical only · {n_days} days",
            "kind": "warn",
        },
        {
            "label": "Required Next Step",
            "value": "Do not optimize 154",
            "subtitle": "new funding-age work needs new rank/name + regime",
            "kind": "warn",
        },
    ]
    note = render_note(
        "<b>状态解释：</b>旧 paper runner 的正收益不能再作为 release gate 证据。最终收口以 "
        "<code>docs/RANK154_ARCHIVE_CLOSEOUT.md</code> 和 <code>rank154_archive_closeout.html</code> 为准。",
        kind="bad",
    )
    return render_metric_cards(cards) + note


def build_artifacts_table() -> str:
    """Key artifacts list."""
    rows = []
    for label, path in ARTIFACTS:
        rows.append(f"<tr><td>{label}</td><td><code>{path}</code></td></tr>")
    header = "<tr><th>Artifact</th><th>Path</th></tr>"
    return f"<table><thead>{header}</thead><tbody>{''.join(rows)}</tbody></table>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Rank 154 research hub page")
    parser.add_argument("--open", action="store_true", help="Open in browser after build")
    args = parser.parse_args()

    # Load live state
    state = read_artifact_json(STATE_PATH)

    # Build sections
    sections = []
    sections.append(build_hero())
    sections.append(render_section("Quick Links", build_quick_links()))
    sections.append(render_section("Research Timeline", build_timeline()))
    sections.append(render_section("Current Status", build_status(state)))
    sections.append(render_section("Key Artifacts", build_artifacts_table()))

    body = "\n\n".join(sections)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = render_page(
        title="Rank 154 · Crypto-Stat-Arb · 归档目录",
        subtitle="最终状态：ARCHIVED / failed release candidate；154b research lead only / no paper lane",
        body_html=body,
        generated_at=now,
        nav_links=[
            {"href": "/momentum/paper/rank154_archive_closeout.html", "label": "Final Archive"},
            {"href": "/momentum/paper/rank154_postmortem.html", "label": "Postmortem"},
            {"href": "/momentum/paper/rank154b_young_funding_backtest.html", "label": "154b No-Go"},
            {"href": "/momentum/paper/rank154_overview.html", "label": "Historical Overview"},
        ],
    )

    out = write_page(SITE_PATH, html)
    print(f"[ok] wrote {out} ({out.stat().st_size:,} bytes)")
    print(f"[url] https://jp.jerrypsy.top/momentum/paper/rank154_hub.html")

    if args.open:
        import webbrowser
        webbrowser.open(str(out))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
