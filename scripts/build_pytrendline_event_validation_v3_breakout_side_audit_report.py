#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3"
ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v3_breakout_side_audit"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v3_breakout_side_audit"

PAIR_SPECS = [
    ("support_breakout_raw", "resistance_breakout_raw", "breakout_raw"),
    ("support_breakout_confirm_1", "resistance_breakout_confirm_1", "breakout_confirm_1"),
    ("support_breakout_confirm_2", "resistance_breakout_confirm_2", "breakout_confirm_2"),
]

TIME_COLS = ["snapshot_asof_timestamp", "event_timestamp", "confirm_timestamp", "action_timestamp"]
RET_COLS = ["fwd_ret_h6", "fwd_ret_h24", "fwd_ret_h48", "fwd_ret_h72"]
KEY_COLS = [
    "symbol",
    "snapshot_asof_timestamp",
    "event_timestamp",
    "confirm_timestamp",
    "action_timestamp",
    "event_open",
    "event_high",
    "event_low",
    "event_close",
    "confirm_close",
    "action_open",
    *RET_COLS,
]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_events(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=TIME_COLS)


def render_table(df: pd.DataFrame, limit: int | None = None) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.copy()
    if limit is not None:
        shown = shown.head(limit)
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def build_geometry_audit(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for event_type, g in df.groupby("event_type", sort=True):
        row = {
            "event_type": event_type,
            "rows": int(len(g)),
            # "price" here is defined as the event-bar close. We keep the more
            # specific *_close_share aliases too, so downstream readers/scripts can
            # see exactly which price reference was used.
            "support_above_price_share": None,
            "support_above_close_share": None,
            "support_above_high_share": None,
            "resistance_below_price_share": None,
            "resistance_below_close_share": None,
            "resistance_below_low_share": None,
        }
        if event_type.startswith("support"):
            share = float((g["line_value_event"] > g["event_close"]).mean())
            row["support_above_price_share"] = share
            row["support_above_close_share"] = share
            row["support_above_high_share"] = float((g["line_value_event"] > g["event_high"]).mean())
        elif event_type.startswith("resistance"):
            share = float((g["line_value_event"] < g["event_close"]).mean())
            row["resistance_below_price_share"] = share
            row["resistance_below_close_share"] = share
            row["resistance_below_low_share"] = float((g["line_value_event"] < g["event_low"]).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def build_pair_outputs(df: pd.DataFrame, label: str) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    summary_rows: list[dict] = []
    detail_frames: dict[str, pd.DataFrame] = {}

    for support_type, resistance_type, family in PAIR_SPECS:
        subset = df[df["event_type"].isin([support_type, resistance_type])].copy()
        grouped = (
            subset.groupby(["symbol", "snapshot_asof_timestamp", "event_timestamp"], dropna=False)["event_type"]
            .agg(groups_rows="size", event_type_nunique="nunique")
            .reset_index()
        )
        groups_total = int(len(grouped))
        both_groups = int((grouped["event_type_nunique"] == 2).sum())

        left = (
            subset[subset["event_type"] == support_type][KEY_COLS + ["engine_line_id", "line_value_event", "line_score", "line_slope"]]
            .rename(
                columns={
                    "engine_line_id": "support_line_id",
                    "line_value_event": "support_line_value",
                    "line_score": "support_line_score",
                    "line_slope": "support_line_slope",
                }
            )
            .copy()
        )
        right = (
            subset[subset["event_type"] == resistance_type][KEY_COLS + ["engine_line_id", "line_value_event", "line_score", "line_slope"]]
            .rename(
                columns={
                    "engine_line_id": "resistance_line_id",
                    "line_value_event": "resistance_line_value",
                    "line_score": "resistance_line_score",
                    "line_slope": "resistance_line_slope",
                }
            )
            .copy()
        )

        merged = left.merge(right, on=KEY_COLS, how="outer", indicator=True)
        merge_counts = merged["_merge"].value_counts().to_dict()
        detail_frames[family] = merged.copy()

        summary_rows.append(
            {
                "sample": label,
                "family": family,
                "support_rows": int(len(left)),
                "resistance_rows": int(len(right)),
                "same_bar_groups": groups_total,
                "groups_with_both_sides": both_groups,
                "both_side_share": float(both_groups / groups_total) if groups_total else 0.0,
                "exact_match_rows": int(merge_counts.get("both", 0)),
                "support_only_rows": int(merge_counts.get("left_only", 0)),
                "resistance_only_rows": int(merge_counts.get("right_only", 0)),
            }
        )

    return pd.DataFrame(summary_rows), detail_frames


def build_pair_geometry_audit(detail_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict] = []
    for family, merged in detail_frames.items():
        both = merged[merged["_merge"] == "both"].copy()
        if both.empty:
            rows.append(
                {
                    "family": family,
                    "paired_rows": 0,
                    "support_above_close_share": None,
                    "resistance_below_close_share": None,
                    "support_above_high_share": None,
                    "resistance_below_low_share": None,
                    "crossed_lines_share": None,
                    "close_between_lines_share": None,
                    "both_inverted_share": None,
                }
            )
            continue

        support_above_close = both["support_line_value"] > both["event_close"]
        resistance_below_close = both["resistance_line_value"] < both["event_close"]
        support_above_high = both["support_line_value"] > both["event_high"]
        resistance_below_low = both["resistance_line_value"] < both["event_low"]
        crossed_lines = both["support_line_value"] > both["resistance_line_value"]
        close_between_lines = (both["support_line_value"] <= both["event_close"]) & (both["event_close"] <= both["resistance_line_value"])
        both_inverted = support_above_close & resistance_below_close

        rows.append(
            {
                "family": family,
                "paired_rows": int(len(both)),
                "support_above_close_share": float(support_above_close.mean()),
                "resistance_below_close_share": float(resistance_below_close.mean()),
                "support_above_high_share": float(support_above_high.mean()),
                "resistance_below_low_share": float(resistance_below_low.mean()),
                "crossed_lines_share": float(crossed_lines.mean()),
                "close_between_lines_share": float(close_between_lines.mean()),
                "both_inverted_share": float(both_inverted.mean()),
            }
        )

    return pd.DataFrame(rows)


def build_summary_json(raw_pair_summary: pd.DataFrame, purged_pair_summary: pd.DataFrame, purged_geom: pd.DataFrame, purged_pair_geom: pd.DataFrame) -> dict:
    def geom_value(event_type: str, col: str) -> float | None:
        row = purged_geom[purged_geom["event_type"] == event_type]
        if row.empty:
            return None
        val = row.iloc[0][col]
        return None if pd.isna(val) else float(val)

    def pair_geom_value(family: str, col: str) -> float | None:
        row = purged_pair_geom[purged_pair_geom["family"] == family]
        if row.empty:
            return None
        val = row.iloc[0][col]
        return None if pd.isna(val) else float(val)

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "finding": "current breakout-side blocker is systemic line-side geometry inversion; same-bar mirror duplicates still exist but are no longer the main issue in the latest artifacts",
        "high_confidence_evidence": {
            "purged_breakout_raw_exact_match_rows": int(
                purged_pair_summary.loc[purged_pair_summary["family"] == "breakout_raw", "exact_match_rows"].iloc[0]
            ),
            "purged_breakout_confirm_1_exact_match_rows": int(
                purged_pair_summary.loc[purged_pair_summary["family"] == "breakout_confirm_1", "exact_match_rows"].iloc[0]
            ),
            "purged_breakout_confirm_2_exact_match_rows": int(
                purged_pair_summary.loc[purged_pair_summary["family"] == "breakout_confirm_2", "exact_match_rows"].iloc[0]
            ),
            "support_breakout_raw_support_above_price_share": geom_value("support_breakout_raw", "support_above_price_share"),
            "resistance_breakout_raw_resistance_below_price_share": geom_value("resistance_breakout_raw", "resistance_below_price_share"),
            "support_breakout_confirm_2_support_above_price_share": geom_value("support_breakout_confirm_2", "support_above_price_share"),
            "resistance_breakout_confirm_2_resistance_below_price_share": geom_value("resistance_breakout_confirm_2", "resistance_below_price_share"),
            "purged_breakout_raw_crossed_lines_share": pair_geom_value("breakout_raw", "crossed_lines_share"),
            "purged_breakout_confirm_1_crossed_lines_share": pair_geom_value("breakout_confirm_1", "crossed_lines_share"),
            "purged_breakout_confirm_2_crossed_lines_share": pair_geom_value("breakout_confirm_2", "crossed_lines_share"),
            "purged_breakout_raw_both_inverted_share": pair_geom_value("breakout_raw", "both_inverted_share"),
        },
        "not_found": [
            "no evidence that the duplication is caused by a summary-table printing bug",
            "no evidence that forward-return calculation itself is duplicated incorrectly",
            "not yet proven whether the root cause should be fixed by geometry gating alone or also by a line-lifecycle / attribution rule change",
        ],
        "reliability": {
            "pairing_diagnosis": "high",
            "geometry_inversion_diagnosis": "high",
            "exact_fix_design": "medium",
        },
        "raw_pair_summary": raw_pair_summary.to_dict(orient="records"),
        "purged_pair_summary": purged_pair_summary.to_dict(orient="records"),
        "purged_pair_geometry": purged_pair_geom.to_dict(orient="records"),
    }


def build_report(
    raw_pair_summary: pd.DataFrame,
    purged_pair_summary: pd.DataFrame,
    raw_geom: pd.DataFrame,
    purged_geom: pd.DataFrame,
    raw_pair_geom: pd.DataFrame,
    purged_pair_geom: pd.DataFrame,
) -> None:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    purged_raw_pair = purged_pair_summary[purged_pair_summary["family"] == "breakout_raw"].iloc[0]
    raw_raw_pair = raw_pair_summary[raw_pair_summary["family"] == "breakout_raw"].iloc[0]
    purged_geom_support = purged_geom[purged_geom["event_type"] == "support_breakout_raw"].iloc[0]
    purged_geom_resistance = purged_geom[purged_geom["event_type"] == "resistance_breakout_raw"].iloc[0]
    purged_pair_geom_raw = purged_pair_geom[purged_pair_geom["family"] == "breakout_raw"].iloc[0]

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline v3 breakout side audit</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .warn {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 10px; padding: 10px 12px; }}
    .ok {{ background: #ecfeff; border: 1px solid #a5f3fc; color: #155e75; border-radius: 10px; padding: 10px 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    ul {{ line-height: 1.7; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 6px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../pytrendline_event_validation_v3/report.html\">← 返回 v3 主报告</a></p>

    <div class=\"card\">
      <h1>PyTrendline v3 breakout side audit</h1>
      <p class=\"muted\">Generated: {escape(generated_at)}</p>
      <p>这页只回答一个问题：为什么 <code>support_breakout_*</code> 和 <code>resistance_breakout_*</code> 在 purged 样本里会长得像同一批事件？</p>
      <div class=\"warn\"><b>结论先说：</b>当前证据强烈支持：<b>breakout 的 side 标签还没有通过几何审计</b>。最新 artifacts 里，“同一 bar 被同时记成 support / resistance breakout”的 exact-match 配对只剩极少数；但更关键的问题还在——<code>support_breakout_*</code> 的 support 线在事件时仍系统性位于价格上方，<code>resistance_breakout_*</code> 的 resistance 线也系统性位于价格下方。</div>
    </div>

    <div class=\"card\">
      <h2>Plain-language summary</h2>
      <ul>
        <li><b>发现了什么：</b>在 <code>event_sample_purged.csv</code> 里，<code>support_breakout_raw</code> 与 <code>resistance_breakout_raw</code> 仍有 <b>{int(purged_raw_pair['exact_match_rows'])}</b> 条逐条 exact match，说明镜像配对问题还没彻底消失；但它已经不再是当前样本里的主量级问题。</li>
        <li><b>更关键的发现：</b><code>support_breakout_raw</code> 里，support 线在事件发生时有 <b>{purged_geom_support['support_above_price_share']:.1%}</b> 位于价格上方；<code>resistance_breakout_raw</code> 里，resistance 线有 <b>{purged_geom_resistance['resistance_below_price_share']:.1%}</b> 位于价格下方。这里的 <code>price</code> 默认指事件 bar 收盘价。</li>
        <li><b>这意味着什么：</b>当前 breakout 的 <code>support</code> / <code>resistance</code> 标签，至少在现有 v3 artifacts 里，还不能被当成两组已经干净分离的独立 alpha 事件；真正先要解决的是 side 几何语义失真，而不是直接比较哪一侧更强。</li>
      </ul>
      <div class=\"ok\"><b>本轮没声称的东西：</b>我们还没有证明修复一定只需要一个几何 gate；也还没正式重跑修复后的最小样本。所以这轮完成的是 <b>审计定位</b>，不是修复关闭。</div>
    </div>

    <div class=\"card\">
      <h2>What was found / not found / reliability</h2>
      <ul>
        <li><b>Found:</b> purged breakout raw / confirm_1 / confirm_2 三组 support-vs-resistance 仍各有 1 条逐条 exact match，说明镜像配对问题还存在，但量级已很小。</li>
        <li><b>Found:</b> 最新 raw 样本里“同一 bar 双边同时 breakout”的占比并不高；以 breakout raw 为例，配对占比是 <b>{raw_raw_pair['both_side_share']:.1%}</b>。这说明当前 blocker 不能再简单概括成“大规模双边重复记账”。</li>
        <li><b>Found:</b> breakout 几何异常依然系统性存在：<code>support_breakout_raw</code> 的 <code>support_above_price_share = {purged_geom_support['support_above_price_share']:.1%}</code>，<code>resistance_breakout_raw</code> 的 <code>resistance_below_price_share = {purged_geom_resistance['resistance_below_price_share']:.1%}</code>。</li>
        <li><b>Found:</b> pair-level geometry audit 新增了 <code>crossed_lines_share</code>、<code>close_between_lines_share</code>、<code>both_inverted_share</code>，可直接看出“support/resistance 两条线是否已经互相穿越、价格是否还夹在两线之间”。</li>
        <li><b>Not found:</b> 没看到“纯粹 summary 计算/打印 bug”的证据；因为 raw 样本里两边计数不同、均值也不完全一样，说明问题在报表之前就已经进入事件流。</li>
        <li><b>Not found:</b> 还没证明底层 pytrendline 自身把 line_side 分错；更像是 <code>visible-line sampler</code> 还缺一个可复查的 side geometry gate / audit layer。</li>
        <li><b>Reliability:</b> 对“breakout side 几何仍不干净”的判断是 <b>high</b>；对“应该怎么修”还是 <b>medium</b>，因为下一步还需要最小 sampler 修复与重跑确认。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Pair summary</h2>
      <p class=\"muted\">看三组 breakout 事件在 raw / purged 样本里，support 与 resistance 是否落在同一批 bar 上。</p>
      <h3>Raw sample</h3>
      {render_table(raw_pair_summary)}
      <h3>Purged sample</h3>
      {render_table(purged_pair_summary)}
    </div>

    <div class=\"card\">
      <h2>Geometry audit</h2>
      <p>如果一个 <code>support_breakout</code> 在事件时 support 线竟然还在价格上方，这就说明当前标签和几何位置已经脱节。这里 <code>support_above_price_share / resistance_below_price_share</code> 里的 <code>price</code> 默认指事件 bar 收盘价；同时保留更严格的 <code>support_above_high_share / resistance_below_low_share</code> 供复查。</p>
      <h3>Purged sample</h3>
      {render_table(purged_geom)}
      <h3>Raw sample</h3>
      {render_table(raw_geom)}
    </div>

    <div class=\"card\">
      <h2>Pair-level geometry audit</h2>
      <p class=\"muted\">这张表把“同一 bar 被双边 breakout 记账”的配对事件单独拿出来看，避免把单边统计和配对统计混在一起。</p>
      <ul>
        <li><code>crossed_lines_share</code>：support 线值已经高于 resistance 线值，说明两条线几何上互相穿越了。</li>
        <li><code>close_between_lines_share</code>：事件收盘价是否还位于 support / resistance 两线之间；如果很低，说明“线作为上下边界”的语义已经坏掉。</li>
        <li><code>both_inverted_share</code>：support 在线上方 + resistance 在线下方同时成立的占比，是最直观的异常几何指标。</li>
      </ul>
      <div class=\"warn\"><b>当前 purged breakout raw（paired_rows = {int(purged_pair_geom_raw['paired_rows'])}）：</b><code>crossed_lines_share = {purged_pair_geom_raw['crossed_lines_share']:.1%}</code>，<code>close_between_lines_share = {purged_pair_geom_raw['close_between_lines_share']:.1%}</code>，<code>both_inverted_share = {purged_pair_geom_raw['both_inverted_share']:.1%}</code>。</div>
      <h3>Purged sample</h3>
      {render_table(purged_pair_geom)}
      <h3>Raw sample</h3>
      {render_table(raw_pair_geom)}
    </div>

    <div class=\"card\">
      <h2>Artifacts</h2>
      <ul>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/summary.json'>summary.json</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/raw_pair_summary.csv'>raw_pair_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_pair_summary.csv'>purged_pair_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/raw_geometry_audit.csv'>raw_geometry_audit.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_geometry_audit.csv'>purged_geometry_audit.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/raw_pair_geometry_audit.csv'>raw_pair_geometry_audit.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_pair_geometry_audit.csv'>purged_pair_geometry_audit.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_breakout_raw_pairs.csv'>purged_breakout_raw_pairs.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_breakout_confirm_1_pairs.csv'>purged_breakout_confirm_1_pairs.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v3_breakout_side_audit/purged_breakout_confirm_2_pairs.csv'>purged_breakout_confirm_2_pairs.csv</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""
    ensure_dir(SITE)
    (SITE / "report.html").write_text(html, encoding="utf-8")


def main() -> None:
    ensure_dir(ART)
    ensure_dir(SITE)

    raw = load_events(SRC_ART / "event_sample_raw.csv")
    purged = load_events(SRC_ART / "event_sample_purged.csv")

    raw_pair_summary, raw_details = build_pair_outputs(raw, "raw")
    purged_pair_summary, purged_details = build_pair_outputs(purged, "purged")
    raw_geom = build_geometry_audit(raw)
    purged_geom = build_geometry_audit(purged)
    raw_pair_geom = build_pair_geometry_audit(raw_details)
    purged_pair_geom = build_pair_geometry_audit(purged_details)

    raw_pair_summary.to_csv(ART / "raw_pair_summary.csv", index=False)
    purged_pair_summary.to_csv(ART / "purged_pair_summary.csv", index=False)
    raw_geom.to_csv(ART / "raw_geometry_audit.csv", index=False)
    purged_geom.to_csv(ART / "purged_geometry_audit.csv", index=False)
    raw_pair_geom.to_csv(ART / "raw_pair_geometry_audit.csv", index=False)
    purged_pair_geom.to_csv(ART / "purged_pair_geometry_audit.csv", index=False)

    for family, detail in purged_details.items():
        detail.to_csv(ART / f"purged_{family}_pairs.csv", index=False)

    summary = build_summary_json(raw_pair_summary, purged_pair_summary, purged_geom, purged_pair_geom)
    (ART / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    build_report(raw_pair_summary, purged_pair_summary, raw_geom, purged_geom, raw_pair_geom, purged_pair_geom)
    print(f"wrote {SITE / 'report.html'}")


if __name__ == "__main__":
    main()
