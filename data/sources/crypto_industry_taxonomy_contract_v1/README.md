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
python scripts/build_crypto_industry_taxonomy_review_priority.py \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
python scripts/build_crypto_industry_taxonomy_review_priority.py \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet \
  --fetch-coingecko-categories \
  --category-fetch-limit 5
# Fill target_sector/target_industry/target_subindustry/target_known_at/
# target_effective_from in the packet, then change reviewed target rows to OK.
python scripts/validate_crypto_industry_taxonomy_review_packet.py \
  --packet-csv research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_batch_001.csv \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
python scripts/apply_crypto_industry_taxonomy_review_packet.py \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --packet-csv research/factor_runs/crypto_top50_factor_library/factor_diagnostics/industry_taxonomy_review_batch_001.csv \
  --output-csv /tmp/symbol_taxonomy.reviewed.csv
python scripts/check_crypto_industry_taxonomy_review_source.py \
  --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv \
  --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
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
`build_factor_values.py`. A source CSV with only `REVIEW`/`BLOCKED` rows fails
the artifact contract and will not produce `symbol_taxonomy.parquet`.

The template file is intentionally not a valid taxonomy artifact because it has
no reviewed rows.

`build_crypto_industry_taxonomy_review_priority.py` writes
`industry_taxonomy_review_priority.csv` and
`industry_taxonomy_review_priority_status.json` under factor diagnostics, plus
`industry_taxonomy_review_batch_plan.csv` and the current
`industry_taxonomy_review_batch_001.csv` packet for manual review batching. It
is only a manual review queue based on observed `quote_volume`; it must not be
used to infer or fill taxonomy groups. The review queue may include CoinGecko mapping
evidence, optional cached CoinGecko category evidence, and the Alpha101
IndNeutralize factor IDs blocked by the taxonomy contract, but those fields are
context for reviewers, not approval. Category evidence fetches are optional and
rate-limited; only successful `OK` category rows are persisted. The priority
status also includes a preview of point-in-time bar coverage from manually
approved `quality_flag == OK` rows with all group fields filled. That preview is
not a substitute for the parquet artifact, contract check, or coverage gate. It
also reports whether review rows are `known_at` before the latest evaluated bar;
rows known after the evaluation window cannot cover that window under the
point-in-time join rule. Review batches are work planning only; they do not
approve taxonomy rows. Batch packet target columns are reviewer workspace only;
approved values still have to be copied into `symbol_taxonomy.csv` and pass the
source, artifact, contract, and coverage gates.
`apply_crypto_industry_taxonomy_review_packet.py` copies only explicit
`target_quality_flag == OK` rows from a reviewed packet and requires all target
group and timing fields for those rows. It does not infer groups or approve
CoinGecko evidence. Prefer writing to a temporary CSV first and running the
source checker before replacing the committed source workbook.
`validate_crypto_industry_taxonomy_review_packet.py` is the pre-apply gate for
reviewed packets. It fails by default when no rows are marked
`target_quality_flag == OK`; use `--allow-no-ok` only for structural checks of a
blank packet before manual review is complete.
