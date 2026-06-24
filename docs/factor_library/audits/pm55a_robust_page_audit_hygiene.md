# PM-55A: Robust Significance Page Audit Hygiene Patch

**Date:** 2026-06-24
**Status:** Documentation / QA hygiene.
**Verdict:** PM55A_ROBUST_PAGE_AUDIT_HYGIENE_PASS

---

## 1. Summary

PM-55 commit `a0a6ed5` completed Robust Significance Page Integration. This PM patches two readability/consistency issues in PM-55 audit docs and page QA reports.

**This PM does NOT:**
- Add new factors
- Modify formulas / expected_direction / factor_values
- Modify cap data source / scorecard / best_horizon
- Enter signal construction
- Make trading recommendations

---

## 2. Files Changed

| File | Change |
|------|--------|
| `scripts/check_factor_evaluation_page_completeness.py` | Size check name: "4.5MB" → "7.0MB" (2 occurrences) |
| `docs/factor_library/audits/pm55_robust_significance_page_integration.md` | funding_rate_zscore_80h 24h row: "not checked" → actual values |
| `.../factor_evaluation_page_completeness_report.csv` | QA report refresh |
| `.../factor_evaluation_page_completeness_report.json` | QA report refresh |
| `docs/factor_library/audits/pm55a_robust_page_audit_hygiene.md` | This audit |

---

## 3. Size Check Fix

**Problem:** `MAX_SIZE_BYTES = 7.0 * 1024 * 1024` (7 MB threshold) but check_name strings still said "HTML file exists and size < 4.5MB". Current page is ~6.6 MB — passes the actual 7.0 MB threshold but check_name was misleading.

**Fix:** Both check_name occurrences updated from "4.5MB" to "7.0MB":
- FAIL path: `"HTML file size < 4.5MB"` → `"HTML file size < 7.0MB"`
- PASS path: `"HTML file exists and size < 4.5MB"` → `"HTML file exists and size < 7.0MB"`

**Verification:** QA report JSON now shows `"check_name": "HTML file exists and size < 7.0MB"` — consistent with `MAX_SIZE_BYTES = 7.0 MB`.

---

## 4. funding_rate_zscore_80h 24h Fix

**Problem:** PM-55 audit doc listed 24h row as `| 24h | — | — | (not checked) | — | HIGH_OVERLAP |`, contradicting the PM-55 claim of 84×4 coverage.

**Actual 24h data:**

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 24h | +16.11 | +2.55 | ROBUST_SIGNIFICANT_POSITIVE | ×6.3 | HIGH_OVERLAP |

24h is NOT naive-only significant (robust_t=2.55 > 2.0). It's not listed in the "top naive-only significant" examples because it IS robust significant at 24h. The "not checked" was an error.

**Fix:** Replaced with actual values. Note: funding_rate_zscore_80h is NAIVE_ONLY at 1h/4h/72h but ROBUST_SIG_POS at 24h.

---

## 5. Page QA Result

```
Total: 33  |  PASS: 33  |  FAIL: 0
Exit code: 0
```

Size check: `"check_name": "HTML file exists and size < 7.0MB"` ✓ consistent

---

## 6. Robust Payload Coverage

84/84 factors × 4/4 horizons = 336 entries (unchanged from PM-55)

---

## 7. No Unauthorized Changes

- No formula changes
- No factor_values changes
- No expected_direction changes
- No scorecard changes
- No best_horizon changes
- No signal construction
- No trading recommendation

---

## 8. Limitations

1. This is a doc-only patch — no functional changes
2. Future PMs should ensure check_name strings are derived from constants, not hardcoded

---

## 9. Recommended Next PM

- **PM-56**: Extend robust significance to LS returns and paper portfolio
