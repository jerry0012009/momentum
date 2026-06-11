#!/usr/bin/env python3
"""Rank154 long-history validation with causal historical universe.

Data source: Binance public data archive (monthly USDⓈ-M futures klines + fundingRate).
Key point: universe is chosen *per historical day* by trailing 30d quote_volume among all
USDT symbols available in the archive, not by today's top tickers.

This script intentionally avoids Binance /ticker/24hr for universe selection because that
would inject today's liquidity ranking into the past.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank154_long_history"
CACHE_DIR = ROOT / "data" / "binance_vision_rank154"
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
HTTP = "https://data.binance.vision"

STABLE_BASES = {"USDT", "USDC", "FDUSD", "BUSD", "USDP", "TUSD", "USDE", "USDS", "DAI", "EUR", "TRY", "BRL"}
LEVERAGED_PREFIXES = ("1000", "1000000")

INITIAL_EQUITY = 10_000.0
DEFAULT_COST_BPS = 5.0


def month_range(start: str, end: str) -> list[str]:
    s = pd.Period(start[:7], freq="M")
    e = pd.Period(end[:7], freq="M")
    return [str(p) for p in pd.period_range(s, e, freq="M")]


def http_get(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "rank154-validation/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def s3_list_common_prefixes(prefix: str) -> list[str]:
    url = f"{S3}?list-type=2&prefix={prefix}&delimiter=/"
    raw = http_get(url).decode("utf-8")
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    root = ET.fromstring(raw)
    return [x.find("s3:Prefix", ns).text for x in root.findall("s3:CommonPrefixes", ns)]


def s3_list_keys(prefix: str) -> list[str]:
    keys: list[str] = []
    token = None
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    while True:
        url = f"{S3}?list-type=2&prefix={prefix}&max-keys=1000"
        if token:
            from urllib.parse import quote
            url += "&continuation-token=" + quote(token)
        raw = http_get(url).decode("utf-8")
        root = ET.fromstring(raw)
        keys.extend([x.find("s3:Key", ns).text for x in root.findall("s3:Contents", ns)])
        tok = root.find("s3:NextContinuationToken", ns)
        if tok is None or not tok.text:
            break
        token = tok.text
    return keys


def discover_symbols() -> list[str]:
    prefixes = s3_list_common_prefixes("data/futures/um/monthly/klines/")
    symbols = []
    for p in prefixes:
        sym = p.rstrip("/").split("/")[-1]
        if not sym.endswith("USDT") or not sym.isascii():
            continue
        base = sym[:-4]
        if not base or not base.isalnum() or not base.isascii() or base in STABLE_BASES:
            continue
        # Exclude synthetic 1000x/1000000x contracts to keep plain alpha-base universe.
        if base.startswith(LEVERAGED_PREFIXES):
            continue
        symbols.append(sym)
    return sorted(set(symbols))


def cached_download(url: str, path: Path, retries: int = 2) -> bytes | None:
    if path.exists() and path.stat().st_size > 0:
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    for attempt in range(retries + 1):
        try:
            data = http_get(url)
            if data and not data.startswith(b"<Error>"):
                tmp = path.with_suffix(path.suffix + ".tmp")
                tmp.write_bytes(data)
                tmp.replace(path)
                return data
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    return None


def read_zip_csv(data: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not names:
            return pd.DataFrame()
        with zf.open(names[0]) as f:
            return pd.read_csv(f)


def fetch_key(key: str) -> pd.DataFrame:
    cache_path = CACHE_DIR / key
    data = cached_download(f"{HTTP}/{key}", cache_path)
    if data is None:
        return pd.DataFrame()
    try:
        return read_zip_csv(data)
    except Exception:
        return pd.DataFrame()


def fetch_month_symbol(symbol: str, month: str, kind: str) -> pd.DataFrame:
    if kind == "klines":
        key = f"data/futures/um/monthly/klines/{symbol}/1d/{symbol}-1d-{month}.zip"
    elif kind == "funding":
        key = f"data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{month}.zip"
    else:
        raise ValueError(kind)
    return fetch_key(key)


def normalize_kline(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if df.empty:
        return df
    # Binance monthly files sometimes include header, sometimes not.
    if "open_time" not in df.columns:
        cols = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"]
        df = pd.read_csv(io.StringIO(df.to_csv(index=False, header=False)), names=cols)
    out = pd.DataFrame({
        "date": pd.to_datetime(pd.to_numeric(df["open_time"], errors="coerce"), unit="ms", utc=True).dt.floor("D"),
        "symbol": symbol,
        "close": pd.to_numeric(df["close"], errors="coerce"),
        "quote_volume": pd.to_numeric(df["quote_volume"], errors="coerce"),
    }).dropna()
    return out


def normalize_funding(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if df.empty:
        return df
    if "fundingTime" not in df.columns:
        # Known columns: calc_time, funding_interval_hours, last_funding_rate, next_funding_time OR older fundingTime/fundingRate.
        pass
    # Handle both archive schemas defensively.
    time_col = "fundingTime" if "fundingTime" in df.columns else ("calc_time" if "calc_time" in df.columns else None)
    rate_col = "fundingRate" if "fundingRate" in df.columns else ("last_funding_rate" if "last_funding_rate" in df.columns else None)
    if time_col is None or rate_col is None:
        return pd.DataFrame()
    f = pd.DataFrame({
        "ts": pd.to_datetime(pd.to_numeric(df[time_col], errors="coerce"), unit="ms", utc=True),
        "symbol": symbol,
        "fr": pd.to_numeric(df[rate_col], errors="coerce"),
    }).dropna()
    if f.empty:
        return pd.DataFrame()
    f["date"] = f["ts"].dt.floor("D")
    return f.groupby(["date", "symbol"], as_index=False).agg(
        funding_rate_last=("fr", "last"),
        funding_rate_sum=("fr", "sum"),
        funding_count=("fr", "count"),
    )


def load_panel(symbols: list[str], months: list[str], max_workers: int = 32) -> tuple[pd.DataFrame, dict]:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = ART_DIR / "data_manifest.json"
    panel_path = ART_DIR / "daily_panel.pkl"
    start_month, end_month = months[0], months[-1]
    if panel_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("start_month") == start_month and meta.get("end_month") == end_month and meta.get("symbol_count") == len(symbols):
            return pd.read_pickle(panel_path), meta

    k_keys: list[tuple[str, str]] = []
    f_keys: list[tuple[str, str]] = []
    month_set = set(months)
    ym_re = re.compile(r"-(20\d{2}-\d{2})\.zip$")
    print("  listing existing archive keys per symbol...", flush=True)
    def list_one(sym: str):
        kk = []
        ff = []
        for key in s3_list_keys(f"data/futures/um/monthly/klines/{sym}/1d/"):
            m = ym_re.search(key)
            if m and m.group(1) in month_set and key.endswith(".zip"):
                kk.append((sym, key))
        for key in s3_list_keys(f"data/futures/um/monthly/fundingRate/{sym}/"):
            m = ym_re.search(key)
            if m and m.group(1) in month_set and key.endswith(".zip"):
                ff.append((sym, key))
        return kk, ff
    with ThreadPoolExecutor(max_workers=min(max_workers, 64)) as ex:
        futs = {ex.submit(list_one, sym): sym for sym in symbols}
        for i, fut in enumerate(as_completed(futs), 1):
            kk, ff = fut.result()
            k_keys.extend(kk); f_keys.extend(ff)
            if i % 100 == 0:
                print(f"  listed {i}/{len(symbols)} symbols; kline_keys={len(k_keys):,}, funding_keys={len(f_keys):,}", flush=True)

    k_parts, f_parts = [], []
    stats = {"kline_files": 0, "funding_files": 0, "kline_keys": len(k_keys), "funding_keys": len(f_keys), "symbols": len(symbols)}

    def one_k(sym_key):
        sym, key = sym_key
        return normalize_kline(fetch_key(key), sym)
    def one_f(sym_key):
        sym, key = sym_key
        return normalize_funding(fetch_key(key), sym)

    print(f"  reading/downloading {len(k_keys):,} kline files...", flush=True)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(one_k, t) for t in k_keys]
        for i, fut in enumerate(as_completed(futs), 1):
            k = fut.result()
            if not k.empty:
                k_parts.append(k); stats["kline_files"] += 1
            if i % 1000 == 0:
                print(f"  klines {i:,}/{len(k_keys):,}", flush=True)
    print(f"  reading/downloading {len(f_keys):,} funding files...", flush=True)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(one_f, t) for t in f_keys]
        for i, fut in enumerate(as_completed(futs), 1):
            f = fut.result()
            if not f.empty:
                f_parts.append(f); stats["funding_files"] += 1
            if i % 1000 == 0:
                print(f"  funding {i:,}/{len(f_keys):,}", flush=True)

    if not k_parts:
        raise RuntimeError("No kline data loaded")
    kl = pd.concat(k_parts, ignore_index=True).drop_duplicates(["date", "symbol"]).sort_values(["symbol", "date"])
    if f_parts:
        fu = pd.concat(f_parts, ignore_index=True).drop_duplicates(["date", "symbol"])
        panel = kl.merge(fu, on=["date", "symbol"], how="left")
    else:
        panel = kl.copy()
    panel["funding_rate_last"] = panel.get("funding_rate_last", pd.Series(dtype=float)).fillna(0.0)
    panel["funding_rate_sum"] = panel.get("funding_rate_sum", pd.Series(dtype=float)).fillna(0.0)
    panel["funding_count"] = panel.get("funding_count", pd.Series(dtype=float)).fillna(0).astype(int)

    # Causal listing proxy: first observed archive kline date. This is not current exchangeInfo.
    first_dates = panel.groupby("symbol")["date"].transform("min")
    panel["listing_days"] = (panel["date"] - first_dates).dt.total_seconds() / 86400.0
    panel = panel.sort_values(["symbol", "date"]).reset_index(drop=True)
    g = panel.groupby("symbol", group_keys=False)
    panel["trail_quote_volume_30d"] = g["quote_volume"].rolling(30, min_periods=30).mean().reset_index(level=0, drop=True)
    panel["momo_10d"] = g["close"].pct_change(10)

    def days_since_high(x):
        a = np.asarray(x, dtype=float)
        return float(len(a) - 1 - int(np.nanargmax(a))) if len(a) and not np.all(np.isnan(a)) else np.nan
    panel["days_since_20d_high"] = g["close"].rolling(20, min_periods=20).apply(days_since_high, raw=True).reset_index(level=0, drop=True)
    panel["breakout_raw"] = 19.0 - panel["days_since_20d_high"]
    panel["carry_raw"] = panel["funding_rate_last"]
    panel["is_eligible"] = (
        (panel["listing_days"] >= 180)
        & panel["trail_quote_volume_30d"].notna()
        & panel["momo_10d"].notna()
        & panel["breakout_raw"].notna()
    )
    panel.to_pickle(panel_path)
    meta = {
        **stats,
        "start_month": start_month,
        "end_month": end_month,
        "rows": int(len(panel)),
        "date_min": str(panel["date"].min().date()),
        "date_max": str(panel["date"].max().date()),
        "symbols_with_rows": int(panel["symbol"].nunique()),
        "source": "Binance public data archive monthly klines/fundingRate",
        "universe_note": "Per-day TopN by 30d trailing quote_volume among archive USDT symbols; no 24h current ticker prefilter.",
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return panel, meta


def build_targets(day: pd.DataFrame, universe_size=30, carry_weight=0.5, momo_weight=0.2, breakout_weight=0.3,
                  max_abs_weight=0.10, min_effective_weight=0.005) -> dict[str, float]:
    u = day[day["is_eligible"]].sort_values("trail_quote_volume_30d", ascending=False).head(universe_size).copy()
    if len(u) < max(5, min(15, universe_size // 2)):
        return {}
    for name, raw in [("carry", "carry_raw"), ("momo", "momo_10d"), ("breakout", "breakout_raw")]:
        ranks = u[raw].rank(method="first")
        q = max(2, min(10, len(u)))
        dec = pd.qcut(ranks, q=q, labels=False, duplicates="drop") + 1.0
        u[f"{name}_centered"] = dec - dec.mean()
    # Normalize remaining weights if user changes carry only; default preserves original 0.5/0.2/0.3.
    score = carry_weight * u["carry_centered"] + momo_weight * u["momo_centered"] + breakout_weight * u["breakout_centered"]
    score = score - score.mean()
    denom = float(score.abs().sum())
    if denom <= 0:
        return {}
    w = (score / denom).clip(-max_abs_weight, max_abs_weight)
    w = w.where(w.abs() >= min_effective_weight, 0.0)
    return {sym: float(val) for sym, val in zip(u["symbol"], w) if abs(float(val)) >= min_effective_weight}


def run_backtest(panel: pd.DataFrame, start: str, end: str, universe_size=30, carry_weight=0.5,
                 momo_weight=0.2, breakout_weight=0.3, cost_bps=5.0, weight_buffer=0.01) -> pd.DataFrame:
    p = panel[(panel["date"] >= pd.Timestamp(start, tz="UTC")) & (panel["date"] <= pd.Timestamp(end, tz="UTC"))].copy()
    if p.empty:
        return pd.DataFrame()
    by_date = {d: df for d, df in p.groupby("date")}
    dates = sorted(by_date.keys())
    equity = INITIAL_EQUITY
    weights: dict[str, float] = {}
    rows = []
    peak = equity
    for i in range(len(dates) - 1):
        d, nd = dates[i], dates[i + 1]
        day = by_date[d]
        nxt = by_date[nd].set_index("symbol")
        today_px = day.set_index("symbol")["close"]
        target = build_targets(day, universe_size, carry_weight, momo_weight, breakout_weight)
        # Buffer: don't trade tiny changes.
        adjusted = {}
        for sym in set(weights) | set(target):
            old = weights.get(sym, 0.0)
            new = target.get(sym, 0.0)
            if abs(new - old) <= weight_buffer:
                new = old
            if abs(new) >= 0.005:
                adjusted[sym] = new
        turnover = sum(abs(adjusted.get(s, 0.0) - weights.get(s, 0.0)) for s in set(adjusted) | set(weights))
        commission = equity * turnover * cost_bps / 10000.0
        equity_after_cost = max(0.0, equity - commission)
        price_ret = 0.0
        funding_ret = 0.0
        missing = 0
        for sym, w in adjusted.items():
            if sym not in today_px.index or sym not in nxt.index:
                missing += 1
                continue
            r = float(nxt.loc[sym, "close"] / today_px.loc[sym] - 1.0)
            fr = float(nxt.loc[sym, "funding_rate_sum"])
            price_ret += w * r
            funding_ret += -w * fr
        gross_ret = price_ret + funding_ret
        equity = equity_after_cost * (1.0 + gross_ret)
        peak = max(peak, equity)
        rows.append({
            "date": str(nd.date()),
            "equity": equity,
            "daily_return": equity / (rows[-1]["equity"] if rows else INITIAL_EQUITY) - 1.0,
            "price_return": price_ret,
            "funding_return": funding_ret,
            "commission": commission,
            "turnover": turnover,
            "n_positions": len(adjusted),
            "missing_positions": missing,
            "drawdown": equity / peak - 1.0,
            "universe_eligible": int(day["is_eligible"].sum()),
        })
        weights = adjusted
    return pd.DataFrame(rows)


def stats(eq: pd.DataFrame) -> dict:
    if eq.empty or len(eq) < 3:
        return {"days": len(eq)}
    r = eq["equity"].pct_change().dropna()
    total = eq["equity"].iloc[-1] / INITIAL_EQUITY - 1.0
    years = len(eq) / 365.25
    ann = (eq["equity"].iloc[-1] / INITIAL_EQUITY) ** (1 / years) - 1 if years > 0 and eq["equity"].iloc[-1] > 0 else np.nan
    return {
        "days": int(len(eq)),
        "start": eq["date"].iloc[0],
        "end": eq["date"].iloc[-1],
        "return": float(total),
        "ann_return": float(ann),
        "max_dd": float(eq["drawdown"].min()),
        "sharpe": float(r.mean() / r.std() * math.sqrt(365.25)) if r.std() > 0 else 0.0,
        "win_rate": float((r > 0).mean()),
        "avg_daily": float(r.mean()),
        "vol_daily": float(r.std()),
        "commission": float(eq["commission"].sum()),
        "avg_turnover": float(eq["turnover"].mean()),
        "median_positions": float(eq["n_positions"].median()),
        "missing_position_days": int((eq["missing_positions"] > 0).sum()),
    }


def monthly_returns(eq: pd.DataFrame) -> dict[str, float]:
    e = eq.copy(); e["month"] = e["date"].str[:7]
    out = {}
    for m, g in e.groupby("month"):
        out[m] = float(g["equity"].iloc[-1] / g["equity"].iloc[0] - 1.0)
    return out


def yearly_returns(eq: pd.DataFrame) -> dict[str, float]:
    e = eq.copy(); e["year"] = e["date"].str[:4]
    return {str(y): float(g["equity"].iloc[-1] / g["equity"].iloc[0] - 1.0) for y, g in e.groupby("year")}


def rolling_windows(panel: pd.DataFrame, start: str, end: str, window_days=180, step_days=30, **params) -> pd.DataFrame:
    dates = sorted(panel[(panel["date"] >= pd.Timestamp(start, tz="UTC")) & (panel["date"] <= pd.Timestamp(end, tz="UTC"))]["date"].unique())
    res = []
    for i in range(0, max(0, len(dates) - window_days), step_days):
        s = pd.Timestamp(dates[i]).strftime("%Y-%m-%d")
        e = pd.Timestamp(dates[min(i + window_days, len(dates)-1)]).strftime("%Y-%m-%d")
        eq = run_backtest(panel, s, e, **params)
        st = stats(eq)
        res.append({"start": s, "end": e, **st})
    return pd.DataFrame(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2021-05-01")
    ap.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--max-symbols", type=int, default=0, help="debug only")
    args = ap.parse_args()

    ART_DIR.mkdir(parents=True, exist_ok=True)
    print("Rank154 long-history validation", flush=True)
    print(f"Period request: {args.start} → {args.end}", flush=True)
    symbols = discover_symbols()
    if args.max_symbols:
        symbols = symbols[:args.max_symbols]
    months = month_range(args.start, args.end)
    print(f"Archive symbols: {len(symbols)} USDT plain symbols; months={months[0]}..{months[-1]} ({len(months)})", flush=True)
    panel, manifest = load_panel(symbols, months, max_workers=args.workers)
    print(f"Panel: {len(panel):,} rows, {panel.symbol.nunique()} symbols, {panel.date.min().date()} → {panel.date.max().date()}", flush=True)

    # Warmup naturally enforced by rolling features + 180 listing days.
    bt_start = args.start
    bt_end = args.end
    baseline_params = dict(universe_size=30, carry_weight=0.5, momo_weight=0.2, breakout_weight=0.3, cost_bps=5.0)
    eq = run_backtest(panel, bt_start, bt_end, **baseline_params)
    base_stats = stats(eq)
    eq.to_csv(ART_DIR / "baseline_equity.csv", index=False)
    print("Baseline", base_stats, flush=True)

    param_rows = []
    for cost in [0, 5, 10, 20, 30]:
        e = run_backtest(panel, bt_start, bt_end, **{**baseline_params, "cost_bps": cost})
        param_rows.append({"param": "cost_bps", "value": cost, **stats(e)})
    for us in [15, 20, 30, 40, 50, 75]:
        e = run_backtest(panel, bt_start, bt_end, **{**baseline_params, "universe_size": us})
        param_rows.append({"param": "universe_size", "value": us, **stats(e)})
    # Keep momo at 0.2; split remaining between carry and breakout to test the earlier finding.
    for cw in [0.0, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8]:
        bw = max(0.0, 0.8 - cw)
        e = run_backtest(panel, bt_start, bt_end, universe_size=30, carry_weight=cw, momo_weight=0.2, breakout_weight=bw, cost_bps=5.0)
        param_rows.append({"param": "carry_weight", "value": cw, "breakout_weight": bw, **stats(e)})
    params_df = pd.DataFrame(param_rows)
    params_df.to_csv(ART_DIR / "param_sweep.csv", index=False)

    roll180 = rolling_windows(panel, bt_start, bt_end, window_days=180, step_days=30, **baseline_params)
    roll365 = rolling_windows(panel, bt_start, bt_end, window_days=365, step_days=60, **baseline_params)
    roll180.to_csv(ART_DIR / "rolling_180d.csv", index=False)
    roll365.to_csv(ART_DIR / "rolling_365d.csv", index=False)

    # Year-by-year isolated backtests (positions reset per year).
    y_rows = []
    for year in sorted({d.year for d in panel["date"]}):
        ys, ye = f"{year}-01-01", f"{year}-12-31"
        if pd.Timestamp(ye, tz="UTC") < pd.Timestamp(bt_start, tz="UTC") or pd.Timestamp(ys, tz="UTC") > pd.Timestamp(bt_end, tz="UTC"):
            continue
        e = run_backtest(panel, max(ys, bt_start), min(ye, bt_end), **baseline_params)
        y_rows.append({"year": year, **stats(e)})
    yearly_df = pd.DataFrame(y_rows)
    yearly_df.to_csv(ART_DIR / "yearly_isolated.csv", index=False)

    results = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "request": vars(args),
        "data_manifest": manifest,
        "baseline_params": baseline_params,
        "baseline": base_stats,
        "monthly": monthly_returns(eq),
        "yearly_continuous": yearly_returns(eq),
        "param_sweep": param_rows,
        "rolling_180d_summary": {
            "count": int(len(roll180)),
            "positive": int((roll180.get("return", pd.Series(dtype=float)) > 0).sum()),
            "positive_rate": float((roll180.get("return", pd.Series(dtype=float)) > 0).mean()) if len(roll180) else None,
            "median_return": float(roll180["return"].median()) if len(roll180) else None,
            "min_return": float(roll180["return"].min()) if len(roll180) else None,
            "max_return": float(roll180["return"].max()) if len(roll180) else None,
        },
        "rolling_365d_summary": {
            "count": int(len(roll365)),
            "positive": int((roll365.get("return", pd.Series(dtype=float)) > 0).sum()),
            "positive_rate": float((roll365.get("return", pd.Series(dtype=float)) > 0).mean()) if len(roll365) else None,
            "median_return": float(roll365["return"].median()) if len(roll365) else None,
            "min_return": float(roll365["return"].min()) if len(roll365) else None,
            "max_return": float(roll365["return"].max()) if len(roll365) else None,
        },
        "causality_audit": [
            {"item": "Universe", "status": "PASS", "detail": "daily TopN selected by that day's 30d trailing quote_volume across archive symbols; no current 24h ticker ranking"},
            {"item": "Listing age", "status": "PASS_WITH_LIMITATION", "detail": "uses first observed archive kline as listing proxy; avoids current exchangeInfo but may differ from official onboardDate by a few days"},
            {"item": "Momentum", "status": "PASS", "detail": "10d pct_change through signal close"},
            {"item": "Breakout", "status": "PASS", "detail": "20d high distance through signal close"},
            {"item": "Carry", "status": "PASS", "detail": "last settled funding record by signal date; PnL uses next day's realized funding sum"},
            {"item": "Execution timing", "status": "PASS", "detail": "rebalance at close D, earn close-to-close return and realized funding on D+1"},
            {"item": "Survivorship", "status": "IMPROVED_NOT_PERFECT", "detail": "uses Binance archive symbol directories including delisted monthly data when present; still limited to data.binance.vision coverage"},
        ],
    }
    (ART_DIR / "long_history_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"Saved artifacts to {ART_DIR}", flush=True)


if __name__ == "__main__":
    main()
