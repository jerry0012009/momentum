#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "reports" / "artifacts" / "pytrendline_research"
OUT_ART = ROOT / "reports" / "artifacts" / "pytrendline_event_source"
OUT_SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_source"
OUT_RESEARCH = ROOT / "outputs" / "research"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def score_bucket(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype="object")
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))

    def label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        if v >= q3:
            return "high"
        if v >= q1:
            return "mid"
        return "low"

    return series.apply(label)


def slope_bucket(series: pd.Series) -> pd.Series:
    abs_s = series.abs()
    if abs_s.empty:
        return pd.Series(dtype="object")
    q1 = float(abs_s.quantile(0.25))
    q3 = float(abs_s.quantile(0.75))

    def label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        mag = abs(v)
        strength = "flat" if mag < q1 else "mid" if mag < q3 else "steep"
        direction = "up" if v > 0 else "down" if v < 0 else "flat"
        return f"{direction}_{strength}"

    return series.apply(label)


def load_lines(path: Path, side: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["starts_at_date", "ends_at_date", "breakout_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    df["line_side"] = side
    return df


def build_event_sample() -> tuple[pd.DataFrame, dict]:
    support = load_lines(ART / "support_trendlines.csv", "support")
    resistance = load_lines(ART / "resistance_trendlines.csv", "resistance")
    summary = json.loads((ART / "summary.json").read_text(encoding="utf-8"))

    lines = pd.concat([support, resistance], ignore_index=True)
    rep = lines[lines.get("is_best_from_duplicate_group", False).fillna(False)].copy()
    if rep.empty:
        rep = lines.copy()

    rep["source_engine"] = "pytrendline"
    rep["symbol"] = str(summary.get("ticker", "BTC-USD"))
    rep["timeframe"] = str(summary.get("interval", "5m"))
    rep["sample_key"] = f"{summary.get('ticker', 'BTC-USD')}_{summary.get('period', 'na')}_{summary.get('interval', 'na')}_window{summary.get('window_bars', 'na')}"
    rep["engine_line_id"] = rep["id"].astype(str)
    rep["line_origin_type"] = rep["is_best_from_duplicate_group"].map(lambda x: "group_best_line" if bool(x) else "candidate_line")
    rep["is_representative"] = rep["is_best_from_duplicate_group"].fillna(False).astype(bool)
    rep["event_family"] = rep["is_breakout"].map(lambda x: "breakout" if bool(x) else "touch")
    rep["event_subtype"] = rep["is_breakout"].map(lambda x: "breakout_tagged_line" if bool(x) else "line_touch_candidate")
    rep["event_timestamp"] = rep.apply(
        lambda row: row["breakout_date"] if bool(row.get("is_breakout", False)) and pd.notna(row.get("breakout_date")) else row.get("ends_at_date"),
        axis=1,
    )
    rep["confirmation_level"] = rep["is_breakout"].map(lambda x: "breakout_tagged" if bool(x) else "none")
    rep["is_provisional"] = False
    rep["is_confirmed"] = rep["is_breakout"].fillna(False).astype(bool)
    rep["bars_since_first_cross"] = 0
    rep["bars_since_touch"] = 0
    rep["line_quality_bucket"] = score_bucket(rep["score"])
    rep["slope_bucket"] = slope_bucket(rep["slope"])
    rep["num_points_bucket"] = rep["num_points"].apply(lambda x: "dense" if x >= 5 else "mid" if x >= 4 else "sparse")
    rep["score_bucket"] = score_bucket(rep["score"])

    keep = [
        "source_engine",
        "sample_key",
        "symbol",
        "timeframe",
        "engine_line_id",
        "line_side",
        "line_origin_type",
        "is_representative",
        "event_family",
        "event_subtype",
        "event_timestamp",
        "confirmation_level",
        "is_provisional",
        "is_confirmed",
        "bars_since_first_cross",
        "bars_since_touch",
        "line_quality_bucket",
        "slope_bucket",
        "num_points_bucket",
        "score_bucket",
        "num_points",
        "score",
        "slope",
        "starts_at_date",
        "ends_at_date",
        "breakout_date",
        "duplicate_group_id",
        "is_best_from_duplicate_group",
        "overall_rank",
        "rank_within_group",
    ]
    sample = rep[keep].sort_values(["event_timestamp", "score"], ascending=[True, False]).reset_index(drop=True)

    meta = {
        "ticker": summary.get("ticker"),
        "period": summary.get("period"),
        "interval": summary.get("interval"),
        "window_bars": summary.get("window_bars"),
        "all_lines": int(len(lines)),
        "representative_lines": int(len(sample)),
        "breakout_events": int((sample["event_family"] == "breakout").sum()),
        "touch_events": int((sample["event_family"] == "touch").sum()),
        "support_lines": int((sample["line_side"] == "support").sum()),
        "resistance_lines": int((sample["line_side"] == "resistance").sum()),
    }
    return sample, meta


def render_table(df: pd.DataFrame, limit: int = 20) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
    return shown.to_html(index=False, classes="tbl", border=0)


def main() -> int:
    ensure_dir(OUT_ART)
    ensure_dir(OUT_SITE)
    ensure_dir(OUT_RESEARCH)

    sample, meta = build_event_sample()
    sample_path = OUT_RESEARCH / "pytrendline_event_sample.csv"
    sample.to_csv(sample_path, index=False)
    (OUT_ART / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    counts = (
        sample.groupby(["event_family", "line_side", "line_quality_bucket"], dropna=False)
        .size()
        .reset_index(name="events")
        .sort_values(["event_family", "line_side", "events"], ascending=[True, True, False])
    )
    top_rows = sample[[
        "event_timestamp", "event_family", "line_side", "engine_line_id", "line_quality_bucket", "slope_bucket", "num_points", "score"
    ]].sort_values(["score"], ascending=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline Event Source Bridge v1</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .pill {{ display: inline-block; margin-right: 8px; margin-top: 8px; padding: 5px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    ul {{ line-height: 1.7; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>
    <div class=\"card\">
      <h1>PyTrendline Event Source Bridge v1</h1>
      <p class=\"muted\">把现有 <code>pytrendline_research</code> 产物翻译成一版最小 event-source sample，供 Mainline 后续统一 schema 与 cross-engine 比较使用。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">symbol: {escape(str(meta['ticker']))}</span>
        <span class=\"pill\">interval: {escape(str(meta['interval']))}</span>
        <span class=\"pill\">representative events: {meta['representative_lines']}</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>这页解决什么问题？</h2>
      <ul>
        <li>确认 <code>PyTrendline</code> 已经可以输出一版最小、可复用的 <code>event sample</code>，而不再只停留在 explainability 页面。</li>
        <li>先把 <code>representative line</code> / <code>breakout tag</code> / <code>score</code> / <code>slope</code> 翻译成统一 schema 可消费的字段。</li>
        <li>明确当前边界：v1 仍主要覆盖 <code>breakout</code> 与非 breakout 的 <code>touch candidate</code>，还不等于完整的 rebound / retest 事件宇宙。</li>
      </ul>
      <p><strong>核心结论：</strong>当前已经可以把 <code>PyTrendline</code> 输出成最小 event-source sample，足以进入下一步 schema 对照与 source-level comparison；但它当前仍偏 breakout / touch 语义，还不能直接宣称已覆盖完整 rebound 研究问题。</p>
      <p><strong>证据：</strong>本次基于已存在的 <code>support_trendlines.csv</code> 与 <code>resistance_trendlines.csv</code>，稳定产出 <code>{meta['representative_lines']}</code> 条 representative event rows，其中 breakout={meta['breakout_events']}、touch={meta['touch_events']}，并已写出 <code>outputs/research/pytrendline_event_sample.csv</code>。</p>
    </div>

    <div class=\"card\">
      <h2>v1 sample 概览</h2>
      <ul>
        <li>all lines: <strong>{meta['all_lines']}</strong></li>
        <li>representative lines: <strong>{meta['representative_lines']}</strong></li>
        <li>breakout events: <strong>{meta['breakout_events']}</strong></li>
        <li>touch events: <strong>{meta['touch_events']}</strong></li>
        <li>support-side rows: <strong>{meta['support_lines']}</strong></li>
        <li>resistance-side rows: <strong>{meta['resistance_lines']}</strong></li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>字段映射（最小版）</h2>
      <ul>
        <li><code>engine_line_id</code> ← 原始 <code>id</code></li>
        <li><code>line_origin_type</code> ← 是否为 <code>is_best_from_duplicate_group</code></li>
        <li><code>event_family</code> ← <code>is_breakout ? breakout : touch</code></li>
        <li><code>event_subtype</code> ← <code>breakout_tagged_line</code> / <code>line_touch_candidate</code></li>
        <li><code>event_timestamp</code> ← breakout 用 <code>breakout_date</code>，否则退回 <code>ends_at_date</code></li>
        <li><code>line_quality_bucket</code> / <code>score_bucket</code> ← 基于当前窗口内 <code>score</code> 分位数分桶</li>
        <li><code>slope_bucket</code> ← 基于当前窗口内 <code>slope</code> 大小与方向分桶</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>事件计数分布</h2>
      {render_table(counts, limit=50)}
    </div>

    <div class=\"card\">
      <h2>最高分代表事件（Top 20）</h2>
      {render_table(top_rows, limit=20)}
    </div>
  </div>
</body>
</html>
"""
    (OUT_SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] pytrendline event sample -> {sample_path}")
    print(f"[ok] pytrendline event source page -> {OUT_SITE / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
