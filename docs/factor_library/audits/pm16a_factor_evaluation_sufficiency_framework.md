# PM-16A Factor Evaluation Sufficiency Framework

**Date:** 2026-06-21
**Follows:** PM-15 (factor evaluation page integration)

---

## Summary Verdict

**`EVALUATION_FRAMEWORK_READY_WITH_GAPS`**

The current factor evaluation page is **sufficient to judge factor quality** for most purposes. 5 of 7 evidence dimensions are fully covered. 2 dimensions have meaningful gaps (quantile shape analysis not surfaced, redundancy matrix sparse). The highest-severity gap is redundancy coverage (6/2485 pairs = 0.2%).

---

## 1. Current Repository State

| Metric | Value |
|--------|-------|
| Registered factors | 71 |
| Computed factor_values | 71 |
| Missing factor_values | 0 |
| Active signal factors | 10 |
| Signal variants | 3 |
| Public pages | 4 |
| Evaluation months | 25 |
| Horizons | 1h, 4h, 24h, 72h |
| Bilingual cards | 71 (41 COMPLETE, 21 DIRECTION_AMBIGUOUS, 6 NEEDS_REVIEW, 3 FORMULA_AMBIGUOUS) |

---

## 2. Evidence Dimensions Coverage

| Dimension | Status | Gap Severity |
|-----------|--------|-------------|
| Computation Integrity | ✅ FULLY_COVERED | MEDIUM (lookback not displayed) |
| Predictive Ranking | ✅ FULLY_COVERED | LOW (n_obs not prominent) |
| Portfolio Extraction | ✅ FULLY_COVERED | NONE |
| Quantile Shape | ⚠️ DATA_AVAILABLE_NOT_SURFACED | MEDIUM |
| Direction & Economic | ✅ FULLY_COVERED | LOW (QA notes not prominent) |
| Novelty / Redundancy | ⚠️ SPARSE | HIGH |
| Extensibility | ⚠️ FUNCTIONAL_NOT_CONTRACTUALIZED | MEDIUM |

---

## 3. Is Current Page Sufficient?

**Yes, with caveats.** The current factor-evaluation.html page displays:

- ✅ 71 factors with bilingual names, formulas, intuition, limitations
- ✅ RankIC, ICIR, t-stat, monthly IC positive rate
- ✅ Sharpe, annualized return, max drawdown, positive month rate
- ✅ Coverage rate
- ✅ Decision bucket and recommended action
- ✅ Monthly IC chart (25 months)
- ✅ Monthly LS bar chart
- ✅ Cumulative LS curve with drawdown shading
- ✅ Quality badges (完整/方向模糊/需复核/公式模糊)
- ✅ Direction badges (正向/负向/条件式)

**Missing from page:**
- ❌ Quantile shape analysis (data exists but not surfaced)
- ❌ Full redundancy matrix (only 6 pairs)
- ❌ Lookback window
- ❌ n_obs per month
- ❌ QA notes from bilingual card review

---

## 4. Highest-Severity Gaps

### 4.1 Redundancy Coverage (HIGH)

Current: 6 pairs out of C(71,2) = 2485 possible pairs (0.2% coverage).

Most factors show `NO_CURRENT_PAIR` — this does NOT mean they are unique, just that redundancy hasn't been measured.

Within-family redundancy is particularly important:
- Momentum family: mom_5h, mom_10h, mom_20h, mom_40h, mom_72h, mom_120h, mom_accel_20h (7 factors)
- Reversal family: rev_1h, rev_3h, rev_10h, rev_24h, rev_72h, reversal_5h (6 factors)
- Volatility family: vol_5h, vol_20h, vol_40h, volatility_20h, vol_ratio_5_20, vol_ratio_20_80 (6 factors)

**Recommendation:** PM-18 should compute within-family redundancy first (fast win), then full pairwise matrix.

### 4.2 Quantile Shape Analysis (MEDIUM)

Data exists: 35,380 period-level quantile rows + 1,420 aggregate quantile rows. But:
- Monotonicity labels are only in old evaluator outputs (metric_panel), not in new diagnostics summary
- The factor-evaluation page does not show quantile shape
- No automated IC-quantile consistency check

**Recommendation:** PM-16B should add quantile shape to the scorecard.

---

## 5. RankIC vs Sharpe: Not a Contradiction

RankIC and Sharpe measure **different evidence dimensions**:

| | RankIC | Sharpe |
|---|--------|--------|
| Measures | Cross-sectional ranking | Portfolio extraction quality |
| Question | Does the factor rank assets correctly? | Does a long-short portfolio work? |
| Strengths | Robust to outliers, direction-free | Directly measures investable outcome |
| Weaknesses | Ignores portfolio construction | Sensitive to costs, construction choices |

**When they disagree:** A factor can have strong RankIC but weak Sharpe if:
1. Signal is concentrated in tails only
2. Returns are driven by a few months
3. Factor is direction-ambiguous

This is **not a simple contradiction** — it requires investigation using quantile shape, monthly stability, and cumulative curve evidence.

**Recommendation:** Use RankIC for screening, Sharpe for viability. Investigate disagreements within the evidence framework.

---

## 6. Recommended Next 3–5 PM Tasks

| PM | Title | Priority |
|----|-------|----------|
| PM-16B | Factor Quality Scorecard Builder | HIGH |
| PM-17 | Integrate Scorecard into Factor Evaluation Page | HIGH |
| PM-18 | Full Pairwise Redundancy Matrix | HIGH |
| PM-19 | Extensibility / Regeneration Contract | MEDIUM |
| PM-20 | Factor Expansion Backlog | LOW |

---

## 7. Non-Change Statement

- No factors added or modified.
- No formulas modified.
- No factor_values modified.
- No signal panel modified.
- No public pages modified.
- No scripts modified.
