#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "abnormal_volume_pullback_proxy"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank101_volume_drydown_long_bias_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank101_volume_drydown_long_bias_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank101_volume_drydown_long_bias_clean_replication.html"

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1160px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.warn { color:#92400e; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def bps(v) -> str:
    if pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.2f} bps"


def num(v, digits: int = 2) -> str:
    if pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    digits_cols = digits_cols or {}
    head = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            val = row[col]
            if col in percent_cols:
                txt = pct(val)
            elif col in bps_cols:
                txt = bps(val)
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                txt = num(val, digits_cols.get(col, 2))
            else:
                txt = str(val)
            cells.append(f'<td>{escape(txt)}</td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    overall = pd.read_csv(SOURCE_DIR / "overall_summary.csv")
    asset = pd.read_csv(SOURCE_DIR / "asset_summary.csv")
    trade_log = pd.read_csv(SOURCE_DIR / "trade_log.csv")
    snapshot = json.loads((SOURCE_DIR / "summary_snapshot.json").read_text(encoding="utf-8"))

    long_overall = overall.loc[overall["side"] == "long"].copy().sort_values("variant").reset_index(drop=True)
    short_overall = overall.loc[overall["side"] == "short"].copy().sort_values("variant").reset_index(drop=True)
    long_asset = asset.loc[asset["side"] == "long"].copy().sort_values(["variant", "asset"]).reset_index(drop=True)
    short_asset = asset.loc[asset["side"] == "short"].copy().sort_values(["variant", "asset"]).reset_index(drop=True)

    dv3_lv80 = long_overall.loc[long_overall["variant"] == "dv3_lv80"].iloc[0]
    baseline = long_overall.loc[long_overall["variant"] == "baseline"].iloc[0]
    lv80 = long_overall.loc[long_overall["variant"] == "lv80"].iloc[0]
    dv3 = long_overall.loc[long_overall["variant"] == "dv3"].iloc[0]
    short_dv3_lv80 = short_overall.loc[short_overall["variant"] == "dv3_lv80"].iloc[0]

    long_asset_positive = long_asset.loc[(long_asset["variant"] == "dv3_lv80") & (long_asset["avg_net_ret_h8"] > 0)]
    verdict = "park / evidence pool"
    verdict_reason = (
        "`3-step volume dry-down + low-volume` 在 long side 的确把平均收益从 baseline 的负值拉到近乎持平，"
        "并把正资产占比抬到 2/3；但它的 trade_count_retention 只剩约 3.4%，"
        "BTC 口袋仍为负，且 short 镜像结果明显更差。"
        "这更像一个可记住的 long-side hold-quality / short-veto 语义，"
        "还不够诚实到能独立升格成 paper candidate 或 narrow paper pilot。"
    )

    verdict_summary = pd.DataFrame([
        {
            "rank": 101,
            "candidate": "3-step volume dry-down long-bias gate",
            "current_hard_verdict": verdict,
            "desk_readthrough": "keep as long-side hold-quality / short-veto note only",
            "next_step": "按 7.10 回 fresh source pool，再认领 1 条 5m/15m crypto paper-repo intake",
            "long_baseline_avg_net_ret_h8": baseline["avg_net_ret_h8"],
            "long_dv3_avg_net_ret_h8": dv3["avg_net_ret_h8"],
            "long_lv80_avg_net_ret_h8": lv80["avg_net_ret_h8"],
            "long_dv3_lv80_avg_net_ret_h8": dv3_lv80["avg_net_ret_h8"],
            "long_dv3_lv80_retention": dv3_lv80["retention_vs_baseline"],
            "long_dv3_lv80_win_rate": dv3_lv80["win_rate"],
            "long_dv3_lv80_positive_asset_ratio": dv3_lv80["positive_asset_ratio"],
            "short_dv3_lv80_avg_net_ret_h8": short_dv3_lv80["avg_net_ret_h8"],
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    ])

    long_overall.to_csv(ART_DIR / "long_overall_summary.csv", index=False)
    short_overall.to_csv(ART_DIR / "short_overall_summary.csv", index=False)
    long_asset.to_csv(ART_DIR / "long_asset_summary.csv", index=False)
    short_asset.to_csv(ART_DIR / "short_asset_summary.csv", index=False)
    trade_log.to_csv(ART_DIR / "trade_log.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    long_overall_table = render_table(
        long_overall[["variant", "trades", "retention_vs_baseline", "win_rate", "avg_net_ret_h8", "median_net_ret_h8", "positive_asset_ratio"]],
        percent_cols={"retention_vs_baseline", "win_rate", "positive_asset_ratio"},
        bps_cols={"avg_net_ret_h8", "median_net_ret_h8"},
        digits_cols={"trades": 0},
    )
    long_asset_table = render_table(
        long_asset[["variant", "asset", "trades", "win_rate", "avg_net_ret_h8", "median_net_ret_h8"]],
        percent_cols={"win_rate"},
        bps_cols={"avg_net_ret_h8", "median_net_ret_h8"},
        digits_cols={"trades": 0},
    )
    short_overall_table = render_table(
        short_overall[["variant", "trades", "retention_vs_baseline", "win_rate", "avg_net_ret_h8", "median_net_ret_h8", "positive_asset_ratio"]],
        percent_cols={"retention_vs_baseline", "win_rate", "positive_asset_ratio"},
        bps_cols={"avg_net_ret_h8", "median_net_ret_h8"},
        digits_cols={"trades": 0},
    )

    positive_assets = ", ".join(long_asset_positive["asset"].tolist()) if not long_asset_positive.empty else "无"

    factor_body = f"""
<h1>Rank 101 · 3-step volume dry-down long-bias gate · minimal clean replication</h1>
<p class='muted'>生成时间：{escape(verdict_summary.iloc[0]['generated_at_utc'])} · 复用 <code>reports/artifacts/quant_digests/abnormal_volume_pullback_proxy/</code> 的既有 15m 代理样本</p>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li><strong>long / baseline</strong>：平均每笔 <strong>{bps(baseline['avg_net_ret_h8'])}</strong>，胜率 <strong>{pct(baseline['win_rate'])}</strong>。</li>
    <li><strong>long / dv3_lv80</strong>：平均每笔 <strong>{bps(dv3_lv80['avg_net_ret_h8'])}</strong>，胜率 <strong>{pct(dv3_lv80['win_rate'])}</strong>，但保留率只剩 <strong>{pct(dv3_lv80['retention_vs_baseline'])}</strong>。</li>
    <li><strong>跨资产</strong>：dv3_lv80 只有 <strong>{positive_assets}</strong> 为正，BTC 仍是负 pocket。</li>
    <li><strong>short 镜像</strong>：dv3_lv80 反而恶化到 <strong>{bps(short_dv3_lv80['avg_net_ret_h8'])}</strong>；因此它不该被当成 shared short admission。</li>
  </ul>
</div>
<div class='card'>
  <h2>Long side 变体对比</h2>
  {long_overall_table}
</div>
<div class='card'>
  <h2>Long side 按资产拆开</h2>
  {long_asset_table}
</div>
<div class='card'>
  <h2>Short side（只作镜像诚实检查）</h2>
  {short_overall_table}
</div>
<div class='card'>
  <h2>排班含义</h2>
  <p>这轮已经把 Rank 101 收成 hard verdict：<strong>它可以保留为 long-side pullback absorption 的执行语义，但不继续占 active Scout 主资源</strong>。</p>
  <p>因此下一轮若 <code>EMA</code> 仍 <code>waiting_not_due</code>，默认应按 <code>7.10</code> 回 fresh source pool，再认领 1 条新的 <strong>5m / 15m crypto paper-repo source</strong>；而不是继续磨 Rank 101 的 admission 包装。</p>
  <p><a href='../../reading/repo_scout/rank101_volume_drydown_long_bias_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank101_volume_drydown_long_bias_source_intake.html'>source intake</a></p>
</div>
"""

    reading_body = f"""
<h1>Rank 101 · 3-step volume dry-down long-bias gate · clean replication write-up</h1>
<p class='muted'>这轮没有追新 bar，也没有再扩策略骨架，只把已有代理快检重新收口成 desk 能执行的结论。</p>
<div class='card'>
  <p><strong>主结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>它对 <strong>long-side pullback / retest / continuation</strong> 确实有一点吸收质量语义：比 baseline 少亏，也让 ETH / SOL 转成正 pocket。</li>
    <li>但它的代价很高：trade retention 只剩约 <strong>{pct(dv3_lv80['retention_vs_baseline'])}</strong>，而且 BTC 仍没过门。</li>
    <li>更关键的是，<strong>short 镜像明显更差</strong>，所以 desk 不该把它误写成 breakout-short 的共享 admission。</li>
  </ul>
</div>
<div class='card'>
  <h2>对 desk 的直接含义</h2>
  <p>后续如果 Fib retest / EMA continuation 还想借这条语义，最诚实的写法是：<strong>把它保留成 long-side hold-quality gate 或 short-veto note</strong>。</p>
  <p>但 Rank 101 本身已经不再值得继续占 clean-replication 队列；下一轮默认应切回 fresh source intake，而不是继续在这条线上追求更漂亮的文案。</p>
  <p><a href='../../factors/scout_rank101_volume_drydown_long_bias_15m/report.html'>查看 factor 页面</a> · <a href='rank101_volume_drydown_long_bias_source_intake.html'>回到 source intake</a></p>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 101 volume dry-down long-bias gate", factor_body)
    write_html(READING_PATH, "Rank 101 volume dry-down long-bias clean replication", reading_body)

    print(f"[ok] wrote {ART_DIR / 'verdict_summary.csv'}")
    print(f"[ok] wrote {SITE_DIR / 'report.html'}")
    print(f"[ok] wrote {READING_PATH}")


if __name__ == "__main__":
    main()
