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
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank113_alpha_beta_abstain_profit_window_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank113_alpha_beta_abstain_profit_window_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank113_alpha_beta_abstain_profit_window_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
VARIANTS = ["baseline", "lower_band_only", "dual_band"]
HORIZONS = [4, 8, 12]
LOWER_QS = [0.15, 0.20, 0.25]
UPPER_QS = [0.75, 0.80, 0.85]
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0]
TRAIN_FRACTION = 0.60
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


def build_frame(asset: str, symbol: str) -> pd.DataFrame:
    df = load_bars(symbol, asset)
    df["ema9"] = df["close"].ewm(span=9, adjust=False).mean()
    df["ema15"] = df["close"].ewm(span=15, adjust=False).mean()
    df["ema_slope"] = df["ema9"].pct_change(3)
    df["vol_ma20"] = df["volume"].rolling(20, min_periods=20).mean()
    df["atr14"] = compute_atr(df)
    df["swing_high_30"] = df["high"].rolling(30, min_periods=30).max().shift(1)
    df["swing_low_30"] = df["low"].rolling(30, min_periods=30).min().shift(1)
    rng = (df["swing_high_30"] - df["swing_low_30"]).clip(lower=EPS)
    df["fib_618"] = df["swing_high_30"] - 0.618 * rng
    df["fib_500"] = df["swing_high_30"] - 0.500 * rng
    df["signal_distance_atr"] = ((df["close"] - df["fib_618"]) / df["atr14"]).replace([np.inf, -np.inf], np.nan)
    df["signal_body_atr"] = ((df["close"] - df["open"]).abs() / df["atr14"]).replace([np.inf, -np.inf], np.nan)

    df["fib_retest_long_signal"] = (
        df["fib_618"].notna()
        & (df["ema9"] > df["ema15"])
        & (df["ema_slope"] > 0)
        & (df["close"] > df["fib_618"])
        & (df["close"].shift(1) <= df["fib_618"].shift(1))
        & (df["low"] <= df["fib_618"] + 0.2 * df["atr14"])
        & (df["close"] > df["fib_500"])
        & (df["volume"] > df["vol_ma20"])
        & df["signal_distance_atr"].notna()
    ).fillna(False)
    return df


def collect_signals(frame: pd.DataFrame, asset: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signal_idx = np.flatnonzero(frame["fib_retest_long_signal"].to_numpy())
    for idx in signal_idx:
        row = frame.iloc[idx]
        entry_idx = idx + 1
        if entry_idx >= len(frame):
            continue
        entry = frame.iloc[entry_idx]
        if not np.isfinite(entry["open"]) or float(entry["open"]) <= 0:
            continue
        out = {
            "asset": asset,
            "signal_idx": int(idx),
            "signal_time": row["timestamp"],
            "entry_idx": int(entry_idx),
            "entry_time": entry["timestamp"],
            "entry_price": float(entry["open"]),
            "proxy_distance_atr": float(row["signal_distance_atr"]),
            "proxy_body_atr": float(row["signal_body_atr"]) if pd.notna(row["signal_body_atr"]) else np.nan,
            "close_to_fib618": float(row["close"] - row["fib_618"]),
            "atr14": float(row["atr14"]),
        }
        for horizon in HORIZONS:
            exit_idx = entry_idx + horizon
            if exit_idx >= len(frame):
                out[f"gross_h{horizon}"] = np.nan
                out[f"early_h{horizon}"] = np.nan
                continue
            exit_row = frame.iloc[exit_idx]
            gross = float(exit_row["close"]) / float(entry["open"]) - 1.0
            early_probe_idx = min(len(frame) - 1, entry_idx + min(4, horizon))
            early_row = frame.iloc[early_probe_idx]
            early = float(early_row["close"]) / float(entry["open"]) - 1.0
            out[f"gross_h{horizon}"] = gross
            out[f"early_h{horizon}"] = early
        rows.append(out)
    return pd.DataFrame(rows)


def choose_train_plan(signals: pd.DataFrame) -> tuple[int, float, float, pd.DataFrame]:
    train_cut = max(1, int(len(signals) * TRAIN_FRACTION))
    train = signals.iloc[:train_cut].copy()
    baseline_totals: dict[int, float] = {}
    for horizon in HORIZONS:
        train[f"net_h{horizon}"] = net_return(train[f"gross_h{horizon}"], PRIMARY_COST)
        asset_totals = train.groupby("asset")[f"net_h{horizon}"].apply(lambda s: float((1.0 + s.dropna()).prod() - 1.0) if s.dropna().size else np.nan)
        baseline_totals[horizon] = float(asset_totals.mean()) if len(asset_totals) else -np.inf
    best_horizon = max(HORIZONS, key=lambda h: baseline_totals.get(h, -np.inf))

    rows: list[dict[str, object]] = []
    for lower_q in LOWER_QS:
        for upper_q in UPPER_QS:
            if lower_q >= upper_q:
                continue
            allowed_parts: list[pd.DataFrame] = []
            thresholds: list[dict[str, object]] = []
            for asset, grp in train.groupby("asset", sort=True):
                proxy = grp["proxy_distance_atr"].dropna()
                if proxy.empty:
                    continue
                lower_thr = float(proxy.quantile(lower_q))
                upper_thr = float(proxy.quantile(upper_q))
                thresholds.append({
                    "asset": asset,
                    "lower_q": lower_q,
                    "upper_q": upper_q,
                    "lower_thr": lower_thr,
                    "upper_thr": upper_thr,
                })
                work = grp.copy()
                work["keep_dual"] = (work["proxy_distance_atr"] >= lower_thr) & (work["proxy_distance_atr"] <= upper_thr)
                allowed_parts.append(work)
            if not allowed_parts:
                continue
            allowed = pd.concat(allowed_parts, ignore_index=True)
            subset = allowed[allowed["keep_dual"]].copy()
            subset[f"net_h{best_horizon}"] = net_return(subset[f"gross_h{best_horizon}"], PRIMARY_COST)
            asset_totals = subset.groupby("asset")[f"net_h{best_horizon}"].apply(lambda s: float((1.0 + s.dropna()).prod() - 1.0) if s.dropna().size else np.nan)
            baseline_counts = train.groupby("asset").size()
            keep_counts = subset.groupby("asset").size()
            retentions = (keep_counts / baseline_counts).reindex(baseline_counts.index)
            rows.append({
                "hold_bars": best_horizon,
                "lower_q": lower_q,
                "upper_q": upper_q,
                "train_mean_total_return": float(asset_totals.mean()) if len(asset_totals) else -np.inf,
                "train_positive_asset_ratio": float((asset_totals > 0).mean()) if len(asset_totals) else 0.0,
                "train_mean_retention": float(retentions.mean()) if len(retentions) else np.nan,
            })
    grid = pd.DataFrame(rows).sort_values(["train_mean_total_return", "train_positive_asset_ratio", "train_mean_retention"], ascending=[False, False, False]).reset_index(drop=True)
    qualified = grid[
        grid["train_mean_retention"].between(0.35, 0.90, inclusive="both")
        & (grid["train_positive_asset_ratio"] >= (1/3))
    ]
    chosen = qualified.iloc[0] if not qualified.empty else grid.iloc[0]
    return best_horizon, float(chosen["lower_q"]), float(chosen["upper_q"]), grid


def build_thresholds(signals: pd.DataFrame, lower_q: float, upper_q: float) -> pd.DataFrame:
    train_cut = max(1, int(len(signals) * TRAIN_FRACTION))
    train = signals.iloc[:train_cut].copy()
    rows: list[dict[str, object]] = []
    for asset, grp in train.groupby("asset", sort=True):
        proxy = grp["proxy_distance_atr"].dropna()
        rows.append({
            "asset": asset,
            "train_rows": int(len(grp)),
            "lower_q": lower_q,
            "upper_q": upper_q,
            "lower_thr": float(proxy.quantile(lower_q)) if not proxy.empty else np.nan,
            "upper_thr": float(proxy.quantile(upper_q)) if not proxy.empty else np.nan,
            "proxy_train_median": float(proxy.median()) if not proxy.empty else np.nan,
        })
    return pd.DataFrame(rows)


def variant_keep(proxy_value: float, lower_thr: float, upper_thr: float, variant: str) -> tuple[bool, str]:
    if variant == "baseline":
        return True, "baseline"
    if pd.isna(proxy_value) or pd.isna(lower_thr):
        return False, "missing_proxy"
    if proxy_value < lower_thr:
        return False, "below_noise_band"
    if variant == "lower_band_only":
        return True, "passed_lower_band"
    if pd.isna(upper_thr):
        return False, "missing_upper_band"
    if proxy_value > upper_thr:
        return False, "above_shock_band"
    return True, "inside_dual_band"


def net_return(gross: pd.Series, cost_bps_per_side: float) -> pd.Series:
    c = float(cost_bps_per_side) / 10000.0
    gross = gross.astype(float)
    return (1.0 + gross) * (1.0 - c) * (1.0 - c) - 1.0


def apply_variants(signals: pd.DataFrame, thresholds: pd.DataFrame, hold_bars: int, cost_bps_per_side: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    thr_map = thresholds.set_index("asset").to_dict(orient="index")
    kept_rows: list[dict[str, object]] = []
    veto_rows: list[dict[str, object]] = []
    for asset, grp in signals.groupby("asset", sort=True):
        grp = grp.sort_values("entry_idx").reset_index(drop=True)
        last_exit = {variant: -1 for variant in VARIANTS}
        meta = thr_map.get(asset, {})
        lower_thr = meta.get("lower_thr", np.nan)
        upper_thr = meta.get("upper_thr", np.nan)
        for _, row in grp.iterrows():
            for variant in VARIANTS:
                keep, reason = variant_keep(float(row["proxy_distance_atr"]), lower_thr, upper_thr, variant)
                if not keep:
                    veto_rows.append({
                        "asset": asset,
                        "variant": variant,
                        "signal_time": pd.to_datetime(row["signal_time"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "proxy_distance_atr": float(row["proxy_distance_atr"]),
                        "veto_reason": reason,
                    })
                    continue
                exit_idx = int(row["entry_idx"] + hold_bars)
                if int(row["entry_idx"]) <= last_exit[variant]:
                    continue
                if pd.isna(row[f"gross_h{hold_bars}"]):
                    continue
                out = row.to_dict()
                out["variant"] = variant
                out["variant_reason"] = reason
                out["cost_bps_per_side"] = float(cost_bps_per_side)
                out["hold_bars"] = int(hold_bars)
                out["gross_return"] = float(row[f"gross_h{hold_bars}"])
                out["net_return"] = float(net_return(pd.Series([row[f"gross_h{hold_bars}"]]), cost_bps_per_side).iloc[0])
                out["early_return_4"] = float(row[f"early_h{hold_bars}"])
                out["false_follow_through_4bars"] = int(float(row[f"early_h{hold_bars}"]) <= 0)
                out["exit_idx"] = exit_idx
                kept_rows.append(out)
                last_exit[variant] = exit_idx
    return pd.DataFrame(kept_rows), pd.DataFrame(veto_rows)


def summarize_asset(detail: pd.DataFrame, signals: pd.DataFrame) -> pd.DataFrame:
    base_counts = signals.groupby("asset").size().rename("baseline_signals")
    rows: list[dict[str, object]] = []
    for (variant, asset, cost), grp in detail.groupby(["variant", "asset", "cost_bps_per_side"], dropna=False):
        baseline_n = int(base_counts.get(asset, 0))
        rows.append({
            "variant": variant,
            "asset": asset,
            "cost_bps_per_side": float(cost),
            "baseline_signals": baseline_n,
            "trades": int(len(grp)),
            "trade_retention": float(len(grp) / baseline_n) if baseline_n else np.nan,
            "total_return": float((1.0 + grp["net_return"]).prod() - 1.0),
            "avg_net_return": float(grp["net_return"].mean()),
            "win_rate": float((grp["net_return"] > 0).mean()),
            "false_follow_through_4bars": float(grp["false_follow_through_4bars"].mean()),
            "avg_proxy_distance_atr": float(grp["proxy_distance_atr"].mean()),
        })
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant", "asset"]).reset_index(drop=True)


def summarize_overall(asset_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (variant, cost), grp in asset_summary.groupby(["variant", "cost_bps_per_side"], dropna=False):
        rows.append({
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "mean_total_return": float(grp["total_return"].mean()),
            "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
            "mean_trades": float(grp["trades"].mean()),
            "mean_trade_retention": float(grp["trade_retention"].mean()) if grp["trade_retention"].notna().any() else np.nan,
            "mean_avg_net_return": float(grp["avg_net_return"].mean()),
            "mean_win_rate": float(grp["win_rate"].mean()),
            "mean_false_follow_through_4bars": float(grp["false_follow_through_4bars"].mean()),
            "mean_proxy_distance_atr": float(grp["avg_proxy_distance_atr"].mean()) if grp["avg_proxy_distance_atr"].notna().any() else np.nan,
        })
    return pd.DataFrame(rows).sort_values(["cost_bps_per_side", "variant"]).reset_index(drop=True)


def summarize_time_buckets(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame(columns=["variant", "bucket", "trades", "mean_net_return", "total_return", "false_follow_through_4bars"])
    work = detail.copy()
    hours = pd.to_datetime(work["signal_time"], utc=True).dt.hour
    work["bucket"] = pd.cut(hours, bins=[-1, 7, 15, 23], labels=["bucket_1", "bucket_2", "bucket_3"])
    rows: list[dict[str, object]] = []
    for (variant, bucket), grp in work.groupby(["variant", "bucket"], dropna=False, observed=False):
        rows.append({
            "variant": variant,
            "bucket": str(bucket),
            "trades": int(len(grp)),
            "mean_net_return": float(grp["net_return"].mean()),
            "total_return": float((1.0 + grp["net_return"]).prod() - 1.0),
            "false_follow_through_4bars": float(grp["false_follow_through_4bars"].mean()),
        })
    return pd.DataFrame(rows).sort_values(["variant", "bucket"]).reset_index(drop=True)


def summarize_vetoes(vetoes: pd.DataFrame) -> pd.DataFrame:
    if vetoes.empty:
        return pd.DataFrame(columns=["variant", "asset", "veto_reason", "count"])
    return (
        vetoes.groupby(["variant", "asset", "veto_reason"], dropna=False)
        .size()
        .rename("count")
        .reset_index()
        .sort_values(["variant", "asset", "count"], ascending=[True, True, False])
        .reset_index(drop=True)
    )


def build_verdict(overall_6: pd.DataFrame) -> tuple[str, str]:
    lookup = overall_6.set_index("variant")
    baseline = lookup.loc["baseline"]
    lower = lookup.loc["lower_band_only"]
    dual = lookup.loc["dual_band"]
    dual_improves = (
        float(dual["mean_total_return"]) > float(baseline["mean_total_return"])
        and float(dual["mean_false_follow_through_4bars"]) <= float(baseline["mean_false_follow_through_4bars"])
    )
    lower_improves = (
        float(lower["mean_total_return"]) > float(baseline["mean_total_return"])
        and float(lower["mean_false_follow_through_4bars"]) <= float(baseline["mean_false_follow_through_4bars"])
    )
    dual_retention_ok = float(dual["mean_trade_retention"]) >= 0.45 if pd.notna(dual["mean_trade_retention"]) else False
    dual_cross_ok = float(dual["positive_asset_ratio"]) >= (2 / 3)

    if dual_improves and dual_retention_ok and dual_cross_ok:
        return (
            "promote_to_P2 / paper candidate pool",
            "双阈值 abstain 在测试段同时改善了成本后收益、假跟随率与跨标的离散，而且样本留存还没塌；当前已经够资格升到 paper candidate pool。",
        )
    if dual_improves or lower_improves:
        return (
            "keep_P1 / honest overlay signal",
            "至少有一层 abstain gate 呈现出诚实 uplift：它确实更像在过滤噪音单或追尾单；但当前跨标的/留存还不够硬，先留在 P1，不直接升 P2。",
        )
    return (
        "park / evidence pool",
        "这轮最小 clean replication 没把 abstain gate 变成更诚实的 fib-retest overlay：成本后收益、假跟随率与留存没有同时改善，因此当前更适合 park。",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    all_signals: list[pd.DataFrame] = []
    meta_rows: list[dict[str, object]] = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower()}_frame.csv", index=False)
        signals = collect_signals(frame, asset)
        if signals.empty:
            continue
        all_signals.append(signals)
        meta_rows.append({
            "asset": asset,
            "symbol": symbol,
            "bars": int(len(frame)),
            "signals": int(len(signals)),
            "sample_start_utc": frame["timestamp"].min().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sample_end_utc": frame["timestamp"].max().strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    if not all_signals:
        raise SystemExit("no signals built")

    signals_df = pd.concat(all_signals, ignore_index=True).sort_values(["asset", "signal_time"]).reset_index(drop=True)
    hold_bars, lower_q, upper_q, train_grid = choose_train_plan(signals_df)
    thresholds = build_thresholds(signals_df, lower_q, upper_q)

    details: list[pd.DataFrame] = []
    vetoes: list[pd.DataFrame] = []
    train_cut = max(1, int(len(signals_df) * TRAIN_FRACTION))
    test_signals = signals_df.iloc[train_cut:].copy().reset_index(drop=True)

    for cost in COSTS:
        detail_cost, veto_cost = apply_variants(test_signals, thresholds, hold_bars, cost)
        if not detail_cost.empty:
            details.append(detail_cost)
        if not veto_cost.empty:
            veto_cost["cost_bps_per_side"] = float(cost)
            vetoes.append(veto_cost)

    detail_df = pd.concat(details, ignore_index=True) if details else pd.DataFrame()
    veto_df = pd.concat(vetoes, ignore_index=True) if vetoes else pd.DataFrame()
    asset_summary = summarize_asset(detail_df, test_signals)
    overall_summary = summarize_overall(asset_summary)
    overall_6 = overall_summary[overall_summary["cost_bps_per_side"] == PRIMARY_COST].copy()
    time_bucket_summary = summarize_time_buckets(detail_df[detail_df["cost_bps_per_side"] == PRIMARY_COST].copy())
    veto_summary = summarize_vetoes(veto_df[veto_df["cost_bps_per_side"] == PRIMARY_COST].copy() if not veto_df.empty else pd.DataFrame())
    meta_df = pd.DataFrame(meta_rows)
    verdict, verdict_note = build_verdict(overall_6)

    detail_df.sort_values(["cost_bps_per_side", "variant", "asset", "entry_time"]).to_csv(ART_DIR / "trade_log.csv", index=False)
    signals_df.to_csv(ART_DIR / "signal_catalog.csv", index=False)
    train_grid.to_csv(ART_DIR / "train_band_horizon_grid.csv", index=False)
    thresholds.to_csv(ART_DIR / "chosen_thresholds.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    veto_summary.to_csv(ART_DIR / "veto_reason_summary.csv", index=False)
    time_bucket_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    meta_df.to_csv(ART_DIR / "sample_meta.csv", index=False)
    (ART_DIR / "summary.json").write_text(json.dumps({
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "verdict_note": verdict_note,
        "base_archetype": "fib_retest_long",
        "hold_bars": int(hold_bars),
        "lower_q": lower_q,
        "upper_q": upper_q,
        "train_fraction": TRAIN_FRACTION,
        "primary_cost_bps_per_side": PRIMARY_COST,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lookup = overall_6.set_index("variant")
    baseline = lookup.loc["baseline"]
    lower = lookup.loc["lower_band_only"]
    dual = lookup.loc["dual_band"]

    factor_body = f"""
<h1>Rank 113 / alpha-beta abstain / profit-window — minimal clean replication</h1>
<div class='card'>
  <p><strong>结论：</strong><span class='{'good' if 'promote' in verdict else 'warn' if 'keep_P1' in verdict else 'bad'}'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p class='muted'>这轮故意只挂 <code>1</code> 条 archetype：<code>fib_retest_long</code>。先在训练段冻结 <code>hold_bars={hold_bars}</code>、<code>lower_q={lower_q:.2f}</code>、<code>upper_q={upper_q:.2f}</code>，再在测试段统一比较 <code>baseline</code> / <code>lower_band_only</code> / <code>dual_band</code> 三臂，口径固定为 <code>signal 当根及之前数据 + next-bar open + no-overlap</code>。</p>
</div>
<div class='card'>
  <h2>主读法（6bps/side）</h2>
  <ul>
    <li>baseline：mean_total_return = <strong>{pct(baseline['mean_total_return'])}</strong>；retention = {pct(baseline['mean_trade_retention'])}；false_follow_through_4bars = {pct(baseline['mean_false_follow_through_4bars'])}</li>
    <li>lower_band_only：mean_total_return = <strong>{pct(lower['mean_total_return'])}</strong>；retention = {pct(lower['mean_trade_retention'])}；false_follow_through_4bars = {pct(lower['mean_false_follow_through_4bars'])}</li>
    <li>dual_band：mean_total_return = <strong>{pct(dual['mean_total_return'])}</strong>；retention = {pct(dual['mean_trade_retention'])}；false_follow_through_4bars = {pct(dual['mean_false_follow_through_4bars'])}</li>
  </ul>
</div>
<div class='card'>
  <h2>这轮到底测了什么</h2>
  <ul>
    <li><strong>noise-band：</strong>若 fib 回踩确认后，<code>(close - fib_618) / ATR</code> 仍太小，就当它还没真正走出来，不做。</li>
    <li><strong>shock-band：</strong>若同一个 proxy 已经太大，就当它更像追尾，不追。</li>
    <li><strong>profit-window：</strong>不按 accuracy 选窗口，而是先在训练段冻结一个更像能赚钱的持有窗口，再拿到测试段看 gate 是否还成立。</li>
  </ul>
</div>
<div class='card'><h2>Overall summary</h2>{render_table(overall_summary, percent_cols={'mean_total_return','positive_asset_ratio','mean_trade_retention','mean_avg_net_return','mean_win_rate','mean_false_follow_through_4bars'}, digits_cols={'cost_bps_per_side': 0, 'mean_trades': 1, 'mean_proxy_distance_atr': 2})}</div>
<div class='card'><h2>Asset summary（6bps）</h2>{render_table(asset_summary[asset_summary['cost_bps_per_side'] == PRIMARY_COST].copy(), percent_cols={'trade_retention','total_return','avg_net_return','win_rate','false_follow_through_4bars'}, digits_cols={'cost_bps_per_side': 0, 'baseline_signals': 0, 'trades': 0, 'avg_proxy_distance_atr': 2})}</div>
<div class='card'><h2>Chosen thresholds</h2>{render_table(thresholds, digits_cols={'train_rows': 0, 'lower_q': 2, 'upper_q': 2, 'lower_thr': 2, 'upper_thr': 2, 'proxy_train_median': 2})}</div>
<div class='card'><h2>Train band / horizon grid</h2>{render_table(train_grid, percent_cols={'train_mean_total_return','train_positive_asset_ratio','train_mean_retention'}, digits_cols={'hold_bars': 0, 'lower_q': 2, 'upper_q': 2})}</div>
<div class='card'><h2>Veto reason summary（6bps）</h2>{render_table(veto_summary, digits_cols={'count': 0})}</div>
<div class='card'><h2>Time bucket summary（6bps）</h2>{render_table(time_bucket_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars'}, digits_cols={'trades': 0})}</div>
<div class='card'><h2>Sample meta</h2>{render_table(meta_df, digits_cols={'bars': 0, 'signals': 0})}</div>
<p class='muted'>Artifacts: overall_summary.csv / asset_summary.csv / chosen_thresholds.csv / train_band_horizon_grid.csv / veto_reason_summary.csv / trade_log.csv / summary.json</p>
"""
    write_html(SITE_DIR / "report.html", "Rank113 alpha-beta abstain clean replication", factor_body)

    reading_body = f"""
<h1>Rank 113 / alpha-beta abstain / profit-window — clean replication note</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(verdict_note)}</p>
  <p>这轮没有把它当独立 alpha，而是只问：<code>fib retest</code> 这种已有 setup 上，能不能用一个事先冻结的“太小不做 / 太大不追”双阈值，减少坏交易。</p>
  <p><a href='../../factors/scout_rank113_alpha_beta_abstain_profit_window_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank113 alpha-beta abstain clean replication", reading_body)

    print(json.dumps({
        "verdict": verdict,
        "verdict_note": verdict_note,
        "hold_bars": hold_bars,
        "lower_q": lower_q,
        "upper_q": upper_q,
        "overall_summary": overall_summary.to_dict(orient='records'),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
