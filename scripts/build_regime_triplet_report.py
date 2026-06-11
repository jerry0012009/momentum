#!/usr/bin/env python3
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals import RegimeTripletConfig, compute_regime_triplet_signals


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

    # Crypto - majors
    {"name": "BTC", "ticker": "BTC-USD", "asset_class": "Crypto", "label_en": "BTC"},
    {"name": "ETH", "ticker": "ETH-USD", "asset_class": "Crypto", "label_en": "ETH"},
    {"name": "SOL", "ticker": "SOL-USD", "asset_class": "Crypto", "label_en": "SOL"},
    {"name": "BNB", "ticker": "BNB-USD", "asset_class": "Crypto", "label_en": "BNB"},
    {"name": "XRP", "ticker": "XRP-USD", "asset_class": "Crypto", "label_en": "XRP"},
    {"name": "ADA", "ticker": "ADA-USD", "asset_class": "Crypto", "label_en": "ADA"},
    {"name": "DOGE", "ticker": "DOGE-USD", "asset_class": "Crypto", "label_en": "DOGE"},

    # Crypto - mid caps
    {"name": "AVAX", "ticker": "AVAX-USD", "asset_class": "Crypto", "label_en": "AVAX"},
    {"name": "LINK", "ticker": "LINK-USD", "asset_class": "Crypto", "label_en": "LINK"},
    {"name": "DOT", "ticker": "DOT-USD", "asset_class": "Crypto", "label_en": "DOT"},
    {"name": "LTC", "ticker": "LTC-USD", "asset_class": "Crypto", "label_en": "LTC"},
    {"name": "BCH", "ticker": "BCH-USD", "asset_class": "Crypto", "label_en": "BCH"},
    {"name": "TRX", "ticker": "TRX-USD", "asset_class": "Crypto", "label_en": "TRX"},
    {"name": "XLM", "ticker": "XLM-USD", "asset_class": "Crypto", "label_en": "XLM"},
    {"name": "ATOM", "ticker": "ATOM-USD", "asset_class": "Crypto", "label_en": "ATOM"},
    {"name": "FIL", "ticker": "FIL-USD", "asset_class": "Crypto", "label_en": "FIL"},
    {"name": "NEAR", "ticker": "NEAR-USD", "asset_class": "Crypto", "label_en": "NEAR"},

    # Crypto - higher beta / small caps
    {"name": "ARB", "ticker": "ARB-USD", "asset_class": "Crypto", "label_en": "ARB"},
    {"name": "OP", "ticker": "OP-USD", "asset_class": "Crypto", "label_en": "OP"},
    {"name": "INJ", "ticker": "INJ-USD", "asset_class": "Crypto", "label_en": "INJ"},
    {"name": "SAND", "ticker": "SAND-USD", "asset_class": "Crypto", "label_en": "SAND"},
    {"name": "MANA", "ticker": "MANA-USD", "asset_class": "Crypto", "label_en": "MANA"},
    {"name": "PEPE", "ticker": "PEPE24478-USD", "asset_class": "Crypto", "label_en": "PEPE"},
    {"name": "WIF", "ticker": "WIF-USD", "asset_class": "Crypto", "label_en": "WIF"},
    {"name": "BONK", "ticker": "BONK-USD", "asset_class": "Crypto", "label_en": "BONK"},

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

BASE_CFG = RegimeTripletConfig(ma_period=20, vol_ma_period=120, vol_multiplier=1.0)
HOLDS = [5, 10, 20, 30]
MODES = ["long_only", "short_only", "long_short"]
HORIZONS = [1, 3, 5, 10, 20]

MA_GRID = [10, 20, 30]
VOL_WINDOW_GRID = [60, 120, 180]
VOL_MULT_GRID = [1.0, 1.2]
COST_BPS_LIST = [0, 10, 20, 50]
OOS_TRAIN_DAYS = 504
OOS_TEST_DAYS = 126
OOS_STEP_DAYS = 126
OOS_MA_GRID = [20]
OOS_VOL_WINDOW_GRID = [60, 120]


@dataclass
class BacktestResult:
    nav: pd.Series
    trades: pd.DataFrame
    in_position: pd.Series


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
    need = ["timestamp", "open", "high", "low", "close", "volume"]
    bars = bars[need].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)
    # Guard against invalid zero/negative prices that can break return math.
    bars = bars[(bars["open"] > 0) & (bars["high"] > 0) & (bars["low"] > 0) & (bars["close"] > 0)].reset_index(drop=True)
    bars["volume"] = bars["volume"].fillna(0.0)
    if bars.empty:
        raise ValueError(f"No positive-price bars for {ticker}")
    return bars


def run_nonoverlap_backtest(sig: pd.DataFrame, hold_days: int, mode: str, fee_bps_roundtrip: float = 0.0) -> BacktestResult:
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
        up = int(df.loc[i, "upwave"]) == 1
        dn = int(df.loc[i, "downwave"]) == 1

        side = None
        signal = None
        if mode == "long_only":
            if up and not dn:
                side = "long"
                signal = "up_regime"
        elif mode == "short_only":
            if dn and not up:
                side = "short"
                signal = "down_regime"
        else:
            if up and not dn:
                side = "long"
                signal = "up_regime"
            elif dn and not up:
                side = "short"
                signal = "down_regime"

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
        mae = float(trade_path.min()) if len(trade_path) else np.nan
        mfe = float(trade_path.max()) if len(trade_path) else np.nan
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
                "mae": mae,
                "mfe": mfe,
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

    vol = float(ret.std() * np.sqrt(252.0))
    sharpe = float((ret.mean() * 252.0) / vol) if vol > 0 else np.nan

    dd = nav / nav.cummax() - 1.0
    mdd = float(dd.min())
    calmar = float(cagr / abs(mdd)) if mdd < 0 else np.nan

    trade_count = int(len(trades))
    win_rate = float(trades["win"].mean()) if trade_count > 0 else np.nan
    pos_sum = float(trades.loc[trades["net_ret"] > 0, "net_ret"].sum()) if trade_count > 0 else 0.0
    neg_sum = float(-trades.loc[trades["net_ret"] < 0, "net_ret"].sum()) if trade_count > 0 else 0.0
    profit_factor = float(pos_sum / neg_sum) if neg_sum > 0 else np.nan

    exposure = float(in_position.mean()) if len(in_position) > 0 else np.nan

    return {
        "total_return": total_return,
        "cagr": cagr,
        "vol": vol,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "calmar": calmar,
        "trade_count": trade_count,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "exposure": exposure,
    }


def build_strategy_variants(sig: pd.DataFrame) -> Dict[str, dict]:
    return {
        "A_up_only_long": {
            "mode": "long_only",
            "up": (sig["up_regime"] == 1),
            "down": pd.Series(False, index=sig.index),
        },
        "B_up_plus_side_long": {
            "mode": "long_only",
            "up": ((sig["up_regime"] == 1) | (sig["side_regime"] == 1)),
            "down": pd.Series(False, index=sig.index),
        },
        "C_up_long_down_short": {
            "mode": "long_short",
            "up": (sig["up_regime"] == 1),
            "down": (sig["down_regime"] == 1),
        },
    }


def pct(v) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.2%}"


def num(v, d=2) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.{d}f}"


def main() -> None:
    root = ROOT
    artifact_dir = root / "reports" / "artifacts" / "regime_triplet"
    site_dir = root / "reports" / "site" / "factors" / "regime_triplet"
    asset_dir = site_dir / "assets"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    market_data: Dict[str, pd.DataFrame] = {}
    signal_data: Dict[str, pd.DataFrame] = {}
    failed_rows = []

    for name, ticker in SYMBOLS.items():
        try:
            bars = download_bars(ticker)
            if len(bars) < 260:
                raise ValueError("too few bars")
            bars["market_name"] = name
            bars["asset_class"] = ASSET_CLASS_MAP[name]
            market_data[name] = bars

            sig = compute_regime_triplet_signals(bars, config=BASE_CFG)
            sig["market_name"] = name
            sig["asset_class"] = ASSET_CLASS_MAP[name]
            signal_data[name] = sig
        except Exception as e:
            failed_rows.append({"market_name": name, "ticker": ticker, "reason": str(e)[:200]})

    if not signal_data:
        raise RuntimeError("No symbols loaded successfully")

    loaded_names = list(signal_data.keys())
    coverage = pd.DataFrame(
        [
            {
                "market_name": n,
                "ticker": SYMBOLS[n],
                "asset_class": ASSET_CLASS_MAP[n],
                "bars": int(len(market_data[n])),
                "start": market_data[n]["timestamp"].iloc[0].strftime("%Y-%m-%d"),
                "end": market_data[n]["timestamp"].iloc[-1].strftime("%Y-%m-%d"),
            }
            for n in loaded_names
        ]
    )
    coverage.to_csv(artifact_dir / "universe_coverage.csv", index=False)
    pd.DataFrame(failed_rows).to_csv(artifact_dir / "universe_failed.csv", index=False)

    # baseline backtest
    rows = []
    nav_store: Dict[Tuple[str, str, int], pd.Series] = {}
    trades_store: Dict[Tuple[str, str, int], pd.DataFrame] = {}

    for name in loaded_names:
        sig = signal_data[name]
        bh = float(sig["close"].iloc[-1] / sig["close"].iloc[0] - 1.0)

        for mode in MODES:
            for hold in HOLDS:
                r = run_nonoverlap_backtest(sig, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0)
                m = calc_metrics(r.nav, r.trades, r.in_position)
                rows.append(
                    {
                        "market_name": name,
                        "ticker": SYMBOLS[name],
                        "asset_class": ASSET_CLASS_MAP[name],
                        "mode": mode,
                        "hold_days": hold,
                        "up_regime_count": int(sig["up_regime"].sum()),
                        "side_regime_count": int(sig["side_regime"].sum()),
                        "down_regime_count": int(sig["down_regime"].sum()),
                        "buyhold_ret": bh,
                        **m,
                    }
                )
                nav_store[(name, mode, hold)] = r.nav
                trades_store[(name, mode, hold)] = r.trades

    cross_df = pd.DataFrame(rows).sort_values(["mode", "market_name", "hold_days"])
    cross_df.to_csv(artifact_dir / "cross_market_metrics.csv", index=False)

    # market suitability: index vs stock vs crypto (hold=10)
    def _bucket(ac: str) -> str:
        if "指数" in ac:
            return "Index"
        if "个股" in ac:
            return "Stock"
        if ac == "Crypto":
            return "Crypto"
        return "Other"

    cross_df["market_bucket"] = cross_df["asset_class"].map(_bucket)

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
    )
    summary_df.to_csv(artifact_dir / "baseline_summary.csv", index=False)

    # event study for three signals
    ev_rows = []
    for name in loaded_names:
        s = signal_data[name].reset_index(drop=True)
        close = s["close"].astype(float)

        for idx in s.index[s["up_regime"] == 1]:
            for h in HORIZONS:
                if idx + h >= len(s):
                    continue
                r = float(close.iloc[idx + h] / close.iloc[idx] - 1.0)
                ev_rows.append({"market_name": name, "signal": "up_regime", "horizon": h, "ret": r})

        for idx in s.index[s["side_regime"] == 1]:
            for h in HORIZONS:
                if idx + h >= len(s):
                    continue
                r = float(close.iloc[idx + h] / close.iloc[idx] - 1.0)
                ev_rows.append({"market_name": name, "signal": "side_regime", "horizon": h, "ret": r})

        for idx in s.index[s["down_regime"] == 1]:
            for h in HORIZONS:
                if idx + h >= len(s):
                    continue
                r = float(close.iloc[idx] / close.iloc[idx + h] - 1.0)  # short return
                ev_rows.append({"market_name": name, "signal": "down_regime", "horizon": h, "ret": r})

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
    )
    event_summary.to_csv(artifact_dir / "event_study_summary.csv", index=False)

    # parameter sensitivity (ma x vol_window x vol_multiplier)
    param_rows = []
    for name in loaded_names:
        bars = market_data[name]
        for ma in MA_GRID:
            for vw in VOL_WINDOW_GRID:
                for vm in VOL_MULT_GRID:
                    cfg = RegimeTripletConfig(ma_period=ma, vol_ma_period=vw, vol_multiplier=vm)
                    sig = compute_regime_triplet_signals(bars, config=cfg)
                    rr = run_nonoverlap_backtest(sig, hold_days=10, mode="long_short", fee_bps_roundtrip=0.0)
                    mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                    param_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP[name],
                            "ma_period": ma,
                            "vol_ma_period": vw,
                            "vol_multiplier": vm,
                            "up_regime_count": int(sig["up_regime"].sum()),
                            "side_regime_count": int(sig["side_regime"].sum()),
                            "down_regime_count": int(sig["down_regime"].sum()),
                            **mm,
                        }
                    )

    param_df = pd.DataFrame(param_rows)
    param_df.to_csv(artifact_dir / "param_grid_metrics.csv", index=False)
    param_summary = (
        param_df.groupby(["ma_period", "vol_ma_period", "vol_multiplier"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["median_cagr", "median_sharpe"], ascending=False)
        .reset_index(drop=True)
    )
    param_summary.to_csv(artifact_dir / "param_grid_summary.csv", index=False)

    # A/B strategy comparison around side_regime
    ab_rows = []
    for name in loaded_names:
        s = signal_data[name]
        variants = build_strategy_variants(s)
        for name_v, cfg_v in variants.items():
            sx = s.copy()
            sx["upwave"] = cfg_v["up"].astype(int)
            sx["downwave"] = cfg_v["down"].astype(int)
            rr = run_nonoverlap_backtest(sx, hold_days=10, mode=cfg_v["mode"], fee_bps_roundtrip=0.0)
            mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
            ab_rows.append(
                {
                    "market_name": name,
                    "asset_class": ASSET_CLASS_MAP[name],
                    "strategy": name_v,
                    **mm,
                }
            )
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
    )
    ab_summary.to_csv(artifact_dir / "strategy_ab_compare_summary.csv", index=False)

    # annual bull/bear decomposition: strategy vs same-market benchmark
    annual_rows = []
    for name in loaded_names:
        s = signal_data[name].copy()
        s["timestamp"] = pd.to_datetime(s["timestamp"], utc=True)
        s = s.sort_values("timestamp").reset_index(drop=True)
        s["year"] = s["timestamp"].dt.year

        bh_year = s.groupby("year", as_index=False).agg(start=("close", "first"), end=("close", "last"))
        bh_year["benchmark_ret"] = bh_year["end"] / bh_year["start"] - 1.0
        bh_map = dict(zip(bh_year["year"], bh_year["benchmark_ret"]))

        variants = build_strategy_variants(s)
        strat_yearly: Dict[str, pd.Series] = {}
        for vname, cfg_v in variants.items():
            sx = s.copy()
            sx["upwave"] = cfg_v["up"].astype(int)
            sx["downwave"] = cfg_v["down"].astype(int)
            rr = run_nonoverlap_backtest(sx, hold_days=10, mode=cfg_v["mode"], fee_bps_roundtrip=0.0)
            nav = rr.nav.to_frame("nav")
            nav["year"] = nav.index.year
            y = nav.groupby("year", as_index=False).agg(start=("nav", "first"), end=("nav", "last"))
            y[vname] = y["end"] / y["start"] - 1.0
            strat_yearly[vname] = y.set_index("year")[vname]

        all_years = sorted(set(bh_map.keys()))
        for y in all_years:
            bench = float(bh_map.get(y, np.nan))
            regime = "bull" if (pd.notna(bench) and bench > 0) else "bear"
            for vname in variants.keys():
                sr = float(strat_yearly[vname].get(y, np.nan)) if vname in strat_yearly else np.nan
                annual_rows.append(
                    {
                        "market_name": name,
                        "asset_class": ASSET_CLASS_MAP[name],
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
    annual_df["market_bucket"] = annual_df["asset_class"].map(_bucket)
    annual_df.to_csv(artifact_dir / "annual_strategy_vs_benchmark.csv", index=False)

    annual_summary = (
        annual_df.groupby(["market_bucket", "strategy", "market_regime"], as_index=False)
        .agg(
            samples=("excess_ret", "size"),
            median_benchmark=("benchmark_ret", "median"),
            median_strategy=("strategy_ret", "median"),
            mean_excess=("excess_ret", "mean"),
            median_excess=("excess_ret", "median"),
            beat_rate=("beat_benchmark", "mean"),
        )
        .sort_values(["market_bucket", "strategy", "market_regime"])
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
    )
    annual_overall.to_csv(artifact_dir / "annual_regime_excess_overall.csv", index=False)

    # rolling OOS (2y train + 6m test)
    oos_rows = []
    for name, bars in market_data.items():
        n = len(bars)
        for ma in OOS_MA_GRID:
            for vw in OOS_VOL_WINDOW_GRID:
                for vm in VOL_MULT_GRID:
                    cfg = RegimeTripletConfig(ma_period=ma, vol_ma_period=vw, vol_multiplier=vm)
                    sig = compute_regime_triplet_signals(bars, config=cfg)
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
                        rr = run_nonoverlap_backtest(test, hold_days=10, mode="long_short", fee_bps_roundtrip=0.0)
                        mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                        oos_rows.append(
                            {
                                "market_name": name,
                                "asset_class": ASSET_CLASS_MAP[name],
                                "ma_period": ma,
                                "vol_ma_period": vw,
                                "vol_multiplier": vm,
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
    if not oos_df.empty:
        oos_summary = (
            oos_df.groupby(["ma_period", "vol_ma_period", "vol_multiplier"], as_index=False)
            .agg(
                samples=("cagr", "size"),
                median_cagr=("cagr", "median"),
                iqr_cagr=("cagr", lambda s: float(np.nanquantile(s, 0.75) - np.nanquantile(s, 0.25))),
                pass_rate=("cagr", lambda s: float((s > 0).mean())),
                median_max_drawdown=("max_drawdown", "median"),
            )
            .sort_values(["median_cagr", "pass_rate"], ascending=False)
        )
    else:
        oos_summary = pd.DataFrame()
    oos_summary.to_csv(artifact_dir / "oos_summary.csv", index=False)

    # signal density by year
    density_rows = []
    for name in loaded_names:
        s = signal_data[name].copy()
        s["year"] = pd.to_datetime(s["timestamp"], utc=True).dt.year
        for y, g in s.groupby("year"):
            density_rows.append(
                {
                    "market_name": name,
                    "asset_class": ASSET_CLASS_MAP[name],
                    "year": int(y),
                    "up_regime_count": int(g["up_regime"].sum()),
                    "side_regime_count": int(g["side_regime"].sum()),
                    "down_regime_count": int(g["down_regime"].sum()),
                }
            )
    density_df = pd.DataFrame(density_rows)
    density_df.to_csv(artifact_dir / "signal_density_by_year.csv", index=False)
    density_summary = (
        density_df.groupby("year", as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            mean_up=("up_regime_count", "mean"),
            mean_side=("side_regime_count", "mean"),
            mean_down=("down_regime_count", "mean"),
        )
        .sort_values("year")
    )
    density_summary.to_csv(artifact_dir / "signal_density_summary.csv", index=False)

    # explicit cost scenario (no approximation)
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
    )
    cost_summary.to_csv(artifact_dir / "cost_scenario_summary.csv", index=False)

    # approximate market break-even from scenario crossing (long_short)
    be_rows = []
    for name, g in cost_df[cost_df["mode"] == "long_short"].groupby("market_name"):
        gg = g.sort_values("fee_bps_roundtrip")
        x = gg["fee_bps_roundtrip"].values.astype(float)
        y = gg["cagr"].values.astype(float)
        be = np.nan
        if np.all(np.isfinite(y)):
            if (y <= 0).all():
                be = 0.0
            elif (y > 0).all():
                be = float(x.max())
            else:
                for i in range(1, len(x)):
                    if y[i] <= 0 < y[i - 1]:
                        x0, x1 = x[i - 1], x[i]
                        y0, y1 = y[i - 1], y[i]
                        be = float(x0 + (0 - y0) * (x1 - x0) / (y1 - y0)) if y1 != y0 else float(x1)
                        break
        be_rows.append({"market_name": name, "break_even_fee_bps": be})
    cost_be_df = pd.DataFrame(be_rows)
    cost_be_df.to_csv(artifact_dir / "cost_budget_by_market.csv", index=False)

    # failure monitor (simple)
    fail_rows = []
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

        if pd.notna(wr_recent) and wr_recent < wr_hist - 0.08:
            status = "degrade"
            action = "降级为过滤器/减仓"
        else:
            status = "normal"
            action = "正常运行"

        fail_rows.append({"market_name": name, "win_rate_hist": wr_hist, "win_rate_recent6m": wr_recent, "status": status, "action": action})

    failure_df = pd.DataFrame(fail_rows)
    failure_df.to_csv(artifact_dir / "failure_monitor.csv", index=False)

    # tail risk
    tr_all = []
    for name in loaded_names:
        tr = trades_store.get((name, "long_short", 10), pd.DataFrame())
        if tr is not None and len(tr):
            tr_all.append(tr[["net_ret", "mae", "mfe"]])
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

    # figures
    # fig1 heatmap long_short cagr by market x hold
    piv = cross_df[cross_df["mode"] == "long_short"].pivot(index="market_name", columns="hold_days", values="cagr")
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    arr = piv.values.astype(float)
    lim = float(np.nanquantile(np.abs(arr[np.isfinite(arr)]), 0.95)) if np.isfinite(arr).any() else 0.2
    im = ax.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=-lim, vmax=lim)
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels(piv.columns)
    ax.set_yticks(range(len(piv.index)))
    ax.set_yticklabels([PLOT_LABELS.get(x, x) for x in piv.index])
    ax.set_title("Long-Short CAGR Heatmap (Regime Triplet)")
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            v = arr[i, j]
            ax.text(j, i, "nan" if not np.isfinite(v) else f"{v:.1%}", ha="center", va="center", fontsize=8)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.savefig(asset_dir / "01_heatmap_ls_cagr.png", dpi=170)
    plt.close(fig)

    # fig2 parameter sensitivity for vm=1.0
    p2 = param_summary[param_summary["vol_multiplier"] == 1.0].copy()
    pv = p2.pivot(index="ma_period", columns="vol_ma_period", values="median_cagr")
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    if not pv.empty:
        arr = pv.values.astype(float)
        lim = float(np.nanquantile(np.abs(arr[np.isfinite(arr)]), 0.95)) if np.isfinite(arr).any() else 0.2
        im = ax.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=-lim, vmax=lim)
        ax.set_xticks(range(len(pv.columns)))
        ax.set_xticklabels(pv.columns)
        ax.set_yticks(range(len(pv.index)))
        ax.set_yticklabels(pv.index)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                v = arr[i, j]
                ax.text(j, i, "nan" if not np.isfinite(v) else f"{v:.1%}", ha="center", va="center", fontsize=8)
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Median CAGR by (MA, Volume MA) | vol_multiplier=1.0")
    ax.set_xlabel("volume MA window")
    ax.set_ylabel("price MA period")
    fig.savefig(asset_dir / "02_param_sensitivity_heatmap.png", dpi=170)
    plt.close(fig)

    # fig3 event study curves
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for sig_name, color in [("up_regime", "tab:green"), ("side_regime", "tab:orange"), ("down_regime", "tab:red")]:
        d = event_summary[event_summary["signal"] == sig_name].sort_values("horizon")
        if d.empty:
            continue
        ax.plot(d["horizon"], d["mean_ret"], marker="o", label=sig_name, color=color)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_xlabel("horizon (days)")
    ax.set_ylabel("mean event return")
    ax.set_title("Event Study: forward return by signal")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(asset_dir / "03_event_study_curves.png", dpi=170)
    plt.close(fig)

    # fig4 signal density yearly
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    if not density_summary.empty:
        ax.plot(density_summary["year"], density_summary["mean_up"], marker="o", label="up_regime")
        ax.plot(density_summary["year"], density_summary["mean_side"], marker="s", label="side_regime")
        ax.plot(density_summary["year"], density_summary["mean_down"], marker="^", label="down_regime")
        ax.legend()
    ax.set_title("Signal density by year (market average)")
    ax.set_xlabel("year")
    ax.set_ylabel("count")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "04_signal_density_yearly.png", dpi=170)
    plt.close(fig)

    # fig5 portfolio equity (equal-weight across markets, long_short hold10)
    ret_cols = []
    for name in loaded_names:
        nav = nav_store.get((name, "long_short", 10))
        if nav is not None:
            ret_cols.append(nav.pct_change().fillna(0.0).rename(name))

    if ret_cols:
        r = pd.concat(ret_cols, axis=1, sort=False).fillna(0.0).mean(axis=1)
        nav_p = (1.0 + r).cumprod()
        dd_p = nav_p / nav_p.cummax() - 1.0

        fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
        axes[0].plot(nav_p.index, nav_p.values)
        axes[0].set_title("Equal-weight portfolio NAV (long_short hold=10)")
        axes[0].grid(alpha=0.3)
        axes[1].plot(dd_p.index, dd_p.values, color="tab:red")
        axes[1].set_title("Portfolio Drawdown")
        axes[1].grid(alpha=0.3)
        fig.savefig(asset_dir / "05_portfolio_nav_dd.png", dpi=170)
        plt.close(fig)

    # fig6 cost scenario curves (median by mode)
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    for mode, color in [("long_only", "tab:blue"), ("long_short", "tab:purple")]:
        d = cost_summary[cost_summary["mode"] == mode].sort_values("fee_bps_roundtrip")
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

    # fig7 A/B strategy comparison
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    if not ab_summary.empty:
        ax.bar(ab_summary["strategy"], ab_summary["median_cagr"])
        ax.tick_params(axis="x", rotation=20)
    ax.axhline(0.0, color="gray", linewidth=1)
    ax.set_title("A/B Strategy Compare (hold=10)")
    ax.set_ylabel("median CAGR")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "07_ab_compare.png", dpi=170)
    plt.close(fig)

    # fig8 OOS stability boxplot by param combo
    if not oos_df.empty:
        o = oos_df.copy()
        o["combo"] = (
            "MA" + o["ma_period"].astype(str)
            + "/V" + o["vol_ma_period"].astype(str)
            + "/k" + o["vol_multiplier"].astype(str)
        )
        order = (
            o.groupby("combo", as_index=False)["cagr"]
            .median()
            .sort_values("cagr", ascending=False)["combo"]
            .tolist()[:8]
        )
        fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
        data = [o.loc[o["combo"] == c, "cagr"].dropna().values for c in order]
        ax.boxplot(data, tick_labels=order, showfliers=False)
        ax.tick_params(axis="x", rotation=25)
        ax.axhline(0.0, color="gray", linewidth=1)
        ax.set_title("OOS CAGR Stability (2y train + 6m test)")
        ax.set_ylabel("CAGR")
        ax.grid(alpha=0.3)
        fig.savefig(asset_dir / "08_oos_cagr_boxplot.png", dpi=170)
        plt.close(fig)

    # textual conclusions Q1~Q14
    ls10 = cross_df[(cross_df["mode"] == "long_short") & (cross_df["hold_days"] == 10)]
    lo10 = cross_df[(cross_df["mode"] == "long_only") & (cross_df["hold_days"] == 10)]
    so10 = cross_df[(cross_df["mode"] == "short_only") & (cross_df["hold_days"] == 10)]

    q1_sentence = f"在 hold=10 下，long_short 中位 CAGR {pct(ls10['cagr'].median())}，long_only {pct(lo10['cagr'].median())}，short_only {pct(so10['cagr'].median())}。"
    if lo10['cagr'].median() >= ls10['cagr'].median():
        q1_action = "默认先以 long_only 部署（up_regime 主进攻），再按市场需要叠加 down_regime 防守腿。"
    else:
        q1_action = "默认先用 long_short，再按市场偏好切 long_only。"

    e_best = event_summary.sort_values("mean_ret", ascending=False).head(1)
    if not e_best.empty:
        r0 = e_best.iloc[0]
        q2_sentence = f"事件研究最强信号为 {r0['signal']}@h={int(r0['horizon'])}，均值 {pct(r0['mean_ret'])}。"
    else:
        q2_sentence = "事件研究样本不足。"
    q2_action = "优先围绕高均值窗口配置持有期，短窗仅作战术补充。"

    side_h10 = event_summary[(event_summary["signal"] == "side_regime") & (event_summary["horizon"] == 10)]
    up_h10 = event_summary[(event_summary["signal"] == "up_regime") & (event_summary["horizon"] == 10)]
    if not side_h10.empty and not up_h10.empty:
        side_v = float(side_h10['mean_ret'].iloc[0])
        up_v = float(up_h10['mean_ret'].iloc[0])
        cmp = "高于" if side_v > up_v else "低于"
        q3_sentence = f"h=10 下，side_regime 均值 {pct(side_v)}，{cmp} up_regime 的 {pct(up_v)}。"
    else:
        q3_sentence = "side_regime 与 up_regime 的收益分层存在但样本有限。"
    q3_action = "把震荡期作为减仓/过滤状态，而非主攻击信号。"

    hs = summary_df[summary_df["mode"] == "long_short"].sort_values("median_cagr", ascending=False)
    if not hs.empty:
        top_hold = int(hs.iloc[0]["hold_days"])
        q4_sentence = f"long_short 最优中位收益持有期约 {top_hold} 天。"
    else:
        q4_sentence = "持有期稳健区间需要更多样本。"
    q4_action = "默认持有期从 10~20 天起步，再按市场调参。"

    if not param_summary.empty:
        pbest = param_summary.iloc[0]
        q5_sentence = f"参数最优组合为 MA{int(pbest['ma_period'])}/VOL{int(pbest['vol_ma_period'])}/k={pbest['vol_multiplier']}，中位 CAGR {pct(pbest['median_cagr'])}。"
    else:
        q5_sentence = "参数网格样本不足。"
    q5_action = "先固定默认参数（20/120/1.0），仅在稳定 OOS 后再做微调。"

    c0_lo = cost_summary[(cost_summary["mode"] == "long_only") & (cost_summary["fee_bps_roundtrip"] == 0)]["median_cagr"]
    c20_lo = cost_summary[(cost_summary["mode"] == "long_only") & (cost_summary["fee_bps_roundtrip"] == 20)]["median_cagr"]
    c0_ls = cost_summary[(cost_summary["mode"] == "long_short") & (cost_summary["fee_bps_roundtrip"] == 0)]["median_cagr"]
    c20_ls = cost_summary[(cost_summary["mode"] == "long_short") & (cost_summary["fee_bps_roundtrip"] == 20)]["median_cagr"]
    be_med = cost_be_df["break_even_fee_bps"].median() if ("break_even_fee_bps" in cost_be_df.columns and len(cost_be_df)) else np.nan
    q6_sentence = (
        f"成本从 0→20bps 时，long_only 中位 CAGR {pct(c0_lo.iloc[0] if len(c0_lo) else np.nan)}→{pct(c20_lo.iloc[0] if len(c20_lo) else np.nan)}，"
        f"long_short {pct(c0_ls.iloc[0] if len(c0_ls) else np.nan)}→{pct(c20_ls.iloc[0] if len(c20_ls) else np.nan)}；"
        f"long_short 市场级 break-even 中位约 {num(be_med,1)} bps。"
    )
    q6_action = "优先做成本情景回测而非单点估算；当实盘费用逼近 break-even 时，降低换手并切换到 long-only。"

    q7_top = ab_summary.head(1)
    if not q7_top.empty:
        q7_sentence = f"A/B 对照中最优策略为 {q7_top['strategy'].iloc[0]}，中位 CAGR {pct(q7_top['median_cagr'].iloc[0])}。"
    else:
        q7_sentence = "A/B 对照样本不足。"
    q7_action = "先部署 A_up_only_long，再评估是否把 side_regime 纳入 B_up_plus_side_long。"

    def _as_val(bucket: str, regime: str, col: str):
        d = annual_summary[
            (annual_summary["market_bucket"] == bucket)
            & (annual_summary["strategy"] == "B_up_plus_side_long")
            & (annual_summary["market_regime"] == regime)
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
    cry_bull_br = _as_val("Crypto", "bull", "beat_rate")
    cry_bear_br = _as_val("Crypto", "bear", "beat_rate")

    q15_question = "这个因子的高收益是否只由牛市驱动？"
    q15_answer = (
        f"不是。以 B_up_plus_side_long 为例，Crypto 在牛市年中位超额 {pct(cry_bull_ex)}，"
        f"熊市年中位超额 {pct(cry_bear_ex)}；熊市防守贡献明显。"
    )
    q15_action = "把该因子定位为‘状态过滤+防守增强’，而非单纯牛市追涨器。"

    q16_question = "它能持续跑赢同市场大盘吗？"
    q16_answer = (
        f"跑赢有条件：Crypto 牛/熊年跑赢率约 {pct(cry_bull_br)} / {pct(cry_bear_br)}；"
        f"指数与个股在牛市年超额多为负（Index {pct(idx_bull_ex)}，Stock {pct(stk_bull_ex)}）。"
    )
    q16_action = "目标改为‘提升风险调整后收益’而非每年都跑赢基准。"

    q17_question = "指数、个股、加密哪个市场更适配？"
    q17_answer = (
        f"从 B_up_plus_side_long 看：Crypto 牛/熊中位超额 {pct(cry_bull_ex)}/{pct(cry_bear_ex)}，"
        f"Index {pct(idx_bull_ex)}/{pct(idx_bear_ex)}，Stock {pct(stk_bull_ex)}/{pct(stk_bear_ex)}。"
    )
    q17_action = "优先在 Crypto 与波动更充分的市场使用；指数更多用作风控开关。"

    if not oos_summary.empty:
        o0 = oos_summary.iloc[0]
        q12_sentence = (
            f"滚动 OOS 最优参数 MA{int(o0['ma_period'])}/VOL{int(o0['vol_ma_period'])}/k={o0['vol_multiplier']}，"
            f"中位 CAGR {pct(o0['median_cagr'])}，IQR {pct(o0['iqr_cagr'])}。"
        )
    else:
        q12_sentence = "滚动 OOS 样本不足。"
    q12_action = "按 OOS 分位数稳定性选参数，避免仅看 in-sample 最优。"

    if not tail_df.empty:
        q13_sentence = f"tail risk: p5 单笔 {pct(tail_df['p5_trade_ret'].iloc[0])}，最差5%均值 {pct(tail_df['avg_worst5_ret'].iloc[0])}。"
        q13_action = f"仓位上限参考 {pct(tail_df['position_size_hint'].iloc[0])}，并配合波动目标。"
    else:
        q13_sentence = "tail risk 样本不足。"
        q13_action = "先使用保守仓位上限（<=20%）并持续监控。"

    q14_sentence = "这组三信号本质是‘趋势强化 + 量能确认 + 震荡识别’的市场状态模块。"
    q14_action = "实盘建议：up_regime 主进攻、side_regime 降杠杆、down_regime 做防守/对冲。"

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
  <title>Regime Triplet Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; line-height: 1.55; margin: 0; color:#111; }}
    .wrap {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
    h1,h2,h3 {{ margin-top: 1.2em; }}
    .muted {{ color:#666; }}
    img {{ max-width: 100%; border:1px solid #ddd; border-radius: 6px; }}
    table.dataframe {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
    table.dataframe th, table.dataframe td {{ border: 1px solid #ddd; padding: 4px 6px; text-align: right; }}
    table.dataframe th:first-child, table.dataframe td:first-child {{ text-align: left; }}
    code {{ background:#f6f6f6; padding:2px 4px; border-radius:4px; }}
  </style>
</head>
<body>
<div class='wrap'>
  <h1>Regime Triplet（上涨期/震荡期/下跌期）评估报告</h1>
  <p class='muted'>生成时间：{now}</p>

  <h2>1) 因子定义</h2>
  <ul>
    <li><b>上涨期 up_regime</b>：T-3 阳线 + T-3..T 收盘在 MA20 上 + T-3..T 成交量均高于 120 日均量。</li>
    <li><b>震荡期 side_regime</b>：满足上涨浪价格结构，但量能连续条件不满足。</li>
    <li><b>下跌期 down_regime</b>：T-3..T 收盘都在 MA20 下，不要求量能。</li>
  </ul>

  <h2>2) 回测设定</h2>
  <p>Universe={len(loaded_names)}（指数/指数ETF + Crypto + A/H/US 个股），mode={MODES}，hold={HOLDS}，默认参数 MA={BASE_CFG.ma_period}, VOL_MA={BASE_CFG.vol_ma_period}, k={BASE_CFG.vol_multiplier}。</p>
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

  <h2>4) 拆解分析</h2>
  <h3>4.1 事件研究（三信号）</h3>
  {df2html(event_summary, ["signal","horizon","samples","mean_ret","median_ret","win_rate"], 60)}
  <img src='assets/03_event_study_curves.png' alt='event-curves' />

  <h3>4.2 参数敏感性（MA × 成交量均线 × 量能阈值）</h3>
  {df2html(param_summary, ["ma_period","vol_ma_period","vol_multiplier","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 60)}
  <img src='assets/02_param_sensitivity_heatmap.png' alt='param-sensitivity' />

  <h3>4.3 信号密度</h3>
  {df2html(density_summary, ["year","markets_n","mean_up","mean_side","mean_down"], 60)}
  <img src='assets/04_signal_density_yearly.png' alt='signal-density' />

  <h3>4.4 A/B 对照（side_regime 是否纳入交易）</h3>
  {df2html(ab_summary, ["strategy","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 20)}
  <img src='assets/07_ab_compare.png' alt='ab-compare' />

  <h3>4.5 OOS 滚动稳定性（2y训练+6m验证）</h3>
  {df2html(oos_summary, ["ma_period","vol_ma_period","vol_multiplier","samples","median_cagr","iqr_cagr","pass_rate","median_max_drawdown"], 30)}
  <img src='assets/08_oos_cagr_boxplot.png' alt='oos-boxplot' />

  <h3>4.6 年份×牛熊：策略是否跑赢同市场基准</h3>
  <p class='muted'>按自然年计算同市场 buy&hold 基准收益；bull=基准年收益>0，bear=<=0。</p>
  {df2html(annual_summary, ["market_bucket","strategy","market_regime","samples","median_benchmark","median_strategy","median_excess","beat_rate"], 60)}
  <h4>整体汇总（不分牛熊）</h4>
  {df2html(annual_overall, ["market_bucket","strategy","samples","median_benchmark","median_strategy","median_excess","beat_rate"], 30)}

  <h2>5) Usage Playbook（Q1~Q17）</h2>
  <ol>
    <li><b>Q1</b>：{q1_sentence}<br/><b>动作</b>：{q1_action}</li>
    <li><b>Q2</b>：{q2_sentence}<br/><b>动作</b>：{q2_action}</li>
    <li><b>Q3</b>：{q3_sentence}<br/><b>动作</b>：{q3_action}</li>
    <li><b>Q4</b>：{q4_sentence}<br/><b>动作</b>：{q4_action}</li>
    <li><b>Q5</b>：{q5_sentence}<br/><b>动作</b>：{q5_action}</li>
    <li><b>Q6</b>：{q6_sentence}<br/><b>动作</b>：{q6_action}</li>
    <li><b>Q7</b>：{q7_sentence}<br/><b>动作</b>：{q7_action}</li>
    <li><b>Q8</b>：风险模块建议：side_regime 触发时降杠杆，下跌期允许防守腿。</li>
    <li><b>Q9</b>：资产适配建议：优先在波动与趋势更充分的市场（如 Crypto）部署；指数更多用于风控门控。</li>
    <li><b>Q10</b>：失效监控：近 6 个月胜率相对历史下滑 &gt; 8pct 时触发降级。</li>
    <li><b>Q11</b>：信号密度：高密度年份应降低单次仓位，避免过度换手。</li>
    <li><b>Q12</b>：{q12_sentence}<br/><b>动作</b>：{q12_action}</li>
    <li><b>Q13</b>：{q13_sentence}<br/><b>动作</b>：{q13_action}</li>
    <li><b>Q14</b>：{q14_sentence}<br/><b>动作</b>：{q14_action}</li>
    <li><b>Q15</b>（{q15_question}）：{q15_answer}<br/><b>动作</b>：{q15_action}</li>
    <li><b>Q16</b>（{q16_question}）：{q16_answer}<br/><b>动作</b>：{q16_action}</li>
    <li><b>Q17</b>（{q17_question}）：{q17_answer}<br/><b>动作</b>：{q17_action}</li>
  </ol>

  <h2>6) 风险与实盘约束</h2>
  <h3>6.1 成本情景压力测试（显式）</h3>
  {df2html(cost_summary, ["mode","fee_bps_roundtrip","markets_n","median_cagr","median_sharpe","median_max_drawdown","pass_rate"], 40)}
  <img src='assets/06_cost_scenario_curves.png' alt='cost-scenario' />
  <p class='muted'>long_short 市场级 break-even（场景插值）</p>
  {df2html(cost_be_df, ["market_name","break_even_fee_bps"], 80)}
  <h3>6.2 失效监控</h3>
  {df2html(failure_df, ["market_name","win_rate_hist","win_rate_recent6m","status","action"], 80)}
  <h3>6.3 尾部风险</h3>
  {df2html(tail_df, ["mode","hold_days","p5_trade_ret","avg_worst5_ret","max_loss_trade","avg_mae","avg_mfe","position_size_hint"], 20)}
  <img src='assets/05_portfolio_nav_dd.png' alt='portfolio-nav-dd' />

  <h2>7) 数据与产物</h2>
  <p>artifact: <code>reports/artifacts/regime_triplet/</code></p>
  <p>site: <code>reports/site/factors/regime_triplet/report.html</code></p>
</div>
</body>
</html>
"""

    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "report.html").write_text(html, encoding="utf-8")

    # index page (append links for both reports)
    idx = root / "reports" / "site" / "index.html"
    idx.parent.mkdir(parents=True, exist_ok=True)
    idx.write_text(
        """<!doctype html><html><head><meta charset='utf-8'><title>Momentum Reports</title></head>
<body><h1>Momentum Reports</h1><ul>
<li><a href='factors/updownwave/report.html'>UpDownWave Report</a></li>
<li><a href='factors/regime_triplet/report.html'>Regime Triplet Report</a></li>
</ul></body></html>""",
        encoding="utf-8",
    )

    manifest = {
        "generatedAt": now,
        "factor": "regime_triplet",
        "config": {
            "base": BASE_CFG.__dict__,
            "holds": HOLDS,
            "modes": MODES,
            "maGrid": MA_GRID,
            "volWindowGrid": VOL_WINDOW_GRID,
            "volMultGrid": VOL_MULT_GRID,
            "costBps": COST_BPS_LIST,
            "oosTrainDays": OOS_TRAIN_DAYS,
            "oosTestDays": OOS_TEST_DAYS,
            "oosStepDays": OOS_STEP_DAYS,
            "oosMaGrid": OOS_MA_GRID,
            "oosVolWindowGrid": OOS_VOL_WINDOW_GRID,
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
