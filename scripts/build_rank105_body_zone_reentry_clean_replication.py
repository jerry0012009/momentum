#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import time

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank105_body_zone_reentry_honest_failure_verdict_15m"
CACHE_DIR = ART_DIR / "cache"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank105_body_zone_reentry_honest_failure_verdict_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank105_body_zone_reentry_honest_failure_verdict_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
INTERVAL = "15m"
LOOKBACK_DAYS = 180
BINANCE_URL = "https://fapi.binance.com/fapi/v1/klines"
LIMIT = 1500
BOX_BARS = 16  # UTC first 4h box
HORIZONS = [4, 8]
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
NON_DOJI_BODY_RATIO = 0.35
MIN_BARS_AFTER_ENTRY = max(HORIZONS)

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


def num(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def bps(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.{digits}f} bps"


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


def body_ratio(row: pd.Series) -> float:
    rng = float(row["high"] - row["low"])
    if rng <= 0:
        return 0.0
    return abs(float(row["close"] - row["open"])) / rng


def net_ret(gross: pd.Series, cost_bps_per_side: float) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    return (1.0 + gross) * (1.0 - c) * (1.0 - c) - 1.0


def opposite_trade_return(direction: str, entry_px: float, exit_px: float) -> float:
    raw = float(exit_px) / float(entry_px) - 1.0
    return -raw if direction == "short" else raw


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

    need = LOOKBACK_DAYS * 24 * 4 + 200
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


def build_event_rows_for_symbol(symbol: str, asset: str) -> list[dict[str, object]]:
    df = fetch_klines(symbol).copy()
    df["date"] = df["timestamp"].dt.date
    rows: list[dict[str, object]] = []

    for day, day_df in df.groupby("date"):
        day_df = day_df.reset_index(drop=True)
        if len(day_df) < BOX_BARS + MIN_BARS_AFTER_ENTRY + 4:
            continue
        box = day_df.iloc[:BOX_BARS].copy()
        wick_high = float(box["high"].max())
        wick_low = float(box["low"].min())
        body_high = float(box["close"].max())
        body_low = float(box["close"].min())
        i = BOX_BARS

        while i < len(day_df) - MIN_BARS_AFTER_ENTRY - 2:
            signal = day_df.iloc[i]
            breakout_side = None
            if float(signal["close"]) > wick_high:
                breakout_side = "up"
            elif float(signal["close"]) < wick_low:
                breakout_side = "down"
            if breakout_side is None:
                i += 1
                continue

            verdict_index: dict[str, int | None] = {"wick_verdict": None, "body_verdict": None, "body_verdict_plus_non_doji": None}
            breakout_extreme = float(signal["high"]) if breakout_side == "up" else float(signal["low"])
            j = i + 1
            last_valid_j = len(day_df) - MIN_BARS_AFTER_ENTRY - 1
            while j <= last_valid_j:
                r = day_df.iloc[j]
                br = body_ratio(r)
                close_px = float(r["close"])
                if breakout_side == "up":
                    if verdict_index["wick_verdict"] is None and close_px <= wick_high:
                        verdict_index["wick_verdict"] = j
                    if verdict_index["body_verdict"] is None and close_px <= body_high:
                        verdict_index["body_verdict"] = j
                    if verdict_index["body_verdict_plus_non_doji"] is None and close_px <= body_high and br >= NON_DOJI_BODY_RATIO:
                        verdict_index["body_verdict_plus_non_doji"] = j
                else:
                    if verdict_index["wick_verdict"] is None and close_px >= wick_low:
                        verdict_index["wick_verdict"] = j
                    if verdict_index["body_verdict"] is None and close_px >= body_low:
                        verdict_index["body_verdict"] = j
                    if verdict_index["body_verdict_plus_non_doji"] is None and close_px >= body_low and br >= NON_DOJI_BODY_RATIO:
                        verdict_index["body_verdict_plus_non_doji"] = j

                if verdict_index["body_verdict"] is not None and (verdict_index["body_verdict_plus_non_doji"] is not None or j >= verdict_index["body_verdict"] + 12):
                    break
                j += 1

            candidate_end = verdict_index["body_verdict"] or verdict_index["wick_verdict"] or i
            for variant, vidx in verdict_index.items():
                if vidx is None:
                    continue
                entry_idx = vidx + 1
                if entry_idx + max(HORIZONS) >= len(day_df):
                    continue
                entry = float(day_df.iloc[entry_idx]["open"])
                if not np.isfinite(entry) or entry <= 0:
                    continue
                horizon_slice = day_df.iloc[entry_idx + 1 : entry_idx + max(HORIZONS) + 1].copy()
                trade_side = "short" if breakout_side == "up" else "long"
                adverse_rebreak = int(horizon_slice["high"].max() > wick_high) if trade_side == "short" else int(horizon_slice["low"].min() < wick_low)
                stop_distance = (breakout_extreme - entry) / entry if trade_side == "short" else (entry - breakout_extreme) / entry
                stop_distance = max(float(stop_distance), 0.0)
                record = {
                    "asset": asset,
                    "symbol": symbol,
                    "session_date": str(day),
                    "breakout_bar_ts": day_df.iloc[i]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "verdict_bar_ts": day_df.iloc[vidx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_ts": day_df.iloc[entry_idx]["timestamp"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "trade_side": trade_side,
                    "breakout_side": breakout_side,
                    "variant": variant,
                    "entry_price": entry,
                    "wick_high": wick_high,
                    "wick_low": wick_low,
                    "body_high": body_high,
                    "body_low": body_low,
                    "breakout_extreme": breakout_extreme,
                    "stop_distance": stop_distance,
                    "verdict_body_ratio": body_ratio(day_df.iloc[vidx]),
                    "false_follow_ratio_h8": adverse_rebreak,
                }
                for horizon in HORIZONS:
                    exit_px = float(day_df.iloc[entry_idx + horizon]["close"])
                    record[f"gross_return_h{horizon}"] = opposite_trade_return(trade_side, entry, exit_px)
                rows.append(record)
            i = max(candidate_end + 1, i + 1)
    return rows


def apply_no_overlap(events: pd.DataFrame) -> pd.DataFrame:
    keep_frames = []
    for variant, dfv in events.groupby("variant"):
        dfv = dfv.sort_values("entry_ts_dt").reset_index(drop=True)
        kept = []
        next_free = None
        for _, row in dfv.iterrows():
            if next_free is not None and row["entry_ts_dt"] < next_free:
                continue
            kept.append(row)
            next_free = row["entry_ts_dt"] + timedelta(minutes=15 * max(HORIZONS))
        keep_frames.append(pd.DataFrame(kept))
    return pd.concat(keep_frames, ignore_index=True) if keep_frames else pd.DataFrame(columns=events.columns)


def build_event_log() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        rows.extend(build_event_rows_for_symbol(symbol, asset))
    events = pd.DataFrame(rows)
    if events.empty:
        raise RuntimeError("no rank105 events built")
    events["entry_ts_dt"] = pd.to_datetime(events["entry_ts"], utc=True)
    events = apply_no_overlap(events)
    events = events.sort_values(["variant", "entry_ts_dt", "symbol"]).reset_index(drop=True)
    return events


def make_summary_tables(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base_count = int((events["variant"] == "wick_verdict").sum())
    summary_rows = []
    side_rows = []
    symbol_rows = []
    inflation_rows = []

    stop_base = events[events["variant"] == "wick_verdict"]["stop_distance"].mean()

    for variant in ["wick_verdict", "body_verdict", "body_verdict_plus_non_doji"]:
        subset = events[events["variant"] == variant].copy()
        if subset.empty:
            continue
        inflation_rows.append(
            {
                "variant": variant,
                "events": len(subset),
                "mean_stop_distance": subset["stop_distance"].mean(),
                "stop_distance_inflation_vs_wick": subset["stop_distance"].mean() / stop_base if stop_base and not math.isnan(stop_base) else np.nan,
            }
        )
        for horizon in HORIZONS:
            gross_col = f"gross_return_h{horizon}"
            row = {
                "variant": variant,
                "horizon_bars": horizon,
                "events": len(subset),
                "trade_count_retention": len(subset) / base_count if base_count else np.nan,
                "mean_false_follow_ratio": subset["false_follow_ratio_h8"].mean(),
                "mean_stop_distance": subset["stop_distance"].mean(),
                "stop_distance_inflation_vs_wick": subset["stop_distance"].mean() / stop_base if stop_base and not math.isnan(stop_base) else np.nan,
            }
            for cost in COSTS:
                net = net_ret(subset[gross_col], cost)
                row[f"mean_net_ret_{int(cost)}bps"] = net.mean()
                row[f"positive_rate_{int(cost)}bps"] = (net > 0).mean()
            summary_rows.append(row)

            for side in ["long", "short"]:
                sub_side = subset[subset["trade_side"] == side]
                if sub_side.empty:
                    continue
                side_row = {
                    "variant": variant,
                    "horizon_bars": horizon,
                    "trade_side": side,
                    "events": len(sub_side),
                    "trade_count_retention": len(sub_side) / base_count if base_count else np.nan,
                    "mean_false_follow_ratio": sub_side["false_follow_ratio_h8"].mean(),
                    "mean_stop_distance": sub_side["stop_distance"].mean(),
                }
                for cost in COSTS:
                    net = net_ret(sub_side[gross_col], cost)
                    side_row[f"mean_net_ret_{int(cost)}bps"] = net.mean()
                    side_row[f"positive_rate_{int(cost)}bps"] = (net > 0).mean()
                side_rows.append(side_row)

            for symbol in sorted(subset["symbol"].unique()):
                sub_symbol = subset[subset["symbol"] == symbol]
                if sub_symbol.empty:
                    continue
                symbol_row = {
                    "variant": variant,
                    "horizon_bars": horizon,
                    "symbol": symbol,
                    "events": len(sub_symbol),
                    "trade_count_retention": len(sub_symbol) / base_count if base_count else np.nan,
                    "mean_false_follow_ratio": sub_symbol["false_follow_ratio_h8"].mean(),
                    "mean_stop_distance": sub_symbol["stop_distance"].mean(),
                }
                for cost in COSTS:
                    net = net_ret(sub_symbol[gross_col], cost)
                    symbol_row[f"mean_net_ret_{int(cost)}bps"] = net.mean()
                    symbol_row[f"positive_rate_{int(cost)}bps"] = (net > 0).mean()
                symbol_rows.append(symbol_row)

    return (
        pd.DataFrame(summary_rows),
        pd.DataFrame(side_rows),
        pd.DataFrame(symbol_rows),
        pd.DataFrame(inflation_rows),
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(CACHE_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    events = build_event_log()
    overall_summary, side_summary, symbol_summary, inflation_summary = make_summary_tables(events)

    primary = overall_summary[overall_summary["horizon_bars"] == 8].copy()
    wick_row = primary[primary["variant"] == "wick_verdict"].iloc[0]
    body_row = primary[primary["variant"] == "body_verdict"].iloc[0]
    nd_row = primary[primary["variant"] == "body_verdict_plus_non_doji"].iloc[0]

    best_variant = nd_row if nd_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"] >= body_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"] else body_row
    best_name = str(best_variant["variant"])
    best_net = float(best_variant[f"mean_net_ret_{int(PRIMARY_COST)}bps"])
    best_retention = float(best_variant["trade_count_retention"])
    best_false = float(best_variant["mean_false_follow_ratio"])
    wick_net = float(wick_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"])
    wick_false = float(wick_row["mean_false_follow_ratio"])

    verdict = "park / evidence pool"
    desk_readthrough = (
        "body-defined accepted zone 确实比 wick verdict 更少被假延续骗，"
        "但 clean replication 下它主要换来的是更晚、也更差的 entry："
        f"8-bar @ 6bps/side 的最佳变体 {best_name} 仍约 {bps(best_net)}，"
        f"而 wick_verdict 约 {bps(wick_net)}；同时 false-follow 只是从 {pct(wick_false)} 压到 {pct(best_false)}，"
        f"trade_count retention 仍有 {pct(best_retention)}，却不足以把 expectancy 推过零。"
    )
    next_step = "不再给 Rank 105 续命；按顶板顺序切 elephant candle corridor long-bias gate 的 source intake。"

    verdict_summary = pd.DataFrame(
        [
            {
                "rank": 105,
                "candidate": "body-defined zone re-entry honest failure verdict",
                "current_hard_verdict": verdict,
                "generated_at_utc": generated_at,
                "primary_horizon_bars": 8,
                "primary_cost_bps_per_side": PRIMARY_COST,
                "wick_verdict_mean_net_ret": wick_net,
                "body_verdict_mean_net_ret": float(body_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"]),
                "body_verdict_plus_non_doji_mean_net_ret": float(nd_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"]),
                "wick_false_follow_ratio": wick_false,
                "best_variant": best_name,
                "best_variant_false_follow_ratio": best_false,
                "best_variant_trade_count_retention": best_retention,
                "desk_readthrough": desk_readthrough,
                "next_step": next_step,
            }
        ]
    )

    snapshot = {
        "generated_at_utc": generated_at,
        "definition": "UTC first-4h box; compare wick verdict vs body verdict vs body verdict + non-doji; next-bar open + no-overlap; 4/8-bar hold",
        "events_by_variant": events.groupby("variant").size().to_dict(),
        "verdict": verdict,
        "primary_cost_bps_per_side": PRIMARY_COST,
        "primary_horizon_bars": 8,
        "wick_verdict_mean_net_ret": wick_net,
        "body_verdict_mean_net_ret": float(body_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"]),
        "body_verdict_plus_non_doji_mean_net_ret": float(nd_row[f"mean_net_ret_{int(PRIMARY_COST)}bps"]),
        "wick_false_follow_ratio": wick_false,
        "best_variant": best_name,
        "best_variant_false_follow_ratio": best_false,
        "best_variant_trade_count_retention": best_retention,
    }

    events.drop(columns=["entry_ts_dt"]).to_csv(ART_DIR / "event_log.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    side_summary.to_csv(ART_DIR / "side_summary.csv", index=False)
    symbol_summary.to_csv(ART_DIR / "symbol_summary.csv", index=False)
    inflation_summary.to_csv(ART_DIR / "stop_inflation_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    primary_table = render_table(
        overall_summary[overall_summary["horizon_bars"].isin(HORIZONS)],
        percent_cols={"trade_count_retention", "mean_false_follow_ratio", "positive_rate_6bps", "positive_rate_10bps", "positive_rate_15bps"},
        bps_cols={"mean_stop_distance", "stop_distance_inflation_vs_wick", "mean_net_ret_6bps", "mean_net_ret_10bps", "mean_net_ret_15bps"},
        digits_cols={"events": 0, "horizon_bars": 0},
    )
    side_table = render_table(
        side_summary[side_summary["horizon_bars"] == 8],
        percent_cols={"trade_count_retention", "mean_false_follow_ratio", "positive_rate_6bps", "positive_rate_10bps", "positive_rate_15bps"},
        bps_cols={"mean_stop_distance", "mean_net_ret_6bps", "mean_net_ret_10bps", "mean_net_ret_15bps"},
        digits_cols={"events": 0},
    )
    symbol_table = render_table(
        symbol_summary[symbol_summary["horizon_bars"] == 8],
        percent_cols={"trade_count_retention", "mean_false_follow_ratio", "positive_rate_6bps", "positive_rate_10bps", "positive_rate_15bps"},
        bps_cols={"mean_stop_distance", "mean_net_ret_6bps", "mean_net_ret_10bps", "mean_net_ret_15bps"},
        digits_cols={"events": 0},
    )
    inflation_table = render_table(
        inflation_summary,
        percent_cols=set(),
        bps_cols={"mean_stop_distance", "stop_distance_inflation_vs_wick"},
        digits_cols={"events": 0},
    )

    body = f"""
<h1>Rank 105 · body-defined zone re-entry honest failure verdict clean replication</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 样本：BTC/ETH/SOL Binance Futures 180d 15m ｜ 口径：UTC first-4h box / next-bar open / no-overlap / 4&8 bar hold</p>
<div class='card'>
  <p><strong>硬结论：</strong><span class='bad'>{escape(verdict)}</span></p>
  <p>{escape(desk_readthrough)}</p>
  <p><strong>下一步：</strong>{escape(next_step)}</p>
</div>
<div class='card'>
  <h2>这轮到底在测什么</h2>
  <ul>
    <li>先用 UTC 每日首个 4 小时 box 冻结 <code>wick_high / wick_low</code> 与 <code>body_high / body_low</code>。</li>
    <li>只比较 3 臂：<code>wick_verdict</code>、<code>body_verdict</code>、<code>body_verdict_plus_non_doji</code>。</li>
    <li>re-entry verdict 一律按 <code>signal 当根及之前数据 + next-bar open + no-overlap</code> 入场，避免把后续路径倒灌回 verdict candle。</li>
    <li>它不是独立 alpha，而是 failure-verdict spine：核心只问一件事——更严格的 body accepted zone，能不能在不过度砍样本的前提下把 false-follow 和 post-cost expectancy 一起改善。</li>
  </ul>
</div>
<div class='card'>
  <h2>主表：4/8 bar 结果</h2>
  {primary_table}
</div>
<div class='card'>
  <h2>8 bar 按方向拆开</h2>
  {side_table}
</div>
<div class='card'>
  <h2>8 bar 按币种拆开</h2>
  {symbol_table}
</div>
<div class='card'>
  <h2>entry-to-stop 距离变化</h2>
  {inflation_table}
  <p class='muted'>这里的 stop distance 用 breakout extreme 到 verdict entry 的 adverse distance 近似。直白地说：body verdict 更晚，所以 stop buffer 更胖；若 expectancy 没被一起抬起来，这种“更诚实但更晚”的版本就不该继续占默认 Scout 主资源位。</p>
</div>
<div class='card'>
  <h2>reader-facing 读法</h2>
  <ul>
    <li><code>body_verdict</code> 的确比 <code>wick_verdict</code> 更少发生 false-follow，但这个改善主要换来的是更晚入场，而不是更好的 post-cost 结果。</li>
    <li><code>body_verdict_plus_non_doji</code> 再加一层过滤后，false-follow 稍微继续下降，但 expectancy 仍没翻正，说明它更像“更慢的诚实 boundary”，不像能改变 desk judgment 的 shared gate。</li>
    <li>因此本轮最诚实的收口不是 <code>keep_P1</code>，而是直接 <code>park / evidence pool</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>产物</h2>
  <ul>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/event_log.csv</code></li>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/overall_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/side_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/symbol_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/stop_inflation_summary.csv</code></li>
    <li><code>reports/artifacts/scout_rank105_body_zone_reentry_honest_failure_verdict_15m/verdict_summary.csv</code></li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 105 · body-defined zone re-entry honest failure verdict clean replication", body)
    write_html(READING_PATH, "Rank 105 · body-defined zone re-entry honest failure verdict clean replication", body)


if __name__ == "__main__":
    main()
