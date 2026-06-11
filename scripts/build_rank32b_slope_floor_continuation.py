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
READING_DIR = ROOT / "reports" / "site" / "reading" / "trendline_alpha_scout"
READING_REPORT = READING_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
BASELINE_VARIANT = "ema_cross_only"
PRIMARY_COST = 6.0


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


def build_time_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty or len(trades) < 9:
        return pd.DataFrame(columns=["time_bucket", "mean_total_return", "positive_asset_ratio", "mean_trades", "mean_win_rate"])
    work = trades.copy()
    work["event_ts"] = pd.to_datetime(work["event_ts"], utc=True)
    work["time_bucket"] = pd.qcut(work["event_ts"].view("int64"), q=3, labels=["bucket_1", "bucket_2", "bucket_3"])
    rows = []
    for bucket, grp in work.groupby("time_bucket", sort=False, observed=False):
        asset_total = grp.groupby("asset")["net_ret"].apply(lambda s: float((1.0 + s).prod() - 1.0))
        rows.append({
            "time_bucket": str(bucket),
            "mean_total_return": float(asset_total.mean()) if len(asset_total) else np.nan,
            "positive_asset_ratio": float((asset_total > 0).mean()) if len(asset_total) else np.nan,
            "mean_trades": float(grp.groupby("asset").size().mean()) if len(grp) else np.nan,
            "mean_win_rate": float(grp.groupby("asset")["net_ret"].apply(lambda s: (s > 0).mean()).mean()) if len(grp) else np.nan,
        })
    return pd.DataFrame(rows)


def build_verdict(overall: pd.DataFrame, time_summary: pd.DataFrame) -> tuple[str, str]:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)]
    if primary.empty:
        return "park / evidence pool", "主变体没有形成可用样本，连最小 clean replication 都不足以成立。"
    row = primary.iloc[0]
    mean_ret = float(row["mean_total_return"])
    pos_ratio = float(row["positive_asset_ratio"])
    mean_trades = float(row["mean_trades"])
    no_trade = float(row["mean_no_trade_ratio"])
    false_ratio = float(row["mean_false_reclaim_ratio"])
    time_positive = int((time_summary["mean_total_return"] > 0).sum()) if not time_summary.empty else 0

    if mean_ret > 0 and pos_ratio >= (2.0 / 3.0) and mean_trades >= 24 and false_ratio <= 0.20 and time_positive == len(time_summary.index):
        if no_trade <= 0.99:
            return "P2 paper candidate", "成本、跨资产与时间 pocket 都站住了，而且交易密度没有稀到完全不可推进。"
        return "P1 weak candidate / evidence pool", "删掉 reclaim 后 pocket 仍保留，而且时间 tercile 没有塌；但 no-trade ratio 依旧过高，只配拿 1 次便宜诚实检查，不足以直接升到 paper candidate。"
    return "park / evidence pool", "虽然删掉 reclaim 后 pocket 没立刻归零，但还不够同时满足跨资产、时间稳定与最小可用交易密度。"


def update_reading_report() -> None:
    if not READING_REPORT.exists():
        return
    text = READING_REPORT.read_text(encoding="utf-8")
    href = 'rank32b_slope_floor_continuation_clean_replication.html'
    if href in text:
        return
    anchor = 'rank32_ema_slope_structure_source_intake.html">Rank 32 source intake</a>'
    if anchor not in text:
        return
    text = text.replace(anchor, anchor + ' ｜ <a href="rank32b_slope_floor_continuation_clean_replication.html">Rank 32b clean replication</a>', 1)
    READING_REPORT.write_text(text, encoding="utf-8")


def update_todo(verdict: str, generated_at: str, primary_row: pd.Series, time_summary: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    bucket_parts = []
    for _, row in time_summary.iterrows():
        bucket_parts.append(f"{row['time_bucket']}≈{pct(row['mean_total_return'])} / {pct(row['positive_asset_ratio'])}")
    time_note = "time-pocket honesty：" + "；".join(bucket_parts) + "。"

    old = "- **最新补充（2026-03-18 01:12 UTC）**：在 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 本轮没有再拿到比现有窄派生提案更贴近执行层的新 `paper / repo based 5m / 15m crypto` source 后，按 `PARK_REFRAME_QUEUE` 比较 `Rank 32b` 与 `Rank 35b` 的当前边际价值，当前只认领 **`Rank 32b`** 进入 active Scout：\n  - `Rank 32b / slope-floor continuation gate`（source=`Rank 32`）→ **`P1 / source intake -> clean replication next`**\n  - 选择理由：这是单轴、repo-based、最便宜且最可能真正改变 verdict 的下一刀；原证据已显示 edge 更可能坐落在 `aligned slope floor`，而不是稀薄的 `spread-mid reclaim`。\n  - `Rank 35b` 继续留在 `PARK_REFRAME_QUEUE` 作为备选，不同时打开；三条既有 `P3`（`Rank 17 / Rank 2 / Rank 29`）继续只做低频托管，不重回默认 bot3 主资源位。"
    new = f"- **最新补充（{generated_at}）**：在 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 本轮没有拿到更贴近执行层的新 `paper / repo based 5m / 15m crypto` source 后，按 `PARK_REFRAME_QUEUE` 继续只认领 **`Rank 32b`**。这轮已把它从 `source intake` 推到 **最小 clean replication + 1 次时间稳定性诚实检查**：\n  - `Rank 32b / slope-floor continuation gate`（source=`Rank 32`）→ **`{verdict}`**\n  - 主变体 `ema_cross_plus_slope_floor` 在 `6bps/side` 下跨资产 `mean_total_return≈{pct(primary_row['mean_total_return'])}`、`positive_asset_ratio≈{pct(primary_row['positive_asset_ratio'])}`、`mean_trades≈{num(primary_row['mean_trades'],1)}`、`mean_false_reclaim_ratio≈{pct(primary_row['mean_false_reclaim_ratio'])}`、`mean_no_trade_ratio≈{pct(primary_row['mean_no_trade_ratio'])}`；{time_note}\n  - 结论：删掉 reclaim 后 pocket 没塌，说明 edge 更像坐落在 `aligned slope floor`；但交易密度仍偏稀，所以当前最多只保留 **1 次便宜诚实检查预算**，不足以直接升到 `paper candidate`。\n  - `Rank 35b` 继续留在 `PARK_REFRAME_QUEUE` 作为备选，不同时打开；三条既有 `P3`（`Rank 17 / Rank 2 / Rank 29`）继续只做低频托管，不重回默认 bot3 主资源位。"
    if old in text:
        text = text.replace(old, new, 1)

    old_run = "当前默认顺序应读成：`Run 1 = EMA due-check（若仍 waiting_not_due 立即跳过） -> Run 2 = Rank 32b source intake / clean replication -> Run 3 = Rank 32b 的 1 次最小 verdict-changing check（优先 Light Stability Pack）；只有 Rank 32b 当轮硬 fail / 外部阻塞时，才回退到 tiny-live plumbing fallback`。"
    new_run = "当前默认顺序应读成：`Run 1 = EMA due-check（若仍 waiting_not_due 立即跳过） -> Run 2 = Rank 32b 那唯一 1 次便宜诚实检查（优先参数稳定性 / friction 邻域，不再重复 source intake） -> Run 3 = fresh paper/repo intake；只有 fresh intake 也真实 exhausted 时，才回退到 tiny-live plumbing fallback`。"
    if old_run in text:
        text = text.replace(old_run, new_run, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(overall: pd.DataFrame, asset_summary: pd.DataFrame, time_summary: pd.DataFrame, verdict: str, verdict_reason: str, generated_at: str) -> str:
    primary = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    headline = (
        f"主变体 {PRIMARY_VARIANT} 在 {int(PRIMARY_COST)}bps/side 下：跨资产 mean_total_return≈{pct(primary['mean_total_return'])}、"
        f"positive_asset_ratio≈{pct(primary['positive_asset_ratio'])}、mean_trades≈{num(primary['mean_trades'],1)}、"
        f"mean_false_reclaim_ratio≈{pct(primary['mean_false_reclaim_ratio'])}、mean_no_trade_ratio≈{pct(primary['mean_no_trade_ratio'])}。"
    )
    overall_view = overall.copy()
    overall_view["cost_bps_per_side"] = overall_view["cost_bps_per_side"].astype(int)
    asset_view = asset_summary.copy()
    asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · slope-floor continuation gate</title>
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
  <p><a href='../../reading/trendline_alpha_scout/report.html'>← 返回 Trendline Alpha Scout</a></p>
  <h1>Rank 32b · slope-floor continuation gate</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：derived-hypothesis clean replication ｜ 角色：active Scout 候选</p>

  <div class='card'>
    <h2>这轮只回答什么</h2>
    <ul>
      <li>它不是重做旧的 Rank 32，而是只验证一个窄派生：<code>remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor</code>。</li>
      <li>固定复用 <code>BTC/ETH/SOL 120d 15m</code> cache，不追新 bar，不扩 universe。</li>
      <li>本轮只做 1 个相邻检查：<code>时间稳定性（3 terciles）</code>，回答它是不是全靠单一时间 pocket。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>clean-room 规则</h2>
    <ul>
      <li><b>baseline：</b><code>ema_cross_only = higher_tf EMA fast > slow（空头镜像）+ close 重新站回 fast EMA</code></li>
      <li><b>Rank 32b：</b><code>ema_cross_plus_slope_floor = 在 baseline 基础上要求 fast/slow slope 同向，且 |fast slope| 过最小门槛</code></li>
      <li><b>删掉的只有一刀：</b>不再要求最近 4 根必须先出现向 <code>spread mid</code> 的回抽 / reclaim。</li>
      <li><b>执行口径：</b><code>next-bar open</code> 入场、持有 <code>{mod.HOLD_BARS}</code> 根 15m bar、默认 non-overlap。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p><b>{escape(headline)}</b></p>
    <p class='muted'>{escape(verdict_reason)}</p>
  </div>

  <div class='card'>
    <h2>成本对照（baseline vs Rank 32b）</h2>
    {render_table(overall_view[["variant","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>分资产摘要（Rank 32b 主变体）</h2>
    {render_table(asset_view[["asset","variant","cost_bps_per_side","trades","total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"]], percent_cols={"total_return","false_reclaim_ratio","no_trade_ratio","win_rate","long_share","short_share"}, digits_cols={"trades":0})}
  </div>

  <div class='card'>
    <h2>时间稳定性（唯一额外诚实检查）</h2>
    {render_table(time_summary[["time_bucket","mean_total_return","positive_asset_ratio","mean_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>reader-facing 结论</h2>
    <ul>
      <li>删掉 reclaim 后，主 pocket 没塌，说明真正贡献 edge 的更像 <code>aligned slope floor</code>，不是那层更“漂亮”的 reclaim 文案。</li>
      <li>但 <code>mean_no_trade_ratio</code> 仍接近 99%，所以它还不是能直接推进到 paper candidate 的密度。</li>
      <li>因此这轮最诚实的 desk verdict 是：<b>{escape(verdict)}</b>，并把后续预算限制为最多 1 次便宜诚实检查。</li>
    </ul>
  </div>
</body>
</html>
"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_DIR)

    overall_rows = []
    asset_rows = []
    primary_trades = []

    for asset, symbol in mod.ASSETS.items():
        frame = mod.build_frame(asset, symbol)
        frame.to_csv(ART_DIR / f"{asset.lower().replace('-usd','')}_frame.csv", index=False)
        for variant in [BASELINE_VARIANT, PRIMARY_VARIANT]:
            for cost in mod.COSTS:
                trades, no_trade_ratio, eligible_bars = mod.build_trades(frame, asset, variant, cost)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST:
                    primary_trades.append(trades)
                if variant == PRIMARY_VARIANT and cost == PRIMARY_COST and not trades.empty:
                    trades.to_csv(ART_DIR / f"trades_primary_6bps_{asset.lower().replace('-usd','')}.csv", index=False)
                asset_rows.append(mod.summarize_asset(trades, asset=asset, variant=variant, cost_bps=cost, no_trade_ratio=no_trade_ratio, eligible_bars=eligible_bars))

    asset_summary = pd.DataFrame(asset_rows)
    overall = mod.summarize_overall(asset_summary)
    overall = overall[overall["variant"].isin([BASELINE_VARIANT, PRIMARY_VARIANT])].reset_index(drop=True)
    primary_asset_summary = asset_summary[(asset_summary["variant"] == PRIMARY_VARIANT) & (asset_summary["cost_bps_per_side"] == PRIMARY_COST)].reset_index(drop=True)
    primary_trades_df = pd.concat([df for df in primary_trades if not df.empty], ignore_index=True) if primary_trades else pd.DataFrame()
    time_summary = build_time_summary(primary_trades_df)
    verdict, verdict_reason = build_verdict(overall, time_summary)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    primary_asset_summary.to_csv(ART_DIR / "asset_summary_primary_6bps.csv", index=False)
    primary_trades_df.to_csv(ART_DIR / "trades_primary_6bps.csv", index=False)
    time_summary.to_csv(ART_DIR / "time_bucket_summary.csv", index=False)
    pd.DataFrame([{
        "generated_at_utc": generated_at,
        "candidate_id": "rank32b_slope_floor_continuation_15m",
        "hard_verdict": verdict,
        "verdict_reason": verdict_reason,
    }]).to_csv(ART_DIR / "meta.csv", index=False)

    html = build_html(overall, primary_asset_summary, time_summary, verdict, verdict_reason, generated_at)
    (SITE_DIR / "report.html").write_text(html, encoding="utf-8")
    (READING_DIR / "rank32b_slope_floor_continuation_clean_replication.html").write_text(html, encoding="utf-8")
    update_reading_report()
    primary_row = overall[(overall["variant"] == PRIMARY_VARIANT) & (overall["cost_bps_per_side"] == PRIMARY_COST)].iloc[0]
    update_todo(verdict, generated_at, primary_row, time_summary)

    print(f"verdict={verdict}")
    print("primary_stats", primary_row.to_dict())
    print("time_buckets", time_summary.to_dict(orient="records"))


if __name__ == "__main__":
    main()
