# Phase 7L — PM Review

> Date: 2026-06-15
>
> Status: LOCAL DATA PASS; REPRODUCIBILITY NEEDS FIX

---

## A. Review Conclusion

Phase 7L appears to have successfully constructed local taker/funding canonical caches and generated summary reports.

However, Phase 7M factor implementation is not yet approved because the large parquet caches are local-only and the commit does not include a reproducible cache-construction script or manifest.

Therefore the next step is not factor implementation. The next step is Phase 7L-R: reproducibility hardening for canonical crypto-native caches.

---

## B. What Passed

Based on the committed summaries:

- Static taker enriched bars row count matches source bars.
- Dynamic taker enriched bars row count matches source bars.
- `taker_buy_quote_volume` exists in enriched local caches.
- Funding events cache contains 2,098,808 events across 679 symbols.
- Funding aligned static rows match static bars.
- Funding aligned dynamic rows match dynamic bars.
- Funding max age is capped at 8h in the summary.
- No factor implementation, factor_values build, evaluation, backtest, alpha promotion, or status upgrade was reported.

---

## C. Blocking Issue

The following local parquet files are not committed to GitHub, which is expected given size limits:

- `data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1_taker_enriched/bars_1h.parquet`
- `data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_events.parquet`
- `data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_static.parquet`
- `data/cache/crypto_funding_rate_1h_contract_v1/funding_rate_1h_aligned_dynamic.parquet`

But the repository currently lacks a committed script that can recreate these caches from raw/local source data.

Without a reproducible construction script and cache manifest, future Phase 7M factor implementation would depend on undocumented local state.

---

## D. PM Decision

Do not start Phase 7M factor implementation yet.

Start Phase 7L-R instead:

```text
Phase 7L-R — Canonical Crypto-native Cache Reproducibility Hardening
```

Allowed Phase 7L-R scope:

- add a reproducible cache-construction script;
- add a cache manifest with paths, file sizes, row counts, schema, and checksums if feasible;
- add validation tests for the construction script outputs;
- update docs to explain local-only parquet artifacts.

Disallowed:

- no factor implementation;
- no factor_values build;
- no evaluation;
- no backtest;
- no alpha promotion;
- no CANDIDATE_REVIEW upgrade.

---

## E. Phase 7M Readiness

Phase 7M implementation is blocked until Phase 7L-R reproducibility hardening is complete.
