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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank111_event_clock_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank111_event_clock_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank111_event_clock_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "same_window_only", "window_plus_timeout"]
PRIMARY_COST = 6.0
HOLD_BARS = 8
FALSE_WINDOW = 4
EVENT_WINDOW = 12
TIMEOUT_WINDOW = 24
ROLLING_EVENT = 96
EVENT_K = 2.0
EPS = 1e-12
CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
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
    rows = []
    for _, row in df.iterrows():
        cells = []
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ret_1"] = df["close"].pct_change()
    df["absret_mu"] = df["ret_1"].abs().rolling(ROLLING_EVENT, min_periods=ROLLING_EVENT).mean()
    df["absret_sigma"] = df["ret_1"].abs().rolling(ROLLING_EVENT, min_periods=ROLLING_EVENT).std()
    event_thr = df["absret_mu"] + EVENT_K * df["absret_sigma"]
    event_hit = df["ret_1"].abs() > event_thr
    event_dir = np.sign(df["ret_1"]).replace(0, np.nan)

    last_event_idx = []
    last_event_dir = []
    idx_mem = None
    dir_mem = np.nan
    for i, hit in enumerate(event_hit.fillna(False).to_list()):
        if hit and pd.notna(event_dir.iloc[i]):
            idx_mem = i
            dir_mem = int(np.sign(event_dir.iloc[i]))
        last_event_idx.append(idx_mem)
        last_event_dir.append(dir_mem)
    df["last_event_idx"] = last_event_idx
    df["last_event_dir"] = last_event_dir
    df["event_age"] = [np.nan if idx is None else i - idx for i, idx in enumerate(last_event_idx)]
    df["event_hit"] = event_hit.fillna(False)

    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["psar"] = compute_psar(df)
    df["rolling_low20"] = df["low"].rolling(20, min_periods=20).min().shift(1)
    df["rolling_high20"] = df["high"].rolling(20, min_periods=20).max().shift(1)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_500"] = df["swing_high_30"] - 0.500 * rng

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
        & (df["close"] > df["fib_500"])
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


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def reconfirm_ok(row: pd.Series, setup: str) -> bool:
    if setup in LONG_SETUPS:
        return bool(row["close"] > row["high"].shift(1) if False else ((row["close"] > row["ema9"]) and (row["close"] > row["open"])) )
    return bool((row["close"] < row["ema9"]) and (row["close"] < row["open"]))


def variant_decision(row: pd.Series, setup: str, variant: str) -> tuple[bool, str]:
    if variant == "baseline":
        return True, "baseline"
    direction = direction_for_setup(setup)
    event_dir = row.get("event_dir")
    event_age = row.get("event_age")
    if pd.isna(event_dir) or pd.isna(event_age):
        return False, "no_recent_event"
    if int(np.sign(event_dir)) != direction:
        return False, "event_direction_mismatch"
    if event_age <= EVENT_WINDOW:
        return True, "same_window_event"
    if variant == "same_window_only":
        return False, "timed_out"
    if event_age <= TIMEOUT_WINDOW:
        if setup in LONG_SETUPS:
            ok = bool((row["close"] > row["ema9"]) and (row["close"] > row["open"]))
        else:
            ok = bool((row["close"] < row["ema9"]) and (row["close"] < row["open"]))
        return ok, "timeout_reconfirm" if ok else "timeout_no_reconfirm"
    return False, "timeout_expired"


def collect_events(frame: pd.DataFrame, asset: str, setup: str) -> pd.DataFrame:
    rows = []
    direction = direction_for_setup(setup)
    signal_col = f"{setup}_signal"
    signal_idx = np.flatnonzero(frame[signal_col].fillna(False).to_numpy())
    for idx in signal_idx:
        entry_idx = idx + 1
        exit_idx = entry_idx + HOLD_BARS
        fail_idx = entry_idx + FALSE_WINDOW
        if exit_idx >= len(frame):
            continue
        row = frame.iloc[idx]
        entry = frame.iloc[entry_idx]
        exit_row = frame.iloc[exit_idx]
        fail_row = frame.iloc[fail_idx]
        entry_price = float(entry["open"])
        exit_price = float(exit_row["close"])
        if not np.isfinite(entry_price) or not np.isfinite(exit_price) or entry_price <= 0 or exit_price <= 0:
            continue
        gross = direction * (exit_price / entry_price - 1.0)
        early = direction * (float(fail_row["close"]) / entry_price - 1.0)
        rows.append(
            {
                "asset": asset,
                "setup": setup,
                "side": "long" if direction > 0 else "short",
                "signal_idx": int(idx),
                "signal_time": row["timestamp"],
                "entry_idx": int(entry_idx),
                "entry_time": entry["timestamp"],
                "entry_price": entry_price,
                "exit_idx": int(exit_idx),
                "exit_time": exit_row["timestamp"],
                "exit_price": exit_price,
                "gross_return": gross,
                "early_return_4": early,
                "false_follow_through_4bars": early <= 0,
                "event_age": float(row["event_age"]) if pd.notna(row["event_age"]) else np.nan,
                "event_dir": float(row["last_event_dir"]) if pd.notna(row["last_event_dir"]) else np.nan,
                "event_hit_same_bar": bool(row["event_hit"]),
                "close": float(row["close"]),
                "open": float(row["open"]),
                "ema9": float(row["ema9"]) if pd.notna(row["ema9"]) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def apply_variants(events: pd.DataFrame) -> pd.DataFrame:
    kept = []
    for (_, setup), grp in events.sort_values(["entry_idx", "signal_idx"]).groupby(["asset", "setup"], sort=False):
        last_exit = {variant: -1 for variant in VARIANTS}
        for _, row in grp.iterrows():
            for variant in VARIANTS:
                allow, reason = variant_decision(row, setup, variant)
                if not allow:
                    continue
                if int(row["entry_idx"]) <= last_exit[variant]:
                    continue
                out = row.to_dict()
                out["variant"] = variant
                out["variant_reason"] = reason
                kept.append(out)
                last_exit[variant] = int(row["exit_idx"])
    return pd.DataFrame(kept)


def net_return(gross: pd.Series, cost_bps_per_side: float) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    return (1.0 + gross.astype(float)) * (1.0 - c) * (1.0 - c) - 1.0


def summarize_primary(events: pd.DataFrame):
    baseline_counts = (
        events[events["variant"] == "baseline"]
        .groupby(["asset", "setup"])
        .size()
        .rename("baseline_count")
    )
    detail = events.copy()
    detail["net_return"] = net_return(detail["gross_return"], PRIMARY_COST)
    detail = detail.merge(baseline_counts, on=["asset", "setup"], how="left")
    detail["retention_vs_setup_baseline"] = detail.groupby(["asset", "setup", "variant"])["variant"].transform("size") / detail["baseline_count"]
    detail["cross_window_trade"] = detail["event_age"] > EVENT_WINDOW
    detail["utc_bucket"] = detail["signal_time"].dt.hour.floordiv(8).map({0: "bucket_1", 1: "bucket_2", 2: "bucket_3"})

    setup_summary = (
        detail.groupby(["variant", "setup"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            left_tail_p5=("net_return", lambda x: np.quantile(x, 0.05) if len(x) else np.nan),
            retention_vs_setup_baseline=("retention_vs_setup_baseline", "mean"),
            cross_window_trade_share=("cross_window_trade", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "setup"])
    )

    asset_summary = (
        detail.groupby(["variant", "asset"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            cross_window_trade_share=("cross_window_trade", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "asset"])
    )

    time_bucket_summary = (
        detail.groupby(["variant", "utc_bucket"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "utc_bucket"])
    )

    event_age_summary = (
        detail.groupby(["variant", "cross_window_trade"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "cross_window_trade"])
    )

    overall_rows = []
    baseline_total = detail[detail["variant"] == "baseline"].shape[0]
    for variant in VARIANTS:
        subset = detail[detail["variant"] == variant].copy()
        if subset.empty:
            continue
        asset_totals = subset.groupby("asset")["net_return"].sum()
        overall_rows.append(
            {
                "variant": variant,
                "trades": int(len(subset)),
                "mean_net_return": float(subset["net_return"].mean()),
                "mean_total_return": float(asset_totals.mean()),
                "positive_asset_ratio": float((asset_totals > 0).mean()),
                "false_follow_through_4bars": float(subset["false_follow_through_4bars"].mean()),
                "trade_count_retention": float(len(subset) / baseline_total) if baseline_total else np.nan,
                "cross_window_trade_share": float(subset["cross_window_trade"].mean()),
                "mean_event_age": float(subset["event_age"].mean()),
            }
        )
    overall_summary = pd.DataFrame(overall_rows).sort_values("variant")
    return detail, overall_summary, setup_summary, asset_summary, time_bucket_summary, event_age_summary


def build_verdict(overall_summary: pd.DataFrame, event_age_summary: pd.DataFrame) -> tuple[str, str]:
    base = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    same = overall_summary.loc[overall_summary["variant"] == "same_window_only"].iloc[0]
    timeout = overall_summary.loc[overall_summary["variant"] == "window_plus_timeout"].iloc[0]
    base_cross = event_age_summary[(event_age_summary["variant"] == "baseline") & (event_age_summary["cross_window_trade"] == True)]
    timeout_cross = event_age_summary[(event_age_summary["variant"] == "window_plus_timeout") & (event_age_summary["cross_window_trade"] == True)]

    same_better = same["mean_total_return"] > base["mean_total_return"] and same["false_follow_through_4bars"] <= base["false_follow_through_4bars"]
    timeout_better = timeout["mean_total_return"] > base["mean_total_return"] and timeout["false_follow_through_4bars"] <= base["false_follow_through_4bars"]
    retention_ok = timeout["trade_count_retention"] >= 0.35
    cross_decay_help = True
    if not base_cross.empty and not timeout_cross.empty:
        cross_decay_help = timeout_cross.iloc[0]["false_follow_through_4bars"] <= base_cross.iloc[0]["false_follow_through_4bars"]

    if same_better and timeout_better and retention_ok and cross_decay_help:
        return (
            "keep_P1 / event-clock gate has honest signal",
            "同窗放行与超窗二次确认的组合，确实比裸 baseline 更像诚实 follow-up/timeout gate，但跨资产与保留率还不够硬，先留在 P1，不直接升 P2。",
        )
    if timeout_better and timeout["trade_count_retention"] >= 0.20:
        return (
            "keep_P1 / mixed but honest",
            "window+timeout 比 baseline 更稳一点，说明“超窗默认不追”有价值；但 same-window-only 收缩太狠，整体仍只够 P1，不够 paper candidate。",
        )
    return (
        "park / evidence pool",
        "event-clock 这轮没有把成本后回报、假延续率与保留率同时拉到足够诚实的区间；当前更像 useful diagnosis，不足以继续占用主资源。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    base_events = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower()}_frame.csv", index=False)
        for setup in SETUPS:
            events = collect_events(frame, asset, setup)
            if not events.empty:
                base_events.append(events)
    if not base_events:
        raise SystemExit("no events built")

    raw_events = pd.concat(base_events, ignore_index=True)
    variant_events = apply_variants(raw_events)
    detail, overall_summary, setup_summary, asset_summary, time_bucket_summary, event_age_summary = summarize_primary(variant_events)
    verdict, verdict_note = build_verdict(overall_summary, event_age_summary)

    detail.sort_values(["variant", "asset", "setup", "entry_time"]).to_csv(ART_DIR / "trade_log.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_bucket_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    event_age_summary.to_csv(ART_DIR / "event_age_summary.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "verdict_note": verdict_note,
        "event_window": EVENT_WINDOW,
        "timeout_window": TIMEOUT_WINDOW,
        "event_k": EVENT_K,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    base_row = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    same_row = overall_summary.loc[overall_summary["variant"] == "same_window_only"].iloc[0]
    timeout_row = overall_summary.loc[overall_summary["variant"] == "window_plus_timeout"].iloc[0]

    factor_body = f"""
<h1>Rank 111 / abnormal-return event clock follow-up gate — minimal clean replication</h1>
<div class='card'>
  <p><strong>结论：</strong><span class='{'bad' if 'park' in verdict else 'warn'}'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p class='muted'>固定 BTC/ETH/SOL 120d 15m 本地 cache，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars + 6bps/side</code>；比较 <code>baseline</code> / <code>same_window_only(event_age≤12)</code> / <code>window_plus_timeout(event_age≤12 或 12~24 内需二次确认)</code> 三臂。</p>
</div>
<div class='card'>
  <h2>主读法</h2>
  <ul>
    <li>baseline mean_total_return = <strong>{pct(base_row['mean_total_return'])}</strong></li>
    <li>same_window_only mean_total_return = <strong>{pct(same_row['mean_total_return'])}</strong></li>
    <li>window_plus_timeout mean_total_return = <strong>{pct(timeout_row['mean_total_return'])}</strong></li>
    <li>false_follow_through_4bars：baseline {pct(base_row['false_follow_through_4bars'])} / same-window {pct(same_row['false_follow_through_4bars'])} / timeout {pct(timeout_row['false_follow_through_4bars'])}</li>
    <li>trade_count_retention：same-window {pct(same_row['trade_count_retention'])} / timeout {pct(timeout_row['trade_count_retention'])}</li>
    <li>cross_window_trade_share：baseline {pct(base_row['cross_window_trade_share'])} / same-window {pct(same_row['cross_window_trade_share'])} / timeout {pct(timeout_row['cross_window_trade_share'])}</li>
  </ul>
</div>
<div class='card'><h2>Overall summary</h2>{render_table(overall_summary, percent_cols={'mean_net_return','mean_total_return','positive_asset_ratio','false_follow_through_4bars','trade_count_retention','cross_window_trade_share'})}</div>
<div class='card'><h2>Setup summary</h2>{render_table(setup_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5','retention_vs_setup_baseline','cross_window_trade_share'})}</div>
<div class='card'><h2>Asset summary</h2>{render_table(asset_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','cross_window_trade_share'})}</div>
<div class='card'><h2>Event-age summary</h2>{render_table(event_age_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars'})}</div>
<div class='card'><h2>Time bucket summary</h2>{render_table(time_bucket_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars'})}</div>
<p class='muted'>Artifacts: overall_summary.csv / setup_summary.csv / asset_summary.csv / event_age_summary.csv / time_bucket_summary.csv / trade_log.csv / summary.json</p>
"""
    write_html(SITE_DIR / "report.html", "Rank111 event clock clean replication", factor_body)

    reading_body = f"""
<h1>Rank 111 / abnormal-return event clock — clean replication note</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(verdict_note)}</p>
  <p>这轮不是测试“异常收益能不能单独开仓”，而是测试：<code>已有 trigger</code> 外面加一层 <code>same-window 放行 / 超窗 timeout + reconfirm</code>，能不能更诚实地少追坏的延续。</p>
  <p><a href='../../factors/scout_rank111_event_clock_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank111 event clock clean replication", reading_body)

    print(json.dumps({
        "verdict": verdict,
        "verdict_note": verdict_note,
        "overall_summary": overall_summary.to_dict(orient='records'),
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
