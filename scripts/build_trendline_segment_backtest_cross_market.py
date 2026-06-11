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

ARTIFACTS = ROOT / "reports" / "artifacts" / "trendline_segment_backtest_cross_market"
SITE = ROOT / "reports" / "site" / "factors" / "trendline_segment_backtest_cross_market"

SYMBOLS = {
    "BTC-USD": {"market": "crypto", "bucket": "crypto_major"},
    "ETH-USD": {"market": "crypto", "bucket": "crypto_major"},
    "SOL-USD": {"market": "crypto", "bucket": "crypto_major"},
    "XRP-USD": {"market": "crypto", "bucket": "crypto_major"},
    "LINK-USD": {"market": "crypto", "bucket": "crypto_alt"},
    "ARB-USD": {"market": "crypto", "bucket": "crypto_alt"},
    "OP-USD": {"market": "crypto", "bucket": "crypto_alt"},
    "AAVE-USD": {"market": "crypto", "bucket": "crypto_alt"},
    "SPY": {"market": "us", "bucket": "us_etf"},
    "QQQ": {"market": "us", "bucket": "us_etf"},
    "AAPL": {"market": "us", "bucket": "us_stock"},
    "NVDA": {"market": "us", "bucket": "us_stock"},
    "AMD": {"market": "us", "bucket": "us_stock"},
    "0700.HK": {"market": "hk", "bucket": "hk_stock"},
    "9988.HK": {"market": "hk", "bucket": "hk_stock"},
    "3690.HK": {"market": "hk", "bucket": "hk_stock"},
    "1810.HK": {"market": "hk", "bucket": "hk_stock"},
    "600519.SS": {"market": "cn", "bucket": "cn_stock"},
    "300750.SZ": {"market": "cn", "bucket": "cn_stock"},
    "601318.SS": {"market": "cn", "bucket": "cn_stock"},
    "002594.SZ": {"market": "cn", "bucket": "cn_stock"},
}
PERIOD = "365d"
INTERVAL = "60m"


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


def render_table(df: pd.DataFrame, max_rows: int = 100) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def build_asset_summary(summary: pd.DataFrame) -> pd.DataFrame:
    grp = (
        summary.groupby(["strategy", "timeframe"], dropna=False)
        .agg(
            assets=("symbol", "nunique"),
            positive_assets=("total_return", lambda s: int((pd.Series(s) > 0).sum())),
            total_trades=("trades", "sum"),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            min_total_return=("total_return", "min"),
            max_total_return=("total_return", "max"),
            mean_max_drawdown=("max_drawdown", "mean"),
        )
        .reset_index()
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets"].replace(0, pd.NA)
    return grp


def build_market_summary(summary: pd.DataFrame) -> pd.DataFrame:
    grp = (
        summary.groupby(["market", "strategy", "timeframe"], dropna=False)
        .agg(
            assets=("symbol", "nunique"),
            positive_assets=("total_return", lambda s: int((pd.Series(s) > 0).sum())),
            total_trades=("trades", "sum"),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_max_drawdown=("max_drawdown", "mean"),
        )
        .reset_index()
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets"].replace(0, pd.NA)
    return grp


def main() -> None:
    ensure_dir(ARTIFACTS)
    ensure_dir(SITE)

    parts: list[pd.DataFrame] = []
    meta_rows: list[dict] = []
    for symbol, info in SYMBOLS.items():
        bars = download_bars(symbol, PERIOD, INTERVAL)
        bars["symbol"] = symbol
        bars["market"] = info["market"]
        bars["bucket"] = info["bucket"]
        parts.append(bars)
        meta_rows.append({"symbol": symbol, "market": info["market"], "bucket": info["bucket"], "rows": int(len(bars))})
        print(f"downloaded {symbol} rows={len(bars)}")

    bars = pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)

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

    nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
    nav = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
    segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)
    result = evaluate_trendline_segment_strategy(nav, segments, event_config=event_cfg, backtest_config=bt_cfg)

    summary = result.summary.copy()
    summary["market"] = summary["symbol"].map(lambda s: SYMBOLS.get(str(s), {}).get("market", "unknown"))
    summary["bucket"] = summary["symbol"].map(lambda s: SYMBOLS.get(str(s), {}).get("bucket", "unknown"))
    summary = summary[[c for c in ["market", "bucket", "strategy", "timeframe", "symbol", "trades", "win_rate", "avg_ret", "median_ret", "total_return", "max_drawdown", "long_trades", "short_trades"] if c in summary.columns]]

    asset_summary = build_asset_summary(summary)
    market_summary = build_market_summary(summary)
    core_all = asset_summary[(asset_summary["timeframe"] == "long") & (asset_summary["strategy"].isin(["breakout", "rebound"]))].copy()
    core_by_market = market_summary[(market_summary["timeframe"] == "long") & (market_summary["strategy"].isin(["breakout", "rebound"]))].copy()
    meta_df = pd.DataFrame(meta_rows)

    meta_df.to_csv(ARTIFACTS / "universe_meta.csv", index=False)
    summary.to_csv(ARTIFACTS / "cross_market_symbol_summary.csv", index=False)
    asset_summary.to_csv(ARTIFACTS / "cross_market_asset_summary.csv", index=False)
    market_summary.to_csv(ARTIFACTS / "cross_market_market_summary.csv", index=False)
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "period": PERIOD,
                "interval": INTERVAL,
                "symbols": list(SYMBOLS.keys()),
                "symbol_count": len(SYMBOLS),
                "regime_filter_medium_short": True,
                "enable_atr_trailing_stop": True,
                "atr_period": 14,
                "atr_trailing_mult": 2.5,
                "event_count": int(len(result.events)),
                "trade_count": int(len(result.trades)),
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
  <title>Trendline Segment Backtest Cross-Market</title>
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
    <h1>Trendline Segment Backtest · Cross-Market 365d / 1h</h1>
    <p class='muted'>同一套优化逻辑：Round A（核心看 long）、Round B（medium/short higher-timeframe regime filter）、Round C（ATR trailing stop）。</p>
    <p class='muted'>样本宇宙：Crypto + 美股 + 港股 + A股，共 <b>{len(SYMBOLS)}</b> 个标的。</p>
    <p class='muted'>说明：因为数据源限制，这次跨市场长样本统一用 <b>365d / 1h</b> 做对照。</p>
  </div>

  <div class='card'>
    <h2>Universe meta</h2>
    {render_table(meta_df, max_rows=40)}
  </div>

  <div class='card'>
    <h2>Core conclusion · long timeframe only (all assets)</h2>
    {render_table(core_all, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Core conclusion · long timeframe by market</h2>
    {render_table(core_by_market, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Market summary · all strategies / all timeframes</h2>
    {render_table(market_summary, max_rows=80)}
  </div>

  <div class='card'>
    <h2>Full symbol summary</h2>
    {render_table(summary, max_rows=200)}
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/trendline_segment_backtest_cross_market/universe_meta.csv'>universe_meta.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_cross_market/cross_market_asset_summary.csv'>cross_market_asset_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_cross_market/cross_market_market_summary.csv'>cross_market_market_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_cross_market/cross_market_symbol_summary.csv'>cross_market_symbol_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_segment_backtest_cross_market/summary.json'>summary.json</a></li>
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
