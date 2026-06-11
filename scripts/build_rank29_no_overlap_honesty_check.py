#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_manual_narrow_paper_lanes import (  # noqa: E402
    ASSET_TO_BINANCE,
    build_rank29_trades_baseline,
    build_rank29_trades_confirmed_lines,
)

ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank29_trendline_breakout_navigator_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m"
REPORT_PATH = SITE_DIR / "no_overlap_honesty_check.html"
CACHE_DIR = ROOT / "reports" / "artifacts" / "scout_tau_band_breakout_15m" / "cache"

COSTS = [6.0, 10.0, 15.0, 20.0]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(x: float | int | None, d: int = 2) -> str:
    if x is None or pd.isna(x):
        return "-"
    return f"{float(x) * 100:.{d}f}%"


def num(x: float | int | None, d: int = 2) -> str:
    if x is None or pd.isna(x):
        return "-"
    return f"{float(x):.{d}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str], digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    digits_cols = digits_cols or {}
    th = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            if c in percent_cols:
                txt = pct(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                txt = num(v, digits_cols.get(c, 2))
            else:
                txt = str(v)
            tds.append(f"<td>{escape(txt)}</td>")
        rows.append(f"<tr>{''.join(tds)}</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_cached_bars(symbol: str, asset: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{symbol}__120d__15m.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["asset"] = asset
    return df.sort_values("timestamp").reset_index(drop=True)


def apply_cost_grid(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=[
            "asset",
            "variant",
            "mode",
            "signal_engine",
            "cost_bps_per_side",
            "event_idx",
            "event_ts",
            "entry_ts",
            "exit_ts",
            "direction",
            "trigger_tf",
            "entry_price",
            "exit_price",
            "gross_ret",
            "net_ret",
            "hold_bars",
            "complete_trade",
        ])
    work = trades.copy()
    out_parts: list[pd.DataFrame] = []
    gross = work["gross_ret"].astype(float)
    for cost in COSTS:
        cost_rate = float(cost) / 10000.0
        part = work.copy()
        part["cost_bps_per_side"] = float(cost)
        part["net_ret"] = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
        out_parts.append(part)
    return pd.concat(out_parts, ignore_index=True)


def summarize(asset: str, engine: str, cost: float, trades: pd.DataFrame) -> dict[str, object]:
    if trades.empty:
        return {
            "asset": asset,
            "signal_engine": engine,
            "cost_bps_per_side": float(cost),
            "trades": 0,
            "win_rate": np.nan,
            "avg_net_ret": np.nan,
            "total_return": 0.0,
        }
    return {
        "asset": asset,
        "signal_engine": engine,
        "cost_bps_per_side": float(cost),
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()),
        "avg_net_ret": float(trades["net_ret"].mean()),
        "total_return": float((1.0 + trades["net_ret"]).prod() - 1.0),
    }


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    rows = []
    trade_exports: list[tuple[str, pd.DataFrame]] = []
    honesty_rows: list[dict[str, object]] = []
    for asset, symbol in ASSET_TO_BINANCE.items():
        bars = load_cached_bars(symbol, asset)
        old = build_rank29_trades_confirmed_lines(asset, bars)
        causal = build_rank29_trades_baseline(asset, bars)
        old = apply_cost_grid(old)
        causal = apply_cost_grid(causal)

        old_keys = set(old["event_ts"].astype(str) + "|" + old["direction"].astype(str) + "|" + old["trigger_tf"].astype(str)) if not old.empty else set()
        causal_keys = set(causal["event_ts"].astype(str) + "|" + causal["direction"].astype(str) + "|" + causal["trigger_tf"].astype(str)) if not causal.empty else set()
        honesty_rows.append(
            {
                "asset": asset,
                "old_signals": len(old_keys),
                "causal_signals": len(causal_keys),
                "hindsight_only": len(old_keys - causal_keys),
                "misleading_pct": (len(old_keys - causal_keys) / len(old_keys)) if old_keys else np.nan,
            }
        )

        for engine_name, frame in [("confirmed_line_only", old), ("causal_replay", causal)]:
            for cost in COSTS:
                part = frame[frame["cost_bps_per_side"] == float(cost)].copy().reset_index(drop=True)
                rows.append(summarize(asset, engine_name, cost, part))
            if engine_name == "causal_replay":
                for cost in COSTS:
                    part = frame[frame["cost_bps_per_side"] == float(cost)].copy().reset_index(drop=True)
                    trade_exports.append((f"{asset.replace('-', '_').lower()}_no_overlap_guard_trades_{int(cost)}bps.csv", part))

    summary = pd.DataFrame(rows)
    overall = (
        summary.groupby(["signal_engine", "cost_bps_per_side"], as_index=False)
        .agg(
            assets_tested=("asset", "nunique"),
            positive_assets=("total_return", lambda s: int((s > 0).sum())),
            mean_total_return=("total_return", "mean"),
            mean_trades=("trades", "mean"),
            min_trades=("trades", "min"),
            mean_win_rate=("win_rate", "mean"),
        )
        .sort_values(["signal_engine", "cost_bps_per_side"])
        .reset_index(drop=True)
    )
    overall["positive_asset_ratio"] = overall["positive_assets"] / overall["assets_tested"].replace(0, np.nan)
    honesty = pd.DataFrame(honesty_rows).sort_values("asset").reset_index(drop=True)

    causal6 = overall[(overall["signal_engine"] == "causal_replay") & (overall["cost_bps_per_side"] == 6.0)]
    headline = "Rank 29 strict-causal + no-overlap 后仍可继续观察。"
    verdict = "keep watching"
    if causal6.empty or float(causal6.iloc[0]["mean_total_return"]) <= 0 or float(causal6.iloc[0]["positive_asset_ratio"]) < (2 / 3):
        headline = "Rank 29 strict-causal + no-overlap 后不再支持原先的健康判断，应压回重评。"
        verdict = "reassess / likely park"

    summary.to_csv(ART_DIR / "no_overlap_asset_summary.csv", index=False)
    overall.to_csv(ART_DIR / "no_overlap_overall_summary.csv", index=False)
    honesty.to_csv(ART_DIR / "no_overlap_signal_honesty_summary.csv", index=False)
    for filename, frame in trade_exports:
        frame.to_csv(ART_DIR / filename, index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 29 no-overlap honesty check</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.66; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; }}
    .muted {{ color:#6b7280; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="report.html">← 返回 Rank 29 主报告</a></p>
  <h1>Rank 29 · no-overlap honesty check（strict-causal rewrite）</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 固定样本 BTC/ETH/SOL 120d 15m，主变体 breakout_align_ge2，固定持有 8 bars，且同资产不重叠持仓。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>
      <li>旧口径和 causal 口径都在同样的 no-overlap 约束下重算；差别只在于是否允许未来确认的结构回填到历史 bars。</li>
      <li>从现在起，写给交易判断的 no-overlap 结果只认 <code>causal_replay</code>。</li>
      <li>本页生成的 <code>*_no_overlap_guard_trades_*bps.csv</code> 也已改成 strict-causal 版本，供后面的时间稳定性检查直接复用。</li>
    </ul>
  </div>

  <div class="card">
    <h2>overall summary</h2>
    {render_table(overall[["signal_engine","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","min_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"cost_bps_per_side":0,"mean_trades":1,"min_trades":0})}
  </div>

  <div class="card">
    <h2>per-asset summary</h2>
    {render_table(summary[["asset","signal_engine","cost_bps_per_side","trades","total_return","win_rate","avg_net_ret"]], percent_cols={"total_return","win_rate","avg_net_ret"}, digits_cols={"cost_bps_per_side":0,"trades":0})}
  </div>

  <div class="card">
    <h2>未来函数污染比例（no-overlap 主口径）</h2>
    {render_table(honesty, percent_cols={"misleading_pct"}, digits_cols={"old_signals":0,"causal_signals":0,"hindsight_only":0})}
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")

    meta = pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank29_trendline_breakout_navigator",
            "check": "no_overlap_guard_honesty_check",
            "hard_verdict": verdict,
            "headline": headline,
        }
    ])
    meta.to_csv(ART_DIR / "no_overlap_trial_meta.csv", index=False)

    print("[ok] rank29 no-overlap honesty check generated")
    print("[artifact]", ART_DIR / "no_overlap_overall_summary.csv")
    print("[site]", REPORT_PATH)
    print("[verdict]", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
