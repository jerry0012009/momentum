#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank56_liquidation_map_path_overlay_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank56_liquidation_map_path_overlay_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"
CACHE_SEARCH_DIRS = [
    ROOT / "reports" / "artifacts" / "scout_rank55_order_imbalance_crash_risk_15m" / "aggtrades_cache",
    ROOT / "reports" / "artifacts" / "scout_rank52_trade_flow_imbalance_15m" / "aggtrades_cache",
]

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "binary_path_gate", "size_tilt"]
PRIMARY_COST = 6.0
COSTS = [6.0]
HOLD_BARS = 8
FALSE_LOOKAHEAD = 4
MAX_SIGNALS_PER_SETUP_ASSET = 8
PATH_THRESHOLD = 0.05
LEVERAGE_WEIGHTS = [(0.99, 1.00), (0.98, 0.85), (0.96, 0.65), (0.90, 0.40)]


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


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def cache_path(symbol: str, signal_ts: pd.Timestamp) -> Path | None:
    stamp = signal_ts.strftime("%Y%m%dT%H%M%SZ")
    name = f"{symbol}_{stamp}.json"
    for base in CACHE_SEARCH_DIRS:
        path = base / name
        if path.exists():
            return path
    return None


def summarize_liquidation_map(symbol: str, signal_ts: pd.Timestamp, signal_price: float, atr14: float, direction: int) -> dict[str, float | int]:
    path = cache_path(symbol, signal_ts)
    if path is None:
        return {
            "path_score": 0.0,
            "favorable_density": 0.0,
            "adverse_density": 0.0,
            "selected_trades": 0,
            "selected_notional": 0.0,
            "coverage_ratio": 0.0,
            "window_trade_count": 0,
        }
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not rows:
        return {
            "path_score": 0.0,
            "favorable_density": 0.0,
            "adverse_density": 0.0,
            "selected_trades": 0,
            "selected_notional": 0.0,
            "coverage_ratio": 0.0,
            "window_trade_count": 0,
        }
    df = pd.DataFrame(rows)
    df["price"] = pd.to_numeric(df["p"], errors="coerce")
    df["qty"] = pd.to_numeric(df["q"], errors="coerce")
    df = df.dropna(subset=["price", "qty"]).copy()
    if df.empty:
        return {
            "path_score": 0.0,
            "favorable_density": 0.0,
            "adverse_density": 0.0,
            "selected_trades": 0,
            "selected_notional": 0.0,
            "coverage_ratio": 0.0,
            "window_trade_count": 0,
        }
    df["notional"] = df["price"] * df["qty"]
    df["sell_aggressor"] = df["m"].astype(bool)
    threshold = max(100000.0, float(df["notional"].quantile(0.99)))
    sel = df[df["notional"] >= threshold].copy()
    if sel.empty:
        return {
            "path_score": 0.0,
            "favorable_density": 0.0,
            "adverse_density": 0.0,
            "selected_trades": 0,
            "selected_notional": 0.0,
            "coverage_ratio": 0.0,
            "window_trade_count": int(len(df)),
        }

    lower_outer = max(1e-9, signal_price - 1.5 * atr14)
    lower_inner = max(1e-9, signal_price - 0.3 * atr14)
    upper_inner = signal_price + 0.3 * atr14
    upper_outer = signal_price + 1.5 * atr14

    favorable = 0.0
    adverse = 0.0
    for _, r in sel.iterrows():
        px = float(r["price"])
        notional = float(r["notional"])
        sell_aggr = bool(r["sell_aggressor"])
        for mult, w in LEVERAGE_WEIGHTS:
            mapped = px * (1.0 / mult if sell_aggr else mult)
            weight = notional * w
            if direction > 0:
                if sell_aggr and upper_inner <= mapped <= upper_outer:
                    favorable += weight
                if (not sell_aggr) and lower_outer <= mapped <= lower_inner:
                    adverse += weight
            else:
                if (not sell_aggr) and lower_outer <= mapped <= lower_inner:
                    favorable += weight
                if sell_aggr and upper_inner <= mapped <= upper_outer:
                    adverse += weight

    total = favorable + adverse
    path_score = (favorable - adverse) / (total + 1e-8)
    selected_notional = float(sel["notional"].sum())
    return {
        "path_score": float(path_score),
        "favorable_density": float(favorable),
        "adverse_density": float(adverse),
        "selected_trades": int(len(sel)),
        "selected_notional": selected_notional,
        "coverage_ratio": float(total / (selected_notional + 1e-8)),
        "window_trade_count": int(len(df)),
    }


def build_signal_frame(frame: pd.DataFrame, asset: str, symbol: str, setup: str) -> pd.DataFrame:
    sig = frame[setup_signal_col(setup)] & ~frame[setup_signal_col(setup)].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        row = frame.iloc[idx]
        signal_ts = pd.to_datetime(row["timestamp"], utc=True)
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
            }
        )
        last_exit = idx + HOLD_BARS
    rows = rows[-MAX_SIGNALS_PER_SETUP_ASSET:]
    enriched: list[dict[str, object]] = []
    for row in rows:
        signal_ts = pd.to_datetime(row["signal_ts"], utc=True)
        proxy = summarize_liquidation_map(symbol, signal_ts, float(row["signal_price"]), float(row["atr14"]), int(row["direction"]))
        enriched.append({**row, **proxy})
    return pd.DataFrame(enriched)


def variant_allowed(sig: pd.Series, variant: str) -> bool:
    if variant == "base":
        return True
    if variant == "binary_path_gate":
        return float(sig["path_score"]) > PATH_THRESHOLD
    if variant == "size_tilt":
        return True
    raise ValueError(variant)


def position_multiplier(sig: pd.Series, variant: str) -> float:
    if variant != "size_tilt":
        return 1.0
    score = float(sig["path_score"])
    if score > PATH_THRESHOLD:
        return 1.2
    if score < -PATH_THRESHOLD:
        return 0.6
    return 0.9


def detect_false_follow(frame: pd.DataFrame, signal_idx: int, direction: int, fail_level: float) -> int:
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
    admitted = 0
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        if not variant_allowed(sig, variant):
            continue
        admitted += 1
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
                "false_follow_4bars": detect_false_follow(frame, int(sig["signal_idx"]), direction, fail_level),
                "path_score": float(sig["path_score"]),
                "selected_trades": int(sig["selected_trades"]),
                "selected_notional": float(sig["selected_notional"]),
                "coverage_ratio": float(sig["coverage_ratio"]),
            }
        )
    return pd.DataFrame(rows), admitted


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
            "false_follow_4bars_rate": np.nan,
            "mean_path_score": np.nan,
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
        "false_follow_4bars_rate": float(trades["false_follow_4bars"].mean()),
        "mean_path_score": float(trades["path_score"].mean()),
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
        gate = primary[(primary["setup"] == setup) & (primary["variant"] == "binary_path_gate")]
        size = primary[(primary["setup"] == setup) & (primary["variant"] == "size_tilt")]
        base_ret = float(base["total_return"].mean()) if not base.empty else np.nan
        gate_ret = float(gate["total_return"].mean()) if not gate.empty else np.nan
        size_ret = float(size["total_return"].mean()) if not size.empty else np.nan
        base_false = float(base["false_follow_4bars_rate"].mean()) if not base.empty else np.nan
        gate_false = float(gate["false_follow_4bars_rate"].mean()) if not gate.empty else np.nan
        size_false = float(size["false_follow_4bars_rate"].mean()) if not size.empty else np.nan
        gate_retention = float(gate["trade_count_retention"].mean()) if not gate.empty else np.nan
        size_retention = float(size["trade_count_retention"].mean()) if not size.empty else np.nan
        best_variant = "base"
        improved = False
        if pd.notna(gate_ret) and pd.notna(base_ret) and pd.notna(gate_retention) and gate_retention >= 0.35 and (gate_ret > base_ret or (pd.notna(gate_false) and pd.notna(base_false) and gate_false < base_false - 0.05)):
            best_variant = "binary_path_gate"
            improved = True
        if pd.notna(size_ret) and pd.notna(base_ret) and pd.notna(size_retention) and size_retention >= 0.6 and size_ret > max(base_ret, gate_ret if pd.notna(gate_ret) else -np.inf):
            best_variant = "size_tilt"
            improved = True
        if improved:
            wins += 1
        rows.append(
            {
                "setup": setup,
                "base_return": base_ret,
                "gate_return": gate_ret,
                "size_return": size_ret,
                "base_false_follow": base_false,
                "gate_false_follow": gate_false,
                "size_false_follow": size_false,
                "gate_trade_retention": gate_retention,
                "size_trade_retention": size_retention,
                "best_variant": best_variant,
                "improved_vs_base": improved,
            }
        )
    comp = pd.DataFrame(rows)
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r['base_return'])} / gate≈{pct(r['gate_return'])} / size≈{pct(r['size_return'])}"
        for _, r in comp.iterrows()
    )
    if wins >= 2:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 至少说明 liquidation-map path overlay 不是纯图像幻觉：在不过度砍样本的前提下，有不止一条 base setup 出现了成本后改善或更低的 false-follow，但当前证据仍不够直接升到 P2。",
            comp,
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：liquidation-map path overlay 偶尔能让单条 setup 少亏，但当前改善不够统一，且更像局部 sizing/veto 作用，不该继续占默认 clean-replication 队列。",
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
        "mean_false_follow_4bars_rate",
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
        "false_follow_4bars_rate",
        "mean_path_score",
    ]].copy()
    compare_view = comp[[
        "setup",
        "base_return",
        "gate_return",
        "size_return",
        "base_false_follow",
        "gate_false_follow",
        "size_false_follow",
        "gate_trade_retention",
        "size_trade_retention",
        "best_variant",
        "improved_vs_base",
    ]].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 56 · liquidation-map path overlay clean replication</title>
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
  <p><a href='../../reading/repo_scout/rank56_liquidation_map_path_overlay_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 56 · liquidation-map path overlay（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m cache；复用已有 signal 前 aggTrades 缓存，把大额主动成交映射成上下方潜在 liquidation cluster；执行统一 <code>next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 56 只拿 1 次最小预算：<b>把 liquidation-map 的 cluster path score 当成 shared path/risk overlay</b>，能不能同时改善当前 desk 三条 archetype（<code>EMA/PSAR long</code>、<code>Fib retest long</code>、<code>breakout short</code>）的成本后表现 / 假 follow-through / 回撤？</p>
    <ul>
      <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
      <li><b>overlay 变体：</b><code>base</code>、<code>binary_path_gate</code>、<code>size_tilt</code>。</li>
      <li><b>path score：</b>对每个 signal 前已缓存的 <code>aggTrades</code>，只保留大额主动成交（<code>max(100k USDT, top1%)</code>），再把 Buy / Sell 映射到下方 / 上方可能的 liquidation 带，比较 entry 上下 <code>0.3~1.5 ATR</code> 内的顺势 fuel 与逆风 trap。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li><code>binary_path_gate</code>：只有 <code>path_score &gt; {PATH_THRESHOLD:.2f}</code> 才放行；否则直接 veto。</li>
      <li><code>size_tilt</code>：<code>path_score</code> 明显顺势时放大到 <code>1.2x</code>，明显逆风时缩到 <code>0.6x</code>，其余中性区降到 <code>0.9x</code>。</li>
      <li>这仍是 <b>cheap public proxy</b>：当前复用的是已缓存的 signal 前 aggTrades 摘要，不是完整 6h/24h 日级回补，也不是真实 liquidation tape。</li>
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
    {render_table(compare_view, percent_cols={'base_return','gate_return','size_return','base_false_follow','gate_false_follow','size_false_follow','gate_trade_retention','size_trade_retention'}, digits_cols={})}
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_max_drawdown','mean_false_follow_4bars_rate'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','max_drawdown','false_follow_4bars_rate','mean_path_score'}, digits_cols={'trades':0})}
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
    anchor = 'rank56_liquidation_map_path_overlay_source_intake.html">Rank 56 source intake</a>'
    if 'rank56_liquidation_map_path_overlay_clean_replication.html' in text or anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank56_liquidation_map_path_overlay_clean_replication.html">clean replication</a>', 1)
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
    anchor = "- **最新补充（2026-03-18 13:12 UTC）**"
    marker = "\n### Next 3 bot3 runs（当前默认执行顺序）"
    insert_block = f"""- **最新补充（{generated_at}）**：这轮已按当前 `Run 2` 顺序把 `Rank 56 / liquidation-map path overlay` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，并复用已有 signal 前 `aggTrades` 缓存，只保留大额主动成交（`max(100k USDT, top1%)`），再按 source 语义映射成 entry 上下 `0.3~1.5 ATR` 的潜在 liquidation cluster density，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`binary_path_gate`、`size_tilt` 三臂；执行统一冻结到 **`next-bar open + no-overlap + hold 8 bars`**。
  - `6bps/side` 下的 setup-level 结果并不算统一：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `gate≈{pct(row_ema['gate_return'])}`、`size≈{pct(row_ema['size_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `gate≈{pct(row_fib['gate_return'])}`、`size≈{pct(row_fib['size_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `gate≈{pct(row_short['gate_return'])}`、`size≈{pct(row_short['size_return'])}`。
  - 当前更诚实的 hard verdict：**`Rank 56 / liquidation-map path overlay = {verdict}`**。更直白地说：它现在已经不该继续停在 clean-replication queue；若后续继续认领，默认只能按这个 verdict 走，而不是继续磨 source-intake wording。
  - reader-facing 落点：`reports/site/factors/scout_rank56_liquidation_map_path_overlay_15m/report.html`、`reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_clean_replication.html`；artifact：`reports/artifacts/scout_rank56_liquidation_map_path_overlay_15m/overall_summary.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = Rank 55 / order-imbalance crash-risk overlay 的 1 次便宜时间稳定性检查（仅当 EMA 仍 waiting_not_due）` -> `Run 3 = 若 Rank 55 也不能给出更高层 verdict，再比较 Rank 35b > Rank 16b > tiny-live plumbing；若出现新的 fresh intake，则仍按 fresh intake 优先`**。"""
    if anchor not in text or insert_block in text:
        return
    if marker in text:
        text = text.replace(marker, "\n" + insert_block + marker, 1)
    else:
        text += "\n" + insert_block + "\n"
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signal_tables: list[pd.DataFrame] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            signal_tables.append(build_signal_frame(frame, asset, symbol, setup))
    all_signals = pd.concat([df for df in signal_tables if not df.empty], ignore_index=True) if signal_tables else pd.DataFrame()
    if all_signals.empty:
        raise RuntimeError("no signals formed for Rank 56 clean replication")
    all_signals.to_csv(ART_DIR / "signal_windows_with_path_score.csv", index=False)

    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, admitted = build_trades(frame, sigs, variant, cost)
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
            mean_false_follow_4bars_rate=("false_follow_4bars_rate", "mean"),
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
            "candidate_id": "rank56_liquidation_map_path_overlay_15m",
            "hard_verdict": verdict,
            "headline": headline,
            "reason": reason,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, asset_summary, pockets, comp, verdict, headline, reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank56_liquidation_map_path_overlay_clean_replication.html").write_text(html, encoding="utf-8")

    update_reading_report()
    update_todo(comp, verdict, generated_at)

    print(f"verdict={verdict}")
    print(headline)


if __name__ == "__main__":
    main()
