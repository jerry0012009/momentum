"""Reusable HTML rendering utilities for momentum report pages.

All pages use a consistent dark theme, responsive grid, and self-contained
CSS (no external dependencies). Import this module in build_*.py scripts
to avoid duplicating table/card/CSS boilerplate.

Usage:
    from momentum.html_render import (
        PAGE_CSS_DARK, render_page, render_metric_cards,
        render_table, render_note, render_section,
        fmt_pct, fmt_bps, fmt_usd, fmt_num, fmt_x,
    )
"""

from __future__ import annotations

from html import escape as _esc
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Number formatters
# ---------------------------------------------------------------------------

def fmt_pct(v: Any, digits: int = 2) -> str:
    """Format as percentage string. Handles NaN/None gracefully."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"{float(v) * 100:.{digits}f}%"


def fmt_bps(v: Any, digits: int = 1) -> str:
    """Format as basis points string."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"{float(v) * 10000:.{digits}f} bps"


def fmt_usd(v: Any, digits: int = 2) -> str:
    """Format as USD string."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"${float(v):,.{digits}f}"


def fmt_num(v: Any, digits: int = 2) -> str:
    """Format as plain number."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"{float(v):,.{digits}f}"


def fmt_x(v: Any, digits: int = 2) -> str:
    """Format as multiplier (e.g. 1.50x)."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"{float(v):.{digits}f}x"


def fmt_int(v: Any) -> str:
    """Format as integer."""
    if v is None or (isinstance(v, float) and (np.isnan(v) or np.isinf(v))):
        return "—"
    return f"{int(v):,}"


# ---------------------------------------------------------------------------
# CSS Themes
# ---------------------------------------------------------------------------

PAGE_CSS_DARK = """\
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body {
  margin: 0; background: #0b1220; color: #e5e7eb;
  font: 15px/1.65 -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', sans-serif;
}
.wrap { max-width: 1180px; margin: 0 auto; padding: 28px 18px 64px; }
h1 { font-size: 1.6em; margin: 0 0 8px; }
h2 { font-size: 1.25em; margin: 28px 0 12px; color: #cbd5e1; }
h3 { font-size: 1.05em; margin: 20px 0 8px; color: #94a3b8; }
p, li { line-height: 1.65; }
.muted { color: #94a3b8; font-size: 13px; }
a { color: #7dd3fc; text-decoration: none; }
a:hover { text-decoration: underline; }
code { background: #0f172a; color: #cbd5e1; padding: 2px 6px; border-radius: 6px; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: 18px 0 28px; }
.card {
  background: #111827; border: 1px solid #1f2937; border-radius: 14px; padding: 16px 18px;
}
.card .k { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
.card .v { font-size: 22px; font-weight: 700; line-height: 1.2; word-break: break-word; }
.card .s { margin-top: 6px; color: #64748b; font-size: 12px; }
.card.good { border-color: #22c55e33; }
.card.good .v { color: #4ade80; }
.card.bad { border-color: #ef444433; }
.card.bad .v { color: #f87171; }
.card.warn { border-color: #f59e0b33; }
.card.warn .v { color: #fbbf24; }
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  border: 1px solid #334155; border-radius: 16px; padding: 24px 28px; margin-bottom: 24px;
}
.hero h1 { color: #f1f5f9; }
.hero .subtitle { color: #94a3b8; margin-top: 4px; }
table { width: 100%; border-collapse: collapse; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; margin: 12px 0 24px; }
th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid #1f2937; font-size: 13px; vertical-align: top; }
th { background: #0f172a; color: #cbd5e1; font-weight: 600; white-space: nowrap; }
td { color: #d1d5db; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #1a2332; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.pos { color: #4ade80; }
.neg { color: #f87171; }
.note {
  border-left: 4px solid #3b82f6; background: #1e3a5f22;
  padding: 12px 16px; border-radius: 0 10px 10px 0; margin: 16px 0;
}
.note.warn { border-left-color: #f59e0b; background: #78350f22; }
.note.good { border-left-color: #22c55e; background: #14532d22; }
.note.bad { border-left-color: #ef4444; background: #7f1d1d22; }
.pill {
  display: inline-block; padding: 2px 10px; border-radius: 999px;
  background: #1e293b; color: #94a3b8; font-size: 12px; margin: 0 4px 4px 0;
}
.tag { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; }
.tag-long { background: #14532d; color: #4ade80; }
.tag-short { background: #7f1d1d; color: #f87171; }
.tag-flat { background: #1e293b; color: #94a3b8; }
.footer { margin-top: 40px; padding-top: 16px; border-top: 1px solid #1f2937; color: #475569; font-size: 12px; }
.chart-placeholder {
  background: #111827; border: 1px solid #1f2937; border-radius: 14px;
  padding: 40px; text-align: center; color: #475569; margin: 12px 0 24px;
}
"""


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def render_page(
    title: str,
    body_html: str,
    *,
    subtitle: str = "",
    generated_at: str = "",
    css: str = PAGE_CSS_DARK,
    nav_links: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Render a complete self-contained HTML page."""
    nav_html = ""
    if nav_links:
        parts = [f'<a href="{_esc(l["href"])}">{_esc(l["label"])}</a>' for l in nav_links]
        nav_html = '<p class="muted">' + " · ".join(parts) + "</p>"

    gen_line = ""
    if generated_at:
        gen_line = f'<p class="muted">Generated: {_esc(generated_at)}</p>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<p class="muted subtitle">{_esc(subtitle)}</p>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_esc(title)}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  {gen_line}
  {nav_html}
  <div class="hero">
    <h1>{_esc(title)}</h1>
    {subtitle_html}
  </div>
  {body_html}
</div>
</body>
</html>"""


def render_section(title: str, content: str, *, level: int = 2) -> str:
    """Wrap content in a section with heading."""
    tag = f"h{level}"
    return f"<{tag}>{_esc(title)}</{tag}>\n{content}"


def render_note(text: str, *, kind: str = "") -> str:
    """Render a callout note. kind: '' (info), 'warn', 'good', 'bad'."""
    cls = f"note {kind}" if kind else "note"
    return f'<div class="{cls}">{text}</div>'


# ---------------------------------------------------------------------------
# Metric cards
# ---------------------------------------------------------------------------

def render_metric_cards(cards: List[Dict[str, str]]) -> str:
    """Render a grid of KPI metric cards.

    Each card dict: {"label": str, "value": str, "subtitle": str?, "kind": str?}
    kind: '' (default), 'good', 'bad', 'warn'
    """
    items = []
    for c in cards:
        kind = c.get("kind", "")
        cls = f"card {kind}" if kind else "card"
        sub = f'<div class="s">{c["subtitle"]}</div>' if c.get("subtitle") else ""
        items.append(
            f'<div class="{cls}">'
            f'<div class="k">{_esc(c["label"])}</div>'
            f'<div class="v">{c["value"]}</div>'
            f'{sub}</div>'
        )
    return '<div class="grid">\n' + "\n".join(items) + "\n</div>"


# ---------------------------------------------------------------------------
# Table rendering
# ---------------------------------------------------------------------------

def _cell_html(val: Any) -> str:
    """Convert a cell value to HTML-safe string."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<td class="num">—</td>'
    return f"<td>{_esc(str(val))}</td>"


def _num_cell_html(val: Any, fmt_fn=None, positive_good: bool = False) -> str:
    """Render a numeric cell with optional formatting and color class."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return '<td class="num">—</td>'
    formatted = fmt_fn(val) if fmt_fn else str(val)
    cls_parts = ["num"]
    if positive_good and isinstance(val, (int, float)):
        if val > 0:
            cls_parts.append("pos")
        elif val < 0:
            cls_parts.append("neg")
    return f'<td class="{" ".join(cls_parts)}">{formatted}</td>'


def render_table(
    df: pd.DataFrame,
    *,
    columns: Optional[List[str]] = None,
    col_labels: Optional[Dict[str, str]] = None,
    col_formats: Optional[Dict[str, Any]] = None,
    col_positive_good: Optional[List[str]] = None,
    highlight_rows: Optional[List[int]] = None,
    max_rows: int = 200,
) -> str:
    """Render a DataFrame as an HTML table.

    Args:
        df: Source DataFrame
        columns: Columns to include (default: all)
        col_labels: Display name overrides {col_name: display_label}
        col_formats: Format functions per column {col_name: callable}
        col_positive_good: Columns where positive=green, negative=red
        highlight_rows: Row indices to highlight
        max_rows: Maximum rows to render
    """
    if df.empty:
        return '<p class="muted">（无数据）</p>'

    cols = columns or list(df.columns)
    labels = col_labels or {}
    fmts = col_formats or {}
    pos_good = set(col_positive_good or [])
    hl = set(highlight_rows or [])

    header = "".join(f"<th>{_esc(labels.get(c, c))}</th>" for c in cols)

    rows_html = []
    for i, (_, row) in enumerate(df.head(max_rows).iterrows()):
        if i in hl:
            row_open = '<tr style="background:#1a2332">'
        else:
            row_open = "<tr>"
        cells = []
        for c in cols:
            val = row.get(c)
            if c in fmts:
                cells.append(_num_cell_html(val, fmt_fn=fmts[c], positive_good=c in pos_good))
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                cells.append(_num_cell_html(val, positive_good=c in pos_good))
            else:
                cells.append(_cell_html(val))
        rows_html.append(row_open + "".join(cells) + "</tr>")

    return (
        "<table>"
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody>"
        "</table>"
    )


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def write_page(path: Path, html: str) -> Path:
    """Write HTML page to disk, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def read_artifact_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read an artifact CSV, returning empty DataFrame if missing."""
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, **kwargs)


def read_artifact_json(path: Path) -> Dict[str, Any]:
    """Read an artifact JSON, returning empty dict if missing."""
    if not path.exists():
        return {}
    import json
    return json.loads(path.read_text(encoding="utf-8"))
