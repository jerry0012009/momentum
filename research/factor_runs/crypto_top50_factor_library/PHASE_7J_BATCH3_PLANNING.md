# Phase 7J — Batch-3 Planning & Crypto-native Data Readiness Review

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7J
- Planning only — no implementation/build/eval/backtest
- v0.3 curated library (36 factors) as baseline
- Crypto-native data readiness audit

---

## B. v0.3 Library Status

- Total factors: 36 (Batch-1: 27, Batch-2: 9)
- Families: 13
- TIER_1: 11, TIER_2: 15, TIER_3: 3, TIER_4: 7
- Redundancy groups: 8

### Main Redundancy Concentrations

1. **technical_indicators**: 4 factors, 2 HIGH_REDUNDANCY groups (ema_12_26_gap↔rsi_28h, rsi_7h↔williams_r_14h). OVER_REDUNDANT.
2. **quote_volume_liquidity**: 3 factors all TIER_4. Structural sign-flip issue.
3. **volume_liquidity**: 2 factors both TIER_4. Same structural issue.
4. **trend_ma**: 3 factors, 2 TIER_4. ma_gap sign-flip.

### Under-covered Areas

All 7 crypto-native families are NOT_COVERED:
- funding_rate, open_interest, basis_premium, taker_imbalance, liquidation, orderbook_microstructure, long_short_ratio

---

## C. Data Readiness Summary

| Data Type | Readiness | Blocking Issue | Next Step |
|-----------|-----------|----------------|-----------|
| taker_buy_sell_volume | YES | None — already in klines | READY_FOR_CANDIDATE_SELECTION |
| funding_rate | PARTIAL | Raw zipped CSV exists (536 symbols, 2020+). Need ingestion pipeline + 8h→1h alignment. | DEFINE_DATA_CONTRACT |
| open_interest | NO | No local data. Binance endpoint exists. | ADD_DATA_INGESTION |
| basis_premium | NO | No mark_price or index_price data. | ADD_DATA_INGESTION |
| mark_price | NO | No local data. | ADD_DATA_INGESTION |
| index_price | NO | No local data. | ADD_DATA_INGESTION |
| liquidation | NO | No local data. Real-time stream only. | ADD_DATA_INGESTION |
| orderbook_depth | NO | No historical data. Real-time only. | DEFER |
| bid_ask_spread | NO | Same as orderbook_depth. | DEFER |
| long_short_ratio | NO | No local data. Binance endpoint exists. | ADD_DATA_INGESTION |
| borrow_rate | NO | Not available for perps. | DEFER |

**Key finding**: Only taker_buy_sell_volume is immediately usable (already in klines). Funding rate data exists locally but needs a data contract (8h→1h alignment, known_at semantics). All other crypto-native types need data ingestion first.

---

## D. Batch-3 Recommendation

**Batch-3 should first run a crypto-native data contract phase before full implementation.**

Rationale:
- 5 candidates are PROPOSE_FOR_PHASE7K: 3 taker_imbalance (data ready) + 2 WQ101 expansion (OHLCV)
- 3 funding_rate candidates need data contract first
- 5 candidates are DEFER_DATA (no local data)
- 1 is DEFER_DIRECTION_UNCLEAR

The recommended path is:
1. Implement the 5 PROPOSE_FOR_PHASE7K candidates (3 taker_imbalance + 2 WQ101)
2. Simultaneously build funding_rate data contract (DEFINE_DATA_CONTRACT)
3. After funding_rate contract, implement funding_rate candidates
4. Defer OI/basis/liquidation/orderbook to later batches

---

## E. Proposed Candidate Groups

### Group 1: Taker Imbalance (data READY)
- B3_001: taker_buy_ratio_20h
- B3_002: taker_buy_zscore_20h
- B3_003: taker_buy_delta_5h

### Group 2: WQ101 Expansion (data READY)
- B3_012: wq101_alpha01 (rank(vwap-close))
- B3_013: wq101_alpha06 (correlation(open, volume, 10))

### Group 3: Funding Rate (data PARTIAL — needs contract)
- B3_004: funding_rate_level_20h
- B3_005: funding_rate_zscore_80h
- B3_006: funding_rate_change_24h

### Group 4: Deferred (data NOT READY)
- B3_007-B3_011: open_interest, basis, liquidation, orderbook

---

## F. Required Negative Declarations

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

## G. Phase 7K Readiness

Phase 7K Batch-3 data contract or candidate selection is allowed pending PM review.
