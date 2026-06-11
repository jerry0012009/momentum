#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank43_atr_retest_bounce_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank43_atr_retest_bounce_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "quant_digests"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_COST = 6.0
PRIMARY_LABEL = "atr_zone0.5_timeout20"
PRIMARY_ZONE_ATR = 0.5
PRIMARY_TIMEOUT = 20
PRIMARY_HOLD_BARS = 8
PRIMARY_FALSE_BREAK_BARS = 4
SWING_LOOKBACK = 5
ATR_PERIOD = 14
HTF_FAST = 20
HTF_SLOW = 50
PARAM_GRID = [
    ("atr_zone0.4_timeout16", 0.4, 16),
    ("atr_zone0.5_timeout16", 0.5, 16),
    ("atr_zone0.5_timeout20", 0.5, 20),
    ("atr_zone0.6_timeout20", 0.6, 20),
]
BASELINE_LABEL = "confirmed_breakout_only"


@dataclass(frozen=True)
class CandidateConfig:
    label: str
    zone_atr: float
    timeout_bars: int
    hold_bars: int = PRIMARY_HOLD_BARS
    false_break_bars: int = PRIMARY_FALSE_BREAK_BARS
    invalidation_atr: float = 1.0
    breakout_body_min: float = 0.5
    bounce_body_min: float = 0.4


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


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def confirmed_pivots(arr: np.ndarray, lookback: int, kind: str) -> tuple[np.ndarray, np.ndarray]:
    n = len(arr)
    prices = np.full(n, np.nan, dtype=float)
    origins = np.full(n, -1, dtype=int)
    for center in range(lookback, n - lookback):
        v = float(arr[center])
        left = arr[center - lookback:center]
        right = arr[center + 1:center + lookback + 1]
        if kind == "high":
            ok = bool(np.all(v > left) and np.all(v > right))
        else:
            ok = bool(np.all(v < left) and np.all(v < right))
        if ok:
            confirm_idx = center + lookback
            prices[confirm_idx] = v
            origins[confirm_idx] = center
    return prices, origins


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    prev_close = df["close"].shift(1)
    tr = np.nanmax(
        np.column_stack([
            (df["high"] - df["low"]).abs().to_numpy(dtype=float),
            (df["high"] - prev_close).abs().to_numpy(dtype=float),
            (df["low"] - prev_close).abs().to_numpy(dtype=float),
        ]),
        axis=1,
    )
    df["atr"] = pd.Series(tr, index=df.index).rolling(ATR_PERIOD, min_periods=ATR_PERIOD).mean()

    htf = df[["timestamp", "close"]].rename(columns={"close": "close_src"}).set_index("timestamp").resample("1h").last().dropna().reset_index()
    htf["ema_fast_1h"] = htf["close_src"].ewm(span=HTF_FAST, adjust=False).mean()
    htf["ema_slow_1h"] = htf["close_src"].ewm(span=HTF_SLOW, adjust=False).mean()
    frame = pd.merge_asof(df.sort_values("timestamp"), htf.sort_values("timestamp"), on="timestamp", direction="backward")
    frame["htf_long"] = (frame["ema_fast_1h"] > frame["ema_slow_1h"]).fillna(False).astype(int)
    frame["htf_short"] = (frame["ema_fast_1h"] < frame["ema_slow_1h"]).fillna(False).astype(int)

    ph, ph_origin = confirmed_pivots(frame["high"].to_numpy(dtype=float), SWING_LOOKBACK, "high")
    pl, pl_origin = confirmed_pivots(frame["low"].to_numpy(dtype=float), SWING_LOOKBACK, "low")
    frame["confirmed_swing_high"] = ph
    frame["confirmed_swing_high_origin"] = ph_origin
    frame["confirmed_swing_low"] = pl
    frame["confirmed_swing_low_origin"] = pl_origin
    frame["active_swing_high"] = pd.Series(ph).ffill()
    frame["active_swing_low"] = pd.Series(pl).ffill()
    frame["active_swing_high_origin"] = pd.Series(ph_origin).replace(-1, np.nan).ffill().fillna(-1).astype(int)
    frame["active_swing_low_origin"] = pd.Series(pl_origin).replace(-1, np.nan).ffill().fillna(-1).astype(int)

    body = (frame["close"] - frame["open"]).abs()
    range_ = (frame["high"] - frame["low"]).replace(0, np.nan)
    frame["body_ratio"] = (body / range_).replace([np.inf, -np.inf], np.nan)
    frame["close_pos"] = ((frame["close"] - frame["low"]) / range_).replace([np.inf, -np.inf], np.nan)
    frame["green"] = (frame["close"] > frame["open"]).astype(int)
    frame["red"] = (frame["close"] < frame["open"]).astype(int)
    return frame


def breakout_candidate(frame: pd.DataFrame, idx: int, cfg: CandidateConfig) -> tuple[int, float, int] | None:
    row = frame.iloc[idx]
    prev = frame.iloc[idx - 1]
    if not math.isfinite(float(row["atr"])) or float(row["atr"]) <= 0:
        return None
    body_ratio = float(row["body_ratio"]) if pd.notna(row["body_ratio"]) else np.nan
    close_pos = float(row["close_pos"]) if pd.notna(row["close_pos"]) else np.nan

    level_h = float(row["active_swing_high"]) if pd.notna(row["active_swing_high"]) else np.nan
    if int(row["htf_long"]) == 1 and math.isfinite(level_h):
        if float(prev["close"]) <= level_h and float(row["close"]) > level_h and body_ratio >= cfg.breakout_body_min and close_pos >= 0.7:
            return 1, level_h, int(row["active_swing_high_origin"])

    level_l = float(row["active_swing_low"]) if pd.notna(row["active_swing_low"]) else np.nan
    if int(row["htf_short"]) == 1 and math.isfinite(level_l):
        if float(prev["close"]) >= level_l and float(row["close"]) < level_l and body_ratio >= cfg.breakout_body_min and close_pos <= 0.3:
            return -1, level_l, int(row["active_swing_low_origin"])
    return None


def bounce_ok(frame: pd.DataFrame, idx: int, direction: int, level: float, cfg: CandidateConfig) -> bool:
    row = frame.iloc[idx]
    body_ratio = float(row["body_ratio"]) if pd.notna(row["body_ratio"]) else np.nan
    close_pos = float(row["close_pos"]) if pd.notna(row["close_pos"]) else np.nan
    if direction > 0:
        return bool(float(row["close"]) > level and int(row["green"]) == 1 and body_ratio >= cfg.bounce_body_min and close_pos >= 0.55)
    return bool(float(row["close"]) < level and int(row["red"]) == 1 and body_ratio >= cfg.bounce_body_min and close_pos <= 0.45)


def false_break_flag(frame: pd.DataFrame, entry_idx: int, direction: int, level: float, atr0: float, max_bars: int) -> int:
    last = min(len(frame) - 1, entry_idx + max_bars)
    threshold = atr0 * 0.5
    for j in range(entry_idx, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < level - threshold:
            return 1
        if direction < 0 and close > level + threshold:
            return 1
    return 0


def simulate_variant(frame: pd.DataFrame, asset: str, cfg: CandidateConfig, *, baseline: bool = False) -> tuple[pd.DataFrame, dict[str, float | int]]:
    rows: list[dict[str, object]] = []
    no_overlap_until = -1
    candidates_seen = 0
    for idx in range(1, len(frame) - 1):
        if idx <= no_overlap_until:
            continue
        cand = breakout_candidate(frame, idx, cfg)
        if cand is None:
            continue
        candidates_seen += 1
        direction, level, pivot_origin = cand
        atr0 = float(frame.iloc[idx]["atr"])
        entry_idx = None
        retest_idx = None
        entry_reason = ""
        invalidated = False

        if baseline:
            entry_idx = idx + 1
            entry_reason = "breakout_only"
        else:
            last_wait = min(len(frame) - 2, idx + cfg.timeout_bars)
            for j in range(idx + 1, last_wait + 1):
                row = frame.iloc[j]
                if direction > 0 and float(row["close"]) < level - cfg.invalidation_atr * atr0:
                    invalidated = True
                    break
                if direction < 0 and float(row["close"]) > level + cfg.invalidation_atr * atr0:
                    invalidated = True
                    break
                in_zone = bool(float(row["low"]) <= level + cfg.zone_atr * atr0 and float(row["high"]) >= level - cfg.zone_atr * atr0)
                if in_zone:
                    retest_idx = j
                    if bounce_ok(frame, j, direction, level, cfg):
                        entry_idx = j + 1
                        entry_reason = "bounce_reclaim"
                        break
            if invalidated or entry_idx is None or entry_idx >= len(frame):
                continue

        exit_idx = min(len(frame) - 1, entry_idx + cfg.hold_bars - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        if not (math.isfinite(entry_px) and math.isfinite(exit_px) and entry_px > 0 and exit_px > 0):
            continue
        gross_ret = (exit_px / entry_px - 1.0) * direction
        rows.append({
            "asset": asset,
            "variant": cfg.label if not baseline else BASELINE_LABEL,
            "breakout_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "retest_ts": "" if retest_idx is None else pd.to_datetime(frame.iloc[retest_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "direction": "long" if direction > 0 else "short",
            "entry_reason": entry_reason,
            "level": level,
            "atr_at_breakout": atr0,
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_ret": gross_ret,
            "false_break_flag": false_break_flag(frame, entry_idx, direction, level, atr0, cfg.false_break_bars),
            "retest_wait_bars": np.nan if retest_idx is None else int(retest_idx - idx),
            "hold_bars": int(exit_idx - entry_idx + 1),
            "pivot_origin": int(pivot_origin),
            "pivot_age_bars": int(idx - pivot_origin) if pivot_origin >= 0 else np.nan,
        })
        no_overlap_until = exit_idx

    trades = pd.DataFrame(rows)
    meta = {
        "candidate_events": int(candidates_seen),
        "executed_trades": int(len(trades)),
    }
    return trades, meta


def apply_cost(trades: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    out = trades.copy()
    cost_rate = float(cost_bps) / 10000.0
    if out.empty:
        out["cost_bps_per_side"] = []
        out["net_ret"] = []
        return out
    out["cost_bps_per_side"] = float(cost_bps)
    out["net_ret"] = (1.0 + out["gross_ret"]) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    return out


def summarize_asset(trades: pd.DataFrame, *, asset: str, variant: str, cost_bps: float, candidate_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "candidate_events": int(candidate_events),
            "trades": 0,
            "candidate_to_trade_ratio": 0.0,
            "win_rate": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "false_break_rate": np.nan,
            "mean_retest_wait_bars": np.nan,
            "mean_pivot_age_bars": np.nan,
        }
    return {
        "asset": asset,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "candidate_events": int(candidate_events),
        "trades": int(len(trades)),
        "candidate_to_trade_ratio": float(len(trades) / candidate_events) if candidate_events > 0 else np.nan,
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "false_break_rate": float(trades["false_break_flag"].mean()),
        "mean_retest_wait_bars": float(trades["retest_wait_bars"].dropna().mean()) if trades["retest_wait_bars"].notna().any() else np.nan,
        "mean_pivot_age_bars": float(trades["pivot_age_bars"].dropna().mean()) if trades["pivot_age_bars"].notna().any() else np.nan,
    }


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], sort=False):
        total_returns = grp["total_return"].to_numpy(dtype=float)
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(np.nanmean(total_returns)) if len(total_returns) else np.nan,
            "positive_asset_ratio": float(np.nanmean(total_returns > 0)) if len(total_returns) else np.nan,
            "mean_trades": float(grp["trades"].mean()),
            "mean_candidate_to_trade_ratio": float(grp["candidate_to_trade_ratio"].mean()),
            "mean_false_break_rate": float(grp["false_break_rate"].mean()),
            "mean_win_rate": float(grp["win_rate"].mean()),
            "mean_retest_wait_bars": float(grp["mean_retest_wait_bars"].mean()),
            "mean_pivot_age_bars": float(grp["mean_pivot_age_bars"].mean()),
        })
    return pd.DataFrame(rows)


def build_time_stability(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_break_rate"])
    work = primary_trades.copy()
    work["entry_ts_dt"] = pd.to_datetime(work["entry_ts"], utc=True)
    try:
        work["time_bucket"] = pd.qcut(work["entry_ts_dt"].astype("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    except ValueError:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_break_rate"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "time_bucket": str(bucket),
            "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
            "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
            "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
            "mean_false_break_rate": float(grp["false_break_flag"].mean()) if len(grp) else np.nan,
        })
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_df: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    baseline = overall[(overall["variant"] == BASELINE_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以站住。"
    p = primary.iloc[0]
    mean_ret = float(p["mean_total_return"])
    pos_ratio = float(p["positive_asset_ratio"])
    mean_trades = float(p["mean_trades"])
    false_rate = float(p["mean_false_break_rate"]) if not pd.isna(p["mean_false_break_rate"]) else 1.0
    positive_buckets = int((time_df["mean_total_return"] > 0).sum()) if not time_df.empty else 0

    baseline_ret = float(baseline.iloc[0]["mean_total_return"]) if not baseline.empty else np.nan
    baseline_false = float(baseline.iloc[0]["mean_false_break_rate"]) if not baseline.empty else np.nan
    better_than_baseline = (not pd.isna(baseline_ret) and mean_ret > baseline_ret) or (not pd.isna(baseline_false) and false_rate < baseline_false)

    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 12 and false_rate <= 0.45 and positive_buckets >= 2 and better_than_baseline:
        return "P1 weak candidate / evidence pool", "最小 clean replication 没直接塌：成本后仍为正、跨资产不只剩单腿、时间 pocket 也不只靠单桶，而且相对 breakout-only 至少在收益或假突破率上有净改进。"
    return "park / evidence pool", "最小 clean replication 没把它拉进候选池：要么成本后仍偏弱，要么交易数 / 时间 pocket / 假突破率没有一起站住。"


def build_html(overall: pd.DataFrame, asset_df: pd.DataFrame, time_df: pd.DataFrame, param_df: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall["variant"] == PRIMARY_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    baseline = overall[(overall["variant"] == BASELINE_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        headline = "主变体没有形成可用样本。"
    else:
        p = primary.iloc[0]
        baseline_note = ""
        if not baseline.empty:
            b = baseline.iloc[0]
            baseline_note = f"；相对 breakout-only 的 mean_total_return≈{pct(b['mean_total_return'])}、false_break_rate≈{pct(b['mean_false_break_rate'])}。"
        headline = (
            f"主变体 {PRIMARY_LABEL} 在 6bps/side 下：跨资产 mean_total_return≈{pct(p['mean_total_return'])}、"
            f"positive_asset_ratio≈{pct(p['positive_asset_ratio'])}、mean_trades≈{num(p['mean_trades'],1)}、"
            f"mean_false_break_rate≈{pct(p['mean_false_break_rate'])}{baseline_note}"
        )
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 43 · ATR retest zone + bounce reclaim clean replication</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    ul {{ padding-left: 20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/quant_digests/report.html'>← 返回 Quant Digests</a></p>
  <h1>Rank 43 · ATR retest zone + bounce reclaim clean replication</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：最小 clean replication + Light Stability Pack ｜ 范围：BTC/ETH/SOL 120d 15m cache</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar。</li>
      <li>把 source intake 里的状态机压成 clean-room 规则：<code>confirmed breakout -&gt; ATR retest zone -&gt; no deep invalidation -&gt; bounce reclaim</code>。</li>
      <li>入场口径固定：<code>next-bar open</code>、<code>no-overlap</code>、持有 <code>{PRIMARY_HOLD_BARS}</code> 根 15m bar。</li>
      <li>Light Stability Pack 只做 4 项：时间稳定性、参数稳定性、跨标的稳定性、成本/交易数稳定性。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>confirmed breakout：</b>只使用 <code>SWING_LOOKBACK={SWING_LOOKBACK}</code> 的 causal pivot；bar close 首次越过最近确认 swing level，且 breakout candle body/range ≥ <code>0.5</code>。</li>
      <li><b>HTF filter：</b><code>1h EMA20 &gt; EMA50</code> 才允许 long，反向才允许 short。</li>
      <li><b>ATR retest zone：</b>突破后 <code>1~{PRIMARY_TIMEOUT}</code> 根内必须回到 level 附近 <code>±0.5 ATR</code>。</li>
      <li><b>invalidation：</b>若 close 反向穿越 level 超过 <code>1 ATR</code>，setup 直接取消。</li>
      <li><b>bounce reclaim：</b>回踩后必须出现同向 bounce candle，且 close 重新站回/压回 breakout level，才在下一根 open 入场。</li>
      <li><b>false-break 定义：</b>入场后前 <code>{PRIMARY_FALSE_BREAK_BARS}</code> 根内若 close 反向穿越 level 超过 <code>0.5 ATR</code>，记为 false break。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(verdict_reason)}</p>
  </div>

  <div class='card'>
    <h2>跨资产总表</h2>
    {render_table(overall[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_candidate_to_trade_ratio","mean_false_break_rate","mean_win_rate","mean_retest_wait_bars"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_candidate_to_trade_ratio","mean_false_break_rate","mean_win_rate"}, digits_cols={"mean_trades":1,"mean_retest_wait_bars":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要</h2>
    {render_table(asset_df[["asset","variant","cost_bps_per_side","candidate_events","trades","candidate_to_trade_ratio","total_return","false_break_rate","mean_retest_wait_bars","mean_pivot_age_bars"]], percent_cols={"candidate_to_trade_ratio","total_return","false_break_rate"}, digits_cols={"candidate_events":0,"trades":0,"mean_retest_wait_bars":1,"mean_pivot_age_bars":1})}
  </div>

  <div class='card'>
    <h2>时间稳定性（主变体 6bps）</h2>
    {render_table(time_df[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_false_break_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_break_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>参数稳定性</h2>
    {render_table(param_df[["variant","mean_total_return","positive_asset_ratio","mean_trades","mean_false_break_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_break_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>成本 / 交易数稳定性（主变体）</h2>
    {render_table(cost_df[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_break_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_break_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>artifact</h2>
    <ul>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/overall_summary.csv'>overall_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/asset_summary.csv'>asset_summary.csv</a></li>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/time_stability.csv'>time_stability.csv</a></li>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/parameter_stability.csv'>parameter_stability.csv</a></li>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/cost_trade_stability.csv'>cost_trade_stability.csv</a></li>
      <li><a href='../../../artifacts/scout_rank43_atr_retest_bounce_15m/trades_primary_6bps.csv'>trades_primary_6bps.csv</a></li>
    </ul>
  </div>
</body>
</html>
"""


def update_todo(verdict: str, generated_at: str, overall: pd.DataFrame, time_df: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    primary = overall[(overall["variant"] == PRIMARY_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    baseline = overall[(overall["variant"] == BASELINE_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        stats = "主变体没有形成可用样本。"
    else:
        p = primary.iloc[0]
        stats = (
            f"主变体 `{PRIMARY_LABEL}` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(p['mean_total_return'])}`、"
            f"`positive_asset_ratio≈{pct(p['positive_asset_ratio'])}`、`mean_trades≈{num(p['mean_trades'],1)}`、"
            f"`mean_false_break_rate≈{pct(p['mean_false_break_rate'])}`。"
        )
    if baseline.empty:
        baseline_note = "breakout-only baseline 当前无可用比较。"
    else:
        b = baseline.iloc[0]
        baseline_note = (
            f"相对 `breakout_only` 的 `mean_total_return≈{pct(b['mean_total_return'])}`、"
            f"`mean_false_break_rate≈{pct(b['mean_false_break_rate'])}`，当前 retest 版本"
            + ("至少在收益或假突破率上给出了一点净改进。" if not primary.empty and ((primary.iloc[0]['mean_total_return'] > b['mean_total_return']) or (primary.iloc[0]['mean_false_break_rate'] < b['mean_false_break_rate'])) else "没有给出足够净改进。")
        )
    if time_df.empty:
        time_note = "时间稳定性样本偏薄，当前不足以拆出 3 个可靠 pocket。"
    else:
        parts = [f"{r['time_bucket']}≈{pct(r['mean_total_return'])}/{pct(r['positive_asset_ratio'])}" for _, r in time_df.iterrows()]
        time_note = "time-pocket honesty：" + "；".join(parts) + "。"

    old_sentence = "换句话说，若下一轮 `EMA` 仍在 waiting-window，bot3 默认应先执行 `Run 2 / Rank 43` 的那 **1 次最小 clean replication**；只有这一步也被真实 blocker 卡住，或 fresh intake 再次耗尽，才回到 `Run 3 / tiny-live plumbing`。"
    if verdict.startswith("P1"):
        new_sentence = "换句话说，`Rank 43` 的那 **1 次最小 clean replication** 已经落地；若下一轮 `EMA` 仍在 waiting-window，bot3 默认只允许再给它 **1 次便宜诚实检查**，回答是否能从 `P1 weak candidate` 升到 `P2 paper candidate`，否则就应压回 `park / evidence pool`。"
    else:
        new_sentence = "换句话说，`Rank 43` 的那 **1 次最小 clean replication** 已经如实落地，而且当前 hard verdict 仍是 **`park / evidence pool`**；若下一轮 `EMA` 仍在 waiting-window，bot3 默认应回到新的 `fresh paper / repo based 5m / 15m crypto intake`，而不是继续磨这条线。"
    if old_sentence in text:
        text = text.replace(old_sentence, new_sentence, 1)

    marker = "43. `Rank 43 ATR retest zone + bounce reclaim / breakout confirmation`（repo `TheVision333/trading-bot`）→ **`admit_to_clean_replication_queue`**"
    start = text.find(marker)
    if start != -1:
        end = text.find("\n\n- **Rank 35 之后的 External-data Scout", start)
        if end != -1:
            block = f"""43. `Rank 43 ATR retest zone + bounce reclaim / breakout confirmation`（repo `TheVision333/trading-bot`）→ **`{verdict}`**
    - 已完成 `fresh repo source intake -> 最小 clean replication + Light Stability Pack`；固定复用 `BTC/ETH/SOL 120d 15m` cache，不追新 bar。
    - clean-room 规则保持为：`trade on = confirmed swing breakout -> ATR retest zone -> no deep invalidation -> bounce reclaim`；`trade off = 无 breakout / 回踩超时 / 深穿失效 / bounce reclaim 失败`。
    - 当前主证据：{stats}
    - {baseline_note}
    - {time_note}
    - **最新补充（{generated_at}）**：这轮 clean replication 的 hard verdict 是 **`{verdict}`**。更直白地说：`Rank 43` 已不再停留在 `admit_to_clean_replication_queue`；若后续继续认领，默认只能按这个 verdict 走——`P1` 才配拿那唯一允许的一次便宜诚实检查，`park` 则应回到 evidence pool，而不是继续停在 intake 文案上。
    - 网页落点：`reports/site/factors/scout_rank43_atr_retest_bounce_15m/report.html`。
"""
            text = text[:start] + block + text[end:]

    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    variant_cfgs = [CandidateConfig(label, zone, timeout) for label, zone, timeout in PARAM_GRID]
    primary_cfg = next(cfg for cfg in variant_cfgs if cfg.label == PRIMARY_LABEL)

    asset_rows = []
    all_costed_trades = []
    primary_costed_trades = []

    for asset, frame in frames.items():
        base_trades, base_meta = simulate_variant(frame, asset, primary_cfg, baseline=True)
        for cost in COSTS:
            base_costed = apply_cost(base_trades, cost)
            asset_rows.append(summarize_asset(base_costed, asset=asset, variant=BASELINE_LABEL, cost_bps=cost, candidate_events=int(base_meta["candidate_events"])))
            all_costed_trades.append(base_costed)

        for cfg in variant_cfgs:
            trades, meta = simulate_variant(frame, asset, cfg, baseline=False)
            if cfg.label == PRIMARY_LABEL:
                frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
            for cost in COSTS:
                costed = apply_cost(trades, cost)
                asset_rows.append(summarize_asset(costed, asset=asset, variant=cfg.label, cost_bps=cost, candidate_events=int(meta["candidate_events"])))
                all_costed_trades.append(costed)
                if cfg.label == PRIMARY_LABEL and cost == PRIMARY_COST:
                    primary_costed_trades.append(costed)
                    costed.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd','')}.csv", index=False)

    asset_df = pd.DataFrame(asset_rows)
    overall = summarize_overall(asset_df)
    primary_trades_df = pd.concat(primary_costed_trades, ignore_index=True) if primary_costed_trades else pd.DataFrame()
    time_df = build_time_stability(primary_trades_df)

    param_df = overall[(overall["variant"] != BASELINE_LABEL) & (overall["cost_bps_per_side"] == PRIMARY_COST)].copy().sort_values(["mean_total_return", "positive_asset_ratio", "mean_false_break_rate"], ascending=[False, False, True]).reset_index(drop=True)
    cost_df = overall[overall["variant"] == PRIMARY_LABEL].copy().sort_values("cost_bps_per_side").reset_index(drop=True)
    verdict, verdict_reason = build_verdict(overall, time_df)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    pd.concat([df for df in all_costed_trades if not df.empty], ignore_index=True).to_csv(ART_DIR / "all_trades.csv", index=False)
    primary_trades_df.to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_df.to_csv(ART_DIR / "time_stability.csv", index=False)
    param_df.to_csv(ART_DIR / "parameter_stability.csv", index=False)
    cost_df.to_csv(ART_DIR / "cost_trade_stability.csv", index=False)
    pd.DataFrame([{
        "generated_at_utc": generated_at,
        "candidate_id": "rank43_atr_retest_bounce_15m",
        "hard_verdict": verdict,
        "verdict_reason": verdict_reason,
        "source": "TheVision333/trading-bot",
        "scope": "BTC/ETH/SOL 120d 15m cache",
    }]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_df, time_df, param_df, cost_df, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank43_atr_retest_clean_replication.html").write_text(html, encoding="utf-8")
    update_todo(verdict, generated_at, overall, time_df)

    print(f"verdict={verdict}")
    primary = overall[(overall['variant'] == PRIMARY_LABEL) & (overall['cost_bps_per_side'] == PRIMARY_COST)]
    if not primary.empty:
        print(primary.iloc[0].to_dict())
    if not time_df.empty:
        print(time_df.to_dict(orient='records'))


if __name__ == "__main__":
    main()
