#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from run_manual_narrow_paper_lanes import build_rank29_trades_baseline  # type: ignore

ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "rank29_regime_monthly_panel"
CACHE_DIR = ROOT / "reports" / "artifacts" / "rank29_trigger_tf_monthly" / "cache"
ASSET_TO_BINANCE = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
COSTS = [6.0, 10.0, 15.0]
SELECTED_FEATURES = [
    "breadth_above_ema200_share",
    "cross_asset_sync_mean",
    "trend_strength_20d_mean",
    "noise_ratio_20d_mean",
    "realized_vol_20d_mean",
    "btc_followthrough_4bar_mean",
    "btc_false_break_ratio_mean",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def load_cached_bars(asset: str) -> pd.DataFrame:
    symbol = ASSET_TO_BINANCE[asset]
    path = CACHE_DIR / f"{symbol}__5y__15m.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing cache: {path}")
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, format="mixed")
    df["close_ts"] = pd.to_datetime(df["close_ts"], utc=True, format="mixed")
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def recompute_cost(trades: pd.DataFrame, cost_bps_per_side: float) -> pd.DataFrame:
    out = trades.copy()
    cost_rate = cost_bps_per_side / 10000.0
    out["cost_bps_per_side"] = float(cost_bps_per_side)
    out["net_ret"] = (1.0 + out["gross_ret"]) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
    return out


def build_trades() -> pd.DataFrame:
    rows = []
    for asset in ASSET_TO_BINANCE:
        bars = load_cached_bars(asset)
        trades = build_rank29_trades_baseline(asset, bars)
        trades = trades[trades["complete_trade"]].copy().reset_index(drop=True)
        for col in ["event_ts", "entry_ts", "exit_ts"]:
            trades[col] = pd.to_datetime(trades[col], utc=True)
        rows.append(trades)
    all_trades = pd.concat(rows, ignore_index=True).sort_values(["entry_ts", "asset"]).reset_index(drop=True)
    all_trades["month"] = pd.to_datetime(all_trades["exit_ts"], utc=True).dt.strftime("%Y-%m")
    return all_trades


def monthly_variant_returns(trades: pd.DataFrame, *, cost_bps_per_side: float) -> pd.DataFrame:
    t = recompute_cost(trades, cost_bps_per_side)
    variant_map = {
        "baseline": t,
        "long_only": t[t["trigger_tf"] == "long"].copy(),
        "medium_only": t[t["trigger_tf"] == "medium"].copy(),
        "short_only": t[t["trigger_tf"] == "short"].copy(),
        "drop_medium": t[t["trigger_tf"] != "medium"].copy(),
        "drop_short": t[t["trigger_tf"] != "short"].copy(),
    }
    frames = []
    for variant, df in variant_map.items():
        asset_month = (
            df.groupby(["month", "asset"], as_index=False)
            .agg(
                trades=("net_ret", "size"),
                asset_month_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
                win_rate=("net_ret", lambda s: float((s > 0).mean())),
            )
        )
        monthly = (
            asset_month.groupby("month", as_index=False)
            .agg(
                active_assets=("asset", "nunique"),
                total_trades=("trades", "sum"),
                mean_asset_month_return=("asset_month_return", "mean"),
                positive_asset_ratio=("asset_month_return", lambda s: float((s > 0).mean())),
                mean_asset_win_rate=("win_rate", "mean"),
            )
        )
        monthly["variant"] = variant
        monthly["cost_bps_per_side"] = float(cost_bps_per_side)
        frames.append(monthly)
    return pd.concat(frames, ignore_index=True)


def build_trade_quality_monthly(trades: pd.DataFrame) -> pd.DataFrame:
    t = trades.copy()
    t["cost_flip"] = ((t["gross_ret"] > 0) & (t["net_ret"] <= 0)).astype(int)
    out = (
        t.groupby(["month", "trigger_tf"], as_index=False)
        .agg(
            trades=("net_ret", "size"),
            mean_net_ret=("net_ret", "mean"),
            month_return=("net_ret", lambda s: float((1.0 + s).prod() - 1.0)),
            win_rate=("net_ret", lambda s: float((s > 0).mean())),
            cost_flip_ratio=("cost_flip", "mean"),
        )
    )
    return out


def build_regime_monthly_features() -> pd.DataFrame:
    asset_month_frames = []
    daily_asset_frames = []
    for asset in ASSET_TO_BINANCE:
        bars = load_cached_bars(asset)
        bars = bars[["timestamp", "open", "high", "low", "close", "volume"]].copy()
        bars["ret_1"] = bars["close"].pct_change()
        bars["followthrough_4bar"] = bars["close"].shift(-4) / bars["close"] - 1.0

        daily = (
            bars.set_index("timestamp")
            .resample("1D")
            .agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
            .dropna()
            .reset_index()
        )
        daily["asset"] = asset
        daily["ret_1d"] = daily["close"].pct_change()
        daily["ema50"] = daily["close"].ewm(span=50, adjust=False).mean()
        daily["ema200"] = daily["close"].ewm(span=200, adjust=False).mean()
        daily["above_ema200"] = (daily["close"] > daily["ema200"]).astype(int)
        daily["trend_strength_20d"] = daily["close"].pct_change(20).abs()
        abs_sum_20 = daily["ret_1d"].abs().rolling(20).sum()
        daily["noise_ratio_20d"] = 1.0 - (daily["close"].pct_change(20).abs() / abs_sum_20.replace(0, np.nan))
        daily["realized_vol_20d"] = daily["ret_1d"].rolling(20).std() * np.sqrt(20)
        daily["month"] = daily["timestamp"].dt.strftime("%Y-%m")
        daily_asset_frames.append(daily)

        bars["month"] = bars["timestamp"].dt.strftime("%Y-%m")
        bars["false_break_proxy"] = (bars["followthrough_4bar"] <= 0).astype(int)
        asset_month = (
            bars.groupby("month", as_index=False)
            .agg(
                followthrough_4bar_mean=("followthrough_4bar", "mean"),
                false_break_ratio_mean=("false_break_proxy", "mean"),
                intraday_vol_mean=("ret_1", lambda s: float(s.std() * np.sqrt(len(s.dropna()))) if len(s.dropna()) > 1 else np.nan),
            )
        )
        asset_month["asset"] = asset
        asset_month_frames.append(asset_month)

    daily_all = pd.concat(daily_asset_frames, ignore_index=True)
    asset_month_all = pd.concat(asset_month_frames, ignore_index=True)

    breadth = (
        daily_all.groupby("month", as_index=False)
        .agg(
            breadth_above_ema200_share=("above_ema200", "mean"),
            trend_strength_20d_mean=("trend_strength_20d", "mean"),
            noise_ratio_20d_mean=("noise_ratio_20d", "mean"),
            realized_vol_20d_mean=("realized_vol_20d", "mean"),
        )
    )

    sync = []
    for month, grp in daily_all.dropna(subset=["ret_1d"]).groupby("month"):
        pivot = grp.pivot(index="timestamp", columns="asset", values="ret_1d").dropna()
        if pivot.empty:
            continue
        sign_sync = pivot.apply(np.sign).mean(axis=1).abs().mean()
        corr = pivot.corr()
        if corr.shape[0] > 1:
            upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack()
            corr_mean = float(upper.mean()) if not upper.empty else np.nan
        else:
            corr_mean = np.nan
        sync.append({"month": month, "cross_asset_sync_mean": sign_sync, "cross_asset_corr_mean": corr_mean})
    sync_df = pd.DataFrame(sync)

    breakout_quality = (
        asset_month_all.groupby("month", as_index=False)
        .agg(
            avg_followthrough_4bar_mean=("followthrough_4bar_mean", "mean"),
            avg_false_break_ratio_mean=("false_break_ratio_mean", "mean"),
            avg_intraday_vol_mean=("intraday_vol_mean", "mean"),
        )
    )

    # keep BTC-specific quality too, as reference market proxy
    btc_month = asset_month_all[asset_month_all["asset"] == "BTC-USD"][
        ["month", "followthrough_4bar_mean", "false_break_ratio_mean", "intraday_vol_mean"]
    ].rename(
        columns={
            "followthrough_4bar_mean": "btc_followthrough_4bar_mean",
            "false_break_ratio_mean": "btc_false_break_ratio_mean",
            "intraday_vol_mean": "btc_intraday_vol_mean",
        }
    )

    out = breadth.merge(sync_df, on="month", how="left").merge(breakout_quality, on="month", how="left").merge(btc_month, on="month", how="left")
    return out.sort_values("month").reset_index(drop=True)


def build_feature_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    targets = [
        "baseline_6bps",
        "long_only_6bps",
        "medium_only_6bps",
        "short_only_6bps",
        "long_minus_short_6bps",
        "long_minus_medium_6bps",
    ]
    rows = []
    for feature in SELECTED_FEATURES:
        if feature not in panel.columns:
            continue
        for target in targets:
            if target not in panel.columns:
                continue
            x = panel[[feature, target]].dropna()
            if len(x) < 8:
                corr = np.nan
            else:
                corr = float(x[feature].corr(x[target]))
            rows.append({"feature": feature, "target": target, "pearson_corr": corr, "samples": len(x)})
    return pd.DataFrame(rows).sort_values(["target", "pearson_corr"], ascending=[True, False]).reset_index(drop=True)


def build_bucket_analysis(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for feature in SELECTED_FEATURES:
        if feature not in panel.columns:
            continue
        x = panel[["month", feature, "baseline_6bps", "long_only_6bps", "medium_only_6bps", "short_only_6bps", "long_minus_short_6bps", "long_minus_medium_6bps"]].dropna()
        if len(x) < 12:
            continue
        try:
            x = x.copy()
            x["bucket"] = pd.qcut(x[feature], 3, labels=["low", "mid", "high"], duplicates="drop")
        except ValueError:
            continue
        for bucket, grp in x.groupby("bucket"):
            rows.append(
                {
                    "feature": feature,
                    "bucket": str(bucket),
                    "months": int(len(grp)),
                    "feature_mean": float(grp[feature].mean()),
                    "baseline_mean_month_return": float(grp["baseline_6bps"].mean()),
                    "long_mean_month_return": float(grp["long_only_6bps"].mean()),
                    "medium_mean_month_return": float(grp["medium_only_6bps"].mean()),
                    "short_mean_month_return": float(grp["short_only_6bps"].mean()),
                    "long_minus_short_mean": float(grp["long_minus_short_6bps"].mean()),
                    "long_minus_medium_mean": float(grp["long_minus_medium_6bps"].mean()),
                    "baseline_positive_month_ratio": float((grp["baseline_6bps"] > 0).mean()),
                    "long_positive_month_ratio": float((grp["long_only_6bps"] > 0).mean()),
                }
            )
    return pd.DataFrame(rows).sort_values(["feature", "bucket"]).reset_index(drop=True)


def assemble_panel(trades: pd.DataFrame, regime_features: pd.DataFrame) -> pd.DataFrame:
    panel = regime_features.copy()
    cost_frames = []
    for cost in COSTS:
        monthly = monthly_variant_returns(trades, cost_bps_per_side=cost)
        monthly = monthly[["month", "variant", "mean_asset_month_return", "positive_asset_ratio", "total_trades"]].copy()
        value_col = f"ret_{int(cost)}bps"
        tmp = monthly.pivot(index="month", columns="variant", values="mean_asset_month_return").reset_index()
        tmp = tmp.rename(columns={c: f"{c}_{int(cost)}bps" for c in tmp.columns if c != "month"})
        cost_frames.append(tmp)
    for frame in cost_frames:
        panel = panel.merge(frame, on="month", how="left")

    tq = build_trade_quality_monthly(trades)
    tq_pivot = tq.pivot(index="month", columns="trigger_tf", values=["trades", "mean_net_ret", "month_return", "win_rate", "cost_flip_ratio"])
    tq_pivot.columns = [f"{metric}_{trigger}" for metric, trigger in tq_pivot.columns]
    tq_pivot = tq_pivot.reset_index()
    panel = panel.merge(tq_pivot, on="month", how="left")

    panel["baseline_6bps"] = panel.get("baseline_6bps")
    panel["long_only_6bps"] = panel.get("long_only_6bps")
    panel["medium_only_6bps"] = panel.get("medium_only_6bps")
    panel["short_only_6bps"] = panel.get("short_only_6bps")
    panel["long_minus_short_6bps"] = panel["long_only_6bps"] - panel["short_only_6bps"]
    panel["long_minus_medium_6bps"] = panel["long_only_6bps"] - panel["medium_only_6bps"]
    panel["recent_flag_last_3m"] = 0
    if len(panel) >= 3:
        panel.loc[panel.index[-3:], "recent_flag_last_3m"] = 1
    return panel.sort_values("month").reset_index(drop=True)


def write_report(panel: pd.DataFrame, corr_df: pd.DataFrame, bucket_df: pd.DataFrame) -> None:
    recent = panel.tail(3).copy()
    long_edge_corr = corr_df[corr_df["target"] == "long_minus_short_6bps"].sort_values("pearson_corr", ascending=False)
    baseline_corr = corr_df[corr_df["target"] == "baseline_6bps"].sort_values("pearson_corr", ascending=False)
    lines = [
        "# Rank29 regime monthly panel",
        "",
        f"- Generated at: `{utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        "- Sample: Binance spot 15m, ~5 years, BTC-USD + ETH-USD + SOL-USD",
        "- Strategy lens: Rank29 / breakout_align_ge2 / no_overlap_guard / hold 8 bars",
        "- Goal: identify which regime features align with better/worse monthly Rank29 performance, and whether recent weak months resemble any repeated historical regime pocket.",
        "",
        "## First-read takeaways",
        "",
        "- This panel should be read as a **hypothesis generator**, not yet a final production gate. Strong candidates should still be retested as explicit filters on the trade stream.",
        "- We care about two separate targets: `baseline_6bps` (when Rank29 as a whole likes the regime) and `long_minus_short_6bps` / `long_minus_medium_6bps` (when long trigger_tf is relatively better than the others).",
        "- If a feature correlates with `baseline_6bps` but not with `long_minus_*`, it may help define a good/bad Rank29 environment without justifying a long-specific filter.",
        "",
        "## Top correlations with baseline monthly return (6bps)",
        "",
    ]
    for _, row in baseline_corr.head(5).iterrows():
        lines.append(f"- {row['feature']}: corr={row['pearson_corr']:.3f} over {int(row['samples'])} months")
    lines.extend(["", "## Top correlations with `long - short` monthly edge (6bps)", ""])
    for _, row in long_edge_corr.head(5).iterrows():
        lines.append(f"- {row['feature']}: corr={row['pearson_corr']:.3f} over {int(row['samples'])} months")

    lines.extend(["", "## Recent 3 months snapshot", ""])
    for _, row in recent.iterrows():
        lines.append(
            f"- {row['month']}: baseline={pct(row.get('baseline_6bps'))}, long={pct(row.get('long_only_6bps'))}, medium={pct(row.get('medium_only_6bps'))}, short={pct(row.get('short_only_6bps'))}, breadth_above_ema200={pct(row.get('breadth_above_ema200_share'))}, trend_strength_20d={pct(row.get('trend_strength_20d_mean'))}, noise_ratio_20d={pct(row.get('noise_ratio_20d_mean'))}, cross_asset_sync={pct(row.get('cross_asset_sync_mean'))}, btc_false_break={pct(row.get('btc_false_break_ratio_mean'))}"
        )

    lines.extend(["", "## Suggested next validation", ""])
    lines.extend(
        [
            "1. Choose 2-3 regime features from this panel that show both interpretability and repeatability.",
            "2. Turn them into explicit month / bar-level filters and rerun full historical trade-stream backtests.",
            "3. Check whether recent months map into the same feature buckets that were historically weak for Rank29 or relatively better for `long`.",
            "",
            "## Output files",
            "",
            "- `monthly_panel.csv`",
            "- `regime_feature_correlations.csv`",
            "- `regime_bucket_analysis.csv`",
            "- `monthly_variant_returns_by_cost.csv`",
            "- `trade_quality_monthly.csv`",
        ]
    )
    (ARTIFACT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    trades = build_trades()
    trades.to_csv(ARTIFACT_DIR / "all_trades_6bps.csv", index=False)

    regime_features = build_regime_monthly_features()
    regime_features.to_csv(ARTIFACT_DIR / "regime_features_monthly.csv", index=False)

    panel = assemble_panel(trades, regime_features)
    panel.to_csv(ARTIFACT_DIR / "monthly_panel.csv", index=False)

    monthly_variant_all = pd.concat([monthly_variant_returns(trades, cost_bps_per_side=c) for c in COSTS], ignore_index=True)
    monthly_variant_all.to_csv(ARTIFACT_DIR / "monthly_variant_returns_by_cost.csv", index=False)

    trade_quality = build_trade_quality_monthly(trades)
    trade_quality.to_csv(ARTIFACT_DIR / "trade_quality_monthly.csv", index=False)

    corr_df = build_feature_correlations(panel)
    corr_df.to_csv(ARTIFACT_DIR / "regime_feature_correlations.csv", index=False)

    bucket_df = build_bucket_analysis(panel)
    bucket_df.to_csv(ARTIFACT_DIR / "regime_bucket_analysis.csv", index=False)

    write_report(panel, corr_df, bucket_df)
    print(ARTIFACT_DIR / "report.md")


if __name__ == "__main__":
    main()
