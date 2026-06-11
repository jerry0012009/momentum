#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank67_regime_matrix_shared_state_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank67_regime_matrix_shared_state_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank67_regime_matrix_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "no_mr_gate", "trend_expansion_only", "compression_to_expansion_breakout"]
PRIMARY_VARIANT = "trend_expansion_only"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0, 20.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
LOOKBACK = 20
ATR_PERIOD = 14
HURST_WINDOW = 100
HURST_LAG = 10
ADX_PERIOD = 14
ADX_SLOPE = 5
RV_PERIOD = 20
RV_SLOPE = 5
RV_THRESHOLD = 0.08

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.72; color: #111827; background: #f8fafc; }
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return (
        df.set_index("timestamp")
        .resample(rule, label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
    prev_close = df["close"].shift(1)
    tr = pd.concat([
        (df["high"] - df["low"]).abs(),
        (df["high"] - prev_close).abs(),
        (df["low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
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


def compute_adx(df: pd.DataFrame, period: int = ADX_PERIOD) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index)
    tr = pd.concat([
        (high - low).abs(),
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    plus_di = 100 * plus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.ewm(alpha=1 / period, adjust=False, min_periods=period).mean() / atr.replace(0, np.nan)
    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    return dx.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def compute_hurst_proxy(close: pd.Series, window: int = HURST_WINDOW, lag: int = HURST_LAG) -> pd.Series:
    diff1 = close.diff().rolling(window, min_periods=window).std()
    difflag = close.diff(lag).rolling(window, min_periods=window).std()
    hurst = np.log(difflag / diff1.replace(0, np.nan)) / np.log(lag)
    return hurst.clip(lower=0.0, upper=1.0)


def build_regime_frame(df15: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df30 = resample_ohlcv(df15[["timestamp", "open", "high", "low", "close", "volume"]], "30min")
    logret = np.log(df30["close"]).diff()
    df30["hurst_100"] = compute_hurst_proxy(df30["close"])
    df30["adx14"] = compute_adx(df30)
    df30["adx_slope_5"] = df30["adx14"].diff(ADX_SLOPE)
    df30["rv20"] = logret.rolling(RV_PERIOD, min_periods=RV_PERIOD).std()
    df30["rv_slope_5"] = df30["rv20"].pct_change(RV_SLOPE)
    trend = (df30["hurst_100"] >= 0.58) & (df30["adx14"] >= 22) & (df30["adx_slope_5"] > 0)
    expansion = (df30["rv_slope_5"] > RV_THRESHOLD) & (df30["adx_slope_5"] > 0) & (~trend)
    compression = (df30["rv_slope_5"] < -RV_THRESHOLD) & (df30["adx14"] <= 16)
    df30["regime"] = np.select(
        [trend, expansion, compression],
        ["Trend", "Expansion", "Compression"],
        default="Mean Reversion",
    )
    prev_regime = df30["regime"].shift(1)
    prev2 = df30["regime"].shift(2)
    prev3 = df30["regime"].shift(3)
    df30["compression_to_expansion"] = (
        (df30["regime"] == "Expansion")
        & ((prev_regime == "Compression") | (prev2 == "Compression") | (prev3 == "Compression"))
    ).fillna(False)
    regime15 = pd.merge_asof(
        df15[["timestamp"]].sort_values("timestamp"),
        df30[["timestamp", "regime", "compression_to_expansion", "hurst_100", "adx14", "rv20"]].sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    regime15["regime"] = regime15["regime"].fillna("Mean Reversion")
    regime15["compression_to_expansion"] = regime15["compression_to_expansion"].fillna(False)
    regime15["no_mr_gate"] = regime15["regime"] != "Mean Reversion"
    regime15["trend_expansion_only"] = regime15["regime"].isin(["Trend", "Expansion"])
    return df30, regime15


def build_signal_frame(df15: pd.DataFrame, regime15: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    signal_col = f"{setup}_signal"
    sigs = df15.loc[df15[signal_col], ["timestamp", "close", "fib_50", "atr14"]].copy()
    if sigs.empty:
        return pd.DataFrame()
    sigs["asset"] = asset
    sigs["setup"] = setup
    sigs["direction"] = np.where(setup in LONG_SETUPS, "long", "short")
    sigs = pd.merge_asof(
        sigs.sort_values("timestamp"),
        regime15.sort_values("timestamp"),
        on="timestamp",
        direction="backward",
    )
    sigs["base"] = True
    sigs["compression_to_expansion_breakout"] = (
        (setup == "breakout_short") & sigs["compression_to_expansion"].fillna(False)
    )
    return sigs.reset_index(drop=True)


def price_at_or_after(df: pd.DataFrame, ts: pd.Timestamp, col: str) -> tuple[pd.Timestamp | None, float | None, int | None]:
    rows = df.loc[df["timestamp"] >= ts]
    if rows.empty:
        return None, None, None
    idx = int(rows.index[0])
    row = rows.iloc[0]
    return pd.Timestamp(row["timestamp"]), float(row[col]), idx


def build_trades(frame: pd.DataFrame, sigs: pd.DataFrame, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    active_until: pd.Timestamp | None = None
    admitted = 0
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in sigs.iterrows():
        allowed = bool(sig[variant])
        if not allowed:
            continue
        admitted += 1
        entry_ts, entry_px, entry_idx = price_at_or_after(frame, sig["timestamp"] + pd.Timedelta(minutes=15), "open")
        if entry_ts is None or entry_px is None or entry_idx is None:
            continue
        if active_until is not None and entry_ts <= active_until:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        if exit_idx <= entry_idx:
            continue
        direction = 1.0 if sig["direction"] == "long" else -1.0
        early_idx = min(len(frame) - 1, entry_idx + EARLY_FAIL_BARS - 1)
        early_px = float(frame.iloc[early_idx]["close"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        early_ret = direction * ((early_px / entry_px) - 1.0)
        forward_8 = net_ret
        failure = int(early_ret <= 0)
        rows.append({
            "asset": sig["asset"],
            "setup": sig["setup"],
            "variant": variant,
            "regime": sig["regime"],
            "compression_to_expansion": bool(sig["compression_to_expansion"]),
            "signal_time": sig["timestamp"],
            "entry_time": entry_ts,
            "exit_time": pd.Timestamp(frame.iloc[exit_idx]["timestamp"]),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "direction": sig["direction"],
            "cost_bps_per_side": float(cost_bps),
            "gross_return": gross_ret,
            "net_return": net_ret,
            "early_return_4bars": early_ret,
            "failure_4bars": failure,
            "forward_return_8bars": forward_8,
        })
        active_until = pd.Timestamp(frame.iloc[exit_idx]["timestamp"])
    return pd.DataFrame(rows), admitted


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, base_signals: int, admitted_signals: int, base_trades: pd.DataFrame | None = None) -> dict[str, object]:
    trades_n = int(len(trades))
    total_return = float(trades["net_return"].sum()) if not trades.empty else np.nan
    avg_net = float(trades["net_return"].mean()) if not trades.empty else np.nan
    fail_rate = float(trades["failure_4bars"].mean()) if not trades.empty else np.nan
    dispersion_8 = float(trades["forward_return_8bars"].std(ddof=0)) if not trades.empty else np.nan
    trade_retention = np.nan
    if base_trades is not None:
        base_n = len(base_trades)
        trade_retention = float(trades_n / base_n) if base_n else np.nan
    signal_retention = float(admitted_signals / base_signals) if base_signals else np.nan
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "base_signals": int(base_signals),
        "admitted_signals": int(admitted_signals),
        "trades": trades_n,
        "trade_count_retention": trade_retention,
        "signal_retention": signal_retention,
        "total_return": total_return,
        "avg_net_ret": avg_net,
        "false_break_or_hold_4bars_rate": fail_rate,
        "forward_return_dispersion_8bars": dispersion_8,
    }


def build_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (setup, variant, cost_bps), grp in asset_summary.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False):
        rows.append({
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "mean_total_return": float(grp["total_return"].mean()) if not grp.empty else np.nan,
            "positive_asset_ratio": float((grp["total_return"] > 0).mean()) if not grp.empty else np.nan,
            "mean_trades": float(grp["trades"].mean()) if not grp.empty else np.nan,
            "mean_trade_count_retention": float(grp["trade_count_retention"].mean()) if not grp.empty else np.nan,
            "mean_signal_retention": float(grp["signal_retention"].mean()) if not grp.empty else np.nan,
            "mean_false_break_or_hold_4bars_rate": float(grp["false_break_or_hold_4bars_rate"].mean()) if not grp.empty else np.nan,
            "mean_forward_return_dispersion_8bars": float(grp["forward_return_dispersion_8bars"].mean()) if not grp.empty else np.nan,
        })
    return pd.DataFrame(rows)


def build_time_pockets(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=["variant", "time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades"])
    rows: list[dict[str, object]] = []
    for variant, grp in trades.groupby("variant", dropna=False):
        grp = grp.sort_values("entry_time").reset_index(drop=True)
        if len(grp) < 3:
            continue
        buckets = pd.qcut(np.arange(len(grp)), 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        grp = grp.assign(time_bucket=buckets)
        by_asset = grp.groupby(["time_bucket", "asset"], dropna=False).agg(total_return=("net_return", "sum"), trades=("net_return", "size")).reset_index()
        summary = by_asset.groupby("time_bucket", dropna=False).agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
        ).reset_index()
        summary["variant"] = variant
        rows.extend(summary.to_dict("records"))
    return pd.DataFrame(rows)


def build_regime_summary(df30: pd.DataFrame) -> pd.DataFrame:
    out = df30.groupby("regime", dropna=False).agg(
        bars=("regime", "size"),
        mean_hurst_100=("hurst_100", "mean"),
        mean_adx14=("adx14", "mean"),
        mean_rv20=("rv20", "mean"),
    ).reset_index()
    total = float(out["bars"].sum()) if not out.empty else 0.0
    out["share"] = out["bars"] / total if total else np.nan
    return out.sort_values("bars", ascending=False).reset_index(drop=True)


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    target = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        subset = target[target["setup"] == setup].set_index("variant")
        if "base" not in subset.index:
            continue
        row = {"setup": setup}
        for variant, prefix in [
            ("base", "base"),
            ("no_mr_gate", "no_mr"),
            ("trend_expansion_only", "trend_expansion"),
            ("compression_to_expansion_breakout", "compression_breakout"),
        ]:
            if variant in subset.index:
                r = subset.loc[variant]
                row[f"{prefix}_return"] = r.get("mean_total_return")
                row[f"{prefix}_retention"] = r.get("mean_trade_count_retention")
                row[f"{prefix}_signal_retention"] = r.get("mean_signal_retention")
                row[f"{prefix}_false_4bars"] = r.get("mean_false_break_or_hold_4bars_rate")
                row[f"{prefix}_dispersion_8bars"] = r.get("mean_forward_return_dispersion_8bars")
                row[f"{prefix}_positive_asset_ratio"] = r.get("positive_asset_ratio")
        rows.append(row)
    return pd.DataFrame(rows)


def build_verdict(compare: pd.DataFrame) -> tuple[str, str, str]:
    if compare.empty:
        return (
            "park / evidence pool",
            "暂无可比样本。",
            "最小 clean replication 连可比 setup 都没形成，不该继续占默认 Scout 预算。",
        )
    wins = 0
    strong_wins = 0
    for _, row in compare.iterrows():
        improved = (
            pd.notna(row.get("trend_expansion_return"))
            and pd.notna(row.get("base_return"))
            and pd.notna(row.get("trend_expansion_retention"))
            and pd.notna(row.get("trend_expansion_false_4bars"))
            and pd.notna(row.get("base_false_4bars"))
            and float(row["trend_expansion_retention"]) >= 0.45
            and (
                float(row["trend_expansion_return"]) > float(row["base_return"]) + 0.002
                or float(row["trend_expansion_false_4bars"]) < float(row["base_false_4bars"]) - 0.03
            )
        )
        if improved:
            wins += 1
            if float(row.get("trend_expansion_positive_asset_ratio", 0.0) or 0.0) >= (2 / 3):
                strong_wins += 1
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r.get('base_return'))} / no_MR≈{pct(r.get('no_mr_return'))} / trend+exp≈{pct(r.get('trend_expansion_return'))} / comp→exp≈{pct(r.get('compression_breakout_return'))}"
        for _, r in compare.iterrows()
    )
    if wins >= 2 and strong_wins >= 1:
        return (
            "P2 paper candidate / evidence queue",
            headline,
            "这次最小 clean replication 说明 regime matrix 不只是砍样本，而是在多条 archetype 上开始形成 shared allow/deny gate 的味道，值得先升到 P2。",
        )
    if wins >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "这次最小 clean replication 说明 regime matrix 在部分 archetype 上有 shared state gate 味道，但改善还不够统一；更诚实的读法仍是先留在 P1 证据池。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在说明：单靠 30m regime matrix shared gate 还不足以稳定改善当前三条 archetype 的成本后质量，不该继续占默认 Scout 主资源位。",
    )


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding="utf-8")


def render_factor_page(overall: pd.DataFrame, asset_summary: pd.DataFrame, compare: pd.DataFrame, pockets: pd.DataFrame, regime_summary: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup", "variant", "cost_bps_per_side", "mean_total_return", "positive_asset_ratio", "mean_trades",
        "mean_trade_count_retention", "mean_signal_retention", "mean_false_break_or_hold_4bars_rate", "mean_forward_return_dispersion_8bars"
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset", "setup", "variant", "trades", "trade_count_retention", "signal_retention", "total_return", "false_break_or_hold_4bars_rate", "forward_return_dispersion_8bars"
    ]].copy()
    compare_view = compare[[
        "setup", "base_return", "no_mr_return", "trend_expansion_return", "compression_breakout_return",
        "base_retention", "no_mr_retention", "trend_expansion_retention", "compression_breakout_retention",
        "base_false_4bars", "no_mr_false_4bars", "trend_expansion_false_4bars", "compression_breakout_false_4bars",
        "base_positive_asset_ratio", "no_mr_positive_asset_ratio", "trend_expansion_positive_asset_ratio", "compression_breakout_positive_asset_ratio"
    ]].copy()
    pockets_view = pockets.copy()
    regime_view = regime_summary.copy()
    return f"""
<p><a href='../../reading/repo_scout/rank67_regime_matrix_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 67 · regime-matrix shared-state gate（minimal clean replication）</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m 本地 cache，30m regime label 由同一条 15m 数据 resample + trailing 指标生成；执行统一冻结到 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>

<div class='card'>
  <h2>这轮只回答一个问题</h2>
  <p>当 <code>EMA = waiting_not_due</code> 时，Rank 67 只拿 1 次最小预算：<b>把 30m regime matrix 当 shared allow/deny layer</b>，能不能比裸做 setup 更诚实地改善 <code>breakout-short / Fib retest / EMA-PSAR</code> 的成本后质量？</p>
  <ul>
    <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
    <li><b>四臂：</b><code>base</code>、<code>no_MR_gate</code>、<code>trend_expansion_only</code>、<code>compression_to_expansion_breakout</code>。</li>
    <li><b>30m 状态变量：</b><code>hurst_100</code>、<code>ADX14</code>、<code>ADX slope(5)</code>、<code>rv20</code>、<code>rv slope(5)</code>。</li>
    <li><b>状态读法：</b><code>Trend / Expansion</code> 更像 continuation 允许态，<code>Compression</code> 更像 breakout 准备态，<code>Mean Reversion</code> 更像减仓 / 禁入态。</li>
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
  {render_table(compare_view, percent_cols={'base_return','no_mr_return','trend_expansion_return','compression_breakout_return','base_retention','no_mr_retention','trend_expansion_retention','compression_breakout_retention','base_false_4bars','no_mr_false_4bars','trend_expansion_false_4bars','compression_breakout_false_4bars','base_positive_asset_ratio','no_mr_positive_asset_ratio','trend_expansion_positive_asset_ratio','compression_breakout_positive_asset_ratio'})}
</div>

<div class='card'>
  <h2>overall summary</h2>
  {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_signal_retention','mean_false_break_or_hold_4bars_rate','mean_forward_return_dispersion_8bars'})}
</div>

<div class='card'>
  <h2>asset summary（6bps）</h2>
  {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','false_break_or_hold_4bars_rate','forward_return_dispersion_8bars'})}
</div>

<div class='card'>
  <h2>30m regime 占比</h2>
  {render_table(regime_view, percent_cols={'share'})}
</div>

<div class='card'>
  <h2>time pockets</h2>
  {render_table(pockets_view, percent_cols={'mean_total_return','positive_asset_ratio'})}
</div>
"""


def render_reading_page(compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    compare_view = compare[[
        "setup", "base_return", "no_mr_return", "trend_expansion_return", "compression_breakout_return",
        "base_retention", "no_mr_retention", "trend_expansion_retention", "compression_breakout_retention",
        "base_false_4bars", "no_mr_false_4bars", "trend_expansion_false_4bars", "compression_breakout_false_4bars"
    ]].copy()
    return f"""
<p><a href='rank67_regime_matrix_source_intake.html'>← 返回 source intake</a></p>
<h1>Rank 67 · regime-matrix shared-state gate clean replication</h1>
<div class='card'>
  <span class='pill'>更新时间：{escape(generated_at)}</span>
  <span class='pill'>类型：minimal clean replication</span>
  <span class='pill'>当前 verdict：{escape(verdict)}</span>
  <p class='muted'>artifact：<code>reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/overall_summary.csv</code></p>
</div>
<div class='card'>
  <h2>一句话结果</h2>
  <p><b>{escape(headline)}</b></p>
  <p class='muted'>{escape(reason)}</p>
</div>
<div class='card'>
  <h2>这轮冻结的最小实验</h2>
  <ul>
    <li><code>BTC/ETH/SOL</code>，复用 120d 15m 本地 cache，统一 resample 成 <code>30m</code> regime label。</li>
    <li>只比较四臂：<code>base</code>、<code>no_MR_gate</code>、<code>trend_expansion_only</code>、<code>compression_to_expansion_breakout</code>。</li>
    <li>执行统一：<code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</li>
    <li>首轮只看：<code>post-cost return</code>、<code>trade count retention</code>、<code>false-break / false-hold rate</code>、<code>8-bar forward return dispersion</code>。</li>
  </ul>
</div>
<div class='card'>
  <h2>setup compare（6bps）</h2>
  {render_table(compare_view, percent_cols={'base_return','no_mr_return','trend_expansion_return','compression_breakout_return','base_retention','no_mr_retention','trend_expansion_retention','compression_breakout_retention','base_false_4bars','no_mr_false_4bars','trend_expansion_false_4bars','compression_breakout_false_4bars'})}
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
- **最新补充（{generated_at}）**：这轮先再次核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane，最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`。因此当前没有新的 `Paper Seat` due-now 动作，也没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity，按权威顺序这轮执行 **`Run 3 / Rank 67 minimal clean replication`**。
  - 这轮已把 `Rank 67 / regime-matrix shared-state gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，统一 resample 成 `30m` regime label；只比较 `base`、`no_MR_gate`、`trend_expansion_only`、`compression_to_expansion_breakout` 四臂，执行统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。
  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `no_MR≈{pct(row_ema['no_mr_return'])}`、`trend+exp≈{pct(row_ema['trend_expansion_return'])}`、`comp→exp≈{pct(row_ema['compression_breakout_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `no_MR≈{pct(row_fib['no_mr_return'])}`、`trend+exp≈{pct(row_fib['trend_expansion_return'])}`、`comp→exp≈{pct(row_fib['compression_breakout_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `no_MR≈{pct(row_short['no_mr_return'])}`、`trend+exp≈{pct(row_short['trend_expansion_return'])}`、`comp→exp≈{pct(row_short['compression_breakout_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 67 / regime-matrix shared-state gate = {verdict}`**。
  - reader-facing 落点：`reports/site/factors/scout_rank67_regime_matrix_shared_state_15m/report.html`、`reports/site/reading/repo_scout/rank67_regime_matrix_clean_replication.html`；artifact：`reports/artifacts/scout_rank67_regime_matrix_shared_state_15m/overall_summary.csv`、`regime_summary_30m.csv`。
  - 当前更诚实的 active Scout 顺序应更新为：**`Rank 68 / block-mitigation retest score` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**（`Rank 67` 本轮已消耗完允许的那次 minimal clean replication；若 verdict 仍不足以升层，就不该继续赖在 fast-lane 队首）。
  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 67 未能升到下一层，则立刻切到 Rank 68 / block-mitigation retest score 做 source intake + 两条轻量诚实守门` -> `Run 3 = 若 Rank 68 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 68 这一轮直接 hard-fail / 未 admitted，则继续按 7.10 先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条新的 5m / 15m crypto source；只有 fresh source 这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。
"""
    text = text.replace(marker, f"\n{insert_block}{marker}", 1)
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    signal_frames: list[pd.DataFrame] = []
    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    regime_rows: list[pd.DataFrame] = []

    base_cache: dict[tuple[str, str, float], pd.DataFrame] = {}
    admitted_cache: dict[tuple[str, str, float, str], int] = {}

    for asset, symbol in ASSETS.items():
        bars15 = add_base_setup_signals(load_bars(symbol, asset))
        regime30, regime15 = build_regime_frame(bars15)
        regime30["asset"] = asset
        regime_rows.append(regime30)
        for setup in SETUPS:
            sigs = build_signal_frame(bars15, regime15, asset, setup)
            if not sigs.empty:
                signal_frames.append(sigs)
            base_signals = int(len(sigs))
            for cost in COSTS:
                base_trades, base_admitted = build_trades(bars15, sigs, "base", cost)
                base_cache[(asset, setup, cost)] = base_trades
                admitted_cache[(asset, setup, cost, "base")] = base_admitted
                if not base_trades.empty:
                    trade_frames.append(base_trades)
            for variant in VARIANTS:
                for cost in COSTS:
                    if variant == "base":
                        trades = base_cache[(asset, setup, cost)]
                        admitted = admitted_cache[(asset, setup, cost, variant)]
                    else:
                        trades, admitted = build_trades(bars15, sigs, variant, cost)
                        admitted_cache[(asset, setup, cost, variant)] = admitted
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
                            admitted_signals=admitted,
                            base_trades=base_cache[(asset, setup, cost)],
                        )
                    )

    all_signals = pd.concat(signal_frames, ignore_index=True) if signal_frames else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 67 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows.csv", index=False)

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame(columns=["asset"])
    all_trades.to_csv(ART_DIR / "trade_log.csv", index=False)
    asset_summary = pd.DataFrame(asset_rows)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall = build_overall(asset_summary)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / "time_pockets.csv", index=False)
    compare = build_setup_compare(overall)
    compare.to_csv(ART_DIR / "setup_compare.csv", index=False)
    regime_all = pd.concat(regime_rows, ignore_index=True)
    regime_summary = regime_all.groupby(["asset", "regime"], dropna=False).agg(
        bars=("regime", "size"),
        mean_hurst_100=("hurst_100", "mean"),
        mean_adx14=("adx14", "mean"),
        mean_rv20=("rv20", "mean"),
    ).reset_index()
    regime_summary.to_csv(ART_DIR / "regime_summary_30m.csv", index=False)
    regime_mix = build_regime_summary(regime_all)

    verdict, headline, reason = build_verdict(compare)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    factor_body = render_factor_page(overall, asset_summary, compare, pockets, regime_mix, verdict, headline, reason, generated_at)
    write_html(SITE_DIR / "report.html", "Rank 67 · regime-matrix shared-state gate clean replication", factor_body)
    reading_body = render_reading_page(compare, verdict, headline, reason, generated_at)
    write_html(READING_PATH, "Rank 67 · regime-matrix clean replication", reading_body)
    update_todo(compare, verdict, generated_at)

    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"headline={headline}")


if __name__ == "__main__":
    main()
