# Phase 7K — Data Contract & Schema Verification Closeout

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7K: data contract / schema verification
- No factors implemented
- No build/eval/backtest

---

## B. Bars Schema Audit

| Dataset | Taker Fields | Status |
|---------|-------------|--------|
| static (50 symbols, 2025-12 → 2026-06) | ❌ Missing | PARTIAL |
| dynamic (266 symbols, 2024-06 → 2026-06) | ❌ Missing | PARTIAL |

Both datasets have: timestamp, OHLCV, quote_volume, trade_count, metadata.
Both datasets lack: taker_buy_volume, taker_buy_quote_volume.

Raw klines (zip) DO have taker_buy_volume and taker_buy_quote_volume.

---

## C. Taker Readiness

| Candidate Factor | Status |
|-----------------|--------|
| taker_buy_ratio_20h | READY_WITH_QUOTE_VOLUME_VARIANT |
| taker_buy_zscore_20h | READY_WITH_QUOTE_VOLUME_VARIANT |
| taker_buy_delta_5h | READY_WITH_QUOTE_VOLUME_VARIANT |

Recommended formula: `taker_buy_quote_volume / quote_volume`

**PM decision needed**: Accept quote-volume variant?

---

## D. Funding Readiness

| Data Source | Symbols | Top50 Coverage | Status |
|-------------|---------|----------------|--------|
| binance_funding_rate | 536 | 37/50 | READY_FOR_CONTRACT |
| binance_vision_rank154 | 679 | 49/50 | READY_FOR_CONTRACT |

**Recommended**: Use binance_vision path (better coverage).

Schema: calc_time (ms), funding_interval_hours, last_funding_rate.
Interval: fixed 8h (±2ms jitter).
Coverage: 2021-05 → 2026-04.

**PM decisions needed**:
1. Forward-fill max duration (suggest 8h)?
2. Funding interval change handling?
3. Symbol mapping rules?
4. Missing symbol handling (NaN)?

---

## E. PM 待决问题

1. **Taker formula**: 是否接受 `taker_buy_quote_volume / quote_volume` 作为 taker buy ratio？
2. **Funding forward-fill**: 是否允许 forward-fill 到 1h？最大时长 8h？
3. **Funding interval**: 如果未来 interval 变化（8h→4h→1h），如何处理？
4. **Funding symbol coverage**: 1000PEPEUSDT 缺失是否可接受？
5. **Schema modification**: 是否需要修改 bars_1h.parquet 以包含 taker 字段？

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

Phase 7L limited crypto-native factor implementation is allowed pending PM review.

Specifically:
- Taker imbalance factors: can implement if PM accepts quote-volume variant
- Funding rate factors: blocked until data contract finalized and ingestion pipeline built
