# PM-50: Factor Evaluation Page Explanation Layer — Audit

**Date**: 2026-06-23
**PM**: PM-50
**Verdict**: `PM50_PAGE_EXPLANATION_LAYER_PASS`

---

## Summary

将 PM-49 研究解释整合进 factor-evaluation.html 页面，让页面本身可读、可解释、可审阅。
新增 tooltip/glossary、research interpretation、red flag badges、evidence/judgment 区分。
无公式、expected_direction、factor_values、signal panel 修改。

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Python: load PM-49 JSON, inject into payload. CSS/HTML/JS: tooltips, glossary, badges, How-to-Read, interpretation panel |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt with new features (3.03MB) |
| `docs/factor_library/reviews/PM49_RECENT_FACTOR_INTERPRETATION_REVIEW.md` | Source alignment corrections |
| `factor_diagnostics/recent_factor_interpretation_review.{csv,json}` | Updated decisions + LS data |
| `factor_diagnostics/factor_direction_semantics_review.{csv,json}` | Updated decisions |

---

## PM-49 Source Alignment Corrections

1. **rev_2h LS data**: Replaced "数据不足" with actual values from canonical source (Sharpe=1.73, Ann Ret=0.09%, MaxDD=-0.06%, Win=56%)
2. **clv_20h text**: Changed from "唯一方向完全对齐" to "best horizon 72h 与 expected_direction 对齐; short horizon shows reversal; direction status = SHORT_HORIZON_REVERSAL"
3. **5 CONFLICT factors**: Unified to DIRECTION_SEMANTICS_REVIEW_REQUIRED (removed FORMULA_REVIEW_REQUIRED and DIRECTION_REVIEW_REQUIRED). No longer suggesting direct formula/direction changes.

---

## Page Explanation Modules Added

### 1. How to Read This Page (可折叠)
- Collapsible section at page top
- 11-step reading order (Evidence → RankIC → LS → Paper → Fee → Regime → Shape → Capacity → Redundancy → Scorecard → Interpretation)
- 5 key warnings (Evidence ≠ good, RankIC ≠ return, Paper ≠ strategy, Scorecard ≠ signal, Interpretation ≠ signal)
- Bilingual (ZH/EN)

### 2. Tooltip/Glossary (21 terms)
- RankIC Mean, IC t-stat, ICIR, LS Mean, LS Sharpe, Ann Return, Max Drawdown
- Paper Gross Return, Fee Sensitivity, Breakeven Fee
- Paper-BTC Corr, LS-BTC Corr, Bull-Bear Δ
- Quantile Shape, Decile Shape, Rolling Stability
- Capacity/Liquidity, Redundancy, Marginal Info
- Quality Score, Profile Score
- Each tooltip: what it is, high/low meaning, common misreadings, signal status

### 3. Research Interpretation Summary (per factor)
- Research Decision badge
- Direction Status badge
- Main Issue (ZH)
- Suggested Action (ZH)
- Not-Signal warning
- Only shown for 7 PM-49 factors (others unaffected)

### 4. Red Flag Badges (10 types)
- DIRECTION_CONFLICT, SHORT_HORIZON_REVERSAL, COST_COLLAPSED
- REGIME_DEPENDENT, HIGH_REDUNDANCY, LOW_MARGINAL_INFO
- FORMULA_REVIEW_CANDIDATE, DIRECTION_SEMANTICS_REVIEW_REQUIRED
- CANDIDATE_POOL_WATCHLIST, DIAGNOSTIC_ONLY

### 5. Evidence vs Judgment Distinction
- Blue left border + label for Evidence sections (机器计算指标)
- Amber left border + label for Judgment sections (PM-49 研究解释)
- Judgment panel includes explicit "非交易信号" warning

---

## 7-Factor Interpretation Visibility

| Factor | Decision | Direction | Red Flags | Visible |
|--------|----------|-----------|-----------|---------|
| rev_2h | LOWER_PRIORITY_REVIEW | ALIGNED | COST_COLLAPSED | ✅ |
| mom_vol_adjusted_20h | DIRECTION_SEMANTICS_REVIEW_REQUIRED | CONFLICT | 4 flags | ✅ |
| range_breakout_vol_confirm_20h | DIRECTION_SEMANTICS_REVIEW_REQUIRED | CONFLICT | 5 flags | ✅ |
| volume_pressure_20h | DIRECTION_SEMANTICS_REVIEW_REQUIRED | CONFLICT | 3 flags | ✅ |
| xs_rank_mom_accel | DIRECTION_SEMANTICS_REVIEW_REQUIRED | CONFLICT | 1 flag | ✅ |
| up_down_vol_ratio_20h | DIRECTION_SEMANTICS_REVIEW_REQUIRED | CONFLICT | 4 flags | ✅ |
| clv_20h | CANDIDATE_POOL_WATCHLIST | REVERSAL | 2 flags | ✅ |

---

## QA Result

| Check | Status |
|-------|--------|
| Page exists and size < 4.5MB | ✅ (3.03MB) |
| 78/78 factors visible | ✅ |
| Page QA 26/26 PASS | ✅ |
| PM-49 data loaded (7/7 factors) | ✅ |
| How-to-Read section visible | ✅ |
| Tooltip/glossary (21 terms) | ✅ |
| Red flag badges | ✅ |
| Evidence/Judgment distinction | ✅ |
| No signal construction wording | ✅ |
| No trading recommendation wording | ✅ |
| No formula/direction/factor_values changes | ✅ |

---

## No Out-of-Scope Changes

| Check | Status |
|-------|--------|
| No formula changes | ✅ |
| No expected_direction changes | ✅ |
| No factor_values changes | ✅ |
| No signal panel changes | ✅ |
| No new factors | ✅ |

---

## Remaining Limitations

1. Tooltip only on Best Horizon Metrics grid (7 metrics). Other sections (paper, regime, shape, capacity) don't have tooltips yet.
2. PM-49 interpretation only covers 7 factors. Other 71 factors have no research interpretation.
3. How-to-Read section is static (not contextual per section).
4. Red flag badges only for PM-49 factors.

---

## Recommended Next PM

**PM-51**: Direction Semantics Review Implementation
- For 5 DIRECTION_SEMANTICS_REVIEW_REQUIRED factors: empirical analysis of direction semantics in crypto
- Or: PM-51 — v0.1 tag + deployment hardening
