#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "site" / "factors" / "trendline_event_foundation"
OUT_HTML = OUT_DIR / "report.html"
OUT_META = OUT_DIR / "contract.json"
ARTIFACTS_DIR = ROOT / "reports" / "artifacts" / "trendline_event_foundation"
SLOPE_AUDIT_DIR = ROOT / "reports" / "artifacts" / "trendline_event_slope_audit"
CONFIRMATION_DIR = ROOT / "reports" / "artifacts" / "trendline_confirmation_ladder"
PYT_VAL_DIR = ROOT / "reports" / "artifacts" / "pytrendline_event_validation"
XENG_DIR = ROOT / "reports" / "artifacts" / "cross_engine_source_comparison"
SVOGUN_DIR = ROOT / "reports" / "artifacts" / "svogun2022_cost_regime_experiment"
CONFIRMATION_PROTOCOL_DOC = ROOT / "docs" / "TRENDLINE_CONFIRMATION_PROTOCOL.md"

DEFAULT_ASSETS = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "XRP-USD"]


@dataclass(frozen=True)
class PlannedArtifact:
    slug: str
    title: str
    question: str
    suggested_fields: list[str]


ARTIFACTS = [
    PlannedArtifact("event_taxonomy_card", "Event taxonomy card", "这页到底在比较哪些 event buckets？", ["event_family", "event_bucket", "plain_language_definition", "belongs_to", "notes"]),
    PlannedArtifact("sample_coverage_table", "Sample coverage table", "哪些 asset × timeframe × side × event bucket 样本够不够？", ["sample_key", "asset", "timeframe", "line_side", "event_bucket", "sample_count", "confidence_flag"]),
    PlannedArtifact("event_density_summary", "Event density summary", "这些事件是稀有、可用，还是过密噪声？", ["sample_key", "asset", "timeframe", "event_bucket", "events_per_1k_bars", "avg_bars_between_events"]),
    PlannedArtifact("breakout_confirmation_comparison", "Breakout confirmation comparison", "raw → confirmed ladder 里哪一层真的改善质量？", ["event_bucket", "sample_count", "fwd_ret_1", "fwd_ret_3", "fwd_ret_6", "fwd_ret_12", "win_rate_3", "MFE_6", "MAE_6", "false_break_ratio"]),
    PlannedArtifact("rebound_confirmation_comparison", "Rebound confirmation comparison", "rebound ladder 是否也在一层层提高质量？", ["event_bucket", "sample_count", "fwd_ret_1", "fwd_ret_3", "fwd_ret_6", "fwd_ret_12", "win_rate_3", "MFE_6", "MAE_6"]),
    PlannedArtifact("slope_bucket_summary", "Slope bucket summary", "sign / sign×magnitude 是否真的改变事件结果？", ["event_bucket", "slope_sign", "slope_mag_bucket", "sample_count", "fwd_ret_3", "fwd_ret_12", "win_rate_3", "MAE_6", "judgement_note"]),
    PlannedArtifact("quality_bucket_summary", "Quality bucket summary", "num_points / score / representative 是否提供增量解释力？", ["event_bucket", "quality_dimension", "quality_bucket", "sample_count", "fwd_ret_3", "fwd_ret_12", "win_rate_3", "judgement_note"]),
    PlannedArtifact("false_break_statistics", "False-break statistics", "哪些突破更像假突破、失败有多快？", ["event_bucket", "sample_count", "false_break_ratio", "median_time_to_fail", "note"]),
    PlannedArtifact("representative_vs_all_valid_sensitivity", "Representative vs all-valid sensitivity", "duplicate grouping 压缩是否改变结论方向？", ["event_bucket", "line_universe", "sample_count", "fwd_ret_3", "fwd_ret_12", "win_rate_3"]),
    PlannedArtifact("case_charts", "2–4 case charts", "统计结论落到真实线和真实事件上，长什么样？", ["chart_type", "asset", "timeframe", "event_bucket", "caption"]),
]


def confidence_flag(sample_count: int) -> str:
    if sample_count < 25:
        return "display-only"
    if sample_count < 50:
        return "low-confidence"
    return "ok"


def render_table(df: pd.DataFrame, max_rows: int = 200) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def load_trade_detail() -> pd.DataFrame:
    path = SLOPE_AUDIT_DIR / "trade_detail.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return df
    df = df[df["symbol"].isin(DEFAULT_ASSETS)].copy()
    if "sample_key" in df.columns:
        df = df.sort_values(["sample_key", "symbol", "event_type", "signal_ts"]).reset_index(drop=True)
    return df


def load_sample_meta() -> pd.DataFrame:
    path = SLOPE_AUDIT_DIR / "sample_meta.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def build_sample_coverage(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    group_cols = ["sample_key", "interval", "period", "symbol", "side_label", "event_type"]
    out = (
        trades.groupby(group_cols, dropna=False)
        .agg(sample_count=("net_ret", "size"))
        .reset_index()
        .rename(columns={"symbol": "asset", "interval": "timeframe", "side_label": "line_side", "event_type": "event_bucket"})
    )
    out["confidence_flag"] = out["sample_count"].map(lambda x: confidence_flag(int(x)))
    return out.sort_values(["sample_key", "asset", "event_bucket", "line_side"]).reset_index(drop=True)


def build_event_density(trades: pd.DataFrame, sample_meta: pd.DataFrame) -> pd.DataFrame:
    if trades.empty or sample_meta.empty:
        return pd.DataFrame()
    meta = sample_meta[["sample_key", "rows", "symbols"]].copy()
    meta["avg_rows_per_symbol"] = meta["rows"] / meta["symbols"].replace(0, pd.NA)
    group_cols = ["sample_key", "interval", "period", "symbol", "event_type"]
    out = (
        trades.groupby(group_cols, dropna=False)
        .agg(sample_count=("net_ret", "size"))
        .reset_index()
        .merge(meta[["sample_key", "avg_rows_per_symbol"]], on="sample_key", how="left")
        .rename(columns={"symbol": "asset", "interval": "timeframe", "event_type": "event_bucket"})
    )
    out["events_per_1k_bars"] = out["sample_count"] * 1000.0 / out["avg_rows_per_symbol"].replace(0, pd.NA)
    out["avg_bars_between_events"] = out["avg_rows_per_symbol"] / out["sample_count"].replace(0, pd.NA)
    out["density_note"] = "approx via sample_meta avg rows per symbol"
    keep = ["sample_key", "timeframe", "period", "asset", "event_bucket", "sample_count", "events_per_1k_bars", "avg_bars_between_events", "density_note"]
    return out[keep].sort_values(["sample_key", "asset", "event_bucket"]).reset_index(drop=True)


def build_event_taxonomy_card(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    rows = []
    mapping = {
        'breakout_long': ('breakout', 'confirmed_breakout_long', 'Current source event is already a confirmed breakout-style trade sample; it is not raw_breach or confirm1 separated.'),
        'breakout_short': ('breakout', 'confirmed_breakout_short', 'Current source event is already a confirmed breakout-style trade sample; it is not raw_breach or confirm1 separated.'),
        'rebound_long': ('rebound', 'confirmed_rebound_long', 'Current source event is already a rebound-style trade sample after confirmation logic; it is not a pure touch-only sample.'),
        'rebound_short': ('rebound', 'confirmed_rebound_short', 'Current source event is already a rebound-style trade sample after confirmation logic; it is not a pure touch-only sample.'),
    }
    for event_type in sorted(trades['event_type'].dropna().unique().tolist()):
        sub = trades[trades['event_type'] == event_type]
        strategy = sub['strategy'].mode().iloc[0] if 'strategy' in sub.columns and not sub['strategy'].dropna().empty else ''
        confirm_bars = sub['confirm_bars'].mode().iloc[0] if 'confirm_bars' in sub.columns and not sub['confirm_bars'].dropna().empty else ''
        family, foundation_bucket, note = mapping.get(event_type, ('unknown', 'unknown', 'No mapping note yet.'))
        rows.append([
            event_type,
            strategy,
            family,
            foundation_bucket,
            confirm_bars,
            note,
        ])
    return pd.DataFrame(rows, columns=['source_event_type', 'source_strategy', 'foundation_family', 'mapped_bucket', 'source_confirm_bars', 'why_this_mapping_is_not_the_full_ladder'])


def build_source_limitations(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    breakout_conf = sorted(pd.to_numeric(trades.loc[trades['strategy'] == 'breakout', 'confirm_bars'], errors='coerce').dropna().astype(int).unique().tolist())
    rebound_conf = sorted(pd.to_numeric(trades.loc[trades['strategy'] == 'rebound', 'confirm_bars'], errors='coerce').dropna().astype(int).unique().tolist())
    rows = [
        ['current source does not expose full confirmation ladder', f'breakout confirm_bars={breakout_conf}; rebound confirm_bars={rebound_conf}', 'The current slope-audit source already collapses events into one confirmed breakout flavor and one confirmed rebound flavor, so it cannot yet populate raw_breach vs close_confirm vs confirm1 vs confirm3 comparisons.'],
        ['current source is trade-sample oriented, not full event-universe oriented', 'trade_detail.csv contains triggered strategy events', 'This means event density / coverage are already useful, but taxonomy-level comparison must be read as “current implemented samples”, not the final full foundation event universe.'],
    ]
    return pd.DataFrame(rows, columns=['limitation', 'current_evidence', 'why_it_matters'])


def build_data_gap_checklist() -> pd.DataFrame:
    rows = [
        ['event_universe_table', 'Need one row per detected event candidate before trade-rule filtering', 'Without this, foundation cannot compare raw_breach / close_confirm / confirm1 / confirm3 as a full event universe; current trade_detail only contains triggered strategy samples.'],
        ['event_bucket_enum', 'Need explicit enum for raw_breach / close_confirm_same_bar / confirm1 / confirm3 / retest_hold / wick_rejection_only / touch_close_back_inside / touch_next_bar_continuation', 'Without a stable bucket enum, different agents may keep collapsing events into incompatible labels.'],
        ['line_object_id', 'Need a stable line identifier that survives from line detection into event evaluation', 'This is required to separate line lifecycle from event lifecycle and to avoid re-deriving identity ad hoc in each script.'],
        ['event_timestamp_fields', 'Need explicit event start / confirm / fail timestamps', 'These fields let us measure forward windows, time-to-fail, and confirmed-switch latency without guessing from trade entries.'],
        ['state_transition_fields', 'Need explicit provisional_break / confirmed_switch state fields', 'Current source only implies confirmation through fixed confirm_bars, but the foundation taxonomy needs state transitions directly represented.'],
        ['symbol_bar_count_by_sample', 'Need precise per-symbol bar counts in each sample universe', 'Current event_density uses sample_meta average rows per symbol, which is a useful approximation but not a precise denominator.'],
    ]
    return pd.DataFrame(rows, columns=['missing_piece', 'why_needed', 'what_breaks_without_it'])


def build_bucket_glossary() -> pd.DataFrame:
    rows = [
        ['event_bucket', 'confirmed_breakout_long / short', '当前 foundation 已接入的 breakout 样本行；它们已经是确认后的 trade-style 事件，不等于 full ladder 里的 raw_breach。', 'connected now'],
        ['event_bucket', 'confirmed_rebound_long / short', '当前 foundation 已接入的 rebound 样本行；它们已经过了现有确认逻辑，不是纯 touch-only 事件。', 'connected now'],
        ['future ladder bucket', 'raw_breach / close_confirm_same_bar / confirm1 / confirm3 / retest_hold', '完整 event-study 最终要直接比较的 confirmation ladder 层；目前还缺 direct rows。', 'missing now'],
        ['line_side', 'support / resistance', '事件发生在线的哪一侧；后续默认至少做 support vs resistance 分层。', 'connected now'],
        ['slope bucket', 'up_* / down_* / flat', '当前用于表达趋势线斜率方向与强度的离散桶；重点不是精确斜率值，而是方向 × 大小是否改变结果。', 'partially connected'],
        ['quality bucket', 'score_bucket / line_quality_bucket / num_points_bucket', '当前用于表达线质量的离散桶；重点是 higher-score / denser-line 是否更像有效事件。', 'partially connected'],
        ['source scope', 'representative_only vs all_valid', '代表线压缩是否改变结论方向；目前 foundation 默认仍以 representative_only 为主。', 'all_valid pending'],
        ['external constraint bucket', 'gross / net_low / net_high / bubble_proxy', '这不是 event bucket 本身，而是后续 breakout 研究默认应报告的外部约束切片。', 'connected as external evidence'],
        ['protocol layer', 'confirmation_level protocol', '这表示 confirmation 不再只是某个 source 的局部实现，而已经被提升成 Mainline 的统一比较 contract。', 'connected now'],
    ]
    return pd.DataFrame(rows, columns=['bucket_type', 'bucket_label', 'plain_language_definition', 'status'])


def build_source_provenance(trade_detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append([
        'PyIndicators slope audit source',
        'connected',
        'reports/artifacts/trendline_event_slope_audit/trade_detail.csv',
        f"event rows={len(trade_detail)} across default assets {', '.join(DEFAULT_ASSETS)}",
        'Current foundation page already uses this as the first real-data base for taxonomy mapping / sample coverage / event density.',
    ])

    sample_meta_path = CONFIRMATION_DIR / 'sample_meta.csv'
    if sample_meta_path.exists():
        sample_meta = pd.read_csv(sample_meta_path)
        samples = ', '.join(sample_meta['sample_key'].astype(str).tolist())
        rows.append([
            'PyIndicators confirmation ladder',
            'connected',
            'reports/artifacts/trendline_confirmation_ladder/summary.json',
            f"sample windows={samples}",
            'This source already extends the foundation with confirmation evidence and currently supports the mainline judgement that breakout remains weak while retained rebound subsets look more alive.',
        ])
    else:
        rows.append([
            'PyIndicators confirmation ladder',
            'missing',
            'reports/artifacts/trendline_confirmation_ladder/summary.json',
            'not found',
            'Without this source, foundation would remain stuck before the confirmation trade-off layer.',
        ])

    pyt_summary_path = PYT_VAL_DIR / 'summary.json'
    if pyt_summary_path.exists():
        pyt_summary = json.loads(pyt_summary_path.read_text(encoding='utf-8'))
        rows.append([
            'PyTrendline validation v1',
            'connected (bridge-v1)',
            'reports/artifacts/pytrendline_event_validation/summary.json',
            f"events={pyt_summary.get('total_events')} | matched={pyt_summary.get('matched_events')} | sample={pyt_summary.get('sample_key')}",
            'This source is now visible to the foundation as a new event-source candidate, but it still only covers BTC-USD / 10d / 5m and mostly breakout/touch semantics.',
        ])
    else:
        rows.append([
            'PyTrendline validation v1',
            'pending',
            'reports/artifacts/pytrendline_event_validation/summary.json',
            'not connected yet',
            'Foundation still needs a pytrendline-backed event source to avoid staying PyIndicators-only.',
        ])

    xeng_path = XENG_DIR / 'summary.json'
    if xeng_path.exists():
        xeng = json.loads(xeng_path.read_text(encoding='utf-8'))
        rows.append([
            'Cross-engine source comparison',
            'connected',
            'reports/artifacts/cross_engine_source_comparison/summary.json',
            f"PyIndicators trades={xeng.get('pyindicators_total_trades')} | PyTrendline events={xeng.get('pytrendline_total_events')}",
            'This source does not create new event rows, but it already audits relative maturity / evidence breadth and should be read as provenance context for why the foundation still leans on PyIndicators first.',
        ])

    svogun_path = SVOGUN_DIR / 'summary.json'
    if svogun_path.exists():
        svogun = json.loads(svogun_path.read_text(encoding='utf-8'))
        rows.append([
            'External constraint track (Svogun 2022)',
            'connected (external evidence)',
            'reports/artifacts/svogun2022_cost_regime_experiment/summary.json',
            f"rules={', '.join(svogun.get('rules', []))} | events={svogun.get('total_events')}",
            'This source is not part of the event-universe itself, but it already adds one crucial constraint to foundation reading: future breakout research should report gross / net / regime splits by default.',
        ])
    else:
        rows.append([
            'External constraint track (Svogun 2022)',
            'pending',
            'reports/artifacts/svogun2022_cost_regime_experiment/summary.json',
            'not connected yet',
            'Without an external cost/regime constraint track, foundation risks staying too gross-only / in-sample-only.',
        ])

    if CONFIRMATION_PROTOCOL_DOC.exists():
        rows.append([
            'Confirmation protocol layer',
            'connected (protocol)',
            'docs/TRENDLINE_CONFIRMATION_PROTOCOL.md',
            'breakout / rebound ladder labels, required fields, required output tables, default judgement rules',
            'This layer does not add new rows by itself, but it upgrades confirmation comparison from a PyIndicators-local implementation into a Mainline-level contract that future sources can plug into.',
        ])

    rows.append([
        'Full event-universe / ladder-native source',
        'missing',
        'future event_universe_table + event_bucket_enum',
        'raw_breach / close_confirm / confirm1 / confirm3 / retest_hold still absent as direct rows',
        'This remains the biggest missing source layer before foundation can become a true full event-study page rather than a stitched partial-stats page.',
    ])
    return pd.DataFrame(rows, columns=['source_layer', 'status', 'path', 'current_scope', 'why_it_matters'])


def render_html(event_taxonomy: pd.DataFrame, source_limitations: pd.DataFrame, data_gaps: pd.DataFrame, sample_coverage: pd.DataFrame, event_density: pd.DataFrame, bucket_glossary: pd.DataFrame, source_provenance: pd.DataFrame, trade_detail: pd.DataFrame) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    artifact_rows = pd.DataFrame([
        {"slug": a.slug, "title": a.title, "question answered": a.question, "suggested fields": ", ".join(a.suggested_fields)}
        for a in ARTIFACTS
    ])
    io_rows = pd.DataFrame(
        [
            ["Primary design source", "docs/RESEARCH_TRENDLINE_EVENT.md"],
            ["Primary task source", "docs/TODO.md"],
            ["Current real-data source", "reports/artifacts/trendline_event_slope_audit/trade_detail.csv"],
            ["Current density source", "reports/artifacts/trendline_event_slope_audit/sample_meta.csv"],
            ["Report html", "reports/site/factors/trendline_event_foundation/report.html"],
            ["Machine-readable contract", "reports/site/factors/trendline_event_foundation/contract.json"],
            ["Exported CSV (coverage)", "reports/artifacts/trendline_event_foundation/sample_coverage_table.csv"],
            ["Exported CSV (density)", "reports/artifacts/trendline_event_foundation/event_density_summary.csv"],
        ],
        columns=["contract part", "path / role"],
    )
    read_order = pd.DataFrame(
        [
            ["1", "sample_coverage_table", "先确认样本够不够，哪些 bucket 只能展示。"],
            ["2", "event_density_summary", "确认事件不是过稀也不是噪声级过密。"],
            ["3", "breakout / rebound confirmation comparison", "下一步最该先填充的真实统计块。"],
            ["4", "slope_bucket_summary", "在确认层之后再看 sign / magnitude 是否稳定解释。"],
            ["5", "quality_bucket_summary", "再看 num_points / score / representative 是否有增量信息。"],
            ["6", "go / feature / park judgement", "最后才下结论，不应跳读。"],
        ],
        columns=["step", "artifact", "why read here"],
    )
    status_rows = pd.DataFrame(
        [
            ["Current page status", "partial_stats", "已从 contract-only 升级为 partial stats：sample coverage 与 event density 已用真实 slope audit 数据填充。"],
            ["Currently filled artifacts", "event_taxonomy_card, source_limitations, data_gap_checklist, sample_coverage_table, event_density_summary", "优先先把 taxonomy mapping、source limitations、data gaps、样本量与事件频率这些后续结论最依赖的基础面放实。"],
            ["Current real-data universe", ", ".join(DEFAULT_ASSETS), f"当前真实数据来自 slope audit，事件样本数={len(trade_detail)}。"],
        ],
        columns=["status", "value", "why it matters"],
    )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Trendline Event Foundation Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111827; margin: 0; background: #ffffff; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 32px 20px 64px; }}
    .hero {{ border: 1px solid #e5e7eb; border-radius: 16px; padding: 22px 24px; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); margin-bottom: 20px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 34px; }}
    .muted {{ color: #6b7280; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 14px; padding: 18px 20px; margin: 16px 0; }}
    .pill-list {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; }}
    .pill {{ display:inline-block; padding:6px 10px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:13px; }}
    .table-wrap {{ overflow-x:auto; }}
    .tbl {{ width:100%; border-collapse:collapse; font-size:14px; }}
    .tbl th, .tbl td {{ border-bottom:1px solid #e5e7eb; text-align:left; vertical-align:top; padding:8px 10px; }}
    code {{ background:#f8fafc; border:1px solid #e5e7eb; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <p><a href="../index.html">← Back to factors index</a></p>
    <div class="hero">
      <h1>Trendline Event Foundation Report</h1>
      <p class="muted">This page now sits between the design docs and the first full event-study implementation. It still is <strong>not</strong> a final trading-system report, but it is no longer contract-only: the first two real-data sections are already filled using the current <code>trendline_event_slope_audit</code> outputs.</p>
      <div class="pill-list">
        <span class="pill">Generated: {escape(generated_at)}</span>
        <span class="pill">Status: partial stats</span>
        <span class="pill">Filled now: taxonomy + sample coverage + event density</span>
      </div>
    </div>

    <div class="card">
      <h2>Current page status</h2>
      {render_table(status_rows)}
    </div>

    <div class="card">
      <h2>What this page is for</h2>
      <p class="muted">The job of this report is to answer a narrower question than a full strategy page: after a trendline-related event occurs, does the future price distribution shift in a stable way, and if so does that event look more like standalone alpha, confirmation/filter, or just a feature?</p>
      <ul>
        <li>It is <strong>not</strong> a final trading-system report.</li>
        <li>It is <strong>not</strong> a PnL-first page.</li>
        <li>It is the bridge between design docs and a real event-study implementation.</li>
      </ul>
    </div>

    <div class="card">
      <h2>Input / output contract</h2>
      {render_table(io_rows)}
    </div>

    <div class="card">
      <h2>Current source provenance / what is already connected</h2>
      <p class="muted">This is the missing auditability block: it makes explicit which source layers are already feeding the foundation, which ones only provide surrounding evidence, and which ones still are not connected. Read this before assuming the page is already a full ladder-native event universe.</p>
      {render_table(source_provenance)}
    </div>

    <div class="card">
      <h2>Bucket glossary / how to read the labels</h2>
      <p class="muted">This is the reader-facing glossary that was still missing: it explains, in plain language, what the current event / slope / quality / source-scope buckets mean, so readers do not have to jump back into design docs just to decode the labels.</p>
      {render_table(bucket_glossary)}
    </div>

    <div class="card">
      <h2>Current source event taxonomy mapping</h2>
      <p class="muted">This is the first real bridge between the current implemented slope-audit data and the richer foundation taxonomy. It shows how the currently available source event buckets map into the broader event families used by the foundation design.</p>
      {render_table(event_taxonomy)}
    </div>

    <div class="card">
      <h2>Current source limitations</h2>
      <p class="muted">Before reading any future confirmation comparisons, it is important to know what the current source does <strong>not</strong> contain yet.</p>
      {render_table(source_limitations)}
    </div>

    <div class="card">
      <h2>Data gaps to unlock the full ladder</h2>
      <p class="muted">This is the concrete checklist for upgrading the current source into a full foundation event universe. It makes explicit what still needs to exist before the page can compare raw breach, close confirm, confirm1, confirm3, and retest-hold as separate event buckets.</p>
      {render_table(data_gaps)}
    </div>

    <div class="card">
      <h2>Sample coverage table</h2>
      <p class="muted">First real-data fill. This answers which <code>sample_key × asset × timeframe × side × event bucket</code> combinations currently have enough samples to support reading, weak conclusions, or only display-only usage.</p>
      {render_table(sample_coverage)}
    </div>

    <div class="card">
      <h2>Event density summary</h2>
      <p class="muted">Second real-data fill. This estimates how sparse or frequent each event bucket currently is. For now, density is approximated from <code>sample_meta.csv</code> using average rows per symbol in each sample universe.</p>
      {render_table(event_density)}
    </div>

    <div class="card">
      <h2>Minimum artifact blueprint</h2>
      {render_table(artifact_rows)}
    </div>

    <div class="card">
      <h2>Default reading order</h2>
      {render_table(read_order)}
    </div>

    <div class="card">
      <h2>Implementation notes for the next agent</h2>
      <ul>
        <li>Default universe remains: BTC / ETH / SOL / DOGE / XRP.</li>
        <li>Default timeframes remain: 30m / 60m, but currently available filled data also includes 60m long-sample variants from slope audit.</li>
        <li>Default line universe remains: <code>representative only</code>, with <code>all valid</code> as sensitivity later.</li>
        <li>Next recommended filled sections: <code>breakout_confirmation_comparison</code> and <code>rebound_confirmation_comparison</code>.</li>
        <li>Keep <code>go / feature / park</code> as the top-level judgement output.</li>
      </ul>
    </div>
  </div>
</body>
</html>'''


def build_contract(event_taxonomy: pd.DataFrame, data_gaps: pd.DataFrame, sample_coverage: pd.DataFrame, event_density: pd.DataFrame, bucket_glossary: pd.DataFrame, source_provenance: pd.DataFrame) -> dict:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "partial_stats",
        "design_source": "docs/RESEARCH_TRENDLINE_EVENT.md",
        "task_source": "docs/TODO.md",
        "filled_artifacts": ["event_taxonomy_card", "source_limitations", "data_gap_checklist", "sample_coverage_table", "event_density_summary", "bucket_glossary", "source_provenance"],
        "planned_artifacts": [
            {
                "slug": a.slug,
                "title": a.title,
                "question": a.question,
                "suggested_fields": a.suggested_fields,
            }
            for a in ARTIFACTS
        ],
        "default_scope": {
            "assets": DEFAULT_ASSETS,
            "timeframes": ["30m", "60m"],
            "line_universe": "representative_only",
        },
        "data_gaps_to_full_ladder": data_gaps.to_dict(orient="records"),
        "current_sources": {
            "trade_detail": "reports/artifacts/trendline_event_slope_audit/trade_detail.csv",
            "sample_meta": "reports/artifacts/trendline_event_slope_audit/sample_meta.csv",
            "confirmation_ladder": "reports/artifacts/trendline_confirmation_ladder/summary.json",
            "confirmation_protocol": "docs/TRENDLINE_CONFIRMATION_PROTOCOL.md",
            "pytrendline_validation_v1": "reports/artifacts/pytrendline_event_validation/summary.json",
            "cross_engine_source_comparison": "reports/artifacts/cross_engine_source_comparison/summary.json",
            "svogun_cost_regime_experiment": "reports/artifacts/svogun2022_cost_regime_experiment/summary.json",
        },
        "bucket_glossary": bucket_glossary.to_dict(orient="records"),
        "source_provenance": source_provenance.to_dict(orient="records"),
        "current_row_counts": {
            "event_taxonomy_card": int(len(event_taxonomy)),
            "data_gap_checklist": int(len(data_gaps)),
            "sample_coverage_table": int(len(sample_coverage)),
            "event_density_summary": int(len(event_density)),
            "bucket_glossary": int(len(bucket_glossary)),
            "source_provenance": int(len(source_provenance)),
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    trades = load_trade_detail()
    sample_meta = load_sample_meta()
    event_taxonomy = build_event_taxonomy_card(trades)
    source_limitations = build_source_limitations(trades)
    data_gaps = build_data_gap_checklist()
    sample_coverage = build_sample_coverage(trades)
    event_density = build_event_density(trades, sample_meta)
    bucket_glossary = build_bucket_glossary()
    source_provenance = build_source_provenance(trades)

    OUT_HTML.write_text(render_html(event_taxonomy, source_limitations, data_gaps, sample_coverage, event_density, bucket_glossary, source_provenance, trades), encoding="utf-8")
    OUT_META.write_text(json.dumps(build_contract(event_taxonomy, data_gaps, sample_coverage, event_density, bucket_glossary, source_provenance), ensure_ascii=False, indent=2), encoding="utf-8")
    event_taxonomy.to_csv(ARTIFACTS_DIR / "event_taxonomy_card.csv", index=False)
    data_gaps.to_csv(ARTIFACTS_DIR / "data_gap_checklist.csv", index=False)
    sample_coverage.to_csv(ARTIFACTS_DIR / "sample_coverage_table.csv", index=False)
    event_density.to_csv(ARTIFACTS_DIR / "event_density_summary.csv", index=False)
    bucket_glossary.to_csv(ARTIFACTS_DIR / "bucket_glossary.csv", index=False)
    source_provenance.to_csv(ARTIFACTS_DIR / "source_provenance.csv", index=False)
    print(f"[ok] wrote {OUT_HTML}")
    print(f"[ok] wrote {OUT_META}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'event_taxonomy_card.csv'}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'data_gap_checklist.csv'}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'sample_coverage_table.csv'}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'event_density_summary.csv'}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'bucket_glossary.csv'}")
    print(f"[ok] wrote {ARTIFACTS_DIR / 'source_provenance.csv'}")


if __name__ == "__main__":
    main()
