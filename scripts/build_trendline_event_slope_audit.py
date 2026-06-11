#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

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
from momentum.analytics.trendline_segment_backtest import (  # noqa: E402
    TrendlineSegmentEventConfig,
    evaluate_trendline_segment_strategy,
)
from momentum.analytics.multi_tf_momentum_backtest import MultiTfMomentumBacktestConfig  # noqa: E402

ARTIFACTS = ROOT / "reports" / "artifacts" / "trendline_event_slope_audit"
SITE = ROOT / "reports" / "site" / "factors" / "trendline_event_slope_audit"

SYMBOLS = {
    "BTC-USD": {"market": "crypto", "bucket": "major"},
    "ETH-USD": {"market": "crypto", "bucket": "major"},
    "SOL-USD": {"market": "crypto", "bucket": "major"},
    "BNB-USD": {"market": "crypto", "bucket": "major"},
    "XRP-USD": {"market": "crypto", "bucket": "alt"},
    "DOGE-USD": {"market": "crypto", "bucket": "alt"},
    "ADA-USD": {"market": "crypto", "bucket": "alt"},
    "AVAX-USD": {"market": "crypto", "bucket": "alt"},
}
SAMPLES = [
    {"sample_key": "30m_60d", "interval": "30m", "period": "60d", "label": "30m / 60d quick scan", "note": "Yahoo 限制下的低周期快筛"},
    {"sample_key": "60m_60d", "interval": "60m", "period": "60d", "label": "60m / 60d quick scan", "note": "与首轮快筛保持同口径的基线"},
    {"sample_key": "60m_365d", "interval": "60m", "period": "365d", "label": "60m / 365d long sample", "note": "1 年样本复核"},
    {"sample_key": "60m_730d", "interval": "60m", "period": "730d", "label": "60m / 730d long sample", "note": "2 年样本复核"},
]


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


def load_multi_symbol_data(sample: dict) -> pd.DataFrame:
    interval = str(sample["interval"])
    period = str(sample["period"])
    parts: list[pd.DataFrame] = []
    for ticker, info in SYMBOLS.items():
        bars = download_bars(ticker=ticker, period=period, interval=interval)
        bars["symbol"] = ticker
        bars["market"] = info["market"]
        bars["bucket"] = info["bucket"]
        parts.append(bars)
        print(f"downloaded {ticker} sample={sample['sample_key']} rows={len(bars)}")
    return pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def render_table(df: pd.DataFrame, max_rows: int = 120) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def _bucket_mag(series: pd.Series) -> tuple[pd.Series, float, float]:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    q1 = float(s.quantile(0.33)) if len(s) else 0.0
    q2 = float(s.quantile(0.66)) if len(s) else 0.0

    def _label(v: float) -> str:
        if v <= q1:
            return "low"
        if v <= q2:
            return "mid"
        return "high"

    return s.map(_label), q1, q2


def attach_slope_metadata(trades: pd.DataFrame, segments: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    empty_threshold_cols = ["sample_key", "interval", "period", "timeframe", "event_type", "flat_threshold", "mag_q33", "mag_q66", "trades"]
    if trades.empty:
        return trades.copy(), pd.DataFrame(columns=empty_threshold_cols)

    seg = segments.copy()
    seg = seg.rename(columns={"timeframe": "segment_timeframe"})
    seg["timeframe"] = seg["segment_timeframe"].astype(str).str.replace("tbn_", "", regex=False)
    keep = [
        "symbol",
        "timeframe",
        "segment_id",
        "side_label",
        "slope",
        "anchor_price",
        "pivot_price",
        "bars_visible",
        "is_provisional",
        "end_reason",
    ]
    seg = seg[keep].drop_duplicates(subset=["symbol", "timeframe", "segment_id"]).reset_index(drop=True)

    out = trades.merge(seg, on=["symbol", "timeframe", "segment_id"], how="left", suffixes=("", "_segment"))
    out["slope_pct_per_bar"] = out["slope"] / out["anchor_price"].abs().replace(0, np.nan)
    out["abs_slope_pct_per_bar"] = out["slope_pct_per_bar"].abs()

    threshold_rows: list[dict] = []
    bucketed_parts: list[pd.DataFrame] = []

    for keys, g in out.groupby(["sample_key", "interval", "period", "timeframe", "event_type"], dropna=False, sort=True):
        sample_key, interval, period, timeframe, event_type = keys
        part = g.copy()
        abs_s = pd.to_numeric(part["abs_slope_pct_per_bar"], errors="coerce").fillna(0.0)
        flat_threshold = float(abs_s.quantile(0.20)) if len(abs_s) else 0.0
        mag_labels, q1, q2 = _bucket_mag(abs_s)
        part["slope_magnitude_bucket"] = mag_labels
        part["slope_sign"] = np.where(
            abs_s <= flat_threshold,
            "flat",
            np.where(pd.to_numeric(part["slope_pct_per_bar"], errors="coerce").fillna(0.0) > 0, "up", "down"),
        )
        part["slope_bucket"] = np.where(part["slope_sign"] == "flat", "flat", part["slope_sign"] + "_" + part["slope_magnitude_bucket"])
        bucketed_parts.append(part)
        threshold_rows.append(
            {
                "sample_key": sample_key,
                "interval": interval,
                "period": period,
                "timeframe": timeframe,
                "event_type": event_type,
                "flat_threshold": flat_threshold,
                "mag_q33": q1,
                "mag_q66": q2,
                "trades": int(len(part)),
            }
        )

    out = pd.concat(bucketed_parts, ignore_index=True) if bucketed_parts else out
    return out, pd.DataFrame(threshold_rows)


def build_symbol_bucket_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    group_cols = ["sample_key", "interval", "period", "timeframe", "event_type", "slope_sign", "slope_bucket", "symbol"]
    grp = (
        trades.groupby(group_cols, dropna=False)
        .agg(
            trades=("net_ret", "size"),
            win_rate=("win", "mean"),
            avg_ret=("net_ret", "mean"),
            median_ret=("net_ret", "median"),
        )
        .reset_index()
    )
    total_return = (
        trades.groupby(group_cols, dropna=False)["net_ret"]
        .apply(lambda s: float((1.0 + pd.Series(s)).prod() - 1.0))
        .reset_index(name="total_return")
    )
    grp = grp.merge(total_return, on=group_cols, how="left")
    grp["positive_symbol"] = (grp["total_return"] > 0).astype(int)
    return grp.sort_values(["sample_key", "timeframe", "event_type", "slope_bucket", "symbol"]).reset_index(drop=True)


def build_bucket_summary(symbol_bucket: pd.DataFrame) -> pd.DataFrame:
    if symbol_bucket.empty:
        return pd.DataFrame()
    group_cols = ["sample_key", "interval", "period", "timeframe", "event_type", "slope_sign", "slope_bucket"]
    grp = (
        symbol_bucket.groupby(group_cols, dropna=False)
        .agg(
            assets=("symbol", "nunique"),
            total_trades=("trades", "sum"),
            positive_assets=("positive_symbol", "sum"),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            min_total_return=("total_return", "min"),
            max_total_return=("total_return", "max"),
            mean_avg_trade_ret=("avg_ret", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
        .reset_index()
    )
    grp["positive_asset_ratio"] = grp["positive_assets"] / grp["assets"].replace(0, np.nan)
    return grp.sort_values(["sample_key", "timeframe", "event_type", "slope_bucket"]).reset_index(drop=True)


def build_verdicts(bucket_summary: pd.DataFrame) -> pd.DataFrame:
    if bucket_summary.empty:
        return pd.DataFrame()
    core = bucket_summary[(bucket_summary["timeframe"] == "long") & (bucket_summary["event_type"].isin(["breakout_long", "rebound_long"]))].copy()
    if core.empty:
        return core

    decisions: list[str] = []
    reasons: list[str] = []
    for _, row in core.iterrows():
        assets = int(row["assets"])
        trades = int(row["total_trades"])
        par = float(row["positive_asset_ratio"]) if pd.notna(row["positive_asset_ratio"]) else 0.0
        mean_ret = float(row["mean_total_return"]) if pd.notna(row["mean_total_return"]) else -1.0
        if trades < 12 or assets < 3:
            decisions.append("too_thin")
            reasons.append("样本太薄，先不下 go/no-go 结论")
        elif par >= 0.60 and mean_ret > 0:
            decisions.append("continue")
            reasons.append("正收益资产占比和平均收益都过线，可继续深挖")
        elif par >= 0.40 and mean_ret > 0:
            decisions.append("continue_only_in_subset")
            reasons.append("只在部分 slope bucket 里像样，适合收缩成子集")
        else:
            decisions.append("park")
            reasons.append("跨资产胜率/收益不够，倾向 park 掉")
    core["suggested_action"] = decisions
    core["reason"] = reasons
    return core.sort_values(["event_type", "sample_key", "mean_total_return"], ascending=[True, True, False]).reset_index(drop=True)


def _sample_meta_rows() -> pd.DataFrame:
    return pd.DataFrame(SAMPLES)[["sample_key", "interval", "period", "label", "note"]]


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

    sample_meta: list[dict] = []
    all_trades: list[pd.DataFrame] = []

    for sample in SAMPLES:
        sample_key = str(sample["sample_key"])
        interval = str(sample["interval"])
        period = str(sample["period"])
        bars = load_multi_symbol_data(sample)
        nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
        nav = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
        segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)
        result = evaluate_trendline_segment_strategy(nav, segments, event_config=event_cfg, backtest_config=bt_cfg)

        if not result.trades.empty:
            trades = result.trades.copy()
            trades["sample_key"] = sample_key
            trades["interval"] = interval
            trades["period"] = period
            trades["market"] = trades["symbol"].map(lambda s: SYMBOLS.get(str(s), {}).get("market", "unknown"))
            trades["bucket"] = trades["symbol"].map(lambda s: SYMBOLS.get(str(s), {}).get("bucket", "unknown"))
            trades, thresholds = attach_slope_metadata(trades, segments.assign(symbol=segments.get("symbol", "ALL")))
            thresholds.to_csv(ARTIFACTS / f"slope_thresholds_{sample_key}.csv", index=False)
            all_trades.append(trades)
        sample_meta.append(
            {
                "sample_key": sample_key,
                "interval": interval,
                "period": period,
                "label": sample["label"],
                "note": sample["note"],
                "symbols": int(bars["symbol"].nunique()),
                "rows": int(len(bars)),
                "segment_count": int(len(segments)),
                "event_count": int(len(result.events)),
                "trade_count": int(len(result.trades)),
            }
        )
        print(f"done sample={sample_key} interval={interval} period={period} trades={len(result.trades)}")

    sample_meta_df = pd.DataFrame(sample_meta)
    trades_all = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    symbol_bucket = build_symbol_bucket_summary(trades_all)
    bucket_summary = build_bucket_summary(symbol_bucket)
    verdicts = build_verdicts(bucket_summary)
    core = bucket_summary[(bucket_summary["timeframe"] == "long") & (bucket_summary["event_type"].isin(["breakout_long", "rebound_long"]))].copy() if not bucket_summary.empty else pd.DataFrame()
    support = bucket_summary[~((bucket_summary["timeframe"] == "long") & (bucket_summary["event_type"].isin(["breakout_long", "rebound_long"])))].copy() if not bucket_summary.empty else pd.DataFrame()
    long_focus = verdicts[verdicts["sample_key"].isin(["60m_365d", "60m_730d"])].copy() if not verdicts.empty else pd.DataFrame()
    long_focus_symbol = symbol_bucket[
        (symbol_bucket["sample_key"].isin(["60m_365d", "60m_730d"]))
        & (symbol_bucket["timeframe"] == "long")
        & (symbol_bucket["event_type"].isin(["breakout_long", "rebound_long"]))
    ].copy() if not symbol_bucket.empty else pd.DataFrame()

    sample_meta_df.to_csv(ARTIFACTS / "sample_meta.csv", index=False)
    trades_all.to_csv(ARTIFACTS / "trade_detail.csv", index=False)
    symbol_bucket.to_csv(ARTIFACTS / "symbol_slope_summary.csv", index=False)
    bucket_summary.to_csv(ARTIFACTS / "slope_bucket_summary.csv", index=False)
    verdicts.to_csv(ARTIFACTS / "core_verdicts.csv", index=False)
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "symbols": list(SYMBOLS.keys()),
                "samples": SAMPLES,
                "regime_filter_medium_short": True,
                "enable_atr_trailing_stop": True,
                "atr_period": 14,
                "atr_trailing_mult": 2.5,
                "total_trades": int(len(trades_all)),
                "total_symbol_slope_cells": int(len(symbol_bucket)),
                "total_bucket_cells": int(len(bucket_summary)),
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
  <title>Trendline Event Slope Audit</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1320px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card'>
    <h1>Trendline Event Slope Audit · crypto quick + long sample</h1>
    <p class='muted'>目的不是继续盲目救 breakout，而是做一次 <b>close-or-continue</b> 审计：在复用 Round A/B/C 逻辑的前提下，看不同 <b>slope bucket</b> 是否真的显著影响结构事件结果。</p>
    <p class='muted'><span class='pill'>scope</span> 8 个 crypto 资产（BTC / ETH / SOL / BNB / XRP / DOGE / ADA / AVAX）<span class='pill'>samples</span> quick scan + 1Y + 2Y</p>
    <p class='muted'><span class='pill'>important</span> Yahoo 对 30m 有最近 60d 限制；所以长样本复核会重点看 <b>60m / 365d</b> 和 <b>60m / 730d</b>。</p>
    <p class='muted'><span class='pill'>bucket rule</span> 使用 <code>slope_pct_per_bar = slope / |anchor_price|</code> 做跨资产标准化；每个 <code>sample_key × timeframe × event_type</code> 内，用绝对斜率的 20% 分位数定义 <b>flat</b>，再把其余样本切成 <b>low / mid / high</b> 三档。</p>
  </div>

  <div class='card'>
    <h2>How to read this page</h2>
    <ul>
      <li>这页是 <b>策略层 slope 审计</b>，不是原始 event study；它复用了当前 Round A/B/C 的 entry / regime filter / ATR trailing stop 口径。</li>
      <li>优先看 <b>1Y / 2Y focus verdicts</b>：只看 <code>breakout_long</code> / <code>rebound_long</code> 且 timeframe=long。</li>
      <li>如果长样本里 trade count 明显上来，而某个 bucket 仍然过不了 <code>positive_asset_ratio</code> 与 <code>mean_total_return</code>，那就更接近真的该 park。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Sample meta</h2>
    {render_table(sample_meta_df, max_rows=20)}
  </div>

  <div class='card'>
    <h2>1Y / 2Y focus verdicts · long timeframe + long-side event types</h2>
    <p class='muted'>这里专门看长样本复核：<code>60m_365d</code> 与 <code>60m_730d</code>。<code>suggested_action</code> 是启发式建议：<b>continue / continue_only_in_subset / park / too_thin</b>。</p>
    {render_table(long_focus, max_rows=120)}
  </div>

  <div class='card'>
    <h2>All core verdicts · quick scan + long sample</h2>
    {render_table(verdicts, max_rows=180)}
  </div>

  <div class='card'>
    <h2>Core slope bucket summary</h2>
    {render_table(core, max_rows=220)}
  </div>

  <div class='card'>
    <h2>Long-sample symbol drill-down</h2>
    <p class='muted'>这张表更适合回答：长样本里某个 promising bucket 的结果是不是只被少数币种撑起来。</p>
    {render_table(long_focus_symbol, max_rows=240)}
  </div>

  <div class='card'>
    <h2>Supporting only · all other timeframes / event types</h2>
    {render_table(support, max_rows=260)}
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/trendline_event_slope_audit/sample_meta.csv'>sample_meta.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/trade_detail.csv'>trade_detail.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/symbol_slope_summary.csv'>symbol_slope_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/slope_bucket_summary.csv'>slope_bucket_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/core_verdicts.csv'>core_verdicts.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/slope_thresholds_30m_60d.csv'>slope_thresholds_30m_60d.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/slope_thresholds_60m_60d.csv'>slope_thresholds_60m_60d.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/slope_thresholds_60m_365d.csv'>slope_thresholds_60m_365d.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/slope_thresholds_60m_730d.csv'>slope_thresholds_60m_730d.csv</a></li>
      <li><a href='../../artifacts/trendline_event_slope_audit/summary.json'>summary.json</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""

    (SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"Wrote report to {SITE / 'report.html'}")


if __name__ == "__main__":
    main()
