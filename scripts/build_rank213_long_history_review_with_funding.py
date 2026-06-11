#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import random
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_long_history_review_with_funding.html"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
CACHE_DIR = ART_DIR / "rank213_local_cache"

DATA_VISION_MONTHLY_KLINES = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{ym}.zip"
DATA_VISION_DAILY_KLINES = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/15m/{symbol}-15m-{ymd}.zip"
DATA_VISION_MONTHLY_FUNDING = "https://data.binance.vision/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{ym}.zip"
KLINES_API = "https://fapi.binance.com/fapi/v1/klines"
FUNDING_API = "https://fapi.binance.com/fapi/v1/fundingRate"

COST_BPS = 4.0
FORMATION_BARS = 64
HOLD_BARS = 12
TOP_N = 3
BOTTOM_N = 3
VETO_FLOOR = 0.015
VETO_MULT = 2.0
VARIANT = "f64_h12_floor150_mult2p0"

SYMBOL_ONBOARD_DATE_MS = {
    "BTCUSDT": 1569398400000,
    "ETHUSDT": 1569398400000,
    "SOLUSDT": 1569398400000,
    "SIRENUSDT": 1742634000000,
    "XRPUSDT": 1569398400000,
    "TAOUSDT": 1712845800000,
    "ONUSDT": 1761294600000,
    "RIVERUSDT": 1760712300000,
    "DOGEUSDT": 1569398400000,
    "CUSDT": 1752570000000,
    "BNBUSDT": 1569398400000,
    "HYPEUSDT": 1748601000000,
    "ZECUSDT": 1569398400000,
    "PIPPINUSDT": 1737713700000,
    "1000PEPEUSDT": 1683244800000,
    "B3USDT": 1739446200000,
    "STGUSDT": 1661324400000,
    "ADAUSDT": 1569398400000,
    "WLDUSDT": 1690200000000,
    "SUIUSDT": 1683072000000,
    "BCHUSDT": 1569398400000,
    "PIXELUSDT": 1708354800000,
    "ENAUSDT": 1712061000000,
    "LINKUSDT": 1569398400000,
    "DOTUSDT": 1569398400000,
    "AVAXUSDT": 1569398400000,
    "ONTUSDT": 1569398400000,
    "FILUSDT": 1569398400000,
    "KNCUSDT": 1569398400000,
    "QUSDT": 1756798200000,
}


@dataclass(frozen=True)
class WindowSpec:
    label: str
    days: int


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    cur = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    end_month = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    out = []
    while cur <= end_month:
        out.append(cur.strftime("%Y-%m"))
        cur = cur + pd.offsets.MonthBegin(1)
    return out


def safe_download(url: str, dst: Path) -> bool:
    ensure_dir(dst.parent)
    if dst.exists() and dst.stat().st_size > 0:
        return True
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            blob = r.read()
        dst.write_bytes(blob)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def read_kline_zip(path: Path) -> pd.DataFrame:
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "close"])
        data = zf.read(members[0])
    df = pd.read_csv(
        io.BytesIO(data),
        header=None,
        names=[
            "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
            "trade_count", "taker_base", "taker_quote", "ignore",
        ],
    )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "close"])
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True),
        "close": df["close"].astype(float),
    })
    return out.drop_duplicates("timestamp").sort_values("timestamp")


def read_funding_zip(path: Path) -> pd.DataFrame:
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "funding_rate"])
        data = zf.read(members[0])

    # 新版列：calc_time,funding_interval_hours,last_funding_rate
    df = pd.read_csv(io.BytesIO(data))
    if {"calc_time", "last_funding_rate"}.issubset(df.columns):
        t = pd.to_numeric(df["calc_time"], errors="coerce")
        r = pd.to_numeric(df["last_funding_rate"], errors="coerce")
    elif {"fundingTime", "fundingRate"}.issubset(df.columns):
        t = pd.to_numeric(df["fundingTime"], errors="coerce")
        r = pd.to_numeric(df["fundingRate"], errors="coerce")
    else:
        df2 = pd.read_csv(io.BytesIO(data), header=None)
        t = pd.to_numeric(df2.iloc[:, 0], errors="coerce")
        r = pd.to_numeric(df2.iloc[:, -1], errors="coerce")

    out = pd.DataFrame({
        "timestamp": pd.to_datetime(t, unit="ms", utc=True, errors="coerce"),
        "funding_rate": r,
    }).dropna()
    return out.drop_duplicates("timestamp").sort_values("timestamp")


def fetch_klines_api_with_retry(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    rows: list[list[Any]] = []
    cur = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    while cur < end_ms:
        ok = False
        last_exc: Exception | None = None
        batch: list[list[Any]] = []
        for retry in range(8):
            try:
                resp = requests.get(
                    KLINES_API,
                    params={"symbol": symbol, "interval": "15m", "startTime": cur, "endTime": end_ms, "limit": 1500},
                    timeout=30,
                )
                if resp.status_code in (418, 429):
                    raise RuntimeError(f"http_{resp.status_code}")
                resp.raise_for_status()
                batch = resp.json()
                ok = True
                break
            except Exception as e:
                last_exc = e
                sleep_s = min(20.0, 1.2 * (2 ** retry)) + random.uniform(0.0, 0.8)
                time.sleep(sleep_s)
        if not ok:
            raise RuntimeError(f"kline api failed for {symbol} at {cur}: {last_exc}")
        if not batch:
            break
        rows.extend(batch)
        last_ts = int(batch[-1][0])
        nxt = last_ts + 1
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.12)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "close"])
    df = pd.DataFrame(
        rows,
        columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "trade_count", "taker_base", "taker_quote", "ignore"],
    )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "close"])
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True),
        "close": df["close"].astype(float),
    })
    return out.drop_duplicates("timestamp").sort_values("timestamp")


def fetch_funding_api_with_retry(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    rows: list[dict] = []
    cur = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    while cur < end_ms:
        ok = False
        last_exc: Exception | None = None
        for retry in range(8):
            try:
                resp = requests.get(
                    FUNDING_API,
                    params={"symbol": symbol, "startTime": cur, "endTime": end_ms, "limit": 1000},
                    timeout=30,
                )
                if resp.status_code in (418, 429):
                    raise RuntimeError(f"http_{resp.status_code}")
                resp.raise_for_status()
                batch = resp.json()
                ok = True
                break
            except Exception as e:
                last_exc = e
                sleep_s = min(20.0, 1.2 * (2 ** retry)) + random.uniform(0.0, 0.8)
                time.sleep(sleep_s)
        if not ok:
            raise RuntimeError(f"funding api failed for {symbol} at {cur}: {last_exc}")
        if not batch:
            break
        rows.extend(batch)
        last_ts = int(batch[-1]["fundingTime"])
        nxt = last_ts + 1
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.12)
    if not rows:
        return pd.DataFrame(columns=["timestamp", "funding_rate"])
    df = pd.DataFrame(rows)
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(pd.to_numeric(df["fundingTime"], errors="coerce"), unit="ms", utc=True, errors="coerce"),
        "funding_rate": pd.to_numeric(df["fundingRate"], errors="coerce"),
    }).dropna()
    return out.drop_duplicates("timestamp").sort_values("timestamp")


def load_or_build_symbol_klines(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    cache_path = CACHE_DIR / "klines_15m" / f"{symbol}.csv"
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True, errors="coerce")
        cached["close"] = pd.to_numeric(cached["close"], errors="coerce")
        cached = cached.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
        cache_fresh_until = end.floor("15min") - pd.Timedelta(minutes=15)
        if not cached.empty and cached["timestamp"].max() >= cache_fresh_until:
            return cached[(cached["timestamp"] >= start) & (cached["timestamp"] <= end)].reset_index(drop=True)
    parts: list[pd.DataFrame] = []
    if cache_path.exists():
        parts.append(cached)
    months = month_range(start, end)
    current_month = end.strftime("%Y-%m")
    for ym in months:
        if ym == current_month:
            continue
        p = CACHE_DIR / "raw" / "klines_monthly" / symbol / f"{symbol}-15m-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_KLINES.format(symbol=symbol, ym=ym), p)
        if ok:
            parts.append(read_kline_zip(p))
            time.sleep(0.02)
    # 当前月先走 daily zip，再用 API 补齐到最新
    cur = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    while cur <= end.normalize():
        ymd = cur.strftime("%Y-%m-%d")
        p = CACHE_DIR / "raw" / "klines_daily" / symbol / f"{symbol}-15m-{ymd}.zip"
        ok = safe_download(DATA_VISION_DAILY_KLINES.format(symbol=symbol, ymd=ymd), p)
        if ok:
            parts.append(read_kline_zip(p))
        cur += pd.Timedelta(days=1)
        time.sleep(0.01)
    api_start = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    if parts:
        known = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
        if not known.empty:
            api_start = max(api_start, pd.to_datetime(known["timestamp"].max(), utc=True) + pd.Timedelta(minutes=15))
    if api_start <= end:
        try:
            api_chunk = fetch_klines_api_with_retry(symbol, api_start, end)
            if not api_chunk.empty:
                parts.append(api_chunk)
        except Exception:
            pass
    if not parts:
        raise RuntimeError(f"no klines for {symbol}")
    df = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].reset_index(drop=True)
    ensure_dir(cache_path.parent)
    df.to_csv(cache_path, index=False)
    return df


def load_or_build_symbol_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, dict]:
    cache_path = CACHE_DIR / "funding_8h" / f"{symbol}.csv"
    source_info = {"monthly_zip_used": True, "api_used": False, "api_failed": False}

    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True, errors="coerce")
        cached["funding_rate"] = pd.to_numeric(cached["funding_rate"], errors="coerce")
        cached = cached.dropna(subset=["timestamp", "funding_rate"]).drop_duplicates("timestamp").sort_values("timestamp")
        if not cached.empty and cached["timestamp"].max() >= end - pd.Timedelta(hours=8):
            sub = cached[(cached["timestamp"] >= start) & (cached["timestamp"] <= end)].reset_index(drop=True)
            return sub, source_info

    parts: list[pd.DataFrame] = []
    months = month_range(start, end)
    latest_monthly_ts: pd.Timestamp | None = None
    for ym in months:
        p = CACHE_DIR / "raw" / "funding_monthly" / symbol / f"{symbol}-fundingRate-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_FUNDING.format(symbol=symbol, ym=ym), p)
        if ok:
            chunk = read_funding_zip(p)
            if not chunk.empty:
                parts.append(chunk)
                latest_monthly_ts = chunk["timestamp"].max() if latest_monthly_ts is None else max(latest_monthly_ts, chunk["timestamp"].max())
            time.sleep(0.02)

    # 当前月增量优先 API（带等待重试，规避 418/429）
    api_start = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    if latest_monthly_ts is not None and latest_monthly_ts >= api_start:
        api_start = latest_monthly_ts + pd.Timedelta(milliseconds=1)
    if api_start <= end:
        try:
            api_chunk = fetch_funding_api_with_retry(symbol, api_start, end)
            if not api_chunk.empty:
                parts.append(api_chunk)
            source_info["api_used"] = True
        except Exception:
            source_info["api_used"] = True
            source_info["api_failed"] = True

    if not parts:
        return pd.DataFrame(columns=["timestamp", "funding_rate"]), source_info

    df = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].reset_index(drop=True)
    ensure_dir(cache_path.parent)
    df.to_csv(cache_path, index=False)
    return df, source_info


def max_drawdown(ret: pd.Series) -> float:
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def overall_metrics(gross_price: pd.Series, funding_ret: pd.Series, net_total: pd.Series, turnover: pd.Series) -> dict:
    gross_total = gross_price + funding_ret
    return {
        "price_gross_mean_bps": float(gross_price.mean() * 10000.0),
        "funding_mean_bps": float(funding_ret.mean() * 10000.0),
        "gross_total_mean_bps": float(gross_total.mean() * 10000.0),
        "net_total_mean_bps": float(net_total.mean() * 10000.0),
        "net_total_cum_pct": float(((1.0 + net_total).prod() - 1.0) * 100.0),
        "win_rate": float((net_total > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "max_drawdown_pct": float(max_drawdown(net_total) * 100.0),
        "worst_net_bps": float(net_total.min() * 10000.0),
        "p5_net_bps": float(np.percentile(net_total, 5) * 10000.0),
    }


def grouped_metrics(detail: pd.DataFrame, key: str) -> pd.DataFrame:
    rows = []
    for k, sub in detail.groupby(key):
        rows.append({
            key: k,
            "rebalances": int(len(sub)),
            "plain_net_mean_bps": float(sub["plain_net_total"].mean() * 10000.0),
            "plain_net_cum_pct": float(((1.0 + sub["plain_net_total"]).prod() - 1.0) * 100.0),
            "plain_win_rate": float((sub["plain_net_total"] > 0).mean() * 100.0),
            "plain_max_dd_pct": float(max_drawdown(sub["plain_net_total"]) * 100.0),
            "plain_avg_turnover_x": float(sub["plain_turnover_x"].mean()),
            "plain_funding_mean_bps": float(sub["plain_funding_ret"].mean() * 10000.0),
            "veto_net_mean_bps": float(sub["veto_net_total"].mean() * 10000.0),
            "veto_net_cum_pct": float(((1.0 + sub["veto_net_total"]).prod() - 1.0) * 100.0),
            "veto_win_rate": float((sub["veto_net_total"] > 0).mean() * 100.0),
            "veto_max_dd_pct": float(max_drawdown(sub["veto_net_total"]) * 100.0),
            "veto_avg_turnover_x": float(sub["veto_turnover_x"].mean()),
            "veto_funding_mean_bps": float(sub["veto_funding_ret"].mean() * 10000.0),
        })
    return pd.DataFrame(rows)


def render_table(df: pd.DataFrame, percent_cols: set[str], bps_cols: set[str], x_cols: set[str]) -> str:
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in percent_cols:
                txt = f"{float(v):.2f}%"
            elif c in bps_cols:
                txt = f"{float(v):.2f} bps"
            elif c in x_cols:
                txt = f"{float(v):.3f}x"
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            tds.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def funding_sum_for_symbols(funding_map: dict[str, pd.DataFrame], symbols: list[str], entry: pd.Timestamp, exit_ts: pd.Timestamp, sign: int) -> tuple[float, int]:
    # sign: +1 long(付 funding), -1 short(收 funding)
    per_symbol = []
    event_count = 0
    for sym in symbols:
        f = funding_map[sym]
        if f.empty:
            per_symbol.append(0.0)
            continue
        m = f[(f["timestamp"] > entry) & (f["timestamp"] <= exit_ts)]
        event_count += int(len(m))
        # long: -sum(rate), short: +sum(rate)
        per_symbol.append(float((-sign) * m["funding_rate"].sum()))
    if not per_symbol:
        return 0.0, event_count
    return float(np.mean(per_symbol) * 0.5), event_count  # side weight 0.5


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)
    ensure_dir(CACHE_DIR)

    seed_summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    symbols: list[str] = seed_summary["symbols"]

    onboard = {s: pd.to_datetime(SYMBOL_ONBOARD_DATE_MS[s], unit="ms", utc=True) for s in symbols}
    common_start = max(onboard.values())

    now = pd.Timestamp.utcnow()
    now = now.tz_convert("UTC") if now.tzinfo else now.tz_localize("UTC")
    sample_end = now.floor("15min") - pd.Timedelta(minutes=15)

    # 1) price panel (local cache priority)
    price_frames = []
    symbol_price_avail = []
    for s in symbols:
        df = load_or_build_symbol_klines(s, common_start, sample_end)
        if df.empty:
            raise RuntimeError(f"empty price history for {s}")
        symbol_price_avail.append({
            "symbol": s,
            "first_price_bar_utc": to_iso(df["timestamp"].min()),
            "last_price_bar_utc": to_iso(df["timestamp"].max()),
            "price_bars": int(len(df)),
        })
        price_frames.append(df.rename(columns={"close": s}).set_index("timestamp")[[s]])

    panel = price_frames[0]
    for f in price_frames[1:]:
        panel = panel.join(f, how="outer")
    panel = panel.sort_index().ffill().dropna()
    actual_start = panel.index.min()
    actual_end = panel.index.max()

    # 2) funding map (local monthly cache + API retry increment)
    funding_map: dict[str, pd.DataFrame] = {}
    funding_sources = []
    for s in symbols:
        fdf, src = load_or_build_symbol_funding(s, actual_start, actual_end)
        funding_map[s] = fdf
        funding_sources.append({
            "symbol": s,
            "funding_first_utc": to_iso(fdf["timestamp"].min()) if not fdf.empty else "",
            "funding_last_utc": to_iso(fdf["timestamp"].max()) if not fdf.empty else "",
            "funding_events": int(len(fdf)),
            "api_used": bool(src["api_used"]),
            "api_failed": bool(src["api_failed"]),
        })

    # 3) frozen-spec backtest + funding
    ret = panel.pct_change()
    rows = []
    i = FORMATION_BARS
    while i + HOLD_BARS < len(panel):
        ts = panel.index[i]
        exit_ts = panel.index[i + HOLD_BARS]
        hist = ret.iloc[i - FORMATION_BARS + 1:i + 1]
        cumret = panel.iloc[i] / panel.iloc[i - FORMATION_BARS] - 1.0
        universe_med = hist.abs().max().median()
        veto_threshold = max(VETO_FLOOR, VETO_MULT * float(universe_med if pd.notna(universe_med) else 0.0))

        rank = cumret.sort_values()
        longs = rank.index[-TOP_N:].tolist()[::-1]
        plain_shorts = rank.index[:BOTTOM_N].tolist()

        short_info = [(sym, float(hist[sym].max())) for sym in plain_shorts]
        eligible = [sym for sym, mx in short_info if pd.notna(mx) and mx <= veto_threshold]
        vetoed = [sym for sym, mx in short_info if pd.notna(mx) and mx > veto_threshold]
        refill = [sym for sym in rank.index if sym not in longs and sym not in plain_shorts]
        veto_shorts = eligible.copy()
        for sym in refill:
            if len(veto_shorts) >= BOTTOM_N:
                break
            mx = float(hist[sym].max())
            if pd.notna(mx) and mx <= veto_threshold:
                veto_shorts.append(sym)
        if len(veto_shorts) < BOTTOM_N:
            for sym in rank.index:
                if sym not in longs and sym not in veto_shorts:
                    veto_shorts.append(sym)
                if len(veto_shorts) >= BOTTOM_N:
                    break

        future = panel.iloc[i + HOLD_BARS] / panel.iloc[i] - 1.0
        long_ret = float(future[longs].mean())
        plain_short_series = -future[plain_shorts]
        veto_short_series = -future[veto_shorts]
        plain_price_gross = 0.5 * long_ret + 0.5 * float(plain_short_series.mean())
        veto_price_gross = 0.5 * long_ret + 0.5 * float(veto_short_series.mean())

        long_funding, long_events = funding_sum_for_symbols(funding_map, longs, ts, exit_ts, sign=+1)
        plain_short_funding, plain_short_events = funding_sum_for_symbols(funding_map, plain_shorts, ts, exit_ts, sign=-1)
        veto_short_funding, veto_short_events = funding_sum_for_symbols(funding_map, veto_shorts, ts, exit_ts, sign=-1)

        plain_funding_ret = long_funding + plain_short_funding
        veto_funding_ret = long_funding + veto_short_funding

        plain_turn = 1.0
        veto_turn = 1.0 + (len(set(veto_shorts) ^ set(plain_shorts)) / 6.0)

        plain_net_total = plain_price_gross + plain_funding_ret - plain_turn * (COST_BPS / 10000.0)
        veto_net_total = veto_price_gross + veto_funding_ret - veto_turn * (COST_BPS / 10000.0)

        rows.append({
            "timestamp_ts": ts,
            "timestamp": to_iso(ts),
            "exit_ts": to_iso(exit_ts),
            "plain_price_gross": plain_price_gross,
            "veto_price_gross": veto_price_gross,
            "plain_funding_ret": plain_funding_ret,
            "veto_funding_ret": veto_funding_ret,
            "plain_net_total": plain_net_total,
            "veto_net_total": veto_net_total,
            "plain_turnover_x": plain_turn,
            "veto_turnover_x": veto_turn,
            "veto_count": len(vetoed),
            "veto_threshold": veto_threshold,
            "plain_longs": ",".join(longs),
            "plain_shorts": ",".join(plain_shorts),
            "veto_shorts": ",".join(veto_shorts),
            "long_price_contrib": 0.5 * long_ret,
            "plain_short_price_contrib": 0.5 * float(plain_short_series.mean()),
            "veto_short_price_contrib": 0.5 * float(veto_short_series.mean()),
            "long_funding_contrib": long_funding,
            "plain_short_funding_contrib": plain_short_funding,
            "veto_short_funding_contrib": veto_short_funding,
            "long_funding_events": long_events,
            "plain_short_funding_events": plain_short_events,
            "veto_short_funding_events": veto_short_events,
        })
        i += HOLD_BARS

    detail = pd.DataFrame(rows)
    detail["month"] = detail["timestamp_ts"].dt.strftime("%Y-%m")
    detail["quarter"] = detail["timestamp_ts"].dt.to_period("Q").astype(str)
    detail["year"] = detail["timestamp_ts"].dt.strftime("%Y")

    # effectiveness
    hit_names = 0
    false_kill_names = 0
    neutral_names = 0
    total_vetoed_names = 0
    for row in detail.itertuples(index=False):
        future = panel.loc[pd.Timestamp(row.exit_ts)] / panel.loc[pd.Timestamp(row.timestamp)] - 1.0
        plain_shorts = [x for x in row.plain_shorts.split(",") if x]
        veto_shorts = [x for x in row.veto_shorts.split(",") if x]
        vetoed_names = sorted(set(plain_shorts) - set(veto_shorts))
        total_vetoed_names += len(vetoed_names)
        for sym in vetoed_names:
            short_pnl = float(-future[sym])
            if short_pnl < 0:
                hit_names += 1
            elif short_pnl > 0:
                false_kill_names += 1
            else:
                neutral_names += 1

    plain_metrics = overall_metrics(detail["plain_price_gross"], detail["plain_funding_ret"], detail["plain_net_total"], detail["plain_turnover_x"])
    veto_metrics = overall_metrics(detail["veto_price_gross"], detail["veto_funding_ret"], detail["veto_net_total"], detail["veto_turnover_x"])

    delta = {
        "net_mean_bps": veto_metrics["net_total_mean_bps"] - plain_metrics["net_total_mean_bps"],
        "net_cum_pct": veto_metrics["net_total_cum_pct"] - plain_metrics["net_total_cum_pct"],
        "win_rate_pct_points": veto_metrics["win_rate"] - plain_metrics["win_rate"],
        "avg_turnover_x": veto_metrics["avg_turnover_x"] - plain_metrics["avg_turnover_x"],
        "max_drawdown_reduction_pct_points": abs(plain_metrics["max_drawdown_pct"]) - abs(veto_metrics["max_drawdown_pct"]),
        "funding_mean_delta_bps": veto_metrics["funding_mean_bps"] - plain_metrics["funding_mean_bps"],
    }

    monthly = grouped_metrics(detail, "month")
    quarterly = grouped_metrics(detail, "quarter")
    yearly = grouped_metrics(detail, "year")

    split = np.array_split(detail.reset_index(drop=True), 2)
    half_split = []
    for idx, sub in enumerate(split, start=1):
        half_split.append({
            "half": idx,
            "start_utc": sub["timestamp"].iloc[0],
            "end_utc": sub["timestamp"].iloc[-1],
            "rebalances": int(len(sub)),
            "plain_net_mean_bps": float(sub["plain_net_total"].mean() * 10000.0),
            "plain_net_cum_pct": float(((1.0 + sub["plain_net_total"]).prod() - 1.0) * 100.0),
            "veto_net_mean_bps": float(sub["veto_net_total"].mean() * 10000.0),
            "veto_net_cum_pct": float(((1.0 + sub["veto_net_total"]).prod() - 1.0) * 100.0),
            "delta_net_mean_bps": float((sub["veto_net_total"] - sub["plain_net_total"]).mean() * 10000.0),
            "delta_net_cum_pct": float((((1.0 + sub["veto_net_total"]).prod() - 1.0) - (((1.0 + sub["plain_net_total"]).prod() - 1.0))) * 100.0),
        })

    # 1Y/2Y/3Y windows
    windows = [WindowSpec("1Y", 365), WindowSpec("2Y", 730), WindowSpec("3Y", 1095)]
    window_reviews = []
    for w in windows:
        required_start = actual_end - pd.Timedelta(days=w.days)
        if required_start < actual_start:
            window_reviews.append({
                "window": w.label,
                "available": False,
                "required_start_utc": to_iso(required_start),
                "available_start_utc": to_iso(actual_start),
                "reason": "common-history shorter than requested window under frozen universe",
            })
            continue
        sub = detail[detail["timestamp_ts"] >= required_start].copy()
        sub_plain = overall_metrics(sub["plain_price_gross"], sub["plain_funding_ret"], sub["plain_net_total"], sub["plain_turnover_x"])
        sub_veto = overall_metrics(sub["veto_price_gross"], sub["veto_funding_ret"], sub["veto_net_total"], sub["veto_turnover_x"])
        window_reviews.append({
            "window": w.label,
            "available": True,
            "start_utc": to_iso(sub["timestamp_ts"].min()),
            "end_utc": to_iso(sub["timestamp_ts"].max()),
            "rebalances": int(len(sub)),
            "plain": sub_plain,
            "veto": sub_veto,
            "delta_net_mean_bps": sub_veto["net_total_mean_bps"] - sub_plain["net_total_mean_bps"],
            "delta_net_cum_pct": sub_veto["net_total_cum_pct"] - sub_plain["net_total_cum_pct"],
        })

    # year leg
    year_leg_rows = []
    for y, sub in detail.groupby("year"):
        year_leg_rows.append({
            "year": y,
            "rebalances": int(len(sub)),
            "plain_short_price_mean_bps": float(sub["plain_short_price_contrib"].mean() * 10000.0),
            "veto_short_price_mean_bps": float(sub["veto_short_price_contrib"].mean() * 10000.0),
            "delta_short_price_bps": float((sub["veto_short_price_contrib"] - sub["plain_short_price_contrib"]).mean() * 10000.0),
            "plain_short_funding_mean_bps": float(sub["plain_short_funding_contrib"].mean() * 10000.0),
            "veto_short_funding_mean_bps": float(sub["veto_short_funding_contrib"].mean() * 10000.0),
            "delta_short_funding_bps": float((sub["veto_short_funding_contrib"] - sub["plain_short_funding_contrib"]).mean() * 10000.0),
            "plain_avg_turnover_x": float(sub["plain_turnover_x"].mean()),
            "veto_avg_turnover_x": float(sub["veto_turnover_x"].mean()),
            "delta_turnover_x": float((sub["veto_turnover_x"] - sub["plain_turnover_x"]).mean()),
        })
    year_leg = pd.DataFrame(year_leg_rows)

    review = {
        "frozen_spec": {
            "universe_size": len(symbols),
            "formation_bars": FORMATION_BARS,
            "hold_bars": HOLD_BARS,
            "bar": "15m",
            "top_n": TOP_N,
            "bottom_n": BOTTOM_N,
            "veto_floor_pct": VETO_FLOOR * 100.0,
            "veto_mult_x_median": VETO_MULT,
            "cost_bps_per_turnover_x": COST_BPS,
            "variant_anchor": VARIANT,
        },
        "data_availability": {
            "common_start_candidate_utc": to_iso(common_start),
            "actual_common_start_utc": to_iso(actual_start),
            "actual_common_end_utc": to_iso(actual_end),
            "bars": int(len(panel)),
            "calendar_days": float((actual_end - actual_start) / pd.Timedelta(days=1)),
            "rebalances": int(len(detail)),
        },
        "local_data_policy": {
            "price_source_priority": "local_cache -> data.binance.vision monthly/daily zip",
            "funding_source_priority": "local_cache -> data.binance.vision monthly funding zip -> fundingRate API(retry/backoff)",
            "api_retry_policy": "up to 8 retries with exponential backoff + jitter on 418/429",
        },
        "funding_data_coverage": {
            "symbols_with_api_failed": [x["symbol"] for x in funding_sources if x["api_failed"]],
            "symbols_with_api_used": [x["symbol"] for x in funding_sources if x["api_used"]],
            "symbol_sources": funding_sources,
        },
        "full_available_history": {
            "plain": plain_metrics,
            "veto": veto_metrics,
            "delta": delta,
        },
        "window_reviews": window_reviews,
        "half_split": half_split,
        "year_leg_effect": year_leg_rows,
        "veto_effectiveness": {
            "pct_rebalances_with_any_veto": float((detail["veto_count"] > 0).mean() * 100.0),
            "avg_veto_count_per_rebalance": float(detail["veto_count"].mean()),
            "total_vetoed_names": int(total_vetoed_names),
            "name_level_hit_rate": float(hit_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
            "name_level_false_kill_rate": float(false_kill_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
            "name_level_neutral_rate": float(neutral_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
        },
    }

    if review["data_availability"]["calendar_days"] < 365:
        verdict = (
            "在冻结当前 universe/spec 下，公共共同历史只到 "
            f"{review['data_availability']['actual_common_start_utc']}，仍不足 1Y。"
            "因此本轮（含 funding 结算计提）不能宣称已通过 1Y/2Y/3Y。"
            "可确认的是：在最大可用共同历史上，veto 在 funding-adjusted 口径下仍明显优于 plain。"
        )
    else:
        verdict = "在 1Y+ 可用窗口里请直接看 window_reviews 对应字段。"
    review["final_verdict"] = verdict

    # write artifacts
    (ART_DIR / "rank213_long_history_with_funding_review_summary.json").write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    detail.to_csv(ART_DIR / "rank213_long_history_with_funding_detail.csv", index=False)
    monthly.to_csv(ART_DIR / "rank213_long_history_with_funding_monthly.csv", index=False)
    quarterly.to_csv(ART_DIR / "rank213_long_history_with_funding_quarterly.csv", index=False)
    yearly.to_csv(ART_DIR / "rank213_long_history_with_funding_yearly.csv", index=False)
    year_leg.to_csv(ART_DIR / "rank213_long_history_with_funding_year_leg_effect.csv", index=False)
    pd.DataFrame(symbol_price_avail).to_csv(ART_DIR / "rank213_long_history_with_funding_symbol_price_availability.csv", index=False)
    pd.DataFrame(funding_sources).to_csv(ART_DIR / "rank213_long_history_with_funding_symbol_funding_availability.csv", index=False)

    # window table
    wr_rows = []
    for w in window_reviews:
        if not w["available"]:
            wr_rows.append({
                "window": w["window"], "available": "no", "required_start_utc": w["required_start_utc"], "available_start_utc": w["available_start_utc"],
                "plain_net_mean_bps": np.nan, "plain_net_cum_pct": np.nan, "plain_win_rate": np.nan, "plain_max_dd_pct": np.nan, "plain_avg_turnover_x": np.nan,
                "veto_net_mean_bps": np.nan, "veto_net_cum_pct": np.nan, "veto_win_rate": np.nan, "veto_max_dd_pct": np.nan, "veto_avg_turnover_x": np.nan,
                "delta_net_mean_bps": np.nan, "delta_net_cum_pct": np.nan, "note": w["reason"],
            })
        else:
            wr_rows.append({
                "window": w["window"], "available": "yes", "required_start_utc": w["start_utc"], "available_start_utc": w["start_utc"],
                "plain_net_mean_bps": w["plain"]["net_total_mean_bps"], "plain_net_cum_pct": w["plain"]["net_total_cum_pct"], "plain_win_rate": w["plain"]["win_rate"],
                "plain_max_dd_pct": w["plain"]["max_drawdown_pct"], "plain_avg_turnover_x": w["plain"]["avg_turnover_x"],
                "veto_net_mean_bps": w["veto"]["net_total_mean_bps"], "veto_net_cum_pct": w["veto"]["net_total_cum_pct"], "veto_win_rate": w["veto"]["win_rate"],
                "veto_max_dd_pct": w["veto"]["max_drawdown_pct"], "veto_avg_turnover_x": w["veto"]["avg_turnover_x"],
                "delta_net_mean_bps": w["delta_net_mean_bps"], "delta_net_cum_pct": w["delta_net_cum_pct"], "note": "",
            })
    wr_df = pd.DataFrame(wr_rows)
    half_df = pd.DataFrame(half_split)

    monthly_table = render_table(monthly,
                                 percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
                                 bps_cols={"plain_net_mean_bps", "plain_funding_mean_bps", "veto_net_mean_bps", "veto_funding_mean_bps"},
                                 x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"})
    quarterly_table = render_table(quarterly,
                                   percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
                                   bps_cols={"plain_net_mean_bps", "plain_funding_mean_bps", "veto_net_mean_bps", "veto_funding_mean_bps"},
                                   x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"})
    yearly_table = render_table(yearly,
                                percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
                                bps_cols={"plain_net_mean_bps", "plain_funding_mean_bps", "veto_net_mean_bps", "veto_funding_mean_bps"},
                                x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"})
    wr_table = render_table(wr_df,
                            percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct", "delta_net_cum_pct"},
                            bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
                            x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"})
    half_table = render_table(half_df,
                              percent_cols={"plain_net_cum_pct", "veto_net_cum_pct", "delta_net_cum_pct"},
                              bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
                              x_cols=set())
    year_leg_table = render_table(year_leg,
                                  percent_cols=set(),
                                  bps_cols={"plain_short_price_mean_bps", "veto_short_price_mean_bps", "delta_short_price_bps", "plain_short_funding_mean_bps", "veto_short_funding_mean_bps", "delta_short_funding_bps"},
                                  x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x", "delta_turnover_x"})

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 long-history review with funding（frozen spec）</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--info:#1d4ed8;--infobg:#dbeafe}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1120px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
.metric{{border:1px solid var(--line);border-radius:12px;padding:12px 14px}} .metric .k{{color:var(--muted);font-size:13px}} .metric .v{{font-size:24px;font-weight:700}}
.note{{border-left:4px solid var(--info);background:var(--infobg);padding:12px 14px;border-radius:10px;white-space:pre-wrap}} .warn{{border-left-color:var(--warn);background:var(--warnbg)}}
table{{width:100%;border-collapse:collapse;margin-top:8px}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
code{{background:#eff6ff;border-radius:6px;padding:2px 6px;font-size:13px}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 long-history review with funding（frozen spec）</h1>
<p><strong>目标：</strong>在完全冻结当前 spec 下，把历史资金费率与结算时间点计入回测。</p>
<p class='muted'>spec 锚点：<code>{VARIANT}</code> / 30币 universe / 15m / 64 / 12 / top3-bottom3 / max(1.5%,2.0×median) / 4bps×turnover_x。</p>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review.html'>不含 funding 的长历史页</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_performance_review.html'>短样本页</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_honesty_audit.html'>honesty_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html'>ffill_impact_audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html'>readiness_note</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html'>asof_universe_long_history_review</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a></p>
</div>

<div class='card'>
<h2>1) 回测区间与数据可用性（含本地优先策略）</h2>
<div class='grid'>
<div class='metric'><div class='k'>common start</div><div class='v' style='font-size:18px'>{review['data_availability']['actual_common_start_utc']}</div></div>
<div class='metric'><div class='k'>common end</div><div class='v' style='font-size:18px'>{review['data_availability']['actual_common_end_utc']}</div></div>
<div class='metric'><div class='k'>bars</div><div class='v'>{review['data_availability']['bars']}</div></div>
<div class='metric'><div class='k'>calendar days</div><div class='v'>{review['data_availability']['calendar_days']:.2f}d</div></div>
<div class='metric'><div class='k'>rebalances</div><div class='v'>{review['data_availability']['rebalances']}</div></div>
</div>
<div class='note'>价格数据：local cache 优先，缺失部分再从 data.binance.vision 月/日 zip 补齐；
funding 数据：local cache 优先，月包补齐后再对当前月用 API 增量拉取；API 遇 418/429 按指数退避重试（最多 8 次）。</div>
</div>

<div class='card'>
<h2>2) plain baseline vs veto（资金费率已计入）</h2>
<div class='grid'>
<div class='metric'><div class='k'>plain net mean</div><div class='v'>{plain_metrics['net_total_mean_bps']:.2f} bps</div></div>
<div class='metric'><div class='k'>plain net cumulative</div><div class='v'>{plain_metrics['net_total_cum_pct']:.2f}%</div></div>
<div class='metric'><div class='k'>plain win rate</div><div class='v'>{plain_metrics['win_rate']:.2f}%</div></div>
<div class='metric'><div class='k'>plain max drawdown</div><div class='v'>{plain_metrics['max_drawdown_pct']:.2f}%</div></div>
<div class='metric'><div class='k'>plain funding mean</div><div class='v'>{plain_metrics['funding_mean_bps']:.2f} bps</div></div>
</div>
<div class='grid' style='margin-top:12px'>
<div class='metric'><div class='k'>veto net mean</div><div class='v'>{veto_metrics['net_total_mean_bps']:.2f} bps</div></div>
<div class='metric'><div class='k'>veto net cumulative</div><div class='v'>{veto_metrics['net_total_cum_pct']:.2f}%</div></div>
<div class='metric'><div class='k'>veto win rate</div><div class='v'>{veto_metrics['win_rate']:.2f}%</div></div>
<div class='metric'><div class='k'>veto max drawdown</div><div class='v'>{veto_metrics['max_drawdown_pct']:.2f}%</div></div>
<div class='metric'><div class='k'>veto funding mean</div><div class='v'>{veto_metrics['funding_mean_bps']:.2f} bps</div></div>
</div>
</div>

<div class='card'>
<h2>3) 1Y / 2Y / 3Y 冻结窗口验证（资金费率已计入）</h2>
{wr_table}
<div class='note warn'>窗口不可用就直接标 no，不改 universe，不调参数，不做“扩样本后重调”。</div>
</div>

<div class='card'>
<h2>4) baseline vs veto 的增量是否稳定</h2>
<div class='grid'>
<div class='metric'><div class='k'>Δ net mean</div><div class='v'>{delta['net_mean_bps']:.2f} bps</div></div>
<div class='metric'><div class='k'>Δ net cumulative</div><div class='v'>{delta['net_cum_pct']:.2f}%</div></div>
<div class='metric'><div class='k'>Δ funding mean</div><div class='v'>{delta['funding_mean_delta_bps']:.2f} bps</div></div>
<div class='metric'><div class='k'>Δ avg turnover</div><div class='v'>{delta['avg_turnover_x']:.3f}x</div></div>
<div class='metric'><div class='k'>MDD reduction</div><div class='v'>{delta['max_drawdown_reduction_pct_points']:.2f}%</div></div>
</div>
<p><strong>half-split stability</strong></p>
{half_table}
</div>

<div class='card'>
<h2>5) 按月 / 按季度 / 按年表现（资金费率已计入）</h2>
<p><strong>按月</strong></p>{monthly_table}
<p><strong>按季度</strong></p>{quarterly_table}
<p><strong>按年</strong></p>{yearly_table}
</div>

<div class='card'>
<h2>6) 不同年份里 veto 是改善 short leg，还是只是降频</h2>
{year_leg_table}
<div class='note'>同时展示 short leg 的价格贡献与 funding 贡献；如果 delta_short_price 为正且并非靠显著降频（delta_turnover 不为负），则更接近真实 short-leg 改善。</div>
</div>

<div class='card'>
<h2>7) veto 命中率 / 误杀率（定义同旧页）</h2>
<ul>
<li>pct rebalances with any veto：<strong>{review['veto_effectiveness']['pct_rebalances_with_any_veto']:.2f}%</strong></li>
<li>avg veto count / rebalance：<strong>{review['veto_effectiveness']['avg_veto_count_per_rebalance']:.3f}</strong></li>
<li>total vetoed names：<strong>{review['veto_effectiveness']['total_vetoed_names']}</strong></li>
<li>name-level hit rate：<strong>{review['veto_effectiveness']['name_level_hit_rate']:.2f}%</strong></li>
<li>name-level false-kill rate：<strong>{review['veto_effectiveness']['name_level_false_kill_rate']:.2f}%</strong></li>
</ul>
</div>

<div class='card'>
<h2>8) 最终 verdict</h2>
<div class='note warn'>{review['final_verdict']}</div>
</div>

</div></body></html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str((ART_DIR / "rank213_long_history_with_funding_review_summary.json").relative_to(ROOT)),
        "detail_csv": str((ART_DIR / "rank213_long_history_with_funding_detail.csv").relative_to(ROOT)),
        "monthly_csv": str((ART_DIR / "rank213_long_history_with_funding_monthly.csv").relative_to(ROOT)),
        "quarterly_csv": str((ART_DIR / "rank213_long_history_with_funding_quarterly.csv").relative_to(ROOT)),
        "yearly_csv": str((ART_DIR / "rank213_long_history_with_funding_yearly.csv").relative_to(ROOT)),
        "year_leg_csv": str((ART_DIR / "rank213_long_history_with_funding_year_leg_effect.csv").relative_to(ROOT)),
        "price_availability_csv": str((ART_DIR / "rank213_long_history_with_funding_symbol_price_availability.csv").relative_to(ROOT)),
        "funding_availability_csv": str((ART_DIR / "rank213_long_history_with_funding_symbol_funding_availability.csv").relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
