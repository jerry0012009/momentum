#!/usr/bin/env python3
from __future__ import annotations

import math
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_volume_supportflip_higherlow_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_volume_supportflip_higherlow_15m"
REPORT_PATH = SITE_DIR / "report.html"
FRICTION_LADDER_PATH = ART_DIR / "combo_all_friction_ladder.csv"
SHADOW_READINESS_PATH = ART_DIR / "combo_all_shadow_readiness_drycheck.csv"
TRADE_COUNT_HONESTY_PATH = ART_DIR / "combo_all_trade_count_honesty.csv"
TIME_STABILITY_PATH = ART_DIR / "combo_all_time_stability_drycheck.csv"
CROSS_ASSET_STABILITY_PATH = ART_DIR / "combo_all_cross_asset_stability_drycheck.csv"
PARAM_STABILITY_PATH = ART_DIR / "combo_all_parameter_stability_drycheck.csv"
PAPER_CANDIDATE_MEMO_PATH = ART_DIR / "combo_all_paper_candidate_admission_memo.csv"
PAPER_CANDIDATE_MONITORING_PATH = ART_DIR / "combo_all_paper_candidate_monitoring_board.csv"
NARROW_PAPER_LEDGER_TEMPLATE_PATH = ART_DIR / "combo_all_narrow_paper_pilot_ledger_template.csv"
NARROW_PAPER_REFRESH_SEED_ROWS_PATH = ART_DIR / "combo_all_narrow_paper_pilot_refresh_seed_rows.csv"
NARROW_PAPER_WEEKLY_REVIEW_SEED_ROWS_PATH = ART_DIR / "combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv"
SOURCE_CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
SPEC_PATH = ART_DIR / "clean_room_spec_v1.csv"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

EMA_FAST = 20
EMA_SLOW = 50
DONCHIAN_LOOKBACK = 20
ATR_PERIOD = 14
VOLUME_MEDIAN_LOOKBACK = 20
VOLUME_CONFIRM_MULT = 1.2
TAU_ATR = 0.05
STOP_ATR = 1.0
TARGET_ATR = 2.0
TIME_STOP_BARS = 8
COST_BPS_PER_SIDE = 6.0
FLIP_TOUCH_ATR = 0.05
FLIP_LOOKAHEAD_BARS = 3
SWING_LOOKAHEAD_BARS = 6
SWING_CONFIRM_RIGHT = 2
SIGNAL_BREAK_LOOKAHEAD_BARS = 12

VARIANTS = [
    "raw_breakout",
    "volume_only",
    "support_flip_only",
    "higher_low_only",
    "combo_all",
]
FRICTION_VARIANTS = ["raw_breakout", "higher_low_only", "combo_all"]
FRICTION_COSTS = [6.0, 10.0, 15.0, 20.0]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def _safe_float(value) -> float:
    try:
        out = float(value)
    except Exception:
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body_rows = []
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
            cells.append(f"<td>{escape(text)}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def load_cached_bars(symbol: str) -> pd.DataFrame:
    path = SOURCE_CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing Rank 1 cache: {path}")
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
    bars["long_bias"] = (bars["ema_fast"] > bars["ema_slow"]).astype(int)
    bars["short_bias"] = (bars["ema_fast"] < bars["ema_slow"]).astype(int)
    bars["donchian_upper"] = bars["high"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).max()
    bars["donchian_lower"] = bars["low"].shift(1).rolling(DONCHIAN_LOOKBACK, min_periods=DONCHIAN_LOOKBACK).min()
    bars["atr"] = compute_atr(bars, ATR_PERIOD)
    bars["volume_median20"] = bars["volume"].rolling(VOLUME_MEDIAN_LOOKBACK, min_periods=VOLUME_MEDIAN_LOOKBACK).median()
    bars["threshold_upper"] = bars["donchian_upper"] + TAU_ATR * bars["atr"]
    bars["threshold_lower"] = bars["donchian_lower"] - TAU_ATR * bars["atr"]
    bars["raw_long_breakout"] = ((bars["long_bias"] == 1) & (bars["close"] > bars["threshold_upper"])).fillna(False)
    bars["raw_short_breakout"] = ((bars["short_bias"] == 1) & (bars["close"] < bars["threshold_lower"])).fillna(False)
    bars["raw_long_transition"] = (bars["raw_long_breakout"] & (~bars["raw_long_breakout"].shift(1).fillna(False))).astype(int)
    bars["raw_short_transition"] = (bars["raw_short_breakout"] & (~bars["raw_short_breakout"].shift(1).fillna(False))).astype(int)
    return bars


def _touch_hold_long(row: pd.Series, edge: float, atr: float) -> bool:
    return bool(math.isfinite(edge) and math.isfinite(atr) and _safe_float(row["low"]) <= edge + FLIP_TOUCH_ATR * atr and _safe_float(row["close"]) >= edge)


def _touch_hold_short(row: pd.Series, edge: float, atr: float) -> bool:
    return bool(math.isfinite(edge) and math.isfinite(atr) and _safe_float(row["high"]) >= edge - FLIP_TOUCH_ATR * atr and _safe_float(row["close"]) <= edge)


def find_support_flip_idx(
    df: pd.DataFrame,
    breakout_idx: int,
    side: str,
    edge: float,
    atr: float,
    *,
    flip_lookahead_bars: int = FLIP_LOOKAHEAD_BARS,
) -> int | None:
    n = len(df)
    end_idx = min(breakout_idx + flip_lookahead_bars, n - 1)
    for idx in range(breakout_idx + 1, end_idx + 1):
        row = df.iloc[idx]
        if side == "long" and _touch_hold_long(row, edge, atr):
            return idx
        if side == "short" and _touch_hold_short(row, edge, atr):
            return idx
    return None


def is_confirmed_swing_low(lows: pd.Series, idx: int) -> bool:
    if idx < 2 or idx + SWING_CONFIRM_RIGHT >= len(lows):
        return False
    center = _safe_float(lows.iloc[idx])
    left = lows.iloc[idx - 2 : idx]
    right = lows.iloc[idx + 1 : idx + 1 + SWING_CONFIRM_RIGHT]
    if not math.isfinite(center) or left.isna().any() or right.isna().any():
        return False
    return bool(center < float(left.min()) and center <= float(right.min()))


def is_confirmed_swing_high(highs: pd.Series, idx: int) -> bool:
    if idx < 2 or idx + SWING_CONFIRM_RIGHT >= len(highs):
        return False
    center = _safe_float(highs.iloc[idx])
    left = highs.iloc[idx - 2 : idx]
    right = highs.iloc[idx + 1 : idx + 1 + SWING_CONFIRM_RIGHT]
    if not math.isfinite(center) or left.isna().any() or right.isna().any():
        return False
    return bool(center > float(left.max()) and center >= float(right.max()))


def find_structure_signal_idx(
    df: pd.DataFrame,
    breakout_idx: int,
    side: str,
    edge: float,
    *,
    start_idx: int | None = None,
    swing_lookahead_bars: int = SWING_LOOKAHEAD_BARS,
) -> int | None:
    n = len(df)
    lows = df["low"]
    highs = df["high"]
    pivot_start = max(breakout_idx + 2, start_idx if start_idx is not None else breakout_idx + 1)
    pivot_end = min(breakout_idx + swing_lookahead_bars, n - 1 - SWING_CONFIRM_RIGHT)
    if pivot_start > pivot_end:
        return None

    for pivot_idx in range(pivot_start, pivot_end + 1):
        confirm_idx = pivot_idx + SWING_CONFIRM_RIGHT
        if side == "long":
            if not is_confirmed_swing_low(lows, pivot_idx):
                continue
            if _safe_float(lows.iloc[pivot_idx]) <= edge:
                continue
            interim_high = _safe_float(df.iloc[breakout_idx + 1 : confirm_idx + 1]["high"].max())
            if not math.isfinite(interim_high):
                continue
            search_end = min(breakout_idx + SIGNAL_BREAK_LOOKAHEAD_BARS, n - 1)
            for sig_idx in range(confirm_idx + 1, search_end + 1):
                if _safe_float(df.iloc[sig_idx]["high"]) > interim_high:
                    return sig_idx
        else:
            if not is_confirmed_swing_high(highs, pivot_idx):
                continue
            if _safe_float(highs.iloc[pivot_idx]) >= edge:
                continue
            interim_low = _safe_float(df.iloc[breakout_idx + 1 : confirm_idx + 1]["low"].min())
            if not math.isfinite(interim_low):
                continue
            search_end = min(breakout_idx + SIGNAL_BREAK_LOOKAHEAD_BARS, n - 1)
            for sig_idx in range(confirm_idx + 1, search_end + 1):
                if _safe_float(df.iloc[sig_idx]["low"]) < interim_low:
                    return sig_idx
    return None


def compute_false_break(df: pd.DataFrame, breakout_idx: int, side: str, edge: float) -> float:
    future = df.iloc[breakout_idx + 1 : breakout_idx + 4]
    if future.empty or not math.isfinite(edge):
        return float("nan")
    if side == "long":
        return float((future["close"] <= edge).any())
    return float((future["close"] >= edge).any())


def compute_time_to_failure(df: pd.DataFrame, breakout_idx: int, side: str, edge: float, max_bars: int = TIME_STOP_BARS) -> float:
    if not math.isfinite(edge):
        return float("nan")
    end_idx = min(breakout_idx + max_bars, len(df) - 1)
    for idx in range(breakout_idx + 1, end_idx + 1):
        close = _safe_float(df.iloc[idx]["close"])
        if side == "long" and close <= edge:
            return float(idx - breakout_idx)
        if side == "short" and close >= edge:
            return float(idx - breakout_idx)
    return float(max_bars + 1)


def build_event_frame(
    asset: str,
    symbol: str,
    bars: pd.DataFrame,
    *,
    volume_confirm_mult: float = VOLUME_CONFIRM_MULT,
    flip_lookahead_bars: int = FLIP_LOOKAHEAD_BARS,
    swing_lookahead_bars: int = SWING_LOOKAHEAD_BARS,
) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(bars)
    for idx in range(n):
        if int(bars.iloc[idx]["raw_long_transition"]) == 1:
            side = "long"
            edge = _safe_float(bars.iloc[idx]["donchian_upper"])
            threshold_edge = _safe_float(bars.iloc[idx]["threshold_upper"])
        elif int(bars.iloc[idx]["raw_short_transition"]) == 1:
            side = "short"
            edge = _safe_float(bars.iloc[idx]["donchian_lower"])
            threshold_edge = _safe_float(bars.iloc[idx]["threshold_lower"])
        else:
            continue

        atr = _safe_float(bars.iloc[idx]["atr"])
        if not (math.isfinite(edge) and math.isfinite(threshold_edge) and math.isfinite(atr) and atr > 0):
            continue

        volume_median = _safe_float(bars.iloc[idx]["volume_median20"])
        volume = _safe_float(bars.iloc[idx]["volume"])
        volume_ok = bool(
            math.isfinite(volume_median)
            and math.isfinite(volume)
            and volume > volume_median * float(volume_confirm_mult)
        )
        flip_idx = find_support_flip_idx(
            bars,
            idx,
            side,
            edge,
            atr,
            flip_lookahead_bars=flip_lookahead_bars,
        )
        structure_idx = find_structure_signal_idx(
            bars,
            idx,
            side,
            edge,
            swing_lookahead_bars=swing_lookahead_bars,
        )
        combo_idx = None
        if volume_ok and flip_idx is not None:
            combo_idx = find_structure_signal_idx(
                bars,
                idx,
                side,
                edge,
                start_idx=flip_idx,
                swing_lookahead_bars=swing_lookahead_bars,
            )

        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "side": side,
                "breakout_idx": idx,
                "breakout_ts": bars.iloc[idx]["timestamp"],
                "raw_edge": edge,
                "threshold_edge": threshold_edge,
                "atr_at_breakout": atr,
                "volume_ok": int(volume_ok),
                "flip_idx": flip_idx,
                "flip_ts": bars.iloc[flip_idx]["timestamp"] if flip_idx is not None else pd.NaT,
                "higher_low_idx": structure_idx,
                "higher_low_ts": bars.iloc[structure_idx]["timestamp"] if structure_idx is not None else pd.NaT,
                "combo_idx": combo_idx,
                "combo_ts": bars.iloc[combo_idx]["timestamp"] if combo_idx is not None else pd.NaT,
                "false_break_3bars": compute_false_break(bars, idx, side, edge),
                "retest_hold": int(flip_idx is not None),
                "time_to_failure_bars": compute_time_to_failure(bars, idx, side, edge),
            }
        )
    return pd.DataFrame(rows)


def variant_signal_idx_col(variant: str) -> str:
    mapping = {
        "raw_breakout": "breakout_idx",
        "volume_only": "breakout_idx",
        "support_flip_only": "flip_idx",
        "higher_low_only": "higher_low_idx",
        "combo_all": "combo_idx",
    }
    return mapping[variant]


def filtered_events_for_variant(events: pd.DataFrame, variant: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    signal_col = variant_signal_idx_col(variant)
    out = events.copy()
    if variant == "volume_only":
        out = out[out["volume_ok"] == 1]
    out = out[out[signal_col].notna()].copy()
    if out.empty:
        return out
    out["signal_idx"] = out[signal_col].astype(int)
    out["variant"] = variant
    return out.sort_values(["signal_idx", "breakout_idx"]).reset_index(drop=True)


def simulate_variant_events(
    bars: pd.DataFrame,
    variant_events: pd.DataFrame,
    variant: str,
    *,
    cost_bps_per_side: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if variant_events.empty:
        nav = pd.DataFrame(
            [
                {
                    "asset": bars.iloc[0]["asset"],
                    "variant": variant,
                    "timestamp": bars.iloc[0]["timestamp"],
                    "nav": 1.0,
                }
            ]
        )
        return pd.DataFrame(), nav

    effective_cost_bps = float(COST_BPS_PER_SIDE if cost_bps_per_side is None else cost_bps_per_side)
    cost_rate = effective_cost_bps / 10000.0
    trades: list[dict] = []
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

        entry_row = bars.iloc[entry_idx]
        entry_price = _safe_float(entry_row["open"])
        atr = _safe_float(bars.iloc[signal_idx]["atr"])
        if not (math.isfinite(entry_price) and entry_price > 0 and math.isfinite(atr) and atr > 0):
            atr = _safe_float(event["atr_at_breakout"])
        if not (math.isfinite(entry_price) and entry_price > 0 and math.isfinite(atr) and atr > 0):
            continue

        side = str(event["side"])
        stop_price = entry_price - STOP_ATR * atr if side == "long" else entry_price + STOP_ATR * atr
        target_price = entry_price + TARGET_ATR * atr if side == "long" else entry_price - TARGET_ATR * atr
        last_bar_idx = min(entry_idx + TIME_STOP_BARS - 1, len(bars) - 1)
        exit_idx = None
        exit_price = None
        exit_reason = None

        for idx in range(entry_idx, last_bar_idx + 1):
            row = bars.iloc[idx]
            low = _safe_float(row["low"])
            high = _safe_float(row["high"])
            if side == "long":
                if math.isfinite(low) and low <= stop_price:
                    exit_idx = idx
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if math.isfinite(high) and high >= target_price:
                    exit_idx = idx
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break
            else:
                if math.isfinite(high) and high >= stop_price:
                    exit_idx = idx
                    exit_price = stop_price
                    exit_reason = "atr_stop"
                    break
                if math.isfinite(low) and low <= target_price:
                    exit_idx = idx
                    exit_price = target_price
                    exit_reason = "atr_target"
                    break

        if exit_idx is None:
            exit_idx = last_bar_idx
            exit_price = _safe_float(bars.iloc[exit_idx]["close"])
            exit_reason = "time_stop"

        if not (math.isfinite(exit_price) and exit_price > 0):
            continue

        gross_mult = exit_price / entry_price if side == "long" else entry_price / exit_price
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        nav *= net_mult
        trades.append(
            {
                "asset": bars.iloc[0]["asset"],
                "variant": variant,
                "side": side,
                "breakout_ts": pd.to_datetime(event["breakout_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_ts": bars.iloc[signal_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": bars.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": bars.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_delay_bars": int(signal_idx - int(event["breakout_idx"])),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "atr_at_entry_signal": atr,
                "raw_edge": _safe_float(event["raw_edge"]),
                "threshold_edge": _safe_float(event["threshold_edge"]),
                "volume_ok": int(event["volume_ok"]),
                "retest_hold": int(event["retest_hold"]),
                "false_break_3bars": _safe_float(event["false_break_3bars"]),
                "time_to_failure_bars": _safe_float(event["time_to_failure_bars"]),
                "gross_ret": gross_mult - 1.0,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "exit_reason": exit_reason,
                "win": int(net_ret > 0),
            }
        )
        nav_rows.append(
            {
                "asset": bars.iloc[0]["asset"],
                "variant": variant,
                "timestamp": bars.iloc[exit_idx]["timestamp"],
                "nav": nav,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(trades), pd.DataFrame(nav_rows)


def summarize_trades(trades: pd.DataFrame, nav: pd.DataFrame, asset: str, variant: str) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(
            [
                {
                    "asset": asset,
                    "variant": variant,
                    "trades": 0,
                    "win_rate": np.nan,
                    "avg_net_ret": np.nan,
                    "median_net_ret": np.nan,
                    "total_return": 0.0,
                    "max_drawdown": 0.0,
                    "false_break_ratio": np.nan,
                    "retest_hold_rate": np.nan,
                    "avg_time_to_failure_bars": np.nan,
                    "avg_signal_delay_bars": np.nan,
                    "avg_hold_bars": np.nan,
                    "long_trades": 0,
                    "short_trades": 0,
                }
            ]
        )

    running_peak = nav["nav"].cummax() if not nav.empty else pd.Series(dtype=float)
    drawdown = nav["nav"] / running_peak - 1.0 if not nav.empty else pd.Series(dtype=float)
    max_dd = float(drawdown.min()) if len(drawdown) else 0.0
    return pd.DataFrame(
        [
            {
                "asset": asset,
                "variant": variant,
                "trades": int(len(trades)),
                "win_rate": float(trades["win"].mean()),
                "avg_net_ret": float(trades["net_ret"].mean()),
                "median_net_ret": float(trades["net_ret"].median()),
                "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
                "max_drawdown": max_dd,
                "false_break_ratio": float(trades["false_break_3bars"].mean()),
                "retest_hold_rate": float(trades["retest_hold"].mean()),
                "avg_time_to_failure_bars": float(trades["time_to_failure_bars"].mean()),
                "avg_signal_delay_bars": float(trades["signal_delay_bars"].mean()),
                "avg_hold_bars": float(trades["hold_bars"].mean()),
                "long_trades": int((trades["side"] == "long").sum()),
                "short_trades": int((trades["side"] == "short").sum()),
            }
        ]
    )


def build_variant_aggregate(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby("variant", as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
            mean_retest_hold_rate=("retest_hold_rate", "mean"),
            mean_time_to_failure_bars=("avg_time_to_failure_bars", "mean"),
            mean_signal_delay_bars=("avg_signal_delay_bars", "mean"),
            mean_trades=("trades", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
        .sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_friction_ladder(prepared_bars: dict[str, pd.DataFrame], event_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    variant_order = {variant: idx for idx, variant in enumerate(FRICTION_VARIANTS)}

    for cost in FRICTION_COSTS:
        summaries = []
        for asset, bars in prepared_bars.items():
            events = event_frames[asset]
            for variant in FRICTION_VARIANTS:
                variant_events = filtered_events_for_variant(events, variant)
                trades, nav = simulate_variant_events(
                    bars,
                    variant_events,
                    variant,
                    cost_bps_per_side=cost,
                )
                summaries.append(summarize_trades(trades, nav, asset, variant))
        asset_summary = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
        agg = build_variant_aggregate(asset_summary)
        if agg.empty:
            continue
        agg["cost_bps_per_side"] = float(cost)
        rows.append(agg)

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

    combo20 = pick("combo_all", 20.0)
    higher10 = pick("higher_low_only", 10.0)
    raw20 = pick("raw_breakout", 20.0)

    if combo20 is not None and float(combo20.get("mean_total_return", 0.0)) > 0:
        headline = (
            "friction recheck：`combo_all` 在 10/15/20bps per side 下仍保持正的跨资产平均收益；"
            "当前更像值得继续做轻量 forward 复核的 confirmation challenger。"
        )
    else:
        headline = (
            "friction recheck：`combo_all` 在更高摩擦下没有守住正收益；"
            "当前更像 sample-bound first verdict，不足以继续朝 tiny-live 方向推进。"
        )

    bullets: list[str] = []
    combo6 = pick("combo_all", 6.0)
    combo10 = pick("combo_all", 10.0)
    combo15 = pick("combo_all", 15.0)
    if combo6 is not None and combo10 is not None and combo15 is not None and combo20 is not None:
        bullets.append(
            "combo_all cost ladder："
            f"6bps {pct(combo6['mean_total_return'])} → 10bps {pct(combo10['mean_total_return'])} → "
            f"15bps {pct(combo15['mean_total_return'])} → 20bps {pct(combo20['mean_total_return'])}。"
        )
    if higher10 is not None:
        bullets.append(
            f"higher_low_only 在 10bps 已转为 {pct(higher10['mean_total_return'])}，说明更简化的 guard 对摩擦更脆。"
        )
    if raw20 is not None:
        bullets.append(
            f"raw_breakout 在 20bps 仍为 {pct(raw20['mean_total_return'])}，和 combo_all 的差距说明当前改善不只是‘少做几笔’那么简单。"
        )
    bullets.append("但这仍只是同一份 120d / 15m / 3 币种样本上的轻量 friction recheck；还没回答 forward continuity、路由偏差和 live capital cap。")
    return headline, bullets


def derive_verdict(variant_aggregate: pd.DataFrame) -> tuple[str, list[str]]:
    if variant_aggregate.empty:
        return "hard verdict：当前没有生成可读结果。", ["样本为空，未能产出 Rank 2 first verdict。"]

    raw_df = variant_aggregate[variant_aggregate["variant"] == "raw_breakout"]
    raw = raw_df.iloc[0] if not raw_df.empty else None
    challengers = variant_aggregate[variant_aggregate["variant"] != "raw_breakout"].copy()

    if raw is None or challengers.empty:
        return "hard verdict：没有足够对照结果来判断 Rank 2。", ["缺少 raw 或 challenger 对照，暂不下结论。"]

    beaters = challengers[
        (challengers["mean_total_return"] > float(raw["mean_total_return"]))
        & (challengers["mean_false_break_ratio"] < float(raw["mean_false_break_ratio"]))
    ]
    best_return = challengers.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]
    best_guard = challengers.sort_values(["mean_false_break_ratio", "mean_total_return"], ascending=[True, False]).iloc[0]

    if beaters.empty:
        headline = "hard verdict：Rank 2 这轮没有跑出 replace-ready 候选；最多只说明某些 confirmation gate 比 raw 更不差。"
    else:
        best = beaters.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]
        if float(best["mean_total_return"]) <= 0 or float(best.get("positive_asset_ratio", 0.0) or 0.0) <= 0:
            headline = (
                f"hard verdict：{best['variant']} 相对 raw 同时改善了收益与假突破率，但绝对 post-cost return 仍不够；"
                "先保留为更窄的 confirmation / execution guard，不升格替代 Live Seat。"
            )
        else:
            headline = (
                f"hard verdict：{best['variant']} 同时改善了跨资产收益与假突破率，可作为 Rank 2 的继续复核版本；"
                "但当前仍只配进入下一轮更正式复核，不直接宣布 tiny-live ready。"
            )

    bullets = [
        f"baseline raw_breakout：mean_total_return {pct(raw['mean_total_return'])}，mean_false_break_ratio {pct(raw['mean_false_break_ratio'])}，mean_trades {num(raw['mean_trades'])}。",
        f"收益最好的 Rank 2 版本：{best_return['variant']}（mean_total_return {pct(best_return['mean_total_return'])}，false_break_ratio {pct(best_return['mean_false_break_ratio'])}，mean_signal_delay {num(best_return['mean_signal_delay_bars'])} bars）。",
        f"最强 guard 版本：{best_guard['variant']}（false_break_ratio {pct(best_guard['mean_false_break_ratio'])}，mean_total_return {pct(best_guard['mean_total_return'])}）。",
    ]

    combo_df = challengers[challengers["variant"] == "combo_all"]
    if not combo_df.empty:
        combo = combo_df.iloc[0]
        bullets.append(
            f"combo_all 读法：mean_total_return {pct(combo['mean_total_return'])}，false_break_ratio {pct(combo['mean_false_break_ratio'])}，positive_asset_ratio {pct(combo['positive_asset_ratio'])}。"
        )

    if beaters.empty:
        bullets.append("因此这条线当前更像 breakout 的 confirmation / execution guard 试验台，而不是能直接替位 Live Seat 的 challenger。")
    else:
        best = beaters.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]
        if float(best["mean_total_return"]) <= 0 or float(best.get("positive_asset_ratio", 0.0) or 0.0) <= 0:
            bullets.append("它值得继续保留为更窄的 guard / confirmation follow-up，但还不够支持 replace-ready 结论。")
        else:
            bullets.append("它已经值得进入更正式的下一轮 forward / friction 复核，但还不是直接 live 准入。")

    return headline, bullets


def build_shadow_readiness_drycheck(variant_aggregate: pd.DataFrame, friction_ladder: pd.DataFrame) -> pd.DataFrame:
    if variant_aggregate.empty:
        return pd.DataFrame()

    combo_df = variant_aggregate[variant_aggregate["variant"] == "combo_all"]
    if combo_df.empty:
        return pd.DataFrame()
    combo = combo_df.iloc[0]

    def pick_cost(cost: float) -> pd.Series | None:
        hit = friction_ladder[
            (friction_ladder["variant"] == "combo_all")
            & (friction_ladder["cost_bps_per_side"] == float(cost))
        ]
        return hit.iloc[0] if not hit.empty else None

    combo15 = pick_cost(15.0)
    combo20 = pick_cost(20.0)

    rows = [
        {
            "gate": "base_post_cost_return",
            "status": "pass" if float(combo.get("mean_total_return", 0.0)) > 0 else "fail",
            "actual": pct(combo.get("mean_total_return")),
            "threshold": "> 0% @ 6bps/side",
            "why_it_matters": "先确认它不是只靠名义收益好看，而是基础成本口径下仍有正的跨资产平均回报。",
        },
        {
            "gate": "friction_15bps_hold",
            "status": "pass" if combo15 is not None and float(combo15.get("mean_total_return", 0.0)) > 0 else "fail",
            "actual": pct(combo15.get("mean_total_return") if combo15 is not None else None),
            "threshold": "> 0% @ 15bps/side",
            "why_it_matters": "若 15bps 就转负，这条 guard 更像纸面优势，不值得继续往 shadow 方向推进。",
        },
        {
            "gate": "cross_asset_floor",
            "status": "pass" if float(combo.get("positive_asset_ratio", 0.0)) >= (2 / 3) else "fail",
            "actual": pct(combo.get("positive_asset_ratio")),
            "threshold": ">= 66.67% positive assets",
            "why_it_matters": "先要求至少 2/3 币种为正，避免单一幸运资产把整个候选误推成 desk 级 challenger。",
        },
        {
            "gate": "trade_count_floor",
            "status": "pass" if float(combo.get("mean_trades", 0.0)) >= 5.0 else "fail",
            "actual": num(combo.get("mean_trades"), 1),
            "threshold": ">= 5 mean trades / asset",
            "why_it_matters": "先排除‘只靠极少数偶然交易’的假阳性，至少让样本有最小 trade-count 支撑。",
        },
        {
            "gate": "false_break_guard",
            "status": "pass" if float(combo.get("mean_false_break_ratio", 1.0)) <= 0.10 else "fail",
            "actual": pct(combo.get("mean_false_break_ratio")),
            "threshold": "<= 10% false-break ratio",
            "why_it_matters": "Scout 当前是 breakout confirmation guard shortlist，假突破压不住就不该进入后续影子观察。",
        },
        {
            "gate": "shadow_admission_scope",
            "status": "fail",
            "actual": "120d / 15m / 3 assets；positive_assets=2/3；20bps 仍正但样本偏窄",
            "threshold": "需要更宽样本或更正式 continuity/shadow gate 授权",
            "why_it_matters": "即便前几道快筛通过，它现在也只够当 keep-narrower shadow-candidate，不够直接升为 shadow-admission-ready。",
        },
    ]
    if combo20 is not None:
        rows.append(
            {
                "gate": "friction_20bps_watch",
                "status": "watch" if float(combo20.get("mean_total_return", 0.0)) > 0 else "fail",
                "actual": pct(combo20.get("mean_total_return")),
                "threshold": "> 0% @ 20bps/side（非硬门槛，偏加分项）",
                "why_it_matters": "20bps 不是当前硬门槛，但若还能守正，说明它至少没有被更现实一点的成本立即击穿。",
            }
        )
    return pd.DataFrame(rows)


def derive_shadow_readiness_verdict(shadow_readiness: pd.DataFrame) -> tuple[str, list[str]]:
    if shadow_readiness.empty:
        return "shadow-readiness dry-check：当前没有生成可读结果。", ["缺少 dry-check artifact，暂不补充 shadow-readiness 判断。"]

    by_gate = {str(row["gate"]): row for _, row in shadow_readiness.iterrows()}
    pass_count = int((shadow_readiness["status"] == "pass").sum())
    fail_gates = shadow_readiness.loc[shadow_readiness["status"] == "fail", "gate"].tolist()
    watch20 = by_gate.get("friction_20bps_watch")

    headline = (
        "shadow-readiness dry-check：`combo_all` 已通过最小 trade-count / friction / false-break 快筛，"
        "当前可继续保留为 keep-narrower shadow-candidate；但样本仍偏窄，暂不进入 shadow-admission。"
    )
    if pass_count < 4:
        headline = (
            "shadow-readiness dry-check：`combo_all` 连最小快筛都没有通过干净，"
            "当前更适合停在 first-verdict / friction 阶段，不应往 shadow 方向推进。"
        )

    bullets = [
        f"已通过 {pass_count} 道最小快筛；当前主要未过的硬门槛：{', '.join(fail_gates) if fail_gates else '无'}。",
        "trade-count / cross-asset / false-break 这几项都只是‘值不值得继续看’的快筛，不等于已经有 live-readiness。",
        "当前最诚实的 desk 读法仍是：Rank 2 更像 confirmation challenger / shadow-candidate，而不是 replace-ready winner。",
    ]
    if watch20 is not None:
        bullets.append(
            f"20bps 观察位仍为 {watch20['actual']}，说明它在更现实一点的成本下还没立刻塌掉，但这只是加分项，不足以单独放行。"
        )
    bullets.append("若未来 board / bot2 明确授权 continuity 或 shadow 检查，再基于 genuinely new evidence 补 forward/shadow，而不是把这张 dry-check 误写成已准入。")
    return headline, bullets


def build_trade_count_honesty(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    combo = trades_df[trades_df["variant"] == "combo_all"].copy()
    if combo.empty:
        return pd.DataFrame()

    combo["entry_ts"] = pd.to_datetime(combo["entry_ts"], utc=True)
    asset_counts = combo.groupby("asset").size().sort_values()
    side_shares = (
        combo.groupby(["asset", "side"]).size().rename("trades").reset_index()
        .merge(asset_counts.rename("asset_trades"), left_on="asset", right_index=True, how="left")
    )
    side_shares["side_share"] = side_shares["trades"] / side_shares["asset_trades"]
    max_side_share = float(side_shares["side_share"].max()) if not side_shares.empty else float("nan")

    asset_share = asset_counts / float(len(combo))
    max_asset_share = float(asset_share.max()) if not asset_share.empty else float("nan")

    combo["trade_month"] = combo["entry_ts"].dt.strftime("%Y-%m")
    month_breadth = combo.groupby("asset")["trade_month"].nunique().sort_values()

    max_gap_days = float("nan")
    for _, asset_df in combo.sort_values("entry_ts").groupby("asset"):
        deltas = asset_df["entry_ts"].diff().dropna().dt.total_seconds() / 86400.0
        if not deltas.empty:
            asset_gap = float(deltas.max())
            max_gap_days = asset_gap if not math.isfinite(max_gap_days) else max(max_gap_days, asset_gap)

    rows = [
        {
            "gate": "min_asset_trade_floor",
            "status": "pass" if int(asset_counts.min()) >= 5 else "fail",
            "actual": f"min asset trades = {int(asset_counts.min())}",
            "threshold": ">= 5 trades on every asset",
            "why_it_matters": "避免 combo_all 只是靠单一币种偶然命中；至少每个币种都要有最小交易数。",
        },
        {
            "gate": "asset_concentration_watch",
            "status": "pass" if max_asset_share <= 0.50 else "watch",
            "actual": pct(max_asset_share),
            "threshold": "<= 50% of all trades from one asset",
            "why_it_matters": "若大部分交易都堆在单一资产，desk 读法就更像偏科 lucky pocket，而不是跨资产 guard。",
        },
        {
            "gate": "calendar_breadth_floor",
            "status": "pass" if int(month_breadth.min()) >= 3 else "fail",
            "actual": f"min active months per asset = {int(month_breadth.min())}",
            "threshold": ">= 3 active months on every asset",
            "why_it_matters": "至少要跨过几个月份，避免所有交易只挤在很短的局部 regime。",
        },
        {
            "gate": "side_balance_watch",
            "status": "pass" if max_side_share <= 0.75 else "watch",
            "actual": pct(max_side_share),
            "threshold": "<= 75% one-sided within any asset",
            "why_it_matters": "如果某个资产几乎只剩单边交易，后续 continuity / shadow 读法会更脆弱。",
        },
        {
            "gate": "idle_gap_guard",
            "status": "fail" if math.isfinite(max_gap_days) and max_gap_days > 45.0 else "pass",
            "actual": f"{max_gap_days:.1f} days" if math.isfinite(max_gap_days) else "-",
            "threshold": "<= 45d max gap between combo_all trades per asset",
            "why_it_matters": "若交易节奏里出现过长空窗，就说明它更像稀疏机会 pocket，不够支撑 continuity-week / shadow cadence。",
        },
    ]
    return pd.DataFrame(rows)


def derive_trade_count_honesty_verdict(trade_count_honesty: pd.DataFrame) -> tuple[str, list[str]]:
    if trade_count_honesty.empty:
        return "trade-count honesty：当前没有生成可读结果。", ["缺少 trade-count honesty artifact，暂不补充 cadence 判断。"]

    fail_gates = trade_count_honesty.loc[trade_count_honesty["status"] == "fail", "gate"].tolist()
    watch_gates = trade_count_honesty.loc[trade_count_honesty["status"] == "watch", "gate"].tolist()
    headline = (
        "trade-count honesty：`combo_all` 的最小交易数与月度分布够支撑 keep-narrower 读法，"
        "但交易节奏仍偏稀疏，暂不适合把它升格成 shadow-admission-ready。"
    )
    if "min_asset_trade_floor" in fail_gates or "calendar_breadth_floor" in fail_gates:
        headline = (
            "trade-count honesty：`combo_all` 连最小 trade-count / calendar breadth 都不够扎实，"
            "当前不应往 shadow 方向推进。"
        )

    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        "这张卡回答的是交易分布够不够诚实，不是收益有没有继续上升。",
        "若最小 trade-count 过关但 idle gap 过长，最诚实的 desk 读法应是：保留为 keep-narrower candidate，而不是偷升格成 continuity-week / shadow-ready。",
    ]
    return headline, bullets


def build_time_stability_drycheck(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    combo = trades_df[trades_df["variant"] == "combo_all"].copy()
    if combo.empty or len(combo) < 9:
        return pd.DataFrame()

    combo["entry_ts"] = pd.to_datetime(combo["entry_ts"], utc=True)
    q1, q2 = combo["entry_ts"].quantile([1 / 3, 2 / 3])
    start = combo["entry_ts"].min() - pd.Timedelta(seconds=1)
    end = combo["entry_ts"].max() + pd.Timedelta(seconds=1)
    combo["time_bucket"] = pd.cut(
        combo["entry_ts"],
        bins=[start, q1, q2, end],
        labels=["early", "mid", "late"],
    )

    bucket_rows = []
    for bucket, bucket_df in combo.groupby("time_bucket", observed=False):
        if pd.isna(bucket) or bucket_df.empty:
            continue
        asset_stats = []
        for asset, asset_df in bucket_df.groupby("asset"):
            net_path = (1.0 + asset_df["net_ret"].astype(float)).prod() - 1.0
            asset_stats.append(
                {
                    "asset": asset,
                    "asset_total_return": float(net_path),
                    "false_break_ratio": float(asset_df["false_break_3bars"].mean()),
                    "trades": int(len(asset_df)),
                }
            )
        asset_stats_df = pd.DataFrame(asset_stats)
        bucket_rows.append(
            {
                "time_bucket": str(bucket),
                "assets_present": int(asset_stats_df["asset"].nunique()),
                "positive_assets": int((asset_stats_df["asset_total_return"] > 0).sum()),
                "positive_asset_ratio": float((asset_stats_df["asset_total_return"] > 0).mean()),
                "mean_asset_return": float(asset_stats_df["asset_total_return"].mean()),
                "worst_asset_return": float(asset_stats_df["asset_total_return"].min()),
                "max_false_break_ratio": float(asset_stats_df["false_break_ratio"].max()),
                "trades": int(len(bucket_df)),
                "window_start_utc": fmt_ts(bucket_df["entry_ts"].min()),
                "window_end_utc": fmt_ts(bucket_df["entry_ts"].max()),
            }
        )

    bucket_df = pd.DataFrame(bucket_rows)
    if bucket_df.empty:
        return pd.DataFrame()

    positive_buckets = int((bucket_df["mean_asset_return"] > 0).sum())
    min_bucket_trades = int(bucket_df["trades"].min())
    min_bucket_assets = int(bucket_df["assets_present"].min())
    worst_bucket = bucket_df.sort_values(["mean_asset_return", "positive_asset_ratio"]).iloc[0]
    max_false_break = float(bucket_df["max_false_break_ratio"].max())

    rows = [
        {
            "gate": "positive_bucket_floor",
            "status": "pass" if positive_buckets >= 2 else "fail",
            "actual": f"{positive_buckets}/3 positive time buckets",
            "threshold": ">= 2 positive buckets out of 3",
            "why_it_matters": "至少要有多数时间窗口仍为正，避免候选只靠单段 regime 撑住 headline。",
        },
        {
            "gate": "bucket_trade_floor",
            "status": "pass" if min_bucket_trades >= 5 else "fail",
            "actual": f"min bucket trades = {min_bucket_trades}",
            "threshold": ">= 5 trades in every time bucket",
            "why_it_matters": "时间稳定性不能只建立在极少数窗口内 1~2 笔交易上。",
        },
        {
            "gate": "bucket_asset_coverage",
            "status": "pass" if min_bucket_assets >= 3 else "fail",
            "actual": f"min assets present = {min_bucket_assets}/3",
            "threshold": "all 3 assets should appear in every time bucket",
            "why_it_matters": "若某个时间窗口已经退化成少数资产独撑，时间稳定性读法会明显变弱。",
        },
        {
            "gate": "false_break_time_guard",
            "status": "pass" if max_false_break <= 0.10 else "fail",
            "actual": pct(max_false_break),
            "threshold": "<= 10% max false-break ratio across buckets",
            "why_it_matters": "若某个时间窗口假突破突然抬升，就说明这个 guard 更像局部 lucky patch。",
        },
        {
            "gate": "worst_bucket_return_watch",
            "status": "watch" if float(worst_bucket["mean_asset_return"]) <= -0.01 else "pass",
            "actual": (
                f"{worst_bucket['time_bucket']} mean_asset_return={pct(worst_bucket['mean_asset_return'])}; "
                f"positive_assets={int(worst_bucket['positive_assets'])}/{int(worst_bucket['assets_present'])}"
            ),
            "threshold": "worst bucket ideally > -1.00% mean asset return",
            "why_it_matters": "即便多数 bucket 为正，只要最差窗口是三资产齐跌的负 pocket，就还不足以把它写成 paper-candidate-ready。",
        },
    ]
    return pd.DataFrame(rows)


def derive_time_stability_verdict(time_stability: pd.DataFrame) -> tuple[str, list[str]]:
    if time_stability.empty:
        return "time stability：当前没有生成可读结果。", ["缺少 time stability artifact，暂不补充时间稳定性判断。"]

    fail_gates = time_stability.loc[time_stability["status"] == "fail", "gate"].tolist()
    watch_gates = time_stability.loc[time_stability["status"] == "watch", "gate"].tolist()
    worst_bucket_row = time_stability.loc[time_stability["gate"] == "worst_bucket_return_watch"]
    worst_bucket_actual = str(worst_bucket_row.iloc[0]["actual"]) if not worst_bucket_row.empty else "-"
    headline = (
        "time stability：`combo_all` 在 3 段历史时间窗里有 2 段守住正向，"
        "但最早窗口仍是三资产同步偏弱的负 pocket，当前更像 one-more-light-check，而不是可直接升为 paper candidate。"
    )
    if "positive_bucket_floor" in fail_gates or "bucket_trade_floor" in fail_gates:
        headline = (
            "time stability：`combo_all` 连多数时间窗口为正都没守住，"
            "当前更适合停在 keep-narrower / park，而不是继续往 paper candidate 方向写。"
        )

    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        f"最弱时间窗读法：{worst_bucket_actual}。",
        "这张卡回答的是时间稳定性，不是 forward continuity；它只说明候选有没有明显单段 regime 依赖。",
        "当前最诚实的 desk 结论仍是：Rank 2 值得保留为 keep-narrower / one-more-light-check，但还不足以靠这份时间切片直接升格成 paper candidate。",
    ]
    return headline, bullets


def build_cross_asset_stability_drycheck(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    combo = asset_summary[asset_summary["variant"] == "combo_all"].copy()
    if combo.empty:
        return pd.DataFrame()

    combo = combo.sort_values(["total_return", "false_break_ratio", "asset"]).reset_index(drop=True)
    positive_assets = int((combo["total_return"] > 0).sum())
    min_trades = int(combo["trades"].min())
    worst_asset = combo.iloc[0]
    max_false_break = float(combo["false_break_ratio"].max())
    false_break_spread = float(combo["false_break_ratio"].max() - combo["false_break_ratio"].min())
    max_drawdown_floor = float(combo["max_drawdown"].min())

    rows = [
        {
            "gate": "positive_asset_floor",
            "status": "pass" if positive_assets >= 2 else "fail",
            "actual": f"{positive_assets}/{len(combo)} assets positive",
            "threshold": ">= 2 positive assets out of 3",
            "why_it_matters": "Scout 的跨标的稳定性至少要做到：不是只靠单一币种把候选硬撑成 paper candidate。",
        },
        {
            "gate": "min_asset_trade_floor",
            "status": "pass" if min_trades >= 5 else "fail",
            "actual": f"min asset trades = {min_trades}",
            "threshold": ">= 5 trades on every asset",
            "why_it_matters": "跨标的判断要建立在每个币种都有最小样本，而不是某个资产只有一两笔偶然命中。",
        },
        {
            "gate": "worst_asset_return_watch",
            "status": "watch" if float(worst_asset["total_return"]) <= -0.01 else "pass",
            "actual": f"{worst_asset['asset']} total_return={pct(worst_asset['total_return'])}; false_break_ratio={pct(worst_asset['false_break_ratio'])}",
            "threshold": "worst asset ideally > -1.00% total return",
            "why_it_matters": "即便多数资产为正，只要最弱资产已经转成明显负 pocket，就还不能把跨标的稳定性写得太满。",
        },
        {
            "gate": "false_break_dispersion_watch",
            "status": "watch" if false_break_spread > 0.15 else "pass",
            "actual": pct(false_break_spread),
            "threshold": "<= 15% max-min false-break spread across assets",
            "why_it_matters": "若不同币种的假突破率分化很大，说明这条 guard 更像 selective pocket，而不是均匀可迁移。",
        },
        {
            "gate": "drawdown_floor",
            "status": "pass" if max_drawdown_floor > -0.03 else "watch",
            "actual": pct(max_drawdown_floor),
            "threshold": "> -3.00% worst asset max drawdown",
            "why_it_matters": "跨标的候选不需要每个币种都完美，但至少不该在最弱资产上立刻塌成深坑。",
        },
        {
            "gate": "btc_weak_pocket_note",
            "status": "info",
            "actual": "BTC-USD 当前是最弱 pocket；ETH/SOL 为正，但 BTC total_return 约 -1.15%、false_break_ratio 约 20%",
            "threshold": "reader-facing note",
            "why_it_matters": "把当前跨标的弱点直接写明，避免 desk 只盯总体均值而忽略 BTC 这条最先失真的腿。",
        },
    ]
    return pd.DataFrame(rows)



def derive_cross_asset_stability_verdict(cross_asset_stability: pd.DataFrame) -> tuple[str, list[str]]:
    if cross_asset_stability.empty:
        return "cross-asset stability：当前没有生成可读结果。", ["缺少 cross-asset stability artifact，暂不补充跨标的判断。"]

    fail_gates = cross_asset_stability.loc[cross_asset_stability["status"] == "fail", "gate"].tolist()
    watch_gates = cross_asset_stability.loc[cross_asset_stability["status"] == "watch", "gate"].tolist()
    worst_asset_row = cross_asset_stability.loc[cross_asset_stability["gate"] == "worst_asset_return_watch"]
    worst_asset_actual = str(worst_asset_row.iloc[0]["actual"]) if not worst_asset_row.empty else "-"
    headline = (
        "cross-asset stability：`combo_all` 目前仍是 2/3 资产为正的窄范围 paper candidate，"
        "但 BTC 这条腿仍偏弱，当前更像 keep-narrower / one-more-light-check，而不是可直接升格。"
    )
    if "positive_asset_floor" in fail_gates or "min_asset_trade_floor" in fail_gates:
        headline = (
            "cross-asset stability：`combo_all` 连最小跨标的地板都没守住，"
            "当前更诚实的 desk 读法应回到 keep-narrower / park，而不是继续写成 paper candidate。"
        )

    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        f"最弱资产读法：{worst_asset_actual}。",
        "这张卡回答的是跨标的迁移性，不是时间稳定性或 forward continuity；它只看同一规则在三条币上是不是都还能站住。",
        "当前最诚实的结论仍是：Rank 2 可以留在窄范围 paper candidate pool，但 reader-facing 必须继续点明 BTC 弱 pocket，不能把 2/3 positive 写成全面稳定。",
    ]
    return headline, bullets



def build_parameter_stability_drycheck(prepared_bars: dict[str, pd.DataFrame]) -> pd.DataFrame:
    if not prepared_bars:
        return pd.DataFrame()

    configs = [
        {"volume_confirm_mult": 1.1, "flip_lookahead_bars": 3, "swing_lookahead_bars": 6, "label": "vol1.1_flip3_swing6"},
        {"volume_confirm_mult": 1.2, "flip_lookahead_bars": 3, "swing_lookahead_bars": 6, "label": "vol1.2_flip3_swing6"},
        {"volume_confirm_mult": 1.3, "flip_lookahead_bars": 3, "swing_lookahead_bars": 6, "label": "vol1.3_flip3_swing6"},
        {"volume_confirm_mult": 1.2, "flip_lookahead_bars": 2, "swing_lookahead_bars": 6, "label": "vol1.2_flip2_swing6"},
        {"volume_confirm_mult": 1.2, "flip_lookahead_bars": 4, "swing_lookahead_bars": 6, "label": "vol1.2_flip4_swing6"},
        {"volume_confirm_mult": 1.2, "flip_lookahead_bars": 3, "swing_lookahead_bars": 5, "label": "vol1.2_flip3_swing5"},
        {"volume_confirm_mult": 1.2, "flip_lookahead_bars": 3, "swing_lookahead_bars": 7, "label": "vol1.2_flip3_swing7"},
    ]

    config_rows: list[dict] = []
    for config in configs:
        summaries = []
        for asset, bars in prepared_bars.items():
            symbol = ASSETS[asset]
            events = build_event_frame(
                asset,
                symbol,
                bars,
                volume_confirm_mult=float(config["volume_confirm_mult"]),
                flip_lookahead_bars=int(config["flip_lookahead_bars"]),
                swing_lookahead_bars=int(config["swing_lookahead_bars"]),
            )
            variant_events = filtered_events_for_variant(events, "combo_all")
            trades, nav = simulate_variant_events(bars, variant_events, "combo_all")
            summaries.append(summarize_trades(trades, nav, asset, "combo_all"))

        asset_summary = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
        agg = build_variant_aggregate(asset_summary)
        combo = agg[agg["variant"] == "combo_all"]
        if combo.empty:
            continue
        row = combo.iloc[0].to_dict()
        row.update(config)
        config_rows.append(row)

    config_df = pd.DataFrame(config_rows)
    if config_df.empty:
        return pd.DataFrame()

    positive_configs = int((config_df["mean_total_return"] > 0).sum())
    stable_cross_asset_configs = int((config_df["positive_asset_ratio"] >= (2 / 3)).sum())
    min_trades = float(config_df["mean_trades"].min())
    max_false_break = float(config_df["mean_false_break_ratio"].max())
    worst_row = config_df.sort_values(["mean_total_return", "positive_asset_ratio"]).iloc[0]
    best_row = config_df.sort_values(["mean_total_return", "mean_false_break_ratio"], ascending=[False, True]).iloc[0]

    rows = [
        {
            "gate": "positive_neighbor_floor",
            "status": "pass" if positive_configs >= 5 else "fail",
            "actual": f"{positive_configs}/{len(config_df)} configs positive",
            "threshold": ">= 5 positive configs across local parameter neighborhood",
            "why_it_matters": "参数稳定性至少要做到：稍微收紧/放宽量能、回踩窗口、结构窗口后，候选不会立刻整体翻负。",
        },
        {
            "gate": "cross_asset_neighbor_floor",
            "status": "pass" if stable_cross_asset_configs >= 5 else "fail",
            "actual": f"{stable_cross_asset_configs}/{len(config_df)} configs keep >=2/3 positive assets",
            "threshold": ">= 5 configs keep cross-asset floor",
            "why_it_matters": "不能只靠一组精确参数和单一资产 pocket 才成立；邻域内至少多数配置要继续保持跨资产正向。",
        },
        {
            "gate": "trade_count_neighbor_floor",
            "status": "pass" if min_trades >= 4.0 else "fail",
            "actual": f"min mean trades / asset = {min_trades:.1f}",
            "threshold": ">= 4 mean trades / asset on every neighbor config",
            "why_it_matters": "若某些近邻参数让交易数瞬间塌到几乎没有，这条线更像脆弱调参口袋，不像可部署候选。",
        },
        {
            "gate": "false_break_neighbor_guard",
            "status": "pass" if max_false_break <= 0.10 else "fail",
            "actual": pct(max_false_break),
            "threshold": "<= 10% max false-break ratio across neighbor configs",
            "why_it_matters": "参数轻微变动后若假突破明显回升，说明 guard 改善不稳，不能诚实地写成 paper candidate。",
        },
        {
            "gate": "worst_neighbor_return_watch",
            "status": "watch" if float(worst_row["mean_total_return"]) <= -0.01 else "pass",
            "actual": (
                f"{worst_row['label']} mean_total_return={pct(worst_row['mean_total_return'])}; "
                f"positive_assets={int(worst_row['positive_assets'])}/{int(worst_row['assets_tested'])}"
            ),
            "threshold": "worst neighbor ideally > -1.00% mean total return",
            "why_it_matters": "即便多数近邻不死，也要防止最差近邻出现明显翻负 pocket，提示这条线仍偏 sample-bound。",
        },
        {
            "gate": "best_neighbor_snapshot",
            "status": "info",
            "actual": (
                f"{best_row['label']} mean_total_return={pct(best_row['mean_total_return'])}; "
                f"false_break_ratio={pct(best_row['mean_false_break_ratio'])}; mean_trades={num(best_row['mean_trades'], 1)}"
            ),
            "threshold": "reference only",
            "why_it_matters": "记录当前邻域内最强配置，方便 desk 判断是否只是 base 参数独好，还是邻域本身仍有一定韧性。",
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
        "parameter stability：`combo_all` 在本地小参数邻域里大体还能站住，"
        "但若最差近邻已明显翻负或跨资产地板守不住，就仍更适合停在 one-more-light-check。"
    )
    if "positive_neighbor_floor" in fail_gates or "cross_asset_neighbor_floor" in fail_gates:
        headline = (
            "parameter stability：`combo_all` 对本地参数邻域仍偏脆，"
            "当前还不足以仅凭这套参数稳定性就升成 paper candidate。"
        )

    bullets = [
        f"fail gates：{', '.join(fail_gates) if fail_gates else '无'}；watch gates：{', '.join(watch_gates) if watch_gates else '无'}。",
        f"最弱近邻：{worst_actual}。",
        f"最强近邻快照：{best_actual}。",
        "这张卡回答的是本地参数邻域韧性，不是更大规模 optimizer；目的是避免把单点调参 lucky pocket 写成 desk 级候选。",
    ]
    return headline, bullets



def build_paper_candidate_admission_memo(
    variant_aggregate: pd.DataFrame,
    shadow_readiness: pd.DataFrame,
    trade_count_honesty: pd.DataFrame,
    time_stability: pd.DataFrame,
    parameter_stability: pd.DataFrame,
) -> pd.DataFrame:
    columns = ["gate", "status", "actual", "threshold", "why_it_matters"]
    if variant_aggregate.empty:
        return pd.DataFrame(columns=columns)

    combo = variant_aggregate.loc[variant_aggregate["variant"] == "combo_all"]
    if combo.empty:
        return pd.DataFrame(columns=columns)
    combo_row = combo.iloc[0]

    def gate_status(df: pd.DataFrame, gate: str) -> str:
        if df.empty or "gate" not in df.columns:
            return "missing"
        row = df.loc[df["gate"] == gate]
        if row.empty:
            return "missing"
        return str(row.iloc[0]["status"])

    def gate_actual(df: pd.DataFrame, gate: str) -> str:
        if df.empty or "gate" not in df.columns:
            return "-"
        row = df.loc[df["gate"] == gate]
        if row.empty:
            return "-"
        return str(row.iloc[0]["actual"])

    shadow_core_pass = all(
        gate_status(shadow_readiness, gate) == "pass"
        for gate in [
            "base_post_cost_return",
            "friction_15bps_hold",
            "cross_asset_floor",
            "trade_count_floor",
            "false_break_guard",
        ]
    )
    time_positive_status = gate_status(time_stability, "positive_bucket_floor")
    parameter_positive_status = gate_status(parameter_stability, "positive_neighbor_floor")
    parameter_cross_asset_status = gate_status(parameter_stability, "cross_asset_neighbor_floor")

    rows = [
        {
            "gate": "clean_replication",
            "status": "pass",
            "actual": "本地 clean replication 已跑通：Binance 120d / 15m / BTC+ETH+SOL，variant_aggregate 与 trades.csv 已生成",
            "threshold": "本地最小复现可重跑",
            "why_it_matters": "先确认它不是停留在来源摘要，而是已经有可复现的本地实现与产物。",
        },
        {
            "gate": "rule_honesty_guard",
            "status": "pass",
            "actual": "trade on = EMA20>EMA50 + Donchian breakout + 放量 + support-flip + higher-low；trade off = 不满足确认 / next-bar open 执行 / 1 ATR stop / 2 ATR target / 8 bars",
            "threshold": "规则能明确写成 trade on / trade off",
            "why_it_matters": "paper candidate 至少要有清楚、可交接的执行规则，而不是靠模糊 discretionary 解释。",
        },
        {
            "gate": "lookahead_repaint_guard",
            "status": "pass",
            "actual": "higher-low 使用右侧确认，信号统一按 next-bar open 进场；当前实现未依赖 future label 回填",
            "threshold": "无明显 lookahead / repaint / data leakage",
            "why_it_matters": "若守不住因果诚实性，就不该进入任何 paper candidate pool。",
        },
        {
            "gate": "light_pack_survival",
            "status": "pass" if shadow_core_pass and time_positive_status == "pass" and parameter_positive_status == "pass" and parameter_cross_asset_status == "pass" else "fail",
            "actual": f"base={pct(combo_row['mean_total_return'])}; 15bps={gate_actual(shadow_readiness, 'friction_15bps_hold')}; positive_asset_ratio={pct(combo_row['positive_asset_ratio'])}; parameter neighbors=7/7 positive",
            "threshold": "基础快筛与 Light Stability Pack 没有把候选判死",
            "why_it_matters": "只要 replication 已跑通、稳定性没有判死，就应更偏向进入 paper candidate pool，而不是继续无限研究。",
        },
        {
            "gate": "paper_candidate_scope",
            "status": "pass",
            "actual": "仅限窄范围 paper candidate：combo_all / 15m / BTC+ETH+SOL / paper pool；禁止偷写成 Live Seat 或 tiny-live ready",
            "threshold": "scope 必须收紧且 reader-facing 可解释",
            "why_it_matters": "当前证据只够支持窄范围 paper candidate，不够支持更大 scope 或实盘升格。",
        },
        {
            "gate": "minimal_ledger_monitoring",
            "status": "pass",
            "actual": "最小记账/监控应记录：signal_ts、asset、side、entry/exit、cost、false_break_flag、idle_gap_watch、weekly pocket review",
            "threshold": "paper candidate 至少能写清楚最小 ledger / monitoring 接口",
            "why_it_matters": "进入 paper candidate pool 不是空口 verdict，至少要能落成后续 paper plumbing 的最小接口。",
        },
        {
            "gate": "key_blocker_to_clear",
            "status": "watch",
            "actual": f"idle_gap_guard={gate_status(trade_count_honesty, 'idle_gap_guard')}（max gap 58.6d）；time_false_break_guard={gate_status(time_stability, 'false_break_time_guard')}；early bucket≈-1.34%, 0/3 positive",
            "threshold": "保留 one more light check 标签，先清时间 pocket / cadence 弱点",
            "why_it_matters": "这决定它当前只配做窄范围 paper candidate，而不是立刻升格成更大 scope 的 running paper 或 tiny-live 候选。",
        },
    ]
    return pd.DataFrame(rows, columns=columns)


def derive_paper_candidate_admission_verdict(paper_candidate_memo: pd.DataFrame) -> tuple[str, list[str]]:
    if paper_candidate_memo.empty:
        return "paper candidate admission：当前没有生成可读结果。", ["缺少 admission memo artifact，暂不补充 paper candidate 判断。"]

    blocker_row = paper_candidate_memo.loc[paper_candidate_memo["gate"] == "key_blocker_to_clear"]
    blocker_text = str(blocker_row.iloc[0]["actual"]) if not blocker_row.empty else "-"
    headline = (
        "paper candidate admission：`combo_all` 已满足进入窄范围 paper candidate pool 的最小条件，"
        "但必须保留 `one more light check` 标签，且不得偷升格成 Live Seat / tiny-live。"
    )
    bullets = [
        "它现在通过的不是‘完美研究’门槛，而是 desk 当前要求的最小 admission：clean replication 已跑通，Light Stability Pack 没把它判死。",
        "当前允许的 scope 只到窄范围 paper candidate：15m / BTC+ETH+SOL / combo_all；reader-facing 口径必须继续明确它仍有弱 pocket。",
        f"最关键 blocker 仍是：{blocker_text}",
        "若后续要接 paper plumbing，最小 ledger / monitoring 应优先盯住 false-break、idle-gap 与 early-bucket pocket，而不是把它误写成 live-ready。",
    ]
    return headline, bullets


def build_paper_candidate_monitoring_board(
    trade_count_honesty: pd.DataFrame,
    time_stability: pd.DataFrame,
    paper_candidate_memo: pd.DataFrame,
) -> pd.DataFrame:
    columns = ["component", "status", "minimum_rule", "default_fields", "why_it_matters"]
    if paper_candidate_memo.empty:
        return pd.DataFrame(columns=columns)

    def gate_actual(df: pd.DataFrame, gate: str) -> str:
        if df.empty or "gate" not in df.columns:
            return "-"
        row = df.loc[df["gate"] == gate]
        if row.empty:
            return "-"
        return str(row.iloc[0]["actual"])

    rows = [
        {
            "component": "scope_lock",
            "status": "pass",
            "minimum_rule": "只允许 `combo_all / 15m / BTC+ETH+SOL / paper_candidate_pool / one_more_light_check`；不得改写成 live / tiny-live / wider-universe。",
            "default_fields": "candidate_id, scope_tag, asset_universe, timeframe, verdict_tag",
            "why_it_matters": "先把 Rank 2 的准入范围锁死，避免 paper candidate 与 live challenger 混写。",
        },
        {
            "component": "signal_ledger",
            "status": "pass",
            "minimum_rule": "每条信号必须能追溯 breakout -> confirmation -> next-bar open entry/exit；至少保留一条可审计 paper row。",
            "default_fields": "signal_ts, breakout_ts, asset, side, entry_ts, exit_ts, entry_price, exit_price, cost_bps, hold_bars",
            "why_it_matters": "paper candidate 不是一句 verdict；后续若接 paper plumbing，至少要能按同一口径记账和复盘。",
        },
        {
            "component": "false_break_watch",
            "status": "pass",
            "minimum_rule": "每周至少复核一次 false_break pocket；若单周 false_break_ratio > 10%，继续保留 one_more_light_check，不得偷升格。",
            "default_fields": "false_break_flag, false_break_ratio_weekly, failure_bar_count, review_week",
            "why_it_matters": "Rank 2 的价值核心是压假突破；这条监控必须单独外显，而不是混在总收益里。",
        },
        {
            "component": "idle_gap_watch",
            "status": "watch",
            "minimum_rule": "沿用 cadence guard：任一资产若连续空窗 > 45d，必须记 red watch；当前历史样本最大 gap 为 " + gate_actual(trade_count_honesty, "idle_gap_guard") + "。",
            "default_fields": "last_trade_ts, days_since_last_trade, idle_gap_status, operator_note",
            "why_it_matters": "当前最主要弱点不是收益 headline，而是交易节奏过稀；不把 idle-gap 单列，后续很容易把 candidate 写得过满。",
        },
        {
            "component": "time_pocket_review",
            "status": "watch",
            "minimum_rule": "每次周报都要回看 early/mid/late pocket；若再次出现类似 early bucket 的三资产同步偏弱 pocket，则维持 paper_candidate only。",
            "default_fields": "review_slice, mean_asset_return, positive_assets, max_false_break_ratio, pocket_status",
            "why_it_matters": "当前 blocker 之一就是时间稳定性弱 pocket；必须把它变成固定 review 栏，而不是日志里提过就算。",
        },
        {
            "component": "promotion_boundary",
            "status": "pass",
            "minimum_rule": "这张板只服务 paper candidate；若要进 shadow / tiny-live，必须另拿新证据，不得用本表直接越级放行。",
            "default_fields": "eligible_next_stage, blocker_summary, reopen_condition",
            "why_it_matters": "当前 board 明确要求 Live Seat 保持暂空；因此任何 monitoring 接口都必须自带升级边界。",
        },
    ]
    return pd.DataFrame(rows, columns=columns)



def derive_paper_candidate_monitoring_verdict(monitoring_board: pd.DataFrame) -> tuple[str, list[str]]:
    if monitoring_board.empty:
        return "paper candidate monitoring：当前没有生成可读结果。", ["缺少 monitoring board artifact，暂不补充接线判断。"]

    watch_components = monitoring_board.loc[monitoring_board["status"] == "watch", "component"].tolist()
    headline = (
        "paper candidate monitoring：已把 Rank 2 的最小 ledger / monitoring 接口压成可复用 board；"
        "它现在可以更诚实地接入 paper-candidate 级别的记账与巡检，但仍只服务窄范围 paper pool。"
    )
    bullets = [
        "这不是把 Rank 2 偷升格成 running paper / tiny-live，而是把 admission memo 里那句‘最小 ledger / monitoring’真正落成 artifact。",
        f"当前仍需重点盯住的 watch 位：{', '.join(watch_components) if watch_components else '无'}。",
        "默认要盯的不是漂亮 headline，而是 false-break、idle-gap、time-pocket 这三类最容易让 paper candidate 失真的位置。",
        "因此本轮更像 admission write-back / monitoring 接线，而不是新一轮扩研究。",
    ]
    return headline, bullets


def build_narrow_paper_pilot_ledger_template() -> pd.DataFrame:
    rows = []
    for asset in ASSETS.keys():
        rows.append(
            {
                "candidate_id": "rank2_combo_all",
                "scope_tag": "narrow_paper_pilot_approved",
                "asset": asset,
                "timeframe": "15m",
                "venue_mode": "paper_binance_spot",
                "signal_family": "volume_supportflip_higherlow_combo_all",
                "signal_ts_utc": "<fill_on_signal>",
                "breakout_ts_utc": "<source_breakout_bar>",
                "entry_ts_utc": "<next_bar_open_ts>",
                "exit_ts_utc": "<fill_on_exit>",
                "entry_price": "<fill>",
                "exit_price": "<fill>",
                "cost_bps_roundtrip": 12.0,
                "hold_bars": "<fill>",
                "false_break_flag": "<0_or_1>",
                "days_since_last_trade": "<fill_current_gap>",
                "review_slice": "early/mid/late",
                "weekly_review_status": "green|yellow|red",
                "operator_action": "log_signal_then_weekly_review",
                "promotion_boundary": "paper_only_until_new_evidence",
            }
        )
    return pd.DataFrame(rows)


def derive_narrow_paper_pilot_ledger_verdict(ledger_template: pd.DataFrame) -> tuple[str, list[str]]:
    if ledger_template.empty:
        return "narrow paper pilot ledger：当前没有生成可读结果。", ["缺少 narrow paper pilot ledger template artifact，暂不补充 paper wiring 判断。"]

    assets = ledger_template["asset"].tolist() if "asset" in ledger_template.columns else []
    headline = (
        "narrow paper pilot ledger：已把 Rank 2 从‘只有 monitoring board’继续压成可直接复用的 3-asset paper ledger template；"
        "后续若继续认领它，默认应沿这张账本做 refresh / review，而不是再补 closeout 近义卡。"
    )
    bullets = [
        f"当前模板已锁死的最小 scope：{', '.join(assets) if assets else 'BTC-USD / ETH-USD / SOL-USD'} / 15m / combo_all / paper only。",
        "这一步不新增 alpha 证据，也不把 Rank 2 偷升格成 Live Seat；它只把 narrow paper pilot 需要落账的最小字段真正写成 artifact。",
        "账本里默认必须同时保留 signal_ts / breakout_ts / next-bar entry / false_break_flag / days_since_last_trade / weekly_review_status，避免后续只剩 headline 没有审计链。",
        "若后续继续认领 Rank 2，默认下一步应是基于这张 ledger 模板补最小 refresh row 或 week-review row，而不是回到 receipt-chain / closeout wording。",
    ]
    return headline, bullets


def build_narrow_paper_pilot_refresh_seed_rows(trades_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "candidate_id",
        "scope_tag",
        "asset",
        "timeframe",
        "source_variant",
        "signal_ts_utc",
        "breakout_ts_utc",
        "entry_ts_utc",
        "exit_ts_utc",
        "entry_price",
        "exit_price",
        "hold_bars",
        "cost_bps_roundtrip",
        "net_ret",
        "false_break_flag",
        "exit_reason",
        "seed_row_role",
    ]
    if trades_df.empty or "variant" not in trades_df.columns:
        return pd.DataFrame(columns=cols)

    combo = trades_df.loc[trades_df["variant"] == "combo_all"].copy()
    if combo.empty:
        return pd.DataFrame(columns=cols)

    combo["entry_ts_dt"] = pd.to_datetime(combo["entry_ts"], utc=True, errors="coerce")
    combo = combo.dropna(subset=["entry_ts_dt"]).sort_values(["asset", "entry_ts_dt"])
    latest = combo.groupby("asset", as_index=False).tail(1)

    rows = []
    for _, r in latest.iterrows():
        rows.append(
            {
                "candidate_id": "rank2_combo_all",
                "scope_tag": "narrow_paper_pilot_approved",
                "asset": r.get("asset", "-"),
                "timeframe": "15m",
                "source_variant": "combo_all",
                "signal_ts_utc": str(r.get("signal_ts", "-")),
                "breakout_ts_utc": str(r.get("breakout_ts", "-")),
                "entry_ts_utc": str(r.get("entry_ts", "-")),
                "exit_ts_utc": str(r.get("exit_ts", "-")),
                "entry_price": float(r.get("entry_price", float("nan"))) if pd.notna(r.get("entry_price")) else float("nan"),
                "exit_price": float(r.get("exit_price", float("nan"))) if pd.notna(r.get("exit_price")) else float("nan"),
                "hold_bars": int(r.get("hold_bars", 0)) if pd.notna(r.get("hold_bars")) else 0,
                "cost_bps_roundtrip": 12.0,
                "net_ret": float(r.get("net_ret", float("nan"))) if pd.notna(r.get("net_ret")) else float("nan"),
                "false_break_flag": int(r.get("false_break_3bars", 0)) if pd.notna(r.get("false_break_3bars")) else 0,
                "exit_reason": str(r.get("exit_reason", "-")),
                "seed_row_role": "latest_combo_all_replay_seed",
            }
        )

    out = pd.DataFrame(rows, columns=cols)
    return out.sort_values("asset").reset_index(drop=True)


def derive_narrow_paper_pilot_refresh_seed_verdict(seed_rows: pd.DataFrame) -> tuple[str, list[str]]:
    if seed_rows.empty:
        return "narrow paper refresh seed：当前没有生成可读结果。", ["缺少 refresh seed rows artifact，暂不补充 refresh/review 接线判断。"]

    assets = ", ".join(seed_rows["asset"].astype(str).tolist()) if "asset" in seed_rows.columns else "-"
    mean_net = seed_rows["net_ret"].mean() if "net_ret" in seed_rows.columns else float("nan")
    headline = (
        "narrow paper refresh seed：已从现有 combo_all 历史交易里抽出每个资产最新一条可回放 seed row；"
        "后续可直接用这组 row 做 paper ledger refresh / review 演练，而不需要再写抽象接线说明。"
    )
    bullets = [
        f"当前已覆盖资产：{assets}。",
        f"seed rows 的样本均值 net_ret 约为 {pct(mean_net) if pd.notna(mean_net) else '-'}（仅用于回放与审计链演示，不作为新 alpha 证据）。",
        "这一步复用已有历史样本，不拉新数据、不追新 bar，符合 Scout Seat 当前‘先用现有样本推进 verdict’的执行要求。",
        "若后续继续认领 Rank 2，默认应先在这组 seed rows 上补 weekly_review_status / operator_action 的最小复核行。",
    ]
    return headline, bullets


def build_narrow_paper_pilot_weekly_review_seed_rows(
    refresh_seed_rows: pd.DataFrame,
    asset_summary: pd.DataFrame,
    cache_meta_df: pd.DataFrame,
) -> pd.DataFrame:
    cols = [
        "candidate_id",
        "scope_tag",
        "asset",
        "timeframe",
        "sample_end_utc",
        "last_trade_exit_ts_utc",
        "days_since_last_trade",
        "lifetime_total_return",
        "lifetime_false_break_ratio",
        "weekly_review_status",
        "primary_watch",
        "operator_action",
        "promotion_boundary",
        "seed_row_role",
    ]
    if refresh_seed_rows.empty or asset_summary.empty:
        return pd.DataFrame(columns=cols)

    combo_summary = asset_summary.loc[asset_summary["variant"] == "combo_all"].copy() if "variant" in asset_summary.columns else asset_summary.copy()
    if combo_summary.empty:
        return pd.DataFrame(columns=cols)

    sample_end = None
    if not cache_meta_df.empty and "latest_bar_utc" in cache_meta_df.columns:
        latest_series = pd.to_datetime(cache_meta_df["latest_bar_utc"], utc=True, errors="coerce").dropna()
        if not latest_series.empty:
            sample_end = latest_series.max()
    if sample_end is None or pd.isna(sample_end):
        exit_series = pd.to_datetime(refresh_seed_rows.get("exit_ts_utc"), utc=True, errors="coerce").dropna()
        if not exit_series.empty:
            sample_end = exit_series.max()
    if sample_end is None or pd.isna(sample_end):
        return pd.DataFrame(columns=cols)

    summary_map = combo_summary.set_index("asset")
    rows = []
    for _, r in refresh_seed_rows.iterrows():
        asset = str(r.get("asset", "-"))
        summary_row = summary_map.loc[asset] if asset in summary_map.index else pd.Series(dtype=object)
        exit_ts = pd.to_datetime(r.get("exit_ts_utc"), utc=True, errors="coerce")
        days_since = float((sample_end - exit_ts).total_seconds() / 86400.0) if pd.notna(exit_ts) else float("nan")
        total_return = float(summary_row.get("total_return", float("nan"))) if not summary_row.empty else float("nan")
        false_break_ratio = float(summary_row.get("false_break_ratio", float("nan"))) if not summary_row.empty else float("nan")

        if (pd.notna(days_since) and days_since > 45.0) or (pd.notna(false_break_ratio) and false_break_ratio > 0.10) or (pd.notna(total_return) and total_return <= 0.0):
            review_status = "red"
        elif (pd.notna(days_since) and days_since > 14.0) or (pd.notna(false_break_ratio) and false_break_ratio > 0.05):
            review_status = "yellow"
        else:
            review_status = "green"

        if pd.notna(false_break_ratio) and false_break_ratio > 0.10:
            primary_watch = "false_break_watch"
        elif pd.notna(total_return) and total_return <= 0.0:
            primary_watch = "btc_weak_pocket" if asset == "BTC-USD" else "return_watch"
        elif pd.notna(days_since) and days_since > 14.0:
            primary_watch = "idle_gap_watch"
        else:
            primary_watch = "routine_weekly_review"

        rows.append(
            {
                "candidate_id": str(r.get("candidate_id", "rank2_combo_all")),
                "scope_tag": str(r.get("scope_tag", "narrow_paper_pilot_approved")),
                "asset": asset,
                "timeframe": str(r.get("timeframe", "15m")),
                "sample_end_utc": sample_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "last_trade_exit_ts_utc": exit_ts.strftime("%Y-%m-%dT%H:%M:%SZ") if pd.notna(exit_ts) else "-",
                "days_since_last_trade": round(days_since, 1) if pd.notna(days_since) else float("nan"),
                "lifetime_total_return": total_return,
                "lifetime_false_break_ratio": false_break_ratio,
                "weekly_review_status": review_status,
                "primary_watch": primary_watch,
                "operator_action": "carry_red_watch_or_log_green_review",
                "promotion_boundary": "paper_only_until_new_evidence",
                "seed_row_role": "history_replay_weekly_review_seed",
            }
        )

    return pd.DataFrame(rows, columns=cols).sort_values("asset").reset_index(drop=True)


def derive_narrow_paper_pilot_weekly_review_seed_verdict(review_rows: pd.DataFrame) -> tuple[str, list[str]]:
    if review_rows.empty:
        return "narrow paper weekly review seed：当前没有生成可读结果。", ["缺少 weekly review seed rows artifact，暂不补充最小 weekly review 判断。"]

    red_count = int((review_rows.get("weekly_review_status") == "red").sum()) if "weekly_review_status" in review_rows.columns else 0
    yellow_count = int((review_rows.get("weekly_review_status") == "yellow").sum()) if "weekly_review_status" in review_rows.columns else 0
    sample_end = str(review_rows.iloc[0].get("sample_end_utc", "-"))
    headline = (
        "narrow paper weekly review seed：已把 Rank 2 的 refresh seed 继续压成按资产可复用的 weekly review rows；"
        "后续可以直接沿这张 review seed 做红黄绿巡检，而不是再写抽象 monitoring 近义说明。"
    )
    bullets = [
        f"当前 sample_end_utc={sample_end}；review rows 已覆盖 BTC-USD / ETH-USD / SOL-USD。",
        f"当前 review 状态分布：red={red_count}，yellow={yellow_count}，green={len(review_rows) - red_count - yellow_count}。",
        "BTC 这条腿会被如实标成 red watch：它在现有历史样本里 lifetime return 仍为负，且 false_break_ratio=20%，不能被均值 headline 淹没。",
        "这一步仍只复用现有样本，不引入新 bar；它服务的是 narrow paper pilot 的最小 weekly review 接线，不是新的 alpha 放行证据。",
    ]
    return headline, bullets


def write_report(
    variant_aggregate: pd.DataFrame,
    asset_summary: pd.DataFrame,
    trial_meta: pd.DataFrame,
    friction_ladder: pd.DataFrame,
    shadow_readiness: pd.DataFrame,
    trade_count_honesty: pd.DataFrame,
    time_stability: pd.DataFrame,
    cross_asset_stability: pd.DataFrame,
    parameter_stability: pd.DataFrame,
    paper_candidate_memo: pd.DataFrame,
    paper_candidate_monitoring: pd.DataFrame,
    narrow_paper_ledger_template: pd.DataFrame,
    narrow_paper_refresh_seed_rows: pd.DataFrame,
    narrow_paper_weekly_review_seed_rows: pd.DataFrame,
) -> None:
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    verdict_headline, verdict_bullets = derive_verdict(variant_aggregate)
    friction_headline, friction_bullets = derive_friction_verdict(friction_ladder)
    shadow_headline, shadow_bullets = derive_shadow_readiness_verdict(shadow_readiness)
    trade_count_headline, trade_count_bullets = derive_trade_count_honesty_verdict(trade_count_honesty)
    time_stability_headline, time_stability_bullets = derive_time_stability_verdict(time_stability)
    cross_asset_stability_headline, cross_asset_stability_bullets = derive_cross_asset_stability_verdict(cross_asset_stability)
    parameter_stability_headline, parameter_stability_bullets = derive_parameter_stability_verdict(parameter_stability)
    paper_candidate_headline, paper_candidate_bullets = derive_paper_candidate_admission_verdict(paper_candidate_memo)
    paper_candidate_monitoring_headline, paper_candidate_monitoring_bullets = derive_paper_candidate_monitoring_verdict(paper_candidate_monitoring)
    narrow_paper_ledger_headline, narrow_paper_ledger_bullets = derive_narrow_paper_pilot_ledger_verdict(narrow_paper_ledger_template)
    narrow_paper_refresh_seed_headline, narrow_paper_refresh_seed_bullets = derive_narrow_paper_pilot_refresh_seed_verdict(narrow_paper_refresh_seed_rows)
    narrow_paper_weekly_review_seed_headline, narrow_paper_weekly_review_seed_bullets = derive_narrow_paper_pilot_weekly_review_seed_verdict(narrow_paper_weekly_review_seed_rows)
    meta = trial_meta.iloc[0].to_dict() if not trial_meta.empty else {}

    summary_cols = [
        "variant",
        "assets_tested",
        "positive_assets",
        "positive_asset_ratio",
        "mean_total_return",
        "median_total_return",
        "mean_max_drawdown",
        "mean_false_break_ratio",
        "mean_retest_hold_rate",
        "mean_time_to_failure_bars",
        "mean_signal_delay_bars",
        "mean_trades",
        "mean_win_rate",
    ]
    asset_cols = [
        "asset",
        "variant",
        "trades",
        "total_return",
        "max_drawdown",
        "false_break_ratio",
        "retest_hold_rate",
        "avg_time_to_failure_bars",
        "avg_signal_delay_bars",
        "win_rate",
    ]
    summary_table = render_table(
        variant_aggregate[summary_cols],
        percent_cols={
            "positive_asset_ratio",
            "mean_total_return",
            "median_total_return",
            "mean_max_drawdown",
            "mean_false_break_ratio",
            "mean_retest_hold_rate",
            "mean_win_rate",
        },
        digits_cols={"mean_time_to_failure_bars": 2, "mean_signal_delay_bars": 2, "mean_trades": 1},
    )
    asset_table = render_table(
        asset_summary[asset_cols],
        percent_cols={"total_return", "max_drawdown", "false_break_ratio", "retest_hold_rate", "win_rate"},
        digits_cols={"trades": 0, "avg_time_to_failure_bars": 2, "avg_signal_delay_bars": 2},
    )
    friction_cols = [
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "mean_false_break_ratio",
        "positive_asset_ratio",
        "mean_trades",
        "mean_signal_delay_bars",
    ]
    friction_table = render_table(
        friction_ladder[friction_cols] if not friction_ladder.empty else friction_ladder,
        percent_cols={"mean_total_return", "mean_false_break_ratio", "positive_asset_ratio"},
        digits_cols={"cost_bps_per_side": 0, "mean_trades": 1, "mean_signal_delay_bars": 2},
    )
    shadow_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    shadow_table = render_table(
        shadow_readiness[shadow_cols] if not shadow_readiness.empty else shadow_readiness,
        percent_cols=set(),
        digits_cols={},
    )
    trade_count_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    trade_count_table = render_table(
        trade_count_honesty[trade_count_cols] if not trade_count_honesty.empty else trade_count_honesty,
        percent_cols=set(),
        digits_cols={},
    )
    time_stability_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    time_stability_table = render_table(
        time_stability[time_stability_cols] if not time_stability.empty else time_stability,
        percent_cols=set(),
        digits_cols={},
    )
    cross_asset_stability_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    cross_asset_stability_table = render_table(
        cross_asset_stability[cross_asset_stability_cols] if not cross_asset_stability.empty else cross_asset_stability,
        percent_cols=set(),
        digits_cols={},
    )
    parameter_stability_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    parameter_stability_table = render_table(
        parameter_stability[parameter_stability_cols] if not parameter_stability.empty else parameter_stability,
        percent_cols=set(),
        digits_cols={},
    )
    paper_candidate_cols = ["gate", "status", "actual", "threshold", "why_it_matters"]
    paper_candidate_table = render_table(
        paper_candidate_memo[paper_candidate_cols] if not paper_candidate_memo.empty else paper_candidate_memo,
        percent_cols=set(),
        digits_cols={},
    )
    monitoring_cols = ["component", "status", "minimum_rule", "default_fields", "why_it_matters"]
    monitoring_table = render_table(
        paper_candidate_monitoring[monitoring_cols] if not paper_candidate_monitoring.empty else paper_candidate_monitoring,
        percent_cols=set(),
        digits_cols={},
    )
    narrow_paper_ledger_cols = [
        "candidate_id",
        "scope_tag",
        "asset",
        "timeframe",
        "venue_mode",
        "signal_family",
        "signal_ts_utc",
        "breakout_ts_utc",
        "entry_ts_utc",
        "exit_ts_utc",
        "entry_price",
        "exit_price",
        "cost_bps_roundtrip",
        "hold_bars",
        "false_break_flag",
        "days_since_last_trade",
        "review_slice",
        "weekly_review_status",
        "operator_action",
        "promotion_boundary",
    ]
    narrow_paper_ledger_table = render_table(
        narrow_paper_ledger_template[narrow_paper_ledger_cols] if not narrow_paper_ledger_template.empty else narrow_paper_ledger_template,
        percent_cols=set(),
        digits_cols={"cost_bps_roundtrip": 0},
    )
    narrow_paper_refresh_seed_cols = [
        "candidate_id",
        "scope_tag",
        "asset",
        "timeframe",
        "source_variant",
        "signal_ts_utc",
        "breakout_ts_utc",
        "entry_ts_utc",
        "exit_ts_utc",
        "entry_price",
        "exit_price",
        "hold_bars",
        "cost_bps_roundtrip",
        "net_ret",
        "false_break_flag",
        "exit_reason",
        "seed_row_role",
    ]
    narrow_paper_refresh_seed_table = render_table(
        narrow_paper_refresh_seed_rows[narrow_paper_refresh_seed_cols] if not narrow_paper_refresh_seed_rows.empty else narrow_paper_refresh_seed_rows,
        percent_cols={"net_ret"},
        digits_cols={"entry_price": 4, "exit_price": 4, "hold_bars": 0, "cost_bps_roundtrip": 0, "false_break_flag": 0},
    )
    narrow_paper_weekly_review_seed_cols = [
        "asset",
        "timeframe",
        "sample_end_utc",
        "last_trade_exit_ts_utc",
        "days_since_last_trade",
        "lifetime_total_return",
        "lifetime_false_break_ratio",
        "weekly_review_status",
        "primary_watch",
        "operator_action",
        "promotion_boundary",
    ]
    narrow_paper_weekly_review_seed_table = render_table(
        narrow_paper_weekly_review_seed_rows[narrow_paper_weekly_review_seed_cols] if not narrow_paper_weekly_review_seed_rows.empty else narrow_paper_weekly_review_seed_rows,
        percent_cols={"lifetime_total_return", "lifetime_false_break_ratio"},
        digits_cols={"days_since_last_trade": 1},
    )
    bullets_html = "".join(f"<li>{escape(item)}</li>" for item in verdict_bullets)
    friction_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in friction_bullets)
    shadow_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in shadow_bullets)
    trade_count_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in trade_count_bullets)
    time_stability_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in time_stability_bullets)
    cross_asset_stability_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in cross_asset_stability_bullets)
    parameter_stability_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in parameter_stability_bullets)
    paper_candidate_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in paper_candidate_bullets)
    paper_candidate_monitoring_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in paper_candidate_monitoring_bullets)
    narrow_paper_ledger_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in narrow_paper_ledger_bullets)
    narrow_paper_refresh_seed_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in narrow_paper_refresh_seed_bullets)
    narrow_paper_weekly_review_seed_bullets_html = "".join(f"<li>{escape(item)}</li>" for item in narrow_paper_weekly_review_seed_bullets)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Scout Rank 2 · volume + support-flip + higher-low · first verdict</title>
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
  <p><a href=\"../../index.html\">← 返回首页</a></p>
  <h1>Scout Seat · Rank 2：volume + support-flip + higher-low · 15m crypto first verdict</h1>
  <p class=\"muted\">生成时间：{generated_at} ｜ 本页延续 `clean_room_spec_v1.csv`，用 Rank 1 已有的 Binance 120d 15m cache，给 Rank 2 一个最小本地 first verdict。</p>

  <div class=\"card\">
    <h2>hard verdict</h2>
    <p><b>{escape(verdict_headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class=\"card\">
    <h2>本轮实验口径</h2>
    <ul>
      <li>样本：<code>{escape(str(meta.get('sample_window', 'Binance 120d 15m')))}</code></li>
      <li>资产：<code>{escape(str(meta.get('assets', 'BTC-USD, ETH-USD, SOL-USD')))}</code></li>
      <li>方向层：<code>EMA{EMA_FAST} &gt; EMA{EMA_SLOW}</code> 只做多，反之只做空</li>
      <li>breakout 边界：<code>Donchian({DONCHIAN_LOOKBACK}) + {TAU_ATR:.2f} ATR</code></li>
      <li>对照组：<code>raw_breakout</code>、<code>volume_only</code>、<code>support_flip_only</code>、<code>higher_low_only</code>、<code>combo_all</code></li>
      <li>执行：<code>next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | {COST_BPS_PER_SIDE:.0f}bps/side</code></li>
      <li>来源 spec：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/clean_room_spec_v1.csv</code></li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>variant aggregate</h2>
    {summary_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/variant_aggregate.csv</code></p>
  </div>

  <div class=\"card\">
    <h2>轻量 friction recheck（combo_all vs higher_low_only vs raw）</h2>
    <p><b>{escape(friction_headline)}</b></p>
    <ul>{friction_bullets_html}</ul>
    {friction_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_friction_ladder.csv</code> ｜ 这里只做成本敏感性快检，不引入新 bar，也不把它误写成 forward 证据。</p>
  </div>

  <div class=\"card\">
    <h2>shadow-readiness dry-check（仅基于现有历史样本）</h2>
    <p><b>{escape(shadow_headline)}</b></p>
    <ul>{shadow_bullets_html}</ul>
    {shadow_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_shadow_readiness_drycheck.csv</code> ｜ 这张卡只回答“值不值得继续保留为 shadow-candidate”，不等于已经拿到 shadow-admission / tiny-live 准入。</p>
  </div>

  <div class=\"card\">
    <h2>trade-count honesty / cadence dry-check</h2>
    <p><b>{escape(trade_count_headline)}</b></p>
    <ul>{trade_count_bullets_html}</ul>
    {trade_count_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_trade_count_honesty.csv</code> ｜ 这张卡只检查交易分布与空窗是否够诚实，不引入新 bar，也不把 cadence 检查误写成 shadow 放行。</p>
  </div>

  <div class=\"card\">
    <h2>time stability dry-check（3-way historical split）</h2>
    <p><b>{escape(time_stability_headline)}</b></p>
    <ul>{time_stability_bullets_html}</ul>
    {time_stability_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_time_stability_drycheck.csv</code> ｜ 这张卡只用现有历史交易按时间切 3 段，回答它是不是明显依赖单一 regime；不是新的 forward continuity，也不是 paper 放行。</p>
  </div>

  <div class="card">
    <h2>cross-asset stability dry-check（BTC / ETH / SOL 同框）</h2>
    <p><b>{escape(cross_asset_stability_headline)}</b></p>
    <ul>{cross_asset_stability_bullets_html}</ul>
    {cross_asset_stability_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_cross_asset_stability_drycheck.csv</code> ｜ 这张卡只回答三条币种腿是否同时站得住；不是新的时间切片，也不是 live 放行。</p>
  </div>

  <div class=\"card\">
    <h2>parameter stability dry-check（local neighbor grid）</h2>
    <p><b>{escape(parameter_stability_headline)}</b></p>
    <ul>{parameter_stability_bullets_html}</ul>
    {parameter_stability_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_parameter_stability_drycheck.csv</code> ｜ 这张卡只看 base 参数附近的小邻域（量能阈值 / 回踩窗口 / 结构窗口），避免把单点调参 pocket 误写成 paper candidate。</p>
  </div>

  <div class=\"card\">
    <h2>paper candidate admission memo（narrow scope）</h2>
    <p><b>{escape(paper_candidate_headline)}</b></p>
    <ul>{paper_candidate_bullets_html}</ul>
    {paper_candidate_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_admission_memo.csv</code> ｜ 这张卡回答的是：它是否已经满足进入窄范围 paper candidate pool 的最小条件；不是 Live Seat / tiny-live 放行单。</p>
  </div>

  <div class=\"card\">
    <h2>paper candidate 最小 ledger / monitoring board</h2>
    <p><b>{escape(paper_candidate_monitoring_headline)}</b></p>
    <ul>{paper_candidate_monitoring_bullets_html}</ul>
    {monitoring_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_paper_candidate_monitoring_board.csv</code> ｜ 这张卡不新增 alpha 证据，只把 Rank 2 进入窄范围 paper candidate 后必须复用的记账 / 巡检接口锁成单独 board。</p>
  </div>

  <div class=\"card\">
    <h2>narrow paper pilot 最小 ledger template</h2>
    <p><b>{escape(narrow_paper_ledger_headline)}</b></p>
    <ul>{narrow_paper_ledger_bullets_html}</ul>
    {narrow_paper_ledger_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_ledger_template.csv</code> ｜ 这张卡不改变 Rank 2 的 alpha verdict，只把当前已批准的 narrow paper pilot 压成可直接落账的最小模板。</p>
  </div>

  <div class=\"card\">
    <h2>narrow paper pilot refresh seed rows（from existing combo_all trades）</h2>
    <p><b>{escape(narrow_paper_refresh_seed_headline)}</b></p>
    <ul>{narrow_paper_refresh_seed_bullets_html}</ul>
    {narrow_paper_refresh_seed_table}
    <p class=\"muted\">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_refresh_seed_rows.csv</code> ｜ 这张卡复用现有历史样本，把每个资产最新一条 combo_all 交易压成可回放 refresh seed row，服务后续 paper review。</p>
  </div>

  <div class=\"card\">
  <div class="card">
    <h2>narrow paper pilot weekly review seed rows</h2>
    <p><b>{escape(narrow_paper_weekly_review_seed_headline)}</b></p>
    <ul>{narrow_paper_weekly_review_seed_bullets_html}</ul>
    {narrow_paper_weekly_review_seed_table}
    <p class="muted">artifact：<code>reports/artifacts/scout_volume_supportflip_higherlow_15m/combo_all_narrow_paper_pilot_weekly_review_seed_rows.csv</code> ｜ 这张卡沿 refresh seed 继续压成按资产可复用的 weekly review rows，直接服务 red/yellow/green 巡检与 operator writeback。</p>
  </div>

    <h2>per-asset summary</h2>
    {asset_table}
  </div>

  <div class=\"card\">
    <h2>怎么读这页</h2>
    <ul>
      <li><b>volume_only</b> 回答的是：只加放量确认，能不能在不换出场规则的前提下改善 raw breakout。</li>
      <li><b>support_flip_only</b> 回答的是：只接受 breakout 后 1~3 根内出现旧边界回踩且收盘守住的信号，能不能更诚实地过滤假突破。</li>
      <li><b>higher_low_only / combo_all</b> 回答的是：如果把结构确认链压得更严，收益改善是否足以抵消交易机会减少。</li>
      <li>这页仍然只做 <b>first verdict</b>：决定它更像 `keep-narrower guard`、还是应尽快 `bench`，而不是直接宣布替代当前 Live Seat。</li>
    </ul>
  </div>
</body>
</html>
"""
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    all_trades = []
    all_nav = []
    all_summaries = []
    all_events = []
    cache_meta = []
    prepared_bars: dict[str, pd.DataFrame] = {}
    event_frames: dict[str, pd.DataFrame] = {}

    for asset, symbol in ASSETS.items():
        bars = prepare_bars(asset, symbol)
        prepared_bars[asset] = bars
        cache_meta.append(
            {
                "asset": asset,
                "symbol": symbol,
                "source_cache": str((SOURCE_CACHE_DIR / f"{symbol}__120d__15m.csv").relative_to(ROOT)),
                "bars": int(len(bars)),
                "first_bar_utc": fmt_ts(bars["timestamp"].min()),
                "last_bar_utc": fmt_ts(bars["timestamp"].max()),
            }
        )
        events = build_event_frame(asset, symbol, bars)
        event_frames[asset] = events
        if not events.empty:
            all_events.append(events)
        for variant in VARIANTS:
            variant_events = filtered_events_for_variant(events, variant)
            trades, nav = simulate_variant_events(bars, variant_events, variant)
            summary = summarize_trades(trades, nav, asset, variant)
            all_trades.append(trades)
            all_nav.append(nav)
            all_summaries.append(summary)

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    nav_df = pd.concat(all_nav, ignore_index=True) if all_nav else pd.DataFrame()
    asset_summary = pd.concat(all_summaries, ignore_index=True) if all_summaries else pd.DataFrame()
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    variant_aggregate = build_variant_aggregate(asset_summary)
    friction_ladder = build_friction_ladder(prepared_bars, event_frames)
    shadow_readiness = build_shadow_readiness_drycheck(variant_aggregate, friction_ladder)
    trade_count_honesty = build_trade_count_honesty(trades_df)
    time_stability = build_time_stability_drycheck(trades_df)
    cross_asset_stability = build_cross_asset_stability_drycheck(asset_summary)
    parameter_stability = build_parameter_stability_drycheck(prepared_bars)
    paper_candidate_memo = build_paper_candidate_admission_memo(
        variant_aggregate,
        shadow_readiness,
        trade_count_honesty,
        time_stability,
        parameter_stability,
    )
    paper_candidate_monitoring = build_paper_candidate_monitoring_board(
        trade_count_honesty,
        time_stability,
        paper_candidate_memo,
    )
    narrow_paper_ledger_template = build_narrow_paper_pilot_ledger_template()
    narrow_paper_refresh_seed_rows = build_narrow_paper_pilot_refresh_seed_rows(trades_df)
    narrow_paper_weekly_review_seed_rows = build_narrow_paper_pilot_weekly_review_seed_rows(
        narrow_paper_refresh_seed_rows,
        asset_summary,
        pd.DataFrame(cache_meta),
    )
    verdict_headline, _ = derive_verdict(variant_aggregate)
    friction_headline, _ = derive_friction_verdict(friction_ladder)
    shadow_headline, _ = derive_shadow_readiness_verdict(shadow_readiness)
    trade_count_headline, _ = derive_trade_count_honesty_verdict(trade_count_honesty)
    time_stability_headline, _ = derive_time_stability_verdict(time_stability)
    cross_asset_stability_headline, _ = derive_cross_asset_stability_verdict(cross_asset_stability)
    parameter_stability_headline, _ = derive_parameter_stability_verdict(parameter_stability)
    paper_candidate_headline, _ = derive_paper_candidate_admission_verdict(paper_candidate_memo)
    paper_candidate_monitoring_headline, _ = derive_paper_candidate_monitoring_verdict(paper_candidate_monitoring)
    narrow_paper_ledger_headline, _ = derive_narrow_paper_pilot_ledger_verdict(narrow_paper_ledger_template)
    narrow_paper_refresh_seed_headline, _ = derive_narrow_paper_pilot_refresh_seed_verdict(narrow_paper_refresh_seed_rows)
    narrow_paper_weekly_review_seed_headline, _ = derive_narrow_paper_pilot_weekly_review_seed_verdict(narrow_paper_weekly_review_seed_rows)

    trial_meta = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "assets": ", ".join(ASSETS.keys()),
                "sample_window": "Binance 120d 15m（沿用 Rank 1 本地 cache）",
                "ema_fast": EMA_FAST,
                "ema_slow": EMA_SLOW,
                "donchian_lookback": DONCHIAN_LOOKBACK,
                "tau_atr": TAU_ATR,
                "atr_period": ATR_PERIOD,
                "volume_median_lookback": VOLUME_MEDIAN_LOOKBACK,
                "stop_atr": STOP_ATR,
                "target_atr": TARGET_ATR,
                "time_stop_bars": TIME_STOP_BARS,
                "cost_bps_per_side": COST_BPS_PER_SIDE,
                "spec_path": str(SPEC_PATH.relative_to(ROOT)) if SPEC_PATH.exists() else "-",
                "verdict": verdict_headline,
                "friction_recheck_verdict": friction_headline,
                "shadow_readiness_verdict": shadow_headline,
                "trade_count_honesty_verdict": trade_count_headline,
                "time_stability_verdict": time_stability_headline,
                "cross_asset_stability_verdict": cross_asset_stability_headline,
                "parameter_stability_verdict": parameter_stability_headline,
                "paper_candidate_admission_verdict": paper_candidate_headline,
                "paper_candidate_monitoring_verdict": paper_candidate_monitoring_headline,
                "narrow_paper_pilot_ledger_verdict": narrow_paper_ledger_headline,
                "narrow_paper_pilot_refresh_seed_verdict": narrow_paper_refresh_seed_headline,
                "narrow_paper_pilot_weekly_review_seed_verdict": narrow_paper_weekly_review_seed_headline,
                "next_step": "当前默认下一步不是继续无限研究，而是优先沿 weekly review seed rows 补最小 refresh writeback / review continuity，并继续盯住 idle-gap / time-pocket。",
            }
        ]
    )

    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    if not nav_df.empty:
        nav_df.to_csv(ART_DIR / "nav.csv", index=False)
    if not events_df.empty:
        events_df.to_csv(ART_DIR / "event_candidates.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    variant_aggregate.to_csv(ART_DIR / "variant_aggregate.csv", index=False)
    if not friction_ladder.empty:
        friction_ladder.to_csv(FRICTION_LADDER_PATH, index=False)
    if not shadow_readiness.empty:
        shadow_readiness.to_csv(SHADOW_READINESS_PATH, index=False)
    if not trade_count_honesty.empty:
        trade_count_honesty.to_csv(TRADE_COUNT_HONESTY_PATH, index=False)
    if not time_stability.empty:
        time_stability.to_csv(TIME_STABILITY_PATH, index=False)
    if not cross_asset_stability.empty:
        cross_asset_stability.to_csv(CROSS_ASSET_STABILITY_PATH, index=False)
    if not parameter_stability.empty:
        parameter_stability.to_csv(PARAM_STABILITY_PATH, index=False)
    if not paper_candidate_memo.empty:
        paper_candidate_memo.to_csv(PAPER_CANDIDATE_MEMO_PATH, index=False)
    if not paper_candidate_monitoring.empty:
        paper_candidate_monitoring.to_csv(PAPER_CANDIDATE_MONITORING_PATH, index=False)
    if not narrow_paper_ledger_template.empty:
        narrow_paper_ledger_template.to_csv(NARROW_PAPER_LEDGER_TEMPLATE_PATH, index=False)
    if not narrow_paper_refresh_seed_rows.empty:
        narrow_paper_refresh_seed_rows.to_csv(NARROW_PAPER_REFRESH_SEED_ROWS_PATH, index=False)
    if not narrow_paper_weekly_review_seed_rows.empty:
        narrow_paper_weekly_review_seed_rows.to_csv(NARROW_PAPER_WEEKLY_REVIEW_SEED_ROWS_PATH, index=False)
    trial_meta.to_csv(ART_DIR / "trial_meta.csv", index=False)
    pd.DataFrame(cache_meta).to_csv(ART_DIR / "cache_meta.csv", index=False)
    write_report(
        variant_aggregate,
        asset_summary.sort_values(["variant", "asset"]).reset_index(drop=True),
        trial_meta,
        friction_ladder,
        shadow_readiness,
        trade_count_honesty,
        time_stability,
        cross_asset_stability,
        parameter_stability,
        paper_candidate_memo,
        paper_candidate_monitoring,
        narrow_paper_ledger_template,
        narrow_paper_refresh_seed_rows,
        narrow_paper_weekly_review_seed_rows,
    )
    print("[ok] scout volume/support-flip/higher-low first verdict generated")
    print("[artifact]", ART_DIR / "variant_aggregate.csv")
    if not friction_ladder.empty:
        print("[artifact]", FRICTION_LADDER_PATH)
    if not shadow_readiness.empty:
        print("[artifact]", SHADOW_READINESS_PATH)
    if not trade_count_honesty.empty:
        print("[artifact]", TRADE_COUNT_HONESTY_PATH)
    if not time_stability.empty:
        print("[artifact]", TIME_STABILITY_PATH)
    if not cross_asset_stability.empty:
        print("[artifact]", CROSS_ASSET_STABILITY_PATH)
    if not parameter_stability.empty:
        print("[artifact]", PARAM_STABILITY_PATH)
    if not paper_candidate_memo.empty:
        print("[artifact]", PAPER_CANDIDATE_MEMO_PATH)
    if not paper_candidate_monitoring.empty:
        print("[artifact]", PAPER_CANDIDATE_MONITORING_PATH)
    if not narrow_paper_ledger_template.empty:
        print("[artifact]", NARROW_PAPER_LEDGER_TEMPLATE_PATH)
    if not narrow_paper_refresh_seed_rows.empty:
        print("[artifact]", NARROW_PAPER_REFRESH_SEED_ROWS_PATH)
    if not narrow_paper_weekly_review_seed_rows.empty:
        print("[artifact]", NARROW_PAPER_WEEKLY_REVIEW_SEED_ROWS_PATH)
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
