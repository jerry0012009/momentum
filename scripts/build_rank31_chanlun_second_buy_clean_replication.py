#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.multi_tf_momentum import MultiTfMomentumConfig, compute_multi_tf_momentum_signals  # noqa: E402
from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank31_chanlun_second_buy_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank31_chanlun_second_buy_15m"
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
PRIMARY_VARIANT = "structural_higher_low_reclaim"
VARIANTS = [
    "raw_pullback_recovery_baseline",
    "structural_higher_low_reclaim",
    "center_breakout_retest_reclaim",
]
HOLD_BARS = 8
FAILURE_LOOKAHEAD = 4
PIVOT_LEFT = 2
PIVOT_RIGHT = 2
CENTER_LOOKBACK = 12
RETEST_LOOKBACK = 3
EPS = 1e-9


@dataclass
class SignalEvent:
    direction: int
    reclaim_level: float


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
    return df.sort_values("timestamp").reset_index(drop=True)


def confirmed_pivot_high(high: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(high)
    prices = np.full(n, np.nan)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = high[center]
        if np.isnan(v):
            continue
        if np.all(v > high[center-left:center]) and np.all(v > high[center+1:center+right+1]):
            prices[center + right] = v
            origins[center + right] = center
    return prices, origins


def confirmed_pivot_low(low: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(low)
    prices = np.full(n, np.nan)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = low[center]
        if np.isnan(v):
            continue
        if np.all(v < low[center-left:center]) and np.all(v < low[center+1:center+right+1]):
            prices[center + right] = v
            origins[center + right] = center
    return prices, origins


def enrich_structure(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    high = out["high"].to_numpy(dtype=float)
    low = out["low"].to_numpy(dtype=float)
    ph_price, ph_origin = confirmed_pivot_high(high, PIVOT_LEFT, PIVOT_RIGHT)
    pl_price, pl_origin = confirmed_pivot_low(low, PIVOT_LEFT, PIVOT_RIGHT)
    out["confirmed_pivot_high"] = ph_price
    out["confirmed_pivot_low"] = pl_price
    out["pivot_high_origin"] = ph_origin
    out["pivot_low_origin"] = pl_origin

    last_high_vals: list[float] = []
    last_low_vals: list[float] = []
    last_high_origins: list[int] = []
    last_low_origins: list[int] = []

    cols = {
        "last_high_1": np.full(len(out), np.nan),
        "last_high_2": np.full(len(out), np.nan),
        "last_low_1": np.full(len(out), np.nan),
        "last_low_2": np.full(len(out), np.nan),
        "last_high_origin_1": np.full(len(out), -1, dtype=int),
        "last_high_origin_2": np.full(len(out), -1, dtype=int),
        "last_low_origin_1": np.full(len(out), -1, dtype=int),
        "last_low_origin_2": np.full(len(out), -1, dtype=int),
        "center_upper": np.full(len(out), np.nan),
        "center_lower": np.full(len(out), np.nan),
        "center_valid": np.zeros(len(out), dtype=int),
    }

    for i in range(len(out)):
        if not np.isnan(ph_price[i]):
            last_high_vals.append(float(ph_price[i]))
            last_high_origins.append(int(ph_origin[i]))
        if not np.isnan(pl_price[i]):
            last_low_vals.append(float(pl_price[i]))
            last_low_origins.append(int(pl_origin[i]))

        if len(last_high_vals) >= 1:
            cols["last_high_1"][i] = last_high_vals[-1]
            cols["last_high_origin_1"][i] = last_high_origins[-1]
        if len(last_high_vals) >= 2:
            cols["last_high_2"][i] = last_high_vals[-2]
            cols["last_high_origin_2"][i] = last_high_origins[-2]
        if len(last_low_vals) >= 1:
            cols["last_low_1"][i] = last_low_vals[-1]
            cols["last_low_origin_1"][i] = last_low_origins[-1]
        if len(last_low_vals) >= 2:
            cols["last_low_2"][i] = last_low_vals[-2]
            cols["last_low_origin_2"][i] = last_low_origins[-2]

        recent_highs = last_high_vals[-2:]
        recent_lows = last_low_vals[-2:]
        if len(recent_highs) == 2 and len(recent_lows) == 2:
            center_upper = min(recent_highs)
            center_lower = max(recent_lows)
            if center_upper > center_lower:
                cols["center_upper"][i] = center_upper
                cols["center_lower"][i] = center_lower
                cols["center_valid"][i] = 1

    for k, v in cols.items():
        out[k] = v
    return out


def build_baseline_frame(bars: pd.DataFrame) -> pd.DataFrame:
    baseline = compute_pullback_recovery_confirmation_signals(
        bars,
        config=PullbackRecoveryConfirmationConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
            vol_window=20,
            pullback_lookback=2,
            pullback_vol_z_max=0.0,
            vol_recover_th=1.0,
            breakout_lookback=1,
        ),
    )
    baseline["timestamp"] = pd.to_datetime(baseline["timestamp"], utc=True)
    return baseline.sort_values("timestamp").reset_index(drop=True)


def build_base_momentum(bars: pd.DataFrame) -> pd.DataFrame:
    base = compute_multi_tf_momentum_signals(
        bars,
        config=MultiTfMomentumConfig(
            window_5m=6,
            window_15m=6,
            threshold_5m=0.003,
            threshold_15m=0.006,
            resample_rule_15m="15min",
        ),
    )
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    return base.sort_values("timestamp").reset_index(drop=True)


def build_variant_frame(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset)
    baseline = build_baseline_frame(bars)
    base = build_base_momentum(bars)
    frame = bars.merge(
        baseline[
            [
                "timestamp",
                "long_signal",
                "short_signal",
                "base_long_signal",
                "base_short_signal",
                "breakout_ref_high",
                "breakout_ref_low",
                "vol_z",
            ]
        ].rename(columns={"long_signal": "baseline_long_signal", "short_signal": "baseline_short_signal"}),
        on="timestamp",
        how="left",
    )
    frame = frame.merge(
        base[["timestamp", "mom_5m", "mom_15m"]],
        on="timestamp",
        how="left",
    )
    frame = enrich_structure(frame)
    frame["recent_high_max_2"] = frame["high"].shift(1).rolling(2, min_periods=2).max()
    frame["recent_low_min_2"] = frame["low"].shift(1).rolling(2, min_periods=2).min()
    frame["center_recent_low"] = frame["low"].shift(1).rolling(RETEST_LOOKBACK, min_periods=RETEST_LOOKBACK).min()
    frame["center_recent_high"] = frame["high"].shift(1).rolling(RETEST_LOOKBACK, min_periods=RETEST_LOOKBACK).max()
    frame["center_breakout_seen_long"] = (
        (frame["close"].shift(1) > frame["center_upper"].shift(1)).rolling(CENTER_LOOKBACK, min_periods=1).max().fillna(0)
    )
    frame["center_breakout_seen_short"] = (
        (frame["close"].shift(1) < frame["center_lower"].shift(1)).rolling(CENTER_LOOKBACK, min_periods=1).max().fillna(0)
    )
    return frame


def get_signal(frame: pd.DataFrame, idx: int, variant: str) -> SignalEvent | None:
    row = frame.iloc[idx]
    prev = frame.iloc[idx - 1]
    if variant == "raw_pullback_recovery_baseline":
        if int(row.get("baseline_long_signal", 0)) == 1 and not pd.isna(row.get("breakout_ref_high")):
            return SignalEvent(direction=1, reclaim_level=float(row["breakout_ref_high"]))
        if int(row.get("baseline_short_signal", 0)) == 1 and not pd.isna(row.get("breakout_ref_low")):
            return SignalEvent(direction=-1, reclaim_level=float(row["breakout_ref_low"]))
        return None

    if variant == "structural_higher_low_reclaim":
        long_ok = (
            int(row.get("base_long_signal", 0)) == 1
            and not pd.isna(row.get("last_low_1"))
            and not pd.isna(row.get("last_low_2"))
            and not pd.isna(row.get("last_high_1"))
            and float(row["last_low_1"]) > float(row["last_low_2"]) * (1.0 + 0.001)
            and float(row["close"]) > max(float(row["last_high_1"]), float(row.get("recent_high_max_2", -np.inf)))
            and float(prev["close"]) <= float(row["close"])
        )
        short_ok = (
            int(row.get("base_short_signal", 0)) == 1
            and not pd.isna(row.get("last_high_1"))
            and not pd.isna(row.get("last_high_2"))
            and not pd.isna(row.get("last_low_1"))
            and float(row["last_high_1"]) < float(row["last_high_2"]) * (1.0 - 0.001)
            and float(row["close"]) < min(float(row["last_low_1"]), float(row.get("recent_low_min_2", np.inf)))
            and float(prev["close"]) >= float(row["close"])
        )
        if long_ok:
            return SignalEvent(direction=1, reclaim_level=float(row["last_high_1"]))
        if short_ok:
            return SignalEvent(direction=-1, reclaim_level=float(row["last_low_1"]))
        return None

    if variant == "center_breakout_retest_reclaim":
        long_ok = (
            int(row.get("base_long_signal", 0)) == 1
            and int(row.get("center_valid", 0)) == 1
            and float(row.get("center_breakout_seen_long", 0)) >= 1.0
            and not pd.isna(row.get("center_recent_low"))
            and not pd.isna(row.get("center_upper"))
            and not pd.isna(row.get("center_lower"))
            and float(row["center_recent_low"]) >= float(row["center_lower"]) - EPS
            and float(row["center_recent_low"]) <= float(row["center_upper"]) * (1.0 + 0.002)
            and float(row["close"]) > float(row["center_upper"])
            and float(prev["close"]) <= float(row["close"])
        )
        short_ok = (
            int(row.get("base_short_signal", 0)) == 1
            and int(row.get("center_valid", 0)) == 1
            and float(row.get("center_breakout_seen_short", 0)) >= 1.0
            and not pd.isna(row.get("center_recent_high"))
            and not pd.isna(row.get("center_upper"))
            and not pd.isna(row.get("center_lower"))
            and float(row["center_recent_high"]) <= float(row["center_upper"]) + EPS
            and float(row["center_recent_high"]) >= float(row["center_lower"]) * (1.0 - 0.002)
            and float(row["close"]) < float(row["center_lower"])
            and float(prev["close"]) >= float(row["close"])
        )
        if long_ok:
            return SignalEvent(direction=1, reclaim_level=float(row["center_upper"]))
        if short_ok:
            return SignalEvent(direction=-1, reclaim_level=float(row["center_lower"]))
        return None

    raise ValueError(f"unknown variant: {variant}")


def detect_false_reclaim(frame: pd.DataFrame, signal_idx: int, direction: int, reclaim_level: float) -> int:
    for step in range(1, FAILURE_LOOKAHEAD + 1):
        j = signal_idx + step
        if j >= len(frame):
            break
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < reclaim_level:
            return 1
        if direction < 0 and close > reclaim_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    last_exit = -1
    signals_seen = 0
    eligible_mask = ((frame.get("base_long_signal", 0) == 1) | (frame.get("base_short_signal", 0) == 1)).astype(int)
    eligible_bars = int(eligible_mask.sum())

    for idx in range(1, len(frame) - 1):
        if idx <= last_exit:
            continue
        signal = get_signal(frame, idx, variant)
        if signal is None:
            continue
        signals_seen += 1
        entry_idx = idx + 1
        exit_idx = min(entry_idx + HOLD_BARS - 1, len(frame) - 1)
        if entry_idx >= len(frame):
            continue
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_price) and math.isfinite(exit_price) and entry_price > 0 and exit_price > 0):
            continue
        gross_ret = (exit_price / entry_price - 1.0) * signal.direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_idx": int(idx),
                "event_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if signal.direction > 0 else "short",
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_reclaim": int(detect_false_reclaim(frame, idx, signal.direction, signal.reclaim_level)),
                "reclaim_level": float(signal.reclaim_level),
                "base_long_signal": int(frame.iloc[idx].get("base_long_signal", 0)),
                "base_short_signal": int(frame.iloc[idx].get("base_short_signal", 0)),
                "center_valid": int(frame.iloc[idx].get("center_valid", 0)),
            }
        )
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
        "false_reclaim_ratio": float(trades["false_reclaim"].mean()),
        "no_trade_ratio": float(no_trade_ratio),
        "eligible_bias_bars": int(eligible_bars),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
                "median_total_return": float(np.nanmedian(total_returns)) if len(total_returns) else np.nan,
                "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
                "mean_trades": float(grp["trades"].mean()),
                "mean_false_reclaim_ratio": float(grp["false_reclaim_ratio"].mean()),
                "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以站住。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"]) if not pd.isna(row["mean_total_return"]) else -1.0
    pos_ratio = float(row["positive_asset_ratio"]) if not pd.isna(row["positive_asset_ratio"]) else 0.0
    mean_trades = float(row["mean_trades"]) if not pd.isna(row["mean_trades"]) else 0.0
    false_ratio = float(row["mean_false_reclaim_ratio"]) if not pd.isna(row["mean_false_reclaim_ratio"]) else 1.0
    no_trade = float(row["mean_no_trade_ratio"]) if not pd.isna(row["mean_no_trade_ratio"]) else 1.0
    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 10 and false_ratio <= 0.55 and no_trade <= 0.97:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没有直接塌掉：成本后仍为正、跨资产不只剩单腿，而且假 reclaim 率 / 交易密度还勉强站得住。"
    return "park / evidence pool", "最小 clean replication 没把它拉进候选池：要么成本后回报仍弱，要么假 reclaim 率偏高、交易密度过薄，或 no-trade 比例过高。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank31_chanlun_second_buy_clean_replication.html" in text:
        return
    anchor = 'rank31_chanlun_second_buy_source_intake.html">Rank 31 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank31_chanlun_second_buy_clean_replication.html">clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame) -> None:
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

    old_block = """31. `Rank 31 chanlun-pro second-buy / breakout-retest continuation gate`（GitHub `yijixiuxin/chanlun-pro` repo + 本地 `pullback / recovery` 邻近语义）→ **`admit_to_clean_replication_queue`**
     - 这轮 fresh intake 默认不再重开已 park 的 `Rank 30`，而是转去一条更贴近当前 desk 主线的 repo-based 候选：`chanlun-pro` 明确支持逐 Bar / 增量结构更新、数字货币市场与 `1m/5m/15m` 周期，且本地学习地图已把 `二买 / 回抽确认` 标成最像 alpha 的提炼对象。
     - 冻结后的 source-intake 规则：`trade on = higher_tf_bias_up + 已确认结构突破 + pullback 不跌破最新因果确认结构低点/中枢下沿 + close 重新站上 pre-pullback reclaim level`；`trade off = 没有已确认结构突破 / pullback 跌破结构地板 / 回抽后始终无法 reclaim 触发位`。
     - 两条轻量诚实守门已先过：一是规则能清楚写成 `trade on / trade off`；二是必须坚持 repo 自己写明的 `逐 Bar / 增量确认` 口径，所有 pivot / pen / zone 代理都只能用因果确认版本，不能把事后画出的结构回填成入场依据。
     - **最新补充（2026-03-17 10:39 UTC）**：本轮 hard verdict 只到 **`admit_to_clean_replication_queue`**，不偷升 `P1 / P2`。下一轮若仍无新的 `EMA due-now` 与 `P3 append/review` need，默认只允许做 `BTC/ETH/SOL 120d~180d 15m` 上的 1 次最小 clean replication：比较 `raw pullback-recovery baseline`、`structural higher-low reclaim`、`center-breakout-retest-reclaim`，先看 `post_cost_return / false_reclaim_ratio / trade_count / no_trade_ratio`；若 trade count 过薄或成本后继续转负，就快速压回 `park`。
     - 网页落点：`reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html`。
"""
    new_block = f"""31. `Rank 31 chanlun-pro second-buy / breakout-retest continuation gate`（GitHub `yijixiuxin/chanlun-pro` repo + 本地 `pullback / recovery` 邻近语义）→ **`{verdict}`**
     - 已完成 `fresh source intake -> 最小 clean replication`，固定复用 `BTC/ETH/SOL 120d 15m` cache；只比较 `raw pullback-recovery baseline`、`structural higher-low reclaim`、`center-breakout-retest-reclaim`，不追新 bar，也不直接扩成完整 stability pack。
     - 冻结后的 clean-room 规则：`raw baseline` 继续沿用现有 `pullback_recovery_confirmation` 的多周期动量 + 缩量回调 + 放量恢复；`structural higher-low reclaim` 只在 `higher_tf_bias` 同向、且最新因果确认 swing 已形成更高低点/更低高点后，要求价格 reclaim 最近结构突破位；`center-breakout-retest-reclaim` 则要求最近两组因果确认 pivots 形成最小 overlap center，并在已有 breakout 后经历一次 center 内 retest 再 reclaim 外沿。
     - 当前最诚实的主证据：{stats}
     - **最新补充（{generated_at}）**：这轮最小 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`chanlun-pro second-buy` 已不再只是 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。
     - 网页落点：`reports/site/factors/scout_rank31_chanlun_second_buy_15m/report.html`、`reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html`。
"""
    if old_block in text:
        text = text.replace(old_block, new_block, 1)

    old_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；若 `Rank 29 / Rank 17 / Rank 2` 都没有新的真实 append/review row，则默认优先认领 `Rank 31` 那 1 次最小 clean replication，而不是重开已 park 的旧线。**"
    if old_summary in text:
        if verdict.startswith("P1"):
            new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；若 `Rank 29 / Rank 17 / Rank 2` 都没有新的真实 append/review row，则下一轮默认只允许给 `Rank 31` 那唯一一次便宜诚实检查预算；若这次检查也不能改变层级，就应压回 `park / evidence pool`，而不是继续磨同一条线。**"
        else:
            new_summary = "**因此当前默认节奏应改为：`Paper Seat / EMA` 继续按 `waiting_not_due` 处理；`Rank 31` 的最小 clean replication 已如实落地，若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 append/review row，则下一轮默认应回到 fresh `paper / repo based 5m / 15m crypto` intake，重新比较新的 active Scout 边际价值，而不是重开已 park 的旧线。**"
        text = text.replace(old_summary, new_summary, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
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
    overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 31 · chanlun-pro second-buy clean replication</title>
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
  <h1>Rank 31 · chanlun-pro second-buy / breakout-retest continuation gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三档最小规则：<code>raw_pullback_recovery_baseline</code>、<code>structural_higher_low_reclaim</code>、<code>center_breakout_retest_reclaim</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_reclaim_ratio</code>、<code>trade_count</code>、<code>no_trade_ratio</code>。</li>
      <li>执行口径固定：信号 bar 只用当时已确认的 swing / center；入场 = <code>next-bar open</code>；持有 = <code>{HOLD_BARS}</code> 根 15m bar；默认 non-overlap。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>raw baseline：</b>沿用现有 <code>pullback_recovery_confirmation</code> 的多周期动量 + 缩量回调 + 放量恢复。</li>
      <li><b>structural higher-low reclaim：</b>只在 <code>higher_tf_bias</code> 同向、且最新因果确认 swing 已形成更高低点 / 更低高点后，要求价格真正 reclaim 最近结构突破位。</li>
      <li><b>center-breakout-retest-reclaim：</b>用最近两组因果确认高低点形成最小 overlap center；只有在已看到 center 外突破之后、又出现一次 center 内 retest 并重新站回外沿时才允许入场。</li>
      <li><b>false reclaim：</b>触发后 {FAILURE_LOOKAHEAD} 根内，若收盘重新跌回 / 涨回 reclaim level 另一侧，则记为假 reclaim。</li>
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
    {render_table(overall_view[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_view[["asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"}, digits_cols={"trades":0})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank31_chanlun_second_buy_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank31_chanlun_second_buy_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank31_chanlun_second_buy_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../../reading/trendline_alpha_scout/rank31_chanlun_second_buy_source_intake.html'>source intake card</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_variant_frame(asset, symbol) for asset, symbol in ASSETS.items()}
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
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, no_trade_ratio=no_trade_ratio, eligible_bars=eligible_bars))

    all_trades_df = pd.concat([df for df in all_trades if not df.empty], ignore_index=True) if any(not df.empty for df in all_trades) else pd.DataFrame()
    if all_trades_df.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    else:
        all_trades_df[(all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)].to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    verdict, verdict_reason = build_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    (ART_DIR / "meta.csv").write_text(
        pd.DataFrame([
            {
                "generated_at_utc": generated_at,
                "candidate_id": "rank31_chanlun_second_buy_15m",
                "hard_verdict": verdict,
                "verdict_reason": verdict_reason,
            }
        ]).to_csv(index=False),
        encoding="utf-8",
    )

    html = build_html(overall, asset_summary, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank31_chanlun_second_buy_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall)

    print(f"verdict={verdict}")
    if not overall.empty:
        primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
        if not primary.empty:
            print("primary_stats", primary.iloc[0].to_dict())


if __name__ == "__main__":
    main()
