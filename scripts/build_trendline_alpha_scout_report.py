#!/usr/bin/env python3
from __future__ import annotations

import csv
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
OUT_PATH = OUT_DIR / "report.html"
ART_DIR = ROOT / "reports" / "artifacts" / "literature"
SHORTLIST_PATH = ART_DIR / "scout_seat_fast_cycle_crypto_shortlist_v1.csv"
LOCAL_SCOUT_ART_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m"
LOCAL_SCOUT_VARIANT_PATH = LOCAL_SCOUT_ART_DIR / "variant_aggregate.csv"
LOCAL_SCOUT_META_PATH = LOCAL_SCOUT_ART_DIR / "trial_meta.csv"
LOCAL_SCOUT_REPORT_HREF = "../../factors/scout_tau_band_breakout_15m/report.html"

RANK2_SPEC_ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
RANK2_SPEC_PATH = RANK2_SPEC_ART_DIR / "clean_room_spec_v1.csv"
RANK2_SPEC_META_PATH = RANK2_SPEC_ART_DIR / "spec_meta.csv"
RANK2_VARIANT_PATH = RANK2_SPEC_ART_DIR / "variant_aggregate.csv"
RANK2_TRIAL_META_PATH = RANK2_SPEC_ART_DIR / "trial_meta.csv"
RANK2_MONITORING_PATH = RANK2_SPEC_ART_DIR / "combo_all_paper_candidate_monitoring_board.csv"
RANK2_SPEC_REPORT_HREF = "../../factors/scout_volume_supportflip_higherlow_15m/report.html"

RANK3_SPEC_ART_DIR = ROOT / "reports" / "artifacts" / "scout_third_touch_ema_macd_15m"
RANK3_SPEC_PATH = RANK3_SPEC_ART_DIR / "clean_room_spec_v1.csv"
RANK3_SPEC_META_PATH = RANK3_SPEC_ART_DIR / "spec_meta.csv"
RANK3_VARIANT_PATH = RANK3_SPEC_ART_DIR / "variant_aggregate.csv"
RANK3_TRIAL_META_PATH = RANK3_SPEC_ART_DIR / "trial_meta.csv"
RANK3_SPEC_REPORT_HREF = "../../factors/scout_third_touch_ema_macd_15m/report.html"

RANK4_ART_DIR = ROOT / "reports" / "artifacts" / "scout_crypto_pairs_stat_arb_15m"
RANK4_PAIR_SUMMARY_PATH = RANK4_ART_DIR / "pair_summary.csv"
RANK4_TRIAL_META_PATH = RANK4_ART_DIR / "trial_meta.csv"
RANK4_REPORT_HREF = "../../factors/scout_crypto_pairs_stat_arb_15m/report.html"

RANK2_TINY_LIVE_HANDOFF_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_paper_candidate_handoff_map_v1.csv"
RANK2_DRY_RUN_REGISTRY_ROW_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_dry_run_registry_row_v1.csv"
RANK2_DRY_RUN_REPLAY_TICKET_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_routing_dry_run_replay_ticket_v1.csv"
RANK2_STATUS_SNAPSHOT_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_status_snapshot_v1.csv"
RANK2_RECEIPT_CHAIN_PACKET_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_receipt_chain_operator_packet_v1.csv"
RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_receipt_chain_log_template_v1.csv"
RANK2_RECEIPT_CHAIN_COMPLETION_GATE_PATH = ROOT / "reports" / "artifacts" / "alpha_closure_board" / "small_live_rank2_receipt_chain_completion_gate_v1.csv"
SCOUT_REPO_FASTLANE_EXHAUSTION_PATH = ROOT / "reports" / "artifacts" / "literature" / "scout_repo_fastlane_exhaustion_board_v1.csv"

FAST_CYCLE_SHORTLIST = [
    {
        "rank": "1",
        "candidate": "τ-band / no-trade breakout filter",
        "source": "De Angelis et al. (2021)",
        "page": "../quant_digests/2026-03-13_0932_threshold-no-trade-band-confirmation.html",
        "why_now": "直接贴合 intraday crypto 边界交易；最容易在 5m/15m breakout 上先拿到 first verdict。",
        "crypto_fit": "high",
        "clean_room": "full_text / no_code / medium",
        "first_test": "15m 做 `裸 breakout vs τ-band vs 2-of-3 closes outside`，先看假突破率与 post-cost return。",
        "desk_role": "优先当 Live Seat 的 confirmation / execution guard challenger，而不是独立主策略。",
    },
    {
        "rank": "2",
        "candidate": "volume + support-flip + higher-low",
        "source": "Yumna et al. (2024)",
        "page": "../quant_digests/2026-03-13_2129_volume-confirmed-breakout-higher-low.html",
        "why_now": "和当前 breakout 主线最贴；规则可 clean-room，且能比继续重切旧样本更快给出 yes/no。",
        "crypto_fit": "high",
        "clean_room": "full_text / no_code / low_to_medium",
        "first_test": "15m 做 `裸 breakout vs 放量确认 vs support-flip vs higher-low vs 组合版`。",
        "desk_role": "当前更适合作为窄范围 paper candidate / keep-narrower challenger；不直接升为 Live Seat。",
    },
    {
        "rank": "3",
        "candidate": "third-touch + EMA/MACD confluence",
        "source": "Wiśniewski (2024)",
        "page": "../quant_digests/2026-03-13_1746_trendline-confluence-confirmation.html",
        "why_now": "仍是 crypto 题材，且能把“先第三次确认、再看共识过滤”压成更严格的 breakout 入场门。",
        "crypto_fit": "medium_high",
        "clean_room": "full_text / no_code / medium",
        "first_test": "15m 做 `裸 breakout vs third-touch gate vs EMA slope 同向 vs EMA+MACD 共识`。",
        "desk_role": "先当更窄的 structure-confirmation challenger；默认低于前两名。",
    },
    {
        "rank": "4",
        "candidate": "crypto pairs trading / high-correlation stat-arb",
        "source": "Tadi et al. (2021, 2023) + open-source repos",
        "page": "https://arxiv.org/abs/2109.10662",
        "page_label": "参考论文",
        "why_now": "方向本身贴近 market-neutral alpha，也和 Jerry 新提出的“高相关币种价差 / 一多一空”思路一致；很适合走 `paper / repo -> replication -> light stability` 快筛。",
        "crypto_fit": "high",
        "clean_room": "paper+repo / code-available / medium",
        "first_test": "先做 BTC/ETH、ETH/SOL 等高相关币对的 `cointegration / z-score spread` 最小复现，再补时间稳定性、参数稳定性、跨对稳定性、成本/交易数稳定性。",
        "desk_role": "当前已完成最小 clean replication；若 frozen-beta z-score spread 在主要 pairs 上整体偏负，则更诚实的 desk 读法应是 park / evidence pool。",
    },
    {
        "rank": "5",
        "candidate": "Polymarket lag-arb / BTC indicator score betting",
        "source": "prediction-market bot ecosystem + desk hypothesis",
        "page": "https://dev.to/benjamin_martin_749c1d57f/polymarket-trading-bots-my-recent-open-source-projects-for-automated-prediction-market-trading-3mge",
        "page_label": "开源生态参考",
        "why_now": "它利用的是 prediction market 下单/改价对外部现货信号的反应延迟，和当前我们做的单边/结构类 alpha 不同，属于新的执行型 alpha 方向。",
        "crypto_fit": "medium_high",
        "clean_room": "desk thesis + open-source infra / medium",
        "first_test": "先把 BTC 的 EMA/MACD/动量等综合成一个方向分数，再对比 Polymarket 对应短周期 BTC 市场价格变化，做最小 lead-lag / fill-delay / post-cost 检查。",
        "desk_role": "新的 scout 候补池候选；默认先做 source intake，不直接抢当前 top-3 排班。若最小 lead-lag 明确存在，再进 clean replication。",
    },
    {
        "rank": "6",
        "candidate": "BTC-equity proxy spread / COIN-MSTR-tech relative-value",
        "source": "desk hypothesis + BTC proxy literature",
        "page": "https://doi.org/10.2139/ssrn.5894464",
        "page_label": "代理关系参考",
        "why_now": "如果 BTC 与 COIN/MSTR/科技板块之间存在高相关但有短时错位，这条线本质上也是跨资产相对价值/统计套利，和纯方向单边不同。",
        "crypto_fit": "medium_high",
        "clean_room": "desk thesis / medium",
        "first_test": "先在 BTC vs COIN、BTC vs MSTR、BTC vs tech proxy 上做 rolling correlation + lead-lag + z-score spread 的最小复现，再补参数/时间/成本检查。",
        "desk_role": "新的 scout 候补池候选；默认先做 source intake 和最小代理关系验证，不直接进入 paper candidate。",
    },
]


def write_shortlist_csv(rows: list[dict[str, str]]) -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["rank", "candidate", "source", "page", "page_label", "why_now", "crypto_fit", "clean_room", "first_test", "desk_role"]
    with SHORTLIST_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_fast_cycle_shortlist(rows: list[dict[str, str]]) -> str:
    header_html = "".join(
        f"<th>{escape(label)}</th>"
        for label in ["Rank", "候选", "为何现在看它", "Crypto 贴合度", "全文/clean-room", "最小 first verdict", "当前 desk 角色"]
    )
    row_html = []
    for row in rows:
        link_label = row.get('page_label') or ('对应 digest' if str(row.get('page','')).startswith('..') else '参考链接')
        candidate_html = (
            f"<b>{escape(row['candidate'])}</b><br />"
            f"<span class=\"muted\">{escape(row['source'])}</span><br />"
            f"<a href=\"{escape(row['page'])}\">{escape(link_label)}</a>"
        )
        row_html.append(
            "<tr>"
            f"<td>{escape(row['rank'])}</td>"
            f"<td>{candidate_html}</td>"
            f"<td>{escape(row['why_now'])}</td>"
            f"<td><code>{escape(row['crypto_fit'])}</code></td>"
            f"<td><code>{escape(row['clean_room'])}</code></td>"
            f"<td>{escape(row['first_test'])}</td>"
            f"<td>{escape(row['desk_role'])}</td>"
            "</tr>"
        )
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(row_html)}</tbody></table>"


def render_local_scout_first_verdict_card() -> str:
    if not LOCAL_SCOUT_VARIANT_PATH.exists() or not LOCAL_SCOUT_META_PATH.exists():
        return ""
    try:
        variant_df = pd.read_csv(LOCAL_SCOUT_VARIANT_PATH)
        meta_df = pd.read_csv(LOCAL_SCOUT_META_PATH)
    except Exception:
        return ""
    if variant_df.empty:
        return ""

    top = variant_df.iloc[0]
    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    verdict = str(meta.get("verdict", "-"))
    sample_window = str(meta.get("sample_window", "-"))
    generated = str(meta.get("generated_at_utc", "-"))

    return f"""
  <div class=\"card\">
    <h2>Run 2 本地最小实验（Rank 1 · τ-band）</h2>
    <p>已落一张 15m crypto 对照实验页：<a href=\"{escape(LOCAL_SCOUT_REPORT_HREF)}\">scout_tau_band_breakout_15m</a>。</p>
    <ul>
      <li><b>hard verdict：</b>{escape(verdict)}</li>
      <li><b>sample：</b><code>{escape(sample_window)}</code></li>
      <li><b>best current challenger：</b><code>{escape(str(top.get('variant', '-')))}</code>（mean_total_return={escape(str(top.get('mean_total_return', '-')))}，mean_false_break_ratio={escape(str(top.get('mean_false_break_ratio', '-')))}）</li>
      <li><b>artifact：</b><code>reports/artifacts/scout_tau_band_breakout_15m/variant_aggregate.csv</code></li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class=\"muted\">这张卡只做 first verdict：判断 τ-band / no-trade 是否值得继续当 breakout execution guard challenger；不直接宣称替代 Live Seat。</p>
  </div>
"""


def render_rank2_first_verdict_card() -> str:
    if not RANK2_VARIANT_PATH.exists() or not RANK2_TRIAL_META_PATH.exists():
        return ""
    try:
        variant_df = pd.read_csv(RANK2_VARIANT_PATH)
        meta_df = pd.read_csv(RANK2_TRIAL_META_PATH)
    except Exception:
        return ""
    if variant_df.empty:
        return ""

    top = variant_df.iloc[0]
    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    verdict = str(meta.get("verdict", "-"))
    friction_verdict = str(meta.get("friction_recheck_verdict", "")).strip()
    shadow_verdict = str(meta.get("shadow_readiness_verdict", "")).strip()
    trade_count_verdict = str(meta.get("trade_count_honesty_verdict", "")).strip()
    time_stability_verdict = str(meta.get("time_stability_verdict", "")).strip()
    cross_asset_stability_verdict = str(meta.get("cross_asset_stability_verdict", "")).strip()
    parameter_stability_verdict = str(meta.get("parameter_stability_verdict", "")).strip()
    paper_candidate_admission_verdict = str(meta.get("paper_candidate_admission_verdict", "")).strip()
    paper_candidate_monitoring_verdict = str(meta.get("paper_candidate_monitoring_verdict", "")).strip()
    narrow_paper_pilot_ledger_verdict = str(meta.get("narrow_paper_pilot_ledger_verdict", "")).strip()
    narrow_paper_pilot_refresh_seed_verdict = str(meta.get("narrow_paper_pilot_refresh_seed_verdict", "")).strip()
    narrow_paper_pilot_weekly_review_seed_verdict = str(meta.get("narrow_paper_pilot_weekly_review_seed_verdict", "")).strip()
    sample_window = str(meta.get("sample_window", "-"))
    generated = str(meta.get("generated_at_utc", "-"))
    friction_line = ""
    shadow_line = ""
    trade_count_line = ""
    time_stability_line = ""
    cross_asset_stability_line = ""
    parameter_stability_line = ""
    if friction_verdict and friction_verdict.lower() != "nan":
        friction_line = f'<li><b>轻量 friction recheck：</b>{escape(friction_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_friction_ladder.csv</code>）</li>'
    if shadow_verdict and shadow_verdict.lower() != "nan":
        shadow_line = f'<li><b>shadow-readiness dry-check：</b>{escape(shadow_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_shadow_readiness_drycheck.csv</code>）</li>'
    if trade_count_verdict and trade_count_verdict.lower() != "nan":
        trade_count_line = f'<li><b>trade-count honesty / cadence：</b>{escape(trade_count_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_trade_count_honesty.csv</code>）</li>'
    if time_stability_verdict and time_stability_verdict.lower() != "nan":
        time_stability_line = f'<li><b>time stability：</b>{escape(time_stability_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_time_stability_drycheck.csv</code>）</li>'
    if cross_asset_stability_verdict and cross_asset_stability_verdict.lower() != "nan":
        cross_asset_stability_line = f'<li><b>cross-asset stability：</b>{escape(cross_asset_stability_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_cross_asset_stability_drycheck.csv</code>）</li>'
    if parameter_stability_verdict and parameter_stability_verdict.lower() != "nan":
        parameter_stability_line = f'<li><b>parameter stability：</b>{escape(parameter_stability_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_parameter_stability_drycheck.csv</code>）</li>'
    paper_candidate_line = ""
    if paper_candidate_admission_verdict and paper_candidate_admission_verdict.lower() != "nan":
        paper_candidate_line = f'<li><b>paper candidate admission：</b>{escape(paper_candidate_admission_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_admission_memo.csv</code>）</li>'
    monitoring_line = ""
    if paper_candidate_monitoring_verdict and paper_candidate_monitoring_verdict.lower() != "nan":
        monitoring_line = f'<li><b>paper candidate monitoring：</b>{escape(paper_candidate_monitoring_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_monitoring_board.csv</code>）</li>'
    narrow_paper_ledger_line = ""
    if narrow_paper_pilot_ledger_verdict and narrow_paper_pilot_ledger_verdict.lower() != "nan":
        narrow_paper_ledger_line = f'<li><b>narrow paper pilot ledger：</b>{escape(narrow_paper_pilot_ledger_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_ledger_template.csv</code>）</li>'
    narrow_paper_refresh_seed_line = ""
    if narrow_paper_pilot_refresh_seed_verdict and narrow_paper_pilot_refresh_seed_verdict.lower() != "nan":
        narrow_paper_refresh_seed_line = f'<li><b>narrow paper refresh seed：</b>{escape(narrow_paper_pilot_refresh_seed_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_seed_rows.csv</code>）</li>'
    narrow_paper_weekly_review_seed_line = ""
    if narrow_paper_pilot_weekly_review_seed_verdict and narrow_paper_pilot_weekly_review_seed_verdict.lower() != "nan":
        narrow_paper_weekly_review_seed_line = f'<li><b>narrow paper weekly review seed：</b>{escape(narrow_paper_pilot_weekly_review_seed_verdict)}（artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv</code>）</li>'

    return f"""
  <div class=\"card\">
    <h2>Run 2 本地 first verdict（Rank 2 · volume + support-flip + higher-low）</h2>
    <p>已把 Rank 2 从 clean-room spec 推到最小本地 verdict 页：<a href=\"{escape(RANK2_SPEC_REPORT_HREF)}\">scout_volume_supportflip_higherlow_15m</a>。</p>
    <ul>
      <li><b>hard verdict：</b>{escape(verdict)}</li>
      {friction_line}
      {shadow_line}
      {trade_count_line}
      {time_stability_line}
      {cross_asset_stability_line}
      {parameter_stability_line}
      {paper_candidate_line}
      {monitoring_line}
      {narrow_paper_ledger_line}
      {narrow_paper_refresh_seed_line}
      {narrow_paper_weekly_review_seed_line}
      <li><b>sample：</b><code>{escape(sample_window)}</code></li>
      <li><b>best current challenger：</b><code>{escape(str(top.get('variant', '-')))}</code>（mean_total_return={escape(str(top.get('mean_total_return', '-')))}，mean_false_break_ratio={escape(str(top.get('mean_false_break_ratio', '-')))}）</li>
      <li><b>artifact：</b><code>reports/artifacts/scout_volume_supportflip_higherlow_15m/variant_aggregate.csv</code></li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class=\"muted\">这张卡现在同时承接 first verdict + paper candidate admission memo：它回答 Rank 2 是否已够资格进入窄范围 paper candidate pool，但仍不直接宣称替代 Live Seat。</p>
  </div>
"""


def render_rank2_spec_card() -> str:
    if not RANK2_SPEC_PATH.exists() or not RANK2_SPEC_META_PATH.exists():
        return ""
    try:
        spec_df = pd.read_csv(RANK2_SPEC_PATH)
        meta_df = pd.read_csv(RANK2_SPEC_META_PATH)
    except Exception:
        return ""
    if spec_df.empty:
        return ""

    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    generated = str(meta.get("generated_at_utc", "-"))
    hard_verdict = str(meta.get("hard_verdict", "-"))
    next_step = str(meta.get("next_step", "-"))
    variants = spec_df.loc[spec_df["item"] == "first_experiment_matrix", "value"]
    matrix = str(variants.iloc[0]) if not variants.empty else "-"

    return f"""
  <div class=\"card\">
    <h2>Run 2 fallback（Rank 2 · volume + support-flip + higher-low spec）</h2>
    <p>当 Rank 1 τ-band 只有极少新 bar、还不够做 honest continuation 时，已把 Rank 2 冻结成可直接实现的 clean-room spec：<a href=\"{escape(RANK2_SPEC_REPORT_HREF)}\">scout_volume_supportflip_higherlow_15m</a>。</p>
    <ul>
      <li><b>hard verdict：</b>{escape(hard_verdict)}</li>
      <li><b>first experiment matrix：</b><code>{escape(matrix)}</code></li>
      <li><b>artifact：</b><code>reports/artifacts/scout_volume_supportflip_higherlow_15m/clean_room_spec_v1.csv</code></li>
      <li><b>next step：</b>{escape(next_step)}</li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class=\"muted\">这张卡保留 spec 入口，方便回看 Rank 2 最初冻结的 clean-room 规则；真正的本地结果以上面的 first verdict 卡为准。</p>
  </div>
"""


def render_rank3_first_verdict_card() -> str:
    if not RANK3_VARIANT_PATH.exists() or not RANK3_TRIAL_META_PATH.exists():
        return ""
    try:
        variant_df = pd.read_csv(RANK3_VARIANT_PATH)
        meta_df = pd.read_csv(RANK3_TRIAL_META_PATH)
    except Exception:
        return ""
    if variant_df.empty:
        return ""

    top = variant_df.iloc[0]
    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    verdict = str(meta.get("verdict", "-"))
    sample_window = str(meta.get("sample_window", "-"))
    generated = str(meta.get("generated_at_utc", "-"))
    friction_verdict = str(meta.get("friction_recheck_verdict", "-"))
    trade_count_verdict = str(meta.get("trade_count_honesty_verdict", "")).strip()
    time_stability_verdict = str(meta.get("time_stability_verdict", "")).strip()
    parameter_stability_verdict = str(meta.get("parameter_stability_verdict", "")).strip()

    return f"""
  <div class="card">
    <h2>Run 3 本地 first verdict（Rank 3 · third-touch + EMA/MACD confluence）</h2>
    <p>已把 Rank 3 从 clean-room spec 推到最小本地 verdict 页：<a href="{escape(RANK3_SPEC_REPORT_HREF)}">scout_third_touch_ema_macd_15m</a>。</p>
    <ul>
      <li><b>hard verdict：</b>{escape(verdict)}</li>
      <li><b>sample：</b><code>{escape(sample_window)}</code></li>
      <li><b>best current challenger：</b><code>{escape(str(top.get('variant', '-')))}</code>（mean_total_return={escape(str(top.get('mean_total_return', '-')))}，mean_false_break_ratio={escape(str(top.get('mean_false_break_ratio', '-')))}）</li>
      <li><b>artifact：</b><code>reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv</code></li>
      <li><b>friction recheck：</b>{escape(friction_verdict)}</li>
      <li><b>trade-count honesty：</b>{escape(trade_count_verdict if trade_count_verdict and trade_count_verdict.lower() != "nan" else "-")}</li>
      <li><b>time stability：</b>{escape(time_stability_verdict if time_stability_verdict and time_stability_verdict.lower() != "nan" else "-")}</li>
      <li><b>parameter stability：</b>{escape(parameter_stability_verdict if parameter_stability_verdict and parameter_stability_verdict.lower() != "nan" else "-")}</li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class="muted">这张卡现在是 performance first verdict，不再只是 spec-only；它回答 Rank 3 更像 keep-narrow 还是应尽快 bench。</p>
  </div>
"""


def render_rank3_spec_card() -> str:
    if not RANK3_SPEC_PATH.exists() or not RANK3_SPEC_META_PATH.exists():
        return ""
    try:
        spec_df = pd.read_csv(RANK3_SPEC_PATH)
        meta_df = pd.read_csv(RANK3_SPEC_META_PATH)
    except Exception:
        return ""
    if spec_df.empty:
        return ""

    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    generated = str(meta.get("generated_at_utc", "-"))
    hard_verdict = str(meta.get("hard_verdict", "-"))
    next_step = str(meta.get("next_step", "-"))
    variants = spec_df.loc[spec_df["item"] == "first_experiment_matrix", "value"]
    matrix = str(variants.iloc[0]) if not variants.empty else "-"

    return f"""
  <div class="card">
    <h2>Rank 3 frozen spec（archive entry）</h2>
    <p>若要回看 Rank 3 最初冻结的实现口径，仍可从同一页面回看 clean-room spec：<a href="{escape(RANK3_SPEC_REPORT_HREF)}">scout_third_touch_ema_macd_15m</a>。</p>
    <ul>
      <li><b>spec verdict：</b>{escape(hard_verdict)}</li>
      <li><b>first experiment matrix：</b><code>{escape(matrix)}</code></li>
      <li><b>artifact：</b><code>reports/artifacts/scout_third_touch_ema_macd_15m/clean_room_spec_v1.csv</code></li>
      <li><b>next step at freeze time：</b>{escape(next_step)}</li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class="muted">这张卡现在只保留作 spec 入口；当前 Rank 3 的最新 desk 读法以上面的 first verdict 卡为准。</p>
  </div>
"""


def render_rank4_first_verdict_card() -> str:
    if not RANK4_PAIR_SUMMARY_PATH.exists() or not RANK4_TRIAL_META_PATH.exists():
        return ""
    try:
        pair_df = pd.read_csv(RANK4_PAIR_SUMMARY_PATH)
        meta_df = pd.read_csv(RANK4_TRIAL_META_PATH)
    except Exception:
        return ""
    if pair_df.empty:
        return ""

    best = pair_df.sort_values("cumulative_net_return", ascending=False).iloc[0]
    meta = meta_df.iloc[0] if not meta_df.empty else pd.Series(dtype=object)
    verdict = str(meta.get("verdict", "-"))
    sample_window = str(meta.get("sample_window", "-"))
    generated = str(meta.get("generated_at_utc", "-"))
    basis = str(meta.get("verdict_basis", "-"))
    best_pair_trade_count = meta.get("best_pair_trade_count", "-")
    best_pair_cum = meta.get("best_pair_cumulative_net_return", "-")

    return f"""
  <div class="card">
    <h2>Run 2 本地 clean replication（Rank 4 · crypto pairs stat-arb）</h2>
    <p>已把 Rank 4 从 source intake 推到最小本地 clean replication 页：<a href="{escape(RANK4_REPORT_HREF)}">scout_crypto_pairs_stat_arb_15m</a>。</p>
    <ul>
      <li><b>hard verdict：</b>{escape(verdict)}</li>
      <li><b>sample：</b><code>{escape(sample_window)}</code></li>
      <li><b>best current pair：</b><code>{escape(str(best.get('pair', '-')))}</code>（cumulative_net_return={escape(str(best_pair_cum))}，trade_count={escape(str(best_pair_trade_count))}）</li>
      <li><b>artifact：</b><code>reports/artifacts/scout_crypto_pairs_stat_arb_15m/pair_summary.csv</code></li>
      <li><b>why：</b>{escape(basis)}</li>
      <li><b>generated_at：</b>{escape(generated)}</li>
    </ul>
    <p class="muted">这张卡现在只回答一件事：repo-inspired frozen-beta z-score spread 在现有 15m crypto 缓存上能不能诚实跑通，以及它更像 one-more-light-check 还是应直接 park。</p>
  </div>
"""

def render_rank2_tiny_live_handoff_card() -> str:
    if not RANK2_TINY_LIVE_HANDOFF_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_TINY_LIVE_HANDOFF_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class=\"card\">
    <h2>Run 3 tiny-live plumbing fallback（Rank 2 handoff map）</h2>
    <p>当 `Run 2` 当前没有新的合格 scout 动作时，这张卡把 <code>Rank 2 paper candidate</code> 的监控字段直接桥接到 <code>small-live dry-run / shadow parity</code>，避免 desk 在 waiting-window 空转。</p>
    {table_html}
    <p class=\"muted\">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_paper_candidate_handoff_map_v1.csv</code> ｜ 这张卡只定义 handoff / 风险边界，不等于已拿到 live admission。</p>
  </div>
"""


def render_rank2_dry_run_registry_row_card() -> str:
    if not RANK2_DRY_RUN_REGISTRY_ROW_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_DRY_RUN_REGISTRY_ROW_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class="card">
    <h2>Run 3 closeout registry（Rank 2 blocked dry-run row）</h2>
    <p>这张卡把 <code>Rank 2 combo_all</code> 真正写成一条可审计的 <code>blocked dry-run registry row</code>：它只允许留在 <code>paper_candidate_only</code> 并排队到 <code>routing_dry_run_replay</code>，不会被 wording 偷升格成 tiny-live。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_dry_run_registry_row_v1.csv</code> ｜ 这是 concrete registry row，不是 live admission；它把当前 blocker（idle-gap / early-pocket / promotion boundary）直接锁进 closeout 链。</p>
  </div>
"""


def render_rank2_dry_run_replay_ticket_card() -> str:
    if not RANK2_DRY_RUN_REPLAY_TICKET_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_DRY_RUN_REPLAY_TICKET_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class="card">
    <h2>Run 3 replay bundle（Rank 2 routing dry-run replay ticket）</h2>
    <p>这张卡把上一张 <code>blocked dry-run registry row</code> 的 <code>next_queue=routing_dry_run_replay</code> 继续压成一张可直接打开的 replay ticket：现在不是继续抽象地说“后面再补 dry-run”，而是把 <b>必须补哪条 receipt chain、要绑哪些 ref、补齐后最多只允许关到哪一步</b> 写死。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_routing_dry_run_replay_ticket_v1.csv</code> ｜ 当前 hard verdict 仍是 <code>blocked / paper_candidate_only</code>；这张票的价值在于把下一步 replay 写成 concrete queue item，而不是把 Rank 2 偷说成已接近 tiny-live。</p>
  </div>
"""


def build_rank2_status_snapshot() -> str:
    required = [RANK2_TRIAL_META_PATH, RANK2_DRY_RUN_REGISTRY_ROW_PATH, RANK2_DRY_RUN_REPLAY_TICKET_PATH]
    if not all(path.exists() for path in required):
        return ""
    try:
        meta_df = pd.read_csv(RANK2_TRIAL_META_PATH)
        registry_df = pd.read_csv(RANK2_DRY_RUN_REGISTRY_ROW_PATH)
        replay_df = pd.read_csv(RANK2_DRY_RUN_REPLAY_TICKET_PATH)
    except Exception:
        return ""
    if meta_df.empty or registry_df.empty or replay_df.empty:
        return ""

    meta = meta_df.iloc[0]
    registry = registry_df.iloc[0]
    replay = replay_df.iloc[0]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    snapshot_row = {
        "candidate_id": str(registry.get("candidate_id", "rank2_combo_all_15m_narrow_paper")),
        "desk_role": "Scout Seat -> narrow paper candidate pool; Run 3 closeout only",
        "light_pack_status": "complete (time / parameter / cross-asset / cost-trade-count all landed)",
        "paper_candidate_status": str(meta.get("paper_candidate_admission_verdict", "-")).replace("paper candidate admission：", "").strip(),
        "monitoring_status": str(meta.get("paper_candidate_monitoring_verdict", "-")).replace("paper candidate monitoring：", "").strip(),
        "closeout_state": str(registry.get("closeout_state", "-")),
        "tiny_live_plumbing_status": str(replay.get("ticket_status", registry.get("ticket_status", "blocked"))).strip() or "blocked",
        "next_allowed_action": "only one real test/no-fill receipt-chain replay on BTC/ETH/SOL whitelist, else keep parked at paper_candidate_only",
        "blocked_actions": "shadow_parity / tiny-live / widened scope / new-symbol routing",
        "key_blockers": str(replay.get("current_blockers", registry.get("blocking_watchers", "-"))),
        "required_receipt_chain": str(replay.get("required_receipt_chain", "-")),
        "required_refs": str(replay.get("required_supporting_refs", registry.get("required_refs", "-"))),
        "current_hard_verdict": "Rank 2 is now a narrow paper candidate with closeout artifacts ready, but it remains blocked at paper_candidate_only until a real dry-run receipt chain is completed without scope drift.",
        "generated_at_utc": generated_at,
    }
    snapshot_df = pd.DataFrame([snapshot_row])
    RANK2_STATUS_SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot_df.to_csv(RANK2_STATUS_SNAPSHOT_PATH, index=False)
    return generated_at


def render_rank2_status_snapshot_card() -> str:
    if not RANK2_STATUS_SNAPSHOT_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_STATUS_SNAPSHOT_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    row = df.iloc[0]
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody><tr>{cells}</tr></tbody></table>"

    return f"""
  <div class="card">
    <h2>Rank 2 current status snapshot（paper candidate only）</h2>
    <p><b>closeout hard verdict：</b>Light Stability Pack 和 paper-candidate write-back 已补齐，但当前允许动作仍只有 <code>BTC/ETH/SOL whitelist</code> 上的一次真实 <code>test/no-fill receipt chain replay</code>；在那条回执链补齐前，Rank 2 继续停在 <code>paper_candidate_only</code>，不得偷进 <code>shadow_parity</code> 或 <code>tiny-live</code>。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_status_snapshot_v1.csv</code> ｜ 这张卡把 Rank 2 当前 desk 状态压成一行 closeout snapshot，方便后续轮次直接判断：是继续补唯一允许的 replay，还是诚实地保持 parked / blocked。</p>
  </div>
"""


def build_rank2_receipt_chain_operator_packet() -> str:
    required = [RANK2_DRY_RUN_REPLAY_TICKET_PATH, RANK2_MONITORING_PATH, RANK2_TRIAL_META_PATH, RANK2_STATUS_SNAPSHOT_PATH]
    if not all(path.exists() for path in required):
        return ""
    try:
        replay_df = pd.read_csv(RANK2_DRY_RUN_REPLAY_TICKET_PATH)
        monitoring_df = pd.read_csv(RANK2_MONITORING_PATH)
        meta_df = pd.read_csv(RANK2_TRIAL_META_PATH)
        snapshot_df = pd.read_csv(RANK2_STATUS_SNAPSHOT_PATH)
    except Exception:
        return ""
    if replay_df.empty or monitoring_df.empty or meta_df.empty or snapshot_df.empty:
        return ""

    replay = replay_df.iloc[0]
    meta = meta_df.iloc[0]
    snapshot = snapshot_df.iloc[0]
    allowed_symbols = [
        ("BTC-USD", "BTCUSDT", "weakest cross-asset leg; only honest test/no-fill receipt replay, no scope widening"),
        ("ETH-USD", "ETHUSDT", "preferred whitelist leg if one clean test/no-fill receipt chain is needed with fewer current blockers"),
        ("SOL-USD", "SOLUSDT", "preferred whitelist leg if venue precision / min_notional is cleaner than BTC while keeping same candidate scope"),
    ]
    common_blockers = str(replay.get("current_blockers", "-"))
    monitoring_refs = "; ".join(str(v) for v in monitoring_df["component"].tolist())
    current_verdict = str(snapshot.get("current_hard_verdict", meta.get("paper_candidate_admission_verdict", "-")))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    for order, (research_symbol, venue_symbol, lane_note) in enumerate(allowed_symbols, start=1):
        rows.append(
            {
                "packet_order": str(order),
                "candidate_id": str(replay.get("candidate_id", "rank2_combo_all_15m_narrow_paper")),
                "deployment_scope": str(replay.get("deployment_scope", "paper_candidate_only")),
                "review_stage": "dry_run_receipt_chain_only",
                "research_symbol": research_symbol,
                "venue_symbol": venue_symbol,
                "venue_mode": "test/no-fill",
                "required_receipt_chain": str(replay.get("required_receipt_chain", "intent->ack->cancel/close")),
                "allowed_operator_action": "one whitelist-bound test/no-fill replay only; cancel_after_ack; capital stays 0",
                "must_keep_refs": str(replay.get("required_supporting_refs", "-")),
                "monitoring_hooks": monitoring_refs,
                "lane_note": lane_note,
                "hard_stop": "any scope drift / capital > 0 / missing ack or cancel / new symbol routing => keep blocked at paper_candidate_only",
                "success_writeback": "close only as dry_run_pass -> eligible_for_shadow_parity_review if same candidate scope is preserved and full receipt chain lands",
                "fail_writeback": "otherwise keep dry_run_only / blocked and route back to routing_dry_run_replay",
                "current_blockers": common_blockers,
                "current_verdict": current_verdict,
                "generated_at_utc": generated_at,
            }
        )

    packet_df = pd.DataFrame(rows)
    RANK2_RECEIPT_CHAIN_PACKET_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet_df.to_csv(RANK2_RECEIPT_CHAIN_PACKET_PATH, index=False)
    return generated_at


def render_rank2_receipt_chain_operator_packet_card() -> str:
    if not RANK2_RECEIPT_CHAIN_PACKET_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_RECEIPT_CHAIN_PACKET_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class="card">
    <h2>Run 3 operator packet（Rank 2 whitelist-bound receipt chain）</h2>
    <p>这张卡不再重复解释 Rank 2 现在是不是 paper candidate，而是把当前唯一允许的 tiny-live plumbing 动作压成一张 <b>Rank 2 专用 operator packet</b>：只允许在 <code>BTC/ETH/SOL whitelist</code> 上做一次真实 <code>test/no-fill intent -&gt; ack -&gt; cancel/close</code> 回执链 replay，且每条 whitelist leg 都写死 <b>scope、可做动作、必须绑定的 refs、成功/失败 writeback</b>。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_operator_packet_v1.csv</code> ｜ 价值不在于暗示 Rank 2 更接近 tiny-live，而在于把“下一步只能补 receipt chain”从一句抽象 hard verdict 压成三条 whitelist-bound 的 concrete operator row；receipt chain 真补齐前，状态仍是 <code>paper_candidate_only / blocked</code>。</p>
  </div>
"""


def build_rank2_receipt_chain_log_template() -> str:
    required = [RANK2_RECEIPT_CHAIN_PACKET_PATH, RANK2_STATUS_SNAPSHOT_PATH]
    if not all(path.exists() for path in required):
        return ""
    try:
        packet_df = pd.read_csv(RANK2_RECEIPT_CHAIN_PACKET_PATH)
        snapshot_df = pd.read_csv(RANK2_STATUS_SNAPSHOT_PATH)
    except Exception:
        return ""
    if packet_df.empty or snapshot_df.empty:
        return ""

    snapshot = snapshot_df.iloc[0]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rows = []
    for _, packet in packet_df.iterrows():
        receipt_stub = f"rank2-{str(packet.get('venue_symbol', 'symbol')).lower()}-test-receipt-001"
        rows.append(
            {
                "receipt_stub_id": receipt_stub,
                "candidate_id": str(packet.get("candidate_id", "rank2_combo_all_15m_narrow_paper")),
                "deployment_scope": str(packet.get("deployment_scope", "paper_candidate_only")),
                "research_symbol": str(packet.get("research_symbol", "-")),
                "venue_symbol": str(packet.get("venue_symbol", "-")),
                "venue_mode": str(packet.get("venue_mode", "test/no-fill")),
                "expected_receipt_chain": str(packet.get("required_receipt_chain", "intent->ack->cancel/close")),
                "intent_ref": "pending_real_test_no_fill_intent_ref",
                "ack_ref": "pending_real_ack_ref",
                "cancel_or_close_ref": "pending_real_cancel_or_close_ref",
                "chain_status": "pending_real_replay",
                "scope_check": "must_match_packet_scope",
                "capital_check": "must_remain_0",
                "writeback_on_success": str(packet.get("success_writeback", "-")),
                "writeback_on_fail": str(packet.get("fail_writeback", "-")),
                "required_refs_bundle": str(packet.get("must_keep_refs", "-")),
                "current_blockers": str(packet.get("current_blockers", snapshot.get("key_blockers", "-"))),
                "operator_note": "Fill this row only after a real whitelist-bound test/no-fill replay lands; without all three refs, keep blocked.",
                "generated_at_utc": generated_at,
            }
        )

    template_df = pd.DataFrame(rows)
    RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    template_df.to_csv(RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH, index=False)
    return generated_at


def render_rank2_receipt_chain_log_template_card() -> str:
    if not RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class="card">
    <h2>Run 3 receipt log template（Rank 2 test/no-fill audit row）</h2>
    <p>这张卡继续沿着上一张 operator packet 往前走半步：不是去假装 receipt chain 已经发生，而是把 <b>真实 replay 一旦发生时必须怎么回写</b> 先冻结成审计模板。这样后续无论挑 <code>BTC/ETH/SOL</code> 哪条 whitelist leg，都会强制留下 <code>intent_ref / ack_ref / cancel_or_close_ref</code> 三段证据，而不是靠文字说明“应该补过了”。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_log_template_v1.csv</code> ｜ 这不是放行结论，而是 receipt chain 的 writeback 模板；只有真实三段回执都落地，后续轮次才有资格把某条 row 从 <code>pending_real_replay</code> 往 <code>dry_run_pass</code> 方向收口。</p>
  </div>
"""


def build_rank2_receipt_chain_completion_gate() -> str:
    required = [RANK2_RECEIPT_CHAIN_PACKET_PATH, RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH, RANK2_STATUS_SNAPSHOT_PATH]
    if not all(path.exists() for path in required):
        return ""
    try:
        packet_df = pd.read_csv(RANK2_RECEIPT_CHAIN_PACKET_PATH)
        template_df = pd.read_csv(RANK2_RECEIPT_CHAIN_LOG_TEMPLATE_PATH)
        snapshot_df = pd.read_csv(RANK2_STATUS_SNAPSHOT_PATH)
    except Exception:
        return ""
    if packet_df.empty or template_df.empty or snapshot_df.empty:
        return ""

    snapshot = snapshot_df.iloc[0]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    packet_cols = [
        'candidate_id', 'research_symbol', 'venue_symbol', 'deployment_scope', 'allowed_operator_action',
        'hard_stop', 'success_writeback', 'fail_writeback', 'current_blockers', 'current_verdict'
    ]
    merged = packet_df[packet_cols].merge(
        template_df[['research_symbol', 'venue_symbol', 'intent_ref', 'ack_ref', 'cancel_or_close_ref', 'chain_status', 'scope_check', 'capital_check', 'required_refs_bundle']],
        on=['research_symbol', 'venue_symbol'],
        how='left',
    )
    rows = []
    for _, row in merged.iterrows():
        rows.append({
            'gate_id': f"gate-{str(row.get('venue_symbol', 'symbol')).lower()}-001",
            'candidate_id': str(row.get('candidate_id', 'rank2_combo_all_15m_narrow_paper')),
            'research_symbol': str(row.get('research_symbol', '-')),
            'venue_symbol': str(row.get('venue_symbol', '-')),
            'deployment_scope': str(row.get('deployment_scope', 'paper_candidate_only')),
            'receipt_gate_status': 'blocked_until_three_real_refs_land',
            'required_real_refs': 'intent_ref + ack_ref + cancel_or_close_ref',
            'current_stub_refs': f"{row.get('intent_ref', '-')} | {row.get('ack_ref', '-')} | {row.get('cancel_or_close_ref', '-')}",
            'scope_guard': str(row.get('scope_check', 'must_match_packet_scope')),
            'capital_guard': str(row.get('capital_check', 'must_remain_0')),
            'pass_condition': 'all three refs are real and candidate scope stays unchanged with capital=0',
            'fail_condition': 'missing any ref / scope drift / capital > 0 / missing cancel-close',
            'pass_transition': 'eligible_for_shadow_parity_review only; still not tiny-live',
            'fail_transition': 'keep dry_run_only / blocked and route back to routing_dry_run_replay',
            'required_refs_bundle': str(row.get('required_refs_bundle', '-')),
            'allowed_operator_action': str(row.get('allowed_operator_action', '-')),
            'current_blockers': str(row.get('current_blockers', snapshot.get('key_blockers', '-'))),
            'current_hard_verdict': str(row.get('current_verdict', snapshot.get('current_hard_verdict', '-'))),
            'generated_at_utc': generated_at,
        })

    gate_df = pd.DataFrame(rows)
    RANK2_RECEIPT_CHAIN_COMPLETION_GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    gate_df.to_csv(RANK2_RECEIPT_CHAIN_COMPLETION_GATE_PATH, index=False)
    return generated_at


def render_rank2_receipt_chain_completion_gate_card() -> str:
    if not RANK2_RECEIPT_CHAIN_COMPLETION_GATE_PATH.exists():
        return ""
    try:
        df = pd.read_csv(RANK2_RECEIPT_CHAIN_COMPLETION_GATE_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class="card">
    <h2>Run 3 receipt completion gate（Rank 2 hard closeout rule）</h2>
    <p>这张卡把 <b>“什么才算 receipt chain 真补齐”</b> 也固定成 closeout 规则：不是有模板就算通过，也不是只出现 <code>intent</code> / <code>ack</code> 任一段就能往下走，而是必须在同一条 whitelist-bound replay 上同时拿到 <code>intent_ref + ack_ref + cancel_or_close_ref</code> 三段真实回执，且 <code>scope</code> 不漂移、<code>capital=0</code>。只有这样，后续轮次才允许把状态从 <code>paper_candidate_only / blocked</code> 收口到 <code>eligible_for_shadow_parity_review</code>；否则继续 blocked。</p>
    {table_html}
    <p class="muted">artifact：<code>reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_completion_gate_v1.csv</code> ｜ 这张 gate 表的价值，是把“真实三段回执都落地才算 dry-run pass”写成机器可读 closeout 规则，避免 future run 把模板行、单段 ack、或 scope 漂移误读成已完成 receipt chain。</p>
  </div>
"""


def build_scout_repo_fastlane_exhaustion_board() -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rows = [
        {
            "bucket": "P3",
            "candidate": "Rank 2 · volume + support-flip + higher-low",
            "current_status": "narrow paper pilot / cron-managed continuity",
            "current_margin_call": "no default append/review need",
            "why_not_now": "继续动作只会回到 whitelist-bound dry-run receipt chain 或 weekly review writeback；当前都不是 Scout Seat 的更高边际主资源。",
            "next_honest_trigger": "real append / weekly-review row / receipt refs",
        },
        {
            "bucket": "P3",
            "candidate": "Rank 17 · pullback recovery confirmation",
            "current_status": "narrow paper pilot / cron-managed continuity",
            "current_margin_call": "no default append/review need",
            "why_not_now": "open paper positions 属于专属 refresh continuity，不自动构成 bot3 本轮默认主资源。",
            "next_honest_trigger": "closed-trade append / weekly-review row",
        },
        {
            "bucket": "P3",
            "candidate": "Rank 29 · trendline breakout navigator",
            "current_status": "narrow paper pilot / cron-managed continuity",
            "current_margin_call": "no default append/review need",
            "why_not_now": "最新 manual refresh 只新增 open continuity position，不是新的 Scout Seat verdict-changing 动作。",
            "next_honest_trigger": "closed-trade append / weekly-review row",
        },
        {
            "bucket": "P0-P1",
            "candidate": "Rank 30-35 repo-based fresh intake family",
            "current_status": "current allowed action consumed",
            "current_margin_call": "park / evidence pool",
            "why_not_now": "Rank 30/31/32/33/34/35 已完成当前允许的一轮 source intake 或最小 clean replication；继续默认会退化成近义 micro-slicing。",
            "next_honest_trigger": "bot2 explicit reopen with one verdict-changing check",
        },
        {
            "bucket": "external-data queue",
            "candidate": "Rank 5 / Rank 6",
            "current_status": "shortlist remains but external-data dependent",
            "current_margin_call": "not default scout resource now",
            "why_not_now": "当前 desk 要求 Scout Seat 默认优先 paper/repo based 5m/15m crypto；这两条需要 prediction-market 或 equity proxy 外部依赖。",
            "next_honest_trigger": "bot2 explicit nomination or fresh external data lane approval",
        },
    ]
    df = pd.DataFrame(rows)
    SCOUT_REPO_FASTLANE_EXHAUSTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SCOUT_REPO_FASTLANE_EXHAUSTION_PATH, index=False)
    return generated_at



def render_scout_repo_fastlane_exhaustion_card() -> str:
    if not SCOUT_REPO_FASTLANE_EXHAUSTION_PATH.exists():
        return ""
    try:
        df = pd.read_csv(SCOUT_REPO_FASTLANE_EXHAUSTION_PATH)
    except Exception:
        return ""
    if df.empty:
        return ""

    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{escape(str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    table_html = f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"

    return f"""
  <div class=\"card\">
    <h2>Scout Seat 边际价值比较（repo fast-lane exhaustion v1）</h2>
    <p>这张卡专门回答当前 <code>EMA = waiting_not_due</code> 时，为什么 bot3 这轮<strong>没有</strong>继续硬开新的 repo-based Scout 主动作：不是因为整个 desk 要等，而是因为本地 <code>paper / repo based 5m / 15m crypto</code> 快筛池里，当前允许动作已经基本被消化完了。</p>
    {table_html}
    <ul>
      <li><b>hard verdict：</b><code>repo_fastlane_temporarily_exhausted -> fallback_to_tiny_live_plumbing</code></li>
      <li><b>desk implication：</b>这轮若没有 bot2 明确点名新 promoted candidate / 新 repo source，默认不该为了“继续像在做 Scout”而重磨已 park 候选或 P3 continuity 文档链。</li>
      <li><b>what changes this verdict：</b>只要出现新的 repo-based 15m crypto 候选、或现有 P3 lane 真新增 <code>closed-trade append / weekly-review row / receipt refs</code>，就可以重新回到 Scout / narrow-paper 主资源。</li>
    </ul>
    <p class=\"muted\">artifact：<code>reports/artifacts/literature/scout_repo_fastlane_exhaustion_board_v1.csv</code> ｜ 这不是“永久没得做”，而是把当前剩余预算读成一条更诚实的 desk 结论：本地 repo fast-lane 暂时耗尽，所以本轮默认转去 <code>Run 3 tiny-live plumbing</code> 比继续伪造 Scout 进展更对。</p>
  </div>
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_shortlist_csv(FAST_CYCLE_SHORTLIST)
    shortlist_html = render_fast_cycle_shortlist(FAST_CYCLE_SHORTLIST)
    local_scout_card_html = render_local_scout_first_verdict_card()
    rank2_first_verdict_card_html = render_rank2_first_verdict_card()
    rank2_spec_card_html = render_rank2_spec_card()
    rank3_first_verdict_card_html = render_rank3_first_verdict_card()
    rank3_spec_card_html = render_rank3_spec_card()
    rank4_first_verdict_card_html = render_rank4_first_verdict_card()
    rank2_tiny_live_handoff_card_html = render_rank2_tiny_live_handoff_card()
    rank2_dry_run_registry_row_card_html = render_rank2_dry_run_registry_row_card()
    rank2_dry_run_replay_ticket_card_html = render_rank2_dry_run_replay_ticket_card()
    build_rank2_status_snapshot()
    rank2_status_snapshot_card_html = render_rank2_status_snapshot_card()
    build_rank2_receipt_chain_operator_packet()
    rank2_receipt_chain_operator_packet_card_html = render_rank2_receipt_chain_operator_packet_card()
    build_rank2_receipt_chain_log_template()
    rank2_receipt_chain_log_template_card_html = render_rank2_receipt_chain_log_template_card()
    build_rank2_receipt_chain_completion_gate()
    rank2_receipt_chain_completion_gate_card_html = render_rank2_receipt_chain_completion_gate_card()
    build_scout_repo_fastlane_exhaustion_board()
    scout_repo_fastlane_exhaustion_card_html = render_scout_repo_fastlane_exhaustion_card()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Trendline Alpha Scout</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul,ol {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Trendline Alpha Scout</h1>
  <p class="muted">生成时间：{generated_at} ｜ 这是 `TODO.md` 中 E 模块的固定网页入口：专门管理外部文献 / 开源仓库 / 复现候选，不直接下本地 alpha 结论。</p>

  <div class="card">
    <h2>一句话定位</h2>
    <p>这页只回答三件事：<b>别人声称什么、证据质量如何、值不值得 clean-room 复现</b>；不在这里把外部 claim 直接当成我们已经验证通过的因子。</p>
  </div>

  <div class="card">
    <h2>Scout Seat 快周期 crypto shortlist（Run 3 fallback v1）</h2>
    <p>这张卡不是在宣布新主线，而是在 <code>EMA waiting-window + breakout cooldown</code> 的双阻塞窗口里，给 desk 一张可以直接认领的备选清单：先找 <b>更快拿到 first verdict</b>、且更贴近 <b>crypto 5m/15m breakout / confirmation</b> 的 challenger。</p>
    <p><b>当前 desk call：</b>先按 <code>Rank 1 → Rank 2 → Rank 3</code> 看；默认先把它们当 <b>breakout 的 confirmation / execution guard 候选</b>，而不是直接宣布替代当前 Live Seat。</p>
    {shortlist_html}
    <p class="muted">artifact：<code>reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv</code>（相对路径：<a href="../../../artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv">csv</a>）</p>
  </div>

{local_scout_card_html}
{rank2_first_verdict_card_html}
{rank2_spec_card_html}
{rank3_first_verdict_card_html}
{rank3_spec_card_html}
{rank4_first_verdict_card_html}
{rank2_tiny_live_handoff_card_html}
{rank2_dry_run_registry_row_card_html}
{rank2_dry_run_replay_ticket_card_html}
{rank2_status_snapshot_card_html}
{rank2_receipt_chain_operator_packet_card_html}
{rank2_receipt_chain_log_template_card_html}
{rank2_receipt_chain_completion_gate_card_html}
{scout_repo_fastlane_exhaustion_card_html}

  <div class="card">
    <h2>Agent 执行协议</h2>
    <ol>
      <li>优先搜索近 5 年的 trendline / support-resistance / breakout / rebound / retest / confirmation / channel 相关材料。</li>
      <li>优先级：<b>有回测 + 有代码/GitHub</b> &gt; 有回测 + 逻辑清晰 &gt; 纯理论。</li>
      <li>每个候选必须落卡到 <code>docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md</code>。</li>
      <li>每轮至少交付一个网页可见产物：quant digest / deep dive / scout board 更新 / replication brief。</li>
      <li>正式实现前必须先写 clean-room replication brief，不直接搬外部代码。</li>
    </ol>
    <p class="muted">当前已把搜索协议正式定稿为 <code>Scout protocol v1</code>：要求同时审 `来源质量 / 全文可得性 / 结构定义清晰度 / 复现可能性 / repaint-future-info 风险`，避免 E 模块退化成随手收链接。</p>
  </div>

  <div class="card">
    <h2>来源卡最小字段（v1）</h2>
    <table>
      <thead>
        <tr><th>字段</th><th>用途</th></tr>
      </thead>
      <tbody>
        <tr><td><code>fulltext_access</code></td><td>区分 <code>full_text</code> / <code>abstract_only</code> / <code>repo_only</code>，避免只凭摘要进 replication shortlist</td></tr>
        <tr><td><code>license / source boundary</code></td><td>提前区分可 clean-room 学习与不能直接搬代码的边界</td></tr>
        <tr><td><code>evidence_status</code></td><td>统一追踪 <code>read / digest_done / deep_dive_done / replication_candidate / parked</code></td></tr>
        <tr><td><code>fit_for_us</code></td><td>明确它是更服务 mainline event、feature、filter 还是 explainability</td></tr>
        <tr><td><code>clean-room difficulty</code></td><td>帮助后续 2~3 轮 E 模块优先挑“最值得且最能快速复现”的对象</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>质量门槛</h2>
    <ul>
      <li><b>近 5 年优先</b>；更老材料只有在是 canonical baseline 时才保留。</li>
      <li><b>alpha claim 要明确</b>：不能只是“画图很好看”，要能说清楚预测对象或交易逻辑。</li>
      <li><b>结构定义要清楚</b>：breakout / rebound / retest / confirmation 至少要能说清事件是怎么触发的。</li>
      <li><b>可复现性要评估</b>：有无代码、许可证是否干净、是否疑似 future info / repaint。</li>
      <li><b>回测证据要可读</b>：最好有 OOS / rolling / cost discussion；至少不能完全黑箱。</li>
    </ul>
  </div>

  <div class="card">
    <h2>当前网页交付边界</h2>
    <ul>
      <li><code>reading/</code>：外部证据、文献卡、deep dive、replication candidate</li>
      <li><code>factors/</code>：我们自己已经做过本地验证的研究结果</li>
      <li>结论纪律：<b>别人声称有效 ≠ 我们已经验证有效</b></li>
    </ul>
  </div>

  <div class="card">
    <h2>首批建议搜集方向</h2>
    <table>
      <thead>
        <tr><th>方向</th><th>为什么重要</th><th>希望找到什么</th></tr>
      </thead>
      <tbody>
        <tr><td>Trendline breakout + confirmation</td><td>最贴近我们当前 mainline</td><td>明确的事件定义 + 回测 + 最好有代码</td></tr>
        <tr><td>Failed breakout / rebound / rejection</td><td>当前内部证据更偏向这条线</td><td>确认/回踩/反抽逻辑是否真有 alpha</td></tr>
        <tr><td>Support-resistance predictive features</td><td>可直接对接 feature builder</td><td>把结构变成可输入模型/规则的特征</td></tr>
        <tr><td>Channel / regression channel</td><td>承接未来分支 D</td><td>是否存在清楚、可复现的 channel alpha</td></tr>
        <tr><td>Pivot / swing structure rules</td><td>和 pytrendline / pyindicators 都有桥接空间</td><td>事件定义与 causal 边界</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>首批种子材料（已有项目内入口）</h2>
    <table>
      <thead>
        <tr><th>材料</th><th>页面入口</th><th>角色</th><th>状态</th><th>下一步</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>PyTrendline repo deep dive</td>
          <td><a href="../deep_dives/2026-03-11_pytrendline-repo-deep-dive.html">deep dive</a></td>
          <td>开源仓库拆解 / 定义参考</td>
          <td><code>deep_dive_done</code></td>
          <td>补进 literature map，明确哪些对象可映射成 event schema</td>
        </tr>
        <tr>
          <td>Trendln repo deep dive</td>
          <td><a href="../deep_dives/2026-03-11_trendln-repo-deep-dive.html">deep dive</a></td>
          <td>替代趋势线引擎参考</td>
          <td><code>deep_dive_done</code></td>
          <td>比较定义差异与复现价值</td>
        </tr>
        <tr>
          <td>Jiang, Kelly, Xiu (2023)</td>
          <td><a href="../deep_dives/2026-03-11_jiang-kelly-xiu-price-trends-deep-dive.html">deep dive</a></td>
          <td>近年价格结构 / 图像趋势主线</td>
          <td><code>deep_dive_done</code></td>
          <td>提炼最值得落地的结构假设</td>
        </tr>
        <tr>
          <td>Support-resistance features profitability</td>
          <td><a href="../quant_digests/2026-03-11_2128_support-resistance-features-profitability.html">digest</a></td>
          <td>S/R feature 候选</td>
          <td><code>parked</code></td>
          <td>保留为 feature reference，不再继续 faithful replication</td>
        </tr>
        <tr>
          <td>Support-resistance optimal stopping</td>
          <td><a href="../quant_digests/2026-03-12_0128_support-resistance-optimal-stopping.html">digest</a></td>
          <td>理论参考 / 机制解释</td>
          <td><code>digest_done</code></td>
          <td>判断是否升级为 confirmation / retest 机制 deep dive</td>
        </tr>
        <tr>
          <td>Fibonacci retracement pullback confirmation</td>
          <td><a href="../quant_digests/2026-03-13_1337_fibonacci-retracement-pullback-confirmation.html">digest</a></td>
          <td>pullback / breakout 确认层参考</td>
          <td><code>digest_done</code></td>
          <td>优先转写成短窗口 pullback confirmation 对照，而不是直接当独立 alpha</td>
        </tr>
        <tr>
          <td>Regime switch indicator stack</td>
          <td><a href="../quant_digests/2026-03-14_0128_regime-switch-indicator-stack.html">digest</a></td>
          <td>regime / filter reference</td>
          <td><code>digest_done</code></td>
          <td>优先吸收“先分 regime，再决定是否允许 breakout / pullback 交易”的约束层原则，不直接照抄论文参数</td>
        </tr>
        <tr>
          <td>Volume-confirmed breakout + higher low</td>
          <td><a href="../quant_digests/2026-03-13_2129_volume-confirmed-breakout-higher-low.html">digest</a></td>
          <td>confirmation / filter reference</td>
          <td><code>digest_done</code></td>
          <td>优先把 `volume filter + support flip + higher-low` 转成客观 15m breakout 过滤层，不直接把周频案例当 alpha 论文</td>
        </tr>
        <tr>
          <td>Third-touch + EMA/MACD confluence</td>
          <td><a href="../quant_digests/2026-03-13_1746_trendline-confluence-confirmation.html">digest</a></td>
          <td>confirmation / filter reference</td>
          <td><code>digest_done</code></td>
          <td>优先把 `third-touch confirmation + EMA/MACD 共识` 转成客观 15m breakout / retest 过滤层，不直接把周频趋势线案例当 alpha 论文</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>第一轮侦察结论（2026-03-12）</h2>
    <ul>
      <li><b>关于 pytrendline 作者：</b>当前没有找到 Eduardo Nunez / Ed Nunez 把 <code>pytrendline</code> 写成正式学术论文并给出论文级回测证据；目前最直接的外部证据是：
        <ul>
          <li><code>pytrendline</code> GitHub / PyPI 的算法说明（更像 detection engine）</li>
          <li>作者 2021 年的博客《Building a reliable and testable day trading bot on python》，其中明确说自己的低频日内 bot 以 trendline detection 为核心指标，并做了大量参数回测，但没有论文级结果表、成本讨论或 OOS 设计。</li>
        </ul>
      </li>
      <li><b>所以对我们最合理的定位是：</b><code>pytrendline</code> 值得继续当 <b>结构定义 / detection / explainability 参考</b>，但目前没有足够外部证据支持把它直接当“已知有效 alpha 文献”。</li>
      <li><b>当前更值得继续推进的 replication 候选</b> 现在主要是：
        <ul>
          <li>Crypto technical analysis under costs / bubbles（Svogun & Bazán-Palomino, 2022）</li>
          <li>Jiang / Kelly / Xiu (2023) 作为结构理论母体，而不是第一批直接规则复刻对象</li>
        </ul>
      </li>
      <li><b>Chan et al. (2022)</b> 这条线我们已经做过规范提取与一版 clean-room 试跑，但因为缺方法细节与官方代码，当前决定先收口，保留为 literature / feature reference。</li>
      <li><b>Gurrib et al. (2022)</b> 这条 Fibonacci 线当前先不升为主 replication candidate：它更像 <code>pullback / breakout confirmation layer</code> 参考，最值得转写的是“确认窗口要短、回撤位更适合作为过滤层而不是独立 alpha 主体”。</li>
      <li><b>Naganjaneyulu et al. (2023)</b> 这条 regime-switch 线当前也不进主 replication shortlist：它更像 <code>regime / filter reference</code>，最值得迁移的是“先分 Uptrend / Downtrend / Fluctuating，再决定是否允许 breakout / pullback 交易”的设计原则，而不是直接照搬日频 BTC 上的 `MIHCS7` 参数。</li>
      <li><b>Yumna et al. (2024)</b> 这条 volume-confirmed breakout 线当前同样不进主 replication shortlist：它更像 <code>confirmation / filter reference</code>，最值得转写的是 `volume confirmation + support flip + higher low persistence` 这套假突破过滤链，而不是把周频 BTC 的定性案例直接当成已验证 alpha。</li>
      <li><b>Wiśniewski (2024)</b> 这条 third-touch + EMA/MACD 线当前也不进主 replication shortlist：它更像 <code>confirmation / filter reference</code>，最值得迁移的是“第三次结构确认后，再要求 EMA/MACD 共识”的设计原则，而不是直接照搬周频 BTC/ETH 的趋势线案例。</li>
    </ul>
  </div>

  <div class="card">
    <h2>正式 shortlist v1（2026-03-13）</h2>
    <table>
      <thead>
        <tr><th>候选</th><th>角色</th><th>状态</th><th>为什么入选</th><th>下一步</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>Svogun &amp; Bazán-Palomino (2022)</td>
          <td>成本 / regime 约束复现</td>
          <td><code>replication_candidate</code></td>
          <td>全文可得、问题直连当前 breakout/trend 主线，且已有 brief + experiment v1</td>
          <td>继续作为 active replication 候选保留</td>
        </tr>
        <tr>
          <td>pytrendline (Eduardo Nunez)</td>
          <td>event-source bridge</td>
          <td><code>deep_dive_done</code></td>
          <td>有代码、结构定义清楚，最适合接 unified event schema / source bridge</td>
          <td>优先补 clean-room bridge / source audit</td>
        </tr>
        <tr>
          <td>trendln (Gregory Morse)</td>
          <td>geometry / channel baseline</td>
          <td><code>deep_dive_done</code></td>
          <td>有代码，extrema → line search → line quality 的拆法清楚，适合做几何 baseline</td>
          <td>作为 secondary 候选保留，低于 pytrendline 优先级</td>
        </tr>
        <tr>
          <td>Optimal Stopping S/R paper</td>
          <td>confirmation / retest 机制候选</td>
          <td><code>digest_done</code></td>
          <td>全文可得，最适合支持 confirmation / retest / regime-switch 机制设计</td>
          <td>优先补 deep dive / protocol mapping</td>
        </tr>
      </tbody>
    </table>
    <p class="muted">当前明确不进 shortlist：<code>Chan 2022</code>（已 park）、<code>Jiang/Kelly/Xiu 2023</code>（理论价值高但暂不适合 direct replication）、<code>Ed Nunez blog</code>（工程背景材料）。</p>
  </div>

  <div class="card">
    <h2>当前 replication 入口</h2>
    <p>第一批 clean-room replication brief 已单独落页：</p>
    <ul>
      <li><a href="../trendline_replication_briefs/report.html">Trendline Replication Briefs</a></li>
      <li><a href="../chan2022_paper_spec/report.html">Chan 2022 · Paper-Faithful Replication Spec</a></li>
      <li><a href="../chan2022_sr_feature_replication/report.html">Chan 2022 · S/R Feature Replication Report</a></li>
      <li><a href="../svogun2022_cost_regime_replication/report.html">Svogun 2022 · Cost/Regime Replication Report</a></li>
      <li><a href="../svogun2022_cost_regime_experiment/report.html">Svogun 2022 · Cost/Regime Experiment v1</a></li>
    </ul>
    <p class="muted">当前优先对象已经改为：<code>Svogun 2022</code>（active replication 约束）、<code>pytrendline</code>（source bridge）、<code>Optimal Stopping</code>（confirmation/retest 机制）。<code>Chan 2022</code> 保留为 reference，不再继续 active replication。</p>
  </div>

  <div class="card">
    <h2>下一步最小交付</h2>
    <ol>
      <li>继续按 `Scout protocol v1` 把来源卡数量补到 `10~20`。</li>
      <li>优先为 shortlist v1 中仍缺的对象补齐 replication brief / deep dive。</li>
      <li>把 shortlist 与候选池状态保持同步，避免页面与 literature map 漂移。</li>
      <li>必要时再做 shortlist v2，而不是频繁改动已 park 的对象。</li>
    </ol>
  </div>
</body>
</html>
"""
    OUT_PATH.write_text(html, encoding="utf-8")
    print("[ok] trendline alpha scout report generated")
    print("[site]", OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
