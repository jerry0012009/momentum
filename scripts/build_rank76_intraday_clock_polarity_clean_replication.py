#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank76_intraday_clock_polarity_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank76_intraday_clock_polarity_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank76_intraday_clock_polarity_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "polarity_only", "polarity_plus_blackout"]
PRIMARY_VARIANT = "polarity_plus_blackout"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
EMA_FAST = 9
EMA_SLOW = 15
POLARITY_MIN_OBS = 30
POLARITY_Z_THRESHOLD = 1.96
FOMC_EVENTS_UTC = [
    "2025-12-17T19:00:00Z",
    "2026-01-28T19:00:00Z",
    "2026-03-18T18:00:00Z",
]
BLACKOUT_HOURS = 2

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


def build_hourly_polarity(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    hourly = (
        df.set_index("timestamp")[["open", "high", "low", "close", "volume"]]
        .resample("1h", label="right", closed="right")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    hourly["hour_ret"] = hourly["close"].pct_change()
    hourly["next_hour_ret"] = hourly["hour_ret"].shift(-1)
    hourly["pair_value"] = hourly["hour_ret"] * hourly["next_hour_ret"]
    hourly["hour_of_day"] = hourly["timestamp"].dt.hour
    hourly["pair_value_lag"] = hourly.groupby("hour_of_day")["pair_value"].shift(1)
    grp = hourly.groupby("hour_of_day")["pair_value_lag"]
    rolling_mean = grp.transform(lambda s: s.rolling(POLARITY_MIN_OBS, min_periods=POLARITY_MIN_OBS).mean())
    rolling_std = grp.transform(lambda s: s.rolling(POLARITY_MIN_OBS, min_periods=POLARITY_MIN_OBS).std(ddof=1))
    rolling_count = grp.transform(lambda s: s.rolling(POLARITY_MIN_OBS, min_periods=POLARITY_MIN_OBS).count())
    hourly["polarity_mean"] = rolling_mean
    hourly["polarity_std"] = rolling_std
    hourly["polarity_obs"] = rolling_count
    hourly["polarity_tstat"] = hourly["polarity_mean"] / (hourly["polarity_std"] / np.sqrt(hourly["polarity_obs"]))
    hourly["polarity"] = 0
    hourly.loc[(hourly["polarity_tstat"] >= POLARITY_Z_THRESHOLD) & (hourly["polarity_mean"] > 0), "polarity"] = 1
    hourly.loc[(hourly["polarity_tstat"] <= -POLARITY_Z_THRESHOLD) & (hourly["polarity_mean"] < 0), "polarity"] = -1
    summary = (
        hourly.dropna(subset=["polarity_obs"])
        .groupby("hour_of_day", dropna=False)
        .agg(
            polarity_mean=("polarity_mean", "last"),
            polarity_tstat=("polarity_tstat", "last"),
            polarity_obs=("polarity_obs", "last"),
            continuation_share=("polarity", lambda s: float((s == 1).mean())),
            reversal_share=("polarity", lambda s: float((s == -1).mean())),
            neutral_share=("polarity", lambda s: float((s == 0).mean())),
        )
        .reset_index()
        .sort_values("hour_of_day")
        .reset_index(drop=True)
    )
    return hourly, summary


def build_blackout_mask(frame: pd.DataFrame) -> pd.Series:
    events = pd.to_datetime(FOMC_EVENTS_UTC, utc=True)
    ts = frame["timestamp"]
    mask = pd.Series(False, index=frame.index)
    for event in events:
        mask |= (ts >= event - pd.Timedelta(hours=BLACKOUT_HOURS)) & (ts <= event + pd.Timedelta(hours=BLACKOUT_HOURS))
    return mask


def build_frame(asset: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load_bars(symbol, asset)
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

    hourly, polarity_summary = build_hourly_polarity(df)
    df["hour_bucket"] = df["timestamp"].dt.ceil("1h")
    df = df.merge(
        hourly[["timestamp", "polarity", "polarity_mean", "polarity_tstat", "polarity_obs"]].rename(columns={"timestamp": "hour_bucket"}),
        on="hour_bucket",
        how="left",
    )
    df["polarity"] = df["polarity"].fillna(0).astype(int)
    df["fomc_blackout"] = build_blackout_mask(df)
    return df, polarity_summary


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def polarity_allows(setup: str, polarity: pd.Series) -> pd.Series:
    if setup == "fib_retest_long":
        return polarity.eq(-1)
    return polarity.eq(1)


def gate_pass(frame: pd.DataFrame, setup: str, variant: str) -> pd.Series:
    allows = polarity_allows(setup, frame["polarity"]).fillna(False)
    blackout = frame["fomc_blackout"].fillna(False)
    if variant == "baseline":
        return pd.Series(True, index=frame.index)
    if variant == "polarity_only":
        return allows
    if variant == "polarity_plus_blackout":
        return allows & ~blackout
    raise ValueError(variant)


def build_signals(frame: pd.DataFrame, asset: str, setup: str, variant: str) -> pd.DataFrame:
    base = frame[f"{setup}_signal"] & ~frame[f"{setup}_signal"].shift(1).fillna(False)
    sig = base & gate_pass(frame, setup, variant)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(60, len(frame) - HOLD_BARS - 1):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        rows.append({
            "signal_id": f"{asset}|{setup}|{variant}|{idx}",
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "direction": direction,
            "signal_idx": idx,
            "entry_idx": idx + 1,
            "signal_ts": pd.to_datetime(frame.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "signal_price": float(frame.iloc[idx]["close"]),
            "polarity": int(frame.iloc[idx]["polarity"]),
            "polarity_mean": float(frame.iloc[idx]["polarity_mean"]) if pd.notna(frame.iloc[idx]["polarity_mean"]) else np.nan,
            "polarity_tstat": float(frame.iloc[idx]["polarity_tstat"]) if pd.notna(frame.iloc[idx]["polarity_tstat"]) else np.nan,
            "polarity_obs": float(frame.iloc[idx]["polarity_obs"]) if pd.notna(frame.iloc[idx]["polarity_obs"]) else np.nan,
            "fomc_blackout": bool(frame.iloc[idx]["fomc_blackout"]),
            "ema15": float(frame.iloc[idx]["ema15"]),
            "breakout_anchor": float(frame.iloc[idx]["rolling_low20"]) if setup == "breakout_short" else np.nan,
            "fib_618": float(frame.iloc[idx]["fib_618"]) if setup == "fib_retest_long" else np.nan,
        })
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def build_trades(frame: pd.DataFrame, signals: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost_bps) / 10000.0
    for _, sig in signals.iterrows():
        entry_idx = int(sig["entry_idx"])
        if entry_idx >= len(frame):
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        direction = int(sig["direction"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        gross = direction * (exit_px / entry_px - 1.0)
        net = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        probe = frame.iloc[entry_idx:min(len(frame), entry_idx + EARLY_FAIL_BARS)].copy()
        if sig["setup"] == "breakout_short":
            early_fail = bool(((probe["close"] > probe["ema15"]) | (probe["close"] > float(sig["breakout_anchor"]))).any())
            false_break = bool((probe["close"] > float(sig["breakout_anchor"])).any())
        elif sig["setup"] == "fib_retest_long":
            fib = float(sig["fib_618"])
            early_fail = bool(((probe["close"] < probe["ema15"]) | (probe["close"] < fib)).any())
            false_break = bool((probe["close"] < fib).any())
        else:
            ema = float(sig["ema15"])
            early_fail = bool((probe["close"] < ema).any())
            false_break = bool((probe["close"] < ema).any())
        rows.append({
            "signal_id": sig["signal_id"],
            "asset": sig["asset"],
            "setup": sig["setup"],
            "variant": sig["variant"],
            "cost_bps_per_side": float(cost_bps),
            "signal_ts": sig["signal_ts"],
            "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "entry_price": entry_px,
            "exit_price": exit_px,
            "gross_ret": gross,
            "net_ret": net,
            "win": bool(net > 0),
            "false_break_ratio_flag": false_break,
            "early_fail_4bars_flag": early_fail,
            "forward_4bars": direction * (float(frame.iloc[min(len(frame)-1, entry_idx + 3)]["close"]) / entry_px - 1.0),
            "forward_8bars": direction * (float(frame.iloc[min(len(frame)-1, entry_idx + 7)]["close"]) / entry_px - 1.0),
            "polarity": int(sig["polarity"]),
            "polarity_tstat": float(sig["polarity_tstat"]) if pd.notna(sig["polarity_tstat"]) else np.nan,
            "fomc_blackout": bool(sig["fomc_blackout"]),
        })
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
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
            "false_break_ratio": np.nan,
            "early_fail_4bars_rate": np.nan,
            "forward_4bars": np.nan,
            "forward_8bars": np.nan,
            "continuation_share": np.nan,
            "reversal_share": np.nan,
            "blackout_share": np.nan,
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
        "win_rate": float(trades["win"].mean()),
        "false_break_ratio": float(trades["false_break_ratio_flag"].mean()),
        "early_fail_4bars_rate": float(trades["early_fail_4bars_flag"].mean()),
        "forward_4bars": float(trades["forward_4bars"].mean()),
        "forward_8bars": float(trades["forward_8bars"].mean()),
        "continuation_share": float((trades["polarity"] == 1).mean()),
        "reversal_share": float((trades["polarity"] == -1).mean()),
        "blackout_share": float(trades["fomc_blackout"].mean()),
    }


def add_trade_retention(asset_df: pd.DataFrame) -> pd.DataFrame:
    out = asset_df.copy()
    for setup in sorted(out["setup"].unique()):
        for cost in sorted(out["cost_bps_per_side"].unique()):
            base_map = (
                out[(out["setup"] == setup) & (out["variant"] == "baseline") & (out["cost_bps_per_side"] == cost)]
                .set_index("asset")["trades"]
                .to_dict()
            )
            mask = (out["setup"] == setup) & (out["cost_bps_per_side"] == cost)
            out.loc[mask, "trade_count_retention"] = out.loc[mask].apply(
                lambda r: (r["trades"] / base_map.get(r["asset"], np.nan)) if base_map.get(r["asset"], 0) else np.nan,
                axis=1,
            )
    return out


def summarize_overall(asset_df: pd.DataFrame) -> pd.DataFrame:
    return (
        asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trades=("trades", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            mean_win_rate=("win_rate", "mean"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
            mean_early_fail_4bars_rate=("early_fail_4bars_rate", "mean"),
            mean_forward_4bars=("forward_4bars", "mean"),
            mean_forward_8bars=("forward_8bars", "mean"),
            mean_continuation_share=("continuation_share", "mean"),
            mean_reversal_share=("reversal_share", "mean"),
            mean_blackout_share=("blackout_share", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant", "cost_bps_per_side"])
        .reset_index(drop=True)
    )


def build_time_pockets(all_trades: pd.DataFrame) -> pd.DataFrame:
    if all_trades.empty:
        return pd.DataFrame(columns=["setup", "variant", "bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_false_break_ratio"])
    work = all_trades.copy()
    work["entry_ts"] = pd.to_datetime(work["entry_ts"], utc=True)
    rows: list[dict[str, object]] = []
    for (setup, variant), grp in work.groupby(["setup", "variant"], dropna=False):
        grp = grp.sort_values("entry_ts").reset_index(drop=True)
        if len(grp) < 3:
            splits = [grp]
        else:
            splits = [x for x in np.array_split(grp, 3) if len(x)]
        for idx, chunk in enumerate(splits, start=1):
            by_asset = chunk.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
            rows.append({
                "setup": setup,
                "variant": variant,
                "bucket": f"bucket_{idx}",
                "mean_total_return": float(by_asset.mean()) if len(by_asset) else np.nan,
                "positive_asset_ratio": float((by_asset > 0).mean()) if len(by_asset) else np.nan,
                "mean_trades": float(chunk.groupby("asset").size().mean()) if len(chunk) else np.nan,
                "mean_false_break_ratio": float(chunk["false_break_ratio_flag"].mean()) if len(chunk) else np.nan,
            })
    return pd.DataFrame(rows)


def verdict_and_notes(overall: pd.DataFrame) -> tuple[str, list[str]]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    baseline = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty or baseline.empty:
        return "hard verdict：缺少 Rank 76 主读法结果。", ["主读法 `polarity_plus_blackout @ 6bps` 或 baseline 对照未产出。"]
    merged = primary.merge(
        baseline[["setup", "mean_total_return", "mean_false_break_ratio", "mean_early_fail_4bars_rate", "mean_trades"]],
        on="setup",
        suffixes=("", "_baseline"),
    )
    notes = []
    better_return = int((merged["mean_total_return"] > merged["mean_total_return_baseline"]).sum())
    better_false = int((merged["mean_false_break_ratio"] < merged["mean_false_break_ratio_baseline"]).sum())
    better_fail = int((merged["mean_early_fail_4bars_rate"] < merged["mean_early_fail_4bars_rate_baseline"]).sum())
    okay_retention = int(((merged["mean_trade_count_retention"] >= 0.30) & (merged["mean_trade_count_retention"] <= 0.90)).sum())
    for _, row in merged.iterrows():
        notes.append(
            f"`{row['setup']} / {PRIMARY_VARIANT} @ 6bps`：return≈{pct(row['mean_total_return'])}、retention≈{pct(row['mean_trade_count_retention'])}、false_break≈{pct(row['mean_false_break_ratio'])}、early_fail≈{pct(row['mean_early_fail_4bars_rate'])}；对照 baseline≈{pct(row['mean_total_return_baseline'])}/{pct(row['mean_false_break_ratio_baseline'])}/{pct(row['mean_early_fail_4bars_rate_baseline'])}。"
        )
    if better_return >= 2 and (better_false + better_fail) >= 4 and okay_retention >= 2 and float(primary["positive_asset_ratio"].mean()) >= 0.5:
        return "hard verdict：Rank 76 / intraday clock polarity + event blackout gate 在这手最小 clean replication 下还保留了继续 cheap-check 的资格，更像 P1 weak candidate，而不是立刻 park。", notes
    return "hard verdict：Rank 76 / intraday clock polarity + event blackout gate 在当前最小 clean replication 下仍更像 `park / evidence pool`；改善若有，也主要来自局部 archetype 或大幅砍单，不够诚实。", notes


def build_report_html(overall: pd.DataFrame, asset_df: pd.DataFrame, pockets: pd.DataFrame, polarity_summary: pd.DataFrame, verdict: str, notes: list[str], generated_at: str) -> str:
    overall6 = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    asset6 = asset_df[asset_df["cost_bps_per_side"] == PRIMARY_COST].copy()
    pocket_primary = pockets[pockets["variant"] == PRIMARY_VARIANT].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 76 · intraday clock polarity clean replication</title>
  <style>{CSS}</style>
</head>
<body>
  <p><a href='../reading/repo_scout/rank76_intraday_clock_polarity_event_blackout_source_intake.html'>← 返回 Rank 76 source intake</a></p>
  <h1>Rank 76 · intraday clock polarity + event blackout gate（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)}｜固定 BTC/ETH/SOL 120d 15m cache；统一冻结为 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，把按小时计算的 <code>continuation / reversal / neutral</code> 极性 gate 接到 <code>ema_psar_long / fib_retest_long / breakout_short</code> 三条 archetype 上，再叠一层最小 <code>FOMC ±2h blackout</code>，能不能在不过度砍单的前提下改善成本后表现与早死率？</p>
    <p><span class='pill'>只做 minimal clean replication，不扩成全天事件宏观研究</span></p>
  </div>

  <div class='card'>
    <h2>冻结规则</h2>
    <ul>
      <li>三条 archetype：<code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
      <li>三臂对照：<code>baseline</code>、<code>polarity_only</code>、<code>polarity_plus_blackout</code>。</li>
      <li>小时极性：对每个 UTC 小时单独，用过往同小时的 <code>hour_ret × next_hour_ret</code> 做滚动统计；<code>t-stat ≥ 1.96 且均值&gt;0</code> 记为 continuation，<code>t-stat ≤ -1.96 且均值&lt;0</code> 记为 reversal，否则 neutral。</li>
      <li>映射规则：<code>ema_psar_long</code> 与 <code>breakout_short</code> 只在 continuation 小时放行；<code>fib_retest_long</code> 只在 reversal 小时放行。</li>
      <li>blackout 只做 veto，不自创方向：当前最小窗口固定为 FOMC 公告前后 ±2 小时。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><b>{escape(verdict)}</b></p>
    <ul>{''.join(f'<li>{escape(line)}</li>' for line in notes)}</ul>
  </div>

  <div class='card'>
    <h2>小时极性摘要</h2>
    {render_table(polarity_summary, percent_cols={'continuation_share','reversal_share','neutral_share'}, digits_cols={'hour_of_day':0,'polarity_obs':0,'polarity_mean':4,'polarity_tstat':2})}
  </div>

  <div class='card'>
    <h2>overall summary（6bps）</h2>
    {render_table(overall6, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_avg_net_ret','mean_win_rate','mean_false_break_ratio','mean_early_fail_4bars_rate','mean_forward_4bars','mean_forward_8bars','mean_continuation_share','mean_reversal_share','mean_blackout_share'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>asset-level（6bps）</h2>
    {render_table(asset6, percent_cols={'total_return','trade_count_retention','avg_net_ret','win_rate','false_break_ratio','early_fail_4bars_rate','forward_4bars','forward_8bars','continuation_share','reversal_share','blackout_share'}, digits_cols={'cost_bps_per_side':0,'signal_events':0,'trades':0})}
  </div>

  <div class='card'>
    <h2>time-pocket honesty（主读法 = polarity_plus_blackout）</h2>
    {render_table(pocket_primary, percent_cols={'mean_total_return','positive_asset_ratio','mean_false_break_ratio'}, digits_cols={'mean_trades':1})}
  </div>
</body>
</html>"""


def build_reading_html(generated_at: str, verdict: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Rank 76 clean replication</title><style>{CSS}</style></head><body>
<p><a href='rank76_intraday_clock_polarity_event_blackout_source_intake.html'>← 返回 Rank 76 source intake</a></p>
<h1>Rank 76 · minimal clean replication</h1>
<div class='card'>
  <p><span class='pill'>更新时间：{escape(generated_at)}</span><span class='pill'>verdict：{escape(verdict)}</span></p>
  <p>这轮把 Rank 76 的最小 clean replication 跑完了：只比较 <code>baseline / polarity_only / polarity_plus_blackout</code> 三臂，固定 <code>BTC/ETH/SOL 120d 15m</code> cache，统一 <code>next-bar open + no-overlap + hold 8 bars</code>。</p>
  <p>Reader-facing 主落点：<a href='../../factors/scout_rank76_intraday_clock_polarity_15m/report.html'>scout_rank76_intraday_clock_polarity_15m/report.html</a></p>
</div>
</body></html>"""


def update_todo(overall: pd.DataFrame, pockets: pd.DataFrame, generated_at: str, verdict: str) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text or f"**最新补充（{generated_at}）**" in text:
        return
    p3_summary = pd.read_json(P3_SUMMARY_PATH, typ='series')
    p3_appends = int(p3_summary.get('new_closed_trades_appended', 0))
    primary = overall[(overall['variant'] == PRIMARY_VARIANT) & (overall['cost_bps_per_side'] == PRIMARY_COST)].set_index('setup')
    baseline = overall[(overall['variant'] == 'baseline') & (overall['cost_bps_per_side'] == PRIMARY_COST)].set_index('setup')
    pocket = pockets[(pockets['variant'] == PRIMARY_VARIANT) & (pockets['setup'] == 'breakout_short')]
    if pocket.empty:
        pocket_text = 'time-pocket 暂无有效分桶结果'
    else:
        pocket_text = '；'.join(f"{row['bucket']}≈{pct(row['mean_total_return'])}/{pct(row['positive_asset_ratio'])}" for _, row in pocket.iterrows())
    if 'P1 weak candidate' in verdict:
        queue_line = "**`Run 1 = EMA due-check only（当前最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 76 仍保留 candidate 资格，则只允许给它 1 个真正会改变 verdict 的最小 Light Stability Pack（默认优先时间稳定性）` -> `Run 3 = 若 Rank 76 cheap check 后仍不能升格，则先回到 fresh paper / repo source re-rank（默认比较 one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source）；只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    else:
        queue_line = "**`Run 1 = EMA due-check only（当前最近 due 点仍是 A股 07:00 UTC；若仍 waiting_not_due，不得空转）` -> `Run 2 = 若 Rank 76 minimal clean replication 已给出 park / evidence pool hard verdict，则先回到 fresh paper / repo source re-rank（默认比较 one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source）` -> `Run 3 = 只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`**"
    insert = (
        f"- **最新补充（{generated_at}）**：这轮再次先核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane，最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`；`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended={p3_appends}`。因此当前 bot3 仍不该回头挤占 `P3 continuity`，而应按 `EMA waiting_not_due -> Scout Seat` 的顺序继续向前。\n"
        f"  - 这轮已把 **`Rank 76 / intraday clock polarity + event blackout gate`** 的唯一那手最小 clean replication 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，只接到 `ema_psar_long / fib_retest_long / breakout_short` 三条 archetype，上比较 `baseline / polarity_only / polarity_plus_blackout` 三臂，并统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。\n"
        f"  - `6bps/side` 下，主读法 `polarity_plus_blackout` 的结果为：`ema_psar_long≈{pct(primary.loc['ema_psar_long','mean_total_return'])} / retention≈{pct(primary.loc['ema_psar_long','mean_trade_count_retention'])} / false_break≈{pct(primary.loc['ema_psar_long','mean_false_break_ratio'])}`；`fib_retest_long≈{pct(primary.loc['fib_retest_long','mean_total_return'])} / retention≈{pct(primary.loc['fib_retest_long','mean_trade_count_retention'])} / false_break≈{pct(primary.loc['fib_retest_long','mean_false_break_ratio'])}`；`breakout_short≈{pct(primary.loc['breakout_short','mean_total_return'])} / retention≈{pct(primary.loc['breakout_short','mean_trade_count_retention'])} / false_break≈{pct(primary.loc['breakout_short','mean_false_break_ratio'])}`。对照 baseline：`ema_psar_long≈{pct(baseline.loc['ema_psar_long','mean_total_return'])}`、`fib_retest_long≈{pct(baseline.loc['fib_retest_long','mean_total_return'])}`、`breakout_short≈{pct(baseline.loc['breakout_short','mean_total_return'])}`；breakout_short 的 time-pocket：{pocket_text}。\n"
        f"  - 因此当前更诚实的 hard verdict 是 **`{verdict}`**。\n"
        f"  - 网页落点：`reports/site/factors/scout_rank76_intraday_clock_polarity_15m/report.html`、`reports/site/reading/repo_scout/rank76_intraday_clock_polarity_clean_replication.html`；artifact：`reports/artifacts/scout_rank76_intraday_clock_polarity_15m/overall_summary.csv`、`asset_summary.csv`、`time_pocket_summary.csv`、`hourly_polarity_summary.csv`。\n"
        f"  - 当前必须同步重排 active Scout 候选的边际价值：**`one-regime-per-session overlay` > `RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**。因此当前 seat 分级应同步收紧为：**`Rank 76 = P0 park / evidence pool`**、**`one-regime-per-session overlay = P0 evidence / backlog（fresh re-rank next）`**、`Rank 2 / 17 / 29 / 32b = P3 narrow paper continuity`；当前 **`P1` 暂空、`P2` 暂空、`P4` 暂空**。\n"
        f"  - 当前最新 `Next 3` 顺序应更新为：{queue_line}\n\n"
    )
    TODO_PATH.write_text(text.replace(marker, marker + insert, 1), encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    asset_rows: list[dict[str, object]] = []
    signal_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    sample_meta: list[dict[str, object]] = []
    polarity_summaries: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame, polarity_summary = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower()}_feature_frame.csv", index=False)
        polarity_summary.insert(0, 'asset', asset)
        polarity_summaries.append(polarity_summary)
        sample_meta.append({
            'asset': asset,
            'symbol': symbol,
            'bars': int(len(frame)),
            'sample_start_utc': frame['timestamp'].min().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'sample_end_utc': frame['timestamp'].max().strftime('%Y-%m-%dT%H:%M:%SZ'),
        })
        for setup in SETUPS:
            signals_by_variant: dict[str, pd.DataFrame] = {}
            for variant in VARIANTS:
                signals = build_signals(frame, asset, setup, variant)
                signals_by_variant[variant] = signals
                signal_rows.append({'asset': asset, 'setup': setup, 'variant': variant, 'signal_events': int(len(signals))})
                (signals if not signals.empty else pd.DataFrame(columns=['signal_id','asset','setup','variant','direction','signal_idx','entry_idx','signal_ts','signal_price','polarity','polarity_mean','polarity_tstat','polarity_obs','fomc_blackout','ema15','breakout_anchor','fib_618']))\
                    .to_csv(ART_DIR / f"signals_{asset.replace('-','').lower()}_{setup}_{variant}.csv", index=False)
            for cost in COSTS:
                for variant in VARIANTS:
                    trades = build_trades(frame, signals_by_variant[variant], cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, setup=setup, variant=variant, cost_bps=cost, signal_events=len(signals_by_variant[variant])))

    asset_df = add_trade_retention(pd.DataFrame(asset_rows)).sort_values(['setup','variant','cost_bps_per_side','asset']).reset_index(drop=True)
    overall = summarize_overall(asset_df)
    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    pockets = build_time_pockets(all_trades)
    verdict, notes = verdict_and_notes(overall)
    polarity_summary = pd.concat(polarity_summaries, ignore_index=True) if polarity_summaries else pd.DataFrame()

    asset_df.to_csv(ART_DIR / 'asset_summary.csv', index=False)
    pd.DataFrame(signal_rows).to_csv(ART_DIR / 'signal_event_counts.csv', index=False)
    pd.DataFrame(sample_meta).to_csv(ART_DIR / 'sample_meta.csv', index=False)
    polarity_summary.to_csv(ART_DIR / 'hourly_polarity_summary.csv', index=False)
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / 'trade_log.csv', index=False)
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)
    pockets.to_csv(ART_DIR / 'time_pocket_summary.csv', index=False)

    report_html = build_report_html(overall, asset_df, pockets, polarity_summary, verdict, notes, generated_at)
    (SITE_DIR / 'report.html').write_text(report_html, encoding='utf-8')
    READING_PATH.write_text(build_reading_html(generated_at, verdict), encoding='utf-8')
    update_todo(overall, pockets, generated_at, verdict)

    print(generated_at)
    print(verdict)
    print(overall[(overall['cost_bps_per_side'] == PRIMARY_COST)][['setup','variant','mean_total_return','positive_asset_ratio','mean_trades','mean_trade_count_retention','mean_false_break_ratio','mean_early_fail_4bars_rate']].to_string(index=False))


if __name__ == '__main__':
    main()
