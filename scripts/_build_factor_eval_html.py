#!/usr/bin/env python3
"""Build the bilingual factor evaluation page.

Reads 6 CSV data sources from the crypto_top50_factor_library and produces
a single static HTML file with embedded JSON, CSS, and JS.

Data sources:
  1. factor_diagnostics/factor_diagnostics_summary.csv
  2. factor_diagnostics/factor_monthly_ic_series.csv
  3. factor_diagnostics/factor_monthly_long_short_series.csv
  4. factor_diagnostics/factor_cumulative_long_short_curve.csv
  5. factor_metadata/factor_bilingual_cards.csv
  6. factor_metadata/factor_card_qa_report.csv
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

# ── Paths ───────────────────────────────────────────────────────────────────
BASE = Path("research/factor_runs/crypto_top50_factor_library")
DIAG_DIR = BASE / "factor_diagnostics"
META_DIR = BASE / "factor_metadata"
OUT = Path("reports/site/factor-library/factor-evaluation.html")

HORIZONS = ["1h", "4h", "24h", "72h"]


# ── Helpers ─────────────────────────────────────────────────────────────────
def sf(v):
    """Safe float: return None for NaN, else rounded float."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    return round(float(v), 10)


def ss(v):
    """Safe string."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v).strip()


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


# ── Build JSON payload ──────────────────────────────────────────────────────
def build_payload() -> dict:
    diag = load_csv(DIAG_DIR / "factor_diagnostics_summary.csv")
    ic_series = load_csv(DIAG_DIR / "factor_monthly_ic_series.csv")
    ls_series = load_csv(DIAG_DIR / "factor_monthly_long_short_series.csv")
    cum_series = load_csv(DIAG_DIR / "factor_cumulative_long_short_curve.csv")
    cards = load_csv(META_DIR / "factor_bilingual_cards.csv")
    qa = load_csv(META_DIR / "factor_card_qa_report.csv")

    # ── Summary stats ──
    all_months = sorted(ic_series["month"].unique().tolist()) if not ic_series.empty else []
    quality_counts = cards["metadata_quality"].value_counts().to_dict() if not cards.empty else {}

    summary = {
        "factor_count": len(diag),
        "horizons": HORIZONS,
        "months": all_months,
        "month_count": len(all_months),
        "quality_counts": quality_counts,
    }

    # ── Build lookup dicts ──
    card_map = {}
    if not cards.empty:
        for _, r in cards.iterrows():
            card_map[r["factor_id"]] = r

    qa_map = {}
    if not qa.empty:
        for _, r in qa.iterrows():
            qa_map[r["factor_id"]] = r

    # ── Build factor list ──
    factors = []
    for _, drow in diag.iterrows():
        fid = str(drow["factor_id"])
        card = card_map.get(fid)
        qa_row = qa_map.get(fid)

        # Time series for this factor (all horizons)
        fic = ic_series[ic_series["factor_id"] == fid] if not ic_series.empty else pd.DataFrame()
        fls = ls_series[ls_series["factor_id"] == fid] if not ls_series.empty else pd.DataFrame()
        fcum = cum_series[cum_series["factor_id"] == fid] if not cum_series.empty else pd.DataFrame()

        best_hz = ss(drow.get("best_horizon", "1h")) or "1h"

        # Monthly IC for best horizon
        fic_best = fic[fic["horizon"] == best_hz].sort_values("month") if not fic.empty else pd.DataFrame()
        monthly_ic = []
        for _, r in fic_best.iterrows():
            monthly_ic.append({
                "month": ss(r["month"]),
                "rank_ic": sf(r["rank_ic"]),
                "rank_ic_adj": sf(r["rank_ic_adj"]),
                "n_obs": int(r["n_obs"]) if not pd.isna(r.get("n_obs")) else None,
                "positive_ic": bool(r["positive_ic"]) if not pd.isna(r.get("positive_ic")) else None,
            })

        # Monthly LS for best horizon
        fls_best = fls[fls["horizon"] == best_hz].sort_values("month") if not fls.empty else pd.DataFrame()
        monthly_ls = []
        for _, r in fls_best.iterrows():
            monthly_ls.append({
                "month": ss(r["month"]),
                "long_short_return": sf(r["long_short_return"]),
                "long_leg_return": sf(r["long_leg_return"]),
                "short_leg_return": sf(r["short_leg_return"]),
                "n_long": int(r["n_long"]) if not pd.isna(r.get("n_long")) else None,
                "n_short": int(r["n_short"]) if not pd.isna(r.get("n_short")) else None,
                "positive_ls": bool(r["positive_ls"]) if not pd.isna(r.get("positive_ls")) else None,
            })

        # Cumulative LS for best horizon
        fcum_best = fcum[fcum["horizon"] == best_hz].sort_values("month") if not fcum.empty else pd.DataFrame()
        cum_curve = []
        for _, r in fcum_best.iterrows():
            cum_curve.append({
                "month": ss(r["month"]),
                "long_short_return": sf(r["long_short_return"]),
                "cum_long_short_return": sf(r["cum_long_short_return"]),
                "drawdown": sf(r["drawdown"]),
            })

        # Card data
        c = card if card is not None else {}
        q = qa_row if qa_row is not None else {}

        factor = {
            "factor_id": fid,
            "family": ss(drow.get("family", "")),
            "lifecycle_status": ss(drow.get("lifecycle_status", "")),
            "expected_direction": ss(drow.get("expected_direction", "")),
            "best_horizon": best_hz,

            # Bilingual card
            "name_en": ss(c.get("name_en", "")),
            "name_zh": ss(c.get("name_zh", "")),
            "family_en": ss(c.get("family_en", "")),
            "family_zh": ss(c.get("family_zh", "")),
            "formula_en": ss(c.get("formula_en", "")),
            "formula_zh": ss(c.get("formula_zh", "")),
            "intuition_en": ss(c.get("intuition_en", "")),
            "intuition_zh": ss(c.get("intuition_zh", "")),
            "expected_direction_explanation_en": ss(c.get("expected_direction_explanation_en", "")),
            "expected_direction_explanation_zh": ss(c.get("expected_direction_explanation_zh", "")),
            "known_limitations_en": ss(c.get("known_limitations_en", "")),
            "known_limitations_zh": ss(c.get("known_limitations_zh", "")),
            "data_source_type": ss(c.get("data_source_type", "")),
            "horizon_notes_en": ss(c.get("horizon_notes_en", "")),
            "horizon_notes_zh": ss(c.get("horizon_notes_zh", "")),
            "status_explanation_en": ss(c.get("status_explanation_en", "")),
            "status_explanation_zh": ss(c.get("status_explanation_zh", "")),
            "review_required_flag": ss(c.get("review_required_flag", "")),
            "metadata_quality": ss(c.get("metadata_quality", drow.get("metadata_quality", ""))),
            "source_fields": ss(c.get("source_fields", "")),
            "required_columns": ss(c.get("required_columns", drow.get("required_columns", ""))),

            # Diagnostics metrics
            "rankic_mean": sf(drow.get("rankic_mean")),
            "rankic_std": sf(drow.get("rankic_std")),
            "rankic_ir": sf(drow.get("rankic_ir")),
            "rankic_t_stat": sf(drow.get("rankic_t_stat")),
            "monthly_ic_positive_rate": sf(drow.get("monthly_ic_positive_rate")),
            "long_short_mean": sf(drow.get("long_short_mean")),
            "long_short_std": sf(drow.get("long_short_std")),
            "long_short_sharpe": sf(drow.get("long_short_sharpe")),
            "long_short_annualized_return": sf(drow.get("long_short_annualized_return")),
            "long_short_annualized_vol": sf(drow.get("long_short_annualized_vol")),
            "long_short_max_drawdown": sf(drow.get("long_short_max_drawdown")),
            "long_short_positive_month_rate": sf(drow.get("long_short_positive_month_rate")),
            "coverage_rate": sf(drow.get("coverage_rate")),
            "redundancy_level": ss(drow.get("redundancy_level", "")),
            "nearest_redundant_factor": ss(drow.get("nearest_redundant_factor", "")),
            "decision_bucket": ss(drow.get("decision_bucket", "")),
            "recommended_action": ss(drow.get("recommended_action", "")),
            "source_warning": ss(drow.get("source_warning", "")),

            # QA
            "qa_notes_zh": ss(q.get("qa_notes_zh", "")),
            "qa_notes_en": ss(q.get("qa_notes_en", "")),
            "needs_human_review": ss(q.get("needs_human_review", "")),
            "qa_reason": ss(q.get("reason", "")),

            # Time series
            "monthly_ic": monthly_ic,
            "monthly_ls": monthly_ls,
            "cum_curve": cum_curve,
        }
        factors.append(factor)

    return {"summary": summary, "factors": factors}


# ── HTML template ───────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor Library — Evaluation 因子评价</title>
<style>
:root{--bg:#0f172a;--panel:#111c31;--panel2:#17243a;--border:#26364f;--text:#e5edf8;--muted:#8ea0b8;--blue:#60a5fa;--green:#34d399;--amber:#fbbf24;--red:#f87171;--purple:#c084fc}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.5;padding:20px}
a{color:var(--blue);text-decoration:none}
h1{font-size:22px;margin:0 0 4px}
h2{font-size:16px;margin:20px 0 8px}
h3{font-size:13px;margin:14px 0 6px;color:#cbd5e1}
.topbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:12px}
.subtitle{color:var(--muted);font-size:12px}
.nav a{margin-right:10px}
.disclaimer{background:#2b1820;border:1px solid #7f1d1d;color:#fecaca;border-radius:8px;padding:10px 12px;margin:10px 0;font-size:12px}
.stats{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.stat{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 10px;min-width:100px}
.stat strong{display:block;font-size:20px}.stat span{color:var(--muted);font-size:10px}
.quality-grid{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.quality-badge{display:inline-block;border-radius:999px;padding:2px 8px;font-size:10px;white-space:nowrap}
.quality-badge.complete{background:#166534;color:#bbf7d0}
.quality-badge.direction_ambiguous{background:#92400e;color:#fef3c7}
.quality-badge.needs_review{background:#7f1d1d;color:#fecaca}
.quality-badge.formula_ambiguous{background:#581c87;color:#e9d5ff}
.layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(340px,.6fr);gap:14px;align-items:start}
@media(max-width:1100px){.layout{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px;margin-bottom:12px}
.detail{position:sticky;top:16px}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
input,select{background:#0b1220;color:var(--text);border:1px solid var(--border);border-radius:7px;padding:6px 8px;font-size:12px}
input[type="text"]{min-width:200px;flex:1}
table{width:100%;border-collapse:collapse;font-size:11px}
th{background:#142035;color:var(--muted);text-align:left;padding:6px 7px;position:sticky;top:0;z-index:1;cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:#e5edf8}
th .sort-arrow{font-size:9px;margin-left:2px}
td{border-bottom:1px solid var(--border);padding:5px 7px;vertical-align:middle}
tr.factor-row{cursor:pointer}tr.factor-row:hover,tr.factor-row.selected{background:#1d2d47}
.num{text-align:right;font-variant-numeric:tabular-nums;font-size:11px}
.strong{color:var(--green);font-weight:700}.watch{color:var(--amber);font-weight:700}.plain{color:var(--text)}.muted-c{color:var(--muted)}
.table-wrap{overflow-x:auto;max-height:70vh;overflow-y:auto}
.factor-link{background:none;border:0;color:var(--blue);font:inherit;font-weight:650;cursor:pointer;padding:0;text-align:left}
.bucket-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;background:#334155;color:#e2e8f0;white-space:nowrap}
.dir-badge{display:inline-block;border-radius:999px;padding:2px 7px;font-size:9px;white-space:nowrap}
.dir-badge.positive{background:#166534;color:#bbf7d0}
.dir-badge.negative{background:#7f1d1d;color:#fecaca}
.dir-badge.conditional{background:#581c87;color:#e9d5ff}
.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
@media(max-width:700px){.metric-grid{grid-template-columns:1fr 1fr}}
.metric{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:7px}
.metric span{display:block;color:var(--muted);font-size:9px;text-transform:uppercase}
.metric strong{font-size:14px}
.chart-container{background:#0b1220;border:1px solid var(--border);border-radius:8px;padding:8px;margin:8px 0;overflow:hidden}
.chart-title{color:var(--muted);font-size:10px;margin-bottom:4px;text-transform:uppercase}
.kv{display:grid;grid-template-columns:120px 1fr;gap:4px;font-size:11px;margin-top:8px}
.kv div:nth-child(odd){color:var(--muted)}
.bilingual{margin:4px 0}.bilingual .zh{font-size:13px}.bilingual .en{font-size:11px;color:var(--muted)}
.formula-block{background:#0b1220;border:1px solid var(--border);border-radius:6px;padding:8px;font-family:'Fira Code',monospace;font-size:12px;margin:4px 0;word-break:break-all}
.section-divider{border-top:1px solid var(--border);margin:12px 0 8px}
.small{font-size:11px;color:var(--muted)}
.footer{margin-top:20px;border-top:1px solid var(--border);padding-top:10px;color:var(--muted);font-size:11px;display:flex;gap:12px;flex-wrap:wrap}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <h1>Factor Library · Evaluation</h1>
    <h1 style="font-size:15px;color:var(--muted)">因子库 · 因子诊断评价</h1>
  </div>
  <div class="subtitle nav">
    <a href="index.html">Home</a> · <a href="actual-script-map.html">Pipeline Map</a> · <a href="signal-evaluation-summary.html">Signal Evaluation</a>
  </div>
</div>

<div class="disclaimer">⚠ 仅作研究诊断 · Diagnostic only — this page evaluates factor behavior for research; it does not promote factors into signals and does not make production or alpha claims.</div>

<div id="statsSection"></div>

<div class="layout">
  <main>
    <div class="card">
      <h2>Factor Scoreboard 因子排行榜</h2>
      <div class="small">Click column headers to sort. 点击列头排序。Best horizon metrics from diagnostics. 最优视野指标来自诊断摘要。</div>
      <div class="controls">
        <input type="text" id="search" placeholder="搜索因子 / Search factor...">
        <select id="familyFilter"><option value="">All families 全部家族</option></select>
        <select id="qualityFilter"><option value="">All quality 全部质量</option></select>
        <select id="horizonFilter"><option value="">All horizons 全部视野</option></select>
      </div>
      <div class="table-wrap">
        <table id="factorTable">
          <thead><tr>
            <th data-col="factor_id">Factor</th>
            <th data-col="name_zh">名称 Name</th>
            <th data-col="family_zh">Family 家族</th>
            <th data-col="metadata_quality">Quality 质量</th>
            <th data-col="best_horizon">Best H 最优视野</th>
            <th data-col="rankic_mean">RankIC</th>
            <th data-col="rankic_ir">ICIR</th>
            <th data-col="monthly_ic_positive_rate">IC Win% IC胜率</th>
            <th data-col="long_short_sharpe">Sharpe</th>
            <th data-col="long_short_annualized_return">Ann Ret 年化收益</th>
            <th data-col="long_short_max_drawdown">Max DD 最大回撤</th>
            <th data-col="long_short_positive_month_rate">LS Win% LS胜率</th>
            <th data-col="coverage_rate">Coverage 覆盖率</th>
            <th data-col="decision_bucket">Decision 决策</th>
          </tr></thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
    </div>
  </main>
  <aside class="detail">
    <div class="card" id="detailCard">
      <h2>Factor Detail 因子详情</h2>
      <div class="small">Select a factor from the table.<br>从表格中选择一个因子查看详情。</div>
    </div>
  </aside>
</div>

<div class="footer">
  <span id="genTime"></span>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/START_HERE.md">Start Here</a>
  <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md">Governance</a>
</div>

<script id="factorPayload" type="application/json">PAYLOAD_PLACEHOLDER</script>
<script>
// ── Data ──
const DATA = JSON.parse(document.getElementById('factorPayload').textContent);
const S = DATA.summary;
const factors = DATA.factors;
const byId = new Map(factors.map(f => [f.factor_id, f]));

// ── Quality label map ──
const QUALITY_LABELS = {
  COMPLETE: {zh:'完整', en:'COMPLETE', cls:'complete'},
  DIRECTION_AMBIGUOUS: {zh:'方向模糊', en:'DIRECTION_AMBIGUOUS', cls:'direction_ambiguous'},
  NEEDS_REVIEW: {zh:'需复核', en:'NEEDS_REVIEW', cls:'needs_review'},
  FORMULA_AMBIGUOUS: {zh:'公式模糊', en:'FORMULA_AMBIGUOUS', cls:'formula_ambiguous'}
};
const DIR_LABELS = {positive:'正向', negative:'负向', conditional:'条件式'};

// ── Helpers ──
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function num(v,d=4,signed=true){if(v===null||v===undefined||Number.isNaN(v))return '—';const s=signed&&v>=0?'+':'';return s+Number(v).toFixed(d)}
function pct(v){if(v===null||v===undefined||Number.isNaN(v))return '—';return(Number(v)*100).toFixed(1)+'%'}
function mcls(v,strong=0.03,watch=0.02){if(v===null||v===undefined||Number.isNaN(v))return 'muted-c';const a=Math.abs(Number(v));return a>=strong?'strong':a>=watch?'watch':'plain'}
function qualBadge(q){
  const l=QUALITY_LABELS[q]||{zh:q,en:q,cls:''};
  return `<span class="quality-badge ${l.cls}">${esc(l.zh)} / ${esc(l.en)}</span>`;
}
function dirBadge(d){
  const lbl=DIR_LABELS[d]||d;
  const cls=d==='positive'?'positive':d==='negative'?'negative':'conditional';
  return `<span class="dir-badge ${cls}">${esc(lbl)} / ${esc(d)}</span>`;
}

// ── Stats section ──
(function(){
  const el=document.getElementById('statsSection');
  const qc=S.quality_counts||{};
  const qcHtml=Object.entries(qc).map(([k,v])=>`<div class="quality-badge ${(QUALITY_LABELS[k]||{cls:''}).cls}" style="font-size:11px;padding:4px 10px"><strong>${v}</strong> ${esc((QUALITY_LABELS[k]||{zh:k,en:k}).zh)} / ${esc((QUALITY_LABELS[k]||{zh:k,en:k}).en)}</div>`).join('');
  el.innerHTML=`
    <div class="stats">
      <div class="stat"><strong>${S.factor_count}</strong><span>Factors 因子数</span></div>
      <div class="stat"><strong>${S.horizons.join(' / ')}</strong><span>Horizons 视野</span></div>
      <div class="stat"><strong>${S.month_count}</strong><span>Months covered 月份数</span></div>
    </div>
    <div class="quality-grid">${qcHtml}</div>
  `;
})();

// ── Populate filters ──
const families=[...new Set(factors.map(f=>f.family_zh||f.family))].sort();
const qualities=[...new Set(factors.map(f=>f.metadata_quality))].sort();
const familyFilter=document.getElementById('familyFilter');
const qualityFilter=document.getElementById('qualityFilter');
const horizonFilter=document.getElementById('horizonFilter');
families.forEach(f=>{const o=document.createElement('option');o.value=f;o.textContent=f;familyFilter.appendChild(o)});
qualities.forEach(q=>{const o=document.createElement('option');o.value=q;o.textContent=(QUALITY_LABELS[q]||{zh:q}).zh+' / '+q;qualityFilter.appendChild(o)});
S.horizons.forEach(h=>{const o=document.createElement('option');o.value=h;o.textContent=h;horizonFilter.appendChild(o)});

// ── Sort state ──
let sortCol='long_short_sharpe';
let sortDir=-1; // -1=desc

// ── Render table ──
function renderTable(){
  const q=document.getElementById('search').value.toLowerCase();
  const fam=familyFilter.value;
  const qual=qualityFilter.value;
  const hz=horizonFilter.value;

  let filtered=factors.filter(f=>{
    const text=[f.factor_id,f.name_zh,f.name_en,f.family_zh,f.family,f.decision_bucket].join(' ').toLowerCase();
    if(q&&!text.includes(q))return false;
    if(fam&&(f.family_zh!==fam&&f.family!==fam))return false;
    if(qual&&f.metadata_quality!==qual)return false;
    if(hz&&f.best_horizon!==hz)return false;
    return true;
  });

  filtered.sort((a,b)=>{
    let va=a[sortCol],vb=b[sortCol];
    if(typeof va==='string')return sortDir*va.localeCompare(vb);
    va=va??-Infinity;vb=vb??-Infinity;
    return sortDir*(va-vb);
  });

  const tbody=document.getElementById('tableBody');
  tbody.innerHTML=filtered.map(f=>{
    const fid=esc(f.factor_id);
    return `<tr data-factor="${fid}" class="factor-row">
      <td><button class="factor-link" type="button">${fid}</button></td>
      <td><span class="zh">${esc(f.name_zh)}</span><br><span class="en small">${esc(f.name_en)}</span></td>
      <td>${esc(f.family_zh||f.family)}</td>
      <td>${qualBadge(f.metadata_quality)}</td>
      <td>${esc(f.best_horizon)}</td>
      <td class="num ${mcls(f.rankic_mean)}">${num(f.rankic_mean)}</td>
      <td class="num">${num(f.rankic_ir,3)}</td>
      <td class="num">${pct(f.monthly_ic_positive_rate)}</td>
      <td class="num ${mcls(f.long_short_sharpe,1.5,0.8)}">${num(f.long_short_sharpe,2)}</td>
      <td class="num">${pct(f.long_short_annualized_return)}</td>
      <td class="num">${pct(f.long_short_max_drawdown)}</td>
      <td class="num">${pct(f.long_short_positive_month_rate)}</td>
      <td class="num">${pct(f.coverage_rate)}</td>
      <td><span class="bucket-badge">${esc(f.decision_bucket)}</span></td>
    </tr>`;
  }).join('');

  // Update sort arrows
  document.querySelectorAll('#factorTable th').forEach(th=>{
    const col=th.dataset.col;
    const arrow=col===sortCol?(sortDir>0?'▲':'▼'):'';
    const base=th.textContent.replace(/[▲▼]/g,'').trim();
    // We rebuild text from data attribute
  });

  // Re-attach row click
  tbody.querySelectorAll('tr').forEach(tr=>tr.addEventListener('click',()=>{
    tbody.querySelectorAll('tr.selected').forEach(r=>r.classList.remove('selected'));
    tr.classList.add('selected');
    renderDetail(tr.dataset.factor);
  }));
}

// ── Sort click ──
document.querySelectorAll('#factorTable th[data-col]').forEach(th=>{
  th.addEventListener('click',()=>{
    const col=th.dataset.col;
    if(sortCol===col){sortDir*=-1}else{sortCol=col;sortDir=-1}
    // Update visual
    document.querySelectorAll('#factorTable th').forEach(h=>{
      h.innerHTML=h.textContent.replace(/ [▲▼]/g,'');
    });
    th.innerHTML=th.textContent.replace(/ [▲▼]/g,'')+(sortDir>0?' ▲':' ▼');
    renderTable();
  });
});

// ── SVG chart helpers ──
function svgLineChart(data, yKey, w, h, opts={}){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const vals=data.map(d=>Number(d[yKey])||0);
  const ymin=Math.min(0,...vals),ymax=Math.max(0,...vals);
  const yrange=ymax-ymin||1;
  function xPos(i){return padL+(i/(data.length-1||1))*cw}
  function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  // Zero line
  const zy=yPos(0);
  svg+=`<line x1="${padL}" y1="${zy}" x2="${w-padR}" y2="${zy}" stroke="#334155" stroke-dasharray="3"/>`;
  // Line
  const points=data.map((d,i)=>`${xPos(i)},${yPos(Number(d[yKey])||0)}`).join(' ');
  svg+=`<polyline points="${points}" fill="none" stroke="${opts.color||'#60a5fa'}" stroke-width="1.5"/>`;
  // Dots
  data.forEach((d,i)=>{
    const v=Number(d[yKey])||0;
    const c=v>=0?'#34d399':'#f87171';
    svg+=`<circle cx="${xPos(i)}" cy="${yPos(v)}" r="2" fill="${c}"/>`;
  });
  // X labels (sparse)
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      svg+=`<text x="${xPos(i)}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  // Y axis label
  svg+=`<text x="4" y="${zy}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+=`<text x="4" y="${padT}" fill="#8ea0b8" font-size="8">${num(ymax,3)}</text>`;
  svg+=`<text x="4" y="${h-padB}" fill="#8ea0b8" font-size="8">${num(ymin,3)}</text>`;
  svg+='</svg>';
  return svg;
}

function svgBarChart(data, yKey, w, h){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const vals=data.map(d=>Number(d[yKey])||0);
  const maxAbs=Math.max(0.000001,...vals.map(v=>Math.abs(v)));
  const bw=Math.max(1,Math.min(8,cw/data.length-1));
  function yPos(v){return padT+ch/2-(v/maxAbs)*(ch/2)}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  const mid=padT+ch/2;
  svg+=`<line x1="${padL}" y1="${mid}" x2="${w-padR}" y2="${mid}" stroke="#334155" stroke-dasharray="3"/>`;
  data.forEach((d,i)=>{
    const v=Number(d[yKey])||0;
    const x=padL+(i/data.length)*cw;
    const barH=Math.abs(v/maxAbs)*(ch/2);
    const y=v>=0?mid-barH:mid;
    const c=v>=0?'#34d399':'#f87171';
    svg+=`<rect x="${x}" y="${y}" width="${bw}" height="${barH}" fill="${c}" rx="1"/>`;
  });
  // X labels
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      const x=padL+(i/data.length)*cw+bw/2;
      svg+=`<text x="${x}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  svg+=`<text x="4" y="${mid}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+='</svg>';
  return svg;
}

function svgCumCurve(data, w, h){
  if(!data||data.length===0)return '<div class="small">No data</div>';
  const padL=50,padR=10,padT=10,padB=20;
  const cw=w-padL-padR,ch=h-padT-padB;
  const cumVals=data.map(d=>Number(d.cum_long_short_return)||0);
  const ddVals=data.map(d=>Number(d.drawdown)||0);
  const ymin=Math.min(0,...cumVals,...ddVals);
  const ymax=Math.max(0,...cumVals);
  const yrange=ymax-ymin||1;
  function xPos(i){return padL+(i/(data.length-1||1))*cw}
  function yPos(v){return padT+ch-((v-ymin)/yrange)*ch}

  let svg=`<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" style="width:100%;height:auto">`;
  const zy=yPos(0);
  svg+=`<line x1="${padL}" y1="${zy}" x2="${w-padR}" y2="${zy}" stroke="#334155" stroke-dasharray="3"/>`;

  // Drawdown shading
  if(data.length>1){
    let ddPath=`M${xPos(0)},${yPos(0)}`;
    data.forEach((d,i)=>{ddPath+=` L${xPos(i)},${yPos(Math.min(0,Number(d.cum_long_short_return)||0))}`});
    ddPath+=` L${xPos(data.length-1)},${yPos(0)} Z`;
    svg+=`<path d="${ddPath}" fill="#f8717133" stroke="none"/>`;
  }

  // Cumulative line
  const points=data.map((d,i)=>`${xPos(i)},${yPos(Number(d.cum_long_short_return)||0)}`).join(' ');
  svg+=`<polyline points="${points}" fill="none" stroke="#60a5fa" stroke-width="1.5"/>`;

  // Drawdown line
  const ddPoints=data.map((d,i)=>`${xPos(i)},${yPos(Number(d.drawdown)||0)}`).join(' ');
  svg+=`<polyline points="${ddPoints}" fill="none" stroke="#f87171" stroke-width="1" stroke-dasharray="3"/>`;

  // X labels
  const step=Math.max(1,Math.floor(data.length/6));
  data.forEach((d,i)=>{
    if(i%step===0||i===data.length-1){
      svg+=`<text x="${xPos(i)}" y="${h-2}" text-anchor="middle" fill="#8ea0b8" font-size="8">${esc(d.month)}</text>`;
    }
  });
  svg+=`<text x="4" y="${zy}" fill="#8ea0b8" font-size="8" dominant-baseline="middle">0</text>`;
  svg+=`<text x="4" y="${padT}" fill="#8ea0b8" font-size="8">${num(ymax,4)}</text>`;
  svg+=`<text x="4" y="${h-padB}" fill="#8ea0b8" font-size="8">${num(ymin,4)}</text>`;
  svg+='</svg>';
  return svg;
}

// ── Render detail ──
function renderDetail(fid){
  const f=byId.get(fid);if(!f)return;
  const card=document.getElementById('detailCard');

  const metricRow=(label,val,cls='')=>`<div class="metric"><span>${label}</span><strong class="${cls}">${val}</strong></div>`;

  card.innerHTML=`
    <h2>${esc(f.factor_id)}</h2>
    <div class="bilingual">
      <div class="zh" style="font-size:15px;font-weight:600">${esc(f.name_zh)}</div>
      <div class="en">${esc(f.name_en)}</div>
    </div>
    <div class="small">${esc(f.family_zh||f.family)} · ${esc(f.family_en||'')} · ${dirBadge(f.expected_direction)} · best=${esc(f.best_horizon)}</div>

    <div class="section-divider"></div>
    <h3>Formula 公式</h3>
    <div class="formula-block">
      <div><strong>ZH:</strong> ${esc(f.formula_zh)}</div>
      <div style="color:var(--muted)"><strong>EN:</strong> ${esc(f.formula_en)}</div>
    </div>

    <h3>Intuition 直觉解释</h3>
    <div class="bilingual"><div class="zh">${esc(f.intuition_zh)}</div><div class="en">${esc(f.intuition_en)}</div></div>

    <h3>Expected Direction 预期方向</h3>
    <div class="bilingual"><div class="zh">${esc(f.expected_direction_explanation_zh)}</div><div class="en">${esc(f.expected_direction_explanation_en)}</div></div>

    <h3>Known Limitations 已知局限</h3>
    <div class="bilingual"><div class="zh">${esc(f.known_limitations_zh)}</div><div class="en">${esc(f.known_limitations_en)}</div></div>

    <div class="kv">
      <div>Data Source 数据源</div><div>${esc(f.data_source_type)}</div>
      <div>Required Columns 必要列</div><div>${esc(f.required_columns)}</div>
      <div>Horizon Notes 视野说明</div><div>${esc(f.horizon_notes_zh)}<br><span class="small">${esc(f.horizon_notes_en)}</span></div>
      <div>Status Explanation 状态说明</div><div>${esc(f.status_explanation_zh)}<br><span class="small">${esc(f.status_explanation_en)}</span></div>
    </div>

    <div class="section-divider"></div>
    <h3>Metadata Quality 元数据质量</h3>
    <div>${qualBadge(f.metadata_quality)}</div>
    ${f.needs_human_review==='yes'?'<div style="color:var(--amber);font-size:11px;margin:4px 0">⚠ Needs human review 需人工复核</div>':''}
    ${f.qa_notes_zh?`<div class="bilingual"><div class="zh" style="font-size:11px">${esc(f.qa_notes_zh)}</div><div class="en" style="font-size:10px">${esc(f.qa_notes_en)}</div></div>`:''}
    ${f.qa_reason?`<div class="small">Reason: ${esc(f.qa_reason)}</div>`:''}

    <div class="section-divider"></div>
    <h3>Best Horizon Metrics 最优视野指标 (${esc(f.best_horizon)})</h3>
    <div class="metric-grid">
      ${metricRow('RankIC Mean',num(f.rankic_mean),mcls(f.rankic_mean))}
      ${metricRow('RankIC Std',num(f.rankic_std,4,false))}
      ${metricRow('ICIR',num(f.rankic_ir,3))}
      ${metricRow('IC t-stat',num(f.rankic_t_stat,2,false))}
      ${metricRow('IC Win Rate IC胜率',pct(f.monthly_ic_positive_rate))}
      ${metricRow('LS Mean LS均值',num(f.long_short_mean,6))}
      ${metricRow('LS Std LS标准差',num(f.long_short_std,6))}
      ${metricRow('Sharpe',num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
      ${metricRow('Ann Return 年化收益',pct(f.long_short_annualized_return))}
      ${metricRow('Ann Vol 年化波动',pct(f.long_short_annualized_vol))}
      ${metricRow('Max Drawdown 最大回撤',pct(f.long_short_max_drawdown))}
      ${metricRow('LS Win Rate LS月胜率',pct(f.long_short_positive_month_rate))}
      ${metricRow('Coverage 覆盖率',pct(f.coverage_rate))}
    </div>

    <div class="kv" style="margin-top:8px">
      <div>Redundancy 冗余度</div><div>${esc(f.redundancy_level)}</div>
      <div>Nearest Factor 最近因子</div><div>${esc(f.nearest_redundant_factor||'—')}</div>
      <div>Decision Bucket 决策桶</div><div><span class="bucket-badge">${esc(f.decision_bucket)}</span></div>
      <div>Recommended Action 建议操作</div><div>${esc(f.recommended_action||'—')}</div>
      <div>Source Warning 源警告</div><div>${esc(f.source_warning||'—')}</div>
    </div>

    <div class="section-divider"></div>
    <h3>Monthly RankIC 月度RankIC (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Monthly RankIC (adj) · 月度调整RankIC</div>
      ${svgLineChart(f.monthly_ic,'rank_ic_adj',600,140)}
    </div>

    <h3>Monthly Long-Short Return 月度多空收益 (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Monthly LS Return · 月度多空收益</div>
      ${svgBarChart(f.monthly_ls,'long_short_return',600,120)}
    </div>

    <h3>Cumulative Long-Short Curve 累计多空曲线 (${esc(f.best_horizon)})</h3>
    <div class="chart-container">
      <div class="chart-title">Cumulative LS (blue) with drawdown (red) · 累计多空(蓝)及回撤(红)</div>
      ${svgCumCurve(f.cum_curve,600,160)}
    </div>

    <h3>Drawdown Summary 回撤概要</h3>
    <div class="metric-grid">
      ${metricRow('Max DD 最大回撤',pct(f.long_short_max_drawdown))}
      ${metricRow('LS Month Win% 月胜率',pct(f.long_short_positive_month_rate))}
      ${metricRow('LS Sharpe',num(f.long_short_sharpe,2),mcls(f.long_short_sharpe,1.5,0.8))}
    </div>
  `;
}

// ── Init ──
const searchEl=document.getElementById('search');
[searchEl,familyFilter,qualityFilter,horizonFilter].forEach(el=>el.addEventListener('input',renderTable));
[familyFilter,qualityFilter,horizonFilter].forEach(el=>el.addEventListener('change',renderTable));

// Set initial sort arrow
document.querySelector(`th[data-col="${sortCol}"]`).innerHTML+=' ▼';

renderTable();
if(factors.length)renderDetail(factors[0].factor_id);

document.getElementById('genTime').textContent='Generated: '+new Date().toISOString().slice(0,16);
</script>
</body>
</html>"""


# ── Main ────────────────────────────────────────────────────────────────────
def render() -> str:
    payload = build_payload()
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # Escape for embedding in <script> tag
    payload_json = payload_json.replace("<", "\\u003c").replace("</", "<\\/")
    return HTML_TEMPLATE.replace("PAYLOAD_PLACEHOLDER", payload_json)


if __name__ == "__main__":
    html_out = render()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html_out):,} bytes)")
