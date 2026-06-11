#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "zenoclaw_clv_proxy"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank99_clv_asymmetric_admission_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank99_clv_asymmetric_admission_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank99_clv_asymmetric_admission_clean_replication.html"

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

FILTER_LABELS = {
    ("short", "baseline"): "short_baseline",
    ("short", "clv70"): "short_clv070",
    ("short", "clv80"): "short_clv080",
    ("short", "clv70_vol15"): "short_clv070_plus_volume",
    ("short", "vol15"): "short_volume_only",
    ("long", "baseline"): "long_baseline",
    ("long", "clv70"): "long_clv070_only",
    ("long", "vol15"): "long_volume_only",
    ("long", "clv70_vol15"): "long_volume_plus_clv",
    ("long", "clv80"): "long_clv080_only",
}


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
    snapshot = json.loads((SOURCE_DIR / "summary_snapshot.json").read_text(encoding="utf-8"))

    overall["variant"] = overall.apply(lambda r: FILTER_LABELS[(r["side"], r["filter"])], axis=1)
    asset["variant"] = asset.apply(lambda r: FILTER_LABELS[(r["side"], r["filter"])], axis=1)

    keep_variants = [
        "short_baseline",
        "short_clv070",
        "short_clv080",
        "short_clv070_plus_volume",
        "long_baseline",
        "long_clv070_only",
        "long_volume_only",
        "long_volume_plus_clv",
    ]
    order = {name: i for i, name in enumerate(keep_variants)}

    overall = overall[overall["variant"].isin(keep_variants)].copy()
    asset = asset[asset["variant"].isin(keep_variants)].copy()
    overall["sort_key"] = overall["variant"].map(order)
    asset["sort_key"] = asset["variant"].map(order)
    overall = overall.sort_values(["sort_key"]).drop(columns=["sort_key", "side", "filter"])
    asset = asset.sort_values(["asset" if "asset" in asset.columns else "symbol", "sort_key"]).drop(columns=["sort_key", "side", "filter"])

    overall = overall.rename(columns={
        "mean_n": "mean_trades",
        "mean_retention": "mean_trade_count_retention",
        "mean_net_ret_h4": "mean_avg_net_ret_h4",
    })
    asset = asset.rename(columns={
        "symbol": "asset",
        "base_n": "baseline_trades",
        "n": "trades",
        "retention": "trade_count_retention",
    })

    short_base = overall.loc[overall["variant"] == "short_baseline"].iloc[0]
    short_clv70 = overall.loc[overall["variant"] == "short_clv070"].iloc[0]
    short_clv80 = overall.loc[overall["variant"] == "short_clv080"].iloc[0]
    short_combo = overall.loc[overall["variant"] == "short_clv070_plus_volume"].iloc[0]
    long_base = overall.loc[overall["variant"] == "long_baseline"].iloc[0]
    long_clv = overall.loc[overall["variant"] == "long_clv070_only"].iloc[0]
    long_vol = overall.loc[overall["variant"] == "long_volume_only"].iloc[0]
    long_combo = overall.loc[overall["variant"] == "long_volume_plus_clv"].iloc[0]

    verdict = "keep_P1 / evidence_pool"
    verdict_reason = (
        "short 侧 strict CLV 把 proxy 样本的 after-cost 亏损压缩到接近打平，"
        "但 long 侧 CLV-only 反而更差，volume+CLV 也还没把结果拉正。"
        "更诚实的读法是：CLV 值得作为方向不对称 admission 线索保留，但还不足以升到 P2。"
    )

    verdict_summary = pd.DataFrame([
        {
            "rank": 99,
            "candidate": "CLV asymmetric admission layer",
            "current_hard_verdict": verdict,
            "next_step": "1 个 truly verdict-changing 的 Light Stability Pack（默认时间稳定性）",
            "short_baseline_avg_net_ret_h4": short_base["mean_avg_net_ret_h4"],
            "short_clv080_avg_net_ret_h4": short_clv80["mean_avg_net_ret_h4"],
            "short_clv070_plus_volume_avg_net_ret_h4": short_combo["mean_avg_net_ret_h4"],
            "long_baseline_avg_net_ret_h4": long_base["mean_avg_net_ret_h4"],
            "long_clv070_only_avg_net_ret_h4": long_clv["mean_avg_net_ret_h4"],
            "long_volume_only_avg_net_ret_h4": long_vol["mean_avg_net_ret_h4"],
            "long_volume_plus_clv_avg_net_ret_h4": long_combo["mean_avg_net_ret_h4"],
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    ])

    overall.to_csv(ART_DIR / "overall_summary.csv", index=False)
    asset.to_csv(ART_DIR / "asset_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    overview_table = render_table(
        overall[["variant", "mean_trades", "mean_trade_count_retention", "mean_avg_net_ret_h4", "mean_median_net_ret_h4", "mean_win_rate_h4", "positive_asset_ratio"]],
        percent_cols={"mean_trade_count_retention", "mean_win_rate_h4", "positive_asset_ratio"},
        bps_cols={"mean_avg_net_ret_h4", "mean_median_net_ret_h4"},
        digits_cols={"mean_trades": 1},
    )
    asset_table = render_table(
        asset[["asset", "variant", "trades", "trade_count_retention", "mean_net_ret_h4", "median_net_ret_h4", "win_rate_h4", "avg_aligned_clv", "avg_vol_ratio"]],
        percent_cols={"trade_count_retention", "win_rate_h4", "avg_aligned_clv"},
        bps_cols={"mean_net_ret_h4", "median_net_ret_h4"},
        digits_cols={"trades": 0, "avg_vol_ratio": 2},
    )

    factor_body = f"""
<h1>Rank 99 · CLV asymmetric admission layer · minimal clean replication</h1>
<p class='muted'>生成时间：{escape(verdict_summary.iloc[0]['generated_at_utc'])} · 数据复用自 <code>reports/artifacts/quant_digests/zenoclaw_clv_proxy/</code></p>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>short baseline = <strong>{bps(short_base['mean_avg_net_ret_h4'])}</strong> → short CLV80 = <strong>{bps(short_clv80['mean_avg_net_ret_h4'])}</strong>，保留率 <strong>{pct(short_clv80['mean_trade_count_retention'])}</strong>。</li>
    <li>short CLV70+volume = <strong>{bps(short_combo['mean_avg_net_ret_h4'])}</strong>，positive-asset-ratio = <strong>{pct(short_combo['positive_asset_ratio'])}</strong>。</li>
    <li>long baseline = <strong>{bps(long_base['mean_avg_net_ret_h4'])}</strong>；long CLV-only = <strong>{bps(long_clv['mean_avg_net_ret_h4'])}</strong>；long volume-only = <strong>{bps(long_vol['mean_avg_net_ret_h4'])}</strong>；long volume+CLV = <strong>{bps(long_combo['mean_avg_net_ret_h4'])}</strong>。</li>
  </ul>
</div>
<div class='card'>
  <h2>最小 clean replication 汇总</h2>
  {overview_table}
</div>
<div class='card'>
  <h2>按资产拆开</h2>
  {asset_table}
</div>
<div class='card'>
  <h2>下一步</h2>
  <p>如果后续继续认领 Rank 99，默认只给 <strong>1 个 truly verdict-changing 的 Light Stability Pack</strong>，先做时间稳定性：检查 short strict-CLV 改善是不是只剩局部 pocket，同时确认 long 侧 volume+CLV 是否仍旧不够硬。</p>
  <p><a href='../../reading/repo_scout/rank99_clv_asymmetric_admission_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank99_clv_asymmetric_admission_source_intake.html'>source intake</a></p>
</div>
"""

    reading_body = f"""
<h1>Rank 99 · CLV asymmetric admission layer · clean replication write-up</h1>
<p class='muted'>本轮没有追新 bar，而是复用已冻结的公开代理样本，只回答一个最小问题：CLV 是否真值得作为方向不对称的 admission layer。</p>
<div class='card'>
  <p><strong>主结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>short 侧 strict CLV 值得保留：baseline <strong>{bps(short_base['mean_avg_net_ret_h4'])}</strong>，CLV80 到 <strong>{bps(short_clv80['mean_avg_net_ret_h4'])}</strong>。</li>
    <li>但 long 侧不能把 close-near-high 当 continuation 充分条件：long CLV-only 比 baseline 更差。</li>
    <li>所以这轮不是 promote to P2，而是把它收口成 <strong>P1 weak candidate / evidence pool</strong>。</li>
  </ul>
</div>
<div class='card'>
  <h2>排班含义</h2>
  <p>下一轮若 <code>EMA</code> 仍 <code>waiting_not_due</code>，Rank 99 默认不再重跑 clean replication；只允许给 1 个 truly verdict-changing 的时间稳定性检查，直接回答 keep_P1 / promote_to_P2 / park。</p>
  <p><a href='../../factors/scout_rank99_clv_asymmetric_admission_15m/report.html'>查看 factor 页面</a> · <a href='rank99_clv_asymmetric_admission_source_intake.html'>回到 source intake</a></p>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 99 CLV asymmetric admission layer", factor_body)
    write_html(READING_PATH, "Rank 99 CLV asymmetric admission layer clean replication", reading_body)

    print(f"[ok] wrote {ART_DIR / 'overall_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'asset_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'verdict_summary.csv'}")
    print(f"[ok] wrote {SITE_DIR / 'report.html'}")
    print(f"[ok] wrote {READING_PATH}")


if __name__ == "__main__":
    main()
