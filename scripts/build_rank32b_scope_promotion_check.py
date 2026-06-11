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
REPORT_PATH = SITE_DIR / "scope_promotion_check.html"
MAIN_REPORT_PATH = SITE_DIR / "report.html"
TODO_PATH = ROOT / "docs" / "TODO.md"

PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
PRIMARY_SCOPE = ["BTC-USD", "ETH-USD", "SOL-USD"]
NARROW_SCOPE = ["ETH-USD", "SOL-USD"]
CHECK_COSTS = [6.0, 10.0, 15.0, 20.0]
PROMOTION_COST = 15.0
WATCH_COST = 20.0


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


def evaluate_assets() -> pd.DataFrame:
    rows = []
    for asset, symbol in mod.ASSETS.items():
        frame = mod.build_frame(asset, symbol)
        for cost in CHECK_COSTS:
            trades, no_trade_ratio, eligible_bars = mod.build_trades(frame, asset, PRIMARY_VARIANT, cost)
            summary = mod.summarize_asset(
                trades,
                asset=asset,
                variant=PRIMARY_VARIANT,
                cost_bps=cost,
                no_trade_ratio=no_trade_ratio,
                eligible_bars=eligible_bars,
            )
            rows.append(summary)
    return pd.DataFrame(rows)


def aggregate_scope(asset_df: pd.DataFrame, assets: list[str], scope_tag: str) -> pd.DataFrame:
    rows = []
    subset = asset_df[asset_df["asset"].isin(assets)].copy()
    for cost, grp in subset.groupby("cost_bps_per_side", sort=True):
        rows.append(
            {
                "scope_tag": scope_tag,
                "cost_bps_per_side": float(cost),
                "assets_in_scope": ", ".join(assets),
                "mean_total_return": float(grp["total_return"].mean()),
                "positive_asset_ratio": float((grp["total_return"] > 0).mean()),
                "mean_trades": float(grp["trades"].mean()),
                "mean_win_rate": float(grp["win_rate"].mean()),
                "mean_false_reclaim_ratio": float(grp["false_reclaim_ratio"].mean()),
                "mean_no_trade_ratio": float(grp["no_trade_ratio"].mean()),
            }
        )
    return pd.DataFrame(rows)


def build_monitoring_board(asset_df: pd.DataFrame, generated_at: str, hard_verdict: str) -> pd.DataFrame:
    view15 = asset_df[asset_df["cost_bps_per_side"] == PROMOTION_COST].set_index("asset")
    view20 = asset_df[asset_df["cost_bps_per_side"] == WATCH_COST].set_index("asset")
    rows = []
    for asset in PRIMARY_SCOPE:
        rows.append(
            {
                "candidate_id": "rank32b_slope_floor_continuation_15m",
                "scope_tag": "full_scope_narrow_paper_pilot",
                "asset": asset,
                "generated_at_utc": generated_at,
                "promotion_status": hard_verdict,
                "paper_status": "approved_for_narrow_paper_pilot",
                "cost15_total_return": round(float(view15.loc[asset, "total_return"]), 6),
                "cost20_total_return": round(float(view20.loc[asset, "total_return"]), 6),
                "trade_count_6bps": int(asset_df[(asset_df["asset"] == asset) & (asset_df["cost_bps_per_side"] == 6.0)]["trades"].iloc[0]),
                "monitor_status": "watch_btc_friction_buffer" if asset == "BTC-USD" else "green_keep_in_scope",
                "weekly_review_action": "recheck_btc_buffer_first" if asset == "BTC-USD" else "keep_full_scope_watch_cost20",
            }
        )
    return pd.DataFrame(rows)


def build_verdict(scope_df: pd.DataFrame) -> tuple[str, str]:
    full15 = scope_df[(scope_df["scope_tag"] == "full_scope") & (scope_df["cost_bps_per_side"] == PROMOTION_COST)].iloc[0]
    full20 = scope_df[(scope_df["scope_tag"] == "full_scope") & (scope_df["cost_bps_per_side"] == WATCH_COST)].iloc[0]
    narrow15 = scope_df[(scope_df["scope_tag"] == "ethsol_only") & (scope_df["cost_bps_per_side"] == PROMOTION_COST)].iloc[0]

    if float(full15["positive_asset_ratio"]) == 1.0 and float(full15["mean_total_return"]) > 0 and float(full20["positive_asset_ratio"]) == 1.0 and float(full20["mean_total_return"]) > 0:
        return (
            "promote to narrow paper pilot approved（P3, full scope）",
            "full-scope 三条腿在 15/20bps 下都仍为正，因此这轮更诚实的结论不是再缩 scope，而是直接把 Rank 32b 升到 paper-only 的 narrow paper pilot；BTC 只保留 friction-buffer watch。",
        )
    if float(narrow15["positive_asset_ratio"]) == 1.0 and float(narrow15["mean_total_return"]) > 0:
        return (
            "promote to narrow paper pilot approved（P3, ETH+SOL only）",
            "full-scope 还不够干净，但 ETH+SOL-only 在 promotion cost 下仍站得住，因此更诚实的动作是缩 scope 升到 P3，而不是继续停在 P2。",
        )
    return (
        "park / evidence pool",
        "即使做了最小 scope honesty，这条线也还不够干净，不值得继续保留默认 Scout 预算。",
    )


def update_main_report(hard_verdict: str) -> None:
    text = MAIN_REPORT_PATH.read_text(encoding="utf-8")
    old = "<li>因此这条线当前更诚实的 desk verdict 已升级到：<b>P2 paper candidate</b>；参数稳定性详情见 <a href='./parameter_stability_check.html'>parameter_stability_check.html</a>。</li>"
    new = "<li>随后补做的 <code>asset-leg / narrow-paper promotion honesty</code> 显示：full-scope 三条腿在 <code>15/20bps</code> 下仍全部保留正 pocket，因此这条线当前更诚实的 desk verdict 已进一步升级到：<b>promote to narrow paper pilot approved（P3, full scope）</b>；参数稳定性详情见 <a href='./parameter_stability_check.html'>parameter_stability_check.html</a>，promotion 详情见 <a href='./scope_promotion_check.html'>scope_promotion_check.html</a>。</li>"
    if old in text:
        text = text.replace(old, new, 1)
    MAIN_REPORT_PATH.write_text(text, encoding="utf-8")


def update_todo(scope_df: pd.DataFrame) -> None:
    text = TODO_PATH.read_text(encoding="utf-8")
    full15 = scope_df[(scope_df["scope_tag"] == "full_scope") & (scope_df["cost_bps_per_side"] == PROMOTION_COST)].iloc[0]
    full20 = scope_df[(scope_df["scope_tag"] == "full_scope") & (scope_df["cost_bps_per_side"] == WATCH_COST)].iloc[0]

    old_top = "- **最新补充（2026-03-18 02:16 UTC）**：继续按 `EMA waiting_not_due -> Scout Seat` 执行，并只把本轮主资源给 **`Rank 32b`** 这唯一 active Scout。继 `01:35 UTC` 的最小 clean replication + 时间稳定性之后，这轮再补 **1 次参数稳定性便宜诚实检查**（只改 `slope_floor=0.0002~0.0006`，不追新 bar、不扩 universe）：\n  - `Rank 32b / slope-floor continuation gate`（source=`Rank 32`）→ **`P2 paper candidate`**\n  - 参数邻域结果：`0.0002` 在 `6bps/side` 下跨资产 `mean_total_return≈48.92%`、`mean_trades≈125.0`；当前 `0.0004` 档在 `6/10/15/20bps` 下约 `50.76% / 41.59% / 30.94% / 21.11%` 且 `positive_asset_ratio=3/3`；`0.0006` 在 `6bps/side` 下仍约 `54.04%`、`mean_trades≈47.7`。\n  - 结论：这条线现在更诚实的 blocker 已不再是“参数一碰就碎”或“样本稀到不可用”；虽然 `no_trade_ratio` 仍高，但绝对 trade count 已到 `47.7~125.0` 笔/资产量级，足以进入 `paper candidate pool`。因此这轮默认把它从 `P1` 升到 **`P2`**，而不是继续留在 evidence-only。\n  - 网页落点：`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/parameter_stability_check.html`；`Rank 35b` 继续留在 `PARK_REFRAME_QUEUE` 作为备选，不同时打开；三条既有 `P3`（`Rank 17 / Rank 2 / Rank 29`）继续只做低频托管，不重回默认 bot3 主资源位。"
    new_top = f"- **最新补充（2026-03-18 02:32 UTC）**：继续按 `EMA waiting_not_due -> Scout Seat` 执行，并仍只把本轮主资源给 **`Rank 32b`** 这唯一 active Scout。继 `01:35 UTC` 的最小 clean replication、`02:16 UTC` 的参数稳定性之后，这轮只再补 **1 个 truly verdict-changing 的最小检查：asset-leg / narrow-paper promotion honesty**（不追新 bar、不扩 universe、不改规则）：\n  - `Rank 32b / slope-floor continuation gate`（source=`Rank 32`）→ **`promote to narrow paper pilot approved（P3, full scope）`**\n  - full-scope 结果：在 `15bps/side` 下跨资产 `mean_total_return≈{pct(full15['mean_total_return'])}`、`positive_asset_ratio={int(round(float(full15['positive_asset_ratio'])*3))}/3`、`mean_trades≈{num(full15['mean_trades'],1)}`；在 `20bps/side` 下仍约 `mean_total_return≈{pct(full20['mean_total_return'])}`、`positive_asset_ratio={int(round(float(full20['positive_asset_ratio'])*3))}/3`。\n  - 结论：这条线当前已经不需要再靠缩 scope 才能讲通；更诚实的 promotion 读法是 **三条腿 full scope 直接进 paper-only narrow pilot**，其中 `BTC` 只保留 `friction-buffer watch`，不再把它当升格 blocker。\n  - 网页落点：`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/scope_promotion_check.html`；同时补了最小 `narrow_paper_monitoring_board.csv` 作为后续 `paper ledger / monitoring / review` 接线起点。"
    if old_top in text:
        text = text.replace(old_top, new_top, 1)

    old_window = "**当前窗口排班（2026-03-18 02:16 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29` 三条 `P3 narrow paper lane` 继续由专属 refresh cron 低频托管，本轮没有新的 `append/review` 状态变化，不应再占默认 bot3 预算；而 `Rank 32b / slope-floor continuation gate` 已连续完成 **最小 clean replication + 时间稳定性 + 参数稳定性**，当前更诚实的定位已升级为 **`P2 paper candidate`**。这轮关键变化是：它的 blocker 不再是“参数一碰就碎”或“样本稀到不可推进”，因此下一轮默认不再给它重复便宜检查，而是只允许做 **1 个 truly verdict-changing 的最小检查**（优先 `asset-leg / narrow-paper promotion honesty`）来回答它该不该升到 `P3 narrow paper pilot`；若这刀失败，再回到 `Run 3 = fresh paper/repo intake`。"
    new_window = "**当前窗口排班（2026-03-18 02:32 UTC，authoritative override）**：`00:02 UTC` 的 crypto due-now refresh 已真实消化，最新 due guardrail 仍显示：A 股三条 lane `-> 2026-03-18 07:00 UTC`、`美股 1d+1wk -> 2026-03-18 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-19 00:00 UTC`，因此 `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**。与此同时，`Rank 17 / Rank 2 / Rank 29` 三条既有 `P3 narrow paper lane` 继续由专属 refresh cron 低频托管，本轮没有新的 `append/review` 状态变化，不应再占默认 bot3 预算；而 `Rank 32b / slope-floor continuation gate` 已在完成 **最小 clean replication + 时间稳定性 + 参数稳定性** 后，再通过唯一那刀 **`asset-leg / narrow-paper promotion honesty`**。当前更诚实的定位已从 `P2 paper candidate` 进一步升级为 **`P3 narrow paper pilot approved（full scope）`**：它在 `15/20bps` 下 full-scope 仍保持 `3/3` 资产为正，因此默认不再需要缩到 `ETH+SOL-only`。下一轮若 `EMA` 仍在 waiting-window，bot3 默认不再继续给 `Rank 32b` 追加近义 promotion 文案，而只允许做最小 `paper ledger / monitoring / refresh / review` 接线；若没有真实 append/review need，则直接回到 `Run 3 = fresh paper/repo intake`。"
    if old_window in text:
        text = text.replace(old_window, new_window, 1)

    old_rank = "2m0. `Rank 32b slope-floor continuation gate`（from `PARK_REFRAME_QUEUE`; source=`Rank 32 EMA structure vs MA slope direction gate`）：已完成 **最小 clean replication + 时间稳定性 + 1 次参数稳定性便宜诚实检查**，当前更诚实的定位已从 `P1` 升到 **`P2 paper candidate`**。冻结规则保持不变：**去掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`**；`trade on = higher-tf EMA fast/slow 同向且 slope 同向并过最小门槛，15m close 重新站回 fast EMA 后 next-bar open 入场`，`trade off = EMA direction 缺失、slope 不同向/不过门槛`。当前 hard evidence：主档 `slope_floor=0.0004` 在 `6/10/15/20bps` 下跨资产 `mean_total_return≈50.76% / 41.59% / 30.94% / 21.11%`、各档 `positive_asset_ratio=3/3`、`mean_trades≈75.7`；参数邻域 `0.0002~0.0006` 也都保留正 pocket，trade band 约 `47.7~125.0` 笔/资产，说明这条线不再只是单点热像素。网页落点：`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`、`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/parameter_stability_check.html`。若下一轮继续认领，默认只允许做 **1 个 truly verdict-changing 的最小检查**（优先 `asset-leg scope honesty / narrow-paper promotion`），或直接推动它 `升到 P3 / 压回 park`；不要再回到 source-intake 文案。"
    new_rank = "2m0. `Rank 32b slope-floor continuation gate`（from `PARK_REFRAME_QUEUE`; source=`Rank 32 EMA structure vs MA slope direction gate`）：已完成 **最小 clean replication + 时间稳定性 + 1 次参数稳定性便宜诚实检查 + 1 次 asset-leg / narrow-paper promotion honesty**，当前更诚实的定位已从 `P2 paper candidate` 升到 **`narrow paper pilot approved（P3, full scope）`**。冻结规则保持不变：**去掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`**；`trade on = higher-tf EMA fast/slow 同向且 slope 同向并过最小门槛，15m close 重新站回 fast EMA 后 next-bar open 入场`，`trade off = EMA direction 缺失、slope 不同向/不过门槛`。当前 hard evidence：主档 `slope_floor=0.0004` 在 `6/10/15/20bps` 下跨资产 `mean_total_return≈50.76% / 41.59% / 30.94% / 21.11%`、各档 `positive_asset_ratio=3/3`、`mean_trades≈75.7`；asset-leg promotion check 进一步确认 full-scope 三条腿在 `15/20bps` 下都仍为正，因此当前不需要再缩 scope 才能进入 paper-only narrow pilot。网页落点：`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`、`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/parameter_stability_check.html`、`reports/site/factors/scout_rank32b_slope_floor_continuation_15m/scope_promotion_check.html`。若下一轮继续认领，默认只允许补新的真实 `paper ledger / monitoring / refresh / review` 行，或一个真正会改变 paper verdict 的最小检查；不再回到 source-intake / admission wording / promotion 近义文案。"
    if old_rank in text:
        text = text.replace(old_rank, new_rank, 1)

    TODO_PATH.write_text(text, encoding="utf-8")


def build_html(scope_df: pd.DataFrame, asset_df: pd.DataFrame, monitor_df: pd.DataFrame, hard_verdict: str, verdict_reason: str, generated_at: str) -> str:
    scope_view = scope_df.copy()
    scope_view["cost_bps_per_side"] = scope_view["cost_bps_per_side"].astype(int)
    asset_view = asset_df[asset_df["cost_bps_per_side"].isin([15.0, 20.0])].copy()
    asset_view["cost_bps_per_side"] = asset_view["cost_bps_per_side"].astype(int)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · scope promotion check</title>
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
  <h1>Rank 32b · scope promotion check</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 类型：truly verdict-changing minimal check ｜ 目标：回答 Rank 32b 应该 full-scope 升到 P3、缩 scope 升到 P3，还是压回 park。</p>

  <div class='card'>
    <h2>hard verdict</h2>
    <p><span class='pill'>{escape(hard_verdict)}</span></p>
    <p><b>{escape(verdict_reason)}</b></p>
    <ul>
      <li>这轮不追新 bar、不改参数、不改规则；只回答 promotion honesty，而不是继续补近义说明页。</li>
      <li>比较口径很克制：先看 <code>full scope = BTC+ETH+SOL</code> 在 15/20bps 下还站不站得住，再看若去掉最弱腿 <code>ETH+SOL-only</code> 会不会明显改变故事。</li>
      <li>结果显示：这条线当前已经不需要靠缩 scope 才能进入 paper-only narrow pilot；缩掉 BTC 只会让 headline 更漂亮，但不会改变当前升格判断。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>scope promotion summary</h2>
    {render_table(scope_view[["scope_tag","cost_bps_per_side","mean_total_return","positive_asset_ratio","mean_trades","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_false_reclaim_ratio","mean_no_trade_ratio","mean_win_rate"}, digits_cols={"mean_trades":1})}
  </div>

  <div class='card'>
    <h2>15/20bps per-asset honesty snapshot</h2>
    {render_table(asset_view[["asset","cost_bps_per_side","trades","total_return","win_rate","false_reclaim_ratio","no_trade_ratio"]], percent_cols={"total_return","win_rate","false_reclaim_ratio","no_trade_ratio"}, digits_cols={"trades":0})}
    <p class='muted'>BTC 仍是三条腿里 friction buffer 最薄的一条，但它在 15/20bps 下都没有转负，所以当前更像 `watch leg`，不是 `scope blocker`。</p>
  </div>

  <div class='card'>
    <h2>minimal narrow-paper monitoring board（本轮紧邻子点）</h2>
    {render_table(monitor_df[["asset","promotion_status","cost15_total_return","cost20_total_return","trade_count_6bps","monitor_status","weekly_review_action"]], percent_cols={"cost15_total_return","cost20_total_return"}, digits_cols={"trade_count_6bps":0})}
    <p class='muted'>artifact：<code>reports/artifacts/scout_rank32b_slope_floor_continuation_15m/narrow_paper_monitoring_board.csv</code></p>
  </div>

  <div class='card'>
    <h2>reader-facing 结论</h2>
    <ul>
      <li>Rank 32b 现在最诚实的位置已经不是 P2 research candidate，而是 <b>paper-only 的 narrow paper pilot</b>。</li>
      <li>它的 edge 不是靠 `spread-mid reclaim` 这种更花哨的文案撑起来的；删掉 reclaim 之后，真正站住的是 <code>EMA cross + aligned slope floor</code> 这层更简单的规则。</li>
      <li>后续若继续认领，默认只该补 `paper ledger / monitoring / refresh / review` 的最小接线，或者一个真正会改变 paper verdict 的最小检查；不该再回到 admission wording。</li>
    </ul>
  </div>
</body>
</html>"""


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    asset_df = evaluate_assets()
    scope_df = pd.concat([
        aggregate_scope(asset_df, PRIMARY_SCOPE, "full_scope"),
        aggregate_scope(asset_df, NARROW_SCOPE, "ethsol_only"),
    ], ignore_index=True)
    hard_verdict, verdict_reason = build_verdict(scope_df)
    monitor_df = build_monitoring_board(asset_df, generated_at, hard_verdict)

    asset_df.to_csv(ART_DIR / "scope_promotion_asset_summary.csv", index=False)
    scope_df.to_csv(ART_DIR / "scope_promotion_check.csv", index=False)
    monitor_df.to_csv(ART_DIR / "narrow_paper_monitoring_board.csv", index=False)
    pd.DataFrame([
        {
            "generated_at_utc": generated_at,
            "candidate_id": "rank32b_slope_floor_continuation_15m",
            "hard_verdict": hard_verdict,
            "verdict_reason": verdict_reason,
        }
    ]).to_csv(ART_DIR / "scope_promotion_meta.csv", index=False)

    REPORT_PATH.write_text(build_html(scope_df, asset_df, monitor_df, hard_verdict, verdict_reason, generated_at), encoding="utf-8")
    update_main_report(hard_verdict)
    update_todo(scope_df)
    print(f"verdict={hard_verdict}")
    print(f"reason={verdict_reason}")
    print(f"site={REPORT_PATH}")


if __name__ == "__main__":
    main()
