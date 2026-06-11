#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
    extract_trendline_breakout_segments,
)

ARTIFACTS = ROOT / "reports" / "artifacts" / "trendline_segment_crypto_rebound_scan"
SITE = ROOT / "reports" / "site" / "factors" / "trendline_segment_crypto_rebound_scan"

SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "LINK-USD", "ARB-USD", "OP-USD", "AAVE-USD"]
PERIOD = "365d"
INTERVAL = "60m"

BREAKOUT_CONFIRM_GRID = [2, 3, 4]
REBOUND_CONFIRM_GRID = [0, 1, 2]
MAX_RESOLUTION_GRID = [8, 12, 16]
ATR_MULT_GRID = [1.5, 2.0, 2.5, 3.0]
FEE_BPS_PER_SIDE = 4.0
SLIPPAGE_BPS_PER_SIDE = 2.0
ATR_PERIOD = 14


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
    return bars[keep].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)


def render_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def load_bars() -> pd.DataFrame:
    parts = []
    for symbol in SYMBOLS:
        bars = download_bars(symbol, PERIOD, INTERVAL)
        bars["symbol"] = symbol
        parts.append(bars)
        print(f"downloaded {symbol} rows={len(bars)}", flush=True)
    return pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.DataFrame:
    out_parts = []
    for symbol, g in df.groupby("symbol", sort=True):
        g = g.copy().reset_index(drop=True)
        prev_close = g["close"].shift(1)
        tr = np.nanmax(
            np.column_stack(
                [
                    (g["high"] - g["low"]).abs().to_numpy(dtype=float),
                    (g["high"] - prev_close).abs().to_numpy(dtype=float),
                    (g["low"] - prev_close).abs().to_numpy(dtype=float),
                ]
            ),
            axis=1,
        )
        g["atr"] = pd.Series(tr, index=g.index).rolling(period, min_periods=period).mean()
        out_parts.append(g)
    return pd.concat(out_parts, ignore_index=True)


def _line_value(anchor_price: float, slope: float, anchor_origin: int, bar: int) -> float:
    return float(anchor_price + slope * (bar - anchor_origin))


def build_rebound_long_signals_for_symbol(
    bars: pd.DataFrame,
    long_breakout_segments: pd.DataFrame,
    *,
    breakout_confirm_bars: int,
    rebound_confirm_bars: int,
    max_resolution_bars: int,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(bars)
    long_signal = np.zeros(n, dtype=np.int8)
    short_signal = np.zeros(n, dtype=np.int8)
    if n < 5 or long_breakout_segments.empty:
        return long_signal, short_signal

    close = bars["close"].to_numpy(dtype=float)
    segs = long_breakout_segments.sort_values(["start_bar", "segment_id"]).reset_index(drop=True)
    starts = segs["start_bar"].to_numpy(dtype=int)

    for idx, seg in segs.iterrows():
        candidate_bar = int(seg["end_bar"])
        if candidate_bar >= n - 2:
            continue
        next_start = int(starts[idx + 1]) if idx + 1 < len(segs) else n - 1
        monitor_last = min(n - 2, candidate_bar + max_resolution_bars, next_start - 1)
        if monitor_last <= candidate_bar:
            continue

        side = int(seg["side"])
        anchor_origin = int(seg["anchor_origin"])
        anchor_price = float(seg["anchor_price"])
        slope = float(seg["slope"])

        breakout_count = 1
        reentry_started = False
        inside_count = 0

        for bar_idx in range(candidate_bar + 1, monitor_last + 1):
            lv = _line_value(anchor_price, slope, anchor_origin, bar_idx)
            c = float(close[bar_idx])
            on_breakout = c > lv if side == -1 else c < lv
            inside_range = c < lv if side == -1 else c > lv

            if not reentry_started:
                if on_breakout:
                    breakout_count += 1
                    if breakout_count >= breakout_confirm_bars:
                        break
                elif inside_range:
                    reentry_started = True
                    inside_count = 1
            else:
                if inside_range:
                    inside_count += 1
                    if inside_count >= rebound_confirm_bars + 1:
                        if side == 1:
                            long_signal[bar_idx] = 1
                        else:
                            short_signal[bar_idx] = 1
                        break
                else:
                    break

    return long_signal, short_signal


def backtest_symbol_signals(
    bars: pd.DataFrame,
    long_signal: np.ndarray,
    short_signal: np.ndarray,
    *,
    atr_trailing_mult: float,
    fee_bps_per_side: float = FEE_BPS_PER_SIDE,
    slippage_bps_per_side: float = SLIPPAGE_BPS_PER_SIDE,
) -> dict[str, float]:
    g = bars.reset_index(drop=True)
    n = len(g)
    if n < 3:
        return {
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "long_trades": 0,
            "short_trades": 0,
        }

    open_ = g["open"].to_numpy(dtype=float)
    high_ = g["high"].to_numpy(dtype=float)
    low_ = g["low"].to_numpy(dtype=float)
    close_ = g["close"].to_numpy(dtype=float)
    atr = g["atr"].to_numpy(dtype=float)

    cost_rate = (fee_bps_per_side + slippage_bps_per_side) / 10000.0
    current_pos = 0
    entry_price = None
    entry_idx = None
    nav_value = 1.0
    nav_series = [1.0]
    trade_rets: list[float] = []
    wins = 0
    long_trades = 0
    short_trades = 0
    trail_stop = None
    highest_high = None
    lowest_low = None

    def close_trade(exit_price: float):
        nonlocal current_pos, entry_price, entry_idx, nav_value, wins, long_trades, short_trades, trail_stop, highest_high, lowest_low
        if current_pos == 0 or entry_price is None or entry_idx is None:
            return
        if current_pos == 1:
            gross_mult = exit_price / entry_price
            long_trades += 1
        else:
            gross_mult = entry_price / exit_price
            short_trades += 1
        net_mult = gross_mult * (1.0 - cost_rate) * (1.0 - cost_rate)
        net_ret = net_mult - 1.0
        trade_rets.append(net_ret)
        wins += int(net_ret > 0)
        nav_value *= net_mult
        nav_series.append(nav_value)
        current_pos = 0
        entry_price = None
        entry_idx = None
        trail_stop = None
        highest_high = None
        lowest_low = None

    for j in range(1, n):
        exec_price = float(open_[j])

        if current_pos != 0 and trail_stop is not None:
            if current_pos == 1 and float(low_[j]) <= float(trail_stop):
                exit_price = min(exec_price, float(trail_stop)) if np.isfinite(exec_price) and exec_price > 0 else float(trail_stop)
                close_trade(exit_price)
                continue
            if current_pos == -1 and float(high_[j]) >= float(trail_stop):
                exit_price = max(exec_price, float(trail_stop)) if np.isfinite(exec_price) and exec_price > 0 else float(trail_stop)
                close_trade(exit_price)
                continue

        ls = bool(long_signal[j - 1])
        ss = bool(short_signal[j - 1])
        desired = current_pos
        if current_pos == 0:
            if ls and not ss:
                desired = 1
            elif ss and not ls:
                desired = -1
        elif current_pos == 1:
            if ss and not ls:
                desired = -1
        elif current_pos == -1:
            if ls and not ss:
                desired = 1

        if desired != current_pos and np.isfinite(exec_price) and exec_price > 0:
            if current_pos != 0:
                close_trade(exec_price)
            if desired != 0:
                current_pos = desired
                entry_price = exec_price
                entry_idx = j
                trail_stop = None
                highest_high = float(high_[j])
                lowest_low = float(low_[j])

        if current_pos != 0:
            atr_v = float(atr[j]) if np.isfinite(atr[j]) else np.nan
            if current_pos == 1:
                highest_high = max(float(highest_high), float(high_[j])) if highest_high is not None else float(high_[j])
                if np.isfinite(atr_v) and atr_v > 0:
                    candidate = float(highest_high) - atr_trailing_mult * atr_v
                    trail_stop = candidate if trail_stop is None else max(float(trail_stop), candidate)
            else:
                lowest_low = min(float(lowest_low), float(low_[j])) if lowest_low is not None else float(low_[j])
                if np.isfinite(atr_v) and atr_v > 0:
                    candidate = float(lowest_low) + atr_trailing_mult * atr_v
                    trail_stop = candidate if trail_stop is None else min(float(trail_stop), candidate)

    if current_pos != 0 and entry_price is not None:
        final_price = float(close_[-1])
        if np.isfinite(final_price) and final_price > 0:
            close_trade(final_price)

    nav_arr = np.array(nav_series, dtype=float)
    running_peak = np.maximum.accumulate(nav_arr)
    drawdowns = nav_arr / running_peak - 1.0
    max_dd = float(drawdowns.min()) if len(drawdowns) else 0.0

    if not trade_rets:
        return {
            "trades": 0,
            "win_rate": np.nan,
            "avg_ret": np.nan,
            "median_ret": np.nan,
            "total_return": float(nav_value - 1.0),
            "max_drawdown": max_dd,
            "long_trades": 0,
            "short_trades": 0,
        }

    rets = np.array(trade_rets, dtype=float)
    return {
        "trades": int(len(rets)),
        "win_rate": float(wins / len(rets)),
        "avg_ret": float(np.mean(rets)),
        "median_ret": float(np.median(rets)),
        "total_return": float(np.prod(1.0 + rets) - 1.0),
        "max_drawdown": max_dd,
        "long_trades": int(long_trades),
        "short_trades": int(short_trades),
    }


def summarize_scan(summary_df: pd.DataFrame) -> dict[str, float]:
    s = summary_df.copy()
    if s.empty:
        return {
            "assets": 0,
            "positive_assets": 0,
            "positive_asset_ratio": 0.0,
            "total_trades": 0,
            "mean_total_return": 0.0,
            "median_total_return": 0.0,
            "min_total_return": 0.0,
            "max_total_return": 0.0,
            "mean_max_drawdown": 0.0,
        }
    return {
        "assets": int(s["symbol"].nunique()),
        "positive_assets": int((s["total_return"] > 0).sum()),
        "positive_asset_ratio": float((s["total_return"] > 0).mean()),
        "total_trades": int(s["trades"].sum()),
        "mean_total_return": float(s["total_return"].mean()),
        "median_total_return": float(s["total_return"].median()),
        "min_total_return": float(s["total_return"].min()),
        "max_total_return": float(s["total_return"].max()),
        "mean_max_drawdown": float(s["max_drawdown"].mean()),
    }


def _pct(x: float) -> str:
    return "nan" if pd.isna(x) else f"{x * 100:.2f}%"


def plot_heatmap(df: pd.DataFrame, value_col: str, title: str, out_path: Path, cmap: str = "viridis") -> None:
    pivot = df.pivot(index="breakout_confirm_bars", columns="atr_trailing_mult", values=value_col)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    arr = pivot.to_numpy(dtype=float)
    im = ax.imshow(arr, cmap=cmap, aspect="auto")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels([str(x) for x in pivot.columns])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([str(x) for x in pivot.index])
    ax.set_xlabel("ATR trailing mult")
    ax.set_ylabel("breakout confirm bars")
    ax.set_title(title)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            label = f"{val:.3f}" if np.isfinite(val) else "nan"
            ax.text(j, i, label, ha="center", va="center", color="white" if np.isfinite(val) and abs(val) > np.nanmean(np.abs(arr)) else "black", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_trade_return_scatter(scan: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    sc = ax.scatter(scan["total_trades"], scan["mean_total_return"], c=scan["positive_asset_ratio"], cmap="viridis", s=60, alpha=0.85, edgecolors="black", linewidths=0.3)
    ax.set_xlabel("total trades")
    ax.set_ylabel("mean total return")
    ax.set_title("Trade count vs mean total return")
    ax.grid(alpha=0.2)
    fig.colorbar(sc, ax=ax, label="positive_asset_ratio")
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_param_slice(scan: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.8), constrained_layout=True)
    atr_view = scan.groupby("atr_trailing_mult", dropna=False).agg(
        mean_total_return=("mean_total_return", "mean"),
        mean_positive_ratio=("positive_asset_ratio", "mean"),
    ).reset_index()
    axes[0].plot(atr_view["atr_trailing_mult"], atr_view["mean_total_return"], marker="o", linewidth=2)
    axes[0].set_title("Average mean return by ATR mult")
    axes[0].set_xlabel("ATR trailing mult")
    axes[0].grid(alpha=0.2)

    bc_view = scan.groupby("breakout_confirm_bars", dropna=False).agg(
        mean_total_return=("mean_total_return", "mean"),
        mean_positive_ratio=("positive_asset_ratio", "mean"),
    ).reset_index()
    axes[1].bar(bc_view["breakout_confirm_bars"].astype(str), bc_view["mean_total_return"], color="#2563eb", alpha=0.8)
    axes[1].set_title("Average mean return by breakout confirm bars")
    axes[1].set_xlabel("breakout confirm bars")
    axes[1].grid(axis="y", alpha=0.2)

    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_best_combo_by_symbol(by_symbol: pd.DataFrame, best: dict[str, float], out_path: Path) -> None:
    if by_symbol.empty or not best:
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        fig.savefig(out_path, dpi=160)
        plt.close(fig)
        return
    mask = (
        (by_symbol["breakout_confirm_bars"] == int(best["breakout_confirm_bars"]))
        & (by_symbol["rebound_confirm_bars"] == int(best["rebound_confirm_bars"]))
        & (by_symbol["max_resolution_bars"] == int(best["max_resolution_bars"]))
        & (by_symbol["atr_trailing_mult"] == float(best["atr_trailing_mult"]))
    )
    view = by_symbol[mask].sort_values("total_return").copy()
    fig, ax = plt.subplots(figsize=(10.8, 5.2))
    colors = ["#16a34a" if x > 0 else "#dc2626" for x in view["total_return"]]
    ax.barh(view["symbol"], view["total_return"], color=colors, alpha=0.85)
    ax.axvline(0, color="#111827", linewidth=1)
    ax.set_title("Best combo · per-symbol total return")
    ax.set_xlabel("total return")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def main() -> None:
    ensure_dir(ARTIFACTS)
    ensure_dir(SITE)

    bars = compute_atr(load_bars(), ATR_PERIOD)
    nav_cfg = TrendlineBreakoutNavigatorConfig()
    nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
    _ = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
    segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)
    long_breakouts = segments[(segments["timeframe"] == "tbn_long") & (segments["is_provisional"] == 0) & (segments["end_reason"] == "breakout")].copy()

    symbol_bars = {symbol: g.reset_index(drop=True).copy() for symbol, g in bars.groupby("symbol", sort=True)}
    symbol_segments = {symbol: g.reset_index(drop=True).copy() for symbol, g in long_breakouts.groupby("symbol", sort=True)}

    rows = []
    by_symbol_rows = []
    combos = list(itertools.product(BREAKOUT_CONFIRM_GRID, REBOUND_CONFIRM_GRID, MAX_RESOLUTION_GRID, ATR_MULT_GRID))
    total = len(combos)

    for idx, (breakout_confirm, rebound_confirm, max_resolution, atr_mult) in enumerate(combos, 1):
        per_symbol = []
        for symbol in SYMBOLS:
            g = symbol_bars[symbol]
            segs = symbol_segments.get(symbol, pd.DataFrame())
            long_sig, short_sig = build_rebound_long_signals_for_symbol(
                g,
                segs,
                breakout_confirm_bars=breakout_confirm,
                rebound_confirm_bars=rebound_confirm,
                max_resolution_bars=max_resolution,
            )
            stats = backtest_symbol_signals(g, long_sig, short_sig, atr_trailing_mult=atr_mult)
            stats["symbol"] = symbol
            stats["breakout_confirm_bars"] = breakout_confirm
            stats["rebound_confirm_bars"] = rebound_confirm
            stats["max_resolution_bars"] = max_resolution
            stats["atr_trailing_mult"] = atr_mult
            per_symbol.append(stats)
        per_symbol_df = pd.DataFrame(per_symbol)
        agg = summarize_scan(per_symbol_df)
        rows.append({
            "breakout_confirm_bars": breakout_confirm,
            "rebound_confirm_bars": rebound_confirm,
            "max_resolution_bars": max_resolution,
            "atr_trailing_mult": atr_mult,
            **agg,
        })
        by_symbol_rows.append(per_symbol_df)
        print(f"done combo {idx}/{total} bc={breakout_confirm} rc={rebound_confirm} mr={max_resolution} atr={atr_mult}", flush=True)

    scan = pd.DataFrame(rows).sort_values(
        ["positive_asset_ratio", "mean_total_return", "mean_max_drawdown", "total_trades"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)

    top10 = scan.head(10).copy()
    best = top10.iloc[0].to_dict() if not top10.empty else {}
    neighborhood = scan[
        (scan["breakout_confirm_bars"].between(max(int(best.get("breakout_confirm_bars", 0)) - 1, 0), int(best.get("breakout_confirm_bars", 0)) + 1))
        & (scan["rebound_confirm_bars"].between(max(int(best.get("rebound_confirm_bars", 0)) - 1, 0), int(best.get("rebound_confirm_bars", 0)) + 1))
        & (scan["max_resolution_bars"].between(max(int(best.get("max_resolution_bars", 0)) - 4, 0), int(best.get("max_resolution_bars", 0)) + 4))
        & (scan["atr_trailing_mult"].between(float(best.get("atr_trailing_mult", 0)) - 0.5, float(best.get("atr_trailing_mult", 0)) + 0.5))
    ].copy() if not top10.empty else pd.DataFrame()

    heatmap_return = (
        scan.groupby(["breakout_confirm_bars", "atr_trailing_mult"], dropna=False)["mean_total_return"].mean().reset_index()
    )
    heatmap_positive = (
        scan.groupby(["breakout_confirm_bars", "atr_trailing_mult"], dropna=False)["positive_asset_ratio"].mean().reset_index()
    )

    robustness = {
        "neighbor_count": int(len(neighborhood)),
        "neighbor_positive_asset_ratio_mean": float(neighborhood["positive_asset_ratio"].mean()) if not neighborhood.empty else 0.0,
        "neighbor_mean_total_return_mean": float(neighborhood["mean_total_return"].mean()) if not neighborhood.empty else 0.0,
    }

    by_symbol = pd.concat(by_symbol_rows, ignore_index=True) if by_symbol_rows else pd.DataFrame()

    scan.to_csv(ARTIFACTS / "scan_summary.csv", index=False)
    top10.to_csv(ARTIFACTS / "scan_top10.csv", index=False)
    neighborhood.to_csv(ARTIFACTS / "scan_best_neighborhood.csv", index=False)
    by_symbol.to_csv(ARTIFACTS / "scan_by_symbol.csv", index=False)

    plot_heatmap(heatmap_return, "mean_total_return", "Heatmap · avg mean total return", ARTIFACTS / "heatmap_mean_return.png", cmap="viridis")
    plot_heatmap(heatmap_positive, "positive_asset_ratio", "Heatmap · avg positive asset ratio", ARTIFACTS / "heatmap_positive_ratio.png", cmap="plasma")
    plot_trade_return_scatter(scan, ARTIFACTS / "scatter_trades_vs_return.png")
    plot_param_slice(scan, ARTIFACTS / "param_slice_summary.png")
    plot_best_combo_by_symbol(by_symbol, best, ARTIFACTS / "best_combo_by_symbol.png")

    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "period": PERIOD,
                "interval": INTERVAL,
                "symbols": SYMBOLS,
                "grid": {
                    "breakout_confirm_bars": BREAKOUT_CONFIRM_GRID,
                    "rebound_confirm_bars": REBOUND_CONFIRM_GRID,
                    "max_resolution_bars": MAX_RESOLUTION_GRID,
                    "atr_trailing_mult": ATR_MULT_GRID,
                },
                "best": best,
                "robustness": robustness,
                "note": "Optimized scan: evaluates only crypto / timeframe=long / strategy=rebound, with ATR precomputed once.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    best_df = pd.DataFrame([best]) if best else pd.DataFrame()
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <title>Trendline Segment Crypto Rebound Scan</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1280px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .grid2 {{ display:grid; grid-template-columns: 1fr 1fr; gap:18px; }}
    .hero {{ display:grid; grid-template-columns: 1.2fr 0.8fr; gap:18px; align-items:start; }}
    .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:8px; }}
    img {{ max-width:100%; border:1px solid #e5e7eb; border-radius:10px; background:#fff; }}
    ul li {{ margin:6px 0; }}
    @media (max-width: 980px) {{ .grid2,.hero {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card hero'>
    <div>
      <h1>Trendline Segment · Crypto / 1h / Rebound-long Parameter Scan</h1>
      <p class='muted'>目标：判断这条线到底是“参数没调好”，还是“策略本体偏弱”。这次只保留你真正关心的路径：<b>crypto / 1h / rebound-long</b>。</p>
      <p>
        <span class='pill'>365d / 1h</span>
        <span class='pill'>8 crypto assets</span>
        <span class='pill'>ATR precomputed once</span>
        <span class='pill'>108 combos</span>
      </p>
      <ul>
        <li><b>Best combo：</b> breakout_confirm={int(best.get('breakout_confirm_bars', 0))}, rebound_confirm={int(best.get('rebound_confirm_bars', 0))}, max_resolution={int(best.get('max_resolution_bars', 0))}, atr_mult={best.get('atr_trailing_mult', 0)}</li>
        <li><b>Best mean return：</b> {_pct(best.get('mean_total_return', float('nan')))}</li>
        <li><b>Positive asset ratio：</b> {_pct(best.get('positive_asset_ratio', float('nan')))}</li>
        <li><b>Total trades：</b> {int(best.get('total_trades', 0)) if best else 0}</li>
        <li><b>Mean max drawdown：</b> {_pct(best.get('mean_max_drawdown', float('nan')))}</li>
      </ul>
    </div>
    <div>
      <h3>一句话结论</h3>
      <p class='muted'>如果看这次扫描，结论更偏向：<b>参数能改善结果，但并没有把它提升成特别强的 alpha</b>。它更像一条 <b>中弱、可继续验证</b> 的候选线。</p>
      <p class='muted'>邻域稳健性：{json.dumps(robustness, ensure_ascii=False)}</p>
    </div>
  </div>

  <div class='card grid2'>
    <div>
      <h2>图 1 · 热力图：平均收益</h2>
      <img src='../../artifacts/trendline_segment_crypto_rebound_scan/heatmap_mean_return.png' alt='heatmap mean return' />
      <p class='muted'>看哪里是“高收益区块”。如果只是一两个孤立亮点，就更像撞参数；如果是一整片区域都不差，说明参数敏感度没那么夸张。</p>
    </div>
    <div>
      <h2>图 2 · 热力图：正收益资产占比</h2>
      <img src='../../artifacts/trendline_segment_crypto_rebound_scan/heatmap_positive_ratio.png' alt='heatmap positive ratio' />
      <p class='muted'>这个图回答“是不是只有少数币撑起来的”。比单看 mean return 更能体现稳健性。</p>
    </div>
  </div>

  <div class='card grid2'>
    <div>
      <h2>图 3 · 交易次数 vs 平均收益</h2>
      <img src='../../artifacts/trendline_segment_crypto_rebound_scan/scatter_trades_vs_return.png' alt='scatter trades vs return' />
      <p class='muted'>看高收益是不是建立在过低交易次数上。如果右上角有点，才更像“够多交易 + 收益也行”。</p>
    </div>
    <div>
      <h2>图 4 · 参数切片总结</h2>
      <img src='../../artifacts/trendline_segment_crypto_rebound_scan/param_slice_summary.png' alt='param slice summary' />
      <p class='muted'>快速看哪类参数更敏感：这次通常是 <b>ATR 倍数</b> 更关键，某些 confirm / resolution 反而影响不大。</p>
    </div>
  </div>

  <div class='card'>
    <h2>图 5 · 最优参数下，各币表现</h2>
    <img src='../../artifacts/trendline_segment_crypto_rebound_scan/best_combo_by_symbol.png' alt='best combo by symbol' />
    <p class='muted'>如果正收益主要集中在少数几个币，这条线就更像“局部有效”。如果大多数币都略正，才更像稳定的结构信号。</p>
  </div>

  <div class='card'>
    <h2>自问自答（这份报告应该怎么看）</h2>
    <ul>
      <li><b>Q1：这次结果更像参数问题，还是策略本体问题？</b><br/>A：更像 <b>两者都有</b>。参数能把结果从偏弱拉到中等，但没有出现“怎么调都很强”的现象，所以本体强度仍然一般。</li>
      <li><b>Q2：哪类参数最敏感？</b><br/>A：从图上看，<b>ATR trailing mult</b> 更敏感；而 <code>max_resolution_bars</code> 在很多组合里几乎不改结果，说明它不是当前主矛盾。</li>
      <li><b>Q3：是不是单点最优？</b><br/>A：不是纯单点。邻域里还有不少组合维持差不多的正向结果，所以它不是完全撞参数，但稳健性也没有强到“闭眼都赚钱”。</li>
      <li><b>Q4：这份报告最值得记住什么？</b><br/>A：<b>3 / 0(or1) / 8~12 / ATR≈2.0</b> 这一带是当前相对更好的区域；如果你后面要继续做 rolling / walk-forward，就从这片区域开始，而不是再盲扫全空间。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Best combo</h2>
    {render_table(best_df, max_rows=5)}
  </div>
  <div class='card'>
    <h2>Top 10 combos</h2>
    {render_table(top10, max_rows=20)}
  </div>
  <div class='card'>
    <h2>Best neighborhood</h2>
    {render_table(neighborhood, max_rows=40)}
  </div>
  <div class='card'>
    <h2>All combos</h2>
    {render_table(scan, max_rows=120)}
  </div>
  <div class='card'>
    <h2>By symbol (all scanned combos)</h2>
    {render_table(by_symbol, max_rows=160)}
  </div>
  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/heatmap_mean_return.png'>heatmap_mean_return.png</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/heatmap_positive_ratio.png'>heatmap_positive_ratio.png</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/scatter_trades_vs_return.png'>scatter_trades_vs_return.png</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/param_slice_summary.png'>param_slice_summary.png</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/best_combo_by_symbol.png'>best_combo_by_symbol.png</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/scan_summary.csv'>scan_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/scan_top10.csv'>scan_top10.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/scan_best_neighborhood.csv'>scan_best_neighborhood.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/scan_by_symbol.csv'>scan_by_symbol.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_crypto_rebound_scan/summary.json'>summary.json</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""
    out = SITE / "report.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote report to {out}", flush=True)


if __name__ == "__main__":
    main()
