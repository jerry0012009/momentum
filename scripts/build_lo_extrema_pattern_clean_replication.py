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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_lo_extrema_pattern_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_lo_extrema_pattern_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

SMOOTH_SPAN = 9
EMA_FAST = 20
EMA_SLOW = 50
ATR_PERIOD = 14
CONFIRM_RIGHT = 2
ZONE_ATR_BAND = 0.35
BREAK_BUFFER = 0.05
RECLAIM_BUFFER = 0.00
PULLBACK_BUFFER = 0.03
PULLBACK_LOOKAHEAD = 3
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
VARIANTS = ["swing_break_only", "double_bottom_reclaim", "pullback_recovery_gate", "pattern_vote_guard"]
PRIMARY_VARIANT = "swing_break_only"
PARAM_CONFIGS = [
    {"label": "band030_buf003", "zone_atr_band": 0.30, "break_buffer": 0.03},
    {"label": "band035_buf005", "zone_atr_band": 0.35, "break_buffer": 0.05},
    {"label": "band040_buf005", "zone_atr_band": 0.40, "break_buffer": 0.05},
    {"label": "band035_buf007", "zone_atr_band": 0.35, "break_buffer": 0.07},
    {"label": "band040_buf007", "zone_atr_band": 0.40, "break_buffer": 0.07},
]


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
                    "smooth_value": float(center),
                    "atr": float(atr_here),
                }
            )
        if center <= min(left) and center < min(right):
            lows.append(
                {
                    "pivot_idx": idx,
                    "confirm_idx": confirm_idx,
                    "price": float(raw_low[idx]),
                    "smooth_value": float(center),
                    "atr": float(atr_here),
                }
            )
    return highs, lows


def zone_from_recent(pivots: list[dict], t: int, zone_atr_band: float) -> dict:
    eligible = [p for p in pivots if int(p["confirm_idx"]) <= t]
    if not eligible:
        return {"count": 0, "lower": np.nan, "upper": np.nan, "center": np.nan, "latest_confirm_idx": np.nan, "latest_pivot_idx": np.nan}
    latest = eligible[-1]
    atr_ref = float(latest.get("atr", np.nan))
    band = zone_atr_band * atr_ref if math.isfinite(atr_ref) and atr_ref > 0 else 0.0
    cluster = [latest]
    for prev in reversed(eligible[:-1]):
        if len(cluster) >= 3:
            break
        if abs(float(prev["price"]) - float(latest["price"])) <= band:
            cluster.append(prev)
        else:
            break
    prices = [float(x["price"]) for x in cluster]
    return {
        "count": len(cluster),
        "lower": float(min(prices)),
        "upper": float(max(prices)),
        "center": float(np.mean(prices)),
        "latest_confirm_idx": int(latest["confirm_idx"]),
        "latest_pivot_idx": int(latest["pivot_idx"]),
    }


def prepare_bars(asset: str, symbol: str, *, zone_atr_band: float = ZONE_ATR_BAND, break_buffer: float = BREAK_BUFFER) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["hlc3"] = (bars["high"] + bars["low"] + bars["close"]) / 3.0
    bars["smooth"] = ema(bars["hlc3"], SMOOTH_SPAN)
    bars["ema_fast"] = ema(bars["close"], EMA_FAST)
    bars["ema_slow"] = ema(bars["close"], EMA_SLOW)
    bars["ema_long"] = bars["ema_fast"] > bars["ema_slow"]
    bars["atr"] = compute_atr(bars, ATR_PERIOD)

    high_pivots, low_pivots = build_confirmed_pivots(bars)
    n = len(bars)
    support_lower = np.full(n, np.nan)
    support_upper = np.full(n, np.nan)
    support_count = np.zeros(n)
    support_confirm = np.full(n, np.nan)
    support_pivot = np.full(n, np.nan)
    resistance_lower = np.full(n, np.nan)
    resistance_upper = np.full(n, np.nan)
    resistance_count = np.zeros(n)
    resistance_confirm = np.full(n, np.nan)
    resistance_pivot = np.full(n, np.nan)
    dbl_sig = np.zeros(n, dtype=bool)
    dbl_mid = np.full(n, np.nan)
    pb_sig = np.zeros(n, dtype=bool)
    pb_zone = np.full(n, np.nan)

    breakout_memory: list[dict] = []

    for t in range(n):
        support = zone_from_recent(low_pivots, t, zone_atr_band)
        resistance = zone_from_recent(high_pivots, t, zone_atr_band)
        support_lower[t] = support["lower"]
        support_upper[t] = support["upper"]
        support_count[t] = support["count"]
        support_confirm[t] = support["latest_confirm_idx"]
        support_pivot[t] = support["latest_pivot_idx"]
        resistance_lower[t] = resistance["lower"]
        resistance_upper[t] = resistance["upper"]
        resistance_count[t] = resistance["count"]
        resistance_confirm[t] = resistance["latest_confirm_idx"]
        resistance_pivot[t] = resistance["latest_pivot_idx"]

        row = bars.iloc[t]
        atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
        if not (bool(row["ema_long"]) and math.isfinite(atr) and atr > 0):
            continue

        res_upper = resistance["upper"]
        if resistance["count"] >= 1 and math.isfinite(res_upper) and float(row["close"]) > res_upper + break_buffer * atr:
            breakout_memory.append({"breakout_idx": t, "zone_upper": float(res_upper), "expires": min(t + PULLBACK_LOOKAHEAD, n - 1)})

        active_breakouts: list[dict] = []
        for info in breakout_memory:
            if t > int(info["expires"]):
                continue
            zone_upper = float(info["zone_upper"])
            if float(row["low"]) <= zone_upper + 0.05 * atr and float(row["close"]) >= zone_upper + PULLBACK_BUFFER * atr and t > int(info["breakout_idx"]):
                pb_sig[t] = True
                pb_zone[t] = zone_upper
            active_breakouts.append(info)
        breakout_memory = active_breakouts

        eligible_lows = [p for p in low_pivots if int(p["confirm_idx"]) <= t]
        if len(eligible_lows) >= 2:
            low2 = eligible_lows[-1]
            low1 = eligible_lows[-2]
            atr_ref = float(low2.get("atr", np.nan))
            if math.isfinite(atr_ref) and atr_ref > 0 and abs(float(low2["price"]) - float(low1["price"])) <= zone_atr_band * atr_ref:
                between_highs = [p for p in high_pivots if int(low1["pivot_idx"]) < int(p["pivot_idx"]) < int(low2["pivot_idx"]) and int(p["confirm_idx"]) <= t]
                if between_highs:
                    midpoint = max(float(p["price"]) for p in between_highs)
                    if float(row["close"]) > midpoint + RECLAIM_BUFFER * atr and float(row["close"]) > support["upper"]:
                        dbl_sig[t] = True
                        dbl_mid[t] = midpoint

    bars["support_lower"] = support_lower
    bars["support_upper"] = support_upper
    bars["support_count"] = support_count
    bars["support_confirm_idx"] = support_confirm
    bars["support_pivot_idx"] = support_pivot
    bars["resistance_lower"] = resistance_lower
    bars["resistance_upper"] = resistance_upper
    bars["resistance_count"] = resistance_count
    bars["resistance_confirm_idx"] = resistance_confirm
    bars["resistance_pivot_idx"] = resistance_pivot
    bars["swing_break_only"] = (
        bars["ema_long"]
        & bars["resistance_count"].ge(1)
        & (bars["close"] > bars["resistance_upper"] + break_buffer * bars["atr"])
    ).fillna(False)
    bars["double_bottom_reclaim"] = pd.Series(dbl_sig, index=bars.index)
    bars["pullback_recovery_gate"] = pd.Series(pb_sig, index=bars.index)
    bars["pattern_vote_guard_votes"] = (
        bars["double_bottom_reclaim"].astype(int)
        + bars["pullback_recovery_gate"].astype(int)
        + bars["ema_long"].astype(int)
    )
    bars["pattern_vote_guard"] = bars["pattern_vote_guard_votes"] >= 2
    bars["double_bottom_midpoint"] = dbl_mid
    bars["pullback_zone_upper"] = pb_zone
    return bars


def build_events(bars: pd.DataFrame, variant: str) -> pd.DataFrame:
    signal = bars[variant].fillna(False)
    transition = signal & (~signal.shift(1).fillna(False))
    rows: list[dict] = []
    for idx in np.where(transition)[0]:
        row = bars.iloc[idx]
        atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
        if not math.isfinite(atr) or atr <= 0:
            continue
        zone_upper = float(row["resistance_upper"]) if pd.notna(row["resistance_upper"]) else float("nan")
        zone_lower = float(row["support_lower"]) if pd.notna(row["support_lower"]) else float("nan")
        if variant == "double_bottom_reclaim":
            trigger_level = float(row["double_bottom_midpoint"]) if pd.notna(row["double_bottom_midpoint"]) else zone_upper
        elif variant == "pullback_recovery_gate":
            trigger_level = float(row["pullback_zone_upper"]) if pd.notna(row["pullback_zone_upper"]) else zone_upper
        else:
            trigger_level = zone_upper
        false_break = float("nan")
        future = bars.iloc[idx + 1 : idx + 4]
        if not future.empty and math.isfinite(zone_upper):
            false_break = float((future["close"] <= zone_upper).any())
        rows.append(
            {
                "asset": row["asset"],
                "variant": variant,
                "signal_idx": int(idx),
                "signal_ts": row["timestamp"],
                "atr": atr,
                "zone_upper": zone_upper,
                "zone_lower": zone_lower,
                "trigger_level": trigger_level,
                "support_count": int(row["support_count"]) if pd.notna(row["support_count"]) else 0,
                "resistance_count": int(row["resistance_count"]) if pd.notna(row["resistance_count"]) else 0,
                "vote_count": int(row.get("pattern_vote_guard_votes", 0)),
                "false_break_proxy": false_break,
            }
        )
    return pd.DataFrame(rows)


def simulate_events(bars: pd.DataFrame, events: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if events.empty:
        nav = pd.DataFrame([
            {"asset": bars.iloc[0]["asset"], "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": 1.0, "cost_bps_per_side": float(cost_bps_per_side)}
        ])
        return pd.DataFrame(), nav
    cost_rate = float(cost_bps_per_side) / 10000.0
    trades = []
    nav = 1.0
    nav_rows = [{"asset": bars.iloc[0]["asset"], "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)}]
    last_exit_idx = -1
    for _, event in events.iterrows():
        signal_idx = int(event["signal_idx"])
        if signal_idx <= last_exit_idx:
            continue
        entry_idx = signal_idx + 1
        if entry_idx >= len(bars):
            continue
        entry_price = float(bars.iloc[entry_idx]["open"])
        atr = float(event["atr"])
        if not math.isfinite(entry_price) or entry_price <= 0 or not math.isfinite(atr) or atr <= 0:
            continue
        stop_price = entry_price - STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, len(bars) - 1)
        exit_idx = None
        exit_price = None
        exit_reason = None
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
                "asset": bars.iloc[0]["asset"],
                "variant": variant,
                "signal_ts": pd.to_datetime(event["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": bars.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": bars.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
                "cost_bps_per_side": float(cost_bps_per_side),
                "false_break_proxy": float(event["false_break_proxy"]) if pd.notna(event["false_break_proxy"]) else np.nan,
                "vote_count": int(event.get("vote_count", 0)),
            }
        )
        nav_rows.append({"asset": bars.iloc[0]["asset"], "variant": variant, "timestamp": bars.iloc[exit_idx]["timestamp"], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)})
        last_exit_idx = exit_idx
    return pd.DataFrame(trades), pd.DataFrame(nav_rows)


def summarize_trades(trades: pd.DataFrame, nav: pd.DataFrame, candidate_events: pd.DataFrame, asset: str, variant: str, cost: float) -> pd.DataFrame:
    total_events = int(len(candidate_events))
    accepted_events = int(len(trades))
    no_trade_ratio = 1.0 - (accepted_events / total_events) if total_events else np.nan
    if trades.empty:
        return pd.DataFrame([
            {
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
                "false_break_proxy": np.nan,
            }
        ])
    running_peak = nav["nav"].cummax() if not nav.empty else pd.Series(dtype=float)
    drawdown = nav["nav"] / running_peak - 1.0 if not nav.empty else pd.Series(dtype=float)
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    return pd.DataFrame([
        {
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
            "false_break_proxy": float(trades["false_break_proxy"].mean()) if trades["false_break_proxy"].notna().any() else np.nan,
        }
    ])


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
            mean_false_break_proxy=("false_break_proxy", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_time_stability(trades_df: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = trades_df[(trades_df["variant"] == variant) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if hit.empty or len(hit) < 9:
        return pd.DataFrame(columns=cols)
    hit["entry_dt"] = pd.to_datetime(hit["entry_ts"], utc=True)
    hit = hit.sort_values("entry_dt").reset_index(drop=True)
    hit["bucket"] = pd.qcut(np.arange(len(hit)), 3, labels=["early", "mid", "late"])
    rows = []
    for bucket, g in hit.groupby("bucket", observed=False):
        if g.empty:
            continue
        asset_totals = g.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({"bucket": str(bucket), "trades": int(len(g)), "mean_asset_return": float(asset_totals.mean())})
    bdf = pd.DataFrame(rows)
    if bdf.empty:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame([
        {"gate": "positive_bucket_floor", "status": "pass" if int((bdf['mean_asset_return'] > 0).sum()) >= 2 else "fail", "actual": f"{int((bdf['mean_asset_return'] > 0).sum())}/3 positive buckets", "threshold": ">= 2 positive buckets", "why_it_matters": "排除只靠单一时间 pocket。"},
        {"gate": "bucket_trade_floor", "status": "pass" if int(bdf['trades'].min()) >= 5 else "fail", "actual": f"min bucket trades = {int(bdf['trades'].min())}", "threshold": ">= 5 trades per bucket", "why_it_matters": "时间稳定性不能只靠几笔交易。"},
        {"gate": "worst_bucket_watch", "status": "watch" if float(bdf['mean_asset_return'].min()) <= -0.01 else "pass", "actual": f"worst mean_asset_return = {pct(bdf['mean_asset_return'].min())}", "threshold": "ideally > -1.00%", "why_it_matters": "最弱 pocket 若明显翻负，就不该写成稳定。"},
    ], columns=cols)


def build_cross_asset_stability(asset_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = asset_summary[(asset_summary["variant"] == variant) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    worst = hit.sort_values("total_return").iloc[0]
    positive_assets = int((hit["total_return"] > 0).sum())
    return pd.DataFrame([
        {"gate": "positive_asset_floor", "status": "pass" if positive_assets >= 2 else "fail", "actual": f"{positive_assets}/{len(hit)} assets positive", "threshold": ">= 2 positive assets", "why_it_matters": "不能只靠单一币种。"},
        {"gate": "min_trade_floor", "status": "pass" if int(hit['trades'].min()) >= 5 else "fail", "actual": f"min trades = {int(hit['trades'].min())}", "threshold": ">= 5 per asset", "why_it_matters": "跨标的判断也要有最小样本。"},
        {"gate": "worst_asset_watch", "status": "watch" if float(worst['total_return']) <= -0.01 else "pass", "actual": f"{worst['asset']} total_return={pct(worst['total_return'])}", "threshold": "ideally > -1.00%", "why_it_matters": "最弱腿不能被均值掩盖。"},
    ], columns=cols)


def run_parameter_grid() -> pd.DataFrame:
    rows = []
    for cfg in PARAM_CONFIGS:
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = prepare_bars(asset, symbol, zone_atr_band=float(cfg["zone_atr_band"]), break_buffer=float(cfg["break_buffer"]))
            events = build_events(bars, PRIMARY_VARIANT)
            trades, nav = simulate_events(bars, events, PRIMARY_VARIANT, PRIMARY_COST)
            asset_rows.append(summarize_trades(trades, nav, events, asset, PRIMARY_VARIANT, PRIMARY_COST))
        agg = build_overall_summary(pd.concat(asset_rows, ignore_index=True))
        if agg.empty:
            continue
        row = agg.iloc[0].to_dict()
        row.update(cfg)
        rows.append(row)
    return pd.DataFrame(rows)


def build_parameter_stability(grid: pd.DataFrame) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if grid.empty:
        return pd.DataFrame(columns=cols)
    positive = int((grid["mean_total_return"] > 0).sum())
    stable_assets = int((grid["positive_asset_ratio"] >= (2 / 3)).sum())
    min_trades = float(grid["min_trades"].min())
    worst = grid.sort_values(["mean_total_return", "positive_asset_ratio"]).iloc[0]
    return pd.DataFrame([
        {"gate": "positive_neighbor_floor", "status": "pass" if positive >= 3 else "fail", "actual": f"{positive}/{len(grid)} configs positive", "threshold": ">= 3 positive local neighbors", "why_it_matters": "小参数邻域别一碰就碎。"},
        {"gate": "cross_asset_neighbor_floor", "status": "pass" if stable_assets >= 3 else "fail", "actual": f"{stable_assets}/{len(grid)} keep >=2/3 positive assets", "threshold": ">= 3 configs keep cross-asset floor", "why_it_matters": "不能只靠单点 lucky pocket。"},
        {"gate": "trade_count_neighbor_floor", "status": "pass" if min_trades >= 5 else "fail", "actual": f"min trades across neighbors = {int(min_trades)}", "threshold": ">= 5 per asset", "why_it_matters": "参数稳定性也需要最小交易数。"},
        {"gate": "worst_neighbor_watch", "status": "watch" if float(worst['mean_total_return']) <= -0.01 else "pass", "actual": f"{worst['label']} mean_total_return={pct(worst['mean_total_return'])}", "threshold": "ideally > -1.00%", "why_it_matters": "最差近邻若明显翻负，说明仍偏 sample-bound。"},
    ], columns=cols)


def build_cost_trade_stability(overall_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = overall_summary[overall_summary["variant"] == variant].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    cost_positive = int((hit["mean_total_return"] > 0).sum())
    at20 = hit[hit["cost_bps_per_side"] == 20.0]
    at20_val = float(at20.iloc[0]["mean_total_return"]) if not at20.empty else np.nan
    return pd.DataFrame([
        {"gate": "cost_survival_floor", "status": "pass" if cost_positive >= 2 else "fail", "actual": f"{cost_positive}/{len(hit)} cost levels positive", "threshold": ">= 2 positive cost levels", "why_it_matters": "轻量摩擦后不能立刻归零。"},
        {"gate": "trade_count_floor", "status": "pass" if int(hit['min_trades'].min()) >= 5 else "fail", "actual": f"min trades across cost ladder = {int(hit['min_trades'].min())}", "threshold": ">= 5 per asset", "why_it_matters": "trade count 过薄就不配继续推广。"},
        {"gate": "20bps_watch", "status": "watch" if pd.notna(at20_val) and at20_val <= 0 else "pass", "actual": pct(at20_val) if pd.notna(at20_val) else "-", "threshold": "ideally > 0% @ 20bps", "why_it_matters": "20bps 不是硬门槛，但能看出是否只在轻摩擦下存活。"},
    ], columns=cols)


def choose_candidate_variant(overall_summary: pd.DataFrame) -> str:
    hit = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if hit.empty:
        return PRIMARY_VARIANT
    actionable = hit[hit["mean_trades"] > 0].copy()
    ranked_source = actionable if not actionable.empty else hit
    ranked = ranked_source.sort_values(["mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"], ascending=[False, False, True])
    return str(ranked.iloc[0]["variant"])


def derive_verdict(overall_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame) -> tuple[str, list[str], str, str]:
    primary = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if primary.empty:
        return "hard verdict：当前没有生成可读 clean replication 结果。", ["缺少 6bps/side 总表。"], "park", PRIMARY_VARIANT
    winner = choose_candidate_variant(overall_summary)
    winner_row = primary[primary["variant"] == winner].iloc[0]
    fail_sets = []
    for name, df in [("time", time_stability), ("parameter", parameter_stability), ("cross_asset", cross_asset_stability), ("cost_trade", cost_trade_stability)]:
        if not df.empty and (df["status"] == "fail").any():
            fail_sets.append(name)
    verdict_tag = "park"
    headline = "hard verdict：Lo-style causal extrema pattern gate 这轮更像 `park / evidence pool`，暂不进入 paper candidate pool。"
    if float(winner_row["mean_total_return"]) > 0 and float(winner_row["positive_asset_ratio"]) >= 2 / 3 and float(winner_row["mean_no_trade_ratio"]) <= 0.80 and not fail_sets:
        verdict_tag = "paper candidate"
        if float(winner_row["mean_total_return"]) > 0.03 and float(winner_row["mean_trades"]) >= 8:
            verdict_tag = "narrow paper pilot"
        headline = f"hard verdict：Lo-style causal extrema pattern gate 的 {winner} 已通过最小 clean replication + Light Stability Pack，可进入 `{verdict_tag}`。"
    bullets = []
    for variant in VARIANTS:
        hit = primary[primary["variant"] == variant]
        if not hit.empty:
            row = hit.iloc[0]
            bullets.append(f"{variant}：mean_total_return {pct(row['mean_total_return'])}，positive_asset_ratio {pct(row['positive_asset_ratio'])}，mean_trades {num(row['mean_trades'],1)}，mean_no_trade_ratio {pct(row['mean_no_trade_ratio'])}，false_break_proxy {pct(row['mean_false_break_proxy'])}。")
    bullets.append("两条轻量诚实守门已通过：规则能明确写成 trade on / trade off；当前实现只用 one-sided EMA 平滑、确认后 extrema 和已有 bar 上的 zone，不用 future label。")
    bullets.append(f"当前 Light Stability Pack 硬 fail 位：{', '.join(fail_sets) if fail_sets else '无硬 fail'}。")
    if float(winner_row["mean_no_trade_ratio"]) > 0.80:
        bullets.append("winner 的 no_trade_ratio 已超过 80%，即便 headline 不差，也要优先怀疑是假改善。")
    if verdict_tag == "park":
        bullets.append("因此这条线当前更像 Scout 证据包，不该抢占新的 paper wiring。")
    else:
        bullets.append(f"因此当前最诚实的 desk call 是：把 {winner} 推进到窄范围 `{verdict_tag}`，而不是继续停在 intake wording。")
    return headline, bullets, verdict_tag, winner


def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame, parameter_grid: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    headline, bullets, _, winner = derive_verdict(overall_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)
    meta = meta_df.iloc[0].to_dict() if not meta_df.empty else {}
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    summary_table = render_table(
        overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST][["variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "mean_trades", "mean_no_trade_ratio", "mean_false_break_proxy"]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "mean_no_trade_ratio", "mean_false_break_proxy"},
        digits_cols={"mean_trades": 1},
    )
    asset_table = render_table(
        asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST) & (asset_summary["variant"] == winner)][["asset", "candidate_events", "trades", "total_return", "win_rate", "no_trade_ratio", "false_break_proxy"]],
        percent_cols={"total_return", "win_rate", "no_trade_ratio", "false_break_proxy"},
        digits_cols={"candidate_events": 0, "trades": 0},
    )
    cost_table = render_table(
        overall_summary[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1},
    )
    time_table = render_table(time_stability, percent_cols=set())
    param_table = render_table(parameter_stability, percent_cols=set())
    cross_table = render_table(cross_asset_stability, percent_cols=set())
    cost_stability_table = render_table(cost_trade_stability, percent_cols=set())
    grid_table = render_table(
        parameter_grid[["label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]] if not parameter_grid.empty else parameter_grid,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1},
    )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Lo extrema pattern · clean replication</title>
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
  <h1>Scout Seat · Lo-style causal extrema pattern gate · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(str(meta.get('generated_at_utc', '-')))} ｜ 这页把上一轮 clean-room spec 推进到最小 clean replication + Light Stability Pack，不再停留在 source-intake wording。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>本轮 clean replication 口径</h2>
    <ul>
      <li>样本：<code>Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD</code></li>
      <li>平滑：<code>one-sided EMA9(hlc3)</code></li>
      <li>extrema：<code>confirmed local highs/lows with 2-bar confirmation delay</code></li>
      <li>变体：<code>swing_break_only / double_bottom_reclaim / pullback_recovery_gate / pattern_vote_guard</code></li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side</code></li>
      <li>spec：<code>{escape(str(SPEC_PATH.relative_to(ROOT)) if SPEC_PATH.exists() else '-')}</code></li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_lo_extrema_pattern_15m/overall_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>winner per-asset（6bps/side）</h2>
    {asset_table}
    <p class="muted">这里把 <code>candidate_events</code>、<code>trades</code>、<code>no_trade_ratio</code> 与 <code>false_break_proxy</code> 一起外显，避免把“少做交易”或“假突破更少”误写成 alpha 增量。</p>
  </div>

  <div class="card">
    <h2>cost ladder</h2>
    {cost_table}
    {cost_stability_table}
  </div>

  <div class="card">
    <h2>Light Stability Pack</h2>
    <h3>1) 时间稳定性</h3>
    {time_table}
    <h3>2) 参数稳定性</h3>
    {param_table}
    <h3>3) 跨标的稳定性</h3>
    {cross_table}
    <h3>4) 成本 / 交易数稳定性</h3>
    {cost_stability_table}
  </div>

  <div class="card">
    <h2>parameter neighbor grid（swing_break_only）</h2>
    {grid_table}
    <p class="muted">这里只看 zone band 与 breakout buffer 的小邻域，防止把单点阈值 pocket 写成结构 alpha。</p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>如果更优版本只是靠 <code>no_trade_ratio</code> 飙升才守住收益，就应该直接 <code>park</code>。</li>
      <li>如果 pattern 版本并不优于最朴素的 <code>swing_break_only</code>，就说明“结构更复杂”本身没有带来足够增量。</li>
      <li>这页服务的是 Scout 快筛 verdict：<code>park / paper candidate / narrow paper pilot</code>，不是直接去争 Live Seat。</li>
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
    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        for variant in VARIANTS:
            events = build_events(bars, variant)
            if not events.empty:
                all_events.append(events)
            for cost in COSTS:
                trades, nav = simulate_events(bars, events, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                if not nav.empty:
                    all_nav.append(nav)
                all_summaries.append(summarize_trades(trades, nav, events, asset, variant, cost))
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    overall_summary = build_overall_summary(asset_summary)
    winner = choose_candidate_variant(overall_summary)
    time_stability = build_time_stability(trades_df, winner)
    parameter_grid = run_parameter_grid()
    parameter_stability = build_parameter_stability(parameter_grid)
    cross_asset_stability = build_cross_asset_stability(asset_summary, winner)
    cost_trade_stability = build_cost_trade_stability(overall_summary, winner)
    verdict_headline, _, verdict_tag, winner = derive_verdict(overall_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)
    meta_df = pd.DataFrame([
        {"generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "candidate_id": "scout_lo_extrema_pattern_15m_v1", "winner_variant": winner, "verdict_tag": verdict_tag, "verdict": verdict_headline, "sample_window": "Binance 120d / 15m / BTC+ETH+SOL", "next_step": "若为 park，则默认压回 evidence pool 并切到新的 repo-based 15m crypto intake；若为 paper candidate，则下一轮只补最小 candidate-pool writeback。"}
    ])
    if not events_df.empty:
        events_df.to_csv(ART_DIR / "candidate_events.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    if not nav_df.empty:
        nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    if not time_stability.empty:
        time_stability.to_csv(ART_DIR / "time_stability_drycheck.csv", index=False)
    if not parameter_grid.empty:
        parameter_grid.to_csv(ART_DIR / "parameter_neighbor_grid.csv", index=False)
    if not parameter_stability.empty:
        parameter_stability.to_csv(ART_DIR / "parameter_stability_drycheck.csv", index=False)
    if not cross_asset_stability.empty:
        cross_asset_stability.to_csv(ART_DIR / "cross_asset_stability_drycheck.csv", index=False)
    if not cost_trade_stability.empty:
        cost_trade_stability.to_csv(ART_DIR / "cost_trade_stability_drycheck.csv", index=False)
    meta_df.to_csv(ART_DIR / "clean_replication_meta.csv", index=False)
    write_report(
        overall_summary,
        asset_summary.sort_values(["cost_bps_per_side", "variant", "asset"]).reset_index(drop=True),
        time_stability,
        parameter_stability,
        cross_asset_stability,
        cost_trade_stability,
        parameter_grid,
        meta_df,
    )
    print("[ok] lo extrema pattern clean replication generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
