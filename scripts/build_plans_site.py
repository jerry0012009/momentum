#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "site" / "plans"
MAIN_INDEX = ROOT / "reports" / "site" / "index.html"

URL_RE = re.compile(r"(https?://[^\s<]+)")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
CODE_RE = re.compile(r"`([^`]+)`")
ORDERED_RE = re.compile(r"^(\d+)\.\s+(.*)$")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass
class PlanDoc:
    source: Path
    slug: str
    title: str
    subtitle: str
    rel_html: str


@dataclass
class ControlDoc:
    source: Path
    title: str
    subtitle: str
    purpose: str
    cadence: str
    anchor: str
    mode: str = "markdown"
    excerpt_only: bool = False
    open_by_default: bool = False


@dataclass
class RecentNote:
    path: Path
    label: str
    title: str
    preview: str
    updated_text: str
    body_html: str
    anchor: str


PLANS = [
    PlanDoc(
        source=ROOT / "docs" / "TODO.md",
        slug="momentum_todo",
        title="Momentum Desk / TODO / Control Tower",
        subtitle="把 command board、bot2/bot3 prompt、scout brief 与最近运行痕迹放到同一页，方便从头到尾通读和跟进。",
        rel_html="plans/momentum_todo.html",
    ),
    PlanDoc(
        source=ROOT / "docs" / "RESEARCH_TRENDLINE_EVENT.md",
        slug="trendline_event_research",
        title="Trendline Event Research Plan",
        subtitle="定义 trendline event foundation：事件分层、confirmation ladder、slope buckets 与 go/no-go 标准。",
        rel_html="plans/trendline_event_research.html",
    ),
    PlanDoc(
        source=ROOT / "docs" / "CROSS_ENGINE_MAPPING.md",
        slug="cross_engine_mapping",
        title="Cross-Engine Mapping",
        subtitle="梳理 PyIndicators / PyTrendline 两套定义方式如何映射到统一的 Structure-Event Mainline。",
        rel_html="plans/cross_engine_mapping.html",
    ),
    PlanDoc(
        source=ROOT / "docs" / "TRENDLINE_CONFIRMATION_PROTOCOL.md",
        slug="trendline_confirmation_protocol",
        title="Trendline Confirmation Protocol",
        subtitle="把 confirmation ladder 提升为跨引擎可复用的 Mainline 协议，而不再只是单一 source 的局部实现。",
        rel_html="plans/trendline_confirmation_protocol.html",
    ),
]


TODO_CONTROL_DOCS = [
    ControlDoc(
        source=ROOT / "docs" / "TODO.md",
        title="项目板 / TODO",
        subtitle="先看这个：它是给人看的项目板；bot 运行规则已经收敛到 fixed policy + runtime state。",
        purpose="你如果只想先看当前项目目标、状态和导航，这一页就是最短入口。",
        cadence="随 TODO 顶部更新而变。",
        anchor="doc-command-board",
        mode="markdown",
        excerpt_only=True,
        open_by_default=True,
    ),
    ControlDoc(
        source=ROOT / "docs" / "BOT2_BOT3_POLICY.md",
        title="bot2/bot3 fixed policy",
        subtitle="当前唯一固定规则源：目标、槽位、禁止事项、follow-up 上限，都在这里。",
        purpose="如果你想知道系统为什么不该回头纠缠旧策略，先看这份 fixed policy。",
        cadence="仅在人工明确调整目标时变更。",
        anchor="doc-bot-policy",
        mode="markdown",
    ),
    ControlDoc(
        source=ROOT / "docs" / "BOT2_STRATEGY_REVIEW_CRON_PROMPT.txt",
        title="bot2 cron prompt",
        subtitle="bot2 定时任务实际拿到的执行提示词。",
        purpose="如果你想知道 bot2 每一轮被要求先做什么、必须回答什么、怎么对外汇报，看这个最直接。",
        cadence="默认 40 分钟一次。",
        anchor="doc-bot2-prompt",
        mode="raw",
    ),
    ControlDoc(
        source=ROOT / "docs" / "BOT2_BOT3_STATE.md",
        title="bot2/bot3 runtime state",
        subtitle="当前运行状态：launch queue / fresh intake / survivor / active P2 / cycle_plan。",
        purpose="如果你想知道现在系统正在推什么、当前轮拆成了哪几个小点，看这份 runtime state。",
        cadence="每轮运行后都可能变动。",
        anchor="doc-bot-state",
        mode="markdown",
    ),
    ControlDoc(
        source=ROOT / "docs" / "AUTO_OPTIMIZATION_CRON_PROMPT.txt",
        title="bot3 cron prompt",
        subtitle="bot3 定时执行轮次实际拿到的 prompt。",
        purpose="如果你想核对 bot3 被强制遵循的执行顺序、日志要求、邮件要求、网页落点要求，看这个最直接。",
        cadence="默认 13 分钟一次。",
        anchor="doc-bot3-prompt",
        mode="raw",
    ),
    ControlDoc(
        source=ROOT / "docs" / "RESEARCH_AUTOMATION_BRIEF.md",
        title="Scout / Research automation brief",
        subtitle="给研究型定时任务的规范：它应该怎样服务 Scout Seat，而不是反客为主。",
        purpose="看外部论文 / GitHub / digest 这条线何时该出手、何时该让位给 Paper / Live Seat。",
        cadence="研究任务按需运行，默认服务 Scout Seat。",
        anchor="doc-scout-brief",
        mode="markdown",
    ),
]


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
            css = ""
            body = stripped[2:]
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


def render_markdown_text(text: str) -> tuple[str, str]:
    return markdown_to_html(text.splitlines())


def format_ts(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def extract_todo_command_board(md_text: str) -> str:
    lines = md_text.splitlines()
    stop_heading = "## 配套规划文档 / Site mirrors"
    for idx, line in enumerate(lines):
        if line.strip() == stop_heading:
            return "\n".join(lines[:idx]).strip() + "\n"
    return md_text


def clean_preview(md_text: str, limit: int = 220) -> str:
    text = MD_LINK_RE.sub(r"\1", md_text)
    text = re.sub(r"^#.+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^- \[(?:x| )\]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^-\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def detect_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def load_recent_notes(rel_dir: str, label: str, limit: int = 4) -> list[RecentNote]:
    note_dir = ROOT / rel_dir
    if not note_dir.exists():
        return []
    paths = sorted(note_dir.glob("*.md"), key=lambda path: path.stat().st_mtime, reverse=True)[:limit]
    notes: list[RecentNote] = []
    for idx, path in enumerate(paths, 1):
        text = safe_read_text(path)
        body_html, _ = render_markdown_text(text)
        notes.append(
            RecentNote(
                path=path,
                label=label,
                title=detect_title(text, path.stem),
                preview=clean_preview(text),
                updated_text=format_ts(path),
                body_html=body_html,
                anchor=f"{slugify(label)}-{idx}",
            )
        )
    return notes


def render_control_doc(doc: ControlDoc, todo_text: str) -> str:
    raw_text = todo_text if doc.source == ROOT / "docs" / "TODO.md" else safe_read_text(doc.source)
    if doc.excerpt_only:
        raw_text = extract_todo_command_board(raw_text)
    if doc.mode == "raw":
        content_html = f'<pre class="doc-raw">{escape(raw_text.strip())}</pre>'
    else:
        content_html, _ = render_markdown_text(raw_text)
        content_html = f'<div class="content">{content_html}</div>'
    open_attr = " open" if doc.open_by_default else ""
    source_rel = doc.source.relative_to(ROOT).as_posix()
    return f'''
    <details class="doc-details" id="{escape(doc.anchor)}"{open_attr}>
      <summary>
        <div>
          <strong>{escape(doc.title)}</strong>
          <span class="muted">{escape(doc.subtitle)}</span>
        </div>
      </summary>
      <div class="doc-meta">
        <span class="mini-pill">Source: {escape(source_rel)}</span>
        <span class="mini-pill">Updated: {escape(format_ts(doc.source))}</span>
        <span class="mini-pill">Cadence: {escape(doc.cadence)}</span>
      </div>
      <p class="muted"><strong>为什么看它：</strong>{escape(doc.purpose)}</p>
      {content_html}
    </details>
    '''


def render_recent_note_group(title: str, subtitle: str, notes: list[RecentNote]) -> str:
    if not notes:
        return f'''
        <section class="card">
          <h2 style="margin-top:0;">{escape(title)}</h2>
          <p class="muted">{escape(subtitle)}</p>
          <p class="muted">当前还没有可镜像的记录。</p>
        </section>
        '''
    items = []
    for note in notes:
        rel_path = note.path.relative_to(ROOT).as_posix()
        items.append(
            f'''
            <details class="note-details" id="{escape(note.anchor)}">
              <summary>
                <div>
                  <strong>{escape(note.title)}</strong>
                  <span class="muted">{escape(note.updated_text)}</span>
                </div>
              </summary>
              <div class="doc-meta">
                <span class="mini-pill">{escape(note.label)}</span>
                <span class="mini-pill">Source: {escape(rel_path)}</span>
              </div>
              <p class="muted">{escape(note.preview)}</p>
              <div class="content note-body">{note.body_html}</div>
            </details>
            '''
        )
    return f'''
    <section class="card">
      <h2 style="margin-top:0;">{escape(title)}</h2>
      <p class="muted">{escape(subtitle)}</p>
      {''.join(items)}
    </section>
    '''


LIVE_CRON_SCRIPT = '''<script>
(function () {
  const grid = document.getElementById('cron-live-grid');
  const fetchedAt = document.getElementById('cron-live-fetched-at');
  const CACHE_KEY = 'momentum-control-tower-public-cron-cache-v1';
  if (!grid || !fetchedAt) return;

  function esc(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function statusClass(enabled, status) {
    if (!enabled) return 'disabled';
    const s = String(status || '').toLowerCase();
    if (s === 'ok') return 'ok';
    if (s === 'error') return 'error';
    if (s === 'idle') return 'idle';
    return 'warn';
  }

  function renderJobs(jobs, opts) {
    opts = opts || {};
    const stale = Boolean(opts.stale);
    const staleNote = stale ? '<p class="muted"><strong>说明：</strong>当前展示的是最近一次成功抓取到的缓存快照；实时接口这次没连上。</p>' : '';
    if (!jobs || !jobs.length) {
      grid.innerHTML = '<div class="live-card"><h3>暂无 cron</h3><p class="muted">当前没有读取到任何定时任务。</p>' + staleNote + '</div>';
      return;
    }
    grid.innerHTML = staleNote + jobs.map(function (job) {
      const state = job.state || {};
      const schedule = job.schedule || {};
      const badgeClass = statusClass(job.enabled, state.lastRunStatus);
      const enabledText = job.enabled ? '已启用' : '已停用';
      const promptKind = job.promptKind ? (' · ' + job.promptKind) : '';
      const bot = job.botName ? (' · ' + job.botName) : '';
      const errorLine = state.lastError ? ('<p><strong>最近错误：</strong>' + esc(state.lastError) + '</p>') : '';
      return '' +
        '<div class="live-card">' +
          '<div class="live-meta">' +
            '<span class="live-badge ' + badgeClass + '">' + esc(enabledText) + '</span>' +
            '<span class="mini-pill">' + esc(schedule.summary || '-') + '</span>' +
            '<span class="mini-pill">' + esc((job.name || job.id || 'cron') + promptKind + bot) + '</span>' +
          '</div>' +
          '<h3>' + esc(job.name || job.id || 'unnamed cron') + '</h3>' +
          '<p><strong>ID：</strong><span class="mono">' + esc(job.id || '-') + '</span></p>' +
          '<p><strong>下次运行：</strong>' + esc(state.nextRunText || '-') + '</p>' +
          '<p><strong>上次运行：</strong>' + esc(state.lastRunText || '-') + '</p>' +
          '<p><strong>上次状态：</strong>' + esc(state.lastRunStatus || '-') + '；<strong>连续错误：</strong>' + esc(state.consecutiveErrors || 0) + '</p>' +
          errorLine +
        '</div>';
    }).join('');
  }

  function readCache() {
    try {
      const raw = window.localStorage.getItem(CACHE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.jobs)) return null;
      return parsed;
    } catch (error) {
      return null;
    }
  }

  function writeCache(data) {
    try {
      window.localStorage.setItem(CACHE_KEY, JSON.stringify(data));
    } catch (error) {
      // ignore quota / privacy errors
    }
  }

  function renderError(message) {
    const cached = readCache();
    if (cached) {
      renderJobs(cached.jobs || [], { stale: true });
      fetchedAt.textContent = '实时读取失败，已回退到缓存：' + new Date(cached.fetchedAt || Date.now()).toLocaleString();
      return;
    }
    grid.innerHTML = '<div class="live-card"><h3>实时状态读取失败</h3><p class="muted">' + esc(message) + '</p><p class="muted">这不影响下面的文档镜像阅读，但意味着当前没拿到实时 cron 摘要。</p></div>';
  }

  async function fetchJsonWithTimeout(url, timeoutMs) {
    const controller = new AbortController();
    const timer = window.setTimeout(function () {
      controller.abort();
    }, timeoutMs || 8000);
    try {
      const res = await fetch(url, { cache: 'no-store', signal: controller.signal });
      if (!res.ok) throw new Error('HTTP ' + res.status + ' @ ' + url);
      return await res.json();
    } finally {
      window.clearTimeout(timer);
    }
  }

  async function loadCronJobs() {
    fetchedAt.textContent = '正在刷新…';
    const urls = [
      '/bots/api/public-cron-jobs?ts=' + Date.now(),
      window.location.origin + '/bots/api/public-cron-jobs?ts=' + Date.now(),
      'https://jp.jerrypsy.top/bots/api/public-cron-jobs?ts=' + Date.now()
    ];
    const tried = [];
    for (const url of urls) {
      try {
        const data = await fetchJsonWithTimeout(url, 8000);
        renderJobs(data.jobs || [], { stale: false });
        writeCache({ jobs: data.jobs || [], fetchedAt: data.fetchedAt || Date.now(), source: url });
        fetchedAt.textContent = 'Live fetched: ' + new Date(data.fetchedAt || Date.now()).toLocaleString();
        return;
      } catch (error) {
        tried.push((error && error.message) ? error.message : String(error));
      }
    }
    fetchedAt.textContent = '读取失败';
    renderError(tried.join(' | ') || 'Failed to fetch');
  }

  loadCronJobs();
  window.setInterval(loadCronJobs, 60000);
})();
</script>'''


BASE_CSS = """
    :root {
      --fg: #111827;
      --muted: #6b7280;
      --border: #e5e7eb;
      --bg-soft: #f8fafc;
      --bg-pill: #eef2ff;
      --bg-done: #ecfdf5;
      --bg-todo: #fff7ed;
      --link: #2563eb;
      --bg-card: #ffffff;
      --bg-highlight: #f5f7ff;
    }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: var(--fg); margin: 0; background: white; }
    .wrap { max-width: 1280px; margin: 0 auto; padding: 32px 20px 64px; }
    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .hero { border: 1px solid var(--border); border-radius: 16px; padding: 22px 24px; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); margin-bottom: 20px; }
    .hero h1 { margin: 0 0 8px; font-size: 34px; }
    .muted { color: var(--muted); }
    .layout { display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 22px; align-items: start; }
    .card { border: 1px solid var(--border); border-radius: 14px; background: var(--bg-card); padding: 18px 20px; }
    .toc { position: sticky; top: 16px; }
    .toc h2 { margin-top: 0; font-size: 18px; }
    .toc-list { list-style: none; padding: 0; margin: 0; }
    .toc-list li { margin: 8px 0; line-height: 1.35; }
    .toc-h3 { padding-left: 12px; font-size: 14px; }
    .content h1:first-child { display: none; }
    .content h2 { margin-top: 28px; padding-top: 8px; border-top: 1px solid var(--border); font-size: 28px; }
    .content h3 { margin-top: 22px; font-size: 21px; }
    .content p { line-height: 1.7; }
    .content ul, .content ol { padding-left: 22px; line-height: 1.7; }
    .content li.done { background: var(--bg-done); }
    .content li.todo { background: var(--bg-todo); }
    .content li { padding: 3px 6px; border-radius: 8px; margin: 3px 0; }
    .content code, code { background: var(--bg-soft); border: 1px solid var(--border); border-radius: 6px; padding: 1px 6px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.95em; }
    blockquote { margin: 14px 0; padding: 10px 14px; border-left: 4px solid #93c5fd; background: #eff6ff; border-radius: 8px; }
    hr { border: none; border-top: 1px solid var(--border); margin: 22px 0; }
    .pills { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 12px; }
    .pill { background: var(--bg-pill); color: #3730a3; border-radius: 999px; padding: 6px 12px; font-size: 13px; }
    .list { display: grid; gap: 16px; }
    .plan-link { display: block; border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; background: white; }
    .plan-link h2 { margin: 0 0 6px; font-size: 24px; }
    .entry-board { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-bottom: 20px; }
    .entry-link { display: block; border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; background: white; }
    .entry-link h2 { margin: 8px 0 6px; font-size: 20px; }
    .entry-pill { display:inline-block; font-size:12px; padding:4px 8px; border-radius:999px; background: var(--bg-pill); color:#3730a3; }
    .stack { display: grid; gap: 22px; }
    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
    .summary-card { display: block; border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; background: var(--bg-highlight); color: inherit; }
    .summary-card h3 { margin: 10px 0 8px; font-size: 18px; }
    .summary-card p { margin: 0; line-height: 1.6; }
    .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
    .status-card { border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; background: white; }
    .status-label { font-size: 12px; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
    .status-value { font-size: 18px; margin-top: 8px; font-weight: 700; }
    .live-meta { display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }
    .live-grid { display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-top: 14px; }
    .live-card { border:1px solid var(--border); border-radius:14px; padding:16px 18px; background:white; }
    .live-card h3 { margin: 0 0 8px; font-size: 18px; }
    .live-card p { margin: 6px 0; line-height: 1.6; }
    .live-card .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    .live-badge { display:inline-block; padding:4px 8px; border-radius:999px; font-size:12px; font-weight:700; }
    .live-badge.ok { background:#ecfdf5; color:#166534; }
    .live-badge.warn { background:#fff7ed; color:#9a3412; }
    .live-badge.error { background:#fef2f2; color:#b91c1c; }
    .live-badge.idle { background:#f3f4f6; color:#374151; }
    .live-badge.disabled { background:#e5e7eb; color:#4b5563; }
    .mini-pill { display: inline-block; margin: 0 8px 8px 0; background: #f3f4f6; color: #374151; border-radius: 999px; padding: 5px 10px; font-size: 12px; }
    .doc-details, .note-details { border: 1px solid var(--border); border-radius: 14px; padding: 0; background: white; margin-top: 14px; overflow: hidden; }
    .doc-details summary, .note-details summary { cursor: pointer; list-style: none; padding: 16px 18px; background: #fafafa; }
    .doc-details summary::-webkit-details-marker, .note-details summary::-webkit-details-marker { display: none; }
    .doc-details[open] summary, .note-details[open] summary { border-bottom: 1px solid var(--border); }
    .doc-details > :not(summary), .note-details > :not(summary) { padding: 16px 18px 18px; }
    .doc-meta { margin-bottom: 8px; }
    .doc-raw { margin: 0; white-space: pre-wrap; word-break: break-word; line-height: 1.65; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; background: #0f172a; color: #e2e8f0; border-radius: 12px; padding: 16px; overflow: auto; }
    .sub-layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 18px; align-items: start; }
    .subcard { border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; background: #fbfdff; }
    .subcard h3 { margin-top: 0; font-size: 16px; }
    .note-body h1:first-child { display: block; }
    .note-body h1 { font-size: 24px; margin-top: 0; }
    .note-body h2 { font-size: 20px; }
    @media (max-width: 960px) {
      .layout { grid-template-columns: 1fr; }
      .toc { position: static; }
      .sub-layout { grid-template-columns: 1fr; }
    }
"""


def render_plan_page(plan: PlanDoc) -> str:
    if plan.slug == "momentum_todo":
        return render_todo_page(plan)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md_text = safe_read_text(plan.source)
    body_html, toc_html = markdown_to_html(md_text.splitlines())
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(plan.title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="wrap">
    <p><a href="report.html">← 返回 Plans / Roadmaps</a> · <a href="../index.html">站点首页</a></p>
    <div class="hero">
      <h1>{escape(plan.title)}</h1>
      <p class="muted">{escape(plan.subtitle)}</p>
      <div class="pills">
        <span class="pill">Generated: {escape(generated_at)}</span>
        <span class="pill">Source: {escape(plan.source.relative_to(ROOT).as_posix())}</span>
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


def render_todo_page(plan: PlanDoc) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    todo_text = safe_read_text(plan.source)
    command_board_text = extract_todo_command_board(todo_text)
    command_board_html, _ = render_markdown_text(command_board_text)
    full_todo_html, full_todo_toc = render_markdown_text(todo_text)

    bot2_notes = load_recent_notes("research/strategy_review", "bot2 / strategy_review", limit=4)
    bot3_notes = load_recent_notes("research/optimization_loop", "bot3 / optimization_loop", limit=4)

    latest_bot2 = bot2_notes[0].updated_text if bot2_notes else "暂无记录"
    latest_bot3 = bot3_notes[0].updated_text if bot3_notes else "暂无记录"

    summary_cards = []
    for doc in TODO_CONTROL_DOCS:
        summary_cards.append(
            f"<a class='summary-card' href='#{escape(doc.anchor)}'><span class='entry-pill'>{escape(doc.cadence)}</span><h3>{escape(doc.title)}</h3><p>{escape(doc.subtitle)}</p></a>"
        )

    control_docs_html = "".join(render_control_doc(doc, todo_text) for doc in TODO_CONTROL_DOCS)

    page_toc = '''
    <ul class="toc-list">
      <li><a href="#overview">怎么读这页</a></li>
      <li><a href="#live-cron">实时 cron / run 状态</a></li>
      <li><a href="#live-status">站点镜像状态</a></li>
      <li><a href="#control-docs">Prompt / Brief / Control Docs</a></li>
      <li class="toc-h3"><a href="#doc-command-board">项目板 / TODO</a></li>
      <li class="toc-h3"><a href="#doc-bot2-brief">bot2 统揽 brief</a></li>
      <li class="toc-h3"><a href="#doc-bot2-prompt">bot2 cron prompt</a></li>
      <li class="toc-h3"><a href="#doc-bot3-brief">bot3 auto loop brief</a></li>
      <li class="toc-h3"><a href="#doc-bot3-prompt">bot3 cron prompt</a></li>
      <li class="toc-h3"><a href="#doc-scout-brief">Scout / Research brief</a></li>
      <li><a href="#full-todo">TODO 全文 / 原始路线图</a></li>
    </ul>
    '''

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(plan.title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="wrap">
    <p><a href="report.html">← 返回 Plans / Roadmaps</a> · <a href="../index.html">站点首页</a></p>
    <div class="hero">
      <h1>{escape(plan.title)}</h1>
      <p class="muted">这一页不再只放一个瘦身 TODO，而是把当前 command board、bot2/bot3 的 prompt / brief、以及最近运行痕迹放到同一屏，方便你从头到尾通读并随时核对现在到底怎么跑。</p>
      <div class="pills">
        <span class="pill">Generated: {escape(generated_at)}</span>
        <span class="pill">Authoritative board: docs/TODO.md 顶部</span>
        <span class="pill">Last bot2 review: {escape(latest_bot2)}</span>
        <span class="pill">Last bot3 run: {escape(latest_bot3)}</span>
      </div>
    </div>
    <div class="layout">
      <aside class="card toc">
        <h2>页内导航</h2>
        {page_toc}
      </aside>
      <main class="stack">
        <section class="card" id="overview">
          <h2 style="margin-top:0;">怎么读这页</h2>
          <p class="muted">如果你想快速搞清楚当前节奏，推荐顺序是：先看 <strong>项目板 / TODO</strong> → 再看 bot2 / bot3 的实际 prompt → 最后看最近 bot2 / bot3 留下的运行痕迹。这样能同时看到“项目现在在推什么”“系统被要求怎么执行”“最近实际上做了什么”。</p>
          <div class="summary-grid">{''.join(summary_cards)}</div>
        </section>

        <section class="card" id="live-cron">
          <h2 style="margin-top:0;">实时 cron / run 状态</h2>
          <p class="muted">这一块不是 build 时写死的，而是页面打开后直接去拉 <code>/bots/api/public-cron-jobs</code> 的只读摘要，所以你不用等 TODO 页重新发布，也能看到当前 cron 的启停、下次运行、上次运行和报错情况。</p>
          <div class="live-meta">
            <span class="mini-pill">Data source: /bots/api/public-cron-jobs</span>
            <span class="mini-pill" id="cron-live-fetched-at">正在拉取…</span>
          </div>
          <div id="cron-live-grid" class="live-grid">
            <div class="live-card">
              <h3>加载中</h3>
              <p class="muted">正在读取当前 cron / run 状态…</p>
            </div>
          </div>
        </section>

        <section class="card" id="live-status">
          <h2 style="margin-top:0;">站点镜像状态</h2>
          <p class="muted">这里展示的是当前已发布到站点的镜像更新时间：command board、最近 bot2 review、最近 bot3 执行记录，以及本页自身的 build 时间。</p>
          <div class="status-grid">
            <div class="status-card">
              <div class="status-label">当前唯一命令板</div>
              <div class="status-value">docs/TODO.md 顶部</div>
              <p class="muted">Updated: {escape(format_ts(plan.source))}</p>
            </div>
            <div class="status-card">
              <div class="status-label">最新 bot2 统揽</div>
              <div class="status-value">{escape(latest_bot2)}</div>
              <p class="muted">来源：research/strategy_review/</p>
            </div>
            <div class="status-card">
              <div class="status-label">最新 bot3 执行</div>
              <div class="status-value">{escape(latest_bot3)}</div>
              <p class="muted">来源：research/optimization_loop/</p>
            </div>
            <div class="status-card">
              <div class="status-label">这个页面</div>
              <div class="status-value">{escape(generated_at)}</div>
              <p class="muted">重新 build / publish 后即可更新这一层镜像。</p>
            </div>
          </div>
        </section>

        {render_recent_note_group('最近 bot2 统揽记录', '看最近几轮 desk-level verdict / 排兵布阵 / TODO 调整。', bot2_notes)}
        {render_recent_note_group('最近 bot3 执行记录', '看最近几轮 bot3 实际认领了什么、留下了什么可审计痕迹。', bot3_notes)}

        <section class="card" id="control-docs">
          <h2 style="margin-top:0;">Prompt / Brief / Control Docs</h2>
          <p class="muted">下面这些是当前节奏真正起作用的控制文档。不是“解释性补充”，而是你想改系统行为时最该看的位置。</p>
          {control_docs_html}
        </section>

        <section class="card" id="full-todo">
          <h2 style="margin-top:0;">TODO 全文 / 原始路线图</h2>
          <p class="muted">如果你想把 backlog、历史背景、收口线、主线、归档线都从头到尾读一遍，这里保留 <code>docs/TODO.md</code> 的完整镜像。</p>
          <div class="sub-layout">
            <aside class="subcard toc">
              <h3>TODO 目录</h3>
              {full_todo_toc}
            </aside>
            <div class="subcard content">
              {full_todo_html}
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
  {LIVE_CRON_SCRIPT}
</body>
</html>'''


def render_plans_index(plans: list[PlanDoc]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    items = []
    for plan in plans:
        items.append(
            f"<a class='plan-link' href='{escape(Path(plan.rel_html).name)}'><h2>{escape(plan.title)}</h2><p class='muted'>{escape(plan.subtitle)}</p><p class='muted'>Source: {escape(plan.source.relative_to(ROOT).as_posix())}</p></a>"
        )

    current_entries = [
        ("../factors/alpha_closure_board/report.html", "Current Alpha Closure Board", "当前收口总入口", "先并排看三条收口线：谁该继续、谁该收口、下一步最值得补什么。"),
        ("../plans/momentum_todo.html", "Desk / TODO / Control Tower", "透明化控制台", "如果你想把 TODO、prompt、brief、最近 bot2/bot3 运行痕迹放到一页里看，先从这里进。"),
        ("../factors/structure_event_mainline/report.html", "主线总览 / Mainline", "默认入口", "先看整个项目有哪些 alpha 方向、哪些已收工、下一步从哪里接着推进。"),
        ("../factors/pytrendline_event_validation_v3_final_verdict/report.html", "PyTrendline v3 Final Verdict", "已收工研究线", "如果你只想快速知道 v3 最终留下了什么，这页就是最短答案。"),
        ("../factors/support_breakout_v0_h24/report.html", "support_breakout v0", "当前最接近策略原型", "这是目前最像可继续推进的 breakout-short 窄原型入口。"),
        ("../factors/support_breakout_v0_fib_ab/report.html", "Fib A/B honesty", "增强层诚实对照", "这页专门回答：fib 叠加是真的增强，还是只是看起来更高级。"),
        ("../factors/ema_psar_raw_alpha/report.html", "EMA / PSAR Raw Alpha", "独立 raw alpha 分支", "结构事件之外，当前另一条更朴素但同样值得继续的 alpha 方向。"),
    ]
    entry_html = "".join(
        f"<a class='entry-link' href='{escape(href)}'><span class='entry-pill'>{escape(tag)}</span><h2>{escape(title)}</h2><p class='muted'>{escape(desc)}</p></a>"
        for href, title, tag, desc in current_entries
    )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Plans / Roadmaps</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="wrap">
    <p><a href="../index.html">← 返回站点首页</a></p>
    <div class="hero">
      <h1>Plans / Roadmaps</h1>
      <p class="muted">这里不只放抽象规划文档，也告诉你当前项目最值得看的 alpha 方向入口，避免先掉进纯方法页或陈旧中间报告。</p>
      <div class="pills">
        <span class="pill">Generated: {escape(generated_at)}</span>
        <span class="pill">Scope: planning docs + current alpha entry board</span>
      </div>
    </div>
    <div class="card" style="margin-bottom:20px;">
      <h2 style="margin-top:0;">现在该从哪里进入？</h2>
      <p class="muted">如果你只想快速搞清楚“当前有哪些 alpha 方向、各自处在什么阶段、下一步去哪”，先看下面这组入口，再回头看详细 planning docs。</p>
      <div class="entry-board">{entry_html}</div>
    </div>
    <div class="list">{''.join(items)}</div>
  </div>
</body>
</html>'''


def ensure_main_index_links() -> None:
    if not MAIN_INDEX.exists():
        return
    html = safe_read_text(MAIN_INDEX)
    insertion = "<li><a href='plans/report.html'>Plans / Roadmaps</a></li>"
    if insertion not in html and "</ul>" in html:
        html = html.replace("</ul>", f"{insertion}\n</ul>", 1)
    MAIN_INDEX.write_text(html, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for plan in PLANS:
        out = OUT_DIR / Path(plan.rel_html).name
        out.write_text(render_plan_page(plan), encoding="utf-8")
    index_html = render_plans_index(PLANS)
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")
    (OUT_DIR / "report.html").write_text(index_html, encoding="utf-8")
    ensure_main_index_links()
    print(f"[ok] plans pages generated -> {OUT_DIR}")


if __name__ == "__main__":
    main()
