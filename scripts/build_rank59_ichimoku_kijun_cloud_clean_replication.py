#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank59_ichimoku_kijun_cloud_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank59_ichimoku_kijun_cloud_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "kijun_only", "cloud_side", "kijun_cloud_side", "kijun_cloud_side_adx_floor"]
PRIMARY_VARIANT = "kijun_cloud_side"
STRICT_VARIANT = "kijun_cloud_side_adx_floor"
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FAIL_WINDOWS = [4, 8]
KIJUN_LOOKBACK = 3
ADX_FLOOR = 20.0

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
pre { background: #0f172a; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow-x: auto; }
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


def compute_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)
    tr = pd.concat(
        [(high - low).abs(), (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1
    ).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["adx14"] = compute_adx(df)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    tenkan_high = df["high"].rolling(9, min_periods=9).max()
    tenkan_low = df["low"].rolling(9, min_periods=9).min()
    kijun_high = df["high"].rolling(26, min_periods=26).max()
    kijun_low = df["low"].rolling(26, min_periods=26).min()
    spanb_high = df["high"].rolling(52, min_periods=52).max()
    spanb_low = df["low"].rolling(52, min_periods=52).min()
    df["tenkan"] = (tenkan_high + tenkan_low) / 2.0
    df["kijun"] = (kijun_high + kijun_low) / 2.0
    df["span_a"] = (df["tenkan"] + df["kijun"]) / 2.0
    df["span_b"] = (spanb_high + spanb_low) / 2.0
    df["cloud_top"] = pd.concat([df["span_a"], df["span_b"]], axis=1).max(axis=1)
    df["cloud_bottom"] = pd.concat([df["span_a"], df["span_b"]], axis=1).min(axis=1)

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


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def kijun_hold_pass(frame: pd.DataFrame, idx: int, direction: int) -> bool:
    start = max(0, idx - KIJUN_LOOKBACK + 1)
    part = frame.iloc[start : idx + 1]
    if part["kijun"].isna().all():
        return False
    if direction > 0:
        hits = (part["close"] > part["kijun"]).sum()
        latest_ok = bool(frame.iloc[idx]["close"] > frame.iloc[idx]["kijun"])
    else:
        hits = (part["close"] < part["kijun"]).sum()
        latest_ok = bool(frame.iloc[idx]["close"] < frame.iloc[idx]["kijun"])
    return bool(hits >= min(2, len(part)) and latest_ok)


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    sig = frame[setup_signal_col(setup)] & ~frame[setup_signal_col(setup)].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(60, len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        row = frame.iloc[idx]
        close = float(row["close"])
        tenkan = float(row["tenkan"]) if pd.notna(row["tenkan"]) else np.nan
        kijun = float(row["kijun"]) if pd.notna(row["kijun"]) else np.nan
        cloud_top = float(row["cloud_top"]) if pd.notna(row["cloud_top"]) else np.nan
        cloud_bottom = float(row["cloud_bottom"]) if pd.notna(row["cloud_bottom"]) else np.nan
        if direction > 0:
            cloud_side = np.isfinite(cloud_top) and close > cloud_top
            tenkan_kijun = np.isfinite(tenkan) and np.isfinite(kijun) and tenkan > kijun
        else:
            cloud_side = np.isfinite(cloud_bottom) and close < cloud_bottom
            tenkan_kijun = np.isfinite(tenkan) and np.isfinite(kijun) and tenkan < kijun
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": close,
                "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else np.nan,
                "adx14": float(row["adx14"]) if pd.notna(row["adx14"]) else np.nan,
                "tenkan": tenkan,
                "kijun": kijun,
                "cloud_top": cloud_top,
                "cloud_bottom": cloud_bottom,
                "kijun_hold": kijun_hold_pass(frame, idx, direction),
                "cloud_side": bool(cloud_side),
                "tenkan_kijun": bool(tenkan_kijun),
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def variant_allowed(sig: pd.Series, variant: str) -> bool:
    kijun = bool(sig.get("kijun_hold", False))
    cloud = bool(sig.get("cloud_side", False))
    cross = bool(sig.get("tenkan_kijun", False))
    adx = float(sig.get("adx14", np.nan))
    if variant == "base":
        return True
    if variant == "kijun_only":
        return kijun
    if variant == "cloud_side":
        return cloud
    if variant == "kijun_cloud_side":
        return kijun and cloud and cross
    if variant == "kijun_cloud_side_adx_floor":
        return kijun and cloud and cross and np.isfinite(adx) and adx >= ADX_FLOOR
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
                "adx14": float(sig["adx14"]) if pd.notna(sig["adx14"]) else np.nan,
            }
        )
    return pd.DataFrame(rows), admitted


def summarize_asset(
    trades: pd.DataFrame,
    *,
    asset: str,
    setup: str,
    variant: str,
    cost_bps: float,
    base_signals: int,
    admitted_signals: int,
    base_trades: pd.DataFrame,
) -> dict[str, object]:
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
                "kijun_return": float(vals["kijun_only"]["mean_total_return"]) if vals["kijun_only"] is not None else np.nan,
                "cloud_return": float(vals["cloud_side"]["mean_total_return"]) if vals["cloud_side"] is not None else np.nan,
                "combo_return": float(vals[PRIMARY_VARIANT]["mean_total_return"]) if vals[PRIMARY_VARIANT] is not None else np.nan,
                "combo_adx_return": float(vals[STRICT_VARIANT]["mean_total_return"]) if vals[STRICT_VARIANT] is not None else np.nan,
                "base_fail4": float(vals["base"]["mean_failure_4bars_rate"]) if vals["base"] is not None else np.nan,
                "combo_fail4": float(vals[PRIMARY_VARIANT]["mean_failure_4bars_rate"]) if vals[PRIMARY_VARIANT] is not None else np.nan,
                "combo_adx_fail4": float(vals[STRICT_VARIANT]["mean_failure_4bars_rate"]) if vals[STRICT_VARIANT] is not None else np.nan,
                "combo_retention": float(vals[PRIMARY_VARIANT]["mean_trade_count_retention"]) if vals[PRIMARY_VARIANT] is not None else np.nan,
                "combo_adx_retention": float(vals[STRICT_VARIANT]["mean_trade_count_retention"]) if vals[STRICT_VARIANT] is not None else np.nan,
                "combo_winner_trunc": float(vals[PRIMARY_VARIANT]["mean_winner_truncation_rate"]) if vals[PRIMARY_VARIANT] is not None else np.nan,
                "combo_adx_winner_trunc": float(vals[STRICT_VARIANT]["mean_winner_truncation_rate"]) if vals[STRICT_VARIANT] is not None else np.nan,
                "combo_pos_ratio": float(vals[PRIMARY_VARIANT]["positive_asset_ratio"]) if vals[PRIMARY_VARIANT] is not None else np.nan,
                "combo_adx_pos_ratio": float(vals[STRICT_VARIANT]["positive_asset_ratio"]) if vals[STRICT_VARIANT] is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    improved = 0
    clean = 0
    for _, r in compare.iterrows():
        combo_better = (
            pd.notna(r["combo_return"]) and pd.notna(r["base_return"]) and pd.notna(r["combo_retention"])
            and pd.notna(r["combo_fail4"]) and pd.notna(r["base_fail4"])
            and float(r["combo_retention"]) >= 0.35
            and float(r["combo_winner_trunc"]) <= 0.60
            and (
                float(r["combo_return"]) > float(r["base_return"]) + 0.002
                or float(r["combo_fail4"]) < float(r["base_fail4"]) - 0.03
            )
        )
        strict_better = (
            pd.notna(r["combo_adx_return"]) and pd.notna(r["base_return"]) and pd.notna(r["combo_adx_retention"])
            and pd.notna(r["combo_adx_fail4"]) and pd.notna(r["base_fail4"])
            and float(r["combo_adx_retention"]) >= 0.25
            and float(r["combo_adx_winner_trunc"]) <= 0.75
            and (
                float(r["combo_adx_return"]) > float(r["base_return"]) + 0.002
                or float(r["combo_adx_fail4"]) < float(r["base_fail4"]) - 0.04
            )
        )
        if combo_better or strict_better:
            improved += 1
        if (
            (combo_better and pd.notna(r["combo_pos_ratio"]) and float(r["combo_pos_ratio"]) >= (1 / 3))
            or (strict_better and pd.notna(r["combo_adx_pos_ratio"]) and float(r["combo_adx_pos_ratio"]) >= (1 / 3))
        ):
            clean += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r['base_return'])} / kijun≈{pct(r['kijun_return'])} / cloud≈{pct(r['cloud_return'])} / combo≈{pct(r['combo_return'])} / combo+ADX≈{pct(r['combo_adx_return'])}"
        for _, r in compare.iterrows()
    )
    if improved >= 2 and clean >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 说明 Kijun + cloud-side 至少在部分 archetype 上不是纯靠砍样本少亏：它对 continuation 噪音有一点 shared gate 味道，但跨 setup / 跨资产还不够统一，因此先保留在 P1 证据池，比直接升格更诚实。",
        )
    return (
        "park / evidence pool",
        headline,
        "最小 clean replication 更像在证明：Ichimoku Kijun + cloud-side 目前主要还是换一种方式筛样本，虽然局部能少亏或少一点早期失败，但还不足以把它留在默认 fast lane。",
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
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = Rank 59 / Ichimoku Kijun + cloud-side 的 1 次便宜诚实检查（默认优先时间稳定性）` -> `Run 3 = 若 Rank 59 仍不能升格或 park，再比较 continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source；只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    else:
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 按 7.10 重新认领 1 条 fresh paper/repo based 5m/15m crypto source（优先 continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source）` -> `Run 3 = 只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    block = (
        f"> **最新补充（{generated_at}）**：这轮先按 `Run 1` 重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane，因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。`manual_narrow_paper_last_run_summary.json` 最新一次虽已出现 `new_closed_trades_appended={latest_p3_appends}`，但在当前有 active `guard-passed` Scout 候选时，它仍不足以越过 `Scout Seat` 的默认优先级，也不该让 bot3 回头挤占受限的 `P3 continuity` 预算。随后按权威顺序执行 **`Run 2 / Rank 59 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`kijun_only`、`cloud_side`、`kijun+cloud_side`、`kijun+cloud_side+ADX floor` 五臂，统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。\n"
        f">  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `kijun≈{pct(row_ema['kijun_return'])}`、`cloud≈{pct(row_ema['cloud_return'])}`、`combo≈{pct(row_ema['combo_return'])}`、`combo+ADX≈{pct(row_ema['combo_adx_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `kijun≈{pct(row_fib['kijun_return'])}`、`cloud≈{pct(row_fib['cloud_return'])}`、`combo≈{pct(row_fib['combo_return'])}`、`combo+ADX≈{pct(row_fib['combo_adx_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `kijun≈{pct(row_short['kijun_return'])}`、`cloud≈{pct(row_short['cloud_return'])}`、`combo≈{pct(row_short['combo_return'])}`、`combo+ADX≈{pct(row_short['combo_adx_return'])}`。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 59 / Ichimoku Kijun + cloud-side continuation gate = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank59_ichimoku_kijun_cloud_15m/report.html`、`reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_clean_replication.html`；artifact：`reports/artifacts/scout_rank59_ichimoku_kijun_cloud_15m/overall_summary.csv`。\n"
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
        raise RuntimeError("no signals formed for Rank 59 clean replication")
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
    primary = overall_df[(overall_df["setup"] == "ema_psar_long") & (overall_df["variant"] == PRIMARY_VARIANT) & (overall_df["cost_bps_per_side"] == PRIMARY_COST)]

    summary_card = f"""
<h1>Rank 59 / Ichimoku Kijun + cloud-side continuation gate — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：Kijun / cloud-side 这层 shared continuation gate，能不能在不过度砍样本的前提下，让现有 `EMA-PSAR / Fib retest / breakout-short` 三条 archetype 少一点 4~8 bar 早衰，或者至少少亏？</p>
</div>
"""

    method = f"""
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>只复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>只比较三条最小 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>五臂固定为：<code>base</code>、<code>kijun_only</code>、<code>cloud_side</code>、<code>kijun+cloud_side</code>、<code>kijun+cloud_side+ADX floor</code>。</li>
    <li>所有执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</li>
    <li>第一轮默认不偷渡 <code>Chikou / RSI / 时间过滤 / BE / trailing</code>，只回答 Kijun/cloud-side 本身有没有共享 continuation gate 的诚实价值。</li>
  </ul>
</div>
"""

    compare_view = compare_df[[
        "setup", "base_return", "kijun_return", "cloud_return", "combo_return", "combo_adx_return",
        "base_fail4", "combo_fail4", "combo_adx_fail4", "combo_retention", "combo_adx_retention",
        "combo_winner_trunc", "combo_adx_winner_trunc", "combo_pos_ratio", "combo_adx_pos_ratio"
    ]].copy()
    report_body = summary_card + method
    report_body += "<h2>setup compare（6bps）</h2>" + render_table(
        compare_view,
        percent_cols={
            "base_return", "kijun_return", "cloud_return", "combo_return", "combo_adx_return",
            "base_fail4", "combo_fail4", "combo_adx_fail4", "combo_retention", "combo_adx_retention",
            "combo_winner_trunc", "combo_adx_winner_trunc", "combo_pos_ratio", "combo_adx_pos_ratio"
        },
    )
    report_body += "<h2>overall summary</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_failure_4bars_rate", "mean_failure_8bars_rate", "mean_winner_truncation_rate"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0},
    )
    report_body += "<h2>asset-level summary</h2>" + render_table(
        asset_df,
        percent_cols={"trade_count_retention", "signal_retention", "total_return", "avg_net_ret", "win_rate", "failure_4bars_rate", "failure_8bars_rate", "winner_truncation_rate"},
        digits_cols={"trades": 0, "base_signals": 0, "admitted_signals": 0, "cost_bps_per_side": 0},
    )
    report_body += "<h2>time pockets</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 1},
    )
    write_html(SITE_DIR / "report.html", "Rank 59 clean replication", report_body)

    reading_body = summary_card
    reading_body += "<div class='card'><h2>当前更直白的读法</h2><p>如果这层 Ichimoku gate 真有用，它应该至少做到两件事之一：一是在不明显砍掉 trade count 的前提下减少 4~8 bar 早衰；二是在多条 archetype 上比 base 更少亏。若它只是把样本筛得更漂亮，但把 base 赢家一起切掉，那就该尽快 park。</p></div>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_failure_4bars_rate", "mean_failure_8bars_rate", "mean_winner_truncation_rate"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>"
    write_html(READING_DIR / "rank59_ichimoku_kijun_cloud_clean_replication.html", "Rank 59 clean replication", reading_body)

    update_todo(compare_df, verdict, generated_at, latest_p3_appends)
    print(f"verdict={verdict}")


if __name__ == "__main__":
    main()
