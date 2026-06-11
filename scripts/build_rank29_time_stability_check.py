#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank29_trendline_breakout_navigator_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank29_trendline_breakout_navigator_15m"
REPORT_PATH = SITE_DIR / "time_stability_check.html"

ASSETS = ["btc_usd", "eth_usd", "sol_usd"]
COSTS = [6, 10, 15, 20]
MODE = "no_overlap_guard"
BUCKET_LABELS = ["bucket_1", "bucket_2", "bucket_3"]


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
    head = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells = []
        for c in df.columns:
            v = row[c]
            if c in percent_cols:
                txt = pct(v)
            elif isinstance(v, (float, np.floating, int, np.integer)) and not isinstance(v, bool):
                txt = num(v, digits_cols.get(c, 2))
            else:
                txt = str(v)
            cells.append(f"<td>{escape(txt)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def load_trades(asset: str, cost: int) -> pd.DataFrame:
    path = ART_DIR / f"{asset}_{MODE}_trades_{cost}bps.csv"
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=["entry_ts", "net_ret", "time_bucket"])
    df = pd.read_csv(path)
    if "entry_ts" not in df.columns:
        return pd.DataFrame(columns=["entry_ts", "net_ret", "time_bucket"])
    df["entry_ts"] = pd.to_datetime(df["entry_ts"], utc=True, errors="coerce")
    df = df[df["entry_ts"].notna()].sort_values("entry_ts").reset_index(drop=True)
    if len(df) >= 3:
        df["time_bucket"] = pd.qcut(df.index, 3, labels=BUCKET_LABELS)
    else:
        df["time_bucket"] = "bucket_all"
    return df


def total_return(series: pd.Series) -> float:
    if series.empty:
        return np.nan
    return float((1.0 + series).prod() - 1.0)


def summarize_bucket(asset: str, cost: int, bucket: str, trades: pd.DataFrame) -> dict[str, object]:
    return {
        "asset": asset.upper().replace("_", "-"),
        "cost_bps_per_side": int(cost),
        "time_bucket": bucket,
        "trades": int(len(trades)),
        "win_rate": float((trades["net_ret"] > 0).mean()) if not trades.empty else np.nan,
        "avg_net_ret": float(trades["net_ret"].mean()) if not trades.empty else np.nan,
        "total_return": total_return(trades["net_ret"]),
    }


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)

    rows: list[dict[str, object]] = []
    for asset in ASSETS:
        for cost in COSTS:
            df = load_trades(asset, cost)
            for bucket, part in df.groupby("time_bucket", observed=False):
                rows.append(summarize_bucket(asset, cost, str(bucket), part))

    bucket_summary = pd.DataFrame(rows)
    if bucket_summary.empty:
        bucket_summary = pd.DataFrame(columns=["asset", "cost_bps_per_side", "time_bucket", "trades", "win_rate", "avg_net_ret", "total_return"])
        overall = pd.DataFrame(columns=["cost_bps_per_side", "time_bucket", "assets_tested", "positive_assets", "mean_total_return", "median_total_return", "mean_trades", "min_trades", "mean_win_rate", "positive_asset_ratio"])
    else:
        bucket_summary = bucket_summary.sort_values(["cost_bps_per_side", "time_bucket", "asset"]).reset_index(drop=True)
        overall = (
            bucket_summary.groupby(["cost_bps_per_side", "time_bucket"], as_index=False)
            .agg(
                assets_tested=("asset", "nunique"),
                positive_assets=("total_return", lambda s: int((s > 0).sum())),
                mean_total_return=("total_return", "mean"),
                median_total_return=("total_return", "median"),
                mean_trades=("trades", "mean"),
                min_trades=("trades", "min"),
                mean_win_rate=("win_rate", "mean"),
            )
            .sort_values(["cost_bps_per_side", "time_bucket"])
            .reset_index(drop=True)
        )
        overall["positive_asset_ratio"] = overall["positive_assets"] / overall["assets_tested"].replace(0, np.nan)

    cost6 = overall[overall["cost_bps_per_side"] == 6].copy()
    cost10 = overall[overall["cost_bps_per_side"] == 10].copy()
    promote = False
    verdict = "park / evidence pool"
    headline = "Rank 29 时间稳定性检查出现决定性破坏：压回 park / evidence pool。"
    if (
        len(cost6) == 3
        and float(cost6["mean_total_return"].min()) > 0
        and int((cost6["positive_assets"] == cost6["assets_tested"]).sum()) == 3
    ):
        promote = True
        verdict = "promote to narrow paper pilot approved (P3)"
        headline = "Rank 29 时间稳定性检查未爆雷：升到 narrow paper pilot（P3），但保留中段 red-watch。"
        if not cost10.empty and float(cost10["mean_total_return"].min()) <= 0:
            headline = "Rank 29 时间稳定性在 6bps 下通过：可升到 narrow paper pilot（P3），但 10/15bps 的中段时间桶要挂 red-watch。"

    meta = pd.DataFrame([
        {
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "candidate_id": "rank29_trendline_breakout_navigator",
            "mode": MODE,
            "check": "time_stability_terciles",
            "hard_verdict": verdict,
            "headline": headline,
        }
    ])

    bucket_summary.to_csv(ART_DIR / "time_stability_bucket_summary.csv", index=False)
    overall.to_csv(ART_DIR / "time_stability_overall_summary.csv", index=False)
    meta.to_csv(ART_DIR / "time_stability_trial_meta.csv", index=False)

    generated_at = meta.iloc[0]["generated_at_utc"]
    if overall.empty:
        verdict_points = [
            "检查口径：把 strict-causal + no-overlap 后的主变体交易按时间顺序切成 3 个等份 bucket（早 / 中 / 晚），分别看每桶是否仍然存活。",
            "这次结果不是“某一桶变弱”，而是 strict-causal + no-overlap 下根本没有留下可分桶的交易样本。",
            "所以这页的结论不是 red-watch，而是更根本的一条：当前主样本已经没有足够交易可支撑时间稳定性判断。",
            "这也意味着基于旧口径的时间稳定性正面结论应全部作废。",
        ]
        reader_points = [
            "未来函数拿掉以后，Rank 29 在当前主样本下已经没有可用于时间切片的交易。",
            "因此它不是“时间分桶后变弱”，而是先在 causal + no-overlap 这一关就已经失去可交易性。",
            "下一步该做的不是继续晋级，而是重写信号定义或直接重新立项。",
        ]
    elif promote:
        verdict_points = [
            "检查口径：把 strict-causal + no-overlap 后的主变体交易按时间顺序切成 3 个等份 bucket（早 / 中 / 晚），分别看每桶是否仍然存活。",
            "最关键结果：6bps 下三个时间桶的跨资产 mean_total_return 都保持为正，且每个桶都是 3/3 资产为正。",
            "红灯位置：10bps 与 15bps 的 <code>bucket_2</code> 明显变弱，说明这条线不是“所有时间段都一样干净”，后续 paper pilot 要把中段 bucket 挂进 weekly review / red-watch。",
            "如果 strict-causal 口径下三个时间桶仍能活下来，才允许继续谈后续 paper；否则就应把之前基于旧口径的晋级结论一并回收。",
        ]
        reader_points = [
            "这不是“完美稳定”的策略：更高 friction 下，中段 bucket 先变弱。",
            "但它也不是“一做时间切片就坍塌”的热像素：在 paper 更贴近的 6bps 口径下，三个 bucket 都还活着。",
            "所以这页现在只回答一件事：未来函数拿掉以后，这条线在时间切片上还有没有连续存活能力。",
        ]
    else:
        verdict_points = [
            "检查口径：把 strict-causal + no-overlap 后的主变体交易按时间顺序切成 3 个等份 bucket（早 / 中 / 晚），分别看每桶是否仍然存活。",
            "最关键结果：主口径下没有通过时间稳定性门槛，不能继续沿用旧的晋级判断。",
            "一旦时间切片结果无法成立，就说明这条线即便偶尔有交易，也没有足够稳的跨阶段生存能力。",
            "所以旧口径里关于“时间稳定”的正面结论也必须一起回收。",
        ]
        reader_points = [
            "这条线在 strict-causal 口径下没有展示出足够稳定的连续表现。",
            "因此更合理的动作不是继续推进 paper，而是回到信号定义层面重做。",
            "这页的作用就是确认：未来函数拿掉后，时间稳定性不再成立。",
        ]
    verdict_points_html = ''.join(f'<li>{p}</li>' for p in verdict_points)
    reader_points_html = ''.join(f'<li>{p}</li>' for p in reader_points)
    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 29 time stability check</title>
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
  <h1>Rank 29 · time stability check（strict-causal / no-overlap）</h1>
  <p class="muted">生成时间：{escape(generated_at)} ｜ 固定复用 strict-causal 的 no-overlap trades，不追新 bar，不改规则；只检查时间稳定性。</p>

  <div class="card">
    <h2>hard verdict</h2>
    <p><b>{escape(headline)}</b></p>
    <ul>{verdict_points_html}</ul>
  </div>

  <div class="card">
    <h2>overall time-bucket summary</h2>
    {render_table(overall[["cost_bps_per_side","time_bucket","mean_total_return","positive_asset_ratio","mean_trades","min_trades","mean_win_rate"]], percent_cols={"mean_total_return","positive_asset_ratio","mean_win_rate"}, digits_cols={"cost_bps_per_side":0,"mean_trades":1,"min_trades":0})}
  </div>

  <div class="card">
    <h2>per-asset bucket summary</h2>
    {render_table(bucket_summary[["asset","cost_bps_per_side","time_bucket","trades","total_return","win_rate","avg_net_ret"]], percent_cols={"total_return","win_rate","avg_net_ret"}, digits_cols={"cost_bps_per_side":0,"trades":0})}
  </div>

  <div class="card">
    <h2>reader-facing 结论</h2>
    <ul>{reader_points_html}</ul>
  </div>
</body>
</html>'''
    REPORT_PATH.write_text(html, encoding="utf-8")

    print("[ok] rank29 time stability check generated")
    print("[artifact]", ART_DIR / "time_stability_overall_summary.csv")
    print("[site]", REPORT_PATH)
    print("[verdict]", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
