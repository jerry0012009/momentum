#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import math
import os
import time
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_14d_phase3_validation.html"

DAILY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_daily.csv"
EXEC_TIMING_DAILY_PATH = ART_DIR / "rank213_age90_14d_second_round_validation_execution_timing_daily.csv"
PRICE_DIR = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "daily_1d"
RAW_15M_DIR = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "raw_15m" / "monthly"

SUMMARY_PATH = ART_DIR / "rank213_age90_14d_phase3_validation_summary.json"
EXEC_COST_PATH = ART_DIR / "rank213_age90_14d_phase3_execution_cost_grid.csv"
EXEC_DAILY_PATH = ART_DIR / "rank213_age90_14d_phase3_execution_daily.csv"
LIQUIDITY_PATH = ART_DIR / "rank213_age90_14d_phase3_liquidity_capacity.csv"
GATE_PATH = ART_DIR / "rank213_age90_14d_phase3_gate_grid.csv"
WALK_FORWARD_PATH = ART_DIR / "rank213_age90_14d_phase3_walk_forward.csv"
SIDE_PATH = ART_DIR / "rank213_age90_14d_phase3_side_decomposition.csv"
MONTHLY_PATH = ART_DIR / "rank213_age90_14d_phase3_monthly.csv"

STRATEGY = "age90_14d_skip1d_voladj"
TOP_N = 3
BOTTOM_N = 3
LEG_WEIGHT = 1.0 / (TOP_N + BOTTOM_N)
COST_GRID_BPS = [4, 8, 12, 16, 20]
TWAP_WINDOWS_MIN = [30, 60, 240]
BINANCE_15M_URL = "https://data.binance.vision/data/futures/um/monthly/klines/{symbol}/15m/{symbol}-15m-{ym}.zip"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fmt_pct(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}%"
    except (TypeError, ValueError):
        return ""


def fmt_bps(x: object, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f} bps"
    except (TypeError, ValueError):
        return ""


def fmt_usd(x: object) -> str:
    try:
        if pd.isna(x):
            return ""
        v = float(x)
    except (TypeError, ValueError):
        return ""
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:.0f}"


def compound(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    return float((1.0 + ret).prod() - 1.0) if len(ret) else np.nan


def max_drawdown(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def stats_from_ret(ret: pd.Series, active: pd.Series | None = None) -> dict:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if active is None:
        active = pd.Series(True, index=ret.index)
    active = active.reindex(ret.index).fillna(False).astype(bool)
    return {
        "rows": int(len(ret)),
        "trading_baskets": int(active.sum()),
        "net_mean_bps": float(ret.mean() * 10000.0) if len(ret) else np.nan,
        "net_cum_pct": float(compound(ret) * 100.0) if len(ret) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(ret) else np.nan,
        "win_rate_pct": float((ret[active] > 0).mean() * 100.0) if active.any() else np.nan,
    }


def read_daily() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PATH)
    df = df[df["strategy"] == STRATEGY].copy()
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True, format="mixed")
    df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True, format="mixed")
    for col in ["gross_ret", "net_ret"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["active"] = df["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df.dropna(subset=["timestamp_ts", "exit_ts", "gross_ret", "net_ret"]).sort_values("timestamp_ts").reset_index(drop=True)


def build_leg_tasks(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row_id, r in daily.iterrows():
        for side, col in [("long", "longs"), ("short", "shorts")]:
            for symbol in [x for x in str(r[col]).split(",") if x]:
                rows.append({
                    "row_id": int(row_id),
                    "timestamp_ts": r["timestamp_ts"],
                    "exit_ts": r["exit_ts"],
                    "symbol": symbol,
                    "side": side,
                })
    return pd.DataFrame(rows)


def needed_symbol_months(tasks: pd.DataFrame) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for _, r in tasks.iterrows():
        out.add((str(r["symbol"]), pd.Timestamp(r["timestamp_ts"]).strftime("%Y-%m")))
        out.add((str(r["symbol"]), pd.Timestamp(r["exit_ts"]).strftime("%Y-%m")))
    return out


def monthly_zip_path(symbol: str, ym: str) -> Path:
    return RAW_15M_DIR / symbol / f"{symbol}-15m-{ym}.zip"


def download_one(symbol: str, ym: str) -> tuple[str, str, bool, str]:
    path = monthly_zip_path(symbol, ym)
    if path.exists() and path.stat().st_size > 0:
        return symbol, ym, True, "cached"
    ensure_dir(path.parent)
    tmp = path.with_suffix(".zip.tmp")
    url = BINANCE_15M_URL.format(symbol=symbol, ym=ym)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "rank213-phase3-validation/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if not data:
            return symbol, ym, False, "empty"
        tmp.write_bytes(data)
        tmp.replace(path)
        return symbol, ym, True, "downloaded"
    except urllib.error.HTTPError as exc:
        if tmp.exists():
            tmp.unlink()
        return symbol, ym, False, f"http_{exc.code}"
    except Exception as exc:
        if tmp.exists():
            tmp.unlink()
        return symbol, ym, False, type(exc).__name__


def ensure_15m_cache(pairs: set[tuple[str, str]], workers: int = 8) -> dict:
    if os.getenv("PHASE3_SKIP_15M_DOWNLOAD", "0") == "1":
        rows = []
        for symbol, ym in sorted(pairs):
            ok = monthly_zip_path(symbol, ym).exists()
            rows.append({"symbol": symbol, "month": ym, "ok": ok, "status": "cached" if ok else "missing_skip_download"})
        ok_count = sum(1 for r in rows if r["ok"])
        return {
            "needed_symbol_months": len(rows),
            "available_symbol_months": ok_count,
            "coverage_pct": ok_count / len(rows) * 100.0 if rows else np.nan,
            "status_counts": pd.Series([r["status"] for r in rows]).value_counts().to_dict() if rows else {},
        }

    rows = []
    done = 0
    pairs_list = sorted(pairs)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(download_one, symbol, ym) for symbol, ym in pairs_list]
        for fut in as_completed(futs):
            symbol, ym, ok, status = fut.result()
            rows.append({"symbol": symbol, "month": ym, "ok": ok, "status": status})
            done += 1
            if done % 100 == 0:
                print(f"[15m-cache] {done}/{len(pairs_list)}")
            time.sleep(0.001)
    ok_count = sum(1 for r in rows if r["ok"])
    return {
        "needed_symbol_months": len(pairs_list),
        "available_symbol_months": ok_count,
        "coverage_pct": ok_count / len(pairs_list) * 100.0 if pairs_list else np.nan,
        "status_counts": pd.Series([r["status"] for r in rows]).value_counts().to_dict() if rows else {},
    }


def read_15m_zip(path: Path) -> pd.DataFrame:
    names = [
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trade_count", "taker_base", "taker_quote", "ignore",
    ]
    try:
        with zipfile.ZipFile(path) as zf:
            members = zf.namelist()
            if not members:
                return pd.DataFrame()
            data = zf.read(members[0])
        df = pd.read_csv(io.BytesIO(data), header=None, names=names)
    except Exception:
        return pd.DataFrame()
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce")
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "close"])
    if df.empty:
        return pd.DataFrame()
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["open_time"].astype("int64"), unit="ms", utc=True),
        "open": df["open"].astype(float),
        "close": df["close"].astype(float),
        "volume": df["volume"].astype(float),
        "quote_volume": df["quote_volume"].astype(float),
    }).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    # Phase 3 only needs execution windows starting at UTC 00:00 up to 4h.
    # Filtering here keeps full-history symbol-month decompression manageable.
    return out[out["timestamp"].dt.hour < 4]


def read_symbol_15m(symbol: str, months: list[str]) -> pd.DataFrame:
    parts = []
    for ym in months:
        path = monthly_zip_path(symbol, ym)
        if not path.exists():
            continue
        part = read_15m_zip(path)
        if not part.empty:
            parts.append(part)
    if not parts:
        return pd.DataFrame(
            columns=["open", "close", "volume", "quote_volume"],
            index=pd.DatetimeIndex([], tz="UTC", name="timestamp"),
        )
    out = pd.concat(parts, ignore_index=True).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    return out.set_index("timestamp")


def window_price(frame: pd.DataFrame, start: pd.Timestamp, minutes: int, mode: str) -> tuple[float, float, int]:
    if frame.empty:
        return np.nan, np.nan, 0
    sub = frame[(frame.index >= start) & (frame.index < start + pd.Timedelta(minutes=minutes))]
    if sub.empty:
        return np.nan, np.nan, 0
    qv = pd.to_numeric(sub["quote_volume"], errors="coerce").fillna(0.0)
    vol = pd.to_numeric(sub["volume"], errors="coerce").fillna(0.0)
    close = pd.to_numeric(sub["close"], errors="coerce").dropna()
    if mode == "vwap" and vol.sum() > 0:
        price = float(qv.sum() / vol.sum())
    else:
        price = float(close.mean()) if len(close) else np.nan
    return price, float(qv.sum()), int(len(sub))


def build_intraday_execution(daily: pd.DataFrame, tasks: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    month_map: dict[str, set[str]] = {}
    for symbol, ym in needed_symbol_months(tasks):
        month_map.setdefault(symbol, set()).add(ym)

    leg_rows = []
    for n, (symbol, sub_tasks) in enumerate(tasks.groupby("symbol"), start=1):
        frame = read_symbol_15m(symbol, sorted(month_map.get(symbol, set())))
        if n % 10 == 0:
            print(f"[15m-eval] {n}/{len(month_map)} symbols", flush=True)
        for _, task in sub_tasks.iterrows():
            for minutes in TWAP_WINDOWS_MIN:
                for mode in ["twap", "vwap"]:
                    entry_price, entry_qv, entry_bars = window_price(frame, task["timestamp_ts"], minutes, mode)
                    exit_price, exit_qv, exit_bars = window_price(frame, task["exit_ts"], minutes, mode)
                    ok = np.isfinite(entry_price) and np.isfinite(exit_price) and entry_price > 0
                    raw = float(exit_price / entry_price - 1.0) if ok else np.nan
                    contrib = raw if task["side"] == "long" else -raw
                    leg_rows.append({
                        "row_id": int(task["row_id"]),
                        "timestamp_ts": task["timestamp_ts"],
                        "scenario": f"{mode}_{minutes}m",
                        "symbol": symbol,
                        "side": task["side"],
                        "entry_price": entry_price,
                        "exit_price": exit_price,
                        "entry_quote_volume": entry_qv,
                        "exit_quote_volume": exit_qv,
                        "min_quote_volume": min(entry_qv, exit_qv) if ok else np.nan,
                        "entry_bars": entry_bars,
                        "exit_bars": exit_bars,
                        "contrib_ret": contrib if ok else np.nan,
                        "ok": bool(ok),
                    })

    leg = pd.DataFrame(leg_rows)
    daily_rows = []
    liq_rows = []
    for (row_id, scenario), sub in leg.groupby(["row_id", "scenario"]):
        ok = sub[sub["ok"]].copy()
        longs = ok[ok["side"] == "long"]["contrib_ret"]
        shorts = ok[ok["side"] == "short"]["contrib_ret"]
        gross = 0.5 * float(longs.mean()) + 0.5 * float(shorts.mean()) if len(longs) == TOP_N and len(shorts) == BOTTOM_N else np.nan
        min_qv = float(ok["min_quote_volume"].min()) if len(ok) else np.nan
        row_ts = daily.loc[int(row_id), "timestamp_ts"]
        daily_rows.append({
            "row_id": int(row_id),
            "timestamp_ts": row_ts,
            "scenario": scenario,
            "gross_ret": gross,
            "ok_legs": int(len(ok)),
            "coverage_pct": float(len(ok) / (TOP_N + BOTTOM_N) * 100.0),
            "min_leg_window_quote_volume": min_qv,
        })
        for participation in [0.01, 0.05, 0.10]:
            cap = min_qv * participation / LEG_WEIGHT if np.isfinite(min_qv) else np.nan
            liq_rows.append({
                "row_id": int(row_id),
                "timestamp_ts": row_ts,
                "scenario": scenario,
                "participation_pct": participation * 100.0,
                "capacity_usdt": cap,
            })
    daily_exec = pd.DataFrame(daily_rows)
    liquidity_daily = pd.DataFrame(liq_rows)

    cost_rows = []
    for scenario, sub in daily_exec.groupby("scenario"):
        sub = sub.sort_values("timestamp_ts").copy()
        active = sub["gross_ret"].notna()
        for cost in COST_GRID_BPS:
            net = sub["gross_ret"].fillna(0.0) - cost / 10000.0
            net = net.where(active, 0.0)
            cost_rows.append({
                "scenario": scenario,
                "cost_bps_per_basket": cost,
                "avg_coverage_pct": float(sub["coverage_pct"].mean()) if len(sub) else np.nan,
                **stats_from_ret(net, active),
            })

    liq_summary = []
    for (scenario, participation), sub in liquidity_daily.groupby(["scenario", "participation_pct"]):
        cap = pd.to_numeric(sub["capacity_usdt"], errors="coerce").dropna()
        liq_summary.append({
            "scenario": scenario,
            "participation_pct": participation,
            "days": int(len(cap)),
            "p10_capacity_usdt": float(cap.quantile(0.10)) if len(cap) else np.nan,
            "median_capacity_usdt": float(cap.median()) if len(cap) else np.nan,
            "p90_capacity_usdt": float(cap.quantile(0.90)) if len(cap) else np.nan,
            "pct_days_capacity_ge_100k": float((cap >= 100_000).mean() * 100.0) if len(cap) else np.nan,
            "pct_days_capacity_ge_500k": float((cap >= 500_000).mean() * 100.0) if len(cap) else np.nan,
            "pct_days_capacity_ge_1m": float((cap >= 1_000_000).mean() * 100.0) if len(cap) else np.nan,
        })
    return pd.DataFrame(cost_rows), daily_exec, pd.DataFrame(liq_summary)


def build_daily_execution_cost_grid(daily: pd.DataFrame) -> pd.DataFrame:
    scenarios: list[tuple[str, pd.Series, pd.Series, float]] = [
        ("close_to_close_reference", daily["gross_ret"], daily["active"], 100.0),
    ]
    if EXEC_TIMING_DAILY_PATH.exists():
        timing = pd.read_csv(EXEC_TIMING_DAILY_PATH)
        timing["timestamp_ts"] = pd.to_datetime(timing["timestamp_ts"], utc=True, format="mixed")
        timing["gross_ret"] = pd.to_numeric(timing["gross_ret"], errors="coerce")
        timing["coverage_pct"] = pd.to_numeric(timing["coverage_pct"], errors="coerce")
        rename = {
            "same_day_open_to_next_open": "signal_day_open_to_next_open",
            "delayed_next_open_to_following_open": "delayed_next_open_to_following_open",
        }
        for old, new in rename.items():
            sub = timing[timing["scenario"] == old].sort_values("timestamp_ts").copy()
            if not sub.empty:
                scenarios.append((new, sub["gross_ret"].reset_index(drop=True), sub["gross_ret"].notna().reset_index(drop=True), float(sub["coverage_pct"].mean())))
    rows = []
    for scenario, gross, active, coverage in scenarios:
        for cost in COST_GRID_BPS:
            net = pd.to_numeric(gross, errors="coerce").fillna(0.0) - cost / 10000.0
            net = net.where(active.fillna(False).astype(bool), 0.0)
            rows.append({
                "scenario": scenario,
                "cost_bps_per_basket": cost,
                "avg_coverage_pct": coverage,
                **stats_from_ret(net, active.fillna(False).astype(bool)),
            })
    return pd.DataFrame(rows)


def read_close(symbol: str) -> pd.Series:
    path = PRICE_DIR / f"{symbol}.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    return df.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp").set_index("timestamp")["close"].sort_index()


def trailing_comp(ret: pd.Series, window: int) -> pd.Series:
    vals = []
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0).reset_index(drop=True)
    for i in range(len(ret)):
        hist = ret.iloc[max(0, i - window):i]
        vals.append(compound(hist) if len(hist) == window else np.nan)
    return pd.Series(vals)


def build_gate_masks(daily: pd.DataFrame) -> dict[str, pd.Series]:
    ret = daily["net_ret"].reset_index(drop=True)
    btc = read_close("BTCUSDT")
    eth = read_close("ETHUSDT")
    btc_vals = []
    eth_vals = []
    for ts in daily["timestamp_ts"]:
        t1 = ts - pd.Timedelta(days=1)
        t0 = ts - pd.Timedelta(days=61)
        btc_vals.append(float(btc.loc[t1] / btc.loc[t0] - 1.0) if t1 in btc.index and t0 in btc.index else np.nan)
        eth_vals.append(float(eth.loc[t1] / eth.loc[t0] - 1.0) if t1 in eth.index and t0 in eth.index else np.nan)
    btc_eth = (pd.Series(btc_vals) > 0) & (pd.Series(eth_vals) > 0)
    return {
        "trade_all_reference": pd.Series(True, index=daily.index),
        "prior_30d_return_positive": (trailing_comp(ret, 30) > 0).set_axis(daily.index),
        "prior_60d_return_positive": (trailing_comp(ret, 60) > 0).set_axis(daily.index),
        "prior_30d_return_above_minus5pct": (trailing_comp(ret, 30) > -0.05).set_axis(daily.index),
        "btc_eth_prior_60d_positive": btc_eth.set_axis(daily.index),
    }


def build_gate_grid(daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    masks = build_gate_masks(daily)
    gate_rows = []
    monthly_rows = []
    for name, mask in masks.items():
        mask = mask.fillna(False).astype(bool)
        for cost in COST_GRID_BPS:
            active = daily["active"] & mask
            net = (daily["gross_ret"] - cost / 10000.0).where(active, 0.0)
            gate_rows.append({
                "gate": name,
                "cost_bps_per_basket": cost,
                "active_rate_pct": float(active.mean() * 100.0),
                **stats_from_ret(net, active),
            })
        base_net = daily["net_ret"].where(daily["active"] & mask, 0.0)
        tmp = daily[["timestamp_ts", "month"]].copy()
        tmp["net_ret"] = base_net
        for month, sub in tmp.groupby("month"):
            monthly_rows.append({
                "gate": name,
                "month": month,
                "net_cum_pct": compound(sub["net_ret"]) * 100.0,
            })

    wf_rows = []
    gate_names = list(masks.keys())
    for test_year in [2022, 2023, 2024, 2025, 2026]:
        train_start = pd.Timestamp(f"{test_year-2}-01-01T00:00:00Z")
        train_end = pd.Timestamp(f"{test_year}-01-01T00:00:00Z")
        test_start = pd.Timestamp(f"{test_year}-01-01T00:00:00Z")
        test_end = pd.Timestamp(f"{test_year+1}-01-01T00:00:00Z")
        if test_year == 2026:
            test_end = daily["timestamp_ts"].max() + pd.Timedelta(days=1)
        train = (daily["timestamp_ts"] >= train_start) & (daily["timestamp_ts"] < train_end)
        test = (daily["timestamp_ts"] >= test_start) & (daily["timestamp_ts"] < test_end)
        choices = []
        for name in gate_names:
            active_train = daily["active"] & masks[name].fillna(False).astype(bool) & train
            train_net = daily["net_ret"].where(active_train, 0.0)
            train_stats = stats_from_ret(train_net[train], active_train[train])
            calmar = train_stats["net_cum_pct"] / abs(train_stats["max_drawdown_pct"]) if train_stats["max_drawdown_pct"] and not pd.isna(train_stats["max_drawdown_pct"]) else -np.inf
            choices.append((calmar, name, train_stats))
        choices.sort(key=lambda x: (x[0], x[2]["net_cum_pct"]), reverse=True)
        chosen = choices[0][1]
        active_test = daily["active"] & masks[chosen].fillna(False).astype(bool) & test
        test_net = daily["net_ret"].where(active_test, 0.0)
        wf_rows.append({
            "test_year": f"{test_year} YTD" if test_year == 2026 else str(test_year),
            "train_window": f"{test_year-2}-{test_year-1}",
            "selection_rule": "highest trailing 2Y Calmar among predeclared gates",
            "chosen_gate": chosen,
            **stats_from_ret(test_net[test], active_test[test]),
        })
    return pd.DataFrame(gate_rows), pd.DataFrame(wf_rows), pd.DataFrame(monthly_rows)


def build_side_decomposition(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cache: dict[str, pd.Series] = {}
    for _, r in daily.iterrows():
        longs = [x for x in str(r["longs"]).split(",") if x]
        shorts = [x for x in str(r["shorts"]).split(",") if x]
        lret = []
        sret = []
        for symbol in longs + shorts:
            if symbol not in cache:
                cache[symbol] = read_close(symbol)
            ser = cache[symbol]
            ts, xt = r["timestamp_ts"], r["exit_ts"]
            if ts not in ser.index or xt not in ser.index:
                continue
            raw = float(ser.loc[xt] / ser.loc[ts] - 1.0)
            if symbol in longs:
                lret.append(raw)
            else:
                sret.append(-raw)
        rows.append({
            "timestamp_ts": r["timestamp_ts"],
            "long_leg_ret": float(np.mean(lret)) if len(lret) == TOP_N else np.nan,
            "short_leg_ret": float(np.mean(sret)) if len(sret) == BOTTOM_N else np.nan,
        })
    leg = pd.DataFrame(rows)
    scenarios = {
        "dollar_neutral_original": 0.5 * leg["long_leg_ret"] + 0.5 * leg["short_leg_ret"] - 0.0004,
        "half_cap_long_contribution": 0.5 * leg["long_leg_ret"],
        "half_cap_short_contribution": 0.5 * leg["short_leg_ret"],
        "full_cap_long_only_minus_4bps": leg["long_leg_ret"] - 0.0004,
        "full_cap_short_only_minus_4bps": leg["short_leg_ret"] - 0.0004,
    }
    out = []
    for name, ret in scenarios.items():
        out.append({"side_scenario": name, **stats_from_ret(ret, ret.notna())})
    return pd.DataFrame(out)


def table_html(df: pd.DataFrame, cols: list[str], limit: int | None = None) -> str:
    work = df.copy()
    if limit is not None:
        work = work.head(limit)
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in work.iterrows():
        cells = []
        for c in cols:
            v = row.get(c, "")
            if c.endswith("_pct"):
                txt = fmt_pct(v)
            elif c.endswith("_bps"):
                txt = fmt_bps(v)
            elif c.endswith("_usdt"):
                txt = fmt_usd(v)
            elif isinstance(v, float):
                txt = f"{v:.4f}"
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_report(summary: dict, exec_cost: pd.DataFrame, liquidity: pd.DataFrame, gates: pd.DataFrame, wf: pd.DataFrame, side: pd.DataFrame, monthly: pd.DataFrame) -> str:
    generated = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    base = summary["base_stats"]
    twap4 = exec_cost[(exec_cost["scenario"] == "twap_240m") & (exec_cost["cost_bps_per_basket"] == 12)]
    twap4_txt = "n/a" if twap4.empty else f"{fmt_pct(twap4.iloc[0]['net_cum_pct'])} / DD {fmt_pct(twap4.iloc[0]['max_drawdown_pct'])}"
    prior60 = gates[(gates["gate"] == "prior_60d_return_positive") & (gates["cost_bps_per_basket"] == 4)]
    prior60_txt = "n/a" if prior60.empty else f"{fmt_pct(prior60.iloc[0]['net_cum_pct'])} / DD {fmt_pct(prior60.iloc[0]['max_drawdown_pct'])}"
    short_only = side[side["side_scenario"] == "full_cap_short_only_minus_4bps"]
    short_txt = "n/a" if short_only.empty else f"{fmt_pct(short_only.iloc[0]['net_cum_pct'])} / DD {fmt_pct(short_only.iloc[0]['max_drawdown_pct'])}"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 age90 Phase 3 严肃验证包</title>
  <style>
    body {{ margin:0; background:#f6f2ea; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.65; }}
    main {{ max-width:1200px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:#fff; border:1px solid #e5dccb; border-radius:16px; padding:18px 20px; margin:14px 0; box-shadow:0 1px 2px rgba(20,24,31,.04); }}
    .hero {{ background:linear-gradient(135deg,#ecfeff,#fff 55%,#fff7ed); border-color:#67e8f9; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#bbf7d0; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .muted {{ color:#64748b; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:980px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:14px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2) {{ text-align:left; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>age90_14d_skip1d_voladj Phase 3 严肃验证包</h1>
    <p>目标：判断它是否有资格进入 paper/live 候选，而不是继续扩展新策略。</p>
    <p class="muted">生成时间：{escape(generated)} · 样本：{escape(summary['sample_start'])} → {escape(summary['sample_end'])} · 15m symbol-month 覆盖：{fmt_pct(summary['cache_meta']['coverage_pct'])}</p>
    <p><a href="/momentum/paper/rank213_age90_14d_second_round_validation.html">二轮验证</a> · <a href="/momentum/paper/rank213_baseline_v2_four_direction_review.html">Baseline V2</a> · <a href="/momentum/paper/rank213_evidence_map.html">Evidence Map</a></p>
  </section>

  <section class="card warn">
    <h2>结论</h2>
    <p><b>当前结论：继续研究，但仍不能进 live。</b> 原 4bps close-to-close 为 {fmt_pct(base['net_cum_pct'])}，最大回撤 {fmt_pct(base['max_drawdown_pct'])}；但执行成本和 2022-2023 弱段仍是硬门槛。</p>
    <p><b>执行层：</b>4h TWAP 在 12bps 下为 {twap4_txt}。如果真实执行接近 12bps，策略安全边际明显变薄。</p>
    <p><b>风控层：</b><code>prior_60d_return_positive</code> 在 4bps 下为 {prior60_txt}，但 walk-forward 选择结果必须优先看下方逐年表，不能只看全样本。</p>
    <p><b>结构层：</b>收益主要来自 long 侧；full-cap short-only 为 {short_txt}，所以“做空弱币”不能单独构成可交易理由。</p>
  </section>

  <section class="card">
    <h2>1. 执行级验证：15m TWAP/VWAP + 成本</h2>
    <p class="muted">同一批 daily 选股，不重新打分；表里同时放 <code>close_to_close_reference</code>、<code>signal_day_open_to_next_open</code>、<code>delayed_next_open_to_following_open</code> 和 15m TWAP/VWAP。因为 score 明确跳过最近 1 天，只用 <code>t-15d → t-1d</code>，所以 UTC 00:00 的 signal-day 进场是 causal，不是拿当天 close 偷看。15m 窗口从 UTC 00:00 开始，30m/1h/4h 分别使用 2/4/16 根 15m bar。成本为 per-basket 扣减。</p>
    <div class="table-wrap">{table_html(exec_cost, ["scenario", "cost_bps_per_basket", "avg_coverage_pct", "trading_baskets", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>2. 换仓日成交额占比限制</h2>
    <p class="muted">容量估算：每条腿权重约 1/6，用 entry/exit 窗口较小 quote_volume 约束，计算在 1%/5%/10% 参与率下可承载的 basket notional。它不是滑点模型，只是容量红线。</p>
    <div class="table-wrap">{table_html(liquidity, ["scenario", "participation_pct", "days", "p10_capacity_usdt", "median_capacity_usdt", "p90_capacity_usdt", "pct_days_capacity_ge_100k", "pct_days_capacity_ge_500k", "pct_days_capacity_ge_1m"])}</div>
  </section>

  <section class="card">
    <h2>3. 预注册 Gate 验证</h2>
    <p class="muted">只测试事先定义的少数 gate：策略自身 30/60 日 trailing return、30 日 > -5%、BTC&ETH 60 日趋势。gate off 时空仓，收益记 0，避免“只统计开仓日”美化。</p>
    <div class="table-wrap">{table_html(gates, ["gate", "cost_bps_per_basket", "active_rate_pct", "trading_baskets", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>4. Walk-forward Freeze</h2>
    <p class="muted">每个测试年只用前两年，从预注册 gate 中按 trailing 2Y Calmar 选一个，然后固定到下一年。这个表比全样本 gate 更接近“以后真的怎么选”。</p>
    <div class="table-wrap">{table_html(wf, ["test_year", "train_window", "chosen_gate", "trading_baskets", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card">
    <h2>5. Long / Short 单边拆解</h2>
    <p class="muted">用原 close-to-close leg 重建收益，判断收益来自 long 强势币、short 弱势币，还是两边都有贡献。</p>
    <div class="table-wrap">{table_html(side, ["side_scenario", "trading_baskets", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "win_rate_pct"])}</div>
  </section>

  <section class="card warn">
    <h2>保守读法</h2>
    <ul>
      <li>如果要进 paper，建议先只允许 very small notional，并强制使用 15m TWAP/VWAP 执行口径，不用日线 close 幻觉。</li>
      <li>如果 12bps 后仍无法接受回撤，这条线应继续留在 research，不进入 live。</li>
      <li>下一轮如果继续推进，应接真实成交模拟：订单簿/盘口深度、资金费率、逐笔换仓和残留仓位处理。</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    daily = read_daily()
    tasks = build_leg_tasks(daily)
    pairs = needed_symbol_months(tasks)
    cache_meta = ensure_15m_cache(pairs)
    exec_cost, exec_daily, liquidity = build_intraday_execution(daily, tasks)
    exec_cost = pd.concat([build_daily_execution_cost_grid(daily), exec_cost], ignore_index=True)
    gates, wf, gate_monthly = build_gate_grid(daily)
    side = build_side_decomposition(daily)

    exec_cost.to_csv(EXEC_COST_PATH, index=False)
    exec_daily.to_csv(EXEC_DAILY_PATH, index=False)
    liquidity.to_csv(LIQUIDITY_PATH, index=False)
    gates.to_csv(GATE_PATH, index=False)
    wf.to_csv(WALK_FORWARD_PATH, index=False)
    side.to_csv(SIDE_PATH, index=False)
    gate_monthly.to_csv(MONTHLY_PATH, index=False)

    base_stats = stats_from_ret(daily["net_ret"], daily["active"])
    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strategy": STRATEGY,
        "sample_start": daily["timestamp_ts"].min().strftime("%Y-%m-%d"),
        "sample_end": daily["exit_ts"].max().strftime("%Y-%m-%d"),
        "base_stats": base_stats,
        "cache_meta": cache_meta,
        "artifacts": {
            "execution_cost_grid": str(EXEC_COST_PATH.relative_to(ROOT)),
            "execution_daily": str(EXEC_DAILY_PATH.relative_to(ROOT)),
            "liquidity_capacity": str(LIQUIDITY_PATH.relative_to(ROOT)),
            "gate_grid": str(GATE_PATH.relative_to(ROOT)),
            "walk_forward": str(WALK_FORWARD_PATH.relative_to(ROOT)),
            "side_decomposition": str(SIDE_PATH.relative_to(ROOT)),
            "gate_monthly": str(MONTHLY_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_PATH.write_text(build_report(summary, exec_cost, liquidity, gates, wf, side, gate_monthly), encoding="utf-8")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
