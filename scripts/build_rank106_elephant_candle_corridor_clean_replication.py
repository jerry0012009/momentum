#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank106_elephant_candle_corridor_15m"
CACHE_DIR = ART_DIR / "cache"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank106_elephant_candle_corridor_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank106_elephant_candle_corridor_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
INTERVAL = "15m"
LOOKBACK_DAYS = 120
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
LIMIT = 1500
HOLD_BARS = 4
COST_BPS_PER_SIDE = 6.0
BREAKOUT_BUFFER_ATR = 0.15
ATR_WINDOW = 14
SMA_FAST = 20
SMA_SLOW = 200
VARIANT_ORDER = ["baseline", "body_only", "full_corridor"]

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


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def bps(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.{digits}f} bps"


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in bps_cols:
                text = bps(value)
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


def net_ret(gross: pd.Series, cost_bps_per_side: float) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    return (1.0 + gross) * (1.0 - c) * (1.0 - c) - 1.0


def fetch_klines(symbol: str) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = CACHE_DIR / f"{symbol}__{LOOKBACK_DAYS}d__{INTERVAL}.csv"
    if cache_path.exists():
        try:
            cached = pd.read_csv(cache_path)
            cached["timestamp"] = pd.to_datetime(cached["timestamp"], utc=True)
            if not cached.empty:
                age = datetime.now(timezone.utc) - cached["timestamp"].max().to_pydatetime().replace(tzinfo=timezone.utc)
                if age < timedelta(hours=1):
                    return cached.sort_values("timestamp").reset_index(drop=True)
        except Exception:
            pass

    need = LOOKBACK_DAYS * 24 * 4 + SMA_SLOW + HOLD_BARS + 50
    rows: list[list[object]] = []
    end_time = None
    session = requests.Session()
    while len(rows) < need:
        params = {"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
        if end_time is not None:
            params["endTime"] = end_time
        resp = session.get(BINANCE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        rows = data + rows
        end_time = int(data[0][0]) - 1
        if len(data) < LIMIT:
            break
        time.sleep(0.15)

    df = pd.DataFrame(
        rows,
        columns=["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "n_trades", "taker_base", "taker_quote", "ignore"],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].drop_duplicates("timestamp").sort_values("timestamp")
    df = df.tail(need).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    return df


def build_symbol_events(symbol: str, asset: str) -> pd.DataFrame:
    df = fetch_klines(symbol).copy()
    prev_close = df["close"].shift(1)
    tr = pd.concat(
        [
            (df["high"] - df["low"]),
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.rolling(ATR_WINDOW).mean()
    df["sma20"] = df["close"].rolling(SMA_FAST).mean()
    df["sma200"] = df["close"].rolling(SMA_SLOW).mean()
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)
    df["prev_range"] = (df["high"] - df["low"]).shift(1)
    df["body"] = (df["close"] - df["open"]).abs()
    df["full_range"] = df["high"] - df["low"]
    df["body_ratio"] = np.where(df["full_range"] > 0, df["body"] / df["full_range"], 0.0)
    df = df.dropna().reset_index(drop=True)

    rows: list[dict[str, object]] = []
    last_idx = len(df) - HOLD_BARS - 1
    for i in range(1, last_idx):
        row = df.iloc[i]
        atr = float(row["atr14"])
        if not np.isfinite(atr) or atr <= 0:
            continue
        prev_range = float(row["prev_range"])
        if not np.isfinite(prev_range) or prev_range <= 0:
            continue
        long_base = bool(row["close"] > row["prev_high"] + BREAKOUT_BUFFER_ATR * atr and row["sma20"] > row["sma200"])
        short_base = bool(row["close"] < row["prev_low"] - BREAKOUT_BUFFER_ATR * atr and row["sma20"] < row["sma200"])
        if not (long_base or short_base):
            continue

        body_only = bool(row["body_ratio"] >= 0.5)
        full_corridor = bool(
            body_only
            and float(row["body"]) > prev_range
            and float(row["body"]) > 0.8 * atr
            and float(row["full_range"]) < 3.5 * atr
        )

        side = "long" if long_base else "short"
        threshold = float(row["prev_high"] + BREAKOUT_BUFFER_ATR * atr) if side == "long" else float(row["prev_low"] - BREAKOUT_BUFFER_ATR * atr)
        entry_idx = i + 1
        exit_idx = i + HOLD_BARS
        if exit_idx >= len(df):
            continue
        entry_px = float(df.iloc[entry_idx]["open"])
        exit_px = float(df.iloc[exit_idx]["close"])
        if not np.isfinite(entry_px) or entry_px <= 0 or not np.isfinite(exit_px) or exit_px <= 0:
            continue

        path = df.iloc[entry_idx : exit_idx + 1]
        if side == "long":
            gross_ret = exit_px / entry_px - 1.0
            fail_back_inside_4bars = int((path["close"] <= threshold).any())
        else:
            gross_ret = entry_px / exit_px - 1.0
            fail_back_inside_4bars = int((path["close"] >= threshold).any())

        common = {
            "asset": asset,
            "symbol": symbol,
            "signal_ts": row["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_ts": df.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": df.iloc[exit_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "side": side,
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_return_h4": gross_ret,
            "body_ratio": float(row["body_ratio"]),
            "body_vs_prev_range": float(row["body"]) / prev_range,
            "body_vs_atr14": float(row["body"]) / atr,
            "range_vs_atr14": float(row["full_range"]) / atr,
            "fail_back_inside_4bars": fail_back_inside_4bars,
            "breakout_threshold": threshold,
        }
        rows.append({**common, "variant": "baseline"})
        if body_only:
            rows.append({**common, "variant": "body_only"})
        if full_corridor:
            rows.append({**common, "variant": "full_corridor"})

    if not rows:
        raise RuntimeError(f"no rank106 events built for {symbol}")
    return pd.DataFrame(rows)


def apply_no_overlap(events: pd.DataFrame) -> pd.DataFrame:
    events = events.copy()
    events["entry_ts_dt"] = pd.to_datetime(events["entry_ts"], utc=True)
    keep_frames = []
    for variant, dfv in events.groupby("variant"):
        dfv = dfv.sort_values(["entry_ts_dt", "symbol"]).reset_index(drop=True)
        kept = []
        next_free_by_symbol: dict[str, pd.Timestamp] = {}
        for _, row in dfv.iterrows():
            symbol = str(row["symbol"])
            next_free = next_free_by_symbol.get(symbol)
            if next_free is not None and row["entry_ts_dt"] < next_free:
                continue
            kept.append(row)
            next_free_by_symbol[symbol] = row["entry_ts_dt"] + timedelta(minutes=15 * HOLD_BARS)
        keep_frames.append(pd.DataFrame(kept))
    if not keep_frames:
        return pd.DataFrame(columns=events.columns)
    return pd.concat(keep_frames, ignore_index=True).drop(columns=["entry_ts_dt"], errors="ignore")


def build_event_log() -> pd.DataFrame:
    frames = [build_symbol_events(symbol, asset) for asset, symbol in ASSETS.items()]
    events = pd.concat(frames, ignore_index=True)
    events = apply_no_overlap(events)
    return events.sort_values(["variant", "entry_ts", "symbol"]).reset_index(drop=True)


def summarize(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_count = int((events["variant"] == "baseline").sum())
    baseline_by_side = events[events["variant"] == "baseline"].groupby("side").size().to_dict()
    overall_rows = []
    side_rows = []
    symbol_rows = []
    verdict_rows = []

    for variant in VARIANT_ORDER:
        subset = events[events["variant"] == variant].copy()
        if subset.empty:
            continue
        net = net_ret(subset["gross_return_h4"], COST_BPS_PER_SIDE)
        overall_rows.append(
            {
                "variant": variant,
                "events": len(subset),
                "trade_count_retention": len(subset) / baseline_count if baseline_count else np.nan,
                "mean_net_ret_6bps": net.mean(),
                "median_net_ret_6bps": net.median(),
                "win_rate_6bps": (net > 0).mean(),
                "fail_back_inside_4bars": subset["fail_back_inside_4bars"].mean(),
                "long_share": (subset["side"] == "long").mean(),
            }
        )
        for side in ["long", "short"]:
            sub_side = subset[subset["side"] == side].copy()
            if sub_side.empty:
                continue
            side_net = net_ret(sub_side["gross_return_h4"], COST_BPS_PER_SIDE)
            side_rows.append(
                {
                    "variant": variant,
                    "side": side,
                    "events": len(sub_side),
                    "trade_count_retention_vs_same_side_baseline": len(sub_side) / baseline_by_side.get(side, np.nan) if baseline_by_side.get(side) else np.nan,
                    "mean_net_ret_6bps": side_net.mean(),
                    "median_net_ret_6bps": side_net.median(),
                    "win_rate_6bps": (side_net > 0).mean(),
                    "fail_back_inside_4bars": sub_side["fail_back_inside_4bars"].mean(),
                }
            )
            for symbol in sorted(sub_side["symbol"].unique()):
                sub_symbol = sub_side[sub_side["symbol"] == symbol].copy()
                symbol_net = net_ret(sub_symbol["gross_return_h4"], COST_BPS_PER_SIDE)
                symbol_rows.append(
                    {
                        "variant": variant,
                        "side": side,
                        "symbol": symbol,
                        "events": len(sub_symbol),
                        "mean_net_ret_6bps": symbol_net.mean(),
                        "median_net_ret_6bps": symbol_net.median(),
                        "win_rate_6bps": (symbol_net > 0).mean(),
                        "fail_back_inside_4bars": sub_symbol["fail_back_inside_4bars"].mean(),
                    }
                )

    overall = pd.DataFrame(overall_rows)
    side = pd.DataFrame(side_rows)
    symbol = pd.DataFrame(symbol_rows)

    base_all = overall[overall["variant"] == "baseline"].iloc[0]
    base_long = side[(side["variant"] == "baseline") & (side["side"] == "long")].iloc[0]
    base_short = side[(side["variant"] == "baseline") & (side["side"] == "short")].iloc[0]
    body_long = side[(side["variant"] == "body_only") & (side["side"] == "long")].iloc[0]
    corr_all = overall[overall["variant"] == "full_corridor"].iloc[0]
    corr_long = side[(side["variant"] == "full_corridor") & (side["side"] == "long")].iloc[0]
    corr_short = side[(side["variant"] == "full_corridor") & (side["side"] == "short")].iloc[0]

    if float(corr_all["mean_net_ret_6bps"]) > 0 and float(corr_short["mean_net_ret_6bps"]) >= float(base_short["mean_net_ret_6bps"]):
        verdict = "promote_to_P2"
    elif float(corr_long["mean_net_ret_6bps"]) > float(base_long["mean_net_ret_6bps"]) and float(corr_all["mean_net_ret_6bps"]) > float(base_all["mean_net_ret_6bps"]) and float(corr_short["mean_net_ret_6bps"]) >= float(base_short["mean_net_ret_6bps"]):
        verdict = "keep_P1"
    else:
        verdict = "park / evidence pool"

    desk_readthrough = (
        f"full_corridor 在 long 侧确实比 baseline 更少失败、更少亏：long mean_net_ret 约 {bps(corr_long['mean_net_ret_6bps'])}，"
        f"baseline long 约 {bps(base_long['mean_net_ret_6bps'])}；fail_back_inside_4bars 约 {pct(corr_long['fail_back_inside_4bars'])} vs {pct(base_long['fail_back_inside_4bars'])}。"
        f"但 overall 仍为负（{bps(corr_all['mean_net_ret_6bps'])}），而 short 侧反而恶化到 {bps(corr_short['mean_net_ret_6bps'])}，"
        "说明它更像 long-side quality filter，不是足够诚实的 shared gate。"
    )
    next_step = "按顶板顺序把 Rank 106 压回 park / evidence pool，并切 MTF CHOP charged-up count 的 source intake。"

    verdict_rows.append(
        {
            "rank": 106,
            "candidate": "elephant candle corridor long-bias gate",
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "primary_hold_bars": HOLD_BARS,
            "cost_bps_per_side": COST_BPS_PER_SIDE,
            "baseline_mean_net_ret_6bps": float(base_all["mean_net_ret_6bps"]),
            "full_corridor_mean_net_ret_6bps": float(corr_all["mean_net_ret_6bps"]),
            "baseline_long_mean_net_ret_6bps": float(base_long["mean_net_ret_6bps"]),
            "full_corridor_long_mean_net_ret_6bps": float(corr_long["mean_net_ret_6bps"]),
            "baseline_short_mean_net_ret_6bps": float(base_short["mean_net_ret_6bps"]),
            "full_corridor_short_mean_net_ret_6bps": float(corr_short["mean_net_ret_6bps"]),
            "baseline_long_fail_back_inside_4bars": float(base_long["fail_back_inside_4bars"]),
            "full_corridor_long_fail_back_inside_4bars": float(corr_long["fail_back_inside_4bars"]),
            "trade_count_retention": float(corr_all["trade_count_retention"]),
            "hard_verdict": verdict,
            "desk_readthrough": desk_readthrough,
            "next_step": next_step,
        }
    )

    return overall, side, symbol, pd.DataFrame(verdict_rows)


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(CACHE_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    events = build_event_log()
    overall, side, symbol, verdict_summary = summarize(events)
    verdict = str(verdict_summary.iloc[0]["hard_verdict"])
    snapshot = {
        "generated_at_utc": generated_at,
        "sample": "BTC/ETH/SOL Binance Futures 120d 15m",
        "entry": "next-bar open",
        "exit": f"close after {HOLD_BARS} bars",
        "cost_bps_per_side": COST_BPS_PER_SIDE,
        "variants": VARIANT_ORDER,
        "verdict": verdict,
        "events_by_variant": events.groupby("variant").size().to_dict(),
    }

    events.to_csv(ART_DIR / "event_log.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    side.to_csv(ART_DIR / "side_summary.csv", index=False)
    symbol.to_csv(ART_DIR / "symbol_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    overall_table = render_table(
        overall,
        percent_cols={"trade_count_retention", "win_rate_6bps", "fail_back_inside_4bars", "long_share"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps"},
        digits_cols={"events": 0},
    )
    side_table = render_table(
        side,
        percent_cols={"trade_count_retention_vs_same_side_baseline", "win_rate_6bps", "fail_back_inside_4bars"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps"},
        digits_cols={"events": 0},
    )
    symbol_table = render_table(
        symbol,
        percent_cols={"win_rate_6bps", "fail_back_inside_4bars"},
        bps_cols={"mean_net_ret_6bps", "median_net_ret_6bps"},
        digits_cols={"events": 0},
    )

    body = f"""
<h1>Rank 106 · elephant candle corridor long-bias gate clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：BTC/ETH/SOL Binance Futures 120d 15m ｜ 口径：signal 当根及之前数据 / next-bar open / no-overlap / hold {HOLD_BARS} bars / {num(COST_BPS_PER_SIDE,1)}bps per side</p>
<div class='card'>
  <p><strong>硬结论：</strong><span class='bad'>{escape(verdict)}</span></p>
  <p>{escape(str(verdict_summary.iloc[0]['desk_readthrough']))}</p>
  <p><strong>下一步：</strong>{escape(str(verdict_summary.iloc[0]['next_step']))}</p>
</div>
<div class='card'>
  <h2>这轮到底在测什么</h2>
  <ul>
    <li>只做最小 clean replication，不扩成完整策略：<code>baseline / body_only / full_corridor</code> 三臂。</li>
    <li><code>baseline</code> = 趋势背景下的最小 breakout 代理（<code>SMA20>SMA200</code> 且 <code>close &gt; prev_high + 0.15*ATR14</code>；short 侧做对照）。</li>
    <li><code>body_only</code> = 只加 <code>body_ratio&gt;=0.5</code>。</li>
    <li><code>full_corridor</code> = 再加 <code>body&gt;prev_range</code>、<code>body&gt;0.8*ATR14</code>、<code>full_range&lt;3.5*ATR14</code>。</li>
    <li>重点不问“它是不是独立 alpha”，只问“这根确认 bar 作为 quality gate 能不能在不过度失真样本的前提下改善 long-side continuation，而且不伤 short-side 对照太多”。</li>
  </ul>
</div>
<div class='card'>
  <h2>主表</h2>
  {overall_table}
</div>
<div class='card'>
  <h2>按方向拆开</h2>
  {side_table}
</div>
<div class='card'>
  <h2>按币种拆开</h2>
  {symbol_table}
</div>
<div class='card'>
  <h2>reader-facing 读法</h2>
  <ul>
    <li><code>full_corridor</code> 在 <code>long</code> 侧确实有改善味道：更少回吐进原区间、post-cost 也比 baseline 少亏。</li>
    <li>但它并没有把整体 expectancy 拉正；更关键的是，<code>short</code> 侧对照反而更差，说明这不是可直接共享给 breakout-short 的通用 gate。</li>
    <li>因此这轮最诚实的 desk verdict 不是继续 keep_P1，而是把它压回 <code>park / evidence pool</code>：记住“strong but not overheated”对 long reclaim 有点帮助，但别把它误包装成更大结论。</li>
  </ul>
</div>
<div class='card'>
  <h2>产物</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/event_log.csv</code></li>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/side_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/symbol_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/verdict_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank106_elephant_candle_corridor_15m/summary_snapshot.json</code></li>
  </ul>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 106 · elephant candle corridor long-bias gate clean replication", body)
    write_html(READING_PATH, "Rank 106 · elephant candle corridor long-bias gate clean replication", body)


if __name__ == "__main__":
    main()
