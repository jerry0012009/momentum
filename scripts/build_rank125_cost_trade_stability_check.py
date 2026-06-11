#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank125_range_location_veto_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank125_range_location_veto_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank125_range_location_veto_cost_trade_stability.html"
PRIMARY_COSTS = [6.0, 10.0, 15.0]

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


def pct(v, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v, digits: int = 2) -> str:
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
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
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


def main() -> None:
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    metrics_path = ART_DIR / "metrics_by_setup_cost_split.csv"
    trade_log_path = ART_DIR / "trade_log.csv"
    if not metrics_path.exists() or not trade_log_path.exists():
        raise FileNotFoundError("missing rank125 clean replication artifacts")

    metrics_df = pd.read_csv(metrics_path)
    trade_log = pd.read_csv(trade_log_path)
    trade_log["signal_time"] = pd.to_datetime(trade_log["signal_time"], utc=True)
    trade_log["entry_time"] = pd.to_datetime(trade_log["entry_time"], utc=True)
    trade_log["exit_time"] = pd.to_datetime(trade_log["exit_time"], utc=True)
    test_metrics = metrics_df[metrics_df["split"] == "test"].copy()

    cost_rows = []
    for cost in PRIMARY_COSTS:
        chunk = test_metrics[test_metrics["cost_bps"] == cost]
        for setup in sorted(chunk["setup"].unique()):
            base = chunk[(chunk["setup"] == setup) & (chunk["variant"] == "baseline")]
            gate = chunk[(chunk["setup"] == setup) & (chunk["variant"] == "rl_gate")]
            if base.empty or gate.empty:
                continue
            b = base.iloc[0]
            g = gate.iloc[0]
            cost_rows.append({
                "setup": setup,
                "cost_bps": cost,
                "baseline_return": float(b["mean_total_return"]),
                "gate_return": float(g["mean_total_return"]),
                "return_delta": float(g["mean_total_return"] - b["mean_total_return"]),
                "baseline_failure": float(b["failure_before_target_rate"]),
                "gate_failure": float(g["failure_before_target_rate"]),
                "failure_delta": float(g["failure_before_target_rate"] - b["failure_before_target_rate"]),
                "baseline_trades": int(b["trades"]),
                "gate_trades": int(g["trades"]),
                "trade_retention": float(g["trades"] / max(b["trades"], 1)),
            })
    cost_summary = pd.DataFrame(cost_rows)
    cost_summary.to_csv(ART_DIR / "cost_trade_stability_summary.csv", index=False)

    overall_rows = []
    for cost in PRIMARY_COSTS:
        chunk = cost_summary[cost_summary["cost_bps"] == cost]
        overall_rows.append({
            "cost_bps": cost,
            "mean_return_delta": float(chunk["return_delta"].mean()),
            "mean_failure_delta": float(chunk["failure_delta"].mean()),
            "mean_trade_retention": float(chunk["trade_retention"].mean()),
            "positive_setup_count": int((chunk["return_delta"] > 0).sum()),
            "non_worsening_failure_count": int((chunk["failure_delta"] <= 0).sum()),
        })
    overall_summary = pd.DataFrame(overall_rows)
    overall_summary.to_csv(ART_DIR / "cost_trade_stability_overall.csv", index=False)

    test_trades = trade_log[trade_log["split"] == "test"].copy()
    asset_rows = []
    for cost in PRIMARY_COSTS:
        tmp = test_trades.copy()
        rate = cost / 10000.0
        tmp["net_return"] = (1.0 + tmp["gross_return"]) * (1.0 - rate) * (1.0 - rate) - 1.0
        for asset in sorted(tmp["asset"].unique()):
            base = tmp[(tmp["asset"] == asset) & (tmp["variant"] == "baseline")]
            gate = tmp[(tmp["asset"] == asset) & (tmp["variant"] == "rl_gate")]
            if base.empty or gate.empty:
                continue
            asset_rows.append({
                "asset": asset,
                "cost_bps": cost,
                "baseline_return": float(base["net_return"].mean()),
                "gate_return": float(gate["net_return"].mean()),
                "return_delta": float(gate["net_return"].mean() - base["net_return"].mean()),
                "baseline_trades": int(len(base)),
                "gate_trades": int(len(gate)),
                "trade_retention": float(len(gate) / max(len(base), 1)),
            })
    asset_cost = pd.DataFrame(asset_rows)
    asset_cost.to_csv(ART_DIR / "asset_cost_stability_summary.csv", index=False)

    mean_delta = float(overall_summary["mean_return_delta"].mean())
    mean_failure = float(overall_summary["mean_failure_delta"].mean())
    mean_retention = float(overall_summary["mean_trade_retention"].mean())
    positive_counts = overall_summary["positive_setup_count"].tolist()
    failure_counts = overall_summary["non_worsening_failure_count"].tolist()

    promote_cond = (
        min(positive_counts) >= 2
        and mean_delta > 0.0006
        and mean_failure <= -0.005
        and mean_retention >= 0.70
    )
    keep_cond = (
        min(positive_counts) >= 2
        and mean_delta > 0
        and mean_failure <= 0
        and mean_retention >= 0.55
    )

    if promote_cond:
        verdict = "promote_P2"
        verdict_label = "promote_P2 / paper candidate"
        verdict_reason = "成本抬到 10/15 bps 后仍保留跨 setup 的正向增量，而且 trade retention 没有塌到失真，足够升到 P2。"
    elif keep_cond:
        verdict = "keep_P1_budget_used"
        verdict_label = "keep_P1 / budget used"
        verdict_reason = "这层 uplift 在 6/10/15 bps 下都没有被直接打穿，但它仍主要集中在 breakout_short no-chase 与 ema_psar_long 的局部改善，trade retention 也明显下滑，所以当前更诚实的位置是 keep_P1 且默认预算用尽，不直接升 P2。"
    else:
        verdict = "park"
        verdict_label = "park / evidence pool"
        verdict_reason = "成本一抬就把增量打回去，或 uplift 主要来自过度砍交易数；当前不值得继续占 active Scout 预算。"

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_reason": verdict_reason,
        "mean_return_delta": mean_delta,
        "mean_failure_delta": mean_failure,
        "mean_trade_retention": mean_retention,
        "positive_setup_count_by_cost": positive_counts,
        "non_worsening_failure_count_by_cost": failure_counts,
    }
    (ART_DIR / "cost_trade_stability_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 125 · range location veto gate · cost / trade stability check</h1>
    <div class=\"card\">
      <p><b>当前 hard verdict：</b><span class=\"{'good' if verdict == 'promote_P2' else 'warn' if verdict.startswith('keep_P1') else 'bad'}\">{escape(verdict_label)}</span></p>
      <p class=\"muted\">{escape(verdict_reason)}</p>
      <p><b>检查口径：</b><code>复用同一份 clean-room trade log；只看 6 / 10 / 15 bps 成本梯度下的 return delta、failure delta、trade retention</code></p>
    </div>
    <div class=\"card\">
      <h2>总体稳定性快照</h2>
      {render_table(overall_summary, percent_cols={'mean_return_delta','mean_failure_delta','mean_trade_retention'})}
    </div>
    <div class=\"card\">
      <h2>分 setup 成本 / 交易数稳定性</h2>
      {render_table(cost_summary, percent_cols={'baseline_return','gate_return','return_delta','baseline_failure','gate_failure','failure_delta','trade_retention'})}
    </div>
    <div class=\"card\">
      <h2>分资产成本快照</h2>
      {render_table(asset_cost, percent_cols={'baseline_return','gate_return','return_delta','trade_retention'})}
    </div>
    <div class=\"card\">
      <h2>当前最诚实的人话</h2>
      <ul>
        <li><b>ema_psar_long：</b>小幅增益在成本抬高后仍保留，但幅度不够把它推成 shared 默认层。</li>
        <li><b>breakout_short：</b>no-chase veto 方向没错，但收益改善继续伴随明显 trade retention 下降，更像值得留样而不是直接升格。</li>
        <li><b>fib_retest_long：</b>基本等价，说明它还谈不上真正三线通吃。</li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_overall.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/asset_cost_stability_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.json</code></li>
      </ul>
    </div>
    """

    write_html(SITE_DIR / "cost_trade_stability_check.html", "Rank 125 · cost/trade stability", body)
    write_html(READING_PATH, "Rank 125 · range location veto cost/trade stability", body)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
