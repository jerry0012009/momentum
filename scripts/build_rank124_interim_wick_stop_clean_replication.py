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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank124_interim_wick_stop_anchor_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank124_interim_wick_stop_anchor_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank124_interim_wick_stop_anchor_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["fib_retest_long", "ema_psar_long", "breakout_short"]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
ATR_PERIOD = 14
ATR_MULT = 1.5
WICK_BUFFER_ATR = 0.25
WICK_BUFFER_PCT = 0.002
OPPOSITE_LOOKBACK = 6
EPS = 1e-12

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
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


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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
    close = df["close"].to_numpy(dtype=float)
    out = np.full(len(df), np.nan)
    if len(df) < 2:
        return pd.Series(out, index=df.index)
    bull = close[1] >= close[0]
    af = step
    ep = high[0] if bull else low[0]
    sar = low[0] if bull else high[0]
    out[0] = sar
    for i in range(1, len(df)):
        sar = sar + af * (ep - sar)
        if bull:
            sar = min(sar, low[i - 1], low[i - 2] if i > 1 else low[i - 1])
            if low[i] < sar:
                bull = False
                sar = ep
                ep = low[i]
                af = step
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + step, max_step)
        else:
            sar = max(sar, high[i - 1], high[i - 2] if i > 1 else high[i - 1])
            if high[i] > sar:
                bull = True
                sar = ep
                ep = high[i]
                af = step
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + step, max_step)
        out[i] = sar
    return pd.Series(out, index=df.index)


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["body_dir"] = np.sign(df["close"] - df["open"]).astype(int)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["psar"] = compute_psar(df)
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["prior20_high"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["prior20_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["prior20_low"].notna()
        & df["atr14"].notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < 0)
        & (df["close"] < df["prior20_low"])
        & (df["close"].shift(1) >= df["prior20_low"].shift(1))
        & (df["psar"] > df["close"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def find_recent_opposite_wick(frame: pd.DataFrame, idx: int, direction: str, lookback: int = OPPOSITE_LOOKBACK) -> tuple[float, int]:
    start = max(0, idx - lookback)
    window = frame.iloc[start:idx]
    if direction == "long":
        opp = window[window["close"] < window["open"]]
        if opp.empty:
            row = frame.iloc[idx]
            return float(row["low"]), int(idx)
        last = opp.iloc[-1]
        return float(last["low"]), int(last.name)
    opp = window[window["close"] > window["open"]]
    if opp.empty:
        row = frame.iloc[idx]
        return float(row["high"]), int(idx)
    last = opp.iloc[-1]
    return float(last["high"]), int(last.name)


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        col = f"{setup}_signal"
        for idx in np.flatnonzero(frame[col].to_numpy()):
            if idx + 2 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
                continue
            direction = "short" if setup == "breakout_short" else "long"
            wick_extreme, wick_idx = find_recent_opposite_wick(frame, int(idx), direction)
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "direction": direction,
                    "signal_idx": int(idx),
                    "signal_time": row["timestamp"],
                    "signal_close": float(row["close"]),
                    "atr14": float(row["atr14"]),
                    "wick_extreme": float(wick_extreme),
                    "wick_idx": int(wick_idx),
                }
            )
    return pd.DataFrame(rows).sort_values(["setup", "asset", "signal_time"]).reset_index(drop=True)


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_setup = {setup: -1 for setup in SETUPS}
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_by_setup[setup]:
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        atr = float(sig["atr14"])
        direction = str(sig["direction"])
        wick_extreme = float(sig["wick_extreme"])
        if variant == "atr_only":
            stop_px = entry_px - ATR_MULT * atr if direction == "long" else entry_px + ATR_MULT * atr
        elif variant == "wick_atr":
            stop_px = wick_extreme - WICK_BUFFER_ATR * atr if direction == "long" else wick_extreme + WICK_BUFFER_ATR * atr
        elif variant == "wick_pct":
            stop_px = wick_extreme * (1 - WICK_BUFFER_PCT) if direction == "long" else wick_extreme * (1 + WICK_BUFFER_PCT)
        else:
            raise ValueError(variant)
        stop_distance_pct = abs(entry_px - stop_px) / max(entry_px, EPS)

        planned_exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS)
        actual_exit_idx = planned_exit_idx
        exit_reason = "time_stop"
        exit_price = float(frame.iloc[planned_exit_idx]["close"])
        stop_hit_4bars = 0
        stop_hit_8bars = 0
        for j in range(entry_idx, planned_exit_idx + 1):
            bar = frame.iloc[j]
            if direction == "long":
                hit = float(bar["low"]) <= stop_px
            else:
                hit = float(bar["high"]) >= stop_px
            if hit:
                actual_exit_idx = j
                exit_reason = "stop_hit"
                exit_price = stop_px
                stop_hit_8bars = 1
                if j <= min(planned_exit_idx, entry_idx + 3):
                    stop_hit_4bars = 1
                break
        if exit_reason == "time_stop":
            early = frame.iloc[entry_idx:min(len(frame), entry_idx + 4)]
            if direction == "long":
                stop_hit_4bars = int((early["low"] <= stop_px).any()) if len(early) else 0
            else:
                stop_hit_4bars = int((early["high"] >= stop_px).any()) if len(early) else 0
        if direction == "long":
            gross = exit_price / entry_px - 1.0
            mfe_window = frame.iloc[entry_idx:planned_exit_idx + 1]
            mfe = float(mfe_window["high"].max() / entry_px - 1.0)
            mae = float(mfe_window["low"].min() / entry_px - 1.0)
        else:
            gross = entry_px / exit_price - 1.0
            mfe_window = frame.iloc[entry_idx:planned_exit_idx + 1]
            mfe = float(entry_px / mfe_window["low"].min() - 1.0)
            mae = float(entry_px / mfe_window["high"].max() - 1.0)
        rows.append(
            {
                **sig.to_dict(),
                "variant": variant,
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "entry_price": entry_px,
                "exit_idx": actual_exit_idx,
                "exit_time": frame.iloc[actual_exit_idx]["timestamp"],
                "exit_price": float(exit_price),
                "exit_reason": exit_reason,
                "gross_return": gross,
                "hold_bars_realized": actual_exit_idx - entry_idx + (1 if exit_reason == "time_stop" else 0),
                "stop_price": stop_px,
                "stop_distance_pct": stop_distance_pct,
                "stop_hit_4bars": stop_hit_4bars,
                "stop_hit_8bars": stop_hit_8bars,
                "mfe": mfe,
                "mae": mae,
            }
        )
        last_exit_by_setup[setup] = actual_exit_idx
    return pd.DataFrame(rows)


def summarize_variant(trades: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    work = trades.copy()
    work["net_return"] = net_ret(work["gross_return"], cost_bps)
    rows = []
    for (setup, asset, variant), grp in work.groupby(["setup", "asset", "variant"], sort=True):
        total_return = float((1.0 + grp["net_return"]).prod() - 1.0) if len(grp) else np.nan
        rows.append(
            {
                "setup": setup,
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "trades": int(len(grp)),
                "mean_total_return": total_return,
                "avg_trade_return": float(grp["net_return"].mean()) if len(grp) else np.nan,
                "stop_hit_4bars": float(grp["stop_hit_4bars"].mean()) if len(grp) else np.nan,
                "stop_hit_8bars": float(grp["stop_hit_8bars"].mean()) if len(grp) else np.nan,
                "avg_stop_distance_pct": float(grp["stop_distance_pct"].mean()) if len(grp) else np.nan,
                "median_stop_distance_pct": float(grp["stop_distance_pct"].median()) if len(grp) else np.nan,
                "avg_hold_bars": float(grp["hold_bars_realized"].mean()) if len(grp) else np.nan,
                "avg_mfe": float(grp["mfe"].mean()) if len(grp) else np.nan,
                "avg_mae": float(grp["mae"].mean()) if len(grp) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def aggregate_setup(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "mean_avg_trade_return": float(grp["avg_trade_return"].mean()),
                "mean_stop_hit_4bars": float(grp["stop_hit_4bars"].mean()),
                "mean_stop_hit_8bars": float(grp["stop_hit_8bars"].mean()),
                "mean_avg_stop_distance_pct": float(grp["avg_stop_distance_pct"].mean()),
                "mean_trades": float(grp["trades"].mean()),
                "positive_asset_ratio": float((grp["mean_total_return"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def aggregate_overall(setup_summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost_bps), grp in setup_summary.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["mean_total_return"].mean()),
                "mean_avg_trade_return": float(grp["mean_avg_trade_return"].mean()),
                "mean_stop_hit_4bars": float(grp["mean_stop_hit_4bars"].mean()),
                "mean_stop_hit_8bars": float(grp["mean_stop_hit_8bars"].mean()),
                "mean_avg_stop_distance_pct": float(grp["mean_avg_stop_distance_pct"].mean()),
                "mean_trades": float(grp["mean_trades"].mean()),
                "positive_setup_ratio": float((grp["mean_total_return"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def verdict_from(primary_setup: pd.DataFrame, primary_overall: pd.DataFrame) -> tuple[str, str]:
    atr_row = primary_overall[primary_overall["variant"] == "atr_only"].iloc[0]
    wick_row = primary_overall[primary_overall["variant"] == "wick_atr"].iloc[0]
    pct_row = primary_overall[primary_overall["variant"] == "wick_pct"].iloc[0]

    uplift = float(wick_row["mean_total_return"] - atr_row["mean_total_return"])
    stop_improve = float(atr_row["mean_stop_hit_8bars"] - wick_row["mean_stop_hit_8bars"])
    dist_delta = float(wick_row["mean_avg_stop_distance_pct"] - atr_row["mean_avg_stop_distance_pct"])
    positive = float(wick_row["positive_setup_ratio"])
    pct_not_better = float(pct_row["mean_total_return"] <= wick_row["mean_total_return"])

    if uplift > 0.004 and stop_improve > 0.08 and dist_delta < 0.005 and positive >= 0.67 and pct_not_better >= 1.0:
        return (
            "promote_P2 / paper candidate",
            "wick+ATR 在测试段同时做到了更低的早停率和更好的成本后结果，而且额外 stop 距离没有明显失控；当前更像值得继续推进的 shared initial risk anchor。",
        )
    if uplift > -0.002 and stop_improve > 0.05 and dist_delta < 0.007:
        return (
            "keep_P1 / honest risk overlay",
            "wick+ATR 至少像一条有料的初始风险锚：更少被近端噪声打掉，但 uplift 还没硬到足够直接升 P2；先保留为 P1 更诚实。",
        )
    return (
        "park / evidence pool",
        "这轮 clean replication 没把结构锚 stop 证明成更诚实的 desk 级升级：改善若存在，也更像来自 stop 更宽，而不是更好的成本后期望。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals = pd.concat([collect_signals(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    signals.to_csv(ART_DIR / "signal_catalog.csv", index=False)

    trade_logs = []
    for asset, frame in frames.items():
        asset_signals = signals[signals["asset"] == asset]
        for variant in ["atr_only", "wick_atr", "wick_pct"]:
            trade_logs.append(simulate_variant(frame, asset_signals, variant))
    trade_log = pd.concat(trade_logs, ignore_index=True)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_parts = []
    for cost in COSTS:
        asset_parts.append(summarize_variant(trade_log, cost))
    asset_summary = pd.concat(asset_parts, ignore_index=True)
    setup_summary = aggregate_setup(asset_summary)
    overall_summary = aggregate_overall(setup_summary)

    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)

    stop_distance_summary = (
        trade_log.groupby(["setup", "variant"], as_index=False)
        .agg(
            mean_stop_distance_pct=("stop_distance_pct", "mean"),
            median_stop_distance_pct=("stop_distance_pct", "median"),
            p90_stop_distance_pct=("stop_distance_pct", lambda s: float(np.nanpercentile(s, 90))),
            max_stop_distance_pct=("stop_distance_pct", "max"),
        )
    )
    stop_distance_summary.to_csv(ART_DIR / "stop_distance_summary.csv", index=False)

    primary_setup = setup_summary[setup_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    primary_overall = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy().reset_index(drop=True)
    verdict, verdict_summary = verdict_from(primary_setup, primary_overall)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    summary = {
        "generated_at_utc": generated_at,
        "rank": 124,
        "candidate": "interim wick + ATR stop anchor",
        "base_setups": SETUPS,
        "sample": "BTC/ETH/SOL 120d 15m local cache",
        "execution": "signal当根及之前数据 + next-bar open + no-overlap + hold 8 bars",
        "frozen_params": {
            "atr_mult": ATR_MULT,
            "wick_buffer_atr": WICK_BUFFER_ATR,
            "wick_buffer_pct": WICK_BUFFER_PCT,
            "opposite_wick_lookback": OPPOSITE_LOOKBACK,
        },
        "verdict": verdict,
        "summary": verdict_summary,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    body = f"""
    <h1>Rank 124 / interim wick + ATR stop anchor · 最小 clean replication</h1>
    <p class='muted'>生成时间：{escape(generated_at)}</p>

    <div class='card'>
      <h2>本轮 hard verdict</h2>
      <p><strong>{escape(verdict)}</strong></p>
      <p>{escape(verdict_summary)}</p>
      <ul>
        <li>base setup：<code>fib_retest_long</code> + <code>ema_psar_long</code> + <code>breakout_short</code></li>
        <li>样本：<code>BTC/ETH/SOL 120d 15m</code></li>
        <li>执行：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></li>
        <li>只比较三种初始风险锚：<code>ATR-only</code>、<code>wick+ATR</code>、<code>wick+pct</code></li>
        <li>固定参数：<code>ATR x {ATR_MULT}</code> / <code>wick ± {WICK_BUFFER_ATR} ATR</code> / <code>wick ± {WICK_BUFFER_PCT*100:.1f}% </code> / 反向 K lookback <code>{OPPOSITE_LOOKBACK}</code></li>
      </ul>
    </div>

    <div class='card'>
      <h2>desk 级测试段摘要</h2>
      {render_table(primary_overall, percent_cols={'mean_total_return','mean_avg_trade_return','mean_stop_hit_4bars','mean_stop_hit_8bars','mean_avg_stop_distance_pct','positive_setup_ratio'}, digits_cols={'cost_bps_per_side':1,'mean_trades':2})}
    </div>

    <div class='card'>
      <h2>按 setup 的测试段摘要（6 bps/side）</h2>
      {render_table(primary_setup[['setup','variant','mean_total_return','mean_avg_trade_return','mean_stop_hit_4bars','mean_stop_hit_8bars','mean_avg_stop_distance_pct','mean_trades','positive_asset_ratio']], percent_cols={'mean_total_return','mean_avg_trade_return','mean_stop_hit_4bars','mean_stop_hit_8bars','mean_avg_stop_distance_pct','positive_asset_ratio'}, digits_cols={'mean_trades':2})}
    </div>

    <div class='card'>
      <h2>分资产摘要（6 bps/side）</h2>
      {render_table(asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST][['setup','asset','variant','trades','mean_total_return','avg_trade_return','stop_hit_4bars','stop_hit_8bars','avg_stop_distance_pct']], percent_cols={'mean_total_return','avg_trade_return','stop_hit_4bars','stop_hit_8bars','avg_stop_distance_pct'}, digits_cols={'trades':0})}
    </div>

    <div class='card'>
      <h2>stop distance 分布</h2>
      {render_table(stop_distance_summary, percent_cols={'mean_stop_distance_pct','median_stop_distance_pct','p90_stop_distance_pct','max_stop_distance_pct'})}
    </div>

    <div class='card'>
      <h2>诚实边界</h2>
      <ul>
        <li>它只测 <strong>entry 后立即生效的初始 stop 锚</strong>；不改 entry，不单独开仓。</li>
        <li>最近反向 K 线只允许从 <code>signal 当根及之前</code> 的已完成 bar 里找。</li>
        <li>如果 wick 锚的改善主要来自 stop 更宽、而不是更好的成本后期望与更低的近端噪声 stopout，就应该 park。</li>
        <li><code>wick+pct</code> 只是对照组，不是默认更优解。</li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", "Rank 124 interim wick stop clean replication", body)

    reading_body = f"""
    <h1>Rank 124 / interim wick + ATR stop anchor · clean replication note</h1>
    <div class='card'>
      <p><strong>一句话：</strong>{escape(verdict_summary)}</p>
      <p>这轮把初始风险锚直接挂到三条最小 clean-room 上，只问一件事：<code>wicK+ATR</code> 是否比 <code>entry ± 1.5 ATR</code> 更诚实，而不是更宽。</p>
      <p><a href='../../factors/scout_rank124_interim_wick_stop_anchor_15m/report.html'>打开完整 report</a></p>
    </div>
    <div class='card'>
      <h2>6 bps/side 总结</h2>
      {render_table(primary_overall[['variant','mean_total_return','mean_stop_hit_8bars','mean_avg_stop_distance_pct','mean_trades','positive_setup_ratio']], percent_cols={'mean_total_return','mean_stop_hit_8bars','mean_avg_stop_distance_pct','positive_setup_ratio'}, digits_cols={'mean_trades':2})}
    </div>
    """
    write_html(READING_PATH, "Rank 124 interim wick stop clean replication", reading_body)

    print(json.dumps({
        "generated_at_utc": generated_at,
        "verdict": verdict,
        "site_report": str(SITE_DIR / 'report.html'),
        "reading_report": str(READING_PATH),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
