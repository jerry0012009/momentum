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

from build_rank29_regime_monthly_panel import (  # type: ignore
    build_regime_monthly_features,
    build_trades,
    recompute_cost,
)

ARTIFACT_DIR = ROOT / "reports" / "artifacts" / "rank29_regime_gate_backtest"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank29_regime_gate_backtest"
COSTS = [6.0, 10.0, 15.0]
RECENT_WINDOWS = [60, 120]
LOW_Q = 1 / 3
HIGH_Q = 2 / 3
WEIGHTS = [0.0, 0.25]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x * 100:.2f}%"


def build_gate_flags(regime_features: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    rf = regime_features.copy().sort_values("month").reset_index(drop=True)
    trend_low = float(rf["trend_strength_20d_mean"].quantile(LOW_Q))
    vol_low = float(rf["realized_vol_20d_mean"].quantile(LOW_Q))
    noise_high = float(rf["noise_ratio_20d_mean"].quantile(HIGH_Q))

    rf["gate_low_trend_low_vol"] = (
        (rf["trend_strength_20d_mean"] <= trend_low)
        & (rf["realized_vol_20d_mean"] <= vol_low)
    ).astype(int)
    rf["gate_low_trend_high_noise"] = (
        (rf["trend_strength_20d_mean"] <= trend_low)
        & (rf["noise_ratio_20d_mean"] >= noise_high)
    ).astype(int)
    rf["gate_combined"] = ((rf["gate_low_trend_low_vol"] == 1) | (rf["gate_low_trend_high_noise"] == 1)).astype(int)

    thresholds = {
        "trend_low_q33": trend_low,
        "vol_low_q33": vol_low,
        "noise_high_q67": noise_high,
    }
    return rf, thresholds


def monthly_asset_returns(trades: pd.DataFrame, ret_col: str) -> pd.DataFrame:
    x = trades.copy()
    x["month"] = pd.to_datetime(x["entry_ts"], utc=True).dt.strftime("%Y-%m")
    return (
        x.groupby(["month", "asset"], as_index=False)
        .agg(
            trades=(ret_col, "size"),
            asset_month_return=(ret_col, lambda s: float((1.0 + s).prod() - 1.0)),
            mean_trade_return=(ret_col, "mean"),
        )
        .sort_values(["month", "asset"])
        .reset_index(drop=True)
    )


def summarize_variant(
    trades: pd.DataFrame,
    ret_col: str,
    weight_col: str,
    *,
    label: str,
    cost: float,
    recent_cutoffs: dict[int, pd.Timestamp],
) -> dict[str, object]:
    x = trades.copy()
    asset_total = (
        x.groupby("asset", as_index=False)
        .agg(
            trades=(ret_col, "size"),
            asset_total_return=(ret_col, lambda s: float((1.0 + s).prod() - 1.0)),
            mean_trade_return=(ret_col, "mean"),
            exposure_share=(weight_col, "mean"),
        )
    )
    asset_month = monthly_asset_returns(x, ret_col)
    month_summary = (
        asset_month.groupby("month", as_index=False)
        .agg(
            active_assets=("asset", "nunique"),
            total_trades=("trades", "sum"),
            mean_asset_month_return=("asset_month_return", "mean"),
            positive_asset_ratio=("asset_month_return", lambda s: float((s > 0).mean())),
        )
    )

    out: dict[str, object] = {
        "variant": label,
        "cost_bps_per_side": float(cost),
        "trades": int(len(x)),
        "mean_asset_total_return": float(asset_total["asset_total_return"].mean()),
        "median_asset_total_return": float(asset_total["asset_total_return"].median()),
        "positive_asset_ratio": float((asset_total["asset_total_return"] > 0).mean()),
        "mean_exposure_share": float(x[weight_col].mean()),
        "positive_month_ratio": float((month_summary["mean_asset_month_return"] > 0).mean()) if len(month_summary) else np.nan,
        "mean_month_return": float(month_summary["mean_asset_month_return"].mean()) if len(month_summary) else np.nan,
        "worst_month_return": float(month_summary["mean_asset_month_return"].min()) if len(month_summary) else np.nan,
    }

    for days, cutoff in recent_cutoffs.items():
        recent = x[x["entry_ts"] >= cutoff].copy()
        if recent.empty:
            recent_asset = pd.DataFrame(columns=["asset", "recent_total_return"])
        else:
            recent_asset = (
                recent.groupby("asset", as_index=False)
                .agg(
                    recent_total_return=(ret_col, lambda s: float((1.0 + s).prod() - 1.0)),
                    exposure_share_recent=(weight_col, "mean"),
                )
            )
        recent_month = monthly_asset_returns(recent, ret_col) if not recent.empty else pd.DataFrame(columns=["month", "asset", "asset_month_return"])
        if not recent_month.empty:
            recent_month_summary = (
                recent_month.groupby("month", as_index=False)
                .agg(mean_asset_month_return=("asset_month_return", "mean"))
            )
            recent_mean_month = float(recent_month_summary["mean_asset_month_return"].mean())
            recent_worst_month = float(recent_month_summary["mean_asset_month_return"].min())
        else:
            recent_mean_month = np.nan
            recent_worst_month = np.nan
        prefix = f"recent{days}d"
        out[f"{prefix}_mean_asset_total_return"] = float(recent_asset["recent_total_return"].mean()) if len(recent_asset) else np.nan
        out[f"{prefix}_positive_asset_ratio"] = float((recent_asset["recent_total_return"] > 0).mean()) if len(recent_asset) else np.nan
        out[f"{prefix}_mean_exposure_share"] = float(recent[weight_col].mean()) if len(recent) else np.nan
        out[f"{prefix}_mean_month_return"] = recent_mean_month
        out[f"{prefix}_worst_month_return"] = recent_worst_month
        out[f"{prefix}_trades"] = int(len(recent))

    return out


def apply_gate_variants(
    trades: pd.DataFrame,
    gate_flags: pd.DataFrame,
    *,
    cost: float,
    recent_cutoffs: dict[int, pd.Timestamp],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    t = recompute_cost(trades, cost).copy()
    t["month"] = pd.to_datetime(t["entry_ts"], utc=True).dt.strftime("%Y-%m")
    t = t.merge(
        gate_flags[["month", "gate_low_trend_low_vol", "gate_low_trend_high_noise", "gate_combined"]],
        on="month",
        how="left",
    )
    for col in ["gate_low_trend_low_vol", "gate_low_trend_high_noise", "gate_combined"]:
        t[col] = t[col].fillna(0).astype(int)

    result_rows: list[dict[str, object]] = []
    trade_frames = []

    baseline = t.copy()
    baseline["variant"] = "baseline"
    baseline["exposure_weight"] = 1.0
    baseline["scaled_net_ret"] = baseline["net_ret"]
    trade_frames.append(baseline)
    result_rows.append(
        summarize_variant(
            baseline,
            "scaled_net_ret",
            "exposure_weight",
            label="baseline",
            cost=cost,
            recent_cutoffs=recent_cutoffs,
        )
    )

    gate_map = {
        "gate_low_trend_low_vol": "low_trend_low_vol",
        "gate_low_trend_high_noise": "low_trend_high_noise",
        "gate_combined": "combined",
    }
    for gate_col, gate_label in gate_map.items():
        for bad_weight in WEIGHTS:
            df = t.copy()
            df["variant"] = f"{gate_label}_w{int(bad_weight * 100):02d}"
            df["exposure_weight"] = np.where(df[gate_col] == 1, bad_weight, 1.0)
            df["scaled_net_ret"] = df["net_ret"] * df["exposure_weight"]
            trade_frames.append(df)
            result_rows.append(
                summarize_variant(
                    df,
                    "scaled_net_ret",
                    "exposure_weight",
                    label=f"{gate_label}_w{int(bad_weight * 100):02d}",
                    cost=cost,
                    recent_cutoffs=recent_cutoffs,
                )
            )

    return pd.DataFrame(result_rows), pd.concat(trade_frames, ignore_index=True)


def write_report(summary: pd.DataFrame, thresholds: dict[str, float], gate_flags: pd.DataFrame) -> None:
    def best_for(cost: float, metric: str, ascending: bool = False) -> pd.DataFrame:
        sub = summary[summary["cost_bps_per_side"] == cost].sort_values(metric, ascending=ascending)
        return sub.head(3)

    lines = [
        "# Rank29 regime gate backtest",
        "",
        f"- Generated at: `{utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')}`",
        "- Gates tested on 5y monthly regime features and then validated on the most recent 60d / 120d windows.",
        "- Trade engine: Rank29 / breakout_align_ge2 / no_overlap_guard / hold 8 bars",
        "- Exposure logic: when a bad regime month is detected, exposure is reduced to either `25%` or `0%` instead of necessarily deleting all trades.",
        "",
        "## Gate definitions",
        "",
        f"- low_trend_low_vol: `trend_strength_20d_mean <= {thresholds['trend_low_q33']:.6f}` and `realized_vol_20d_mean <= {thresholds['vol_low_q33']:.6f}`",
        f"- low_trend_high_noise: `trend_strength_20d_mean <= {thresholds['trend_low_q33']:.6f}` and `noise_ratio_20d_mean >= {thresholds['noise_high_q67']:.6f}`",
        "- combined: either of the two gates above is active",
        "",
        "## Gate hit counts by month",
        "",
        f"- low_trend_low_vol months: `{int(gate_flags['gate_low_trend_low_vol'].sum())}`",
        f"- low_trend_high_noise months: `{int(gate_flags['gate_low_trend_high_noise'].sum())}`",
        f"- combined months: `{int(gate_flags['gate_combined'].sum())}`",
        "",
        "## Best variants by full 5y mean asset total return",
        "",
    ]
    for cost in COSTS:
        lines.append(f"### {int(cost)}bps / side")
        for _, row in best_for(cost, "mean_asset_total_return", ascending=False).iterrows():
            lines.append(
                f"- {row['variant']}: full5y mean_asset_total_return={pct(row['mean_asset_total_return'])}, "
                f"positive_month_ratio={pct(row['positive_month_ratio'])}, mean_exposure={pct(row['mean_exposure_share'])}, "
                f"recent120d mean_asset_total_return={pct(row['recent120d_mean_asset_total_return'])}, recent60d mean_asset_total_return={pct(row['recent60d_mean_asset_total_return'])}"
            )
        lines.append("")

    lines.extend(["## Best variants on recent 120 days", ""])
    for cost in COSTS:
        lines.append(f"### {int(cost)}bps / side")
        sub = summary[summary["cost_bps_per_side"] == cost].sort_values("recent120d_mean_asset_total_return", ascending=False)
        for _, row in sub.head(3).iterrows():
            lines.append(
                f"- {row['variant']}: recent120d mean_asset_total_return={pct(row['recent120d_mean_asset_total_return'])}, "
                f"recent120d mean_month_return={pct(row['recent120d_mean_month_return'])}, recent120d mean_exposure={pct(row['recent120d_mean_exposure_share'])}, "
                f"full5y mean_asset_total_return={pct(row['mean_asset_total_return'])}"
            )
        lines.append("")

    lines.extend(["## Best variants on recent 60 days", ""])
    for cost in COSTS:
        lines.append(f"### {int(cost)}bps / side")
        sub = summary[summary["cost_bps_per_side"] == cost].sort_values("recent60d_mean_asset_total_return", ascending=False)
        for _, row in sub.head(3).iterrows():
            lines.append(
                f"- {row['variant']}: recent60d mean_asset_total_return={pct(row['recent60d_mean_asset_total_return'])}, "
                f"recent60d mean_month_return={pct(row['recent60d_mean_month_return'])}, recent60d mean_exposure={pct(row['recent60d_mean_exposure_share'])}, "
                f"full5y mean_asset_total_return={pct(row['mean_asset_total_return'])}"
            )
        lines.append("")

    lines.extend(
        [
            "## What to look for",
            "",
            "- A useful gate should improve recent60d / recent120d results **without destroying** full5y quality.",
            "- `w25` versions are softer; if they rescue recent months while keeping long-run returns more intact, they are often better first paper candidates than hard `w00` vetoes.",
            "- If a gate helps recent60d but badly degrades 5y robustness, it is probably overfitting the current pocket.",
            "",
            "## Output files",
            "",
            "- `summary_by_cost.csv`",
            "- `trade_level_variants.csv`",
            "- `gate_month_flags.csv`",
            "- `report.md`",
        ]
    )
    (ARTIFACT_DIR / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_site_html(summary: pd.DataFrame, thresholds: dict[str, float], gate_flags: pd.DataFrame) -> None:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    focus_variants = ["baseline", "low_trend_high_noise_w25", "low_trend_high_noise_w00", "low_trend_low_vol_w25"]
    focus = summary[summary["variant"].isin(focus_variants)].copy()

    def make_rows(cost: float) -> str:
        sub = focus[focus["cost_bps_per_side"] == cost].copy()
        rows = []
        order = ["baseline", "low_trend_high_noise_w25", "low_trend_high_noise_w00", "low_trend_low_vol_w25"]
        for variant in order:
            row = sub[sub["variant"] == variant]
            if row.empty:
                continue
            r = row.iloc[0]
            rows.append(
                "<tr>"
                f"<td>{variant}</td>"
                f"<td>{pct(r['mean_asset_total_return'])}</td>"
                f"<td>{pct(r['mean_month_return'])}</td>"
                f"<td>{pct(r['recent120d_mean_asset_total_return'])}</td>"
                f"<td>{pct(r['recent120d_mean_month_return'])}</td>"
                f"<td>{pct(r['recent120d_worst_month_return'])}</td>"
                f"<td>{pct(r['recent60d_mean_asset_total_return'])}</td>"
                f"<td>{pct(r['recent60d_mean_month_return'])}</td>"
                f"<td>{pct(r['recent60d_worst_month_return'])}</td>"
                f"<td>{pct(r['mean_exposure_share'])}</td>"
                "</tr>"
            )
        return "".join(rows)

    recent_flags = gate_flags.tail(18).copy()
    flag_rows = []
    for _, r in recent_flags.iterrows():
        flag_rows.append(
            "<tr>"
            f"<td>{r['month']}</td>"
            f"<td>{'✓' if int(r['gate_low_trend_low_vol']) else ''}</td>"
            f"<td>{'✓' if int(r['gate_low_trend_high_noise']) else ''}</td>"
            f"<td>{'✓' if int(r['gate_combined']) else ''}</td>"
            "</tr>"
        )

    html = f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Rank29 regime gate backtest</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .good {{ color:#047857; font-weight:600; }}
    .warn {{ color:#b45309; font-weight:600; }}
  </style>
</head>
<body>
  <p><a href="../scout_rank29_trendline_breakout_navigator_15m/report.html">← 返回 Rank29 主页</a></p>
  <h1>Rank29 · regime gate backtest</h1>
  <p class="muted">生成时间：{utc_now().strftime('%Y-%m-%d %H:%M:%S UTC')} ｜ 目标：验证“低趋势 + 高噪音”与“低趋势 + 低波动”两类坏环境 gate，比较 5 年整体表现与最近 120/60 天的修复效果。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <ul>
      <li><b>当前最值得继续推进的是 <code>low_trend_high_noise_w25</code></b>，不是 <code>low_trend_low_vol</code>，也不是直接 hard veto。</li>
      <li>原因：在 <b>10bps / 15bps</b> 下，<code>low_trend_high_noise</code> 能明显改善最近 <b>60d / 120d</b>，而 <code>w25</code> 比 <code>w00</code> 更温和，更适合先做 paper A/B。</li>
      <li><span class="warn">注意</span>：这个 gate 仍然会牺牲一部分 5 年长期总收益，所以它更像“修最近坏环境”的补丁，不是“全历史更优”的无脑升级版。</li>
    </ul>
  </div>

  <div class="card">
    <h2>gate 定义</h2>
    <ul>
      <li><code>low_trend_low_vol</code>：<code>trend_strength_20d_mean &lt;= {thresholds['trend_low_q33']:.6f}</code> 且 <code>realized_vol_20d_mean &lt;= {thresholds['vol_low_q33']:.6f}</code></li>
      <li><code>low_trend_high_noise</code>：<code>trend_strength_20d_mean &lt;= {thresholds['trend_low_q33']:.6f}</code> 且 <code>noise_ratio_20d_mean &gt;= {thresholds['noise_high_q67']:.6f}</code></li>
      <li><code>w25</code>：坏环境仓位降到 25%</li>
      <li><code>w00</code>：坏环境仓位降到 0%</li>
    </ul>
    <p class="muted">命中月份：low_trend_low_vol = {int(gate_flags['gate_low_trend_low_vol'].sum())}；low_trend_high_noise = {int(gate_flags['gate_low_trend_high_noise'].sum())}；combined = {int(gate_flags['gate_combined'].sum())}</p>
  </div>

  <div class="card">
    <h2>重点对比表：5 年 + 最近 120 天 + 最近 60 天</h2>
    <p>下面这张表专门给你看 baseline 与几种最 relevant 的 gate 版本。读法重点：如果一个 gate 的 <b>5 年降幅可接受</b>，同时 <b>120d / 60d 改善明显</b>，它才值得推进到下一轮 paper A/B。</p>

    <h3>6bps / side</h3>
    <table>
      <thead><tr><th>variant</th><th>5y mean asset total</th><th>5y mean month</th><th>120d mean asset total</th><th>120d mean month</th><th>120d worst month</th><th>60d mean asset total</th><th>60d mean month</th><th>60d worst month</th><th>mean exposure</th></tr></thead>
      <tbody>{make_rows(6.0)}</tbody>
    </table>

    <h3>10bps / side</h3>
    <table>
      <thead><tr><th>variant</th><th>5y mean asset total</th><th>5y mean month</th><th>120d mean asset total</th><th>120d mean month</th><th>120d worst month</th><th>60d mean asset total</th><th>60d mean month</th><th>60d worst month</th><th>mean exposure</th></tr></thead>
      <tbody>{make_rows(10.0)}</tbody>
    </table>

    <h3>15bps / side（最该盯的一档）</h3>
    <table>
      <thead><tr><th>variant</th><th>5y mean asset total</th><th>5y mean month</th><th>120d mean asset total</th><th>120d mean month</th><th>120d worst month</th><th>60d mean asset total</th><th>60d mean month</th><th>60d worst month</th><th>mean exposure</th></tr></thead>
      <tbody>{make_rows(15.0)}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>怎么读 15bps 这张表（人话版）</h2>
    <ul>
      <li>如果你只看长期 5 年，baseline 仍然最好，所以这个 gate 不是“全历史升级版”。</li>
      <li>但如果你关心 <b>最近坏环境的修复</b>，<code>low_trend_high_noise_w25</code> 往往比 baseline 更能改善最近窗口，尤其在更高 friction 下更明显。</li>
      <li>这说明：<b>坏环境里降仓</b>，比“完全不做”更像一个可先试运行的版本。</li>
    </ul>
  </div>

  <div class="card">
    <h2>最近 18 个月 gate 命中月份</h2>
    <table>
      <thead><tr><th>month</th><th>low_trend_low_vol</th><th>low_trend_high_noise</th><th>combined</th></tr></thead>
      <tbody>{''.join(flag_rows)}</tbody>
    </table>
  </div>
</body>
</html>
"""
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    trades = build_trades()
    regime_features = build_regime_monthly_features()
    gate_flags, thresholds = build_gate_flags(regime_features)
    gate_flags.to_csv(ARTIFACT_DIR / "gate_month_flags.csv", index=False)
    (ARTIFACT_DIR / "thresholds.json").write_text(json.dumps(thresholds, indent=2), encoding="utf-8")

    latest_entry = pd.to_datetime(trades["entry_ts"], utc=True).max()
    recent_cutoffs = {days: latest_entry - pd.Timedelta(days=days) for days in RECENT_WINDOWS}

    summary_frames = []
    trade_frames = []
    for cost in COSTS:
        summary, trade_frame = apply_gate_variants(trades, gate_flags, cost=cost, recent_cutoffs=recent_cutoffs)
        summary_frames.append(summary)
        trade_frames.append(trade_frame)

    summary_df = pd.concat(summary_frames, ignore_index=True).sort_values(["cost_bps_per_side", "mean_asset_total_return"], ascending=[True, False]).reset_index(drop=True)
    trade_df = pd.concat(trade_frames, ignore_index=True)
    summary_df.to_csv(ARTIFACT_DIR / "summary_by_cost.csv", index=False)
    trade_df.to_csv(ARTIFACT_DIR / "trade_level_variants.csv", index=False)

    write_report(summary_df, thresholds, gate_flags)
    render_site_html(summary_df, thresholds, gate_flags)
    print(ARTIFACT_DIR / "report.md")


if __name__ == "__main__":
    main()
