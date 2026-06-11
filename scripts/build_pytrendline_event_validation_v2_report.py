#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.factors.pytrendline_bridge import PyTrendlineConfig, detect_pytrendlines  # noqa: E402

ART = ROOT / "reports" / "artifacts" / "pytrendline_event_validation_v2"
SITE = ROOT / "reports" / "site" / "factors" / "pytrendline_event_validation_v2"

SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD"]
INTERVAL = "60m"
PERIOD = "365d"
WINDOW_BARS = 96
STEP_BARS = 24
HORIZONS = [1, 3, 6, 12, 24]
PYTRENDLINE_TIME_INTERVAL = "1h"
CFG = PyTrendlineConfig(
    window_bars=WINDOW_BARS,
    min_points_required=3,
    ignore_breakouts=False,
    trend_type="BOTH",
    first_pt_must_be_pivot=False,
    last_pt_must_be_pivot=False,
    all_pts_must_be_pivots=True,
    trendline_must_include_global_maxmin_pt=False,
    time_interval=PYTRENDLINE_TIME_INTERVAL,
)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def flatten_yf_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def download_bars(symbol: str) -> pd.DataFrame:
    import yfinance as yf  # lazy import: only needed when artifacts are missing and we must redownload

    raw = yf.download(symbol, period=PERIOD, interval=INTERVAL, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        raise ValueError(f"No data for {symbol}")
    raw = flatten_yf_columns(raw)
    bars = raw.reset_index().rename(columns={
        "Datetime": "timestamp",
        "Date": "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
    keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in bars.columns]
    return bars[keep].dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)


def score_bucket(series: pd.Series) -> pd.Series:
    if series.empty:
        return pd.Series(dtype="object")
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))

    def label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        if v >= q3:
            return "high"
        if v >= q1:
            return "mid"
        return "low"

    return series.apply(label)


def slope_bucket(series: pd.Series) -> pd.Series:
    abs_s = series.abs()
    if abs_s.empty:
        return pd.Series(dtype="object")
    q1 = float(abs_s.quantile(0.25))
    q3 = float(abs_s.quantile(0.75))

    def label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        mag = abs(v)
        strength = "flat" if mag < q1 else "mid" if mag < q3 else "steep"
        direction = "up" if v > 0 else "down" if v < 0 else "flat"
        return f"{direction}_{strength}"

    return series.apply(label)


def representative_lines(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    rep = df[df.get("is_best_from_duplicate_group", False).fillna(False)].copy()
    if rep.empty:
        rep = df.copy()
    return rep.reset_index(drop=True)


def extract_window_events(symbol: str, bars: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    if len(bars) < WINDOW_BARS + max(HORIZONS) + 2:
        return pd.DataFrame()

    for end_idx in range(WINDOW_BARS - 1, len(bars) - max(HORIZONS), STEP_BARS):
        start_idx = end_idx - WINDOW_BARS + 1
        window = bars.iloc[start_idx:end_idx + 1].copy()
        end_ts = pd.Timestamp(window["timestamp"].iloc[-1])
        prev_anchor_idx = max(start_idx, end_idx - STEP_BARS + 1)
        prev_anchor_ts = pd.Timestamp(bars["timestamp"].iloc[prev_anchor_idx])

        try:
            result = detect_pytrendlines(window, config=CFG)
        except Exception as e:
            print(f"warn symbol={symbol} end_idx={end_idx} pytrendline_failed={e}", flush=True)
            continue

        support = representative_lines(result.get("support_trendlines", pd.DataFrame())).copy()
        resistance = representative_lines(result.get("resistance_trendlines", pd.DataFrame())).copy()
        if not support.empty:
            support["line_side"] = "support"
        if not resistance.empty:
            resistance["line_side"] = "resistance"
        lines = pd.concat([support, resistance], ignore_index=True) if (not support.empty or not resistance.empty) else pd.DataFrame()
        if lines.empty:
            continue

        lines = lines.copy()
        for col in ["starts_at_date", "ends_at_date", "breakout_date"]:
            if col in lines.columns:
                lines[col] = pd.to_datetime(lines[col], utc=True, errors="coerce")
        lines["line_quality_bucket"] = score_bucket(pd.to_numeric(lines.get("score"), errors="coerce"))
        lines["slope_bucket"] = slope_bucket(pd.to_numeric(lines.get("slope"), errors="coerce").fillna(0.0))

        current_close = float(window["close"].iloc[-1])
        for _, line in lines.iterrows():
            is_breakout = bool(line.get("is_breakout", False))
            if is_breakout and pd.notna(line.get("breakout_date")):
                event_ts = pd.Timestamp(line["breakout_date"])
                if not (prev_anchor_ts <= event_ts <= end_ts):
                    continue
                event_family = "breakout"
                event_subtype = "breakout_tagged_line"
            else:
                end_date = line.get("ends_at_date")
                if pd.isna(end_date):
                    continue
                event_ts = pd.Timestamp(end_date)
                if not (prev_anchor_ts <= event_ts <= end_ts):
                    continue
                event_family = "touch"
                event_subtype = "line_touch_candidate"

            ts_matches = bars.index[bars["timestamp"] == event_ts]
            if len(ts_matches) == 0:
                continue
            event_idx = int(ts_matches[0])
            if event_idx + max(HORIZONS) >= len(bars):
                continue
            event_close = float(bars.loc[event_idx, "close"])
            rec = {
                "symbol": symbol,
                "sample_key": f"multiasset_{INTERVAL}_{PERIOD}_window{WINDOW_BARS}_step{STEP_BARS}",
                "window_end": end_ts,
                "event_timestamp": event_ts,
                "event_index": event_idx,
                "engine_line_id": str(line.get("id")),
                "line_side": line.get("line_side"),
                "event_family": event_family,
                "event_subtype": event_subtype,
                "line_quality_bucket": line.get("line_quality_bucket", "unknown"),
                "slope_bucket": line.get("slope_bucket", "unknown"),
                "score": float(line.get("score")) if pd.notna(line.get("score")) else np.nan,
                "slope": float(line.get("slope")) if pd.notna(line.get("slope")) else np.nan,
                "current_close": current_close,
                "event_close": event_close,
            }
            for h in HORIZONS:
                future_close = float(bars.loc[event_idx + h, "close"])
                rec[f"fwd_ret_h{h}"] = future_close / event_close - 1.0
            rows.append(rec)
        print(f"processed symbol={symbol} end={end_ts.isoformat()} lines={len(lines)} cumulative_events={len(rows)}", flush=True)

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out = out.drop_duplicates(subset=["symbol", "event_family", "event_subtype", "line_side", "engine_line_id", "event_timestamp"]).reset_index(drop=True)
    return out


def confidence_tier(n: int) -> str:
    if n >= 250:
        return "high"
    if n >= 120:
        return "medium"
    if n >= 40:
        return "low"
    return "very_low"


def directional_label(up_ratio: float, mean_ret: float) -> str:
    if pd.isna(up_ratio) or pd.isna(mean_ret):
        return "unknown"
    if up_ratio >= 0.55 and mean_ret > 0:
        return "more_likely_up"
    if up_ratio <= 0.45 and mean_ret < 0:
        return "more_likely_down"
    return "mixed"


def summarize(df: pd.DataFrame, group_cols: list[str], horizon: int) -> pd.DataFrame:
    ret_col = f"fwd_ret_h{horizon}"
    if df.empty:
        return pd.DataFrame()
    grp = (
        df.groupby(group_cols, dropna=False)[ret_col]
        .agg(events="size", mean_ret="mean", median_ret="median", up_ratio=lambda s: float((s > 0).mean()))
        .reset_index()
    )
    grp["confidence_tier"] = grp["events"].map(confidence_tier)
    grp["direction_label"] = grp.apply(lambda r: directional_label(float(r["up_ratio"]), float(r["mean_ret"])), axis=1)
    return grp.sort_values(group_cols).reset_index(drop=True)


def summarize_from_ret(df: pd.DataFrame, group_cols: list[str], ret_col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    grp = (
        df.groupby(group_cols, dropna=False)[ret_col]
        .agg(events="size", mean_ret="mean", median_ret="median", up_ratio=lambda s: float((s > 0).mean()))
        .reset_index()
    )
    grp["confidence_tier"] = grp["events"].map(confidence_tier)
    grp["direction_label"] = grp.apply(lambda r: directional_label(float(r["up_ratio"]), float(r["mean_ret"])), axis=1)
    return grp.sort_values(group_cols).reset_index(drop=True)


def render_table(df: pd.DataFrame, limit: int = 40) -> str:
    if df is None or df.empty:
        return '<p><em>empty</em></p>'
    shown = df.head(limit).copy()
    for col in shown.columns:
        if pd.api.types.is_datetime64_any_dtype(shown[col]):
            shown[col] = shown[col].dt.strftime("%Y-%m-%d %H:%M")
        elif pd.api.types.is_float_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: round(float(x), 6) if pd.notna(x) else "")
    return shown.to_html(index=False, classes="tbl", border=0)


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def bp(x: float) -> str:
    return f"{x * 10000:.2f}bp"


def chart_bar(df: pd.DataFrame, label_col: str, value_col: str, title: str, out_path: Path, top_n: int | None = None) -> None:
    if df.empty:
        return
    plot_df = df.copy()
    if top_n is not None and len(plot_df) > top_n:
        plot_df = plot_df.head(top_n).copy()
    plt.figure(figsize=(10, 4.8))
    colors = ["#16a34a" if v > 0 else "#dc2626" if v < 0 else "#64748b" for v in plot_df[value_col]]
    plt.bar(plot_df[label_col].astype(str), plot_df[value_col], color=colors)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.title(title)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def chart_dual(df: pd.DataFrame, label_col: str, left_col: str, right_col: str, out_path: Path, title: str) -> None:
    if df.empty:
        return
    labels = df[label_col].astype(str).tolist()
    x = np.arange(len(labels))
    width = 0.38
    fig, ax1 = plt.subplots(figsize=(10, 4.8))
    ax1.bar(x - width / 2, df[left_col], width=width, color="#2563eb", label=left_col)
    ax1.set_ylabel("mean return")
    ax1.axhline(0, color="#334155", linewidth=1)
    ax2 = ax1.twinx()
    ax2.bar(x + width / 2, df[right_col], width=width, color="#f59e0b", alpha=0.75, label=right_col)
    ax2.set_ylabel("up ratio")
    ax2.set_ylim(0, 1)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=30, ha="right")
    plt.title(title)
    fig.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def chart_side_horizon(side_horizon: pd.DataFrame, out_path: Path) -> None:
    if side_horizon.empty:
        return
    plt.figure(figsize=(9.2, 4.8))
    for side, sub in side_horizon.groupby("line_side"):
        sub = sub.sort_values("horizon")
        plt.plot(sub["horizon"], sub["mean_ret"], marker="o", linewidth=2, label=side)
    plt.axhline(0, color="#334155", linewidth=1)
    plt.xticks(HORIZONS)
    plt.xlabel("horizon (bars)")
    plt.ylabel("mean return")
    plt.title("Side effect persistence across horizons")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def chart_lag_hist(lag_hours: pd.Series, out_path: Path) -> None:
    if lag_hours.empty:
        return
    plt.figure(figsize=(9.2, 4.8))
    bins = np.arange(0, max(48, int(lag_hours.max()) + 2), 1)
    plt.hist(lag_hours, bins=bins, color="#3b82f6", alpha=0.8, edgecolor="#1e3a8a")
    plt.axvline(float(lag_hours.median()), color="#dc2626", linestyle="--", linewidth=1.5, label=f"median={lag_hours.median():.1f}h")
    plt.xlabel("window_end - event_timestamp (hours)")
    plt.ylabel("count")
    plt.title("Event lag distribution (observability risk)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def chart_triplet(compare_df: pd.DataFrame, key_col: str, out_path: Path, title: str, top_n: int | None = None) -> None:
    if compare_df.empty:
        return
    plot_df = compare_df.copy()
    if top_n is not None and len(plot_df) > top_n:
        plot_df = plot_df.head(top_n).copy()

    labels = plot_df[key_col].astype(str).tolist()
    x = np.arange(len(labels))
    width = 0.24

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.bar(x - width, plot_df["raw_mean_ret"], width=width, label="raw", color="#2563eb")
    ax.bar(x, plot_df["collapsed_mean_ret"], width=width, label="timestamp-collapsed", color="#0ea5e9")
    ax.bar(x + width, plot_df["lag1_mean_ret"], width=width, label="lag<=1h", color="#f59e0b")
    ax.axhline(0, color="#334155", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("mean return")
    ax.set_title(title)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def chart_heatmap(df: pd.DataFrame, out_path: Path, title: str) -> None:
    if df.empty:
        return
    mat = df.copy()
    values = mat.values
    vmax = float(np.nanmax(np.abs(values)))
    if vmax <= 0:
        vmax = 1e-6
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    im = ax.imshow(values, cmap="RdBu_r", aspect="auto", vmin=-vmax, vmax=vmax)
    ax.set_xticks(np.arange(len(mat.columns)))
    ax.set_xticklabels(mat.columns)
    ax.set_yticks(np.arange(len(mat.index)))
    ax.set_yticklabels(mat.index)
    ax.set_title(title)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j] * 100:.2f}%", ha="center", va="center", fontsize=8, color="#0f172a")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close(fig)


def collapse_for_bucket(events: pd.DataFrame, bucket_cols: list[str], ret_col: str) -> pd.DataFrame:
    keys = ["symbol", "event_timestamp", *bucket_cols]
    return events.groupby(keys, dropna=False)[ret_col].mean().reset_index()


def build_robustness_compare(raw: pd.DataFrame, collapsed: pd.DataFrame, lag1: pd.DataFrame, key_col: str) -> pd.DataFrame:
    out = raw[[key_col, "events", "mean_ret", "up_ratio"]].rename(columns={
        "events": "raw_events",
        "mean_ret": "raw_mean_ret",
        "up_ratio": "raw_up_ratio",
    })
    out = out.merge(
        collapsed[[key_col, "events", "mean_ret", "up_ratio"]].rename(columns={
            "events": "collapsed_events",
            "mean_ret": "collapsed_mean_ret",
            "up_ratio": "collapsed_up_ratio",
        }),
        on=key_col,
        how="left",
    )
    out = out.merge(
        lag1[[key_col, "events", "mean_ret", "up_ratio"]].rename(columns={
            "events": "lag1_events",
            "mean_ret": "lag1_mean_ret",
            "up_ratio": "lag1_up_ratio",
        }),
        on=key_col,
        how="left",
    )

    for col in ["collapsed_events", "lag1_events"]:
        out[col] = out[col].fillna(0).astype(int)
    for col in ["collapsed_mean_ret", "lag1_mean_ret", "collapsed_up_ratio", "lag1_up_ratio"]:
        out[col] = out[col].astype(float)

    denom = out["raw_mean_ret"].abs().replace(0, np.nan)
    out["collapse_abs_retention"] = out["collapsed_mean_ret"].abs() / denom
    out["lag1_abs_retention"] = out["lag1_mean_ret"].abs() / denom
    out["lag1_sign_match"] = np.sign(out["raw_mean_ret"]) == np.sign(out["lag1_mean_ret"])
    return out.sort_values(key_col).reset_index(drop=True)


def symbol_consistency(events: pd.DataFrame, bucket_col: str, ret_col: str = "fwd_ret_h6") -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=[bucket_col, "symbols", "pos_symbols", "neg_symbols", "consistency_ratio"])
    by_symbol = events.groupby(["symbol", bucket_col], dropna=False)[ret_col].mean().reset_index()
    rows: list[dict] = []
    for bucket, sub in by_symbol.groupby(bucket_col, dropna=False):
        pos = int((sub[ret_col] > 0).sum())
        neg = int((sub[ret_col] < 0).sum())
        n = int(len(sub))
        rows.append({
            bucket_col: bucket,
            "symbols": n,
            "pos_symbols": pos,
            "neg_symbols": neg,
            "consistency_ratio": (max(pos, neg) / n) if n > 0 else np.nan,
        })
    return pd.DataFrame(rows).sort_values(bucket_col).reset_index(drop=True)


def _pick_value(df: pd.DataFrame, key_col: str, key: str, val_col: str) -> float:
    sub = df[df[key_col] == key]
    if sub.empty:
        return float("nan")
    return float(sub.iloc[0][val_col])


def level_from_score(score: float) -> str:
    if pd.isna(score):
        return "低"
    if score >= 0.75:
        return "高"
    if score >= 0.60:
        return "中高"
    if score >= 0.45:
        return "中"
    if score >= 0.30:
        return "中低"
    return "低"


def build_reliability_matrix(
    side_compare: pd.DataFrame,
    slope_compare: pd.DataFrame,
    quality_compare: pd.DataFrame,
    side_symbol_cons: pd.DataFrame,
    slope_symbol_cons: pd.DataFrame,
    lag_hours: pd.Series,
) -> tuple[pd.DataFrame, dict]:
    # side reliability
    raw_support = _pick_value(side_compare, "line_side", "support", "raw_mean_ret")
    raw_resist = _pick_value(side_compare, "line_side", "resistance", "raw_mean_ret")
    coll_support = _pick_value(side_compare, "line_side", "support", "collapsed_mean_ret")
    coll_resist = _pick_value(side_compare, "line_side", "resistance", "collapsed_mean_ret")
    lag1_support = _pick_value(side_compare, "line_side", "support", "lag1_mean_ret")
    lag1_resist = _pick_value(side_compare, "line_side", "resistance", "lag1_mean_ret")

    side_gap_raw = abs(raw_support - raw_resist)
    side_gap_coll = abs(coll_support - coll_resist)
    side_gap_lag1 = abs(lag1_support - lag1_resist)

    side_collapse_ret = side_gap_coll / side_gap_raw if side_gap_raw > 0 else np.nan
    side_lag1_ret = side_gap_lag1 / side_gap_raw if side_gap_raw > 0 else np.nan
    side_sym_cons = float(side_symbol_cons["consistency_ratio"].min()) if not side_symbol_cons.empty else np.nan

    side_desc_score = 0.6 * min(1.0, side_collapse_ret) + 0.4 * side_sym_cons
    side_trade_score = 0.7 * min(1.0, side_lag1_ret) + 0.3 * side_sym_cons

    # slope reliability (focus on directional buckets)
    strong = slope_compare[slope_compare["slope_bucket"].isin(["up_steep", "down_steep", "up_mid", "down_mid"])].copy()
    raw_abs = float(strong["raw_mean_ret"].abs().mean()) if not strong.empty else np.nan
    coll_abs = float(strong["collapsed_mean_ret"].abs().mean()) if not strong.empty else np.nan
    lag1_abs = float(strong["lag1_mean_ret"].abs().mean()) if not strong.empty else np.nan
    slope_coll_ret = coll_abs / raw_abs if raw_abs and raw_abs > 0 else np.nan
    slope_lag1_ret = lag1_abs / raw_abs if raw_abs and raw_abs > 0 else np.nan

    slope_sym = slope_symbol_cons[slope_symbol_cons["slope_bucket"].isin(["up_steep", "down_steep", "up_mid", "down_mid"])]
    slope_sym_cons = float(slope_sym["consistency_ratio"].mean()) if not slope_sym.empty else np.nan

    slope_desc_score = 0.5 * min(1.0, slope_coll_ret) + 0.5 * slope_sym_cons
    slope_trade_score = 0.7 * min(1.0, slope_lag1_ret) + 0.3 * slope_sym_cons

    # quality reliability: effect itself very small
    quality_raw_spread = float(quality_compare["raw_mean_ret"].max() - quality_compare["raw_mean_ret"].min()) if not quality_compare.empty else np.nan
    quality_coll_spread = float(quality_compare["collapsed_mean_ret"].max() - quality_compare["collapsed_mean_ret"].min()) if not quality_compare.empty else np.nan
    quality_lag1_spread = float(quality_compare["lag1_mean_ret"].max() - quality_compare["lag1_mean_ret"].min()) if not quality_compare.empty else np.nan

    quality_desc_score = min(1.0, (quality_raw_spread / 0.003 if quality_raw_spread == quality_raw_spread else 0.0)) * 0.5 + min(
        1.0, (quality_coll_spread / 0.003 if quality_coll_spread == quality_coll_spread else 0.0)
    ) * 0.5
    quality_trade_score = min(1.0, (quality_lag1_spread / 0.003 if quality_lag1_spread == quality_lag1_spread else 0.0)) * 0.4

    # method risk from lag
    share_lag0 = float((lag_hours == 0).mean())
    share_lag1 = float((lag_hours <= 1).mean())
    lag_med = float(lag_hours.median())
    lag_p95 = float(lag_hours.quantile(0.95))

    method_desc_score = 0.50
    method_trade_score = 0.15 if share_lag1 < 0.15 else 0.30 if share_lag1 < 0.30 else 0.45

    rows = [
        {
            "topic": "line_side（support vs resistance）",
            "descriptive_reliability": level_from_score(side_desc_score),
            "trading_reliability": level_from_score(side_trade_score),
            "evidence": (
                f"h6 raw gap={bp(side_gap_raw)}，collapsed gap={bp(side_gap_coll)}（保留 {side_collapse_ret*100:.1f}%），"
                f"lag<=1h gap={bp(side_gap_lag1)}（保留 {side_lag1_ret*100:.1f}%）。"
            ),
        },
        {
            "topic": "slope_direction（mid/steep）",
            "descriptive_reliability": level_from_score(slope_desc_score),
            "trading_reliability": level_from_score(slope_trade_score),
            "evidence": (
                f"|mean| raw={bp(raw_abs)}，collapsed={bp(coll_abs)}，lag<=1h={bp(lag1_abs)}；"
                f"lag<=1h 方向强度仅保留约 {slope_lag1_ret*100:.1f}%。"
            ),
        },
        {
            "topic": "line_quality（high/mid/low）",
            "descriptive_reliability": level_from_score(quality_desc_score),
            "trading_reliability": level_from_score(quality_trade_score),
            "evidence": (
                f"h6 raw bucket spread={bp(quality_raw_spread)}，collapsed spread={bp(quality_coll_spread)}，"
                f"lag<=1h spread={bp(quality_lag1_spread)}。"
            ),
        },
        {
            "topic": "method risk（event observability）",
            "descriptive_reliability": level_from_score(method_desc_score),
            "trading_reliability": level_from_score(method_trade_score),
            "evidence": (
                f"event lag median={lag_med:.1f}h，p95={lag_p95:.1f}h；lag==0 仅 {share_lag0*100:.1f}%，lag<=1h 仅 {share_lag1*100:.1f}%。"
            ),
        },
    ]

    reliability_df = pd.DataFrame(rows)
    overall = {
        "side_gap_raw": side_gap_raw,
        "side_gap_collapsed": side_gap_coll,
        "side_gap_lag1": side_gap_lag1,
        "side_gap_lag1_retention": side_lag1_ret,
        "lag_median_h": lag_med,
        "lag_p95_h": lag_p95,
        "lag0_share": share_lag0,
        "lag1_share": share_lag1,
    }
    return reliability_df, overall


def build_key_findings(overall_h6: pd.DataFrame, side_h6: pd.DataFrame, quality_h6: pd.DataFrame, slope_h6: pd.DataFrame) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for _, row in overall_h6.iterrows():
        findings.append({
            "topic": f"overall / {row['event_family']}",
            "reading": f"n={int(row['events'])}，6-bar 平均收益 {pct(float(row['mean_ret']))}，上涨占比 {pct(float(row['up_ratio']))}，置信度 {row['confidence_tier']}。",
            "verdict": "整体效应偏弱，更像事件上下文监控，不像可独立交易 alpha。",
        })
    if not side_h6.empty:
        best_side = side_h6.sort_values(["events", "mean_ret"], ascending=[False, False]).iloc[0]
        findings.append({
            "topic": "line side",
            "reading": f"side 是样本最充足、方向也最清楚的维度。当前较强一侧：{best_side['line_side']}，n={int(best_side['events'])}，mean={pct(float(best_side['mean_ret']))}，up={pct(float(best_side['up_ratio']))}。",
            "verdict": "side 值得继续做 feature/filter，但不建议直接当交易规则。",
        })
    if not slope_h6.empty:
        stable = slope_h6[slope_h6["events"] >= 40].sort_values(["events", "mean_ret"], ascending=[False, False]).head(4)
        if not stable.empty:
            desc = "；".join([f"{r['slope_bucket']} (n={int(r['events'])}, mean={pct(float(r['mean_ret']))})" for _, r in stable.iterrows()])
            findings.append({
                "topic": "slope bucket",
                "reading": f"slope 在 raw 统计中呈现明显方向梯度：{desc}。",
                "verdict": "但在更严格可观测子样本中会明显衰减，当前只能算候选上下文特征。",
            })
    if not quality_h6.empty:
        spread = float(quality_h6["mean_ret"].max() - quality_h6["mean_ret"].min())
        findings.append({
            "topic": "line quality",
            "reading": f"quality 三档在 h=6 的均值差异仅 {bp(spread)}，量级较小。",
            "verdict": "quality 暂不支持强预测结论，优先作为噪音过滤假设继续观察。",
        })
    return findings


def findings_html(findings: list[dict[str, str]]) -> str:
    blocks = []
    for item in findings:
        blocks.append(
            f"<div class='qa-item'><div class='qa-q'>{escape(item['topic'])}</div><div class='qa-a'>{escape(item['reading'])}<br/><strong>解读：</strong>{escape(item['verdict'])}</div></div>"
        )
    return "".join(blocks)


def note_block(items: list[tuple[str, str]]) -> str:
    lis = "".join([f"<li><b>{escape(k)}：</b>{escape(v)}</li>" for k, v in items])
    return f"<div class='chart-notes'><ul>{lis}</ul></div>"


def load_existing_or_run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = {
        "events": ART / "event_sample.csv",
        "symbol": ART / "symbol_meta.csv",
        "overall": ART / "overall_by_family_horizon.csv",
        "side": ART / "side_summary_h6.csv",
        "slope": ART / "slope_summary_h6.csv",
        "quality": ART / "quality_summary_h6.csv",
    }
    if all(p.exists() for p in paths.values()):
        return (
            pd.read_csv(paths["events"], parse_dates=["window_end", "event_timestamp"]),
            pd.read_csv(paths["symbol"], parse_dates=["start", "end"]),
            pd.read_csv(paths["overall"]),
            pd.read_csv(paths["side"]),
            pd.read_csv(paths["slope"]),
            pd.read_csv(paths["quality"]),
        )

    all_events: list[pd.DataFrame] = []
    symbol_meta: list[dict] = []
    for symbol in SYMBOLS:
        bars = download_bars(symbol)
        symbol_meta.append({"symbol": symbol, "rows": int(len(bars)), "start": bars["timestamp"].iloc[0], "end": bars["timestamp"].iloc[-1]})
        print(f"downloaded symbol={symbol} rows={len(bars)}", flush=True)
        events = extract_window_events(symbol, bars)
        if not events.empty:
            all_events.append(events)
        print(f"finished symbol={symbol} events={0 if events.empty else len(events)}", flush=True)

    events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    symbol_meta_df = pd.DataFrame(symbol_meta)
    if events.empty:
        raise SystemExit("No events produced for pytrendline_event_validation_v2")

    overall_rows: list[pd.DataFrame] = []
    for h in HORIZONS:
        s = summarize(events, ["event_family"], h)
        s.insert(0, "horizon", h)
        overall_rows.append(s)
    overall = pd.concat(overall_rows, ignore_index=True)
    side_h6 = summarize(events, ["line_side"], 6)
    slope_h6 = summarize(events, ["slope_bucket"], 6).sort_values(["events", "mean_ret"], ascending=[False, False]).reset_index(drop=True)
    quality_h6 = summarize(events, ["line_quality_bucket"], 6)

    events.to_csv(paths["events"], index=False)
    symbol_meta_df.to_csv(paths["symbol"], index=False)
    overall.to_csv(paths["overall"], index=False)
    side_h6.to_csv(paths["side"], index=False)
    slope_h6.to_csv(paths["slope"], index=False)
    quality_h6.to_csv(paths["quality"], index=False)

    return events, symbol_meta_df, overall, side_h6, slope_h6, quality_h6


def main() -> int:
    ensure_dir(ART)
    ensure_dir(SITE)

    events, symbol_meta_df, overall, side_h6, slope_h6, quality_h6 = load_existing_or_run()
    events = events.copy()
    events["event_lag_h"] = ((events["window_end"] - events["event_timestamp"]).dt.total_seconds() / 3600.0).astype(float)

    overall_h6 = overall[overall["horizon"] == 6].copy().reset_index(drop=True)

    # extra summaries
    side_horizon_rows: list[pd.DataFrame] = []
    for h in HORIZONS:
        tmp = summarize(events, ["line_side"], h)
        tmp.insert(0, "horizon", h)
        side_horizon_rows.append(tmp)
    side_horizon = pd.concat(side_horizon_rows, ignore_index=True)

    side_raw = summarize_from_ret(events, ["line_side"], "fwd_ret_h6")
    side_collapsed = summarize_from_ret(collapse_for_bucket(events, ["line_side"], "fwd_ret_h6"), ["line_side"], "fwd_ret_h6")
    side_lag1 = summarize_from_ret(events[events["event_lag_h"] <= 1], ["line_side"], "fwd_ret_h6")
    side_compare = build_robustness_compare(side_raw, side_collapsed, side_lag1, "line_side")

    slope_raw = summarize_from_ret(events, ["slope_bucket"], "fwd_ret_h6")
    slope_collapsed = summarize_from_ret(collapse_for_bucket(events, ["slope_bucket"], "fwd_ret_h6"), ["slope_bucket"], "fwd_ret_h6")
    slope_lag1 = summarize_from_ret(events[events["event_lag_h"] <= 1], ["slope_bucket"], "fwd_ret_h6")
    slope_compare = build_robustness_compare(slope_raw, slope_collapsed, slope_lag1, "slope_bucket")

    quality_raw = summarize_from_ret(events, ["line_quality_bucket"], "fwd_ret_h6")
    quality_collapsed = summarize_from_ret(collapse_for_bucket(events, ["line_quality_bucket"], "fwd_ret_h6"), ["line_quality_bucket"], "fwd_ret_h6")
    quality_lag1 = summarize_from_ret(events[events["event_lag_h"] <= 1], ["line_quality_bucket"], "fwd_ret_h6")
    quality_compare = build_robustness_compare(quality_raw, quality_collapsed, quality_lag1, "line_quality_bucket")

    side_symbol_cons = symbol_consistency(events, "line_side")
    slope_symbol_cons = symbol_consistency(events, "slope_bucket")

    reliability_df, reliability_overall = build_reliability_matrix(
        side_compare=side_compare,
        slope_compare=slope_compare,
        quality_compare=quality_compare,
        side_symbol_cons=side_symbol_cons,
        slope_symbol_cons=slope_symbol_cons,
        lag_hours=events["event_lag_h"],
    )

    lag_summary = pd.DataFrame([
        {
            "events": int(len(events)),
            "lag_mean_h": float(events["event_lag_h"].mean()),
            "lag_median_h": float(events["event_lag_h"].median()),
            "lag_p95_h": float(events["event_lag_h"].quantile(0.95)),
            "lag_max_h": float(events["event_lag_h"].max()),
            "share_lag0": float((events["event_lag_h"] == 0).mean()),
            "share_lag1": float((events["event_lag_h"] <= 1).mean()),
            "share_lag6": float((events["event_lag_h"] <= 6).mean()),
        }
    ])

    # persist extra artifacts
    side_horizon.to_csv(ART / "side_horizon_summary.csv", index=False)
    side_compare.to_csv(ART / "side_robustness_h6.csv", index=False)
    slope_compare.to_csv(ART / "slope_robustness_h6.csv", index=False)
    quality_compare.to_csv(ART / "quality_robustness_h6.csv", index=False)
    side_symbol_cons.to_csv(ART / "side_symbol_consistency_h6.csv", index=False)
    slope_symbol_cons.to_csv(ART / "slope_symbol_consistency_h6.csv", index=False)
    reliability_df.to_csv(ART / "reliability_matrix.csv", index=False)
    lag_summary.to_csv(ART / "lag_summary.csv", index=False)

    # charts
    chart_bar(overall_h6, "event_family", "mean_ret", "Overall mean return by family (h=6)", SITE / "overall_h6_mean.png")
    chart_dual(side_h6, "line_side", "mean_ret", "up_ratio", SITE / "side_h6_dual.png", "Line side: mean return vs up ratio (h=6)")
    chart_dual(quality_h6, "line_quality_bucket", "mean_ret", "up_ratio", SITE / "quality_h6_dual.png", "Line quality: mean return vs up ratio (h=6)")
    chart_dual(slope_h6.sort_values("events", ascending=False).head(8), "slope_bucket", "mean_ret", "up_ratio", SITE / "slope_h6_top8_dual.png", "Top slope buckets by sample size (h=6)")
    chart_side_horizon(side_horizon, SITE / "side_horizon_trend.png")
    chart_lag_hist(events["event_lag_h"], SITE / "event_lag_hist.png")
    chart_triplet(side_compare, "line_side", SITE / "side_robustness_h6.png", "Side robustness (raw vs collapsed vs lag<=1h)")
    chart_triplet(quality_compare, "line_quality_bucket", SITE / "quality_robustness_h6.png", "Quality robustness (raw vs collapsed vs lag<=1h)")

    side_symbol_heatmap = collapse_for_bucket(events, ["line_side"], "fwd_ret_h6").groupby(["symbol", "line_side"], dropna=False)["fwd_ret_h6"].mean().unstack("line_side")
    chart_heatmap(side_symbol_heatmap, SITE / "side_symbol_heatmap_h6.png", "Collapsed h=6 mean return by symbol × side")

    findings = build_key_findings(overall_h6, side_h6, quality_h6, slope_h6)

    side_support_raw = _pick_value(side_compare, "line_side", "support", "raw_mean_ret")
    side_resist_raw = _pick_value(side_compare, "line_side", "resistance", "raw_mean_ret")
    side_support_lag1 = _pick_value(side_compare, "line_side", "support", "lag1_mean_ret")
    side_resist_lag1 = _pick_value(side_compare, "line_side", "resistance", "lag1_mean_ret")
    side_support_up = _pick_value(side_compare, "line_side", "support", "raw_up_ratio")
    side_resist_up = _pick_value(side_compare, "line_side", "resistance", "raw_up_ratio")
    side_support_events = int(side_h6[side_h6["line_side"] == "support"]["events"].iloc[0])
    side_resist_events = int(side_h6[side_h6["line_side"] == "resistance"]["events"].iloc[0])
    side_gap_raw = abs(side_support_raw - side_resist_raw)
    side_gap_lag1 = abs(side_support_lag1 - side_resist_lag1)
    side_gap_lag1_ret = side_gap_lag1 / side_gap_raw if side_gap_raw > 0 else np.nan

    qna = [
        (
            "Q1. 这次 v2 到底在做什么？",
            "它不是在证明“这个策略已经能赚钱”，而是在做一件更基础的事：把样本放大以后，看看 pytrendline 里哪些现象还存在，哪些只是小样本错觉。",
        ),
        (
            "Q2. 例如 support 的 65.38% 到底是什么意思？",
            f"人话翻译：在全部 {side_support_events} 个 support 事件里，如果事件发生后往后看 6 根 K 线（这里 1 根=1 小时，所以就是 6 小时），有 {pct(side_support_up)} 的样本价格是上涨的。"
            f"同一批样本的平均 6 小时收益是 {pct(side_support_raw)}。这就是“support 更偏正向”的意思。",
        ),
        (
            "Q3. 那 line、support、resistance 分别是什么？",
            "line 就是 pytrendline 在一个滚动窗口里自动找出来的一条趋势线。support line 可以粗略理解成“下方支撑线”，resistance line 可以粗略理解成“上方压制线”。这页报告是在看：当价格和这些线发生特定事件后，未来表现有没有统计差异。",
        ),
        (
            "Q4. 当前最清楚的结论是什么？",
            f"是 side 这个维度。support 事件 6 小时后更常上涨（up={pct(side_support_up)}，mean={pct(side_support_raw)}）；resistance 事件 6 小时后更常偏弱（up={pct(side_resist_up)}，mean={pct(side_resist_raw)}）。它不是 100% 正确，但方向上很清楚。",
        ),
        (
            "Q5. 去重后（同 symbol+timestamp 合并）结论还在吗？",
            f"还在。support 去重后仍是 {pct(_pick_value(side_compare, 'line_side', 'support', 'collapsed_mean_ret'))}，resistance 去重后仍是 {pct(_pick_value(side_compare, 'line_side', 'resistance', 'collapsed_mean_ret'))}。这说明它不是单纯因为同一时刻画出了很多条相似线，才把结果“堆”出来的。",
        ),
        (
            "Q6. 那为什么你又说它还不能直接当交易信号？",
            f"因为可观测性有问题：当我们只看更接近实时可用的样本（lag<=1h）时，side gap 会从 {bp(side_gap_raw)} 掉到 {bp(side_gap_lag1)}，只剩原来的 {side_gap_lag1_ret*100:.1f}%。也就是说，现象是有的，但真正拿来实时交易时，强度会缩水很多。",
        ),
        (
            "Q7. slope 和 quality 怎么理解？",
            "slope 可以理解成“线的斜率方向和陡峭程度”；它在描述性统计里有明显梯度。quality 可以理解成“这条线本身质量高不高”；但它目前的效应很小，所以暂时看不出强预测力。",
        ),
        (
            "Q8. 这些结论现在该怎么用？",
            "更合适的用法是：先把 side / slope 当作 feature 或 filter 候选，继续做更严格验证；不合适的用法是：直接把这页里的某个 bucket 当成可实盘交易规则。",
        ),
    ]
    qna_html = "".join(
        f"<div class='qa-item'><div class='qa-q'>{escape(q)}</div><div class='qa-a'>{escape(a)}</div></div>" for q, a in qna
    )

    breakout_h6_mean = _pick_value(overall_h6, "event_family", "breakout", "mean_ret")
    breakout_h6_up = _pick_value(overall_h6, "event_family", "breakout", "up_ratio")
    touch_h6_mean = _pick_value(overall_h6, "event_family", "touch", "mean_ret")
    touch_h6_up = _pick_value(overall_h6, "event_family", "touch", "up_ratio")

    quality_high_mean = _pick_value(quality_h6, "line_quality_bucket", "high", "mean_ret")
    quality_mid_mean = _pick_value(quality_h6, "line_quality_bucket", "mid", "mean_ret")
    quality_low_mean = _pick_value(quality_h6, "line_quality_bucket", "low", "mean_ret")
    quality_high_up = _pick_value(quality_h6, "line_quality_bucket", "high", "up_ratio")
    quality_mid_up = _pick_value(quality_h6, "line_quality_bucket", "mid", "up_ratio")
    quality_low_up = _pick_value(quality_h6, "line_quality_bucket", "low", "up_ratio")
    quality_raw_spread = float(quality_compare["raw_mean_ret"].max() - quality_compare["raw_mean_ret"].min())
    quality_coll_spread = float(quality_compare["collapsed_mean_ret"].max() - quality_compare["collapsed_mean_ret"].min())
    quality_lag1_spread = float(quality_compare["lag1_mean_ret"].max() - quality_compare["lag1_mean_ret"].min())

    up_steep_mean = _pick_value(slope_h6, "slope_bucket", "up_steep", "mean_ret")
    up_steep_up = _pick_value(slope_h6, "slope_bucket", "up_steep", "up_ratio")
    down_steep_mean = _pick_value(slope_h6, "slope_bucket", "down_steep", "mean_ret")
    down_steep_up = _pick_value(slope_h6, "slope_bucket", "down_steep", "up_ratio")
    up_mid_mean = _pick_value(slope_h6, "slope_bucket", "up_mid", "mean_ret")
    down_mid_mean = _pick_value(slope_h6, "slope_bucket", "down_mid", "mean_ret")

    support_curve = side_horizon[side_horizon["line_side"] == "support"].sort_values("horizon")
    resistance_curve = side_horizon[side_horizon["line_side"] == "resistance"].sort_values("horizon")
    support_curve_desc = " / ".join([f"h{int(r['horizon'])}={pct(float(r['mean_ret']))}" for _, r in support_curve.iterrows()])
    resistance_curve_desc = " / ".join([f"h{int(r['horizon'])}={pct(float(r['mean_ret']))}" for _, r in resistance_curve.iterrows()])
    side_gap_collapsed = abs(
        _pick_value(side_compare, "line_side", "support", "collapsed_mean_ret")
        - _pick_value(side_compare, "line_side", "resistance", "collapsed_mean_ret")
    )

    support_pos_syms = int(side_symbol_cons[side_symbol_cons["line_side"] == "support"]["pos_symbols"].iloc[0])
    support_neg_syms = int(side_symbol_cons[side_symbol_cons["line_side"] == "support"]["neg_symbols"].iloc[0])
    resistance_pos_syms = int(side_symbol_cons[side_symbol_cons["line_side"] == "resistance"]["pos_symbols"].iloc[0])
    resistance_neg_syms = int(side_symbol_cons[side_symbol_cons["line_side"] == "resistance"]["neg_symbols"].iloc[0])

    overall_chart_notes_html = note_block([
        ("怎么看", "先看均值是否明显远离 0，以及上涨占比是否明显偏离 50%。如果两者都贴近中性，说明 family 单变量解释力弱。"),
        ("图上结果", f"breakout：mean={pct(breakout_h6_mean)}、up={pct(breakout_h6_up)}；touch：mean={pct(touch_h6_mean)}、up={pct(touch_h6_up)}。两类都非常接近中性。"),
        ("这意味着什么", "breakout / touch 本身不够强，后续更应该看它和 side、slope 的联合结构，而不是单独拿 family 做信号。"),
        ("别过度解读", "这里不能据此说 touch 一定差、breakout 一定好；能得出的更稳结论只是：family 单变量不够有力。"),
    ])
    side_chart_notes_html = note_block([
        ("怎么看", "左边看 mean return 的正负和大小，右边看 up ratio 是否显著偏离 50%。如果两边同时同向，就说明这个维度更值得重视。"),
        ("图上结果", f"support：mean={pct(side_support_raw)}、up={pct(_pick_value(side_compare, 'line_side', 'support', 'raw_up_ratio'))}；resistance：mean={pct(side_resist_raw)}、up={pct(_pick_value(side_compare, 'line_side', 'resistance', 'raw_up_ratio'))}。两边几乎镜像。"),
        ("这意味着什么", "line side 是当前最清晰、最稳定的结构维度：support 更偏正向，resistance 更偏负向。"),
        ("别过度解读", "这更像“结构上下文”而不是现成交易规则；后面还要过可观测性、成本和切分验证。"),
    ])
    quality_chart_notes_html = note_block([
        ("怎么看", "如果 quality 真有信息量，high / mid / low 三档应该拉开明显间距，而且上涨占比也应同步分层。"),
        ("图上结果", f"high={pct(quality_high_mean)} / {pct(quality_high_up)}，mid={pct(quality_mid_mean)} / {pct(quality_mid_up)}，low={pct(quality_low_mean)} / {pct(quality_low_up)}；raw spread 只有 {bp(quality_raw_spread)}。"),
        ("这意味着什么", "quality 目前更像弱过滤假设，而不是强预测特征。"),
        ("别过度解读", "不要因为 high 略高于 low 就直接认为“高质量线可交易”；当前差距太小。"),
    ])
    slope_chart_notes_html = note_block([
        ("怎么看", "重点看方向和斜率强弱是否形成梯度：up_steep / up_mid 是否更偏正，down_steep / down_mid 是否更偏负。"),
        ("图上结果", f"up_steep={pct(up_steep_mean)}、up={pct(up_steep_up)}；down_steep={pct(down_steep_mean)}、up={pct(down_steep_up)}；up_mid={pct(up_mid_mean)}；down_mid={pct(down_mid_mean)}。方向梯度很明显。"),
        ("这意味着什么", "slope_direction 在描述性上是有东西的，尤其 steep 档最醒目。"),
        ("别过度解读", "它在更严格 lag<=1h 子样本里会明显衰减，所以现在更适合当候选特征，不适合直接当交易结论。"),
    ])
    side_horizon_notes_html = note_block([
        ("怎么看", "看两条线在不同 horizon 上是否持续分离；如果多个 horizon 都保持同方向，说明不是只在单个持有期偶然成立。"),
        ("图上结果", f"support 曲线：{support_curve_desc}；resistance 曲线：{resistance_curve_desc}。两条线从 h1 到 h24 始终分开。"),
        ("这意味着什么", "side 的方向性不是只在 1 个 horizon 上出现，而是具有一定持续性。"),
        ("别过度解读", "持续存在不等于可交易；因为这些事件很多并不是在当下就能观测到。"),
    ])
    side_robustness_notes_html = note_block([
        ("怎么看", "三组柱子分别回答三个问题：raw 会不会被重复线条夸大？collapsed 去重后还在不在？lag<=1h 下实时可用强度还剩多少？"),
        ("图上结果", f"raw gap={bp(side_gap_raw)}，collapsed gap={bp(side_gap_collapsed)}，lag<=1h gap={bp(side_gap_lag1)}；实时可用强度只保留约 {side_gap_lag1_ret*100:.1f}%。"),
        ("这意味着什么", "side 不是重复统计造成的假象，但它的“交易强度”会在更严格可观测条件下明显缩水。"),
        ("别过度解读", "不能只看 raw 柱子就宣布信号成立；真正要拿去做交易，必须看最右边那个 lag<=1h 版本。"),
    ])
    lag_chart_notes_html = note_block([
        ("怎么看", "这张图不是看收益，而是看“事件在多晚之后才被窗口看到”。分布越靠右，实时交易解释越危险。"),
        ("图上结果", f"median lag={reliability_overall['lag_median_h']:.1f}h，p95={reliability_overall['lag_p95_h']:.1f}h，lag==0 仅 {reliability_overall['lag0_share']*100:.1f}%，lag<=1h 仅 {reliability_overall['lag1_share']*100:.1f}%。"),
        ("这意味着什么", "这是当前整页报告最重要的方法风险：很多事件更像“事后在窗口里被确认”，而不是“当下可立即使用”。"),
        ("别过度解读", "这不是说结果没用，而是说它更适合做结构解释 / feature 候选，不该直接包装成实盘 alpha。"),
    ])
    heatmap_notes_html = note_block([
        ("怎么看", "逐行看每个币种，support 列应尽量为正、resistance 列应尽量为负；如果跨资产方向一致，说明不是单一资产偶然。"),
        ("图上结果", f"collapsed 后，support 在 {support_pos_syms} 个资产上为正、{support_neg_syms} 个为负；resistance 在 {resistance_neg_syms} 个资产上为负、{resistance_pos_syms} 个为正。这里是 6/6 一致。"),
        ("这意味着什么", "side 维度不仅在整体样本里成立，在 6 个资产上也呈现出相同方向，这是它最像“真结构”的地方。"),
        ("别过度解读", "样本仍然只有 6 个主流 crypto，不能直接外推出别的市场或更小币种。"),
    ])
    quality_robustness_notes_html = note_block([
        ("怎么看", "和 side robustness 一样：先看 raw，再看 collapsed，最后看 lag<=1h。真正稳的 quality 分层，三组柱子都应该方向一致且间距可观。"),
        ("图上结果", f"quality raw spread={bp(quality_raw_spread)}，collapsed spread={bp(quality_coll_spread)}，lag<=1h spread={bp(quality_lag1_spread)}；整体差距都不大，而且不够稳定。"),
        ("这意味着什么", "quality 目前不具备“拿来就能用”的解释力，更像待证伪的辅助过滤器。"),
        ("别过度解读", "不要因为 lag<=1h 某一档偶尔更高就强行下结论；这个维度目前最需要的是更多验证，而不是更强叙事。"),
    ])

    glossary_html = """
      <ul>
        <li><b>line：</b>pytrendline 自动识别出来的一条趋势线，不是人工主观手画的线。</li>
        <li><b>support line：</b>下方支撑线。可以粗略理解成“价格掉到这附近时，历史上更容易偏强”。</li>
        <li><b>resistance line：</b>上方压制线。可以粗略理解成“价格碰到这附近时，历史上更容易偏弱”。</li>
        <li><b>event：</b>价格和这条 line 发生一次我们关心的事件，比如触碰（touch）或突破（breakout）。</li>
        <li><b>h=6：</b>往后看 6 根 K 线。这里是 60m 数据，所以 h=6 就是往后看 6 小时。</li>
        <li><b>mean return：</b>这些历史事件发生后，未来 h 根 K 线收益的平均值。</li>
        <li><b>up ratio：</b>这些历史事件里，未来 h 根 K 线后价格上涨的比例。比如 65.38% 就是“100 次里大约 65 次上涨”。</li>
        <li><b>collapsed：</b>把同一个币、同一个时间点上重复/重叠的 line 先合并，避免同一时刻被重复计数。</li>
        <li><b>lag&lt;=1h：</b>只保留更接近“当下可看到”的事件，用来粗略测试实时交易可用性。</li>
      </ul>
    """

    q2_plain_html = f"""
      <div class='chart-notes'>
        <ul>
          <li><b>原句：</b>support mean={pct(side_support_raw)}、up={pct(side_support_up)}</li>
          <li><b>翻译成人话：</b>在 {side_support_events} 次 support 事件里，往后看 6 小时，大约每 100 次里有 65 次上涨；平均涨跌幅是 {pct(side_support_raw)}。</li>
          <li><b>再翻译短一点：</b>“遇到 support 这类事件时，历史上后面 6 小时更容易涨。”</li>
        </ul>
      </div>
    """

    summary_payload = {
        "symbols": SYMBOLS,
        "interval": INTERVAL,
        "period": PERIOD,
        "window_bars": WINDOW_BARS,
        "step_bars": STEP_BARS,
        "events": int(len(events)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "key_findings": findings,
        "qna": [{"q": q, "a": a} for q, a in qna],
        "reliability": reliability_overall,
    }
    (ART / "summary.json").write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>PyTrendline Event Validation v2</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }}
    .wrap {{ max-width: 1220px; margin: 0 auto; padding: 28px 18px 48px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px 22px; margin-bottom: 18px; }}
    .muted {{ color: #64748b; }}
    .warn {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; border-radius: 10px; padding: 10px 12px; }}
    .pill {{ display: inline-block; margin-right: 8px; margin-top: 8px; padding: 5px 10px; border-radius: 999px; background: #eef2ff; color: #3730a3; font-size: 12px; }}
    .tbl {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    .tbl th, .tbl td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .tbl th {{ background: #f8fafc; }}
    .qa-item {{ margin-bottom: 14px; }}
    .qa-q {{ font-weight: 700; margin-bottom: 4px; }}
    .qa-a {{ color: #334155; line-height: 1.7; }}
    .chart-notes {{ margin-top: 12px; color: #334155; }}
    .chart-notes ul {{ margin: 0; padding-left: 20px; }}
    ul {{ line-height: 1.7; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }}
    img.chart {{ width: 100%; max-width: 980px; border: 1px solid #e2e8f0; border-radius: 12px; background: white; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <p><a href=\"../../index.html\">← 返回站点首页</a></p>
    <div class=\"card\">
      <h1>PyTrendline Event Validation v2</h1>
      <p class=\"muted\">这页升级为“数据化 Q&A + 可信度分层”版本：不仅回答现象，还明确回答这些结论到底有多稳、哪里可能被样本结构误导。</p>
      <div>
        <span class=\"pill\">Generated: {escape(generated_at)}</span>
        <span class=\"pill\">symbols: {len(SYMBOLS)}</span>
        <span class=\"pill\">interval: {escape(INTERVAL)}</span>
        <span class=\"pill\">period: {escape(PERIOD)}</span>
        <span class=\"pill\">window_bars: {WINDOW_BARS}</span>
        <span class=\"pill\">step_bars: {STEP_BARS}</span>
        <span class=\"pill\">events: {len(events)}</span>
      </div>
    </div>

    <div class=\"card\">
      <h2>先把术语翻成人话</h2>
      {glossary_html}
    </div>

    <div class=\"card\">
      <h2>先看一个例子：Q2 那句话到底在说什么？</h2>
      {q2_plain_html}
    </div>

    <div class=\"card\">
      <h2>Q&amp;A · 数据化讲解</h2>
      {qna_html}
    </div>

    <div class=\"card\">
      <h2>结论可靠度分层（你问的“到底有多靠谱”）</h2>
      {render_table(reliability_df, limit=20)}
      <p class=\"warn\"><b>重要方法注记：</b>事件时间与窗口终点存在系统性 lag（median={reliability_overall['lag_median_h']:.1f}h，p95={reliability_overall['lag_p95_h']:.1f}h，lag==0 仅 {reliability_overall['lag0_share']*100:.1f}%）。
      因此当前更适合解释“结构现象”，不适合直接宣称“可实时交易 alpha”。</p>
    </div>

    <div class=\"card\">
      <h2>Key findings</h2>
      {findings_html(findings)}
    </div>

    <div class=\"card\">
      <h2>Chart 1 · Overall by family (h=6)</h2>
      <img class=\"chart\" src=\"overall_h6_mean.png\" alt=\"overall h6 mean return chart\" />
      {overall_chart_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 2 · Side summary (h=6)</h2>
      <img class=\"chart\" src=\"side_h6_dual.png\" alt=\"side dual chart\" />
      {side_chart_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 3 · Quality summary (h=6)</h2>
      <img class=\"chart\" src=\"quality_h6_dual.png\" alt=\"quality dual chart\" />
      {quality_chart_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 4 · Slope buckets (top by sample size, h=6)</h2>
      <img class=\"chart\" src=\"slope_h6_top8_dual.png\" alt=\"slope bucket chart\" />
      {slope_chart_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 5 · Side effect across horizons</h2>
      <img class=\"chart\" src=\"side_horizon_trend.png\" alt=\"side horizon trend chart\" />
      {side_horizon_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 6 · Side robustness (raw vs collapsed vs lag<=1h)</h2>
      <img class=\"chart\" src=\"side_robustness_h6.png\" alt=\"side robustness chart\" />
      {side_robustness_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 7 · Event lag distribution</h2>
      <img class=\"chart\" src=\"event_lag_hist.png\" alt=\"event lag histogram\" />
      {lag_chart_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 8 · Symbol × side heatmap (collapsed h=6)</h2>
      <img class=\"chart\" src=\"side_symbol_heatmap_h6.png\" alt=\"symbol side heatmap\" />
      {heatmap_notes_html}
    </div>

    <div class=\"card\">
      <h2>Chart 9 · Quality robustness (h=6)</h2>
      <img class=\"chart\" src=\"quality_robustness_h6.png\" alt=\"quality robustness chart\" />
      {quality_robustness_notes_html}
    </div>

    <div class=\"card\">
      <h2>后续研究建议（下一阶段）</h2>
      <ul>
        <li><b>R1. 先做 v3 严格可观测版：</b>只保留 event 在决策时刻可见的样本（或显式建模发布延迟），并对重叠事件做 purged/embargo 处理。</li>
        <li><b>R2. 从 event 统计切到 factor 验证：</b>把 side/slope 转成横截面特征，跑 IC/rank-IC/bucket spread，而不是只看 event 后均值。</li>
        <li><b>R3. 交易可实现性验证：</b>加入交易成本、滑点、换手约束，评估真实可部署收益质量。</li>
        <li><b>R4. 结构分解：</b>单独做 family×side×slope 交互项，确认哪些组合在严格可观测样本里还能保留方向性。</li>
        <li><b>R5. 稳健性协议：</b>固定训练/验证切分，做 walk-forward + 跨资产留一验证，避免“样本内解释好看”。</li>
      </ul>
    </div>

    <div class=\"card\">
      <h2>Symbol coverage</h2>
      {render_table(symbol_meta_df, limit=20)}
    </div>

    <div class=\"card\">
      <h2>Overall by family / horizon</h2>
      {render_table(overall, limit=40)}
    </div>

    <div class=\"card\">
      <h2>Side summary (h=6)</h2>
      {render_table(side_h6, limit=20)}
    </div>

    <div class=\"card\">
      <h2>Slope summary (h=6)</h2>
      {render_table(slope_h6, limit=30)}
    </div>

    <div class=\"card\">
      <h2>Quality summary (h=6)</h2>
      {render_table(quality_h6, limit=20)}
    </div>

    <div class=\"card\">
      <h2>Robustness tables</h2>
      <h3>Side robustness (h=6)</h3>
      {render_table(side_compare, limit=20)}
      <h3>Quality robustness (h=6)</h3>
      {render_table(quality_compare, limit=20)}
    </div>

    <div class=\"card\">
      <h2>Artifacts</h2>
      <ul>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/event_sample.csv'>event_sample.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/symbol_meta.csv'>symbol_meta.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/overall_by_family_horizon.csv'>overall_by_family_horizon.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/side_summary_h6.csv'>side_summary_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/slope_summary_h6.csv'>slope_summary_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/quality_summary_h6.csv'>quality_summary_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/side_horizon_summary.csv'>side_horizon_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/side_robustness_h6.csv'>side_robustness_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/slope_robustness_h6.csv'>slope_robustness_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/quality_robustness_h6.csv'>quality_robustness_h6.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/reliability_matrix.csv'>reliability_matrix.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/lag_summary.csv'>lag_summary.csv</a></li>
        <li><a href='../../artifacts/pytrendline_event_validation_v2/summary.json'>summary.json</a></li>
      </ul>
    </div>
  </div>
</body>
</html>
"""

    (SITE / "report.html").write_text(html, encoding="utf-8")
    print(f"[ok] pytrendline event validation v2 page -> {SITE / 'report.html'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
