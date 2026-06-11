#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "external_data_probes"
ART_DIR.mkdir(parents=True, exist_ok=True)

RANK5_MARKETS_CSV = ART_DIR / "rank5_polymarket_btc_market_probe.csv"
RANK6_METRICS_CSV = ART_DIR / "rank6_btc_equity_proxy_probe_metrics.csv"
SUMMARY_JSON = ART_DIR / "rank5_rank6_external_data_probe_summary.json"

YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0"}
PL_HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*"}


@dataclass
class Rank6ProbeRow:
    symbol: str
    overlap_bars: int
    same_bar_corr: float
    btc_leads_1bar_corr: float
    eq_leads_1bar_corr: float
    best_nonzero_lag_bars: int
    best_nonzero_lag_corr: float
    top20pct_btc_move_events: int
    top20pct_sign_hit_next_eq_bar: float
    mean_eq_next_bar_after_large_pos_btc: float
    mean_eq_next_bar_after_large_neg_btc: float


def fetch_json(url: str, *, headers: dict | None = None, timeout: int = 30):
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def fetch_binance_klines(symbol: str = "BTCUSDT", interval: str = "15m", days: int = 70) -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 3600 * 1000
    rows: list[list] = []
    cur = start_ms
    while cur < end_ms:
        params = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": cur,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urllib.request.urlopen(f"https://api.binance.com/api/v3/klines?{params}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        cur = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(
        rows,
        columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "q", "n", "tb", "tq", "ignore"],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.floor("15min"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
        }
    )
    out = out.dropna().groupby("timestamp", as_index=False).last().sort_values("timestamp")
    return out


def fetch_yahoo_chart(symbol: str, interval: str = "15m", range_: str = "60d") -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
    payload = fetch_json(url, headers=YAHOO_HEADERS)
    result = payload["chart"]["result"][0]
    quote = result["indicators"]["quote"][0]
    ts = pd.to_datetime(result["timestamp"], unit="s", utc=True).floor("15min")
    out = pd.DataFrame({"timestamp": ts, "close": quote["close"]})
    out = out.dropna().groupby("timestamp", as_index=False).last().sort_values("timestamp")
    return out


def compute_rank6_probe() -> pd.DataFrame:
    btc = fetch_binance_klines().rename(columns={"close": "BTC"})
    rows: list[Rank6ProbeRow] = []
    for symbol in ["SPY", "QQQ", "COIN", "MSTR"]:
        eq = fetch_yahoo_chart(symbol).rename(columns={"close": symbol})
        merged = btc.merge(eq, on="timestamp", how="inner").sort_values("timestamp").reset_index(drop=True)
        merged["btc_ret"] = np.log(merged["BTC"].astype(float)).diff()
        merged["eq_ret"] = np.log(merged[symbol].astype(float)).diff()
        merged = merged.dropna().reset_index(drop=True)

        same_bar = float(merged["btc_ret"].corr(merged["eq_ret"]))
        btc_leads_1 = float(merged["eq_ret"].shift(-1).corr(merged["btc_ret"]))
        eq_leads_1 = float(merged["btc_ret"].shift(-1).corr(merged["eq_ret"]))

        lag_scores = []
        for lag in range(-8, 9):
            if lag == 0:
                continue
            corr = merged["btc_ret"].corr(merged["eq_ret"].shift(lag))
            if pd.notna(corr):
                lag_scores.append((lag, float(corr)))
        best_nonzero_lag, best_nonzero_corr = max(lag_scores, key=lambda x: abs(x[1]))

        merged["btc_prev"] = merged["btc_ret"].shift(1)
        sig = merged.dropna().copy()
        threshold = sig["btc_prev"].abs().quantile(0.8)
        sig = sig[sig["btc_prev"].abs() >= threshold].copy()
        sign_hit = float((np.sign(sig["btc_prev"]) == np.sign(sig["eq_ret"])).mean()) if len(sig) else float("nan")
        pos_mean = float(sig.loc[sig["btc_prev"] > 0, "eq_ret"].mean()) if len(sig) else float("nan")
        neg_mean = float(sig.loc[sig["btc_prev"] < 0, "eq_ret"].mean()) if len(sig) else float("nan")

        rows.append(
            Rank6ProbeRow(
                symbol=symbol,
                overlap_bars=int(len(merged)),
                same_bar_corr=same_bar,
                btc_leads_1bar_corr=btc_leads_1,
                eq_leads_1bar_corr=eq_leads_1,
                best_nonzero_lag_bars=int(best_nonzero_lag),
                best_nonzero_lag_corr=float(best_nonzero_corr),
                top20pct_btc_move_events=int(len(sig)),
                top20pct_sign_hit_next_eq_bar=sign_hit,
                mean_eq_next_bar_after_large_pos_btc=pos_mean,
                mean_eq_next_bar_after_large_neg_btc=neg_mean,
            )
        )
    return pd.DataFrame([r.__dict__ for r in rows])


def fetch_polymarket_markets_pages(max_offset: int = 2000, step: int = 500) -> list[dict]:
    out: list[dict] = []
    for offset in range(0, max_offset, step):
        url = f"https://gamma-api.polymarket.com/markets?limit={step}&offset={offset}&active=true&closed=false"
        batch = fetch_json(url, headers=PL_HEADERS)
        if not batch:
            break
        out.extend(batch)
        if len(batch) < step:
            break
    dedup = {str(m.get("id")): m for m in out}
    return list(dedup.values())


def price_history_probe(asset_id: str) -> tuple[int, str | None, str | None, float | None, float | None]:
    url = f"https://clob.polymarket.com/prices-history?market={asset_id}&interval=max"
    payload = fetch_json(url, headers=PL_HEADERS)
    history = payload.get("history", [])
    if not history:
        return 0, None, None, None, None
    prices = [float(x["p"]) for x in history]
    ts = [pd.to_datetime(int(x["t"]), unit="s", utc=True).strftime("%Y-%m-%dT%H:%M:%SZ") for x in history]
    return len(history), ts[0], ts[-1], min(prices), max(prices)


def book_probe(asset_id: str) -> tuple[float | None, float | None, float | None]:
    url = f"https://clob.polymarket.com/book?token_id={asset_id}"
    payload = fetch_json(url, headers=PL_HEADERS)
    bids = payload.get("bids", []) or []
    asks = payload.get("asks", []) or []
    best_bid = float(bids[0]["price"]) if bids else None
    best_ask = float(asks[0]["price"]) if asks else None
    spread = (best_ask - best_bid) if (best_bid is not None and best_ask is not None) else None
    return best_bid, best_ask, spread


def compute_rank5_probe() -> pd.DataFrame:
    markets = fetch_polymarket_markets_pages()
    keywords = ["bitcoin", " btc ", "btc?", "$btc", "bitcoin ", "bitcoin?"]
    rows = []
    for m in markets:
        text = " " + ((m.get("question", "") + " " + m.get("description", "") + " " + m.get("slug", "")).lower()) + " "
        if not any(k in text for k in keywords):
            continue
        asset_ids = json.loads(m.get("clobTokenIds", "[]")) if isinstance(m.get("clobTokenIds"), str) else (m.get("clobTokenIds") or [])
        yes_asset = str(asset_ids[0]) if asset_ids else None
        hist_n = None
        hist_start = None
        hist_end = None
        pmin = None
        pmax = None
        best_bid = None
        best_ask = None
        spread = None
        if yes_asset:
            hist_n, hist_start, hist_end, pmin, pmax = price_history_probe(yes_asset)
            best_bid, best_ask, spread = book_probe(yes_asset)
        rows.append(
            {
                "market_id": m.get("id"),
                "question": m.get("question"),
                "slug": m.get("slug"),
                "end_date": m.get("endDate"),
                "liquidity": float(m.get("liquidity") or 0),
                "volume24hr": float(m.get("volume24hr") or 0),
                "yes_asset_id": yes_asset,
                "history_points": hist_n,
                "history_start_utc": hist_start,
                "history_end_utc": hist_end,
                "price_min": pmin,
                "price_max": pmax,
                "best_bid": best_bid,
                "best_ask": best_ask,
                "best_spread": spread,
            }
        )
    df = pd.DataFrame(rows).sort_values(["volume24hr", "liquidity"], ascending=[False, False]).reset_index(drop=True)
    return df


def main() -> int:
    rank6 = compute_rank6_probe()
    rank5 = compute_rank5_probe()

    rank6.to_csv(RANK6_METRICS_CSV, index=False)
    rank5.to_csv(RANK5_MARKETS_CSV, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rank6_symbols": rank6["symbol"].tolist(),
        "rank6_best_same_bar_corr": rank6[["symbol", "same_bar_corr"]].sort_values("same_bar_corr", ascending=False).iloc[0].to_dict() if not rank6.empty else None,
        "rank5_active_btc_markets": int(len(rank5)),
        "rank5_highest_volume24hr_market": rank5[["question", "volume24hr"]].iloc[0].to_dict() if not rank5.empty else None,
        "artifacts": {
            "rank5_probe_csv": str(RANK5_MARKETS_CSV.relative_to(ROOT)),
            "rank6_probe_csv": str(RANK6_METRICS_CSV.relative_to(ROOT)),
        },
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
