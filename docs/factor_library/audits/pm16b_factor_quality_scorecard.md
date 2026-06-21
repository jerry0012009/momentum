# PM-16B Factor Quality Scorecard

**Date:** 2026-06-21
**Follows:** PM-16A (factor evaluation sufficiency framework)

---

## Summary Verdict

**`FACTOR_SCORECARD_PASS_WITH_LIMITATIONS`**

A deterministic, rule-based factor quality scorecard has been built for all 71 factors. The scorecard synthesizes 7 evidence dimensions into transparent sub-scores and a final review class. Major limitation: redundancy confidence is LOW for 67/71 factors due to sparse pairwise coverage (6/2485 pairs).

---

## 1. Files Generated

| File | Size | Rows |
|------|------|------|
| `scripts/build_factor_quality_scorecard.py` | 31KB | ~570 lines |
| `factor_diagnostics/factor_quality_scorecard.csv` | 55KB | 71 |
| `factor_diagnostics/factor_quality_scorecard.json` | 118KB | 71 |
| `factor_diagnostics/factor_quality_scorecard_manifest.json` | 2.9KB | — |

---

## 2. Factor Count Coverage

- Registered: 71
- Scored: 71
- Missing: 0
- Join: 71/71

---

## 3. Final Quality Class Distribution

| Class | Count | Description |
|-------|-------|-------------|
| STRONG_RESEARCH_CANDIDATE | 12 | Strong ranking + usable portfolio extraction + stable + clear direction |
| PROMISING_BUT_INCONSISTENT | 50 | Meaningful evidence but mixed across dimensions |
| DIRECTION_DEPENDENT | 0 | (none assigned — direction ambiguity handled via DIRECTION_AMBIGUOUS → PROMISING) |
| REDUNDANT_OR_WEAK | 0 | (none assigned — redundancy data too sparse to classify) |
| INSUFFICIENT_EVIDENCE | 0 | (none assigned — all factors have computed values) |
| REVIEW_REQUIRED | 9 | Metadata/formula/direction flags need human review |

---

## 4. Score Confidence Distribution

| Confidence | Count | Criteria |
|------------|-------|----------|
| HIGH | 4 | COMPLETE metadata + non-LOW redundancy + coverage >= 0.95 |
| MEDIUM | 61 | COMPLETE metadata OR (coverage >= 0.95 + LOW redundancy) |
| LOW | 6 | NEEDS_REVIEW or FORMULA_AMBIGUOUS metadata |

---

## 5. Redundancy Confidence Distribution

| Confidence | Count |
|------------|-------|
| LOW | 67 | No explicit redundancy evidence |
| MEDIUM | 4 | Has redundancy evidence from 6 computed pairs |

---

## 6. Top 10 Factors by Score

| Rank | Factor | Score | Class | Confidence |
|------|--------|-------|-------|------------|
| 1 | rev_1h | 80.9 | STRONG_RESEARCH_CANDIDATE | HIGH |
| 2 | rev_3h | 75.4 | STRONG_RESEARCH_CANDIDATE | MEDIUM |
| 3 | vol_5h | 75.0 | STRONG_RESEARCH_CANDIDATE | MEDIUM |
| 4 | mom_20h | 74.5 | PROMISING_BUT_INCONSISTENT | MEDIUM |
| 5 | reversal_5h | 74.5 | STRONG_RESEARCH_CANDIDATE | MEDIUM |
| 6 | downside_vol_20h | 73.1 | STRONG_RESEARCH_CANDIDATE | MEDIUM |
| 7 | q158_high_low_range | 72.4 | PROMISING_BUT_INCONSISTENT | MEDIUM |
| 8 | range_1h | 72.4 | PROMISING_BUT_INCONSISTENT | MEDIUM |
| 9 | vol_of_vol_20h | 72.3 | STRONG_RESEARCH_CANDIDATE | MEDIUM |
| 10 | range_4h | 72.2 | PROMISING_BUT_INCONSISTENT | MEDIUM |

---

## 7. Examples by Quality Class

### STRONG_RESEARCH_CANDIDATE (12 factors)
- `rev_1h` (80.9): Strong RankIC, good Sharpe, clear direction, stable
- `vol_5h` (75.0): Strong volatility signal, good portfolio extraction
- `downside_vol_20h` (73.1): Active in signal, strong evidence

### PROMISING_BUT_INCONSISTENT (50 factors)
- `mom_20h` (74.5): Strong momentum but direction can be conditional
- `range_4h` (72.2): Good ranking but portfolio extraction mixed
- Most factors fall here — meaningful evidence but not decisive

### REVIEW_REQUIRED (9 factors)
- 6 NEEDS_REVIEW: taker/funding factors (diagnostic-only, not standalone signals)
- 3 FORMULA_AMBIGUOUS: WQ101 factors (direction unknown without running full WQ formula)

---

## 8. RankIC vs Sharpe: Separate Dimensions

The scorecard treats RankIC and Sharpe as **separate evidence dimensions**:

| Dimension | Measures | Score Range |
|-----------|----------|-------------|
| predictive_ranking_score | Cross-sectional ranking ability (RankIC, ICIR, t-stat) | 0-100 |
| portfolio_extraction_score | Portfolio extraction quality (Sharpe, return, drawdown) | 0-100 |

A factor can score high on one and low on the other. This is NOT a contradiction — it reflects different evidence strengths. The final_quality_class considers both independently.

---

## 9. Limitations

### 9.1 Redundancy Matrix Sparse (CRITICAL)
Only 6/2485 pairs computed (0.2% coverage). 67/71 factors have LOW redundancy confidence. The novelty/redundancy score is the weakest dimension. PM-18 should expand to full pairwise matrix.

### 9.2 Quantile Shape Analysis Simplified
Quantile monotonicity is computed from aggregate quantile returns (not period-level). A more robust analysis would use period-level stability of monotonicity.

### 9.3 No Out-of-Sample Validation
All scores are based on the full 25-month sample. No train/test split or walk-forward validation.

### 9.4 Score Confidence Mostly MEDIUM
61/71 factors have MEDIUM confidence, primarily because redundancy confidence is LOW. As redundancy coverage improves, confidence should increase.

---

## 10. Non-Change Statement

- No factors added or modified.
- No formulas modified.
- No factor_values modified.
- No signal panel modified.
- No public pages modified.
- No other scripts modified.

---

## 11. Recommended Next PM

**PM-17** — Integrate scorecard into existing factor-evaluation.html page to display quality classes and sub-scores.
