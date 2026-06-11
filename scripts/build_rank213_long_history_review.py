#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import time
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_long_history_review.html"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
BASE_API_URL = "https://fapi.binance.com/fapi/v1/klines"
DATA_VISION_MONTHLY = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{ym}.zip"
DATA_VISION_DAILY = "https://data.binance.vision/data/futures/um/daily/klines/{symbol}/15m/{symbol}-15m-{ymd}.zip"
INTERVAL = "15m"
LIMIT = 1500
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


def to_iso(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def month_range(start: pd.Timestamp, end: pd.Timestamp) -> list[str]:
    months = []
    cur = pd.Timestamp(start.year, start.month, 1, tz="UTC")
    end_month = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    while cur <= end_month:
        months.append(cur.strftime("%Y-%m"))
        cur = cur + pd.offsets.MonthBegin(1)
    return months


def read_monthly_zip(symbol: str, ym: str) -> pd.DataFrame:
    url = DATA_VISION_MONTHLY.format(symbol=symbol, ym=ym)
    with urllib.request.urlopen(url, timeout=60) as resp:
        blob = resp.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            raise RuntimeError(f"empty zip for {symbol} {ym}")
        with zf.open(members[0]) as fh:
            df = pd.read_csv(
                fh,
                header=None,
                names=[
                    "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
                    "trade_count", "taker_base", "taker_quote", "ignore"
                ],
            )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df[df["open_time"].notna()].copy()
    df["timestamp"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df[df["close"].notna()].copy()
    return df[["timestamp", "close"]].drop_duplicates("timestamp").sort_values("timestamp")


def read_daily_zip(symbol: str, ymd: str) -> pd.DataFrame:
    url = DATA_VISION_DAILY.format(symbol=symbol, ymd=ymd)
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            blob = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return pd.DataFrame(columns=["timestamp", "close"])
        raise
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        members = zf.namelist()
        if not members:
            return pd.DataFrame(columns=["timestamp", "close"])
        with zf.open(members[0]) as fh:
            df = pd.read_csv(
                fh,
                header=None,
                names=[
                    "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
                    "trade_count", "taker_base", "taker_quote", "ignore"
                ],
            )
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    df = df[df["open_time"].notna()].copy()
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True)
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df[df["close"].notna()].copy()
    return df[["timestamp", "close"]].drop_duplicates("timestamp").sort_values("timestamp")


def fetch_symbol_long_history(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    months = month_range(start, end)
    parts: list[pd.DataFrame] = []
    current_month = end.strftime("%Y-%m")
    for ym in months:
        if ym == current_month:
            continue
        month_start = pd.Timestamp(f"{ym}-01", tz="UTC")
        if month_start < start.normalize() - pd.Timedelta(days=31):
            continue
        part = read_monthly_zip(symbol, ym)
        parts.append(part)
        time.sleep(0.03)
    current_month_start = pd.Timestamp(end.year, end.month, 1, tz="UTC")
    cur_day = current_month_start
    while cur_day <= end.normalize():
        daily = read_daily_zip(symbol, cur_day.strftime("%Y-%m-%d"))
        if not daily.empty:
            parts.append(daily)
        cur_day += pd.Timedelta(days=1)
        time.sleep(0.01)
    if not parts:
        raise RuntimeError(f"no history for {symbol}")
    df = pd.concat(parts, ignore_index=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp")
    df = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].reset_index(drop=True)
    return df


def build_close_panel(symbols: list[str], start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = []
    availability_rows = []
    for symbol in symbols:
        df = fetch_symbol_long_history(symbol, start, end)
        if df.empty:
            raise RuntimeError(f"empty history for {symbol}")
        availability_rows.append({
            "symbol": symbol,
            "first_bar_utc": to_iso(df["timestamp"].min()),
            "last_bar_utc": to_iso(df["timestamp"].max()),
            "bars": int(len(df)),
        })
        s = df.rename(columns={"close": symbol}).set_index("timestamp")[[symbol]]
        frames.append(s)
    panel = frames[0]
    for s in frames[1:]:
        panel = panel.join(s, how="outer")
    panel = panel.sort_index().ffill().dropna()
    return panel, pd.DataFrame(availability_rows)


def overall_metrics(gross: pd.Series, net: pd.Series, turnover: pd.Series) -> dict:
    return {
        "gross_mean_bps": float(gross.mean() * 10000.0),
        "gross_cum_pct": float(((1.0 + gross).prod() - 1.0) * 100.0),
        "net_mean_bps": float(net.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + net).prod() - 1.0) * 100.0),
        "win_rate": float((net > 0).mean() * 100.0),
        "avg_turnover_x": float(turnover.mean()),
        "max_drawdown_pct": float(max_drawdown(net) * 100.0),
        "worst_net_bps": float(net.min() * 10000.0),
        "p5_net_bps": float(np.percentile(net, 5) * 10000.0),
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


def grouped_metrics(detail: pd.DataFrame, key: str) -> pd.DataFrame:
    rows = []
    for k, sub in detail.groupby(key):
        rows.append({
            key: k,
            "rebalances": int(len(sub)),
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
        })
    return pd.DataFrame(rows)


def year_short_leg_effect(detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y, sub in detail.groupby("year"):
        rows.append({
            "year": y,
            "rebalances": int(len(sub)),
            "plain_short_leg_mean_gross_bps": float(sub["plain_short_contrib"].mean() * 10000.0),
            "veto_short_leg_mean_gross_bps": float(sub["veto_short_contrib"].mean() * 10000.0),
            "delta_short_leg_bps": float((sub["veto_short_contrib"] - sub["plain_short_contrib"]).mean() * 10000.0),
            "plain_avg_turnover_x": float(sub["plain_turnover_x"].mean()),
            "veto_avg_turnover_x": float(sub["veto_turnover_x"].mean()),
            "delta_turnover_x": float((sub["veto_turnover_x"] - sub["plain_turnover_x"]).mean()),
            "pct_rebalances_with_any_veto": float((sub["veto_count"] > 0).mean() * 100.0),
        })
    return pd.DataFrame(rows)


def window_metrics(detail: pd.DataFrame, label: str, days: int, end_ts: pd.Timestamp, available_start: pd.Timestamp) -> dict:
    required_start = end_ts - pd.Timedelta(days=days)
    if required_start < available_start:
        return {
            "window": label,
            "available": False,
            "required_start_utc": to_iso(required_start),
            "available_start_utc": to_iso(available_start),
            "reason": "common-history shorter than requested window under frozen universe",
        }
    sub = detail[detail["timestamp_ts"] >= required_start].copy()
    return {
        "window": label,
        "available": True,
        "start_utc": to_iso(sub["timestamp_ts"].min()),
        "end_utc": to_iso(sub["timestamp_ts"].max()),
        "rebalances": int(len(sub)),
        "plain": overall_metrics(sub["plain_gross"], sub["plain_net"], sub["plain_turnover_x"]),
        "veto": overall_metrics(sub["veto_gross"], sub["veto_net"], sub["veto_turnover_x"]),
        "delta_net_mean_bps": float((sub["veto_net"] - sub["plain_net"]).mean() * 10000.0),
        "delta_net_cum_pct": float((((1.0 + sub["veto_net"]).prod() - 1.0) - (((1.0 + sub["plain_net"]).prod() - 1.0))) * 100.0),
    }


def run_backtest(panel: pd.DataFrame) -> pd.DataFrame:
    ret = panel.pct_change()
    rows = []
    i = FORMATION_BARS
    while i + HOLD_BARS < len(panel):
        ts = panel.index[i]
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

        exit_ts = panel.index[i + HOLD_BARS]
        future = panel.iloc[i + HOLD_BARS] / panel.iloc[i] - 1.0
        long_ret = float(future[longs].mean())
        plain_short_series = -future[plain_shorts]
        veto_short_series = -future[veto_shorts]
        plain_gross = 0.5 * long_ret + 0.5 * float(plain_short_series.mean())
        veto_gross = 0.5 * long_ret + 0.5 * float(veto_short_series.mean())
        rows.append({
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
            "plain_gross": plain_gross,
            "veto_gross": veto_gross,
            "plain_turnover_x": 1.0,
            "veto_turnover_x": 1.0 + (len(set(veto_shorts) ^ set(plain_shorts)) / 6.0),
            "veto_count": len(vetoed),
            "veto_threshold": veto_threshold,
            "plain_longs": ",".join(longs),
            "plain_shorts": ",".join(plain_shorts),
            "veto_shorts": ",".join(veto_shorts),
            "long_contrib": 0.5 * long_ret,
            "plain_short_contrib": 0.5 * float(plain_short_series.mean()),
            "veto_short_contrib": 0.5 * float(veto_short_series.mean()),
        })
        i += HOLD_BARS
    out = pd.DataFrame(rows)
    out["timestamp"] = out["timestamp_ts"].map(to_iso)
    out["plain_net"] = out["plain_gross"] - out["plain_turnover_x"] * (COST_BPS / 10000.0)
    out["veto_net"] = out["veto_gross"] - out["veto_turnover_x"] * (COST_BPS / 10000.0)
    out["month"] = out["timestamp_ts"].dt.strftime("%Y-%m")
    out["quarter"] = out["timestamp_ts"].dt.to_period("Q").astype(str)
    out["year"] = out["timestamp_ts"].dt.strftime("%Y")
    return out


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    seed_summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    symbols = seed_summary["symbols"]

    availability_seed = []
    onboard_dates = []
    for s in symbols:
        onboard_ms = SYMBOL_ONBOARD_DATE_MS[s]
        onboard = pd.to_datetime(onboard_ms, unit="ms", utc=True)
        onboard_dates.append(onboard)
        availability_seed.append({
            "symbol": s,
            "onboard_date_utc": to_iso(onboard),
            "source": "cached_exchangeInfo_snapshot_2026-04-11",
        })
    availability_seed_df = pd.DataFrame(availability_seed).sort_values("onboard_date_utc", ascending=False)
    common_start_candidate = max(onboard_dates)

    now = pd.Timestamp.utcnow()
    now = now.tz_convert("UTC") if now.tzinfo else now.tz_localize("UTC")
    sample_end = now.floor("15min") - pd.Timedelta(minutes=15)

    panel, symbol_bar_availability = build_close_panel(symbols, common_start_candidate, sample_end)
    actual_start = panel.index.min()
    actual_end = panel.index.max()

    detail = run_backtest(panel)
    veto_events = detail[detail["veto_count"] > 0].copy()

    hit_names = 0
    false_kill_names = 0
    neutral_names = 0
    total_vetoed_names = 0
    for row in detail.itertuples(index=False):
        future = panel.loc[row.exit_ts] / panel.loc[row.timestamp_ts] - 1.0
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

    full_plain = overall_metrics(detail["plain_gross"], detail["plain_net"], detail["plain_turnover_x"])
    full_veto = overall_metrics(detail["veto_gross"], detail["veto_net"], detail["veto_turnover_x"])
    monthly = grouped_metrics(detail, "month")
    quarterly = grouped_metrics(detail, "quarter")
    yearly = grouped_metrics(detail, "year")
    year_leg = year_short_leg_effect(detail)

    split = np.array_split(detail.reset_index(drop=True), 2)
    half_split = []
    for idx, sub in enumerate(split, start=1):
        half_split.append({
            "half": idx,
            "start_utc": sub["timestamp"].iloc[0],
            "end_utc": sub["timestamp"].iloc[-1],
            "rebalances": int(len(sub)),
            "plain_net_mean_bps": float(sub["plain_net"].mean() * 10000.0),
            "plain_net_cum_pct": float(((1.0 + sub["plain_net"]).prod() - 1.0) * 100.0),
            "veto_net_mean_bps": float(sub["veto_net"].mean() * 10000.0),
            "veto_net_cum_pct": float(((1.0 + sub["veto_net"]).prod() - 1.0) * 100.0),
            "delta_net_mean_bps": float((sub["veto_net"] - sub["plain_net"]).mean() * 10000.0),
            "delta_net_cum_pct": float((((1.0 + sub["veto_net"]).prod() - 1.0) - (((1.0 + sub["plain_net"]).prod() - 1.0))) * 100.0),
        })

    windows = [WindowSpec("1Y", 365), WindowSpec("2Y", 730), WindowSpec("3Y", 1095)]
    window_reviews = [window_metrics(detail, w.label, w.days, actual_end, actual_start) for w in windows]

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
            "requested_goal": "validate 1Y/2Y/3Y under frozen current universe/spec without retuning",
            "common_start_candidate_utc": to_iso(common_start_candidate),
            "actual_common_start_utc": to_iso(actual_start),
            "actual_common_end_utc": to_iso(actual_end),
            "bars": int(len(panel)),
            "calendar_days": float((actual_end - actual_start) / pd.Timedelta(days=1)),
            "rebalances": int(len(detail)),
            "limiting_symbols": availability_seed_df.head(5).to_dict("records"),
        },
        "full_available_history": {
            "plain": full_plain,
            "veto": full_veto,
            "delta": {
                "gross_mean_bps": full_veto["gross_mean_bps"] - full_plain["gross_mean_bps"],
                "net_mean_bps": full_veto["net_mean_bps"] - full_plain["net_mean_bps"],
                "net_cum_pct": full_veto["net_cum_pct"] - full_plain["net_cum_pct"],
                "win_rate_pct_points": full_veto["win_rate"] - full_plain["win_rate"],
                "avg_turnover_x": full_veto["avg_turnover_x"] - full_plain["avg_turnover_x"],
                "max_drawdown_reduction_pct_points": abs(full_plain["max_drawdown_pct"]) - abs(full_veto["max_drawdown_pct"]),
            },
        },
        "window_reviews": window_reviews,
        "half_split": half_split,
        "leg_contribution": {
            "long_leg_mean_gross_bps": float(detail["long_contrib"].mean() * 10000.0),
            "plain_short_leg_mean_gross_bps": float(detail["plain_short_contrib"].mean() * 10000.0),
            "veto_short_leg_mean_gross_bps": float(detail["veto_short_contrib"].mean() * 10000.0),
            "long_leg_sum_pct_points": float(detail["long_contrib"].sum() * 100.0),
            "plain_short_leg_sum_pct_points": float(detail["plain_short_contrib"].sum() * 100.0),
            "veto_short_leg_sum_pct_points": float(detail["veto_short_contrib"].sum() * 100.0),
        },
        "veto_effectiveness": {
            "pct_rebalances_with_any_veto": float((detail["veto_count"] > 0).mean() * 100.0),
            "avg_veto_count_per_rebalance": float(detail["veto_count"].mean()),
            "rebalance_count_with_any_veto": int(len(veto_events)),
            "total_vetoed_names": int(total_vetoed_names),
            "name_level_hit_rate": float(hit_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
            "name_level_false_kill_rate": float(false_kill_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
            "name_level_neutral_rate": float(neutral_names / total_vetoed_names * 100.0) if total_vetoed_names else None,
            "rebalance_level_outperform_rate_given_any_veto": float(veto_events.apply(lambda r: r["veto_gross"] > r["plain_gross"], axis=1).mean() * 100.0) if len(veto_events) else None,
            "rebalance_level_underperform_rate_given_any_veto": float(veto_events.apply(lambda r: r["veto_gross"] < r["plain_gross"], axis=1).mean() * 100.0) if len(veto_events) else None,
        },
    }

    if review["data_availability"]["calendar_days"] < 365:
        verdict = (
            "在严格冻结当前 universe/spec 的前提下，公共共同历史仅能回到 "
            f"{review['data_availability']['actual_common_start_utc']}，不足 1Y；因此本轮不能把 Rank213 宣称为已通过 1Y/2Y/3Y 长历史验证。"
            "当前 keep/live 只能继续依赖原 admission seed 证据；这次 long-history check 的作用是确认在最大可用共同历史上同口径表现如何，而不是升级为更长历史已证实。"
        )
    else:
        delta = review["full_available_history"]["delta"]["net_mean_bps"]
        if delta > 0:
            verdict = (
                "在冻结当前 universe/spec 的最长可用共同历史上，veto 相对 baseline 仍保持正增量；因此当前 keep/live 不被长历史同口径验证直接推翻。"
            )
        else:
            verdict = (
                "在冻结当前 universe/spec 的最长可用共同历史上，veto 相对 baseline 未维持正增量；因此当前 keep/live 不能再被表述为已获同口径长历史支持。"
            )
    review["final_verdict"] = verdict

    availability_seed_df.to_csv(ART_DIR / "rank213_long_history_universe_availability.csv", index=False)
    symbol_bar_availability.to_csv(ART_DIR / "rank213_long_history_symbol_bar_availability.csv", index=False)
    detail.to_csv(ART_DIR / "rank213_long_history_detail.csv", index=False)
    monthly.to_csv(ART_DIR / "rank213_long_history_monthly.csv", index=False)
    quarterly.to_csv(ART_DIR / "rank213_long_history_quarterly.csv", index=False)
    yearly.to_csv(ART_DIR / "rank213_long_history_yearly.csv", index=False)
    year_leg.to_csv(ART_DIR / "rank213_long_history_year_leg_effect.csv", index=False)
    (ART_DIR / "rank213_long_history_review_summary.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    windows_rows = []
    for w in window_reviews:
        if not w["available"]:
            windows_rows.append({
                "window": w["window"],
                "available": "no",
                "required_start_utc": w["required_start_utc"],
                "available_start_utc": w["available_start_utc"],
                "plain_net_mean_bps": np.nan,
                "plain_net_cum_pct": np.nan,
                "plain_win_rate": np.nan,
                "plain_max_dd_pct": np.nan,
                "plain_avg_turnover_x": np.nan,
                "veto_net_mean_bps": np.nan,
                "veto_net_cum_pct": np.nan,
                "veto_win_rate": np.nan,
                "veto_max_dd_pct": np.nan,
                "veto_avg_turnover_x": np.nan,
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
                "plain_net_mean_bps": w["plain"]["net_mean_bps"],
                "plain_net_cum_pct": w["plain"]["net_cum_pct"],
                "plain_win_rate": w["plain"]["win_rate"],
                "plain_max_dd_pct": w["plain"]["max_drawdown_pct"],
                "plain_avg_turnover_x": w["plain"]["avg_turnover_x"],
                "veto_net_mean_bps": w["veto"]["net_mean_bps"],
                "veto_net_cum_pct": w["veto"]["net_cum_pct"],
                "veto_win_rate": w["veto"]["win_rate"],
                "veto_max_dd_pct": w["veto"]["max_drawdown_pct"],
                "veto_avg_turnover_x": w["veto"]["avg_turnover_x"],
                "delta_net_mean_bps": w["delta_net_mean_bps"],
                "delta_net_cum_pct": w["delta_net_cum_pct"],
                "note": "",
            })
    windows_df = pd.DataFrame(windows_rows)

    monthly_table = render_table(
        monthly,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"},
    )
    quarterly_table = render_table(
        quarterly,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"},
    )
    yearly_table = render_table(
        yearly,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"},
    )
    windows_table = render_table(
        windows_df,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct", "delta_net_cum_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x"},
    )
    year_leg_table = render_table(
        year_leg,
        percent_cols={"pct_rebalances_with_any_veto"},
        bps_cols={"plain_short_leg_mean_gross_bps", "veto_short_leg_mean_gross_bps", "delta_short_leg_bps"},
        x_cols={"plain_avg_turnover_x", "veto_avg_turnover_x", "delta_turnover_x"},
    )
    half_df = pd.DataFrame(half_split)
    half_table = render_table(
        half_df,
        percent_cols={"plain_net_cum_pct", "veto_net_cum_pct", "delta_net_cum_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps", "delta_net_mean_bps"},
    )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 213 long history review（frozen spec）</title>
  <style>
    :root {{
      --bg:#f8fafc; --card:#ffffff; --fg:#0f172a; --muted:#64748b; --line:#e2e8f0;
      --good:#166534; --good-bg:#dcfce7; --warn:#9a3412; --warn-bg:#ffedd5; --info:#1d4ed8; --info-bg:#dbeafe;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .wrap {{ max-width:1120px; margin:0 auto; padding:28px 18px 64px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:14px; }}
    h1,h2,h3 {{ margin:0 0 12px; line-height:1.35; }}
    h1 {{ font-size:28px; }}
    h2 {{ font-size:20px; margin-top:4px; }}
    p, li {{ margin:0 0 8px; }}
    ul {{ margin:0; padding-left:20px; }}
    code {{ background:#eff6ff; border-radius:6px; padding:2px 6px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; }}
    .muted {{ color:var(--muted); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; }}
    .metric {{ border:1px solid var(--line); border-radius:12px; padding:12px 14px; background:#fff; }}
    .metric .k {{ color:var(--muted); font-size:13px; margin-bottom:4px; }}
    .metric .v {{ font-size:24px; font-weight:700; }}
    .note {{ border-left:4px solid var(--info); background:var(--info-bg); padding:12px 14px; border-radius:10px; white-space:pre-wrap; }}
    .warn {{ border-left-color:var(--warn); background:var(--warn-bg); }}
    .good {{ border-left-color:var(--good); background:var(--good-bg); }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
    th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    .mono {{ white-space:pre-wrap; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; background:#f8fafc; border:1px solid var(--line); border-radius:10px; padding:12px; }}
    a {{ color:#0f766e; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Rank 213 long history review（frozen spec）</h1>
      <p><strong>对象：</strong><code>Rank 213 / large-cap XS momentum × short-leg jump veto</code></p>
      <p><strong>页面目标：</strong>严格冻结当前 spec，不改 universe / formation / hold / topN / bottomN / veto / cost，只回答长历史同口径验证。</p>
      <p class="muted">同口径锚点：<code>{SUMMARY_PATH.relative_to(ROOT)}</code>；当前 frozen spec：<code>{VARIANT}</code> / <code>15m</code> / <code>64</code> / <code>12</code> / <code>top3-bottom3</code> / <code>max(1.5%, 2.0×median)</code> / <code>4bps×turnover_x</code></p>
      <p><a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">当前 runner 页面</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_spec.html">最小可复现 spec</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_performance_review.html">短样本 performance review</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_honesty_audit.html">honesty_audit</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_ffill_impact_audit.html">ffill_impact_audit</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_readiness_note.html">readiness_note</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_asof_universe_long_history_review.html">asof_universe_long_history_review</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_regime_review.html">regime_review</a></p>
    </div>

    <div class="card">
      <h2>1) 回测区间与数据可用性</h2>
      <div class="grid">
        <div class="metric"><div class="k">common start candidate（latest onboard）</div><div class="v" style="font-size:18px">{review['data_availability']['common_start_candidate_utc']}</div></div>
        <div class="metric"><div class="k">actual common start</div><div class="v" style="font-size:18px">{review['data_availability']['actual_common_start_utc']}</div></div>
        <div class="metric"><div class="k">actual common end</div><div class="v" style="font-size:18px">{review['data_availability']['actual_common_end_utc']}</div></div>
        <div class="metric"><div class="k">bars</div><div class="v">{review['data_availability']['bars']}</div></div>
        <div class="metric"><div class="k">calendar days</div><div class="v">{review['data_availability']['calendar_days']:.2f}d</div></div>
        <div class="metric"><div class="k">rebalances</div><div class="v">{review['data_availability']['rebalances']}</div></div>
      </div>
      <div class="note warn">这页先回答最重要的 honesty 问题：在<strong>不改当前 30 币 universe</strong> 的前提下，公共共同历史被最新上市的成员截断；因此这次 long-history review 的上限由 universe 数据可用性决定，不是我自由挑窗口。</div>
      <p><strong>限制共同历史的最新上市成员（前 5）</strong></p>
      {render_table(availability_seed_df.head(5))}
    </div>

    <div class="card">
      <h2>2) plain baseline 与 veto 版：full available history</h2>
      <div class="grid">
        <div class="metric"><div class="k">plain net mean</div><div class="v">{fmt_bps(review['full_available_history']['plain']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">plain net cumulative</div><div class="v">{fmt_pct(review['full_available_history']['plain']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">plain win rate</div><div class="v">{fmt_pct(review['full_available_history']['plain']['win_rate'])}</div></div>
        <div class="metric"><div class="k">plain max drawdown</div><div class="v">{fmt_pct(review['full_available_history']['plain']['max_drawdown_pct'])}</div></div>
        <div class="metric"><div class="k">plain avg turnover</div><div class="v">{fmt_x(review['full_available_history']['plain']['avg_turnover_x'])}</div></div>
      </div>
      <div class="grid" style="margin-top:12px">
        <div class="metric"><div class="k">veto net mean</div><div class="v">{fmt_bps(review['full_available_history']['veto']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">veto net cumulative</div><div class="v">{fmt_pct(review['full_available_history']['veto']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">veto win rate</div><div class="v">{fmt_pct(review['full_available_history']['veto']['win_rate'])}</div></div>
        <div class="metric"><div class="k">veto max drawdown</div><div class="v">{fmt_pct(review['full_available_history']['veto']['max_drawdown_pct'])}</div></div>
        <div class="metric"><div class="k">veto avg turnover</div><div class="v">{fmt_x(review['full_available_history']['veto']['avg_turnover_x'])}</div></div>
      </div>
      <p class="muted">直接回答“长历史下有多强”：看的是这里这组 <strong>full available history</strong> 指标；如果 1Y/2Y/3Y 不可用，就不能把下面的 full-history 数字偷换成 1Y/2Y/3Y 结论。</p>
    </div>

    <div class="card">
      <h2>3) 1Y / 2Y / 3Y 冻结窗口验证</h2>
      {windows_table}
      <div class="note">这一节严格回答：在当前 frozen universe/spec 下，<strong>1Y / 2Y / 3Y 到底能不能测</strong>。不可用就直接记 <code>no</code>，不为了凑长度改 universe 或重调参数。</div>
    </div>

    <div class="card">
      <h2>4) baseline vs veto 的增量是否稳定</h2>
      <div class="grid">
        <div class="metric"><div class="k">Δ net mean（full history）</div><div class="v">{fmt_bps(review['full_available_history']['delta']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">Δ net cumulative</div><div class="v">{fmt_pct(review['full_available_history']['delta']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">Δ win rate</div><div class="v">{fmt_pct(review['full_available_history']['delta']['win_rate_pct_points'])}</div></div>
        <div class="metric"><div class="k">Δ avg turnover</div><div class="v">{fmt_x(review['full_available_history']['delta']['avg_turnover_x'])}</div></div>
        <div class="metric"><div class="k">MDD reduction</div><div class="v">{fmt_pct(review['full_available_history']['delta']['max_drawdown_reduction_pct_points'])}</div></div>
      </div>
      <p><strong>half-split stability</strong></p>
      {half_table}
      <div class="note">half-split 只用于回答“全可用历史内部前后半是否一致方向”，不是新调参入口。</div>
    </div>

    <div class="card">
      <h2>5) 按月 / 按季度 / 按年表现</h2>
      <p><strong>按月</strong></p>
      {monthly_table}
      <p style="margin-top:12px"><strong>按季度</strong></p>
      {quarterly_table}
      <p style="margin-top:12px"><strong>按年</strong></p>
      {yearly_table}
    </div>

    <div class="card">
      <h2>6) 不同年份里 veto 是改善 short leg 还是只是降频</h2>
      <div class="mono">定义：按每次换仓 gross return 线性分解，long leg = 0.5 × mean(long future return)，short leg = 0.5 × mean(-future return of selected shorts)。这一页不讨论新想法，只看同一 frozen spec 下，不同年份里 veto 是否把 short leg contribution 往正方向推，以及它是否只是通过降低换手“看起来更好”。</div>
      <ul>
        <li>full-history long leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['long_leg_mean_gross_bps'])}</strong></li>
        <li>full-history plain short leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['plain_short_leg_mean_gross_bps'])}</strong></li>
        <li>full-history veto short leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['veto_short_leg_mean_gross_bps'])}</strong></li>
      </ul>
      {year_leg_table}
      <div class="note">如果某年 <code>delta_short_leg_bps &gt; 0</code> 但 <code>delta_turnover_x</code> 并没有显著下降，说明 veto 更像是在改善 short leg，而不只是靠“少动”拿表面分数。</div>
    </div>

    <div class="card">
      <h2>7) veto 命中率与误杀率</h2>
      <div class="mono">name-level 命中：被 veto 的 plain-short 候选，在该持有窗里如果原本做空它会亏钱（short PnL &lt; 0），记为 hit；
name-level 误杀：被 veto 的 plain-short 候选，在该持有窗里如果原本做空它会赚钱（short PnL &gt; 0），记为 false kill；
rebalance-level outperform / underperform：仅在发生过 veto 的换仓里，看 veto gross 是否高于 / 低于 plain gross。</div>
      <ul>
        <li>pct rebalances with any veto：<strong>{fmt_pct(review['veto_effectiveness']['pct_rebalances_with_any_veto'])}</strong></li>
        <li>avg veto count / rebalance：<strong>{review['veto_effectiveness']['avg_veto_count_per_rebalance']:.3f}</strong></li>
        <li>rebalance count with any veto：<strong>{review['veto_effectiveness']['rebalance_count_with_any_veto']}</strong></li>
        <li>total vetoed names：<strong>{review['veto_effectiveness']['total_vetoed_names']}</strong></li>
        <li>name-level hit rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_hit_rate'])}</strong></li>
        <li>name-level false-kill rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_false_kill_rate'])}</strong></li>
        <li>name-level neutral rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_neutral_rate'])}</strong></li>
        <li>rebalance-level outperform rate | any veto：<strong>{fmt_pct(review['veto_effectiveness']['rebalance_level_outperform_rate_given_any_veto'])}</strong></li>
        <li>rebalance-level underperform rate | any veto：<strong>{fmt_pct(review['veto_effectiveness']['rebalance_level_underperform_rate_given_any_veto'])}</strong></li>
      </ul>
    </div>

    <div class="card">
      <h2>8) 当前 keep/live 是否还能成立</h2>
      <div class="note warn">{review['final_verdict']}</div>
      <p class="muted">这句 verdict 只基于这次 <strong>frozen-spec long-history validation</strong>：不新增研究、不改参数、不扩样本后重调。</p>
    </div>
  </div>
</body>
</html>
'''
    SITE_PATH.write_text(html, encoding="utf-8")

    print(json.dumps({
        "summary_json": str((ART_DIR / "rank213_long_history_review_summary.json").relative_to(ROOT)),
        "detail_csv": str((ART_DIR / "rank213_long_history_detail.csv").relative_to(ROOT)),
        "monthly_csv": str((ART_DIR / "rank213_long_history_monthly.csv").relative_to(ROOT)),
        "quarterly_csv": str((ART_DIR / "rank213_long_history_quarterly.csv").relative_to(ROOT)),
        "yearly_csv": str((ART_DIR / "rank213_long_history_yearly.csv").relative_to(ROOT)),
        "year_leg_csv": str((ART_DIR / "rank213_long_history_year_leg_effect.csv").relative_to(ROOT)),
        "availability_csv": str((ART_DIR / "rank213_long_history_universe_availability.csv").relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
