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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank136_phase_wide_rsi_memory_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank136_phase_wide_rsi_memory_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank136_phase_wide_rsi_memory_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["breakout_short", "fib_retest_long", "ema_psar_long"]
HOLD_BARS = 8
ATR_PERIOD = 14
RSI_PERIOD = 14
PHASE_LOOKBACK = 6
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
LONG_RSI_FLOOR = 55.0
SHORT_RSI_CEIL = 44.0
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


def compute_rsi(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_up = up.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


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
    for days in (120, 240):
        path = CACHE_DIR / f"{symbol}__{days}d__15m.csv"
        if path.exists():
            df = pd.read_csv(path)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df["asset"] = asset
            return df.sort_values("timestamp").reset_index(drop=True)
    raise FileNotFoundError(f"No cache found for {symbol} under {CACHE_DIR}")


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["psar"] = compute_psar(df)
    df["atr14"] = compute_atr(df)
    df["rsi14"] = compute_rsi(df["close"])
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


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for setup in SETUPS:
        side = -1 if setup == "breakout_short" else 1
        for idx in np.flatnonzero(frame[f"{setup}_signal"].to_numpy()):
            if idx + HOLD_BARS + 1 >= len(frame):
                continue
            row = frame.iloc[idx]
            if not np.isfinite(row["atr14"]) or row["atr14"] <= 0:
                continue
            phase_slice = frame.iloc[max(0, idx - PHASE_LOOKBACK): idx + 1]
            rec = {
                "asset": asset,
                "setup": setup,
                "side": side,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "signal_rsi": float(row["rsi14"]),
                "phase_min_rsi": float(phase_slice["rsi14"].min()),
                "phase_max_rsi": float(phase_slice["rsi14"].max()),
                "atr14": float(row["atr14"]),
            }
            rec["phase_gate_pass"] = (
                rec["phase_min_rsi"] >= LONG_RSI_FLOOR if side > 0 else rec["phase_max_rsi"] <= SHORT_RSI_CEIL
            )
            rows.append(rec)
    out = pd.DataFrame(rows)
    return out.sort_values(["signal_time", "asset", "setup"]).reset_index(drop=True)


def simulate(signals: pd.DataFrame, frames: dict[str, pd.DataFrame], variant: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_by_asset: dict[str, pd.Timestamp] = {}
    for sig in signals.itertuples(index=False):
        if variant == "phase_gate" and not bool(sig.phase_gate_pass):
            continue
        frame = frames[sig.asset]
        signal_time = pd.Timestamp(sig.signal_time)
        last_exit = last_exit_by_asset.get(sig.asset)
        if last_exit is not None and signal_time <= last_exit:
            continue
        signal_idx = int(sig.signal_idx)
        entry_idx = signal_idx + 1
        exit_idx = signal_idx + HOLD_BARS
        if exit_idx >= len(frame):
            continue
        entry_row = frame.iloc[entry_idx]
        path = frame.iloc[entry_idx: exit_idx + 1]
        entry_price = float(entry_row["open"])
        atr = float(sig.atr14)
        side = int(sig.side)
        tp_price = entry_price + side * 0.75 * atr
        sl_price = entry_price - side * 0.75 * atr
        outcome = "timeout"
        exit_price = float(path.iloc[-1]["close"])
        exit_time = path.iloc[-1]["timestamp"]
        first_hit_bar = HOLD_BARS
        for bar_idx, bar in enumerate(path.itertuples(index=False), start=1):
            if side > 0:
                tp_hit = float(bar.high) >= tp_price
                sl_hit = float(bar.low) <= sl_price
            else:
                tp_hit = float(bar.low) <= tp_price
                sl_hit = float(bar.high) >= sl_price
            if tp_hit and sl_hit:
                close = float(bar.close)
                tp_dist = abs(close - tp_price)
                sl_dist = abs(close - sl_price)
                outcome = "tp" if tp_dist <= sl_dist else "sl"
            elif tp_hit:
                outcome = "tp"
            elif sl_hit:
                outcome = "sl"
            else:
                continue
            first_hit_bar = bar_idx
            exit_price = tp_price if outcome == "tp" else sl_price
            exit_time = bar.timestamp
            break
        gross_return = side * (exit_price / entry_price - 1.0)
        rows.append(
            {
                "variant": variant,
                "asset": sig.asset,
                "setup": sig.setup,
                "signal_time": signal_time,
                "entry_time": entry_row["timestamp"],
                "exit_time": exit_time,
                "signal_rsi": float(sig.signal_rsi),
                "phase_min_rsi": float(sig.phase_min_rsi),
                "phase_max_rsi": float(sig.phase_max_rsi),
                "phase_gate_pass": bool(sig.phase_gate_pass),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_return": gross_return,
                "outcome": outcome,
                "first_hit_bar": first_hit_bar,
            }
        )
        last_exit_by_asset[sig.asset] = pd.Timestamp(exit_time)
    return pd.DataFrame(rows)


def summarize_variant(df: pd.DataFrame, cost_bps: float) -> dict[str, float | int]:
    if df.empty:
        return {
            "trades": 0,
            "mean_return": np.nan,
            "tp_rate": np.nan,
            "sl_rate": np.nan,
            "timeout_rate": np.nan,
            "failure_before_target": np.nan,
        }
    net = net_ret(df["gross_return"], cost_bps)
    return {
        "trades": int(len(df)),
        "mean_return": float(np.mean(net)),
        "tp_rate": float((df["outcome"] == "tp").mean()),
        "sl_rate": float((df["outcome"] == "sl").mean()),
        "timeout_rate": float((df["outcome"] == "timeout").mean()),
        "failure_before_target": float((df["outcome"] == "sl").mean()),
    }


def compare_group(group_cols: list[str], base: pd.DataFrame, gate: pd.DataFrame, cost_bps: float) -> pd.DataFrame:
    keys = sorted(set(map(tuple, base[group_cols].drop_duplicates().values.tolist())) | set(map(tuple, gate[group_cols].drop_duplicates().values.tolist())))
    rows: list[dict[str, object]] = []
    for key in keys:
        mask_base = np.ones(len(base), dtype=bool)
        mask_gate = np.ones(len(gate), dtype=bool)
        row: dict[str, object] = {}
        for col, val in zip(group_cols, key):
            mask_base &= base[col].to_numpy() == val
            mask_gate &= gate[col].to_numpy() == val
            row[col] = val
        b = summarize_variant(base.loc[mask_base], cost_bps)
        g = summarize_variant(gate.loc[mask_gate], cost_bps)
        row.update(
            {
                "baseline_trades": b["trades"],
                "gate_trades": g["trades"],
                "trade_count_retention": (g["trades"] / b["trades"]) if b["trades"] else np.nan,
                "baseline_return": b["mean_return"],
                "gate_return": g["mean_return"],
                "return_delta": (g["mean_return"] - b["mean_return"]) if pd.notna(b["mean_return"]) and pd.notna(g["mean_return"]) else np.nan,
                "baseline_failure": b["failure_before_target"],
                "gate_failure": g["failure_before_target"],
                "failure_delta": (g["failure_before_target"] - b["failure_before_target"]) if pd.notna(b["failure_before_target"]) and pd.notna(g["failure_before_target"]) else np.nan,
                "baseline_timeout": b["timeout_rate"],
                "gate_timeout": g["timeout_rate"],
                "timeout_delta": (g["timeout_rate"] - b["timeout_rate"]) if pd.notna(b["timeout_rate"]) and pd.notna(g["timeout_rate"]) else np.nan,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def build_scorecard(overall_row: pd.Series, setup_summary: pd.DataFrame, asset_summary: pd.DataFrame) -> pd.DataFrame:
    retention = float(overall_row["trade_count_retention"])
    delta_bps = float(overall_row["return_delta"]) * 10000.0 if pd.notna(overall_row["return_delta"]) else np.nan
    breadth_setup = int((setup_summary["return_delta"] > 0).sum()) if not setup_summary.empty else 0
    breadth_asset = int((asset_summary["return_delta"] > 0).sum()) if not asset_summary.empty else 0
    usefulness = 3 if pd.notna(delta_bps) and delta_bps >= 6 and breadth_setup >= 2 else 2 if pd.notna(delta_bps) and delta_bps > 0 else 1 if pd.notna(delta_bps) and delta_bps > -3 else 0
    time_stability = 1
    cross_asset_stability = 3 if breadth_asset >= 3 else 2 if breadth_asset >= 2 else 1 if breadth_asset >= 1 else 0
    cost_trade_stability = 3 if retention >= 0.75 else 2 if retention >= 0.60 else 1 if retention >= 0.45 else 0
    deployability = 3 if pd.notna(delta_bps) and delta_bps >= 4 and retention >= 0.65 else 2 if pd.notna(delta_bps) and delta_bps > 0 and retention >= 0.55 else 1 if retention >= 0.40 else 0
    hard_fail_flags = []
    if retention < 0.35:
        hard_fail_flags.append("too_sparse")
    if breadth_asset <= 1:
        hard_fail_flags.append("single_pocket_dependency")
    if pd.notna(overall_row["gate_return"]) and overall_row["gate_return"] < 0 and pd.notna(overall_row["baseline_return"]) and overall_row["gate_return"] < overall_row["baseline_return"]:
        hard_fail_flags.append("post_cost_collapse")
    recommended_action = "promote_P2" if not hard_fail_flags and usefulness >= 2 and cross_asset_stability >= 2 and deployability >= 2 else "keep_P1" if not hard_fail_flags and usefulness >= 1 else "park"
    why_now = "EMA 仍 waiting_not_due，本轮需要给 Rank 136 一次最小 clean replication，回答 phase-wide RSI memory 是 shared gate 还是只剩故事。"
    main_weakness = "改善是否过于依赖单一 setup / 单一资产，以及 retention 是否为此付出过大代价。"
    return pd.DataFrame(
        [
            {
                "usefulness": usefulness,
                "time_stability": time_stability,
                "cross_asset_stability": cross_asset_stability,
                "cost_trade_stability": cost_trade_stability,
                "deployability": deployability,
                "hard_fail_flags": ", ".join(hard_fail_flags) if hard_fail_flags else "none",
                "recommended_action": recommended_action,
                "why_now": why_now,
                "main_weakness": main_weakness,
            }
        ]
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = {asset: build_frame(asset, symbol) for asset, symbol in ASSETS.items()}
    signals = pd.concat([collect_signals(frame, asset) for asset, frame in frames.items()], ignore_index=True)
    if signals.empty:
        raise SystemExit("No signals collected; cannot build Rank 136 clean replication.")

    signals.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    baseline = simulate(signals, frames, variant="baseline")
    gate = simulate(signals, frames, variant="phase_gate")
    trade_log = pd.concat([baseline, gate], ignore_index=True).sort_values(["entry_time", "variant", "asset", "setup"])
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)

    overall_summary = compare_group([], baseline.assign(_all="all"), gate.assign(_all="all"), PRIMARY_COST)
    if overall_summary.empty:
        overall_summary = compare_group(["_all"], baseline.assign(_all="all"), gate.assign(_all="all"), PRIMARY_COST).drop(columns=["_all"])
    setup_summary = compare_group(["setup"], baseline, gate, PRIMARY_COST)
    asset_summary = compare_group(["asset"], baseline, gate, PRIMARY_COST)
    cost_summary_rows = []
    for cost in COSTS:
        row = compare_group(["_all"], baseline.assign(_all="all"), gate.assign(_all="all"), cost).drop(columns=["_all"]).iloc[0].to_dict()
        row["cost_bps"] = cost
        cost_summary_rows.append(row)
    cost_summary = pd.DataFrame(cost_summary_rows)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)

    scorecard = build_scorecard(overall_summary.iloc[0], setup_summary, asset_summary)
    scorecard.to_csv(ART_DIR / "scorecard.csv", index=False)
    meta = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "phase_lookback_bars": PHASE_LOOKBACK,
        "long_min_rsi_floor": LONG_RSI_FLOOR,
        "short_max_rsi_ceil": SHORT_RSI_CEIL,
        "hold_bars": HOLD_BARS,
        "costs_bps": COSTS,
        "assets": list(ASSETS.keys()),
        "setups": SETUPS,
        "primary_verdict": scorecard.iloc[0]["recommended_action"],
    }
    (ART_DIR / "summary.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    title = "Rank 136 / phase-wide RSI memory retest gate / clean replication"
    overall_row = overall_summary.iloc[0]
    score_row = scorecard.iloc[0]
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>生成时间：{escape(meta['generated_at_utc'])}</p>
<div class='card'>
  <p><strong>实验口径：</strong> BTC/ETH/SOL，15m，本地 cache，三条 archetype（breakout_short / fib_retest_long / ema_psar_long），<code>next-bar open</code>、按资产 <code>no-overlap</code>、持有 {HOLD_BARS} bars。</p>
  <p><strong>Phase gate：</strong> long 看最近 {PHASE_LOOKBACK + 1} 根 completed bars 的 <code>min RSI &gt;={LONG_RSI_FLOOR:.0f}</code>；short 看 <code>max RSI &lt;={SHORT_RSI_CEIL:.0f}</code>。</p>
  <p><strong>当前建议：</strong> <span class='warn'>{escape(str(score_row['recommended_action']))}</span></p>
</div>
<div class='card'>
  <h2>Overall（6 bps）</h2>
  {render_table(overall_summary, percent_cols={'trade_count_retention','baseline_return','gate_return','return_delta','baseline_failure','gate_failure','failure_delta','baseline_timeout','gate_timeout','timeout_delta'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
</div>
<div class='card'>
  <h2>By setup（6 bps）</h2>
  {render_table(setup_summary, percent_cols={'trade_count_retention','baseline_return','gate_return','return_delta','baseline_failure','gate_failure','failure_delta','baseline_timeout','gate_timeout','timeout_delta'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
</div>
<div class='card'>
  <h2>By asset（6 bps）</h2>
  {render_table(asset_summary, percent_cols={'trade_count_retention','baseline_return','gate_return','return_delta','baseline_failure','gate_failure','failure_delta','baseline_timeout','gate_timeout','timeout_delta'}, digits_cols={'baseline_trades':0,'gate_trades':0})}
</div>
<div class='card'>
  <h2>Cost summary</h2>
  {render_table(cost_summary[['cost_bps','baseline_trades','gate_trades','trade_count_retention','baseline_return','gate_return','return_delta','failure_delta']], percent_cols={'trade_count_retention','baseline_return','gate_return','return_delta','failure_delta'}, digits_cols={'cost_bps':0,'baseline_trades':0,'gate_trades':0})}
</div>
<div class='card'>
  <h2>Scout Promotion Scorecard</h2>
  {render_table(scorecard)}
  <p><strong>证据槽位：</strong> return_delta={pct(overall_row['return_delta'])}，trade_count_retention={pct(overall_row['trade_count_retention'])}，failure_delta={pct(overall_row['failure_delta'])}</p>
</div>
"""
    write_html(SITE_DIR / "report.html", title, body)
    reading_body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>这是给 Scout Seat 的 reader-facing clean replication 落点。详细 artifacts 见 <code>reports/artifacts/scout_rank136_phase_wide_rsi_memory_15m/</code>。</p>
<div class='card'>
  <p><strong>一句话：</strong>baseline vs phase-wide RSI memory gate（long <code>min RSI &gt;= 55</code> / short <code>max RSI &lt;= 44</code>）在 6 bps 下的最小 clean replication 结果为：<strong>{escape(str(score_row['recommended_action']))}</strong>。</p>
  <p><strong>为什么：</strong>return delta = {pct(overall_row['return_delta'])}，trade count retention = {pct(overall_row['trade_count_retention'])}，failure delta = {pct(overall_row['failure_delta'])}。</p>
  <p><a href='../..//factors/scout_rank136_phase_wide_rsi_memory_15m/report.html'>查看完整 report</a></p>
</div>
<div class='card'>
  <h2>Scorecard</h2>
  {render_table(scorecard)}
</div>
"""
    reading_body = reading_body.replace("../..//", "../../")
    write_html(READING_PATH, title, reading_body)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
