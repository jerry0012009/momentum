#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_15M_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
CACHE_5M_DIR = ROOT / "reports" / "artifacts" / "scout_rank66_exec_tf_switch_alignment_15m" / "spot_cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank132_adaptive_exhaustion_countertrend_leg_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank132_adaptive_exhaustion_countertrend_leg_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank132_adaptive_exhaustion_countertrend_leg_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["breakout_short", "fib_retest_long", "ema_psar_long"]
VARIANTS = ["baseline", "minor_exhaustion_gate", "strict_exhaustion_tier"]
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
ATR_PERIOD = 14
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
EPS = 1e-12

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def compute_atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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
    df = pd.read_csv(CACHE_15M_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def load_5m(symbol: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_5M_DIR / f"{symbol}_120d_5m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_15m(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["psar"] = compute_psar(df)
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["prior20_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0.0003)
        & (df["psar"] < df["close"])
        & (df["close"] > df["high"].shift(1))
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["prior20_low"].notna()
        & df["atr14"].notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < 0)
        & (df["close"] < df["prior20_low"])
        & (df["close"].shift(1) >= df["prior20_low"].shift(1))
        & (df["psar"] > df["close"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    return df


def build_5m_features(df5m: pd.DataFrame) -> pd.DataFrame:
    out = df5m.copy()
    out["ret1"] = out["close"].pct_change().fillna(0.0)
    return out[["timestamp", "open", "high", "low", "close", "ret1"]]


def collect_signals(frame: pd.DataFrame, feature_5m: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        direction = -1.0 if setup == "breakout_short" else 1.0
        signal_col = f"{setup}_signal"
        for idx in np.flatnonzero(frame[signal_col].to_numpy()):
            if idx + HOLD_BARS + 1 >= len(frame):
                continue
            signal_row = frame.iloc[idx]
            window_5m = feature_5m[feature_5m["timestamp"] <= signal_row["timestamp"]].tail(3)
            if len(window_5m) < 3 or not np.isfinite(signal_row["atr14"]):
                continue
            signed_rets = direction * window_5m["ret1"].to_numpy(dtype=float)
            counter_mag = float(np.maximum(-signed_rets, 0.0).sum())
            counter_count = int((signed_rets < 0).sum())
            response_strength = float(np.maximum(signed_rets[-1], 0.0) + 0.5 * np.maximum(signed_rets[-2], 0.0))
            response_ratio = response_strength / (counter_mag + EPS)
            pre_counter_mag = float(np.maximum(-signed_rets[:2], 0.0).sum())
            last_bar_in_trade_dir = bool(signed_rets[-1] > 0)
            last2_in_trade_dir = int((signed_rets[-2:] > 0).sum())
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "direction": direction,
                    "signal_idx": int(idx),
                    "signal_time": signal_row["timestamp"],
                    "atr14": float(signal_row["atr14"]),
                    "counter_mag": counter_mag,
                    "counter_count": counter_count,
                    "response_strength": response_strength,
                    "response_ratio": response_ratio,
                    "pre_counter_mag": pre_counter_mag,
                    "last_bar_in_trade_dir": last_bar_in_trade_dir,
                    "last2_in_trade_dir": last2_in_trade_dir,
                    "r5m_a": float(signed_rets[0]),
                    "r5m_b": float(signed_rets[1]),
                    "r5m_c": float(signed_rets[2]),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["setup", "asset", "signal_time"]).reset_index(drop=True)


def split_signals(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff = signals["signal_time"].sort_values().iloc[max(1, int(len(signals) * TRAIN_FRACTION)) - 1]
    train = signals[signals["signal_time"] <= cutoff].copy()
    test = signals[signals["signal_time"] > cutoff].copy()
    if test.empty:
        test = train.iloc[-max(1, len(train) // 3):].copy()
        train = train.iloc[:-len(test)].copy()
    return train, test


def make_threshold_config(train_catalog: pd.DataFrame) -> pd.DataFrame:
    cfg_rows = []
    for setup in SETUPS:
        subset = train_catalog[train_catalog["setup"] == setup].copy()
        with_counter = subset[subset["counter_count"] >= 1]
        if with_counter.empty:
            with_counter = subset.copy()
        minor_ratio = float(with_counter["response_ratio"].quantile(0.50))
        strict_ratio = float(with_counter["response_ratio"].quantile(0.75))
        min_counter_mag = float(with_counter["counter_mag"].quantile(0.33))
        cfg_rows.append(
            {
                "setup": setup,
                "minor_ratio_min": minor_ratio,
                "strict_ratio_min": max(strict_ratio, minor_ratio),
                "min_counter_mag": max(min_counter_mag, 0.0),
            }
        )
    return pd.DataFrame(cfg_rows)


def variant_pass(row: pd.Series, config_map: dict[str, dict[str, float]], variant: str) -> bool:
    if variant == "baseline":
        return True
    cfg = config_map[str(row["setup"])]
    if variant == "minor_exhaustion_gate":
        return (
            int(row["counter_count"]) >= 1
            and bool(row["last_bar_in_trade_dir"])
            and float(row["counter_mag"]) >= float(cfg["min_counter_mag"])
            and float(row["response_ratio"]) >= float(cfg["minor_ratio_min"])
        )
    if variant == "strict_exhaustion_tier":
        return (
            int(row["counter_count"]) >= 2
            and bool(row["last_bar_in_trade_dir"])
            and int(row["last2_in_trade_dir"]) >= 1
            and float(row["counter_mag"]) >= float(cfg["min_counter_mag"])
            and float(row["pre_counter_mag"]) > 0
            and float(row["response_ratio"]) >= float(cfg["strict_ratio_min"])
        )
    raise ValueError(variant)


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, config_map: dict[str, dict[str, float]], variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_setup = {setup: -1 for setup in SETUPS}
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_by_setup[setup]:
            continue
        if not variant_pass(sig, config_map, variant):
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        direction = float(sig["direction"])
        entry = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        gross = direction * (exit_price / entry - 1.0)
        atr = float(sig["atr14"])
        path = frame.iloc[entry_idx: exit_idx + 1]
        target = entry * (1.0 + direction * (atr / entry))
        failure = entry * (1.0 - direction * (atr / entry))
        target_hit = None
        failure_hit = None
        mae4 = 0.0
        for bar_idx, bar in path.iterrows():
            if direction > 0:
                if target_hit is None and float(bar["high"]) >= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["low"]) <= failure:
                    failure_hit = int(bar_idx)
                adverse = float(bar["low"]) / entry - 1.0
            else:
                if target_hit is None and float(bar["low"]) <= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["high"]) >= failure:
                    failure_hit = int(bar_idx)
                adverse = -(float(bar["high"]) / entry - 1.0)
            if bar_idx <= entry_idx + 3:
                mae4 = min(mae4, adverse)
        sl_first_rate = bool(failure_hit is not None and (target_hit is None or failure_hit <= target_hit))
        rows.append(
            {
                "asset": sig["asset"],
                "setup": setup,
                "variant": variant,
                "signal_idx": idx,
                "signal_time": sig["signal_time"],
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "exit_time": frame.iloc[exit_idx]["timestamp"],
                "entry_price": entry,
                "exit_price": exit_price,
                "gross_return": gross,
                "counter_mag": float(sig["counter_mag"]),
                "counter_count": int(sig["counter_count"]),
                "response_ratio": float(sig["response_ratio"]),
                "entry_delay_bars": 1,
                "sl_first_rate": sl_first_rate,
                "mae4": mae4,
            }
        )
        last_exit_by_setup[setup] = exit_idx
    return pd.DataFrame(rows)


def summarize_pair(baseline: pd.DataFrame, variant_df: pd.DataFrame, cost_bps: float) -> dict[str, float]:
    b_net = net_ret(baseline["gross_return"], cost_bps) if len(baseline) else pd.Series(dtype=float)
    v_net = net_ret(variant_df["gross_return"], cost_bps) if len(variant_df) else pd.Series(dtype=float)
    return {
        "baseline_trades": float(len(baseline)),
        "variant_trades": float(len(variant_df)),
        "trade_count_retention": float(len(variant_df) / len(baseline)) if len(baseline) else np.nan,
        "baseline_return": float(b_net.mean()) if len(b_net) else np.nan,
        "variant_return": float(v_net.mean()) if len(v_net) else np.nan,
        "return_delta": float(v_net.mean() - b_net.mean()) if len(v_net) and len(b_net) else np.nan,
        "baseline_sl_first_rate": float(baseline["sl_first_rate"].mean()) if len(baseline) else np.nan,
        "variant_sl_first_rate": float(variant_df["sl_first_rate"].mean()) if len(variant_df) else np.nan,
        "sl_first_delta": float(variant_df["sl_first_rate"].mean() - baseline["sl_first_rate"].mean()) if len(variant_df) and len(baseline) else np.nan,
        "baseline_mae4": float(baseline["mae4"].mean()) if len(baseline) else np.nan,
        "variant_mae4": float(variant_df["mae4"].mean()) if len(variant_df) else np.nan,
        "mae4_delta": float(variant_df["mae4"].mean() - baseline["mae4"].mean()) if len(variant_df) and len(baseline) else np.nan,
        "variant_entry_delay_bars": float(variant_df["entry_delay_bars"].mean()) if len(variant_df) else np.nan,
    }


def make_scorecard(test_overall: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for variant in ["minor_exhaustion_gate", "strict_exhaustion_tier"]:
        row = test_overall[(test_overall["split"] == "test") & (test_overall["variant"] == variant) & (test_overall["cost_bps"] == PRIMARY_COST)].iloc[0]
        trade_ret = float(row["trade_count_retention"])
        return_delta = float(row["return_delta"])
        sl_delta = float(row["sl_first_delta"])
        useful = 3 if return_delta > 0.001 else 2 if return_delta > 0 else 1 if return_delta > -0.001 else 0
        time_stability = 2 if trade_ret >= 0.55 else 1 if trade_ret >= 0.40 else 0
        cross_asset_stability = np.nan
        cost_trade_stability = 2 if return_delta > 0 and trade_ret >= 0.50 else 1 if return_delta > -0.0005 else 0
        deployability = 2 if sl_delta <= 0 and trade_ret >= 0.50 else 1 if sl_delta <= 0.01 else 0
        hard_fail_flags = []
        if trade_ret < 0.35:
            hard_fail_flags.append("too_sparse")
        if return_delta < -0.001:
            hard_fail_flags.append("post_cost_collapse")
        rows.append(
            {
                "variant": variant,
                "usefulness": useful,
                "time_stability": time_stability,
                "cross_asset_stability": cross_asset_stability,
                "cost_trade_stability": cost_trade_stability,
                "deployability": deployability,
                "hard_fail_flags": ", ".join(hard_fail_flags) if hard_fail_flags else "",
            }
        )
    return pd.DataFrame(rows)


def verdict_from_test(test_overall: pd.DataFrame, test_asset: pd.DataFrame) -> tuple[str, str, str]:
    test_minor = test_overall[(test_overall["split"] == "test") & (test_overall["variant"] == "minor_exhaustion_gate") & (test_overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    test_strict = test_overall[(test_overall["split"] == "test") & (test_overall["variant"] == "strict_exhaustion_tier") & (test_overall["cost_bps"] == PRIMARY_COST)].iloc[0]
    best = test_minor if float(test_minor["return_delta"]) >= float(test_strict["return_delta"]) else test_strict
    positive_assets = test_asset[(test_asset["split"] == "test") & (test_asset["variant"] == best["variant"]) & (test_asset["cost_bps"] == PRIMARY_COST) & (test_asset["return_delta"] > 0)]
    if float(best["return_delta"]) > 0.001 and float(best["trade_count_retention"]) >= 0.55 and len(positive_assets) >= 2:
        return "promote_P2", "test 段在 6bps 下有正向 uplift，且交易保留率与跨资产分布都还过得去。", "当前最大短板是 5m exhaustion 只对部分 setup 更明显，shared 性还不够硬。"
    if float(best["return_delta"]) > -0.0005 and float(best["trade_count_retention"]) >= 0.40:
        return "keep_P1", "test 段说明它更像 honest follow-up gate，而不是足够硬的 paper candidate。", "主要弱点是严格 tier 交易数掉得更快，shared 默认层还不够稳。"
    return "park", "test 段没有证明它值得继续占默认预算。", "主要弱点是成本后增益站不住或 trade retention 过薄。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    features_5m = {asset: build_5m_features(load_5m(symbol)) for asset, symbol in ASSETS.items()}
    signal_parts = [collect_signals(frames[asset], features_5m[asset], asset) for asset in ASSETS]
    signal_catalog = pd.concat(signal_parts, ignore_index=True)
    if signal_catalog.empty:
        raise SystemExit("rank132: no signals collected")

    train_catalog, test_catalog = split_signals(signal_catalog)
    threshold_df = make_threshold_config(train_catalog)
    config_map = threshold_df.set_index("setup").to_dict(orient="index")

    signal_catalog = signal_catalog.merge(threshold_df, on="setup", how="left")
    signal_catalog["minor_pass"] = signal_catalog.apply(lambda row: variant_pass(row, config_map, "minor_exhaustion_gate"), axis=1)
    signal_catalog["strict_pass"] = signal_catalog.apply(lambda row: variant_pass(row, config_map, "strict_exhaustion_tier"), axis=1)
    signal_catalog["split"] = np.where(signal_catalog["signal_time"] <= train_catalog["signal_time"].max(), "train", "test")

    overall_rows = []
    setup_rows = []
    asset_rows = []
    cost_rows = []
    trade_parts = []

    split_frames = {
        "train": train_catalog,
        "test": test_catalog,
    }

    for split_name, split_df in split_frames.items():
        variant_parts = {variant: [] for variant in VARIANTS}
        for asset in ASSETS:
            asset_signals = split_df[split_df["asset"] == asset].copy()
            frame = frames[asset]
            for variant in VARIANTS:
                variant_parts[variant].append(simulate_variant(frame, asset_signals, config_map, variant))
        variant_dfs = {variant: pd.concat(parts, ignore_index=True) if parts else pd.DataFrame() for variant, parts in variant_parts.items()}
        for variant, df in variant_dfs.items():
            if not df.empty:
                trade_parts.append(df.assign(split=split_name))
        baseline_df = variant_dfs["baseline"]
        for variant in ["minor_exhaustion_gate", "strict_exhaustion_tier"]:
            variant_df = variant_dfs[variant]
            for cost in COSTS:
                overall_rows.append({"split": split_name, "variant": variant, "cost_bps": cost, **summarize_pair(baseline_df, variant_df, cost)})
                cost_rows.append({"split": split_name, "variant": variant, "cost_bps": cost, **summarize_pair(baseline_df, variant_df, cost)})
                for setup in SETUPS:
                    b_sub = baseline_df[baseline_df["setup"] == setup].copy()
                    v_sub = variant_df[variant_df["setup"] == setup].copy()
                    setup_rows.append({"split": split_name, "variant": variant, "setup": setup, "cost_bps": cost, **summarize_pair(b_sub, v_sub, cost)})
                for asset in ASSETS:
                    b_sub = baseline_df[baseline_df["asset"] == asset].copy()
                    v_sub = variant_df[variant_df["asset"] == asset].copy()
                    asset_rows.append({"split": split_name, "variant": variant, "asset": asset, "cost_bps": cost, **summarize_pair(b_sub, v_sub, cost)})

    trade_log = pd.concat(trade_parts, ignore_index=True) if trade_parts else pd.DataFrame()
    overall_df = pd.DataFrame(overall_rows)
    setup_df = pd.DataFrame(setup_rows)
    asset_df = pd.DataFrame(asset_rows)
    cost_df = pd.DataFrame(cost_rows)
    scorecard_df = make_scorecard(overall_df)
    recommended_action, why_now, main_weakness = verdict_from_test(overall_df, asset_df)

    threshold_df.to_csv(ART_DIR / "threshold_config.csv", index=False)
    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    overall_df.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_df.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_df.to_csv(ART_DIR / "cost_summary.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    scorecard_df.to_csv(ART_DIR / "scorecard.csv", index=False)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "recommended_action": recommended_action,
        "why_now": why_now,
        "main_weakness": main_weakness,
        "costs_bps": COSTS,
        "hold_bars": HOLD_BARS,
        "setup_count": int(signal_catalog["setup"].nunique()),
        "asset_count": int(signal_catalog["asset"].nunique()),
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    test_minor = overall_df[(overall_df["split"] == "test") & (overall_df["variant"] == "minor_exhaustion_gate") & (overall_df["cost_bps"] == PRIMARY_COST)].iloc[0]
    test_strict = overall_df[(overall_df["split"] == "test") & (overall_df["variant"] == "strict_exhaustion_tier") & (overall_df["cost_bps"] == PRIMARY_COST)].iloc[0]

    title = "Rank 132 / adaptive exhaustion countertrend-leg gate clean replication"
    body = f"""
    <h1>{escape(title)}</h1>
    <p class='muted'>生成时间：{escape(summary['generated_at_utc'])} · 口径：BTC/ETH/SOL perpetual、15m signal + 5m execution readout、next-bar open、no-overlap、hold 8 bars、6/10/15bps</p>
    <div class='card'>
      <h2>一句话结论</h2>
      <p><strong>{escape(recommended_action)}</strong> —— {escape(why_now)}</p>
      <p>main_weakness：{escape(main_weakness)}</p>
      <p>test @ 6bps：minor gate return delta = <strong>{pct(test_minor['return_delta'])}</strong>，trade retention = <strong>{pct(test_minor['trade_count_retention'])}</strong>；strict tier return delta = <strong>{pct(test_strict['return_delta'])}</strong>，trade retention = <strong>{pct(test_strict['trade_count_retention'])}</strong>。</p>
    </div>
    <div class='card'>
      <h2>冻结阈值</h2>
      {render_table(threshold_df, digits_cols={'minor_ratio_min': 3, 'strict_ratio_min': 3, 'min_counter_mag': 4})}
    </div>
    <div class='card'>
      <h2>Scout Promotion Scorecard</h2>
      {render_table(scorecard_df)}
    </div>
    <div class='card'>
      <h2>Overall summary</h2>
      {render_table(overall_df[overall_df['cost_bps'] == PRIMARY_COST], percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_sl_first_rate','variant_sl_first_rate','sl_first_delta','baseline_mae4','variant_mae4','mae4_delta'})}
    </div>
    <div class='card'>
      <h2>Setup summary（test @ 6bps）</h2>
      {render_table(setup_df[(setup_df['split'] == 'test') & (setup_df['cost_bps'] == PRIMARY_COST)], percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_sl_first_rate','variant_sl_first_rate','sl_first_delta','baseline_mae4','variant_mae4','mae4_delta'})}
    </div>
    <div class='card'>
      <h2>Asset summary（test @ 6bps）</h2>
      {render_table(asset_df[(asset_df['split'] == 'test') & (asset_df['cost_bps'] == PRIMARY_COST)], percent_cols={'trade_count_retention','baseline_return','variant_return','return_delta','baseline_sl_first_rate','variant_sl_first_rate','sl_first_delta','baseline_mae4','variant_mae4','mae4_delta'})}
    </div>
    <div class='card'>
      <h2>说明</h2>
      <ul>
        <li><code>minor_exhaustion_gate</code>：要求最近 3 根 5m 里至少出现过一次 countertrend leg，且最后一根 5m 已回到交易方向，同时反抽/回踩反应强度达到训练段冻结阈值。</li>
        <li><code>strict_exhaustion_tier</code>：要求最近 3 根 5m 至少有两根体现 countertrend leg，再用更高的 response_ratio 阈值做更严格放行。</li>
        <li>这不是独立 alpha；它只是在 baseline setup 上测试“countertrend leg 已衰竭再放行”这层 follow-up honesty gap 是否成立。</li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / "report.html", title, body)
    write_html(READING_PATH, title, body)

    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
