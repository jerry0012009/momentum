#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class HttpError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_z(ts) -> str:
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def normalize_for_csv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return out


def json_request(url: str, headers: dict | None = None, timeout: int = 20):
    req = Request(url, headers=headers or {})
    with urlopen(req, timeout=timeout) as resp:
        status = getattr(resp, "status", 200)
        body = resp.read().decode("utf-8")
    if status >= 400:
        raise HttpError(f"HTTP {status}: {url} :: {body[:300]}")
    return json.loads(body)


def fetch_coinbase_candles(product: str, granularity_sec: int, start: datetime, end: datetime) -> pd.DataFrame:
    # Coinbase Exchange candles limit ≈ 300 rows per request.
    chunk = timedelta(seconds=granularity_sec * 300)
    headers = {"User-Agent": "OpenClaw-Momentum-PaperRunner/1.0"}
    rows: list[list[float]] = []
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + chunk, end)
        qs = urlencode(
            {
                "granularity": granularity_sec,
                "start": cursor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "end": chunk_end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
        )
        url = f"https://api.exchange.coinbase.com/products/{product}/candles?{qs}"
        payload = json_request(url, headers=headers)
        if isinstance(payload, list):
            rows.extend(payload)
        cursor = chunk_end
    if not rows:
        return pd.DataFrame(columns=["ts", "low", "high", "open", "close", "volume"])
    df = pd.DataFrame(rows, columns=["epoch", "low", "high", "open", "close", "volume"])
    df["ts"] = pd.to_datetime(df["epoch"], unit="s", utc=True)
    df = df.sort_values("ts").drop_duplicates(subset=["ts"]).reset_index(drop=True)
    return df[["ts", "low", "high", "open", "close", "volume"]].astype(
        {"low": float, "high": float, "open": float, "close": float, "volume": float}
    )


def fetch_coinbase_book(product: str, level: int = 1) -> dict:
    headers = {"User-Agent": "OpenClaw-Momentum-PaperRunner/1.0"}
    return json_request(f"https://api.exchange.coinbase.com/products/{product}/book?level={level}", headers=headers)


def fetch_binance_futures_klines(
    symbol: str,
    interval: str,
    start_ms: int,
    end_ms: int,
    limit: int = 1500,
) -> pd.DataFrame:
    rows: list[list[str]] = []
    cursor = start_ms
    while cursor < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": min(limit, 1500),
            }
        )
        payload = json_request(f"https://fapi.binance.com/fapi/v1/klines?{qs}")
        if not payload:
            break
        rows.extend(payload)
        last_open_ms = int(payload[-1][0])
        step_ms = interval_to_ms(interval)
        cursor = last_open_ms + step_ms
        if cursor <= last_open_ms:
            break
    if not rows:
        return pd.DataFrame(columns=["ts", "open", "high", "low", "close", "volume", "close_ts"])
    df = pd.DataFrame(
        rows,
        columns=[
            "open_ms",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_ms",
            "quote_volume",
            "trade_count",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    df["ts"] = pd.to_datetime(df["open_ms"].astype("int64"), unit="ms", utc=True)
    df["close_ts"] = pd.to_datetime(df["close_ms"].astype("int64"), unit="ms", utc=True)
    df = df.sort_values("ts").drop_duplicates(subset=["ts"]).reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[["ts", "open", "high", "low", "close", "volume", "close_ts"]]


def fetch_binance_futures_book(symbol: str, limit: int = 5) -> dict:
    qs = urlencode({"symbol": symbol, "limit": limit})
    return json_request(f"https://fapi.binance.com/fapi/v1/depth?{qs}")


def interval_to_ms(interval: str) -> int:
    unit = interval[-1]
    qty = int(interval[:-1])
    if unit == "m":
        return qty * 60_000
    if unit == "h":
        return qty * 3_600_000
    if unit == "d":
        return qty * 86_400_000
    raise ValueError(f"unsupported interval: {interval}")


def upsert_ledger(existing_path: Path, new_rows: pd.DataFrame, key_cols: Iterable[str]) -> pd.DataFrame:
    existing = read_csv_or_empty(existing_path)
    if existing.empty:
        out = normalize_for_csv(new_rows)
        if not out.empty:
            ensure_dir(existing_path.parent)
            out.to_csv(existing_path, index=False)
        return out
    combined = pd.concat([existing, normalize_for_csv(new_rows)], ignore_index=True)
    combined = combined.drop_duplicates(subset=list(key_cols), keep="last")
    combined.to_csv(existing_path, index=False)
    return combined
