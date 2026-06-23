# PM-51: Metric Computation Glossary + Page Hover Explanation Layer — Audit

**Date**: 2026-06-23
**PM**: PM-51
**Verdict**: `PM51_METRIC_GLOSSARY_HOVER_LAYER_PASS`

---

## Summary

建立结构化 metric glossary（68 条目），在 factor-evaluation.html 实现 hover tooltip + click 展开详细解释，为 11 种图表添加 "How to read this chart"，添加 inference guardrail 标签系统。

## Files Changed

| File | Change |
|------|--------|
| `scripts/factor_metric_glossary.json` | NEW — 68 metric glossary entries |
| `scripts/_build_factor_eval_html.py` | Modified — glossary loading, tooltip/detail panel, chart guides, guard badges, CSS |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt — 3,084KB |

## Glossary Coverage: 68 Metrics

### Best Horizon Metrics (13)
RankIC Mean, RankIC Std, ICIR, IC t-stat, IC Win Rate, LS Mean, LS Std, LS Sharpe, Ann Return, Ann Vol, Max Drawdown, LS Win Rate, Coverage

### Paper Portfolio (8)
Gross Sharpe, Gross Return, Paper Max DD, Positive Mo%, Avg Turnover, Median Turnover, B/E Fee, 0/5/10/20bps Return

### Fee Sensitivity (1)
B/E Fee (covers COST_COLLAPSED etc. via label maps)

### Regime/BTC (8)
Paper-BTC Corr, Paper-BTC Beta, LS-BTC Corr, LS-BTC Beta, IC-BTC Corr, Bull-Bear Δ, HV-LV Δ, DD-Normal Δ, Regime Class

### Shape (7)
Quantile Shape, Stability Score, Q Spread Return, Q Spearman, Positive Spread%, Dir-aware ρ, Decile Mono., Tail Conc.

### Capacity/Liquidity (14)
Avg/Median/P90 Turnover, Basket Vol Median/P10, Low-Vol Share, Top Symbol Vol Share, 1/5/10% Participation, $100K/$1M/$10M Median/P10

### Redundancy (6)
Nearest Factor, Nearest abs Spearman, Redundancy Confidence, Cluster Role, Marginal Info

### Scorecard/Profile (6)
Quality Score, Profile Score, Evidence Completeness, Research Decision, Direction Status, Red Flag Badges

## Sections Covered

| Section | Chart Guide | Tooltips | Guard Badges |
|---------|-------------|----------|--------------|
| Best Horizon Metrics | ✅ Monthly RankIC | 13/13 | ✅ Evidence |
| LS Charts | ✅ Monthly LS, Cum LS | 8/8 | ✅ Evidence |
| Paper Portfolio | ✅ Paper NAV | 8/8 | ✅ Evidence |
| Fee Sensitivity | ✅ Fee Sensitivity | 1/1 | ✅ Evidence |
| Regime/BTC | ✅ Regime IC/LS/Paper | 9/9 | ✅ Evidence |
| Shape | ✅ Quantile/Decile | 7/7 | ✅ Evidence |
| Capacity/Liquidity | — | 14/14 | ✅ Evidence |
| Redundancy | — | 6/6 | ✅ Diagnostic |
| Scorecard/Profile | — | 6/6 | ✅ Diagnostic |
| PM-49 Research Interpretation | — | 7/7 | ✅ Interpretation |

## Tooltip vs Expanded Detail

- **Hover tooltip**: 2-4 line brief explanation + signal badge + "click for details" hint
- **Click expanded**: Full detail panel with 9 sections:
  1. 它是什么 / What
  2. 怎么算 / Formula
  3. 数据来源 / Source (file + columns)
  4. 高值含义 / High
  5. 低值含义 / Low
  6. 常见误读 / Misreading
  7. 可以推断 / Can Infer (with guard badge)
  8. 不能推断 / Cannot Infer (with guard badge)
  9. 关联指标 / Linked (clickable)

## Chart Reading Guide Coverage: 11 Charts

1. Monthly RankIC
2. Monthly Long-Short Return
3. Cumulative Long-Short Curve
4. Paper Portfolio NAV
5. Fee Sensitivity
6. Monthly Turnover
7. Regime: IC by Market State
8. Regime: LS by Market State
9. Regime: Paper Return by State
10. Q1-Q5 Quantile Shape
11. D1-D10 Decile Shape

## Inference Guardrails

| Badge | Meaning | Usage |
|-------|---------|-------|
| 📊 Evidence | Machine-computed historical evidence | All metric tooltips |
| 🔬 Interpretation | PM-49 research judgment | Research Decision section |
| 💡 Inference | Cautious real-world inference | Chart guides, detail panel |
| 🚫 Not a Signal | Cannot be used as trading signal | All tooltips, chart guides |
| ⚠️ Requires Validation | Needs signal-level validation | PM-49 factors |

## QA Result: PASS

| Check | Result |
|-------|--------|
| Glossary loaded | ✅ 68 entries |
| All metric_key entries | ✅ 68/68 |
| Best Horizon tooltips | ✅ 13/13 |
| Chart guides | ✅ 11/11 |
| No trading recommendation | ✅ |
| No signal construction | ✅ |
| Factor count 78 | ✅ |
| Page size | ✅ 3,084KB (<5MB) |
| PM-49 visible | ✅ 7/7 factors |

## Public Page Result

- URL: https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
- Size: 3,084KB (gzip ~350KB)
- Cache-Control: max-age=3600

## No Unauthorized Changes

- ✅ No formula changes
- ✅ No expected_direction changes
- ✅ No factor_values changes
- ✅ No signal panel changes
- ✅ No signal construction
- ✅ No new factors

## Remaining Limitations

1. 11 metricRow calls still without tooltips (minor/duplicate metrics)
2. Capacity/Liquidity section lacks chart guide (no dedicated chart)
3. Redundancy section lacks chart guide
4. Detail panel position may overflow on small screens
5. Chart guide text is hardcoded, not from glossary

## Recommended Next PM

PM-52: Signal Construction Readiness Gate 或 v0.1 tag + deployment hardening
