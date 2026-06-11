#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank130_crossmarket_leader_impulse_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank130_crossmarket_leader_impulse_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank130_crossmarket_leader_impulse_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["breakout_short", "fib_retest_long", "ema_psar_long"]
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
ATR_PERIOD = 14
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
EPS = 1e-12
LOW_Z = 0.5
HIGH_Z = 1.0
LEADER_RATIO = 1.2

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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_base_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ret1"] = df["close"].pct_change()
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["psar"] = compute_psar(df)
    df["atr14"] = compute_atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["prior20_high"] = df["high"].rolling(20, min_periods=20).max().shift(1)
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


def add_crossmarket_features(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    aligned = []
    for asset, df in frames.items():
        aligned.append(df[["timestamp", "ret1"]].rename(columns={"ret1": asset}))
    merged = aligned[0]
    for other in aligned[1:]:
        merged = merged.merge(other, on="timestamp", how="inner")
    merged = merged.sort_values("timestamp").reset_index(drop=True)

    out: dict[str, pd.DataFrame] = {}
    for asset, df in frames.items():
        peer_cols = [a for a in ASSETS if a != asset]
        feat = merged[["timestamp"] + peer_cols + [asset]].copy()
        feat["leader_ret"] = feat[peer_cols].mean(axis=1)
        feat["leader_same_dir"] = np.sign(feat[peer_cols[0]]) == np.sign(feat[peer_cols[1]])
        feat["leader_abs_mean"] = feat[peer_cols].abs().mean(axis=1)
        feat["leader_strength_ok"] = feat["leader_abs_mean"] > (LEADER_RATIO * feat[asset].abs())
        feat["leader_valid"] = feat["leader_same_dir"] & feat["leader_strength_ok"]
        abs_mean = feat["leader_ret"].abs().rolling(96, min_periods=96).mean()
        abs_std = feat["leader_ret"].abs().rolling(96, min_periods=96).std(ddof=0)
        feat["leader_z"] = ((feat["leader_ret"].abs() - abs_mean) / abs_std.replace(0, np.nan)).shift(1)
        feat["leader_ret"] = feat["leader_ret"].shift(1)
        feat["leader_valid"] = feat["leader_valid"].shift(1)
        feat["leader_same_dir"] = feat["leader_same_dir"].shift(1)
        feat = feat[["timestamp", "leader_ret", "leader_z", "leader_valid"]]
        out[asset] = df.merge(feat, on="timestamp", how="left")
    return out


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        for idx in np.flatnonzero(frame[f"{setup}_signal"].to_numpy()):
            if idx + HOLD_BARS + 1 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
                continue
            if not np.isfinite(row["leader_z"]) or not pd.notna(row["leader_valid"]):
                continue
            direction = -1.0 if setup == "breakout_short" else 1.0
            leader_ret = float(row["leader_ret"]) if np.isfinite(row["leader_ret"]) else np.nan
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "signal_idx": int(idx),
                    "signal_time": row["timestamp"],
                    "atr14": float(row["atr14"]),
                    "leader_ret": leader_ret,
                    "leader_z": float(row["leader_z"]),
                    "leader_valid": bool(row["leader_valid"]),
                    "direction": direction,
                    "same_direction_leader": bool(np.sign(leader_ret) == direction) if np.isfinite(leader_ret) else False,
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


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_setup = {setup: -1 for setup in SETUPS}
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_by_setup[setup]:
            continue

        same_dir = bool(sig["same_direction_leader"])
        valid = bool(sig["leader_valid"])
        z = float(sig["leader_z"])
        if variant == "low_z_only":
            if not (valid and same_dir and z < LOW_Z):
                continue
        elif variant == "high_z_veto":
            if valid and same_dir and z > HIGH_Z:
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
        target = entry * (1.0 + direction * (atr / entry))
        failure = entry * (1.0 - direction * (atr / entry))
        path = frame.iloc[entry_idx: exit_idx + 1]
        target_hit = None
        failure_hit = None
        for bar_idx, bar in path.iterrows():
            if direction > 0:
                if target_hit is None and float(bar["high"]) >= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["low"]) <= failure:
                    failure_hit = int(bar_idx)
            else:
                if target_hit is None and float(bar["low"]) <= target:
                    target_hit = int(bar_idx)
                if failure_hit is None and float(bar["high"]) >= failure:
                    failure_hit = int(bar_idx)
        failure_before_target = bool(failure_hit is not None and (target_hit is None or failure_hit <= target_hit))
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
                "leader_ret": float(sig["leader_ret"]),
                "leader_z": z,
                "leader_valid": valid,
                "same_direction_leader": same_dir,
                "failure_before_target": failure_before_target,
            }
        )
        last_exit_by_setup[setup] = exit_idx
    return pd.DataFrame(rows)


def summarize_pair(baseline: pd.DataFrame, variant_df: pd.DataFrame, cost_bps: float) -> dict[str, float]:
    b_net = net_ret(baseline["gross_return"], cost_bps) if len(baseline) else pd.Series(dtype=float)
    v_net = net_ret(variant_df["gross_return"], cost_bps) if len(variant_df) else pd.Series(dtype=float)
    return {
        "baseline_trades": int(len(baseline)),
        "variant_trades": int(len(variant_df)),
        "trade_count_retention": float(len(variant_df) / max(len(baseline), 1)),
        "baseline_return": float(b_net.mean()) if len(b_net) else np.nan,
        "variant_return": float(v_net.mean()) if len(v_net) else np.nan,
        "return_delta": float(v_net.mean() - b_net.mean()) if len(b_net) and len(v_net) else np.nan,
        "baseline_failure": float(baseline["failure_before_target"].mean()) if len(baseline) else np.nan,
        "variant_failure": float(variant_df["failure_before_target"].mean()) if len(variant_df) else np.nan,
        "failure_delta": float(variant_df["failure_before_target"].mean() - baseline["failure_before_target"].mean()) if len(baseline) and len(variant_df) else np.nan,
    }


def decide_verdict(test_overall: pd.DataFrame, test_setup: pd.DataFrame) -> tuple[str, str]:
    low = test_overall[test_overall["variant"] == "low_z_only"].iloc[0]
    veto = test_overall[test_overall["variant"] == "high_z_veto"].iloc[0]
    veto_good_setups = int(
        (
            (test_setup["variant"] == "high_z_veto")
            & (test_setup["return_delta"] > 0)
            & (test_setup["failure_delta"] <= 0)
            & (test_setup["trade_count_retention"] >= 0.50)
        ).sum()
    )
    low_good_setups = int(
        (
            (test_setup["variant"] == "low_z_only")
            & (test_setup["return_delta"] > 0)
            & (test_setup["trade_count_retention"] >= 0.25)
        ).sum()
    )
    if (
        pd.notna(veto["return_delta"]) and veto["return_delta"] > 0.0006
        and pd.notna(veto["failure_delta"]) and veto["failure_delta"] <= -0.01
        and veto["trade_count_retention"] >= 0.60
        and veto_good_setups >= 2
    ):
        return "promote_P2", "high-z veto 在测试段里同时改善成本后收益与 false-follow，且没有把交易数砍坏，足够升到 paper candidate。"
    if (
        (
            pd.notna(veto["return_delta"]) and veto["return_delta"] > 0 and veto["trade_count_retention"] >= 0.45
        )
        or (
            pd.notna(low["return_delta"]) and low["return_delta"] > 0 and low["trade_count_retention"] >= 0.20
        )
    ) and (veto_good_setups + low_good_setups >= 1):
        return "keep_P1", "leader impulse 这层还有一点 honest gate 味道，但还不够硬，先留在 P1。"
    return "park", "这轮 clean replication 没把 leader impulse 变成更诚实的 shared gate；改善主要像 setup 间互相打架或纯缩样本，先 park。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    base_frames = {asset: build_base_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    frames = add_crossmarket_features(base_frames)
    signals_by_asset = {asset: collect_signals(frame, asset) for asset, frame in frames.items()}
    split_by_asset = {asset: split_signals(signals) for asset, signals in signals_by_asset.items()}

    train_catalog = pd.concat([train.assign(split="train") for train, _ in split_by_asset.values()], ignore_index=True)
    test_catalog = pd.concat([test.assign(split="test") for _, test in split_by_asset.values()], ignore_index=True)
    signal_catalog = pd.concat([train_catalog, test_catalog], ignore_index=True)
    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)

    config_df = pd.DataFrame([
        {"metric": "leader_z", "low_z": LOW_Z, "high_z": HIGH_Z, "leader_ratio": LEADER_RATIO, "rolling_window_bars": 96, "hold_bars": HOLD_BARS}
    ])
    config_df.to_csv(ART_DIR / "threshold_config.csv", index=False)

    split_trade_parts = []
    overall_rows = []
    setup_rows = []
    asset_rows = []
    cost_rows = []

    for split_name in ["train", "test"]:
        baseline_parts = []
        low_parts = []
        veto_parts = []
        for asset in ASSETS:
            frame = frames[asset]
            signals = split_by_asset[asset][0] if split_name == "train" else split_by_asset[asset][1]
            baseline = simulate_variant(frame, signals, "baseline")
            low = simulate_variant(frame, signals, "low_z_only")
            veto = simulate_variant(frame, signals, "high_z_veto")
            baseline_parts.append(baseline)
            low_parts.append(low)
            veto_parts.append(veto)
            for variant_name, df in [("low_z_only", low), ("high_z_veto", veto)]:
                asset_rows.append({"split": split_name, "asset": asset, "variant": variant_name, **summarize_pair(baseline, df, PRIMARY_COST)})
                for setup in SETUPS:
                    b = baseline[baseline["setup"] == setup]
                    v = df[df["setup"] == setup]
                    setup_rows.append({"split": split_name, "setup": setup, "variant": variant_name, **summarize_pair(b, v, PRIMARY_COST)})
        baseline_df = pd.concat(baseline_parts, ignore_index=True)
        low_df = pd.concat(low_parts, ignore_index=True)
        veto_df = pd.concat(veto_parts, ignore_index=True)
        split_trade_parts.append(baseline_df.assign(split=split_name))
        split_trade_parts.append(low_df.assign(split=split_name))
        split_trade_parts.append(veto_df.assign(split=split_name))
        for variant_name, df in [("low_z_only", low_df), ("high_z_veto", veto_df)]:
            overall_rows.append({"split": split_name, "variant": variant_name, **summarize_pair(baseline_df, df, PRIMARY_COST)})
            for cost in COSTS:
                cost_rows.append({"split": split_name, "variant": variant_name, "cost_bps_per_side": cost, **summarize_pair(baseline_df, df, cost)})

    trade_log = pd.concat(split_trade_parts, ignore_index=True)
    overall_summary = pd.DataFrame(overall_rows)
    setup_summary = pd.DataFrame(setup_rows)
    asset_summary = pd.DataFrame(asset_rows)
    cost_summary = pd.DataFrame(cost_rows)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)

    verdict, verdict_reason = decide_verdict(
        overall_summary[overall_summary["split"] == "test"].reset_index(drop=True),
        setup_summary[setup_summary["split"] == "test"].reset_index(drop=True),
    )
    verdict_label = {
        "promote_P2": "promote_P2 / paper candidate",
        "keep_P1": "keep_P1 / weak candidate",
        "park": "park / evidence pool",
    }[verdict]

    summary_json = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "config": {
            "low_z": LOW_Z,
            "high_z": HIGH_Z,
            "leader_ratio": LEADER_RATIO,
            "rolling_window_bars": 96,
            "hold_bars": HOLD_BARS,
        },
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_reason": verdict_reason,
        "test_low_z_only": overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "low_z_only")].iloc[0].to_dict(),
        "test_high_z_veto": overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "high_z_veto")].iloc[0].to_dict(),
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    test_overall = overall_summary[overall_summary["split"] == "test"].copy()
    test_setup = setup_summary[setup_summary["split"] == "test"].copy()
    test_asset = asset_summary[asset_summary["split"] == "test"].copy()
    test_cost = cost_summary[cost_summary["split"] == "test"].copy()

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 130 · cross-market leader impulse nonlinear gate · minimal clean replication</h1>
    <div class=\"card\">
      <p><b>冻结参数：</b><code>leader_z low &lt; {LOW_Z}</code> / <code>high &gt; {HIGH_Z}</code> / <code>leader_abs_mean &gt; {LEADER_RATIO:.1f} × |target_ret|</code></p>
      <p><b>执行口径：</b><code>BTC/ETH/SOL 120d 15m + signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></p>
      <p><b>三臂：</b><code>baseline / low_z_only / high_z_veto</code></p>
      <p><b>当前 hard verdict：</b><span class=\"{'good' if verdict == 'promote_P2' else 'warn' if verdict == 'keep_P1' else 'bad'}\">{escape(verdict_label)}</span></p>
      <p class=\"muted\">{escape(verdict_reason)}</p>
    </div>
    <div class=\"card\">
      <h2>一句话人话</h2>
      <p>这轮只回答一件事：跨市场 leader 冲击是不是能当 shared follow-up gate。我们不再继续讲论文故事，而是直接看：<code>low-z</code> 放行、<code>high-z</code> veto，放到三个 setup 和三种资产上之后，成本后收益、false-follow、交易保留率到底有没有更诚实。</p>
    </div>
    <div class=\"card\">
      <h2>测试段总表（6 bps / side）</h2>
      {render_table(test_overall[["variant","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"})}
    </div>
    <div class=\"card\">
      <h2>测试段分 setup 对照</h2>
      {render_table(test_setup[["setup","variant","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"})}
    </div>
    <div class=\"card\">
      <h2>测试段分资产对照</h2>
      {render_table(test_asset[["asset","variant","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"})}
    </div>
    <div class=\"card\">
      <h2>成本稳健性（测试段）</h2>
      {render_table(test_cost[["variant","cost_bps_per_side","baseline_trades","variant_trades","trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"]], percent_cols={"trade_count_retention","baseline_return","variant_return","return_delta","baseline_failure","variant_failure","failure_delta"})}
    </div>
    <div class=\"card\">
      <h2>冻结配置</h2>
      {render_table(config_df, digits_cols={"low_z":2,"high_z":2,"leader_ratio":2})}
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/overall_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/setup_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/asset_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/cost_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/summary.json</code></li>
      </ul>
    </div>
    """

    write_html(SITE_DIR / "report.html", "Rank 130 · cross-market leader impulse nonlinear gate", body)
    write_html(READING_PATH, "Rank 130 · cross-market leader impulse nonlinear gate clean replication", body)
    print(json.dumps(summary_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
