#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_14d_fourth_round_benchmark_attribution.html"

DAILY_PATH = ART_DIR / "rank213_monthly_volume_baseline_refresh_daily.csv"
UNIVERSE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_monthly_universe.csv"
CANDIDATE_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_candidates.csv"
PRICE_DIR = ART_DIR / "rank213_local_cache" / "monthly_volume_universe" / "daily_1d"

SUMMARY_PATH = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_summary.json"
DAILY_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_daily.csv"
BENCHMARK_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_benchmark_stats.csv"
REGRESSION_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_regression_stats.csv"
ANNUAL_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_annual.csv"
MONTHLY_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_monthly.csv"
CONDITIONAL_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_conditional.csv"
STATE_SLICE_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_state_slices.csv"
DISPERSION_OUT = ART_DIR / "rank213_age90_14d_fourth_round_benchmark_attribution_dispersion_slices.csv"
PARAM_GRID_OUT = ART_DIR / "rank213_age90_14d_fourth_round_param_stability_grid.csv"
PARAM_DAILY_OUT = ART_DIR / "rank213_age90_14d_fourth_round_param_stability_daily.csv"
DISPERSION_CONTROL_OUT = ART_DIR / "rank213_age90_14d_fourth_round_dispersion_position_control.csv"
LONG_ONLY_HEDGE_OUT = ART_DIR / "rank213_age90_14d_fourth_round_long_only_btc_hedge.csv"

STRATEGY = "age90_14d_skip1d_voladj"
BASE_COST_BPS = 4.0
AGE_DAYS = 90
ROLLING_BETA_DAYS = 180
ROLLING_BETA_MIN_DAYS = 90
UNIVERSE_SIZE_GRID = [20, 30, 50, 70, 100]
LEG_COUNT_GRID = [3, 4]


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


def fmt_num(x: object, digits: int = 3) -> str:
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return escape(str(x))


def compound(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    return float((1.0 + ret).prod() - 1.0)


def max_drawdown(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def stats(name: str, ret: pd.Series) -> dict:
    ret = pd.to_numeric(ret, errors="coerce").dropna()
    return {
        "series": name,
        "rows": int(len(ret)),
        "mean_bps": float(ret.mean() * 10000.0) if len(ret) else np.nan,
        "cum_pct": float(compound(ret) * 100.0) if len(ret) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(ret) else np.nan,
        "win_rate_pct": float((ret > 0).mean() * 100.0) if len(ret) else np.nan,
        "daily_vol_pct": float(ret.std() * 100.0) if len(ret) > 1 else np.nan,
    }


def stats_with_active(name: str, ret: pd.Series, active: pd.Series | None = None) -> dict:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if active is None:
        active = pd.Series(True, index=ret.index)
    active = active.fillna(False).astype(bool)
    out = stats(name, ret)
    out["active_days"] = int(active.sum())
    out["active_rate_pct"] = float(active.mean() * 100.0) if len(active) else np.nan
    active_ret = ret[active]
    out["active_mean_bps"] = float(active_ret.mean() * 10000.0) if len(active_ret) else np.nan
    return out


def selected_symbols(text: object) -> list[str]:
    if pd.isna(text):
        return []
    return [x.strip().upper() for x in str(text).split(",") if x.strip()]


def read_strategy_daily() -> pd.DataFrame:
    df = pd.read_csv(DAILY_PATH)
    df = df[df["strategy"] == STRATEGY].copy()
    df["timestamp_ts"] = pd.to_datetime(df["timestamp_ts"], utc=True, format="mixed")
    df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True, format="mixed")
    for col in ["gross_ret", "net_ret"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["active"] = df["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df.dropna(subset=["timestamp_ts", "exit_ts", "gross_ret", "net_ret"]).sort_values("timestamp_ts").reset_index(drop=True)


def read_universe_map() -> dict[str, list[str]]:
    df = pd.read_csv(UNIVERSE_PATH)
    return {str(row["month"]): selected_symbols(row["selected_symbols"]) for _, row in df.iterrows()}


def read_onboard_map() -> dict[str, pd.Timestamp]:
    df = pd.read_csv(CANDIDATE_PATH)
    df["onboard_utc"] = pd.to_datetime(df["onboard_utc"], utc=True, format="mixed")
    return {str(row["symbol"]).upper(): row["onboard_utc"] for _, row in df.iterrows()}


def read_price_cache(symbol: str, cache: dict[str, pd.Series | None]) -> pd.Series | None:
    symbol = symbol.upper()
    if symbol in cache:
        return cache[symbol]
    path = PRICE_DIR / f"{symbol}.csv"
    if not path.exists():
        cache[symbol] = None
        return None
    df = pd.read_csv(path, usecols=["timestamp", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce", format="mixed")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df = df.dropna(subset=["timestamp", "close"]).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
    cache[symbol] = df.set_index("timestamp")["close"] if not df.empty else None
    return cache[symbol]


def symbol_ret(symbol: str, ts: pd.Timestamp, exit_ts: pd.Timestamp, cache: dict[str, pd.Series | None]) -> float:
    ser = read_price_cache(symbol, cache)
    if ser is None or ts not in ser.index or exit_ts not in ser.index:
        return np.nan
    px0 = float(ser.loc[ts])
    px1 = float(ser.loc[exit_ts])
    if not np.isfinite(px0) or not np.isfinite(px1) or px0 <= 0:
        return np.nan
    return px1 / px0 - 1.0


def mean_symbol_return(symbols: list[str], ts: pd.Timestamp, exit_ts: pd.Timestamp, cache: dict[str, pd.Series | None]) -> tuple[float, int, int]:
    vals = [symbol_ret(sym, ts, exit_ts, cache) for sym in symbols]
    good = [x for x in vals if np.isfinite(x)]
    return (float(np.mean(good)) if good else np.nan, len(good), len(vals))


def symbol_return_stats(symbols: list[str], ts: pd.Timestamp, exit_ts: pd.Timestamp, cache: dict[str, pd.Series | None]) -> dict:
    vals = [symbol_ret(sym, ts, exit_ts, cache) for sym in symbols]
    good = np.array([x for x in vals if np.isfinite(x)], dtype=float)
    if good.size == 0:
        return {
            "mean": np.nan,
            "std": np.nan,
            "p90": np.nan,
            "p10": np.nan,
            "p90_p10": np.nan,
            "avg_abs": np.nan,
            "ok": 0,
            "total": len(vals),
        }
    p90 = float(np.percentile(good, 90))
    p10 = float(np.percentile(good, 10))
    return {
        "mean": float(np.mean(good)),
        "std": float(np.std(good, ddof=1)) if good.size > 1 else 0.0,
        "p90": p90,
        "p10": p10,
        "p90_p10": p90 - p10,
        "avg_abs": float(np.mean(np.abs(good))),
        "ok": int(good.size),
        "total": len(vals),
    }


def build_daily_attribution(strategy: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    universe_map = read_universe_map()
    onboard_map = read_onboard_map()
    cache: dict[str, pd.Series | None] = {}
    rows = []

    for _, row in strategy.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        month = str(row["month"])
        universe = universe_map.get(month, [])
        eligible = [
            sym for sym in universe
            if sym in onboard_map and ts - onboard_map[sym] >= pd.Timedelta(days=AGE_DAYS)
        ]
        longs = selected_symbols(row["longs"])
        shorts = selected_symbols(row["shorts"])

        btc_ret = symbol_ret("BTCUSDT", ts, exit_ts, cache)
        top30_stats = symbol_return_stats(universe, ts, exit_ts, cache)
        eligible_stats = symbol_return_stats(eligible, ts, exit_ts, cache)
        long_stats = symbol_return_stats(longs, ts, exit_ts, cache)
        short_stats = symbol_return_stats(shorts, ts, exit_ts, cache)
        top30_ew = top30_stats["mean"]
        eligible_ew = eligible_stats["mean"]
        long_avg = long_stats["mean"]
        short_raw_avg = short_stats["mean"]

        short_pnl_avg = -short_raw_avg if np.isfinite(short_raw_avg) else np.nan
        xs_long_vs_eligible = long_avg - eligible_ew if np.isfinite(long_avg) and np.isfinite(eligible_ew) else np.nan
        xs_short_vs_eligible = eligible_ew - short_raw_avg if np.isfinite(short_raw_avg) and np.isfinite(eligible_ew) else np.nan
        xs_spread_gross = 0.5 * xs_long_vs_eligible + 0.5 * xs_short_vs_eligible if np.isfinite(xs_long_vs_eligible) and np.isfinite(xs_short_vs_eligible) else np.nan

        rows.append({
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
            "month": month,
            "strategy_gross": float(row["gross_ret"]),
            "strategy_net_4bps": float(row["net_ret"]),
            "btc_ret": btc_ret,
            "top30_ew_ret": top30_ew,
            "eligible_ew_ret": eligible_ew,
            "long_top3_avg_ret": long_avg,
            "short_bottom3_raw_ret": short_raw_avg,
            "short_bottom3_pnl_ret": short_pnl_avg,
            "long_half_contribution": 0.5 * long_avg if np.isfinite(long_avg) else np.nan,
            "short_half_contribution": 0.5 * short_pnl_avg if np.isfinite(short_pnl_avg) else np.nan,
            "long_top3_minus_eligible_ew": xs_long_vs_eligible,
            "short_bottom3_minus_eligible_ew": xs_short_vs_eligible,
            "xs_spread_gross_rebuilt": xs_spread_gross,
            "xs_spread_net_4bps": xs_spread_gross - BASE_COST_BPS / 10000.0 if np.isfinite(xs_spread_gross) else np.nan,
            "strategy_minus_btc": float(row["net_ret"]) - btc_ret if np.isfinite(btc_ret) else np.nan,
            "strategy_minus_top30_ew": float(row["net_ret"]) - top30_ew if np.isfinite(top30_ew) else np.nan,
            "strategy_minus_eligible_ew": float(row["net_ret"]) - eligible_ew if np.isfinite(eligible_ew) else np.nan,
            "long_top3_minus_btc": long_avg - btc_ret if np.isfinite(long_avg) and np.isfinite(btc_ret) else np.nan,
            "eligible_dispersion_std": eligible_stats["std"],
            "eligible_dispersion_p90_p10": eligible_stats["p90_p10"],
            "eligible_avg_abs_ret": eligible_stats["avg_abs"],
            "top30_dispersion_p90_p10": top30_stats["p90_p10"],
            "universe_count": len(universe),
            "eligible_count": len(eligible),
            "top30_price_coverage_pct": top30_stats["ok"] / top30_stats["total"] * 100.0 if top30_stats["total"] else np.nan,
            "eligible_price_coverage_pct": eligible_stats["ok"] / eligible_stats["total"] * 100.0 if eligible_stats["total"] else np.nan,
            "long_price_coverage_pct": long_stats["ok"] / long_stats["total"] * 100.0 if long_stats["total"] else np.nan,
            "short_price_coverage_pct": short_stats["ok"] / short_stats["total"] * 100.0 if short_stats["total"] else np.nan,
        })

    out = pd.DataFrame(rows)
    out["btc_abs_ret"] = out["btc_ret"].abs()
    out["eligible_abs_ret"] = out["eligible_ew_ret"].abs()
    out["prior30_btc_vol"] = out["btc_ret"].shift(1).rolling(30, min_periods=20).std()
    out["prior30_eligible_vol"] = out["eligible_ew_ret"].shift(1).rolling(30, min_periods=20).std()
    out["prior30_eligible_dispersion"] = out["eligible_dispersion_p90_p10"].shift(1).rolling(30, min_periods=20).mean()
    meta = {
        "rows": int(len(out)),
        "avg_top30_price_coverage_pct": float(out["top30_price_coverage_pct"].mean()),
        "avg_eligible_price_coverage_pct": float(out["eligible_price_coverage_pct"].mean()),
        "avg_eligible_count": float(out["eligible_count"].mean()),
        "avg_eligible_dispersion_p90_p10_bps": float(out["eligible_dispersion_p90_p10"].mean() * 10000.0),
        "strategy_gross_rebuild_max_abs_diff": float((out["strategy_gross"] - out["xs_spread_gross_rebuilt"]).abs().max()),
    }
    return out, meta


def regression_stats(y: pd.Series, x: pd.Series, factor_name: str) -> dict:
    df = pd.DataFrame({"y": y, "x": x}).dropna()
    if len(df) < 3 or float(df["x"].var()) == 0.0:
        return {
            "factor": factor_name,
            "rows": int(len(df)),
            "alpha_bps_per_day": np.nan,
            "beta": np.nan,
            "r2": np.nan,
            "corr": np.nan,
            "beta_hedged_cum_pct": np.nan,
            "beta_hedged_mdd_pct": np.nan,
        }
    x_arr = df["x"].to_numpy(dtype=float)
    y_arr = df["y"].to_numpy(dtype=float)
    X = np.column_stack([np.ones_like(x_arr), x_arr])
    alpha, beta = np.linalg.lstsq(X, y_arr, rcond=None)[0]
    yhat = X @ np.array([alpha, beta])
    r2 = 1.0 - float(((y_arr - yhat) ** 2).sum() / ((y_arr - y_arr.mean()) ** 2).sum())
    beta_hedged = pd.Series(y_arr - beta * x_arr, index=df.index)
    return {
        "factor": factor_name,
        "rows": int(len(df)),
        "alpha_bps_per_day": float(alpha * 10000.0),
        "beta": float(beta),
        "r2": float(r2),
        "corr": float(df["y"].corr(df["x"])),
        "beta_hedged_cum_pct": float(compound(beta_hedged) * 100.0),
        "beta_hedged_mdd_pct": float(max_drawdown(beta_hedged) * 100.0),
    }


def add_rolling_beta_hedges(daily: pd.DataFrame) -> pd.DataFrame:
    out = daily.copy()
    for factor_col, out_col in [
        ("btc_ret", "rolling180_btc_beta_hedged_net"),
        ("eligible_ew_ret", "rolling180_eligible_beta_hedged_net"),
        ("top30_ew_ret", "rolling180_top30_beta_hedged_net"),
    ]:
        betas = []
        y = pd.to_numeric(out["strategy_net_4bps"], errors="coerce")
        x = pd.to_numeric(out[factor_col], errors="coerce")
        for i in range(len(out)):
            hist = pd.DataFrame({
                "y": y.iloc[max(0, i - ROLLING_BETA_DAYS):i],
                "x": x.iloc[max(0, i - ROLLING_BETA_DAYS):i],
            }).dropna()
            if len(hist) < ROLLING_BETA_MIN_DAYS or float(hist["x"].var()) == 0.0:
                betas.append(0.0)
                continue
            beta = float(np.cov(hist["y"], hist["x"], ddof=1)[0, 1] / hist["x"].var(ddof=1))
            betas.append(beta)
        beta_col = out_col.replace("_net", "_beta")
        out[beta_col] = betas
        out[out_col] = out["strategy_net_4bps"] - out[beta_col] * out[factor_col]
    return out


def build_benchmark_stats(daily: pd.DataFrame) -> pd.DataFrame:
    series = {
        "strategy_net_4bps": daily["strategy_net_4bps"],
        "strategy_gross": daily["strategy_gross"],
        "BTC buy-and-hold close-to-close": daily["btc_ret"],
        "Top30 causal universe equal-weight": daily["top30_ew_ret"],
        "Age90 eligible universe equal-weight": daily["eligible_ew_ret"],
        "Long top3 full exposure gross": daily["long_top3_avg_ret"],
        "Long top3 minus eligible EW": daily["long_top3_minus_eligible_ew"],
        "Short bottom3 vs eligible EW": daily["short_bottom3_minus_eligible_ew"],
        "XS spread rebuilt net 4bps": daily["xs_spread_net_4bps"],
        "Strategy minus BTC": daily["strategy_minus_btc"],
        "Strategy minus Top30 EW": daily["strategy_minus_top30_ew"],
        "Rolling180 BTC beta-hedged net": daily["rolling180_btc_beta_hedged_net"],
        "Rolling180 eligible beta-hedged net": daily["rolling180_eligible_beta_hedged_net"],
    }
    return pd.DataFrame([stats(name, ret) for name, ret in series.items()])


def build_annual(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.copy()
    work["year"] = work["timestamp_ts"].dt.year
    rows = []
    for year, sub in work.groupby("year"):
        rows.append({
            "year": int(year),
            "days": int(len(sub)),
            "strategy_net_pct": compound(sub["strategy_net_4bps"]) * 100.0,
            "btc_pct": compound(sub["btc_ret"]) * 100.0,
            "eligible_ew_pct": compound(sub["eligible_ew_ret"]) * 100.0,
            "long_top3_pct": compound(sub["long_top3_avg_ret"]) * 100.0,
            "long_half_contribution_pct": compound(sub["long_half_contribution"]) * 100.0,
            "short_half_contribution_pct": compound(sub["short_half_contribution"]) * 100.0,
            "long_minus_eligible_pct": compound(sub["long_top3_minus_eligible_ew"]) * 100.0,
            "short_vs_eligible_pct": compound(sub["short_bottom3_minus_eligible_ew"]) * 100.0,
            "long_half_mean_bps": float(sub["long_half_contribution"].mean() * 10000.0),
            "short_half_mean_bps": float(sub["short_half_contribution"].mean() * 10000.0),
            "long_xs_mean_bps": float(sub["long_top3_minus_eligible_ew"].mean() * 10000.0),
            "short_xs_mean_bps": float(sub["short_bottom3_minus_eligible_ew"].mean() * 10000.0),
            "rolling_btc_hedged_pct": compound(sub["rolling180_btc_beta_hedged_net"]) * 100.0,
            "corr_to_btc": sub["strategy_net_4bps"].corr(sub["btc_ret"]),
            "corr_to_eligible_ew": sub["strategy_net_4bps"].corr(sub["eligible_ew_ret"]),
        })
    return pd.DataFrame(rows)


def build_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.copy()
    work["month"] = work["timestamp_ts"].dt.strftime("%Y-%m")
    rows = []
    for month, sub in work.groupby("month"):
        rows.append({
            "month": month,
            "days": int(len(sub)),
            "strategy_net_pct": compound(sub["strategy_net_4bps"]) * 100.0,
            "btc_pct": compound(sub["btc_ret"]) * 100.0,
            "eligible_ew_pct": compound(sub["eligible_ew_ret"]) * 100.0,
            "long_top3_pct": compound(sub["long_top3_avg_ret"]) * 100.0,
            "long_minus_eligible_pct": compound(sub["long_top3_minus_eligible_ew"]) * 100.0,
            "short_vs_eligible_pct": compound(sub["short_bottom3_minus_eligible_ew"]) * 100.0,
        })
    return pd.DataFrame(rows)


def build_conditional(daily: pd.DataFrame) -> pd.DataFrame:
    masks = {
        "BTC up days": daily["btc_ret"] > 0,
        "BTC down days": daily["btc_ret"] < 0,
        "Eligible EW up days": daily["eligible_ew_ret"] > 0,
        "Eligible EW down days": daily["eligible_ew_ret"] < 0,
        "BTC abs <= 1%": daily["btc_ret"].abs() <= 0.01,
        "BTC abs > 3%": daily["btc_ret"].abs() > 0.03,
        "Eligible EW abs <= 1%": daily["eligible_ew_ret"].abs() <= 0.01,
        "Eligible EW abs > 3%": daily["eligible_ew_ret"].abs() > 0.03,
    }
    rows = []
    for name, mask in masks.items():
        sub = daily[mask.fillna(False)]
        row = stats(name, sub["strategy_net_4bps"])
        row["days"] = int(len(sub))
        row["btc_mean_bps"] = float(sub["btc_ret"].mean() * 10000.0) if len(sub) else np.nan
        row["eligible_ew_mean_bps"] = float(sub["eligible_ew_ret"].mean() * 10000.0) if len(sub) else np.nan
        row["long_minus_eligible_mean_bps"] = float(sub["long_top3_minus_eligible_ew"].mean() * 10000.0) if len(sub) else np.nan
        row["short_vs_eligible_mean_bps"] = float(sub["short_bottom3_minus_eligible_ew"].mean() * 10000.0) if len(sub) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def slice_row(group: str, name: str, sub: pd.DataFrame, total_rows: int) -> dict:
    row = stats(name, sub["strategy_net_4bps"])
    row["slice_group"] = group
    row["slice"] = name
    row["days"] = int(len(sub))
    row["active_rate_pct"] = float(len(sub) / total_rows * 100.0) if total_rows else np.nan
    row["btc_mean_bps"] = float(sub["btc_ret"].mean() * 10000.0) if len(sub) else np.nan
    row["eligible_ew_mean_bps"] = float(sub["eligible_ew_ret"].mean() * 10000.0) if len(sub) else np.nan
    row["long_half_mean_bps"] = float(sub["long_half_contribution"].mean() * 10000.0) if len(sub) else np.nan
    row["short_half_mean_bps"] = float(sub["short_half_contribution"].mean() * 10000.0) if len(sub) else np.nan
    row["long_xs_mean_bps"] = float(sub["long_top3_minus_eligible_ew"].mean() * 10000.0) if len(sub) else np.nan
    row["short_xs_mean_bps"] = float(sub["short_bottom3_minus_eligible_ew"].mean() * 10000.0) if len(sub) else np.nan
    row["eligible_dispersion_mean_bps"] = float(sub["eligible_dispersion_p90_p10"].mean() * 10000.0) if len(sub) else np.nan
    row["prior30_dispersion_mean_bps"] = float(sub["prior30_eligible_dispersion"].mean() * 10000.0) if len(sub) else np.nan
    return row


def tercile_masks(s: pd.Series) -> list[tuple[str, pd.Series]]:
    valid = pd.to_numeric(s, errors="coerce").dropna()
    if len(valid) < 10:
        empty = pd.Series(False, index=s.index)
        return [("low", empty), ("mid", empty), ("high", empty)]
    q1, q2 = valid.quantile([1 / 3, 2 / 3])
    return [
        ("low", s <= q1),
        ("mid", (s > q1) & (s <= q2)),
        ("high", s > q2),
    ]


def build_state_slices(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(daily)
    state_masks = [
        ("eligible_EW_state", "big_up_>3pct", daily["eligible_ew_ret"] > 0.03),
        ("eligible_EW_state", "up_1pct_to_3pct", (daily["eligible_ew_ret"] > 0.01) & (daily["eligible_ew_ret"] <= 0.03)),
        ("eligible_EW_state", "flat_abs_<=1pct", daily["eligible_ew_ret"].abs() <= 0.01),
        ("eligible_EW_state", "down_-3pct_to_-1pct", (daily["eligible_ew_ret"] >= -0.03) & (daily["eligible_ew_ret"] < -0.01)),
        ("eligible_EW_state", "big_down_<-3pct", daily["eligible_ew_ret"] < -0.03),
        ("BTC_realized_move", "abs_<=1pct", daily["btc_abs_ret"] <= 0.01),
        ("BTC_realized_move", "abs_1pct_to_3pct", (daily["btc_abs_ret"] > 0.01) & (daily["btc_abs_ret"] <= 0.03)),
        ("BTC_realized_move", "abs_>3pct", daily["btc_abs_ret"] > 0.03),
    ]
    for group, name, mask in state_masks:
        rows.append(slice_row(group, name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_btc_vol"]):
        rows.append(slice_row("BTC_prior30_vol_causal_tercile", name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_eligible_vol"]):
        rows.append(slice_row("eligible_prior30_vol_causal_tercile", name, daily[mask.fillna(False)], total))
    return pd.DataFrame(rows)


def build_dispersion_slices(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total = len(daily)
    for name, mask in tercile_masks(daily["eligible_dispersion_p90_p10"]):
        rows.append(slice_row("same_day_eligible_dispersion_diagnostic", name, daily[mask.fillna(False)], total))
    for name, mask in tercile_masks(daily["prior30_eligible_dispersion"]):
        rows.append(slice_row("prior30_eligible_dispersion_causal_proxy", name, daily[mask.fillna(False)], total))

    valid = daily.dropna(subset=["eligible_dispersion_p90_p10"]).copy()
    if len(valid) >= 10:
        valid["dispersion_decile"] = pd.qcut(valid["eligible_dispersion_p90_p10"], 10, labels=False, duplicates="drop")
        for decile, sub in valid.groupby("dispersion_decile"):
            rows.append(slice_row("same_day_eligible_dispersion_decile", f"decile_{int(decile) + 1}", sub, total))
    return pd.DataFrame(rows)


def load_close_quote_panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    candidates = pd.read_csv(CANDIDATE_PATH)["symbol"].astype(str).str.upper().tolist()
    close_frames: list[pd.Series] = []
    qv_frames: list[pd.Series] = []
    for symbol in candidates:
        path = PRICE_DIR / f"{symbol}.csv"
        if not path.exists():
            continue
        try:
            df = pd.read_csv(path, usecols=["timestamp", "close", "quote_volume"])
        except ValueError:
            continue
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce", format="mixed")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["quote_volume"] = pd.to_numeric(df["quote_volume"], errors="coerce")
        df = df.dropna(subset=["timestamp"]).drop_duplicates("timestamp", keep="last").sort_values("timestamp")
        if df.empty:
            continue
        close_frames.append(df.set_index("timestamp")["close"].rename(symbol))
        qv_frames.append(df.set_index("timestamp")["quote_volume"].rename(symbol))
    close = pd.concat(close_frames, axis=1).sort_index()
    quote_volume = pd.concat(qv_frames, axis=1).sort_index()
    close.index = pd.to_datetime(close.index, utc=True)
    quote_volume.index = pd.to_datetime(quote_volume.index, utc=True)
    return close, quote_volume


def build_monthly_ranked_universes(
    months: list[str],
    quote_volume: pd.DataFrame,
    onboard_map: dict[str, pd.Timestamp],
    max_n: int,
) -> dict[str, list[str]]:
    ranked: dict[str, list[str]] = {}
    for month in sorted(set(months)):
        current = pd.Timestamp(f"{month}-01T00:00:00Z")
        prev_start = current - pd.offsets.MonthBegin(1)
        prev_end = current - pd.Timedelta(days=1)
        sub = quote_volume[(quote_volume.index >= prev_start) & (quote_volume.index <= prev_end)]
        qv = sub.sum(axis=0, min_count=1).dropna()
        qv = qv[qv > 0].sort_values(ascending=False)
        symbols = [
            sym for sym in qv.index.astype(str)
            if sym in onboard_map and onboard_map[sym] < current
        ]
        ranked[month] = symbols[:max_n]
    return ranked


def score_for_day(close: pd.DataFrame, decision_ts: pd.Timestamp, eligible: list[str]) -> pd.Series:
    t0 = decision_ts - pd.Timedelta(days=15)
    t1 = decision_ts - pd.Timedelta(days=1)
    if t0 not in close.index or t1 not in close.index or not eligible:
        return pd.Series(dtype=float)
    cols = [sym for sym in eligible if sym in close.columns]
    if not cols:
        return pd.Series(dtype=float)
    px0 = pd.to_numeric(close.loc[t0, cols], errors="coerce")
    px1 = pd.to_numeric(close.loc[t1, cols], errors="coerce")
    mom = px1 / px0 - 1.0
    hist = close.loc[t0:t1, cols].pct_change(fill_method=None).dropna(how="all")
    vol = hist.std().replace(0.0, np.nan)
    return (mom / vol).replace([np.inf, -np.inf], np.nan).dropna()


def returns_for_symbols(close: pd.DataFrame, symbols: list[str], ts: pd.Timestamp, exit_ts: pd.Timestamp) -> pd.Series:
    cols = [sym for sym in symbols if sym in close.columns]
    if not cols or ts not in close.index or exit_ts not in close.index:
        return pd.Series(dtype=float)
    px0 = pd.to_numeric(close.loc[ts, cols], errors="coerce")
    px1 = pd.to_numeric(close.loc[exit_ts, cols], errors="coerce")
    ret = px1 / px0 - 1.0
    return ret.replace([np.inf, -np.inf], np.nan).dropna()


def build_param_stability_backtest(strategy: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    close, quote_volume = load_close_quote_panels()
    onboard_map = read_onboard_map()
    ranked_by_month = build_monthly_ranked_universes(
        strategy["month"].astype(str).tolist(),
        quote_volume,
        onboard_map,
        max(UNIVERSE_SIZE_GRID),
    )
    rows: list[dict] = []
    for _, row in strategy.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        month = str(row["month"])
        ranked_universe = ranked_by_month.get(month, [])
        btc_ret_ser = returns_for_symbols(close, ["BTCUSDT"], ts, exit_ts)
        btc_ret = float(btc_ret_ser.iloc[0]) if len(btc_ret_ser) else np.nan
        for universe_size in UNIVERSE_SIZE_GRID:
            universe = ranked_universe[:universe_size]
            eligible = [
                sym for sym in universe
                if sym in onboard_map and ts - onboard_map[sym] >= pd.Timedelta(days=AGE_DAYS)
            ]
            scores = score_for_day(close, ts, eligible).sort_values()
            for leg_count in LEG_COUNT_GRID:
                active = len(scores) >= leg_count * 2
                longs = scores.index[-leg_count:].tolist()[::-1] if active else []
                shorts = scores.index[:leg_count].tolist() if active else []
                long_ret = returns_for_symbols(close, longs, ts, exit_ts)
                short_raw_ret = returns_for_symbols(close, shorts, ts, exit_ts)
                active = active and len(long_ret) == leg_count and len(short_raw_ret) == leg_count
                long_avg = float(long_ret.mean()) if active else np.nan
                short_raw_avg = float(short_raw_ret.mean()) if active else np.nan
                short_pnl = -short_raw_avg if active else np.nan
                gross = 0.5 * long_avg + 0.5 * short_pnl if active else 0.0
                net = gross - BASE_COST_BPS / 10000.0 if active else 0.0
                long_only_net = long_avg - BASE_COST_BPS / 10000.0 if active else 0.0
                rows.append({
                    "timestamp_ts": ts,
                    "exit_ts": exit_ts,
                    "month": month,
                    "universe_size": universe_size,
                    "leg_count": leg_count,
                    "eligible_count": len(eligible),
                    "active": bool(active),
                    "longs": ",".join(longs),
                    "shorts": ",".join(shorts),
                    "long_avg_ret": long_avg if active else 0.0,
                    "short_raw_avg_ret": short_raw_avg if active else 0.0,
                    "short_pnl_avg_ret": short_pnl if active else 0.0,
                    "gross_ret": gross,
                    "net_ret_4bps": net,
                    "long_only_net_4bps": long_only_net,
                    "btc_ret": btc_ret,
                })
    daily = pd.DataFrame(rows).sort_values(["universe_size", "leg_count", "timestamp_ts"]).reset_index(drop=True)
    grid_rows = []
    long_hedge_rows = []
    for (universe_size, leg_count), sub in daily.groupby(["universe_size", "leg_count"]):
        name = f"universe{universe_size}_long{leg_count}_short{leg_count}"
        stat = stats_with_active(name, sub["net_ret_4bps"], sub["active"])
        stat["universe_size"] = universe_size
        stat["leg_count"] = leg_count
        stat["avg_eligible_count"] = float(sub["eligible_count"].mean())
        stat["long_half_mean_bps"] = float((0.5 * sub["long_avg_ret"]).mean() * 10000.0)
        stat["short_half_mean_bps"] = float((0.5 * sub["short_pnl_avg_ret"]).mean() * 10000.0)
        grid_rows.append(stat)

        work = sub.copy().reset_index(drop=True)
        y = pd.to_numeric(work["long_only_net_4bps"], errors="coerce").fillna(0.0)
        x = pd.to_numeric(work["btc_ret"], errors="coerce").fillna(0.0)
        betas = []
        for i in range(len(work)):
            hist = pd.DataFrame({
                "y": y.iloc[max(0, i - ROLLING_BETA_DAYS):i],
                "x": x.iloc[max(0, i - ROLLING_BETA_DAYS):i],
            }).dropna()
            if len(hist) < ROLLING_BETA_MIN_DAYS or float(hist["x"].var()) == 0.0:
                betas.append(0.0)
            else:
                betas.append(float(np.cov(hist["y"], hist["x"], ddof=1)[0, 1] / hist["x"].var(ddof=1)))
        work["rolling_btc_beta"] = betas
        work["long_only_btc_hedged_net"] = work["long_only_net_4bps"] - work["rolling_btc_beta"] * work["btc_ret"]
        unhedged = stats_with_active(f"long_only_unhedged_u{universe_size}_top{leg_count}", work["long_only_net_4bps"], work["active"])
        hedged = stats_with_active(f"long_only_btc_hedged_u{universe_size}_top{leg_count}", work["long_only_btc_hedged_net"], work["active"])
        for label, row_stat in [("unhedged", unhedged), ("rolling_btc_hedged", hedged)]:
            row_stat["universe_size"] = universe_size
            row_stat["leg_count"] = leg_count
            row_stat["variant"] = label
            row_stat["avg_rolling_beta"] = float(np.mean(betas))
            long_hedge_rows.append(row_stat)

    grid = pd.DataFrame(grid_rows).sort_values(["universe_size", "leg_count"])
    long_hedge = pd.DataFrame(long_hedge_rows).sort_values(["universe_size", "leg_count", "variant"])
    return daily, grid, long_hedge


def build_dispersion_position_control(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.copy()
    q1, q2 = work["prior30_eligible_dispersion"].dropna().quantile([1 / 3, 2 / 3])
    low = work["prior30_eligible_dispersion"] <= q1
    mid = (work["prior30_eligible_dispersion"] > q1) & (work["prior30_eligible_dispersion"] <= q2)
    high = work["prior30_eligible_dispersion"] > q2
    variants = {
        "base_no_dispersion_control": pd.Series(1.0, index=work.index),
        "gate_high_only": high.astype(float),
        "gate_mid_high": (mid | high).astype(float),
        "scale_low0.5_mid1_high1.5": pd.Series(np.select([low, mid, high], [0.5, 1.0, 1.5], default=0.0), index=work.index),
        "scale_low0_mid0.75_high1.5": pd.Series(np.select([low, mid, high], [0.0, 0.75, 1.5], default=0.0), index=work.index),
    }
    rows = []
    gross = pd.to_numeric(work["strategy_gross"], errors="coerce").fillna(0.0)
    for name, scale in variants.items():
        scale = scale.fillna(0.0).astype(float)
        ret = scale * gross - scale * BASE_COST_BPS / 10000.0
        stat = stats_with_active(name, ret, scale > 0)
        stat["avg_scale"] = float(scale.mean())
        stat["max_scale"] = float(scale.max())
        stat["low_days"] = int((scale == 0.5).sum()) if "low0.5" in name else int((low & (scale > 0)).sum())
        stat["mid_days"] = int((mid & (scale > 0)).sum())
        stat["high_days"] = int((high & (scale > 0)).sum())
        rows.append(stat)
    return pd.DataFrame(rows)


def table_html(df: pd.DataFrame, cols: list[str], *, max_rows: int | None = None) -> str:
    view = df[cols].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in view.iterrows():
        cells = []
        for c in cols:
            v = row.get(c, "")
            if c.endswith("_pct") or c in {"cum_pct", "max_drawdown_pct", "win_rate_pct", "daily_vol_pct"}:
                txt = fmt_pct(v)
            elif c.endswith("_bps") or c in {"mean_bps", "alpha_bps_per_day", "btc_mean_bps", "eligible_ew_mean_bps", "long_minus_eligible_mean_bps", "short_vs_eligible_mean_bps"}:
                txt = fmt_bps(v)
            elif c in {"beta", "r2", "corr", "corr_to_btc", "corr_to_eligible_ew"}:
                txt = fmt_num(v, 4)
            elif isinstance(v, float):
                txt = fmt_num(v, 2)
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def multi_equity_svg(daily: pd.DataFrame) -> str:
    series = {
        "strategy net": ("strategy_net_4bps", "#1d4ed8"),
        "BTC": ("btc_ret", "#f97316"),
        "eligible EW": ("eligible_ew_ret", "#16a34a"),
        "rolling BTC hedged": ("rolling180_btc_beta_hedged_net", "#7c3aed"),
    }
    width, height = 1120, 420
    left, right, top, bottom = 72, 190, 30, 54
    plot_w = width - left - right
    plot_h = height - top - bottom
    work = daily.sort_values("timestamp_ts").copy()
    ts_min, ts_max = work["timestamp_ts"].min(), work["timestamp_ts"].max()
    x_span = max((ts_max - ts_min).total_seconds(), 1.0)
    equities = {}
    logs = []
    for label, (col, _) in series.items():
        eq = (1.0 + pd.to_numeric(work[col], errors="coerce").fillna(0.0)).cumprod()
        equities[label] = eq
        logs.extend(np.log(eq.clip(lower=1e-6)).tolist())
    y_min, y_max = float(np.nanmin(logs)), float(np.nanmax(logs))
    if y_max <= y_min:
        y_max = y_min + 1.0

    def xy(ts: pd.Timestamp, eq: float) -> tuple[float, float]:
        x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
        y = top + (1.0 - ((np.log(max(eq, 1e-6)) - y_min) / (y_max - y_min))) * plot_h
        return x, y

    paths = []
    legend = []
    for i, (label, (_, color)) in enumerate(series.items()):
        pts = [xy(ts, float(eq)) for ts, eq in zip(work["timestamp_ts"], equities[label])]
        path = " ".join(("M" if j == 0 else "L") + f"{x:.2f},{y:.2f}" for j, (x, y) in enumerate(pts))
        paths.append(f"<path d='{path}' fill='none' stroke='{color}' stroke-width='2.3'/>")
        ly = top + 22 + i * 24
        legend.append(f"<line x1='{width-right+25}' y1='{ly}' x2='{width-right+48}' y2='{ly}' stroke='{color}' stroke-width='3'/><text x='{width-right+56}' y='{ly+4}'>{escape(label)}</text>")
    grid = []
    for eq in [0.25, 0.5, 1, 2, 5, 10]:
        y = top + (1.0 - ((np.log(eq) - y_min) / (y_max - y_min))) * plot_h
        if top <= y <= top + plot_h:
            grid.append(f"<line x1='{left}' y1='{y:.1f}' x2='{width-right}' y2='{y:.1f}' stroke='#e2e8f0'/><text x='{left-8}' y='{y+4:.1f}' text-anchor='end'>{eq:g}x</text>")
    years = []
    for year in range(ts_min.year, ts_max.year + 1):
        ts = pd.Timestamp(f"{year}-01-01T00:00:00Z")
        if ts_min <= ts <= ts_max:
            x = left + ((ts - ts_min).total_seconds() / x_span) * plot_w
            years.append(f"<line x1='{x:.1f}' y1='{top}' x2='{x:.1f}' y2='{top+plot_h}' stroke='#f1f5f9'/><text x='{x:.1f}' y='{height-28}' text-anchor='middle'>{year}</text>")
    return f"""
<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="benchmark equity comparison">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="13" fill="#475569">
    {''.join(grid)}
    {''.join(years)}
    <line x1="{left}" y1="{top+plot_h}" x2="{width-right}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    <line x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}" stroke="#cbd5e1"/>
    {''.join(paths)}
    {''.join(legend)}
    <text x="{left}" y="20" font-size="15" font-weight="700" fill="#172033">策略 vs BTC / 同池等权 / causal beta hedge（log scale）</text>
  </g>
</svg>
"""


def monthly_scatter_svg(monthly: pd.DataFrame) -> str:
    width, height = 760, 520
    left, right, top, bottom = 70, 26, 34, 62
    plot_w = width - left - right
    plot_h = height - top - bottom
    x = pd.to_numeric(monthly["btc_pct"], errors="coerce")
    y = pd.to_numeric(monthly["strategy_net_pct"], errors="coerce")
    xmin, xmax = min(float(x.min()), -5.0), max(float(x.max()), 5.0)
    ymin, ymax = min(float(y.min()), -5.0), max(float(y.max()), 5.0)
    span_x = xmax - xmin or 1.0
    span_y = ymax - ymin or 1.0

    def px(v: float) -> float:
        return left + (v - xmin) / span_x * plot_w

    def py(v: float) -> float:
        return top + (1.0 - (v - ymin) / span_y) * plot_h

    dots = []
    for _, row in monthly.iterrows():
        xv, yv = float(row["btc_pct"]), float(row["strategy_net_pct"])
        color = "#1d4ed8" if yv >= 0 else "#dc2626"
        dots.append(f"<circle cx='{px(xv):.1f}' cy='{py(yv):.1f}' r='4.2' fill='{color}' opacity='0.72'><title>{escape(str(row['month']))}: BTC {xv:.1f}%, strategy {yv:.1f}%</title></circle>")
    zero_x = px(0.0)
    zero_y = py(0.0)
    return f"""
<svg class="scatter" viewBox="0 0 {width} {height}" role="img" aria-label="monthly BTC versus strategy scatter">
  <rect x="0" y="0" width="{width}" height="{height}" rx="18" fill="#fff"/>
  <g font-family="Noto Sans SC, Microsoft YaHei, sans-serif" font-size="13" fill="#475569">
    <line x1="{left}" y1="{zero_y:.1f}" x2="{width-right}" y2="{zero_y:.1f}" stroke="#cbd5e1"/>
    <line x1="{zero_x:.1f}" y1="{top}" x2="{zero_x:.1f}" y2="{height-bottom}" stroke="#cbd5e1"/>
    {''.join(dots)}
    <text x="{left}" y="22" font-size="15" font-weight="700" fill="#172033">逐月：BTC 收益 vs 策略收益</text>
    <text x="{left + plot_w/2}" y="{height-20}" text-anchor="middle">BTC 月收益</text>
    <text x="18" y="{top + plot_h/2}" transform="rotate(-90 18,{top + plot_h/2})" text-anchor="middle">策略月收益</text>
    <text x="{left}" y="{height-36}">{xmin:.0f}%</text><text x="{width-right}" y="{height-36}" text-anchor="end">{xmax:.0f}%</text>
    <text x="{left-8}" y="{py(ymax)+4:.1f}" text-anchor="end">{ymax:.0f}%</text><text x="{left-8}" y="{py(ymin)+4:.1f}" text-anchor="end">{ymin:.0f}%</text>
  </g>
</svg>
"""


def build_report(
    daily: pd.DataFrame,
    benchmark: pd.DataFrame,
    regression: pd.DataFrame,
    annual: pd.DataFrame,
    monthly: pd.DataFrame,
    conditional: pd.DataFrame,
    state_slices: pd.DataFrame,
    dispersion_slices: pd.DataFrame,
    param_grid: pd.DataFrame,
    dispersion_control: pd.DataFrame,
    long_only_hedge: pd.DataFrame,
    meta: dict,
) -> str:
    generated = pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M UTC")
    b = benchmark.set_index("series")
    reg = regression.set_index("factor")
    btc_corr = float(reg.loc["BTC", "corr"])
    btc_beta = float(reg.loc["BTC", "beta"])
    eligible_beta = float(reg.loc["Age90 eligible EW", "beta"])
    down_btc = conditional[conditional["series"] == "BTC down days"].iloc[0]
    up_btc = conditional[conditional["series"] == "BTC up days"].iloc[0]
    btc_down_months = monthly[monthly["btc_pct"] < 0].copy()
    btc_up_big_months = monthly[monthly["btc_pct"] > 15].copy()
    best_excess = monthly.sort_values("long_minus_eligible_pct", ascending=False).head(8)
    worst_excess = monthly.sort_values("long_minus_eligible_pct", ascending=True).head(8)
    annual_best_long = annual.sort_values("long_xs_mean_bps", ascending=False).iloc[0]
    annual_worst_long = annual.sort_values("long_xs_mean_bps", ascending=True).iloc[0]
    same_day_disp = dispersion_slices[dispersion_slices["slice_group"] == "same_day_eligible_dispersion_diagnostic"].copy()
    prior_disp = dispersion_slices[dispersion_slices["slice_group"] == "prior30_eligible_dispersion_causal_proxy"].copy()
    high_disp = same_day_disp[same_day_disp["slice"] == "high"].iloc[0]
    low_disp = same_day_disp[same_day_disp["slice"] == "low"].iloc[0]
    best_param = param_grid.sort_values("cum_pct", ascending=False).iloc[0]
    hedged_only = long_only_hedge[long_only_hedge["variant"] == "rolling_btc_hedged"].copy()
    unhedged_only = long_only_hedge[long_only_hedge["variant"] == "unhedged"].copy()
    best_long_hedge = hedged_only.sort_values("cum_pct", ascending=False).iloc[0]
    best_long_unhedged = unhedged_only.sort_values("cum_pct", ascending=False).iloc[0]
    best_disp_control = dispersion_control.sort_values("cum_pct", ascending=False).iloc[0]

    verdict = (
        "不是单纯 BTC beta，但 long leg 仍有明显 crypto/alt beta 暴露；真正值得保留的是同池横截面排序，"
        "策略最吃横截面离散度和波动环境。下一步应优先研究 long 主体化、beta hedge、short 条件化，而不是继续叠复杂 gate。"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 age90 第四轮：Benchmark / Beta / Residual Alpha</title>
  <style>
    body {{ margin:0; background:#f4efe4; color:#182033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.65; }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:#fff; border:1px solid #e8ddca; border-radius:16px; padding:18px 20px; margin:14px 0; box-shadow:0 1px 2px rgba(20,24,31,.04); }}
    .hero {{ background:linear-gradient(135deg,#ecfeff,#fff 54%,#fff7ed); border-color:#67e8f9; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .good {{ background:#f0fdf4; border-color:#bbf7d0; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .twocol {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; align-items:start; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .muted {{ color:#64748b; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:880px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:14px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child {{ text-align:left; }}
    .chart,.scatter {{ width:100%; height:auto; border:1px solid #e2e8f0; border-radius:18px; background:#fff; margin:8px 0; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:860px) {{ .grid,.twocol {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213 age90 第四轮：Benchmark / Beta / Residual Alpha</h1>
    <p>问题：<b>213-age90 的收益到底来自市场上涨暴露，还是来自同一个历史可交易池内的横截面选币能力？</b></p>
    <p class="muted">生成时间：{escape(generated)}。样本与 Phase 3 一致：2020-02 到 2026-04，causal monthly-volume universe，age >= 90d。</p>
    <p><a href="/momentum/paper/rank213_age90_14d_fifth_round_profit_thickness.html">第五轮：真实成本利润厚度</a> · <a href="/momentum/paper/rank213_age90_top50_4x4_execution_stability.html">Top50 4x4 执行成本</a></p>
    <p><a href="/momentum/paper/rank213_age90_14d_phase3_validation.html">Phase 3</a> · <a href="/momentum/paper/rank213_age90_14d_second_round_validation.html">二轮验证</a> · <a href="/momentum/paper/rank213_age90_live_launch.html">Live launch</a></p>
  </section>

  <section class="card warn">
    <h2>一句话结论</h2>
    <p><b>{escape(verdict)}</b></p>
    <p>关键证据：策略对 BTC 的日频相关性 {fmt_num(btc_corr, 4)}，静态 beta {fmt_num(btc_beta, 4)}；BTC 下跌日策略均值 {fmt_bps(down_btc['mean_bps'])}，BTC 上涨日反而只有 {fmt_bps(up_btc['mean_bps'])}。这说明它不是简单 BTC 多头替代品。</p>
    <p>但 long top3 full exposure 累计 {fmt_pct(b.loc['Long top3 full exposure gross','cum_pct'])}，eligible universe 等权累计 {fmt_pct(b.loc['Age90 eligible universe equal-weight','cum_pct'])}；long 侧仍显著受 alt 市场环境影响，不能把未来收益建立在“币圈一定牛市”上。</p>
    <p>新增切片显示：同日 eligible 横截面离散度高时策略均值 {fmt_bps(high_disp['mean_bps'])}，低离散度时 {fmt_bps(low_disp['mean_bps'])}。这更接近策略本质：它需要币与币之间拉开差距，而不是所有币同涨同跌。</p>
    <p>参数扩展显示：最强参数网格是 universe={int(best_param['universe_size'])}, long/short={int(best_param['leg_count'])}/{int(best_param['leg_count'])}，累计 {fmt_pct(best_param['cum_pct'])}；最佳 long-only BTC hedge 是 {escape(str(best_long_hedge['series']))}，累计 {fmt_pct(best_long_hedge['cum_pct'])}；最佳 dispersion 控制是 {escape(str(best_disp_control['series']))}，累计 {fmt_pct(best_disp_control['cum_pct'])}。</p>
    <p><b>实用读法：</b>Top20/30/50 都能活，Top70/100 明显稀释；4x4 只在 Top50 上明显优于 3x3。prior30 dispersion sizing 没有跑赢原始全仓，最多是降低风险/降低收益的风控旋钮。long-only 裸多收益高但回撤极深；BTC beta hedge 没有救它，说明 short leg 不能简单用 BTC hedge 替代。</p>
  </section>

  <section class="card">
    <h2>核心指标</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_pct(b.loc['strategy_net_4bps','cum_pct'])}</b><span>策略净收益</span></div>
      <div class="metric"><b>{fmt_pct(b.loc['BTC buy-and-hold close-to-close','cum_pct'])}</b><span>同期 BTC</span></div>
      <div class="metric"><b>{fmt_pct(b.loc['Age90 eligible universe equal-weight','cum_pct'])}</b><span>同池 age90 等权</span></div>
      <div class="metric"><b>{fmt_pct(b.loc['Rolling180 BTC beta-hedged net','cum_pct'])}</b><span>滚动 BTC beta hedge 后</span></div>
    </div>
  </section>

  <section class="card">
    <h2>收益曲线对照</h2>
    {multi_equity_svg(daily)}
    <p class="muted">注意：Top30 / eligible EW benchmark 未扣真实换仓成本；策略净收益使用原研究 4bps flat cost。</p>
  </section>

  <section class="card">
    <h2>Benchmark 结果</h2>
    <div class="table-wrap">{table_html(benchmark, ["series", "rows", "mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "daily_vol_pct"])}</div>
  </section>

  <section class="card">
    <h2>Beta / 相关性</h2>
    <p>这里做两类判断：静态回归只用于诊断；rolling 180d beta hedge 是 causal 口径，只用过去数据估 beta。</p>
    <div class="table-wrap">{table_html(regression, ["factor", "rows", "alpha_bps_per_day", "beta", "r2", "corr", "beta_hedged_cum_pct", "beta_hedged_mdd_pct"])}</div>
    <p class="muted">解读：BTC beta 近 0，说明原策略不是 BTC 单因子；对 eligible EW 的 beta 为 {fmt_num(eligible_beta, 4)}，说明它与同池山寨市场也不是简单同向，但 long leg 本身仍会吃 alt regime。</p>
  </section>

  <section class="card">
    <h2>横截面增量拆解</h2>
    <p><code>long_top3_minus_eligible_ew</code> 衡量 long 选币是否跑赢同池平均；<code>short_bottom3_minus_eligible_ew</code> 衡量 short 选币是否真的选中了后续弱币。两者相加就是原多空 spread 的主体。</p>
    <div class="grid">
      <div class="metric"><b>{fmt_pct(b.loc['Long top3 minus eligible EW','cum_pct'])}</b><span>long 选币超额</span></div>
      <div class="metric"><b>{fmt_pct(b.loc['Short bottom3 vs eligible EW','cum_pct'])}</b><span>short 选币超额</span></div>
      <div class="metric"><b>{fmt_pct(b.loc['XS spread rebuilt net 4bps','cum_pct'])}</b><span>重建多空净收益</span></div>
      <div class="metric"><b>{fmt_pct(meta['avg_eligible_price_coverage_pct'])}</b><span>eligible 价格覆盖</span></div>
    </div>
  </section>

  <section class="card">
    <h2>年度 Long / Short 贡献</h2>
    <p>这里把原策略拆成：long top3 裸收益、0.5 long contribution、0.5 short contribution、long 相对同池超额、short 相对同池超额。重点看每年到底是哪一侧在赚钱。</p>
    <p class="muted">年度观察：long 选币超额最强年份是 {int(annual_best_long['year'])}，均值 {fmt_bps(annual_best_long['long_xs_mean_bps'])}；最弱年份是 {int(annual_worst_long['year'])}，均值 {fmt_bps(annual_worst_long['long_xs_mean_bps'])}。2025-2026 的改善确实主要来自 long 选币突然变强。</p>
    <div class="table-wrap">{table_html(annual, ["year", "days", "strategy_net_pct", "long_half_contribution_pct", "short_half_contribution_pct", "long_half_mean_bps", "short_half_mean_bps", "long_xs_mean_bps", "short_xs_mean_bps", "btc_pct", "eligible_ew_pct"])}</div>
  </section>

  <section class="card">
    <h2>条件切片</h2>
    <div class="table-wrap">{table_html(conditional, ["series", "days", "mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "btc_mean_bps", "eligible_ew_mean_bps", "long_minus_eligible_mean_bps", "short_vs_eligible_mean_bps"])}</div>
  </section>

  <section class="card">
    <h2>市场状态切片</h2>
    <p>这部分回答“什么环境适合 213-age90”。eligible EW 大涨/大跌/震荡是同池市场状态；BTC prior30 vol 和 eligible prior30 vol 是只用过去数据的 causal 波动 proxy。</p>
    <div class="table-wrap">{table_html(state_slices, ["slice_group", "slice", "days", "active_rate_pct", "mean_bps", "cum_pct", "max_drawdown_pct", "btc_mean_bps", "eligible_ew_mean_bps", "long_half_mean_bps", "short_half_mean_bps", "long_xs_mean_bps", "short_xs_mean_bps", "eligible_dispersion_mean_bps"])}</div>
  </section>

  <section class="card warn">
    <h2>横截面离散度切片</h2>
    <p><b>诊断口径：</b><code>same_day_eligible_dispersion</code> 使用当天 t→t+1d 的 eligible 内 p90-p10 收益差，只能解释环境，不能在入场时提前知道。</p>
    <p><b>可研究口径：</b><code>prior30_eligible_dispersion</code> 是过去 30 天离散度均值，属于 causal proxy，可以作为下一轮 gate/size 的候选，但还没证明可上线。</p>
    <div class="table-wrap">{table_html(dispersion_slices, ["slice_group", "slice", "days", "active_rate_pct", "mean_bps", "cum_pct", "max_drawdown_pct", "long_xs_mean_bps", "short_xs_mean_bps", "eligible_dispersion_mean_bps", "prior30_dispersion_mean_bps"])}</div>
  </section>

  <section class="card">
    <h2>参数稳定性：Universe 20/30/50/70/100 与 3x3/4x4</h2>
    <p>这里完整重算 causal monthly quote-volume universe，不再只拿原 Top30。每个月用上一完整月成交额选 Top N，再做 age90、14d skip1d vol-adjust 排名，比较 3L3S 与 4L4S。</p>
    <p class="muted">成本仍用 4bps flat，方便和主回测比较；4x4 实盘订单更多，真实成本可能高于表中假设。</p>
    <div class="table-wrap">{table_html(param_grid, ["series", "universe_size", "leg_count", "active_days", "active_rate_pct", "mean_bps", "active_mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "avg_eligible_count", "long_half_mean_bps", "short_half_mean_bps"])}</div>
  </section>

  <section class="card">
    <h2>Dispersion 仓位控制</h2>
    <p>这部分只用 <code>prior30_eligible_dispersion</code>，即入场前过去 30 天 eligible 内 p90-p10 离散度均值。它是可交易 proxy，不使用当天未来收益。</p>
    <p class="muted">结果用于判断是否值得下一轮做 sizing/gate；不是最终上线参数。尤其是高档 leverage 1.5 会放大回撤和真实成本。</p>
    <p><b>结论：</b>这一轮 prior30 dispersion 控制没有改善主策略。<code>gate_high_only</code> 把回撤从约 -60% 降到约 -41%，但累计收益也从约 +456% 降到约 +89%；scale 版本也没有优于原始全仓。因此 dispersion 更适合当风险监控/解释变量，不适合现在直接作为强 gate。</p>
    <div class="table-wrap">{table_html(dispersion_control, ["series", "active_days", "active_rate_pct", "avg_scale", "max_scale", "mean_bps", "active_mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "low_days", "mid_days", "high_days"])}</div>
  </section>

  <section class="card">
    <h2>不 Short：Long-only + BTC Rolling Beta Hedge</h2>
    <p>这里测试“只做 long topK，同时用过去 180 天估计 BTC beta 后动态对冲”。这回答：如果 short leg 很难实盘赚钱，能否用 BTC hedge 替代 short leg。</p>
    <p><b>结论：</b>不理想。最佳裸 long-only 是 {escape(str(best_long_unhedged['series']))}，累计 {fmt_pct(best_long_unhedged['cum_pct'])}，但最大回撤 {fmt_pct(best_long_unhedged['max_drawdown_pct'])}；最佳 BTC hedge 后只剩 {fmt_pct(best_long_hedge['cum_pct'])}，最大回撤仍 {fmt_pct(best_long_hedge['max_drawdown_pct'])}。BTC hedge 大幅削弱 upside，却没有真正解决 alt 崩盘尾部风险。</p>
    <div class="table-wrap">{table_html(long_only_hedge, ["series", "variant", "universe_size", "leg_count", "active_days", "active_rate_pct", "mean_bps", "active_mean_bps", "cum_pct", "max_drawdown_pct", "win_rate_pct", "avg_rolling_beta"])}</div>
  </section>

  <section class="card">
    <h2>年度表现</h2>
    <div class="table-wrap">{table_html(annual, ["year", "days", "strategy_net_pct", "btc_pct", "eligible_ew_pct", "long_top3_pct", "long_minus_eligible_pct", "short_vs_eligible_pct", "rolling_btc_hedged_pct", "corr_to_btc", "corr_to_eligible_ew"])}</div>
  </section>

  <section class="card">
    <h2>逐月关系</h2>
    <div class="twocol">
      <div>{monthly_scatter_svg(monthly)}</div>
      <div>
        <h3>BTC 下跌最深月份</h3>
        <div class="table-wrap">{table_html(btc_down_months.sort_values("btc_pct").head(10), ["month", "strategy_net_pct", "btc_pct", "eligible_ew_pct", "long_minus_eligible_pct", "short_vs_eligible_pct"])}</div>
        <h3>BTC 大涨月份</h3>
        <div class="table-wrap">{table_html(btc_up_big_months.sort_values("btc_pct", ascending=False).head(10), ["month", "strategy_net_pct", "btc_pct", "eligible_ew_pct", "long_minus_eligible_pct", "short_vs_eligible_pct"])}</div>
      </div>
    </div>
  </section>

  <section class="card">
    <h2>Long 选币超额的好坏月份</h2>
    <div class="twocol">
      <div>
        <h3>最好</h3>
        <div class="table-wrap">{table_html(best_excess, ["month", "strategy_net_pct", "btc_pct", "eligible_ew_pct", "long_minus_eligible_pct", "short_vs_eligible_pct"])}</div>
      </div>
      <div>
        <h3>最差</h3>
        <div class="table-wrap">{table_html(worst_excess, ["month", "strategy_net_pct", "btc_pct", "eligible_ew_pct", "long_minus_eligible_pct", "short_vs_eligible_pct"])}</div>
      </div>
    </div>
  </section>

  <section class="card good">
    <h2>第四轮后的研发方向</h2>
    <p><b>优先方向：</b>把 213-age90 改写为「Top20-50 横截面动量 + 更谨慎 short admission / 风控」研究，而不是简单 long-only BTC hedge。</p>
    <ul>
      <li>第一优先：围绕 <code>universe50_long4_short4</code> 和 <code>universe20/30_long3_short3</code> 做成本、换手、年份外推和真实执行压力测试。</li>
      <li>第二优先：short leg 不要删除，也不要简单替换成 BTC hedge；改成 short admission 或 short 降权，重点减少 short squeeze 和高成本场景。</li>
      <li>第三优先：dispersion 不作为硬 gate 上线；先作为仓位监控指标，只有在更多 causal proxy 验证后再考虑 sizing。</li>
      <li>第四优先：用 live canary 继续收集真实 maker/taker 成本；如果真实成本接近 12bps，当前所有高收益版本都需要重估。</li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    strategy = read_strategy_daily()
    daily, meta = build_daily_attribution(strategy)
    daily = add_rolling_beta_hedges(daily)

    benchmark = build_benchmark_stats(daily)
    regression = pd.DataFrame([
        regression_stats(daily["strategy_net_4bps"], daily["btc_ret"], "BTC"),
        regression_stats(daily["strategy_net_4bps"], daily["top30_ew_ret"], "Top30 EW"),
        regression_stats(daily["strategy_net_4bps"], daily["eligible_ew_ret"], "Age90 eligible EW"),
    ])
    annual = build_annual(daily)
    monthly = build_monthly(daily)
    conditional = build_conditional(daily)
    state_slices = build_state_slices(daily)
    dispersion_slices = build_dispersion_slices(daily)
    param_daily, param_grid, long_only_hedge = build_param_stability_backtest(strategy)
    dispersion_control = build_dispersion_position_control(daily)

    daily.to_csv(DAILY_OUT, index=False)
    benchmark.to_csv(BENCHMARK_OUT, index=False)
    regression.to_csv(REGRESSION_OUT, index=False)
    annual.to_csv(ANNUAL_OUT, index=False)
    monthly.to_csv(MONTHLY_OUT, index=False)
    conditional.to_csv(CONDITIONAL_OUT, index=False)
    state_slices.to_csv(STATE_SLICE_OUT, index=False)
    dispersion_slices.to_csv(DISPERSION_OUT, index=False)
    param_daily.to_csv(PARAM_DAILY_OUT, index=False)
    param_grid.to_csv(PARAM_GRID_OUT, index=False)
    dispersion_control.to_csv(DISPERSION_CONTROL_OUT, index=False)
    long_only_hedge.to_csv(LONG_ONLY_HEDGE_OUT, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "strategy": STRATEGY,
        "objective": "fourth-round benchmark/beta/residual alpha attribution",
        "meta": meta,
        "headline": {
            "strategy_net_cum_pct": float(benchmark.set_index("series").loc["strategy_net_4bps", "cum_pct"]),
            "btc_cum_pct": float(benchmark.set_index("series").loc["BTC buy-and-hold close-to-close", "cum_pct"]),
            "eligible_ew_cum_pct": float(benchmark.set_index("series").loc["Age90 eligible universe equal-weight", "cum_pct"]),
            "long_selection_excess_cum_pct": float(benchmark.set_index("series").loc["Long top3 minus eligible EW", "cum_pct"]),
            "short_selection_excess_cum_pct": float(benchmark.set_index("series").loc["Short bottom3 vs eligible EW", "cum_pct"]),
            "btc_beta": float(regression.set_index("factor").loc["BTC", "beta"]),
            "btc_corr": float(regression.set_index("factor").loc["BTC", "corr"]),
            "rolling_btc_beta_hedged_cum_pct": float(benchmark.set_index("series").loc["Rolling180 BTC beta-hedged net", "cum_pct"]),
        },
        "artifacts": {
            "daily": str(DAILY_OUT.relative_to(ROOT)),
            "benchmark_stats": str(BENCHMARK_OUT.relative_to(ROOT)),
            "regression_stats": str(REGRESSION_OUT.relative_to(ROOT)),
            "annual": str(ANNUAL_OUT.relative_to(ROOT)),
            "monthly": str(MONTHLY_OUT.relative_to(ROOT)),
            "conditional": str(CONDITIONAL_OUT.relative_to(ROOT)),
            "state_slices": str(STATE_SLICE_OUT.relative_to(ROOT)),
            "dispersion_slices": str(DISPERSION_OUT.relative_to(ROOT)),
            "param_stability_daily": str(PARAM_DAILY_OUT.relative_to(ROOT)),
            "param_stability_grid": str(PARAM_GRID_OUT.relative_to(ROOT)),
            "dispersion_position_control": str(DISPERSION_CONTROL_OUT.relative_to(ROOT)),
            "long_only_btc_hedge": str(LONG_ONLY_HEDGE_OUT.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
        "limitations": [
            "Top30 and eligible equal-weight benchmarks are close-to-close research benchmarks and do not include their own turnover costs.",
            "Rolling beta hedges are causal but still daily-bar approximations, not executable hedge simulations with funding/slippage.",
            "Same-day cross-sectional dispersion is diagnostic only; it is known after the holding period and cannot be used directly as an entry gate.",
            "This round diagnoses alpha source; it intentionally does not optimize new gates.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    SITE_PATH.write_text(
        build_report(
            daily,
            benchmark,
            regression,
            annual,
            monthly,
            conditional,
            state_slices,
            dispersion_slices,
            param_grid,
            dispersion_control,
            long_only_hedge,
            meta,
        ),
        encoding="utf-8",
    )
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
