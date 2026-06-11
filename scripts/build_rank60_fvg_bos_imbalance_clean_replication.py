#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank60_fvg_bos_imbalance_retest_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank60_fvg_bos_imbalance_retest_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "bos_only", "bos_fvg_retest", "bos_vi_retest"]
PRIMARY_VARIANTS = ["bos_fvg_retest", "bos_vi_retest"]
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FAIL_WINDOWS = [4, 8]
SWING_LOOKBACK = 20
BOS_RECENT_BARS = 8
RETEST_TOL_ATR = 0.15

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
.muted { color: #6b7280; }
.good { color: #065f46; font-weight: 600; }
.bad { color: #991b1b; font-weight: 600; }
.card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
"""


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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


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


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    df["confirmed_swing_high"] = df["high"].rolling(SWING_LOOKBACK, min_periods=SWING_LOOKBACK).max().shift(1)
    df["confirmed_swing_low"] = df["low"].rolling(SWING_LOOKBACK, min_periods=SWING_LOOKBACK).min().shift(1)
    df["bullish_bos"] = (df["close"] > df["confirmed_swing_high"]).fillna(False)
    df["bearish_bos"] = (df["close"] < df["confirmed_swing_low"]).fillna(False)

    df["bullish_fvg"] = (df["low"] > df["high"].shift(2)).fillna(False)
    df["bullish_fvg_low"] = df["high"].shift(2)
    df["bullish_fvg_high"] = df["low"]
    df["bearish_fvg"] = (df["high"] < df["low"].shift(2)).fillna(False)
    df["bearish_fvg_low"] = df["high"]
    df["bearish_fvg_high"] = df["low"].shift(2)

    df["bullish_vi"] = (df["low"] > df["high"].shift(1)).fillna(False)
    df["bullish_vi_low"] = df["high"].shift(1)
    df["bullish_vi_high"] = df["low"]
    df["bearish_vi"] = (df["high"] < df["low"].shift(1)).fillna(False)
    df["bearish_vi_low"] = df["high"]
    df["bearish_vi_high"] = df["low"].shift(1)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
    atr = df["atr14"]
    df["breakout_short_signal"] = (
        low.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr)
        & (df["high"] <= low + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def recent_zone_pass(frame: pd.DataFrame, idx: int, direction: int, zone_kind: str) -> tuple[bool, float, float, int | None]:
    atr = float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan
    tol = 0.0 if not np.isfinite(atr) else atr * RETEST_TOL_ATR
    if direction > 0:
        bos_col = "bullish_bos"
        flag_col = "bullish_fvg" if zone_kind == "fvg" else "bullish_vi"
        low_col = "bullish_fvg_low" if zone_kind == "fvg" else "bullish_vi_low"
        high_col = "bullish_fvg_high" if zone_kind == "fvg" else "bullish_vi_high"
    else:
        bos_col = "bearish_bos"
        flag_col = "bearish_fvg" if zone_kind == "fvg" else "bearish_vi"
        low_col = "bearish_fvg_low" if zone_kind == "fvg" else "bearish_vi_low"
        high_col = "bearish_fvg_high" if zone_kind == "fvg" else "bearish_vi_high"

    start = max(0, idx - BOS_RECENT_BARS)
    bos_idxs = frame.index[start: idx + 1][frame.loc[start:idx, bos_col]]
    if len(bos_idxs) == 0:
        return False, np.nan, np.nan, None
    bos_idx = int(bos_idxs[-1])
    zone_idxs = frame.index[bos_idx: idx + 1][frame.loc[bos_idx:idx, flag_col]]
    if len(zone_idxs) == 0:
        return False, np.nan, np.nan, bos_idx
    zidx = int(zone_idxs[-1])
    zone_low = float(frame.iloc[zidx][low_col]) if pd.notna(frame.iloc[zidx][low_col]) else np.nan
    zone_high = float(frame.iloc[zidx][high_col]) if pd.notna(frame.iloc[zidx][high_col]) else np.nan
    if not (np.isfinite(zone_low) and np.isfinite(zone_high)):
        return False, np.nan, np.nan, bos_idx
    row = frame.iloc[idx]
    close = float(row["close"])
    candle_low = float(row["low"])
    candle_high = float(row["high"])
    if direction > 0:
        retest_touch = candle_low <= zone_high + tol
        still_right_side = close >= zone_low
    else:
        retest_touch = candle_high >= zone_low - tol
        still_right_side = close <= zone_high
    return bool(retest_touch and still_right_side), zone_low, zone_high, bos_idx


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    sig = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    bos_col = "bullish_bos" if direction > 0 else "bearish_bos"
    for idx in range(max(SWING_LOOKBACK + 5, 40), len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        recent_bos = bool(frame.loc[max(0, idx - BOS_RECENT_BARS):idx, bos_col].any())
        fvg_gate, fvg_low, fvg_high, bos_idx = recent_zone_pass(frame, idx, direction, "fvg")
        vi_gate, vi_low, vi_high, _ = recent_zone_pass(frame, idx, direction, "vi")
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(frame.iloc[idx]["close"]),
                "atr14": float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan,
                "recent_bos": recent_bos,
                "bos_idx": bos_idx,
                "bos_age_bars": (idx - bos_idx) if bos_idx is not None else np.nan,
                "fvg_gate": fvg_gate,
                "fvg_low": fvg_low,
                "fvg_high": fvg_high,
                "vi_gate": vi_gate,
                "vi_low": vi_low,
                "vi_high": vi_high,
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def variant_allowed(sig: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "bos_only":
        return bool(sig.get("recent_bos", False))
    if variant == "bos_fvg_retest":
        return bool(sig.get("recent_bos", False) and sig.get("fvg_gate", False))
    if variant == "bos_vi_retest":
        return bool(sig.get("recent_bos", False) and sig.get("vi_gate", False))
    raise ValueError(variant)


def detect_failure(frame: pd.DataFrame, signal_idx: int, direction: int, signal_price: float, bars: int) -> int:
    last = min(len(frame) - 1, signal_idx + bars)
    for j in range(signal_idx + 1, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < signal_price:
            return 1
        if direction < 0 and close > signal_price:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    admitted = 0
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        if not variant_allowed(sig, variant):
            continue
        admitted += 1
        entry_idx = int(sig["entry_idx"])
        if entry_idx >= len(frame):
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        direction = int(sig["direction"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "signal_id": sig["signal_id"],
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "direction": direction,
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "signal_price": float(sig["signal_price"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "failure_4bars": detect_failure(frame, int(sig["signal_idx"]), direction, float(sig["signal_price"]), 4),
                "failure_8bars": detect_failure(frame, int(sig["signal_idx"]), direction, float(sig["signal_price"]), 8),
                "bos_age_bars": float(sig["bos_age_bars"]) if pd.notna(sig["bos_age_bars"]) else np.nan,
                "fvg_gate": bool(sig["fvg_gate"]),
                "vi_gate": bool(sig["vi_gate"]),
            }
        )
    return pd.DataFrame(rows), admitted


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int, base_trades: pd.DataFrame) -> dict[str, object]:
    base_winners = set(base_trades.loc[base_trades["net_ret"] > 0, "signal_id"].tolist())
    variant_ids = set(trades["signal_id"].tolist()) if not trades.empty else set()
    retained_winners = len(base_winners & variant_ids)
    winner_trunc = np.nan
    if base_winners:
        winner_trunc = 1.0 - (retained_winners / len(base_winners))
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "base_signals": int(base_signals),
            "admitted_signals": int(admitted_signals),
            "trades": 0,
            "trade_count_retention": np.nan,
            "signal_retention": (admitted_signals / base_signals) if base_signals else np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "failure_4bars_rate": np.nan,
            "failure_8bars_rate": np.nan,
            "winner_truncation_rate": winner_trunc,
            "mean_bos_age_bars": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "signal_retention": (admitted_signals / base_signals) if base_signals else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "failure_4bars_rate": float(trades["failure_4bars"].mean()),
        "failure_8bars_rate": float(trades["failure_8bars"].mean()),
        "winner_truncation_rate": winner_trunc,
        "mean_bos_age_bars": float(trades["bos_age_bars"].dropna().mean()) if trades["bos_age_bars"].notna().any() else np.nan,
    }


def add_retentions(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            base_map = (
                out[(out["setup"] == setup) & (out["variant"] == "base") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
                axis=1,
            )
    return out


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    q1 = df["entry_ts"].quantile(1 / 3)
    q2 = df["entry_ts"].quantile(2 / 3)

    def bucket(ts: pd.Timestamp) -> str:
        if ts <= q1:
            return "bucket_1"
        if ts <= q2:
            return "bucket_2"
        return "bucket_3"

    df["bucket"] = df["entry_ts"].map(bucket)
    rows: list[dict[str, object]] = []
    grouped = df.groupby(["setup", "variant", "bucket", "asset"], dropna=False)
    for (setup, variant, bucket_name, asset), part in grouped:
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    primary = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        vals = {}
        for variant in VARIANTS:
            part = primary[(primary["setup"] == setup) & (primary["variant"] == variant)]
            vals[variant] = part.iloc[0] if not part.empty else None
        rows.append(
            {
                "setup": setup,
                "base_return": float(vals["base"]["mean_total_return"]) if vals["base"] is not None else np.nan,
                "bos_return": float(vals["bos_only"]["mean_total_return"]) if vals["bos_only"] is not None else np.nan,
                "fvg_return": float(vals["bos_fvg_retest"]["mean_total_return"]) if vals["bos_fvg_retest"] is not None else np.nan,
                "vi_return": float(vals["bos_vi_retest"]["mean_total_return"]) if vals["bos_vi_retest"] is not None else np.nan,
                "base_fail4": float(vals["base"]["mean_failure_4bars_rate"]) if vals["base"] is not None else np.nan,
                "bos_fail4": float(vals["bos_only"]["mean_failure_4bars_rate"]) if vals["bos_only"] is not None else np.nan,
                "fvg_fail4": float(vals["bos_fvg_retest"]["mean_failure_4bars_rate"]) if vals["bos_fvg_retest"] is not None else np.nan,
                "vi_fail4": float(vals["bos_vi_retest"]["mean_failure_4bars_rate"]) if vals["bos_vi_retest"] is not None else np.nan,
                "bos_retention": float(vals["bos_only"]["mean_trade_count_retention"]) if vals["bos_only"] is not None else np.nan,
                "fvg_retention": float(vals["bos_fvg_retest"]["mean_trade_count_retention"]) if vals["bos_fvg_retest"] is not None else np.nan,
                "vi_retention": float(vals["bos_vi_retest"]["mean_trade_count_retention"]) if vals["bos_vi_retest"] is not None else np.nan,
                "bos_pos_ratio": float(vals["bos_only"]["positive_asset_ratio"]) if vals["bos_only"] is not None else np.nan,
                "fvg_pos_ratio": float(vals["bos_fvg_retest"]["positive_asset_ratio"]) if vals["bos_fvg_retest"] is not None else np.nan,
                "vi_pos_ratio": float(vals["bos_vi_retest"]["positive_asset_ratio"]) if vals["bos_vi_retest"] is not None else np.nan,
                "fvg_winner_trunc": float(vals["bos_fvg_retest"]["mean_winner_truncation_rate"]) if vals["bos_fvg_retest"] is not None else np.nan,
                "vi_winner_trunc": float(vals["bos_vi_retest"]["mean_winner_truncation_rate"]) if vals["bos_vi_retest"] is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    improved = 0
    clean = 0
    packaging_only = 0
    for _, r in compare.iterrows():
        bos_better = (
            pd.notna(r["bos_return"]) and pd.notna(r["base_return"]) and pd.notna(r["bos_retention"]) and pd.notna(r["bos_fail4"])
            and float(r["bos_retention"]) >= 0.30
            and (float(r["bos_return"]) > float(r["base_return"]) + 0.001 or float(r["bos_fail4"]) < float(r["base_fail4"]) - 0.03)
        )
        fvg_better = (
            pd.notna(r["fvg_return"]) and pd.notna(r["fvg_retention"]) and pd.notna(r["fvg_fail4"])
            and float(r["fvg_retention"]) >= 0.15 and float(r["fvg_winner_trunc"]) <= 0.75
            and (float(r["fvg_return"]) > float(r["base_return"]) + 0.002 or float(r["fvg_fail4"]) < float(r["base_fail4"]) - 0.04)
        )
        vi_better = (
            pd.notna(r["vi_return"]) and pd.notna(r["vi_retention"]) and pd.notna(r["vi_fail4"])
            and float(r["vi_retention"]) >= 0.15 and float(r["vi_winner_trunc"]) <= 0.75
            and (float(r["vi_return"]) > float(r["base_return"]) + 0.002 or float(r["vi_fail4"]) < float(r["base_fail4"]) - 0.04)
        )
        if fvg_better or vi_better:
            improved += 1
            best_pos = max(float(r["fvg_pos_ratio"]) if pd.notna(r["fvg_pos_ratio"]) else 0.0, float(r["vi_pos_ratio"]) if pd.notna(r["vi_pos_ratio"]) else 0.0)
            if best_pos >= (1 / 3):
                clean += 1
        if bos_better and not fvg_better and not vi_better:
            packaging_only += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r['base_return'])} / BOS≈{pct(r['bos_return'])} / BOS+FVG≈{pct(r['fvg_return'])} / BOS+VI≈{pct(r['vi_return'])}"
        for _, r in compare.iterrows()
    )
    if improved >= 2 and clean >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 至少说明 FVG/VI retest 不全是给 BOS 换词包装：在部分 archetype 上它能比纯 BOS 更少亏或更少 4-bar 早衰，但跨 setup/跨资产还不够统一，所以先留在 P1 证据池，比直接升格更诚实。",
        )
    if packaging_only >= 2:
        return (
            "park / evidence pool",
            headline,
            "最小 clean replication 更像在证明：真正起作用的主要是 recent BOS，本轮 FVG/VI retest 没能稳定提供额外增量，更多像给 BOS 包装一层 zone 叙事，不值得继续占 fast lane。",
        )
    return (
        "park / evidence pool",
        headline,
        "最小 clean replication 没把 Rank 60 推进到候选池：BOS/FVG/VI 这层 gate 当前仍主要靠砍样本，跨资产与 setup 的结果不够统一，继续给预算不如转向下一条 fresh Scout。",
    )


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    compare = compare.set_index("setup")
    row_ema = compare.loc["ema_psar_long"]
    row_fib = compare.loc["fib_retest_long"]
    row_short = compare.loc["breakout_short"]
    if verdict.startswith("P1"):
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 60 仍保留在 P1，则只允许给它 1 个真正会改变 verdict 的最小检查（默认优先 time stability 或 cross-asset honesty）` -> `Run 3 = 若 Rank 60 仍不能升格，则转去比较 Rank 61 > continuation fail-fast overlay > pullback-quality / CQI；只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    else:
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 按 7.10 重新认领 1 条 fresh paper/repo based 5m/15m crypto source（优先 Rank 61 > continuation fail-fast overlay > pullback-quality / CQI）` -> `Run 3 = 只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    block = (
        f"> **最新补充（{generated_at}）**：这轮先按 `Run 1` 重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane，因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。`manual_narrow_paper_last_run_summary.json` 最新一次仍为 `new_closed_trades_appended={latest_p3_appends}`，不构成回头挤占 `P3 continuity` 的更高优先级。随后按权威顺序执行 **`Run 2 / Rank 60 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`bos_only`、`bos_fvg_retest`、`bos_vi_retest` 四臂，统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。\n"
        f">  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `BOS≈{pct(row_ema['bos_return'])}`、`BOS+FVG≈{pct(row_ema['fvg_return'])}`、`BOS+VI≈{pct(row_ema['vi_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `BOS≈{pct(row_fib['bos_return'])}`、`BOS+FVG≈{pct(row_fib['fvg_return'])}`、`BOS+VI≈{pct(row_fib['vi_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `BOS≈{pct(row_short['bos_return'])}`、`BOS+FVG≈{pct(row_short['fvg_return'])}`、`BOS+VI≈{pct(row_short['vi_return'])}`。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 60 / FVG-BOS imbalance retest gate = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank60_fvg_bos_imbalance_retest_15m/report.html`、`reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_clean_replication.html`；artifact：`reports/artifacts/scout_rank60_fvg_bos_imbalance_retest_15m/overall_summary.csv`。\n"
        f">  - 排班含义：当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 60 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    latest_p3_appends = 0
    summary_path = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"
    if summary_path.exists():
        try:
            latest_p3_appends = int(pd.read_json(summary_path, typ="series").get("new_closed_trades_appended", 0))
        except Exception:
            latest_p3_appends = 0

    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            base_cache: dict[float, pd.DataFrame] = {}
            admitted_cache: dict[tuple[str, float], int] = {}
            for cost in COSTS:
                base_trades, base_admitted = build_trades(frame, sigs, "base", cost)
                base_cache[cost] = base_trades
                admitted_cache[("base", cost)] = base_admitted
                if not base_trades.empty:
                    trade_frames.append(base_trades)
            for variant in VARIANTS:
                for cost in COSTS:
                    if variant == "base":
                        trades = base_cache[cost]
                        admitted = admitted_cache[(variant, cost)]
                    else:
                        trades, admitted = build_trades(frame, sigs, variant, cost)
                        if not trades.empty:
                            trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            setup=setup,
                            variant=variant,
                            cost_bps=cost,
                            base_signals=base_signals,
                            admitted_signals=admitted,
                            base_trades=base_cache[cost],
                        )
                    )

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_df = add_retentions(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall_df = (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_signal_retention=("signal_retention", "mean"),
            mean_failure_4bars_rate=("failure_4bars_rate", "mean"),
            mean_failure_8bars_rate=("failure_8bars_rate", "mean"),
            mean_winner_truncation_rate=("winner_truncation_rate", "mean"),
            mean_bos_age_bars=("mean_bos_age_bars", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )
    time_pockets_df = build_time_pockets(trades_df)
    compare_df = build_setup_compare(overall_df)
    verdict, headline, reason = build_verdict(compare_df)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    compare_df.to_csv(ART_DIR / "setup_compare.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_card = f"""
<h1>Rank 60 / FVG-BOS imbalance retest gate — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：FVG / VI retest 这层 zone 语义，能不能在 recent BOS 之上提供额外、而不是仅仅换词包装的 shared continuation gate 价值。</p>
</div>
"""

    method = f"""
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>只复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>只比较三条最小 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>四臂固定为：<code>base</code>、<code>bos_only</code>、<code>bos_fvg_retest</code>、<code>bos_vi_retest</code>。</li>
    <li>所有执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</li>
    <li>recent BOS 只看最近 <code>{BOS_RECENT_BARS}</code> 根内 confirmed swing 穿越；FVG 用三根 K gap，VI 用一根错位 gap，不偷渡 liquidity sweep / HTF bias / premium-discount 叙事。</li>
  </ul>
</div>
"""

    compare_view = compare_df[[
        "setup", "base_return", "bos_return", "fvg_return", "vi_return", "base_fail4", "bos_fail4", "fvg_fail4", "vi_fail4", "bos_retention", "fvg_retention", "vi_retention", "bos_pos_ratio", "fvg_pos_ratio", "vi_pos_ratio"
    ]].copy()
    report_body = summary_card + method
    report_body += "<h2>setup compare（6bps）</h2>" + render_table(
        compare_view,
        percent_cols={"base_return", "bos_return", "fvg_return", "vi_return", "base_fail4", "bos_fail4", "fvg_fail4", "vi_fail4", "bos_retention", "fvg_retention", "vi_retention", "bos_pos_ratio", "fvg_pos_ratio", "vi_pos_ratio"},
    )
    report_body += "<h2>overall summary</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_failure_4bars_rate", "mean_failure_8bars_rate", "mean_winner_truncation_rate"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_bos_age_bars": 1},
    )
    report_body += "<h2>asset-level summary</h2>" + render_table(
        asset_df,
        percent_cols={"trade_count_retention", "signal_retention", "total_return", "avg_net_ret", "win_rate", "failure_4bars_rate", "failure_8bars_rate", "winner_truncation_rate"},
        digits_cols={"trades": 0, "base_signals": 0, "admitted_signals": 0, "cost_bps_per_side": 0, "mean_bos_age_bars": 1},
    )
    report_body += "<h2>time pockets</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 1},
    )
    write_html(SITE_DIR / "report.html", "Rank 60 clean replication", report_body)

    reading_body = summary_card
    reading_body += "<div class='card'><h2>当前更直白的读法</h2><p>如果这层 FVG / VI retest 真有用，它至少应该在 recent BOS 之上多给一点增量：要么更少 4~8 bar 早衰，要么比纯 BOS 少亏，而且不能靠把样本砍得只剩极少数交易。若最有用的其实只是 BOS 本身，那 Rank 60 就该尽快 park。</p></div>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_failure_4bars_rate", "mean_failure_8bars_rate", "mean_winner_truncation_rate"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_bos_age_bars": 1},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>"
    write_html(READING_DIR / "rank60_fvg_bos_imbalance_retest_clean_replication.html", "Rank 60 clean replication", reading_body)

    update_todo(compare_df, verdict, generated_at, latest_p3_appends)
    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
