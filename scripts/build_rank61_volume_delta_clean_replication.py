#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank61_volume_delta_polarity_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank61_volume_delta_polarity_veto_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
KLINE_CACHE_DIR = ART_DIR / "subtf_kline_cache"
BINANCE_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"
REQ_TIMEOUT = 20

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "same_direction_gate", "opposite_delta_veto", "strong_same_direction_only"]
PRIMARY_SETUP = "ema_psar_long"
PRIMARY_VARIANT = "opposite_delta_veto"
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FALSE_WINDOW = 4
SUBTF_INTERVAL = "1m"
FLOW_WINDOW_MINUTES = 5

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


def kline_cache_path(symbol: str, signal_ts: pd.Timestamp) -> Path:
    return KLINE_CACHE_DIR / f"{symbol}_{signal_ts.strftime('%Y%m%dT%H%M%SZ')}_{SUBTF_INTERVAL}_{FLOW_WINDOW_MINUTES}m.json"


def fetch_subtf_klines(symbol: str, signal_ts: pd.Timestamp) -> list[list]:
    ensure_dir(KLINE_CACHE_DIR)
    cache_path = kline_cache_path(symbol, signal_ts)
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    end_ms = int(signal_ts.timestamp() * 1000)
    start_ms = int((signal_ts - timedelta(minutes=FLOW_WINDOW_MINUTES)).timestamp() * 1000)
    params = {
        "symbol": symbol,
        "interval": SUBTF_INTERVAL,
        "startTime": start_ms,
        "endTime": end_ms - 1,
        "limit": FLOW_WINDOW_MINUTES + 3,
    }
    resp = None
    for attempt in range(6):
        resp = requests.get(BINANCE_KLINES_URL, params=params, timeout=REQ_TIMEOUT, headers={"User-Agent": "OpenClaw/1.0"})
        if resp.status_code != 429:
            break
        retry_after = resp.headers.get("Retry-After")
        wait_s = float(retry_after) if retry_after else min(20.0, 2 ** attempt)
        time.sleep(wait_s)
    assert resp is not None
    resp.raise_for_status()
    data = resp.json()
    cache_path.write_text(json.dumps(data), encoding="utf-8")
    time.sleep(0.05)
    return data


def summarize_subtf_delta(symbol: str, signal_ts: pd.Timestamp) -> dict[str, float | int]:
    rows = fetch_subtf_klines(symbol, signal_ts)
    if not rows:
        return {
            "delta_align": 0.0,
            "abs_delta_align": 0.0,
            "sub_bars": 0,
            "window_volume": 0.0,
            "positive_subbar_ratio": np.nan,
            "negative_subbar_ratio": np.nan,
            "neutral_subbar_ratio": np.nan,
        }

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trade_count", "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[(df["open_time"] >= signal_ts - timedelta(minutes=FLOW_WINDOW_MINUTES)) & (df["open_time"] < signal_ts)].copy()
    if df.empty:
        return {
            "delta_align": 0.0,
            "abs_delta_align": 0.0,
            "sub_bars": 0,
            "window_volume": 0.0,
            "positive_subbar_ratio": np.nan,
            "negative_subbar_ratio": np.nan,
            "neutral_subbar_ratio": np.nan,
        }
    sign = np.where(df["close"] > df["open"], 1.0, np.where(df["close"] < df["open"], -1.0, 0.0))
    signed_volume = sign * df["volume"].fillna(0.0).to_numpy()
    vol_sum = float(df["volume"].sum())
    delta_align = float(signed_volume.sum() / vol_sum) if vol_sum > 0 else 0.0
    return {
        "delta_align": delta_align,
        "abs_delta_align": abs(delta_align),
        "sub_bars": int(len(df)),
        "window_volume": vol_sum,
        "positive_subbar_ratio": float((sign > 0).mean()),
        "negative_subbar_ratio": float((sign < 0).mean()),
        "neutral_subbar_ratio": float((sign == 0).mean()),
    }


def build_signal_frame(frame: pd.DataFrame, asset: str, symbol: str, setup: str) -> pd.DataFrame:
    sig = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(max(40, 2), len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        signal_ts = pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True)
        delta = summarize_subtf_delta(symbol, signal_ts)
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "symbol": symbol,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(frame.iloc[idx]["close"]),
                **delta,
            }
        )
        last_exit = idx + HOLD_BARS
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["same_direction"] = (out["direction"] * out["delta_align"]) > 0
    out["opposite_direction"] = (out["direction"] * out["delta_align"]) < 0
    out["strong_delta_threshold"] = (
        out.groupby(["asset", "setup"], dropna=False)["abs_delta_align"]
        .transform(lambda s: s.rolling(20, min_periods=10).median().shift(1))
    )
    out["strong_same_direction"] = out["same_direction"] & (out["abs_delta_align"] >= out["strong_delta_threshold"].fillna(np.inf))
    return out


def variant_allowed(row: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "same_direction_gate":
        return bool(row["same_direction"])
    if variant == "opposite_delta_veto":
        return not bool(row["opposite_direction"])
    if variant == "strong_same_direction_only":
        return bool(row["strong_same_direction"])
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
        ft2_idx = min(len(frame) - 1, entry_idx + 1)
        ft4_idx = min(len(frame) - 1, entry_idx + 3)
        ft2 = direction * ((float(frame.iloc[ft2_idx]["close"]) / entry_px) - 1.0)
        ft4 = direction * ((float(frame.iloc[ft4_idx]["close"]) / entry_px) - 1.0)
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
                "follow_through_2bars": ft2,
                "follow_through_4bars": ft4,
                "false_break_or_hold_4bars": detect_failure(frame, int(sig["signal_idx"]), direction, float(sig["signal_price"]), FALSE_WINDOW),
                "delta_align": float(sig["delta_align"]),
                "abs_delta_align": float(sig["abs_delta_align"]),
                "sub_bars": int(sig["sub_bars"]),
                "window_volume": float(sig["window_volume"]),
                "positive_subbar_ratio": float(sig["positive_subbar_ratio"]) if pd.notna(sig["positive_subbar_ratio"]) else np.nan,
                "negative_subbar_ratio": float(sig["negative_subbar_ratio"]) if pd.notna(sig["negative_subbar_ratio"]) else np.nan,
            }
        )
    return pd.DataFrame(rows), admitted


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int) -> dict[str, object]:
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
            "signal_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_break_or_hold_4bars_rate": np.nan,
            "follow_through_2bars": np.nan,
            "follow_through_4bars": np.nan,
            "mean_abs_delta_align": np.nan,
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
        "false_break_or_hold_4bars_rate": float(trades["false_break_or_hold_4bars"].mean()),
        "follow_through_2bars": float(trades["follow_through_2bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "mean_abs_delta_align": float(trades["abs_delta_align"].mean()),
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


def build_verdict(overall: pd.DataFrame) -> tuple[str, str, str]:
    primary = overall[(overall["setup"] == PRIMARY_SETUP) & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    fib = overall[(overall["setup"] == "fib_retest_long") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    short = overall[(overall["setup"] == "breakout_short") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主读法没有形成可用样本。", "主读法没有产出有效结果，因此不能继续占默认 clean-replication 队列。"
    p = primary.iloc[0]
    f = fib.iloc[0] if not fib.empty else None
    s = short.iloc[0] if not short.empty else None
    headline = (
        f"`ema_psar_long + opposite_delta_veto @ {int(PRIMARY_COST)}bps`：mean_total_return≈{pct(p['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(p['positive_asset_ratio'])}、mean_trades≈{num(p['mean_trades'],1)}、"
        f"trade_count_retention≈{pct(p['mean_trade_count_retention'])}、false_break_or_hold_4bars≈{pct(p['mean_false_break_or_hold_4bars_rate'])}"
        + (f"；`fib_retest_long≈{pct(f['mean_total_return'])} / {pct(f['positive_asset_ratio'])}`" if f is not None else "")
        + (f"；`breakout_short≈{pct(s['mean_total_return'])} / {pct(s['positive_asset_ratio'])}`" if s is not None else "")
    )
    primary_good = (
        float(p["mean_total_return"]) > 0
        and float(p["positive_asset_ratio"]) >= (2 / 3)
        and float(p["mean_trade_count_retention"]) >= 0.45
        and float(p["mean_false_break_or_hold_4bars_rate"]) <= 0.45
    )
    supporting = 0
    for row in [f, s]:
        if row is None:
            continue
        if float(row["mean_total_return"]) > -0.005 and float(row["mean_trade_count_retention"]) >= 0.35:
            supporting += 1
    if primary_good and supporting >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 至少说明 lower-TF delta polarity mismatch 不是纯噪音：在主读法里它能在不过度砍样本的前提下留下正 pocket，但跨 setup 还不够统一，所以先留在 P1 证据池，而不是直接升格。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：lower-TF delta polarity 作为 shared veto 有一点直觉味道，但当前改善仍主要靠砍样本或只落在单一 archetype，跨资产/跨 setup 不够统一，不值得继续占 fast-lane。",
    )


def update_todo(overall: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    primary = overall[(overall["setup"] == PRIMARY_SETUP) & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    fib = overall[(overall["setup"] == "fib_retest_long") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    short = overall[(overall["setup"] == "breakout_short") & (overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    fib_text = ""
    short_text = ""
    if not fib.empty:
        row = fib.iloc[0]
        fib_text = f"；`fib_retest_long + opposite_delta_veto≈{pct(row['mean_total_return'])} / retention≈{pct(row['mean_trade_count_retention'])} / false≈{pct(row['mean_false_break_or_hold_4bars_rate'])}`"
    if not short.empty:
        row = short.iloc[0]
        short_text = f"；`breakout_short + opposite_delta_veto≈{pct(row['mean_total_return'])} / retention≈{pct(row['mean_trade_count_retention'])} / false≈{pct(row['mean_false_break_or_hold_4bars_rate'])}`"
    queue_line = (
        "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 61 仍不足以升格，则转去比较 continuation fail-fast overlay > pullback-quality / CQI` -> `Run 3 = 只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
        if verdict.startswith("park")
        else
        "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 61 仍保留在 P1，则只允许给它 1 个真正会改变 verdict 的最小检查（默认优先 time stability）` -> `Run 3 = 若 Rank 61 仍不能升格，则转去比较 continuation fail-fast overlay > pullback-quality / CQI；只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    )
    block = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane（最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，其后 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、A 股三条 lane `-> 2026-03-19 07:00 UTC`），而 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended={latest_p3_appends}`，因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。随后按权威顺序执行 **`Run 2 / Rank 61 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，并对每个 setup 只抓 `signal 前最后 5 分钟` 的 Binance public `{SUBTF_INTERVAL}` klines，把 `sub close>open` 记正量、`sub close<open` 记负量，统一比较 `base`、`same_direction_gate`、`opposite_delta_veto`、`strong_same_direction_only` 四臂；执行统一冻结到 `next-bar open + no-overlap + hold 8 bars`。\n"
        f">  - `6bps/side` 下的主读法 `ema_psar_long + opposite_delta_veto` 结果为：`mean_total_return≈{pct(primary['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}`、`mean_trades≈{num(primary['mean_trades'],1)}`、`trade_count_retention≈{pct(primary['mean_trade_count_retention'])}`、`false_break_or_hold_4bars_rate≈{pct(primary['mean_false_break_or_hold_4bars_rate'])}`{fib_text}{short_text}。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 61 / lower-TF volume-delta polarity mismatch veto = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank61_volume_delta_polarity_veto_15m/report.html`、`reports/site/reading/repo_scout/rank61_volume_delta_polarity_veto_clean_replication.html`；artifact：`reports/artifacts/scout_rank61_volume_delta_polarity_veto_15m/overall_summary.csv`。\n"
        f">  - 排班含义：当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def update_repo_scout_index() -> None:
    report_path = READING_DIR / "report.html"
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8")
    if "rank61_volume_delta_polarity_veto_clean_replication.html" in text:
        return
    old = 'rank61_volume_delta_polarity_veto_source_intake.html">Rank 61 source intake</a>'
    if old in text:
        text = text.replace(old, old + ' ｜ <a href="rank61_volume_delta_polarity_veto_clean_replication.html">clean replication</a>', 1)
        report_path.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)
    ensure_dir(KLINE_CACHE_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, symbol, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 61 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows_with_subtf_delta.csv", index=False)

    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
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
            for variant in VARIANTS:
                for cost in COSTS:
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
                        )
                    )

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_df = add_retentions(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)

    overall_df = (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_signal_retention=("signal_retention", "mean"),
            mean_false_break_or_hold_4bars_rate=("false_break_or_hold_4bars_rate", "mean"),
            mean_follow_through_2bars=("follow_through_2bars", "mean"),
            mean_follow_through_4bars=("follow_through_4bars", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_abs_delta_align=("mean_abs_delta_align", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)

    time_pockets_df = build_time_pockets(trades_df)
    time_pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)

    verdict, headline, reason = build_verdict(overall_df)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank61_volume_delta_polarity_veto_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    summary_card = f"""
<h1>Rank 61 / lower-TF volume-delta polarity mismatch veto — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：当 15m setup 已经给出方向和价位时，入场前最后 5 分钟的 lower-TF 子周期量价极性，能不能作为 shared veto / confirmation 层减少假动作，而不是重新包装成新 alpha。</p>
</div>
"""

    method = f"""
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>只复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>三条最小 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>子周期固定用 Binance Futures 公开 <code>{SUBTF_INTERVAL}</code> kline proxy，只取 setup 触发前最后 <code>{FLOW_WINDOW_MINUTES}</code> 分钟。</li>
    <li><code>sub close &gt; open</code> 记正量，<code>sub close &lt; open</code> 记负量；不引入入场后的 volume，不引入 repo 里的其它 kitchen-sink 组件。</li>
    <li>四臂固定为：<code>base</code>、<code>same_direction_gate</code>、<code>opposite_delta_veto</code>、<code>strong_same_direction_only</code>。</li>
    <li>所有执行统一冻结到 <code>next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</li>
  </ul>
</div>
"""

    report_body = summary_card + method
    report_body += "<h2>overall summary</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_false_break_or_hold_4bars_rate", "mean_follow_through_2bars", "mean_follow_through_4bars"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_abs_delta_align": 3},
    )
    report_body += "<h2>asset-level summary</h2>" + render_table(
        asset_df,
        percent_cols={"trade_count_retention", "signal_retention", "total_return", "avg_net_ret", "win_rate", "false_break_or_hold_4bars_rate", "follow_through_2bars", "follow_through_4bars"},
        digits_cols={"trades": 0, "base_signals": 0, "admitted_signals": 0, "cost_bps_per_side": 0, "mean_abs_delta_align": 3},
    )
    report_body += "<h2>time-pocket honesty</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 1},
    )
    write_html(SITE_DIR / "report.html", "Rank 61 clean replication", report_body)

    reading_body = summary_card
    reading_body += "<div class='card'><h2>当前更直白的读法</h2><p>如果这层 lower-TF delta polarity 真有用，它至少应该在不把样本砍废的前提下，让现有 15m setup 更少 4-bar 假突破 / 假守住；如果改善主要来自单一 pocket 或强砍样本，那它就该尽快 park。</p></div>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_signal_retention", "mean_false_break_or_hold_4bars_rate", "mean_follow_through_2bars", "mean_follow_through_4bars"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_abs_delta_align": 3},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>"
    write_html(READING_DIR / "rank61_volume_delta_polarity_veto_clean_replication.html", "Rank 61 clean replication", reading_body)

    update_repo_scout_index()
    update_todo(overall_df, verdict, generated_at, latest_p3_appends)
    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
