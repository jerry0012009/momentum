#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
R32B_SCRIPT = ROOT / "scripts" / "build_rank32b_slope_floor_continuation.py"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
PRIMARY_COST = 6.0
ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
DEFAULT_DAYS = 365


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


base_mod = load_module(BASE_SCRIPT, "rank32_base_mod")
r32b_mod = load_module(R32B_SCRIPT, "rank32b_mod")


def fetch_binance_bars(symbol: str, days: int = DEFAULT_DAYS, interval: str = "15m") -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        params = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urllib.request.urlopen(f"https://api.binance.com/api/v3/klines?{params}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
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
    out = out.dropna().sort_values("timestamp").reset_index(drop=True)
    return out


def _build_completed_hours_from_15m(bars: pd.DataFrame) -> pd.DataFrame:
    work = bars.copy().sort_values("timestamp").reset_index(drop=True)
    work["timestamp"] = pd.to_datetime(work["timestamp"], utc=True)
    work["hour_start"] = work["timestamp"].dt.floor("1h")
    hours = (
        work.groupby("hour_start", sort=True)
        .agg(hour_close=("close", "last"))
        .reset_index()
        .sort_values("hour_start")
        .reset_index(drop=True)
    )
    fast_vals: list[float] = []
    slow_vals: list[float] = []
    prev_fast = math.nan
    prev_slow = math.nan
    alpha_fast = 2.0 / (base_mod.EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (base_mod.EMA_SLOW_1H + 1.0)
    for close in hours["hour_close"].astype(float):
        if not math.isfinite(prev_fast):
            prev_fast = close
            prev_slow = close
        else:
            prev_fast = alpha_fast * close + (1.0 - alpha_fast) * prev_fast
            prev_slow = alpha_slow * close + (1.0 - alpha_slow) * prev_slow
        fast_vals.append(prev_fast)
        slow_vals.append(prev_slow)
    hours["ema_fast_hour"] = fast_vals
    hours["ema_slow_hour"] = slow_vals
    return hours


def build_rank32b_frame_from_bars(asset: str, bars: pd.DataFrame) -> pd.DataFrame:
    frame = bars.copy().sort_values("timestamp").reset_index(drop=True)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["asset"] = asset

    hour_df = _build_completed_hours_from_15m(frame)
    frame["signal_confirmed_at"] = frame["timestamp"] + pd.Timedelta(minutes=15)
    frame["hour_start"] = frame["signal_confirmed_at"].dt.floor("1h")

    hour_map = hour_df[["hour_start", "ema_fast_hour", "ema_slow_hour"]].copy()
    hour_map["prev_hour_start"] = hour_map["hour_start"] + pd.Timedelta(hours=1)
    hour_map = hour_map[["prev_hour_start", "ema_fast_hour", "ema_slow_hour"]].rename(
        columns={"prev_hour_start": "hour_start", "ema_fast_hour": "prev_hour_fast", "ema_slow_hour": "prev_hour_slow"}
    )
    frame = frame.merge(hour_map, on="hour_start", how="left")

    alpha_fast = 2.0 / (base_mod.EMA_FAST_1H + 1.0)
    alpha_slow = 2.0 / (base_mod.EMA_SLOW_1H + 1.0)
    frame["ema_fast_1h"] = alpha_fast * frame["close"] + (1.0 - alpha_fast) * frame["prev_hour_fast"]
    frame["ema_slow_1h"] = alpha_slow * frame["close"] + (1.0 - alpha_slow) * frame["prev_hour_slow"]
    frame["fast_slope"] = frame["ema_fast_1h"] / frame["prev_hour_fast"] - 1.0
    frame["slow_slope"] = frame["ema_slow_1h"] / frame["prev_hour_slow"] - 1.0
    frame["spread_mid"] = (frame["ema_fast_1h"] + frame["ema_slow_1h"]) / 2.0
    frame["long_structure"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["short_structure"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["slope_floor_long"] = ((frame["fast_slope"] > base_mod.SLOPE_FLOOR) & (frame["slow_slope"] > 0)).fillna(False).astype(int)
    frame["slope_floor_short"] = ((frame["fast_slope"] < -base_mod.SLOPE_FLOOR) & (frame["slow_slope"] < 0)).fillna(False).astype(int)
    frame["slope_strength"] = frame["fast_slope"].abs().fillna(0.0) + frame["slow_slope"].abs().fillna(0.0)

    prev_close = frame["close"].shift(1)
    prev_fast = frame["ema_fast_1h"].shift(1)
    prev_mid = frame["spread_mid"].shift(1)
    recent_low = frame["low"].shift(1).rolling(base_mod.RECLAIM_LOOKBACK, min_periods=base_mod.RECLAIM_LOOKBACK).min()
    recent_high = frame["high"].shift(1).rolling(base_mod.RECLAIM_LOOKBACK, min_periods=base_mod.RECLAIM_LOOKBACK).max()
    frame["cross_only_long"] = ((frame["long_structure"] == 1) & (prev_close <= prev_fast) & (frame["close"] > frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["cross_only_short"] = ((frame["short_structure"] == 1) & (prev_close >= prev_fast) & (frame["close"] < frame["ema_fast_1h"])).fillna(False).astype(int)
    frame["slope_floor_long_signal"] = ((frame["cross_only_long"] == 1) & (frame["slope_floor_long"] == 1)).astype(int)
    frame["slope_floor_short_signal"] = ((frame["cross_only_short"] == 1) & (frame["slope_floor_short"] == 1)).astype(int)
    frame["reclaim_long_signal"] = ((frame["long_structure"] == 1) & (frame["slope_floor_long"] == 1) & (recent_low <= prev_mid) & (frame["close"] > frame["ema_fast_1h"]) & (frame["close"] > frame["spread_mid"]) & (prev_close <= prev_mid)).fillna(False).astype(int)
    frame["reclaim_short_signal"] = ((frame["short_structure"] == 1) & (frame["slope_floor_short"] == 1) & (recent_high >= prev_mid) & (frame["close"] < frame["ema_fast_1h"]) & (frame["close"] < frame["spread_mid"]) & (prev_close >= prev_mid)).fillna(False).astype(int)
    return frame


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
    rows = []
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
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def build_extended_time_summary(trades: pd.DataFrame, bucket_count: int) -> pd.DataFrame:
    if trades.empty or len(trades) < max(24, bucket_count * 3):
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = trades.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    work["time_bucket"] = pd.qcut(work["event_ts"].view("int64"), q=bucket_count, labels=[f"bucket_{i}" for i in range(1, bucket_count + 1)], duplicates="drop")
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "time_bucket": str(bucket),
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_extended_window_compare(trades: pd.DataFrame, days: int) -> pd.DataFrame:
    if trades.empty or len(trades) < 24:
        return pd.DataFrame(columns=["window", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = trades.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    end = work["event_ts"].max()
    start = work["event_ts"].min()
    total_days = max((end - start).days, 1)
    if days >= 5 * 365 - 30 and total_days >= 4 * 365:
        edges = [end - pd.Timedelta(days=365 * i) for i in range(5, 0, -1)]
        windows = []
        lower = start
        for idx, upper in enumerate(edges[1:], start=1):
            label = f"year_{idx}"
            windows.append((label, work[(work["event_ts"] >= lower) & (work["event_ts"] < upper)]))
            lower = upper
        windows.append(("year_5_recent", work[work["event_ts"] >= edges[-1]]))
    else:
        if total_days < 240:
            return pd.DataFrame(columns=["window", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
        cut_recent = end - pd.Timedelta(days=120)
        cut_mid = end - pd.Timedelta(days=240)
        windows = [
            ("older_365d_to_240d", work[work["event_ts"] < cut_mid]),
            ("middle_240d_to_120d", work[(work["event_ts"] >= cut_mid) & (work["event_ts"] < cut_recent)]),
            ("recent_120d", work[work["event_ts"] >= cut_recent]),
        ]
    rows = []
    for name, grp in windows:
        if grp.empty:
            continue
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "window": name,
                "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
                "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
                "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
                "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def run_probe(days: int, bucket_count: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    asset_rows = []
    primary_trades = []
    for asset, symbol in ASSETS.items():
        bars = fetch_binance_bars(symbol, days=days)
        bars["asset"] = asset
        frame = build_rank32b_frame_from_bars(asset, bars)
        trades, no_trade_ratio, eligible_bars = base_mod.build_trades(frame, asset, PRIMARY_VARIANT, PRIMARY_COST)
        if not trades.empty:
            primary_trades.append(trades)
        asset_rows.append(
            base_mod.summarize_asset(
                trades,
                asset=asset,
                variant=PRIMARY_VARIANT,
                cost_bps=PRIMARY_COST,
                no_trade_ratio=no_trade_ratio,
                eligible_bars=eligible_bars,
            )
        )
    asset_summary = pd.DataFrame(asset_rows)
    overall = base_mod.summarize_overall(asset_summary)
    overall = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].reset_index(drop=True)
    trades_df = pd.concat([df for df in primary_trades if not df.empty], ignore_index=True) if primary_trades else pd.DataFrame()
    bucket_summary = build_extended_time_summary(trades_df, bucket_count=bucket_count)
    window_compare = build_extended_window_compare(trades_df, days=days)
    return overall, asset_summary, trades_df, bucket_summary, window_compare


def inject_section(report_path: Path, html_block: str, marker_id: str) -> None:
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
    parser = argparse.ArgumentParser(description="Build longer-history robustness probe for Rank 32b.")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--bucket-count", type=int, default=6)
    args = parser.parse_args()

    days = int(args.days)
    bucket_count = int(args.bucket_count)
    label = f"{days}d"
    marker_id = f"rank32b-{label}-robustness"

    overall, asset_summary, trades_df, bucket_summary, window_compare = run_probe(days=days, bucket_count=bucket_count)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    overall.to_csv(ART_DIR / f"extended_history_{label}_overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / f"extended_history_{label}_asset_summary.csv", index=False)
    trades_df.to_csv(ART_DIR / f"extended_history_{label}_trades.csv", index=False)
    bucket_summary.to_csv(ART_DIR / f"extended_history_{label}_time_buckets.csv", index=False)
    window_compare.to_csv(ART_DIR / f"extended_history_{label}_window_compare.csv", index=False)

    if overall.empty:
        headline = f"{label} 扩展历史样本未形成可用 trades。"
        note = "当前 extended-history probe 没拿到足够样本，暂不增加 reader-facing 结论。"
    else:
        row = overall.iloc[0]
        headline = (
            f"{label} 扩展历史下，主变体 {PRIMARY_VARIANT} 在 6bps/side：mean_total_return≈{pct(row['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(row['positive_asset_ratio'])}、mean_trades≈{num(row['mean_trades'],1)}、"
            f"mean_false_reclaim_ratio≈{pct(row['mean_false_reclaim_ratio'])}、mean_no_trade_ratio≈{pct(row['mean_no_trade_ratio'])}。"
        )
        pos_buckets = int((bucket_summary["mean_total_return"] > 0).sum()) if not bucket_summary.empty else 0
        total_buckets = int(len(bucket_summary))
        if days >= 5 * 365 - 30:
            note = (
                f"这组额外证据不是新的主 verdict，只是更久历史的 robustness 补充。当前 {label} 时间分桶里正收益 bucket = {pos_buckets}/{total_buckets}；"
                f"另外把整段历史拆成 5 个年度样本来对照，用来检查它是否只是某一段牛熊口袋有效。"
            )
        else:
            note = (
                f"这组额外证据不是新的主 verdict，只是更久历史的 robustness 补充。当前 {label} 时间分桶里正收益 bucket = {pos_buckets}/{total_buckets}；"
                f"若 older/middle/recent 三段都没塌，说明 Rank 32b 不只是最近 120d 的偶然口袋。"
            )

    block = f"""
  <div class='card'>
    <h2>extended-history robustness（{escape(label)}）</h2>
    <p class='muted'>新增时间：{escape(generated_at)} ｜ 样本：Binance spot 15m ｜ 窗口：最近 {days} 天 ｜ 角色：reader-facing 补充证据，不替代原 120d clean replication 主 verdict。</p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(note)}</p>
    <h3>{escape(label)} 分资产摘要</h3>
    {render_table(asset_summary[["asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"}, digits_cols={"trades":0})}
    <h3>{escape(label)} 时间稳定性（{bucket_count} buckets）</h3>
    {render_table(bucket_summary[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
    <h3>{'5 个年度样本对照' if days >= 5 * 365 - 30 else 'older / middle / recent 三段对照'}</h3>
    {render_table(window_compare[["window","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>"""

    for path in [SITE_DIR / "report.html", ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout" / "rank32b_slope_floor_continuation_clean_replication.html"]:
        inject_section(path, block, marker_id=marker_id)

    print(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "days": days,
        "overall_rows": int(len(overall)),
        "time_buckets": int(len(bucket_summary)),
        "window_rows": int(len(window_compare)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
