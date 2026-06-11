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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_ema_plateau_consensus_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_ema_plateau_consensus_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
META_PATH = ART_DIR / "clean_replication_meta.csv"
SUMMARY_PATH = ART_DIR / "clean_replication_summary.csv"
ASSET_SUMMARY_PATH = ART_DIR / "clean_replication_asset_summary.csv"
TRADES_PATH = ART_DIR / "clean_replication_trades.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability.csv"
PARAM_STABILITY_PATH = ART_DIR / "parameter_stability.csv"
CROSS_ASSET_PATH = ART_DIR / "cross_asset_stability.csv"
COST_STABILITY_PATH = ART_DIR / "cost_trade_stability.csv"
PAPER_CANDIDATE_PATH = ART_DIR / "paper_candidate_admission_memo.csv"
SIGNAL_SNAPSHOT_PATH = ART_DIR / "signal_snapshot.csv"

FASTS = [8, 10, 12]
SLOWS = [34, 40, 50]
PAIRS = [(f, s) for f in FASTS for s in SLOWS if f < s]
ATR_PERIOD = 14
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
TIME_BUCKETS = 3
SPREAD_THRESHOLDS = [0.0010, 0.0020, 0.0030]
VOTE_THRESHOLDS = [4, 5, 6]

PRIMARY_VARIANT = "plateau_vote_5of9_spread_guard"
VARIANTS = [
    "anchor_10_40",
    "row_consensus_2of3",
    "plateau_vote_5of9",
    "plateau_vote_5of9_spread_guard",
]


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
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
    bars = load_cached_bars(symbol, asset).copy()
    bars["atr"] = compute_atr(bars)
    for fast, slow in PAIRS:
        fast_col = f"ema_{fast}"
        slow_col = f"ema_{slow}"
        if fast_col not in bars:
            bars[fast_col] = bars["close"].ewm(span=fast, adjust=False).mean()
        if slow_col not in bars:
            bars[slow_col] = bars["close"].ewm(span=slow, adjust=False).mean()
        spread_col = f"spread_{fast}_{slow}"
        bars[spread_col] = (bars[fast_col] - bars[slow_col]) / bars["close"].replace(0, np.nan)
        bars[f"vote_{fast}_{slow}"] = (bars[spread_col] > 0).astype(int)

    vote_cols = [f"vote_{fast}_{slow}" for fast, slow in PAIRS]
    spread_cols = [f"spread_{fast}_{slow}" for fast, slow in PAIRS]
    bars["long_votes_9"] = bars[vote_cols].sum(axis=1)
    bars["median_norm_spread_9"] = bars[spread_cols].median(axis=1)
    bars["row_votes_slow40"] = bars[[f"vote_{fast}_40" for fast in FASTS]].sum(axis=1)
    return bars



def build_signal_snapshot(bars: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tail = bars.tail(12).copy()
    for _, row in tail.iterrows():
        rows.append(
            {
                "timestamp": row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "asset": row["asset"],
                "close": float(row["close"]),
                "long_votes_9": int(row["long_votes_9"]),
                "row_votes_slow40": int(row["row_votes_slow40"]),
                "median_norm_spread_9": float(row["median_norm_spread_9"]),
                "anchor_10_40_on": int(row["vote_10_40"]),
                "row_consensus_2of3_on": int(row["row_votes_slow40"] >= 2),
                "plateau_vote_5of9_on": int(row["long_votes_9"] >= 5),
                "plateau_vote_5of9_spread_guard_on": int((row["long_votes_9"] >= 5) and (row["median_norm_spread_9"] >= 0.0020)),
            }
        )
    return pd.DataFrame(rows)



def variant_signal(bars: pd.DataFrame, variant: str) -> pd.Series:
    if variant == "anchor_10_40":
        return (bars["vote_10_40"] == 1).astype(int)
    if variant == "row_consensus_2of3":
        return (bars["row_votes_slow40"] >= 2).astype(int)
    if variant == "plateau_vote_5of9":
        return (bars["long_votes_9"] >= 5).astype(int)
    if variant == "plateau_vote_5of9_spread_guard":
        return ((bars["long_votes_9"] >= 5) & (bars["median_norm_spread_9"] >= 0.0020)).astype(int)
    if variant.startswith("plateau_vote_") and variant.endswith("of9"):
        threshold = int(variant.split("_")[2].replace("of9", ""))
        return (bars["long_votes_9"] >= threshold).astype(int)
    if variant.startswith("plateau_vote_5of9_spread_"):
        code = variant.rsplit("_", 1)[-1]
        threshold = float(f"0.{code}")
        return ((bars["long_votes_9"] >= 5) & (bars["median_norm_spread_9"] >= threshold)).astype(int)
    raise ValueError(variant)



def simulate_variant(bars: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    signal = variant_signal(bars, variant).astype(int).to_numpy()
    timestamps = bars["timestamp"].to_numpy()
    opens = bars["open"].to_numpy(dtype=float)
    highs = bars["high"].to_numpy(dtype=float)
    lows = bars["low"].to_numpy(dtype=float)
    closes = bars["close"].to_numpy(dtype=float)
    atrs = bars["atr"].to_numpy(dtype=float)
    votes = bars["long_votes_9"].to_numpy(dtype=int)
    spreads = bars["median_norm_spread_9"].to_numpy(dtype=float)
    asset = str(bars.iloc[0]["asset"])
    cost_rate = float(cost_bps_per_side) / 10000.0
    position = 0
    entry_idx = None
    entry_price = None
    entry_atr = None
    trades = []
    nav = 1.0
    nav_rows = [{"asset": asset, "variant": variant, "timestamp": timestamps[0], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)}]

    for idx in range(len(bars) - 1):
        if position == 0:
            prev_sig = int(signal[idx - 1]) if idx > 0 else 0
            if prev_sig == 0 and int(signal[idx]) == 1:
                atr = float(atrs[idx])
                entry_open = float(opens[idx + 1])
                if math.isfinite(atr) and atr > 0 and math.isfinite(entry_open) and entry_open > 0:
                    position = 1
                    entry_idx = idx + 1
                    entry_price = entry_open
                    entry_atr = atr
            continue

        assert entry_idx is not None and entry_price is not None and entry_atr is not None
        stop_price = entry_price - STOP_ATR * entry_atr
        target_price = entry_price + TARGET_ATR * entry_atr
        exit_reason = None
        exit_price = None
        exit_idx = idx

        if lows[idx] <= stop_price:
            exit_reason = "atr_stop"
            exit_price = stop_price
        elif highs[idx] >= target_price:
            exit_reason = "atr_target"
            exit_price = target_price
        elif int(signal[idx]) == 0:
            exit_reason = "signal_off"
            exit_price = float(closes[idx])
        elif (idx - entry_idx + 1) >= TIME_STOP_BARS:
            exit_reason = "time_stop"
            exit_price = float(closes[idx])

        if exit_reason is None:
            continue

        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        vote_idx = entry_idx - 1 if entry_idx > 0 else entry_idx
        trades.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "entry_ts": pd.Timestamp(timestamps[entry_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.Timestamp(timestamps[exit_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "hold_bars": int(exit_idx - entry_idx + 1),
                "entry_votes": int(votes[vote_idx]),
                "entry_median_norm_spread": float(spreads[vote_idx]),
                "gross_ret": float(gross_mult - 1.0),
                "net_ret": float(net_ret),
                "win": int(net_ret > 0),
                "exit_reason": exit_reason,
            }
        )
        nav_rows.append({"asset": asset, "variant": variant, "timestamp": timestamps[exit_idx], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)})
        position = 0
        entry_idx = None
        entry_price = None
        entry_atr = None

    if position == 1 and entry_idx is not None and entry_price is not None:
        exit_idx = len(bars) - 1
        exit_price = float(closes[exit_idx])
        gross_mult = exit_price / entry_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        vote_idx = entry_idx - 1 if entry_idx > 0 else entry_idx
        trades.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps_per_side),
                "entry_ts": pd.Timestamp(timestamps[entry_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.Timestamp(timestamps[exit_idx]).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": float(entry_price),
                "exit_price": float(exit_price),
                "hold_bars": int(exit_idx - entry_idx + 1),
                "entry_votes": int(votes[vote_idx]),
                "entry_median_norm_spread": float(spreads[vote_idx]),
                "gross_ret": float(gross_mult - 1.0),
                "net_ret": float(net_ret),
                "win": int(net_ret > 0),
                "exit_reason": "forced_close",
            }
        )
        nav_rows.append({"asset": asset, "variant": variant, "timestamp": timestamps[exit_idx], "nav": nav, "cost_bps_per_side": float(cost_bps_per_side)})

    transitions = int(np.sum((np.r_[0, signal[:-1]] == 0) & (signal == 1)))
    stats = {
        "signal_on_ratio": float(signal.mean()),
        "no_trade_ratio": float(1.0 - signal.mean()),
        "candidate_entries": transitions,
    }
    return pd.DataFrame(trades), pd.DataFrame(nav_rows), stats



def summarize_trades(trades: pd.DataFrame, nav: pd.DataFrame, stats: dict, asset: str, variant: str, cost: float) -> dict:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "avg_hold_bars": np.nan,
            "mean_entry_votes": np.nan,
            "mean_entry_median_norm_spread": np.nan,
            "no_trade_ratio": float(stats["no_trade_ratio"]),
            "signal_on_ratio": float(stats["signal_on_ratio"]),
            "candidate_entries": int(stats["candidate_entries"]),
        }
    running_peak = nav["nav"].cummax() if not nav.empty else pd.Series(dtype=float)
    drawdown = nav["nav"] / running_peak - 1.0 if not nav.empty else pd.Series(dtype=float)
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "trades": int(len(trades)),
        "win_rate": float(trades["win"].mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "median_net_ret": float(trades["net_ret"].median()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "max_drawdown": max_dd,
        "avg_hold_bars": float(trades["hold_bars"].mean()),
        "mean_entry_votes": float(trades["entry_votes"].mean()),
        "mean_entry_median_norm_spread": float(trades["entry_median_norm_spread"].mean()),
        "no_trade_ratio": float(stats["no_trade_ratio"]),
        "signal_on_ratio": float(stats["signal_on_ratio"]),
        "candidate_entries": int(stats["candidate_entries"]),
    }



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
            mean_hold_bars=("avg_hold_bars", "mean"),
            mean_entry_votes=("mean_entry_votes", "mean"),
            mean_entry_median_norm_spread=("mean_entry_median_norm_spread", "mean"),
            mean_no_trade_ratio=("no_trade_ratio", "mean"),
            mean_signal_on_ratio=("signal_on_ratio", "mean"),
            mean_candidate_entries=("candidate_entries", "mean"),
        )
        .sort_values(["cost_bps_per_side", "mean_total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out



def build_time_stability(bars_by_asset: dict[str, pd.DataFrame], variant: str) -> pd.DataFrame:
    rows = []
    for asset, bars in bars_by_asset.items():
        n = len(bars)
        chunk = n // TIME_BUCKETS
        for i in range(TIME_BUCKETS):
            start = i * chunk
            end = (i + 1) * chunk if i < TIME_BUCKETS - 1 else n
            part = bars.iloc[start:end].reset_index(drop=True)
            if len(part) < 80:
                continue
            trades, nav, stats = simulate_variant(part, variant, PRIMARY_COST)
            rows.append(summarize_trades(trades, nav, stats, asset, variant, PRIMARY_COST) | {"time_bucket": f"bucket_{i+1}"})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df[["asset", "time_bucket", "trades", "total_return", "win_rate", "no_trade_ratio"]]



def build_parameter_stability(bars_by_asset: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    parameter_variants = [f"plateau_vote_{k}of9" for k in VOTE_THRESHOLDS] + [f"plateau_vote_5of9_spread_{int(t * 10000):04d}" for t in SPREAD_THRESHOLDS]
    for variant in parameter_variants:
        asset_rows = []
        for asset, bars in bars_by_asset.items():
            trades, nav, stats = simulate_variant(bars, variant, PRIMARY_COST)
            asset_rows.append(summarize_trades(trades, nav, stats, asset, variant, PRIMARY_COST))
        asset_df = pd.DataFrame(asset_rows)
        rows.append(
            {
                "variant": variant,
                "mean_total_return": float(asset_df["total_return"].mean()),
                "positive_asset_ratio": float((asset_df["total_return"] > 0).mean()),
                "mean_trades": float(asset_df["trades"].mean()),
                "mean_no_trade_ratio": float(asset_df["no_trade_ratio"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["mean_total_return", "positive_asset_ratio", "mean_trades"], ascending=[False, False, False]).reset_index(drop=True)



def build_cross_asset_stability(asset_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    hit = asset_summary[(asset_summary["variant"] == variant) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if hit.empty:
        return hit
    return hit[["asset", "trades", "total_return", "win_rate", "no_trade_ratio", "mean_entry_votes", "mean_entry_median_norm_spread"]].sort_values("asset").reset_index(drop=True)



def build_cost_trade_stability(overall_summary: pd.DataFrame, variant: str) -> pd.DataFrame:
    hit = overall_summary[overall_summary["variant"] == variant].copy()
    if hit.empty:
        return hit
    return hit[["variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio"]].sort_values("cost_bps_per_side").reset_index(drop=True)



def derive_verdict(overall_summary: pd.DataFrame, parameter_df: pd.DataFrame, time_df: pd.DataFrame, cross_df: pd.DataFrame, cost_df: pd.DataFrame) -> tuple[str, str, list[str]]:
    primary = overall_summary[(overall_summary["variant"] == PRIMARY_VARIANT) & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    anchor = overall_summary[(overall_summary["variant"] == "anchor_10_40") & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty or anchor.empty:
        return "park", "当前缺少可读 aggregate clean replication，保守读作 park。", ["主变体或 anchor 汇总缺失。"]

    p = primary.iloc[0]
    a = anchor.iloc[0]
    cost10 = cost_df[cost_df["cost_bps_per_side"] == 10.0]
    cost10_ret = float(cost10.iloc[0]["mean_total_return"]) if not cost10.empty else float("nan")
    positive_buckets = float((time_df["total_return"] > 0).mean()) if not time_df.empty else 0.0
    positive_neighbors = float((parameter_df["mean_total_return"] > 0).mean()) if not parameter_df.empty else 0.0
    cross_positive = float((cross_df["total_return"] > 0).mean()) if not cross_df.empty else 0.0

    bullets = [
        f"主变体 plateau_vote_5of9_spread_guard 在 6bps/side 下跨资产 mean_total_return={pct(p['mean_total_return'])}，positive_asset_ratio={pct(p['positive_asset_ratio'])}，mean_trades={num(p['mean_trades'], 1)}，mean_no_trade_ratio={pct(p['mean_no_trade_ratio'])}。",
        f"anchor_10_40 对照在同口径下 mean_total_return={pct(a['mean_total_return'])}，positive_asset_ratio={pct(a['positive_asset_ratio'])}；用来防止把‘更少交易’误写成 plateau 增量。",
        f"最小诚实检查：trade on / trade off 已冻结；实现只使用当下 bar 的 EMA vote、median spread 与 ATR，不用 future label，因此没有显式 lookahead / repaint。",
    ]

    is_paper_candidate = (
        float(p["mean_total_return"]) > 0
        and float(p["positive_asset_ratio"]) >= (2 / 3)
        and float(p["mean_total_return"]) > float(a["mean_total_return"])
        and float(p["positive_asset_ratio"]) >= float(a["positive_asset_ratio"])
        and float(p["mean_no_trade_ratio"]) <= 0.80
        and math.isfinite(cost10_ret)
        and cost10_ret > 0
        and positive_buckets >= (4 / 9)
        and positive_neighbors >= 0.5
        and cross_positive >= (2 / 3)
    )
    if is_paper_candidate:
        headline = "当前 EMA neighborhood consensus 已通过最小 clean replication + Light Stability Pack admission，可进入 paper candidate pool，但暂不升 narrow paper pilot。"
        return "paper_candidate", headline, bullets

    headline = "当前 EMA neighborhood consensus 更诚实的读法仍是 park / evidence pool，不进入 paper candidate pool。"
    if float(p["mean_no_trade_ratio"]) > 0.80:
        bullets.append("主变体 no_trade_ratio 已超过 80%，即使表面回报不差，也更像是稀疏持仓，而不是可靠 plateau 稳定性。")
    if float(p["mean_total_return"]) <= float(a["mean_total_return"]):
        bullets.append("主变体没有比单点 anchor_10_40 更好，说明当前看不到清晰的邻域稳定增量。")
    if cross_positive < (2 / 3):
        bullets.append("跨标的正资产占比仍不足 2/3，不能把单一币种 pocket 写成 paper candidate。")
    if math.isfinite(cost10_ret) and cost10_ret <= 0:
        bullets.append("10bps/side 已不能存活，说明 plateau 版本对轻摩擦仍偏脆弱。")
    return "park", headline, bullets



def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, time_df: pd.DataFrame, parameter_df: pd.DataFrame, cross_df: pd.DataFrame, cost_df: pd.DataFrame, meta_df: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = meta_df.iloc[0]
    bullets = [meta["evidence_line_1"], meta["evidence_line_2"], meta["evidence_line_3"], meta["evidence_line_4"]]
    bullets_html = "".join(f"<li>{escape(str(x))}</li>" for x in bullets if str(x).strip())
    summary_table = render_table(
        overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST][["variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_no_trade_ratio", "mean_entry_votes"]],
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1, "mean_entry_votes": 2},
    )
    asset_table = render_table(
        cross_df,
        percent_cols={"total_return", "win_rate", "no_trade_ratio"},
        digits_cols={"trades": 0, "mean_entry_votes": 2, "mean_entry_median_norm_spread": 4},
    )
    time_table = render_table(
        time_df,
        percent_cols={"total_return", "win_rate", "no_trade_ratio"},
        digits_cols={"trades": 0},
    )
    param_table = render_table(
        parameter_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"mean_trades": 1},
    )
    cost_table = render_table(
        cost_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_no_trade_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1},
    )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · EMA plateau consensus · clean replication</title>
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
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · EMA plateau consensus · 15m crypto clean replication</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ 这页把 Rank 18 从 clean-room spec 推到最小 clean replication + Light Stability Pack。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['hard_verdict']))}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>本轮固定口径</h2>
    <ul>
      <li>样本：<code>Binance 120d / 15m / BTC-USD + ETH-USD + SOL-USD</code></li>
      <li>规则：比较 <code>anchor_10_40 / row_consensus_2of3 / plateau_vote_5of9 / plateau_vote_5of9_spread_guard</code></li>
      <li>trade on：对应 EMA 邻域票数达到阈值；trade off：票数回落，或 spread_guard 不足</li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | signal_off close | 6bps/side</code></li>
      <li>spec：<code>{escape(str(SPEC_PATH.relative_to(ROOT)) if SPEC_PATH.exists() else '-')}</code></li>
    </ul>
  </div>

  <div class="card">
    <h2>aggregate clean replication（6bps/side）</h2>
    {summary_table}
    <p class="muted">重点同时看 <code>mean_total_return</code>、<code>positive_asset_ratio</code> 与 <code>mean_no_trade_ratio</code>，避免把“少做交易”误读成平台稳定性。</p>
  </div>

  <div class="card">
    <h2>跨标的稳定性（winner @ 6bps/side）</h2>
    {asset_table}
  </div>

  <div class="card">
    <h2>时间稳定性</h2>
    {time_table}
  </div>

  <div class="card">
    <h2>参数稳定性（plateau 邻域）</h2>
    {param_table}
  </div>

  <div class="card">
    <h2>成本 / 交易数稳定性</h2>
    {cost_table}
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li>这条线服务的是 <code>Scout Seat</code>：回答 EMA 在 15m crypto 上是单点 lucky，还是邻域真有稳定平台。</li>
      <li>若 plateau 版本既没比单点 anchor 更好，又主要靠 no-trade_ratio 飙升，那就该直接 <code>park</code>。</li>
      <li>若它只是勉强达到 <code>paper candidate</code>，下一轮也只该补最小 monitoring / refresh 准备，不该立刻抢 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding="utf-8")



def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    bars_by_asset = {asset: prepare_bars(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_snapshots = [build_signal_snapshot(bars) for bars in bars_by_asset.values()]

    summary_rows = []
    trades_list = []
    nav_list = []
    for asset, bars in bars_by_asset.items():
        for variant in VARIANTS:
            for cost in COSTS:
                trades, nav, stats = simulate_variant(bars, variant, cost)
                if not trades.empty:
                    trades_list.append(trades)
                if not nav.empty:
                    nav_list.append(nav)
                summary_rows.append(summarize_trades(trades, nav, stats, asset, variant, cost))

    asset_summary = pd.DataFrame(summary_rows)
    overall_summary = build_overall_summary(asset_summary)
    cross_df = build_cross_asset_stability(asset_summary, PRIMARY_VARIANT)
    time_df = build_time_stability(bars_by_asset, PRIMARY_VARIANT)
    parameter_df = build_parameter_stability(bars_by_asset)
    cost_df = build_cost_trade_stability(overall_summary, PRIMARY_VARIANT)
    verdict_tag, verdict, bullets = derive_verdict(overall_summary, parameter_df, time_df, cross_df, cost_df)

    trades_df = pd.concat(trades_list, ignore_index=True) if trades_list else pd.DataFrame()
    nav_df = pd.concat(nav_list, ignore_index=True) if nav_list else pd.DataFrame()
    signal_snapshot_df = pd.concat(signal_snapshots, ignore_index=True) if signal_snapshots else pd.DataFrame()

    primary = overall_summary[(overall_summary["variant"] == PRIMARY_VARIANT) & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    anchor = overall_summary[(overall_summary["variant"] == "anchor_10_40") & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)]
    cost10 = cost_df[cost_df["cost_bps_per_side"] == 10.0]
    cost20 = cost_df[cost_df["cost_bps_per_side"] == 20.0]
    paper_candidate_df = pd.DataFrame([
        {
            "candidate_id": "scout_ema_plateau_consensus_15m_v1",
            "verdict": verdict_tag,
            "primary_variant": PRIMARY_VARIANT,
            "aggregate_total_return_6bps": float(primary.iloc[0]["mean_total_return"]) if not primary.empty else np.nan,
            "anchor_total_return_6bps": float(anchor.iloc[0]["mean_total_return"]) if not anchor.empty else np.nan,
            "positive_asset_ratio_6bps": float(primary.iloc[0]["positive_asset_ratio"]) if not primary.empty else np.nan,
            "mean_trades_6bps": float(primary.iloc[0]["mean_trades"]) if not primary.empty else np.nan,
            "mean_no_trade_ratio_6bps": float(primary.iloc[0]["mean_no_trade_ratio"]) if not primary.empty else np.nan,
            "aggregate_total_return_10bps": float(cost10.iloc[0]["mean_total_return"]) if not cost10.empty else np.nan,
            "aggregate_total_return_20bps": float(cost20.iloc[0]["mean_total_return"]) if not cost20.empty else np.nan,
            "next_gate": "若 verdict=park，则切去下一条更高边际值 Scout 候选；若 verdict=paper_candidate，则下一轮只补最小 monitoring / refresh seed，不回到大范围 wording 打磨。",
        }
    ])
    meta_df = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "scout_ema_plateau_consensus_15m_v1",
            "desk_role": "Scout fast lane / EMA neighborhood stability candidate",
            "hard_verdict": verdict,
            "verdict_tag": verdict_tag,
            "evidence_line_1": bullets[0] if len(bullets) > 0 else "",
            "evidence_line_2": bullets[1] if len(bullets) > 1 else "",
            "evidence_line_3": bullets[2] if len(bullets) > 2 else "",
            "evidence_line_4": bullets[3] if len(bullets) > 3 else "",
        }
    ])

    overall_summary.to_csv(SUMMARY_PATH, index=False)
    asset_summary.to_csv(ASSET_SUMMARY_PATH, index=False)
    trades_df.to_csv(TRADES_PATH, index=False)
    nav_df.to_csv(ART_DIR / "clean_replication_nav.csv", index=False)
    time_df.to_csv(TIME_STABILITY_PATH, index=False)
    parameter_df.to_csv(PARAM_STABILITY_PATH, index=False)
    cross_df.to_csv(CROSS_ASSET_PATH, index=False)
    cost_df.to_csv(COST_STABILITY_PATH, index=False)
    paper_candidate_df.to_csv(PAPER_CANDIDATE_PATH, index=False)
    meta_df.to_csv(META_PATH, index=False)
    signal_snapshot_df.to_csv(SIGNAL_SNAPSHOT_PATH, index=False)
    write_report(overall_summary, asset_summary, time_df, parameter_df, cross_df, cost_df, meta_df)
    print("[ok] ema plateau consensus clean replication generated")
    print("[artifact]", SUMMARY_PATH)
    print("[site]", REPORT_PATH)
    print(meta_df.iloc[0]["hard_verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
