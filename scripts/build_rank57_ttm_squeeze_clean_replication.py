#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank57_ttm_squeeze_release_regime_gate_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank57_ttm_squeeze_release_regime_gate_15m"
READING_DIR = ROOT / "reports" / "site" / "reading" / "repo_scout"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["base", "no_sqz_on_veto", "release_recent_gate", "release_recent_gate_momentum_sign"]
RELEASE_WINDOWS = [1, 2, 3, 4]
COSTS = [6.0, 10.0]
PRIMARY_COST = 6.0
PRIMARY_VARIANT = "release_recent_gate"
HOLD_BARS = 8
WHIP_LOOKAHEADS = [2, 4]


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


def rolling_linreg_last(series: pd.Series, window: int = 20) -> pd.Series:
    x = np.arange(window, dtype=float)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()

    def _calc(vals: np.ndarray) -> float:
        y = np.asarray(vals, dtype=float)
        y_mean = y.mean()
        slope = ((x - x_mean) * (y - y_mean)).sum() / x_var
        intercept = y_mean - slope * x_mean
        return float(intercept + slope * x[-1])

    return series.rolling(window, min_periods=window).apply(_calc, raw=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
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

    basis = df["close"].rolling(20, min_periods=20).mean()
    std20 = df["close"].rolling(20, min_periods=20).std(ddof=0)
    upper_bb = basis + 2.0 * std20
    lower_bb = basis - 2.0 * std20
    kc_basis = df["close"].ewm(span=20, adjust=False).mean()
    atr20 = compute_atr(df, period=20)
    upper_kc = kc_basis + 1.5 * atr20
    lower_kc = kc_basis - 1.5 * atr20
    df["sqz_on"] = ((lower_bb > lower_kc) & (upper_bb < upper_kc)).fillna(False)
    df["sqz_off"] = (~df["sqz_on"]).fillna(False)
    linreg_mid = rolling_linreg_last(df["close"] - ((df["high"].rolling(20, min_periods=20).max() + df["low"].rolling(20, min_periods=20).min()) / 2.0), 20)
    df["linreg_momentum"] = linreg_mid
    df["momentum_sign"] = np.sign(df["linreg_momentum"].fillna(0.0))

    for window in RELEASE_WINDOWS:
        recent_sqz = pd.concat([df["sqz_on"].shift(i).fillna(False) for i in range(1, window + 1)], axis=1).any(axis=1)
        df[f"release_recent_{window}"] = (df["sqz_off"] & recent_sqz).fillna(False)

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


def build_signal_frame(frame: pd.DataFrame, asset: str, symbol: str, setup: str) -> pd.DataFrame:
    sig = frame[setup_signal_col(setup)] & ~frame[setup_signal_col(setup)].shift(1).fillna(False)
    rows: list[dict[str, object]] = []
    last_exit = -1
    direction = direction_for_setup(setup)
    for idx in range(40, len(frame) - 2):
        if idx <= last_exit or not bool(sig.iloc[idx]):
            continue
        row = frame.iloc[idx]
        rows.append(
            {
                "asset": asset,
                "symbol": symbol,
                "setup": setup,
                "direction": direction,
                "signal_idx": idx,
                "entry_idx": idx + 1,
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "signal_price": float(row["close"]),
                "atr14": float(row["atr14"]),
                "sqz_on": bool(row["sqz_on"]),
                "release_recent_1": bool(row["release_recent_1"]),
                "release_recent_2": bool(row["release_recent_2"]),
                "release_recent_3": bool(row["release_recent_3"]),
                "release_recent_4": bool(row["release_recent_4"]),
                "momentum_sign": float(row["momentum_sign"]),
            }
        )
        last_exit = idx + HOLD_BARS
    return pd.DataFrame(rows)


def release_gate(sig: pd.Series, window: int = 4) -> bool:
    return bool(sig.get(f"release_recent_{window}", False))


def variant_allowed(sig: pd.Series, variant: str) -> bool:
    direction = int(sig["direction"])
    if variant == "base":
        return True
    if variant == "no_sqz_on_veto":
        return not bool(sig["sqz_on"])
    if variant == "release_recent_gate":
        return release_gate(sig, 4)
    if variant == "release_recent_gate_momentum_sign":
        return release_gate(sig, 4) and (direction * float(sig["momentum_sign"]) > 0)
    raise ValueError(variant)


def detect_whipsaw(frame: pd.DataFrame, signal_idx: int, direction: int, signal_price: float, bars: int) -> int:
    last = min(len(frame) - 1, signal_idx + bars)
    for j in range(signal_idx + 1, last + 1):
        close = float(frame.iloc[j]["close"])
        if direction > 0 and close < signal_price:
            return 1
        if direction < 0 and close > signal_price:
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
        if entry_idx >= len(frame):
            continue
        exit_idx = min(len(frame) - 1, entry_idx + HOLD_BARS - 1)
        direction = int(sig["direction"])
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["close"])
        gross_ret = direction * ((exit_px / entry_px) - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        ft2_idx = min(len(frame) - 1, entry_idx + 1)
        ft4_idx = min(len(frame) - 1, entry_idx + 3)
        ft2 = direction * ((float(frame.iloc[ft2_idx]["close"]) / entry_px) - 1.0)
        ft4 = direction * ((float(frame.iloc[ft4_idx]["close"]) / entry_px) - 1.0)
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
                "follow_through_2bars": ft2,
                "follow_through_4bars": ft4,
                "whipsaw_2bars": detect_whipsaw(frame, int(sig["signal_idx"]), direction, float(sig["signal_price"]), 2),
                "whipsaw_4bars": detect_whipsaw(frame, int(sig["signal_idx"]), direction, float(sig["signal_price"]), 4),
                "sqz_on": bool(sig["sqz_on"]),
                "release_recent_4": bool(sig["release_recent_4"]),
                "momentum_sign": float(sig["momentum_sign"]),
            }
        )
    return pd.DataFrame(rows), admitted


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
            "win_rate": np.nan,
            "whipsaw_2bars_rate": np.nan,
            "whipsaw_4bars_rate": np.nan,
            "follow_through_2bars": np.nan,
            "follow_through_4bars": np.nan,
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
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "whipsaw_2bars_rate": float(trades["whipsaw_2bars"].mean()),
        "whipsaw_4bars_rate": float(trades["whipsaw_4bars"].mean()),
        "follow_through_2bars": float(trades["follow_through_2bars"].mean()),
        "follow_through_4bars": float(trades["follow_through_4bars"].mean()),
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
    grouped = df.groupby(["setup", "variant", "bucket", "asset"], dropna=False)
    for (setup, variant, bucket_name, asset), part in grouped:
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


def build_parameter_summary(all_signals: pd.DataFrame, frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for window in RELEASE_WINDOWS:
        for use_momentum in [False, True]:
            variant_name = f"release_{window}bars" + ("_momentum" if use_momentum else "")
            asset_rows: list[dict[str, object]] = []
            for asset in ASSETS:
                frame = frames[asset]
                for setup in SETUPS:
                    sigs = all_signals[(all_signals["asset"] == asset) & (all_signals["setup"] == setup)].copy().reset_index(drop=True)
                    if sigs.empty:
                        continue
                    selected = sigs[sigs[f"release_recent_{window}"]].copy()
                    if use_momentum:
                        selected = selected[(selected["direction"] * selected["momentum_sign"]) > 0]
                    trades, admitted = build_trades(frame, selected, "base", PRIMARY_COST)
                    asset_rows.append(
                        summarize_asset(
                            trades,
                            asset=asset,
                            setup=setup,
                            variant=variant_name,
                            cost_bps=PRIMARY_COST,
                            base_signals=int(len(sigs)),
                            admitted_signals=int(admitted),
                        )
                    )
            if not asset_rows:
                continue
            asset_df = add_retentions(pd.DataFrame(asset_rows))
            overall = (
                asset_df.groupby(["setup", "variant", "cost_bps_per_side"], dropna=False)
                .agg(
                    mean_total_return=("total_return", "mean"),
                    positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
                    mean_trades=("trades", "mean"),
                    mean_trade_count_retention=("trade_count_retention", "mean"),
                    mean_whipsaw_2bars_rate=("whipsaw_2bars_rate", "mean"),
                    mean_whipsaw_4bars_rate=("whipsaw_4bars_rate", "mean"),
                )
                .reset_index()
            )
            for _, r in overall.iterrows():
                rows.append(
                    {
                        "release_window": window,
                        "uses_momentum_sign": use_momentum,
                        "setup": r["setup"],
                        "variant": variant_name,
                        "mean_total_return": float(r["mean_total_return"]),
                        "positive_asset_ratio": float(r["positive_asset_ratio"]),
                        "mean_trades": float(r["mean_trades"]),
                        "mean_trade_count_retention": float(r["mean_trade_count_retention"]),
                        "mean_whipsaw_2bars_rate": float(r["mean_whipsaw_2bars_rate"]),
                        "mean_whipsaw_4bars_rate": float(r["mean_whipsaw_4bars_rate"]),
                    }
                )
    return pd.DataFrame(rows).sort_values(["setup", "uses_momentum_sign", "release_window"]).reset_index(drop=True)


def build_setup_compare(overall: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    primary = overall[overall["cost_bps_per_side"] == PRIMARY_COST].copy()
    for setup in SETUPS:
        base = primary[(primary["setup"] == setup) & (primary["variant"] == "base")]
        veto = primary[(primary["setup"] == setup) & (primary["variant"] == "no_sqz_on_veto")]
        release = primary[(primary["setup"] == setup) & (primary["variant"] == "release_recent_gate")]
        release_m = primary[(primary["setup"] == setup) & (primary["variant"] == "release_recent_gate_momentum_sign")]
        rows.append(
            {
                "setup": setup,
                "base_return": float(base.iloc[0]["mean_total_return"]) if not base.empty else np.nan,
                "veto_return": float(veto.iloc[0]["mean_total_return"]) if not veto.empty else np.nan,
                "release_return": float(release.iloc[0]["mean_total_return"]) if not release.empty else np.nan,
                "release_momentum_return": float(release_m.iloc[0]["mean_total_return"]) if not release_m.empty else np.nan,
                "base_whipsaw_2": float(base.iloc[0]["mean_whipsaw_2bars_rate"]) if not base.empty else np.nan,
                "release_whipsaw_2": float(release.iloc[0]["mean_whipsaw_2bars_rate"]) if not release.empty else np.nan,
                "release_momentum_whipsaw_2": float(release_m.iloc[0]["mean_whipsaw_2bars_rate"]) if not release_m.empty else np.nan,
                "release_retention": float(release.iloc[0]["mean_trade_count_retention"]) if not release.empty else np.nan,
                "release_momentum_retention": float(release_m.iloc[0]["mean_trade_count_retention"]) if not release_m.empty else np.nan,
                "release_positive_asset_ratio": float(release.iloc[0]["positive_asset_ratio"]) if not release.empty else np.nan,
                "release_momentum_positive_asset_ratio": float(release_m.iloc[0]["positive_asset_ratio"]) if not release_m.empty else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_verdict(setup_compare: pd.DataFrame, parameter_summary: pd.DataFrame) -> tuple[str, str, str]:
    wins = 0
    clean_wins = 0
    for _, r in setup_compare.iterrows():
        improved = (
            pd.notna(r["release_return"]) and pd.notna(r["base_return"]) and pd.notna(r["release_retention"])
            and pd.notna(r["release_whipsaw_2"]) and pd.notna(r["base_whipsaw_2"])
            and float(r["release_retention"]) >= 0.35
            and float(r["release_positive_asset_ratio"]) >= (1/3)
            and (float(r["release_return"]) > float(r["base_return"]) or float(r["release_whipsaw_2"]) < float(r["base_whipsaw_2"]) - 0.03)
        )
        if improved:
            wins += 1
            if float(r["release_positive_asset_ratio"]) >= (2/3):
                clean_wins += 1
    stable_params = False
    if not parameter_summary.empty:
        param_primary = parameter_summary[(parameter_summary["uses_momentum_sign"] == False)]
        stable_slice = param_primary[
            (param_primary["mean_trade_count_retention"] >= 0.25)
            & (param_primary["positive_asset_ratio"] >= (1/3))
            & (param_primary["mean_whipsaw_2bars_rate"] <= 0.75)
        ]
        stable_params = len(stable_slice) >= 3
    headline = "；".join(
        f"{r['setup']}: base≈{pct(r['base_return'])} / veto≈{pct(r['veto_return'])} / release≈{pct(r['release_return'])} / release+mom≈{pct(r['release_momentum_return'])}"
        for _, r in setup_compare.iterrows()
    )
    if wins >= 2 and stable_params and clean_wins >= 1:
        return (
            "P2 paper candidate / narrow paper admission queue",
            headline,
            "这次最小 clean replication 已经给出足够诚实的 shared gate 味道：release gate 至少在两条 archetype 上不是纯靠砍样本少亏，跨资产与 release-window 参数也没一碰就碎，因此更适合先进入 paper candidate pool，而不是继续停在研究态。",
        )
    if wins >= 1:
        return (
            "P1 weak candidate / evidence pool",
            headline,
            "最小 clean replication 至少说明 TTM squeeze release 不是纯图像幻觉：它在部分 archetype 上能减少 2-bar 假启动或少亏，但当前改善还不够统一，且 release-window / momentum 约束仍有样本变薄问题，所以先保留为 P1 证据池候选更诚实。",
        )
    return (
        "park / evidence pool",
        headline,
        "这次最小 clean replication 更像在证明：TTM squeeze release 作为 shared avoid-chop / expansion gate 目前主要靠砍样本，跨 setup 与跨资产都还不够统一，不该继续占默认 Scout 主资源位。",
    )


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, pockets: pd.DataFrame, params: pd.DataFrame, compare: pd.DataFrame, verdict: str, headline: str, reason: str, generated_at: str) -> str:
    overall_view = overall[[
        "setup",
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "mean_trade_count_retention",
        "mean_whipsaw_2bars_rate",
        "mean_whipsaw_4bars_rate",
        "mean_follow_through_2bars",
        "mean_follow_through_4bars",
    ]].copy()
    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == PRIMARY_COST][[
        "asset",
        "setup",
        "variant",
        "trades",
        "trade_count_retention",
        "signal_retention",
        "total_return",
        "whipsaw_2bars_rate",
        "whipsaw_4bars_rate",
    ]].copy()
    compare_view = compare[[
        "setup",
        "base_return",
        "veto_return",
        "release_return",
        "release_momentum_return",
        "base_whipsaw_2",
        "release_whipsaw_2",
        "release_momentum_whipsaw_2",
        "release_retention",
        "release_momentum_retention",
        "release_positive_asset_ratio",
        "release_momentum_positive_asset_ratio",
    ]].copy()
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 57 · TTM squeeze release regime gate clean replication</title>
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
  <p><a href='../../reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_source_intake.html'>← 返回 source intake</a></p>
  <h1>Rank 57 · TTM squeeze release regime gate（minimal clean replication）</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 固定 BTC/ETH/SOL 120d 15m cache；统一冻结到 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>

  <div class='card'>
    <h2>这轮只回答一个问题</h2>
    <p>当 <code>EMA = waiting_not_due</code> 时，Rank 57 只拿 1 次最小预算：<b>TTM squeeze 的 <code>not sqz_on</code> / <code>release_recent</code> / <code>momentum_sign</code> 这层 shared regime gate</b>，能不能在不过度砍样本的前提下，让当前 desk 三条 archetype 少一点 2~4 bar 假启动，或者至少更少亏？</p>
    <ul>
      <li><b>base setup：</b><code>ema_psar_long</code>、<code>fib_retest_long</code>、<code>breakout_short</code>。</li>
      <li><b>overlay 变体：</b><code>base</code>、<code>no_sqz_on_veto</code>、<code>release_recent_gate</code>、<code>release_recent_gate_momentum_sign</code>。</li>
      <li><b>shared 规则：</b>overlay 只能 veto / 延后，不单独发明 entry；release 语义只由 <code>BB(20,2)</code> vs <code>KC(20,1.5*ATR)</code> 的 <code>sqz_on -> sqz_off</code> 状态生成。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>硬结论</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>release gate setup compare（6bps）</h2>
    {render_table(compare_view, percent_cols={'base_return','veto_return','release_return','release_momentum_return','base_whipsaw_2','release_whipsaw_2','release_momentum_whipsaw_2','release_retention','release_momentum_retention','release_positive_asset_ratio','release_momentum_positive_asset_ratio'}, digits_cols={})}
  </div>

  <div class='card'>
    <h2>overall summary</h2>
    {render_table(overall_view, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_whipsaw_2bars_rate','mean_whipsaw_4bars_rate','mean_follow_through_2bars','mean_follow_through_4bars'}, digits_cols={'cost_bps_per_side':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>primary cost（6bps）asset-level</h2>
    {render_table(asset_view, percent_cols={'trade_count_retention','signal_retention','total_return','whipsaw_2bars_rate','whipsaw_4bars_rate'}, digits_cols={'trades':0})}
  </div>

  <div class='card'>
    <h2>Light Stability Pack · time stability</h2>
    {render_table(pockets, percent_cols={'mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>Light Stability Pack · parameter stability（release 1~4 bars）</h2>
    {render_table(params, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_count_retention','mean_whipsaw_2bars_rate','mean_whipsaw_4bars_rate'}, digits_cols={'release_window':0,'mean_trades':1})}
  </div>
</body>
</html>
"""


def update_todo(compare: pd.DataFrame, verdict: str, generated_at: str) -> None:
    text = TODO_PATH.read_text(encoding='utf-8')
    marker = "\n### Next 3 bot3 runs（当前默认执行顺序）"
    if marker not in text:
        raise RuntimeError('Next 3 marker not found in TODO.md')
    if f"**最新补充（{generated_at}）**" in text:
        return
    compare = compare.set_index('setup')
    row_ema = compare.loc['ema_psar_long']
    row_fib = compare.loc['fib_retest_long']
    row_short = compare.loc['breakout_short']
    insert_block = f"""
- **最新补充（{generated_at}）**：这轮再次先核对 `Run 1 / EMA due-check` 与 `P3` 托管位状态：`ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 没有新的 `due-now / overdue` lane（最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`），而 `manual_narrow_paper_last_run_summary.json` 继续是 `new_closed_trades_appended=0`。因此这轮不该误把 `waiting_not_due` 当成整桌等待，合法主动作仍是 **`Run 2 / Rank 57 minimal clean replication`**。
  - 这轮已把 `Rank 57 / TTM squeeze release regime gate` 的唯一那手 **最小 clean replication** 跑完：固定复用 `BTC/ETH/SOL 120d 15m` cache，在三条 base archetype（`ema_psar_long`、`fib_retest_long`、`breakout_short`）上比较 `base`、`no_sqz_on_veto`、`release_recent_gate`、`release_recent_gate_momentum_sign` 四臂；执行统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**。
  - `6bps/side` 下的 setup-level 结果已冻结为：`ema_psar_long` 从 `base≈{pct(row_ema['base_return'])}` 到 `veto≈{pct(row_ema['veto_return'])}`、`release≈{pct(row_ema['release_return'])}`、`release+mom≈{pct(row_ema['release_momentum_return'])}`；`fib_retest_long` 从 `base≈{pct(row_fib['base_return'])}` 到 `veto≈{pct(row_fib['veto_return'])}`、`release≈{pct(row_fib['release_return'])}`、`release+mom≈{pct(row_fib['release_momentum_return'])}`；`breakout_short` 从 `base≈{pct(row_short['base_return'])}` 到 `veto≈{pct(row_short['veto_return'])}`、`release≈{pct(row_short['release_return'])}`、`release+mom≈{pct(row_short['release_momentum_return'])}`。
  - 同轮顺手完成了 2 个轻量稳定性切片：`time stability`（按时间三分桶）与 `parameter stability`（`release 1~4 bars`，并对比是否叠 `momentum_sign`）。因此当前更诚实的 hard verdict 应冻结为：**`Rank 57 / TTM squeeze release regime gate = {verdict}`**。
  - reader-facing 落点：`reports/site/factors/scout_rank57_ttm_squeeze_release_regime_gate_15m/report.html`、`reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_clean_replication.html`；artifact：`reports/artifacts/scout_rank57_ttm_squeeze_release_regime_gate_15m/overall_summary.csv`、`parameter_stability_summary.csv`。
  - 排班含义：当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 Rank 57 verdict 仍不足以升到下一层，则按 7.10 再认领 1 条 fresh paper/repo source（优先 5m / 15m crypto）` -> `Run 3 = 只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`**。"""
    text = text.replace(marker, "\n" + insert_block + marker, 1)
    TODO_PATH.write_text(text, encoding='utf-8')


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
        raise RuntimeError('no signals formed for Rank 57 clean replication')
    all_signals.to_csv(ART_DIR / 'signal_windows.csv', index=False)

    trade_frames: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame = frames[asset]
        for setup in SETUPS:
            sigs = all_signals[(all_signals['asset'] == asset) & (all_signals['setup'] == setup)].copy().reset_index(drop=True)
            base_signals = int(len(sigs))
            for variant in VARIANTS:
                admitted_count = int(sigs.apply(lambda r: variant_allowed(r, variant), axis=1).sum()) if not sigs.empty else 0
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
                            admitted_signals=admitted_count if variant != 'base' else admitted,
                        )
                    )

    all_trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    if not all_trades.empty:
        all_trades.to_csv(ART_DIR / 'trade_log.csv', index=False)

    asset_summary = add_retentions(pd.DataFrame(asset_rows)).sort_values(['setup', 'variant', 'cost_bps_per_side', 'asset']).reset_index(drop=True)
    asset_summary.to_csv(ART_DIR / 'asset_summary.csv', index=False)

    overall = (
        asset_summary.groupby(['setup', 'variant', 'cost_bps_per_side'], dropna=False)
        .agg(
            mean_total_return=('total_return', 'mean'),
            positive_asset_ratio=('total_return', lambda s: float((s > 0).mean())),
            mean_trades=('trades', 'mean'),
            mean_trade_count_retention=('trade_count_retention', 'mean'),
            mean_signal_retention=('signal_retention', 'mean'),
            mean_whipsaw_2bars_rate=('whipsaw_2bars_rate', 'mean'),
            mean_whipsaw_4bars_rate=('whipsaw_4bars_rate', 'mean'),
            mean_follow_through_2bars=('follow_through_2bars', 'mean'),
            mean_follow_through_4bars=('follow_through_4bars', 'mean'),
            mean_avg_net_ret=('avg_net_ret', 'mean'),
        )
        .reset_index()
        .sort_values(['setup', 'variant', 'cost_bps_per_side'])
        .reset_index(drop=True)
    )
    overall.to_csv(ART_DIR / 'overall_summary.csv', index=False)

    pockets = build_time_pockets(all_trades)
    pockets.to_csv(ART_DIR / 'time_pocket_summary.csv', index=False)

    parameter_summary = build_parameter_summary(all_signals, frames)
    parameter_summary.to_csv(ART_DIR / 'parameter_stability_summary.csv', index=False)

    setup_compare = build_setup_compare(overall)
    setup_compare.to_csv(ART_DIR / 'setup_compare.csv', index=False)

    verdict, headline, reason = build_verdict(setup_compare, parameter_summary)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    pd.DataFrame([
        {
            'generated_at_utc': generated_at,
            'candidate_id': 'rank57_ttm_squeeze_release_regime_gate_15m',
            'hard_verdict': verdict,
            'headline': headline,
            'reason': reason,
        }
    ]).to_csv(ART_DIR / 'meta.csv', index=False)

    html = build_html(overall, asset_summary, pockets, parameter_summary, setup_compare, verdict, headline, reason, generated_at)
    (SITE_DIR / 'report.html').write_text(html, encoding='utf-8')
    (READING_DIR / 'rank57_ttm_squeeze_release_regime_gate_clean_replication.html').write_text(html, encoding='utf-8')

    update_todo(setup_compare, verdict, generated_at)

    print(f'verdict={verdict}')
    print(headline)


if __name__ == '__main__':
    main()
