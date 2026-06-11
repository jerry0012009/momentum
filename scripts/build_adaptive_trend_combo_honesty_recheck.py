#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from build_adaptive_trend_combo_clean_replication import (
    ART_DIR as BASE_ART_DIR,
    SITE_DIR as BASE_SITE_DIR,
    COSTS,
    PRIMARY_COST,
    ASSETS,
    choose_variant_acceptance,
    compute_regime_columns,
    ensure_dir,
    prepare_bars,
    build_event_frame,
    summarize_with_notrade,
    build_overall_summary,
    build_time_stability,
    build_cross_asset_stability,
    build_cost_trade_stability,
    render_table,
    pct,
    simulate_variant_events,
)

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = BASE_ART_DIR
SITE_DIR = BASE_SITE_DIR
REPORT_PATH = SITE_DIR / "fixed_priority_honesty_recheck.html"
SUMMARY_PATH = ART_DIR / "fixed_priority_honesty_recheck_summary.csv"
ASSET_PATH = ART_DIR / "fixed_priority_honesty_recheck_asset_summary.csv"
META_PATH = ART_DIR / "fixed_priority_honesty_recheck_meta.csv"

VARIANTS = [
    ("fixed_priority_baseline", "保留原 fixed_priority：EMA 同向 + combo + retest"),
    ("ema_plus_one", "只放松 1 条门：EMA 同向，且 combo / retest 任一成立"),
    ("ema_plus_combo", "只保留 EMA 同向 + combo"),
    ("ema_plus_retest", "只保留 EMA 同向 + retest"),
]


def build_custom_variant_rows(candidate: pd.DataFrame) -> pd.DataFrame:
    base = candidate[candidate["variant"] == "fixed_priority"].copy()
    if base.empty:
        return pd.DataFrame()

    rows = []
    for _, row in base.iterrows():
        ema_aligned = str(row.get("ema_side", "flat")) == str(row.get("side", ""))
        combo_present = pd.notna(row.get("combo_idx"))
        retest_ok = int(row.get("retest_vote", 0)) == 1
        breakout_idx = int(row["breakout_idx"])
        combo_idx = None if pd.isna(row.get("combo_idx")) else int(row.get("combo_idx"))
        retest_idx = None if pd.isna(row.get("retest_signal_idx")) else int(row.get("retest_signal_idx"))

        checks = {
            "fixed_priority_baseline": ema_aligned and combo_present and retest_ok,
            "ema_plus_one": ema_aligned and (combo_present or retest_ok),
            "ema_plus_combo": ema_aligned and combo_present,
            "ema_plus_retest": ema_aligned and retest_ok,
        }
        signal_idx_map = {
            "fixed_priority_baseline": max([x for x in [combo_idx, retest_idx] if x is not None], default=breakout_idx),
            "ema_plus_one": max([x for x in [combo_idx, retest_idx, breakout_idx] if x is not None], default=breakout_idx),
            "ema_plus_combo": max([x for x in [combo_idx, breakout_idx] if x is not None], default=breakout_idx),
            "ema_plus_retest": max([x for x in [retest_idx, breakout_idx] if x is not None], default=breakout_idx),
        }

        for variant, _desc in VARIANTS:
            accepted = bool(checks[variant])
            item = row.to_dict()
            item["variant"] = variant
            item["accepted"] = int(accepted)
            item["signal_idx"] = signal_idx_map[variant] if accepted else np.nan
            item["trade_side"] = row["side"] if accepted else "flat"
            rows.append(item)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["signal_ts"] = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    return out


def choose_verdict(summary: pd.DataFrame) -> tuple[str, list[str], str]:
    primary = summary[summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if primary.empty:
        return "hard verdict：Rank 7 这轮 cheap honesty recheck 没有生成可读结果。", ["缺少 6bps/side 总表。"], "recheck_failed"

    baseline = primary[primary["variant"] == "fixed_priority_baseline"].iloc[0]
    best = primary.sort_values(["mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"], ascending=[False, False, True]).iloc[0]

    improvement = float(baseline["mean_no_trade_ratio"]) - float(best["mean_no_trade_ratio"])
    survives_cross_asset = float(best["positive_asset_ratio"]) >= 2 / 3
    survives_cost = float(best["mean_total_return"]) > 0
    still_extreme = float(best["mean_no_trade_ratio"]) >= 0.90

    if best["variant"] != "fixed_priority_baseline" and survives_cross_asset and survives_cost and not still_extreme:
        headline = (
            f"hard verdict：Rank 7 的 cheap honesty recheck 说明，{best['variant']} 在放松 1 条门后仍保留 post-cost / cross-asset 存活，"
            "可继续保留为 P1 weak candidate。"
        )
        verdict_tag = "keep_p1"
    else:
        headline = (
            "hard verdict：Rank 7 这次 cheap honesty recheck 仍没证明“更可用的交易密度”和“成本/跨标的存活”能同时成立；"
            "因此更诚实的 desk 读法应从 `P1 weak candidate` 压回 `park / evidence pool`。"
        )
        verdict_tag = "park"

    bullets = [
        f"baseline（fixed_priority）@6bps：mean_total_return {pct(baseline['mean_total_return'])}，positive_asset_ratio {pct(baseline['positive_asset_ratio'])}，mean_no_trade_ratio {pct(baseline['mean_no_trade_ratio'])}。",
        f"本轮最不差微放松版本（{best['variant']}）@6bps：mean_total_return {pct(best['mean_total_return'])}，positive_asset_ratio {pct(best['positive_asset_ratio'])}，mean_no_trade_ratio {pct(best['mean_no_trade_ratio'])}。",
        f"相对 baseline，no_trade_ratio 仅改善 {pct(improvement)}。",
        "本轮只做 fixed_priority 邻近的 cheap honesty recheck：不换大框架、不追新 bar、不扩更多参数网格。",
    ]
    if verdict_tag == "park":
        bullets.append("结论重点不是“它完全没 edge”，而是：当前没有证据证明它能在不破坏成本/跨标的读法的前提下，把极端稀疏度压回更可部署的范围。")
    else:
        bullets.append("因此这条线仍只配保留在 P1：若后续继续认领，仍不得再无限续命。")
    return headline, bullets, verdict_tag


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    asset_summaries = []
    all_trades = []

    for asset, symbol in ASSETS.items():
        bars = compute_regime_columns(prepare_bars(asset, symbol))
        events = build_event_frame(asset, symbol, bars)
        candidate = choose_variant_acceptance(bars, events)
        custom = build_custom_variant_rows(candidate)
        if custom.empty:
            continue
        for variant, _desc in VARIANTS:
            variant_candidate = custom[custom["variant"] == variant].copy()
            variant_events = variant_candidate[variant_candidate["accepted"] == 1].copy()
            if not variant_events.empty:
                variant_events["side"] = variant_events["trade_side"]
            for cost in COSTS:
                trades, nav = simulate_variant_events(bars, variant_events, variant, cost_bps_per_side=cost)
                if not trades.empty:
                    trades["cost_bps_per_side"] = float(cost)
                    trades["variant"] = variant
                    all_trades.append(trades)
                summary = summarize_with_notrade(trades, nav, variant_candidate, asset, variant, cost)
                asset_summaries.append(summary)

    asset_df = pd.concat(asset_summaries, ignore_index=True) if asset_summaries else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    summary = build_overall_summary(asset_df)
    summary.to_csv(SUMMARY_PATH, index=False)
    asset_df.to_csv(ASSET_PATH, index=False)

    primary = summary[summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    best_variant = str(primary.sort_values(["mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"], ascending=[False, False, True]).iloc[0]["variant"]) if not primary.empty else "fixed_priority_baseline"
    time_stability = build_time_stability(trades_df[trades_df["cost_bps_per_side"] == PRIMARY_COST].copy() if not trades_df.empty else trades_df, best_variant)
    cross_asset_stability = build_cross_asset_stability(asset_df, best_variant)
    cost_trade_stability = build_cost_trade_stability(summary, best_variant)
    headline, bullets, verdict_tag = choose_verdict(summary)

    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank7_adaptive_trend_combo_fixed_priority_honesty_recheck",
            "verdict_tag": verdict_tag,
            "best_variant_6bps": best_variant,
            "note": "Cheap honesty recheck around fixed_priority only; answers whether one relaxed gate can reduce extreme no_trade_ratio without breaking cost/cross-asset read.",
        }
    ])
    meta_df.to_csv(META_PATH, index=False)

    summary_table = render_table(
        primary[["variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "mean_trades", "mean_no_trade_ratio"]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1},
    ) if not primary.empty else "<p>无结果</p>"

    asset_table = render_table(
        asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST][["asset", "variant", "trades", "total_return", "win_rate", "no_trade_ratio"]],
        percent_cols={"total_return", "win_rate", "no_trade_ratio"},
        digits_cols={"trades": 0},
    ) if not asset_df.empty else "<p>无结果</p>"

    time_table = render_table(time_stability, percent_cols=set()) if not time_stability.empty else "<p>无时间稳定性表。</p>"
    cross_table = render_table(cross_asset_stability, percent_cols=set()) if not cross_asset_stability.empty else "<p>无跨标的稳定性表。</p>"
    cost_table = render_table(cost_trade_stability, percent_cols=set()) if not cost_trade_stability.empty else "<p>无成本/交易数稳定性表。</p>"
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    variants_html = "".join(f"<li><code>{escape(k)}</code>：{escape(v)}</li>" for k, v in VARIANTS)

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 7 · fixed-priority honesty recheck</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Rank 7 · adaptive trend combo · fixed-priority cheap honesty recheck</h1>
  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>
  <div class="card">
    <h2>本轮只检查什么</h2>
    <p>目标不是重开 Rank 7 大研究，而是只回答一个问题：<b>围绕原本最不差的 <code>fixed_priority</code>，若只放松一条门，能不能把极端 <code>no_trade_ratio</code> 压回更可用范围，而且不把成本 / 跨标的存活炸掉？</b></p>
    <ul>{variants_html}</ul>
  </div>
  <div class="card">
    <h2>6bps/side summary</h2>
    {summary_table}
    <p>artifact：<code>{escape(str(SUMMARY_PATH.relative_to(ROOT)))}</code></p>
  </div>
  <div class="card">
    <h2>per-asset summary（6bps/side）</h2>
    {asset_table}
  </div>
  <div class="card">
    <h2>最不差版本的 Light Stability quick read</h2>
    <h3>时间稳定性</h3>
    {time_table}
    <h3>跨标的稳定性</h3>
    {cross_table}
    <h3>成本 / 交易数稳定性</h3>
    {cost_table}
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")

    print("[ok] rank7 fixed-priority honesty recheck generated")
    print("[artifact]", SUMMARY_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
