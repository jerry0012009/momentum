#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path("/root/clawd/jerry/momentum")
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m" / "perp_cache"
OUT_DIR = ROOT / "reports" / "artifacts" / "rank201_5y_validation"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "LINKUSDT"]
ROUND_TRIP_COST_BPS = 8.0
ROUND_TRIP_COST = ROUND_TRIP_COST_BPS / 10000.0


def load_symbol(symbol: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__1825d__15m__perp.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, usecols=["timestamp", "open"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["symbol"] = symbol
    return df.sort_values("timestamp").reset_index(drop=True)


def build_symbol_trades(df: pd.DataFrame, common_start: pd.Timestamp, common_end: pd.Timestamp) -> pd.DataFrame:
    symbol = str(df["symbol"].iloc[0])
    work = df[(df["timestamp"] >= common_start.normalize()) & (df["timestamp"] <= common_end)].copy()
    work["date"] = work["timestamp"].dt.floor("D")
    work["hhmm"] = work["timestamp"].dt.strftime("%H:%M")
    piv = work[work["hhmm"].isin(["20:00", "22:00", "00:00"])].pivot(index="date", columns="hhmm", values="open").sort_index()

    long_trades = piv.dropna(subset=["20:00", "22:00"])[["20:00", "22:00"]].copy()
    long_trades["entry_ts"] = long_trades.index + pd.Timedelta(hours=20)
    long_trades["exit_ts"] = long_trades.index + pd.Timedelta(hours=22)
    long_trades["gross_ret"] = long_trades["22:00"] / long_trades["20:00"] - 1.0
    long_trades["net_ret"] = long_trades["gross_ret"] - ROUND_TRIP_COST
    long_trades["side"] = "long"
    long_trades["sleeve"] = "20_22_long"
    long_trades["symbol"] = symbol

    next_midnight = piv[["00:00"]].copy()
    next_midnight.index = next_midnight.index - pd.Timedelta(days=1)
    short_trades = piv[["22:00"]].join(next_midnight, how="inner").dropna().copy()
    short_trades["entry_ts"] = short_trades.index + pd.Timedelta(hours=22)
    short_trades["exit_ts"] = short_trades.index + pd.Timedelta(days=1)
    short_trades["gross_ret"] = short_trades["22:00"] / short_trades["00:00"] - 1.0
    short_trades["net_ret"] = short_trades["gross_ret"] - ROUND_TRIP_COST
    short_trades["side"] = "short"
    short_trades["sleeve"] = "22_00_short"
    short_trades["symbol"] = symbol

    trades = pd.concat(
        [
            long_trades[["symbol", "side", "sleeve", "entry_ts", "exit_ts", "gross_ret", "net_ret"]],
            short_trades[["symbol", "side", "sleeve", "entry_ts", "exit_ts", "gross_ret", "net_ret"]],
        ],
        ignore_index=True,
    )
    return trades.sort_values(["exit_ts", "side"]).reset_index(drop=True)


def compounded_return(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    return float((1.0 + series).prod() - 1.0)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frames = {symbol: load_symbol(symbol) for symbol in SYMBOLS}
    common_start = max(df["timestamp"].min() for df in frames.values())
    common_end = min(df["timestamp"].max() for df in frames.values())

    trades = pd.concat(
        [build_symbol_trades(df, common_start, common_end) for df in frames.values()],
        ignore_index=True,
    ).sort_values(["exit_ts", "symbol", "sleeve"]).reset_index(drop=True)

    portfolio = (
        trades.groupby("exit_ts", as_index=False)[["gross_ret", "net_ret"]]
        .mean()
        .sort_values("exit_ts")
        .reset_index(drop=True)
    )
    portfolio["equity"] = (1.0 + portfolio["net_ret"]).cumprod()
    portfolio["cumret"] = portfolio["equity"] - 1.0
    portfolio["month"] = portfolio["exit_ts"].dt.to_period("M").astype(str)
    portfolio["year"] = portfolio["exit_ts"].dt.year.astype(str)

    monthly = (
        portfolio.groupby("month")["net_ret"]
        .apply(compounded_return)
        .reset_index(name="net_return")
    )
    monthly["year"] = monthly["month"].str.slice(0, 4)
    yearly = (
        portfolio.groupby("year")["net_ret"]
        .apply(compounded_return)
        .reset_index(name="net_return")
    )
    by_symbol = (
        trades.groupby("symbol")
        .agg(
            trades=("net_ret", "size"),
            total_net_return=("net_ret", compounded_return),
            mean_net_bps=("net_ret", lambda s: float(s.mean() * 10000.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
        )
        .reset_index()
        .sort_values("total_net_return", ascending=False)
    )
    by_sleeve = (
        trades.groupby("sleeve")
        .agg(
            trades=("net_ret", "size"),
            total_net_return=("net_ret", compounded_return),
            mean_net_bps=("net_ret", lambda s: float(s.mean() * 10000.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
        )
        .reset_index()
        .sort_values("sleeve")
    )
    yearly_monthly = (
        monthly.groupby("year")
        .agg(
            months=("net_return", "size"),
            positive_months=("net_return", lambda s: int((s > 0).sum())),
            negative_months=("net_return", lambda s: int((s < 0).sum())),
            mean_monthly_return=("net_return", "mean"),
        )
        .reset_index()
    )

    rolling_peak = portfolio["equity"].cummax()
    drawdown = portfolio["equity"] / rolling_peak - 1.0

    summary = {
        "strategy": "Rank 201 / fixed UTC sleeves: long 20:00-21:59 UTC, short 22:00-23:59 UTC",
        "symbols": SYMBOLS,
        "round_trip_cost_bps": ROUND_TRIP_COST_BPS,
        "common_start_utc": common_start.isoformat(),
        "common_end_utc": common_end.isoformat(),
        "portfolio_events": int(len(portfolio)),
        "symbol_trades": int(len(trades)),
        "lifetime_total_return": float(portfolio["equity"].iloc[-1] - 1.0),
        "max_drawdown": float(drawdown.min()),
        "positive_months": int((monthly["net_return"] > 0).sum()),
        "total_months": int(len(monthly)),
        "positive_month_ratio": float((monthly["net_return"] > 0).mean()),
        "mean_monthly_return": float(monthly["net_return"].mean()),
        "median_monthly_return": float(monthly["net_return"].median()),
        "std_monthly_return": float(monthly["net_return"].std()),
        "best_month": {
            "month": str(monthly.loc[monthly["net_return"].idxmax(), "month"]),
            "return": float(monthly["net_return"].max()),
        },
        "worst_month": {
            "month": str(monthly.loc[monthly["net_return"].idxmin(), "month"]),
            "return": float(monthly["net_return"].min()),
        },
    }

    trades.to_csv(OUT_DIR / "rank201_5y_symbol_trades.csv", index=False)
    portfolio.to_csv(OUT_DIR / "rank201_5y_portfolio_events.csv", index=False)
    monthly.to_csv(OUT_DIR / "rank201_5y_monthly_returns.csv", index=False)
    yearly.to_csv(OUT_DIR / "rank201_5y_yearly_returns.csv", index=False)
    by_symbol.to_csv(OUT_DIR / "rank201_5y_by_symbol.csv", index=False)
    by_sleeve.to_csv(OUT_DIR / "rank201_5y_by_sleeve.csv", index=False)
    yearly_monthly.to_csv(OUT_DIR / "rank201_5y_yearly_month_counts.csv", index=False)
    (OUT_DIR / "rank201_5y_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
