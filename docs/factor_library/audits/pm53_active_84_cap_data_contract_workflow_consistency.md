# PM-53: Active Factor Library 84 / Cap Data Contract / Workflow Consistency Audit

**Date**: 2026-06-24T12:00 UTC+8
**Scope**: Active 84-factor library, cap-based Alpha101 factors, market cap data contract, workflow completeness
**Not in scope**: No new factors, no formula changes, no direction changes, no signal construction, no trading advice

---

## I. Active Factor Count Consistency

| # | Source | Count | Status |
|---|--------|-------|--------|
| 1 | Registry (`factor_library_state.json`) | 84 | ✅ |
| 2 | Selected/active factor IDs | 84 | ✅ |
| 3 | `factor_values` computed (dirs) | 1 family | ⚠️ |
| 4 | `factor_diagnostics_summary.csv` | 84 | ✅ |
| 5 | `factor_level_rankic_summary.csv` | 84 | ✅ |
| 6 | `factor_level_long_short_summary.csv` | 84 | ✅ |
| 7 | `factor_quality_scorecard` | 84 | ✅ |
| 8 | `factor_redundancy_summary` | 84 | ✅ |
| 9 | `factor_regime_exposure_summary` | 84 | ✅ |
| 10 | `factor_quantile_shape_summary` (shape) | **80** | ❌ |
| 10b | `factor_rolling_stability_summary` | **80** | ❌ |
| 10c | `factor_decile_shape_summary` | **80** | ❌ |
| 11 | `factor_capacity_liquidity_summary` | **80** | ❌ |
| 12 | `factor_unified_profile_summary` | 84 | ✅ |
| 13 | `factor_bilingual_cards.csv` | 84 | ✅ |
| 14 | Public page (`factor-evaluation.html`) | 84 | ✅ |

**Missing from shape/decile/capacity (4 factors)**:
- `a101_volume_xs_z_mean_neg_112h`
- `a101_vol_xs_z_product_112h`
- `a101_volume_low_alpha_min_84_120`
- `a101_volume_high_alpha_min_84_84`

**Root cause**: Post-intake workflow for shape/decile/capacity was run with `--factor-ids` targeting only the 2 cap factors. The 4 non-cap a101 factors were not processed by these stages.

**Verdict**: ❌ FAIL — active count not consistent across all 14 sources.

---

## II. Alpha101 Factor Status Table

| factor_id | required_columns | uses_cap | scope | reg | rankic | ls | profile | card | shape | decile | cap | page | horizons | source_meta |
|-----------|-----------------|----------|-------|-----|--------|----|---------|------|-------|--------|-----|------|----------|-------------|
| a101_volume_xs_z_mean_neg_112h | volume | No | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | 1h/4h/24h/72h | ✅ |
| a101_vol_xs_z_product_112h | volume | No | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | 1h/4h/24h/72h | ✅ |
| a101_volume_low_alpha_min_84_120 | volume, low | No | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | 1h/4h/24h/72h | ✅ |
| a101_volume_high_alpha_min_84_84 | volume, high | No | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | 1h/4h/24h/72h | ✅ |
| a101_volume_cap_alpha_min_80_80 | volume, cap | Yes | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1h/4h/24h/72h | ✅ |
| a101_volume_cap_alpha_min_56_84 | volume, cap | Yes | panel | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 1h/4h/24h/72h | ✅ |

**Summary**: 6/6 registered, 6/6 in rankic/ls/profile/card/page. 4/6 missing from shape/decile/capacity. 6/6 have 4 horizons. 6/6 have source metadata.

**Verdict**: ❌ FAIL — 4 non-cap factors missing from shape/decile/capacity.

---

## III. Cap Data Contract Audit

### 3.1 `crypto_symbol_coingecko_overrides.csv`

| Check | Result | Status |
|-------|--------|--------|
| Total rows | 186 | ℹ️ |
| Unique symbols | 177 (9 duplicates) | ⚠️ |
| Duplicate details | 9 symbols appear twice (same coingecko_id, both RESOLVED) | Benign |
| map_status enum | RESOLVED: 174, CHECK: 11, `RESOLved`: 1 | ⚠️ |
| Case inconsistency | `CHRUSDT`: `RESOLved` → should be `RESOLVED` | ⚠️ |
| CHECK symbols | 11 (1000RATS, LOKA, COMBO, NFP, ASTER, COOKIE, ANIME, LUMIA, FORM, APEX, KMNO) | ℹ️ |
| CHECK in active parquet | 4: ANIMEUSDT, 1000RATSUSDT, COOKIEUSDT, ASTERUSDT | ⚠️ |
| 1000xxx handling | 7 symbols, 6 RESOLVED + 1 CHECK (1000RATS) | ✅ |

### 3.2 `market_cap_1h_aligned.parquet`

| Check | Result | Status |
|-------|--------|--------|
| Shape | 3,316,259 rows × 10 columns | ℹ️ |
| Unique symbols | 266 | ℹ️ |
| Date range | 2024-06-01 → 2026-06-13 | ℹ️ |
| (timestamp, symbol) uniqueness | 0 duplicates | ✅ |
| cap ≤ 0 | 0 | ✅ |
| cap null | 366,010 (11.0%) | ⚠️ |
| cap range | $2.57M → $1.04T | ℹ️ |
| cap_known_at exists | Yes | ✅ |
| cap_source_timestamp exists | Yes | ✅ |
| cap_known_at > timestamp | 0 (no future-known) | ✅ |
| cap_source columns | cap_source, cap_frequency, cap_fill_method, cap_quality_flag | ✅ |

### 3.3 Cap Definition

- **cap = circulating_supply × daily_close**
- cap is underlying coin USD market cap
- cap is NOT futures quote_volume proxy
- cap is NOT open interest
- cap is NOT tradeable capacity
- cap is a size/liquidity/cross-sectional structure proxy
- Forward-fill: daily close → 1h via last-known-value
- 1000xxx symbols: CoinGecko returns base supply (e.g., PEPE not 1000×PEPE), cap calculation uses that supply × price

### 3.4 Risk Assessment

**Verdict**: **CAP_POINT_IN_TIME_APPROXIMATE**

Rationale:
- cap_known_at ≤ timestamp holds (no future-known cap) ✅
- Forward-fill from daily close to 1h is an approximation
- 11% null caps (symbols without CoinGecko data)
- circulating_supply is a snapshot, not true point-in-time historical
- No explicit lookahead risk detected

---

## IV. Cap Factor Workflow Completeness

| Stage | a101_cap_80_80 | a101_cap_56_84 |
|-------|---------------|---------------|
| registry | ✅ PASS | ✅ PASS |
| factor_values | ✅ PASS | ✅ PASS |
| RankIC 1h/4h/24h/72h | ✅ PASS (4 horizons) | ✅ PASS (4 horizons) |
| LS 1h/4h/24h/72h | ✅ PASS | ✅ PASS |
| monthly IC | ✅ PASS (100 rows) | ✅ PASS (100 rows) |
| monthly LS | ✅ PASS (100 rows) | ✅ PASS (100 rows) |
| cumulative LS | ✅ PASS (100 rows) | ✅ PASS (100 rows) |
| paper diagnostics | ✅ PASS (in payload) | ✅ PASS (in payload) |
| fee sensitivity | ✅ PASS | ✅ PASS |
| regime/BTC | ✅ PASS (BEAR_DEPENDENT) | ✅ PASS (BEAR_DEPENDENT) |
| shape | ✅ PASS (WEAK_MONOTONIC) | ✅ PASS (WEAK_MONOTONIC) |
| decile | ✅ PASS (TOP_TAIL_DEPENDENT) | ✅ PASS (DECILE_MONOTONIC_WEAK) |
| capacity | ✅ PASS | ✅ PASS |
| redundancy | ✅ PASS (83 pairs) | ✅ PASS (83 pairs) |
| scorecard | ✅ PASS (score=64.8) | ✅ PASS (score=65.7) |
| profile | ✅ PASS | ✅ PASS |
| bilingual card | ✅ PASS | ✅ PASS |
| page | ✅ PASS | ✅ PASS |
| integrity QA | ✅ PASS (19/19) | ✅ PASS (19/19) |
| source metadata | ✅ PASS | ✅ PASS |
| ls_btc_corr | ✅ PASS (-0.197) | ✅ PASS (-0.206) |

**Verdict**: ✅ PASS — Both cap factors have complete workflow.

---

## V. Panel Computation Path Audit

| Check | Result | Status |
|-------|--------|--------|
| to_wide timestamp-symbol uniqueness | Maintained | ✅ |
| from_wide no duplicates | Verified | ✅ |
| xs_zscore per-timestamp cross-section | Correct | ✅ |
| xs_winsorize per-timestamp cross-section | Correct | ✅ |
| rolling_mean/min/product historical only | No future window | ✅ |
| ts_alpha_wide no lookahead | Verified | ✅ |
| ts_alpha_wide cap/volume index alignment | Column/index misalignment handled | ✅ |
| build_factor_values cap merge | Cap panel merge path exists | ✅ |
| Missing cap file handling | File-not-found check exists, fails hard | ✅ |
| --allow-blocked misuse risk | Flag exists; no silent skip of active factors | ✅ |
| Panel factors postprocess | Same as ordinary factors | ✅ |
| Panel factors in canonical outputs | Same output paths | ✅ |

**Verdict**: ✅ PASS

---

## VI. QA Requirement Checks

| # | Check | Result | Status |
|---|-------|--------|--------|
| 1 | Registry integrity | 84 checks | ✅ |
| 2 | Post-intake workflow integrity | 38/38 PASS (2 cap factors) | ✅ |
| 3 | Page completeness | 26/26 PASS, 0 FAIL | ✅ |
| 4 | Factor count consistency | shape/decile/capacity=80 | ❌ |
| 5 | Cap data contract checker | Exists and functional | ✅ |
| 6 | Alpha101 active workflow check | 4/6 missing shape/decile/capacity | ❌ |
| 7 | Public page HTTP check | 6.25MB, 84 factors, deployed | ✅ |

**Verdict**: ❌ FAIL — checks 4 and 6 failed.

---

## VII. Overall Verdict

```
PM53_ACTIVE_84_CAP_WORKFLOW_FAIL
```

**Reason**: Active factor count inconsistency — shape/decile/capacity stages contain 80 factors instead of 84.

### Required Fixes

1. **Run shape/decile/capacity for 4 non-cap a101 factors**:
   ```bash
   cd /root/clawd/jerry/momentum && PYTHONPATH=scripts .venv/bin/python \
     scripts/run_post_intake_workflow_completion.py \
     --factor-ids a101_volume_xs_z_mean_neg_112h,a101_vol_xs_z_product_112h,a101_volume_low_alpha_min_84_120,a101_volume_high_alpha_min_84_84 \
     --start-from shape-stability
   ```

2. **Fix `RESOLved` typo** in `config/crypto_symbol_coingecko_overrides.csv` (line for CHRUSDT)

3. **Deduplicate 9 symbols** in overrides CSV (benign but untidy)

4. **Resolve 4 CHECK symbols** in active parquet (ANIMEUSDT, 1000RATSUSDT, COOKIEUSDT, ASTERUSDT) or document as accepted

### Acceptance Status

| Component | Status |
|-----------|--------|
| Cap factors (2) as active | ✅ Accepted — complete workflow, PASS integrity |
| Non-cap a101 factors (4) as active | ⚠️ Partially accepted — rankic/ls/profile/page complete, shape/decile/capacity pending |
| Cap data source | ✅ Accepted as CAP_POINT_IN_TIME_APPROXIMATE |
| Panel computation path | ✅ Accepted — clean |
| Public page | ✅ Accepted — 84 factors visible |

### Recommended Next PM

**PM-53A**: Fix shape/decile/capacity for 4 non-cap a101 factors, then re-run PM-53 for PASS.
