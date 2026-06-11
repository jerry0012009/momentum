#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "TODO.md"
OUT_DIR = ROOT / "reports" / "site" / "plans"
OUT_PATH = OUT_DIR / "momentum_todo.html"

URL_RE = re.compile(r"(https?://[^\s<]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
ORDERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def inline_md(text: str) -> str:
    text = escape(text)
    text = CODE_RE.sub(r"<code>\1</code>", text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = URL_RE.sub(r'<a href="\1">\1</a>', text)
    return text


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[`'\"]", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff\-\s]+", "", text)
    text = re.sub(r"\s+", "-", text)
    return text or "section"


def markdown_to_html(lines: list[str]) -> tuple[str, str]:
    chunks: list[str] = []
    para: list[str] = []
    list_mode: str | None = None
    toc_items: list[tuple[int, str, str]] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            chunks.append(f"<p>{inline_md(' '.join(s.strip() for s in para))}</p>")
            para = []

    def close_list() -> None:
        nonlocal list_mode
        if list_mode == "ul":
            chunks.append("</ul>")
        elif list_mode == "ol":
            chunks.append("</ol>")
        list_mode = None

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            flush_para()
            close_list()
            continue

        if stripped == "---":
            flush_para()
            close_list()
            chunks.append("<hr />")
            continue

        if stripped.startswith("### "):
            flush_para()
            close_list()
            text = stripped[4:]
            anchor = slugify(text)
            toc_items.append((3, text, anchor))
            chunks.append(f'<h3 id="{escape(anchor)}">{inline_md(text)}</h3>')
            continue

        if stripped.startswith("## "):
            flush_para()
            close_list()
            text = stripped[3:]
            anchor = slugify(text)
            toc_items.append((2, text, anchor))
            chunks.append(f'<h2 id="{escape(anchor)}">{inline_md(text)}</h2>')
            continue

        if stripped.startswith("# "):
            flush_para()
            close_list()
            text = stripped[2:]
            chunks.append(f"<h1>{inline_md(text)}</h1>")
            continue

        ordered = ORDERED_RE.match(stripped)
        if ordered:
            flush_para()
            if list_mode != "ol":
                close_list()
                chunks.append("<ol>")
                list_mode = "ol"
            chunks.append(f"<li>{inline_md(ordered.group(2))}</li>")
            continue

        if stripped.startswith("> "):
            flush_para()
            close_list()
            chunks.append(f'<blockquote>{inline_md(stripped[2:])}</blockquote>')
            continue

        if stripped.startswith("- "):
            flush_para()
            if list_mode != "ul":
                close_list()
                chunks.append("<ul>")
                list_mode = "ul"
            body = stripped[2:]
            css = ""
            if body.startswith("[x]"):
                css = ' class="done"'
            elif body.startswith("[ ]"):
                css = ' class="todo"'
            chunks.append(f"<li{css}>{inline_md(body)}</li>")
            continue

        para.append(stripped)

    flush_para()
    close_list()

    toc_parts = []
    if toc_items:
        toc_parts.append('<ul class="toc-list">')
        for level, text, anchor in toc_items:
            css = "toc-h2" if level == 2 else "toc-h3"
            toc_parts.append(f'<li class="{css}"><a href="#{escape(anchor)}">{inline_md(text)}</a></li>')
        toc_parts.append("</ul>")

    return "\n".join(chunks), "\n".join(toc_parts)


def render_page(md_text: str) -> str:
    lines = md_text.splitlines()
    title = "Momentum TODO / Roadmap"
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body_html, toc_html = markdown_to_html(lines)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      --fg: #111827;
      --muted: #6b7280;
      --border: #e5e7eb;
      --bg-soft: #f8fafc;
      --bg-pill: #eef2ff;
      --bg-done: #ecfdf5;
      --bg-todo: #fff7ed;
      --link: #2563eb;
    }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--fg); margin: 0; background: white; }}
    .wrap {{ max-width: 1280px; margin: 0 auto; padding: 32px 20px 64px; }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .topnav {{ margin-bottom: 18px; }}
    .hero {{ border: 1px solid var(--border); border-radius: 16px; padding: 22px 24px; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); margin-bottom: 20px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 34px; }}
    .muted {{ color: var(--muted); }}
    .layout {{ display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 22px; align-items: start; }}
    .card {{ border: 1px solid var(--border); border-radius: 14px; background: white; padding: 18px 20px; }}
    .toc {{ position: sticky; top: 16px; }}
    .toc h2 {{ margin-top: 0; font-size: 18px; }}
    .toc-list {{ list-style: none; padding: 0; margin: 0; }}
    .toc-list li {{ margin: 8px 0; line-height: 1.35; }}
    .toc-h3 {{ padding-left: 12px; font-size: 14px; }}
    .content h1:first-child {{ display: none; }}
    .content h2 {{ margin-top: 28px; padding-top: 8px; border-top: 1px solid var(--border); font-size: 28px; }}
    .content h3 {{ margin-top: 22px; font-size: 21px; }}
    .content p {{ line-height: 1.7; }}
    .content ul, .content ol {{ padding-left: 22px; line-height: 1.7; }}
    .content li.done {{ background: var(--bg-done); }}
    .content li.todo {{ background: var(--bg-todo); }}
    .content li {{ padding: 3px 6px; border-radius: 8px; margin: 3px 0; }}
    .content code {{ background: var(--bg-soft); border: 1px solid var(--border); border-radius: 6px; padding: 1px 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.95em; }}
    blockquote {{ margin: 14px 0; padding: 10px 14px; border-left: 4px solid #93c5fd; background: #eff6ff; border-radius: 8px; }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 22px 0; }}
    .pills {{ display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }}
    .pill {{ background: var(--bg-pill); color: #3730a3; border-radius: 999px; padding: 6px 12px; font-size: 13px; }}
    @media (max-width: 960px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .toc {{ position: static; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topnav"><a href="../index.html">← Back to Momentum site index</a></div>
    <div class="hero">
      <h1>{escape(title)}</h1>
      <p class="muted">当前 `jerry/momentum` 项目的重排任务清单：从 “parallel channel 单线推进” 调整为先验证 <strong>structure-event alpha</strong>，再决定 channel 是否升级为主线。</p>
      <div class="pills">
        <span class="pill">Generated: {escape(generated_at)}</span>
        <span class="pill">Source: docs/TODO.md</span>
        <span class="pill">For agent task pickup</span>
      </div>
    </div>
    <div class="layout">
      <aside class="card toc">
        <h2>目录</h2>
        {toc_html}
      </aside>
      <main class="card content">
        {body_html}
      </main>
    </div>
  </div>
</body>
</html>'''


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_text = SRC.read_text(encoding="utf-8")
    OUT_PATH.write_text(render_page(md_text), encoding="utf-8")
    print(f"[ok] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
