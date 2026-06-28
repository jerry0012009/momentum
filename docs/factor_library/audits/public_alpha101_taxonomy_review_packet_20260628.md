# Public Alpha101 Taxonomy Review Packet - 2026-06-28

## Scope

This audit advances the remaining Alpha101 `IndNeutralize(..., IndClass.*)`
blocker without unskipping any factor.

No new factor was registered in this packet. The work only improves the
reviewable taxonomy data-source path required before the remaining
industry-neutralized Alpha101 formulas can enter the factor library.

## Current Blocker

- Alpha101 total manifest rows: 107
- Alpha101 implemented/accounted non-skipped rows: 88
- Alpha101 skipped rows: 19
- Taxonomy/IndNeutralize skipped rows: 18
- Other skipped row: `wq101_alpha96_low_coverage_skipped`

The 18 taxonomy-blocked formulas require one or more of:

- `sector`
- `industry`
- `subindustry`

The current source file remains review-only:

```text
data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv
```

It has 266 rows, all with `quality_flag=REVIEW`, and zero `OK` rows. Therefore
no taxonomy parquet artifact is valid yet and no IndNeutralize factor may be
unskipped.

## Review Packet Improvement

`scripts/build_crypto_industry_taxonomy_review_priority.py` now enriches the
manual review queue with:

- CoinGecko mapping evidence from the market-cap workflow when available;
- optional CoinGecko category evidence cached as review-only metadata;
- required taxonomy groups for the blocked Alpha101 formulas;
- the count and IDs of blocked Alpha101 factors affected by taxonomy approval;
- an explicit review-only note stating that groups must be manually filled
  before any row can become `OK`.

Generated packet:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_priority.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_priority_status.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_coingecko_category_evidence.csv
```

Current packet summary:

- Rows: 266
- Bar rows: 3,316,259
- Symbols needing review: 266
- Symbols with CoinGecko mapping evidence: 242
- Symbols with cached CoinGecko category evidence: 11
- Blocked Alpha101 IndNeutralize factors: 18
- Required groups: `industry|sector|subindustry`
- Top 20 symbols by quote volume cover 78.85% of observed quote volume
- Top 50 symbols by quote volume cover 86.98% of observed quote volume
- Top 20 symbols by quote volume cover 10.08% of bar rows
- Top 50 symbols by quote volume cover 24.98% of bar rows
- The 98% bar-row coverage gate is first reached at review rank 249 under the
  current quote-volume priority order

The coverage gate uses point-in-time full-group bar coverage and symbol
coverage, not quote volume. The quote-volume ranking is still useful for review
order, but it cannot be treated as the unlock threshold by itself.

CoinGecko category evidence has been cached for the first 11 symbols in the
current review-priority order. A conservative request cadence is required:
CoinGecko free-tier requests returned HTTP 429 during the attempt to fetch the
next symbols. The cache persists only successful `OK` category rows; rate-limit
errors are not retained as source evidence.

## Guardrails

This packet does not:

- infer `sector`, `industry`, or `subindustry`;
- treat CoinGecko categories as approved taxonomy groups;
- change any taxonomy row from `REVIEW` to `OK`;
- build `symbol_taxonomy.parquet`;
- register new factors;
- compute factor values;
- mutate signal, paper, execution, or live trading code.

## Verification

Commands run:

```bash
.venv/bin/python -m pytest tests/unit/test_build_crypto_industry_taxonomy_review_priority.py -q
.venv/bin/python -m py_compile scripts/build_crypto_industry_taxonomy_review_priority.py
.venv/bin/python scripts/build_crypto_industry_taxonomy_review_priority.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
.venv/bin/python scripts/build_crypto_industry_taxonomy_review_priority.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet --fetch-coingecko-categories --category-fetch-limit 5 --category-fetch-delay 6.5
.venv/bin/python scripts/build_crypto_industry_taxonomy_review_priority.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet --fetch-coingecko-categories --category-fetch-limit 15 --category-fetch-delay 6.5
```

Results:

- Review-priority unit tests: 9 passed
- Script compilation: pass
- Review packet regenerated with 266 rows, 18 blocked-factor context, and
  explicit 98% bar-row coverage threshold fields
- CoinGecko category evidence cached for 11 review-priority symbols

## Next Valid Step

Manually review the prioritized symbols, fill point-in-time
`sector`/`industry`/`subindustry` values, set approved rows to `OK`, then run:

```bash
.venv/bin/python scripts/check_crypto_industry_taxonomy_review_source.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv
.venv/bin/python scripts/build_crypto_industry_taxonomy_artifact.py --input-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --output data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
.venv/bin/python scripts/check_crypto_industry_taxonomy_contract.py --path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
.venv/bin/python scripts/check_crypto_industry_taxonomy_coverage.py --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet --taxonomy-path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet --min-full-coverage 0.98
```

Only after those gates pass should any `*_indneutralize_skipped` manifest row
move to an implemented batch.
