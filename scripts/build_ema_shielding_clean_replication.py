#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from build_volume_supportflip_higherlow_first_verdict import (
    ASSETS,
    ensure_dir,
    fmt_ts,
    num,
    pct,
    render_table,
)

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_ema_shielding_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_ema_shielding_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

EMA_FAST = 20
EMA_SLOW = 50
ATR_PERIOD = 14
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_VARIANT = "threshold_005"
PRIMARY_THRESHOLD = 0.05
RETEST_TOLERANCE_ATR = 0.05
RETEST_LOOKAHEAD_BARS = 4
THRESHOLDS = [0.03, 0.05, 0.08, 0.10, 0.12]
PRIMARY_LABELS = {
    "raw_cross": "raw_cross",
    "threshold_005": "threshold_005",
    "retest_hold": "retest_hold",
}


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


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


def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["ema_fast"] = bars["close"].ewm(span=EMA_FAST, adjust=False).mean()
    bars["ema_slow"] = bars["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    bars["atr"] = compute_atr(bars, ATR_PERIOD)
    bars["ema_spread"] = bars["ema_fast"] - bars["ema_slow"]
    bars["bias"] = np.where(bars["ema_spread"] > 0, "long", np.where(bars["ema_spread"] < 0, "short", "flat"))
    prev_bias = bars["bias"].shift(1).fillna("flat")
    bars["cross_transition"] = ((bars["bias"] != prev_bias) & (bars["bias"] != "flat")).astype(int)
    bars["dist_to_slow_atr"] = (bars["close"] - bars["ema_slow"]).abs() / bars["atr"].replace(0, np.nan)
    return bars


def build_events(bars: pd.DataFrame, threshold: float = PRIMARY_THRESHOLD) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(bars)
    for idx in range(n):
        row = bars.iloc[idx]
        if int(row["cross_transition"]) != 1:
            continue
        side = str(row["bias"])
        atr = float(row["atr"]) if pd.notna(row["atr"]) else float("nan")
        ema_slow = float(row["ema_slow"]) if pd.notna(row["ema_slow"]) else float("nan")
        if side not in {"long", "short"} or not math.isfinite(atr) or atr <= 0 or not math.isfinite(ema_slow):
            continue

        dist = float(row["dist_to_slow_atr"]) if pd.notna(row["dist_to_slow_atr"]) else float("nan")
        threshold_ok = math.isfinite(dist) and dist >= threshold
        threshold_idx = idx if threshold_ok else None

        retest_idx = None
        for j in range(idx + 1, min(idx + RETEST_LOOKAHEAD_BARS, n - 1) + 1):
            probe = bars.iloc[j]
            probe_atr = float(probe["atr"]) if pd.notna(probe["atr"]) else atr
            band = RETEST_TOLERANCE_ATR * probe_atr if math.isfinite(probe_atr) else 0.0
            probe_slow = float(probe["ema_slow"]) if pd.notna(probe["ema_slow"]) else ema_slow
            if side == "long":
                touch = float(probe["low"]) <= probe_slow + band
                hold = float(probe["close"]) >= probe_slow
            else:
                touch = float(probe["high"]) >= probe_slow - band
                hold = float(probe["close"]) <= probe_slow
            if touch and hold:
                retest_idx = j
                break

        rows.append(
            {
                "asset": str(row["asset"]),
                "side": side,
                "cross_idx": idx,
                "cross_ts": row["timestamp"],
                "atr_at_cross": atr,
                "ema_slow_at_cross": ema_slow,
                "dist_to_slow_atr": dist,
                "threshold_ok": int(bool(threshold_ok)),
                "threshold_idx": float(threshold_idx) if threshold_idx is not None else np.nan,
                "retest_idx": float(retest_idx) if retest_idx is not None else np.nan,
                "retest_ts": bars.iloc[retest_idx]["timestamp"] if retest_idx is not None else pd.NaT,
            }
        )
    return pd.DataFrame(rows)


def filtered_events(events: pd.DataFrame, variant: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    out = events.copy()
    if variant == "raw_cross":
        out["signal_idx"] = out["cross_idx"]
    elif variant == "threshold_005":
        out = out[out["threshold_ok"] == 1].copy()
        out["signal_idx"] = out["threshold_idx"]
    elif variant == "retest_hold":
        out = out[out["retest_idx"].notna()].copy()
        out["signal_idx"] = out["retest_idx"]
    else:
        raise ValueError(variant)
    out["signal_idx"] = out["signal_idx"].astype(int)
    out["variant"] = variant
    return out.sort_values(["signal_idx", "cross_idx"]).reset_index(drop=True)


def simulate_events(bars: pd.DataFrame, variant_events: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    if variant_events.empty:
        nav = pd.DataFrame([{"asset": bars.iloc[0]["asset"], "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": 1.0}])
        return pd.DataFrame(), nav

    cost_rate = float(cost_bps_per_side) / 10000.0
    trades = []
    nav_rows = [{"asset": bars.iloc[0]["asset"], "variant": variant, "timestamp": bars.iloc[0]["timestamp"], "nav": 1.0}]
    nav = 1.0
    last_exit_idx = -1

    for _, event in variant_events.iterrows():
        signal_idx = int(event["signal_idx"])
        if signal_idx <= last_exit_idx:
            continue
        entry_idx = signal_idx + 1
        if entry_idx >= len(bars):
            continue
        side = str(event["side"])
        atr = float(bars.iloc[signal_idx]["atr"]) if pd.notna(bars.iloc[signal_idx]["atr"]) else float(event["atr_at_cross"])
        entry_price = float(bars.iloc[entry_idx]["open"])
        if side not in {"long", "short"} or not math.isfinite(atr) or atr <= 0 or not math.isfinite(entry_price) or entry_price <= 0:
            continue

        stop_price = entry_price - STOP_ATR * atr if side == "long" else entry_price + STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr if side == "long" else entry_price - TARGET_ATR * atr
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, len(bars) - 1)
        exit_idx = None
        exit_price = None
        exit_reason = None

        for idx in range(entry_idx, last_bar_idx + 1):
            probe = bars.iloc[idx]
            low = float(probe["low"])
            high = float(probe["high"])
            if side == "long":
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
            else:
                if high >= stop_price:
                    exit_idx = idx
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if low <= target_price:
                    exit_idx = idx
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break

        if exit_idx is None:
            exit_idx = last_bar_idx
            exit_price = float(bars.iloc[exit_idx]["close"])
            exit_reason = "time_stop"

        gross_mult = exit_price / entry_price if side == "long" else entry_price / exit_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        trades.append(
            {
                "asset": bars.iloc[0]["asset"],
                "variant": variant,
                "side": side,
                "cross_ts": pd.to_datetime(event["cross_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_ts": bars.iloc[signal_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": bars.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": bars.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_delay_bars": int(signal_idx - int(event["cross_idx"])),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "dist_to_slow_atr": float(event["dist_to_slow_atr"]),
                "gross_ret": gross_mult - 1.0,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
                "cost_bps_per_side": float(cost_bps_per_side),
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
                "trades": 0,
                "win_rate": np.nan,
                "avg_net_ret": np.nan,
                "median_net_ret": np.nan,
                "total_return": 0.0,
                "max_drawdown": 0.0,
                "avg_signal_delay_bars": np.nan,
                "avg_hold_bars": np.nan,
                "mean_dist_to_slow_atr": np.nan,
                "no_trade_ratio": no_trade_ratio,
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
            "trades": int(len(trades)),
            "win_rate": float(trades["win"].mean()),
            "avg_net_ret": float(trades["net_ret"].mean()),
            "median_net_ret": float(trades["net_ret"].median()),
            "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
            "max_drawdown": max_dd,
            "avg_signal_delay_bars": float(trades["signal_delay_bars"].mean()),
            "avg_hold_bars": float(trades["hold_bars"].mean()),
            "mean_dist_to_slow_atr": float(trades["dist_to_slow_atr"].mean()),
            "no_trade_ratio": no_trade_ratio,
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
            mean_signal_delay_bars=("avg_signal_delay_bars", "mean"),
            mean_no_trade_ratio=("no_trade_ratio", "mean"),
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


def run_parameter_grid() -> pd.DataFrame:
    rows = []
    for threshold in THRESHOLDS:
        asset_rows = []
        for asset, symbol in ASSETS.items():
            bars = prepare_bars(asset, symbol)
            events = build_events(bars, threshold=threshold)
            variant_name = f"threshold_{int(round(threshold * 100)):03d}"
            accepted = events[events["threshold_ok"] == 1].copy()
            if not accepted.empty:
                accepted["signal_idx"] = accepted["threshold_idx"].astype(int)
                accepted["variant"] = variant_name
            trades, nav = simulate_events(bars, accepted, variant_name, PRIMARY_COST)
            asset_rows.append(summarize_trades(trades, nav, events, asset, variant_name, PRIMARY_COST))
        agg = build_overall_summary(pd.concat(asset_rows, ignore_index=True))
        if agg.empty:
            continue
        row = agg.iloc[0].to_dict()
        row["threshold"] = threshold
        row["label"] = variant_name
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
        {"gate": "positive_neighbor_floor", "status": "pass" if positive >= 3 else "fail", "actual": f"{positive}/{len(grid)} threshold configs positive", "threshold": ">= 3 positive neighbors", "why_it_matters": "小阈值邻域别一碰就碎。"},
        {"gate": "cross_asset_neighbor_floor", "status": "pass" if stable_assets >= 3 else "fail", "actual": f"{stable_assets}/{len(grid)} keep >=2/3 positive assets", "threshold": ">= 3 configs keep cross-asset floor", "why_it_matters": "不能只靠单点 lucky pocket。"},
        {"gate": "trade_count_neighbor_floor", "status": "pass" if min_trades >= 5 else "fail", "actual": f"min trades across neighbors = {int(min_trades)}", "threshold": ">= 5 per asset", "why_it_matters": "参数稳定性也需要最小交易数。"},
        {"gate": "worst_neighbor_watch", "status": "watch" if float(worst['mean_total_return']) <= -0.01 else "pass", "actual": f"{worst['label']} mean_total_return={pct(worst['mean_total_return'])}", "threshold": "ideally > -1.00%", "why_it_matters": "最差近邻若明显翻负，说明仍偏 sample-bound。"},
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


def build_cost_trade_stability(overall_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    hit = overall_summary[overall_summary["variant"] == variant].copy()
    if hit.empty:
        return pd.DataFrame(columns=cols)
    at20 = hit[hit["cost_bps_per_side"] == 20.0]
    at20_val = float(at20.iloc[0]["mean_total_return"]) if not at20.empty else np.nan
    cost_positive = int((hit["mean_total_return"] > 0).sum())
    return pd.DataFrame([
        {"gate": "cost_survival_floor", "status": "pass" if cost_positive >= 2 else "fail", "actual": f"{cost_positive}/{len(hit)} cost levels positive", "threshold": ">= 2 positive cost levels", "why_it_matters": "轻量摩擦后不能立刻归零。"},
        {"gate": "trade_count_floor", "status": "pass" if int(hit['min_trades'].min()) >= 5 else "fail", "actual": f"min trades across cost ladder = {int(hit['min_trades'].min())}", "threshold": ">= 5 per asset", "why_it_matters": "trade count 过薄就不配继续推广。"},
        {"gate": "20bps_watch", "status": "watch" if pd.notna(at20_val) and at20_val <= 0 else "pass", "actual": pct(at20_val) if pd.notna(at20_val) else "-", "threshold": "ideally > 0% @ 20bps", "why_it_matters": "20bps 不是硬门槛，但能看出是否只在轻摩擦下存活。"},
    ], columns=cols)


def choose_candidate_variant(overall_summary: pd.DataFrame) -> str:
    hit = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    if hit.empty:
        return PRIMARY_VARIANT
    ranked = hit.sort_values(["mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"], ascending=[False, False, True])
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
    headline = "hard verdict：EMA 保护阈值 / retest 候选当前更像 `park / evidence pool`，暂不进入 paper candidate pool。"
    if float(winner_row["mean_total_return"]) > 0 and float(winner_row["positive_asset_ratio"]) >= 2 / 3 and not fail_sets:
        verdict_tag = "paper candidate"
        headline = f"hard verdict：EMA 保护层候选的 {winner} 已通过最小 clean replication + Light Stability Pack，可进入 `paper candidate pool`。"
    bullets = []
    for variant in ["raw_cross", "threshold_005", "retest_hold"]:
        hit = primary[primary["variant"] == variant]
        if not hit.empty:
            row = hit.iloc[0]
            bullets.append(f"{variant}：mean_total_return {pct(row['mean_total_return'])}，positive_asset_ratio {pct(row['positive_asset_ratio'])}，mean_no_trade_ratio {pct(row['mean_no_trade_ratio'])}。")
    bullets.append("两条轻量诚实守门已通过：规则能明确写成 trade on / trade off；当前实现只用当下 bar 的 EMA / ATR / retest，不用 future label。")
    bullets.append(f"当前 Light Stability Pack 硬 fail 位：{', '.join(fail_sets) if fail_sets else '无硬 fail'}。")
    if float(winner_row["mean_no_trade_ratio"]) > 0.75:
        bullets.append("winner 的 no_trade_ratio 已很高，因此即便 headline 不差，也要防止把‘少做交易’误写成保护优势。")
    if verdict_tag == "park":
        bullets.append("因此这条线当前只配留在 EMA 保护层证据池，不该抢占新的 paper wiring。")
    else:
        bullets.append(f"因此当前最诚实的 desk call 是：把 {winner} 推进到窄范围 `paper candidate pool`，而不是继续停在 digest wording。")
    return headline, bullets, verdict_tag, winner


def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_stability: pd.DataFrame, parameter_stability: pd.DataFrame, cross_asset_stability: pd.DataFrame, cost_trade_stability: pd.DataFrame, parameter_grid: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    headline, bullets, _, winner = derive_verdict(overall_summary, time_stability, parameter_stability, cross_asset_stability, cost_trade_stability)
    meta = meta_df.iloc[0].to_dict() if not meta_df.empty else {}
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)
    summary_table = render_table(
        overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST][["variant", "assets_tested", "positive_assets", "positive_asset_ratio", "mean_total_return", "mean_trades", "mean_no_trade_ratio", "mean_signal_delay_bars"]],
        percent_cols={"positive_asset_ratio", "mean_total_return", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1, "mean_signal_delay_bars": 2},
    )
    asset_table = render_table(
        asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST) & (asset_summary["variant"] == winner)][["asset", "trades", "total_return", "win_rate", "no_trade_ratio"]],
        percent_cols={"total_return", "win_rate", "no_trade_ratio"},
        digits_cols={"trades": 0},
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
    grid_table = render_table(parameter_grid[["label", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]] if not parameter_grid.empty else parameter_grid, percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"}, digits_cols={"mean_trades": 1})

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · EMA shielding · clean replication</title>
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
  <h1>Scout Seat · EMA shielding / retest hold · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(str(meta.get('generated_at_utc', '-')))} ｜ 这页把 De Angelis et al. (2021) 的“裸 EMA 不一定差，但保护层更擅长压回撤”压成 15m crypto 最小 clean replication。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>本轮 clean replication 口径</h2>
    <ul>
      <li>样本：<code>Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD</code></li>
      <li>规则：<code>EMA20/EMA50 cross</code> 为 baseline，保护层只允许加 <code>distance-to-EMA50 threshold</code> 或 <code>retest_hold</code></li>
      <li>trade on：出现 EMA cross，且满足对应保护层</li>
      <li>trade off：不满足保护层则 no-trade</li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side</code></li>
      <li>spec：<code>{escape(str(SPEC_PATH.relative_to(ROOT)) if SPEC_PATH.exists() else '-')}</code></li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate（6bps/side）</h2>
    {summary_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_ema_shielding_15m/overall_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>winner per-asset（6bps/side）</h2>
    {asset_table}
    <p class="muted">这里把 <code>no_trade_ratio</code> 单独外显，避免把“少做交易”误写成保护层增量。</p>
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
    <h2>threshold neighbor grid</h2>
    {grid_table}
    <p class="muted">这张表只看 EMA-slow 距离阈值的小邻域，防止把单点阈值 pocket 写成保护层优势。</p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>这条线不是给当前 EMA Paper Seat 直接换人，而是更快回答：保护阈值 / retest_hold 能不能成为下一条 EMA-family scout 候选。</li>
      <li>若 winner 只是靠 no-trade_ratio 飙升才站住，就应该直接 <code>park</code>。</li>
      <li>这页服务的是 Scout 快筛 verdict：<code>park / paper candidate</code>，不是直接去争 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    spec_df = pd.DataFrame([
        {"candidate_id": "scout_ema_shielding_15m_v1", "source_paper": "De Angelis et al. (2021)", "sample": "Binance 120d / 15m / BTC+ETH+SOL", "baseline": "EMA20/EMA50 cross", "variants": "raw_cross|threshold_005|retest_hold", "threshold_unit": "abs(close-EMA50)/ATR", "execution": "next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side", "honesty_gate": "no lookahead / no repaint / no future label"}
    ])
    spec_df.to_csv(SPEC_PATH, index=False)

    all_events = []
    all_trades = []
    all_nav = []
    all_summaries = []

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        events = build_events(bars, threshold=PRIMARY_THRESHOLD)
        if not events.empty:
            all_events.append(events)
        for variant in PRIMARY_LABELS:
            variant_events = filtered_events(events, variant)
            for cost in COSTS:
                trades, nav = simulate_events(bars, variant_events, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                if not nav.empty:
                    all_nav.append(nav)
                all_summaries.append(summarize_trades(trades, nav, variant_events, asset, variant, cost))

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
        {"generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "candidate_id": "scout_ema_shielding_15m_v1", "winner_variant": winner, "verdict_tag": verdict_tag, "verdict": verdict_headline, "sample_window": "Binance 120d / 15m / BTC+ETH+SOL", "next_step": "若为 park，则继续切去更高边际价值的新 Scout intake；若为 paper candidate，则下一轮只补最小 candidate-pool writeback。"}
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
    print("[ok] ema shielding clean replication generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
