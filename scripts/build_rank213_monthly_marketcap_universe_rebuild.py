#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import re
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_monthly_marketcap_universe_rebuild.html"

FREEZE_PATH = ART_DIR / "rank213_formal_strategy_freeze_summary.json"
FORMAL_THREEWAY_PATH = ART_DIR / "rank213_formal_threeway_backtest_summary.json"
ADMISSION_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"

SUMMARY_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_summary.json"
MONTHLY_UNIVERSE_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_monthly_universe.csv"
COMPARE_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_compare.csv"
DETAIL_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_detail.csv"
CANDIDATE_PATH = ART_DIR / "rank213_monthly_marketcap_universe_rebuild_candidates.csv"

CACHE_DIR = ART_DIR / "rank213_local_cache" / "monthly_marketcap_universe"
COINGECKO_CACHE = CACHE_DIR / "coingecko_top500_markets.json"
EXCHANGE_CACHE = CACHE_DIR / "binance_exchange_info.json"

DATA_VISION_MONTHLY_KLINES = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{ym}.zip"
DATA_VISION_DAILY_KLINES = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/15m/{symbol}-15m-{ymd}.zip"
DATA_VISION_MONTHLY_KLINES_1D = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/1d/{symbol}-1d-{ym}.zip"
DATA_VISION_DAILY_KLINES_1D = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/1d/{symbol}-1d-{ymd}.zip"
COINGECKO_MARKETS = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}&sparkline=false"
BINANCE_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"

FORMATION_BARS = 64
HOLD_BARS = 12
TOP_N = 3
BOTTOM_N = 3
VETO_FLOOR = 0.015
VETO_MULT = 2.0
COST_BPS = 4.0
BAR_MINUTES = 15
TARGET_UNIVERSE_SIZE = 30


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_pct(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    if pd.isna(x):
        return ""
    return f"{x:.{digits}f} bps"


def max_drawdown(ret: pd.Series) -> float:
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def calc_stats(ret: pd.Series, turnover: pd.Series, gate_on: pd.Series | None = None) -> dict:
    if ret.empty:
        return {
            "rebalances": 0,
            "net_mean_bps": np.nan,
            "net_cum_pct": np.nan,
            "max_drawdown_pct": np.nan,
            "win_rate_pct": np.nan,
            "avg_turnover_x": np.nan,
            "gate_on_rate_pct": np.nan,
        }
    return {
        "rebalances": int(len(ret)),
        "net_mean_bps": float(ret.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + ret).prod() - 1.0) * 100.0),
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0),
        "win_rate_pct": float((ret > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "gate_on_rate_pct": float(pd.Series(gate_on).astype(bool).mean() * 100.0) if gate_on is not None else 100.0,
    }


def render_table(df: pd.DataFrame, pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cols = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(float(v))
            elif c in bps_cols:
                txt = fmt_bps(float(v))
            elif c in x_cols:
                txt = f"{float(v):.3f}x"
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            cols.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(cols) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def _retry_after_seconds(err: urllib.error.HTTPError, default_sleep: float, attempt: int) -> float:
    header = None
    try:
        header = err.headers.get("Retry-After") if err.headers else None
    except Exception:  # noqa: BLE001
        header = None
    if header:
        try:
            return max(float(header), default_sleep)
        except Exception:  # noqa: BLE001
            pass
    # 418 usually means temporary auto-ban on Binance side; sleep materially longer.
    if err.code == 418:
        return max(60.0, default_sleep * (attempt + 1) * 5.0)
    return max(default_sleep, default_sleep * (attempt + 1))


def safe_json_request(url: str, *, retries: int = 6, sleep_sec: float = 2.0):
    headers = {"User-Agent": "Mozilla/5.0"}
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in {418, 429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(_retry_after_seconds(e, sleep_sec, attempt))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt + 1 < retries:
                time.sleep(sleep_sec * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"failed request: {url} ({last_err})")


def safe_download(url: str, dst: Path, *, retries: int = 7, sleep_sec: float = 2.0) -> bool:
    ensure_dir(dst.parent)
    if dst.exists() and dst.stat().st_size > 0:
        return True
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                blob = r.read()
            dst.write_bytes(blob)
            return True
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 404:
                return False
            if e.code in {418, 429, 500, 502, 503, 504} and attempt + 1 < retries:
                time.sleep(_retry_after_seconds(e, sleep_sec, attempt))
                continue
            raise
        except (urllib.error.URLError, ConnectionResetError, TimeoutError) as e:
            last_err = e
            if attempt + 1 < retries:
                time.sleep(max(sleep_sec, sleep_sec * (attempt + 1)))
                continue
            raise
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt + 1 < retries:
                time.sleep(max(sleep_sec, sleep_sec * (attempt + 1)))
                continue
            raise
    raise RuntimeError(f"failed download: {url} ({last_err})")


def read_kline_zip(path: Path) -> pd.DataFrame:
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "close", "volume", "quote_volume"])
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
    for col in ["close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "close", "volume", "quote_volume"])
    return pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True),
        "close": df["close"].astype(float),
        "volume": df["volume"].astype(float),
        "quote_volume": df["quote_volume"].astype(float),
    }).drop_duplicates("timestamp").sort_values("timestamp")


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    cur = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    end_month = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    out = []
    while cur <= end_month:
        out.append(cur.strftime("%Y-%m"))
        cur = cur + pd.offsets.MonthBegin(1)
    return out


def normalize_base_asset(base: str) -> str:
    return re.sub(r"^\d+", "", base.lower())


def contract_multiplier_from_base(base: str) -> float:
    m = re.match(r"^(\d+)", str(base))
    return float(m.group(1)) if m else 1.0


def load_exchange_info() -> dict:
    ensure_dir(CACHE_DIR)
    if EXCHANGE_CACHE.exists():
        return json.loads(EXCHANGE_CACHE.read_text(encoding="utf-8"))
    obj = safe_json_request(BINANCE_EXCHANGE_INFO)
    EXCHANGE_CACHE.write_text(json.dumps(obj), encoding="utf-8")
    return obj


def load_coingecko_top500() -> list[dict]:
    ensure_dir(CACHE_DIR)
    if COINGECKO_CACHE.exists():
        return json.loads(COINGECKO_CACHE.read_text(encoding="utf-8"))
    rows = []
    for page in [1, 2]:
        rows.extend(safe_json_request(COINGECKO_MARKETS.format(page=page), sleep_sec=4.0))
        time.sleep(2.0)
    COINGECKO_CACHE.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def build_candidates() -> pd.DataFrame:
    ex = load_exchange_info()
    coins = load_coingecko_top500()

    by_symbol: dict[str, list[dict]] = {}
    for c in coins:
        by_symbol.setdefault(str(c.get("symbol", "")).lower(), []).append(c)

    rows = []
    for s in ex["symbols"]:
        if s.get("quoteAsset") != "USDT" or s.get("contractType") != "PERPETUAL" or s.get("status") != "TRADING":
            continue
        symbol = str(s["symbol"])
        base = str(s.get("baseAsset", ""))
        # Guard against malformed / prank / non-ASCII exchangeInfo entries.
        if not re.fullmatch(r"[A-Z0-9]+USDT", symbol):
            continue
        if not re.fullmatch(r"[A-Z0-9]+", base):
            continue
        norm = normalize_base_asset(base)
        contract_multiplier = contract_multiplier_from_base(base)
        cands = by_symbol.get(norm, [])
        if len(cands) != 1:
            continue
        c = cands[0]
        current_price = float(c.get("current_price") or 0.0)
        market_cap = float(c.get("market_cap") or 0.0)
        if current_price <= 0 or market_cap <= 0:
            continue
        rows.append({
            "symbol": symbol,
            "base_asset": base,
            "normalized_base": norm,
            "onboard_utc": to_iso(pd.to_datetime(int(s["onboardDate"]), unit="ms", utc=True)),
            "onboard_ms": int(s["onboardDate"]),
            "coingecko_id": str(c["id"]),
            "coingecko_symbol": str(c.get("symbol", "")),
            "coingecko_name": str(c.get("name", "")),
            "contract_multiplier": contract_multiplier,
            "current_price": current_price,
            "current_market_cap": market_cap,
            "market_cap_rank_current": float(c.get("market_cap_rank") or np.nan),
            "supply_proxy": market_cap / current_price,
        })
    out = pd.DataFrame(rows).sort_values(["market_cap_rank_current", "symbol"])
    out.to_csv(CANDIDATE_PATH, index=False)
    return out


def load_daily_prices(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    cache_path = CACHE_DIR / "daily_1d" / f"{symbol}.csv"
    need_start = start.floor("1D")
    need_end = end.floor("1D")
    if cache_path.exists():
        old = pd.read_csv(cache_path)
        old["timestamp"] = pd.to_datetime(old["timestamp"], utc=True, errors="coerce")
        old["close"] = pd.to_numeric(old["close"], errors="coerce")
        if "volume" not in old.columns:
            old["volume"] = np.nan
        if "quote_volume" not in old.columns:
            old["quote_volume"] = np.nan
        old["volume"] = pd.to_numeric(old["volume"], errors="coerce")
        old["quote_volume"] = pd.to_numeric(old["quote_volume"], errors="coerce")
        old = old.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
        if not old.empty and old["timestamp"].min() <= need_start and old["timestamp"].max() >= need_end - pd.Timedelta(days=1):
            return old[(old["timestamp"] >= need_start) & (old["timestamp"] <= need_end)].reset_index(drop=True)
    else:
        old = pd.DataFrame(columns=["timestamp", "close", "volume", "quote_volume"])

    months = month_range(need_start, need_end)
    current_month = need_end.strftime("%Y-%m")
    parts: list[pd.DataFrame] = [old] if not old.empty else []

    for ym in months:
        if ym == current_month:
            continue
        p = CACHE_DIR / "raw_1d" / "monthly" / symbol / f"{symbol}-1d-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_KLINES_1D.format(symbol=symbol, ym=ym), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        time.sleep(0.003)

    cur = pd.Timestamp(need_end.year, need_end.month, 1, tz="UTC")
    if cur < need_start.normalize():
        cur = need_start.normalize()
    while cur <= need_end.normalize():
        ymd = cur.strftime("%Y-%m-%d")
        p = CACHE_DIR / "raw_1d" / "daily" / symbol / f"{symbol}-1d-{ymd}.zip"
        ok = safe_download(DATA_VISION_DAILY_KLINES_1D.format(symbol=symbol, ymd=ymd), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        cur += pd.Timedelta(days=1)
        time.sleep(0.001)

    if not parts:
        return pd.DataFrame(columns=["timestamp", "close"])
    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    ensure_dir(cache_path.parent)
    out.to_csv(cache_path, index=False)
    return out[(out["timestamp"] >= need_start) & (out["timestamp"] <= need_end)].reset_index(drop=True)


def build_monthly_universe(candidates: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, frozen_symbols: list[str]) -> pd.DataFrame:
    month_start_floor = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    month_end_floor = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    months = pd.date_range(start=month_start_floor, end=month_end_floor, freq="MS", tz="UTC")
    rows = []
    prev = set()
    frozen_set = set(frozen_symbols)
    formation_buffer = pd.Timedelta(minutes=FORMATION_BARS * BAR_MINUTES)

    daily_cache: dict[str, pd.DataFrame] = {}
    for _, cand in candidates.iterrows():
        daily = load_daily_prices(cand["symbol"], start - pd.Timedelta(days=7), end + pd.Timedelta(days=7))
        if daily.empty:
            continue
        daily_cache[str(cand["symbol"])] = daily.sort_values("timestamp").reset_index(drop=True)

    for month_start in months:
        eligible_rows = []
        for _, cand in candidates.iterrows():
            onboard = pd.to_datetime(int(cand["onboard_ms"]), unit="ms", utc=True)
            if onboard > month_start - formation_buffer:
                continue
            if pd.isna(cand.get("supply_proxy")) or float(cand["supply_proxy"]) <= 0:
                continue
            daily = daily_cache.get(str(cand["symbol"]))
            if daily is None or daily.empty:
                continue
            sub = daily[daily["timestamp"] < month_start]
            if sub.empty:
                continue
            px = float(sub.iloc[-1]["close"])
            if not np.isfinite(px) or px <= 0:
                continue
            multiplier = float(cand.get("contract_multiplier", contract_multiplier_from_base(str(cand.get("base_asset", "")))) or 1.0)
            # Binance 1000*/1000000* perps quote a pack price. Convert back to the underlying-token price
            # before multiplying by CoinGecko token supply; otherwise market-cap proxy is inflated by multiplier.
            mc = float(cand["supply_proxy"]) * (px / multiplier)
            eligible_rows.append((cand["symbol"], mc))

        eligible_rows.sort(key=lambda x: x[1], reverse=True)
        selected = [sym for sym, _ in eligible_rows[:TARGET_UNIVERSE_SIZE]]
        selected_set = set(selected)
        entered = sorted(selected_set - prev)
        exited = sorted(prev - selected_set)
        overlap = sorted(selected_set & frozen_set)
        only_selected = sorted(selected_set - frozen_set)
        only_frozen = sorted(frozen_set - selected_set)

        rows.append({
            "month": month_start.strftime("%Y-%m"),
            "month_start_utc": to_iso(month_start),
            "selected_count": int(len(selected)),
            "selected_symbols": ",".join(selected),
            "entered_count": int(len(entered)),
            "entered_symbols": ",".join(entered),
            "exited_count": int(len(exited)),
            "exited_symbols": ",".join(exited),
            "overlap_with_frozen_count": int(len(overlap)),
            "overlap_with_frozen_symbols": ",".join(overlap),
            "selected_not_in_frozen_count": int(len(only_selected)),
            "selected_not_in_frozen_symbols": ",".join(only_selected),
            "frozen_not_in_selected_count": int(len(only_frozen)),
            "frozen_not_in_selected_symbols": ",".join(only_frozen),
        })
        prev = selected_set

    out = pd.DataFrame(rows)
    out.to_csv(MONTHLY_UNIVERSE_PATH, index=False)
    return out


def load_15m_symbol(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    cache_path = CACHE_DIR / "klines_15m" / f"{symbol}.csv"
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True, errors="coerce")
        cached["close"] = pd.to_numeric(cached["close"], errors="coerce")
        if "volume" not in cached.columns:
            cached["volume"] = np.nan
        if "quote_volume" not in cached.columns:
            cached["quote_volume"] = np.nan
        cached["volume"] = pd.to_numeric(cached["volume"], errors="coerce")
        cached["quote_volume"] = pd.to_numeric(cached["quote_volume"], errors="coerce")
        cached = cached.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
        if not cached.empty and cached["timestamp"].min() <= start and cached["timestamp"].max() >= end - pd.Timedelta(days=1):
            return cached[(cached["timestamp"] >= start) & (cached["timestamp"] <= end)].reset_index(drop=True)
    else:
        cached = pd.DataFrame(columns=["timestamp", "close", "volume", "quote_volume"])
    onboard = None
    # no fetch before start; month-based build already limits symbols
    months = month_range(start, end)
    current_month = end.strftime("%Y-%m")
    parts: list[pd.DataFrame] = [cached] if not cached.empty else []
    for ym in months:
        if ym == current_month:
            continue
        p = CACHE_DIR / "raw_15m" / "monthly" / symbol / f"{symbol}-15m-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_KLINES.format(symbol=symbol, ym=ym), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        time.sleep(0.005)
    cur = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    while cur <= end.normalize():
        ymd = cur.strftime("%Y-%m-%d")
        p = CACHE_DIR / "raw_15m" / "daily" / symbol / f"{symbol}-15m-{ymd}.zip"
        ok = safe_download(DATA_VISION_DAILY_KLINES.format(symbol=symbol, ymd=ymd), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        cur += pd.Timedelta(days=1)
        time.sleep(0.002)
    if not parts:
        return pd.DataFrame(columns=["timestamp", "close"])
    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp")
    ensure_dir(cache_path.parent)
    out.to_csv(cache_path, index=False)
    return out[(out["timestamp"] >= start) & (out["timestamp"] <= end)].reset_index(drop=True)


def build_panel(symbols: list[str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    full_index = pd.date_range(start=start, end=end, freq="15min", tz="UTC")
    panel = pd.DataFrame(index=full_index)
    for symbol in symbols:
        df = load_15m_symbol(symbol, start, end)
        s = df.set_index("timestamp")["close"].astype(float) if not df.empty else pd.Series(dtype=float)
        panel[symbol] = s.reindex(full_index)
    return panel


def run_backtest(panel: pd.DataFrame, monthly_universe: dict[str, list[str]], onboard_map: dict[str, int]) -> pd.DataFrame:
    idx = panel.index
    rows = []
    i = FORMATION_BARS
    while i + HOLD_BARS < len(panel):
        ts = idx[i]
        exit_ts = idx[i + HOLD_BARS]
        month = ts.strftime("%Y-%m")
        month_symbols = monthly_universe.get(month, [])
        if len(month_symbols) < TOP_N + BOTTOM_N:
            i += HOLD_BARS
            continue

        eligible = []
        for sym in month_symbols:
            onboard = pd.to_datetime(int(onboard_map[sym]), unit="ms", utc=True)
            if ts < onboard:
                continue
            close_window = panel[sym].iloc[i - FORMATION_BARS:i + 1]
            if close_window.isna().any():
                continue
            if pd.isna(panel[sym].iat[i + HOLD_BARS]):
                continue
            eligible.append(sym)

        if len(eligible) < TOP_N + BOTTOM_N:
            i += HOLD_BARS
            continue

        close_window = panel[eligible].iloc[i - FORMATION_BARS:i + 1]
        hist = close_window.pct_change().iloc[1:]
        if hist.isna().any().any():
            i += HOLD_BARS
            continue

        cumret = close_window.iloc[-1] / close_window.iloc[0] - 1.0
        universe_med = hist.abs().max().median()
        veto_threshold = max(VETO_FLOOR, VETO_MULT * float(universe_med if pd.notna(universe_med) else 0.0))

        rank = cumret.sort_values()
        longs = rank.index[-TOP_N:].tolist()[::-1]
        plain_shorts = rank.index[:BOTTOM_N].tolist()

        short_info = [(sym, float(hist[sym].max())) for sym in plain_shorts]
        eligible_shorts = [sym for sym, mx in short_info if pd.notna(mx) and mx <= veto_threshold]
        vetoed = [sym for sym, mx in short_info if pd.notna(mx) and mx > veto_threshold]
        refill = [sym for sym in rank.index if sym not in longs and sym not in plain_shorts]

        veto_shorts = eligible_shorts.copy()
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

        future = panel[eligible].iloc[i + HOLD_BARS] / panel[eligible].iloc[i] - 1.0
        long_ret = float(future[longs].mean())
        plain_short_series = -future[plain_shorts]
        veto_short_series = -future[veto_shorts]

        plain_gross = 0.5 * long_ret + 0.5 * float(plain_short_series.mean())
        veto_gross = 0.5 * long_ret + 0.5 * float(veto_short_series.mean())
        plain_turnover = 1.0
        veto_turnover = 1.0 + (len(set(veto_shorts) ^ set(plain_shorts)) / 6.0)

        rows.append({
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
            "month": month,
            "month_universe_size": int(len(month_symbols)),
            "month_universe_symbols": ",".join(month_symbols),
            "eligible_universe_size": int(len(eligible)),
            "eligible_symbols": ",".join(eligible),
            "plain_longs": ",".join(longs),
            "plain_shorts": ",".join(plain_shorts),
            "veto_shorts": ",".join(veto_shorts),
            "veto_count": int(len(vetoed)),
            "veto_threshold": float(veto_threshold),
            "plain_gross": float(plain_gross),
            "veto_gross": float(veto_gross),
            "plain_turnover_x": float(plain_turnover),
            "veto_turnover_x": float(veto_turnover),
            "long_price_contrib": float(0.5 * long_ret),
            "plain_short_price_contrib": float(0.5 * float(plain_short_series.mean())),
            "veto_short_price_contrib": float(0.5 * float(veto_short_series.mean())),
            "btc_cumret": float(cumret["BTCUSDT"]) if "BTCUSDT" in cumret.index else np.nan,
            "universe_cumret_mean": float(cumret.mean()),
            "universe_cumret_std": float(cumret.std()),
            "universe_cumret_iqr": float(cumret.quantile(0.75) - cumret.quantile(0.25)),
            "universe_realized_vol_median": float(hist.std().median()),
        })
        i += HOLD_BARS

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    unit = COST_BPS / 10000.0
    out["timestamp"] = out["timestamp_ts"].map(to_iso)
    out["plain_net"] = out["plain_gross"] - out["plain_turnover_x"] * unit
    out["veto_net"] = out["veto_gross"] - out["veto_turnover_x"] * unit
    return out


def apply_frozen_gate(detail: pd.DataFrame, freeze: dict) -> pd.DataFrame:
    gate = freeze["gate"]
    rules = gate["rules"]
    vote_ratio = float(gate.get("vote_ratio", 0.67))
    lookback_days = int(gate.get("lookback_days", 30))

    out = detail.copy().sort_values("timestamp_ts").reset_index(drop=True)
    out["timestamp_ts"] = pd.to_datetime(out["timestamp_ts"], utc=True)
    out["exit_ts"] = pd.to_datetime(out["exit_ts"], utc=True, errors="coerce")

    veto_active_rate = (pd.to_numeric(out["veto_count"], errors="coerce").fillna(0) > 0).astype(float).to_numpy()
    xs_dispersion_bps = pd.to_numeric(out["universe_cumret_std"], errors="coerce").astype(float).to_numpy() * 10000.0
    ls_divergence_bps = (
        pd.to_numeric(out["long_price_contrib"], errors="coerce").astype(float).to_numpy()
        - pd.to_numeric(out["veto_short_price_contrib"], errors="coerce").astype(float).to_numpy()
    ) * 10000.0

    ts_ns = out["timestamp_ts"].astype("int64").to_numpy()
    exit_ns = out["exit_ts"].astype("int64").to_numpy()
    start_ns = ts_ns - pd.Timedelta(days=lookback_days).value
    start_ixs = np.searchsorted(ts_ns, start_ns, side="left")
    end_decision_ixs = np.arange(len(out), dtype=int)
    end_realized_ixs = np.searchsorted(exit_ns, ts_ns, side="right") - 1

    def window_mean(values: np.ndarray, end_ixs: np.ndarray) -> np.ndarray:
        valid = np.isfinite(values)
        csum = np.concatenate([[0.0], np.cumsum(np.where(valid, values, 0.0))])
        ccnt = np.concatenate([[0], np.cumsum(valid.astype(int))])
        res = np.full(len(values), np.nan, dtype=float)
        for i, (start_ix, end_ix) in enumerate(zip(start_ixs, end_ixs)):
            if end_ix < start_ix or end_ix < 0:
                continue
            total = csum[end_ix + 1] - csum[start_ix]
            count = ccnt[end_ix + 1] - ccnt[start_ix]
            if count > 0:
                res[i] = total / count
        return res

    out["gate_feature_veto_active_rate"] = window_mean(veto_active_rate, end_decision_ixs)
    out["gate_feature_xs_dispersion_bps"] = window_mean(xs_dispersion_bps, end_decision_ixs)
    out["gate_feature_ls_divergence_bps"] = window_mean(ls_divergence_bps, end_realized_ixs)

    out["gate_on"] = False
    out["gate_votes"] = 0
    out["gate_valid_rules"] = 0
    out["gate_needed_votes"] = 0
    for idx_row, row in out.iterrows():
        votes = 0
        valid = 0
        for rule in rules:
            var = str(rule["variable"])
            col = f"gate_feature_{var}"
            val = row[col] if col in out.columns else np.nan
            if pd.isna(val):
                continue
            valid += 1
            ok = bool(float(val) >= float(rule["threshold"])) if bool(rule["higher_is_good"]) else bool(float(val) <= float(rule["threshold"]))
            votes += int(ok)
        needed = max(1, int(np.ceil(valid * vote_ratio))) if valid > 0 else 1
        out.at[idx_row, "gate_on"] = bool(votes >= needed) if valid > 0 else False
        out.at[idx_row, "gate_votes"] = int(votes)
        out.at[idx_row, "gate_valid_rules"] = int(valid)
        out.at[idx_row, "gate_needed_votes"] = int(needed)
    return out


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    formal = json.loads(FORMAL_THREEWAY_PATH.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION_SUMMARY_PATH.read_text(encoding="utf-8"))
    frozen_symbols = admission["symbols"]

    sample_start = pd.Timestamp("2020-02-01T00:00:00Z")
    sample_end = pd.to_datetime(formal["sample"]["end_utc"], utc=True)

    candidates = build_candidates()
    monthly_universe_df = build_monthly_universe(candidates, sample_start, sample_end, frozen_symbols)
    monthly_universe = {
        row["month"]: [s for s in str(row["selected_symbols"]).split(",") if s]
        for _, row in monthly_universe_df.iterrows()
    }

    union_symbols = sorted({s for syms in monthly_universe.values() for s in syms})
    onboard_map = {str(row["symbol"]): int(row["onboard_ms"]) for _, row in candidates.iterrows()}

    panel_start = sample_start - pd.Timedelta(minutes=FORMATION_BARS * BAR_MINUTES)
    panel_end = sample_end + pd.Timedelta(minutes=HOLD_BARS * BAR_MINUTES)
    panel = build_panel(union_symbols, panel_start, panel_end)
    detail = run_backtest(panel, monthly_universe, onboard_map)
    if detail.empty:
        raise RuntimeError("monthly marketcap rebuild returned empty detail")
    detail = apply_frozen_gate(detail, freeze)
    detail["gate_net"] = np.where(detail["gate_on"], detail["veto_net"], 0.0)
    detail["gate_turnover_x"] = np.where(detail["gate_on"], detail["veto_turnover_x"], 0.0)
    detail.to_csv(DETAIL_PATH, index=False)

    rebuild_plain = calc_stats(detail["plain_net"], detail["plain_turnover_x"])
    rebuild_veto = calc_stats(detail["veto_net"], detail["veto_turnover_x"])
    rebuild_gate = calc_stats(detail["gate_net"], detail["gate_turnover_x"], gate_on=detail["gate_on"])

    frozen_full = formal["full_period"]
    compare = pd.DataFrame([
        {"version": "frozen30", "strategy": "plain baseline", **frozen_full["plain"]},
        {"version": "frozen30", "strategy": "baseline+veto", **frozen_full["baseline_plus_veto"]},
        {"version": "frozen30", "strategy": "baseline+veto+gate", **frozen_full["baseline_plus_veto_plus_gate"]},
        {"version": "monthly_marketcap_rebuild", "strategy": "plain baseline", **rebuild_plain},
        {"version": "monthly_marketcap_rebuild", "strategy": "baseline+veto", **rebuild_veto},
        {"version": "monthly_marketcap_rebuild", "strategy": "baseline+veto+gate", **rebuild_gate},
    ])[["version", "strategy", "rebalances", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct", "avg_turnover_x", "gate_on_rate_pct"]]
    compare.to_csv(COMPARE_PATH, index=False)

    avg_overlap = float(monthly_universe_df["overlap_with_frozen_count"].mean()) if not monthly_universe_df.empty else np.nan
    avg_new = float(monthly_universe_df["selected_not_in_frozen_count"].mean()) if not monthly_universe_df.empty else np.nan

    gate_cum = rebuild_gate["net_cum_pct"]
    gate_mean = rebuild_gate["net_mean_bps"]
    if gate_cum > 0 and gate_mean > 0:
        final_verdict = (
            "在按月 marketcap 重建的 as-of universe 下，baseline+veto+gate 仍保持正 net_mean / 正累计收益，"
            "说明这条线在更科学的选池下没有被直接推翻。"
        )
    elif gate_mean > 0:
        final_verdict = (
            "在按月 marketcap 重建的 as-of universe 下，gate 线仍有正 net_mean，但累计收益不再像 frozen30 那样强，"
            "结论应降级为‘仍有边际，但显著变弱’。"
        )
    else:
        final_verdict = (
            "在按月 marketcap 重建的 as-of universe 下，gate 线已失去正 net_mean，"
            "说明 frozen30 版本的强结果有较大概率受静态选池/幸存者偏差放大。"
        )

    summary = {
        "scope": "monthly marketcap universe rebuild under frozen rank213 baseline/veto/gate/cost settings",
        "important_limitation": (
            "本页使用 current CoinGecko top500 的 current market_cap/current_price 推导 static supply proxy，再乘以当月月初前最近可见 Binance 价格近似 monthly marketcap。"
            "原因是当前环境无法直接调用免密历史 marketcap API；因此这是一条比 frozen30 更科学、但仍非完美的 marketcap-proxy rebuild。"
        ),
        "source_paths": {
            "formal_threeway_summary": str(FORMAL_THREEWAY_PATH.relative_to(ROOT)),
            "frozen_rules": str(FREEZE_PATH.relative_to(ROOT)),
            "candidates_csv": str(CANDIDATE_PATH.relative_to(ROOT)),
            "monthly_universe_csv": str(MONTHLY_UNIVERSE_PATH.relative_to(ROOT)),
            "detail_csv": str(DETAIL_PATH.relative_to(ROOT)),
            "compare_csv": str(COMPARE_PATH.relative_to(ROOT)),
        },
        "coverage": {
            "candidate_count": int(len(candidates)),
            "union_symbols_selected_any_month": int(len(union_symbols)),
            "avg_overlap_with_frozen30": avg_overlap,
            "avg_selected_not_in_frozen30": avg_new,
        },
        "sample": {
            "start_utc": to_iso(pd.to_datetime(detail["timestamp_ts"], utc=True).min()),
            "end_utc": to_iso(pd.to_datetime(detail["timestamp_ts"], utc=True).max()),
            "rebalances": int(len(detail)),
        },
        "metrics": {
            "frozen30": frozen_full,
            "monthly_marketcap_rebuild": {
                "plain": rebuild_plain,
                "baseline_plus_veto": rebuild_veto,
                "baseline_plus_veto_plus_gate": rebuild_gate,
            },
        },
        "final_verdict": final_verdict,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    compare_html = render_table(compare, pct_cols={"net_cum_pct", "max_drawdown_pct", "win_rate_pct", "gate_on_rate_pct"}, bps_cols={"net_mean_bps"}, x_cols={"avg_turnover_x"})
    monthly_view = monthly_universe_df[["month", "selected_count", "entered_count", "exited_count", "overlap_with_frozen_count", "selected_not_in_frozen_count", "frozen_not_in_selected_count"]].copy()
    monthly_html = render_table(monthly_view)

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 monthly marketcap universe rebuild (retired)</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--note:#dbeafe}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1200px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} .warn{{border-left:4px solid var(--warn);background:var(--warnbg);padding:12px 14px;border-radius:10px;white-space:pre-wrap}} .note{{border-left:4px solid #1d4ed8;background:var(--note);padding:12px 14px;border-radius:10px;white-space:pre-wrap}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}} code{{background:#eff6ff;border-radius:6px;padding:2px 6px}} a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
  <h1>Rank213 monthly_marketcap_universe_rebuild 已退役</h1>
  <p>这页只保留为历史审计记录。当前滚动选池主线已切到 <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'><code>monthly_volume_universe_rebuild</code></a>，并由 <a href='/momentum/paper/rank213_evidence_map.html'><code>evidence_map</code></a> 统一解释证据等级。</p>
  <p><a href='/momentum/paper/rank213_evidence_map.html'>evidence_map</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner</a></p>
</div>
<div class='card'>
  <h2>退役原因</h2>
  <div class='warn'>marketcap proxy 曾用于探索，但存在代理口径和 1000*/1000000* 合约 multiplier 扭曲问题。后续不要再用本页作为当前结论或策略有效性证据。</div>
</div>
<div class='card'>
  <h2>重要限制</h2>
  <div class='warn'>{summary['important_limitation']}</div>
</div>
<div class='card'>
  <h2>与 frozen30 的同口径对比</h2>
  {compare_html}
  <p class='muted'>compare csv: <code>{COMPARE_PATH.relative_to(ROOT)}</code></p>
</div>
<div class='card'>
  <h2>每月 universe 变动摘要</h2>
  {monthly_html}
  <p class='muted'>full monthly universe csv: <code>{MONTHLY_UNIVERSE_PATH.relative_to(ROOT)}</code></p>
</div>
<div class='card'>
  <h2>最终结论</h2>
  <div class='note'>{final_verdict}</div>
</div>
</div></body></html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str(SUMMARY_PATH.relative_to(ROOT)),
        "monthly_universe_csv": str(MONTHLY_UNIVERSE_PATH.relative_to(ROOT)),
        "compare_csv": str(COMPARE_PATH.relative_to(ROOT)),
        "detail_csv": str(DETAIL_PATH.relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
        "union_symbols": len(union_symbols),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
