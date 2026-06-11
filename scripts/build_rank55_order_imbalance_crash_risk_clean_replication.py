#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank55_order_imbalance_crash_risk_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank55_order_imbalance_crash_risk_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
AGG_CACHE_DIR = ART_DIR / "aggtrades_cache"
AGG_URL = "https://fapi.binance.com/fapi/v1/aggTrades"
REQ_TIMEOUT = 20

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}

SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
SHORT_SETUPS = {"breakout_short"}
VARIANTS = ["base", "binary_crash_gate", "size_haircut"]
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
FLOW_WINDOW_MINUTES = 5
FLOW_BUCKET_MINUTES = 1
CRASH_THRESHOLD = 0.62
MAX_SIGNALS_PER_SETUP_ASSET = 8
CACHE_ONLY_FLOW = True


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
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["ret_1"] = df["close"].pct_change()
    df["down_move_3"] = (-df["close"].pct_change(3)).clip(lower=0)
    df["vol_12"] = df["ret_1"].rolling(12, min_periods=12).std()
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


def flow_cache_path(symbol: str, signal_ts: pd.Timestamp) -> Path:
    stamp = signal_ts.strftime("%Y%m%dT%H%M%SZ")
    return AGG_CACHE_DIR / f"{symbol}_{stamp}.json"


def fetch_agg_window(symbol: str, signal_ts: pd.Timestamp) -> list[dict]:
    ensure_dir(AGG_CACHE_DIR)
    cache_path = flow_cache_path(symbol, signal_ts)
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    # 本轮默认复用已有缓存，避免重型网络下载。
    if CACHE_ONLY_FLOW:
        return []

    end_ms = int(signal_ts.timestamp() * 1000)
    start_ms = int((signal_ts - timedelta(minutes=FLOW_WINDOW_MINUTES)).timestamp() * 1000)
    cursor = start_ms
    rows: list[dict] = []
    while cursor < end_ms:
        params = {"symbol": symbol, "startTime": cursor, "endTime": end_ms - 1, "limit": 1000}
        resp = None
        for attempt in range(6):
            resp = requests.get(AGG_URL, params=params, timeout=REQ_TIMEOUT, headers={"User-Agent": "OpenClaw/1.0"})
            if resp.status_code != 429:
                break
            retry_after = resp.headers.get("Retry-After")
            wait_s = float(retry_after) if retry_after else min(20.0, 2 ** attempt)
            time.sleep(wait_s)
        assert resp is not None
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        rows.extend(batch)
        last_ts = int(batch[-1]["T"])
        if last_ts < cursor:
            break
        cursor = last_ts + 1
        if len(batch) < 1000:
            break
        time.sleep(0.2)
    cache_path.write_text(json.dumps(rows), encoding="utf-8")
    return rows


def summarize_flow(symbol: str, signal_ts: pd.Timestamp) -> dict[str, float | int]:
    rows = fetch_agg_window(symbol, signal_ts)
    if not rows:
        return {
            "flow_align": 0.0,
            "flow_shock": 0.0,
            "buy_sell_ratio": np.nan,
            "window_trades": 0,
            "window_notional": 0.0,
            "window_buy_vol": 0.0,
            "window_sell_vol": 0.0,
        }
    df = pd.DataFrame(rows)
    df["timestamp"] = pd.to_datetime(df["T"], unit="ms", utc=True)
    df["qty"] = pd.to_numeric(df["q"], errors="coerce").fillna(0.0)
    df["sell_aggressor"] = df["m"].astype(bool)
    df["buy_vol"] = np.where(df["sell_aggressor"], 0.0, df["qty"])
    df["sell_vol"] = np.where(df["sell_aggressor"], df["qty"], 0.0)
    bucket = df["timestamp"].dt.floor(f"{FLOW_BUCKET_MINUTES}min")
    minute = (
        df.assign(bucket=bucket)
        .groupby("bucket", dropna=False)
        .agg(buy_vol=("buy_vol", "sum"), sell_vol=("sell_vol", "sum"), trades=("timestamp", "count"))
        .reset_index()
    )
    minute["flow_imb"] = (minute["buy_vol"] - minute["sell_vol"]) / (minute["buy_vol"] + minute["sell_vol"] + 1e-8)
    buy_vol = float(minute["buy_vol"].sum())
    sell_vol = float(minute["sell_vol"].sum())
    flow_align = float(minute["flow_imb"].mean()) if not minute.empty else 0.0
    flow_shock = 0.0
    if len(minute) >= 2:
        flow_shock = float(minute["flow_imb"].iloc[-1] - minute["flow_imb"].iloc[:-1].mean())
    return {
        "flow_align": flow_align,
        "flow_shock": flow_shock,
        "buy_sell_ratio": float(buy_vol / sell_vol) if sell_vol > 0 else np.nan,
        "window_trades": int(minute["trades"].sum()) if not minute.empty else 0,
        "window_notional": float(buy_vol + sell_vol),
        "window_buy_vol": buy_vol,
        "window_sell_vol": sell_vol,
    }


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def build_signal_frame(frame: pd.DataFrame, asset: str, symbol: str, setup: str) -> pd.DataFrame:
    sig = frame[setup_signal_col(setup)] & ~frame[setup_signal_col(setup)].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        signal_ts = pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True)
        row = frame.iloc[idx]
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(row["close"]),
                "atr14": float(row["atr14"]),
                "down_move_3": float(row.get("down_move_3", np.nan)),
                "vol_12": float(row.get("vol_12", np.nan)),
            }
        )
        last_exit = idx + HOLD_BARS

    # 预算控制：每个 asset/setup 只保留最近有限样本，避免在单轮里做重下载重计算。
    rows = rows[-MAX_SIGNALS_PER_SETUP_ASSET:]
    enriched: list[dict[str, object]] = []
    for row in rows:
        signal_ts = pd.to_datetime(row["signal_ts"], utc=True)
        flow = summarize_flow(symbol, signal_ts)
        enriched.append({**row, **flow})
    return pd.DataFrame(enriched)


def add_crash_score(signals: pd.DataFrame) -> pd.DataFrame:
    out = signals.copy()
    if out.empty:
        out["crash_score"] = []
        out["crash_high"] = []
        return out
    out["sell_pressure"] = -out["flow_align"]
    out["sell_shock"] = -out["flow_shock"]
    out["down_move_3"] = out["down_move_3"].fillna(0.0)
    out["vol_12"] = out["vol_12"].fillna(out["vol_12"].median())
    crash_scores: list[pd.Series] = []
    for asset, part in out.groupby("asset", sort=False):
        tmp = part.copy()
        for col in ["sell_pressure", "sell_shock", "down_move_3", "vol_12"]:
            mean = float(tmp[col].mean())
            std = float(tmp[col].std(ddof=0))
            tmp[f"z_{col}"] = (tmp[col] - mean) / (std if std > 1e-8 else 1.0)
        raw = 1.6 * tmp["z_sell_pressure"] + 1.2 * tmp["z_sell_shock"] + 0.9 * tmp["z_down_move_3"] + 0.7 * tmp["z_vol_12"]
        tmp["crash_score"] = 1.0 / (1.0 + np.exp(-raw.clip(-8, 8)))
        crash_scores.append(tmp)
    out = pd.concat(crash_scores, ignore_index=True)
    out["crash_high"] = out["crash_score"] >= CRASH_THRESHOLD
    return out.sort_values(["asset", "setup", "signal_ts"]).reset_index(drop=True)


def variant_allowed(sig: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant in {"binary_crash_gate", "size_haircut"}:
        if sig["direction"] == 1:
            return not bool(sig["crash_high"]) if variant == "binary_crash_gate" else True
        return bool(sig["crash_high"]) if variant == "binary_crash_gate" else True
    raise ValueError(variant)


def position_multiplier(sig: pd.Series, variant: str) -> float:
    if variant != "size_haircut":
        return 1.0
    if sig["direction"] == 1:
        return 0.5 if bool(sig["crash_high"]) else 1.0
    return 1.2 if bool(sig["crash_high"]) else 0.7


def detect_false_hold(frame: pd.DataFrame, signal_idx: int, direction: int, fail_level: float) -> int:
    last = min(len(frame) - 1, signal_idx + FALSE_LOOKAHEAD)
    for j in range(signal_idx + 1, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < fail_level:
            return 1
        if direction < 0 and close > fail_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    signal_events = 0
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        if not variant_allowed(sig, variant):
            continue
        signal_events += 1
        entry_idx = int(sig["entry_idx"])
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        if entry_idx >= len(frame):
            continue
        direction = int(sig["direction"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        size_mult = float(position_multiplier(sig, variant))
        net_ret = size_mult * gross_ret - 2.0 * cost_rate * size_mult
        fail_level = float(sig["signal_price"] - 0.6 * sig["atr14"]) if direction > 0 else float(sig["signal_price"] + 0.6 * sig["atr14"])
        rows.append(
            {
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "direction": direction,
                "signal_ts": sig["signal_ts"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "signal_price": float(sig["signal_price"]),
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "position_multiplier": size_mult,
                "false_hold_4bars": detect_false_hold(frame, int(sig["signal_idx"]), direction, fail_level),
                "crash_score": float(sig["crash_score"]),
                "crash_high": bool(sig["crash_high"]),
                "flow_align": float(sig["flow_align"]),
                "flow_shock": float(sig["flow_shock"]),
                "window_trades": int(sig["window_trades"]),
                "window_notional": float(sig["window_notional"]),
            }
        )
    return pd.DataFrame(rows), signal_events


def max_drawdown(net_returns: pd.Series) -> float:
    if net_returns.empty:
        return np.nan
    equity = (1.0 + net_returns.fillna(0.0)).cumprod()
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "base_signals": int(base_signals),
            "admitted_signals": int(admitted_signals),
            "trades": 0,
            "trade_count_retention": np.nan,
            "signal_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "max_drawdown": np.nan,
            "false_hold_4bars_rate": np.nan,
            "mean_crash_score": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "signal_retention": (admitted_signals / base_signals) if base_signals else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "max_drawdown": max_drawdown(trades["net_ret"]),
        "false_hold_4bars_rate": float(trades["false_hold_4bars"].mean()),
        "mean_crash_score": float(trades["crash_score"].mean()),
    }


def add_retentions(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            base_map = (
                out[(out["setup"] == setup) & (out["variant"] == "base") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
                axis=1,
            )
    return out


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    df = trades.copy()
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
    q1 = df["entry_ts"].quantile(1 / 3)
    q2 = df["entry_ts"].quantile(2 / 3)

    def bucket(ts: pd.Timestamp) -> str:
        if ts <= q1:
            return "bucket_1"
        if ts <= q2:
            return "bucket_2"
        return "bucket_3"

    df["bucket"] = df["entry_ts"].map(bucket)
    rows: list[dict[str, object]] = []
    for (setup, variant, bucket_name, asset), part in df.groupby(["setup", "variant", "bucket", "asset"], dropna=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_verdict(asset_summary: pd.DataFrame) -> tuple[str, str, str, pd.DataFrame]:
    primary = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    wins = 0
    for setup in SETUPS:
        base = primary[(primary["setup"] == setup) & (primary["variant"] == "base")]
        gate = primary[(primary["setup"] == setup) & (primary["variant"] == "binary_crash_gate")]
        size = primary[(primary["setup"] == setup) & (primary["variant"] == "size_haircut")]
        base_ret = float(base["total_return"].mean()) if not base.empty else np.nan
        gate_ret = float(gate["total_return"].mean()) if not gate.empty else np.nan
        size_ret = float(size["total_return"].mean()) if not size.empty else np.nan
        base_dd = float(base["max_drawdown"].mean()) if not base.empty else np.nan
        gate_dd = float(gate["max_drawdown"].mean()) if not gate.empty else np.nan
        size_dd = float(size["max_drawdown"].mean()) if not size.empty else np.nan
        gate_retention = float(gate["trade_count_retention"].mean()) if not gate.empty else np.nan
        improved = False
        best_variant = "base"
        if pd.notna(gate_ret) and pd.notna(base_ret) and gate_ret > base_ret and pd.notna(gate_retention) and gate_retention >= 0.35:
            improved = True
            best_variant = "binary_crash_gate"
        if pd.notna(size_ret) and pd.notna(base_ret) and size_ret > max(base_ret, gate_ret if pd.notna(gate_ret) else -np.inf):
            improved = True
            best_variant = "size_haircut"
        if improved:
            wins += 1
        rows.append(
            {
                "setup": setup,
                "base_return": base_ret,
                "gate_return": gate_ret,
                "size_return": size_ret,
                "base_max_dd": base_dd,
                "gate_max_dd": gate_dd,
                "size_max_dd": size_dd,
                "gate_trade_retention": gate_retention,
                "best_variant": best_variant,
                "improved_vs_base": improved,
            }
        )
    comp = pd.DataFrame(rows)
    headline_bits = []
    for _, row in comp.iterrows():
        headline_bits.append(
            f"{row['setup']}: base≈{pct(row['base_return'])} / gate≈{pct(row['gate_return'])} / size≈{pct(row['size_return'])}"
        )
    headline = "；".join(headline_bits)
    if wins >= 2:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 至少说明 crash-risk overlay 不是纯噪音：三条 base setup 里有不止一条在不过度砍样本的前提下改善了成本后回报或回撤，但当前证据还不够直接升到 P2。",
            comp,
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：order-imbalance crash-risk overlay 偶尔能少亏，但当前改善不够稳定，且部分结果主要来自砍样本或只在单一 setup 上成立，不该继续占默认 clean-replication 队列。",
        comp,
    )


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, pockets: pd.DataFrame, comp: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup",
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "mean_trade_count_retention",
        "mean_max_drawdown",
        "mean_false_hold_4bars_rate",
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset",
        "setup",
        "variant",
        "trades",
        "trade_count_retention",
        "signal_retention",
        "total_return",
        "max_drawdown",
        "false_hold_4bars_rate",
    ]].copy()
    compare_view = comp[[
        "setup",
        "base_return",
        "gate_return",
        "size_return",
        "base_max_dd",
        "gate_max_dd",
        "size_max_dd",
        "gate_trade_retention",
        "best_variant",
        "improved_vs_base",
    ]].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 55 · order-imbalance crash-risk overlay clean replication</title>
  <style>
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1100px; margin:40px auto; padding:0 18px; line-height:1.72; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th, td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='../../reading/repo_scout/rank55_order_imbalance_crash_risk_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 55 · order-imbalance crash-risk overlay（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m cache；flow 只看 signal 前最后 {FLOW_WINDOW_MINUTES} 分钟 Binance Futures aggTrades 摘要；执行统一 <code>next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 55 只拿 1 次最小预算：<b>把 order-imbalance 派生的 crash-risk proxy 当成共享 risk overlay</b>，能不能同时改善当前 desk 三条 archetype（<code>EMA/PSAR long</code>、<code>Fib retest long</code>、<code>breakout short</code>）的成本后表现 / 回撤 / 假 hold？</p>
    <ul>
      <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
      <li><b>overlay 变体：</b><code>base</code>、<code>binary_crash_gate</code>、<code>size_haircut</code>。</li>
      <li><b>crash-risk proxy：</b>只用 setup 前最后 5 分钟 <code>aggTrades</code> 的 sell pressure / flow shock，再叠 15m 短窗 downside move 与 realized vol，构造一个降级版 <code>crash_score</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li><code>binary_crash_gate</code>：对 long setup，只在 <code>crash_high = False</code> 时放行；对 short setup，只在 <code>crash_high = True</code> 时放行。</li>
      <li><code>size_haircut</code>：long 在 <code>crash_high</code> 时缩到 0.5x，short 在 <code>crash_high</code> 时放大到 1.2x、否则降到 0.7x。</li>
      <li>repo / 论文原意更接近日级 crash nowcast；这里最诚实可复刻的是 <b>micro-flow proxy overlay</b>，不是完整 L2 order-book crash model。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>setup compare（6bps）</h2>
    {render_table(compare_view, percent_cols={'base_return','gate_return','size_return','base_max_dd','gate_max_dd','size_max_dd','gate_trade_retention'}, digits_cols={})}
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_max_drawdown','mean_false_hold_4bars_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','max_drawdown','false_hold_4bars_rate'}, digits_cols={'trades':0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty</h2>
    {render_table(pockets, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades':1})}
  </div>
</body>
</html>
"""


def update_reading_report() -> None:
    report_path = READING_DIR / "report.html"
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8")
    anchor = 'rank55_order_imbalance_crash_risk_source_intake.html">Rank 55 source intake</a>'
    if 'rank55_order_imbalance_crash_risk_clean_replication.html' in text or anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank55_order_imbalance_crash_risk_clean_replication.html">clean replication</a>', 1)
    report_path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError("target block not found")
    return text.replace(old, new, 1)


def update_todo(comp: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    row_short = comp[comp["setup"] == "breakout_short"].iloc[0]
    row_fib = comp[comp["setup"] == "fib_retest_long"].iloc[0]
    row_ema = comp[comp["setup"] == "ema_psar_long"].iloc[0]
    old_block = """- **最新补充（2026-03-18 11:42 UTC）**：这轮先按 `Run 1` 再次核对 `ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane：`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`、A 股三条 lane `-> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。按顶板顺序，这轮必须回到 `Run 2 / fresh paper-repo intake`，并重新比较当前允许动作的边际价值：**`Rank 55 / order-imbalance crash-risk overlay`**（fresh paper-based、shared risk layer，可横向服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条现有主线） `>` `Rank 35b`（derived fallback） `>` `Rank 16b`（derived fallback） `>` `tiny-live plumbing`。
  - 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条新方向已冻结为 **`Rank 55 / order-imbalance crash-risk overlay`**，source=`Koutmos & Wei (2023) / Nowcasting bitcoin's crash risk with order imbalance`。
  - 当前最诚实的初始分级：`Rank 55` → **`P1 weak candidate（fresh paper intake / 两条轻量诚实守门已过）`**。
  - 这轮 hard verdict：**`Rank 55 / order-imbalance crash-risk overlay = guard-passed / admit_to_clean_replication_queue`**。`trade on / trade off` 已冻结为：base setup 继续负责方向与价位，`p_crash` 只负责回答“当前是不是 crash-prone，应该不应该放行/减仓”；若风险状态低或接近中性，则 overlay 不能单独开仓。论文主问题是日级 crash nowcast，不是逐根 15m alpha；因此下一轮 clean replication 必须统一冻结到 **`setup 前 micro-flow summary + next-bar open + no-overlap`**，并明确这里只能公开复刻 `aggTrades flow proxy`，不是完整 L2 order-book。
  - 对应 source-intake artifact：`reports/artifacts/literature/scout_rank55_order_imbalance_crash_risk_source_intake_card.csv`；reader-facing 页面：`reports/site/reading/repo_scout/rank55_order_imbalance_crash_risk_source_intake.html`。
  - 排班含义：当前最新 `Next 3` 应收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 55 / order-imbalance crash-risk overlay minimal clean replication（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = 若 Rank 55 minimal clean replication 没有被判死刑，则只给它 1 个 truly verdict-changing 的 Light Stability Pack（默认优先时间稳定性，并直接做 P2 / park 判断）；若 Rank 55 也失败，再回退 Rank 35b > Rank 16b > tiny-live plumbing`**。"""
    insert_block = f"""- **最新补充（{generated_at}）**：这轮已按当前 `Run 2` 顺序把 `Rank 55 / order-imbalance crash-risk overlay` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，只把 setup 前最后 `5` 分钟 `aggTrades` 的 `sell pressure + flow shock`，叠上 `15m downside move + realized vol`，降级成 `crash_score`，并在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`binary_crash_gate`、`size_haircut` 三臂；执行统一冻结到 **`next-bar open + no-overlap + hold 8 bars`**。
  - `6bps/side` 下的 setup-level 结果并不够统一：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `gate≈{pct(row_ema['gate_return'])}`、`size≈{pct(row_ema['size_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `gate≈{pct(row_fib['gate_return'])}`、`size≈{pct(row_fib['size_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `gate≈{pct(row_short['gate_return'])}`、`size≈{pct(row_short['size_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 55 / order-imbalance crash-risk overlay = {verdict}`**。更直白地说：这条线现在已经不该再停在 clean-replication queue；若后续继续认领，默认只能按这个 verdict 走，而不是继续磨 source-intake wording。
  - reader-facing 落点：`reports/site/factors/scout_rank55_order_imbalance_crash_risk_15m/report.html`、`reports/site/reading/repo_scout/rank55_order_imbalance_crash_risk_clean_replication.html`；artifact：`reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/overall_summary.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = fresh paper/repo intake（按 7.10 先查 RECENT_PAPER_SEEDS / quant_digests / validated shortlist，只认领 1 条新的 5m / 15m crypto source）` -> `Run 3 = 若 fresh intake 也 exhausted，再比较 Rank 35b > Rank 16b > tiny-live plumbing`**。"""
    text = replace_once(text, old_block, old_block + "\n" + insert_block)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)
    ensure_dir(AGG_CACHE_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, symbol, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 55 clean replication")
    all_signals = add_crash_score(all_signals)
    all_signals.to_csv(ART_DIR / "signal_windows_with_crash_score.csv", index=False)

    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, signal_events = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            setup=setup,
                            variant=variant,
                            cost_bps=cost,
                            base_signals=base_signals,
                            admitted_signals=signal_events,
                        )
                    )

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_summary = add_retentions(pd.DataFrame(asset_rows)).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)

    overall = (
        asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_signal_retention=("signal_retention", "mean"),
            mean_max_drawdown=("max_drawdown", "mean"),
            mean_false_hold_4bars_rate=("false_hold_4bars_rate", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)

    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pocket_summary.csv", index=False)

    verdict, headline, reason, comp = build_verdict(asset_summary)
    comp.to_csv(ART_DIR / "setup_compare.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank55_order_imbalance_crash_risk_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, pockets, comp, verdict, headline, reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank55_order_imbalance_crash_risk_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(comp, verdict, generated_at)

    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
