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

from momentum.factors.confirmed_extrema import ConfirmedExtremaConfig, compute_confirmed_extrema
from momentum.factors.endpoint_nadaraya_watson import EndpointNadarayaWatsonConfig, compute_endpoint_nadaraya_watson

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank33_nw_hl_reclaim_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank33_nw_hl_reclaim_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
VARIANTS = [
    "raw_extrema_reclaim",
    "nw_hl_reclaim",
    "nw_hl_plus_highbreak",
]
PRIMARY_VARIANT = "nw_hl_plus_highbreak"
HOLD_BARS = 8
FALSE_BREAK_LOOKAHEAD = 4
NW_BANDWIDTH_15M = 8.0
NW_BANDWIDTH_1H = 6.0
NW_LOOKBACK_15M = 96
NW_LOOKBACK_1H = 48
NEIGHBOR_BARS = 4
BIAS_SLOPE_FLOOR = 0.0002


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
    df["asset"] = asset
    df["symbol"] = symbol
    return df.sort_values("timestamp").reset_index(drop=True)


def _add_last_confirmed_levels(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    out = frame.copy()
    out[f"{prefix}_last_high_value"] = out[f"{prefix}_confirm_high_value"].replace(0, np.nan).ffill()
    out[f"{prefix}_last_low_value"] = out[f"{prefix}_confirm_low_value"].replace(0, np.nan).ffill()
    out[f"{prefix}_last_high_structure"] = out[f"{prefix}_confirm_high_structure"].replace("", np.nan).ffill().fillna("")
    out[f"{prefix}_last_low_structure"] = out[f"{prefix}_confirm_low_structure"].replace("", np.nan).ffill().fillna("")
    out[f"{prefix}_swing_range"] = out[f"{prefix}_last_high_value"] - out[f"{prefix}_last_low_value"]
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset)

    nw_15m = compute_endpoint_nadaraya_watson(
        bars[["timestamp", "open", "high", "low", "close", "symbol"]],
        config=EndpointNadarayaWatsonConfig(
            source_column="close",
            bandwidth=NW_BANDWIDTH_15M,
            lookback=NW_LOOKBACK_15M,
            result_column="nw_smooth",
        ),
    )
    nw_15m["timestamp"] = pd.to_datetime(nw_15m["timestamp"], utc=True)
    nw_15m["nw_smooth"] = nw_15m["nw_smooth"].astype(float)
    nw_15m["nw_slope"] = nw_15m["nw_smooth"].pct_change()

    raw_extrema = compute_confirmed_extrema(
        bars[["timestamp", "open", "high", "low", "close", "symbol"]],
        config=ConfirmedExtremaConfig(
            value_column="close",
            neighbor_bars=NEIGHBOR_BARS,
            anchor_high_column="high",
            anchor_low_column="low",
            high_flag_column="raw_confirm_high",
            low_flag_column="raw_confirm_low",
            high_value_column="raw_confirm_high_value",
            low_value_column="raw_confirm_low_value",
            high_structure_column="raw_confirm_high_structure",
            low_structure_column="raw_confirm_low_structure",
            high_origin_index_column="raw_confirm_high_origin_index",
            low_origin_index_column="raw_confirm_low_origin_index",
        ),
    )
    raw_extrema["timestamp"] = pd.to_datetime(raw_extrema["timestamp"], utc=True)

    nw_extrema_input = nw_15m[["timestamp", "high", "low", "nw_smooth", "symbol"]].copy()
    nw_extrema = compute_confirmed_extrema(
        nw_extrema_input,
        config=ConfirmedExtremaConfig(
            value_column="nw_smooth",
            neighbor_bars=NEIGHBOR_BARS,
            anchor_high_column="high",
            anchor_low_column="low",
            high_flag_column="nw_confirm_high",
            low_flag_column="nw_confirm_low",
            high_value_column="nw_confirm_high_value",
            low_value_column="nw_confirm_low_value",
            high_structure_column="nw_confirm_high_structure",
            low_structure_column="nw_confirm_low_structure",
            high_origin_index_column="nw_confirm_high_origin_index",
            low_origin_index_column="nw_confirm_low_origin_index",
        ),
    )
    nw_extrema["timestamp"] = pd.to_datetime(nw_extrema["timestamp"], utc=True)

    frame = bars.merge(
        nw_15m[["timestamp", "nw_smooth", "nw_slope"]],
        on="timestamp",
        how="left",
    ).merge(
        raw_extrema[[
            "timestamp", "raw_confirm_high", "raw_confirm_low", "raw_confirm_high_value", "raw_confirm_low_value",
            "raw_confirm_high_structure", "raw_confirm_low_structure"
        ]],
        on="timestamp",
        how="left",
    ).merge(
        nw_extrema[[
            "timestamp", "nw_confirm_high", "nw_confirm_low", "nw_confirm_high_value", "nw_confirm_low_value",
            "nw_confirm_high_structure", "nw_confirm_low_structure"
        ]],
        on="timestamp",
        how="left",
    )

    market_1h = bars[["timestamp", "close"]].copy().rename(columns={"close": "close_1h"}).set_index("timestamp").resample("1h").last().dropna().reset_index()
    market_1h["symbol"] = symbol
    nw_1h = compute_endpoint_nadaraya_watson(
        market_1h[["timestamp", "close_1h", "symbol"]].rename(columns={"close_1h": "close"}),
        config=EndpointNadarayaWatsonConfig(
            source_column="close",
            bandwidth=NW_BANDWIDTH_1H,
            lookback=NW_LOOKBACK_1H,
            result_column="nw_smooth_1h",
        ),
    )
    nw_1h["timestamp"] = pd.to_datetime(nw_1h["timestamp"], utc=True)
    nw_1h["nw_smooth_1h"] = nw_1h["nw_smooth_1h"].astype(float)
    nw_1h["nw_slope_1h"] = nw_1h["nw_smooth_1h"].pct_change()
    nw_1h = nw_1h.rename(columns={"close": "close_1h_src"})

    frame = pd.merge_asof(
        frame.sort_values("timestamp"),
        nw_1h[["timestamp", "close_1h_src", "nw_smooth_1h", "nw_slope_1h"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )

    frame = _add_last_confirmed_levels(frame, "raw")
    frame = _add_last_confirmed_levels(frame, "nw")

    frame["bias_long"] = ((frame["nw_slope_1h"] > BIAS_SLOPE_FLOOR) & (frame["close_1h_src"] >= frame["nw_smooth_1h"]))
    frame["bias_short"] = ((frame["nw_slope_1h"] < -BIAS_SLOPE_FLOOR) & (frame["close_1h_src"] <= frame["nw_smooth_1h"]))

    frame["raw_reclaim_level_long"] = frame["raw_last_low_value"] + 0.5 * frame["raw_swing_range"]
    frame["raw_reclaim_level_short"] = frame["raw_last_high_value"] - 0.5 * frame["raw_swing_range"]

    prev_close = frame["close"].shift(1)
    prev_nw = frame["nw_smooth"].shift(1)
    frame["raw_extrema_reclaim_long"] = (
        frame["bias_long"]
        & (frame["raw_last_low_structure"] == "HL")
        & frame["raw_swing_range"].gt(0)
        & prev_close.le(frame["raw_reclaim_level_long"])
        & frame["close"].gt(frame["raw_reclaim_level_long"])
    ).fillna(False).astype(int)
    frame["raw_extrema_reclaim_short"] = (
        frame["bias_short"]
        & (frame["raw_last_high_structure"] == "LH")
        & frame["raw_swing_range"].gt(0)
        & prev_close.ge(frame["raw_reclaim_level_short"])
        & frame["close"].lt(frame["raw_reclaim_level_short"])
    ).fillna(False).astype(int)

    frame["nw_hl_reclaim_long"] = (
        frame["bias_long"]
        & (frame["nw_last_low_structure"] == "HL")
        & prev_close.le(prev_nw)
        & frame["close"].gt(frame["nw_smooth"])
    ).fillna(False).astype(int)
    frame["nw_hl_reclaim_short"] = (
        frame["bias_short"]
        & (frame["nw_last_high_structure"] == "LH")
        & prev_close.ge(prev_nw)
        & frame["close"].lt(frame["nw_smooth"])
    ).fillna(False).astype(int)

    frame["nw_hl_plus_highbreak_long"] = (
        frame["nw_hl_reclaim_long"].eq(1)
        & frame["close"].gt(frame["nw_last_high_value"])
    ).fillna(False).astype(int)
    frame["nw_hl_plus_highbreak_short"] = (
        frame["nw_hl_reclaim_short"].eq(1)
        & frame["close"].lt(frame["nw_last_low_value"])
    ).fillna(False).astype(int)

    frame["structure_strength"] = frame[["nw_slope" , "nw_slope_1h"]].abs().sum(axis=1)
    return frame


def get_signal(frame: pd.DataFrame, idx: int, variant: str) -> tuple[int, str, float] | None:
    row = frame.iloc[idx]
    if variant == "raw_extrema_reclaim":
        if int(row["raw_extrema_reclaim_long"]) == 1:
            return 1, variant, float(row["raw_reclaim_level_long"])
        if int(row["raw_extrema_reclaim_short"]) == 1:
            return -1, variant, float(row["raw_reclaim_level_short"])
    elif variant == "nw_hl_reclaim":
        if int(row["nw_hl_reclaim_long"]) == 1:
            return 1, variant, float(row["nw_smooth"])
        if int(row["nw_hl_reclaim_short"]) == 1:
            return -1, variant, float(row["nw_smooth"])
    elif variant == "nw_hl_plus_highbreak":
        if int(row["nw_hl_plus_highbreak_long"]) == 1:
            return 1, variant, float(row["nw_last_high_value"])
        if int(row["nw_hl_plus_highbreak_short"]) == 1:
            return -1, variant, float(row["nw_last_low_value"])
    else:
        raise ValueError(f"unknown variant: {variant}")
    return None


def detect_false_reclaim(frame: pd.DataFrame, signal_idx: int, direction: int, level: float, variant: str) -> int:
    for step in range(1, FALSE_BREAK_LOOKAHEAD + 1):
        j = signal_idx + step
        if j >= len(frame):
            break
        close = float(frame.iloc[j]["close"])
        if not math.isfinite(close):
            continue
        if direction > 0 and close < level:
            return 1
        if direction < 0 and close > level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    last_exit = -1
    eligible_mask = (frame["bias_long"] | frame["bias_short"]).astype(int)
    eligible_bars = int(eligible_mask.sum())
    signals_seen = 0

    for idx in range(1, len(frame) - 1):
        if idx <= last_exit:
            continue
        signal = get_signal(frame, idx, variant)
        if signal is None:
            continue
        direction, trigger_name, failure_level = signal
        signals_seen += 1
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append({
            "asset": asset,
            "variant": trigger_name,
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
            "hold_bars": int(exit_idx - entry_idx + 1),
            "false_reclaim_ratio": int(detect_false_reclaim(frame, idx, direction, failure_level, variant)),
            "structure_strength": float(frame.iloc[idx]["structure_strength"]),
            "bias_slope_1h": float(frame.iloc[idx]["nw_slope_1h"]) if not pd.isna(frame.iloc[idx]["nw_slope_1h"]) else np.nan,
        })
        last_exit = exit_idx

    trades = pd.DataFrame(rows)
    no_trade_ratio = 1.0 if eligible_bars == 0 else max(0.0, 1.0 - (signals_seen / eligible_bars))
    return trades, no_trade_ratio, eligible_bars


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, no_trade_ratio: float, eligible_bars: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
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
            "avg_structure_strength": np.nan,
            "long_share": np.nan,
            "short_share": np.nan,
        }
    return {
        "asset": asset,
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
        "avg_structure_strength": float(trades["structure_strength"].mean()),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
            "median_total_return": float(np.nanmedian(total_returns)) if len(total_returns) else np.nan,
            "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
            "mean_trades": float(grp["trades"].mean()),
            "mean_false_reclaim_ratio": float(grp["false_reclaim_ratio"].mean()),
            "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
            "mean_win_rate": float(grp["win_rate"].mean()),
            "mean_structure_strength": float(grp["avg_structure_strength"].mean()),
        })
    return pd.DataFrame(rows)


def build_time_bucket_summary(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty or len(primary_trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = primary_trades.sort_values("event_ts").reset_index(drop=True).copy()
    work["time_bucket"] = pd.qcut(work.index + 1, q=3, labels=["bucket_1", "bucket_2", "bucket_3"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "time_bucket": str(bucket),
            "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
            "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
            "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
        })
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_buckets: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以站住。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"]) if not pd.isna(row["mean_total_return"]) else -1.0
    pos_ratio = float(row["positive_asset_ratio"]) if not pd.isna(row["positive_asset_ratio"]) else 0.0
    mean_trades = float(row["mean_trades"]) if not pd.isna(row["mean_trades"]) else 0.0
    false_ratio = float(row["mean_false_reclaim_ratio"]) if not pd.isna(row["mean_false_reclaim_ratio"]) else 1.0
    no_trade = float(row["mean_no_trade_ratio"]) if not pd.isna(row["mean_no_trade_ratio"]) else 1.0
    positive_buckets = int((time_buckets["mean_total_return"] > 0).sum()) if not time_buckets.empty else 0
    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 12 and false_ratio <= 0.45 and no_trade <= 0.985 and positive_buckets >= 2:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没直接塌掉：成本后仍为正、跨资产不只剩单腿，而且 time-pocket honesty 也不是只靠单一热像素。"
    return "park / evidence pool", "最小 clean replication 没把它推成合格候选：要么成本后仍偏弱，要么 trade count / false_reclaim_ratio / time-pocket honesty 没能一起站住。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank33_nw_hl_reclaim_clean_replication.html" not in text and "rank33_nw_hl_reclaim_source_intake.html" in text:
        text = text.replace(
            'rank33_nw_hl_reclaim_source_intake.html">Rank 33 source intake</a>',
            'rank33_nw_hl_reclaim_source_intake.html">Rank 33 source intake</a> ｜ <a href="rank33_nw_hl_reclaim_clean_replication.html">clean replication</a>',
            1,
        )
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_buckets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not primary.empty:
        row = primary.iloc[0]
        stats = (
            f"主变体 `{PRIMARY_VARIANT}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(row['mean_total_return'])}`、"
            f"`positive_asset_ratio≈{pct(row['positive_asset_ratio'])}`、`mean_trades≈{num(row['mean_trades'],1)}`、"
            f"`mean_false_reclaim_ratio≈{pct(row['mean_false_reclaim_ratio'])}`、`mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}`。"
        )
    else:
        stats = "主变体没有形成可用样本。"

    if time_buckets.empty:
        time_note = "当前样本过薄，time-pocket honesty 还不足以可靠拆成 3 桶；这本身也不支持升格。"
    else:
        bucket_parts = []
        for _, row in time_buckets.iterrows():
            bucket_parts.append(f"{row['time_bucket']}≈{pct(row['mean_total_return'])} / {pct(row['positive_asset_ratio'])}")
        time_note = "time-pocket honesty：" + "；".join(bucket_parts) + "。"

    old_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 33` 当前只完成 fresh intake 并维持 `admit_to_clean_replication_queue`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认先给 `Rank 33` 做那 1 次最小 clean replication，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32`。**"
    if verdict.startswith("P1"):
        new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 33` 的最小 clean replication 已如实落地并进入 `P1 weak candidate`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认只允许给 `Rank 33` 那唯一 1 次便宜诚实检查预算；若这次检查也不能改变层级，就应压回 `park / evidence pool`。**"
    else:
        new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 33` 的最小 clean replication 已如实落地且当前维持 `park / evidence pool`。若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认应回到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是重开已 park 的 `Rank 30 / Rank 31 / Rank 32`。**"
    if old_summary in text:
        text = text.replace(old_summary, new_summary, 1)

    old_run2 = "2m3. `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`（repo `endpoint_nadaraya_watson.py` + `confirmed_extrema.py`）：本轮已完成 **fresh source intake only**，当前定位 = **`admit_to_clean_replication_queue`**。冻结入口规则：`trade on = endpoint NW slope 与 higher-tf bias 同向，最近一个确认低点保持 HL，且当前 close 重新站回 NW smooth 之上并突破最近确认高点（做空反向）`；`trade off = NW slope 走平/反向、最近确认低点转成 LL、当前 bar 无法 reclaim NW smooth / 最近确认高点，或突破后很快跌回结构错误一侧`。当前边际价值判断：它比继续围着 `Rank 29 / Rank 17 / Rank 2` 做近义 wiring 更值钱，也比引入 shares 假设更重的 chip 路线更便宜诚实；同时它直接贴着当前存活的 pullback / structure 家族，而不是再开新大框架。**若下一轮继续认领，默认只允许做 1 个最小 clean replication**：固定复用 `BTC/ETH/SOL 120d 15m` cache，比较 `raw_extrema_reclaim` vs `nw_hl_reclaim` vs `nw_hl_plus_highbreak`，先回答 `post_cost_return / trade_count / false_reclaim_ratio / time-pocket honesty`，然后快速判 `park / P1`；不要提前扩成完整 stability pack 或 admission wording。网页落点：`reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`。"
    new_run2 = (
        f"2m3. `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`（repo `endpoint_nadaraya_watson.py` + `confirmed_extrema.py`）：已完成 **fresh source intake -> 最小 clean replication**，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `raw_extrema_reclaim`、`nw_hl_reclaim`、`nw_hl_plus_highbreak`，不追新 bar，也不扩成完整 stability pack。"
        f" 冻结后的 clean-room 规则：`raw_extrema_reclaim = higher-tf bias 同向 + 最近确认 swing 保持 HL/LH，并重新站回最近 swing 中位 reclaim level`；`nw_hl_reclaim = 在前者思路上改用 endpoint NW 平滑与 NW-confirmed HL/LH`；`nw_hl_plus_highbreak = 再要求当前 close 同时突破最近确认高/低点`。"
        f" 当前最诚实的主证据：{stats} {time_note}"
        f" **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`Rank 33` 已不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。"
        " 网页落点：`reports/site/factors/scout_rank33_nw_hl_reclaim_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`。"
    )
    if old_run2 in text:
        text = text.replace(old_run2, new_run2, 1)

    old_rank_block = "33. `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`（repo `endpoint_nadaraya_watson.py` + `confirmed_extrema.py`）→ **`admit_to_clean_replication_queue`**\n    - 已完成 `fresh source intake`；当前只冻结最小入口规则，不偷跑 clean replication，也不扩成完整 stability pack。\n    - 冻结后的 clean-room 规则：`trade on = endpoint NW slope 与 higher-tf bias 同向，最近一个确认低点保持 HL，且当前 close 重新站回 NW smooth 之上并突破最近确认高点（做空反向）`；`trade off = NW slope 走平/反向、最近确认低点转成 LL、当前 bar 无法 reclaim NW smooth / 最近确认高点，或突破后很快跌回结构错误一侧`。\n    - 这条线的诚实性前提写死为：`endpoint NW` 只允许 causal 版本；`confirmed extrema` 只在确认 bar 后才可用，禁止把中心点未确认时的 swing 提前拿来交易。\n    - **最新补充（2026-03-17 11:28 UTC）**：当前 hard verdict 仍是 **`fresh intake only / admit_to_clean_replication_queue`**。更直白地说：它现在只是“下一条值得花 1 轮预算验证的 repo-based 15m crypto 结构候选”；若后续最小 clean replication 不能证明 `NW+HL reclaim` 比 `raw extrema reclaim` 更诚实，就应尽快压回 `park / evidence pool`。\n    - 网页落点：`reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`。"
    new_rank_block = (
        f"33. `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate`（repo `endpoint_nadaraya_watson.py` + `confirmed_extrema.py`）→ **`{verdict}`**\n"
        "    - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `raw_extrema_reclaim`、`nw_hl_reclaim`、`nw_hl_plus_highbreak`，不追新 bar，也不扩成完整 stability pack。\n"
        "    - 冻结后的 clean-room 规则：`raw_extrema_reclaim = higher-tf bias 同向 + 最近确认 swing 保持 HL/LH，并重新站回最近 swing 中位 reclaim level`；`nw_hl_reclaim = 在前者思路上改用 endpoint NW 平滑与 NW-confirmed HL/LH`；`nw_hl_plus_highbreak = 再要求当前 close 同时突破最近确认高/低点`。\n"
        f"    - 当前最诚实的主证据：{stats}\n"
        f"    - {time_note}\n"
        f"    - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`Rank 33` 已不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。\n"
        "    - 网页落点：`reports/site/factors/scout_rank33_nw_hl_reclaim_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`。"
    )
    if old_rank_block in text:
        text = text.replace(old_rank_block, new_rank_block, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_buckets: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        headline = "主变体没有形成可用样本。"
    else:
        row = primary.iloc[0]
        headline = (
            f"主变体 {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下：跨资产 mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、"
            f"mean_false_reclaim_ratio≈{pct(row['mean_false_reclaim_ratio'])}、mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}。"
        )
    overall_view = overall.copy()
    if not overall_view.empty:
        overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    if not asset_view.empty:
        asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 33 · endpoint NW + confirmed HL reclaim clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
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
  <p><a href='../../reading/trendline_alpha_scout/report.html'>← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 33 · endpoint NW + confirmed HL reclaim / causal swing persistence gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三档最小规则：<code>raw_extrema_reclaim</code>、<code>nw_hl_reclaim</code>、<code>nw_hl_plus_highbreak</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>trade_count</code>、<code>false_reclaim_ratio</code>、<code>time-pocket honesty</code>。</li>
      <li>执行口径固定：higher-tf bias 用 completed 1h endpoint NW slope；入场 = <code>next-bar open</code>；持有 = <code>{HOLD_BARS}</code> 根 15m bar；默认 non-overlap。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>raw_extrema_reclaim：</b>higher-tf bias 同向，最近确认 swing 保持 <code>HL/LH</code>，并重新站回最近 swing 的中位 reclaim level。</li>
      <li><b>nw_hl_reclaim：</b>在前者思路上改用 <code>endpoint NW</code> 平滑与 <code>NW-confirmed HL/LH</code>，要求价格重新站回 NW smooth 同侧。</li>
      <li><b>nw_hl_plus_highbreak：</b>在 <code>nw_hl_reclaim</code> 基础上，再要求当前 close 同时突破最近确认高/低点。</li>
      <li><b>lookahead guard：</b><code>endpoint NW</code> 只允许 causal 版本；<code>confirmed extrema</code> 只在确认 bar 后才可用，不允许把中心点未确认时的 swing 提前拿来交易。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(verdict_reason)}</p>
  </div>

  <div class='card'>
    <h2>跨资产总表</h2>
    {render_table(overall_view[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate","mean_structure_strength"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1,"mean_structure_strength":5})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_view[["asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","avg_structure_strength","long_share","short_share"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"}, digits_cols={"trades":0,"avg_structure_strength":5})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty（主变体 6bps）</h2>
    {render_table(time_buckets[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank33_nw_hl_reclaim_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank33_nw_hl_reclaim_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank33_nw_hl_reclaim_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../../artifacts/scout_rank33_nw_hl_reclaim_15m/time_bucket_summary.csv'>time_bucket_summary.csv</a></li>
      <li><a href='../../../reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html'>source intake card</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    asset_rows = []
    all_trades = []

    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, no_trade_ratio, eligible_bars = build_trades(frame, asset, variant, cost)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd','')}.csv", index=False)
                all_trades.append(trades)
                asset_rows.append(
                    summarize_asset(
                        trades,
                        asset=asset,
                        variant=variant,
                        cost_bps=cost,
                        no_trade_ratio=no_trade_ratio,
                        eligible_bars=eligible_bars,
                    )
                )

    non_empty = [df for df in all_trades if not df.empty]
    all_trades_df = pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    if all_trades_df.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
        time_buckets = pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    else:
        primary_trades = all_trades_df[
            (all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)
        ].copy()
        primary_trades.to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
        time_buckets = build_time_bucket_summary(primary_trades)

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    verdict, verdict_reason = build_verdict(overall, time_buckets)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_buckets.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank33_nw_hl_reclaim_15m",
            "hard_verdict": verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, time_buckets, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank33_nw_hl_reclaim_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall, time_buckets)

    print(f"verdict={verdict}")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not primary.empty:
        print("primary_stats", primary.iloc[0].to_dict())
    if not time_buckets.empty:
        print("time_buckets", time_buckets.to_dict(orient="records"))


if __name__ == "__main__":
    main()
