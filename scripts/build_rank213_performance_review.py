#!/usr/bin/env python3
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VARIANT = "f64_h12_floor150_mult2p0"
SUMMARY_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "summary.json"
TIMESERIES_PATH = ROOT / "reports" / "artifacts" / "optimization_loop" / "rank213_p2_admission_20260328" / "variant_timeseries.csv"
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_performance_review.html"
BASE_URL = "https://fapi.binance.com/fapi/v1/klines"
INTERVAL = "15m"
LIMIT = 1500
COST_BPS = 4.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fmt_pct(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}%"


def fmt_bps(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f} bps"


def fmt_x(x: float, digits: int = 3) -> str:
    return f"{x:.{digits}f}x"


def max_drawdown(ret: pd.Series) -> float:
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def fetch_symbol(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)
    rows = []
    cur = start_ms
    while cur < end_ms:
        qs = urllib.parse.urlencode({
            "symbol": symbol,
            "interval": INTERVAL,
            "startTime": cur,
            "endTime": end_ms,
            "limit": LIMIT,
        })
        url = f"{BASE_URL}?{qs}"
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if not payload:
            break
        rows.extend(payload)
        last_open = int(payload[-1][0])
        nxt = last_open + 15 * 60 * 1000
        if nxt <= cur:
            break
        cur = nxt
        time.sleep(0.03)
    if not rows:
        raise RuntimeError(f"no data for {symbol}")
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume",
        "trade_count", "taker_base", "taker_quote", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close"] = df["close"].astype(float)
    df = df[["timestamp", "close"]].drop_duplicates("timestamp").sort_values("timestamp")
    return df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].reset_index(drop=True)


def build_close_panel(symbols: list[str], start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    panel = None
    for symbol in symbols:
        df = fetch_symbol(symbol, start, end)
        s = df.rename(columns={"close": symbol}).set_index("timestamp")[[symbol]]
        panel = s if panel is None else panel.join(s, how="outer")
    return panel.sort_index().ffill().dropna()


def overall_metrics(gross: pd.Series, net: pd.Series, turnover: pd.Series) -> dict:
    return {
        "gross_mean_bps": float(gross.mean() * 10000.0),
        "gross_cum_pct": float(((1.0 + gross).prod() - 1.0) * 100.0),
        "net_mean_bps": float(net.mean() * 10000.0),
        "net_cum_pct": float(((1.0 + net).prod() - 1.0) * 100.0),
        "win_rate": float((net > 0).mean()),
        "avg_turnover_x": float(turnover.mean()),
        "max_drawdown_pct": float(max_drawdown(net) * 100.0),
        "worst_net_bps": float(net.min() * 10000.0),
        "p5_net_bps": float(np.percentile(net, 5) * 10000.0),
    }


def grouped_metrics(detail: pd.DataFrame, key: str) -> pd.DataFrame:
    rows = []
    for group_key, sub in detail.groupby(key):
        rows.append({
            key: group_key,
            "rebalances": int(len(sub)),
            "plain_net_mean_bps": float(sub["plain_net"].mean() * 10000.0),
            "plain_net_cum_pct": float(((1.0 + sub["plain_net"]).prod() - 1.0) * 100.0),
            "plain_win_rate": float((sub["plain_net"] > 0).mean() * 100.0),
            "plain_max_dd_pct": float(max_drawdown(sub["plain_net"]) * 100.0),
            "veto_net_mean_bps": float(sub["veto_net"].mean() * 10000.0),
            "veto_net_cum_pct": float(((1.0 + sub["veto_net"]).prod() - 1.0) * 100.0),
            "veto_win_rate": float((sub["veto_net"] > 0).mean() * 100.0),
            "veto_max_dd_pct": float(max_drawdown(sub["veto_net"]) * 100.0),
        })
    return pd.DataFrame(rows)


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None) -> str:
    percent_cols = percent_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    body_rows = []
    for _, row in df.iterrows():
        tds = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in percent_cols:
                txt = fmt_pct(float(v), 2)
            elif c in bps_cols:
                txt = fmt_bps(float(v), 2)
            elif c in x_cols:
                txt = fmt_x(float(v), 3)
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = str(v)
            tds.append(f"<td>{txt}</td>")
        body_rows.append("<tr>" + "".join(tds) + "</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    variant_meta = next(v for v in summary["variants"] if v["variant"] == VARIANT)
    df = pd.read_csv(TIMESERIES_PATH)
    df = df[df["variant"] == VARIANT].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    start = pd.to_datetime(summary["sample_start"], utc=True)
    end = pd.to_datetime(summary["sample_end"], utc=True)
    hold_bars = int(variant_meta["hold_bars"])
    symbols = summary["symbols"]

    close_panel = build_close_panel(symbols, start, end)

    df["plain_net"] = df["plain_gross_return"] - df["plain_turnover_x"] * (COST_BPS / 10000.0)
    df["veto_net"] = df["veto_gross_return"] - df["veto_turnover_x"] * (COST_BPS / 10000.0)
    df["month"] = df["timestamp"].dt.strftime("%Y-%m")
    df["year"] = df["timestamp"].dt.strftime("%Y")

    detail_rows = []
    for row in df.itertuples(index=False):
        entry_ts = row.timestamp
        exit_ts = entry_ts + pd.Timedelta(minutes=15 * hold_bars)
        future = close_panel.loc[exit_ts] / close_panel.loc[entry_ts] - 1.0
        longs = [x for x in str(row.plain_longs).split(",") if x]
        plain_shorts = [x for x in str(row.plain_shorts).split(",") if x]
        veto_shorts = [x for x in str(row.veto_shorts).split(",") if x]
        vetoed_names = sorted(set(plain_shorts) - set(veto_shorts))

        long_contrib = 0.5 * float(future[longs].mean())
        plain_short_contrib = 0.5 * float((-future[plain_shorts]).mean())
        veto_short_contrib = 0.5 * float((-future[veto_shorts]).mean())

        hit_names = 0
        false_kill_names = 0
        neutral_names = 0
        for sym in vetoed_names:
            short_pnl = float(-future[sym])
            if short_pnl < 0:
                hit_names += 1
            elif short_pnl > 0:
                false_kill_names += 1
            else:
                neutral_names += 1

        detail_rows.append({
            "timestamp": entry_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "month": row.month,
            "year": row.year,
            "plain_net": float(row.plain_net),
            "veto_net": float(row.veto_net),
            "plain_gross": float(row.plain_gross_return),
            "veto_gross": float(row.veto_gross_return),
            "plain_turnover_x": float(row.plain_turnover_x),
            "veto_turnover_x": float(row.veto_turnover_x),
            "long_contrib": long_contrib,
            "plain_short_contrib": plain_short_contrib,
            "veto_short_contrib": veto_short_contrib,
            "veto_count": int(row.veto_count),
            "vetoed_name_count": int(len(vetoed_names)),
            "hit_names": int(hit_names),
            "false_kill_names": int(false_kill_names),
            "neutral_names": int(neutral_names),
            "veto_event_outperform": bool(float(row.veto_gross_return) > float(row.plain_gross_return)),
            "veto_event_underperform": bool(float(row.veto_gross_return) < float(row.plain_gross_return)),
            "plain_longs": row.plain_longs,
            "plain_shorts": row.plain_shorts,
            "veto_shorts": row.veto_shorts,
        })
    detail = pd.DataFrame(detail_rows)

    plain = overall_metrics(df["plain_gross_return"], df["plain_net"], df["plain_turnover_x"])
    veto = overall_metrics(df["veto_gross_return"], df["veto_net"], df["veto_turnover_x"])
    monthly = grouped_metrics(detail, "month")
    yearly = grouped_metrics(detail, "year")

    veto_events = detail[detail["veto_count"] > 0].copy()
    total_vetoed_names = int(detail["vetoed_name_count"].sum())
    hit_names = int(detail["hit_names"].sum())
    false_kill_names = int(detail["false_kill_names"].sum())
    neutral_names = int(detail["neutral_names"].sum())

    review = {
        "sample": {
            "sample_start_utc": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sample_end_utc": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bars": int(summary["bars"]),
            "calendar_days": float((end - start) / pd.Timedelta(days=1)),
            "rebalances": int(len(df)),
            "variant": VARIANT,
        },
        "plain": plain,
        "veto": veto,
        "delta_veto_minus_plain": {
            "gross_mean_bps": veto["gross_mean_bps"] - plain["gross_mean_bps"],
            "net_mean_bps": veto["net_mean_bps"] - plain["net_mean_bps"],
            "net_cum_pct": veto["net_cum_pct"] - plain["net_cum_pct"],
            "win_rate_pct_points": (veto["win_rate"] - plain["win_rate"]) * 100.0,
            "avg_turnover_x": veto["avg_turnover_x"] - plain["avg_turnover_x"],
            "max_drawdown_reduction_pct_points": abs(plain["max_drawdown_pct"]) - abs(veto["max_drawdown_pct"]),
            "avg_top_short_contributor_share_pct_points": (variant_meta["veto"]["avg_top_short_contributor_share"] - variant_meta["plain"]["avg_top_short_contributor_share"]) * 100.0,
            "avg_largest_short_loss_bps": variant_meta["veto"]["avg_largest_short_loss_bps"] - variant_meta["plain"]["avg_largest_short_loss_bps"],
            "avg_short_leg_max_upbar_pct_points": variant_meta["veto"]["avg_short_leg_max_upbar_pct"] - variant_meta["plain"]["avg_short_leg_max_upbar_pct"],
        },
        "leg_contribution": {
            "long_leg_mean_gross_bps": float(detail["long_contrib"].mean() * 10000.0),
            "plain_short_leg_mean_gross_bps": float(detail["plain_short_contrib"].mean() * 10000.0),
            "veto_short_leg_mean_gross_bps": float(detail["veto_short_contrib"].mean() * 10000.0),
            "long_leg_sum_pct_points": float(detail["long_contrib"].sum() * 100.0),
            "plain_short_leg_sum_pct_points": float(detail["plain_short_contrib"].sum() * 100.0),
            "veto_short_leg_sum_pct_points": float(detail["veto_short_contrib"].sum() * 100.0),
        },
        "veto_effectiveness": {
            "pct_rebalances_with_any_veto": float((detail["veto_count"] > 0).mean()),
            "avg_veto_count_per_rebalance": float(detail["veto_count"].mean()),
            "rebalance_count_with_any_veto": int(len(veto_events)),
            "total_vetoed_names": total_vetoed_names,
            "name_level_hit_rate": float(hit_names / total_vetoed_names) if total_vetoed_names else None,
            "name_level_false_kill_rate": float(false_kill_names / total_vetoed_names) if total_vetoed_names else None,
            "name_level_neutral_rate": float(neutral_names / total_vetoed_names) if total_vetoed_names else None,
            "rebalance_level_outperform_rate_given_any_veto": float(veto_events["veto_event_outperform"].mean()) if len(veto_events) else None,
            "rebalance_level_underperform_rate_given_any_veto": float(veto_events["veto_event_underperform"].mean()) if len(veto_events) else None,
        },
        "grid_evidence": {
            "positive_veto_variants": int(sum(v["veto"]["net_mean_4bps_bps"] > 0 for v in summary["variants"])),
            "improved_vs_plain_variants": int(sum(v["veto"]["net_mean_4bps_bps"] > v["plain"]["net_mean_4bps_bps"] for v in summary["variants"])),
            "variant_count": int(len(summary["variants"])),
            "selected_variant_time_split": variant_meta["time_split"],
        },
    }

    (ART_DIR / "rank213_performance_review_summary.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    monthly.to_csv(ART_DIR / "rank213_performance_review_monthly.csv", index=False)
    yearly.to_csv(ART_DIR / "rank213_performance_review_yearly.csv", index=False)
    detail.to_csv(ART_DIR / "rank213_performance_review_detail.csv", index=False)

    monthly_fmt = monthly.copy()
    yearly_fmt = yearly.copy()
    monthly_table = render_table(
        monthly_fmt,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps"},
    )
    yearly_table = render_table(
        yearly_fmt,
        percent_cols={"plain_net_cum_pct", "plain_win_rate", "plain_max_dd_pct", "veto_net_cum_pct", "veto_win_rate", "veto_max_dd_pct"},
        bps_cols={"plain_net_mean_bps", "veto_net_mean_bps"},
    )

    html = f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank 213 performance review（冻结 admission seed）</title>
  <style>
    :root {{
      --bg:#f8fafc; --card:#ffffff; --fg:#0f172a; --muted:#64748b; --line:#e2e8f0;
      --good:#166534; --good-bg:#dcfce7; --warn:#9a3412; --warn-bg:#ffedd5; --info:#1d4ed8; --info-bg:#dbeafe;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:28px 18px 64px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px 20px; margin-bottom:14px; }}
    h1,h2,h3 {{ margin:0 0 12px; line-height:1.35; }}
    h1 {{ font-size:28px; }}
    h2 {{ font-size:20px; margin-top:4px; }}
    p, li {{ margin:0 0 8px; }}
    ul {{ margin:0; padding-left:20px; }}
    code {{ background:#eff6ff; border-radius:6px; padding:2px 6px; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; }}
    .muted {{ color:var(--muted); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:12px; }}
    .metric {{ border:1px solid var(--line); border-radius:12px; padding:12px 14px; background:#fff; }}
    .metric .k {{ color:var(--muted); font-size:13px; margin-bottom:4px; }}
    .metric .v {{ font-size:24px; font-weight:700; }}
    .note {{ border-left:4px solid var(--info); background:var(--info-bg); padding:12px 14px; border-radius:10px; }}
    .warn {{ border-left-color:var(--warn); background:var(--warn-bg); }}
    .good {{ border-left-color:var(--good); background:var(--good-bg); }}
    table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
    th, td {{ border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }}
    th {{ background:#f8fafc; }}
    .mono {{ white-space:pre-wrap; font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:13px; background:#f8fafc; border:1px solid var(--line); border-radius:10px; padding:12px; }}
    a {{ color:#0f766e; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Rank 213 performance review（冻结 admission seed）</h1>
      <p><strong>对象：</strong><code>Rank 213 / large-cap XS momentum × short-leg jump veto</code></p>
      <p><strong>页面目标：</strong>只补证据，不新增研究；把当前 live 所依赖的 <code>admission timeseries seed</code> 直接整理成可审计、可复述、可回答“有多强、稳不稳、测了多久”的 performance review。</p>
      <p class="muted">source of truth：<code>{SUMMARY_PATH.relative_to(ROOT)}</code>、<code>{TIMESERIES_PATH.relative_to(ROOT)}</code>；衍生产物：<code>reports/artifacts/paper_rank213_largecap_xs_jump_veto/rank213_performance_review_*.{{json,csv}}</code></p>
      <p><a href="/momentum/paper/rank213_largecap_xs_jump_veto.html">当前 runner 页面</a> · <a href="/momentum/paper/rank213_largecap_xs_jump_veto_spec.html">最小可复现 spec 页面</a></p>
    </div>

    <div class="card">
      <h2>1) admission timeseries seed 的起止时间与总样本长度</h2>
      <div class="grid">
        <div class="metric"><div class="k">sample_start_utc</div><div class="v" style="font-size:18px">{review['sample']['sample_start_utc']}</div></div>
        <div class="metric"><div class="k">sample_end_utc</div><div class="v" style="font-size:18px">{review['sample']['sample_end_utc']}</div></div>
        <div class="metric"><div class="k">bars</div><div class="v">{review['sample']['bars']}</div></div>
        <div class="metric"><div class="k">rebalances（当前冻结 variant）</div><div class="v">{review['sample']['rebalances']}</div></div>
        <div class="metric"><div class="k">calendar length</div><div class="v">{review['sample']['calendar_days']:.2f}d</div></div>
        <div class="metric"><div class="k">frozen variant</div><div class="v" style="font-size:18px">{review['sample']['variant']}</div></div>
      </div>
      <p class="muted">回答“测了多久”：这条 current live seed 对应的是 <strong>{review['sample']['bars']} 根 15m bar</strong>、约 <strong>{review['sample']['calendar_days']:.2f} 天</strong> 的 admission 样本，在当前冻结 variant 上形成 <strong>{review['sample']['rebalances']} 次非重叠换仓</strong>。</p>
    </div>

    <div class="card">
      <h2>2) plain XS momentum baseline（同口径）</h2>
      <div class="grid">
        <div class="metric"><div class="k">gross mean / rebalance</div><div class="v">{fmt_bps(review['plain']['gross_mean_bps'])}</div></div>
        <div class="metric"><div class="k">net mean @ 4bps × turnover_x</div><div class="v">{fmt_bps(review['plain']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">net cumulative</div><div class="v">{fmt_pct(review['plain']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">win rate</div><div class="v">{fmt_pct(review['plain']['win_rate']*100)}</div></div>
        <div class="metric"><div class="k">avg turnover</div><div class="v">{fmt_x(review['plain']['avg_turnover_x'])}</div></div>
        <div class="metric"><div class="k">max drawdown（net）</div><div class="v">{fmt_pct(review['plain']['max_drawdown_pct'])}</div></div>
      </div>
      <p class="muted">补充尾部：p5 net = {fmt_bps(review['plain']['p5_net_bps'])}；worst rebalance net = {fmt_bps(review['plain']['worst_net_bps'])}。</p>
    </div>

    <div class="card">
      <h2>3) veto 版（同口径）</h2>
      <div class="grid">
        <div class="metric"><div class="k">gross mean / rebalance</div><div class="v">{fmt_bps(review['veto']['gross_mean_bps'])}</div></div>
        <div class="metric"><div class="k">net mean @ 4bps × turnover_x</div><div class="v">{fmt_bps(review['veto']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">net cumulative</div><div class="v">{fmt_pct(review['veto']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">win rate</div><div class="v">{fmt_pct(review['veto']['win_rate']*100)}</div></div>
        <div class="metric"><div class="k">avg turnover</div><div class="v">{fmt_x(review['veto']['avg_turnover_x'])}</div></div>
        <div class="metric"><div class="k">max drawdown（net）</div><div class="v">{fmt_pct(review['veto']['max_drawdown_pct'])}</div></div>
      </div>
      <p class="muted">补充尾部：p5 net = {fmt_bps(review['veto']['p5_net_bps'])}；worst rebalance net = {fmt_bps(review['veto']['worst_net_bps'])}。</p>
    </div>

    <div class="card">
      <h2>4) baseline vs veto 的差值</h2>
      <div class="grid">
        <div class="metric"><div class="k">Δ gross mean</div><div class="v">{fmt_bps(review['delta_veto_minus_plain']['gross_mean_bps'])}</div></div>
        <div class="metric"><div class="k">Δ net mean</div><div class="v">{fmt_bps(review['delta_veto_minus_plain']['net_mean_bps'])}</div></div>
        <div class="metric"><div class="k">Δ net cumulative</div><div class="v">{fmt_pct(review['delta_veto_minus_plain']['net_cum_pct'])}</div></div>
        <div class="metric"><div class="k">Δ win rate</div><div class="v">{fmt_pct(review['delta_veto_minus_plain']['win_rate_pct_points'])}</div></div>
        <div class="metric"><div class="k">Δ avg turnover</div><div class="v">{fmt_x(review['delta_veto_minus_plain']['avg_turnover_x'])}</div></div>
        <div class="metric"><div class="k">MDD reduction</div><div class="v">{fmt_pct(review['delta_veto_minus_plain']['max_drawdown_reduction_pct_points'])}</div></div>
      </div>
      <ul>
        <li>avg top short contributor share：{review['delta_veto_minus_plain']['avg_top_short_contributor_share_pct_points']:.2f} pct-pts（veto - plain）</li>
        <li>avg largest short loss：{fmt_bps(review['delta_veto_minus_plain']['avg_largest_short_loss_bps'])}（veto - plain）</li>
        <li>avg short-leg max upbar：{review['delta_veto_minus_plain']['avg_short_leg_max_upbar_pct_points']:.3f} pct-pts（veto - plain）</li>
      </ul>
      <div class="note good">这页只做证据整理，不把这些差值再解释成新研究结论；它们就是当前 frozen seed 上 plain 与 veto 的同口径对比。</div>
    </div>

    <div class="card">
      <h2>5) 按月 / 按年稳定性</h2>
      <p><strong>按月</strong></p>
      {monthly_table}
      <p style="margin-top:12px"><strong>按年</strong></p>
      {yearly_table}
      <div class="note warn">当前 seed 样本只覆盖 <strong>2026-02 ~ 2026-03</strong>，因此“按年稳定性”只有 <strong>2026</strong> 这一行；这能回答“本页测了多久、月度是否断层”，但<strong>不能</strong>被误读成跨年稳定性已被证明。</div>
      <div class="note" style="margin-top:12px">当前冻结 variant 的二分样本（来自 admission summary）也保持为正：前半 veto net mean = {fmt_bps(review['grid_evidence']['selected_variant_time_split'][0]['veto_net_mean_4bps_bps'])}，后半 veto net mean = {fmt_bps(review['grid_evidence']['selected_variant_time_split'][1]['veto_net_mean_4bps_bps'])}。</div>
    </div>

    <div class="card">
      <h2>6) long leg / short leg 贡献</h2>
      <div class="mono">定义：按每次换仓的 gross return 线性分解。long leg contribution = 0.5 × mean(long future return)；short leg contribution = 0.5 × mean(-future return of selected shorts)。因此 gross return = long contribution + short contribution。这里展示平均 gross bps / rebalance，以及跨全样本简单求和后的 pct-points；不把 compounding attribution 硬拆。</div>
      <ul>
        <li>long leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['long_leg_mean_gross_bps'])}</strong> / rebalance</li>
        <li>plain short leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['plain_short_leg_mean_gross_bps'])}</strong> / rebalance</li>
        <li>veto short leg mean gross contribution：<strong>{fmt_bps(review['leg_contribution']['veto_short_leg_mean_gross_bps'])}</strong> / rebalance</li>
      </ul>
      <ul>
        <li>long leg sum：<strong>{fmt_pct(review['leg_contribution']['long_leg_sum_pct_points'])}</strong> pct-points</li>
        <li>plain short leg sum：<strong>{fmt_pct(review['leg_contribution']['plain_short_leg_sum_pct_points'])}</strong> pct-points</li>
        <li>veto short leg sum：<strong>{fmt_pct(review['leg_contribution']['veto_short_leg_sum_pct_points'])}</strong> pct-points</li>
      </ul>
      <p class="muted">直接读法：这条 seed 的 gross alpha 主体并不是 long leg 变了，而是 <strong>short leg 从接近不贡献，变成了明显正贡献</strong>。</p>
    </div>

    <div class="card">
      <h2>7) veto 命中率与误杀率</h2>
      <div class="mono">本页的可审计定义：
- name-level 命中：一个被 veto 的 plain-short 候选，如果在该持有窗里“原本做空它会亏钱”（short PnL &lt; 0），记为 hit。
- name-level 误杀：一个被 veto 的 plain-short 候选，如果在该持有窗里“原本做空它会赚钱”（short PnL &gt; 0），记为 false kill。
- rebalance-level outperform / underperform：仅在发生过 veto 的换仓里，看 veto 版 gross return 是否高于 / 低于 plain。</div>
      <ul>
        <li>pct rebalances with any veto：<strong>{fmt_pct(review['veto_effectiveness']['pct_rebalances_with_any_veto']*100)}</strong></li>
        <li>avg veto count / rebalance：<strong>{review['veto_effectiveness']['avg_veto_count_per_rebalance']:.3f}</strong></li>
        <li>rebalance count with any veto：<strong>{review['veto_effectiveness']['rebalance_count_with_any_veto']}</strong></li>
        <li>total vetoed names：<strong>{review['veto_effectiveness']['total_vetoed_names']}</strong></li>
        <li>name-level hit rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_hit_rate']*100)}</strong></li>
        <li>name-level false-kill rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_false_kill_rate']*100)}</strong></li>
        <li>name-level neutral rate：<strong>{fmt_pct(review['veto_effectiveness']['name_level_neutral_rate']*100)}</strong></li>
        <li>rebalance-level outperform rate | any veto：<strong>{fmt_pct(review['veto_effectiveness']['rebalance_level_outperform_rate_given_any_veto']*100)}</strong></li>
        <li>rebalance-level underperform rate | any veto：<strong>{fmt_pct(review['veto_effectiveness']['rebalance_level_underperform_rate_given_any_veto']*100)}</strong></li>
      </ul>
      <div class="note warn">这里的“误杀率”是严格按当前 seed 的持有窗 realized short PnL 定义的 <strong>同窗审计指标</strong>，不是对未来 out-of-sample 的主张。</div>
    </div>

    <div class="card">
      <h2>8) 当前 keep / live 结论到底依赖什么证据</h2>
      <ul>
        <li><strong>依赖的是 admission timeseries seed 本身</strong>：当前 live runner 明确是 <code>frozen_admission_timeseries_seed</code>，不是 raw-bar live recomputation，也不是 2026-03-28 之后的新 forward sample。</li>
        <li><strong>依赖当前冻结 variant 的整段样本表现</strong>：<code>{VARIANT}</code> 在这段 seed 上给出 veto net mean = <strong>{fmt_bps(review['veto']['net_mean_bps'])}</strong>、net cumulative = <strong>{fmt_pct(review['veto']['net_cum_pct'])}</strong>、max drawdown = <strong>{fmt_pct(review['veto']['max_drawdown_pct'])}</strong>。</li>
        <li><strong>依赖同一 admission 网格的稳定性证据</strong>：同一 24 组 parameter/time 变体里，veto 成本后为正的有 <strong>{review['grid_evidence']['positive_veto_variants']}/{review['grid_evidence']['variant_count']}</strong> 组，相对 plain 改善的有 <strong>{review['grid_evidence']['improved_vs_plain_variants']}/{review['grid_evidence']['variant_count']}</strong> 组。</li>
        <li><strong>依赖“当前冻结 spec 已经写死且诚实”</strong>：当前系统结论不是“Rank213 已完成 raw-bar live 证明”，而是“这版 frozen admission seed 已接成 dedicated paper lane，当前应维持 live，新增改动限制在 veto 参数外”。</li>
      </ul>
      <div class="note">所以这页能直接回答三件事：
- <strong>有多强</strong>：看 whole-sample net mean / net cumulative / max drawdown / short-leg contribution；
- <strong>稳不稳</strong>：看月度表、半样本 split、24 组 grid evidence；
- <strong>测了多久</strong>：看 sample 起止、4500 bars、369 rebalances、约 46.86 天。</div>
    </div>
  </div>
</body>
</html>
'''
    SITE_PATH.write_text(html, encoding="utf-8")
    print(json.dumps({
        "summary_json": str((ART_DIR / 'rank213_performance_review_summary.json').relative_to(ROOT)),
        "monthly_csv": str((ART_DIR / 'rank213_performance_review_monthly.csv').relative_to(ROOT)),
        "yearly_csv": str((ART_DIR / 'rank213_performance_review_yearly.csv').relative_to(ROOT)),
        "detail_csv": str((ART_DIR / 'rank213_performance_review_detail.csv').relative_to(ROOT)),
        "html": str(SITE_PATH.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
