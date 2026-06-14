# Phase 7L-R — Cache Reproducibility Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7L-R: cache reproducibility hardening
- Reproducible script + manifest + validation tests
- No factor implementation, no factor_values build, no evaluation/backtest

---

## B. Script

| Item | Value |
|------|-------|
| Path | `scripts/build_crypto_native_caches.py` |
| Modes | `all`, `taker`, `funding`, `validate` |
| Input (bars) | `data/cache/{dataset_id}/bars_1h.parquet` |
| Input (klines) | `data/binance_vision_1h_v1_6/klines/{SYMBOL}/` |
| Input (funding) | `data/binance_vision_rank154/data/futures/um/monthly/fundingRate/` |
| Output (taker) | `data/cache/{dataset_id}_taker_enriched/bars_1h.parquet` |
| Output (funding) | `data/cache/crypto_funding_rate_1h_contract_v1/` |

---

## C. Manifest

| Item | Value |
|------|-------|
| Path | `phase7l_r_crypto_native_cache_manifest.csv` |
| Artifacts | 5 |
| Local-only | taker_enriched_dynamic (168.4MB), funding_events (12.3MB), funding_aligned_dynamic (5.7MB) |
| Checksum policy | SHA-256 for files <100MB; `SKIPPED_LARGE_FILE` for >100MB |

---

## D. Validation

| Test | Result |
|------|--------|
| Script exists | ✅ |
| Manifest exists (5 artifacts) | ✅ |
| Large parquets marked NO_LOCAL_ARTIFACT | ✅ |
| Taker row_count_match | ✅ |
| Funding row_count_match | ✅ |
| Funding max_age ≤ 8h | ✅ |
| Registry unchanged (47 factors) | ✅ |
| factor_ops unchanged | ✅ |
| No factor_values built | ✅ |
| **Total** | **13/13 PASS** |

---

## E. Phase 7M Readiness

**Phase 7M limited crypto-native factor implementation is allowed pending PM review.**

Script, manifest, and validation tests all pass. Cache is reproducible from raw data.

---

## F. Negative Declarations

No new factors were implemented.
No factor registry was modified.
No factor_ops were modified.
No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was run.
No diagnostic classification was run.
No redundancy analysis was run.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
