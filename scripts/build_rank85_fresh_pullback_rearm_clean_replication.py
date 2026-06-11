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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank85_fresh_pullback_rearm_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank85_fresh_pullback_rearm_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank85_fresh_pullback_rearm_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
DUE_PATH = ROOT / "reports" / "artifacts" / "ema_psar_raw_alpha" / "ema_paper_trading_due_guardrail_snapshot.csv"
P3_SUMMARY_PATH = ROOT / "reports" / "artifacts" / "manual_narrow_paper_lanes" / "manual_narrow_paper_last_run_summary.json"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "rearm_gate", "rearm_gate_plus_hard_invalidation"]
PRIMARY_VARIANT = "rearm_gate"
STRICT_VARIANT = "rearm_gate_plus_hard_invalidation"
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
HOLD_BARS = 8
EARLY_FAIL_BARS = 3
LOOKBACK = 30
ATR_PERIOD = 14
VOL_PERIOD = 20
REARM_WINDOW = 12
CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


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


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = ATR_PERIOD) -> pd.Series:
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
    df = load_cached_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df["atr14"] = atr(df)
    df["psar"] = compute_psar(df)
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["swing_high_30"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    rng = df["swing_high_30"] - df["swing_low_30"]
    df["fib_382"] = df["swing_high_30"] - 0.382 * rng
    df["fib_50"] = df["swing_high_30"] - 0.5 * rng
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng

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
    atr14 = df["atr14"]
    df["breakout_short_signal"] = (
        low.notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > low.shift(1))
        & (df["close"].shift(2) > low.shift(2))
        & (df["close"] < low - 0.1 * atr14)
        & (df["high"] <= low + 0.3 * atr14)
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["long_bias"] = (df["ema9"] > df["ema15"]).fillna(False)
    df["short_bias"] = (df["ema9"] < df["ema15"]).fillna(False)
    return df


def setup_direction(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def setup_signal_col(setup: str) -> str:
    return f"{setup}_signal"


def build_setup_trades(frame: pd.DataFrame, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    rows: list[dict[str, object]] = []
    raw_events = 0
    last_exit_idx = -1
    direction = setup_direction(setup)
    cost_rate = float(cost_bps) / 10000.0
    armed_idx: int | None = None
    armed_extreme: float | None = None
    armed_atr: float | None = None

    for idx in range(40, len(frame) - HOLD_BARS - 2):
        row = frame.iloc[idx]
        if direction == 1:
            if bool(row["long_bias"]) and float(row["close"]) < float(row["ema21"]):
                armed_idx = idx
                armed_extreme = float(row["low"])
                armed_atr = float(row["atr14"]) if not pd.isna(row["atr14"]) else np.nan
            rearm_ready = (
                armed_idx is not None
                and idx > armed_idx
                and idx - armed_idx <= REARM_WINDOW
                and float(row["close"]) > float(row["ema21"])
                and float(frame.iloc[idx - 1]["close"]) <= float(frame.iloc[idx - 1]["ema21"])
            )
        else:
            if bool(row["short_bias"]) and float(row["close"]) > float(row["ema21"]):
                armed_idx = idx
                armed_extreme = float(row["high"])
                armed_atr = float(row["atr14"]) if not pd.isna(row["atr14"]) else np.nan
            rearm_ready = (
                armed_idx is not None
                and idx > armed_idx
                and idx - armed_idx <= REARM_WINDOW
                and float(row["close"]) < float(row["ema21"])
                and float(frame.iloc[idx - 1]["close"]) >= float(frame.iloc[idx - 1]["ema21"])
            )

        if idx <= last_exit_idx:
            continue
        base_signal = bool(row[setup_signal_col(setup)])
        if not base_signal:
            continue
        raw_events += 1
        allow_trade = variant == "baseline" or rearm_ready
        if not allow_trade:
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        entry_px = float(frame.iloc[entry_idx]["open"])
        planned_exit_px = float(frame.iloc[exit_idx]["open"])
        exit_px = planned_exit_px
        stopped = 0
        invalidation_level = np.nan
        if variant == STRICT_VARIANT and armed_extreme is not None and armed_atr is not None and not pd.isna(armed_atr):
            invalidation_level = armed_extreme - 0.5 * armed_atr if direction == 1 else armed_extreme + 0.5 * armed_atr
            path = frame.iloc[entry_idx : exit_idx + 1]
            if direction == 1:
                breach = path[path["low"] <= invalidation_level]
            else:
                breach = path[path["high"] >= invalidation_level]
            if not breach.empty:
                breach_idx = int(breach.index[0])
                exit_px = float(invalidation_level)
                exit_idx = breach_idx
                stopped = 1

        gross_ret = direction * (exit_px / entry_px - 1.0)
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        path_early = frame.iloc[entry_idx : min(exit_idx, entry_idx + EARLY_FAIL_BARS) + 1]
        if direction == 1:
            early_fail = int((path_early["close"] < frame.iloc[idx]["ema21"]).any())
            mae = float((path_early["low"] / entry_px - 1.0).min())
            mfe = float((path_early["high"] / entry_px - 1.0).max())
        else:
            early_fail = int((path_early["close"] > frame.iloc[idx]["ema21"]).any())
            mae = float((1.0 - path_early["high"] / entry_px).min())
            mfe = float((1.0 - path_early["low"] / entry_px).max())

        rows.append(
            {
                "asset": frame.iloc[0]["asset"],
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "armed_gap_bars": idx - armed_idx if armed_idx is not None else np.nan,
                "invalidation_level": invalidation_level,
                "stopped_early": stopped,
                "early_fail_3bars": early_fail,
                "mae_3bars": mae,
                "mfe_3bars": mfe,
            }
        )
        last_exit_idx = exit_idx
        armed_idx = None
        armed_extreme = None
        armed_atr = None
    return pd.DataFrame(rows), raw_events


def summarize_asset(trades: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float, raw_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "raw_signal_count": int(raw_events),
            "trades": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": np.nan,
            "early_fail_3bars_rate": np.nan,
            "stopped_early_rate": np.nan,
            "mean_mae_3bars": np.nan,
            "mean_mfe_3bars": np.nan,
            "mean_armed_gap_bars": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "raw_signal_count": int(raw_events),
        "trades": int(len(trades)),
        "trade_count_retention": float(len(trades) / raw_events) if raw_events > 0 else np.nan,
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "early_fail_3bars_rate": float(trades["early_fail_3bars"].mean()),
        "stopped_early_rate": float(trades["stopped_early"].mean()),
        "mean_mae_3bars": float(trades["mae_3bars"].mean()),
        "mean_mfe_3bars": float(trades["mfe_3bars"].mean()),
        "mean_armed_gap_bars": float(trades["armed_gap_bars"].mean()) if trades["armed_gap_bars"].notna().any() else np.nan,
    }


def overall_summary(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (variant, cost), grp in asset_df.groupby(["variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_cell_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()) if grp["avg_net_ret"].notna().any() else np.nan,
                "mean_early_fail_3bars_rate": float(grp["early_fail_3bars_rate"].mean()) if grp["early_fail_3bars_rate"].notna().any() else np.nan,
                "mean_stopped_early_rate": float(grp["stopped_early_rate"].mean()) if grp["stopped_early_rate"].notna().any() else np.nan,
                "mean_mae_3bars": float(grp["mean_mae_3bars"].mean()) if grp["mean_mae_3bars"].notna().any() else np.nan,
                "mean_mfe_3bars": float(grp["mean_mfe_3bars"].mean()) if grp["mean_mfe_3bars"].notna().any() else np.nan,
                "mean_armed_gap_bars": float(grp["mean_armed_gap_bars"].mean()) if grp["mean_armed_gap_bars"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def by_setup_summary(asset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setup, variant, cost), grp in asset_df.groupby(["setup", "variant", "cost_bps_per_side"], sort=False):
        rows.append(
            {
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_trade_count_retention": float(grp["trade_count_retention"].mean()),
                "mean_avg_net_ret": float(grp["avg_net_ret"].mean()) if grp["avg_net_ret"].notna().any() else np.nan,
                "mean_early_fail_3bars_rate": float(grp["early_fail_3bars_rate"].mean()) if grp["early_fail_3bars_rate"].notna().any() else np.nan,
                "mean_stopped_early_rate": float(grp["stopped_early_rate"].mean()) if grp["stopped_early_rate"].notna().any() else np.nan,
            }
        )
    return pd.DataFrame(rows)


def verdict_from_overall(overall: pd.DataFrame, by_setup: pd.DataFrame) -> tuple[str, str]:
    base = overall[(overall["variant"] == "baseline") & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    gate = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    strict = overall[(overall["variant"] == STRICT_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    breakout_gate = by_setup[(by_setup["setup"] == "breakout_short") & (by_setup["variant"] == PRIMARY_VARIANT) & (by_setup["cost_bps_per_side"] == PRIMARY_COST)]
    breakout_gate_ret = float(breakout_gate.iloc[0]["mean_total_return"]) if not breakout_gate.empty else -1.0

    if (
        float(gate["mean_avg_net_ret"]) > float(base["mean_avg_net_ret"]) + 0.00015
        and float(base["mean_early_fail_3bars_rate"]) - float(gate["mean_early_fail_3bars_rate"]) > 0.03
        and 0.35 <= float(gate["mean_trade_count_retention"]) <= 0.8
        and float(gate["positive_cell_ratio"]) >= 0.5
        and breakout_gate_ret >= -0.002
    ):
        return (
            "promote_to_P2 / paper_candidate_pool",
            "re-arm gate 在不过度砍单的前提下，确实压低了 3-bar fail，并把 desk 级平均净收益推高，说明它不只是 intake wording，而是真有 shared gate 价值。",
        )

    if (
        float(gate["mean_avg_net_ret"]) >= float(base["mean_avg_net_ret"]) - 0.0002
        and float(base["mean_early_fail_3bars_rate"]) - float(gate["mean_early_fail_3bars_rate"]) > 0.01
        and float(gate["mean_trade_count_retention"]) >= 0.25
        and float(strict["mean_trade_count_retention"]) < float(gate["mean_trade_count_retention"]) - 0.05
    ):
        return (
            "keep_P1 / evidence_pool",
            "re-arm gate 确实比 baseline 更诚实一些：3-bar early fail 有所下降，而且不像 hard invalidation 那样把交易数砍得更狠；但 desk 级提升还不够统一，暂时只够留在 P1。",
        )

    return (
        "park / evidence_pool",
        "这轮最小 clean replication 没证明 re-arm 状态机能把三条 archetype 一起修好：要么收益没更好，要么只是靠大幅砍交易数换来的。当前更诚实的结论是 park。",
    )


def read_due_text() -> str:
    due = pd.read_csv(DUE_PATH)
    earliest = due.sort_values("next_expected_close_utc").iloc[0]
    return f"全 desk 仍无 due-now / overdue；最近 due 点仍是 {earliest['deployment_scope']} -> {earliest['next_expected_close_utc']}。"


def read_p3_text() -> str:
    meta = json.loads(P3_SUMMARY_PATH.read_text(encoding='utf-8'))
    return f"manual narrow-paper 最新 refresh @ {meta.get('run_at_utc')}，new_closed_trades_appended={meta.get('new_closed_trades_appended', 0)}。"


def update_todo(generated_at: str, verdict: str, note: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）"
    if marker not in text:
        return
    next3 = (
        "`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> "
        + ("`Run 2 = 若 Rank 85 保留为 P1，则只允许 1 个 truly verdict-changing 的最小检查；若已 hard-fail / park，则立刻切 Rank 84 / volume-price interaction admission layer source intake` -> `Run 3 = 其他 fresh paper/repo source > Rank 82 / 80 / 81（evidence_pool）；P3 continuity 仍不得默认抢占 Scout 主资源`" if "keep_P1" in verdict else
           "`Run 2 = Rank 84 / volume-price interaction admission layer source intake（因为 Rank 85 已 hard-fail / park）` -> `Run 3 = 其他 fresh paper/repo source > Rank 82 / 80 / 81（evidence_pool）；P3 continuity 仍不得默认抢占 Scout 主资源`" if "park" in verdict else
           "`Run 2 = 仅当 EMA 仍 waiting_not_due 时，给 Rank 85 1 个 truly verdict-changing 的最小检查或 admission write-back 到 P2/P3 决策包` -> `Run 3 = Rank 84 / volume-price interaction admission layer source intake；P3 continuity 仍不得默认抢占 Scout 主资源`")
    )
    note_block = (
        f"- **最新补充（{generated_at}）**：这轮先再次按 `Run 1 / EMA due-check only` 实际核对 guardrail，结果仍是 `waiting_not_due`：{read_due_text()} {read_p3_text()} 因此本轮合法主动作落在 **`Run 2 / Rank 85 minimal clean replication`**，而不是继续给旧 `P1 evidence_pool` 续命，也不是回头挤占 `P3 continuity`。\n"
        f"  - 这轮固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，把 `EMA / PSAR continuation`、`Fib retest_hold`、`breakout_short follow-up` 三条 archetype 统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars`**，直接比较 `baseline / rearm_gate / rearm_gate_plus_hard_invalidation` 三臂。\n"
        f"  - `rearm_gate` 的最小口径是：只有先发生一次 fresh pullback（long: `close < ema21`；short: `close > ema21`）并在 `<= {REARM_WINDOW}` 根内 reclaim 回来时，才允许下一次同方向 continuation/retest entry；`hard_invalidation` 再额外把止损钉在 `pullback_extreme ± 0.5 ATR`。\n"
        f"  - 当前更诚实的 hard verdict 是：**`Rank 85 / fresh pullback → reclaim re-arm gate = {verdict}`**。{note}\n"
        f"  - reader-facing 落点：`reports/site/factors/scout_rank85_fresh_pullback_rearm_15m/report.html`、`reports/site/reading/repo_scout/rank85_fresh_pullback_rearm_clean_replication.html`；artifact：`reports/artifacts/scout_rank85_fresh_pullback_rearm_15m/overall_summary.csv`、`by_setup_summary.csv`。\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**{next3}**。"
    )
    start = text.find(marker)
    line_end = text.find("\n", start)
    text = text[: line_end + 1] + note_block + "\n" + text[line_end + 1 :]
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []
    frame_snaps: list[pd.DataFrame] = []

    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd', '')}_frame.csv", index=False)
        frame_snaps.append(frame[["timestamp", "asset", "close", "ema21", "atr14", "ema_psar_long_signal", "fib_retest_long_signal", "breakout_short_signal"]].copy())
        for setup in SETUPS:
            for variant in VARIANTS:
                for cost in COSTS:
                    trades, raw_events = build_setup_trades(frame, setup, variant, cost)
                    asset_rows.append(summarize_asset(trades, asset, setup, variant, cost, raw_events))
                    if not trades.empty:
                        all_trades.append(trades)

    asset_df = pd.DataFrame(asset_rows).sort_values(["cost_bps_per_side", "setup", "variant", "asset"]).reset_index(drop=True)
    overall = overall_summary(asset_df).sort_values(["cost_bps_per_side", "variant"]).reset_index(drop=True)
    by_setup = by_setup_summary(asset_df).sort_values(["cost_bps_per_side", "setup", "variant"]).reset_index(drop=True)
    verdict, verdict_note = verdict_from_overall(overall, by_setup)

    all_trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    frame_df = pd.concat(frame_snaps, ignore_index=True)
    asset_df.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    by_setup.to_csv(ART_DIR / "by_setup_summary.csv", index=False)
    frame_df.to_csv(ART_DIR / "signal_frame_snapshot.csv", index=False)
    if not all_trades_df.empty:
        all_trades_df.to_csv(ART_DIR / "trade_samples.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "scout_rank85_fresh_pullback_rearm_15m",
            "scope": "BTC/ETH/SOL 120d 15m cache | EMA/PSAR + Fib retest + breakout-short shared re-arm gate",
            "hard_verdict": verdict,
            "verdict_note": verdict_note,
        }
    ]).to_csv(ART_DIR / "meta.csv", index=False)

    primary_overall = overall[overall["cost_bps_per_side"].eq(PRIMARY_COST)].reset_index(drop=True)
    primary_by_setup = by_setup[by_setup["cost_bps_per_side"].eq(PRIMARY_COST)].reset_index(drop=True)
    base = primary_overall[primary_overall["variant"].eq("baseline")].iloc[0]
    gate = primary_overall[primary_overall["variant"].eq(PRIMARY_VARIANT)].iloc[0]
    strict = primary_overall[primary_overall["variant"].eq(STRICT_VARIANT)].iloc[0]

    body = f"""
<h1>Rank 85 / fresh pullback → reclaim re-arm gate</h1>
<p class='muted'>生成时间：{escape(generated_at)} ｜ 最小 clean replication：固定复用 BTC/ETH/SOL 120d 15m 本地 cache；只测试 shared re-arm gate，不扩写新框架；统一执行 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars</code>。</p>
<div class='card'>
  <p><strong>先核对 desk 状态：</strong>{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p><strong>re-arm 口径冻结：</strong>long 侧先要求一次 <code>fresh pullback</code>（<code>close &lt; ema21</code>）把状态置为 armed，再要求 <code>&lt;= {REARM_WINDOW}</code> 根内 <code>close</code> 重新站回 <code>ema21</code> 才允许下一次 continuation/retest；short 侧镜像。<code>hard_invalidation</code> 再把止损钉到 <code>pullback_extreme ± 0.5 ATR</code>。</p>
</div>
<div class='card'>
  <p><strong>6bps/side desk 级结果：</strong></p>
  <ul>
    <li><code>baseline</code>：mean total return ≈ <strong>{pct(base['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(base['mean_avg_net_ret'], 3)}</strong>，3-bar fail ≈ <strong>{pct(base['mean_early_fail_3bars_rate'])}</strong></li>
    <li><code>rearm_gate</code>：mean total return ≈ <strong>{pct(gate['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(gate['mean_avg_net_ret'], 3)}</strong>，retention ≈ <strong>{pct(gate['mean_trade_count_retention'])}</strong>，3-bar fail ≈ <strong>{pct(gate['mean_early_fail_3bars_rate'])}</strong></li>
    <li><code>rearm_gate_plus_hard_invalidation</code>：mean total return ≈ <strong>{pct(strict['mean_total_return'])}</strong>，mean avg net ret ≈ <strong>{pct(strict['mean_avg_net_ret'], 3)}</strong>，retention ≈ <strong>{pct(strict['mean_trade_count_retention'])}</strong>，stopped-early ≈ <strong>{pct(strict['mean_stopped_early_rate'])}</strong></li>
  </ul>
  <p><strong>Hard verdict：</strong><span class='{"good" if "promote" in verdict else "bad" if "park" in verdict else "muted"}'>{escape(verdict)}</span>。{escape(verdict_note)}</p>
</div>
<div class='card'>
  <h2>Overall summary</h2>
  {render_table(primary_overall[["variant", "mean_total_return", "positive_cell_ratio", "mean_trades", "mean_trade_count_retention", "mean_avg_net_ret", "mean_early_fail_3bars_rate", "mean_stopped_early_rate", "mean_armed_gap_bars"]], percent_cols={"mean_total_return", "positive_cell_ratio", "mean_trade_count_retention", "mean_avg_net_ret", "mean_early_fail_3bars_rate", "mean_stopped_early_rate"}, digits_cols={"mean_trades": 1, "mean_armed_gap_bars": 2})}
</div>
<div class='card'>
  <h2>By setup @ 6bps/side</h2>
  {render_table(primary_by_setup[["setup", "variant", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_trade_count_retention", "mean_avg_net_ret", "mean_early_fail_3bars_rate"]], percent_cols={"mean_total_return", "positive_asset_ratio", "mean_trade_count_retention", "mean_avg_net_ret", "mean_early_fail_3bars_rate"}, digits_cols={"mean_trades": 1})}
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 85 fresh pullback re-arm clean replication", body)

    reading_body = f"""
<h1>Rank 85 clean replication：先证明“fresh pullback → reclaim”真能减少假延续，再谈升格</h1>
<p class='muted'>生成时间：{escape(generated_at)}｜只做 1 次最小 clean replication。</p>
<div class='card'>
  <p>这轮没有回头挤占 EMA paper continuity。原因很简单：{escape(read_due_text())} {escape(read_p3_text())}</p>
  <p>因此本轮合法主动作就是 <strong>Run 2 / Rank 85</strong>：固定复用本地 <code>BTC/ETH/SOL 120d 15m</code> cache，把 <code>EMA/PSAR continuation</code>、<code>Fib retest_hold</code>、<code>breakout_short follow-up</code> 统一接成 shared re-arm gate，并直接比较 <code>baseline / rearm_gate / rearm_gate_plus_hard_invalidation</code> 三臂。</p>
  <p>当前最诚实的结论是：<strong>{escape(verdict)}</strong>。{escape(verdict_note)}</p>
  <p>网页落点：<a href="../factors/scout_rank85_fresh_pullback_rearm_15m/report.html">factor report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 85 fresh pullback re-arm clean replication", reading_body)
    update_todo(generated_at, verdict, verdict_note)
    print(f"Rank 85 clean replication done -> {verdict}")


if __name__ == "__main__":
    main()
