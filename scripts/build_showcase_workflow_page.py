#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "interview_showcase"
ALIAS_SITE_DIR = ROOT / "reports" / "site" / "factor_research_library"
OUT_HTML = SITE_DIR / "workflow.html"
ALIAS_OUT_HTML = ALIAS_SITE_DIR / "workflow.html"


def ensure_dirs() -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    ALIAS_SITE_DIR.mkdir(parents=True, exist_ok=True)


def table_html(df: pd.DataFrame, cols: list[str], labels: dict[str, str], max_rows: int = 80) -> str:
    if df.empty:
        return "<p class='muted'>No data.</p>"
    head = df[cols].head(max_rows).copy()
    parts = ["<table><thead><tr>"]
    for col in cols:
        parts.append(f"<th>{escape(labels.get(col, col))}</th>")
    parts.append("</tr></thead><tbody>")
    for _, row in head.iterrows():
        parts.append("<tr>")
        for col in cols:
            parts.append(f"<td>{escape(str(row.get(col, '') if pd.notna(row.get(col, '')) else ''))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def workflow_crontab_lines() -> list[str]:
    try:
        proc = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False)
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    lines: list[str] = []
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "/root/clawd/jerry/momentum" not in line:
            continue
        lines.append(line)
    return lines


def live_cron_df() -> pd.DataFrame:
    wrapper_meta = {
        "run_ema_paper_trading_autopilot_cron.sh": {
            "job_name": "EMA paper autopilot",
            "purpose": "每 15 分钟检查 EMA paper lane 是否真的到点；未到点则只记录 waiting 状态，到点才执行 guarded refresh 并发布页面。",
            "runner": "run_ema_paper_trading_autopilot.py -> run_ema_paper_trading_guarded_refresh.py",
            "publish": "publish_ema_paper_trading_site.sh",
            "outputs": "ema_psar_raw_alpha status / due snapshot / refresh history / factor page",
        },
        "run_rank151_breakout_bandpass_paper_runner_cron.sh": {
            "job_name": "Rank151 breakout band-pass paper runner",
            "purpose": "每 15 分钟刷新 Rank151 的 paper lane；已有 state 则 append，新线则 init，并把报告页同步到外网。",
            "runner": "run_rank151_breakout_bandpass_paper_runner.py",
            "publish": "publish_rank151_breakout_bandpass_paper_page.sh",
            "outputs": "paper_rank151_breakout_bandpass_gate ledger / status / state / factor page",
        },
    }
    rows: list[dict[str, str]] = []
    for line in workflow_crontab_lines():
        tokens = line.split()
        if len(tokens) < 6:
            continue
        schedule = " ".join(tokens[:5])
        command = " ".join(tokens[5:])
        comment = ""
        if "#" in command:
            command, comment = command.split("#", 1)
            command = command.strip()
            comment = comment.strip()
        wrapper = ""
        for token in command.split():
            if token.endswith(".sh") or token.endswith(".py"):
                wrapper = Path(token).name
                break
        meta = wrapper_meta.get(wrapper, {})
        rows.append(
            {
                "schedule": schedule,
                "job_name": meta.get("job_name", comment or wrapper or "momentum scheduled job"),
                "wrapper": wrapper or "-",
                "purpose": meta.get("purpose", command),
                "runner": meta.get("runner", "-"),
                "publish": meta.get("publish", "-"),
                "outputs": meta.get("outputs", "-"),
                "raw_command": line,
            }
        )
    return pd.DataFrame(rows)


def repo_automation_df() -> pd.DataFrame:
    rows = [
        {
            "layer": "Research automation",
            "entrypoint": "docs/RESEARCH_AUTOMATION_BRIEF.md",
            "role": "定义 OpenClaw / Scout 定时研究的选题、写作与网站同步规则。",
            "promotion": "paper / external idea -> quant digest",
        },
        {
            "layer": "Digest build",
            "entrypoint": "build_quant_digest_site.py",
            "role": "把 research/quant_digests/*.md 编译成 reading 子站 HTML。",
            "promotion": "markdown digest -> reading page",
        },
        {
            "layer": "Registry / map",
            "entrypoint": "MAINLINE1_STRATEGY_FACTOR_MAP + P2/P3 registry",
            "role": "把题材归入策略母题、当前阶段和后续 admission 路线。",
            "promotion": "digest / idea -> rank candidate",
        },
        {
            "layer": "Paper runner",
            "entrypoint": "run_rank*_paper_runner.py",
            "role": "把通过审查的 rank 变成持续刷新的 paper lane，沉淀 state / status / closed trades。",
            "promotion": "clean replication -> runner artifacts",
        },
        {
            "layer": "Publish pipeline",
            "entrypoint": "publish_report_site.sh / publish_interview_showcase.sh / publish_homepage_index.sh",
            "role": "把 reports/site 与 artifacts 同步到 /var/www/momentum-report。",
            "promotion": "local site -> public site",
        },
        {
            "layer": "OpenClaw callback",
            "entrypoint": "run_report_pipeline.py -> report_pipeline.py",
            "role": "流水线完成后可调用 `openclaw system event` 回推 build/publish 结果。",
            "promotion": "pipeline end -> openclaw event",
        },
    ]
    return pd.DataFrame(rows)


def flow_box(title: str, body: str, meta: str = "") -> str:
    meta_html = f"<p class='box-meta'>{escape(meta)}</p>" if meta else ""
    return (
        "<div class='flow-box'>"
        f"<h3>{escape(title)}</h3>"
        f"{meta_html}"
        f"<p>{escape(body)}</p>"
        "</div>"
    )


def render_page() -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cron_df = live_cron_df()
    repo_df = repo_automation_df()
    cron_names = ", ".join(cron_df["job_name"].astype(str).tolist()) if not cron_df.empty else "-"
    cron_table = table_html(
        cron_df,
        ["schedule", "job_name", "wrapper", "purpose", "runner", "publish", "outputs"],
        {
            "schedule": "Cron",
            "job_name": "任务",
            "wrapper": "入口 shell",
            "purpose": "功能",
            "runner": "核心 runner",
            "publish": "发布动作",
            "outputs": "主要产物",
        },
        max_rows=20,
    )
    repo_table = table_html(
        repo_df,
        ["layer", "entrypoint", "role", "promotion"],
        {"layer": "自动化层", "entrypoint": "入口", "role": "功能", "promotion": "推进到下一步"},
        max_rows=20,
    )
    raw_cron = (
        "<pre class='code-block'>"
        + escape("\n".join(cron_df["raw_command"].astype(str).tolist()))
        + "</pre>"
        if not cron_df.empty
        else "<p class='muted'>当前没有从 host `crontab -l` 读取到 momentum 相关条目。</p>"
    )
    upstream_flow = (
        "<div class='flow-grid'>"
        + flow_box("1. OpenClaw / Scout 选题", "先按 RESEARCH_AUTOMATION_BRIEF 选一个小主题，默认优先 raw alpha、快 first verdict、可复刻。", "研究自动化入口")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("2. Quant Digest", "把研究写成 digest markdown，再编译成 reading 子站 HTML，形成可追溯的研究解释层。", "research/quant_digests -> reading")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("3. Registry / Strategy Hub", "把题材映射进 MAINLINE1 map、P2/P3 registry 与 strategy hub，决定它是否值得升成 rank 研究线。", "idea -> candidate")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("4. Scout / Clean Replication", "做 source intake、clean replication、time stability、honesty audit，确认它不是只在故事层成立。", "candidate -> validated rank")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("5. Paper Runner / Monitoring", "只有通过 admission 的研究线，才进入独立 paper runner，开始沉淀 status、state、closed trades 与 monitoring page。", "rank -> persistent lane")
        + "</div>"
    )
    downstream_flow = (
        "<div class='flow-grid'>"
        + flow_box("Host cron", "Linux host 只负责定时触发 wrapper shell，本身不读取交易逻辑。", f"当前在线任务: {cron_names}")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("Wrapper shell + flock", "先拿锁、防重复运行，再决定本轮是 init、refresh，还是 waiting / skip。", "cron.sh")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("Python runner", "真正更新水位线、due guardrail、status、closed trades 和 run summary 的都是 Python runner。", "paper runner / autopilot")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("Publish script", "单策略 publish 脚本把 factor page 与 artifacts 同步到 `/var/www/momentum-report`。", "publish_*page.sh")
        + "<div class='flow-arrow'>→</div>"
        + flow_box("Showcase 聚合", "showcase 读取各 rank 已写好的 artifacts、IC summary 和状态表，再统一做排序、讲解和横向比较。", "interview_showcase / factor_research_library")
        + "</div>"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Momentum 工作流与定时任务</title>
  <style>
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:#f6f7f9; color:#172033; font:14px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif; }}
    .wrap {{ max-width:1220px; margin:0 auto; padding:28px 18px 56px; }}
    .hero, .section {{ background:#fff; border:1px solid #d9dee8; border-radius:8px; }}
    .hero {{ padding:22px 24px; }}
    .section {{ padding:18px 20px; margin-top:16px; overflow:auto; }}
    h1 {{ margin:0 0 8px; font-size:28px; }}
    h2 {{ margin:0 0 10px; font-size:20px; }}
    h3 {{ margin:0 0 8px; font-size:16px; }}
    p {{ margin:8px 0; }}
    .muted {{ color:#667085; }}
    .nav, .toc {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
    .btn {{ border:1px solid #cfd6e4; border-radius:6px; background:#fff; padding:6px 9px; font-weight:600; color:#175cd3; text-decoration:none; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:16px 0; }}
    .card {{ background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:14px 16px; min-height:96px; }}
    .k {{ color:#667085; font-size:12px; text-transform:uppercase; }}
    .v {{ margin-top:5px; font-size:24px; font-weight:700; }}
    .s {{ margin-top:4px; color:#667085; font-size:12px; }}
    .note {{ border-left:4px solid #175cd3; background:#eff6ff; padding:10px 12px; margin:12px 0; }}
    .warn {{ border-left-color:#dc6803; background:#fff7ed; }}
    .two {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .definition {{ background:#f8fafc; border:1px solid #e4e7ec; border-radius:8px; padding:12px 14px; }}
    .flow-grid {{ display:grid; grid-template-columns:repeat(9,minmax(0,1fr)); gap:10px; align-items:stretch; }}
    .flow-box {{ border:1px solid #d9dee8; border-radius:8px; background:#fff; padding:12px 14px; min-height:138px; }}
    .flow-arrow {{ display:flex; align-items:center; justify-content:center; color:#98a2b3; font-size:28px; font-weight:700; }}
    .box-meta {{ color:#175cd3; font-size:12px; font-weight:600; margin-bottom:6px; }}
    .code-block {{ white-space:pre-wrap; background:#0f172a; color:#e2e8f0; border-radius:8px; padding:14px 16px; overflow:auto; }}
    table {{ width:100%; border-collapse:collapse; min-width:980px; }}
    th, td {{ border-bottom:1px solid #e5e8ef; padding:8px 10px; vertical-align:top; text-align:left; }}
    th {{ background:#f1f4f8; color:#344054; font-size:12px; white-space:nowrap; }}
    a {{ color:#175cd3; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
      .two {{ grid-template-columns:1fr; }}
      .flow-grid {{ grid-template-columns:1fr; }}
      .flow-arrow {{ min-height:20px; font-size:22px; }}
    }}
    @media (max-width: 560px) {{
      .grid {{ grid-template-columns:1fr; }}
      .wrap {{ padding:14px 10px 40px; }}
    }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>Momentum 工作流与定时任务</h1>
    <p class="muted">这页解释两件事：一是当前 host 上真正在线的 momentum 定时任务；二是 OpenClaw / Scout 怎样把研究题材推进成 rank、paper runner 和 showcase 页面。Generated: {escape(generated_at)}</p>
    <div class="note warn">重要区分：不是所有仓库里的 runner 都已挂在 cron 上。这页会把“当前在线 cron”与“仓库里可调用的自动化入口”明确分开。</div>
    <div class="nav">
      <a class="btn" href="index.html">返回 Showcase</a>
      <a class="btn" href="../index.html">Reports 首页</a>
      <a class="btn" href="momentum/rank151_source_breakdown.html">Rank151 来源拆解</a>
      <a class="btn" href="../factors/rank_strategy_hub/report.html">Rank Strategy Hub</a>
      <a class="btn" href="../factors/rank_registry_p3_p2/report.html">P3/P2 Registry</a>
    </div>
    <div class="toc">
      <a class="btn" href="#live-cron">在线 Cron</a>
      <a class="btn" href="#rank-flow">Rank 产出流程</a>
      <a class="btn" href="#lane-flow">Runner 刷新流程</a>
      <a class="btn" href="#repo-automation">自动化入口</a>
      <a class="btn" href="#raw-cron">原始 Crontab</a>
    </div>
  </div>

  <div class="grid">
    <div class="card"><div class="k">在线 Momentum Cron</div><div class="v">{len(cron_df)}</div><div class="s">当前 `crontab -l` 里实际接线的 momentum 任务</div></div>
    <div class="card"><div class="k">当前在线任务</div><div class="v">{escape(cron_names)}</div><div class="s">按 host cron 实际读取，不把全部 repo 脚本算进去</div></div>
    <div class="card"><div class="k">工作流层数</div><div class="v">5</div><div class="s">research -> digest -> registry -> runner -> publish/showcase</div></div>
    <div class="card"><div class="k">OpenClaw 回调点</div><div class="v">1</div><div class="s">report pipeline 可选用 `openclaw system event` 回推完成状态</div></div>
  </div>

  <div class="section">
    <h2>先讲结论</h2>
    <div class="two">
      <div class="definition">
        <h3>不是所有 Rank 都挂定时任务</h3>
        <p>只有已经进入 paper runner / monitoring 阶段、值得持续刷新状态的研究线，才会接到 host cron。大量 rank 仍停留在 digest、scout 或 clean replication 阶段。</p>
      </div>
      <div class="definition">
        <h3>Showcase 是聚合层，不是执行层</h3>
        <p>showcase 不直接跑信号、不维护 watermark，也不做下单。它读取各 rank 已经写好的 artifacts、审计 IC 和状态表，再统一做解释、排序和横向比较。</p>
      </div>
    </div>
  </div>

  <div class="section" id="live-cron">
    <h2>当前在线的 Host Cron</h2>
    <p class="muted">这张表直接来自当前主机的 `crontab -l`，再结合 wrapper shell 与 runner 脚本补足功能说明。它回答的是：这台机器现在到底定时跑了什么。</p>
    {cron_table}
  </div>

  <div class="section" id="rank-flow">
    <h2>Rank 如何产出</h2>
    <p class="muted">上游逻辑不是“先编号、再补故事”，而是先用定时研究自动化找到题材、做 digest、做 scout/clean replication，再决定是否升格成真正的 rank 研究线。</p>
    {upstream_flow}
    <div class="note">真正把题材推进成 rank 的关键在第 3 和第 4 步：如果题材不能通过 intake / clean replication / honesty audit，它就不会进入后面的 paper runner 与 showcase 主线。</div>
  </div>

  <div class="section" id="lane-flow">
    <h2>定时刷新怎样把 Rank 推到页面</h2>
    <p class="muted">这条链路更偏下游，描述的是：一个已经进入 paper lane 的 rank，怎样被 cron 周期性刷新，并把状态发布成 factor page / public site / showcase 证据。</p>
    {downstream_flow}
    <div class="note">host cron 的职责很薄：只负责定时触发与防重入。真正的状态推进、due guardrail、closed trades append、页面构建和外网发布，都在后面的 Python runner 与 publish shell 中完成。</div>
  </div>

  <div class="section" id="repo-automation">
    <h2>仓库里的自动化入口</h2>
    <p class="muted">下面这些入口不代表“全都常驻运行”。它们是不同阶段可被调用的自动化节点：有的服务研究写作，有的服务 digest 编译，有的服务 factor / showcase / homepage 发布。</p>
    {repo_table}
  </div>

  <div class="section" id="raw-cron">
    <h2>原始 Crontab 片段</h2>
    <p class="muted">保留原始 host cron 片段，方便交叉核对这页没有脱离真实机器状态。</p>
    {raw_cron}
  </div>
</div>
</body>
</html>"""


def main() -> int:
    ensure_dirs()
    html = render_page()
    OUT_HTML.write_text(html, encoding="utf-8")
    ALIAS_OUT_HTML.write_text(html, encoding="utf-8")
    print(f"[ok] wrote {OUT_HTML.relative_to(ROOT)}")
    print(f"[ok] wrote {ALIAS_OUT_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
