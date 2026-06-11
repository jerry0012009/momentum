#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
import sys

import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals import BoxConsolidationConfig, compute_box_consolidation_signals


ASSET_UNIVERSE = [
    # Index / ETF
    {"name": "上证指数", "ticker": "000001.SS", "asset_class": "A股指数", "label_en": "SSE Composite"},
    {"name": "沪深300ETF", "ticker": "510300.SS", "asset_class": "A股指数", "label_en": "CSI300 ETF"},
    {"name": "中证500ETF", "ticker": "510500.SS", "asset_class": "A股指数", "label_en": "CSI500 ETF"},
    {"name": "创业板ETF", "ticker": "159915.SZ", "asset_class": "A股指数", "label_en": "ChiNext ETF"},
    {"name": "恒生ETF", "ticker": "2800.HK", "asset_class": "港股指数", "label_en": "Hang Seng ETF"},
    {"name": "标普500ETF", "ticker": "SPY", "asset_class": "美股指数", "label_en": "SPY"},
    {"name": "纳指100ETF", "ticker": "QQQ", "asset_class": "美股指数", "label_en": "QQQ"},
    {"name": "道指ETF", "ticker": "DIA", "asset_class": "美股指数", "label_en": "DIA"},
    # Crypto proxy cohort (use liquid majors as broad-crypto proxy when a single total-market index is unavailable)
    {"name": "BTC", "ticker": "BTC-USD", "asset_class": "加密主流（指数代理）", "label_en": "BTC"},
    {"name": "ETH", "ticker": "ETH-USD", "asset_class": "加密主流（指数代理）", "label_en": "ETH"},
    {"name": "SOL", "ticker": "SOL-USD", "asset_class": "加密主流（指数代理）", "label_en": "SOL"},
    {"name": "BNB", "ticker": "BNB-USD", "asset_class": "加密主流（指数代理）", "label_en": "BNB"},
    {"name": "XRP", "ticker": "XRP-USD", "asset_class": "加密主流（指数代理）", "label_en": "XRP"},
    {"name": "ADA", "ticker": "ADA-USD", "asset_class": "加密主流（指数代理）", "label_en": "ADA"},
    # A-share stocks
    {"name": "贵州茅台", "ticker": "600519.SS", "asset_class": "A股个股", "label_en": "Moutai"},
    {"name": "宁德时代", "ticker": "300750.SZ", "asset_class": "A股个股", "label_en": "CATL"},
    {"name": "中国平安", "ticker": "601318.SS", "asset_class": "A股个股", "label_en": "Ping An"},
    {"name": "招商银行", "ticker": "600036.SS", "asset_class": "A股个股", "label_en": "CMB"},
    {"name": "比亚迪A", "ticker": "002594.SZ", "asset_class": "A股个股", "label_en": "BYD A"},
    # HK stocks
    {"name": "腾讯控股", "ticker": "0700.HK", "asset_class": "港股个股", "label_en": "Tencent"},
    {"name": "阿里巴巴-SW", "ticker": "9988.HK", "asset_class": "港股个股", "label_en": "Alibaba HK"},
    {"name": "小米集团", "ticker": "1810.HK", "asset_class": "港股个股", "label_en": "Xiaomi"},
    {"name": "美团-W", "ticker": "3690.HK", "asset_class": "港股个股", "label_en": "Meituan"},
    {"name": "比亚迪股份", "ticker": "1211.HK", "asset_class": "港股个股", "label_en": "BYD HK"},
    # US stocks
    {"name": "苹果", "ticker": "AAPL", "asset_class": "美股个股", "label_en": "Apple"},
    {"name": "微软", "ticker": "MSFT", "asset_class": "美股个股", "label_en": "Microsoft"},
    {"name": "英伟达", "ticker": "NVDA", "asset_class": "美股个股", "label_en": "NVIDIA"},
    {"name": "亚马逊", "ticker": "AMZN", "asset_class": "美股个股", "label_en": "Amazon"},
    {"name": "特斯拉", "ticker": "TSLA", "asset_class": "美股个股", "label_en": "Tesla"},
]

SYMBOLS = {x["name"]: x["ticker"] for x in ASSET_UNIVERSE}
ASSET_CLASS_MAP = {x["name"]: x["asset_class"] for x in ASSET_UNIVERSE}
PLOT_LABELS = {x["name"]: x["label_en"] for x in ASSET_UNIVERSE}

BASE_CFG = BoxConsolidationConfig()
HOLDS = [5, 10, 20, 30]
MODES = ["long_only", "short_only", "long_short"]
HORIZONS = [1, 3, 5, 10, 20]

DECLINE_GRID = [0.08, 0.12, 0.16]
NARROW_RANGE_GRID = [0.06, 0.08, 0.10]
BOX_LOOKBACK_GRID = [20, 30, 40]
COST_BPS_LIST = [0, 10, 20, 50]

OOS_TRAIN_DAYS = 504
OOS_TEST_DAYS = 126
OOS_STEP_DAYS = 126
OOS_DECLINE_GRID = [0.10, 0.12]
OOS_NARROW_GRID = [0.07, 0.09]
OOS_BOX_LOOKBACK_GRID = [30]


@dataclass
class BacktestResult:
    nav: pd.Series
    trades: pd.DataFrame
    in_position: pd.Series


def pct(v: float) -> str:
    return "nan" if pd.isna(v) else f"{v * 100:.2f}%"


def num(v: float, d: int = 2) -> str:
    return "nan" if pd.isna(v) else f"{v:.{d}f}"


def _bucket(ac: str) -> str:
    if "加密" in ac:
        return "Crypto"
    if "指数" in ac:
        return "Index"
    if "个股" in ac:
        return "Stock"
    return "Other"


def configure_matplotlib_fonts() -> None:
    preferred = [
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "Microsoft YaHei",
        "PingFang SC",
        "SimHei",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = [name for name in preferred if name in available]
    plt.rcParams["font.sans-serif"] = chosen + ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def classify_decline_bin(v: float) -> str:
    if pd.isna(v):
        return "unknown"
    if v <= -0.35:
        return "deep (<=-35%)"
    if v <= -0.20:
        return "medium (-35%~-20%)"
    if v <= -0.12:
        return "shallow (-20%~-12%)"
    return "weak (> -12%)"


def download_bars(ticker: str, period: str = "10y", interval: str = "1d") -> pd.DataFrame:
    raw = yf.download(ticker, period=period, interval=interval, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {ticker}")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]

    bars = raw.reset_index().rename(
        columns={
            "Date": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars[["timestamp", "open", "high", "low", "close", "volume"]]
    bars = bars.dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)
    bars = bars[(bars["open"] > 0) & (bars["high"] > 0) & (bars["low"] > 0) & (bars["close"] > 0)].reset_index(drop=True)
    bars["volume"] = bars["volume"].fillna(0.0)
    if bars.empty:
        raise ValueError(f"No positive-price bars for {ticker}")
    return bars


def run_nonoverlap_backtest(
    sig: pd.DataFrame,
    hold_days: int,
    mode: str,
    long_col: str = "accumulation_ready",
    short_col: str = "downwave",
    fee_bps_roundtrip: float = 0.0,
) -> BacktestResult:
    df = sig.sort_values("timestamp").reset_index(drop=True).copy()
    n = len(df)
    nav = np.full(n, np.nan, dtype=float)
    in_pos = np.zeros(n, dtype=float)
    fee = fee_bps_roundtrip / 10000.0

    current_nav = 1.0
    cursor = 0
    i = 0
    trades: List[dict] = []

    while i < n - 1:
        long_sig = int(df.loc[i, long_col]) == 1 if long_col in df.columns else False
        short_sig = int(df.loc[i, short_col]) == 1 if short_col in df.columns else False

        side = None
        signal = None
        if mode == "long_only":
            if long_sig and not short_sig:
                side = "long"
                signal = long_col
        elif mode == "short_only":
            if short_sig and not long_sig:
                side = "short"
                signal = short_col
        else:
            if long_sig and not short_sig:
                side = "long"
                signal = long_col
            elif short_sig and not long_sig:
                side = "short"
                signal = short_col

        if side is None:
            i += 1
            continue

        entry_i = i + 1
        exit_i = i + hold_days
        if exit_i >= n:
            break

        entry_open = float(df.loc[entry_i, "open"])
        if not np.isfinite(entry_open) or entry_open <= 0:
            i += 1
            continue

        if cursor <= entry_i - 1:
            nav[cursor:entry_i] = current_nav

        if side == "long":
            trade_ret = float(df.loc[exit_i, "close"] / entry_open - 1.0)
            trade_path = df.loc[entry_i:exit_i, "close"].astype(float) / entry_open - 1.0
        else:
            trade_ret = float(entry_open / df.loc[exit_i, "close"] - 1.0)
            trade_path = entry_open / df.loc[entry_i:exit_i, "close"].astype(float) - 1.0

        trade_ret -= fee

        entry_ts = pd.to_datetime(df.loc[entry_i, "timestamp"], utc=True)
        exit_ts = pd.to_datetime(df.loc[exit_i, "timestamp"], utc=True)
        days = max((exit_ts - entry_ts).days, 1)

        for k in range(entry_i, exit_i + 1):
            frac = (k - entry_i + 1) / max(1, (exit_i - entry_i + 1))
            nav[k] = current_nav * (1.0 + trade_ret * frac)
            in_pos[k] = 1.0

        current_nav = current_nav * (1.0 + trade_ret)
        trades.append(
            {
                "entry_i": int(entry_i),
                "exit_i": int(exit_i),
                "entry_ts": entry_ts,
                "exit_ts": exit_ts,
                "signal": signal,
                "side": side,
                "hold_days": int(days),
                "net_ret": trade_ret,
                "mae": float(trade_path.min()) if len(trade_path) else np.nan,
                "mfe": float(trade_path.max()) if len(trade_path) else np.nan,
                "win": int(trade_ret > 0),
            }
        )

        cursor = exit_i + 1
        i = exit_i + 1

    if cursor < n:
        nav[cursor:] = current_nav

    idx = pd.to_datetime(df["timestamp"], utc=True)
    nav_s = pd.Series(nav, index=idx, name="nav").ffill().fillna(1.0)
    inpos_s = pd.Series(in_pos, index=idx, name="in_position")
    trades_df = pd.DataFrame(trades)
    return BacktestResult(nav=nav_s, trades=trades_df, in_position=inpos_s)


def calc_metrics(nav: pd.Series, trades: pd.DataFrame, in_position: pd.Series) -> dict:
    nav = nav.astype(float)
    ret = nav.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0)

    nav0 = float(nav.iloc[0])
    navn = float(nav.iloc[-1])
    ratio = navn / nav0 if nav0 != 0 else np.nan
    total_return = float(ratio - 1.0) if np.isfinite(ratio) else np.nan

    days = max((nav.index[-1] - nav.index[0]).days, 1)
    if np.isfinite(ratio) and ratio > 0:
        cagr = float(ratio ** (365.0 / days) - 1.0)
    else:
        cagr = np.nan

    vol = float(ret.std(ddof=0) * np.sqrt(252.0))
    sharpe = float((ret.mean() * 252.0) / vol) if vol > 0 else np.nan

    dd = nav / nav.cummax() - 1.0
    mdd = float(dd.min())

    trade_count = int(len(trades))
    win_rate = float(trades["win"].mean()) if trade_count > 0 else np.nan

    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "trade_count": trade_count,
        "win_rate": win_rate,
        "avg_hold_days": float(trades["hold_days"].mean()) if trade_count > 0 else np.nan,
        "avg_trade_ret": float(trades["net_ret"].mean()) if trade_count > 0 else np.nan,
        "exposure": float(in_position.mean()) if len(in_position) else np.nan,
    }


def build_variants(s: pd.DataFrame) -> Dict[str, dict]:
    return {
        "A_narrow_only_long": {
            "mode": "long_only",
            "long_col": "narrow_accum_ready",
            "short_col": "downwave",
        },
        "B_union_long": {
            "mode": "long_only",
            "long_col": "accumulation_ready",
            "short_col": "downwave",
        },
        "C_union_long_down_short": {
            "mode": "long_short",
            "long_col": "accumulation_ready",
            "short_col": "downwave",
        },
    }


def main() -> None:
    root = ROOT
    artifact_dir = root / "reports" / "artifacts" / "box_consolidation"
    site_dir = root / "reports" / "site" / "factors" / "box_consolidation"
    asset_dir = site_dir / "assets"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)
    configure_matplotlib_fonts()

    market_data: Dict[str, pd.DataFrame] = {}
    signal_data: Dict[str, pd.DataFrame] = {}
    loaded_names: List[str] = []
    failed_rows: List[dict] = []
    coverage_rows: List[dict] = []

    for item in ASSET_UNIVERSE:
        name = item["name"]
        ticker = item["ticker"]
        try:
            bars = download_bars(ticker)
            sig = compute_box_consolidation_signals(bars, config=BASE_CFG)
            sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)

            market_data[name] = bars
            signal_data[name] = sig
            loaded_names.append(name)

            coverage_rows.append(
                {
                    "market_name": name,
                    "ticker": ticker,
                    "asset_class": ASSET_CLASS_MAP[name],
                    "bars": int(len(bars)),
                    "start": str(pd.to_datetime(bars["timestamp"].min(), utc=True).date()),
                    "end": str(pd.to_datetime(bars["timestamp"].max(), utc=True).date()),
                }
            )
        except Exception as e:
            failed_rows.append({"market_name": name, "ticker": ticker, "error": str(e)})

    coverage = pd.DataFrame(coverage_rows).sort_values(["asset_class", "market_name"]) if coverage_rows else pd.DataFrame()
    failed_df = pd.DataFrame(failed_rows)
    coverage.to_csv(artifact_dir / "universe_coverage.csv", index=False)
    failed_df.to_csv(artifact_dir / "universe_failed.csv", index=False)

    rows: List[dict] = []
    nav_store: Dict[tuple, pd.Series] = {}
    trades_store: Dict[tuple, pd.DataFrame] = {}

    for name in loaded_names:
        sig = signal_data[name]
        bh = float(sig["close"].iloc[-1] / sig["close"].iloc[0] - 1.0)

        for mode in MODES:
            for hold in HOLDS:
                r = run_nonoverlap_backtest(sig, hold_days=hold, mode=mode)
                m = calc_metrics(r.nav, r.trades, r.in_position)
                rows.append(
                    {
                        "market_name": name,
                        "ticker": SYMBOLS[name],
                        "asset_class": ASSET_CLASS_MAP[name],
                        "mode": mode,
                        "hold_days": hold,
                        "narrow_signal_count": int(sig["narrow_accum_ready"].sum()),
                        "box_breakout_count": int(sig["box_breakout_ready"].sum()),
                        "accum_signal_count": int(sig["accumulation_ready"].sum()),
                        "downwave_count": int(sig["downwave"].sum()) if "downwave" in sig.columns else 0,
                        "buyhold_ret": bh,
                        **m,
                    }
                )
                nav_store[(name, mode, hold)] = r.nav
                trades_store[(name, mode, hold)] = r.trades

    cross_df = pd.DataFrame(rows).sort_values(["mode", "market_name", "hold_days"]) if rows else pd.DataFrame()
    if not cross_df.empty:
        cross_df["market_bucket"] = cross_df["asset_class"].map(_bucket)
    cross_df.to_csv(artifact_dir / "cross_market_metrics.csv", index=False)

    suitability = (
        cross_df[cross_df["hold_days"] == 10]
        .groupby(["market_bucket", "mode"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["mode", "median_cagr"], ascending=[True, False])
        if not cross_df.empty
        else pd.DataFrame()
    )
    suitability.to_csv(artifact_dir / "market_suitability_summary.csv", index=False)

    region_strength = (
        cross_df[(cross_df["hold_days"] == 10) & (cross_df["mode"] == "long_only")]
        .assign(region=lambda d: d["asset_class"].str.replace("个股", "", regex=False).str.replace("指数", "", regex=False))
        .groupby(["region", "market_bucket"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["region", "market_bucket"])
        if not cross_df.empty
        else pd.DataFrame()
    )
    region_strength.to_csv(artifact_dir / "region_index_vs_stock_strength.csv", index=False)

    summary_df = (
        cross_df.groupby(["mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["mode", "hold_days"])
        if not cross_df.empty
        else pd.DataFrame()
    )
    summary_df.to_csv(artifact_dir / "baseline_summary.csv", index=False)

    # event study
    ev_rows = []
    for name in loaded_names:
        s = signal_data[name].reset_index(drop=True)
        close = s["close"].astype(float)
        for sig_col in ["narrow_accum_ready", "box_breakout_ready", "accumulation_ready"]:
            for idx in s.index[s[sig_col] == 1]:
                for h in HORIZONS:
                    if idx + h >= len(s):
                        continue
                    r = float(close.iloc[idx + h] / close.iloc[idx] - 1.0)
                    dd = float(s.loc[idx, "drawdown_from_peak"]) if "drawdown_from_peak" in s.columns else np.nan
                    ev_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP[name],
                            "market_bucket": _bucket(ASSET_CLASS_MAP[name]),
                            "signal": sig_col,
                            "horizon": h,
                            "ret": r,
                            "drawdown_from_peak": dd,
                            "decline_bin": classify_decline_bin(dd),
                        }
                    )
        if "downwave" in s.columns:
            for idx in s.index[s["downwave"] == 1]:
                for h in HORIZONS:
                    if idx + h >= len(s):
                        continue
                    r = float(close.iloc[idx] / close.iloc[idx + h] - 1.0)
                    dd = float(s.loc[idx, "drawdown_from_peak"]) if "drawdown_from_peak" in s.columns else np.nan
                    ev_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP[name],
                            "market_bucket": _bucket(ASSET_CLASS_MAP[name]),
                            "signal": "downwave_short",
                            "horizon": h,
                            "ret": r,
                            "drawdown_from_peak": dd,
                            "decline_bin": classify_decline_bin(dd),
                        }
                    )

    event_df = pd.DataFrame(ev_rows)
    event_df.to_csv(artifact_dir / "event_study_raw.csv", index=False)
    event_summary = (
        event_df.groupby(["signal", "horizon"], as_index=False)
        .agg(
            samples=("ret", "size"),
            mean_ret=("ret", "mean"),
            median_ret=("ret", "median"),
            win_rate=("ret", lambda s: float((s > 0).mean())),
        )
        .sort_values(["signal", "horizon"])
        if not event_df.empty
        else pd.DataFrame()
    )
    event_summary.to_csv(artifact_dir / "event_study_summary.csv", index=False)

    # parameter sensitivity
    param_rows = []
    for name in loaded_names:
        bars = market_data[name]
        for decline in DECLINE_GRID:
            for narrow in NARROW_RANGE_GRID:
                for box_lb in BOX_LOOKBACK_GRID:
                    cfg = replace(BASE_CFG, min_decline_pct=decline, narrow_range_max=narrow, box_lookback=box_lb)
                    sig = compute_box_consolidation_signals(bars, config=cfg)
                    rr = run_nonoverlap_backtest(sig, hold_days=10, mode="long_short")
                    mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                    param_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP[name],
                            "min_decline_pct": decline,
                            "narrow_range_max": narrow,
                            "box_lookback": box_lb,
                            "narrow_signal_count": int(sig["narrow_accum_ready"].sum()),
                            "box_breakout_count": int(sig["box_breakout_ready"].sum()),
                            **mm,
                        }
                    )

    param_df = pd.DataFrame(param_rows)
    param_df.to_csv(artifact_dir / "param_grid_metrics.csv", index=False)
    param_summary = (
        param_df.groupby(["min_decline_pct", "narrow_range_max", "box_lookback"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["median_cagr", "median_sharpe"], ascending=False)
        .reset_index(drop=True)
        if not param_df.empty
        else pd.DataFrame()
    )
    param_summary.to_csv(artifact_dir / "param_grid_summary.csv", index=False)

    # A/B/C strategy compare
    ab_rows = []
    for name in loaded_names:
        s = signal_data[name]
        variants = build_variants(s)
        for vname, cfg_v in variants.items():
            rr = run_nonoverlap_backtest(
                s,
                hold_days=10,
                mode=cfg_v["mode"],
                long_col=cfg_v["long_col"],
                short_col=cfg_v["short_col"],
            )
            mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
            ab_rows.append({"market_name": name, "asset_class": ASSET_CLASS_MAP[name], "strategy": vname, **mm})
    ab_df = pd.DataFrame(ab_rows)
    ab_df.to_csv(artifact_dir / "strategy_ab_compare_by_market.csv", index=False)
    ab_summary = (
        ab_df.groupby("strategy", as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values("median_cagr", ascending=False)
        if not ab_df.empty
        else pd.DataFrame()
    )
    ab_summary.to_csv(artifact_dir / "strategy_ab_compare_summary.csv", index=False)

    # rolling OOS (small grid)
    oos_rows = []
    for name, bars in market_data.items():
        n = len(bars)
        for decline in OOS_DECLINE_GRID:
            for narrow in OOS_NARROW_GRID:
                for box_lb in OOS_BOX_LOOKBACK_GRID:
                    cfg = replace(BASE_CFG, min_decline_pct=decline, narrow_range_max=narrow, box_lookback=box_lb)
                    sig = compute_box_consolidation_signals(bars, config=cfg)
                    sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)

                    fold = 0
                    start = 0
                    while start + OOS_TRAIN_DAYS + OOS_TEST_DAYS <= n:
                        ts = start + OOS_TRAIN_DAYS
                        te = ts + OOS_TEST_DAYS
                        test = sig.iloc[ts:te].copy().reset_index(drop=True)
                        if len(test) < 40:
                            start += OOS_STEP_DAYS
                            fold += 1
                            continue

                        rr = run_nonoverlap_backtest(test, hold_days=10, mode="long_short")
                        mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                        oos_rows.append(
                            {
                                "market_name": name,
                                "asset_class": ASSET_CLASS_MAP[name],
                                "min_decline_pct": decline,
                                "narrow_range_max": narrow,
                                "box_lookback": box_lb,
                                "fold": fold,
                                "test_start": str(test["timestamp"].iloc[0])[:10],
                                "test_end": str(test["timestamp"].iloc[-1])[:10],
                                **mm,
                            }
                        )
                        start += OOS_STEP_DAYS
                        fold += 1

    oos_df = pd.DataFrame(oos_rows)
    oos_df.to_csv(artifact_dir / "oos_by_fold.csv", index=False)
    oos_summary = (
        oos_df.groupby(["min_decline_pct", "narrow_range_max", "box_lookback"], as_index=False)
        .agg(
            samples=("cagr", "size"),
            median_cagr=("cagr", "median"),
            iqr_cagr=("cagr", lambda s: float(np.nanquantile(s, 0.75) - np.nanquantile(s, 0.25))),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
            median_max_drawdown=("max_drawdown", "median"),
        )
        .sort_values(["median_cagr", "pass_rate"], ascending=False)
        if not oos_df.empty
        else pd.DataFrame()
    )
    oos_summary.to_csv(artifact_dir / "oos_summary.csv", index=False)

    # annual bull/bear decomposition
    annual_rows = []
    for name in loaded_names:
        s = signal_data[name].copy()
        s["timestamp"] = pd.to_datetime(s["timestamp"], utc=True)
        s = s.sort_values("timestamp").reset_index(drop=True)
        s["year"] = s["timestamp"].dt.year

        bh_year = s.groupby("year", as_index=False).agg(start=("close", "first"), end=("close", "last"))
        bh_year["benchmark_ret"] = bh_year["end"] / bh_year["start"] - 1.0
        bh_map = dict(zip(bh_year["year"], bh_year["benchmark_ret"]))

        variants = build_variants(s)
        strat_yearly: Dict[str, pd.Series] = {}
        for vname, cfg_v in variants.items():
            rr = run_nonoverlap_backtest(
                s,
                hold_days=10,
                mode=cfg_v["mode"],
                long_col=cfg_v["long_col"],
                short_col=cfg_v["short_col"],
            )
            nav = rr.nav.to_frame("nav")
            nav["year"] = nav.index.year
            y = nav.groupby("year", as_index=False).agg(start=("nav", "first"), end=("nav", "last"))
            y[vname] = y["end"] / y["start"] - 1.0
            strat_yearly[vname] = y.set_index("year")[vname]

        for y in sorted(bh_map.keys()):
            bench = float(bh_map.get(y, np.nan))
            regime = "bull" if (pd.notna(bench) and bench > 0) else "bear"
            for vname in variants.keys():
                sr = float(strat_yearly[vname].get(y, np.nan)) if vname in strat_yearly else np.nan
                annual_rows.append(
                    {
                        "market_name": name,
                        "asset_class": ASSET_CLASS_MAP[name],
                        "market_bucket": _bucket(ASSET_CLASS_MAP[name]),
                        "year": int(y),
                        "market_regime": regime,
                        "strategy": vname,
                        "benchmark_ret": bench,
                        "strategy_ret": sr,
                        "excess_ret": sr - bench if pd.notna(sr) and pd.notna(bench) else np.nan,
                        "beat_benchmark": int(sr > bench) if pd.notna(sr) and pd.notna(bench) else np.nan,
                    }
                )

    annual_df = pd.DataFrame(annual_rows)
    annual_df.to_csv(artifact_dir / "annual_strategy_vs_benchmark.csv", index=False)

    annual_summary = (
        annual_df.groupby(["market_bucket", "strategy", "market_regime"], as_index=False)
        .agg(
            samples=("excess_ret", "size"),
            median_benchmark=("benchmark_ret", "median"),
            median_strategy=("strategy_ret", "median"),
            median_excess=("excess_ret", "median"),
            beat_rate=("beat_benchmark", "mean"),
        )
        .sort_values(["market_bucket", "strategy", "market_regime"])
        if not annual_df.empty
        else pd.DataFrame()
    )
    annual_summary.to_csv(artifact_dir / "annual_regime_excess_summary.csv", index=False)

    annual_overall = (
        annual_df.groupby(["market_bucket", "strategy"], as_index=False)
        .agg(
            samples=("excess_ret", "size"),
            beat_rate=("beat_benchmark", "mean"),
            median_excess=("excess_ret", "median"),
            median_strategy=("strategy_ret", "median"),
            median_benchmark=("benchmark_ret", "median"),
        )
        .sort_values(["market_bucket", "median_excess"], ascending=[True, False])
        if not annual_df.empty
        else pd.DataFrame()
    )
    annual_overall.to_csv(artifact_dir / "annual_regime_excess_overall.csv", index=False)

    strategy_asset_class_summary = (
        ab_df.groupby(["asset_class", "strategy"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["strategy", "median_cagr"], ascending=[True, False])
        if not ab_df.empty
        else pd.DataFrame()
    )
    strategy_asset_class_summary.to_csv(artifact_dir / "strategy_asset_class_summary.csv", index=False)

    annual_asset_class_summary = (
        annual_df.groupby(["asset_class", "strategy", "market_regime"], as_index=False)
        .agg(
            samples=("excess_ret", "size"),
            median_benchmark=("benchmark_ret", "median"),
            median_strategy=("strategy_ret", "median"),
            median_excess=("excess_ret", "median"),
            beat_rate=("beat_benchmark", "mean"),
        )
        .sort_values(["asset_class", "strategy", "market_regime"])
        if not annual_df.empty
        else pd.DataFrame()
    )
    annual_asset_class_summary.to_csv(artifact_dir / "annual_asset_class_regime_summary.csv", index=False)

    event_asset_class_summary = (
        event_df[event_df["horizon"] == 10]
        .groupby(["asset_class", "signal"], as_index=False)
        .agg(
            samples=("ret", "size"),
            mean_ret=("ret", "mean"),
            median_ret=("ret", "median"),
            win_rate=("ret", lambda s: float((s > 0).mean())),
        )
        .sort_values(["signal", "mean_ret"], ascending=[True, False])
        if not event_df.empty
        else pd.DataFrame()
    )
    event_asset_class_summary.to_csv(artifact_dir / "event_asset_class_h10_summary.csv", index=False)

    event_decline_summary = (
        event_df[
            (event_df["horizon"] == 10)
            & (event_df["signal"].isin(["narrow_accum_ready", "box_breakout_ready", "accumulation_ready"]))
        ]
        .groupby(["signal", "decline_bin"], as_index=False)
        .agg(
            samples=("ret", "size"),
            mean_ret=("ret", "mean"),
            median_ret=("ret", "median"),
            win_rate=("ret", lambda s: float((s > 0).mean())),
        )
        .sort_values(["signal", "mean_ret"], ascending=[True, False])
        if not event_df.empty
        else pd.DataFrame()
    )
    event_decline_summary.to_csv(artifact_dir / "event_decline_context_h10_summary.csv", index=False)

    # cost scenario
    cost_rows = []
    for name in loaded_names:
        s = signal_data[name]
        for mode in ["long_only", "long_short"]:
            for fee_bps in COST_BPS_LIST:
                rr = run_nonoverlap_backtest(s, hold_days=10, mode=mode, fee_bps_roundtrip=fee_bps)
                mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                cost_rows.append(
                    {
                        "market_name": name,
                        "asset_class": ASSET_CLASS_MAP[name],
                        "mode": mode,
                        "fee_bps_roundtrip": fee_bps,
                        **mm,
                    }
                )
    cost_df = pd.DataFrame(cost_rows)
    cost_df.to_csv(artifact_dir / "cost_scenario_by_market.csv", index=False)
    cost_summary = (
        cost_df.groupby(["mode", "fee_bps_roundtrip"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["mode", "fee_bps_roundtrip"])
        if not cost_df.empty
        else pd.DataFrame()
    )
    cost_summary.to_csv(artifact_dir / "cost_scenario_summary.csv", index=False)

    # failure monitor + tail risk
    fail_rows = []
    tr_all = []
    for name in loaded_names:
        tr = trades_store.get((name, "long_short", 10), pd.DataFrame()).copy()
        if tr.empty:
            continue
        tr["exit_ts"] = pd.to_datetime(tr["exit_ts"], utc=True)
        end = tr["exit_ts"].max()
        cut6 = end - pd.Timedelta(days=180)
        recent = tr[tr["exit_ts"] >= cut6]
        hist = tr[tr["exit_ts"] < cut6]
        wr_hist = float(hist["win"].mean()) if len(hist) else float(tr["win"].mean())
        wr_recent = float(recent["win"].mean()) if len(recent) else np.nan

        status = "degrade" if pd.notna(wr_recent) and wr_recent < wr_hist - 0.08 else "normal"
        action = "降级为过滤器/减仓" if status == "degrade" else "正常运行"
        fail_rows.append({"market_name": name, "win_rate_hist": wr_hist, "win_rate_recent6m": wr_recent, "status": status, "action": action})
        tr_all.append(tr[["net_ret", "mae", "mfe"]])

    failure_df = pd.DataFrame(fail_rows)
    failure_df.to_csv(artifact_dir / "failure_monitor.csv", index=False)

    if tr_all:
        tt = pd.concat(tr_all, ignore_index=True)
        q5 = float(np.nanquantile(tt["net_ret"], 0.05))
        worst = tt[tt["net_ret"] <= q5]
        tail_df = pd.DataFrame(
            [
                {
                    "mode": "long_short",
                    "hold_days": 10,
                    "p5_trade_ret": q5,
                    "avg_worst5_ret": float(worst["net_ret"].mean()) if len(worst) else np.nan,
                    "max_loss_trade": float(tt["net_ret"].min()),
                    "avg_mae": float(tt["mae"].mean()),
                    "avg_mfe": float(tt["mfe"].mean()),
                    "position_size_hint": float(min(1.0, 0.02 / abs(q5))) if q5 < 0 else 1.0,
                }
            ]
        )
    else:
        tail_df = pd.DataFrame()
    tail_df.to_csv(artifact_dir / "tail_risk_summary.csv", index=False)

    # aggregate nav (equal-weight of available long_short hold10)
    nav_list = [nav_store[k] for k in nav_store if k[1] == "long_short" and k[2] == 10]
    if nav_list:
        nav_df = pd.concat(nav_list, axis=1).sort_index().ffill()
        ret_df = nav_df.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0.0)
        ret_mean = ret_df.mean(axis=1)
        agg_nav = (1.0 + ret_mean).cumprod()
    else:
        agg_nav = pd.Series(dtype=float)

    # plots
    # fig1 heatmap long_short cagr (hold10)
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    ls10 = cross_df[(cross_df["mode"] == "long_short") & (cross_df["hold_days"] == 10)].copy()
    if not ls10.empty:
        ls10 = ls10.sort_values("cagr", ascending=False).reset_index(drop=True)
        vals = ls10["cagr"].values.reshape(1, -1)
        vlim = float(np.nanquantile(np.abs(vals), 0.95)) if np.isfinite(vals).any() else 0.2
        im = ax.imshow(vals, cmap="RdYlGn", aspect="auto", vmin=-vlim, vmax=vlim)
        ax.set_xticks(np.arange(len(ls10)))
        ax.set_xticklabels([PLOT_LABELS.get(x, x) for x in ls10["market_name"]], rotation=70, ha="right", fontsize=8)
        ax.set_yticks([0])
        ax.set_yticklabels(["long_short@hold10 CAGR"])
        fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Cross-Market Heatmap: Box Consolidation (long_short, hold=10)")
    fig.savefig(asset_dir / "01_heatmap_ls_cagr.png", dpi=170)
    plt.close(fig)

    # fig2 event study curves
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for sig_name, color in [
        ("narrow_accum_ready", "tab:blue"),
        ("box_breakout_ready", "tab:green"),
        ("accumulation_ready", "tab:orange"),
        ("downwave_short", "tab:red"),
    ]:
        d = event_summary[event_summary["signal"] == sig_name].sort_values("horizon") if not event_summary.empty else pd.DataFrame()
        if d.empty:
            continue
        ax.plot(d["horizon"], d["mean_ret"], marker="o", label=sig_name, color=color)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_xlabel("horizon (days)")
    ax.set_ylabel("mean event return")
    ax.set_title("Event Study Curves")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(asset_dir / "02_event_study_curves.png", dpi=170)
    plt.close(fig)

    # fig3 hold robustness
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for mode, color in [("long_only", "tab:blue"), ("short_only", "tab:red"), ("long_short", "tab:purple")]:
        d = summary_df[summary_df["mode"] == mode].sort_values("hold_days") if not summary_df.empty else pd.DataFrame()
        if d.empty:
            continue
        ax.plot(d["hold_days"], d["median_cagr"], marker="o", label=mode, color=color)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_xlabel("hold days")
    ax.set_ylabel("median CAGR")
    ax.set_title("Hold Robustness Curves")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(asset_dir / "03_hold_robustness_curves.png", dpi=170)
    plt.close(fig)

    # fig4 param heatmap (box_lookback=30)
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    p4 = param_summary[param_summary["box_lookback"] == 30].copy() if not param_summary.empty else pd.DataFrame()
    if not p4.empty:
        piv = p4.pivot(index="min_decline_pct", columns="narrow_range_max", values="median_cagr")
        im = ax.imshow(piv.values, cmap="RdYlGn", aspect="auto")
        ax.set_xticks(np.arange(len(piv.columns)))
        ax.set_xticklabels([num(c, 2) for c in piv.columns])
        ax.set_yticks(np.arange(len(piv.index)))
        ax.set_yticklabels([num(i, 2) for i in piv.index])
        ax.set_xlabel("narrow_range_max")
        ax.set_ylabel("min_decline_pct")
        fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Param Sensitivity Heatmap (box_lookback=30)")
    fig.savefig(asset_dir / "04_param_sensitivity_heatmap.png", dpi=170)
    plt.close(fig)

    # fig5 aggregate nav & drawdown
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, constrained_layout=True)
    if not agg_nav.empty:
        dd = agg_nav / agg_nav.cummax() - 1.0
        ax1.plot(agg_nav.index, agg_nav.values, color="tab:blue")
        ax2.fill_between(dd.index, dd.values, 0.0, color="tab:red", alpha=0.35)
    ax1.set_title("Aggregate NAV (equal-weight long_short@hold10)")
    ax2.set_title("Aggregate Drawdown")
    fig.savefig(asset_dir / "05_portfolio_nav_dd.png", dpi=170)
    plt.close(fig)

    # fig6 cost scenario
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for mode, color in [("long_only", "tab:blue"), ("long_short", "tab:purple")]:
        d = cost_summary[cost_summary["mode"] == mode].sort_values("fee_bps_roundtrip") if not cost_summary.empty else pd.DataFrame()
        if d.empty:
            continue
        ax.plot(d["fee_bps_roundtrip"], d["median_cagr"], marker="o", label=mode, color=color)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_xlabel("roundtrip fee (bps)")
    ax.set_ylabel("median CAGR")
    ax.set_title("Cost Scenario Stress Test")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(asset_dir / "06_cost_scenario_curves.png", dpi=170)
    plt.close(fig)

    # fig7 strategy compare
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    if not ab_summary.empty:
        ax.bar(ab_summary["strategy"], ab_summary["median_cagr"])
        ax.tick_params(axis="x", rotation=20)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_title("A/B/C Strategy Compare (hold=10)")
    ax.set_ylabel("median CAGR")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "07_ab_compare.png", dpi=170)
    plt.close(fig)

    # fig8 bull/bear beat rate
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    bb = annual_summary[annual_summary["strategy"] == "B_union_long"].copy() if not annual_summary.empty else pd.DataFrame()
    if not bb.empty:
        bb = bb.sort_values(["market_bucket", "market_regime"])
        x = np.arange(len(bb))
        ax.bar(x, bb["beat_rate"], color=["tab:green" if r == "bear" else "tab:orange" for r in bb["market_regime"]])
        ax.set_xticks(x)
        ax.set_xticklabels([f"{a}-{r}" for a, r in zip(bb["market_bucket"], bb["market_regime"])], rotation=20)
    ax.set_ylim(0, 1)
    ax.set_ylabel("beat_rate")
    ax.set_title("Beat Rate by Market Regime (B_union_long)")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "08_bull_bear_beat_rate.png", dpi=170)
    plt.close(fig)

    # fig9 recommended strategy strength by asset class
    fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
    s9 = strategy_asset_class_summary[strategy_asset_class_summary["strategy"] == "B_union_long"].copy() if not strategy_asset_class_summary.empty else pd.DataFrame()
    if not s9.empty:
        s9 = s9.sort_values("median_cagr", ascending=False)
        asset_class_plot_labels = {
            "A股指数": "AIndex",
            "港股指数": "HKIndex",
            "美股指数": "USIndex",
            "A股个股": "AStock",
            "港股个股": "HKStock",
            "美股个股": "USStock",
            "加密主流（指数代理）": "CryptoProxy",
        }
        labels = [asset_class_plot_labels.get(x, x) for x in s9["asset_class"]]
        ax.bar(labels, s9["median_cagr"], color="tab:blue")
        ax.tick_params(axis="x", rotation=25)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_ylabel("median CAGR")
    ax.set_title("Recommended Strategy Strength by Asset Class (B_union_long)")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "09_strategy_asset_class_strength.png", dpi=170)
    plt.close(fig)

    # fig10 decline-context strength (accumulation_ready, h=10)
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    s10 = event_decline_summary[event_decline_summary["signal"] == "accumulation_ready"].copy() if not event_decline_summary.empty else pd.DataFrame()
    if not s10.empty:
        order = ["shallow (-20%~-12%)", "medium (-35%~-20%)", "deep (<=-35%)", "weak (> -12%)", "unknown"]
        s10["decline_bin"] = pd.Categorical(s10["decline_bin"], categories=order, ordered=True)
        s10 = s10.sort_values("decline_bin")
        ax.bar(s10["decline_bin"].astype(str), s10["mean_ret"], color="tab:green")
        ax.tick_params(axis="x", rotation=20)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_ylabel("mean h=10 return")
    ax.set_title("When the Factor Is Strong: Prior Decline Context (accumulation_ready)")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "10_decline_context_strength.png", dpi=170)
    plt.close(fig)

    # Q&A text
    lo10 = cross_df[(cross_df["mode"] == "long_only") & (cross_df["hold_days"] == 10)]
    ls10 = cross_df[(cross_df["mode"] == "long_short") & (cross_df["hold_days"] == 10)]
    so10 = cross_df[(cross_df["mode"] == "short_only") & (cross_df["hold_days"] == 10)]

    q1_question = "这个因子更适合作为独立入场策略，还是作为建仓过滤器？"
    q2_question = "窄幅建仓、箱体突破、并集三种信号里，哪一个更强？"
    q3_question = "窄幅建仓与箱体突破应该如何分工？"
    q4_question = "最佳持有期是否稳健，默认值怎么选？"
    q5_question = "参数是否敏感，是否存在明显过拟合风险？"
    q6_question = "考虑成本后，这个因子还成立吗？"
    q7_question = "主策略应选 narrow-only、union-long，还是 union+short？"
    q8_question = "实盘里这个因子更适合试仓、加仓还是一次性重仓？"
    q9_question = "不同市场类别里，哪些最适配这个因子？"
    q10_question = "如何做失效监控和降级？"
    q11_question = "信号密度是否健康，会不会太稀疏或太拥挤？"
    q12_question = "滚动 OOS 稳定吗？默认参数是否站得住？"
    q13_question = "尾部风险有多大，仓位应该怎么定？"
    q14_question = "综合来看，这个因子的实盘最优定位是什么？"

    q1_sentence = f"在 hold=10 下，long_only 中位 CAGR {pct(lo10['cagr'].median())}，long_short {pct(ls10['cagr'].median())}，short_only {pct(so10['cagr'].median())}。"
    q1_action = "默认以 long_only 部署‘建仓完成’信号；在风险偏好允许时再叠加 short 防守腿。"

    e_best = event_summary[event_summary["signal"].isin(["narrow_accum_ready", "box_breakout_ready", "accumulation_ready"])] if not event_summary.empty else pd.DataFrame()
    if not e_best.empty:
        r0 = e_best.sort_values("mean_ret", ascending=False).iloc[0]
        q2_sentence = f"事件研究最强信号为 {r0['signal']}@h={int(r0['horizon'])}，均值 {pct(r0['mean_ret'])}。"
    else:
        q2_sentence = "事件研究样本不足。"
    q2_action = "优先围绕最强事件窗口配置持有期。"

    narrow_h10 = event_summary[(event_summary["signal"] == "narrow_accum_ready") & (event_summary["horizon"] == 10)] if not event_summary.empty else pd.DataFrame()
    box_h10 = event_summary[(event_summary["signal"] == "box_breakout_ready") & (event_summary["horizon"] == 10)] if not event_summary.empty else pd.DataFrame()
    if not narrow_h10.empty and not box_h10.empty:
        nv = float(narrow_h10["mean_ret"].iloc[0])
        bv = float(box_h10["mean_ret"].iloc[0])
        cmp = "高于" if bv > nv else "低于"
        q3_sentence = f"h=10 下，box_breakout 均值 {pct(bv)}，{cmp} narrow_accum 的 {pct(nv)}。"
    else:
        q3_sentence = "窄幅建仓与箱体突破的收益分层存在但样本有限。"
    q3_action = "把窄幅建仓作为‘提前布局’，箱体突破作为‘确认加仓’。"

    hs = summary_df[summary_df["mode"] == "long_only"].sort_values("median_cagr", ascending=False) if not summary_df.empty else pd.DataFrame()
    if not hs.empty:
        top_hold = int(hs.iloc[0]["hold_days"])
        q4_sentence = f"long_only 最优中位收益持有期约 {top_hold} 天。"
    else:
        q4_sentence = "持有期稳健区间需更多样本。"
    q4_action = "默认持有期先用 10~20 天，再按市场微调。"

    if not param_summary.empty:
        pbest = param_summary.iloc[0]
        q5_sentence = (
            f"参数最优组合为 decline={num(pbest['min_decline_pct'],2)}, narrow={num(pbest['narrow_range_max'],2)}, "
            f"box_lb={int(pbest['box_lookback'])}，中位 CAGR {pct(pbest['median_cagr'])}。"
        )
    else:
        q5_sentence = "参数网格样本不足。"
    q5_action = "先固定默认参数，再用 OOS 稳定性筛参数。"

    c0_lo = cost_summary[(cost_summary["mode"] == "long_only") & (cost_summary["fee_bps_roundtrip"] == 0)]["median_cagr"] if not cost_summary.empty else pd.Series(dtype=float)
    c20_lo = cost_summary[(cost_summary["mode"] == "long_only") & (cost_summary["fee_bps_roundtrip"] == 20)]["median_cagr"] if not cost_summary.empty else pd.Series(dtype=float)
    c0_ls = cost_summary[(cost_summary["mode"] == "long_short") & (cost_summary["fee_bps_roundtrip"] == 0)]["median_cagr"] if not cost_summary.empty else pd.Series(dtype=float)
    c20_ls = cost_summary[(cost_summary["mode"] == "long_short") & (cost_summary["fee_bps_roundtrip"] == 20)]["median_cagr"] if not cost_summary.empty else pd.Series(dtype=float)
    q6_sentence = (
        f"成本从 0→20bps 时，long_only 中位 CAGR {pct(c0_lo.iloc[0] if len(c0_lo) else np.nan)}→{pct(c20_lo.iloc[0] if len(c20_lo) else np.nan)}，"
        f"long_short {pct(c0_ls.iloc[0] if len(c0_ls) else np.nan)}→{pct(c20_ls.iloc[0] if len(c20_ls) else np.nan)}。"
    )
    q6_action = "实盘若费用接近策略边界，优先降换手并切回 long_only。"

    q7_top = ab_summary.head(1) if not ab_summary.empty else pd.DataFrame()
    if not q7_top.empty:
        best_strategy = str(q7_top['strategy'].iloc[0])
        q7_sentence = f"A/B/C 对照中最优策略为 {best_strategy}，中位 CAGR {pct(q7_top['median_cagr'].iloc[0])}。"
        if best_strategy == "A_narrow_only_long":
            q7_action = "先部署 A_narrow_only_long 作为基础版本；若要提高参与度，再评估升级到 B_union_long。"
        elif best_strategy == "B_union_long":
            q7_action = "先部署 B_union_long，再视市场状态决定是否加 short 防守。"
        else:
            q7_action = "先用 C_union_long_down_short 小资金试运行，并严格监控回撤与费用。"
    else:
        q7_sentence = "A/B/C 对照样本不足。"
        q7_action = "先从 B_union_long 小规模试运行，等样本充分后再决策。"

    if not oos_summary.empty:
        o0 = oos_summary.iloc[0]
        q12_sentence = (
            f"滚动 OOS 最优参数 decline={num(o0['min_decline_pct'],2)}, narrow={num(o0['narrow_range_max'],2)}, box_lb={int(o0['box_lookback'])}，"
            f"中位 CAGR {pct(o0['median_cagr'])}，IQR {pct(o0['iqr_cagr'])}。"
        )
    else:
        q12_sentence = "滚动 OOS 样本不足。"
    q12_action = "参数选择优先看 OOS 分位稳定性，不只看 in-sample 最优。"

    if not tail_df.empty:
        q13_sentence = f"tail risk: p5 单笔 {pct(tail_df['p5_trade_ret'].iloc[0])}，最差5%均值 {pct(tail_df['avg_worst5_ret'].iloc[0])}。"
        q13_action = f"仓位上限参考 {pct(tail_df['position_size_hint'].iloc[0])} 并配合波动目标。"
    else:
        q13_sentence = "tail risk 样本不足。"
        q13_action = "先用保守仓位上限（<=20%）并持续监控。"

    q14_sentence = "该信号本质是‘先跌后稳 + 波动收缩/箱体结构 + 突破确认’的建仓模块。"
    q14_action = "实盘建议：窄幅信号用于试仓，突破信号用于确认加仓。"

    def _as_val(bucket: str, regime: str, col: str) -> float:
        if annual_summary.empty:
            return np.nan
        d = annual_summary[
            (annual_summary["market_bucket"] == bucket)
            & (annual_summary["strategy"] == "B_union_long")
            & (annual_summary["market_regime"] == regime)
        ]
        if d.empty:
            return np.nan
        return float(d.iloc[0][col])

    def _as_asset_val(asset_class: str, regime: str, col: str) -> float:
        if annual_asset_class_summary.empty:
            return np.nan
        d = annual_asset_class_summary[
            (annual_asset_class_summary["asset_class"] == asset_class)
            & (annual_asset_class_summary["strategy"] == "B_union_long")
            & (annual_asset_class_summary["market_regime"] == regime)
        ]
        if d.empty:
            return np.nan
        return float(d.iloc[0][col])

    idx_bull_ex = _as_val("Index", "bull", "median_excess")
    idx_bear_ex = _as_val("Index", "bear", "median_excess")
    stk_bull_ex = _as_val("Stock", "bull", "median_excess")
    stk_bear_ex = _as_val("Stock", "bear", "median_excess")
    cry_bull_ex = _as_val("Crypto", "bull", "median_excess")
    cry_bear_ex = _as_val("Crypto", "bear", "median_excess")
    idx_bull_br = _as_val("Index", "bull", "beat_rate")
    idx_bear_br = _as_val("Index", "bear", "beat_rate")
    stk_bull_br = _as_val("Stock", "bull", "beat_rate")
    stk_bear_br = _as_val("Stock", "bear", "beat_rate")
    cry_bull_br = _as_val("Crypto", "bull", "beat_rate")
    cry_bear_br = _as_val("Crypto", "bear", "beat_rate")

    q15_question = "这个因子的收益是否只由牛市驱动？"
    q15_answer = (
        f"不是。以 B_union_long 为例，Crypto 指数代理牛/熊中位超额 {pct(cry_bull_ex)}/{pct(cry_bear_ex)}，"
        f"Index {pct(idx_bull_ex)}/{pct(idx_bear_ex)}，Stock {pct(stk_bull_ex)}/{pct(stk_bear_ex)}。"
    )
    q15_action = "把它定位为‘建仓时机过滤器’，重点看回撤控制与风险调整收益，而不是单纯吃牛市 beta。"

    q16_question = "它能持续跑赢同市场基准吗？"
    q16_answer = (
        f"跑赢是条件性的：Crypto 指数代理牛/熊跑赢率约 {pct(cry_bull_br)}/{pct(cry_bear_br)}，"
        f"Index {pct(idx_bull_br)}/{pct(idx_bear_br)}，Stock {pct(stk_bull_br)}/{pct(stk_bear_br)}。"
    )
    q16_action = "不要把目标设成‘每年跑赢’，而是‘在特定市场状态提升赔率/盈亏比’。"

    hk_stock_bull_ex = _as_asset_val("港股个股", "bull", "median_excess")
    hk_stock_bear_ex = _as_asset_val("港股个股", "bear", "median_excess")
    a_stock_bull_ex = _as_asset_val("A股个股", "bull", "median_excess")
    a_stock_bear_ex = _as_asset_val("A股个股", "bear", "median_excess")
    us_stock_bull_ex = _as_asset_val("美股个股", "bull", "median_excess")
    us_stock_bear_ex = _as_asset_val("美股个股", "bear", "median_excess")

    q17_question = "不同市场类别里，哪里更适配？（加密/A股/港股/美股/指数/个股）"
    q17_answer = (
        f"从 B_union_long 看：Crypto 指数代理牛/熊超额 {pct(cry_bull_ex)}/{pct(cry_bear_ex)}；"
        f"A股个股 {pct(a_stock_bull_ex)}/{pct(a_stock_bear_ex)}，港股个股 {pct(hk_stock_bull_ex)}/{pct(hk_stock_bear_ex)}，美股个股 {pct(us_stock_bull_ex)}/{pct(us_stock_bear_ex)}；"
        f"整体 Index 为 {pct(idx_bull_ex)}/{pct(idx_bear_ex)}，Stock 为 {pct(stk_bull_ex)}/{pct(stk_bear_ex)}。"
    )
    q17_action = "优先在波动更充分、先跌后稳更明显的个股与加密代理市场使用；指数更适合做仓位节奏管理。"

    best_asset_row = (
        strategy_asset_class_summary[strategy_asset_class_summary["strategy"] == "B_union_long"]
        .sort_values("median_cagr", ascending=False)
        .head(1)
    ) if not strategy_asset_class_summary.empty else pd.DataFrame()
    worst_asset_row = (
        strategy_asset_class_summary[strategy_asset_class_summary["strategy"] == "B_union_long"]
        .sort_values("median_cagr", ascending=True)
        .head(1)
    ) if not strategy_asset_class_summary.empty else pd.DataFrame()
    best_decline_row = (
        event_decline_summary[event_decline_summary["signal"] == "accumulation_ready"]
        .sort_values("mean_ret", ascending=False)
        .head(1)
    ) if not event_decline_summary.empty else pd.DataFrame()
    worst_decline_row = (
        event_decline_summary[event_decline_summary["signal"] == "accumulation_ready"]
        .sort_values("mean_ret", ascending=True)
        .head(1)
    ) if not event_decline_summary.empty else pd.DataFrame()

    executive_best_market = (
        f"{best_asset_row.iloc[0]['asset_class']}（B_union_long 中位 CAGR {pct(best_asset_row.iloc[0]['median_cagr'])}）"
        if not best_asset_row.empty
        else "样本不足"
    )
    executive_worst_market = (
        f"{worst_asset_row.iloc[0]['asset_class']}（B_union_long 中位 CAGR {pct(worst_asset_row.iloc[0]['median_cagr'])}）"
        if not worst_asset_row.empty
        else "样本不足"
    )
    executive_best_context = (
        f"先跌后稳幅度为 {best_decline_row.iloc[0]['decline_bin']}（accumulation_ready@h10 均值 {pct(best_decline_row.iloc[0]['mean_ret'])}）"
        if not best_decline_row.empty
        else "样本不足"
    )
    executive_worst_context = (
        f"先跌后稳幅度为 {worst_decline_row.iloc[0]['decline_bin']}（accumulation_ready@h10 均值 {pct(worst_decline_row.iloc[0]['mean_ret'])}）"
        if not worst_decline_row.empty
        else "样本不足"
    )

    # html
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    def df2html(df: pd.DataFrame, cols: List[str] | None = None, max_rows: int = 120) -> str:
        x = df.copy()
        if cols is not None:
            cols2 = [c for c in cols if c in x.columns]
            x = x[cols2]
        if len(x) > max_rows:
            x = x.head(max_rows)
        return x.to_html(index=False, border=0, classes="dataframe")

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Box Consolidation Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", "Microsoft YaHei", sans-serif; line-height: 1.55; margin: 0; color:#111; }}
    .wrap {{ max-width: 1240px; margin: 0 auto; padding: 20px; }}
    h1,h2,h3 {{ margin-top: 1.2em; }}
    .muted {{ color:#666; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin: 14px 0 20px; }}
    .card {{ border:1px solid #ddd; border-radius:10px; padding:12px 14px; background:#fafafa; }}
    .card h3 {{ margin:0 0 8px; font-size:16px; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef3ff; color:#2442a8; font-size:12px; margin-right:6px; }}
    .note {{ padding:10px 12px; border-left:4px solid #4c7cf0; background:#f6f8ff; margin:12px 0; }}
    img {{ max-width: 100%; border:1px solid #ddd; border-radius: 6px; }}
    table.dataframe {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
    table.dataframe th, table.dataframe td {{ border: 1px solid #ddd; padding: 4px 6px; text-align: right; }}
    table.dataframe th:first-child, table.dataframe td:first-child {{ text-align: left; }}
    code {{ background:#f6f6f6; padding:2px 4px; border-radius:4px; }}
  </style>
</head>
<body>
<div class='wrap'>
  <h1>Box Consolidation（窄幅震荡/箱体突破建仓）评估报告</h1>
  <p class='muted'>生成时间：{now}</p>

  <h2>1) 因子定义</h2>
  <ul>
    <li><b>窄幅震荡建仓 narrow_accum_ready</b>：先跌后稳 + 连续站上历史阴线低点 + 波动收缩 + 近期上涨浪确认。</li>
    <li><b>箱体突破建仓 box_breakout_ready</b>：先跌后箱体 + up/down wave 共现且不破关键结构 + 阳线突破箱体上沿。</li>
    <li><b>总信号 accumulation_ready</b>：上述两类建仓信号并集。</li>
  </ul>

  <div class='note'>
    <b>一句话定位：</b>这个因子更像“先跌后稳后的建仓过滤器/加仓确认器”，不是无条件的趋势追涨器，也不是要求年年跑赢基准的万能策略。
  </div>

  <h2>1.1) Executive Summary</h2>
  <div class='grid'>
    <div class='card'>
      <h3>最强市场类别</h3>
      <div>{executive_best_market}</div>
    </div>
    <div class='card'>
      <h3>最弱市场类别</h3>
      <div>{executive_worst_market}</div>
    </div>
    <div class='card'>
      <h3>最强触发场景</h3>
      <div>{executive_best_context}</div>
    </div>
    <div class='card'>
      <h3>最弱触发场景</h3>
      <div>{executive_worst_context}</div>
    </div>
  </div>

  <h2>2) 回测设定</h2>
  <p>Universe={len(loaded_names)}（指数/指数ETF + A/H/US 个股 + 加密主流代理），mode={MODES}，hold={HOLDS}，默认参数见 manifest。</p>
  <p class='muted'>说明：由于 Yahoo 上缺少稳定可用的单一“加密总市值指数”，此处额外用 BTC/ETH/SOL/BNB/XRP/ADA 作为“加密市场指数代理”样本组。</p>
  <h3>2.1 覆盖资产</h3>
  {df2html(coverage, ["market_name","ticker","asset_class","bars","start","end"], 80)}

  <h2>3) 基础表现</h2>
  <h3>3.1 跨市场汇总（中位数）</h3>
  {df2html(summary_df, ["mode","hold_days","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 30)}
  <h3>3.2 市场明细（节选）</h3>
  {df2html(cross_df, ["market_name","asset_class","market_bucket","mode","hold_days","trade_count","win_rate","cagr","sharpe","max_drawdown","buyhold_ret"], 220)}
  <img src='assets/01_heatmap_ls_cagr.png' alt='heatmap' />

  <h3>3.3 适用市场总览（hold=10）</h3>
  {df2html(suitability, ["market_bucket","mode","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 40)}

  <h3>3.4 指数 vs 个股 强度对比（long_only, hold=10）</h3>
  {df2html(region_strength, ["region","market_bucket","markets_n","median_cagr","median_sharpe","pass_rate"], 40)}

  <h3>3.5 按资产类别拆开看（推荐策略 B_union_long）</h3>
  {df2html(strategy_asset_class_summary, ["asset_class","strategy","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 80)}
  <p class='muted'>图中缩写：AIndex/AStock=A股指数/个股，HKIndex/HKStock=港股指数/个股，USIndex/USStock=美股指数/个股，CryptoProxy=加密主流指数代理。</p>
  <img src='assets/09_strategy_asset_class_strength.png' alt='asset-class-strength' />

  <h2>4) 拆解分析</h2>
  <h3>4.1 事件研究（窄幅/突破/并集）</h3>
  {df2html(event_summary, ["signal","horizon","samples","mean_ret","median_ret","win_rate"], 60)}
  <img src='assets/02_event_study_curves.png' alt='event-curves' />

  <h3>4.1.1 不同市场类别里的事件强度（h=10）</h3>
  {df2html(event_asset_class_summary, ["asset_class","signal","samples","mean_ret","median_ret","win_rate"], 120)}

  <h3>4.1.2 什么时候强、什么时候弱：按前序跌幅分层（h=10）</h3>
  {df2html(event_decline_summary, ["signal","decline_bin","samples","mean_ret","median_ret","win_rate"], 60)}
  <img src='assets/10_decline_context_strength.png' alt='decline-context-strength' />

  <h3>4.2 持有期稳健性</h3>
  <img src='assets/03_hold_robustness_curves.png' alt='hold-robustness' />

  <h3>4.3 参数敏感性（decline × narrow × box）</h3>
  {df2html(param_summary, ["min_decline_pct","narrow_range_max","box_lookback","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 60)}
  <img src='assets/04_param_sensitivity_heatmap.png' alt='param-sensitivity' />

  <h3>4.4 A/B/C 对照（窄幅-only vs 并集-long vs 并集+short）</h3>
  {df2html(ab_summary, ["strategy","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 20)}
  <img src='assets/07_ab_compare.png' alt='ab-compare' />

  <h3>4.5 OOS 滚动稳定性（2y训练+6m验证）</h3>
  {df2html(oos_summary, ["min_decline_pct","narrow_range_max","box_lookback","samples","median_cagr","iqr_cagr","pass_rate","median_max_drawdown"], 30)}

  <h3>4.6 年份×牛熊：策略是否跑赢同市场基准</h3>
  <p class='muted'>按自然年计算同市场 buy&hold 基准收益；bull=基准年收益>0，bear=<=0。</p>
  {df2html(annual_summary, ["market_bucket","strategy","market_regime","samples","median_benchmark","median_strategy","median_excess","beat_rate"], 60)}
  <h4>按资产类别细分（你关心的 A股/港股/美股/加密代理）</h4>
  {df2html(annual_asset_class_summary, ["asset_class","strategy","market_regime","samples","median_benchmark","median_strategy","median_excess","beat_rate"], 120)}
  <h4>整体汇总（不分牛熊）</h4>
  {df2html(annual_overall, ["market_bucket","strategy","samples","median_benchmark","median_strategy","median_excess","beat_rate"], 30)}
  <img src='assets/08_bull_bear_beat_rate.png' alt='bull-bear' />

  <h2>5) Usage Playbook（Q1~Q17）</h2>
  <ol>
    <li><b>Q1</b>（{q1_question}）：{q1_sentence}<br/><b>动作</b>：{q1_action}</li>
    <li><b>Q2</b>（{q2_question}）：{q2_sentence}<br/><b>动作</b>：{q2_action}</li>
    <li><b>Q3</b>（{q3_question}）：{q3_sentence}<br/><b>动作</b>：{q3_action}</li>
    <li><b>Q4</b>（{q4_question}）：{q4_sentence}<br/><b>动作</b>：{q4_action}</li>
    <li><b>Q5</b>（{q5_question}）：{q5_sentence}<br/><b>动作</b>：{q5_action}</li>
    <li><b>Q6</b>（{q6_question}）：{q6_sentence}<br/><b>动作</b>：{q6_action}</li>
    <li><b>Q7</b>（{q7_question}）：{q7_sentence}<br/><b>动作</b>：{q7_action}</li>
    <li><b>Q8</b>（{q8_question}）：风险模块建议：narrow 更适合试仓，box_breakout 更适合确认加仓，真正重仓应结合市场 beta 与流动性过滤。<br/><b>动作</b>：先小仓验证，再由突破信号推动加仓，不建议单靠窄幅信号一次性重仓。</li>
    <li><b>Q9</b>（{q9_question}）：从按资产类别拆分结果看，应优先关注个股与加密代理组；A股/港股/美股的“个股 vs 指数”差异会在年景切换时明显放大。<br/><b>动作</b>：页面上优先看 3.5 与 4.6 的资产类别拆分，而不要只看总中位数。</li>
    <li><b>Q10</b>（{q10_question}）：失效监控建议使用“近6个月胜率 vs 历史胜率”做一级门槛，阈值默认 8pct。<br/><b>动作</b>：一旦触发 degrade，就把该市场降级成过滤器或减仓信号，而不是强行继续交易。</li>
    <li><b>Q11</b>（{q11_question}）：这是低频建仓型信号，天然会出现“好机会不多但质量更高”的特征。<br/><b>动作</b>：接受空仓与低频，不要为了提高资金利用率去破坏信号定义。</li>
    <li><b>Q12</b>（{q12_question}）：{q12_sentence}<br/><b>动作</b>：{q12_action}</li>
    <li><b>Q13</b>（{q13_question}）：{q13_sentence}<br/><b>动作</b>：{q13_action}</li>
    <li><b>Q14</b>（{q14_question}）：{q14_sentence}<br/><b>动作</b>：{q14_action}</li>
    <li><b>Q15</b>（{q15_question}）：{q15_answer}<br/><b>动作</b>：{q15_action}</li>
    <li><b>Q16</b>（{q16_question}）：{q16_answer}<br/><b>动作</b>：{q16_action}</li>
    <li><b>Q17</b>（{q17_question}）：{q17_answer}<br/><b>动作</b>：{q17_action}</li>
  </ol>

  <h2>6) 风险与实盘约束</h2>
  <h3>6.1 成本情景压力测试</h3>
  {df2html(cost_summary, ["mode","fee_bps_roundtrip","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 40)}
  <img src='assets/06_cost_scenario_curves.png' alt='cost-scenario' />

  <h3>6.2 失效监控</h3>
  {df2html(failure_df, ["market_name","win_rate_hist","win_rate_recent6m","status","action"], 80)}

  <h3>6.3 尾部风险</h3>
  {df2html(tail_df, ["mode","hold_days","p5_trade_ret","avg_worst5_ret","max_loss_trade","avg_mae","avg_mfe","position_size_hint"], 20)}
  <img src='assets/05_portfolio_nav_dd.png' alt='portfolio-nav-dd' />

  <h2>7) 文献参考（概念映射）</h2>
  <ol>
    <li>John Bollinger, <i>Bollinger on Bollinger Bands</i>（波动收缩 / squeeze）</li>
    <li>Donchian Channel（区间上沿突破）</li>
    <li>Wyckoff Method（吸筹-整理-突破）</li>
    <li>Lo, Mamaysky, Wang (2000), <i>Foundations of Technical Analysis</i></li>
    <li>Minervini VCP（波动收敛后突破）</li>
  </ol>

  <h2>8) 数据与产物</h2>
  <p>artifact: <code>reports/artifacts/box_consolidation/</code></p>
  <p>site: <code>reports/site/factors/box_consolidation/report.html</code></p>
</div>
</body>
</html>
"""

    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    idx = root / "reports" / "site" / "index.html"
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text(
        """<!doctype html><html><head><meta charset='utf-8'><title>Momentum Reports</title></head>
<body><h1>Momentum Reports</h1><ul>
<li><a href='factors/updownwave/report.html'>UpDownWave Report</a></li>
<li><a href='factors/regime_triplet/report.html'>Regime Triplet Report</a></li>
<li><a href='factors/box_consolidation/report.html'>Box Consolidation Report</a></li>
</ul></body></html>""",
        encoding="utf-8",
    )

    manifest = {
        "generatedAt": now,
        "factor": "box_consolidation",
        "config": {
            "base": BASE_CFG.__dict__,
            "holds": HOLDS,
            "modes": MODES,
            "declineGrid": DECLINE_GRID,
            "narrowRangeGrid": NARROW_RANGE_GRID,
            "boxLookbackGrid": BOX_LOOKBACK_GRID,
            "costBps": COST_BPS_LIST,
            "oosTrainDays": OOS_TRAIN_DAYS,
            "oosTestDays": OOS_TEST_DAYS,
            "oosStepDays": OOS_STEP_DAYS,
            "oosDeclineGrid": OOS_DECLINE_GRID,
            "oosNarrowGrid": OOS_NARROW_GRID,
            "oosBoxLookbackGrid": OOS_BOX_LOOKBACK_GRID,
        },
        "loadedSymbols": {k: SYMBOLS[k] for k in loaded_names},
        "failedSymbols": failed_rows,
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[ok] report generated")
    print("site:", site_dir / "report.html")
    print("index:", idx)


if __name__ == "__main__":
    main()
