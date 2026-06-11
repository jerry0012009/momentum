#!/usr/bin/env python3
"""Rank 139 — CUSUM event-bar confirm/veto gate (minimal clean replication).

Design constraints (from desk board):
- Keep the 15m entry logic unchanged (baseline setups).
- Only add a post-entry event-confirm / veto layer.
- Use *only* information available after entry, in time order.
- Classification within a fixed latency budget (default 45 minutes) on 1m closes.

This script intentionally stays small and auditable:
- trades = next-bar open entry, fixed-hold exit (8x 15m bars)
- event = first CUSUM threshold crossing (+/-) within the latency window
- gate arms compare: baseline vs veto_opp_dir vs confirm_same_dir_only
- evaluation window = residual return after the latency window (`T+3 -> T+8` style), to avoid overlapping the grouping window with the scored return window

Outputs:
- reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv
- reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_15M_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank139_cusum_event_bar_confirm_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank139_cusum_event_bar_confirm_veto_15m"
KLINE_1M_CACHE_DIR = ART_DIR / "kline_1m_cache"

BINANCE_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"
REQ_TIMEOUT = 20

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}

HOLD_BARS_15M = 8
LATENCY_MINUTES = 45
ATR_PERIOD = 14
THR_MULTS = [0.4, 0.6, 0.8]  # threshold = mult * ATR15m% (ATR/close)
COST_BPS = 6.0

# Practical guardrail for this 13m loop: avoid exploding API calls.
# We keep the test honest by sampling the *most recent* signals per setup/asset.
MAX_TRADES_PER_SETUP_ASSET = 18

ARMS = ["baseline", "veto_opp_dir", "confirm_same_dir_only"]

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
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
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
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def net_ret(gross_ret: float | pd.Series, cost_bps: float) -> float | pd.Series:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross_ret) * (1.0 - rate) * (1.0 - rate) - 1.0


def compute_atr_ewm(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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


def load_15m(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_15M_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_signals(df: pd.DataFrame) -> pd.DataFrame:
    # Baseline entry logic: intentionally consistent with common scout scripts.
    out = df.copy()
    out["ema9"] = out["close"].ewm(span=9, adjust=False).mean()
    out["ema15"] = out["close"].ewm(span=15, adjust=False).mean()
    out["ema_slope"] = out["ema9"].pct_change(3)
    out["psar"] = compute_psar(out)
    out["atr14"] = compute_atr_ewm(out)

    out["vol_ma20"] = out["volume"].rolling(20, min_periods=20).mean()
    out["prior20_high"] = out["high"].rolling(20, min_periods=20).max().shift(1)
    out["prior20_low"] = out["low"].rolling(20, min_periods=20).min().shift(1)

    # swing fib
    out["swing_high_30"] = out["high"].rolling(30, min_periods=30).max().shift(1)
    out["swing_low_30"] = out["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (out["swing_high_30"] - out["swing_low_30"]).replace(0, np.nan)
    out["fib_618"] = out["swing_high_30"] - 0.618 * swing_range
    out["fib_500"] = out["swing_high_30"] - 0.500 * swing_range

    out["fib_retest_long_signal"] = (
        out["fib_618"].notna()
        & out["atr14"].notna()
        & (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0)
        & (out["close"] > out["fib_618"])
        & (out["close"].shift(1) <= out["fib_618"].shift(1))
        & (out["low"] <= out["fib_618"] + 0.2 * out["atr14"])
        & (out["close"] > out["fib_500"])
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)

    out["ema_psar_long_signal"] = (
        (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0.0003)
        & (out["psar"] < out["close"])
        & (out["close"] > out["high"].shift(1))
        & (out["close"].shift(1) < out["ema9"].shift(1))
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)

    out["breakout_short_signal"] = (
        out["prior20_low"].notna()
        & out["atr14"].notna()
        & (out["ema9"] < out["ema15"])
        & (out["ema_slope"] < 0)
        & (out["close"] < out["prior20_low"])
        & (out["close"].shift(1) >= out["prior20_low"].shift(1))
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)

    return out


def fetch_1m_klines(symbol: str, start_ms: int, end_ms: int) -> pd.DataFrame:
    """Fetch 1m klines [start_ms, end_ms] inclusive. Uses local cache per window."""
    ensure_dir(KLINE_1M_CACHE_DIR)
    cache_path = KLINE_1M_CACHE_DIR / f"{symbol}__{start_ms}_{end_ms}.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
        return df

    # Binance limit=1500 per request. Window is at most 45m, so single call.
    params = {
        "symbol": symbol,
        "interval": "1m",
        "startTime": int(start_ms),
        "endTime": int(end_ms),
        "limit": 1500,
    }

    max_tries = 6
    last_err: Exception | None = None
    for i in range(max_tries):
        try:
            r = requests.get(BINANCE_KLINES_URL, params=params, timeout=REQ_TIMEOUT)
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else min(2.0 * (i + 1), 12.0)
                time.sleep(wait_s)
                continue
            r.raise_for_status()
            data = r.json()
            cols = [
                "open_time",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "num_trades",
                "taker_buy_base",
                "taker_buy_quote",
                "ignore",
            ]
            df = pd.DataFrame(data, columns=cols)
            for c in ["open", "high", "low", "close", "volume"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
            df.to_csv(cache_path, index=False)
            time.sleep(0.08)
            return df
        except requests.RequestException as e:
            last_err = e
            time.sleep(min(1.5 * (i + 1), 8.0))

    if last_err is not None:
        raise last_err
    raise RuntimeError("fetch_1m_klines failed without explicit exception")


def classify_from_rel(rel: np.ndarray, trade_dir: int, thr_pct: float) -> str:
    """Classify first threshold-crossing direction from cumulative return path."""
    up = rel >= float(thr_pct)
    dn = rel <= -float(thr_pct)

    idx_up = int(np.argmax(up)) if np.any(up) else None
    idx_dn = int(np.argmax(dn)) if np.any(dn) else None

    if idx_up is None and idx_dn is None:
        return "no_event_timeout"

    first: tuple[int, str] | None = None
    if idx_up is not None:
        first = (idx_up, "up")
    if idx_dn is not None and (first is None or idx_dn < first[0]):
        first = (idx_dn, "dn")

    assert first is not None
    _, kind = first
    if trade_dir > 0:
        return "same_dir_first" if kind == "up" else "opp_dir_first"
    return "same_dir_first" if kind == "dn" else "opp_dir_first"


def classify_first_event(
    symbol: str,
    entry_ts: pd.Timestamp,
    entry_px: float,
    trade_dir: int,
    thr_pct: float,
    latency_minutes: int = LATENCY_MINUTES,
) -> str:
    """Return: same_dir_first | opp_dir_first | no_event_timeout."""
    start = entry_ts
    end = entry_ts + pd.Timedelta(minutes=latency_minutes)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    df1 = fetch_1m_klines(symbol, start_ms, end_ms)
    if df1.empty or df1["close"].isna().all():
        return "no_event_timeout"

    closes = df1.sort_values("timestamp")["close"].to_numpy(dtype=float)
    rel = closes / float(entry_px) - 1.0
    return classify_from_rel(rel=rel, trade_dir=trade_dir, thr_pct=thr_pct)


def build_trades_for_asset(asset: str, symbol: str) -> pd.DataFrame:
    df = build_signals(load_15m(symbol, asset))

    rows: list[dict] = []
    for setup in SETUPS:
        sig_col = f"{setup}_signal"
        if sig_col not in df.columns:
            continue
        trade_dir = 1 if setup in LONG_SETUPS else -1

        # entry = next bar open; exit = close after HOLD_BARS_15M
        sig_idx = df.index[df[sig_col]].to_numpy(dtype=int)
        if len(sig_idx) > MAX_TRADES_PER_SETUP_ASSET:
            sig_idx = sig_idx[-MAX_TRADES_PER_SETUP_ASSET:]
        for i in sig_idx:
            entry_i = i + 1
            exit_i = entry_i + HOLD_BARS_15M - 1
            if exit_i >= len(df):
                continue
            entry_ts = df.loc[entry_i, "timestamp"]
            entry_px = float(df.loc[entry_i, "open"])
            exit_ts = df.loc[exit_i, "timestamp"]
            exit_px = float(df.loc[exit_i, "close"])

            gross_full_window = (exit_px / entry_px - 1.0) * float(trade_dir)

            atr = df.loc[i, "atr14"]
            close = df.loc[i, "close"]
            if pd.isna(atr) or pd.isna(close) or close <= 0:
                continue
            atr_pct = float(atr) / float(close)

            rows.append(
                {
                    "asset": asset,
                    "symbol": symbol,
                    "setup": setup,
                    "signal_ts": df.loc[i, "timestamp"],
                    "entry_ts": entry_ts,
                    "entry_px": entry_px,
                    "exit_ts": exit_ts,
                    "exit_px": exit_px,
                    "trade_dir": trade_dir,
                    "gross_ret_full_window": gross_full_window,
                    "atr15m_pct": atr_pct,
                }
            )

    trades = pd.DataFrame(rows)
    if trades.empty:
        return trades

    # classify events (single 1m fetch per trade, then apply all thresholds)
    labels_map: dict[float, list[str]] = {m: [] for m in THR_MULTS}
    latency_end_ts: list[pd.Timestamp] = []
    latency_end_px: list[float] = []
    gross_residual: list[float] = []

    for r in trades.itertuples(index=False):
        start = pd.Timestamp(r.entry_ts)
        end = start + pd.Timedelta(minutes=LATENCY_MINUTES)
        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)

        try:
            df1 = fetch_1m_klines(str(r.symbol), start_ms, end_ms)
        except requests.RequestException:
            df1 = pd.DataFrame()

        if df1.empty or df1["close"].isna().all():
            for mult in THR_MULTS:
                labels_map[mult].append("no_event_timeout")
            latency_end_ts.append(pd.NaT)
            latency_end_px.append(np.nan)
            gross_residual.append(np.nan)
            continue

        df1 = df1.sort_values("timestamp")
        closes = df1["close"].to_numpy(dtype=float)
        rel = closes / float(r.entry_px) - 1.0

        for mult in THR_MULTS:
            thr = float(mult) * float(r.atr15m_pct)
            labels_map[mult].append(classify_from_rel(rel=rel, trade_dir=int(r.trade_dir), thr_pct=thr))

        eval_ts = pd.Timestamp(df1.iloc[-1]["timestamp"])
        eval_px = float(df1.iloc[-1]["close"])
        latency_end_ts.append(eval_ts)
        latency_end_px.append(eval_px)
        gross_residual.append((float(r.exit_px) / eval_px - 1.0) * float(r.trade_dir))

    for mult in THR_MULTS:
        trades[f"event_{mult}"] = labels_map[mult]

    trades["latency_end_ts"] = latency_end_ts
    trades["latency_end_px"] = latency_end_px
    trades["gross_ret_residual"] = gross_residual
    # From this point onward, all summary / monitoring code reads `gross_ret` as the scored return window.
    trades["gross_ret"] = trades["gross_ret_residual"]

    return trades


def summarize(trades: pd.DataFrame) -> pd.DataFrame:
    out_rows: list[dict] = []
    for mult in THR_MULTS:
        col = f"event_{mult}"
        for arm in ARMS:
            df = trades
            if arm == "veto_opp_dir":
                df = df[df[col] != "opp_dir_first"]
            elif arm == "confirm_same_dir_only":
                df = df[df[col] == "same_dir_first"]

            if df.empty:
                out_rows.append(
                    {
                        "thr_mult": mult,
                        "arm": arm,
                        "trades": 0,
                        "retention_vs_base": np.nan,
                        "mean_gross": np.nan,
                        "mean_net@6bps": np.nan,
                        "positive_ratio_net": np.nan,
                        "same_dir_first": np.nan,
                        "opp_dir_first": np.nan,
                        "no_event_timeout": np.nan,
                    }
                )
                continue

            net = net_ret(df["gross_ret"].astype(float), COST_BPS)
            base_n = len(trades)
            out_rows.append(
                {
                    "thr_mult": mult,
                    "arm": arm,
                    "trades": int(len(df)),
                    "retention_vs_base": float(len(df)) / float(base_n) if base_n else np.nan,
                    "mean_gross": float(df["gross_ret"].mean()),
                    "mean_net@6bps": float(net.mean()),
                    "positive_ratio_net": float((net > 0).mean()),
                    "same_dir_first": float((df[col] == "same_dir_first").mean()),
                    "opp_dir_first": float((df[col] == "opp_dir_first").mean()),
                    "no_event_timeout": float((df[col] == "no_event_timeout").mean()),
                }
            )

    return pd.DataFrame(out_rows)


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    t0 = time.time()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    all_trades: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        all_trades.append(build_trades_for_asset(asset, symbol))

    trades = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    if trades.empty:
        (ART_DIR / "summary_by_arm.csv").write_text("", encoding="utf-8")
        write_html(
            SITE_DIR / "report.html",
            "Rank 139 minimal clean replication (empty)",
            f"<h1>Rank 139 · CUSUM confirm/veto gate</h1><p class='muted'>No trades generated.</p>",
        )
        return 1

    summary = summarize(trades)
    summary.to_csv(ART_DIR / "summary_by_arm.csv", index=False)
    trades.to_csv(ART_DIR / "trade_log.csv", index=False)

    # small evidence snippet: which arm best by mean_net@6bps per mult
    best = (
        summary.dropna(subset=["mean_net@6bps"])\
            .sort_values(["thr_mult", "mean_net@6bps"], ascending=[True, False])\
            .groupby("thr_mult", as_index=False)
            .head(1)
    )

    dur = time.time() - t0

    title = "Rank 139 · CUSUM event-bar confirm/veto gate · minimal clean replication"
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>generated_at: <code>{escape(generated_at)}</code> · latency=<code>{LATENCY_MINUTES}m</code> · hold=<code>{HOLD_BARS_15M}×15m</code> · scored_window=<code>latency_end → exit (T+3→T+8 style residual)</code> · costs=<code>{COST_BPS} bps/side</code> · thresholds=<code>{THR_MULTS}×ATR15m%</code></p>

<div class='card'>
  <b>这轮只回答一件事：</b>把 <code>CUSUM first-event</code> 当作 post-entry 的 <b>confirm / veto</b>，在**去掉前 45m 重叠窗口之后**，是否仍能改善后续残余区间（`T+3→T+8` style）的成本后期望？
  <ul>
    <li><code>baseline</code>：不加 gate。</li>
    <li><code>veto_opp_dir</code>：若先出现 <code>opp_dir_first</code> 则丢弃该笔。</li>
    <li><code>confirm_same_dir_only</code>：仅保留 <code>same_dir_first</code> 的交易。</li>
  </ul>
  <p class='muted'>注1：这里的“CUSUM”是最小可审计替身：用 entry 后 1m close 的累计收益穿越阈值来定义 first-event；目的是先把 <b>方向确认 / 否决</b> 口径跑通，而不是争论最优微观事件定义。</p>
  <p class='muted'>注1.5：本版开始，分组窗口（前 45m）与收益评估窗口显式分离：summary 中的 <code>gross_ret / mean_net@6bps</code> 均对应 <b>latency_end → exit</b> 的残余收益，而不再使用包含前 45m 的整段持有收益。</p>
  <p class='muted'>注2（13m 守门）：为避免把本轮变成 API 压测，每个 asset×setup 仅取最近 <code>{MAX_TRADES_PER_SETUP_ASSET}</code> 个信号样本做最小复现；如果这一轮出现明显 uplift，会在后续轮次再补全样本（或改成离线缓存后全量复现）。</p>
</div>

<h2>结果总表（跨资产 + 三个 setup 汇总）</h2>
{render_table(summary, percent_cols={"retention_vs_base","positive_ratio_net","same_dir_first","opp_dir_first","no_event_timeout"})}

<h2>每个阈值的最优 arm（按 mean_net@6bps）</h2>
{render_table(best, percent_cols={"retention_vs_base","positive_ratio_net","same_dir_first","opp_dir_first","no_event_timeout"})}

<div class='card'>
  <b>下一步建议（按 desk 规则）：</b>
  <ul>
    <li>若 <code>veto_opp_dir</code> 能在 retention 仍可接受的情况下把 <code>mean_net@6bps</code> 推到更高，倾向给 <code>Rank 139</code> 升级为 <code>P2 paper candidate</code>（shared confirm/veto layer）。</li>
    <li>若改善主要来自 <code>confirm_same_dir_only</code> 且 retention 明显塌缩，则更像“后验筛选”，应谨慎：要么 keep_P1 再做一项更贴近执行的 cheap check，要么直接 park。</li>
  </ul>
</div>

<p class='muted'>runtime: {dur:.1f}s · artifacts: <code>reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/</code></p>
"""

    write_html(SITE_DIR / "report.html", title, body)

    # minimal machine-readable meta
    meta = {
        "rank": 139,
        "generated_at": generated_at,
        "latency_minutes": LATENCY_MINUTES,
        "hold_bars_15m": HOLD_BARS_15M,
        "scored_window": "latency_end_to_exit_residual",
        "thr_mults": THR_MULTS,
        "cost_bps": COST_BPS,
        "trades": int(len(trades)),
        "summary_csv": str((ART_DIR / "summary_by_arm.csv").relative_to(ROOT)),
        "report_html": str((SITE_DIR / "report.html").relative_to(ROOT)),
    }
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[rank139] wrote {ART_DIR / 'summary_by_arm.csv'}")
    print(f"[rank139] wrote {SITE_DIR / 'report.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
