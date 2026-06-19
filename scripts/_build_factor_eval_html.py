#!/usr/bin/env python3
"""Rebuild factor-evaluation.html with H8-R parity note."""
import json, pandas as pd
from pathlib import Path

OUT = Path("reports/site/factor-library/factor-evaluation.html")
manifest = json.load(open("research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_evaluation_manifest.json"))
df = pd.read_csv("research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.csv")
cov = pd.read_csv("research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_coverage_summary.csv")

horizons = ["1h", "4h", "24h", "72h"]

# Build rows
rows = []
for fid in df["factor_name"].unique():
    fdf = df[df["factor_name"] == fid]
    spec = fdf.iloc[0]
    cat = spec["category"]
    direction = spec["expected_direction"]
    in_sig = spec.get("used_in_current_signal", False)
    status = spec["status"]

    row = {"factor": fid, "category": cat, "direction": direction,
           "in_signal": in_sig, "status": status}
    for hz in horizons:
        hz_row = fdf[fdf["horizon"] == hz]
        if len(hz_row) == 0:
            row[f"ic_{hz}"] = "—"
            row[f"t_{hz}"] = "—"
            row[f"n_{hz}"] = "—"
            continue
        r = hz_row.iloc[0]
        if pd.notna(r.get("direction_adjusted_mean_rank_ic")):
            row[f"ic_{hz}"] = f"{r['direction_adjusted_mean_rank_ic']:+.4f}"
            row[f"t_{hz}"] = f"{r['t_stat']:.1f}"
            row[f"n_{hz}"] = f"{int(r['n_periods'])}"
        else:
            row[f"ic_{hz}"] = "NOT_COMPUTED"
            row[f"t_{hz}"] = "—"
            row[f"n_{hz}"] = "—"
    rows.append(row)

rows.sort(key=lambda r: (r["status"] != "MISSING_FACTOR_VALUES",
                         -abs(float(r["ic_1h"].replace("+","")) if r["ic_1h"] not in ("—","NOT_COMPUTED") else 0)))

# CSS for status tags
status_colors = {
    "COMPUTED": ("#22c55e", "#052e16"),
    "ACTIVE_IN_SIGNAL_COMPUTED": ("#3b82f6", "#1e1b4b"),
    "DIRECTION_UNKNOWN": ("#f59e0b", "#451a03"),
    "MISSING_FACTOR_VALUES": ("#ef4444", "#450a0a"),
    "NO_VALID_PERIODS": ("#6b7280", "#1f2937"),
}

def status_badge(s):
    bg, fg = status_colors.get(s, ("#6b7280", "#1f2937"))
    return f'<span style="background:{bg};color:{fg};padding:2px 8px;border-radius:4px;font-size:11px">{s}</span>'

def sig_mark(in_sig):
    return "★" if in_sig else ""

# Build HTML
table_rows = ""
for r in rows:
    ic_cells = ""
    for hz in horizons:
        val = r[f"ic_{hz}"]
        t = r[f"t_{hz}"]
        n = r[f"n_{hz}"]
        if val in ("—", "NOT_COMPUTED"):
            ic_cells += f'<td style="text-align:center;color:#94a3b8">{val}</td>'
        else:
            fv = float(val.replace("+",""))
            color = "#22c55e" if abs(fv) >= 0.02 else "#f59e0b" if abs(fv) >= 0.01 else "#e2e8f0"
            ic_cells += f'<td style="text-align:center;color:{color};font-weight:600">{val}</td>'
        ic_cells += f'<td style="text-align:center;color:#94a3b8;font-size:11px">{t}</td>'
        ic_cells += f'<td style="text-align:center;color:#64748b;font-size:11px">{n}</td>'

    table_rows += f'''<tr>
  <td>{sig_mark(r["in_signal"])} {r["factor"]}</td>
  <td>{r["category"]}</td>
  <td>{r["direction"]}</td>
  <td>{status_badge(r["status"])}</td>
  {ic_cells}
</tr>
'''

# Computed count
n_computed = len([r for r in rows if "COMPUTED" in r["status"]])
n_missing = len([r for r in rows if r["status"] == "MISSING_FACTOR_VALUES"])
n_total = len(rows)

# Top factors
top_factors = [r for r in rows if r["in_signal"] and r["ic_1h"] not in ("—", "NOT_COMPUTED")]
top_factors.sort(key=lambda r: abs(float(r["ic_1h"].replace("+",""))))

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Factor-Level IC Evaluation</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }}
h1 {{ color: #f1f5f9; font-size: 22px; margin-bottom: 8px; }}
h2 {{ color: #cbd5e1; font-size: 16px; margin: 24px 0 12px; }}
.subtitle {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
.stats {{ display: flex; gap: 16px; margin-bottom: 20px; flex-wrap: wrap; }}
.stat {{ background: #1e293b; border-radius: 8px; padding: 12px 18px; min-width: 120px; }}
.stat-val {{ font-size: 24px; font-weight: 700; color: #f1f5f9; }}
.stat-label {{ font-size: 11px; color: #94a3b8; margin-top: 4px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th {{ background: #1e293b; color: #94a3b8; padding: 8px 10px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; position: sticky; top: 0; }}
td {{ padding: 6px 10px; border-bottom: 1px solid #1e293b; }}
tr:hover {{ background: #1e293b40; }}
.hz-header {{ text-align: center; color: #3b82f6; }}
.method-box {{ background: #1e293b; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 13px; line-height: 1.6; color: #94a3b8; }}
.method-box strong {{ color: #e2e8f0; }}
.parity-box {{ background: #064e3b; border: 1px solid #22c55e; border-radius: 8px; padding: 16px; margin: 16px 0; font-size: 13px; line-height: 1.6; color: #a7f3d0; }}
.parity-box strong {{ color: #6ee7b7; }}
footer {{ margin-top: 24px; padding-top: 12px; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; display: flex; gap: 16px; }}
footer a {{ color: #60a5fa; text-decoration: none; }}
footer a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>

<h1>Factor-Level IC Evaluation</h1>
<p class="subtitle">Direction-adjusted RankIC (Spearman) · {n_total} registered factors · {n_computed} computed · {n_missing} missing FV · Generated {manifest["generated"][:10]}</p>

<div class="stats">
 <div class="stat"><div class="stat-val">{n_computed}</div><div class="stat-label">Computed</div></div>
 <div class="stat"><div class="stat-val">{n_missing}</div><div class="stat-label">Missing FV</div></div>
 <div class="stat"><div class="stat-val">{len([r for r in rows if r["in_signal"]])}</div><div class="stat-label">In Signal</div></div>
 <div class="stat"><div class="stat-val">4</div><div class="stat-label">Horizons</div></div>
</div>

<div class="method-box">
 <strong>方法说明</strong><br>
 Factor-level IC 是单因子 vs forward return 的 RankIC（Spearman），不同于 signal-level RankIC（组合信号 vs forward return）。<br>
 计算方法：每个 timestamp 内 rank(factor_value) 与 rank(forward_return) 的 Pearson 相关系数。Direction-adjusted：负方向因子 IC 取反。<br>
 详见 <code>scripts/evaluate_factors.py</code>。
</div>

<div class="parity-box">
 <strong>H8-R Parity Check (2026-06-19)</strong><br>
 evaluate_factors.py 与 momentum.signal_evaluation.compute_rank_ic 公共 API 做了抽样 parity 验证。<br>
 测试因子：vol_5h, vol_40h, rsi_7h, range_1h, price_pos_24h × horizons 1h, 24h。<br>
 结果：<strong>10/10 PASS，max mean RankIC diff = 0.00e+00（exact match）</strong>。<br>
 Root cause 已修复：NaN factor_value 行必须在 rank 前 dropna，否则 tied return values 的平均 rank 会偏移。
</div>

<table>
<thead>
<tr>
 <th>Factor</th><th>Category</th><th>Direction</th><th>Status</th>
 <th colspan="3" class="hz-header">1h IC / t / n</th>
 <th colspan="3" class="hz-header">4h IC / t / n</th>
 <th colspan="3" class="hz-header">24h IC / t / n</th>
 <th colspan="3" class="hz-header">72h IC / t / n</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>

<footer>
 <a href="index.html">← 首页</a>
 <a href="repository-map.html">代码结构</a>
 <a href="actual-script-map.html">执行脚本地图</a>
 <a href="signal-evaluation-summary.html">信号评价</a>
</footer>

</body>
</html>'''

OUT.write_text(html, encoding="utf-8")
print(f"Wrote {OUT} ({len(html)} bytes)")
