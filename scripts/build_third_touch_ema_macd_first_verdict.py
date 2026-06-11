#!/usr/bin/env python3
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_third_touch_ema_macd_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_third_touch_ema_macd_15m"
REPORT_PATH = SITE_DIR / "report.html"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"
SPEC_META_PATH = ART_DIR / "spec_meta.csv"
VARIANT_PATH = ART_DIR / "variant_aggregate.csv"
ASSET_PATH = ART_DIR / "asset_summary.csv"
TRIAL_META_PATH = ART_DIR / "trial_meta.csv"
EVENT_SAMPLE_PATH = ART_DIR / "event_sample.csv"
FRICTION_LADDER_PATH = ART_DIR / "friction_ladder.csv"
TRADE_DETAIL_PATH = ART_DIR / "trade_detail.csv"
TRADE_COUNT_HONESTY_PATH = ART_DIR / "trade_count_honesty.csv"
TIME_STABILITY_PATH = ART_DIR / "time_stability_drycheck.csv"
PARAM_STABILITY_PATH = ART_DIR / "parameter_stability_drycheck.csv"
SOURCE_CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

EMA_FAST = 20
EMA_SLOW = 50
ATR_PERIOD = 14
DONCHIAN_LOOKBACK = 20
TAU_ATR = 0.05
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
COST_BPS_PER_SIDE = 6.0
SWING_LEFT = 2
SWING_RIGHT = 2
THIRD_TOUCH_WINDOW_MIN = 4
THIRD_TOUCH_WINDOW_MAX = 24
TOUCH_TOL_ATR = 0.05
REACTION_MIN_ATR = 0.2
PERSISTENCE_LOOKAHEAD = 3
PERSISTENCE_NEED = 2
BREAKOUT_LOOKAHEAD = 12
EMA_SLOPE_BARS = 3
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

VARIANTS = [
    "raw_breakout",
    "third_touch_only",
    "third_touch_plus_ema",
    "third_touch_plus_ema_macd",
]
FRICTION_VARIANTS = [
    "raw_breakout",
    "third_touch_only",
    "third_touch_plus_ema",
    "third_touch_plus_ema_macd",
]
FRICTION_COSTS = [6.0, 10.0, 15.0, 20.0]


@dataclass
class TradeResult:
    asset: str
    variant: str
    side: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    boundary_level: float
    entry_price: float
    exit_time: pd.Timestamp
    exit_price: float
    net_return: float
    max_drawdown: float
    false_break: float
    time_to_failure_bars: float
    persistence_pass: float


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_float(value) -> float:
    try:
        out = float(value)
    except Exception:
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def fmt_ts(ts) -> str:
    if ts is None or pd.isna(ts):
        return "-"
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%d %H:%M UTC")


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = SOURCE_CACHE_DIR / f"{symbol}__120d__15m.csv"
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


def compute_macd(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = close.ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = close.ewm(span=MACD_SLOW, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal = macd_line.ewm(span=MACD_SIGNAL, adjust=False).mean()
    hist = macd_line - signal
    return macd_line, signal, hist


def prepare_bars(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol).copy()
    bars["asset"] = asset
    bars["ema_fast"] = bars["close"].ewm(span=EMA_FAST, adjust=False).mean()
    bars["ema_slow"] = bars["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    bars["atr"] = compute_atr(bars)
    bars["donchian_upper"] = bars["high"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).max()
    bars["donchian_lower"] = bars["low"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).min()
    bars["threshold_upper"] = bars["donchian_upper"] + TAU_ATR * bars["atr"]
    bars["threshold_lower"] = bars["donchian_lower"] - TAU_ATR * bars["atr"]
    bars["long_bias"] = bars["ema_fast"] > bars["ema_slow"]
    bars["short_bias"] = bars["ema_fast"] < bars["ema_slow"]
    bars["ema_fast_slope"] = bars["ema_fast"].diff()
    bars["ema_slope_up3"] = (bars["ema_fast_slope"] > 0).rolling(EMA_SLOPE_BARS).sum() >= EMA_SLOPE_BARS
    bars["ema_slope_down3"] = (bars["ema_fast_slope"] < 0).rolling(EMA_SLOPE_BARS).sum() >= EMA_SLOPE_BARS
    macd_line, macd_signal, macd_hist = compute_macd(bars["close"])
    bars["macd_line"] = macd_line
    bars["macd_signal"] = macd_signal
    bars["macd_hist"] = macd_hist
    bars["raw_long_breakout"] = ((bars["long_bias"]) & (bars["close"] > bars["threshold_upper"]) & bars["threshold_upper"].notna())
    bars["raw_short_breakout"] = ((bars["short_bias"]) & (bars["close"] < bars["threshold_lower"]) & bars["threshold_lower"].notna())
    return bars


def is_pivot_high(df: pd.DataFrame, idx: int) -> bool:
    if idx < SWING_LEFT or idx + SWING_RIGHT >= len(df):
        return False
    center = safe_float(df.iloc[idx]["high"])
    left = df.iloc[idx - SWING_LEFT:idx]["high"]
    right = df.iloc[idx + 1: idx + 1 + SWING_RIGHT]["high"]
    return math.isfinite(center) and center > float(left.max()) and center >= float(right.max())


def is_pivot_low(df: pd.DataFrame, idx: int) -> bool:
    if idx < SWING_LEFT or idx + SWING_RIGHT >= len(df):
        return False
    center = safe_float(df.iloc[idx]["low"])
    left = df.iloc[idx - SWING_LEFT:idx]["low"]
    right = df.iloc[idx + 1: idx + 1 + SWING_RIGHT]["low"]
    return math.isfinite(center) and center < float(left.min()) and center <= float(right.min())


def _cluster_touches(values: list[float], atr: float, *, touch_tol_atr: float = TOUCH_TOL_ATR) -> tuple[bool, float]:
    if len(values) < 3 or not math.isfinite(atr) or atr <= 0:
        return False, float("nan")
    level = float(np.mean(values[-3:]))
    ok = all(abs(v - level) <= touch_tol_atr * atr for v in values[-3:])
    return ok, level


def _reaction_ok(df: pd.DataFrame, pivot_idx: int, side: str, level: float, atr: float) -> bool:
    if not math.isfinite(level) or not math.isfinite(atr) or atr <= 0:
        return False
    end_idx = min(pivot_idx + SWING_RIGHT + 4, len(df) - 1)
    future = df.iloc[pivot_idx + 1 : end_idx + 1]
    if future.empty:
        return False
    if side == "long":
        reaction = float(future["high"].max()) - level
    else:
        reaction = level - float(future["low"].min())
    return reaction >= REACTION_MIN_ATR * atr


def _persistence_pass(df: pd.DataFrame, breakout_idx: int, side: str, threshold: float) -> bool:
    future = df.iloc[breakout_idx : breakout_idx + PERSISTENCE_LOOKAHEAD]
    if len(future) < PERSISTENCE_LOOKAHEAD:
        return False
    if side == "long":
        return int((future["close"] > threshold).sum()) >= PERSISTENCE_NEED
    return int((future["close"] < threshold).sum()) >= PERSISTENCE_NEED


def _find_third_touch_breakouts(
    df: pd.DataFrame,
    *,
    touch_tol_atr: float = TOUCH_TOL_ATR,
    third_touch_window_min: int = THIRD_TOUCH_WINDOW_MIN,
    third_touch_window_max: int = THIRD_TOUCH_WINDOW_MAX,
) -> list[dict]:
    events: list[dict] = []
    long_touches: list[tuple[int, float]] = []
    short_touches: list[tuple[int, float]] = []
    n = len(df)

    for idx in range(n):
        atr = safe_float(df.iloc[idx]["atr"])
        if not math.isfinite(atr):
            continue

        if is_pivot_high(df, idx):
            high = safe_float(df.iloc[idx]["high"])
            long_touches.append((idx, high))
            if len(long_touches) >= 3:
                touch_idxs = [t[0] for t in long_touches[-3:]]
                touch_vals = [t[1] for t in long_touches[-3:]]
                spacing = touch_idxs[-1] - touch_idxs[0]
                clustered, level = _cluster_touches(touch_vals, atr, touch_tol_atr=touch_tol_atr)
                if clustered and third_touch_window_min <= spacing <= third_touch_window_max and _reaction_ok(df, touch_idxs[-1], "long", level, atr):
                    third_idx = touch_idxs[-1]
                    search_end = min(third_idx + BREAKOUT_LOOKAHEAD, n - PERSISTENCE_LOOKAHEAD)
                    threshold = level + TAU_ATR * atr
                    for brk_idx in range(third_idx + 1, search_end + 1):
                        if safe_float(df.iloc[brk_idx]["close"]) > threshold and _persistence_pass(df, brk_idx, "long", threshold):
                            events.append({
                                "side": "long",
                                "pivot_idx": third_idx,
                                "breakout_idx": brk_idx,
                                "boundary_level": level,
                                "threshold": threshold,
                                "touch_span_bars": spacing,
                            })
                            break

        if is_pivot_low(df, idx):
            low = safe_float(df.iloc[idx]["low"])
            short_touches.append((idx, low))
            if len(short_touches) >= 3:
                touch_idxs = [t[0] for t in short_touches[-3:]]
                touch_vals = [t[1] for t in short_touches[-3:]]
                spacing = touch_idxs[-1] - touch_idxs[0]
                clustered, level = _cluster_touches(touch_vals, atr, touch_tol_atr=touch_tol_atr)
                if clustered and third_touch_window_min <= spacing <= third_touch_window_max and _reaction_ok(df, touch_idxs[-1], "short", level, atr):
                    third_idx = touch_idxs[-1]
                    search_end = min(third_idx + BREAKOUT_LOOKAHEAD, n - PERSISTENCE_LOOKAHEAD)
                    threshold = level - TAU_ATR * atr
                    for brk_idx in range(third_idx + 1, search_end + 1):
                        if safe_float(df.iloc[brk_idx]["close"]) < threshold and _persistence_pass(df, brk_idx, "short", threshold):
                            events.append({
                                "side": "short",
                                "pivot_idx": third_idx,
                                "breakout_idx": brk_idx,
                                "boundary_level": level,
                                "threshold": threshold,
                                "touch_span_bars": spacing,
                            })
                            break
    return events


def _simulate_trade(
    df: pd.DataFrame,
    asset: str,
    variant: str,
    side: str,
    signal_idx: int,
    boundary_level: float,
    *,
    cost_bps_per_side: float = COST_BPS_PER_SIDE,
) -> TradeResult | None:
    entry_idx = signal_idx + 1
    if entry_idx >= len(df):
        return None
    atr = safe_float(df.iloc[signal_idx]["atr"])
    entry_price = safe_float(df.iloc[entry_idx]["open"])
    if not math.isfinite(atr) or not math.isfinite(entry_price) or atr <= 0:
        return None

    if side == "long":
        stop = entry_price - STOP_ATR * atr
        target = entry_price + TARGET_ATR * atr
    else:
        stop = entry_price + STOP_ATR * atr
        target = entry_price - TARGET_ATR * atr

    exit_idx = min(entry_idx + TIME_STOP_BARS, len(df) - 1)
    running_max_loss = 0.0
    for idx in range(entry_idx, exit_idx + 1):
        row = df.iloc[idx]
        high = safe_float(row["high"])
        low = safe_float(row["low"])
        close = safe_float(row["close"])
        if side == "long":
            adverse = min(0.0, low / entry_price - 1.0)
            running_max_loss = min(running_max_loss, adverse)
            if low <= stop:
                exit_price = stop
                exit_idx = idx
                break
            if high >= target:
                exit_price = target
                exit_idx = idx
                break
            exit_price = close
        else:
            adverse = min(0.0, entry_price / high - 1.0)
            running_max_loss = min(running_max_loss, adverse)
            if high >= stop:
                exit_price = stop
                exit_idx = idx
                break
            if low <= target:
                exit_price = target
                exit_idx = idx
                break
            exit_price = close

    if side == "long":
        gross_return = exit_price / entry_price - 1.0
    else:
        gross_return = entry_price / exit_price - 1.0
    net_return = gross_return - 2 * cost_bps_per_side / 10000.0

    future = df.iloc[signal_idx + 1 : signal_idx + 4]
    if side == "long":
        false_break = float((future["close"] <= boundary_level).any()) if not future.empty else float("nan")
    else:
        false_break = float((future["close"] >= boundary_level).any()) if not future.empty else float("nan")

    time_to_failure = float(TIME_STOP_BARS + 1)
    for idx in range(signal_idx + 1, min(signal_idx + TIME_STOP_BARS, len(df) - 1) + 1):
        close = safe_float(df.iloc[idx]["close"])
        if side == "long" and close <= boundary_level:
            time_to_failure = float(idx - signal_idx)
            break
        if side == "short" and close >= boundary_level:
            time_to_failure = float(idx - signal_idx)
            break

    return TradeResult(
        asset=asset,
        variant=variant,
        side=side,
        signal_time=df.iloc[signal_idx]["timestamp"],
        entry_time=df.iloc[entry_idx]["timestamp"],
        boundary_level=boundary_level,
        entry_price=entry_price,
        exit_time=df.iloc[exit_idx]["timestamp"],
        exit_price=float(exit_price),
        net_return=float(net_return),
        max_drawdown=float(running_max_loss),
        false_break=false_break,
        time_to_failure_bars=time_to_failure,
        persistence_pass=1.0,
    )


def _raw_signal_indices(df: pd.DataFrame, side: str) -> list[tuple[int, float]]:
    if side == "long":
        mask = df["raw_long_breakout"]
        boundaries = df["donchian_upper"]
    else:
        mask = df["raw_short_breakout"]
        boundaries = df["donchian_lower"]
    transitions = mask & (~mask.shift(1).fillna(False))
    out: list[tuple[int, float]] = []
    for idx in np.where(transitions.to_numpy())[0].tolist():
        level = safe_float(boundaries.iloc[idx])
        if math.isfinite(level):
            out.append((int(idx), level))
    return out


def _passes_ema_gate(df: pd.DataFrame, idx: int, side: str, *, ema_slope_bars: int = EMA_SLOPE_BARS) -> bool:
    if idx < max(ema_slope_bars - 1, 0):
        return False
    slope = df["ema_fast"].diff()
    if side == "long":
        return bool(df.iloc[idx]["long_bias"] and (slope.iloc[idx - ema_slope_bars + 1: idx + 1] > 0).sum() >= ema_slope_bars)
    return bool(df.iloc[idx]["short_bias"] and (slope.iloc[idx - ema_slope_bars + 1: idx + 1] < 0).sum() >= ema_slope_bars)


def _passes_macd_gate(df: pd.DataFrame, idx: int, side: str) -> bool:
    row = df.iloc[idx]
    if side == "long":
        return bool(safe_float(row["macd_line"]) > safe_float(row["macd_signal"]) and safe_float(row["macd_hist"]) >= 0)
    return bool(safe_float(row["macd_line"]) < safe_float(row["macd_signal"]) and safe_float(row["macd_hist"]) <= 0)


def collect_variant_trades(
    asset: str,
    df: pd.DataFrame,
    *,
    cost_bps_per_side: float = COST_BPS_PER_SIDE,
    touch_tol_atr: float = TOUCH_TOL_ATR,
    third_touch_window_min: int = THIRD_TOUCH_WINDOW_MIN,
    third_touch_window_max: int = THIRD_TOUCH_WINDOW_MAX,
    ema_slope_bars: int = EMA_SLOPE_BARS,
) -> list[TradeResult]:
    trades: list[TradeResult] = []

    for side in ("long", "short"):
        for signal_idx, level in _raw_signal_indices(df, side):
            trade = _simulate_trade(df, asset, "raw_breakout", side, signal_idx, level, cost_bps_per_side=cost_bps_per_side)
            if trade is not None:
                trades.append(trade)

    for event in _find_third_touch_breakouts(
        df,
        touch_tol_atr=touch_tol_atr,
        third_touch_window_min=third_touch_window_min,
        third_touch_window_max=third_touch_window_max,
    ):
        side = str(event["side"])
        signal_idx = int(event["breakout_idx"])
        level = float(event["boundary_level"])
        base_trade = _simulate_trade(df, asset, "third_touch_only", side, signal_idx, level, cost_bps_per_side=cost_bps_per_side)
        if base_trade is not None:
            trades.append(base_trade)
        if _passes_ema_gate(df, signal_idx, side, ema_slope_bars=ema_slope_bars):
            ema_trade = _simulate_trade(df, asset, "third_touch_plus_ema", side, signal_idx, level, cost_bps_per_side=cost_bps_per_side)
            if ema_trade is not None:
                trades.append(ema_trade)
            if _passes_macd_gate(df, signal_idx, side):
                macd_trade = _simulate_trade(df, asset, "third_touch_plus_ema_macd", side, signal_idx, level, cost_bps_per_side=cost_bps_per_side)
                if macd_trade is not None:
                    trades.append(macd_trade)
    return trades


def _equity_drawdown(returns: pd.Series) -> float:
    if returns.empty:
        return float("nan")
    equity = (1.0 + returns.fillna(0)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def build_outputs(*, cost_bps_per_side: float = COST_BPS_PER_SIDE) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    trade_rows: list[dict] = []
    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        for trade in collect_variant_trades(asset, bars, cost_bps_per_side=cost_bps_per_side):
            trade_rows.append(
                {
                    "asset": trade.asset,
                    "variant": trade.variant,
                    "side": trade.side,
                    "signal_time_utc": fmt_ts(trade.signal_time),
                    "entry_time_utc": fmt_ts(trade.entry_time),
                    "boundary_level": trade.boundary_level,
                    "entry_price": trade.entry_price,
                    "exit_time_utc": fmt_ts(trade.exit_time),
                    "exit_price": trade.exit_price,
                    "net_return": trade.net_return,
                    "max_drawdown": trade.max_drawdown,
                    "false_break": trade.false_break,
                    "time_to_failure_bars": trade.time_to_failure_bars,
                    "persistence_pass": trade.persistence_pass,
                }
            )

    trades_df = pd.DataFrame(trade_rows)
    asset_rows: list[dict] = []
    for asset in ASSETS:
        for variant in VARIANTS:
            subset = trades_df[(trades_df["asset"] == asset) & (trades_df["variant"] == variant)]
            total_return = float((1.0 + subset["net_return"]).prod() - 1.0) if not subset.empty else float("nan")
            asset_rows.append(
                {
                    "asset": asset,
                    "variant": variant,
                    "trades": int(len(subset)),
                    "total_return": total_return,
                    "win_rate": float((subset["net_return"] > 0).mean()) if not subset.empty else float("nan"),
                    "false_break_ratio": float(subset["false_break"].mean()) if not subset.empty else float("nan"),
                    "persistence_pass_rate": float(subset["persistence_pass"].mean()) if not subset.empty else float("nan"),
                    "mean_time_to_failure_bars": float(subset["time_to_failure_bars"].mean()) if not subset.empty else float("nan"),
                    "max_drawdown": _equity_drawdown(subset["net_return"]) if not subset.empty else float("nan"),
                }
            )
    asset_df = pd.DataFrame(asset_rows)

    variant_rows: list[dict] = []
    for variant in VARIANTS:
        subset = asset_df[asset_df["variant"] == variant]
        positive_assets = int((subset["total_return"] > 0).sum()) if not subset.empty else 0
        variant_rows.append(
            {
                "variant": variant,
                "assets_tested": int(subset["asset"].nunique()),
                "positive_assets": positive_assets,
                "mean_total_return": float(subset["total_return"].mean()) if not subset.empty else float("nan"),
                "median_total_return": float(subset["total_return"].median()) if not subset.empty else float("nan"),
                "mean_max_drawdown": float(subset["max_drawdown"].mean()) if not subset.empty else float("nan"),
                "mean_false_break_ratio": float(subset["false_break_ratio"].mean()) if not subset.empty else float("nan"),
                "mean_persistence_pass_rate": float(subset["persistence_pass_rate"].mean()) if not subset.empty else float("nan"),
                "mean_time_to_failure_bars": float(subset["mean_time_to_failure_bars"].mean()) if not subset.empty else float("nan"),
                "mean_trades": float(subset["trades"].mean()) if not subset.empty else float("nan"),
                "mean_win_rate": float(subset["win_rate"].mean()) if not subset.empty else float("nan"),
                "positive_asset_ratio": float(positive_assets / len(subset)) if len(subset) else float("nan"),
            }
        )
    variant_df = pd.DataFrame(variant_rows).sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).reset_index(drop=True)

    best = variant_df.iloc[0]
    raw = variant_df[variant_df["variant"] == "raw_breakout"].iloc[0]
    macd = variant_df[variant_df["variant"] == "third_touch_plus_ema_macd"].iloc[0]
    if (
        safe_float(macd["mean_total_return"]) > safe_float(raw["mean_total_return"])
        and safe_float(macd["mean_false_break_ratio"]) < safe_float(raw["mean_false_break_ratio"])
        and safe_float(macd["mean_trades"]) >= 0.25 * safe_float(raw["mean_trades"])
    ):
        verdict = "hard verdict：third_touch_plus_ema_macd 同时改善了跨资产平均收益与假突破率，且交易压缩未超过 bench 红线；当前可作为 Rank 3 的更窄 structure-confirmation challenger 继续复核，但仍不是 replace-ready / tiny-live ready。"
        next_step = "优先对 third_touch_plus_ema_macd 做一刀轻量 friction / forward 复核，确认增量不是纯样本偶然。"
    elif safe_float(best["mean_total_return"]) > safe_float(raw["mean_total_return"]) and safe_float(best["mean_false_break_ratio"]) < safe_float(raw["mean_false_break_ratio"]):
        verdict = f"hard verdict：{best['variant']} 比 raw_breakout 更诚实，说明 third-touch 链有一定增量；但最强版本还不是 full EMA+MACD 共识，因此当前更像 keep-narrower guard，而不是可直接替换 Live Seat 的 challenger。"
        next_step = "优先继续保留当前最佳窄门版本，并做轻量 forward / friction 复核；若 full EMA+MACD 继续落后，则应把 Rank 3 收窄到更简单 guard。"
    else:
        verdict = "hard verdict：Rank 3 目前没有打赢 raw_breakout；third-touch + EMA/MACD 更像把交易压得更少、但未换来更好收益/假突破率，因此当前应先 bench，不再把它写成 replace-ready 候选。"
        next_step = "默认先 bench；只有在未来换更诚实样本/口径后真出现 blocker reduction，才值得重开。"

    meta_df = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "assets": ", ".join(ASSETS.keys()),
                "sample_window": "Binance 120d 15m（沿用 Rank 1 本地 cache）",
                "ema_fast": EMA_FAST,
                "ema_slow": EMA_SLOW,
                "atr_period": ATR_PERIOD,
                "touch_tolerance_atr": TOUCH_TOL_ATR,
                "third_touch_window": f"{THIRD_TOUCH_WINDOW_MIN}-{THIRD_TOUCH_WINDOW_MAX} bars",
                "breakout_lookahead_bars": BREAKOUT_LOOKAHEAD,
                "stop_atr": STOP_ATR,
                "target_atr": TARGET_ATR,
                "time_stop_bars": TIME_STOP_BARS,
                "cost_bps_per_side": cost_bps_per_side,
                "spec_path": str(SPEC_PATH.relative_to(ROOT)),
                "verdict": verdict,
                "next_step": next_step,
            }
        ]
    )

    event_sample = trades_df.sort_values(["variant", "asset", "signal_time_utc"]).head(24).reset_index(drop=True)
    return variant_df, asset_df, meta_df, event_sample, trades_df


def build_friction_ladder() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    variant_order = {variant: idx for idx, variant in enumerate(FRICTION_VARIANTS)}

    for cost in FRICTION_COSTS:
        variant_df, _, _, _, _ = build_outputs(cost_bps_per_side=cost)
        if variant_df.empty:
            continue
        subset = variant_df[variant_df["variant"].isin(FRICTION_VARIANTS)].copy()
        subset["cost_bps_per_side"] = float(cost)
        rows.append(subset)

    if not rows:
        return pd.DataFrame()

    out = pd.concat(rows, ignore_index=True)
    out["variant_order"] = out["variant"].map(variant_order).fillna(999)
    out = out.sort_values(["cost_bps_per_side", "variant_order"]).drop(columns=["variant_order"]).reset_index(drop=True)
    return out


def derive_friction_verdict(friction_ladder: pd.DataFrame) -> tuple[str, list[str]]:
    if friction_ladder.empty:
        return "friction recheck：当前没有生成可读结果。", ["缺少 friction ladder，暂不补充成本敏感性判断。"]

    def pick(variant: str, cost: float) -> pd.Series | None:
        hit = friction_ladder[
            (friction_ladder["variant"] == variant)
            & (friction_ladder["cost_bps_per_side"] == float(cost))
        ]
        return hit.iloc[0] if not hit.empty else None

    macd6 = pick("third_touch_plus_ema_macd", 6.0)
    macd10 = pick("third_touch_plus_ema_macd", 10.0)
    macd15 = pick("third_touch_plus_ema_macd", 15.0)
    macd20 = pick("third_touch_plus_ema_macd", 20.0)
    ema20 = pick("third_touch_plus_ema", 20.0)
    raw20 = pick("raw_breakout", 20.0)

    if macd20 is not None and float(macd20.get("mean_total_return", 0.0)) > 0:
        headline = (
            "friction recheck：`third_touch_plus_ema_macd` 在 10/15/20bps per side 下仍守住正的跨资产平均收益；"
            "当前更像值得继续做轻量 forward 复核的窄门 structure-confirmation challenger。"
        )
    else:
        headline = (
            "friction recheck：`third_touch_plus_ema_macd` 在更高摩擦下没有守住正收益；"
            "当前更像 keep-narrow guard，而不是可继续朝 replace-ready 推进的候选。"
        )

    bullets: list[str] = []
    if macd6 is not None and macd10 is not None and macd15 is not None and macd20 is not None:
        bullets.append(
            "third_touch_plus_ema_macd cost ladder："
            f"6bps {pct(macd6['mean_total_return'])} → 10bps {pct(macd10['mean_total_return'])} → "
            f"15bps {pct(macd15['mean_total_return'])} → 20bps {pct(macd20['mean_total_return'])}。"
        )
    if ema20 is not None:
        bullets.append(
            f"third_touch_plus_ema 在 20bps 为 {pct(ema20['mean_total_return'])}，可用来判断 Rank 3 的增量是否必须依赖完整 EMA+MACD 共识。"
        )
    if raw20 is not None:
        bullets.append(
            f"raw_breakout 在 20bps 仍为 {pct(raw20['mean_total_return'])}，说明 Rank 3 的改善至少不是靠忽略摩擦得来的假象。"
        )
    bullets.append("但这仍只是同一份 120d / 15m / 3 币种样本上的轻量 friction recheck；还没回答 forward continuity、路由偏差和 live capital cap。")
    return headline, bullets


def build_parameter_stability_drycheck(prepared_bars: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not prepared_bars:
        return pd.DataFrame()

    configs = [
        {"touch_tol_atr": 0.04, "third_touch_window_max": 24, "ema_slope_bars": 3, "label": "tol0.04_win24_slope3"},
        {"touch_tol_atr": 0.05, "third_touch_window_max": 24, "ema_slope_bars": 3, "label": "tol0.05_win24_slope3"},
        {"touch_tol_atr": 0.06, "third_touch_window_max": 24, "ema_slope_bars": 3, "label": "tol0.06_win24_slope3"},
        {"touch_tol_atr": 0.05, "third_touch_window_max": 20, "ema_slope_bars": 3, "label": "tol0.05_win20_slope3"},
        {"touch_tol_atr": 0.05, "third_touch_window_max": 28, "ema_slope_bars": 3, "label": "tol0.05_win28_slope3"},
        {"touch_tol_atr": 0.05, "third_touch_window_max": 24, "ema_slope_bars": 2, "label": "tol0.05_win24_slope2"},
        {"touch_tol_atr": 0.05, "third_touch_window_max": 24, "ema_slope_bars": 4, "label": "tol0.05_win24_slope4"},
    ]

    config_rows: list[dict] = []
    for config in configs:
        trade_rows: list[dict] = []
        for asset, bars in prepared_bars.items():
            for trade in collect_variant_trades(
                asset,
                bars,
                touch_tol_atr=float(config["touch_tol_atr"]),
                third_touch_window_max=int(config["third_touch_window_max"]),
                ema_slope_bars=int(config["ema_slope_bars"]),
            ):
                if trade.variant != "third_touch_plus_ema_macd":
                    continue
                trade_rows.append({
                    "asset": trade.asset,
                    "net_return": trade.net_return,
                    "false_break": trade.false_break,
                })

        trades_df = pd.DataFrame(trade_rows)
        asset_rows: list[dict] = []
        for asset in ASSETS:
            subset = trades_df[trades_df["asset"] == asset] if not trades_df.empty else pd.DataFrame()
            asset_rows.append({
                "asset": asset,
                "trades": int(len(subset)),
                "total_return": float((1.0 + subset["net_return"]).prod() - 1.0) if not subset.empty else float("nan"),
                "false_break_ratio": float(subset["false_break"].mean()) if not subset.empty else float("nan"),
            })
        asset_df = pd.DataFrame(asset_rows)
        positive_assets = int((asset_df["total_return"] > 0).sum()) if not asset_df.empty else 0
        mean_total_return = float(asset_df["total_return"].mean()) if not asset_df.empty else float("nan")
        mean_false_break_ratio = float(asset_df["false_break_ratio"].mean()) if not asset_df.empty else float("nan")
        mean_trades = float(asset_df["trades"].mean()) if not asset_df.empty else float("nan")
        config_rows.append({
            "label": config["label"],
            "touch_tol_atr": config["touch_tol_atr"],
            "third_touch_window_max": config["third_touch_window_max"],
            "ema_slope_bars": config["ema_slope_bars"],
            "assets_tested": len(ASSETS),
            "positive_assets": positive_assets,
            "mean_total_return": mean_total_return,
            "mean_false_break_ratio": mean_false_break_ratio,
            "mean_trades": mean_trades,
            "positive_asset_ratio": float(positive_assets / len(ASSETS)),
        })

    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        return pd.DataFrame()

    positive_configs = int((config_df["mean_total_return"] > 0).sum())
    cross_asset_configs = int((config_df["positive_asset_ratio"] >= (2 / 3)).sum())
    trade_count_configs = int((config_df["mean_trades"] >= 1.0).sum())
    max_false_break = float(config_df["mean_false_break_ratio"].fillna(1.0).max())
    worst_row = config_df.assign(_sort=config_df["mean_total_return"].fillna(-1.0)).sort_values(["_sort", "positive_asset_ratio"]).iloc[0]
    best_row = config_df.assign(_sort=config_df["mean_total_return"].fillna(-1.0), _fb=config_df["mean_false_break_ratio"].fillna(1.0)).sort_values(["_sort", "_fb"], ascending=[False, True]).iloc[0]

    rows = [
        {
            "gate": "positive_neighbor_floor",
            "status": "pass" if positive_configs >= 4 else "fail",
            "actual": f"{positive_configs}/{len(config_df)} configs positive",
            "threshold": ">= 4 positive configs across local parameter neighborhood",
            "why_it_matters": "参数轻微变动后若多数近邻立刻翻负，说明这条线更像单点 lucky pocket，不像稳定 guard。",
        },
        {
            "gate": "cross_asset_neighbor_floor",
            "status": "pass" if cross_asset_configs >= 2 else "fail",
            "actual": f"{cross_asset_configs}/{len(config_df)} configs keep >=2/3 positive assets",
            "threshold": ">= 2 configs keep cross-asset floor",
            "why_it_matters": "如果参数一改就只剩单币种存活，就不该把它写成 desk 级候选。",
        },
        {
            "gate": "trade_count_neighbor_floor",
            "status": "pass" if trade_count_configs >= 4 else "fail",
            "actual": f"{trade_count_configs}/{len(config_df)} configs keep >=1 mean trades / asset",
            "threshold": ">= 4 configs keep >=1 mean trades / asset",
            "why_it_matters": "若邻域内大多配置交易数都塌到接近 0，就说明这条线的可观察性本身不足。",
        },
        {
            "gate": "false_break_neighbor_guard",
            "status": "pass" if max_false_break <= 0.10 else "fail",
            "actual": pct(max_false_break),
            "threshold": "<= 10% max false-break ratio across neighbor configs",
            "why_it_matters": "即便样本稀疏，也要确认参数轻微扰动后不会立刻把假突破率放大。",
        },
        {
            "gate": "worst_neighbor_return_watch",
            "status": "watch" if float(worst_row["mean_total_return"]) <= -0.005 else "pass",
            "actual": f"{worst_row['label']} mean_total_return={pct(worst_row['mean_total_return'])}; positive_assets={int(worst_row['positive_assets'])}/{int(worst_row['assets_tested'])}",
            "threshold": "worst neighbor ideally > -0.50% mean total return",
            "why_it_matters": "记录最弱近邻，防止 base 配置只是在邻域边缘侥幸为正。",
        },
        {
            "gate": "best_neighbor_snapshot",
            "status": "info",
            "actual": f"{best_row['label']} mean_total_return={pct(best_row['mean_total_return'])}; false_break_ratio={pct(best_row['mean_false_break_ratio'])}; mean_trades={num(best_row['mean_trades'], 1)}",
            "threshold": "reference only",
            "why_it_matters": "保留邻域最强快照，方便 desk 判断是否只是一个参数偶然出彩。",
        },
    ]
    return pd.DataFrame(rows)


def derive_parameter_stability_verdict(parameter_stability: pd.DataFrame) -> tuple[str, list[str]]:
    if parameter_stability.empty:
        return "parameter stability：当前没有生成可读结果。", ["缺少 parameter stability artifact，暂不补充参数稳定性判断。"]

    fail_gates = parameter_stability.loc[parameter_stability["status"] == "fail", "gate"].tolist()
    watch_gates = parameter_stability.loc[parameter_stability["status"] == "watch", "gate"].tolist()
    worst_row = parameter_stability.loc[parameter_stability["gate"] == "worst_neighbor_return_watch"]
    best_row = parameter_stability.loc[parameter_stability["gate"] == "best_neighbor_snapshot"]
    worst_actual = str(worst_row.iloc[0]["actual"]) if not worst_row.empty else "-"
    best_actual = str(best_row.iloc[0]["actual"]) if not best_row.empty else "-"

    headline = (
        "parameter stability：`third_touch_plus_ema_macd` 的本地参数邻域仍明显偏薄，"
        "当前不足以把单点正收益写成可升级的 paper candidate / live challenger。"
    )
    if not fail_gates and not watch_gates:
        headline = (
            "parameter stability：`third_touch_plus_ema_macd` 在本地小参数邻域里暂时没有一碰就碎，"
            "但仍要和 trade-count / time stability 一起读，不能单靠这张卡 promotion。"
        )

    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        f"最弱近邻：{worst_actual}。",
        f"最强近邻快照：{best_actual}。",
        "这张卡回答的是本地参数邻域韧性；若邻域大多时候都接近无交易/单币存活，就应优先 park。",
    ]
    return headline, bullets


def build_trade_count_honesty(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    subset = trades_df[trades_df["variant"] == "third_touch_plus_ema_macd"].copy()
    if subset.empty:
        return pd.DataFrame()

    subset["entry_ts"] = pd.to_datetime(subset["entry_time_utc"], utc=True)
    asset_counts = subset.groupby("asset").size()
    total_trades = int(len(subset))
    active_assets = int(asset_counts.size)
    max_asset_share = float((asset_counts / total_trades).max()) if total_trades else float("nan")
    month_breadth = subset.groupby("asset")["entry_ts"].apply(lambda s: s.dt.strftime("%Y-%m").nunique())

    max_gap_days = float("nan")
    for _, asset_df in subset.sort_values("entry_ts").groupby("asset"):
        deltas = asset_df["entry_ts"].diff().dropna().dt.total_seconds() / 86400.0
        if not deltas.empty:
            asset_gap = float(deltas.max())
            max_gap_days = asset_gap if not math.isfinite(max_gap_days) else max(max_gap_days, asset_gap)

    rows = [
        {
            "gate": "total_trade_floor",
            "status": "pass" if total_trades >= 9 else "fail",
            "actual": f"total trades = {total_trades}",
            "threshold": ">= 9 total trades for 3-way time split",
            "why_it_matters": "至少要有最小样本量，才配谈 3 段时间稳定性；否则只能如实承认这是极稀疏 pocket。",
        },
        {
            "gate": "asset_coverage_floor",
            "status": "pass" if active_assets == len(ASSETS) else "fail",
            "actual": f"active assets = {active_assets}/{len(ASSETS)}",
            "threshold": "all 3 assets should print at least one trade",
            "why_it_matters": "如果只有单一币种留下信号，它更像局部结构 pocket，不够支撑 desk 级候选。",
        },
        {
            "gate": "min_asset_trade_floor",
            "status": "pass" if not asset_counts.empty and int(asset_counts.min()) >= 2 else "fail",
            "actual": f"min asset trades = {int(asset_counts.min()) if not asset_counts.empty else 0}",
            "threshold": ">= 2 trades on every active asset",
            "why_it_matters": "至少每个活跃资产要不止一笔，否则 trade-count honesty 过于脆弱。",
        },
        {
            "gate": "calendar_breadth_floor",
            "status": "pass" if not month_breadth.empty and int(month_breadth.min()) >= 2 else "fail",
            "actual": f"min active months per asset = {int(month_breadth.min()) if not month_breadth.empty else 0}",
            "threshold": ">= 2 active months on every active asset",
            "why_it_matters": "至少跨过不止一个月，避免所有信号都挤在单段局部行情。",
        },
        {
            "gate": "asset_concentration_watch",
            "status": "pass" if math.isfinite(max_asset_share) and max_asset_share <= 0.60 else "watch",
            "actual": pct(max_asset_share),
            "threshold": "<= 60% of trades from one asset",
            "why_it_matters": "若几乎所有交易都来自一个币种，就不该把 headline 误写成跨资产稳定。",
        },
        {
            "gate": "idle_gap_guard",
            "status": "fail" if math.isfinite(max_gap_days) and max_gap_days > 30.0 else "pass",
            "actual": f"{max_gap_days:.1f} days" if math.isfinite(max_gap_days) else "single-print / no gap yet",
            "threshold": "<= 30d max gap between trades per asset",
            "why_it_matters": "若交易之间长期空窗，就更像极稀疏结构警报，而不是可连续观察的候选。",
        },
    ]
    return pd.DataFrame(rows)


def derive_trade_count_honesty_verdict(trade_count_honesty: pd.DataFrame) -> tuple[str, list[str]]:
    if trade_count_honesty.empty:
        return "trade-count honesty：当前没有生成可读结果。", ["缺少 trade-count artifact，暂不补充样本诚实性判断。"]

    fail_gates = trade_count_honesty.loc[trade_count_honesty["status"] == "fail", "gate"].tolist()
    watch_gates = trade_count_honesty.loc[trade_count_honesty["status"] == "watch", "gate"].tolist()
    headline = (
        "trade-count honesty：`third_touch_plus_ema_macd` 的有效交易过于稀疏，当前只能保留为 keep-narrow guard 证据，"
        "还不够资格往 paper candidate / live challenger 方向写。"
    )
    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        "这张卡回答的是样本够不够诚实，不是收益 headline 看起来漂不漂亮。",
        "若最优版本几乎只剩单笔或单资产信号，最诚实的 desk 结论应是 keep-narrow / one-more-light-check，不能偷升格。",
    ]
    return headline, bullets


def build_time_stability_drycheck(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    subset = trades_df[trades_df["variant"] == "third_touch_plus_ema_macd"].copy()
    if subset.empty:
        return pd.DataFrame()

    subset["entry_ts"] = pd.to_datetime(subset["entry_time_utc"], utc=True)
    total_trades = int(len(subset))
    enough_split = total_trades >= 9
    enough_assets = int(subset["asset"].nunique()) == len(ASSETS)

    rows = [
        {
            "gate": "three_bucket_sample_floor",
            "status": "pass" if enough_split else "fail",
            "actual": f"total trades = {total_trades}",
            "threshold": ">= 9 trades before attempting early/mid/late split",
            "why_it_matters": "没有最小样本量，就不该假装自己做出了时间稳定性结论。",
        },
        {
            "gate": "bucket_asset_coverage",
            "status": "pass" if enough_assets else "fail",
            "actual": f"assets with trades = {int(subset['asset'].nunique())}/{len(ASSETS)}",
            "threshold": "all 3 assets should appear before 3-way time split",
            "why_it_matters": "如果时间切片前就只剩少数资产，时间稳定性读法天然不可信。",
        },
    ]

    if enough_split and enough_assets:
        q1, q2 = subset["entry_ts"].quantile([1 / 3, 2 / 3])
        start = subset["entry_ts"].min() - pd.Timedelta(seconds=1)
        end = subset["entry_ts"].max() + pd.Timedelta(seconds=1)
        subset["time_bucket"] = pd.cut(subset["entry_ts"], bins=[start, q1, q2, end], labels=["early", "mid", "late"])
        bucket_rows = []
        for bucket, bucket_df in subset.groupby("time_bucket", observed=False):
            if pd.isna(bucket) or bucket_df.empty:
                continue
            asset_stats = bucket_df.groupby("asset")["net_return"].apply(lambda s: float((1.0 + s.astype(float)).prod() - 1.0))
            bucket_rows.append({
                "time_bucket": str(bucket),
                "assets_present": int(bucket_df["asset"].nunique()),
                "positive_assets": int((asset_stats > 0).sum()),
                "mean_asset_return": float(asset_stats.mean()),
                "trades": int(len(bucket_df)),
            })
        bucket_df = pd.DataFrame(bucket_rows)
        positive_buckets = int((bucket_df["mean_asset_return"] > 0).sum()) if not bucket_df.empty else 0
        min_bucket_trades = int(bucket_df["trades"].min()) if not bucket_df.empty else 0
        rows.extend([
            {
                "gate": "positive_bucket_floor",
                "status": "pass" if positive_buckets >= 2 else "fail",
                "actual": f"{positive_buckets}/3 positive time buckets",
                "threshold": ">= 2 positive buckets out of 3",
                "why_it_matters": "至少多数时间窗要守住正向，才能说它不只是单段 regime pocket。",
            },
            {
                "gate": "bucket_trade_floor",
                "status": "pass" if min_bucket_trades >= 2 else "fail",
                "actual": f"min bucket trades = {min_bucket_trades}",
                "threshold": ">= 2 trades in every time bucket",
                "why_it_matters": "即便样本刚够切三段，每段也不能只剩 0/1 笔交易。",
            },
        ])
    else:
        rows.extend([
            {
                "gate": "positive_bucket_floor",
                "status": "fail",
                "actual": "not attempted: sample too sparse for honest split",
                "threshold": ">= 2 positive buckets out of 3",
                "why_it_matters": "当前更重要的是先如实承认样本太薄，而不是捏一个看似完整的时间切片。",
            },
            {
                "gate": "bucket_trade_floor",
                "status": "fail",
                "actual": "not attempted: sample too sparse for honest split",
                "threshold": ">= 2 trades in every time bucket",
                "why_it_matters": "若还没到能切桶的样本量，时间稳定性默认视作未通过。",
            },
        ])

    return pd.DataFrame(rows)


def derive_time_stability_verdict(time_stability: pd.DataFrame) -> tuple[str, list[str]]:
    if time_stability.empty:
        return "time stability：当前没有生成可读结果。", ["缺少 time stability artifact，暂不补充时间稳定性判断。"]

    fail_gates = time_stability.loc[time_stability["status"] == "fail", "gate"].tolist()
    watch_gates = time_stability.loc[time_stability["status"] == "watch", "gate"].tolist()
    headline = (
        "time stability：`third_touch_plus_ema_macd` 当前样本薄到还不配做诚实的 early/mid/late 三段切片，"
        "因此只能继续停在 keep-narrow / one-more-light-check。"
    )
    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        "这不是 forward continuity 失败，而是更基础的事实：样本量还没达到能做时间稳定性判断的最低诚实门槛。",
        "当时间稳定性都还无法诚实起表时，desk 读法应优先是 park 或 keep-narrow guard，而不是 promotion。",
    ]
    return headline, bullets


def render_table(df: pd.DataFrame, *, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if col in percent_cols:
                text = pct(val)
            elif isinstance(val, (float, np.floating, int, np.integer)) and not isinstance(val, bool):
                text = num(val, digits_cols.get(col, 2))
            else:
                text = str(val)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def write_report(
    variant_df: pd.DataFrame,
    asset_df: pd.DataFrame,
    meta_df: pd.DataFrame,
    event_sample: pd.DataFrame,
    friction_ladder: pd.DataFrame,
    trade_count_honesty: pd.DataFrame,
    time_stability: pd.DataFrame,
    parameter_stability: pd.DataFrame,
) -> None:
    ensure_dir(SITE_DIR)
    spec_note = "clean_room spec 已存在，当前这页把 Rank 3 从 spec-only 推到 first verdict。"
    meta = meta_df.iloc[0]
    best = variant_df.iloc[0] if not variant_df.empty else pd.Series(dtype=object)
    friction_cols = [
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "mean_false_break_ratio",
        "positive_asset_ratio",
        "mean_trades",
        "mean_time_to_failure_bars",
    ]
    honesty_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Rank 3 · third-touch + EMA/MACD confluence · first verdict</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1160px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
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
  <h1>Scout Seat · Rank 3：third-touch + EMA/MACD confluence · first verdict</h1>
  <p class="muted">生成时间：{escape(str(meta['generated_at_utc']))} ｜ {escape(spec_note)}</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(str(meta['verdict']))}</b></p>
    <ul>
      <li>当前最佳版本：<code>{escape(str(best.get('variant', '-')))}</code></li>
      <li>sample：<code>{escape(str(meta['sample_window']))}</code></li>
      <li>这页回答的是 performance first verdict，不再只是 implementation-ready spec。</li>
    </ul>
  </div>

  <div class="card">
    <h2>variant aggregate</h2>
    {render_table(variant_df, percent_cols={'mean_total_return','median_total_return','mean_max_drawdown','mean_false_break_ratio','mean_persistence_pass_rate','mean_win_rate','positive_asset_ratio'}, digits_cols={'mean_trades':2,'mean_time_to_failure_bars':2})}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv</code></p>
  </div>

  <div class="card">
    <h2>轻量 friction recheck</h2>
    <p><b>{escape(str(meta.get('friction_recheck_verdict', '-')))}</b></p>
    <ul>
      <li>{escape(str(meta.get('friction_bullet_1', '-')))}</li>
      <li>{escape(str(meta.get('friction_bullet_2', '-')))}</li>
      <li>{escape(str(meta.get('friction_bullet_3', '-')))}</li>
      <li>{escape(str(meta.get('friction_bullet_4', '-')))}</li>
    </ul>
    {render_table(friction_ladder[friction_cols] if not friction_ladder.empty else friction_ladder, percent_cols={'mean_total_return','mean_false_break_ratio','positive_asset_ratio'}, digits_cols={'cost_bps_per_side':0,'mean_trades':2,'mean_time_to_failure_bars':2})}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv</code> ｜ 这里只做成本敏感性快检，不引入新 bar，也不把它误写成 forward 证据。</p>
  </div>

  <div class="card">
    <h2>trade-count honesty / cadence dry-check</h2>
    <p><b>{escape(str(meta.get('trade_count_honesty_verdict', '-')))}</b></p>
    <ul>
      <li>{escape(str(meta.get('trade_count_bullet_1', '-')))}</li>
      <li>{escape(str(meta.get('trade_count_bullet_2', '-')))}</li>
      <li>{escape(str(meta.get('trade_count_bullet_3', '-')))}</li>
    </ul>
    {render_table(trade_count_honesty[honesty_cols] if not trade_count_honesty.empty else trade_count_honesty)}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/trade_count_honesty.csv</code> ｜ 这张卡不追求好看，只回答当前最优版本的交易分布够不够诚实。</p>
  </div>

  <div class="card">
    <h2>time stability dry-check</h2>
    <p><b>{escape(str(meta.get('time_stability_verdict', '-')))}</b></p>
    <ul>
      <li>{escape(str(meta.get('time_stability_bullet_1', '-')))}</li>
      <li>{escape(str(meta.get('time_stability_bullet_2', '-')))}</li>
      <li>{escape(str(meta.get('time_stability_bullet_3', '-')))}</li>
    </ul>
    {render_table(time_stability[honesty_cols] if not time_stability.empty else time_stability)}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/time_stability_drycheck.csv</code> ｜ 若样本量连三段时间切片都不配做，就如实显示 fail，而不是伪造稳定性。
</p>
  </div>

  <div class="card">
    <h2>parameter stability dry-check</h2>
    <p><b>{escape(str(meta.get('parameter_stability_verdict', '-')))}</b></p>
    <ul>
      <li>{escape(str(meta.get('parameter_stability_bullet_1', '-')))}</li>
      <li>{escape(str(meta.get('parameter_stability_bullet_2', '-')))}</li>
      <li>{escape(str(meta.get('parameter_stability_bullet_3', '-')))}</li>
      <li>{escape(str(meta.get('parameter_stability_bullet_4', '-')))}</li>
    </ul>
    {render_table(parameter_stability[honesty_cols] if not parameter_stability.empty else parameter_stability)}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/parameter_stability_drycheck.csv</code> ｜ 这里只做本地小参数邻域的诚实干检，不做大规模 optimizer。
</p>
  </div>

  <div class="card">
    <h2>per-asset summary</h2>
    {render_table(asset_df, percent_cols={'total_return','win_rate','false_break_ratio','persistence_pass_rate','max_drawdown'}, digits_cols={'trades':0,'mean_time_to_failure_bars':2})}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/asset_summary.csv</code></p>
  </div>

  <div class="card">
    <h2>sample events</h2>
    {render_table(event_sample, percent_cols={'net_return','max_drawdown','false_break'}, digits_cols={'boundary_level':4,'entry_price':4,'exit_price':4,'time_to_failure_bars':2,'persistence_pass':0})}
    <p class="muted">artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/event_sample.csv</code></p>
  </div>

  <div class="card">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>若 full EMA+MACD 版本没赢，不要硬吹成更高级。</b> 这条线的价值只在于更诚实地过滤假突破，而不是因为规则更复杂就自动更强。</li>
      <li><b>trade compression 必须一起看。</b> 如果收益改善只来自极度减少交易，那它更像 guard，不像可替换 Live Seat 的 challenger。</li>
      <li><b>当前新补的 honesty 卡优先级更高。</b> 一旦 trade-count / time stability 直接显示样本过薄，就应先接受 keep-narrow / park 读法，而不是继续靠 headline 收益自我安慰。</li>
      <li><b>这仍不是 replace-ready / tiny-live ready。</b> 最多只是帮 desk 更快判断 Rank 3 应 keep-narrow 还是直接 bench。</li>
    </ul>
  </div>

  <div class="card">
    <h2>下一步</h2>
    <p><b>{escape(str(meta['next_step']))}</b></p>
    <p class="muted">如需回看冻结口径，可参考既有 spec artifact：<code>reports/artifacts/scout_third_touch_ema_macd_15m/clean_room_spec_v1.csv</code></p>
  </div>
</body>
</html>
'''
    REPORT_PATH.write_text(html, encoding='utf-8')


def main() -> int:
    ensure_dir(ART_DIR)
    prepared_bars = {asset: prepare_bars(asset, symbol) for asset, symbol in ASSETS.items()}
    variant_df, asset_df, meta_df, event_sample, trades_df = build_outputs()
    friction_ladder = build_friction_ladder()
    trade_count_honesty = build_trade_count_honesty(trades_df)
    time_stability = build_time_stability_drycheck(trades_df)
    parameter_stability = build_parameter_stability_drycheck(prepared_bars)
    friction_headline, friction_bullets = derive_friction_verdict(friction_ladder)
    trade_count_headline, trade_count_bullets = derive_trade_count_honesty_verdict(trade_count_honesty)
    time_stability_headline, time_stability_bullets = derive_time_stability_verdict(time_stability)
    parameter_stability_headline, parameter_stability_bullets = derive_parameter_stability_verdict(parameter_stability)
    strong_fail = (not trade_count_honesty.empty and (trade_count_honesty['status'] == 'fail').sum() >= 2) or (not time_stability.empty and (time_stability['status'] == 'fail').sum() >= 2) or (not parameter_stability.empty and (parameter_stability['status'] == 'fail').sum() >= 2)
    if strong_fail:
        meta_df['verdict'] = "hard verdict：Rank 3 `third_touch_plus_ema_macd` 已补齐最小 Light Stability Pack 后，仍显示样本与邻域都过薄；当前最诚实的 desk 读法应是 `park`，保留为 structure-filter evidence，不进入 paper candidate pool，也不争夺 Live Seat。"
        meta_df['next_step'] = "默认 park；只有当未来来自更宽历史样本或更诚实 repo/paper 复现出现明显更厚的 trade-count / cross-asset 证据时，才值得重开。"
    for idx in range(4):
        key = f"friction_bullet_{idx + 1}"
        meta_df[key] = friction_bullets[idx] if idx < len(friction_bullets) else "-"
    for idx in range(3):
        key = f"trade_count_bullet_{idx + 1}"
        meta_df[key] = trade_count_bullets[idx] if idx < len(trade_count_bullets) else "-"
    for idx in range(3):
        key = f"time_stability_bullet_{idx + 1}"
        meta_df[key] = time_stability_bullets[idx] if idx < len(time_stability_bullets) else "-"
    for idx in range(4):
        key = f"parameter_stability_bullet_{idx + 1}"
        meta_df[key] = parameter_stability_bullets[idx] if idx < len(parameter_stability_bullets) else "-"
    meta_df["friction_recheck_verdict"] = friction_headline
    meta_df["trade_count_honesty_verdict"] = trade_count_headline
    meta_df["time_stability_verdict"] = time_stability_headline
    meta_df["parameter_stability_verdict"] = parameter_stability_headline
    variant_df.to_csv(VARIANT_PATH, index=False)
    asset_df.to_csv(ASSET_PATH, index=False)
    meta_df.to_csv(TRIAL_META_PATH, index=False)
    event_sample.to_csv(EVENT_SAMPLE_PATH, index=False)
    trades_df.to_csv(TRADE_DETAIL_PATH, index=False)
    friction_ladder.to_csv(FRICTION_LADDER_PATH, index=False)
    trade_count_honesty.to_csv(TRADE_COUNT_HONESTY_PATH, index=False)
    time_stability.to_csv(TIME_STABILITY_PATH, index=False)
    parameter_stability.to_csv(PARAM_STABILITY_PATH, index=False)
    write_report(variant_df, asset_df, meta_df, event_sample, friction_ladder, trade_count_honesty, time_stability, parameter_stability)
    print('[ok] scout third-touch EMA/MACD first verdict generated')
    print('[artifact]', VARIANT_PATH)
    print('[artifact]', FRICTION_LADDER_PATH)
    print('[artifact]', TRADE_COUNT_HONESTY_PATH)
    print('[artifact]', TIME_STABILITY_PATH)
    print('[artifact]', PARAM_STABILITY_PATH)
    print('[site]', REPORT_PATH)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
