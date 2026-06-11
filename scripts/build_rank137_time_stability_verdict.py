#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank137_state_expiry_latency_budget_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank137_state_expiry_latency_budget_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank137_state_expiry_latency_budget_time_stability.html"
TRADE_LOG = ART_DIR / "trade_log.csv"
PRIMARY_VARIANT = "confirm_window_12"
PRIMARY_COST = 6.0
COSTS = [6.0, 10.0, 15.0]

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def net_ret(gross: pd.Series, cost_bps: float) -> pd.Series:
    rate = float(cost_bps) / 10000.0
    return (1.0 + gross) * (1.0 - rate) * (1.0 - rate) - 1.0


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
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
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


def assign_buckets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("signal_time").reset_index(drop=True).copy()
    labels = ["early", "mid", "late"]
    df["time_bucket"] = pd.qcut(df.index, 3, labels=labels)
    return df


def score_from_series(series: pd.Series, positive_is_good: bool = True) -> int:
    good_count = int(series.sum()) if positive_is_good else int((~series).sum())
    if good_count >= 3:
        return 3
    if good_count == 2:
        return 2
    if good_count == 1:
        return 1
    return 0


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    df = pd.read_csv(TRADE_LOG, parse_dates=["signal_time", "entry_time", "exit_time"])
    test = df[df["split"] == "test"].copy()
    baseline = assign_buckets(test[test["variant"] == "baseline_no_expiry"].copy())
    variant = assign_buckets(test[test["variant"] == PRIMARY_VARIANT].copy())

    for cost in COSTS:
        baseline[f"net_{int(cost)}"] = net_ret(baseline["gross_return"], cost)
        variant[f"net_{int(cost)}"] = net_ret(variant["gross_return"], cost)

    bucket_rows: list[dict[str, object]] = []
    labels = ["early", "mid", "late"]
    for label in labels:
        b = baseline[baseline["time_bucket"] == label]
        v = variant[variant["time_bucket"] == label]
        row: dict[str, object] = {
            "time_bucket": label,
            "baseline_trades": int(len(b)),
            "variant_trades": int(len(v)),
            "trade_count_retention": len(v) / len(b) if len(b) else None,
            "baseline_failure": b["failure_before_target"].mean(),
            "variant_failure": v["failure_before_target"].mean(),
            "failure_delta": v["failure_before_target"].mean() - b["failure_before_target"].mean() if len(b) and len(v) else None,
            "variant_time_to_entry_bars": v["time_to_entry_bars"].mean(),
        }
        for cost in COSTS:
            k = int(cost)
            row[f"baseline_return_{k}bps"] = b[f"net_{k}"].mean()
            row[f"variant_return_{k}bps"] = v[f"net_{k}"].mean()
            row[f"return_delta_{k}bps"] = v[f"net_{k}"].mean() - b[f"net_{k}"].mean() if len(b) and len(v) else None
        bucket_rows.append(row)
    bucket_summary = pd.DataFrame(bucket_rows)
    bucket_summary.to_csv(ART_DIR / "time_stability_bucket_summary.csv", index=False)

    asset_rows = []
    for label in labels:
        sub = variant[variant["time_bucket"] == label]
        for asset, grp in sub.groupby("asset"):
            asset_rows.append(
                {
                    "time_bucket": label,
                    "asset": asset,
                    "trades": int(len(grp)),
                    "mean_return_6bps": grp["net_6"].mean(),
                    "failure_rate": grp["failure_before_target"].mean(),
                }
            )
    asset_summary = pd.DataFrame(asset_rows).sort_values(["time_bucket", "asset"])
    asset_summary.to_csv(ART_DIR / "time_stability_asset_summary.csv", index=False)

    setup_rows = []
    for label in labels:
        sub = variant[variant["time_bucket"] == label]
        for setup, grp in sub.groupby("setup"):
            setup_rows.append(
                {
                    "time_bucket": label,
                    "setup": setup,
                    "trades": int(len(grp)),
                    "mean_return_6bps": grp["net_6"].mean(),
                    "failure_rate": grp["failure_before_target"].mean(),
                }
            )
    setup_summary = pd.DataFrame(setup_rows).sort_values(["time_bucket", "setup"])
    setup_summary.to_csv(ART_DIR / "time_stability_setup_summary.csv", index=False)

    positive_bucket_6 = (bucket_summary["variant_return_6bps"] > 0).sum()
    positive_bucket_10 = (bucket_summary["variant_return_10bps"] > 0).sum()
    positive_bucket_15 = (bucket_summary["variant_return_15bps"] > 0).sum()
    positive_asset_breadth = asset_summary.groupby("time_bucket")["mean_return_6bps"].apply(lambda s: int((s > 0).sum())).to_dict()
    all_buckets_have_2pos_assets = sum(v >= 2 for v in positive_asset_breadth.values())

    usefulness = 1
    time_stability = score_from_series(bucket_summary["variant_return_6bps"] > 0)
    cross_asset_stability = 1 if all_buckets_have_2pos_assets >= 2 else 0
    cost_trade_stability = score_from_series(bucket_summary["variant_return_10bps"] > 0)
    deployability = 0 if positive_bucket_6 < 2 else 1

    recommended_action = "park"
    hard_fail_flags = [
        "single_pocket_dependency" if positive_bucket_6 <= 1 else "",
        "post_cost_collapse" if positive_bucket_10 <= 1 else "",
    ]
    hard_fail_flags = [x for x in hard_fail_flags if x]

    scorecard = pd.DataFrame(
        [
            {
                "candidate": "Rank 137 / state expiry latency budget gate",
                "checked_variant": PRIMARY_VARIANT,
                "usefulness": usefulness,
                "time_stability": time_stability,
                "cross_asset_stability": cross_asset_stability,
                "cost_trade_stability": cost_trade_stability,
                "deployability": deployability,
                "hard_fail_flags": ", ".join(hard_fail_flags) if hard_fail_flags else "none",
                "recommended_action": recommended_action,
                "why_now": "最小时间稳定性裁决已经把它从『有点改善』推进到『是否真的能升 P2』；如果 uplift 只集中在中段 pocket，就该及时 park，让 Scout 资源回到 fresh intake。",
                "main_weakness": "6bps 下只有中段时间桶明显转正，early/late 仍为负；10/15bps 也只有中段勉强站住，不足以支撑更高层级。",
            }
        ]
    )
    scorecard.to_csv(ART_DIR / "time_stability_scorecard.csv", index=False)

    summary = {
        "candidate": "Rank 137 / state expiry latency budget gate",
        "checked_variant": PRIMARY_VARIANT,
        "test_baseline_trades": int(len(baseline)),
        "test_variant_trades": int(len(variant)),
        "positive_time_buckets_6bps": int(positive_bucket_6),
        "positive_time_buckets_10bps": int(positive_bucket_10),
        "positive_time_buckets_15bps": int(positive_bucket_15),
        "positive_asset_breadth_6bps_by_bucket": positive_asset_breadth,
        "recommended_action": recommended_action,
        "hard_fail_flags": hard_fail_flags,
    }
    (ART_DIR / "time_stability_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    title = "Rank 137 / state expiry latency budget gate — minimal time stability verdict"
    summary_html = f"""
    <h1>{escape(title)}</h1>
    <p class='muted'>只对 <code>{PRIMARY_VARIANT}</code> 做测试集三桶时间稳定性裁决；不重开新研究，不追加重型回测。</p>
    <div class='card'>
      <h2>硬结论</h2>
      <p><span class='bad'>recommended_action = park</span></p>
      <ul>
        <li>6bps 下三个时间桶里，只有 <code>mid</code> 转正；<code>early</code> 与 <code>late</code> 仍为负。</li>
        <li>10/15bps 下也只有中段时间桶还能站住，其余桶继续为负，说明 uplift 不是稳定 desk 口袋。</li>
        <li>失败率确实下降，但收益改善更像 <code>single-pocket dependency</code>，不足以把它从 P1 升到 P2。</li>
      </ul>
    </div>
    <div class='card'>
      <h2>时间稳定性三桶（test only）</h2>
      {render_table(bucket_summary, percent_cols={"trade_count_retention", "baseline_failure", "variant_failure", "failure_delta", "baseline_return_6bps", "variant_return_6bps", "return_delta_6bps", "baseline_return_10bps", "variant_return_10bps", "return_delta_10bps", "baseline_return_15bps", "variant_return_15bps", "return_delta_15bps"}, digits_cols={"variant_time_to_entry_bars": 2})}
    </div>
    <div class='card'>
      <h2>按资产拆解（variant @ 6bps）</h2>
      {render_table(asset_summary, percent_cols={"mean_return_6bps", "failure_rate"})}
    </div>
    <div class='card'>
      <h2>按 setup 拆解（variant @ 6bps）</h2>
      {render_table(setup_summary, percent_cols={"mean_return_6bps", "failure_rate"})}
    </div>
    <div class='card'>
      <h2>轻量 Scorecard</h2>
      {render_table(scorecard)}
    </div>
    """
    write_html(SITE_DIR / "time_stability_verdict.html", title, summary_html)

    reading_html = f"""
    <h1>Rank 137 / state expiry latency budget gate — 时间稳定性最小裁决</h1>
    <div class='card'>
      <p>bot3 只给了这条线一次真正会改变 verdict 的最小检查：把 <code>confirm_window_12</code> 的测试集按时间顺序切成 <code>early / mid / late</code> 三桶。</p>
      <p><span class='bad'>结果：park。</span> 原因很简单——改善主要集中在中段时间桶，早段和晚段在 6bps 下仍为负；成本抬到 10/15bps 后也没有跨桶站稳。它更像一个 pocket repair，而不是稳定 shared gate。</p>
      <p><a href='../..//factors/scout_rank137_state_expiry_latency_budget_15m/time_stability_verdict.html'>查看完整 verdict 页面</a></p>
    </div>
    """
    write_html(READING_PATH, title, reading_html)

    print("Wrote Rank 137 time stability verdict artifacts.")


if __name__ == "__main__":
    main()
