#!/usr/bin/env python3
"""Strict backtest for rank154b young-coin funding continuation.

Spec v0:
- Causal universe: Binance archive daily panel, no current ticker prefilter.
- Listing age: 180 <= listing_days < 365 by first observed archive daily kline proxy.
- Liquidity: same-date trailing 30d quote volume TopN.
- Signal: high funding_rate_last = long crowding/attention continuation.
- Variants: long_short high-vs-low funding and long_only high funding.
- Rebalance: daily full rebalance and 5d staggered overlapping buckets.
- PnL: close-to-close price return plus realized next-day funding sum; long pays positive funding.
- Costs: turnover * cost_bps / 10000, cost_bps interpreted as per-side notional turnover haircut.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PANEL_PATH = ROOT / "reports" / "artifacts" / "rank154_long_history" / "daily_panel.pkl"
ART_DIR = ROOT / "reports" / "artifacts" / "rank154b_young_funding_backtest"
INITIAL_EQUITY = 10_000.0

SideMode = Literal["long_short", "long_only"]
RebalanceMode = Literal["daily", "staggered"]


@dataclass(frozen=True)
class Config:
    name: str
    age_min: int = 180
    age_max: int = 365
    universe_size: int = 30
    sleeve_frac: float = 0.20
    mode: SideMode = "long_short"
    rebalance: RebalanceMode = "staggered"
    hold_days: int = 5
    cost_bps: float = 20.0
    max_abs_weight: float = 0.10
    funding_clip_abs: float | None = 0.02  # 2% daily funding cap guard; normally inactive


def _date(s: str) -> pd.Timestamp:
    return pd.Timestamp(s, tz="UTC")


def load_panel() -> pd.DataFrame:
    if not PANEL_PATH.exists():
        raise SystemExit(f"missing panel: {PANEL_PATH}")
    panel = pd.read_pickle(PANEL_PATH).sort_values(["date", "symbol"]).reset_index(drop=True)
    return panel


def build_signal(day: pd.DataFrame, cfg: Config, scale: float = 1.0) -> dict[str, float]:
    u = day[
        day["is_eligible"]
        & (day["listing_days"] >= cfg.age_min)
        & (day["listing_days"] < cfg.age_max)
        & day["trail_quote_volume_30d"].notna()
        & day["carry_raw"].notna()
    ].copy()
    u = u.sort_values(["trail_quote_volume_30d", "quote_volume"], ascending=False).head(cfg.universe_size)
    if len(u) < max(8, min(15, cfg.universe_size // 2)):
        return {}
    k = max(2, int(round(len(u) * cfg.sleeve_frac)))
    long_syms = u.nlargest(k, "carry_raw")["symbol"].tolist()
    weights: dict[str, float] = {}
    if cfg.mode == "long_only":
        w = scale / len(long_syms)
        weights = {s: min(cfg.max_abs_weight, w) for s in long_syms}
        # Renormalize after cap to use intended gross when possible.
        gross = sum(abs(x) for x in weights.values())
        if gross > 0 and gross < scale:
            weights = {s: x * scale / gross for s, x in weights.items()}
    else:
        short_syms = u.nsmallest(k, "carry_raw")["symbol"].tolist()
        lw = 0.5 * scale / len(long_syms)
        sw = -0.5 * scale / len(short_syms)
        weights.update({s: max(-cfg.max_abs_weight, min(cfg.max_abs_weight, lw)) for s in long_syms})
        weights.update({s: max(-cfg.max_abs_weight, min(cfg.max_abs_weight, sw)) for s in short_syms})
        gross = sum(abs(x) for x in weights.values())
        if gross > 0 and gross < scale:
            weights = {s: x * scale / gross for s, x in weights.items()}
    return {s: float(w) for s, w in weights.items() if abs(w) > 1e-12}


def combine_buckets(buckets: list[tuple[int, dict[str, float]]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for _, wmap in buckets:
        for s, w in wmap.items():
            out[s] = out.get(s, 0.0) + w
    return {s: w for s, w in out.items() if abs(w) > 1e-12}


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1.0).min())


def run_backtest(panel: pd.DataFrame, cfg: Config, start: str, end: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = panel[(panel["date"] >= _date(start)) & (panel["date"] <= _date(end))].copy()
    by_date = {d: df for d, df in p.groupby("date", sort=True)}
    dates = sorted(by_date.keys())
    if len(dates) < 10:
        return pd.DataFrame(), pd.DataFrame()

    equity = INITIAL_EQUITY
    rows = []
    trades = []
    buckets: list[tuple[int, dict[str, float]]] = []
    old_weights: dict[str, float] = {}
    peak = equity
    scale = 1.0 if cfg.rebalance == "daily" else 1.0 / max(1, cfg.hold_days)
    effective_hold = 1 if cfg.rebalance == "daily" else cfg.hold_days

    for i in range(len(dates) - 1):
        d, nd = dates[i], dates[i + 1]
        day = by_date[d]
        today_px = day.set_index("symbol")["close"]
        nxt = by_date[nd].set_index("symbol")

        # Expire buckets before opening new positions for d->nd.
        if cfg.rebalance == "daily":
            buckets = []
        else:
            buckets = [(expiry, w) for expiry, w in buckets if expiry > i]
        signal = build_signal(day, cfg, scale=scale)
        if signal:
            buckets.append((i + effective_hold, signal))
        weights = combine_buckets(buckets)

        symbols = set(old_weights) | set(weights)
        turnover = sum(abs(weights.get(s, 0.0) - old_weights.get(s, 0.0)) for s in symbols)
        commission = equity * turnover * cfg.cost_bps / 10000.0
        equity_after_cost = max(0.0, equity - commission)

        price_ret = 0.0
        funding_ret = 0.0
        long_gross = 0.0
        short_gross = 0.0
        missing = 0
        for sym, w in weights.items():
            if sym not in today_px.index or sym not in nxt.index:
                missing += 1
                continue
            close0 = float(today_px.loc[sym])
            close1 = float(nxt.loc[sym, "close"])
            if close0 <= 0 or not math.isfinite(close0) or not math.isfinite(close1):
                missing += 1
                continue
            r = close1 / close0 - 1.0
            fr = float(nxt.loc[sym, "funding_rate_sum"]) if "funding_rate_sum" in nxt.columns else 0.0
            if cfg.funding_clip_abs is not None:
                fr = float(np.clip(fr, -cfg.funding_clip_abs, cfg.funding_clip_abs))
            price_ret += w * r
            funding_ret += -w * fr  # positive funding: longs pay, shorts receive
            if w > 0:
                long_gross += abs(w)
            elif w < 0:
                short_gross += abs(w)

        gross_ret = price_ret + funding_ret
        prev_equity = equity
        equity = equity_after_cost * (1.0 + gross_ret)
        peak = max(peak, equity)
        daily_return = equity / prev_equity - 1.0 if prev_equity else 0.0
        row = {
            "date": str(nd.date()),
            "signal_date": str(d.date()),
            "config": cfg.name,
            "equity": equity,
            "daily_return": daily_return,
            "gross_return_before_cost": gross_ret,
            "price_return": price_ret,
            "funding_return": funding_ret,
            "commission": commission,
            "commission_return": -commission / prev_equity if prev_equity else 0.0,
            "turnover": turnover,
            "n_positions": len(weights),
            "long_gross": long_gross,
            "short_gross": short_gross,
            "net_weight": sum(weights.values()),
            "gross_weight": sum(abs(w) for w in weights.values()),
            "missing_positions": missing,
            "drawdown": equity / peak - 1.0,
            "eligible_young": int(day[
                day["is_eligible"]
                & (day["listing_days"] >= cfg.age_min)
                & (day["listing_days"] < cfg.age_max)
            ].shape[0]),
        }
        rows.append(row)
        # compact trade ledger: only non-zero changes
        for sym in sorted(symbols):
            delta = weights.get(sym, 0.0) - old_weights.get(sym, 0.0)
            if abs(delta) > 1e-9:
                trades.append({
                    "date": str(d.date()), "config": cfg.name, "symbol": sym,
                    "old_weight": old_weights.get(sym, 0.0), "new_weight": weights.get(sym, 0.0),
                    "delta_weight": delta, "equity_before": prev_equity,
                    "notional_delta": prev_equity * delta, "cost": abs(delta) * prev_equity * cfg.cost_bps / 10000.0,
                })
        old_weights = weights
    return pd.DataFrame(rows), pd.DataFrame(trades)


def perf_stats(eq: pd.DataFrame, initial: float = INITIAL_EQUITY) -> dict:
    if eq.empty or len(eq) < 3:
        return {"days": int(len(eq))}
    r = eq["daily_return"].astype(float)
    years = len(eq) / 365.25
    total = float(eq["equity"].iloc[-1] / initial - 1.0)
    ann = float((eq["equity"].iloc[-1] / initial) ** (1 / years) - 1) if years > 0 and eq["equity"].iloc[-1] > 0 else np.nan
    return {
        "days": int(len(eq)),
        "start": str(eq["date"].iloc[0]),
        "end": str(eq["date"].iloc[-1]),
        "return": total,
        "ann_return": ann,
        "max_dd": max_drawdown(eq["equity"]),
        "sharpe": float(r.mean() / r.std(ddof=1) * math.sqrt(365.25)) if r.std(ddof=1) > 0 else 0.0,
        "win_rate": float((r > 0).mean()),
        "avg_daily_return": float(r.mean()),
        "daily_vol": float(r.std(ddof=1)),
        "avg_turnover": float(eq["turnover"].mean()),
        "total_turnover": float(eq["turnover"].sum()),
        "commission": float(eq["commission"].sum()),
        "price_return_sum": float(eq["price_return"].sum()),
        "funding_return_sum": float(eq["funding_return"].sum()),
        "commission_return_sum": float(eq["commission_return"].sum()),
        "median_positions": float(eq["n_positions"].median()),
        "avg_gross_weight": float(eq["gross_weight"].mean()),
        "avg_long_gross": float(eq["long_gross"].mean()),
        "avg_short_gross": float(eq["short_gross"].mean()),
        "missing_position_days": int((eq["missing_positions"] > 0).sum()),
    }


def period_breakdown(eq: pd.DataFrame, freq: str) -> pd.DataFrame:
    if eq.empty:
        return pd.DataFrame()
    x = eq.copy()
    x["date_ts"] = pd.to_datetime(x["date"], utc=True)
    x["period"] = x["date_ts"].dt.to_period(freq).astype(str)
    rows = []
    for p, g in x.groupby("period", sort=True):
        rows.append({
            "period": p,
            "days": int(len(g)),
            "return": float(g["equity"].iloc[-1] / g["equity"].iloc[0] - 1.0),
            "max_dd": max_drawdown(g["equity"]),
            "avg_turnover": float(g["turnover"].mean()),
            "price_return_sum": float(g["price_return"].sum()),
            "funding_return_sum": float(g["funding_return"].sum()),
            "commission_return_sum": float(g["commission_return"].sum()),
        })
    return pd.DataFrame(rows)


def rolling_windows(eq: pd.DataFrame, window: int = 180, step: int = 30) -> pd.DataFrame:
    rows = []
    if len(eq) < window:
        return pd.DataFrame()
    for i in range(0, len(eq) - window + 1, step):
        g = eq.iloc[i:i + window]
        st = perf_stats(g, initial=float(g["equity"].iloc[0]))
        rows.append({"start": g["date"].iloc[0], "end": g["date"].iloc[-1], **st})
    return pd.DataFrame(rows)


def config_grid() -> list[Config]:
    cfgs: list[Config] = []
    for mode in ["long_short", "long_only"]:
        for reb in ["daily", "staggered"]:
            for cost in [0, 10, 20, 30, 50]:
                hold = 1 if reb == "daily" else 5
                cfgs.append(Config(
                    name=f"154b_{mode}_{reb}_h{hold}_cost{cost}",
                    mode=mode, rebalance=reb, hold_days=hold, cost_bps=float(cost),
                ))
    # old-coin placebo and wider age checks for core cost=20 staggered long_short
    cfgs.extend([
        Config(name="154b_placebo_old3y_long_short_staggered_h5_cost20", age_min=1095, age_max=10_000, mode="long_short", rebalance="staggered", hold_days=5, cost_bps=20),
        Config(name="154b_young180_730_long_short_staggered_h5_cost20", age_min=180, age_max=730, mode="long_short", rebalance="staggered", hold_days=5, cost_bps=20),
        Config(name="154b_young180_365_top15_long_short_staggered_h5_cost20", universe_size=15, mode="long_short", rebalance="staggered", hold_days=5, cost_bps=20),
        Config(name="154b_young180_365_top50_long_short_staggered_h5_cost20", universe_size=50, mode="long_short", rebalance="staggered", hold_days=5, cost_bps=20),
    ])
    return cfgs


def main() -> None:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_panel()
    start, end = "2021-05-01", "2026-04-30"
    configs = config_grid()
    all_stats = []
    all_yearly = []
    all_monthly = []
    all_rolling = []
    best_equities = []
    trade_parts = []

    for cfg in configs:
        print(f"[run] {cfg.name}", flush=True)
        eq, tr = run_backtest(panel, cfg, start, end)
        eq.to_csv(ART_DIR / f"{cfg.name}_equity.csv", index=False)
        if not tr.empty and cfg.cost_bps == 20 and cfg.rebalance == "staggered":
            trade_parts.append(tr)
        st = {"config": cfg.name, **cfg.__dict__, **perf_stats(eq)}
        all_stats.append(st)
        y = period_breakdown(eq, "Y"); y.insert(0, "config", cfg.name); all_yearly.append(y)
        m = period_breakdown(eq, "M"); m.insert(0, "config", cfg.name); all_monthly.append(m)
        r = rolling_windows(eq, 365, 60); r.insert(0, "config", cfg.name); all_rolling.append(r)
        if cfg.name in {"154b_long_short_staggered_h5_cost20", "154b_long_only_staggered_h5_cost20", "154b_placebo_old3y_long_short_staggered_h5_cost20"}:
            best_equities.append(eq)

    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv(ART_DIR / "rank154b_backtest_stats.csv", index=False)
    pd.concat(all_yearly, ignore_index=True).to_csv(ART_DIR / "rank154b_backtest_yearly.csv", index=False)
    pd.concat(all_monthly, ignore_index=True).to_csv(ART_DIR / "rank154b_backtest_monthly.csv", index=False)
    pd.concat(all_rolling, ignore_index=True).to_csv(ART_DIR / "rank154b_backtest_rolling365.csv", index=False)
    if trade_parts:
        pd.concat(trade_parts, ignore_index=True).to_csv(ART_DIR / "rank154b_backtest_trades_core.csv", index=False)
    if best_equities:
        pd.concat(best_equities, ignore_index=True).to_csv(ART_DIR / "rank154b_backtest_core_equities.csv", index=False)

    core_name = "154b_long_short_staggered_h5_cost20"
    core = stats_df[stats_df["config"] == core_name].iloc[0].to_dict()
    results = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "period": {"start": start, "end": end},
        "data": {
            "panel_path": str(PANEL_PATH.relative_to(ROOT)),
            "rows": int(len(panel)),
            "symbols": int(panel["symbol"].nunique()),
            "date_min": str(panel["date"].min()),
            "date_max": str(panel["date"].max()),
        },
        "core_config": core_name,
        "core_stats": {k: (float(v) if isinstance(v, (np.floating, float)) and math.isfinite(float(v)) else int(v) if isinstance(v, (np.integer,)) else v) for k, v in core.items()},
        "causality_audit": [
            {"item": "Universe", "status": "PASS", "detail": "Per date, filter by listing_days 180-365 and select same-date trailing 30d quote_volume Top30 from archive panel."},
            {"item": "Listing age", "status": "PASS_WITH_LIMITATION", "detail": "listing_days uses first observed archive daily kline, not current exchangeInfo; causal but approximate."},
            {"item": "Signal", "status": "PASS", "detail": "funding_rate_last observed on signal date; high funding goes long, low funding goes short."},
            {"item": "Execution timing", "status": "PASS", "detail": "rebalance at signal close D; earn D to D+1 close return and next-day realized funding sum."},
            {"item": "Costs", "status": "ROUGH", "detail": "turnover-based bps haircut; not orderbook/liquidity fill simulation."},
            {"item": "OOS split", "status": "INCLUDED", "detail": "Year/month/rolling breakdown supports 2021-2023 train vs 2024-2026 OOS diagnosis."},
        ],
    }
    (ART_DIR / "rank154b_backtest_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print("[ok] wrote artifacts to", ART_DIR)
    print(stats_df.sort_values("sharpe", ascending=False).head(12).to_string(index=False))


if __name__ == "__main__":
    main()
