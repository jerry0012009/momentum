# Public Alpha101 Cap Batch 12 Intake Audit - 2026-06-28

## Scope

Batch 12 resolved the remaining market-cap input blocker in the public WQ101
Alpha101 intake.

Implemented in the registry and factor library:

- `wq101_alpha56`

This is a single-factor batch by design. After Alpha101 batch 11, Alpha56 was
the only public Alpha101 candidate blocked only by the cap input contract; the
other remaining Alpha101 skips require an approved taxonomy/IndNeutralize
mapping or failed coverage suitability.

## Market-Cap Contract

The market-cap builder now augments the CoinGecko top-pages supply universe with
explicit manual override ids before symbol mapping. This fixed long-tail symbols
whose CoinGecko ids were known but whose supply rows were not present in the
default paged market list.

Commands run:

```bash
.venv/bin/python scripts/build_crypto_market_cap_1h.py --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
.venv/bin/python scripts/check_market_cap_data_contract.py
```

Contract result:

- Contract pass: true
- Overall coverage: 90.2%, pass against the 90.0% gate
- Symbol coverage summary: 237 symbols >= 90%, 29 symbols < 80%
- Public cap readiness: ready for cap unskip

The generated market-cap artifacts remain local data/cache products and are not
part of the versioned factor-library source bundle.

## Formula Decision

Alpha56 was implemented with the cap-based public formula:

```text
-rank(sum(returns,10)/sum(sum(returns,2),3))*rank(returns*cap)
```

The implementation follows the cap variant used by the reviewed WorldQuant 101
formula sources and the DolphinDB reference shape. `returns` is computed as
`close / delay(close, 1) - 1`; `cap` is supplied from the point-in-time
market-cap panel.

## Build Results

Factor values:

- Factor: `wq101_alpha56`
- Rows: 2,989,340
- Coverage: 100.000%
- Required inputs: `close`, `cap`

## Workflow Results

Intake run:

- Run ID: `public_alpha101_cap_batch12_20260628`
- Factors: 1
- Status: complete
- Redundancy pairs reviewed during intake: 248
- Redundancy labels: 158 `LOW_REDUNDANCY`, 90 `INSUFFICIENT_DATA`
- Conclusion card: `CONDITIONAL_DIRECTION_REVIEW`

Post-intake workflow:

- Quality scorecard rebuilt
- Factor evaluation page rebuilt
- Bilingual factor cards regenerated
- Page completeness QA: 112 PASS, 0 FAIL
- Post-intake integrity QA for `wq101_alpha56`: 23 PASS, 0 FAIL, 1 WARN

## Counts After Intake

- Registered factors: 249
- Computed factor values: 249
- Missing factor values: 0
- Alpha101 manifest rows: 107
- Alpha101 accounted non-skipped rows: 88
- Alpha101 skipped rows: 19
- Alpha158 manifest rows: 101
- Alpha158 accounted non-skipped rows: 95
- Alpha158 skipped rows: 6

Remaining public Alpha101 skips:

- 18 formulas require an approved taxonomy/IndNeutralize source.
- `wq101_alpha96_low_coverage_skipped` remains unsuitable because the dry-run
  produced only 62 finite rows on the current crypto panel.

## Final Verification

Commands run:

```bash
.venv/bin/python scripts/check_public_factor_integration_status.py
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/check_factor_evaluation_page_completeness.py
.venv/bin/python -m pytest tests/unit/test_build_crypto_market_cap_1h.py tests/unit/test_public_alpha101_cap_batch12.py tests/unit/test_public_factor_candidate_manifest.py tests/unit/test_public_factor_integration_status.py tests/unit/test_factor_library_start_here_entrypoint.py tests/unit/test_factor_library_state.py -q
```

Results:

- Public integration status: 249 registered, 249 computed, 0 missing
- Registry integrity: 249 checked, 0 critical issues
- Factor evaluation page completeness: 112 PASS, 0 FAIL
- Unit tests: 24 passed

## Production Boundary

This batch only extends the diagnostic public factor library. It does not mutate
live signals, ranking logic, paper trading lanes, execution code, or production
trading behavior.
