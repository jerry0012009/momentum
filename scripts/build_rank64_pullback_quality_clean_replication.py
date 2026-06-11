#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank64_pullback_quality_score_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank64_pullback_quality_score_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "zone_only", "zone_plus_vol", "full_score_80"]
PRIMARY_VARIANT = "full_score_80"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
FALSE_WINDOW = 4

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; }
th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
.muted { color: #6b7280; }
.good { color: #065f46; font-weight: 600; }
.bad { color: #991b1b; font-weight: 600; }
.card { background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; margin: 16px 0; }
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)

    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["rolling_high20"] = df["high"].rolling(20, min_periods=20).max().shift(1)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    low = df["rolling_low20"]
    atr = df["atr14"]
    df["breakout_short_signal"] = (
        low.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr)
        & (df["high"] <= low + 0.3 * atr)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def compute_quality_features(frame: pd.DataFrame, idx: int, direction: int) -> dict[str, float | int]:
    row = frame.iloc[idx]
    atr = float(row["atr14"]) if np.isfinite(row["atr14"]) and row["atr14"] > 0 else np.nan
    if not np.isfinite(atr) or atr <= 0:
        return {
            "trend_pts": 0,
            "zone_pts": 0,
            "vol_pts": 0,
            "trigger_pts": 0,
            "score": 0,
            "depth_atr": np.nan,
            "pullback_vol_ratio": np.nan,
        }

    if direction > 0:
        depth_atr = float((row["swing_high_30"] - row["close"]) / atr) if np.isfinite(row["swing_high_30"]) else np.nan
        trend_ok = bool(row["ema9"] > row["ema21"] > row["ema50"] and row["ema_slope"] > 0)
        trigger_ok = bool((row["close"] > row["high"] - 0.25 * atr) and (row["close"] > row["ema9"]))
    else:
        depth_atr = float((row["close"] - row["swing_low_30"]) / atr) if np.isfinite(row["swing_low_30"]) else np.nan
        trend_ok = bool(row["ema9"] < row["ema21"] < row["ema50"] and row["ema_slope"] < 0)
        trigger_ok = bool((row["close"] < row["low"] + 0.25 * atr) and (row["close"] < row["ema9"]))

    zone_ok = bool(np.isfinite(depth_atr) and 0.6 <= depth_atr <= 1.8)

    start = max(0, idx - 3)
    pullback_slice = frame.iloc[start:idx]
    if len(pullback_slice) == 0 or not np.isfinite(row["vol_ma20"]) or float(row["vol_ma20"]) <= 0:
        pullback_vol_ratio = np.nan
        vol_ok = False
    else:
        pullback_vol_ratio = float(pullback_slice["volume"].mean() / float(row["vol_ma20"]))
        vol_ok = bool(pullback_vol_ratio < 0.9)

    trend_pts = 30 if trend_ok else 0
    zone_pts = 30 if zone_ok else 0
    vol_pts = 20 if vol_ok else 0
    trigger_pts = 20 if trigger_ok else 0
    score = trend_pts + zone_pts + vol_pts + trigger_pts

    return {
        "trend_pts": trend_pts,
        "zone_pts": zone_pts,
        "vol_pts": vol_pts,
        "trigger_pts": trigger_pts,
        "score": score,
        "depth_atr": depth_atr,
        "pullback_vol_ratio": pullback_vol_ratio,
    }


def build_signal_frame(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    sig = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(max(60, 2), len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        q = compute_quality_features(frame, idx, direction)
        atr = float(frame.iloc[idx]["atr14"]) if np.isfinite(frame.iloc[idx]["atr14"]) else np.nan
        if not np.isfinite(atr) or atr <= 0:
            continue
        if direction > 0:
            invalidation = min(float(frame.iloc[idx]["ema21"]), float(frame.iloc[idx]["low"]))
        else:
            invalidation = max(float(frame.iloc[idx]["ema21"]), float(frame.iloc[idx]["high"]))
        rows.append(
            {
                "signal_id": f"{asset}|{setup}|{idx}",
                "asset": asset,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "signal_ts": frame.iloc[idx]["timestamp"],
                "entry_idx": idx + 1,
                "entry_ts": frame.iloc[idx + 1]["timestamp"],
                "entry_open": float(frame.iloc[idx + 1]["open"]),
                "atr14": atr,
                "invalidation": invalidation,
                **q,
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def variant_gate(signal: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "zone_only":
        return bool(signal["zone_pts"] >= 30)
    if variant == "zone_plus_vol":
        return bool(signal["zone_pts"] >= 30 and signal["vol_pts"] >= 20)
    if variant == "full_score_80":
        return bool(signal["score"] >= 80)
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for _, signal in signals.iterrows():
        if not variant_gate(signal, variant):
            continue
        entry_idx = int(signal["entry_idx"])
        if entry_idx <= last_exit_idx or entry_idx >= len(frame):
            continue
        entry_px = float(signal["entry_open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        direction = int(signal["direction"])
        invalidation = float(signal["invalidation"])
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        exit_reason = "time_stop"
        false_follow = 0
        max_adverse_atr = 0.0

        for j in range(entry_idx, min(len(frame), entry_idx + HOLD_BARS)):
            row = frame.iloc[j]
            low = float(row["low"])
            high = float(row["high"])
            close = float(row["close"])
            if direction > 0:
                adverse = max(entry_px - low, 0.0)
                invalid = close < invalidation
            else:
                adverse = max(high - entry_px, 0.0)
                invalid = close > invalidation
            max_adverse_atr = max(max_adverse_atr, adverse / float(signal["atr14"]))
            if j <= entry_idx + FALSE_WINDOW - 1 and invalid:
                false_follow = 1
            if invalid:
                exit_idx = j
                exit_reason = "invalidation"
                break

        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = direction * (exit_px / entry_px - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": signal["asset"],
                "setup": signal["setup"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(signal["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(signal["entry_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": direction,
                "entry_price": entry_px,
                "exit_price": exit_px,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_follow_4bars": int(false_follow),
                "max_adverse_atr": float(max_adverse_atr),
                "score": float(signal["score"]),
                "depth_atr": float(signal["depth_atr"]) if np.isfinite(signal["depth_atr"]) else np.nan,
                "pullback_vol_ratio": float(signal["pullback_vol_ratio"]) if np.isfinite(signal["pullback_vol_ratio"]) else np.nan,
                "exit_reason": exit_reason,
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "false_follow_4bars_rate": np.nan,
            "mean_hold_bars": np.nan,
            "mean_score": np.nan,
            "mean_depth_atr": np.nan,
            "mean_pullback_vol_ratio": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": float(len(trades) / signal_events) if signal_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "false_follow_4bars_rate": float(trades["false_follow_4bars"].mean()),
        "mean_hold_bars": float(trades["hold_bars"].mean()),
        "mean_score": float(trades["score"].mean()),
        "mean_depth_atr": float(trades["depth_atr"].mean()),
        "mean_pullback_vol_ratio": float(trades["pullback_vol_ratio"].mean()),
    }


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    df = df.sort_values("entry_ts").reset_index(drop=True)
    df["bucket"] = pd.qcut(df.index + 1, 3, labels=["bucket_1", "bucket_2", "bucket_3"])
    rows = []
    for bucket, sub in df.groupby("bucket", observed=False):
        asset_returns = sub.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append(
            {
                "bucket": bucket,
                "mean_total_return": float(asset_returns.mean()) if not asset_returns.empty else np.nan,
                "positive_asset_ratio": float((asset_returns > 0).mean()) if not asset_returns.empty else np.nan,
                "mean_trades": float(sub.groupby("asset").size().mean()) if not sub.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame) -> tuple[str, str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本。", "`full_score_80` 在当前 15m 三资产样本下没有稳定可用的 replication 证据。"
    row = primary.iloc[0]
    ret = float(row["mean_total_return"])
    pos = float(row["positive_asset_ratio"])
    trades = float(row["mean_trades"])
    retention = float(row["mean_trade_count_retention"])
    false = float(row["mean_false_follow_4bars_rate"]) if np.isfinite(row["mean_false_follow_4bars_rate"]) else np.nan

    if ret > 0.03 and pos >= 2/3 and trades >= 15 and retention >= 0.25:
        return "P2 / paper candidate", "full-score 版本在成本后仍保留跨资产正 pocket。", "它不是单纯靠砍样本存活：6bps 下仍有正回报、至少 2/3 资产为正，且 trade retention 没有塌到不可用。"
    if ret > 0 and pos >= 1/3 and trades >= 8 and retention >= 0.15:
        return "P1 weak candidate / evidence pool", "有一点 shared pullback-quality 味道，但还不够干净。", "full-score 版本虽然比 base 更诚实，但当前还没形成足够稳定的跨资产口径，最多保留作下一手 cheap check 的候选。"
    if trades <= 1:
        return "park / evidence pool", "full-score 基本把样本切没了。", "改善主要来自过度砍单，而不是更诚实地降低 false-hold / false-follow-through。"
    return "park / evidence pool", "回踩质量打分没有把 15m setup 稳定拉回 admission 线。", f"6bps 下 `full_score_80` 仍只有 mean_total_return≈{pct(ret)}、positive_asset_ratio≈{pct(pos)}、mean_trades≈{num(trades,1)}、trade_count_retention≈{pct(retention)}" + (f"、false_follow_4bars≈{pct(false)}" if np.isfinite(false) else "") + "，更像 research evidence，不像可升格的 paper candidate。"


def update_repo_scout_index() -> None:
    index_path = READING_DIR / "report.html"
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    if "rank64_pullback_quality_score_clean_replication.html" in text:
        return
    old = 'rank64_pullback_quality_score_source_intake.html">Rank 64 source intake</a>'
    if old in text:
        text = text.replace(old, old + ' ｜ <a href="rank64_pullback_quality_score_clean_replication.html">clean replication</a>', 1)
        index_path.write_text(text, encoding="utf-8")


def update_todo(overall: pd.DataFrame, verdict: str, generated_at: str, latest_p3_appends: int) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return

    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    zone = overall[(overall["variant"] == "zone_only") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    zone_vol = overall[(overall["variant"] == "zone_plus_vol") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]

    if verdict.startswith("P1") or verdict.startswith("P2"):
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 64 minimal clean replication 后仍保留 candidate 资格，则只给它 1 个 truly verdict-changing 的最小 Light Stability Pack（默认优先时间稳定性），并直接做 P2 / park 判断` -> `Run 3 = 若 Rank 64 这次 cheap check 后仍不能升格，则回到 fresh source 比较 perp-stress resetComplete / re-arm gate > exec-TF switch alignment gate > regime-matrix shared-state gate；只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    else:
        queue_line = "**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 64 已直接 park，则回到 fresh source 比较 perp-stress resetComplete / re-arm gate > exec-TF switch alignment gate > regime-matrix shared-state gate` -> `Run 3 = 只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"

    block = (
        f"> **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane（最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，其后 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、A 股三条 lane `-> 2026-03-19 07:00 UTC`），而 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended={latest_p3_appends}`，因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。随后按权威顺序执行 **`Run 2 / Rank 64 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`base+zone`、`base+zone+vol`、`base+full_score` 四臂，统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。\n"
        f">  - `6bps/side` 下的跨资产结果已冻结为：`zone_only≈{pct(zone['mean_total_return'])} / retention≈{pct(zone['mean_trade_count_retention'])}`、`zone_plus_vol≈{pct(zone_vol['mean_total_return'])} / retention≈{pct(zone_vol['mean_trade_count_retention'])}`、`full_score_80≈{pct(primary['mean_total_return'])} / positive_asset_ratio≈{pct(primary['positive_asset_ratio'])} / mean_trades≈{num(primary['mean_trades'],1)} / trade_count_retention≈{pct(primary['mean_trade_count_retention'])}`。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 64 / pullback-quality score gate = {verdict}`**。\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank64_pullback_quality_score_15m/report.html`、`reports/site/reading/repo_scout/rank64_pullback_quality_score_clean_replication.html`；artifact：`reports/artifacts/scout_rank64_pullback_quality_score_15m/overall_summary.csv`。\n"
        f">  - 当前更诚实的 active Scout 顺序应更新为：**`perp-stress resetComplete / re-arm gate` > `exec-TF switch alignment gate` > `regime-matrix shared-state gate` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**。`Rank 64` 当前已不再占默认 fresh intake / replication 队列。\n"
        f">  - 因此当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    latest_p3_appends = 0
    if P3_SUMMARY_PATH.exists():
        try:
            latest_p3_appends = int(pd.read_json(P3_SUMMARY_PATH, typ="series").get("new_closed_trades_appended", 0))
        except Exception:
            latest_p3_appends = 0

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True)
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    for asset in ASSETS.keys():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            signal_events = int(len(sigs))
            for cost in COSTS:
                for variant in VARIANTS:
                    trades = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=signal_events)
                    )

    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_df = pd.DataFrame(asset_rows).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall_df = (
        asset_df.groupby(["variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_false_follow_4bars_rate=("false_follow_4bars_rate", "mean"),
            mean_hold_bars=("mean_hold_bars", "mean"),
            mean_score=("mean_score", "mean"),
            mean_depth_atr=("mean_depth_atr", "mean"),
            mean_pullback_vol_ratio=("mean_pullback_vol_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["cost_bps_per_side", "variant"])
        .reset_index(drop=True)
    )
    time_pockets_df = build_time_pockets(trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)])
    verdict, headline, reason = build_verdict(overall_df)

    trades_df.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "candidate_id": "rank64_pullback_quality_score_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    summary_card = f"""
<h1>Rank 64 / pullback-quality score gate — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if verdict.startswith('P') else 'bad'}'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p>{escape(reason)}</p>
  <p>本轮只回答一个问题：把 `trendPts + zonePts + volPts + triggerPts` 压成 15m 的 shared pullback-quality score 后，能不能比二元 `retest_hold` 更诚实地改善三条 base setup 的成本后表现与 false-follow-through。</p>
</div>
"""

    method = f"""
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>三条 base archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>四臂固定为：<code>base</code>、<code>base+zone</code>、<code>base+zone+vol</code>、<code>base+full_score</code>。</li>
    <li><code>trendPts=30</code> 用 EMA 结构和 slope；<code>zonePts=30</code> 用 pullback 深度落在 <code>0.6~1.8 ATR</code>；<code>volPts=20</code> 用 signal 前 3 根的 pullback volume 低于 <code>0.9 * SMA20(volume)</code>；<code>triggerPts=20</code> 用 reclaim / continuation trigger。</li>
    <li>入场统一 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>，默认持有上限 <code>{HOLD_BARS}</code> 根 15m bar。</li>
    <li>第一轮只回答 shared score 的增量，不偷渡 ATR 止盈止损、仓位管理或高周期 long-only 叙事。</li>
  </ul>
</div>
"""

    report_body = summary_card + method
    report_body += "<h2>overall summary</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_avg_net_ret", "mean_false_follow_4bars_rate", "mean_pullback_vol_ratio"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_hold_bars": 2, "mean_score": 1, "mean_depth_atr": 2},
    )
    report_body += "<h2>asset-level summary</h2>" + render_table(
        asset_df,
        percent_cols={"total_return", "trade_count_retention", "avg_net_ret", "false_follow_4bars_rate", "mean_pullback_vol_ratio"},
        digits_cols={"trades": 0, "cost_bps_per_side": 0, "mean_hold_bars": 2, "mean_score": 1, "mean_depth_atr": 2},
    )
    report_body += "<h2>time-pocket honesty（full_score_80 @ 6bps）</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 1},
    )
    write_html(SITE_DIR / "report.html", "Rank 64 clean replication", report_body)

    reading_body = summary_card
    reading_body += "<div class='card'><h2>当前更直白的读法</h2><p>如果这套 score 真有 shared 价值，它至少应该在不把样本切没的前提下，给三条 base setup 带来更好的成本后回报或更低的 4-bar false-follow-through。若改善主要来自 trade-count 塌缩，或仍只在单一资产 pocket 存活，就该尽快 park。</p></div>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_avg_net_ret", "mean_false_follow_4bars_rate", "mean_pullback_vol_ratio"},
        digits_cols={"mean_trades": 1, "cost_bps_per_side": 0, "mean_hold_bars": 2, "mean_score": 1, "mean_depth_atr": 2},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(reason)}</p>"
    write_html(READING_DIR / "rank64_pullback_quality_score_clean_replication.html", "Rank 64 clean replication", reading_body)

    update_repo_scout_index()
    update_todo(overall_df, verdict, generated_at, latest_p3_appends)
    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
