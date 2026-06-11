#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT_BASE = ROOT / "reports" / "site" / "factors"
CONFIRMATION_LADDER_REPORT = OUT_BASE / "trendline_confirmation_ladder" / "report.html"


@dataclass
class QaItem:
    q: str
    a: str


@dataclass
class ReportRef:
    rel_html: str
    title: str
    phase: str
    question: str
    takeaway: str
    qa_title: str = ""
    qa_items: list[QaItem] = field(default_factory=list)


@dataclass
class LinkRef:
    href: str
    label: str


@dataclass
class FocusCard:
    title: str
    status: str
    summary: str
    href: str
    cta: str = "打开页面"


@dataclass
class Track:
    slug: str
    title: str
    subtitle: str
    engine_label: str
    engine_summary: str
    why_this_track: list[str] = field(default_factory=list)
    reports: list[ReportRef] = field(default_factory=list)
    appendix_links: list[LinkRef] = field(default_factory=list)
    decision_title: str = ""
    decision_items: list[str] = field(default_factory=list)
    focus_title: str = ""
    focus_cards: list[FocusCard] = field(default_factory=list)
    next_steps_title: str = ""
    next_steps: list[str] = field(default_factory=list)


TRACKS = [
    Track(
        slug="structure_event_mainline",
        title="Structure-Event Research · Mainline",
        subtitle="把当前项目主线、alpha 方向、历史证据和后续入口收敛成默认导航页，不再让读者自己在一堆中间报告里找路。",
        engine_label="研究主线：alpha directions / evidence / next-entry（跨引擎）",
        engine_summary="这页现在优先回答三个问题：我们当前有哪些 alpha 方向、每条线处在什么阶段、下一步应该从哪一页继续。PyTrendline / PyIndicators 仍是底层定义引擎，但默认不应盖过 breakout-short、fib honesty、EMA / PSAR 这些更接近决策的问题。",
        why_this_track=[
            "这是默认主入口：先看整个项目当前有哪些 alpha 方向，而不是先掉进某个局部方法页。",
            "这里会同时告诉你：哪些线已经收工、哪些还值得继续、哪些只是 honesty check，不该误读成已确认 alpha。",
            "Engine Labs 仍然保留，但它们现在更像证据来源和定义层，不再是默认阅读起点。",
        ],
        reports=[
            ReportRef(
                rel_html="../alpha_closure_board/report.html",
                title="Current Alpha Closure Board",
                phase="0. closure-first / current decision board",
                question="当前三条收口线分别处在什么状态？现在最值得继续做什么、什么该收口、什么别过度解读？",
                takeaway="这是新的默认第一页：先把 V3 / Fib / EMA-PSAR 三条线并排看清，再决定要不要回到 TODO、方法页或单条原始报告。",
                qa_title="Q&A · 为什么现在要先看 Closure Board？",
                qa_items=[
                    QaItem(
                        q="Q1. 它和 TODO / Mainline 的区别是什么？",
                        a="Closure Board 只负责把当前三条收口线讲清楚，并直接回答‘现在先做什么’；TODO / Mainline 再负责放更完整的项目结构与历史上下文。",
                    ),
                    QaItem(
                        q="Q2. 我如果只想知道短期研发资源怎么分配，先看什么？",
                        a="先看 Closure Board；它会直接告诉你 EMA / PSAR、breakout-short follow-up、Fibonacci 这三条线各自的当前定位、边界和下一步。",
                    ),
                ],
            ),
            ReportRef(
                rel_html="../../plans/momentum_todo.html",
                title="Momentum TODO / Roadmap",
                phase="1. project map / current priorities",
                question="当前整个项目到底在推进哪些方向？哪些线已经收工，哪些还值得继续？",
                takeaway="先看这页，把主线、收工线、下一步优先级一次性对齐，不要自己在目录里猜。",
                qa_title="Q&A · Mainline 现在应该怎么读？",
                qa_items=[
                    QaItem(
                        q="Q1. 这页和以前的 Mainline 最大区别是什么？",
                        a="以前更像研究协议导航，现在同时承担项目总览：直接把 v3、v0、fib、EMA / PSAR 这些 alpha 方向挂出来。",
                    ),
                    QaItem(
                        q="Q2. 如果我只想知道“现在最值得继续的是什么”，先看哪几页？",
                        a="先看 Closure Board，再看 support_breakout_v0_h24 与 EMA / PSAR；Fib A/B honesty page 用来确认为什么 Fibonacci 应该收口。",
                    ),
                ],
            ),
            ReportRef(
                rel_html="../pytrendline_event_validation_v3_final_verdict/report.html",
                title="PyTrendline v3 Final Verdict",
                phase="1. archived evidence / closed research line",
                question="v3 这条线最终留下了什么？什么被保留，什么被 park，为什么这条线可以正式收工？",
                takeaway="把它当历史证据包看：v3 最重要的遗产不是“继续扩写”，而是留下了 support-breakout short 候选。",
            ),
            ReportRef(
                rel_html="../support_breakout_v0_h24/report.html",
                title="support_breakout_raw @ h24 v0 回测页",
                phase="2. narrow strategy prototype / breakout-short candidate",
                question="如果把 v3 留下来的 breakout-short 候选压成一个最小、可交易解释的策略原型，长什么样？",
                takeaway="这是当前最接近策略层的一页：它把 support_breakout_raw @ h24 变成了一个可继续做成本/执行验证的窄原型。",
            ),
            ReportRef(
                rel_html="../support_breakout_v0_fib_ab/report.html",
                title="Breakout v0 vs Breakout + Fibonacci Retest-Hold",
                phase="3. honesty check / fib enhancement A-B",
                question="Fib 叠加层真的比简单 breakout v0 更好吗，还是只是让人感觉更“高级”？",
                takeaway="当前最诚实的答案是：fib 版没有跑赢简单 breakout v0，所以它更像 honesty check，不像已确认增强层。",
            ),
            ReportRef(
                rel_html="../ema_psar_raw_alpha/report.html",
                title="EMA / PSAR Raw Alpha Focus Report",
                phase="4. independent raw alpha branch",
                question="除了结构事件这条线，当前还有哪些更独立、更朴素的 alpha baseline 候选值得继续？",
                takeaway="这页代表另一条独立方向：EMA 更像 raw baseline，PSAR 更像快反应 / loss-protection 候选。",
            ),
            ReportRef(
                rel_html="../../plans/trendline_event_research.html",
                title="Trendline Event Research Plan",
                phase="5. protocol / research contract",
                question="如果要回到结构事件定义本身，我们到底在验证哪些事件、哪些 protocol、哪些 go/no-go 标准？",
                takeaway="这是研究协议页：当你需要追根溯源时再回来，不是默认第一站。",
            ),
            *([
                ReportRef(
                    rel_html="../trendline_confirmation_ladder/report.html",
                    title="Trendline Confirmation Ladder Report",
                    phase="6. confirmation protocol / retention trade-off",
                    question="更强确认到底是在提升质量，还是只是在牺牲样本换一个更好看的结果？",
                    takeaway="这页是结构事件的协议证据，不是当前 alpha 方向总览本身；需要时再回来核对。",
                    qa_title="Q&A · confirmation ladder 现在扮演什么角色？",
                    qa_items=[
                        QaItem(
                            q="Q1. 为什么它还留在 Mainline？",
                            a="因为它回答的是结构事件本身的确认价值，而不是某个单独引擎的局部实现。",
                        ),
                        QaItem(
                            q="Q2. 它和 v3 / v0 / fib / EMA 的关系是什么？",
                            a="它更像协议层和比较层；而 v3 / v0 / fib / EMA 这些页更接近当前可讨论的 alpha 方向与决策入口。",
                        ),
                    ],
                ),
            ] if CONFIRMATION_LADDER_REPORT.exists() else []),
            ReportRef(
                rel_html="../../plans/cross_engine_mapping.html",
                title="Cross-Engine Mapping",
                phase="7. architecture / where engines fit",
                question="PyIndicators 和 PyTrendline 在整个主线结构里分别扮演什么角色？哪些问题属于 mainline，哪些属于 engine lab？",
                takeaway="当你想搞清“方法页”和“研究主线页”边界时，回来看这页。",
            ),
        ],
        appendix_links=[
            LinkRef("../alpha_closure_board/report.html", "Current Alpha Closure Board"),
            LinkRef("../../plans/report.html", "Plans / Roadmaps"),
            LinkRef("../trendline_pytrendline_track/report.html", "Engine Lab · PyTrendline"),
            LinkRef("../trendline_pyindicator_track/report.html", "Engine Lab · PyIndicators"),
            LinkRef("../../plans/cross_engine_mapping.html", "Cross-Engine Mapping"),
        ],
        decision_title="当前三条收口线（先看这个）",
        decision_items=[
            "EMA / PSAR：继续，且是当前最像 raw alpha baseline 的线 —— EMA 更像主 raw baseline，PSAR 更像快反应 / loss-protection 候选。",
            "support_breakout v0 / breakout-short follow-up：继续，但定位是 conditional alpha / 窄策略原型 —— 值得补成本、OOS、rolling、执行约束，而不是直接宣称成熟短空策略。",
            "Fib retest-hold：正式收口，不升主线 —— 当前证据不支持“fib 增强 breakout”优于简单 v0，更适合降级成 optional filter / archived idea。",
            "PyTrendline v3：已收工 / 历史证据包 —— 它留下来的不是继续扩写 v3，而是 breakout-short 候选与 final verdict。",
        ],
        focus_title="当前 alpha 方向（可直接点进去）",
        focus_cards=[
            FocusCard(
                title="PyTrendline v3 Final Verdict",
                status="已收工 / 历史证据包",
                summary="v3 已正式收线；核心遗产是保留 breakout-short 候选，而不是继续扩 365d / cross-market / huge grid。",
                href="../pytrendline_event_validation_v3_final_verdict/report.html",
            ),
            FocusCard(
                title="support_breakout_raw @ h24 v0",
                status="当前最接近策略原型",
                summary="如果你只想看“当前最像 alpha 的窄原型”，先看这页；它是 v3 结论落到策略层的第一步。",
                href="../support_breakout_v0_h24/report.html",
            ),
            FocusCard(
                title="Breakout v0 vs Fib A/B",
                status="honesty check / 不升主线",
                summary="这页专门防止把 fib 想象成天然增强层；当前最诚实读法是 fib 版没跑赢简单 breakout v0。",
                href="../support_breakout_v0_fib_ab/report.html",
            ),
            FocusCard(
                title="EMA / PSAR Raw Alpha Focus",
                status="独立 raw alpha 分支",
                summary="如果你想看结构事件之外、更朴素的 alpha baseline，这页是当前最明确的入口。",
                href="../ema_psar_raw_alpha/report.html",
            ),
        ],
        next_steps_title="后续推进方向（有明确入口）",
        next_steps=[
            "沿结构事件继续：先看 support_breakout_v0_h24，再进入成本、执行延迟、非重叠持仓这些更接近实现层的验证。",
            "继续看 fib：默认当 A/B honesty page 读，不把它误当成已经跑赢 v0 的增强层。",
            "继续 raw alpha baseline：直接进入 EMA / PSAR 页，回答它们是否值得升级成更完整策略决策页。",
            "需要回到方法和边界：再去看 Trendline Event Research Plan、Confirmation Ladder、Cross-Engine Mapping。",
        ],
    ),
    Track(
        slug="trendline_pytrendline_track",
        title="Engine Lab · PyTrendline",
        subtitle="这是 pytrendline 这套 candidate-line / grouping 定义方式的实验室，用来提供 explainability baseline 与未来 event source 候选。",
        engine_label="定义引擎：pytrendline exhaustive line search",
        engine_summary="这条线不是 live active-line 状态机，而是先找 pivots，再枚举 candidate lines，经过 filter / grouping / scoring 后得到 representative lines，并把其中一部分标成 breakout research events。",
        why_this_track=[
            "这里只回答 pytrendline 这套定义方式本身是怎么工作的。",
            "它当前最大的价值是 explainability baseline，而不是直接给出主线结论。",
            "读完这里后，应回到 Mainline 看这些事件是否真的值得继续研究。",
        ],
        reports=[
            ReportRef(
                rel_html="../pytrendline_research/report.html",
                title="PyTrendline Research Report",
                phase="1. explainability baseline v1",
                question="pivot 如何变成 candidate lines？为什么不能把所有 pivot 两两相连？duplicate grouping / breakout tagging / hindsight boundary 如何理解？",
                takeaway="这是 pytrendline engine 的基线页：它负责讲清定义方式，不负责下最终 alpha 结论。",
            ),
            ReportRef(
                rel_html="../pytrendline_event_source/report.html",
                title="PyTrendline Event Source Bridge v1",
                phase="2. event-source bridge / unified schema input",
                question="现有 pytrendline 产物能不能先翻译成一版最小 event-source sample，供 Mainline 后续统一 schema 与 cross-engine 比较使用？",
                takeaway="这页回答的是“能不能先接进来再比较”。当前答案是：可以，但 v1 仍主要覆盖 breakout / touch candidate，还不是完整 rebound 语义。",
            ),
            ReportRef(
                rel_html="../pytrendline_event_validation/report.html",
                title="PyTrendline Event Validation v1",
                phase="3. event-level observation / forward returns",
                question="这些由 PyTrendline 定义出来的事件发生后，后面 `+1 / +3 / +6 / +12 bars` 是偏涨还是偏跌？哪些 side / slope / quality bucket 更像样？",
                takeaway="这是第一张真正进入 observation 层的页面：不再只做 bridge，而是直接看 event 后的 forward-return 分布。",
            ),
            ReportRef(
                rel_html="../pytrendline_event_validation_v2/report.html",
                title="PyTrendline Event Validation v2",
                phase="4. bigger-sample stability check",
                question="把样本扩到多资产、更长窗口后，v1 里看到的 side / slope / quality 方向性结论还稳不稳？哪些结论只是小样本幻觉？",
                takeaway="这页专门回答“更大样本里这些现象还站不站得住”。如果 v2 仍然不稳，就不能把这些事件升级成可预测因子。",
            ),
        ],
        appendix_links=[
            LinkRef("../structure_event_mainline/report.html", "返回主线：Structure-Event Mainline"),
            LinkRef("../../plans/cross_engine_mapping.html", "Cross-Engine Mapping"),
            LinkRef("../../plans/momentum_todo.html", "Momentum TODO / Roadmap"),
            LinkRef("../trendline_pyindicator_track/report.html", "对照：Engine Lab · PyIndicators"),
        ],
    ),
    Track(
        slug="trendline_pyindicator_track",
        title="Engine Lab · PyIndicators",
        subtitle="这是 active-line / segment-state 这套定义方式的实验室；它提供了大量历史回测与反证，但不再被当作唯一主线。",
        engine_label="定义引擎：PyIndicators-style active-line flow",
        engine_summary="这条线更偏逐 bar 的结构状态机：先有 active support / resistance，再围绕 breakout / failed-breakout / rebound 做事件验证与回测。它当前最大的价值是 baseline event source 和对照组。",
        why_this_track=[
            "这里保留 PyIndicators 这套定义方式的历史证据与语义说明。",
            "它已经贡献了大量重要反证：raw breakout 整体偏弱，只剩少数 subset 值得继续。",
            "后续是否继续，不由这个 lab 自己决定，而由 Mainline 的统一事件验证决定。",
        ],
        reports=[
            ReportRef(
                rel_html="../trendline_breakout_navigator/report.html",
                title="Trendline Breakout Navigator Report",
                phase="1. engine semantics / active-line definition",
                question="PyIndicators 这套 active-line 是怎么逐 bar 长出来的？breakout / wick / provisional / final 各是什么意思？",
                takeaway="这是这个 engine 的定义层基线。先看懂它怎么定义事件，再看后面的回测证据。",
            ),
            ReportRef(
                rel_html="../trendline_segment_backtest/report.html",
                title="Trendline Segment Backtest Report",
                phase="2. baseline backtest",
                question="把这套 engine 产出的 confirmed breakout / failed-breakout rebound 正式变成策略后，baseline 表现如何？",
                takeaway="这是 PyIndicators engine 的基础回测页，也是后续所有 interval / cross-market / subset evidence 的起点。",
            ),
            ReportRef(
                rel_html="../trendline_segment_backtest_interval_sweep/report.html",
                title="Trendline Segment Backtest · Interval Sweep",
                phase="3. interval robustness",
                question="同一套 PyIndicators event logic，在不同 interval 下是否稳定？",
                takeaway="回答这套 engine 的结果是否只是某个单一周期偶然跑出来。",
            ),
            ReportRef(
                rel_html="../trendline_segment_backtest_cross_market/report.html",
                title="Trendline Segment Backtest · Cross-Market",
                phase="4. cross-market robustness",
                question="这套 PyIndicators event logic 是否只在 crypto 勉强成立，还是能迁移到别的市场？",
                takeaway="它负责告诉我们这个 engine 当前的迁移边界，而不是直接给 mainline 下结论。",
            ),
            ReportRef(
                rel_html="../trendline_segment_crypto_rebound_scan/report.html",
                title="Trendline Segment · Crypto Rebound Scan",
                phase="5. rebound subset clue",
                question="如果只在这个 engine 内看，哪些 rebound 参数组合更值得继续审？",
                takeaway="这页的价值不是继续无边界调参，而是告诉我们：在这个 engine 内，rebound 至少存在少数值得进入 mainline 审计的局部高地。",
                qa_title="Q&A · 这页现在应该怎么读？",
                qa_items=[
                    QaItem(
                        q="Q1. 这页是不是还在证明 PyIndicators 是主线？",
                        a="不是。它现在更像一个局部证据页：说明在这个 engine 里，某些 rebound 组合还值得进入下一轮 mainline 审计，但不代表整个 engine 或整个 breakout thesis 值得继续押注。",
                    ),
                    QaItem(
                        q="Q2. 读完这页下一步去哪？",
                        a="下一步应该回到 Structure-Event Mainline，看 subset evidence 和 confirmation ladder，而不是在这个 engine 里无限继续调参。",
                    ),
                ],
            ),
        ],
        appendix_links=[
            LinkRef("../structure_event_mainline/report.html", "返回主线：Structure-Event Mainline"),
            LinkRef("../../plans/cross_engine_mapping.html", "Cross-Engine Mapping"),
            LinkRef("../../plans/momentum_todo.html", "Momentum TODO / Roadmap"),
            LinkRef("../trendline_pytrendline_track/report.html", "对照：Engine Lab · PyTrendline"),
        ],
    ),
]


BASE_CSS = """
    :root {
      --fg: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --bg: #f8fafc;
      --card: #ffffff;
      --link: #2563eb;
      --pill: #eef2ff;
      --pill-fg: #3730a3;
      --accent: #0ea5e9;
      --qa-bg: #fffbeb;
      --qa-border: #fde68a;
    }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: var(--fg); margin: 0; background: var(--bg); }
    a { color: var(--link); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .wrap { max-width: 1480px; margin: 0 auto; padding: 28px 18px 48px; }
    .hero, .card { background: var(--card); border: 1px solid var(--border); border-radius: 16px; }
    .hero { padding: 24px 26px; margin-bottom: 18px; }
    .hero h1 { margin: 0 0 8px; font-size: 34px; line-height: 1.2; }
    .muted { color: var(--muted); }
    .pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
    .pill { display: inline-block; padding: 5px 10px; border-radius: 999px; background: var(--pill); color: var(--pill-fg); font-size: 12px; }
    .grid { display: grid; grid-template-columns: 360px minmax(0, 1fr); gap: 18px; align-items: start; }
    .sidebar { position: sticky; top: 16px; padding: 18px; }
    .sidebar h2 { margin: 0 0 12px; font-size: 20px; }
    .sidebar ul { margin: 0; padding-left: 20px; line-height: 1.7; }
    .viewer { padding: 18px; }
    .report-list { display: grid; gap: 12px; margin-top: 12px; }
    .report-btn { width: 100%; text-align: left; border: 1px solid var(--border); border-radius: 14px; background: #fff; padding: 14px; cursor: pointer; }
    .report-btn.active { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); background: #f0f9ff; }
    .report-btn .phase { font-size: 12px; color: var(--muted); margin-bottom: 4px; }
    .report-btn .title { font-weight: 700; margin-bottom: 6px; }
    .report-btn .desc { font-size: 13px; color: var(--muted); line-height: 1.45; }
    .viewer-head { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; margin-bottom: 12px; }
    .viewer-head h2 { margin: 0 0 6px; font-size: 24px; }
    .actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .action { display: inline-block; border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; background: white; font-size: 13px; }
    .decision-card { margin-top: 16px; border: 1px solid #bfdbfe; border-radius: 14px; background: #eff6ff; padding: 14px 16px; }
    .decision-card h3 { margin: 0 0 10px; font-size: 18px; }
    .decision-card ul { margin: 0; padding-left: 18px; line-height: 1.65; }
    .focus-title { margin: 18px 0 10px; font-size: 18px; }
    .focus-grid { display: grid; gap: 10px; }
    .focus-card { border: 1px solid var(--border); border-radius: 14px; padding: 12px 13px; background: #fff; }
    .focus-card h3 { margin: 8px 0 6px; font-size: 16px; line-height: 1.35; }
    .focus-card p { margin: 0; color: var(--muted); line-height: 1.55; font-size: 13px; }
    .focus-status { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #ede9fe; color: #5b21b6; font-size: 11px; }
    .focus-link { display: inline-block; margin-top: 10px; font-size: 13px; }
    .qa-card { margin: 0 0 14px; border: 1px solid var(--qa-border); border-radius: 14px; background: var(--qa-bg); padding: 16px 18px; }
    .qa-card h3 { margin: 0 0 12px; font-size: 22px; }
    .qa-item { margin-bottom: 14px; }
    .qa-item:last-child { margin-bottom: 0; }
    .qa-q { font-weight: 700; margin-bottom: 6px; }
    .qa-a { line-height: 1.7; color: #334155; }
    .iframe-wrap { border: 1px solid var(--border); border-radius: 14px; overflow: hidden; background: white; }
    iframe { width: 100%; height: 1100px; border: 0; background: white; }
    .appendix { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 10px; }
    @media (max-width: 1080px) {
      .grid { grid-template-columns: 1fr; }
      .sidebar { position: static; }
      iframe { height: 900px; }
    }
"""


def qa_html(report: ReportRef) -> str:
    if not report.qa_items:
        return "<p class='muted'>这个报告当前没有单独的 Q&A 收束区；优先看上面的研究问题与下方原报告内容。</p>"
    items = []
    for item in report.qa_items:
        items.append(
            f"<div class='qa-item'><div class='qa-q'>{escape(item.q)}</div><div class='qa-a'>{escape(item.a)}</div></div>"
        )
    title = report.qa_title or "Q&A 讲解"
    return f"<div class='qa-card'><h3>{escape(title)}</h3>{''.join(items)}</div>"


def render_track_page(track: Track) -> str:
    out_dir = OUT_BASE / track.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    default = track.reports[0]

    report_map: dict[str, dict[str, str]] = {}
    buttons = []
    for idx, report in enumerate(track.reports):
        report_id = f"r{idx}"
        report_map[report_id] = {
            "url": report.rel_html,
            "title": report.title,
            "question": report.question,
            "takeaway": report.takeaway,
            "qaHtml": qa_html(report),
        }
        buttons.append(
            f"""
<button class=\"report-btn{' active' if idx == 0 else ''}\" onclick=\"selectReport('{report_id}', this)\">
  <div class=\"phase\">{escape(report.phase)}</div>
  <div class=\"title\">{escape(report.title)}</div>
  <div class=\"desc\">{escape(report.question)}</div>
</button>
""".strip()
        )

    why_items = "".join(f"<li>{escape(item)}</li>" for item in track.why_this_track)
    decision_html = ""
    if track.decision_items:
        decision_rows = "".join(f"<li>{escape(item)}</li>" for item in track.decision_items)
        decision_title = escape(track.decision_title or "当前 decision board")
        decision_html = f"<div class=\"decision-card\"><h3>{decision_title}</h3><ul>{decision_rows}</ul></div>"
    appendix_html = "".join(
        f"<a class=\"action\" href=\"{escape(link.href)}\">{escape(link.label)}</a>" for link in track.appendix_links
    )
    focus_html = ""
    if track.focus_cards:
        focus_cards_html = "".join(
            f"<div class=\"focus-card\"><span class=\"focus-status\">{escape(card.status)}</span><h3>{escape(card.title)}</h3><p>{escape(card.summary)}</p><a class=\"focus-link\" href=\"{escape(card.href)}\">{escape(card.cta)} →</a></div>"
            for card in track.focus_cards
        )
        focus_title = escape(track.focus_title or "当前重点")
        focus_html = f"<h2 class=\"focus-title\">{focus_title}</h2><div class=\"focus-grid\">{focus_cards_html}</div>"
    next_steps_html = ""
    if track.next_steps:
        next_title = escape(track.next_steps_title or "后续方向")
        next_rows = "".join(f"<li>{escape(item)}</li>" for item in track.next_steps)
        next_steps_html = f"<div class=\"decision-card\"><h3>{next_title}</h3><ul>{next_rows}</ul></div>"
    default_qa_html = report_map["r0"]["qaHtml"]
    report_json = json.dumps(report_map, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(track.title)}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>
    <div class=\"hero\">
      <h1>{escape(track.title)}</h1>
      <p class=\"muted\">{escape(track.subtitle)}</p>
      <div class=\"pills\">
        <span class=\"pill\">{escape(track.engine_label)}</span>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">Reports included: {len(track.reports)}</span>
      </div>
      <p style=\"margin-top:12px;\">{escape(track.engine_summary)}</p>
    </div>

    <div class=\"grid\">
      <aside class=\"card sidebar\">
        <h2>这条大轨道解决什么问题？</h2>
        <ul>{why_items}</ul>
        {decision_html}
        {focus_html}
        {next_steps_html}
        <div class=\"appendix\">{appendix_html}</div>
        <h2 style=\"margin-top:18px;\">按研究顺序查看</h2>
        <div class=\"report-list\">{' '.join(buttons)}</div>
      </aside>

      <main class=\"card viewer\">
        <div class=\"viewer-head\">
          <div>
            <h2 id=\"viewer-title\">{escape(default.title)}</h2>
            <p id=\"viewer-question\" class=\"muted\">{escape(default.question)}</p>
            <p id=\"viewer-takeaway\">{escape(default.takeaway)}</p>
          </div>
          <div class=\"actions\">
            <a id=\"open-raw\" class=\"action\" href=\"{escape(default.rel_html)}\" target=\"_blank\" rel=\"noreferrer\">单独打开原报告</a>
          </div>
        </div>
        <div id=\"viewer-qa\">{default_qa_html}</div>
        <div class=\"iframe-wrap\">
          <iframe id=\"viewer-frame\" src=\"{escape(default.rel_html)}\" loading=\"eager\"></iframe>
        </div>
      </main>
    </div>
  </div>

  <script>
    const REPORTS = {report_json};
    function selectReport(reportId, btn) {{
      const report = REPORTS[reportId];
      if (!report) return;
      document.querySelectorAll('.report-btn').forEach(el => el.classList.remove('active'));
      if (btn) btn.classList.add('active');
      document.getElementById('viewer-title').textContent = report.title || '';
      document.getElementById('viewer-question').textContent = report.question || '';
      document.getElementById('viewer-takeaway').textContent = report.takeaway || '';
      document.getElementById('viewer-frame').src = report.url || '';
      document.getElementById('open-raw').href = report.url || '';
      document.getElementById('viewer-qa').innerHTML = report.qaHtml || '';
    }}
  </script>
</body>
</html>
"""
    (out_dir / "report.html").write_text(html, encoding="utf-8")


def main() -> int:
    for track in TRACKS:
        render_track_page(track)
    print("[ok] trendline track pages generated")
    for track in TRACKS:
        print("[site]", OUT_BASE / track.slug / "report.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
