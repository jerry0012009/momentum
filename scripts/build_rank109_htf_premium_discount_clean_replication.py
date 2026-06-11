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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank109_htf_premium_discount_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank109_htf_premium_discount_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank109_htf_premium_discount_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "long_only_discount_gate", "symmetric_discount_premium_gate"]
PRIMARY_VARIANT = "long_only_discount_gate"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
FALSE_WINDOW = 4
EPS = 1e-12

CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 32px auto; padding: 0 18px 48px; line-height: 1.68; color: #111827; background: #f8fafc; }
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
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
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


def add_prev4h_context(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["h4_bucket"] = out["timestamp"].dt.floor("4h")
    h4 = (
        out.groupby("h4_bucket", sort=True)
        .agg(prev4h_high=("high", "max"), prev4h_low=("low", "min"))
        .shift(1)
        .reset_index()
    )
    out = out.merge(h4, on="h4_bucket", how="left")
    out["prev4h_mid"] = (out["prev4h_high"] + out["prev4h_low"]) / 2.0
    return out


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema21"] = df["close"].ewm(span=21, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
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

    return add_prev4h_context(df)


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def variant_decision(row: pd.Series, setup: str, variant: str) -> tuple[bool, float, str]:
    discount = bool(pd.notna(row["prev4h_mid"]) and row["entry_price"] < row["prev4h_mid"])
    premium = bool(pd.notna(row["prev4h_mid"]) and row["entry_price"] > row["prev4h_mid"])
    is_long = setup in LONG_SETUPS

    if variant == "baseline":
        return True, 1.0, "baseline"
    if variant == PRIMARY_VARIANT:
        if is_long:
            return discount, 1.0, "discount_long_ok" if discount else "long_not_in_discount"
        return True, 1.0, "short_baseline_unchanged"
    if variant == "symmetric_discount_premium_gate":
        if is_long:
            return discount, 1.0, "discount_long_ok" if discount else "long_not_in_discount"
        return premium, 1.0, "premium_short_ok" if premium else "short_not_in_premium"
    raise ValueError(variant)


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
                "prev4h_high": float(row["prev4h_high"]) if pd.notna(row["prev4h_high"]) else np.nan,
                "prev4h_low": float(row["prev4h_low"]) if pd.notna(row["prev4h_low"]) else np.nan,
                "prev4h_mid": float(row["prev4h_mid"]) if pd.notna(row["prev4h_mid"]) else np.nan,
                "entry_vs_prev4h_mid": float(entry_price / row["prev4h_mid"] - 1.0) if pd.notna(row["prev4h_mid"]) and row["prev4h_mid"] else np.nan,
                "entry_in_discount": bool(pd.notna(row["prev4h_mid"]) and entry_price < row["prev4h_mid"]),
                "entry_in_premium": bool(pd.notna(row["prev4h_mid"]) and entry_price > row["prev4h_mid"]),
            }
        )
    return pd.DataFrame(rows)


def apply_variants(events: pd.DataFrame) -> pd.DataFrame:
    kept = []
    for (_, setup), grp in events.sort_values(["entry_idx", "signal_idx"]).groupby(["asset", "setup"], sort=False):
        last_exit = {variant: -1 for variant in VARIANTS}
        for _, row in grp.iterrows():
            for variant in VARIANTS:
                allow, size, reason = variant_decision(row, setup, variant)
                if not allow:
                    continue
                if int(row["entry_idx"]) <= last_exit[variant]:
                    continue
                out = row.to_dict()
                out["variant"] = variant
                out["position_size"] = size
                out["variant_reason"] = reason
                kept.append(out)
                last_exit[variant] = int(row["exit_idx"])
    return pd.DataFrame(kept)


def net_return(gross: pd.Series, cost_bps_per_side: float, size: pd.Series) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    scaled = gross.astype(float) * size.astype(float)
    return (1.0 + scaled) * (1.0 - c) * (1.0 - c) - 1.0


def summarize_primary(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_counts = (
        events[events["variant"] == "baseline"]
        .groupby(["asset", "setup"])
        .size()
        .rename("baseline_count")
    )

    detail = events.copy()
    detail["net_return"] = net_return(detail["gross_return"], PRIMARY_COST, detail["position_size"])
    detail = detail.merge(baseline_counts, on=["asset", "setup"], how="left")
    detail["retention_vs_setup_baseline"] = detail.groupby(["asset", "setup", "variant"])["variant"].transform("size") / detail["baseline_count"]
    detail["utc_bucket"] = detail["signal_time"].dt.hour.floordiv(8).map({0: "bucket_1", 1: "bucket_2", 2: "bucket_3"})

    setup_summary = (
        detail.groupby(["variant", "setup"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            left_tail_p5=("net_return", lambda x: np.quantile(x, 0.05) if len(x) else np.nan),
            mean_position_size=("position_size", "mean"),
            retention_vs_setup_baseline=("retention_vs_setup_baseline", "mean"),
        )
        .reset_index()
        .sort_values(["variant", "setup"])
    )

    side_summary = (
        detail.groupby(["variant", "side"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            left_tail_p5=("net_return", lambda x: np.quantile(x, 0.05) if len(x) else np.nan),
        )
        .reset_index()
        .sort_values(["variant", "side"])
    )

    asset_summary = (
        detail.groupby(["variant", "asset"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            left_tail_p5=("net_return", lambda x: np.quantile(x, 0.05) if len(x) else np.nan),
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

    overall_rows = []
    for variant in VARIANTS:
        subset = detail[detail["variant"] == variant].copy()
        if subset.empty:
            continue
        asset_totals = subset.groupby("asset")["net_return"].sum()
        baseline_total = detail[detail["variant"] == "baseline"].shape[0]
        long_subset = subset[subset["side"] == "long"]
        short_subset = subset[subset["side"] == "short"]
        overall_rows.append(
            {
                "variant": variant,
                "trades": int(len(subset)),
                "mean_net_return": float(subset["net_return"].mean()),
                "mean_total_return": float(asset_totals.mean()),
                "positive_asset_ratio": float((asset_totals > 0).mean()),
                "false_follow_through_4bars": float(subset["false_follow_through_4bars"].mean()),
                "left_tail_p5": float(np.quantile(subset["net_return"], 0.05)),
                "trade_count_retention": float(len(subset) / baseline_total) if baseline_total else np.nan,
                "long_trades_share": float(len(long_subset) / len(subset)) if len(subset) else np.nan,
                "long_mean_net_return": float(long_subset["net_return"].mean()) if len(long_subset) else np.nan,
                "short_mean_net_return": float(short_subset["net_return"].mean()) if len(short_subset) else np.nan,
            }
        )
    overall_summary = pd.DataFrame(overall_rows).sort_values("variant")
    return detail, overall_summary, setup_summary, side_summary, asset_summary, time_bucket_summary


def summarize_costs(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost in COSTS:
        tmp = events.copy()
        tmp["net_return"] = net_return(tmp["gross_return"], cost, tmp["position_size"])
        for variant, grp in tmp.groupby("variant"):
            rows.append(
                {
                    "cost_bps_per_side": cost,
                    "variant": variant,
                    "trades": int(len(grp)),
                    "mean_net_return": float(grp["net_return"].mean()),
                    "total_return": float(grp["net_return"].sum()),
                }
            )
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant"])


def build_verdict(overall_summary: pd.DataFrame, setup_summary: pd.DataFrame) -> tuple[str, str]:
    base = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    long_only = overall_summary.loc[overall_summary["variant"] == PRIMARY_VARIANT].iloc[0]
    symmetric = overall_summary.loc[overall_summary["variant"] == "symmetric_discount_premium_gate"].iloc[0]
    long_setup_base = setup_summary[(setup_summary["variant"] == "baseline") & (setup_summary["setup"].isin(sorted(LONG_SETUPS)))]
    long_setup_lo = setup_summary[(setup_summary["variant"] == PRIMARY_VARIANT) & (setup_summary["setup"].isin(sorted(LONG_SETUPS)))]
    long_base_total = float(long_setup_base["total_return"].sum()) if not long_setup_base.empty else np.nan
    long_lo_total = float(long_setup_lo["total_return"].sum()) if not long_setup_lo.empty else np.nan

    if (
        long_only["mean_total_return"] > base["mean_total_return"]
        and long_only["mean_net_return"] > base["mean_net_return"]
        and symmetric["mean_total_return"] < long_only["mean_total_return"]
        and long_lo_total > long_base_total
        and long_only["trade_count_retention"] >= 0.60
    ):
        return "park_as_asymmetric_context_note", "long-only discount gate 比 baseline 更诚实，但一旦强行镜像到 short 侧就明显变差；因此这条线最多保留为 Fib retest / EMA continuation 的 asymmetric context note，不升 shared gate，也不继续占默认 Scout 主资源位。"
    if long_only["trade_count_retention"] < 0.35 or long_lo_total <= long_base_total:
        return "park", "discount gate 主要靠砍样本，且连 long 侧 aggregate 都没明显更好；当前不值得保留为 active 候选。"
    return "keep_P1", "long-only discount gate 有一点局部改善，但 shared 版本不诚实；先留作低优先级 long-side context evidence。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    base_events = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower().replace('usdt', '')}_frame.csv", index=False)
        for setup in SETUPS:
            events = collect_events(frame, asset, setup)
            if not events.empty:
                base_events.append(events)

    if not base_events:
        raise SystemExit("no events built")

    raw_events = pd.concat(base_events, ignore_index=True)
    variant_events = apply_variants(raw_events)
    detail, overall_summary, setup_summary, side_summary, asset_summary, time_bucket_summary = summarize_primary(variant_events)
    cost_summary = summarize_costs(variant_events)
    verdict, verdict_note = build_verdict(overall_summary, setup_summary)

    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
    side_summary.to_csv(ART_DIR / "side_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    time_bucket_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    cost_summary.to_csv(ART_DIR / "cost_summary.csv", index=False)
    detail.sort_values(["variant", "asset", "setup", "entry_time"]).to_csv(ART_DIR / "trade_log.csv", index=False)

    summary_payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "verdict_note": verdict_note,
        "primary_variant": PRIMARY_VARIANT,
        "primary_cost_bps_per_side": PRIMARY_COST,
    }
    (ART_DIR / "summary.json").write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    primary_row = overall_summary.loc[overall_summary["variant"] == PRIMARY_VARIANT].iloc[0]
    base_row = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    sym_row = overall_summary.loc[overall_summary["variant"] == "symmetric_discount_premium_gate"].iloc[0]

    report_body = f"""
<h1>Rank 109 / HTF premium-discount long-bias context gate — clean replication</h1>
<div class='card'>
  <p><strong>结论：</strong><span class='{ 'good' if 'park' not in verdict else 'bad' }'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p class='muted'>最小复现实验：固定 BTC/ETH/SOL 120d 15m cache，统一 <code>signal 当根及之前数据 + 上一根完整 4h bar + next-bar open + no-overlap + hold 8 bars + 6bps/side</code>，比较 <code>baseline / long_only_discount_gate / symmetric_discount_premium_gate</code> 三臂。</p>
</div>
<div class='card'>
  <h2>主读法</h2>
  <ul>
    <li>baseline mean_total_return = <strong>{pct(base_row['mean_total_return'])}</strong></li>
    <li>long_only_discount_gate mean_total_return = <strong>{pct(primary_row['mean_total_return'])}</strong></li>
    <li>symmetric_discount_premium_gate mean_total_return = <strong>{pct(sym_row['mean_total_return'])}</strong></li>
    <li>trade_count_retention: {pct(primary_row['trade_count_retention'])}（long-only） / {pct(sym_row['trade_count_retention'])}（symmetric）</li>
    <li>long_mean_net_return: {pct(base_row['long_mean_net_return'])} → <strong>{pct(primary_row['long_mean_net_return'])}</strong></li>
    <li>short_mean_net_return: {pct(base_row['short_mean_net_return'])} → <strong>{pct(sym_row['short_mean_net_return'])}</strong></li>
    <li>false_follow_through_4bars: baseline {pct(base_row['false_follow_through_4bars'])} / long-only <strong>{pct(primary_row['false_follow_through_4bars'])}</strong> / symmetric <strong>{pct(sym_row['false_follow_through_4bars'])}</strong></li>
  </ul>
</div>
<div class='card'><h2>Overall summary</h2>{render_table(overall_summary, percent_cols={'mean_net_return','mean_total_return','positive_asset_ratio','false_follow_through_4bars','left_tail_p5','trade_count_retention','long_trades_share','long_mean_net_return','short_mean_net_return'})}</div>
<div class='card'><h2>Setup summary</h2>{render_table(setup_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5','mean_position_size','retention_vs_setup_baseline'})}</div>
<div class='card'><h2>Side summary</h2>{render_table(side_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5'})}</div>
<div class='card'><h2>Asset summary</h2>{render_table(asset_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5'})}</div>
<div class='card'><h2>Time bucket summary</h2>{render_table(time_bucket_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars'})}</div>
<div class='card'><h2>Cost summary</h2>{render_table(cost_summary, percent_cols={'mean_net_return','total_return'})}</div>
<p class='muted'>Artifacts: overall_summary.csv / setup_summary.csv / side_summary.csv / asset_summary.csv / time_bucket_summary.csv / cost_summary.csv / trade_log.csv / summary.json</p>
"""
    write_html(SITE_DIR / "report.html", "Rank109 HTF premium discount clean replication", report_body)

    reading_body = f"""
<h1>Rank 109 / HTF premium-discount long-bias context gate — clean replication note</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(verdict_note)}</p>
  <p>这轮把它严格收紧成 <code>上一根完整 4h midline</code> 的最小 honesty test：如果只有 long 侧的 <code>discount</code> 还能讲得通，而 short 侧的 <code>premium</code> 一镜像就变差，那就只能把它留成 <code>Fib retest_hold / EMA continuation</code> 的方向不对称 context note。</p>
  <p><a href='../factors/scout_rank109_htf_premium_discount_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank109 HTF premium discount clean replication", reading_body)

    print(json.dumps({
        "verdict": verdict,
        "verdict_note": verdict_note,
        "primary_variant": PRIMARY_VARIANT,
        "overall_summary": overall_summary.to_dict(orient="records"),
    }, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
