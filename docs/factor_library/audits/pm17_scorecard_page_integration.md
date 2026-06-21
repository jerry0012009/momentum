# PM-17 Scorecard Page Integration

**Date:** 2026-06-21
**Follows:** PM-16B (factor quality scorecard)

---

## Summary Verdict

**`SCORECARD_PAGE_INTEGRATION_PASS`**

The existing factor-evaluation.html page has been upgraded to display the PM-16B factor quality scorecard as a first-class decision layer. All existing features (charts, badges, bilingual cards, diagnostics) are preserved.

---

## 1. Files Changed/Generated

| File | Action |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Upgraded (+481 lines, -38 lines) |
| `reports/site/factor-library/factor-evaluation.html` | Regenerated (907KB) |

---

## 2. Confirmation

The existing `factor-evaluation.html` was **upgraded**, not replaced by a new page. No new public page was created.

---

## 3. Scorecard Input Coverage

- Scorecard CSV: 71 factors
- Join to existing payload: 71/71
- Quality class distribution: STRONG=12, PROMISING=50, REVIEW=9

---

## 4. Page Features Added

### 4.1 Top Summary Section
- Quality class distribution cards (STRONG/PROMISING/REVIEW counts)
- Confidence distribution (HIGH/MEDIUM/LOW counts)
- Prominent redundancy caveat: "冗余置信度大部分为 LOW，因冗余矩阵仅覆盖 6/2485 对。PM-18 将扩展。"

### 4.2 Main Factor Table
- New columns: Quality Class 质量分类, Score 分数, Confidence 置信度, Main Action 建议动作
- New filters: final_quality_class dropdown, score_confidence dropdown
- Default sort: final_quality_score descending
- All existing columns preserved (RankIC, ICIR, Sharpe, drawdown, coverage, etc.)

### 4.3 Factor Detail Panel
- New section: "Factor Quality Scorecard / 因子质量记分卡"
- Quality class badge (bilingual)
- Score bar (visual)
- Confidence badge
- Recommended next action
- Strengths/weaknesses/review notes (bilingual)
- 7 sub-score horizontal bars:
  - computation_integrity_score 计算完整性
  - predictive_ranking_score 预测排名能力
  - portfolio_extraction_score 组合提取能力
  - stability_score 稳定性
  - quantile_shape_score 分位形状
  - direction_interpretability_score 方向可解释性
  - redundancy_novelty_score 冗余新颖性
- Color coding: green ≥70, yellow 40-70, red <40

### 4.4 Interpretation Caveats
- STRONG_RESEARCH_CANDIDATE = strong research evidence, NOT deployable strategy
- PROMISING_BUT_INCONSISTENT = meaningful evidence but mixed
- REVIEW_REQUIRED = needs review before quality judgment
- Score confidence may be capped by sparse redundancy coverage
- "本记分卡为研究分诊工具，不是交易建议 / This scorecard is a research triage tool, not a trading recommendation"

---

## 5. Preserved Features

- ✅ Bilingual display (Chinese-first)
- ✅ Monthly RankIC chart
- ✅ Monthly LS bar chart
- ✅ Cumulative LS curve with drawdown
- ✅ Formula / intuition / limitations
- ✅ Quality badges (完整/方向模糊/需复核/公式模糊)
- ✅ Direction badges (正向/负向/条件式)
- ✅ All existing filters

---

## 6. Validation Results

- py_compile: OK
- Page size: 906,893 bytes (0.86 MB) — under 2MB
- All 17 text checks pass:
  - Factor Quality Scorecard ✓
  - 因子质量记分卡 ✓
  - STRONG_RESEARCH_CANDIDATE ✓
  - PROMISING_BUT_INCONSISTENT ✓
  - REVIEW_REQUIRED ✓
  - final_quality_score ✓
  - score_confidence ✓
  - redundancy confidence ✓
  - 冗余 ✓
  - 不是交易建议 ✓
  - All 7 sub-score fields ✓

---

## 7. Known Limitations

- Sub-score bars are static (no hover/tooltip detail)
- No per-horizon scorecard breakdown (uses best_horizon only)
- Redundancy score is low-confidence for 67/71 factors
- No interactive drill-down from scorecard to raw evidence

---

## 8. Non-Change Statement

- No factors added or modified.
- No formulas modified.
- No factor_values modified.
- No signal panel modified.
- No other public pages modified.

---

## 9. Recommended Next PM

**PM-18** — Full pairwise redundancy matrix (expand from 6/2485 to within-family at minimum)
