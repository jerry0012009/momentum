#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import math
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank138_funding_oi_crowding_breadth_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank138_funding_oi_crowding_breadth_15m"
READING_PAGE = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank138_funding_oi_crowding_breadth_clean_replication.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_trend_long", "reclaim_long", "breakdown_short"]
VARIANTS = ["baseline", "size_discount_p80", "veto_p90", "extra_confirm_p80"]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "veto_p90"
SAMPLE_DAYS = 30
EMA_FAST = 9
EMA_SLOW = 15
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0005
ATR_PERIOD = 14
BREAK_LOOKBACK = 20
RECLAIM_LOOKBACK = 20
RECLAIM_BREAK_ATR = 0.1
RECLAIM_RETEST_ATR = 0.35
BREAK_CONFIRM_ATR = 0.1
BREAK_RETEST_ATR = 0.5
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
BREADTH_WINDOW_BARS = 10 * 24 * 4  # 10d of 15m bars
BINANCE_LIMIT = 500
OI_URL = "https://fapi.binance.com/futures/data/openInterestHist"
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
REQ_TIMEOUT = 20


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


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
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    cutoff = df["timestamp"].max() - pd.Timedelta(days=SAMPLE_DAYS)
    df = df[df["timestamp"] >= cutoff].copy()
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_oi_5m(symbol: str, start_ms: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    end_time: int | None = None
    max_pages = math.ceil((SAMPLE_DAYS * 24 * 12) / BINANCE_LIMIT) + 4
    for _ in range(max_pages):
        params: dict[str, object] = {
            "symbol": symbol,
            "contractType": "PERPETUAL",
            "period": "5m",
            "limit": BINANCE_LIMIT,
        }
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(OI_URL, params=params, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = min(int(item["timestamp"]) for item in batch)
        if earliest <= start_ms:
            break
        end_time = earliest - 1
    if not rows:
        return pd.DataFrame(columns=["timestamp", "sumOpenInterest"])
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["sumOpenInterest"] = pd.to_numeric(df["sumOpenInterest"], errors="coerce")
    df = df[["timestamp", "sumOpenInterest"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df = df[df["timestamp"] >= pd.to_datetime(start_ms, unit="ms", utc=True)].copy()
    return df


def aggregate_oi_to_15m(oi_5m: pd.DataFrame) -> pd.DataFrame:
    if oi_5m.empty:
        return pd.DataFrame(columns=["timestamp", "oi_close", "oi_delta_15m"])
    work = oi_5m.copy()
    work["timestamp"] = work["timestamp"].dt.floor("15min")
    out = work.groupby("timestamp", as_index=False)["sumOpenInterest"].last().rename(columns={"sumOpenInterest": "oi_close"})
    out["oi_delta_15m"] = out["oi_close"].diff()
    return out


def fetch_funding(symbol: str, start_ms: int) -> pd.DataFrame:
    params = {"symbol": symbol, "limit": 1000, "startTime": start_ms}
    resp = requests.get(FUNDING_URL, params=params, timeout=REQ_TIMEOUT)
    resp.raise_for_status()
    rows = resp.json()
    if not rows:
        return pd.DataFrame(columns=["timestamp", "funding_rate"])
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
    df["funding_rate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
    return df[["timestamp", "funding_rate"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)


def build_asset_frame(asset: str, symbol: str, start_ms: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    bars = load_cached_bars(symbol, asset)
    oi_5m = fetch_oi_5m(symbol, start_ms)
    oi_15m = aggregate_oi_to_15m(oi_5m)
    funding = fetch_funding(symbol, start_ms)

    frame = bars.merge(oi_15m, on="timestamp", how="left")
    frame = pd.merge_asof(
        frame.sort_values("timestamp"),
        funding.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    frame["ema_fast"] = frame["close"].ewm(span=EMA_FAST, adjust=False).mean()
    frame["ema_slow"] = frame["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    frame["ema_slope"] = frame["ema_fast"].pct_change(EMA_SLOPE_LOOKBACK)
    frame["atr14"] = compute_atr(frame)
    frame["rolling_high"] = frame["high"].rolling(RECLAIM_LOOKBACK, min_periods=RECLAIM_LOOKBACK).max().shift(1)
    frame["rolling_low"] = frame["low"].rolling(BREAK_LOOKBACK, min_periods=BREAK_LOOKBACK).min().shift(1)
    frame["asset"] = asset
    return frame.reset_index(drop=True), oi_5m, funding


def build_breadth(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for asset, frame in frames.items():
        part = frame[["timestamp", "funding_rate", "oi_delta_15m"]].copy()
        part["asset"] = asset
        part["is_long_crowded"] = ((part["funding_rate"] > 0) & (part["oi_delta_15m"] > 0)).fillna(False)
        part["is_short_crowded"] = ((part["funding_rate"] < 0) & (part["oi_delta_15m"] > 0)).fillna(False)
        part["has_obs"] = part["funding_rate"].notna() & part["oi_delta_15m"].notna()
        rows.append(part)
    panel = pd.concat(rows, ignore_index=True)
    breadth = (
        panel.groupby("timestamp", as_index=False)
        .agg(
            long_crowd_breadth=("is_long_crowded", "mean"),
            short_crowd_breadth=("is_short_crowded", "mean"),
            observed_assets=("has_obs", "sum"),
        )
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    for side in ["long", "short"]:
        col = f"{side}_crowd_breadth"
        breadth[f"{side}_p80"] = breadth[col].rolling(BREADTH_WINDOW_BARS, min_periods=max(96, BREADTH_WINDOW_BARS // 3)).quantile(0.8).shift(1)
        breadth[f"{side}_p90"] = breadth[col].rolling(BREADTH_WINDOW_BARS, min_periods=max(96, BREADTH_WINDOW_BARS // 3)).quantile(0.9).shift(1)
        breadth[f"{side}_crowded_p80"] = (breadth[col] >= breadth[f"{side}_p80"]).fillna(False)
        breadth[f"{side}_crowded_p90"] = (breadth[col] >= breadth[f"{side}_p90"]).fillna(False)
    return breadth


def base_signal(frame: pd.DataFrame, setup: str) -> pd.Series:
    if setup == "ema_trend_long":
        state = (
            (frame["ema_fast"] > frame["ema_slow"])
            & (frame["ema_slope"] > EMA_SLOPE_FLOOR)
            & (frame["close"] > frame["ema_fast"])
        )
        return (state & ~state.shift(1).fillna(False)).fillna(False)
    if setup == "reclaim_long":
        level = frame["rolling_high"]
        atr = frame["atr14"]
        setup_flag = (
            level.notna()
            & (frame["close"] > level + RECLAIM_BREAK_ATR * atr)
            & (frame["low"] <= level + RECLAIM_RETEST_ATR * atr)
        )
        return (setup_flag & ~setup_flag.shift(1).fillna(False)).fillna(False)
    if setup == "breakdown_short":
        level = frame["rolling_low"]
        atr = frame["atr14"]
        setup_flag = (
            level.notna()
            & (frame["close"] < level - BREAK_CONFIRM_ATR * atr)
            & (frame["high"] <= level + BREAK_RETEST_ATR * atr)
        )
        return (setup_flag & ~setup_flag.shift(1).fillna(False)).fillna(False)
    raise ValueError(setup)


def direction_for_setup(setup: str) -> int:
    return -1 if setup == "breakdown_short" else 1


def max_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    equity = (1.0 + returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def build_trades(frame: pd.DataFrame, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    sig = base_signal(frame, setup).fillna(False)
    direction = direction_for_setup(setup)
    crowded_p80_col = "long_crowded_p80" if direction > 0 else "short_crowded_p80"
    crowded_p90_col = "long_crowded_p90" if direction > 0 else "short_crowded_p90"
    breadth_col = "long_crowd_breadth" if direction > 0 else "short_crowd_breadth"
    cost_rate = float(cost_bps) / 10000.0
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1

    for idx in range(1, len(frame) - 3):
        if idx <= last_exit_idx or not bool(sig.iloc[idx]):
            continue
        signal_events += 1
        crowded_p80 = bool(frame.iloc[idx][crowded_p80_col])
        crowded_p90 = bool(frame.iloc[idx][crowded_p90_col])
        size_mult = 1.0
        entry_idx = idx + 1
        signal_kind = "baseline"

        if variant == "size_discount_p80" and crowded_p80:
            size_mult = 0.6
            signal_kind = "size_discount"
        elif variant == "veto_p90" and crowded_p90:
            signal_kind = "veto_skip"
            continue
        elif variant == "extra_confirm_p80" and crowded_p80:
            confirm_idx = idx + 1
            if confirm_idx >= len(frame) - 2:
                continue
            confirm_close = float(frame.iloc[confirm_idx]["close"])
            signal_close = float(frame.iloc[idx]["close"])
            confirmed = confirm_close > signal_close if direction > 0 else confirm_close < signal_close
            if not confirmed:
                signal_kind = "confirm_fail_skip"
                continue
            entry_idx = idx + 2
            signal_kind = "extra_confirm"

        if entry_idx >= len(frame):
            break
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = ((exit_px / entry_px) - 1.0) * direction
        gross_ret *= size_mult
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate * size_mult) * (1.0 - cost_rate * size_mult) - 1.0

        probe_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        early_ret = ((float(frame.iloc[probe_idx]["close"]) / entry_px) - 1.0) * direction * size_mult
        early_fail = int(early_ret <= 0)

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "size_multiplier": size_mult,
                "early_fail_4bars": early_fail,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "breadth_value": float(frame.iloc[idx][breadth_col]) if pd.notna(frame.iloc[idx][breadth_col]) else np.nan,
                "crowded_p80": int(crowded_p80),
                "crowded_p90": int(crowded_p90),
                "overlay_action": signal_kind,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "exposure_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "failure_rate_4bars": np.nan,
            "max_drawdown": np.nan,
            "crowded_trade_share": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "exposure_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "failure_rate_4bars": float(trades["early_fail_4bars"].mean()),
        "max_drawdown": max_drawdown(trades["net_ret"]),
        "crowded_trade_share": float(trades["crowded_p80"].mean()),
    }


def add_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in out["setup"].unique():
        for cost in out["cost_bps_per_side"].unique():
            baseline_map = (
                out[(out["setup"] == setup) & (out["variant"] == "baseline") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")[["trades"]]
                .to_dict("index")
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / baseline_map.get(r["asset"], {}).get("trades", np.nan)) if baseline_map.get(r["asset"], {}).get("trades", 0) else np.nan,
                axis=1,
            )
    return out


def add_exposure_retention(asset_df: pd.DataFrame, trades_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    if trades_df.empty:
        return out
    exposure = (
        trades_df.groupby(["asset", "setup", "variant", "cost_bps_per_side"], dropna=False)["size_multiplier"]
        .sum()
        .reset_index()
        .rename(columns={"size_multiplier": "size_sum"})
    )
    baseline = (
        exposure[exposure["variant"] == "baseline"]
        .rename(columns={"size_sum": "baseline_size_sum"})
        [["asset", "setup", "cost_bps_per_side", "baseline_size_sum"]]
    )
    exposure = exposure.merge(baseline, on=["asset", "setup", "cost_bps_per_side"], how="left")
    exposure["exposure_retention"] = exposure["size_sum"] / exposure["baseline_size_sum"]
    out = out.merge(
        exposure[["asset", "setup", "variant", "cost_bps_per_side", "exposure_retention"]],
        on=["asset", "setup", "variant", "cost_bps_per_side"],
        how="left",
        suffixes=("", "_new"),
    )
    if "exposure_retention_new" in out.columns:
        out["exposure_retention"] = out["exposure_retention_new"].combine_first(out["exposure_retention"])
        out = out.drop(columns=["exposure_retention_new"])
    return out


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    grouped = asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
    for (setup, variant, cost), grp in grouped:
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if grp["trade_count_retention"].notna().any() else np.nan,
                "mean_exposure_retention": float(grp["exposure_retention"].mean()) if grp["exposure_retention"].notna().any() else np.nan,
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()) if grp["avg_net_ret"].notna().any() else np.nan,
                "mean_failure_rate_4bars": float(grp["failure_rate_4bars"].mean()) if grp["failure_rate_4bars"].notna().any() else np.nan,
                "mean_max_drawdown": float(grp["max_drawdown"].mean()) if grp["max_drawdown"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "variant", "cost_bps_per_side"]).reset_index(drop=True)


def best_variant_rows(overall_df: pd.DataFrame, cost: float = PRIMARY_COST) -> tuple[pd.DataFrame, pd.DataFrame]:
    cost_df = overall_df[overall_df["cost_bps_per_side"] == cost].copy()
    baseline = cost_df[cost_df["variant"] == "baseline"].copy()
    others = cost_df[cost_df["variant"] != "baseline"].copy()
    return baseline, others


def build_scorecard(overall_df: pd.DataFrame) -> pd.DataFrame:
    baseline, others = best_variant_rows(overall_df)
    if others.empty or baseline.empty:
        return pd.DataFrame([{
            "rank": 138,
            "candidate": "funding × OI cross-symbol crowding breadth overlay",
            "recommended_action": "park",
            "why_now": "最小 clean replication 没有产出足够结果。",
            "main_weakness": "artifact missing",
            "usefulness": 0,
            "time_stability": 0,
            "cross_asset_stability": 0,
            "cost_trade_stability": 0,
            "deployability": 0,
            "hard_fail_flags": "artifact_missing",
        }])

    merged = others.merge(
        baseline[["setup", "mean_avg_net_ret", "mean_failure_rate_4bars", "mean_trade_count_retention", "positive_asset_ratio", "mean_max_drawdown"]],
        on="setup",
        how="left",
        suffixes=("", "_baseline"),
    )
    merged["expectancy_delta"] = merged["mean_avg_net_ret"] - merged["mean_avg_net_ret_baseline"]
    merged["failure_delta"] = merged["mean_failure_rate_4bars"] - merged["mean_failure_rate_4bars_baseline"]
    merged["dd_delta"] = merged["mean_max_drawdown"] - merged["mean_max_drawdown_baseline"]
    merged = merged.sort_values(["expectancy_delta", "positive_asset_ratio", "mean_trade_count_retention"], ascending=[False, False, False]).reset_index(drop=True)
    best = merged.iloc[0]

    hard_flags: list[str] = []
    if float(best["mean_trade_count_retention"]) < 0.35:
        hard_flags.append("too_sparse")
    if float(best["positive_asset_ratio"]) < (2 / 3):
        hard_flags.append("single_pocket_dependency")
    if float(best["expectancy_delta"]) <= 0:
        hard_flags.append("post_cost_collapse")

    recommended_action = "promote_P2" if not hard_flags and float(best["mean_trade_count_retention"]) >= 0.6 else "park"
    usefulness = 3 if float(best["expectancy_delta"]) > 0.001 else 2 if float(best["expectancy_delta"]) > 0 else 1 if float(best["expectancy_delta"]) > -0.0005 else 0
    time_stability = 1
    cross_asset_stability = 3 if float(best["positive_asset_ratio"]) >= 2 / 3 else 1 if float(best["positive_asset_ratio"]) > 1 / 3 else 0
    cost_trade_stability = 3 if float(best["mean_trade_count_retention"]) >= 0.8 else 2 if float(best["mean_trade_count_retention"]) >= 0.6 else 1 if float(best["mean_trade_count_retention"]) >= 0.4 else 0
    deployability = 2 if best["variant"] in {"size_discount_p80", "veto_p90"} else 1

    why_now = (
        f"best minimal overlay={best['variant']} @ 6bps；"
        f"expectancy_delta={pct(best['expectancy_delta'])}，"
        f"trade_retention={pct(best['mean_trade_count_retention'])}，"
        f"positive_asset_ratio={pct(best['positive_asset_ratio'])}。"
    )
    weakness = "未做时间稳定性/更长样本；当前只是一轮 30d clean replication。"

    return pd.DataFrame([
        {
            "rank": 138,
            "candidate": "funding × OI cross-symbol crowding breadth overlay",
            "best_variant_6bps": best["variant"],
            "recommended_action": recommended_action,
            "why_now": why_now,
            "main_weakness": weakness,
            "usefulness": usefulness,
            "time_stability": time_stability,
            "cross_asset_stability": cross_asset_stability,
            "cost_trade_stability": cost_trade_stability,
            "deployability": deployability,
            "hard_fail_flags": ",".join(hard_flags) if hard_flags else "none",
        }
    ])


def build_verdict(overall_df: pd.DataFrame) -> tuple[str, str]:
    baseline, others = best_variant_rows(overall_df)
    if baseline.empty or others.empty:
        return "park", "缺少足够结果，直接 park。"
    merged = others.merge(
        baseline[["setup", "mean_avg_net_ret", "mean_failure_rate_4bars", "mean_trade_count_retention", "positive_asset_ratio", "mean_max_drawdown"]],
        on="setup",
        how="left",
        suffixes=("", "_baseline"),
    )
    merged["expectancy_delta"] = merged["mean_avg_net_ret"] - merged["mean_avg_net_ret_baseline"]
    merged["failure_delta"] = merged["mean_failure_rate_4bars"] - merged["mean_failure_rate_4bars_baseline"]
    merged = merged.sort_values(["expectancy_delta", "positive_asset_ratio", "mean_trade_count_retention"], ascending=[False, False, False]).reset_index(drop=True)
    best = merged.iloc[0]

    if float(best["expectancy_delta"]) > 0 and float(best["positive_asset_ratio"]) >= 2 / 3 and float(best["mean_trade_count_retention"]) >= 0.6:
        return (
            "keep_P1",
            f"最好的最小接法是 {best['variant']}：post-cost expectancy 比 baseline 改善 {pct(best['expectancy_delta'])}，跨资产正收益占比 {pct(best['positive_asset_ratio'])}，trade retention {pct(best['mean_trade_count_retention'])}；当前先 keep_P1，下一次只值得补 1 个轻量稳定性检查。",
        )

    return (
        "park",
        f"最好的最小接法 {best['variant']} 仍不够诚实：post-cost expectancy 改善 {pct(best['expectancy_delta'])}，跨资产正收益占比 {pct(best['positive_asset_ratio'])}，trade retention {pct(best['mean_trade_count_retention'])}。更像单 pocket / 砍交易数换来的好看数字，不值得继续占 desk 主资源。",
    )


def build_html(sample_meta: pd.DataFrame, breadth_df: pd.DataFrame, overall_df: pd.DataFrame, asset_df: pd.DataFrame, scorecard_df: pd.DataFrame, verdict: str, detail: str) -> str:
    overall_6 = overall_df[overall_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    asset_6 = asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    breadth_tail = breadth_df.tail(24).copy()
    percent_cols_overall = {
        "mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_exposure_retention",
        "mean_avg_net_ret", "mean_failure_rate_4bars", "mean_max_drawdown",
    }
    percent_cols_asset = {
        "trade_count_retention", "exposure_retention", "total_return", "avg_net_ret", "win_rate", "failure_rate_4bars", "max_drawdown", "crowded_trade_share",
    }
    percent_cols_breadth = {"long_crowd_breadth", "short_crowd_breadth", "long_p80", "long_p90", "short_p80", "short_p90"}
    percent_cols_score = set()
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 138 · funding × OI crowding breadth clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:40px auto; padding:0 18px; line-height:1.7; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:16px 18px; margin:14px 0; }}
    .muted {{ color:#6b7280; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ border:1px solid #e5e7eb; padding:6px 8px; text-align:left; vertical-align:top; }}
    th {{ background:#f3f4f6; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
  </style>
</head>
<body>
  <p><a href='../reading/repo_scout/rank138_funding_oi_crowding_breadth_source_intake.html'>← 返回 Rank 138 source intake</a></p>
  <h1>Rank 138 · funding × OI cross-symbol crowding breadth overlay（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated)}｜样本冻结：BTC / ETH / SOL 15m 最近 {SAMPLE_DAYS} 天本地 cache + Binance funding / 5m OI 聚合到 15m。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>把 <code>funding × OI crowding breadth</code> 收窄成 shared overlay 之后，它能不能在不过度砍样本的前提下，给最小 baseline 带来更诚实的 <b>post-cost expectancy / failure-rate / retention</b> 改善？</p>
    <ul>
      <li>baseline setup 只保留 3 条最小代理：<code>ema_trend_long</code>、<code>reclaim_long</code>、<code>breakdown_short</code>。</li>
      <li>overlay 只测 3 种最小接法：<code>size × 0.6 @ p80</code>、<code>veto @ p90</code>、<code>extra confirm @ p80</code>。</li>
      <li>统一执行：<code>next-bar open + no-overlap + hold 8 bars</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <p>{escape(detail)}</p>
  </div>

  <div class='card'>
    <h2>Scout Promotion Scorecard</h2>
    {render_table(scorecard_df, percent_cols=percent_cols_score)}
  </div>

  <div class='card'>
    <h2>sample meta</h2>
    {render_table(sample_meta)}
  </div>

  <div class='card'>
    <h2>overall summary（6bps）</h2>
    {render_table(overall_6, percent_cols=percent_cols_overall, digits_cols={'cost_bps_per_side':0, 'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>asset summary（6bps）</h2>
    {render_table(asset_6, percent_cols=percent_cols_asset, digits_cols={'cost_bps_per_side':0, 'signal_events':0, 'trades':0})}
  </div>

  <div class='card'>
    <h2>breadth tail（最近 24 根 15m）</h2>
    {render_table(breadth_tail[["timestamp", "long_crowd_breadth", "short_crowd_breadth", "long_p80", "long_p90", "short_p80", "short_p90", "observed_assets"]], percent_cols=percent_cols_breadth, digits_cols={'observed_assets':0})}
  </div>
</body>
</html>
"""


def build_reading_html(scorecard_df: pd.DataFrame, verdict: str, detail: str, overall_df: pd.DataFrame) -> str:
    primary = overall_df[(overall_df["cost_bps_per_side"] == PRIMARY_COST) & (overall_df["variant"] != "baseline")].copy()
    primary = primary.sort_values(["setup", "mean_avg_net_ret"], ascending=[True, False]).reset_index(drop=True)
    percent_cols = {"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_exposure_retention", "mean_avg_net_ret", "mean_failure_rate_4bars", "mean_max_drawdown"}
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 138 clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1080px; margin:40px auto; padding:0 18px; line-height:1.7; color:#111827; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ border:1px solid #e5e7eb; padding:6px 8px; text-align:left; vertical-align:top; }}
    th {{ background:#f3f4f6; }}
    .muted {{ color:#6b7280; }}
  </style>
</head>
<body>
  <h1>Rank 138 · funding × OI cross-symbol crowding breadth overlay</h1>
  <p class='muted'>最小 clean replication reader-facing 摘要</p>
  <p><b>hard verdict：{escape(verdict)}</b></p>
  <p>{escape(detail)}</p>
  <h2>Scorecard</h2>
  {render_table(scorecard_df)}
  <h2>6bps primary summary</h2>
  {render_table(primary, percent_cols=percent_cols, digits_cols={'cost_bps_per_side':0, 'mean_trades':1})}
  <p>完整报告：<a href='../factors/scout_rank138_funding_oi_crowding_breadth_15m/report.html'>factor report</a></p>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PAGE.parent)
    ensure_dir(ART_DIR / "oi_cache")
    ensure_dir(ART_DIR / "funding_cache")

    start_dt = datetime.now(timezone.utc) - timedelta(days=SAMPLE_DAYS + 2)
    start_ms = int(start_dt.timestamp() * 1000)

    frames: dict[str, pd.DataFrame] = {}
    meta_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame, oi_5m, funding = build_asset_frame(asset, symbol, start_ms)
        frames[asset] = frame
        oi_5m.to_csv(ART_DIR / "oi_cache" / f"{symbol}_5m_open_interest.csv", index=False)
        funding.to_csv(ART_DIR / "funding_cache" / f"{symbol}_funding.csv", index=False)
        meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bars_15m": int(len(frame)),
                "oi_rows_5m": int(len(oi_5m)),
                "funding_rows": int(len(funding)),
                "sample_start_utc": frame["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
                "sample_end_utc": frame["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
            }
        )

    breadth = build_breadth(frames)
    breadth.to_csv(ART_DIR / "breadth_panel.csv", index=False)

    all_trades: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    signal_rows: list[dict[str, object]] = []
    for asset, frame in frames.items():
        merged = frame.merge(breadth, on="timestamp", how="left")
        merged.to_csv(ART_DIR / f"{ASSETS[asset].lower()}_feature_frame.csv", index=False)
        for setup in SETUPS:
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, signal_events = build_trades(merged, setup, variant, cost)
                    if not trades.empty:
                        all_trades.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=signal_events))
                    signal_rows.append(
                        {
                            "asset": asset,
                            "setup": setup,
                            "variant": variant,
                            "cost_bps_per_side": cost,
                            "signal_events": signal_events,
                        }
                    )

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    pd.DataFrame(signal_rows).to_csv(ART_DIR / "signal_event_counts.csv", index=False)

    asset_df = add_retention(pd.DataFrame(asset_rows))
    asset_df = add_exposure_retention(asset_df, trades_df)
    overall_df = summarize_overall(asset_df)
    scorecard_df = build_scorecard(overall_df)
    verdict, detail = build_verdict(overall_df)
    sample_meta = pd.DataFrame(meta_rows)

    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    scorecard_df.to_csv(ART_DIR / "scorecard.csv", index=False)
    sample_meta.to_csv(ART_DIR / "sample_meta.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sample_days": SAMPLE_DAYS,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "primary_variant": PRIMARY_VARIANT,
            "verdict": verdict,
            "detail": detail,
        }
    ]).to_csv(ART_DIR / "summary.csv", index=False)

    (SITE_DIR / "report.html").write_text(build_html(sample_meta, breadth, overall_df, asset_df, scorecard_df, verdict, detail), encoding="utf-8")
    READING_PAGE.write_text(build_reading_html(scorecard_df, verdict, detail, overall_df), encoding="utf-8")
    print(f"ok: built rank138 clean replication ({verdict})")


if __name__ == "__main__":
    main()
