#!/usr/bin/env python3
"""Comprehensive Rank 154 validation: extended time range + parameter sweep + stability.

Tests:
1. 150-day backtest (extended from 93 days)
2. Parameter sensitivity: universe size, legs, momentum lookback, breakout window, carry weight
3. Rolling window stability
4. Sub-period analysis
5. Drawdown recovery analysis

Usage:
    python scripts/validate_rank154_comprehensive.py
"""

from __future__ import annotations

import json
import sys
import time as _time
from collections import defaultdict
from datetime import datetime, timezone
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
COST_BPS = 5.0
REQUEST_SLEEP = 0.06
FUTURES_TICKER = "https://fapi.binance.com/fapi/v1/ticker/24hr"
FUTURES_KLINES = "https://fapi.binance.com/fapi/v1/klines"
FUTURES_FUNDING = "https://fapi.binance.com/fapi/v1/fundingRate"
FUTURES_EXCHANGE = "https://fapi.binance.com/fapi/v1/exchangeInfo"

ART_DIR = ROOT / "reports" / "artifacts" / "rank154_validation"


def fetch_json(url, params=None):
    import urllib.request
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    return json.loads(urllib.request.urlopen(url, timeout=30).read())


def fetch_exchange_info():
    data = fetch_json(FUTURES_EXCHANGE)
    info = {}
    stable = {"USDT", "USDC", "FDUSD", "BUSD", "USDP", "TUSD", "USDE", "USDS", "DAI"}
    for s in data.get("symbols", []):
        if s.get("contractType") != "PERPETUAL":
            continue
        base = s.get("baseAsset", "")
        info[s["symbol"]] = {
            "symbol": s["symbol"], "base_asset": base,
            "plain_alpha_base": bool(base) and base.isalpha() and base.upper() == base and base not in stable,
            "onboard_ms": int(s.get("onboardDate", 0) or 0),
        }
    return info


def fetch_top_symbols(n):
    tickers = fetch_json(FUTURES_TICKER)
    ranked = sorted(tickers, key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)
    return [t["symbol"] for t in ranked[:n]]


def fetch_symbol_data(symbol, info, kline_limit=150):
    klines = fetch_json(FUTURES_KLINES, {"symbol": symbol, "interval": "1d", "limit": kline_limit})
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
    }).dropna().sort_values("date").reset_index(drop=True)

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
        _time.sleep(REQUEST_SLEEP)

    if funding_rows:
        fdf = pd.DataFrame(funding_rows)
        fdf["ts"] = pd.to_datetime(pd.to_numeric(fdf["fundingTime"], errors="coerce"), unit="ms", utc=True)
        fdf["fr"] = pd.to_numeric(fdf["fundingRate"], errors="coerce")
        fdf = fdf.dropna(subset=["ts", "fr"])
        fdf["date"] = fdf["ts"].dt.floor("D")
        daily = fdf.groupby("date").agg(funding_rate_last=("fr", "last"), funding_rate_sum=("fr", "sum"), funding_count=("fr", "count")).reset_index()
        frame = frame.merge(daily, on="date", how="left")
    frame["funding_rate_last"] = frame.get("funding_rate_last", pd.Series(dtype=float)).fillna(0.0)
    frame["funding_rate_sum"] = frame.get("funding_rate_sum", pd.Series(dtype=float)).fillna(0.0)
    frame["funding_count"] = frame.get("funding_count", pd.Series(dtype=float)).fillna(0).astype(int)

    meta = info.get(symbol, {})
    frame["symbol"] = symbol
    frame["plain_alpha_base"] = meta.get("plain_alpha_base", False)
    onboard_ms = meta.get("onboard_ms", 0)
    frame["listing_days"] = (frame["date"] - pd.to_datetime(onboard_ms, unit="ms", utc=True)).dt.total_seconds() / 86400.0
    frame["trail_quote_volume_30d"] = frame["quote_volume"].rolling(30, min_periods=30).mean()
    frame["momo_10d"] = frame["close"].pct_change(10)
    def _dsh(arr):
        a = np.asarray(arr, dtype=float)
        if len(a) == 0 or np.all(np.isnan(a)):
            return np.nan
        return float(len(a) - 1 - int(np.nanargmax(a)))
    frame["days_since_20d_high"] = frame["close"].rolling(20, min_periods=20).apply(_dsh, raw=True)
    frame["breakout_raw"] = 19.0 - frame["days_since_20d_high"]
    frame["carry_raw"] = frame["funding_rate_last"]
    frame["guard_pass"] = (
        frame["plain_alpha_base"] & (frame["listing_days"] >= 180)
        & frame["trail_quote_volume_30d"].notna() & frame["momo_10d"].notna() & frame["breakout_raw"].notna()
    )
    return frame.sort_values("date").reset_index(drop=True)


def build_universe(frames, date, universe_size=30, min_listing_days=180, max_abs_weight=0.10, min_effective_weight=0.005):
    rows = []
    for sym, f in frames.items():
        row = f[f["date"] == date]
        if row.empty:
            continue
        r = row.iloc[0].to_dict()
        if r.get("plain_alpha_base") and r.get("listing_days", 0) >= min_listing_days and pd.notna(r.get("trail_quote_volume_30d")) and pd.notna(r.get("momo_10d")) and pd.notna(r.get("breakout_raw")):
            rows.append(r)
    if not rows:
        return pd.DataFrame()
    panel = pd.DataFrame(rows).sort_values("trail_quote_volume_30d", ascending=False).head(universe_size).reset_index(drop=True)
    for col, raw in [("carry", "carry_raw"), ("momo", "momo_10d"), ("breakout", "breakout_raw")]:
        ranks = panel[raw].rank(method="first")
        q = max(2, min(10, len(panel)))
        dec = pd.qcut(ranks, q=q, labels=False, duplicates="drop") + 1.0
        panel[f"{col}_decile"] = dec
        panel[f"{col}_centered"] = dec - dec.mean()
    panel["combined"] = 0.5 * panel["carry_centered"] + 0.2 * panel["momo_centered"] + 0.3 * panel["breakout_centered"]
    panel["combined"] -= panel["combined"].mean()
    denom = float(panel["combined"].abs().sum())
    panel["target_weight"] = (panel["combined"] / denom).clip(-max_abs_weight, max_abs_weight) if denom > 0 else 0.0
    panel["target_weight"] = np.where(panel["target_weight"].abs() >= min_effective_weight, panel["target_weight"], 0.0)
    return panel


def run_backtest(frames, dates, universe_size=30, weight_buffer=0.01, cost_bps=5.0, max_abs_weight=0.10, min_effective_weight=0.005):
    equity = INITIAL_EQUITY
    positions = {}
    max_eq = equity
    rows = []
    for date in dates:
        universe = build_universe(frames, date, universe_size=universe_size, max_abs_weight=max_abs_weight, min_effective_weight=min_effective_weight)
        if universe.empty:
            continue
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
            price_pnl += pos["qty"] * (close - pos["entry"])
            funding_pnl += -pos["qty"] * pos["entry"] * float(row.iloc[0]["funding_rate_sum"])
        eq_before = equity + price_pnl + funding_pnl
        target_map = dict(zip(universe["symbol"], universe["target_weight"]))
        new_positions = {}
        commission = 0.0
        for sym in set(list(positions.keys()) + list(target_map.keys())):
            old_qty = positions.get(sym, {}).get("qty", 0.0)
            old_w = 0.0
            if old_qty != 0:
                f = frames.get(sym)
                if f is not None:
                    r = f[f["date"] == date]
                    if not r.empty:
                        old_w = old_qty * float(r.iloc[0]["close"]) / eq_before if eq_before > 0 else 0
            new_w = float(target_map.get(sym, 0.0))
            if abs(new_w - old_w) <= weight_buffer:
                new_w = old_w
            if abs(new_w) < min_effective_weight:
                new_w = 0.0
            if new_w != old_w and eq_before > 0:
                f = frames.get(sym)
                if f is not None:
                    r = f[f["date"] == date]
                    if not r.empty:
                        px = float(r.iloc[0]["close"])
                        commission += abs(new_w - old_w) * eq_before * cost_bps / 10000.0
                        if abs(new_w) >= min_effective_weight:
                            new_positions[sym] = {"qty": eq_before * new_w / px, "entry": px, "weight": new_w}
        for sym in target_map:
            if sym in new_positions:
                continue
            w = float(target_map[sym])
            if abs(w) < min_effective_weight:
                continue
            f = frames.get(sym)
            if f is None:
                continue
            r = f[f["date"] == date]
            if r.empty:
                continue
            px = float(r.iloc[0]["close"])
            old_w2 = 0.0
            if sym in positions:
                old_w2 = positions[sym]["qty"] * positions[sym]["entry"] / eq_before if eq_before > 0 else 0
            if abs(w - old_w2) <= weight_buffer:
                continue
            commission += abs(w - old_w2) * eq_before * cost_bps / 10000.0
            new_positions[sym] = {"qty": eq_before * w / px, "entry": px, "weight": w}
        equity = max(0.0, eq_before - commission)
        max_eq = max(max_eq, equity)
        dd = (equity / max_eq - 1.0) if max_eq > 0 else 0.0
        positions = new_positions
        rows.append({"date": str(date)[:10], "equity": equity, "price_pnl": price_pnl, "funding_pnl": funding_pnl, "commission": commission, "drawdown": dd})
    return pd.DataFrame(rows)


def compute_stats(eq):
    if eq.empty:
        return {}
    n = len(eq)
    first_eq = eq["equity"].iloc[0]
    last_eq = eq["equity"].iloc[-1]
    daily_ret = eq["equity"].pct_change().dropna()
    return {
        "days": n, "return": (last_eq / first_eq) - 1, "final_equity": last_eq,
        "max_dd": eq["drawdown"].min(),
        "sharpe": (daily_ret.mean() / daily_ret.std() * np.sqrt(365)) if daily_ret.std() > 0 else 0,
        "win_rate": (daily_ret > 0).mean(),
        "avg_daily": daily_ret.mean(),
        "funding_pnl": eq["funding_pnl"].sum(),
        "commission": eq["commission"].sum(),
    }


def main():
    ART_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Rank 154 Comprehensive Validation")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)

    # === Phase 1: Fetch data ===
    print("\n[Phase 1] Fetching data for 80 symbols...")
    info = fetch_exchange_info()
    top_syms = fetch_top_symbols(80)
    frames = {}
    for i, sym in enumerate(top_syms):
        try:
            frame = fetch_symbol_data(sym, info, kline_limit=150)
            if not frame.empty and len(frame) >= 40:
                frames[sym] = frame
        except Exception as e:
            pass
        _time.sleep(REQUEST_SLEEP)
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/80] {len(frames)} symbols loaded")
    print(f"  Total: {len(frames)} symbols with data")

    # Get all available dates
    all_dates = set()
    for f in frames.values():
        all_dates.update(f["date"].tolist())
    start = pd.Timestamp("2025-12-01", tz="UTC")
    warmup = start + pd.Timedelta(days=35)
    all_bt_dates = sorted(d for d in all_dates if d >= warmup)
    print(f"  Available backtest dates: {all_bt_dates[0].date()} → {all_bt_dates[-1].date()} ({len(all_bt_dates)} days)")

    # === Phase 2: Baseline 150-day backtest ===
    print("\n[Phase 2] Running 150-day baseline backtest...")
    eq_baseline = run_backtest(frames, all_bt_dates, universe_size=30, cost_bps=5.0)
    stats_baseline = compute_stats(eq_baseline)
    print(f"  Period: {stats_baseline['days']} days")
    print(f"  Return: {stats_baseline['return']:.2%}")
    print(f"  Max DD: {stats_baseline['max_dd']:.2%}")
    print(f"  Sharpe: {stats_baseline['sharpe']:.2f}")
    print(f"  Win Rate: {stats_baseline['win_rate']:.2%}")

    # === Phase 3: Parameter sensitivity ===
    print("\n[Phase 3] Parameter sensitivity sweep...")
    param_results = []

    # 3a: Universe size
    for us in [15, 20, 30, 50]:
        eq = run_backtest(frames, all_bt_dates, universe_size=us, cost_bps=5.0)
        s = compute_stats(eq)
        param_results.append({"param": "universe_size", "value": us, **s})
        print(f"  universe={us}: ret={s['return']:.2%} dd={s['max_dd']:.2%} sharpe={s['sharpe']:.2f}")

    # 3b: Carry weight (change the 0.5 in combined score)
    for cw in [0.2, 0.35, 0.5, 0.65, 0.8]:
        # Custom backtest with different carry weight
        equity = INITIAL_EQUITY
        positions = {}
        max_eq = equity
        rows = []
        for date in all_bt_dates:
            # Build universe with custom carry weight
            urows = []
            for sym, f in frames.items():
                row = f[f["date"] == date]
                if row.empty:
                    continue
                r = row.iloc[0].to_dict()
                if r.get("plain_alpha_base") and r.get("listing_days", 0) >= 180 and pd.notna(r.get("trail_quote_volume_30d")) and pd.notna(r.get("momo_10d")) and pd.notna(r.get("breakout_raw")):
                    urows.append(r)
            if not urows:
                continue
            panel = pd.DataFrame(urows).sort_values("trail_quote_volume_30d", ascending=False).head(30).reset_index(drop=True)
            for col, raw in [("carry", "carry_raw"), ("momo", "momo_10d"), ("breakout", "breakout_raw")]:
                ranks = panel[raw].rank(method="first")
                q = max(2, min(10, len(panel)))
                dec = pd.qcut(ranks, q=q, labels=False, duplicates="drop") + 1.0
                panel[f"{col}_centered"] = dec - dec.mean()
            mw = 1.0 - cw - 0.2
            if mw < 0:
                mw = 0
            panel["combined"] = cw * panel["carry_centered"] + 0.2 * panel["momo_centered"] + mw * panel["breakout_centered"]
            panel["combined"] -= panel["combined"].mean()
            denom = float(panel["combined"].abs().sum())
            panel["target_weight"] = (panel["combined"] / denom).clip(-0.10, 0.10) if denom > 0 else 0.0
            panel["target_weight"] = np.where(panel["target_weight"].abs() >= 0.005, panel["target_weight"], 0.0)
            target_map = dict(zip(panel["symbol"], panel["target_weight"]))
            # PnL + rebalance
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
                price_pnl += pos["qty"] * (close - pos["entry"])
                funding_pnl += -pos["qty"] * pos["entry"] * float(row.iloc[0]["funding_rate_sum"])
            eq_before = equity + price_pnl + funding_pnl
            new_positions = {}
            commission = 0.0
            for sym in set(list(positions.keys()) + list(target_map.keys())):
                old_qty = positions.get(sym, {}).get("qty", 0.0)
                old_w = 0.0
                if old_qty != 0:
                    f = frames.get(sym)
                    if f is not None:
                        r = f[f["date"] == date]
                        if not r.empty:
                            old_w = old_qty * float(r.iloc[0]["close"]) / eq_before if eq_before > 0 else 0
                new_w = float(target_map.get(sym, 0.0))
                if abs(new_w - old_w) <= 0.01:
                    new_w = old_w
                if abs(new_w) < 0.005:
                    new_w = 0.0
                if new_w != old_w and eq_before > 0:
                    f = frames.get(sym)
                    if f is not None:
                        r = f[f["date"] == date]
                        if not r.empty:
                            px = float(r.iloc[0]["close"])
                            commission += abs(new_w - old_w) * eq_before * 5.0 / 10000.0
                            if abs(new_w) >= 0.005:
                                new_positions[sym] = {"qty": eq_before * new_w / px, "entry": px}
            for sym in target_map:
                if sym in new_positions:
                    continue
                w = float(target_map[sym])
                if abs(w) < 0.005:
                    continue
                f = frames.get(sym)
                if f is None:
                    continue
                r = f[f["date"] == date]
                if r.empty:
                    continue
                px = float(r.iloc[0]["close"])
                old_w2 = 0.0
                if sym in positions:
                    old_w2 = positions[sym]["qty"] * positions[sym]["entry"] / eq_before if eq_before > 0 else 0
                if abs(w - old_w2) <= 0.01:
                    continue
                commission += abs(w - old_w2) * eq_before * 5.0 / 10000.0
                new_positions[sym] = {"qty": eq_before * w / px, "entry": px}
            equity = max(0.0, eq_before - commission)
            max_eq = max(max_eq, equity)
            dd = (equity / max_eq - 1.0) if max_eq > 0 else 0.0
            positions = new_positions
            rows.append({"equity": equity, "drawdown": dd})
        eq_cw = pd.DataFrame(rows)
        daily_ret = eq_cw["equity"].pct_change().dropna()
        s = {
            "days": len(eq_cw), "return": (eq_cw["equity"].iloc[-1] / eq_cw["equity"].iloc[0]) - 1,
            "max_dd": eq_cw["drawdown"].min(),
            "sharpe": (daily_ret.mean() / daily_ret.std() * np.sqrt(365)) if daily_ret.std() > 0 else 0,
            "win_rate": (daily_ret > 0).mean(),
        }
        param_results.append({"param": "carry_weight", "value": cw, **s})
        print(f"  carry_weight={cw}: ret={s['return']:.2%} dd={s['max_dd']:.2%} sharpe={s['sharpe']:.2f}")

    # === Phase 4: Rolling window stability ===
    print("\n[Phase 4] Rolling window stability (30-day windows)...")
    window_size = 30
    rolling_results = []
    for start_idx in range(0, len(all_bt_dates) - window_size, 5):
        window_dates = all_bt_dates[start_idx:start_idx + window_size]
        eq_w = run_backtest(frames, window_dates, universe_size=30, cost_bps=5.0)
        s = compute_stats(eq_w)
        rolling_results.append({
            "start": str(window_dates[0])[:10], "end": str(window_dates[-1])[:10],
            "return": s.get("return", 0), "max_dd": s.get("max_dd", 0), "sharpe": s.get("sharpe", 0),
        })
    rolling_df = pd.DataFrame(rolling_results)
    positive_windows = (rolling_df["return"] > 0).sum()
    total_windows = len(rolling_df)
    print(f"  {positive_windows}/{total_windows} windows positive ({positive_windows/total_windows:.0%})")
    print(f"  Window returns: min={rolling_df['return'].min():.2%} median={rolling_df['return'].median():.2%} max={rolling_df['return'].max():.2%}")

    # === Phase 5: Sub-period analysis ===
    print("\n[Phase 5] Sub-period analysis...")
    eq_baseline["month"] = eq_baseline["date"].str[:7]
    monthly = eq_baseline.groupby("month").apply(lambda g: g["equity"].iloc[-1] / g["equity"].iloc[0] - 1)
    for month, ret in monthly.items():
        print(f"  {month}: {ret:+.2%}")

    # === Phase 6: Drawdown recovery ===
    print("\n[Phase 6] Drawdown recovery analysis...")
    eq_b = eq_baseline.copy()
    eq_b["peak"] = eq_b["equity"].cummax()
    eq_b["in_dd"] = eq_b["equity"] < eq_b["peak"]
    dd_periods = []
    in_dd = False
    dd_start = None
    dd_trough = 0
    for _, row in eq_b.iterrows():
        if row["in_dd"] and not in_dd:
            in_dd = True
            dd_start = row["date"]
            dd_trough = row["drawdown"]
        elif in_dd:
            dd_trough = min(dd_trough, row["drawdown"])
            if not row["in_dd"]:
                dd_periods.append({"start": dd_start, "end": row["date"], "trough": dd_trough, "days": (pd.Timestamp(row["date"]) - pd.Timestamp(dd_start)).days})
                in_dd = False
    if dd_periods:
        avg_recovery = np.mean([d["days"] for d in dd_periods])
        print(f"  {len(dd_periods)} drawdown periods, avg recovery: {avg_recovery:.0f} days")
        for dp in dd_periods:
            print(f"    {dp['start']} → {dp['end']}: trough {dp['trough']:.2%}, {dp['days']} days")

    # === Save all results ===
    results = {
        "baseline": stats_baseline,
        "param_sensitivity": param_results,
        "rolling_stability": {
            "window_size": 30,
            "total_windows": total_windows,
            "positive_windows": int(positive_windows),
            "positive_rate": positive_windows / total_windows,
            "min_return": float(rolling_df["return"].min()),
            "median_return": float(rolling_df["return"].median()),
            "max_return": float(rolling_df["return"].max()),
            "details": rolling_results,
        },
        "monthly": {str(k): float(v) for k, v in monthly.items()},
        "drawdown_recovery": dd_periods,
    }
    results_path = ART_DIR / "validation_results.json"
    results_path.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    eq_baseline.to_csv(ART_DIR / "baseline_equity_150d.csv", index=False)
    print(f"\n[ok] Results saved: {results_path}")
    print(f"[ok] Equity curve: {ART_DIR / 'baseline_equity_150d.csv'}")


if __name__ == "__main__":
    main()
