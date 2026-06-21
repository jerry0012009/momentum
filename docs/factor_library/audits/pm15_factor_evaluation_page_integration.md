# PM-15 Factor Evaluation Page Integration

**Date:** 2026-06-21
**Follows:** PM-14B (factor card review and polish)

---

## Summary Verdict

**`FACTOR_EVAL_PAGE_INTEGRATION_PASS`**

The existing factor-evaluation.html page has been upgraded to consume diagnostics metrics and bilingual factor cards. The page is now bilingual (Chinese-first), interactive, and decision-oriented with SVG charts.

---

## 1. Files Changed/Generated

| File | Action |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Rewritten (35KB, ~570 lines) |
| `reports/site/factor-library/factor-evaluation.html` | Regenerated (848KB) |

Generator remains **reproducible**: `python scripts/_build_factor_eval_html.py` regenerates the page deterministically from 6 CSV inputs.

---

## 2. Inputs Consumed

| Input | Rows | Factors |
|-------|------|---------|
| factor_diagnostics_summary.csv | 71 | 71 |
| factor_monthly_ic_series.csv | 7076 | 71 |
| factor_monthly_long_short_series.csv | 7076 | 71 |
| factor_cumulative_long_short_curve.csv | 7076 | 71 |
| factor_bilingual_cards.csv | 71 | 71 |
| factor_card_qa_report.csv | 71 | 71 |

Join count: 71/71 factors.

---

## 3. Existing Page Upgraded (Not New Page)

The existing `reports/site/factor-library/factor-evaluation.html` was upgraded in-place. No new public page was created.

---

## 4. Page Features

### Top Summary Section
- Factor count: 71
- Horizons: 1h / 4h / 24h / 72h
- Months covered (from monthly IC series)
- Quality badge distribution: 完整/方向模糊/需复核/公式模糊
- Disclaimer: "仅作研究诊断 / Diagnostic only"

### Main Factor Table
- 14 columns with bilingual headers
- 4 filter controls: search, family, quality, horizon
- Click column headers to sort (Sharpe default desc)
- Quality/direction colored badges

### Factor Detail Panel
- Bilingual: name_zh/name_en, formula_zh/formula_en, intuition_zh/intuition_en
- Direction explanation (bilingual)
- Known limitations (bilingual)
- Data source type
- Metadata quality with QA notes
- Best horizon metrics from diagnostics_summary

### SVG Charts (no external library)
- Monthly RankIC line chart (月度RankIC)
- Monthly LS bar chart (月度多空收益)
- Cumulative LS curve with drawdown shading (累计多空曲线)

### Bilingual Display
- Chinese-first with English secondary
- Quality badges: 完整/方向模糊/需复核/公式模糊
- Direction badges: 正向/负向/条件式
- Review flags displayed honestly

---

## 5. Metadata Quality Distribution on Page

| Quality | Count | Badge |
|---------|-------|-------|
| COMPLETE | 41 | 完整 |
| DIRECTION_AMBIGUOUS | 21 | 方向模糊 |
| NEEDS_REVIEW | 6 | 需复核 |
| FORMULA_AMBIGUOUS | 3 | 公式模糊 |

---

## 6. Validation Results

- `python -m py_compile scripts/_build_factor_eval_html.py` → OK
- `python scripts/_build_factor_eval_html.py` → Wrote 848KB
- Join count: 71/71
- Contains: Sharpe, 最大回撤, Long-Short, 多空, DIRECTION_AMBIGUOUS, NEEDS_REVIEW, FORMULA_AMBIGUOUS, COMPLETE, 方向模糊, 需复核, 公式模糊, 完整, 仅作研究诊断, 因子库, 正向, 负向, 条件式
- No external CDN dependencies

---

## 7. Known Limitations

- diagnostics_summary only has best_horizon data (not per-horizon breakdowns), so the detail panel shows best_horizon metrics only
- Monthly IC/LS/cumulative charts are filtered to best_horizon
- No per-horizon comparison table (would require metric_panel data)
- SVG charts are lightweight sparklines, not full interactive charts

---

## 8. Non-Change Statement

- No factor formulas modified.
- No `scripts/factor_formula_registry.py` modified.
- No `scripts/factor_ops.py` modified.
- No factor_values modified.
- No signal panel modified.
- No other public pages modified.

---

## 9. Recommended Next PM

**PM-16: Signal evaluation page upgrade** — Apply similar bilingual + diagnostics treatment to signal-evaluation-summary.html
