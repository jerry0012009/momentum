#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

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
from momentum.analytics.trendline_segment_backtest import (  # noqa: E402
    TrendlineSegmentEventConfig,
    evaluate_trendline_segment_strategy,
)
from momentum.analytics.multi_tf_momentum_backtest import MultiTfMomentumBacktestConfig  # noqa: E402

ARTIFACTS = ROOT / "reports" / "artifacts" / "trendline_segment_backtest_interval_sweep"
SITE = ROOT / "reports" / "site" / "factors" / "trendline_segment_backtest_interval_sweep"

TICKERS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD", "AVAX-USD"]
INTERVAL_PERIODS = {
    "5m": "60d",
    "15m": "60d",
    "30m": "60d",
    "60m": "60d",
}


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
        raise ValueError(f"No data for {ticker} {period} {interval}")
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


def load_multi_symbol_data(interval: str, period: str) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for ticker in TICKERS:
        bars = download_bars(ticker=ticker, period=period, interval=interval)
        bars["symbol"] = ticker
        parts.append(bars)
    return pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def render_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def build_cross_asset_summary(summary: pd.DataFrame) -> pd.DataFrame:
    if summary is None or summary.empty or "symbol" not in summary.columns:
        return pd.DataFrame()
    grp = (
        summary.groupby(["interval", "strategy", "timeframe"], dropna=False)
        .agg(
            assets=("symbol", "nunique"),
            total_trades=("trades", "sum"),
            positive_assets=("total_return", lambda s: int((pd.Series(s) > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            min_total_return=("total_return", "min"),
            max_total_return=("total_return", "max"),
            mean_max_drawdown=("max_drawdown", "mean"),
        )
        .reset_index()
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets"].replace(0, pd.NA)
    return grp[[
        "interval", "strategy", "timeframe", "assets", "positive_assets", "positive_asset_ratio",
        "total_trades", "mean_total_return", "median_total_return", "min_total_return",
        "max_total_return", "mean_max_drawdown",
    ]]


def main() -> None:
    ensure_dir(ARTIFACTS)
    ensure_dir(SITE)

    nav_cfg = TrendlineBreakoutNavigatorConfig()
    event_cfg = TrendlineSegmentEventConfig(
        breakout_confirm_bars=3,
        rebound_confirm_bars=1,
        max_resolution_bars=12,
        only_final_segments=True,
        regime_filter_medium_short=True,
    )
    bt_cfg = MultiTfMomentumBacktestConfig(
        enable_atr_trailing_stop=True,
        atr_period=14,
        atr_trailing_mult=2.5,
    )

    all_summary: list[pd.DataFrame] = []
    interval_meta: list[dict] = []

    for interval, period in INTERVAL_PERIODS.items():
        bars = load_multi_symbol_data(interval=interval, period=period)
        nav = compute_trendline_breakout_navigator(bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy(), config=nav_cfg)
        segments = extract_trendline_breakout_segments(bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy(), config=nav_cfg)
        result = evaluate_trendline_segment_strategy(nav, segments, event_config=event_cfg, backtest_config=bt_cfg)
        summary = result.summary.copy()
        if not summary.empty:
            summary["interval"] = interval
            summary = summary[[c for c in ["interval", "strategy", "timeframe", "symbol", "trades", "win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "long_trades", "short_trades"] if c in summary.columns]]
            all_summary.append(summary)
        interval_meta.append(
            {
                "interval": interval,
                "period": period,
                "symbols": int(bars["symbol"].nunique()),
                "rows": int(len(bars)),
                "event_count": int(len(result.events)),
                "trade_count": int(len(result.trades)),
            }
        )
        print(f"done {interval} {period} rows={len(bars)} trades={len(result.trades)}")

    summary_all = pd.concat(all_summary, ignore_index=True) if all_summary else pd.DataFrame()
    cross_asset = build_cross_asset_summary(summary_all)
    core = cross_asset[(cross_asset["timeframe"] == "long") & (cross_asset["strategy"].isin(["breakout", "rebound"]))].copy() if not cross_asset.empty else pd.DataFrame()
    support = cross_asset[cross_asset["timeframe"].isin(["medium", "short"])].copy() if not cross_asset.empty else pd.DataFrame()
    interval_meta_df = pd.DataFrame(interval_meta)

    summary_all.to_csv(ARTIFACTS / "interval_strategy_summary.csv", index=False)
    cross_asset.to_csv(ARTIFACTS / "interval_cross_asset_summary.csv", index=False)
    interval_meta_df.to_csv(ARTIFACTS / "interval_meta.csv", index=False)
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "tickers": TICKERS,
                "interval_periods": INTERVAL_PERIODS,
                "regime_filter_medium_short": True,
                "enable_atr_trailing_stop": True,
                "atr_period": 14,
                "atr_trailing_mult": 2.5,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <title>Trendline Segment Backtest Interval Sweep</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1280px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card'>
    <h1>Trendline Segment Backtest · Interval Sweep</h1>
    <p class='muted'>在你当前优化版逻辑基础上做 interval sweep：Round A（核心只看 long）、Round B（medium/short higher-timeframe regime filter）、Round C（ATR trailing stop）。</p>
    <p class='muted'>样本：8 个主流币（BTC / ETH / SOL / BNB / XRP / ADA / DOGE / AVAX）</p>
  </div>

  <div class='card'>
    <h2>Interval meta</h2>
    {render_table(interval_meta_df, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Core conclusion · long timeframe only</h2>
    <p class='muted'>优先看 breakout-long / rebound-long。higher timeframe 是否更好，就看这里。</p>
    {render_table(core, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Supporting only · medium / short</h2>
    {render_table(support, max_rows=40)}
  </div>

  <div class='card'>
    <h2>Full interval × strategy × symbol summary</h2>
    {render_table(summary_all, max_rows=160)}
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/trendline_segment_backtest_interval_sweep/interval_meta.csv'>interval_meta.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_interval_sweep/interval_cross_asset_summary.csv'>interval_cross_asset_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_interval_sweep/interval_strategy_summary.csv'>interval_strategy_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_interval_sweep/summary.json'>summary.json</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""
    out = SITE / "report.html"
    out.write_text(html, encoding="utf-8")
    print(f"Wrote report to {out}")


if __name__ == "__main__":
    main()
