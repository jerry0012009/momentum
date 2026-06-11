#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank69_ivu_opening_volume_uncertainty_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank69_ivu_opening_volume_uncertainty_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank69_ivu_opening_volume_uncertainty_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "ivu_allow_q476", "ivu_allow_q40", "ivu_size_haircut_q40"]
PRIMARY_VARIANT = "ivu_allow_q40"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
TARGET_BARS = 12
STOP_ATR = 0.75
TARGET_ATR = 1.0
ROLLING_SESSIONS = 60
SESSION_ANCHOR_HOUR = 0
Q476 = 0.476225
Q40 = 0.40

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }
.card { border: 1px solid #e5e7eb; border-radius: 14px; background: white; padding: 18px 20px; margin: 16px 0; }
.pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }
.muted { color:#6b7280; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


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


def add_base_setup_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema9"] = out["close"].ewm(span=9, adjust=False).mean()
    out["ema15"] = out["close"].ewm(span=15, adjust=False).mean()
    out["ema_slope"] = out["ema9"].pct_change(3)
    out["vol_ma20"] = out["volume"].rolling(20, min_periods=20).mean()
    out["atr14"] = compute_atr(out)
    out["psar"] = compute_psar(out)
    out["rolling_low20"] = out["low"].rolling(20, min_periods=20).min().shift(1)
    out["swing_high_30"] = out["high"].rolling(30, min_periods=30).max().shift(1)
    out["swing_low_30"] = out["low"].rolling(30, min_periods=30).min().shift(1)
    rng = out["swing_high_30"] - out["swing_low_30"]
    out["fib_618"] = out["swing_high_30"] - 0.618 * rng
    out["fib_50"] = out["swing_high_30"] - 0.5 * rng
    out["ema_psar_long_signal"] = (
        (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0.0003)
        & (out["psar"] < out["close"])
        & (out["close"] > out["high"].shift(1))
        & (out["close"].shift(1) < out["ema9"].shift(1))
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    out["fib_retest_long_signal"] = (
        out["fib_618"].notna()
        & (out["ema9"] > out["ema15"])
        & (out["ema_slope"] > 0)
        & (out["close"] > out["fib_618"])
        & (out["close"].shift(1) <= out["fib_618"].shift(1))
        & (out["low"] <= out["fib_618"] + 0.2 * out["atr14"])
        & (out["close"] > out["fib_50"])
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    low = out["rolling_low20"]
    atr = out["atr14"]
    out["breakout_short_signal"] = (
        low.notna()
        & (out["ema9"] < out["ema15"])
        & (out["ema_slope"] < -0.0003)
        & (out["close"].shift(1) > low.shift(1))
        & (out["close"].shift(2) > low.shift(2))
        & (out["close"] < low - 0.1 * atr)
        & (out["high"] <= low + 0.3 * atr)
        & (out["volume"] > out["vol_ma20"])
    ).fillna(False)
    return out


def add_ivu_session_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    ts = out["timestamp"]
    out["session_anchor"] = ts.dt.floor("1D") + pd.to_timedelta(SESSION_ANCHOR_HOUR, unit="h")
    out.loc[ts < out["session_anchor"], "session_anchor"] -= pd.Timedelta(days=1)
    out["session_bar_index"] = ((ts - out["session_anchor"]) / pd.Timedelta(minutes=15)).astype(int)
    out["session_bar1_volume"] = out.groupby("session_anchor")["volume"].transform("first")
    out["session_first7_volume"] = out.groupby("session_anchor")["volume"].transform(lambda s: s.iloc[:7].sum())
    out["session_ivu"] = out["session_bar1_volume"] / out["session_first7_volume"].replace(0, np.nan)
    session_df = (
        out.groupby("session_anchor", as_index=False)
        .agg(session_bar1_volume_ref=("session_bar1_volume", "first"), session_ivu_ref=("session_ivu", "first"))
        .sort_values("session_anchor")
        .reset_index(drop=True)
    )
    session_df["open_vol_median_60"] = session_df["session_bar1_volume_ref"].rolling(ROLLING_SESSIONS, min_periods=20).median().shift(1)
    session_df["ivu_q40_60"] = session_df["session_ivu_ref"].rolling(ROLLING_SESSIONS, min_periods=20).quantile(Q40).shift(1)
    out = out.merge(session_df[["session_anchor", "open_vol_median_60", "ivu_q40_60"]], on="session_anchor", how="left")
    out["ivu_known"] = (out["session_bar_index"] >= 7) & out["session_ivu"].notna()
    out["open_vol_high"] = (out["session_bar1_volume"] > out["open_vol_median_60"]).fillna(False)
    out["ivu_allow_q476"] = (out["ivu_known"] & out["open_vol_high"] & (out["session_ivu"] < Q476)).fillna(False)
    out["ivu_allow_q40"] = (out["ivu_known"] & out["open_vol_high"] & (out["session_ivu"] < out["ivu_q40_60"])) .fillna(False)
    return out


def build_signal_frame(df: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    signal_col = f"{setup}_signal"
    sig_idx = np.flatnonzero(df[signal_col].to_numpy())
    rows: list[dict[str, object]] = []
    for idx in sig_idx:
        if idx < 30 or idx + 1 >= len(df):
            continue
        row = df.iloc[idx]
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "direction": "long" if setup in LONG_SETUPS else "short",
                "signal_index": int(idx),
                "timestamp": row["timestamp"],
                "signal_close": float(row["close"]),
                "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else np.nan,
                "session_anchor": row["session_anchor"],
                "session_bar_index": int(row["session_bar_index"]),
                "session_ivu": float(row["session_ivu"]) if pd.notna(row["session_ivu"]) else np.nan,
                "session_bar1_volume": float(row["session_bar1_volume"]) if pd.notna(row["session_bar1_volume"]) else np.nan,
                "session_first7_volume": float(row["session_first7_volume"]) if pd.notna(row["session_first7_volume"]) else np.nan,
                "open_vol_median_60": float(row["open_vol_median_60"]) if pd.notna(row["open_vol_median_60"]) else np.nan,
                "ivu_q40_60": float(row["ivu_q40_60"]) if pd.notna(row["ivu_q40_60"]) else np.nan,
                "open_vol_high": bool(row["open_vol_high"]),
                "ivu_known": bool(row["ivu_known"]),
                "ivu_allow_q476": bool(row["ivu_allow_q476"]),
                "ivu_allow_q40": bool(row["ivu_allow_q40"]),
            }
        )
    return pd.DataFrame(rows)


def variant_weight(sig: pd.Series, variant: str) -> tuple[bool, float, bool]:
    if variant == "base":
        return True, 1.0, True
    if variant == "ivu_allow_q476":
        allow = bool(sig["ivu_allow_q476"])
        return allow, 1.0, allow
    if variant == "ivu_allow_q40":
        allow = bool(sig["ivu_allow_q40"])
        return allow, 1.0, allow
    if variant == "ivu_size_haircut_q40":
        allow = bool(sig["ivu_allow_q40"])
        if not bool(sig["ivu_known"]):
            return False, 0.0, False
        return True, 1.0 if allow else 0.5, allow
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, sigs: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int, int]:
    rows: list[dict[str, object]] = []
    admitted = 0
    allow_count = 0
    active_until: pd.Timestamp | None = None
    cost_rate = float(cost_bps) / 10000.0

    for _, sig in sigs.iterrows():
        admitted_flag, size_weight, allow_flag = variant_weight(sig, variant)
        if not admitted_flag:
            continue
        admitted += 1
        if allow_flag:
            allow_count += 1
        signal_idx = int(sig["signal_index"])
        entry_idx = signal_idx + 1
        if entry_idx >= len(frame):
            continue
        entry_ts = pd.Timestamp(frame.iloc[entry_idx]["timestamp"])
        if active_until is not None and entry_ts <= active_until:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        path_end_idx = min(len(frame) - 1, entry_idx + TARGET_BARS - 1)
        if exit_idx <= entry_idx:
            continue

        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        direction = 1.0 if sig["direction"] == "long" else -1.0
        gross_ret_raw = direction * ((exit_px / entry_px) - 1.0)
        gross_ret = gross_ret_raw * size_weight
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate * size_weight) * (1.0 - cost_rate * size_weight) - 1.0

        atr = float(sig["atr14"]) if pd.notna(sig["atr14"]) else np.nan
        target_px = np.nan
        stop_px = np.nan
        target_hit = np.nan
        failure_before_target = np.nan
        future = frame.iloc[entry_idx : path_end_idx + 1].copy()
        if pd.notna(atr) and atr > 0:
            if sig["direction"] == "long":
                target_px = entry_px + TARGET_ATR * atr
                stop_px = entry_px - STOP_ATR * atr
                target_hits = future.index[future["high"] >= target_px].tolist()
                fail_hits = future.index[future["low"] <= stop_px].tolist()
            else:
                target_px = entry_px - TARGET_ATR * atr
                stop_px = entry_px + STOP_ATR * atr
                target_hits = future.index[future["low"] <= target_px].tolist()
                fail_hits = future.index[future["high"] >= stop_px].tolist()
            first_target = target_hits[0] if target_hits else None
            first_fail = fail_hits[0] if fail_hits else None
            target_hit = bool(first_target is not None)
            failure_before_target = bool(first_fail is not None and (first_target is None or first_fail <= first_target))

        rows.append(
            {
                "asset": sig["asset"],
                "setup": sig["setup"],
                "variant": variant,
                "signal_time": sig["timestamp"],
                "entry_time": entry_ts,
                "exit_time": pd.Timestamp(frame.iloc[exit_idx]["timestamp"]),
                "direction": sig["direction"],
                "cost_bps_per_side": float(cost_bps),
                "size_weight": float(size_weight),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_return": gross_ret,
                "net_return": net_ret,
                "session_bar_index": sig["session_bar_index"],
                "session_ivu": sig["session_ivu"],
                "open_vol_high": sig["open_vol_high"],
                "ivu_known": sig["ivu_known"],
                "ivu_allow_q476": sig["ivu_allow_q476"],
                "ivu_allow_q40": sig["ivu_allow_q40"],
                "target_hit_12bars": target_hit,
                "failure_before_target": failure_before_target,
            }
        )
        active_until = pd.Timestamp(frame.iloc[exit_idx]["timestamp"])

    return pd.DataFrame(rows), admitted, allow_count


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int, allow_count: int, base_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trade_retention = np.nan
    if base_trades is not None and len(base_trades) > 0:
        trade_retention = float(len(trades) / len(base_trades))
    total_return = float((1.0 + trades["net_return"]).prod() - 1.0) if not trades.empty else np.nan
    avg_net = float(trades["net_return"].mean()) if not trades.empty else np.nan
    fail_rate = float(trades["failure_before_target"].mean()) if not trades.empty and trades["failure_before_target"].notna().any() else np.nan
    target_rate = float(trades["target_hit_12bars"].mean()) if not trades.empty and trades["target_hit_12bars"].notna().any() else np.nan
    positive_window_ratio = np.nan
    if not trades.empty:
        tmp = trades.copy()
        if len(tmp) >= 3:
            ranks = np.linspace(0, 3, len(tmp), endpoint=False)
            tmp["time_bucket"] = pd.cut(ranks, bins=[0, 1, 2, 3], labels=["bucket_1", "bucket_2", "bucket_3"], include_lowest=True)
        else:
            tmp["time_bucket"] = [f"bucket_{i+1}" for i in range(len(tmp))]
        positive_window_ratio = float(tmp.groupby("time_bucket", observed=False)["net_return"].sum().gt(0).mean()) if tmp["time_bucket"].notna().any() else np.nan
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "allow_signals": int(allow_count),
        "trades": int(len(trades)),
        "signal_retention": float(admitted_signals / base_signals) if base_signals else np.nan,
        "trade_count_retention": trade_retention,
        "allow_ratio": float(allow_count / admitted_signals) if admitted_signals else np.nan,
        "total_return": total_return,
        "avg_net_ret": avg_net,
        "win_rate": float((trades["net_return"] > 0).mean()) if not trades.empty else np.nan,
        "failure_before_target_rate": fail_rate,
        "target_hit_12bars_rate": target_rate,
        "positive_window_ratio": positive_window_ratio,
        "mean_size_weight": float(trades["size_weight"].mean()) if not trades.empty else np.nan,
        "mean_session_ivu": float(trades["session_ivu"].mean()) if not trades.empty else np.nan,
    }


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "mean_total_return": float(grp["total_return"].mean()) if not grp.empty else np.nan,
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()) if not grp.empty else np.nan,
                "mean_trades": float(grp["trades"].mean()) if not grp.empty else np.nan,
                "mean_signal_retention": float(grp["signal_retention"].mean()) if not grp.empty else np.nan,
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if not grp.empty else np.nan,
                "mean_allow_ratio": float(grp["allow_ratio"].mean()) if not grp.empty else np.nan,
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()) if not grp.empty else np.nan,
                "mean_failure_before_target_rate": float(grp["failure_before_target_rate"].mean()) if not grp.empty else np.nan,
                "mean_target_hit_12bars_rate": float(grp["target_hit_12bars_rate"].mean()) if not grp.empty else np.nan,
                "mean_positive_window_ratio": float(grp["positive_window_ratio"].mean()) if not grp.empty else np.nan,
                "mean_size_weight": float(grp["mean_size_weight"].mean()) if not grp.empty else np.nan,
            }
        )
    return pd.DataFrame(rows).sort_values(["setup", "cost_bps_per_side", "variant"]).reset_index(drop=True)


def build_time_stability(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_failure_before_target_rate"])
    work = trades.copy().sort_values("entry_time").reset_index(drop=True)
    work["bucket"] = pd.qcut(np.arange(len(work)), 3, labels=["bucket_1", "bucket_2", "bucket_3"], duplicates="drop")
    tmp = (
        work.groupby(["setup", "variant", "bucket", "asset"], dropna=False)
        .agg(total_return=("net_return", lambda s: float((1.0 + s).prod() - 1.0)), trades=("net_return", "size"), failure_before_target_rate=("failure_before_target", "mean"))
        .reset_index()
    )
    return (
        tmp.groupby(["setup", "variant", "bucket"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_failure_before_target_rate=("failure_before_target_rate", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "bucket"])
        .reset_index(drop=True)
    )


def build_parameter_summary(frames: dict[str, pd.DataFrame], all_signals: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    param_grid = [
        ("allow_q476", "ivu_allow_q476"),
        ("allow_q40", "ivu_allow_q40"),
        ("size_haircut_q40", "ivu_size_haircut_q40"),
    ]
    for label, variant in param_grid:
        asset_rows: list[dict[str, object]] = []
        for asset in ASSETS:
            frame = frames[asset]
            for setup in SETUPS:
                sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
                if sigs.empty:
                    continue
                base_trades, _, _ = build_trades(frame, sigs, "base", PRIMARY_COST)
                trades, admitted, allow_count = build_trades(frame, sigs, variant, PRIMARY_COST)
                asset_rows.append(
                    summarize_asset(
                        trades,
                        asset=asset,
                        setup=setup,
                        variant=label,
                        cost_bps=PRIMARY_COST,
                        base_signals=int(len(sigs)),
                        admitted_signals=int(admitted),
                        allow_count=int(allow_count),
                        base_trades=base_trades,
                    )
                )
        if asset_rows:
            agg = pd.DataFrame(asset_rows).groupby("variant", dropna=False).agg(
                mean_total_return=("total_return", "mean"),
                positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
                mean_trades=("trades", "mean"),
                mean_trade_count_retention=("trade_count_retention", "mean"),
                mean_allow_ratio=("allow_ratio", "mean"),
                mean_failure_before_target_rate=("failure_before_target_rate", "mean"),
                mean_target_hit_12bars_rate=("target_hit_12bars_rate", "mean"),
            ).reset_index()
            rows.extend(agg.to_dict("records"))
    return pd.DataFrame(rows)


def build_cost_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    primary = asset_summary[asset_summary["variant"] == PRIMARY_VARIANT].copy()
    return (
        primary.groupby("cost_bps_per_side", dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_allow_ratio=("allow_ratio", "mean"),
            mean_failure_before_target_rate=("failure_before_target_rate", "mean"),
            mean_target_hit_12bars_rate=("target_hit_12bars_rate", "mean"),
            mean_positive_window_ratio=("positive_window_ratio", "mean"),
        )
        .reset_index()
        .sort_values("cost_bps_per_side")
        .reset_index(drop=True)
    )


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    target = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        subset = target[target["setup"] == setup].set_index("variant")
        if "base" not in subset.index:
            continue
        base = subset.loc["base"]
        q476 = subset.loc["ivu_allow_q476"] if "ivu_allow_q476" in subset.index else pd.Series(dtype=float)
        q40 = subset.loc["ivu_allow_q40"] if "ivu_allow_q40" in subset.index else pd.Series(dtype=float)
        size = subset.loc["ivu_size_haircut_q40"] if "ivu_size_haircut_q40" in subset.index else pd.Series(dtype=float)
        rows.append(
            {
                "setup": setup,
                "base_return": base.get("mean_total_return"),
                "q476_return": q476.get("mean_total_return"),
                "q40_return": q40.get("mean_total_return"),
                "size_return": size.get("mean_total_return"),
                "base_retention": base.get("mean_trade_count_retention"),
                "q40_retention": q40.get("mean_trade_count_retention"),
                "size_retention": size.get("mean_trade_count_retention"),
                "base_failure": base.get("mean_failure_before_target_rate"),
                "q40_failure": q40.get("mean_failure_before_target_rate"),
                "size_failure": size.get("mean_failure_before_target_rate"),
                "base_target12": base.get("mean_target_hit_12bars_rate"),
                "q40_target12": q40.get("mean_target_hit_12bars_rate"),
                "size_target12": size.get("mean_target_hit_12bars_rate"),
                "q40_positive_asset_ratio": q40.get("positive_asset_ratio"),
                "q40_allow_ratio": q40.get("mean_allow_ratio"),
            }
        )
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame, params: pd.DataFrame, cost_df: pd.DataFrame) -> tuple[str, str, str]:
    if compare.empty:
        return (
            "park / evidence pool",
            "暂无可比结果。",
            "这轮最小 clean replication 连 setup compare 都没形成，不该继续占 Scout 预算。",
        )
    wins = 0
    strong_wins = 0
    for _, row in compare.iterrows():
        improved = (
            pd.notna(row.get("q40_return"))
            and pd.notna(row.get("base_return"))
            and pd.notna(row.get("q40_retention"))
            and float(row["q40_retention"]) >= 0.35
            and pd.notna(row.get("q40_allow_ratio"))
            and float(row["q40_allow_ratio"]) >= 0.25
            and (
                float(row["q40_return"]) > float(row["base_return"]) + 0.002
                or (
                    pd.notna(row.get("q40_failure"))
                    and pd.notna(row.get("base_failure"))
                    and float(row["q40_failure"]) < float(row["base_failure"]) - 0.03
                )
                or (
                    pd.notna(row.get("q40_target12"))
                    and pd.notna(row.get("base_target12"))
                    and float(row["q40_target12"]) > float(row["base_target12"]) + 0.03
                )
            )
        )
        if improved:
            wins += 1
            if float(row.get("q40_positive_asset_ratio", 0.0) or 0.0) >= (2 / 3):
                strong_wins += 1
    stable_params = False
    if not params.empty:
        stable_slice = params[
            (params["mean_trade_count_retention"] >= 0.30)
            & (params["mean_allow_ratio"] >= 0.25)
            & (params["positive_asset_ratio"] >= (1 / 3))
        ]
        stable_params = len(stable_slice) >= 2
    cost_survives = False
    if not cost_df.empty:
        c10 = cost_df[cost_df["cost_bps_per_side"] == 10.0]
        cost_survives = not c10.empty and float(c10.iloc[0]["mean_total_return"]) > 0
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r.get('base_return'))} / q476≈{pct(r.get('q476_return'))} / q40≈{pct(r.get('q40_return'))} / size≈{pct(r.get('size_return'))}"
        for _, r in compare.iterrows()
    )
    if wins >= 2 and strong_wins >= 1 and stable_params and cost_survives:
        return (
            "P2 paper candidate / admission queue",
            headline,
            "这次最小 clean replication 说明 IVU 作为 shared continuation gate 已不只是砍样本换胜率：至少两条 archetype 上同时改善了收益/失效率/target-hit 的其中一项，参数邻域没一碰就碎，10bps 也还活着，因此值得先升到 paper candidate pool。",
        )
    if wins >= 1 and stable_params:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 说明 IVU gate 在部分 archetype 上有 shared continuation filter 的味道，但改善还不够统一，或成本生存/跨资产还不够硬；更诚实的读法仍是先留在 P1 证据池。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：把股票论文里的 IVU 开盘量不确定性硬搬到 crypto 15m 后，目前主要效果还是砍单，收益/失效率/target-hit 的改善不够统一，不该继续占默认 Scout 主资源位。",
    )


def render_factor_page(overall: pd.DataFrame, asset_summary: pd.DataFrame, compare: pd.DataFrame, time_df: pd.DataFrame, params: pd.DataFrame, cost_df: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup", "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_count_retention", "mean_allow_ratio", "mean_avg_net_ret", "mean_failure_before_target_rate",
        "mean_target_hit_12bars_rate", "mean_positive_window_ratio", "mean_size_weight"
    ]].copy()
    asset_view = asset_summary[(asset_summary["cost_bps_per_side"] == PRIMARY_COST) & (asset_summary["variant"] == PRIMARY_VARIANT)][[
        "asset", "setup", "trades", "trade_count_retention", "allow_ratio", "total_return", "avg_net_ret",
        "failure_before_target_rate", "target_hit_12bars_rate", "positive_window_ratio", "mean_size_weight"
    ]].copy()
    compare_view = compare[[
        "setup", "base_return", "q476_return", "q40_return", "size_return", "base_retention", "q40_retention",
        "size_retention", "base_failure", "q40_failure", "size_failure", "base_target12", "q40_target12", "size_target12", "q40_allow_ratio"
    ]].copy()
    time_view = time_df[(time_df["variant"] == PRIMARY_VARIANT)][["setup", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_failure_before_target_rate"]].copy() if not time_df.empty else pd.DataFrame()
    return f"""
<p><a href='../../reading/repo_scout/rank69_ivu_opening_volume_uncertainty_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 69 · IVU opening-volume uncertainty gate（minimal clean replication）</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m 本地 cache；执行统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>；session anchor 固定 <code>00:00 UTC</code>，IVU 只用 anchor 后前 7 根已完成 15m bar。</p>

<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <p>当 <code>EMA = waiting_not_due</code> 时，Rank 69 只拿 1 次最小预算：<b>把 <code>高开盘量 + 低 IVU</code> 当作 shared continuation allow/deny gate</b>，对当前三条 archetype（<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>）到底是能改善成本后质量，还是只是靠砍单看起来更好？</p>
  <ul>
    <li><b>四臂：</b><code>base</code>、<code>ivu_allow_q476</code>、<code>ivu_allow_q40</code>、<code>ivu_size_haircut_q40</code>。</li>
    <li><b>trade on：</b><code>open_vol_high &amp; IVU low</code> 时放行；<code>size_haircut</code> 臂在不满足放行时保留半仓，用来回答它更像硬 veto 还是软降仓。</li>
    <li><b>最小诚实边界：</b>不引入论文里的 ML 分类器，不用未来 session 量分布，不调 session anchor，不改单独 entry/exit。</li>
  </ul>
</div>

<div class='card'>
  <h2>硬结论</h2>
  <p><span class='pill'>{escape(verdict)}</span></p>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>

<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','q476_return','q40_return','size_return','base_retention','q40_retention','size_retention','base_failure','q40_failure','size_failure','base_target12','q40_target12','size_target12','q40_allow_ratio'})}
</div>

<div class='card'>
  <h2>overall summary</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_allow_ratio','mean_avg_net_ret','mean_failure_before_target_rate','mean_target_hit_12bars_rate','mean_positive_window_ratio'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1,'mean_size_weight':2})}
</div>

<div class='card'>
  <h2>cross-asset stability（主变体 q40）</h2>
  {render_table(asset_view, percent_cols={'trade_count_retention','allow_ratio','total_return','avg_net_ret','failure_before_target_rate','target_hit_12bars_rate','positive_window_ratio'}, digits_cols={'trades':0,'mean_size_weight':2})}
</div>

<div class='card'>
  <h2>time stability（主变体 q40）</h2>
  {render_table(time_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_failure_before_target_rate'}, digits_cols={'mean_trades':1})}
</div>

<div class='card'>
  <h2>parameter stability</h2>
  {render_table(params, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_allow_ratio','mean_failure_before_target_rate','mean_target_hit_12bars_rate'}, digits_cols={'mean_trades':1})}
</div>

<div class='card'>
  <h2>cost / trade-count stability（主变体 q40）</h2>
  {render_table(cost_df, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_allow_ratio','mean_failure_before_target_rate','mean_target_hit_12bars_rate','mean_positive_window_ratio'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
</div>
"""


def render_reading_page(compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    compare_view = compare[[
        "setup", "base_return", "q476_return", "q40_return", "size_return", "base_retention", "q40_retention", "size_retention",
        "base_failure", "q40_failure", "size_failure", "base_target12", "q40_target12", "size_target12", "q40_allow_ratio"
    ]].copy()
    return f"""
<p><a href='rank69_ivu_opening_volume_uncertainty_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 69 · IVU opening-volume uncertainty gate clean replication</h1>
<div class='card'>
  <span class='pill'>更新时间：{escape(generated_at)}</span>
  <span class='pill'>类型：minimal clean replication</span>
  <span class='pill'>当前 verdict：{escape(verdict)}</span>
  <p class='muted'>artifact：<code>reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/overall_summary.csv</code></p>
</div>
<div class='card'>
  <h2>一句话结果</h2>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>
<div class='card'>
  <h2>这轮冻结的最小实验</h2>
  <ul>
    <li><code>BTC/ETH/SOL</code>，只复用 120d 15m 本地 cache，不追新 bar，不做重下载。</li>
    <li>固定 session anchor 为 <code>00:00 UTC</code>；IVU = <code>vol_bar1 / sum(vol_bar1..bar7)</code>，只在第 7 根 15m 收完之后才允许 gate 生效。</li>
    <li>只比较四臂：<code>base</code>、<code>ivu_allow_q476</code>、<code>ivu_allow_q40</code>、<code>ivu_size_haircut_q40</code>。</li>
    <li>首轮只看：<code>post-cost return</code>、<code>trade count retention</code>、<code>failure-before-target</code>、<code>target-hit within 12 bars</code>、<code>positive-window-ratio</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','q476_return','q40_return','size_return','base_retention','q40_retention','size_retention','base_failure','q40_failure','size_failure','base_target12','q40_target12','size_target12','q40_allow_ratio'})}
</div>
"""


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "\n### Next 3 bot3 runs（当前默认执行顺序）"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    if f"**最新补充（{generated_at}）**" in text:
        return
    compare = compare.set_index("setup")
    row_ema = compare.loc["ema_psar_long"]
    row_fib = compare.loc["fib_retest_long"]
    row_short = compare.loc["breakout_short"]
    insert_block = f"""
- **最新补充（{generated_at}）**：这轮再次先核对 `Run 1 / EMA due-check` 与当前 `P3 continuity` 状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`。因此这轮合法主动作仍是 **`Run 2 / Rank 69 minimal clean replication`**，而不是继续磨 `P3 continuity`。
  - 这轮已把 `Rank 69 / IVU opening-volume uncertainty gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`ivu_allow_q476`、`ivu_allow_q40`、`ivu_size_haircut_q40` 四臂；执行统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**，session anchor 固定 `00:00 UTC`，IVU 只用 anchor 后前 `7` 根已完成 `15m` bar。
  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `q476≈{pct(row_ema['q476_return'])}`、`q40≈{pct(row_ema['q40_return'])}`、`size≈{pct(row_ema['size_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `q476≈{pct(row_fib['q476_return'])}`、`q40≈{pct(row_fib['q40_return'])}`、`size≈{pct(row_fib['size_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `q476≈{pct(row_short['q476_return'])}`、`q40≈{pct(row_short['q40_return'])}`、`size≈{pct(row_short['size_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 69 / IVU opening-volume uncertainty gate = {verdict}`**。
  - reader-facing 落点：`reports/site/factors/scout_rank69_ivu_opening_volume_uncertainty_15m/report.html`、`reports/site/reading/repo_scout/rank69_ivu_opening_volume_uncertainty_clean_replication.html`；artifact：`reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/overall_summary.csv`、`setup_compare.csv`。
  - 这轮 verdict 已消耗掉 Rank 69 允许的那次 minimal clean replication。按 desk 顺序，当前更诚实的 active Scout 顺序应更新为：**fresh source intake（优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source） > Rank 35b > Rank 16b > tiny-live plumbing**。
  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 69 verdict 不足以升到下一层，则按 7.10 继续认领 1 条新的 5m / 15m crypto fresh source` -> `Run 3 = 若新的 fresh source 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。
"""
    text = text.replace(marker, "\n" + insert_block + marker, 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames: dict[str, pd.DataFrame] = {}
    signal_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        frame = add_ivu_session_features(add_base_setup_signals(load_bars(symbol, asset)))
        frames[asset] = frame
        for setup in SETUPS:
            sigs = build_signal_frame(frame, asset, setup)
            if not sigs.empty:
                signal_frames.append(sigs)

    all_signals = pd.concat(signal_frames, ignore_index=True) if signal_frames else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 69 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    for asset in ASSETS:
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            if sigs.empty:
                continue
            base_trades, _, _ = build_trades(frame, sigs, "base", PRIMARY_COST)
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, admitted, allow_count = build_trades(frame, sigs, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            setup=setup,
                            variant=variant,
                            cost_bps=cost,
                            base_signals=int(len(sigs)),
                            admitted_signals=int(admitted),
                            allow_count=int(allow_count),
                            base_trades=base_trades if cost == PRIMARY_COST else None,
                        )
                    )

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)

    asset_summary = pd.DataFrame(asset_rows).sort_values(["setup", "variant", "cost_bps_per_side", "asset"]).reset_index(drop=True)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall = build_overall(asset_summary)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    time_df = build_time_stability(all_trades)
    time_df.to_csv(ART_DIR / "time_stability.csv", index=False)
    params = build_parameter_summary(frames, all_signals)
    params.to_csv(ART_DIR / "parameter_stability.csv", index=False)
    cost_df = build_cost_summary(asset_summary)
    cost_df.to_csv(ART_DIR / "cost_trade_stability.csv", index=False)
    setup_compare = build_setup_compare(overall)
    setup_compare.to_csv(ART_DIR / "setup_compare.csv", index=False)

    verdict, headline, reason = build_verdict(setup_compare, params, cost_df)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    meta = pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank69_ivu_opening_volume_uncertainty_gate",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    factor_body = render_factor_page(overall, asset_summary, setup_compare, time_df, params, cost_df, verdict, headline, reason, generated_at)
    write_html(SITE_DIR / "report.html", "Rank 69 · IVU opening-volume uncertainty clean replication", factor_body)
    reading_body = render_reading_page(setup_compare, verdict, headline, reason, generated_at)
    write_html(READING_PATH, "Rank 69 · IVU opening-volume uncertainty clean replication", reading_body)
    update_todo(setup_compare, verdict, generated_at)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"headline={headline}")


if __name__ == "__main__":
    main()
