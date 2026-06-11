#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from dataclasses import dataclass
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_age90_14d_fifth_round_profit_thickness.html"
FOURTH_SCRIPT_PATH = ROOT / "scripts" / "build_rank213_age90_14d_fourth_round_benchmark_attribution.py"

SUMMARY_PATH = ART_DIR / "rank213_age90_14d_fifth_round_profit_thickness_summary.json"
DAILY_OUT = ART_DIR / "rank213_age90_14d_fifth_round_profit_thickness_daily.csv"
RESULTS_OUT = ART_DIR / "rank213_age90_14d_fifth_round_profit_thickness_results.csv"
CANDIDATES_OUT = ART_DIR / "rank213_age90_14d_fifth_round_profit_thickness_candidates.csv"
FUNDING_OUT = ART_DIR / "rank213_age90_14d_fifth_round_funding_sensitivity.csv"
TOP50_REFERENCE_DAILY_PATH = ART_DIR / "rank213_age90_top50_4x4_execution_stability_daily.csv"

COST_GRID_BPS = [4.0, 8.0, 12.0, 16.0]
FUNDING_SENSITIVITY_BPS = [0.0, 1.0, 2.0, 3.0]
BASE_UNIVERSE_SIZE = 50
BASE_LEG_COUNT = 4
AGE_DAYS = 90
SAMPLE_START = pd.Timestamp("2020-02-01T00:00:00Z")


def load_fourth_module():
    spec = importlib.util.spec_from_file_location("rank213_fourth_round_mod", FOURTH_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {FOURTH_SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rank213_fourth_round_mod"] = mod
    spec.loader.exec_module(mod)
    return mod


fourth = load_fourth_module()


@dataclass(frozen=True)
class SignalSpec:
    name: str
    lookback_days: int = 14
    score_mode: str = "return_over_vol"
    universe_size: int = BASE_UNIVERSE_SIZE
    leg_count: int = BASE_LEG_COUNT


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


def sharpe(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    sd = float(ret.std(ddof=1))
    if len(ret) < 2 or sd <= 0:
        return np.nan
    return float(ret.mean() / sd * math.sqrt(365.0))


def parse_symbols(text: object) -> list[str]:
    if pd.isna(text):
        return []
    return [x.strip().upper() for x in str(text).split(",") if x.strip()]


def returns_for_weights(next_ret: pd.DataFrame, weights: dict[str, float], ts: pd.Timestamp) -> tuple[float, float, float, int, int]:
    long_ret = 0.0
    short_ret = 0.0
    long_count = 0
    short_count = 0
    if not weights or ts not in next_ret.index:
        return 0.0, 0.0, 0.0, 0, 0
    for sym, weight in weights.items():
        if sym not in next_ret.columns:
            continue
        raw_ret = pd.to_numeric(next_ret.at[ts, sym], errors="coerce")
        if not np.isfinite(raw_ret):
            continue
        contrib = weight * float(raw_ret)
        if weight > 0:
            long_ret += contrib
            long_count += 1
        elif weight < 0:
            short_ret += contrib
            short_count += 1
    return long_ret + short_ret, long_ret, short_ret, long_count, short_count


def turnover(prev: dict[str, float], cur: dict[str, float]) -> float:
    keys = set(prev) | set(cur)
    return float(sum(abs(cur.get(k, 0.0) - prev.get(k, 0.0)) for k in keys))


def eligible_for_day(universe: list[str], onboard_map: dict[str, pd.Timestamp], ts: pd.Timestamp) -> list[str]:
    return [
        sym for sym in universe
        if sym in onboard_map and ts - onboard_map[sym] >= pd.Timedelta(days=AGE_DAYS)
    ]


def build_score_panels(close: pd.DataFrame) -> dict[str, pd.DataFrame]:
    daily_ret = close.pct_change(fill_method=None)
    panels: dict[str, pd.DataFrame] = {}
    for lookback in [7, 14, 21]:
        mom = close.shift(1) / close.shift(lookback + 1) - 1.0
        vol = daily_ret.shift(1).rolling(lookback, min_periods=max(3, lookback // 2)).std().replace(0.0, np.nan)
        panels[f"retvol_{lookback}d_skip1d"] = (mom / vol).replace([np.inf, -np.inf], np.nan)
        if lookback == 14:
            downside = daily_ret.mask(daily_ret > 0.0, 0.0)
            dvol = downside.shift(1).rolling(lookback, min_periods=max(3, lookback // 2)).std().replace(0.0, np.nan)
            panels["downside_vol_14d_skip1d"] = (mom / dvol).replace([np.inf, -np.inf], np.nan)
            panels["raw_return_14d_skip1d"] = mom.replace([np.inf, -np.inf], np.nan)
            panels["retvol_14d_skip1d_top50_4x4"] = panels["retvol_14d_skip1d"]
    rank_parts = [
        panels["retvol_7d_skip1d"].rank(axis=1, pct=True),
        panels["retvol_14d_skip1d"].rank(axis=1, pct=True),
        panels["retvol_21d_skip1d"].rank(axis=1, pct=True),
    ]
    panels["rank_ensemble_7_14_21"] = sum(rank_parts) / len(rank_parts)
    return panels


def score_one(close: pd.DataFrame, ts: pd.Timestamp, eligible: list[str], spec: SignalSpec, score_panels: dict[str, pd.DataFrame] | None = None) -> pd.Series:
    if score_panels is not None and spec.name in score_panels and ts in score_panels[spec.name].index:
        cols = [sym for sym in eligible if sym in score_panels[spec.name].columns]
        if not cols:
            return pd.Series(dtype=float)
        return pd.to_numeric(score_panels[spec.name].loc[ts, cols], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()

    if spec.score_mode == "ensemble_7_14_21":
        pieces = []
        for lookback in [7, 14, 21]:
            s = score_one(close, ts, eligible, SignalSpec(f"tmp_{lookback}", lookback, "return_over_vol", spec.universe_size, spec.leg_count), score_panels)
            if not s.empty:
                pieces.append(s.rank(pct=True))
        if not pieces:
            return pd.Series(dtype=float)
        return pd.concat(pieces, axis=1).mean(axis=1).dropna()

    t0 = ts - pd.Timedelta(days=spec.lookback_days + 1)
    t1 = ts - pd.Timedelta(days=1)
    if t0 not in close.index or t1 not in close.index:
        return pd.Series(dtype=float)
    cols = [sym for sym in eligible if sym in close.columns]
    if not cols:
        return pd.Series(dtype=float)
    px0 = pd.to_numeric(close.loc[t0, cols], errors="coerce")
    px1 = pd.to_numeric(close.loc[t1, cols], errors="coerce")
    mom = px1 / px0 - 1.0
    if spec.score_mode == "raw_return":
        return mom.replace([np.inf, -np.inf], np.nan).dropna()

    hist = close.loc[t0:t1, cols].pct_change(fill_method=None).dropna(how="all")
    if spec.score_mode == "downside_vol":
        downside = hist.mask(hist > 0.0, 0.0)
        vol = downside.std().replace(0.0, np.nan)
    else:
        vol = hist.std().replace(0.0, np.nan)
    return (mom / vol).replace([np.inf, -np.inf], np.nan).dropna()


def weights_from_longs_shorts(longs: list[str], shorts: list[str], *, long_capital: float = 0.5, short_capital: float = 0.5) -> dict[str, float]:
    weights: dict[str, float] = {}
    if longs and long_capital > 0:
        w = long_capital / len(longs)
        for sym in longs:
            weights[sym] = weights.get(sym, 0.0) + w
    if shorts and short_capital > 0:
        w = -short_capital / len(shorts)
        for sym in shorts:
            weights[sym] = weights.get(sym, 0.0) + w
    return {k: v for k, v in weights.items() if abs(v) > 1e-12}


def desired_from_scores(scores: pd.Series, leg_count: int) -> tuple[list[str], list[str]]:
    scores = scores.dropna().sort_values()
    if len(scores) < leg_count * 2:
        return [], []
    shorts = scores.index[:leg_count].astype(str).tolist()
    longs = scores.index[-leg_count:].astype(str).tolist()[::-1]
    return longs, shorts


def apply_rank_buffer(prev: list[str], desired: list[str], rank_order: list[str], keep_zone: int) -> list[str]:
    rank_set = set(rank_order[:keep_zone])
    kept = [sym for sym in prev if sym in rank_set]
    out = kept[:]
    for sym in desired:
        if sym not in out:
            out.append(sym)
        if len(out) >= len(desired):
            break
    return out[:len(desired)]


def apply_replacement_cap(prev: list[str], desired: list[str], cap: int) -> list[str]:
    if not prev:
        return desired[:]
    kept = [sym for sym in prev if sym in desired]
    slots = max(0, len(desired) - len(kept))
    allowed = min(cap, slots)
    additions = [sym for sym in desired if sym not in kept][:allowed]
    out = kept + additions
    for sym in prev:
        if len(out) >= len(desired):
            break
        if sym not in out:
            out.append(sym)
    for sym in desired:
        if len(out) >= len(desired):
            break
        if sym not in out:
            out.append(sym)
    return out[:len(desired)]


def build_market_context(close: pd.DataFrame, ranked_by_month: dict[str, list[str]], onboard_map: dict[str, pd.Timestamp], dates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in dates.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        month = str(row["month"])
        top50 = ranked_by_month.get(month, [])[:BASE_UNIVERSE_SIZE]
        eligible = eligible_for_day(top50, onboard_map, ts)
        eret = fourth.returns_for_symbols(close, eligible, ts, exit_ts)
        btc_1d = fourth.returns_for_symbols(close, ["BTCUSDT"], ts, exit_ts)
        rows.append({
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
            "month": month,
            "btc_ret": float(btc_1d.iloc[0]) if len(btc_1d) else np.nan,
            "eligible_ew_ret": float(eret.mean()) if len(eret) else np.nan,
            "eligible_dispersion_p90_p10": float(np.percentile(eret, 90) - np.percentile(eret, 10)) if len(eret) else np.nan,
            "eligible_count_top50": int(len(eligible)),
        })
    ctx = pd.DataFrame(rows).sort_values("timestamp_ts").reset_index(drop=True)
    for col in ["btc_ret", "eligible_ew_ret"]:
        ctx[f"prior7_{col}"] = (1.0 + ctx[col].shift(1)).rolling(7, min_periods=5).apply(np.prod, raw=True) - 1.0
        ctx[f"prior30_{col}"] = (1.0 + ctx[col].shift(1)).rolling(30, min_periods=20).apply(np.prod, raw=True) - 1.0
    ctx["prior30_dispersion"] = ctx["eligible_dispersion_p90_p10"].shift(1).rolling(30, min_periods=20).mean()
    if "BTCUSDT" in close.columns:
        btc = pd.to_numeric(close["BTCUSDT"], errors="coerce")
        ctx = ctx.merge(
            pd.DataFrame({
                "timestamp_ts": close.index,
                "btc_above_ma20": btc > btc.shift(1).rolling(20, min_periods=15).mean(),
                "btc_above_ma50": btc > btc.shift(1).rolling(50, min_periods=35).mean(),
            }),
            on="timestamp_ts",
            how="left",
        )
    ctx["eligible_ew_above_ma20"] = ctx["eligible_ew_ret"].shift(1).rolling(5, min_periods=3).mean() > ctx["eligible_ew_ret"].shift(1).rolling(20, min_periods=15).mean()
    ctx["eligible_ew_above_ma50"] = ctx["eligible_ew_ret"].shift(1).rolling(10, min_periods=5).mean() > ctx["eligible_ew_ret"].shift(1).rolling(50, min_periods=35).mean()
    valid_disp = ctx["prior30_dispersion"].dropna()
    q33, q50, q67 = valid_disp.quantile([1 / 3, 0.5, 2 / 3]) if len(valid_disp) else (np.nan, np.nan, np.nan)
    ctx["prior30_dispersion_high"] = ctx["prior30_dispersion"] > q67
    ctx["prior30_dispersion_mid_high"] = ctx["prior30_dispersion"] > q33
    ctx["prior30_dispersion_low"] = ctx["prior30_dispersion"] <= q33
    ctx["prior30_dispersion_q33"] = q33
    ctx["prior30_dispersion_q50"] = q50
    ctx["prior30_dispersion_q67"] = q67
    return ctx


def gate_masks(ctx: pd.DataFrame) -> dict[str, pd.Series]:
    return {
        "short_every_day": pd.Series(True, index=ctx.index),
        "btc_prior7_positive": ctx["prior7_btc_ret"] > 0,
        "btc_prior7_negative": ctx["prior7_btc_ret"] < 0,
        "btc_prior30_positive": ctx["prior30_btc_ret"] > 0,
        "btc_above_ma20": ctx["btc_above_ma20"].fillna(False).astype(bool),
        "btc_above_ma50": ctx["btc_above_ma50"].fillna(False).astype(bool),
        "eligible_prior7_positive": ctx["prior7_eligible_ew_ret"] > 0,
        "eligible_prior7_negative": ctx["prior7_eligible_ew_ret"] < 0,
        "eligible_prior30_positive": ctx["prior30_eligible_ew_ret"] > 0,
        "eligible_ew_above_ma20": ctx["eligible_ew_above_ma20"].fillna(False).astype(bool),
        "eligible_ew_above_ma50": ctx["eligible_ew_above_ma50"].fillna(False).astype(bool),
        "prior30_dispersion_high": ctx["prior30_dispersion_high"].fillna(False).astype(bool),
        "prior30_dispersion_mid_high": ctx["prior30_dispersion_mid_high"].fillna(False).astype(bool),
    }


def add_reference_gate_context(ctx: pd.DataFrame) -> pd.DataFrame:
    if not TOP50_REFERENCE_DAILY_PATH.exists():
        return ctx
    ref = pd.read_csv(TOP50_REFERENCE_DAILY_PATH)
    ref["timestamp_ts"] = pd.to_datetime(ref["timestamp_ts"], utc=True, errors="coerce", format="mixed")
    keep_cols = [
        "timestamp_ts",
        "btc_ret",
        "top50_eligible_ew_ret",
        "top50_eligible_dispersion_p90_p10",
        "prior30_top50_dispersion",
    ]
    ref = ref[[c for c in keep_cols if c in ref.columns]].copy()
    out = ctx.merge(ref, on="timestamp_ts", how="left", suffixes=("", "_ref"))
    if "btc_ret_ref" in out.columns:
        out["btc_ret"] = pd.to_numeric(out["btc_ret_ref"], errors="coerce").combine_first(pd.to_numeric(out["btc_ret"], errors="coerce"))
    if "top50_eligible_ew_ret" in out.columns:
        out["eligible_ew_ret"] = pd.to_numeric(out["top50_eligible_ew_ret"], errors="coerce").combine_first(pd.to_numeric(out["eligible_ew_ret"], errors="coerce"))
    if "top50_eligible_dispersion_p90_p10" in out.columns:
        out["eligible_dispersion_p90_p10"] = pd.to_numeric(out["top50_eligible_dispersion_p90_p10"], errors="coerce").combine_first(pd.to_numeric(out["eligible_dispersion_p90_p10"], errors="coerce"))
    if "prior30_top50_dispersion" in out.columns:
        out["prior30_dispersion"] = pd.to_numeric(out["prior30_top50_dispersion"], errors="coerce").combine_first(pd.to_numeric(out["prior30_dispersion"], errors="coerce"))

    for col in ["btc_ret", "eligible_ew_ret"]:
        out[f"prior7_{col}"] = (1.0 + pd.to_numeric(out[col], errors="coerce").shift(1)).rolling(7, min_periods=5).apply(np.prod, raw=True) - 1.0
        out[f"prior30_{col}"] = (1.0 + pd.to_numeric(out[col], errors="coerce").shift(1)).rolling(30, min_periods=20).apply(np.prod, raw=True) - 1.0

    btc_proxy = (1.0 + pd.to_numeric(out["btc_ret"], errors="coerce").fillna(0.0)).cumprod().shift(1)
    eligible_proxy = (1.0 + pd.to_numeric(out["eligible_ew_ret"], errors="coerce").fillna(0.0)).cumprod().shift(1)
    out["btc_above_ma20"] = btc_proxy > btc_proxy.rolling(20, min_periods=15).mean()
    out["btc_above_ma50"] = btc_proxy > btc_proxy.rolling(50, min_periods=35).mean()
    out["eligible_ew_above_ma20"] = eligible_proxy > eligible_proxy.rolling(20, min_periods=15).mean()
    out["eligible_ew_above_ma50"] = eligible_proxy > eligible_proxy.rolling(50, min_periods=35).mean()

    valid_disp = out["prior30_dispersion"].dropna()
    if len(valid_disp):
        q33, q50, q67 = valid_disp.quantile([1 / 3, 0.5, 2 / 3])
        out["prior30_dispersion_high"] = out["prior30_dispersion"] > q67
        out["prior30_dispersion_mid_high"] = out["prior30_dispersion"] > q33
        out["prior30_dispersion_low"] = out["prior30_dispersion"] <= q33
        out["prior30_dispersion_q33"] = q33
        out["prior30_dispersion_q50"] = q50
        out["prior30_dispersion_q67"] = q67
    drop_cols = [c for c in out.columns if c.endswith("_ref") or c.startswith("top50_eligible_")]
    return out.drop(columns=drop_cols, errors="ignore")


def simulate_variant(
    *,
    close: pd.DataFrame,
    next_ret: pd.DataFrame,
    score_panels: dict[str, pd.DataFrame],
    ranked_by_month: dict[str, list[str]],
    onboard_map: dict[str, pd.Timestamp],
    ctx: pd.DataFrame,
    group: str,
    variant: str,
    signal_spec: SignalSpec,
    short_gate: pd.Series | None = None,
    rebalance_every_days: int = 1,
    rank_buffer_extra: int | None = None,
    replacement_cap: int | None = None,
    dynamic_universe_by_dispersion: bool = False,
) -> pd.DataFrame:
    rows = []
    prev_weights: dict[str, float] = {}
    prev_longs: list[str] = []
    prev_shorts: list[str] = []
    last_rebalance_i = -10**9

    short_gate = short_gate if short_gate is not None else pd.Series(True, index=ctx.index)

    for i, row in ctx.iterrows():
        ts = row["timestamp_ts"]
        exit_ts = row["exit_ts"]
        month = str(row["month"])
        universe_size = signal_spec.universe_size
        if dynamic_universe_by_dispersion:
            if bool(row.get("prior30_dispersion_high", False)):
                universe_size = 80
            elif bool(row.get("prior30_dispersion_low", False)):
                universe_size = 20
            else:
                universe_size = 50
        ranked_universe = ranked_by_month.get(month, [])[:universe_size]
        eligible = eligible_for_day(ranked_universe, onboard_map, ts)

        do_rebalance = (i - last_rebalance_i) >= rebalance_every_days or not prev_weights
        if do_rebalance:
            scores = score_one(close, ts, eligible, SignalSpec(signal_spec.name, signal_spec.lookback_days, signal_spec.score_mode, universe_size, signal_spec.leg_count), score_panels)
            desired_longs, desired_shorts = desired_from_scores(scores, signal_spec.leg_count)
            if desired_longs and desired_shorts:
                if rank_buffer_extra is not None and prev_longs and prev_shorts:
                    desc = scores.sort_values(ascending=False).index.astype(str).tolist()
                    asc = scores.sort_values(ascending=True).index.astype(str).tolist()
                    zone = signal_spec.leg_count + rank_buffer_extra
                    desired_longs = apply_rank_buffer(prev_longs, desired_longs, desc, zone)
                    desired_shorts = apply_rank_buffer(prev_shorts, desired_shorts, asc, zone)
                if replacement_cap is not None and prev_longs and prev_shorts:
                    desired_longs = apply_replacement_cap(prev_longs, desired_longs, replacement_cap)
                    desired_shorts = apply_replacement_cap(prev_shorts, desired_shorts, replacement_cap)
                prev_longs = desired_longs
                prev_shorts = desired_shorts
                last_rebalance_i = i
        gate_on = bool(short_gate.iloc[i]) if i < len(short_gate) else True
        cur_weights = weights_from_longs_shorts(prev_longs, prev_shorts if gate_on else [], long_capital=0.5, short_capital=0.5)
        active = bool(cur_weights)
        active_short = any(w < 0 for w in cur_weights.values())
        gross, long_contrib, short_contrib, long_count, short_count = returns_for_weights(next_ret, cur_weights, ts)
        t = turnover(prev_weights, cur_weights)
        rows.append({
            "experiment_group": group,
            "variant": variant,
            "timestamp_ts": ts,
            "exit_ts": exit_ts,
            "month": month,
            "universe_size": universe_size,
            "eligible_count": len(eligible),
            "active": active,
            "active_short": active_short,
            "gross_ret": gross if active else 0.0,
            "long_half_contribution": long_contrib if active else 0.0,
            "short_half_contribution": short_contrib if active_short else 0.0,
            "target_turnover_x": t,
            "long_count": long_count,
            "short_count": short_count,
            "longs": ",".join(prev_longs),
            "shorts": ",".join(prev_shorts if gate_on else []),
            "signal": signal_spec.name,
            "rebalance_every_days": rebalance_every_days,
            "rank_buffer_extra": rank_buffer_extra if rank_buffer_extra is not None else 0,
            "replacement_cap": replacement_cap if replacement_cap is not None else 0,
        })
        prev_weights = cur_weights
    return pd.DataFrame(rows)


def summarize_one(daily: pd.DataFrame, cost_bps: float, funding_credit_bps: float = 0.0) -> dict:
    gross = pd.to_numeric(daily["gross_ret"], errors="coerce").fillna(0.0)
    turn = pd.to_numeric(daily["target_turnover_x"], errors="coerce").fillna(0.0)
    active = daily["active"].fillna(False).astype(bool)
    active_short = daily["active_short"].fillna(False).astype(bool)
    funding_credit = funding_credit_bps / 10000.0 * active_short.astype(float)
    net = gross + funding_credit - cost_bps / 10000.0 * turn
    active_short_days = int(active_short.sum())
    return {
        "experiment_group": str(daily["experiment_group"].iloc[0]),
        "variant": str(daily["variant"].iloc[0]),
        "cost_bps_per_1x_turnover": cost_bps,
        "funding_credit_bps_per_short_active_day": funding_credit_bps,
        "days": int(len(daily)),
        "active_days": int(active.sum()),
        "active_short_days": active_short_days,
        "active_short_rate_pct": float(active_short.mean() * 100.0) if len(daily) else np.nan,
        "gross_mean_bps": float(gross.mean() * 10000.0),
        "net_mean_bps": float(net.mean() * 10000.0),
        "net_active_mean_bps": float(net[active].mean() * 10000.0) if active.sum() else np.nan,
        "net_cum_pct": float(compound(net) * 100.0),
        "max_drawdown_pct": float(max_drawdown(net) * 100.0),
        "sharpe": sharpe(net),
        "win_rate_pct": float((net > 0).mean() * 100.0) if len(net) else np.nan,
        "avg_turnover_x": float(turn.mean()),
        "active_avg_turnover_x": float(turn[active].mean()) if active.sum() else np.nan,
        "turnover_p95_x": float(turn.quantile(0.95)) if len(turn) else np.nan,
        "long_half_mean_bps": float(pd.to_numeric(daily["long_half_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "short_half_mean_bps": float(pd.to_numeric(daily["short_half_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0),
        "short_active_mean_bps": float(pd.to_numeric(daily.loc[active_short, "short_half_contribution"], errors="coerce").fillna(0.0).mean() * 10000.0) if active_short_days else np.nan,
        "avg_universe_size": float(pd.to_numeric(daily["universe_size"], errors="coerce").mean()),
        "avg_eligible_count": float(pd.to_numeric(daily["eligible_count"], errors="coerce").mean()),
    }


def classify(row: pd.Series) -> tuple[str, str]:
    if row["funding_credit_bps_per_short_active_day"] > 0:
        if row["net_mean_bps"] > 0 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -55:
            return "Watch", "funding sensitivity only; not treated as real PnL"
        return "Fail", "funding sensitivity still does not clear 12bps"
    if row["net_mean_bps"] > 5 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -35 and row["sharpe"] >= 0.75 and row["avg_turnover_x"] <= 1.0:
        return "Pass", "positive at 12bps with controlled drawdown and lower turnover"
    if row["net_mean_bps"] > 0 and row["net_cum_pct"] > 0 and row["max_drawdown_pct"] > -55 and row["avg_turnover_x"] <= 1.5:
        return "Watch", "positive at 12bps, but drawdown/turnover still needs execution proof"
    return "Fail", "does not clear positive 12bps net with acceptable drawdown/turnover"


def table_html(df: pd.DataFrame, cols: list[str], max_rows: int | None = None) -> str:
    view = df[cols].copy()
    if max_rows is not None:
        view = view.head(max_rows)
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = []
    for _, row in view.iterrows():
        cells = []
        for c in cols:
            v = row.get(c, "")
            if c.endswith("_pct") or c in {"net_cum_pct", "max_drawdown_pct", "win_rate_pct", "active_short_rate_pct"}:
                txt = fmt_pct(v)
            elif c.endswith("_bps") or c in {"gross_mean_bps", "net_mean_bps", "long_half_mean_bps", "short_half_mean_bps", "short_active_mean_bps"}:
                txt = fmt_bps(v)
            elif isinstance(v, float):
                txt = fmt_num(v, 3)
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_report(results: pd.DataFrame, candidates: pd.DataFrame, funding: pd.DataFrame, summary: dict) -> str:
    generated = summary["generated_at_utc"].replace("T", " ").replace("Z", " UTC")
    cost12 = results[(results["cost_bps_per_1x_turnover"] == 12.0) & (results["funding_credit_bps_per_short_active_day"] == 0.0)].copy()
    top_watch = cost12.sort_values(["verdict_rank", "net_mean_bps"], ascending=[True, False]).head(24)
    best_candidate = candidates.iloc[0]
    base = cost12[(cost12["experiment_group"] == "short_gate") & (cost12["variant"] == "short_every_day")].iloc[0]
    best_short_gate = cost12[cost12["experiment_group"] == "short_gate"].sort_values("net_mean_bps", ascending=False).iloc[0]
    best_turnover = cost12[cost12["experiment_group"] == "turnover_reduction"].sort_values("net_mean_bps", ascending=False).iloc[0]
    best_signal = cost12[cost12["experiment_group"] == "signal_variant"].sort_values("net_mean_bps", ascending=False).iloc[0]
    best_universe = cost12[cost12["experiment_group"] == "dynamic_universe"].sort_values("net_mean_bps", ascending=False).iloc[0]
    funding12 = funding[funding["cost_bps_per_1x_turnover"] == 12.0].sort_values("funding_credit_bps_per_short_active_day")
    funding3 = funding12[funding12["funding_credit_bps_per_short_active_day"] == 3.0].iloc[0]
    cols = [
        "verdict", "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe",
        "avg_turnover_x", "active_short_days", "gross_mean_bps", "long_half_mean_bps", "short_half_mean_bps",
    ]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 / 213c 第五轮：利润厚度</title>
  <style>
    body {{ margin:0; background:#f6f3ec; color:#172033; font-family:"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei",sans-serif; line-height:1.62; }}
    main {{ max-width:1220px; margin:0 auto; padding:28px 16px 56px; }}
    .card {{ background:white; border:1px solid #e6dccb; border-radius:14px; padding:18px 20px; margin:14px 0; }}
    .hero {{ border-color:#0f766e; background:#f0fdfa; }}
    .warn {{ background:#fff7ed; border-color:#fdba74; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .metric {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:12px; }}
    .metric b {{ display:block; font-size:22px; line-height:1.2; }}
    .muted {{ color:#64748b; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ border-collapse:collapse; min-width:1120px; width:100%; }}
    th,td {{ border-bottom:1px solid #e2e8f0; padding:8px 10px; text-align:right; vertical-align:top; font-size:13px; }}
    th {{ background:#f8fafc; color:#475569; }}
    td:first-child,th:first-child,td:nth-child(2),th:nth-child(2),td:nth-child(3),th:nth-child(3) {{ text-align:left; }}
    code {{ background:#f1f5f9; border-radius:6px; padding:2px 6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    @media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
<main>
  <section class="card hero">
    <h1>Rank213 / 213c 第五轮：真实成本下利润厚度</h1>
    <p>对象：<code>rank213_age90_14d_skip1d_voladj</code> / 213c family。样本使用 monthly-volume causal universe、age≥90d、daily next-day hold，不重新下载行情。</p>
    <p class="muted">生成时间：{escape(generated)}。成本表统一为 <code>cost_bps_per_1x_turnover</code>，覆盖 4/8/12/16bps；funding 只做 sensitivity，不计作真实收益。</p>
    <p><a href="/momentum/paper/rank213_version_overview.html">Rank213 版本总览</a> · <a href="/momentum/paper/rank213_age90_top50_4x4_execution_stability.html">Top50 4x4 第四轮扩展</a> · <a href="/momentum/paper/rank213_age90_14d_fourth_round_benchmark_attribution.html">第四轮归因</a></p>
  </section>

  <section class="card warn">
    <h2>结论</h2>
    <p><b>第五轮没有找到可以直接 Pass 的候选。</b> 基准 daily short_every_day 在 12bps/1x turnover 后为 {fmt_bps(base['net_mean_bps'])}，累计 {fmt_pct(base['net_cum_pct'])}，最大回撤 {fmt_pct(base['max_drawdown_pct'])}。它说明第四轮 flat 12bps 的表观余量，落到换手成本口径后并不够厚。</p>
    <p>唯一 Watch 是 <code>{escape(str(best_candidate['variant']))}</code>：12bps 后日均 {fmt_bps(best_candidate['net_mean_bps'])}，累计 {fmt_pct(best_candidate['net_cum_pct'])}，换手 {fmt_num(best_candidate['avg_turnover_x'])}x/day，但最大回撤仍有 {fmt_pct(best_candidate['max_drawdown_pct'])}，不能作为放大 notional 的依据。</p>
    <p>本轮最有用的方向是：rank buffer / 慢 rebalance / 持仓 carry 这类低换手结构。short gate 能改善部分均值，但回撤没有被压住；prior30 dispersion 仍更适合解释和监控，不适合作为主交易开关。</p>
  </section>

  <section class="card">
    <h2>给新研究者的读法</h2>
    <ul>
      <li><b>本页回答的问题：</b>如果把 213c 放到更接近实盘的换手成本口径，策略还有没有足够利润厚度。</li>
      <li><b>先看 12bps 候选筛选。</b> Pass 表示可以进入下一轮严格验证，Watch 表示有研究价值但不能上线放大，Fail 表示当前形态不值得继续。</li>
      <li><b>不要只看日均 bps。</b> 还要同时看累计收益、最大回撤、换手率和 active_short_days。一个变体均值变高但回撤扩大，通常不能算进步。</li>
      <li><b>funding sensitivity 只是敏感性。</b> 它不是已经确认的真实收益，不能拿来抵消 12bps 成本压力。</li>
      <li><b>本页最重要的结论：</b>213c 的下一轮优化应该优先降低换手和重构 short leg，而不是继续扩大参数网格。</li>
    </ul>
  </section>

  <section class="card">
    <h2>核心读数</h2>
    <div class="grid">
      <div class="metric"><b>{fmt_bps(base['net_mean_bps'])}</b><span>基准 12bps 日均</span></div>
      <div class="metric"><b>{fmt_bps(best_candidate['net_mean_bps'])}</b><span>唯一 Watch 12bps 日均</span></div>
      <div class="metric"><b>{fmt_num(best_candidate['avg_turnover_x'])}x</b><span>唯一 Watch 平均换手</span></div>
      <div class="metric"><b>{int(summary['pass_count_12bps'])} / {int(summary['watch_count_12bps'])} / {int(summary['fail_count_12bps'])}</b><span>Pass / Watch / Fail</span></div>
    </div>
  </section>

  <section class="card">
    <h2>12bps 候选筛选</h2>
    <div class="table-wrap">{table_html(candidates, ["verdict", "experiment_group", "variant", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe", "avg_turnover_x", "active_short_days", "reason"])}</div>
    <p class="muted">筛选规则偏保守：必须在 12bps 后为正，同时回撤和换手不能太差；funding sensitivity 不参与真实候选排序。</p>
  </section>

  <section class="card">
    <h2>12bps 全部实验 Top 24</h2>
    <div class="table-wrap">{table_html(top_watch, cols)}</div>
  </section>

  <section class="card">
    <h2>Short Leg 条件化</h2>
    <p class="muted">long half 每天保留；short gate OFF 时 short half 空仓。表中 active_short_days 是实际做空天数。</p>
    <p>最好的 short gate 是 <code>{escape(str(best_short_gate['variant']))}</code>：active short days {int(best_short_gate['active_short_days'])}，short half 日均 {fmt_bps(best_short_gate['short_half_mean_bps'])}，12bps 后组合日均 {fmt_bps(best_short_gate['net_mean_bps'])}，但累计仍为 {fmt_pct(best_short_gate['net_cum_pct'])}、最大回撤 {fmt_pct(best_short_gate['max_drawdown_pct'])}。推论是：short 条件化能减少坏 short，但它没有解决组合路径风险。</p>
    <div class="table-wrap">{table_html(cost12[cost12["experiment_group"] == "short_gate"].sort_values("net_mean_bps", ascending=False), cols)}</div>
  </section>

  <section class="card">
    <h2>降换手增厚</h2>
    <p>这组是本轮唯一有正向可用信息的方向。最强均值来自 <code>{escape(str(best_turnover['variant']))}</code>，12bps 后 {fmt_bps(best_turnover['net_mean_bps'])}，平均换手 {fmt_num(best_turnover['avg_turnover_x'])}x/day；但它最大回撤 {fmt_pct(best_turnover['max_drawdown_pct'])}。唯一 Watch 的 <code>{escape(str(best_candidate['variant']))}</code> 稍弱但回撤更低，说明“少换一点、让持仓有惯性”比“每天完全追 rank”更接近真实成本下可活的形态。</p>
    <div class="table-wrap">{table_html(cost12[cost12["experiment_group"] == "turnover_reduction"].sort_values("net_mean_bps", ascending=False), cols)}</div>
  </section>

  <section class="card">
    <h2>信号小范围优化</h2>
    <p>信号微调没有稳定增厚。最好的 <code>{escape(str(best_signal['variant']))}</code> 在 12bps 后只有 {fmt_bps(best_signal['net_mean_bps'])}，其余 7d、ensemble、downside vol、raw return 都更差。推论是：当前问题不是再找一个更锋利的 return-vol 变体，而是成本、换手和 short-leg 结构。</p>
    <div class="table-wrap">{table_html(cost12[cost12["experiment_group"] == "signal_variant"].sort_values("net_mean_bps", ascending=False), cols)}</div>
  </section>

  <section class="card">
    <h2>Dynamic Universe</h2>
    <p>静态 <code>{escape(str(best_universe['variant']))}</code> 是 universe 组里最不差的版本，12bps 后 {fmt_bps(best_universe['net_mean_bps'])}、最大回撤 {fmt_pct(best_universe['max_drawdown_pct'])}。Top80 和 dispersion-driven low20/mid50/high80 都更差，说明扩大池子不是免费增厚，容易把小币暴露和 short 噪声一起放大。</p>
    <div class="table-wrap">{table_html(cost12[cost12["experiment_group"] == "dynamic_universe"].sort_values("net_mean_bps", ascending=False), cols + ["avg_universe_size", "avg_eligible_count"])}</div>
  </section>

  <section class="card">
    <h2>Funding Sensitivity</h2>
    <p>没有在当前 monthly-volume age90 Top50 逐日样本里发现可直接对齐每条 short leg 的完整 funding 序列；本节只把 short active day 加 0/+1/+2/+3bps/day 做敏感性，不作为真实 PnL。即使 +3bps/day，12bps 后也只有 {fmt_bps(funding3['net_mean_bps'])}，累计仍为 {fmt_pct(funding3['net_cum_pct'])}，因此 funding 不能被当作这轮 cover 12bps 的主答案。</p>
    <div class="table-wrap">{table_html(funding.sort_values(["funding_credit_bps_per_short_active_day", "cost_bps_per_1x_turnover"]), ["variant", "cost_bps_per_1x_turnover", "funding_credit_bps_per_short_active_day", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "sharpe", "avg_turnover_x", "active_short_days"])}</div>
  </section>

  <section class="card">
    <h2>推论与操作建议</h2>
    <ul>
      <li><b>不要把 213c 直接放大。</b> 换手成本口径下，基准 12bps 后已经转负；唯一 Watch 也有接近 50% 的历史回撤。</li>
      <li><b>下一轮若继续研究，只围绕低换手结构。</b> rank buffer、持仓 carry、rebalance 7d 是这轮唯一能同时保留正均值和降低成本的方向。</li>
      <li><b>short leg 不应简单每日满配。</b> BTC prior7 positive / BTC MA20 这类 gate 有改善均值的迹象，但路径仍差；更合理的是把 short 作为风控/机会模块，而不是强制 0.5 capital 每天开。</li>
      <li><b>dispersion 继续做监控，不做主开关。</b> prior30 dispersion high 只把 short active days 降到 756，12bps 后仍累计为负；它解释收益环境，但不足以因果增厚。</li>
      <li><b>实盘 canary 的任务更明确。</b> 重点收集真实 maker fill、taker fallback、exit slippage、funding 和 live-vs-shadow drift，用真实成本替换本页的 12bps 假设。</li>
    </ul>
  </section>

  <section class="card">
    <h2>产物</h2>
    <ul>
      <li><code>{escape(str(RESULTS_OUT.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(DAILY_OUT.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(CANDIDATES_OUT.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(SUMMARY_PATH.relative_to(ROOT)))}</code></li>
    </ul>
  </section>
</main>
</body>
</html>
"""


def main() -> int:
    close, quote_volume = fourth.load_close_quote_panels()
    close = close[close.index >= SAMPLE_START - pd.Timedelta(days=45)].copy()
    next_ret = (close.shift(-1) / close - 1.0).replace([np.inf, -np.inf], np.nan)
    score_panels = build_score_panels(close)
    onboard_map = fourth.read_onboard_map()

    months = sorted({ts.strftime("%Y-%m") for ts in close.index[close.index >= SAMPLE_START]})
    ranked_by_month = fourth.build_monthly_ranked_universes(months, quote_volume, onboard_map, 100)
    dates = pd.DataFrame({
        "timestamp_ts": [ts for ts in close.index if ts >= SAMPLE_START and ts + pd.Timedelta(days=1) in close.index],
    })
    dates["exit_ts"] = dates["timestamp_ts"] + pd.Timedelta(days=1)
    dates["month"] = dates["timestamp_ts"].dt.strftime("%Y-%m")
    ctx = build_market_context(close, ranked_by_month, onboard_map, dates)
    ctx = add_reference_gate_context(ctx)

    base_spec = SignalSpec("retvol_14d_skip1d_top50_4x4", 14, "return_over_vol", 50, 4)
    variants: list[pd.DataFrame] = []

    for gate_name, mask in gate_masks(ctx).items():
        variants.append(simulate_variant(
            close=close,
            next_ret=next_ret,
            score_panels=score_panels,
            ranked_by_month=ranked_by_month,
            onboard_map=onboard_map,
            ctx=ctx,
            group="short_gate",
            variant=gate_name,
            signal_spec=base_spec,
            short_gate=mask,
        ))

    for extra in [2, 4, 8]:
        variants.append(simulate_variant(
            close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
            group="turnover_reduction", variant=f"rank_buffer_extra_{extra}", signal_spec=base_spec, rank_buffer_extra=extra,
        ))
    for days in [2, 3, 7]:
        variants.append(simulate_variant(
            close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
            group="turnover_reduction", variant=f"rebalance_every_{days}d", signal_spec=base_spec, rebalance_every_days=days,
        ))
    for cap in [1, 2]:
        variants.append(simulate_variant(
            close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
            group="turnover_reduction", variant=f"replacement_cap_{cap}_per_side", signal_spec=base_spec, replacement_cap=cap,
        ))

    signal_specs = [
        SignalSpec("retvol_7d_skip1d", 7, "return_over_vol", 50, 4),
        SignalSpec("retvol_14d_skip1d", 14, "return_over_vol", 50, 4),
        SignalSpec("retvol_21d_skip1d", 21, "return_over_vol", 50, 4),
        SignalSpec("rank_ensemble_7_14_21", 14, "ensemble_7_14_21", 50, 4),
        SignalSpec("downside_vol_14d_skip1d", 14, "downside_vol", 50, 4),
        SignalSpec("raw_return_14d_skip1d", 14, "raw_return", 50, 4),
    ]
    for spec in signal_specs:
        variants.append(simulate_variant(
            close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
            group="signal_variant", variant=spec.name, signal_spec=spec,
        ))

    for n in [20, 30, 50, 80]:
        spec = SignalSpec(f"static_top{n}_4x4", 14, "return_over_vol", n, 4)
        variants.append(simulate_variant(
            close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
            group="dynamic_universe", variant=f"static_top{n}", signal_spec=spec,
        ))
    variants.append(simulate_variant(
        close=close, next_ret=next_ret, score_panels=score_panels, ranked_by_month=ranked_by_month, onboard_map=onboard_map, ctx=ctx,
        group="dynamic_universe", variant="prior30_dispersion_low20_mid50_high80", signal_spec=base_spec,
        dynamic_universe_by_dispersion=True,
    ))

    daily = pd.concat(variants, ignore_index=True)
    daily.to_csv(DAILY_OUT, index=False)

    rows = []
    for (_, variant), sub in daily.groupby(["experiment_group", "variant"], sort=False):
        for cost in COST_GRID_BPS:
            rows.append(summarize_one(sub, cost, 0.0))
    results = pd.DataFrame(rows)

    funding_rows = []
    base_daily = daily[(daily["experiment_group"] == "short_gate") & (daily["variant"] == "short_every_day")].copy()
    for credit in FUNDING_SENSITIVITY_BPS:
        for cost in COST_GRID_BPS:
            funding_rows.append(summarize_one(base_daily, cost, credit))
    funding = pd.DataFrame(funding_rows)
    funding.to_csv(FUNDING_OUT, index=False)

    verdicts = []
    cost12_mask = (results["cost_bps_per_1x_turnover"] == 12.0) & (results["funding_credit_bps_per_short_active_day"] == 0.0)
    for idx, row in results.loc[cost12_mask].iterrows():
        verdict, reason = classify(row)
        verdicts.append((idx, verdict, reason))
    results["verdict"] = ""
    results["reason"] = ""
    for idx, verdict, reason in verdicts:
        results.loc[idx, "verdict"] = verdict
        results.loc[idx, "reason"] = reason
    rank_map = {"Pass": 0, "Watch": 1, "Fail": 2, "": 3}
    results["verdict_rank"] = results["verdict"].map(rank_map).fillna(3).astype(int)

    candidates = results.loc[cost12_mask].copy().sort_values(["verdict_rank", "net_mean_bps"], ascending=[True, False])
    candidates.to_csv(CANDIDATES_OUT, index=False)
    results.to_csv(RESULTS_OUT, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "objective": "fifth round profit thickness: short gating, turnover reduction, signal variants, funding sensitivity, dynamic universe",
        "sample_start": dates["timestamp_ts"].min().strftime("%Y-%m-%d"),
        "sample_end": dates["exit_ts"].max().strftime("%Y-%m-%d"),
        "cost_model": "net = gross + funding_sensitivity - cost_bps_per_1x_turnover * target_turnover_x",
        "cost_grid_bps": COST_GRID_BPS,
        "funding_data_status": "no complete per-leg funding alignment for monthly-volume age90 top50 daily sample; sensitivity only",
        "variant_count": int(daily[["experiment_group", "variant"]].drop_duplicates().shape[0]),
        "pass_count_12bps": int((candidates["verdict"] == "Pass").sum()),
        "watch_count_12bps": int((candidates["verdict"] == "Watch").sum()),
        "fail_count_12bps": int((candidates["verdict"] == "Fail").sum()),
        "artifacts": {
            "daily": str(DAILY_OUT.relative_to(ROOT)),
            "results": str(RESULTS_OUT.relative_to(ROOT)),
            "candidates": str(CANDIDATES_OUT.relative_to(ROOT)),
            "funding_sensitivity": str(FUNDING_OUT.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SITE_PATH.write_text(build_report(results, candidates, funding, summary), encoding="utf-8")

    print(f"wrote {RESULTS_OUT.relative_to(ROOT)}")
    print(f"wrote {CANDIDATES_OUT.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_PATH.relative_to(ROOT)}")
    print(f"wrote {SITE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
