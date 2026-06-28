# Crypto Industry Taxonomy Source

This directory is the reviewed source intake for the optional taxonomy required
by Alpha101 `IndNeutralize(..., IndClass.*)` formulas.

Do not put inferred, temporary, or future-known classifications here. Each row
must be reviewed and must include the `known_at`, `effective_from`, and optional
`effective_to` timestamps needed for point-in-time factor computation.

Required workflow:

```bash
python scripts/init_crypto_industry_taxonomy_review.py \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --output-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --known-at 2026-06-28T00:00:00Z \
  --taxonomy-version reviewed_v1 \
  --source manual_review
# Fill sector/industry/subindustry, then change reviewed rows from REVIEW to OK.
python scripts/build_crypto_industry_taxonomy_artifact.py \
  --input-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --output data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
python scripts/check_crypto_industry_taxonomy_contract.py \
  --path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet
python scripts/check_crypto_industry_taxonomy_coverage.py \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --taxonomy-path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet \
  --min-full-coverage 0.98
```

Only `quality_flag == OK` rows are eligible for factor computation. `REVIEW` and
`BLOCKED` rows are retained for audit, but they are ignored by
`build_factor_values.py`.

The template file is intentionally not a valid taxonomy artifact because it has
no reviewed rows.
