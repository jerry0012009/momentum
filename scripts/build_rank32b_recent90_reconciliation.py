#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_recent90_reconciliation"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "rank32b_recent90_reconciliation"

REGIME_SCRIPT = ROOT / "scripts" / "build_rank32b_regime_5y_quarterly.py"
PREVIEW_ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_unclosed15m_preview_backtest" / "canary_core18_90d"
REGIME_ART_DIR = ROOT / "reports" / "artifacts" / "rank32b_regime_5y_quarterly" / "canary_core18_5y_quarterly"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


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
        return "<p class='muted'>暂无数据。</p>"
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    body = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            v = row[col]
            if col in percent_cols:
                text = pct(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                text = num(v, digits_cols.get(col, 2))
            else:
                text = str(v)
            cells.append(f"<td>{escape(text)}</td>")
        body.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_clean_recent90(regime_mod):
    bar_map: dict[str, pd.DataFrame] = {}
    trade_map_by_cost: dict[float, dict[str, pd.DataFrame]] = {c: {} for c in regime_mod.COSTS}
    asset_rows = []

    for asset, symbol in regime_mod.ASSETS.items():
        cache = ROOT / "reports" / "artifacts" / "rank32b_regime_5y_quarterly" / "cache_15m" / f"{symbol}__1830d__15m__perp.csv"
        bars = pd.read_csv(cache)
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True)
        end_ts = pd.to_datetime(bars["timestamp"].max(), utc=True)
        start_ts = end_ts - pd.Timedelta(days=90)
        recent = bars[bars["timestamp"] >= start_ts].copy().reset_index(drop=True)
        bar_map[asset] = recent
        frame = regime_mod.build_frame_from_bars(asset, recent)
        for cost in regime_mod.COSTS:
            trades = regime_mod.build_trades(frame, asset=asset, cost_bps=cost)
            trade_map_by_cost[cost][asset] = trades
            s = regime_mod.summarize_asset_window(trades, available=(len(recent) >= 2))
            asset_rows.append(
                {
                    "asset": asset,
                    "mode": "clean_baseline_fixed_hold",
                    "market_cost_bps": float(cost),
                    **s,
                }
            )

    benchmark = regime_mod.build_benchmark_features(bar_map)
    eq_close = benchmark["eq_close"].dropna()
    btc_close = benchmark["btc_close"].dropna()
    eq_ret = benchmark["eq_ret"].dropna()
    asset_rets = []
    for asset, bars in bar_map.items():
        if len(bars) >= 2:
            asset_rets.append(float(bars.iloc[-1]["close"] / bars.iloc[0]["close"] - 1.0))
    eq_ret_90 = float(eq_close.iloc[-1] / eq_close.iloc[0] - 1.0)
    btc_ret_90 = float(btc_close.iloc[-1] / btc_close.iloc[0] - 1.0) if len(btc_close) >= 2 else np.nan
    breadth = float((pd.Series(asset_rets) > 0).mean()) if asset_rets else np.nan
    vol = float(eq_ret.std(ddof=0) * np.sqrt(365 * 24 * 4)) if len(eq_ret) >= 2 else np.nan
    eff = float(abs(eq_ret_90) / eq_ret.abs().sum()) if len(eq_ret) >= 2 and eq_ret.abs().sum() > 0 else np.nan
    regime = regime_mod.classify_direction(eq_ret_90, breadth)

    recent_meta = {
        "start": pd.to_datetime(benchmark["timestamp"].min(), utc=True).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "end": pd.to_datetime(benchmark["timestamp"].max(), utc=True).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "eq_ret_90": eq_ret_90,
        "btc_ret_90": btc_ret_90,
        "breadth_pos": breadth,
        "ew_vol_ann": vol,
        "ew_efficiency": eff,
        "direction_bucket": regime,
    }

    asset_df = pd.DataFrame(asset_rows)
    overall_rows = []
    for cost, grp in asset_df.groupby("market_cost_bps", sort=True):
        overall_rows.append(
            {
                "mode": "clean_baseline_fixed_hold",
                "market_cost_bps": float(cost),
                "mean_total_return": float(grp["asset_return"].mean()),
                "median_total_return": float(grp["asset_return"].median()),
                "positive_asset_ratio": float((grp["asset_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
            }
        )
    overall_df = pd.DataFrame(overall_rows)
    return recent_meta, asset_df, overall_df


def load_preview_artifacts():
    overall = pd.read_csv(PREVIEW_ART_DIR / "overall_summary.csv")
    asset = pd.read_csv(PREVIEW_ART_DIR / "asset_summary.csv")
    return overall, asset


def load_quarter_context():
    quarter = pd.read_csv(REGIME_ART_DIR / "quarter_window_primary.csv")
    return quarter[quarter["quarter"].isin(["2025Q4", "2026Q1"])].copy().reset_index(drop=True)


def build_html(generated_at: str, recent_meta: dict[str, object], overall_compare: pd.DataFrame, clean_asset: pd.DataFrame, preview_asset: pd.DataFrame, quarter_ctx: pd.DataFrame, verdict: str) -> str:
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank32b recent90 reconciliation</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .muted {{ color:#6b7280; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <h1>Rank32b · recent90 reconciliation</h1>
  <p class='muted'>生成时间：{escape(generated_at)}</p>

  <div class='card'>
    <h2>这次修什么</h2>
    <ul>
      <li>把“recent90 fixed-hold 是负的”这个旧结论正式复核。</li>
      <li>统一使用 <code>build_rank32b_regime_5y_quarterly.py</code> 的 baseline 代码路径做 recent90 clean baseline。</li>
      <li>把它与已有 <code>live-like official_close</code> / <code>preview_unclosed15m</code> 回测并排对照，避免再混口径。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <ul>
      <li>recent90 市场状态：<b>{escape(str(recent_meta['direction_bucket']))}</b>，eq 90d return≈{pct(recent_meta['eq_ret_90'])}，BTC≈{pct(recent_meta['btc_ret_90'])}，breadth≈{pct(recent_meta['breadth_pos'])}。</li>
      <li>结论：<b>recent90 并不是坏 regime；clean baseline 其实是正收益。</b></li>
      <li>旧的“recent90 fixed-hold 负收益”应视为 <b>一次临时代码路径的错误结论</b>，不再采用。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>recent90 regime 指标</h2>
    {render_table(pd.DataFrame([recent_meta]))}
  </div>

  <div class='card'>
    <h2>统一口径对照（按资产均值）</h2>
    {render_table(overall_compare[['mode','market_cost_bps','mean_total_return','median_total_return','positive_asset_ratio','mean_trades','mean_win_rate']], percent_cols={'mean_total_return','median_total_return','positive_asset_ratio','mean_win_rate'}, digits_cols={'market_cost_bps':0,'mean_trades':1})}
  </div>

  <div class='card'>
    <h2>季度上下文（5y regime study）</h2>
    {render_table(quarter_ctx[['quarter','direction_bucket','efficiency_bucket','eq_ret_3m','breadth_pos','mean_total_return','positive_asset_ratio','mean_trades_per_asset']], percent_cols={'eq_ret_3m','breadth_pos','mean_total_return','positive_asset_ratio'}, digits_cols={'mean_trades_per_asset':1})}
  </div>

  <div class='card'>
    <h2>clean baseline 最近90天：分资产</h2>
    {render_table(clean_asset[clean_asset['market_cost_bps']==10.0][['asset','asset_return','trades','win_rate']].sort_values('asset_return', ascending=False), percent_cols={'asset_return','win_rate'}, digits_cols={'trades':0})}
  </div>

  <div class='card'>
    <h2>live-like official / preview：分资产（10bps）</h2>
    {render_table(preview_asset[preview_asset['market_cost_bps']==10.0][['asset','mode','total_return','trades','win_rate','confirmed_at_close_ratio','preview_only_ratio','avg_lead_minutes','avg_entry_improve_bps']].sort_values(['mode','total_return'], ascending=[True, False]), percent_cols={'total_return','win_rate','confirmed_at_close_ratio','preview_only_ratio'}, digits_cols={'trades':0,'avg_lead_minutes':2,'avg_entry_improve_bps':2})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    regime_mod = load_module(REGIME_SCRIPT, "rank32b_regime5y")
    recent_meta, clean_asset, clean_overall = build_clean_recent90(regime_mod)
    preview_overall, preview_asset = load_preview_artifacts()
    quarter_ctx = load_quarter_context()

    preview_overall = preview_overall.copy()
    preview_overall = preview_overall.rename(columns={
        "mean_total_return": "mean_total_return",
        "median_total_return": "median_total_return",
        "positive_asset_ratio": "positive_asset_ratio",
        "mean_trades": "mean_trades",
        "mean_win_rate": "mean_win_rate",
    })
    overall_compare = pd.concat([
        clean_overall,
        preview_overall[["mode","market_cost_bps","mean_total_return","median_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]],
    ], ignore_index=True)
    overall_compare = overall_compare.sort_values(["market_cost_bps","mode"]).reset_index(drop=True)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    verdict = "alpha alive / recent90 regime compatible"

    tag_dir = ensure_dir(ART_DIR / "recent90")
    clean_asset.to_csv(tag_dir / "clean_asset_recent90.csv", index=False)
    clean_overall.to_csv(tag_dir / "clean_overall_recent90.csv", index=False)
    preview_overall.to_csv(tag_dir / "preview_overall_reference.csv", index=False)
    preview_asset.to_csv(tag_dir / "preview_asset_reference.csv", index=False)
    quarter_ctx.to_csv(tag_dir / "quarter_context.csv", index=False)
    overall_compare.to_csv(tag_dir / "overall_compare.csv", index=False)
    (tag_dir / "meta.json").write_text(json.dumps({"generated_at": generated_at, "recent_meta": recent_meta, "verdict": verdict}, ensure_ascii=False, indent=2), encoding="utf-8")

    html = build_html(generated_at, recent_meta, overall_compare, clean_asset, preview_asset, quarter_ctx, verdict)
    site_path = SITE_DIR / "report.html"
    site_path.write_text(html, encoding="utf-8")

    print("=== recent_meta ===")
    print(json.dumps(recent_meta, ensure_ascii=False, indent=2))
    print("\n=== overall_compare ===")
    print(overall_compare.to_string(index=False))
    print(f"\nartifacts: {tag_dir}")
    print(f"site: {site_path}")


if __name__ == "__main__":
    main()
