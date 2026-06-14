# Phase 7K — Data Contract & Schema Verification Closeout

> Date: 2026-06-14
>
> Status: COMPLETE (PM correction applied)

---

## A. Scope

- Phase 7K: data contract / schema verification
- No factors implemented
- No build/eval/backtest

---

## B. Bars Schema Audit

| Dataset | Taker Fields | Status |
|---------|-------------|--------|
| static (50 symbols, 2025-12 → 2026-06) | Missing | PARTIAL |
| dynamic (266 symbols, 2024-06 → 2026-06) | Missing | PARTIAL |

Both datasets have: timestamp, OHLCV, quote_volume, trade_count, metadata.

Both datasets lack: taker_buy_volume, taker_buy_quote_volume.

Raw klines have taker_buy_volume and taker_buy_quote_volume, but the current Phase 7 factor-library bars cache does not include them.

---

## C. Taker Readiness

| Candidate Factor | Status |
|-----------------|--------|
| taker_buy_ratio_20h | NEEDS_SCHEMA_FIX |
| taker_buy_zscore_20h | NEEDS_SCHEMA_FIX |
| taker_buy_delta_5h | NEEDS_SCHEMA_FIX |

PM decision:

- Accept quote-volume taker imbalance as the preferred formula family.
- Preferred future formula: `taker_buy_quote_volume / quote_volume`.
- Do not implement taker factors until `taker_buy_quote_volume` is present in the canonical factor-library cache.

---

## D. Funding Readiness

| Data Source | Symbols | Top50 Coverage | Status |
|-------------|---------|----------------|--------|
| binance_funding_rate | 536 | 37/50 | READY_FOR_CONTRACT |
| binance_vision_rank154 | 679 | 49/50 | READY_FOR_CONTRACT |

Recommended: use binance_vision path because coverage is better.

Schema: calc_time (ms), funding_interval_hours, last_funding_rate.

Interval: fixed 8h in current audit sample.

Coverage: 2021-05 → 2026-04.

PM decisions:

1. Forward-fill to 1h is allowed only through backward merge_asof with max_age <= funding_interval_hours.
2. Default max_age = 8h for current data.
3. If interval changes in future, max_age must use each record's `funding_interval_hours`.
4. Missing symbols remain NaN; do not impute.
5. 1000PEPEUSDT missing is acceptable and should not block the funding data contract.

---

## E. Next Phase

Phase 7L should be data cache construction, not factor implementation.

Recommended Phase 7L:

```text
Phase 7L — Taker / Funding Canonical Data Cache Construction
```

Allowed Phase 7L scope:

- enrich static/dynamic bars cache with `taker_buy_quote_volume` if raw klines support it;
- build canonical funding-rate parquet/cache from local funding archives;
- generate coverage and schema reports;
- do not implement new factors.

---

## F. 负面声明

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

---

## G. Phase 7L Readiness

Phase 7L implementation is blocked pending data/schema fixes.

Phase 7L taker/funding canonical data cache construction is allowed pending PM review.
