#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_SCRIPT = ROOT / "scripts" / "build_pytrendline_event_validation_v3_report.py"
REAUDIT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_breakout_metric_reaudit"
SIDE_AUDIT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_breakout_side_audit"
ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_sampler_fix_spec"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_sampler_fix_spec"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_table(df: pd.DataFrame, limit: int = 50) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x):.1%}"


def main() -> None:
    ensure_dir(ART)
    ensure_dir(SITE)

    metric_df = pd.read_csv(REAUDIT_ART / "metric_reaudit_summary.csv")
    pair_df = pd.read_csv(REAUDIT_ART / "pair_focus_summary.csv")
    purged_geom_df = pd.read_csv(SIDE_AUDIT_ART / "purged_pair_geometry_audit.csv")

    raw_pairs = pd.read_csv(SIDE_AUDIT_ART / "purged_breakout_raw_pairs.csv")
    c1_pairs = pd.read_csv(SIDE_AUDIT_ART / "purged_breakout_confirm_1_pairs.csv")
    c2_pairs = pd.read_csv(SIDE_AUDIT_ART / "purged_breakout_confirm_2_pairs.csv")

    pair_examples = pd.concat(
        [
            raw_pairs.assign(family="breakout_raw"),
            c1_pairs.assign(family="breakout_confirm_1"),
            c2_pairs.assign(family="breakout_confirm_2"),
        ],
        ignore_index=True,
    )
    pair_examples = pair_examples[pair_examples["_merge"] == "both"].copy()
    keep_cols = [
        "family",
        "symbol",
        "snapshot_asof_timestamp",
        "event_timestamp",
        "confirm_timestamp",
        "action_timestamp",
        "event_high",
        "event_low",
        "event_close",
        "support_line_id",
        "support_line_value",
        "resistance_line_id",
        "resistance_line_value",
        "_merge",
    ]
    pair_examples = pair_examples[[c for c in keep_cols if c in pair_examples.columns]].reset_index(drop=True)
    pair_examples.to_csv(ART / "mirrored_pair_examples.csv", index=False)

    src_text = SRC_SCRIPT.read_text(encoding="utf-8")
    snapshot_guard_present = (
        "if lv_asof > (asof_close + tolerance):" in src_text
        and "if lv_asof < (asof_close - tolerance):" in src_text
    )

    def metric_row(sample: str, event_type: str) -> pd.Series:
        row = metric_df[(metric_df["sample"] == sample) & (metric_df["event_type"] == event_type)]
        if row.empty:
            raise KeyError(f"Missing metric row: {sample=} {event_type=}")
        return row.iloc[0]

    def pair_row(sample: str, family: str) -> pd.Series:
        row = pair_df[(pair_df["sample"] == sample) & (pair_df["family"] == family)]
        if row.empty:
            raise KeyError(f"Missing pair row: {sample=} {family=}")
        return row.iloc[0]

    support_raw = metric_row("purged", "support_breakout_raw")
    resistance_raw = metric_row("purged", "resistance_breakout_raw")
    support_c1 = metric_row("purged", "support_breakout_confirm_1")
    resistance_c1 = metric_row("purged", "resistance_breakout_confirm_1")
    support_c2 = metric_row("purged", "support_breakout_confirm_2")
    resistance_c2 = metric_row("purged", "resistance_breakout_confirm_2")
    pair_raw = pair_row("purged", "breakout_raw")
    pair_c1 = pair_row("purged", "breakout_confirm_1")
    pair_c2 = pair_row("purged", "breakout_confirm_2")

    rules = pd.DataFrame(
        [
            {
                "rule_id": "R1",
                "title": "Keep the snapshot-side visibility guard as the first screen",
                "scope": "All future breakout/touch candidates",
                "action": "Reject lines that are already on the wrong side at snapshot time before generating any event rows.",
                "why": "This is the earliest causal checkpoint: if a support line is already above price (or resistance already below price) when the snapshot becomes visible, later event labels are hard to interpret.",
                "current_status": "present_in_sampler_code" if snapshot_guard_present else "not_detected_in_sampler_code",
                "reliability": "high for code detection; medium for downstream impact",
            },
            {
                "rule_id": "R2",
                "title": "Drop strict wrong-side breakout rows at event time",
                "scope": "support/resistance breakout raw + confirm families",
                "action": "For support-side breakout rows, drop if line_value_event > event_high. For resistance-side breakout rows, drop if line_value_event < event_low.",
                "why": "These rows are not merely close-based breakouts; the entire event candle already sits on the wrong side of the labeled line, so the side tag is geometrically unreliable.",
                "current_status": "design_fixed_here_not_implemented_here",
                "reliability": "high for identifying bad rows; medium for how much alpha changes after rerun",
            },
            {
                "rule_id": "R3",
                "title": "Resolve exact mirrored breakout pairs after row-level filtering",
                "scope": "Rows sharing symbol + family + event/confirm/action timestamps across support/resistance",
                "action": "If only one side survives R2, keep that side. If both sides fail, drop both. If both sides survive, keep the higher-score row only as a temporary tie-break and mark it ambiguous in audit output.",
                "why": "The remaining mirrored rows are the clearest source of duplicated family returns. They should be handled explicitly instead of hoping the top-score-per-event_type rule removes them.",
                "current_status": "design_fixed_here_not_implemented_here",
                "reliability": "high that mirrored pairs exist; low-to-medium for the tie-break branch because this sample does not yet contain a clean surviving pair",
            },
            {
                "rule_id": "R4",
                "title": "Judge success by rerun audits, not by hope",
                "scope": "BTC+ETH / 20d-45d minimal rerun",
                "action": "After implementation, re-export the same audit tables and compare strict_wrong_side_rows and exact_match_rows before vs after.",
                "why": "A sampler fix is only credible if the known blockers shrink materially in the next audited sample.",
                "current_status": "next_step_after_this_spec",
                "reliability": "high",
            },
        ]
    )
    rules.to_csv(ART / "repair_rules.csv", index=False)

    removal_upper_bound = pd.DataFrame(
        [
            {
                "family": "breakout_raw",
                "support_rows": int(support_raw["rows"]),
                "support_strict_wrong_side_rows": int(support_raw["strict_wrong_side_rows"]),
                "support_strict_wrong_side_share": float(support_raw["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_raw["rows"]),
                "resistance_strict_wrong_side_rows": int(resistance_raw["strict_wrong_side_rows"]),
                "resistance_strict_wrong_side_share": float(resistance_raw["strict_wrong_side_share"]),
                "exact_mirrored_pairs": int(pair_raw["exact_match_rows"]),
            },
            {
                "family": "breakout_confirm_1",
                "support_rows": int(support_c1["rows"]),
                "support_strict_wrong_side_rows": int(support_c1["strict_wrong_side_rows"]),
                "support_strict_wrong_side_share": float(support_c1["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_c1["rows"]),
                "resistance_strict_wrong_side_rows": int(resistance_c1["strict_wrong_side_rows"]),
                "resistance_strict_wrong_side_share": float(resistance_c1["strict_wrong_side_share"]),
                "exact_mirrored_pairs": int(pair_c1["exact_match_rows"]),
            },
            {
                "family": "breakout_confirm_2",
                "support_rows": int(support_c2["rows"]),
                "support_strict_wrong_side_rows": int(support_c2["strict_wrong_side_rows"]),
                "support_strict_wrong_side_share": float(support_c2["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_c2["rows"]),
                "resistance_strict_wrong_side_rows": int(resistance_c2["strict_wrong_side_rows"]),
                "resistance_strict_wrong_side_share": float(resistance_c2["strict_wrong_side_share"]),
                "exact_mirrored_pairs": int(pair_c2["exact_match_rows"]),
            },
        ]
    )
    removal_upper_bound.to_csv(ART / "expected_removal_upper_bound.csv", index=False)

    summary = {
        "title": "PyTrendline V3 sampler fix spec v1",
        "finding": "narrow A4-b from a vague sampler-fix request into explicit repair rules: keep snapshot-side visibility gating, add event-time strict wrong-side filters, then resolve exact mirrored breakout pairs and judge success by a rerun audit",
        "snapshot_guard_present": snapshot_guard_present,
        "purged_breakout_strict_wrong_side": {
            "breakout_raw": {
                "support_share": float(support_raw["strict_wrong_side_share"]),
                "support_rows": int(support_raw["strict_wrong_side_rows"]),
                "resistance_share": float(resistance_raw["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_raw["strict_wrong_side_rows"]),
                "exact_mirrored_pairs": int(pair_raw["exact_match_rows"]),
            },
            "breakout_confirm_1": {
                "support_share": float(support_c1["strict_wrong_side_share"]),
                "support_rows": int(support_c1["strict_wrong_side_rows"]),
                "resistance_share": float(resistance_c1["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_c1["strict_wrong_side_rows"]),
                "exact_mirrored_pairs": int(pair_c1["exact_match_rows"]),
            },
            "breakout_confirm_2": {
                "support_share": float(support_c2["strict_wrong_side_share"]),
                "support_rows": int(support_c2["strict_wrong_side_rows"]),
                "resistance_share": float(resistance_c2["strict_wrong_side_share"]),
                "resistance_rows": int(resistance_c2["strict_wrong_side_rows"]),
                "exact_mirrored_pairs": int(pair_c2["exact_match_rows"]),
            },
        },
        "pair_geometry": {
            row["family"]: {
                "paired_rows": int(row["paired_rows"]),
                "crossed_lines_share": float(row["crossed_lines_share"]),
                "both_inverted_share": float(row["both_inverted_share"]),
                "close_between_lines_share": float(row["close_between_lines_share"]),
            }
            for _, row in purged_geom_df.iterrows()
        },
        "not_found": [
            "No evidence that all breakout rows are bad; the earlier 100% close-based inversion metric overstated the problem.",
            "No rerun after the proposed repair rules, so there is still no closure on whether breakout family alpha survives once the sampler is cleaned.",
            "No observed case in the current purged sample where an exact mirrored pair survives strict geometry cleanly on both sides, so the tie-break branch remains low-confidence.",
        ],
        "reliability": {
            "artifact_counts": "high",
            "repair_rule_spec": "medium",
            "post_fix_alpha_claim": "not_available_yet",
        },
    }
    (ART / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>PyTrendline V3 · Sampler Fix Spec v1</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #1f2937; padding: 0 16px; }}
    h1, h2, h3 {{ color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; background: #fff; }}
    .ok {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 12px 14px; }}
    .warn {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 14px; }}
    .muted {{ color: #6b7280; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    .tbl th, .tbl td {{ border: 1px solid #e5e7eb; padding: 6px 8px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f9fafb; }}
    ul {{ margin-top: 0.3em; }}
  </style>
</head>
<body>
  <h1>PyTrendline V3 · Sampler Fix Spec v1</h1>
  <p><a href=\"../pytrendline_event_validation_v3/report.html\">← 返回 v3 主报告</a> ｜ <a href=\"../pytrendline_event_validation_v3_breakout_metric_reaudit/report.html\">上一页：breakout metric re-audit</a></p>

  <div class=\"card warn\">
    <b>这页完成了什么？</b>
    把 TODO 里的 <code>A4-b</code> 从一句很大的“修 sampler”拆成更小、可执行的 repair spec。
    这页的目标不是宣称已经修好，而是先把 <b>该修什么、为什么修、修完要看什么</b> 写清楚。
  </div>

  <div class=\"card ok\">
    <b>一句话结论：</b>
    当前最合理的最小修法不是把全部 breakout 样本一刀切删掉，而是：<b>保留 snapshot 可见性门槛，新增 event-time strict wrong-side filter，再单独处理 exact mirrored breakout pairs</b>。
  </div>

  <h2>1. 这轮发现了什么？</h2>
  <div class=\"card\">
    <ul>
      <li><b>Found:</b> purged 样本里 breakout 仍有一批严格几何异常，不是 100%，但也不是可以忽略的小噪声：
        <ul>
          <li><code>support_breakout_raw</code> strict wrong-side share = <b>{pct(float(support_raw['strict_wrong_side_share']))}</b>（{int(support_raw['strict_wrong_side_rows'])}/{int(support_raw['rows'])}）</li>
          <li><code>resistance_breakout_raw</code> strict wrong-side share = <b>{pct(float(resistance_raw['strict_wrong_side_share']))}</b>（{int(resistance_raw['strict_wrong_side_rows'])}/{int(resistance_raw['rows'])}）</li>
          <li><code>support_breakout_confirm_1</code> = <b>{pct(float(support_c1['strict_wrong_side_share']))}</b>；<code>resistance_breakout_confirm_1</code> = <b>{pct(float(resistance_c1['strict_wrong_side_share']))}</b></li>
          <li><code>support_breakout_confirm_2</code> = <b>{pct(float(support_c2['strict_wrong_side_share']))}</b>；<code>resistance_breakout_confirm_2</code> = <b>{pct(float(resistance_c2['strict_wrong_side_share']))}</b></li>
        </ul>
      </li>
      <li><b>Found:</b> purged breakout 三个 family 各还留着 <b>1</b> 条 exact mirrored pair，而且 pair-level geometry 仍然是彻底异常：<code>crossed_lines_share = 100%</code>、<code>both_inverted_share = 100%</code>。</li>
      <li><b>Found:</b> 当前 sampler 源码里已经能检测到 snapshot 时刻的 side 可见性门槛（support 不应早已高于价格，resistance 不应早已低于价格）。说明下一步修法应继续往 <b>更晚一层的 event-time / pair-time 清洗</b> 补，而不是推翻已有全部逻辑。</li>
    </ul>
  </div>

  <h2>2. 这轮没有发现什么？</h2>
  <div class=\"card\">
    <ul>
      <li><b>Not found:</b> 没有证据支持“全部 breakout 行都坏了”。上一轮最刺眼的 <code>100%</code> close-based 指标，主要是在重复 breakout 定义本身。</li>
      <li><b>Not found:</b> 还没有修完后的最小重跑，因此这页不回答“修完后 breakout family 还剩多少 alpha”。</li>
      <li><b>Not found:</b> 当前 purged 样本里没有观察到“support / resistance 两边都严格几何合法、却还 exact mirrored”的 clean case，所以若未来两边都存活，临时 tie-break 只能先视为低置信 fallback。</li>
    </ul>
  </div>

  <h2>3. 建议的最小 repair rules</h2>
  <div class=\"card\">{render_table(rules)}</div>

  <h2>4. 预计会先扫掉多少坏样本？（上限估算）</h2>
  <div class=\"card\">
    <p>下面这个表不是“修后真实剩余量”，只是一个 <b>上限估算</b>：strict wrong-side rows 与 exact mirrored pairs 可能有重叠，所以不能简单相加。</p>
    {render_table(removal_upper_bound)}
  </div>

  <h2>5. 镜像坏样本示例</h2>
  <div class=\"card\">
    <p>这是当前 purged 样本里还能直接看到的 mirrored pair 示例。它的意义不是“样本很多”，而是证明：<b>剩下哪怕只有 1 条，也值得被 sampler 显式处理</b>，否则 family-level 统计里会继续混入重复记账。</p>
    {render_table(pair_examples, limit=10)}
  </div>

  <h2>6. 这页的可信度</h2>
  <div class=\"card\">
    <ul>
      <li><b>高：</b>坏样本数量、占比、mirrored pair 是否存在 —— 这些都直接来自现有 audit artifacts。</li>
      <li><b>中：</b>repair rule 的设计是否正好就是最佳实现 —— 这是设计页，不是跑完后的 closure 页。</li>
      <li><b>低 / 暂无：</b>修完后 breakout alpha 会不会彻底消失，或反而更稳定 —— 这必须等 A4-c 的最小重跑。</li>
    </ul>
  </div>

  <h2>Artifacts</h2>
  <div class=\"card\">
    <ul>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_spec/summary.json'>summary.json</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_spec/repair_rules.csv'>repair_rules.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_spec/expected_removal_upper_bound.csv'>expected_removal_upper_bound.csv</a></li>
      <li><a href='../../artifacts/pytrendline_event_validation_v3_sampler_fix_spec/mirrored_pair_examples.csv'>mirrored_pair_examples.csv</a></li>
      <li><a href='../pytrendline_event_validation_v3_breakout_metric_reaudit/report.html'>breakout metric re-audit</a></li>
      <li><a href='../pytrendline_event_validation_v3_breakout_side_audit/report.html'>breakout side audit</a></li>
    </ul>
  </div>

  <p class=\"muted\">Generated by <code>scripts/build_pytrendline_event_validation_v3_sampler_fix_spec_report.py</code>.</p>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"wrote {SITE / 'report.html'}")


if __name__ == "__main__":
    main()
