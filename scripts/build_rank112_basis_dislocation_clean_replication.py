#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank112_basis_dislocation_short_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank112_basis_dislocation_short_veto_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank112_basis_dislocation_short_veto_clean_replication.html"
FETCH_CACHE_DIR = ART_DIR / "public_data_cache"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
VARIANTS = ["baseline", "basis_extreme_veto", "basis_extreme_plus_oi_veto"]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
HOLD_BARS = 8
FOLLOW_BARS = [4, 8, 12]
BREAK_LOOKBACK = 20
EMA_FAST = 9
EMA_SLOW = 15
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0003
ATR_PERIOD = 14
BREAK_CONFIRM_ATR = 0.1
BREAK_RETEST_ATR = 0.3
BASIS_WINDOW = 30 * 24 * 4  # 30d on 15m bars
OI_DELTA_BARS = 4
PREMIUM_URL = "https://fapi.binance.com/fapi/v1/premiumIndexKlines"
OI_URL = "https://fapi.binance.com/futures/data/openInterestHist"
REQ_TIMEOUT = 20
BINANCE_LIMIT = 1000
OI_LIMIT = 500

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
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


def rolling_percentile_of_last(series: pd.Series, window: int) -> pd.Series:
    values = series.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(window - 1, len(values)):
        chunk = values[i - window + 1:i + 1]
        cur = chunk[-1]
        if np.isnan(cur):
            continue
        valid = chunk[~np.isnan(chunk)]
        if len(valid) < window // 2:
            continue
        out[i] = float((valid <= cur).mean())
    return pd.Series(out, index=series.index)


def fetch_premium_history(symbol: str, start_ts: pd.Timestamp) -> pd.DataFrame:
    cache_path = FETCH_CACHE_DIR / f"{symbol}_premium_15m.csv"
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True)
        if len(cached) and cached["timestamp"].min() <= start_ts and cached["timestamp"].max() >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=1):
            return cached.sort_values("timestamp").reset_index(drop=True)

    rows: list[list] = []
    end_time: int | None = None
    start_ms = int(start_ts.timestamp() * 1000)
    for _ in range(20):
        params: dict[str, object] = {"symbol": symbol, "interval": "15m", "limit": BINANCE_LIMIT}
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(PREMIUM_URL, params=params, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = int(batch[0][0])
        if earliest <= start_ms:
            break
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end

    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "ignore1", "close_time", "ignore2", "ignore3", "ignore4", "ignore5", "ignore6"
    ])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["basis_close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df[["timestamp", "basis_close"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    return df


def fetch_oi_history(symbol: str, start_ts: pd.Timestamp) -> pd.DataFrame:
    cache_path = FETCH_CACHE_DIR / f"{symbol}_oi_15m.csv"
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True)
        if len(cached) and cached["timestamp"].min() <= start_ts and cached["timestamp"].max() >= pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=1):
            return cached.sort_values("timestamp").reset_index(drop=True)

    rows: list[dict[str, object]] = []
    end_time: int | None = None
    start_ms = int(start_ts.timestamp() * 1000)
    for _ in range(40):
        params: dict[str, object] = {
            "symbol": symbol,
            "period": "15m",
            "limit": OI_LIMIT,
            "contractType": "PERPETUAL",
        }
        if end_time is not None:
            params["endTime"] = end_time
        resp = requests.get(OI_URL, params=params, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        earliest = min(int(item["timestamp"]) for item in batch)
        if earliest <= start_ms:
            break
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end

    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["sumOpenInterest"] = pd.to_numeric(df["sumOpenInterest"], errors="coerce")
    df["sumOpenInterestValue"] = pd.to_numeric(df.get("sumOpenInterestValue"), errors="coerce")
    df = df[["timestamp", "sumOpenInterest", "sumOpenInterestValue"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    return df


def build_frame(asset: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    bars = load_bars(symbol, asset)
    start_ts = bars["timestamp"].min() - pd.Timedelta(days=35)
    premium = fetch_premium_history(symbol, start_ts)
    oi = fetch_oi_history(symbol, start_ts)

    frame = bars.merge(premium, on="timestamp", how="left")
    frame = frame.merge(oi, on="timestamp", how="left")
    frame["basis_pct_30d"] = rolling_percentile_of_last(frame["basis_close"], BASIS_WINDOW)
    frame["oi_delta_1h"] = frame["sumOpenInterest"].diff(OI_DELTA_BARS)
    frame["ema9"] = frame["close"].ewm(span=EMA_FAST, adjust=False).mean()
    frame["ema15"] = frame["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    frame["ema_slope"] = frame["ema9"].pct_change(EMA_SLOPE_LOOKBACK)
    frame["atr14"] = compute_atr(frame)
    frame["rolling_low20"] = frame["low"].rolling(BREAK_LOOKBACK, min_periods=BREAK_LOOKBACK).min().shift(1)
    low = frame["rolling_low20"]
    atr = frame["atr14"]
    frame["breakout_short_signal"] = (
        low.notna()
        & (frame["ema9"] < frame["ema15"])
        & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
        & (frame["close"].shift(1) > low.shift(1))
        & (frame["close"].shift(2) > low.shift(2))
        & (frame["close"] < low - BREAK_CONFIRM_ATR * atr)
        & (frame["high"] <= low + BREAK_RETEST_ATR * atr)
        & (frame["volume"] > frame["volume"].rolling(20, min_periods=20).mean())
    ).fillna(False)
    frame["basis_extreme_negative"] = (frame["basis_pct_30d"] <= 0.10).fillna(False)
    frame["basis_oi_veto"] = (frame["basis_extreme_negative"] & (frame["oi_delta_1h"] <= 0)).fillna(False)
    return frame.reset_index(drop=True), premium, oi


def variant_allowed(row: pd.Series, variant: str) -> tuple[bool, str]:
    if variant == "baseline":
        return True, "baseline"
    if variant == "basis_extreme_veto":
        if bool(row["basis_extreme_negative"]):
            return False, "basis_extreme_negative"
        return True, "basis_not_extreme"
    if variant == "basis_extreme_plus_oi_veto":
        if bool(row["basis_oi_veto"]):
            return False, "basis_extreme_plus_oi_negative"
        return True, "basis_or_oi_clear"
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, variant: str, cost_bps_per_side: float) -> tuple[pd.DataFrame, int, pd.DataFrame]:
    rows: list[dict[str, object]] = []
    veto_rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost = float(cost_bps_per_side) / 10000.0

    for idx in range(2, len(frame) - max(FOLLOW_BARS) - 1):
        if idx <= last_exit_idx or not bool(frame.iloc[idx]["breakout_short_signal"]):
            continue
        signal_events += 1
        allow, reason = variant_allowed(frame.iloc[idx], variant)
        if not allow:
            veto_rows.append({
                "asset": frame.iloc[0]["asset"],
                "variant": variant,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "veto_reason": reason,
                "basis_close": float(frame.iloc[idx]["basis_close"]) if pd.notna(frame.iloc[idx]["basis_close"]) else np.nan,
                "basis_pct_30d": float(frame.iloc[idx]["basis_pct_30d"]) if pd.notna(frame.iloc[idx]["basis_pct_30d"]) else np.nan,
                "oi_delta_1h": float(frame.iloc[idx]["oi_delta_1h"]) if pd.notna(frame.iloc[idx]["oi_delta_1h"]) else np.nan,
            })
            continue
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross = entry_px / exit_px - 1.0
        net = (1.0 + gross) * (1.0 - cost) * (1.0 - cost) - 1.0
        follow = {}
        mae = 0.0
        mfe = 0.0
        for bars in FOLLOW_BARS:
            probe_idx = min(len(frame) - 1, entry_idx + bars - 1)
            probe_ret = entry_px / float(frame.iloc[probe_idx]["close"]) - 1.0
            follow[bars] = probe_ret
        for j in range(entry_idx, exit_idx + 1):
            low_ret = entry_px / float(frame.iloc[j]["high"]) - 1.0
            high_ret = entry_px / float(frame.iloc[j]["low"]) - 1.0
            mae = min(mae, low_ret)
            mfe = max(mfe, high_ret)
        rows.append({
            "asset": frame.iloc[0]["asset"],
            "variant": variant,
            "cost_bps_per_side": float(cost_bps_per_side),
            "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_return": gross,
            "net_return": net,
            "follow_through_4bars": follow[4],
            "follow_through_8bars": follow[8],
            "follow_through_12bars": follow[12],
            "false_break_4bars": int(follow[4] <= 0),
            "false_break_8bars": int(follow[8] <= 0),
            "false_break_12bars": int(follow[12] <= 0),
            "mae": mae,
            "mfe": mfe,
            "basis_close": float(frame.iloc[idx]["basis_close"]) if pd.notna(frame.iloc[idx]["basis_close"]) else np.nan,
            "basis_pct_30d": float(frame.iloc[idx]["basis_pct_30d"]) if pd.notna(frame.iloc[idx]["basis_pct_30d"]) else np.nan,
            "oi_delta_1h": float(frame.iloc[idx]["oi_delta_1h"]) if pd.notna(frame.iloc[idx]["oi_delta_1h"]) else np.nan,
            "basis_extreme_negative": int(bool(frame.iloc[idx]["basis_extreme_negative"])),
            "basis_oi_veto": int(bool(frame.iloc[idx]["basis_oi_veto"])),
            "hold_bars": int(exit_idx - entry_idx + 1),
            "variant_reason": reason,
        })
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events, pd.DataFrame(veto_rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps_per_side: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps_per_side),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": np.nan,
            "total_return": 0.0,
            "avg_net_return": np.nan,
            "win_rate": np.nan,
            "false_break_4bars": np.nan,
            "false_break_8bars": np.nan,
            "false_break_12bars": np.nan,
            "avg_mae": np.nan,
            "avg_mfe": np.nan,
            "avg_basis_pct_30d": np.nan,
            "avg_oi_delta_1h": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps_per_side),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_return"]).prod() - 1.0),
        "avg_net_return": float(trades["net_return"].mean()),
        "win_rate": float((trades["net_return"] > 0).mean()),
        "false_break_4bars": float(trades["false_break_4bars"].mean()),
        "false_break_8bars": float(trades["false_break_8bars"].mean()),
        "false_break_12bars": float(trades["false_break_12bars"].mean()),
        "avg_mae": float(trades["mae"].mean()),
        "avg_mfe": float(trades["mfe"].mean()),
        "avg_basis_pct_30d": float(trades["basis_pct_30d"].mean()) if trades["basis_pct_30d"].notna().any() else np.nan,
        "avg_oi_delta_1h": float(trades["oi_delta_1h"].mean()) if trades["oi_delta_1h"].notna().any() else np.nan,
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for cost in sorted(out["cost_bps_per_side"].dropna().unique()):
        raw_map = (
            out[(out["variant"] == "baseline") & (out["cost_bps_per_side"] == cost)]
            .set_index("asset")["trades"]
            .to_dict()
        )
        mask = out["cost_bps_per_side"] == cost
        out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
            lambda r: float(r["trades"] / raw_map.get(r["asset"], np.nan)) if raw_map.get(r["asset"], 0) else np.nan,
            axis=1,
        )
    return out


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], dropna=False):
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(grp["total_return"].mean()),
            "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
            "mean_trades": float(grp["trades"].mean()),
            "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if grp["trade_count_retention"].notna().any() else np.nan,
            "mean_avg_net_return": float(grp["avg_net_return"].mean()) if grp["avg_net_return"].notna().any() else np.nan,
            "mean_false_break_4bars": float(grp["false_break_4bars"].mean()) if grp["false_break_4bars"].notna().any() else np.nan,
            "mean_false_break_8bars": float(grp["false_break_8bars"].mean()) if grp["false_break_8bars"].notna().any() else np.nan,
            "mean_false_break_12bars": float(grp["false_break_12bars"].mean()) if grp["false_break_12bars"].notna().any() else np.nan,
            "mean_avg_mae": float(grp["avg_mae"].mean()) if grp["avg_mae"].notna().any() else np.nan,
            "mean_avg_mfe": float(grp["avg_mfe"].mean()) if grp["avg_mfe"].notna().any() else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["variant", "cost_bps_per_side"]).reset_index(drop=True)


def summarize_time_buckets(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty:
        return pd.DataFrame(columns=["bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "false_break_8bars"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["bucket"] = pd.qcut(work["entry_ts_dt"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "false_break_8bars"])
    rows = []
    for bucket, grp in work.groupby("bucket", observed=False):
        asset_total = grp.groupby("asset")["net_return"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "bucket": str(bucket),
            "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
            "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
            "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
            "false_break_8bars": float(grp["false_break_8bars"].mean()) if len(grp) else np.nan,
        })
    return pd.DataFrame(rows)


def summarize_vetoes(veto_df: pd.DataFrame) -> pd.DataFrame:
    if veto_df.empty:
        return pd.DataFrame(columns=["variant", "asset", "veto_reason", "count"])
    return (
        veto_df.groupby(["variant", "asset", "veto_reason"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
        .sort_values(["variant", "asset", "count"], ascending=[True, True, False])
        .reset_index(drop=True)
    )


def build_verdict(overall_6: pd.DataFrame) -> tuple[str, str]:
    lookup = overall_6.set_index("variant")
    base = lookup.loc["baseline"]
    basis = lookup.loc["basis_extreme_veto"]
    basis_oi = lookup.loc["basis_extreme_plus_oi_veto"]

    basis_improves = (
        float(basis["mean_total_return"]) > float(base["mean_total_return"])
        and float(basis["mean_false_break_8bars"]) <= float(base["mean_false_break_8bars"])
    )
    basis_oi_improves = (
        float(basis_oi["mean_total_return"]) > float(base["mean_total_return"])
        and float(basis_oi["mean_false_break_8bars"]) <= float(base["mean_false_break_8bars"])
    )
    retention_ok = float(basis_oi["mean_trade_count_retention"]) >= 0.60 if pd.notna(basis_oi["mean_trade_count_retention"]) else False
    cross_ok = float(basis_oi["positive_asset_ratio"]) >= (2 / 3)

    if basis_oi_improves and retention_ok and cross_ok:
        return (
            "promote_to_P2 / paper candidate pool",
            "极端负 basis + OI 负增量 veto 在 6bps 下同时改善了成本后收益、false-break 与跨资产比率，且样本留存没有塌；这轮已经够资格进 paper candidate pool。",
        )
    if basis_improves or basis_oi_improves:
        return (
            "keep_P1 / honest veto signal",
            "极端负 basis veto 至少证明了一个诚实方向：某些下破确实不该继续追空；但当前留存/跨资产仍不够硬，只够继续留在 P1，不直接升 P2。",
        )
    return (
        "park / evidence pool",
        "这轮 minimal clean replication 没把 basis veto 变成更诚实的 breakout-short 过滤层：成本后收益、false-break 与样本留存没有同时改善，因此当前更适合 park。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    ensure_dir(FETCH_CACHE_DIR)

    all_trades: list[pd.DataFrame] = []
    all_vetoes: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    meta_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame, premium, oi = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower()}_frame.csv", index=False)
        premium.to_csv(FETCH_CACHE_DIR / f"{symbol.lower()}_premium_15m.csv", index=False)
        oi.to_csv(FETCH_CACHE_DIR / f"{symbol.lower()}_oi_15m.csv", index=False)
        meta_rows.append({
            "asset": asset,
            "symbol": symbol,
            "bars": int(len(frame)),
            "premium_rows": int(len(premium)),
            "oi_rows": int(len(oi)),
            "sample_start_utc": frame["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
            "sample_end_utc": frame["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ") if len(frame) else "-",
        })
        for variant in VARIANTS:
            for cost in COSTS:
                trades, signal_events, vetoes = build_trades(frame, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                if not vetoes.empty:
                    all_vetoes.append(vetoes.assign(cost_bps_per_side=float(cost)))
                asset_rows.append(summarize_asset(trades, asset=asset, variant=variant, cost_bps_per_side=cost, signal_events=signal_events))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    veto_df = pd.concat(all_vetoes, ignore_index=True) if all_vetoes else pd.DataFrame()
    asset_df = add_trade_retention(pd.DataFrame(asset_rows))
    overall_df = summarize_overall(asset_df)
    overall_6 = overall_df[overall_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    time_df = summarize_time_buckets(trades_df[(trades_df["variant"] == "basis_extreme_plus_oi_veto") & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy() if not trades_df.empty else pd.DataFrame())
    veto_summary = summarize_vetoes(veto_df[veto_df["cost_bps_per_side"] == PRIMARY_COST].copy() if not veto_df.empty else pd.DataFrame())
    meta_df = pd.DataFrame(meta_rows)

    verdict, verdict_note = build_verdict(overall_6)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    veto_summary.to_csv(ART_DIR / "veto_reason_summary.csv", index=False)
    time_df.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    meta_df.to_csv(ART_DIR / "sample_meta.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "verdict_note": verdict_note,
        "primary_cost_bps_per_side": PRIMARY_COST,
        "basis_window_bars": BASIS_WINDOW,
        "oi_delta_bars": OI_DELTA_BARS,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    base = overall_6.set_index("variant").loc["baseline"]
    basis = overall_6.set_index("variant").loc["basis_extreme_veto"]
    basis_oi = overall_6.set_index("variant").loc["basis_extreme_plus_oi_veto"]

    factor_body = f"""
<h1>Rank 112 / basis dislocation short veto — minimal clean replication</h1>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'promote' in verdict else 'warn' if 'keep_P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p class='muted'>固定 BTC/ETH/SOL 120d 15m 本地 cache，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>，只比较 <code>baseline</code> / <code>basis_extreme_veto</code> / <code>basis_extreme_plus_oi_veto</code> 三臂。</p>
</div>
<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <ul>
    <li>当 breakout-short 触发已经成立时，<code>basis_pct_30d &lt;= 10%</code> 这种“极端负基差”是不是在提醒你：这单别继续追空？</li>
    <li>再加一层 <code>oi_delta_1h &lt;= 0</code>，能不能更诚实地把“贴地负基差 + 没有新增拥挤参与”的坏追空过滤掉？</li>
  </ul>
</div>
<div class='card'>
  <h2>主读法（6bps/side）</h2>
  <ul>
    <li>baseline：mean_total_return = <strong>{pct(base['mean_total_return'])}</strong>；positive_asset_ratio = {pct(base['positive_asset_ratio'])}；false_break_8bars = {pct(base['mean_false_break_8bars'])}</li>
    <li>basis_extreme_veto：mean_total_return = <strong>{pct(basis['mean_total_return'])}</strong>；retention = {pct(basis['mean_trade_count_retention'])}；false_break_8bars = {pct(basis['mean_false_break_8bars'])}</li>
    <li>basis_extreme_plus_oi_veto：mean_total_return = <strong>{pct(basis_oi['mean_total_return'])}</strong>；retention = {pct(basis_oi['mean_trade_count_retention'])}；false_break_8bars = {pct(basis_oi['mean_false_break_8bars'])}</li>
  </ul>
</div>
<div class='card'><h2>Overall summary</h2>{render_table(overall_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_avg_net_return','mean_false_break_4bars','mean_false_break_8bars','mean_false_break_12bars','mean_avg_mae','mean_avg_mfe'}, digits_cols={'cost_bps_per_side': 0, 'mean_trades': 1})}</div>
<div class='card'><h2>Asset summary</h2>{render_table(asset_df[asset_df['cost_bps_per_side'] == PRIMARY_COST].copy(), percent_cols={'trade_count_retention','total_return','avg_net_return','win_rate','false_break_4bars','false_break_8bars','false_break_12bars','avg_mae','avg_mfe','avg_basis_pct_30d'}, digits_cols={'cost_bps_per_side': 0, 'signal_events': 0, 'trades': 0})}</div>
<div class='card'><h2>Veto reason summary（6bps）</h2>{render_table(veto_summary, digits_cols={'count': 0})}</div>
<div class='card'><h2>Time bucket summary（主臂 = basis_extreme_plus_oi_veto @ 6bps）</h2>{render_table(time_df, percent_cols={'mean_total_return','positive_asset_ratio','false_break_8bars'}, digits_cols={'mean_trades': 1})}</div>
<div class='card'><h2>Sample meta</h2>{render_table(meta_df, digits_cols={'bars': 0, 'premium_rows': 0, 'oi_rows': 0})}</div>
<p class='muted'>Artifacts: overall_summary.csv / asset_summary.csv / veto_reason_summary.csv / time_bucket_summary.csv / trade_log.csv / summary.json</p>
"""
    write_html(SITE_DIR / "report.html", "Rank112 basis dislocation clean replication", factor_body)

    reading_body = f"""
<h1>Rank 112 / basis dislocation short veto — clean replication note</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(verdict_note)}</p>
  <p>它不是新的 short alpha，只是问：<code>这次已经出现的 breakdown，是不是在极端负 basis + OI 不扩张时更像末端拥挤，不该继续追空。</code></p>
  <p><a href='../../factors/scout_rank112_basis_dislocation_short_veto_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank112 basis dislocation clean replication", reading_body)

    print(json.dumps({
        "verdict": verdict,
        "verdict_note": verdict_note,
        "overall_summary": overall_df.to_dict(orient='records'),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
