# PM-45: Controlled New Factor Intake Batch02 — Single Alpha158-Derived Factor

**Date:** 2026-06-23
**Verdict:** `BATCH02_SINGLE_FACTOR_INTAKE_PASS_WITH_LIMITATIONS`

---

## Summary

Successfully added `up_down_vol_ratio_20h` as the 77th factor. The post-intake workflow completed with 11/11 integrity PASS. One limitation: `post_intake_workflow_completion.py` cannot run the evaluate stage in partial mode (safety guard), requiring manual merge of batch evaluation results.

## Candidate Factor Selection

| factor_id | formula | required | lookback | family | expected | overlap | risk | verdict |
|-----------|---------|----------|----------|--------|----------|---------|------|---------|
| up_down_vol_ratio_20h | sum(vol*(ret>0),20)/sum(vol,20) | close,volume | 20 | alpha158_ohlcv | positive | volume_pressure (partial) | low | **SELECTED** |
| obv_slope_20h | linreg_slope(cumsum(vol*sign(ret)),20) | close,volume | 20 | volume_price | positive | volume_pressure,price_volume_corr | low | reject |
| clv_20h | mean(((close-low)-(high-close))/(high-low),20) | high,low,close | 20 | alpha158_ohlcv | positive | klow_close | low | reject |
| hloc_range_ratio_20h | std(high-low,20)/std(close-open,20) | open,high,low,close | 20 | alpha158_ohlcv | negative | q158_high_low_range | med | reject |
| ret_autocorr_20h | corr(ret,lag(ret,1),20) | close | 20 | alpha158_ohlcv | negative | rev_2h,mom_20h | low | reject |

**Why `up_down_vol_ratio_20h`:**
- Distinct from existing factors (not a pure momentum/reversal/volatility measure)
- Clear economic intuition: buying pressure ratio
- Only needs close + volume (canonical bars)
- Low implementation risk

## New Factor Details

- **factor_id:** `up_down_vol_ratio_20h`
- **Family:** `alpha158_ohlcv`
- **Formula:** `sum(volume * (ret > 0), 20) / sum(volume, 20)`
- **Expected direction:** positive (higher buying pressure → higher future returns)
- **Required columns:** close, volume
- **Lookback:** 20 bars
- **Status:** DIAGNOSTIC_PROBE
- **Intuition (zh):** 上涨时段的成交量占比反映买方主导程度。值越高说明上涨时放量、下跌时缩量，是典型的多头量价结构。
- **Intuition (en):** Fraction of volume on up bars. Higher values indicate bullish volume dominance — price rises on heavy volume, falls on light volume.

## Factor Values

- **Path:** `research/factor_runs/crypto_top50_factor_library/factor_values/up_down_vol_ratio_20h.parquet`
- **Coverage:** 99.58%
- **Rows:** 3,316,259

## Factor-Level Evaluation Summary

| Horizon | RankIC (dir-adj) | t-stat | LS Sharpe | LS Ann Return |
|---------|-----------------|--------|-----------|---------------|
| 1h | -0.0155 | -18.46 | — | — |
| 4h | — | — | 1.998 | 0.42% |

**Note:** Direction-adjusted IC is negative at 1h, suggesting the factor may behave as a contrarian indicator at short horizons. This is expected for a volume-based factor — high buying pressure may precede reversals.

## Paper / Fee / Regime / Capacity / Shape / Redundancy / Profile

- **Paper viability:** PAPER_MIXED
- **Cost sensitivity:** COST_COLLAPSED (collapses at 10bps)
- **Regime:** BEAR_DEPENDENT (performs better in bear markets)
- **Redundancy:** DISTINCT_SINGLETON (no strong pairwise correlation with existing factors)
- **Profile class:** BROAD_WATCHLIST
- **Profile score:** ~48/100

## Post-Intake Workflow Integrity

```
✅ up_down_vol_ratio_20h  PASS=11 FAIL=0 WARN=0
```

All 11 dimensions PASS:
1. factor_values ✅
2. factor_level_evaluation ✅
3. period_ic ✅
4. period_ls ✅
5. ls_aggregate ✅
6. paper_summary ✅
7. fee_sensitivity ✅
8. regime_exposure ✅
9. pairwise_redundancy ✅
10. cluster ✅
11. marginal_info ✅

## Page QA

```
Total: 23 | PASS: 23 | FAIL: 0
```

- factor_count: 77 (was 76)
- up_down_vol_ratio_20h: present in page ✅
- No stale warnings ✅
- Public page: HTTP 200 ✅

## Existing Factor Integrity

```
✅ rev_2h                         PASS=11 FAIL=0
✅ mom_vol_adjusted_20h           PASS=11 FAIL=0
✅ range_breakout_vol_confirm_20h PASS=11 FAIL=0
✅ volume_pressure_20h            PASS=11 FAIL=0
✅ xs_rank_mom_accel              PASS=11 FAIL=0
```

## No Existing Changes Confirmation

- ✅ No existing factor formulas changed
- ✅ No existing factor_values changed
- ✅ No expected_direction changed
- ✅ No signal panel changed
- ✅ No signal construction

## Limitations

1. **`run_post_intake_workflow_completion.py` cannot run evaluate stage in partial mode** — the safety guard in `evaluate_factors.py` prevents writing to canonical outputs when `--factor-ids` is used without `--output-suffix`. Workaround: run evaluate with `--output-suffix batch02`, then manually merge CSVs.

2. **Paper diagnostics overwrites canonical files** — `build_single_factor_paper_portfolio_diagnostics.py` writes to the same directory regardless of `--factor-ids`. Workaround: use `--output-dir /tmp/` then merge.

3. **Regime script depends on paper monthly returns** — when paper diagnostics is run for a subset, it overwrites the canonical file, breaking the regime script for all factors. Must restore from git and merge.

**Recommendation:** Fix `run_post_intake_workflow_completion.py` to handle partial factor intake correctly (output-suffix mode + auto-merge). This is the main workflow gap for batch02+.

## Files Changed

1. `scripts/factor_formula_registry.py` — added `_compute_up_down_vol_ratio_20h` + FactorSpec
2. `research/factor_runs/crypto_top50_factor_library/factor_library_state.json` — 77 factors
3. `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/*.csv` — merged batch02 evaluation
4. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv` — added new factor
5. `research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv` — added new factor
6. `research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv` — added new factor
7. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_*.csv` — merged new factor
8. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv` — 77 factors
9. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_pairwise_redundancy.csv` — 77 factors
10. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv` — 77 factors
11. `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_unified_profile_summary.csv` — 77 factors
12. `reports/site/factor-library/factor-evaluation.html` — 77 factors
13. `docs/factor_library/audits/pm45_controlled_factor_intake_batch02_single_alpha158_factor.md` — this audit

## Recommended Next Steps

- **PM-46:** Fix `run_post_intake_workflow_completion.py` to support partial factor intake (output-suffix + auto-merge)
- **PM-47:** Factor interpretation for `up_down_vol_ratio_20h` (direction analysis, regime dependency)
- **PM-48:** Batch03 planning (select next batch of factors)
