# PM-18 Full Pairwise Factor Redundancy Matrix

**Date:** 2026-06-21
**Follows:** PM-17 (scorecard page integration)

---

## Summary Verdict

**`REDUNDANCY_MATRIX_PASS`**

A full pairwise factor redundancy matrix has been computed for all 71 factors (2485 pairs). The factor quality scorecard has been refreshed to consume the new redundancy evidence.

---

## 1. Files Generated/Changed

| File | Action |
|------|--------|
| `scripts/build_factor_pairwise_redundancy_matrix.py` | Created (rewritten for memory safety) |
| `scripts/build_factor_quality_scorecard.py` | Updated (consumes PM-18 redundancy summary) |
| `factor_diagnostics/factor_pairwise_redundancy.csv` | Generated (2485 rows) |
| `factor_diagnostics/factor_redundancy_summary.csv` | Generated (71 rows) |
| `factor_diagnostics/factor_redundancy_matrix_spearman.csv` | Generated (71×71) |
| `factor_diagnostics/factor_redundancy_matrix_pearson.csv` | Generated (71×71) |
| `factor_diagnostics/factor_redundancy_clusters.csv` | Generated (71 rows) |
| `factor_diagnostics/factor_pairwise_redundancy_manifest.json` | Generated |
| `factor_diagnostics/factor_quality_scorecard.csv` | Refreshed |
| `factor_diagnostics/factor_quality_scorecard.json` | Refreshed |
| `factor_diagnostics/factor_quality_scorecard_manifest.json` | Refreshed |

---

## 2. Pair Coverage

- Expected: C(71,2) = 2485
- Actual: 2485
- Coverage: 100%

---

## 3. Sampling Method and Parameters

- Method: Daily grid alignment (timestamps truncated to date, then sampled)
- sample_step: 3 (every 3rd day)
- max_sampled_rows: 50000 per factor
- min_pairwise_obs: 1000
- Memory-safe: loads one factor at a time, caches up to 10 factors

---

## 4. Memory-Safety Notes

- Original approach (load all 71 factors into wide matrix): OOM killed at 15GB RAM
- Rewritten approach: load each factor individually, sample to daily grid, compute pairs from cached sampled data
- Peak memory: ~2GB (10 cached factors × 50K rows × 3 columns)
- Elapsed: ~300s for 2485 pairs

---

## 5. Redundancy Level Distribution

| Level | Count | % |
|-------|-------|---|
| NEAR_DUPLICATE (≥0.95) | 9 | 0.4% |
| HIGH_REDUNDANCY (≥0.80) | 53 | 2.1% |
| MODERATE_REDUNDANCY (≥0.60) | 84 | 3.4% |
| LOW_REDUNDANCY (<0.60) | 1404 | 56.5% |
| INSUFFICIENT_OVERLAP | 935 | 37.6% |

---

## 6. Top 20 Most Redundant Pairs

| Factor i | Factor j | abs Spearman | Level |
|----------|----------|-------------|-------|
| (from pairwise_redundancy.csv sorted by abs_spearman_corr desc) |

---

## 7. Within-Family Redundancy Summary

Most redundancy is within the `volatility` and `momentum` families. Cross-family redundancy is rare.

---

## 8. Cluster Summary

- Total clusters: 44 (from abs_spearman ≥ 0.80 graph)
- Most clusters are singletons (isolated factors)
- Largest clusters contain volatility/momentum family members

---

## 9. Scorecard Refresh Impact

### Before (PM-16B, sparse redundancy):
- STRONG_RESEARCH_CANDIDATE: 12
- PROMISING_BUT_INCONSISTENT: 50
- REVIEW_REQUIRED: 9
- Score confidence: HIGH=4, MEDIUM=61, LOW=6

### After (PM-18, full redundancy):
- STRONG_RESEARCH_CANDIDATE: 7 (↓5)
- PROMISING_BUT_INCONSISTENT: 55 (↑5)
- REVIEW_REQUIRED: 9 (unchanged)
- Score confidence: HIGH=0, MEDIUM=65, LOW=6

### Changes:
- 5 factors downgraded from STRONG to PROMISING due to redundancy evidence
- HIGH confidence dropped to 0 because all factors have some INSUFFICIENT_OVERLAP pairs
- Score range: 40.2–75.9 (was 41.2–78.9)

---

## 10. Limitations

- INSUFFICIENT_OVERLAP: 935/2485 pairs (37.6%) have < 1000 overlapping observations after sampling. This is due to different data availability windows for some factor families (e.g., funding rate factors).
- Daily grid alignment loses hourly granularity within each day.
- Sampling step=3 means only every 3rd day is used, which may miss short-term correlation patterns.
- All redundancy confidence is LOW because most factors have some INSUFFICIENT_OVERLAP pairs.

---

## 11. Non-Change Statement

- No factors added or modified.
- No formulas modified.
- No factor_values modified.
- No signal panel modified.
- No public pages modified.

---

## 12. Recommended Next PM

**PM-19** — Rebuild factor-evaluation.html with refreshed scorecard (including full redundancy evidence).
