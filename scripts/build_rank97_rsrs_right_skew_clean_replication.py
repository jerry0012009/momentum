#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank97_rsrs_right_skew_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank97_rsrs_right_skew_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank97_rsrs_right_skew_clean_replication.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["no_overlay", "hard_veto", "half_size_overlay", "tiered_sizing_overlay"]
PRIMARY_VARIANT = "tiered_sizing_overlay"
PRIMARY_COST_BPS = 6.0
COSTS_BPS = [6.0]
HOLD_BARS = 8
EARLY_FAIL_BARS = 4
RSRS_N = 18
RSRS_M = 300
ROLL_MIN = 120
Q_LOW = 0.30
Q_HIGH = 0.70
EPS = 1e-12
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


def load_bars(symbol: str, asset: str) -> pd.DataFrame:
    df = pd.read_csv(CACHE_DIR / f"{symbol}__120d__15m.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
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


def rolling_rsrs(df: pd.DataFrame, n: int = RSRS_N, m: int = RSRS_M) -> pd.DataFrame:
    x = df["low"]
    y = df["high"]
    mean_x = x.rolling(n, min_periods=n).mean()
    mean_y = y.rolling(n, min_periods=n).mean()
    cov = (x * y).rolling(n, min_periods=n).mean() - mean_x * mean_y
    var_x = (x * x).rolling(n, min_periods=n).mean() - mean_x * mean_x
    beta = cov / var_x.replace(0.0, np.nan)
    alpha = mean_y - beta * mean_x
    fitted = beta * x + alpha
    resid = y - fitted
    ss_res = (resid * resid).rolling(n, min_periods=n).sum()
    ss_tot = ((y - mean_y) ** 2).rolling(n, min_periods=n).sum()
    r2 = 1.0 - ss_res / ss_tot.replace(0.0, np.nan)
    beta_mean = beta.rolling(m, min_periods=ROLL_MIN).mean().shift(1)
    beta_std = beta.rolling(m, min_periods=ROLL_MIN).std(ddof=0).shift(1)
    zscore = (beta - beta_mean) / beta_std.replace(0.0, np.nan)
    modified = zscore * r2.clip(lower=0.0)
    right_skew = modified * beta
    q30 = right_skew.shift(1).rolling(m, min_periods=ROLL_MIN).quantile(Q_LOW)
    q70 = right_skew.shift(1).rolling(m, min_periods=ROLL_MIN).quantile(Q_HIGH)
    out = pd.DataFrame(index=df.index)
    out["rsrs_beta"] = beta
    out["rsrs_r2"] = r2.clip(lower=0.0)
    out["rsrs_zscore"] = zscore
    out["rsrs_modified_score"] = modified
    out["rsrs_right_skew"] = right_skew
    out["rsrs_q30"] = q30
    out["rsrs_q70"] = q70
    out["rsrs_ready"] = out[["rsrs_right_skew", "rsrs_q30", "rsrs_q70"]].notna().all(axis=1)
    out["rsrs_high_state"] = (out["rsrs_right_skew"] >= out["rsrs_q70"]).fillna(False)
    out["rsrs_low_state"] = (out["rsrs_right_skew"] <= out["rsrs_q30"]).fillna(False)
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["atr14"] = atr(df)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["psar"] = compute_psar(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_382"] = df["swing_low_30"] + 0.382 * rng
    df["fib_500"] = df["swing_low_30"] + 0.500 * rng
    df["fib_618"] = df["swing_low_30"] + 0.618 * rng
    df["donchian_low"] = df["low"].rolling(20, min_periods=20).min().shift(1)

    df["ema_psar_long_signal"] = (
        (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0.0002)
        & (df["psar"] < df["close"])
        & (df["close"].shift(1) < df["ema9"].shift(1))
        & (df["close"] > df["ema9"])
        & (df["close"] > df["high"].shift(1) - 0.15 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema21"])
        & (df["ema_slope"] > 0)
        & (df["low"] <= df["fib_618"] + 0.15 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["close"].shift(1) <= df["fib_500"].shift(1))
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    df["breakout_short_signal"] = (
        df["donchian_low"].notna()
        & (df["ema9"] < df["ema21"])
        & (df["ema_slope"] < -0.0002)
        & (df["close"].shift(1) > df["donchian_low"].shift(1))
        & (df["close"] < df["donchian_low"] - 0.1 * df["atr14"])
        & (df["volume"] > df["vol_ma20"])
    ).fillna(False)

    rsrs = rolling_rsrs(df)
    return pd.concat([df, rsrs], axis=1)


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def size_for_variant(row: pd.Series, setup: str, variant: str) -> float:
    if not bool(row.get("rsrs_ready", False)):
        return 1.0 if variant == "no_overlay" else 0.0
    high = bool(row.get("rsrs_high_state", False))
    low = bool(row.get("rsrs_low_state", False))
    is_long = setup in LONG_SETUPS
    adverse = low if is_long else high
    favorable = high if is_long else low
    if variant == "no_overlay":
        return 1.0
    if variant == "hard_veto":
        return 0.0 if adverse else 1.0
    if variant == "half_size_overlay":
        return 0.5 if adverse else 1.0
    if variant == "tiered_sizing_overlay":
        if adverse:
            return 0.5
        if favorable:
            return 1.25
        return 1.0
    raise ValueError(variant)


def simulate_variant(df: pd.DataFrame, asset: str, setup: str, variant: str, cost_bps: float) -> list[dict]:
    sig_col = f"{setup}_signal"
    direction = direction_for_setup(setup)
    rows: list[dict] = []
    last_exit = -1
    cost = cost_bps / 10000.0

    signal = df[sig_col].to_numpy(dtype=bool)
    open_px = df["open"].to_numpy(dtype=float)
    close_px = df["close"].to_numpy(dtype=float)
    ts = df["timestamp"].to_numpy()
    ready = df["rsrs_ready"].to_numpy(dtype=bool)
    high_state = df["rsrs_high_state"].to_numpy(dtype=bool)
    low_state = df["rsrs_low_state"].to_numpy(dtype=bool)
    rsrs_right = df["rsrs_right_skew"].to_numpy(dtype=float)
    q30 = df["rsrs_q30"].to_numpy(dtype=float)
    q70 = df["rsrs_q70"].to_numpy(dtype=float)
    is_long = setup in LONG_SETUPS

    for idx in range(len(df) - HOLD_BARS - 1):
        if idx <= last_exit or not signal[idx]:
            continue
        if variant == "no_overlay":
            size = 1.0
        else:
            if not ready[idx]:
                size = 0.0
            else:
                adverse = low_state[idx] if is_long else high_state[idx]
                favorable = high_state[idx] if is_long else low_state[idx]
                if variant == "hard_veto":
                    size = 0.0 if adverse else 1.0
                elif variant == "half_size_overlay":
                    size = 0.5 if adverse else 1.0
                else:
                    size = 0.5 if adverse else (1.25 if favorable else 1.0)
        if size <= 0:
            continue
        entry_idx = idx + 1
        exit_idx = idx + HOLD_BARS
        if exit_idx >= len(df):
            continue
        entry = open_px[entry_idx]
        exitp = close_px[exit_idx]
        gross = direction * (exitp / entry - 1.0)
        net = gross - 2.0 * cost
        early_idx = min(idx + EARLY_FAIL_BARS, len(df) - 1)
        fail_price = close_px[early_idx]
        early_ret = direction * (fail_price / entry - 1.0) - 2.0 * cost
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "variant": variant,
                "signal_timestamp": ts[idx],
                "entry_timestamp": ts[entry_idx],
                "exit_timestamp": ts[exit_idx],
                "direction": direction,
                "position_size": size,
                "rsrs_right_skew": rsrs_right[idx],
                "rsrs_q30": q30[idx],
                "rsrs_q70": q70[idx],
                "gross_return": gross * size,
                "net_return": net * size,
                "turnover": 2.0 * size,
                "early_fail_4bars": int(early_ret < 0),
                "adverse_overlay_hit": int(size < 1.0),
                "favorable_overlay_hit": int(size > 1.0),
            }
        )
        last_exit = exit_idx
    return rows


def summarize(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    overall = (
        trades.groupby(["variant", "cost_bps"], as_index=False)
        .agg(
            mean_total_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            mean_trade_count=("net_return", "size"),
            mean_position_size=("position_size", "mean"),
            mean_turnover=("turnover", "sum"),
            mean_early_fail_4bars=("early_fail_4bars", "mean"),
            veto_hit_rate=("adverse_overlay_hit", "mean"),
            sizeup_hit_rate=("favorable_overlay_hit", "mean"),
            positive_asset_ratio=("asset", lambda s: np.nan),
        )
    )
    pa = (
        trades.groupby(["variant", "cost_bps", "asset"], as_index=False)
        .agg(total_return=("net_return", "sum"), trade_count=("net_return", "size"), mean_position_size=("position_size", "mean"), veto_hit_rate=("adverse_overlay_hit", "mean"))
    )
    ratio = pa.groupby(["variant", "cost_bps"]).apply(lambda g: (g["total_return"] > 0).mean()).rename("positive_asset_ratio").reset_index()
    overall = overall.drop(columns=["positive_asset_ratio"]).merge(ratio, on=["variant", "cost_bps"], how="left")

    asset_summary = (
        trades.groupby(["variant", "cost_bps", "asset"], as_index=False)
        .agg(
            total_return=("net_return", "sum"),
            trade_count=("net_return", "size"),
            avg_position_size=("position_size", "mean"),
            early_fail_4bars=("early_fail_4bars", "mean"),
            veto_hit_rate=("adverse_overlay_hit", "mean"),
            sizeup_hit_rate=("favorable_overlay_hit", "mean"),
        )
    )

    setup_summary = (
        trades.groupby(["variant", "cost_bps", "setup"], as_index=False)
        .agg(
            total_return=("net_return", "sum"),
            trade_count=("net_return", "size"),
            avg_position_size=("position_size", "mean"),
            early_fail_4bars=("early_fail_4bars", "mean"),
            veto_hit_rate=("adverse_overlay_hit", "mean"),
        )
    )

    cost_summary = overall.copy()
    return overall, asset_summary, setup_summary, cost_summary


def verdict_note(primary_row: pd.Series, baseline_row: pd.Series) -> tuple[str, str]:
    improve = float(primary_row["total_return"]) - float(baseline_row["total_return"])
    retention = float(primary_row["mean_trade_count"]) / max(float(baseline_row["mean_trade_count"]), 1.0)
    pos_ratio = float(primary_row["positive_asset_ratio"])
    early_fail = float(primary_row["mean_early_fail_4bars"])
    veto = float(primary_row["veto_hit_rate"])
    sizeup = float(primary_row["sizeup_hit_rate"])
    if improve > 0.06 and pos_ratio >= 2 / 3 and retention >= 0.55 and early_fail <= float(baseline_row["mean_early_fail_4bars"]) + 0.03:
        return "promote_to_P2", "RSRS overlay 在成本后给出跨资产更统一的减亏/转正，同时没有靠过度砍样本换结果。"
    if improve > 0.02 and retention >= 0.45:
        return "keep_P1", f"RSRS overlay 确实减亏，但更像 shared sizing/veto 弱线索：`6bps` 下总收益较 baseline 改善 {improve:.2%}，trade retention≈{retention:.2%}，positive_asset_ratio≈{pos_ratio:.2%}，仍不足以直接升 P2。"
    return "park", f"RSRS overlay 没把当前 desk judgement 真正推过门槛：`6bps` 下相对 baseline 改善 {improve:.2%}、trade retention≈{retention:.2%}、positive_asset_ratio≈{pos_ratio:.2%}、veto_hit_rate≈{veto:.2%}、sizeup_hit_rate≈{sizeup:.2%}；更像局部 sizing 噪声，不值得继续占主资源。"


def update_todo(generated_at: str, verdict: str, note: str) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    anchor = "- **最新补充（2026-03-19 18:56 UTC，bot2 desk review）**：当前最新 `Next 3` 顺序应再收紧为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 97 / RSRS right-skew shared veto + sizing overlay 1 次最小 clean replication（固定 BTC/ETH/SOL | 120d | 15m，本轮只比较 no_overlay / hard_veto(q30-q70) / half_size_overlay / tiered_sizing_overlay，并直接回答 keep_P1 / promote_to_P2 / park）` -> `Run 3 = 若 Rank 97 clean replication 仍存活，则只给 1 个 truly verdict-changing 的 Light Stability Pack（默认先做时间稳定性，并直接回答 promote_to_P2 / keep_P1 / park）；若 Rank 97 在 clean replication 直接 hard-fail / park，则先切 `Fib placebo-zone honesty gate` 的 source intake；只有 Fib 这一层也 hard-fail / exhausted，才轮到 `CLV asymmetric admission layer reserve`，再之后才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 96 / Rank 95 / Rank 92 / Rank 94 park > P3 continuity > tiny-live plumbing`**。"
    if anchor not in text:
        return
    insertion = (
        f"\n- **最新补充（{generated_at}）**：这轮继续严格按 `Run 1 -> Run 2` 执行：`EMA` due-check 仍真实返回 **`waiting_not_due`**，因此本轮合法主动作就是把 **`Rank 97 / RSRS right-skew shared veto + sizing overlay`** 的那 1 次最小 clean replication 跑完。\n"
        f"  - 本轮新增并执行：`python3 scripts/build_rank97_rsrs_right_skew_clean_replication.py`，固定复用 `BTC/ETH/SOL | 120d | 15m` 本地 cache，统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap + hold {HOLD_BARS} bars`**，比较 `no_overlay / hard_veto / half_size_overlay / tiered_sizing_overlay` 四臂。\n"
        f"  - 当前更诚实的 hard verdict 已冻结为：**`Rank 97 = {verdict}`**。{note}\n"
        f"  - reader-facing 落点已补：`reports/site/factors/scout_rank97_rsrs_right_skew_15m/report.html` 与 `reports/site/reading/repo_scout/rank97_rsrs_right_skew_clean_replication.html`；artifact：`reports/artifacts/scout_rank97_rsrs_right_skew_15m/overall_summary.csv`、`asset_summary.csv`、`setup_summary.csv`。\n"
        f"  - 因此当前最新 `Next 3` 顺序应更新为：**`Run 1 = EMA due-check only` -> `Run 2 = 若 EMA 仍 waiting_not_due，则先切 Fib placebo-zone honesty gate 的 source intake` -> `Run 3 = 若 Fib guard-pass，则只给它 1 次最小 clean replication；只有 Fib 这一层也 hard-fail / exhausted，才轮到 CLV asymmetric admission layer reserve，再之后才允许回退到 Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 park > P3 continuity > tiny-live plumbing`**。\n"
    )
    text = text.replace(anchor, anchor + insertion, 1)
    text = text.replace(
        "**`Rank 97 = P1 weak candidate（guard-passed / minimal clean replication next）`**、**`Fib placebo-zone honesty gate = P0（fresh paper honesty-gate intake reserve）`**、**`CLV asymmetric admission layer reserve = P0（fresh repo reserve / not yet queue-facing）`**、**`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1 evidence_pool`**、**`Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0 park`**",
        f"**`Rank 97 = {'P1 weak candidate（keep_P1 / Light Stability Pack next）' if verdict == 'keep_P1' else 'P2 paper candidate（最小 stability / admission writeback next）' if verdict == 'promote_to_P2' else 'P0 park / evidence pool'}`**、**`Fib placebo-zone honesty gate = P0（fresh paper honesty-gate intake reserve）`**、**`CLV asymmetric admission layer reserve = P0（fresh repo reserve / not yet queue-facing）`**、**`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1 evidence_pool`**、**`Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0 park`**",
        1,
    )
    TODO_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = []
    all_trades: list[dict] = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.replace('-', '_').lower()}_frame.csv", index=False)
        frames.append(frame)
        for cost_bps in COSTS_BPS:
            for setup in SETUPS:
                rows = simulate_variant(frame, asset, setup, "no_overlay", cost_bps)
                for r in rows:
                    r["cost_bps"] = cost_bps
                all_trades.extend(rows)
                for variant in VARIANTS[1:]:
                    rows = simulate_variant(frame, asset, setup, variant, cost_bps)
                    for r in rows:
                        r["cost_bps"] = cost_bps
                    all_trades.extend(rows)

    trades = pd.DataFrame(all_trades)
    trades.to_csv(ART_DIR / "trades.csv", index=False)
    overall, asset_summary, setup_summary, cost_summary = summarize(trades)
    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)

    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps"] == PRIMARY_COST_BPS)].iloc[0]
    baseline = overall[(overall["variant"] == "no_overlay") & (overall["cost_bps"] == PRIMARY_COST_BPS)].iloc[0]
    verdict, note = verdict_note(primary, baseline)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    meta = pd.DataFrame(
        [
            {
                "generated_at_utc": generated_at,
                "primary_variant": PRIMARY_VARIANT,
                "primary_cost_bps": PRIMARY_COST_BPS,
                "hold_bars": HOLD_BARS,
                "rsrs_n": RSRS_N,
                "rsrs_m": RSRS_M,
                "q30": Q_LOW,
                "q70": Q_HIGH,
                "verdict": verdict,
                "note": note,
            }
        ]
    )
    meta.to_csv(ART_DIR / "meta.csv", index=False)

    summary_card = pd.DataFrame(
        [
            {
                "variant": "baseline",
                "mean_total_return": baseline["mean_total_return"],
                "total_return": baseline["total_return"],
                "trade_count": baseline["mean_trade_count"],
                "positive_asset_ratio": baseline["positive_asset_ratio"],
            },
            {
                "variant": PRIMARY_VARIANT,
                "mean_total_return": primary["mean_total_return"],
                "total_return": primary["total_return"],
                "trade_count": primary["mean_trade_count"],
                "positive_asset_ratio": primary["positive_asset_ratio"],
            },
        ]
    )

    body = f"""
<h1>Rank 97 / RSRS right-skew shared veto + sizing overlay</h1>
<div class='card'>
  <p><strong>本轮最小 clean replication 结论：</strong><span class='{'good' if verdict != 'park' else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(note)}</p>
  <p class='muted'>固定 BTC/ETH/SOL | 120d | 15m，本轮只比较 <code>no_overlay / hard_veto / half_size_overlay / tiered_sizing_overlay</code>，统一使用 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars</code>。</p>
</div>
<div class='card'>
  <h2>主结论对照（6bps/side）</h2>
  {render_table(summary_card, percent_cols={'mean_total_return','total_return','positive_asset_ratio'})}
</div>
<div class='card'>
  <h2>总体汇总</h2>
  {render_table(overall, percent_cols={'mean_total_return','total_return','mean_early_fail_4bars','veto_hit_rate','sizeup_hit_rate','positive_asset_ratio'}, digits_cols={'cost_bps':0,'mean_trade_count':0,'mean_position_size':2,'mean_turnover':2})}
</div>
<div class='card'>
  <h2>按资产</h2>
  {render_table(asset_summary[asset_summary['cost_bps'] == PRIMARY_COST_BPS], percent_cols={'total_return','early_fail_4bars','veto_hit_rate','sizeup_hit_rate'}, digits_cols={'cost_bps':0,'trade_count':0,'avg_position_size':2})}
</div>
<div class='card'>
  <h2>按 setup</h2>
  {render_table(setup_summary[setup_summary['cost_bps'] == PRIMARY_COST_BPS], percent_cols={'total_return','early_fail_4bars','veto_hit_rate'}, digits_cols={'cost_bps':0,'trade_count':0,'avg_position_size':2})}
</div>
<div class='card'>
  <p>产物目录：<code>{escape(str(ART_DIR.relative_to(ROOT)))}</code></p>
  <p>Reader-facing reading 页：<a href="../../reading/repo_scout/rank97_rsrs_right_skew_clean_replication.html">repo_scout / clean replication</a></p>
</div>
"""
    write_html(SITE_DIR / "report.html", "Rank 97 RSRS right-skew clean replication", body)

    reading_body = f"""
<h1>Rank 97 / RSRS right-skew clean replication</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(note)}</p>
  <p>这轮不再谈 source intake，而是只回答：把 RSRS right-skew 当 shared veto / sizing overlay，是否真能在不改 base setup 方向逻辑的前提下，给 desk 带来更诚实的成本后改善。</p>
</div>
<div class='card'>
  <h2>主结论（6bps/side）</h2>
  {render_table(summary_card, percent_cols={'mean_total_return','total_return','positive_asset_ratio'})}
</div>
<div class='card'>
  <h2>怎么读</h2>
  <ul>
    <li><code>hard_veto</code>：不利 regime 直接禁入。</li>
    <li><code>half_size_overlay</code>：不利 regime 半仓，其他维持原样。</li>
    <li><code>tiered_sizing_overlay</code>：不利 <code>0.5x</code>、中性 <code>1.0x</code>、有利 <code>1.25x</code>。</li>
  </ul>
  <p>若结果只靠大幅砍 trade count 或极偏的单资产 pocket 才改善，就不应升格。</p>
</div>
<div class='card'>
  <p>网页落点：<a href="../factors/scout_rank97_rsrs_right_skew_15m/report.html">factor report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank 97 RSRS right-skew clean replication", reading_body)

    update_todo(generated_at, verdict, note)
    print(f"generated_at={generated_at}")
    print(f"verdict={verdict}")
    print(f"note={note}")


if __name__ == "__main__":
    main()
