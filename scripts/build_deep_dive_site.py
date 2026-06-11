#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "research" / "deep_dives"
OUT_DIR = ROOT / "reports" / "site" / "reading" / "deep_dives"
MAIN_INDEX = ROOT / "reports" / "site" / "index.html"

URL_RE = re.compile(r"(https?://[^\s<]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
ORDERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")
META_RE = re.compile(r"^-\s*([^：:]+)[：:]\s*(.*)$")


@dataclass
class DeepDive:
    path: Path
    slug: str
    title: str
    rel_html: str
    time_text: str
    kind: str
    tags: str
    relevance: str
    summary: str
    body_html: str
    toc_html: str


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

        if stripped.startswith("### "):
            flush_para()
            close_list()
            text = stripped[4:]
            anchor = slugify(text)
            toc_items.append((3, text, anchor))
            chunks.append(f"<h3 id=\"{escape(anchor)}\">{inline_md(text)}</h3>")
            continue
        if stripped.startswith("## "):
            flush_para()
            close_list()
            text = stripped[3:]
            anchor = slugify(text)
            toc_items.append((2, text, anchor))
            chunks.append(f"<h2 id=\"{escape(anchor)}\">{inline_md(text)}</h2>")
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

        if stripped.startswith("- "):
            flush_para()
            if list_mode != "ul":
                close_list()
                chunks.append("<ul>")
                list_mode = "ul"
            chunks.append(f"<li>{inline_md(stripped[2:])}</li>")
            continue

        para.append(stripped)

    flush_para()
    close_list()

    toc_parts = []
    if toc_items:
        toc_parts.append('<ul class="toc-list">')
        for level, text, anchor in toc_items:
            css = "toc-h2" if level == 2 else "toc-h3"
            toc_parts.append(
                f'<li class="{css}"><a href="#{escape(anchor)}">{inline_md(text)}</a></li>'
            )
        toc_parts.append("</ul>")
    return "\n".join(chunks), "\n".join(toc_parts)


def parse_deep_dive(path: Path) -> DeepDive:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = path.stem
    time_text = ""
    kind = ""
    tags = ""
    relevance = ""
    summary = ""

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    for line in lines:
        m = META_RE.match(line.strip())
        if not m:
            continue
        key = m.group(1).strip()
        value = m.group(2).strip()
        if key == "时间":
            time_text = value
        elif key == "类型":
            kind = value
        elif key == "主题标签":
            tags = value
        elif key == "当前相关性":
            relevance = value

    for idx, line in enumerate(lines):
        if line.strip() == "## 1. 为什么这篇对你现在特别重要" or line.strip() == "## 1. 为什么这篇值得你现在认真看" or line.strip() == "## 1. 这个仓库到底是干什么的" or line.strip() == "## 1. 为什么 `pytrendline` 对你当前阶段特别重要":
            for nxt in lines[idx + 1 :]:
                if nxt.strip() and not nxt.strip().startswith("-"):
                    summary = nxt.strip()
                    break
            break
    if not summary:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                summary = stripped
                break

    body_html, toc_html = markdown_to_html(lines[1:])
    rel_html = f"reading/deep_dives/{path.stem}.html"
    return DeepDive(
        path=path,
        slug=path.stem,
        title=title,
        rel_html=rel_html,
        time_text=time_text,
        kind=kind,
        tags=tags,
        relevance=relevance,
        summary=summary,
        body_html=body_html,
        toc_html=toc_html,
    )


def render_deep_dive_page(d: DeepDive) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(d.title)}</title>
  <style>
    :root {{
      --fg: #111827;
      --muted: #6b7280;
      --border: #e5e7eb;
      --bg-soft: #f8fafc;
      --bg-pill: #eef2ff;
      --link: #2563eb;
    }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--fg); margin: 0; background: white; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 64px; }}
    .topnav {{ margin-bottom: 20px; }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .layout {{ display: grid; grid-template-columns: minmax(0, 780px) 300px; gap: 28px; align-items: start; }}
    .main {{ min-width: 0; }}
    .side {{ position: sticky; top: 24px; align-self: start; }}
    .card {{ border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin: 16px 0; background: white; }}
    .toc-card {{ background: var(--bg-soft); }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: var(--bg-pill); color: #3730a3; font-size: 12px; margin: 0 6px 6px 0; }}
    h1 {{ font-size: 2rem; line-height: 1.2; margin: 0 0 16px; }}
    h2 {{ font-size: 1.35rem; line-height: 1.3; margin-top: 30px; padding-top: 6px; border-top: 1px solid var(--border); }}
    h3 {{ font-size: 1.05rem; margin-top: 22px; }}
    p, li {{ line-height: 1.8; }}
    ul, ol {{ padding-left: 24px; }}
    code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 6px; }}
    .muted {{ color: var(--muted); }}
    .toc-list {{ list-style: none; padding-left: 0; margin: 12px 0 0; }}
    .toc-list li {{ margin: 8px 0; line-height: 1.5; }}
    .toc-h3 {{ padding-left: 14px; font-size: 0.95rem; }}
    @media (max-width: 980px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .side {{ position: static; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"topnav\"><a href=\"report.html\">← 返回 Deep Dives</a> · <a href=\"../../index.html\">站点首页</a></div>
    <div class=\"layout\">
      <main class=\"main\">
        <h1>{escape(d.title)}</h1>
        <div class=\"card\">
          {f'<span class="pill">{escape(d.time_text)}</span>' if d.time_text else ''}
          {f'<span class="pill">{escape(d.kind)}</span>' if d.kind else ''}
          {f'<span class="pill">{escape(d.tags)}</span>' if d.tags else ''}
          {f'<span class="pill">当前相关性：{escape(d.relevance)}</span>' if d.relevance else ''}
          <p class=\"muted\">源文件：<code>research/deep_dives/{escape(d.path.name)}</code></p>
        </div>
        {d.body_html}
      </main>
      <aside class=\"side\">
        <div class=\"card toc-card\">
          <strong>目录</strong>
          <p class=\"muted\">这是一篇长报告，建议按目录跳读。</p>
          {d.toc_html or '<p class="muted">暂无目录。</p>'}
        </div>
      </aside>
    </div>
  </div>
</body>
</html>
"""


def render_index_page(items: list[DeepDive]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = []
    for d in items:
        cards.append(
            f"""
  <div class=\"card\">
    <h2><a href=\"{escape(Path(d.rel_html).name)}\">{escape(d.title)}</a></h2>
    <div>
      {f'<span class="pill">{escape(d.time_text)}</span>' if d.time_text else ''}
      {f'<span class="pill">{escape(d.kind)}</span>' if d.kind else ''}
      {f'<span class="pill">{escape(d.tags)}</span>' if d.tags else ''}
      {f'<span class="pill">相关性：{escape(d.relevance)}</span>' if d.relevance else ''}
    </div>
    <p>{inline_md(d.summary)}</p>
    <p class=\"muted\">文件：<code>research/deep_dives/{escape(d.path.name)}</code></p>
    <p><a href=\"{escape(Path(d.rel_html).name)}\">阅读全文</a></p>
  </div>
""".rstrip()
        )
    card_html = "\n".join(cards) if cards else "<p class='muted'>暂无 deep dive 报告。</p>"
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Deep Dives</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 1040px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; margin: 0 6px 6px 0; }}
    code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 6px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <p><a href=\"../../index.html\">← 返回站点首页</a></p>
  <h1>Deep Dives</h1>
  <p class=\"muted\">长篇研究报告索引页。来源于 <code>research/deep_dives/*.md</code>，用于系统学习论文、仓库、结构型 alpha 与实现思路。相比短卡片，这里保留更多细节、上下文与落地建议。</p>
  <div class=\"card\">
    <p><strong>更新方式：</strong>新增 markdown 长报告后，运行 <code>python3 scripts/build_deep_dive_site.py</code>，再执行发布脚本即可同步到网站。</p>
    <p class=\"muted\">最近生成时间：{generated_at}</p>
  </div>
  {card_html}
</body>
</html>
"""


def ensure_main_index_link() -> None:
    if not MAIN_INDEX.exists():
        return
    text = MAIN_INDEX.read_text(encoding="utf-8")
    href = "reading/deep_dives/report.html"
    if href in text:
        return
    item = "<li><a href='reading/deep_dives/report.html'>Deep Dives</a></li>"
    if "</ul>" in text:
        text = text.replace("</ul>", f"{item}\n</ul>")
    else:
        text += f"\n<ul>{item}</ul>\n"
    MAIN_INDEX.write_text(text, encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = sorted([p for p in SRC_DIR.glob("*.md") if p.name not in {"INDEX.md", "README.md"}], reverse=True)
    items = [parse_deep_dive(p) for p in paths]

    for item in items:
        (OUT_DIR / f"{item.slug}.html").write_text(render_deep_dive_page(item), encoding="utf-8")

    index_html = render_index_page(items)
    (OUT_DIR / "report.html").write_text(index_html, encoding="utf-8")
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    ensure_main_index_link()

    print("[ok] deep dive pages generated")
    print("[site]", OUT_DIR / "report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
