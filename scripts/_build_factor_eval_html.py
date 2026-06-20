#!/usr/bin/env python3
"""Rebuild factor-evaluation.html — Phase 13A-P1 upgraded version.

Reads:
  - factor_level_metric_panel.csv (new in P1)
  - factor_level_rankic_summary.csv (canonical)
  - factor_level_coverage_summary.csv
  - factor_level_long_short_summary.csv
  - factor_level_period_ic_summary.csv
  - factor_level_evaluation_manifest.json

Writes:
  reports/site/factor-library/factor-evaluation.html
"""
import json
import pandas as pd
from pathlib import Path

EVAL_DIR = Path("research/factor_runs/crypto_top50_factor_library/factor_level_evaluation")
OUT = Path("reports/site/factor-library/factor-evaluation.html")

# Load data
manifest = json.load(open(EVAL_DIR / "factor_level_evaluation_manifest.json"))

# Try metric panel first (P1), fall back to rankic summary
mp_path = EVAL_DIR / "factor_level_metric_panel.csv"
if mp_path.exists():
    mp = pd.read_csv(mp_path)
    USE_METRIC_PANEL = True
else:
    mp = pd.read_csv(EVAL_DIR / "factor_level_rankic_summary.csv")
    USE_METRIC_PANEL = False

cov = pd.read_csv(EVAL_DIR / "factor_level_coverage_summary.csv")

ls_path = EVAL_DIR / "factor_level_long_short_summary.csv"
ls_df = pd.read_csv(ls_path) if ls_path.exists() else pd.DataFrame()

period_path = EVAL_DIR / "factor_level_period_ic_summary.csv"
period_df = pd.read_csv(period_path) if period_path.exists() else pd.DataFrame()

horizons = ["1h", "4h", "24h", "72h"]

# Missing factors (from manifest)
missing_fids = manifest.get("missing_factor_ids", [
    "taker_buy_ratio_20h", "taker_buy_zscore_20h", "taker_buy_delta_5h",
    "funding_rate_level_20h", "funding_rate_zscore_80h", "funding_rate_change_24h",
])

# Build rows from metric panel
rows = []
for fid in mp["factor_name"].unique():
    fdf = mp[mp["factor_name"] == fid]
    spec = fdf.iloc[0]
    cat = spec.get("category", "unknown")
    direction = spec.get("expected_direction", "conditional")
    in_sig = spec.get("used_in_current_signal", False)
    status = spec.get("status", "UNKNOWN")
    missing_rate = spec.get("missing_rate", None)
    coverage = spec.get("coverage", None)

    row = {
        "factor": fid, "category": cat, "direction": direction,
        "in_signal": bool(in_sig), "status": str(status),
        "missing_rate": missing_rate, "coverage": coverage,
    }

    for hz in horizons:
        hz_row = fdf[fdf["horizon"] == hz]
        if len(hz_row) == 0:
            for k in ["ic", "icir", "t", "n", "win_adj", "ls_mean", "ls_t", "ls_win"]:
                row[f"{k}_{hz}"] = "—"
            continue
        r = hz_row.iloc[0]

        def _fmt(val, fmt="+.4f", none_val="—"):
            if pd.isna(val):
                return none_val
            return f"{val:{fmt}}"

        row[f"ic_{hz}"] = _fmt(r.get("direction_adjusted_mean_rank_ic"))
        row[f"icir_{hz}"] = _fmt(r.get("icir"), ".3f") if pd.notna(r.get("icir")) else "—"
        row[f"t_{hz}"] = _fmt(r.get("t_stat"), ".1f")
        row[f"n_{hz}"] = str(int(r["n_periods"])) if pd.notna(r.get("n_periods")) else "—"
        row[f"win_adj_{hz}"] = _fmt(r.get("ic_win_rate_adjusted"), ".1%", none_val="—")
        row[f"ls_mean_{hz}"] = _fmt(r.get("long_short_spread_mean"), "+.6f")
        row[f"ls_t_{hz}"] = _fmt(r.get("long_short_spread_t_stat"), ".2f")
        row[f"ls_win_{hz}"] = _fmt(r.get("long_short_win_rate"), ".1%", none_val="—")

    rows.append(row)

# Sort: active-in-signal first, then by abs IC 1h
def sort_key(r):
    ic_val = r.get("ic_1h", "—")
    try:
        abs_ic = abs(float(ic_val.replace("+", "")))
    except (ValueError, AttributeError):
        abs_ic = 0
    return (not r["in_signal"], -abs_ic)

rows.sort(key=sort_key)

# Build top diagnostic sections
top_ic_rows = [r for r in rows if r.get("ic_1h", "—") not in ("—", "NOT_COMPUTED")]
top_ic_rows.sort(key=lambda r: -abs(float(r["ic_1h"].replace("+", ""))))
top_10_ic = top_ic_rows[:10]

top_icir_rows = [r for r in rows if r.get("icir_1h", "—") not in ("—",)]
top_icir_rows.sort(key=lambda r: -abs(float(r["icir_1h"].replace("+", "").replace("—", "0"))))
top_10_icir = top_icir_rows[:10]

# Active-in-signal summary
active_rows = [r for r in rows if r["in_signal"]]

# CSS
status_colors = {
    "COMPUTED": ("#22c55e", "#052e16"),
    "ACTIVE_IN_SIGNAL_COMPUTED": ("#3b82f6", "#1e1b4b"),
    "DIRECTION_UNKNOWN": ("#f59e0b", "#451a03"),
    "MISSING_FACTOR_VALUES": ("#ef4444", "#450a0a"),
    "NO_VALID_PERIODS": ("#6b7280", "#1f2937"),
}

def status_badge(s):
    s = str(s)
    bg, fg = status_colors.get(s, ("#6b7280", "#1f2937"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:4px;font-size:11px">{s}</span>'

def sig_mark(in_sig):
    return "★" if in_sig else ""

def ic_color(val_str):
    try:
        v = abs(float(val_str.replace("+", "")))
    except (ValueError, AttributeError):
        return "#e2e8f0"
    if v >= 0.03:
        return "#22c55e"
    elif v >= 0.02:
        return "#f59e0b"
    return "#e2e8f0"


# ── Build HTML ──────────────────────────────────────────────────

# Stats
n_total = manifest.get("total_registered_factors", len(rows))
n_computed = manifest.get("computed_factors", 0)
n_missing = manifest.get("missing_factor_values", len(missing_fids))
n_signal = manifest.get("active_in_signal", len(active_rows))

# Period stability summary (top/best monthly IC per factor)
period_stability_rows = []
if not period_df.empty:
    for fid in period_df["factor_name"].unique():
        pdf = period_df[period_df["factor_name"] == fid]
        for hz in horizons:
            hz_pdf = pdf[pdf["horizon"] == hz]
            if hz_pdf.empty:
                continue
            adj_col = "direction_adjusted_mean_rank_ic"
            if adj_col in hz_pdf.columns:
                best_month = hz_pdf.loc[hz_pdf[adj_col].idxmax()]
                worst_month = hz_pdf.loc[hz_pdf[adj_col].idxmin()]
                period_stability_rows.append({
                    "factor": fid, "horizon": hz,
                    "best_period": best_month.get("period", ""),
                    "best_adj_ic": best_month.get(adj_col, 0),
                    "worst_period": worst_month.get("period", ""),
                    "worst_adj_ic": worst_month.get(adj_col, 0),
                    "n_months": len(hz_pdf),
                })

# Main table rows
table_rows = ""
for r in rows:
    ic_cells = ""
    for hz in horizons:
        val = r[f"ic_{hz}"]
        icir = r[f"icir_{hz}"]
        win = r[f"win_adj_{hz}"]
        ls_mean = r[f"ls_mean_{hz}"]

        if val in ("—", "NOT_COMPUTED"):
            ic_cells += f'<td style="text-align:center;color:#94a3b8" colspan="4">{val}</td>'
        else:
            color = ic_color(val)
            ic_cells += f'<td style="text-align:center;color:{color};font-weight:600">{val}</td>'
            icir_color = "#94a3b8" if icir == "—" else "#e2e8f0"
            ic_cells += f'<td style="text-align:center;color:{icir_color};font-size:11px">{icir}</td>'
            ic_cells += f'<td style="text-align:center;color:#94a3b8;font-size:11px">{win}</td>'
            ls_color = ic_color(ls_mean) if ls_mean != "—" else "#94a3b8"
            ic_cells += f'<td style="text-align:center;color:{ls_color};font-size:11px">{ls_mean}</td>'

    mr_str = f"{r['missing_rate']:.1%}" if pd.notna(r.get("missing_rate")) else "—"

    table_rows += f'''<tr>
  <td>{sig_mark(r["in_signal"])} {r["factor"]}</td>
  <td>{r["category"]}</td>
  <td>{r["direction"]}</td>
  <td>{status_badge(r["status"])}</td>
  <td style="text-align:center">{mr_str}</td>
  {ic_cells}
</tr>
'''

# Top diagnostic section
top_diag_html = ""
for label, data, metric_key, metric_label in [
    ("Top 10 by Adjusted IC (1h)", top_10_ic, "ic_1h", "Adj IC"),
    ("Top 10 by ICIR (1h)", top_10_icir, "icir_1h", "ICIR"),
]:
    top_diag_html += f'<h3>{label}</h3>\n<table><thead><tr><th>Factor</th><th>Category</th><th>{metric_label}</th><th>Status</th></tr></thead><tbody>\n'
    for r in data[:10]:
        val = r.get(metric_key, "—")
        top_diag_html += f'<tr><td>{sig_mark(r["in_signal"])} {r["factor"]}</td><td>{r["category"]}</td><td style="text-align:center">{val}</td><td>{status_badge(r["status"])}</td></tr>\n'
    top_diag_html += '</tbody></table>\n'

# Active-in-signal summary
active_html = '<table><thead><tr><th>Factor</th><th>Category</th><th>Direction</th>'
for hz in horizons:
    active_html += f'<th style="text-align:center">IC {hz}</th><th style="text-align:center">ICIR {hz}</th>'
active_html += '</tr></thead><tbody>\n'
for r in active_rows:
    active_html += f'<tr><td>★ {r["factor"]}</td><td>{r["category"]}</td><td>{r["direction"]}</td>'
    for hz in horizons:
        val = r.get(f"ic_{hz}", "—")
        icir = r.get(f"icir_{hz}", "—")
        color = ic_color(val) if val != "—" else "#94a3b8"
        active_html += f'<td style="text-align:center;color:{color};font-weight:600">{val}</td>'
        active_html += f'<td style="text-align:center;color:#94a3b8;font-size:11px">{icir}</td>'
    active_html += '</tr>\n'
active_html += '</tbody></table>\n'

# Missing factors section
missing_html = '<table><thead><tr><th>Factor</th><th>Category</th><th>Direction</th><th>Reason</th></tr></thead><tbody>\n'
missing_reason = "Current raw bars (bars_1h.parquet) do not contain taker_buy_quote_volume or funding_rate columns."
for fid in missing_fids:
    fdf = mp[mp["factor_name"] == fid] if fid in mp["factor_name"].values else pd.DataFrame()
    cat = fdf.iloc[0]["category"] if len(fdf) > 0 else "unknown"
    d = fdf.iloc[0]["expected_direction"] if len(fdf) > 0 else "unknown"
    missing_html += f'<tr><td>{fid}</td><td>{cat}</td><td>{d}</td><td>{missing_reason}</td></tr>\n'
missing_html += '</tbody></table>\n'

# Period stability section
period_html = ""
if period_stability_rows:
    period_html = '<table><thead><tr><th>Factor</th><th>Horizon</th><th>Best Month</th><th>Best Adj IC</th><th>Worst Month</th><th>Worst Adj IC</th><th>Months</th></tr></thead><tbody>\n'
    # Sort by abs(best_adj_ic) descending
    period_stability_rows.sort(key=lambda r: -abs(float(r.get("best_adj_ic", 0) or 0)))
    for r in period_stability_rows[:20]:  # Top 20
        period_html += f'<tr><td>{r["factor"]}</td><td>{r["horizon"]}</td>'
        period_html += f'<td>{r["best_period"]}</td><td>{r["best_adj_ic"]:+.4f}</td>'
        period_html += f'<td>{r["worst_period"]}</td><td>{r["worst_adj_ic"]:+.4f}</td>'
        period_html += f'<td>{r["n_months"]}</td></tr>\n'
    period_html += '</tbody></table>\n'
else:
    period_html = '<p style="color:#94a3b8">Period IC summary not available.</p>'

# ── Assemble HTML ───────────────────────────────────────────────

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor-Level IC Evaluation</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }}
h1 {{ color: #f1f5f9; font-size: 22px; margin-bottom: 8px; }}
h2 {{ color: #cbd5e1; font-size: 16px; margin: 24px 0 12px; }}
h3 {{ color: #94a3b8; font-size: 14px; margin: 16px 0 8px; }}
.subtitle {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
.stats {{ display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
.stat {{ background: #1e293b; border-radius: 8px; padding: 12px 18px; min-width: 120px; }}
.stat-val {{ font-size: 24px; font-weight: 700; color: #f1f5f9; }}
.stat-label {{ font-size: 11px; color: #94a3b8; margin-top: 4px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; margin: 8px 0; }}
th {{ background: #1e293b; color: #94a3b8; padding: 8px 10px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; position: sticky; top: 0; }}
td {{ padding: 6px 10px; border-bottom: 1px solid #1e293b; }}
tr:hover {{ background: #1e293b40; }}
.hz-header {{ text-align: center; color: #3b82f6; }}
.method-box {{ background: #1e293b; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 13px; line-height: 1.6; color: #94a3b8; }}
.method-box strong {{ color: #e2e8f0; }}
.method-box ul {{ margin: 4px 0 0 16px; }}
.parity-box {{ background: #064e3b; border: 1px solid #22c55e; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 13px; line-height: 1.6; color: #a7f3d0; }}
.parity-box strong {{ color: #6ee7b7; }}
.alert-box {{ background: #450a0a; border: 1px solid #ef4444; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 13px; line-height: 1.6; color: #fca5a5; }}
.alert-box strong {{ color: #f87171; }}
.diagnostic-box {{ background: #1e293b; border: 1px solid #3b82f6; border-radius: 8px; padding: 16px; margin: 16px 0; }}
.diagnostic-box h3 {{ color: #60a5fa; margin-top: 0; }}
footer {{ margin-top: 24px; padding-top: 12px; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; display: flex; gap: 16px; }}
footer a {{ color: #60a5fa; text-decoration: none; }}
footer a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>

<h1>Factor-Level IC Evaluation</h1>
<p class="subtitle">Direction-adjusted RankIC (Spearman) · {n_total} registered factors · {n_computed} computed · {n_missing} missing FV · {n_signal} in signal · Phase 13A-P1</p>

<div class="stats">
 <div class="stat"><div class="stat-val">{n_total}</div><div class="stat-label">Registered</div></div>
 <div class="stat"><div class="stat-val">{n_computed}</div><div class="stat-label">Computed</div></div>
 <div class="stat"><div class="stat-val">{n_missing}</div><div class="stat-label">Missing FV</div></div>
 <div class="stat"><div class="stat-val">{n_signal}</div><div class="stat-label">In Signal</div></div>
 <div class="stat"><div class="stat-val">4</div><div class="stat-label">Horizons</div></div>
</div>

<div class="alert-box">
<strong>⚠️ 声明 / Disclaimer:</strong> Phase 13A research governance/evaluation work has started. Production/live-trading Phase 13 has NOT started.<br>
本页是因子层诊断（factor-level diagnostics），不是可交易 alpha。Not tradeable alpha. Not production. Not live trading.
</div>

<div class="method-box">
<strong>方法说明 / Methodology</strong>
<ul>
<li><strong>Factor-level RankIC:</strong> 每个 timestamp 内 rank(factor_value) 与 rank(forward_return) 的 Pearson 相关系数（等价于 Spearman）。不同于 signal-level RankIC（组合信号 vs forward return）。</li>
<li><strong>Raw vs Direction-Adjusted IC:</strong> raw IC 是未经方向调整的相关系数。Direction-adjusted: positive→raw, negative→-raw, conditional→raw (标记 DIRECTION_UNKNOWN)。</li>
<li><strong>ICIR:</strong> mean(raw RankIC) / std(raw RankIC)。衡量 IC 的稳定性。ICIR 越高，因子在时间维度上越稳定。</li>
<li><strong>IC Win Rate:</strong> per-timestamp IC > 0 的比例。raw = 未经方向调整; adjusted = 方向调整后。</li>
<li><strong>Quantile Bucket Returns:</strong> 按因子值排序分为 5 个 bucket，计算各 bucket 的平均 forward return。</li>
<li><strong>Long-Short Spread:</strong> direction-adjusted 排序后 top bucket - bottom bucket 的 mean return 差异。仅用于诊断，不等于可交易 PnL。</li>
<li><strong>Coverage / Missing Rate:</strong> 因子值覆盖率和缺失率。</li>
<li><strong>Period IC:</strong> 按月聚合的 IC 统计，用于评估因子在不同市场状态下的稳定性。</li>
<li><strong>formula_proxy:</strong> 当前使用 FactorSpec.notes 作为公式代理，不是 canonical DSL。</li>
</ul>
</div>

<div class="parity-box">
<strong>H8-R Parity Check (2026-06-19)</strong><br>
evaluate_factors.py 与 momentum.signal_evaluation.compute_rank_ic 公共 API 做了抽样 parity 验证。<br>
测试因子：vol_5h, vol_40h, rsi_7h, range_1h, price_pos_24h × horizons 1h, 24h。<br>
结果：<strong>10/10 PASS，max mean RankIC diff = 0.00e+00（exact match）</strong>。
</div>

<h2>Active Signal Factors ({n_signal})</h2>
{active_html}

<h2>Diagnostic Factors — Top Rankings</h2>
<div class="diagnostic-box">
{top_diag_html}
</div>

<h2>Missing Taker/Funding Factors ({n_missing})</h2>
<div class="alert-box">
<strong>Missing Factor Values:</strong> 以下 {n_missing} 个因子的 factor_values 尚未计算，因为当前 raw bars (bars_1h.parquet) 不包含 taker_buy_quote_volume 和 funding_rate 字段。<br>
需要扩展数据下载脚本以包含这些字段后才能计算。
</div>
{missing_html}

<h2>Period Stability (Monthly IC)</h2>
<p style="color:#94a3b8;font-size:13px">按月聚合的 direction-adjusted IC。Top 20 by best monthly IC.</p>
{period_html}

<h2>Full Factor Table</h2>
<p style="color:#94a3b8;font-size:13px">IC = direction-adjusted RankIC · ICIR = mean/std · Win = adjusted win rate · LS = long-short spread mean</p>

<table>
<thead>
<tr>
 <th>Factor</th><th>Category</th><th>Direction</th><th>Status</th><th>Missing%</th>
 <th colspan="4" class="hz-header">1h IC / ICIR / Win / LS</th>
 <th colspan="4" class="hz-header">4h IC / ICIR / Win / LS</th>
 <th colspan="4" class="hz-header">24h IC / ICIR / Win / LS</th>
 <th colspan="4" class="hz-header">72h IC / ICIR / Win / LS</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>

<footer>
 <a href="index.html">← 首页</a>
 <a href="actual-script-map.html">代码结构</a>
 <a href="signal-evaluation-summary.html">信号评价</a>
 <a href="https://github.com/jerry0012009/momentum/tree/main/docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md">治理中心</a>
</footer>

</body>
</html>'''

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT} ({len(html)} bytes)")
