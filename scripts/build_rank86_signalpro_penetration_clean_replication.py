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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank86_signalpro_penetration_atr_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank86_signalpro_penetration_atr_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank86_signalpro_penetration_atr_clean_replication.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
SETUPS = ["breakout_short", "ema_psar_follow_short", "fib_retest_short"]
VARIANTS = ["baseline", "penetration_only", "atr_only", "pen_plus_atr", "pen_ge_0_10_plus_atr"]
PRIMARY_VARIANT = "pen_plus_atr"
STRICT_VARIANT = "pen_ge_0_10_plus_atr"
COSTS = [6.0, 10.0, 15.0]
PRIMARY_COST = 6.0
LOOKBACK = 30
DONCHIAN = 20
ATR_PERIOD = 14
ATR_RANK_WINDOW = 100
VOL_PERIOD = 20
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
EPS = 1e-9
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


def rolling_percent_rank(series: pd.Series, window: int) -> pd.Series:
    def _rank(values: np.ndarray) -> float:
        if len(values) < 2 or np.isnan(values).any():
            return np.nan
        return float((values[:-1] <= values[-1]).mean() * 100.0)
    return series.rolling(window, min_periods=max(20, window // 2)).apply(_rank, raw=True)


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_cached_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(VOL_PERIOD, min_periods=VOL_PERIOD).mean()
    df["atr14"] = atr(df)
    df["atr_rank"] = rolling_percent_rank(df["atr14"], ATR_RANK_WINDOW).shift(1)
    df["psar"] = compute_psar(df)
    df["donchian_high"] = df["high"].rolling(DONCHIAN, min_periods=DONCHIAN).max().shift(1)
    df["donchian_low"] = df["low"].rolling(DONCHIAN, min_periods=DONCHIAN).min().shift(1)
    df["donchian_range"] = (df["donchian_high"] - df["donchian_low"]).clip(lower=EPS)
    df["swing_high_30"] = df["high"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_382"] = df["swing_low_30"] + 0.382 * rng
    df["fib_50"] = df["swing_low_30"] + 0.5 * rng
    df["fib_618"] = df["swing_low_30"] + 0.618 * rng

    df["breakout_short_signal"] = (
        df["donchian_low"].notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0003)
        & (df["close"].shift(1) > df["donchian_low"].shift(1))
        & (df["close"].shift(2) > df["donchian_low"].shift(2))
        & (df["close"] < df["donchian_low"] - 0.1 * df["atr14"])
        & (df["high"] <= df["donchian_low"] + 0.3 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["breakout_short_trigger_level"] = df["donchian_low"]

    df["ema_psar_follow_short_signal"] = (
        (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < -0.0002)
        & (df["psar"] > df["close"])
        & (df["close"] < df[["low", "ema9"]].min(axis=1).shift(1) - 0.05 * df["atr14"])
        & (df["close"].shift(1) > df["ema9"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["ema_psar_follow_short_trigger_level"] = df[["ema9", "low"]].min(axis=1).shift(1)

    df["fib_retest_short_signal"] = (
        df["fib_382"].notna()
        & (df["ema9"] < df["ema15"])
        & (df["ema_slope"] < 0)
        & (df["close"] < df["fib_382"])
        & (df["close"].shift(1) >= df["fib_382"].shift(1))
        & (df["high"] >= df["fib_382"] - 0.2 * df["atr14"])
        & (df["close"] < df["fib_50"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)
    df["fib_retest_short_trigger_level"] = df["fib_382"]

    for setup in SETUPS:
        trigger_col = f"{setup}_trigger_level"
        pen_col = f"{setup}_penetration"
        df[pen_col] = ((df[trigger_col] - df["close"]) / df["donchian_range"]).clip(lower=0.0)
    return df


def variant_size(row: pd.Series, setup: str, variant: str) -> float:
    pen = float(row.get(f"{setup}_penetration", np.nan)) if not pd.isna(row.get(f"{setup}_penetration", np.nan)) else np.nan
    atr_rank = float(row.get("atr_rank", np.nan)) if not pd.isna(row.get("atr_rank", np.nan)) else np.nan
    if variant == "baseline":
        return 1.0
    if pd.isna(pen) or pd.isna(atr_rank):
        return 0.0
    if variant == "penetration_only":
        return 1.0 if pen >= 0.05 else 0.0
    if variant == "atr_only":
        return 1.0 if atr_rank >= 40.0 else 0.0
    if variant == "pen_plus_atr":
        return 1.0 if (pen >= 0.05 and atr_rank >= 40.0) else 0.0
    if variant == "pen_ge_0_10_plus_atr":
        return 1.0 if (pen >= 0.10 and atr_rank >= 40.0) else 0.0
    raise ValueError(variant)


def build_trades(frame: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float) -> tuple[pd.DataFrame, int]:
    signal_col = f"{setup}_signal"
    trigger_col = f"{setup}_trigger_level"
    pen_col = f"{setup}_penetration"
    rows: list[dict[str, object]] = []
    signal_events = 0
    last_exit_idx = -1
    cost_rate = float(cost_bps) / 10000.0

    for idx in range(40, len(frame) - HOLD_BARS - 2):
        if idx <= last_exit_idx:
            continue
        row = frame.iloc[idx]
        if not bool(row[signal_col]):
            continue
        signal_events += 1
        size = variant_size(row, setup, variant)
        if size <= 0:
            continue
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        if exit_idx >= len(frame):
            break
        entry_px = float(frame.iloc[entry_idx]["open"])
        exit_px = float(frame.iloc[exit_idx]["open"])
        gross_ret = (entry_px / exit_px - 1.0) * size
        path = frame.iloc[entry_idx : entry_idx + EARLY_FAIL_BARS + 1]
        trigger = float(row[trigger_col])
        fail_4bars = bool((path["close"] > trigger).any())
        best_move = float((entry_px / path["low"] - 1.0).max()) * size
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "cost_bps_per_side": float(cost_bps),
                "signal_ts": pd.to_datetime(row["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(frame.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(frame.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_price": entry_px,
                "exit_price": exit_px,
                "size": size,
                "gross_ret": gross_ret,
                "net_ret": (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0,
                "expectancy": gross_ret - 2.0 * cost_rate * size,
                "fail_4bars": int(fail_4bars),
                "penetration": float(row[pen_col]),
                "atr_rank": float(row["atr_rank"]),
                "trigger_level": trigger,
                "best_move_4bars": best_move,
            }
        )
        last_exit_idx = exit_idx
    return pd.DataFrame(rows), signal_events


def summarize_group(trades: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float, signal_events: int) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "setup": setup,
            "variant": variant,
            "cost_bps_per_side": float(cost_bps),
            "signal_events": int(signal_events),
            "trade_count": 0,
            "trade_count_retention": 0.0,
            "total_return": 0.0,
            "avg_net_ret": 0.0,
            "win_rate": 0.0,
            "false_follow_4bars_rate": np.nan,
            "mean_penetration": np.nan,
            "mean_atr_rank": np.nan,
            "mean_best_move_4bars": np.nan,
        }
    return {
        "asset": asset,
        "setup": setup,
        "variant": variant,
        "cost_bps_per_side": float(cost_bps),
        "signal_events": int(signal_events),
        "trade_count": int(len(trades)),
        "trade_count_retention": float(len(trades) / signal_events) if signal_events else 0.0,
        "total_return": float(trades["net_ret"].sum()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "false_follow_4bars_rate": float(trades["fail_4bars"].mean()),
        "mean_penetration": float(trades["penetration"].mean()),
        "mean_atr_rank": float(trades["atr_rank"].mean()),
        "mean_best_move_4bars": float(trades["best_move_4bars"].mean()),
    }


def patch_todo(latest_due_line: str, p3_zero: bool, verdict: str, next_run3: str) -> None:
    text = (ROOT / "docs" / "TODO.md").read_text(encoding="utf-8")
    marker = "### Next 3 bot3 runs（当前默认执行顺序）\n"
    if marker not in text:
        raise RuntimeError("Next 3 marker not found in TODO.md")
    head, tail = text.split(marker, 1)
    insert = (
        f"- **最新补充（{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}）**：这轮先再次按 `Run 1 / EMA due-check only` 实际核对 guardrail，结果仍是 `waiting_not_due`：{latest_due_line}。"
        f"`manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，因此本轮合法主动作继续落在 **`Run 2 / Rank 86 minimal clean replication`**，而不是回头挤占 `P3 continuity`。\n"
        f"  - 这轮固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，把 `breakout_short / EMA-PSAR follow-up short / Fib retest short` 三条 archetype 统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**，直接比较 `baseline / penetration_only / atr_only / penetration+atr / strict_pen+atr` 五臂。\n"
        f"  - 当前更诚实的 hard verdict 是：**`Rank 86 / SignalPro penetration×ATR admission = {verdict}`**。\n"
        f"  - reader-facing 落点：`reports/site/factors/scout_rank86_signalpro_penetration_atr_15m/report.html`、`reports/site/reading/repo_scout/rank86_signalpro_penetration_atr_clean_replication.html`；artifact：`reports/artifacts/scout_rank86_signalpro_penetration_atr_15m/overall_summary.csv`、`setup_summary.csv`。\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only（若脚本仍返回 waiting_not_due，不得空转）` -> `Run 2 = {next_run3}`**。\n"
    )
    (ROOT / "docs" / "TODO.md").write_text(head + marker + insert + tail, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames: dict[str, pd.DataFrame] = {}
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frames[asset] = frame
        frame.to_csv(ART_DIR / f"{symbol.lower()}_frame.csv", index=False)

    asset_rows: list[dict[str, object]] = []
    trade_frames: list[pd.DataFrame] = []
    setup_rows: list[dict[str, object]] = []

    for asset, frame in frames.items():
        for setup in SETUPS:
            for cost in COSTS:
                for variant in VARIANTS:
                    trades, signal_events = build_trades(frame, asset, setup, variant, cost)
                    if not trades.empty:
                        trade_frames.append(trades)
                    asset_rows.append(summarize_group(trades, asset, setup, variant, cost, signal_events))

    asset_summary = pd.DataFrame(asset_rows)
    trades_df = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    asset_summary.to_csv(ART_DIR / "asset_setup_summary.csv", index=False)
    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trade_samples.csv", index=False)

    cost_mask = asset_summary["cost_bps_per_side"] == PRIMARY_COST
    primary = asset_summary[cost_mask].copy()
    setup_summary = (
        primary.groupby(["setup", "variant"], dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trade_count=("trade_count", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_false_follow_4bars_rate=("false_follow_4bars_rate", "mean"),
            mean_penetration=("mean_penetration", "mean"),
            mean_atr_rank=("mean_atr_rank", "mean"),
            mean_best_move_4bars=("mean_best_move_4bars", "mean"),
        )
        .reset_index()
        .sort_values(["setup", "variant"])
    )
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)

    overall_summary = (
        primary.groupby("variant", dropna=False)
        .agg(
            mean_total_return=("total_return", "mean"),
            mean_avg_net_ret=("avg_net_ret", "mean"),
            positive_asset_ratio=("total_return", lambda s: float((s > 0).mean())),
            mean_trade_count=("trade_count", "mean"),
            mean_trade_count_retention=("trade_count_retention", "mean"),
            mean_false_follow_4bars_rate=("false_follow_4bars_rate", "mean"),
            mean_penetration=("mean_penetration", "mean"),
            mean_atr_rank=("mean_atr_rank", "mean"),
            mean_best_move_4bars=("mean_best_move_4bars", "mean"),
        )
        .reset_index()
    )
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)

    primary_row = overall_summary.loc[overall_summary["variant"] == PRIMARY_VARIANT].iloc[0]
    base_row = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    strict_row = overall_summary.loc[overall_summary["variant"] == STRICT_VARIANT].iloc[0]
    verdict = "park / evidence_pool"
    if (
        float(primary_row["mean_total_return"]) > float(base_row["mean_total_return"]) + 0.01
        and float(primary_row["positive_asset_ratio"]) >= 2 / 3
        and float(primary_row["mean_trade_count_retention"]) >= 0.35
        and float(primary_row["mean_false_follow_4bars_rate"]) <= float(base_row["mean_false_follow_4bars_rate"]) - 0.03
    ):
        verdict = "P1 keep / worth one Light Stability Pack check"

    meta = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "primary_cost_bps_per_side": PRIMARY_COST,
            "hold_bars": HOLD_BARS,
            "early_fail_bars": EARLY_FAIL_BARS,
            "primary_variant": PRIMARY_VARIANT,
            "strict_variant": STRICT_VARIANT,
            "verdict": verdict,
            "baseline_mean_total_return": float(base_row["mean_total_return"]),
            "primary_mean_total_return": float(primary_row["mean_total_return"]),
            "strict_mean_total_return": float(strict_row["mean_total_return"]),
        }
    ])
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    title = "Rank 86 / SignalPro penetration×ATR admission — minimal clean replication"
    verdict_class = "good" if verdict.startswith("P1") else "bad"
    body = f"""
<h1>{escape(title)}</h1>
<p class='muted'>固定复用 BTC/ETH/SOL 120d 15m 本地 cache，执行冻结为 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>
<div class='card'>
  <h2>本轮 hard verdict</h2>
  <p class='{verdict_class}'>{escape(verdict)}</p>
  <p>主变体 <code>{PRIMARY_VARIANT}</code> 对照 <code>baseline</code>：mean_total_return {num(primary_row['mean_total_return'])} vs {num(base_row['mean_total_return'])}，positive_asset_ratio {pct(primary_row['positive_asset_ratio'])} vs {pct(base_row['positive_asset_ratio'])}，false_follow_4bars_rate {pct(primary_row['mean_false_follow_4bars_rate'])} vs {pct(base_row['mean_false_follow_4bars_rate'])}。</p>
</div>
<div class='card'>
  <h2>overall summary（6 bps/side）</h2>
  {render_table(overall_summary, percent_cols={'mean_total_return','mean_avg_net_ret','positive_asset_ratio','mean_trade_count_retention','mean_false_follow_4bars_rate','mean_penetration','mean_best_move_4bars'}, digits_cols={'mean_trade_count':1,'mean_atr_rank':1})}
</div>
<div class='card'>
  <h2>setup summary（6 bps/side）</h2>
  {render_table(setup_summary, percent_cols={'mean_total_return','mean_avg_net_ret','positive_asset_ratio','mean_trade_count_retention','mean_false_follow_4bars_rate','mean_penetration','mean_best_move_4bars'}, digits_cols={'mean_trade_count':1,'mean_atr_rank':1})}
</div>
<div class='card'>
  <h2>说明</h2>
  <ul>
    <li><code>penetration_only</code> = penetration ≥ 0.05</li>
    <li><code>atr_only</code> = trailing ATR percentile ≥ 40</li>
    <li><code>pen_plus_atr</code> = penetration ≥ 0.05 且 ATR percentile ≥ 40</li>
    <li><code>pen_ge_0_10_plus_atr</code> = 更严格版本：penetration ≥ 0.10 且 ATR percentile ≥ 40</li>
  </ul>
</div>
"""
    write_html(SITE_DIR / "report.html", title, body)
    write_html(READING_PATH, title, body)

    due_out = ROOT / "tmp" / "rank86_due_check.txt"
    due_out.parent.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()
