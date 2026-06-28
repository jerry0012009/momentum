# Public Alpha101 Panel Batch 11 Intake Audit - 2026-06-28

## Scope

Batch 11 reviewed the remaining public WQ101 Alpha101 formulas that could be grouped by OHLCV, VWAP, and ADV-style rolling-volume inputs.

Implemented in the registry and factor library:

- `wq101_alpha73`
- `wq101_alpha81`
- `wq101_alpha84`
- `wq101_alpha98`

Reviewed but skipped:

- `wq101_alpha96_low_coverage_skipped`: dry-run produced only 62 finite rows out of 3,301,833 panel rows, so it was not suitable for factor-library intake.
- `wq101_alpha56_cap_skipped`: requires a point-in-time market-cap artifact that is not available in the current workspace.
- `wq101_alpha48`, `63`, `76`, `79`, `80`, `82`, `87`, `89`, `90`, `91`, `97`, `100`: require `IndNeutralize` with approved sector, industry, or subindustry taxonomy.

## Formula and Data Notes

The implemented factors use only current approved inputs:

- OHLCV bars
- VWAP derived from `quote_volume / volume`
- ADV proxies derived from rolling mean volume
- Cross-sectional ranks computed per timestamp
- Time-series rolling operators computed per symbol

Alpha96 was deliberately excluded after a dry-run coverage audit. Its nested rank/correlation/argmax branches had insufficient finite output under the current 1h crypto panel and would have created a misleading library entry.

## Counts After Intake

- Registered factors: 248
- Computed factor values: 248
- Missing factor values: 0
- Alpha101 manifest rows: 107
- Alpha101 accounted non-skipped rows: 87
- Alpha101 skipped rows: 20
- Alpha158 manifest rows: 101
- Alpha158 accounted non-skipped rows: 95
- Alpha158 skipped rows: 6

The Alpha101 public-number coverage is now accounted in the manifest: implementable formulas are registered, while formulas blocked by taxonomy, market-cap input, or unacceptable coverage are explicitly skipped with reasons.

## Workflow Results

Intake run:

- Run ID: `public_alpha101_panel_batch11_20260628`
- Factors: 4
- Status: complete
- Conclusion cards: 4 `CONDITIONAL_DIRECTION_REVIEW`

Post-intake workflow:

- 18 stages completed successfully
- Pairwise redundancy: 30,628 pairs covering 248 factors
- Factor evaluation page asset: 248 factors
- Page completeness QA: 112 PASS, 0 FAIL
- Post-intake integrity QA for batch factors: 92 PASS, 0 FAIL, 4 WARN

## Final Verification

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_public_alpha101_panel_batch11.py tests/unit/test_public_factor_candidate_manifest.py tests/unit/test_public_factor_integration_status.py tests/unit/test_factor_library_start_here_entrypoint.py tests/unit/test_factor_library_state.py -q
.venv/bin/python scripts/check_factor_registry_integrity.py
.venv/bin/python scripts/check_public_factor_integration_status.py
.venv/bin/python scripts/check_factor_evaluation_page_completeness.py
```

Results:

- Unit tests: 23 passed
- Registry integrity: 248 checked, 0 critical issues
- Public integration status: 248 registered, 248 computed, 0 missing
- Factor evaluation page completeness: 112 PASS, 0 FAIL

## Production Boundary

All four implemented factors remain diagnostic-only public formula transfers. This batch does not mutate live signals, ranking logic, paper trading lanes, or production trading behavior.
