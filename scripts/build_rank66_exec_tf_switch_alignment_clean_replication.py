#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank66_exec_tf_switch_alignment_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank66_exec_tf_switch_alignment_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base_15m_only", "always_5m_confirm", "alignment_switch", "alignment_switch_plus_pressure"]
PRIMARY_VARIANT = "alignment_switch"
STRICT_VARIANT = "alignment_switch_plus_pressure"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_MINUTES = 120
EARLY_FAIL_MINUTES = 60
BINANCE_LIMIT = 1000
PAGES_5M = 36
REQ_TIMEOUT = 20
BOS_LOOKBACK_15M = 20
BOS_LOOKBACK_5M = 36
BODY_PRESSURE_FLOOR = 0.55
EMA_ALIGN = 200

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


def load_15m_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_5m_spot(symbol: str) -> pd.DataFrame:
    cache_path = ensure_dir(ART_DIR / "spot_cache") / f"{symbol}_120d_5m.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df.sort_values("timestamp").reset_index(drop=True)

    url = "https://api.binance.com/api/v3/klines"
    rows: list[list[object]] = []
    end_time: int | None = None
    for _ in range(PAGES_5M):
        params: dict[str, object] = {"symbol": symbol, "interval": "5m", "limit": BINANCE_LIMIT}
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(url, params=params, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = int(batch[0][0])
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "count", "taker_buy_base", "taker_buy_quote", "ignore",
    ])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    out = df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    out.to_csv(cache_path, index=False)
    return out


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    out = (
        df.set_index("timestamp")
        .resample(rule, label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return out


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


def add_bos_columns(df: pd.DataFrame, lookback: int) -> pd.DataFrame:
    out = df.copy()
    out["bos_high"] = out["high"].rolling(lookback, min_periods=lookback).max().shift(1)
    out["bos_low"] = out["low"].rolling(lookback, min_periods=lookback).min().shift(1)
    body = (out["close"] - out["open"]).abs()
    rng = (out["high"] - out["low"]).replace(0, np.nan)
    out["body_pct"] = (body / rng).fillna(0.0)
    out["vol_ma20"] = out["volume"].rolling(20, min_periods=20).mean()
    out["pressure"] = ((out["body_pct"] >= BODY_PRESSURE_FLOOR) & (out["volume"] > out["vol_ma20"])).fillna(False)
    out["bos_long"] = (out["close"] > out["bos_high"]).fillna(False)
    out["bos_short"] = (out["close"] < out["bos_low"]).fillna(False)
    return out


def build_alignment_table(df_15m: pd.DataFrame, df_5m: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    h1 = resample_ohlcv(df_5m, "1h")
    h4 = resample_ohlcv(df_5m, "4h")
    h1["ema200"] = h1["close"].ewm(span=EMA_ALIGN, adjust=False).mean()
    h4["ema200"] = h4["close"].ewm(span=EMA_ALIGN, adjust=False).mean()
    h1["trend_long"] = (h1["close"] > h1["ema200"]).fillna(False)
    h1["trend_short"] = (h1["close"] < h1["ema200"]).fillna(False)
    h4["bias_long"] = (h4["close"] > h4["ema200"]).fillna(False)
    h4["bias_short"] = (h4["close"] < h4["ema200"]).fillna(False)
    align = df_15m[["timestamp"]].copy()
    align = pd.merge_asof(align.sort_values("timestamp"), h1[["timestamp", "trend_long", "trend_short"]].sort_values("timestamp"), on="timestamp", direction="backward")
    align = pd.merge_asof(align.sort_values("timestamp"), h4[["timestamp", "bias_long", "bias_short"]].sort_values("timestamp"), on="timestamp", direction="backward")
    align["aligned_long"] = (align["trend_long"] & align["bias_long"]).fillna(False)
    align["aligned_short"] = (align["trend_short"] & align["bias_short"]).fillna(False)
    return align, h1, h4


def build_signal_frame(df15: pd.DataFrame, df5: pd.DataFrame, align: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    col = f"{setup}_signal"
    sigs = df15.loc[df15[col], ["timestamp"]].copy()
    if sigs.empty:
        return pd.DataFrame()
    direction = "long" if setup in LONG_SETUPS else "short"
    sigs["asset"] = asset
    sigs["setup"] = setup
    sigs["direction"] = direction
    sigs = pd.merge_asof(sigs.sort_values("timestamp"), align.sort_values("timestamp"), on="timestamp", direction="backward")
    sigs = pd.merge_asof(
        sigs.sort_values("timestamp"),
        df15[["timestamp", "bos_long", "bos_short", "pressure", "close"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    df5_now = df5.rename(columns={
        "timestamp": "timestamp_5m",
        "bos_long": "bos_long_5m",
        "bos_short": "bos_short_5m",
        "pressure": "pressure_5m",
        "open": "open_5m",
        "close": "close_5m",
    })
    sigs = pd.merge_asof(
        sigs.sort_values("timestamp"),
        df5_now[["timestamp_5m", "bos_long_5m", "bos_short_5m", "pressure_5m", "open_5m", "close_5m"]].sort_values("timestamp_5m"),
        left_on="timestamp",
        right_on="timestamp_5m",
        direction="backward",
    )
    if direction == "long":
        sigs["aligned"] = sigs["aligned_long"].fillna(False)
        sigs["bos_15m"] = sigs["bos_long"].fillna(False)
        sigs["bos_5m"] = sigs["bos_long_5m"].fillna(False)
    else:
        sigs["aligned"] = sigs["aligned_short"].fillna(False)
        sigs["bos_15m"] = sigs["bos_short"].fillna(False)
        sigs["bos_5m"] = sigs["bos_short_5m"].fillna(False)
    sigs["pressure_15m"] = sigs["pressure"].fillna(False)
    sigs["pressure_5m"] = sigs["pressure_5m"].fillna(False)
    return sigs.reset_index(drop=True)


def variant_gate(row: pd.Series, variant: str) -> tuple[bool, str]:
    if variant == "base_15m_only":
        return bool(row["bos_15m"]), "15m"
    if variant == "always_5m_confirm":
        return bool(row["bos_5m"]), "5m"
    if variant == "alignment_switch":
        tf = "5m" if bool(row["aligned"]) else "15m"
        return (bool(row["bos_5m"]) if tf == "5m" else bool(row["bos_15m"])), tf
    if variant == "alignment_switch_plus_pressure":
        tf = "5m" if bool(row["aligned"]) else "15m"
        if tf == "5m":
            return bool(row["bos_5m"] and row["pressure_5m"]), tf
        return bool(row["bos_15m"] and row["pressure_15m"]), tf
    raise ValueError(variant)


def price_at_or_after(df: pd.DataFrame, ts: pd.Timestamp, col: str) -> tuple[pd.Timestamp | None, float | None, int | None]:
    rows = df.loc[df["timestamp"] >= ts]
    if rows.empty:
        return None, None, None
    idx = int(rows.index[0])
    row = rows.iloc[0]
    return pd.Timestamp(row["timestamp"]), float(row[col]), idx


def build_trades(df15: pd.DataFrame, df5: pd.DataFrame, sigs: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    active_until: pd.Timestamp | None = None
    admitted = 0
    for _, sig in sigs.iterrows():
        allowed, tf = variant_gate(sig, variant)
        if not allowed:
            continue
        admitted += 1
        step = 5 if tf == "5m" else 15
        frame = df5 if tf == "5m" else df15
        entry_ts, entry_px, entry_idx = price_at_or_after(frame, sig["timestamp"] + pd.Timedelta(minutes=step), "open")
        if entry_ts is None or entry_px is None or entry_idx is None:
            continue
        if active_until is not None and entry_ts <= active_until:
            continue
        early_ts, early_px, _ = price_at_or_after(frame, entry_ts + pd.Timedelta(minutes=EARLY_FAIL_MINUTES), "close")
        exit_ts, exit_px, _ = price_at_or_after(frame, entry_ts + pd.Timedelta(minutes=HOLD_MINUTES), "close")
        if exit_ts is None or exit_px is None:
            continue
        direction = 1.0 if sig["direction"] == "long" else -1.0
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = gross_ret - 2.0 * (cost_bps / 10000.0)
        early_gross = np.nan
        if early_px is not None:
            early_gross = direction * ((early_px / entry_px) - 1.0)
        rows.append(
            {
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "exec_tf": tf,
                "aligned": bool(sig["aligned"]),
                "signal_time": sig["timestamp"],
                "entry_time": entry_ts,
                "exit_time": exit_ts,
                "entry_price": entry_px,
                "exit_price": exit_px,
                "direction": sig["direction"],
                "cost_bps_per_side": cost_bps,
                "gross_return": gross_ret,
                "net_return": net_ret,
                "early_return_60m": early_gross,
                "used_pressure": bool(variant == STRICT_VARIANT),
            }
        )
        active_until = exit_ts
    return pd.DataFrame(rows), admitted


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int, base_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trades = trades.copy()
    total_return = float(trades["net_return"].sum()) if not trades.empty else np.nan
    trades_n = int(len(trades))
    win_rate = float((trades["net_return"] > 0).mean()) if not trades.empty else np.nan
    avg_net = float(trades["net_return"].mean()) if not trades.empty else np.nan
    early_fail = float((trades["early_return_60m"] <= 0).mean()) if not trades.empty else np.nan
    exec_5m_share = float((trades["exec_tf"] == "5m").mean()) if not trades.empty else np.nan
    trade_retention = np.nan
    if base_trades is not None:
        base_n = len(base_trades)
        trade_retention = float(trades_n / base_n) if base_n else np.nan
    signal_retention = float(admitted_signals / base_signals) if base_signals else np.nan
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": cost_bps,
        "base_signals": base_signals,
        "admitted_signals": admitted_signals,
        "trades": trades_n,
        "trade_count_retention": trade_retention,
        "signal_retention": signal_retention,
        "total_return": total_return,
        "avg_net_ret": avg_net,
        "win_rate": win_rate,
        "early_fail_60m_rate": early_fail,
        "exec_5m_share": exec_5m_share,
    }


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    work = trades.copy()
    work = work.sort_values(["variant", "entry_time"]).reset_index(drop=True)
    rows: list[dict[str, object]] = []
    for variant, grp in work.groupby("variant"):
        if grp.empty:
            continue
        idx = np.arange(len(grp))
        bucket = pd.qcut(idx, 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        grp = grp.assign(time_bucket=bucket)
        by_asset = (
            grp.groupby(["time_bucket", "asset"], dropna=False)
            .agg(total_return=("net_return", "sum"), trades=("net_return", "size"))
            .reset_index()
        )
        summary = (
            by_asset.groupby("time_bucket", dropna=False)
            .agg(
                mean_total_return=("total_return", "mean"),
                positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
                mean_trades=("trades", "mean"),
            )
            .reset_index()
        )
        summary["variant"] = variant
        rows.extend(summary.to_dict("records"))
    return pd.DataFrame(rows)


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    target = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    for setup in SETUPS:
        subset = target[target["setup"] == setup].set_index("variant")
        if "base_15m_only" not in subset.index:
            continue
        row = {"setup": setup}
        for variant, prefix in [
            ("base_15m_only", "base"),
            ("always_5m_confirm", "always5"),
            ("alignment_switch", "switch"),
            ("alignment_switch_plus_pressure", "switch_pressure"),
        ]:
            if variant in subset.index:
                r = subset.loc[variant]
                row[f"{prefix}_return"] = r.get("mean_total_return")
                row[f"{prefix}_retention"] = r.get("mean_trade_count_retention")
                row[f"{prefix}_signal_retention"] = r.get("mean_signal_retention")
                row[f"{prefix}_early_fail"] = r.get("mean_early_fail_60m_rate")
                row[f"{prefix}_positive_asset_ratio"] = r.get("positive_asset_ratio")
                row[f"{prefix}_exec_5m_share"] = r.get("mean_exec_5m_share")
        rows.append(row)
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    if compare.empty:
        return ("park / evidence pool", "暂无可用 setup compare。", "当前最小 replication 连可比样本都没形成，不该继续占默认 Scout 预算。")
    wins = 0
    strong_wins = 0
    for _, r in compare.iterrows():
        improved = (
            pd.notna(r.get("switch_return")) and pd.notna(r.get("base_return"))
            and pd.notna(r.get("switch_retention")) and pd.notna(r.get("switch_early_fail")) and pd.notna(r.get("base_early_fail"))
            and float(r["switch_retention"]) >= 0.55
            and (
                float(r["switch_return"]) > float(r["base_return"]) + 0.002
                or float(r["switch_early_fail"]) < float(r["base_early_fail"]) - 0.03
            )
        )
        if improved:
            wins += 1
            if float(r.get("switch_positive_asset_ratio", 0.0) or 0.0) >= (2/3):
                strong_wins += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r.get('base_return'))} / always5≈{pct(r.get('always5_return'))} / switch≈{pct(r.get('switch_return'))} / switch+pressure≈{pct(r.get('switch_pressure_return'))}"
        for _, r in compare.iterrows()
    )
    if wins >= 2 and strong_wins >= 1:
        return (
            "P2 paper candidate / evidence queue",
            headline,
            "这次最小 clean replication 至少说明：‘对齐时放宽到 5m、失配时坚持 15m’ 不是纯靠砍样本少亏，已经在多条 archetype 上给出 shared execution gate 的味道，值得先进入 paper-candidate 证据队列。",
        )
    if wins >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 说明 exec-TF switch 在部分 archetype 上有一点 shared execution gate 味道，但改善还不够统一；当前更诚实的读法是先留在 P1 证据池，而不是直接升格。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：单靠 exec-TF switch（对齐用 5m、失配守 15m）还不足以稳定改善三条 archetype 的成本后质量，不该继续占默认 Scout 主资源位。",
    )


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, pockets: pd.DataFrame, compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup", "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_count_retention", "mean_signal_retention", "mean_early_fail_60m_rate", "mean_exec_5m_share"
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset", "setup", "variant", "trades", "trade_count_retention", "signal_retention", "total_return", "early_fail_60m_rate", "exec_5m_share"
    ]].copy()
    compare_view = compare[[
        "setup", "base_return", "always5_return", "switch_return", "switch_pressure_return",
        "base_retention", "always5_retention", "switch_retention", "switch_pressure_retention",
        "base_early_fail", "always5_early_fail", "switch_early_fail", "switch_pressure_early_fail",
        "switch_positive_asset_ratio", "switch_pressure_positive_asset_ratio", "switch_exec_5m_share", "switch_pressure_exec_5m_share"
    ]].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 66 · exec-TF switch alignment gate clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.72; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th, td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/repo_scout/rank66_exec_tf_switch_alignment_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 66 · exec-TF switch alignment gate（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m cache + Binance spot 5m cache；4H/1H 从同一条 5m 数据 resample；执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 120m</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 66 只拿 1 次最小预算：<b>同向时让触发切到 5m、失配时坚持 15m</b> 这条 shared execution gate，能不能比一刀切的 <code>15m only</code> 或 <code>always 5m</code> 更诚实地改善三条 archetype 的成本后质量？</p>
    <ul>
      <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
      <li><b>四臂：</b><code>base_15m_only</code>、<code>always_5m_confirm</code>、<code>alignment_switch</code>、<code>alignment_switch_plus_pressure</code>。</li>
      <li><b>对齐定义：</b><code>4H bias</code> 与 <code>1H trend</code> 同向（都站上/跌破各自 <code>EMA200</code>）时，允许用 5m BOS；否则继续坚持 15m BOS。</li>
      <li><b>pressure：</b>只加最轻一脚：<code>bodyPct ≥ 0.55</code> 且 <code>volume &gt; SMA20</code>。</li>
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
    {render_table(compare_view, percent_cols={'base_return','always5_return','switch_return','switch_pressure_return','base_retention','always5_retention','switch_retention','switch_pressure_retention','base_early_fail','always5_early_fail','switch_early_fail','switch_pressure_early_fail','switch_positive_asset_ratio','switch_pressure_positive_asset_ratio','switch_exec_5m_share','switch_pressure_exec_5m_share'}, digits_cols={})}
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_signal_retention','mean_early_fail_60m_rate','mean_exec_5m_share'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','early_fail_60m_rate','exec_5m_share'}, digits_cols={'trades':0})}
  </div>

  <div class='card'>
    <h2>time pockets（按变体三分桶）</h2>
    {render_table(pockets, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades':1})}
  </div>
</body>
</html>
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
- **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`。因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity，按权威顺序这轮执行 **`Run 2 / Rank 66 minimal clean replication`**。
  - 这轮已把 `Rank 66 / exec-TF switch alignment gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` spot cache，并补 Binance spot `5m` cache；`1h / 4h` 全部从同一条 5m 数据 resample，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base_15m_only`、`always_5m_confirm`、`alignment_switch`、`alignment_switch_plus_pressure` 四臂，执行统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 120m`**。
  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `always5≈{pct(row_ema['always5_return'])}`、`switch≈{pct(row_ema['switch_return'])}`、`switch+pressure≈{pct(row_ema['switch_pressure_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `always5≈{pct(row_fib['always5_return'])}`、`switch≈{pct(row_fib['switch_return'])}`、`switch+pressure≈{pct(row_fib['switch_pressure_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `always5≈{pct(row_short['always5_return'])}`、`switch≈{pct(row_short['switch_return'])}`、`switch+pressure≈{pct(row_short['switch_pressure_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 66 / exec-TF switch alignment gate = {verdict}`**。
  - reader-facing 落点：`reports/site/factors/scout_rank66_exec_tf_switch_alignment_15m/report.html`、`reports/site/reading/repo_scout/rank66_exec_tf_switch_alignment_clean_replication.html`；artifact：`reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/overall_summary.csv`、`setup_compare.csv`。
  - 当前更诚实的 active Scout 顺序应更新为：**`Rank 67 / regime-matrix shared-state gate` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**（`Rank 66` 本轮已消耗完默认 clean-replication 预算；若 verdict 仍不足以直接升层，就不该继续赖在 fast-lane 队首）。
  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 66 verdict 不足以升到下一层，则再比较 Rank 67 / regime-matrix shared-state gate；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing` -> `Run 3 = 若 Rank 67 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 fresh source 这一层仍未 admitted，则继续按 7.10 从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条 5m/15m crypto source`**。"""
    text = text.replace(marker, "\n" + insert_block + marker, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    signal_tables: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        bars15 = add_base_setup_signals(load_15m_bars(symbol, asset))
        bars15 = add_bos_columns(bars15, BOS_LOOKBACK_15M)
        bars5 = add_bos_columns(fetch_5m_spot(symbol), BOS_LOOKBACK_5M)
        align, _, _ = build_alignment_table(bars15, bars5)
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(bars15, bars5, align, asset, setup))

    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 66 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    for asset, symbol in ASSETS.items():
        bars15 = add_base_setup_signals(load_15m_bars(symbol, asset))
        bars15 = add_bos_columns(bars15, BOS_LOOKBACK_15M)
        bars5 = add_bos_columns(fetch_5m_spot(symbol), BOS_LOOKBACK_5M)
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            base_cache: dict[float, pd.DataFrame] = {}
            admitted_cache: dict[tuple[str, float], int] = {}
            for cost in COSTS:
                base_trades, base_admitted = build_trades(bars15, bars5, sigs, "base_15m_only", cost)
                base_cache[cost] = base_trades
                admitted_cache[("base_15m_only", cost)] = base_admitted
                if not base_trades.empty:
                    trade_frames.append(base_trades)
            for variant in VARIANTS:
                for cost in COSTS:
                    if variant == "base_15m_only":
                        trades = base_cache[cost]
                        admitted = admitted_cache[(variant, cost)]
                    else:
                        trades, admitted = build_trades(bars15, bars5, sigs, variant, cost)
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
    asset_df = pd.DataFrame(asset_rows).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall_df = (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_signal_retention=("signal_retention", "mean"),
            mean_early_fail_60m_rate=("early_fail_60m_rate", "mean"),
            mean_exec_5m_share=("exec_5m_share", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )
    pockets_df = build_time_pockets(trades_df)
    compare_df = build_setup_compare(overall_df)
    verdict, headline, reason = build_verdict(compare_df)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    compare_df.to_csv(ART_DIR / "setup_compare.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    report_html = build_html(overall_df, asset_df, pockets_df, compare_df, verdict, headline, reason, generated_at)
    write_html(SITE_DIR / "report.html", "Rank 66 clean replication", report_html)

    reading_body = f"""
<h1>Rank 66 / exec-TF switch alignment gate — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'P1' in verdict or 'P2' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：当高周期对齐时把触发切到 5m、失配时坚持 15m，这条 shared execution gate，能不能比 `always 15m` 或 `always 5m` 更诚实？</p>
</div>
<div class='card'>
  <h2>结果表</h2>
  {render_table(overall_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_signal_retention','mean_early_fail_60m_rate','mean_exec_5m_share'}, digits_cols={'mean_trades':1,'cost_bps_per_side':0})}
</div>
<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>
"""
    write_html(READING_DIR / "rank66_exec_tf_switch_alignment_clean_replication.html", "Rank 66 clean replication", reading_body)

    update_todo(compare_df, verdict, generated_at)
    print(f"verdict={verdict}")


if __name__ == "__main__":
    main()
