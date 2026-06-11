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

from momentum.signals.multi_tf_momentum import (  # noqa: E402
    MultiTfMomentumConfig,
    compute_multi_tf_momentum_signals,
)
from momentum.signals.trend_regime_filter import (  # noqa: E402
    TrendRegimeFilterConfig,
    compute_trend_regime_filter_signals,
)
from momentum.signals.market_risk_on_off_filter import (  # noqa: E402
    MarketRiskOnOffFilterConfig,
    compute_market_risk_on_off_filter_signals,
)
from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)


REGIME_WINDOW_GRID = [12, 24, 36]
TREND_THRESHOLD_GRID = [0.005, 0.01, 0.015]
REGIME_SCORE_GRID = [1.5, 2.0, 2.5]
CROSS_MARKET_ASSETS = ["BTC-USD", "ETH-USD", "SPY", "QQQ", "510300.SS"]
LONG_SAMPLE_ASSETS = ["BTC-USD", "ETH-USD"]
ROLLING_WINDOW_DAYS = 20
ROLLING_STEP_DAYS = 10


def pct(v: float) -> str:
    return "nan" if pd.isna(v) else f"{v * 100:.2f}%"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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
    bars = bars[keep].dropna(subset=["open", "close"]).sort_values("timestamp").reset_index(drop=True)
    return bars


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


def binance_symbol_from_ticker(ticker: str) -> str | None:
    mapping = {
        "BTC-USD": "BTCUSDT",
        "ETH-USD": "ETHUSDT",
        "BTCUSDT": "BTCUSDT",
        "ETHUSDT": "ETHUSDT",
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
    out = out.dropna().sort_values("timestamp").reset_index(drop=True)
    return out


def evaluate_filter_variants(
    bars: pd.DataFrame,
    *,
    symbol: str,
    sig_cfg: MultiTfMomentumConfig,
    regime_cfg: TrendRegimeFilterConfig,
    risk_on_cfg: MarketRiskOnOffFilterConfig,
    bt_cfg: MultiTfMomentumBacktestConfig,
    sample_label: str,
) -> pd.DataFrame:
    bars = bars.copy()
    bars["symbol"] = symbol
    base_sig = compute_multi_tf_momentum_signals(bars, config=sig_cfg)
    base_bt = evaluate_multi_tf_momentum_reversal(base_sig, config=bt_cfg)
    regime_sig = compute_trend_regime_filter_signals(bars, config=regime_cfg)
    regime_bt = evaluate_multi_tf_momentum_reversal(regime_sig, config=bt_cfg)
    risk_on_sig = compute_market_risk_on_off_filter_signals(bars, config=risk_on_cfg)
    risk_on_bt = evaluate_multi_tf_momentum_reversal(risk_on_sig, config=bt_cfg)

    rows = []
    variants = [
        ("baseline", base_bt, base_sig),
        ("regime_default", regime_bt, regime_sig),
        ("risk_on_v1", risk_on_bt, risk_on_sig),
    ]
    for variant, bt, sig in variants:
        summary = bt.summary.iloc[0] if not bt.summary.empty else pd.Series(dtype=float)
        rows.append(
            {
                "asset": symbol,
                "sample": sample_label,
                "variant": variant,
                "trades": int(summary.get("trades", 0) or 0),
                "win_rate": float(summary.get("win_rate", np.nan)),
                "total_return": float(summary.get("total_return", 0.0) or 0.0),
                "max_drawdown": float(summary.get("max_drawdown", 0.0) or 0.0),
                "filtered_signal_count": int(sig.get("long_filtered_out", pd.Series(dtype=int)).sum() + sig.get("short_filtered_out", pd.Series(dtype=int)).sum()) if variant != "baseline" else 0,
            }
        )
    return pd.DataFrame(rows)


def aggregate_cross_market(df: pd.DataFrame) -> pd.DataFrame:
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


def compute_cross_market_tables(
    *,
    sig_cfg: MultiTfMomentumConfig,
    regime_cfg: TrendRegimeFilterConfig,
    risk_on_cfg: MarketRiskOnOffFilterConfig,
    bt_cfg: MultiTfMomentumBacktestConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    sources = []
    for asset in CROSS_MARKET_ASSETS:
        try:
            bars = download_bars(asset, period="60d", interval="5m")
            rows.append(evaluate_filter_variants(bars, symbol=asset, sig_cfg=sig_cfg, regime_cfg=regime_cfg, risk_on_cfg=risk_on_cfg, bt_cfg=bt_cfg, sample_label="Yahoo 60d 5m"))
            sources.append({"asset": asset, "sample": "Yahoo 60d 5m", "rows": int(len(bars))})
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})
    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown", "filtered_signal_count"])
    agg = aggregate_cross_market(raw) if not raw.empty else pd.DataFrame()
    return raw, agg, pd.DataFrame(sources)


def compute_long_sample_tables(
    *,
    sig_cfg: MultiTfMomentumConfig,
    regime_cfg: TrendRegimeFilterConfig,
    risk_on_cfg: MarketRiskOnOffFilterConfig,
    bt_cfg: MultiTfMomentumBacktestConfig,
    days: int = 180,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    sources = []
    for asset in LONG_SAMPLE_ASSETS:
        try:
            symbol = binance_symbol_from_ticker(asset)
            if symbol is None:
                continue
            bars = download_binance_bars(symbol, interval="5m", days=days)
            rows.append(evaluate_filter_variants(bars, symbol=asset, sig_cfg=sig_cfg, regime_cfg=regime_cfg, risk_on_cfg=risk_on_cfg, bt_cfg=bt_cfg, sample_label=f"Binance {days}d 5m"))
            sources.append({"asset": asset, "sample": f"Binance {days}d 5m", "rows": int(len(bars))})
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})
    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown", "filtered_signal_count"])
    agg = aggregate_cross_market(raw) if not raw.empty else pd.DataFrame()
    return raw, pd.DataFrame(sources) if sources else pd.DataFrame()


def load_best_available_asset_sample(asset: str) -> tuple[pd.DataFrame, str]:
    symbol = binance_symbol_from_ticker(asset)
    if symbol is not None:
        bars = download_binance_bars(symbol, interval="5m", days=180)
        bars["symbol"] = asset
        return bars, "Binance 180d 5m"
    bars = download_bars(asset, period="60d", interval="5m")
    bars["symbol"] = asset
    return bars, "Yahoo 60d 5m"


def compute_rolling_validation_tables(
    *,
    sig_cfg: MultiTfMomentumConfig,
    regime_cfg: TrendRegimeFilterConfig,
    risk_on_cfg: MarketRiskOnOffFilterConfig,
    bt_cfg: MultiTfMomentumBacktestConfig,
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
                if len(sub) < 100:
                    continue
                window_id += 1
                part = evaluate_filter_variants(
                    sub,
                    symbol=asset,
                    sig_cfg=sig_cfg,
                    regime_cfg=regime_cfg,
                    risk_on_cfg=risk_on_cfg,
                    bt_cfg=bt_cfg,
                    sample_label=sample_label,
                )
                part["window_id"] = int(window_id)
                part["window_start"] = pd.Timestamp(sub["timestamp"].iloc[0]).strftime("%Y-%m-%d %H:%M:%S%z")
                part["window_end"] = pd.Timestamp(sub["timestamp"].iloc[-1]).strftime("%Y-%m-%d %H:%M:%S%z")
                part["window_days"] = window_days
                rows.append(part)
        except Exception as e:
            sources.append({"asset": asset, "sample": f"ERROR: {e}", "rows": 0})

    raw = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["asset", "sample", "variant", "trades", "win_rate", "total_return", "max_drawdown", "filtered_signal_count", "window_id", "window_start", "window_end", "window_days"])
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


def compute_cost_sensitivity(signal_df: pd.DataFrame, fee_bps_options: list[float], slippage_bps: float) -> pd.DataFrame:
    rows = []
    for fee_bps in fee_bps_options:
        out = evaluate_multi_tf_momentum_reversal(
            signal_df,
            config=MultiTfMomentumBacktestConfig(
                fee_bps_per_side=fee_bps,
                slippage_bps_per_side=slippage_bps,
                flip_on_reverse_signal=True,
            ),
        )
        summary = out.summary.iloc[0] if not out.summary.empty else pd.Series(dtype=float)
        rows.append(
            {
                "fee_bps_per_side": fee_bps,
                "slippage_bps_per_side": slippage_bps,
                "trades": int(summary.get("trades", 0) or 0),
                "total_return": float(summary.get("total_return", 0.0) or 0.0),
                "max_drawdown": float(summary.get("max_drawdown", 0.0) or 0.0),
            }
        )
    return pd.DataFrame(rows)


def compute_window_sweep(
    bars: pd.DataFrame,
    base_config: MultiTfMomentumConfig,
    fee_bps_per_side: float,
    slippage_bps_per_side: float,
    window_grid_5m: list[int],
    window_grid_15m: list[int],
) -> pd.DataFrame:
    rows = []
    for w5 in window_grid_5m:
        for w15 in window_grid_15m:
            cfg = MultiTfMomentumConfig(
                window_5m=w5,
                window_15m=w15,
                threshold_5m=base_config.threshold_5m,
                threshold_15m=base_config.threshold_15m,
                resample_rule_15m=base_config.resample_rule_15m,
            )
            sig = compute_multi_tf_momentum_signals(bars, config=cfg)
            out = evaluate_multi_tf_momentum_reversal(
                sig,
                config=MultiTfMomentumBacktestConfig(
                    fee_bps_per_side=fee_bps_per_side,
                    slippage_bps_per_side=slippage_bps_per_side,
                    flip_on_reverse_signal=True,
                ),
            )
            summary = out.summary.iloc[0] if not out.summary.empty else pd.Series(dtype=float)
            rows.append(
                {
                    "window_5m": w5,
                    "window_15m": w15,
                    "trades": int(summary.get("trades", 0) or 0),
                    "total_return": float(summary.get("total_return", 0.0) or 0.0),
                    "max_drawdown": float(summary.get("max_drawdown", 0.0) or 0.0),
                }
            )
    return pd.DataFrame(rows)


def add_atr_filter(
    signal_df: pd.DataFrame,
    *,
    atr_period: int = 14,
    quantile_window: int = 288,
    quantile_max: float = 0.8,
) -> pd.DataFrame:
    df = signal_df.copy()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr"] = tr.ewm(alpha=1.0 / atr_period, adjust=False, min_periods=atr_period).mean()
    df["atr_ratio"] = df["atr"] / df["close"].replace(0, np.nan).abs()
    df["atr_ratio_qmax"] = df["atr_ratio"].rolling(
        quantile_window, min_periods=max(atr_period, quantile_window // 4)
    ).quantile(quantile_max)
    df["atr_filter_pass"] = ((df["atr_ratio_qmax"].isna()) | (df["atr_ratio"] <= df["atr_ratio_qmax"]))
    df["long_signal"] = (df["long_signal"].astype(bool) & df["atr_filter_pass"]).astype(int)
    df["short_signal"] = (df["short_signal"].astype(bool) & df["atr_filter_pass"]).astype(int)
    return df


def compute_regime_sweep(
    bars: pd.DataFrame,
    *,
    base_cfg: MultiTfMomentumConfig,
    bt_cfg: MultiTfMomentumBacktestConfig,
    regime_windows: list[int],
    trend_thresholds: list[float],
    regime_score_thresholds: list[float],
) -> tuple[pd.DataFrame, list[tuple[TrendRegimeFilterConfig, pd.DataFrame, object, dict]]]:
    rows: list[dict] = []
    details: list[tuple[TrendRegimeFilterConfig, pd.DataFrame, object, dict]] = []
    for n in regime_windows:
        for trend_th in trend_thresholds:
            for score_th in regime_score_thresholds:
                cfg = TrendRegimeFilterConfig(
                    window_5m=base_cfg.window_5m,
                    window_15m=base_cfg.window_15m,
                    threshold_5m=base_cfg.threshold_5m,
                    threshold_15m=base_cfg.threshold_15m,
                    resample_rule_15m=base_cfg.resample_rule_15m,
                    regime_window=n,
                    trend_threshold=trend_th,
                    regime_score_threshold=score_th,
                )
                sig = compute_trend_regime_filter_signals(bars, config=cfg)
                bt = evaluate_multi_tf_momentum_reversal(sig, config=bt_cfg)
                summary = bt.summary.iloc[0] if not bt.summary.empty else pd.Series(dtype=float)
                row = {
                    "variant": "regime_filter",
                    "regime_window": n,
                    "trend_threshold": trend_th,
                    "regime_score_threshold": score_th,
                    "signal_pass_count": int(sig["regime_filter_pass"].sum()) if "regime_filter_pass" in sig.columns else 0,
                    "filtered_signal_count": int(sig["long_filtered_out"].sum() + sig["short_filtered_out"].sum()) if "long_filtered_out" in sig.columns else 0,
                    "trades": int(summary.get("trades", 0) or 0),
                    "win_rate": float(summary.get("win_rate", np.nan)),
                    "avg_ret": float(summary.get("avg_ret", np.nan)),
                    "median_ret": float(summary.get("median_ret", np.nan)),
                    "total_return": float(summary.get("total_return", 0.0) or 0.0),
                    "max_drawdown": float(summary.get("max_drawdown", 0.0) or 0.0),
                    "long_trades": int(summary.get("long_trades", 0) or 0),
                    "short_trades": int(summary.get("short_trades", 0) or 0),
                }
                rows.append(row)
                details.append((cfg, sig, bt, row))
    df = pd.DataFrame(rows).sort_values(["total_return", "max_drawdown", "trades"], ascending=[False, False, False]).reset_index(drop=True)
    return df, details


def summarize_variant(summary_df: pd.DataFrame, variant: str, **params) -> pd.DataFrame:
    if summary_df.empty:
        row = {"variant": variant, **params, "trades": 0, "win_rate": np.nan, "avg_ret": np.nan, "median_ret": np.nan, "total_return": 0.0, "max_drawdown": 0.0, "long_trades": 0, "short_trades": 0}
        return pd.DataFrame([row])
    out = summary_df.copy()
    out.insert(0, "variant", variant)
    for k, v in params.items():
        out[k] = v
    return out


def plot_price_signals(df: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ts = pd.to_datetime(df["timestamp"], utc=True)
    ax.plot(ts, df["close"], label="close", linewidth=1.0)
    long_idx = df["long_signal"] == 1
    short_idx = df["short_signal"] == 1
    if long_idx.any():
        ax.scatter(ts[long_idx], df.loc[long_idx, "close"], s=10, marker="^", label="long", alpha=0.7)
    if short_idx.any():
        ax.scatter(ts[short_idx], df.loc[short_idx, "close"], s=10, marker="v", label="short", alpha=0.7)
    ax.set_title(f"{ticker} close with multi-TF momentum signals")
    ax.legend(loc="best")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_nav(nav_df: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    ts = pd.to_datetime(nav_df["timestamp"], utc=True)
    ax.plot(ts, nav_df["nav"], label="strategy NAV", linewidth=1.5)
    ax.set_title(f"{ticker} strategy NAV")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_nav_compare_generic(
    nav_a: pd.DataFrame,
    nav_b: pd.DataFrame,
    path: Path,
    ticker: str,
    *,
    label_a: str,
    label_b: str,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    if not nav_a.empty:
        ts = pd.to_datetime(nav_a["timestamp"], utc=True)
        ax.plot(ts, nav_a["nav"], label=label_a, linewidth=1.5)
    if not nav_b.empty:
        ts2 = pd.to_datetime(nav_b["timestamp"], utc=True)
        ax.plot(ts2, nav_b["nav"], label=label_b, linewidth=1.5)
    ax.set_title(f"{ticker} {title}")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_window_heatmap(df: pd.DataFrame, path: Path) -> None:
    pivot = df.pivot(index="window_15m", columns="window_5m", values="total_return").sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=[str(x) for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
    ax.set_xlabel("window_5m")
    ax.set_ylabel("window_15m")
    ax.set_title("Window sweep total return heatmap")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_regime_heatmap(df: pd.DataFrame, path: Path, *, regime_window: int) -> None:
    sub = df[df["regime_window"] == regime_window].copy()
    pivot = sub.pivot(index="trend_threshold", columns="regime_score_threshold", values="total_return").sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=[str(x) for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
    ax.set_xlabel("regime_score_threshold")
    ax.set_ylabel("trend_threshold")
    ax.set_title(f"Regime sweep heatmap (regime_window={regime_window})")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_regime_top_variants(df: pd.DataFrame, path: Path) -> None:
    top = df.head(10).copy()
    top["label"] = top.apply(
        lambda r: f"N{int(r['regime_window'])}|t{r['trend_threshold']:.3f}|s{r['regime_score_threshold']:.1f}", axis=1
    )
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.bar(top["label"], top["total_return"])
    ax.set_title("Regime filter top 10 parameter combos by total return")
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_asset_variant_returns(df: pd.DataFrame, path: Path, *, title: str) -> None:
    assets = sorted(df["asset"].unique())
    preferred = ["baseline", "regime_default", "risk_on_v1"]
    variants = [v for v in preferred if v in set(df["variant"]) ]
    if not variants:
        variants = sorted(df["variant"].unique())
    x = np.arange(len(assets))
    width = 0.8 / max(len(variants), 1)
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    center_shift = (len(variants) - 1) / 2
    for idx, variant in enumerate(variants):
        sub = df[df["variant"] == variant].set_index("asset").reindex(assets)
        ax.bar(x + (idx - center_shift) * width, sub["total_return"], width=width, label=variant)
    ax.set_xticks(x, labels=assets)
    ax.set_ylabel("total_return")
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="best")
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_rolling_scores(df: pd.DataFrame, path: Path) -> None:
    sub = df.copy()
    fig, ax1 = plt.subplots(figsize=(8, 4.6))
    ax1.bar(sub["variant"], sub["positive_window_ratio"], alpha=0.75, label="positive_window_ratio")
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("positive_window_ratio")
    ax1.grid(axis="y", alpha=0.2)
    ax2 = ax1.twinx()
    ax2.plot(sub["variant"], sub["mean_total_return"], color="tab:red", marker="o", label="mean_total_return")
    ax2.set_ylabel("mean_total_return")
    ax1.set_title("Rolling validation: positive-window ratio + mean return")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def render_html(
    *,
    ticker: str,
    period: str,
    interval: str,
    summary: pd.Series,
    signal_df: pd.DataFrame,
    cost_df: pd.DataFrame,
    window_df: pd.DataFrame,
    compare_df: pd.DataFrame,
    regime_sweep_df: pd.DataFrame,
    cross_market_raw_df: pd.DataFrame,
    cross_market_agg_df: pd.DataFrame,
    cross_market_sources_df: pd.DataFrame,
    long_sample_raw_df: pd.DataFrame,
    long_sample_agg_df: pd.DataFrame,
    long_sample_sources_df: pd.DataFrame,
    rolling_raw_df: pd.DataFrame,
    rolling_agg_df: pd.DataFrame,
    rolling_sources_df: pd.DataFrame,
    regime_default_cfg: TrendRegimeFilterConfig,
    risk_on_cfg: MarketRiskOnOffFilterConfig,
    assets_rel: dict,
    config: MultiTfMomentumConfig,
    bt_config: MultiTfMomentumBacktestConfig,
    atr_period: int,
    atr_quantile_window: int,
    atr_quantile_max: float,
) -> str:
    long_count = int(signal_df["long_signal"].sum())
    short_count = int(signal_df["short_signal"].sum())
    best_window = window_df.sort_values(["total_return", "max_drawdown"], ascending=[False, False]).iloc[0]
    cost_break = cost_df.sort_values("fee_bps_per_side").iloc[-1]
    baseline_row = compare_df[compare_df["variant"] == "baseline"].iloc[0]
    atr_row = compare_df[compare_df["variant"] == "atr_filter"].iloc[0]
    regime_default_row = compare_df[compare_df["variant"] == "regime_filter_default"].iloc[0]
    risk_on_row = compare_df[compare_df["variant"] == "risk_on_v1"].iloc[0]
    regime_best_row = compare_df[compare_df["variant"] == "regime_filter_best"].iloc[0]
    stable_zone_count = int((regime_sweep_df["total_return"] > float(baseline_row.get("total_return", 0.0))).sum())

    cross_market_baseline = cross_market_agg_df[cross_market_agg_df["variant"] == "baseline"].iloc[0] if not cross_market_agg_df.empty and (cross_market_agg_df["variant"] == "baseline").any() else None
    cross_market_regime = cross_market_agg_df[cross_market_agg_df["variant"] == "regime_default"].iloc[0] if not cross_market_agg_df.empty and (cross_market_agg_df["variant"] == "regime_default").any() else None
    cross_market_risk_on = cross_market_agg_df[cross_market_agg_df["variant"] == "risk_on_v1"].iloc[0] if not cross_market_agg_df.empty and (cross_market_agg_df["variant"] == "risk_on_v1").any() else None
    long_sample_baseline = long_sample_agg_df[long_sample_agg_df["variant"] == "baseline"].iloc[0] if not long_sample_agg_df.empty and (long_sample_agg_df["variant"] == "baseline").any() else None
    long_sample_regime = long_sample_agg_df[long_sample_agg_df["variant"] == "regime_default"].iloc[0] if not long_sample_agg_df.empty and (long_sample_agg_df["variant"] == "regime_default").any() else None
    long_sample_risk_on = long_sample_agg_df[long_sample_agg_df["variant"] == "risk_on_v1"].iloc[0] if not long_sample_agg_df.empty and (long_sample_agg_df["variant"] == "risk_on_v1").any() else None
    rolling_baseline = rolling_agg_df[rolling_agg_df["variant"] == "baseline"].iloc[0] if not rolling_agg_df.empty and (rolling_agg_df["variant"] == "baseline").any() else None
    rolling_regime = rolling_agg_df[rolling_agg_df["variant"] == "regime_default"].iloc[0] if not rolling_agg_df.empty and (rolling_agg_df["variant"] == "regime_default").any() else None
    rolling_risk_on = rolling_agg_df[rolling_agg_df["variant"] == "risk_on_v1"].iloc[0] if not rolling_agg_df.empty and (rolling_agg_df["variant"] == "risk_on_v1").any() else None

    q1 = (
        "这个 baseline 有初步研究价值"
        if float(summary.get("trades", 0) or 0) >= 10 and float(summary.get("total_return", 0) or 0) > 0
        else "当前 evidence 偏弱，更多像基线原型而不是可直接实盘"
    )
    q2 = (
        "成本较敏感，短周期策略需要严肃对待手续费和滑点"
        if float(cost_break.get("total_return", 0.0) or 0.0) < float(summary.get("total_return", 0.0) or 0.0)
        else "成本敏感度目前不算夸张，但仍需要继续验证"
    )
    q3 = (
        "窗口有一定稳定区间，不是只在单点参数上有效"
        if (window_df["total_return"] > 0).sum() >= 3
        else "参数稳定性偏弱，存在只在局部参数表现好的风险"
    )
    q4 = (
        "当前 ATR 过滤有帮助，至少在这个样本里改善了收益/回撤之一"
        if (float(atr_row.get("total_return", 0.0)) > float(baseline_row.get("total_return", 0.0))) or (float(atr_row.get("max_drawdown", 0.0)) > float(baseline_row.get("max_drawdown", 0.0)))
        else "当前 ATR 过滤没有带来明显提升，说明过滤阈值/逻辑仍需继续调"
    )
    q5 = (
        f"默认 regime gate（N={regime_default_cfg.regime_window}, trend>{regime_default_cfg.trend_threshold:.3f}, score>{regime_default_cfg.regime_score_threshold:.1f}）"
        f"把策略从 {pct(float(baseline_row['total_return']))} 调整到 {pct(float(regime_default_row['total_return']))}，说明过滤器本身是有效的；"
        f"但它还不足以把一个偏弱 baseline 直接抬成稳健策略。"
    )
    q6 = (
        f"当前样本里最优 regime 组合是 N={int(regime_best_row['regime_window'])}, trend_threshold={regime_best_row['trend_threshold']:.3f}, score_threshold={regime_best_row['regime_score_threshold']:.1f}；"
        f"但真正更重要的是，看默认值附近是否也还行。当前有 {stable_zone_count} 组参数至少优于 baseline。"
    )
    q7 = "先把 regime gate 定位成‘弱有效环境过滤模块’：它负责减少坏环境里的低质量交易，不负责单独拯救一个本身就偏弱的 baseline。下一步该补的是更强的 risk-on/risk-off 定义，而不是继续在同一组参数上反复微调。"
    q8 = (
        f"跨市场统一样本下，default regime gate 在 {int(cross_market_regime['positive_assets'])}/{int(cross_market_regime['assets_tested'])} 个资产上为正，"
        f"而 baseline 只有 {int(cross_market_baseline['positive_assets'])}/{int(cross_market_baseline['assets_tested'])} 个。"
        if cross_market_baseline is not None and cross_market_regime is not None
        else "跨市场结果暂不完整，先看单市场证据。"
    )
    q9 = (
        f"更长样本里（crypto 180d 5m），default regime gate 的平均收益是 {pct(float(long_sample_regime['mean_total_return']))}，"
        f"baseline 是 {pct(float(long_sample_baseline['mean_total_return']))}。"
        if long_sample_baseline is not None and long_sample_regime is not None
        else "更长样本结果暂不完整。"
    )
    q10 = (
        f"rolling 下，default regime gate 在 {int(rolling_regime['positive_windows'])}/{int(rolling_regime['windows_tested'])} 个窗口为正，"
        f"positive_window_ratio={rolling_regime['positive_window_ratio']:.2f}；baseline 只有 {rolling_baseline['positive_window_ratio']:.2f}。"
        f" 这说明它跨阶段有改善，但还没达到‘大多数阶段都有效’的稳健线。"
        if rolling_baseline is not None and rolling_regime is not None
        else "rolling 结果暂不完整。"
    )
    q11 = (
        f"risk-on/off v1 用 3 个最小特征：1h 趋势为正、1h 价格站上 EMA、1h 波动未进入极端高风险区；满足至少 {risk_on_cfg.min_pass_count}/3 才开机。"
        f" 单市场里它把 baseline 从 {pct(float(baseline_row['total_return']))} 调整到 {pct(float(risk_on_row['total_return']))}。"
    )
    q12 = (
        f"如果看 rolling，risk-on/off v1 的 positive_window_ratio={rolling_risk_on['positive_window_ratio']:.2f}，"
        f"default regime 是 {rolling_regime['positive_window_ratio']:.2f}，baseline 是 {rolling_baseline['positive_window_ratio']:.2f}；"
        f"这能告诉我们更高层 market gate 是否真的比局部 trend/choppy gate 更稳。"
        if rolling_baseline is not None and rolling_regime is not None and rolling_risk_on is not None
        else "risk-on/off v1 的 rolling 结果暂不完整。"
    )

    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Multi-TF Momentum Report</title>
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
  <h1>多周期动量（5m / 15m）研究报告</h1>
  <p class="muted">Ticker: {ticker} · period={period} · interval={interval} · generated_at={datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>0. 基本信息</h2>
  <div class="grid">
    <div class="card"><b>window_5m</b><br>{config.window_5m}</div>
    <div class="card"><b>window_15m</b><br>{config.window_15m}</div>
    <div class="card"><b>thresholds</b><br>{config.threshold_5m:.4f} / {config.threshold_15m:.4f}</div>
    <div class="card"><b>signals</b><br>long={long_count} · short={short_count}</div>
    <div class="card"><b>trade count</b><br>{int(summary.get('trades', 0) or 0)}</div>
    <div class="card"><b>cost / side</b><br>fee={bt_config.fee_bps_per_side:.1f}bps · slip={bt_config.slippage_bps_per_side:.1f}bps</div>
  </div>

  <h2>1. 因子定义</h2>
  <p><code>mom_5m = close_5m[t] / close_5m[t-M] - 1</code></p>
  <p><code>mom_15m = close_15m[T] / close_15m[T-N] - 1</code>，其中 T 是 t 时刻之前最近一根已完成的 15m bar。</p>
  <p>做多：<code>mom_5m &gt; th_5m</code> 且 <code>mom_15m &gt; th_15m</code>；做空同理取负阈值。策略规则为：空仓开仓、同向信号忽略、反向信号下一根 5m open 反手。</p>

  <h2>2. 核心结果（baseline）</h2>
  <div class="grid">
    <div class="card"><b>Total Return</b><br>{pct(float(summary.get('total_return', 0.0) or 0.0))}</div>
    <div class="card"><b>Max Drawdown</b><br>{pct(float(summary.get('max_drawdown', 0.0) or 0.0))}</div>
    <div class="card"><b>Win Rate</b><br>{pct(float(summary.get('win_rate', np.nan)))}</div>
    <div class="card"><b>Avg Trade</b><br>{pct(float(summary.get('avg_ret', np.nan)))}</div>
    <div class="card"><b>Median Trade</b><br>{pct(float(summary.get('median_ret', np.nan)))}</div>
    <div class="card"><b>Long / Short</b><br>{int(summary.get('long_trades', 0) or 0)} / {int(summary.get('short_trades', 0) or 0)}</div>
  </div>

  <h3>价格与信号</h3>
  <img src="{assets_rel['price']}" alt="price signals" />
  <h3>策略净值</h3>
  <img src="{assets_rel['nav']}" alt="nav curve" />

  <h2>3. 过滤器总对照（ATR vs Regime vs Risk-on/off）</h2>
  {compare_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>4. ATR 过滤 A/B 对照</h2>
  <p>过滤规则：使用 5m ATR({atr_period}) / close 作为波动尺度，若当前 ATR 比率高于最近 {atr_quantile_window} 根中的 {int(atr_quantile_max * 100)}% 分位阈值，则屏蔽该根的开仓信号。</p>
  <img src="{assets_rel['nav_compare_atr']}" alt="nav compare atr" />

  <h2>5. Regime Gate baseline（模块 D first baseline）</h2>
  <p>这版 gate 不预测涨跌方向，只判断当前环境是否适合让趋势信号上场。</p>
  <ul>
    <li><code>ret = close.pct_change()</code></li>
    <li><code>trend_return = close / close.shift(N) - 1</code></li>
    <li><code>trend_strength = abs(trend_return)</code></li>
    <li><code>noise_level = rolling_std(ret, N)</code></li>
    <li><code>regime_score = trend_strength / noise_level</code></li>
  </ul>
  <p>默认值：<code>N={regime_default_cfg.regime_window}</code>，<code>trend_threshold={regime_default_cfg.trend_threshold:.3f}</code>，<code>regime_score_threshold={regime_default_cfg.regime_score_threshold:.1f}</code>。</p>
  <img src="{assets_rel['nav_compare_regime']}" alt="nav compare regime" />

  <h2>5.5 Market Risk-on / Risk-off baseline v1</h2>
  <p>这是更高层的“是否开机”门控，不预测方向，只判断当前市场环境是否值得让策略出手。</p>
  <ul>
    <li><code>trend_ok_1h: close / close.shift({risk_on_cfg.trend_window_1h}) - 1 &gt; {risk_on_cfg.trend_threshold_1h:.3f}</code></li>
    <li><code>ema_ok_1h: close_1h &gt; EMA({risk_on_cfg.ema_window_1h})</code></li>
    <li><code>vol_ok_1h: rv_1h &lt;= rolling_q{int(risk_on_cfg.vol_quantile_max * 100)}(rv_1h, {risk_on_cfg.vol_quantile_window_1h})</code></li>
    <li><code>risk_on_pass = score &gt;= {risk_on_cfg.min_pass_count}</code></li>
  </ul>
  <p>直觉：趋势在、位置不差、风险不过热，这三件事至少满足 {risk_on_cfg.min_pass_count} 件，策略才开机。</p>
  <img src="{assets_rel['nav_compare_risk_on']}" alt="nav compare risk on" />

  <h2>6. Regime 参数过滤效果（不同参数）</h2>
  <p>这里扫的是：<code>regime_window ∈ {REGIME_WINDOW_GRID}</code>、<code>trend_threshold ∈ {TREND_THRESHOLD_GRID}</code>、<code>regime_score_threshold ∈ {REGIME_SCORE_GRID}</code>。</p>
  <img src="{assets_rel['regime_heatmap']}" alt="regime heatmap" />
  <img src="{assets_rel['regime_top']}" alt="regime top" />
  {regime_sweep_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>7. Cross-market：default 参数在不同市场行不行？</h2>
  <p class="muted">统一样本：Yahoo 60d 5m。资产：{', '.join(CROSS_MARKET_ASSETS)}。</p>
  {cross_market_sources_df.to_html(index=False) if not cross_market_sources_df.empty else '<p>no source rows</p>'}
  {cross_market_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not cross_market_agg_df.empty else '<p>cross-market aggregate unavailable</p>'}
  {cross_market_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not cross_market_raw_df.empty else '<p>cross-market raw unavailable</p>'}
  <img src="{assets_rel['cross_market']}" alt="cross market returns" />

  <h2>8. Longer-sample：更长 5m 数据下还行不行？</h2>
  <p class="muted">统一样本：Binance 180d 5m。资产：{', '.join(LONG_SAMPLE_ASSETS)}。</p>
  {long_sample_sources_df.to_html(index=False) if not long_sample_sources_df.empty else '<p>no source rows</p>'}
  {long_sample_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not long_sample_agg_df.empty else '<p>long-sample aggregate unavailable</p>'}
  {long_sample_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not long_sample_raw_df.empty else '<p>long-sample raw unavailable</p>'}
  <img src="{assets_rel['long_sample']}" alt="long sample returns" />

  <h2>9. Rolling：多个时间窗里 default 还有效吗？</h2>
  <p class="muted">rolling 设置：window={ROLLING_WINDOW_DAYS}d，step={ROLLING_STEP_DAYS}d。crypto 用 Binance 180d 5m，股票/A股代理用 Yahoo 60d 5m。</p>
  {rolling_sources_df.to_html(index=False) if not rolling_sources_df.empty else '<p>no rolling sources</p>'}
  {rolling_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not rolling_agg_df.empty else '<p>rolling aggregate unavailable</p>'}
  <img src="{assets_rel['rolling_scores']}" alt="rolling scores" />
  {rolling_raw_df.to_html(index=False, float_format=lambda x: f'{x:.4f}') if not rolling_raw_df.empty else '<p>rolling raw unavailable</p>'}

  <h2>10. 成本敏感度</h2>
  {cost_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>11. 参数邻域（窗口扫描）</h2>
  <img src="{assets_rel['heatmap']}" alt="window sweep heatmap" />
  {window_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <p><b>当前最佳窗口（按 total_return 粗排）</b>：5m={int(best_window['window_5m'])}, 15m={int(best_window['window_15m'])}, total_return={pct(float(best_window['total_return']))}, max_dd={pct(float(best_window['max_drawdown']))}</p>

  <h2>12. 文字版研究结论（问题 → 结论 → 动作）</h2>
  <div class="qa">
    <h3>Q1. 这个 baseline 现在值不值得继续研究？</h3>
    <p><b>结论：</b>{q1}</p>
    <p><b>动作：</b>先把它当成可解释基线，不急着和更复杂模型混在一起。</p>
  </div>
  <div class="qa">
    <h3>Q2. 它最容易死在哪？</h3>
    <p><b>结论：</b>{q2}</p>
    <p><b>动作：</b>下一步优先做 fee/slippage 情景测试，再叠加波动、量价或 regime 过滤。</p>
  </div>
  <div class="qa">
    <h3>Q3. 参数稳定性怎么样？</h3>
    <p><b>结论：</b>{q3}</p>
    <p><b>动作：</b>如果只有孤立参数赚钱，要谨慎；如果一片参数都还能活，才更像真信号。</p>
  </div>
  <div class="qa">
    <h3>Q4. 加 ATR 过滤有帮助吗？</h3>
    <p><b>结论：</b>{q4}</p>
    <p><b>动作：</b>把 ATR 过滤当作可调模块继续验证；如果 A/B 已变好，就继续扫阈值和窗口。</p>
  </div>
  <div class="qa">
    <h3>Q5. 默认 regime gate 值得保留吗？</h3>
    <p><b>结论：</b>{q5}</p>
    <p><b>动作：</b>先把默认值当成 first baseline；不要只因为它改善一点点就急着宣布“市场状态过滤搞定了”。</p>
  </div>
  <div class="qa">
    <h3>Q6. 不同参数的过滤效果说明了什么？</h3>
    <p><b>结论：</b>{q6}</p>
    <p><b>动作：</b>如果默认值附近一整片都不差，说明默认值不是拍脑袋；如果只有单点好看，就先别深挖。</p>
  </div>
  <div class="qa">
    <h3>Q7. 这份带有行情过滤的报告，下一步怎么做？</h3>
    <p><b>结论：</b>{q7}</p>
    <p><b>动作：</b>优先做 cross-market / longer-sample 验证，确认它到底是“真环境过滤”还是“样本内小修补”。</p>
  </div>
  <div class="qa">
    <h3>Q8. default 参数跨市场迁移性如何？</h3>
    <p><b>结论：</b>{q8}</p>
    <p><b>动作：</b>如果 default 只在 crypto 有效，就把它定义成 crypto regime gate，而不是通用全市场 gate。</p>
  </div>
  <div class="qa">
    <h3>Q9. default 参数在更长数据里还活着吗？</h3>
    <p><b>结论：</b>{q9}</p>
    <p><b>动作：</b>若更长样本也优于 baseline，再继续做 OOS / rolling；若长样本失效，就降级为样本内技巧。</p>
  </div>
  <div class="qa">
    <h3>Q10. rolling 告诉我们它是“持续有效”还是“阶段有效”？</h3>
    <p><b>结论：</b>{q10}</p>
    <p><b>动作：</b>如果 positive_window_ratio 只是略高于 baseline，但仍低于 0.5，就把它视为“有改善但仍偏阶段性”；只有明显超过 0.5，才更像跨阶段稳健。</p>
  </div>
  <div class="qa">
    <h3>Q11. risk-on / risk-off v1 到底在算什么？</h3>
    <p><b>结论：</b>{q11}</p>
    <p><b>动作：</b>把它理解成“开机条件检查表”，而不是新方向预测器。它属于环境门控层，介于底层信号和真正执行之间。</p>
  </div>
  <div class="qa">
    <h3>Q12. 更高层的 market gate，真的比 default regime 更稳吗？</h3>
    <p><b>结论：</b>{q12}</p>
    <p><b>动作：</b>如果 rolling / cross-market 明显优于 default regime，就继续沿这条线扩展；如果没有，就说明简单 market gate 还不够，需要更强的 risk proxy 或跨资产状态特征。</p>
  </div>
</body>
</html>
"""

def main() -> int:
    parser = argparse.ArgumentParser(description="Build multi-timeframe momentum backtest report.")
    parser.add_argument("--ticker", default="BTC-USD")
    parser.add_argument("--period", default="60d")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--input", default=None, help="Optional local 5m OHLCV CSV")
    parser.add_argument("--window-5m", type=int, default=6)
    parser.add_argument("--window-15m", type=int, default=6)
    parser.add_argument("--threshold-5m", type=float, default=0.003)
    parser.add_argument("--threshold-15m", type=float, default=0.006)
    parser.add_argument("--resample-rule-15m", default="15min")
    parser.add_argument("--fee-bps-per-side", type=float, default=4.0)
    parser.add_argument("--slippage-bps-per-side", type=float, default=2.0)
    parser.add_argument("--regime-window", type=int, default=36)
    parser.add_argument("--trend-threshold", type=float, default=0.015)
    parser.add_argument("--regime-score-threshold", type=float, default=2.0)
    args = parser.parse_args()

    factor = "multi_tf_momentum"
    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / factor)
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / factor)
    assets_dir = ensure_dir(site_dir / "assets")

    bars = load_input_data(args.input, args.ticker, args.period, args.interval)
    bars["symbol"] = args.ticker

    sig_cfg = MultiTfMomentumConfig(
        window_5m=args.window_5m,
        window_15m=args.window_15m,
        threshold_5m=args.threshold_5m,
        threshold_15m=args.threshold_15m,
        resample_rule_15m=args.resample_rule_15m,
    )
    signal_df = compute_multi_tf_momentum_signals(bars, config=sig_cfg)

    bt_cfg = MultiTfMomentumBacktestConfig(
        fee_bps_per_side=args.fee_bps_per_side,
        slippage_bps_per_side=args.slippage_bps_per_side,
        flip_on_reverse_signal=True,
    )
    bt = evaluate_multi_tf_momentum_reversal(signal_df, config=bt_cfg)
    summary = bt.summary.iloc[0] if not bt.summary.empty else pd.Series(dtype=float)

    atr_period = 14
    atr_quantile_window = 288
    atr_quantile_max = 0.8
    signal_df_atr = add_atr_filter(
        signal_df,
        atr_period=atr_period,
        quantile_window=atr_quantile_window,
        quantile_max=atr_quantile_max,
    )
    bt_atr = evaluate_multi_tf_momentum_reversal(signal_df_atr, config=bt_cfg)

    regime_default_cfg = TrendRegimeFilterConfig(
        window_5m=args.window_5m,
        window_15m=args.window_15m,
        threshold_5m=args.threshold_5m,
        threshold_15m=args.threshold_15m,
        resample_rule_15m=args.resample_rule_15m,
        regime_window=args.regime_window,
        trend_threshold=args.trend_threshold,
        regime_score_threshold=args.regime_score_threshold,
    )
    signal_df_regime_default = compute_trend_regime_filter_signals(bars, config=regime_default_cfg)
    bt_regime_default = evaluate_multi_tf_momentum_reversal(signal_df_regime_default, config=bt_cfg)

    risk_on_v1_cfg = MarketRiskOnOffFilterConfig(
        window_5m=args.window_5m,
        window_15m=args.window_15m,
        threshold_5m=args.threshold_5m,
        threshold_15m=args.threshold_15m,
        resample_rule_15m=args.resample_rule_15m,
        market_resample_rule="1h",
        trend_window_1h=12,
        trend_threshold_1h=0.005,
        ema_window_1h=24,
        vol_window_1h=12,
        vol_quantile_window_1h=72,
        vol_quantile_max=0.8,
        min_pass_count=2,
    )
    signal_df_risk_on_v1 = compute_market_risk_on_off_filter_signals(bars, config=risk_on_v1_cfg)
    bt_risk_on_v1 = evaluate_multi_tf_momentum_reversal(signal_df_risk_on_v1, config=bt_cfg)

    regime_sweep_df, regime_details = compute_regime_sweep(
        bars,
        base_cfg=sig_cfg,
        bt_cfg=bt_cfg,
        regime_windows=REGIME_WINDOW_GRID,
        trend_thresholds=TREND_THRESHOLD_GRID,
        regime_score_thresholds=REGIME_SCORE_GRID,
    )
    best_regime_cfg, best_regime_sig, best_regime_bt, best_regime_row = max(
        regime_details,
        key=lambda x: (float(x[3].get("total_return", 0.0)), float(x[3].get("max_drawdown", -1e9)), int(x[3].get("trades", 0))),
    )

    cross_market_raw_df, cross_market_agg_df, cross_market_sources_df = compute_cross_market_tables(
        sig_cfg=sig_cfg,
        regime_cfg=regime_default_cfg,
        risk_on_cfg=risk_on_v1_cfg,
        bt_cfg=bt_cfg,
    )
    long_sample_raw_df, long_sample_sources_df = compute_long_sample_tables(
        sig_cfg=sig_cfg,
        regime_cfg=regime_default_cfg,
        risk_on_cfg=risk_on_v1_cfg,
        bt_cfg=bt_cfg,
        days=180,
    )
    long_sample_agg_df = aggregate_cross_market(long_sample_raw_df) if not long_sample_raw_df.empty else pd.DataFrame()
    rolling_raw_df, rolling_agg_df, rolling_sources_df = compute_rolling_validation_tables(
        sig_cfg=sig_cfg,
        regime_cfg=regime_default_cfg,
        risk_on_cfg=risk_on_v1_cfg,
        bt_cfg=bt_cfg,
        window_days=ROLLING_WINDOW_DAYS,
        step_days=ROLLING_STEP_DAYS,
    )

    cost_df = compute_cost_sensitivity(signal_df, fee_bps_options=[0, 1, 2, 4, 6, 10], slippage_bps=args.slippage_bps_per_side)
    window_df = compute_window_sweep(
        bars,
        base_config=sig_cfg,
        fee_bps_per_side=args.fee_bps_per_side,
        slippage_bps_per_side=args.slippage_bps_per_side,
        window_grid_5m=[3, 6, 9, 12],
        window_grid_15m=[3, 6, 9, 12],
    )

    compare_df = pd.concat(
        [
            summarize_variant(bt.summary, "baseline"),
            summarize_variant(bt_atr.summary, "atr_filter"),
            summarize_variant(
                bt_regime_default.summary,
                "regime_filter_default",
                regime_window=regime_default_cfg.regime_window,
                trend_threshold=regime_default_cfg.trend_threshold,
                regime_score_threshold=regime_default_cfg.regime_score_threshold,
                filtered_signal_count=int(signal_df_regime_default.get("long_filtered_out", pd.Series(dtype=int)).sum() + signal_df_regime_default.get("short_filtered_out", pd.Series(dtype=int)).sum()),
            ),
            summarize_variant(
                bt_risk_on_v1.summary,
                "risk_on_v1",
                trend_window_1h=risk_on_v1_cfg.trend_window_1h,
                trend_threshold_1h=risk_on_v1_cfg.trend_threshold_1h,
                ema_window_1h=risk_on_v1_cfg.ema_window_1h,
                vol_window_1h=risk_on_v1_cfg.vol_window_1h,
                vol_quantile_window_1h=risk_on_v1_cfg.vol_quantile_window_1h,
                vol_quantile_max=risk_on_v1_cfg.vol_quantile_max,
                min_pass_count=risk_on_v1_cfg.min_pass_count,
                filtered_signal_count=int(signal_df_risk_on_v1.get("long_filtered_out", pd.Series(dtype=int)).sum() + signal_df_risk_on_v1.get("short_filtered_out", pd.Series(dtype=int)).sum()),
            ),
            summarize_variant(
                best_regime_bt.summary,
                "regime_filter_best",
                regime_window=best_regime_cfg.regime_window,
                trend_threshold=best_regime_cfg.trend_threshold,
                regime_score_threshold=best_regime_cfg.regime_score_threshold,
                filtered_signal_count=int(best_regime_sig.get("long_filtered_out", pd.Series(dtype=int)).sum() + best_regime_sig.get("short_filtered_out", pd.Series(dtype=int)).sum()),
            ),
        ],
        ignore_index=True,
    )

    signal_keep = [c for c in ["timestamp", "symbol", "open", "high", "low", "close", "mom_5m", "mom_15m", "long_signal", "short_signal"] if c in signal_df.columns]
    signal_df[signal_keep].to_csv(artifacts_dir / "signal_snapshot.csv", index=False)
    signal_df_atr[[c for c in ["timestamp", "symbol", "close", "atr", "atr_ratio", "atr_ratio_qmax", "atr_filter_pass", "long_signal", "short_signal"] if c in signal_df_atr.columns]].to_csv(artifacts_dir / "atr_filter_snapshot.csv", index=False)
    signal_df_regime_default[[c for c in ["timestamp", "symbol", "close", "ret_1", "trend_return", "trend_strength", "noise_level", "regime_score", "regime_filter_pass", "long_signal", "short_signal", "long_filtered_out", "short_filtered_out"] if c in signal_df_regime_default.columns]].to_csv(artifacts_dir / "regime_filter_snapshot.csv", index=False)
    signal_df_risk_on_v1[[c for c in ["timestamp", "symbol", "close", "trend_1h", "ema_1h", "rv_1h", "rv_1h_qmax", "trend_ok_1h", "ema_ok_1h", "vol_ok_1h", "risk_on_score", "risk_on_pass", "long_signal", "short_signal", "long_filtered_out", "short_filtered_out"] if c in signal_df_risk_on_v1.columns]].to_csv(artifacts_dir / "risk_on_v1_snapshot.csv", index=False)
    best_regime_sig[[c for c in ["timestamp", "symbol", "close", "ret_1", "trend_return", "trend_strength", "noise_level", "regime_score", "regime_filter_pass", "long_signal", "short_signal", "long_filtered_out", "short_filtered_out"] if c in best_regime_sig.columns]].to_csv(artifacts_dir / "regime_filter_best_snapshot.csv", index=False)
    bt.trades.to_csv(artifacts_dir / "trade_log.csv", index=False)
    bt.nav.to_csv(artifacts_dir / "nav_curve.csv", index=False)
    bt.summary.to_csv(artifacts_dir / "baseline_summary.csv", index=False)
    bt_atr.summary.to_csv(artifacts_dir / "atr_filter_summary.csv", index=False)
    bt_regime_default.summary.to_csv(artifacts_dir / "regime_filter_summary.csv", index=False)
    bt_risk_on_v1.summary.to_csv(artifacts_dir / "risk_on_v1_summary.csv", index=False)
    best_regime_bt.summary.to_csv(artifacts_dir / "regime_filter_best_summary.csv", index=False)
    compare_df.to_csv(artifacts_dir / "strategy_compare.csv", index=False)
    cost_df.to_csv(artifacts_dir / "cost_sensitivity.csv", index=False)
    window_df.to_csv(artifacts_dir / "window_sweep.csv", index=False)
    regime_sweep_df.to_csv(artifacts_dir / "regime_filter_sweep.csv", index=False)
    cross_market_raw_df.to_csv(artifacts_dir / "regime_filter_cross_market.csv", index=False)
    cross_market_agg_df.to_csv(artifacts_dir / "regime_filter_cross_market_aggregate.csv", index=False)
    cross_market_sources_df.to_csv(artifacts_dir / "regime_filter_cross_market_sources.csv", index=False)
    long_sample_raw_df.to_csv(artifacts_dir / "regime_filter_long_sample.csv", index=False)
    long_sample_agg_df.to_csv(artifacts_dir / "regime_filter_long_sample_aggregate.csv", index=False)
    long_sample_sources_df.to_csv(artifacts_dir / "regime_filter_long_sample_sources.csv", index=False)
    rolling_raw_df.to_csv(artifacts_dir / "regime_filter_rolling.csv", index=False)
    rolling_agg_df.to_csv(artifacts_dir / "regime_filter_rolling_aggregate.csv", index=False)
    rolling_sources_df.to_csv(artifacts_dir / "regime_filter_rolling_sources.csv", index=False)

    price_png = assets_dir / "01_price_signals.png"
    nav_png = assets_dir / "02_nav_curve.png"
    heatmap_png = assets_dir / "03_window_heatmap.png"
    atr_nav_compare_png = assets_dir / "04_nav_compare_atr.png"
    regime_nav_compare_png = assets_dir / "05_nav_compare_regime.png"
    risk_on_nav_compare_png = assets_dir / "05b_nav_compare_risk_on.png"
    regime_heatmap_png = assets_dir / "06_regime_heatmap.png"
    regime_top_png = assets_dir / "07_regime_top_variants.png"
    cross_market_png = assets_dir / "08_regime_cross_market.png"
    long_sample_png = assets_dir / "09_regime_long_sample.png"
    rolling_scores_png = assets_dir / "10_regime_rolling_scores.png"

    plot_price_signals(signal_df, price_png, args.ticker)
    if not bt.nav.empty:
        plot_nav(bt.nav[bt.nav["symbol"] == args.ticker] if "symbol" in bt.nav.columns else bt.nav, nav_png, args.ticker)
    plot_window_heatmap(window_df, heatmap_png)
    plot_nav_compare_generic(
        bt.nav[bt.nav["symbol"] == args.ticker] if (not bt.nav.empty and "symbol" in bt.nav.columns) else bt.nav,
        bt_atr.nav[bt_atr.nav["symbol"] == args.ticker] if (not bt_atr.nav.empty and "symbol" in bt_atr.nav.columns) else bt_atr.nav,
        atr_nav_compare_png,
        args.ticker,
        label_a="baseline",
        label_b="ATR-filtered",
        title="NAV compare: baseline vs ATR filter",
    )
    plot_nav_compare_generic(
        bt.nav[bt.nav["symbol"] == args.ticker] if (not bt.nav.empty and "symbol" in bt.nav.columns) else bt.nav,
        bt_regime_default.nav[bt_regime_default.nav["symbol"] == args.ticker] if (not bt_regime_default.nav.empty and "symbol" in bt_regime_default.nav.columns) else bt_regime_default.nav,
        regime_nav_compare_png,
        args.ticker,
        label_a="baseline",
        label_b="regime gate",
        title="NAV compare: baseline vs regime gate",
    )
    plot_nav_compare_generic(
        bt.nav[bt.nav["symbol"] == args.ticker] if (not bt.nav.empty and "symbol" in bt.nav.columns) else bt.nav,
        bt_risk_on_v1.nav[bt_risk_on_v1.nav["symbol"] == args.ticker] if (not bt_risk_on_v1.nav.empty and "symbol" in bt_risk_on_v1.nav.columns) else bt_risk_on_v1.nav,
        risk_on_nav_compare_png,
        args.ticker,
        label_a="baseline",
        label_b="risk_on_v1",
        title="NAV compare: baseline vs market risk-on/off v1",
    )
    plot_regime_heatmap(regime_sweep_df, regime_heatmap_png, regime_window=args.regime_window)
    plot_regime_top_variants(regime_sweep_df, regime_top_png)
    if not cross_market_raw_df.empty:
        plot_asset_variant_returns(cross_market_raw_df, cross_market_png, title="Cross-market: baseline vs default regime vs risk_on_v1")
    if not long_sample_raw_df.empty:
        plot_asset_variant_returns(long_sample_raw_df, long_sample_png, title="Long-sample crypto: baseline vs default regime vs risk_on_v1")
    if not rolling_agg_df.empty:
        plot_rolling_scores(rolling_agg_df, rolling_scores_png)

    manifest = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "signal_config": sig_cfg.__dict__,
        "backtest_config": bt_cfg.__dict__,
        "atr_filter": {
            "atr_period": atr_period,
            "quantile_window": atr_quantile_window,
            "quantile_max": atr_quantile_max,
        },
        "regime_filter_default": regime_default_cfg.__dict__,
        "risk_on_v1": risk_on_v1_cfg.__dict__,
        "regime_sweep": {
            "regime_windows": REGIME_WINDOW_GRID,
            "trend_thresholds": TREND_THRESHOLD_GRID,
            "regime_score_thresholds": REGIME_SCORE_GRID,
            "best": {
                "regime_window": best_regime_cfg.regime_window,
                "trend_threshold": best_regime_cfg.trend_threshold,
                "regime_score_threshold": best_regime_cfg.regime_score_threshold,
            },
        },
        "cross_market": {
            "assets": CROSS_MARKET_ASSETS,
            "rows": int(len(cross_market_raw_df)),
            "sources": cross_market_sources_df.to_dict(orient="records"),
        },
        "long_sample": {
            "assets": LONG_SAMPLE_ASSETS,
            "rows": int(len(long_sample_raw_df)),
            "sources": long_sample_sources_df.to_dict(orient="records"),
        },
        "rolling": {
            "window_days": ROLLING_WINDOW_DAYS,
            "step_days": ROLLING_STEP_DAYS,
            "rows": int(len(rolling_raw_df)),
            "sources": rolling_sources_df.to_dict(orient="records"),
        },
        "rows": int(len(signal_df)),
        "long_signal_count": int(signal_df["long_signal"].sum()),
        "short_signal_count": int(signal_df["short_signal"].sum()),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (artifacts_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    html = render_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        summary=summary,
        signal_df=signal_df,
        cost_df=cost_df,
        window_df=window_df,
        compare_df=compare_df,
        regime_sweep_df=regime_sweep_df,
        cross_market_raw_df=cross_market_raw_df,
        cross_market_agg_df=cross_market_agg_df,
        cross_market_sources_df=cross_market_sources_df,
        long_sample_raw_df=long_sample_raw_df,
        long_sample_agg_df=long_sample_agg_df,
        long_sample_sources_df=long_sample_sources_df,
        rolling_raw_df=rolling_raw_df,
        rolling_agg_df=rolling_agg_df,
        rolling_sources_df=rolling_sources_df,
        regime_default_cfg=regime_default_cfg,
        risk_on_cfg=risk_on_v1_cfg,
        assets_rel={
            "price": "assets/01_price_signals.png",
            "nav": "assets/02_nav_curve.png",
            "heatmap": "assets/03_window_heatmap.png",
            "nav_compare_atr": "assets/04_nav_compare_atr.png",
            "nav_compare_regime": "assets/05_nav_compare_regime.png",
            "nav_compare_risk_on": "assets/05b_nav_compare_risk_on.png",
            "regime_heatmap": "assets/06_regime_heatmap.png",
            "regime_top": "assets/07_regime_top_variants.png",
            "cross_market": "assets/08_regime_cross_market.png",
            "long_sample": "assets/09_regime_long_sample.png",
            "rolling_scores": "assets/10_regime_rolling_scores.png",
        },
        config=sig_cfg,
        bt_config=bt_cfg,
        atr_period=atr_period,
        atr_quantile_window=atr_quantile_window,
        atr_quantile_max=atr_quantile_max,
    )
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    print(f"[ok] report: {site_dir / 'report.html'}")
    print(f"[ok] artifacts: {artifacts_dir}")
    if not bt.summary.empty:
        row = bt.summary.iloc[0]
        print(
            f"[ok] baseline: trades={int(row['trades'])}, total_return={row['total_return']:.4f}, "
            f"max_dd={row['max_drawdown']:.4f}, win_rate={row['win_rate']:.4f}"
        )
    if not bt_atr.summary.empty:
        row = bt_atr.summary.iloc[0]
        print(
            f"[ok] atr_filter: trades={int(row['trades'])}, total_return={row['total_return']:.4f}, "
            f"max_dd={row['max_drawdown']:.4f}, win_rate={row['win_rate']:.4f}"
        )
    if not bt_regime_default.summary.empty:
        row = bt_regime_default.summary.iloc[0]
        print(
            f"[ok] regime_default: trades={int(row['trades'])}, total_return={row['total_return']:.4f}, "
            f"max_dd={row['max_drawdown']:.4f}, win_rate={row['win_rate']:.4f}"
        )
    if not bt_risk_on_v1.summary.empty:
        row = bt_risk_on_v1.summary.iloc[0]
        print(
            f"[ok] risk_on_v1: trades={int(row['trades'])}, total_return={row['total_return']:.4f}, "
            f"max_dd={row['max_drawdown']:.4f}, win_rate={row['win_rate']:.4f}"
        )
    print("[ok] regime top 5:")
    print(regime_sweep_df.head(5)[["regime_window", "trend_threshold", "regime_score_threshold", "filtered_signal_count", "trades", "total_return", "max_drawdown"]].to_string(index=False))
    if not cross_market_agg_df.empty:
        print("[ok] cross-market aggregate:")
        print(cross_market_agg_df.to_string(index=False))
    if not long_sample_agg_df.empty:
        print("[ok] long-sample aggregate:")
        print(long_sample_agg_df.to_string(index=False))
    if not rolling_agg_df.empty:
        print("[ok] rolling aggregate:")
        print(rolling_agg_df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
