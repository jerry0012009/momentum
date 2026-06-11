#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
CACHE_DIR = ART_DIR / "rank213_local_cache" / "asof_universe"

DATA_VISION_MONTHLY_KLINES = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{ym}.zip"
DATA_VISION_DAILY_KLINES = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/15m/{symbol}-15m-{ymd}.zip"
RECENT_FUTURES_KLINES_API = "https://fapi.binance.com/fapi/v1/klines"

COST_BPS = 4.0
FORMATION_BARS = 64
HOLD_BARS = 12
TOP_N = 3
BOTTOM_N = 3
VETO_FLOOR = 0.015
VETO_MULT = 2.0
VARIANT = "f64_h12_floor150_mult2p0"
BAR_MINUTES = 15
MAX_LOOKBACK_DAYS = 2920  # target up to ~8Y if data exists
RECENT_KLINES_LIMIT = 1500
RECENT_TAIL_STALE_TOLERANCE = pd.Timedelta(minutes=BAR_MINUTES)

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


def fmt_pct(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f} bps"


def fmt_x(x: float, digits: int = 3) -> str:
    return f"{x:.{digits}f}x"


def max_drawdown(ret: pd.Series) -> float:
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


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


def fetch_recent_futures_klines(symbol: str, limit: int = RECENT_KLINES_LIMIT) -> pd.DataFrame:
    params = urllib.parse.urlencode({
        "symbol": symbol,
        "interval": "15m",
        "limit": max(1, min(int(limit), RECENT_KLINES_LIMIT)),
    })
    with urllib.request.urlopen(f"{RECENT_FUTURES_KLINES_API}?{params}", timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    rows = []
    for row in payload:
        if not isinstance(row, list) or len(row) < 5:
            continue
        open_time = pd.to_numeric(row[0], errors="coerce")
        close = pd.to_numeric(row[4], errors="coerce")
        if pd.isna(open_time) or pd.isna(close):
            continue
        rows.append({
            "timestamp": pd.to_datetime(int(open_time), unit="ms", utc=True),
            "close": float(close),
        })
    if not rows:
        return pd.DataFrame(columns=["timestamp", "close"])
    return pd.DataFrame(rows).drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)


def load_or_build_symbol(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    cache_path = CACHE_DIR / "klines_15m" / f"{symbol}.csv"
    cached = pd.DataFrame(columns=["timestamp", "close"])
    if cache_path.exists():
        cached = pd.read_csv(cache_path)
        cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True, errors="coerce")
        cached["close"] = pd.to_numeric(cached["close"], errors="coerce")
        cached = cached.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").sort_values("timestamp")
        if not cached.empty:
            have_start = cached["timestamp"].min()
            have_end = cached["timestamp"].max()
            if have_start <= start and have_end >= end - RECENT_TAIL_STALE_TOLERANCE:
                return cached[(cached["timestamp"] >= start) & (cached["timestamp"] <= end)].reset_index(drop=True)

    onboard = pd.to_datetime(SYMBOL_ONBOARD_DATE_MS[symbol], unit="ms", utc=True)
    symbol_start = max(start, onboard)
    months = month_range(symbol_start, end)
    current_month = end.strftime("%Y-%m")

    parts: list[pd.DataFrame] = []
    for ym in months:
        if ym == current_month:
            continue
        p = CACHE_DIR / "raw" / "monthly" / symbol / f"{symbol}-15m-{ym}.zip"
        ok = safe_download(DATA_VISION_MONTHLY_KLINES.format(symbol=symbol, ym=ym), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        time.sleep(0.01)

    cur = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    if cur < symbol_start.normalize():
        cur = symbol_start.normalize()
    while cur <= end.normalize():
        ymd = cur.strftime("%Y-%m-%d")
        p = CACHE_DIR / "raw" / "daily" / symbol / f"{symbol}-15m-{ymd}.zip"
        ok = safe_download(DATA_VISION_DAILY_KLINES.format(symbol=symbol, ymd=ymd), p)
        if ok:
            part = read_kline_zip(p)
            if not part.empty:
                parts.append(part)
        cur += pd.Timedelta(days=1)
        time.sleep(0.003)

    now_utc = pd.Timestamp.now(tz="UTC")
    if end >= now_utc - pd.Timedelta(days=2):
        recent = fetch_recent_futures_klines(symbol)
        if not recent.empty:
            parts.append(recent)

    if not parts and cached.empty:
        return pd.DataFrame(columns=["timestamp", "close"])

    merged_parts = [df for df in [cached, *parts] if not df.empty]
    out = pd.concat(merged_parts, ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp") if merged_parts else pd.DataFrame(columns=["timestamp", "close"])
    out = out[(out["timestamp"] >= start) & (out["timestamp"] <= end)].reset_index(drop=True)

    ensure_dir(cache_path.parent)
    out.to_csv(cache_path, index=False)
    return out


def build_panel(symbols: list[str], start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    full_index = pd.date_range(start=start, end=end, freq="15min", tz="UTC")
    panel = pd.DataFrame(index=full_index)
    avail_rows = []
    for symbol in symbols:
        df = load_or_build_symbol(symbol, start, end)
        if not df.empty:
            s = df.set_index("timestamp")["close"].astype(float)
            panel[symbol] = s.reindex(full_index)
            avail_rows.append({
                "symbol": symbol,
                "first_bar_utc": to_iso(df["timestamp"].min()),
                "last_bar_utc": to_iso(df["timestamp"].max()),
                "bars": int(len(df)),
                "onboard_utc": to_iso(pd.to_datetime(SYMBOL_ONBOARD_DATE_MS[symbol], unit="ms", utc=True)),
            })
        else:
            panel[symbol] = np.nan
            avail_rows.append({
                "symbol": symbol,
                "first_bar_utc": "",
                "last_bar_utc": "",
                "bars": 0,
                "onboard_utc": to_iso(pd.to_datetime(SYMBOL_ONBOARD_DATE_MS[symbol], unit="ms", utc=True)),
            })
    return panel, pd.DataFrame(avail_rows)


def overall_metrics(net: pd.Series, gross: pd.Series, turnover: pd.Series) -> dict:
    return {
        "net_mean_bps": float(net.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + net).prod() - 1.0) * 100.0),
        "win_rate": float((net > 0).mean() * 100.0),
        "max_drawdown_pct": float(max_drawdown(net) * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "gross_mean_bps": float(gross.mean() * 10000.0),
    }


def run_asof_backtest(panel: pd.DataFrame, symbols: list[str]) -> pd.DataFrame:
    idx = panel.index
    rows = []
    i = FORMATION_BARS
    while i + HOLD_BARS < len(panel):
        ts = idx[i]
        exit_ts = idx[i + HOLD_BARS]

        eligible = []
        for sym in symbols:
            onboard = pd.to_datetime(SYMBOL_ONBOARD_DATE_MS[sym], unit="ms", utc=True)
            if ts < onboard:
                continue
            close_window = panel[sym].iloc[i - FORMATION_BARS:i + 1]
            if close_window.isna().any():
                continue
            if pd.isna(panel[sym].iat[i + HOLD_BARS]):
                continue
            eligible.append(sym)

        if len(eligible) < TOP_N + BOTTOM_N:
            i += 1
            continue

        close_window = panel[eligible].iloc[i - FORMATION_BARS:i + 1]
        hist = close_window.pct_change().iloc[1:]
        if hist.isna().any().any():
            i += 1
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

        long_price_contrib = 0.5 * long_ret
        plain_short_price_contrib = 0.5 * float(plain_short_series.mean())
        veto_short_price_contrib = 0.5 * float(veto_short_series.mean())

        rows.append({
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
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
            "long_price_contrib": float(long_price_contrib),
            "plain_short_price_contrib": float(plain_short_price_contrib),
            "veto_short_price_contrib": float(veto_short_price_contrib),
            "btc_cumret": float(cumret["BTCUSDT"]) if "BTCUSDT" in cumret.index else np.nan,
            "universe_cumret_mean": float(cumret.mean()),
            "universe_cumret_std": float(cumret.std()),
            "universe_cumret_iqr": float(cumret.quantile(0.75) - cumret.quantile(0.25)),
            "universe_realized_vol_median": float(hist.std().median()),
        })
        i += 1

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["timestamp"] = out["timestamp_ts"].map(to_iso)
    out["plain_net"] = out["plain_gross"] - out["plain_turnover_x"] * (COST_BPS / 10000.0)
    out["veto_net"] = out["veto_gross"] - out["veto_turnover_x"] * (COST_BPS / 10000.0)
    out["year"] = out["timestamp_ts"].dt.strftime("%Y")
    out["month"] = out["timestamp_ts"].dt.strftime("%Y-%m")
    return out


def grouped_year_metrics(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y, sub in detail.groupby("year"):
        rows.append({
            "year": y,
            "rebalances": int(len(sub)),
            "avg_universe_size": float(sub["eligible_universe_size"].mean()),
            "plain_net_mean_bps": float(sub["plain_net"].mean() * 10000.0),
            "plain_net_cum_pct": float(((1.0 + sub["plain_net"]).prod() - 1.0) * 100.0),
            "plain_win_rate": float((sub["plain_net"] > 0).mean() * 100.0),
            "plain_max_dd_pct": float(max_drawdown(sub["plain_net"]) * 100.0),
            "plain_avg_turnover_x": float(sub["plain_turnover_x"].mean()),
            "veto_net_mean_bps": float(sub["veto_net"].mean() * 10000.0),
            "veto_net_cum_pct": float(((1.0 + sub["veto_net"]).prod() - 1.0) * 100.0),
            "veto_win_rate": float((sub["veto_net"] > 0).mean() * 100.0),
            "veto_max_dd_pct": float(max_drawdown(sub["veto_net"]) * 100.0),
            "veto_avg_turnover_x": float(sub["veto_turnover_x"].mean()),
            "delta_net_mean_bps": float((sub["veto_net"] - sub["plain_net"]).mean() * 10000.0),
            "delta_net_cum_pct": float((((1.0 + sub["veto_net"]).prod() - 1.0) - (((1.0 + sub["plain_net"]).prod() - 1.0))) * 100.0),
        })
    return pd.DataFrame(rows)


def build_universe_timeline(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if detail.empty:
        return pd.DataFrame(), pd.DataFrame()

    timeline_rows = []
    prev = set()
    for row in detail.itertuples(index=False):
        cur = set(x for x in row.eligible_symbols.split(",") if x)
        timeline_rows.append({
            "timestamp": row.timestamp,
            "month": row.month,
            "universe_size": len(cur),
            "entered_names": len(cur - prev),
            "exited_names": len(prev - cur),
            "entered_symbols": ",".join(sorted(cur - prev)),
            "exited_symbols": ",".join(sorted(prev - cur)),
            "eligible_symbols": row.eligible_symbols,
        })
        prev = cur

    timeline = pd.DataFrame(timeline_rows)

    exploded = timeline.assign(symbol=timeline["eligible_symbols"].str.split(",")).explode("symbol")
    exploded = exploded[exploded["symbol"].astype(str) != ""]
    active = exploded.groupby("month")["symbol"].nunique().rename("active_symbols")

    monthly = timeline.groupby("month", as_index=False).agg(
        rebalances=("month", "size"),
        universe_size_mean=("universe_size", "mean"),
        universe_size_min=("universe_size", "min"),
        universe_size_max=("universe_size", "max"),
        entered_names_sum=("entered_names", "sum"),
        exited_names_sum=("exited_names", "sum"),
    )
    monthly = monthly.merge(active, on="month", how="left")
    return timeline, monthly


def window_metrics(detail: pd.DataFrame, w: WindowSpec) -> dict:
    end_ts = detail["timestamp_ts"].max()
    start_ts = detail["timestamp_ts"].min()
    req_start = end_ts - pd.Timedelta(days=w.days)
    if start_ts > req_start:
        return {
            "window": w.label,
            "available": False,
            "required_start_utc": to_iso(req_start),
            "available_start_utc": to_iso(start_ts),
            "reason": "insufficient as-of backtest span",
        }

    sub = detail[detail["timestamp_ts"] >= req_start].copy()
    return {
        "window": w.label,
        "available": True,
        "start_utc": to_iso(sub["timestamp_ts"].min()),
        "end_utc": to_iso(sub["timestamp_ts"].max()),
        "rebalances": int(len(sub)),
        "avg_universe_size": float(sub["eligible_universe_size"].mean()),
        "plain": overall_metrics(sub["plain_net"], sub["plain_gross"], sub["plain_turnover_x"]),
        "veto": overall_metrics(sub["veto_net"], sub["veto_gross"], sub["veto_turnover_x"]),
        "delta_net_mean_bps": float((sub["veto_net"] - sub["plain_net"]).mean() * 10000.0),
        "delta_net_cum_pct": float((((1.0 + sub["veto_net"]).prod() - 1.0) - (((1.0 + sub["plain_net"]).prod() - 1.0))) * 100.0),
    }


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None) -> str:
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    body = []
    for _, row in df.iterrows():
        cols = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in percent_cols:
                txt = fmt_pct(float(v))
            elif c in bps_cols:
                txt = fmt_bps(float(v))
            elif c in x_cols:
                txt = fmt_x(float(v))
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            cols.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cols) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    seed = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    symbols = seed["symbols"]

    now = pd.Timestamp.utcnow()
    now = now.tz_convert("UTC") if now.tzinfo else now.tz_localize("UTC")
    sample_end = now.floor("15min") - pd.Timedelta(minutes=15)

    lookback_buffer = pd.Timedelta(minutes=BAR_MINUTES * (FORMATION_BARS + HOLD_BARS + 8))
    target_start = (sample_end - pd.Timedelta(days=MAX_LOOKBACK_DAYS) - lookback_buffer).floor("15min")
    earliest_onboard = min(pd.to_datetime(v, unit="ms", utc=True) for v in SYMBOL_ONBOARD_DATE_MS.values())
    sample_start = max(target_start, (earliest_onboard - lookback_buffer).floor("15min"))

    panel, symbol_avail = build_panel(symbols, sample_start, sample_end)
    detail = run_asof_backtest(panel, symbols)
    if detail.empty:
        raise RuntimeError("as-of backtest returned empty detail")

    full_plain = overall_metrics(detail["plain_net"], detail["plain_gross"], detail["plain_turnover_x"])
    full_veto = overall_metrics(detail["veto_net"], detail["veto_gross"], detail["veto_turnover_x"])

    year_df = grouped_year_metrics(detail)
    timeline_df, universe_monthly_df = build_universe_timeline(detail)

    windows = [
        WindowSpec("1Y", 365),
        WindowSpec("2Y", 730),
        WindowSpec("3Y", 1095),
        WindowSpec("5Y", 1825),
        WindowSpec("6Y", 2190),
        WindowSpec("7Y", 2555),
        WindowSpec("8Y", 2920),
    ]
    window_reviews = [window_metrics(detail, w) for w in windows]

    windows_rows = []
    for w in window_reviews:
        if not w["available"]:
            windows_rows.append({
                "window": w["window"],
                "available": "no",
                "required_start_utc": w["required_start_utc"],
                "available_start_utc": w["available_start_utc"],
                "rebalances": np.nan,
                "avg_universe_size": np.nan,
                "plain_net_mean_bps": np.nan,
                "plain_net_cum_pct": np.nan,
                "veto_net_mean_bps": np.nan,
                "veto_net_cum_pct": np.nan,
                "delta_net_mean_bps": np.nan,
                "delta_net_cum_pct": np.nan,
                "note": w["reason"],
            })
        else:
            windows_rows.append({
                "window": w["window"],
                "available": "yes",
                "required_start_utc": w["start_utc"],
                "available_start_utc": w["start_utc"],
                "rebalances": w["rebalances"],
                "avg_universe_size": w["avg_universe_size"],
                "plain_net_mean_bps": w["plain"]["net_mean_bps"],
                "plain_net_cum_pct": w["plain"]["net_cum_pct"],
                "veto_net_mean_bps": w["veto"]["net_mean_bps"],
                "veto_net_cum_pct": w["veto"]["net_cum_pct"],
                "delta_net_mean_bps": w["delta_net_mean_bps"],
                "delta_net_cum_pct": w["delta_net_cum_pct"],
                "note": "",
            })
    windows_df = pd.DataFrame(windows_rows)

    all_available = all(bool(w.get("available")) for w in window_reviews)
    available_deltas = [float(w.get("delta_net_mean_bps", 0.0)) for w in window_reviews if w.get("available")]

    long_windows = [w for w in window_reviews if w["window"] in {"5Y", "6Y", "7Y", "8Y"}]
    long_available = [w for w in long_windows if w.get("available")]

    if long_available:
        if all(float(w.get("delta_net_mean_bps", 0.0)) > 0 for w in long_available):
            final_verdict = (
                "as-of universe 长历史线已向 5~8Y 扩展到可用范围；其中可用长窗里 veto 相对 baseline 仍维持正增量。"
                "但未覆盖到的更长窗口仍应明确标 unavailable，不能超范围宣称。"
            )
        else:
            final_verdict = (
                "as-of universe 长历史线已向 5~8Y 扩展，但在可用长窗中 veto 并非一致优于 baseline；"
                "结论应保持为“窗口分化”，不能表述成全长窗通过。"
            )
    else:
        final_verdict = "as-of universe 在当前可得数据下尚无 5~8Y 可用窗口，当前仅能给出较短窗口结论。"

    review = {
        "scope": "as-of listed universe only; keep spec frozen except universe membership being historical-time-aware",
        "requested_long_windows": ["5Y", "6Y", "7Y", "8Y"],
        "long_window_availability": {
            w["window"]: bool(w.get("available")) for w in window_reviews if w["window"] in {"5Y", "6Y", "7Y", "8Y"}
        },
        "frozen_spec": {
            "variant_anchor": VARIANT,
            "bar": "15m",
            "formation_bars": FORMATION_BARS,
            "hold_bars": HOLD_BARS,
            "top_n": TOP_N,
            "bottom_n": BOTTOM_N,
            "veto_floor_pct": VETO_FLOOR * 100.0,
            "veto_mult_x_median": VETO_MULT,
            "cost_bps_per_turnover_x": COST_BPS,
        },
        "sample": {
            "start_utc": to_iso(detail["timestamp_ts"].min()),
            "end_utc": to_iso(detail["timestamp_ts"].max()),
            "calendar_days": float((detail["timestamp_ts"].max() - detail["timestamp_ts"].min()) / pd.Timedelta(days=1)),
            "rebalances": int(len(detail)),
            "avg_eligible_universe_size": float(detail["eligible_universe_size"].mean()),
            "min_eligible_universe_size": int(detail["eligible_universe_size"].min()),
            "max_eligible_universe_size": int(detail["eligible_universe_size"].max()),
        },
        "full_available_history": {
            "plain": full_plain,
            "veto": full_veto,
            "delta": {
                "net_mean_bps": full_veto["net_mean_bps"] - full_plain["net_mean_bps"],
                "net_cum_pct": full_veto["net_cum_pct"] - full_plain["net_cum_pct"],
                "max_drawdown_reduction_pct_points": abs(full_plain["max_drawdown_pct"]) - abs(full_veto["max_drawdown_pct"]),
                "avg_turnover_x": full_veto["avg_turnover_x"] - full_plain["avg_turnover_x"],
            },
        },
        "window_reviews": window_reviews,
        "final_verdict": final_verdict,
    }

    detail.to_csv(ART_DIR / "rank213_asof_universe_long_history_detail.csv", index=False)
    year_df.to_csv(ART_DIR / "rank213_asof_universe_long_history_yearly.csv", index=False)
    windows_df.to_csv(ART_DIR / "rank213_asof_universe_long_history_windows.csv", index=False)
    timeline_df.to_csv(ART_DIR / "rank213_asof_universe_timeline.csv", index=False)
    universe_monthly_df.to_csv(ART_DIR / "rank213_asof_universe_monthly.csv", index=False)
    symbol_avail.to_csv(ART_DIR / "rank213_asof_universe_symbol_availability.csv", index=False)
    (ART_DIR / "rank213_asof_universe_long_history_review_summary.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    yearly_table = render_table(
        year_df,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct", "delta_net_cum_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x", "avg_universe_size"},
    )
    windows_table = render_table(
        windows_df,
        percent_cols={"plain_net_cum_pct", "veto_net_cum_pct", "delta_net_cum_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
        x_cols={"avg_universe_size"},
    )
    universe_monthly_table = render_table(
        universe_monthly_df,
        x_cols={"universe_size_mean"},
    )

    timeline_head = timeline_df.head(6).copy()
    timeline_tail = timeline_df.tail(6).copy()

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
<meta charset='utf-8' />
<meta name='viewport' content='width=device-width, initial-scale=1' />
<title>Rank213 as-of universe long history review</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--warn:#9a3412;--warnbg:#ffedd5;--ok:#166534;--okbg:#dcfce7;--info:#1d4ed8;--infobg:#dbeafe}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}}
.wrap{{max-width:1160px;margin:0 auto;padding:28px 18px 64px}} .card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:14px}}
h1,h2{{margin:0 0 12px}} .muted{{color:var(--muted)}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
.metric{{border:1px solid var(--line);border-radius:12px;padding:12px 14px}} .metric .k{{color:var(--muted);font-size:13px}} .metric .v{{font-size:24px;font-weight:700}}
.note{{border-left:4px solid var(--info);background:var(--infobg);padding:12px 14px;border-radius:10px;white-space:pre-wrap}} .warn{{border-left-color:var(--warn);background:var(--warnbg)}} .ok{{border-left-color:var(--ok);background:var(--okbg)}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}} th{{background:#f8fafc}}
a{{color:#0f766e;text-decoration:none}} a:hover{{text-decoration:underline}}
</style>
</head>
<body><div class='wrap'>
<div class='card'>
<h1>Rank213 as-of universe long history review</h1>
<p><strong>目标：</strong>补一条“历史时点真实 universe”验证线，不替换 frozen universe 线。</p>
<p class='muted'>规则冻结：<code>15m / 64 / 12 / top3-bottom3 / max(1.5%,2×median) / 4bps×turnover</code>；唯一变化是 universe membership 按历史时点可用性动态决定。</p>
<div class='note warn'><b>证据等级提醒：</b>本页只解决“币未上线时不能提前参赛”的 onboard-time 可见性问题；它不是 monthly/quarterly rolling Top30 选池回测。历史滚动选池讨论默认看 <a href='/momentum/paper/rank213_evidence_map.html'>evidence_map</a> 与 <a href='/momentum/paper/rank213_largecap_xs_jump_veto_monthly_volume_universe_rebuild.html'>monthly_volume_universe_rebuild</a>。</div>
<p><a href='/momentum/paper/rank213_largecap_xs_jump_veto.html'>runner 页面</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review.html'>frozen universe long-history</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_long_history_review_with_funding.html'>funding long-history</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html'>ffill impact audit</a> · <a href='/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html'>regime_review</a></p>
</div>

<div class='card'>
<h2>1) 样本与 baseline vs veto（as-of universe）</h2>
<div class='grid'>
<div class='metric'><div class='k'>start</div><div class='v' style='font-size:18px'>{review['sample']['start_utc']}</div></div>
<div class='metric'><div class='k'>end</div><div class='v' style='font-size:18px'>{review['sample']['end_utc']}</div></div>
<div class='metric'><div class='k'>calendar days</div><div class='v'>{review['sample']['calendar_days']:.2f}d</div></div>
<div class='metric'><div class='k'>rebalances</div><div class='v'>{review['sample']['rebalances']}</div></div>
<div class='metric'><div class='k'>avg universe size</div><div class='v'>{review['sample']['avg_eligible_universe_size']:.2f}</div></div>
<div class='metric'><div class='k'>universe size range</div><div class='v'>{review['sample']['min_eligible_universe_size']}~{review['sample']['max_eligible_universe_size']}</div></div>
</div>
<div class='grid' style='margin-top:12px'>
<div class='metric'><div class='k'>plain net mean</div><div class='v'>{fmt_bps(review['full_available_history']['plain']['net_mean_bps'])}</div></div>
<div class='metric'><div class='k'>plain net cumulative</div><div class='v'>{fmt_pct(review['full_available_history']['plain']['net_cum_pct'])}</div></div>
<div class='metric'><div class='k'>veto net mean</div><div class='v'>{fmt_bps(review['full_available_history']['veto']['net_mean_bps'])}</div></div>
<div class='metric'><div class='k'>veto net cumulative</div><div class='v'>{fmt_pct(review['full_available_history']['veto']['net_cum_pct'])}</div></div>
<div class='metric'><div class='k'>Δ net mean</div><div class='v'>{fmt_bps(review['full_available_history']['delta']['net_mean_bps'])}</div></div>
<div class='metric'><div class='k'>Δ net cumulative</div><div class='v'>{fmt_pct(review['full_available_history']['delta']['net_cum_pct'])}</div></div>
</div>
</div>

<div class='card'>
<h2>2) 1Y / 2Y / 3Y / 5Y / 6Y / 7Y / 8Y 可用性与同口径结果</h2>
{windows_table}
</div>

<div class='card'>
<h2>3) 按年表现（as-of universe）</h2>
{yearly_table}
</div>

<div class='card'>
<h2>4) universe 随时间变化</h2>
{universe_monthly_table}
<p class='muted'>首尾 6 笔 rebalance 的 universe 变化快照（entered / exited）：</p>
<h3>Head</h3>
{render_table(timeline_head)}
<h3>Tail</h3>
{render_table(timeline_tail)}
</div>

<div class='card'>
<h2>5) 最终结论</h2>
<div class='note {'ok' if all_available else 'warn'}'><b>{review['final_verdict']}</b></div>
</div>
</div></body></html>
"""

    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str((ART_DIR / "rank213_asof_universe_long_history_review_summary.json").relative_to(ROOT)),
        "detail_csv": str((ART_DIR / "rank213_asof_universe_long_history_detail.csv").relative_to(ROOT)),
        "yearly_csv": str((ART_DIR / "rank213_asof_universe_long_history_yearly.csv").relative_to(ROOT)),
        "windows_csv": str((ART_DIR / "rank213_asof_universe_long_history_windows.csv").relative_to(ROOT)),
        "universe_monthly_csv": str((ART_DIR / "rank213_asof_universe_monthly.csv").relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
