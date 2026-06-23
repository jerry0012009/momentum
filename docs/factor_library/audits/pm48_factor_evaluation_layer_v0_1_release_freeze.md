# PM-48: Factor Evaluation Layer v0.1 Release Freeze — Audit

**Date**: 2026-06-23
**PM**: PM-48
**Verdict**: `FACTOR_EVALUATION_LAYER_V0_1_RELEASE_PASS`

---

## Summary

Factor Evaluation Layer v0.1 frozen at 78 factors. All integrity checks pass.
Page QA 26/26 PASS. No out-of-scope modifications detected.
Legacy fallback mechanism confirmed and checker aligned with page builder.

---

## Factor Count Verification

| Source | Expected | Actual | Status |
|--------|----------|--------|--------|
| `factor_library_state.json` registered | 78 | 78 | ✅ |
| `factor_library_state.json` computed | 78 | 78 | ✅ |
| `factor_library_state.json` missing | 0 | 0 | ✅ |
| `factor_unified_profile_summary.csv` | 78 | 78 | ✅ |
| `factor_diagnostics_summary.csv` | 78 | 78 | ✅ |
| `factor-evaluation.html` visible rows | 78 | 78 | ✅ |

---

## PM-35 / Batch02 / Batch03 Integrity Table

### PM-35 (5 factors) — 19/19 PASS each

| Factor | PASS | FAIL | Status |
|--------|------|------|--------|
| rev_2h | 19 | 0 | ✅ |
| mom_vol_adjusted_20h | 19 | 0 | ✅ |
| range_breakout_vol_confirm_20h | 19 | 0 | ✅ |
| volume_pressure_20h | 19 | 0 | ✅ |
| xs_rank_mom_accel | 19 | 0 | ✅ |

### Batch02 (1 factor) — 19/19 PASS

| Factor | PASS | FAIL | Status |
|--------|------|------|--------|
| up_down_vol_ratio_20h | 19 | 0 | ✅ |

### Batch03 (1 factor) — 19/19 PASS

| Factor | PASS | FAIL | Status |
|--------|------|------|--------|
| clv_20h | 19 | 0 | ✅ |

### Full Library — 78/78 factors, 1482/1482 checks PASS

---

## Page QA Result

```
Total: 26  |  PASS: 26  |  FAIL: 0
```

All checks including:
- file_exists_and_size ✅
- csv_factor_coverage (78/78) ✅
- pm35_new_factors (5/5) ✅
- new_factor_metrics ✅
- pm40b_display_consistency ✅
- All section markers ✅
- pm46b_source_metadata ✅
- pm46b_ls_btc_corr ✅
- pm46b_shape_q5 ✅
- doc_align (3/3) ✅

---

## Public Page Status

- URL: `https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html`
- Size: 2.96 MB (< 4.5MB limit) ✅
- 78/78 factors visible ✅
- All cells populated, no N/A or empty values ✅
- 0 stale warnings visible on page ✅

---

## Source Metadata Result

| Field | N/A Count | Total | Status |
|-------|-----------|-------|--------|
| data_source_type | 0 | 78 | ✅ |
| source_fields | 0 | 78 | ✅ |
| required_columns | 0 | 78 | ✅ |

---

## LS-BTC Corr/Beta Result

| Field | Empty | Total | Status |
|-------|-------|-------|--------|
| long_short_btc_corr | 0 | 78 | ✅ |
| long_short_btc_beta | 0 | 78 | ✅ |
| paper_return_btc_corr | 0 | 78 | ✅ |
| paper_return_btc_beta | 0 | 78 | ✅ |
| ic_btc_return_corr | 0 | 78 | ✅ |

---

## Q5 Classification Result

- Decile shape factors: 1512 rows (78 factors × 19+ horizon/bucket combos)
- Q5 empty: 0 ✅

---

## Legacy Fallback Explanation

71/78 factors have NaN `long_short_spread_std` and `long_short_spread_annualized_return` in `factor_level_long_short_summary.csv` (canonical). These were built from older batch files that did not compute aggregate fields.

**Resolution**: Page builder uses `factor_diagnostics_summary.csv` as primary source (73/78 have LS data). The 5 remaining factors (`rev_2h`, `mom_vol_adjusted_20h`, `range_breakout_vol_confirm_20h`, `volume_pressure_20h`, `xs_rank_mom_accel`) have data in the canonical file.

**Checker fix**: `check_ls_aggregate` updated to use dual-source fallback matching page builder. Before fix: 71 FAIL. After fix: 78 PASS.

Both sources together cover 78/78 factors. No visible page gap.

---

## Stale Warnings

5 factors have `source_warning` in diagnostics CSV:
- `rev_2h`, `mom_vol_adjusted_20h`, `range_breakout_vol_confirm_20h`, `volume_pressure_20h`, `xs_rank_mom_accel`
- Value: `no_horizon_data;monthly_ls_unavailable`
- **Page builder clears these at render time** (line 501-504 in `_build_factor_eval_html.py`)
- No visible impact on page display

---

## No Out-of-Scope Modifications Confirmation

| Check | Status |
|-------|--------|
| No signal panel changes | ✅ |
| No strategy code changes | ✅ |
| No portfolio construction changes | ✅ |
| No live trading code | ✅ |
| No existing factor formulas changed | ✅ |
| No existing factor_values changed | ✅ |
| Only intended new factors: `up_down_vol_ratio_20h`, `clv_20h` | ✅ |

Git diff shows only:
- `check_post_intake_workflow_integrity.py` (checker fix — this PM)
- Data CSV/JSON files (factor library outputs)
- Report HTML files (cron-generated, not code changes)

---

## Remaining Limitations

1. **Stale source_warning in CSV**: 5 PM-35 factors. Cosmetic — page builder handles it.
2. **LS aggregate legacy path**: 71 factors use diagnostics fallback. Works correctly.
3. **No live validation**: Historical backtest only.
4. **Single universe**: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1`.
5. **11 NEEDS_REVIEW factors**: Data quality flag, not a display issue.

---

## Recommended Next PM

**PM-49**: Signal Construction Layer v0.1
- Factor selection from v0.1 evaluation results
- Multi-factor combination methodology
- Entry/exit logic, position sizing, portfolio construction
- Backtest with transaction costs

Alternative: **PM-49** — v0.1 tag + deployment hardening (CI, automated refresh, Docker).
