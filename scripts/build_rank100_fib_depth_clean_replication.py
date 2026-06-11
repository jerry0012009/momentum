#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "fib_zone_depth_proxy"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank100_fib_depth_shallow_mid_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank100_fib_depth_shallow_mid_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank100_fib_depth_shallow_mid_clean_replication.html"

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

BAND_TO_BUCKET = {
    "38_50": "shallow_mid_38_62",
    "50_62": "shallow_mid_38_62",
    "62_71": "deep_62_79",
    "71_79": "deep_62_79",
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

    trade_log = pd.read_csv(SOURCE_DIR / "trade_log.csv")
    overall = pd.read_csv(SOURCE_DIR / "overall_summary.csv")
    asset = pd.read_csv(SOURCE_DIR / "asset_summary.csv")
    bucket = pd.read_csv(SOURCE_DIR / "depth_bucket_summary.csv")
    snapshot = json.loads((SOURCE_DIR / "summary_snapshot.json").read_text(encoding="utf-8"))

    trade_log["depth_bucket"] = trade_log["band"].map(BAND_TO_BUCKET)

    bucket_asset = (
        trade_log.groupby(["depth_bucket", "asset"], sort=False)
        .agg(
            trades=("net_ret", "size"),
            avg_net_ret=("net_ret", "mean"),
            win_rate=("net_ret", lambda s: (s > 0).mean()),
            success_rate=("success", "mean"),
            total_return=("net_ret", lambda s: (1.0 + s).prod() - 1.0),
            median_bars_to_touch=("bars_to_touch", "median"),
            stop_rate=("exit_reason", lambda s: (s == "stop_100").mean()),
            time_stop_rate=("exit_reason", lambda s: (s == "time_stop").mean()),
            tp_rate=("exit_reason", lambda s: (s == "tp_0").mean()),
        )
        .reset_index()
        .sort_values(["depth_bucket", "asset"])
        .reset_index(drop=True)
    )

    bucket = bucket.copy().sort_values(["depth_bucket"]).reset_index(drop=True)
    bucket["stop_rate"] = bucket["depth_bucket"].map(
        trade_log.groupby("depth_bucket")["exit_reason"].apply(lambda s: float((s == "stop_100").mean())).to_dict()
    )
    bucket["time_stop_rate"] = bucket["depth_bucket"].map(
        trade_log.groupby("depth_bucket")["exit_reason"].apply(lambda s: float((s == "time_stop").mean())).to_dict()
    )
    bucket["tp_rate"] = bucket["depth_bucket"].map(
        trade_log.groupby("depth_bucket")["exit_reason"].apply(lambda s: float((s == "tp_0").mean())).to_dict()
    )

    band_summary = overall.copy().sort_values(["band"]).reset_index(drop=True)
    band_asset = asset.copy().sort_values(["band", "asset"]).reset_index(drop=True)

    shallow = bucket.loc[bucket["depth_bucket"] == "shallow_mid_38_62"].iloc[0]
    deep = bucket.loc[bucket["depth_bucket"] == "deep_62_79"].iloc[0]
    best_band = band_summary.sort_values(["avg_net_ret", "success_rate"], ascending=[False, False]).iloc[0]

    verdict = "park / evidence pool"
    verdict_reason = (
        "浅中回踩（38-62）确实比深回踩（62-79）更少亏、触达更快、stop 更少，"
        "但两档在成本后仍都没有转成足够硬的正向 edge。"
        "更诚实的 desk 读法是：把它收口成 generic retrace ordering（默认浅中优先，深回踩只作条件触发），"
        "而不是继续把 Fib 深度当独立 active Scout 候选。"
    )

    verdict_summary = pd.DataFrame([
        {
            "rank": 100,
            "candidate": "Fib-depth shallow-mid admission gate",
            "current_hard_verdict": verdict,
            "desk_readthrough": "generic retrace ordering only: prefer 38-62 before 62-79",
            "next_step": "切 Rank 101 / 3-step volume dry-down long-bias gate 做 source intake",
            "shallow_avg_net_ret": shallow["avg_net_ret"],
            "deep_avg_net_ret": deep["avg_net_ret"],
            "shallow_success_rate": shallow["success_rate"],
            "deep_success_rate": deep["success_rate"],
            "shallow_stop_rate": shallow["stop_rate"],
            "deep_stop_rate": deep["stop_rate"],
            "best_single_band": best_band["band"],
            "best_single_band_avg_net_ret": best_band["avg_net_ret"],
            "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    ])

    bucket.to_csv(ART_DIR / "depth_bucket_summary.csv", index=False)
    bucket_asset.to_csv(ART_DIR / "depth_bucket_asset_summary.csv", index=False)
    band_summary.to_csv(ART_DIR / "band_summary.csv", index=False)
    band_asset.to_csv(ART_DIR / "band_asset_summary.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    bucket_table = render_table(
        bucket[["depth_bucket", "trades", "avg_net_ret", "win_rate", "success_rate", "total_return", "median_bars_to_touch", "stop_rate", "tp_rate", "time_stop_rate"]],
        percent_cols={"win_rate", "success_rate", "total_return", "stop_rate", "tp_rate", "time_stop_rate"},
        bps_cols={"avg_net_ret"},
        digits_cols={"trades": 0, "median_bars_to_touch": 1},
    )
    bucket_asset_table = render_table(
        bucket_asset[["depth_bucket", "asset", "trades", "avg_net_ret", "win_rate", "success_rate", "total_return", "median_bars_to_touch", "stop_rate"]],
        percent_cols={"win_rate", "success_rate", "total_return", "stop_rate"},
        bps_cols={"avg_net_ret"},
        digits_cols={"trades": 0, "median_bars_to_touch": 1},
    )
    band_table = render_table(
        band_summary[["band", "trades", "avg_net_ret", "win_rate", "success_rate", "total_return", "median_bars_to_touch", "avg_anchor_range_pct"]],
        percent_cols={"win_rate", "success_rate", "total_return", "avg_anchor_range_pct"},
        bps_cols={"avg_net_ret"},
        digits_cols={"trades": 0, "median_bars_to_touch": 1},
    )

    factor_body = f"""
<h1>Rank 100 · Fib-depth shallow-mid admission gate · minimal clean replication</h1>
<p class='muted'>生成时间：{escape(verdict_summary.iloc[0]['generated_at_utc'])} · 数据复用自 <code>reports/artifacts/quant_digests/fib_zone_depth_proxy/</code></p>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li><strong>浅中桶 38-62</strong>：平均每笔 <strong>{bps(shallow['avg_net_ret'])}</strong>，成功率 <strong>{pct(shallow['success_rate'])}</strong>，stop 率 <strong>{pct(shallow['stop_rate'])}</strong>，中位触达 <strong>{num(shallow['median_bars_to_touch'], 1)}</strong> 根 bar。</li>
    <li><strong>深桶 62-79</strong>：平均每笔 <strong>{bps(deep['avg_net_ret'])}</strong>，成功率 <strong>{pct(deep['success_rate'])}</strong>，stop 率 <strong>{pct(deep['stop_rate'])}</strong>，中位触达 <strong>{num(deep['median_bars_to_touch'], 1)}</strong> 根 bar。</li>
    <li>最不差的单带是 <strong>{escape(str(best_band['band']))}</strong>，但也只有 <strong>{bps(best_band['avg_net_ret'])}</strong>；这更像 admission 排序，不像独立 alpha。</li>
  </ul>
</div>
<div class='card'>
  <h2>深浅两桶汇总</h2>
  {bucket_table}
</div>
<div class='card'>
  <h2>按资产拆开（两桶）</h2>
  {bucket_asset_table}
</div>
<div class='card'>
  <h2>按 Fib 细带拆开</h2>
  {band_table}
</div>
<div class='card'>
  <h2>排班含义</h2>
  <p>这轮已经给出 hard verdict：Rank 100 不再继续占 clean-replication 队列。后续只保留一条 desk 读法——<strong>默认浅中回踩优先，深回踩只在更强 trend/context 下条件放行</strong>。</p>
  <p>下一轮若 <code>EMA</code> 仍 <code>waiting_not_due</code>，默认切去 <strong>Rank 101 / 3-step volume dry-down long-bias gate</strong> 做 source intake，而不是继续打磨 Rank 100 的 admission 文案。</p>
  <p><a href='../../reading/repo_scout/rank100_fib_depth_shallow_mid_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank100_fib_depth_shallow_mid_source_intake.html'>source intake</a></p>
</div>
"""

    reading_body = f"""
<h1>Rank 100 · Fib-depth shallow-mid admission gate · clean replication write-up</h1>
<p class='muted'>这轮没有追新 bar，只把已有 15m 公开代理样本重新收口成 desk 能执行的结论：Fib 回踩默认到底该先浅中，还是继续迷信深回踩。</p>
<div class='card'>
  <p><strong>主结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(verdict_reason)}</p>
  <ul>
    <li>浅中桶 <strong>38-62</strong> 明显优于深桶 <strong>62-79</strong>：更少亏、触达更快、stop 更少。</li>
    <li>但浅中桶本身也还没转成足够硬的正 alpha，所以不该升到 P2 / paper candidate。</li>
    <li>因此更诚实的收口不是“深回踩更稳”，也不是“浅中已经能单飞”，而是：<strong>把 Fib 深度退回 generic retrace ordering</strong>。</li>
  </ul>
</div>
<div class='card'>
  <h2>对 desk 的直接含义</h2>
  <p>如果后续 Fib / EMA / breakout-retest 线还要用到深度门，默认先把 <code>38-62</code> 当常态 admission，把 <code>62-79</code> 改成更强 trend/context 才开放的条件分支。</p>
  <p>但 Rank 100 这条线本身已经给出 hard verdict，不再继续占 Scout 主资源；下一轮应切 <strong>Rank 101</strong>。</p>
  <p><a href='../../factors/scout_rank100_fib_depth_shallow_mid_15m/report.html'>查看 factor 页面</a> · <a href='rank100_fib_depth_shallow_mid_source_intake.html'>回到 source intake</a></p>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 100 Fib-depth shallow-mid admission gate", factor_body)
    write_html(READING_PATH, "Rank 100 Fib-depth shallow-mid clean replication", reading_body)

    print(f"[ok] wrote {ART_DIR / 'depth_bucket_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'depth_bucket_asset_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'band_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'verdict_summary.csv'}")
    print(f"[ok] wrote {SITE_DIR / 'report.html'}")
    print(f"[ok] wrote {READING_PATH}")


if __name__ == "__main__":
    main()
