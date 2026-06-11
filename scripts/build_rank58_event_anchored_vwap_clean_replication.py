#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank58_event_anchored_vwap_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank58_event_anchored_vwap_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
VARIANTS = ["base", "session_vwap_gate", "event_avwap_gate", "event_avwap_plus_proximity"]
PRIMARY_VARIANT = "event_avwap_gate"
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
AVWAP_HOLD_LOOKBACK = 3
ANCHOR_LOOKBACK = 12
SESSION_VWAP_TOL = 0.0015


CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px auto; max-width: 1180px; line-height: 1.55; color: #1f2937; padding: 0 16px 40px; }
h1,h2,h3 { color: #111827; }
code { background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }
pre { background: #0f172a; color: #e5e7eb; padding: 12px; border-radius: 8px; overflow-x: auto; }
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


def anchored_vwap(frame: pd.DataFrame, anchor_idx: int, current_idx: int) -> float:
    if anchor_idx > current_idx:
        anchor_idx = current_idx
    tpv = frame["tpv_cum"].iloc[current_idx] - (frame["tpv_cum"].iloc[anchor_idx - 1] if anchor_idx > 0 else 0.0)
    vol = frame["vol_cum"].iloc[current_idx] - (frame["vol_cum"].iloc[anchor_idx - 1] if anchor_idx > 0 else 0.0)
    if not vol:
        return float("nan")
    return float(tpv / vol)


def find_recent_true(series: pd.Series, start: int, end: int) -> int | None:
    lo = max(0, start)
    hi = min(len(series) - 1, end)
    if lo > hi:
        return None
    idx = series.iloc[lo : hi + 1][series.iloc[lo : hi + 1]].index
    if len(idx) == 0:
        return None
    return int(idx[-1])


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3.0
    df["tpv"] = df["typical_price"] * df["volume"]
    df["tpv_cum"] = df["tpv"].cumsum()
    df["vol_cum"] = df["volume"].cumsum()
    df["atr14"] = compute_atr(df)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    session_key = df["timestamp"].dt.floor("1D")
    df["session_cum_vol"] = df.groupby(session_key)["volume"].cumsum()
    df["session_cum_tpv"] = df.groupby(session_key)["tpv"].cumsum()
    df["session_vwap"] = df["session_cum_tpv"] / df["session_cum_vol"].replace(0, np.nan)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["ema_event_trigger"] = (
        (df["close"] > df["ema15"]) & (df["close"].shift(1) <= df["ema15"].shift(1))
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
    df["fib_event_trigger"] = (
        df["fib_618"].notna()
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
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
    df["breakout_event_trigger"] = (
        low.notna() & (df["close"] < low) & (df["close"].shift(1) >= low.shift(1))
    ).fillna(False)
    return df


def signal_direction(setup: str) -> int:
    return -1 if setup == "breakout_short" else 1


def event_anchor_idx(frame: pd.DataFrame, setup: str, signal_idx: int) -> int:
    lo = max(0, signal_idx - ANCHOR_LOOKBACK)
    if setup == "ema_psar_long":
        found = find_recent_true(frame["ema_event_trigger"], lo, signal_idx)
    elif setup == "fib_retest_long":
        found = find_recent_true(frame["fib_event_trigger"], lo, signal_idx)
    else:
        found = find_recent_true(frame["breakout_event_trigger"], lo, signal_idx)
    return int(found if found is not None else signal_idx)


def hold_side_gate(frame: pd.DataFrame, idx: int, gate_col: str, direction: int) -> bool:
    start = max(0, idx - AVWAP_HOLD_LOOKBACK + 1)
    closes = frame.loc[start:idx, "close"].to_numpy(dtype=float)
    gate = frame.loc[start:idx, gate_col].to_numpy(dtype=float)
    valid = np.isfinite(gate)
    if valid.sum() == 0:
        return False
    if direction > 0:
        return int((closes[valid] > gate[valid]).sum()) >= min(2, valid.sum())
    return int((closes[valid] < gate[valid]).sum()) >= min(2, valid.sum())


def build_signal_table(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        direction = signal_direction(setup)
        signal_col = f"{setup}_signal"
        for idx in range(len(frame)):
            if not bool(frame.iloc[idx][signal_col]):
                continue
            anchor_idx = event_anchor_idx(frame, setup, idx)
            avwap = anchored_vwap(frame, anchor_idx, idx)
            session_vwap = float(frame.iloc[idx]["session_vwap"]) if pd.notna(frame.iloc[idx]["session_vwap"]) else np.nan
            atr = float(frame.iloc[idx]["atr14"]) if pd.notna(frame.iloc[idx]["atr14"]) else np.nan
            close = float(frame.iloc[idx]["close"])
            if direction > 0:
                session_gate = close > session_vwap * (1.0 - SESSION_VWAP_TOL) if np.isfinite(session_vwap) else False
                event_gate = close > avwap if np.isfinite(avwap) else False
            else:
                session_gate = close < session_vwap * (1.0 + SESSION_VWAP_TOL) if np.isfinite(session_vwap) else False
                event_gate = close < avwap if np.isfinite(avwap) else False
            hold_event = hold_side_gate(frame.assign(event_avwap=np.nan), idx, "event_avwap", direction) if False else None
            # 用临时列避免多次复制整表
            frame.loc[idx, "_event_avwap_tmp"] = avwap
            hold_event = hold_side_gate(frame, idx, "_event_avwap_tmp", direction) if np.isfinite(avwap) else False
            frame.loc[idx, "_session_vwap_tmp"] = session_vwap
            hold_session = hold_side_gate(frame, idx, "_session_vwap_tmp", direction) if np.isfinite(session_vwap) else False
            proximity = np.isfinite(avwap) and np.isfinite(atr) and abs(close - avwap) <= 0.5 * atr
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "signal_idx": idx,
                    "signal_ts": frame.iloc[idx]["timestamp"],
                    "direction": direction,
                    "anchor_idx": anchor_idx,
                    "anchor_ts": frame.iloc[anchor_idx]["timestamp"],
                    "anchor_type": {
                        "ema_psar_long": "ema15 reclaim trigger",
                        "fib_retest_long": "fib0.618 reclaim trigger",
                        "breakout_short": "rolling-low breakdown trigger",
                    }[setup],
                    "session_vwap": session_vwap,
                    "event_avwap": avwap,
                    "atr14": atr,
                    "base": True,
                    "session_vwap_gate": bool(session_gate and hold_session),
                    "event_avwap_gate": bool(event_gate and hold_event),
                    "event_avwap_plus_proximity": bool(event_gate and hold_event and proximity),
                }
            )
    out = pd.DataFrame(rows)
    if not out.empty:
        out["signal_ts"] = pd.to_datetime(out["signal_ts"], utc=True)
        out["anchor_ts"] = pd.to_datetime(out["anchor_ts"], utc=True)
        out = out.sort_values(["asset", "setup", "signal_ts"]).reset_index(drop=True)
    return out


def false_follow(frame: pd.DataFrame, entry_idx: int, direction: int, guard_level: float) -> int:
    last = min(len(frame) - 1, entry_idx + FALSE_LOOKAHEAD - 1)
    if not np.isfinite(guard_level):
        guard_level = float(frame.iloc[entry_idx - 1]["close"])
    for j in range(entry_idx, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < guard_level:
            return 1
        if direction < 0 and close > guard_level:
            return 1
    return 0


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    direction = signal_direction(setup)
    cost_rate = float(cost_bps) / 10000.0
    setup_signals = signals[(signals["setup"] == setup) & (signals[variant])].copy()
    rows: list[dict[str, object]] = []
    signal_events = int(len(setup_signals))
    last_exit = -1
    for _, sig in setup_signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit or idx + 1 >= len(frame):
            continue
        entry_idx = idx + 1
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross = (exit_px / entry_px - 1.0) * direction
        net = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        if variant.startswith("event_avwap"):
            guard_level = float(sig["event_avwap"]) if pd.notna(sig["event_avwap"]) else np.nan
        elif variant == "session_vwap_gate":
            guard_level = float(sig["session_vwap"]) if pd.notna(sig["session_vwap"]) else np.nan
        else:
            guard_level = float(frame.iloc[idx]["close"])
        rows.append(
            {
                "asset": sig["asset"],
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(sig["signal_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "anchor_ts": pd.to_datetime(sig["anchor_ts"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "anchor_type": sig["anchor_type"],
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "short" if direction < 0 else "long",
                "entry_price": entry_px,
                "exit_price": exit_px,
                "session_vwap": float(sig["session_vwap"]) if pd.notna(sig["session_vwap"]) else np.nan,
                "event_avwap": float(sig["event_avwap"]) if pd.notna(sig["event_avwap"]) else np.nan,
                "gross_ret": gross,
                "net_ret": net,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_follow_4bars": int(false_follow(frame, entry_idx, direction, guard_level)),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_slice(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trades": 0,
            "trade_count_retention": np.nan,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "win_rate": np.nan,
            "false_follow_4bars_rate": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trades": int(len(trades)),
        "trade_count_retention": np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_follow_4bars_rate": float(trades["false_follow_4bars"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for cost in sorted(out["cost_bps_per_side"].unique()):
        base_map = (
            out[(out["variant"] == "base") & (out["cost_bps_per_side"] == cost)]
            .set_index(["asset", "setup"])["trades"]
            .to_dict()
        )
        mask = out["cost_bps_per_side"] == cost
        out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
            lambda r: (r["trades"] / base_map.get((r["asset"], r["setup"]), np.nan)) if base_map.get((r["asset"], r["setup"]), 0) else np.nan,
            axis=1,
        )
    return out


def build_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (variant, cost), part in asset_df.groupby(["variant", "cost_bps_per_side"], dropna=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(part["total_return"].mean()),
                "positive_asset_ratio": float((part["total_return"] > 0).mean()),
                "mean_trades": float(part["trades"].mean()),
                "mean_trade_count_retention": float(part["trade_count_retention"].dropna().mean()) if part["trade_count_retention"].notna().any() else np.nan,
                "mean_false_follow_4bars_rate": float(part["false_follow_4bars_rate"].dropna().mean()) if part["false_follow_4bars_rate"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant"]).reset_index(drop=True)


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
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
    for (variant, bucket_name, asset, setup), part in df.groupby(["variant", "bucket", "asset", "setup"], dropna=False):
        rows.append(
            {
                "variant": variant,
                "bucket": bucket_name,
                "asset": asset,
                "setup": setup,
                "total_return": float((1.0 + part["net_ret"]).prod() - 1.0),
                "trades": int(len(part)),
            }
        )
    tmp = pd.DataFrame(rows)
    return (
        tmp.groupby(["variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "bucket"])
        .reset_index(drop=True)
    )


def build_anchor_mix(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame(columns=["setup", "anchor_type", "signals", "gate_pass_rate"])
    rows = []
    for (setup, anchor_type), part in signals.groupby(["setup", "anchor_type"], dropna=False):
        rows.append(
            {
                "setup": setup,
                "anchor_type": anchor_type,
                "signals": int(len(part)),
                "event_gate_pass_rate": float(part["event_avwap_gate"].mean()),
                "event_plus_proximity_pass_rate": float(part["event_avwap_plus_proximity"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "anchor_type"]).reset_index(drop=True)


def build_verdict(overall: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    session = overall[(overall["variant"] == "session_vwap_gate") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用结果，不值得继续占默认 fast lane。"
    p = primary.iloc[0]
    s = session.iloc[0] if not session.empty else None
    mean_ret = float(p["mean_total_return"]) if not pd.isna(p["mean_total_return"]) else -1.0
    pos_ratio = float(p["positive_asset_ratio"]) if not pd.isna(p["positive_asset_ratio"]) else 0.0
    mean_trades = float(p["mean_trades"]) if not pd.isna(p["mean_trades"]) else 0.0
    retention = float(p["mean_trade_count_retention"]) if not pd.isna(p["mean_trade_count_retention"]) else 0.0
    false_rate = float(p["mean_false_follow_4bars_rate"]) if not pd.isna(p["mean_false_follow_4bars_rate"]) else 1.0
    session_ret = float(s["mean_total_return"]) if s is not None and not pd.isna(s["mean_total_return"]) else -1.0
    if mean_ret > 0 and pos_ratio >= 0.5 and mean_trades >= 4 and retention >= 0.25 and false_rate <= 0.5 and mean_ret >= session_ret:
        return "P1 weak candidate / evidence pool", "最小 clean replication 至少说明 event anchor 不是纯切样本：成本后转正，跨 setup/资产不只剩单腿，且不比 session VWAP 更差。"
    return "park / evidence pool", "最小 clean replication 没把它推到候选池：event AVWAP 仍主要表现为切样本执行层，成本后收益/跨资产稳定性/false follow-through 还不够诚实。"


def write_html(report_path: Path, title: str, body: str) -> None:
    report_path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def update_todo(verdict: str, note: str, overall: pd.DataFrame, time_pockets: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker missing in TODO.md")
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    s = overall[(overall["variant"] == "session_vwap_gate") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    tp = time_pockets[time_pockets["variant"] == PRIMARY_VARIANT]
    if tp.empty:
        tp_text = "time-pocket 暂无可用样本。"
    else:
        tp_bits = [
            f"{row.bucket}≈{pct(row.mean_total_return)} / {pct(row.positive_asset_ratio)}"
            for row in tp.itertuples()
        ]
        tp_text = "；".join(tp_bits)
    block = (
        f"> **最新补充（{ts}）**：这轮先按 `Run 1` 重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane；因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。随后按权威顺序执行 **`Run 2 / Rank 58 minimal clean replication`**：固定复用 `BTC/ETH/SOL 120d 15m` cache，只在三条最小 archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`session_vwap_gate`、`event_avwap_gate`、`event_avwap_gate+0.5ATR proximity` 四臂，统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`。\n"
        f">  - 6bps/side 下，主读法 `event_avwap_gate` 的跨切片结果为：`mean_total_return≈{pct(p['mean_total_return'])}`、`positive_asset_ratio≈{pct(p['positive_asset_ratio'])}`、`mean_trades≈{num(p['mean_trades'])}`、`mean_trade_count_retention≈{pct(p['mean_trade_count_retention'])}`、`mean_false_follow_4bars_rate≈{pct(p['mean_false_follow_4bars_rate'])}`；对照 `session_vwap_gate≈{pct(s['mean_total_return'])} / retention≈{pct(s['mean_trade_count_retention'])}`。\n"
        f">  - time-pocket：{tp_text}。\n"
        f">  - 当前更诚实的 hard verdict：**`Rank 58 / event-anchored VWAP hold-reclaim spine = {verdict}`**。{note}\n"
        f">  - reader-facing 落点：`reports/site/factors/scout_rank58_event_anchored_vwap_15m/report.html`、`reports/site/reading/repo_scout/rank58_event_anchored_vwap_clean_replication.html`；artifact：`reports/artifacts/scout_rank58_event_anchored_vwap_15m/overall_summary.csv`。\n"
        f">  - 排班含义：当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 58 已给出 {verdict} 后退出 fast-lane，则按 7.10 重新认领 1 条 fresh paper/repo based 5m/15m crypto source（优先 continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source）` -> `Run 3 = 只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。\n\n"
    )
    text = text.replace(marker, marker + "\n" + block, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    signal_tables: list[pd.DataFrame] = []
    trades_all: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        signals = build_signal_table(frame, asset)
        signal_tables.append(signals)
        for setup in SETUPS:
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, signal_events = build_trades(frame, signals, setup, variant, cost)
                    if not trades.empty:
                        trades_all.append(trades)
                    asset_rows.append(
                        summarize_slice(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=signal_events)
                    )

    signals_df = pd.concat(signal_tables, ignore_index=True) if signal_tables else pd.DataFrame()
    trades_df = pd.concat(trades_all, ignore_index=True) if trades_all else pd.DataFrame()
    asset_df = add_trade_retention(pd.DataFrame(asset_rows))
    overall_df = build_overall(asset_df)
    time_pockets_df = build_time_pockets(trades_df)
    anchor_mix_df = build_anchor_mix(signals_df)
    verdict, verdict_note = build_verdict(overall_df)

    signals_out = signals_df.copy()
    if not signals_out.empty:
        signals_out["signal_ts"] = signals_out["signal_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        signals_out["anchor_ts"] = signals_out["anchor_ts"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    signals_out.to_csv(ART_DIR / "signal_snapshot.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_setup_summary.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_pockets_df.to_csv(ART_DIR / "time_pockets.csv", index=False)
    anchor_mix_df.to_csv(ART_DIR / "anchor_mix_summary.csv", index=False)
    trades_df.to_csv(ART_DIR / "trades.csv", index=False)

    primary = overall_df[(overall_df["variant"] == PRIMARY_VARIANT) & (overall_df["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    session = overall_df[(overall_df["variant"] == "session_vwap_gate") & (overall_df["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]

    summary_card = f"""
<h1>Rank 58 / event-anchored VWAP hold-reclaim spine — 最小 clean replication</h1>
<p class='muted'>生成时间：{escape(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))}</p>
<div class='card'>
  <p><strong>结论：</strong><span class='{ 'good' if 'P1' in verdict else 'bad' }'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p>主读法 <code>event_avwap_gate</code> @ 6bps：mean_total_return={escape(pct(primary['mean_total_return']))}；positive_asset_ratio={escape(pct(primary['positive_asset_ratio']))}；mean_trades={escape(num(primary['mean_trades']))}；trade_count_retention={escape(pct(primary['mean_trade_count_retention']))}；false_follow_4bars={escape(pct(primary['mean_false_follow_4bars_rate']))}。</p>
  <p>对照 <code>session_vwap_gate</code>：mean_total_return={escape(pct(session['mean_total_return']))}；trade_count_retention={escape(pct(session['mean_trade_count_retention']))}；false_follow_4bars={escape(pct(session['mean_false_follow_4bars_rate']))}。</p>
</div>
"""

    method = """
<div class='card'>
  <h2>本轮冻结口径</h2>
  <ul>
    <li>只复用 <code>BTC/ETH/SOL 120d 15m</code> 本地 cache，不追新 bar。</li>
    <li>只比较三条最小 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li>四臂固定为：<code>base</code>、<code>session_vwap_gate</code>、<code>event_avwap_gate</code>、<code>event_avwap_gate+0.5ATR proximity</code>。</li>
    <li>所有执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</li>
    <li>event anchor 类型提前冻结：<code>ema15 reclaim trigger</code>、<code>fib0.618 reclaim trigger</code>、<code>rolling-low breakdown trigger</code>；不允许事后挑最好看的锚点。</li>
  </ul>
</div>
"""

    report_body = summary_card + method + "<h2>Overall summary</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_false_follow_4bars_rate"},
        digits_cols={"mean_trades": 2, "cost_bps_per_side": 0},
    )
    report_body += "<h2>Asset/setup summary</h2>" + render_table(
        asset_df,
        percent_cols={"trade_count_retention", "total_return", "avg_net_ret", "win_rate", "false_follow_4bars_rate"},
        digits_cols={"trades": 0, "signal_events": 0, "cost_bps_per_side": 0},
    )
    report_body += "<h2>Time pockets</h2>" + render_table(
        time_pockets_df,
        percent_cols={"mean_total_return", "positive_asset_ratio"},
        digits_cols={"mean_trades": 2},
    )
    report_body += "<h2>Anchor mix</h2>" + render_table(
        anchor_mix_df,
        percent_cols={"event_gate_pass_rate", "event_plus_proximity_pass_rate"},
        digits_cols={"signals": 0},
    )
    write_html(SITE_DIR / "report.html", "Rank 58 clean replication", report_body)

    reading_body = summary_card + "<h2>为什么这轮是 hard verdict</h2><p>这轮不是继续 intake，也不是写近义说明页；它只回答一个问题：把 session 锚点换成预先冻结的 event anchor 之后，event AVWAP 能不能在不过度砍样本的前提下，比 session VWAP 更诚实地改善三条现有 archetype 的 post-cost / hold 质量。</p>"
    reading_body += "<h2>结果表</h2>" + render_table(
        overall_df,
        percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_false_follow_4bars_rate"},
        digits_cols={"mean_trades": 2, "cost_bps_per_side": 0},
    )
    reading_body += f"<p><strong>最终口径：</strong>{escape(verdict)}。{escape(verdict_note)}</p>"
    write_html(READING_DIR / "rank58_event_anchored_vwap_clean_replication.html", "Rank 58 clean replication", reading_body)

    update_todo(verdict, verdict_note, overall_df, time_pockets_df)


if __name__ == "__main__":
    main()
