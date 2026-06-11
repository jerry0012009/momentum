#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank108_prebreak_higherlow_pressure_ladder_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank108_prebreak_higherlow_pressure_ladder_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank108_prebreak_higherlow_pressure_ladder_clean_replication.html"

ASSETS = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT"}
SETUPS = ["ema_psar_long", "fib_retest_long", "breakout_short"]
LONG_SETUPS = {"ema_psar_long", "fib_retest_long"}
VARIANTS = ["baseline", "ladder_hard_gate", "ladder_plus_smallbody_context"]
PRIMARY_VARIANT = "ladder_plus_smallbody_context"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]
HOLD_BARS = 8
FALSE_WINDOW = 4
LADDER_LOOKBACK = 16
BODY_RATIO_LIMIT = 0.30
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


def body_ratio(row: pd.Series) -> float:
    rng = float(row["high"] - row["low"])
    if rng <= 0:
        return 0.0
    return abs(float(row["close"] - row["open"])) / rng


def close_pos(row: pd.Series) -> float:
    rng = float(row["high"] - row["low"])
    if rng <= 0:
        return 0.5
    return float((row["close"] - row["low"]) / rng)


def lower_wick_ratio(row: pd.Series) -> float:
    rng = float(row["high"] - row["low"])
    if rng <= 0:
        return 0.0
    wick = min(float(row["open"]), float(row["close"])) - float(row["low"])
    return max(wick, 0.0) / rng


def add_ladder_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pivot_low_confirmed"] = (
        (out["low"].shift(1) < out["low"].shift(2))
        & (out["low"].shift(1) <= out["low"])
    ).fillna(False)
    out["pivot_low_value"] = np.where(out["pivot_low_confirmed"], out["low"].shift(1), np.nan)

    pivot_values: list[float] = []
    pivot_indices: list[int] = []
    ladder_score: list[int] = []
    bars_since_last: list[float] = []
    for i, (is_pivot, pivot_val) in enumerate(zip(out["pivot_low_confirmed"].tolist(), out["pivot_low_value"].tolist())):
        if bool(is_pivot) and pd.notna(pivot_val):
            pivot_values.append(float(pivot_val))
            pivot_indices.append(i - 1)
        if pivot_indices:
            bars_since_last.append(float(i - pivot_indices[-1]))
        else:
            bars_since_last.append(999.0)

        recent_pairs = [
            (pv, pi) for pv, pi in zip(pivot_values, pivot_indices)
            if i - pi <= LADDER_LOOKBACK
        ]
        score = 0
        if len(recent_pairs) >= 2 and recent_pairs[-1][0] > recent_pairs[-2][0] + EPS:
            score = 1
        if len(recent_pairs) >= 3 and recent_pairs[-1][0] > recent_pairs[-2][0] + EPS and recent_pairs[-2][0] > recent_pairs[-3][0] + EPS:
            score = 2
        ladder_score.append(score)

    out["ladder_score"] = ladder_score
    out["bars_since_last_pivot"] = bars_since_last
    out["ladder_recent"] = (out["ladder_score"] >= 2) & (out["bars_since_last_pivot"] <= LADDER_LOOKBACK)
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
    df["body_ratio"] = df.apply(body_ratio, axis=1)
    df["close_pos"] = df.apply(close_pos, axis=1)
    df["lower_wick_ratio"] = df.apply(lower_wick_ratio, axis=1)

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
    return add_ladder_features(df)


def direction_for_setup(setup: str) -> int:
    return 1 if setup in LONG_SETUPS else -1


def reference_level(row: pd.Series, setup: str) -> float:
    if setup == "ema_psar_long":
        return float(row["ema9"])
    if setup == "fib_retest_long":
        return float(row["fib_500"])
    return float(row["rolling_low20"])


def variant_decision(row: pd.Series, setup: str, variant: str) -> tuple[bool, float, str]:
    ladder_recent = bool(row["ladder_recent"])
    smallbody_context = bool(
        row["body_ratio"] <= BODY_RATIO_LIMIT
        and row["close"] >= reference_level(row, setup)
    )
    is_long = setup in LONG_SETUPS

    if variant == "baseline":
        return True, 1.0, "baseline"

    if is_long:
        if variant == "ladder_hard_gate":
            return ladder_recent, 1.0, "ladder_recent" if ladder_recent else "no_recent_higherlow_ladder"
        if variant == "ladder_plus_smallbody_context":
            allow = ladder_recent and smallbody_context
            return allow, 1.0, "ladder_plus_smallbody" if allow else "missing_ladder_or_smallbody"
    else:
        if variant == "ladder_hard_gate":
            allow = not ladder_recent
            return allow, 1.0, "short_allowed_no_ladder" if allow else "veto_adverse_long_ladder"
        if variant == "ladder_plus_smallbody_context":
            adverse = ladder_recent and smallbody_context
            allow = not adverse
            return allow, 1.0, "short_allowed" if allow else "veto_ladder_plus_smallbody"

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
        gross = direction * (exit_price / entry_price - 1.0)
        early = direction * (float(fail_row["close"]) / entry_price - 1.0)
        rows.append(
            {
                "asset": asset,
                "setup": setup,
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
                "ladder_score": int(row["ladder_score"]),
                "ladder_recent": bool(row["ladder_recent"]),
                "smallbody_context": bool(
                    row["body_ratio"] <= BODY_RATIO_LIMIT
                    and row["close"] >= reference_level(row, setup)
                ),
                "body_ratio": float(row["body_ratio"]),
                "close_pos": float(row["close_pos"]),
                "level_ref": reference_level(row, setup),
            }
        )
    return pd.DataFrame(rows)


def apply_variants(events: pd.DataFrame) -> pd.DataFrame:
    kept = []
    for (asset, setup), grp in events.sort_values(["entry_idx", "signal_idx"]).groupby(["asset", "setup"], sort=False):
        last_exit = {variant: -1 for variant in VARIANTS}
        frame = None
        symbol = ASSETS[asset]
        frame = build_frame(asset, symbol)
        for _, row in grp.iterrows():
            signal_row = frame.iloc[int(row["signal_idx"])]
            for variant in VARIANTS:
                allow, size, reason = variant_decision(signal_row, setup, variant)
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


def summarize_primary(events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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

    asset_summary = (
        detail.groupby(["variant", "asset"], dropna=False)
        .agg(
            trades=("net_return", "size"),
            mean_net_return=("net_return", "mean"),
            total_return=("net_return", "sum"),
            false_follow_through_4bars=("false_follow_through_4bars", "mean"),
            left_tail_p5=("net_return", lambda x: np.quantile(x, 0.05) if len(x) else np.nan),
            mean_position_size=("position_size", "mean"),
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
                "mean_position_size": float(subset["position_size"].mean()),
            }
        )
    overall_summary = pd.DataFrame(overall_rows).sort_values("variant")
    return detail, overall_summary, setup_summary, asset_summary, time_bucket_summary


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


def build_verdict(overall_summary: pd.DataFrame) -> tuple[str, str]:
    base = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]
    hard = overall_summary.loc[overall_summary["variant"] == "ladder_hard_gate"].iloc[0]
    primary = overall_summary.loc[overall_summary["variant"] == PRIMARY_VARIANT].iloc[0]
    if (
        primary["mean_total_return"] > base["mean_total_return"]
        and primary["positive_asset_ratio"] >= 2 / 3
        and primary["trade_count_retention"] >= 0.45
        and primary["false_follow_through_4bars"] < base["false_follow_through_4bars"]
        and primary["mean_net_return"] > base["mean_net_return"]
    ):
        return "promote_to_P2", "结构背景+小实体质量在跨资产上足够一致，值得进入下一层。"
    if (
        hard["mean_total_return"] > base["mean_total_return"]
        and hard["mean_net_return"] > base["mean_net_return"]
        and hard["positive_asset_ratio"] >= 1 / 3
        and hard["trade_count_retention"] >= 0.25
    ):
        return "keep_P1", "higher-low ladder 作为 long-side context 有一点诚实改善，但还不够硬到升 P2。"
    return "park", "long-side context 只在局部 setup 上减亏，跨资产仍不成立；而 smallbody 版本基本只剩缩样本，不值得继续占默认主资源位。"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    base_events = []
    for asset, symbol in ASSETS.items():
        frame = build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{symbol.lower().replace('usdt','')}_frame.csv", index=False)
        for setup in SETUPS:
            events = collect_events(frame, asset, setup)
            if not events.empty:
                base_events.append(events)

    raw_events = pd.concat(base_events, ignore_index=True)
    variant_events = apply_variants(raw_events)
    detail, overall_summary, setup_summary, asset_summary, time_bucket_summary = summarize_primary(variant_events)
    cost_summary = summarize_costs(variant_events)
    verdict, verdict_note = build_verdict(overall_summary)

    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    setup_summary.to_csv(ART_DIR / "setup_summary.csv", index=False)
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
    (ART_DIR / "summary.json").write_text(pd.Series(summary_payload).to_json(indent=2), encoding="utf-8")

    primary_row = overall_summary.loc[overall_summary["variant"] == PRIMARY_VARIANT].iloc[0]
    base_row = overall_summary.loc[overall_summary["variant"] == "baseline"].iloc[0]

    report_body = f"""
<h1>Rank 108 / prebreak higher-low pressure ladder context gate — clean replication</h1>
<div class='card'>
  <p><strong>结论：</strong><span class='{ 'good' if verdict != 'park' else 'bad' }'>{escape(verdict)}</span></p>
  <p>{escape(verdict_note)}</p>
  <p class='muted'>最小复现实验：固定 BTC/ETH/SOL 120d 15m cache，统一 <code>signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars + 6bps/side</code>，比较 <code>baseline / ladder_hard_gate / ladder_plus_smallbody_context</code> 三臂。</p>
</div>
<div class='card'>
  <h2>主读法</h2>
  <ul>
    <li>baseline mean_total_return = <strong>{pct(base_row['mean_total_return'])}</strong></li>
    <li>{PRIMARY_VARIANT} mean_total_return = <strong>{pct(primary_row['mean_total_return'])}</strong></li>
    <li>trade_count_retention = <strong>{pct(primary_row['trade_count_retention'])}</strong></li>
    <li>positive_asset_ratio = <strong>{pct(primary_row['positive_asset_ratio'])}</strong></li>
    <li>false_follow_through_4bars: {pct(base_row['false_follow_through_4bars'])} → <strong>{pct(primary_row['false_follow_through_4bars'])}</strong></li>
    <li>left_tail_p5: {pct(base_row['left_tail_p5'])} → <strong>{pct(primary_row['left_tail_p5'])}</strong></li>
  </ul>
</div>
<div class='card'><h2>Overall summary</h2>{render_table(overall_summary, percent_cols={'mean_net_return','mean_total_return','positive_asset_ratio','false_follow_through_4bars','left_tail_p5','trade_count_retention','mean_position_size'})}</div>
<div class='card'><h2>Setup summary</h2>{render_table(setup_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5','mean_position_size','retention_vs_setup_baseline'})}</div>
<div class='card'><h2>Asset summary</h2>{render_table(asset_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars','left_tail_p5','mean_position_size'})}</div>
<div class='card'><h2>Time bucket summary</h2>{render_table(time_bucket_summary, percent_cols={'mean_net_return','total_return','false_follow_through_4bars'})}</div>
<div class='card'><h2>Cost summary</h2>{render_table(cost_summary, percent_cols={'mean_net_return','total_return'})}</div>
<p class='muted'>Artifacts: overall_summary.csv / setup_summary.csv / asset_summary.csv / time_bucket_summary.csv / cost_summary.csv / trade_log.csv / summary.json</p>
"""
    write_html(SITE_DIR / "report.html", "Rank108 prebreak higher-low pressure ladder clean replication", report_body)

    reading_body = f"""
<h1>Rank 108 / prebreak higher-low pressure ladder context gate — clean replication note</h1>
<div class='card'>
  <p><strong>一句话：</strong>{escape(verdict_note)}</p>
  <p>这轮把它严格收紧成 <code>context gate</code> 而不是独立 alpha：对 <code>Fib retest_hold / EMA continuation</code> 只在 prebreak higher-low ladder 已出现、且当根回踩蜡烛足够克制时放行；对 <code>breakout_short</code> 只把它当 adverse long-context 的 veto 线索。</p>
  <p><a href='../factors/scout_rank108_prebreak_higherlow_pressure_ladder_15m/report.html'>打开完整 report</a></p>
</div>
"""
    write_html(READING_PATH, "Rank108 prebreak higher-low pressure ladder clean replication", reading_body)

    print(json_safe({
        "verdict": verdict,
        "verdict_note": verdict_note,
        "primary_variant": PRIMARY_VARIANT,
        "overall_summary": overall_summary.to_dict(orient="records"),
    }))


def json_safe(payload: dict) -> str:
    import json
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
