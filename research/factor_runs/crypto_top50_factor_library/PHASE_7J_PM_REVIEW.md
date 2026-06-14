# Phase 7J — PM Review

> Date: 2026-06-15
>
> Status: PM OVERRIDE APPLIED

---

## A. Review Conclusion

The server-generated Phase 7J planning output is accepted as a planning draft, but not accepted as implementation authorization.

Phase 7K must be a data-contract / schema-verification phase, not a factor implementation phase.

---

## B. What Passed

- Phase 7J remained planning-only.
- No new factors were implemented.
- No factor registry was modified.
- No factor_ops were modified.
- No factor_values were built.
- No evaluation, redundancy, backtest, alpha promotion, or status upgrade was run.
- The v0.3 factor library baseline was correctly recognized as 36 diagnostic factors.
- The main gap analysis correctly identified crypto-native families as under-covered.

---

## C. PM Concerns

### 1. Taker imbalance is not yet implementation-ready

The Phase 7J draft marked `taker_buy_sell_volume` as immediately usable. This is too optimistic.

Reason:

- Binance raw kline archives contain taker buy fields.
- Older event-study scripts can normalize some taker buy fields.
- However, Phase 7 factor_values are built from `data/cache/<dataset_id>/bars_1h.parquet` through `scripts/build_factor_values.py`.
- It has not yet been verified that the current factor-library bars cache contains `taker_buy_volume`, `taker_buy_base`, or `taker_buy_quote_volume` for both static and dynamic datasets.

Therefore taker imbalance candidates cannot enter implementation until a schema verification pass confirms the required columns exist in the actual factor-library datasets.

### 2. Funding rate exists but still needs data contract

Funding-rate raw archive appears to exist in a separate legacy/event-study path, but Phase 7 factor-library integration is not defined.

Before funding factors can be implemented, the project needs:

- canonical funding raw-data path;
- parquet/cache format;
- symbol mapping rule;
- known_at semantics;
- 8h/4h/variable interval to 1h alignment rule;
- join rule to OHLCV bars;
- coverage report for current static and dynamic universes.

### 3. WQ101 candidates are not automatically implementation-ready

`wq101_alpha01` uses `rank(...)` and VWAP-style semantics. Current Phase 7 factor factory supports only limited cross-sectional post-processing for explicitly known `xs_rank_*` factors. WQ-style cross-sectional rank semantics should not be inferred silently.

`wq101_alpha01` should be deferred until WQ rank/VWAP semantics are explicitly specified.

`wq101_alpha06` may be easier, but it should also wait until the Batch-3 data-contract/schema verification phase has completed.

---

## D. PM Override

Do not start Phase 7K implementation.

Phase 7K should be:

```text
Phase 7K — Crypto-native Data Contract & Schema Verification
```

Allowed Phase 7K scope:

- inspect actual `bars_1h.parquet` schemas for static and dynamic datasets;
- verify whether taker buy columns are available in the factor-library cache;
- verify funding raw archive presence and schema;
- design canonical funding integration contract;
- update Batch-3 candidate readiness after schema verification.

Disallowed in Phase 7K:

- no new factor implementation;
- no factor_values build;
- no evaluation;
- no backtest;
- no alpha promotion;
- no CANDIDATE_REVIEW upgrade.

---

## E. Corrected Next-Step Interpretation

The server draft says 5 candidates are `PROPOSE_FOR_PHASE7K`. Under PM review, this should be interpreted as:

- `taker_buy_ratio_20h`, `taker_buy_zscore_20h`, `taker_buy_delta_5h`: **schema verification required first**;
- `wq101_alpha01`: **defer until WQ rank/VWAP semantics are defined**;
- `wq101_alpha06`: **possible later, but not before Phase 7K schema/data-contract review**.

No candidate is approved for implementation yet.

---

## F. Required Negative Declarations

No new factors were implemented by this PM review.
No factor registry was modified by this PM review.
No factor_ops were modified by this PM review.
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

## G. Phase 7K Readiness

Phase 7K crypto-native data contract and schema verification is allowed pending PM review.
