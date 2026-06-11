#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "research" / "quant_digests"
OUT_DIR = ROOT / "reports" / "site" / "reading" / "quant_digests"
MAIN_INDEX = ROOT / "reports" / "site" / "index.html"

URL_RE = re.compile(r"(https?://[^\s<]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
ORDERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")
META_RE = re.compile(r"^-\s*([^：:]+)[：:]\s*(.*)$")


@dataclass
class Digest:
    path: Path
    slug: str
    title: str
    rel_html: str
    time_text: str
    updated_at: datetime
    updated_text: str
    kind: str
    tags: str
    evidence: str
    summary: str
    body_html: str


def inline_md(text: str) -> str:
    text = escape(text)
    text = CODE_RE.sub(r"<code>\1</code>", text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = URL_RE.sub(r'<a href="\1">\1</a>', text)
    return text


def markdown_to_html(lines: list[str]) -> str:
    chunks: list[str] = []
    para: list[str] = []
    list_mode: str | None = None

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
            chunks.append(f"<h3>{inline_md(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            flush_para()
            close_list()
            chunks.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            flush_para()
            close_list()
            chunks.append(f"<h1>{inline_md(stripped[2:])}</h1>")
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
    return "\n".join(chunks)


def format_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def render_pills(items: Iterable[tuple[str, str]]) -> str:
    return "\n      ".join(
        f'<span class="pill">{escape(label)}：{escape(value)}</span>'
        for label, value in items
        if value
    )


def parse_digest(path: Path) -> Digest:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    title = path.stem
    time_text = ""
    kind = ""
    tags = ""
    evidence = ""
    summary = ""
    stat = path.stat()
    updated_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    updated_text = format_utc(stat.st_mtime)

    for idx, line in enumerate(lines):
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
        elif key == "证据类型":
            evidence = value

    for idx, line in enumerate(lines):
        if line.strip() == "## 1. 这次看了什么":
            for nxt in lines[idx + 1 :]:
                if nxt.strip():
                    summary = nxt.strip()
                    break
            break
    if not summary:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
                summary = stripped
                break

    rel_html = f"reading/quant_digests/{path.stem}.html"
    body_html = markdown_to_html(lines[1:])
    return Digest(
        path=path,
        slug=path.stem,
        title=title,
        rel_html=rel_html,
        time_text=time_text,
        updated_at=updated_at,
        updated_text=updated_text,
        kind=kind,
        tags=tags,
        evidence=evidence,
        summary=summary,
        body_html=body_html,
    )


def render_digest_page(d: Digest) -> str:
    detail_pills = render_pills(
        [
            ("更新时间", d.updated_text),
            ("研究时间", d.time_text if d.time_text != d.updated_text else ""),
            ("类型", d.kind),
            ("主题标签", d.tags),
            ("证据类型", d.evidence),
        ]
    )
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(d.title)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; max-width: 960px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; margin: 0 6px 6px 0; }}
    ul, ol {{ padding-left: 22px; }}
    code {{ background: #f3f4f6; padding: 1px 5px; border-radius: 6px; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <p><a href=\"report.html\">← 返回 Quant Digests</a> · <a href=\"../../index.html\">站点首页</a></p>
  <h1>{escape(d.title)}</h1>
  <div class=\"card\">
    {detail_pills}
    <p class=\"muted\">源文件：<code>research/quant_digests/{escape(d.path.name)}</code></p>
  </div>
  {d.body_html}
</body>
</html>
"""


def render_index_page(digests: list[Digest]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards = []
    for d in digests:
        card_pills = render_pills(
            [
                ("更新时间", d.updated_text),
                ("研究时间", d.time_text if d.time_text != d.updated_text else ""),
                ("类型", d.kind),
                ("主题标签", d.tags),
            ]
        )
        cards.append(
            f"""
  <div class=\"card\">
    <h2><a href=\"{escape(Path(d.rel_html).name)}\">{escape(d.title)}</a></h2>
    <div>
      {card_pills}
    </div>
    <p>{inline_md(d.summary)}</p>
    <p class=\"muted\">文件：<code>research/quant_digests/{escape(d.path.name)}</code></p>
    <p><a href=\"{escape(Path(d.rel_html).name)}\">查看全文</a></p>
  </div>
""".rstrip()
        )
    card_html = "\n".join(cards) if cards else "<p class='muted'>暂无研究笔记。</p>"
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Quant Digests</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; max-width: 960px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111; }}
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
  <h1>Quant Digests</h1>
  <p class=\"muted\">自动研究笔记索引页。来源于 <code>research/quant_digests/*.md</code>，用于沉淀论文卡 / 仓库拆解 / 小知识点卡，并服务于 5m / 15m Crypto 策略研发。</p>
  <div class=\"card\">
    <p><strong>更新方式：</strong>新增 markdown 笔记后，运行 <code>python3 scripts/build_quant_digest_site.py</code>，再执行发布脚本即可同步到网站。</p>
    <p><strong>当前排序：</strong>按研究笔记源文件更新时间倒序（最新更新优先）。</p>
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
    href = "reading/quant_digests/report.html"
    if href in text:
        return
    item = "<li><a href='reading/quant_digests/report.html'>Quant Digests</a></li>"
    if "</ul>" in text:
        text = text.replace("</ul>", f"{item}\n</ul>")
    else:
        text += f"\n<ul>{item}</ul>\n"
    MAIN_INDEX.write_text(text, encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    digest_paths = [p for p in SRC_DIR.glob("*.md") if p.name not in {"INDEX.md", "README.md"}]
    digests = sorted((parse_digest(p) for p in digest_paths), key=lambda d: d.updated_at, reverse=True)

    for digest in digests:
        html = render_digest_page(digest)
        (OUT_DIR / f"{digest.slug}.html").write_text(html, encoding="utf-8")

    index_html = render_index_page(digests)
    (OUT_DIR / "report.html").write_text(index_html, encoding="utf-8")
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    ensure_main_index_link()

    print("[ok] quant digest pages generated")
    print("[site]", OUT_DIR / "report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
