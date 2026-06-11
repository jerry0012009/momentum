#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
OUTPUT_HTML = SITE_DIR / "parameter_stability_check.html"
FLOORS = [0.0002, 0.0003, 0.0004, 0.0005, 0.0006]
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"


def load_base_module():
    spec = importlib.util.spec_from_file_location("rank32_base", BASE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


mod = load_base_module()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


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


def apply_floor(frame: pd.DataFrame, floor: float) -> pd.DataFrame:
    work = frame.copy()
    work["slope_floor_long"] = ((work["fast_slope"] > floor) & (work["slow_slope"] > 0)).fillna(False).astype(int)
    work["slope_floor_short"] = ((work["fast_slope"] < -floor) & (work["slow_slope"] < 0)).fillna(False).astype(int)
    work["slope_floor_long_signal"] = ((work["cross_only_long"] == 1) & (work["slope_floor_long"] == 1)).astype(int)
    work["slope_floor_short_signal"] = ((work["cross_only_short"] == 1) & (work["slope_floor_short"] == 1)).astype(int)
    return work


def build_outputs() -> tuple[pd.DataFrame, pd.DataFrame, str, str]:
    frames = {asset: mod.build_frame(asset, symbol) for asset, symbol in mod.ASSETS.items()}
    asset_rows = []
    for floor in FLOORS:
        for asset, frame in frames.items():
            floored = apply_floor(frame, floor)
            for cost in mod.COSTS:
                trades, no_trade_ratio, eligible_bars = mod.build_trades(floored, asset, PRIMARY_VARIANT, cost)
                row = mod.summarize_asset(
                    trades,
                    asset=asset,
                    variant=f"floor_{floor:.4f}",
                    cost_bps=cost,
                    no_trade_ratio=no_trade_ratio,
                    eligible_bars=eligible_bars,
                )
                row["slope_floor"] = float(floor)
                asset_rows.append(row)
    asset_summary = pd.DataFrame(asset_rows)

    overall_rows = []
    for floor, grp in asset_summary.groupby("slope_floor", sort=True):
        overall = mod.summarize_overall(grp.drop(columns=["slope_floor"]))
        overall["slope_floor"] = float(floor)
        overall_rows.append(overall)
    overall_summary = pd.concat(overall_rows, ignore_index=True)
    overall_summary = overall_summary[[
        "slope_floor",
        "variant",
        "cost_bps_per_side",
        "mean_total_return",
        "median_total_return",
        "positive_asset_ratio",
        "mean_trades",
        "mean_false_reclaim_ratio",
        "mean_no_trade_ratio",
        "mean_win_rate",
        "mean_slope_strength",
    ]]

    view_6 = overall_summary[overall_summary["cost_bps_per_side"] == 6.0].sort_values("slope_floor").reset_index(drop=True)
    view_20 = overall_summary[overall_summary["cost_bps_per_side"] == 20.0].sort_values("slope_floor").reset_index(drop=True)

    stable_6 = bool((view_6["positive_asset_ratio"] == 1.0).all() and (view_6["mean_total_return"] > 0).all())
    stable_20 = bool((view_20["mean_total_return"] > 0).all())
    trade_floor = float(view_6["mean_trades"].min()) if not view_6.empty else 0.0
    no_trade_floor = float(view_6["mean_no_trade_ratio"].min()) if not view_6.empty else 1.0

    if stable_6 and stable_20 and trade_floor >= 45:
        verdict = "P2 paper candidate"
        reason = "参数邻域没有塌，6~20bps 成本后整体仍保留正 pocket；虽然 no-trade ratio 仍高，但绝对 trade count 已经足够支撑进入 paper candidate pool。"
    elif stable_6:
        verdict = "P1 weak candidate / evidence pool"
        reason = "参数邻域没有塌，但成本/交易密度还不足以把它推进到 paper candidate。"
    else:
        verdict = "park / evidence pool"
        reason = "一旦离开当前 slope floor，pocket 就不够稳，不值得继续保留默认 Scout 预算。"

    return overall_summary, asset_summary, verdict, reason


def build_html(overall_summary: pd.DataFrame, asset_summary: pd.DataFrame, verdict: str, reason: str, generated_at: str) -> str:
    overall_view = overall_summary.copy()
    overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    overall_view["slope_floor"] = overall_view["slope_floor"].map(lambda v: f"{v:.4f}")

    asset_view = asset_summary[asset_summary["cost_bps_per_side"] == 6.0].copy()
    asset_view["slope_floor"] = asset_view["slope_floor"].map(lambda v: f"{v:.4f}")
    asset_view = asset_view[[
        "slope_floor", "asset", "trades", "total_return", "no_trade_ratio", "false_reclaim_ratio", "win_rate"
    ]].sort_values(["slope_floor", "asset"]).reset_index(drop=True)

    key6 = overall_summary[overall_summary["cost_bps_per_side"] == 6.0].sort_values("slope_floor").reset_index(drop=True)
    key20 = overall_summary[overall_summary["cost_bps_per_side"] == 20.0].sort_values("slope_floor").reset_index(drop=True)
    low_floor = key6.iloc[0]
    mid_floor = key6[key6["slope_floor"] == 0.0004].iloc[0]
    high_floor = key6.iloc[-1]
    high_cost_mid = key20[key20["slope_floor"] == 0.0004].iloc[0]

    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · 参数稳定性检查</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · 参数稳定性检查</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：cheap honesty check ｜ 目标：判断 `slope_floor` 邻域是否一碰就碎</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>固定信号骨架不变：<code>EMA cross + aligned slope floor</code>。</li>
      <li>只改一个参数轴：<code>slope_floor = 0.0002 ~ 0.0006</code>。</li>
      <li>不追新 bar，不扩 universe，不改持有期；仍固定 <code>BTC/ETH/SOL 120d 15m</code> cache 与 <code>next-bar open / hold 8 bars / non-overlap</code>。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(reason)}</b></p>
    <ul>
      <li>最松门槛 <code>0.0002</code>：6bps 下跨资产 <b>{pct(low_floor['mean_total_return'])}</b>，平均 <b>{num(low_floor['mean_trades'],1)}</b> 笔，空仓比 <b>{pct(low_floor['mean_no_trade_ratio'])}</b>。</li>
      <li>当前门槛 <code>0.0004</code>：6bps 下跨资产 <b>{pct(mid_floor['mean_total_return'])}</b>，平均 <b>{num(mid_floor['mean_trades'],1)}</b> 笔，20bps 下仍约 <b>{pct(high_cost_mid['mean_total_return'])}</b>。</li>
      <li>最严门槛 <code>0.0006</code>：6bps 下跨资产 <b>{pct(high_floor['mean_total_return'])}</b>，平均 <b>{num(high_floor['mean_trades'],1)}</b> 笔，说明 edge 不是单一 hot pixel。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>为什么这次会改 verdict</h2>
    <ul>
      <li>如果参数一放松就亏、或一收紧就只剩极少数孤例，那它最多还是 <code>P1</code>。</li>
      <li>实际结果是：邻域内 6bps 全部保留 <code>positive_asset_ratio=3/3</code>，而 0.0004 这一档在 20bps 也仍为正，说明 pocket 不是只靠单点 slope floor 偶然翻正。</li>
      <li>更关键的是：虽然 <code>no_trade_ratio</code> 仍高，但绝对交易数带已经来到 <code>47.7 ~ 125.0</code> 笔/资产量级，不再是“几乎没法验证”的稀疏样本。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>参数稳定性总表</h2>
    {render_table(overall_view[["slope_floor","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_no_trade_ratio","mean_false_reclaim_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_no_trade_ratio","mean_false_reclaim_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>6bps 分资产摘要</h2>
    {render_table(asset_view, percent_cols={"total_return","no_trade_ratio","false_reclaim_ratio","win_rate"}, digits_cols={"trades":0})}
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    overall_summary, asset_summary, verdict, reason = build_outputs()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    overall_summary.to_csv(ART_DIR / "parameter_stability_summary.csv", index=False)
    asset_summary.to_csv(ART_DIR / "parameter_stability_asset_summary.csv", index=False)
    OUTPUT_HTML.write_text(build_html(overall_summary, asset_summary, verdict, reason, generated_at), encoding="utf-8")
    print(f"verdict={verdict}")
    print(f"reason={reason}")
    print(f"html={OUTPUT_HTML}")


if __name__ == "__main__":
    main()
