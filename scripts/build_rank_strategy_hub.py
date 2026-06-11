#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_FACTORS = ROOT / "reports" / "site" / "factors"
ARTIFACTS = ROOT / "reports" / "artifacts"
RESEARCH = ROOT / "research"
OUT_DIR = SITE_FACTORS / "rank_strategy_hub"
OUT_PATH = OUT_DIR / "report.html"

BJ_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")

RANK_PAT = re.compile(r"^(rank\d+|paper_rank\d+|scout_rank\d+)", re.IGNORECASE)


@dataclass
class SiteRow:
    name: str
    rel_report: str
    html_count: int
    updated_text: str


def format_bj(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M 北京时间")


def collect_site_rows() -> list[SiteRow]:
    rows: list[SiteRow] = []
    for d in sorted(SITE_FACTORS.iterdir()):
        if not d.is_dir() or not RANK_PAT.match(d.name):
            continue
        report = d / "report.html"
        if not report.exists():
            continue
        html_count = sum(1 for p in d.rglob("*.html"))
        rel_report = report.relative_to(ROOT / "reports" / "site").as_posix()
        rows.append(
            SiteRow(
                name=d.name,
                rel_report=rel_report,
                html_count=html_count,
                updated_text=format_bj(report.stat().st_mtime),
            )
        )
    return rows


def collect_artifact_rank_dirs() -> list[str]:
    out: list[str] = []
    for d in sorted(ARTIFACTS.iterdir()):
        if d.is_dir() and RANK_PAT.match(d.name):
            out.append(d.name)
    return out


def read_rank_research_hits(limit: int = 60) -> list[str]:
    hits: list[tuple[float, str]] = []
    for base in [RESEARCH / "optimization_loop", RESEARCH / "strategy_review"]:
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            name = p.name.lower()
            if "rank" not in name:
                continue
            hits.append((p.stat().st_mtime, p.relative_to(ROOT / "research").as_posix()))
    hits.sort(key=lambda x: x[0], reverse=True)
    return [h[1] for h in hits[:limit]]


def render_rows(rows: list[SiteRow]) -> str:
    if not rows:
        return "<tr><td colspan='4'>暂无</td></tr>"
    parts: list[str] = []
    for r in rows:
        parts.append(
            "<tr>"
            f"<td><code>{escape(r.name)}</code></td>"
            f"<td><a href='../../{escape(r.rel_report)}'>{escape(r.rel_report)}</a></td>"
            f"<td>{r.html_count}</td>"
            f"<td>{escape(r.updated_text)}</td>"
            "</tr>"
        )
    return "\n".join(parts)


def render_list(items: list[str], base_prefix: str = "") -> str:
    if not items:
        return "<li>暂无</li>"
    out: list[str] = []
    for it in items:
        if base_prefix:
            out.append(f"<li><a href='{escape(base_prefix + it)}'><code>{escape(it)}</code></a></li>")
        else:
            out.append(f"<li><code>{escape(it)}</code></li>")
    return "\n".join(out)


def main() -> int:
    site_rows = collect_site_rows()
    artifact_dirs = collect_artifact_rank_dirs()
    site_names = {r.name for r in site_rows}
    not_published = [n for n in artifact_dirs if n not in site_names]

    core_rows = [r for r in site_rows if r.name.startswith("rank") and not r.name.startswith("rank32")]
    rank32_rows = [r for r in site_rows if r.name.startswith("rank32") or r.name.startswith("scout_rank32")]
    paper_rows = [r for r in site_rows if r.name.startswith("paper_rank")]
    scout_rows = [r for r in site_rows if r.name.startswith("scout_rank") and not r.name.startswith("scout_rank32")]

    research_hits = read_rank_research_hits(limit=80)

    generated_at = datetime.now(timezone.utc).astimezone(BJ_TZ).strftime("%Y-%m-%d %H:%M 北京时间")

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank 策略总入口（发布盘点）</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 32px auto; padding: 0 16px; line-height: 1.6; color: #0f172a; background: #f8fafc; }}
    .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px 18px; margin-bottom: 14px; }}
    .muted {{ color: #64748b; }}
    h1,h2 {{ margin: 0 0 8px; }}
    table {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    th,td {{ border-bottom: 1px solid #e2e8f0; padding: 8px 10px; text-align:left; vertical-align: top; }}
    th {{ background: #f8fafc; }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    code {{ background: #f1f5f9; border-radius: 6px; padding: 2px 6px; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>Rank 策略总入口（发布盘点）</h1>
    <p class=\"muted\">用途：回答“哪些 Rank 已经在网站可点开，哪些还只有 artifacts / 研究笔记”。生成时间：{escape(generated_at)}</p>
    <p><b>站点主入口：</b><a href=\"../../index.html\">../../index.html</a> ｜ <b>本页：</b><code>factors/rank_strategy_hub/report.html</code> ｜ <b>P3+P2 全量总表：</b><a href=\"../rank_registry_p3_p2/report.html\">../rank_registry_p3_p2/report.html</a></p>
    <ul>
      <li>rank artifacts 目录数：<b>{len(artifact_dirs)}</b></li>
      <li>已发布为 factors 页面：<b>{len(site_rows)}</b></li>
      <li>尚未发布为 factors 页面：<b>{len(not_published)}</b></li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>32b 主链路</h2>
    <table>
      <thead><tr><th>目录</th><th>页面入口</th><th>html 数</th><th>更新时间</th></tr></thead>
      <tbody>{render_rows(rank32_rows)}</tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>Paper Rank（已发布）</h2>
    <table>
      <thead><tr><th>目录</th><th>页面入口</th><th>html 数</th><th>更新时间</th></tr></thead>
      <tbody>{render_rows(paper_rows)}</tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>Scout Rank（已发布，非 32b）</h2>
    <table>
      <thead><tr><th>目录</th><th>页面入口</th><th>html 数</th><th>更新时间</th></tr></thead>
      <tbody>{render_rows(scout_rows)}</tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>Core / Live Rank（已发布）</h2>
    <table>
      <thead><tr><th>目录</th><th>页面入口</th><th>html 数</th><th>更新时间</th></tr></thead>
      <tbody>{render_rows(core_rows)}</tbody>
    </table>
  </div>

  <div class=\"card\">
    <h2>Artifacts 已有但尚未发布到 factors 的 Rank 目录</h2>
    <p class=\"muted\">这些目录存在于 <code>reports/artifacts</code>，但还没有同名 <code>reports/site/factors/*/report.html</code> 入口。</p>
    <div class=\"grid\">
      <ul>{render_list(not_published[:120])}</ul>
      <ul>{render_list(not_published[120:240])}</ul>
    </div>
  </div>

  <div class=\"card\">
    <h2>研究笔记里的 Rank 记录（最近）</h2>
    <p class=\"muted\">来源：<code>research/optimization_loop</code> 与 <code>research/strategy_review</code>，这里只做索引，不代表都已发布为 factors 页面。</p>
    <ul>{render_list(research_hits, base_prefix='../../reading/deep_dives/../') if False else render_list(research_hits)}</ul>
  </div>
</body>
</html>
"""

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(html, encoding="utf-8")
    print({
        "out": str(OUT_PATH),
        "artifact_rank_dirs": len(artifact_dirs),
        "published_rank_factor_dirs": len(site_rows),
        "not_published_rank_dirs": len(not_published),
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
