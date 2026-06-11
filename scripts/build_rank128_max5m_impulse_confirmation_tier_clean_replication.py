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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank128_max5m_impulse_confirmation_tier_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank128_max5m_impulse_confirmation_tier_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank128_max5m_impulse_confirmation_tier_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_reclaim_long", "fib_retest_long"]
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
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


def load_15m(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_15M_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def load_5m(symbol: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_5M_DIR / f"{symbol}_120d_5m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def build_15m_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_15m(symbol, asset)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema20_slope3"] = df["ema20"].pct_change(3)
    tr = pd.concat(
        [
            (df["high"] - df["low"]).abs(),
            (df["high"] - df["close"].shift(1)).abs(),
            (df["low"] - df["close"].shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["atr14"] = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range

    df["ema_reclaim_long_signal"] = (
        (df["ema20"] > df["ema50"])
        & (df["ema20_slope3"] > 0)
        & (df["close"] > df["ema20"])
        & (df["close"].shift(1) <= df["ema20"].shift(1))
        & (df["low"] <= df["ema20"] + 0.15 * df["atr14"])
        & (df["close"] > df["open"])
        & (df["volume"] >= 0.8 * df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & (df["ema20"] > df["ema50"])
        & (df["ema20_slope3"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] >= 0.8 * df["vol_ma20"])
    ).fillna(False)
    return df


def compute_max5m_1h(df5m: pd.DataFrame) -> pd.DataFrame:
    out = df5m.copy()
    out["ret1"] = out["close"].pct_change()
    out["max5m_1h"] = out["ret1"].rolling(12, min_periods=12).max().shift(1)
    return out[["timestamp", "max5m_1h"]]


def attach_max_feature(df15m: pd.DataFrame, feature_5m: pd.DataFrame) -> pd.DataFrame:
    feat = feature_5m.rename(columns={"timestamp": "feature_time"}).copy()
    merged = pd.merge_asof(
        df15m.sort_values("timestamp"),
        feat.sort_values("feature_time"),
        left_on="timestamp",
        right_on="feature_time",
        direction="backward",
        allow_exact_matches=True,
    )
    return merged.drop(columns=["feature_time"])


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        signal_col = f"{setup}_signal"
        for idx in np.flatnonzero(frame[signal_col].to_numpy()):
            if idx + HOLD_BARS + 1 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["max5m_1h"]):
                continue
            rows.append(
                {
                    "asset": asset,
                    "setup": setup,
                    "signal_idx": int(idx),
                    "signal_time": row["timestamp"],
                    "max5m_1h": float(row["max5m_1h"]),
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


def simulate_variant(
    frame: pd.DataFrame,
    signals: pd.DataFrame,
    variant: str,
    threshold: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_setup = {setup: -1 for setup in SETUPS}
    for _, sig in signals.iterrows():
        setup = str(sig["setup"])
        idx = int(sig["signal_idx"])
        if idx <= last_exit_by_setup[setup]:
            continue
        maxv = float(sig["max5m_1h"])
        if variant == "max_high_only" and maxv < threshold:
            continue
        if variant == "exclude_max_high" and maxv >= threshold:
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        entry = float(frame.iloc[entry_idx]["open"])
        exit_price = float(frame.iloc[exit_idx]["close"])
        gross = exit_price / entry - 1.0
        path = frame.iloc[entry_idx: exit_idx + 1]
        atr = float(frame.iloc[idx]["atr14"]) if np.isfinite(frame.iloc[idx]["atr14"]) else float(frame.iloc[idx]["close"]) * 0.01
        target = entry + atr
        failure = entry - atr
        target_hit = None
        failure_hit = None
        for bar_idx, bar in path.iterrows():
            if target_hit is None and float(bar["high"]) >= target:
                target_hit = int(bar_idx)
            if failure_hit is None and float(bar["low"]) <= failure:
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
                "max5m_1h": maxv,
                "high_tier": bool(maxv >= threshold),
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
    high = test_overall[test_overall["variant"] == "max_high_only"].iloc[0]
    excl = test_overall[test_overall["variant"] == "exclude_max_high"].iloc[0]
    high_setup_good = int(
        (
            (test_setup["variant"] == "max_high_only")
            & (test_setup["return_delta"] > 0)
            & (test_setup["trade_count_retention"] >= 0.20)
        ).sum()
    )
    if (
        pd.notna(high["return_delta"]) and high["return_delta"] > 0.0008
        and pd.notna(high["variant_return"]) and high["variant_return"] > high["baseline_return"]
        and high["trade_count_retention"] >= 0.28
        and pd.notna(excl["return_delta"]) and excl["return_delta"] < -0.0003
        and high_setup_good >= 2
    ):
        return "promote_P2", "高 MAX tier 在测试段里既优于 baseline，也明显优于排除高 MAX 的对照，足够升到 paper candidate。"
    if (
        pd.notna(high["return_delta"]) and high["return_delta"] > 0
        and high["trade_count_retention"] >= 0.15
        and high_setup_good >= 1
    ):
        return "keep_P1", "高 MAX tier 仍有一点 honest continuation-confirmation 味道，但强度还不够硬，先留在 P1。"
    return "park", "这轮 clean replication 没把 MAX(5m) 变成更诚实的 desk 分层；改善主要像缩样本或 setup 间不一致，先 park。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {}
    signals_by_asset = {}
    split_by_asset = {}
    for asset, symbol in ASSETS.items():
        frame15 = build_15m_frame(asset, symbol)
        feat5 = compute_max5m_1h(load_5m(symbol))
        frame = attach_max_feature(frame15, feat5)
        frames[asset] = frame
        signals = collect_signals(frame, asset)
        signals_by_asset[asset] = signals
        split_by_asset[asset] = split_signals(signals)

    train_catalog = pd.concat([train.assign(split="train") for train, _ in split_by_asset.values()], ignore_index=True)
    test_catalog = pd.concat([test.assign(split="test") for _, test in split_by_asset.values()], ignore_index=True)
    signal_catalog = pd.concat([train_catalog, test_catalog], ignore_index=True)
    signal_catalog.to_csv(ART_DIR / "signal_catalog.csv", index=False)

    threshold = float(train_catalog["max5m_1h"].quantile(0.70))
    threshold_df = pd.DataFrame([
        {"scope": "global", "metric": "max5m_1h", "high_tier_quantile": 0.70, "threshold": threshold}
    ])
    threshold_df.to_csv(ART_DIR / "thresholds.csv", index=False)

    split_trade_parts = []
    overall_rows = []
    setup_rows = []
    asset_rows = []
    cost_rows = []

    for split_name in ["train", "test"]:
        baseline_parts = []
        high_parts = []
        excl_parts = []
        for asset in ASSETS:
            frame = frames[asset]
            signals = split_by_asset[asset][0] if split_name == "train" else split_by_asset[asset][1]
            baseline = simulate_variant(frame, signals, "baseline", threshold)
            high = simulate_variant(frame, signals, "max_high_only", threshold)
            excl = simulate_variant(frame, signals, "exclude_max_high", threshold)
            baseline_parts.append(baseline)
            high_parts.append(high)
            excl_parts.append(excl)
            for variant_name, df in [("max_high_only", high), ("exclude_max_high", excl)]:
                asset_rows.append({"split": split_name, "asset": asset, "variant": variant_name, **summarize_pair(baseline, df, PRIMARY_COST)})
                for setup in SETUPS:
                    b = baseline[baseline["setup"] == setup]
                    v = df[df["setup"] == setup]
                    setup_rows.append({"split": split_name, "setup": setup, "variant": variant_name, **summarize_pair(b, v, PRIMARY_COST)})
        baseline_df = pd.concat(baseline_parts, ignore_index=True)
        high_df = pd.concat(high_parts, ignore_index=True)
        excl_df = pd.concat(excl_parts, ignore_index=True)
        split_trade_parts.append(baseline_df.assign(split=split_name))
        split_trade_parts.append(high_df.assign(split=split_name))
        split_trade_parts.append(excl_df.assign(split=split_name))
        for variant_name, df in [("max_high_only", high_df), ("exclude_max_high", excl_df)]:
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
        "threshold_quantile": 0.70,
        "threshold": threshold,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_reason": verdict_reason,
        "test_max_high_only": overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "max_high_only")].iloc[0].to_dict(),
        "test_exclude_max_high": overall_summary[(overall_summary["split"] == "test") & (overall_summary["variant"] == "exclude_max_high")].iloc[0].to_dict(),
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")

    test_overall = overall_summary[overall_summary["split"] == "test"].copy()
    test_setup = setup_summary[setup_summary["split"] == "test"].copy()
    test_asset = asset_summary[asset_summary["split"] == "test"].copy()
    test_cost = cost_summary[cost_summary["split"] == "test"].copy()

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 128 · MAX(5m) impulse confirmation tier · minimal clean replication</h1>
    <div class=\"card\">
      <p><b>冻结阈值：</b>训练段 <code>max5m_1h</code> 的 <code>top30%</code>，阈值 = <code>{threshold:.6f}</code></p>
      <p><b>执行口径：</b><code>BTC/ETH/SOL 120d 5m+15m + signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code></p>
      <p><b>base archetype：</b><code>ema_reclaim_long</code> + <code>fib_retest_long</code></p>
      <p><b>当前 hard verdict：</b><span class=\"{'good' if verdict == 'promote_P2' else 'warn' if verdict == 'keep_P1' else 'bad'}\">{escape(verdict_label)}</span></p>
      <p class=\"muted\">{escape(verdict_reason)}</p>
    </div>
    <div class=\"card\">
      <h2>一句话人话</h2>
      <p>这轮只回答一件事：在 <code>EMA reclaim / Fib retest</code> 之后，小时内最猛那根 5 分钟上冲，究竟更像 continuation-confirmation tier，还是只是把样本砍薄的幻觉。为避免偷看，我们先在训练段冻结 high-tier 阈值，再去测试段比较 <code>baseline / max_high_only / exclude_max_high</code>。</p>
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
      <h2>阈值冻结</h2>
      {render_table(threshold_df, digits_cols={"threshold": 6, "high_tier_quantile": 2})}
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/overall_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/setup_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/asset_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/cost_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/summary.json</code></li>
      </ul>
    </div>
    """

    write_html(SITE_DIR / "report.html", "Rank 128 · MAX(5m) impulse confirmation tier", body)
    write_html(READING_PATH, "Rank 128 · MAX(5m) impulse confirmation tier clean replication", body)
    print(json.dumps(summary_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
