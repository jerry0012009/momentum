# PM-34 Audit: Factor Expansion Backlog & Intake-Readiness Checklist

**Date:** 2026-06-22
**Prompt:** PM34_FACTOR_EXPANSION_BACKLOG_INTAKE_READINESS_PROMPT_20260622.md
**Script:** `scripts/build_factor_expansion_backlog.py`

---

## Executive Summary

Created a factor expansion backlog with **22 candidate factors** across **12 target families**, selecting **5 candidates for BATCH_01_CONTROLLED_INTAKE**. Built an intake-readiness checklist with **11/11 checks PASS**. No existing registry, ops, or pipeline files were modified.

---

## Deliverables

| File | Description |
|------|-------------|
| `scripts/build_factor_expansion_backlog.py` | Backlog generation script |
| `docs/factor_library/FACTOR_EXPANSION_BACKLOG.md` | Human-readable backlog summary |
| `factor_diagnostics/factor_expansion_backlog.csv` | Full candidate table (CSV) |
| `factor_diagnostics/factor_expansion_backlog.json` | Full candidate table (JSON) |
| `factor_diagnostics/factor_intake_readiness_checklist.csv` | Readiness checklist (CSV) |
| `factor_diagnostics/factor_intake_readiness_checklist.json` | Readiness checklist (JSON) |
| `factor_diagnostics/factor_expansion_backlog_manifest.json` | Generation manifest with metadata |

---

## Candidate Summary

**Total candidates:** 22
**Families covered:** 12

### Priority Distribution

| Priority | Count | Description |
|----------|-------|-------------|
| P1_CONTROLLED_BATCH | 5 | Implementable now, high diagnostic value, low redundancy |
| P2_BACKLOG | 16 | Good candidates, deferred for controlled intake sequencing |
| P5_DEFER | 1 | Excluded duplicate (realized_vol_regime_ratio_20_80 ≡ vol_ratio_20_80) |

### Family Distribution

- short_term_reversal: 2 candidates
- medium_term_momentum: 2 candidates
- range_breakout: 2 candidates
- volatility_adjusted_momentum: 1 candidate
- volume_pressure: 2 candidates
- liquidity_stress: 1 candidate
- funding_rate_structure: 2 candidates
- taker_flow_structure: 2 candidates
- intraday_candle_structure: 2 candidates
- realized_volatility_shape: 2 candidates
- cross_sectional_rank_acceleration: 2 candidates
- mean_reversion_after_extreme_move: 2 candidates

---

## BATCH_01_CONTROLLED_INTAKE — 5 Candidates

| # | Factor ID | Family | Direction | Redundancy Risk | Complexity | Rationale |
|---|-----------|--------|-----------|-----------------|------------|-----------|
| 1 | `rev_2h` | short_term_reversal | positive | LOW | LOW | Fills 1h-3h gap; tests reversal curve granularity |
| 2 | `mom_vol_adjusted_20h` | medium_term_momentum | positive | LOW | LOW | Risk-adjusted momentum; tests vol-normalization marginal info |
| 3 | `range_breakout_vol_confirm_20h` | range_breakout | positive | LOW | LOW | Volume-confirmed breakout; tests price×volume interaction |
| 4 | `volume_pressure_20h` | volume_pressure | positive | LOW | LOW | Directional volume; novel signal vs raw volume |
| 5 | `xs_rank_mom_accel` | cross_sectional_rank_acceleration | positive | LOW | MEDIUM | Cross-sectional rank of acceleration; tests second-order signal normalization |

**Selection criteria met:**
- ✅ Implementable with current data (no new data sources)
- ✅ Not exact duplicates of dominant clusters (cluster 4: 14 factors)
- ✅ Covers 5 distinct families
- ✅ Clear diagnostic value for each candidate
- ✅ Direction from domain logic, not post-hoc fitting

---

## Intake-Readiness Checklist

| Check ID | Status | What It Checks |
|----------|--------|----------------|
| registry_integrity_ready | **PASS** | Factor registry parseable, unique IDs, valid columns |
| factor_ops_reuse_ready | **PASS** | 14 primitive operators available in factor_ops.py |
| factor_values_build_ready | **PASS** | Factor values pipeline functional |
| intake_runner_ready | **PASS** | Incremental single-factor intake supported |
| full_refresh_runner_ready | **PASS** | Full pipeline stages execute in order |
| expensive_stage_guardrails_ready | **PASS** | --expensive-ok flag guards costly stages |
| profile_stage_ready | **PASS** | Unified profile produces quality scores |
| evidence_matrix_ready | **PASS** | Evidence matrix has IC, turnover, stability, regime data |
| staleness_monitor_ready | **PASS** | Staleness detection functional |
| page_ready_payload_ready | **PASS** | Paper page payload with NAV, drawdown, turnover |
| no_signal_mutation_guard_ready | **PASS** | Factor values computed independently |

**Result: 11/11 PASS, 0 WARN, 0 FAIL**

---

## Registry Integrity Confirmation

```bash
git diff -- scripts/factor_formula_registry.py scripts/factor_ops.py scripts/build_factor_values.py scripts/build_phase9b_signal_panel.py
# (empty — no changes)
```

No factors were registered, added, or modified. This PM produces a backlog only.

---

## Validation

| Test | Result |
|------|--------|
| `python -m py_compile scripts/build_factor_expansion_backlog.py` | ✅ PASS |
| `python scripts/build_factor_expansion_backlog.py` | ✅ PASS (22 candidates, 5 BATCH_01) |
| `python scripts/run_factor_library_refresh.py --stage profile --dry-run` | ✅ PASS |
| `python scripts/check_factor_library_staleness.py` | ✅ PASS (pre-existing state staleness warnings unrelated) |
| Candidate count > 0 | ✅ PASS |
| BATCH_01 count >= 3 | ✅ PASS (5) |
| No registry file changes | ✅ PASS (empty diff) |

---

## Limitations

1. **Backlog is advisory only** — no factors are registered or computed
2. **Redundancy risk assessments** are based on structural analysis of formulas and existing cluster membership, not actual pairwise correlation computation
3. **BLOCKED_BY_DATA factors** were not included since all 12 families can be implemented with existing data sources (OHLCV + funding_rate + taker_buy_quote_volume)
4. **Cross-sectional factors** (xs_rank_mom_accel) have MEDIUM complexity because they require cross-sectional ranking logic in build_factor_values.py
5. **Existing state staleness warnings** from check_factor_library_staleness.py are pre-existing and unrelated to this PM

---

## Recommended Next PM

**PM-35: Register BATCH_01 Factor Candidates**

1. Register the 5 BATCH_01 factors in `factor_formula_registry.py`
2. Run full refresh pipeline to compute and evaluate new factors
3. Review RankIC, turnover, stability, and regime diagnostics
4. Update evidence matrix and profile with new factor data
5. Decide on retention/removal based on marginal information contribution
