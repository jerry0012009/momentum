#!/usr/bin/env python3
"""Incrementally update BTCUSDT 15m kline cache for rank32c strategy.

Stores zipped CSV klines in the same format used by rank213 cache:
  raw_15m/monthly/BTCUSDT/BTCUSDT-15m-YYYY-MM.zip
  raw_15m/daily/BTCUSDT/BTCUSDT-15m-YYYY-MM-DD.zip

Also maintains a sidecar 'latest' directory with the most recent 90 days
for fast live-runner access.
"""
from __future__ import annotations

import csv
import io
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = (
    ROOT
    / "reports"
    / "artifacts"
    / "paper_rank213_largecap_xs_jump_veto"
    / "rank213_local_cache"
    / "monthly_marketcap_universe"
    / "raw_15m"
)
LATEST_DIR = ROOT / "reports" / "artifacts" / "rank32c_kline_cache" / "raw_15m"
SYMBOL = "BTCUSDT"
INTERVAL = "15m"
BAR_MS = 15 * 60 * 1000
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"

CSV_COLS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trades", "taker_base", "taker_quote", "ignore",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def fetch_klines(symbol: str, interval: str, start_ms: int, end_ms: int, limit: int = 1500) -> list[list]:
    """Fetch klines from Binance Futures API with pagination."""
    rows: list[list] = []
    cursor = start_ms
    while cursor < end_ms:
        qs = urlencode({
            "symbol": symbol, "interval": interval,
            "startTime": cursor, "endTime": end_ms, "limit": min(limit, 1500),
        })
        url = f"{BINANCE_URL}?{qs}"
        req = Request(url, headers={"User-Agent": "Momentum-FirstMoney/1.0"})
        with urlopen(req, timeout=30) as resp:
            payload = __import__("json").loads(resp.read().decode("utf-8"))
        if not payload:
            break
        rows.extend(payload)
        last_open_ms = int(payload[-1][0])
        cursor = last_open_ms + BAR_MS
        if cursor <= last_open_ms:
            break
    return rows


def load_zip_csv(path: Path) -> list[list]:
    """Load rows from a zip file containing a single CSV."""
    if not path.exists():
        return []
    with zipfile.ZipFile(path) as zf:
        members = zf.namelist()
        if not members:
            return []
        data = zf.read(members[0])
    reader = csv.reader(io.StringIO(data.decode("utf-8")))
    rows = list(reader)
    if rows and rows[0][0] == "open_time":
        rows = rows[1:]
    return rows


def save_zip_csv(path: Path, rows: list[list]) -> None:
    """Save rows as a zipped CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_COLS)
    for row in rows:
        writer.writerow(row)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{path.stem}.csv", buf.getvalue())


def row_open_ms(row: list) -> int:
    return int(row[0])


def row_close_time(row: list) -> int:
    return int(row[6])


def month_key(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m")


def day_key(ts_ms: int) -> str:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d")


def update_monthly_cache(symbol: str = SYMBOL) -> int:
    """Update monthly zip cache. Returns number of new bars fetched."""
    monthly_dir = CACHE_DIR / "monthly" / symbol
    monthly_dir.mkdir(parents=True, exist_ok=True)

    # Find the last cached bar
    existing_files = sorted(monthly_dir.glob(f"{symbol}-15m-*.zip"))
    total_new = 0

    if existing_files:
        last_file = existing_files[-1]
        existing_rows = load_zip_csv(last_file)
        if existing_rows:
            last_cached_ms = max(row_open_ms(r) for r in existing_rows)
            start_ms = last_cached_ms + BAR_MS
        else:
            start_ms = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
    else:
        start_ms = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

    end_ms = int(utc_now().timestamp() * 1000)
    if start_ms >= end_ms:
        print(f"[cache] monthly cache already up to date (last bar: {last_cached_ms})")
        return 0

    print(f"[cache] fetching monthly klines from {start_ms} to {end_ms}")
    new_rows = fetch_klines(symbol, INTERVAL, start_ms, end_ms)
    total_new += len(new_rows)

    if not new_rows:
        print("[cache] no new monthly klines returned")
        return 0

    # Group new rows by month and merge/overwrite
    groups: dict[str, list[list]] = {}
    for row in new_rows:
        mk = month_key(row_open_ms(row))
        groups.setdefault(mk, []).append(row)

    for mk, rows in groups.items():
        zip_path = monthly_dir / f"{symbol}-15m-{mk}.zip"
        existing = load_zip_csv(zip_path)
        existing_map = {row_open_ms(r): r for r in existing}
        for r in rows:
            existing_map[row_open_ms(r)] = r
        merged = sorted(existing_map.values(), key=lambda r: row_open_ms(r))
        save_zip_csv(zip_path, merged)
        print(f"[cache] monthly {mk}: {len(merged)} bars")

    return total_new


def update_daily_cache(symbol: str = SYMBOL, lookback_days: int = 60) -> int:
    """Update daily zip cache for the most recent N days."""
    daily_dir = CACHE_DIR / "daily" / symbol
    daily_dir.mkdir(parents=True, exist_ok=True)

    now = utc_now()
    start_day = now - __import__("datetime").timedelta(days=lookback_days)
    start_ms = int(start_day.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    end_ms = int(now.timestamp() * 1000)

    print(f"[cache] fetching daily klines (last {lookback_days} days)")
    new_rows = fetch_klines(symbol, INTERVAL, start_ms, end_ms)

    if not new_rows:
        print("[cache] no daily klines returned")
        return 0

    groups: dict[str, list[list]] = {}
    for row in new_rows:
        dk = day_key(row_open_ms(row))
        groups.setdefault(dk, []).append(row)

    for dk, rows in groups.items():
        zip_path = daily_dir / f"{symbol}-15m-{dk}.zip"
        save_zip_csv(zip_path, rows)

    print(f"[cache] daily: updated {len(groups)} days, {len(new_rows)} bars total")
    return len(new_rows)


def update_latest_cache(symbol: str = SYMBOL, lookback_days: int = 90) -> None:
    """Copy recent data to sidecar latest directory for fast runner access."""
    for subdir in ["monthly", "daily"]:
        src = CACHE_DIR / subdir / symbol
        dst = LATEST_DIR / subdir / symbol
        dst.mkdir(parents=True, exist_ok=True)
        if src.exists():
            import shutil
            for f in src.iterdir():
                shutil.copy2(f, dst / f.name)


def main() -> int:
    t0 = utc_now()
    print(f"[cache] update started at {t0.isoformat()}")

    n_monthly = update_monthly_cache()
    n_daily = update_daily_cache()
    update_latest_cache()

    t1 = utc_now()
    elapsed = (t1 - t0).total_seconds()
    print(f"[cache] done in {elapsed:.1f}s; monthly_new={n_monthly}, daily bars refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
