#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
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

ARTIFACTS = ROOT / "reports" / "artifacts" / "trendline_confirmation_ladder"
SITE = ROOT / "reports" / "site" / "factors" / "trendline_confirmation_ladder"
CACHE = ARTIFACTS / "cache"

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
    {"sample_key": "60m_365d", "interval": "60m", "period": "365d", "label": "60m / 365d", "note": "1 年样本复核"},
    {"sample_key": "60m_730d", "interval": "60m", "period": "730d", "label": "60m / 730d", "note": "2 年样本复核"},
]
BREAKOUT_LADDER = [
    {"ladder_label": "breakout_hold_1", "display_label": "breakout hold = 1", "breakout_confirm_bars": 1, "rebound_confirm_bars": 1, "note": "最宽松的 breakout 持续确认（当前实现里仍不是 raw breach）。"},
    {"ladder_label": "breakout_hold_2", "display_label": "breakout hold = 2", "breakout_confirm_bars": 2, "rebound_confirm_bars": 1, "note": "要求更长的线外持续性。"},
    {"ladder_label": "breakout_hold_3", "display_label": "breakout hold = 3", "breakout_confirm_bars": 3, "rebound_confirm_bars": 1, "note": "当前 baseline 常用口径。"},
    {"ladder_label": "breakout_hold_4", "display_label": "breakout hold = 4", "breakout_confirm_bars": 4, "rebound_confirm_bars": 1, "note": "更强确认，代价是样本数继续缩小。"},
]
REBOUND_LADDER = [
    {"ladder_label": "rebound_inside_0", "display_label": "rebound inside = 0", "breakout_confirm_bars": 3, "rebound_confirm_bars": 0, "note": "最宽松的 rebound 确认。"},
    {"ladder_label": "rebound_inside_1", "display_label": "rebound inside = 1", "breakout_confirm_bars": 3, "rebound_confirm_bars": 1, "note": "当前 baseline 常用口径。"},
    {"ladder_label": "rebound_inside_2", "display_label": "rebound inside = 2", "breakout_confirm_bars": 3, "rebound_confirm_bars": 2, "note": "要求更长的回到线内持续性。"},
    {"ladder_label": "rebound_inside_3", "display_label": "rebound inside = 3", "breakout_confirm_bars": 3, "rebound_confirm_bars": 3, "note": "最严格的 inside-hold 确认。"},
]
RETAINED_REBOUND_BUCKETS = ["flat", "down_high"]


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
    parts: list[pd.DataFrame] = []
    for ticker, info in SYMBOLS.items():
        bars = download_bars(ticker, sample["period"], sample["interval"])
        bars["symbol"] = ticker
        bars["market"] = info["market"]
        bars["bucket"] = info["bucket"]
        parts.append(bars)
        print(f"downloaded {ticker} sample={sample['sample_key']} rows={len(bars)}", flush=True)
    return pd.concat(parts, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def read_csv_cached(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in parse_dates or []:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    return df


def sample_cache_dir(sample: dict) -> Path:
    return ensure_dir(CACHE / sample["sample_key"])


def combo_cache_path(sample: dict, ladder_type: str, ladder_label: str) -> Path:
    return sample_cache_dir(sample) / f"trades__{ladder_type}__{ladder_label}.csv"


def combo_empty_marker_path(sample: dict, ladder_type: str, ladder_label: str) -> Path:
    return sample_cache_dir(sample) / f"trades__{ladder_type}__{ladder_label}.empty"


def load_or_build_sample_state(sample: dict, nav_cfg: TrendlineBreakoutNavigatorConfig) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cache_dir = sample_cache_dir(sample)
    bars_path = cache_dir / "bars.csv"
    nav_path = cache_dir / "nav.csv"
    segments_path = cache_dir / "segments.csv"

    if bars_path.exists() and nav_path.exists() and segments_path.exists():
        bars = read_csv_cached(bars_path, parse_dates=["timestamp"])
        nav = read_csv_cached(nav_path, parse_dates=["timestamp"])
        segments = read_csv_cached(
            segments_path,
            parse_dates=["start_timestamp", "end_timestamp", "anchor_timestamp", "pivot_timestamp", "computed_timestamp"],
        )
        print(f"resume sample={sample['sample_key']} from cache", flush=True)
        return bars, nav, segments

    bars = load_multi_symbol_data(sample)
    nav_input = bars[["timestamp", "symbol", "open", "high", "low", "close"]].copy()
    nav = compute_trendline_breakout_navigator(nav_input, config=nav_cfg)
    segments = extract_trendline_breakout_segments(nav_input, config=nav_cfg)

    bars.to_csv(bars_path, index=False)
    nav.to_csv(nav_path, index=False)
    segments.to_csv(segments_path, index=False)
    print(f"cached sample={sample['sample_key']} bars={len(bars)} nav={len(nav)} segments={len(segments)}", flush=True)
    return bars, nav, segments


def render_table(df: pd.DataFrame, max_rows: int = 120) -> str:
    if df is None or df.empty:
        return '<p class="muted">(empty)</p>'
    view = df.head(max_rows).copy()
    for c in view.columns:
        if pd.api.types.is_float_dtype(view[c]):
            view[c] = view[c].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return view.to_html(index=False, classes="tbl", border=0)


def pct(x: float | int | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{float(x) * 100:.2f}%"


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


def attach_slope_metadata(trades: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return trades.copy()
    seg = segments.copy().rename(columns={"timeframe": "segment_timeframe"})
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

    bucketed_parts: list[pd.DataFrame] = []
    for keys, g in out.groupby(["sample_key", "ladder_type", "timeframe", "event_type"], dropna=False, sort=True):
        part = g.copy()
        abs_s = pd.to_numeric(part["abs_slope_pct_per_bar"], errors="coerce").fillna(0.0)
        flat_threshold = float(abs_s.quantile(0.20)) if len(abs_s) else 0.0
        mag_labels, _, _ = _bucket_mag(abs_s)
        part["slope_magnitude_bucket"] = mag_labels
        part["slope_sign"] = np.where(
            abs_s <= flat_threshold,
            "flat",
            np.where(pd.to_numeric(part["slope_pct_per_bar"], errors="coerce").fillna(0.0) > 0, "up", "down"),
        )
        part["slope_bucket"] = np.where(part["slope_sign"] == "flat", "flat", part["slope_sign"] + "_" + part["slope_magnitude_bucket"])
        bucketed_parts.append(part)
    return pd.concat(bucketed_parts, ignore_index=True) if bucketed_parts else out


def summarize_symbol_level(trades: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    symbol_cols = group_cols + ["symbol"]
    grp = (
        trades.groupby(symbol_cols, dropna=False)
        .agg(
            trades=("net_ret", "size"),
            win_rate=("win", "mean"),
            avg_ret=("net_ret", "mean"),
            median_ret=("net_ret", "median"),
        )
        .reset_index()
    )
    total_return = (
        trades.groupby(symbol_cols, dropna=False)["net_ret"]
        .apply(lambda s: float((1.0 + pd.Series(s)).prod() - 1.0))
        .reset_index(name="total_return")
    )
    grp = grp.merge(total_return, on=symbol_cols, how="left")
    grp["positive_symbol"] = (grp["total_return"] > 0).astype(int)
    return grp.sort_values(symbol_cols).reset_index(drop=True)


def summarize_group_level(symbol_level: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if symbol_level.empty:
        return pd.DataFrame()
    grp = (
        symbol_level.groupby(group_cols, dropna=False)
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
    return grp.sort_values(group_cols).reset_index(drop=True)


def add_trade_retention(summary: pd.DataFrame, key_cols: list[str], ladder_col: str) -> pd.DataFrame:
    if summary.empty:
        return summary
    out = summary.copy()
    base = out.sort_values(ladder_col).groupby(key_cols, dropna=False)["total_trades"].transform("first")
    out["trade_retention_vs_first"] = out["total_trades"] / base.replace(0, np.nan)
    return out


def ladder_svg() -> str:
    return """
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-label="confirmation ladder diagram">
  <rect width="1200" height="320" fill="#ffffff" />
  <text x="30" y="42" font-size="28" font-family="system-ui, sans-serif" fill="#0f172a">Confirmation Ladder · conceptual view</text>
  <text x="30" y="72" font-size="16" font-family="system-ui, sans-serif" fill="#475569">不是每次碰线/越线都算同一个强度；我们要比较“多一层确认，值不值得”。</text>
  <g font-family="system-ui, sans-serif">
    <rect x="40" y="120" rx="16" ry="16" width="180" height="110" fill="#eff6ff" stroke="#93c5fd" />
    <text x="60" y="155" font-size="22" fill="#1d4ed8">raw / provisional</text>
    <text x="60" y="183" font-size="14" fill="#334155">刚碰线 / 刚越线</text>
    <text x="60" y="204" font-size="14" fill="#334155">样本最多，噪音也最多</text>

    <rect x="280" y="120" rx="16" ry="16" width="180" height="110" fill="#ecfeff" stroke="#67e8f9" />
    <text x="300" y="155" font-size="22" fill="#0f766e">confirm1</text>
    <text x="300" y="183" font-size="14" fill="#334155">再给一层 close / hold</text>
    <text x="300" y="204" font-size="14" fill="#334155">样本少一些，质量应更高</text>

    <rect x="520" y="120" rx="16" ry="16" width="180" height="110" fill="#fef3c7" stroke="#fcd34d" />
    <text x="540" y="155" font-size="22" fill="#92400e">confirm3</text>
    <text x="540" y="183" font-size="14" fill="#334155">持续性更强</text>
    <text x="540" y="204" font-size="14" fill="#334155">但会进一步损失样本</text>

    <rect x="760" y="120" rx="16" ry="16" width="180" height="110" fill="#f5f3ff" stroke="#c4b5fd" />
    <text x="780" y="155" font-size="22" fill="#6d28d9">retest_hold</text>
    <text x="780" y="183" font-size="14" fill="#334155">回踩后仍守住</text>
    <text x="780" y="204" font-size="14" fill="#334155">理论上更像真切换</text>

    <rect x="1000" y="120" rx="16" ry="16" width="160" height="110" fill="#f0fdf4" stroke="#86efac" />
    <text x="1020" y="155" font-size="22" fill="#166534">go / no-go</text>
    <text x="1020" y="183" font-size="14" fill="#334155">看收益质量是否提升</text>
    <text x="1020" y="204" font-size="14" fill="#334155">是否值得推进</text>

    <path d="M220 175 L280 175" stroke="#64748b" stroke-width="3" marker-end="url(#arrow)" />
    <path d="M460 175 L520 175" stroke="#64748b" stroke-width="3" marker-end="url(#arrow)" />
    <path d="M700 175 L760 175" stroke="#64748b" stroke-width="3" marker-end="url(#arrow)" />
    <path d="M940 175 L1000 175" stroke="#64748b" stroke-width="3" marker-end="url(#arrow)" />
  </g>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#64748b" />
    </marker>
  </defs>
</svg>
"""


def make_headline(breakout_summary: pd.DataFrame, rebound_subset_summary: pd.DataFrame) -> list[str]:
    lines: list[str] = []
    focus_breakout = breakout_summary[breakout_summary["sample_key"] == "60m_730d"].copy() if not breakout_summary.empty else pd.DataFrame()
    focus_rebound = rebound_subset_summary[
        (rebound_subset_summary["sample_key"] == "60m_730d")
        & (rebound_subset_summary["subset_group"] == "retained_union")
    ].copy() if not rebound_subset_summary.empty else pd.DataFrame()

    if not focus_breakout.empty:
        best_breakout = focus_breakout.sort_values(["positive_asset_ratio", "mean_total_return", "trade_retention_vs_first"], ascending=[False, False, False]).iloc[0]
        lines.append(
            f"2Y breakout 侧最像样的一档是 <b>{best_breakout['display_label']}</b>，但也只有 positive_asset_ratio={pct(best_breakout['positive_asset_ratio'])}、mean_total_return={pct(best_breakout['mean_total_return'])}，说明更强确认并没有真正把 breakout 救起来。"
        )

    if not focus_rebound.empty:
        best_rebound = focus_rebound.sort_values(["positive_asset_ratio", "mean_total_return", "trade_retention_vs_first"], ascending=[False, False, False]).iloc[0]
        lines.append(
            f"2Y retained rebound 子集（flat + down_high）里，当前最值得继续看的梯级是 <b>{best_rebound['display_label']}</b>：positive_asset_ratio={pct(best_rebound['positive_asset_ratio'])}、mean_total_return={pct(best_rebound['mean_total_return'])}、trade_retention={pct(best_rebound['trade_retention_vs_first'])}。"
        )

    if not lines:
        lines.append("当前样本还不足以给出强结论；这份报告的主要作用仍是把 confirmation ladder 的读法和下一步问题固定下来。")
    return lines


def main() -> None:
    ensure_dir(ARTIFACTS)
    ensure_dir(SITE)

    nav_cfg = TrendlineBreakoutNavigatorConfig()
    bt_cfg = MultiTfMomentumBacktestConfig(
        enable_atr_trailing_stop=True,
        atr_period=14,
        atr_trailing_mult=2.5,
    )

    ensure_dir(CACHE)
    sample_meta_rows: list[dict] = []
    ladder_trades: list[pd.DataFrame] = []

    for sample in SAMPLES:
        bars, nav, segments = load_or_build_sample_state(sample, nav_cfg)
        sample_meta_rows.append(
            {
                "sample_key": sample["sample_key"],
                "interval": sample["interval"],
                "period": sample["period"],
                "label": sample["label"],
                "note": sample["note"],
                "symbols": int(bars["symbol"].nunique()),
                "rows": int(len(bars)),
                "segment_count": int(len(segments)),
            }
        )

        configs = [("breakout", item) for item in BREAKOUT_LADDER] + [("rebound", item) for item in REBOUND_LADDER]
        for ladder_type, item in configs:
            trade_cache = combo_cache_path(sample, ladder_type, item["ladder_label"])
            empty_marker = combo_empty_marker_path(sample, ladder_type, item["ladder_label"])

            if trade_cache.exists():
                trades = read_csv_cached(trade_cache)
                ladder_trades.append(trades)
                print(
                    f"resume sample={sample['sample_key']} ladder_type={ladder_type} label={item['ladder_label']} trades={len(trades)}",
                    flush=True,
                )
                continue

            if empty_marker.exists():
                print(
                    f"resume sample={sample['sample_key']} ladder_type={ladder_type} label={item['ladder_label']} empty=true",
                    flush=True,
                )
                continue

            event_cfg = TrendlineSegmentEventConfig(
                breakout_confirm_bars=int(item["breakout_confirm_bars"]),
                rebound_confirm_bars=int(item["rebound_confirm_bars"]),
                max_resolution_bars=12,
                only_final_segments=True,
                regime_filter_medium_short=True,
            )
            result = evaluate_trendline_segment_strategy(nav, segments, event_config=event_cfg, backtest_config=bt_cfg)
            trades = result.trades.copy()
            if trades.empty:
                empty_marker.write_text("", encoding="utf-8")
                print(
                    f"done sample={sample['sample_key']} ladder_type={ladder_type} label={item['ladder_label']} trades=0",
                    flush=True,
                )
                continue
            trades["sample_key"] = sample["sample_key"]
            trades["interval"] = sample["interval"]
            trades["period"] = sample["period"]
            trades["ladder_type"] = ladder_type
            trades["ladder_label"] = item["ladder_label"]
            trades["display_label"] = item["display_label"]
            trades["breakout_confirm_bars_cfg"] = int(item["breakout_confirm_bars"])
            trades["rebound_confirm_bars_cfg"] = int(item["rebound_confirm_bars"])
            trades["ladder_note"] = item["note"]
            trades = attach_slope_metadata(trades, segments)
            trades.to_csv(trade_cache, index=False)
            ladder_trades.append(trades)
            print(
                f"done sample={sample['sample_key']} ladder_type={ladder_type} label={item['ladder_label']} trades={len(trades)}",
                flush=True,
            )

    sample_meta = pd.DataFrame(sample_meta_rows)
    trades_all = pd.concat(ladder_trades, ignore_index=True) if ladder_trades else pd.DataFrame()

    breakout_trades = trades_all[
        (trades_all["ladder_type"] == "breakout")
        & (trades_all["strategy"] == "breakout")
        & (trades_all["timeframe"] == "long")
        & (trades_all["event_type"] == "breakout_long")
    ].copy() if not trades_all.empty else pd.DataFrame()
    rebound_trades = trades_all[
        (trades_all["ladder_type"] == "rebound")
        & (trades_all["strategy"] == "rebound")
        & (trades_all["timeframe"] == "long")
        & (trades_all["event_type"] == "rebound_long")
    ].copy() if not trades_all.empty else pd.DataFrame()

    breakout_symbol = summarize_symbol_level(breakout_trades, ["sample_key", "display_label", "breakout_confirm_bars_cfg"])
    breakout_summary = summarize_group_level(breakout_symbol, ["sample_key", "display_label", "breakout_confirm_bars_cfg"])
    breakout_summary = add_trade_retention(breakout_summary, ["sample_key"], "breakout_confirm_bars_cfg")

    rebound_symbol = summarize_symbol_level(rebound_trades, ["sample_key", "display_label", "rebound_confirm_bars_cfg"])
    rebound_summary = summarize_group_level(rebound_symbol, ["sample_key", "display_label", "rebound_confirm_bars_cfg"])
    rebound_summary = add_trade_retention(rebound_summary, ["sample_key"], "rebound_confirm_bars_cfg")

    rebound_retained = rebound_trades[rebound_trades["slope_bucket"].isin(RETAINED_REBOUND_BUCKETS)].copy() if not rebound_trades.empty else pd.DataFrame()
    if not rebound_retained.empty:
        union = rebound_retained.copy()
        union["subset_group"] = "retained_union"
        single = rebound_retained.copy()
        single["subset_group"] = single["slope_bucket"]
        rebound_retained = pd.concat([single, union], ignore_index=True)
    rebound_retained_symbol = summarize_symbol_level(rebound_retained, ["sample_key", "display_label", "rebound_confirm_bars_cfg", "subset_group"])
    rebound_retained_summary = summarize_group_level(rebound_retained_symbol, ["sample_key", "display_label", "rebound_confirm_bars_cfg", "subset_group"])
    rebound_retained_summary = add_trade_retention(rebound_retained_summary, ["sample_key", "subset_group"], "rebound_confirm_bars_cfg")

    focus_qa = [
        ("Q1. 这份报告想回答什么？", "它不想继续泛泛地问“这条策略整体行不行”，而是更具体地问：多一层 confirmation，是否能显著提升质量，并且值得付出样本收缩的代价。"),
        ("Q2. 为什么要单独做第 8 份报告？", "因为前面的 slope audit 已经告诉我们：该研究线不能再整体推进，只能在保留下来的 subset 上继续做“质量提纯”。confirmation ladder 正是提纯这一步。"),
        ("Q3. 这份报告里最该看的是什么？", "先看 breakout ladder 总表：更强确认有没有把 breakout 真正救起来；再看 retained rebound subsets：`flat` / `down_high` 在更强确认下是变好，还是只是样本塌缩。"),
        ("Q4. 我们最想得到什么研究结论？", "最理想的结论是：在 retained rebound subsets 内，存在一档确认强度，让 positive_asset_ratio 和 mean_total_return 都上升，而 trade retention 没有塌得太狠。这样它才值得继续推进成下一轮默认口径。"),
        ("Q5. 如果结果不支持更强确认呢？", "那也同样有价值：说明这条线的提升空间有限，或者 confirmation 带来的滞后抵消了质量改善。到那一步，我们就更有底气把这条线当 feature 或直接收束。"),
    ]
    headline_lines = make_headline(breakout_summary, rebound_retained_summary)

    sample_meta.to_csv(ARTIFACTS / "sample_meta.csv", index=False)
    trades_all.to_csv(ARTIFACTS / "trade_detail.csv", index=False)
    breakout_summary.to_csv(ARTIFACTS / "breakout_ladder_summary.csv", index=False)
    rebound_summary.to_csv(ARTIFACTS / "rebound_ladder_summary.csv", index=False)
    rebound_retained_summary.to_csv(ARTIFACTS / "rebound_retained_subset_summary.csv", index=False)
    rebound_retained_symbol.to_csv(ARTIFACTS / "rebound_retained_subset_symbol_summary.csv", index=False)
    (ARTIFACTS / "summary.json").write_text(
        json.dumps(
            {
                "samples": SAMPLES,
                "breakout_ladder": BREAKOUT_LADDER,
                "rebound_ladder": REBOUND_LADDER,
                "retained_rebound_buckets": RETAINED_REBOUND_BUCKETS,
                "headline": headline_lines,
                "total_trades": int(len(trades_all)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    qa_html = "".join(
        f"<div class='qa-item'><div class='qa-q'>{escape(q)}</div><div class='qa-a'>{escape(a)}</div></div>" for q, a in focus_qa
    )
    headline_html = "".join(f"<li>{line}</li>" for line in headline_lines)
    html = f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <title>Trendline Confirmation Ladder Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background:#f8fafc; color:#0f172a; margin:0; padding:24px; }}
    .wrap {{ max-width: 1320px; margin: 0 auto; }}
    .card {{ background:white; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,0.04); }}
    .muted {{ color:#475569; }}
    .tbl {{ width:100%; border-collapse: collapse; font-size: 14px; }}
    .tbl th,.tbl td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eff6ff; color:#1d4ed8; font-size:12px; margin-right:6px; }}
    .qa-item {{ margin-bottom:14px; }}
    .qa-q {{ font-weight:700; margin-bottom:6px; }}
    .qa-a {{ line-height:1.7; color:#334155; }}
    code {{ background:#f1f5f9; padding:1px 4px; border-radius:6px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
<div class='wrap'>
  <div class='card'>
    <h1>Trendline Confirmation Ladder Report</h1>
    <p class='muted'>这是 PyIndicators track 的第 8 份回测报告。目标不是继续加大参数搜索，而是单独回答：<b>多一层 confirmation，是否真的能提升质量，并且值得付出样本数收缩的代价？</b></p>
    <p class='muted'><span class='pill'>scope</span> 8 个 crypto（BTC / ETH / SOL / BNB / XRP / DOGE / ADA / AVAX）<span class='pill'>samples</span> 60m / 365d + 60m / 730d</p>
    <p class='muted'><span class='pill'>important</span> 这页先做的是 <b>operational confirmation ladder</b>，即基于当前已实现的 close-persistence / inside-hold 口径做比较；还不是完整的 <code>raw_breach → close_confirm → confirm1 → confirm3 → retest_hold</code> 全事件宇宙。</p>
  </div>

  <div class='card'>
    <h2>示意图：为什么要做 confirmation ladder？</h2>
    {ladder_svg()}
  </div>

  <div class='card'>
    <h2>Q&amp;A · 这份报告想得到什么结论？</h2>
    {qa_html}
  </div>

  <div class='card'>
    <h2>当前 headline</h2>
    <ul>{headline_html}</ul>
  </div>

  <div class='card'>
    <h2>Sample meta</h2>
    {render_table(sample_meta, max_rows=20)}
  </div>

  <div class='card'>
    <h2>Breakout ladder · long timeframe / breakout_long</h2>
    <p class='muted'>如果更强的 breakout 确认真的有价值，它应该在更长样本里提升 <code>positive_asset_ratio</code> / <code>mean_total_return</code>，且 trade retention 不能塌得太厉害。</p>
    {render_table(breakout_summary, max_rows=40)}
  </div>

  <div class='card'>
    <h2>Rebound ladder · long timeframe / rebound_long</h2>
    <p class='muted'>这是整体 rebound 分支的 ladder 比较；它回答“更强 inside-hold 确认有没有整体改善质量”。</p>
    {render_table(rebound_summary, max_rows=40)}
  </div>

  <div class='card'>
    <h2>Rebound ladder · retained subsets only</h2>
    <p class='muted'>这里才是当前最值得看的主表：只看上一轮 slope audit 保留下来的 <code>flat</code> / <code>down_high</code> 及它们的并集 <code>retained_union</code>。</p>
    {render_table(rebound_retained_summary, max_rows=80)}
  </div>

  <div class='card'>
    <h2>Retained subset · symbol drill-down</h2>
    <p class='muted'>如果某档 ladder 只是被 1~2 个币撑起来，这里会看得更清楚。</p>
    {render_table(rebound_retained_symbol, max_rows=120)}
  </div>

  <div class='card'>
    <h2>How to use this page</h2>
    <ol>
      <li>先看 breakout ladder：确认更强后，breakout 是否真的变得像样？</li>
      <li>再看 rebound overall：确认更强是否只是“样本变少”，还是质量真提升？</li>
      <li>最后只看 retained subsets：这一步才决定下一轮默认 confirmation 口径该放在哪一档。</li>
    </ol>
    <p class='muted'>如果 retained subsets 内存在一档确认强度，让收益质量改善而 trade retention 仍可接受，这条线就值得继续推进；否则更可能停留在 feature / park。</p>
  </div>

  <div class='card'>
    <h2>Artifacts</h2>
    <ul>
      <li><a href='../../artifacts/trendline_confirmation_ladder/sample_meta.csv'>sample_meta.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/breakout_ladder_summary.csv'>breakout_ladder_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/rebound_ladder_summary.csv'>rebound_ladder_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/rebound_retained_subset_summary.csv'>rebound_retained_subset_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/rebound_retained_subset_symbol_summary.csv'>rebound_retained_subset_symbol_summary.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/trade_detail.csv'>trade_detail.csv</a></li>
      <li><a href='../../artifacts/trendline_confirmation_ladder/summary.json'>summary.json</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""
    (SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"Wrote report to {SITE / 'report.html'}", flush=True)


if __name__ == "__main__":
    main()
