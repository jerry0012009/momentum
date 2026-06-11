#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

ROOT = Path('/root/clawd/jerry/momentum')
CSV_PATH = ROOT / 'reports' / 'artifacts' / 'rank_registry' / 'full_rank_p3_p2_table.csv'
STATE_PATH = ROOT / 'reports' / 'artifacts' / 'rank_registry' / 'p3_p2_report_batch_state.json'
SITE_FACTORS = ROOT / 'reports' / 'site' / 'factors'
OUT_DIR = SITE_FACTORS / 'rank_registry_p3_p2'
OUT_PATH = OUT_DIR / 'report.html'
ENTRY_ROOT = SITE_FACTORS / 'rank_registry_p3_p2_entries'
ARTIFACTS = ROOT / 'reports' / 'artifacts'

STAGE_ORDER = {'P3': 0, 'P2': 1}


def read_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f'csv not found: {CSV_PATH}')
    with CSV_PATH.open('r', encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: (STAGE_ORDER.get(r.get('stage', ''), 99), r.get('rank', '')))
    return rows


def read_batch_state() -> tuple[dict[str, str], Counter]:
    rank_status: dict[str, str] = {}
    counts: Counter = Counter()
    if not STATE_PATH.exists():
        return rank_status, counts
    try:
        obj = json.loads(STATE_PATH.read_text(encoding='utf-8'))
        tasks = obj.get('tasks', []) if isinstance(obj, dict) else []
        for t in tasks:
            rank = (t.get('rank') or '').strip()
            status = (t.get('status') or '').strip().lower()
            if not rank:
                continue
            rank_status[rank] = status or 'unknown'
            counts[status or 'unknown'] += 1
    except Exception:
        return {}, Counter()
    return rank_status, counts


def fmt_bj_utc(dt: datetime) -> str:
    bj = dt.astimezone(timezone(timedelta(hours=8)))
    return f"{bj.strftime('%Y-%m-%d %H:%M:%S')} 北京时间 / {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC"


def badge_class(status: str) -> str:
    s = (status or '').strip().lower()
    return {
        'keep': 'keep',
        'watch': 'watch',
        'bench': 'bench',
        'archive': 'archive',
    }.get(s, 'other')


def batch_badge_class(status: str) -> str:
    s = (status or '').strip().lower()
    return {
        'done': 'batch-done',
        'pending': 'batch-pending',
        'running': 'batch-running',
        'blocked': 'batch-blocked',
    }.get(s, 'batch-other')


def rank_token_pattern(rank: str) -> re.Pattern[str]:
    m = re.search(r'(\d+)', rank or '')
    if not m:
        return re.compile(r'^$')
    num = m.group(1)
    return re.compile(rf'(^|_)rank{num}(?:_|$)', re.IGNORECASE)


def find_factor_reports(rank: str) -> list[str]:
    pat = rank_token_pattern(rank)
    out: list[str] = []
    for d in sorted(SITE_FACTORS.iterdir()):
        if not d.is_dir():
            continue
        if not pat.search(d.name):
            continue
        report = d / 'report.html'
        if report.exists():
            out.append(report.relative_to(ROOT / 'reports' / 'site').as_posix())
    return out


def find_artifact_dirs(rank: str) -> list[str]:
    pat = rank_token_pattern(rank)
    out: list[str] = []
    for d in sorted(ARTIFACTS.iterdir()):
        if d.is_dir() and pat.search(d.name):
            out.append(d.name)
    return out


def write_rank_entry_page(row: dict[str, str], factor_reports: list[str], artifact_dirs: list[str], batch_status: str) -> str:
    rank = (row.get('rank') or '-').strip() or '-'
    out_dir = ENTRY_ROOT / rank
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'report.html'

    if factor_reports:
        report_items_list: list[str] = []
        for rel in factor_reports:
            rel_path = Path(rel)
            try:
                entry_href = '../../' + rel_path.relative_to('factors').as_posix()
            except Exception:
                entry_href = '../../' + rel_path.as_posix()
            report_items_list.append(
                f"<li><a href='{escape(entry_href)}'>{escape(rel)}</a></li>"
            )
        report_items = ''.join(report_items_list)
        publish_hint = f"已在 factors 下发布 {len(factor_reports)} 个报告入口。"
    else:
        report_items = '<li>暂无同 rank 的 report.html（需要补页面）</li>'
        publish_hint = '当前仅有 registry 条目，尚未发布独立 factors 报告页。'

    artifact_items = ''.join(f"<li><code>{escape(name)}</code></li>" for name in artifact_dirs) or '<li>暂无</li>'

    decomp_link = f"../../{rank}/decomposition.html"

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(rank)} · P3/P2 registry entry</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 980px; margin: 28px auto; padding: 0 16px; line-height: 1.65; color: #0f172a; background: #f8fafc; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }}
    .muted {{ color:#64748b; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
    .pill {{ display:inline-block; border-radius:999px; padding:3px 9px; font-size:12px; background:#e2e8f0; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>{escape(rank)} · P3/P2 registry entry</h1>
    <p class=\"muted\">来自 <code>full_rank_p3_p2_table.csv</code> 的单条落地页，用于确保该 rank 在 <code>factors/</code> 目录有可点击入口。</p>
    <p><a href='../../rank_registry_p3_p2/report.html'>← 返回 P3/P2 总表</a> ｜ <a href='../../../index.html'>站点首页</a></p>
  </div>

  <div class=\"card\">
    <p><b>stage：</b>{escape(row.get('stage', '-'))}</p>
    <p><b>status：</b><span class='pill'>{escape((row.get('status') or '-').strip() or '-')}</span></p>
    <p><b>batch 进度：</b><span class='pill'>{escape(batch_status or 'unknown')}</span></p>
    <p><b>mother theme：</b>{escape(row.get('mother_theme', '-'))}</p>
    <p><b>role：</b>{escape(row.get('role', '-'))}</p>
    <p><b>challenge baseline：</b>{escape(row.get('challenge_baseline', '-'))}</p>
    <p><b>unique increment：</b>{escape(row.get('unique_increment', '-'))}</p>
    <p><b>next action：</b>{escape(row.get('next_action', '-'))}</p>
  </div>

  <div class=\"card\">
    <h2>双页结构入口</h2>
    <ul>
      <li><a href='../../{escape(rank)}/report.html'>报告页 report.html</a></li>
      <li><a href='{escape(decomp_link)}'>拆解页 decomposition.html</a></li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>factor 报告入口（同 rank）</h2>
    <p class=\"muted\">{escape(publish_hint)}</p>
    <ul>{report_items}</ul>
  </div>

  <div class=\"card\">
    <h2>artifacts 目录（同 rank）</h2>
    <ul>{artifact_items}</ul>
  </div>
</body>
</html>
"""

    out_path.write_text(html, encoding='utf-8')
    return out_path.relative_to(ROOT / 'reports' / 'site').as_posix()


def render() -> str:
    rows = read_rows()
    now = datetime.now(timezone.utc)

    by_stage = Counter(row.get('stage', '-') for row in rows)
    by_status = Counter((row.get('status') or '').strip().lower() for row in rows)
    batch_status_map, batch_counts = read_batch_state()

    row_html = []
    published_count = 0
    dual_ready_count = 0

    for idx, row in enumerate(rows, 1):
        status = (row.get('status') or '').strip()
        rank = (row.get('rank') or '-').strip() or '-'
        factor_reports = find_factor_reports(rank)
        artifact_dirs = find_artifact_dirs(rank)
        batch_status = batch_status_map.get(rank, 'unknown')
        entry_rel = write_rank_entry_page(row, factor_reports, artifact_dirs, batch_status)

        report_exists = (SITE_FACTORS / rank / 'report.html').exists()
        decomp_exists = (SITE_FACTORS / rank / 'decomposition.html').exists()
        if report_exists and decomp_exists:
            dual_ready_count += 1
        if factor_reports:
            published_count += 1

        dual_badge = f"<span class='pill {'ok' if report_exists and decomp_exists else 'warn'}'>dual: {'ready' if report_exists and decomp_exists else 'partial'}</span>"
        batch_badge = f"<span class='pill {batch_badge_class(batch_status)}'>batch: {escape(batch_status)}</span>"
        factor_cell = (
            f"<a href='../{escape(entry_rel.split('/', 1)[1])}'>entry</a>"
            f" · 同 rank 报告 {len(factor_reports)}"
            f" · {dual_badge} {batch_badge}"
        )

        row_html.append(
            '<tr>'
            f"<td>{idx}</td>"
            f"<td>{escape(row.get('stage', '-'))}</td>"
            f"<td><b><a href='../{escape(entry_rel.split('/', 1)[1])}'>{escape(rank)}</a></b></td>"
            f"<td>{escape(row.get('mother_theme', '-'))}</td>"
            f"<td>{escape(row.get('role', '-'))}</td>"
            f"<td>{escape(row.get('challenge_baseline', '-'))}</td>"
            f"<td>{escape(row.get('unique_increment', '-'))}</td>"
            f"<td><span class='badge {badge_class(status)}'>{escape(status or '-')}</span></td>"
            f"<td>{escape(row.get('next_action', '-'))}</td>"
            f"<td>{factor_cell}</td>"
            '</tr>'
        )

    def status_num(key: str) -> int:
        return by_status.get(key, 0)

    summary_status_html = ''.join(
        f"<span class='pill {badge_class(k)}'>{k}: {status_num(k)}</span>"
        for k in ['keep', 'watch', 'bench', 'archive']
    )

    batch_pills = ''.join(
        f"<span class='pill {batch_badge_class(k)}'>batch {k}: {batch_counts.get(k, 0)}</span>"
        for k in ['done', 'pending', 'running', 'blocked']
    ) if batch_counts else "<span class='pill'>batch state: not initialized</span>"

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>全量 Rank（P3+P2）总表</title>
  <style>
    :root {{
      --fg:#0f172a; --muted:#64748b; --bg:#f8fafc; --card:#ffffff; --line:#e2e8f0;
      --keep:#dcfce7; --watch:#dbeafe; --bench:#ffedd5; --archive:#f1f5f9;
      --keep-f:#166534; --watch-f:#1d4ed8; --bench-f:#9a3412; --archive-f:#334155;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.6 -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; }}
    .wrap {{ max-width:1460px; margin:0 auto; padding:24px 18px 56px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px 18px; margin-bottom:14px; }}
    h1,h2 {{ margin:0 0 10px; }}
    .muted {{ color:var(--muted); }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .nav {{ display:flex; flex-wrap:wrap; gap:10px; margin:10px 0 2px; }}
    .btn {{ display:inline-block; border:1px solid var(--line); background:#fff; border-radius:10px; padding:8px 12px; font-weight:600; }}
    .pills {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
    .pill {{ display:inline-block; border-radius:999px; padding:4px 10px; border:1px solid var(--line); background:#f8fafc; font-size:12px; }}
    .pill.keep {{ background:var(--keep); color:var(--keep-f); border-color:#86efac; }}
    .pill.watch {{ background:var(--watch); color:var(--watch-f); border-color:#93c5fd; }}
    .pill.bench {{ background:var(--bench); color:var(--bench-f); border-color:#fdba74; }}
    .pill.archive {{ background:var(--archive); color:var(--archive-f); border-color:#cbd5e1; }}
    .pill.batch-done {{ background:#dcfce7; color:#166534; border-color:#86efac; }}
    .pill.batch-pending {{ background:#e2e8f0; color:#334155; border-color:#cbd5e1; }}
    .pill.batch-running {{ background:#dbeafe; color:#1d4ed8; border-color:#93c5fd; }}
    .pill.batch-blocked {{ background:#fee2e2; color:#991b1b; border-color:#fca5a5; }}
    .pill.batch-other {{ background:#f1f5f9; color:#334155; border-color:#cbd5e1; }}
    .pill.ok {{ background:#dcfce7; color:#166534; border-color:#86efac; }}
    .pill.warn {{ background:#ffedd5; color:#9a3412; border-color:#fdba74; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; background:#fff; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:9px 10px; text-align:left; vertical-align:top; }}
    thead th {{ position:sticky; top:0; z-index:1; background:#f1f5f9; }}
    .table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:12px; }}
    .badge {{ display:inline-block; border-radius:999px; padding:2px 8px; font-size:12px; font-weight:700; }}
    .badge.keep {{ background:var(--keep); color:var(--keep-f); }}
    .badge.watch {{ background:var(--watch); color:var(--watch-f); }}
    .badge.bench {{ background:var(--bench); color:var(--bench-f); }}
    .badge.archive {{ background:var(--archive); color:var(--archive-f); }}
    .badge.other {{ background:#e2e8f0; color:#334155; }}
    .summary-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:10px; margin-top:10px; }}
    .summary-box {{ border:1px solid var(--line); border-radius:10px; padding:10px 12px; background:#fff; }}
    code {{ background:#eff6ff; border-radius:6px; padding:1px 5px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card\">
      <h1>全量 Rank（P3+P2）总表</h1>
      <p class=\"muted\">口径：保留曾进过 P3/P2 的条目。每个 rank 都生成 entry 页，并按 batch 状态推进双页（report + decomposition）。</p>
      <div class=\"nav\">
        <a class=\"btn\" href=\"../../index.html\">← 站点首页</a>
        <a class=\"btn\" href=\"../rank_strategy_hub/report.html\">Rank Strategy Hub</a>
        <a class=\"btn\" href=\"../alpha_closure_board/report.html\">Alpha Closure Board</a>
        <a class=\"btn\" href=\"../rank32b/report.html\">Rank32B 主页面</a>
      </div>
      <div class=\"pills\">
        <span class=\"pill\">总条目：{len(rows)}</span>
        <span class=\"pill\">P3：{by_stage.get('P3', 0)}</span>
        <span class=\"pill\">P2：{by_stage.get('P2', 0)}</span>
        <span class=\"pill\">已有同 rank 报告：{published_count}</span>
        <span class=\"pill\">dual-page ready：{dual_ready_count}</span>
        {summary_status_html}
        {batch_pills}
      </div>
    </div>

    <div class=\"card\">
      <h2>维护说明（可持续更新）</h2>
      <div class=\"summary-grid\">
        <div class=\"summary-box\">
          <b>数据源</b>
          <p class=\"muted\"><code>reports/artifacts/rank_registry/full_rank_p3_p2_table.csv</code></p>
        </div>
        <div class=\"summary-box\">
          <b>双页构建脚本</b>
          <p class=\"muted\"><code>python3 /root/clawd/jerry/momentum/scripts/build_rank_p2p3_dedicated_reports.py --rank rankXXX</code></p>
        </div>
        <div class=\"summary-box\">
          <b>批处理状态</b>
          <p class=\"muted\"><code>reports/artifacts/rank_registry/p3_p2_report_batch_state.json</code></p>
        </div>
        <div class=\"summary-box\">
          <b>发布时间</b>
          <p class=\"muted\">{fmt_bj_utc(now)}</p>
        </div>
      </div>
    </div>

    <div class=\"card\">
      <h2>明细表</h2>
      <div class=\"table-wrap\">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>阶段</th>
              <th>rank</th>
              <th>母题</th>
              <th>角色</th>
              <th>挑战 baseline</th>
              <th>唯一增量</th>
              <th>状态</th>
              <th>下一步唯一动作</th>
              <th>factor 目录展示</th>
            </tr>
          </thead>
          <tbody>
            {''.join(row_html)}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ENTRY_ROOT.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(), encoding='utf-8')
    print(f'[ok] wrote {OUT_PATH}')


if __name__ == '__main__':
    main()
