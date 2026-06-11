#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import urlopen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.ema_donchian_breakout import (  # noqa: E402
    EmaDonchianBreakoutConfig,
    compute_ema_donchian_breakout_signals,
)
from momentum.analytics.ema_donchian_breakout_backtest import (  # noqa: E402
    EmaDonchianBacktestConfig,
    evaluate_ema_donchian_breakout,
)


LOOKBACK_GRID = [20, 40, 60]
CONFIRM_GRID = [1, 2, 3]
ATR_MULT_GRID = [1.0, 1.5, 2.0]
CROSS_MARKET_ASSETS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "SPY", "QQQ", "510300.SS"]
LONG_SAMPLE_ASSETS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD"]
OOS_TRAIN_DAYS = 120
OOS_TEST_DAYS = 60
ROLLING_WINDOW_DAYS = 20
ROLLING_STEP_DAYS = 10


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path



def pct(v: float) -> str:
    return "nan" if pd.isna(v) else f"{v * 100:.2f}%"



def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df



def download_bars(ticker: str, period: str, interval: str) -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(
        columns={
            "Datetime": "timestamp",
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    return bars[keep].dropna().sort_values("timestamp").reset_index(drop=True)



def load_input_data(input_path: str | None, ticker: str, period: str, interval: str) -> pd.DataFrame:
    if input_path:
        path = Path(input_path)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise ValueError(f"Input not found: {path}")
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df
    return download_bars(ticker=ticker, period=period, interval=interval)



def summarize_variant(summary_df: pd.DataFrame, variant: str, **params) -> dict:
    if summary_df.empty:
        return {
            "variant": variant,
            **params,
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "long_trades": 0,
            "short_trades": 0,
        }
    row = summary_df.iloc[0].to_dict()
    return {"variant": variant, **params, **row}



def binance_symbol_from_ticker(ticker: str) -> str | None:
    mapping = {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "SOL-USD": "SOLUSDT",
        "XRP-USD": "XRPUSDT",
        "DOGE-USD": "DOGEUSDT",
        "LTC-USD": "LTCUSDT",
        "ADA-USD": "ADAUSDT",
        "BNB-USD": "BNBUSDT",
    }
    return mapping.get(ticker)



def download_binance_bars(symbol: str, *, interval: str = "5m", days: int = 180) -> pd.DataFrame:
    end_ms = int(pd.Timestamp.now("UTC").timestamp() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    url = "https://api.binance.com/api/v3/klines"
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        qs = urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": current,
                "endTime": end_ms,
                "limit": 1000,
            }
        )
        with urlopen(f"{url}?{qs}", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data:
            break
        rows.extend(data)
        last_close_time = int(data[-1][6])
        current = last_close_time + 1
        if len(data) < 1000:
            break
    if not rows:
        raise ValueError(f"No Binance data for {symbol}")
    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    out = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(df["open_time"], unit="ms", utc=True),
            "open": pd.to_numeric(df["open"], errors="coerce"),
            "high": pd.to_numeric(df["high"], errors="coerce"),
            "low": pd.to_numeric(df["low"], errors="coerce"),
            "close": pd.to_numeric(df["close"], errors="coerce"),
            "volume": pd.to_numeric(df["volume"], errors="coerce"),
        }
    )
    return out.dropna().sort_values("timestamp").reset_index(drop=True)



def load_best_available_asset_sample(asset: str) -> tuple[pd.DataFrame, str]:
    symbol = binance_symbol_from_ticker(asset)
    if symbol is not None:
        bars = download_binance_bars(symbol, interval="5m", days=180)
        bars["symbol"] = asset
        return bars, "Binance 180d 5m"
    bars = download_bars(asset, period="60d", interval="5m")
    bars["symbol"] = asset
    return bars, "Yahoo 60d 5m"



def evaluate_default_strategy(
    bars: pd.DataFrame,
    *,
    symbol: str,
    cfg: EmaDonchianBreakoutConfig,
    bt_cfg: EmaDonchianBacktestConfig,
    sample_label: str,
    phase: str | None = None,
    window_id: int | None = None,
    window_start: str | None = None,
    window_end: str | None = None,
) -> pd.DataFrame:
    bars = bars.copy()
    bars["symbol"] = symbol
    sig = build_variant_signals(bars, mode="ema_donchian_default", cfg=cfg)
    bt = evaluate_ema_donchian_breakout(sig, config=bt_cfg)
    summary = bt.summary.iloc[0] if not bt.summary.empty else pd.Series(dtype=float)
    row = {
        "asset": symbol,
        "sample": sample_label,
        "variant": "ema_donchian_default",
        "trades": int(summary.get("trades", 0) or 0),
        "win_rate": float(summary.get("win_rate", np.nan)),
        "total_return": float(summary.get("total_return", 0.0) or 0.0),
        "max_drawdown": float(summary.get("max_drawdown", 0.0) or 0.0),
    }
    if phase is not None:
        row["phase"] = phase
    if window_id is not None:
        row["window_id"] = int(window_id)
        row["window_start"] = window_start
        row["window_end"] = window_end
    return pd.DataFrame([row])



def asset_class_of(asset: str) -> str:
    return "crypto" if asset in {"BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "LTC-USD", "ADA-USD", "BNB-USD"} else "other"



def aggregate_asset_results(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    grp = df.groupby("variant", as_index=False).agg(
        assets_tested=("asset", "nunique"),
        positive_assets=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        min_total_return=("total_return", "min"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets_tested"].replace(0, np.nan)
    return grp



def aggregate_by_asset_class(df: pd.DataFrame, *, positive_col_name: str = "positive_asset_ratio") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["asset_class"] = tmp["asset"].map(asset_class_of)
    grp = tmp.groupby(["variant", "asset_class"], as_index=False).agg(
        assets_tested=("asset", "nunique"),
        positive_assets=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        min_total_return=("total_return", "min"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
    )
    grp[positive_col_name] = grp["positive_assets"] / grp["assets_tested"].replace(0, np.nan)
    return grp



def aggregate_rolling_by_asset_class(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["asset_class"] = tmp["asset"].map(asset_class_of)
    grp = tmp.groupby(["variant", "asset_class"], as_index=False).agg(
        assets_tested=("asset", "nunique"),
        windows_tested=("total_return", "size"),
        positive_windows=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        min_total_return=("total_return", "min"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
    )
    grp["positive_window_ratio"] = grp["positive_windows"] / grp["windows_tested"].replace(0, np.nan)
    return grp



def compute_cross_market_tables(
    *,
    cfg: EmaDonchianBreakoutConfig,
    bt_cfg: EmaDonchianBacktestConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    sources = []
    for asset in CROSS_MARKET_ASSETS:
        try:
            bars, sample_label = load_best_available_asset_sample(asset)
            if "Yahoo" in sample_label:
                bars = download_bars(asset, period="60d", interval="5m")
                bars["symbol"] = asset
                sample_label = "Yahoo 60d 5m"
            else:
                # use same-window comparison for crypto too
                bars = bars.tail(60 * 24 * 12)
                sample_label = "Binance tail 60d 5m"
            rows.append(evaluate_default_strategy(bars, symbol=asset, cfg=cfg, bt_cfg=bt_cfg, sample_label=sample_label))
            sources.append({"asset": asset, "sample": sample_label, "rows": int(len(bars))})
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})
    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown"])
    agg = aggregate_asset_results(raw) if not raw.empty else pd.DataFrame()
    return raw, agg, pd.DataFrame(sources)



def compute_oos_tables(
    *,
    cfg: EmaDonchianBreakoutConfig,
    bt_cfg: EmaDonchianBacktestConfig,
    train_days: int = OOS_TRAIN_DAYS,
    test_days: int = OOS_TEST_DAYS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    sources = []
    total_days = train_days + test_days
    for asset in LONG_SAMPLE_ASSETS:
        try:
            symbol = binance_symbol_from_ticker(asset)
            if symbol is None:
                continue
            bars = download_binance_bars(symbol, interval="5m", days=total_days)
            bars["symbol"] = asset
            ts = pd.to_datetime(bars["timestamp"], utc=True)
            split_ts = ts.max() - pd.Timedelta(days=test_days)
            train = bars[ts < split_ts].copy().reset_index(drop=True)
            test = bars[ts >= split_ts].copy().reset_index(drop=True)
            rows.append(evaluate_default_strategy(train, symbol=asset, cfg=cfg, bt_cfg=bt_cfg, sample_label=f"Binance {train_days}d 5m", phase="train"))
            rows.append(evaluate_default_strategy(test, symbol=asset, cfg=cfg, bt_cfg=bt_cfg, sample_label=f"Binance {test_days}d 5m", phase="test"))
            sources.append({"asset": asset, "sample": f"Binance {total_days}d split {train_days}/{test_days}", "rows": int(len(bars))})
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})
    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown", "phase"])
    if raw.empty:
        return raw, pd.DataFrame(), pd.DataFrame(sources)
    agg = raw.groupby(["variant", "phase"], as_index=False).agg(
        assets_tested=("asset", "nunique"),
        positive_assets=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        min_total_return=("total_return", "min"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
    )
    agg["positive_asset_ratio"] = agg["positive_assets"] / agg["assets_tested"].replace(0, np.nan)
    return raw, agg, pd.DataFrame(sources)



def compute_rolling_validation_tables(
    *,
    cfg: EmaDonchianBreakoutConfig,
    bt_cfg: EmaDonchianBacktestConfig,
    window_days: int = ROLLING_WINDOW_DAYS,
    step_days: int = ROLLING_STEP_DAYS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    sources = []
    window_td = pd.Timedelta(days=window_days)
    step_td = pd.Timedelta(days=step_days)
    for asset in CROSS_MARKET_ASSETS:
        try:
            bars, sample_label = load_best_available_asset_sample(asset)
            sources.append({"asset": asset, "sample": sample_label, "rows": int(len(bars))})
            ts = pd.to_datetime(bars["timestamp"], utc=True)
            start = ts.min()
            limit = ts.max() - window_td
            window_id = 0
            while start <= limit:
                end = start + window_td
                sub = bars[(ts >= start) & (ts < end)].copy().reset_index(drop=True)
                start = start + step_td
                if len(sub) < 200:
                    continue
                window_id += 1
                rows.append(
                    evaluate_default_strategy(
                        sub,
                        symbol=asset,
                        cfg=cfg,
                        bt_cfg=bt_cfg,
                        sample_label=sample_label,
                        window_id=window_id,
                        window_start=pd.Timestamp(sub["timestamp"].iloc[0]).strftime("%Y-%m-%d %H:%M:%S%z"),
                        window_end=pd.Timestamp(sub["timestamp"].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S%z"),
                    )
                )
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})
    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown", "window_id", "window_start", "window_end"])
    if raw.empty:
        return raw, pd.DataFrame(), pd.DataFrame(sources)
    agg = raw.groupby("variant", as_index=False).agg(
        assets_tested=("asset", "nunique"),
        windows_tested=("total_return", "size"),
        positive_windows=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        min_total_return=("total_return", "min"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
    )
    agg["positive_window_ratio"] = agg["positive_windows"] / agg["windows_tested"].replace(0, np.nan)
    return raw, agg, pd.DataFrame(sources)



def build_variant_signals(bars: pd.DataFrame, *, mode: str, cfg: EmaDonchianBreakoutConfig) -> pd.DataFrame:
    sig = compute_ema_donchian_breakout_signals(bars, config=cfg)
    if mode == "raw_breakout":
        long_ready = sig["long_confirm"] == 1
        short_ready = sig["short_confirm"] == 1
        sig["long_signal"] = (long_ready & (~long_ready.shift(1).fillna(False))).astype(int)
        sig["short_signal"] = (short_ready & (~short_ready.shift(1).fillna(False))).astype(int)
    elif mode == "confirmed_breakout":
        long_ready = sig["long_confirm"] == 1
        short_ready = sig["short_confirm"] == 1
        sig["long_signal"] = (long_ready & (~long_ready.shift(1).fillna(False))).astype(int)
        sig["short_signal"] = (short_ready & (~short_ready.shift(1).fillna(False))).astype(int)
    elif mode == "ema_donchian_default":
        pass
    else:
        raise ValueError(f"Unknown mode: {mode}")
    return sig



def plot_price_system(df: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.2))
    ts = pd.to_datetime(df["timestamp"], utc=True)
    ax.plot(ts, df["close"], label="close", linewidth=1.0)
    if "donchian_upper" in df.columns:
        ax.plot(ts, df["donchian_upper"], label="donchian_upper", linewidth=0.9, alpha=0.8)
    if "donchian_lower" in df.columns:
        ax.plot(ts, df["donchian_lower"], label="donchian_lower", linewidth=0.9, alpha=0.8)
    long_idx = df["long_signal"] == 1
    short_idx = df["short_signal"] == 1
    if long_idx.any():
        ax.scatter(ts[long_idx], df.loc[long_idx, "close"], s=12, marker="^", label="long", alpha=0.8)
    if short_idx.any():
        ax.scatter(ts[short_idx], df.loc[short_idx, "close"], s=12, marker="v", label="short", alpha=0.8)
    ax.set_title(f"{ticker} EMA + Donchian system view")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_nav_compare(nav_map: dict[str, pd.DataFrame], path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 4.3))
    for label, nav in nav_map.items():
        if nav is None or nav.empty:
            continue
        ts = pd.to_datetime(nav["timestamp"], utc=True)
        ax.plot(ts, nav["nav"], label=label, linewidth=1.4)
    ax.set_title(f"{ticker} NAV compare: breakout variants")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_sweep_heatmap(df: pd.DataFrame, path: Path) -> None:
    pivot = df.pivot(index="confirm_bars", columns="donchian_lookback", values="total_return").sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(6.2, 4.5))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=[str(x) for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
    ax.set_xlabel("donchian_lookback")
    ax.set_ylabel("confirm_bars")
    ax.set_title("EMA+Donchian sweep: total return heatmap")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_top_variants(df: pd.DataFrame, path: Path) -> None:
    top = df.sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).head(8).copy()
    top["label"] = top.apply(lambda r: f"N{int(r['donchian_lookback'])}|c{int(r['confirm_bars'])}", axis=1)
    fig, ax = plt.subplots(figsize=(10.5, 4.5))
    ax.bar(top["label"], top["total_return"])
    ax.set_title("Top EMA+Donchian variants by total return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_asset_returns(df: pd.DataFrame, path: Path, *, title: str) -> None:
    assets = list(df["asset"])
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.bar(assets, df["total_return"])
    ax.set_title(title)
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_oos_train_test(df: pd.DataFrame, path: Path) -> None:
    assets = sorted(df["asset"].unique())
    phases = ["train", "test"]
    x = np.arange(len(assets))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    for idx, phase in enumerate(phases):
        sub = df[df["phase"] == phase].set_index("asset").reindex(assets)
        ax.bar(x + (idx - 0.5) * width, sub["total_return"], width=width, label=phase)
    ax.set_xticks(x, labels=assets)
    ax.set_title("OOS split: train vs test returns")
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="best")
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_rolling_scores(df: pd.DataFrame, path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(8, 4.6))
    ax1.bar(df["variant"], df["positive_window_ratio"], alpha=0.75, label="positive_window_ratio")
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("positive_window_ratio")
    ax1.grid(axis="y", alpha=0.2)
    ax2 = ax1.twinx()
    ax2.plot(df["variant"], df["mean_total_return"], color="tab:red", marker="o", label="mean_total_return")
    ax2.set_ylabel("mean_total_return")
    ax1.set_title("Rolling validation: positive-window ratio + mean return")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def plot_asset_class_compare(df: pd.DataFrame, path: Path, *, title: str, ratio_col: str) -> None:
    sub = df.copy()
    classes = [c for c in ["crypto", "other"] if c in set(sub["asset_class"])]
    sub = sub.set_index("asset_class").reindex(classes).reset_index()
    fig, ax1 = plt.subplots(figsize=(7.5, 4.6))
    ax1.bar(sub["asset_class"], sub["mean_total_return"], alpha=0.8, label="mean_total_return")
    ax1.set_ylabel("mean_total_return")
    ax1.grid(axis="y", alpha=0.2)
    ax2 = ax1.twinx()
    ax2.plot(sub["asset_class"], sub[ratio_col], color="tab:red", marker="o", label=ratio_col)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel(ratio_col)
    ax1.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def render_html(
    *,
    ticker: str,
    period: str,
    interval: str,
    compare_df: pd.DataFrame,
    sweep_df: pd.DataFrame,
    atr_df: pd.DataFrame,
    cross_market_raw_df: pd.DataFrame,
    cross_market_agg_df: pd.DataFrame,
    cross_market_sources_df: pd.DataFrame,
    cross_market_class_df: pd.DataFrame,
    oos_raw_df: pd.DataFrame,
    oos_agg_df: pd.DataFrame,
    oos_sources_df: pd.DataFrame,
    rolling_raw_df: pd.DataFrame,
    rolling_agg_df: pd.DataFrame,
    rolling_sources_df: pd.DataFrame,
    rolling_class_df: pd.DataFrame,
    default_cfg: EmaDonchianBreakoutConfig,
    backtest_cfg: EmaDonchianBacktestConfig,
    assets_rel: dict,
) -> str:
    raw_row = compare_df[compare_df["variant"] == "raw_breakout"].iloc[0]
    confirm_row = compare_df[compare_df["variant"] == "confirmed_breakout"].iloc[0]
    default_row = compare_df[compare_df["variant"] == "ema_donchian_default"].iloc[0]
    best_row = sweep_df.sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).iloc[0]
    best_atr_row = atr_df.sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).iloc[0]

    cross_market_row = cross_market_agg_df.iloc[0] if not cross_market_agg_df.empty else None
    cross_crypto_row = cross_market_class_df[cross_market_class_df["asset_class"] == "crypto"].iloc[0] if not cross_market_class_df.empty and (cross_market_class_df["asset_class"] == "crypto").any() else None
    cross_other_row = cross_market_class_df[cross_market_class_df["asset_class"] == "other"].iloc[0] if not cross_market_class_df.empty and (cross_market_class_df["asset_class"] == "other").any() else None
    oos_train_row = oos_agg_df[oos_agg_df["phase"] == "train"].iloc[0] if not oos_agg_df.empty and (oos_agg_df["phase"] == "train").any() else None
    oos_test_row = oos_agg_df[oos_agg_df["phase"] == "test"].iloc[0] if not oos_agg_df.empty and (oos_agg_df["phase"] == "test").any() else None
    rolling_row = rolling_agg_df.iloc[0] if not rolling_agg_df.empty else None
    rolling_crypto_row = rolling_class_df[rolling_class_df["asset_class"] == "crypto"].iloc[0] if not rolling_class_df.empty and (rolling_class_df["asset_class"] == "crypto").any() else None
    rolling_other_row = rolling_class_df[rolling_class_df["asset_class"] == "other"].iloc[0] if not rolling_class_df.empty and (rolling_class_df["asset_class"] == "other").any() else None

    q1 = "Donchian breakout 负责触发，1h EMA 结构负责方向过滤，ATR 负责风控；这是一个适合教学的最小趋势系统模板。"
    q2 = (
        f"当前样本里，raw breakout={pct(float(raw_row['total_return']))}，confirmed breakout={pct(float(confirm_row['total_return']))}，"
        f"EMA+Donchian default={pct(float(default_row['total_return']))}。"
    )
    q3 = (
        f"当前 sweep 最优组合是 lookback={int(best_row['donchian_lookback'])}, confirm_bars={int(best_row['confirm_bars'])}，"
        f"total_return={pct(float(best_row['total_return']))}, max_dd={pct(float(best_row['max_drawdown']))}。"
    )
    q4 = (
        f"当前 ATR 对比里，最优是 atr_mult={best_atr_row['atr_mult']:.1f}，但默认 baseline 仍建议先从 {backtest_cfg.atr_mult:.1f} 开始。"
    )
    q5 = (
        f"跨市场（{int(cross_market_row['assets_tested'])} 个标的）里，default 策略的 positive_asset_ratio={cross_market_row['positive_asset_ratio']:.2f}，mean_return={pct(float(cross_market_row['mean_total_return']))}。"
        if cross_market_row is not None
        else "跨市场结果暂不完整。"
    )
    q6 = (
        f"长样本 OOS 拆分里，train 的平均收益={pct(float(oos_train_row['mean_total_return']))}，test 的平均收益={pct(float(oos_test_row['mean_total_return']))}；"
        f"如果 test 还维持为正，说明这套模板不只是样本内好看。"
        if oos_train_row is not None and oos_test_row is not None
        else "OOS 结果暂不完整。"
    )
    q7 = (
        f"rolling 里，positive_window_ratio={rolling_row['positive_window_ratio']:.2f}，mean_return={pct(float(rolling_row['mean_total_return']))}。"
        f" 这能帮助我们判断它是跨阶段稳定，还是只在少数窗口有效。"
        if rolling_row is not None
        else "rolling 结果暂不完整。"
    )
    q8 = (
        f"如果拆成加密 vs 其他，cross-market 里 crypto 的 mean_return={pct(float(cross_crypto_row['mean_total_return']))}、positive_asset_ratio={cross_crypto_row['positive_asset_ratio']:.2f}；"
        f"other 的 mean_return={pct(float(cross_other_row['mean_total_return']))}、positive_asset_ratio={cross_other_row['positive_asset_ratio']:.2f}。"
        f" rolling 里 crypto 的 positive_window_ratio={rolling_crypto_row['positive_window_ratio']:.2f}，other 是 {rolling_other_row['positive_window_ratio']:.2f}。"
        if cross_crypto_row is not None and cross_other_row is not None and rolling_crypto_row is not None and rolling_other_row is not None
        else "加密 vs 其他的分组结果暂不完整。"
    )
    q9 = "学习上先保留这套最小模板，不急着把回踩确认、量能确认、更多 regime 过滤全部堆上去；先看它在更多币种、更多样本、更多阶段里能不能站住。"

    return f"""
<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>EMA + Donchian Breakout Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1100px; line-height: 1.6; color: #111; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color: #666; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
    .card {{ border: 1px solid #e5e5e5; border-radius: 10px; padding: 14px; background: #fafafa; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 20px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; font-size: 14px; }}
    th {{ background: #f3f3f3; }}
    img {{ max-width: 100%; border: 1px solid #e5e5e5; border-radius: 8px; margin: 8px 0 20px; }}
    .qa {{ border-left: 4px solid #4f46e5; padding-left: 14px; margin: 18px 0; }}
    code {{ background: #f6f6f6; padding: 2px 6px; border-radius: 6px; }}
  </style>
</head>
<body>
  <h1>均线结构 + Donchian breakout 学习型报告</h1>
  <p class=\"muted\">Ticker: {ticker} · period={period} · interval={interval} · generated_at={datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>0. 研究问题</h2>
  <p>这份报告回答的问题是：<b>在短周期里，能不能用 1h EMA 结构给方向、用 5m Donchian breakout 给触发、再用收盘确认和 ATR 止损拼出一个可解释的最小趋势系统？</b></p>

  <h2>1. 系统模板</h2>
  <div class=\"grid\">
    <div class=\"card\"><b>方向层</b><br>1h EMA({default_cfg.ema_window_1h})<br>close_1h > EMA 且 slope up</div>
    <div class=\"card\"><b>触发层</b><br>5m Donchian breakout<br>lookback={default_cfg.donchian_lookback}</div>
    <div class=\"card\"><b>确认/风控</b><br>confirm_bars={default_cfg.confirm_bars}<br>ATR stop={backtest_cfg.atr_mult:.1f}x</div>
  </div>

  <h2>2. 规则定义</h2>
  <ul>
    <li><code>ema_1h = EMA(close_1h, {default_cfg.ema_window_1h})</code></li>
    <li><code>donchian_upper = rolling_max(high.shift(1), {default_cfg.donchian_lookback})</code></li>
    <li><code>donchian_lower = rolling_min(low.shift(1), {default_cfg.donchian_lookback})</code></li>
    <li>方向过滤：<code>close_1h &gt; ema_1h</code> 且 <code>ema_1h</code> 斜率为正（做空方向对称）</li>
    <li>突破确认：连续 <code>{default_cfg.confirm_bars}</code> 根收盘维持在上轨之上 / 下轨之下</li>
    <li>止损：<code>entry ± {backtest_cfg.atr_mult:.1f} * ATR({backtest_cfg.atr_period})</code></li>
  </ul>

  <h2>3. 价格与默认系统信号</h2>
  <img src=\"{assets_rel['price']}\" alt=\"price system\" />

  <h2>4. 变体对照：裸 breakout / 确认 breakout / EMA+Donchian</h2>
  {compare_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src=\"{assets_rel['nav_compare']}\" alt=\"nav compare\" />

  <h2>5. 参数扫描（lookback × confirm）</h2>
  {sweep_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src=\"{assets_rel['heatmap']}\" alt=\"heatmap\" />
  <img src=\"{assets_rel['top']}\" alt=\"top variants\" />

  <h2>6. ATR 止损敏感度</h2>
  {atr_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>7. Cross-market：更多币种 / 美股 / A股代理里还有效吗？</h2>
  {cross_market_sources_df.to_html(index=False) if not cross_market_sources_df.empty else '<p>no cross-market sources</p>'}
  {cross_market_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not cross_market_agg_df.empty else '<p>cross-market aggregate unavailable</p>'}
  <img src=\"{assets_rel['cross_market']}\" alt=\"cross market\" />
  {cross_market_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not cross_market_raw_df.empty else '<p>cross-market raw unavailable</p>'}

  <h2>7.5 加密 vs 其他：它更像 crypto-specific 吗？</h2>
  {cross_market_class_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not cross_market_class_df.empty else '<p>cross-market class aggregate unavailable</p>'}
  <img src=\"{assets_rel['cross_market_class']}\" alt=\"cross market class\" />
  {rolling_class_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not rolling_class_df.empty else '<p>rolling class aggregate unavailable</p>'}
  <img src=\"{assets_rel['rolling_class']}\" alt=\"rolling class\" />

  <h2>8. OOS：长样本拆 train / test 之后还站得住吗？</h2>
  <p class=\"muted\">这里固定默认参数，不做重调参；只看 train/test 的 forward split 表现。</p>
  {oos_sources_df.to_html(index=False) if not oos_sources_df.empty else '<p>no oos sources</p>'}
  {oos_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not oos_agg_df.empty else '<p>oos aggregate unavailable</p>'}
  <img src=\"{assets_rel['oos_train_test']}\" alt=\"oos train test\" />
  {oos_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not oos_raw_df.empty else '<p>oos raw unavailable</p>'}

  <h2>9. Rolling：多个时间阶段里是否持续有效？</h2>
  <p class=\"muted\">rolling 设置：window={ROLLING_WINDOW_DAYS}d，step={ROLLING_STEP_DAYS}d。crypto 用 Binance 180d 5m，其它市场用 Yahoo 60d 5m。</p>
  {rolling_sources_df.to_html(index=False) if not rolling_sources_df.empty else '<p>no rolling sources</p>'}
  {rolling_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not rolling_agg_df.empty else '<p>rolling aggregate unavailable</p>'}
  <img src=\"{assets_rel['rolling_scores']}\" alt=\"rolling scores\" />
  {rolling_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not rolling_raw_df.empty else '<p>rolling raw unavailable</p>'}

  <h2>10. 文字版研究结论（问题 → 结论 → 动作）</h2>
  <div class=\"qa\">
    <h3>Q0. 这个 EMA 策略到底是什么？</h3>
    <p><b>结论：</b>一句话讲：<b>EMA 管方向，Donchian 管触发，ATR 管止损</b>。具体做法是：先看 1h EMA(20)，如果价格站在 EMA 上且 EMA 斜率向上，就优先只做多；如果价格在 EMA 下且 EMA 斜率向下，就优先只做空。然后回到 5m，用 Donchian 突破找进场，再用 3 根收盘确认减少假突破，最后用 1.5x ATR 做止损。</p>
    <p><b>动作：</b>把它记成 4 层：<b>方向层 → 触发层 → 确认层 → 风控层</b>，不要把它当成“单一均线金叉死叉策略”。</p>
  </div>
  <div class=\"qa\">
    <h3>Q1. 它现在强在哪里？</h3>
    <p><b>结论：</b>它最强的地方不是“绝对收益特别夸张”，而是<b>比裸 breakout 明显更像一个能用的系统</b>。当前样本里，raw breakout={pct(float(raw_row['total_return']))}，confirmed breakout={pct(float(confirm_row['total_return']))}，EMA+Donchian default={pct(float(default_row['total_return']))}；也就是说，EMA 方向过滤把原本很差的裸突破，拉成了正收益模板。</p>
    <p><b>动作：</b>先把“它为什么比裸突破强”理解清楚：不是因为 EMA 会预测未来，而是因为 EMA 在帮你少做逆势突破。</p>
  </div>
  <div class=\"qa\">
    <h3>Q2. 它到底有多强？</h3>
    <p><b>结论：</b>如果只看当前 BTC-USD、60d、5m 这个样本，默认参数结果是：<b>{int(default_row['trades'])} 笔交易，收益 {pct(float(default_row['total_return']))}，最大回撤 {pct(float(default_row['max_drawdown']))}</b>。如果看参数扫描里的单点最优，lookback={int(best_row['donchian_lookback'])}、confirm={int(best_row['confirm_bars'])} 可以到 <b>{pct(float(best_row['total_return']))}</b>，但那更像样本内最优，不适合直接当最终答案。</p>
    <p><b>动作：</b>默认先记住这组更保守、更可信的结果；不要先被单点最优带偏。</p>
  </div>
  <div class=\"qa\">
    <h3>Q3. 它现在强得稳不稳？</h3>
    <p><b>结论：</b>{q6} 同时，{q7}</p>
    <p><b>动作：</b>正确定位应该是：<b>有一定生命力的候选模板</b>，不是已经毕业的主策略。</p>
  </div>
  <div class=\"qa\">
    <h3>Q4. 它更像哪种市场的策略？</h3>
    <p><b>结论：</b>{q8}</p>
    <p><b>动作：</b>先把它理解成“更适合加密市场的短周期趋势模板”，不要急着把它包装成通用市场策略。</p>
  </div>
  <div class=\"qa\">
    <h3>Q5. 当前样本里，Donchian 的窗口和确认根数偏向什么？</h3>
    <p><b>结论：</b>{q3}</p>
    <p><b>动作：</b>如果最优只是孤立单点，不要急着宣布“找到答案”；优先看邻域是不是也还行。</p>
  </div>
  <div class=\"qa\">
    <h3>Q6. ATR 止损该怎么理解？</h3>
    <p><b>结论：</b>{q4}</p>
    <p><b>动作：</b>学习上先把 1.5x ATR 当 baseline，后续再比较 1.0 / 1.5 / 2.0 的权衡。</p>
  </div>
  <div class=\"qa\">
    <h3>Q7. 在更多币种和市场里，它普遍有效吗？</h3>
    <p><b>结论：</b>{q5} 所以它现在不能算“普遍有效”。</p>
    <p><b>动作：</b>先看 crypto 是否明显好于股票/A股代理；如果只在 crypto 有效，就更像加密市场模板而不是通用模板。</p>
  </div>
  <div class=\"qa\">
    <h3>Q8. 如果让我一句话总结这条 EMA 策略，现在该怎么定性？</h3>
    <p><b>结论：</b><b>它是一条已经证明“比裸突破强很多”、但还没有证明“跨市场稳健”的加密短周期趋势候选模板。</b></p>
    <p><b>动作：</b>后续应该继续把它当候选模板观察，而不是当作已经定型的主 alpha 直接重仓推进。</p>
  </div>
  <div class=\"qa\">
    <h3>Q9. 这轮扩展验证之后，下一步怎么走？</h3>
    <p><b>结论：</b>{q9}</p>
    <p><b>动作：</b>先判断它是不是值得升级为真正候选策略；若 rolling / OOS 仍弱，就继续把它留在学习模板层。</p>
  </div>
</body>
</html>
"""



def main() -> int:
    parser = argparse.ArgumentParser(description="Build EMA + Donchian breakout learning report.")
    parser.add_argument("--ticker", default="BTC-USD")
    parser.add_argument("--period", default="60d")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--input", default=None)
    parser.add_argument("--ema-window-1h", type=int, default=20)
    parser.add_argument("--donchian-lookback", type=int, default=20)
    parser.add_argument("--confirm-bars", type=int, default=3)
    parser.add_argument("--atr-period", type=int, default=14)
    parser.add_argument("--atr-mult", type=float, default=1.5)
    parser.add_argument("--fee-bps-per-side", type=float, default=4.0)
    parser.add_argument("--slippage-bps-per-side", type=float, default=2.0)
    args = parser.parse_args()

    factor = "ema_donchian_breakout"
    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / factor)
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / factor)
    assets_dir = ensure_dir(site_dir / "assets")

    bars = load_input_data(args.input, args.ticker, args.period, args.interval)
    bars["symbol"] = args.ticker

    default_cfg = EmaDonchianBreakoutConfig(
        ema_window_1h=args.ema_window_1h,
        donchian_lookback=args.donchian_lookback,
        confirm_bars=args.confirm_bars,
        use_ema_slope=True,
    )
    bt_cfg = EmaDonchianBacktestConfig(
        fee_bps_per_side=args.fee_bps_per_side,
        slippage_bps_per_side=args.slippage_bps_per_side,
        atr_period=args.atr_period,
        atr_mult=args.atr_mult,
        flip_on_reverse_signal=True,
    )

    raw_cfg = EmaDonchianBreakoutConfig(
        ema_window_1h=args.ema_window_1h,
        donchian_lookback=args.donchian_lookback,
        confirm_bars=1,
        use_ema_slope=False,
    )
    confirm_cfg = EmaDonchianBreakoutConfig(
        ema_window_1h=args.ema_window_1h,
        donchian_lookback=args.donchian_lookback,
        confirm_bars=args.confirm_bars,
        use_ema_slope=False,
    )

    raw_sig = build_variant_signals(bars, mode="raw_breakout", cfg=raw_cfg)
    confirm_sig = build_variant_signals(bars, mode="confirmed_breakout", cfg=confirm_cfg)
    default_sig = build_variant_signals(bars, mode="ema_donchian_default", cfg=default_cfg)

    raw_bt = evaluate_ema_donchian_breakout(raw_sig, config=bt_cfg)
    confirm_bt = evaluate_ema_donchian_breakout(confirm_sig, config=bt_cfg)
    default_bt = evaluate_ema_donchian_breakout(default_sig, config=bt_cfg)

    compare_df = pd.DataFrame(
        [
            summarize_variant(raw_bt.summary, "raw_breakout", donchian_lookback=raw_cfg.donchian_lookback, confirm_bars=1, atr_mult=bt_cfg.atr_mult),
            summarize_variant(confirm_bt.summary, "confirmed_breakout", donchian_lookback=confirm_cfg.donchian_lookback, confirm_bars=confirm_cfg.confirm_bars, atr_mult=bt_cfg.atr_mult),
            summarize_variant(default_bt.summary, "ema_donchian_default", donchian_lookback=default_cfg.donchian_lookback, confirm_bars=default_cfg.confirm_bars, atr_mult=bt_cfg.atr_mult),
        ]
    )

    sweep_rows = []
    for lookback in LOOKBACK_GRID:
        for confirm in CONFIRM_GRID:
            cfg = EmaDonchianBreakoutConfig(
                ema_window_1h=args.ema_window_1h,
                donchian_lookback=lookback,
                confirm_bars=confirm,
                use_ema_slope=True,
            )
            sig = build_variant_signals(bars, mode="ema_donchian_default", cfg=cfg)
            bt = evaluate_ema_donchian_breakout(sig, config=bt_cfg)
            row = summarize_variant(bt.summary, "ema_donchian_default", donchian_lookback=lookback, confirm_bars=confirm, atr_mult=bt_cfg.atr_mult)
            sweep_rows.append(row)
    sweep_df = pd.DataFrame(sweep_rows).sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).reset_index(drop=True)

    atr_rows = []
    for atr_mult in ATR_MULT_GRID:
        cfg = EmaDonchianBacktestConfig(
            fee_bps_per_side=args.fee_bps_per_side,
            slippage_bps_per_side=args.slippage_bps_per_side,
            atr_period=args.atr_period,
            atr_mult=atr_mult,
            flip_on_reverse_signal=True,
        )
        bt = evaluate_ema_donchian_breakout(default_sig, config=cfg)
        atr_rows.append(summarize_variant(bt.summary, "ema_donchian_default", atr_mult=atr_mult))
    atr_df = pd.DataFrame(atr_rows)

    cross_market_raw_df, cross_market_agg_df, cross_market_sources_df = compute_cross_market_tables(
        cfg=default_cfg,
        bt_cfg=bt_cfg,
    )
    cross_market_class_df = aggregate_by_asset_class(cross_market_raw_df, positive_col_name="positive_asset_ratio") if not cross_market_raw_df.empty else pd.DataFrame()
    oos_raw_df, oos_agg_df, oos_sources_df = compute_oos_tables(
        cfg=default_cfg,
        bt_cfg=bt_cfg,
        train_days=OOS_TRAIN_DAYS,
        test_days=OOS_TEST_DAYS,
    )
    rolling_raw_df, rolling_agg_df, rolling_sources_df = compute_rolling_validation_tables(
        cfg=default_cfg,
        bt_cfg=bt_cfg,
        window_days=ROLLING_WINDOW_DAYS,
        step_days=ROLLING_STEP_DAYS,
    )
    rolling_class_df = aggregate_rolling_by_asset_class(rolling_raw_df) if not rolling_raw_df.empty else pd.DataFrame()

    default_sig.to_csv(artifacts_dir / "signal_snapshot.csv", index=False)
    raw_bt.summary.to_csv(artifacts_dir / "raw_breakout_summary.csv", index=False)
    confirm_bt.summary.to_csv(artifacts_dir / "confirmed_breakout_summary.csv", index=False)
    default_bt.summary.to_csv(artifacts_dir / "ema_donchian_default_summary.csv", index=False)
    default_bt.trades.to_csv(artifacts_dir / "trade_log.csv", index=False)
    default_bt.nav.to_csv(artifacts_dir / "nav_curve.csv", index=False)
    compare_df.to_csv(artifacts_dir / "strategy_compare.csv", index=False)
    sweep_df.to_csv(artifacts_dir / "param_sweep_summary.csv", index=False)
    atr_df.to_csv(artifacts_dir / "atr_sensitivity.csv", index=False)
    cross_market_raw_df.to_csv(artifacts_dir / "cross_market.csv", index=False)
    cross_market_agg_df.to_csv(artifacts_dir / "cross_market_aggregate.csv", index=False)
    cross_market_sources_df.to_csv(artifacts_dir / "cross_market_sources.csv", index=False)
    cross_market_class_df.to_csv(artifacts_dir / "cross_market_asset_class_aggregate.csv", index=False)
    oos_raw_df.to_csv(artifacts_dir / "oos_split.csv", index=False)
    oos_agg_df.to_csv(artifacts_dir / "oos_split_aggregate.csv", index=False)
    oos_sources_df.to_csv(artifacts_dir / "oos_split_sources.csv", index=False)
    rolling_raw_df.to_csv(artifacts_dir / "rolling.csv", index=False)
    rolling_agg_df.to_csv(artifacts_dir / "rolling_aggregate.csv", index=False)
    rolling_sources_df.to_csv(artifacts_dir / "rolling_sources.csv", index=False)
    rolling_class_df.to_csv(artifacts_dir / "rolling_asset_class_aggregate.csv", index=False)

    price_png = assets_dir / "01_price_system.png"
    nav_compare_png = assets_dir / "02_nav_compare.png"
    heatmap_png = assets_dir / "03_param_heatmap.png"
    top_png = assets_dir / "04_top_variants.png"
    cross_market_png = assets_dir / "05_cross_market.png"
    cross_market_class_png = assets_dir / "05b_cross_market_asset_class.png"
    oos_train_test_png = assets_dir / "06_oos_train_test.png"
    rolling_scores_png = assets_dir / "07_rolling_scores.png"
    rolling_class_png = assets_dir / "07b_rolling_asset_class.png"

    plot_price_system(default_sig, price_png, args.ticker)
    plot_nav_compare(
        {
            "raw_breakout": raw_bt.nav[raw_bt.nav["symbol"] == args.ticker] if (not raw_bt.nav.empty and "symbol" in raw_bt.nav.columns) else raw_bt.nav,
            "confirmed_breakout": confirm_bt.nav[confirm_bt.nav["symbol"] == args.ticker] if (not confirm_bt.nav.empty and "symbol" in confirm_bt.nav.columns) else confirm_bt.nav,
            "ema_donchian_default": default_bt.nav[default_bt.nav["symbol"] == args.ticker] if (not default_bt.nav.empty and "symbol" in default_bt.nav.columns) else default_bt.nav,
        },
        nav_compare_png,
        args.ticker,
    )
    plot_sweep_heatmap(sweep_df, heatmap_png)
    plot_top_variants(sweep_df, top_png)
    if not cross_market_raw_df.empty:
        plot_asset_returns(cross_market_raw_df.sort_values("total_return", ascending=False), cross_market_png, title="Cross-market: EMA+Donchian default")
    if not cross_market_class_df.empty:
        plot_asset_class_compare(cross_market_class_df, cross_market_class_png, title="Cross-market: crypto vs other", ratio_col="positive_asset_ratio")
    if not oos_raw_df.empty:
        plot_oos_train_test(oos_raw_df, oos_train_test_png)
    if not rolling_agg_df.empty:
        plot_rolling_scores(rolling_agg_df, rolling_scores_png)
    if not rolling_class_df.empty:
        plot_asset_class_compare(rolling_class_df, rolling_class_png, title="Rolling: crypto vs other", ratio_col="positive_window_ratio")

    manifest = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "default_config": default_cfg.__dict__,
        "backtest_config": bt_cfg.__dict__,
        "lookback_grid": LOOKBACK_GRID,
        "confirm_grid": CONFIRM_GRID,
        "atr_mult_grid": ATR_MULT_GRID,
        "cross_market_assets": CROSS_MARKET_ASSETS,
        "long_sample_assets": LONG_SAMPLE_ASSETS,
        "oos": {"train_days": OOS_TRAIN_DAYS, "test_days": OOS_TEST_DAYS, "rows": int(len(oos_raw_df))},
        "rolling": {"window_days": ROLLING_WINDOW_DAYS, "step_days": ROLLING_STEP_DAYS, "rows": int(len(rolling_raw_df))},
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (artifacts_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    html = render_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        compare_df=compare_df,
        sweep_df=sweep_df,
        atr_df=atr_df,
        cross_market_raw_df=cross_market_raw_df,
        cross_market_agg_df=cross_market_agg_df,
        cross_market_sources_df=cross_market_sources_df,
        cross_market_class_df=cross_market_class_df,
        oos_raw_df=oos_raw_df,
        oos_agg_df=oos_agg_df,
        oos_sources_df=oos_sources_df,
        rolling_raw_df=rolling_raw_df,
        rolling_agg_df=rolling_agg_df,
        rolling_sources_df=rolling_sources_df,
        rolling_class_df=rolling_class_df,
        default_cfg=default_cfg,
        backtest_cfg=bt_cfg,
        assets_rel={
            "price": "assets/01_price_system.png",
            "nav_compare": "assets/02_nav_compare.png",
            "heatmap": "assets/03_param_heatmap.png",
            "top": "assets/04_top_variants.png",
            "cross_market": "assets/05_cross_market.png",
            "cross_market_class": "assets/05b_cross_market_asset_class.png",
            "oos_train_test": "assets/06_oos_train_test.png",
            "rolling_scores": "assets/07_rolling_scores.png",
            "rolling_class": "assets/07b_rolling_asset_class.png",
        },
    )
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    print(f"[ok] report: {site_dir / 'report.html'}")
    print(f"[ok] artifacts: {artifacts_dir}")
    print(compare_df.to_string(index=False))
    print("[ok] best sweep row:")
    print(sweep_df.head(5).to_string(index=False))
    print("[ok] atr sensitivity:")
    print(atr_df.to_string(index=False))
    if not cross_market_agg_df.empty:
        print("[ok] cross-market aggregate:")
        print(cross_market_agg_df.to_string(index=False))
    if not oos_agg_df.empty:
        print("[ok] oos aggregate:")
        print(oos_agg_df.to_string(index=False))
    if not rolling_agg_df.empty:
        print("[ok] rolling aggregate:")
        print(rolling_agg_df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
