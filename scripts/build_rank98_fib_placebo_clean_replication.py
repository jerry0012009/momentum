#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank98_fib_placebo_honesty_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank98_fib_placebo_honesty_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank98_fib_placebo_honesty_clean_replication.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
LOOKBACK = 50
VOL_PERIOD = 24
ATR_PERIOD = 14
EMA_FAST = 9
EMA_SLOW = 26
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANTS = ["fib_exact", "fib_zone_015", "fib_zone_030", "placebo_zone_mean"]
ALL_VARIANTS = PRIMARY_VARIANTS + ["placebo_zone_each"]
FIB_NEIGHBORS = [0.236, 0.382, 0.5, 0.618, 0.786]
RNG_SEED = 20260319
PLACEBO_COUNT = 24
ZONE_MAP = {
    "fib_exact": 0.0,
    "fib_zone_015": 0.15,
    "fib_zone_030": 0.30,
    "placebo_zone_each": 0.30,
}
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f'<td>{escape(text)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def build_placebo_ratios() -> list[float]:
    rng = np.random.default_rng(RNG_SEED)
    picked: list[float] = []
    attempts = 0
    while len(picked) < PLACEBO_COUNT and attempts < 5000:
        attempts += 1
        candidate = float(np.round(rng.uniform(0.18, 0.82), 3))
        if any(abs(candidate - fib) <= 0.03 for fib in FIB_NEIGHBORS):
            continue
        if any(abs(candidate - x) < 0.012 for x in picked):
            continue
        picked.append(candidate)
    return sorted(picked)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["volume_sma24"] = df["volume"].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df["atr14"] = atr(df)
    df["swing_high"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df["swing_low"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    df["swing_range"] = df["swing_high"] - df["swing_low"]
    df["fib_50"] = df["swing_high"] - 0.5 * df["swing_range"]
    df["trend_ok"] = ((df["ema9"] > df["ema26"]) & (df["ema_slope"] > 0) & (df["volume"] > df["volume_sma24"]) & (df["swing_range"] > 0)).fillna(False)
    return df


def variant_reference(frame: pd.DataFrame, variant: str, placebo_ratio: float | None = None) -> pd.Series:
    if variant.startswith("fib_"):
        ratio = 0.618
    else:
        assert placebo_ratio is not None
        ratio = placebo_ratio
    return frame["swing_high"] - ratio * frame["swing_range"]


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float, placebo_ratio: float | None = None) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0
    zone_mult = ZONE_MAP[variant]
    ref = variant_reference(frame, variant, placebo_ratio)

    reclaim = (frame["close"] > ref) & (frame["close"].shift(1) <= ref.shift(1))
    low_touches = frame["low"] <= (ref + zone_mult * frame["atr14"])
    signal = (frame["trend_ok"] & reclaim & low_touches).fillna(False)

    for idx in range(LOOKBACK + 5, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx or not bool(signal.iloc[idx]):
            continue
        fib50 = float(frame.iloc[idx]["fib_50"])
        ref_px = float(ref.iloc[idx])
        atr14 = float(frame.iloc[idx]["atr14"])
        if not (np.isfinite(fib50) and np.isfinite(ref_px) and np.isfinite(atr14) and atr14 > 0):
            continue
        signal_events += 1
        entry_idx = idx + 1
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS)
        window = frame.iloc[entry_idx : exit_idx + 1]
        early_window = frame.iloc[entry_idx : min(len(frame), entry_idx + EARLY_FAIL_BARS)]
        false_rebreak = int((early_window["close"] < fib50).any()) if len(early_window) else 0
        hold_4bars = int(false_rebreak == 0 and len(early_window) >= EARLY_FAIL_BARS)
        max_high = float(window["high"].max()) if len(window) else entry_px
        best_move = max_high / entry_px - 1.0
        mae = float((window["low"] / entry_px - 1.0).min()) if len(window) else 0.0
        fail_close = False
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        for j in range(entry_idx, exit_idx + 1):
            if float(frame.iloc[j]["close"]) < fib50:
                actual_exit_idx = j
                exit_reason = "fib50_fail"
                fail_close = True
                break
        exit_px = float(frame.iloc[actual_exit_idx]["open"] if actual_exit_idx + 1 < len(frame) else frame.iloc[actual_exit_idx]["close"])
        gross_ret = exit_px / entry_px - 1.0
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "placebo_ratio": placebo_ratio if placebo_ratio is not None else np.nan,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[actual_exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "post_cost_expectancy": net_ret,
                "hold_4bars": hold_4bars,
                "false_rebreak_4bars": false_rebreak,
                "fail_close": int(fail_close),
                "best_move": best_move,
                "mae": mae,
                "atr14": atr14,
                "reference_price": ref_px,
                "fib50": fib50,
                "zone_mult_atr": zone_mult,
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = actual_exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_asset(trades: pd.DataFrame, asset: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "post_cost_expectancy": np.nan,
            "hold_4bars_rate": np.nan,
            "false_rebreak_4bars_rate": np.nan,
            "fail_close_rate": np.nan,
            "best_move": np.nan,
            "mae": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "post_cost_expectancy": float(trades["post_cost_expectancy"].mean()),
        "hold_4bars_rate": float(trades["hold_4bars"].mean()),
        "false_rebreak_4bars_rate": float(trades["false_rebreak_4bars"].mean()),
        "fail_close_rate": float(trades["fail_close"].mean()),
        "best_move": float(trades["best_move"].mean()),
        "mae": float(trades["mae"].mean()),
    }


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if grp["trade_count_retention"].notna().any() else np.nan,
                "mean_post_cost_expectancy": float(grp["post_cost_expectancy"].mean()) if grp["post_cost_expectancy"].notna().any() else np.nan,
                "mean_hold_4bars_rate": float(grp["hold_4bars_rate"].mean()) if grp["hold_4bars_rate"].notna().any() else np.nan,
                "mean_false_rebreak_4bars_rate": float(grp["false_rebreak_4bars_rate"].mean()) if grp["false_rebreak_4bars_rate"].notna().any() else np.nan,
                "mean_fail_close_rate": float(grp["fail_close_rate"].mean()) if grp["fail_close_rate"].notna().any() else np.nan,
                "mean_best_move": float(grp["best_move"].mean()) if grp["best_move"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def render_summary_html(primary: pd.DataFrame, asset_primary: pd.DataFrame, placebo_head: pd.DataFrame, placebo_meta: list[float], meta: dict[str, object]) -> str:
    verdict_class = "good" if meta["hard_verdict"].startswith("keep") else "bad"
    body = [
        f"<h1>Rank 98 / Fib placebo honesty gate — 最小 clean replication</h1>",
        f"<p class='muted'>生成时间：{escape(str(meta['generated_at_utc']))}</p>",
        "<div class='card'>",
        "<h2>一句话结论</h2>",
        f"<p class='{verdict_class}'>{escape(str(meta['headline']))}</p>",
        f"<p>{escape(str(meta['plain_language']))}</p>",
        "</div>",
        "<div class='card'>",
        "<h2>这轮怎么做</h2>",
        "<ul>",
        "<li>固定 BTC / ETH / SOL、120d、15m 本地 cache。</li>",
        "<li>统一冻结到 signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars。</li>",
        "<li>比较 fib_exact、fib_zone_015、fib_zone_030 与 placebo_zone_mean。</li>",
        f"<li>placebo ratio 固定随机种子 {RNG_SEED}，共 {len(placebo_meta)} 个，且排除 Fib 邻域。</li>",
        "</ul>",
        "</div>",
        "<div class='card'><h2>总体结果（主口径 6bps/side）</h2>",
        render_table(
            primary[[
                "variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_post_cost_expectancy", "mean_hold_4bars_rate", "mean_false_rebreak_4bars_rate", "mean_fail_close_rate"
            ]],
            percent_cols={"mean_total_return", "positive_asset_ratio", "mean_post_cost_expectancy", "mean_hold_4bars_rate", "mean_false_rebreak_4bars_rate", "mean_fail_close_rate"},
            digits_cols={"mean_trades": 1},
        ),
        "</div>",
        "<div class='card'><h2>资产侧（主口径 6bps/side）</h2>",
        render_table(
            asset_primary[[
                "asset", "variant", "total_return", "trades", "post_cost_expectancy", "hold_4bars_rate", "false_rebreak_4bars_rate", "fail_close_rate"
            ]],
            percent_cols={"total_return", "post_cost_expectancy", "hold_4bars_rate", "false_rebreak_4bars_rate", "fail_close_rate"},
            digits_cols={"trades": 0},
        ),
        "</div>",
        "<div class='card'><h2>placebo ratio 样本（主口径 6bps/side，前 12 条）</h2>",
        render_table(
            placebo_head,
            percent_cols={"mean_total_return", "positive_asset_ratio", "mean_post_cost_expectancy", "mean_hold_4bars_rate", "mean_false_rebreak_4bars_rate"},
            digits_cols={"ratio": 3, "mean_trades": 1},
        ),
        "</div>",
        "<div class='card'><h2>为什么是这个 verdict</h2><ul>",
        "<li>如果 fib_zone 的改善只是因为 zone 放宽，而 placebo_zone_mean 也同步改善，那就不该继续把 0.618 写成特殊 ratio edge。</li>",
        "<li>这轮最重要的不是把 Fib 线救活，而是诚实回答：它到底是 ratio 优势，还是 generic retrace scaffold。</li>",
        "</ul></div>",
    ]
    return ''.join(body)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    placebo_ratios = build_placebo_ratios()
    Path(ART_DIR / "placebo_ratios.json").write_text(json.dumps(placebo_ratios, ensure_ascii=False, indent=2), encoding="utf-8")

    all_trades = []
    asset_rows = []
    placebo_ratio_rows = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.replace('-', '_').lower()}_frame.csv", index=False)
        for cost in COSTS:
            for variant in ["fib_exact", "fib_zone_015", "fib_zone_030"]:
                trades, signal_events = build_trades(frame, asset, variant, cost)
                if not trades.empty:
                    all_trades.append(trades)
                asset_rows.append(summarize_asset(trades, asset, variant, cost, signal_events))

            placebo_asset_rows = []
            placebo_trade_frames = []
            for ratio in placebo_ratios:
                trades, signal_events = build_trades(frame, asset, "placebo_zone_each", cost, placebo_ratio=ratio)
                if not trades.empty:
                    placebo_trade_frames.append(trades)
                    all_trades.append(trades)
                summary = summarize_asset(trades, asset, "placebo_zone_each", cost, signal_events)
                summary["ratio"] = ratio
                placebo_asset_rows.append(summary)
            placebo_asset_df = pd.DataFrame(placebo_asset_rows)
            placebo_asset_df.to_csv(ART_DIR / f"placebo_ratio_asset_summary_{asset.replace('-', '_').lower()}_{int(cost)}bps.csv", index=False)
            if not placebo_asset_df.empty:
                agg = {
                    "asset": asset,
                    "variant": "placebo_zone_mean",
                    "cost_bps_per_side": float(cost),
                    "signal_events": float(placebo_asset_df["signal_events"].mean()),
                    "trades": float(placebo_asset_df["trades"].mean()),
                    "trade_count_retention": float(placebo_asset_df["trade_count_retention"].mean()),
                    "total_return": float(placebo_asset_df["total_return"].mean()),
                    "avg_net_ret": float(placebo_asset_df["avg_net_ret"].mean()) if placebo_asset_df["avg_net_ret"].notna().any() else np.nan,
                    "post_cost_expectancy": float(placebo_asset_df["post_cost_expectancy"].mean()) if placebo_asset_df["post_cost_expectancy"].notna().any() else np.nan,
                    "hold_4bars_rate": float(placebo_asset_df["hold_4bars_rate"].mean()) if placebo_asset_df["hold_4bars_rate"].notna().any() else np.nan,
                    "false_rebreak_4bars_rate": float(placebo_asset_df["false_rebreak_4bars_rate"].mean()) if placebo_asset_df["false_rebreak_4bars_rate"].notna().any() else np.nan,
                    "fail_close_rate": float(placebo_asset_df["fail_close_rate"].mean()) if placebo_asset_df["fail_close_rate"].notna().any() else np.nan,
                    "best_move": float(placebo_asset_df["best_move"].mean()) if placebo_asset_df["best_move"].notna().any() else np.nan,
                    "mae": float(placebo_asset_df["mae"].mean()) if placebo_asset_df["mae"].notna().any() else np.nan,
                }
                asset_rows.append(agg)
            ratio_grp = placebo_asset_df.groupby("ratio", sort=True).agg(
                mean_total_return=("total_return", "mean"),
                positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
                mean_trades=("trades", "mean"),
                mean_post_cost_expectancy=("post_cost_expectancy", "mean"),
                mean_hold_4bars_rate=("hold_4bars_rate", "mean"),
                mean_false_rebreak_4bars_rate=("false_rebreak_4bars_rate", "mean"),
            ).reset_index()
            ratio_grp["cost_bps_per_side"] = cost
            placebo_ratio_rows.append(ratio_grp)

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_df = pd.DataFrame(asset_rows)
    overall_df = summarize_overall(asset_df)
    primary_overall = overall_df[(overall_df["cost_bps_per_side"] == PRIMARY_COST) & (overall_df["variant"].isin(PRIMARY_VARIANTS))].copy()
    primary_overall["variant"] = pd.Categorical(primary_overall["variant"], PRIMARY_VARIANTS, ordered=True)
    primary_overall = primary_overall.sort_values("variant").reset_index(drop=True)
    asset_primary = asset_df[(asset_df["cost_bps_per_side"] == PRIMARY_COST) & (asset_df["variant"].isin(PRIMARY_VARIANTS))].copy()
    asset_primary["variant"] = pd.Categorical(asset_primary["variant"], PRIMARY_VARIANTS, ordered=True)
    asset_primary = asset_primary.sort_values(["variant", "asset"]).reset_index(drop=True)
    placebo_ratio_df = pd.concat(placebo_ratio_rows, ignore_index=True) if placebo_ratio_rows else pd.DataFrame()
    placebo_head = placebo_ratio_df[placebo_ratio_df["cost_bps_per_side"] == PRIMARY_COST].sort_values("mean_total_return", ascending=False).head(12).copy()
    placebo_head = placebo_head.rename(columns={"mean_post_cost_expectancy": "mean_post_cost_expectancy", "ratio": "ratio"})

    trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    primary_overall.to_csv(ART_DIR / "overall_summary_primary_6bps.csv", index=False)
    asset_primary.to_csv(ART_DIR / "asset_summary_primary_6bps.csv", index=False)
    placebo_ratio_df.to_csv(ART_DIR / "placebo_ratio_summary.csv", index=False)

    fib_exact = primary_overall[primary_overall["variant"] == "fib_exact"].iloc[0] if (primary_overall["variant"] == "fib_exact").any() else None
    fib_zone_030 = primary_overall[primary_overall["variant"] == "fib_zone_030"].iloc[0] if (primary_overall["variant"] == "fib_zone_030").any() else None
    placebo_mean = primary_overall[primary_overall["variant"] == "placebo_zone_mean"].iloc[0] if (primary_overall["variant"] == "placebo_zone_mean").any() else None

    fib_improves_vs_exact = float(fib_zone_030["mean_post_cost_expectancy"] - fib_exact["mean_post_cost_expectancy"]) if fib_exact is not None and fib_zone_030 is not None else np.nan
    placebo_gap = float(fib_zone_030["mean_post_cost_expectancy"] - placebo_mean["mean_post_cost_expectancy"]) if fib_zone_030 is not None and placebo_mean is not None else np.nan

    if pd.notna(placebo_gap) and placebo_gap <= 0.0005:
        verdict = "park"
        headline = "Rank 98 = park：这轮改善主要像 zone 放宽带来的 generic retrace scaffold，不像 0.618 本身有独立增量信息。"
        plain = "换成人话：Fib 不是完全没用，但这轮最小 clean replication 没证明 0.618 比一批非 Fib placebo zone 更特别。"
    elif fib_zone_030 is not None and fib_zone_030["mean_post_cost_expectancy"] > 0 and placebo_mean is not None and placebo_gap > 0.001:
        verdict = "keep_P1"
        headline = "Rank 98 = keep_P1：Fib zone 比 placebo zone 还有一点增量，但还不够直接升格。"
        plain = "这说明 Fib 线还没死，但也远不到可以重新神化 0.618 的程度。"
    else:
        verdict = "park"
        headline = "Rank 98 = park：Fib zone 虽比 exact 好一点，但 placebo zone 也差不多，当前不值得继续占 Scout 主资源。"
        plain = "更诚实的做法是把 Fib 降级成坐标系 / 回踩 scaffold，把真正的 edge 继续放回 volume、trend、failure path。"

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "hard_verdict": verdict,
        "headline": headline,
        "plain_language": plain,
        "fib_zone_030_minus_exact": fib_improves_vs_exact,
        "fib_zone_030_minus_placebo": placebo_gap,
        "primary_cost_bps": PRIMARY_COST,
        "placebo_ratios": placebo_ratios,
    }
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    page_title = "Rank 98 / Fib placebo honesty gate"
    html = render_summary_html(primary_overall, asset_primary, placebo_head, placebo_ratios, meta)
    write_html(SITE_DIR / "report.html", page_title, html)
    write_html(READING_PATH, page_title + " clean replication", html)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
