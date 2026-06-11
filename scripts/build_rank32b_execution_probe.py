#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import math
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
EXT_SCRIPT = ROOT / "scripts" / "build_rank32b_extended_history_probe.py"
PERP_SCRIPT = ROOT / "scripts" / "build_rank32b_perp_funding_probe.py"

PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
DEFAULT_DAYS = 1825
HORIZONS_15M = [1, 2, 4, 8, 12, 16]
FIXED_EXIT_HOLDS_15M = [4, 8, 12, 16]
TP_ATR_MULTS = [0.75, 1.00, 1.25]
TAKER_FEE_BPS = 6.0
MAKER_FEE_BPS = 0.0
ENTRY_TTL_5M_BARS = 3
ENTRY_OFFSETS_BPS = [2.0, 4.0]
TIMEOUT_HOLD_15M = 16
MARKER_ID = "rank32b-execution-research-1825d"
EXIT_ORDER = [
    "fixed_hold_4_taker",
    "fixed_hold_8_taker",
    "fixed_hold_12_taker",
    "fixed_hold_16_taker",
    "tp_0.75atr_limit_timeout16",
    "tp_1.00atr_limit_timeout16",
    "tp_1.25atr_limit_timeout16",
]
EXEC_ORDER = [
    "baseline_taker_fixed8",
    "maker_entry_2bps_ttl15m_fixed8",
    "maker_entry_4bps_ttl15m_fixed8",
    "baseline_taker_tp1atr_timeout16",
    "maker_entry_2bps_ttl15m_tp1atr_timeout16",
]
SIDE_ORDER = ["long_short", "long_only", "short_only"]
SIDE_LABELS = {
    "long_short": "多空都做",
    "long_only": "只做多",
    "short_only": "只做空",
}
EXIT_LABELS = {
    "fixed_hold_4_taker": "固定持有 4x15m（taker exit）",
    "fixed_hold_8_taker": "固定持有 8x15m（当前 baseline）",
    "fixed_hold_12_taker": "固定持有 12x15m（taker exit）",
    "fixed_hold_16_taker": "固定持有 16x15m（taker exit）",
    "tp_0.75atr_limit_timeout16": "0.75 ATR 限价止盈，超时 16x15m taker",
    "tp_1.00atr_limit_timeout16": "1.00 ATR 限价止盈，超时 16x15m taker",
    "tp_1.25atr_limit_timeout16": "1.25 ATR 限价止盈，超时 16x15m taker",
}
EXEC_LABELS = {
    "baseline_taker_fixed8": "taker entry + 固定 8x15m taker exit",
    "maker_entry_2bps_ttl15m_fixed8": "maker-first 入场 2bps / 15m TTL + 固定 8x15m taker exit",
    "maker_entry_4bps_ttl15m_fixed8": "maker-first 入场 4bps / 15m TTL + 固定 8x15m taker exit",
    "baseline_taker_tp1atr_timeout16": "taker entry + 1.0 ATR 限价止盈 / 16x15m timeout",
    "maker_entry_2bps_ttl15m_tp1atr_timeout16": "maker-first 入场 2bps / 15m TTL + 1.0 ATR 限价止盈 / 16x15m timeout",
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base_mod = load_module(BASE_SCRIPT, "rank32_base_mod_for_exec_probe")
ext_mod = load_module(EXT_SCRIPT, "rank32b_extended_mod_for_exec_probe")
perp_mod = load_module(PERP_SCRIPT, "rank32b_perp_mod_for_exec_probe")


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


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def load_cached_csv(path: Path, time_cols: list[str] | None = None) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, on_bad_lines="skip")
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()
    for col in time_cols or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce", format="mixed")
    if time_cols:
        present = [col for col in time_cols if col in df.columns]
        if present:
            df = df.dropna(subset=present)
    return df.reset_index(drop=True)


def fetch_perp_5m_klines(symbol: str, days: int) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    limit = 1000
    base_sleep = 0.08
    max_retries = 8

    while current < end_ms:
        params = {
            "symbol": symbol,
            "interval": "5m",
            "startTime": current,
            "endTime": end_ms,
            "limit": limit,
        }
        retry = 0
        while True:
            resp = requests.get("https://fapi.binance.com/fapi/v1/klines", params=params, timeout=30)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else min(30.0, (2 ** retry) * 0.6)
                time.sleep(wait_s)
                retry += 1
                if retry > max_retries:
                    resp.raise_for_status()
                continue
            if resp.status_code >= 500:
                time.sleep(min(20.0, (2 ** retry) * 0.5))
                retry += 1
                if retry > max_retries:
                    resp.raise_for_status()
                continue
            resp.raise_for_status()
            batch = resp.json()
            break

        if not batch:
            break
        rows.extend(batch)
        current = int(batch[-1][6]) + 1
        if len(batch) < limit:
            break
        time.sleep(base_sleep)

    if not rows:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    return out.dropna().sort_values("timestamp").reset_index(drop=True)


def load_or_fetch_perp_5m(symbol: str, days: int, refresh: bool = False) -> pd.DataFrame:
    cache_dir = ensure_dir(ART_DIR / "exec_cache")
    path = cache_dir / f"{symbol}__{days}d__5m__perp.csv"
    if path.exists() and not refresh:
        return load_cached_csv(path, ["timestamp"])
    df = fetch_perp_5m_klines(symbol, days=days)
    df.to_csv(path, index=False)
    return df


def build_signal_trades(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    zero_cost_trades, _, _ = base_mod.build_trades(frame, asset, PRIMARY_VARIANT, 0.0)
    if zero_cost_trades.empty:
        return pd.DataFrame(
            columns=[
                "asset",
                "signal_idx",
                "entry_idx",
                "base_exit_idx",
                "direction",
                "direction_sign",
                "event_ts",
                "entry_ts",
                "entry_price_15m",
                "atr14_entry",
            ]
        )
    rows: list[dict[str, object]] = []
    for _, row in zero_cost_trades.iterrows():
        signal_idx = int(row["signal_idx"])
        entry_idx = signal_idx + 1
        if entry_idx >= len(frame):
            continue
        entry_ts = pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True)
        base_exit_idx = min(len(frame) - 1, entry_idx + base_mod.HOLD_BARS - 1)
        direction = str(row["direction"])
        rows.append(
            {
                "asset": asset,
                "signal_idx": signal_idx,
                "entry_idx": entry_idx,
                "base_exit_idx": base_exit_idx,
                "direction": direction,
                "direction_sign": 1 if direction == "long" else -1,
                "event_ts": pd.to_datetime(frame.iloc[signal_idx]["timestamp"], utc=True),
                "entry_ts": entry_ts,
                "entry_price_15m": float(frame.iloc[entry_idx]["open"]),
                "atr14_entry": float(frame.iloc[entry_idx]["atr14"]) if not pd.isna(frame.iloc[entry_idx]["atr14"]) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_path_rows(trades: pd.DataFrame, frame_map: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, trade in trades.iterrows():
        asset = str(trade["asset"])
        frame = frame_map[asset]
        entry_idx = int(trade["entry_idx"])
        if entry_idx >= len(frame):
            continue
        direction_sign = int(trade["direction_sign"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not math.isfinite(entry_px) or entry_px <= 0:
            continue
        horizon_end = min(len(frame) - 1, entry_idx + max(HORIZONS_15M) - 1)
        window = frame.iloc[entry_idx : horizon_end + 1].copy().reset_index(drop=True)
        if window.empty:
            continue
        if direction_sign > 0:
            favorable_path = window["high"] / entry_px - 1.0
            adverse_path = window["low"] / entry_px - 1.0
        else:
            favorable_path = entry_px / window["low"] - 1.0
            adverse_path = entry_px / window["high"] - 1.0
        row: dict[str, object] = {
            "asset": asset,
            "direction": str(trade["direction"]),
            "entry_ts": pd.to_datetime(trade["entry_ts"], utc=True),
            "entry_price_15m": entry_px,
            "mfe_16bars": float(favorable_path.max()),
            "mae_16bars": float(max(0.0, -adverse_path.min())),
            "time_to_mfe_bars": int(favorable_path.to_numpy().argmax()) + 1,
            "time_to_mae_bars": int(adverse_path.to_numpy().argmin()) + 1,
        }
        for horizon in HORIZONS_15M:
            probe_idx = min(len(frame) - 1, entry_idx + horizon - 1)
            close_px = float(frame.iloc[probe_idx]["close"])
            ret = (close_px / entry_px - 1.0) * direction_sign
            row[f"ret_{horizon}bars"] = float(ret)
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_path(path_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    horizon_rows: list[dict[str, object]] = []
    stat_rows: list[dict[str, object]] = []
    side_masks = {
        "long_short": pd.Series(True, index=path_rows.index),
        "long_only": path_rows["direction"].eq("long"),
        "short_only": path_rows["direction"].eq("short"),
    }
    for side in SIDE_ORDER:
        scoped = path_rows[side_masks[side]].copy()
        if scoped.empty:
            continue
        stat_rows.append(
            {
                "side": side,
                "trades": int(len(scoped)),
                "avg_mfe_16bars": float(scoped["mfe_16bars"].mean()),
                "avg_mae_16bars": float(scoped["mae_16bars"].mean()),
                "median_time_to_mfe_bars": float(scoped["time_to_mfe_bars"].median()),
                "median_time_to_mae_bars": float(scoped["time_to_mae_bars"].median()),
            }
        )
        for horizon in HORIZONS_15M:
            col = f"ret_{horizon}bars"
            horizon_rows.append(
                {
                    "side": side,
                    "horizon_15m_bars": horizon,
                    "avg_price_ret": float(scoped[col].mean()),
                    "median_price_ret": float(scoped[col].median()),
                    "win_rate": float((scoped[col] > 0).mean()),
                }
            )
    return pd.DataFrame(horizon_rows), pd.DataFrame(stat_rows)


def attach_asset_maps(df: pd.DataFrame, asset: str) -> pd.DataFrame:
    out = df.copy()
    out["asset"] = asset
    return out


def search_left(ts_array: np.ndarray, ts: np.datetime64) -> int:
    return int(np.searchsorted(ts_array, ts, side="left"))


def search_right(ts_array: np.ndarray, ts: np.datetime64) -> int:
    return int(np.searchsorted(ts_array, ts, side="right"))


def get_start_bar(sub_df: pd.DataFrame, ts_array: np.ndarray, start_ts: pd.Timestamp) -> tuple[int, pd.Series] | tuple[None, None]:
    idx = search_left(ts_array, start_ts.to_datetime64())
    if idx >= len(sub_df):
        return None, None
    bar = sub_df.iloc[idx]
    return idx, bar


def apply_fees(gross_ret: float, entry_fee_bps: float, exit_fee_bps: float) -> float:
    entry_fee = float(entry_fee_bps) / 10000.0
    exit_fee = float(exit_fee_bps) / 10000.0
    return float((1.0 + gross_ret) * (1.0 - entry_fee) * (1.0 - exit_fee) - 1.0)


def gross_return(entry_px: float, exit_px: float, direction_sign: int) -> float:
    return float((exit_px / entry_px - 1.0) * direction_sign)


def simulate_entry(
    sub_df: pd.DataFrame,
    ts_array: np.ndarray,
    entry_ts: pd.Timestamp,
    direction_sign: int,
    entry_style: str,
    entry_offset_bps: float = 0.0,
    ttl_bars: int = ENTRY_TTL_5M_BARS,
) -> dict[str, object] | None:
    start_idx, start_bar = get_start_bar(sub_df, ts_array, entry_ts)
    if start_bar is None:
        return None
    if entry_style == "taker":
        return {
            "fill_idx": int(start_idx),
            "fill_ts": pd.to_datetime(start_bar["timestamp"], utc=True),
            "fill_px": float(start_bar["open"]),
            "entry_fee_bps": TAKER_FEE_BPS,
            "entry_maker": 0,
            "entry_ttl_bars": 0,
            "entry_offset_bps": 0.0,
        }
    limit_px = float(start_bar["open"]) * (1.0 - direction_sign * (float(entry_offset_bps) / 10000.0))
    end_idx = min(len(sub_df), start_idx + int(ttl_bars))
    for idx in range(start_idx, end_idx):
        bar = sub_df.iloc[idx]
        if direction_sign > 0 and float(bar["low"]) <= limit_px:
            return {
                "fill_idx": int(idx),
                "fill_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "fill_px": limit_px,
                "entry_fee_bps": MAKER_FEE_BPS,
                "entry_maker": 1,
                "entry_ttl_bars": int(ttl_bars),
                "entry_offset_bps": float(entry_offset_bps),
            }
        if direction_sign < 0 and float(bar["high"]) >= limit_px:
            return {
                "fill_idx": int(idx),
                "fill_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "fill_px": limit_px,
                "entry_fee_bps": MAKER_FEE_BPS,
                "entry_maker": 1,
                "entry_ttl_bars": int(ttl_bars),
                "entry_offset_bps": float(entry_offset_bps),
            }
    fallback_idx = end_idx - 1
    if fallback_idx < start_idx:
        return None
    fallback_bar = sub_df.iloc[fallback_idx]
    return {
        "fill_idx": int(fallback_idx),
        "fill_ts": pd.to_datetime(fallback_bar["timestamp"], utc=True),
        "fill_px": float(fallback_bar["close"]),
        "entry_fee_bps": TAKER_FEE_BPS,
        "entry_maker": 0,
        "entry_ttl_bars": int(ttl_bars),
        "entry_offset_bps": float(entry_offset_bps),
    }


def simulate_fixed_exit(sub_df: pd.DataFrame, fill_idx: int, hold_15m_bars: int) -> dict[str, object] | None:
    hold_5m_bars = int(hold_15m_bars * 3)
    exit_idx = min(len(sub_df) - 1, fill_idx + hold_5m_bars - 1)
    if exit_idx < fill_idx:
        return None
    bar = sub_df.iloc[exit_idx]
    return {
        "exit_idx": int(exit_idx),
        "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
        "exit_px": float(bar["close"]),
        "exit_fee_bps": TAKER_FEE_BPS,
        "exit_maker": 0,
        "target_hit": 0,
        "hold_minutes": int((exit_idx - fill_idx + 1) * 5),
    }


def simulate_tp_limit_exit(
    sub_df: pd.DataFrame,
    fill_idx: int,
    fill_px: float,
    direction_sign: int,
    atr_value: float,
    tp_mult: float,
    timeout_15m_bars: int = TIMEOUT_HOLD_15M,
) -> dict[str, object] | None:
    if not math.isfinite(atr_value) or atr_value <= 0:
        return None
    target_px = float(fill_px + direction_sign * tp_mult * atr_value)
    timeout_5m_bars = int(timeout_15m_bars * 3)
    end_idx = min(len(sub_df) - 1, fill_idx + timeout_5m_bars - 1)
    for idx in range(fill_idx, end_idx + 1):
        bar = sub_df.iloc[idx]
        if direction_sign > 0 and float(bar["high"]) >= target_px:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": target_px,
                "exit_fee_bps": MAKER_FEE_BPS,
                "exit_maker": 1,
                "target_hit": 1,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
        if direction_sign < 0 and float(bar["low"]) <= target_px:
            return {
                "exit_idx": int(idx),
                "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
                "exit_px": target_px,
                "exit_fee_bps": MAKER_FEE_BPS,
                "exit_maker": 1,
                "target_hit": 1,
                "hold_minutes": int((idx - fill_idx + 1) * 5),
            }
    bar = sub_df.iloc[end_idx]
    return {
        "exit_idx": int(end_idx),
        "exit_ts": pd.to_datetime(bar["timestamp"], utc=True),
        "exit_px": float(bar["close"]),
        "exit_fee_bps": TAKER_FEE_BPS,
        "exit_maker": 0,
        "target_hit": 0,
        "hold_minutes": int((end_idx - fill_idx + 1) * 5),
    }


def run_exit_family(trades: pd.DataFrame, subbars_map: dict[str, pd.DataFrame], ts_map: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, trade in trades.iterrows():
        asset = str(trade["asset"])
        sub_df = subbars_map[asset]
        ts_array = ts_map[asset]
        direction_sign = int(trade["direction_sign"])
        base_entry = simulate_entry(sub_df, ts_array, pd.to_datetime(trade["entry_ts"], utc=True), direction_sign, entry_style="taker")
        if base_entry is None:
            continue
        for hold in FIXED_EXIT_HOLDS_15M:
            exit_res = simulate_fixed_exit(sub_df, int(base_entry["fill_idx"]), hold)
            if exit_res is None:
                continue
            gret = gross_return(float(base_entry["fill_px"]), float(exit_res["exit_px"]), direction_sign)
            rows.append(
                {
                    "asset": asset,
                    "direction": str(trade["direction"]),
                    "scenario": f"fixed_hold_{hold}_taker",
                    "entry_ts": pd.to_datetime(base_entry["fill_ts"], utc=True),
                    "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                    "entry_price": float(base_entry["fill_px"]),
                    "exit_price": float(exit_res["exit_px"]),
                    "gross_ret": gret,
                    "net_ret": apply_fees(gret, float(base_entry["entry_fee_bps"]), float(exit_res["exit_fee_bps"])),
                    "entry_maker": int(base_entry["entry_maker"]),
                    "exit_maker": int(exit_res["exit_maker"]),
                    "target_hit": int(exit_res["target_hit"]),
                    "hold_minutes": int(exit_res["hold_minutes"]),
                }
            )
        atr_value = float(trade["atr14_entry"]) if not pd.isna(trade["atr14_entry"]) else np.nan
        for mult in TP_ATR_MULTS:
            exit_res = simulate_tp_limit_exit(sub_df, int(base_entry["fill_idx"]), float(base_entry["fill_px"]), direction_sign, atr_value, mult)
            if exit_res is None:
                continue
            gret = gross_return(float(base_entry["fill_px"]), float(exit_res["exit_px"]), direction_sign)
            rows.append(
                {
                    "asset": asset,
                    "direction": str(trade["direction"]),
                    "scenario": f"tp_{mult:.2f}atr_limit_timeout16",
                    "entry_ts": pd.to_datetime(base_entry["fill_ts"], utc=True),
                    "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                    "entry_price": float(base_entry["fill_px"]),
                    "exit_price": float(exit_res["exit_px"]),
                    "gross_ret": gret,
                    "net_ret": apply_fees(gret, float(base_entry["entry_fee_bps"]), float(exit_res["exit_fee_bps"])),
                    "entry_maker": int(base_entry["entry_maker"]),
                    "exit_maker": int(exit_res["exit_maker"]),
                    "target_hit": int(exit_res["target_hit"]),
                    "hold_minutes": int(exit_res["hold_minutes"]),
                }
            )
    return pd.DataFrame(rows)


def run_execution_scenarios(trades: pd.DataFrame, subbars_map: dict[str, pd.DataFrame], ts_map: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, trade in trades.iterrows():
        asset = str(trade["asset"])
        sub_df = subbars_map[asset]
        ts_array = ts_map[asset]
        entry_ts = pd.to_datetime(trade["entry_ts"], utc=True)
        direction_sign = int(trade["direction_sign"])
        atr_value = float(trade["atr14_entry"]) if not pd.isna(trade["atr14_entry"]) else np.nan
        scenarios = [
            ("baseline_taker_fixed8", "taker", 0.0, "fixed", 8),
            ("maker_entry_2bps_ttl15m_fixed8", "maker", 2.0, "fixed", 8),
            ("maker_entry_4bps_ttl15m_fixed8", "maker", 4.0, "fixed", 8),
            ("baseline_taker_tp1atr_timeout16", "taker", 0.0, "tp", 1.0),
            ("maker_entry_2bps_ttl15m_tp1atr_timeout16", "maker", 2.0, "tp", 1.0),
        ]
        for scenario_name, entry_style, offset_bps, exit_style, param in scenarios:
            entry_res = simulate_entry(
                sub_df,
                ts_array,
                entry_ts,
                direction_sign,
                entry_style="taker" if entry_style == "taker" else "maker",
                entry_offset_bps=float(offset_bps),
                ttl_bars=ENTRY_TTL_5M_BARS,
            )
            if entry_res is None:
                continue
            if exit_style == "fixed":
                exit_res = simulate_fixed_exit(sub_df, int(entry_res["fill_idx"]), int(param))
            else:
                exit_res = simulate_tp_limit_exit(sub_df, int(entry_res["fill_idx"]), float(entry_res["fill_px"]), direction_sign, atr_value, float(param))
            if exit_res is None:
                continue
            gret = gross_return(float(entry_res["fill_px"]), float(exit_res["exit_px"]), direction_sign)
            rows.append(
                {
                    "asset": asset,
                    "direction": str(trade["direction"]),
                    "scenario": scenario_name,
                    "entry_ts": pd.to_datetime(entry_res["fill_ts"], utc=True),
                    "exit_ts": pd.to_datetime(exit_res["exit_ts"], utc=True),
                    "entry_price": float(entry_res["fill_px"]),
                    "exit_price": float(exit_res["exit_px"]),
                    "gross_ret": gret,
                    "net_ret": apply_fees(gret, float(entry_res["entry_fee_bps"]), float(exit_res["exit_fee_bps"])),
                    "entry_maker": int(entry_res["entry_maker"]),
                    "exit_maker": int(exit_res["exit_maker"]),
                    "target_hit": int(exit_res["target_hit"]),
                    "hold_minutes": int(exit_res["hold_minutes"]),
                    "entry_offset_bps": float(entry_res["entry_offset_bps"]),
                }
            )
    return pd.DataFrame(rows)


def summarize_scenarios(trades: pd.DataFrame, scenario_order: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    asset_rows: list[dict[str, object]] = []
    overall_rows: list[dict[str, object]] = []
    if trades.empty:
        return pd.DataFrame(), pd.DataFrame()
    for scenario in scenario_order:
        scoped = trades[trades["scenario"] == scenario].copy()
        if scoped.empty:
            continue
        per_asset_rows = []
        for asset in ASSETS.keys():
            part = scoped[scoped["asset"] == asset].copy()
            if part.empty:
                row = {
                    "scenario": scenario,
                    "asset": asset,
                    "trades": 0,
                    "total_return": 0.0,
                    "win_rate": np.nan,
                    "avg_net_ret": np.nan,
                    "avg_hold_minutes": np.nan,
                    "entry_maker_fill_rate": np.nan,
                    "exit_maker_fill_rate": np.nan,
                    "target_hit_rate": np.nan,
                }
            else:
                row = {
                    "scenario": scenario,
                    "asset": asset,
                    "trades": int(len(part)),
                    "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                    "win_rate": float((part["net_ret"] > 0).mean()),
                    "avg_net_ret": float(part["net_ret"].mean()),
                    "avg_hold_minutes": float(part["hold_minutes"].mean()),
                    "entry_maker_fill_rate": float(part["entry_maker"].mean()),
                    "exit_maker_fill_rate": float(part["exit_maker"].mean()),
                    "target_hit_rate": float(part["target_hit"].mean()),
                }
            per_asset_rows.append(row)
            asset_rows.append(row)
        asset_df = pd.DataFrame(per_asset_rows)
        total_returns = asset_df["total_return"].to_numpy(dtype=float)
        overall_rows.append(
            {
                "scenario": scenario,
                "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
                "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
                "mean_trades": float(asset_df["trades"].mean()) if len(asset_df) else np.nan,
                "mean_win_rate": float(asset_df["win_rate"].mean()) if len(asset_df) else np.nan,
                "mean_avg_net_ret": float(asset_df["avg_net_ret"].mean()) if len(asset_df) else np.nan,
                "mean_hold_minutes": float(asset_df["avg_hold_minutes"].mean()) if len(asset_df) else np.nan,
                "mean_entry_maker_fill_rate": float(asset_df["entry_maker_fill_rate"].mean()) if len(asset_df) else np.nan,
                "mean_exit_maker_fill_rate": float(asset_df["exit_maker_fill_rate"].mean()) if len(asset_df) else np.nan,
                "mean_target_hit_rate": float(asset_df["target_hit_rate"].mean()) if len(asset_df) else np.nan,
            }
        )
    return pd.DataFrame(overall_rows), pd.DataFrame(asset_rows)


def ordered_path_horizon_view(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["side"] = pd.Categorical(work["side"], categories=SIDE_ORDER, ordered=True)
    work = work.sort_values(["side", "horizon_15m_bars"]).reset_index(drop=True)
    work["side"] = work["side"].map(SIDE_LABELS)
    return work


def ordered_path_stats_view(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["side"] = pd.Categorical(work["side"], categories=SIDE_ORDER, ordered=True)
    work = work.sort_values(["side"]).reset_index(drop=True)
    work["side"] = work["side"].map(SIDE_LABELS)
    return work


def ordered_scenario_view(df: pd.DataFrame, labels: dict[str, str], order: list[str]) -> pd.DataFrame:
    work = df.copy()
    work["scenario"] = pd.Categorical(work["scenario"], categories=order, ordered=True)
    work = work.sort_values(["scenario"]).reset_index(drop=True)
    work["scenario"] = work["scenario"].map(labels)
    return work


def build_reader_notes(path_horizon: pd.DataFrame, exit_overall: pd.DataFrame, exec_overall: pd.DataFrame) -> tuple[str, list[str]]:
    horizon_view = path_horizon.set_index(["side", "horizon_15m_bars"])
    long_short_4 = horizon_view.loc[("long_short", 4), "avg_price_ret"]
    long_short_8 = horizon_view.loc[("long_short", 8), "avg_price_ret"]
    long_short_16 = horizon_view.loc[("long_short", 16), "avg_price_ret"]
    exit_view = exit_overall.set_index("scenario")
    best_exit = exit_overall.sort_values("mean_total_return", ascending=False).iloc[0]
    exec_view = exec_overall.set_index("scenario")
    base_fixed8 = exec_view.loc["baseline_taker_fixed8", "mean_total_return"]
    maker_entry_2 = exec_view.loc["maker_entry_2bps_ttl15m_fixed8", "mean_total_return"]
    hybrid_tp = exec_view.loc["maker_entry_2bps_ttl15m_tp1atr_timeout16", "mean_total_return"]
    headline = (
        f"从 15m 路径上看，32b 的均值利润不是极端前置：多空合并在 4 bars≈{pct(long_short_4)}、8 bars≈{pct(long_short_8)}、16 bars≈{pct(long_short_16)}；"
        f"离场族里当前最强的是 {EXIT_LABELS[str(best_exit['scenario'])]}（mean_total_return≈{pct(best_exit['mean_total_return'])}）。"
    )
    notes = [
        f"如果只看路径衰减，32b 的 edge 更像‘前 4 bars 基本成型’，但不是 1~2 根就完全走完；所以给 maker-first 一个很短 TTL 去试成交，是值得研究的。",
        f"在这版 5m 执行仿真里，温和的 maker-first 入场确实有帮助：baseline fixed8≈{pct(base_fixed8)}，maker-first 2bps + fixed8≈{pct(maker_entry_2)}；但 4bps 那档已经回落，说明这条 continuation 可以争取一点价格改善，但不能贪得太深。",
        f"对 exit 来说，纯收益最优仍是更短的固定持有（尤其 4x15m）；maker-friendly target exit / timeout fallback 更像是‘可落地 compromise’——绝对收益低于 raw fixed-hold，但换来更短持仓、更高 maker exit rate，以及更像真实 desk 会接受的离场结构。当前最完整的 hybrid 方案（maker-first entry 2bps + 1ATR target）≈{pct(hybrid_tp)}。",
    ]
    return headline, notes


def inject_section(report_path: Path, html_block: str, marker_id: str = MARKER_ID) -> None:
    html = report_path.read_text(encoding="utf-8")
    start_marker = f"<!-- {marker_id}:start -->"
    end_marker = f"<!-- {marker_id}:end -->"
    wrapped = f"{start_marker}\n{html_block}\n{end_marker}"
    if start_marker in html and end_marker in html:
        left = html.split(start_marker)[0]
        right = html.split(end_marker, 1)[1]
        html = left + wrapped + right
    else:
        html = html.replace("</body>", wrapped + "\n</body>")
    report_path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank 32b execution / exit research probe.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    days = int(args.days)
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    frame_map: dict[str, pd.DataFrame] = {}
    subbars_map: dict[str, pd.DataFrame] = {}
    ts_map: dict[str, np.ndarray] = {}
    trade_rows: list[pd.DataFrame] = []
    meta_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        bars_15m = perp_mod.load_or_fetch_perp_bars(symbol, days=days, refresh=bool(args.refresh))
        bars_5m = load_or_fetch_perp_5m(symbol, days=days, refresh=bool(args.refresh))
        frame = ext_mod.build_rank32b_frame_from_bars(asset, bars_15m)
        frame["atr14"] = compute_atr(frame)
        frame_map[asset] = frame
        subbars_map[asset] = bars_5m.copy().sort_values("timestamp").reset_index(drop=True)
        ts_map[asset] = subbars_map[asset]["timestamp"].to_numpy(dtype="datetime64[ns]")
        signals = build_signal_trades(frame, asset)
        trade_rows.append(signals)
        meta_rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "bars_15m": int(len(bars_15m)),
                "bars_5m": int(len(bars_5m)),
                "signals": int(len(signals)),
                "first_15m_utc": bars_15m["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(bars_15m) else "-",
                "last_15m_utc": bars_15m["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(bars_15m) else "-",
            }
        )

    trades = pd.concat([df for df in trade_rows if not df.empty], ignore_index=True) if trade_rows else pd.DataFrame()
    path_rows = build_path_rows(trades, frame_map)
    path_horizon, path_stats = summarize_path(path_rows)
    exit_trades = run_exit_family(trades, subbars_map, ts_map)
    exit_overall, exit_asset = summarize_scenarios(exit_trades, EXIT_ORDER)
    exec_trades = run_execution_scenarios(trades, subbars_map, ts_map)
    exec_overall, exec_asset = summarize_scenarios(exec_trades, EXEC_ORDER)

    path_horizon_out = ordered_path_horizon_view(path_horizon)
    path_stats_out = ordered_path_stats_view(path_stats)
    exit_overall_out = ordered_scenario_view(exit_overall, EXIT_LABELS, EXIT_ORDER)
    exec_overall_out = ordered_scenario_view(exec_overall, EXEC_LABELS, EXEC_ORDER)
    exit_asset_top = exit_asset[exit_asset["scenario"].isin(["fixed_hold_8_taker", "tp_1.00atr_limit_timeout16"])].copy()
    exec_asset_top = exec_asset[exec_asset["scenario"].isin(["baseline_taker_fixed8", "maker_entry_2bps_ttl15m_tp1atr_timeout16"])].copy()
    if not exit_asset_top.empty:
        exit_asset_top["scenario"] = pd.Categorical(exit_asset_top["scenario"], categories=["fixed_hold_8_taker", "tp_1.00atr_limit_timeout16"], ordered=True)
        exit_asset_top = exit_asset_top.sort_values(["scenario", "asset"]).reset_index(drop=True)
        exit_asset_top["scenario"] = exit_asset_top["scenario"].map(EXIT_LABELS)
    if not exec_asset_top.empty:
        exec_asset_top["scenario"] = pd.Categorical(exec_asset_top["scenario"], categories=["baseline_taker_fixed8", "maker_entry_2bps_ttl15m_tp1atr_timeout16"], ordered=True)
        exec_asset_top = exec_asset_top.sort_values(["scenario", "asset"]).reset_index(drop=True)
        exec_asset_top["scenario"] = exec_asset_top["scenario"].map(EXEC_LABELS)

    headline, notes = build_reader_notes(path_horizon, exit_overall, exec_overall)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Persist artifacts
    path_rows_out = path_rows.copy()
    trades_out = trades.copy()
    exit_trades_out = exit_trades.copy()
    exec_trades_out = exec_trades.copy()
    for df in [path_rows_out, trades_out, exit_trades_out, exec_trades_out]:
        for col in ["event_ts", "entry_ts", "exit_ts"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    pd.DataFrame(meta_rows).to_csv(ART_DIR / f"execution_probe_{days}d_meta.csv", index=False)
    trades_out.to_csv(ART_DIR / f"execution_probe_{days}d_signal_trades.csv", index=False)
    path_rows_out.to_csv(ART_DIR / f"execution_probe_{days}d_path_rows.csv", index=False)
    path_horizon.to_csv(ART_DIR / f"execution_probe_{days}d_path_horizon_summary.csv", index=False)
    path_stats.to_csv(ART_DIR / f"execution_probe_{days}d_path_stats_summary.csv", index=False)
    exit_trades_out.to_csv(ART_DIR / f"execution_probe_{days}d_exit_family_trades.csv", index=False)
    exit_overall.to_csv(ART_DIR / f"execution_probe_{days}d_exit_family_overall.csv", index=False)
    exit_asset.to_csv(ART_DIR / f"execution_probe_{days}d_exit_family_asset.csv", index=False)
    exec_trades_out.to_csv(ART_DIR / f"execution_probe_{days}d_execution_scenarios_trades.csv", index=False)
    exec_overall.to_csv(ART_DIR / f"execution_probe_{days}d_execution_scenarios_overall.csv", index=False)
    exec_asset.to_csv(ART_DIR / f"execution_probe_{days}d_execution_scenarios_asset.csv", index=False)

    html_block = f"""
  <div class='card'>
    <h2>execution / exit research（新增）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 信号层：Binance perp 15m Rank 32b 原规则不变 ｜ 执行层：Binance perp 5m 仿真 ｜ 费用假设：maker=0bps、taker=6bps ｜ 目的：回答 32b 是否值得往 limit / maker-friendly exit 继续推进。</p>
    <p><b>{escape(headline)}</b></p>
    <h3>1) 利润衰减 / MFE-MAE（15m 路径）</h3>
    {render_table(path_horizon_out[["side","horizon_15m_bars","avg_price_ret","median_price_ret","win_rate"]], percent_cols={"avg_price_ret","median_price_ret","win_rate"}, digits_cols={"horizon_15m_bars":0})}
    {render_table(path_stats_out[["side","trades","avg_mfe_16bars","avg_mae_16bars","median_time_to_mfe_bars","median_time_to_mae_bars"]], percent_cols={"avg_mfe_16bars","avg_mae_16bars"}, digits_cols={"trades":0, "median_time_to_mfe_bars":1, "median_time_to_mae_bars":1})}
    <h3>2) 离场条件敏感性（5m execution engine）</h3>
    {render_table(exit_overall_out[["scenario","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate","mean_hold_minutes","mean_exit_maker_fill_rate","mean_target_hit_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_exit_maker_fill_rate","mean_target_hit_rate"}, digits_cols={"mean_trades":1, "mean_hold_minutes":1})}
    <p class='muted'>分资产只展开 baseline 与最像 desk 可落地的 <code>1.00 ATR limit target</code> 对照。</p>
    {render_table(exit_asset_top[["scenario","asset","trades","total_return","win_rate","avg_net_ret","avg_hold_minutes","exit_maker_fill_rate","target_hit_rate"]], percent_cols={"total_return","win_rate","avg_net_ret","exit_maker_fill_rate","target_hit_rate"}, digits_cols={"trades":0, "avg_hold_minutes":1})}
    <h3>3) maker-first 入场仿真（5m）</h3>
    {render_table(exec_overall_out[["scenario","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate","mean_hold_minutes","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_target_hit_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate","mean_entry_maker_fill_rate","mean_exit_maker_fill_rate","mean_target_hit_rate"}, digits_cols={"mean_trades":1, "mean_hold_minutes":1})}
    {render_table(exec_asset_top[["scenario","asset","trades","total_return","win_rate","avg_net_ret","avg_hold_minutes","entry_maker_fill_rate","exit_maker_fill_rate"]], percent_cols={"total_return","win_rate","avg_net_ret","entry_maker_fill_rate","exit_maker_fill_rate"}, digits_cols={"trades":0, "avg_hold_minutes":1})}
    <h3>reader-facing 结论</h3>
    <ul>{''.join(f'<li>{escape(note)}</li>' for note in notes)}</ul>
    <p class='muted'>重要假设：maker-first 入场 = 以 signal 后第一根 15m 的开盘价为锚，向自己有利方向改进 {ENTRY_OFFSETS_BPS[0]:.0f}/{ENTRY_OFFSETS_BPS[1]:.0f} bps，给 3 根 5m TTL；没成交则 fallback 为 taker。limit target exit = 命中 ATR 目标时按 maker 成交，否则最晚在 16x15m timeout 用 taker 平仓。</p>
    <p class='muted'>artifact：<code>execution_probe_{days}d_path_horizon_summary.csv</code>、<code>execution_probe_{days}d_exit_family_overall.csv</code>、<code>execution_probe_{days}d_execution_scenarios_overall.csv</code> 等。</p>
  </div>
"""

    for path in [SITE_DIR / "report.html", READING_PATH]:
        inject_section(path, html_block, marker_id=MARKER_ID)

    print(
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "days": days,
            "signals": int(len(trades)),
            "path_rows": int(len(path_rows)),
            "exit_trades": int(len(exit_trades)),
            "exec_trades": int(len(exec_trades)),
        }
    )


if __name__ == "__main__":
    main()
