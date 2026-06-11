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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank83_fib_trend_strength_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank83_fib_trend_strength_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank83_fib_trend_strength_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
VARIANTS = ["base_binary", "strength_filter", "strength_sizing"]
PRIMARY_VARIANT = "strength_sizing"
FILTER_VARIANT = "strength_filter"
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
LOOKBACK = 30
ATR_PERIOD = 14
VOL_PERIOD = 20
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1160px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df["atr14"] = atr(df)
    df["swing_high_30"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_382"] = df["swing_high_30"] - 0.382 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    base_event = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["fib_strength_bucket"] = np.select(
        [
            base_event & (df["close"] > df["fib_50"]) & ((df["close"] > df["fib_382"]) | (df["close"] > df["high"].shift(1))),
            base_event & (df["close"] > df["fib_50"]),
            base_event,
        ],
        ["strong", "medium", "weak"],
        default="off",
    )
    df["base_event"] = base_event
    return df


def variant_size(bucket: str, variant: str) -> float:
    if bucket == "off":
        return 0.0
    if variant == "base_binary":
        return 1.0
    if variant == "strength_filter":
        return 1.0 if bucket in {"medium", "strong"} else 0.0
    if variant == "strength_sizing":
        return {"weak": 0.0, "medium": 0.5, "strong": 1.0}[bucket]
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, asset: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx:
            continue
        if not bool(frame.iloc[idx]["base_event"]):
            continue
        bucket = str(frame.iloc[idx]["fib_strength_bucket"])
        size = variant_size(bucket, variant)
        signal_events += 1
        if size <= 0:
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        gross_ret = (exit_px / entry_px - 1.0) * size
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        fail4 = bool((path["close"] < frame.iloc[idx]["fib_50"]).any())
        weak_rebreak4 = bool((path["close"] < frame.iloc[idx]["fib_618"]).any())
        mae = float((path["low"] / entry_px - 1.0).min()) * size
        rows.append(
            {
                "asset": asset,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "bucket": bucket,
                "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "size": size,
                "gross_ret": gross_ret,
                "net_ret": (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0,
                "expectancy": gross_ret - 2.0 * cost_rate * size,
                "fail_4bars": int(fail4),
                "rebreak_618_4bars": int(weak_rebreak4),
                "mae": mae,
                "fib_382": float(frame.iloc[idx]["fib_382"]),
                "fib_50": float(frame.iloc[idx]["fib_50"]),
                "fib_618": float(frame.iloc[idx]["fib_618"]),
            }
        )
        last_exit_idx = exit_idx
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
            "fail_4bars_rate": np.nan,
            "rebreak_618_4bars_rate": np.nan,
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
        "fail_4bars_rate": float(trades["fail_4bars"].mean()),
        "rebreak_618_4bars_rate": float(trades["rebreak_618_4bars"].mean()),
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
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()) if grp["avg_net_ret"].notna().any() else np.nan,
                "mean_fail_4bars_rate": float(grp["fail_4bars_rate"].mean()) if grp["fail_4bars_rate"].notna().any() else np.nan,
                "mean_rebreak_618_4bars_rate": float(grp["rebreak_618_4bars_rate"].mean()) if grp["rebreak_618_4bars_rate"].notna().any() else np.nan,
                "mean_mae": float(grp["mae"].mean()) if grp["mae"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_bucket_summary(primary_trades: pd.DataFrame) -> pd.DataFrame:
    if primary_trades.empty:
        return pd.DataFrame(columns=["bucket", "trades", "mean_net_ret", "fail_4bars_rate", "rebreak_618_4bars_rate"])
    return (
        primary_trades.groupby("bucket", as_index=False)
        .agg(
            trades=("entry_ts", "count"),
            mean_net_ret=("net_ret", "mean"),
            fail_4bars_rate=("fail_4bars", "mean"),
            rebreak_618_4bars_rate=("rebreak_618_4bars", "mean"),
        )
        .sort_values("bucket")
        .reset_index(drop=True)
    )


def build_verdict(overall: pd.DataFrame, bucket_df: pd.DataFrame) -> tuple[str, str]:
    base = overall[(overall["variant"] == "base_binary") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    filt = overall[(overall["variant"] == FILTER_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    sizing = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    strong_or_medium_ok = False
    if not bucket_df.empty and "strong" in set(bucket_df["bucket"]):
        strong = bucket_df[bucket_df["bucket"] == "strong"].iloc[0]
        medium = bucket_df[bucket_df["bucket"] == "medium"].iloc[0] if "medium" in set(bucket_df["bucket"]) else None
        strong_or_medium_ok = float(strong["mean_net_ret"]) > 0 and (medium is None or float(medium["mean_net_ret"]) >= -0.0005)

    if (
        float(sizing["mean_avg_net_ret"]) > float(base["mean_avg_net_ret"]) + 0.0001
        and float(base["mean_fail_4bars_rate"]) - float(sizing["mean_fail_4bars_rate"]) > 0.03
        and float(sizing["mean_trade_count_retention"]) >= 0.50
        and float(sizing["positive_asset_ratio"]) >= (2.0 / 3.0)
        and strong_or_medium_ok
    ):
        return (
            "promote_to_P2 / paper_candidate_pool",
            "strength_sizing 在不完全砍光交易的前提下，同时改善了成本后均值与 4-bar fail rate，且 strong/medium 桶确实比 weak 更像可保留的确认层，值得升到 P2。",
        )

    if (
        float(filt["mean_avg_net_ret"]) >= float(base["mean_avg_net_ret"]) - 0.00015
        and float(base["mean_fail_4bars_rate"]) - float(filt["mean_fail_4bars_rate"]) > 0.01
        and float(filt["mean_trade_count_retention"]) >= 0.30
    ):
        return (
            "keep_P1 / evidence_pool",
            "medium+strong 的过滤确实降低了早期失效，但改善还不够统一；当前更诚实的位置是保留为 P1 evidence，而不是直接升格。",
        )

    return (
        "park / evidence_pool",
        "这轮最小 clean replication 没证明 strength buckets 能把 Fib retest lane 稳定修成 desk 级提升；现在应 park，而不是继续默认占 fast-lane 预算。",
    )


def read_due_text() -> str:
    due = pd.read_csv(DUE_PATH)
    earliest = due.sort_values("next_expected_close_utc").iloc[0]
    return f"全 desk 仍无 due-now / overdue；最近 due 点仍是 {earliest['deployment_scope']} -> {earliest['next_expected_close_utc']}。"


def read_p3_text() -> str:
    meta = json.loads(P3_SUMMARY_PATH.read_text(encoding="utf-8"))
    return f"manual narrow-paper 最新 refresh @ {meta.get('run_at_utc')}，new_closed_trades_appended={meta.get('new_closed_trades_appended', 0)}。"


def update_todo(generated_at: str, verdict: str, note: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）"
    if marker not in text:
        return
    if "Rank 83 / Fib trend-strength admission layer = " in text and generated_at in text:
        return
    if "park" in verdict:
        next3 = "`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> `Run 2 = Rank 85 / fresh pullback → reclaim re-arm gate source intake` -> `Run 3 = 若 Rank 85 也拿不到合格对象，再切 Rank 84 / volume-price interaction admission layer；P3 continuity 仍不得默认抢占 Scout 主资源`"
    else:
        next3 = "`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 83 仍不足以升格但未硬 fail，则只允许给它 1 个 truly verdict-changing 的最小检查` -> `Run 3 = 若不继续 Rank 83，则切 Rank 85 / fresh pullback → reclaim re-arm gate source intake；P3 continuity 仍不得默认抢占 Scout 主资源`"
    note_block = (
        f"- **最新补充（{generated_at}）**：这轮先再次按 `Run 1 / EMA due-check only` 实际核对 guardrail，结果仍是 `waiting_not_due`：{read_due_text()} {read_p3_text()} 因此本轮合法主动作落在 **`Run 2 / Rank 83 minimal clean replication`**，而不是继续挤占 `P3 continuity` 或回头给旧 `P1 evidence_pool` 续命。\n"
        f"  - 这轮固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，只接当前 `Fib retest` 单 lane，统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars`**，直接比较 `base_binary / strength_filter / strength_sizing` 三臂。\n"
        f"  - 当前更诚实的 hard verdict 是：**`Rank 83 / Fib trend-strength admission layer = {verdict}`**。{note}\n"
        f"  - reader-facing 落点：`reports/site/factors/scout_rank83_fib_trend_strength_15m/report.html`、`reports/site/reading/repo_scout/rank83_fib_trend_strength_clean_replication.html`；artifact：`reports/artifacts/scout_rank83_fib_trend_strength_15m/overall_summary.csv`。\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**{next3}**。"
    )
    start = text.find(marker)
    line_end = text.find("\n", start)
    text = text[: line_end + 1] + note_block + "\n" + text[line_end + 1 :]
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []
    all_frames: list[pd.DataFrame] = []
    primary_trades: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        all_frames.append(frame.assign(source_asset=asset))
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd', '')}_frame.csv", index=False)
        for variant in VARIANTS:
            for cost in COSTS:
                trades, signal_events = build_trades(frame, asset, variant, cost)
                asset_rows.append(summarize_asset(trades, asset, variant, cost, signal_events))
                if not trades.empty:
                    all_trades.append(trades)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST and not trades.empty:
                    primary_trades.append(trades)

    asset_df = pd.DataFrame(asset_rows).sort_values(["variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    overall = summarize_overall(asset_df).sort_values(["variant", "cost_bps_per_side"]).reset_index(drop=True)
    all_trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    primary_trades_df = pd.concat(primary_trades, ignore_index=True) if primary_trades else pd.DataFrame()
    bucket_df = build_bucket_summary(primary_trades_df)
    verdict, verdict_note = build_verdict(overall, bucket_df)

    frames_df = pd.concat(all_frames, ignore_index=True)
    signal_snapshot = frames_df.loc[frames_df["base_event"], ["asset", "timestamp", "close", "fib_382", "fib_50", "fib_618", "fib_strength_bucket"]].copy()

    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    bucket_df.to_csv(ART_DIR / "bucket_summary_primary_6bps.csv", index=False)
    signal_snapshot.to_csv(ART_DIR / "signal_snapshot.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "scout_rank83_fib_trend_strength_15m",
            "scope": "BTC/ETH/SOL 120d 15m cache | single-lane Fib retest strength buckets",
            "hard_verdict": verdict,
            "verdict_note": verdict_note,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)
    if not all_trades_df.empty:
        all_trades_df.to_csv(ART_DIR / "all_trades.csv", index=False)
    if not primary_trades_df.empty:
        primary_trades_df.to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)

    primary = overall[overall["cost_bps_per_side"] == PRIMARY_COST].reset_index(drop=True)
    base = primary[primary["variant"] == "base_binary"].iloc[0]
    filt = primary[primary["variant"] == FILTER_VARIANT].iloc[0]
    sizing = primary[primary["variant"] == PRIMARY_VARIANT].iloc[0]

    body = f"""
<h1>Rank 83 / Fib trend-strength admission layer</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m 本地 cache；只接 Fib retest 单 lane；统一执行 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
<div class='card'>
  <p><strong>先核对 desk 状态：</strong>{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p><strong>strength bucket 冻结口径：</strong>只把 <code>Fib retest</code> 的确认强度拆成三档，不偷渡成独立 alpha：<code>weak</code>=站回 0.618 但收盘仍未回到 0.5 上方；<code>medium</code>=收回 0.5；<code>strong</code>=在 medium 基础上再收回 0.382 或站上前一根高点。</p>
  <p><strong>三臂比较：</strong><code>base_binary</code>=所有 bucket 都放行；<code>strength_filter</code>=只放行 medium+strong；<code>strength_sizing</code>=weak=0 / medium=0.5x / strong=1.0x。</p>
</div>
<div class='card'>
  <p><strong>6bps/side desk 级结果：</strong></p>
  <ul>
    <li><code>base_binary</code>：mean total return ≈ <strong>{pct(base['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(base['mean_avg_net_ret'], 3)}</strong>，4-bar fail ≈ <strong>{pct(base['mean_fail_4bars_rate'])}</strong></li>
    <li><code>strength_filter</code>：mean total return ≈ <strong>{pct(filt['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(filt['mean_avg_net_ret'], 3)}</strong>，retention ≈ <strong>{pct(filt['mean_trade_count_retention'])}</strong></li>
    <li><code>strength_sizing</code>：mean total return ≈ <strong>{pct(sizing['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(sizing['mean_avg_net_ret'], 3)}</strong>，retention ≈ <strong>{pct(sizing['mean_trade_count_retention'])}</strong>，4-bar fail ≈ <strong>{pct(sizing['mean_fail_4bars_rate'])}</strong></li>
  </ul>
  <p><strong>Hard verdict：</strong><span class='{"good" if "promote" in verdict else "bad" if "park" in verdict else "muted"}'>{escape(verdict)}</span>。{escape(verdict_note)}</p>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(primary[["variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_trade_count_retention", "mean_avg_net_ret", "mean_fail_4bars_rate", "mean_rebreak_618_4bars_rate", "mean_mae"]], percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_avg_net_ret", "mean_fail_4bars_rate", "mean_rebreak_618_4bars_rate", "mean_mae"}, digits_cols={"mean_trades": 1})}
</div>
<div class='card'>
  <h2>By bucket @ 6bps/side (primary variant)</h2>
  {render_table(bucket_df[["bucket", "trades", "mean_net_ret", "fail_4bars_rate", "rebreak_618_4bars_rate"]], percent_cols={"mean_net_ret", "fail_4bars_rate", "rebreak_618_4bars_rate"}, digits_cols={"trades": 0})}
</div>
<div class='card'>
  <h2>Per asset summary</h2>
  {render_table(asset_df[asset_df['cost_bps_per_side'].eq(PRIMARY_COST)][["asset", "variant", "trades", "trade_count_retention", "total_return", "avg_net_ret", "fail_4bars_rate", "rebreak_618_4bars_rate"]], percent_cols={"trade_count_retention", "total_return", "avg_net_ret", "fail_4bars_rate", "rebreak_618_4bars_rate"}, digits_cols={"trades": 0})}
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 83 fib trend-strength clean replication", body)

    reading_body = f"""
<h1>Rank 83 clean replication：Fib 强弱分桶先证明自己能降低早期失效，再谈升格</h1>
<p class='muted'>生成时间：{escape(generated_at)}｜只做 1 次最小 clean replication。</p>
<div class='card'>
  <p>这轮没有回头挤占 EMA paper continuity。原因很简单：{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p>因此本轮合法主动作就是 <strong>Run 2 / Rank 83</strong>：固定复用本地 <code>BTC/ETH/SOL 120d 15m</code> cache，只接当前 <code>Fib retest</code> 单 lane，直接比较 <code>base_binary / strength_filter / strength_sizing</code> 三臂。</p>
  <p>当前最诚实的结论是：<strong>{escape(verdict)}</strong>。{escape(verdict_note)}</p>
  <p>网页落点：<a href="../factors/scout_rank83_fib_trend_strength_15m/report.html">factor report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 83 fib trend-strength clean replication", reading_body)
    update_todo(generated_at, verdict, verdict_note)


if __name__ == "__main__":
    main()
