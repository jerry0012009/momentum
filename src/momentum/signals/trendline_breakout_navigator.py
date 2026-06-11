"""Clean reimplementation of a multi-timeframe trendline breakout navigator.

Design notes:
- inspired by the logic path used in PyIndicators' breakout navigator
- implemented from scratch in the style of this repository
- confirmation is causal: pivots are only known on their confirmation bar
- output is research-friendly and auditable bar-by-bar
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "high", "low", "close"]


@dataclass(frozen=True)
class TrendlineBreakoutNavigatorConfig:
    swing_long: int = 60
    swing_medium: int = 30
    swing_short: int = 10
    swing_right: int = 1
    min_pivot_gap: int = 5
    enable_long: bool = True
    enable_medium: bool = True
    enable_short: bool = True
    backfill_history: bool = True


def _validate_df(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _validate_config(config: TrendlineBreakoutNavigatorConfig) -> None:
    if config.swing_right <= 0:
        raise ValueError("swing_right must be > 0")
    for name in ["swing_long", "swing_medium", "swing_short"]:
        if getattr(config, name) <= 1:
            raise ValueError(f"{name} must be > 1")
    if config.min_pivot_gap < 1:
        raise ValueError("min_pivot_gap must be >= 1")


def _confirmed_pivot_high(high: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(high)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = high[center]
        if np.isnan(v):
            continue
        left_ok = bool(np.all(v > high[center - left:center]))
        right_ok = bool(np.all(v > high[center + 1:center + right + 1]))
        if left_ok and right_ok:
            confirm_bar = center + right
            prices[confirm_bar] = v
            origins[confirm_bar] = center
    return prices, origins


def _confirmed_pivot_low(low: np.ndarray, left: int, right: int) -> tuple[np.ndarray, np.ndarray]:
    n = len(low)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(left, n - right):
        v = low[center]
        if np.isnan(v):
            continue
        left_ok = bool(np.all(v < low[center - left:center]))
        right_ok = bool(np.all(v < low[center + 1:center + right + 1]))
        if left_ok and right_ok:
            confirm_bar = center + right
            prices[confirm_bar] = v
            origins[confirm_bar] = center
    return prices, origins


def _compute_timeframe(high: np.ndarray, low: np.ndarray, close: np.ndarray, *, swing_left: int, swing_right: int, min_pivot_gap: int, backfill_history: bool = True) -> dict[str, np.ndarray]:
    n = len(close)
    ph_prices, ph_origins = _confirmed_pivot_high(high, swing_left, swing_right)
    pl_prices, pl_origins = _confirmed_pivot_low(low, swing_left, swing_right)

    trend = np.zeros(n, dtype=int)
    line_value = np.full(n, np.nan, dtype=float)
    line_slope = np.full(n, np.nan, dtype=float)
    line_side = np.zeros(n, dtype=int)  # +1 support, -1 resistance, 0 none
    anchor_origin = np.full(n, -1, dtype=int)
    anchor_price = np.full(n, np.nan, dtype=float)
    active_pivot_origin = np.full(n, -1, dtype=int)
    active_pivot_price = np.full(n, np.nan, dtype=float)
    line_is_provisional = np.zeros(n, dtype=int)
    wick_bull = np.zeros(n, dtype=int)
    wick_bear = np.zeros(n, dtype=int)
    breakout_bull = np.zeros(n, dtype=int)
    breakout_bear = np.zeros(n, dtype=int)
    hh = np.zeros(n, dtype=int)
    ll = np.zeros(n, dtype=int)

    current_trend = 0
    prev_high_price = np.nan
    prev_high_origin = -1
    prev_low_price = np.nan
    prev_low_origin = -1

    active = False
    tl_x1 = -1
    tl_y1 = np.nan
    tl_x2 = -1
    tl_y2 = np.nan
    tl_cur_slope = 0.0
    tl_cp_idx = -1
    tl_cp_price = np.nan
    tl_pivot_idx = -1
    tl_pivot_price = np.nan
    tl_side = 0
    tl_slope_set = False

    segments: list[dict[str, object]] = []
    next_segment_id = 1
    active_segment_id = 0
    active_segment_start = -1

    last_fixnan_high = np.nan
    last_fixnan_low = np.nan

    def _fill_line_meta(start: int, end: int) -> None:
        provisional = 0 if tl_slope_set else 1
        for b in range(max(0, start), end + 1):
            line_side[b] = tl_side
            anchor_origin[b] = tl_x1
            anchor_price[b] = tl_y1
            active_pivot_origin[b] = tl_pivot_idx
            active_pivot_price[b] = tl_pivot_price
            line_is_provisional[b] = provisional

    def _capture_visible_state() -> tuple[float, float, int, int, float, int, float, int]:
        return (
            float(tl_y2),
            float(tl_cur_slope),
            int(tl_side),
            int(tl_x1),
            float(tl_y1),
            int(tl_pivot_idx),
            float(tl_pivot_price),
            0 if tl_slope_set else 1,
        )

    def _start_segment(start_bar: int) -> None:
        nonlocal next_segment_id, active_segment_id, active_segment_start
        active_segment_id = next_segment_id
        next_segment_id += 1
        active_segment_start = start_bar

    def _end_segment(end_bar: int, reason: str) -> None:
        nonlocal active_segment_id, active_segment_start
        if active_segment_id == 0 or active_segment_start < 0 or end_bar < active_segment_start:
            active_segment_id = 0
            active_segment_start = -1
            return
        start_value = float(tl_y1 + tl_cur_slope * (active_segment_start - tl_x1))
        end_value = float(tl_y1 + tl_cur_slope * (end_bar - tl_x1))
        segments.append(
            {
                "segment_id": int(active_segment_id),
                "start_bar": int(active_segment_start),
                "end_bar": int(end_bar),
                "bars_visible": int(end_bar - active_segment_start + 1),
                "end_reason": reason,
                "side": int(tl_side),
                "side_label": "support" if tl_side == 1 else "resistance" if tl_side == -1 else "none",
                "is_provisional": int(0 if tl_slope_set else 1),
                "anchor_origin": int(tl_x1),
                "anchor_price": float(tl_y1),
                "pivot_origin": int(tl_pivot_idx),
                "pivot_price": float(tl_pivot_price),
                "slope": float(tl_cur_slope),
                "start_value": start_value,
                "end_value": end_value,
            }
        )
        active_segment_id = 0
        active_segment_start = -1

    for bar in range(n):
        visible_state: tuple[float, float, int, int, float, int, float, int] | None = None
        if active:
            if tl_x1 >= 0 and (bar - tl_x1) > 5000:
                active = False
            else:
                tl_y2 = tl_y2 + tl_cur_slope
                tl_x2 = bar
                visible_state = _capture_visible_state()

        new_ph = not np.isnan(ph_prices[bar])
        new_pl = not np.isnan(pl_prices[bar])

        cur_fixnan_high = float(ph_prices[bar]) if new_ph else last_fixnan_high
        cur_fixnan_low = float(pl_prices[bar]) if new_pl else last_fixnan_low

        ch_h = (
            not np.isnan(cur_fixnan_high)
            and not np.isnan(last_fixnan_high)
            and cur_fixnan_high != last_fixnan_high
        )
        ch_l = (
            not np.isnan(cur_fixnan_low)
            and not np.isnan(last_fixnan_low)
            and cur_fixnan_low != last_fixnan_low
        )
        chH = ch_h and not ch_l
        chL = ch_l and not ch_h

        if new_ph:
            last_fixnan_high = float(ph_prices[bar])
        if new_pl:
            last_fixnan_low = float(pl_prices[bar])

        if chH and new_ph:
            pivot_price = float(ph_prices[bar])
            pivot_origin = int(ph_origins[bar])
            pivot_close = float(close[pivot_origin]) if 0 <= pivot_origin < n else np.nan

            if current_trend < 1:
                is_hh = (
                    not np.isnan(prev_high_price)
                    and pivot_price > prev_high_price
                    and prev_high_origin >= 0
                    and pivot_origin - prev_high_origin > min_pivot_gap
                    and prev_low_origin >= 0
                    and bar - prev_low_origin < 5000
                )
                if is_hh:
                    if active_segment_id:
                        _end_segment(bar - 1, "trend_switch")
                    hh[bar] = 1
                    current_trend = 1

                    tl_x1 = prev_low_origin
                    tl_y1 = float(prev_low_price)
                    tl_x2 = bar
                    tl_y2 = float(prev_low_price)
                    tl_cur_slope = 0.0
                    tl_cp_idx = prev_low_origin
                    tl_cp_price = float(prev_low_price)
                    tl_pivot_idx = -1
                    tl_pivot_price = np.nan
                    tl_side = 1
                    active = True
                    tl_slope_set = False

                    if backfill_history:
                        for b in range(max(0, tl_x1), bar + 1):
                            line_value[b] = tl_y1
                            line_slope[b] = 0.0
                            trend[b] = current_trend
                        _fill_line_meta(tl_x1, bar)
                    _start_segment(bar)
                    visible_state = _capture_visible_state()
                elif active and not np.isnan(pivot_price):
                    slope = (pivot_price - tl_cp_price) / max(pivot_origin - tl_cp_idx, 1)
                    cur_proj = tl_y1 + tl_cur_slope * (pivot_origin - tl_x1)

                    if pivot_price < cur_proj and (pivot_price > tl_y2 or not tl_slope_set):
                        if tl_x2 != tl_x1:
                            price_at_pivot = tl_y1 + (tl_y2 - tl_y1) / (tl_x2 - tl_x1) * (pivot_origin - tl_x1)
                        else:
                            price_at_pivot = tl_y1

                        if not np.isnan(pivot_close) and pivot_close < price_at_pivot:
                            if tl_slope_set:
                                wick_bear[bar] = 1
                            if active_segment_id:
                                _end_segment(bar - 1, "pivot_update")

                            tl_y2 = pivot_price + slope * (bar - pivot_origin)
                            tl_x2 = bar
                            tl_cur_slope = float(slope)
                            tl_pivot_idx = pivot_origin
                            tl_pivot_price = pivot_price
                            tl_side = 1
                            tl_slope_set = True

                            if backfill_history:
                                for b in range(max(0, tl_x1), bar + 1):
                                    line_value[b] = tl_y1 + tl_cur_slope * (b - tl_x1)
                                    line_slope[b] = tl_cur_slope
                                    trend[b] = current_trend
                                _fill_line_meta(tl_x1, bar)
                            _start_segment(bar)
                            visible_state = _capture_visible_state()
                        else:
                            breakout_bull[bar] = 1
                            if active_segment_id:
                                _end_segment(bar, "breakout")
                            active = False

            prev_high_price = pivot_price
            prev_high_origin = pivot_origin
        else:
            if current_trend < 1 and active and not np.isnan(tl_y2):
                if close[bar] > tl_y2:
                    breakout_bull[bar] = 1
                    if active_segment_id:
                        _end_segment(bar, "breakout")
                    active = False

        if chL and new_pl:
            pivot_price = float(pl_prices[bar])
            pivot_origin = int(pl_origins[bar])
            pivot_close = float(close[pivot_origin]) if 0 <= pivot_origin < n else np.nan

            if current_trend > -1:
                is_ll = (
                    not np.isnan(prev_low_price)
                    and pivot_price < prev_low_price
                    and prev_low_origin >= 0
                    and pivot_origin - prev_low_origin > min_pivot_gap
                    and prev_high_origin >= 0
                    and bar - prev_high_origin < 5000
                )
                if is_ll:
                    if active_segment_id:
                        _end_segment(bar - 1, "trend_switch")
                    ll[bar] = 1
                    current_trend = -1

                    tl_x1 = prev_high_origin
                    tl_y1 = float(prev_high_price)
                    tl_x2 = bar
                    tl_y2 = float(prev_high_price)
                    tl_cur_slope = 0.0
                    tl_cp_idx = prev_high_origin
                    tl_cp_price = float(prev_high_price)
                    tl_pivot_idx = -1
                    tl_pivot_price = np.nan
                    tl_side = -1
                    active = True
                    tl_slope_set = False

                    if backfill_history:
                        for b in range(max(0, tl_x1), bar + 1):
                            line_value[b] = tl_y1
                            line_slope[b] = 0.0
                            trend[b] = current_trend
                        _fill_line_meta(tl_x1, bar)
                    _start_segment(bar)
                    visible_state = _capture_visible_state()
                elif active and not np.isnan(pivot_price):
                    slope = (pivot_price - tl_cp_price) / max(pivot_origin - tl_cp_idx, 1)
                    cur_proj = tl_y1 + tl_cur_slope * (pivot_origin - tl_x1)

                    if pivot_price > cur_proj and (pivot_price < tl_y2 or not tl_slope_set):
                        if tl_x2 != tl_x1:
                            price_at_pivot = tl_y1 + (tl_y2 - tl_y1) / (tl_x2 - tl_x1) * (pivot_origin - tl_x1)
                        else:
                            price_at_pivot = tl_y1

                        if not np.isnan(pivot_close) and pivot_close > price_at_pivot:
                            if tl_slope_set:
                                wick_bull[bar] = 1
                            if active_segment_id:
                                _end_segment(bar - 1, "pivot_update")

                            tl_y2 = pivot_price + slope * (bar - pivot_origin)
                            tl_x2 = bar
                            tl_cur_slope = float(slope)
                            tl_pivot_idx = pivot_origin
                            tl_pivot_price = pivot_price
                            tl_side = -1
                            tl_slope_set = True

                            if backfill_history:
                                for b in range(max(0, tl_x1), bar + 1):
                                    line_value[b] = tl_y1 + tl_cur_slope * (b - tl_x1)
                                    line_slope[b] = tl_cur_slope
                                    trend[b] = current_trend
                                _fill_line_meta(tl_x1, bar)
                            _start_segment(bar)
                            visible_state = _capture_visible_state()
                        else:
                            breakout_bear[bar] = 1
                            if active_segment_id:
                                _end_segment(bar, "breakout")
                            active = False

            prev_low_price = pivot_price
            prev_low_origin = pivot_origin
        else:
            if current_trend > -1 and active and not np.isnan(tl_y2):
                if close[bar] < tl_y2:
                    breakout_bear[bar] = 1
                    if active_segment_id:
                        _end_segment(bar, "breakout")
                    active = False

        trend[bar] = current_trend
        if active:
            visible_state = _capture_visible_state()

        if visible_state is not None:
            (
                line_value[bar],
                line_slope[bar],
                line_side[bar],
                anchor_origin[bar],
                anchor_price[bar],
                active_pivot_origin[bar],
                active_pivot_price[bar],
                line_is_provisional[bar],
            ) = visible_state
        else:
            line_value[bar] = np.nan
            line_slope[bar] = np.nan
            line_side[bar] = 0
            anchor_origin[bar] = -1
            anchor_price[bar] = np.nan
            active_pivot_origin[bar] = -1
            active_pivot_price[bar] = np.nan
            line_is_provisional[bar] = 0

    if active_segment_id:
        _end_segment(n - 1, "window_end")

    return {
        "trend": trend,
        "line_value": line_value,
        "line_slope": line_slope,
        "line_side": line_side,
        "anchor_origin": anchor_origin,
        "anchor_price": anchor_price,
        "active_pivot_origin": active_pivot_origin,
        "active_pivot_price": active_pivot_price,
        "line_is_provisional": line_is_provisional,
        "wick_bull": wick_bull,
        "wick_bear": wick_bear,
        "breakout_bull": breakout_bull,
        "breakout_bear": breakout_bear,
        "hh": hh,
        "ll": ll,
        "pivot_high_price": ph_prices,
        "pivot_high_origin": ph_origins,
        "pivot_low_price": pl_prices,
        "pivot_low_origin": pl_origins,
        "segments": segments,
    }


def _apply_timeframe(df: pd.DataFrame, prefix: str, result: dict[str, np.ndarray]) -> pd.DataFrame:
    out = df.copy()
    out[f"{prefix}_trend"] = result["trend"]
    out[f"{prefix}_line_value"] = result["line_value"]
    out[f"{prefix}_line_slope"] = result["line_slope"]
    out[f"{prefix}_line_side"] = result["line_side"]
    out[f"{prefix}_anchor_origin"] = result["anchor_origin"]
    out[f"{prefix}_anchor_price"] = result["anchor_price"]
    out[f"{prefix}_active_pivot_origin"] = result["active_pivot_origin"]
    out[f"{prefix}_active_pivot_price"] = result["active_pivot_price"]
    out[f"{prefix}_line_is_provisional"] = result["line_is_provisional"]
    out[f"{prefix}_wick_bull"] = result["wick_bull"]
    out[f"{prefix}_wick_bear"] = result["wick_bear"]
    out[f"{prefix}_breakout_bull"] = result["breakout_bull"]
    out[f"{prefix}_breakout_bear"] = result["breakout_bear"]
    out[f"{prefix}_hh"] = result["hh"]
    out[f"{prefix}_ll"] = result["ll"]
    out[f"{prefix}_pivot_high_price"] = result["pivot_high_price"]
    out[f"{prefix}_pivot_high_origin"] = result["pivot_high_origin"]
    out[f"{prefix}_pivot_low_price"] = result["pivot_low_price"]
    out[f"{prefix}_pivot_low_origin"] = result["pivot_low_origin"]
    return out


def _segment_records_to_frame(out: pd.DataFrame, prefix: str, records: list[dict[str, object]]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(
            columns=[
                "timeframe",
                "segment_id",
                "start_bar",
                "end_bar",
                "bars_visible",
                "end_reason",
                "side",
                "side_label",
                "is_provisional",
                "anchor_origin",
                "anchor_price",
                "pivot_origin",
                "pivot_price",
                "slope",
                "start_value",
                "end_value",
                "start_timestamp",
                "end_timestamp",
                "anchor_timestamp",
                "pivot_timestamp",
                "symbol",
            ]
        )
    seg = pd.DataFrame(records).copy()
    seg["timeframe"] = prefix
    seg["start_timestamp"] = out.loc[seg["start_bar"].astype(int), "timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").to_numpy()
    seg["end_timestamp"] = out.loc[seg["end_bar"].astype(int), "timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").to_numpy()
    seg["anchor_timestamp"] = out.loc[seg["anchor_origin"].astype(int), "timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").to_numpy()
    seg["pivot_timestamp"] = ""
    has_pivot = seg["pivot_origin"].astype(int) >= 0
    if has_pivot.any():
        pivot_times = out.loc[seg.loc[has_pivot, "pivot_origin"].astype(int), "timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ").to_numpy()
        seg.loc[has_pivot, "pivot_timestamp"] = pivot_times
    if "symbol" in out.columns:
        seg["symbol"] = out["symbol"].iloc[0]
    else:
        seg["symbol"] = ""
    return seg


def _compute_single_symbol_with_segments(df: pd.DataFrame, config: TrendlineBreakoutNavigatorConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out = out.sort_values("timestamp").reset_index(drop=True)

    high = out["high"].astype(float).to_numpy()
    low = out["low"].astype(float).to_numpy()
    close = out["close"].astype(float).to_numpy()

    enabled_trends: list[np.ndarray] = []
    wick_bull_all = np.zeros(len(out), dtype=int)
    wick_bear_all = np.zeros(len(out), dtype=int)
    breakout_bull_all = np.zeros(len(out), dtype=int)
    breakout_bear_all = np.zeros(len(out), dtype=int)
    hh_all = np.zeros(len(out), dtype=int)
    ll_all = np.zeros(len(out), dtype=int)
    segment_tables: list[pd.DataFrame] = []

    specs = [
        ("tbn_long", config.enable_long, config.swing_long),
        ("tbn_medium", config.enable_medium, config.swing_medium),
        ("tbn_short", config.enable_short, config.swing_short),
    ]

    for prefix, enabled, swing_left in specs:
        if enabled:
            result = _compute_timeframe(
                high,
                low,
                close,
                swing_left=swing_left,
                swing_right=config.swing_right,
                min_pivot_gap=config.min_pivot_gap,
                backfill_history=config.backfill_history,
            )
            out = _apply_timeframe(out, prefix, result)
            segment_tables.append(_segment_records_to_frame(out, prefix, result["segments"]))
            enabled_trends.append(result["trend"])
            wick_bull_all = np.maximum(wick_bull_all, result["wick_bull"])
            wick_bear_all = np.maximum(wick_bear_all, result["wick_bear"])
            breakout_bull_all = np.maximum(breakout_bull_all, result["breakout_bull"])
            breakout_bear_all = np.maximum(breakout_bear_all, result["breakout_bear"])
            hh_all = np.maximum(hh_all, result["hh"])
            ll_all = np.maximum(ll_all, result["ll"])
        else:
            out[f"{prefix}_trend"] = 0
            out[f"{prefix}_line_value"] = np.nan
            out[f"{prefix}_line_slope"] = np.nan
            out[f"{prefix}_line_side"] = 0
            out[f"{prefix}_anchor_origin"] = -1
            out[f"{prefix}_anchor_price"] = np.nan
            out[f"{prefix}_active_pivot_origin"] = -1
            out[f"{prefix}_active_pivot_price"] = np.nan
            out[f"{prefix}_line_is_provisional"] = 0
            out[f"{prefix}_wick_bull"] = 0
            out[f"{prefix}_wick_bear"] = 0
            out[f"{prefix}_breakout_bull"] = 0
            out[f"{prefix}_breakout_bear"] = 0
            out[f"{prefix}_hh"] = 0
            out[f"{prefix}_ll"] = 0
            out[f"{prefix}_pivot_high_price"] = np.nan
            out[f"{prefix}_pivot_high_origin"] = -1
            out[f"{prefix}_pivot_low_price"] = np.nan
            out[f"{prefix}_pivot_low_origin"] = -1

    out["tbn_wick_bull"] = wick_bull_all
    out["tbn_wick_bear"] = wick_bear_all
    out["tbn_breakout_bull"] = breakout_bull_all
    out["tbn_breakout_bear"] = breakout_bear_all
    out["tbn_hh"] = hh_all
    out["tbn_ll"] = ll_all
    if enabled_trends:
        composite = np.sum(np.vstack(enabled_trends), axis=0)
    else:
        composite = np.zeros(len(out), dtype=int)
    out["tbn_composite_trend"] = composite.astype(int)
    out["tbn_signal"] = np.where(composite > 0, 1, np.where(composite < 0, -1, 0)).astype(int)

    segments = pd.concat(segment_tables, ignore_index=True) if segment_tables else pd.DataFrame()
    return out, segments


def _compute_single_symbol(df: pd.DataFrame, config: TrendlineBreakoutNavigatorConfig) -> pd.DataFrame:
    out, _ = _compute_single_symbol_with_segments(df, config)
    return out


def extract_trendline_breakout_segments(
    bars: pd.DataFrame,
    *,
    config: TrendlineBreakoutNavigatorConfig = TrendlineBreakoutNavigatorConfig(),
) -> pd.DataFrame:
    _validate_df(bars)
    _validate_config(config)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        segment_parts: list[pd.DataFrame] = []
        for _, g in df.groupby("symbol", sort=True):
            _, seg = _compute_single_symbol_with_segments(g.reset_index(drop=True), config)
            segment_parts.append(seg)
        segments = pd.concat(segment_parts, ignore_index=True) if segment_parts else pd.DataFrame()
    else:
        _, segments = _compute_single_symbol_with_segments(df, config)

    if not segments.empty:
        for col in ["start_timestamp", "end_timestamp", "anchor_timestamp", "pivot_timestamp"]:
            parsed = pd.to_datetime(segments[col], utc=True, errors="coerce")
            segments[col] = parsed.dt.strftime("%Y-%m-%dT%H:%M:%SZ").fillna("")
    return segments


def compute_trendline_breakout_navigator(
    bars: pd.DataFrame,
    *,
    config: TrendlineBreakoutNavigatorConfig = TrendlineBreakoutNavigatorConfig(),
) -> pd.DataFrame:
    _validate_df(bars)
    _validate_config(config)

    df = bars.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    if "symbol" in df.columns:
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
        parts: list[pd.DataFrame] = []
        segment_parts: list[pd.DataFrame] = []
        for _, g in df.groupby("symbol", sort=True):
            part, seg = _compute_single_symbol_with_segments(g.reset_index(drop=True), config)
            parts.append(part)
            segment_parts.append(seg)
        out = pd.concat(parts, ignore_index=True)
        segments = pd.concat(segment_parts, ignore_index=True) if segment_parts else pd.DataFrame()
    else:
        out, segments = _compute_single_symbol_with_segments(df, config)

    out.attrs["tbn_segments"] = segments.copy()
    out["timestamp"] = out["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


__all__ = [
    "TrendlineBreakoutNavigatorConfig",
    "compute_trendline_breakout_navigator",
    "extract_trendline_breakout_segments",
]
