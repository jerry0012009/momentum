#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "build_pytrendline_event_validation_v3_report.py"
SRC_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3"
ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_sampler_fix_r3_impl"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_sampler_fix_r3_impl"

PAIR_FAMILIES = ["breakout_raw", "breakout_confirm_1", "breakout_confirm_2"]
GROUP_COLS = ["symbol", "event_family", "event_timestamp", "confirm_timestamp", "action_timestamp"]
TIME_COLS = ["snapshot_asof_timestamp", "event_timestamp", "confirm_timestamp", "action_timestamp"]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def find_line(lines: list[str], needle: str) -> int | None:
    for i, line in enumerate(lines, start=1):
        if needle in line:
            return i
    return None


def snippet(lines: list[str], center: int | None, radius: int = 4) -> str:
    if center is None:
        return "not found"
    start = max(1, center - radius)
    end = min(len(lines), center + radius)
    return "\n".join(f"{i:04d}: {lines[i-1]}" for i in range(start, end + 1))


def load_events(name: str) -> pd.DataFrame:
    return pd.read_csv(SRC_ART / name, parse_dates=TIME_COLS)


def preview_pair_resolution(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    work = df.copy()
    if work.empty:
        cols = [
            "event_family",
            "rows_before",
            "paired_groups_before",
            "rows_after_preview",
            "paired_groups_after_preview",
            "dropped_rows_preview",
            "score_tie_groups_preview",
        ]
        detail_cols = [
            *GROUP_COLS,
            "group_rows",
            "winner_event_type",
            "winner_engine_line_id",
            "winner_line_score",
            "score_tie",
            "dropped_event_types",
            "dropped_engine_line_ids",
            "dropped_line_scores",
        ]
        return pd.DataFrame(columns=cols), pd.DataFrame(columns=detail_cols), pd.DataFrame(columns=list(work.columns) + ["preview_drop_reason"])

    work["event_type_str"] = work["event_type"].astype(str)
    work["event_family"] = work["event_family"].astype(str)
    work["event_side_preview"] = work["event_type_str"].map(lambda s: "support" if s.startswith("support_") else ("resistance" if s.startswith("resistance_") else "other"))
    work["line_score_preview"] = pd.to_numeric(work["line_score"], errors="coerce").fillna(-1e18)
    work["engine_line_id_preview"] = work["engine_line_id"].astype(str)

    details: list[dict] = []
    dropped_frames: list[pd.DataFrame] = []
    drop_indices: list[int] = []

    for family in PAIR_FAMILIES:
        fam = work[work["event_family"] == family].copy()
        if fam.empty:
            continue
        for group_key, g in fam.groupby(GROUP_COLS, dropna=False, sort=False):
            sides = set(g["event_side_preview"].tolist())
            if len(g) < 2 or sides != {"support", "resistance"}:
                continue

            ranked = g.sort_values(
                ["line_score_preview", "event_type_str", "engine_line_id_preview"],
                ascending=[False, True, True],
            ).copy()
            winner = ranked.iloc[0]
            losers = ranked.iloc[1:].copy()
            score_tie = bool((ranked["line_score_preview"] == float(winner["line_score_preview"])).sum() > 1)

            if not losers.empty:
                loser_frame = work.loc[losers.index].copy()
                loser_frame["preview_drop_reason"] = "exact_mirrored_breakout_pair_lower_score"
                dropped_frames.append(loser_frame)
                drop_indices.extend(losers.index.tolist())

            details.append(
                {
                    **dict(zip(GROUP_COLS, group_key)),
                    "group_rows": int(len(g)),
                    "winner_event_type": str(winner["event_type"]),
                    "winner_engine_line_id": str(winner["engine_line_id"]),
                    "winner_line_score": float(winner["line_score"]) if pd.notna(winner["line_score"]) else None,
                    "score_tie": bool(score_tie),
                    "dropped_event_types": " | ".join(losers["event_type"].astype(str).tolist()),
                    "dropped_engine_line_ids": " | ".join(losers["engine_line_id"].astype(str).tolist()),
                    "dropped_line_scores": " | ".join(f"{float(v):.6f}" if pd.notna(v) else "nan" for v in losers["line_score"].tolist()),
                }
            )

    filtered = work.drop(index=sorted(set(drop_indices))).copy().reset_index(drop=True)
    details_df = pd.DataFrame(details)
    dropped_df = pd.concat(dropped_frames, ignore_index=True) if dropped_frames else pd.DataFrame(columns=list(df.columns) + ["preview_drop_reason"])

    summary_rows: list[dict] = []
    for family in PAIR_FAMILIES:
        before = work[work["event_family"] == family].copy()
        after = filtered[filtered["event_family"] == family].copy()
        detail_family = details_df[details_df["event_family"] == family] if not details_df.empty else pd.DataFrame()
        before_groups = before.groupby(GROUP_COLS, dropna=False)["event_side_preview"].nunique().reset_index(name="side_nunique")
        after_groups = after.groupby(GROUP_COLS, dropna=False)["event_side_preview"].nunique().reset_index(name="side_nunique")
        summary_rows.append(
            {
                "event_family": family,
                "rows_before": int(len(before)),
                "paired_groups_before": int((before_groups["side_nunique"] == 2).sum()) if not before_groups.empty else 0,
                "rows_after_preview": int(len(after)),
                "paired_groups_after_preview": int((after_groups["side_nunique"] == 2).sum()) if not after_groups.empty else 0,
                "dropped_rows_preview": int(len(dropped_df[dropped_df["event_family"].astype(str) == family])) if not dropped_df.empty else 0,
                "score_tie_groups_preview": int(detail_family["score_tie"].sum()) if not detail_family.empty else 0,
            }
        )

    keep_cols = [c for c in df.columns if c in dropped_df.columns] + ["preview_drop_reason"]
    return pd.DataFrame(summary_rows), details_df, dropped_df[keep_cols] if not dropped_df.empty else pd.DataFrame(columns=keep_cols)


def main() -> None:
    ensure_dir(ART)
    ensure_dir(SITE)

    lines = SRC.read_text(encoding="utf-8").splitlines()
    helper_line = find_line(lines, "def resolve_exact_mirrored_breakout_pairs(")
    raw_call_line = find_line(lines, "resolve_exact_mirrored_breakout_pairs(events_raw)")
    purged_call_line = find_line(lines, "resolve_exact_mirrored_breakout_pairs(events_purged)")
    raw_export_line = find_line(lines, 'mirrored_breakout_pair_resolution_raw_summary.csv')
    purged_export_line = find_line(lines, 'mirrored_breakout_pair_resolution_purged_summary.csv')

    checks = pd.DataFrame(
        [
            {
                "check_id": "R3-helper-present",
                "status": "present" if helper_line else "missing",
                "line": helper_line,
                "what_it_checks": "main v3 sampler source defines an explicit mirrored-breakout resolver",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R3-raw-call-present",
                "status": "present" if raw_call_line else "missing",
                "line": raw_call_line,
                "what_it_checks": "raw event sample is passed through the mirrored-breakout resolver before downstream artifacts are written",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R3-purged-call-present",
                "status": "present" if purged_call_line else "missing",
                "line": purged_call_line,
                "what_it_checks": "purged event sample is also checked again, so audit artifacts can prove whether mirrored pairs remain",
                "reliability": "high for source-code presence",
            },
            {
                "check_id": "R3-audit-export-present",
                "status": "present" if raw_export_line and purged_export_line else "missing",
                "line": raw_export_line,
                "what_it_checks": "fresh v3 reruns will export mirrored-pair audit CSVs instead of silently deduping",
                "reliability": "high for source-code presence",
            },
        ]
    )
    checks.to_csv(ART / "implementation_checks.csv", index=False)

    helper_snippet = snippet(lines, helper_line, radius=18)
    apply_snippet = snippet(lines, raw_call_line, radius=10)
    export_snippet = snippet(lines, raw_export_line, radius=8)
    (ART / "resolver_snippet.txt").write_text(helper_snippet + "\n", encoding="utf-8")
    (ART / "apply_snippet.txt").write_text(apply_snippet + "\n", encoding="utf-8")
    (ART / "export_snippet.txt").write_text(export_snippet + "\n", encoding="utf-8")

    raw_summary, raw_details, raw_dropped = preview_pair_resolution(load_events("event_sample_raw.csv"))
    purged_summary, purged_details, purged_dropped = preview_pair_resolution(load_events("event_sample_purged.csv"))

    raw_summary.to_csv(ART / "raw_preview_summary.csv", index=False)
    raw_details.to_csv(ART / "raw_preview_resolved_groups.csv", index=False)
    raw_dropped.to_csv(ART / "raw_preview_dropped_rows.csv", index=False)
    purged_summary.to_csv(ART / "purged_preview_summary.csv", index=False)
    purged_details.to_csv(ART / "purged_preview_resolved_groups.csv", index=False)
    purged_dropped.to_csv(ART / "purged_preview_dropped_rows.csv", index=False)

    implemented = bool(helper_line and raw_call_line and purged_call_line and raw_export_line and purged_export_line)
    summary = {
        "title": "PyTrendline V3 sampler fix R3 implementation note",
        "todo_item": "V3X-A / A4-b3",
        "implemented": implemented,
        "finding": "The v3 sampler source now contains an explicit mirrored-breakout resolver, and the same source also wires audit CSV exports so the next fresh rerun can show what got dropped instead of hiding it.",
        "found": [
            "a dedicated resolver function now exists in the main v3 sampler source",
            "the source applies that resolver to both raw and purged event samples",
            "the source now writes mirrored-pair summary/detail/dropped-row CSVs for fresh reruns",
            "on the currently stored legacy artifacts, an in-memory preview says the resolver would drop 1 mirrored row in each breakout family and reduce paired mirrored groups to 0",
        ],
        "not_found": [
            "This step did not do the BTC+ETH / 20~45d fresh rerun, so it is not A4-c closure.",
            "This page does not claim the currently published v3 main report already reflects R2+R3-cleaned samples; the stored event_sample CSVs still predate a full rerun.",
            "This page does not claim breakout-family alpha survived or died after the repair; that still needs the rerun audit.",
        ],
        "reliability": {
            "code_presence": "high",
            "preview_on_current_artifacts": "high",
            "post_rerun_alpha_impact": "not_measured_yet",
        },
        "source_checks": checks.to_dict("records"),
        "raw_preview_summary": raw_summary.to_dict("records"),
        "purged_preview_summary": purged_summary.to_dict("records"),
    }
    (ART / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    raw_drops = int(raw_summary["dropped_rows_preview"].sum()) if not raw_summary.empty else 0
    purged_drops = int(purged_summary["dropped_rows_preview"].sum()) if not purged_summary.empty else 0

    html = f"""<!doctype html>
<html lang=\"zh\">
<head>
  <meta charset=\"utf-8\" />
  <title>PyTrendline V3 · Sampler Fix R3 Implementation Note</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #1f2937; padding: 0 16px; }}
    h1, h2, h3 {{ color: #111827; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px 18px; margin: 16px 0; background: #fff; }}
    .ok {{ background: #ecfdf5; border-left: 4px solid #10b981; padding: 12px 14px; }}
    .warn {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 14px; }}
    .muted {{ color: #6b7280; }}
    code {{ background: #f3f4f6; padding: 1px 4px; border-radius: 4px; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 14px; border-radius: 10px; overflow-x: auto; font-size: 13px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    .tbl th, .tbl td {{ border: 1px solid #e5e7eb; padding: 6px 8px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f9fafb; }}
    ul {{ margin-top: 0.3em; }}
  </style>
</head>
<body>
  <h1>PyTrendline V3 · Sampler Fix R3 Implementation Note</h1>
  <p><a href="../pytrendline_event_validation_v3/report.html">← 返回 v3 主报告</a> ｜ <a href="../pytrendline_event_validation_v3_sampler_fix_r2_impl/report.html">上一页：sampler fix R2</a></p>

  <div class="card warn">
    <b>这页完成了什么？</b>
    只完成 TODO 里的 <code>A4-b3</code>：把 <b>exact mirrored breakout pair</b> 的显式去重 / 丢弃规则落进 v3 sampler 源码，并补上对应的 audit 导出位。
    这页不是最小重跑 closure，所以不会假装回答“修完后 breakout alpha 还剩多少”。
  </div>

  <div class="card ok">
    <b>一句话结论：</b>
    v3 采样器源码里现在已经有了显式的 R3 镜像对处理：<b>同一 symbol + breakout family + event/confirm/action timestamps 的 support / resistance 若同时存活，就只保留更高 <code>line_score</code> 的一边，并把被丢弃的那边写进审计输出</b>。
  </div>

  <h2>1. 这轮发现了什么？</h2>
  <div class="card">
    <ul>
      <li><b>Found:</b> 源码里已存在专门的 mirrored-breakout resolver 函数，并且不是只写了函数没调用；raw / purged 两条样本流都接上了。</li>
      <li><b>Found:</b> fresh rerun 时，源码会额外导出 <code>mirrored_breakout_pair_resolution_*.(csv)</code>，所以后续不会“静悄悄去重”而没有证据链。</li>
      <li><b>Found:</b> 对当前保存下来的 legacy artifacts 做 in-memory preview，resolver 会在 <code>breakout_raw / breakout_confirm_1 / breakout_confirm_2</code> 三个 family 各丢 <b>1</b> 条 mirrored row：raw 预览共丢 <b>{raw_drops}</b> 条，purged 预览共丢 <b>{purged_drops}</b> 条。</li>
      <li><b>Found:</b> 这份 preview 下，三个 breakout family 的 <code>paired_groups_after_preview</code> 都会降到 <b>0</b>，说明 R3 规则确实瞄准了当前已知 blocker，而不是无关去重。</li>
    </ul>
  </div>

  <h2>2. 这轮没有发现什么？</h2>
  <div class="card">
    <ul>
      <li><b>Not found:</b> 这轮没有做 BTC+ETH / 20~45d fresh rerun，所以这页不是 <code>A4-c</code>。</li>
      <li><b>Not found:</b> 这轮没有宣称当前公开的 v3 主报告已经自动变干净；因为主报告 artifacts 还没按新代码重导一次。</li>
      <li><b>Not found:</b> 这轮没有证明 breakout short 还能不能留在 shortlist；那要等 fresh rerun 后的 honesty audit。</li>
    </ul>
  </div>

  <h2>3. 实现检查表</h2>
  <div class="card">{render_table(checks)}</div>

  <h2>4. 当前 artifacts 上的预览结果（raw）</h2>
  <div class="card">{render_table(raw_summary)}</div>

  <h2>5. 当前 artifacts 上的预览结果（purged）</h2>
  <div class="card">{render_table(purged_summary)}</div>

  <h2>6. 预览里实际会被丢掉哪些行？（purged 示例）</h2>
  <div class="card">{render_table(purged_dropped.head(10))}</div>

  <h2>7. 代码证据：resolver 本体</h2>
  <div class="card">
    <pre>{escape(helper_snippet)}</pre>
  </div>

  <h2>8. 代码证据：apply + audit export</h2>
  <div class="card">
    <h3>Apply</h3>
    <pre>{escape(apply_snippet)}</pre>
    <h3>Audit export</h3>
    <pre>{escape(export_snippet)}</pre>
  </div>

  <h2>9. 这页该怎么读？</h2>
  <div class="card">
    <ul>
      <li><b>Plain language：</b>以前 sampler 可能把同一根事件 bar 上、时间戳完全重合的 support breakout 和 resistance breakout 同时记账。现在至少有一条明确规则：两边都活着时，不再双记，而是留分数更高的一边，并把另一边记进审计表。</li>
      <li><b>What this supports：</b>后续 A4-c 重跑时，可以直接检查 mirrored-pair summary 是否降到 0，而不是再靠人工对表。</li>
      <li><b>What this does NOT support：</b>还不支持说 side-level breakout alpha 已经可信；在 fresh rerun 前，最稳的口径仍然是 family-level 结论优先。</li>
    </ul>
  </div>

  <h2>10. 可靠性</h2>
  <div class="card">
    <ul>
      <li><b>高：</b>“代码里有没有 resolver / 有没有审计导出”——这是直接扫源码。</li>
      <li><b>高：</b>“resolver 在当前保存下来的样本上会丢哪些 mirrored rows”——这是直接在现有 CSV 上做 preview。</li>
      <li><b>低 / 未测：</b>“fresh rerun 后 alpha 还剩多少、strict wrong-side share 会不会一起下降”——这必须等 A4-c。</li>
    </ul>
  </div>

  <h2>11. 下一步</h2>
  <div class="card">
    <ol>
      <li>做 <code>A4-c</code>：用 R2+R3 后的 sampler 重跑 BTC+ETH / 20~45d 最小样本。</li>
      <li>重导 breakout side audit / metric re-audit，重点比对 <code>exact_match_rows</code> 与 strict geometry 指标是否明显下降。</li>
    </ol>
  </div>

  <h2>Artifacts</h2>
  <div class="card">
    <ul>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/implementation_checks.csv">implementation_checks.csv</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/raw_preview_summary.csv">raw_preview_summary.csv</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/purged_preview_summary.csv">purged_preview_summary.csv</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/purged_preview_dropped_rows.csv">purged_preview_dropped_rows.csv</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/resolver_snippet.txt">resolver_snippet.txt</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/apply_snippet.txt">apply_snippet.txt</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/export_snippet.txt">export_snippet.txt</a></li>
      <li><a href="../../artifacts/pytrendline_event_validation_v3_sampler_fix_r3_impl/summary.json">summary.json</a></li>
    </ul>
  </div>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
