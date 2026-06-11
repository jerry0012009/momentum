#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank77_alt_btc_rs_breadth_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank77_alt_btc_rs_breadth_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank77_alt_btc_rs_breadth_clean_replication.html"
UNIVERSE_CACHE_DIR = ART_DIR / "universe_cache"

BASE_ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
ALT_UNIVERSE = ["ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "LINKUSDT"]
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "breadth_24h_gate", "breadth_8h_gate", "breadth_dual_gate"]
PRIMARY_VARIANT = "breadth_dual_gate"
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
EMA_FAST = 9
EMA_SLOW = 15
BREADTH_THRESHOLD = 0.55
START_BUFFER_BARS = 96

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1160px; margin:40px auto; padding:0 18px; line-height:1.72; color:#111827; background:#f8fafc; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


@dataclass
class Trade:
    asset: str
    setup: str
    variant: str
    timestamp: pd.Timestamp
    side: str
    entry_price: float
    exit_price: float
    bars_held: int
    ret_6bps: float
    ret_10bps: float
    ret_15bps: float
    early_fail: float
    breadth_pos_24h: float
    breadth_neg_24h: float
    breadth_pos_8h: float
    breadth_neg_8h: float


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


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


def load_local_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_binance_klines(symbol: str, start_ms: int, end_ms: int, interval: str = "15m") -> pd.DataFrame:
    ensure_dir(UNIVERSE_CACHE_DIR)
    cache_path = UNIVERSE_CACHE_DIR / f"{symbol}__{start_ms}__{end_ms}__{interval}.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df

    base = "https://api.binance.com/api/v3/klines"
    limit = 1000
    rows: list[list[object]] = []
    cur = start_ms
    step_ms = 15 * 60 * 1000
    while cur < end_ms:
        query = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": cur,
                "endTime": end_ms,
                "limit": limit,
            }
        )
        with urllib.request.urlopen(f"{base}?{query}") as resp:
            batch = json.loads(resp.read().decode("utf-8"))
        if not batch:
            break
        rows.extend(batch)
        last_open = int(batch[-1][0])
        nxt = last_open + step_ms
        if nxt <= cur:
            break
        cur = nxt
        if len(batch) < limit:
            break

    if not rows:
        raise RuntimeError(f"No klines fetched for {symbol}")

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trade_count",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore",
        ],
    )
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    out = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
    out.to_csv(cache_path, index=False)
    return out


def wilder_rma(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(alpha=1.0 / length, adjust=False).mean()


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return wilder_rma(tr, period)


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


def build_breadth_panel(start_ts: pd.Timestamp, end_ts: pd.Timestamp) -> pd.DataFrame:
    start_ms = int(start_ts.timestamp() * 1000)
    end_ms = int(end_ts.timestamp() * 1000)
    btc = fetch_binance_klines("BTCUSDT", start_ms, end_ms)
    panel = btc[["timestamp", "close"]].rename(columns={"close": "btc_close"}).copy()
    for symbol in ALT_UNIVERSE:
        alt = fetch_binance_klines(symbol, start_ms, end_ms)[["timestamp", "close"]].rename(columns={"close": symbol})
        panel = panel.merge(alt, on="timestamp", how="inner")

    btc_ret_24h = panel["btc_close"].pct_change(96)
    btc_ret_8h = panel["btc_close"].pct_change(32)
    pos_24h = []
    neg_24h = []
    pos_8h = []
    neg_8h = []
    for symbol in ALT_UNIVERSE:
        rs24 = panel[symbol].pct_change(96) - btc_ret_24h
        rs8 = panel[symbol].pct_change(32) - btc_ret_8h
        pos_24h.append((rs24 > 0).astype(float))
        neg_24h.append((rs24 < 0).astype(float))
        pos_8h.append((rs8 > 0).astype(float))
        neg_8h.append((rs8 < 0).astype(float))

    panel["breadth_pos_24h"] = pd.concat(pos_24h, axis=1).mean(axis=1)
    panel["breadth_neg_24h"] = pd.concat(neg_24h, axis=1).mean(axis=1)
    panel["breadth_pos_8h"] = pd.concat(pos_8h, axis=1).mean(axis=1)
    panel["breadth_neg_8h"] = pd.concat(neg_8h, axis=1).mean(axis=1)
    panel["alts_count"] = len(ALT_UNIVERSE)
    return panel[["timestamp", "breadth_pos_24h", "breadth_neg_24h", "breadth_pos_8h", "breadth_neg_8h", "alts_count"]]


def build_frame(asset: str, symbol: str, breadth: pd.DataFrame) -> pd.DataFrame:
    df = load_local_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
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
    df["breakout_short_signal"] = (
        low.notna()
        & (df["close"] < low)
        & (df["close"].shift(1) >= low.shift(1))
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df = df.merge(breadth, on="timestamp", how="left")
    return df


def allow_variant(row: pd.Series, setup: str, variant: str) -> bool:
    if variant == "baseline":
        return True
    is_long = setup in LONG_SETUPS
    pos24 = float(row["breadth_pos_24h"])
    neg24 = float(row["breadth_neg_24h"])
    pos8 = float(row["breadth_pos_8h"])
    neg8 = float(row["breadth_neg_8h"])
    if variant == "breadth_24h_gate":
        return pos24 >= BREADTH_THRESHOLD if is_long else neg24 >= BREADTH_THRESHOLD
    if variant == "breadth_8h_gate":
        return pos8 >= BREADTH_THRESHOLD if is_long else neg8 >= BREADTH_THRESHOLD
    if variant == "breadth_dual_gate":
        return (pos24 >= BREADTH_THRESHOLD and pos8 >= 0.50) if is_long else (neg24 >= BREADTH_THRESHOLD and neg8 >= 0.50)
    raise ValueError(variant)


def cost_return(entry: float, exit_: float, side: str, cost_bps: float) -> float:
    gross = (exit_ / entry) - 1.0 if side == "long" else (entry / exit_) - 1.0
    return gross - 2.0 * (cost_bps / 10000.0)


def calc_early_fail(segment: pd.DataFrame, entry: float, side: str) -> float:
    window = segment.iloc[:EARLY_FAIL_BARS]
    if window.empty:
        return np.nan
    if side == "long":
        adverse = (window["low"].min() / entry) - 1.0
        favorable = (window["high"].max() / entry) - 1.0
        return float(abs(adverse) > favorable)
    adverse = (entry / window["high"].max()) - 1.0
    favorable = (entry / window["low"].min()) - 1.0
    return float(abs(adverse) > favorable)


def run_variant(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> list[Trade]:
    signal_col = f"{setup}_signal"
    side = "long" if setup in LONG_SETUPS else "short"
    trades: list[Trade] = []
    i = START_BUFFER_BARS
    n = len(frame)
    while i < n - HOLD_BARS - 1:
        row = frame.iloc[i]
        if not bool(row[signal_col]):
            i += 1
            continue
        if not allow_variant(row, setup, variant):
            i += 1
            continue
        entry_idx = i + 1
        exit_idx = min(entry_idx + HOLD_BARS, n - 1)
        entry_price = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        segment = frame.iloc[entry_idx:exit_idx + 1]
        trades.append(
            Trade(
                asset=asset,
                setup=setup,
                variant=variant,
                timestamp=pd.Timestamp(row["timestamp"]),
                side=side,
                entry_price=entry_price,
                exit_price=exit_price,
                bars_held=exit_idx - entry_idx,
                ret_6bps=cost_return(entry_price, exit_price, side, 6.0),
                ret_10bps=cost_return(entry_price, exit_price, side, 10.0),
                ret_15bps=cost_return(entry_price, exit_price, side, 15.0),
                early_fail=calc_early_fail(segment, entry_price, side),
                breadth_pos_24h=float(row["breadth_pos_24h"]),
                breadth_neg_24h=float(row["breadth_neg_24h"]),
                breadth_pos_8h=float(row["breadth_pos_8h"]),
                breadth_neg_8h=float(row["breadth_neg_8h"]),
            )
        )
        i = exit_idx + 1
    return trades


def trades_df(trades: list[Trade]) -> pd.DataFrame:
    return pd.DataFrame([t.__dict__ for t in trades])


def summarise(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if trades.empty:
        empty = pd.DataFrame()
        return empty, empty, empty, empty

    asset_setup_rows: list[dict[str, object]] = []
    for cost in COSTS:
        ret_col = f"ret_{int(cost)}bps"
        grouped = (
            trades.groupby(["asset", "setup", "variant"], dropna=False)
            .agg(
                total_return=(ret_col, "sum"),
                mean_trade_return=(ret_col, "mean"),
                trades=(ret_col, "size"),
                early_fail_rate=("early_fail", "mean"),
                mean_breadth_pos_24h=("breadth_pos_24h", "mean"),
                mean_breadth_neg_24h=("breadth_neg_24h", "mean"),
                mean_breadth_pos_8h=("breadth_pos_8h", "mean"),
                mean_breadth_neg_8h=("breadth_neg_8h", "mean"),
            )
            .reset_index()
        )
        grouped["cost_bps"] = cost
        asset_setup_rows.append(grouped)
    asset_setup = pd.concat(asset_setup_rows, ignore_index=True)

    overall = (
        asset_setup.groupby(["variant", "cost_bps"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_early_fail_rate=("early_fail_rate", "mean"),
        )
        .reset_index()
        .sort_values(["cost_bps", "variant"])
        .reset_index(drop=True)
    )

    setup_compare = (
        asset_setup.loc[asset_setup["cost_bps"] == PRIMARY_COST]
        .groupby(["setup", "variant"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_early_fail_rate=("early_fail_rate", "mean"),
            mean_breadth_pos_24h=("mean_breadth_pos_24h", "mean"),
            mean_breadth_neg_24h=("mean_breadth_neg_24h", "mean"),
            mean_breadth_pos_8h=("mean_breadth_pos_8h", "mean"),
            mean_breadth_neg_8h=("mean_breadth_neg_8h", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant"])
        .reset_index(drop=True)
    )

    primary = trades.loc[trades["variant"] == PRIMARY_VARIANT].copy()
    if primary.empty:
        time_pocket = pd.DataFrame()
    else:
        primary["time_bucket"] = pd.qcut(primary["timestamp"].rank(method="first"), 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        time_rows: list[dict[str, object]] = []
        for setup, sub in primary.groupby("setup", dropna=False):
            for bucket, pocket in sub.groupby("time_bucket", dropna=False):
                setup_assets = sorted(primary.loc[primary["setup"] == setup, "asset"].unique())
                asset_returns = []
                for asset in setup_assets:
                    asset_ret = pocket.loc[pocket["asset"] == asset, "ret_6bps"].sum()
                    asset_returns.append(asset_ret)
                asset_returns = np.array(asset_returns, dtype=float)
                time_rows.append(
                    {
                        "setup": setup,
                        "time_bucket": str(bucket),
                        "mean_total_return": float(pocket["ret_6bps"].sum() / max(len(setup_assets), 1)),
                        "positive_asset_ratio": float(np.mean(asset_returns > 0)) if len(asset_returns) else np.nan,
                        "mean_trades": float(pocket.groupby("asset").size().mean()),
                    }
                )
        time_pocket = pd.DataFrame(time_rows)

    breadth_snapshot = trades[["timestamp", "breadth_pos_24h", "breadth_neg_24h", "breadth_pos_8h", "breadth_neg_8h"]].drop_duplicates().sort_values("timestamp")
    return asset_setup, overall, setup_compare, time_pocket, breadth_snapshot


def verdict_text(overall: pd.DataFrame, setup_compare: pd.DataFrame) -> str:
    if overall.empty:
        return "park / evidence pool"
    prim = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST)]
    if prim.empty:
        return "park / evidence pool"
    row = prim.iloc[0]
    broad_ok = (
        float(row["mean_total_return"]) > 0
        and float(row["positive_asset_ratio"]) >= 0.67
        and float(row["mean_trades"]) >= 8
        and float(row["mean_early_fail_rate"]) <= 0.5
    )
    per_setup = setup_compare[setup_compare["variant"] == PRIMARY_VARIANT]
    if broad_ok and (per_setup["mean_total_return"] > 0).sum() >= 2:
        return "P1 weak candidate / evidence pool"
    return "park / evidence pool"


def build_html(overall: pd.DataFrame, setup_compare: pd.DataFrame, time_pocket: pd.DataFrame, verdict: str) -> str:
    overall_show = overall.copy()
    setup_show = setup_compare.copy()
    pocket_show = time_pocket.copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8'>
  <title>Rank 77 / alt-vs-BTC RS breadth shared gate</title>
  <style>{CSS}</style>
</head>
<body>
  <h1>Rank 77 / alt-vs-BTC RS breadth shared gate</h1>
  <p class='muted'>最小 clean replication｜120d 15m｜BTC / ETH / SOL setups × alt-vs-BTC breadth gate</p>

  <div class='card'>
    <span class='pill'>Scout Seat</span>
    <span class='pill'>Run 2</span>
    <span class='pill'>Minimal clean replication</span>
    <h2>Hard verdict</h2>
    <p><strong>{escape(verdict)}</strong></p>
    <p>这轮只回答一个问题：把 <code>alt-vs-BTC breadth</code> 当 shared allow/deny gate，能不能在不靠极端砍单的前提下，改善当前三条 archetype（<code>ema_psar_long</code> / <code>fib_retest_long</code> / <code>breakout_short</code>）的成本后读法。</p>
  </div>

  <div class='card'>
    <h2>最小实验口径</h2>
    <ul>
      <li>base setups：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code></li>
      <li>执行冻结：<code>signal bar and prior data only + next-bar open + no-overlap + hold 8 bars</code></li>
      <li>breadth universe：<code>ETH/SOL/XRP/BNB/DOGE/ADA/LINK</code> 相对 <code>BTC</code></li>
      <li>变体：<code>baseline</code>、<code>breadth_24h_gate</code>、<code>breadth_8h_gate</code>、<code>breadth_dual_gate</code></li>
      <li>gate 读法：long setups 要求 <code>breadth_pos</code> 过阈值；short setup 要求 <code>breadth_neg</code> 过阈值</li>
    </ul>
  </div>

  <div class='card'>
    <h2>Overall summary</h2>
    {render_table(overall_show, percent_cols={'mean_total_return','positive_asset_ratio','mean_early_fail_rate'})}
  </div>

  <div class='card'>
    <h2>Setup compare @ 6bps/side</h2>
    {render_table(setup_show, percent_cols={'mean_total_return','positive_asset_ratio','mean_early_fail_rate','mean_breadth_pos_24h','mean_breadth_neg_24h','mean_breadth_pos_8h','mean_breadth_neg_8h'})}
  </div>

  <div class='card'>
    <h2>Time-pocket honesty（primary variant）</h2>
    {render_table(pocket_show, percent_cols={'mean_total_return','positive_asset_ratio'})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    btc = load_local_bars("BTCUSDT", "BTC-USD")
    start_ts = btc["timestamp"].min() - pd.Timedelta(minutes=15 * START_BUFFER_BARS)
    end_ts = btc["timestamp"].max() + pd.Timedelta(minutes=15)
    breadth = build_breadth_panel(start_ts, end_ts)

    all_trades: list[Trade] = []
    for asset, symbol in BASE_ASSETS.items():
        frame = build_frame(asset, symbol, breadth)
        for setup in SETUPS:
            for variant in VARIANTS:
                all_trades.extend(run_variant(frame, asset, setup, variant))

    trades = trades_df(all_trades)
    asset_setup, overall, setup_compare, time_pocket, breadth_snapshot = summarise(trades)
    verdict = verdict_text(overall, setup_compare)

    trades.to_csv(ART_DIR / "trades.csv", index=False)
    asset_setup.to_csv(ART_DIR / "asset_setup_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_compare.to_csv(ART_DIR / "setup_compare.csv", index=False)
    time_pocket.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)
    breadth_snapshot.to_csv(ART_DIR / "breadth_snapshot.csv", index=False)

    html = build_html(overall, setup_compare, time_pocket, verdict)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    READING_PATH.write_text(html, encoding="utf-8")

    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "verdict": verdict,
        "primary_variant": PRIMARY_VARIANT,
        "universe": ALT_UNIVERSE,
        "breadth_threshold": BREADTH_THRESHOLD,
    }
    (ART_DIR / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
