#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank49_funding_basis_crowding_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank49_funding_basis_crowding_15m"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
BASE_SETUPS = ["ema_short", "breakdown_short"]
VARIANTS = ["no_gate", "crowded_long_only", "already_crowded_short_veto"]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
FOLLOW_THROUGH_BARS = [4, 8, 16]
EMA_FAST = 9
EMA_SLOW = 15
EMA_SLOPE_LOOKBACK = 3
EMA_SLOPE_FLOOR = 0.0003
ATR_PERIOD = 14
BREAK_LOOKBACK = 20
BREAK_RETEST_ATR = 0.5
BREAK_CONFIRM_ATR = 0.1
PREMIUM_Z_WINDOW = 96
FUNDING_Z_WINDOW = 21
FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
PREMIUM_KLINES_URL = "https://fapi.binance.com/fapi/v1/premiumIndexKlines"
BINANCE_LIMIT = 1000
PREMIUM_FETCH_PAGES = 14
FUNDING_FETCH_PAGES = 3
REQ_TIMEOUT = 20


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


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def rolling_z(series: pd.Series, window: int) -> pd.Series:
    mean = series.rolling(window, min_periods=window).mean()
    std = series.rolling(window, min_periods=window).std(ddof=0)
    z = (series - mean) / std.replace(0, np.nan)
    return z


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


def fetch_paginated(url: str, params: dict[str, object], pages: int) -> list:
    rows: list = []
    end_time: int | None = None
    for _ in range(pages):
        req = dict(params)
        if end_time is not None:
            req["endTime"] = end_time
        resp = requests.get(url, params=req, timeout=REQ_TIMEOUT)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows = batch + rows
        if isinstance(batch[0], list):
            earliest = int(batch[0][0])
        else:
            earliest = int(batch[0]["fundingTime"])
        next_end = earliest - 1
        if end_time is not None and next_end >= end_time:
            break
        end_time = next_end
    return rows


def fetch_funding(symbol: str) -> pd.DataFrame:
    rows = fetch_paginated(FUNDING_URL, {"symbol": symbol, "limit": BINANCE_LIMIT}, FUNDING_FETCH_PAGES)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "funding_rate", "funding_z"])
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["fundingTime"], unit="ms", utc=True)
    df["funding_rate"] = pd.to_numeric(df["fundingRate"], errors="coerce")
    df = df[["timestamp", "funding_rate"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df["funding_z"] = rolling_z(df["funding_rate"], FUNDING_Z_WINDOW)
    return df


def fetch_premium_klines(symbol: str) -> pd.DataFrame:
    rows = fetch_paginated(PREMIUM_KLINES_URL, {"symbol": symbol, "interval": "15m", "limit": BINANCE_LIMIT}, PREMIUM_FETCH_PAGES)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "premium_close", "premium_z"])
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "ignore1", "close_time", "ignore2", "ignore3", "ignore4", "ignore5", "ignore6"
    ])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["premium_close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df[["timestamp", "premium_close"]].drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)
    df["premium_z"] = rolling_z(df["premium_close"], PREMIUM_Z_WINDOW)
    return df


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset)
    premium = fetch_premium_klines(symbol)
    funding = fetch_funding(symbol)

    frame = bars.merge(premium, on="timestamp", how="left")
    frame = pd.merge_asof(
        frame.sort_values("timestamp"),
        funding[["timestamp", "funding_rate", "funding_z"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    frame["ema_fast"] = frame["close"].ewm(span=EMA_FAST, adjust=False).mean()
    frame["ema_slow"] = frame["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    frame["ema_slope"] = frame["ema_fast"].pct_change(EMA_SLOPE_LOOKBACK)
    frame["atr14"] = compute_atr(frame)
    frame["rolling_low"] = frame["low"].rolling(BREAK_LOOKBACK, min_periods=BREAK_LOOKBACK).min().shift(1)
    frame["crowded_long"] = ((frame["funding_z"] > 0.5) & (frame["premium_z"] > 0.5)).fillna(False)
    frame["already_crowded_short"] = ((frame["funding_z"] < -0.5) | (frame["premium_z"] < 0)).fillna(False)
    return frame.reset_index(drop=True)


def base_short_signal(frame: pd.DataFrame, setup: str) -> pd.Series:
    if setup == "ema_short":
        state = (
            (frame["ema_fast"] < frame["ema_slow"])
            & (frame["ema_slope"] < -EMA_SLOPE_FLOOR)
            & (frame["close"] < frame["ema_fast"])
        )
        return (state & ~state.shift(1).fillna(False)).fillna(False)
    if setup == "breakdown_short":
        atr = frame["atr14"]
        rolling_low = frame["rolling_low"]
        setup_flag = (
            rolling_low.notna()
            & (frame["close"] < rolling_low - BREAK_CONFIRM_ATR * atr)
            & (frame["high"] <= rolling_low + BREAK_RETEST_ATR * atr)
        )
        return (setup_flag & ~setup_flag.shift(1).fillna(False)).fillna(False)
    raise ValueError(setup)


def variant_mask(frame: pd.DataFrame, variant: str) -> pd.Series:
    if variant == "no_gate":
        return pd.Series(True, index=frame.index)
    if variant == "crowded_long_only":
        return frame["crowded_long"].fillna(False)
    if variant == "already_crowded_short_veto":
        return (~frame["already_crowded_short"]).fillna(False)
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    short_sig = (base_short_signal(frame, setup) & variant_mask(frame, variant)).fillna(False)
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(1, len(frame) - 2):
        if idx <= last_exit_idx or not bool(short_sig.iloc[idx]):
            continue
        signal_events += 1
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            break
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = (entry_px / exit_px - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0

        ft: dict[int, float] = {}
        for bars in FOLLOW_THROUGH_BARS:
            probe_idx = min(len(frame) - 1, entry_idx + bars - 1)
            ft[bars] = (entry_px / float(frame.iloc[probe_idx]["close"]) - 1.0)

        probe_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        false_break = int(float(frame.iloc[probe_idx]["close"]) > entry_px)

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "follow_through_4bars": ft[4],
                "follow_through_8bars": ft[8],
                "follow_through_16bars": ft[16],
                "false_break_4bars": false_break,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "crowded_long": int(bool(frame.iloc[idx]["crowded_long"])),
                "already_crowded_short": int(bool(frame.iloc[idx]["already_crowded_short"])),
                "funding_rate": float(frame.iloc[idx]["funding_rate"]) if pd.notna(frame.iloc[idx]["funding_rate"]) else np.nan,
                "funding_z": float(frame.iloc[idx]["funding_z"]) if pd.notna(frame.iloc[idx]["funding_z"]) else np.nan,
                "premium_close": float(frame.iloc[idx]["premium_close"]) if pd.notna(frame.iloc[idx]["premium_close"]) else np.nan,
                "premium_z": float(frame.iloc[idx]["premium_z"]) if pd.notna(frame.iloc[idx]["premium_z"]) else np.nan,
            }
        )
        last_exit_idx = exit_idx

    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_break_4bars_rate": np.nan,
            "follow_through_4bars": np.nan,
            "follow_through_8bars": np.nan,
            "follow_through_16bars": np.nan,
            "crowded_long_share": np.nan,
            "already_crowded_short_share": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_break_4bars_rate": float(trades["false_break_4bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
        "follow_through_8bars": float(trades["follow_through_8bars"].mean()),
        "follow_through_16bars": float(trades["follow_through_16bars"].mean()),
        "crowded_long_share": float(trades["crowded_long"].mean()),
        "already_crowded_short_share": float(trades["already_crowded_short"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            raw_map = (
                out[(out["setup"] == setup) & (out["variant"] == "no_gate") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / raw_map.get(r["asset"], np.nan)) if raw_map.get(r["asset"], 0) else np.nan,
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
    if tmp.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
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


def verdict_lines(overall: pd.DataFrame) -> tuple[str, list[str]]:
    primary = overall[(overall["setup"] == "ema_short") & (overall["variant"] == "crowded_long_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "hard verdict：缺少 Rank 49 的主读法结果。", ["主读法 `ema_short + crowded_long_only @ 6bps` 未产出。"]
    row = primary.iloc[0]
    notes = [
        f"`ema_short + crowded_long_only @ 6bps`：mean_total_return≈{pct(row['mean_total_return'])}、positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'])}、mean_false_break_4bars_rate≈{pct(row['mean_false_break_4bars_rate'])}。"
    ]
    if row["mean_total_return"] <= 0 or row["positive_asset_ratio"] < (2 / 3):
        return (
            "hard verdict：Rank 49 / funding-basis crowded-long unwind gate 在当前最小 clean replication 下仍更像 `park / evidence pool`；它最多只是在少数 pocket 帮 short setup 少亏，但还没诚实到能当默认 overlay 升格。",
            notes,
        )
    return (
        "hard verdict：Rank 49 在当前最小 clean replication 下拿到了可继续观察的正向 first verdict，但仍只配留在 paper candidate 讨论前的证据位，不应直接抢占 desk 主线。",
        notes,
    )


def build_report_html(overall: pd.DataFrame, asset_level: pd.DataFrame, pocket: pd.DataFrame, verdict: str, notes: list[str], generated_at: str) -> str:
    overall_view = overall.copy()
    overall_view["mean_total_return"] = overall_view["mean_total_return"].map(lambda x: pct(x))
    overall_view["positive_asset_ratio"] = overall_view["positive_asset_ratio"].map(lambda x: pct(x))
    overall_view["mean_avg_net_ret"] = overall_view["mean_avg_net_ret"].map(lambda x: pct(x))
    overall_view["mean_false_break_4bars_rate"] = overall_view["mean_false_break_4bars_rate"].map(lambda x: pct(x))
    overall_view["mean_trade_count_retention"] = overall_view["mean_trade_count_retention"].map(lambda x: pct(x))
    pocket_view = pocket.copy()
    if not pocket_view.empty:
        pocket_view["mean_total_return"] = pocket_view["mean_total_return"].map(lambda x: pct(x))
        pocket_view["positive_asset_ratio"] = pocket_view["positive_asset_ratio"].map(lambda x: pct(x))
    asset_view = asset_level.copy()
    asset_view = asset_view[(asset_view["cost_bps_per_side"] == PRIMARY_COST)].copy()
    for col in ["total_return", "avg_net_ret", "win_rate", "false_break_4bars_rate", "trade_count_retention"]:
        if col in asset_view.columns:
            asset_view[col] = asset_view[col].map(lambda x: pct(x))

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 49 · funding/basis crowded-long gate clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.7; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:16px 18px; margin:14px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ border:1px solid #e5e7eb; padding:6px 8px; text-align:left; vertical-align:top; }}
    th {{ background:#f3f4f6; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    .muted {{ color:#6b7280; }}
  </style>
</head>
<body>
  <p><a href='../reading/repo_scout/funding_basis_crowding_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 49 · funding/basis crowded-long unwind gate（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)}｜固定 BTC/ETH/SOL 120d 15m cache，执行统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>

  <div class='card'>
    <h2>本轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 49 只拿 1 次最小预算：<b>funding / premium crowding</b> 这种拥挤度过滤层，能不能在不过度砍样本的前提下，让 <code>ema_short</code> 或 <code>breakdown_short</code> 的 15m short setup 更诚实？</p>
    <p><span class='pill'>只做 clean replication，不做 admission wording 扩写</span></p>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li><b>base setup A / ema_short</b>：<code>EMA9 &lt; EMA15</code> 且斜率为负、价格在快线下方时，取第一次 short continuation。</li>
      <li><b>base setup B / breakdown_short</b>：跌破最近 <code>20</code> 根低点后，价格仍留在 breakdown 下方的最小 continuation。</li>
      <li><b>crowded_long_only</b>：仅当 <code>funding_z &gt; 0.5</code> 且 <code>premium_z &gt; 0.5</code> 时放行 short。</li>
      <li><b>already_crowded_short_veto</b>：若 <code>funding_z &lt; -0.5</code> 或 <code>premium_z &lt; 0</code>，则禁止继续追 short。</li>
      <li>数据只用入场前最后一个已发布的 funding（8h）与 premium（15m premium index kline），避免同 bar 泄漏。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <ul>{''.join(f'<li>{escape(line)}</li>' for line in notes)}</ul>
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view)}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view)}
  </div>

  <div class='card'>
    <h2>time-pocket honesty</h2>
    {render_table(pocket_view)}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    signal_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame[["timestamp", "funding_rate", "funding_z", "premium_close", "premium_z", "crowded_long", "already_crowded_short"]].to_csv(
            ART_DIR / f"{symbol.lower()}_crowding_features.csv", index=False
        )
        for setup in BASE_SETUPS:
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, signal_events = build_trades(frame, setup, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=signal_events))
                    signal_rows.append({
                        "asset": asset,
                        "setup": setup,
                        "variant": variant,
                        "cost_bps_per_side": cost,
                        "signal_events": signal_events,
                    })

    asset_level = add_trade_retention(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    pd.DataFrame(signal_rows).to_csv(ART_DIR / "signal_event_counts.csv", index=False)
    asset_level.to_csv(ART_DIR / "asset_summary.csv", index=False)

    overall = (
        asset_level.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_false_break_4bars_rate=("false_break_4bars_rate", "mean"),
            mean_follow_through_4bars=("follow_through_4bars", "mean"),
            mean_follow_through_8bars=("follow_through_8bars", "mean"),
            mean_follow_through_16bars=("follow_through_16bars", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)

    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)

    verdict, notes = verdict_lines(overall)
    report_html = build_report_html(overall, asset_level, pockets, verdict, notes, generated_at)
    (SITE_DIR / "report.html").write_text(report_html, encoding="utf-8")


if __name__ == "__main__":
    main()
