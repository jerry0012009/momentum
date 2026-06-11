#!/usr/bin/env python3
"""Build the canonical Rank 450 strategy directory and page aliases."""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "reports" / "site" / "paper"
RANK450 = PAPER / "rank450"

LEGACY_INDEX = PAPER / "rank450_event_alpha_research.html"
CANONICAL_INDEX = RANK450 / "index.html"


STRATEGIES = [
    {
        "phase": "Phase 2a",
        "slug": "phase2a_momentum_ignition",
        "name": "Momentum Ignition",
        "cn_name": "二次点火追多",
        "role": "事件语境内的追多/tail-capture 方向",
        "legacy": "binance_event_study_v1_6a_momentum_ignition_report.html",
        "canonical": "phase2a_momentum_ignition.html",
        "status": "ARCHIVE RESEARCH / 当前执行已迁移到 SL-only",
        "summary": "用量能突增和小时涨幅识别事件后的二段 squeeze。早期移动止盈版本因为回测-实盘差异过大已弃用；当前只保留为研究证据，实盘/paper 执行入口已迁移到 Phase2a SL-only。",
        "why": "适合回答：事件已经出现后，是否继续顺势追多、如何抓右尾。",
        "risk": "中位数偏弱、收益依赖少数大行情，对滑点和去尾部检验敏感。",
    },
    {
        "phase": "Phase 2b",
        "slug": "phase2b_short_reversal",
        "name": "Short Reversal",
        "cn_name": "冲高回落做空",
        "role": "极端上涨后的短线反转/止盈型做空方向",
        "legacy": "binance_event_study_v1_6_2b_short_reversal.html",
        "canonical": "phase2b_short_reversal.html",
        "status": "WATCH / 不能直接上线",
        "summary": "要求前 12h 放量冲高，随后从局部高点回落。最佳组合 B_sv5.0_dr-2 / hold_8h_tp5pct 单笔净均值约 +0.83%，但收益集中在 B 类和 5% 止盈退出。",
        "why": "适合回答：极端事件后买盘衰竭时，能否短线做空回吐。",
        "risk": "参数族窄、止盈触发乐观风险高，2024 明显变薄，需要 walk-forward 和 position-level replay。",
    },
    {
        "phase": "Phase 2c",
        "slug": "phase2c_funding_squeeze_carry",
        "name": "Funding Squeeze Carry",
        "cn_name": "负费率延续做多",
        "role": "极端负 funding + continuation 的拥挤空头挤压方向",
        "legacy": "binance_event_study_phase2c.html",
        "canonical": "phase2c_funding_squeeze_carry.html",
        "status": "WATCH+ / 样本内强，继续 OOS",
        "summary": "在 continuation 结构确认后，筛选极端负资金费率币种做多。修复 funding 结算和前视偏差后，样本内最优仍很强，但样本较小且需要样本外验证。",
        "why": "适合回答：空头拥挤且价格继续上行时，是否可以吃 squeeze 与 funding carry。",
        "risk": "结构确认晚、样本量偏小，收益不应被理解为纯 funding 收租，仍需 holdout、walk-forward 和成本曲线。",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def rel_to_paper(path: str) -> str:
    if path.startswith(("#", "http://", "https://", "mailto:", "../", "/", "rank450/")):
        return path
    if path.endswith(".html"):
        return "../" + path
    return path


def rewrite_links_for_rank450(content: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return f'href="{rel_to_paper(match.group(1))}"'

    return re.sub(r'href="([^"]+)"', repl, content)


def nav_html(current_slug: str) -> str:
    links = [
        ("index", "总览", "index.html"),
        ("phase2a_momentum_ignition", "2a 二次点火追多", "phase2a_momentum_ignition.html"),
        ("phase2b_short_reversal", "2b 冲高回落做空", "phase2b_short_reversal.html"),
        ("phase2c_funding_squeeze_carry", "2c 负费率延续做多", "phase2c_funding_squeeze_carry.html"),
        ("phase2_portal", "Phase2 当前总入口", "../../factors/phase2_strategy_portal/report.html"),
        ("hub", "事件研究入口", "../binance_event_study_hub.html"),
    ]
    items = []
    for slug, label, href in links:
        active = "font-weight:700;color:#fff;" if slug == current_slug else ""
        items.append(f'<a style="{active}" href="{href}">{html.escape(label)}</a>')
    return (
        '<nav class="rank450-nav" style="margin:0 0 18px;padding:12px 14px;'
        'border:1px solid #334155;border-radius:10px;background:#0f172a;'
        'display:flex;gap:12px;flex-wrap:wrap;font-size:13px">'
        + " · ".join(items)
        + "</nav>"
    )


def archive_notice_html(slug: str) -> str:
    base_style = (
        "margin:0 0 18px;padding:12px 14px;border-left:4px solid #f59e0b;"
        "border-radius:0 8px 8px 0;background:rgba(245,158,11,.10);color:#e5e7eb"
    )
    if slug == "phase2a_momentum_ignition":
        text = (
            "<strong>归档提示：</strong>本页保留的是 Phase2a 早期 V4 / trailing-stop 研究证据，"
            "其中“2% 移动止盈可进 paper”的旧执行建议已经被撤销。当前 paper/live 只认 "
            "<a href=\"../../factors/phase2_strategy_portal/report.html\">Phase2 策略总入口</a> 与 "
            "<a href=\"../../factors/paper_phase2a_event_v4_sl_only/report.html\">Phase2a SL-only 审计页</a>："
            "固定 8% SL + 96h timeout，不再使用移动止盈。"
        )
    elif slug == "phase2b_short_reversal":
        text = (
            "<strong>归档提示：</strong>Phase2b 当前是 WATCH 研究方向，不具备 paper/live 执行权限。"
            "当前 Phase2 执行只在 Phase2a SL-only。"
        )
    elif slug == "phase2c_funding_squeeze_carry":
        text = (
            "<strong>归档提示：</strong>Phase2c 当前是 WATCH+ 研究方向，仍需 OOS / walk-forward，"
            "不属于当前 paper/live 执行包。"
        )
    else:
        text = (
            "<strong>归档提示：</strong>本目录是 Rank450 / Phase2 研究归档。"
            "当前执行入口请看 <a href=\"../../factors/phase2_strategy_portal/report.html\">Phase2 策略总入口</a>。"
        )
    return f'<div class="rank450-archive-notice" style="{base_style}">{text}</div>'


def inject_nav(content: str, slug: str) -> str:
    marker = nav_html(slug)
    notice = archive_notice_html(slug)
    content = re.sub(r'<nav class="rank450-nav".*?</nav>\s*', "", content, flags=re.DOTALL)
    content = re.sub(r'<div class="rank450-archive-notice".*?</div>\s*', "", content, flags=re.DOTALL)
    content = rewrite_links_for_rank450(content)
    content = re.sub(r'<p class="muted"><a href="[^"]+">←?[^<]+</a></p>\s*', "", content, count=1)
    content = re.sub(r'<p class="muted"><a href="[^"]+">[^<]+</a> · <a href="[^"]+">[^<]+</a></p>\s*', "", content, count=1)
    if "<body><div class=\"wrap\">" in content:
        return content.replace("<body><div class=\"wrap\">", f"<body><div class=\"wrap\">\n{marker}\n{notice}\n", 1)
    if "<body>\n<div class=\"wrap\">" in content:
        return content.replace("<body>\n<div class=\"wrap\">", f"<body>\n<div class=\"wrap\">\n{marker}\n{notice}\n", 1)
    return content.replace("<body>", f"<body>\n{marker}\n{notice}", 1)


def read_strategy_source(strategy: dict[str, str]) -> str:
    legacy = PAPER / strategy["legacy"]
    canonical = RANK450 / strategy["canonical"]
    if legacy.exists():
        text = legacy.read_text(encoding="utf-8")
        if "rank450-legacy-redirect" not in text:
            return text
    if canonical.exists():
        return canonical.read_text(encoding="utf-8")
    raise FileNotFoundError(f"missing source page for {strategy['phase']}: {legacy}")


def redirect_page(title: str, target: str) -> str:
    safe_title = html.escape(title)
    safe_target = html.escape(target, quote=True)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="0; url={safe_target}">
<link rel="canonical" href="{safe_target}">
<title>{safe_title} · 已整理到 Rank 450 新路径</title>
<style>
body{{margin:0;background:#0b1220;color:#e5e7eb;font:15px/1.7 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif}}
.wrap{{max-width:760px;margin:80px auto;padding:0 20px}}
a{{color:#7dd3fc}}
code{{background:#111827;padding:2px 6px;border-radius:6px}}
</style>
</head>
<body class="rank450-legacy-redirect">
<div class="wrap">
<h1>{safe_title}</h1>
<p>这个旧链接已整理到 Rank 450 的规范路径：</p>
<p><a href="{safe_target}"><code>{safe_target}</code></a></p>
</div>
</body>
</html>
"""


def build_index() -> str:
    rows = []
    cards = []
    for s in STRATEGIES:
        href = s["canonical"]
        cards.append(
            f"""<section class="card">
<div class="phase">{html.escape(s['phase'])}</div>
<h2><a href="{href}">{html.escape(s['cn_name'])}</a></h2>
<p class="en">{html.escape(s['name'])}</p>
<p>{html.escape(s['summary'])}</p>
<p class="status">{html.escape(s['status'])}</p>
</section>"""
        )
        rows.append(
            f"""<tr>
<td><strong>{html.escape(s['phase'])}</strong></td>
<td><a href="{href}">{html.escape(s['cn_name'])}</a><br><span>{html.escape(s['name'])}</span></td>
<td>{html.escape(s['role'])}</td>
<td>{html.escape(s['why'])}</td>
<td>{html.escape(s['risk'])}</td>
<td><code>paper/rank450/{html.escape(s['canonical'])}</code></td>
</tr>"""
        )

    legacy_rows = "\n".join(
        f"<tr><td><code>paper/{html.escape(s['legacy'])}</code></td><td><code>paper/rank450/{html.escape(s['canonical'])}</code></td></tr>"
        for s in STRATEGIES
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rank 450 策略方向总览</title>
<style>
:root{{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#d1d7df;--muted:#8b949e;--accent:#58a6ff;--green:#3fb950;--yellow:#d29922;--red:#f85149}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.7 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif}}
.wrap{{max-width:1240px;margin:0 auto;padding:28px 18px 64px}}
a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}
.hero{{border:1px solid #334155;border-radius:14px;background:#0f172a;padding:22px 24px;margin:0 0 20px}}
h1{{margin:0 0 8px;font-size:1.9rem;color:#f1f5f9}}h2{{margin:0 0 4px;font-size:1.15rem}}
.muted,.en,td span{{color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:18px 0}}
.card{{border:1px solid var(--border);border-radius:10px;background:var(--card);padding:16px}}
.phase{{font-size:.78rem;color:var(--yellow);font-weight:700;text-transform:uppercase;letter-spacing:.04em}}
.status{{display:inline-block;margin-top:8px;padding:2px 8px;border-radius:6px;background:#10281a;color:var(--green);font-size:.82rem;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin:14px 0 28px;background:var(--card);border:1px solid var(--border)}}
th,td{{border-bottom:1px solid var(--border);padding:9px 11px;text-align:left;vertical-align:top;font-size:.9rem}}
th{{background:#101821;color:#cbd5e1;white-space:nowrap}}tr:last-child td{{border-bottom:0}}
code{{background:#0b1320;border:1px solid #263244;padding:2px 6px;border-radius:5px;color:#e6edf3;font-size:.85em}}
.note{{border-left:4px solid var(--yellow);background:rgba(210,153,34,.08);padding:12px 15px;border-radius:0 8px 8px 0;margin:16px 0}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}table{{font-size:.82rem}}th,td{{padding:7px}}}}
</style>
</head>
<body>
<div class="wrap">
{nav_html("index")}
<div class="hero">
<h1>Rank 450 · 策略方向总览</h1>
<p class="muted">把原先混在 v1.6a / Phase 2b / Phase 2c 里的三条可交易方向整理为固定命名和固定路径。生成时间：{utc_now()}</p>
</div>

<div class="note">
<strong>命名口径：</strong>Rank 450 现在只保留三条 Phase 2 策略方向：2a 追多、2b 做空、2c 负费率延续做多。旧口径里的“Phase 2b 去事件化测试”不再作为策略方向命名；它是 2a 的反偏差验证模块。当前交易执行入口不是本目录，而是 <a href="../../factors/phase2_strategy_portal/report.html">Phase2 策略总入口</a> 和 <a href="../../factors/paper_phase2a_event_v4_sl_only/report.html">Phase2a SL-only 审计页</a>。
</div>

<div class="grid">
{''.join(cards)}
</div>

<h2>三条方向怎么区分</h2>
<table>
<thead><tr><th>Phase</th><th>名称</th><th>策略角色</th><th>回答的问题</th><th>主要风险</th><th>规范路径</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>

<h2>推荐阅读顺序</h2>
<ol>
<li>先看 <a href="../../factors/phase2_strategy_portal/report.html">Phase2 策略总入口</a>，确认 current / archive / deprecated 的边界。</li>
<li>再看 <a href="phase2a_momentum_ignition.html">Phase 2a 二次点火追多</a>，理解事件内 V4 timing filter 的来源和反偏差验证。</li>
<li>再看 <a href="phase2b_short_reversal.html">Phase 2b 冲高回落做空</a>，它是 2a 的相反交易假设，关注买盘衰竭后的短线回吐。</li>
<li>最后看 <a href="phase2c_funding_squeeze_carry.html">Phase 2c 负费率延续做多</a>，它不是 V4 信号，而是 funding 拥挤 + continuation 的独立方向。</li>
</ol>

<h2>路径整理</h2>
<table>
<thead><tr><th>旧路径</th><th>新规范路径</th></tr></thead>
<tbody>
{legacy_rows}
<tr><td><code>paper/rank450_event_alpha_research.html</code></td><td><code>paper/rank450/index.html</code>（同内容镜像，作为兼容入口保留）</td></tr>
</tbody>
</table>

<p class="muted">上级入口：<a href="../binance_event_study_hub.html">Binance 事件研究统一入口</a></p>
</div>
</body>
</html>
"""


def index_for_paper_root(index_html: str) -> str:
    replacements = {
        'href="index.html"': 'href="rank450/index.html"',
        'href="phase2a_momentum_ignition.html"': 'href="rank450/phase2a_momentum_ignition.html"',
        'href="phase2b_short_reversal.html"': 'href="rank450/phase2b_short_reversal.html"',
        'href="phase2c_funding_squeeze_carry.html"': 'href="rank450/phase2c_funding_squeeze_carry.html"',
        'href="../binance_event_study_hub.html"': 'href="binance_event_study_hub.html"',
        'href="../../factors/phase2_strategy_portal/report.html"': 'href="../factors/phase2_strategy_portal/report.html"',
        'href="../../factors/paper_phase2a_event_v4_sl_only/report.html"': 'href="../factors/paper_phase2a_event_v4_sl_only/report.html"',
    }
    out = index_html
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out


def main() -> None:
    RANK450.mkdir(parents=True, exist_ok=True)

    for strategy in STRATEGIES:
        content = read_strategy_source(strategy)
        content = inject_nav(content, strategy["slug"])
        target = RANK450 / strategy["canonical"]
        target.write_text(content, encoding="utf-8")

        legacy = PAPER / strategy["legacy"]
        legacy.write_text(
            redirect_page(
                f"{strategy['phase']} {strategy['cn_name']}",
                f"rank450/{strategy['canonical']}",
            ),
            encoding="utf-8",
        )

    index_html = build_index()
    CANONICAL_INDEX.write_text(index_html, encoding="utf-8")
    LEGACY_INDEX.write_text(index_for_paper_root(index_html), encoding="utf-8")

    print(f"[ok] wrote {CANONICAL_INDEX}")
    print(f"[ok] wrote {LEGACY_INDEX}")
    for s in STRATEGIES:
        print(f"[ok] {s['phase']} -> {RANK450 / s['canonical']}")


if __name__ == "__main__":
    main()
