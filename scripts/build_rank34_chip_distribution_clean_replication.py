#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from momentum.factors.chip_distribution import ChipConfig, estimate_chip_distribution_panel

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank34_chip_distribution_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank34_chip_distribution_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
ANCHORS = {
    "conservative": 288,
    "neutral": 96,
    "aggressive": 32,
}
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
VARIANTS = [
    "raw_baseline",
    "chip_cost_reclaim",
    "chip_cost_reclaim_plus_winner_ratio",
]
PRIMARY_VARIANT = "chip_cost_reclaim"
PRIMARY_HOLD_BARS = 8
FALSE_RECLAIM_LOOKAHEAD = 4
WINNER_RECOVER_THRESHOLD = 0.55
WINNER_RECOVER_LOOKBACK_MIN = 0.48


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
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["symbol"] = asset
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def load_panel() -> tuple[pd.DataFrame, dict[str, float]]:
    frames = []
    median_volume = {}
    for asset, symbol in ASSETS.items():
        bars = load_cached_bars(symbol, asset)
        frames.append(bars[["timestamp", "symbol", "asset", "open", "high", "low", "close", "volume"]])
        median_volume[asset] = float(bars["volume"].median())
    panel = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    return panel, median_volume


def build_anchor_chip_summary(panel: pd.DataFrame, median_volume: dict[str, float]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    for anchor_name, multiplier in ANCHORS.items():
        shares_map = {asset: median_volume[asset] * multiplier for asset in ASSETS}
        _, _, summary = estimate_chip_distribution_panel(
            panel[["timestamp", "symbol", "open", "high", "low", "close", "volume"]],
            config=ChipConfig(),
            shares_by_symbol=shares_map,
        )
        summary["timestamp"] = pd.to_datetime(summary["timestamp"], utc=True)
        summary["anchor"] = anchor_name
        summary["synthetic_shares"] = summary["symbol"].map(shares_map)
        out[anchor_name] = summary
    return out


def build_frame(asset_bars: pd.DataFrame, chip_summary: pd.DataFrame) -> pd.DataFrame:
    frame = asset_bars.merge(
        chip_summary[["timestamp", "symbol", "avg_cost", "cost_p50", "winner_ratio", "trapped_ratio", "turnover", "synthetic_shares"]],
        on=["timestamp", "symbol"],
        how="left",
    ).sort_values("timestamp").reset_index(drop=True)

    frame["ema20_15m"] = frame["close"].ewm(span=20, adjust=False).mean()
    frame["ema50_15m"] = frame["close"].ewm(span=50, adjust=False).mean()

    hourly = frame.set_index("timestamp")["close"].resample("1h").last().dropna().to_frame("close_1h").reset_index()
    hourly["ema20_1h"] = hourly["close_1h"].ewm(span=20, adjust=False).mean()
    hourly["ema50_1h"] = hourly["close_1h"].ewm(span=50, adjust=False).mean()
    hourly["ema20_slope_1h"] = hourly["ema20_1h"].pct_change()
    frame = pd.merge_asof(
        frame.sort_values("timestamp"),
        hourly[["timestamp", "close_1h", "ema20_1h", "ema50_1h", "ema20_slope_1h"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    frame["bias_long"] = (frame["ema20_1h"] > frame["ema50_1h"]) & (frame["ema20_slope_1h"] > 0)
    frame["bias_short"] = (frame["ema20_1h"] < frame["ema50_1h"]) & (frame["ema20_slope_1h"] < 0)

    frame["chip_band_top"] = frame[["avg_cost", "cost_p50"]].max(axis=1)
    frame["chip_band_bottom"] = frame[["avg_cost", "cost_p50"]].min(axis=1)
    frame["winner_ratio_roll_min4"] = frame["winner_ratio"].rolling(4, min_periods=1).min().shift(1)
    frame["trapped_ratio_roll_min4"] = frame["trapped_ratio"].rolling(4, min_periods=1).min().shift(1)

    frame["raw_baseline_long"] = (
        frame["bias_long"]
        & (frame["close"].shift(1) <= frame["ema20_15m"].shift(1))
        & (frame["close"] > frame["ema20_15m"])
    ).fillna(False)
    frame["raw_baseline_short"] = (
        frame["bias_short"]
        & (frame["close"].shift(1) >= frame["ema20_15m"].shift(1))
        & (frame["close"] < frame["ema20_15m"])
    ).fillna(False)

    frame["chip_cost_reclaim_long"] = (
        frame["bias_long"]
        & (frame["close"].shift(1) <= frame["chip_band_top"].shift(1))
        & (frame["close"] > frame["chip_band_top"])
    ).fillna(False)
    frame["chip_cost_reclaim_short"] = (
        frame["bias_short"]
        & (frame["close"].shift(1) >= frame["chip_band_bottom"].shift(1))
        & (frame["close"] < frame["chip_band_bottom"])
    ).fillna(False)

    frame["chip_cost_reclaim_plus_winner_ratio_long"] = (
        frame["chip_cost_reclaim_long"]
        & (frame["winner_ratio"] >= WINNER_RECOVER_THRESHOLD)
        & (frame["winner_ratio_roll_min4"] <= WINNER_RECOVER_LOOKBACK_MIN)
    ).fillna(False)
    frame["chip_cost_reclaim_plus_winner_ratio_short"] = (
        frame["chip_cost_reclaim_short"]
        & (frame["trapped_ratio"] >= WINNER_RECOVER_THRESHOLD)
        & (frame["trapped_ratio_roll_min4"] <= WINNER_RECOVER_LOOKBACK_MIN)
    ).fillna(False)
    return frame


def get_signal(frame: pd.DataFrame, idx: int, variant: str) -> tuple[int, float] | None:
    row = frame.iloc[idx]
    if variant == "raw_baseline":
        if bool(row["raw_baseline_long"]):
            return 1, float(row["ema20_15m"])
        if bool(row["raw_baseline_short"]):
            return -1, float(row["ema20_15m"])
    elif variant == "chip_cost_reclaim":
        if bool(row["chip_cost_reclaim_long"]):
            return 1, float(row["chip_band_top"])
        if bool(row["chip_cost_reclaim_short"]):
            return -1, float(row["chip_band_bottom"])
    elif variant == "chip_cost_reclaim_plus_winner_ratio":
        if bool(row["chip_cost_reclaim_plus_winner_ratio_long"]):
            return 1, float(row["chip_band_top"])
        if bool(row["chip_cost_reclaim_plus_winner_ratio_short"]):
            return -1, float(row["chip_band_bottom"])
    else:
        raise ValueError(f"unknown variant: {variant}")
    return None


def detect_false_reclaim(frame: pd.DataFrame, signal_idx: int, direction: int, ref_level: float) -> int:
    for step in range(1, FALSE_RECLAIM_LOOKAHEAD + 1):
        j = signal_idx + step
        if j >= len(frame):
            break
        close = float(frame.iloc[j]["close"])
        if not math.isfinite(close):
            continue
        if direction > 0 and close < ref_level:
            return 1
        if direction < 0 and close > ref_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, anchor: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    last_exit = -1
    eligible_bars = int((frame["bias_long"] | frame["bias_short"]).sum())
    signals_seen = 0

    for idx in range(1, len(frame) - PRIMARY_HOLD_BARS - 1):
        if idx <= last_exit:
            continue
        signal = get_signal(frame, idx, variant)
        if signal is None:
            continue
        direction, ref_level = signal
        signals_seen += 1
        entry_idx = idx + 1
        exit_idx = min(entry_idx + PRIMARY_HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        false_reclaim = detect_false_reclaim(frame, idx, direction, ref_level)
        rows.append(
            {
                "asset": asset,
                "anchor": anchor,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_idx": int(idx),
                "event_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "false_reclaim_ratio": int(false_reclaim),
                "turnover": float(frame.iloc[idx]["turnover"]) if not pd.isna(frame.iloc[idx]["turnover"]) else np.nan,
                "winner_ratio": float(frame.iloc[idx]["winner_ratio"]) if not pd.isna(frame.iloc[idx]["winner_ratio"]) else np.nan,
                "trapped_ratio": float(frame.iloc[idx]["trapped_ratio"]) if not pd.isna(frame.iloc[idx]["trapped_ratio"]) else np.nan,
                "synthetic_shares": float(frame.iloc[idx]["synthetic_shares"]) if not pd.isna(frame.iloc[idx]["synthetic_shares"]) else np.nan,
            }
        )
        last_exit = exit_idx

    trades = pd.DataFrame(rows)
    no_trade_ratio = 1.0 if eligible_bars == 0 else max(0.0, 1.0 - (signals_seen / eligible_bars))
    return trades, no_trade_ratio, eligible_bars


def summarize_asset(trades: pd.DataFrame, *, asset: str, anchor: str, variant: str, cost_bps: float, no_trade_ratio: float, eligible_bars: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "anchor": anchor,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "total_return": 0.0,
            "false_reclaim_ratio": np.nan,
            "no_trade_ratio": float(no_trade_ratio),
            "eligible_bias_bars": int(eligible_bars),
            "avg_turnover": np.nan,
            "avg_winner_ratio": np.nan,
            "avg_trapped_ratio": np.nan,
        }
    return {
        "asset": asset,
        "anchor": anchor,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "median_net_ret": float(trades["net_ret"].median()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "false_reclaim_ratio": float(trades["false_reclaim_ratio"].mean()),
        "no_trade_ratio": float(no_trade_ratio),
        "eligible_bias_bars": int(eligible_bars),
        "avg_turnover": float(trades["turnover"].mean()),
        "avg_winner_ratio": float(trades["winner_ratio"].mean()),
        "avg_trapped_ratio": float(trades["trapped_ratio"].mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (anchor, variant, cost), grp in asset_summary.groupby(["anchor", "variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "anchor": anchor,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
                "median_total_return": float(np.nanmedian(total_returns)) if len(total_returns) else np.nan,
                "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
                "mean_trades": float(grp["trades"].mean()),
                "mean_false_reclaim_ratio": float(grp["false_reclaim_ratio"].mean()),
                "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
                "mean_turnover": float(grp["avg_turnover"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_assumption_sensitivity(overall: pd.DataFrame) -> pd.DataFrame:
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if focus.empty:
        return pd.DataFrame()
    focus = focus.sort_values("anchor").reset_index(drop=True)
    best = focus["mean_total_return"].max()
    worst = focus["mean_total_return"].min()
    focus["return_gap_vs_best"] = best - focus["mean_total_return"]
    focus["survives_min_cross_asset"] = focus["positive_asset_ratio"] >= (2.0 / 3.0)
    focus["survives_min_return"] = focus["mean_total_return"] > 0
    focus["survives_min_trade_count"] = focus["mean_trades"] >= 60
    focus["survives_min_false_reclaim"] = focus["mean_false_reclaim_ratio"] <= 0.40
    meta = pd.DataFrame(
        [
            {
                "anchor": "range_summary",
                "variant": PRIMARY_VARIANT,
                "cost_bps_per_side": float(PRIMARY_COST),
                "mean_total_return": float(best - worst),
                "median_total_return": np.nan,
                "positive_asset_ratio": np.nan,
                "mean_trades": np.nan,
                "mean_false_reclaim_ratio": np.nan,
                "mean_no_trade_ratio": np.nan,
                "mean_win_rate": np.nan,
                "mean_turnover": np.nan,
                "return_gap_vs_best": float(best - worst),
                "survives_min_cross_asset": np.nan,
                "survives_min_return": np.nan,
                "survives_min_trade_count": np.nan,
                "survives_min_false_reclaim": np.nan,
            }
        ]
    )
    return pd.concat([focus, meta], ignore_index=True)


def build_verdict(overall: pd.DataFrame, assumption: pd.DataFrame) -> tuple[str, str]:
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if focus.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以站住。"
    focus = focus.sort_values("anchor").reset_index(drop=True)
    all_positive = bool((focus["mean_total_return"] > 0).all())
    all_cross_asset = bool((focus["positive_asset_ratio"] >= (2.0 / 3.0)).all())
    all_trade_count = bool((focus["mean_trades"] >= 60).all())
    all_false_reclaim_ok = bool((focus["mean_false_reclaim_ratio"] <= 0.40).all())
    return_range = float(focus["mean_total_return"].max() - focus["mean_total_return"].min())
    if all_positive and all_cross_asset and all_trade_count and all_false_reclaim_ok and return_range <= 0.10:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没直接塌掉：主变体在三档 synthetic shares anchor 下都保持成本后为正、跨标的不只剩单腿，而且 false reclaim 也没一起炸开。"
    strongest_anchor = focus.sort_values("mean_total_return", ascending=False).iloc[0]
    weakest_anchor = focus.sort_values("mean_total_return", ascending=True).iloc[0]
    return (
        "park / evidence pool",
        f"最强 pocket 只出现在 `{strongest_anchor['anchor']}` anchor（mean_total_return≈{pct(strongest_anchor['mean_total_return'])}，positive_asset_ratio≈{pct(strongest_anchor['positive_asset_ratio'])}），但一旦把 synthetic shares 收紧到 `{weakest_anchor['anchor']}`，主变体就掉到 mean_total_return≈{pct(weakest_anchor['mean_total_return'])}、positive_asset_ratio≈{pct(weakest_anchor['positive_asset_ratio'])}。这说明当前 edge 对 shares / turnover 假设过于敏感，不够诚实地进入 paper candidate pool。",
    )


def update_reading_report(verdict: str, generated_at: str, overall: pd.DataFrame) -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    start = text.find('<h2>Rank 34 · chip-distribution：fresh intake</h2>')
    if start == -1:
        return
    card_start = text.rfind('<div class="card">', 0, start)
    card_end = text.find('</div>', start)
    if card_start == -1 or card_end == -1:
        return
    card_end += len('</div>')

    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    conservative = focus[focus["anchor"] == "conservative"]
    neutral = focus[focus["anchor"] == "neutral"]
    aggressive = focus[focus["anchor"] == "aggressive"]
    cons_text = "-" if conservative.empty else f"{pct(conservative.iloc[0]['mean_total_return'])} / {pct(conservative.iloc[0]['positive_asset_ratio'])}"
    neu_text = "-" if neutral.empty else f"{pct(neutral.iloc[0]['mean_total_return'])} / {pct(neutral.iloc[0]['positive_asset_ratio'])}"
    agg_text = "-" if aggressive.empty else f"{pct(aggressive.iloc[0]['mean_total_return'])} / {pct(aggressive.iloc[0]['positive_asset_ratio'])}"

    new_card = f'''<div class="card">
  <h2>Rank 34 · chip-distribution：clean replication</h2>
  <p>这轮没有继续围着旧 P3 做近义 wiring，而是按上轮约束把 <code>Rank 34</code> 真推进到 1 次带 <code>synthetic shares / turnover anchor</code> 的最小 clean replication：<a href="rank34_chip_distribution_source_intake.html">source intake</a> ｜ <a href="rank34_chip_distribution_clean_replication.html">clean replication</a>。</p>
  <ul>
    <li><b>只回答了什么：</b>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，只比较 <code>raw_baseline / chip_cost_reclaim / chip_cost_reclaim_plus_winner_ratio</code>，先回答 <code>post_cost_return / trade_count / assumption_sensitivity / false_reclaim_ratio</code>。</li>
    <li><b>主变体：</b><code>{PRIMARY_VARIANT}</code>；6bps/side 下三档 anchor 分别约为：conservative = <code>{cons_text}</code>，neutral = <code>{neu_text}</code>，aggressive = <code>{agg_text}</code>（格式 = mean_total_return / positive_asset_ratio）。</li>
    <li><b>当前 verdict：</b><code>{escape(verdict)}</code>。</li>
    <li><b>为什么没升格：</b>最强 pocket 主要留在更宽松的 synthetic shares 假设里；一旦 shares anchor 收紧，跨标的存活与成本后收益都会明显塌掉，说明这条线当前更像 assumptions-sensitive evidence，而不是可诚实推进的 paper candidate。</li>
    <li><b>下一轮约束：</b>除非 bot2 明确点名或出现新的 genuinely verdict-changing 证据，否则默认应把它压回 <code>park / evidence pool</code>，并把 Scout 主资源切回下一条新的 repo-based 5m/15m crypto intake。</li>
    <li><b>时间戳：</b>{escape(generated_at)}</li>
  </ul>
</div>'''
    text = text[:card_start] + new_card + text[card_end:]
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, assumption: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    focus = focus.sort_values("anchor").reset_index(drop=True)

    def row_for(anchor: str) -> pd.Series | None:
        rows = focus[focus["anchor"] == anchor]
        return None if rows.empty else rows.iloc[0]

    conservative = row_for("conservative")
    neutral = row_for("neutral")
    aggressive = row_for("aggressive")
    stats_line = (
        f"主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下的 assumption ladder 为："
        f"`conservative -> mean_total_return≈{pct(conservative['mean_total_return']) if conservative is not None else '-'} / positive_asset_ratio≈{pct(conservative['positive_asset_ratio']) if conservative is not None else '-'} / mean_trades≈{num(conservative['mean_trades'],1) if conservative is not None else '-'}`；"
        f"`neutral -> mean_total_return≈{pct(neutral['mean_total_return']) if neutral is not None else '-'} / positive_asset_ratio≈{pct(neutral['positive_asset_ratio']) if neutral is not None else '-'} / mean_trades≈{num(neutral['mean_trades'],1) if neutral is not None else '-'}`；"
        f"`aggressive -> mean_total_return≈{pct(aggressive['mean_total_return']) if aggressive is not None else '-'} / positive_asset_ratio≈{pct(aggressive['positive_asset_ratio']) if aggressive is not None else '-'} / mean_trades≈{num(aggressive['mean_trades'],1) if aggressive is not None else '-'}`。"
    )
    old_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 34` 这轮先落 `fresh intake only`，下一轮若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则默认只允许给它做 1 次带 `synthetic shares / turnover anchor` 诚实门槛的最小 clean replication，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32 / Rank 33`。**"
    new_summary = f"**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 34` 的最小 clean replication 已如实落地，当前 hard verdict = **`{verdict}`**。{stats_line} 这说明当前不应继续围着 `Rank 34` 做近义 admission copy；若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则默认应切回下一条新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32 / Rank 33`。**"
    if old_summary in text:
        text = text.replace(old_summary, new_summary, 1)

    old_rank_block = "34. `Rank 34 chip-distribution trapped-holder reclaim / winner-ratio gate`（repo `chip_distribution.py` + `docs/CHIP_DISTRIBUTION.md`）→ **`fresh intake only / admit_to_clean_replication_queue_with_assumption_gate`**\n    - 这轮先完成 `source intake`，不偷跑 clean replication：当前更诚实的读法不是宣称筹码分布已经可交易，而是把它压成一条 **repo-based support / reclaim** 候补，并明确把 `shares / turnover` 假设当成第一优先的诚实门槛。\n    - 冻结后的 intake 规则：`trade on = higher_tf bias 同向，且价格在一次 pullback 后重新站回估算 cost_p50 / avg_cost 带上方，同时 winner_ratio 从拥挤区下缘回升到阈值之上`；`trade off = 价格始终站不回 cost 带、winner_ratio 不恢复，或 trapped_ratio 继续抬升导致所谓 reclaim 只是拥挤反弹`。\n    - 当前 hard verdict：**`fresh intake only / admit_to_clean_replication_queue_with_assumption_gate`**。更直白地说：它值得拿 1 轮预算，但下一轮必须先回答 `synthetic shares 假设一改，结论会不会直接翻脸`；若答案是会，就应直接 `park / evidence pool`。\n    - 下一轮默认只允许做 1 次最小 clean replication：固定复用 `BTC/ETH/SOL 120d 15m` cache，先设 3 档 `synthetic shares / turnover anchors`，比较 `raw baseline / chip_cost_reclaim / chip_cost_reclaim_plus_winner_ratio`，优先回答 `post_cost_return / trade_count / assumption_sensitivity / false_reclaim_ratio`。\n    - 网页落点：`reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html`。"
    new_rank_block = (
        f"34. `Rank 34 chip-distribution trapped-holder reclaim / winner-ratio gate`（repo `chip_distribution.py` + `docs/CHIP_DISTRIBUTION.md`）→ **`{verdict}`**\n"
        "    - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `raw_baseline`、`chip_cost_reclaim`、`chip_cost_reclaim_plus_winner_ratio`，不追新 bar，也不扩成完整 stability pack。\n"
        "    - 冻结后的 clean-room 规则：`raw_baseline = higher_tf bias 同向 + 15m pullback 后重新站回 EMA20`；`chip_cost_reclaim = 在前者基础上，把 reclaim 参考从 EMA20 换成估算的 cost_p50 / avg_cost 带`；`chip_cost_reclaim_plus_winner_ratio = 再要求 winner_ratio（空头看 trapped_ratio）从拥挤区下缘恢复到阈值之上`。\n"
        f"    - 当前最诚实的主证据：{stats_line}\n"
        f"    - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：筹码分布这条线当前最大的风险不是 repaint，而是 **shares / turnover 假设一收紧，edge 就明显缩水甚至翻负**；因此它已不再只是 `admit_to_clean_replication_queue_with_assumption_gate`，而是应先压回 evidence pool。\n"
        "    - 网页落点：`reports/site/factors/scout_rank34_chip_distribution_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html`。"
    )
    if old_rank_block in text:
        text = text.replace(old_rank_block, new_rank_block, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, assumption: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy()
    headline = "主变体没有形成可用样本。"
    if not focus.empty:
        best = focus.sort_values("mean_total_return", ascending=False).iloc[0]
        worst = focus.sort_values("mean_total_return", ascending=True).iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 6bps/side 下最强 pocket 来自 {best['anchor']} anchor："
            f"mean_total_return≈{pct(best['mean_total_return'])}、positive_asset_ratio≈{pct(best['positive_asset_ratio'])}；"
            f"但最弱的 {worst['anchor']} anchor 已掉到 mean_total_return≈{pct(worst['mean_total_return'])}、positive_asset_ratio≈{pct(worst['positive_asset_ratio'])}。"
        )
    overall_view = overall.copy()
    if not overall_view.empty:
        overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    if not asset_view.empty:
        asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    assumption_view = assumption.copy()
    if not assumption_view.empty:
        assumption_view["cost_bps_per_side"] = assumption_view["cost_bps_per_side"].fillna(PRIMARY_COST)
        assumption_view["cost_bps_per_side"] = assumption_view["cost_bps_per_side"].astype(int)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 34 · chip-distribution clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="../../reading/trendline_alpha_scout/report.html">← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 34 · chip-distribution trapped-holder reclaim / winner-ratio gate</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 assumption-gated repo fast verdict</p>

  <div class="card">
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三档最小规则：<code>raw_baseline</code>、<code>chip_cost_reclaim</code>、<code>chip_cost_reclaim_plus_winner_ratio</code>。</li>
      <li>只跑三档 <code>synthetic shares / turnover anchors</code>：<code>conservative = median_volume × 288</code>、<code>neutral = × 96</code>、<code>aggressive = × 32</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>trade_count</code>、<code>assumption_sensitivity</code>、<code>false_reclaim_ratio</code>。</li>
    </ul>
  </div>

  <div class="card">
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>raw_baseline：</b>higher-tf bias 同向，且 15m 价格在一次 pullback 后重新站回 <code>EMA20</code>。</li>
      <li><b>chip_cost_reclaim：</b>在前者基础上，把 reclaim 参考从 <code>EMA20</code> 换成估算的 <code>cost_p50 / avg_cost</code> 带。</li>
      <li><b>chip_cost_reclaim_plus_winner_ratio：</b>在 <code>chip_cost_reclaim</code> 基础上，再要求 <code>winner_ratio</code>（空头看 <code>trapped_ratio</code>）从拥挤区下缘恢复到阈值之上。</li>
      <li><b>诚实边界：</b>这里的 “chip” 不是链上真实持仓账本，而是由 <code>volume / synthetic shares</code> 递推出来的成本带近似；因此最关键的不是再加更多稳定性检查，而是先看它会不会被 shares 假设本身推翻。</li>
    </ul>
  </div>

  <div class="card">
    <h2>hard verdict</h2>
    <p><span class="pill">{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class="muted">{escape(verdict_reason)}</p>
  </div>

  <div class="card">
    <h2>assumption sensitivity（主变体 6bps）</h2>
    {render_table(assumption_view[["anchor","variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","return_gap_vs_best","survives_min_cross_asset","survives_min_return","survives_min_trade_count","survives_min_false_reclaim"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","return_gap_vs_best"}, digits_cols={"mean_trades":1})}
  </div>

  <div class="card">
    <h2>跨资产总表</h2>
    {render_table(overall_view[["anchor","variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class="card">
    <h2>分资产摘要</h2>
    {render_table(asset_view[["anchor","asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","avg_turnover"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate"}, digits_cols={"trades":0,"avg_turnover":4})}
  </div>

  <div class="card">
    <h2>artifact</h2>
    <ul>
      <li><a href="../../../artifacts/scout_rank34_chip_distribution_15m/overall_summary.csv">overall_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank34_chip_distribution_15m/asset_summary.csv">asset_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank34_chip_distribution_15m/assumption_sensitivity_summary.csv">assumption_sensitivity_summary.csv</a></li>
      <li><a href="../../../artifacts/scout_rank34_chip_distribution_15m/primary_trades_6bps.csv">primary_trades_6bps.csv</a></li>
      <li><a href="../../../reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html">source intake card</a></li>
    </ul>
  </div>
</body>
</html>
'''


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    panel, median_volume = load_panel()
    chip_by_anchor = build_anchor_chip_summary(panel, median_volume)

    asset_rows = []
    all_trades = []
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for anchor, chip_summary in chip_by_anchor.items():
        for asset in ASSETS:
            asset_bars = panel[panel["symbol"] == asset].copy().reset_index(drop=True)
            asset_chip = chip_summary[chip_summary["symbol"] == asset].copy().reset_index(drop=True)
            frame = build_frame(asset_bars, asset_chip)
            frame.to_csv(ART_DIR / f"{anchor}_{asset.lower().replace('-usd','')}_frame.csv", index=False)
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, no_trade_ratio, eligible_bars = build_trades(frame, asset, anchor, variant, cost)
                    if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                        trades.to_csv(ART_DIR / f"primary_6bps_{anchor}_{asset.lower().replace('-usd','')}.csv", index=False)
                    all_trades.append(trades)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            anchor=anchor,
                            variant=variant,
                            cost_bps=cost,
                            no_trade_ratio=no_trade_ratio,
                            eligible_bars=eligible_bars,
                        )
                    )

    non_empty = [df for df in all_trades if not df.empty]
    all_trades_df = pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    primary_trades = pd.DataFrame()
    if not all_trades_df.empty:
        primary_trades = all_trades_df[
            (all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)
        ].copy()
    primary_trades.to_csv(ART_DIR / "primary_trades_6bps.csv", index=False)

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    assumption = build_assumption_sensitivity(overall)
    verdict, verdict_reason = build_verdict(overall, assumption)

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    assumption.to_csv(ART_DIR / "assumption_sensitivity_summary.csv", index=False)
    pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at,
                "candidate_id": "rank34_chip_distribution_15m",
                "hard_verdict": verdict,
                "verdict_reason": verdict_reason,
            }
        ]
    ).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, assumption, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank34_chip_distribution_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report(verdict, generated_at, overall)
    update_todo(verdict, generated_at, overall, assumption)

    print(f"verdict={verdict}")
    focus = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not focus.empty:
        print("primary_anchor_stats", focus.to_dict(orient="records"))


if __name__ == "__main__":
    main()
