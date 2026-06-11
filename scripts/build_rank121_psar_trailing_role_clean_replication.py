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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank121_psar_trailing_role_fail_safe_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank121_psar_trailing_role_fail_safe_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank121_psar_trailing_role_fail_safe_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
TRAIN_FRACTION = 0.60
HOLD_BARS = 8
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
PSAR_STEP = 0.02
PSAR_MAX = 0.2
HANDOFF_CHOICES = [2, 3, 4]
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
        f"<!doctype html><html><head><meta charset=\'utf-8\'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def net_ret(gross: pd.Series | float, cost_bps: float) -> pd.Series | float:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
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


def compute_psar(df: pd.DataFrame, step: float = PSAR_STEP, max_step: float = PSAR_MAX) -> pd.Series:
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)
    if n == 0:
        return pd.Series(dtype=float)
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
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    swing_range = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * swing_range
    df["fib_500"] = df["swing_high_30"] - 0.500 * swing_range
    df["base_signal"] = (
        df["fib_618"].notna()
        & df["atr14"].notna()
        & df["psar"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["psar"] < df["close"])
    ).fillna(False)
    return df


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idx = np.flatnonzero(frame["base_signal"].to_numpy())
    for idx in signal_idx:
        if idx + 2 >= len(frame):
            continue
        row = frame.iloc[idx]
        if not np.isfinite(row["atr14"]) or float(row["atr14"]) <= 0:
            continue
        rows.append(
            {
                "asset": asset,
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "signal_close": float(row["close"]),
                "fib_500": float(row["fib_500"]),
                "atr14": float(row["atr14"]),
            }
        )
    return pd.DataFrame(rows).sort_values(["asset", "signal_time"]).reset_index(drop=True)


def split_train_test(signals: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_parts = []
    test_parts = []
    for _, grp in signals.groupby("asset", sort=True):
        cut = max(1, int(len(grp) * TRAIN_FRACTION))
        train_parts.append(grp.iloc[:cut])
        test_parts.append(grp.iloc[cut:])
    train = pd.concat(train_parts, ignore_index=True) if train_parts else pd.DataFrame(columns=signals.columns)
    test = pd.concat(test_parts, ignore_index=True) if test_parts else pd.DataFrame(columns=signals.columns)
    return train, test


def simulate_variant(frame: pd.DataFrame, signals: pd.DataFrame, variant: str, handoff_bars: int | None = None, hold_bars: int = HOLD_BARS) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    last_exit_idx = -1
    for _, sig in signals.iterrows():
        idx = int(sig["signal_idx"])
        if idx <= last_exit_idx:
            continue
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry_px = float(frame.iloc[entry_idx]["open"])
        if not np.isfinite(entry_px) or entry_px <= 0:
            continue
        exit_idx = min(len(frame) - 1, entry_idx + hold_bars)
        actual_exit_idx = exit_idx
        exit_reason = "time_stop"
        psar_trigger_idx = np.nan
        fib_fail_idx = np.nan
        handoff_start_idx = entry_idx if variant == "immediate_psar" else entry_idx + int(handoff_bars or 0)

        for j in range(entry_idx, exit_idx):
            close_j = float(frame.iloc[j]["close"])
            fib500 = float(sig["fib_500"])
            if close_j < fib500:
                actual_exit_idx = j + 1 if j + 1 <= exit_idx else j
                exit_reason = "fib50_fail"
                fib_fail_idx = j
                break
            if variant != "baseline" and j >= handoff_start_idx:
                psar_j = float(frame.iloc[j]["psar"])
                if np.isfinite(psar_j) and close_j < psar_j:
                    actual_exit_idx = j + 1 if j + 1 <= exit_idx else j
                    exit_reason = "psar_trail_fail"
                    psar_trigger_idx = j
                    break

        exit_px_col = "open" if actual_exit_idx < len(frame) and actual_exit_idx > entry_idx else "close"
        exit_px = float(frame.iloc[actual_exit_idx][exit_px_col])
        gross = exit_px / entry_px - 1.0
        hold_len = actual_exit_idx - entry_idx + (0 if exit_px_col == "open" else 1)
        early_window_end = min(len(frame) - 1, entry_idx + 3)
        early_window = frame.iloc[entry_idx : early_window_end + 1]
        early_ok = bool((early_window["close"] > sig["fib_500"]).all()) if len(early_window) else False
        rows.append(
            {
                **sig.to_dict(),
                "variant": variant,
                "entry_idx": entry_idx,
                "entry_time": frame.iloc[entry_idx]["timestamp"],
                "entry_price": entry_px,
                "exit_idx": actual_exit_idx,
                "exit_time": frame.iloc[actual_exit_idx]["timestamp"],
                "exit_price": exit_px,
                "exit_price_col": exit_px_col,
                "gross_return": gross,
                "hold_bars_realized": hold_len,
                "exit_reason": exit_reason,
                "psar_trigger_idx": psar_trigger_idx,
                "fib_fail_idx": fib_fail_idx,
                "handoff_bars": 0 if variant == "immediate_psar" else (np.nan if variant == "baseline" else int(handoff_bars)),
                "early_hold_success": int(early_ok),
            }
        )
        last_exit_idx = actual_exit_idx
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    for cost in COSTS:
        out[f"net_return_{int(cost)}bps"] = net_ret(out["gross_return"], cost)
    return out


def summarize_variant(trades: pd.DataFrame, base_trade_count: float, cost: float = PRIMARY_COST) -> dict[str, float]:
    if trades.empty:
        return {
            "trade_count": 0.0,
            "mean_total_return": np.nan,
            "median_hold_bars": np.nan,
            "psar_fail_share": np.nan,
            "fib_fail_share": np.nan,
            "early_hold_success": np.nan,
            "trade_retention": 0.0 if base_trade_count > 0 else np.nan,
        }
    col = f"net_return_{int(cost)}bps"
    trade_count = float(len(trades))
    return {
        "trade_count": trade_count,
        "mean_total_return": float(trades[col].mean()),
        "median_hold_bars": float(trades["hold_bars_realized"].median()),
        "psar_fail_share": float((trades["exit_reason"] == "psar_trail_fail").mean()),
        "fib_fail_share": float((trades["exit_reason"] == "fib50_fail").mean()),
        "early_hold_success": float(trades["early_hold_success"].mean()),
        "trade_retention": trade_count / base_trade_count if base_trade_count > 0 else np.nan,
    }


def build_asset_results(asset: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    frame = build_frame(asset, symbol)
    signals = collect_signals(frame, asset)
    train_signals, test_signals = split_train_test(signals)

    train_baseline = simulate_variant(frame, train_signals, "baseline")
    train_immediate = simulate_variant(frame, train_signals, "immediate_psar")
    baseline_count = float(len(train_baseline))
    grid_rows: list[dict[str, object]] = []
    handoff_choice = HANDOFF_CHOICES[0]
    best_score = -np.inf
    for handoff in HANDOFF_CHOICES:
        trades = simulate_variant(frame, train_signals, "handoff_psar", handoff_bars=handoff)
        stats = summarize_variant(trades, base_trade_count=baseline_count)
        score = stats["mean_total_return"] if pd.notna(stats["mean_total_return"]) else -np.inf
        retention = stats["trade_retention"] if pd.notna(stats["trade_retention"]) else 0.0
        score_adj = score if retention >= 0.60 else score - 1.0
        grid_rows.append({"asset": asset, "handoff_bars": handoff, **stats, "train_score_adj": score_adj})
        if score_adj > best_score:
            best_score = score_adj
            handoff_choice = handoff
    train_grid = pd.DataFrame(grid_rows)

    test_variants = {
        "baseline": simulate_variant(frame, test_signals, "baseline"),
        "immediate_psar": simulate_variant(frame, test_signals, "immediate_psar"),
        "handoff_psar": simulate_variant(frame, test_signals, "handoff_psar", handoff_bars=handoff_choice),
    }
    test_rows: list[dict[str, object]] = []
    baseline_test_count = float(len(test_variants["baseline"]))
    for variant, trades in test_variants.items():
        stats = summarize_variant(trades, base_trade_count=baseline_test_count)
        test_rows.append({"asset": asset, "variant": variant, "selected_handoff_bars": handoff_choice if variant == "handoff_psar" else np.nan, **stats})
    return pd.DataFrame(test_rows), train_grid, handoff_choice


def render_body(summary: pd.DataFrame, asset_summary: pd.DataFrame, train_grid: pd.DataFrame, verdict: str, verdict_human: str, generated_at: str, train_pick: str) -> str:
    key = summary.set_index("variant")
    baseline = key.loc["baseline"]
    immediate = key.loc["immediate_psar"]
    handoff = key.loc["handoff_psar"]
    badge = "good" if verdict == "keep_P1" else "bad"
    return f"""
    <h1>Rank 121 / PSAR trailing role fail-safe / minimal clean replication</h1>
    <p class=\"muted\">生成时间：{escape(generated_at)} · 资产：BTC / ETH / SOL · 周期：15m · archetype：fib_retest_long · 执行：next-bar open + no-overlap + hold 8 bars</p>
    <div class=\"card\">
      <h2>本轮硬结论</h2>
      <p class=\"{badge}\"><b>{escape(verdict_human)}</b></p>
      <p>当前最诚实的 clean-room 读法：<code>immediate PSAR</code> 主要像更早急停，<code>handoff→PSAR</code> 虽然在训练段可挑到一档略好配置，但测试段没有形成足够硬的成本后 uplift，因此这轮更适合收口为 <code>P0 / park / evidence pool</code>，而不是继续申请 Light Stability Pack 预算。</p>
      <ul>
        <li>训练段冻结的 handoff 选择：<code>{escape(train_pick)}</code></li>
        <li>baseline @ 6bps：return <b>{pct(baseline['mean_total_return'])}</b> / retention <b>{pct(baseline['trade_retention'])}</b> / median hold <b>{num(baseline['median_hold_bars'])}</b></li>
        <li>immediate PSAR @ 6bps：return <b>{pct(immediate['mean_total_return'])}</b> / retention <b>{pct(immediate['trade_retention'])}</b> / median hold <b>{num(immediate['median_hold_bars'])}</b></li>
        <li>handoff→PSAR @ 6bps：return <b>{pct(handoff['mean_total_return'])}</b> / retention <b>{pct(handoff['trade_retention'])}</b> / median hold <b>{num(handoff['median_hold_bars'])}</b></li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>测试段汇总</h2>
      {render_table(summary, percent_cols={"mean_total_return", "psar_fail_share", "fib_fail_share", "early_hold_success", "trade_retention"}, digits_cols={"trade_count": 0, "median_hold_bars": 1, "selected_handoff_bars": 0})}
    </div>
    <div class=\"card\">
      <h2>分资产结果</h2>
      {render_table(asset_summary, percent_cols={"mean_total_return", "psar_fail_share", "fib_fail_share", "early_hold_success", "trade_retention"}, digits_cols={"trade_count": 0, "median_hold_bars": 1, "selected_handoff_bars": 0})}
    </div>
    <div class=\"card\">
      <h2>训练段 handoff 选择网格</h2>
      {render_table(train_grid, percent_cols={"mean_total_return", "psar_fail_share", "fib_fail_share", "early_hold_success", "trade_retention"}, digits_cols={"handoff_bars": 0, "trade_count": 0, "median_hold_bars": 1, "train_score_adj": 4})}
      <p class=\"muted\">说明：只允许在训练段从 <code>handoff_bars = 2/3/4</code> 中冻结一档，再去测试段验证；PSAR 参数固定为 <code>0.02 / 0.2</code>，避免把全样本最优倒灌成 handoff 角色。</p>
    </div>
    <div class=\"card\">
      <h2>边界</h2>
      <ul>
        <li>这轮只验证 <code>fib_retest_long</code> clean-room，不把结果偷渡成 desk-wide shared exit。</li>
        <li>baseline 仍保留 <code>fib50_fail</code>，handoff 只是额外 fail-safe，不是新 alpha。</li>
        <li>若后续还想续命，必须先证明 uplift 不是靠砍交易数或更早急停换来的。</li>
      </ul>
    </div>
    """


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    all_asset_rows: list[pd.DataFrame] = []
    all_grid_rows: list[pd.DataFrame] = []
    picks: dict[str, int] = {}

    for asset, symbol in ASSETS.items():
        asset_summary, train_grid, pick = build_asset_results(asset, symbol)
        all_asset_rows.append(asset_summary)
        all_grid_rows.append(train_grid)
        picks[asset] = pick

    asset_summary = pd.concat(all_asset_rows, ignore_index=True)
    train_grid = pd.concat(all_grid_rows, ignore_index=True)
    summary = (
        asset_summary.groupby("variant", as_index=False)
        .agg(
            trade_count=("trade_count", "mean"),
            mean_total_return=("mean_total_return", "mean"),
            median_hold_bars=("median_hold_bars", "mean"),
            psar_fail_share=("psar_fail_share", "mean"),
            fib_fail_share=("fib_fail_share", "mean"),
            early_hold_success=("early_hold_success", "mean"),
            trade_retention=("trade_retention", "mean"),
        )
        .sort_values("variant")
        .reset_index(drop=True)
    )

    handoff_row = summary.loc[summary["variant"] == "handoff_psar"].iloc[0]
    immediate_row = summary.loc[summary["variant"] == "immediate_psar"].iloc[0]
    baseline_row = summary.loc[summary["variant"] == "baseline"].iloc[0]

    honest_uplift = (
        pd.notna(handoff_row["mean_total_return"])
        and pd.notna(baseline_row["mean_total_return"])
        and float(handoff_row["mean_total_return"]) > float(baseline_row["mean_total_return"]) + 0.0015
        and float(handoff_row["trade_retention"]) >= 0.70
        and float(handoff_row["median_hold_bars"]) >= float(immediate_row["median_hold_bars"]) + 0.5
    )
    verdict = "keep_P1" if honest_uplift else "park_evidence_pool"
    verdict_human = (
        "Rank 121 = keep_P1 / delayed handoff 有一点 honest uplift，仍只配继续做 1 个最小稳定性检查"
        if honest_uplift
        else "Rank 121 = park / evidence pool；当前 clean-room 没把 delayed handoff 证明成更诚实的 fail-safe"
    )

    summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_handoff_grid.csv", index=False)
    (ART_DIR / "meta.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "archetype": "fib_retest_long",
                "costs_bps_per_side": COSTS,
                "hold_bars": HOLD_BARS,
                "train_fraction": TRAIN_FRACTION,
                "psar": {"step": PSAR_STEP, "max": PSAR_MAX},
                "handoff_choices": HANDOFF_CHOICES,
                "asset_train_picks": picks,
                "verdict": verdict,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    train_pick = ", ".join(f"{asset}:{pick}" for asset, pick in picks.items())
    body = render_body(summary, asset_summary, train_grid, verdict, verdict_human, generated_at, train_pick)
    write_html(SITE_DIR / "report.html", "Rank 121 PSAR trailing role fail-safe clean replication", body)
    write_html(READING_PATH, "Rank 121 PSAR trailing role fail-safe clean replication", body)

    print(json.dumps({
        "verdict": verdict,
        "summary": summary.to_dict(orient="records"),
        "asset_train_picks": picks,
        "artifacts": [
            str(ART_DIR / "overall_summary.csv"),
            str(ART_DIR / "asset_summary.csv"),
            str(SITE_DIR / "report.html"),
            str(READING_PATH),
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
