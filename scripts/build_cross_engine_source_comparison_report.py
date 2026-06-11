#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PYI_LADDER = ROOT / "reports" / "artifacts" / "trendline_confirmation_ladder"
PYI_SLOPE = ROOT / "reports" / "artifacts" / "trendline_event_slope_audit"
PYT_VAL = ROOT / "reports" / "artifacts" / "pytrendline_event_validation"
OUT_SITE = ROOT / "reports" / "site" / "factors" / "cross_engine_source_comparison"
OUT_ART = ROOT / "reports" / "artifacts" / "cross_engine_source_comparison"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return "—"
    return f"{x * 100:.2f}%"


def render_table(df: pd.DataFrame, pct_cols: set[str] | None = None) -> str:
    if df.empty:
        return "<p><em>empty</em></p>"
    shown = df.copy()
    pct_cols = pct_cols or set()
    for col in shown.columns:
        if col in pct_cols:
            shown[col] = shown[col].apply(fmt_pct)
    return shown.to_html(index=False, classes="tbl", border=0)


def main() -> int:
    ensure_dir(OUT_SITE)
    ensure_dir(OUT_ART)

    pyi_summary = json.loads((PYI_LADDER / "summary.json").read_text(encoding="utf-8"))
    sample_meta = pd.read_csv(PYI_LADDER / "sample_meta.csv")
    breakout = pd.read_csv(PYI_LADDER / "breakout_ladder_summary.csv")
    rebound = pd.read_csv(PYI_LADDER / "rebound_retained_subset_summary.csv")
    slope_summary = json.loads((PYI_SLOPE / "summary.json").read_text(encoding="utf-8"))

    pyt_summary = json.loads((PYT_VAL / "summary.json").read_text(encoding="utf-8"))
    pyt_overall = pd.read_csv(PYT_VAL / "overall_by_family_horizon.csv")

    pyi_breakout_2y = breakout[(breakout["sample_key"] == "60m_730d") & (breakout["display_label"] == "breakout hold = 3")].iloc[0]
    pyi_rebound_2y = rebound[(rebound["sample_key"] == "60m_730d") & (rebound["display_label"] == "rebound inside = 0") & (rebound["subset_group"] == "retained_union")].iloc[0]
    pyt_breakout_h6 = pyt_overall[(pyt_overall["event_family"] == "breakout") & (pyt_overall["horizon_bars"] == 6)].iloc[0]
    pyt_breakout_h12 = pyt_overall[(pyt_overall["event_family"] == "breakout") & (pyt_overall["horizon_bars"] == 12)].iloc[0]

    comparison = pd.DataFrame([
        {
            "engine": "PyIndicators",
            "current_role": "baseline event source / 对照组",
            "sample_scope": "8 symbols · 30m/60m · 60d/365d/730d",
            "event_coverage": "breakout + rebound + confirmation ladders + slope audit",
            "current_best_signal": "rebound retained subsets（inside=0/1）",
            "current_weak_point": "breakout overall 仍偏弱",
            "current_decision": "部分 continue（rebound）；breakout 偏 park",
        },
        {
            "engine": "PyTrendline",
            "current_role": "clean explainability source / 新 event source 候选",
            "sample_scope": "BTC-USD · 5m · 10d · window96",
            "event_coverage": "breakout + touch candidate（bridge/validation v1）",
            "current_best_signal": "当前无强阳性；touch 样本太小",
            "current_weak_point": "coverage 窄，当前 breakout forward return 偏弱",
            "current_decision": "unknown / need more validation",
        },
    ])

    key_metrics = pd.DataFrame([
        {
            "engine": "PyIndicators breakout (2Y)",
            "anchor_metric": "breakout hold = 3",
            "sample_count_or_trades": int(pyi_breakout_2y["total_trades"]),
            "up_or_positive_ratio": float(pyi_breakout_2y["positive_asset_ratio"]),
            "mean_return": float(pyi_breakout_2y["mean_total_return"]),
            "note": "2Y / multi-asset / strategy-style summary",
        },
        {
            "engine": "PyIndicators rebound retained (2Y)",
            "anchor_metric": "rebound inside = 0 / retained_union",
            "sample_count_or_trades": int(pyi_rebound_2y["total_trades"]),
            "up_or_positive_ratio": float(pyi_rebound_2y["positive_asset_ratio"]),
            "mean_return": float(pyi_rebound_2y["mean_total_return"]),
            "note": "当前 PyIndicators 侧最值得继续的 retained subset",
        },
        {
            "engine": "PyTrendline breakout v1",
            "anchor_metric": "+6 bars forward return",
            "sample_count_or_trades": int(pyt_breakout_h6["sample_count"]),
            "up_or_positive_ratio": float(pyt_breakout_h6["up_ratio"]),
            "mean_return": float(pyt_breakout_h6["mean_forward_return"]),
            "note": "单窗口 observation-style summary",
        },
        {
            "engine": "PyTrendline breakout v1",
            "anchor_metric": "+12 bars forward return",
            "sample_count_or_trades": int(pyt_breakout_h12["sample_count"]),
            "up_or_positive_ratio": float(pyt_breakout_h12["up_ratio"]),
            "mean_return": float(pyt_breakout_h12["mean_forward_return"]),
            "note": "单窗口 observation-style summary",
        },
    ])

    meta = {
        "pyindicators_symbols": int(sample_meta["symbols"].max()),
        "pyindicators_total_rows": int(sample_meta["rows"].sum()),
        "pyindicators_total_trades": int(pyi_summary["total_trades"]),
        "pyindicators_total_symbol_slope_cells": int(slope_summary["total_symbol_slope_cells"]),
        "pytrendline_total_events": int(pyt_summary["total_events"]),
        "pytrendline_matched_events": int(pyt_summary["matched_events"]),
        "pytrendline_horizons": pyt_summary["horizons"],
    }
    (OUT_ART / "summary.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    comparison.to_csv(OUT_ART / "engine_scorecard.csv", index=False)
    key_metrics.to_csv(OUT_ART / "key_metrics.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Cross-Engine Source Comparison v1</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; padding: 28px 18px 48px; }}
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
      <h1>Cross-Engine Source Comparison v1</h1>
      <p class=\"muted\">把当前 `PyIndicators` 与 `PyTrendline` 的 source maturity、覆盖范围、已有证据与下一步缺口放到同一页上比较。注意：这是一版 source-level / evidence-level 对照，不是严格 same-sample 的 apples-to-apples 策略赛马。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">PyIndicators: 8 symbols · multi-sample</span>
        <span class=\"pill\">PyTrendline: BTC-USD · 10d / 5m</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>这页回答什么问题？</h2>
      <ul>
        <li>当前两条 source 线分别成熟到什么程度？</li>
        <li>它们各自最强、最弱的地方是什么？</li>
        <li>下一步应该继续补 validation、补 bridge，还是已经足够进入 signal / strategy？</li>
      </ul>
      <p><strong>核心结论：</strong>`PyIndicators` 目前仍然是覆盖更广、证据更丰富的 baseline source，但它的 breakout 线整体偏弱，只剩 retained rebound subsets 更像可继续候选；`PyTrendline` 的定义更干净、explainability 更强，也已经进入 observation 层，但当前 coverage 仍窄，且 breakout validation v1 依然偏弱。</p>
      <p><strong>证据：</strong>`PyIndicators` 已覆盖 8 个资产、多档样本窗口，并有 45574 笔 ladder trades 与 1123 个 symbol-slope cells 的证据地基；而 `PyTrendline` 当前 validation v1 只在 `BTC-USD / 10d / 5m` 上对 215 条事件做了 `+1/+3/+6/+12 bars` 观察，其中 breakout 在 `+6/+12` bars 的 mean forward return 约为 `-0.04% / -0.08%`，说明它已进入验证层，但还不能直接宣布强阳性。</p>
    </div>

    <div class=\"card\">
      <h2>Engine scorecard</h2>
      {render_table(comparison)}
    </div>

    <div class=\"card\">
      <h2>Key anchor metrics</h2>
      {render_table(key_metrics, pct_cols={'up_or_positive_ratio', 'mean_return'})}
    </div>

    <div class=\"card\">
      <h2>当前最合理的阅读结论</h2>
      <ul>
        <li><b>如果你的问题是“哪个 source 现在证据更多？”</b>：答案还是 `PyIndicators`，因为它已经跑过 multi-asset / multi-sample 的 slope audit、confirmation ladder 与 retained subset 分析。</li>
        <li><b>如果你的问题是“哪个 source 定义更干净、未来更适合 clean event research？”</b>：当前更像 `PyTrendline`，因为它的 definition / explainability / source bridge 更清晰。</li>
        <li><b>如果你的问题是“现在能不能直接宣布 PyTrendline 胜出？”</b>：还不能。因为它当前只是一版单窗口 observation，而且 breakout 结果暂时偏弱。</li>
        <li><b>如果你的问题是“下一步最该干嘛？”</b>：先做更可比的 source-level 对照，而不是急着上 signal / strategy。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>下一步建议</h2>
      <ul>
        <li>补 `PyTrendline bridge v2`：至少把 `representative only vs all valid` 分开。</li>
        <li>继续补 `rebound / retest` 方向的 PyTrendline event 语义，不要长期停在 breakout-only。</li>
        <li>之后再做第二轮更严格的对照：同样问题、尽量同样窗口、尽量同样 bucket，比较 `PyIndicators source vs PyTrendline source`。</li>
      </ul>
    </div>
  </div>
</body>
</html>
"""
    (OUT_SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] comparison site -> {OUT_SITE / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
