#!/usr/bin/env python3
"""Build the public factor evaluation page.

The page is a static, interactive diagnostic browser:
  - scan-friendly factor table
  - click a factor to inspect horizon metrics, stability, quantiles, and notes
  - no backend and no raw CSV dump
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd


EVAL_DIR = Path("research/factor_runs/crypto_top50_factor_library/factor_level_evaluation")
STATE_PATH = Path("research/factor_runs/crypto_top50_factor_library/factor_library_state.json")
OUT = Path("reports/site/factor-library/factor-evaluation.html")
HORIZONS = ["1h", "4h", "24h", "72h"]
REDUNDANCY_RANK = {
    "NEAR_DUPLICATE": 3,
    "HIGH_REDUNDANCY": 2,
    "MODERATE_REDUNDANCY": 1,
    "LOW_REDUNDANCY": 0,
    "NO_CURRENT_PAIR": -1,
}


def load_csv(name: str) -> pd.DataFrame:
    path = EVAL_DIR / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def safe_float(value):
    if value is None or pd.isna(value):
        return None
    return round(float(value), 8)


def fmt(value, digits=4, signed=True):
    if value is None or pd.isna(value):
        return "—"
    sign = "+" if signed else ""
    return f"{float(value):{sign}.{digits}f}"


def fmt_pct(value):
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value) * 100:.1f}%"


def classify_metric(value, strong=0.03, watch=0.02):
    if value is None or pd.isna(value):
        return "muted"
    v = abs(float(value))
    if v >= strong:
        return "strong"
    if v >= watch:
        return "watch"
    return "plain"


def stability_summary(period_df: pd.DataFrame, fid: str, horizon: str) -> dict:
    if period_df.empty:
        return {"label": "NO_DATA", "positive_ratio": None, "n_months": 0, "worst": None, "best": None}
    sub = period_df[(period_df["factor_name"] == fid) & (period_df["horizon"] == horizon)]
    if sub.empty or "direction_adjusted_mean_rank_ic" not in sub:
        return {"label": "NO_DATA", "positive_ratio": None, "n_months": 0, "worst": None, "best": None}
    vals = sub["direction_adjusted_mean_rank_ic"].dropna()
    if vals.empty:
        return {"label": "NO_DATA", "positive_ratio": None, "n_months": 0, "worst": None, "best": None}
    ratio = float((vals > 0).mean())
    n_months = int(vals.shape[0])
    if ratio >= 0.8:
        label = "STABLE"
    elif ratio >= 0.6:
        label = "MODERATE"
    elif ratio >= 0.4:
        label = "MIXED"
    else:
        label = "UNSTABLE"
    best_row = sub.loc[sub["direction_adjusted_mean_rank_ic"].idxmax()]
    worst_row = sub.loc[sub["direction_adjusted_mean_rank_ic"].idxmin()]
    return {
        "label": label,
        "positive_ratio": round(ratio, 4),
        "n_months": n_months,
        "best": {
            "period": str(best_row.get("period", "")),
            "adj_ic": safe_float(best_row.get("direction_adjusted_mean_rank_ic")),
        },
        "worst": {
            "period": str(worst_row.get("period", "")),
            "adj_ic": safe_float(worst_row.get("direction_adjusted_mean_rank_ic")),
        },
    }


def quantile_shape(quantile_df: pd.DataFrame, fid: str, horizon: str) -> dict:
    empty = {"label": "NO_DATA", "returns": []}
    if quantile_df.empty:
        return empty
    sub = quantile_df[(quantile_df["factor_name"] == fid) & (quantile_df["horizon"] == horizon)]
    if sub.empty:
        return empty
    buckets = sub[sub["bucket"].astype(str) != "LONG_SHORT"].copy()
    if buckets.empty:
        return empty
    buckets["bucket_num"] = pd.to_numeric(buckets["bucket"], errors="coerce")
    buckets = buckets.sort_values("bucket_num")
    returns = [safe_float(v) for v in buckets["mean_forward_return"].tolist()]
    clean = [v for v in returns if v is not None]
    if len(clean) < 3:
        label = "INSUFFICIENT"
    else:
        diffs = [clean[i + 1] - clean[i] for i in range(len(clean) - 1)]
        if all(d > 0 for d in diffs):
            label = "MONOTONIC_UP"
        elif all(d < 0 for d in diffs):
            label = "MONOTONIC_DOWN"
        else:
            turns = sum(1 for i in range(1, len(diffs)) if diffs[i] * diffs[i - 1] < 0)
            label = "NEAR_MONOTONIC" if turns <= 1 else "NON_MONOTONIC"
    return {"label": label, "returns": returns}


def choose_best_horizon(review_row: pd.Series | None, metric_rows: pd.DataFrame) -> str:
    if review_row is not None:
        hz = review_row.get("best_adj_ic_horizon")
        if isinstance(hz, str) and hz in HORIZONS:
            return hz
    if metric_rows.empty:
        return "1h"
    rows = metric_rows.copy()
    rows["abs_adj_ic"] = rows["direction_adjusted_mean_rank_ic"].abs()
    best = rows.sort_values("abs_adj_ic", ascending=False).iloc[0]
    return str(best.get("horizon", "1h"))


def redundancy_lookup(redundancy_df: pd.DataFrame) -> dict[str, dict]:
    """Return the strongest available redundancy diagnostic for each factor."""
    lookup: dict[str, list[dict]] = {}
    if redundancy_df.empty:
        return {}

    for _, row in redundancy_df.iterrows():
        left = str(row.get("factor_i", ""))
        right = str(row.get("factor_j", ""))
        if not left or not right:
            continue
        pair = {
            "factor_i": left,
            "factor_j": right,
            "family_i": str(row.get("family_i", "")),
            "family_j": str(row.get("family_j", "")),
            "same_family": bool(row.get("same_family", False)),
            "spearman_corr": safe_float(row.get("spearman_corr")),
            "abs_spearman_corr": safe_float(row.get("abs_spearman_corr")),
            "pearson_corr": safe_float(row.get("pearson_corr")),
            "n_pairwise_obs": None if pd.isna(row.get("n_pairwise_obs")) else int(row.get("n_pairwise_obs")),
            "redundancy_level": str(row.get("redundancy_level", "LOW_REDUNDANCY")),
            "recommendation": str(row.get("recommendation", "")),
        }
        lookup.setdefault(left, []).append({**pair, "nearest_factor": right, "nearest_family": pair["family_j"]})
        lookup.setdefault(right, []).append({**pair, "nearest_factor": left, "nearest_family": pair["family_i"]})

    out = {}
    for fid, pairs in lookup.items():
        pairs = sorted(
            pairs,
            key=lambda p: (
                REDUNDANCY_RANK.get(p["redundancy_level"], -1),
                p["abs_spearman_corr"] or 0,
            ),
            reverse=True,
        )
        strongest = pairs[0]
        out[fid] = {
            "redundancy_level": strongest["redundancy_level"],
            "nearest_existing_factors": pairs[:3],
            "nearest_abs_spearman_corr": strongest["abs_spearman_corr"],
            "nearest_factor": strongest["nearest_factor"],
            "recommendation": strongest["recommendation"],
        }
    return out


def build_payload() -> tuple[dict, list[dict]]:
    manifest = json.loads((EVAL_DIR / "factor_level_evaluation_manifest.json").read_text())
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    metric_df = load_csv("factor_level_metric_panel.csv")
    review_df = load_csv("factor_level_candidate_review.csv")
    period_df = load_csv("factor_level_period_ic_summary.csv")
    quantile_df = load_csv("factor_level_quantile_return_summary.csv")
    formula_df = load_csv("factor_level_formula_catalog.csv")
    redundancy_df = load_csv("factor_redundancy.csv")
    redundancy_by_factor = redundancy_lookup(redundancy_df)

    factors: list[dict] = []
    for fid in sorted(metric_df["factor_name"].unique()):
        mrows = metric_df[metric_df["factor_name"] == fid]
        first = mrows.iloc[0]
        rmatch = review_df[review_df["factor_name"] == fid] if not review_df.empty else pd.DataFrame()
        review = rmatch.iloc[0] if not rmatch.empty else None
        fmatch = formula_df[formula_df["factor_name"] == fid] if not formula_df.empty else pd.DataFrame()
        formula = fmatch.iloc[0] if not fmatch.empty else None
        best_hz = choose_best_horizon(review, mrows)
        best_row = mrows[mrows["horizon"] == best_hz].iloc[0] if not mrows[mrows["horizon"] == best_hz].empty else first

        horizon_metrics = {}
        for hz in HORIZONS:
            hrow = mrows[mrows["horizon"] == hz]
            if hrow.empty:
                horizon_metrics[hz] = None
                continue
            row = hrow.iloc[0]
            horizon_metrics[hz] = {
                "adj_ic": safe_float(row.get("direction_adjusted_mean_rank_ic")),
                "raw_ic": safe_float(row.get("raw_mean_rank_ic")),
                "adj_icir": safe_float(row.get("direction_adjusted_icir")),
                "raw_icir": safe_float(row.get("raw_icir")),
                "t_stat": safe_float(row.get("t_stat")),
                "win_rate": safe_float(row.get("ic_win_rate_adjusted")),
                "coverage": safe_float(row.get("coverage")),
                "missing_rate": safe_float(row.get("missing_rate")),
                "ls_spread": safe_float(row.get("long_short_spread_mean")),
                "ls_t": safe_float(row.get("long_short_spread_t_stat")),
                "ls_win_rate": safe_float(row.get("long_short_win_rate")),
                "stability": stability_summary(period_df, fid, hz),
                "quantile": quantile_shape(quantile_df, fid, hz),
            }

        review_bucket = str(review.get("review_bucket", "UNKNOWN")) if review is not None else "UNKNOWN"
        consistency = str(review.get("rankic_longshort_consistency", "N/A")) if review is not None else "N/A"
        best_adj_ic = safe_float(review.get("best_adj_ic")) if review is not None else safe_float(best_row.get("direction_adjusted_mean_rank_ic"))
        best_icir = safe_float(review.get("best_direction_adjusted_icir")) if review is not None else safe_float(best_row.get("direction_adjusted_icir"))
        best_ls = safe_float(review.get("best_long_short_spread")) if review is not None else safe_float(best_row.get("long_short_spread_mean"))
        best_ls_t = safe_float(review.get("best_long_short_t_stat")) if review is not None else safe_float(best_row.get("long_short_spread_t_stat"))
        best_win = safe_float(review.get("best_ic_win_rate_adjusted")) if review is not None else safe_float(best_row.get("ic_win_rate_adjusted"))
        redundancy = redundancy_by_factor.get(fid, {
            "redundancy_level": "NO_CURRENT_PAIR",
            "nearest_existing_factors": [],
            "nearest_abs_spearman_corr": None,
            "nearest_factor": "",
            "recommendation": "No pair for this factor appears in the current redundancy artifact.",
        })

        factors.append({
            "factor_id": fid,
            "family": str(first.get("category", "unknown")),
            "expected_direction": str(first.get("expected_direction", "unknown")),
            "status": str(first.get("status", "UNKNOWN")),
            "used_in_signal": bool(first.get("used_in_current_signal", False)),
            "required_columns": str(first.get("required_columns", "")),
            "lookback_window": None if pd.isna(first.get("lookback_window")) else str(first.get("lookback_window")),
            "formula_proxy": str(formula.get("formula_proxy", first.get("formula_proxy", ""))) if formula is not None else str(first.get("formula_proxy", "")),
            "review_bucket": review_bucket,
            "review_notes": str(review.get("review_notes", "")) if review is not None else "",
            "rankic_longshort_consistency": consistency,
            "best_horizon": best_hz,
            "best_adj_ic": best_adj_ic,
            "best_adj_icir": best_icir,
            "best_ls_spread": best_ls,
            "best_ls_t": best_ls_t,
            "best_win_rate": best_win,
            "coverage_min": safe_float(review.get("coverage_min")) if review is not None else safe_float(first.get("coverage")),
            "missing_rate_max": safe_float(review.get("missing_rate_max")) if review is not None else safe_float(first.get("missing_rate")),
            "redundancy_level": redundancy["redundancy_level"],
            "nearest_existing_factors": redundancy["nearest_existing_factors"],
            "nearest_abs_spearman_corr": redundancy["nearest_abs_spearman_corr"],
            "nearest_factor": redundancy["nearest_factor"],
            "redundancy_recommendation": redundancy["recommendation"],
            "horizons": horizon_metrics,
        })

    summary = {
        "registered": state.get("registered_factors", manifest.get("total_registered_factors", len(factors))),
        "computed": state.get("computed_factor_values", manifest.get("computed_factors", 0)),
        "missing": state.get("missing_factor_values", len(manifest.get("missing_factor_ids", []))),
        "active_signal_factors": state.get("active_signal_factors", sum(1 for f in factors if f["used_in_signal"])),
        "generated_at": state.get("generated_at", manifest.get("generated_at", "")),
    }
    return summary, factors


def build_table_rows(factors: list[dict]) -> str:
    bucket_rank = {
        "ACTIVE_IN_SIGNAL_REVIEW": 0,
        "DIRECTION_REVIEW_REQUIRED": 1,
        "TAIL_OR_MONOTONICITY_REVIEW_REQUIRED": 2,
        "CONDITIONAL_DIRECTION_REVIEW": 3,
        "RANKIC_STRONG_LONGSHORT_WEAK": 4,
        "LONGSHORT_STRONG_RANKIC_WEAK": 5,
        "PASS_DIAGNOSTIC": 6,
        "WEAK_OR_NOISY": 7,
        "MISSING_INPUT": 8,
        "METADATA_REVIEW": 9,
    }
    sorted_factors = sorted(
        factors,
        key=lambda f: (
            bucket_rank.get(f["review_bucket"], 99),
            -(abs(f["best_adj_ic"]) if f["best_adj_ic"] is not None else 0),
        ),
    )
    rows = []
    for f in sorted_factors:
        fid = html.escape(f["factor_id"])
        best_ic = fmt(f["best_adj_ic"], 4)
        best_icir = fmt(f["best_adj_icir"], 3)
        ls = fmt(f["best_ls_spread"], 5)
        ls_t = fmt(f["best_ls_t"], 2, signed=False)
        win = fmt_pct(f["best_win_rate"])
        missing = fmt_pct(f["missing_rate_max"])
        redundancy = html.escape(f["redundancy_level"])
        nearest = html.escape(f["nearest_factor"] or "—")
        nearest_corr = fmt(f["nearest_abs_spearman_corr"], 3, signed=False)
        signal = "signal" if f["used_in_signal"] else ""
        bucket = html.escape(f["review_bucket"])
        rows.append(
            f"<tr data-factor=\"{fid}\" class=\"factor-row {signal}\">"
            f"<td><button class=\"factor-link\" type=\"button\">{fid}</button></td>"
            f"<td>{html.escape(f['family'])}</td>"
            f"<td>{html.escape(f['expected_direction'])}</td>"
            f"<td><span class=\"bucket {bucket.lower()}\">{bucket}</span></td>"
            f"<td>{html.escape(f['best_horizon'])}</td>"
            f"<td class=\"num {classify_metric(f['best_adj_ic'])}\">{best_ic}</td>"
            f"<td class=\"num\">{best_icir}</td>"
            f"<td class=\"num\">{win}</td>"
            f"<td class=\"num {classify_metric(f['best_ls_spread'], strong=0.002, watch=0.001)}\">{ls}</td>"
            f"<td class=\"num\">{ls_t}</td>"
            f"<td>{html.escape(f['rankic_longshort_consistency'])}</td>"
            f"<td><span class=\"redundancy {redundancy.lower()}\">{redundancy}</span><br><span class=\"small\">{nearest} {nearest_corr}</span></td>"
            f"<td class=\"num\">{missing}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render() -> str:
    summary, factors = build_payload()
    payload = json.dumps({"summary": summary, "factors": factors}, ensure_ascii=False, separators=(",", ":"))
    payload_for_script = payload.replace("<", "\\u003c").replace("</", "<\\/")
    rows_html = build_table_rows(factors)
    bucket_counts = pd.Series([f["review_bucket"] for f in factors]).value_counts().to_dict()
    bucket_cards = "\n".join(
        f"<div class=\"mini-stat\"><strong>{count}</strong><span>{html.escape(bucket)}</span></div>"
        for bucket, count in sorted(bucket_counts.items(), key=lambda x: (-x[1], x[0]))
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor Evaluation</title>
<style>
:root{{--bg:#0f172a;--panel:#111c31;--panel2:#17243a;--border:#26364f;--text:#e5edf8;--muted:#8ea0b8;--blue:#60a5fa;--green:#34d399;--amber:#fbbf24;--red:#f87171;--purple:#c084fc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.5;padding:20px}}
a{{color:var(--blue);text-decoration:none}}h1{{font-size:24px;margin:0 0 6px}}h2{{font-size:17px;margin:24px 0 10px}}h3{{font-size:14px;margin:16px 0 8px;color:#cbd5e1}}
.topbar{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:16px}}.subtitle{{color:var(--muted);font-size:13px}}
.notice{{background:#2b1820;border:1px solid #7f1d1d;color:#fecaca;border-radius:8px;padding:12px 14px;margin:14px 0;font-size:13px}}
.stats,.bucket-grid{{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}}.stat,.mini-stat{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 12px;min-width:110px}}
.stat strong,.mini-stat strong{{display:block;font-size:22px}}.stat span,.mini-stat span{{color:var(--muted);font-size:11px}}
.layout{{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(360px,.65fr);gap:16px;align-items:start}}@media(max-width:1100px){{.layout{{grid-template-columns:1fr}}}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:14px}}.detail{{position:sticky;top:16px}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}}input,select{{background:#0b1220;color:var(--text);border:1px solid var(--border);border-radius:7px;padding:8px 10px;font-size:13px}}input{{min-width:240px;flex:1}}
table{{width:100%;border-collapse:collapse;font-size:12px}}th{{background:#142035;color:var(--muted);text-align:left;padding:8px;position:sticky;top:0;z-index:1}}td{{border-bottom:1px solid var(--border);padding:7px 8px;vertical-align:middle}}tr.factor-row{{cursor:pointer}}tr.factor-row:hover,tr.factor-row.selected{{background:#1d2d47}}tr.signal td:first-child:before{{content:'★ ';color:var(--blue)}}.num{{text-align:right;font-variant-numeric:tabular-nums}}.strong{{color:var(--green);font-weight:700}}.watch{{color:var(--amber);font-weight:700}}.plain{{color:var(--text)}}.muted{{color:var(--muted)}}
.table-wrap{{overflow-x:auto}}
.factor-link{{background:none;border:0;color:var(--blue);font:inherit;font-weight:650;cursor:pointer;padding:0;text-align:left}}.bucket,.redundancy{{display:inline-block;border-radius:999px;padding:2px 7px;font-size:10px;background:#334155;color:#e2e8f0;white-space:nowrap}}.bucket.active_in_signal_review{{background:#1d4ed8}}.bucket.direction_review_required,.bucket.tail_or_monotonicity_review_required{{background:#7f1d1d}}.bucket.conditional_direction_review{{background:#581c87}}.bucket.missing_input{{background:#991b1b}}.bucket.longshort_strong_rankic_weak,.bucket.rankic_strong_longshort_weak{{background:#92400e}}.redundancy.near_duplicate,.redundancy.high_redundancy{{background:#7f1d1d}}.redundancy.moderate_redundancy{{background:#92400e}}.redundancy.low_redundancy{{background:#166534}}.redundancy.no_current_pair{{background:#475569}}
.tabs{{display:flex;gap:6px;margin:10px 0}}.tab{{border:1px solid var(--border);background:#0b1220;color:var(--muted);padding:5px 9px;border-radius:999px;cursor:pointer}}.tab.active{{color:#fff;background:#2563eb;border-color:#2563eb}}
.metric-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}@media(max-width:700px){{.metric-grid{{grid-template-columns:1fr 1fr}}}}.metric{{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:8px}}.metric span{{display:block;color:var(--muted);font-size:10px;text-transform:uppercase}}.metric strong{{font-size:15px}}
.bar-svg{{width:100%;height:120px;background:#0b1220;border:1px solid var(--border);border-radius:8px}}.small{{font-size:12px;color:var(--muted)}}.kv{{display:grid;grid-template-columns:135px 1fr;gap:6px;font-size:12px;margin-top:10px}}.kv div:nth-child(odd){{color:var(--muted)}}.footer{{margin-top:22px;border-top:1px solid var(--border);padding-top:12px;color:var(--muted);font-size:12px;display:flex;gap:12px;flex-wrap:wrap}}
</style>
</head>
<body>
<div class="topbar">
  <div>
    <h1>Factor Evaluation</h1>
    <div class="subtitle">Factor-level diagnostics · click any factor for details · generated from canonical evaluation outputs</div>
  </div>
  <div class="subtitle"><a href="index.html">Home</a> · <a href="actual-script-map.html">Pipeline Map</a> · <a href="signal-evaluation-summary.html">Signal Evaluation</a></div>
</div>
<div class="notice">Diagnostic only. This page evaluates factor behavior; it does not promote factors into signals and does not make production, live trading, tradeability, or alpha claims.</div>
<div class="stats">
  <div class="stat"><strong>{summary['registered']}</strong><span>Registered</span></div>
  <div class="stat"><strong>{summary['computed']}</strong><span>Computed factor_values</span></div>
  <div class="stat"><strong>{summary['missing']}</strong><span>Missing input/FV</span></div>
  <div class="stat"><strong>{summary['active_signal_factors']}</strong><span>Active signal factors</span></div>
</div>
<div class="card">
  <h2>Review Bucket Distribution</h2>
  <div class="bucket-grid">{bucket_cards}</div>
</div>
<div class="layout">
  <main>
    <div class="card">
      <h2>Factor Scoreboard</h2>
      <div class="small">Best horizon is selected by candidate review. IC/ICIR are direction-adjusted. LS is long-short spread. Redundancy is shown when available from factor_redundancy.csv. Divergent factors require review even when IC is strong.</div>
      <div class="controls">
        <input id="search" placeholder="Search factor, family, bucket...">
        <select id="bucketFilter"><option value="">All buckets</option></select>
        <select id="signalFilter"><option value="">All factors</option><option value="signal">Active in signal</option><option value="non_signal">Not in signal</option></select>
      </div>
      <div class="table-wrap"><table id="factorTable">
        <thead><tr><th>Factor</th><th>Family</th><th>Direction</th><th>Bucket</th><th>Best H</th><th>Best IC</th><th>ICIR</th><th>Win</th><th>LS</th><th>LS t</th><th>Consistency</th><th>Redundancy</th><th>Missing</th></tr></thead>
        <tbody>{rows_html}</tbody>
      </table></div>
    </div>
  </main>
  <aside class="detail">
    <div class="card" id="detailCard"><h2>Factor Detail</h2><div class="small">Select a factor from the table.</div></div>
  </aside>
</div>
<div class="footer">
  <span>Generated: {html.escape(str(summary.get('generated_at','')))}</span>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/START_HERE.md">Start Here</a>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md">Governance</a>
</div>
<script id="factorPayload" type="application/json">{payload_for_script}</script>
<script>
const DATA = JSON.parse(document.getElementById('factorPayload').textContent);
const factors = DATA.factors;
const byId = new Map(factors.map(f => [f.factor_id, f]));
const table = document.getElementById('factorTable');
const search = document.getElementById('search');
const bucketFilter = document.getElementById('bucketFilter');
const signalFilter = document.getElementById('signalFilter');
const detailCard = document.getElementById('detailCard');
const horizons = ["1h","4h","24h","72h"];
const buckets = [...new Set(factors.map(f => f.review_bucket))].sort();
buckets.forEach(b => {{ const o=document.createElement('option'); o.value=b; o.textContent=b; bucketFilter.appendChild(o); }});
function esc(v) {{ return String(v ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c])); }}
function num(v,d=4,signed=true) {{ if(v===null || v===undefined || Number.isNaN(v)) return '—'; const sign=signed && v>=0?'+':''; return sign + Number(v).toFixed(d); }}
function pct(v) {{ if(v===null || v===undefined || Number.isNaN(v)) return '—'; return (Number(v)*100).toFixed(1)+'%'; }}
function count(v) {{ if(v===null || v===undefined || Number.isNaN(v)) return '—'; return Math.round(Number(v)).toLocaleString('en-US'); }}
function cls(v, strong=0.03, watch=0.02) {{ if(v===null || v===undefined || Number.isNaN(v)) return 'muted'; const a=Math.abs(Number(v)); return a>=strong?'strong':a>=watch?'watch':'plain'; }}
function barChart(vals) {{
  const clean = vals.map(v => v===null || v===undefined ? 0 : Number(v));
  const max = Math.max(...clean.map(v => Math.abs(v)), 0.000001);
  const w=360,h=110,mid=55,bw=42,gap=22,start=32;
  let s=`<svg viewBox="0 0 ${{w}} ${{h}}" class="bar-svg" preserveAspectRatio="none"><line x1="8" y1="${{mid}}" x2="${{w-8}}" y2="${{mid}}" stroke="#334155"/>`;
  clean.forEach((v,i)=>{{ const bh=Math.abs(v)/max*42; const x=start+i*(bw+gap); const y=v>=0?mid-bh:mid; const c=v>=0?'#34d399':'#f87171'; s+=`<rect x="${{x}}" y="${{y}}" width="${{bw}}" height="${{bh}}" fill="${{c}}" rx="3"/><text x="${{x+bw/2}}" y="102" text-anchor="middle" fill="#8ea0b8" font-size="10">Q${{i+1}}</text>`; }});
  return s+'</svg>';
}}
function horizonTabs(f, selected) {{ return `<div class="tabs">${{horizons.map(h => `<button class="tab ${{h===selected?'active':''}}" data-hz="${{h}}">${{h}}</button>`).join('')}}</div>`; }}
function redundancyRows(f) {{
  const rows = f.nearest_existing_factors || [];
  if(!rows.length) return '<div class="small">No pair for this factor appears in the current redundancy artifact.</div>';
  return `<table><thead><tr><th>Nearest Factor</th><th>Level</th><th>Spearman</th><th>Pearson</th><th>Obs</th></tr></thead><tbody>${{rows.map(r => `<tr><td>${{esc(r.nearest_factor)}} <span class="small">${{esc(r.nearest_family || '')}}</span></td><td><span class="redundancy ${{esc(String(r.redundancy_level || '').toLowerCase())}}">${{esc(r.redundancy_level || '—')}}</span></td><td class="num">${{num(r.spearman_corr,3)}}</td><td class="num">${{num(r.pearson_corr,3)}}</td><td class="num">${{esc(r.n_pairwise_obs ?? '—')}}</td></tr>`).join('')}}</tbody></table>`;
}}
function renderDetail(fid, hz) {{
  const f = byId.get(fid); if(!f) return;
  hz = hz || f.best_horizon || '1h';
  const h = f.horizons[hz] || {{}};
  const q = h.quantile || {{}};
  const st = h.stability || {{}};
  detailCard.innerHTML = `
    <h2>${{esc(f.factor_id)}}</h2>
    <div class="small">${{esc(f.family)}} · direction=${{esc(f.expected_direction)}} · best horizon=${{esc(f.best_horizon)}}</div>
    ${{horizonTabs(f, hz)}}
    <div class="metric-grid">
      <div class="metric"><span>Adj IC</span><strong class="${{cls(h.adj_ic)}}">${{num(h.adj_ic,4)}}</strong></div>
      <div class="metric"><span>Adj ICIR</span><strong>${{num(h.adj_icir,3)}}</strong></div>
      <div class="metric"><span>IC win rate</span><strong>${{pct(h.win_rate)}}</strong></div>
      <div class="metric"><span>LS spread</span><strong class="${{cls(h.ls_spread,0.002,0.001)}}">${{num(h.ls_spread,5)}}</strong></div>
      <div class="metric"><span>LS t-stat</span><strong>${{num(h.ls_t,2,false)}}</strong></div>
      <div class="metric"><span>Coverage obs</span><strong>${{count(h.coverage)}}</strong></div>
    </div>
    <h3>Quantile Return Shape</h3>
    <div class="small">Shape: ${{esc(q.label || 'NO_DATA')}}. Bars show mean forward return by factor quantile for selected horizon.</div>
    ${{barChart(q.returns || [])}}
    <h3>Monthly Stability</h3>
    <div class="metric-grid">
      <div class="metric"><span>Label</span><strong>${{esc(st.label || 'NO_DATA')}}</strong></div>
      <div class="metric"><span>Positive months</span><strong>${{pct(st.positive_ratio)}}</strong></div>
      <div class="metric"><span>Months</span><strong>${{esc(st.n_months ?? 0)}}</strong></div>
      <div class="metric"><span>Best month</span><strong>${{esc(st.best?.period || '—')}} ${{num(st.best?.adj_ic,4)}}</strong></div>
      <div class="metric"><span>Worst month</span><strong>${{esc(st.worst?.period || '—')}} ${{num(st.worst?.adj_ic,4)}}</strong></div>
      <div class="metric"><span>Consistency</span><strong>${{esc(f.rankic_longshort_consistency)}}</strong></div>
    </div>
    <h3>Redundancy</h3>
    <div class="small">Nearest factors are based on the available current-mainline redundancy diagnostics. High redundancy means review is required before any later canonical use.</div>
    <div class="metric-grid">
      <div class="metric"><span>Level</span><strong><span class="redundancy ${{esc(String(f.redundancy_level || '').toLowerCase())}}">${{esc(f.redundancy_level || '—')}}</span></strong></div>
      <div class="metric"><span>Nearest factor</span><strong>${{esc(f.nearest_factor || '—')}}</strong></div>
      <div class="metric"><span>Abs Spearman</span><strong>${{num(f.nearest_abs_spearman_corr,3,false)}}</strong></div>
    </div>
    ${{redundancyRows(f)}}
    <div class="small">${{esc(f.redundancy_recommendation || '')}}</div>
    <h3>Review</h3>
    <div class="kv">
      <div>Decision bucket</div><div><span class="bucket ${{esc(f.review_bucket.toLowerCase())}}">${{esc(f.review_bucket)}}</span></div>
      <div>Review notes</div><div>${{esc(f.review_notes || '—')}}</div>
      <div>Formula proxy</div><div>${{esc(f.formula_proxy || '—')}}</div>
      <div>Required columns</div><div>${{esc(f.required_columns || '—')}}</div>
      <div>Lookback</div><div>${{esc(f.lookback_window || '—')}}</div>
      <div>Status</div><div>${{esc(f.status)}}</div>
    </div>`;
  detailCard.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => renderDetail(fid, btn.dataset.hz)));
}}
function applyFilters() {{
  const q = search.value.toLowerCase();
  const b = bucketFilter.value;
  const s = signalFilter.value;
  table.querySelectorAll('tbody tr').forEach(tr => {{
    const f = byId.get(tr.dataset.factor);
    const text = [f.factor_id,f.family,f.expected_direction,f.review_bucket,f.rankic_longshort_consistency].join(' ').toLowerCase();
    const okQ = !q || text.includes(q);
    const okB = !b || f.review_bucket === b;
    const okS = !s || (s==='signal' ? f.used_in_signal : !f.used_in_signal);
    tr.style.display = okQ && okB && okS ? '' : 'none';
  }});
}}
table.querySelectorAll('tbody tr').forEach(tr => tr.addEventListener('click', () => {{
  table.querySelectorAll('tr.selected').forEach(r => r.classList.remove('selected'));
  tr.classList.add('selected');
  renderDetail(tr.dataset.factor);
}}));
[search,bucketFilter,signalFilter].forEach(el => el.addEventListener('input', applyFilters));
if(factors.length) {{
  const first = factors.find(f => f.review_bucket === 'DIRECTION_REVIEW_REQUIRED') || factors[0];
  const row = table.querySelector(`tr[data-factor="${{CSS.escape(first.factor_id)}}"]`);
  if(row) row.classList.add('selected');
  renderDetail(first.factor_id);
}}
</script>
</body>
</html>"""


if __name__ == "__main__":
    html_out = render()
    OUT.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html_out)} bytes)")
