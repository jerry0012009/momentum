#!/usr/bin/env python3
"""Build Rank 154 admission notes HTML page from two research markdown files."""
from __future__ import annotations

import re
from html import escape as _esc
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from momentum.html_render import render_page, write_page, PAGE_CSS_DARK, render_section, render_note

# Source markdown files
MD_HONESTY = ROOT / "research" / "optimization_loop" / "2026-03-24_1046_crypto-stat-arb-p2-honesty-execution.md"
MD_PROMOTE = ROOT / "research" / "optimization_loop" / "2026-03-24_0950_crypto-stat-arb-followup-promote-p2.md"

# Output
OUT_HTML = ROOT / "reports" / "site" / "reading" / "optimization_loop" / "rank154_admission_notes.html"


def md_to_html(md: str) -> str:
    """Simple markdown-to-HTML converter: headers, bold, code, lists, blockquotes, tables, paragraphs."""
    lines = md.split("\n")
    html_parts: list[str] = []
    in_list = False
    in_table = False
    table_header_done = False

    def flush_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    def flush_table():
        nonlocal in_table, table_header_done
        if in_table:
            html_parts.append("</tbody></table>")
            in_table = False
            table_header_done = False

    def inline(text: str) -> str:
        # Escape HTML first
        text = _esc(text)
        # Inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text

    for raw in lines:
        line = raw.rstrip()

        # Blank line
        if not line.strip():
            flush_list()
            flush_table()
            continue

        # Blockquote
        if line.startswith("> "):
            flush_list()
            flush_table()
            content = inline(line[2:])
            html_parts.append(f'<blockquote class="note">{content}</blockquote>')
            continue

        # Table row
        if line.startswith("|") and line.endswith("|"):
            flush_list()
            cells = [c.strip() for c in line.strip("|").split("|")]
            # Skip separator rows
            if all(re.match(r'^[-:]+$', c) for c in cells):
                table_header_done = True
                continue
            if not in_table:
                html_parts.append('<table>')
                in_table = True
                # First row is header
                html_parts.append('<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
                table_header_done = True
            else:
                html_parts.append('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in cells) + '</tr>')
            continue

        # Headers
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            flush_list()
            flush_table()
            level = len(m.group(1))
            content = inline(m.group(2))
            html_parts.append(f'<h{level}>{content}</h{level}>')
            continue

        # List items
        if re.match(r'^[-*]\s+', line):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            content = inline(re.sub(r'^[-*]\s+', '', line))
            html_parts.append(f'<li>{content}</li>')
            continue

        # Ordered list
        m_ol = re.match(r'^(\d+)\.\s+(.*)', line)
        if m_ol:
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            content = inline(m_ol.group(2))
            html_parts.append(f'<li><strong>{m_ol.group(1)}.</strong> {content}</li>')
            continue

        # Regular paragraph
        flush_list()
        flush_table()
        html_parts.append(f'<p>{inline(line)}</p>')

    flush_list()
    flush_table()
    return "\n".join(html_parts)


def build_annotations_honesty() -> str:
    """Chinese annotations for the honesty/execution audit document."""
    parts = []
    parts.append(render_note(
        '<strong>📝 中文注释 — 回测执行现实性审计</strong><br>'
        '本文档的核心问题是：Crypto-Stat-Arb 的回测结果是否依赖了过于乐观的执行假设？'
        'bot3 通过将权重和 funding 滞后一天来做"诚实压力测试"。',
        kind="",
    ))
    return "\n".join(parts)


def build_annotations_promote() -> str:
    """Chinese annotations for the P2 promotion document."""
    parts = []
    parts.append(render_note(
        '<strong>📝 中文注释 — P2 晋升成本敏感性分析</strong><br>'
        '这是 Rank 154 的首次正式 follow-up：对 carry / momentum / breakout 三条腿分别做'
        '佣金敏感性和 trade buffer 敏感性测试，决定是否从 P1 推进到 P2。',
        kind="",
    ))
    return "\n".join(parts)


def build_backtest_annotations() -> str:
    """Annotations for the key backtest numbers."""
    return render_section("📊 关键数据解读", """
<div class="grid">
  <div class="card good">
    <div class="k">Combined 10bps Sharpe</div>
    <div class="v">1.31 → 1.27</div>
    <div class="s">滞后1天后仅降0.04，说明边际不靠同日执行幻觉</div>
  </div>
  <div class="card good">
    <div class="k">Funding 贡献</div>
    <div class="v">去掉 funding → Sharpe 1.08</div>
    <div class="s">funding 是真实贡献项（+0.19 Sharpe），但 same-day vs lagged 差异很小</div>
  </div>
  <div class="card warn">
    <div class="k">Buffer 敏感性</div>
    <div class="v">0% buffer → Sharpe 0.73</div>
    <div class="s">buffer=0% 换手极高（61.9%/日），5% 是合理甜点（7.2%/日）</div>
  </div>
  <div class="card">
    <div class="k">分腿归因</div>
    <div class="v">carry 29.8% / breakout 13.6%</div>
    <div class="s">momentum 仅 5.6% 边际很弱，主要贡献来自 carry + breakout</div>
  </div>
</div>
""", level=2)


def build_verdict_summary() -> str:
    """Final verdict callout."""
    return render_note(
        '<strong>结论：keep_P2</strong> — 权重 + funding 滞后一天后仍保持正边（Sharpe 1.27），'
        '但边际明显依赖 trade_buffer≈5% 的低换手实现，且 carry 单腿换手远高于 combined，'
        '未到可直接升 P3 的稳健度。<br><br>'
        '<strong>Scorecard：</strong>'
        '执行现实性 7/10 · funding 诚实度 7/10 · buffer 摩擦稳健性 6/10 · P3 就绪度 5/10',
        kind="good",
    )


def main() -> None:
    # Read markdown files
    md_honesty = MD_HONESTY.read_text(encoding="utf-8")
    md_promote = MD_PROMOTE.read_text(encoding="utf-8")

    # Convert to HTML
    html_honesty = md_to_html(md_honesty)
    html_promote = md_to_html(md_promote)

    # Assemble page
    nav_links = [
        {"href": "../paper/rank154_overview.html", "label": "← Rank 154 Overview"},
        {"href": "../../index.html", "label": "Site Index"},
    ]

    body_parts = []
    body_parts.append(build_backtest_annotations())
    body_parts.append(build_verdict_summary())

    # Section 1: Honesty audit
    body_parts.append(render_section("Part 1 — P2 Admission Honesty / Execution Audit (2026-03-24 10:46 UTC)", "", level=2))
    body_parts.append(build_annotations_honesty())
    body_parts.append(f'<div class="reading-md">{html_honesty}</div>')

    # Section 2: Promotion cost sensitivity
    body_parts.append(render_section("Part 2 — P2 Promotion Cost Sensitivity (2026-03-24 09:50 UTC)", "", level=2))
    body_parts.append(build_annotations_promote())
    body_parts.append(f'<div class="reading-md">{html_promote}</div>')

    body = "\n".join(body_parts)

    # Extra CSS for reading content
    extra_css = """
.reading-md { margin: 18px 0; }
.reading-md h1 { font-size: 1.4em; margin: 24px 0 8px; color: #f1f5f9; }
.reading-md h2 { font-size: 1.15em; margin: 20px 0 8px; color: #cbd5e1; }
.reading-md h3 { font-size: 1.0em; margin: 16px 0 6px; color: #94a3b8; }
.reading-md p { margin: 8px 0; }
.reading-md ul { margin: 8px 0; padding-left: 24px; }
.reading-md li { margin: 4px 0; }
.reading-md blockquote {
  border-left: 4px solid #334155; padding: 8px 16px; margin: 12px 0;
  background: #111827; border-radius: 0 10px 10px 0; color: #94a3b8;
}
.reading-md table { margin: 12px 0; }
"""
    css = PAGE_CSS_DARK + extra_css

    page = render_page(
        title="Rank 154 · 研发笔记：回测审计与成本分析",
        body_html=body,
        subtitle="Crypto-Stat-Arb · P2 admission honesty audit + cost sensitivity analysis",
        generated_at="2026-03-24",
        css=css,
        nav_links=nav_links,
    )

    out = write_page(OUT_HTML, page)
    print(f"Wrote {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
