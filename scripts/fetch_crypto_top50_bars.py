#!/usr/bin/env python3
"""Fetch 1h OHLCV bars for the crypto_top50_usdt_perp_1h universe.

Default is V0: latest 180 days, closed candles only. This script downloads data only; it does not trade.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h"
MANIFEST = CACHE / "manifest.json"
BARS = CACHE / "bars_1h.parquet"
LOG = CACHE / "fetch_log.json"
INTERVAL = "1h"
LIMIT = 1500
HOUR_MS = 3_600_000
COLS = ["timestamp", "symbol", "open", "high", "low", "close", "volume", "quote_volume", "trade_count", "source", "market", "instrument_type", "timeframe"]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def hour_floor(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)


def parse_dt(text: str | None) -> datetime | None:
    if not text:
        return None
    return hour_floor(datetime.fromisoformat(text.replace("Z", "+00:00")))


def to_ms(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def from_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def read_manifest() -> dict:
    with MANIFEST.open("r", encoding="utf-8") as f:
        return json.load(f)


def request_klines(symbol: str, start_ms: int, end_ms: int) -> list:
    url = "https://" + "fapi.binance.com" + "/fapi/v1/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "startTime": start_ms, "endTime": end_ms, "limit": LIMIT}
    last_error = None
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # keep batch alive on transient failures
            last_error = exc
            time.sleep(0.25 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {symbol}: {last_error}")


def fetch_symbol(symbol: str, start: datetime, end_exclusive: datetime) -> tuple[pd.DataFrame, dict]:
    cursor = to_ms(start)
    end_inclusive = to_ms(end_exclusive) - 1
    rows = []
    calls = 0
    while cursor < to_ms(end_exclusive):
        raw = request_klines(symbol, cursor, end_inclusive)
        calls += 1
        if not raw:
            break
        for k in raw:
            open_ms = int(k[0])
            if open_ms >= to_ms(end_exclusive):
                continue
            rows.append({
                "timestamp": from_ms(open_ms), "symbol": symbol,
                "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4]),
                "volume": float(k[5]), "quote_volume": float(k[7]), "trade_count": int(k[8]),
                "source": "binance_fapi", "market": "crypto", "instrument_type": "usdt_margined_perpetual", "timeframe": INTERVAL,
            })
        next_cursor = int(raw[-1][0]) + HOUR_MS
        if next_cursor <= cursor or len(raw) < LIMIT:
            break
        cursor = next_cursor
        time.sleep(0.08)
    df = pd.DataFrame(rows, columns=COLS)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.drop_duplicates(["symbol", "timestamp"]).sort_values(["symbol", "timestamp"])
    return df, {"symbol": symbol, "status": "ok", "rows": int(len(df)), "requests": calls}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    p.add_argument("--days", type=int, default=180)
    p.add_argument("--symbols", nargs="*", default=None)
    p.add_argument("--append", action="store_true")
    args = p.parse_args()

    manifest = read_manifest()
    all_symbols = manifest.get("symbols", [])
    symbols = args.symbols or all_symbols
    unknown = sorted(set(symbols) - set(all_symbols))
    if unknown:
        raise ValueError(f"symbols not in manifest: {unknown}")

    end = parse_dt(args.end) or hour_floor(now_utc())
    start = parse_dt(args.start) or (end - timedelta(days=args.days))
    if start >= end:
        raise ValueError("start must be before end")

    print(f"Fetching {len(symbols)} symbols from {start.isoformat()} to {end.isoformat()} exclusive")
    frames, logs = [], []
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] {symbol}")
        try:
            df, log = fetch_symbol(symbol, start, end)
            frames.append(df)
            logs.append(log)
            print(f"  rows={log['rows']} requests={log['requests']}")
        except Exception as exc:
            logs.append({"symbol": symbol, "status": "error", "rows": 0, "error": repr(exc)})
            print(f"  ERROR {exc}")

    bars = pd.concat([x for x in frames if not x.empty], ignore_index=True) if any(not x.empty for x in frames) else pd.DataFrame(columns=COLS)
    if args.append and BARS.exists():
        old = pd.read_parquet(BARS)
        bars = pd.concat([old, bars], ignore_index=True)
    if not bars.empty:
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        bars = bars.drop_duplicates(["symbol", "timestamp"]).sort_values(["symbol", "timestamp"])[COLS]
    CACHE.mkdir(parents=True, exist_ok=True)
    bars.to_parquet(BARS, index=False)

    run_log = {"run_type": "V0 Debug Run", "start": start.isoformat(), "end_exclusive": end.isoformat(), "rows_total": int(len(bars)), "symbol_logs": logs}
    LOG.write_text(json.dumps(run_log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest.update({
        "downloaded_at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_start": bars["timestamp"].min().isoformat() if not bars.empty else "",
        "data_end": bars["timestamp"].max().isoformat() if not bars.empty else "",
        "bars_rows": int(len(bars)),
        "bars_path": str(BARS.relative_to(ROOT)),
        "fetch_log_path": str(LOG.relative_to(ROOT)),
        "fetch_window": {"start": start.isoformat(), "end_exclusive": end.isoformat(), "closed_candles_only": True},
        "research_caveat": "Static current Top50 diagnostic universe; debug and initial screening only.",
    })
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {len(bars)} rows to {BARS}")


if __name__ == "__main__":
    main()
