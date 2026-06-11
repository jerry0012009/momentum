#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re
import shutil

import numpy as np
import pandas as pd

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - report still builds without charts
    plt = None

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "interview_showcase"
ALIAS_ART_DIR = ROOT / "reports" / "artifacts" / "factor_research_library"
SITE_DIR = ROOT / "reports" / "site" / "interview_showcase"
ALIAS_SITE_DIR = ROOT / "reports" / "site" / "factor_research_library"
OUT_HTML = SITE_DIR / "index.html"
ALIAS_OUT_HTML = ALIAS_SITE_DIR / "index.html"
IC_SUMMARY = ART_DIR / "factor_ic_ir_summary.csv"
STORY_SUMMARY = ART_DIR / "strategy_story_summary.csv"
EVIDENCE_SUMMARY = ART_DIR / "paper_live_evidence_summary.csv"
AUTO_IC_COVERAGE = ART_DIR / "auto_ic_coverage.csv"
RANK_REPORT_CATALOG = ART_DIR / "rank_report_catalog.csv"
REGISTRY_TABLE = ROOT / "reports" / "artifacts" / "rank_registry" / "full_rank_p3_p2_table.csv"
EVIDENCE_ARTIFACT_DIR = ART_DIR / "evidence_artifacts"
RANK342_IC_SUMMARY = ROOT / "reports" / "artifacts" / "paper_rank342_samechain_crossdex" / "rank342_gap_close_ic_summary.csv"


@dataclass(frozen=True)
class FactorSpec:
    strategy: str
    display: str
    artifact_dir: str
    frame_glob: str
    factors: tuple[str, ...]
    report_href: str
    thesis: str


FACTOR_SPECS: tuple[FactorSpec, ...] = (
    FactorSpec(
        strategy="Rank32B slope-floor continuation",
        display="趋势延续 / EMA slope floor",
        artifact_dir="scout_rank32b_slope_floor_continuation_15m",
        frame_glob="*_frame.csv",
        factors=("slope_strength", "fast_slope", "slow_slope", "spread_mid", "signed_slope_floor_signal"),
        report_href="../factors/rank32b/report.html",
        thesis="用 1h EMA 斜率和结构确认过滤 15m 延续信号；该线已因 future/lookahead audit 下线，IC/回测只作为审计材料保留。",
    ),
    FactorSpec(
        strategy="Rank76 intraday clock polarity",
        display="日内时钟 / polarity overlay",
        artifact_dir="scout_rank76_intraday_clock_polarity_15m",
        frame_glob="*_feature_frame.csv",
        factors=("polarity", "polarity_mean", "polarity_tstat", "signed_clock_signal"),
        report_href="../factors/scout_rank76_intraday_clock_polarity_15m/report.html",
        thesis="同一基础形态在不同 UTC 小时的方向性不一致，因此把时钟作为 admission/blackout 层。",
    ),
    FactorSpec(
        strategy="Rank54 LVN/POC acceptance",
        display="成交密集区 / POC-LVN acceptance",
        artifact_dir="scout_rank54_lvn_poc_acceptance_15m",
        frame_glob="*_frame.csv",
        factors=("above_poc_ratio_3", "below_poc_ratio_3", "signed_lvn_signal"),
        report_href="../factors/scout_rank54_lvn_poc_acceptance_15m/report.html",
        thesis="把价格是否接受 POC/LVN 区域转成微观结构状态，检验其对后续短周期收益的方向信息。",
    ),
    FactorSpec(
        strategy="Rank97 RSRS right-skew",
        display="RSRS / right-skew state",
        artifact_dir="scout_rank97_rsrs_right_skew_15m",
        frame_glob="*_frame.csv",
        factors=("rsrs_beta", "rsrs_zscore", "rsrs_modified_score", "rsrs_right_skew", "signed_rsrs_signal"),
        report_href="../factors/scout_rank97_rsrs_right_skew_15m/report.html",
        thesis="用高低价回归斜率和右偏修正表达趋势弹性，避免只看 close-to-close 动量。",
    ),
    FactorSpec(
        strategy="Rank112 basis dislocation veto",
        display="Basis/OI / crowded dislocation",
        artifact_dir="scout_rank112_basis_dislocation_short_veto_15m",
        frame_glob="*_frame.csv",
        factors=("basis_pct_30d", "oi_delta_1h", "basis_extreme_negative", "basis_oi_veto"),
        report_href="../factors/scout_rank112_basis_dislocation_short_veto_15m/report.html",
        thesis="把 basis 和 OI 的异常状态作为 crowded move 的 veto/反身性证据，而不是裸价格突破。",
    ),
    FactorSpec(
        strategy="Rank153 liquidation consensus",
        display="清算拥挤 / funding-OI consensus",
        artifact_dir="scout_rank153_liquidation_consensus_cascade_15m",
        frame_glob="*_feature_frame.csv",
        factors=("funding_rate", "oi_4h_pct", "abs_ret_45m", "funding_abs", "signed_consensus_signal"),
        report_href="../factors/scout_rank153_liquidation_consensus_cascade_15m/report.html",
        thesis="用 funding、OI、急跌急涨和 crowd side 的一致性识别清算级联，而不是单独追涨杀跌。",
    ),
)

IC_REVIEW_RULES: tuple[dict[str, object], ...] = (
    {
        "strategy": "Rank112 basis dislocation veto",
        "factor": "basis_extreme_negative",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "current_candidate",
        "note": "已按 Rank112 clean replication 复核：固定 BTC/ETH/SOL 120d 15m、next-bar open、no-overlap、hold 8 bars；该行只表达『极端负 basis 不宜继续追空』的 honest veto 口径，当前可作为 keep_P1 候选比较。",
    },
    {
        "strategy": "Rank76 intraday clock polarity",
        "factor": "polarity",
        "horizons": (16,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank76 minimal clean replication 复核：小时极性统计本身可重复计算，但整条线在 clean replication 页面已明确是 park / evidence pool；这里只保留可比 IC，供审计和横向参考，不进入当前候选排序。",
    },
    {
        "strategy": "Rank54 LVN/POC acceptance",
        "factor": "signed_lvn_signal",
        "horizons": (4,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank54 clean replication 复核：POC/LVN acceptance 的信号定义和 horizon 可对齐，但页面 hard verdict 为 park / evidence pool，且改善主要来自大幅砍样本；只保留为审计比较行。",
    },
    {
        "strategy": "Rank97 RSRS right-skew",
        "factor": "rsrs_right_skew",
        "horizons": (16,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank97 clean replication 复核：RSRS right-skew 连续状态列可形成稳定横截面 IC，但整条 overlay 研究 hard verdict 仍是 park；该行只作为非主线审计样例展示。",
    },
    {
        "strategy": "Rank154B young funding stat-arb",
        "factor": "funding_price_young_180_365_top30_core",
        "horizons": (10,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "来源是 Rank154B 独立日频 IC summary。已复核 sample=young_180_365_top30_core、target=price、horizon=10 的口径，但 Rank154 系列当前只保留为 archive/research lead，不进入当前候选排序。",
    },
    {
        "strategy": "Rank34 auto frame IC",
        "factor": "ema20_slope_1h",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank34 clean replication 复核：ema20_slope_1h 由已闭合 1h EMA20 的 pct_change 构造，在 BTC/ETH/SOL 15m frame 上独立复算一致；但 Rank34 hard verdict 明确是 park / evidence pool，因为主结论对 synthetic shares / turnover 假设过敏。该行只保留为 audit-only 连续状态对照。",
    },
    {
        "strategy": "Rank35 auto frame IC",
        "factor": "bias_4h",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank35 clean replication 复核：bias_4h = close_4h > ema20_4h，并以 backward as-of 方式并回 15m frame；独立复算一致。但 Rank35 hard verdict 仍是 park / evidence pool，主变体对 VWAP anchor 敏感且成本后 edge 不够诚实。该行只保留为 audit-only higher-tf bias 对照。",
    },
    {
        "strategy": "Rank33 auto frame IC",
        "factor": "bias_long",
        "horizons": (1, 4),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank33 clean replication 复核：bias_long 由因果 NW 1h slope floor + close_1h >= nw_smooth_1h 构造，并只与已确认 extrema / next-bar open 执行口径并存；独立复算一致。但 Rank33 hard verdict 仍是 park / evidence pool，因此这里只保留为 audit-only 的 higher-tf admission bias 对照。",
    },
    {
        "strategy": "Rank33 auto frame IC",
        "factor": "bias_short",
        "horizons": (1, 4),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank33 clean replication 复核：bias_short 由因果 NW 1h slope floor 的 short 侧 admission flag 构造，确认 extrema 与 lookahead guard 口径可对齐；独立复算一致。但 Rank33 页面 hard verdict 仍是 park / evidence pool，该行只作为 audit-only 的 short-side bias 参考。",
    },
    {
        "strategy": "Rank110 auto frame IC",
        "factor": "bear_reclaim_signal",
        "horizons": (4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank110 clean replication 复核：bear_reclaim_signal 明确对应『前一枚已出现的 bear flip dot 在 N bars 内被当根 reclaim』，并按 next-bar open / no-overlap 口径执行；独立复算一致。但 report hard verdict 是 keep_P1_mixed，且页面明确 short mirror 不够硬，因此只保留为 audit-only 的 mixed-evidence 样例。",
    },
    {
        "strategy": "Rank53 auto frame IC",
        "factor": "breakdown_reclaim_short_signal",
        "horizons": (4,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank53 clean replication 复核：breakdown_reclaim_short_signal 对应 15m close-confirmed CHoCH 研究里的 short archetype 原始触发列，定义为 EMA 走弱 + rolling_low20 breakdown reclaim + volume gate；独立复算一致。需注意它不是页面最终的 liquidity_sweep_veto 执行臂，只能作为 raw setup archetype 的 audit-only IC 参考，而 report hard verdict 仍是 park / evidence pool。",
    },
    {
        "strategy": "Rank50 auto frame IC",
        "factor": "signal_structural_reclaim_plus_htf",
        "horizons": (4,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank50 clean replication 复核：signal_structural_reclaim_plus_htf 直接对应页面主变体 structural_reclaim_plus_htf，即 confirmed breakout retest reclaim 再叠加 1h/15m 同向 bias；独立复算一致。但 6bps 下跨资产 mean_total_return 约 -4.63%、false_reclaim 约 72.78%、no-trade 约 87.14%，hard verdict 明确仍是 park / evidence pool，因此只保留为 audit-only 样例。",
    },
    {
        "strategy": "Rank50 auto frame IC",
        "factor": "signal_structural_reclaim",
        "horizons": (4,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank50 clean replication 复核：signal_structural_reclaim 直接对应页面中间变体 structural_reclaim，即 confirmed breakout retest reclaim 不叠加 higher-tf bias 的版本；独立复算一致。但该变体在 6bps 下跨资产 mean_total_return 约 -4.85%、false_reclaim 约 70.42%、no-trade 约 86.47%，同样属于审计后应保留的负例，而不是当前候选。",
    },
    {
        "strategy": "Rank63 auto frame IC",
        "factor": "signal_volume_gate_fib50_fail_sma200",
        "horizons": (1,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank63 clean replication 复核：signal_volume_gate_fib50_fail_sma200 直接对应页面主臂 +volume_gate+fib50_fail+sma200_filter，定义为 fib618 reclaim 叠加成交量过滤、fib50 fail exit 语义和 SMA200 顺风过滤；独立复算一致。但该主臂在 6bps 下跨资产 mean_total_return 仍约 -7.24%，hard verdict 仍是 park / evidence pool，所以只保留为 audit-only 对照。",
    },
    {
        "strategy": "Rank86 auto frame IC",
        "factor": "fib_retest_short_signal",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank86 clean replication 复核：fib_retest_short_signal 直接对应页面 setup `fib_retest_short` 的原始触发列，定义为 bearish EMA bias 下跌回 Fib382、且收盘跌回 Fib50 下方并带 volume gate；独立复算一致。该 setup 在 setup_summary 中明显强于 breakout_short / ema_psar_follow_short，但页面 hard verdict 仍只是 `P1 keep / worth one Light Stability Pack check`，且主结论依赖 pen_plus_atr sizing gate，因此这里只保留为 audit-only 的 setup-signal 参考。",
    },
    {
        "strategy": "Rank53 auto frame IC",
        "factor": "ema_pullback_long_signal",
        "horizons": (4,),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank53 clean replication 复核：ema_pullback_long_signal 对应 15m close-confirmed CHoCH 研究里的 long archetype 原始触发列，定义为 EMA 走强 + breakout continuation + volume gate；独立复算一致。需要注意，这一 raw long setup 的 4-bar horizon IC 为负，而页面里真正略有改善的是带 htf/sweep gate 的后续执行臂，因此该行更适合作为 audited negative setup 对照，不进入当前候选。",
    },
    {
        "strategy": "Rank51 auto frame IC",
        "factor": "signal_touch_reclaim_plus_breadth",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank51 clean replication 复核：signal_touch_reclaim_plus_breadth 直接对应页面主变体 `touch_reclaim_plus_breadth`，定义为 session VWAP touch + reclaim 再叠加 breadth gate；独立复算一致。审计结果显示该主变体在 1/4/16 bar horizon 下的横截面 IC 都为负，且 6bps 下跨资产 mean_total_return 约 -43.79%，因此它适合作为 audited negative example 展示，而不是当前候选。",
    },
    {
        "strategy": "Rank342 lane snapshot IC",
        "factor": "best_net_bps",
        "horizons": (1, 4, 16),
        "status": "reviewed",
        "display_role": "audit_only",
        "note": "已按 Rank342 same-chain cross-DEX lane snapshots 独立复核：先把每次 15m bucket 的 4 条预设 lane 对齐成横截面，以当前 `best_net_bps` 作为因子，再以同一 lane 未来 h 个 bucket 的 pocket contraction（`best_net_bps_t - best_net_bps_t+h`）作为 target 计算 Spearman IC。该定义与页面里的 `price-gap close` 叙事一致，且复算得到 1/4/16 bucket horizon 下均为正 IC；但 Rank342 页面 hard verdict 已明确是 observe only / 非主研发线，runner 也不是 fill replay，因此这里只保留为 audit-only 的结构观察证据，不进入当前候选主榜。",
    },
)

STORY_ARTIFACTS: tuple[dict[str, str], ...] = (
    {
        "strategy": "Rank32B slope-floor continuation",
        "family": "trend / continuation",
        "source": "reports/artifacts/scout_rank32b_slope_floor_continuation_15m/extended_history_1825d_asset_summary.csv",
        "report_href": "../factors/rank32b/report.html",
        "summary": "5 年级别长窗、跨资产、含执行/资金费/稳定性扩展，但该线已因 future/lookahead audit 下线；适合作为审计和研究纪律样例。",
    },
    {
        "strategy": "Rank29 trendline breakout navigator",
        "family": "structure breakout",
        "source": "reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/overall_summary.csv",
        "report_href": "../factors/scout_rank29_trendline_breakout_navigator_15m/report.html",
        "summary": "保留负例和 blocker：breakout 不是只要有图形就做，必须能通过 false-break 和 out-of-sample 检查。",
    },
    {
        "strategy": "Rank213 largecap xs jump veto",
        "family": "cross-sectional / jump-veto",
        "source": "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_formal_threeway_backtest_summary.json",
        "report_href": "../factors/rank213/report.html",
        "summary": "保留为 evidence map / causality audit 样例：旧 frozen30 结果不能再当滚动 Top30 长历史证明，monthly-volume causal 后明显变弱。",
    },
    {
        "strategy": "Rank154 young funding stat-arb",
        "family": "funding / cross-section",
        "source": "reports/artifacts/rank154b_young_funding_backtest/rank154b_funding_ic_summary.csv",
        "report_href": "../factors/paper_rank154_crypto_stat_arb_runner/report.html",
        "summary": "保留为 funding 类 postmortem / archive 样例：Rank154 原策略 failed release candidate，154b 有研究价值但不是净 alpha。",
    },
)

EVIDENCE_ITEMS: tuple[dict[str, str], ...] = (
    {
        "strategy": "Rank32B global live",
        "status": "live_disabled_after_bias_audit",
        "family": "trend / continuation",
        "report_href": "../factors/rank32b_global_live/report.html",
        "chart": "rank32b_shadow_180d_cumpnl.png",
        "primary_artifact": "reports/artifacts/rank32b_global_live/live_vs_shadow_summary.json",
        "curve_artifact": "reports/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_180d.csv",
        "note": "曾上 global live；当前 live_status 明确记录因 preview_unclosed_15m/lookahead audit 停用，适合展示研究纪律和下线机制。",
    },
    {
        "strategy": "Rank154 crypto stat-arb",
        "status": "archived_failed_release_candidate",
        "family": "funding / cross-section",
        "report_href": "../factors/paper_rank154_crypto_stat_arb_runner/report.html",
        "chart": "rank154_paper_equity.png",
        "primary_artifact": "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_status.csv",
        "curve_artifact": "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_equity_curve.csv",
        "note": "已由 RANK154_ARCHIVE_CLOSEOUT 收口：旧 paper runner/历史正收益只保留为证据，不代表当前 release candidate。",
    },
    {
        "strategy": "Rank213 largecap xs jump veto",
        "status": "causality_audit_archived_canary",
        "family": "cross-sectional / jump-veto",
        "report_href": "../factors/rank213/report.html",
        "chart": "rank213_threeway_backtest.png",
        "primary_artifact": "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_formal_threeway_backtest_summary.json",
        "curve_artifact": "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_long_history_with_funding_yearly.csv",
        "note": "evidence map 明确：旧 frozen30 结果有选池/幸存者偏差风险；monthly-volume causal 后明显变弱，age90 live canary 已停止归档。",
    },
    {
        "strategy": "Manual narrow paper lanes",
        "status": "P3_narrow_paper_pilot",
        "family": "paper pilot portfolio",
        "report_href": "../factors/manual_narrow_paper_lanes/report.html",
        "chart": "",
        "primary_artifact": "reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv",
        "curve_artifact": "reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv",
        "note": "多个 rank 的窄 paper pilot 状态表，展示哪些候选仍在跟踪、哪些有 open position。",
    },
    {
        "strategy": "Rank29 trendline navigator",
        "status": "paper/shadow plus negative controls",
        "family": "structure breakout",
        "report_href": "../factors/scout_rank29_trendline_breakout_navigator_15m/report.html",
        "chart": "",
        "primary_artifact": "reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/overall_summary.csv",
        "curve_artifact": "reports/artifacts/rank29_trigger_tf_monthly/monthly_by_trigger_tf_6bps.csv",
        "note": "保留 long-window、no-overlap honesty、monitoring board，用来说明并非所有 rank 都被包装成正例。",
    },
)

KEY_RANK_PLAYBOOK: tuple[dict[str, str], ...] = (
    {
        "rank": "Rank151",
        "family": "trend/momentum/breakout",
        "status": "paper runner / launch admission",
        "definition": "EWMAC breakout band-pass gate，把趋势突破限制在特定波段和 admission bar，避免无条件追突破。",
        "evidence": "paper runner page、launch admission bar、artifact status、对应回测报告。",
        "talk_track": "适合作为正在 paper 的中间阶段例子：已经从 clean replication 推到 runner，但仍要等待连续性和成本后表现。",
        "href": "../factors/paper_rank151_breakout_bandpass_gate/report.html",
    },
    {
        "rank": "Rank29",
        "family": "structure breakout + risk/execution",
        "status": "retired live / paper-shadow 对照 / negative control",
        "definition": "趋势线突破导航器，关注 trigger timeframe、false break、replay-vs-paper-vs-shadow 差异和 gate 条件。",
        "evidence": "shadow dashboard、monitoring hub、gate live debug、trigger timeframe monthly、narrow paper monitoring board。",
        "talk_track": "这是负例/纪律样例：不是所有 rank 都包装成正例，失败或下线同样纳入目录，说明如何识别不可上线或需退场的研究。",
        "href": "../factors/scout_rank29_trendline_breakout_navigator_15m/report.html",
    },
    {
        "rank": "Rank154",
        "family": "funding/basis/carry + cross-section stat-arb",
        "status": "已归档：failed release candidate；154b 仅保留 research lead，不进 paper lane",
        "definition": "原组合使用 funding、10d momentum、20d high breakout 的日频横截面打分；154b 聚焦 young coin high funding continuation。",
        "evidence": "RANK154_ARCHIVE_CLOSEOUT、postmortem IC、young funding strict backtest、funding IC summary。",
        "talk_track": "不是当前主线成果。它适合说明 funding 因子如何做 postmortem：原策略 long-history gate 失败，combined IC 接近 0；154b price IC 有一点信号，但 after-funding/after-cost 不是净 alpha。",
        "href": "../factors/paper_rank154_crypto_stat_arb_runner/report.html",
    },
    {
        "rank": "Rank213",
        "family": "cross-sectional + universe causality audit",
        "status": "旧 frozen30 叙事降级；age90 live canary 已停止归档",
        "definition": "largecap 横截面 momentum / jump-veto / gate 系列；必须区分 frozen30 运行口径、monthly-volume causal 历史口径和 live audit 口径。",
        "evidence": "RANK213_EVIDENCE_MAP、monthly-volume causal rebuild、archive close-out、live-vs-backtest checklist。",
        "talk_track": "不是当前可包装的正例主线。它适合说明 universe selection causality：旧 frozen30 看起来更强，但 monthly-volume causal 选池后显著变弱；任何展示都必须写清楚它是审计/候选研究，不是已过关 alpha。",
        "href": "../factors/rank213/report.html",
    },
    {
        "rank": "Rank32B",
        "family": "trend/momentum/breakout",
        "status": "已因 future/lookahead audit 下线，不能作为当前有效 alpha 排在最前",
        "definition": "15m 执行层叠加 1h EMA slope floor；历史 IC/回测只作为审计材料保留，不再按当前可上线候选解读。",
        "evidence": "global live/live-like shadow、live parity universe、180d cumulative PnL 图、live_status 中的 STOPPED 记录。",
        "talk_track": "这是研究纪律案例：曾经进入 live，但审计确认 preview_unclosed_15m/lookahead 风险后主动停用。页面保留它，是为了说明下线机制和负例透明度，而不是把它包装成当前主成果。",
        "href": "../factors/rank32b/report.html",
    },
)

COMPLETE_RESEARCH_SHOWCASE: tuple[dict[str, object], ...] = (
    {
        "rank": "Rank154",
        "priority": 1,
        "family": "funding/basis/carry + cross-section stat-arb",
        "status": "archived / failed release candidate / strong postmortem",
        "why_front": "这条线最适合作为“完整做过、最后诚实归档”的样例：定义、日频横截面、IC、成本、postmortem、154b 衍生研究都比较完整。",
        "coverage": {
            "def": "Y",
            "clean": "Y",
            "align": "Y",
            "anti_lookahead": "Y",
            "ic": "Y",
            "groups": "Y",
            "cost": "Y",
            "oos": "Y",
            "exposure": "Y",
            "memo": "Y",
        },
        "memo": "从原始策略到 close-out、再到 154b young funding strict backtest，比较像一套完整研究 memo + postmortem 包。",
        "href": "../factors/paper_rank154_crypto_stat_arb_runner/report.html",
    },
    {
        "rank": "Rank213",
        "priority": 2,
        "family": "cross-sectional + universe causality audit",
        "status": "archived / causality audit / canary close-out",
        "why_front": "这条线最大的价值是把选池因果性、frozen30 幸存者偏差、causal rebuild 和 live close-out 串成了一套完整反证过程。",
        "coverage": {
            "def": "Y",
            "clean": "Y",
            "align": "Y",
            "anti_lookahead": "Y",
            "ic": "P",
            "groups": "Y",
            "cost": "Y",
            "oos": "Y",
            "exposure": "P",
            "memo": "Y",
        },
        "memo": "适合作为 universe selection causality 的完整研究 memo：不是结果最好，但研究方法很完整。",
        "href": "../factors/rank213/report.html",
    },
    {
        "rank": "Rank32B",
        "priority": 3,
        "family": "trend/momentum/breakout",
        "status": "archived / future-lookahead audit",
        "why_front": "它是“做到实盘，再被未来函数审计打回去”的完整治理样例，最能体现时间对齐、future audit 和下线机制。",
        "coverage": {
            "def": "Y",
            "clean": "P",
            "align": "Y",
            "anti_lookahead": "Y",
            "ic": "Y",
            "groups": "Y",
            "cost": "Y",
            "oos": "Y",
            "exposure": "N",
            "memo": "Y",
        },
        "memo": "更像 execution + governance memo，不是当前 alpha 成果，但非常适合放在完整工作样例前排。",
        "href": "../factors/rank32b/report.html",
    },
    {
        "rank": "Rank151",
        "priority": 4,
        "family": "trend/momentum/breakout",
        "status": "active / launch admission / paper runner",
        "why_front": "这条线是当前 active 里最完整的一条：source digest、定义修正、band-pass 逻辑、rolling split、launch admission、runner 全都齐。",
        "coverage": {
            "def": "Y",
            "clean": "P",
            "align": "Y",
            "anti_lookahead": "Y",
            "ic": "P",
            "groups": "Y",
            "cost": "Y",
            "oos": "Y",
            "exposure": "N",
            "memo": "Y",
        },
        "memo": "它不是经典单调 IC 因子，但作为“来源拆解 + 研究翻译 + paper runner”的完整样例已经很成熟。",
        "href": "../factors/paper_rank151_breakout_bandpass_gate/report.html",
    },
    {
        "rank": "Rank29",
        "priority": 5,
        "family": "structure breakout + risk/execution",
        "status": "retired live / shadow / negative controls",
        "why_front": "如果读者想看 execution、false break、gate、shadow/live debug 和负例控制，Rank29 是最完整的操作型样例之一。",
        "coverage": {
            "def": "Y",
            "clean": "P",
            "align": "Y",
            "anti_lookahead": "Y",
            "ic": "N",
            "groups": "Y",
            "cost": "Y",
            "oos": "Y",
            "exposure": "N",
            "memo": "Y",
        },
        "memo": "更偏 execution memo 和 negative-control 样例，不靠 IC，而靠 replay/paper/shadow/live 一致性审计。",
        "href": "../factors/scout_rank29_trendline_breakout_navigator_15m/report.html",
    },
)

ACTIVE_OBSERVATION_IC_AUDIT_OVERRIDES: dict[str, dict[str, str]] = {
    "rank151": {
        "structure_verdict": "runner status only / no factor frame",
        "audit_note": "当前 artifact 只有 runner/status/state 三类运行证据，没有可复算的 bar-level feature frame 或 IC summary。现阶段适合展示 paper 连续性，不适合发布横截面 IC。",
        "next_step": "若后续要发布 IC，需要补出按 timestamp-asset 对齐的 feature frame，并明确主信号列、future return horizon 与成本口径。",
    },
    "rank183": {
        "structure_verdict": "single-pair relative value / not cross-sectional",
        "audit_note": "现有产物是 cbETH-ETH pair series、closed trades 和 runner status，核心对象是一对价差，不是同一时点多资产横截面排序；按本页标准不发布横截面 IC。",
        "next_step": "若要增加可比统计，应单列 pair spread 的时间序列评估或 markout，不与横截面 IC 主榜混排。",
    },
    "rank186": {
        "structure_verdict": "event-window runner / not factor frame",
        "audit_note": "当前是 CME expiry 事件表、cache event windows 和 closed trades。它是事件窗口执行研究，不是 timestamp-asset bar frame，因此不发布横截面 IC。",
        "next_step": "保留事件收益、分月表现和回测报告；如要做因子比较，应先构造统一事件特征表和事件后收益 target。",
    },
    "rank187": {
        "structure_verdict": "snapshot plus trades / no bar-level xs frame",
        "audit_note": "现有 snapshot 只记录当下候选路径形态和未来最大涨幅预测，缺少同一时点多资产横截面对齐的历史 factor frame；closed trades 也不能直接替代 IC。",
        "next_step": "若要审 IC，需要补历史日内 shape feature panel，并把预测列与真实 future return 在 as-of 口径下对齐。",
    },
    "rank200": {
        "structure_verdict": "single-asset frame with target only",
        "audit_note": "rank200_recent_hourly_frame 只有 BTC 单资产，且数值列实质上只有未来收益 ret_1h；没有可审计的独立因子列，也没有至少 3 个资产的横截面，因此不发布 IC。",
        "next_step": "如果保留为单资产时钟策略，应展示 schedule、closed trades 和 hourly markout；若想进入 IC 主榜，需要扩成多资产同口径时钟因子面板。",
    },
    "rank201": {
        "structure_verdict": "schedule and markout evidence / no factor frame",
        "audit_note": "当前产物是 daily schedule、recent markouts、closed trades 和 status。它能证明 runner 行为和收益样本，但没有正式 bar-level feature frame，不能发布横截面 IC。",
        "next_step": "若后续要比较 IC，应把 symbol-hour sleeve 信号整理成 timestamp-asset 面板，并明确 target_side 到 future return 的映射。",
    },
    "rank229": {
        "structure_verdict": "trade log / not bar-level frame",
        "audit_note": "rank229_current_signal_frame 记录的是 entry/exit 与 net_bps 的已实现交易样本，而不是同一时点的历史横截面因子值；因此不把它当 IC 口径发布。",
        "next_step": "如要做 IC，需要生成 abnormal-day 信号在每个 as-of 时点的历史特征表，并与后续收益做严格时间对齐。",
    },
    "rank342": {
        "structure_verdict": "lane snapshot / no future target join",
        "audit_note": "current_lane_frame 和 lane_snapshots 展示的是跨链价差机会快照，包含 gross/net bps 与流动性约束，但没有和未来 realized close/markout 联表；这类 lane snapshot 不是 IC frame。",
        "next_step": "若要发布 IC，需要保留历史 as-of lane panel，并为每个 lane 计算后续 markout 或成交后净收益 target，再做横向相关性审计。",
    },
    "rank368": {
        "structure_verdict": "launch-check evidence / no time-series factor panel",
        "audit_note": "当前只有 launch checks、status 和 frozen spec，说明研究还在上线前检查阶段，没有历史 factor panel 或 IC artifact。",
        "next_step": "保持为 launch-readiness 证据；若进入正式研究比较，再补 funding extreme 的历史特征面板和 future return target。",
    },
    "rank370": {
        "structure_verdict": "surface snapshot / no realized target history",
        "audit_note": "rank370_current_signal_frame 只有当下几档 strike 的 surface mispricing 快照，缺少跨时间、跨标的的历史 realized target；因此不能按 IC 口径发布。",
        "next_step": "若要审 IC，需要沉淀连续 surface snapshots，并为每个 snapshot 连接未来价格或成交后 markout 作为 target。",
    },
    "rank32c": {
        "structure_verdict": "execution gate / governance evidence",
        "audit_note": "rank32c_pre_live_gate 主要是 runner_status、release decision、live_vs_shadow 和 replay trades，属于执行/治理层证据，不是因子研究 frame。",
        "next_step": "继续展示 live gate 和 release audit；不建议强行补 IC，除非后续把其底层 alpha 信号独立拆出并形成 factor frame。",
    },
    "manual_narrow_paper_lanes": {
        "structure_verdict": "portfolio board / mixed multi-rank status",
        "audit_note": "Manual narrow paper lanes 是多 rank 的组合状态板，行里混合 asset、signal_family 和 open position 状态，不对应单一因子定义，因此不能发布单一 IC。",
        "next_step": "它应继续作为 P3 窄组合 pilot 监控板；若要比较 IC，应回到各底层 rank 的独立因子面板逐条审计。",
    },
}


def ensure_dirs() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    ALIAS_ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    ALIAS_SITE_DIR.mkdir(parents=True, exist_ok=True)


RANK_RE = re.compile(r"rank(\d+[a-z]?)", re.IGNORECASE)
EXCLUDE_FACTOR_COLUMNS = {
    "timestamp",
    "ts",
    "date",
    "datetime",
    "asset",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "quote_volume",
    "signal_idx",
    "entry_idx",
    "exit_idx",
    "entry_time",
    "exit_time",
    "entry_price",
    "exit_price",
}
FACTOR_HINTS = (
    "signal",
    "score",
    "z",
    "slope",
    "spread",
    "basis",
    "funding",
    "oi",
    "rsi",
    "atr",
    "polarity",
    "breadth",
    "ratio",
    "rank",
    "beta",
    "skew",
    "veto",
    "gate",
    "state",
    "bias",
    "crowd",
    "ret_",
    "imbalance",
    "efficiency",
    "winner",
    "trapped",
    "turnover",
    "pfe",
    "rsrs",
    "ema",
    "psar",
    "fib",
    "donchian",
    "vwap",
)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def signed_series(df: pd.DataFrame, name: str) -> pd.Series | None:
    zeros = pd.Series(0.0, index=df.index)
    if name == "signed_slope_floor_signal":
        return df.get("slope_floor_long_signal", zeros).astype(float) - df.get("slope_floor_short_signal", zeros).astype(float)
    if name == "signed_clock_signal":
        return (
            df.get("ema_psar_long_signal", zeros).astype(float)
            + df.get("fib_retest_long_signal", zeros).astype(float)
            - df.get("breakout_short_signal", zeros).astype(float)
        )
    if name == "signed_lvn_signal":
        return df.get("ema_pullback_long_signal", zeros).astype(float) - df.get("breakdown_reclaim_short_signal", zeros).astype(float)
    if name == "signed_rsrs_signal":
        return (
            df.get("ema_psar_long_signal", zeros).astype(float)
            + df.get("fib_retest_long_signal", zeros).astype(float)
            - df.get("breakout_short_signal", zeros).astype(float)
        )
    if name == "signed_consensus_signal":
        if "signal_side" in df.columns:
            side = df["signal_side"].astype(str).str.lower()
            return np.where(side.str.contains("long"), 1.0, np.where(side.str.contains("short"), -1.0, 0.0))
        return df.get("direction", zeros).astype(float)
    if name in df.columns:
        return pd.to_numeric(df[name], errors="coerce")
    return None


def rank_label_from_name(name: str) -> str:
    m = RANK_RE.search(name)
    if not m:
        return name.replace("_", " ")
    return f"Rank{m.group(1).upper()}"


def rank_id_from_text(text: str) -> str:
    m = RANK_RE.search(text or "")
    return f"rank{m.group(1).lower()}" if m else ""


def load_rank_registry() -> dict[str, dict[str, str]]:
    if not REGISTRY_TABLE.exists():
        return {}
    try:
        df = pd.read_csv(REGISTRY_TABLE).fillna("")
    except Exception:
        return {}
    out: dict[str, dict[str, str]] = {}
    for _, row in df.iterrows():
        rank_id = str(row.get("rank", "")).strip().lower()
        if rank_id:
            out[rank_id] = {str(k): str(v) for k, v in row.items()}
    return out


def family_from_registry_theme(theme: str, baseline: str = "", increment: str = "", role: str = "") -> str:
    text = f"{theme} {baseline} {increment} {role}".lower()
    if "趋势" in text or "trend" in text or "supertrend" in text or "continuation" in text:
        return "trend/momentum/breakout"
    if "均值" in text or "pairs" in text or "fair-value" in text or "reversal" in text or "cointegration" in text or "price-gap" in text:
        return "mean-reversion/stat-arb"
    if "截面" in text or "xs" in text or "rotation" in text or "lottery" in text or "pairbook" in text:
        return "cross-sectional"
    if "事件" in text or "时钟" in text or "季节" in text or "fomc" in text or "cme" in text or "weekday" in text:
        return "event/clock/session"
    if "波动" in text or "state" in text or "vol" in text or "basis state" in text:
        return "regime/risk-filter"
    if "风险" in text or "filter" in text or "veto" in text or "gate" in text or "异常日" in text:
        return "regime/risk-filter"
    if "deployment" in text or "routing" in text or "exit" in text or "执行" in text:
        return "risk/execution"
    if "跨市场" in text or "联动" in text:
        return "regime/risk-filter"
    return "meta-review/governance"


def strip_tags(text: str) -> str:
    return WS_RE.sub(" ", TAG_RE.sub("", text or "")).strip()


def extract_html_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    for regex in (TITLE_RE, H1_RE):
        m = regex.search(text)
        if m:
            title = strip_tags(m.group(1))
            if title:
                return title
    return path.parent.name.replace("_", " ").replace("-", " ")


def classify_source_type(rel: str) -> str:
    low = rel.lower()
    if "rank_registry" in low:
        return "registry_entry"
    if low.startswith("paper/") or "/paper_rank" in low or "paper_rank" in low:
        return "paper"
    if "live" in low:
        return "live_or_monitor"
    if "shadow" in low:
        return "shadow"
    if "/scout_rank" in low or low.startswith("factors/scout_rank"):
        return "scout_research"
    if low.startswith("factors/rank"):
        return "rank_hub"
    return "rank_related"


def classify_status(rel: str, title: str) -> str:
    text = f"{rel} {title}".lower()
    if any(k in text for k in ("archive", "close-out", "closeout", "postmortem", "retired", "failed release", "收口", "归档", "失败归因")):
        return "archived/audit"
    if "decommission" in text or "disabled" in text or "retirement" in text:
        return "disabled/decommissioned"
    if "live" in text and "checklist" not in text:
        return "live/monitor"
    if "paper" in text:
        return "paper"
    if "shadow" in text:
        return "shadow"
    if "canary" in text:
        return "canary"
    if "registry" in text:
        return "registry"
    if "stability" in text or "backtest" in text or "validation" in text:
        return "research_validation"
    return "research_report"


def classify_family(rel: str, title: str, registry_row: dict[str, str] | None = None) -> str:
    if registry_row:
        return family_from_registry_theme(
            registry_row.get("mother_theme", ""),
            registry_row.get("challenge_baseline", ""),
            registry_row.get("unique_increment", ""),
            registry_row.get("role", ""),
        )
    text = f"{rel} {title}".lower()
    if "rank154" in text:
        return "funding/basis/carry"
    if "registry" in text or any(k in text for k in ("overview", "hub", "archive", "close-out", "postmortem", "evidence map", "version", "architecture", "decomposition", "validation", "long history", "status", "transparency", "decision", "diagnostics", "stability", "review", "follow-up", "综合验证", "归档", "总览", "版本", "架构", "审计", "状态", "透明", "冻结决策", "诊断", "审阅")):
        return "meta-review/governance"
    if any(k in text for k in ("funding", "basis", "carry", "crossvenue", "netcarry", "surface", "mispricing")):
        return "funding/basis/carry"
    if any(k in text for k in ("cointegration", "pairs", "spread", "statarb", "stat_arb", "mean", "reversion", "cbeth")):
        return "mean-reversion/stat-arb"
    if any(k in text for k in ("orderbook", "imbalance", "micro", "liquidity", "book", "ofi", "oi quadrant", "oi_quadrant", "oi router", "oi_router", "liquidation", "liqshock", "crowded", "toptrader", "smartmoney", "fvg", "volume delta", "clv", "leader")):
        return "microstructure/liquidity"
    if any(k in text for k in ("trend", "momentum", "slope", "ema", "breakout", "continuation", "donchian", "psar", "drift", "impulse", "ichimoku", "cloud", "squeeze", "adx", "tsmom", "ttm", "roc", "rearm", "rsrs", "supertrend", "hot-coin", "hot_fee", "rank32b", "32b", "proxy")):
        return "trend/momentum/breakout"
    if any(k in text for k in ("clock", "session", "weekday", "hour", "event", "cme", "expiry", "news", "abnormal day", "abnormal_day", "dailyveto", "fomc", "intraday sign", "timecycle", "time cycle", "jump", "follower", "contagion")):
        return "event/clock/session"
    if any(k in text for k in ("xs", "cross", "breadth", "relative", "strength", "samechain", "newlisting", "alt btc", "semivariance", "commonality")):
        return "cross-sectional"
    if any(k in text for k in ("risk", "dd", "drawdown", "execution", "slippage", "capacity", "live", "canary", "shadow", "fee", "vip0", "exec_tf", "alignment")):
        return "risk/execution"
    if any(k in text for k in ("fib", "vwap", "retest", "reclaim", "range", "structure", "swing", "path", "pullback", "overshoot", "envelope", "bounce", "fade", "wick", "zone", "choch", "lvn", "poc", "body", "retracement", "candle", "chanlun", "chip", "poc", "premium discount", "block", "mitigation", "signflip", "back-inside", "sweep", "first-major-break", "base-age", "penetration", "handoff")):
        return "structure/retest"
    if any(k in text for k in ("volume", "dry-down", "drydown", "turnover", "participation")):
        return "volume/participation"
    if any(k in text for k in ("regime", "matrix", "state", "chop", "gcr", "exhaustion", "stress", "vol", "realized-vol", "ivu", "uncertainty", "triple barrier", "no-trade", "phase gate", "atr delta")):
        return "regime/risk-filter"
    return "other"


def explain_rank_report(title: str, source_type: str, status: str, family: str, registry_row: dict[str, str] | None = None) -> str:
    family_text = {
        "funding/basis/carry": "围绕资金费率、basis 或 carry 的相对价值/拥挤度信号",
        "mean-reversion/stat-arb": "围绕价差、协整、残差或均值回复的统计套利信号",
        "microstructure/liquidity": "围绕订单簿、流动性、成交/盘口失衡的微观结构信号",
        "trend/momentum/breakout": "围绕趋势、动量、突破或延续确认的方向性信号",
        "event/clock/session": "围绕事件窗口、交易时钟或 session 条件的条件收益信号",
        "cross-sectional": "围绕横截面排序、相对强弱或多资产分层的选币/组合信号",
        "risk/execution": "围绕执行、容量、滑点、风控或 live/paper 差异的治理层证据",
        "structure/retest": "围绕结构位、回踩、reclaim、VWAP/Fib/区间行为的形态信号",
        "regime/risk-filter": "围绕波动状态、风险过滤、veto/gate 或不交易条件的状态层信号",
        "volume/participation": "围绕成交量、参与度、turnover 或 dry-down 的交易活跃度信号",
        "meta-review/governance": "围绕版本、归档、稳定性审计、registry 或研究治理的证据页",
        "other": "归入其他研究线，保留为可追溯报告入口",
    }.get(family, "保留为可追溯报告入口")
    status_text = {
        "live/monitor": "已进入 live/monitor 链路，展示重点看实盘状态、告警和 live-vs-shadow 差异",
        "paper": "处于 paper runner 或 paper 报告状态，展示重点看收益曲线、持仓/交易流水和晋级条件",
        "shadow": "处于 shadow 验证状态，展示重点看和 live/backtest 的偏差",
        "canary": "处于 canary 或准实盘验证状态，展示重点看守门条件和风险控制",
        "research_validation": "处于研究验证/稳定性检查状态，展示重点看 OOS、成本、时间稳定性和负例",
        "research_report": "处于研究报告状态，展示重点看 idea 来源、最小复现和下一步 admission",
        "registry": "注册表入口，用来解释该 rank 在 P2/P3 管线中的角色",
        "disabled/decommissioned": "已下线或归档，展示重点讲诚实审计和为什么停止",
        "archived/audit": "已归档或作为审计/postmortem 证据保留，展示重点是失败原因、口径风险和停止规则",
    }.get(status, "保留为研究证据入口")
    if registry_row:
        stage = registry_row.get("stage", "")
        role = registry_row.get("role", "")
        baseline = registry_row.get("challenge_baseline", "")
        increment = registry_row.get("unique_increment", "")
        next_action = registry_row.get("next_action", "")
        action_text = status_text if status == "archived/audit" else (next_action or status_text)
        return (
            f"{title}：P2/P3 registry 中的 {stage} 条目，角色={role or '-'}；"
            f"母题/基线={baseline or registry_row.get('mother_theme', '-')}; 独特增量={increment or '-'}。"
            f"归类为 {family}；展示重点是它在研究管线中的位置、当前状态和下一步：{action_text}。"
        )
    return f"{title}：{family_text}；当前归类为 {status}，{status_text}。"


def artifact_hits_for_rank(rank_id: str) -> tuple[int, str]:
    if not rank_id:
        return 0, ""
    hits: list[str] = []
    for p in (ROOT / "reports" / "artifacts").glob(f"**/{rank_id}*"):
        if p.is_file():
            hits.append(p.relative_to(ROOT).as_posix())
            if len(hits) >= 5:
                break
    return len(hits), "; ".join(hits)


def discover_rank_report_catalog() -> pd.DataFrame:
    site_root = ROOT / "reports" / "site"
    registry = load_rank_registry()
    files: list[Path] = []
    for base in (site_root / "factors", site_root / "paper"):
        if not base.exists():
            continue
        for path in base.rglob("*.html"):
            rel = path.relative_to(site_root).as_posix()
            if "rank" not in rel.lower():
                continue
            if path.name != "report.html" and not path.name.startswith("rank") and "rank" not in path.parent.name.lower():
                continue
            files.append(path)
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in sorted(files):
        rel = path.relative_to(site_root).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        title = extract_html_title(path)
        rank_id = rank_id_from_text(rel) or rank_id_from_text(title)
        registry_row = registry.get(rank_id.lower()) if rank_id else None
        hit_count, sample_hits = artifact_hits_for_rank(rank_id)
        source_type = classify_source_type(rel)
        status = classify_status(rel, title)
        family = classify_family(rel, title, registry_row)
        rows.append(
            {
                "rank_id": rank_id or "unranked",
                "title": title,
                "source_type": source_type,
                "status": status,
                "family": family,
                "registry_stage": registry_row.get("stage", "") if registry_row else "",
                "registry_role": registry_row.get("role", "") if registry_row else "",
                "registry_theme": registry_row.get("mother_theme", "") if registry_row else "",
                "registry_increment": registry_row.get("unique_increment", "") if registry_row else "",
                "report_href": "../" + rel,
                "rel_path": rel,
                "artifact_hit_count_sampled": hit_count,
                "artifact_examples": sample_hits,
                "research_note": explain_rank_report(title, source_type, status, family, registry_row),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        order = {"live/monitor": 0, "paper": 1, "shadow": 2, "canary": 3, "research_validation": 4, "research_report": 5, "registry": 6}
        df["_status_order"] = df["status"].map(order).fillna(9)
        df = df.sort_values(["_status_order", "rank_id", "rel_path"]).drop(columns=["_status_order"])
    return df


def attach_ic_summary_to_catalog(catalog_df: pd.DataFrame, ic_df: pd.DataFrame) -> pd.DataFrame:
    if catalog_df.empty or ic_df.empty:
        return catalog_df
    work = normalize_ic_schema(ic_df)
    status = work.get("ic_review_status", pd.Series("", index=work.index)).fillna("").astype(str)
    work = work[status.eq("reviewed")].copy()
    if work.empty:
        return catalog_df
    work["abs_ir"] = pd.to_numeric(work["ir"], errors="coerce").abs()
    work["abs_ic"] = pd.to_numeric(work["ic_mean"], errors="coerce").abs()
    work["rank_id"] = work["report_href"].map(rank_id_from_text)
    best = (
        work.dropna(subset=["rank_id"])
        .sort_values(["abs_ir", "abs_ic", "ic_observations"], ascending=False)
        .drop_duplicates("rank_id")
    )
    best = best[["rank_id", "factor", "horizon_bars", "ic_mean", "ir", "ic_observations", "assets", "source"]].rename(
        columns={
            "factor": "best_ic_factor",
            "horizon_bars": "best_ic_horizon_bars",
            "ic_mean": "best_ic_mean",
            "ir": "best_ir",
            "ic_observations": "best_ic_observations",
            "assets": "best_ic_assets",
            "source": "best_ic_source",
        }
    )
    out = catalog_df.merge(best, how="left", on="rank_id")
    return out


def normalize_ic_schema(ic_df: pd.DataFrame) -> pd.DataFrame:
    """Keep reused/legacy IC CSVs from leaking into formal display without review metadata."""
    if ic_df.empty:
        return ic_df.copy()
    out = ic_df.copy()
    if "ic_review_status" not in out.columns:
        out["ic_review_status"] = "needs_strategy_review"
    out["ic_review_status"] = out["ic_review_status"].fillna("").astype(str).replace("", "needs_strategy_review")
    if "ic_review_note" not in out.columns:
        out["ic_review_note"] = "Legacy/reused IC row; not audited for current display."
    out["ic_review_note"] = out["ic_review_note"].fillna("").astype(str)
    missing_note = out["ic_review_note"].eq("")
    out.loc[missing_note, "ic_review_note"] = "未完成逐策略口径审计；不进入正式 IC/IR 主榜。"
    if "ic_display_role" not in out.columns:
        out["ic_display_role"] = ""
    out["ic_display_role"] = out["ic_display_role"].fillna("").astype(str)
    for col in ("ic_mean", "ic_median", "ic_std", "ir", "positive_rate", "ic_observations", "assets", "horizon_bars"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def apply_ic_review_rules(ic_df: pd.DataFrame) -> pd.DataFrame:
    if ic_df.empty:
        return normalize_ic_schema(ic_df)
    out = normalize_ic_schema(ic_df)
    strategy_col = out.get("strategy", pd.Series("", index=out.index)).fillna("").astype(str)
    factor_col = out.get("factor", pd.Series("", index=out.index)).fillna("").astype(str)
    horizon_col = pd.to_numeric(out.get("horizon_bars", pd.Series(np.nan, index=out.index)), errors="coerce")
    for rule in IC_REVIEW_RULES:
        horizons = tuple(int(h) for h in rule.get("horizons", ()))
        mask = strategy_col.eq(str(rule["strategy"])) & factor_col.eq(str(rule["factor"]))
        if horizons:
            mask &= horizon_col.isin(horizons)
        if not mask.any():
            continue
        out.loc[mask, "ic_review_status"] = str(rule.get("status", "reviewed"))
        out.loc[mask, "ic_review_note"] = str(rule.get("note", ""))
        out.loc[mask, "ic_display_role"] = str(rule.get("display_role", ""))
    return out


def report_href_for_artifact_dir(name: str) -> str:
    candidates = [
        ROOT / "reports" / "site" / "factors" / name / "report.html",
    ]
    m = RANK_RE.search(name)
    if m:
        rank_dir = f"rank{m.group(1).lower()}"
        candidates.extend(
            [
                ROOT / "reports" / "site" / "factors" / rank_dir / "report.html",
                ROOT / "reports" / "site" / "factors" / f"{rank_dir}_live" / "report.html",
                ROOT / "reports" / "site" / "factors" / "rank_registry_p3_p2_entries" / rank_dir / "report.html",
                ROOT / "reports" / "site" / "paper" / f"{rank_dir}.html",
            ]
        )
        if not rank_dir.endswith(tuple("abcdefghijklmnopqrstuvwxyz")):
            rank_prefix = f"paper_{rank_dir}_"
            paper_dirs = sorted((ROOT / "reports" / "site" / "factors").glob(f"{rank_prefix}*/report.html"))
            scout_dirs = sorted((ROOT / "reports" / "site" / "factors").glob(f"scout_{rank_dir}_*/report.html"))
            candidates.extend(paper_dirs + scout_dirs)
    for path in candidates:
        if path.exists():
            return "../" + path.relative_to(ROOT / "reports" / "site").as_posix()
    return "../index.html"


def frame_files_for_dir(path: Path) -> list[Path]:
    files = []
    for p in path.iterdir():
        if not p.is_file() or p.suffix.lower() != ".csv":
            continue
        n = p.name.lower()
        if "cache" in n or "trade" in n or "summary" in n or "status" in n:
            continue
        if n.endswith("_frame.csv") or n.endswith("_feature_frame.csv") or n.startswith("frame_"):
            files.append(p)
    return sorted(files)


def choose_factor_columns(frame_files: list[Path], common_columns: set[str] | None = None, limit: int = 10) -> list[str]:
    common_columns = {c.lower() for c in (common_columns or set())}
    scores: dict[str, int] = {}
    for path in frame_files[:8]:
        try:
            header = pd.read_csv(path, nrows=0).columns
        except Exception:
            continue
        for col in header:
            c = str(col)
            low = c.lower()
            if low in EXCLUDE_FACTOR_COLUMNS or low.endswith("_time") or low.endswith("_ts") or "origin" in low:
                continue
            if low in common_columns:
                continue
            hint_score = sum(1 for hint in FACTOR_HINTS if hint in low)
            if hint_score <= 0:
                continue
            scores[c] = max(scores.get(c, 0), hint_score)
    ranked = sorted(scores, key=lambda c: (-scores[c], c.lower()))
    return ranked[:limit]


def diagnose_frame_files(frame_files: list[Path], common_columns: set[str] | None = None) -> dict[str, object]:
    if not frame_files:
        return {"status": "skip_no_frame_files", "assets": 0, "rows": 0, "usable_files": 0, "factors": []}
    total_rows = 0
    assets: set[str] = set()
    usable_files = 0
    has_time_close = False
    for path in frame_files[:20]:
        try:
            df = pd.read_csv(path, usecols=lambda c: True)
        except Exception:
            continue
        lower_cols = {str(c).lower(): c for c in df.columns}
        timestamp_col = lower_cols.get("timestamp") or lower_cols.get("ts")
        close_col = lower_cols.get("close")
        if timestamp_col is None or close_col is None:
            continue
        has_time_close = True
        usable_files += 1
        total_rows += len(df)
        asset_col = lower_cols.get("asset") or lower_cols.get("symbol")
        if asset_col is not None:
            vals = df[asset_col].dropna().astype(str).unique()
            assets.update(vals[:500])
        else:
            assets.add(path.stem.replace("_feature_frame", "").replace("_frame", "").upper())
    factors = choose_factor_columns(frame_files, common_columns=common_columns)
    if not has_time_close:
        status = "skip_not_bar_level_frame"
    elif len(assets) < 3:
        status = "skip_less_than_3_assets"
    elif not factors:
        status = "skip_no_factor_like_columns"
    else:
        status = "included"
    return {"status": status, "assets": len(assets), "rows": total_rows, "usable_files": usable_files, "factors": factors}


def common_auto_factor_columns(threshold: int = 3) -> set[str]:
    """Columns repeated across many scout artifacts are scaffold features, not rank-specific factors."""
    column_dirs: dict[str, set[str]] = {}
    for directory in sorted((ROOT / "reports" / "artifacts").iterdir()):
        if not directory.is_dir() or "rank" not in directory.name.lower():
            continue
        frame_files = frame_files_for_dir(directory)
        if not frame_files:
            continue
        seen: set[str] = set()
        for path in frame_files[:3]:
            try:
                header = pd.read_csv(path, nrows=0).columns
            except Exception:
                continue
            seen.update(str(c).lower() for c in header)
        for col in seen:
            column_dirs.setdefault(col, set()).add(directory.name)
    common = {col for col, dirs in column_dirs.items() if len(dirs) >= threshold}
    common.update(str(c).lower() for c in EXCLUDE_FACTOR_COLUMNS)
    return common


def discover_auto_factor_specs() -> tuple[list[FactorSpec], pd.DataFrame]:
    specs: list[FactorSpec] = []
    coverage: list[dict[str, object]] = []
    manual_dirs = {spec.artifact_dir for spec in FACTOR_SPECS}
    common_columns = common_auto_factor_columns()
    for path in sorted((ROOT / "reports" / "artifacts").iterdir()):
        if not path.is_dir() or path.name in manual_dirs:
            continue
        if "rank" not in path.name.lower():
            continue
        frame_files = frame_files_for_dir(path)
        diagnosis = diagnose_frame_files(frame_files, common_columns=common_columns)
        if diagnosis["status"] != "included":
            coverage.append(
                {
                    "artifact_dir": path.name,
                    "status": diagnosis["status"],
                    "frame_files": len(frame_files),
                    "usable_files": diagnosis.get("usable_files", 0),
                    "assets": diagnosis.get("assets", 0),
                    "rows": diagnosis.get("rows", 0),
                    "factor_count": len(diagnosis.get("factors", [])),
                    "factors": ",".join(diagnosis.get("factors", [])),
                }
            )
            continue
        factors = list(diagnosis["factors"])
        specs.append(
            FactorSpec(
                strategy=f"{rank_label_from_name(path.name)} auto frame IC",
                display=path.name.replace("_", " "),
                artifact_dir=path.name,
                frame_glob="*.csv",
                factors=tuple(factors),
                report_href=report_href_for_artifact_dir(path.name),
                thesis="自动从 frame/feature_frame CSV 抽取数值因子，按同一横截面 IC/IR 口径纳入总表。",
            )
        )
        coverage.append(
            {
                "artifact_dir": path.name,
                "status": "included",
                "frame_files": len(frame_files),
                "usable_files": diagnosis.get("usable_files", 0),
                "assets": diagnosis.get("assets", 0),
                "rows": diagnosis.get("rows", 0),
                "factor_count": len(factors),
                "factors": ",".join(factors),
            }
        )
    return specs, pd.DataFrame(coverage)


def load_factor_frame(spec: FactorSpec) -> pd.DataFrame:
    base = ROOT / "reports" / "artifacts" / spec.artifact_dir
    frames: list[pd.DataFrame] = []
    for path in sorted(base.glob(spec.frame_glob)):
        df = pd.read_csv(path)
        lower_cols = {str(c).lower(): c for c in df.columns}
        if "timestamp" not in df.columns and "ts" in lower_cols:
            df["timestamp"] = df[lower_cols["ts"]]
        if "timestamp" not in df.columns or "close" not in df.columns:
            continue
        if "asset" not in df.columns:
            df["asset"] = path.stem.replace("_feature_frame", "").replace("_frame", "").upper()
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df = df.dropna(subset=["timestamp", "asset", "close"]).sort_values(["asset", "timestamp"])
        keep = df[["timestamp", "asset", "close"]].copy()
        for factor in spec.factors:
            series = signed_series(df, factor)
            if series is not None:
                keep[factor] = pd.to_numeric(series, errors="coerce")
        frames.append(keep)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).sort_values(["asset", "timestamp"])


def cross_sectional_spearman(frame: pd.DataFrame, factor: str, target: str) -> pd.Series:
    """Vectorized per-timestamp Spearman IC across assets."""
    wide_factor = frame.pivot_table(index="timestamp", columns="asset", values=factor, aggfunc="last")
    wide_target = frame.pivot_table(index="timestamp", columns="asset", values=target, aggfunc="last")
    wide_factor, wide_target = wide_factor.align(wide_target, join="inner", axis=0)
    wide_factor, wide_target = wide_factor.align(wide_target, join="inner", axis=1)
    if wide_factor.empty or wide_factor.shape[1] < 3:
        return pd.Series(dtype=float)

    fr = wide_factor.rank(axis=1)
    tr = wide_target.rank(axis=1)
    valid = fr.notna() & tr.notna()
    n = valid.sum(axis=1)
    fr = fr.where(valid)
    tr = tr.where(valid)
    fr_centered = fr.sub(fr.mean(axis=1), axis=0)
    tr_centered = tr.sub(tr.mean(axis=1), axis=0)
    cov = (fr_centered * tr_centered).sum(axis=1)
    denom = np.sqrt((fr_centered.pow(2).sum(axis=1)) * (tr_centered.pow(2).sum(axis=1)))
    ic = cov / denom
    return ic.where(n >= 3).replace([np.inf, -np.inf], np.nan).dropna()


def compute_ic_rows(spec: FactorSpec, horizons: tuple[int, ...] = (1, 4, 16)) -> list[dict[str, object]]:
    frame = load_factor_frame(spec)
    if frame.empty:
        return []
    for h in horizons:
        frame[f"fwd_ret_{h}"] = frame.groupby("asset")["close"].shift(-h) / frame["close"] - 1.0

    rows: list[dict[str, object]] = []
    for factor in spec.factors:
        if factor not in frame.columns:
            continue
        factor_non_null = frame[factor].replace([np.inf, -np.inf], np.nan).dropna()
        if factor_non_null.empty or factor_non_null.nunique() < 2:
            continue
        for h in horizons:
            target = f"fwd_ret_{h}"
            ic = cross_sectional_spearman(frame, factor, target)
            if ic.empty:
                continue
            std = float(ic.std(ddof=1)) if len(ic) > 1 else np.nan
            ic_mean = float(ic.mean())
            rows.append(
                {
                    "strategy": spec.strategy,
                    "display": spec.display,
                    "factor": factor,
                    "horizon_bars": h,
                    "ic_mean": ic_mean,
                    "ic_median": float(ic.median()),
                    "ic_std": std,
                    "ir": ic_mean / std if std and not math.isnan(std) else np.nan,
                    "positive_rate": float((ic > 0).mean()),
                    "ic_observations": int(len(ic)),
                    "assets": int(frame["asset"].nunique()),
                    "sample_start": frame["timestamp"].min().strftime("%Y-%m-%d"),
                    "sample_end": frame["timestamp"].max().strftime("%Y-%m-%d"),
                    "source": f"reports/artifacts/{spec.artifact_dir}/{spec.frame_glob}",
                    "report_href": spec.report_href,
                    "thesis": spec.thesis,
                    "ic_review_status": "needs_strategy_review",
                    "ic_review_note": "自动批量候选：尚未逐策略确认信号定义、horizon、资产截面和未来函数风险；不进入主榜。",
                }
            )
    return rows


def append_existing_ic(rows: list[dict[str, object]]) -> None:
    path = ROOT / "reports" / "artifacts" / "rank154b_young_funding_backtest" / "rank154b_funding_ic_summary.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    for _, row in df.iterrows():
        rows.append(
            {
                "strategy": "Rank154B young funding stat-arb",
                "display": "Funding cross-section / young coin placebo check",
                "factor": f"funding_{row.get('target', '-')}_{row.get('sample', '-')}",
                "horizon_bars": row.get("horizon"),
                "ic_mean": row.get("ic_mean"),
                "ic_median": row.get("ic_median"),
                "ic_std": row.get("ic_std"),
                "ir": row.get("icir_daily"),
                "positive_rate": row.get("positive_rate"),
                "ic_observations": row.get("days"),
                "assets": row.get("avg_n"),
                "sample_start": "from source",
                "sample_end": "from source",
                "source": path.relative_to(ROOT).as_posix(),
                "report_href": "../factors/paper_rank154_crypto_stat_arb_runner/report.html",
                "thesis": "Funding 类因子已有独立日频 IC 表；这里并列展示，便于和 bar 级形态因子比较。",
                "ic_review_status": "source_artifact_needs_review",
                "ic_review_note": "已有专项 IC artifact，但仍需按策略报告逐条复核口径；不进入当前候选主榜。",
            }
        )


def append_rank342_snapshot_ic(rows: list[dict[str, object]]) -> None:
    path = ROOT / "reports" / "artifacts" / "paper_rank342_samechain_crossdex" / "rank342_lane_snapshots.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    required = {"captured_at_utc", "chain", "base_symbol", "quote_symbol", "best_net_bps"}
    if df.empty or not required.issubset(df.columns):
        return
    work = df.copy()
    work["captured_at_utc"] = pd.to_datetime(work["captured_at_utc"], utc=True, errors="coerce")
    work["best_net_bps"] = pd.to_numeric(work["best_net_bps"], errors="coerce")
    work = work.dropna(subset=["captured_at_utc", "best_net_bps"]).copy()
    if work.empty:
        return
    work["timestamp"] = work["captured_at_utc"].dt.floor("15min")
    work = (
        work.sort_values(["timestamp", "chain", "base_symbol", "quote_symbol", "captured_at_utc"])
        .drop_duplicates(["timestamp", "chain", "base_symbol", "quote_symbol"], keep="last")
        .copy()
    )
    work["asset"] = work["chain"].astype(str) + "|" + work["base_symbol"].astype(str) + "|" + work["quote_symbol"].astype(str)
    work = work.sort_values(["asset", "timestamp"]).copy()

    summary_rows: list[dict[str, object]] = []
    for h in (1, 4, 16):
        target = f"future_gap_close_bps_{h}"
        work[target] = work["best_net_bps"] - work.groupby("asset")["best_net_bps"].shift(-h)
        ic = cross_sectional_spearman(work, "best_net_bps", target)
        if ic.empty:
            continue
        std = float(ic.std(ddof=1)) if len(ic) > 1 else np.nan
        ic_mean = float(ic.mean())
        row = {
            "strategy": "Rank342 lane snapshot IC",
            "display": "Rank342 same-chain cross-DEX lane pocket close",
            "factor": "best_net_bps",
            "horizon_bars": h,
            "ic_mean": ic_mean,
            "ic_median": float(ic.median()),
            "ic_std": std,
            "ir": ic_mean / std if std and not math.isnan(std) else np.nan,
            "positive_rate": float((ic > 0).mean()),
            "ic_observations": int(len(ic)),
            "assets": int(work["asset"].nunique()),
            "sample_start": work["timestamp"].min().strftime("%Y-%m-%d"),
            "sample_end": work["timestamp"].max().strftime("%Y-%m-%d"),
            "source": RANK342_IC_SUMMARY.relative_to(ROOT).as_posix(),
            "report_href": "../factors/rank342/report.html",
            "thesis": "用 same-chain cross-DEX lane snapshots 的当前 best_net_bps 预测未来同 lane 的 pocket contraction；target 定义为 future gap close，而不是 fill replay PnL。",
            "ic_review_status": "needs_strategy_review",
            "ic_review_note": "专项 lane-snapshot IC，待按 frozen spec / exit rule / observe-only 口径复核后决定展示角色。",
        }
        summary_rows.append(row)
        rows.append(row.copy())
    if summary_rows:
        pd.DataFrame(summary_rows).to_csv(RANK342_IC_SUMMARY, index=False)

    for path in sorted((ROOT / "reports" / "artifacts").glob("rank*/**/*ic*summary*.csv")):
        if path.name == "rank154b_funding_ic_summary.csv":
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        cols = {c.lower(): c for c in df.columns}
        ic_col = next((cols[c] for c in ("ic_mean", "mean_ic", "avg_ic", "ic") if c in cols), None)
        if not ic_col:
            continue
        ir_col = next((cols[c] for c in ("ir", "icir", "ic_ir", "icir_daily") if c in cols), None)
        factor_col = next((cols[c] for c in ("factor", "feature", "bucket", "sample", "target") if c in cols), None)
        obs_col = next((cols[c] for c in ("days", "n", "obs", "observations") if c in cols), None)
        for _, row in df.head(80).iterrows():
            rows.append(
                {
                    "strategy": f"{rank_label_from_name(path.as_posix())} existing IC artifact",
                    "display": path.parent.name.replace("_", " "),
                    "factor": row.get(factor_col, path.stem) if factor_col else path.stem,
                    "horizon_bars": row.get(cols.get("horizon", ""), np.nan) if "horizon" in cols else np.nan,
                    "ic_mean": row.get(ic_col),
                    "ic_median": row.get(cols.get("ic_median", ""), np.nan) if "ic_median" in cols else np.nan,
                    "ic_std": row.get(cols.get("ic_std", ""), np.nan) if "ic_std" in cols else np.nan,
                    "ir": row.get(ir_col, np.nan) if ir_col else np.nan,
                    "positive_rate": row.get(cols.get("positive_rate", ""), np.nan) if "positive_rate" in cols else np.nan,
                    "ic_observations": row.get(obs_col, np.nan) if obs_col else np.nan,
                    "assets": row.get(cols.get("avg_n", ""), np.nan) if "avg_n" in cols else np.nan,
                    "sample_start": "from source",
                    "sample_end": "from source",
                    "source": path.relative_to(ROOT).as_posix(),
                    "report_href": report_href_for_artifact_dir(path.parent.name),
                    "thesis": "已有 IC artifact，按原始文件口径并列展示。",
                    "ic_review_status": "source_artifact_needs_review",
                    "ic_review_note": "已有 IC artifact，但尚未纳入本页逐策略审计通过清单；不进入当前候选主榜。",
                }
            )


def summarize_story_artifacts() -> pd.DataFrame:
    out: list[dict[str, object]] = []
    for item in STORY_ARTIFACTS:
        path = ROOT / item["source"]
        row: dict[str, object] = dict(item)
        row["available"] = path.exists()
        if path.exists() and path.suffix == ".csv":
            df = pd.read_csv(path)
            row["rows"] = len(df)
            for col in ("trades", "total_return", "win_rate", "avg_net_ret", "mean_total_return", "positive_asset_ratio"):
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors="coerce").dropna()
                    if not vals.empty:
                        row[f"avg_{col}"] = float(vals.mean())
        out.append(row)
    return pd.DataFrame(out)


def safe_read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def metric_chip(label: str, value: object) -> str:
    text = "-" if value is None or (isinstance(value, float) and math.isnan(value)) else str(value)
    return f"<span class='metric-chip'><b>{escape(label)}</b>{escape(text)}</span>"


def key_rank_metrics(rank: str) -> list[tuple[str, str]]:
    rank = rank.lower()
    metrics: list[tuple[str, str]] = []
    if rank == "rank32b":
        summary = safe_read_json(ROOT / "reports/artifacts/rank32b_global_live/live_vs_shadow_summary.json")
        status = safe_read_json(ROOT / "reports/artifacts/rank32b_global_live/live_status.json")
        if summary:
            metrics.extend(
                [
                    ("closed trades", str(summary.get("closed_trades", "-"))),
                    ("live pnl", f"{float(summary.get('live_net_pnl_usdt', 0.0)):.2f} USDT"),
                    ("delta vs shadow", f"{float(summary.get('delta_vs_shadow_usdt', 0.0)):.2f} USDT"),
                ]
            )
        if status:
            metrics.append(("trade enabled", str(status.get("trade_enabled", "-"))))
            notes = status.get("notes")
            if isinstance(notes, list) and notes:
                metrics.append(("governance", str(notes[-1])[:120]))
    elif rank == "rank154":
        metrics.append(("status", "archived"))
        ic_path = ROOT / "reports/artifacts/rank154_postmortem/factor_ic_summary.csv"
        if ic_path.exists():
            df = pd.read_csv(ic_path)
            combined = df[(df["factor"].astype(str).eq("combined")) & (pd.to_numeric(df["horizon"], errors="coerce").eq(5))]
            carry = df[(df["factor"].astype(str).eq("carry")) & (pd.to_numeric(df["horizon"], errors="coerce").eq(10))]
            if not combined.empty:
                row = combined.iloc[0]
                metrics.append(("combined IC 5d", fmt_num(row.get("mean_ic"))))
                metrics.append(("combined ICIR", fmt_num(row.get("icir_daily"))))
            if not carry.empty:
                row = carry.iloc[0]
                metrics.append(("carry IC 10d", fmt_num(row.get("mean_ic"))))
        stats_path = ROOT / "reports/artifacts/rank154b_young_funding_backtest/rank154b_backtest_stats.csv"
        if stats_path.exists():
            df = pd.read_csv(stats_path)
            core = df[df["name"].astype(str).eq("154b_long_short_staggered_h5_cost20")]
            if not core.empty:
                row = core.iloc[0]
                metrics.append(("154b h5 cost20", fmt_pct(row.get("return"))))
                metrics.append(("154b maxDD", fmt_pct(row.get("max_dd"))))
    elif rank == "rank213":
        summary = safe_read_json(ROOT / "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_monthly_volume_universe_rebuild_summary.json")
        sample = summary.get("sample") if isinstance(summary, dict) else None
        monthly = summary.get("metrics", {}).get("monthly_volume_rebuild", {}) if isinstance(summary, dict) else {}
        frozen = summary.get("metrics", {}).get("frozen30", {}) if isinstance(summary, dict) else {}
        if isinstance(sample, dict):
            metrics.append(("sample", f"{sample.get('start_utc', '-')[:10]} -> {sample.get('end_utc', '-')[:10]}"))
        if isinstance(monthly, dict):
            gate = monthly.get("baseline_plus_veto_plus_gate", {})
            plain = monthly.get("plain", {})
            metrics.append(("causal plain", f"{float(plain.get('net_cum_pct', 0.0)):.1f}%"))
            metrics.append(("causal gate", f"{float(gate.get('net_cum_pct', 0.0)):.1f}%"))
            metrics.append(("causal maxDD", f"{float(gate.get('max_drawdown_pct', 0.0)):.1f}%"))
        if isinstance(frozen, dict):
            gate = frozen.get("baseline_plus_veto_plus_gate", {})
            metrics.append(("frozen gate", f"{float(gate.get('net_cum_pct', 0.0)):.1f}%"))
        receipt = safe_read_json(ROOT / "reports/artifacts/rank213_age90_live_canary_shell/rank213_archive_closeout_receipt.json")
        pre = receipt.get("pre_close_metrics") if isinstance(receipt, dict) else None
        if isinstance(pre, dict):
            metrics.append(("live closeout pnl", f"{float(pre.get('snapshot_total_pnl', 0.0)):.2f} USDT"))
    elif rank == "rank29":
        summary_path = ROOT / "reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/overall_summary.csv"
        if summary_path.exists():
            df = pd.read_csv(summary_path)
            if not df.empty:
                causal = df[(df["signal_engine"].eq("causal_replay")) & (df["variant"].eq("breakout_align_ge1")) & (df["cost_bps_per_side"].eq(6.0))]
                best = causal.iloc[0] if not causal.empty else df.iloc[0]
                metrics.extend(
                    [
                        ("main replay", str(best.get("variant", "-"))),
                        ("mean return", fmt_pct(best.get("mean_total_return"))),
                        ("positive assets", f"{int(best.get('positive_assets', 0))}/{int(best.get('assets_tested', 0))}"),
                        ("false break", fmt_pct(best.get("mean_false_break_ratio"))),
                    ]
                )
        status = safe_read_json(ROOT / "reports/artifacts/rank29_gate_live/rank29_gate_live_status.json")
        if status:
            metrics.append(("allow live", str(status.get("allow_live_orders", "-"))))
            metrics.append(("closed trades", str(status.get("closed_trades", "-"))))
    elif rank == "rank151":
        catalog = ROOT / "reports/artifacts/interview_showcase/rank_report_catalog.csv"
        if catalog.exists():
            df = pd.read_csv(catalog)
            sub = df[df["rank_id"].astype(str).str.lower().eq("rank151")]
            metrics.extend(
                [
                    ("reports", str(len(sub))),
                    ("status", ", ".join(sorted(sub["status"].dropna().unique())[:3]) if not sub.empty else "-"),
                    ("family", ", ".join(sorted(sub["family"].dropna().unique())[:2]) if not sub.empty else "-"),
                ]
            )
    return metrics


def summarize_evidence_items() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in EVIDENCE_ITEMS:
        row: dict[str, object] = dict(item)
        primary = ROOT / item["primary_artifact"]
        curve = ROOT / item["curve_artifact"]
        row["primary_exists"] = primary.exists()
        row["curve_exists"] = curve.exists()
        if primary.exists() and primary.suffix == ".csv":
            df = pd.read_csv(primary)
            row["rows"] = len(df)
            for col in ("equity_usd", "lifetime_return", "current_drawdown", "lifetime_total_return_6bps"):
                if col in df.columns:
                    vals = pd.to_numeric(df[col], errors="coerce").dropna()
                    if not vals.empty:
                        row[col] = float(vals.mean())
        elif primary.exists() and primary.suffix == ".json":
            obj = safe_read_json(primary)
            for key in ("closed_trades", "live_net_pnl_usdt", "shadow_proxy_net_pnl_usdt", "delta_vs_shadow_usdt"):
                if key in obj:
                    row[key] = obj[key]
            full = obj.get("full_period") if isinstance(obj, dict) else None
            if isinstance(full, dict):
                gate = full.get("baseline_plus_veto_plus_gate")
                if isinstance(gate, dict):
                    row["formal_gate_net_cum_pct"] = gate.get("net_cum_pct")
                    row["formal_gate_max_dd_pct"] = gate.get("max_drawdown_pct")
        rows.append(row)
    rows.extend(discover_auto_evidence_items())
    df = pd.DataFrame(rows)
    if not df.empty and "primary_artifact" in df.columns:
        df = df.drop_duplicates(subset=["primary_artifact"], keep="first")
    return df


def evidence_slug_from_row(row: pd.Series) -> str:
    primary = str(row.get("primary_artifact") or "")
    parts = Path(primary).parts
    if len(parts) >= 3 and parts[0] == "reports" and parts[1] == "artifacts":
        return slugify(parts[2])
    return slugify(str(row.get("strategy") or "evidence"))


def generated_evidence_href(row: pd.Series) -> str:
    return f"generated_evidence/{evidence_slug_from_row(row)}/report.html"


def library_artifact_href(path: Path) -> str:
    return "../artifacts/factor_research_library/" + path.name


def library_artifact_label(path: Path) -> str:
    return "reports/artifacts/factor_research_library/" + path.name


def artifact_preview_html(path_text: str) -> str:
    if not path_text or path_text == "nan":
        return "<p class='muted'>No artifact.</p>"
    path = ROOT / path_text
    if not path.exists():
        return f"<p class='muted'>{escape(path_text)} not found in workspace.</p>"
    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
            sample = df.head(20).copy()
            cols = list(sample.columns[:10])
            return table_html(sample, cols, {c: c for c in cols}, max_rows=20)
        if path.suffix.lower() == ".json":
            obj = safe_read_json(path)
            lines = []
            for key, value in list(obj.items())[:40]:
                if isinstance(value, (dict, list)):
                    value = str(value)[:260]
                lines.append({"key": key, "value": value})
            df = pd.DataFrame(lines)
            return table_html(df, ["key", "value"], {"key": "key", "value": "value"}, max_rows=40)
    except Exception as exc:
        return f"<p class='muted'>Unable to preview {escape(path_text)}: {escape(str(exc))}</p>"
    return f"<p class='muted'>{escape(path_text)}</p>"


def mirror_evidence_artifact(path_text: str) -> str:
    if not path_text or path_text == "nan":
        return ""
    src = ROOT / path_text
    if not src.exists() or not src.is_file():
        return ""
    try:
        rel = src.relative_to(ROOT / "reports" / "artifacts")
    except ValueError:
        rel = Path(slugify(path_text))
    dst = EVIDENCE_ARTIFACT_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    alias_dst = ALIAS_ART_DIR / "evidence_artifacts" / rel
    alias_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, alias_dst)
    return "../../../artifacts/factor_research_library/evidence_artifacts/" + rel.as_posix()


def artifact_link_html(label: str, path_text: str) -> str:
    href = mirror_evidence_artifact(path_text)
    if not href:
        return f"<p class='muted'>{escape(label)}: no downloadable artifact.</p>"
    return f"<p><a href='{escape(href)}'>{escape(label)} download</a></p>"


def render_generated_evidence_page(row: pd.Series, base_href: str) -> str:
    title = str(row.get("strategy") or "evidence")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    primary = str(row.get("primary_artifact") or "")
    curve = str(row.get("curve_artifact") or "")
    chips = evidence_metric_chips(row)
    metrics = [
        ("family", row.get("family", "-")),
        ("status", row.get("status", "-")),
        ("primary artifact", primary or "-"),
        ("curve artifact", curve or "-"),
        ("closed trades", row.get("closed_trades", "-")),
        ("lifetime return", pct_metric(row.get("lifetime_return"))),
        ("6bps return", pct_metric(row.get("lifetime_total_return_6bps"))),
        ("live pnl", row.get("live_net_pnl_usdt", "-")),
    ]
    metric_df = pd.DataFrame(metrics, columns=["item", "value"])
    css = """
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    body { margin:0; background:#f6f7f9; color:#172033; font:14px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif; }
    .wrap { max-width:1120px; margin:0 auto; padding:28px 18px 56px; }
    .panel { background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:18px 20px; margin-top:14px; overflow:auto; }
    h1 { margin:0 0 8px; font-size:26px; letter-spacing:0; }
    h2 { margin:22px 0 10px; font-size:18px; }
    h3 { margin:18px 0 8px; font-size:16px; }
    .muted { color:#667085; }
    .note { border-left:4px solid #175cd3; background:#eff6ff; padding:10px 12px; margin:12px 0; }
    .btn { display:inline-block; border:1px solid #cfd6e4; border-radius:6px; background:#fff; padding:6px 9px; font-weight:600; color:#175cd3; text-decoration:none; margin-right:8px; }
    table { width:100%; border-collapse:collapse; min-width:760px; }
    th,td { border-bottom:1px solid #e5e8ef; padding:8px 10px; vertical-align:top; text-align:left; }
    th { background:#f1f4f8; color:#344054; font-size:12px; white-space:nowrap; }
    td.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .metric-row { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 10px; }
    .metric-chip { display:inline-flex; gap:5px; align-items:center; border:1px solid #d0d5dd; border-radius:6px; padding:4px 7px; background:#f8fafc; color:#344054; font-size:12px; max-width:100%; }
    .metric-chip b { color:#101828; }
    a { color:#175cd3; text-decoration:none; }
    a:hover { text-decoration:underline; }
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)} | Evidence</title>
  <style>{css}</style>
</head>
<body>
<div class="wrap">
  <a class="btn" href="{escape(base_href)}">Back to research library</a>
  <div class="panel">
    <h1>{escape(title)}</h1>
    <p class="muted">Generated evidence page: {escape(generated_at)}</p>
    {chips}
    <div class="note">这是为没有独立 HTML 报告的 paper/live artifact 自动生成的轻量证据页。它不替代完整研究报告；用途是让外网页面可以直接打开，看到状态、分类、指标、artifact 样例和当前展示说明。</div>
    <p>{escape(str(row.get('note') or ''))}</p>
  </div>
  <div class="panel">
    <h2>Evidence Summary</h2>
    {table_html(metric_df, ['item', 'value'], {'item': 'item', 'value': 'value'}, max_rows=20)}
  </div>
  <div class="panel">
    <h2>Primary Artifact Preview</h2>
    <p class="muted">{escape(primary or '-')}</p>
    {artifact_link_html('Primary artifact', primary)}
    {artifact_preview_html(primary)}
  </div>
  <div class="panel">
    <h2>Curve / Trade Artifact Preview</h2>
    <p class="muted">{escape(curve or '-')}</p>
    {artifact_link_html('Curve/trade artifact', curve)}
    {artifact_preview_html(curve)}
  </div>
</div>
</body>
</html>"""


def generate_missing_evidence_pages(evidence_df: pd.DataFrame) -> pd.DataFrame:
    if evidence_df.empty or "report_href" not in evidence_df.columns:
        return evidence_df
    work = evidence_df.copy()
    mask = work["report_href"].fillna("").eq("../index.html") & work.get("primary_exists", False).map(truthy_cell)
    if not mask.any():
        return work
    for idx, row in work[mask].iterrows():
        href = generated_evidence_href(row)
        work.at[idx, "report_href"] = href
        for site_dir, base_href in ((SITE_DIR, "../../index.html"), (ALIAS_SITE_DIR, "../../index.html")):
            out = site_dir / href
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_generated_evidence_page(row, base_href), encoding="utf-8")
    return work


def sync_library_artifacts() -> None:
    ALIAS_ART_DIR.mkdir(parents=True, exist_ok=True)
    for path in (IC_SUMMARY, STORY_SUMMARY, EVIDENCE_SUMMARY, RANK_REPORT_CATALOG, AUTO_IC_COVERAGE):
        if path.exists():
            shutil.copy2(path, ALIAS_ART_DIR / path.name)


def first_existing_report_for_rank(rank_id: str, artifact_dir: str) -> str:
    candidates = []
    if artifact_dir:
        candidates.append(ROOT / "reports" / "site" / "factors" / artifact_dir / "report.html")
    if rank_id:
        candidates.extend(
            [
                ROOT / "reports" / "site" / "factors" / rank_id / "report.html",
                ROOT / "reports" / "site" / "paper" / f"{rank_id}.html",
            ]
        )
    for path in candidates:
        if path.exists():
            return "../" + path.relative_to(ROOT / "reports" / "site").as_posix()
    return report_href_for_artifact_dir(artifact_dir or rank_id)


def find_curve_artifact(directory: Path) -> str:
    preferred = []
    for pattern in ("*equity_curve*.csv", "*equity*.csv", "*monthly_summary*.csv", "*closed_trades*.csv", "*live_vs_shadow*.csv"):
        preferred.extend(sorted(directory.glob(pattern)))
        preferred.extend(sorted(directory.glob(f"**/{pattern}")))
    for path in preferred:
        if path.is_file():
            return path.relative_to(ROOT).as_posix()
    return ""


def summarize_status_csv(path: Path, row: dict[str, object]) -> None:
    try:
        df = pd.read_csv(path)
    except Exception:
        return
    row["rows"] = len(df)
    for col in (
        "equity_usd",
        "lifetime_return",
        "current_drawdown",
        "lifetime_total_return_6bps",
        "closed_trades",
        "live_net_pnl_usdt",
        "shadow_proxy_net_pnl_usdt",
        "delta_vs_shadow_usdt",
    ):
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            if not vals.empty:
                row[col] = float(vals.mean())
    for col in ("stage", "runner_mode", "mode", "status"):
        if col in df.columns and not df.empty:
            val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else ""
            if val:
                row["status"] = val
                break


def summarize_status_json(path: Path, row: dict[str, object]) -> None:
    obj = safe_read_json(path)
    if not isinstance(obj, dict):
        return
    for key in (
        "closed_trades",
        "live_net_pnl_usdt",
        "shadow_proxy_net_pnl_usdt",
        "delta_vs_shadow_usdt",
        "equity_usd",
        "lifetime_return",
        "current_drawdown",
    ):
        if key in obj:
            row[key] = obj[key]
    for key in ("stage", "runner_mode", "mode", "system_health", "status"):
        if obj.get(key):
            row["status"] = str(obj[key])
            break


def discover_auto_evidence_items() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    roots = [p for p in (ROOT / "reports" / "artifacts").iterdir() if p.is_dir() and "rank" in p.name.lower()]
    for directory in sorted(roots):
        status_files = []
        for pattern in ("*status.csv", "*status.json", "*last_run_summary.json", "*live_vs_shadow_summary.json"):
            status_files.extend(sorted(directory.glob(pattern)))
        if not status_files:
            continue
        primary = status_files[0]
        rank_id = rank_id_from_text(directory.name)
        curve = find_curve_artifact(directory)
        report_href = first_existing_report_for_rank(rank_id, directory.name)
        rel_primary = primary.relative_to(ROOT).as_posix()
        source_status = classify_status(rel_primary, directory.name)
        row: dict[str, object] = {
            "strategy": directory.name.replace("_", " "),
            "status": source_status,
            "family": classify_family(directory.name, directory.name),
            "report_href": report_href,
            "chart": "",
            "primary_artifact": rel_primary,
            "curve_artifact": curve,
            "primary_exists": True,
            "curve_exists": bool(curve and (ROOT / curve).exists()),
            "note": explain_rank_report(directory.name.replace("_", " "), classify_source_type(rel_primary), source_status, classify_family(directory.name, directory.name)),
        }
        if primary.suffix == ".csv":
            summarize_status_csv(primary, row)
        elif primary.suffix == ".json":
            summarize_status_json(primary, row)
        out.append(row)
    return out


def generate_charts(reviewed_ic_df: pd.DataFrame | None = None) -> None:
    if plt is None:
        return

    def save_chart(fig, name: str) -> None:
        for site_dir in (SITE_DIR, ALIAS_SITE_DIR):
            site_dir.mkdir(parents=True, exist_ok=True)
            fig.savefig(site_dir / name, dpi=150)

    if reviewed_ic_df is not None and not reviewed_ic_df.empty:
        scatter = reviewed_ic_df.copy()
        scatter["rank_id"] = scatter.get("rank_id", pd.Series("", index=scatter.index)).fillna("").astype(str)
        scatter["display_role"] = scatter.get("ic_display_role", pd.Series("", index=scatter.index)).fillna("").astype(str)
        scatter["ic_mean_num"] = pd.to_numeric(scatter.get("ic_mean"), errors="coerce")
        scatter["ir_num"] = pd.to_numeric(scatter.get("ir"), errors="coerce")
        scatter["ic_observations_num"] = pd.to_numeric(scatter.get("ic_observations"), errors="coerce")
        scatter = scatter.dropna(subset=["ic_mean_num"])
        scatter = scatter[scatter["rank_id"].ne("")]
        if not scatter.empty:
            scatter["abs_ir"] = scatter["ir_num"].abs()
            scatter["abs_ic"] = scatter["ic_mean_num"].abs()
            rank_order = (
                scatter.groupby("rank_id", dropna=False)
                .agg(best_abs_ir=("abs_ir", "max"), best_abs_ic=("abs_ic", "max"), total_obs=("ic_observations_num", "max"))
                .sort_values(["best_abs_ir", "best_abs_ic", "total_obs"], ascending=False)
                .reset_index()
            )
            rank_pos = {rank_id: idx for idx, rank_id in enumerate(rank_order["rank_id"].tolist())}
            scatter["x_base"] = scatter["rank_id"].map(rank_pos).astype(float)
            scatter["point_order"] = scatter.groupby("rank_id").cumcount()
            scatter["point_count"] = scatter.groupby("rank_id")["rank_id"].transform("count")
            scatter["x_jitter"] = scatter.apply(
                lambda row: 0.0
                if row["point_count"] <= 1
                else -0.24 + 0.48 * (float(row["point_order"]) / float(max(row["point_count"] - 1, 1))),
                axis=1,
            )
            scatter["x"] = scatter["x_base"] + scatter["x_jitter"]
            max_obs = float(scatter["ic_observations_num"].max()) if scatter["ic_observations_num"].notna().any() else 1.0
            if not math.isfinite(max_obs) or max_obs <= 0:
                max_obs = 1.0
            scatter["size"] = scatter["ic_observations_num"].fillna(0).map(
                lambda v: float(np.clip(40.0 + 220.0 * math.sqrt(max(float(v), 0.0) / max_obs), 40.0, 260.0))
            )

            role_specs = (
                ("current_candidate", "#175cd3", "current candidate"),
                ("audit_only", "#98a2b3", "audit-only"),
            )
            fig_width = max(12.0, min(22.0, 0.5 * len(rank_order) + 8.0))
            fig, ax = plt.subplots(figsize=(fig_width, 5.4))
            for role, color, label in role_specs:
                subset = scatter[scatter["display_role"].eq(role)].copy()
                if subset.empty:
                    continue
                ax.scatter(
                    subset["x"],
                    subset["ic_mean_num"],
                    s=subset["size"],
                    c=color,
                    alpha=0.82,
                    edgecolors="#ffffff",
                    linewidths=0.8,
                    label=label,
                )
            ax.axhline(0, color="#344054", linewidth=1, alpha=0.85)
            ax.set_title("Reviewed IC Distribution by Rank")
            ax.set_ylabel("IC mean")
            ax.set_xlabel("Rank")
            ax.grid(True, axis="y", alpha=0.22)
            ax.set_axisbelow(True)
            tick_labels = [rank_label_from_name(str(rank_id)) for rank_id in rank_order["rank_id"].tolist()]
            ax.set_xticks(list(rank_pos.values()))
            ax.set_xticklabels(tick_labels, rotation=70, ha="right", fontsize=8)
            ax.legend(loc="upper left", frameon=True)
            fig.tight_layout()
            save_chart(fig, "reviewed_ic_distribution_scatter.png")
            plt.close(fig)

    rank154 = ROOT / "reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_paper_equity_curve.csv"
    if rank154.exists():
        df = pd.read_csv(rank154)
        if {"rebalance_ts_utc", "equity_after_rebalance_usd"}.issubset(df.columns):
            df["rebalance_ts_utc"] = pd.to_datetime(df["rebalance_ts_utc"], errors="coerce")
            df = df.dropna(subset=["rebalance_ts_utc"]).sort_values("rebalance_ts_utc")
            fig, ax = plt.subplots(figsize=(9, 3.6))
            ax.plot(df["rebalance_ts_utc"], df["equity_after_rebalance_usd"], color="#175cd3", linewidth=2)
            ax.set_title("Rank154 paper equity")
            ax.set_ylabel("USD")
            ax.grid(True, alpha=0.25)
            fig.autofmt_xdate()
            fig.tight_layout()
            save_chart(fig, "rank154_paper_equity.png")
            plt.close(fig)

    rank32b = ROOT / "reports/artifacts/rank32b_shadow_global_live_like_backtest_atr1_1/trade_ledgers/monthly_summary_180d.csv"
    if rank32b.exists():
        df = pd.read_csv(rank32b)
        if {"month", "cum_pnl_usdt"}.issubset(df.columns):
            fig, ax = plt.subplots(figsize=(9, 3.6))
            ax.plot(df["month"].astype(str), df["cum_pnl_usdt"], color="#067647", marker="o", linewidth=2)
            ax.set_title("Rank32B shadow live-like cumulative PnL, 180d")
            ax.set_ylabel("USDT")
            ax.grid(True, alpha=0.25)
            fig.autofmt_xdate(rotation=25)
            fig.tight_layout()
            save_chart(fig, "rank32b_shadow_180d_cumpnl.png")
            plt.close(fig)

    rank213 = ROOT / "reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_formal_threeway_backtest_summary.json"
    obj = safe_read_json(rank213)
    full = obj.get("full_period") if isinstance(obj, dict) else None
    if isinstance(full, dict):
        labels = ["plain", "veto", "veto+gate"]
        keys = ["plain", "baseline_plus_veto", "baseline_plus_veto_plus_gate"]
        vals = [float(full.get(k, {}).get("net_cum_pct", np.nan)) for k in keys]
        if any(pd.notna(vals)):
            fig, ax = plt.subplots(figsize=(8, 3.6))
            colors = ["#b42318" if v < 0 else "#067647" for v in vals]
            ax.bar(labels, vals, color=colors)
            ax.axhline(0, color="#344054", linewidth=1)
            ax.set_title("Rank213 formal same-spec backtest")
            ax.set_ylabel("Net cumulative return (%)")
            ax.grid(True, axis="y", alpha=0.25)
            fig.tight_layout()
            save_chart(fig, "rank213_threeway_backtest.png")
            plt.close(fig)


def fmt_num(v: object, digits: int = 3) -> str:
    try:
        x = float(v)
    except Exception:
        return "-" if v is None or (isinstance(v, float) and math.isnan(v)) else escape(str(v))
    if math.isnan(x) or math.isinf(x):
        return "-"
    return f"{x:.{digits}f}"


def fmt_pct(v: object, digits: int = 1) -> str:
    try:
        x = float(v)
    except Exception:
        return "-"
    if math.isnan(x) or math.isinf(x):
        return "-"
    return f"{x * 100:.{digits}f}%"


def table_html(df: pd.DataFrame, cols: list[str], labels: dict[str, str], numeric: set[str] | None = None, pct: set[str] | None = None, max_rows: int = 80) -> str:
    numeric = numeric or set()
    pct = pct or set()
    if df.empty:
        return "<p class='muted'>No data.</p>"
    head = "".join(f"<th>{escape(labels.get(c, c))}</th>" for c in cols)
    body = []
    for _, row in df.head(max_rows).iterrows():
        cells = []
        search_cols = [c for c in cols if c not in {"artifact_examples", "research_note"}]
        row_search = " ".join(str(row.get(c, "")) for c in search_cols if pd.notna(row.get(c, np.nan))).lower()
        note = str(row.get("research_note", ""))
        if note:
            row_search = f"{row_search} {note[:180].lower()}"
        for c in cols:
            val = row.get(c)
            if c in pct:
                cells.append(f"<td class='num'>{fmt_pct(val)}</td>")
            elif c in numeric:
                cls = "num"
                try:
                    x = float(val)
                    if c in {"ic_mean", "ir", "avg_total_return", "avg_win_rate", "avg_avg_net_ret"}:
                        cls += " pos" if x > 0 else " neg" if x < 0 else ""
                except Exception:
                    pass
                cells.append(f"<td class='{cls}'>{fmt_num(val)}</td>")
            elif c == "report_href":
                cells.append(f"<td><a href='{escape(str(val))}'>open</a></td>")
            elif c in {"primary_artifact", "curve_artifact", "source", "chart"}:
                cells.append(f"<td>{path_cell_html(val, c)}</td>")
            else:
                cells.append(f"<td>{escape(str(val)) if pd.notna(val) else '-'}</td>")
        body.append(f"<tr data-search='{escape(row_search)}'>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def path_cell_html(value: object, column: str) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    text = str(value).strip()
    if not text or text == "nan":
        return "-"
    href = ""
    if column == "chart" and text.lower().endswith((".png", ".jpg", ".jpeg", ".svg")):
        href = text
    elif text.startswith("reports/artifacts/"):
        mirrored = mirror_evidence_artifact(text)
        if mirrored.startswith("../../../artifacts/"):
            href = "../" + mirrored.removeprefix("../../../")
        else:
            parts = Path(text).parts
            if len(parts) >= 3:
                rel = Path(*parts[2:]).as_posix()
                if (ALIAS_ART_DIR / "evidence_artifacts" / rel).exists():
                    href = "../artifacts/factor_research_library/evidence_artifacts/" + rel
                elif (ALIAS_ART_DIR / Path(text).name).exists():
                    href = "../artifacts/factor_research_library/" + Path(text).name
    elif text.startswith("../") or text.startswith("generated_evidence/"):
        href = text
    label = Path(text).name if "/" in text else text
    if href:
        return f"<a href='{escape(href)}'>{escape(label)}</a>"
    return escape(text)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "section"


def family_group_html(catalog_df: pd.DataFrame, cols: list[str], labels: dict[str, str]) -> str:
    if catalog_df.empty:
        return "<p class='muted'>No catalog data.</p>"
    parts: list[str] = []
    order = catalog_df.groupby("family", dropna=False).size().sort_values(ascending=False).index.tolist()
    for family in order:
        group = catalog_df[catalog_df["family"].eq(family)].copy()
        stage_bits = []
        if "registry_stage" in group.columns:
            stages = group["registry_stage"].replace("", np.nan).dropna().value_counts().to_dict()
            stage_bits = [f"{k}:{v}" for k, v in stages.items()]
        with_ic = int(group.get("best_ir", pd.Series(dtype=float)).notna().sum()) if "best_ir" in group.columns else 0
        anchor = f"family-{slugify(str(family))}"
        open_attr = " open" if len(parts) < 2 else ""
        parts.append(
            f"<details class='family-block' id='{escape(anchor)}'{open_attr}>"
            f"<summary>{escape(str(family))} <span class='subtle'>({len(group)} reports, 审计通过IC {with_ic})</span></summary>"
            f"<p class='muted'>{escape(' / '.join(stage_bits)) if stage_bits else '按报告标题、路径与 registry theme 归入该家族。'}</p>"
            + table_html(group, cols, labels, numeric={"artifact_hit_count_sampled", "best_ic_mean", "best_ir", "best_ic_observations"}, max_rows=80)
            + "</details>"
        )
    return "".join(parts)


def family_reading_focus(family: str) -> str:
    return {
        "funding/basis/carry": "先看 funding/basis 是否覆盖成本和拥挤反转，再看 after-cost 净收益。",
        "mean-reversion/stat-arb": "先看价差定义、半衰期、协整/残差稳定性，再看换手和执行容量。",
        "microstructure/liquidity": "先看数据频率、盘口可获得性、延迟和成交假设，避免把不可执行信号当 alpha。",
        "trend/momentum/breakout": "先看信号是否收盘确认、是否存在 lookahead，再看跨资产/跨阶段稳定性。",
        "event/clock/session": "先看事件窗口和 UTC/session 定义，再看样本数、节假日/周内稳定性。",
        "cross-sectional": "先看 universe 是否 as-of/causal，再看横截面 IC、分层收益和容量。",
        "risk/execution": "先看 live-vs-shadow、滑点、残余仓位、风控停止条件。",
        "structure/retest": "先看结构定义是否可复现，false-break、retest 和 OOS 表现。",
        "regime/risk-filter": "先看 gate/veto 是否减少尾部风险，避免只提高回测选择性。",
        "volume/participation": "先看成交量定义、流动性约束和 dry-down 期间稳定性。",
        "meta-review/governance": "先看版本、归档、审计和研究治理，不把它当直接交易 alpha。",
    }.get(str(family), "作为可追溯入口保留，先确认报告用途和是否有可计算证据。")


def catalog_overview_html(catalog_df: pd.DataFrame) -> str:
    if catalog_df.empty:
        return "<p class='muted'>No catalog data.</p>"
    work = catalog_df.copy()
    work["has_ic"] = work.get("best_ir", pd.Series(index=work.index, dtype=float)).notna().astype(int)
    work["artifact_count_num"] = pd.to_numeric(work.get("artifact_hit_count_sampled"), errors="coerce").fillna(0)
    work["has_artifact"] = work["artifact_count_num"].gt(0).astype(int)
    work["rank_for_count"] = work["rank_id"].replace("unranked", np.nan)
    work["is_paper_live"] = work["status"].isin(["paper", "live/monitor", "shadow", "canary"]).astype(int)
    work["is_p2p3"] = work.get("registry_stage", pd.Series(index=work.index, dtype=str)).fillna("").isin(["P2", "P3"]).astype(int)
    family = (
        work.groupby("family", dropna=False)
        .agg(
            reports=("title", "size"),
            unique_ranks=("rank_for_count", "nunique"),
            with_ic=("has_ic", "sum"),
            with_artifacts=("has_artifact", "sum"),
            paper_live_rows=("is_paper_live", "sum"),
            p2_p3_rows=("is_p2p3", "sum"),
        )
        .reset_index()
        .sort_values(["reports", "with_ic"], ascending=False)
    )
    family["reading_focus"] = family["family"].map(family_reading_focus)
    source = work.groupby("source_type", dropna=False).size().reset_index(name="reports").sort_values("reports", ascending=False)
    status = work.groupby("status", dropna=False).size().reset_index(name="reports").sort_values("reports", ascending=False)
    totals = pd.DataFrame(
        [
            {"metric": "报告目录行", "value": len(work), "note": "从 reports/site/factors 与 reports/site/paper 扫描 rank 相关 HTML。"},
            {"metric": "唯一 rank", "value": work["rank_for_count"].dropna().nunique(), "note": "同一 rank 可有 hub、paper、live、archive 多个页面。"},
            {"metric": "带审计通过 IC/IR 指针", "value": int(work["has_ic"].sum()), "note": "目录只关联逐策略审计通过的 best IC/IR；未审计候选在待审计队列。"},
            {"metric": "带 artifact 样例", "value": int(work["has_artifact"].sum()), "note": "可从报告追到 CSV/JSON/PNG 等研究产物。"},
            {"metric": "paper/live/shadow/canary 行", "value": int(work["is_paper_live"].sum()), "note": "这些行优先用于展示运行证据和收益曲线。"},
            {"metric": "P2/P3 registry 行", "value": int(work["is_p2p3"].sum()), "note": "说明研究管线里的角色、增量和下一步。"},
        ]
    )
    return (
        "<h3>目录覆盖摘要</h3>"
        + table_html(totals, ["metric", "value", "note"], {"metric": "指标", "value": "数量", "note": "说明"}, numeric={"value"}, max_rows=20)
        + "<h3>策略家族证据覆盖</h3>"
        + table_html(
            family,
            ["family", "reports", "unique_ranks", "with_ic", "with_artifacts", "paper_live_rows", "p2_p3_rows", "reading_focus"],
            {
                "family": "策略家族",
                "reports": "报告数",
                "unique_ranks": "唯一 rank",
                "with_ic": "审计通过IC",
                "with_artifacts": "带 artifact",
                "paper_live_rows": "paper/live 行",
                "p2_p3_rows": "P2/P3 行",
                "reading_focus": "阅读重点",
            },
            numeric={"reports", "unique_ranks", "with_ic", "with_artifacts", "paper_live_rows", "p2_p3_rows"},
            max_rows=30,
        )
        + "<h3>来源与状态覆盖</h3>"
        + "<div class='two'>"
        + "<div>" + table_html(source, ["source_type", "reports"], {"source_type": "来源", "reports": "报告数"}, numeric={"reports"}, max_rows=20) + "</div>"
        + "<div>" + table_html(status, ["status", "reports"], {"status": "状态", "reports": "报告数"}, numeric={"reports"}, max_rows=20) + "</div>"
        + "</div>"
    )


def enrich_ic_rows(ic_df: pd.DataFrame, catalog_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if ic_df.empty:
        return ic_df.copy()
    work = normalize_ic_schema(ic_df)
    work["rank_id"] = work["report_href"].map(rank_id_from_text)
    missing_rank = work["rank_id"].eq("")
    if missing_rank.any():
        work.loc[missing_rank, "rank_id"] = work.loc[missing_rank, "strategy"].map(rank_id_from_text)
    work["rank_id"] = work["rank_id"].replace("", "unranked")
    work["abs_ir"] = pd.to_numeric(work["ir"], errors="coerce").abs()
    work["abs_ic"] = pd.to_numeric(work["ic_mean"], errors="coerce").abs()
    work["ic_observations_num"] = pd.to_numeric(work["ic_observations"], errors="coerce")

    if catalog_df is not None and not catalog_df.empty:
        cat = catalog_df.copy()
        cat["rank_id"] = cat["rank_id"].fillna("unranked").astype(str)
        family_mode = (
            cat.groupby("rank_id")["family"]
            .agg(lambda s: s.dropna().astype(str).mode().iloc[0] if not s.dropna().empty else "")
            .reset_index()
        )
        meta_cols = ["rank_id", "family", "registry_stage", "registry_role", "registry_increment"]
        meta = (
            cat[meta_cols]
            .replace("", np.nan)
            .sort_values(["rank_id", "registry_stage", "registry_role"], na_position="last")
            .drop_duplicates("rank_id")
        )
        meta = meta.drop(columns=["family"]).merge(family_mode, on="rank_id", how="left")
        work = work.merge(meta, on="rank_id", how="left")
    if "family" not in work.columns:
        work["family"] = ""
    work["family"] = work["family"].fillna("")
    missing_family = work["family"].eq("")
    if missing_family.any():
        work.loc[missing_family, "family"] = work.loc[missing_family].apply(
            lambda r: classify_family(str(r.get("report_href", "")), str(r.get("display", r.get("strategy", "")))), axis=1
        )
    return work


def reviewed_ic_rows(ic_df: pd.DataFrame, catalog_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if ic_df.empty:
        return ic_df.copy()
    work = enrich_ic_rows(ic_df, catalog_df)
    status = work.get("ic_review_status", pd.Series("", index=work.index)).fillna("").astype(str)
    return work[status.eq("reviewed")].copy()


def pending_ic_rows(ic_df: pd.DataFrame, catalog_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if ic_df.empty:
        return ic_df.copy()
    work = enrich_ic_rows(ic_df, catalog_df)
    status = work.get("ic_review_status", pd.Series("", index=work.index)).fillna("").astype(str)
    return work[~status.eq("reviewed")].copy()


def mini_ic_card(row: pd.Series) -> str:
    family = str(row.get("family") or "-")
    stage = str(row.get("registry_stage") or "")
    subtitle = f"{row.get('rank_id', 'unranked')} · {family}" + (f" · {stage}" if stage and stage != "nan" else "")
    thesis = str(row.get("thesis", ""))[:180]
    if is_non_current_candidate_ic_row(row):
        thesis = "已归档、存在口径/causality 风险或已被 close-out 降级；历史 IC/回测只作为审计与治理证据，不作为当前候选 alpha。"
    return (
        "<div class='mini-card'>"
        f"<h3>{escape(str(row.get('display', row.get('strategy', '-'))))}</h3>"
        f"<p class='muted'>{escape(subtitle)}</p>"
        "<div class='metric-row'>"
        + metric_chip("factor", row.get("factor", "-"))
        + metric_chip("horizon", row.get("horizon_bars", "-"))
        + metric_chip("IC", fmt_num(row.get("ic_mean")))
        + metric_chip("IR", fmt_num(row.get("ir")))
        + metric_chip("obs", row.get("ic_observations", "-"))
        + "</div>"
        f"<p class='muted'>{escape(thesis)}</p>"
        f"<p><a href='{escape(str(row.get('report_href', '../index.html')))}'>open report</a></p>"
        "</div>"
    )


def is_non_current_candidate_ic_row(row: pd.Series) -> bool:
    display_role = str(row.get("ic_display_role") or "").lower()
    if display_role == "audit_only":
        return True
    if display_role == "current_candidate":
        return False
    text = " ".join(
        str(row.get(k, ""))
        for k in ("rank_id", "strategy", "display", "report_href", "thesis")
    ).lower()
    if "rank32b" in text or "rank32" in text and "slope" in text:
        return True
    if "rank154" in text or "rank154b" in text or "young funding" in text:
        return True
    if "rank213" in text:
        return True
    return False


def truthy_cell(value: object) -> bool:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def is_non_current_strategy_text(text: str) -> bool:
    lower = text.lower()
    blocked_tokens = (
        "rank32b",
        "rank32 ",
        "rank29",
        "rank154",
        "rank154b",
        "rank213",
        "young funding",
        "future",
        "lookahead",
        "look-ahead",
        "archived",
        "archive",
        "closeout",
        "close-out",
        "disabled",
        "decommissioned",
        "failed",
        "audit",
        "bias",
        "survivorship",
    )
    return any(token in lower for token in blocked_tokens)


def is_active_observation_evidence_row(row: pd.Series) -> bool:
    text = " ".join(
        str(row.get(k, ""))
        for k in ("strategy", "status", "family", "report_href", "primary_artifact", "curve_artifact", "note")
    )
    if is_non_current_strategy_text(text):
        return False
    if not truthy_cell(row.get("primary_exists")):
        return False
    status = str(row.get("status", "")).lower()
    active_tokens = (
        "paper",
        "runner",
        "running",
        "connected",
        "queue",
        "pilot",
        "launch",
        "shadow",
        "canary",
        "live",
    )
    return any(token in status for token in active_tokens)


def pct_metric(value: object) -> str:
    num = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(num):
        return "-"
    return f"{float(num) * 100:.1f}%"


def evidence_metric_chips(row: pd.Series) -> str:
    chips: list[str] = []
    chips.append(metric_chip("status", row.get("status", "-")))
    if pd.notna(pd.to_numeric(pd.Series([row.get("closed_trades")]), errors="coerce").iloc[0]):
        chips.append(metric_chip("closed trades", fmt_num(row.get("closed_trades"), 0)))
    if pd.notna(pd.to_numeric(pd.Series([row.get("lifetime_total_return_6bps")]), errors="coerce").iloc[0]):
        chips.append(metric_chip("6bps return", pct_metric(row.get("lifetime_total_return_6bps"))))
    if pd.notna(pd.to_numeric(pd.Series([row.get("lifetime_return")]), errors="coerce").iloc[0]):
        chips.append(metric_chip("lifetime", pct_metric(row.get("lifetime_return"))))
    if truthy_cell(row.get("curve_exists")):
        chips.append(metric_chip("curve", "yes"))
    return "<div class='metric-row'>" + "".join(chips) + "</div>"


def artifact_dir_from_evidence_row(row: pd.Series) -> str:
    primary = str(row.get("primary_artifact") or "").strip()
    if primary.startswith("reports/artifacts/"):
        parts = Path(primary).parts
        if len(parts) >= 3:
            return parts[2]
    return str(row.get("strategy") or "").strip().replace(" ", "_")


def best_observation_ic_rows(ic_rows: pd.DataFrame) -> pd.DataFrame:
    if ic_rows.empty:
        return ic_rows.copy()
    work = ic_rows.copy()
    work["abs_ir"] = pd.to_numeric(work.get("ir"), errors="coerce").abs()
    work["abs_ic"] = pd.to_numeric(work.get("ic_mean"), errors="coerce").abs()
    work["ic_observations_num"] = pd.to_numeric(work.get("ic_observations"), errors="coerce")
    return work.sort_values(["abs_ir", "abs_ic", "ic_observations_num"], ascending=False)


def ic_rows_for_observation(row: pd.Series, ic_df: pd.DataFrame) -> pd.DataFrame:
    if ic_df.empty:
        return ic_df.copy()
    href = str(row.get("report_href") or "")
    strategy = str(row.get("strategy") or "")
    if href and "report_href" in ic_df.columns:
        exact = ic_df[ic_df["report_href"].astype(str).eq(href)].copy()
        if not exact.empty:
            return exact
    rank_id = rank_id_from_text(href) or rank_id_from_text(strategy)
    if rank_id and "rank_id" in ic_df.columns:
        ranked = ic_df[ic_df["rank_id"].astype(str).eq(rank_id)].copy()
        if not ranked.empty:
            return ranked
    return ic_df.iloc[0:0].copy()


def coverage_status_label(status: str) -> str:
    return {
        "skip_no_frame_files": "无 bar-level frame",
        "skip_not_bar_level_frame": "不是 bar-level 横截面",
        "skip_less_than_3_assets": "资产数不足 3",
        "skip_no_factor_like_columns": "缺少因子列",
        "included": "已纳入自动 IC",
    }.get(status, status or "-")


def active_observation_ic_audit(row: pd.Series, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame) -> dict[str, object]:
    reviewed_rows = ic_rows_for_observation(row, reviewed_ic_df)
    current_rows = reviewed_rows[~reviewed_rows.apply(is_non_current_candidate_ic_row, axis=1)].copy() if not reviewed_rows.empty else reviewed_rows.copy()
    audit_only_rows = reviewed_rows[reviewed_rows.apply(is_non_current_candidate_ic_row, axis=1)].copy() if not reviewed_rows.empty else reviewed_rows.copy()
    pending_rows = ic_rows_for_observation(row, pending_ic_df)

    if not current_rows.empty:
        best = best_observation_ic_rows(current_rows).iloc[0]
        return {
            "status": "已审计",
            "structure_verdict": "current-candidate IC",
            "coverage_status": "-",
            "best": best,
            "audit_note": "已存在经过独立复算和策略定义复核的 current-candidate IC 行，可直接与主榜对读。",
            "next_step": "继续结合 paper/live 证据、成本、样本和稳定性决定是否晋级。",
        }

    if not audit_only_rows.empty:
        best = best_observation_ic_rows(audit_only_rows).iloc[0]
        return {
            "status": "仅 audit-only",
            "structure_verdict": "reviewed but not promotable",
            "coverage_status": "-",
            "best": best,
            "audit_note": "该观察对象能对应到已复核 IC，但页面 hard verdict 不支持 promotion，因此这里只能作为审计对照。",
            "next_step": "保留审计透明度，不进入当前候选主榜。",
        }

    if not pending_rows.empty:
        best = best_observation_ic_rows(pending_rows).iloc[0]
        return {
            "status": "待审计",
            "structure_verdict": "auto candidate only",
            "coverage_status": "-",
            "best": best,
            "audit_note": "已存在自动候选 IC，但还未完成信号定义、方向、horizon、as-of 对齐和未来函数复核。",
            "next_step": "完成逐策略审计后，才能决定是否进入正式 IC 主榜。",
        }

    rank_id = rank_id_from_text(str(row.get("report_href") or "")) or rank_id_from_text(str(row.get("strategy") or ""))
    artifact_dir = artifact_dir_from_evidence_row(row)
    coverage_match = coverage_df.iloc[0:0].copy()
    if not coverage_df.empty and "artifact_dir" in coverage_df.columns:
        coverage_match = coverage_df[coverage_df["artifact_dir"].astype(str).eq(artifact_dir)].copy()
    coverage_status = str(coverage_match["status"].iloc[0]) if not coverage_match.empty else ""
    base = ACTIVE_OBSERVATION_IC_AUDIT_OVERRIDES.get(rank_id) or ACTIVE_OBSERVATION_IC_AUDIT_OVERRIDES.get(artifact_dir) or {}
    return {
        "status": "暂无可比 IC",
        "structure_verdict": str(base.get("structure_verdict") or coverage_status_label(coverage_status) or "暂无可比 IC"),
        "coverage_status": coverage_status_label(coverage_status) if coverage_status else "-",
        "best": None,
        "audit_note": str(base.get("audit_note") or "当前页面只找到运行状态、交易流水或治理产物，未找到可发布的横截面 IC 口径。"),
        "next_step": str(base.get("next_step") or "如后续补出可比的 timestamp-asset factor frame，再进入 IC 审计。"),
    }


def active_observation_ic_html(row: pd.Series, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame) -> str:
    audit = active_observation_ic_audit(row, reviewed_ic_df, pending_ic_df, coverage_df)
    best = audit.get("best")
    chips = [metric_chip("IC审计", audit.get("status", "-")), metric_chip("结构判定", audit.get("structure_verdict", "-"))]
    if audit.get("coverage_status"):
        chips.append(metric_chip("覆盖判定", audit.get("coverage_status", "-")))
    if best is not None:
        chips.extend(
            [
                metric_chip("factor", best.get("factor", "-")),
                metric_chip("h", best.get("horizon_bars", "-")),
                metric_chip("IC", fmt_num(best.get("ic_mean"))),
                metric_chip("IR", fmt_num(best.get("ir"))),
                metric_chip("obs", best.get("ic_observations", "-")),
            ]
        )
    return (
        "<div class='definition'>"
        "<h3>对应 IC / 审计</h3>"
        f"<div class='metric-row'>{''.join(chips)}</div>"
        f"<p class='subtle'>{escape(str(audit.get('audit_note', '')))}</p>"
        f"<p class='subtle'>下一步：{escape(str(audit.get('next_step', '')))}</p>"
        "</div>"
    )


def active_observation_ordered_work(evidence_df: pd.DataFrame, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame, limit: int = 12) -> pd.DataFrame:
    if evidence_df.empty:
        return evidence_df.iloc[0:0].copy()
    work = evidence_df.copy()
    work = work[work.apply(is_active_observation_evidence_row, axis=1)].copy()
    if work.empty:
        return work
    audits: list[dict[str, object]] = []
    for _, row in work.iterrows():
        audit = active_observation_ic_audit(row, reviewed_ic_df, pending_ic_df, coverage_df)
        best = audit.get("best")
        status = str(audit.get("status") or "")
        if status in {"已审计", "仅 audit-only"} and best is not None:
            tier = 0
        elif status == "待审计" and best is not None:
            tier = 1
        else:
            tier = 2
        audits.append(
            {
                "ic_sort_tier": tier,
                "ic_sort_status": status,
                "ic_has_explicit": best is not None,
                "ic_best_abs_ir": abs(float(best.get("ir"))) if best is not None and pd.notna(best.get("ir")) else -1.0,
                "ic_best_obs": float(best.get("ic_observations")) if best is not None and pd.notna(best.get("ic_observations")) else -1.0,
            }
        )
    audit_df = pd.DataFrame(audits, index=work.index)
    work = pd.concat([work, audit_df], axis=1)
    work["curve_rank"] = work.get("curve_exists", False).map(lambda v: 1 if truthy_cell(v) else 0)
    work["closed_trades_num"] = pd.to_numeric(work.get("closed_trades"), errors="coerce").fillna(-1)
    work["rows_num"] = pd.to_numeric(work.get("rows"), errors="coerce").fillna(-1)
    work["return_rank"] = pd.to_numeric(work.get("lifetime_total_return_6bps"), errors="coerce").fillna(-999)
    work = work.sort_values(
        ["ic_sort_tier", "ic_best_abs_ir", "ic_best_obs", "curve_rank", "closed_trades_num", "return_rank", "rows_num"],
        ascending=[True, False, False, False, False, False, False],
    ).head(limit)
    return work


def active_observation_card(row: pd.Series, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame) -> str:
    artifact = str(row.get("primary_artifact") or "")
    artifact_html = f"<p class='subtle'>artifact: {path_cell_html(artifact, 'primary_artifact')}</p>" if artifact else ""
    curve = str(row.get("curve_artifact") or "")
    curve_html = f"<p class='subtle'>curve/trades: {path_cell_html(curve, 'curve_artifact')}</p>" if curve and curve != "nan" else ""
    ic_html = active_observation_ic_html(row, reviewed_ic_df, pending_ic_df, coverage_df)
    return (
        "<div class='mini-card'>"
        f"<h3>{escape(str(row.get('strategy', '-')))}</h3>"
        f"<p class='muted'>{escape(str(row.get('family') or '-'))}</p>"
        f"{evidence_metric_chips(row)}"
        f"{ic_html}"
        f"<p class='muted'>{escape(str(row.get('note') or ''))}</p>"
        f"<p><a href='{escape(str(row.get('report_href') or '../index.html'))}'>open report</a></p>"
        f"{artifact_html}"
        f"{curve_html}"
        "</div>"
    )


def active_observation_audit_table_html(evidence_df: pd.DataFrame, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame, limit: int = 12) -> str:
    work = active_observation_ordered_work(evidence_df, reviewed_ic_df, pending_ic_df, coverage_df, limit=limit)
    if work.empty:
        return "<p class='muted'>当前没有通过保守筛选的 paper/live 观察行。</p>"
    rows: list[dict[str, object]] = []
    for _, row in work.iterrows():
        audit = active_observation_ic_audit(row, reviewed_ic_df, pending_ic_df, coverage_df)
        best = audit.get("best")
        rows.append(
            {
                "strategy": row.get("strategy"),
                "family": row.get("family"),
                "ic_audit_status": audit.get("status"),
                "structure_verdict": audit.get("structure_verdict"),
                "best_factor": best.get("factor") if best is not None else "-",
                "best_horizon": best.get("horizon_bars") if best is not None else np.nan,
                "best_ic": best.get("ic_mean") if best is not None else np.nan,
                "best_ir": best.get("ir") if best is not None else np.nan,
                "best_obs": best.get("ic_observations") if best is not None else np.nan,
                "audit_note": audit.get("audit_note"),
                "next_step": audit.get("next_step"),
                "report_href": row.get("report_href"),
            }
        )
    df = pd.DataFrame(rows)
    return table_html(
        df,
        ["strategy", "family", "ic_audit_status", "structure_verdict", "best_factor", "best_horizon", "best_ic", "best_ir", "best_obs", "audit_note", "next_step", "report_href"],
        {
            "strategy": "观察对象",
            "family": "家族",
            "ic_audit_status": "IC审计",
            "structure_verdict": "结构判定",
            "best_factor": "最佳对应因子",
            "best_horizon": "h",
            "best_ic": "IC",
            "best_ir": "IR",
            "best_obs": "obs",
            "audit_note": "审计结论",
            "next_step": "下一步",
            "report_href": "报告",
        },
        numeric={"best_horizon", "best_ic", "best_ir", "best_obs"},
        max_rows=limit,
    )


def active_observations_html(evidence_df: pd.DataFrame, reviewed_ic_df: pd.DataFrame, pending_ic_df: pd.DataFrame, coverage_df: pd.DataFrame, limit: int = 12) -> str:
    work = active_observation_ordered_work(evidence_df, reviewed_ic_df, pending_ic_df, coverage_df, limit=limit)
    if work.empty:
        return "<p class='muted'>当前没有通过保守筛选的 paper/live 观察行。</p>"
    audited = []
    remaining = []
    for _, row in work.iterrows():
        audit = active_observation_ic_audit(row, reviewed_ic_df, pending_ic_df, coverage_df)
        card = active_observation_card(row, reviewed_ic_df, pending_ic_df, coverage_df)
        if str(audit.get("status") or "") in {"已审计", "仅 audit-only"} and audit.get("best") is not None:
            audited.append(card)
        else:
            remaining.append(card)
    parts: list[str] = []
    if audited:
        parts.append(
            "<h3>已审计且有明确 IC</h3>"
            "<p class='muted'>这一组优先展示已经完成口径审计、并能挂出明确 IC/IR 的观察对象。即使其中某些仍是 audit-only，它们也比纯 runner 状态更适合先被读者横向比较。</p>"
            "<div class='mini-grid'>" + "".join(audited) + "</div>"
        )
    if remaining:
        parts.append(
            "<h3>其余运行观察</h3>"
            "<p class='muted'>这些对象仍保留观察价值，但当前主要证据是 runner/status/快照/交易流水，尚未形成可正式发布的横截面 IC，或还停留在待审计状态。</p>"
            "<div class='mini-grid'>" + "".join(remaining) + "</div>"
        )
    return "".join(parts) if parts else "<p class='muted'>当前没有通过保守筛选的 paper/live 观察行。</p>"


def evidence_stage(row: pd.Series) -> str:
    text = " ".join(
        str(row.get(k, ""))
        for k in ("strategy", "status", "family", "report_href", "primary_artifact", "curve_artifact", "note")
    ).lower()
    status = str(row.get("status", "")).lower()
    if is_non_current_strategy_text(text):
        return "归档/审计/反证"
    if is_active_observation_evidence_row(row):
        return "当前可继续验证"
    if any(token in status for token in ("live", "canary", "shadow", "dry_run", "monitor", "waiting", "global_live")):
        return "执行观察 / live-shadow"
    if any(token in status for token in ("paper", "runner", "ready", "launch", "queue", "connected", "running", "frozen")):
        return "paper 队列 / 待验证"
    return "研究材料 / 参考"


def evidence_overview_html(evidence_df: pd.DataFrame) -> str:
    if evidence_df.empty:
        return "<p class='muted'>No paper/live evidence rows yet.</p>"
    work = evidence_df.copy()
    work["stage"] = work.apply(evidence_stage, axis=1)
    work["has_curve"] = work.get("curve_exists", False).map(lambda v: 1 if truthy_cell(v) else 0)
    work["has_primary"] = work.get("primary_exists", False).map(lambda v: 1 if truthy_cell(v) else 0)
    work["closed_trades_num"] = pd.to_numeric(work.get("closed_trades"), errors="coerce").fillna(-1)
    work["return_num"] = pd.to_numeric(work.get("lifetime_total_return_6bps"), errors="coerce").fillna(
        pd.to_numeric(work.get("lifetime_return"), errors="coerce")
    ).fillna(-999)
    stage_order = ["当前可继续验证", "paper 队列 / 待验证", "执行观察 / live-shadow", "归档/审计/反证", "研究材料 / 参考"]
    summary = (
        work.groupby("stage", dropna=False)
        .agg(
            rows=("strategy", "size"),
            with_primary=("has_primary", "sum"),
            with_curve=("has_curve", "sum"),
            closed_trades=("closed_trades_num", lambda s: int(s[s > 0].sum()) if (s > 0).any() else 0),
        )
        .reset_index()
    )
    summary["order"] = summary["stage"].map(lambda s: stage_order.index(s) if s in stage_order else 99)
    summary = summary.sort_values("order").drop(columns=["order"])
    cards: list[str] = []
    for stage in stage_order:
        group = work[work["stage"].eq(stage)].copy()
        if group.empty:
            continue
        group = group.sort_values(["has_curve", "closed_trades_num", "return_num", "has_primary"], ascending=False).head(4)
        links = []
        for _, row in group.iterrows():
            href = str(row.get("report_href") or "../index.html")
            label = str(row.get("strategy") or "-")
            links.append(f"<li><a href='{escape(href)}'>{escape(label)}</a> <span class='subtle'>{escape(str(row.get('status') or '-'))}</span></li>")
        cards.append(
            "<div class='mini-card'>"
            f"<h3>{escape(stage)}</h3>"
            f"<p class='muted'>共 {len(work[work['stage'].eq(stage)])} 条；优先看有曲线、交易流水和 primary artifact 的行。</p>"
            "<ul class='priority-list'>" + "".join(links) + "</ul>"
            "</div>"
        )
    return (
        "<div class='note'>这张总览把 paper/live evidence 从大表改成读者可扫描的阶段：先看仍可继续验证的候选，再看 paper 队列和执行观察；归档/审计/反证保留为研究纪律，不作为当前 alpha 主张。</div>"
        + table_html(
            summary,
            ["stage", "rows", "with_primary", "with_curve", "closed_trades"],
            {"stage": "阶段", "rows": "行数", "with_primary": "有 primary artifact", "with_curve": "有曲线/流水", "closed_trades": "已记录 closed trades"},
            numeric={"rows", "with_primary", "with_curve", "closed_trades"},
            max_rows=10,
        )
        + "<h3>优先阅读样例</h3>"
        + "<div class='mini-grid'>" + "".join(cards) + "</div>"
    )


def evidence_definitions_html() -> str:
    rows = pd.DataFrame(
        [
            {
                "term": "当前可继续验证",
                "definition": "有 primary artifact，仍处于 paper / runner / queue / shadow / canary / live 观察链路，且未被 close-out、future/lookahead、universe causality 或失败归档否定。",
                "reader_action": "优先看收益曲线、交易流水、状态 artifact、样本数和下一步 admission 条件。",
            },
            {
                "term": "paper / paper_runner_live",
                "definition": "离线或小资金前的运行观察状态；它说明策略正在持续产生日志、状态或交易流水，不等于已经通过上线。",
                "reader_action": "重点检查 closed trades、当前持仓、是否有 curve/trades artifact、是否经过成本和容量检查。",
            },
            {
                "term": "live / canary / shadow",
                "definition": "live 是真实或准真实执行链路；canary 是小规模试运行；shadow 是不下单或对照执行，用来比较信号、成交和风控偏差。",
                "reader_action": "重点看 live-vs-shadow、残余仓位、滑点、拒单、告警和是否有停机/降级记录。",
            },
            {
                "term": "归档/审计/反证",
                "definition": "已经因为 future/lookahead、选池因果性、成本后失效、live canary 失败或 release gate 失败而不能作为当前 alpha 主张。",
                "reader_action": "把它当研究纪律证据：看失败原因、停止规则和修正后的口径，不把历史 PnL 当当前成果。",
            },
            {
                "term": "primary artifact",
                "definition": "该行最核心的状态、摘要或配置证据，通常是 status.csv、summary.json、live_status.json 或 formal backtest summary。",
                "reader_action": "先打开 primary artifact 判断这条 evidence 是否仍在运行、是否归档、最近状态和关键指标。",
            },
            {
                "term": "curve/trades artifact",
                "definition": "收益曲线、closed trades、equity curve、monthly summary 或交易流水。它比单个收益数字更能说明稳定性和样本结构。",
                "reader_action": "检查交易数、收益分布、回撤、是否集中在少数时间段或少数资产。",
            },
            {
                "term": "closed trades",
                "definition": "已完成的交易记录数。它不是收益质量本身，但可以判断样本是否足够支持初步观察。",
                "reader_action": "交易数很少时只作为线索；交易数较多时再结合成本、回撤、分阶段表现和异常交易检查。",
            },
            {
                "term": "drawdown / current_drawdown / maxDD",
                "definition": "drawdown 是从权益高点到低点的回撤；current_drawdown 是当前相对历史高点的回撤；maxDD 是历史最大回撤。",
                "reader_action": "收益高但回撤不可接受的线不能直接晋级，需要看 regime、gate、止损和容量。",
            },
            {
                "term": "formal backtest",
                "definition": "固定规则、固定成本、固定口径下的正式回测。它比探索表更接近可复现证据，但仍不等于 live 结果。",
                "reader_action": "检查 universe 是否 causal/as-of、成本是否足够保守、是否有 OOS 和参数敏感性。",
            },
            {
                "term": "IC / IR",
                "definition": "IC 是同一时点横截面因子值和未来收益的 Spearman rank correlation；IR 是 IC 时间序列 mean/std。",
                "reader_action": "用来横向比较预测相关性，但必须和 PnL、成本、执行、样本数和归档状态分开看。",
            },
        ]
    )
    return table_html(
        rows,
        ["term", "definition", "reader_action"],
        {"term": "术语/字段", "definition": "定量或治理定义", "reader_action": "读者应如何使用"},
        max_rows=40,
    )


def ic_audit_plan_html() -> str:
    rows = pd.DataFrame(
        [
            {"rank": "Rank201", "priority": "P1", "status": "todo", "audit_focus": "先读 paper/live artifact，确认信号列、方向、horizon 和 closed-trade 样本。", "formal_rule": "只在收盘确认后的 as-of frame 上算横截面 Spearman IC。"},
            {"rank": "Rank200", "priority": "P1", "status": "todo", "audit_focus": "核对当前候选定义、预测周期、资产池和成本后收益是否一致。", "formal_rule": "信号方向必须来自策略报告，不从 IC 符号倒推。"},
            {"rank": "Rank229", "priority": "P1", "status": "todo", "audit_focus": "检查运行观察 artifact 与 bar-level frame 是否同一口径。", "formal_rule": "若只有状态/交易流水而无横截面 frame，则不强行发布 IC。"},
            {"rank": "Rank187", "priority": "P1", "status": "todo", "audit_focus": "逐列确认候选因子是否为策略核心信号，排除通用模板特征列。", "formal_rule": "候选列通过报告定义后才进入正式 IC。"},
            {"rank": "Rank183", "priority": "P1", "status": "todo", "audit_focus": "确认结构/形态信号的时间戳是否只使用已闭合 K 线。", "formal_rule": "发现 preview/unclosed bar 依赖则只能归档。"},
            {"rank": "Rank186", "priority": "P1", "status": "todo", "audit_focus": "核对 universe、样本期和策略方向，避免把反向控制组当 alpha。", "formal_rule": "资产池必须 as-of/causal，不能用事后幸存者集合。"},
            {"rank": "Rank151", "priority": "P2", "status": "todo", "audit_focus": "检查是否有独立 IC artifact，若有先复核原始口径。", "formal_rule": "source artifact 也需人工确认后才标 reviewed。"},
            {"rank": "Rank342", "priority": "P2", "status": "todo", "audit_focus": "先判断报告是候选、归档还是治理材料，再决定是否需要 IC。", "formal_rule": "非当前候选不进入 Top IC/IR。"},
            {"rank": "Rank368", "priority": "P2", "status": "todo", "audit_focus": "核对是否为 paper/live 运行线，以及交易证据是否足够。", "formal_rule": "收益曲线和 IC 分开展示，互不替代。"},
            {"rank": "Rank370", "priority": "P2", "status": "todo", "audit_focus": "检查 signal、close、未来收益是否同一 timestamp 对齐。", "formal_rule": "target 必须用未来收益，feature 必须只含当时可知信息。"},
            {"rank": "Rank32B", "priority": "Archive", "status": "rejected", "audit_focus": "已因 future/lookahead 下线。", "formal_rule": "不作为当前主线或 Top IC 展示，只保留审计案例。"},
            {"rank": "Rank154", "priority": "Archive", "status": "rejected", "audit_focus": "failed release candidate / postmortem。", "formal_rule": "不作为当前主线；历史 IC 只能作为归档材料。"},
            {"rank": "Rank213", "priority": "Archive", "status": "rejected", "audit_focus": "旧 frozen30/rolling Top30 有 universe causality/幸存者风险，causal 版本弱。", "formal_rule": "不作为当前正例；如展示必须说明选池口径风险。"},
        ]
    )
    return table_html(
        rows,
        ["rank", "priority", "status", "audit_focus", "formal_rule"],
        {"rank": "Rank", "priority": "优先级", "status": "审计状态", "audit_focus": "逐条审计重点", "formal_rule": "正式发布规则"},
        max_rows=40,
    )


def ic_coverage_audit_html(coverage_df: pd.DataFrame) -> str:
    if coverage_df.empty:
        return "<p class='muted'>No auto IC coverage audit data.</p>"
    labels = {
        "included": "已纳入自动 IC",
        "skip_no_frame_files": "无 bar-level frame 文件",
        "skip_not_bar_level_frame": "不是 bar-level 横截面",
        "skip_less_than_3_assets": "同一时点资产少于 3 个",
        "skip_no_factor_like_columns": "没有可用数值因子列",
    }
    summary = coverage_df.groupby("status", dropna=False).size().reset_index(name="artifact_groups")
    summary["status_label"] = summary["status"].map(lambda v: labels.get(str(v), str(v)))
    summary = summary.sort_values("artifact_groups", ascending=False)
    sample_cols = ["artifact_dir", "status", "usable_files", "assets", "rows", "factor_count", "factors"]
    examples = []
    for status in summary["status"].tolist():
        group = coverage_df[coverage_df["status"].astype(str).eq(str(status))].copy()
        sort_cols = [c for c in ["usable_files", "assets", "rows", "factor_count"] if c in group.columns]
        if sort_cols:
            for col in sort_cols:
                group[col] = pd.to_numeric(group[col], errors="coerce")
            group = group.sort_values(sort_cols, ascending=False)
        examples.append(group.head(5))
    example_df = pd.concat(examples, ignore_index=True) if examples else pd.DataFrame(columns=sample_cols)
    return (
        "<div class='note'>IC/IR 不是按报告数量强行补齐；只有 timestamp、close、可识别资产、同一时点至少 3 个资产、且存在数值因子列的 bar-level frame 才自动计算。其他报告继续作为目录、paper/live 证据或审计材料保留。</div>"
        + table_html(
            summary,
            ["status_label", "artifact_groups"],
            {"status_label": "覆盖判定", "artifact_groups": "artifact 组数"},
            numeric={"artifact_groups"},
            max_rows=20,
        )
        + "<h3>覆盖审计样例</h3>"
        + table_html(
            example_df,
            sample_cols,
            {
                "artifact_dir": "artifact 目录",
                "status": "判定",
                "usable_files": "可用文件",
                "assets": "资产数",
                "rows": "行数",
                "factor_count": "因子列数",
                "factors": "因子列样例",
            },
            numeric={"usable_files", "assets", "rows", "factor_count"},
            max_rows=30,
        )
    )


def top_ic_cards_html(ic_df: pd.DataFrame, catalog_df: pd.DataFrame | None = None, limit: int = 10) -> str:
    if ic_df.empty:
        return "<p class='muted'>No IC data.</p>"
    work = reviewed_ic_rows(ic_df, catalog_df).dropna(subset=["abs_ir", "abs_ic"], how="all")
    if work.empty:
        return "<p class='muted'>当前没有逐策略审计通过的 IC/IR 行。自动批量候选和已有 source artifact 已移到下方待审计队列，避免把模板列或未确认口径误当成正式横向结果。</p>"
    work["audit_only"] = work.apply(is_non_current_candidate_ic_row, axis=1)
    candidate_work = work[~work["audit_only"]].copy()
    ranked = candidate_work.sort_values(["abs_ir", "abs_ic", "ic_observations_num"], ascending=False)
    by_rank = ranked.drop_duplicates("rank_id").head(limit)
    by_family = ranked[ranked["family"].ne("")].drop_duplicates("family").head(8)
    audit_ranked = work[work["audit_only"]].sort_values(["abs_ir", "abs_ic", "ic_observations_num"], ascending=False).drop_duplicates("rank_id").head(3)
    rank_cards = "<div class='mini-grid'>" + "".join(mini_ic_card(row) for _, row in by_rank.iterrows()) + "</div>"
    family_cards = "<div class='mini-grid'>" + "".join(mini_ic_card(row) for _, row in by_family.iterrows()) + "</div>"
    audit_cards = ""
    if not audit_ranked.empty:
        audit_cards = (
            "<h3>归档/审计样例，不作为当前候选排序</h3>"
            "<p class='muted'>Rank32/32B、Rank154、Rank213 等已被 future/lookahead、归档 close-out、universe causality 或 live-canary 失败降级；保留在这里是为了透明展示为什么不能继续当作当前可用 alpha。</p>"
            "<div class='mini-grid'>" + "".join(mini_ic_card(row) for _, row in audit_ranked.iterrows()) + "</div>"
        )
    return (
        "<h3>每个 Rank 的最佳 IC/IR 代表行</h3>"
        "<p class='muted'>同一 rank 只保留 |IR| 最高的一行，且排除已归档、已确认 future/lookahead 或存在核心 causality 风险的线，避免把不可用研究线误当成当前候选。</p>"
        + rank_cards
        + "<h3>每个策略家族的代表 IC/IR 行</h3>"
        "<p class='muted'>同一策略家族只保留一行，用来快速检查不同 alpha 母题是否都有可比证据。</p>"
        + family_cards
        + audit_cards
    )


def key_rank_playbook_html() -> str:
    cards = []
    for item in KEY_RANK_PLAYBOOK:
        metrics = key_rank_metrics(item["rank"])
        metric_html = ""
        if metrics:
            metric_html = "<div class='metric-row'>" + "".join(metric_chip(label, value) for label, value in metrics) + "</div>"
        cards.append(
            "<div class='playbook-card'>"
            f"<h3>{escape(item['rank'])}</h3>"
            f"{metric_html}"
            f"<p><b>定位：</b>{escape(item['family'])}</p>"
            f"<p><b>状态：</b>{escape(item['status'])}</p>"
            f"<p><b>定量定义：</b>{escape(item['definition'])}</p>"
            f"<p><b>证据：</b>{escape(item['evidence'])}</p>"
            f"<p><b>研究说明：</b>{escape(item['talk_track'])}</p>"
            f"<p><a href='{escape(item['href'])}'>open report</a></p>"
            "</div>"
        )
    return "<div class='playbook'>" + "".join(cards) + "</div>"


def complete_research_showcase_html() -> str:
    cols = [
        "rank",
        "status",
        "def",
        "clean",
        "align",
        "anti_lookahead",
        "ic",
        "groups",
        "cost",
        "oos",
        "exposure",
        "memo",
        "why_front",
        "report_href",
    ]
    rows: list[dict[str, object]] = []
    cards: list[str] = []
    legend = {"Y": "已覆盖", "P": "部分覆盖 / 取决于该线角色", "N": "不是这条线的主展示点"}
    for item in sorted(COMPLETE_RESEARCH_SHOWCASE, key=lambda x: int(x.get("priority", 99))):
        coverage = dict(item.get("coverage") or {})
        rank = str(item["rank"])
        metrics = key_rank_metrics(rank)
        metric_html = "<div class='metric-row'>" + "".join(metric_chip(label, value) for label, value in metrics) + "</div>" if metrics else ""
        cards.append(
            "<div class='playbook-card'>"
            f"<h3>{escape(rank)}</h3>"
            f"{metric_html}"
            f"<p><b>定位：</b>{escape(str(item['family']))}</p>"
            f"<p><b>状态：</b>{escape(str(item['status']))}</p>"
            f"<p><b>为什么排前：</b>{escape(str(item['why_front']))}</p>"
            f"<p><b>memo 读法：</b>{escape(str(item['memo']))}</p>"
            f"<p><a href='{escape(str(item['href']))}'>open report</a></p>"
            "</div>"
        )
        rows.append(
            {
                "rank": rank,
                "status": str(item["status"]),
                "def": coverage.get("def", "-"),
                "clean": coverage.get("clean", "-"),
                "align": coverage.get("align", "-"),
                "anti_lookahead": coverage.get("anti_lookahead", "-"),
                "ic": coverage.get("ic", "-"),
                "groups": coverage.get("groups", "-"),
                "cost": coverage.get("cost", "-"),
                "oos": coverage.get("oos", "-"),
                "exposure": coverage.get("exposure", "-"),
                "memo": coverage.get("memo", "-"),
                "why_front": str(item["why_front"]),
                "report_href": str(item["href"]),
            }
        )
    df = pd.DataFrame(rows)
    labels = {
        "rank": "Rank",
        "status": "状态",
        "def": "因子定义",
        "clean": "数据清洗",
        "align": "时间对齐",
        "anti_lookahead": "避免未来函数",
        "ic": "IC / Rank IC",
        "groups": "分组收益",
        "cost": "交易成本",
        "oos": "样本外",
        "exposure": "行业/风格暴露",
        "memo": "最终 memo",
        "why_front": "为什么前排展示",
        "report_href": "报告",
    }
    return (
        "<div class='note'>这一节不按“当前能不能上线”排，而按“研究工作是否做完整”排。"
        "所以即使某条线已经归档，只要它把定义、清洗、时间对齐、future audit、IC/分组收益、成本、样本外和 memo 做得足够完整，也会被提到前面，方便展示研究方法论。</div>"
        "<p class='muted'>表里用 `Y / P / N` 表示覆盖度：`Y` = 已覆盖，`P` = 部分覆盖或更偏该线的子议题，`N` = 不是这条线的核心展示重点。</p>"
        + table_html(df, cols, labels, max_rows=20)
        + "<h3>完整研究样例</h3><div class='playbook'>" + "".join(cards) + "</div>"
    )


def render_page(ic_df: pd.DataFrame, story_df: pd.DataFrame, evidence_df: pd.DataFrame, catalog_df: pd.DataFrame, coverage_df: pd.DataFrame) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    reviewed_ic_df = reviewed_ic_rows(ic_df, catalog_df)
    pending_ic_df = pending_ic_rows(ic_df, catalog_df)
    current_candidate_ic_df = reviewed_ic_df.copy()
    if not current_candidate_ic_df.empty:
        current_candidate_ic_df = current_candidate_ic_df[~current_candidate_ic_df.apply(is_non_current_candidate_ic_row, axis=1)].copy()
    audit_only_ic_df = reviewed_ic_df.copy()
    if not audit_only_ic_df.empty:
        audit_only_ic_df = audit_only_ic_df[audit_only_ic_df.apply(is_non_current_candidate_ic_row, axis=1)].copy()

    candidate_main = current_candidate_ic_df.copy()
    if not candidate_main.empty:
        candidate_main["abs_ir"] = pd.to_numeric(candidate_main["ir"], errors="coerce").abs()
        candidate_main["abs_ic"] = pd.to_numeric(candidate_main["ic_mean"], errors="coerce").abs()
        candidate_main["ic_observations_num"] = pd.to_numeric(candidate_main["ic_observations"], errors="coerce")
        candidate_main = (
            candidate_main.sort_values(["abs_ir", "abs_ic", "ic_observations_num"], ascending=False)
            .drop(columns=["abs_ir", "abs_ic", "ic_observations_num"])
            .head(40)
        )
    audit_only_main = audit_only_ic_df.copy()
    if not audit_only_main.empty:
        audit_only_main["abs_ir"] = pd.to_numeric(audit_only_main["ir"], errors="coerce").abs()
        audit_only_main["abs_ic"] = pd.to_numeric(audit_only_main["ic_mean"], errors="coerce").abs()
        audit_only_main["ic_observations_num"] = pd.to_numeric(audit_only_main["ic_observations"], errors="coerce")
        audit_only_main = (
            audit_only_main.sort_values(["abs_ir", "abs_ic", "ic_observations_num"], ascending=False)
            .drop(columns=["abs_ir", "abs_ic", "ic_observations_num"])
            .head(40)
        )
    pending_main = pending_ic_df.copy()
    if not pending_main.empty:
        pending_main["abs_ir"] = pd.to_numeric(pending_main["ir"], errors="coerce").abs()
        pending_main = pending_main.sort_values(["abs_ir", "ic_observations"], ascending=False).drop(columns=["abs_ir"]).head(80)
    current_ic_df = current_candidate_ic_df.copy()
    best = current_ic_df.sort_values(["ir", "ic_mean"], ascending=False).head(12).copy() if not current_ic_df.empty else pd.DataFrame(columns=ic_df.columns)
    top_ic = pd.to_numeric(current_ic_df["ic_mean"], errors="coerce").abs().max() if not current_ic_df.empty else np.nan
    top_ir = pd.to_numeric(current_ic_df["ir"], errors="coerce").abs().max() if not current_ic_df.empty else np.nan
    report_count = len(catalog_df)
    unique_rank_count = catalog_df["rank_id"].replace("unranked", np.nan).dropna().nunique() if not catalog_df.empty else 0
    ic_strategy_count = reviewed_ic_df["strategy"].nunique() if not reviewed_ic_df.empty else 0
    pending_ic_strategy_count = pending_ic_df["strategy"].nunique() if not pending_ic_df.empty else 0
    included_auto_count = int((coverage_df.get("status") == "included").sum()) if not coverage_df.empty and "status" in coverage_df.columns else 0
    current_candidate_count = len(current_candidate_ic_df)
    audit_only_count = len(audit_only_ic_df)

    ic_cols = ["display", "factor", "horizon_bars", "ic_mean", "ir", "positive_rate", "ic_observations", "assets", "sample_start", "sample_end", "ic_review_note", "report_href"]
    pending_ic_cols = ["display", "factor", "horizon_bars", "ic_mean", "ir", "ic_observations", "assets", "ic_review_status", "ic_review_note", "source", "report_href"]
    ic_labels = {
        "display": "研究线",
        "factor": "因子",
        "horizon_bars": "预测 horizon(bar)",
        "ic_mean": "IC mean",
        "ir": "IR = IC mean/std",
        "positive_rate": "IC>0 占比",
        "ic_observations": "IC 样本数",
        "assets": "资产数/均值",
        "sample_start": "开始",
        "sample_end": "结束",
        "ic_review_note": "审计说明",
        "report_href": "报告",
        "ic_review_status": "审计状态",
        "source": "来源",
    }
    story_cols = ["strategy", "family", "available", "rows", "avg_trades", "avg_total_return", "avg_win_rate", "avg_avg_net_ret", "report_href", "summary"]
    story_labels = {
        "strategy": "策略/因子线",
        "family": "类别",
        "available": "artifact",
        "rows": "rows",
        "avg_trades": "avg trades",
        "avg_total_return": "avg total return",
        "avg_win_rate": "avg win rate",
        "avg_avg_net_ret": "avg net ret",
        "report_href": "报告",
        "summary": "研究说明",
    }
    evidence_cols = [
        "strategy",
        "status",
        "family",
        "report_href",
        "chart",
        "lifetime_return",
        "current_drawdown",
        "closed_trades",
        "live_net_pnl_usdt",
        "formal_gate_net_cum_pct",
        "formal_gate_max_dd_pct",
        "primary_artifact",
        "note",
    ]
    evidence_labels = {
        "strategy": "因子/策略",
        "status": "状态",
        "family": "类别",
        "report_href": "报告",
        "chart": "收益/回测图",
        "lifetime_return": "lifetime return",
        "current_drawdown": "drawdown",
        "closed_trades": "closed trades",
        "live_net_pnl_usdt": "live pnl",
        "formal_gate_net_cum_pct": "formal cum%",
        "formal_gate_max_dd_pct": "formal maxDD%",
        "primary_artifact": "主要 artifact",
        "note": "展示要点",
    }
    catalog_cols = ["rank_id", "title", "source_type", "status", "family", "registry_stage", "registry_role", "registry_increment", "report_href", "best_ic_factor", "best_ic_mean", "best_ir", "best_ic_observations", "artifact_hit_count_sampled", "research_note"]
    catalog_labels = {
        "rank_id": "Rank",
        "title": "报告标题",
        "source_type": "来源",
        "status": "状态",
        "family": "策略家族",
        "registry_stage": "P2/P3",
        "registry_role": "角色",
        "registry_increment": "独特增量",
        "report_href": "报告",
        "best_ic_factor": "最佳IC因子",
        "best_ic_mean": "best IC",
        "best_ir": "best IR",
        "best_ic_observations": "IC样本",
        "artifact_hit_count_sampled": "artifact样例数",
        "research_note": "说明",
    }
    family_stats = pd.DataFrame()
    status_stats = pd.DataFrame()
    if not catalog_df.empty:
        family_stats = catalog_df.groupby("family", dropna=False).size().reset_index(name="reports").sort_values("reports", ascending=False)
        status_stats = catalog_df.groupby("status", dropna=False).size().reset_index(name="reports").sort_values("reports", ascending=False)
    family_nav = ""
    if not family_stats.empty:
        family_nav = "<div class='toc'>" + "".join(
            f"<a class='btn' href='#family-{escape(slugify(str(row.family)))}'>{escape(str(row.family))} ({int(row.reports)})</a>"
            for _, row in family_stats.iterrows()
        ) + "</div>"
    catalog_overview = catalog_overview_html(catalog_df)
    family_catalog_html = family_group_html(catalog_df, catalog_cols, catalog_labels)
    top_ic_cards = top_ic_cards_html(ic_df, catalog_df)
    active_observation_cards = active_observations_html(evidence_df, reviewed_ic_df, pending_ic_df, coverage_df)
    active_observation_audit_table = active_observation_audit_table_html(evidence_df, reviewed_ic_df, pending_ic_df, coverage_df)
    evidence_overview = evidence_overview_html(evidence_df)
    evidence_definitions = evidence_definitions_html()
    ic_audit_plan = ic_audit_plan_html()
    ic_coverage_html = ic_coverage_audit_html(coverage_df)
    ic_scatter_chart = SITE_DIR / "reviewed_ic_distribution_scatter.png"
    if ic_scatter_chart.exists():
        ic_distribution_html = (
            "<div class='chart-card'>"
            "<h3>IC 分布总览</h3>"
            "<a href='reviewed_ic_distribution_scatter.png'>"
            "<img src='reviewed_ic_distribution_scatter.png' alt='Reviewed IC distribution scatter chart'>"
            "</a>"
            "<p class='muted'>每个点代表一个已审计的因子-horizon 组合；纵轴是 IC mean，横轴按各 rank 的最佳 |IR| / |IC| 排序，颜色区分 current candidate 与 audit-only，点大小表示 IC 样本数。读图时先看一条 rank 的点是否整体稳定地偏离 0，再回到下方表格核对 factor 定义、horizon 和样本纪律。</p>"
            "</div>"
        )
    else:
        ic_distribution_html = "<p class='muted'>IC distribution chart not generated.</p>"
    reviewed_audit = reviewed_ic_df.copy()
    if not reviewed_audit.empty:
        reviewed_audit["audit_role"] = (
            reviewed_audit.get("ic_display_role", pd.Series("", index=reviewed_audit.index))
            .fillna("")
            .replace({"current_candidate": "current_candidate", "audit_only": "audit_only"})
        )
        reviewed_audit = reviewed_audit.sort_values(["audit_role", "display", "factor", "horizon_bars"], ascending=[True, True, True, True])
    reviewed_audit_cols = ["display", "factor", "horizon_bars", "audit_role", "ic_observations", "source", "ic_review_note", "report_href"]
    reviewed_audit_labels = {
        "display": "研究线",
        "factor": "因子",
        "horizon_bars": "预测 horizon(bar)",
        "audit_role": "展示角色",
        "ic_observations": "IC 样本数",
        "source": "复核来源",
        "ic_review_note": "审计结论",
        "report_href": "报告",
    }
    pending_focus_rows: list[dict[str, object]] = []
    pending_focus_specs = (
        (
            "Rank53 auto frame IC",
            "breakdown_reclaim_short_signal",
            4,
            "已复核定义与数值，但不提升：report hard verdict 是 park / evidence pool；6bps 成本后 short 读法 mean_total_return 约 -2.88%，改善主要来自 retention 下降与 sample thinning。"
        ),
        (
            "Rank50 auto frame IC",
            "signal_structural_reclaim_plus_htf",
            4,
            "已复核定义与数值，但不提升：report hard verdict 是 park / evidence pool；主变体 6bps 下跨资产 mean_total_return 约 -4.63%，false reclaim 与 no-trade 比例过高。"
        ),
        (
            "Rank35 auto frame IC",
            "signal_combo_long_only",
            16,
            "已复核定义与数值，但不提升：IR 较高主要来自极小样本，ic_observations=10；report hard verdict 仍是 park / evidence pool，不足以作为正式横向比较。"
        ),
        (
            "Rank32 auto frame IC",
            "reclaim_short_signal",
            16,
            "不提升：尽管数值高，但 Rank32/32B 家族已与 future/lookahead audit 强相关，默认归入 archive 审计材料，不进入 reviewed 或 current-candidate 口径。"
        ),
        (
            "Rank86 auto frame IC",
            "ema_psar_follow_short_signal",
            16,
            "暂不提升：已独立复算一致，但该行只对应 Rank86 的 setup 子臂，ic_observations=93 过薄；页面 hard verdict 仅到 `P1 keep / worth one Light Stability Pack check`，不足以进入 reviewed 横向主表。"
        ),
        (
            "Rank31 auto frame IC",
            "base_short_signal",
            4,
            "暂不提升：数值不差，但它更接近 Rank31 baseline / base momentum 组件列，而不是页面最终对外叙事的主变体；同时 6bps 下各主变体跨资产 mean_total_return 全面为负，当前更适合作为后续排查队列，不进入 reviewed 主表。"
        ),
    )
    pending_focus_cols = ["display", "factor", "horizon_bars", "ic_mean", "ir", "ic_observations", "audit_holdout_reason", "report_href"]
    pending_focus_labels = {
        "display": "研究线",
        "factor": "因子",
        "horizon_bars": "预测 horizon(bar)",
        "ic_mean": "IC mean",
        "ir": "IR = IC mean/std",
        "ic_observations": "IC 样本数",
        "audit_holdout_reason": "暂不提升原因",
        "report_href": "报告",
    }
    for strategy, factor, horizon, reason in pending_focus_specs:
        match = pending_ic_df[
            pending_ic_df["strategy"].astype(str).eq(strategy)
            & pending_ic_df["factor"].astype(str).eq(factor)
            & pd.to_numeric(pending_ic_df["horizon_bars"], errors="coerce").eq(horizon)
        ]
        if match.empty:
            continue
        row = match.iloc[0].to_dict()
        row["audit_holdout_reason"] = reason
        pending_focus_rows.append(row)
    pending_focus_df = pd.DataFrame(pending_focus_rows)
    low_obs_threshold = 100
    candidate_low_obs_count = int(pd.to_numeric(current_candidate_ic_df.get("ic_observations"), errors="coerce").lt(low_obs_threshold).sum()) if not current_candidate_ic_df.empty else 0
    audit_low_obs_count = int(pd.to_numeric(audit_only_ic_df.get("ic_observations"), errors="coerce").lt(low_obs_threshold).sum()) if not audit_only_ic_df.empty else 0
    live_like_count = int(catalog_df["status"].isin(["live/monitor", "canary", "shadow"]).sum()) if not catalog_df.empty else 0
    paper_count = int(catalog_df["status"].eq("paper").sum()) if not catalog_df.empty else 0
    p3_count = int(catalog_df.get("registry_stage", pd.Series(dtype=str)).fillna("").eq("P3").sum()) if not catalog_df.empty else 0
    p2_count = int(catalog_df.get("registry_stage", pd.Series(dtype=str)).fillna("").eq("P2").sum()) if not catalog_df.empty else 0
    chart_cards: list[str] = []
    for _, row in evidence_df.iterrows():
        chart = str(row.get("chart") or "")
        if not chart:
            continue
        chart_path = SITE_DIR / chart
        if chart_path.exists():
            chart_cards.append(
                f"<div class='chart-card'><h3>{escape(str(row.get('strategy')))}</h3><a href='{escape(chart)}'><img src='{escape(chart)}' alt='{escape(str(row.get('strategy')))} chart'></a><p class='muted'>{escape(str(row.get('note') or ''))}</p></div>"
            )
    charts_html = "<div class='charts'>" + "".join(chart_cards) + "</div>" if chart_cards else "<p class='muted'>No generated charts.</p>"

    css = """
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    body { margin:0; background:#f6f7f9; color:#172033; font:14px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif; }
    .wrap { max-width:1240px; margin:0 auto; padding:28px 18px 56px; }
    .hero { background:#ffffff; border:1px solid #d9dee8; border-radius:8px; padding:22px 24px; }
    h1 { margin:0 0 8px; font-size:28px; letter-spacing:0; }
    h2 { margin:28px 0 10px; font-size:20px; }
    h3 { margin:20px 0 8px; font-size:16px; }
    p { margin:8px 0; }
    .muted { color:#667085; }
    .grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin:16px 0; }
    .card { background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:14px 16px; min-height:94px; }
    .card h3 { margin-top:0; }
    .k { color:#667085; font-size:12px; text-transform:uppercase; }
    .v { margin-top:5px; font-size:24px; font-weight:700; }
    .s { margin-top:4px; color:#667085; font-size:12px; }
    .section { background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:18px 20px; margin-top:16px; overflow:auto; }
    table { width:100%; border-collapse:collapse; min-width:980px; }
    th,td { border-bottom:1px solid #e5e8ef; padding:8px 10px; vertical-align:top; text-align:left; }
    th { background:#f1f4f8; color:#344054; font-size:12px; white-space:nowrap; }
    td.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
    .pos { color:#067647; }
    .neg { color:#b42318; }
    a { color:#175cd3; text-decoration:none; }
    a:hover { text-decoration:underline; }
    .nav { display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }
    .btn { border:1px solid #cfd6e4; border-radius:6px; background:#fff; padding:6px 9px; font-weight:600; }
    .toc { display:flex; flex-wrap:wrap; gap:8px; margin:12px 0 16px; }
    .note { border-left:4px solid #175cd3; background:#eff6ff; padding:10px 12px; margin:12px 0; }
    .warn { border-left-color:#dc6803; background:#fff7ed; }
    .subtle { color:#667085; font-weight:500; font-size:12px; }
    .two { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
    .definition { background:#f8fafc; border:1px solid #e4e7ec; border-radius:8px; padding:12px 14px; }
    .tools { display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin:12px 0; }
    .search { min-width:280px; flex:1; border:1px solid #cfd6e4; border-radius:6px; padding:8px 10px; font:inherit; }
    .family-block { border:1px solid #d9dee8; border-radius:8px; margin:10px 0; padding:0 12px 12px; background:#fff; }
    .family-block summary { cursor:pointer; padding:12px 0; font-weight:700; font-size:16px; }
    .mini-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:12px; }
    .mini-card { border:1px solid #d9dee8; border-radius:8px; background:#fff; padding:12px 14px; }
    .mini-card h3 { margin-top:0; }
    .lead { display:grid; grid-template-columns:1.1fr .9fr; gap:12px; align-items:stretch; }
    .lead-panel { background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:16px 18px; }
    .lead-panel h2 { margin-top:0; }
    .priority-list { margin:8px 0 0; padding-left:18px; }
    .priority-list li { margin:6px 0; }
    .section-nav { display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 0; }
    .fold { padding:0; overflow:hidden; }
    .fold > summary { cursor:pointer; list-style:none; padding:16px 20px; font-weight:700; font-size:18px; display:flex; align-items:center; justify-content:space-between; }
    .fold > summary::-webkit-details-marker { display:none; }
    .fold > summary::after { content:'展开'; color:#667085; font-size:12px; font-weight:600; }
    .fold[open] > summary::after { content:'收起'; }
    .fold-body { padding:0 20px 18px; border-top:1px solid #e5e8ef; }
    .compact-stack { display:grid; gap:14px; }
    .section-kicker { margin:0 0 6px; color:#667085; font-size:12px; text-transform:uppercase; }
    .playbook { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:12px; }
    .playbook-card { border:1px solid #d9dee8; border-radius:8px; padding:14px 16px; background:#fff; }
    .playbook-card p { margin:6px 0; }
    .metric-row { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 10px; }
    .metric-chip { display:inline-flex; gap:5px; align-items:center; border:1px solid #d0d5dd; border-radius:6px; padding:4px 7px; background:#f8fafc; color:#344054; font-size:12px; max-width:100%; }
    .metric-chip b { color:#101828; }
    .charts { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:14px; }
    .chart-card { border:1px solid #d9dee8; border-radius:8px; padding:12px; background:#fff; }
    .chart-card img { width:100%; height:auto; display:block; border:1px solid #eaecf0; border-radius:6px; }
    .hidden-row { display:none; }
    @media (max-width: 860px) { .grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .two, .lead { grid-template-columns:1fr; } }
    @media (max-width: 560px) { .grid { grid-template-columns:1fr; } .wrap { padding:14px 10px 40px; } }
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Momentum 因子研究结果库</title>
  <style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>Momentum 因子研究结果库</h1>
    <p class="muted">统一入口：把 200+ rank 研究报告、代表策略、因子 IC/IR、负例审计和 live/paper 链路放在同一页。Generated: {escape(generated_at)}</p>
    <div class="note warn">轻量发布模式可只同步本研究库页面和对应 artifacts。本页核心目录、分类、IC/IR、CSV 和 PNG 图均可独立访问；表格里的 open 链接指向完整站内报告，只有在完整 reports 站点已发布时才保证可打开。</div>
    <div class="nav">
      <a class="btn" href="../index.html">Reports 首页</a>
      <a class="btn" href="workflow.html">工作流 / 定时任务</a>
      <a class="btn" href="momentum/rank151_source_breakdown.html">Rank151 来源拆解</a>
      <a class="btn" href="../factors/rank_strategy_hub/report.html">Rank Strategy Hub</a>
      <a class="btn" href="../factors/rank_registry_p3_p2/report.html">P3/P2 Registry</a>
      <a class="btn" href="../factors/rank32b/report.html">Rank32B 审计案例</a>
      <a class="btn" href="../factors/live_trading_center/report.html">Live Trading Center</a>
    </div>
    <div class="section-nav">
      <a class="btn" href="workflow.html">工作流页</a>
      <a class="btn" href="momentum/rank151_source_breakdown.html">Rank151 来源拆解</a>
      <a class="btn" href="#complete-work">完整研究样例</a>
      <a class="btn" href="#active-observations">当前候选</a>
      <a class="btn" href="#key-ranks">关键 Rank</a>
      <a class="btn" href="#key-charts">关键图</a>
      <a class="btn" href="#ic-core">IC / IR</a>
      <a class="btn" href="#performance-matrix">Paper / Live</a>
      <a class="btn" href="#appendix-library">附录目录</a>
      <a class="btn" href="#appendix-audit">附录审计</a>
    </div>
  </div>

  <div class="grid">
    <div class="card"><div class="k">Rank 报告页</div><div class="v">{report_count}</div><div class="s">自动扫描 reports/site/factors + paper</div></div>
    <div class="card"><div class="k">唯一 Rank</div><div class="v">{unique_rank_count}</div><div class="s">含 scout / paper / live / registry</div></div>
    <div class="card"><div class="k">审计通过 IC rows</div><div class="v">{len(reviewed_ic_df)}</div><div class="s">只展示逐策略确认口径的行</div></div>
    <div class="card"><div class="k">待审计 IC 线</div><div class="v">{pending_ic_strategy_count}</div><div class="s">自动候选不进主榜；自动 frame 覆盖 {included_auto_count} 组</div></div>
  </div>

  <div class="grid">
    <div class="card"><div class="k">Max |IC|</div><div class="v">{fmt_num(top_ic)}</div><div class="s">当前候选口径，已排除归档/审计线</div></div>
    <div class="card"><div class="k">Max |IR|</div><div class="v">{fmt_num(top_ir)}</div><div class="s">当前候选口径，IC mean / IC std</div></div>
    <div class="card"><div class="k">分类维度</div><div class="v">{catalog_df['family'].nunique() if not catalog_df.empty else 0}</div><div class="s">按策略家族粗分类</div></div>
    <div class="card"><div class="k">状态维度</div><div class="v">{catalog_df['status'].nunique() if not catalog_df.empty else 0}</div><div class="s">live / paper / shadow / research</div></div>
  </div>

  <div class="lead" id="summary">
    <div class="lead-panel">
      <h2>读者先看什么</h2>
      <p>这不是单一策略报告，而是一套从研究发现到 paper/live 治理、归档和反证审计的量化研究资产库。阅读时先看当前仍可继续验证的候选，再看已归档案例如何暴露 future/lookahead、选池偏差、成本后失效等问题。</p>
      <ol class="priority-list">
        <li><b>完整研究样例：</b>若你是拿这页给别人展示研究方法，先看“完整研究样例”。这里不按当前可上线排序，而按研究工作是否做完整排序，归档线也会前置。</li>
        <li><b>当前可继续验证：</b>先看“当前候选 / 运行观察”，只放仍处于 paper/admission/shadow 且未被 close-out 否定的候选。</li>
        <li><b>归档和反证：</b>Rank154 已 failed release candidate，Rank213 旧 frozen30 叙事有选池/幸存者偏差风险，Rank32B 已因 future/lookahead 下线。</li>
        <li><b>横向验证：</b>IC/IR 表把可计算因子放在同一口径下比较；已确认 future/lookahead、归档或口径失效的线不放进当前候选榜单。</li>
        <li><b>研究纪律：</b>Rank29 和 archive/negative-control 页面展示失败、退场、veto 和治理证据，说明研究库不是只包装正例。</li>
      </ol>
    </div>
    <div class="lead-panel">
      <h2>当前资产盘点</h2>
      <p><b>{report_count}</b> 个 rank 相关报告页，覆盖 <b>{unique_rank_count}</b> 个唯一 rank；其中 P3 条目 <b>{p3_count}</b> 行、P2 条目 <b>{p2_count}</b> 行。</p>
      <p>状态上，live/canary/shadow 相关报告 <b>{live_like_count}</b> 行，paper 报告 <b>{paper_count}</b> 行；paper/live evidence 矩阵记录 <b>{len(evidence_df)}</b> 条运行证据，含 <b>{int(evidence_df['curve_exists'].fillna(False).sum()) if not evidence_df.empty and 'curve_exists' in evidence_df.columns else 0}</b> 条曲线 artifact。</p>
    <p>IC/IR 当前分为两层：审计通过 <b>{ic_strategy_count}</b> 条研究线、<b>{len(reviewed_ic_df)}</b> 个因子-horizon 组合；待审计 <b>{pending_ic_strategy_count}</b> 条研究线、<b>{len(pending_ic_df)}</b> 个候选组合。待审计行只作为排查队列，不作为正式横向排名。</p>
    </div>
  </div>

  <div class="section" id="map">
    <h2>如何阅读这页</h2>
    <div class="two">
      <div class="definition">
        <h3>研究管线</h3>
        <p>Rank 是候选研究编号；P3/P2 registry 记录进入重点跟踪的研究线，字段包含母题、角色、独特增量、当前状态和下一步。阅读时先看研究从 idea、最小复现、稳定性检查、paper/shadow 到 live/canary 的晋级路径。</p>
      </div>
      <div class="definition">
        <h3>横向比较</h3>
        <p>IC/IR 只在可形成横截面的 bar-level frame 上计算：需要 timestamp、close、可识别资产，且同一时点至少 3 个资产可比。current signal、status、lane snapshot 或单资产 frame 不强行算 IC，仍保留报告、回测和治理证据。</p>
      </div>
      <div class="definition">
        <h3>定量定义</h3>
        <p>IC 是同一时间截面上因子值与未来收益的 Spearman rank correlation；IR 是 IC 时间序列的 mean/std。horizon=1/4/16 对多数 15m frame 约等于 15m/1h/4h。</p>
      </div>
      <div class="definition">
        <h3>成果证据</h3>
        <p>Paper/live 矩阵优先展示收益曲线、live-vs-shadow、formal backtest、status artifact 和回测报告；关键负例也保留，用来解释为什么某些 rank 被下线、归档或只做观察。</p>
      </div>
    </div>
  </div>

  <div class="section" id="complete-work">
    <p class="section-kicker">Core</p>
    <h2>完整研究样例</h2>
    <p class="muted">这一节优先服务“展示研究能力”而不是“展示当前最该上线什么”。排序逻辑因此改成：谁把因子定义、数据清洗、时间对齐、未来函数排查、IC/Rank IC、分组收益、交易成本、样本外、暴露和最终 memo 做得更完整，谁就更靠前；即使该线最后被归档，也照样前置。</p>
    {complete_research_showcase_html()}
  </div>

  <div class="section" id="active-observations">
    <p class="section-kicker">Core</p>
    <h2>当前候选 / 运行观察</h2>
    <p class="muted">这里是推荐优先看的当前观察对象，不等于已验证 alpha。筛选只保留有 primary artifact、仍处于 paper/runner/queue/shadow/canary/live 观察链路的行，并显式排除 Rank154、Rank213、Rank32B/32 这类已经归档、存在 future/lookahead、universe causality 或 close-out 风险的研究线。展示顺序上，已经完成审计且有明确 IC/IR 的对象会优先放在最前；其余 runner/live 观察对象放在后面，并写清楚为什么当前还不能正式横向比较。</p>
    {active_observation_cards}
    <details class="fold">
      <summary>当前观察 IC 审计台账</summary>
      <div class="fold-body">
        <p class="muted">这张台账逐条说明 active 观察对象为什么能发布 IC、为什么只能保留为 audit-only，或为什么当前结构上还不能发布横截面 IC。对于没有 IC 的行，这里会写明缺的是 frame、target 还是横截面资产维度。</p>
        {active_observation_audit_table}
      </div>
    </details>
  </div>

  <div class="section" id="key-ranks">
    <p class="section-kicker">Core</p>
    <h2>关键 Rank 研究说明</h2>
    <p class="muted">这一节按“可继续验证候选 → 负例/归档/审计案例”组织。Rank154、Rank213、Rank32B 都不能再被包装成当前正例主线：154 已归档，213 旧口径有选池/幸存者偏差风险且 live canary 已停止，32B 因 future/lookahead audit 下线。</p>
    {key_rank_playbook_html()}
  </div>

  <div class="section" id="key-charts">
    <p class="section-kicker">Core</p>
    <h2>关键收益曲线 / 回测图</h2>
    {charts_html}
  </div>

  <div class="section" id="ic-core">
    <p class="section-kicker">Core</p>
    <h2>因子 IC / IR：定义、治理与横向比较</h2>
    <p class="muted">这一节先回答“IC 在这里具体怎么算”，再回答“哪些行可以进入当前候选主榜”。页面把数学定义、策略 hard verdict 和样本纪律拆开，避免把单行好看的数值误读成已经完成的 alpha 结论。</p>
    <div class="note">截至 {escape(generated_at)}，本页 reviewed IC 已独立复算通过 <b>{len(reviewed_ic_df)}</b> 个因子-horizon 组合、覆盖 <b>{ic_strategy_count}</b> 条研究线；其中 <b>{current_candidate_count}</b> 行进入 current candidate 主榜，<b>{audit_only_count}</b> 行保留为 audit-only 对照。audit-only 的含义是“定义和数值都对，但页面 hard verdict 仍停留在 park / archive / evidence pool / mixed evidence”，所以它们只保留为研究治理证据。</div>
    <div class="two">
      <div class="definition">
        <h3>IC 的数学口径</h3>
        <p>IC 统一按同一 timestamp 的横截面计算：对每个时点，把因子值 <code>factor_t</code> 与未来收益 <code>r(t,t+h)</code> 做 Spearman rank correlation，再在时间维上取均值。它回答的是“同一时点里，分数更高的资产，未来 h 根 bar 表现是否更强/更弱”。</p>
      </div>
      <div class="definition">
        <h3>IR 的含义</h3>
        <p>IR 定义为 IC 时间序列的 <code>mean / std</code>。它不是策略 Sharpe，也不等于收益曲线质量；它只衡量横截面排序信号是否稳定。页面因此把 IC/IR 和 paper/live PnL 分开展示，避免把排序能力和交易实现混成一件事。</p>
      </div>
      <div class="definition">
        <h3>符号方向怎么读</h3>
        <p>IC 的正负号必须结合信号语义解释。对于 long-only score，更常见的是正 IC；对于 short signal 或 bearish setup，负 IC 往往才符合预期。因此主榜按 <code>|IR|</code>、<code>|IC|</code> 和样本数排序，但具体解读仍要回到该因子的方向定义。</p>
      </div>
      <div class="definition">
        <h3>为什么高 IR 也不能直接 promotion</h3>
        <p>页面 hard verdict 的优先级高于单行 IC。若该 rank 已被 archive、future/lookahead、universe causality、成本后失效或 evidence-pool 结论否定，那么即使某个 setup 行可复算、甚至 <code>|IR|</code> 很高，也只能进入 audit-only 或 holdout，而不能包装成当前候选。</p>
      </div>
    </div>
    <div class="two">
      <div class="definition">
        <h3>一行 IC 里最该看什么</h3>
        <p><b>factor</b> 代表页面上具体哪一层信号或 gate；<b>horizon</b> 是未来几根 bar；<b>obs</b> 是有效横截面样本数；<b>assets</b> 是每次横截面的平均可比资产数量。先确认它是不是页面主信号，再比较数值。</p>
      </div>
      <div class="definition">
        <h3>样本纪律</h3>
        <p>本页把 <code>obs &lt; {low_obs_threshold}</code> 的行默认视为弱证据。当前 current candidate 中有 <b>{candidate_low_obs_count}</b> 行低样本，audit-only 中有 <b>{audit_low_obs_count}</b> 行低样本；这类行可作为线索，但不足以单独支撑 promotion。</p>
      </div>
    </div>
    {ic_distribution_html}
    <h3>当前候选 IC 主榜</h3>
    <p class="muted">这里只有仍处于可继续验证链路、且已经完成信号定义/时间对齐/未来函数审计的行，适合做同口径横向比较。读法是先看它是否对应页面主信号，再看 IC、IR 和样本数是否一致支持该叙事。</p>
    {table_html(candidate_main, ic_cols, ic_labels, numeric={'horizon_bars','ic_mean','ir','ic_observations','assets'}, pct={'positive_rate'}, max_rows=40)}
    <details class="fold">
      <summary>对照与审计附表</summary>
      <div class="fold-body compact-stack">
        <div>
          <h3>审计通过但只作对照的 IC</h3>
          <p class="muted">这些行的公式和数值已经独立复算通过，但所在 rank 的页面 hard verdict 仍不支持升格。它们保留在这里，是为了展示“为什么不能只看高 IR/高 IC 就下结论”。</p>
          {table_html(audit_only_main, ic_cols, ic_labels, numeric={'horizon_bars','ic_mean','ir','ic_observations','assets'}, pct={'positive_rate'}, max_rows=40)}
        </div>
        <div>
          <h3>IC 审计台账</h3>
          <p class="muted">台账列出每条 reviewed 行的展示角色和复核结论，方便追踪哪些已经进入主榜，哪些只允许作为 audit-only 证据。</p>
          {table_html(reviewed_audit, reviewed_audit_cols, reviewed_audit_labels, numeric={'horizon_bars','ic_observations'}, max_rows=40)}
        </div>
        <div>
          <h3>Top IC/IR 研究线</h3>
          <p class="muted">按 |IR|、|IC| 和样本数排序，但先按 rank 和策略家族去重，并把已归档、future/lookahead 或核心 causality 风险案例移出当前候选榜单。</p>
          {top_ic_cards}
        </div>
      </div>
    </details>
  </div>

  <div class="section" id="performance-matrix">
    <p class="section-kicker">Core</p>
    <h2>Paper / Live 成果矩阵</h2>
    <p class="muted">这一节把已经上实盘、曾经上实盘后下线、仍在 paper/shadow 的因子放在一起；可以直接从状态跳到回测报告、收益曲线和主要 artifact。</p>
    {evidence_overview}
    <details class="fold">
      <summary>完整 evidence 明细</summary>
      <div class="fold-body">
        {table_html(evidence_df, evidence_cols, evidence_labels, numeric={'lifetime_return','current_drawdown','closed_trades','live_net_pnl_usdt','formal_gate_net_cum_pct','formal_gate_max_dd_pct'}, pct={'lifetime_return','current_drawdown'}, max_rows=180)}
      </div>
    </details>
  </div>

  <details class="section fold" id="appendix-library">
    <summary>附录：全量目录与背景说明</summary>
    <div class="fold-body compact-stack">
      <div>
        <h3>证据等级与字段定义</h3>
        <p class="muted">这一节定义页面里的状态、artifact 和关键指标。读者应先区分“仍可继续验证的候选”和“归档/审计/反证”，再比较 IC/IR 或收益曲线。</p>
        {evidence_definitions}
      </div>
      <div>
        <h3>全量 Rank 研究报告目录</h3>
        <div class="note">这里逐一扫描现有 HTML 报告页并按状态、来源、策略家族归类。IC/IR 只对有可用 frame 或已有 IC artifact 的研究线计算；没有 bar-level frame 的报告仍保留在目录中，作为论文阅读、回测、paper/live 证据入口。</div>
        {catalog_overview}
        <h3>策略家族统计</h3>
        {table_html(family_stats, ['family','reports'], {'family':'策略家族','reports':'报告数'}, numeric={'reports'}, max_rows=30)}
        <h3>状态统计</h3>
        {table_html(status_stats, ['status','reports'], {'status':'状态','reports':'报告数'}, numeric={'reports'}, max_rows=30)}
        <h3>按策略家族跳转</h3>
        {family_nav}
        <div class="tools">
          <input id="catalogSearch" class="search" type="search" placeholder="搜索 rank、家族、状态、因子、说明..." />
          <button class="btn" type="button" onclick="setFamilyOpen(true)">展开全部</button>
          <button class="btn" type="button" onclick="setFamilyOpen(false)">折叠全部</button>
        </div>
        <h3>分组报告清单</h3>
        {family_catalog_html}
      </div>
      <div>
        <h3>研究叙事线</h3>
        <div class="note">推荐阅读顺序：先看研究系统如何把 idea 进入 P3/P2 registry，再看仍可继续验证的候选线；随后用 IC/IR 表说明不是只看 PnL；最后重点查看 Rank154、Rank213、Rank32B、Rank29 这类归档/审计/负例，理解哪些证据不能再作为当前 alpha 主张。</div>
        {table_html(story_df, story_cols, story_labels, numeric={'rows','avg_trades','avg_total_return','avg_win_rate','avg_avg_net_ret'}, pct={'avg_win_rate','avg_avg_net_ret'}, max_rows=20)}
      </div>
    </div>
  </details>

  <details class="section fold" id="appendix-audit">
    <summary>附录：待审计队列、覆盖台账与产物位置</summary>
    <div class="fold-body compact-stack">
      <div id="pending-ic-audit">
        <h3>待审计 IC 队列</h3>
        <div class="note warn">这里的行只用于后续逐条排查，不作为展示成果或横向排名。下一步应按策略逐个定义：信号列、交易方向、预测 horizon、资产池、时间对齐、成本和是否存在未来函数；审计通过后才可进入正式 IC/IR 并列表。</div>
        <h3>高 IR 但暂不提升的样例</h3>
        {table_html(pending_focus_df, pending_focus_cols, pending_focus_labels, numeric={'horizon_bars','ic_mean','ir','ic_observations'}, max_rows=12)}
        <h3>逐策略审计计划</h3>
        <p class="muted">优先从当前候选和运行观察线开始，一个 rank 一个 rank 审；Rank32B、Rank154、Rank213 已明确不进入主线，只作为归档/审计材料。</p>
        {ic_audit_plan}
        <h3>自动候选明细</h3>
        {table_html(pending_main, pending_ic_cols, ic_labels, numeric={'horizon_bars','ic_mean','ir','ic_observations','assets'}, max_rows=80)}
      </div>
      <div id="ic-coverage-audit">
        <h3>IC 覆盖审计</h3>
        {ic_coverage_html}
      </div>
      <div>
        <h3>正向候选 Top 12</h3>
        <p class="muted">按 IR 和 IC mean 降序，只作为快速定位候选，不替代完整稳定性、成本和 OOS 检查。</p>
        {table_html(best, ic_cols, ic_labels, numeric={'horizon_bars','ic_mean','ir','ic_observations','assets'}, pct={'positive_rate'}, max_rows=12)}
      </div>
      <div>
        <h3>产物位置</h3>
        <p>IC/IR CSV: <a href="{escape(library_artifact_href(IC_SUMMARY))}"><code>{escape(library_artifact_label(IC_SUMMARY))}</code></a></p>
        <p>Story CSV: <a href="{escape(library_artifact_href(STORY_SUMMARY))}"><code>{escape(library_artifact_label(STORY_SUMMARY))}</code></a></p>
        <p>Paper/Live Evidence CSV: <a href="{escape(library_artifact_href(EVIDENCE_SUMMARY))}"><code>{escape(library_artifact_label(EVIDENCE_SUMMARY))}</code></a></p>
        <p>Rank Report Catalog CSV: <a href="{escape(library_artifact_href(RANK_REPORT_CATALOG))}"><code>{escape(library_artifact_label(RANK_REPORT_CATALOG))}</code></a></p>
        <p>Auto IC Coverage CSV: <a href="{escape(library_artifact_href(AUTO_IC_COVERAGE))}"><code>{escape(library_artifact_label(AUTO_IC_COVERAGE))}</code></a></p>
        <p>轻量发布：本页与配套 CSV/PNG/artifact 可独立同步到外网访问。</p>
      </div>
    </div>
  </details>
</div>
<script>
function setFamilyOpen(open) {{
  document.querySelectorAll('.family-block').forEach(function(el) {{ el.open = open; }});
}}
const searchBox = document.getElementById('catalogSearch');
if (searchBox) {{
  searchBox.addEventListener('input', function() {{
    const q = searchBox.value.trim().toLowerCase();
    document.querySelectorAll('tbody tr[data-search]').forEach(function(row) {{
      const hit = !q || row.dataset.search.indexOf(q) >= 0;
      row.classList.toggle('hidden-row', !hit);
      if (hit) {{
        const block = row.closest('.family-block');
        if (block && q) block.open = true;
      }}
    }});
  }});
}}
</script>
</body>
</html>"""


def main() -> int:
    ensure_dirs()
    import os

    reuse_ic = os.environ.get("OPENCLAW_SHOWCASE_REUSE_IC") == "1" and IC_SUMMARY.exists() and AUTO_IC_COVERAGE.exists()
    if reuse_ic:
        ic_df = apply_ic_review_rules(pd.read_csv(IC_SUMMARY))
        coverage_df = pd.read_csv(AUTO_IC_COVERAGE)
        print(f"[info] reused {IC_SUMMARY.relative_to(ROOT)} rows={len(ic_df)}")
    else:
        rows: list[dict[str, object]] = []
        auto_specs, coverage_df = discover_auto_factor_specs()
        all_specs = list(FACTOR_SPECS) + auto_specs
        coverage_df.to_csv(AUTO_IC_COVERAGE, index=False)
        for spec in all_specs:
            rows.extend(compute_ic_rows(spec))
        append_existing_ic(rows)
        append_rank342_snapshot_ic(rows)
        ic_df = pd.DataFrame(rows)
        if not ic_df.empty:
            for col in ("ic_mean", "ic_median", "ic_std", "ir", "positive_rate", "ic_observations", "assets"):
                ic_df[col] = pd.to_numeric(ic_df[col], errors="coerce")
            ic_df = ic_df.sort_values(["strategy", "factor", "horizon_bars"])
        ic_df = apply_ic_review_rules(ic_df)
    ic_df.to_csv(IC_SUMMARY, index=False)

    story_df = summarize_story_artifacts()
    story_df.to_csv(STORY_SUMMARY, index=False)

    evidence_df = generate_missing_evidence_pages(summarize_evidence_items())
    evidence_df.to_csv(EVIDENCE_SUMMARY, index=False)

    catalog_df = attach_ic_summary_to_catalog(discover_rank_report_catalog(), ic_df)
    catalog_df.to_csv(RANK_REPORT_CATALOG, index=False)

    reviewed_ic_df = reviewed_ic_rows(ic_df, catalog_df)
    generate_charts(reviewed_ic_df)
    sync_library_artifacts()

    html = render_page(ic_df, story_df, evidence_df, catalog_df, coverage_df)
    OUT_HTML.write_text(html, encoding="utf-8")
    ALIAS_OUT_HTML.write_text(html, encoding="utf-8")
    print(f"[ok] wrote {IC_SUMMARY.relative_to(ROOT)} rows={len(ic_df)}")
    print(f"[ok] wrote {RANK_REPORT_CATALOG.relative_to(ROOT)} rows={len(catalog_df)}")
    print(f"[ok] wrote {OUT_HTML.relative_to(ROOT)}")
    print(f"[ok] wrote {ALIAS_OUT_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
