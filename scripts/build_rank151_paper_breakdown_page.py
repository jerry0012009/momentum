#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import csv
import json
import math
import shutil

import pandas as pd

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "reports" / "site" / "interview_showcase" / "momentum"
ALIAS_SITE_DIR = ROOT / "reports" / "site" / "factor_research_library" / "momentum"
ART_DIR = ROOT / "reports" / "artifacts" / "interview_showcase" / "momentum"
ALIAS_ART_DIR = ROOT / "reports" / "artifacts" / "factor_research_library" / "momentum"
OUT_HTML = SITE_DIR / "rank151_source_breakdown.html"
ALIAS_OUT_HTML = ALIAS_SITE_DIR / "rank151_source_breakdown.html"
OUT_PNG = ART_DIR / "rank151_source_breakdown_profile.png"
ALIAS_OUT_PNG = ALIAS_ART_DIR / "rank151_source_breakdown_profile.png"
OUT_JSON = ART_DIR / "rank151_source_breakdown_summary.json"
ALIAS_OUT_JSON = ALIAS_ART_DIR / "rank151_source_breakdown_summary.json"

EVENT_TABLE = ROOT / "reports" / "artifacts" / "quant_digests" / "ewmac_breakout_alignment_20260323" / "event_table.csv"
SUMMARY_CSV = ROOT / "reports" / "artifacts" / "quant_digests" / "ewmac_breakout_alignment_20260323" / "bandpass_summary.csv"
BUCKET_CSV = ROOT / "reports" / "artifacts" / "quant_digests" / "ewmac_breakout_alignment_20260323" / "bucket_summary.csv"
INTAKE_CSV = ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "source_intake_card.csv"
PROMOTION_CSV = ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "promotion_scorecard.csv"
ROLLING_CSV = ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "rolling_split_scorecard.csv"
ADMISSION_CSV = ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "launch_admission_scorecard.csv"
ADMISSION_SLICE_CSV = ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "launch_admission_recent_slice_summary.csv"
RUNNER_STATUS_CSV = ROOT / "reports" / "artifacts" / "paper_rank151_breakout_bandpass_gate" / "rank151_paper_status.csv"


def ensure_dirs() -> None:
    for path in (SITE_DIR, ALIAS_SITE_DIR, ART_DIR, ALIAS_ART_DIR):
        path.mkdir(parents=True, exist_ok=True)


def fmt_num(value: float | int | None, digits: int = 3) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "-"
    return f"{value:.{digits}f}"


def fmt_pct(value: float | int | None, digits: int = 2) -> str:
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return "-"
    return f"{value * 100:.{digits}f}%"


def spearman_like(a: pd.Series, b: pd.Series) -> float:
    ranked_a = a.rank(method="average")
    ranked_b = b.rank(method="average")
    return float(ranked_a.corr(ranked_b))


def load_two_col_csv(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if not row:
                continue
            rows[row[0]] = ",".join(row[1:]).strip()
    return rows


def load_metrics() -> dict[str, object]:
    events = pd.read_csv(EVENT_TABLE, parse_dates=["ts"])
    summary = pd.read_csv(SUMMARY_CSV)
    buckets = pd.read_csv(BUCKET_CSV)
    intake = load_two_col_csv(INTAKE_CSV)
    promotion = pd.read_csv(PROMOTION_CSV).iloc[0].to_dict()
    rolling = pd.read_csv(ROLLING_CSV).iloc[0].to_dict()
    admission = pd.read_csv(ADMISSION_CSV).iloc[0].to_dict()
    admission_slices = pd.read_csv(ADMISSION_SLICE_CSV)
    admission_assets = pd.read_csv(
        ROOT / "reports" / "artifacts" / "scout_rank151_ewmac_breakout_bandpass_gate_15m" / "launch_admission_recent_slice_asset_summary.csv"
    )
    runner = pd.read_csv(RUNNER_STATUS_CSV).iloc[0].to_dict()

    q20 = float(events["align_score"].quantile(0.2))
    q80 = float(events["align_score"].quantile(0.8))
    events["band_pass_flag"] = ((events["align_score"] > q20) & (events["align_score"] <= q80)).astype(int)
    events["pct_rank"] = events["align_score"].rank(pct=True, method="average")
    events["center_proximity"] = -(events["pct_rank"] - 0.5).abs()

    pooled_align_rho = spearman_like(events["align_score"], events["signed_bps"])
    pooled_center_rho = spearman_like(events["center_proximity"], events["signed_bps"])

    cs_ic_rows: list[dict[str, float | str]] = []
    for ts, frame in events.groupby("ts"):
        if len(frame) < 3:
            continue
        if frame["align_score"].nunique() < 2 or frame["signed_bps"].nunique() < 2:
            continue
        cs_ic_rows.append(
            {
                "ts": ts.isoformat(),
                "ic": spearman_like(frame["align_score"], frame["signed_bps"]),
            }
        )
    cs_ic_df = pd.DataFrame(cs_ic_rows)
    ic_mean = float(cs_ic_df["ic"].mean()) if not cs_ic_df.empty else math.nan
    ic_std = float(cs_ic_df["ic"].std(ddof=0)) if not cs_ic_df.empty else math.nan
    ic_ir = float(ic_mean / ic_std) if cs_ic_df.shape[0] and ic_std else math.nan
    ic_positive_ratio = float((cs_ic_df["ic"] > 0).mean()) if not cs_ic_df.empty else math.nan

    summary_map = {
        "baseline": {
            "label": "baseline",
            "mean_bps": float(summary.loc[summary["slice"] == "base_all", "mean_bps"].iloc[0]),
            "n": int(summary.loc[summary["slice"] == "base_all", "n"].iloc[0]),
        },
        "hard_positive": {
            "label": "hard-positive",
            "mean_bps": float(events.loc[events["align_score"] > 0, "signed_bps"].mean()),
            "n": int((events["align_score"] > 0).sum()),
        },
        "band_pass": {
            "label": "band-pass",
            "mean_bps": float(summary.loc[summary["slice"] == "mid_band_q20_q80", "mean_bps"].iloc[0]),
            "n": int(summary.loc[summary["slice"] == "mid_band_q20_q80", "n"].iloc[0]),
        },
        "tail_extremes": {
            "label": "tail extremes",
            "mean_bps": float(summary.loc[summary["slice"] == "extreme_tail", "mean_bps"].iloc[0]),
            "n": int(summary.loc[summary["slice"] == "extreme_tail", "n"].iloc[0]),
        },
    }
    admission_slices = admission_slices.sort_values("window_days")

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "events": events,
        "summary": summary,
        "summary_map": summary_map,
        "buckets": buckets,
        "intake": intake,
        "promotion": promotion,
        "rolling": rolling,
        "admission": admission,
        "admission_slices": admission_slices,
        "admission_assets": admission_assets,
        "runner": runner,
        "q20": q20,
        "q80": q80,
        "pooled_align_rho": pooled_align_rho,
        "pooled_center_rho": pooled_center_rho,
        "cs_ic_n": int(len(cs_ic_df)),
        "cs_ic_mean": ic_mean,
        "cs_ic_std": ic_std,
        "cs_ic_ir": ic_ir,
        "cs_ic_positive_ratio": ic_positive_ratio,
    }


def build_chart(metrics: dict[str, object]) -> None:
    if plt is None:
        return
    events: pd.DataFrame = metrics["events"]  # type: ignore[assignment]
    buckets: pd.DataFrame = metrics["buckets"]  # type: ignore[assignment]
    q20 = float(metrics["q20"])
    q80 = float(metrics["q80"])
    summary_map: dict[str, dict[str, float | int | str]] = metrics["summary_map"]  # type: ignore[assignment]

    sample = events.sample(min(len(events), 1800), random_state=42).sort_values("align_score")
    bins = pd.cut(events["align_score"], bins=20, duplicates="drop")
    binned = (
        events.assign(score_bin=bins)
        .groupby("score_bin", observed=False)
        .agg(bin_x=("align_score", "mean"), bin_y=("signed_bps", "mean"))
        .dropna()
        .reset_index(drop=True)
    )

    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2))
    ax = axes[0]
    ax.scatter(sample["align_score"], sample["signed_bps"], s=10, alpha=0.16, color="#175cd3", edgecolors="none")
    ax.plot(binned["bin_x"], binned["bin_y"], color="#111827", linewidth=2.2, label="Binned mean return")
    ax.axhline(0, color="#98a2b3", linewidth=1)
    ax.axvline(q20, color="#dc6803", linestyle="--", linewidth=1.3)
    ax.axvline(q80, color="#dc6803", linestyle="--", linewidth=1.3)
    ax.set_title("Align score vs 8-bar signed return")
    ax.set_xlabel("align_score")
    ax.set_ylabel("signed_bps")
    ax.legend(frameon=False, fontsize=9, loc="upper right")

    ax = axes[1]
    labels = ["baseline", "hard-positive", "band-pass", "tail extremes"]
    keys = ["baseline", "hard_positive", "band_pass", "tail_extremes"]
    means = [float(summary_map[key]["mean_bps"]) for key in keys]
    colors = ["#94a3b8", "#60a5fa", "#16a34a", "#ef4444"]
    ax.bar(labels, means, color=colors, width=0.62)
    ax.axhline(0, color="#98a2b3", linewidth=1)
    for idx, val in enumerate(means):
        ax.text(idx, val + (0.8 if val >= 0 else -1.6), f"{val:.2f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=9)
    ax.set_title("Mean signed return by reading mode")
    ax.set_ylabel("mean_bps")
    ax.tick_params(axis="x", labelrotation=12)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=170, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(OUT_PNG, ALIAS_OUT_PNG)


def links_for_page(artifact_prefix: str) -> dict[str, str]:
    return {
        "showcase": "../index.html",
        "workflow": "../workflow.html",
        "factor_report": "../../factors/scout_rank151_ewmac_breakout_bandpass_gate_15m/report.html",
        "paper_runner": "../../factors/paper_rank151_breakout_bandpass_gate/report.html",
        "launch_reading": "../../reading/repo_scout/rank151_ewmac_breakout_bandpass_gate_launch_admission_bar.html",
        "rolling_reading": "../../reading/repo_scout/rank151_ewmac_breakout_bandpass_gate_rolling_split.html",
        "digest_reading": "../../reading/quant_digests/2026-03-23_0735_ewmac-breakout-bandpass-not-highest-score-wins.html",
        "intake_csv": f"{artifact_prefix}/scout_rank151_ewmac_breakout_bandpass_gate_15m/source_intake_card.csv",
        "runner_csv": f"{artifact_prefix}/paper_rank151_breakout_bandpass_gate/rank151_paper_status.csv",
        "chart_png": f"{artifact_prefix}/momentum/rank151_source_breakdown_profile.png",
        "summary_json": f"{artifact_prefix}/momentum/rank151_source_breakdown_summary.json",
        "source_repo": "https://github.com/nicolasdd1996/crypto-trend-follow",
    }


def stage_timeline(metrics: dict[str, object]) -> str:
    promotion = metrics["promotion"]
    rolling = metrics["rolling"]
    admission = metrics["admission"]
    runner = metrics["runner"]
    items = [
        (
            "1. Fresh intake",
            "keep_P1",
            "第一轮只完成 generic breakout 事件上的本地 quickcheck，还没走完整个 family-level A/B/C 冻结切口与 retention 守门，所以当时只配 keep_P1。",
        ),
        (
            "2. Rolling split",
            str(rolling.get("recommended_action", "")),
            "前后半段 split 之后，breakout-short 承载家族仍保留 band-pass 优势，但 fib retest 样本偏小，所以只够进 P2 讨论。",
        ),
        (
            "3. Launch admission",
            str(admission.get("recommended_action", "")),
            "recent 30/60/90 天切片继续通过正 uplift、正均值、足够交易密度和 3/3 资产覆盖。",
        ),
        (
            "4. Current runner",
            str(runner.get("stage", "")),
            "现在已经接入 host cron 的 paper runner，但它还是 frozen digest runner，不是 raw-bar 在线重算器。",
        ),
    ]
    html = ["<div class='timeline'>"]
    for title, verdict, body in items:
        html.append("<div class='timeline-item'>")
        html.append(f"<h3>{escape(title)}</h3>")
        html.append(f"<p class='timeline-k'>{escape(verdict)}</p>")
        html.append(f"<p>{escape(body)}</p>")
        html.append("</div>")
    html.append("</div>")
    return "".join(html)


def slice_table_html(admission_slices: pd.DataFrame, admission_assets: pd.DataFrame) -> str:
    parts = [
        "<table><thead><tr><th>window_days</th><th>band_pass_mean_net_bps</th><th>baseline_mean_net_bps</th><th>uplift_vs_baseline</th><th>band_pass_trades</th><th>trades_per_active_day</th><th>asset_coverage</th><th>pass</th></tr></thead><tbody>"
    ]
    baseline_map = (
        admission_slices[admission_slices["variant"] == "baseline"]
        .set_index("window_days")["mean_net_bps"]
        .to_dict()
    )
    asset_coverage_map = admission_assets.groupby("window_days")["symbol"].nunique().to_dict()
    for _, row in admission_slices.iterrows():
        if str(row["variant"]) != "band_pass":
            continue
        window_days = int(row["window_days"])
        baseline_mean = float(baseline_map.get(window_days, math.nan))
        uplift = float(row["mean_net_bps"]) - baseline_mean
        trades_per_active_day = float(row["trades"] / row["active_days"]) if float(row["active_days"]) else math.nan
        asset_coverage = int(asset_coverage_map.get(window_days, 0))
        passed = uplift > 0 and float(row["mean_net_bps"]) > 0 and trades_per_active_day >= 4 and asset_coverage == 3
        parts.append("<tr>")
        parts.append(f"<td>{escape(str(window_days))}</td>")
        parts.append(f"<td>{fmt_num(float(row['mean_net_bps']), 2)}</td>")
        parts.append(f"<td>{fmt_num(baseline_mean, 2)}</td>")
        parts.append(f"<td>{fmt_num(uplift, 2)}</td>")
        parts.append(f"<td>{escape(str(int(row['trades'])))}</td>")
        parts.append(f"<td>{fmt_num(trades_per_active_day, 2)}</td>")
        parts.append(f"<td>{escape(str(asset_coverage))}</td>")
        parts.append(f"<td>{'yes' if passed else 'no'}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def render_page(metrics: dict[str, object], artifact_prefix: str, title_suffix: str = "") -> str:
    links = links_for_page(artifact_prefix)
    summary_map: dict[str, dict[str, float | int | str]] = metrics["summary_map"]  # type: ignore[assignment]
    intake: dict[str, str] = metrics["intake"]  # type: ignore[assignment]
    runner: dict[str, object] = metrics["runner"]  # type: ignore[assignment]
    admission_slices: pd.DataFrame = metrics["admission_slices"]  # type: ignore[assignment]
    admission_assets: pd.DataFrame = metrics["admission_assets"]  # type: ignore[assignment]
    title = "Rank151 论文/来源拆解"
    if title_suffix:
        title = f"{title} · {title_suffix}"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:#f6f7f9; color:#172033; font:14px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans SC',sans-serif; }}
    .wrap {{ max-width:1140px; margin:0 auto; padding:24px 18px 56px; }}
    .hero, .section {{ background:#fff; border:1px solid #d9dee8; border-radius:8px; }}
    .hero {{ padding:22px 24px; }}
    .section {{ padding:18px 20px; margin-top:16px; }}
    h1 {{ margin:0 0 8px; font-size:28px; }}
    h2 {{ margin:0 0 10px; font-size:20px; }}
    h3 {{ margin:0 0 8px; font-size:16px; }}
    p {{ margin:8px 0; }}
    ul {{ margin:8px 0 0; padding-left:18px; }}
    li {{ margin:6px 0; }}
    .muted {{ color:#667085; }}
    .nav, .toc, .metric-row {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .btn {{ border:1px solid #cfd6e4; border-radius:6px; background:#fff; padding:6px 9px; font-weight:600; color:#175cd3; text-decoration:none; }}
    .note {{ border-left:4px solid #175cd3; background:#eff6ff; padding:10px 12px; margin:12px 0; }}
    .warn {{ border-left-color:#dc6803; background:#fff7ed; }}
    .grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:16px; }}
    .card {{ background:#fff; border:1px solid #d9dee8; border-radius:8px; padding:14px 16px; }}
    .k {{ color:#667085; font-size:12px; text-transform:uppercase; }}
    .v {{ margin-top:5px; font-size:24px; font-weight:700; }}
    .s {{ margin-top:4px; color:#667085; font-size:12px; }}
    .two {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .definition {{ background:#f8fafc; border:1px solid #e4e7ec; border-radius:8px; padding:12px 14px; }}
    .timeline {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }}
    .timeline-item {{ border:1px solid #d9dee8; border-radius:8px; background:#fff; padding:14px 16px; }}
    .timeline-k {{ color:#175cd3; font-size:12px; font-weight:700; text-transform:uppercase; }}
    table {{ width:100%; border-collapse:collapse; min-width:760px; }}
    th, td {{ border-bottom:1px solid #e5e8ef; padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f1f4f8; color:#344054; font-size:12px; white-space:nowrap; }}
    .table-wrap {{ overflow:auto; }}
    .chart {{ width:100%; height:auto; display:block; border:1px solid #e5e8ef; border-radius:8px; background:#fff; }}
    .metric-chip {{ display:inline-flex; gap:5px; align-items:center; border:1px solid #d0d5dd; border-radius:6px; padding:4px 7px; background:#f8fafc; color:#344054; font-size:12px; }}
    .metric-chip b {{ color:#101828; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    a {{ color:#175cd3; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width: 920px) {{
      .grid, .two, .timeline {{ grid-template-columns:1fr; }}
    }}
    @media (max-width: 560px) {{
      .wrap {{ padding:14px 10px 40px; }}
    }}
  </style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <h1>Rank151 论文 / 来源拆解</h1>
    <p class="muted">这页专门解释一个问题：Rank151 到底继承了原始来源的什么，修正了什么，以及为什么它现在仍是 active、未归档的研究线。Generated: {escape(str(metrics["generated_at"]))}</p>
    <div class="note warn">先说清楚：Rank151 的原始锚点不是期刊论文，而是 <code>nicolasdd1996/crypto-trend-follow</code> 这个研究型策略仓库。这页因此刻意写成“论文 / 来源拆解”，而不是假装它本来就是一篇学术论文。</div>
    <div class="nav">
      <a class="btn" href="{links['showcase']}">返回 Showcase</a>
      <a class="btn" href="{links['workflow']}">工作流 / 定时任务</a>
      <a class="btn" href="{links['factor_report']}">Rank151 因子页</a>
      <a class="btn" href="{links['paper_runner']}">Rank151 Paper Runner</a>
    </div>
    <div class="toc" style="margin-top:14px;">
      <a class="btn" href="#why-this-rank">为什么选它</a>
      <a class="btn" href="#source-thesis">原始来源讲了什么</a>
      <a class="btn" href="#translation">本地翻译成了什么</a>
      <a class="btn" href="#math">IC 与数理逻辑</a>
      <a class="btn" href="#verdict">当前 verdict</a>
      <a class="btn" href="#links">证据链接</a>
    </div>
  </div>

  <div class="grid">
    <div class="card"><div class="k">当前阶段</div><div class="v">{escape(str(runner.get("stage", "-")))}</div><div class="s">当前未归档，已经接入 paper runner</div></div>
    <div class="card"><div class="k">已闭合交易</div><div class="v">{escape(str(int(float(runner.get("closed_trades", 0)))))}</div><div class="s">runner 当前冻结 digest 样本</div></div>
    <div class="card"><div class="k">累计收益</div><div class="v">{fmt_pct(float(runner.get("lifetime_total_return_6bps", math.nan)), 2)}</div><div class="s">paper lane 展示值，不是新一轮 source 证明</div></div>
    <div class="card"><div class="k">Band-pass mean bps</div><div class="v">{fmt_num(float(summary_map['band_pass']['mean_bps']), 2)}</div><div class="s">原始事件样本上的中段收益均值</div></div>
  </div>

  <div class="section" id="why-this-rank">
    <h2>为什么选 Rank151</h2>
    <div class="two">
      <div class="definition">
        <h3>它是活的研究线</h3>
        <p>Rank151 不是归档负例，也不是已经被 future/lookahead 审计打死的线。它已经走过 <code>fresh intake -&gt; rolling split -&gt; launch admission -&gt; paper runner</code> 这一整条链路。</p>
      </div>
      <div class="definition">
        <h3>它的本地研究最完整</h3>
        <p>这条线同时有 digest、source intake、rolling split、launch admission 和 paper runner 页面，所以很适合做“一条 rank 是怎么从来源变成网站上的研究资产”的完整拆解。</p>
      </div>
    </div>
    <p>更关键的是，Rank151 的研究结论有一个很适合讲明白的反直觉点：<b>EMA / breakout 对齐分数不是越高越好</b>。这比“又发现了一个新 trigger”更有解释价值，因为它改变的是读者如何理解趋势分数本身。</p>
  </div>

  <div class="section" id="source-thesis">
    <h2>原始来源到底讲了什么</h2>
    <div class="two">
      <div class="definition">
        <h3>Source thesis</h3>
        <p>原始来源的主线不是单根 K 线择时，而是一个更完整的趋势跟随框架：在流动性较高的加密资产上，用 <code>EWMAC + breakout</code> 做连续仓位，再叠加风险过滤、执行优化和部分跨资产对冲。</p>
      </div>
      <div class="definition">
        <h3>README 里的关键句，翻成人话</h3>
        <ul>
          <li>不是 binary 的 long/flat，而是 <b>continuous positioning</b>。</li>
          <li>信号来源包含 <b>EWMAC</b> 和 <b>breakout</b>。</li>
          <li>趋势仓位要受 <b>risk-off regime filter</b> 约束。</li>
          <li>完整系统还包含 <b>execution optimization</b> 和部分 <b>hedging</b>。</li>
        </ul>
      </div>
    </div>
    <div class="note">也就是说，这个来源本来就更像“完整 trend engine 的研究仓库”，而不是一条可以直接拿来当单独 alpha 排名的因子论文。</div>
  </div>

  <div class="section" id="translation">
    <h2>本地把它翻译成了什么</h2>
    <div class="two">
      <div class="definition">
        <h3>我们继承的部分</h3>
        <p>本地真正 intake 的，是 <b>EWMAC 与 breakout 的对齐度更适合作为 admission / sizing gate</b> 这个思想，而不是把整个仓库原样搬进 desk。</p>
      </div>
      <div class="definition">
        <h3>我们没有照搬的部分</h3>
        <p>没有照搬它的市场值选池、daily 级别组合框架、risk-off 总控、hedging 执行层，也没有把“分数越高越强”当成默认真理。Rank151 只提炼出一个更窄、更诚实的 shared gate。</p>
      </div>
    </div>
    <div class="table-wrap" style="margin-top:12px;">
      <table>
        <thead><tr><th>来源层</th><th>原始来源</th><th>Rank151 本地化</th></tr></thead>
        <tbody>
          <tr><td>信号本体</td><td>EWMAC + breakout 共同驱动趋势仓位</td><td>只保留 <code>align_score</code> 的解释层，把它读成 gate，而不是独立 raw alpha</td></tr>
          <tr><td>仓位逻辑</td><td>continuous positioning，仓位随分数变化</td><td>先简化成 <code>band-pass</code>：中段放行，极端尾部分数降权或 veto</td></tr>
          <tr><td>市场范围</td><td>高流动性加密资产组合</td><td>先用 BTC/ETH/SOL 15m 的最小可复验切口</td></tr>
          <tr><td>风险层</td><td>risk-off filter、execution optimization、hedging</td><td>暂不一并搬运，先单独验证 gate 是否真的有信息量</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="section" id="math">
    <h2>IC 与数理逻辑</h2>
    <p>这条线最容易被误读的地方就在这里。<b>如果你把 align_score 当成“越大越好”的单调因子来算 IC，它并不好。</b> 但这并不和研究结论冲突，因为 Rank151 的 thesis 本来就不是单调排序，而是 <b>中段优于两端的 band-pass</b>。</p>
    <div class="grid">
      <div class="card"><div class="k">Pooled monotonic rho</div><div class="v">{fmt_num(float(metrics["pooled_align_rho"]), 3)}</div><div class="s">align_score 对 signed_bps 的整体 Spearman，接近 0 且偏负</div></div>
      <div class="card"><div class="k">Cross-sectional IC mean</div><div class="v">{fmt_num(float(metrics["cs_ic_mean"]), 3)}</div><div class="s">只在同一时刻 >=3 资产同时有事件时计算；这里不强</div></div>
      <div class="card"><div class="k">Cross-sectional IR</div><div class="v">{fmt_num(float(metrics["cs_ic_ir"]), 3)}</div><div class="s">这说明它不应被当作标准单调 rank 来读</div></div>
      <div class="card"><div class="k">Center-proximity rho</div><div class="v">{fmt_num(float(metrics["pooled_center_rho"]), 3)}</div><div class="s">把“越接近中段越好”编码后，方向变成正值</div></div>
    </div>
    <div class="note">最诚实的说法是：Rank151 的“IC”更适合当成 <b>反单调证明</b>。它告诉你，直接把强趋势尾部当作高 rank 去追，是错的；这条线真正有信息量的，是“不要追太极端”的带通结构。</div>
    <img class="chart" src="{links['chart_png']}" alt="Rank151 band-pass profile chart" />
    <div class="metric-row" style="margin-top:12px;">
      <span class="metric-chip"><b>baseline</b>{fmt_num(float(summary_map['baseline']['mean_bps']), 2)} bps</span>
      <span class="metric-chip"><b>hard-positive</b>{fmt_num(float(summary_map['hard_positive']['mean_bps']), 2)} bps</span>
      <span class="metric-chip"><b>band-pass</b>{fmt_num(float(summary_map['band_pass']['mean_bps']), 2)} bps</span>
      <span class="metric-chip"><b>tail extremes</b>{fmt_num(float(summary_map['tail_extremes']['mean_bps']), 2)} bps</span>
      <span class="metric-chip"><b>q20</b>{fmt_num(float(metrics['q20']), 3)}</span>
      <span class="metric-chip"><b>q80</b>{fmt_num(float(metrics['q80']), 3)}</span>
    </div>
    <p>在本地 quickcheck 里，band-pass 组均值约 <b>{fmt_num(float(summary_map['band_pass']['mean_bps']), 2)} bps</b>，而两端极值组约 <b>{fmt_num(float(summary_map['tail_extremes']['mean_bps']), 2)} bps</b>。这就是为什么这条线更应该展示成“结构解释 + 分组比较”，而不是误导成单一 IC 排名冠军。</p>
  </div>

  <div class="section">
    <h2>本地审计链路</h2>
    {stage_timeline(metrics)}
    <div class="table-wrap" style="margin-top:12px;">
      {slice_table_html(admission_slices, admission_assets)}
    </div>
  </div>

  <div class="section" id="verdict">
    <h2>当前最诚实的 verdict</h2>
    <div class="two">
      <div class="definition">
        <h3>它是什么</h3>
        <p>把 EMA / breakout 对齐度当作一个带通型仓位闸门：让中等强度的延续 setup 更大声，而不是默认追最极端、最容易 late-chase 的尾部分数。</p>
      </div>
      <div class="definition">
        <h3>它不是什么</h3>
        <ul>
          <li>不是独立 raw alpha。</li>
          <li>不是“分数越高越该追”的单调趋势因子。</li>
          <li>不是整套 <code>crypto-trend-follow</code> 系统的完整移植。</li>
          <li>不是已经完成 raw-bar 在线重算的 live engine。</li>
        </ul>
      </div>
    </div>
    <p>所以这页的结论不是“Rank151 的 IC 很高”，而是：<b>Rank151 把一个来源仓库里的 continuous-positioning 思路，翻译成了一个更适合 desk 的 band-pass gate；它的价值来自读法被修正，而不是来自单调排序被放大。</b></p>
  </div>

  <div class="section" id="links">
    <h2>证据链接</h2>
    <ul>
      <li><a href="{links['source_repo']}">原始来源仓库：nicolasdd1996 / crypto-trend-follow</a></li>
      <li><a href="{links['digest_reading']}">本地 digest：别把 EMA/Breakout 分数越高当越好</a></li>
      <li><a href="{links['factor_report']}">Rank151 因子页</a></li>
      <li><a href="{links['paper_runner']}">Rank151 paper runner 页面</a></li>
      <li><a href="{links['launch_reading']}">launch admission 拆页</a></li>
      <li><a href="{links['rolling_reading']}">rolling split 拆页</a></li>
      <li><a href="{links['intake_csv']}">source intake card.csv</a></li>
      <li><a href="{links['runner_csv']}">paper runner status.csv</a></li>
      <li><a href="{links['summary_json']}">本页摘要 JSON</a></li>
    </ul>
  </div>
</div>
</body>
</html>"""


def main() -> int:
    ensure_dirs()
    metrics = load_metrics()
    build_chart(metrics)

    summary_payload = {
        "generated_at": metrics["generated_at"],
        "q20": metrics["q20"],
        "q80": metrics["q80"],
        "pooled_align_rho": metrics["pooled_align_rho"],
        "pooled_center_rho": metrics["pooled_center_rho"],
        "cross_sectional_ic_n": metrics["cs_ic_n"],
        "cross_sectional_ic_mean": metrics["cs_ic_mean"],
        "cross_sectional_ic_ir": metrics["cs_ic_ir"],
        "band_pass_mean_bps": float(metrics["summary_map"]["band_pass"]["mean_bps"]),  # type: ignore[index]
        "tail_extreme_mean_bps": float(metrics["summary_map"]["tail_extremes"]["mean_bps"]),  # type: ignore[index]
        "paper_stage": metrics["runner"]["stage"],  # type: ignore[index]
    }
    OUT_JSON.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    ALIAS_OUT_JSON.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    OUT_HTML.write_text(render_page(metrics, "../../artifacts/interview_showcase"), encoding="utf-8")
    ALIAS_OUT_HTML.write_text(render_page(metrics, "../../artifacts/factor_research_library"), encoding="utf-8")
    print(f"[ok] wrote {OUT_HTML.relative_to(ROOT)}")
    print(f"[ok] wrote {ALIAS_OUT_HTML.relative_to(ROOT)}")
    print(f"[ok] wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
