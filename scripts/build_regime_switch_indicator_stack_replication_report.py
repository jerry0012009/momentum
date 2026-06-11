#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "regime_switch_indicator_stack_replication"
SITE_DIR = ROOT / "reports" / "site" / "reading" / "regime_switch_indicator_stack_replication"
SITE_PATH = SITE_DIR / "report.html"


ASSETS = [
    {"name": "BTC", "ticker": "BTC-USD", "asset_class": "Crypto"},
    {"name": "ETH", "ticker": "ETH-USD", "asset_class": "Crypto"},
    {"name": "SOL", "ticker": "SOL-USD", "asset_class": "Crypto"},
    {"name": "SPY", "ticker": "SPY", "asset_class": "美股"},
    {"name": "QQQ", "ticker": "QQQ", "asset_class": "美股"},
    {"name": "AAPL", "ticker": "AAPL", "asset_class": "美股"},
    {"name": "沪深300ETF", "ticker": "510300.SS", "asset_class": "A股"},
    {"name": "创业板ETF", "ticker": "159915.SZ", "asset_class": "A股"},
    {"name": "贵州茅台", "ticker": "600519.SS", "asset_class": "A股"},
]

FREQ_SETTINGS = [
    {"interval": "1d", "period": "10y", "label": "日频(1d)"},
    {"interval": "1wk", "period": "10y", "label": "周频(1wk)"},
    {"interval": "60m", "period": "730d", "label": "小时频(60m)"},
]

BASE_STRATEGIES = ["EMA", "BB", "RSI", "PSAR"]
FILTERED_STRATEGIES = ["MIHS9", "MIHS7", "MIHCS9", "MIHCS7"]
ALL_STRATEGIES = BASE_STRATEGIES + FILTERED_STRATEGIES

PAPER_CLAIM_PP = {
    "EMA": 394.13,
    "BB": -71.70,
    "RSI": -64.50,
    "PSAR": 113.80,
    "MIHS9": 154.45,
    "MIHS7": 437.48,
    "MIHCS9": 256.31,
    "MIHCS7": 701.77,
}


@dataclass
class BTResult:
    equity: pd.Series
    trades: pd.DataFrame
    metrics: Dict[str, float]


def download_bars(
    ticker: str,
    *,
    period: Optional[str] = None,
    interval: str = "1d",
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> pd.DataFrame:
    kwargs = {
        "tickers": ticker,
        "interval": interval,
        "auto_adjust": False,
        "progress": False,
        "group_by": "column",
    }
    if start is not None:
        kwargs["start"] = start
    if end is not None:
        kwargs["end"] = end
    if period is not None:
        kwargs["period"] = period

    raw = yf.download(**kwargs)
    if raw is None or raw.empty:
        raise ValueError(f"no data: {ticker} {interval}")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] if isinstance(c, tuple) else c for c in raw.columns]

    bars = raw.reset_index().rename(
        columns={
            "Date": "timestamp",
            "Datetime": "timestamp",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )

    need = ["timestamp", "open", "high", "low", "close", "volume"]
    for c in need:
        if c not in bars.columns:
            raise ValueError(f"missing column {c}: {ticker} {interval}")

    bars = bars[need].copy()
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    bars = bars.sort_values("timestamp").dropna(subset=["open", "high", "low", "close"])
    bars = bars[(bars["open"] > 0) & (bars["high"] > 0) & (bars["low"] > 0) & (bars["close"] > 0)]
    bars["volume"] = bars["volume"].fillna(0.0)
    bars = bars.reset_index(drop=True)
    if len(bars) < 120:
        raise ValueError(f"too few bars: {ticker} {interval} ({len(bars)})")
    return bars


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(50.0)


def bollinger(close: pd.Series, window: int = 21, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    return lower, mid, upper


def psar(high: pd.Series, low: pd.Series, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    n = len(high)
    out = np.full(n, np.nan, dtype=float)
    if n < 2:
        return pd.Series(out, index=high.index)

    trend_up = True
    af = step
    ep = float(high.iloc[0])
    sar = float(low.iloc[0])
    out[0] = sar

    for i in range(1, n):
        prev_sar = sar
        sar = prev_sar + af * (ep - prev_sar)

        if trend_up:
            sar = min(sar, float(low.iloc[i - 1]))
            if i >= 2:
                sar = min(sar, float(low.iloc[i - 2]))
            if float(low.iloc[i]) < sar:
                trend_up = False
                sar = ep
                ep = float(low.iloc[i])
                af = step
            else:
                if float(high.iloc[i]) > ep:
                    ep = float(high.iloc[i])
                    af = min(af + step, max_step)
        else:
            sar = max(sar, float(high.iloc[i - 1]))
            if i >= 2:
                sar = max(sar, float(high.iloc[i - 2]))
            if float(high.iloc[i]) > sar:
                trend_up = True
                sar = ep
                ep = float(high.iloc[i])
                af = step
            else:
                if float(low.iloc[i]) < ep:
                    ep = float(low.iloc[i])
                    af = min(af + step, max_step)

        out[i] = sar

    return pd.Series(out, index=high.index)


def build_feature_frame(bars: pd.DataFrame) -> pd.DataFrame:
    df = bars.copy()
    df["ema9"] = ema(df["close"], 9)
    df["ema20"] = ema(df["close"], 20)
    df["rsi14"] = rsi(df["close"], 14)
    df["rsi_ema7"] = ema(df["rsi14"], 7)
    df["rsi_ema9"] = ema(df["rsi14"], 9)
    bb_l, bb_m, bb_u = bollinger(df["close"], window=21, num_std=2.0)
    df["bb_lower"] = bb_l
    df["bb_mid"] = bb_m
    df["bb_upper"] = bb_u
    df["psar"] = psar(df["high"], df["low"], step=0.02, max_step=0.2)
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)
    df["prev_rsi"] = df["rsi14"].shift(1)
    return df


def signal_ema(row: pd.Series) -> str:
    if row["ema9"] > row["ema20"]:
        return "BUY"
    if row["ema9"] < row["ema20"]:
        return "SELL"
    return "HOLD"


def signal_bb(row: pd.Series) -> str:
    if pd.notna(row["bb_lower"]) and row["close"] <= row["bb_lower"]:
        return "BUY"
    if pd.notna(row["bb_upper"]) and row["close"] >= row["bb_upper"]:
        return "SELL"
    return "HOLD"


def signal_rsi(row: pd.Series) -> str:
    if row["rsi14"] <= 40:
        return "BUY"
    if row["rsi14"] >= 60:
        return "SELL"
    return "HOLD"


def psar_buy_cond(row: pd.Series) -> bool:
    if pd.isna(row["prev_high"]) or pd.isna(row["psar"]):
        return False
    return (row["psar"] <= row["close"]) and (row["high"] > row["prev_high"])


def psar_sell_cond(row: pd.Series) -> bool:
    if pd.isna(row["prev_low"]) or pd.isna(row["psar"]):
        return False
    return (row["psar"] > row["close"]) and (row["low"] < row["prev_low"])


def signal_psar(row: pd.Series) -> str:
    if psar_buy_cond(row):
        return "BUY"
    if psar_sell_cond(row):
        return "SELL"
    return "HOLD"


def signal_mihs(df: pd.DataFrame, ema_period: int, constrained: bool) -> pd.Series:
    regime_col = f"rsi_ema{ema_period}"
    sig = []
    for _, row in df.iterrows():
        regime_v = row[regime_col]
        if pd.isna(regime_v):
            sig.append("HOLD")
            continue

        # Uptrend -> EMA strategy
        if regime_v > 60:
            if row["ema9"] > row["ema20"]:
                sig.append("BUY")
            elif row["ema9"] < row["ema20"]:
                sig.append("SELL")
            else:
                sig.append("HOLD")
            continue

        # Downtrend -> PSAR branch
        if regime_v < 40:
            if constrained:
                if psar_sell_cond(row):
                    sig.append("SELL")
                else:
                    sig.append("HOLD")
            else:
                if psar_buy_cond(row):
                    sig.append("BUY")
                elif psar_sell_cond(row):
                    sig.append("SELL")
                else:
                    sig.append("HOLD")
            continue

        # Fluctuating -> RSI branch
        prev_rsi = row["prev_rsi"]
        cur_rsi = row["rsi14"]
        if pd.isna(prev_rsi) or pd.isna(cur_rsi):
            sig.append("HOLD")
            continue

        sell_cross = (prev_rsi > 55) and (cur_rsi <= 55)
        buy_cross = (prev_rsi < 45) and (cur_rsi >= 45)

        if sell_cross:
            sig.append("SELL")
        elif buy_cross and (not constrained):
            sig.append("BUY")
        else:
            sig.append("HOLD")

    return pd.Series(sig, index=df.index, name="signal")


def run_long_only_backtest(df: pd.DataFrame, signals: pd.Series, initial_capital: float = 100000.0) -> BTResult:
    cash = float(initial_capital)
    qty = 0.0
    in_pos = False
    entry_price = np.nan

    equity = []
    trades = []

    for i, row in df.iterrows():
        px = float(row["close"])
        sig = signals.iloc[i]

        if sig == "BUY" and (not in_pos) and px > 0:
            qty = cash / px
            cash = 0.0
            in_pos = True
            entry_price = px
        elif sig == "SELL" and in_pos and px > 0:
            cash = qty * px
            ret = px / entry_price - 1.0
            trades.append(
                {
                    "entry_price": float(entry_price),
                    "exit_price": px,
                    "ret": float(ret),
                    "win": int(ret > 0),
                    "exit_ts": row["timestamp"],
                }
            )
            qty = 0.0
            in_pos = False
            entry_price = np.nan

        eq = cash + qty * px
        equity.append(eq)

    if in_pos and qty > 0:
        final_px = float(df.iloc[-1]["close"])
        cash = qty * final_px
        ret = final_px / entry_price - 1.0
        trades.append(
            {
                "entry_price": float(entry_price),
                "exit_price": final_px,
                "ret": float(ret),
                "win": int(ret > 0),
                "exit_ts": df.iloc[-1]["timestamp"],
            }
        )
        qty = 0.0
        in_pos = False
        equity[-1] = cash

    equity_s = pd.Series(equity, index=pd.to_datetime(df["timestamp"], utc=True), name="equity")
    trades_df = pd.DataFrame(trades)

    final_equity = float(equity_s.iloc[-1])
    pp = (final_equity / initial_capital - 1.0) * 100.0

    nt = int(len(trades_df))
    if nt > 0:
        npct = float(trades_df["win"].mean() * 100.0)
        avg_ret = float(trades_df["ret"].mean() * 100.0)
    else:
        npct = np.nan
        avg_ret = np.nan

    days = max(int((equity_s.index[-1] - equity_s.index[0]).days), 1)
    cagr = (final_equity / initial_capital) ** (365.0 / days) - 1.0 if final_equity > 0 else np.nan

    dd = equity_s / equity_s.cummax() - 1.0
    mdd = float(dd.min())

    metrics = {
        "profit_pct": float(pp),
        "np_pct": float(npct) if np.isfinite(npct) else np.nan,
        "nt": float(nt),
        "avg_trade_ret_pct": float(avg_ret) if np.isfinite(avg_ret) else np.nan,
        "final_equity": final_equity,
        "cagr": float(cagr) if np.isfinite(cagr) else np.nan,
        "max_drawdown": mdd,
    }

    return BTResult(equity=equity_s, trades=trades_df, metrics=metrics)


def compute_all_signals(df: pd.DataFrame) -> Dict[str, pd.Series]:
    sigs = {
        "EMA": df.apply(signal_ema, axis=1),
        "BB": df.apply(signal_bb, axis=1),
        "RSI": df.apply(signal_rsi, axis=1),
        "PSAR": df.apply(signal_psar, axis=1),
        "MIHS9": signal_mihs(df, ema_period=9, constrained=False),
        "MIHS7": signal_mihs(df, ema_period=7, constrained=False),
        "MIHCS9": signal_mihs(df, ema_period=9, constrained=True),
        "MIHCS7": signal_mihs(df, ema_period=7, constrained=True),
    }
    for k, s in sigs.items():
        sigs[k] = s.fillna("HOLD")
    return sigs


def run_strategy_suite(df: pd.DataFrame) -> Dict[str, BTResult]:
    sigs = compute_all_signals(df)
    out: Dict[str, BTResult] = {}
    for name in ALL_STRATEGIES:
        out[name] = run_long_only_backtest(df, sigs[name], initial_capital=100000.0)
    return out


def fmt_pct(v: float | int | None) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.2f}%"


def fmt_num(v: float | int | None, d: int = 2) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "-"
    return f"{float(v):.{d}f}"


def build_table_html(df: pd.DataFrame, cols: List[str]) -> str:
    if df.empty:
        return "<p>无数据</p>"
    use = df[cols].copy()
    return use.to_html(index=False, border=0, classes="data-table", justify="left", escape=False)


def make_paper_bar_chart(paper_df: pd.DataFrame, out_path: Path) -> None:
    order = ["EMA", "BB", "RSI", "PSAR", "MIHS9", "MIHS7", "MIHCS9", "MIHCS7"]
    d = paper_df.set_index("strategy").reindex(order).reset_index()

    plt.figure(figsize=(11, 4.8))
    colors = ["#64748b"] * 4 + ["#2563eb", "#1d4ed8", "#16a34a", "#15803d"]
    plt.bar(d["strategy"], d["profit_pct"], color=colors)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.title("BTC 日频(2018-2022) | 论文口径复现实验 Profit %")
    plt.ylabel("Profit %")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def make_filter_compare_chart(summary_df: pd.DataFrame, out_path: Path) -> None:
    if summary_df.empty:
        return
    d = summary_df.copy()
    d["tag"] = d["asset"] + " | " + d["freq"]

    plt.figure(figsize=(8, 7))
    color_map = {"Crypto": "#f59e0b", "美股": "#2563eb", "A股": "#dc2626"}
    for ac, g in d.groupby("asset_class"):
        plt.scatter(
            g["best_unfiltered_pp"],
            g["best_filtered_pp"],
            s=55,
            alpha=0.85,
            label=ac,
            color=color_map.get(ac, "#475569"),
        )

    lo = min(d["best_unfiltered_pp"].min(), d["best_filtered_pp"].min()) - 5
    hi = max(d["best_unfiltered_pp"].max(), d["best_filtered_pp"].max()) + 5
    plt.plot([lo, hi], [lo, hi], "k--", linewidth=1)
    plt.xlim(lo, hi)
    plt.ylim(lo, hi)
    plt.xlabel("未做趋势筛选（四个单指标中最佳 Profit%）")
    plt.ylabel("做趋势筛选（四个原型中最佳 Profit%）")
    plt.title("多资产×多频率：趋势筛选前后收益对比")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def make_equity_example_chart(eq_map: Dict[str, pd.Series], out_path: Path) -> None:
    plt.figure(figsize=(11, 4.6))
    for name, s in eq_map.items():
        plt.plot(s.index, s.values, label=name, linewidth=1.8)
    plt.title("BTC 日频(2018-2022) 权益曲线示例")
    plt.ylabel("Equity")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def make_paper_claim_compare_chart(comp_df: pd.DataFrame, out_path: Path) -> None:
    order = ["EMA", "BB", "RSI", "PSAR", "MIHS9", "MIHS7", "MIHCS9", "MIHCS7"]
    d = comp_df.set_index("strategy").reindex(order).reset_index()
    x = np.arange(len(d))
    w = 0.38

    plt.figure(figsize=(12, 4.8))
    plt.bar(x - w / 2, d["paper_claim_pp"], width=w, label="论文 claim", color="#94a3b8")
    plt.bar(x + w / 2, d["reproduced_pp"], width=w, label="clean-room 复现", color="#2563eb")
    plt.axhline(0, color="#334155", linewidth=1)
    plt.xticks(x, d["strategy"], rotation=15)
    plt.ylabel("Profit %")
    plt.title("BTC 日频(2018-2022) | 论文声称值 vs clean-room 复现值")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def make_delta_heatmap(pair_df: pd.DataFrame, out_path: Path) -> None:
    if pair_df.empty:
        return
    pivot = pair_df.pivot(index="asset", columns="freq", values="delta_filtered_minus_unfiltered")
    pivot = pivot.reindex(sorted(pivot.index), axis=0)
    col_order = [c for c in ["日频(1d)", "周频(1wk)", "小时频(60m)"] if c in pivot.columns]
    pivot = pivot[col_order]
    arr = pivot.values.astype(float)

    plt.figure(figsize=(8.5, max(4.8, 0.45 * len(pivot.index))))
    vmax = np.nanmax(np.abs(arr)) if np.isfinite(arr).any() else 1.0
    im = plt.imshow(arr, aspect="auto", cmap="RdYlGn", vmin=-vmax, vmax=vmax)
    plt.colorbar(im, label="filtered - unfiltered (Profit %) ")
    plt.xticks(np.arange(len(pivot.columns)), pivot.columns)
    plt.yticks(np.arange(len(pivot.index)), pivot.index)
    plt.title("各资产在不同频率上的趋势筛选增益/拖累")

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if np.isfinite(arr[i, j]):
                plt.text(j, i, f"{arr[i, j]:.0f}", ha="center", va="center", fontsize=8, color="#111827")

    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def main() -> int:
    ART_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    # 1) paper-window replication (BTC 2018-2022 daily)
    btc_paper = download_bars("BTC-USD", start="2018-01-01", end="2023-01-01", interval="1d")
    btc_feat = build_feature_frame(btc_paper)
    paper_bt = run_strategy_suite(btc_feat)

    paper_rows = []
    for s in ALL_STRATEGIES:
        m = paper_bt[s].metrics
        paper_rows.append(
            {
                "strategy": s,
                "profit_pct": m["profit_pct"],
                "np_pct": m["np_pct"],
                "nt": int(m["nt"]),
                "cagr_pct": m["cagr"] * 100 if np.isfinite(m["cagr"]) else np.nan,
                "max_dd_pct": m["max_drawdown"] * 100 if np.isfinite(m["max_drawdown"]) else np.nan,
            }
        )
    paper_df = pd.DataFrame(paper_rows)
    paper_df.to_csv(ART_DIR / "paper_window_btc_2018_2022_metrics.csv", index=False)

    make_paper_bar_chart(paper_df, ART_DIR / "paper_profit_bar.png")
    make_equity_example_chart(
        {
            "EMA": paper_bt["EMA"].equity,
            "MIHS7": paper_bt["MIHS7"].equity,
            "MIHCS7": paper_bt["MIHCS7"].equity,
        },
        ART_DIR / "paper_equity_curves.png",
    )

    claim_compare_df = paper_df[["strategy", "profit_pct", "nt"]].copy()
    claim_compare_df = claim_compare_df.rename(columns={"profit_pct": "reproduced_pp", "nt": "reproduced_nt"})
    claim_compare_df["paper_claim_pp"] = claim_compare_df["strategy"].map(PAPER_CLAIM_PP)
    claim_compare_df["pp_diff_repro_minus_claim"] = claim_compare_df["reproduced_pp"] - claim_compare_df["paper_claim_pp"]
    claim_compare_df.to_csv(ART_DIR / "paper_claim_compare.csv", index=False)
    make_paper_claim_compare_chart(claim_compare_df, ART_DIR / "paper_claim_compare.png")

    # 2) cross-asset / cross-frequency backtests
    rows = []
    skipped = []

    for a in ASSETS:
        for f in FREQ_SETTINGS:
            try:
                bars = download_bars(a["ticker"], period=f["period"], interval=f["interval"])
                feat = build_feature_frame(bars)
                bt = run_strategy_suite(feat)

                start_ts = feat["timestamp"].iloc[0]
                end_ts = feat["timestamp"].iloc[-1]
                bars_n = len(feat)

                for s in ALL_STRATEGIES:
                    m = bt[s].metrics
                    rows.append(
                        {
                            "asset": a["name"],
                            "ticker": a["ticker"],
                            "asset_class": a["asset_class"],
                            "freq": f["label"],
                            "interval": f["interval"],
                            "bars": bars_n,
                            "start": start_ts.strftime("%Y-%m-%d"),
                            "end": end_ts.strftime("%Y-%m-%d"),
                            "strategy": s,
                            "group": "filtered" if s in FILTERED_STRATEGIES else "unfiltered",
                            "profit_pct": m["profit_pct"],
                            "np_pct": m["np_pct"],
                            "nt": m["nt"],
                            "cagr_pct": m["cagr"] * 100 if np.isfinite(m["cagr"]) else np.nan,
                            "max_dd_pct": m["max_drawdown"] * 100 if np.isfinite(m["max_drawdown"]) else np.nan,
                        }
                    )
            except Exception as e:
                skipped.append(
                    {
                        "asset": a["name"],
                        "ticker": a["ticker"],
                        "freq": f["label"],
                        "interval": f["interval"],
                        "reason": str(e),
                    }
                )

    res_df = pd.DataFrame(rows)
    if res_df.empty:
        raise RuntimeError("No cross-market results produced.")

    res_df.to_csv(ART_DIR / "cross_market_results.csv", index=False)
    pd.DataFrame(skipped).to_csv(ART_DIR / "cross_market_skipped.csv", index=False)

    # 3) trend-filter vs no-filter summary
    grp = []
    for (asset, ticker, asset_class, freq), g in res_df.groupby(["asset", "ticker", "asset_class", "freq"], as_index=False):
        u = g[g["group"] == "unfiltered"]
        f = g[g["group"] == "filtered"]
        if u.empty or f.empty:
            continue
        best_u = u.loc[u["profit_pct"].idxmax()]
        best_f = f.loc[f["profit_pct"].idxmax()]
        grp.append(
            {
                "asset": asset,
                "ticker": ticker,
                "asset_class": asset_class,
                "freq": freq,
                "best_unfiltered_strategy": best_u["strategy"],
                "best_unfiltered_pp": best_u["profit_pct"],
                "best_filtered_strategy": best_f["strategy"],
                "best_filtered_pp": best_f["profit_pct"],
                "delta_filtered_minus_unfiltered": best_f["profit_pct"] - best_u["profit_pct"],
            }
        )

    pair_df = pd.DataFrame(grp)
    pair_df.to_csv(ART_DIR / "trend_filter_compare_pairs.csv", index=False)
    make_filter_compare_chart(pair_df, ART_DIR / "trend_filter_compare_scatter.png")
    make_delta_heatmap(pair_df, ART_DIR / "trend_filter_delta_heatmap.png")

    # Class/freq summary
    summary_df = (
        pair_df.groupby(["asset_class", "freq"], as_index=False)
        .agg(
            n=("asset", "count"),
            median_unfiltered_pp=("best_unfiltered_pp", "median"),
            median_filtered_pp=("best_filtered_pp", "median"),
            median_delta=("delta_filtered_minus_unfiltered", "median"),
            mean_delta=("delta_filtered_minus_unfiltered", "mean"),
        )
        .sort_values(["asset_class", "freq"])
    )
    summary_df.to_csv(ART_DIR / "trend_filter_summary_by_class_freq.csv", index=False)

    # 4) HTML report
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    paper_tbl = paper_df.copy()
    for c in ["profit_pct", "np_pct", "cagr_pct", "max_dd_pct"]:
        paper_tbl[c] = paper_tbl[c].map(fmt_pct)
    paper_tbl["nt"] = paper_tbl["nt"].map(lambda x: f"{int(x)}")

    claim_tbl = claim_compare_df.copy()
    for c in ["paper_claim_pp", "reproduced_pp", "pp_diff_repro_minus_claim"]:
        claim_tbl[c] = claim_tbl[c].map(fmt_pct)
    claim_tbl["reproduced_nt"] = claim_tbl["reproduced_nt"].map(lambda x: f"{int(x)}")

    summary_tbl = summary_df.copy()
    for c in ["median_unfiltered_pp", "median_filtered_pp", "median_delta", "mean_delta"]:
        summary_tbl[c] = summary_tbl[c].map(fmt_pct)
    summary_tbl["n"] = summary_tbl["n"].map(lambda x: f"{int(x)}")

    pair_tbl = pair_df.copy()
    for c in ["best_unfiltered_pp", "best_filtered_pp", "delta_filtered_minus_unfiltered"]:
        pair_tbl[c] = pair_tbl[c].map(fmt_pct)

    top_helped = pair_df.sort_values("delta_filtered_minus_unfiltered", ascending=False).head(6).copy()
    top_hurt = pair_df.sort_values("delta_filtered_minus_unfiltered", ascending=True).head(6).copy()
    for df_ in [top_helped, top_hurt]:
        for c in ["best_unfiltered_pp", "best_filtered_pp", "delta_filtered_minus_unfiltered"]:
            df_[c] = df_[c].map(fmt_pct)

    skipped_df = pd.DataFrame(skipped)

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Regime Switch Indicator Stack 论文复现回测报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1260px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; }}
    .muted {{ color:#475569; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    .warn {{ color:#92400e; background:#fffbeb; border:1px solid #fcd34d; border-radius:10px; padding:10px 12px; }}
    ul,ol {{ padding-left: 20px; }}
    img {{ max-width:100%; border:1px solid #e2e8f0; border-radius:10px; }}
    .data-table {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .data-table th,.data-table td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    code {{ background:#f1f5f9; padding:1px 4px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
<div class=\"wrap\">
  <p><a href=\"../../index.html\">← 返回首页</a></p>

  <div class=\"card\">
    <h1>Regime Switch Indicator Stack · 论文复现回测报告</h1>
    <p class=\"muted\">生成时间：{generated_at}</p>
    <p>
      <span class=\"pill\">paper replication</span>
      <span class=\"pill\">MIHS / MIHCS</span>
      <span class=\"pill\">跨市场</span>
      <span class=\"pill\">多频率</span>
    </p>
    <p class=\"muted\">
      复现对象：Naganjaneyulu et al. (2023), <i>Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm</i>。
      本报告先按论文中可明确提取的规则做 faithful clean-room 复现，再扩展到加密+美股+A股、日频/周频/小时频，比较“趋势筛选前后”的收益差异。
    </p>
  </div>

  <div class=\"card\">
    <h2>这次实现了什么（规则口径）</h2>
    <ul>
      <li><b>四个单指标策略（未做趋势筛选）</b>：EMA(9/20)、BB(21,2)、RSI(40/60)、PSAR(0.02~0.2)。</li>
      <li><b>四个原型（做趋势筛选）</b>：MIHS9、MIHS7、MIHCS9、MIHCS7。</li>
      <li>Regime 定义：<code>EMA(RSI) > 60</code> 视为 Uptrend；<code>&lt; 40</code> 视为 Downtrend；其余视为 Fluctuating。</li>
      <li>MIHCS 的核心约束：在 Downtrend / Fluctuating 分支忽略 BUY（仅保留保护性 SELL / HOLD）。</li>
      <li>回测执行：long-only、单仓位、信号按当根 close 执行、期末若仍持仓按最后 close 平仓（与论文叙述口径一致）。</li>
    </ul>
    <p class=\"warn\"><b>重要：</b>论文页中个别公式以图片形式给出，文本不可直接复制；本实现基于原文文字定义 + flowchart OCR 重建，属于 faithful clean-room replication，而非作者原始代码逐行复刻。</p>
  </div>

  <div class=\"card\">
    <h2>1) BTC 日频 2018-2022（论文窗口）复现实验</h2>
    {build_table_html(paper_tbl, ["strategy", "profit_pct", "np_pct", "nt", "cagr_pct", "max_dd_pct"])}
    <p class=\"muted\">指标含义：PP=Profit Percentage；NP=盈利交易占比；NT=完成的 BUY→SELL 交易数。</p>
    <p><img src=\"../../../artifacts/regime_switch_indicator_stack_replication/paper_profit_bar.png\" alt=\"paper profit bar\" /></p>
    <p><img src=\"../../../artifacts/regime_switch_indicator_stack_replication/paper_equity_curves.png\" alt=\"paper equity curves\" /></p>
  </div>

  <div class=\"card\">
    <h2>2) 论文声称值 vs clean-room 复现值</h2>
    {build_table_html(claim_tbl, ["strategy", "paper_claim_pp", "reproduced_pp", "pp_diff_repro_minus_claim", "reproduced_nt"])}
    <p><img src=\"../../../artifacts/regime_switch_indicator_stack_replication/paper_claim_compare.png\" alt=\"paper claim compare\" /></p>
    <ul>
      <li><b>EMA / BB / RSI</b> 的复现值和论文比较接近，说明基础单指标部分大体对上了。</li>
      <li><b>分层原型差异更大</b>：我们的 MIHCS 明显更强，MIHS 明显更弱，提示 flowchart 里某些细节、执行假设、或作者代码实现细节很可能对结果有较大影响。</li>
      <li>因此这份报告更应该读成：<b>论文思想可复现，但具体数值对实现细节敏感</b>。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>3) 多资产×多频率：趋势筛选前后收益</h2>
    <p class=\"muted\">比较口径：每个“资产×频率”先取四个未筛选策略中的最佳 PP，再取四个筛选原型中的最佳 PP，比较两者差值。</p>
    {build_table_html(summary_tbl, ["asset_class", "freq", "n", "median_unfiltered_pp", "median_filtered_pp", "median_delta", "mean_delta"])}
    <p><img src=\"../../../artifacts/regime_switch_indicator_stack_replication/trend_filter_compare_scatter.png\" alt=\"trend filter compare\" /></p>
    <p><img src=\"../../../artifacts/regime_switch_indicator_stack_replication/trend_filter_delta_heatmap.png\" alt=\"trend filter heatmap\" /></p>
    <ul>
      <li>散点图在对角线上方，表示筛选后更强；下方则表示未筛选更强。</li>
      <li>热力图更适合看单个资产：绿色越深，表示 regime gate 帮助越大；红色越深，表示 gate 拖累越明显。</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>4) 哪些地方被趋势筛选明显帮到 / 拖累</h2>
    <h3>帮助最大的样本</h3>
    {build_table_html(top_helped, ["asset", "asset_class", "freq", "best_unfiltered_strategy", "best_unfiltered_pp", "best_filtered_strategy", "best_filtered_pp", "delta_filtered_minus_unfiltered"])}
    <h3>拖累最大的样本</h3>
    {build_table_html(top_hurt, ["asset", "asset_class", "freq", "best_unfiltered_strategy", "best_unfiltered_pp", "best_filtered_strategy", "best_filtered_pp", "delta_filtered_minus_unfiltered"])}
  </div>

  <div class=\"card\">
    <h2>5) 分资产明细（最佳未筛选 vs 最佳筛选）</h2>
    {build_table_html(pair_tbl, ["asset", "ticker", "asset_class", "freq", "best_unfiltered_strategy", "best_unfiltered_pp", "best_filtered_strategy", "best_filtered_pp", "delta_filtered_minus_unfiltered"])}
  </div>

  <div class=\"card\">
    <h2>6) 结论（可直接用于策略讨论）</h2>
    <ol>
      <li><b>这篇论文最稳定可迁移的，不是某个固定参数，而是 regime gate 思想本身</b>：先判断 Uptrend / Downtrend / Fluctuating，再决定是否允许交易。</li>
      <li><b>但它并不是跨市场通吃 alpha</b>。在这次扩展回测里，趋势筛选在 A 股更容易提供帮助；在强趋势 Crypto 日频/周频里，直接的 EMA / PSAR 往往已经非常强，gate 反而可能过度约束。</li>
      <li><b>MIHCS 比 MIHS 更像可用的风险控制层</b>：忽略非理想状态下的 BUY，代价是牺牲部分反弹/震荡利润，换来更保守的路径。</li>
      <li>因此从你当前“找靠谱 alpha”的目标看，<b>更合理的定位是把它作为 filter / gate / risk policy 候选</b>，先去管 breakout / retest / trend-following 规则什么时候允许出手，而不是直接把 MIHCS7 当成最终 alpha 本体。</li>
    </ol>
  </div>

  <div class=\"card\">
    <h2>7) 复现产物</h2>
    <ul>
      <li><code>reports/artifacts/regime_switch_indicator_stack_replication/paper_window_btc_2018_2022_metrics.csv</code></li>
      <li><code>reports/artifacts/regime_switch_indicator_stack_replication/cross_market_results.csv</code></li>
      <li><code>reports/artifacts/regime_switch_indicator_stack_replication/trend_filter_compare_pairs.csv</code></li>
      <li><code>reports/artifacts/regime_switch_indicator_stack_replication/trend_filter_summary_by_class_freq.csv</code></li>
      <li><code>reports/artifacts/regime_switch_indicator_stack_replication/cross_market_skipped.csv</code>（数据源缺失或频率不支持）</li>
    </ul>
  </div>

  <div class=\"card\">
    <h2>8) 下一步（若要纳入因子库）</h2>
    <ol>
      <li>把最优原型固定为候选门控层（建议先从 MIHCS7 开始），与当前 breakout/retest/confirmation 事件层耦合。</li>
      <li>加入成本与滑点敏感性（当前报告按论文口径未扣交易成本）。</li>
      <li>做 rolling / OOS / 子市场稳健性复验，避免单窗口偶然性。</li>
    </ol>
  </div>

  <div class=\"card\">
    <p class=\"muted\">参考：<a href=\"../quant_digests/2026-03-14_0128_regime-switch-indicator-stack.html\">原始 digest 页面</a></p>
  </div>
</div>
</body>
</html>
"""

    SITE_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] report generated: {SITE_PATH}")
    print(f"[ok] artifacts dir: {ART_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
