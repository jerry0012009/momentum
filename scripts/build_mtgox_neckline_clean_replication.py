#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from build_volume_supportflip_higherlow_first_verdict import ASSETS, ensure_dir, pct, num, render_table

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_mtgox_neckline_confirmation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_mtgox_neckline_confirmation_15m"
REPORT_PATH = SITE_DIR / "report.html"

SMOOTH_SPAN = 9
CONFIRM_RIGHT = 2
ATR_PERIOD = 14
NECKLINE_ATR_BAND = 0.35
BREAK_BUFFER = 0.05
CONFIRM_WINDOW = 12
CONFIRM_MIN_CLOSES = 2
RETEST_LOOKAHEAD = 3
RETEST_TOUCH_ATR = 0.05
RETEST_HOLD_ATR = 0.03
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
FAILURE_LOOKAHEAD = 12
FAILURE_BUFFER_ATR = 0.00
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
VARIANTS = ["raw_breakout", "neckline_confirm", "neckline_confirm_plus_retest_hold"]
PRIMARY_VARIANT = "neckline_confirm"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def build_confirmed_pivots(bars: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    highs: list[dict] = []
    lows: list[dict] = []
    smooth = bars["smooth"].tolist()
    raw_high = bars["high"].tolist()
    raw_low = bars["low"].tolist()
    atr = bars["atr"].tolist()
    n = len(bars)
    for idx in range(2, n - CONFIRM_RIGHT):
        center = smooth[idx]
        if not math.isfinite(center):
            continue
        left = smooth[idx - 2 : idx]
        right = smooth[idx + 1 : idx + 1 + CONFIRM_RIGHT]
        if any(not math.isfinite(x) for x in left + right):
            continue
        confirm_idx = idx + CONFIRM_RIGHT
        atr_here = atr[confirm_idx] if confirm_idx < n else float("nan")
        if center >= max(left) and center > max(right):
            highs.append(
                {
                    "pivot_idx": idx,
                    "confirm_idx": confirm_idx,
                    "price": float(raw_high[idx]),
                    "atr": float(atr_here),
                }
            )
        if center <= min(left) and center < min(right):
            lows.append(
                {
                    "pivot_idx": idx,
                    "confirm_idx": confirm_idx,
                    "price": float(raw_low[idx]),
                    "atr": float(atr_here),
                }
            )
    return highs, lows


def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["hlc3"] = (bars["high"] + bars["low"] + bars["close"]) / 3.0
    bars["smooth"] = ema(bars["hlc3"], SMOOTH_SPAN)
    bars["atr"] = compute_atr(bars)
    bars["ema20"] = ema(bars["close"], 20)
    bars["ema50"] = ema(bars["close"], 50)
    bars["ema_long"] = bars["ema20"] > bars["ema50"]
    return bars


def build_candidate_events(bars: pd.DataFrame) -> pd.DataFrame:
    high_pivots, low_pivots = build_confirmed_pivots(bars)
    rows: list[dict] = []
    n = len(bars)
    for i in range(1, len(low_pivots)):
        low1 = low_pivots[i - 1]
        low2 = low_pivots[i]
        if int(low2["confirm_idx"]) <= int(low1["confirm_idx"]):
            continue
        atr_ref = float(low2.get("atr", np.nan))
        if not math.isfinite(atr_ref) or atr_ref <= 0:
            continue
        if abs(float(low2["price"]) - float(low1["price"])) > NECKLINE_ATR_BAND * atr_ref:
            continue
        between_highs = [
            p for p in high_pivots if int(low1["pivot_idx"]) < int(p["pivot_idx"]) < int(low2["pivot_idx"])
        ]
        if not between_highs:
            continue
        neckline_pivot = max(between_highs, key=lambda p: float(p["price"]))
        neckline = float(neckline_pivot["price"])
        pattern_ready_idx = max(int(low2["confirm_idx"]), int(neckline_pivot["confirm_idx"]))
        if pattern_ready_idx >= n - 1:
            continue
        breakout_idx = None
        for idx in range(pattern_ready_idx, n - 1):
            row = bars.iloc[idx]
            atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
            if not math.isfinite(atr) or atr <= 0:
                continue
            if float(row["close"]) > neckline + BREAK_BUFFER * atr:
                breakout_idx = idx
                break
        if breakout_idx is None:
            continue
        confirm_hits = []
        end_idx = min(breakout_idx + CONFIRM_WINDOW, n - 1)
        for idx in range(breakout_idx, end_idx + 1):
            row = bars.iloc[idx]
            atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
            if math.isfinite(atr) and atr > 0 and float(row["close"]) > neckline + BREAK_BUFFER * atr:
                confirm_hits.append(idx)
        confirm_idx = confirm_hits[CONFIRM_MIN_CLOSES - 1] if len(confirm_hits) >= CONFIRM_MIN_CLOSES else None
        retest_idx = None
        if confirm_idx is not None:
            retest_end = min(confirm_idx + RETEST_LOOKAHEAD, n - 1)
            for idx in range(confirm_idx + 1, retest_end + 1):
                row = bars.iloc[idx]
                atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
                if not math.isfinite(atr) or atr <= 0:
                    continue
                if float(row["low"]) <= neckline + RETEST_TOUCH_ATR * atr and float(row["close"]) >= neckline + RETEST_HOLD_ATR * atr:
                    retest_idx = idx
                    break
        rows.append(
            {
                "asset": str(bars.iloc[0]["asset"]),
                "pattern_low1_idx": int(low1["pivot_idx"]),
                "pattern_low2_idx": int(low2["pivot_idx"]),
                "low1_price": float(low1["price"]),
                "low2_price": float(low2["price"]),
                "neckline": neckline,
                "neckline_pivot_idx": int(neckline_pivot["pivot_idx"]),
                "pattern_ready_idx": int(pattern_ready_idx),
                "breakout_idx": int(breakout_idx),
                "confirm_idx": int(confirm_idx) if confirm_idx is not None else np.nan,
                "retest_idx": int(retest_idx) if retest_idx is not None else np.nan,
                "breakout_ts": bars.iloc[breakout_idx]["timestamp"],
                "confirm_ts": bars.iloc[confirm_idx]["timestamp"] if confirm_idx is not None else pd.NaT,
                "retest_ts": bars.iloc[retest_idx]["timestamp"] if retest_idx is not None else pd.NaT,
                "breakout_atr": float(bars.iloc[breakout_idx]["atr"]),
                "confirm_hits": len(confirm_hits),
            }
        )
    events = pd.DataFrame(rows)
    if events.empty:
        return events
    events = events.sort_values(["asset", "breakout_idx"]).reset_index(drop=True)
    return events


def select_variant_events(events: pd.DataFrame, variant: str) -> pd.DataFrame:
    out = events.copy()
    if variant == "raw_breakout":
        out["signal_idx"] = out["breakout_idx"]
        out["signal_ts"] = out["breakout_ts"]
    elif variant == "neckline_confirm":
        out = out[out["confirm_idx"].notna()].copy()
        out["signal_idx"] = out["confirm_idx"].astype(int)
        out["signal_ts"] = out["confirm_ts"]
    elif variant == "neckline_confirm_plus_retest_hold":
        out = out[out["retest_idx"].notna()].copy()
        out["signal_idx"] = out["retest_idx"].astype(int)
        out["signal_ts"] = out["retest_ts"]
    else:
        raise ValueError(variant)
    out["variant"] = variant
    return out.sort_values(["asset", "signal_idx"]).reset_index(drop=True)


def simulate_events(bars: pd.DataFrame, events: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if events.empty:
        nav = pd.DataFrame(
            [{
                "asset": str(bars.iloc[0]["asset"]),
                "variant": variant,
                "timestamp": bars.iloc[0]["timestamp"],
                "nav": 1.0,
                "cost_bps_per_side": float(cost_bps_per_side),
            }]
        )
        return pd.DataFrame(), nav

    cost_rate = float(cost_bps_per_side) / 10000.0
    trades = []
    nav = 1.0
    nav_rows = [{"asset": str(bars.iloc[0]["asset"]), "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)}]
    last_exit_idx = -1

    for _, event in events.iterrows():
        signal_idx = int(event["signal_idx"])
        if signal_idx <= last_exit_idx:
            continue
        entry_idx = signal_idx + 1
        if entry_idx >= len(bars):
            continue
        entry_price = float(bars.iloc[entry_idx]["open"])
        atr = float(event["breakout_atr"])
        neckline = float(event["neckline"])
        if not math.isfinite(entry_price) or entry_price <= 0 or not math.isfinite(atr) or atr <= 0:
            continue
        stop_price = entry_price - STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, len(bars) - 1)
        exit_idx = None
        exit_price = None
        exit_reason = None
        first_failure_bars = np.nan
        failure_flag = 0
        failure_end = min(signal_idx + FAILURE_LOOKAHEAD, len(bars) - 1)
        for idx in range(signal_idx + 1, failure_end + 1):
            close = float(bars.iloc[idx]["close"])
            if close <= neckline + FAILURE_BUFFER_ATR * atr:
                failure_flag = 1
                first_failure_bars = float(idx - signal_idx)
                break
        for idx in range(entry_idx, last_bar_idx + 1):
            probe = bars.iloc[idx]
            low = float(probe["low"])
            high = float(probe["high"])
            if low <= stop_price:
                exit_idx = idx
                exit_price = stop_price
                exit_reason = "atr_stop"
                break
            if high >= target_price:
                exit_idx = idx
                exit_price = target_price
                exit_reason = "atr_target"
                break
        if exit_idx is None:
            exit_idx = last_bar_idx
            exit_price = float(bars.iloc[exit_idx]["close"])
            exit_reason = "time_stop"
        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        trades.append(
            {
                "asset": str(bars.iloc[0]["asset"]),
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "signal_ts": pd.to_datetime(event["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": bars.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": bars.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "neckline": neckline,
                "confirm_hits": int(event["confirm_hits"]),
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
                "false_break_ratio": float(failure_flag),
                "time_to_failure_bars": first_failure_bars,
            }
        )
        nav_rows.append({"asset": str(bars.iloc[0]["asset"]), "variant": variant, "timestamp": bars.iloc[exit_idx]["timestamp"], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)})
        last_exit_idx = exit_idx
    return pd.DataFrame(trades), pd.DataFrame(nav_rows)


def summarize_trades(trades: pd.DataFrame, nav: pd.DataFrame, candidate_events: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    total_events = int(len(candidate_events))
    accepted_events = int(len(trades))
    no_trade_ratio = 1.0 - (accepted_events / total_events) if total_events else np.nan
    if trades.empty:
        return pd.DataFrame(
            [{
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "candidate_events": total_events,
                "trades": 0,
                "win_rate": np.nan,
                "avg_net_ret": np.nan,
                "median_net_ret": np.nan,
                "total_return": 0.0,
                "max_drawdown": 0.0,
                "avg_hold_bars": np.nan,
                "no_trade_ratio": no_trade_ratio,
                "false_break_ratio": np.nan,
                "mean_time_to_failure_bars": np.nan,
            }]
        )
    running_peak = nav["nav"].cummax() if not nav.empty else pd.Series(dtype=float)
    drawdown = nav["nav"] / running_peak - 1.0 if not nav.empty else pd.Series(dtype=float)
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    return pd.DataFrame(
        [{
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "candidate_events": total_events,
            "trades": int(len(trades)),
            "win_rate": float(trades["win"].mean()),
            "avg_net_ret": float(trades["net_ret"].mean()),
            "median_net_ret": float(trades["net_ret"].median()),
            "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
            "max_drawdown": max_dd,
            "avg_hold_bars": float(trades["hold_bars"].mean()),
            "no_trade_ratio": no_trade_ratio,
            "false_break_ratio": float(trades["false_break_ratio"].mean()) if trades["false_break_ratio"].notna().any() else np.nan,
            "mean_time_to_failure_bars": float(trades["time_to_failure_bars"].mean()) if trades["time_to_failure_bars"].notna().any() else np.nan,
        }]
    )


def build_overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_win_rate=("win_rate", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
            mean_candidate_events=("candidate_events", "mean"),
            mean_no_trade_ratio=("no_trade_ratio", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
            mean_time_to_failure_bars=("mean_time_to_failure_bars", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def choose_challenger(overall_summary: pd.DataFrame) -> str:
    hit = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if hit.empty:
        return PRIMARY_VARIANT
    challengers = hit[hit["variant"] != "raw_breakout"].copy()
    if challengers.empty:
        return PRIMARY_VARIANT
    ranked = challengers.sort_values(["mean_total_return", "mean_false_break_ratio", "mean_no_trade_ratio"], ascending=[False, True, True])
    return str(ranked.iloc[0]["variant"])


def derive_verdict(overall_summary: pd.DataFrame) -> tuple[str, list[str], str, str]:
    primary = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if primary.empty:
        return "hard verdict：本轮没有生成可读的 Rank 27 clean replication 结果。", ["缺少 6bps/side 总表。"], "park", PRIMARY_VARIANT
    raw = primary[primary["variant"] == "raw_breakout"].iloc[0]
    winner = choose_challenger(overall_summary)
    winner_row = primary[primary["variant"] == winner].iloc[0]
    verdict_tag = "park"
    if (
        float(winner_row["mean_total_return"]) > float(raw["mean_total_return"])
        and float(winner_row["mean_false_break_ratio"]) < float(raw["mean_false_break_ratio"])
        and float(winner_row["mean_total_return"]) > 0
        and float(winner_row["positive_asset_ratio"]) >= 2 / 3
    ):
        verdict_tag = "paper candidate"
    headline = (
        f"hard verdict：Rank 27 的 {winner} 当前更像 `{verdict_tag} / evidence pool`，没有形成足够干净的 paper candidate 读法。"
        if verdict_tag == "park"
        else f"hard verdict：Rank 27 的 {winner} 已通过最小 clean replication first verdict，可先进入 `paper candidate`。"
    )
    bullets = []
    for variant in VARIANTS:
        row = primary[primary["variant"] == variant].iloc[0]
        bullets.append(
            f"{variant}：mean_total_return {pct(row['mean_total_return'])}，positive_asset_ratio {pct(row['positive_asset_ratio'])}，mean_trades {num(row['mean_trades'], 1)}，mean_false_break_ratio {pct(row['mean_false_break_ratio'])}，mean_time_to_failure_bars {num(row['mean_time_to_failure_bars'], 1)}。"
        )
    if verdict_tag == "park":
        bullets.append("当前最好的 challenger 也没有同时做到‘成本后收益更好’和‘假突破率更低’，所以这轮更诚实的 desk call 是 park，而不是继续把 Rank 27 留在研究态续命。")
    else:
        bullets.append("最好的 challenger 同时改善了成本后收益和假突破率，因此这轮可以把它推进到 paper candidate pool，而不是继续停在 source-intake wording。")
    bullets.append("这轮只做了最小 clean replication：固定复用 BTC/ETH/SOL 的 120d 15m cache，比较 raw_breakout / neckline_confirm / neckline_confirm_plus_retest_hold；没有追新 bar，也没有展开完整 Light Stability Pack。")
    return headline, bullets, verdict_tag, winner


def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    headline, bullets, _, winner = derive_verdict(overall_summary)
    meta = meta_df.iloc[0].to_dict() if not meta_df.empty else {}
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    summary_table = render_table(
        overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST][["variant", "positive_asset_ratio", "mean_total_return", "mean_trades", "mean_false_break_ratio", "mean_time_to_failure_bars", "mean_no_trade_ratio"]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "mean_false_break_ratio", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1, "mean_time_to_failure_bars": 1},
    )
    asset_table = render_table(
        asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST) & (asset_summary["variant"] == winner)][["asset", "candidate_events", "trades", "total_return", "false_break_ratio", "mean_time_to_failure_bars", "no_trade_ratio"]],
        percent_cols={"total_return", "false_break_ratio", "no_trade_ratio"},
        digits_cols={"candidate_events": 0, "trades": 0, "mean_time_to_failure_bars": 1},
    )
    cost_table = render_table(
        overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_false_break_ratio", "mean_trades"]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_false_break_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1},
    )
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Mt.Gox neckline confirmation · clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · Mt.Gox neckline confirmation / pattern-complete breakout gate · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(str(meta.get('generated_at_utc', '-')))} ｜ 这页把 Rank 27 从 source-intake 推到最小 clean replication first verdict。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>本轮固定口径</h2>
    <ul>
      <li>样本：<code>Binance 120d / 15m / BTC+ETH+SOL</code></li>
      <li>模式近似：<code>EMA9(hlc3)</code> one-sided smoothing + 2-bar confirmed extrema + 双低点/颈线近似</li>
      <li>对照：<code>raw_breakout</code> vs <code>neckline_confirm</code> vs <code>neckline_confirm_plus_retest_hold</code></li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop</code></li>
      <li>先看：<code>false_break_ratio</code>、<code>post_cost_return</code>、<code>time_to_failure</code></li>
      <li>边界：只做 long 侧 first verdict；short 侧仍需额外 gate，当前不偷做镜像升格。</li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_mtgox_neckline_confirmation_15m/overall_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>winner per-asset（6bps/side）</h2>
    {asset_table}
  </div>

  <div class="card">
    <h2>cost ladder</h2>
    {cost_table}
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>如果确认层只是减少交易、但没有把 <code>false_break_ratio</code> 压下去，或者成本后收益并没改善，就不该继续包装成下一条 paper 候选。</li>
      <li>如果 <code>retest_hold</code> 的收益比 <code>neckline_confirm</code> 更差，说明“等得更久”在当前 15m crypto 样本里只是在错过顺势，而不是更诚实的 confirmation alpha。</li>
      <li>这页只回答一个问题：Rank 27 值不值得继续占 Scout 预算；不是直接去争 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    all_events = []
    all_trades = []
    all_nav = []
    all_summaries = []
    raw_candidate_events = []

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        candidate_events = build_candidate_events(bars)
        if not candidate_events.empty:
            raw_candidate_events.append(candidate_events)
        for variant in VARIANTS:
            variant_events = select_variant_events(candidate_events, variant) if not candidate_events.empty else pd.DataFrame()
            if not variant_events.empty:
                all_events.append(variant_events)
            for cost in COSTS:
                trades, nav = simulate_events(bars, variant_events, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                if not nav.empty:
                    all_nav.append(nav)
                all_summaries.append(summarize_trades(trades, nav, variant_events, asset, variant, cost))

    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    raw_events_df = pd.concat(raw_candidate_events, ignore_index=True) if raw_candidate_events else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    overall_summary = build_overall_summary(asset_summary)
    headline, _, verdict_tag, winner = derive_verdict(overall_summary)
    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_mtgox_neckline_confirmation_15m_v1",
            "winner_variant": winner,
            "verdict_tag": verdict_tag,
            "verdict": headline,
            "sample_window": "Binance 120d / 15m / BTC+ETH+SOL",
            "next_step": "若为 park，则默认切去新的 Scout 候选；若为 paper candidate，则下一轮才值得补最小 stability / writeback。",
        }
    ])

    if not raw_events_df.empty:
        raw_events_df.to_csv(ART_DIR / "candidate_events_raw.csv", index=False)
    if not events_df.empty:
        events_df.to_csv(ART_DIR / "candidate_events_by_variant.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    if not nav_df.empty:
        nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    meta_df.to_csv(ART_DIR / "clean_replication_meta.csv", index=False)
    write_report(asset_summary=asset_summary.sort_values(["cost_bps_per_side", "variant", "asset"]).reset_index(drop=True), overall_summary=overall_summary, meta_df=meta_df)
    print("[ok] mtgox neckline clean replication generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
