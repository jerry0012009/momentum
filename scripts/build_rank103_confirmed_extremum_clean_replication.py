#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "reports" / "artifacts" / "quant_digests" / "confirmed_extremum_anchor_proxy"
DEPTH_REF = ROOT / "reports" / "artifacts" / "scout_rank100_fib_depth_shallow_mid_15m" / "band_summary.csv"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank103_confirmed_extremum_honest_fib_anchor_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank103_confirmed_extremum_honest_fib_anchor_15m"
READING_PATH = ROOT / "reports" / "site" / "reading" / "repo_scout" / "rank103_confirmed_extremum_honest_fib_anchor_clean_replication.html"

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

ADMIT_BUCKETS = ["38.2-50", "50-61.8", "61.8-79"]
BUCKET_ORDER = ["<38.2", "38.2-50", "50-61.8", "61.8-79", ">=79"]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def pct(v, digits: int = 2) -> str:
    if pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def bps(v, digits: int = 2) -> str:
    if pd.isna(v):
        return "-"
    return f"{float(v) * 10000:.{digits}f} bps"


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
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    rows: list[str] = []
    for _, row in df.iterrows():
        cells: list[str] = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif col in bps_cols:
                text = bps(value)
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


def bucket(frac: float) -> str:
    if frac < 0.382:
        return "<38.2"
    if frac < 0.5:
        return "38.2-50"
    if frac < 0.618:
        return "50-61.8"
    if frac < 0.79:
        return "61.8-79"
    return ">=79"


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    event = pd.read_csv(SOURCE_DIR / "event_summary.csv")
    snapshot = json.loads((SOURCE_DIR / "summary_snapshot.json").read_text(encoding="utf-8"))
    usable = event.dropna(subset=["frac_prov", "frac_conf"]).copy()
    usable["bucket_prov"] = usable["frac_prov"].map(bucket)
    usable["bucket_conf"] = usable["frac_conf"].map(bucket)
    usable["admit_prov"] = usable["bucket_prov"].isin(ADMIT_BUCKETS)
    usable["admit_conf"] = usable["bucket_conf"].isin(ADMIT_BUCKETS)
    usable["bucket_shift"] = usable["bucket_prov"] != usable["bucket_conf"]
    usable["promoted_to_admit"] = (~usable["admit_prov"]) & usable["admit_conf"]
    usable["demoted_out_of_admit"] = usable["admit_prov"] & (~usable["admit_conf"])

    band = pd.read_csv(DEPTH_REF)
    bucket_proxy = pd.DataFrame(
        [
            {
                "depth_bucket": "38.2-50",
                "proxy_avg_net_ret": float(band.loc[band["band"] == "38_50", "avg_net_ret"].iloc[0]),
                "proxy_success_rate": float(band.loc[band["band"] == "38_50", "success_rate"].iloc[0]),
                "proxy_trades": int(band.loc[band["band"] == "38_50", "trades"].iloc[0]),
            },
            {
                "depth_bucket": "50-61.8",
                "proxy_avg_net_ret": float(band.loc[band["band"] == "50_62", "avg_net_ret"].iloc[0]),
                "proxy_success_rate": float(band.loc[band["band"] == "50_62", "success_rate"].iloc[0]),
                "proxy_trades": int(band.loc[band["band"] == "50_62", "trades"].iloc[0]),
            },
            {
                "depth_bucket": "61.8-79",
                "proxy_avg_net_ret": float((band.loc[band["band"].isin(["62_71", "71_79"]), "avg_net_ret"] * band.loc[band["band"].isin(["62_71", "71_79"]), "trades"]).sum() / band.loc[band["band"].isin(["62_71", "71_79"]), "trades"].sum()),
                "proxy_success_rate": float((band.loc[band["band"].isin(["62_71", "71_79"]), "success_rate"] * band.loc[band["band"].isin(["62_71", "71_79"]), "trades"]).sum() / band.loc[band["band"].isin(["62_71", "71_79"]), "trades"].sum()),
                "proxy_trades": int(band.loc[band["band"].isin(["62_71", "71_79"]), "trades"].sum()),
            },
        ]
    )
    proxy_ret = bucket_proxy.set_index("depth_bucket")["proxy_avg_net_ret"].to_dict()
    proxy_success = bucket_proxy.set_index("depth_bucket")["proxy_success_rate"].to_dict()

    def anchor_summary(name: str, bucket_col: str, admit_col: str) -> dict[str, object]:
        bucket_share = usable[bucket_col].value_counts(normalize=True).reindex(BUCKET_ORDER).fillna(0.0)
        admitted = usable.loc[usable[admit_col]].copy()
        if not admitted.empty:
            admitted["proxy_avg_net_ret"] = admitted[bucket_col].map(proxy_ret)
            admitted["proxy_success_rate"] = admitted[bucket_col].map(proxy_success)
            proxy_avg_net_ret = admitted["proxy_avg_net_ret"].mean()
            proxy_success_rate = admitted["proxy_success_rate"].mean()
        else:
            proxy_avg_net_ret = float("nan")
            proxy_success_rate = float("nan")
        out = {
            "anchor_variant": name,
            "events": len(usable),
            "admit_rate": usable[admit_col].mean(),
            "bucket_lt_38": bucket_share["<38.2"],
            "bucket_38_50": bucket_share["38.2-50"],
            "bucket_50_61_8": bucket_share["50-61.8"],
            "bucket_61_8_79": bucket_share["61.8-79"],
            "bucket_ge_79": bucket_share[">=79"],
            "proxy_post_cost_expectancy": proxy_avg_net_ret,
            "proxy_success_rate": proxy_success_rate,
        }
        return out

    anchor_compare = pd.DataFrame(
        [
            anchor_summary("provisional_anchor", "bucket_prov", "admit_prov"),
            anchor_summary("confirmed_anchor", "bucket_conf", "admit_conf"),
        ]
    )

    side_rows = []
    for side, group in usable.groupby("side"):
        for name, bucket_col, admit_col in [
            ("provisional_anchor", "bucket_prov", "admit_prov"),
            ("confirmed_anchor", "bucket_conf", "admit_conf"),
        ]:
            admitted = group.loc[group[admit_col]].copy()
            if not admitted.empty:
                admitted["proxy_avg_net_ret"] = admitted[bucket_col].map(proxy_ret)
                proxy_avg_ret = admitted["proxy_avg_net_ret"].mean()
            else:
                proxy_avg_ret = float("nan")
            side_rows.append(
                {
                    "side": side,
                    "anchor_variant": name,
                    "events": len(group),
                    "admit_rate": group[admit_col].mean(),
                    "bucket_shift_rate": group["bucket_shift"].mean(),
                    "promoted_to_admit_rate": group["promoted_to_admit"].mean(),
                    "proxy_post_cost_expectancy": proxy_avg_ret,
                }
            )
    side_summary = pd.DataFrame(side_rows)

    shift_summary = pd.DataFrame(
        [
            {
                "usable_events": len(usable),
                "bucket_shift_rate": usable["bucket_shift"].mean(),
                "promoted_to_admit_rate": usable["promoted_to_admit"].mean(),
                "demoted_out_of_admit_rate": usable["demoted_out_of_admit"].mean(),
                "confirmed_rate_overall": snapshot["confirmed_rate_overall"],
                "median_extra_atr_confirmed": snapshot["extra_atr_quantiles_confirmed"]["0.5"],
                "p75_extra_atr_confirmed": snapshot["extra_atr_quantiles_confirmed"]["0.75"],
                "p90_extra_atr_confirmed": snapshot["extra_atr_quantiles_confirmed"]["0.9"],
                "median_bars_to_confirm": snapshot["bars_to_confirm_quantiles"]["0.5"],
                "p75_bars_to_confirm": snapshot["bars_to_confirm_quantiles"]["0.75"],
                "p90_bars_to_confirm": snapshot["bars_to_confirm_quantiles"]["0.9"],
            }
        ]
    )

    verdict = "park / evidence pool"
    desk_readthrough = (
        "confirmed anchor 确实会把更多事件从 <38.2 推进到可交易的 38-79 回踩带，"
        "但这轮 clean replication 仍只证明它是 measurement correction / honest anchor，"
        "没有证明它已经能单独把 post-cost expectancy 推过门槛。"
    )
    next_step = "切 post-break sign-flip density 的 source intake；只有 fresh source 也 exhausted，才回退旧 evidence pool。"

    verdict_summary = pd.DataFrame(
        [
            {
                "rank": 103,
                "candidate": "confirmed extremum honest fib anchor",
                "current_hard_verdict": verdict,
                "desk_readthrough": desk_readthrough,
                "next_step": next_step,
                "provisional_admit_rate": anchor_compare.loc[anchor_compare["anchor_variant"] == "provisional_anchor", "admit_rate"].iloc[0],
                "confirmed_admit_rate": anchor_compare.loc[anchor_compare["anchor_variant"] == "confirmed_anchor", "admit_rate"].iloc[0],
                "bucket_shift_rate": shift_summary["bucket_shift_rate"].iloc[0],
                "promoted_to_admit_rate": shift_summary["promoted_to_admit_rate"].iloc[0],
                "demoted_out_of_admit_rate": shift_summary["demoted_out_of_admit_rate"].iloc[0],
                "provisional_proxy_post_cost_expectancy": anchor_compare.loc[anchor_compare["anchor_variant"] == "provisional_anchor", "proxy_post_cost_expectancy"].iloc[0],
                "confirmed_proxy_post_cost_expectancy": anchor_compare.loc[anchor_compare["anchor_variant"] == "confirmed_anchor", "proxy_post_cost_expectancy"].iloc[0],
                "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            }
        ]
    )

    anchor_compare.to_csv(ART_DIR / "anchor_compare_summary.csv", index=False)
    side_summary.to_csv(ART_DIR / "side_compare_summary.csv", index=False)
    shift_summary.to_csv(ART_DIR / "shift_summary.csv", index=False)
    bucket_proxy.to_csv(ART_DIR / "bucket_proxy_reference.csv", index=False)
    verdict_summary.to_csv(ART_DIR / "verdict_summary.csv", index=False)
    (ART_DIR / "summary_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    anchor_table = render_table(
        anchor_compare[["anchor_variant", "events", "admit_rate", "bucket_lt_38", "bucket_38_50", "bucket_50_61_8", "bucket_61_8_79", "proxy_post_cost_expectancy", "proxy_success_rate"]],
        percent_cols={"admit_rate", "bucket_lt_38", "bucket_38_50", "bucket_50_61_8", "bucket_61_8_79", "proxy_success_rate"},
        bps_cols={"proxy_post_cost_expectancy"},
        digits_cols={"events": 0},
    )
    side_table = render_table(
        side_summary[["side", "anchor_variant", "events", "admit_rate", "bucket_shift_rate", "promoted_to_admit_rate", "proxy_post_cost_expectancy"]],
        percent_cols={"admit_rate", "bucket_shift_rate", "promoted_to_admit_rate"},
        bps_cols={"proxy_post_cost_expectancy"},
        digits_cols={"events": 0},
    )
    proxy_table = render_table(
        bucket_proxy,
        percent_cols={"proxy_success_rate"},
        bps_cols={"proxy_avg_net_ret"},
        digits_cols={"proxy_trades": 0},
    )

    prov = anchor_compare.loc[anchor_compare["anchor_variant"] == "provisional_anchor"].iloc[0]
    conf = anchor_compare.loc[anchor_compare["anchor_variant"] == "confirmed_anchor"].iloc[0]
    shift = shift_summary.iloc[0]

    factor_body = f"""
<h1>Rank 103 · confirmed extremum honest fib anchor · minimal clean replication</h1>
<p class='muted'>生成时间：{escape(verdict_summary.iloc[0]['generated_at_utc'])} · 复用既有代理样本 <code>reports/artifacts/quant_digests/confirmed_extremum_anchor_proxy/</code>，并用 <code>Rank 100</code> 已冻结的 Fib-depth band return 当作轻量 post-cost proxy。</p>
<div class='card'>
  <p><strong>一句话结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <p>{escape(desk_readthrough)}</p>
  <ul>
    <li><strong>可交易回踩带 admit rate</strong>：从 <strong>{pct(prov['admit_rate'])}</strong> 提高到 <strong>{pct(conf['admit_rate'])}</strong>。</li>
    <li><strong>bucket shift rate</strong>：<strong>{pct(shift['bucket_shift_rate'])}</strong>；其中 <strong>{pct(shift['promoted_to_admit_rate'])}</strong> 是从原本不可交易区被重新推进到 <code>38.2-79</code> 的事件，<strong>{pct(shift['demoted_out_of_admit_rate'])}</strong> 被踢出。</li>
    <li><strong>proxy post-cost expectancy</strong>：<code>provisional</code> 约 <strong>{bps(prov['proxy_post_cost_expectancy'])}</strong>，<code>confirmed</code> 约 <strong>{bps(conf['proxy_post_cost_expectancy'])}</strong> —— 量级几乎没变，仍没穿过 0。</li>
    <li><strong>确认延伸</strong>：已确认事件的额外延伸中位数约 <strong>{num(shift['median_extra_atr_confirmed'], 2)} ATR</strong>；确认所需 bar 数中位数约 <strong>{num(shift['median_bars_to_confirm'], 1)}</strong>。</li>
  </ul>
</div>
<div class='card'>
  <h2>Anchor compare</h2>
  {anchor_table}
</div>
<div class='card'>
  <h2>Side breakdown</h2>
  {side_table}
</div>
<div class='card'>
  <h2>Fib-depth proxy reference（来自 Rank 100）</h2>
  {proxy_table}
</div>
<div class='card'>
  <h2>Desk readthrough</h2>
  <p>confirmed extremum 这条线已经回答了最关键的问题：<strong>锚点画早确实会系统性把回踩看浅</strong>。但它同样也回答了另一个更重要的问题：<strong>把锚点改诚实，不等于自动拿到可部署 alpha</strong>。</p>
  <p>这轮 minimal clean replication 更像是给 Fib / failure verdict / EMA continuation 提供一个 <strong>measurement correction</strong>，而不是新的 queue-facing shared gate。因此当前更诚实的 hard verdict 是 <strong>{escape(verdict)}</strong>，不继续占 active Scout 主资源位。</p>
  <p>下一步：<strong>{escape(next_step)}</strong></p>
  <p><a href='../../reading/repo_scout/rank103_confirmed_extremum_honest_fib_anchor_clean_replication.html'>阅读版说明</a> · <a href='../../reading/repo_scout/rank103_confirmed_extremum_honest_fib_anchor_source_intake.html'>source intake</a></p>
</div>
"""

    reading_body = f"""
<h1>Rank 103 · confirmed extremum honest fib anchor · clean replication write-up</h1>
<p class='muted'>这轮没有追新 bar，也没有再发明新策略；只把 source intake 提出的核心问题压成最小 A/B：<code>provisional-anchor</code> 和 <code>confirmed-anchor</code> 到底会不会真正改变 queue-facing judgment。</p>
<div class='card'>
  <p><strong>主结论：</strong><span class='warn'>{escape(verdict)}</span>。</p>
  <ul>
    <li>confirmed anchor 的确更诚实：可交易回踩带占比从 <strong>{pct(prov['admit_rate'])}</strong> 提到 <strong>{pct(conf['admit_rate'])}</strong>，bucket shift rate 达到 <strong>{pct(shift['bucket_shift_rate'])}</strong>。</li>
    <li>但它并没有把 proxy post-cost expectancy 推过 0：<strong>{bps(prov['proxy_post_cost_expectancy'])}</strong> vs <strong>{bps(conf['proxy_post_cost_expectancy'])}</strong>，仍都只是轻微负值。</li>
    <li>更直白地说：它证明了“锚点别画早”，却没证明“只要改成 confirmed anchor 就值得升到 P2 / paper candidate”。</li>
  </ul>
</div>
<div class='card'>
  <h2>为什么不升格</h2>
  <p>如果这条线只是把更多事件推进到 <code>38.2-79</code>，但这些新增事件在现有 Fib-depth proxy 下并没有带来足够硬的成本后改善，那它就还只是上游 measurement correction，而不是独立的 shared edge。</p>
  <p>所以这轮最诚实的处理不是继续给 Rank 103 做稳定性 pack，而是直接收口：<strong>park / evidence pool</strong>。</p>
  <p><a href='../../factors/scout_rank103_confirmed_extremum_honest_fib_anchor_15m/report.html'>查看 factor 页面</a> · <a href='rank103_confirmed_extremum_honest_fib_anchor_source_intake.html'>回到 source intake</a></p>
</div>
"""

    write_html(SITE_DIR / "report.html", "Rank 103 confirmed extremum honest fib anchor", factor_body)
    write_html(READING_PATH, "Rank 103 confirmed extremum honest fib anchor clean replication", reading_body)

    print(f"[ok] wrote {ART_DIR / 'anchor_compare_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'side_compare_summary.csv'}")
    print(f"[ok] wrote {ART_DIR / 'verdict_summary.csv'}")
    print(f"[ok] wrote {SITE_DIR / 'report.html'}")
    print(f"[ok] wrote {READING_PATH}")


if __name__ == "__main__":
    main()
