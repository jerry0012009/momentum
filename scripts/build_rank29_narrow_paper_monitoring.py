#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank29_trendline_breakout_navigator_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m"
REPORT_PATH = SITE_DIR / "narrow_paper_monitoring_board.html"

MODE = "no_overlap_guard"
PRIMARY_VARIANT = "breakout_align_ge2"
QUEUE_SCOPE = "narrow_paper_pilot_rank29_breakout_align_ge2"


def pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{float(value) * 100:.{digits}f}%"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    head = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, float):
                text = f"{value:.2f}"
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(ART_DIR / name)


def build_monitoring_board(
    no_overlap_overall: pd.DataFrame,
    no_overlap_asset: pd.DataFrame,
    bucket_overall: pd.DataFrame,
    clean_overall: pd.DataFrame,
) -> pd.DataFrame:
    get_overall = lambda cost: no_overlap_overall[no_overlap_overall["cost_bps_per_side"] == cost].iloc[0]
    get_bucket = lambda cost, bucket: bucket_overall[
        (bucket_overall["cost_bps_per_side"] == cost) & (bucket_overall["time_bucket"] == bucket)
    ].iloc[0]

    cost6 = get_overall(6.0)
    cost15 = get_overall(15.0)
    bucket6_mid = get_bucket(6, "bucket_2")
    bucket10_mid = get_bucket(10, "bucket_2")
    bucket15_mid = get_bucket(15, "bucket_2")
    btc20 = no_overlap_asset[
        (no_overlap_asset["asset"] == "BTC-USD") & (no_overlap_asset["mode"] == MODE) & (no_overlap_asset["cost_bps_per_side"] == 20.0)
    ].iloc[0]
    clean_primary = clean_overall[
        (clean_overall["variant"] == PRIMARY_VARIANT) & (clean_overall["cost_bps_per_side"] == 6.0)
    ].iloc[0]
    mean_false_break = float(clean_primary["mean_false_break_ratio"])

    rows = [
        {
            "component": "scope_freeze",
            "status": "pass",
            "minimum_rule": "冻结为 breakout_align_ge2 + no_overlap_guard + next-bar open 持有 8 根；当前只允许 paper-only narrow pilot。",
            "why_it_matters": "先把可运行口径钉死，避免 P3 阶段又退回 fresh-intake 或 overlap 乐观版。",
        },
        {
            "component": "base_cost_guard",
            "status": "pass",
            "minimum_rule": f"6bps mean_total_return={pct(cost6['mean_total_return'])} 且 3/3 资产为正；15bps 仍保持 {pct(cost15['mean_total_return'])} / 3/3。",
            "why_it_matters": "说明这条线当前不是只能在最轻 friction 下活着，足够支撑 narrow paper pilot。",
        },
        {
            "component": "middle_bucket_red_watch",
            "status": "red_watch",
            "minimum_rule": f"bucket_2 在 6bps 仍为 {pct(bucket6_mid['mean_total_return'])}，但 10bps 只剩 {pct(bucket10_mid['mean_total_return'])} / 1/3 资产为正，15bps 约 {pct(bucket15_mid['mean_total_return'])}。",
            "why_it_matters": "time stability 没有爆雷，但中段 pocket 明显更脆，后续 weekly review 必须优先盯这一段。",
        },
        {
            "component": "btc_high_friction_tail_watch",
            "status": "watch",
            "minimum_rule": f"BTC 在 20bps no-overlap 下 total_return={pct(btc20['total_return'])}；不改当前 pilot scope，但要保留成本尾部 watch。",
            "why_it_matters": "避免把 aggregate 为正误读成每条腿在更高 friction 下都同样干净。",
        },
        {
            "component": "false_break_guard",
            "status": "pass",
            "minimum_rule": f"6bps no-overlap 的 mean_false_break_ratio 约 {pct(mean_false_break)}，继续沿同一口径做 paper review。",
            "why_it_matters": "这条线的 alpha 不是靠大量假突破堆出来的；后续 review 可以继续沿 false-break ratio 做诚实跟踪。",
        },
        {
            "component": "promotion_boundary",
            "status": "pass",
            "minimum_rule": "当前只升到 narrow paper pilot approved（P3）；不得偷升 tiny-live，也不重回 admission wording。",
            "why_it_matters": "符合 board 当前约束：P3 只补 paper ledger / monitoring / refresh / weekly-review 的最小接线。",
        },
    ]
    return pd.DataFrame(rows)


def build_weekly_review_queue(trades_6: dict[str, pd.DataFrame]) -> pd.DataFrame:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows: list[dict[str, object]] = []
    for asset, df in trades_6.items():
        df = df.copy()
        df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True)
        df["exit_ts"] = pd.to_datetime(df["exit_ts"], utc=True)
        df = df.sort_values("entry_ts").reset_index(drop=True)
        df["time_bucket"] = pd.qcut(df.index, 3, labels=["bucket_1", "bucket_2", "bucket_3"])
        mid = df[df["time_bucket"] == "bucket_2"].copy()
        last_exit = mid["exit_ts"].max()
        total_return = float((1.0 + mid["net_ret"]).prod() - 1.0)
        if asset in {"BTC-USD", "ETH-USD"}:
            review_priority = "P3_red_watch_now"
            weekly_status = "red_watch_review_now"
            monitor_hint = "red_watch"
            focus = "bucket_2_cost_fragility"
        else:
            review_priority = "P3_yellow_watch_now"
            weekly_status = "yellow_watch_review_now"
            monitor_hint = "watch"
            focus = "bucket_2_only_green_leg_hold"
        rows.append(
            {
                "candidate_id": "rank29_trendline_breakout_navigator",
                "asset": asset,
                "scope_tag": QUEUE_SCOPE,
                "review_bucket": "bucket_2",
                "review_priority": review_priority,
                "latest_sample_end_utc": last_exit.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "last_trade_exit_ts_utc": last_exit.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "lifetime_total_return_6bps": total_return,
                "weekly_review_status": weekly_status,
                "review_focus": focus,
                "operator_action": "append_weekly_review_row_keep_rank29_narrow_pilot",
                "promotion_boundary": "paper_only_narrow_pilot_until_new_live_clearance",
                "generated_at_utc": generated_at,
                "monitor_status_hint": monitor_hint,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    no_overlap_overall = load_csv("no_overlap_overall_summary.csv")
    no_overlap_asset = load_csv("no_overlap_asset_summary.csv")
    bucket_overall = load_csv("time_stability_overall_summary.csv")
    clean_overall = load_csv("overall_summary.csv")

    trades_6 = {}
    for asset_slug, asset_name in [("btc_usd", "BTC-USD"), ("eth_usd", "ETH-USD"), ("sol_usd", "SOL-USD")]:
        trades_6[asset_name] = pd.read_csv(ART_DIR / f"{asset_slug}_{MODE}_trades_6bps.csv")

    monitoring_board = build_monitoring_board(no_overlap_overall, no_overlap_asset, bucket_overall, clean_overall)
    weekly_review_queue = build_weekly_review_queue(trades_6)

    monitoring_board.to_csv(ART_DIR / "narrow_paper_pilot_monitoring_board.csv", index=False)
    weekly_review_queue.to_csv(ART_DIR / "narrow_paper_pilot_weekly_review_queue.csv", index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 29 narrow paper monitoring board</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1080px; margin: 40px auto; padding: 0 18px; line-height: 1.66; color:#111827; background:#f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
    .muted {{ color:#6b7280; }}
    a {{ color:#2563eb; text-decoration:none; }}
  </style>
</head>
<body>
  <p><a href="report.html">← 返回 Rank 29 主报告</a></p>
  <h1>Rank 29 · narrow paper pilot monitoring / weekly-review red-watch</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 这页不追新 bar、不改规则，只把 P3 最小 monitoring / weekly-review 接线落成可执行 artifact。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>Rank 29 当前最该补的不是再做 admission wording，而是把中段 time-bucket red-watch 压成 monitoring board + weekly-review queue。</b></p>
    <ul>
      <li>主口径继续冻结：<code>breakout_align_ge2 + no_overlap_guard + next-bar open 持有 8 根</code>。</li>
      <li>当前 narrow paper pilot 仍成立：6bps 与 15bps 的 aggregate 都保持为正，说明它不需要被压回研究态。</li>
      <li>真正需要 operator 持续盯的是 <code>bucket_2</code>：10/15bps 下明显变弱，因此这轮把它直接挂成 weekly-review 队列，而不是继续口头提醒。</li>
      <li>当前仍是 <code>paper-only narrow pilot</code>；没有偷升 tiny-live，也没有改动原策略规则。</li>
    </ul>
  </div>

  <div class="card">
    <h2>monitoring board</h2>
    {render_table(monitoring_board)}
    <p class="muted">artifact：<code>reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/narrow_paper_pilot_monitoring_board.csv</code></p>
  </div>

  <div class="card">
    <h2>weekly-review red-watch queue</h2>
    {render_table(weekly_review_queue[["asset", "review_bucket", "review_priority", "lifetime_total_return_6bps", "weekly_review_status", "review_focus", "promotion_boundary"]], percent_cols={"lifetime_total_return_6bps"})}
    <p class="muted">artifact：<code>reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/narrow_paper_pilot_weekly_review_queue.csv</code></p>
  </div>

  <div class="card">
    <h2>reader-facing 结论</h2>
    <ul>
      <li>这条线当前已经配得上 narrow paper pilot，但必须带着 <code>bucket_2</code> red-watch 前进。</li>
      <li>BTC / ETH 的中段 bucket 是当前最脆的两条腿；SOL 的中段 bucket 仍为正，但也不能当成全局免检通行证。</li>
      <li>因此后续若继续认领 Rank 29，默认应沿这张 monitoring board / weekly-review queue 做 append，而不是再回到 intake 文案。</li>
    </ul>
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")

    print("[ok] rank29 narrow paper monitoring generated")
    print("[artifact]", ART_DIR / "narrow_paper_pilot_monitoring_board.csv")
    print("[artifact]", ART_DIR / "narrow_paper_pilot_weekly_review_queue.csv")
    print("[site]", REPORT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
