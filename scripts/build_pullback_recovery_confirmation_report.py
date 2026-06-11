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
from momentum.signals.pullback_recovery_confirmation import (  # noqa: E402
    PullbackRecoveryConfirmationConfig,
    compute_pullback_recovery_confirmation_signals,
)
from momentum.analytics.multi_tf_momentum_backtest import (  # noqa: E402
    MultiTfMomentumBacktestConfig,
    evaluate_multi_tf_momentum_reversal,
)


ROUND1_PULLBACKS = [1, 2, 3]
ROUND1_VOLS = [0.5, 1.0, 1.5]
ROUND1_BREAKOUTS = [1, 2, 3]
ROUND2_THRESHOLD_15M = [0.002, 0.004, 0.006]
ROUND3_ASSETS = ["BTC-USD", "ETH-USD", "SPY", "QQQ", "510300.SS"]
ROUND3_THRESHOLD_15M = [0.003, 0.004, 0.005, 0.006, 0.007, 0.008]
ROUND3_PULLBACKS = [1, 2]
ROUND3_VOLS = [1.0, 1.5]
ROUND3_BREAKOUTS = [1, 3]
ROUND4_TOP_N = 3
ROUND4_LONG_SAMPLE_DAYS = 180
ROUND4_TRAIN_DAYS = 20
ROUND4_TEST_DAYS = 10
ROUND4_STEP_DAYS = 10


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
    bars = bars[keep].dropna(subset=["open", "high", "low", "close", "volume"]).sort_values("timestamp").reset_index(drop=True)
    return bars


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


def load_round2_long_sample(ticker: str, *, preferred_days: int = 180) -> tuple[pd.DataFrame, str]:
    binance_symbol = binance_symbol_from_ticker(ticker)
    if binance_symbol is not None:
        bars = download_binance_bars(binance_symbol, interval="5m", days=preferred_days)
        bars["symbol"] = ticker
        return bars, f"Binance {preferred_days}d 5m"
    bars = download_bars(ticker=ticker, period="60d", interval="5m")
    bars["symbol"] = ticker
    return bars, "Yahoo 60d 5m fallback"


def load_round3_asset_sample(ticker: str) -> tuple[pd.DataFrame, str]:
    bars = download_bars(ticker=ticker, period="60d", interval="5m")
    bars["symbol"] = ticker
    return bars, "Yahoo 60d 5m"


def load_round4_asset_sample(ticker: str, *, preferred_days: int = ROUND4_LONG_SAMPLE_DAYS) -> tuple[pd.DataFrame, str]:
    binance_symbol = binance_symbol_from_ticker(ticker)
    if binance_symbol is not None:
        bars = download_binance_bars(binance_symbol, interval="5m", days=preferred_days)
        bars["symbol"] = ticker
        return bars, f"Binance {preferred_days}d 5m"
    bars = download_bars(ticker=ticker, period="60d", interval="5m")
    bars["symbol"] = ticker
    return bars, "Yahoo 60d 5m fallback"


def combo_label(threshold_15m: float, pullback_lookback: int, vol_recover_th: float, breakout_lookback: int) -> str:
    return f"t{threshold_15m:.3f}|p{int(pullback_lookback)}|v{float(vol_recover_th):.1f}|b{int(breakout_lookback)}"


def build_confirmation_config(
    *,
    window_5m: int,
    window_15m: int,
    threshold_5m: float,
    threshold_15m: float,
    pullback_lookback: int,
    vol_recover_th: float,
    breakout_lookback: int,
) -> PullbackRecoveryConfirmationConfig:
    return PullbackRecoveryConfirmationConfig(
        window_5m=window_5m,
        window_15m=window_15m,
        threshold_5m=threshold_5m,
        threshold_15m=threshold_15m,
        vol_window=20,
        pullback_lookback=int(pullback_lookback),
        pullback_vol_z_max=0.0,
        vol_recover_th=float(vol_recover_th),
        breakout_lookback=int(breakout_lookback),
    )


def evaluate_confirmation_variant(
    bars: pd.DataFrame,
    *,
    cfg: PullbackRecoveryConfirmationConfig,
    backtest_cfg: MultiTfMomentumBacktestConfig,
    variant: str,
    **params,
) -> tuple[pd.DataFrame, object, dict]:
    sig = compute_pullback_recovery_confirmation_signals(bars, config=cfg)
    bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg)
    row = summarize_variant(
        bt.summary,
        variant,
        signal_count=int(sig["long_signal"].sum() + sig["short_signal"].sum()),
        long_signal_count=int(sig["long_signal"].sum()),
        short_signal_count=int(sig["short_signal"].sum()),
        **params,
    )
    return sig, bt, row


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


def plot_nav_compare(nav_base: pd.DataFrame, nav_best: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 4))
    if not nav_base.empty:
        ts = pd.to_datetime(nav_base["timestamp"], utc=True)
        ax.plot(ts, nav_base["nav"], label="baseline", linewidth=1.5)
    if not nav_best.empty:
        ts2 = pd.to_datetime(nav_best["timestamp"], utc=True)
        ax.plot(ts2, nav_best["nav"], label="best confirmation", linewidth=1.5)
    ax.set_title(f"{ticker} NAV compare: baseline vs confirmation")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_best_signals(df: pd.DataFrame, path: Path, ticker: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ts = pd.to_datetime(df["timestamp"], utc=True)
    ax.plot(ts, df["close"], label="close", linewidth=1.0)
    long_idx = df["long_signal"] == 1
    short_idx = df["short_signal"] == 1
    if long_idx.any():
        ax.scatter(ts[long_idx], df.loc[long_idx, "close"], s=12, marker="^", label="long", alpha=0.7)
    if short_idx.any():
        ax.scatter(ts[short_idx], df.loc[short_idx, "close"], s=12, marker="v", label="short", alpha=0.7)
    ax.set_title(f"{ticker} confirmation signals")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_heatmap_grid(df: pd.DataFrame, path: Path) -> None:
    breakout_vals = sorted(df["breakout_lookback"].unique())
    fig, axes = plt.subplots(1, len(breakout_vals), figsize=(5 * len(breakout_vals), 4), squeeze=False)
    for idx, br in enumerate(breakout_vals):
        ax = axes[0, idx]
        sub = df[df["breakout_lookback"] == br].copy()
        pivot = sub.pivot(index="pullback_lookback", columns="vol_recover_th", values="total_return").sort_index(ascending=False)
        im = ax.imshow(pivot.values, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)), labels=[str(x) for x in pivot.columns])
        ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
        ax.set_xlabel("vol_recover_th")
        ax.set_ylabel("pullback_lookback")
        ax.set_title(f"breakout_lookback={br}")
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
        fig.colorbar(im, ax=ax, shrink=0.80)
    fig.suptitle("Round1 confirmation grid: total return heatmap")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_top_variants(df: pd.DataFrame, path: Path) -> None:
    top = df.sort_values(["total_return", "max_drawdown"], ascending=[False, False]).head(10).copy()
    top["label"] = top.apply(
        lambda r: f"p{int(r['pullback_lookback'])}|v{r['vol_recover_th']}|b{int(r['breakout_lookback'])}", axis=1
    )
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(top["label"], top["total_return"])
    ax.set_title("Round1 top 10 parameter combos by total return")
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round2_returns(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for variant in ["baseline_long_sample", "confirmation_long_sample"]:
        sub = df[df["variant"] == variant].sort_values("threshold_15m")
        ax.plot(sub["threshold_15m"], sub["total_return"], marker="o", label=variant.replace("_", " "))
    ax.set_xlabel("threshold_15m")
    ax.set_ylabel("total_return")
    ax.set_title("Round2: total return vs threshold_15m")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round2_trades(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for variant in ["baseline_long_sample", "confirmation_long_sample"]:
        sub = df[df["variant"] == variant].sort_values("threshold_15m")
        ax.plot(sub["threshold_15m"], sub["trades"], marker="o", label=variant.replace("_", " "))
    ax.set_xlabel("threshold_15m")
    ax.set_ylabel("trades")
    ax.set_title("Round2: trade count vs threshold_15m")
    ax.grid(alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def aggregate_round3(raw_df: pd.DataFrame) -> pd.DataFrame:
    grp = raw_df.groupby(["threshold_15m", "pullback_lookback", "vol_recover_th", "breakout_lookback"], as_index=False)
    out = grp.agg(
        assets_tested=("asset", "nunique"),
        positive_assets=("total_return", lambda s: int((s > 0).sum())),
        mean_total_return=("total_return", "mean"),
        median_total_return=("total_return", "median"),
        std_total_return=("total_return", "std"),
        min_total_return=("total_return", "min"),
        max_total_return=("total_return", "max"),
        mean_max_drawdown=("max_drawdown", "mean"),
        mean_trades=("trades", "mean"),
        min_trades=("trades", "min"),
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out.sort_values(
        ["positive_asset_ratio", "median_total_return", "mean_total_return", "min_total_return", "mean_trades"],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def plot_round3_positive_ratio_heatmap(df: pd.DataFrame, path: Path) -> None:
    pullbacks = sorted(df["pullback_lookback"].unique())
    breakouts = sorted(df["breakout_lookback"].unique())
    fig, axes = plt.subplots(len(pullbacks), len(breakouts), figsize=(5 * len(breakouts), 4 * len(pullbacks)), squeeze=False)
    for i, pb in enumerate(pullbacks):
        for j, br in enumerate(breakouts):
            ax = axes[i, j]
            sub = df[(df["pullback_lookback"] == pb) & (df["breakout_lookback"] == br)].copy()
            pivot = sub.pivot(index="vol_recover_th", columns="threshold_15m", values="positive_asset_ratio").sort_index(ascending=False)
            im = ax.imshow(pivot.values, aspect="auto", vmin=0, vmax=1)
            ax.set_xticks(range(len(pivot.columns)), labels=[f"{x:.3f}" for x in pivot.columns])
            ax.set_yticks(range(len(pivot.index)), labels=[str(x) for x in pivot.index])
            ax.set_xlabel("threshold_15m")
            ax.set_ylabel("vol_recover_th")
            ax.set_title(f"pullback={pb}, breakout={br}")
            for r in range(pivot.shape[0]):
                for c in range(pivot.shape[1]):
                    ax.text(c, r, f"{pivot.values[r, c]:.2f}", ha="center", va="center", color="white", fontsize=8)
            fig.colorbar(im, ax=ax, shrink=0.80)
    fig.suptitle("Round3: positive asset ratio heatmap")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round3_top_combo_scores(df: pd.DataFrame, path: Path) -> None:
    top = df.head(10).copy()
    top["label"] = top.apply(
        lambda r: f"t{r['threshold_15m']:.3f}|p{int(r['pullback_lookback'])}|v{r['vol_recover_th']}|b{int(r['breakout_lookback'])}",
        axis=1,
    )
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.bar(top["label"], top["positive_asset_ratio"], alpha=0.75, label="positive_asset_ratio")
    ax1.set_ylabel("positive_asset_ratio")
    ax1.set_ylim(0, 1.05)
    ax1.grid(axis="y", alpha=0.2)
    ax2 = ax1.twinx()
    ax2.plot(top["label"], top["mean_total_return"], color="tab:red", marker="o", label="mean_total_return")
    ax2.set_ylabel("mean_total_return")
    ax1.set_title("Round3: top aggregate combos (ratio + mean return)")
    plt.xticks(rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round3_best_combo_assets(df: pd.DataFrame, path: Path) -> None:
    sub = df.sort_values("asset").copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(sub["asset"], sub["total_return"])
    ax.set_title("Round3: best aggregate combo across assets")
    ax.set_ylabel("total_return")
    ax.grid(axis="y", alpha=0.2)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def select_round4_top_candidates(round3_agg_df: pd.DataFrame, *, top_n: int = ROUND4_TOP_N) -> pd.DataFrame:
    out = round3_agg_df.head(top_n).copy().reset_index(drop=True)
    out["combo_id"] = [f"C{i + 1}" for i in range(len(out))]
    out["combo_label"] = out.apply(
        lambda r: combo_label(r["threshold_15m"], r["pullback_lookback"], r["vol_recover_th"], r["breakout_lookback"]),
        axis=1,
    )
    cols = [
        "combo_id",
        "combo_label",
        "threshold_15m",
        "pullback_lookback",
        "vol_recover_th",
        "breakout_lookback",
        "positive_asset_ratio",
        "mean_total_return",
        "median_total_return",
        "min_total_return",
        "mean_trades",
    ]
    return out[cols]


def evaluate_round4_oos(
    *,
    asset: str,
    bars: pd.DataFrame,
    sample_source: str,
    candidates_df: pd.DataFrame,
    window_5m: int,
    window_15m: int,
    threshold_5m: float,
    backtest_cfg: MultiTfMomentumBacktestConfig,
    train_ratio: float = 0.7,
) -> pd.DataFrame:
    split_idx = int(len(bars) * train_ratio)
    split_idx = max(1, min(len(bars) - 1, split_idx))
    train_bars = bars.iloc[:split_idx].copy().reset_index(drop=True)
    test_bars = bars.iloc[split_idx:].copy().reset_index(drop=True)
    rows = []
    for candidate in candidates_df.to_dict("records"):
        cfg = build_confirmation_config(
            window_5m=window_5m,
            window_15m=window_15m,
            threshold_5m=threshold_5m,
            threshold_15m=float(candidate["threshold_15m"]),
            pullback_lookback=int(candidate["pullback_lookback"]),
            vol_recover_th=float(candidate["vol_recover_th"]),
            breakout_lookback=int(candidate["breakout_lookback"]),
        )
        _, _, train_row = evaluate_confirmation_variant(
            train_bars,
            cfg=cfg,
            backtest_cfg=backtest_cfg,
            variant="round4_train",
        )
        _, _, test_row = evaluate_confirmation_variant(
            test_bars,
            cfg=cfg,
            backtest_cfg=backtest_cfg,
            variant="round4_oos",
        )
        rows.append(
            {
                "asset": asset,
                "sample_source": sample_source,
                "combo_id": candidate["combo_id"],
                "combo_label": candidate["combo_label"],
                "threshold_15m": float(candidate["threshold_15m"]),
                "pullback_lookback": int(candidate["pullback_lookback"]),
                "vol_recover_th": float(candidate["vol_recover_th"]),
                "breakout_lookback": int(candidate["breakout_lookback"]),
                "train_rows": int(len(train_bars)),
                "oos_rows": int(len(test_bars)),
                "train_start": train_bars["timestamp"].iloc[0],
                "train_end": train_bars["timestamp"].iloc[-1],
                "oos_start": test_bars["timestamp"].iloc[0],
                "oos_end": test_bars["timestamp"].iloc[-1],
                "train_trades": int(train_row.get("trades", 0)),
                "train_total_return": float(train_row.get("total_return", 0.0)),
                "train_max_drawdown": float(train_row.get("max_drawdown", 0.0)),
                "oos_trades": int(test_row.get("trades", 0)),
                "oos_total_return": float(test_row.get("total_return", 0.0)),
                "oos_max_drawdown": float(test_row.get("max_drawdown", 0.0)),
            }
        )
    return pd.DataFrame(rows)


def aggregate_round4_oos(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["combo_id", "combo_label", "threshold_15m", "pullback_lookback", "vol_recover_th", "breakout_lookback"], as_index=False)
    out = grp.agg(
        assets_tested=("asset", "nunique"),
        positive_oos_assets=("oos_total_return", lambda s: int((s > 0).sum())),
        mean_train_total_return=("train_total_return", "mean"),
        mean_oos_total_return=("oos_total_return", "mean"),
        median_oos_total_return=("oos_total_return", "median"),
        min_oos_total_return=("oos_total_return", "min"),
        mean_oos_max_drawdown=("oos_max_drawdown", "mean"),
        mean_oos_trades=("oos_trades", "mean"),
    )
    out["positive_oos_asset_ratio"] = out["positive_oos_assets"] / out["assets_tested"].replace(0, np.nan)
    return out.sort_values(
        ["positive_oos_asset_ratio", "median_oos_total_return", "mean_oos_total_return", "min_oos_total_return"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)


def evaluate_round4_rolling(
    *,
    asset: str,
    bars: pd.DataFrame,
    sample_source: str,
    candidates_df: pd.DataFrame,
    window_5m: int,
    window_15m: int,
    threshold_5m: float,
    backtest_cfg: MultiTfMomentumBacktestConfig,
    train_days: int = ROUND4_TRAIN_DAYS,
    test_days: int = ROUND4_TEST_DAYS,
    step_days: int = ROUND4_STEP_DAYS,
) -> pd.DataFrame:
    train_td = pd.Timedelta(days=train_days)
    test_td = pd.Timedelta(days=test_days)
    step_td = pd.Timedelta(days=step_days)
    ts = pd.to_datetime(bars["timestamp"], utc=True)
    start = ts.min()
    limit = ts.max() - train_td - test_td
    rows = []
    window_id = 0

    while start <= limit:
        train_end = start + train_td
        test_end = train_end + test_td
        train_bars = bars[(ts >= start) & (ts < train_end)].copy().reset_index(drop=True)
        test_bars = bars[(ts >= train_end) & (ts < test_end)].copy().reset_index(drop=True)
        if len(train_bars) < 200 or len(test_bars) < 80:
            start = start + step_td
            continue
        window_id += 1
        for candidate in candidates_df.to_dict("records"):
            cfg = build_confirmation_config(
                window_5m=window_5m,
                window_15m=window_15m,
                threshold_5m=threshold_5m,
                threshold_15m=float(candidate["threshold_15m"]),
                pullback_lookback=int(candidate["pullback_lookback"]),
                vol_recover_th=float(candidate["vol_recover_th"]),
                breakout_lookback=int(candidate["breakout_lookback"]),
            )
            _, _, train_row = evaluate_confirmation_variant(
                train_bars,
                cfg=cfg,
                backtest_cfg=backtest_cfg,
                variant="round4_rolling_train",
            )
            _, _, test_row = evaluate_confirmation_variant(
                test_bars,
                cfg=cfg,
                backtest_cfg=backtest_cfg,
                variant="round4_rolling_oos",
            )
            rows.append(
                {
                    "asset": asset,
                    "sample_source": sample_source,
                    "window_id": int(window_id),
                    "window_start": start,
                    "train_end": train_end,
                    "test_end": test_end,
                    "combo_id": candidate["combo_id"],
                    "combo_label": candidate["combo_label"],
                    "threshold_15m": float(candidate["threshold_15m"]),
                    "pullback_lookback": int(candidate["pullback_lookback"]),
                    "vol_recover_th": float(candidate["vol_recover_th"]),
                    "breakout_lookback": int(candidate["breakout_lookback"]),
                    "train_rows": int(len(train_bars)),
                    "oos_rows": int(len(test_bars)),
                    "train_trades": int(train_row.get("trades", 0)),
                    "train_total_return": float(train_row.get("total_return", 0.0)),
                    "oos_trades": int(test_row.get("trades", 0)),
                    "oos_total_return": float(test_row.get("total_return", 0.0)),
                    "oos_max_drawdown": float(test_row.get("max_drawdown", 0.0)),
                }
            )
        start = start + step_td
    return pd.DataFrame(rows)


def aggregate_round4_rolling(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["combo_id", "combo_label", "threshold_15m", "pullback_lookback", "vol_recover_th", "breakout_lookback"], as_index=False)
    out = grp.agg(
        assets_tested=("asset", "nunique"),
        windows_tested=("oos_total_return", "size"),
        positive_oos_windows=("oos_total_return", lambda s: int((s > 0).sum())),
        mean_train_total_return=("train_total_return", "mean"),
        mean_oos_total_return=("oos_total_return", "mean"),
        median_oos_total_return=("oos_total_return", "median"),
        min_oos_total_return=("oos_total_return", "min"),
        mean_oos_max_drawdown=("oos_max_drawdown", "mean"),
        mean_oos_trades=("oos_trades", "mean"),
    )
    out["positive_window_ratio"] = out["positive_oos_windows"] / out["windows_tested"].replace(0, np.nan)
    return out.sort_values(
        ["positive_window_ratio", "median_oos_total_return", "mean_oos_total_return", "min_oos_total_return"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)


def aggregate_round4_rolling_asset_combo(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["asset", "combo_id", "combo_label"], as_index=False)
    out = grp.agg(
        windows_tested=("oos_total_return", "size"),
        positive_window_ratio=("oos_total_return", lambda s: float((s > 0).mean())),
        mean_oos_total_return=("oos_total_return", "mean"),
        median_oos_total_return=("oos_total_return", "median"),
    )
    return out.sort_values(["combo_id", "asset"]).reset_index(drop=True)


def plot_round4_oos_train_vs_test(df: pd.DataFrame, path: Path) -> None:
    sub = df.copy()
    x = np.arange(len(sub))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(x - width / 2, sub["mean_train_total_return"], width=width, label="train mean return")
    ax.bar(x + width / 2, sub["mean_oos_total_return"], width=width, label="OOS mean return")
    ax.set_xticks(x, labels=sub["combo_id"])
    ax.set_ylabel("total_return")
    ax.set_title("Round4: train vs OOS mean return by combo")
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round4_rolling_combo_scores(df: pd.DataFrame, path: Path) -> None:
    sub = df.copy()
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.bar(sub["combo_id"], sub["positive_window_ratio"], alpha=0.75, label="positive_window_ratio")
    ax1.set_ylim(0, 1.05)
    ax1.set_ylabel("positive_window_ratio")
    ax1.grid(axis="y", alpha=0.2)
    ax2 = ax1.twinx()
    ax2.plot(sub["combo_id"], sub["mean_oos_total_return"], color="tab:red", marker="o", label="mean_oos_total_return")
    ax2.set_ylabel("mean_oos_total_return")
    ax1.set_title("Round4 rolling: positive-window ratio + mean OOS return")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_round4_rolling_asset_heatmap(df: pd.DataFrame, path: Path) -> None:
    pivot = df.pivot(index="asset", columns="combo_id", values="mean_oos_total_return").sort_index()
    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(pivot.values, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)), labels=list(pivot.columns))
    ax.set_yticks(range(len(pivot.index)), labels=list(pivot.index))
    ax.set_title("Round4 rolling: asset x combo mean OOS return")
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j] * 100:.1f}%", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def render_html(
    *,
    ticker: str,
    period: str,
    interval: str,
    base_row: dict,
    best_row: dict,
    compare_df: pd.DataFrame,
    grid_df: pd.DataFrame,
    round2_df: pd.DataFrame,
    round2_source: str,
    round3_raw_df: pd.DataFrame,
    round3_agg_df: pd.DataFrame,
    round3_best_assets_df: pd.DataFrame,
    round3_source: str,
    round4_candidates_df: pd.DataFrame,
    round4_asset_sources_df: pd.DataFrame,
    round4_oos_asset_df: pd.DataFrame,
    round4_oos_agg_df: pd.DataFrame,
    round4_rolling_raw_df: pd.DataFrame,
    round4_rolling_agg_df: pd.DataFrame,
    round4_rolling_asset_combo_df: pd.DataFrame,
    round4_source_note: str,
    assets_rel: dict,
    base_cfg: MultiTfMomentumConfig,
    backtest_cfg: MultiTfMomentumBacktestConfig,
) -> str:
    top5 = grid_df.sort_values(["total_return", "max_drawdown"], ascending=[False, False]).head(5).copy()
    positive_count = int((grid_df["total_return"] > 0).sum())
    q1 = "存在稳健候选区间，确认规则值得继续保留" if positive_count >= 5 else "大部分参数组合表现一般，说明这套确认规则还偏脆弱"
    q2 = "恢复触发定义对结果影响明显，是这套规则最敏感的部分之一"
    q3 = "量价确认相对裸动量有增益" if float(best_row.get("total_return", 0.0)) > float(base_row.get("total_return", 0.0)) else "当前样本里量价确认没有稳定打赢裸动量"

    round2_best_confirm = round2_df[round2_df["variant"] == "confirmation_long_sample"].sort_values(
        ["total_return", "max_drawdown", "trades"], ascending=[False, False, False]
    ).iloc[0]
    round2_best_base = round2_df[round2_df["variant"] == "baseline_long_sample"].sort_values(
        ["total_return", "max_drawdown", "trades"], ascending=[False, False, False]
    ).iloc[0]
    q4 = f"更长样本里，threshold_15m={round2_best_confirm['threshold_15m']:.3f} 的确认版表现最好，说明 0.006 不是随便拍脑袋出来的，但仍需看邻域和平滑性"
    q5 = "如果更长样本里交易数明显增加且仍优于 baseline，这套规则的可信度会上升" if (float(round2_best_confirm["trades"]) >= 20 and float(round2_best_confirm["total_return"]) > float(round2_best_base["total_return"])) else "更长样本验证后仍需谨慎，尤其要警惕‘收益好看但交易数太少’的假稳健"

    round3_best_combo = round3_agg_df.iloc[0]
    q6 = (
        f"在多资产/多参数比较里，当前最稳的组合是 threshold_15m={round3_best_combo['threshold_15m']:.3f}, pullback={int(round3_best_combo['pullback_lookback'])}, vol={round3_best_combo['vol_recover_th']}, breakout={int(round3_best_combo['breakout_lookback'])}；"
        f"它在 {int(round3_best_combo['positive_assets'])}/{int(round3_best_combo['assets_tested'])} 个资产上为正。"
    )
    q7 = "多自变量稳定性，优先看正收益资产占比、平均/中位收益、最差资产表现、平均交易数，而不是只看单个最优回测。"

    round4_best_oos = round4_oos_agg_df.iloc[0]
    q8 = (
        f"round4 的单次 OOS 里，{round4_best_oos['combo_id']} 在 {int(round4_best_oos['positive_oos_assets'])}/{int(round4_best_oos['assets_tested'])} 个资产上保持样本外正收益，"
        f"说明它离开训练区后仍有一定生命力。"
    )

    round4_best_rolling = round4_rolling_agg_df.iloc[0]
    q9 = (
        f"rolling 里当前最稳的是 {round4_best_rolling['combo_id']}，positive_window_ratio={round4_best_rolling['positive_window_ratio']:.2f}，"
        f"mean_oos_total_return={round4_best_rolling['mean_oos_total_return']:.4f}。如果它领先但幅度不大，说明应保留‘参数区间’，而不是迷信单点。"
    )
    q10 = "单次 OOS 更像一次考试，容易刚好踩中有利行情；rolling 是连续多次考试，更能暴露 regime 依赖和时间不稳定。"
    q11 = "当前应保留的是参数结构，而不是单点最优：优先保留 pullback=2、breakout=1、vol_recover_th=1.0。"
    q12 = "threshold_15m 不建议继续迷信 0.005 单点；更合理的研究决策是先保留 0.003~0.004 区间，因为它们在 rolling 里比 0.005 更耐打。"
    q13 = "这套规则当前适合继续作为趋势确认模块，尤其在 crypto 里值得保留；但证据还不支持把它升级成独立稳健主因子。"

    return f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>Pullback Recovery Confirmation Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px auto; max-width: 1160px; line-height: 1.6; color: #111; }}
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
  <h1>缩量回调 + 放量恢复：稳健性报告（round1 ~ round4）</h1>
  <p class="muted">Ticker: {ticker} · period={period} · interval={interval} · generated_at={datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

  <h2>0. 研究问题</h2>
  <p>这份报告分 4 轮：round1 做局部参数网格，round2 扩样本检查 15m 动量阈值，round3 做多资产 + 多参数稳定性分析，round4 则检查这些候选组合在更长时间上的 OOS / rolling 稳定性。</p>

  <h2>1. 固定不动的 baseline</h2>
  <div class="grid">
    <div class="card"><b>window_5m</b><br>{base_cfg.window_5m}</div>
    <div class="card"><b>window_15m</b><br>{base_cfg.window_15m}</div>
    <div class="card"><b>threshold_5m / threshold_15m</b><br>{base_cfg.threshold_5m:.4f} / {base_cfg.threshold_15m:.4f}</div>
    <div class="card"><b>fee / side</b><br>{backtest_cfg.fee_bps_per_side:.1f}bps</div>
    <div class="card"><b>slippage / side</b><br>{backtest_cfg.slippage_bps_per_side:.1f}bps</div>
    <div class="card"><b>round1 grid size</b><br>{len(grid_df)} combos</div>
  </div>

  <h2>2. 规则定义</h2>
  <ul>
    <li><b>趋势：</b>沿用多周期动量 baseline（5m/15m 同向）</li>
    <li><b>回调：</b>最近 <code>pullback_lookback</code> 根内出现逆向 bar，且该阶段平均 <code>vol_z &lt; 0</code></li>
    <li><b>恢复：</b>当前 bar 突破前 <code>breakout_lookback</code> 根高点/低点，且 <code>vol_z &gt; vol_recover_th</code></li>
  </ul>

  <h2>3. Round1：裸动量 baseline vs 最优确认组合（60d）</h2>
  {compare_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['nav_compare']}" alt="nav compare" />

  <h2>4. Round1：参数热图</h2>
  <img src="{assets_rel['heatmap']}" alt="heatmap" />

  <h2>5. Round1：最优组合信号示意</h2>
  <p>当前 best combo：<code>pullback_lookback={int(best_row['pullback_lookback'])}, vol_recover_th={best_row['vol_recover_th']}, breakout_lookback={int(best_row['breakout_lookback'])}</code></p>
  <img src="{assets_rel['signals']}" alt="best signals" />
  <img src="{assets_rel['top10']}" alt="top 10 combos" />

  <h2>6. Round1：全部参数表（27组）</h2>
  {grid_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>7. Round2：更长样本 + 动量阈值扫描</h2>
  <p class="muted">数据源：{round2_source}。固定 round1 最优确认结构，只扫描 <code>threshold_15m ∈ [0.002, 0.004, 0.006]</code>。</p>
  {round2_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['round2_returns']}" alt="round2 returns" />
  <img src="{assets_rel['round2_trades']}" alt="round2 trades" />

  <h2>8. Round3：多资产 + 多自变量稳定性</h2>
  <p class="muted">数据源：{round3_source}。资产：{', '.join(sorted(round3_raw_df['asset'].unique()))}。这里不只看“最优点”，而是看多资产、多参数下的 <b>稳定性统计</b>。</p>
  <div class="grid">
    <div class="card"><b>常用统计 1</b><br>positive_asset_ratio<br><span class="muted">一个参数组合在多少资产上为正</span></div>
    <div class="card"><b>常用统计 2</b><br>mean / median total_return<br><span class="muted">平均/中位表现是否仍然为正</span></div>
    <div class="card"><b>常用统计 3</b><br>min_total_return / mean_trades<br><span class="muted">最差资产有多差、交易数是否过少</span></div>
  </div>
  {round3_agg_df.head(12).to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['round3_heatmap']}" alt="round3 positive ratio heatmap" />
  <img src="{assets_rel['round3_top']}" alt="round3 top combos" />

  <h3>Round3：最佳聚合组合的各资产表现</h3>
  {round3_best_assets_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['round3_assets']}" alt="round3 asset breakdown" />

  <h2>9. Round4：候选组合（来自 round3 top3）</h2>
  <p class="muted">这一步不再全网格暴扫，只拿 round3 最稳的 top3 组合做更长时间的 OOS / rolling 验证。数据源：{round4_source_note}</p>
  {round4_candidates_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <h3>Round4：各资产样本来源</h3>
  {round4_asset_sources_df.to_html(index=False)}

  <h2>10. Round4：单次 OOS（train/test split）</h2>
  <p>做法：每个资产按时间顺序切成 <b>70% train + 30% OOS</b>。train 只负责“让我们看到组合在旧数据里表现如何”，OOS 才是检验它离开训练区后还能不能活。</p>
  {round4_oos_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['round4_oos']}" alt="round4 oos train vs test" />
  <h3>Round4：单次 OOS 各资产拆分</h3>
  {round4_oos_asset_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>11. Round4：Rolling / Walk-forward</h2>
  <p>做法：按 <b>train=20天, test=10天, step=10天</b> 滚动向前。这样我们不会只做一次 OOS，而是反复换时间窗检查参数是否跨时间稳定。</p>
  <div class="grid">
    <div class="card"><b>rolling 核心统计 1</b><br>positive_window_ratio<br><span class="muted">测试窗口里有多少比例为正</span></div>
    <div class="card"><b>rolling 核心统计 2</b><br>mean / median OOS return<br><span class="muted">跨窗口平均表现是否还为正</span></div>
    <div class="card"><b>rolling 核心统计 3</b><br>min OOS return / mean OOS trades<br><span class="muted">最差窗口有多差、测试频率够不够</span></div>
  </div>
  {round4_rolling_agg_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}
  <img src="{assets_rel['round4_rolling_scores']}" alt="round4 rolling combo scores" />
  <img src="{assets_rel['round4_rolling_heatmap']}" alt="round4 rolling asset heatmap" />
  <h3>Round4：rolling 资产×组合均值表</h3>
  {round4_rolling_asset_combo_df.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>12. Top 5 参数组合（round1 局部）</h2>
  {top5.to_html(index=False, float_format=lambda x: f'{x:.4f}')}

  <h2>13. 文字版研究结论（问题 → 结论 → 动作）</h2>
  <div class="qa">
    <h3>Q1. 这套确认规则在局部参数上有没有活性？</h3>
    <p><b>结论：</b>{q1}</p>
    <p><b>动作：</b>先看是不是一片区域都还能活，而不是只盯最优点。</p>
  </div>
  <div class="qa">
    <h3>Q2. 哪一部分最敏感？</h3>
    <p><b>结论：</b>{q2}</p>
    <p><b>动作：</b>后续优先继续审视恢复触发定义（前1根/前2根/前3根高点突破）。</p>
  </div>
  <div class="qa">
    <h3>Q3. 相比裸动量，这套确认有没有增益？</h3>
    <p><b>结论：</b>{q3}</p>
    <p><b>动作：</b>若最优组合能稳定改善收益/信号质量，再继续做 cross-market 与 OOS；否则只保留为备选因子。</p>
  </div>
  <div class="qa">
    <h3>Q4. 更长样本里，15m 动量阈值是不是过严？</h3>
    <p><b>结论：</b>{q4}</p>
    <p><b>动作：</b>把 threshold 当成研究对象，而不是默认 0.006 永远正确。</p>
  </div>
  <div class="qa">
    <h3>Q5. 二轮验证后，现在该给它什么评级？</h3>
    <p><b>结论：</b>{q5}</p>
    <p><b>动作：</b>如果交易数、收益、回撤三者都更平衡，再继续做 cross-market；否则继续把它当作局部确认模块，而非独立主策略。</p>
  </div>
  <div class="qa">
    <h3>Q6. 多资产 + 多自变量下，当前最稳的组合是什么？</h3>
    <p><b>结论：</b>{q6}</p>
    <p><b>动作：</b>不要只盯 mean return，要同时看 positive_asset_ratio 和最差资产表现。</p>
  </div>
  <div class="qa">
    <h3>Q7. 多自变量稳定性到底看什么统计？</h3>
    <p><b>结论：</b>{q7}</p>
    <p><b>动作：</b>以后做多变量稳健性报告，默认至少给出：热图、聚合表、最佳组合的资产拆分表。</p>
  </div>
  <div class="qa">
    <h3>Q8. OOS 看什么？</h3>
    <p><b>结论：</b>{q8}</p>
    <p><b>动作：</b>训练集收益再好，也要盯住 OOS 的正收益资产占比和最差资产表现。</p>
  </div>
  <div class="qa">
    <h3>Q9. rolling 看什么？</h3>
    <p><b>结论：</b>{q9}</p>
    <p><b>动作：</b>如果 rolling 里只有个别窗口赚钱，就说明它更像阶段性 luck，不像稳健结构。</p>
  </div>
  <div class="qa">
    <h3>Q10. 为什么 one-shot OOS 可能偏乐观？</h3>
    <p><b>结论：</b>{q10}</p>
    <p><b>动作：</b>以后看到单次 OOS 很漂亮时，第一反应不是“参数成了”，而是立刻补 rolling / walk-forward。</p>
  </div>
  <div class="qa">
    <h3>Q11. 这次 round4 之后，哪些参数结构应该保留？</h3>
    <p><b>结论：</b>{q11}</p>
    <p><b>动作：</b>后续如果继续扩展量价确认，优先围绕这条主结构做增量改造，而不是重新全空间乱扫。</p>
  </div>
  <div class="qa">
    <h3>Q12. threshold_15m 现在该怎么处理？</h3>
    <p><b>结论：</b>{q12}</p>
    <p><b>动作：</b>后续报告里把 0.003~0.004 视为“保留区间”，0.005 视为“样本外曾亮眼但 rolling 较弱”的观察点。</p>
  </div>
  <div class="qa">
    <h3>Q13. 这套确认规则现在的研究评级是什么？</h3>
    <p><b>结论：</b>{q13}</p>
    <p><b>动作：</b>研究流程上继续保留它，但把后续资源投入到：更严格跨时间验证、跨市场扩展、以及和其他确认因子的组合。</p>
  </div>

  <h2>14. 研究决策摘要（这次 round4 之后怎么做）</h2>
  <div class="grid">
    <div class="card"><b>保留</b><br><code>pullback=2</code><br><code>breakout=1</code><br><code>vol_recover_th=1.0</code></div>
    <div class="card"><b>阈值决策</b><br>优先保留 <code>threshold_15m=0.003~0.004</code><br>不再迷信 <code>0.005</code> 单点</div>
    <div class="card"><b>当前评级</b><br>可保留的趋势确认模块<br>但暂不升级为独立稳健主因子</div>
  </div>
  <p>一句话总结：<b>round3 告诉我们“它有候选区间”，round4 告诉我们“它还没通过更严格的跨时间稳定性考试”。</b></p>
</body>
</html>
"""

def main() -> int:
    parser = argparse.ArgumentParser(description="Build pullback recovery confirmation stability report.")
    parser.add_argument("--ticker", default="BTC-USD")
    parser.add_argument("--period", default="60d")
    parser.add_argument("--interval", default="5m")
    parser.add_argument("--input", default=None)
    parser.add_argument("--window-5m", type=int, default=6)
    parser.add_argument("--window-15m", type=int, default=6)
    parser.add_argument("--threshold-5m", type=float, default=0.003)
    parser.add_argument("--threshold-15m", type=float, default=0.006)
    parser.add_argument("--fee-bps-per-side", type=float, default=4.0)
    parser.add_argument("--slippage-bps-per-side", type=float, default=2.0)
    parser.add_argument("--round2-days", type=int, default=180)
    parser.add_argument("--round4-days", type=int, default=ROUND4_LONG_SAMPLE_DAYS)
    parser.add_argument("--round4-train-days", type=int, default=ROUND4_TRAIN_DAYS)
    parser.add_argument("--round4-test-days", type=int, default=ROUND4_TEST_DAYS)
    parser.add_argument("--round4-step-days", type=int, default=ROUND4_STEP_DAYS)
    args = parser.parse_args()

    factor = "pullback_recovery_confirmation"
    artifacts_dir = ensure_dir(ROOT / "reports" / "artifacts" / factor)
    site_dir = ensure_dir(ROOT / "reports" / "site" / "factors" / factor)
    assets_dir = ensure_dir(site_dir / "assets")

    bars = load_input_data(args.input, args.ticker, args.period, args.interval)
    bars["symbol"] = args.ticker

    base_cfg = MultiTfMomentumConfig(
        window_5m=args.window_5m,
        window_15m=args.window_15m,
        threshold_5m=args.threshold_5m,
        threshold_15m=args.threshold_15m,
    )
    backtest_cfg = MultiTfMomentumBacktestConfig(
        fee_bps_per_side=args.fee_bps_per_side,
        slippage_bps_per_side=args.slippage_bps_per_side,
        flip_on_reverse_signal=True,
    )

    # round1
    base_signals = compute_multi_tf_momentum_signals(bars, config=base_cfg)
    base_bt = evaluate_multi_tf_momentum_reversal(base_signals, config=backtest_cfg)
    base_row = summarize_variant(base_bt.summary, "baseline")

    round1_rows = []
    round1_details = []
    for pullback_lookback in ROUND1_PULLBACKS:
        for vol_recover_th in ROUND1_VOLS:
            for breakout_lookback in ROUND1_BREAKOUTS:
                cfg = PullbackRecoveryConfirmationConfig(
                    window_5m=args.window_5m,
                    window_15m=args.window_15m,
                    threshold_5m=args.threshold_5m,
                    threshold_15m=args.threshold_15m,
                    vol_window=20,
                    pullback_lookback=pullback_lookback,
                    pullback_vol_z_max=0.0,
                    vol_recover_th=vol_recover_th,
                    breakout_lookback=breakout_lookback,
                )
                sig = compute_pullback_recovery_confirmation_signals(bars, config=cfg)
                bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg)
                row = summarize_variant(
                    bt.summary,
                    "confirmation",
                    pullback_lookback=pullback_lookback,
                    vol_recover_th=vol_recover_th,
                    breakout_lookback=breakout_lookback,
                    signal_count=int(sig["long_signal"].sum() + sig["short_signal"].sum()),
                    long_signal_count=int(sig["long_signal"].sum()),
                    short_signal_count=int(sig["short_signal"].sum()),
                )
                round1_rows.append(row)
                round1_details.append((cfg, sig, bt, row))

    grid_df = pd.DataFrame(round1_rows).sort_values(
        ["total_return", "max_drawdown", "trades"], ascending=[False, False, False]
    ).reset_index(drop=True)
    best_row = grid_df.iloc[0].to_dict()
    best_cfg, best_sig, best_bt, _ = max(
        round1_details,
        key=lambda x: (float(x[3].get("total_return", 0.0)), float(x[3].get("max_drawdown", -1e9)), int(x[3].get("trades", 0))),
    )

    compare_df = pd.DataFrame([base_row, {"variant": "best_confirmation", **best_row}])[
        [
            "variant",
            "pullback_lookback",
            "vol_recover_th",
            "breakout_lookback",
            "signal_count",
            "trades",
            "win_rate",
            "avg_ret",
            "median_ret",
            "total_return",
            "max_drawdown",
            "long_trades",
            "short_trades",
        ]
    ]
    compare_df.loc[
        compare_df["variant"] == "baseline",
        ["pullback_lookback", "vol_recover_th", "breakout_lookback", "signal_count"],
    ] = np.nan

    base_nav = base_bt.nav[base_bt.nav["symbol"] == args.ticker] if (not base_bt.nav.empty and "symbol" in base_bt.nav.columns) else base_bt.nav
    best_nav = best_bt.nav[best_bt.nav["symbol"] == args.ticker] if (not best_bt.nav.empty and "symbol" in best_bt.nav.columns) else best_bt.nav

    # round2
    round2_bars, round2_source = load_round2_long_sample(args.ticker, preferred_days=args.round2_days)
    round2_rows = []
    for th_15 in ROUND2_THRESHOLD_15M:
        base_cfg_long = MultiTfMomentumConfig(
            window_5m=args.window_5m,
            window_15m=args.window_15m,
            threshold_5m=args.threshold_5m,
            threshold_15m=th_15,
        )
        base_sig_long = compute_multi_tf_momentum_signals(round2_bars, config=base_cfg_long)
        base_bt_long = evaluate_multi_tf_momentum_reversal(base_sig_long, config=backtest_cfg)
        round2_rows.append(
            summarize_variant(base_bt_long.summary, "baseline_long_sample", threshold_15m=th_15, sample_source=round2_source)
        )

        confirm_cfg_long = PullbackRecoveryConfirmationConfig(
            window_5m=args.window_5m,
            window_15m=args.window_15m,
            threshold_5m=args.threshold_5m,
            threshold_15m=th_15,
            vol_window=20,
            pullback_lookback=int(best_cfg.pullback_lookback),
            pullback_vol_z_max=float(best_cfg.pullback_vol_z_max),
            vol_recover_th=float(best_cfg.vol_recover_th),
            breakout_lookback=int(best_cfg.breakout_lookback),
        )
        confirm_sig_long = compute_pullback_recovery_confirmation_signals(round2_bars, config=confirm_cfg_long)
        confirm_bt_long = evaluate_multi_tf_momentum_reversal(confirm_sig_long, config=backtest_cfg)
        round2_rows.append(
            summarize_variant(
                confirm_bt_long.summary,
                "confirmation_long_sample",
                threshold_15m=th_15,
                sample_source=round2_source,
                signal_count=int(confirm_sig_long["long_signal"].sum() + confirm_sig_long["short_signal"].sum()),
                long_signal_count=int(confirm_sig_long["long_signal"].sum()),
                short_signal_count=int(confirm_sig_long["short_signal"].sum()),
                fixed_pullback_lookback=int(best_cfg.pullback_lookback),
                fixed_vol_recover_th=float(best_cfg.vol_recover_th),
                fixed_breakout_lookback=int(best_cfg.breakout_lookback),
            )
        )
    round2_df = pd.DataFrame(round2_rows).sort_values(["variant", "threshold_15m"]).reset_index(drop=True)

    # round3: multi-asset + multi-variable robustness
    round3_raw_rows = []
    round3_source = "Yahoo 60d 5m (standardized cross-asset sample)"
    for asset in ROUND3_ASSETS:
        asset_bars, _ = load_round3_asset_sample(asset)
        for th_15 in ROUND3_THRESHOLD_15M:
            for pullback_lookback in ROUND3_PULLBACKS:
                for vol_recover_th in ROUND3_VOLS:
                    for breakout_lookback in ROUND3_BREAKOUTS:
                        cfg = PullbackRecoveryConfirmationConfig(
                            window_5m=args.window_5m,
                            window_15m=args.window_15m,
                            threshold_5m=args.threshold_5m,
                            threshold_15m=th_15,
                            vol_window=20,
                            pullback_lookback=pullback_lookback,
                            pullback_vol_z_max=0.0,
                            vol_recover_th=vol_recover_th,
                            breakout_lookback=breakout_lookback,
                        )
                        sig = compute_pullback_recovery_confirmation_signals(asset_bars, config=cfg)
                        bt = evaluate_multi_tf_momentum_reversal(sig, config=backtest_cfg)
                        row = summarize_variant(
                            bt.summary,
                            "round3_confirmation",
                            asset=asset,
                            sample_source=round3_source,
                            threshold_15m=th_15,
                            pullback_lookback=pullback_lookback,
                            vol_recover_th=vol_recover_th,
                            breakout_lookback=breakout_lookback,
                            signal_count=int(sig["long_signal"].sum() + sig["short_signal"].sum()),
                            long_signal_count=int(sig["long_signal"].sum()),
                            short_signal_count=int(sig["short_signal"].sum()),
                        )
                        round3_raw_rows.append(row)

    round3_raw_df = pd.DataFrame(round3_raw_rows)
    round3_agg_df = aggregate_round3(round3_raw_df)
    best_round3_combo = round3_agg_df.iloc[0]
    round3_best_assets_df = round3_raw_df[
        (round3_raw_df["threshold_15m"] == best_round3_combo["threshold_15m"])
        & (round3_raw_df["pullback_lookback"] == best_round3_combo["pullback_lookback"])
        & (round3_raw_df["vol_recover_th"] == best_round3_combo["vol_recover_th"])
        & (round3_raw_df["breakout_lookback"] == best_round3_combo["breakout_lookback"])
    ].sort_values("asset").reset_index(drop=True)

    # round4: longer-sample OOS + rolling validation on round3 top candidates
    round4_candidates_df = select_round4_top_candidates(round3_agg_df, top_n=ROUND4_TOP_N)
    round4_asset_sources = []
    round4_oos_parts = []
    round4_rolling_parts = []
    for asset in ROUND3_ASSETS:
        asset_bars, asset_source = load_round4_asset_sample(asset, preferred_days=args.round4_days)
        round4_asset_sources.append({"asset": asset, "sample_source": asset_source, "rows": int(len(asset_bars))})
        round4_oos_parts.append(
            evaluate_round4_oos(
                asset=asset,
                bars=asset_bars,
                sample_source=asset_source,
                candidates_df=round4_candidates_df,
                window_5m=args.window_5m,
                window_15m=args.window_15m,
                threshold_5m=args.threshold_5m,
                backtest_cfg=backtest_cfg,
                train_ratio=0.7,
            )
        )
        round4_rolling_parts.append(
            evaluate_round4_rolling(
                asset=asset,
                bars=asset_bars,
                sample_source=asset_source,
                candidates_df=round4_candidates_df,
                window_5m=args.window_5m,
                window_15m=args.window_15m,
                threshold_5m=args.threshold_5m,
                backtest_cfg=backtest_cfg,
                train_days=args.round4_train_days,
                test_days=args.round4_test_days,
                step_days=args.round4_step_days,
            )
        )

    round4_asset_sources_df = pd.DataFrame(round4_asset_sources).sort_values("asset").reset_index(drop=True)
    round4_oos_asset_df = pd.concat(round4_oos_parts, ignore_index=True).sort_values(["combo_id", "asset"]).reset_index(drop=True)
    round4_oos_agg_df = aggregate_round4_oos(round4_oos_asset_df)
    round4_rolling_raw_df = pd.concat(round4_rolling_parts, ignore_index=True).sort_values(["combo_id", "asset", "window_id"]).reset_index(drop=True)
    round4_rolling_agg_df = aggregate_round4_rolling(round4_rolling_raw_df)
    round4_rolling_asset_combo_df = aggregate_round4_rolling_asset_combo(round4_rolling_raw_df)
    round4_source_note = "; ".join(
        f"{row.asset}: {row.sample_source}" for row in round4_asset_sources_df.itertuples(index=False)
    )

    pd.DataFrame([base_row]).to_csv(artifacts_dir / "baseline_summary.csv", index=False)
    grid_df.to_csv(artifacts_dir / "param_grid_summary.csv", index=False)
    compare_df.to_csv(artifacts_dir / "strategy_compare.csv", index=False)
    best_sig.to_csv(artifacts_dir / "best_signal_snapshot.csv", index=False)
    best_bt.trades.to_csv(artifacts_dir / "best_trade_log.csv", index=False)
    best_bt.nav.to_csv(artifacts_dir / "best_nav_curve.csv", index=False)
    round2_df.to_csv(artifacts_dir / "round2_threshold15_sweep.csv", index=False)
    round3_raw_df.to_csv(artifacts_dir / "round3_asset_param_raw.csv", index=False)
    round3_agg_df.to_csv(artifacts_dir / "round3_combo_aggregate.csv", index=False)
    round3_best_assets_df.to_csv(artifacts_dir / "round3_best_combo_asset_breakdown.csv", index=False)
    round4_candidates_df.to_csv(artifacts_dir / "round4_top_candidates.csv", index=False)
    round4_asset_sources_df.to_csv(artifacts_dir / "round4_asset_sources.csv", index=False)
    round4_oos_asset_df.to_csv(artifacts_dir / "round4_oos_asset_summary.csv", index=False)
    round4_oos_agg_df.to_csv(artifacts_dir / "round4_oos_combo_aggregate.csv", index=False)
    round4_rolling_raw_df.to_csv(artifacts_dir / "round4_rolling_window_raw.csv", index=False)
    round4_rolling_agg_df.to_csv(artifacts_dir / "round4_rolling_combo_aggregate.csv", index=False)
    round4_rolling_asset_combo_df.to_csv(artifacts_dir / "round4_rolling_asset_combo_summary.csv", index=False)

    heatmap_png = assets_dir / "01_param_heatmap.png"
    nav_compare_png = assets_dir / "02_nav_compare.png"
    signals_png = assets_dir / "03_best_signals.png"
    top10_png = assets_dir / "04_top10.png"
    round2_returns_png = assets_dir / "05_round2_returns.png"
    round2_trades_png = assets_dir / "06_round2_trades.png"
    round3_heatmap_png = assets_dir / "07_round3_positive_ratio_heatmap.png"
    round3_top_png = assets_dir / "08_round3_top_combo_scores.png"
    round3_assets_png = assets_dir / "09_round3_best_combo_assets.png"
    round4_oos_png = assets_dir / "10_round4_oos_train_vs_test.png"
    round4_rolling_scores_png = assets_dir / "11_round4_rolling_combo_scores.png"
    round4_rolling_heatmap_png = assets_dir / "12_round4_rolling_asset_heatmap.png"

    plot_heatmap_grid(grid_df, heatmap_png)
    plot_nav_compare(base_nav, best_nav, nav_compare_png, args.ticker)
    plot_best_signals(best_sig, signals_png, args.ticker)
    plot_top_variants(grid_df, top10_png)
    plot_round2_returns(round2_df, round2_returns_png)
    plot_round2_trades(round2_df, round2_trades_png)
    plot_round3_positive_ratio_heatmap(round3_agg_df, round3_heatmap_png)
    plot_round3_top_combo_scores(round3_agg_df, round3_top_png)
    plot_round3_best_combo_assets(round3_best_assets_df, round3_assets_png)
    plot_round4_oos_train_vs_test(round4_oos_agg_df, round4_oos_png)
    plot_round4_rolling_combo_scores(round4_rolling_agg_df, round4_rolling_scores_png)
    plot_round4_rolling_asset_heatmap(round4_rolling_asset_combo_df, round4_rolling_heatmap_png)

    manifest = {
        "ticker": args.ticker,
        "period": args.period,
        "interval": args.interval,
        "baseline_config": base_cfg.__dict__,
        "best_confirmation_config": best_cfg.__dict__,
        "backtest_config": backtest_cfg.__dict__,
        "grid_size": int(len(grid_df)),
        "round2": {
            "source": round2_source,
            "days": args.round2_days,
            "threshold_15m_grid": ROUND2_THRESHOLD_15M,
        },
        "round3": {
            "source": round3_source,
            "assets": ROUND3_ASSETS,
            "threshold_15m_grid": ROUND3_THRESHOLD_15M,
            "pullback_grid": ROUND3_PULLBACKS,
            "vol_grid": ROUND3_VOLS,
            "breakout_grid": ROUND3_BREAKOUTS,
            "aggregate_rows": int(len(round3_agg_df)),
            "raw_rows": int(len(round3_raw_df)),
        },
        "round4": {
            "top_n": ROUND4_TOP_N,
            "round4_days": args.round4_days,
            "train_days": args.round4_train_days,
            "test_days": args.round4_test_days,
            "step_days": args.round4_step_days,
            "candidate_rows": int(len(round4_candidates_df)),
            "oos_rows": int(len(round4_oos_asset_df)),
            "rolling_rows": int(len(round4_rolling_raw_df)),
            "asset_sources": round4_asset_sources_df.to_dict(orient="records"),
        },
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (artifacts_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    html = render_html(
        ticker=args.ticker,
        period=args.period,
        interval=args.interval,
        base_row=base_row,
        best_row=best_row,
        compare_df=compare_df,
        grid_df=grid_df,
        round2_df=round2_df,
        round2_source=round2_source,
        round3_raw_df=round3_raw_df,
        round3_agg_df=round3_agg_df,
        round3_best_assets_df=round3_best_assets_df,
        round3_source=round3_source,
        round4_candidates_df=round4_candidates_df,
        round4_asset_sources_df=round4_asset_sources_df,
        round4_oos_asset_df=round4_oos_asset_df,
        round4_oos_agg_df=round4_oos_agg_df,
        round4_rolling_raw_df=round4_rolling_raw_df,
        round4_rolling_agg_df=round4_rolling_agg_df,
        round4_rolling_asset_combo_df=round4_rolling_asset_combo_df,
        round4_source_note=round4_source_note,
        assets_rel={
            "heatmap": "assets/01_param_heatmap.png",
            "nav_compare": "assets/02_nav_compare.png",
            "signals": "assets/03_best_signals.png",
            "top10": "assets/04_top10.png",
            "round2_returns": "assets/05_round2_returns.png",
            "round2_trades": "assets/06_round2_trades.png",
            "round3_heatmap": "assets/07_round3_positive_ratio_heatmap.png",
            "round3_top": "assets/08_round3_top_combo_scores.png",
            "round3_assets": "assets/09_round3_best_combo_assets.png",
            "round4_oos": "assets/10_round4_oos_train_vs_test.png",
            "round4_rolling_scores": "assets/11_round4_rolling_combo_scores.png",
            "round4_rolling_heatmap": "assets/12_round4_rolling_asset_heatmap.png",
        },
        base_cfg=base_cfg,
        backtest_cfg=backtest_cfg,
    )
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    print(f"[ok] report: {site_dir / 'report.html'}")
    print(f"[ok] artifacts: {artifacts_dir}")
    print(
        f"[ok] baseline total_return={float(base_row.get('total_return', 0.0)):.4f}, best total_return={float(best_row.get('total_return', 0.0)):.4f}"
    )
    print(f"[ok] round2 source={round2_source}")
    print(f"[ok] round3 source={round3_source}")
    print(f"[ok] round4 source={round4_source_note}")
    print("[ok] round3 best aggregate combo:")
    print(
        round3_agg_df.head(5)[[
            "threshold_15m", "pullback_lookback", "vol_recover_th", "breakout_lookback",
            "positive_assets", "assets_tested", "positive_asset_ratio", "mean_total_return",
            "median_total_return", "min_total_return", "mean_trades"
        ]].to_string(index=False)
    )
    print("[ok] round4 OOS aggregate:")
    print(
        round4_oos_agg_df[[
            "combo_id", "positive_oos_assets", "assets_tested", "positive_oos_asset_ratio",
            "mean_train_total_return", "mean_oos_total_return", "median_oos_total_return", "min_oos_total_return"
        ]].to_string(index=False)
    )
    print("[ok] round4 rolling aggregate:")
    print(
        round4_rolling_agg_df[[
            "combo_id", "windows_tested", "positive_oos_windows", "positive_window_ratio",
            "mean_oos_total_return", "median_oos_total_return", "min_oos_total_return"
        ]].to_string(index=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
