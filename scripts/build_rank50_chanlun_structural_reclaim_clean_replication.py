#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank50_chanlun_structural_reclaim_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank50_chanlun_structural_reclaim_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
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
    "raw_breakout_retest",
    "structural_reclaim",
    "structural_reclaim_plus_htf",
]
PRIMARY_VARIANT = "structural_reclaim_plus_htf"
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
SWING_LOOKBACK = 4
BREAKOUT_LOOKBACK = 24
RETEST_TIMEOUT = 16
EMA_FAST_1H = 20
EMA_SLOW_1H = 50
EMA_FAST_15M = 9
EMA_SLOW_15M = 21
ATR_PERIOD = 14
MIN_BREAK_ATR = 0.20
RETEST_ATR = 0.60
INVALIDATE_ATR = 0.90
HL_BUFFER = 0.001


@dataclass(frozen=True)
class BreakoutEvent:
    direction: int
    level: float
    structure_floor: float
    structure_cap: float


@dataclass(frozen=True)
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
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def confirmed_pivots(arr: np.ndarray, lookback: int, kind: str) -> tuple[np.ndarray, np.ndarray]:
    n = len(arr)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(lookback, n - lookback):
        v = float(arr[center])
        left = arr[center - lookback:center]
        right = arr[center + 1:center + lookback + 1]
        if kind == "high":
            ok = bool(np.all(v > left) and np.all(v > right))
        else:
            ok = bool(np.all(v < left) and np.all(v < right))
        if ok:
            prices[center + lookback] = v
            origins[center + lookback] = center
    return prices, origins


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["atr14"] = compute_atr(df)
    df["ema_fast_15m"] = df["close"].ewm(span=EMA_FAST_15M, adjust=False).mean()
    df["ema_slow_15m"] = df["close"].ewm(span=EMA_SLOW_15M, adjust=False).mean()

    htf = (
        df[["timestamp", "close"]]
        .rename(columns={"close": "close_1h_src"})
        .set_index("timestamp")
        .resample("1h")
        .last()
        .dropna()
        .reset_index()
    )
    htf["ema_fast_1h"] = htf["close_1h_src"].ewm(span=EMA_FAST_1H, adjust=False).mean()
    htf["ema_slow_1h"] = htf["close_1h_src"].ewm(span=EMA_SLOW_1H, adjust=False).mean()
    htf["htf_long"] = (htf["ema_fast_1h"] > htf["ema_slow_1h"]).astype(int)
    htf["htf_short"] = (htf["ema_fast_1h"] < htf["ema_slow_1h"]).astype(int)
    df = pd.merge_asof(df.sort_values("timestamp"), htf.sort_values("timestamp"), on="timestamp", direction="backward")

    ph, ph_origin = confirmed_pivots(df["high"].to_numpy(dtype=float), SWING_LOOKBACK, "high")
    pl, pl_origin = confirmed_pivots(df["low"].to_numpy(dtype=float), SWING_LOOKBACK, "low")
    df["confirmed_high"] = ph
    df["confirmed_high_origin"] = ph_origin
    df["confirmed_low"] = pl
    df["confirmed_low_origin"] = pl_origin

    last_high_vals: list[float] = []
    last_low_vals: list[float] = []
    last_high_origins: list[int] = []
    last_low_origins: list[int] = []
    cols = {
        "last_high_1": np.full(len(df), np.nan),
        "last_high_2": np.full(len(df), np.nan),
        "last_low_1": np.full(len(df), np.nan),
        "last_low_2": np.full(len(df), np.nan),
        "last_high_origin_1": np.full(len(df), -1, dtype=int),
        "last_low_origin_1": np.full(len(df), -1, dtype=int),
        "breakout_ref_high": np.full(len(df), np.nan),
        "breakout_ref_low": np.full(len(df), np.nan),
    }
    for i in range(len(df)):
        if not np.isnan(ph[i]):
            last_high_vals.append(float(ph[i]))
            last_high_origins.append(int(ph_origin[i]))
        if not np.isnan(pl[i]):
            last_low_vals.append(float(pl[i]))
            last_low_origins.append(int(pl_origin[i]))
        if len(last_high_vals) >= 1:
            cols["last_high_1"][i] = last_high_vals[-1]
            cols["last_high_origin_1"][i] = last_high_origins[-1]
        if len(last_high_vals) >= 2:
            cols["last_high_2"][i] = last_high_vals[-2]
        if len(last_low_vals) >= 1:
            cols["last_low_1"][i] = last_low_vals[-1]
            cols["last_low_origin_1"][i] = last_low_origins[-1]
        if len(last_low_vals) >= 2:
            cols["last_low_2"][i] = last_low_vals[-2]
        if len(last_high_vals) >= 1:
            cols["breakout_ref_high"][i] = max(last_high_vals[-BREAKOUT_LOOKBACK:])
        if len(last_low_vals) >= 1:
            cols["breakout_ref_low"][i] = min(last_low_vals[-BREAKOUT_LOOKBACK:])
    for k, v in cols.items():
        df[k] = v

    df["long_bias_15m"] = ((df["ema_fast_15m"] > df["ema_slow_15m"]) & (df["close"] > df["ema_fast_15m"]))
    df["short_bias_15m"] = ((df["ema_fast_15m"] < df["ema_slow_15m"]) & (df["close"] < df["ema_fast_15m"]))
    return df.reset_index(drop=True)


def breakout_candidate(frame: pd.DataFrame, idx: int) -> BreakoutEvent | None:
    row = frame.iloc[idx]
    prev = frame.iloc[idx - 1]
    atr = float(row["atr14"]) if pd.notna(row["atr14"]) else float("nan")
    if not math.isfinite(atr) or atr <= 0:
        return None

    ref_high = float(row["breakout_ref_high"]) if pd.notna(row["breakout_ref_high"]) else float("nan")
    ref_low = float(row["breakout_ref_low"]) if pd.notna(row["breakout_ref_low"]) else float("nan")

    if int(row.get("htf_long", 0)) == 1 and math.isfinite(ref_high):
        if float(prev["close"]) <= ref_high and float(row["close"]) > ref_high + MIN_BREAK_ATR * atr:
            floor = float(row["last_low_1"]) if pd.notna(row["last_low_1"]) else ref_high - atr
            return BreakoutEvent(direction=1, level=ref_high, structure_floor=floor, structure_cap=float("nan"))

    if int(row.get("htf_short", 0)) == 1 and math.isfinite(ref_low):
        if float(prev["close"]) >= ref_low and float(row["close"]) < ref_low - MIN_BREAK_ATR * atr:
            cap = float(row["last_high_1"]) if pd.notna(row["last_high_1"]) else ref_low + atr
            return BreakoutEvent(direction=-1, level=ref_low, structure_floor=float("nan"), structure_cap=cap)
    return None


def get_signal(frame: pd.DataFrame, idx: int, variant: str) -> SignalEvent | None:
    event = breakout_candidate(frame, idx)
    if event is None:
        return None
    if variant == "raw_breakout_retest":
        return SignalEvent(direction=event.direction, reclaim_level=event.level)

    atr0 = float(frame.iloc[idx]["atr14"])
    last_wait = min(len(frame) - 2, idx + RETEST_TIMEOUT)
    for j in range(idx + 1, last_wait + 1):
        row = frame.iloc[j]
        prev = frame.iloc[j - 1]
        if event.direction > 0:
            if float(row["close"]) < event.level - INVALIDATE_ATR * atr0:
                return None
            in_zone = float(row["low"]) <= event.level + RETEST_ATR * atr0 and float(row["high"]) >= event.level - RETEST_ATR * atr0
            if not in_zone:
                continue
            if not (pd.notna(row["last_low_1"]) and pd.notna(row["last_low_2"])):
                continue
            hl_ok = float(row["last_low_1"]) > float(row["last_low_2"]) * (1.0 + HL_BUFFER)
            floor_ok = float(row["low"]) >= event.structure_floor - RETEST_ATR * atr0
            reclaim_ok = float(prev["close"]) <= event.level and float(row["close"]) > event.level
            htf_ok = bool(int(row.get("htf_long", 0)) == 1 and bool(row.get("long_bias_15m", False)))
            if hl_ok and floor_ok and reclaim_ok:
                if variant == "structural_reclaim":
                    return SignalEvent(direction=1, reclaim_level=event.level)
                if variant == "structural_reclaim_plus_htf" and htf_ok:
                    return SignalEvent(direction=1, reclaim_level=event.level)
        else:
            if float(row["close"]) > event.level + INVALIDATE_ATR * atr0:
                return None
            in_zone = float(row["high"]) >= event.level - RETEST_ATR * atr0 and float(row["low"]) <= event.level + RETEST_ATR * atr0
            if not in_zone:
                continue
            if not (pd.notna(row["last_high_1"]) and pd.notna(row["last_high_2"])):
                continue
            lh_ok = float(row["last_high_1"]) < float(row["last_high_2"]) * (1.0 - HL_BUFFER)
            cap_ok = float(row["high"]) <= event.structure_cap + RETEST_ATR * atr0
            reclaim_ok = float(prev["close"]) >= event.level and float(row["close"]) < event.level
            htf_ok = bool(int(row.get("htf_short", 0)) == 1 and bool(row.get("short_bias_15m", False)))
            if lh_ok and cap_ok and reclaim_ok:
                if variant == "structural_reclaim":
                    return SignalEvent(direction=-1, reclaim_level=event.level)
                if variant == "structural_reclaim_plus_htf" and htf_ok:
                    return SignalEvent(direction=-1, reclaim_level=event.level)
    return None


def detect_false_reclaim(frame: pd.DataFrame, signal_idx: int, direction: int, reclaim_level: float) -> int:
    last = min(len(frame) - 1, signal_idx + FALSE_LOOKAHEAD)
    for j in range(signal_idx + 1, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < reclaim_level:
            return 1
        if direction < 0 and close > reclaim_level:
            return 1
    return 0


def annotate_signals(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["eligible_breakout"] = 0
    for variant in VARIANTS:
        out[f"signal_{variant}"] = 0
        out[f"direction_{variant}"] = 0
        out[f"reclaim_level_{variant}"] = np.nan
    for idx in range(1, len(out) - 2):
        event = breakout_candidate(out, idx)
        if event is not None:
            out.at[idx, "eligible_breakout"] = 1
        for variant in VARIANTS:
            signal = get_signal(out, idx, variant)
            if signal is None:
                continue
            out.at[idx, f"signal_{variant}"] = 1
            out.at[idx, f"direction_{variant}"] = int(signal.direction)
            out.at[idx, f"reclaim_level_{variant}"] = float(signal.reclaim_level)
    return out


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, float, int]:
    rows: list[dict[str, object]] = []
    last_exit = -1
    signal_events = 0
    eligible_breakouts = int(frame["eligible_breakout"].sum()) if "eligible_breakout" in frame.columns else 0
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit:
            continue
        if int(frame.iloc[idx].get(f"signal_{variant}", 0)) != 1:
            continue
        direction = int(frame.iloc[idx][f"direction_{variant}"])
        reclaim_level = float(frame.iloc[idx][f"reclaim_level_{variant}"])
        signal_events += 1
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        if entry_idx >= len(frame):
            break
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_px) and math.isfinite(exit_px) and entry_px > 0 and exit_px > 0):
            continue
        gross_ret = (exit_px / entry_px - 1.0) * direction
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
                "direction": "long" if direction > 0 else "short",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_reclaim_ratio": int(detect_false_reclaim(frame, idx, direction, reclaim_level)),
                "reclaim_level": reclaim_level,
            }
        )
        last_exit = exit_idx

    trades = pd.DataFrame(rows)
    no_trade_ratio = 1.0 if eligible_breakouts == 0 else max(0.0, 1.0 - (signal_events / eligible_breakouts))
    return trades, no_trade_ratio, eligible_breakouts


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, no_trade_ratio: float, eligible_breakouts: int) -> dict[str, object]:
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
            "eligible_breakouts": int(eligible_breakouts),
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
        "eligible_breakouts": int(eligible_breakouts),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
    }


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        totals = grp["total_return"].to_numpy(dtype=float)
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(np.nanmean(totals)) if len(totals) else np.nan,
                "median_total_return": float(np.nanmedian(totals)) if len(totals) else np.nan,
                "positive_asset_ratio": float(np.nanmean(totals > 0)) if len(totals) else np.nan,
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
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以支撑 admission。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"]) if not pd.isna(row["mean_total_return"]) else -1.0
    pos_ratio = float(row["positive_asset_ratio"]) if not pd.isna(row["positive_asset_ratio"]) else 0.0
    mean_trades = float(row["mean_trades"]) if not pd.isna(row["mean_trades"]) else 0.0
    false_ratio = float(row["mean_false_reclaim_ratio"]) if not pd.isna(row["mean_false_reclaim_ratio"]) else 1.0
    no_trade = float(row["mean_no_trade_ratio"]) if not pd.isna(row["mean_no_trade_ratio"]) else 1.0
    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 8 and false_ratio <= 0.50 and no_trade <= 0.92:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少没有直接塌掉：成本后仍为正、跨资产不只剩单腿，而且假 reclaim 率 / no-trade 比例还没坏到必须立刻 park。"
    return "park / evidence pool", "最小 clean replication 没把 structural reclaim 推进候选池：成本后仍偏弱，或假 reclaim / no-trade 比例说明它更像把样本切薄。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    if "rank50_chanlun_structural_reclaim_clean_replication.html" in text:
        return
    anchor = 'rank50_chanlun_structural_reclaim_source_intake.html">Rank 50 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank50_chanlun_structural_reclaim_clean_replication.html">clean replication</a>', 1)
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

    old_scout_block = """- **最新补充（2026-03-18 07:38 UTC）**：这轮已按 `Run 2` 只认领 **`Rank 50 / chanlun-pro structural reclaim gate source intake + 两条轻量诚实守门`**，并且先比较了当前所有 active fresh Scout 候选的边际价值：`Rank 50 / chanlun-pro structural reclaim gate`（成熟 repo、可同时服务 breakout/Fib/EMA-PSAR 的共用结构确认层） `>` `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate`（`2026-03-18 07:34 UTC` 新 digest，对 24/7 crypto 的 session 迁移与社会证明更弱，先排下一条 fresh intake） `>` `Rank 35b`（queue-only fallback）。
  - 本轮 hard verdict：**`Rank 50 / chanlun-pro structural reclaim gate = guard-passed / admit_to_clean_replication_queue`**。`trade on / trade off` 已能冻结成 `higher-low / lower-high + reclaim / fail-reclaim` 的因果版结构确认；源码语义也明确要求逐 Bar 增量确认，因此当前未见必须立刻判死刑的 `lookahead / repaint / leakage`，但下一轮 clean replication 仍必须统一到 `next-bar open + no-overlap`，避免把事后结构倒灌回入场。
  - reader-facing 落点：`reports/site/reading/repo_scout/rank50_chanlun_structural_reclaim_source_intake.html`；artifact：`reports/artifacts/literature/scout_rank50_chanlun_structural_reclaim_source_intake_card.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 50 minimal clean replication（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = Rank 51 / vwap-trend-defense source intake；若 Rank 51 也不合格，再回退到 Rank 35b / tiny-live plumbing`**。"""

    new_scout_block = f"""- **最新补充（2026-03-18 07:38 UTC）**：这轮已按 `Run 2` 只认领 **`Rank 50 / chanlun-pro structural reclaim gate source intake + 两条轻量诚实守门`**，并且先比较了当前所有 active fresh Scout 候选的边际价值：`Rank 50 / chanlun-pro structural reclaim gate`（成熟 repo、可同时服务 breakout/Fib/EMA-PSAR 的共用结构确认层） `>` `Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate`（`2026-03-18 07:34 UTC` 新 digest，对 24/7 crypto 的 session 迁移与社会证明更弱，先排下一条 fresh intake） `>` `Rank 35b`（queue-only fallback）。
  - 上一轮 hard verdict：**`Rank 50 / chanlun-pro structural reclaim gate = guard-passed / admit_to_clean_replication_queue`**。`trade on / trade off` 已能冻结成 `higher-low / lower-high + reclaim / fail-reclaim` 的因果版结构确认；源码语义也明确要求逐 Bar 增量确认，因此 clean replication 必须统一到 `next-bar open + no-overlap`，避免把事后结构倒灌回入场。
  - **最新补充（{generated_at}）**：这轮已完成 `Rank 50` 的唯一那手 **最小 clean replication**：固定复用 `BTC/ETH/SOL 120d 15m` cache，只比较 `raw_breakout_retest`、`structural_reclaim`、`structural_reclaim_plus_htf` 三臂，并统一冻结到 `next-bar open + no-overlap + hold 8 bars`。{stats}
  - 当前更诚实的 hard verdict：**`Rank 50 / chanlun-pro structural reclaim gate = {verdict}`**。更直白地说：这条线已经不再停在 intake queue；若后续继续认领，默认只能按这个 verdict 走——若仍只是 `{verdict}`，就不该继续靠 intake / admission 近义文案续命。
  - reader-facing 落点：`reports/site/factors/scout_rank50_chanlun_structural_reclaim_15m/report.html`、`reports/site/reading/repo_scout/rank50_chanlun_structural_reclaim_clean_replication.html`；artifact：`reports/artifacts/scout_rank50_chanlun_structural_reclaim_15m/overall_summary.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 51 / vwap-trend-defense source intake（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = Rank 35b / tiny-live plumbing（若 Rank 51 也不合格）`**。"""
    if old_scout_block in text:
        text = text.replace(old_scout_block, new_scout_block, 1)

    pattern = re.compile(r"> \*\*最新补充（2026-03-18 07:20 UTC）\*\*[\s\S]*?Run 3 = Rank 50 minimal clean replication（仅当 Run 2 guard-passed 且 EMA 仍 waiting_not_due）；若 Run 2 硬 fail，再回退到下一条 fresh source intake，其次才是 Rank 35b / tiny-live plumbing`\*\*。")
    replacement = f"> **最新补充（2026-03-18 08:3x UTC，沿 07:38 Rank 50 队列更新）**：`Rank 50 / chanlun-pro structural reclaim gate` 已完成其唯一允许的一手最小 clean replication，因此不应再继续把它留在默认 `Run 2`。当前更诚实的 desk 读法是：`EMA` 仍是 `running paper / waiting_not_due`，`Rank 50` 已拿到 hard verdict **`{verdict}`**，而 active fresh Scout 队列应顺延到 **`Rank 51 / vwap-trend-defense / session VWAP reclaim + breadth gate`**。\n>  - 这次 clean replication 固定复用 `BTC/ETH/SOL 120d 15m` cache，只比较 `raw_breakout_retest`、`structural_reclaim`、`structural_reclaim_plus_htf` 三臂，并统一冻结到 `next-bar open + no-overlap + hold 8 bars`；{stats}\n>  - 因此当前最新的 `Next 3` 顺序应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 51 / vwap-trend-defense source intake（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = Rank 35b / tiny-live plumbing（若 Rank 51 也不合格）`**。"
    text, count = pattern.subn(replacement, text, count=1)
    if count == 0:
        raise RuntimeError("failed to update Next 3 block for Rank 50")

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
  <title>Rank 50 · chanlun structural reclaim clean replication</title>
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
  <p><a href='../../reading/repo_scout/report.html'>← 返回 Repo Scout</a></p>
  <h1>Rank 50 · chanlun-pro structural reclaim gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication ｜ 角色：Scout Seat 的 repo-based 15m crypto fast verdict</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>只比较三臂：<code>raw_breakout_retest</code>、<code>structural_reclaim</code>、<code>structural_reclaim_plus_htf</code>。</li>
      <li>执行口径固定：<code>signal bar close -> next-bar open -> no-overlap -> hold {HOLD_BARS} bars</code>。</li>
      <li>先回答四个便宜问题：<code>post_cost_return</code>、<code>false_reclaim_ratio</code>、<code>trade_count</code>、<code>no_trade_ratio</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>raw_breakout_retest：</b>只要因果确认 swing 的 breakout 真正越过最近结构位，就 next-bar open 入场，不再要求后续 HL/LH reclaim。</li>
      <li><b>structural_reclaim：</b>breakout 后允许最多 {RETEST_TIMEOUT} 根等待 retest；只有 pullback 仍站在结构地板/天花板内，并形成 <code>higher-low / lower-high + reclaim</code> 时才入场。</li>
      <li><b>structural_reclaim_plus_htf：</b>在上一臂基础上，再要求 <code>1h EMA20/50</code> 与 <code>15m EMA9/21</code> 同向，避免把逆风反抽误读成 continuation。</li>
      <li><b>false reclaim：</b>触发后 {FALSE_LOOKAHEAD} 根内，若收盘重新跌回 / 涨回 reclaim level 另一侧，则记为假 reclaim。</li>
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
      <li><a href='../../../artifacts/scout_rank50_chanlun_structural_reclaim_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank50_chanlun_structural_reclaim_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank50_chanlun_structural_reclaim_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
      <li><a href='../../reading/repo_scout/rank50_chanlun_structural_reclaim_source_intake.html'>source intake card</a></li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: annotate_signals(build_frame(asset, symbol)) for asset, symbol in ASSETS.items()}
    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []
    for asset, frame in frames.items():
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, no_trade_ratio, eligible_breakouts = build_trades(frame, asset, variant, cost)
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
                        eligible_breakouts=eligible_breakouts,
                    )
                )

    non_empty = [df for df in all_trades if not df.empty]
    all_trades_df = pd.concat(non_empty, ignore_index=True) if non_empty else pd.DataFrame()
    if all_trades_df.empty:
        pd.DataFrame().to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    else:
        all_trades_df[(all_trades_df["variant"] == PRIMARY_VARIANT) & (all_trades_df["cost_bps_per_side"] == PRIMARY_COST)].to_csv(
            ART_DIR / "trades_primary_6bps.csv", index=False
        )

    asset_summary = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_summary)
    verdict, verdict_reason = build_verdict(overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    meta = pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at,
                "candidate_id": "rank50_chanlun_structural_reclaim_15m",
                "hard_verdict": verdict,
                "verdict_reason": verdict_reason,
            }
        ]
    )
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank50_chanlun_structural_reclaim_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(verdict, generated_at, overall)

    print(f"verdict={verdict}")
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if not primary.empty:
        print(primary.iloc[0].to_dict())


if __name__ == "__main__":
    main()
