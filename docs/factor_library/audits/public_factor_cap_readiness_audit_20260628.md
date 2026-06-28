# Public Factor Cap Readiness Audit - 2026-06-28

## Scope

This audit updates the public Alpha101/Alpha158 integration blocker state for
market-cap dependent candidates.

The only current public Alpha101 cap-blocked candidate is:

- `wq101_alpha56_cap_skipped`

## Current Evidence

The market-cap artifact exists:

```text
data/cache/crypto_market_cap_1h_contract_v1/market_cap_1h_aligned.parquet
```

However, the contract gate does not pass:

```bash
.venv/bin/python scripts/check_market_cap_data_contract.py
```

Result:

- File exists: pass
- Required columns: pass
- UTC-aware timestamps: pass
- No duplicate keys: pass
- Positive-or-null cap values: pass
- No forward-looking cap source timestamps: pass
- Overall coverage: 89.0%, fail against the 90.0% gate
- Symbol coverage summary: 234 symbols >= 90%, 32 symbols < 80%

Therefore `wq101_alpha56_cap_skipped` remains skipped. The blocker is no longer
"artifact missing"; it is "artifact exists but market-cap contract coverage
fails".

## Status Reporting Change

`scripts/check_public_factor_integration_status.py` now reports a
`cap_readiness` section alongside `taxonomy_readiness`.

Current cap readiness:

- `artifact_exists`: true
- `contract_pass`: false
- `ready_for_cap_unskip`: false
- `blocker`: `cap_contract_failed`
- `overall_coverage`: `89.0% (FAIL)`
- `blocked_alpha101_factor_ids`: `wq101_alpha56_cap_skipped`

## Next Valid Step

Do not unskip Alpha56 until the market-cap contract passes. The practical next
step is to improve symbol mapping/source coverage for low-coverage symbols in
`data/cache/crypto_market_cap_1h_contract_v1/market_cap_quality_report.csv`,
then rerun the market-cap builder and contract check.

This remains diagnostic-only and does not affect signal, paper, execution, or
live trading code.
