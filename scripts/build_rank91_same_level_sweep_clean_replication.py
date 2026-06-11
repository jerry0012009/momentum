#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank91_same_level_sweep_count_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank91_same_level_sweep_count_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank91_same_level_sweep_count_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["baseline", "single_sweep_gate", "consec2plus_gate", "consec2plus_plus_body_or_small_retest"]
PRIMARY_VARIANT = "consec2plus_gate"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
LOOKBACK = 20
SWEEP_WINDOW = 10
LEVEL_TOL = 0.005
VOL_GATE = 1.2
EPS = 1e-12
CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
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


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def compute_psar(df: pd.DataFrame, step: float = 0.02, max_step: float = 0.2) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    psar = np.full(n, np.nan)
    bull = True
    af = step
    ep = high[0]
    psar[0] = low[0]
    if n > 1:
        bull = high[1] >= high[0]
        ep = high[1] if bull else low[1]
        psar[1] = min(low[0], low[1]) if bull else max(high[0], high[1])
    for i in range(2, n):
        prev_psar = psar[i - 1]
        if bull:
            cur = prev_psar + af * (ep - prev_psar)
            cur = min(cur, low[i - 1], low[i - 2])
            if low[i] < cur:
                bull = False
                cur = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(max_step, af + step)
        else:
            cur = prev_psar + af * (ep - prev_psar)
            cur = max(cur, high[i - 1], high[i - 2])
            if high[i] > cur:
                bull = True
                cur = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(max_step, af + step)
        psar[i] = cur
    return pd.Series(psar, index=df.index)


def build_sweep_overlay(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["vol_ma20"] = out["volume"].rolling(20, min_periods=20).mean()
    out["vol_ratio"] = out["volume"] / out["vol_ma20"]
    out["prior_high_20"] = out["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    out["prior_low_20"] = out["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    out["bull_sweep_event"] = (
        out["prior_low_20"].notna()
        & (out["low"] < out["prior_low_20"])
        & (out["close"] >= out["prior_low_20"])
        & (out["vol_ratio"] >= VOL_GATE)
    ).fillna(False)
    out["bear_sweep_event"] = (
        out["prior_high_20"].notna()
        & (out["high"] > out["prior_high_20"])
        & (out["close"] <= out["prior_high_20"])
        & (out["vol_ratio"] >= VOL_GATE)
    ).fillna(False)

    bull_count = np.zeros(len(out), dtype=int)
    bear_count = np.zeros(len(out), dtype=int)
    last_bull_idx = None
    last_bull_level = None
    last_bull_count = 0
    last_bear_idx = None
    last_bear_level = None
    last_bear_count = 0

    close = out["close"].to_numpy(dtype=float)
    for i in range(len(out)):
        if bool(out.iloc[i]["bull_sweep_event"]):
            level = float(out.iloc[i]["prior_low_20"])
            same = (
                last_bull_idx is not None
                and i - int(last_bull_idx) <= SWEEP_WINDOW
                and abs(level - float(last_bull_level)) <= LEVEL_TOL * max(close[i], EPS)
            )
            bull_count[i] = last_bull_count + 1 if same else 1
            last_bull_idx = i
            last_bull_level = level
            last_bull_count = bull_count[i]
        if bool(out.iloc[i]["bear_sweep_event"]):
            level = float(out.iloc[i]["prior_high_20"])
            same = (
                last_bear_idx is not None
                and i - int(last_bear_idx) <= SWEEP_WINDOW
                and abs(level - float(last_bear_level)) <= LEVEL_TOL * max(close[i], EPS)
            )
            bear_count[i] = last_bear_count + 1 if same else 1
            last_bear_idx = i
            last_bear_level = level
            last_bear_count = bear_count[i]

    out["bull_sweep_count"] = bull_count
    out["bear_sweep_count"] = bear_count
    out["recent_bull_sweep_count"] = out["bull_sweep_count"].rolling(SWEEP_WINDOW, min_periods=1).max().fillna(0).astype(int)
    out["recent_bear_sweep_count"] = out["bear_sweep_count"].rolling(SWEEP_WINDOW, min_periods=1).max().fillna(0).astype(int)

    bar_range = (out["high"] - out["low"]).clip(lower=EPS)
    body = (out["close"] - out["open"]).abs()
    out["body_ratio"] = body / bar_range
    out["lower_wick_ratio"] = (np.minimum(out["open"], out["close"]) - out["low"]).clip(lower=0) / bar_range
    out["upper_wick_ratio"] = (out["high"] - np.maximum(out["open"], out["close"])).clip(lower=0) / bar_range
    out["small_body"] = out["body_ratio"] <= 0.45
    out["long_small_retest"] = out["small_body"] | (out["lower_wick_ratio"] >= 0.35)
    out["short_small_retest"] = out["small_body"] | (out["upper_wick_ratio"] >= 0.35)
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = atr(df)
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_382"] = df["swing_low_30"] + 0.382 * rng
    df["fib_500"] = df["swing_low_30"] + 0.500 * rng
    df["fib_618"] = df["swing_low_30"] + 0.618 * rng
    df["donchian_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    vol_ma20 = df["volume"].rolling(20, min_periods=20).mean()

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0.0002)
        & (df["psar"] < df["close"])
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["close"] > df["ema9"])
        & (df["close"] > df["high"].shift(1) - 0.15 * df["atr14"])
        & (df["volume"] > vol_ma20)
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0)
        & (df["low"] <= df["fib_618"] + 0.15 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["close"].shift(1) <= df["fib_500"].shift(1))
        & (df["volume"] > vol_ma20)
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["donchian_low"].notna()
        & (df["ema9"] < df["ema21"])
        & (df["ema_slope"] < -0.0002)
        & (df["close"].shift(1) > df["donchian_low"].shift(1))
        & (df["close"] < df["donchian_low"] - 0.1 * df["atr14"])
        & (df["volume"] > vol_ma20)
    ).fillna(False)

    return build_sweep_overlay(df)


def variant_policy(row: pd.Series, setup: str, variant: str) -> tuple[bool, str]:
    is_long = setup.endswith("long")
    sweep_count = int(row["recent_bull_sweep_count"] if is_long else row["recent_bear_sweep_count"])
    if variant == "baseline":
        return True, "baseline"
    if variant == "single_sweep_gate":
        allow = sweep_count >= 1
        return allow, f"sweep_count={sweep_count}"
    if variant == "consec2plus_gate":
        allow = sweep_count >= 2
        return allow, f"sweep_count={sweep_count}"
    extra_ok = bool(row["long_small_retest"] if is_long else row["short_small_retest"])
    allow = sweep_count >= 2 and extra_ok
    return allow, f"sweep_count={sweep_count}|extra={int(extra_ok)}"


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal_col = f"{setup}_signal"
    rows = []
    signal_events = 0
    last_exit_idx = -1
    direction = -1.0 if setup.endswith("short") else 1.0
    cost_rate = float(cost_bps) / 10000.0

    ts = frame["timestamp"].to_numpy()
    opens = frame["open"].to_numpy(dtype=float)
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    signal_mask = frame[signal_col].to_numpy(dtype=bool)

    for idx in range(60, len(frame) - HOLD_BARS - 1):
        if idx <= last_exit_idx:
            continue
        if not bool(signal_mask[idx]):
            continue
        signal_events += 1
        row = frame.iloc[idx]
        allow, gate_reason = variant_policy(row, setup, variant)
        if not allow:
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        entry_price = opens[entry_idx]
        exit_price = closes[exit_idx]
        raw_return = direction * (exit_price - entry_price) / max(entry_price, EPS)
        net_return = raw_return - 2.0 * cost_rate
        path_slice = slice(entry_idx, min(exit_idx + 1, entry_idx + EARLY_FAIL_BARS + 1))
        if direction > 0:
            early_fail = float(np.min(lows[path_slice]) < entry_price)
            hold4 = float(closes[min(entry_idx + EARLY_FAIL_BARS - 1, len(frame) - 1)] > entry_price)
        else:
            early_fail = float(np.max(highs[path_slice]) > entry_price)
            hold4 = float(closes[min(entry_idx + EARLY_FAIL_BARS - 1, len(frame) - 1)] < entry_price)
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "cost_bps": cost_bps,
                "signal_timestamp": ts[idx],
                "entry_timestamp": ts[entry_idx],
                "exit_timestamp": ts[exit_idx],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "raw_return": raw_return,
                "net_return": net_return,
                "hold4": hold4,
                "early_fail_4bars": early_fail,
                "gate_reason": gate_reason,
                "recent_bull_sweep_count": int(row["recent_bull_sweep_count"]),
                "recent_bear_sweep_count": int(row["recent_bear_sweep_count"]),
                "body_ratio": float(row["body_ratio"]),
                "lower_wick_ratio": float(row["lower_wick_ratio"]),
                "upper_wick_ratio": float(row["upper_wick_ratio"]),
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize(trades: pd.DataFrame, signal_events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall_rows = []
    asset_rows = []
    setup_rows = []
    time_rows = []
    for cost in COSTS:
        base_trades = trades[(trades["cost_bps"] == cost) & (trades["variant"] == "baseline")]
        base_by_asset = base_trades.groupby("asset").size().to_dict()
        for variant in VARIANTS:
            subset = trades[(trades["cost_bps"] == cost) & (trades["variant"] == variant)]
            if subset.empty:
                continue
            grouped = subset.groupby("asset")["net_return"].sum()
            overall_rows.append(
                {
                    "cost_bps": cost,
                    "variant": variant,
                    "mean_total_return": grouped.mean(),
                    "positive_asset_ratio": (grouped > 0).mean(),
                    "mean_trades": subset.groupby("asset").size().mean(),
                    "trade_count_retention": np.mean([
                        subset[subset["asset"] == asset].shape[0] / max(base_by_asset.get(asset, 1), 1)
                        for asset in ASSETS
                    ]),
                    "mean_hold4": subset["hold4"].mean(),
                    "mean_early_fail_4bars": subset["early_fail_4bars"].mean(),
                }
            )

        primary = trades[(trades["cost_bps"] == cost) & (trades["variant"] == PRIMARY_VARIANT)]
        if primary.empty:
            continue
        if cost == PRIMARY_COST:
            for asset, asset_df in primary.groupby("asset"):
                asset_rows.append(
                    {
                        "asset": asset,
                        "trades": len(asset_df),
                        "total_return": asset_df["net_return"].sum(),
                        "mean_return": asset_df["net_return"].mean(),
                        "hold4": asset_df["hold4"].mean(),
                        "early_fail_4bars": asset_df["early_fail_4bars"].mean(),
                        "bull_count_median": asset_df["recent_bull_sweep_count"].median(),
                        "bear_count_median": asset_df["recent_bear_sweep_count"].median(),
                    }
                )
            for setup, setup_df in primary.groupby("setup"):
                base_setup = trades[(trades["cost_bps"] == cost) & (trades["variant"] == "baseline") & (trades["setup"] == setup)]
                setup_rows.append(
                    {
                        "setup": setup,
                        "trades": len(setup_df),
                        "baseline_trades": len(base_setup),
                        "trade_count_retention": len(setup_df) / max(len(base_setup), 1),
                        "mean_return": setup_df["net_return"].mean(),
                        "total_return": setup_df["net_return"].sum(),
                        "hold4": setup_df["hold4"].mean(),
                        "early_fail_4bars": setup_df["early_fail_4bars"].mean(),
                    }
                )
            ordered = primary.sort_values("entry_timestamp").reset_index(drop=True)
            ordered["bucket"] = pd.qcut(np.arange(len(ordered)), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
            for bucket, bucket_df in ordered.groupby("bucket"):
                grouped = bucket_df.groupby("asset")["net_return"].sum()
                time_rows.append(
                    {
                        "bucket": bucket,
                        "mean_total_return": grouped.mean(),
                        "positive_asset_ratio": (grouped > 0).mean(),
                        "mean_hold4": bucket_df["hold4"].mean(),
                        "mean_early_fail_4bars": bucket_df["early_fail_4bars"].mean(),
                        "trades": len(bucket_df),
                    }
                )
    return (
        pd.DataFrame(overall_rows),
        pd.DataFrame(asset_rows),
        pd.DataFrame(setup_rows),
        pd.DataFrame(time_rows),
    )


def verdict_from_summary(overall: pd.DataFrame) -> str:
    row = overall[(overall["cost_bps"] == PRIMARY_COST) & (overall["variant"] == PRIMARY_VARIANT)].iloc[0]
    if (
        row["mean_total_return"] > 0
        and row["positive_asset_ratio"] >= 2 / 3
        and row["trade_count_retention"] >= 0.25
        and row["mean_early_fail_4bars"] <= 0.50
    ):
        return "promote_to_P2"
    baseline = overall[(overall["cost_bps"] == PRIMARY_COST) & (overall["variant"] == "baseline")].iloc[0]
    if row["mean_total_return"] > baseline["mean_total_return"] or row["positive_asset_ratio"] > baseline["positive_asset_ratio"]:
        return "keep_P1"
    return "park"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    all_trades = []
    signal_rows = []
    for asset, frame in frames.items():
        for cost in COSTS:
            for setup in SETUPS:
                for variant in VARIANTS:
                    trades, signal_events = build_trades(frame, asset, setup, variant, cost)
                    all_trades.append(trades)
                    signal_rows.append(
                        {
                            "asset": asset,
                            "setup": setup,
                            "variant": variant,
                            "cost_bps": cost,
                            "signal_events": signal_events,
                            "executed_trades": len(trades),
                        }
                    )
    trades = pd.concat(all_trades, ignore_index=True)
    signal_df = pd.DataFrame(signal_rows)
    overall, asset_summary, setup_summary, time_summary = summarize(trades, signal_df)
    verdict = verdict_from_summary(overall)

    primary_row = overall[(overall["cost_bps"] == PRIMARY_COST) & (overall["variant"] == PRIMARY_VARIANT)].iloc[0]
    baseline_row = overall[(overall["cost_bps"] == PRIMARY_COST) & (overall["variant"] == "baseline")].iloc[0]
    meta = pd.DataFrame(
        [
            {
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "primary_variant": PRIMARY_VARIANT,
                "primary_cost_bps": PRIMARY_COST,
                "hard_verdict": verdict,
                "primary_mean_total_return": primary_row["mean_total_return"],
                "primary_positive_asset_ratio": primary_row["positive_asset_ratio"],
                "primary_trade_count_retention": primary_row["trade_count_retention"],
                "primary_mean_hold4": primary_row["mean_hold4"],
                "primary_mean_early_fail_4bars": primary_row["mean_early_fail_4bars"],
                "baseline_mean_total_return": baseline_row["mean_total_return"],
                "baseline_positive_asset_ratio": baseline_row["positive_asset_ratio"],
            }
        ]
    )

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    time_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    signal_df.to_csv(ART_DIR / "signal_summary.csv", index=False)
    trades[(trades["cost_bps"] == PRIMARY_COST) & (trades["variant"] == PRIMARY_VARIANT)].to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    verdict_cn = {"promote_to_P2": "升到 P2 / paper candidate", "keep_P1": "保留 P1 / evidence_pool", "park": "压回 park / evidence_pool"}[verdict]
    summary_body = f"""
    <h1>Rank 91 / same-level consecutive sweep count clean replication</h1>
    <p class="muted">固定 BTC/ETH/SOL 120d 15m 本地 cache，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>；比较 baseline / single_sweep_gate / consec2plus_gate / consec2plus_plus_body_or_small_retest。</p>
    <div class="card">
      <h2>Hard verdict</h2>
      <p><strong>{escape(verdict_cn)}</strong></p>
      <ul>
        <li>baseline @6bps：mean_total_return={pct(baseline_row['mean_total_return'])}，positive_asset_ratio={pct(baseline_row['positive_asset_ratio'])}，trade_count_retention={pct(baseline_row['trade_count_retention'])}</li>
        <li>{PRIMARY_VARIANT} @6bps：mean_total_return={pct(primary_row['mean_total_return'])}，positive_asset_ratio={pct(primary_row['positive_asset_ratio'])}，trade_count_retention={pct(primary_row['trade_count_retention'])}</li>
        <li>hold4={pct(primary_row['mean_hold4'])}，early_fail_4bars={pct(primary_row['mean_early_fail_4bars'])}</li>
      </ul>
    </div>
    <div class="card">
      <h2>overall summary</h2>
      {render_table(overall.sort_values(['cost_bps','variant']), percent_cols={'mean_total_return','positive_asset_ratio','trade_count_retention','mean_hold4','mean_early_fail_4bars'})}
    </div>
    <div class="card">
      <h2>asset summary ({PRIMARY_VARIANT} @ 6bps)</h2>
      {render_table(asset_summary, percent_cols={'total_return','mean_return','hold4','early_fail_4bars'})}
    </div>
    <div class="card">
      <h2>setup summary ({PRIMARY_VARIANT} @ 6bps)</h2>
      {render_table(setup_summary, percent_cols={'trade_count_retention','mean_return','total_return','hold4','early_fail_4bars'})}
    </div>
    <div class="card">
      <h2>time pocket summary ({PRIMARY_VARIANT} @ 6bps)</h2>
      {render_table(time_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_hold4','mean_early_fail_4bars'})}
    </div>
    <div class="card">
      <h2>artifacts</h2>
      <ul>
        <li><a href="../../artifacts/scout_rank91_same_level_sweep_count_15m/overall_summary.csv">overall_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank91_same_level_sweep_count_15m/asset_summary.csv">asset_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank91_same_level_sweep_count_15m/setup_summary.csv">setup_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank91_same_level_sweep_count_15m/time_bucket_summary.csv">time_bucket_summary.csv</a></li>
        <li><a href="../../artifacts/scout_rank91_same_level_sweep_count_15m/trades_primary_6bps.csv">trades_primary_6bps.csv</a></li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 91 same-level sweep clean replication", summary_body)

    reading_body = f"""
    <h1>Rank 91 / same-level consecutive sweep count clean replication</h1>
    <p class="muted">这是把 13:50 UTC 的 guard-passed intake 往前推一手：只回答这层 level-memory gate 在 desk 共用 setup 上，到底是 promotion 证据，还是只够留下 evidence_pool。</p>
    <div class="card">
      <p><strong>结论：</strong>{escape(verdict_cn)}</p>
      <p>primary 口径固定为 <code>{PRIMARY_VARIANT}</code> @ <code>{int(PRIMARY_COST)}bps/side</code>。当前结果：mean_total_return={pct(primary_row['mean_total_return'])}，positive_asset_ratio={pct(primary_row['positive_asset_ratio'])}，trade_count_retention={pct(primary_row['trade_count_retention'])}，hold4={pct(primary_row['mean_hold4'])}，early_fail_4bars={pct(primary_row['mean_early_fail_4bars'])}。</p>
      <p>对照 baseline：mean_total_return={pct(baseline_row['mean_total_return'])}，positive_asset_ratio={pct(baseline_row['positive_asset_ratio'])}，trade_count_retention={pct(baseline_row['trade_count_retention'])}。</p>
      <p><a href="../../factors/scout_rank91_same_level_sweep_count_15m/report.html">查看完整报告页</a></p>
    </div>
    """
    write_html(READING_PATH, "Rank 91 same-level sweep clean replication", reading_body)

    print(f"hard_verdict={verdict}")
    print(f"primary_mean_total_return={primary_row['mean_total_return']:.6f}")
    print(f"primary_positive_asset_ratio={primary_row['positive_asset_ratio']:.6f}")
    print(f"primary_trade_count_retention={primary_row['trade_count_retention']:.6f}")
    print(f"primary_mean_hold4={primary_row['mean_hold4']:.6f}")
    print(f"primary_mean_early_fail_4bars={primary_row['mean_early_fail_4bars']:.6f}")


if __name__ == "__main__":
    main()
