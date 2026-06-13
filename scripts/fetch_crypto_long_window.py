#!/usr/bin/env python3
"""Fetch 1h OHLCV bars for the long-window v1 dataset.

Same 50 symbols as Phase 2E, but targeting ~2 years of history.
Output goes to data/cache/crypto_top50_usdt_perp_1h_long_v1/ to avoid
overwriting the original 180d dataset.
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
DEFAULT_CACHE = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h_long_v1"
INTERVAL = "1h"
LIMIT = 1500
HOUR_MS = 3_600_000
COLS = ["timestamp", "bar_open_time", "bar_close_time", "symbol", "open", "high", "low", "close", "volume", "quote_volume", "trade_count", "source", "market", "instrument_type", "timeframe"]


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


def request_klines(symbol: str, start_ms: int, end_ms: int) -> list:
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": INTERVAL, "startTime": start_ms, "endTime": end_ms, "limit": LIMIT}
    last_error = None
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
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
                "bar_open_time": from_ms(open_ms),
                "bar_close_time": from_ms(open_ms + HOUR_MS),
                "timestamp": from_ms(open_ms + HOUR_MS),
                "symbol": symbol,
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
    p = argparse.ArgumentParser(description="Fetch long-window 1h bars for crypto Top50")
    p.add_argument("--start", default="2024-06-13T00:00:00Z", help="Start time (default: 2024-06-13)")
    p.add_argument("--end", default=None, help="End time exclusive (default: now)")
    p.add_argument("--symbols", nargs="*", default=None, help="Symbols to fetch (default: from existing dataset manifest)")
    p.add_argument("--output-dir", default=None, help="Output directory (default: data/cache/crypto_top50_usdt_perp_1h_long_v1)")
    p.add_argument("--symbols-from-existing", default=None, help="Path to existing manifest.json to read symbols from")
    p.add_argument("--append", action="store_true", help="Append to existing parquet instead of overwriting")
    args = p.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_CACHE
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read symbols
    if args.symbols:
        symbols = args.symbols
    elif args.symbols_from_existing:
        with open(args.symbols_from_existing, "r") as f:
            manifest = json.load(f)
        symbols = manifest.get("symbols", [])
    else:
        # Default: read from original dataset manifest
        orig_manifest = ROOT / "data" / "cache" / "crypto_top50_usdt_perp_1h" / "manifest.json"
        if orig_manifest.exists():
            with open(orig_manifest, "r") as f:
                manifest = json.load(f)
            symbols = manifest.get("symbols", [])
        else:
            raise ValueError("No symbols provided and no existing manifest found")

    end = parse_dt(args.end) or hour_floor(now_utc())
    start = parse_dt(args.start)
    if not start:
        start = end - timedelta(days=730)
    if start >= end:
        raise ValueError("start must be before end")

    print(f"Dataset: {output_dir.name}")
    print(f"Fetching {len(symbols)} symbols from {start.isoformat()} to {end.isoformat()} exclusive")
    expected_hours = int((end - start).total_seconds() / 3600)
    print(f"Expected rows per symbol: ~{expected_hours}")

    frames, logs = [], []
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] {symbol}", end=" ")
        try:
            df, log = fetch_symbol(symbol, start, end)
            frames.append(df)
            logs.append(log)
            print(f"rows={log['rows']} requests={log['requests']}")
        except Exception as exc:
            logs.append({"symbol": symbol, "status": "error", "rows": 0, "error": repr(exc)})
            print(f"ERROR {exc}")

    bars = pd.concat([x for x in frames if not x.empty], ignore_index=True) if any(not x.empty for x in frames) else pd.DataFrame(columns=COLS)
    if not bars.empty:
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        bars = bars.drop_duplicates(["symbol", "timestamp"]).sort_values(["symbol", "timestamp"])[COLS]

    bars_path = output_dir / "bars_1h.parquet"
    if args.append and bars_path.exists():
        old = pd.read_parquet(bars_path)
        bars = pd.concat([old, bars], ignore_index=True)
        bars = bars.drop_duplicates(["symbol", "timestamp"]).sort_values(["symbol", "timestamp"])
        print(f"Merged: {len(old)} old + new = {len(bars)} total")
    bars.to_parquet(bars_path, index=False)

    # Write fetch log
    run_log = {
        "run_type": "Phase 3 Long-window Fetch",
        "start": start.isoformat(),
        "end_exclusive": end.isoformat(),
        "rows_total": int(len(bars)),
        "symbol_logs": logs,
        "fallback": None,
    }
    log_path = output_dir / "fetch_log.json"
    log_path.write_text(json.dumps(run_log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Write manifest
    manifest_data = {
        "dataset_id": output_dir.name,
        "downloaded_at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_start": bars["timestamp"].min().isoformat() if not bars.empty else "",
        "data_end": bars["timestamp"].max().isoformat() if not bars.empty else "",
        "bars_rows": int(len(bars)),
        "bars_path": str(bars_path.relative_to(ROOT)),
        "fetch_log_path": str(log_path.relative_to(ROOT)),
        "fetch_window": {"start": start.isoformat(), "end_exclusive": end.isoformat(), "closed_candles_only": True},
        "target_window": {"start": "2024-06-13T00:00:00+00:00", "end": "2026-06-13T00:00:00+00:00"},
        "symbols": symbols,
        "n_symbols": len(symbols),
        "timestamp_convention": "timestamp = bar_close_time; bar_open_time retained",
        "selection_rule": "static_current_top50_by_24h_quote_volume (same as Phase 2E)",
        "research_caveat": "Static Top50 long-window diagnostic universe; Phase 3 baseline only.",
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nSaved {len(bars)} rows to {bars_path}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
