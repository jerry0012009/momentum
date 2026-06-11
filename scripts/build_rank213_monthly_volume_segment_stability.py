#!/usr/bin/env python3
from __future__ import annotations

import json
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / "reports" / "artifacts" / "paper_rank213_largecap_xs_jump_veto"
SITE_PATH = ROOT / "reports" / "site" / "paper" / "rank213_largecap_xs_jump_veto_monthly_volume_segment_stability.html"

DETAIL_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_detail.csv"
PCT_DETAIL_PATH = ART_DIR / "rank213_monthly_volume_percentile_gate_review_detail.csv"
MONTHLY_SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_universe_rebuild_summary.json"
PCT_SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_percentile_gate_review_summary.json"

SUMMARY_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_summary.json"
ANNUAL_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_annual.csv"
REGIME_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_regime.csv"
ROLLING_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_rolling_3y_5y.csv"
OVERALL_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_overall.csv"
MONTHLY_PATH = ART_DIR / "rank213_monthly_volume_segment_stability_monthly.csv"

PCT_GATE_Q = 60.0

STRATEGIES = [
    {
        "strategy": "plain_baseline",
        "label": "1) plain baseline",
        "ret_col": "plain_net",
        "turnover_col": "plain_turnover_x",
        "active_col": None,
        "note": "不加 veto / gate；每个 rebalance 都开门。",
    },
    {
        "strategy": "baseline_plus_veto",
        "label": "2) baseline + veto",
        "ret_col": "veto_net",
        "turnover_col": "veto_turnover_x",
        "active_col": None,
        "note": "只加 short-leg jump veto；不加 gate。",
    },
    {
        "strategy": "baseline_plus_veto_plus_fixed_gate",
        "label": "3a) veto + fixed gate",
        "ret_col": "gate_net",
        "turnover_col": "gate_turnover_x",
        "active_col": "gate_on",
        "note": "沿用 frozen30 研究里的固定阈值 gate，直接套到 monthly-volume universe。",
    },
    {
        "strategy": "baseline_plus_veto_plus_percentile_gate_q60",
        "label": "3b) veto + percentile gate q60",
        "ret_col": "pct_gate_q60_net",
        "turnover_col": "pct_gate_q60_turnover_x",
        "active_col": "pct_gate_q60_on",
        "note": "monthly-volume 自身历史的 expanding percentile gate；strength_min_pct >= 60 才开门。",
    },
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def to_iso(ts: pd.Timestamp | None) -> str | None:
    if ts is None or pd.isna(ts):
        return None
    return pd.to_datetime(ts, utc=True).strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_pct(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}%"


def fmt_bps(x: float | int | None, digits: int = 2) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f} bps"


def fmt_x(x: float | int | None, digits: int = 3) -> str:
    if x is None or pd.isna(x):
        return ""
    return f"{float(x):.{digits}f}x"


def max_drawdown(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    eq = (1.0 + ret).cumprod()
    dd = eq / eq.cummax() - 1.0
    return float(dd.min())


def compound_ret(ret: pd.Series) -> float:
    ret = pd.to_numeric(ret, errors="coerce").fillna(0.0)
    if ret.empty:
        return np.nan
    return float((1.0 + ret).prod() - 1.0)


def calc_strategy_stats(df: pd.DataFrame, *, segment_type: str, segment: str, start_ts: pd.Timestamp, end_ts: pd.Timestamp, strategy_spec: dict) -> dict:
    ret = pd.to_numeric(df[strategy_spec["ret_col"]], errors="coerce").fillna(0.0)
    turnover = pd.to_numeric(df.get(strategy_spec["turnover_col"], pd.Series(0.0, index=df.index)), errors="coerce").fillna(0.0)
    active_col = strategy_spec.get("active_col")
    if active_col:
        active = df[active_col].fillna(False).astype(bool)
    else:
        active = pd.Series(True, index=df.index)

    months = df["month"].astype(str) if "month" in df.columns else pd.Series([], dtype=str)
    return {
        "segment_type": segment_type,
        "segment": segment,
        "strategy": strategy_spec["strategy"],
        "label": strategy_spec["label"],
        "start_utc": to_iso(start_ts),
        "end_utc": to_iso(end_ts),
        "months": int(months.nunique()) if len(months) else 0,
        "rebalances": int(len(df)),
        "net_mean_bps": float(ret.mean() * 10000.0) if len(ret) else np.nan,
        "net_cum_pct": float(compound_ret(ret) * 100.0) if len(ret) else np.nan,
        "max_drawdown_pct": float(max_drawdown(ret) * 100.0) if len(ret) else np.nan,
        "win_rate_pct": float((ret > 0).mean() * 100.0) if len(ret) else np.nan,
        "open_rate_pct": float(active.mean() * 100.0) if len(active) else np.nan,
        "active_rebalances": int(active.sum()) if len(active) else 0,
        "avg_turnover_x": float(turnover.mean()) if len(turnover) else np.nan,
        "avg_eligible_universe_size": float(pd.to_numeric(df.get("eligible_universe_size", pd.Series(np.nan, index=df.index)), errors="coerce").mean()) if len(df) else np.nan,
    }


def segment_stats(df: pd.DataFrame, segment_type: str, segment_col: str, order: list[str] | None = None) -> pd.DataFrame:
    rows: list[dict] = []
    groups = df.dropna(subset=[segment_col]).groupby(segment_col, sort=False)
    for segment, g in groups:
        g = g.sort_values("timestamp_ts")
        if g.empty:
            continue
        for spec in STRATEGIES:
            rows.append(calc_strategy_stats(
                g,
                segment_type=segment_type,
                segment=str(segment),
                start_ts=g["timestamp_ts"].min(),
                end_ts=g["timestamp_ts"].max(),
                strategy_spec=spec,
            ))
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    if order:
        out["_segment_order"] = out["segment"].map({v: i for i, v in enumerate(order)}).fillna(9999)
        out["_strategy_order"] = out["strategy"].map({s["strategy"]: i for i, s in enumerate(STRATEGIES)}).fillna(9999)
        out = out.sort_values(["_segment_order", "_strategy_order", "segment", "strategy"]).drop(columns=["_segment_order", "_strategy_order"])
    return out.reset_index(drop=True)


def overall_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    g = df.sort_values("timestamp_ts")
    for spec in STRATEGIES:
        rows.append(calc_strategy_stats(
            g,
            segment_type="overall",
            segment="2020-02..2026-04",
            start_ts=g["timestamp_ts"].min(),
            end_ts=g["timestamp_ts"].max(),
            strategy_spec=spec,
        ))
    return pd.DataFrame(rows)


def rolling_window_stats(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    years = sorted(int(y) for y in df["year"].dropna().unique())
    for width in [3, 5]:
        for start_year in years:
            end_year = start_year + width - 1
            # Keep YTD windows too, but require at least 24 months for 3y and 36 months for 5y so the table is not noise.
            w = df[(df["year"] >= start_year) & (df["year"] <= end_year)].copy()
            if w.empty:
                continue
            months = w["month"].nunique()
            if (width == 3 and months < 24) or (width == 5 and months < 36):
                continue
            label = f"{start_year}-{min(end_year, int(df['year'].max()))} ({width}y{' YTD' if end_year > int(df['year'].max()) else ''})"
            for spec in STRATEGIES:
                rows.append(calc_strategy_stats(
                    w,
                    segment_type=f"rolling_{width}y",
                    segment=label,
                    start_ts=w["timestamp_ts"].min(),
                    end_ts=w["timestamp_ts"].max(),
                    strategy_spec=spec,
                ))
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["_width"] = out["segment_type"].str.extract(r"(\d+)").astype(float)
    out["_start"] = out["segment"].str.extract(r"^(\d{4})").astype(float)
    out["_strategy_order"] = out["strategy"].map({s["strategy"]: i for i, s in enumerate(STRATEGIES)}).fillna(9999)
    return out.sort_values(["_width", "_start", "_strategy_order"]).drop(columns=["_width", "_start", "_strategy_order"]).reset_index(drop=True)


def add_regimes(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    btc = pd.to_numeric(out["btc_cumret"], errors="coerce")
    xs_bps = pd.to_numeric(out["universe_cumret_std"], errors="coerce") * 10000.0
    q30, q70 = xs_bps.quantile([0.30, 0.70])

    def trend_label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        if v <= -0.015:
            return "btc_down_64bar<=-1.5%"
        if v >= 0.015:
            return "btc_up_64bar>=+1.5%"
        return "btc_flat_64bar[-1.5%,+1.5%]"

    def xs_label(v: float) -> str:
        if pd.isna(v):
            return "unknown"
        if v <= q30:
            return "low_xs_dispersion_p0_p30"
        if v >= q70:
            return "high_xs_dispersion_p70_p100"
        return "mid_xs_dispersion_p30_p70"

    out["regime_btc_trend"] = btc.map(trend_label)
    out["regime_xs_dispersion"] = xs_bps.map(xs_label)
    out["regime_calendar"] = np.select(
        [out["year"].between(2020, 2021), out["year"].between(2022, 2023), out["year"].between(2024, 2026)],
        ["2020-2021 early/liquidity expansion", "2022-2023 bear-to-chop", "2024-2026 recent/high-beta"],
        default="other",
    )
    return out


def render_table(df: pd.DataFrame, *, columns: list[str], pct_cols: set[str] | None = None, bps_cols: set[str] | None = None, x_cols: set[str] | None = None, int_cols: set[str] | None = None, max_rows: int | None = None) -> str:
    pct_cols = pct_cols or set()
    bps_cols = bps_cols or set()
    x_cols = x_cols or set()
    int_cols = int_cols or set()
    if df.empty:
        return "<p class='muted'>暂无数据。</p>"
    work = df[columns].copy()
    if max_rows is not None:
        work = work.head(max_rows)
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in work.columns)
    rows = []
    for _, row in work.iterrows():
        cells = []
        for c in work.columns:
            v = row[c]
            if pd.isna(v):
                txt = ""
            elif c in pct_cols:
                txt = fmt_pct(v)
            elif c in bps_cols:
                txt = fmt_bps(v)
            elif c in x_cols:
                txt = fmt_x(v)
            elif c in int_cols:
                txt = str(int(v))
            elif isinstance(v, (float, np.floating)):
                txt = f"{float(v):.4f}"
            else:
                txt = escape(str(v))
            cells.append(f"<td>{txt}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<div class='table-wrap'><table><thead><tr>" + headers + "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"


def strategy_pivot(df: pd.DataFrame, segment_type: str | None = None) -> pd.DataFrame:
    work = df.copy()
    if segment_type:
        work = work[work["segment_type"] == segment_type].copy()
    cols = ["net_mean_bps", "net_cum_pct", "max_drawdown_pct", "open_rate_pct"]
    piv = work.pivot_table(index="segment", columns="strategy", values=cols, aggfunc="first")
    piv.columns = [f"{strategy}.{metric}" for metric, strategy in piv.columns]
    piv = piv.reset_index()
    return piv


def main() -> int:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_PATH.parent)
    if not DETAIL_PATH.exists():
        raise RuntimeError(f"missing {DETAIL_PATH}; run build_rank213_monthly_volume_universe_rebuild.py first")
    if not PCT_DETAIL_PATH.exists():
        raise RuntimeError(f"missing {PCT_DETAIL_PATH}; run build_rank213_monthly_volume_percentile_gate_review.py first")

    usecols = [
        "timestamp_ts", "exit_ts", "month", "eligible_universe_size", "plain_net", "veto_net", "gate_net",
        "plain_turnover_x", "veto_turnover_x", "gate_turnover_x", "gate_on", "btc_cumret", "universe_cumret_std",
    ]
    detail = pd.read_csv(DETAIL_PATH, usecols=usecols)
    pct = pd.read_csv(PCT_DETAIL_PATH, usecols=["timestamp_ts", "strength_min_pct"])
    detail["timestamp_ts"] = pd.to_datetime(detail["timestamp_ts"], utc=True)
    detail["exit_ts"] = pd.to_datetime(detail["exit_ts"], utc=True)
    pct["timestamp_ts"] = pd.to_datetime(pct["timestamp_ts"], utc=True)
    df = detail.merge(pct, on="timestamp_ts", how="left")
    df = df.sort_values("timestamp_ts").reset_index(drop=True)
    df["year"] = df["timestamp_ts"].dt.year.astype(int)
    df["gate_on"] = df["gate_on"].fillna(False).astype(bool)
    df["pct_gate_q60_on"] = pd.to_numeric(df["strength_min_pct"], errors="coerce") >= PCT_GATE_Q
    df["pct_gate_q60_net"] = np.where(df["pct_gate_q60_on"], pd.to_numeric(df["veto_net"], errors="coerce").fillna(0.0), 0.0)
    df["pct_gate_q60_turnover_x"] = np.where(df["pct_gate_q60_on"], pd.to_numeric(df["veto_turnover_x"], errors="coerce").fillna(0.0), 0.0)
    df = add_regimes(df)

    # Monthly diagnostic table helps inspect exact months behind annual/regime aggregate swings.
    monthly_rows = []
    for month, g in df.groupby("month", sort=True):
        for spec in STRATEGIES:
            monthly_rows.append(calc_strategy_stats(
                g.sort_values("timestamp_ts"),
                segment_type="monthly",
                segment=str(month),
                start_ts=g["timestamp_ts"].min(),
                end_ts=g["timestamp_ts"].max(),
                strategy_spec=spec,
            ))
    monthly = pd.DataFrame(monthly_rows)

    overall = overall_stats(df)
    annual = segment_stats(df, "calendar_year", "year", order=[str(y) for y in sorted(df["year"].unique())])
    # Three complementary regime cuts: calendar research phases, BTC trend, and cross-sectional dispersion.
    regime_parts = [
        segment_stats(df, "regime_calendar_phase", "regime_calendar", order=["2020-2021 early/liquidity expansion", "2022-2023 bear-to-chop", "2024-2026 recent/high-beta"]),
        segment_stats(df, "regime_btc_64bar_trend", "regime_btc_trend", order=["btc_down_64bar<=-1.5%", "btc_flat_64bar[-1.5%,+1.5%]", "btc_up_64bar>=+1.5%"]),
        segment_stats(df, "regime_xs_dispersion_tercile", "regime_xs_dispersion", order=["low_xs_dispersion_p0_p30", "mid_xs_dispersion_p30_p70", "high_xs_dispersion_p70_p100"]),
    ]
    regime = pd.concat(regime_parts, ignore_index=True)
    rolling = rolling_window_stats(df)

    for path, obj in [(OVERALL_PATH, overall), (ANNUAL_PATH, annual), (REGIME_PATH, regime), (ROLLING_PATH, rolling), (MONTHLY_PATH, monthly)]:
        obj.to_csv(path, index=False)

    monthly_summary = read_json(MONTHLY_SUMMARY_PATH)
    pct_summary = read_json(PCT_SUMMARY_PATH)
    summary = {
        "scope": "rank213 monthly volume causal universe: segmented stability by annual / regime / rolling 3y-5y windows",
        "methodology": {
            "universe": "monthly volume rebuild: at each month, select top30 by previous full calendar month's Binance UM perpetual 1d quote_volume, then run rank213 rules on that month's universe.",
            "strategies": {s["strategy"]: {"label": s["label"], "note": s["note"]} for s in STRATEGIES},
            "percentile_gate": f"pct_gate_q60_on = strength_min_pct >= {PCT_GATE_Q}; strength percentiles are from prior monthly-volume rebuild rows in build_rank213_monthly_volume_percentile_gate_review.py.",
            "regime_cuts": {
                "calendar_phase": "2020-2021 / 2022-2023 / 2024-2026 research-phase split.",
                "btc_64bar_trend": "descriptive bins by BTC 64-bar cumulative return: <=-1.5%, flat, >=+1.5%.",
                "xs_dispersion_tercile": "descriptive bins by universe_cumret_std terciles over the monthly-volume sample.",
            },
            "metric_definitions": {
                "net_mean_bps": "mean net return per rebalance basket, in bps.",
                "net_cum_pct": "compounded net return inside the segment, reset to 1 at segment start.",
                "max_drawdown_pct": "max drawdown inside the segment, reset to 1 at segment start.",
                "open_rate_pct": "gate active rate; plain/veto are always open by definition.",
            },
        },
        "input_paths": {
            "monthly_detail": str(DETAIL_PATH.relative_to(ROOT)),
            "percentile_detail": str(PCT_DETAIL_PATH.relative_to(ROOT)),
            "monthly_summary": str(MONTHLY_SUMMARY_PATH.relative_to(ROOT)),
            "percentile_summary": str(PCT_SUMMARY_PATH.relative_to(ROOT)),
        },
        "output_paths": {
            "overall_csv": str(OVERALL_PATH.relative_to(ROOT)),
            "annual_csv": str(ANNUAL_PATH.relative_to(ROOT)),
            "regime_csv": str(REGIME_PATH.relative_to(ROOT)),
            "rolling_csv": str(ROLLING_PATH.relative_to(ROOT)),
            "monthly_csv": str(MONTHLY_PATH.relative_to(ROOT)),
            "site": str(SITE_PATH.relative_to(ROOT)),
        },
        "sample": {
            "start_utc": to_iso(df["timestamp_ts"].min()),
            "end_utc": to_iso(df["timestamp_ts"].max()),
            "rebalances": int(len(df)),
            "months": int(df["month"].nunique()),
            "years": [int(x) for x in sorted(df["year"].unique())],
        },
        "overall": overall.to_dict(orient="records"),
        "anchors": {
            "monthly_volume_raw_fixed_gate_from_existing_summary": monthly_summary.get("metrics", {}).get("monthly_volume_rebuild", {}).get("baseline_plus_veto_plus_gate", {}),
            "percentile_review_frozen_decision": pct_summary.get("frozen_decision", {}),
            "percentile_review_recommendation": pct_summary.get("recommendation", {}),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    pct_cols = {"net_cum_pct", "max_drawdown_pct", "win_rate_pct", "open_rate_pct"}
    bps_cols = {"net_mean_bps"}
    x_cols = {"avg_turnover_x"}
    int_cols = {"months", "rebalances", "active_rebalances"}
    long_cols = ["segment_type", "segment", "label", "months", "rebalances", "net_mean_bps", "net_cum_pct", "max_drawdown_pct", "open_rate_pct", "win_rate_pct", "avg_turnover_x", "avg_eligible_universe_size"]

    overall_html = render_table(overall, columns=long_cols[2:], pct_cols=pct_cols, bps_cols=bps_cols, x_cols=x_cols, int_cols=int_cols)
    annual_html = render_table(annual, columns=long_cols[1:], pct_cols=pct_cols, bps_cols=bps_cols, x_cols=x_cols, int_cols=int_cols)
    regime_html = render_table(regime, columns=long_cols, pct_cols=pct_cols, bps_cols=bps_cols, x_cols=x_cols, int_cols=int_cols)
    rolling_html = render_table(rolling, columns=long_cols, pct_cols=pct_cols, bps_cols=bps_cols, x_cols=x_cols, int_cols=int_cols)

    wide_annual = strategy_pivot(annual, "calendar_year")
    wide_regime_cal = strategy_pivot(regime[regime["segment_type"] == "regime_calendar_phase"])
    wide_cols = list(wide_annual.columns)
    wide_pct_cols = {c for c in wide_cols if any(k in c for k in ["net_cum_pct", "max_drawdown_pct", "open_rate_pct"])}
    wide_bps_cols = {c for c in wide_cols if "net_mean_bps" in c}
    wide_annual_html = render_table(wide_annual, columns=wide_cols, pct_cols=wide_pct_cols, bps_cols=wide_bps_cols)
    wide_regime_html = render_table(wide_regime_cal, columns=list(wide_regime_cal.columns), pct_cols={c for c in wide_regime_cal.columns if any(k in c for k in ["net_cum_pct", "max_drawdown_pct", "open_rate_pct"])}, bps_cols={c for c in wide_regime_cal.columns if "net_mean_bps" in c})

    # Key read-through rows for the page hero.
    overall_key = overall.set_index("strategy")
    verdict_items = []
    for s in [spec["strategy"] for spec in STRATEGIES]:
        r = overall_key.loc[s]
        verdict_items.append(
            f"<li><b>{escape(r['label'])}</b>: mean {fmt_bps(r['net_mean_bps'])}, cum {fmt_pct(r['net_cum_pct'])}, DD {fmt_pct(r['max_drawdown_pct'])}, open {fmt_pct(r['open_rate_pct'])}</li>"
        )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rank213 monthly-volume 分段稳定性</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1240px; margin: 32px auto; padding: 0 18px; line-height: 1.62; color: #111827; background: #f8fafc; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    .hero, .card {{ border: 1px solid #e5e7eb; background: white; border-radius: 16px; padding: 18px 20px; margin: 16px 0; box-shadow: 0 1px 2px rgba(15,23,42,0.03); }}
    .muted {{ color:#64748b; }}
    .warn {{ color:#92400e; background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:12px 14px; }}
    .good {{ color:#166534; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:12px 14px; }}
    .pill {{ display:inline-block; padding:4px 10px; margin:2px 4px 2px 0; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; }}
    .table-wrap {{ overflow-x:auto; margin: 12px 0; }}
    table {{ border-collapse: collapse; min-width: 1040px; width: 100%; background:white; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 7px 9px; text-align: right; white-space: nowrap; font-size: 13px; }}
    th {{ background:#f1f5f9; color:#334155; position: sticky; top: 0; z-index: 1; }}
    td:first-child, th:first-child, td:nth-child(2), th:nth-child(2), td:nth-child(3), th:nth-child(3) {{ text-align: left; }}
    code {{ background:#f1f5f9; border-radius: 6px; padding: 2px 5px; }}
    a {{ color:#2563eb; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
  </style>
</head>
<body>
  <div class="hero">
    <h1>Rank213 monthly-volume causal universe：分段稳定性</h1>
    <p class="muted">本页只看 <b>monthly volume rebuild</b> 口径：每月用上一完整自然月 Binance UM perpetual 1d quote_volume 选 top30，再跑 Rank213。目标是把 plain / veto / fixed gate / percentile gate 四条证据链并排，检查年度、regime、3y/5y 窗口稳定性。</p>
    <p>
      <span class="pill">sample {escape(str(summary['sample']['start_utc']))} → {escape(str(summary['sample']['end_utc']))}</span>
      <span class="pill">{summary['sample']['rebalances']} rebalances</span>
      <span class="pill">{summary['sample']['months']} months</span>
      <span class="pill">percentile gate q={PCT_GATE_Q:.0f}</span>
    </p>
    <div class="warn"><b>读法：</b>plain/veto 的 open rate 恒为 100%；gate 线的 open rate 就是开门率。cum/DD 都在每个 segment 内重新归一化，避免跨段权益曲线污染。</div>
  </div>

  <div class="card">
    <h2>结论快照（全样本）</h2>
    <ul>{''.join(verdict_items)}</ul>
    <p class="muted">直接结论：monthly-volume 下 baseline 本身并不稳；veto 不是修复器，反而在全样本更差。固定阈值 gate 太稀疏，只把亏损缩小但没转正；percentile q60 能把全样本拉到轻微正值，但 DD 仍很深，不能当“已过关”。</p>
  </div>

  <div class="card">
    <h2>全样本四线长表</h2>
    {overall_html}
  </div>

  <div class="card">
    <h2>按年切：四线并排宽表</h2>
    <p class="muted">指标后缀含义：net_mean_bps / net_cum_pct / max_drawdown_pct / open_rate_pct。</p>
    {wide_annual_html}
  </div>

  <div class="card">
    <h2>按年切：可读长表</h2>
    {annual_html}
  </div>

  <div class="card">
    <h2>按 regime 切：calendar phase 宽表</h2>
    <p class="muted">先给最直观的研究阶段切分：2020-2021 / 2022-2023 / 2024-2026。后面再给 BTC 64-bar trend 与横截面离散度 tercile 的环境切分。</p>
    {wide_regime_html}
  </div>

  <div class="card">
    <h2>按 regime 切：完整长表</h2>
    {regime_html}
  </div>

  <div class="card">
    <h2>3y / 5y rolling window 稳定性</h2>
    <p class="muted">只保留至少 24 个月的 3y 窗口、至少 36 个月的 5y 窗口；2026 是 YTD，因此尾部窗口会标注 YTD。</p>
    {rolling_html}
  </div>

  <div class="card">
    <h2>落盘产物</h2>
    <ul>
      <li><code>{escape(str(SUMMARY_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(ANNUAL_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(REGIME_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(ROLLING_PATH.relative_to(ROOT)))}</code></li>
      <li><code>{escape(str(MONTHLY_PATH.relative_to(ROOT)))}</code></li>
    </ul>
  </div>
</body>
</html>
"""
    SITE_PATH.write_text(html, encoding="utf-8")
    print(f"[ok] wrote {SUMMARY_PATH}")
    print(f"[ok] wrote {ANNUAL_PATH}")
    print(f"[ok] wrote {REGIME_PATH}")
    print(f"[ok] wrote {ROLLING_PATH}")
    print(f"[ok] wrote {SITE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
