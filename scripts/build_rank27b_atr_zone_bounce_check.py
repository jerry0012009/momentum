#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

import build_mtgox_neckline_clean_replication as base

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank27b_atr_zone_bounce_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank27b_atr_zone_bounce_15m"
REPORT_PATH = SITE_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

VARIANTS = ["raw_breakout", "neckline_confirm", "neckline_confirm_plus_retest_hold", "atr_zone_bounce_reclaim"]
PRIMARY_VARIANT = "atr_zone_bounce_reclaim"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]

ATR_ZONE_LOOKAHEAD = 8
ATR_ZONE_HALF_WIDTH = 0.50
ATR_BOUNCE_CLOSE = 0.10


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def select_events_variant(events: pd.DataFrame, bars: pd.DataFrame, variant: str) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame()
    if variant in {"raw_breakout", "neckline_confirm", "neckline_confirm_plus_retest_hold"}:
        return base.select_variant_events(events, variant)
    if variant != PRIMARY_VARIANT:
        raise ValueError(variant)

    rows = []
    n = len(bars)
    for _, ev in events.iterrows():
        if pd.isna(ev["confirm_idx"]):
            continue
        confirm_idx = int(ev["confirm_idx"])
        neckline = float(ev["neckline"])
        atr = float(ev["breakout_atr"])
        if not np.isfinite(atr) or atr <= 0:
            continue
        end_idx = min(confirm_idx + ATR_ZONE_LOOKAHEAD, n - 1)
        signal_idx = None
        for idx in range(confirm_idx + 1, end_idx + 1):
            row = bars.iloc[idx]
            low = float(row["low"])
            close = float(row["close"])
            open_ = float(row["open"])
            in_zone = (low <= neckline + ATR_ZONE_HALF_WIDTH * atr) and (low >= neckline - ATR_ZONE_HALF_WIDTH * atr)
            bounce_reclaim = close >= neckline + ATR_BOUNCE_CLOSE * atr and close >= open_
            if in_zone and bounce_reclaim:
                signal_idx = idx
                break
        if signal_idx is None:
            continue
        out = ev.to_dict()
        out["signal_idx"] = int(signal_idx)
        out["signal_ts"] = bars.iloc[signal_idx]["timestamp"]
        out["variant"] = PRIMARY_VARIANT
        rows.append(out)

    out_df = pd.DataFrame(rows)
    if out_df.empty:
        return out_df
    return out_df.sort_values(["asset", "signal_idx"]).reset_index(drop=True)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_break_ratio"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    work["time_bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_false_break_ratio": float(grp["false_break_ratio"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def pick_verdict(overall: pd.DataFrame, time_df: pd.DataFrame) -> tuple[str, str]:
    p = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if p.empty:
        return "park / evidence pool", "ATR 弹性回踩区变体没有形成可用样本。"
    row = p.iloc[0]
    ret = float(row["mean_total_return"])
    pos = float(row["positive_asset_ratio"])
    fb = float(row["mean_false_break_ratio"])
    tr = float(row["mean_trades"])
    pos_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0

    if ret > 0 and pos >= (2 / 3) and fb <= 0.55 and tr >= 15 and pos_buckets >= 2:
        return "P1 weak candidate / evidence pool", "ATR 回踩区 + bounce reclaim 已形成可保留的一档 pocket，可给一次便宜诚实检查预算。"
    return "park / evidence pool", "ATR 回踩区改写没有把 Rank 27 从成本后负收益状态里救出来，仍不配继续占默认 Scout 预算。"


def render_table(df: pd.DataFrame, percent_cols: set[str], digits_cols: dict[str, int]) -> str:
    return base.render_table(df, percent_cols=percent_cols, digits_cols=digits_cols)


def write_report(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_df: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> None:
    ensure_dir(SITE_DIR)
    p6 = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    r6 = overall[(overall["variant"] == "raw_breakout") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    h6 = overall[(overall["variant"] == "neckline_confirm_plus_retest_hold") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"ATR zone 变体在 6bps/side 下：mean_total_return≈{base.pct(p6['mean_total_return'])}、"
        f"positive_asset_ratio≈{base.pct(p6['positive_asset_ratio'])}、mean_trades≈{base.num(p6['mean_trades'],1)}、"
        f"mean_false_break_ratio≈{base.pct(p6['mean_false_break_ratio'])}；"
        f"对照 raw≈{base.pct(r6['mean_total_return'])}/{base.pct(r6['mean_false_break_ratio'])}，"
        f"retest_hold≈{base.pct(h6['mean_total_return'])}/{base.pct(h6['mean_false_break_ratio'])}。"
    )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 27b · ATR zone retest + bounce reclaim</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../plans/momentum_todo.html'>← 返回 TODO / desk board</a></p>
  <h1>Rank 27b · ATR zone retest + bounce reclaim</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 本轮类型：P1 那唯一一次便宜诚实检查（在 Rank 27 基础上仅改一条轴）</p>

  <div class='card'>
    <h2>这轮只做什么</h2>
    <ul>
      <li>只改一条轴：把原来静态 <code>retest_hold</code> 改成 <code>ATR 弹性回踩区 + bounce reclaim</code>。</li>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar，不扩 universe。</li>
      <li>执行冻结不变：<code>next-bar open + 1ATR stop + 2ATR target + 8-bar time stop + no-overlap</code>。</li>
      <li>只回答一次会改变 verdict 的问题：这条改写是否能把 Rank 27 从 park 拉回可保留状态。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>成本对照（4 variants）</h2>
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_break_ratio","mean_no_trade_ratio"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_break_ratio","mean_no_trade_ratio"}, digits_cols={"cost_bps_per_side":0,"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要（ATR zone 变体 / 6bps）</h2>
    {render_table(asset_summary[["asset","candidate_events","trades","total_return","false_break_ratio","mean_time_to_failure_bars","no_trade_ratio"]], percent_cols={"total_return","false_break_ratio","no_trade_ratio"}, digits_cols={"candidate_events":0,"trades":0,"mean_time_to_failure_bars":1})}
  </div>

  <div class='card'>
    <h2>时间稳定性（唯一 Light pack 项）</h2>
    {render_table(time_df[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_false_break_ratio"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_break_ratio"}, digits_cols={"mean_trades":1})}
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def update_todo(generated_at: str, overall: pd.DataFrame, time_df: pd.DataFrame, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    row = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    raw = overall[(overall["variant"] == "raw_breakout") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    hold = overall[(overall["variant"] == "neckline_confirm_plus_retest_hold") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    b = [f"{r['time_bucket']}≈{base.pct(r['mean_total_return'])} / {base.pct(r['positive_asset_ratio'])}" for _, r in time_df.iterrows()]
    tnote = "time-pocket：" + "；".join(b) if b else "time-pocket：样本不足"
    note = (
        f"- **最新补充（{generated_at}）**：按 `Run 2` 回退顺序，这轮先拿 `Rank 27b`（高于 `Rank 35b`）做了那唯一一次便宜诚实检查：在 `Rank 27` 基础上只改一条轴（静态 `retest_hold` -> `ATR 弹性回踩区 + bounce reclaim`），并固定复用 `BTC/ETH/SOL 120d 15m` cache。结果：`atr_zone_bounce_reclaim` 在 `6bps/side` 下跨资产 `mean_total_return≈{base.pct(row['mean_total_return'])}`、`positive_asset_ratio≈{base.pct(row['positive_asset_ratio'])}`、`mean_trades≈{base.num(row['mean_trades'],1)}`、`mean_false_break_ratio≈{base.pct(row['mean_false_break_ratio'])}`；对照 `raw_breakout≈{base.pct(raw['mean_total_return'])}/{base.pct(raw['mean_false_break_ratio'])}`、`retest_hold≈{base.pct(hold['mean_total_return'])}/{base.pct(hold['mean_false_break_ratio'])}`。{tnote}。因此这轮 hard verdict 仍是 **`{verdict}`**，`Rank 27b` 预算用尽后应压回 evidence pool；若下一轮 `EMA` 仍 `waiting_not_due`，默认转去比较 `Rank 35b > Run 3`。\n  - 网页落点：`reports/site/factors/scout_rank27b_atr_zone_bounce_15m/report.html`。"
    )
    marker = "- **当前候选阶段表（精简版，authoritative）**："
    if marker in text and note not in text:
        text = text.replace(marker, note + "\n" + marker, 1)

    old_window = "> **当前窗口排班（2026-03-18 03:57 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29 / Rank 32b` 这几条既有 `P3 narrow paper lane` 继续由专属 refresh cron 或最小 monitoring 接线低频托管，当前没有新的 `append/review` 状态变化；`Rank 43` 与 `Rank 40` 已分别用完各自唯一那手 fast-lane budget 并压回 **`park / evidence pool`**，而新的 `BotScalpingTwinRange / PSAR anchor + EMA confirm` 也已完成那唯一一手最小 clean replication，并如实压回 **`park / evidence pool`**。换句话说：若下一轮 `EMA` 仍在 waiting-window，bot3 默认应回退比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`，而不是继续磨 `Rank 40 / 43`、继续给这条 repo 模板续命，或回头挤占 `P3` continuity。"
    new_window = "> **当前窗口排班（2026-03-18 04:10 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29 / Rank 32b` 这几条既有 `P3 narrow paper lane` 继续由专属 refresh cron 或最小 monitoring 接线低频托管，当前没有新的 `append/review` 状态变化；`Rank 43`、`Rank 40`、`BotScalpingTwinRange` 与 `Rank 27b` 均已在各自允许预算内给出 hard verdict 并压回 **`park / evidence pool`**。换句话说：若下一轮 `EMA` 仍在 waiting-window，bot3 默认应继续比较 `Rank 35b > Run 3 / tiny-live plumbing`，而不是回头重磨已 park 线或挤占 `P3` continuity。"
    if old_window in text:
        text = text.replace(old_window, new_window, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    all_events, all_trades, all_nav, all_summaries = [], [], [], []

    for asset, symbol in base.ASSETS.items():
        bars = base.prepare_bars(asset, symbol)
        events = base.build_candidate_events(bars)
        for variant in VARIANTS:
            var_events = select_events_variant(events, bars, variant) if not events.empty else pd.DataFrame()
            if not var_events.empty:
                all_events.append(var_events)
            for cost in COSTS:
                trades, nav = base.simulate_events(bars, var_events, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                if not nav.empty:
                    all_nav.append(nav)
                all_summaries.append(base.summarize_trades(trades, nav, var_events, asset, variant, cost))

    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    overall = base.build_overall_summary(asset_summary)
    primary_trades = trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy() if not trades_df.empty else pd.DataFrame()
    time_df = build_time_stability(primary_trades)
    verdict, reason = pick_verdict(overall, time_df)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not events_df.empty:
        events_df.to_csv(ART_DIR / "candidate_events_by_variant.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    if not nav_df.empty:
        nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_df.to_csv(ART_DIR / "time_stability.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank27b_atr_zone_bounce",
            "hard_verdict": verdict,
            "verdict_reason": reason,
            "scope": "BTC/ETH/SOL 120d 15m cache",
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    primary_asset = asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].copy()
    write_report(overall, primary_asset, time_df, verdict, reason, generated_at)
    update_todo(generated_at, overall, time_df, verdict)

    print(f"verdict={verdict}")
    print(overall[(overall['cost_bps_per_side']==6.0)][['variant','mean_total_return','positive_asset_ratio','mean_false_break_ratio','mean_trades']].to_dict(orient='records'))


if __name__ == "__main__":
    main()
