#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank68_block_mitigation_retest_score_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank68_block_mitigation_retest_score_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank68_block_mitigation_retest_score_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "plus_block_length", "plus_block_length_and_range", "plus_full_block_score"]
PRIMARY_VARIANT = "plus_full_block_score"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
TARGET_BARS = 12
LOOKBACK_MIN = 3
LOOKBACK_MAX = 10
MAX_BLOCK_RANGE_ATR = 2.8
MAX_BODY_MEDIAN = 0.6
MAX_DRIFT_SHARE = 0.45
MIN_BLOCK_LENGTH = 4
MIN_BLOCK_RANGE_PCT = 0.0015
MIN_BLOCK_VOL_RATIO = 1.0
MAX_RETEST_DEPTH = 0.6

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }
.card { border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 18px 20px; margin: 16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
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


def add_base_setup_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema9"] = out["close"].ewm(span=9, adjust=False).mean()
    out["ema15"] = out["close"].ewm(span=15, adjust=False).mean()
    out["ema_slope"] = out["ema9"].pct_change(3)
    out["vol_ma20"] = out["volume"].rolling(20, min_periods=20).mean()
    out["atr14"] = compute_atr(out)
    out["psar"] = compute_psar(out)
    out["rolling_low20"] = out["low"].rolling(20, min_periods=20).min().shift(1)
    out["swing_high_30"] = out["high"].rolling(30, min_periods=30).max().shift(1)
    out["swing_low_30"] = out["low"].rolling(30, min_periods=30).min().shift(1)
    rng = out["swing_high_30"] - out["swing_low_30"]
    out["fib_618"] = out["swing_high_30"] - 0.618 * rng
    out["fib_50"] = out["swing_high_30"] - 0.5 * rng
    out["ema_psar_long_signal"] = (
        (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0.0003)
        & (out["psar"] < out["close"])
        & (out["close"] > out["high"].shift(1))
        & (out["close"].shift(1) < out["ema9"].shift(1))
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    out["fib_retest_long_signal"] = (
        out["fib_618"].notna()
        & (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0)
        & (out["close"] > out["fib_618"])
        & (out["close"].shift(1) <= out["fib_618"].shift(1))
        & (out["low"] <= out["fib_618"] + 0.2 * out["atr14"])
        & (out["close"] > out["fib_50"])
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    low = out["rolling_low20"]
    atr = out["atr14"]
    out["breakout_short_signal"] = (
        low.notna()
        & (out["ema9"] < out["ema15"])
        & (out["ema_slope"] < -0.0003)
        & (out["close"].shift(1) > low.shift(1))
        & (out["close"].shift(2) > low.shift(2))
        & (out["close"] < low - 0.1 * atr)
        & (out["high"] <= low + 0.3 * atr)
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    return out


def detect_block_features(df: pd.DataFrame, signal_idx: int, direction: str) -> dict[str, object]:
    if signal_idx < LOOKBACK_MIN + 2:
        return {
            "has_block": False,
            "block_length": np.nan,
            "block_range_pct": np.nan,
            "block_vol_ratio": np.nan,
            "retest_depth": np.nan,
            "zone_low": np.nan,
            "zone_high": np.nan,
            "block_score": np.nan,
        }
    atr_signal = float(df.iloc[signal_idx]["atr14"]) if pd.notna(df.iloc[signal_idx]["atr14"]) else np.nan
    if pd.isna(atr_signal) or atr_signal <= 0:
        return {
            "has_block": False,
            "block_length": np.nan,
            "block_range_pct": np.nan,
            "block_vol_ratio": np.nan,
            "retest_depth": np.nan,
            "zone_low": np.nan,
            "zone_high": np.nan,
            "block_score": np.nan,
        }

    best: dict[str, object] | None = None
    for length in range(LOOKBACK_MAX, LOOKBACK_MIN - 1, -1):
        start = signal_idx - length
        end = signal_idx - 1
        if start < 0:
            continue
        window = df.iloc[start : end + 1].copy()
        zone_low = float(window["low"].min())
        zone_high = float(window["high"].max())
        zone_size = zone_high - zone_low
        if zone_size <= 0:
            continue
        range_atr = zone_size / atr_signal
        body_pct = ((window["close"] - window["open"]).abs() / (window["high"] - window["low"]).replace(0, np.nan)).fillna(0.0)
        drift_share = abs(float(window.iloc[-1]["close"] - window.iloc[0]["open"])) / zone_size
        if range_atr > MAX_BLOCK_RANGE_ATR:
            continue
        if float(body_pct.median()) > MAX_BODY_MEDIAN:
            continue
        if drift_share > MAX_DRIFT_SHARE:
            continue
        avg_vol_ratio = float((window["volume"] / window["vol_ma20"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan).mean())
        signal_bar = df.iloc[signal_idx]
        close_px = float(signal_bar["close"])
        low_px = float(signal_bar["low"])
        high_px = float(signal_bar["high"])
        if direction == "long":
            depth = max(0.0, zone_high - low_px) / zone_size if low_px < zone_high else 0.0
            close_ok = close_px >= zone_high
        else:
            depth = max(0.0, high_px - zone_low) / zone_size if high_px > zone_low else 0.0
            close_ok = close_px <= zone_low
        score = (
            min(length / 8.0, 1.5)
            + min((zone_size / float(signal_bar["close"])) / 0.003, 1.5)
            + min((avg_vol_ratio if pd.notna(avg_vol_ratio) else 0.0) / 1.2, 1.2)
            + max(0.0, 1.0 - min(depth, 1.0))
            + (0.25 if close_ok else 0.0)
        )
        best = {
            "has_block": True,
            "block_length": int(length),
            "block_range_pct": zone_size / float(signal_bar["close"]),
            "block_vol_ratio": avg_vol_ratio,
            "retest_depth": depth,
            "zone_low": zone_low,
            "zone_high": zone_high,
            "block_score": score,
        }
        break

    if best is None:
        return {
            "has_block": False,
            "block_length": np.nan,
            "block_range_pct": np.nan,
            "block_vol_ratio": np.nan,
            "retest_depth": np.nan,
            "zone_low": np.nan,
            "zone_high": np.nan,
            "block_score": np.nan,
        }
    return best


def build_signal_frame(df: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    signal_col = f"{setup}_signal"
    sig_idx = np.flatnonzero(df[signal_col].to_numpy())
    rows: list[dict[str, object]] = []
    for idx in sig_idx:
        row = df.iloc[idx]
        direction = "long" if setup in LONG_SETUPS else "short"
        block = detect_block_features(df, int(idx), direction)
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "direction": direction,
                "signal_index": int(idx),
                "timestamp": row["timestamp"],
                "signal_close": float(row["close"]),
                "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else np.nan,
                **block,
            }
        )
    return pd.DataFrame(rows)


def variant_gate(sig: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "plus_block_length":
        return bool(sig["has_block"]) and float(sig["block_length"] or 0) >= MIN_BLOCK_LENGTH
    if variant == "plus_block_length_and_range":
        return (
            bool(sig["has_block"])
            and float(sig["block_length"] or 0) >= MIN_BLOCK_LENGTH
            and pd.notna(sig["block_range_pct"])
            and float(sig["block_range_pct"]) >= MIN_BLOCK_RANGE_PCT
        )
    if variant == "plus_full_block_score":
        return (
            bool(sig["has_block"])
            and float(sig["block_length"] or 0) >= MIN_BLOCK_LENGTH
            and pd.notna(sig["block_range_pct"])
            and float(sig["block_range_pct"]) >= MIN_BLOCK_RANGE_PCT
            and pd.notna(sig["block_vol_ratio"])
            and float(sig["block_vol_ratio"]) >= MIN_BLOCK_VOL_RATIO
            and pd.notna(sig["retest_depth"])
            and float(sig["retest_depth"]) <= MAX_RETEST_DEPTH
        )
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, sigs: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    admitted = 0
    active_until: pd.Timestamp | None = None
    cost_rate = float(cost_bps) / 10000.0

    for _, sig in sigs.iterrows():
        if not variant_gate(sig, variant):
            continue
        admitted += 1
        signal_idx = int(sig["signal_index"])
        entry_idx = signal_idx + 1
        if entry_idx >= len(frame):
            continue
        entry_ts = pd.Timestamp(frame.iloc[entry_idx]["timestamp"])
        if active_until is not None and entry_ts <= active_until:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        path_end_idx = min(len(frame) - 1, entry_idx + TARGET_BARS - 1)
        if exit_idx <= entry_idx:
            continue

        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        direction = 1.0 if sig["direction"] == "long" else -1.0
        atr = float(sig["atr14"]) if pd.notna(sig["atr14"]) else np.nan
        zone_low = float(sig["zone_low"]) if pd.notna(sig["zone_low"]) else np.nan
        zone_high = float(sig["zone_high"]) if pd.notna(sig["zone_high"]) else np.nan
        future = frame.iloc[entry_idx : path_end_idx + 1].copy()
        target_px = np.nan
        target_hit_8 = np.nan
        target_hit_12 = np.nan
        failure_before_target = np.nan

        if pd.notna(atr) and atr > 0 and pd.notna(zone_low) and pd.notna(zone_high):
            if sig["direction"] == "long":
                target_px = entry_px + atr
                target_hit_8 = bool((frame.iloc[entry_idx : exit_idx + 1]["high"] >= target_px).any())
                target_hit_12 = bool((future["high"] >= target_px).any())
                fail_hits = future.index[future["low"] <= zone_low].tolist()
                target_hits = future.index[future["high"] >= target_px].tolist()
            else:
                target_px = entry_px - atr
                target_hit_8 = bool((frame.iloc[entry_idx : exit_idx + 1]["low"] <= target_px).any())
                target_hit_12 = bool((future["low"] <= target_px).any())
                fail_hits = future.index[future["high"] >= zone_high].tolist()
                target_hits = future.index[future["low"] <= target_px].tolist()
            first_fail = fail_hits[0] if fail_hits else None
            first_target = target_hits[0] if target_hits else None
            failure_before_target = bool(first_fail is not None and (first_target is None or first_fail <= first_target))

        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "signal_time": sig["timestamp"],
                "entry_time": entry_ts,
                "exit_time": pd.Timestamp(frame.iloc[exit_idx]["timestamp"]),
                "direction": sig["direction"],
                "cost_bps_per_side": float(cost_bps),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_return": gross_ret,
                "net_return": net_ret,
                "block_length": sig["block_length"],
                "block_range_pct": sig["block_range_pct"],
                "block_vol_ratio": sig["block_vol_ratio"],
                "retest_depth": sig["retest_depth"],
                "target_hit_8bars": target_hit_8,
                "target_hit_12bars": target_hit_12,
                "failure_before_target": failure_before_target,
            }
        )
        active_until = pd.Timestamp(frame.iloc[exit_idx]["timestamp"])

    return pd.DataFrame(rows), admitted


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int, base_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trades_n = int(len(trades))
    total_return = float(trades["net_return"].sum()) if not trades.empty else np.nan
    avg_net = float(trades["net_return"].mean()) if not trades.empty else np.nan
    fail_rate = float(trades["failure_before_target"].mean()) if not trades.empty and trades["failure_before_target"].notna().any() else np.nan
    target8 = float(trades["target_hit_8bars"].mean()) if not trades.empty and trades["target_hit_8bars"].notna().any() else np.nan
    target12 = float(trades["target_hit_12bars"].mean()) if not trades.empty and trades["target_hit_12bars"].notna().any() else np.nan
    mean_block_length = float(trades["block_length"].mean()) if not trades.empty else np.nan
    mean_retest_depth = float(trades["retest_depth"].mean()) if not trades.empty else np.nan
    trade_retention = np.nan
    if base_trades is not None:
        base_n = len(base_trades)
        trade_retention = float(trades_n / base_n) if base_n else np.nan
    signal_retention = float(admitted_signals / base_signals) if base_signals else np.nan
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "trades": trades_n,
        "trade_count_retention": trade_retention,
        "signal_retention": signal_retention,
        "total_return": total_return,
        "avg_net_ret": avg_net,
        "failure_before_target_rate": fail_rate,
        "target_hit_8bars_rate": target8,
        "target_hit_12bars_rate": target12,
        "mean_block_length": mean_block_length,
        "mean_retest_depth": mean_retest_depth,
    }


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["total_return"].mean()) if not grp.empty else np.nan,
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()) if not grp.empty else np.nan,
                "mean_trades": float(grp["trades"].mean()) if not grp.empty else np.nan,
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if not grp.empty else np.nan,
                "mean_signal_retention": float(grp["signal_retention"].mean()) if not grp.empty else np.nan,
                "mean_failure_before_target_rate": float(grp["failure_before_target_rate"].mean()) if not grp.empty else np.nan,
                "mean_target_hit_8bars_rate": float(grp["target_hit_8bars_rate"].mean()) if not grp.empty else np.nan,
                "mean_target_hit_12bars_rate": float(grp["target_hit_12bars_rate"].mean()) if not grp.empty else np.nan,
                "mean_block_length": float(grp["mean_block_length"].mean()) if not grp.empty else np.nan,
                "mean_retest_depth": float(grp["mean_retest_depth"].mean()) if not grp.empty else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "cost_bps_per_side", "variant"]).reset_index(drop=True)


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    rows: list[dict[str, object]] = []
    for variant, grp in trades.groupby("variant", dropna=False):
        grp = grp.sort_values("entry_time").reset_index(drop=True)
        if len(grp) < 3:
            continue
        buckets = pd.qcut(np.arange(len(grp)), 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        grp = grp.assign(time_bucket=buckets)
        by_asset = grp.groupby(["time_bucket", "asset"], dropna=False).agg(total_return=("net_return", "sum"), trades=("net_return", "size")).reset_index()
        summary = by_asset.groupby("time_bucket", dropna=False).agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        ).reset_index()
        summary["variant"] = variant
        rows.extend(summary.to_dict("records"))
    return pd.DataFrame(rows)


def build_feature_board(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame(columns=["setup", "has_block_ratio", "mean_block_length", "mean_block_range_pct", "mean_block_vol_ratio", "mean_retest_depth"])
    work = signals.copy()
    rows: list[dict[str, object]] = []
    for setup, grp in work.groupby("setup", dropna=False):
        rows.append(
            {
                "setup": setup,
                "has_block_ratio": float(grp["has_block"].mean()),
                "mean_block_length": float(grp.loc[grp["has_block"], "block_length"].mean()) if grp["has_block"].any() else np.nan,
                "mean_block_range_pct": float(grp.loc[grp["has_block"], "block_range_pct"].mean()) if grp["has_block"].any() else np.nan,
                "mean_block_vol_ratio": float(grp.loc[grp["has_block"], "block_vol_ratio"].mean()) if grp["has_block"].any() else np.nan,
                "mean_retest_depth": float(grp.loc[grp["has_block"], "retest_depth"].mean()) if grp["has_block"].any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    target = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        subset = target[target["setup"] == setup].set_index("variant")
        if "base" not in subset.index:
            continue
        row = {"setup": setup}
        for variant, prefix in [
            ("base", "base"),
            ("plus_block_length", "len"),
            ("plus_block_length_and_range", "len_range"),
            ("plus_full_block_score", "full"),
        ]:
            if variant in subset.index:
                r = subset.loc[variant]
                row[f"{prefix}_return"] = r.get("mean_total_return")
                row[f"{prefix}_retention"] = r.get("mean_trade_count_retention")
                row[f"{prefix}_signal_retention"] = r.get("mean_signal_retention")
                row[f"{prefix}_failure"] = r.get("mean_failure_before_target_rate")
                row[f"{prefix}_target8"] = r.get("mean_target_hit_8bars_rate")
                row[f"{prefix}_target12"] = r.get("mean_target_hit_12bars_rate")
                row[f"{prefix}_positive_asset_ratio"] = r.get("positive_asset_ratio")
        rows.append(row)
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    if compare.empty:
        return (
            "park / evidence pool",
            "暂无可比样本。",
            "这次最小 clean replication 连可比 setup 都没形成，不该继续占默认 Scout 预算。",
        )
    wins = 0
    strong_wins = 0
    for _, row in compare.iterrows():
        improved = (
            pd.notna(row.get("full_return"))
            and pd.notna(row.get("base_return"))
            and pd.notna(row.get("full_retention"))
            and float(row["full_retention"]) >= 0.45
            and (
                float(row["full_return"]) > float(row["base_return"]) + 0.002
                or (
                    pd.notna(row.get("full_failure"))
                    and pd.notna(row.get("base_failure"))
                    and float(row["full_failure"]) < float(row["base_failure"]) - 0.03
                )
                or (
                    pd.notna(row.get("full_target12"))
                    and pd.notna(row.get("base_target12"))
                    and float(row["full_target12"]) > float(row["base_target12"]) + 0.03
                )
            )
        )
        if improved:
            wins += 1
            if float(row.get("full_positive_asset_ratio", 0.0) or 0.0) >= (2 / 3):
                strong_wins += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r.get('base_return'))} / L≈{pct(r.get('len_return'))} / L+R≈{pct(r.get('len_range_return'))} / full≈{pct(r.get('full_return'))}"
        for _, r in compare.iterrows()
    )
    if wins >= 2 and strong_wins >= 1:
        return (
            "P2 paper candidate / evidence queue",
            headline,
            "这次最小 clean replication 说明 block 长度/厚度/回踩深度 这层结构评分，已经不只是砍样本，而是在多条 archetype 上开始形成 shared retest-quality gate 的味道，值得先升到 P2。",
        )
    if wins >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 说明 block-mitigation score 在部分 archetype 上有 shared retest-quality gate 的味道，但改善还不够统一；更诚实的读法仍是先留在 P1 证据池。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在说明：单靠 block length / block range / retest depth 这层便宜结构评分，还不足以稳定改善当前三条 archetype 的成本后质量，不该继续占默认 Scout 主资源位。",
    )


def render_factor_page(overall: pd.DataFrame, asset_summary: pd.DataFrame, compare: pd.DataFrame, pockets: pd.DataFrame, feature_board: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup", "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_count_retention", "mean_signal_retention", "mean_failure_before_target_rate", "mean_target_hit_8bars_rate",
        "mean_target_hit_12bars_rate", "mean_block_length", "mean_retest_depth"
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset", "setup", "variant", "trades", "trade_count_retention", "signal_retention", "total_return",
        "failure_before_target_rate", "target_hit_8bars_rate", "target_hit_12bars_rate", "mean_block_length", "mean_retest_depth"
    ]].copy()
    compare_view = compare[[
        "setup", "base_return", "len_return", "len_range_return", "full_return",
        "base_retention", "len_retention", "len_range_retention", "full_retention",
        "base_failure", "len_failure", "len_range_failure", "full_failure",
        "base_target12", "len_target12", "len_range_target12", "full_target12"
    ]].copy()
    return f"""
<p><a href='../../reading/repo_scout/rank68_block_mitigation_retest_score_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 68 · block-mitigation retest score（minimal clean replication）</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m 本地 cache；执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>，并额外统计 <code>target-hit within 12 bars</code> 与 <code>failure-before-target</code>。</p>

<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <p>当 <code>EMA = waiting_not_due</code> 时，Rank 68 只拿 1 次最小预算：<b>给当前三条 archetype 叠上一层 block 长度/厚度/回踩深度的 shared retest-quality gate</b>，能不能在保留可接受 trade count 的前提下，降低 <code>failure-before-target</code> 并提高 <code>target-hit within 8/12 bars</code>？</p>
  <ul>
    <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li><b>四臂：</b><code>base</code>、<code>plus_block_length</code>、<code>plus_block_length_and_range</code>、<code>plus_full_block_score</code>。</li>
    <li><b>最小 block 定义：</b>在信号前找最近 <code>3~10</code> 根 closed bars 的压缩块，要求 <code>zone_range / ATR <= {MAX_BLOCK_RANGE_ATR}</code>、<code>median_body_pct <= {MAX_BODY_MEDIAN}</code>、<code>drift_share <= {MAX_DRIFT_SHARE}</code>。</li>
    <li><b>最小 full gate：</b><code>L >= {MIN_BLOCK_LENGTH}</code>、<code>range_pct >= {MIN_BLOCK_RANGE_PCT:.4f}</code>、<code>vol_ratio >= {MIN_BLOCK_VOL_RATIO:.1f}</code>、<code>retest_depth <= {MAX_RETEST_DEPTH:.1f}</code>。</li>
  </ul>
</div>

<div class='card'>
  <h2>硬结论</h2>
  <p><span class='pill'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>

<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','len_return','len_range_return','full_return','base_retention','len_retention','len_range_retention','full_retention','base_failure','len_failure','len_range_failure','full_failure','base_target12','len_target12','len_range_target12','full_target12'})}
</div>

<div class='card'>
  <h2>overall summary</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_signal_retention','mean_failure_before_target_rate','mean_target_hit_8bars_rate','mean_target_hit_12bars_rate','mean_retest_depth'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1,'mean_block_length':2})}
</div>

<div class='card'>
  <h2>asset summary（6bps）</h2>
  {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','failure_before_target_rate','target_hit_8bars_rate','target_hit_12bars_rate','mean_retest_depth'}, digits_cols={'trades':0,'mean_block_length':2})}
</div>

<div class='card'>
  <h2>signal-level block feature board</h2>
  {render_table(feature_board, percent_cols={'has_block_ratio','mean_block_range_pct','mean_retest_depth'})}
</div>

<div class='card'>
  <h2>time pockets</h2>
  {render_table(pockets, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades':1})}
</div>
"""


def render_reading_page(compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    compare_view = compare[[
        "setup", "base_return", "len_return", "len_range_return", "full_return",
        "base_retention", "len_retention", "len_range_retention", "full_retention",
        "base_failure", "len_failure", "len_range_failure", "full_failure",
        "base_target12", "len_target12", "len_range_target12", "full_target12"
    ]].copy()
    return f"""
<p><a href='rank68_block_mitigation_retest_score_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 68 · block-mitigation retest score clean replication</h1>
<div class='card'>
  <span class='pill'>更新时间：{escape(generated_at)}</span>
  <span class='pill'>类型：minimal clean replication</span>
  <span class='pill'>当前 verdict：{escape(verdict)}</span>
  <p class='muted'>artifact：<code>reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/overall_summary.csv</code></p>
</div>
<div class='card'>
  <h2>一句话结果</h2>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>
<div class='card'>
  <h2>这轮冻结的最小实验</h2>
  <ul>
    <li><code>BTC/ETH/SOL</code>，复用 120d 15m 本地 cache，不追新 bar，不做重型下载。</li>
    <li>只比较四臂：<code>base</code>、<code>plus_block_length</code>、<code>plus_block_length_and_range</code>、<code>plus_full_block_score</code>。</li>
    <li>执行统一：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</li>
    <li>首轮只看：<code>post-cost return</code>、<code>trade count retention</code>、<code>failure-before-target</code>、<code>target-hit within 8/12 bars</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','len_return','len_range_return','full_return','base_retention','len_retention','len_range_retention','full_retention','base_failure','len_failure','len_range_failure','full_failure','base_target12','len_target12','len_range_target12','full_target12'})}
</div>
"""


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "\n### Next 3 bot3 runs（当前默认执行顺序）"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    compare = compare.set_index("setup")
    row_ema = compare.loc["ema_psar_long"]
    row_fib = compare.loc["fib_retest_long"]
    row_short = compare.loc["breakout_short"]
    insert_block = f"""
- **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`。因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity，按权威顺序这轮执行 **`Run 2 / Rank 68 minimal clean replication`**。
  - 这轮已把 `Rank 68 / block-mitigation retest score` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，只在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`plus_block_length`、`plus_block_length_and_range`、`plus_full_block_score` 四臂；执行统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**，并额外统计 `target-hit within 12 bars` 与 `failure-before-target`。
  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `L≈{pct(row_ema['len_return'])}`、`L+R≈{pct(row_ema['len_range_return'])}`、`full≈{pct(row_ema['full_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `L≈{pct(row_fib['len_return'])}`、`L+R≈{pct(row_fib['len_range_return'])}`、`full≈{pct(row_fib['full_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `L≈{pct(row_short['len_return'])}`、`L+R≈{pct(row_short['len_range_return'])}`、`full≈{pct(row_short['full_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 68 / block-mitigation retest score = {verdict}`**。
  - reader-facing 落点：`reports/site/factors/scout_rank68_block_mitigation_retest_score_15m/report.html`、`reports/site/reading/repo_scout/rank68_block_mitigation_retest_score_clean_replication.html`；artifact：`reports/artifacts/scout_rank68_block_mitigation_retest_score_15m/overall_summary.csv`、`setup_compare.csv`。
  - 当前更诚实的 active Scout 顺序应更新为：**fresh source intake（先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source） > Rank 35b > Rank 16b > tiny-live plumbing**（`Rank 68` 本轮已消耗完允许的那次 minimal clean replication；若 verdict 仍不足以升层，就不该继续赖在 fast-lane 队首）。
  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 68 verdict 不足以升到下一层，则继续按 7.10 先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source` -> `Run 3 = 若新的 fresh source 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。
"""
    text = text.replace(marker, f"\n{insert_block}{marker}", 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    signal_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    base_cache: dict[tuple[str, str, float], pd.DataFrame] = {}
    admitted_cache: dict[tuple[str, str, float, str], int] = {}

    for asset, symbol in ASSETS.items():
        bars = add_base_setup_signals(load_bars(symbol, asset))
        for setup in SETUPS:
            sigs = build_signal_frame(bars, asset, setup)
            if not sigs.empty:
                signal_frames.append(sigs)
            base_signals = int(len(sigs))
            for cost in COSTS:
                base_trades, base_admitted = build_trades(bars, sigs, "base", cost)
                base_cache[(asset, setup, cost)] = base_trades
                admitted_cache[(asset, setup, cost, "base")] = base_admitted
                if not base_trades.empty:
                    trade_frames.append(base_trades)
            for variant in VARIANTS:
                for cost in COSTS:
                    if variant == "base":
                        trades = base_cache[(asset, setup, cost)]
                        admitted = admitted_cache[(asset, setup, cost, variant)]
                    else:
                        trades, admitted = build_trades(bars, sigs, variant, cost)
                        admitted_cache[(asset, setup, cost, variant)] = admitted
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
                            base_trades=base_cache[(asset, setup, cost)],
                        )
                    )

    all_signals = pd.concat(signal_frames, ignore_index=True) if signal_frames else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 68 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary = pd.DataFrame(asset_rows)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall = build_overall(asset_summary)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pockets.csv", index=False)
    feature_board = build_feature_board(all_signals)
    feature_board.to_csv(ART_DIR / "feature_board.csv", index=False)
    compare = build_setup_compare(overall)
    compare.to_csv(ART_DIR / "setup_compare.csv", index=False)

    verdict, headline, reason = build_verdict(compare)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    factor_body = render_factor_page(overall, asset_summary, compare, pockets, feature_board, verdict, headline, reason, generated_at)
    write_html(SITE_DIR / "report.html", "Rank 68 · block-mitigation retest score clean replication", factor_body)
    reading_body = render_reading_page(compare, verdict, headline, reason, generated_at)
    write_html(READING_PATH, "Rank 68 · block-mitigation clean replication", reading_body)
    update_todo(compare, verdict, generated_at)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"headline={headline}")


if __name__ == "__main__":
    main()
