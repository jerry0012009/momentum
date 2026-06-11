#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank274_survivor_followup"
CACHE_DIR = ART_DIR / "kline_cache"
ART_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://data.binance.vision/data/futures/um"
LOOKBACK_DAYS = 900
DAILY_WARMUP_DAYS = 260
COSTS_BPS_PER_SIDE = [6.0, 10.0, 14.0]
BASE_SYMBOLS = ["ETHUSDT", "BTCUSDT", "SOLUSDT"]
INTERVALS = {
    "ETHUSDT": ["5m", "15m"],
    "BTCUSDT": ["5m"],
    "SOLUSDT": ["5m"],
}
RETRIES = 5
REQUEST_SLEEP_SEC = 0.05

COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume", "close_time",
    "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore",
]


def month_start(d: date) -> date:
    return d.replace(day=1)


def next_month(d: date) -> date:
    if d.month == 12:
        return d.replace(year=d.year + 1, month=1, day=1)
    return d.replace(month=d.month + 1, day=1)


def date_range(start: date, stop: date):
    cur = start
    while cur < stop:
        yield cur
        cur += timedelta(days=1)


def fetch_bytes(url: str) -> bytes:
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 OpenClaw Rank274/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last = exc
        except Exception as exc:  # noqa: BLE001
            last = exc
        if attempt < RETRIES - 1:
            time.sleep(1.0 + attempt)
    raise RuntimeError(f"failed fetch: {url} :: {last}")


def load_zip_csv(cache_path: Path, url: str) -> pd.DataFrame:
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        return df

    raw = fetch_bytes(url)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = zf.namelist()[0]
        with zf.open(name) as fh:
            df = pd.read_csv(fh, header=None, names=COLUMNS)
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df[df["open_time"].notna()].copy()
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ts"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    out = df[["ts", "open", "high", "low", "close", "volume", "quote_volume"]].drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    out.to_csv(cache_path, index=False)
    time.sleep(REQUEST_SLEEP_SEC)
    return out


def load_monthly(symbol: str, interval: str, ym: str) -> pd.DataFrame | None:
    cache_path = CACHE_DIR / f"monthly_{symbol}_{interval}_{ym}.csv"
    url = f"{BASE_URL}/monthly/klines/{symbol}/{interval}/{symbol}-{interval}-{ym}.zip"
    try:
        return load_zip_csv(cache_path, url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def load_daily(symbol: str, interval: str, ymd: str) -> pd.DataFrame | None:
    cache_path = CACHE_DIR / f"daily_{symbol}_{interval}_{ymd}.csv"
    url = f"{BASE_URL}/daily/klines/{symbol}/{interval}/{symbol}-{interval}-{ymd}.zip"
    try:
        return load_zip_csv(cache_path, url)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def collect_klines(symbol: str, interval: str, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    start_d = start_dt.date()
    end_d = end_dt.date()
    pieces: list[pd.DataFrame] = []

    end_month = month_start(end_d)
    cur_month = month_start(start_d)
    while cur_month < end_month:
        ym = f"{cur_month.year:04d}-{cur_month.month:02d}"
        frame = load_monthly(symbol, interval, ym)
        if frame is not None:
            pieces.append(frame)
        cur_month = next_month(cur_month)

    for d in date_range(end_month, end_d):
        ymd = f"{d.year:04d}-{d.month:02d}-{d.day:02d}"
        frame = load_daily(symbol, interval, ymd)
        if frame is not None:
            pieces.append(frame)

    if not pieces:
        raise RuntimeError(f"no pieces for {symbol} {interval}")

    df = pd.concat(pieces, ignore_index=True).drop_duplicates("ts").sort_values("ts").reset_index(drop=True)
    df = df[(df["ts"] >= start_dt) & (df["ts"] < end_dt)].reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"empty filtered frame for {symbol} {interval}")
    return df


def build_daily(intraday: pd.DataFrame) -> pd.DataFrame:
    work = intraday.copy()
    work["session_date"] = work["ts"].dt.floor("D")
    daily = work.groupby("session_date", as_index=False).agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        bars=("open", "size"),
    )
    daily["sma200"] = daily["close"].rolling(200, min_periods=200).mean()
    return daily


def summarize_trades(trades: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if trades.empty:
        return pd.DataFrame(columns=[
            "symbol", "interval", "cost_bps_side", "trades", "win_rate", "stop_rate",
            "mean_raw_bps", "median_raw_bps", "mean_net_bps", "median_net_bps",
            "total_net_pct", "years_positive", "first_half_net_pct", "second_half_net_pct",
        ])
    for (symbol, interval), sub in trades.groupby(["symbol", "interval"]):
        sub = sub.sort_values("trade_date").reset_index(drop=True)
        mid = len(sub) // 2
        for cost in COSTS_BPS_PER_SIDE:
            net_col = f"net_ret_{int(cost)}bps"
            year_sum = sub.groupby("year")[net_col].sum()
            first_half = sub.iloc[:mid][net_col].sum() if mid > 0 else np.nan
            second_half = sub.iloc[mid:][net_col].sum() if mid < len(sub) else np.nan
            rows.append({
                "symbol": symbol,
                "interval": interval,
                "cost_bps_side": cost,
                "trades": int(len(sub)),
                "win_rate": float((sub[net_col] > 0).mean()),
                "stop_rate": float((sub["exit_reason"] == "stop").mean()),
                "mean_raw_bps": float(sub["raw_ret"].mean() * 10000.0),
                "median_raw_bps": float(sub["raw_ret"].median() * 10000.0),
                "mean_net_bps": float(sub[net_col].mean() * 10000.0),
                "median_net_bps": float(sub[net_col].median() * 10000.0),
                "total_net_pct": float(sub[net_col].sum() * 100.0),
                "years_positive": int((year_sum > 0).sum()),
                "first_half_net_pct": float(first_half * 100.0) if pd.notna(first_half) else np.nan,
                "second_half_net_pct": float(second_half * 100.0) if pd.notna(second_half) else np.nan,
            })
    return pd.DataFrame(rows).sort_values(["symbol", "interval", "cost_bps_side"]).reset_index(drop=True)


def summarize_by_year(trades: pd.DataFrame, symbol: str, interval: str, cost: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    sub = trades[(trades["symbol"] == symbol) & (trades["interval"] == interval)].copy()
    if sub.empty:
        return pd.DataFrame()
    net_col = f"net_ret_{int(cost)}bps"
    out = sub.groupby("year", as_index=False).agg(
        trades=("trade_date", "size"),
        stop_rate=("exit_reason", lambda s: float((s == "stop").mean())),
        total_net_pct=(net_col, lambda s: float(s.sum() * 100.0)),
        mean_net_bps=(net_col, lambda s: float(s.mean() * 10000.0)),
    )
    return out.sort_values("year").reset_index(drop=True)


def interval_minutes(interval: str) -> int:
    return int(interval[:-1])


def simulate_symbol(symbol: str, interval: str, intraday: pd.DataFrame) -> pd.DataFrame:
    daily = build_daily(intraday)
    intraday = intraday.copy()
    intraday["session_date"] = intraday["ts"].dt.floor("D")
    rows = []
    intraday_by_date = {k: v.reset_index(drop=True) for k, v in intraday.groupby("session_date")}

    for i in range(3, len(daily)):
        prev_day = daily.iloc[i - 1]
        if pd.isna(prev_day["sma200"]) or prev_day["close"] <= prev_day["sma200"]:
            continue

        recent = daily.iloc[i - 3:i]
        if len(recent) < 3:
            continue
        rng = max(recent["high"].max() - recent["close"].min(), recent["close"].max() - recent["low"].min())
        if not np.isfinite(rng) or rng <= 0:
            continue

        day = pd.Timestamp(daily.iloc[i]["session_date"])
        day_bars = intraday_by_date.get(day)
        if day_bars is None or day_bars.empty:
            continue

        if day.tzinfo is None:
            day = day.tz_localize("UTC")
        else:
            day = day.tz_convert("UTC")
        start_ts = day + pd.Timedelta(hours=7)
        exit_ts = day + pd.Timedelta(hours=16)
        scan = day_bars[(day_bars["ts"] >= start_ts) & (day_bars["ts"] < exit_ts)].copy().reset_index(drop=True)
        if scan.empty:
            continue
        if scan.iloc[0]["ts"] != start_ts:
            continue

        anchor_open = float(scan.iloc[0]["open"])
        trigger = anchor_open + 0.5 * rng

        hit_idx = None
        for j in range(len(scan)):
            if float(scan.iloc[j]["high"]) > trigger:
                hit_idx = j
                break
        if hit_idx is None or hit_idx + 1 >= len(scan):
            continue

        entry_bar = scan.iloc[hit_idx + 1]
        entry_ts = pd.Timestamp(entry_bar["ts"])
        entry_price = float(entry_bar["open"])
        if not np.isfinite(entry_price) or entry_price <= 0:
            continue
        stop_price = entry_price * 0.99

        exit_row = day_bars[day_bars["ts"] == exit_ts]
        if exit_row.empty:
            continue
        exit_price = float(exit_row.iloc[0]["open"])
        exit_reason = "time"
        stop_hit_ts = None

        post_entry = day_bars[(day_bars["ts"] >= entry_ts) & (day_bars["ts"] < exit_ts)].copy().reset_index(drop=True)
        for _, bar in post_entry.iterrows():
            if float(bar["low"]) <= stop_price:
                exit_price = stop_price
                exit_reason = "stop"
                stop_hit_ts = pd.Timestamp(bar["ts"])
                break

        raw_ret = exit_price / entry_price - 1.0
        row = {
            "symbol": symbol,
            "interval": interval,
            "bar_minutes": interval_minutes(interval),
            "trade_date": pd.Timestamp(day).strftime("%Y-%m-%d"),
            "year": int(pd.Timestamp(day).year),
            "prev_close_vs_sma200": float(prev_day["close"] / prev_day["sma200"] - 1.0),
            "range_abs": float(rng),
            "range_pct_of_anchor": float(rng / anchor_open),
            "trigger": float(trigger),
            "trigger_hit_ts": pd.Timestamp(scan.iloc[hit_idx]["ts"]).strftime("%Y-%m-%d %H:%M:%S%z"),
            "entry_ts": entry_ts.strftime("%Y-%m-%d %H:%M:%S%z"),
            "entry_price": float(entry_price),
            "stop_price": float(stop_price),
            "exit_ts": (stop_hit_ts or exit_ts).strftime("%Y-%m-%d %H:%M:%S%z"),
            "exit_price": float(exit_price),
            "exit_reason": exit_reason,
            "raw_ret": float(raw_ret),
        }
        for cost in COSTS_BPS_PER_SIDE:
            c = cost / 10000.0
            row[f"net_ret_{int(cost)}bps"] = float((1.0 + raw_ret) * (1.0 - c) * (1.0 - c) - 1.0)
        rows.append(row)

    return pd.DataFrame(rows).sort_values(["trade_date", "entry_ts"]).reset_index(drop=True)


def main() -> None:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    data_end = now.replace(hour=0, minute=0)
    intraday_start = data_end - timedelta(days=LOOKBACK_DAYS)
    warmup_start = intraday_start - timedelta(days=DAILY_WARMUP_DAYS)

    all_trades = []
    fetch_meta = []
    for symbol in BASE_SYMBOLS:
        for interval in INTERVALS[symbol]:
            bars = collect_klines(symbol, interval, warmup_start, data_end)
            fetch_meta.append({
                "symbol": symbol,
                "interval": interval,
                "rows": int(len(bars)),
                "start_ts": str(bars["ts"].min()),
                "end_ts": str(bars["ts"].max()),
            })
            trades = simulate_symbol(symbol, interval, bars)
            trades.to_csv(ART_DIR / f"trades_{symbol}_{interval}.csv", index=False)
            all_trades.append(trades)

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    summary_df = summarize_trades(trades_df)
    summary_df.to_csv(ART_DIR / "summary.csv", index=False)
    pd.DataFrame(fetch_meta).to_csv(ART_DIR / "fetch_meta.csv", index=False)
    trades_df.to_csv(ART_DIR / "all_trades.csv", index=False)

    eth_5m_y = summarize_by_year(trades_df, "ETHUSDT", "5m", 10.0)
    eth_15m_y = summarize_by_year(trades_df, "ETHUSDT", "15m", 10.0)
    btc_5m_y = summarize_by_year(trades_df, "BTCUSDT", "5m", 10.0)
    sol_5m_y = summarize_by_year(trades_df, "SOLUSDT", "5m", 10.0)
    eth_5m_y.to_csv(ART_DIR / "eth_5m_yearly_10bps.csv", index=False)
    eth_15m_y.to_csv(ART_DIR / "eth_15m_yearly_10bps.csv", index=False)
    btc_5m_y.to_csv(ART_DIR / "btc_5m_yearly_10bps.csv", index=False)
    sol_5m_y.to_csv(ART_DIR / "sol_5m_yearly_10bps.csv", index=False)

    lookup = {(r["symbol"], r["interval"], int(r["cost_bps_side"])): r for r in summary_df.to_dict(orient="records")}
    eth5_10 = lookup.get(("ETHUSDT", "5m", 10), {})
    eth15_10 = lookup.get(("ETHUSDT", "15m", 10), {})

    eth_positive_years = int(eth_5m_y["total_net_pct"].gt(0).sum()) if not eth_5m_y.empty else 0
    eth_first_half = float(eth5_10.get("first_half_net_pct", np.nan)) if eth5_10 else np.nan
    eth_second_half = float(eth5_10.get("second_half_net_pct", np.nan)) if eth5_10 else np.nan

    promote = bool(
        eth5_10
        and float(eth5_10.get("trades", 0)) >= 20
        and float(eth5_10.get("mean_net_bps", np.nan)) > 0
        and float(eth5_10.get("total_net_pct", np.nan)) > 0
        and eth_positive_years >= 2
        and pd.notna(eth_first_half) and pd.notna(eth_second_half)
        and eth_first_half > 0 and eth_second_half > 0
        and float(eth15_10.get("total_net_pct", np.nan)) < float(eth5_10.get("total_net_pct", np.nan))
    )

    decision = {
        "generated_at_utc": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "data_end_utc": data_end.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "lookback_days": LOOKBACK_DAYS,
        "daily_warmup_days": DAILY_WARMUP_DAYS,
        "rule": "prior-day close > SMA200; range=max(HH-LC,HC-LL) over prior 3 completed UTC days; anchor open=07:00 UTC; trigger=anchor+0.5*range; honest execution=next-bar open after first bar with high>trigger; one trade/day; 1% stop; 16:00 UTC time exit; fixed-size return sums",
        "costs_bps_per_side": COSTS_BPS_PER_SIDE,
        "summary_rows": summary_df.to_dict(orient="records"),
        "eth_5m_yearly_10bps": eth_5m_y.to_dict(orient="records"),
        "eth_15m_yearly_10bps": eth_15m_y.to_dict(orient="records"),
        "btc_5m_yearly_10bps": btc_5m_y.to_dict(orient="records"),
        "sol_5m_yearly_10bps": sol_5m_y.to_dict(orient="records"),
    }
    if promote:
        decision["verdict"] = "promote_P2"
        decision["one_line"] = "Rank 274 在 900d 更长窗口、honest next-bar-open 与 10bps/side 成本下，ETH 5m 仍保留多年份正 pocket，且前后半样本都为正、明显优于 15m；这更像可进入 P2 admission 的 ETH-specific raw alpha，而不是 210d 幸运窗口。"
    else:
        decision["verdict"] = "background_P0"
        decision["one_line"] = "Rank 274 在更长窗口下没有把 ETH 5m after-cost pocket 证明成跨年份、跨半样本都站得住的稳边；若再叠 BTC/SOL falsification 与 15m 对照，它更像 ETH-only 且执行敏感的薄 pocket，不够诚实地升 P2。"
    (ART_DIR / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
