#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from momentum.signals.trendline_breakout_navigator import (  # noqa: E402
    TrendlineBreakoutNavigatorConfig,
    compute_trendline_breakout_navigator,
)

CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank29_trendline_breakout_navigator_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m"
REPORT_PATH = SITE_DIR / "report.html"

ASSETS = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
PREFIX_PRIORITY = ["tbn_short", "tbn_medium", "tbn_long"]
BREAKOUT_VARIANTS = [
    ("breakout_align_ge1", 1),
    ("breakout_align_ge2", 2),
]
SIGNAL_ENGINES = [
    ("confirmed_line_only", True),
    ("causal_replay", False),
]
COSTS = [6.0, 10.0, 15.0, 20.0]
PRIMARY_VARIANT = "breakout_align_ge2"
PRIMARY_COST = 6.0
FAILURE_LOOKAHEAD = 4
HOLD_BARS = 8


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def num(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value):.{digits}f}"


def render_table(df: pd.DataFrame, *, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
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
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def build_asset_frame(asset: str, symbol: str, *, backfill_history: bool) -> pd.DataFrame:
    bars = load_cached_bars(symbol, asset)
    nav = compute_trendline_breakout_navigator(
        bars[["timestamp", "high", "low", "close"]].copy(),
        config=TrendlineBreakoutNavigatorConfig(backfill_history=backfill_history),
    )
    full = pd.concat(
        [
            bars.reset_index(drop=True),
            nav.drop(columns=["timestamp", "high", "low", "close"], errors="ignore").reset_index(drop=True),
        ],
        axis=1,
    )
    return full


def choose_breakout_event(row: pd.Series, *, min_abs_composite: int) -> tuple[str, int] | None:
    composite = int(row.get("tbn_composite_trend", 0) or 0)
    for prefix in PREFIX_PRIORITY:
        if int(row.get(f"{prefix}_line_is_provisional", 0) or 0) == 1:
            continue
        if row.get(f"{prefix}_breakout_bull") == 1 and composite >= min_abs_composite:
            return prefix, 1
        if row.get(f"{prefix}_breakout_bear") == 1 and composite <= -min_abs_composite:
            return prefix, -1
    return None


def detect_line_failure(full: pd.DataFrame, event_idx: int, prefix: str, direction: int, *, lookahead: int) -> int:
    line_value = full.iloc[event_idx].get(f"{prefix}_line_value")
    line_slope = full.iloc[event_idx].get(f"{prefix}_line_slope")
    if pd.isna(line_value):
        return 1
    line_value = float(line_value)
    line_slope = 0.0 if pd.isna(line_slope) else float(line_slope)
    for step in range(1, lookahead + 1):
        idx = event_idx + step
        if idx >= len(full):
            break
        future_line = line_value + line_slope * step
        close = float(full.iloc[idx]["close"])
        if direction > 0 and close <= future_line:
            return 1
        if direction < 0 and close >= future_line:
            return 1
    return 0


def build_breakout_trades(
    full: pd.DataFrame,
    *,
    asset: str,
    signal_engine: str,
    variant: str,
    min_abs_composite: int,
    cost: float,
    no_overlap: bool = False,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    cost_rate = float(cost) / 10000.0
    last_exit = -1
    for idx, row in full.iterrows():
        chosen = choose_breakout_event(row, min_abs_composite=min_abs_composite)
        if chosen is None:
            continue
        prefix, direction = chosen
        entry_idx = idx + 1
        exit_idx = min(idx + HOLD_BARS, len(full) - 1)
        if entry_idx >= len(full):
            continue
        if no_overlap and idx <= last_exit:
            continue
        entry_price = float(full.iloc[entry_idx]["open"])
        exit_price = float(full.iloc[exit_idx]["close"])
        gross_ret = (exit_price / entry_price - 1.0) * direction
        net_ret = (1.0 + gross_ret) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        rows.append(
            {
                "asset": asset,
                "signal_engine": signal_engine,
                "variant": variant,
                "cost_bps_per_side": float(cost),
                "event_idx": int(idx),
                "event_ts": pd.to_datetime(full.iloc[idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_ts": pd.to_datetime(full.iloc[entry_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "exit_ts": pd.to_datetime(full.iloc[exit_idx]["timestamp"], utc=True).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "direction": "long" if direction > 0 else "short",
                "trigger_tf": prefix.replace("tbn_", ""),
                "composite_trend": int(row.get("tbn_composite_trend", 0) or 0),
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_ret": gross_ret,
                "net_ret": net_ret,
                "hold_bars": int(exit_idx - entry_idx + 1),
                "false_break_ratio": float(detect_line_failure(full, idx, prefix, direction, lookahead=FAILURE_LOOKAHEAD)),
            }
        )
        last_exit = exit_idx
    return pd.DataFrame(rows)


def summarize_asset(trades: pd.DataFrame, *, asset: str, signal_engine: str, variant: str, cost: float) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "signal_engine": signal_engine,
            "variant": variant,
            "cost_bps_per_side": float(cost),
            "trades": 0,
            "long_share": np.nan,
            "short_share": np.nan,
            "short_tf_share": np.nan,
            "medium_tf_share": np.nan,
            "long_tf_share": np.nan,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "median_net_ret": np.nan,
            "total_return": 0.0,
            "false_break_ratio": np.nan,
            "avg_hold_bars": np.nan,
        }
    tf_counts = trades["trigger_tf"].value_counts(normalize=True)
    return {
        "asset": asset,
        "signal_engine": signal_engine,
        "variant": variant,
        "cost_bps_per_side": float(cost),
        "trades": int(len(trades)),
        "long_share": float((trades["direction"] == "long").mean()),
        "short_share": float((trades["direction"] == "short").mean()),
        "short_tf_share": float(tf_counts.get("short", 0.0)),
        "medium_tf_share": float(tf_counts.get("medium", 0.0)),
        "long_tf_share": float(tf_counts.get("long", 0.0)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "median_net_ret": float(trades["net_ret"].median()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
        "false_break_ratio": float(trades["false_break_ratio"].mean()),
        "avg_hold_bars": float(trades["hold_bars"].mean()),
    }


def build_overall_summary(asset_summary: pd.DataFrame) -> pd.DataFrame:
    if asset_summary.empty:
        return pd.DataFrame()
    out = (
        asset_summary.groupby(["signal_engine", "variant", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            median_total_return=("total_return", "median"),
            mean_win_rate=("win_rate", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
            mean_false_break_ratio=("false_break_ratio", "mean"),
            mean_short_tf_share=("short_tf_share", "mean"),
        )
        .sort_values(["signal_engine", "cost_bps_per_side", "variant"], ascending=[True, True, True])
        .reset_index(drop=True)
    )
    out["positive_asset_ratio"] = out["positive_assets"] / out["assets_tested"].replace(0, np.nan)
    return out


def build_signal_honesty_summary(trades_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    primary = trades_df[(trades_df["variant"] == PRIMARY_VARIANT) & (trades_df["cost_bps_per_side"] == PRIMARY_COST)].copy()
    if primary.empty:
        return pd.DataFrame(), pd.DataFrame()
    primary["signal_key"] = (
        primary["asset"].astype(str)
        + "|"
        + primary["event_ts"].astype(str)
        + "|"
        + primary["direction"].astype(str)
        + "|"
        + primary["trigger_tf"].astype(str)
    )
    rows: list[dict[str, object]] = []
    detail_parts: list[pd.DataFrame] = []
    for asset, g in primary.groupby("asset", sort=True):
        old = g[g["signal_engine"] == "confirmed_line_only"].copy()
        causal = g[g["signal_engine"] == "causal_replay"].copy()
        old_keys = set(old["signal_key"])
        causal_keys = set(causal["signal_key"])
        hindsight_only = old[~old["signal_key"].isin(causal_keys)].copy()
        overlap = old[old["signal_key"].isin(causal_keys)].copy()
        rows.append(
            {
                "asset": asset,
                "old_signals": int(len(old)),
                "causal_signals": int(len(causal)),
                "hindsight_only": int(len(hindsight_only)),
                "overlap_signals": int(len(overlap)),
                "misleading_pct": float(len(hindsight_only) / len(old)) if len(old) else np.nan,
            }
        )
        if not hindsight_only.empty:
            detail_parts.append(hindsight_only[[c for c in ["asset", "event_ts", "direction", "trigger_tf", "entry_ts"] if c in hindsight_only.columns]].copy())
    summary = pd.DataFrame(rows).sort_values("asset").reset_index(drop=True)
    detail = pd.concat(detail_parts, ignore_index=True) if detail_parts else pd.DataFrame(columns=["asset", "event_ts", "direction", "trigger_tf", "entry_ts"])
    if not detail.empty:
        detail = detail.sort_values("event_ts", ascending=False).reset_index(drop=True)
    return summary, detail


def derive_verdict(overall_summary: pd.DataFrame, honesty_summary: pd.DataFrame) -> tuple[str, list[str], str]:
    old_row = overall_summary[
        (overall_summary["signal_engine"] == "confirmed_line_only")
        & (overall_summary["variant"] == PRIMARY_VARIANT)
        & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)
    ]
    causal_row = overall_summary[
        (overall_summary["signal_engine"] == "causal_replay")
        & (overall_summary["variant"] == PRIMARY_VARIANT)
        & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)
    ]
    if old_row.empty or causal_row.empty:
        return (
            "当前没有产出可比较的 old vs causal 主样本结果，先暂停晋级判断。",
            ["缺少 primary summary，说明这轮 causal 复盘还不够完整。"],
            "pause / incomplete evidence",
        )

    old = old_row.iloc[0]
    causal = causal_row.iloc[0]
    misleading_pct = float(honesty_summary["hindsight_only"].sum() / honesty_summary["old_signals"].sum()) if not honesty_summary.empty and float(honesty_summary["old_signals"].sum()) > 0 else np.nan

    if float(causal["mean_total_return"]) > 0 and float(causal["positive_asset_ratio"]) >= (2 / 3):
        verdict = "survives causal audit"
        headline = "Rank 29 在 strict-causal 口径下仍有存活证据，但必须按 causal 结果重估，不得再引用旧口径收益。"
    else:
        verdict = "fails causal health check"
        headline = "Rank 29 旧回测被未来函数严重放大；按 strict-causal 主样本重算后，不足以继续沿用原健康结论。"

    bullets = [
        f"旧口径（confirmed_line_only）主样本 {PRIMARY_VARIANT} @ 6bps：mean_total_return {pct(old['mean_total_return'])}，positive_asset_ratio {pct(old['positive_asset_ratio'])}，mean_trades {num(old['mean_trades'], 1)}。",
        f"新口径（causal_replay）主样本 {PRIMARY_VARIANT} @ 6bps：mean_total_return {pct(causal['mean_total_return'])}，positive_asset_ratio {pct(causal['positive_asset_ratio'])}，mean_trades {num(causal['mean_trades'], 1)}。",
        f"旧主样本信号里，被未来函数误导出来的比例：{pct(misleading_pct)}（按 asset + event_ts + direction + trigger_tf 对齐）。",
        "因此从现在起，Rank 29 的基准结论只能引用 causal 结果；旧口径保留为污染对照，不再用于策略晋级。",
    ]
    return headline, bullets, verdict


def write_report(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, honesty_summary: pd.DataFrame, honesty_detail: pd.DataFrame, trial_meta: pd.DataFrame) -> None:
    ensure_dir(SITE_DIR)
    meta = trial_meta.iloc[0].to_dict() if not trial_meta.empty else {}
    headline, bullets, _ = derive_verdict(overall_summary, honesty_summary)
    bullets_html = "".join(f"<li>{escape(x)}</li>" for x in bullets)

    compare_slice = overall_summary[
        (overall_summary["variant"] == PRIMARY_VARIANT)
        & (overall_summary["cost_bps_per_side"] == PRIMARY_COST)
    ][[
        "signal_engine",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "min_trades",
        "mean_win_rate",
        "mean_false_break_ratio",
    ]]

    asset_slice = asset_summary[
        (asset_summary["variant"] == PRIMARY_VARIANT)
        & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)
    ][[
        "asset",
        "signal_engine",
        "trades",
        "total_return",
        "win_rate",
        "false_break_ratio",
        "avg_net_ret",
    ]].sort_values(["asset", "signal_engine"]).reset_index(drop=True)

    cost_slice = overall_summary[
        overall_summary["variant"] == PRIMARY_VARIANT
    ][[
        "signal_engine",
        "cost_bps_per_side",
        "mean_total_return",
        "positive_asset_ratio",
        "mean_false_break_ratio",
        "mean_trades",
        "min_trades",
    ]].sort_values(["signal_engine", "cost_bps_per_side"]).reset_index(drop=True)

    honesty_total_old = int(honesty_summary["old_signals"].sum()) if not honesty_summary.empty else 0
    honesty_total_causal = int(honesty_summary["causal_signals"].sum()) if not honesty_summary.empty else 0
    honesty_total_honly = int(honesty_summary["hindsight_only"].sum()) if not honesty_summary.empty else 0
    honesty_ratio = (honesty_total_honly / honesty_total_old) if honesty_total_old else np.nan

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scout Seat · Rank 29 strict-causal reassessment</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1120px; margin: 40px auto; padding: 0 18px; line-height: 1.68; color: #111827; background: #f8fafc; }}
    h1,h2,h3 {{ line-height: 1.25; }}
    .muted {{ color:#6b7280; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    ul {{ padding-left:20px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <p><a href="../../index.html">← 返回首页</a></p>
  <h1>Scout Seat · Rank 29 strict-causal reassessment / 15m crypto</h1>
  <p class="muted">生成时间：{escape(str(meta.get('generated_at_utc', '-')))} ｜ 复盘对象仍是同一套 <code>Binance 120d / 15m / BTC+ETH+SOL</code> 主样本，但这次把 old 与 strict-causal 放到同一页正面对比。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{bullets_html}</ul>
  </div>

  <div class="card">
    <h2>这次到底改了什么</h2>
    <ul>
      <li><b>旧口径：</b><code>confirmed_line_only</code> 会在后续 pivot 确认后把线和趋势状态回填到更早 bars，再去扫信号。</li>
      <li><b>新口径：</b><code>causal_replay</code> 使用单次全样本 strict-causal frame：允许当前 bar 看到已确认结构，但不把未来才确认的状态回填到历史 bars。</li>
      <li>所以这页回答的是：<b>同样的 120d 样本、同样的持有期与费用，只把未来函数拿掉以后，这条线还剩多少真实表现。</b></li>
    </ul>
  </div>

  <div class="card">
    <h2>主样本：old vs strict-causal（{escape(PRIMARY_VARIANT)} @ 6bps）</h2>
    {render_table(compare_slice, percent_cols={'mean_total_return', 'positive_asset_ratio', 'mean_win_rate', 'mean_false_break_ratio'}, digits_cols={'mean_trades': 1, 'min_trades': 0})}
  </div>

  <div class="card">
    <h2>未来函数污染比例（主样本）</h2>
    <ul>
      <li>旧口径信号数：<b>{honesty_total_old}</b></li>
      <li>strict-causal 信号数：<b>{honesty_total_causal}</b></li>
      <li>hindsight-only：<b>{honesty_total_honly}</b></li>
      <li>误导比例：<b>{pct(honesty_ratio)}</b></li>
    </ul>
    {render_table(honesty_summary, percent_cols={'misleading_pct'}, digits_cols={'old_signals': 0, 'causal_signals': 0, 'hindsight_only': 0, 'overlap_signals': 0})}
  </div>

  <div class="card">
    <h2>主样本按资产拆开（{escape(PRIMARY_VARIANT)} @ 6bps）</h2>
    {render_table(asset_slice, percent_cols={'total_return', 'win_rate', 'false_break_ratio', 'avg_net_ret'}, digits_cols={'trades': 0})}
  </div>

  <div class="card">
    <h2>主样本成本梯度（只看 {escape(PRIMARY_VARIANT)}）</h2>
    {render_table(cost_slice, percent_cols={'mean_total_return', 'positive_asset_ratio', 'mean_false_break_ratio'}, digits_cols={'cost_bps_per_side': 0, 'mean_trades': 1, 'min_trades': 0})}
  </div>

  <div class="card">
    <h2>最近 hindsight-only 样本</h2>
    {render_table(honesty_detail.head(20), percent_cols=set(), digits_cols={})}
    <p class="muted">这些就是“旧回测会记成可交易，但 strict-causal 下并不成立”的代表样本。</p>
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    all_trades: list[pd.DataFrame] = []
    asset_rows: list[dict[str, object]] = []

    for asset, symbol in ASSETS.items():
        for signal_engine, use_backfill in SIGNAL_ENGINES:
            full = build_asset_frame(asset, symbol, backfill_history=use_backfill)
            signal_name = f"{asset.replace('-', '_').lower()}_{signal_engine}_signals.csv"
            full.to_csv(ART_DIR / signal_name, index=False)
            for variant, min_abs_composite in BREAKOUT_VARIANTS:
                for cost in COSTS:
                    trades = build_breakout_trades(
                        full,
                        asset=asset,
                        signal_engine=signal_engine,
                        variant=variant,
                        min_abs_composite=min_abs_composite,
                        cost=cost,
                        no_overlap=False,
                    )
                    if not trades.empty:
                        all_trades.append(trades)
                    asset_rows.append(summarize_asset(trades, asset=asset, signal_engine=signal_engine, variant=variant, cost=cost))

    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    asset_summary = pd.DataFrame(asset_rows)
    overall_summary = build_overall_summary(asset_summary)
    honesty_summary, honesty_detail = build_signal_honesty_summary(trades_df)
    headline, bullets, verdict = derive_verdict(overall_summary, honesty_summary)

    trial_meta = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank29_trendline_breakout_navigator",
            "sample_window": "Binance 120d / 15m / BTC+ETH+SOL",
            "primary_variant": PRIMARY_VARIANT,
            "primary_cost_bps_per_side": PRIMARY_COST,
            "hold_bars": HOLD_BARS,
            "failure_lookahead_bars": FAILURE_LOOKAHEAD,
            "hard_verdict": verdict,
            "headline": headline,
            "evidence_1": bullets[0] if bullets else "",
            "evidence_2": bullets[1] if len(bullets) > 1 else "",
        }
    ])

    if not trades_df.empty:
        trades_df.to_csv(ART_DIR / "trades.csv", index=False)
    asset_summary.to_csv(ART_DIR / "asset_summary.csv", index=False)
    overall_summary.to_csv(ART_DIR / "overall_summary.csv", index=False)
    honesty_summary.to_csv(ART_DIR / "signal_honesty_summary.csv", index=False)
    honesty_detail.to_csv(ART_DIR / "signal_honesty_detail.csv", index=False)
    trial_meta.to_csv(ART_DIR / "trial_meta.csv", index=False)

    write_report(overall_summary, asset_summary, honesty_summary, honesty_detail, trial_meta)
    print("[ok] rank29 strict-causal reassessment generated")
    print("[artifact]", ART_DIR / "overall_summary.csv")
    print("[site]", REPORT_PATH)
    print("[verdict]", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
