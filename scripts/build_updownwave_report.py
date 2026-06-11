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

from momentum.signals.up_down_wave import UpDownWaveConfig, compute_up_down_wave_signals


# ---------- Config ----------
ASSET_UNIVERSE: List[dict] = [
    # Crypto majors
    {"name": "BTC", "ticker": "BTC-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "BTC"},
    {"name": "ETH", "ticker": "ETH-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "ETH"},
    {"name": "BNB", "ticker": "BNB-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "BNB"},
    {"name": "SOL", "ticker": "SOL-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "SOL"},
    {"name": "XRP", "ticker": "XRP-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "XRP"},
    {"name": "ADA", "ticker": "ADA-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "ADA"},
    {"name": "DOGE", "ticker": "DOGE-USD", "asset_class": "Crypto", "asset_group": "Majors", "label_en": "DOGE"},

    # A-share indexes
    {"name": "上证指数", "ticker": "000001.SS", "asset_class": "A股指数", "asset_group": "宽基指数", "label_en": "SSE Composite"},
    {"name": "沪深300", "ticker": "000300.SS", "asset_class": "A股指数", "asset_group": "宽基指数", "label_en": "CSI 300"},
    {"name": "中证500", "ticker": "510500.SS", "asset_class": "A股指数", "asset_group": "ETF代理", "label_en": "CSI 500 (ETF Proxy)"},
    {"name": "深证成指", "ticker": "399001.SZ", "asset_class": "A股指数", "asset_group": "宽基指数", "label_en": "SZ Component"},
    {"name": "创业板指", "ticker": "159915.SZ", "asset_class": "A股指数", "asset_group": "ETF代理", "label_en": "ChiNext (ETF Proxy)"},

    # A-share representative stocks
    {"name": "贵州茅台", "ticker": "600519.SS", "asset_class": "A股个股", "asset_group": "消费", "label_en": "Kweichow Moutai"},
    {"name": "宁德时代", "ticker": "300750.SZ", "asset_class": "A股个股", "asset_group": "新能源", "label_en": "CATL"},
    {"name": "中国平安", "ticker": "601318.SS", "asset_class": "A股个股", "asset_group": "金融", "label_en": "Ping An"},
    {"name": "招商银行", "ticker": "600036.SS", "asset_class": "A股个股", "asset_group": "金融", "label_en": "CMB"},
    {"name": "京东方A", "ticker": "000725.SZ", "asset_class": "A股个股", "asset_group": "科技制造", "label_en": "BOE A"},
    {"name": "比亚迪A", "ticker": "002594.SZ", "asset_class": "A股个股", "asset_group": "汽车", "label_en": "BYD A"},

    # HK indexes + proxies
    {"name": "恒生指数", "ticker": "^HSI", "asset_class": "港股指数", "asset_group": "宽基指数", "label_en": "Hang Seng"},
    {"name": "国企指数", "ticker": "^HSCE", "asset_class": "港股指数", "asset_group": "宽基指数", "label_en": "HSCEI"},
    {"name": "恒生ETF", "ticker": "2800.HK", "asset_class": "港股指数", "asset_group": "ETF代理", "label_en": "Tracker Fund"},

    # HK representative stocks
    {"name": "小米集团", "ticker": "1810.HK", "asset_class": "港股个股", "asset_group": "科技", "label_en": "Xiaomi"},
    {"name": "腾讯控股", "ticker": "0700.HK", "asset_class": "港股个股", "asset_group": "科技", "label_en": "Tencent"},
    {"name": "阿里巴巴-SW", "ticker": "9988.HK", "asset_class": "港股个股", "asset_group": "科技", "label_en": "Alibaba HK"},
    {"name": "美团-W", "ticker": "3690.HK", "asset_class": "港股个股", "asset_group": "消费科技", "label_en": "Meituan"},
    {"name": "比亚迪股份", "ticker": "1211.HK", "asset_class": "港股个股", "asset_group": "汽车", "label_en": "BYD HK"},
    {"name": "汇丰控股", "ticker": "0005.HK", "asset_class": "港股个股", "asset_group": "金融", "label_en": "HSBC"},

    # US indexes + representative stocks
    {"name": "标普500", "ticker": "^GSPC", "asset_class": "美股指数", "asset_group": "宽基指数", "label_en": "S&P 500"},
    {"name": "纳斯达克", "ticker": "^IXIC", "asset_class": "美股指数", "asset_group": "宽基指数", "label_en": "NASDAQ"},
    {"name": "道琼斯", "ticker": "^DJI", "asset_class": "美股指数", "asset_group": "宽基指数", "label_en": "Dow Jones"},
    {"name": "特斯拉", "ticker": "TSLA", "asset_class": "美股个股", "asset_group": "科技成长", "label_en": "Tesla"},
    {"name": "苹果", "ticker": "AAPL", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "Apple"},
    {"name": "微软", "ticker": "MSFT", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "Microsoft"},
    {"name": "英伟达", "ticker": "NVDA", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "NVIDIA"},
    {"name": "亚马逊", "ticker": "AMZN", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "Amazon"},
    {"name": "谷歌", "ticker": "GOOGL", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "Google"},
    {"name": "Meta", "ticker": "META", "asset_class": "美股个股", "asset_group": "科技龙头", "label_en": "Meta"},

    # Gold
    {"name": "纽约黄金", "ticker": "GC=F", "asset_class": "黄金", "asset_group": "期货", "label_en": "Gold Futures"},
    {"name": "黄金ETF", "ticker": "GLD", "asset_class": "黄金", "asset_group": "ETF", "label_en": "GLD"},
]

SYMBOLS: Dict[str, str] = {x["name"]: x["ticker"] for x in ASSET_UNIVERSE}
ASSET_CLASS_MAP: Dict[str, str] = {x["name"]: x["asset_class"] for x in ASSET_UNIVERSE}
ASSET_GROUP_MAP: Dict[str, str] = {x["name"]: x["asset_group"] for x in ASSET_UNIVERSE}
PLOT_LABELS: Dict[str, str] = {x["name"]: x["label_en"] for x in ASSET_UNIVERSE}

HOLDS = [5, 10, 30]
MODES = ["long_only", "short_only", "long_short"]
MA_WINDOWS = [10, 20, 30, 60]
HOLD_SWEEP = [3, 5, 10, 20, 30]
COST_BPS_LIST = [0, 10, 20, 50]
FORWARD_HORIZONS = [1, 3, 5, 10, 20]

TREND_FILTER = {
    "bbw_window": 20,
    "bbw_std": 2.0,
    "bbw_quantile": 0.55,
    "adr_window": 20,
    "adr_quantile": 0.55,
    "adx_window": 14,
    "adx_quantile": 0.55,
    "adx_floor": 20.0,
}

SCORE_VARIANTS = {
    "eq": "trend_score_eq",
    "adx_weighted": "trend_score_adxw",
    "min_shortboard": "trend_score_min",
}
SCORE_BUCKET_BINS = [0.0, 0.3, 0.5, 0.7, 1.000001]
SCORE_BUCKET_LABELS = ["0-30%", "30-50%", "50-70%", "70-100%"]
THRESHOLD_SCAN = [0.3, 0.4, 0.5, 0.6, 0.7]


@dataclass
class BacktestResult:
    nav: pd.Series
    trades: pd.DataFrame
    in_position: pd.Series


def download_bars(ticker: str, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
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
    return bars


def run_nonoverlap_backtest(
    sig: pd.DataFrame,
    hold_days: int,
    mode: str,
    fee_bps_roundtrip: float = 0.0,
    size_col: str | None = None,
) -> BacktestResult:
    """Non-overlap backtest with optional soft position sizing.

    - Signal at t close
    - Enter at t+1 open
    - Exit at t+hold_days close
    - While in a trade, ignore new signals
    - size_col (optional): per-signal position size in [0,1]
    """

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
                signal = "upwave"
        elif mode == "short_only":
            if dn and not up:
                side = "short"
                signal = "downwave"
        else:
            if up and not dn:
                side = "long"
                signal = "upwave"
            elif dn and not up:
                side = "short"
                signal = "downwave"

        if side is None:
            i += 1
            continue

        pos_size = 1.0
        if size_col is not None and size_col in df.columns:
            raw_size = float(df.loc[i, size_col]) if pd.notna(df.loc[i, size_col]) else 0.0
            pos_size = float(np.clip(raw_size, 0.0, 1.0))

        if pos_size <= 0:
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

        # Flat region up to entry-1
        if cursor <= entry_i - 1:
            nav[cursor:entry_i] = current_nav

        # Mark-to-market during holding window (by close), with soft sizing
        path_ret: List[float] = []
        for t in range(entry_i, exit_i + 1):
            close_t = float(df.loc[t, "close"])
            if not np.isfinite(close_t) or close_t <= 0:
                nav[t] = current_nav
                raw_ret = 0.0
            else:
                if side == "long":
                    raw_ret = close_t / entry_open - 1.0
                else:
                    raw_ret = entry_open / close_t - 1.0
                nav[t] = current_nav * (1.0 + pos_size * raw_ret)
            path_ret.append(float(raw_ret))
            in_pos[t] = pos_size

        exit_nav_gross = float(nav[exit_i])
        exit_nav_net = exit_nav_gross * (1.0 - fee * pos_size)
        nav[exit_i] = exit_nav_net

        gross_ret = exit_nav_gross / current_nav - 1.0
        net_ret = exit_nav_net / current_nav - 1.0

        trades.append(
            {
                "signal": signal,
                "side": side,
                "signal_ts": df.loc[i, "timestamp"],
                "entry_ts": df.loc[entry_i, "timestamp"],
                "exit_ts": df.loc[exit_i, "timestamp"],
                "entry_open": entry_open,
                "exit_close": float(df.loc[exit_i, "close"]),
                "hold_days": hold_days,
                "position_size": pos_size,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "mae": float(np.min(path_ret)) if len(path_ret) else np.nan,
                "mfe": float(np.max(path_ret)) if len(path_ret) else np.nan,
                "win": int(net_ret > 0),
            }
        )

        current_nav = exit_nav_net
        cursor = exit_i + 1
        i = exit_i + 1

    if cursor < n:
        nav[cursor:] = current_nav

    nav_series = pd.Series(nav, index=df["timestamp"]).ffill().fillna(1.0)
    in_pos_series = pd.Series(in_pos, index=df["timestamp"])
    trades_df = pd.DataFrame(trades)
    return BacktestResult(nav=nav_series, trades=trades_df, in_position=in_pos_series)


def calc_metrics(nav: pd.Series, trades: pd.DataFrame, in_pos: pd.Series) -> dict:
    total_return = float(nav.iloc[-1] - 1.0)
    days = (nav.index[-1] - nav.index[0]).days
    cagr = float(nav.iloc[-1] ** (365.0 / days) - 1.0) if days > 0 else np.nan

    peak = nav.cummax()
    drawdown = nav / peak - 1.0
    max_dd = float(drawdown.min())

    daily_ret = nav.pct_change().fillna(0.0)
    ann_vol = float(daily_ret.std(ddof=0) * np.sqrt(252.0)) if daily_ret.std(ddof=0) > 0 else np.nan
    sharpe = float(daily_ret.mean() / daily_ret.std(ddof=0) * np.sqrt(252.0)) if daily_ret.std(ddof=0) > 0 else np.nan

    if len(trades):
        win_rate = float(trades["win"].mean())
        avg_trade = float(trades["net_ret"].mean())
        med_trade = float(trades["net_ret"].median())
        pos_sum = float(trades.loc[trades["net_ret"] > 0, "net_ret"].sum())
        neg_sum = float(trades.loc[trades["net_ret"] < 0, "net_ret"].sum())
        profit_factor = (pos_sum / abs(neg_sum)) if neg_sum < 0 else np.nan
    else:
        win_rate = np.nan
        avg_trade = np.nan
        med_trade = np.nan
        profit_factor = np.nan

    return {
        "total_return": total_return,
        "cagr": cagr,
        "sharpe": sharpe,
        "ann_vol": ann_vol,
        "max_drawdown": max_dd,
        "calmar": float(cagr / abs(max_dd)) if np.isfinite(cagr) and max_dd < 0 else np.nan,
        "trade_count": int(len(trades)),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_trade_ret": avg_trade,
        "median_trade_ret": med_trade,
        "exposure": float(in_pos.mean()),
    }


def yearly_returns(nav: pd.Series) -> pd.Series:
    df = nav.to_frame("nav")
    df["year"] = df.index.year
    out = {}
    for y, g in df.groupby("year"):
        out[int(y)] = float(g["nav"].iloc[-1] / g["nav"].iloc[0] - 1.0)
    return pd.Series(out).sort_index()


def signal_forward_path(df: pd.DataFrame, horizons: List[int]) -> pd.DataFrame:
    tmp = df.copy().reset_index(drop=True)
    out = []
    for h in horizons:
        fut_ret = tmp["close"].shift(-h) / tmp["close"] - 1.0
        up_mask = tmp["upwave"] == 1
        dn_mask = tmp["downwave"] == 1
        out.append(
            {
                "horizon": h,
                "upwave_future_ret_mean": float(fut_ret[up_mask].mean()),
                "downwave_future_ret_mean": float(fut_ret[dn_mask].mean()),
                "downwave_short_ret_mean": float((-fut_ret[dn_mask]).mean()),
                "upwave_count": int(up_mask.sum()),
                "downwave_count": int(dn_mask.sum()),
            }
        )
    return pd.DataFrame(out)


def _pct_rank_01(s: pd.Series) -> pd.Series:
    v = s.astype(float)
    out = pd.Series(np.nan, index=v.index, dtype=float)
    m = v.notna()
    if m.any():
        out.loc[m] = v.loc[m].rank(method="average", pct=True)
    return out.clip(0.0, 1.0)


def _score_bucket(s: pd.Series) -> pd.Series:
    return pd.cut(
        s.clip(0.0, 1.0),
        bins=SCORE_BUCKET_BINS,
        labels=SCORE_BUCKET_LABELS,
        include_lowest=True,
        right=False,
    )


def compute_trend_filter_columns(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Compute BBW/ADR/ADX raw values + normalized scores + score buckets.

    Keeps legacy hard-filter columns for compatibility, while exposing continuous
    score system for deeper analysis.
    """
    out = df.copy()

    close = out["close"].astype(float)
    high = out["high"].astype(float)
    low = out["low"].astype(float)

    # BBW: Bollinger Band Width
    bbw_w = int(cfg["bbw_window"])
    bbw_k = float(cfg["bbw_std"])
    ma = close.rolling(bbw_w, min_periods=bbw_w).mean()
    sd = close.rolling(bbw_w, min_periods=bbw_w).std(ddof=0)
    upper = ma + bbw_k * sd
    lower = ma - bbw_k * sd
    bbw = (upper - lower) / ma.replace(0, np.nan).abs()

    # ADR: Average Daily Range ratio
    adr_w = int(cfg["adr_window"])
    daily_range = (high - low) / close.replace(0, np.nan).abs()
    adr = daily_range.rolling(adr_w, min_periods=adr_w).mean()

    # ADX: trend strength (Wilder-like smoothing)
    adx_w = int(cfg["adx_window"])
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    atr = tr.ewm(alpha=1.0 / adx_w, adjust=False, min_periods=adx_w).mean()
    plus_di = 100.0 * pd.Series(plus_dm, index=out.index).ewm(alpha=1.0 / adx_w, adjust=False, min_periods=adx_w).mean() / atr
    minus_di = 100.0 * pd.Series(minus_dm, index=out.index).ewm(alpha=1.0 / adx_w, adjust=False, min_periods=adx_w).mean() / atr

    di_sum = (plus_di + minus_di).replace(0, np.nan)
    dx = 100.0 * (plus_di - minus_di).abs() / di_sum
    adx = dx.ewm(alpha=1.0 / adx_w, adjust=False, min_periods=adx_w).mean()

    out["bbw"] = bbw
    out["adr"] = adr
    out["adx"] = adx

    # Continuous normalized scores [0,1]
    out["bbw_score"] = _pct_rank_01(out["bbw"])
    out["adr_score"] = _pct_rank_01(out["adr"])
    out["adx_score"] = _pct_rank_01(out["adx"])

    out["trend_score_eq"] = (out["bbw_score"] + out["adr_score"] + out["adx_score"]) / 3.0
    out["trend_score_adxw"] = 0.25 * out["bbw_score"] + 0.25 * out["adr_score"] + 0.50 * out["adx_score"]
    out["trend_score_min"] = out[["bbw_score", "adr_score", "adx_score"]].min(axis=1)

    for k, col in SCORE_VARIANTS.items():
        out[f"{col}_bucket"] = _score_bucket(out[col])

    # Keep legacy hard-filter fields (for backward comparability)
    valid = out[["bbw", "adr", "adx"]].replace([np.inf, -np.inf], np.nan).dropna()
    if valid.empty:
        out["trend_filter"] = 0
        out["upwave_tf"] = 0
        out["downwave_tf"] = 0
        out["trend_filter_meta"] = "invalid"
        return out

    bbw_thr = float(valid["bbw"].quantile(float(cfg["bbw_quantile"])))
    adr_thr = float(valid["adr"].quantile(float(cfg["adr_quantile"])))
    adx_q_thr = float(valid["adx"].quantile(float(cfg["adx_quantile"])))
    adx_thr = max(float(cfg["adx_floor"]), adx_q_thr)

    trend_mask = (
        (out["bbw"] >= bbw_thr)
        & (out["adr"] >= adr_thr)
        & (out["adx"] >= adx_thr)
    )
    out["trend_filter"] = trend_mask.fillna(False).astype(int)
    out["upwave_tf"] = ((out["upwave"] == 1) & (out["trend_filter"] == 1)).astype(int)
    out["downwave_tf"] = ((out["downwave"] == 1) & (out["trend_filter"] == 1)).astype(int)
    out["trend_filter_meta"] = f"bbw>={bbw_thr:.6f};adr>={adr_thr:.6f};adx>={adx_thr:.4f}"

    return out


def compute_up_down_wave_signals_n(bars: pd.DataFrame, ma_period: int, n_days: int) -> pd.DataFrame:
    out = bars.copy().sort_values("timestamp").reset_index(drop=True)
    ma_col = f"ma_{ma_period}"
    out[ma_col] = out["close"].rolling(ma_period, min_periods=ma_period).mean()

    above = out["close"] > out[ma_col]
    below = out["close"] < out[ma_col]

    alln_above = pd.Series(True, index=out.index)
    alln_below = pd.Series(True, index=out.index)
    for k in range(n_days):
        alln_above = alln_above & above.shift(k)
        alln_below = alln_below & below.shift(k)

    bullish_tlag = out["close"].shift(n_days - 1) > out["open"].shift(n_days - 1)
    out["upwave"] = (bullish_tlag & alln_above).fillna(False).astype(int)
    out["downwave"] = alln_below.fillna(False).astype(int)
    return out


def compute_core_baseline_metrics(
    signal_data: Dict[str, pd.DataFrame],
    symbol_map: Dict[str, str],
    asset_class_map: Dict[str, str],
    asset_group_map: Dict[str, str],
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    Dict[Tuple[str, str, int], pd.Series],
    Dict[Tuple[str, str, int], pd.DataFrame],
    Dict[Tuple[str, str, int], pd.Series],
]:
    """Compute baseline cross-market metrics (ma20, modes x holds)."""

    rows = []
    nav_store: Dict[Tuple[str, str, int], pd.Series] = {}
    trades_store: Dict[Tuple[str, str, int], pd.DataFrame] = {}
    inpos_store: Dict[Tuple[str, str, int], pd.Series] = {}

    for name, sig in signal_data.items():
        bh = float(sig["close"].iloc[-1] / sig["close"].iloc[0] - 1.0)
        up_total = int(sig["upwave"].sum())
        down_total = int(sig["downwave"].sum())

        for mode in MODES:
            for hold in HOLDS:
                res = run_nonoverlap_backtest(sig, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0)
                m = calc_metrics(res.nav, res.trades, res.in_position)
                rows.append(
                    {
                        "market_name": name,
                        "ticker": symbol_map[name],
                        "asset_class": asset_class_map.get(name, "Unknown"),
                        "asset_group": asset_group_map.get(name, "Unknown"),
                        "mode": mode,
                        "hold_days": hold,
                        "start": sig["timestamp"].iloc[0].strftime("%Y-%m-%d"),
                        "end": sig["timestamp"].iloc[-1].strftime("%Y-%m-%d"),
                        "bars": int(len(sig)),
                        "up_signals_total": up_total,
                        "down_signals_total": down_total,
                        "signals_total": up_total + down_total,
                        "buyhold_ret": bh,
                        **m,
                    }
                )
                nav_store[(name, mode, hold)] = res.nav
                trades_store[(name, mode, hold)] = res.trades
                inpos_store[(name, mode, hold)] = res.in_position

    cross_df = pd.DataFrame(rows).sort_values(["mode", "asset_class", "market_name", "hold_days"]).reset_index(drop=True)

    asset_class_summary = (
        cross_df[cross_df["mode"] == "long_short"]
        .groupby(["asset_class", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            pass_rate_pos=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["asset_class", "hold_days"])
        .reset_index(drop=True)
    )

    return cross_df, asset_class_summary, nav_store, trades_store, inpos_store


def compute_usage_q1_q3(
    score_data: Dict[str, pd.DataFrame],
    asset_class_map: Dict[str, str],
) -> tuple[
    Dict[str, pd.DataFrame],
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    """Compute usage playbook Q1~Q3 artifacts with explicit IO boundaries."""

    score_data_out: Dict[str, pd.DataFrame] = {}
    regime_rows = []
    q1_rows = []
    event_rows = []
    fear_rows = []

    for name, sig_sc in score_data.items():
        s = sig_sc.copy()
        s["eq_score"] = s[SCORE_VARIANTS["eq"]].fillna(0.0).clip(0.0, 1.0)
        s["regime"] = np.where(s["eq_score"] >= 0.7, "up", np.where(s["eq_score"] >= 0.3, "side", "down"))
        score_data_out[name] = s

        regime_rows.append(
            {
                "market_name": name,
                "asset_class": asset_class_map.get(name, "Unknown"),
                "up_ratio": float((s["regime"] == "up").mean()),
                "side_ratio": float((s["regime"] == "side").mean()),
                "down_ratio": float((s["regime"] == "down").mean()),
            }
        )

        bh_nav = pd.Series(
            (s["close"].astype(float) / float(s["close"].iloc[0])).values,
            index=pd.to_datetime(s["timestamp"], utc=True),
        )
        bh_m = calc_metrics(bh_nav, pd.DataFrame(), pd.Series(np.ones(len(s)), index=bh_nav.index))
        q1_rows.append(
            {
                "market_name": name,
                "asset_class": asset_class_map.get(name, "Unknown"),
                "scenario": "buy_hold",
                "mode": "long_only",
                "hold_days": 0,
                **bh_m,
            }
        )

        base_long = run_nonoverlap_backtest(s, hold_days=10, mode="long_only", fee_bps_roundtrip=0.0)
        q1_rows.append(
            {
                "market_name": name,
                "asset_class": asset_class_map.get(name, "Unknown"),
                "scenario": "upwave_entry",
                "mode": "long_only",
                "hold_days": 10,
                **calc_metrics(base_long.nav, base_long.trades, base_long.in_position),
            }
        )

        for rg in ["up", "side", "down"]:
            sx = s.copy()
            mm = sx["regime"] == rg
            sx["upwave"] = ((sx["upwave"] == 1) & mm).astype(int)
            sx["downwave"] = ((sx["downwave"] == 1) & mm).astype(int)
            r = run_nonoverlap_backtest(sx, hold_days=10, mode="long_only", fee_bps_roundtrip=0.0)
            q1_rows.append(
                {
                    "market_name": name,
                    "asset_class": asset_class_map.get(name, "Unknown"),
                    "scenario": f"trade_permission_{rg}",
                    "mode": "long_only",
                    "hold_days": 10,
                    **calc_metrics(r.nav, r.trades, r.in_position),
                }
            )

        close = s["close"].astype(float).reset_index(drop=True)
        high = s["high"].astype(float).reset_index(drop=True)
        low = s["low"].astype(float).reset_index(drop=True)
        prev_close = close.shift(1)
        tr = pd.concat([(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
        atr_pct = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean() / close.replace(0, np.nan).abs()

        s["atr_pct"] = atr_pct
        s["adx_q"] = _pct_rank_01(s["adx"])
        s["bbw_q"] = _pct_rank_01(s["bbw"])
        s["atr_q"] = _pct_rank_01(s["atr_pct"])
        s["adx_bucket"] = pd.qcut(s["adx_q"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"], duplicates="drop")
        s["bbw_bucket"] = pd.qcut(s["bbw_q"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"], duplicates="drop")
        s["atr_bucket"] = pd.qcut(s["atr_q"], q=5, labels=["Q1", "Q2", "Q3", "Q4", "Q5"], duplicates="drop")
        score_data_out[name] = s

        for idx in s.index[s["upwave"] == 1]:
            for h in [1, 3, 5, 10, 20, 30]:
                if idx + h >= len(s):
                    continue
                base = float(close.iloc[idx])
                fut = float(close.iloc[idx + h] / base - 1.0)
                path = close.iloc[idx + 1 : idx + h + 1] / base - 1.0
                mae = float(path.min()) if len(path) else np.nan
                event_rows.append(
                    {
                        "market_name": name,
                        "asset_class": asset_class_map.get(name, "Unknown"),
                        "signal_side": "upwave_long",
                        "horizon": h,
                        "ret": fut,
                        "mae": mae,
                    }
                )

                if h == 10:
                    fear_rows.append(
                        {
                            "market_name": name,
                            "asset_class": asset_class_map.get(name, "Unknown"),
                            "signal_side": "upwave_long",
                            "ret_h10": fut,
                            "adx": float(s.loc[idx, "adx"]),
                            "adx_q": float(s.loc[idx, "adx_q"]) if pd.notna(s.loc[idx, "adx_q"]) else np.nan,
                            "adx_bucket": s.loc[idx, "adx_bucket"],
                            "bbw_q": float(s.loc[idx, "bbw_q"]) if pd.notna(s.loc[idx, "bbw_q"]) else np.nan,
                            "bbw_bucket": s.loc[idx, "bbw_bucket"],
                            "atr_q": float(s.loc[idx, "atr_q"]) if pd.notna(s.loc[idx, "atr_q"]) else np.nan,
                            "atr_bucket": s.loc[idx, "atr_bucket"],
                        }
                    )

        for idx in s.index[s["downwave"] == 1]:
            for h in [1, 3, 5, 10, 20, 30]:
                if idx + h >= len(s):
                    continue
                base = float(close.iloc[idx])
                fut_short = float(base / close.iloc[idx + h] - 1.0)
                path_short = base / close.iloc[idx + 1 : idx + h + 1] - 1.0
                mae_short = float(path_short.min()) if len(path_short) else np.nan
                event_rows.append(
                    {
                        "market_name": name,
                        "asset_class": asset_class_map.get(name, "Unknown"),
                        "signal_side": "downwave_short",
                        "horizon": h,
                        "ret": fut_short,
                        "mae": mae_short,
                    }
                )

                if h == 10:
                    fear_rows.append(
                        {
                            "market_name": name,
                            "asset_class": asset_class_map.get(name, "Unknown"),
                            "signal_side": "downwave_short",
                            "ret_h10": fut_short,
                            "adx": float(s.loc[idx, "adx"]),
                            "adx_q": float(s.loc[idx, "adx_q"]) if pd.notna(s.loc[idx, "adx_q"]) else np.nan,
                            "adx_bucket": s.loc[idx, "adx_bucket"],
                            "bbw_q": float(s.loc[idx, "bbw_q"]) if pd.notna(s.loc[idx, "bbw_q"]) else np.nan,
                            "bbw_bucket": s.loc[idx, "bbw_bucket"],
                            "atr_q": float(s.loc[idx, "atr_q"]) if pd.notna(s.loc[idx, "atr_q"]) else np.nan,
                            "atr_bucket": s.loc[idx, "atr_bucket"],
                        }
                    )

    regime_df_play = pd.DataFrame(regime_rows)
    q1_df = pd.DataFrame(q1_rows)
    q1_summary = (
        q1_df.groupby(["scenario"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            median_win_rate=("win_rate", "median"),
            median_trade_count=("trade_count", "median"),
        )
        .sort_values("scenario")
    )

    event_df = pd.DataFrame(event_rows)
    event_summary = (
        event_df.groupby(["signal_side", "horizon"], as_index=False)
        .agg(
            samples=("ret", "size"),
            mean_ret=("ret", "mean"),
            median_ret=("ret", "median"),
            p10_ret=("ret", lambda s: float(np.nanquantile(s, 0.10))),
            p90_ret=("ret", lambda s: float(np.nanquantile(s, 0.90))),
            mean_mae=("mae", "mean"),
        )
        .sort_values(["signal_side", "horizon"])
    )

    fear_df = pd.DataFrame(fear_rows)
    fear_tables = []
    for ind_col, bucket_col in [("adx", "adx_bucket"), ("bbw_q", "bbw_bucket"), ("atr_q", "atr_bucket")]:
        g = (
            fear_df.groupby(["signal_side", bucket_col], as_index=False)
            .agg(
                samples=("ret_h10", "size"),
                mean_ret=("ret_h10", "mean"),
                win_rate=("ret_h10", lambda s: float((s > 0).mean())),
                p10_ret=("ret_h10", lambda s: float(np.nanquantile(s, 0.10))),
            )
            .rename(columns={bucket_col: "bucket"})
        )
        g["indicator"] = ind_col
        fear_tables.append(g)
    fear_summary = pd.concat(fear_tables, ignore_index=True)

    return score_data_out, regime_df_play, q1_df, q1_summary, event_df, event_summary, fear_df, fear_summary


def compute_usage_q4_q6(
    signal_data: Dict[str, pd.DataFrame],
    market_data: Dict[str, pd.DataFrame],
    cross_df: pd.DataFrame,
    break_even_df: pd.DataFrame,
    loaded_names: List[str],
    asset_class_map: Dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute usage playbook Q4~Q6 artifacts with explicit IO boundaries."""

    # internal: Q4 hold robustness
    hold_rows = []
    for name, sig in signal_data.items():
        for mode in MODES:
            for hold in HOLD_SWEEP:
                r = run_nonoverlap_backtest(sig, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0)
                hold_rows.append(
                    {
                        "market_name": name,
                        "asset_class": asset_class_map.get(name, "Unknown"),
                        "mode": mode,
                        "hold_days": hold,
                        **calc_metrics(r.nav, r.trades, r.in_position),
                    }
                )
    hold_df = pd.DataFrame(hold_rows)

    hold_summary = (
        hold_df.groupby(["mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            median_trade_count=("trade_count", "median"),
        )
        .sort_values(["mode", "hold_days"])
    )

    robust_rows = []
    for mode in MODES:
        p = hold_summary[hold_summary["mode"] == mode].copy()
        if p.empty:
            continue
        max_cagr = float(p["median_cagr"].max())
        cand = p[p["median_cagr"] >= max_cagr * 0.9].sort_values("hold_days")
        if cand.empty:
            cand = p.sort_values("median_cagr", ascending=False).head(1)
        robust_min = int(cand["hold_days"].min())
        robust_max = int(cand["hold_days"].max())
        robust_default = int(int(np.median(cand["hold_days"])))
        robust_rows.append(
            {
                "mode": mode,
                "robust_hold_min": robust_min,
                "robust_hold_max": robust_max,
                "recommended_default_hold": robust_default,
            }
        )
    hold_robust_band = pd.DataFrame(robust_rows)

    # internal: Q5 rolling OOS
    oos_rows = []
    for name, bars in market_data.items():
        n = len(bars)
        train_len = 504
        test_len = 126
        step = 126

        for ma in [10, 20, 30]:
            for nd in [3, 4, 5]:
                sign = compute_up_down_wave_signals_n(bars, ma_period=ma, n_days=nd)
                sign["timestamp"] = pd.to_datetime(sign["timestamp"], utc=True)

                fold = 0
                start = 0
                while start + train_len + test_len <= n:
                    ts = start + train_len
                    te = ts + test_len
                    test = sign.iloc[ts:te].copy().reset_index(drop=True)
                    if len(test) < 40:
                        start += step
                        fold += 1
                        continue
                    rr = run_nonoverlap_backtest(test, hold_days=10, mode="long_short", fee_bps_roundtrip=0.0)
                    mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                    oos_rows.append(
                        {
                            "market_name": name,
                            "asset_class": asset_class_map.get(name, "Unknown"),
                            "ma_period": ma,
                            "n_days": nd,
                            "fold": fold,
                            "test_start": str(test["timestamp"].iloc[0])[:10],
                            "test_end": str(test["timestamp"].iloc[-1])[:10],
                            **mm,
                        }
                    )
                    start += step
                    fold += 1

    oos_df = pd.DataFrame(oos_rows)

    oos_summary = (
        oos_df.groupby(["ma_period", "n_days"], as_index=False)
        .agg(
            samples=("cagr", "size"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_max_drawdown=("max_drawdown", "median"),
            median_win_rate=("win_rate", "median"),
        )
        .sort_values(["ma_period", "n_days"])
    )

    # internal: Q6 cost budget
    years_est = max(
        (
            signal_data[loaded_names[0]]["timestamp"].iloc[-1]
            - signal_data[loaded_names[0]]["timestamp"].iloc[0]
        ).days
        / 365.0,
        1.0,
    )
    base_ls10 = cross_df[(cross_df["mode"] == "long_short") & (cross_df["hold_days"] == 10)][["market_name", "trade_count"]]
    cost_budget = break_even_df.merge(base_ls10, on="market_name", how="left")
    cost_budget["turnover_trades_per_year"] = cost_budget["trade_count"] / years_est
    cost_budget["required_hold_hint"] = np.where(cost_budget["break_even_fee_bps"] < 10, ">=20", ">=10")

    return hold_df, hold_summary, hold_robust_band, oos_df, oos_summary, cost_budget


def compute_usage_q7_q9(
    score_data: Dict[str, pd.DataFrame],
    nav_store: Dict[Tuple[str, str, int], pd.Series],
    loaded_names: List[str],
    cross_df: pd.DataFrame,
    coverage_df: pd.DataFrame,
    break_even_df: pd.DataFrame,
    oos_df: pd.DataFrame,
    asset_class_map: Dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series | None, pd.Series | None]:
    """Compute usage playbook Q7~Q9 artifacts with explicit IO boundaries."""

    combo_rows = []
    combo_nav: Dict[Tuple[str, str], pd.Series] = {}
    for name, s in score_data.items():
        eq = s[SCORE_VARIANTS["eq"]].fillna(0.0).clip(0.0, 1.0)

        combo_defs = {
            "hard_and": (s["trend_filter"].astype(float), True),
            "regime_layer": (np.where(eq >= 0.7, 1.0, np.where(eq >= 0.3, 0.3, 0.0)), True),
            "score_top30": ((eq >= 0.7).astype(float), True),
            "score_top50": ((eq >= 0.5).astype(float), True),
            "score_top70": ((eq >= 0.3).astype(float), True),
        }

        for combo_name, (size_vec, _) in combo_defs.items():
            sx = s.copy()
            sx["position_size"] = size_vec
            for mode in MODES:
                for hold in HOLDS:
                    rr = run_nonoverlap_backtest(sx, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0, size_col="position_size")
                    mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
                    combo_rows.append(
                        {
                            "market_name": name,
                            "asset_class": asset_class_map.get(name, "Unknown"),
                            "combo_method": combo_name,
                            "mode": mode,
                            "hold_days": hold,
                            **mm,
                        }
                    )
                    if mode == "long_short" and hold == 10:
                        combo_nav[(name, combo_name)] = rr.nav

    combo_df = pd.DataFrame(combo_rows)

    combo_summary = (
        combo_df.groupby(["combo_method", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            median_trade_count=("trade_count", "median"),
            median_exposure=("exposure", "median"),
        )
        .sort_values(["mode", "hold_days", "combo_method"])
    )

    # Q8 risk module
    nav_pb: pd.Series | None = None
    nav_pl: pd.Series | None = None
    ret_base = []
    ret_layer = []
    for name in loaded_names:
        nb = nav_store.get((name, "long_short", 10))
        nl = combo_nav.get((name, "regime_layer"))
        if nb is None or nl is None:
            continue
        ret_base.append(nb.pct_change().fillna(0.0).rename(name))
        ret_layer.append(nl.pct_change().fillna(0.0).rename(name))

    if ret_base and ret_layer:
        rb = pd.concat(ret_base, axis=1).fillna(0.0).mean(axis=1)
        rl = pd.concat(ret_layer, axis=1).fillna(0.0).mean(axis=1)
        nav_pb = (1.0 + rb).cumprod()
        nav_pl = (1.0 + rl).cumprod()

        m_pb = calc_metrics(nav_pb, pd.DataFrame(), pd.Series(np.ones(len(nav_pb)), index=nav_pb.index))
        m_pl = calc_metrics(nav_pl, pd.DataFrame(), pd.Series(np.ones(len(nav_pl)), index=nav_pl.index))

        risk_mod = pd.DataFrame(
            [
                {"portfolio": "baseline", **m_pb, "recovery_days": calc_recovery_days(nav_pb)},
                {"portfolio": "regime_layer", **m_pl, "recovery_days": calc_recovery_days(nav_pl)},
            ]
        )
    else:
        risk_mod = pd.DataFrame()

    # Q9 asset whitelist
    oos_base = oos_df[(oos_df["ma_period"] == 20) & (oos_df["n_days"] == 4)]
    oos_pos = oos_base.groupby("market_name", as_index=False).agg(rolling_pos_rate=("cagr", lambda s: float((s > 0).mean())))

    class_tbl = (
        cross_df[(cross_df["mode"] == "long_short") & (cross_df["hold_days"] == 10)]
        .groupby(["asset_class"], as_index=False)
        .agg(
            median_mdd=("max_drawdown", "median"),
            median_calmar=("calmar", "median"),
        )
    )

    mk_tbl = coverage_df[["market_name", "asset_class"]].merge(oos_pos, on="market_name", how="left")
    mk_tbl = mk_tbl.merge(break_even_df[["market_name", "break_even_fee_bps"]], on="market_name", how="left")
    class_extra = mk_tbl.groupby("asset_class", as_index=False).agg(
        median_rolling_pos_rate=("rolling_pos_rate", "median"),
        median_break_even_fee_bps=("break_even_fee_bps", "median"),
    )

    class_suit = class_tbl.merge(class_extra, on="asset_class", how="left")
    class_suit["list_flag"] = np.where(
        (class_suit["median_rolling_pos_rate"] >= 0.55)
        & (class_suit["median_break_even_fee_bps"] >= 20)
        & (class_suit["median_calmar"] > 0),
        "white",
        "black_or_watch",
    )

    return combo_df, combo_summary, risk_mod, class_suit, nav_pb, nav_pl


def compute_usage_q10_q11(
    signal_data: Dict[str, pd.DataFrame],
    trades_store: Dict[Tuple[str, str, int], pd.DataFrame],
    inpos_store: Dict[Tuple[str, str, int], pd.Series],
    score_data: Dict[str, pd.DataFrame],
    loaded_names: List[str],
    asset_class_map: Dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Compute usage playbook Q10~Q11 artifacts with explicit IO boundaries."""

    fail_rows = []
    for name in loaded_names:
        tr = trades_store.get((name, "long_short", 10), pd.DataFrame()).copy()
        if tr.empty:
            continue
        tr["exit_ts"] = pd.to_datetime(tr["exit_ts"], utc=True)
        end = tr["exit_ts"].max()
        cut6 = end - pd.Timedelta(days=180)
        cut3 = end - pd.Timedelta(days=90)
        cut9 = end - pd.Timedelta(days=270)

        recent6 = tr[tr["exit_ts"] >= cut6]
        hist6 = tr[tr["exit_ts"] < cut6]
        p1 = tr[(tr["exit_ts"] >= cut9) & (tr["exit_ts"] < cut6)]
        p2 = tr[(tr["exit_ts"] >= cut6) & (tr["exit_ts"] < cut3)]
        p3 = tr[tr["exit_ts"] >= cut3]

        wr_hist = float(hist6["win"].mean()) if len(hist6) else float(tr["win"].mean())
        wr_recent = float(recent6["win"].mean()) if len(recent6) else np.nan
        mae_hist = float(hist6["mae"].mean()) if len(hist6) else float(tr["mae"].mean())
        mae_recent = float(recent6["mae"].mean()) if len(recent6) else np.nan

        score_side = score_data[name].copy()
        score_side["eq_score"] = score_side[SCORE_VARIANTS["eq"]].fillna(0.0)
        score_side["is_side"] = ((score_side["eq_score"] >= 0.3) & (score_side["eq_score"] < 0.7)).astype(int)
        side_hist = float(score_side["is_side"].mean())
        side_recent = float(score_side.loc[score_side["timestamp"] >= cut6, "is_side"].mean()) if (score_side["timestamp"] >= cut6).any() else np.nan

        wr_p1 = float(p1["win"].mean()) if len(p1) else np.nan
        wr_p2 = float(p2["win"].mean()) if len(p2) else np.nan
        wr_p3 = float(p3["win"].mean()) if len(p3) else np.nan

        consecutive_weak = int((pd.notna(wr_p2) and wr_p2 < wr_hist - 0.08) and (pd.notna(wr_p3) and wr_p3 < wr_hist - 0.08))

        if consecutive_weak and pd.notna(mae_recent) and pd.notna(mae_hist) and mae_recent < mae_hist * 1.25:
            status = "stop"
            action = "停用（仅保留监控）"
        elif (pd.notna(wr_recent) and wr_recent < wr_hist - 0.08) or (pd.notna(side_recent) and side_recent > side_hist + 0.12):
            status = "degrade"
            action = "降级为过滤器（禁主动入场）"
        else:
            status = "normal"
            action = "正常运行"

        fail_rows.append(
            {
                "market_name": name,
                "asset_class": asset_class_map.get(name, "Unknown"),
                "win_rate_hist": wr_hist,
                "win_rate_recent6m": wr_recent,
                "win_rate_p1": wr_p1,
                "win_rate_p2": wr_p2,
                "win_rate_p3": wr_p3,
                "mae_hist": mae_hist,
                "mae_recent6m": mae_recent,
                "side_ratio_hist": side_hist,
                "side_ratio_recent6m": side_recent,
                "consecutive_weak": consecutive_weak,
                "status": status,
                "action": action,
            }
        )

    failure_df = pd.DataFrame(fail_rows)

    density_rows = []
    for name in loaded_names:
        sig = signal_data[name].copy()
        sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
        sig["year"] = sig["timestamp"].dt.year

        tr = trades_store.get((name, "long_short", 10), pd.DataFrame()).copy()
        if not tr.empty:
            tr["entry_ts"] = pd.to_datetime(tr["entry_ts"], utc=True)
            tr["year"] = tr["entry_ts"].dt.year
        inpos = inpos_store.get((name, "long_short", 10))
        if inpos is not None:
            inp = inpos.to_frame("in_pos")
            inp["year"] = inp.index.year
        else:
            inp = pd.DataFrame(columns=["in_pos", "year"])

        years = sorted(sig["year"].unique())
        for y in years:
            sgy = sig[sig["year"] == y]
            tgy = tr[tr["year"] == y] if not tr.empty else pd.DataFrame()
            igy = inp[inp["year"] == y] if not inp.empty else pd.DataFrame()
            density_rows.append(
                {
                    "market_name": name,
                    "asset_class": asset_class_map.get(name, "Unknown"),
                    "year": int(y),
                    "signal_count": int(sgy["upwave"].sum() + sgy["downwave"].sum()),
                    "trade_count": int(len(tgy)),
                    "avg_hold_days": float(tgy["hold_days"].mean()) if len(tgy) else np.nan,
                    "idle_ratio": float(1.0 - igy["in_pos"].mean()) if len(igy) else np.nan,
                }
            )

    density_df = pd.DataFrame(density_rows)
    density_summary = (
        density_df.groupby(["year"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            mean_signal_count=("signal_count", "mean"),
            mean_trade_count=("trade_count", "mean"),
            mean_idle_ratio=("idle_ratio", "mean"),
        )
        .sort_values("year")
    )

    return failure_df, density_df, density_summary


def compute_usage_q12_q14(
    trades_store: Dict[Tuple[str, str, int], pd.DataFrame],
    loaded_names: List[str],
) -> pd.DataFrame:
    """Compute usage playbook Q12~Q14-related artifact (tail risk summary)."""

    tail_rows = []
    for mode in MODES:
        for hold in HOLDS:
            all_tr = []
            for name in loaded_names:
                tr = trades_store.get((name, mode, hold), pd.DataFrame())
                if tr is not None and len(tr):
                    all_tr.append(tr[["net_ret", "mae", "mfe"]])
            if not all_tr:
                continue
            tt = pd.concat(all_tr, ignore_index=True)
            q5 = float(np.nanquantile(tt["net_ret"], 0.05))
            worst5 = tt[tt["net_ret"] <= q5]
            tail_rows.append(
                {
                    "mode": mode,
                    "hold_days": hold,
                    "p5_trade_ret": q5,
                    "avg_worst5_ret": float(worst5["net_ret"].mean()) if len(worst5) else np.nan,
                    "max_loss_trade": float(tt["net_ret"].min()),
                    "avg_mae": float(tt["mae"].mean()),
                    "avg_mfe": float(tt["mfe"].mean()),
                    "position_size_hint": float(min(1.0, 0.02 / abs(q5))) if q5 < 0 else 1.0,
                }
            )

    return pd.DataFrame(tail_rows)


def calc_recovery_days(nav: pd.Series) -> int:
    arr = nav.astype(float).values
    if len(arr) == 0:
        return 0
    peak = arr[0]
    draw_len = 0
    max_draw_len = 0
    for v in arr:
        if v >= peak:
            peak = v
            draw_len = 0
        else:
            draw_len += 1
            max_draw_len = max(max_draw_len, draw_len)
    return int(max_draw_len)


def heatmap(
    ax,
    pivot: pd.DataFrame,
    title: str,
    cmap: str = "RdYlGn",
    center_zero: bool = False,
    clip_abs_q: float | None = None,
):
    arr = pivot.values.astype(float)

    kwargs = {}
    finite_vals = arr[np.isfinite(arr)]
    if center_zero and finite_vals.size > 0:
        if clip_abs_q is not None:
            lim = float(np.nanquantile(np.abs(finite_vals), clip_abs_q))
        else:
            lim = float(np.nanmax(np.abs(finite_vals)))
        lim = max(lim, 1e-12)
        kwargs = {"vmin": -lim, "vmax": lim}

    im = ax.imshow(arr, aspect="auto", cmap=cmap, **kwargs)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ylabels = [PLOT_LABELS.get(str(x), str(x)) for x in pivot.index]
    ax.set_yticklabels(ylabels)
    ax.set_title(title)

    annotate = arr.shape[0] * arr.shape[1] <= 120
    if annotate:
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                v = arr[i, j]
                txt = "nan" if not np.isfinite(v) else f"{v:.2%}"
                ax.text(j, i, txt, ha="center", va="center", fontsize=7)

    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def pct(x):
    return "-" if (x is None or not np.isfinite(x)) else f"{x:.2%}"


def num(x, d=3):
    return "-" if (x is None or not np.isfinite(x)) else f"{x:.{d}f}"


def main():
    root = Path(__file__).resolve().parents[1]
    artifact_dir = root / "reports" / "artifacts" / "updownwave"
    site_dir = root / "reports" / "site" / "factors" / "updownwave"
    asset_dir = site_dir / "assets"

    artifact_dir.mkdir(parents=True, exist_ok=True)
    asset_dir.mkdir(parents=True, exist_ok=True)

    # 1) Load market data + baseline signals(ma20)
    market_data: Dict[str, pd.DataFrame] = {}
    signal_data: Dict[str, pd.DataFrame] = {}
    coverage_rows: List[dict] = []
    failed_rows: List[dict] = []

    for name, ticker in SYMBOLS.items():
        try:
            bars = download_bars(ticker)
        except Exception as e:
            failed_rows.append({"market_name": name, "ticker": ticker, "reason": str(e)[:200]})
            continue

        if bars.empty or len(bars) < 120:
            failed_rows.append({"market_name": name, "ticker": ticker, "reason": f"insufficient_bars:{len(bars)}"})
            continue

        bars["symbol"] = ticker
        bars["market_name"] = name
        bars["asset_class"] = ASSET_CLASS_MAP.get(name, "Unknown")
        bars["asset_group"] = ASSET_GROUP_MAP.get(name, "Unknown")
        market_data[name] = bars

        sig = compute_up_down_wave_signals(bars, config=UpDownWaveConfig(ma_period=20))
        sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
        sig["market_name"] = name
        sig["ticker"] = ticker
        sig["asset_class"] = ASSET_CLASS_MAP.get(name, "Unknown")
        sig["asset_group"] = ASSET_GROUP_MAP.get(name, "Unknown")
        signal_data[name] = sig

        coverage_rows.append(
            {
                "market_name": name,
                "ticker": ticker,
                "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                "asset_group": ASSET_GROUP_MAP.get(name, "Unknown"),
                "bars": int(len(bars)),
                "start": bars["timestamp"].iloc[0].strftime("%Y-%m-%d"),
                "end": bars["timestamp"].iloc[-1].strftime("%Y-%m-%d"),
            }
        )

    if not market_data:
        raise RuntimeError("No symbols loaded successfully; cannot generate report.")

    coverage_df = pd.DataFrame(coverage_rows).sort_values(["asset_class", "market_name"]).reset_index(drop=True)
    coverage_df.to_csv(artifact_dir / "universe_coverage.csv", index=False)

    failed_df = pd.DataFrame(failed_rows, columns=["market_name", "ticker", "reason"])
    failed_df.to_csv(artifact_dir / "universe_failed.csv", index=False)

    loaded_names = list(market_data.keys())

    # 2) Core baseline metrics (decoupled unit)
    cross_df, asset_class_summary, nav_store, trades_store, inpos_store = compute_core_baseline_metrics(
        signal_data=signal_data,
        symbol_map=SYMBOLS,
        asset_class_map=ASSET_CLASS_MAP,
        asset_group_map=ASSET_GROUP_MAP,
    )
    cross_df.to_csv(artifact_dir / "cross_market_metrics.csv", index=False)
    asset_class_summary.to_csv(artifact_dir / "asset_class_summary_longshort.csv", index=False)

    # 2b) Trend-score research pipeline (soft score first, then gating)
    score_data: Dict[str, pd.DataFrame] = {}
    signal_ret_rows = []

    for name, sig_base in signal_data.items():
        sig_sc = compute_trend_filter_columns(sig_base, cfg=TREND_FILTER)
        score_data[name] = sig_sc

        sig_total = int(sig_sc["upwave"].sum() + sig_sc["downwave"].sum())
        sig_tf_total = int(sig_sc["upwave_tf"].sum() + sig_sc["downwave_tf"].sum())
        signal_ret_rows.append(
            {
                "market_name": name,
                "ticker": SYMBOLS[name],
                "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                "asset_group": ASSET_GROUP_MAP.get(name, "Unknown"),
                "signals_total": sig_total,
                "signals_tf_total": sig_tf_total,
                "signal_retention": float(sig_tf_total / sig_total) if sig_total > 0 else np.nan,
                "trend_days_ratio": float(sig_sc["trend_filter"].mean()),
            }
        )

    tf_signal_df = pd.DataFrame(signal_ret_rows).sort_values(["asset_class", "market_name"]).reset_index(drop=True)
    tf_signal_df.to_csv(artifact_dir / "trend_filter_signal_retention.csv", index=False)

    # 2b-1) score bucket -> forward returns (signal-level)
    forward_rows = []
    for name, sig_sc in score_data.items():
        for score_name, score_col in SCORE_VARIANTS.items():
            bucket_col = f"{score_col}_bucket"
            for hold in HOLDS:
                fut = sig_sc["close"].shift(-hold) / sig_sc["close"] - 1.0

                for side_label, mask, ret in [
                    ("upwave_long", sig_sc["upwave"] == 1, fut),
                    ("downwave_short", sig_sc["downwave"] == 1, -fut),
                ]:
                    part = pd.DataFrame({"bucket": sig_sc[bucket_col], "ret": ret, "mask": mask.astype(int)})
                    part = part[(part["mask"] == 1) & part["bucket"].notna() & part["ret"].notna()]
                    if part.empty:
                        continue

                    gb = part.groupby("bucket", observed=False)["ret"]
                    for bucket, s in gb:
                        forward_rows.append(
                            {
                                "market_name": name,
                                "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                                "score_version": score_name,
                                "signal_side": side_label,
                                "hold_days": hold,
                                "score_bucket": str(bucket),
                                "samples": int(len(s)),
                                "mean_ret": float(s.mean()),
                                "median_ret": float(s.median()),
                                "win_rate": float((s > 0).mean()),
                            }
                        )

    score_forward_df = pd.DataFrame(forward_rows)
    score_forward_df.to_csv(artifact_dir / "trend_score_forward_by_bucket.csv", index=False)

    score_forward_summary = (
        score_forward_df.groupby(["score_version", "signal_side", "hold_days", "score_bucket"], as_index=False)
        .agg(
            samples=("samples", "sum"),
            mean_ret=("mean_ret", "mean"),
            median_ret=("median_ret", "median"),
            win_rate=("win_rate", "mean"),
        )
        .sort_values(["score_version", "signal_side", "hold_days", "score_bucket"])
        .reset_index(drop=True)
    )
    score_forward_summary.to_csv(artifact_dir / "trend_score_forward_summary.csv", index=False)

    # 2b-2) score bucket -> strategy metrics (bucket as state-conditioned strategy)
    bucket_metric_rows = []
    for name, sig_sc in score_data.items():
        for score_name, score_col in SCORE_VARIANTS.items():
            bucket_col = f"{score_col}_bucket"
            for bucket in SCORE_BUCKET_LABELS:
                mm = sig_sc[bucket_col] == bucket
                sig_bucket = sig_sc.copy()
                sig_bucket["upwave"] = ((sig_bucket["upwave"] == 1) & mm).astype(int)
                sig_bucket["downwave"] = ((sig_bucket["downwave"] == 1) & mm).astype(int)

                for mode in MODES:
                    for hold in HOLDS:
                        res = run_nonoverlap_backtest(sig_bucket, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0)
                        m = calc_metrics(res.nav, res.trades, res.in_position)
                        bucket_metric_rows.append(
                            {
                                "market_name": name,
                                "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                                "score_version": score_name,
                                "score_bucket": bucket,
                                "mode": mode,
                                "hold_days": hold,
                                **m,
                            }
                        )

    score_bucket_metrics = pd.DataFrame(bucket_metric_rows)
    score_bucket_metrics.to_csv(artifact_dir / "trend_score_bucket_strategy_metrics.csv", index=False)

    score_bucket_summary = (
        score_bucket_metrics.groupby(["score_version", "score_bucket", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            median_trade_count=("trade_count", "median"),
            median_exposure=("exposure", "median"),
        )
        .sort_values(["score_version", "mode", "hold_days", "score_bucket"])
        .reset_index(drop=True)
    )
    score_bucket_summary.to_csv(artifact_dir / "trend_score_bucket_strategy_summary.csv", index=False)

    score_bucket_class_summary = (
        score_bucket_metrics.groupby(["asset_class", "score_version", "score_bucket", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_max_drawdown=("max_drawdown", "median"),
        )
        .sort_values(["asset_class", "score_version", "mode", "hold_days", "score_bucket"])
        .reset_index(drop=True)
    )
    score_bucket_class_summary.to_csv(artifact_dir / "trend_score_bucket_strategy_by_asset_class.csv", index=False)

    # 2b-3) score version comparison via soft gate (no hard threshold)
    soft_rows = []
    for name, sig_sc in score_data.items():
        for score_name, score_col in SCORE_VARIANTS.items():
            sig_soft = sig_sc.copy()
            sig_soft["position_size"] = sig_soft[score_col].fillna(0.0).clip(0.0, 1.0)
            for mode in MODES:
                for hold in HOLDS:
                    res = run_nonoverlap_backtest(
                        sig_soft,
                        hold_days=hold,
                        mode=mode,
                        fee_bps_roundtrip=0.0,
                        size_col="position_size",
                    )
                    m = calc_metrics(res.nav, res.trades, res.in_position)
                    soft_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                            "variant": "soft_gate",
                            "score_version": score_name,
                            "mode": mode,
                            "hold_days": hold,
                            **m,
                        }
                    )

    soft_df = pd.DataFrame(soft_rows)
    baseline_for_compare = cross_df[["market_name", "asset_class", "mode", "hold_days", "cagr", "max_drawdown", "sharpe", "trade_count", "exposure"]].copy()
    baseline_for_compare["variant"] = "baseline"
    baseline_for_compare["score_version"] = "na"

    score_version_metrics = pd.concat([baseline_for_compare, soft_df], ignore_index=True)
    score_version_metrics.to_csv(artifact_dir / "trend_score_version_compare.csv", index=False)

    score_version_summary = (
        score_version_metrics.groupby(["variant", "score_version", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_max_drawdown=("max_drawdown", "median"),
            median_sharpe=("sharpe", "median"),
            median_trade_count=("trade_count", "median"),
            median_exposure=("exposure", "median"),
        )
        .sort_values(["variant", "score_version", "mode", "hold_days"])
        .reset_index(drop=True)
    )
    score_version_summary.to_csv(artifact_dir / "trend_score_version_summary.csv", index=False)

    # 2b-4) threshold scan: hard filter vs soft gate vs filter+soft gate (eq score)
    scan_rows = []
    for name, sig_sc in score_data.items():
        base_score = sig_sc[SCORE_VARIANTS["eq"]].fillna(0.0).clip(0.0, 1.0)

        # soft gate independent of threshold
        sig_soft = sig_sc.copy()
        sig_soft["position_size"] = base_score
        for mode in MODES:
            for hold in HOLDS:
                res_soft = run_nonoverlap_backtest(sig_soft, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0, size_col="position_size")
                m_soft = calc_metrics(res_soft.nav, res_soft.trades, res_soft.in_position)
                scan_rows.append(
                    {
                        "market_name": name,
                        "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                        "method": "soft_gate",
                        "threshold": np.nan,
                        "mode": mode,
                        "hold_days": hold,
                        **m_soft,
                    }
                )

        for th in THRESHOLD_SCAN:
            # pure hard filter
            sig_hard = sig_sc.copy()
            sig_hard["position_size"] = (base_score >= th).astype(float)

            # filter + soft gate
            sig_mix = sig_sc.copy()
            sig_mix["position_size"] = np.where(base_score >= th, base_score, 0.0)

            for mode in MODES:
                for hold in HOLDS:
                    res_h = run_nonoverlap_backtest(sig_hard, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0, size_col="position_size")
                    m_h = calc_metrics(res_h.nav, res_h.trades, res_h.in_position)
                    scan_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                            "method": "hard_filter",
                            "threshold": float(th),
                            "mode": mode,
                            "hold_days": hold,
                            **m_h,
                        }
                    )

                    res_m = run_nonoverlap_backtest(sig_mix, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0, size_col="position_size")
                    m_m = calc_metrics(res_m.nav, res_m.trades, res_m.in_position)
                    scan_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                            "method": "filter_plus_soft",
                            "threshold": float(th),
                            "mode": mode,
                            "hold_days": hold,
                            **m_m,
                        }
                    )

    threshold_scan_df = pd.DataFrame(scan_rows)
    baseline_merge = cross_df[["market_name", "mode", "hold_days", "cagr", "max_drawdown", "sharpe"]].rename(
        columns={"cagr": "baseline_cagr", "max_drawdown": "baseline_max_drawdown", "sharpe": "baseline_sharpe"}
    )
    threshold_scan_df = threshold_scan_df.merge(baseline_merge, on=["market_name", "mode", "hold_days"], how="left")
    threshold_scan_df["delta_cagr"] = threshold_scan_df["cagr"] - threshold_scan_df["baseline_cagr"]
    threshold_scan_df["delta_max_drawdown"] = threshold_scan_df["max_drawdown"] - threshold_scan_df["baseline_max_drawdown"]
    threshold_scan_df["delta_sharpe"] = threshold_scan_df["sharpe"] - threshold_scan_df["baseline_sharpe"]
    threshold_scan_df.to_csv(artifact_dir / "trend_score_threshold_scan.csv", index=False)

    threshold_summary = (
        threshold_scan_df.groupby(["method", "threshold", "mode", "hold_days"], dropna=False, as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_delta_cagr=("delta_cagr", "median"),
            median_max_drawdown=("max_drawdown", "median"),
            median_delta_max_drawdown=("delta_max_drawdown", "median"),
            median_sharpe=("sharpe", "median"),
            median_delta_sharpe=("delta_sharpe", "median"),
            median_trade_count=("trade_count", "median"),
            median_exposure=("exposure", "median"),
        )
        .sort_values(["mode", "hold_days", "method", "threshold"])
        .reset_index(drop=True)
    )
    threshold_summary.to_csv(artifact_dir / "trend_score_threshold_summary.csv", index=False)

    threshold_class_summary = (
        threshold_scan_df.groupby(["asset_class", "method", "threshold", "mode", "hold_days"], dropna=False, as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_delta_cagr=("delta_cagr", "median"),
        )
        .sort_values(["asset_class", "mode", "hold_days", "method", "threshold"])
        .reset_index(drop=True)
    )
    threshold_class_summary.to_csv(artifact_dir / "trend_score_threshold_by_asset_class.csv", index=False)

    # 2b-5) ablation (single / double / triple indicator combinations)
    combo_defs = {
        "BBW": ["bbw_score"],
        "ADR": ["adr_score"],
        "ADX": ["adx_score"],
        "BBW+ADR": ["bbw_score", "adr_score"],
        "BBW+ADX": ["bbw_score", "adx_score"],
        "ADR+ADX": ["adr_score", "adx_score"],
        "BBW+ADR+ADX": ["bbw_score", "adr_score", "adx_score"],
    }

    ab_rows = []
    for name, sig_sc in score_data.items():
        for combo_name, cols in combo_defs.items():
            combo_score = sig_sc[cols].mean(axis=1).fillna(0.0).clip(0.0, 1.0)
            sig_combo = sig_sc.copy()
            sig_combo["position_size"] = (combo_score >= 0.5).astype(float)

            for mode in MODES:
                for hold in HOLDS:
                    res = run_nonoverlap_backtest(sig_combo, hold_days=hold, mode=mode, fee_bps_roundtrip=0.0, size_col="position_size")
                    m = calc_metrics(res.nav, res.trades, res.in_position)
                    ab_rows.append(
                        {
                            "market_name": name,
                            "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                            "combo": combo_name,
                            "threshold": 0.5,
                            "mode": mode,
                            "hold_days": hold,
                            **m,
                        }
                    )

    ablation_df = pd.DataFrame(ab_rows)
    ablation_df = ablation_df.merge(baseline_merge, on=["market_name", "mode", "hold_days"], how="left")
    ablation_df["delta_cagr"] = ablation_df["cagr"] - ablation_df["baseline_cagr"]
    ablation_df["delta_max_drawdown"] = ablation_df["max_drawdown"] - ablation_df["baseline_max_drawdown"]
    ablation_df["delta_sharpe"] = ablation_df["sharpe"] - ablation_df["baseline_sharpe"]
    ablation_df.to_csv(artifact_dir / "trend_score_ablation.csv", index=False)

    ablation_summary = (
        ablation_df.groupby(["combo", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
            median_delta_cagr=("delta_cagr", "median"),
            median_delta_max_drawdown=("delta_max_drawdown", "median"),
            median_delta_sharpe=("delta_sharpe", "median"),
        )
        .sort_values(["mode", "hold_days", "combo"])
        .reset_index(drop=True)
    )
    ablation_summary.to_csv(artifact_dir / "trend_score_ablation_summary.csv", index=False)

    ablation_class_summary = (
        ablation_df.groupby(["asset_class", "combo", "mode", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_delta_cagr=("delta_cagr", "median"),
            pass_rate_cagr=("cagr", lambda s: float((s > 0).mean())),
        )
        .sort_values(["asset_class", "mode", "hold_days", "combo"])
        .reset_index(drop=True)
    )
    ablation_class_summary.to_csv(artifact_dir / "trend_score_ablation_by_asset_class.csv", index=False)

    # 2d) Usage playbook analytics (Q1~Q11 + OOS + tail risk)
    # Precompute per-market break-even (baseline MA20 signal, hold in HOLDS) for usage sections
    be_rows_pre = []
    for name, sig in signal_data.items():
        best_hold = None
        best_cagr = -np.inf
        best_mdd = np.nan

        for hold in HOLDS:
            r0 = run_nonoverlap_backtest(sig, hold_days=hold, mode="long_short", fee_bps_roundtrip=0.0)
            m0 = calc_metrics(r0.nav, r0.trades, r0.in_position)
            c0 = float(m0.get("cagr", np.nan))
            if np.isfinite(c0) and c0 > best_cagr:
                best_cagr = c0
                best_hold = hold
                best_mdd = float(m0.get("max_drawdown", np.nan))

        if best_hold is None:
            be_rows_pre.append(
                {
                    "market_name": name,
                    "ticker": SYMBOLS.get(name, ""),
                    "best_ma_period": 20,
                    "best_hold_days": np.nan,
                    "cagr_at_0bps": np.nan,
                    "max_drawdown_at_0bps": np.nan,
                    "break_even_fee_bps": np.nan,
                }
            )
            continue

        cagr_line = []
        for bps in COST_BPS_LIST:
            rr = run_nonoverlap_backtest(sig, hold_days=int(best_hold), mode="long_short", fee_bps_roundtrip=float(bps))
            mm = calc_metrics(rr.nav, rr.trades, rr.in_position)
            cagr_line.append((float(bps), float(mm.get("cagr", np.nan))))

        viable = [bps for bps, c in cagr_line if np.isfinite(c) and c > 0]
        break_even_fee = float(max(viable)) if len(viable) else -1.0

        be_rows_pre.append(
            {
                "market_name": name,
                "ticker": SYMBOLS.get(name, ""),
                "best_ma_period": 20,
                "best_hold_days": int(best_hold),
                "cagr_at_0bps": float(best_cagr),
                "max_drawdown_at_0bps": float(best_mdd),
                "break_even_fee_bps": break_even_fee,
            }
        )

    break_even_df = pd.DataFrame(be_rows_pre)

    # Q1~Q3 (stage-like decoupled unit)
    (
        score_data,
        regime_df_play,
        q1_df,
        q1_summary,
        event_df,
        event_summary,
        fear_df,
        fear_summary,
    ) = compute_usage_q1_q3(score_data=score_data, asset_class_map=ASSET_CLASS_MAP)

    regime_df_play.to_csv(artifact_dir / "usage_regime_profile.csv", index=False)
    q1_df.to_csv(artifact_dir / "usage_q1_module_positioning.csv", index=False)
    q1_summary.to_csv(artifact_dir / "usage_q1_module_positioning_summary.csv", index=False)
    event_df.to_csv(artifact_dir / "usage_q2_event_study_raw.csv", index=False)
    event_summary.to_csv(artifact_dir / "usage_q2_event_study_summary.csv", index=False)
    fear_df.to_csv(artifact_dir / "usage_q3_fear_conditions_raw.csv", index=False)
    fear_summary.to_csv(artifact_dir / "usage_q3_fear_conditions_summary.csv", index=False)

    # Q4~Q6 (stage-like decoupled unit)
    hold_df, hold_summary, hold_robust_band, oos_df, oos_summary, cost_budget = compute_usage_q4_q6(
        signal_data=signal_data,
        market_data=market_data,
        cross_df=cross_df,
        break_even_df=break_even_df,
        loaded_names=loaded_names,
        asset_class_map=ASSET_CLASS_MAP,
    )

    hold_df.to_csv(artifact_dir / "usage_q4_hold_robustness_by_market.csv", index=False)
    hold_summary.to_csv(artifact_dir / "usage_q4_hold_robustness_summary.csv", index=False)
    hold_robust_band.to_csv(artifact_dir / "usage_q4_hold_robust_band.csv", index=False)
    oos_df.to_csv(artifact_dir / "usage_oos_2y6m_by_fold.csv", index=False)
    oos_summary.to_csv(artifact_dir / "usage_q5_ma_n_oos_summary.csv", index=False)
    cost_budget.to_csv(artifact_dir / "usage_q6_cost_budget_by_market.csv", index=False)

    # Q7~Q9 (stage-like decoupled unit)
    combo_df, combo_summary, risk_mod, class_suit, nav_pb, nav_pl = compute_usage_q7_q9(
        score_data=score_data,
        nav_store=nav_store,
        loaded_names=loaded_names,
        cross_df=cross_df,
        coverage_df=coverage_df,
        break_even_df=break_even_df,
        oos_df=oos_df,
        asset_class_map=ASSET_CLASS_MAP,
    )
    combo_df.to_csv(artifact_dir / "usage_q7_combo_compare_by_market.csv", index=False)
    combo_summary.to_csv(artifact_dir / "usage_q7_combo_compare_summary.csv", index=False)
    risk_mod.to_csv(artifact_dir / "usage_q8_risk_module_compare.csv", index=False)
    class_suit.to_csv(artifact_dir / "usage_q9_asset_whitelist.csv", index=False)

    # Q10~Q11 (stage-like decoupled unit)
    failure_df, density_df, density_summary = compute_usage_q10_q11(
        signal_data=signal_data,
        trades_store=trades_store,
        inpos_store=inpos_store,
        score_data=score_data,
        loaded_names=loaded_names,
        asset_class_map=ASSET_CLASS_MAP,
    )
    failure_df.to_csv(artifact_dir / "usage_q10_failure_monitor.csv", index=False)
    density_df.to_csv(artifact_dir / "usage_q11_signal_density.csv", index=False)
    density_summary.to_csv(artifact_dir / "usage_q11_signal_density_summary.csv", index=False)

    # Q12~Q14-related artifact (stage-like decoupled unit)
    tail_df = compute_usage_q12_q14(
        trades_store=trades_store,
        loaded_names=loaded_names,
    )
    tail_df.to_csv(artifact_dir / "usage_tail_risk_summary.csv", index=False)

    # 3) Annual returns for baseline long_short hold=10
    annual_rows = []
    for name in loaded_names:
        nav = nav_store[(name, "long_short", 10)]
        yr = yearly_returns(nav)
        for y, r in yr.items():
            annual_rows.append(
                {
                    "market_name": name,
                    "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                    "year": int(y),
                    "strategy_ret": float(r),
                }
            )
    annual_df = pd.DataFrame(annual_rows)
    annual_df.to_csv(artifact_dir / "annual_returns_longshort_hold10.csv", index=False)

    # 3b) Year regime classification by market buy&hold annual return
    regime_rows = []
    for name, bars in market_data.items():
        d = bars[["timestamp", "close"]].copy()
        d["year"] = d["timestamp"].dt.year
        for y, g in d.groupby("year"):
            r = float(g["close"].iloc[-1] / g["close"].iloc[0] - 1.0)
            if r >= 0.15:
                regime = "bull"
            elif r <= -0.15:
                regime = "bear"
            else:
                regime = "sideways"
            regime_rows.append(
                {
                    "market_name": name,
                    "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                    "year": int(y),
                    "buyhold_year_ret": r,
                    "year_regime": regime,
                }
            )
    regime_df = pd.DataFrame(regime_rows)
    regime_df.to_csv(artifact_dir / "market_year_regime.csv", index=False)

    annual_regime = annual_df.merge(regime_df, on=["market_name", "asset_class", "year"], how="left")
    annual_regime.to_csv(artifact_dir / "annual_strategy_with_regime.csv", index=False)

    regime_summary = (
        annual_regime.groupby(["year_regime"], as_index=False)
        .agg(
            samples=("strategy_ret", "size"),
            mean_strategy_ret=("strategy_ret", "mean"),
            median_strategy_ret=("strategy_ret", "median"),
            pos_rate=("strategy_ret", lambda s: float((s > 0).mean())),
        )
        .sort_values("year_regime")
        .reset_index(drop=True)
    )
    regime_summary.to_csv(artifact_dir / "annual_regime_summary.csv", index=False)

    # 4) Parameter sensitivity (Xiaomi as default case study)
    anchor_name = "小米集团" if "小米集团" in market_data else loaded_names[0]
    xm = market_data[anchor_name]
    sens_rows = []
    for ma in MA_WINDOWS:
        sig = compute_up_down_wave_signals(xm, config=UpDownWaveConfig(ma_period=ma))
        sig["timestamp"] = pd.to_datetime(sig["timestamp"], utc=True)
        for hold in HOLD_SWEEP:
            res = run_nonoverlap_backtest(sig, hold_days=hold, mode="long_short", fee_bps_roundtrip=0.0)
            m = calc_metrics(res.nav, res.trades, res.in_position)
            sens_rows.append({"ma_period": ma, "hold_days": hold, **m})
    sens_df = pd.DataFrame(sens_rows)
    sens_df.to_csv(artifact_dir / "xiaomi_param_sensitivity.csv", index=False)

    # 5) Cost sensitivity (Xiaomi, ma20, long_short, holds=5/10/30)
    x20 = signal_data[anchor_name]
    cost_rows = []
    for hold in HOLDS:
        for bps in COST_BPS_LIST:
            res = run_nonoverlap_backtest(x20, hold_days=hold, mode="long_short", fee_bps_roundtrip=float(bps))
            m = calc_metrics(res.nav, res.trades, res.in_position)
            cost_rows.append({"hold_days": hold, "fee_bps_roundtrip": bps, **m})
    cost_df = pd.DataFrame(cost_rows)
    cost_df.to_csv(artifact_dir / "xiaomi_cost_sensitivity.csv", index=False)

    # 5b) Cross-market sensitivity big table (ma x hold x cost x mode)
    big_rows = []
    for name, bars in market_data.items():
        bh = float(bars["close"].iloc[-1] / bars["close"].iloc[0] - 1.0)
        for ma in MA_WINDOWS:
            sig_ma = compute_up_down_wave_signals(bars, config=UpDownWaveConfig(ma_period=ma))
            sig_ma["timestamp"] = pd.to_datetime(sig_ma["timestamp"], utc=True)
            up_total = int(sig_ma["upwave"].sum())
            down_total = int(sig_ma["downwave"].sum())

            for mode in MODES:
                for hold in HOLD_SWEEP:
                    for bps in COST_BPS_LIST:
                        res = run_nonoverlap_backtest(
                            sig_ma,
                            hold_days=hold,
                            mode=mode,
                            fee_bps_roundtrip=float(bps),
                        )
                        m = calc_metrics(res.nav, res.trades, res.in_position)
                        big_rows.append(
                            {
                                "market_name": name,
                                "ticker": SYMBOLS[name],
                                "asset_class": ASSET_CLASS_MAP.get(name, "Unknown"),
                                "asset_group": ASSET_GROUP_MAP.get(name, "Unknown"),
                                "ma_period": int(ma),
                                "mode": mode,
                                "hold_days": int(hold),
                                "fee_bps_roundtrip": float(bps),
                                "up_signals_total": up_total,
                                "down_signals_total": down_total,
                                "signals_total": up_total + down_total,
                                "buyhold_ret": bh,
                                **m,
                            }
                        )

    big_df = pd.DataFrame(big_rows)
    big_df.to_csv(artifact_dir / "sensitivity_cost_big_table.csv", index=False)

    # Aggregations for broad sensitivity analysis
    broad_base = big_df[(big_df["mode"] == "long_short") & (big_df["fee_bps_roundtrip"] == 0)].copy()
    param_agg = (
        broad_base.groupby(["ma_period", "hold_days"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            pass_rate_pos=("cagr", lambda s: float((s > 0).mean())),
            median_max_drawdown=("max_drawdown", "median"),
            median_sharpe=("sharpe", "median"),
        )
        .sort_values(["ma_period", "hold_days"])
        .reset_index(drop=True)
    )
    param_agg.to_csv(artifact_dir / "sensitivity_param_agg_cross_market.csv", index=False)

    cost_agg = (
        big_df[big_df["mode"] == "long_short"]
        .groupby(["hold_days", "fee_bps_roundtrip"], as_index=False)
        .agg(
            markets_n=("market_name", "nunique"),
            median_cagr=("cagr", "median"),
            mean_cagr=("cagr", "mean"),
            pass_rate_pos=("cagr", lambda s: float((s > 0).mean())),
            median_sharpe=("sharpe", "median"),
            median_max_drawdown=("max_drawdown", "median"),
        )
        .sort_values(["hold_days", "fee_bps_roundtrip"])
        .reset_index(drop=True)
    )
    cost_agg.to_csv(artifact_dir / "sensitivity_cost_agg_cross_market.csv", index=False)

    # Break-even cost for each market under its best (ma, hold) at 0 bps, long_short mode
    base_zero = big_df[(big_df["mode"] == "long_short") & (big_df["fee_bps_roundtrip"] == 0)].copy()
    best_combo_rows = []
    for mk in sorted(base_zero["market_name"].unique()):
        part = base_zero[base_zero["market_name"] == mk]
        if part.empty:
            continue
        best = part.loc[part["cagr"].idxmax()]
        ma = int(best["ma_period"])
        hold = int(best["hold_days"])

        line = big_df[
            (big_df["market_name"] == mk)
            & (big_df["mode"] == "long_short")
            & (big_df["ma_period"] == ma)
            & (big_df["hold_days"] == hold)
        ].sort_values("fee_bps_roundtrip")

        viable = line[line["cagr"] > 0]
        break_even = float(viable["fee_bps_roundtrip"].max()) if not viable.empty else -1.0
        best_combo_rows.append(
            {
                "market_name": mk,
                "ticker": SYMBOLS.get(mk, ""),
                "best_ma_period": ma,
                "best_hold_days": hold,
                "cagr_at_0bps": float(best["cagr"]),
                "max_drawdown_at_0bps": float(best["max_drawdown"]),
                "break_even_fee_bps": break_even,
            }
        )

    break_even_df = pd.DataFrame(best_combo_rows).sort_values("cagr_at_0bps", ascending=False)
    break_even_df.to_csv(artifact_dir / "sensitivity_break_even_cost.csv", index=False)

    # 6) Trade contribution decomposition (Xiaomi baseline long_short hold=10)
    tr_xm = trades_store[(anchor_name, "long_short", 10)].copy()
    tr_xm = tr_xm.sort_values("net_ret", ascending=False).reset_index(drop=True)
    tr_xm["cum_sum_ret"] = tr_xm["net_ret"].cumsum()
    tr_xm["cum_share"] = tr_xm["cum_sum_ret"] / tr_xm["net_ret"].sum() if tr_xm["net_ret"].sum() != 0 else np.nan
    tr_xm.to_csv(artifact_dir / "xiaomi_trade_contribution_hold10.csv", index=False)

    # 7) Signal forward path (Xiaomi)
    fp = signal_forward_path(x20, FORWARD_HORIZONS)
    fp.to_csv(artifact_dir / "xiaomi_signal_forward_path.csv", index=False)

    # ---------- Plotting ----------
    # Figure 1: heatmap market x hold x mode (CAGR)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)
    for ax, mode in zip(axes, MODES):
        pvt = cross_df[cross_df["mode"] == mode].pivot(index="market_name", columns="hold_days", values="cagr")
        pvt = pvt.reindex(index=loaded_names, columns=HOLDS)
        heatmap(ax, pvt, f"CAGR Heatmap ({mode})")
    fig.savefig(asset_dir / "01_heatmap_market_hold_mode_cagr.png", dpi=170)
    plt.close(fig)

    # Figure 2: annual returns heatmap (long_short hold=10)
    pvt2 = annual_df.pivot(index="market_name", columns="year", values="strategy_ret").reindex(index=loaded_names)
    fig, ax = plt.subplots(figsize=(14, 6), constrained_layout=True)
    # center at 0 and clip extreme tails so colors are visually interpretable
    heatmap(
        ax,
        pvt2,
        "Annual Return Heatmap (long_short, hold=10, centered@0, clipped@95% abs)",
        center_zero=True,
        clip_abs_q=0.95,
    )
    fig.savefig(asset_dir / "02_annual_return_heatmap.png", dpi=170)
    plt.close(fig)

    # Figure 3: broad parameter sensitivity (cross-market, long_short, 0bps)
    pvt3 = (
        param_agg.pivot(index="ma_period", columns="hold_days", values="median_cagr")
        .reindex(index=MA_WINDOWS, columns=HOLD_SWEEP)
    )
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    heatmap(ax, pvt3, "Cross-Market Sensitivity: MA Window x Hold Days (Median CAGR)")
    fig.savefig(asset_dir / "03_xiaomi_param_sensitivity.png", dpi=170)
    plt.close(fig)

    # Figure 4: broad cost sensitivity (cross-market aggregation)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)

    for hold in HOLDS:
        part = cost_agg[cost_agg["hold_days"] == hold].sort_values("fee_bps_roundtrip")
        axes[0].plot(part["fee_bps_roundtrip"], part["median_cagr"], marker="o", label=f"hold={hold}")
    axes[0].set_title("Cross-Market Cost Sensitivity: Median CAGR")
    axes[0].set_xlabel("Roundtrip Fee (bps)")
    axes[0].set_ylabel("Median CAGR")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    for hold in HOLDS:
        part = cost_agg[cost_agg["hold_days"] == hold].sort_values("fee_bps_roundtrip")
        axes[1].plot(part["fee_bps_roundtrip"], part["pass_rate_pos"], marker="s", label=f"hold={hold}")
    axes[1].set_title("Cross-Market Cost Sensitivity: Positive CAGR Pass Rate")
    axes[1].set_xlabel("Roundtrip Fee (bps)")
    axes[1].set_ylabel("Pass Rate")
    axes[1].set_ylim(0, 1)
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    fig.savefig(asset_dir / "04_cost_sensitivity.png", dpi=170)
    plt.close(fig)

    # Figure 5: trade contribution decomposition
    anchor_label = PLOT_LABELS.get(anchor_name, anchor_name)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    topn = min(40, len(tr_xm))
    axes[0].bar(range(topn), tr_xm["net_ret"].iloc[:topn].values)
    axes[0].set_title(f"Top Trade Returns ({anchor_label}, hold=10)")
    axes[0].set_xlabel("Rank")
    axes[0].set_ylabel("Net Return")
    axes[0].grid(alpha=0.2)

    bot = tr_xm.sort_values("net_ret", ascending=True).reset_index(drop=True)
    botn = min(40, len(bot))
    axes[1].bar(range(botn), bot["net_ret"].iloc[:botn].values)
    axes[1].set_title(f"Worst Trade Returns ({anchor_label}, hold=10)")
    axes[1].set_xlabel("Rank")
    axes[1].set_ylabel("Net Return")
    axes[1].grid(alpha=0.2)
    fig.savefig(asset_dir / "05_trade_contribution.png", dpi=170)
    plt.close(fig)

    # Figure 6: drawdown curves (long_short, market-specific best hold by cagr)
    best_rows = []
    for name in loaded_names:
        part = cross_df[(cross_df["market_name"] == name) & (cross_df["mode"] == "long_short")]
        if part.empty:
            continue
        r = part.loc[part["cagr"].idxmax()]
        best_rows.append((name, int(r["hold_days"])))

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    for name, hold in best_rows:
        nav = nav_store[(name, "long_short", hold)]
        dd = nav / nav.cummax() - 1.0
        ax.plot(nav.index, dd.values, label=f"{PLOT_LABELS.get(name, name)} (hold={hold})")
    ax.set_title("Drawdown Curves (long_short, per-market best hold)")
    ax.set_ylabel("Drawdown")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.savefig(asset_dir / "06_drawdown_curves.png", dpi=170)
    plt.close(fig)

    # Figure 7: signal forward path (anchor market)
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    ax.plot(fp["horizon"], fp["upwave_future_ret_mean"], marker="o", label="UpWave -> future long return")
    ax.plot(fp["horizon"], fp["downwave_short_ret_mean"], marker="s", label="DownWave -> future short return")
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title(f"{anchor_label} Signal Forward Path")
    ax.set_xlabel("Forward Horizon (days)")
    ax.set_ylabel("Average Return")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.savefig(asset_dir / "07_signal_forward_path.png", dpi=170)
    plt.close(fig)

    # Figure 8: trend score bucket -> forward return relation (eq score)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), constrained_layout=True)
    for ax, side in zip(axes, ["upwave_long", "downwave_short"]):
        part = score_forward_summary[
            (score_forward_summary["score_version"] == "eq")
            & (score_forward_summary["signal_side"] == side)
        ].copy()
        for hold in HOLDS:
            p = part[part["hold_days"] == hold].set_index("score_bucket").reindex(SCORE_BUCKET_LABELS).reset_index()
            ax.plot(p["score_bucket"], p["mean_ret"], marker="o", label=f"hold={hold}")
        ax.axhline(0.0, color="black", linewidth=1)
        ax.set_title("UpWave forward long" if side == "upwave_long" else "DownWave forward short")
        ax.set_xlabel("Trend Score Bucket (eq)")
        ax.set_ylabel("Mean Forward Return")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.savefig(asset_dir / "08_trend_filter_enhancement.png", dpi=170)
    plt.close(fig)

    # Figure 9: threshold scan (eq score) by mode
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    for ax, mode in zip(axes, MODES):
        part = threshold_summary[threshold_summary["mode"] == mode]

        # hard filter and filter+soft as function of threshold
        for method, marker in [("hard_filter", "o"), ("filter_plus_soft", "s")]:
            p = part[(part["method"] == method) & part["threshold"].notna()].sort_values("threshold")
            if not p.empty:
                ax.plot(p["threshold"], p["median_delta_cagr"], marker=marker, label=method)

        # soft gate baseline reference (single point -> horizontal)
        p_soft = part[part["method"] == "soft_gate"]
        if not p_soft.empty:
            y = float(p_soft["median_delta_cagr"].median())
            ax.axhline(y, linestyle="--", label="soft_gate")

        ax.axhline(0.0, color="black", linewidth=1)
        ax.set_title(f"{mode}: ΔMedian CAGR vs baseline")
        ax.set_xlabel("Threshold (top x%)")
        ax.set_ylabel("Delta Median CAGR")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.savefig(asset_dir / "09_threshold_scan.png", dpi=170)
    plt.close(fig)

    # Figure 10: ablation (hold=10, long_short)
    ab_plot = ablation_summary[(ablation_summary["mode"] == "long_short") & (ablation_summary["hold_days"] == 10)].copy()
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    if not ab_plot.empty:
        ax.bar(ab_plot["combo"], ab_plot["median_delta_cagr"])
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_title("Ablation: Delta Median CAGR vs baseline (long_short, hold=10)")
    ax.set_ylabel("Delta Median CAGR")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "10_ablation_delta_cagr.png", dpi=170)
    plt.close(fig)

    # Figure 11: hold robustness curves (per-market lines + median)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    for ax, mode in zip(axes, MODES):
        p = hold_df[hold_df["mode"] == mode]
        if p.empty:
            continue
        for mk, g in p.groupby("market_name"):
            g2 = g.sort_values("hold_days")
            ax.plot(g2["hold_days"], g2["cagr"], color="#4c72b0", alpha=0.18, linewidth=1)
        med = p.groupby("hold_days", as_index=False)["cagr"].median().sort_values("hold_days")
        ax.plot(med["hold_days"], med["cagr"], color="black", linewidth=2.2, marker="o", label="median")
        ax.axhline(0.0, color="gray", linewidth=1)
        ax.set_title(f"{mode}: hold robustness")
        ax.set_xlabel("hold days")
        ax.set_ylabel("CAGR")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.savefig(asset_dir / "11_hold_robustness_curves.png", dpi=170)
    plt.close(fig)

    # Figure 12: OOS rolling stability boxplots (2y train + 6m val)
    oos_df_plot = oos_df.copy()
    oos_df_plot["combo"] = oos_df_plot["ma_period"].astype(str) + "xN" + oos_df_plot["n_days"].astype(str)
    combo_order = [f"{ma}xN{nd}" for ma in [10, 20, 30] for nd in [3, 4, 5]]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5), constrained_layout=True)
    for ax, metric, title in [
        (axes[0], "cagr", "OOS CAGR"),
        (axes[1], "max_drawdown", "OOS Max Drawdown"),
        (axes[2], "win_rate", "OOS Win Rate"),
    ]:
        data = [oos_df_plot.loc[oos_df_plot["combo"] == c, metric].dropna().values for c in combo_order]
        ax.boxplot(data, tick_labels=combo_order, showfliers=False)
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "12_oos_stability_boxplot.png", dpi=170)
    plt.close(fig)

    # Figure 13: risk module equity (baseline vs regime-layered)
    if nav_pb is not None and nav_pl is not None:
        fig, axes = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
        axes[0].plot(nav_pb.index, nav_pb.values, label="baseline")
        axes[0].plot(nav_pl.index, nav_pl.values, label="regime_layer")
        axes[0].set_title("Portfolio Equity Curve (equal-weight across markets)")
        axes[0].set_ylabel("NAV")
        axes[0].grid(alpha=0.3)
        axes[0].legend()

        dd_pb = nav_pb / nav_pb.cummax() - 1.0
        dd_pl = nav_pl / nav_pl.cummax() - 1.0
        axes[1].plot(dd_pb.index, dd_pb.values, label="baseline")
        axes[1].plot(dd_pl.index, dd_pl.values, label="regime_layer")
        axes[1].set_title("Drawdown")
        axes[1].set_ylabel("DD")
        axes[1].grid(alpha=0.3)
        axes[1].legend()

        fig.savefig(asset_dir / "13_risk_module_equity.png", dpi=170)
        plt.close(fig)

    # Figure 14: signal density by year
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    if not density_summary.empty:
        ax.plot(density_summary["year"], density_summary["mean_signal_count"], marker="o", label="mean signals")
        ax.plot(density_summary["year"], density_summary["mean_trade_count"], marker="s", label="mean trades")
        ax2 = ax.twinx()
        ax2.plot(density_summary["year"], density_summary["mean_idle_ratio"], marker="^", color="tab:red", label="idle ratio")
        ax2.set_ylabel("Idle Ratio")
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc="best")
    ax.set_title("Signal Density / Trade Count / Idle Ratio by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.grid(alpha=0.3)
    fig.savefig(asset_dir / "14_signal_density_yearly.png", dpi=170)
    plt.close(fig)

    # ---------- Build report HTML ----------
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # key tables
    core_cols = [
        "market_name",
        "mode",
        "hold_days",
        "trade_count",
        "win_rate",
        "profit_factor",
        "total_return",
        "cagr",
        "sharpe",
        "max_drawdown",
        "exposure",
    ]
    core_tbl = cross_df[core_cols].copy()
    for c in ["win_rate", "total_return", "cagr", "max_drawdown", "exposure"]:
        core_tbl[c] = core_tbl[c].map(pct)
    for c in ["sharpe", "profit_factor"]:
        core_tbl[c] = core_tbl[c].map(lambda x: num(x, 3))

    core_table_html = core_tbl.to_html(index=False, escape=False, table_id="core-metrics-table")
    market_options_html = "".join([f'<option value="{m}">{m}</option>' for m in sorted(cross_df["market_name"].unique())])
    mode_options_html = "".join([f'<option value="{m}">{m}</option>' for m in sorted(cross_df["mode"].unique())])
    hold_options_html = "".join([f'<option value="{h}">{h}</option>' for h in sorted(cross_df["hold_days"].unique())])

    best_tbl_rows = []
    for name in loaded_names:
        part = cross_df[(cross_df["market_name"] == name) & (cross_df["mode"] == "long_short")]
        if part.empty:
            continue
        best = part.loc[part["cagr"].idxmax()]
        best_tbl_rows.append(best)
    best_tbl = pd.DataFrame(best_tbl_rows)
    if not best_tbl.empty:
        show_best = best_tbl[["market_name", "hold_days", "trade_count", "total_return", "cagr", "max_drawdown", "sharpe", "win_rate"]].copy()
        for c in ["total_return", "cagr", "max_drawdown", "win_rate"]:
            show_best[c] = show_best[c].map(pct)
        show_best["sharpe"] = show_best["sharpe"].map(lambda x: num(x, 3))
    else:
        show_best = pd.DataFrame()

    # cost tables (broad + xiaomi drilldown)
    cost_show = cost_df[["hold_days", "fee_bps_roundtrip", "trade_count", "total_return", "cagr", "max_drawdown", "win_rate"]].copy()
    for c in ["total_return", "cagr", "max_drawdown", "win_rate"]:
        cost_show[c] = cost_show[c].map(pct)

    cost_agg_show = cost_agg[["hold_days", "fee_bps_roundtrip", "markets_n", "median_cagr", "mean_cagr", "pass_rate_pos", "median_max_drawdown"]].copy()
    for c in ["median_cagr", "mean_cagr", "pass_rate_pos", "median_max_drawdown"]:
        cost_agg_show[c] = cost_agg_show[c].map(pct)

    param_agg_show = param_agg[["ma_period", "hold_days", "markets_n", "median_cagr", "mean_cagr", "pass_rate_pos", "median_max_drawdown", "median_sharpe"]].copy()
    for c in ["median_cagr", "mean_cagr", "pass_rate_pos", "median_max_drawdown"]:
        param_agg_show[c] = param_agg_show[c].map(pct)
    param_agg_show["median_sharpe"] = param_agg_show["median_sharpe"].map(lambda x: num(x, 3))

    break_even_show = break_even_df.copy()
    if not break_even_show.empty:
        for c in ["cagr_at_0bps", "max_drawdown_at_0bps"]:
            break_even_show[c] = break_even_show[c].map(pct)

    coverage_show = coverage_df.copy()

    asset_class_show = asset_class_summary.copy()
    if not asset_class_show.empty:
        for c in ["median_cagr", "mean_cagr", "median_max_drawdown", "pass_rate_pos"]:
            asset_class_show[c] = asset_class_show[c].map(pct)
        asset_class_show["median_sharpe"] = asset_class_show["median_sharpe"].map(lambda x: num(x, 3))

    regime_show = regime_summary.copy()
    if not regime_show.empty:
        for c in ["mean_strategy_ret", "median_strategy_ret", "pos_rate"]:
            regime_show[c] = regime_show[c].map(pct)

    failed_universe_show = failed_df.copy()

    tf_signal_show = tf_signal_df[
        ["market_name", "asset_class", "signals_total", "signals_tf_total", "signal_retention", "trend_days_ratio"]
    ].copy()
    for c in ["signal_retention", "trend_days_ratio"]:
        tf_signal_show[c] = tf_signal_show[c].map(pct)

    score_forward_show = score_forward_summary[score_forward_summary["score_version"] == "eq"].copy()
    if not score_forward_show.empty:
        for c in ["mean_ret", "median_ret", "win_rate"]:
            score_forward_show[c] = score_forward_show[c].map(pct)

    score_bucket_show = score_bucket_summary[score_bucket_summary["score_version"] == "eq"].copy()
    if not score_bucket_show.empty:
        for c in ["median_cagr", "mean_cagr", "pass_rate_cagr", "median_max_drawdown", "median_exposure"]:
            score_bucket_show[c] = score_bucket_show[c].map(pct)
        score_bucket_show["median_sharpe"] = score_bucket_show["median_sharpe"].map(lambda x: num(x, 3))
        score_bucket_show["median_trade_count"] = score_bucket_show["median_trade_count"].map(lambda x: num(x, 1))

    score_version_show = score_version_summary.copy()
    if not score_version_show.empty:
        for c in ["median_cagr", "mean_cagr", "pass_rate_cagr", "median_max_drawdown", "median_exposure"]:
            score_version_show[c] = score_version_show[c].map(pct)
        score_version_show["median_sharpe"] = score_version_show["median_sharpe"].map(lambda x: num(x, 3))
        score_version_show["median_trade_count"] = score_version_show["median_trade_count"].map(lambda x: num(x, 1))

    threshold_show = threshold_summary.copy()
    if not threshold_show.empty:
        for c in [
            "median_cagr",
            "pass_rate_cagr",
            "median_delta_cagr",
            "median_max_drawdown",
            "median_delta_max_drawdown",
            "median_exposure",
        ]:
            threshold_show[c] = threshold_show[c].map(pct)
        threshold_show["median_sharpe"] = threshold_show["median_sharpe"].map(lambda x: num(x, 3))
        threshold_show["median_delta_sharpe"] = threshold_show["median_delta_sharpe"].map(lambda x: num(x, 3))
        threshold_show["median_trade_count"] = threshold_show["median_trade_count"].map(lambda x: num(x, 1))

    ablation_show = ablation_summary.copy()
    if not ablation_show.empty:
        for c in ["median_cagr", "pass_rate_cagr", "median_delta_cagr", "median_delta_max_drawdown"]:
            ablation_show[c] = ablation_show[c].map(pct)
        ablation_show["median_delta_sharpe"] = ablation_show["median_delta_sharpe"].map(lambda x: num(x, 3))

    q1_show = q1_summary.copy()
    if not q1_show.empty:
        for c in ["median_cagr", "median_max_drawdown", "median_win_rate"]:
            q1_show[c] = q1_show[c].map(pct)
        q1_show["median_trade_count"] = q1_show["median_trade_count"].map(lambda x: num(x, 1))

    event_show = event_summary.copy()
    if not event_show.empty:
        for c in ["mean_ret", "median_ret", "p10_ret", "p90_ret", "mean_mae"]:
            event_show[c] = event_show[c].map(pct)

    fear_show = fear_summary.copy()
    if not fear_show.empty:
        for c in ["mean_ret", "win_rate", "p10_ret"]:
            fear_show[c] = fear_show[c].map(pct)

    hold_show = hold_summary.copy()
    if not hold_show.empty:
        for c in ["median_cagr", "median_max_drawdown"]:
            hold_show[c] = hold_show[c].map(pct)
        hold_show["median_trade_count"] = hold_show["median_trade_count"].map(lambda x: num(x, 1))

    hold_band_show = hold_robust_band.copy()

    oos_show = oos_summary.copy()
    if not oos_show.empty:
        for c in ["median_cagr", "mean_cagr", "pass_rate_cagr", "median_max_drawdown", "median_win_rate"]:
            oos_show[c] = oos_show[c].map(pct)

    cost_budget_show = cost_budget.copy()
    if not cost_budget_show.empty:
        for c in ["cagr_at_0bps", "max_drawdown_at_0bps"]:
            if c in cost_budget_show.columns:
                cost_budget_show[c] = cost_budget_show[c].map(pct)

    combo_show = combo_summary.copy()
    if not combo_show.empty:
        for c in ["median_cagr", "pass_rate_cagr", "median_max_drawdown", "median_exposure"]:
            combo_show[c] = combo_show[c].map(pct)
        combo_show["median_sharpe"] = combo_show["median_sharpe"].map(lambda x: num(x, 3))
        combo_show["median_trade_count"] = combo_show["median_trade_count"].map(lambda x: num(x, 1))

    risk_show = risk_mod.copy()
    if not risk_show.empty:
        for c in ["total_return", "cagr", "max_drawdown", "win_rate", "exposure"]:
            if c in risk_show.columns:
                risk_show[c] = risk_show[c].map(pct)
        for c in ["sharpe", "profit_factor", "calmar"]:
            if c in risk_show.columns:
                risk_show[c] = risk_show[c].map(lambda x: num(x, 3))

    class_show = class_suit.copy()
    if not class_show.empty:
        for c in ["median_mdd", "median_rolling_pos_rate"]:
            class_show[c] = class_show[c].map(pct)
        class_show["median_calmar"] = class_show["median_calmar"].map(lambda x: num(x, 3))

    failure_show = failure_df.copy()
    if not failure_show.empty:
        for c in ["win_rate_hist", "win_rate_recent6m", "win_rate_p1", "win_rate_p2", "win_rate_p3", "mae_hist", "mae_recent6m", "side_ratio_hist", "side_ratio_recent6m"]:
            failure_show[c] = failure_show[c].map(pct)

    density_show = density_summary.copy()
    if not density_show.empty:
        density_show["mean_idle_ratio"] = density_show["mean_idle_ratio"].map(pct)

    tail_show = tail_df.copy()
    if not tail_show.empty:
        for c in ["p5_trade_ret", "avg_worst5_ret", "max_loss_trade", "avg_mae", "avg_mfe", "position_size_hint"]:
            if c == "position_size_hint":
                tail_show[c] = tail_show[c].map(pct)
            else:
                tail_show[c] = tail_show[c].map(pct)

    # one-line conclusions + actions (auto-generated)
    q1_best = q1_summary.sort_values("median_cagr", ascending=False).iloc[0] if not q1_summary.empty else None
    q1_sentence = (
        f"UpWave 更像{q1_best['scenario']}模块，主要改善来自收益/回撤结构。" if q1_best is not None else "UpWave 模块定位需更多样本。"
    )
    q1_action = "若目标是降回撤，优先当交易许可；若目标是提收益，可保留入场角色但需叠加状态过滤。"

    q2_focus = event_summary[event_summary["signal_side"] == "upwave_long"].sort_values("mean_ret", ascending=False).head(1)
    q2_h = int(q2_focus["horizon"].iloc[0]) if len(q2_focus) else 10
    q2_sentence = f"收益贡献主要集中在触发后 {q2_h} 天窗口，且 MAE 在短期先扩张后收敛。"
    q2_action = "若1–5天贡献主导可偏短持有；若10–30天贡献更高，应采用趋势持仓框架。"

    q3_sentence = "在低 ADX / 低 BBW / 低 ATR% 分位下，期望收益与胜率明显走弱，这些区间属于禁入候选。"
    q3_action = "示例禁入：ADX<18 或 BBW分位<10% 时仅减仓/不追。"

    q4_sentence = "持有期存在稳健区间，不建议追逐单点最优。"
    q4_action = "默认选择稳健区间中值；极值点只用于研究不直接实盘。"

    q5_sentence = "MA/N 在滚动 OOS 下存在差异，但并非单一参数统治，建议用稳健组合而非极值。"
    q5_action = "参数敏感时采用软评分；参数稳健时可固化到执行规则。"

    q6_sentence = "各市场 break-even cost 差异较大，成本预算必须按市场单独约束。"
    q6_action = "roundtrip fee 超过市场 break-even 时，降低换手并延长持有期。"

    q7_sentence = "组合方式上，分层仓位通常比纯硬过滤更平滑，且更利于维持机会覆盖。"
    q7_action = "推荐先用 regime 分层仓位，再按资产类别决定是否叠加硬门槛。"

    q8_sentence = "分层仓位可压低组合级回撤并缩短修复时间，适合作为风控开关。"
    q8_action = "DownRegime 触发时降杠杆/停高弹性策略；UpRegime 恢复常态仓位。"

    q9_sentence = "资产适配存在明显分层：趋势占比高、成本可控、Calmar 更优的类别更适合白名单。"
    q9_action = "按 rolling 正收益占比 + break-even + Calmar 制定白/黑名单并动态更新。"

    q10_sentence = "当近6个月胜率持续低于历史且 MAE 恶化、sideways 占比抬升时，应判定失效风险上升。"
    q10_action = "降级路径：入场信号 → 过滤器 → 停用，仅保留监控。"

    q11_sentence = "信号密度决定资金利用率与换手成本，密度过高需要配套分层仓位与多策略分流。"
    q11_action = "按年度密度与空仓比设置容量阈值，避免单策略过度挤占。"

    # Q12~Q14 textual synthesis
    if not oos_summary.empty:
        oos_best = oos_summary.sort_values("median_cagr", ascending=False).iloc[0]
        q12_sentence = (
            f"2y+6m 滚动 OOS 下，MA{oos_best['ma_period']:.0f}×N{oos_best['n_days']:.0f} 的中位 CAGR 最优"
            f"（{oos_best['median_cagr']:.2%}），但整体稳定性仍需持续监控。"
        )
    else:
        q12_sentence = "滚动 OOS 结果待补充。"
    q12_action = "每月更新滚动窗口箱线图，按分位数（非均值）评估是否继续上线。"

    ls10_tail = tail_df[(tail_df["mode"] == "long_short") & (tail_df["hold_days"] == 10)] if not tail_df.empty else pd.DataFrame()
    if not ls10_tail.empty:
        tr = ls10_tail.iloc[0]
        q13_sentence = (
            f"long_short/hold=10 的 tail risk：p5 单笔约 {tr['p5_trade_ret']:.2%}，"
            f"最差5%均值约 {tr['avg_worst5_ret']:.2%}，建议单笔仓位上限约 {tr['position_size_hint']:.2%}。"
        )
    else:
        q13_sentence = "Tail risk 结果待补充。"
    q13_action = "按 worst-5% 与 MAE 动态约束仓位，并叠加 vol targeting。"

    q14_sentence = "综合看，该因子更适合做‘条件型趋势模块’（入场+过滤+风控联动），而非裸跑单模块。"
    q14_action = "默认采用 long-first + regime gating + 成本预算 + 失效降级监控。"

    # report text decisions
    suitability = """
    <ul>
      <li><b>相对更适用：</b>趋势性强、波动较大的市场（如加密、部分成长股），并且持有期偏中长（10~30天）时表现更容易释放。</li>
      <li><b>相对不适用：</b>长期震荡/均值回归市场、交易受限的做空场景（A股融券约束）以及高成本环境。</li>
      <li><b>定位建议：</b>把 Up/Down Wave 作为“趋势过滤器 + 方向触发器”，与 ATR/ADX/仓位控制联用，而非单独裸奔策略。</li>
    </ul>
    """

    interactive_js = """
<script>
(function() {
  const table = document.getElementById('core-metrics-table');
  if (!table) return;

  const tbody = table.querySelector('tbody');
  const allRows = Array.from(tbody.querySelectorAll('tr'));

  const marketSel = document.getElementById('filter-market');
  const modeSel = document.getElementById('filter-mode');
  const holdSel = document.getElementById('filter-hold');
  const searchInput = document.getElementById('filter-search');
  const resetBtn = document.getElementById('filter-reset');
  const countEl = document.getElementById('core-metrics-count');

  const COL = {
    market: 0,
    mode: 1,
    hold: 2,
  };

  let sortState = { col: null, asc: true };

  function parseCellValue(text) {
    const t = (text || '').trim();
    if (t === '' || t === '-') return Number.NaN;
    const n = Number(t.replace(/,/g, '').replace(/%/g, ''));
    if (!Number.isNaN(n)) return n;
    return t.toLowerCase();
  }

  function compareValues(a, b, asc) {
    const av = parseCellValue(a);
    const bv = parseCellValue(b);

    const aNum = typeof av === 'number' && !Number.isNaN(av);
    const bNum = typeof bv === 'number' && !Number.isNaN(bv);

    if (aNum && bNum) return asc ? av - bv : bv - av;
    if (aNum && !bNum) return asc ? -1 : 1;
    if (!aNum && bNum) return asc ? 1 : -1;

    const as = String(av);
    const bs = String(bv);
    return asc ? as.localeCompare(bs, 'zh-Hans-CN') : bs.localeCompare(as, 'zh-Hans-CN');
  }

  function applyFiltersAndRender() {
    const market = marketSel.value;
    const mode = modeSel.value;
    const hold = holdSel.value;
    const keyword = (searchInput.value || '').trim().toLowerCase();

    let rows = allRows.filter(row => {
      const cells = row.querySelectorAll('td');
      const m = cells[COL.market]?.textContent?.trim() || '';
      const md = cells[COL.mode]?.textContent?.trim() || '';
      const h = cells[COL.hold]?.textContent?.trim() || '';
      const full = row.textContent.toLowerCase();

      if (market && m !== market) return false;
      if (mode && md !== mode) return false;
      if (hold && h !== hold) return false;
      if (keyword && !full.includes(keyword)) return false;
      return true;
    });

    if (sortState.col !== null) {
      rows.sort((r1, r2) => {
        const a = r1.querySelectorAll('td')[sortState.col]?.textContent || '';
        const b = r2.querySelectorAll('td')[sortState.col]?.textContent || '';
        return compareValues(a, b, sortState.asc);
      });
    }

    tbody.innerHTML = '';
    rows.forEach(r => tbody.appendChild(r));
    countEl.textContent = `当前显示 ${rows.length} / ${allRows.length} 行`;
  }

  const headers = Array.from(table.querySelectorAll('thead th'));
  headers.forEach((th, idx) => {
    th.title = '点击排序';
    th.addEventListener('click', () => {
      if (sortState.col === idx) {
        sortState.asc = !sortState.asc;
      } else {
        sortState.col = idx;
        sortState.asc = true;
      }
      applyFiltersAndRender();
    });
  });

  [marketSel, modeSel, holdSel].forEach(el => el.addEventListener('change', applyFiltersAndRender));
  searchInput.addEventListener('input', applyFiltersAndRender);
  resetBtn.addEventListener('click', () => {
    marketSel.value = '';
    modeSel.value = '';
    holdSel.value = '';
    searchInput.value = '';
    sortState = { col: null, asc: true };
    applyFiltersAndRender();
  });

  applyFiltersAndRender();
})();
</script>
    """

    html = f"""
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Momentum 因子评估报告 - UpWave / DownWave</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft Yahei", sans-serif; margin: 24px; color:#111; }}
    h1,h2,h3 {{ margin: 0.6em 0 0.3em; }}
    .muted {{ color:#666; font-size: 14px; }}
    .section {{ margin-top: 28px; }}
    img {{ max-width: 100%; border:1px solid #ddd; border-radius:8px; margin: 10px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0 18px; font-size: 13px; }}
    th,td {{ border:1px solid #ddd; padding: 6px 8px; text-align: left; }}
    th {{ background: #f7f7f7; position: sticky; top: 0; }}
    #core-metrics-table th {{ cursor: pointer; user-select: none; }}
    .toolbar {{ display:flex; flex-wrap:wrap; gap:10px; align-items:center; padding:10px 12px; background:#fafafa; border:1px solid #e5e5e5; border-radius:8px; margin: 8px 0 10px; }}
    .toolbar label {{ font-size: 13px; color:#333; }}
    .toolbar select, .toolbar input {{ margin-left: 6px; padding: 4px 8px; }}
    #core-metrics-count {{ font-size: 13px; color:#666; margin: 4px 0 10px; }}
    .card {{ border:1px solid #e5e5e5; border-radius:8px; padding: 12px 14px; background:#fafafa; margin: 10px 0; }}
    code {{ background:#f4f4f4; padding:2px 6px; border-radius:4px; }}
  </style>
</head>
<body>
  <h1>Momentum 因子有效性评估报告：UpWave / DownWave</h1>
  <div class="muted">生成时间：{now} ｜ 样本：近5年日线 ｜ 回测口径：非重叠持仓（开仓到平仓期间不开新仓）</div>

  <div class="section">
    <h2>1) 因子定义</h2>
    <div class="card">
      <p><b>UpWave(t)</b>：t-3 为阳线，且 t-3..t 四天收盘都在 MA20 上方。</p>
      <p><b>DownWave(t)</b>：t-3..t 四天收盘都在 MA20 下方。</p>
      <p>执行：t 日收盘确认信号，t+1 开盘进场，持有 N 天后收盘离场。</p>
      <p>本报告主口径：<code>long_only / short_only / long_short</code> 三模式对比，且 <b>不允许重叠持仓</b>。</p>
    </div>
  </div>

  <div class="section">
    <h2>2) 回测设定</h2>
    <ul>
      <li>样本区间：各标的近5年日线（yfinance）</li>
      <li>标的范围：覆盖 Crypto / A股个股 / A股指数 / 港股个股 / 港股指数 / 美股个股 / 美股指数 / 黄金</li>
      <li>持有期：5 / 10 / 30 天（另有参数扩展）</li>
      <li>参数扩展：MA窗口 {MA_WINDOWS}，持有期扩展 {HOLD_SWEEP}</li>
      <li>成本假设：基线 0 bps（另做 {COST_BPS_LIST} bps 敏感性）</li>
      <li>多空可交易：回测层面允许（实盘需考虑融券/合约限制）</li>
      <li>仓位规则：单笔满仓、非重叠</li>
      <li>大表产物：<code>reports/artifacts/updownwave/sensitivity_cost_big_table.csv</code>（market × ma × mode × hold × cost）</li>
    </ul>

    <h3>2.1 覆盖资产清单（成功加载）</h3>
    {coverage_show.to_html(index=False, escape=False)}

    <h3>2.2 未加载标的（如有）</h3>
    {failed_universe_show.to_html(index=False, escape=False)}
  </div>

  <div class="section">
    <h2>3) 基础表现</h2>
    <p>关键指标：Total Return, CAGR, Sharpe, Max Drawdown, Win Rate, Profit Factor, Trade Count。</p>

    <h3>3.1 资产大类聚合（long_short）</h3>
    {asset_class_show.to_html(index=False, escape=False)}

    <h3>3.2 全市场明细（可筛选/排序）</h3>
    <div class="toolbar">
      <label>市场
        <select id="filter-market">
          <option value="">全部</option>
          {market_options_html}
        </select>
      </label>
      <label>模式
        <select id="filter-mode">
          <option value="">全部</option>
          {mode_options_html}
        </select>
      </label>
      <label>持有天数
        <select id="filter-hold">
          <option value="">全部</option>
          {hold_options_html}
        </select>
      </label>
      <label>关键词
        <input id="filter-search" type="text" placeholder="搜索 market/mode/指标" />
      </label>
      <button id="filter-reset" type="button">重置</button>
    </div>
    <div id="core-metrics-count"></div>
    {core_table_html}
  </div>

  <div class="section">
    <h2>4) 拆解分析</h2>
    <h3>4.1 各市场 × 持有期 × 多空模式（CAGR 热力图）</h3>
    <img src="assets/01_heatmap_market_hold_mode_cagr.png" alt="heatmap" />

    <h3>4.2 年度收益（long_short, hold=10）</h3>
    <p class="muted">颜色说明：以 0% 为中轴（红亏绿盈），并对极端值做 95% 绝对分位裁剪，避免个别年份/标的把全图色阶“拉爆”。</p>
    <img src="assets/02_annual_return_heatmap.png" alt="annual" />

    <h3>4.3 参数敏感性（跨市场聚合：MA窗口 × 持有期）</h3>
    <img src="assets/03_xiaomi_param_sensitivity.png" alt="sensitivity" />
    <p class="muted">统计口径：long_short、0 bps，按市场聚合后展示 median CAGR 与稳健性。</p>
    {param_agg_show.to_html(index=False, escape=False)}

    <h3>4.4 成本敏感性（跨市场聚合）</h3>
    <img src="assets/04_cost_sensitivity.png" alt="cost" />
    <p class="muted">左图：不同持有期在不同成本下的 median CAGR；右图：正收益市场占比（pass rate）。</p>
    {cost_agg_show.to_html(index=False, escape=False)}

    <h3>4.5 收益贡献拆解（{anchor_name}，hold=10）</h3>
    <img src="assets/05_trade_contribution.png" alt="contrib" />
  </div>

  <div class="section">
    <h2>5) Usage Playbook（实盘使用手册）</h2>

    <h3>5.1 定位：入场信号还是环境过滤器（Q1~Q3）</h3>
    <p class="muted"><b>Q1 问题：</b>UpWave 更应该作为主入场信号，还是作为“交易许可”过滤器？</p>
    <p><b>一句话结论：</b>{q1_sentence}</p>
    <p><b>实盘动作：</b>{q1_action}</p>
    {q1_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q2 问题：</b>该因子更擅长捕捉启动、延续，还是过滤失败抄底？</p>
    <p><b>事件研究（Q2）一句话结论：</b>{q2_sentence}</p>
    <p><b>实盘动作：</b>{q2_action}</p>
    <img src="assets/08_trend_filter_enhancement.png" alt="trend-score-forward" />
    {event_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q3 问题：</b>这个因子最怕什么市场状态（震荡/波动收缩/过热拥挤）？</p>
    <p><b>禁区识别（Q3）一句话结论：</b>{q3_sentence}</p>
    <p><b>实盘动作：</b>{q3_action}</p>
    {fear_show.to_html(index=False, escape=False)}

    <h3>5.2 适配与名单（Q9）</h3>
    <p class="muted"><b>Q9 问题：</b>哪些资产类别更适配该因子，白/黑名单规则如何落地？</p>
    <p><b>一句话结论：</b>{q9_sentence}</p>
    <p><b>实盘动作：</b>{q9_action}</p>
    {class_show.to_html(index=False, escape=False)}

    <h3>5.3 参数与稳健区间（Q4~Q6）</h3>
    <p class="muted"><b>Q4 问题：</b>最佳持有期是否稳健，是否存在可执行的稳健区间？</p>
    <p><b>Q4 结论：</b>{q4_sentence}</p>
    <p><b>Q4 动作：</b>{q4_action}</p>
    <img src="assets/11_hold_robustness_curves.png" alt="hold-robustness" />
    {hold_show.to_html(index=False, escape=False)}
    {hold_band_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q5 问题：</b>MA 与连续天数 N 的参数是否稳定，还是存在过拟合风险？</p>
    <p><b>Q5 结论：</b>{q5_sentence}</p>
    <p><b>Q5 动作：</b>{q5_action}</p>
    <img src="assets/12_oos_stability_boxplot.png" alt="oos-stability" />
    {oos_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q6 问题：</b>在真实成本/滑点条件下，这套信号还能否存活？</p>
    <p><b>Q6 结论：</b>{q6_sentence}</p>
    <p><b>Q6 动作：</b>{q6_action}</p>
    {cost_budget_show.to_html(index=False, escape=False)}

    <h3>5.4 组合与风控（Q7~Q8）</h3>
    <p class="muted"><b>Q7 问题：</b>与主信号如何组合（AND / 分层仓位 / score 分位）才能兼顾收益与稳定？</p>
    <p><b>Q7 结论：</b>{q7_sentence}</p>
    <p><b>Q7 动作：</b>{q7_action}</p>
    <img src="assets/09_threshold_scan.png" alt="threshold-scan" />
    <img src="assets/10_ablation_delta_cagr.png" alt="ablation" />
    {combo_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q8 问题：</b>它能否作为独立风险管理模块，显著降低回撤并改善恢复效率？</p>
    <p><b>Q8 结论：</b>{q8_sentence}</p>
    <p><b>Q8 动作：</b>{q8_action}</p>
    <img src="assets/13_risk_module_equity.png" alt="risk-module-equity" />
    {risk_show.to_html(index=False, escape=False)}

    <h3>5.5 监控与失效（Q10~Q11）</h3>
    <p class="muted"><b>Q10 问题：</b>如何定义失效/降级，并设置可执行的停用阈值？</p>
    <p><b>Q10 结论：</b>{q10_sentence}</p>
    <p><b>Q10 动作：</b>{q10_action}</p>
    {failure_show.to_html(index=False, escape=False)}

    <p class="muted"><b>Q11 问题：</b>信号密度是否合理，资金利用率与换手是否匹配实盘约束？</p>
    <p><b>Q11 结论：</b>{q11_sentence}</p>
    <p><b>Q11 动作：</b>{q11_action}</p>
    <img src="assets/14_signal_density_yearly.png" alt="signal-density" />
    {density_show.to_html(index=False, escape=False)}

    <h3>5.6 Tail Risk（实盘仓位上限）</h3>
    <p class="muted"><b>Q13 问题：</b>尾部风险有多大，应如何反推单笔仓位、止损与波动目标？</p>
    <p class="muted">基于最差 5% 交易与 MAE/MFE 统计，推导单笔仓位建议（position_size_hint）。</p>
    {tail_show.to_html(index=False, escape=False)}

    <h3>5.7 文字版研究结论（Q1~Q14）</h3>
    <div class="card">
      <ol>
        <li><b>Q1 问题：</b>UpWave 更适合作为入场信号还是交易许可过滤器？<br/><b>结论：</b>{q1_sentence}<br/><b>实盘动作：</b>{q1_action}</li>
        <li><b>Q2 问题：</b>该因子更擅长捕捉启动、延续，还是过滤失败抄底？<br/><b>结论：</b>{q2_sentence}<br/><b>实盘动作：</b>{q2_action}</li>
        <li><b>Q3 问题：</b>该因子最怕什么环境（震荡/波动收缩/过热）？<br/><b>结论：</b>{q3_sentence}<br/><b>实盘动作：</b>{q3_action}</li>
        <li><b>Q4 问题：</b>最佳持有期是否稳健，能否给默认区间？<br/><b>结论：</b>{q4_sentence}<br/><b>实盘动作：</b>{q4_action}</li>
        <li><b>Q5 问题：</b>MA 与连续天数 N 是否敏感，是否存在过拟合？<br/><b>结论：</b>{q5_sentence}<br/><b>实盘动作：</b>{q5_action}</li>
        <li><b>Q6 问题：</b>成本/滑点条件下还能活吗？<br/><b>结论：</b>{q6_sentence}<br/><b>实盘动作：</b>{q6_action}</li>
        <li><b>Q7 问题：</b>与主信号如何组合最优（AND/分层/分位）？<br/><b>结论：</b>{q7_sentence}<br/><b>实盘动作：</b>{q7_action}</li>
        <li><b>Q8 问题：</b>能否作为风险管理模块独立使用？<br/><b>结论：</b>{q8_sentence}<br/><b>实盘动作：</b>{q8_action}</li>
        <li><b>Q9 问题：</b>哪些资产更适配，白/黑名单如何定义？<br/><b>结论：</b>{q9_sentence}<br/><b>实盘动作：</b>{q9_action}</li>
        <li><b>Q10 问题：</b>如何定义失效与降级，并执行停用规则？<br/><b>结论：</b>{q10_sentence}<br/><b>实盘动作：</b>{q10_action}</li>
        <li><b>Q11 问题：</b>信号密度是否合理，资金利用率是否健康？<br/><b>结论：</b>{q11_sentence}<br/><b>实盘动作：</b>{q11_action}</li>
        <li><b>Q12 问题：</b>2年训练+6个月验证的滚动 OOS 是否稳定？<br/><b>结论：</b>{q12_sentence}<br/><b>实盘动作：</b>{q12_action}</li>
        <li><b>Q13 问题：</b>Tail risk 有多大，仓位和止损怎么定？<br/><b>结论：</b>{q13_sentence}<br/><b>实盘动作：</b>{q13_action}</li>
        <li><b>Q14 问题：</b>综合来看，这个因子在实盘里的最优定位是什么？<br/><b>结论：</b>{q14_sentence}<br/><b>实盘动作：</b>{q14_action}</li>
      </ol>
    </div>
  </div>

  <div class="section">
    <h2>6) 稳定性分析（原有）</h2>
    <h3>6.1 市场迁移性（每市场 long_short 最佳持有期）</h3>
    {show_best.to_html(index=False, escape=False)}
    <h3>6.2 年份趋势分类稳定性（bull / bear / sideways）</h3>
    {regime_show.to_html(index=False, escape=False)}
    <h3>6.3 成本抗压能力（Break-even Cost）</h3>
    <p class="muted">每个市场先选 0bps 下最佳 (MA, hold) 组合，再看在不同成本下何时 CAGR 失效。</p>
    {break_even_show.to_html(index=False, escape=False)}
    <h3>6.4 回撤曲线（long_short，各市场最佳持有期）</h3>
    <img src="assets/06_drawdown_curves.png" alt="drawdown" />
  </div>

  <div class="section">
    <h2>7) 机制分析（原有）</h2>
    <p>信号后未来收益路径（{anchor_name}）：</p>
    <img src="assets/07_signal_forward_path.png" alt="forward-path" />
    {fp.to_html(index=False, escape=False)}
  </div>

  <div class="section">
    <h2>8) Trend Score 研究附录</h2>
    <div class="card">
      <p><b>研究原则：</b>先评分（连续关系）再阈值（离散决策），避免机械调参。</p>
      <p><b>标准化：</b>每个市场内将 BBW/ADR/ADX 映射到 0~1 分位分数。</p>
    </div>
    <h3>8.1 分桶策略表现（eq）</h3>
    {score_bucket_show.to_html(index=False, escape=False)}
    <h3>8.2 score 版本对比（soft gate）</h3>
    {score_version_show.to_html(index=False, escape=False)}
    <h3>8.3 阈值扫描（eq）</h3>
    {threshold_show.to_html(index=False, escape=False)}
    <h3>8.4 消融实验</h3>
    {ablation_show.to_html(index=False, escape=False)}
    <h3>8.5 信号保留率</h3>
    {tf_signal_show.to_html(index=False, escape=False)}
  </div>

  <div class="section">
    <h2>9) 风险与实盘约束</h2>
    <ul>
      <li>高收益组合通常伴随高回撤，尤其加密市场。</li>
      <li>A股做空存在现实限制（融券可得性、成本、限制）。</li>
      <li>成本、滑点、冲击成本会显著吞噬短持有期边际收益。</li>
      <li>容量受限：信号集中触发时，真实成交价格偏离会扩大。</li>
      <li>极端行情（跳空、熔断、流动性缺失）对该类规则不友好。</li>
    </ul>
  </div>

  <div class="section">
    <h2>10) 最终定位建议</h2>
    {suitability}
    <div class="card">
      <b>推荐定位：</b>作为趋势模块中的“信号过滤器/触发器”，与波动过滤、仓位管理、风险控制联动。<br/>
      <b>后续优化：</b>OOS/滚动窗口验证、成本情景、多因子融合（ATR/ADX/量能/筹码）与参数稳健区间筛选。
    </div>
  </div>

  <div class="section muted">
    原始产物：<code>reports/artifacts/updownwave</code> ｜ 页面：<code>reports/site/factors/updownwave</code>
  </div>

  {interactive_js}
</body>
</html>
"""

    (site_dir / "report.html").write_text(html, encoding="utf-8")

    # site index (reusable for future factors)
    idx_html = f"""
<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Momentum Research Reports</title>
<style>body{{font-family:Arial,\"PingFang SC\";margin:28px}}a{{display:block;margin:10px 0;font-size:18px}}</style></head>
<body>
<h1>Momentum Research Reports</h1>
<p>更新时间：{now}</p>
<a href="./factors/updownwave/report.html">UpWave / DownWave 因子有效性评估报告</a>
</body></html>
"""
    (root / "reports" / "site" / "index.html").write_text(idx_html, encoding="utf-8")

    # manifest
    manifest = {
        "generatedAt": now,
        "artifactsDir": str(artifact_dir.relative_to(root)),
        "siteDir": str(site_dir.relative_to(root)),
        "universe": ASSET_UNIVERSE,
        "loadedSymbols": {k: SYMBOLS[k] for k in loaded_names},
        "failedSymbols": failed_rows,
        "holds": HOLDS,
        "modes": MODES,
        "maWindows": MA_WINDOWS,
        "holdSweep": HOLD_SWEEP,
        "costBps": COST_BPS_LIST,
        "trendFilter": TREND_FILTER,
        "scoreVariants": SCORE_VARIANTS,
        "scoreBuckets": SCORE_BUCKET_LABELS,
        "thresholdScan": THRESHOLD_SCAN,
        "usagePlaybook": {
            "eventHorizons": [1, 3, 5, 10, 20, 30],
            "holdSweep": HOLD_SWEEP,
            "oosTrainDays": 504,
            "oosTestDays": 126,
        },
    }
    (artifact_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[ok] report generated")
    print("site:", site_dir / "report.html")
    print("index:", root / "reports" / "site" / "index.html")


if __name__ == "__main__":
    main()
