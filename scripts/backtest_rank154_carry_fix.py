#!/usr/bin/env python3
"""Rank 154 backtest with corrected carry signal (last settled funding rate).

Replays the strategy from 2026-01-01 to today using Binance historical data.
Universe is causal: top 30 by 30d rolling quote volume, age >= 180 days.
Carry signal uses last settled funding rate per day (no interval bias).

Usage:
    python scripts/backtest_rank154_carry_fix.py
    python scripts/backtest_rank154_carry_fix.py --days 90
    python scripts/backtest_rank154_carry_fix.py --start 2026-03-25
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.strategies import rank154_crypto_stat_arb as signal

# --- Config ---
INITIAL_EQUITY = 10_000.0
COST_BPS_PER_SIDE = 5.0
UNIVERSE_SIZE = 30
TOP_PROBE = 80  # fetch more symbols for better historical coverage
MIN_LISTING_DAYS = 180
MAX_ABS_WEIGHT = 0.10
MIN_EFFECTIVE_WEIGHT = 0.005
WEIGHT_BUFFER = 0.01
KLINE_LIMIT = 150
REQUEST_SLEEP = 0.08

FUTURES_TICKER = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"
FUTURES_FUNDING = "https://fapi.binance.com/fapi/v1/fundingRate"
FUTURES_EXCHANGE = "https://fapi.binance.com/fapi/v1/exchangeInfo"

ART_DIR = ROOT / "reports" / "artifacts" / "rank154_backtest_fix"


def fetch_json(url: str, params: dict | None = None) -> Any:
    import urllib.request
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    resp = urllib.request.urlopen(url, timeout=30)
    return json.loads(resp.read())


def iso_z(ts: pd.Timestamp) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Data fetching ---

def fetch_exchange_info() -> dict[str, dict]:
    """Fetch symbol metadata."""
    data = fetch_json(FUTURES_EXCHANGE)
    info = {}
    for s in data.get("symbols", []):
        if s.get("contractType") != "PERPETUAL":
            continue
        base = s.get("baseAsset", "")
        stable_bases = {"USDT", "USDC", "FDUSD", "BUSD", "USDP", "TUSD", "USDE", "USDS", "DAI"}
        plain = bool(base) and base.isalpha() and base.upper() == base and base not in stable_bases
        onboard = s.get("onboardDate", 0)
        info[s["symbol"]] = {
            "symbol": s["symbol"],
            "base_asset": base,
            "plain_alpha_base": plain,
            "onboard_ms": int(onboard) if onboard else 0,
        }
    return info


def fetch_top_symbols(n: int) -> list[str]:
    """Get top N symbols by 24h quote volume."""
    tickers = fetch_json(FUTURES_TICKER)
    ranked = sorted(tickers, key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)
    return [t["symbol"] for t in ranked[:n]]


def fetch_symbol_data(symbol: str, info: dict) -> pd.DataFrame:
    """Fetch klines + funding for one symbol."""
    # Klines
    klines = fetch_json(FUTURES_KLINES, {"symbol": symbol, "interval": "1d", "limit": KLINE_LIMIT})
    if not klines:
        return pd.DataFrame()

    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore",
    ])
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    df = df[pd.to_numeric(df["close_time"], errors="coerce") < now_ms].copy()
    if df.empty:
        return pd.DataFrame()

    frame = pd.DataFrame({
        "date": pd.to_datetime(pd.to_numeric(df["open_time"], errors="coerce"), unit="ms", utc=True).dt.floor("D"),
        "close": pd.to_numeric(df["close"], errors="coerce"),
        "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce"),
    })
    frame = frame.dropna().sort_values("date").reset_index(drop=True)

    # Funding
    start_ms = int(frame["date"].min().timestamp() * 1000)
    funding_rows = []
    current = start_ms
    while True:
        data = fetch_json(FUTURES_FUNDING, {"symbol": symbol, "startTime": current, "limit": 1000})
        if not data:
            break
        funding_rows.extend(data)
        last_ts = int(data[-1].get("fundingTime", 0))
        if len(data) < 1000 or last_ts <= current:
            break
        current = last_ts + 1
        time.sleep(REQUEST_SLEEP)

    if funding_rows:
        fdf = pd.DataFrame(funding_rows)
        fdf["ts"] = pd.to_datetime(pd.to_numeric(fdf["fundingTime"], errors="coerce"), unit="ms", utc=True)
        fdf["fr"] = pd.to_numeric(fdf["fundingRate"], errors="coerce")
        fdf["mp"] = pd.to_numeric(fdf.get("markPrice", pd.Series(dtype=float)), errors="coerce")
        fdf = fdf.dropna(subset=["ts", "fr"])
        fdf["date"] = fdf["ts"].dt.floor("D")
        # Daily aggregation
        daily = fdf.groupby("date").agg(
            funding_rate_last=("fr", "last"),
            funding_rate_sum=("fr", "sum"),
            funding_count=("fr", "count"),
        ).reset_index()
        frame = frame.merge(daily, on="date", how="left")

    frame["funding_rate_last"] = frame.get("funding_rate_last", pd.Series(dtype=float)).fillna(0.0)
    frame["funding_rate_sum"] = frame.get("funding_rate_sum", pd.Series(dtype=float)).fillna(0.0)
    frame["funding_count"] = frame.get("funding_count", pd.Series(dtype=float)).fillna(0).astype(int)

    # Signal features
    meta = info.get(symbol, {})
    frame["symbol"] = symbol
    frame["base_asset"] = meta.get("base_asset", "")
    frame["plain_alpha_base"] = meta.get("plain_alpha_base", False)
    onboard_ms = meta.get("onboard_ms", 0)
    frame["listing_days"] = (frame["date"] - pd.to_datetime(onboard_ms, unit="ms", utc=True)).dt.total_seconds() / 86400.0
    frame["trail_quote_volume_30d"] = frame["quote_volume"].rolling(30, min_periods=30).mean()
    frame["momo_10d"] = frame["close"].pct_change(10)
    # Breakout
    def _dsh(arr):
        a = np.asarray(arr, dtype=float)
        if len(a) == 0 or np.all(np.isnan(a)):
            return np.nan
        return float(len(a) - 1 - int(np.nanargmax(a)))
    frame["days_since_20d_high"] = frame["close"].rolling(20, min_periods=20).apply(_dsh, raw=True)
    frame["breakout_raw"] = 19.0 - frame["days_since_20d_high"]
    # Carry: use last settled rate (no interval bias)
    frame["carry_raw"] = frame["funding_rate_last"]
    frame["guard_pass"] = (
        frame["plain_alpha_base"]
        & (frame["listing_days"] >= MIN_LISTING_DAYS)
        & frame["trail_quote_volume_30d"].notna()
        & frame["momo_10d"].notna()
        & frame["breakout_raw"].notna()
    )
    return frame.sort_values("date").reset_index(drop=True)


# --- Strategy logic ---

def build_universe(frames: dict[str, pd.DataFrame], date: pd.Timestamp) -> pd.DataFrame:
    """Build universe for a given date using causal 30d rolling volume."""
    rows = []
    for sym, f in frames.items():
        row = f[f["date"] == date]
        if row.empty:
            continue
        rows.append(row.iloc[0].to_dict())
    if not rows:
        return pd.DataFrame()
    panel = pd.DataFrame(rows)
    eligible = panel[panel["guard_pass"]].copy()
    eligible = eligible.sort_values("trail_quote_volume_30d", ascending=False).reset_index(drop=True)
    universe = eligible.head(UNIVERSE_SIZE).copy().reset_index(drop=True)
    if universe.empty:
        return universe
    # Score
    for col, raw_col in [("carry", "carry_raw"), ("momo", "momo_10d"), ("breakout", "breakout_raw")]:
        ranks = universe[raw_col].rank(method="first")
        q = max(2, min(10, len(universe)))
        dec = pd.qcut(ranks, q=q, labels=False, duplicates="drop") + 1.0
        universe[f"{col}_decile"] = dec
        universe[f"{col}_centered"] = dec - dec.mean()
    universe["combined"] = 0.5 * universe["carry_centered"] + 0.2 * universe["momo_centered"] + 0.3 * universe["breakout_centered"]
    universe["combined"] = universe["combined"] - universe["combined"].mean()
    denom = float(universe["combined"].abs().sum())
    universe["target_weight"] = (universe["combined"] / denom).clip(-MAX_ABS_WEIGHT, MAX_ABS_WEIGHT) if denom > 0 else 0.0
    universe["target_weight"] = np.where(universe["target_weight"].abs() >= MIN_EFFECTIVE_WEIGHT, universe["target_weight"], 0.0)
    universe["dominant"] = universe[["carry_centered", "momo_centered", "breakout_centered"]].abs().idxmax(axis=1).str.replace("_centered", "")
    return universe


def run_backtest(frames: dict[str, pd.DataFrame], dates: list[pd.Timestamp]) -> pd.DataFrame:
    """Run the backtest day by day."""
    equity = INITIAL_EQUITY
    positions: dict[str, dict] = {}
    max_equity = equity
    rows = []

    for i, date in enumerate(dates):
        universe = build_universe(frames, date)
        if universe.empty:
            continue

        # Compute PnL for existing positions
        price_pnl = 0.0
        funding_pnl = 0.0
        for sym, pos in positions.items():
            f = frames.get(sym)
            if f is None:
                continue
            row = f[f["date"] == date]
            if row.empty:
                continue
            close = float(row.iloc[0]["close"])
            qty = pos["qty"]
            entry = pos["entry"]
            price_pnl += qty * (close - entry)
            funding_pnl += -qty * entry * float(row.iloc[0]["funding_rate_sum"])

        equity_before = equity + price_pnl + funding_pnl

        # Rebalance
        target_map = dict(zip(universe["symbol"], universe["target_weight"]))
        reason_map = dict(zip(universe["symbol"], universe.apply(
            lambda r: f"carry D{int(r['carry_decile'])}/momo D{int(r['momo_decile'])}/break D{int(r['breakout_decile'])}", axis=1)))

        new_positions = {}
        commission = 0.0
        all_syms = set(list(positions.keys()) + list(target_map.keys()))

        for sym in all_syms:
            old_qty = positions.get(sym, {}).get("qty", 0.0)
            old_w = 0.0
            if old_qty != 0:
                f = frames.get(sym)
                if f is not None:
                    r = f[f["date"] == date]
                    if not r.empty:
                        px = float(r.iloc[0]["close"])
                        old_w = old_qty * px / equity_before if equity_before > 0 else 0

            new_w = float(target_map.get(sym, 0.0))

            # Buffer
            if abs(new_w - old_w) <= WEIGHT_BUFFER:
                new_w = old_w  # keep current

            if abs(new_w) < MIN_EFFECTIVE_WEIGHT:
                new_w = 0.0

            if new_w != old_w and equity_before > 0:
                f = frames.get(sym)
                if f is not None:
                    r = f[f["date"] == date]
                    if not r.empty:
                        px = float(r.iloc[0]["close"])
                        trade_notional = abs(new_w - old_w) * equity_before
                        commission += trade_notional * COST_BPS_PER_SIDE / 10000.0
                        if abs(new_w) >= MIN_EFFECTIVE_WEIGHT:
                            new_qty = equity_before * new_w / px
                            new_positions[sym] = {"qty": new_qty, "entry": px, "weight": new_w, "reason": reason_map.get(sym, "")}
                        elif sym in positions:
                            pass  # closed

        # Fill new positions not yet in new_positions
        for sym in target_map:
            if sym in new_positions:
                continue
            w = float(target_map[sym])
            if abs(w) < MIN_EFFECTIVE_WEIGHT:
                continue
            f = frames.get(sym)
            if f is None:
                continue
            r = f[f["date"] == date]
            if r.empty:
                continue
            px = float(r.iloc[0]["close"])
            if px <= 0:
                continue
            # Check buffer against old
            old_w = 0.0
            if sym in positions:
                old_qty = positions[sym]["qty"]
                old_w = old_qty * positions[sym]["entry"] / equity_before if equity_before > 0 else 0
            if abs(w - old_w) <= WEIGHT_BUFFER:
                continue
            trade_notional = abs(w - old_w) * equity_before
            commission += trade_notional * COST_BPS_PER_SIDE / 10000.0
            qty = equity_before * w / px
            new_positions[sym] = {"qty": qty, "entry": px, "weight": w, "reason": reason_map.get(sym, "")}

        equity = max(0.0, equity_before - commission)
        max_equity = max(max_equity, equity)
        dd = (equity / max_equity - 1.0) if max_equity > 0 else 0.0

        long_count = sum(1 for p in new_positions.values() if p["weight"] > 0)
        short_count = sum(1 for p in new_positions.values() if p["weight"] < 0)

        rows.append({
            "date": iso_z(date),
            "equity": equity,
            "price_pnl": price_pnl,
            "funding_pnl": funding_pnl,
            "commission": commission,
            "drawdown": dd,
            "long_count": long_count,
            "short_count": short_count,
            "universe_size": len(universe),
        })

        positions = new_positions

        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/{len(dates)}] {iso_z(date)[:10]}  equity=${equity:,.2f}  dd={dd:.2%}")

    return pd.DataFrame(rows)


def compute_stats(eq: pd.DataFrame) -> dict:
    """Compute summary statistics."""
    if eq.empty:
        return {}
    n = len(eq)
    first_eq = eq["equity"].iloc[0]
    last_eq = eq["equity"].iloc[-1]
    ret = (last_eq / first_eq) - 1
    daily_ret = eq["equity"].pct_change().dropna()
    sharpe = (daily_ret.mean() / daily_ret.std() * np.sqrt(365)) if daily_ret.std() > 0 else 0
    win_rate = (daily_ret > 0).mean()
    max_dd = eq["drawdown"].min()
    total_funding = eq["funding_pnl"].sum()
    total_commission = eq["commission"].sum()
    total_price = eq["price_pnl"].sum()
    return {
        "days": n,
        "start_date": eq["date"].iloc[0][:10],
        "end_date": eq["date"].iloc[-1][:10],
        "total_return": ret,
        "final_equity": last_eq,
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "win_rate": win_rate,
        "total_price_pnl": total_price,
        "total_funding_pnl": total_funding,
        "total_commission": total_commission,
        "avg_daily_return": daily_ret.mean(),
    }


def main():
    parser = argparse.ArgumentParser(description="Rank 154 backtest with corrected carry signal")
    parser.add_argument("--days", type=int, default=140, help="Days of history to fetch")
    parser.add_argument("--start", type=str, default="2026-01-01", help="Backtest start date (YYYY-MM-DD)")
    parser.add_argument("--symbols", type=int, default=TOP_PROBE, help="Number of symbols to probe")
    args = parser.parse_args()

    start_date = pd.Timestamp(args.start, tz="UTC")
    print(f"=== Rank 154 Backtest (carry fix: last settled rate) ===")
    print(f"Start: {start_date.date()}, Universe probe: {args.symbols} symbols")
    print()

    # 1. Fetch exchange info
    print("[1/4] Fetching exchange info...")
    info = fetch_exchange_info()
    print(f"  {len(info)} perpetual symbols found")

    # 2. Fetch top symbols
    print(f"[2/4] Fetching top {args.symbols} by 24h volume...")
    top_syms = fetch_top_symbols(args.symbols)
    print(f"  {len(top_syms)} symbols fetched")

    # 3. Fetch data for each symbol
    print(f"[3/4] Fetching klines + funding for {len(top_syms)} symbols...")
    frames: dict[str, pd.DataFrame] = {}
    for i, sym in enumerate(top_syms):
        try:
            frame = fetch_symbol_data(sym, info)
            if not frame.empty and len(frame) >= 30:
                frames[sym] = frame
        except Exception as e:
            print(f"  [warn] {sym}: {e}")
        time.sleep(REQUEST_SLEEP)
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(top_syms)}] {len(frames)} symbols with data")
    print(f"  Total: {len(frames)} symbols with sufficient data")

    # 4. Determine backtest date range
    all_dates = set()
    for f in frames.values():
        all_dates.update(f["date"].tolist())
    available_dates = sorted(d for d in all_dates if d >= start_date)
    if not available_dates:
        print("ERROR: No dates available for backtest")
        return

    # Skip first 30 days (need warmup for 30d rolling volume + 20d breakout + 10d momentum)
    warmup_end = start_date + pd.Timedelta(days=35)
    bt_dates = [d for d in available_dates if d >= warmup_end]
    print(f"[4/4] Running backtest: {len(bt_dates)} days ({bt_dates[0].date()} → {bt_dates[-1].date()})")
    print()

    eq = run_backtest(frames, bt_dates)

    # Save
    ART_DIR.mkdir(parents=True, exist_ok=True)
    eq_path = ART_DIR / "backtest_equity.csv"
    eq.to_csv(eq_path, index=False)
    print(f"\n[ok] Equity curve saved: {eq_path}")

    stats = compute_stats(eq)
    stats_path = ART_DIR / "backtest_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] Stats saved: {stats_path}")

    # Print summary
    print(f"\n{'='*50}")
    print(f"BACKTEST RESULTS (carry_raw = last settled rate)")
    print(f"{'='*50}")
    print(f"Period:        {stats['start_date']} → {stats['end_date']} ({stats['days']} days)")
    print(f"Total Return:  {stats['total_return']:.2%}")
    print(f"Final Equity:  ${stats['final_equity']:,.2f}")
    print(f"Max Drawdown:  {stats['max_drawdown']:.2%}")
    print(f"Sharpe (ann.): {stats['sharpe']:.2f}")
    print(f"Win Rate:      {stats['win_rate']:.2%}")
    print(f"Price PnL:     ${stats['total_price_pnl']:,.2f}")
    print(f"Funding PnL:   ${stats['total_funding_pnl']:,.2f}")
    print(f"Commission:    ${stats['total_commission']:,.2f}")


if __name__ == "__main__":
    main()
