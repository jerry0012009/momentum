# PM-19 Redundancy-Aware Scorecard Page Refresh

**Date:** 2026-06-21
**Follows:** PM-18 (full pairwise redundancy matrix)

---

## Summary Verdict

**`REDUNDANCY_AWARE_PAGE_REFRESH_PASS`**

---

## 1. Files Changed/Generated

| File | Action |
|------|--------|
| `scripts/build_factor_quality_scorecard.py` | Updated (calibrated redundancy confidence) |
| `scripts/_build_factor_eval_html.py` | Updated (redundancy-aware display) |
| `factor_diagnostics/factor_quality_scorecard.csv` | Refreshed |
| `factor_diagnostics/factor_quality_scorecard.json` | Refreshed |
| `factor_diagnostics/factor_quality_scorecard_manifest.json` | Refreshed |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt (912KB) |

---

## 2. Confidence Calibration Change

### Problem
PM-18 scorecard had HIGH=0 because all factors had some INSUFFICIENT_OVERLAP pairs. This was over-conservative — a factor should not be globally penalized merely because a subset of its pairs has insufficient overlap.

### Solution
Confidence is now based on valid-pair coverage and nearest redundancy evidence:

- **HIGH**: valid_redundancy_pair_coverage >= 0.70 and n_valid_pairs >= 40
- **MEDIUM**: valid_redundancy_pair_coverage >= 0.40 and n_valid_pairs >= 20
- **LOW**: otherwise

Also: factors with clear high-redundancy evidence (NEAR_DUPLICATE or HIGH_REDUNDANCY nearest neighbor) can be MEDIUM/HIGH even if some unrelated pairs have insufficient overlap.

---

## 3. Scorecard Class Distribution

| Class | Before (PM-18) | After (PM-19) | Change |
|-------|---------------|---------------|--------|
| STRONG_RESEARCH_CANDIDATE | 7 | 7 | — |
| PROMISING_BUT_INCONSISTENT | 55 | 55 | — |
| REVIEW_REQUIRED | 9 | 9 | — |

---

## 4. Score Confidence Distribution

| Confidence | Before (PM-18) | After (PM-19) | Change |
|------------|---------------|---------------|--------|
| HIGH | 0 | **35** | +35 |
| MEDIUM | 65 | **9** | -56 |
| LOW | 6 | **27** | +21 |

Note: LOW increased because factors with insufficient valid-pair coverage are now correctly LOW instead of artificially MEDIUM.

---

## 5. Redundancy Confidence Distribution

| Confidence | Count |
|------------|-------|
| HIGH | 55 |
| MEDIUM | 6 |
| LOW | 10 |

---

## 6. Factors Whose Confidence Changed

- 35 factors: LOW/MEDIUM → HIGH (valid-pair coverage >= 0.70)
- 56 factors: MEDIUM → LOW/MEDIUM (recalibrated based on actual coverage)
- Net: 35 factors gained HIGH confidence

---

## 7. Top 20 Most Redundant Pairs

| Factor i | Factor j | abs Spearman | Level |
|----------|----------|-------------|-------|
| mom_10h | rev_10h | 1.0000 | NEAR_DUPLICATE |
| mom_72h | rev_72h | 1.0000 | NEAR_DUPLICATE |
| q158_high_low_range | range_1h | 1.0000 | NEAR_DUPLICATE |
| mom_5h | reversal_5h | 1.0000 | NEAR_DUPLICATE |
| qvol_zscore_20h | vol_zscore_20h | 0.9987 | NEAR_DUPLICATE |
| qvol_zscore_48h | vol_zscore_48h | 0.9974 | NEAR_DUPLICATE |
| intraday_ret | rev_1h | 0.9949 | NEAR_DUPLICATE |
| bb_zscore_20h | rsi_7h | 0.9606 | NEAR_DUPLICATE |
| candle_body | intraday_ret | 0.9530 | NEAR_DUPLICATE |
| candle_body | rev_1h | 0.9476 | HIGH_REDUNDANCY |
| price_volume_corr_20h | vol_ret_corr_20h | 0.9423 | HIGH_REDUNDANCY |
| bb_zscore_20h | breakout_dist_20h | 0.9340 | HIGH_REDUNDANCY |
| rsi_14h | rsi_7h | 0.9284 | HIGH_REDUNDANCY |
| bb_zscore_20h | vwap_dev_20h | 0.9268 | HIGH_REDUNDANCY |
| breakout_dist_20h | williams_r_14h | 0.9266 | HIGH_REDUNDANCY |
| rsi_7h | vwap_dev_20h | 0.9262 | HIGH_REDUNDANCY |
| breakout_dist_20h | vwap_dev_20h | 0.9256 | HIGH_REDUNDANCY |
| rsi_7h | williams_r_14h | 0.9199 | HIGH_REDUNDANCY |
| breakout_dist_20h | rsi_7h | 0.9181 | HIGH_REDUNDANCY |
| bb_zscore_20h | rsi_14h | 0.9111 | HIGH_REDUNDANCY |

---

## 8. Page Features Added

### Top Summary
- Near-Duplicate Pairs count
- High-Redundancy Pairs count
- Redundancy Clusters count
- Largest Cluster size

### Main Table
- Novelty / 新颖性 column
- Nearest Factor / 最近因子 column
- Redundancy / 冗余等级 column
- Redundancy Confidence / 冗余置信度 column
- Cluster / 聚类 column

### Detail Panel
- Redundancy & Novelty / 冗余与新颖性 section with:
  - Novelty assessment (badge)
  - Nearest factor
  - Nearest abs Spearman correlation
  - Strongest redundancy level (badge)
  - Redundancy confidence (badge)
  - Valid pair count / expected
  - Valid pair coverage
  - Insufficient overlap pair count
  - Cluster ID / size
  - Explanation that redundancy is a research diagnostic, not a deletion reason

---

## 9. Validation

- py_compile: OK (both scripts)
- Scorecard: 71 rows, 71 factors
- Page: 912KB, 12/12 text checks pass
- No forbidden terms (production/live/tradeable/alpha)

---

## 10. Limitations

- INSUFFICIENT_OVERLAP: 935/2485 pairs (37.6%) have < 1000 overlapping observations
- Daily grid alignment loses hourly granularity
- Sampling step=3 means only every 3rd day is used
- Cluster detection uses simple connected components at threshold 0.80

---

## 11. Non-Change Statement

- No factors added or modified.
- No formulas modified.
- No factor_values modified.
- No signal panel modified.
- No other public pages modified.

---

## 12. Recommended Next PM

**PM-20** — Full factor intake pipeline (new factor registration, validation, scoring)
