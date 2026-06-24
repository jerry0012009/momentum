# PM-57: Return-side Robust Diagnostics Page Integration

**Date:** 2026-06-24
**Status:** Page integration.
**Verdict:** PM57_RETURN_SIDE_ROBUST_PAGE_INTEGRATION_PASS

---

## 1. Summary

PM-56 generated return-side robust diagnostics as standalone CSV/JSON files. PM-57 integrates these into `factor-evaluation.html` so users can directly read LS robust, paper robust, and fee cost-collapse diagnostics alongside existing RankIC robust diagnostics.

**This PM does NOT:**
- Add new factors
- Modify formulas / expected_direction / factor_values
- Modify scorecard / best_horizon
- Modify RankIC results
- Enter signal construction
- Make trading recommendations

---

## 2. Files Changed

| File | Change |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Load LS/paper/fee robust CSVs; add `return_robust` payload; add LS robust section rendering; add paper/fee badges; add CSS |
| `scripts/check_factor_evaluation_page_completeness.py` | Added 10 PM-57 QA checks; added `import re` |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt (6.88 MB) |
| `docs/factor_library/audits/pm57_return_side_robust_page_integration.md` | New audit |

---

## 3. Payload Coverage

Each factor payload now includes:

```json
"return_robust": {
  "ls": {"1h": {...}, "4h": {...}, "24h": {...}, "72h": {...}},
  "paper": {... or null},
  "fee": {... or null},
  "coverage": {
    "ls_robust": "FULL_UNIVERSE",
    "paper_robust": "DOCUMENTED_SUBSET" or "UNAVAILABLE",
    "fee_robust": "DOCUMENTED_SUBSET" or "UNAVAILABLE"
  }
}
```

| Component | Coverage | Count |
|-----------|----------|-------|
| LS robust | Full universe | 84/84 factors × 4 horizons |
| Paper robust | Documented subset | 5/84 factors |
| Fee cost-collapse | Documented subset | 13/84 factors |

---

## 4. UI Changes — Reading Flow

Page sections now read in this natural order:

1. **Redundancy analysis**
2. **Monthly RankIC** (chart)
3. **Monthly LS Return** (chart)
4. **Cumulative LS Curve** (chart)
5. **Drawdown Summary** (metrics)
6. **📊 LS Return Robust Diagnostics** ← NEW (PM-57)
   - Best-horizon metrics: LS mean, naive t, robust t, NW lag, bootstrap CI, sign consistency, inflation, overlap
   - All-horizon table: 4 horizons × 9 columns
   - How-to-read guide (bilingual)
7. **Paper Portfolio** ← Enhanced with paper robust + fee cost-collapse badges
   - Paper robust badge (RETURN_ROBUST_POSITIVE / NAIVE_ONLY / etc.)
   - Fee cost-status badge (RETURN_COST_COLLAPSED / COST_SURVIVED)
   - Paper robust metrics: robust t, bootstrap CI, sign %
   - Fee metrics: gross Sharpe, net Sharpe, Sharpe decay
8. **BTC/Market Regime**
9. **Capacity/Liquidity**

**Design principle:** LS robust is placed right after LS charts (where you just looked at LS returns) — the natural next question is "are these returns statistically robust?" Paper/fee badges are embedded in the Paper Portfolio section where they belong contextually.

---

## 5. Key Examples

### clv_20h
- RankIC robust: ROBUST_SIGNIFICANT_POSITIVE at all horizons
- LS robust: RETURN_NOT_SIGNIFICANT at best horizon (RankIC robust but weak LS return translation)
- Demonstrates that robust ranking relation does NOT guarantee robust return translation

### rev_2h
- LS robust: RETURN_ROBUST_NEGATIVE at 72h (robust_t = -3.09)
- Fee cost-collapse: RETURN_COST_COLLAPSED (gross Sharpe 1.22, net Sharpe -1.93, decay 3.14)
- Demonstrates robust negative LS return that collapses after fees

### funding_rate_zscore_80h
- LS robust: RETURN_NOT_SIGNIFICANT at 1h, RETURN_ROBUST_POSITIVE at 24h
- Paper robust: RETURN_ROBUST_POSITIVE (subset)
- Fee: COST_SURVIVED

### a101_volume_cap_alpha_min_80_80
- LS robust: RETURN_ROBUST_POSITIVE at 1h (robust_t = +2.96)
- Demonstrates cap factor with robust LS translation

### Cost-collapsed example: rev_2h
- Gross Sharpe: 1.22 → Net Sharpe: -1.93 (decay 3.14)
- cost-status-badge shows RETURN_COST_COLLAPSED (red)

---

## 6. CSS Classes Added

| Class | Purpose |
|-------|---------|
| `.ret-robust-badge` | Return-side robust classification badges |
| `.ret-robust-badge.RETURN_ROBUST_POSITIVE` | Green — robust positive |
| `.ret-robust-badge.RETURN_ROBUST_NEGATIVE` | Red — robust negative |
| `.ret-robust-badge.NAIVE_ONLY_RETURN_SIGNIFICANT` | Amber — possibly inflated |
| `.ret-robust-badge.RETURN_NOT_SIGNIFICANT` | Gray — not significant |
| `.ret-robust-badge.RETURN_COST_COLLAPSED` | Dark red — fee collapse |
| `.cost-status-badge` | Fee cost-collapse/survived badge |
| `.robust-table` | LS robust all-horizon table |

---

## 7. Page QA Result

```
Total: 43  |  PASS: 43  |  FAIL: 0
```

New PM-57 checks (10):
| Check | Status | Evidence |
|-------|--------|----------|
| pm57_return_robust_payload | PASS | 84/84 |
| pm57_ls_horizon_coverage | PASS | 84/84 × 4 horizons |
| pm57_ls_section | PASS | Section h3 found |
| pm57_ls_table | PASS | robust-table class found |
| pm57_paper_subset | PASS | 79 factors without paper robust |
| pm57_fee_subset | PASS | 71 factors without fee robust |
| pm57_rev2h_negative | PASS | class=RETURN_ROBUST_NEGATIVE |
| pm57_cost_collapsed | PASS | rev_2h |
| pm57_factor_count | PASS | 84 |
| pm57_cost_badge_css | PASS | Found |

---

## 8. Active Workflow Consistency Result

```
Tables checked: 15
PASS: 15  |  FAIL: 0
Verdict: PASS
```

---

## 9. No Unauthorized Changes

- No new factors ✓
- No formula changes ✓
- No expected_direction changes ✓
- No factor_values changes ✓
- No scorecard changes ✓
- No best_horizon changes ✓
- No RankIC result changes ✓
- No LS original result changes ✓
- No signal construction ✓
- No trading recommendations ✓

---

## 10. Limitations

1. Paper robust covers only 5/84 factors (documented subset)
2. Fee cost-collapse covers only 13/84 factors (documented subset)
3. LS robust table only shows when all 4 horizons available (always true for current data)
4. Return-side section uses best_horizon only for the summary metrics; all-horizon table shows all 4

---

## 11. Recommended Next PM

- **PM-58**: Expand paper portfolio diagnostics to all 84 factors
- **PM-59**: Add robust diagnostics trend tracking (track robust class changes over time)
