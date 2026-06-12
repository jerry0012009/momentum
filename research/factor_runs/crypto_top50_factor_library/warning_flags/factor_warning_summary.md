# Factor Warning Flags Summary

- generated_at: 2026-06-12T16:09:03Z
- universe: crypto_top50_usdt_perp_1h
- purpose: lightweight risk-awareness mechanism for diagnostic probes
- this is NOT a pass/fail gate

## Overview

| factor | label | flags | severity | recommendation |
|---|---|---|---|---|
| mom_20h | ret_fwd_1h | 3 | MEDIUM | REVIEW_LATER |
| mom_20h | ret_fwd_4h | 4 | HIGH | PARK |
| mom_20h | ret_fwd_24h | 5 | HIGH | PARK |
| mom_20h | ret_fwd_72h | 4 | HIGH | PARK |
| reversal_5h | ret_fwd_1h | 4 | HIGH | PARK |
| reversal_5h | ret_fwd_4h | 3 | MEDIUM | REVIEW_LATER |
| reversal_5h | ret_fwd_24h | 5 | HIGH | PARK |
| reversal_5h | ret_fwd_72h | 4 | HIGH | PARK |
| volatility_20h | ret_fwd_1h | 4 | HIGH | PARK |
| volatility_20h | ret_fwd_4h | 2 | MEDIUM | REVIEW_LATER |
| volatility_20h | ret_fwd_24h | 4 | HIGH | PARK |
| volatility_20h | ret_fwd_72h | 4 | HIGH | PARK |
| rsi_14h | ret_fwd_1h | 2 | MEDIUM | REVIEW_LATER |
| rsi_14h | ret_fwd_4h | 2 | MEDIUM | REVIEW_LATER |
| rsi_14h | ret_fwd_24h | 4 | HIGH | PARK |
| rsi_14h | ret_fwd_72h | 3 | MEDIUM | REVIEW_LATER |
| bb_zscore_20h | ret_fwd_1h | 1 | LOW | KEEP_AS_PROBE |
| bb_zscore_20h | ret_fwd_4h | 2 | MEDIUM | REVIEW_LATER |
| bb_zscore_20h | ret_fwd_24h | 3 | MEDIUM | REVIEW_LATER |
| bb_zscore_20h | ret_fwd_72h | 2 | MEDIUM | REVIEW_LATER |

## Flag Frequency

| flag | count |
|---|---:|
| DIRECTION_CONFLICT | 16 / 20 |
| SYMBOL_CONCENTRATION | 16 / 20 |
| MONTHLY_INSTABILITY | 14 / 20 |
| OVERLAP_INFLATION | 10 / 20 |
| OUTLIER_SENSITIVE | 9 / 20 |

## Per-Factor Summary

### mom_20h
- max severity: **HIGH**
- active flags: DIRECTION_CONFLICT, MONTHLY_INSTABILITY, OUTLIER_SENSITIVE, OVERLAP_INFLATION, SYMBOL_CONCENTRATION
- recommendation across labels: REVIEW_LATER, PARK

### reversal_5h
- max severity: **HIGH**
- active flags: DIRECTION_CONFLICT, MONTHLY_INSTABILITY, OUTLIER_SENSITIVE, OVERLAP_INFLATION, SYMBOL_CONCENTRATION
- recommendation across labels: PARK, REVIEW_LATER

### volatility_20h
- max severity: **HIGH**
- active flags: DIRECTION_CONFLICT, MONTHLY_INSTABILITY, OUTLIER_SENSITIVE, OVERLAP_INFLATION, SYMBOL_CONCENTRATION
- recommendation across labels: PARK, REVIEW_LATER

### rsi_14h
- max severity: **HIGH**
- active flags: DIRECTION_CONFLICT, MONTHLY_INSTABILITY, OVERLAP_INFLATION, SYMBOL_CONCENTRATION
- recommendation across labels: REVIEW_LATER, PARK

### bb_zscore_20h
- max severity: **MEDIUM**
- active flags: DIRECTION_CONFLICT, MONTHLY_INSTABILITY, OVERLAP_INFLATION
- recommendation across labels: KEEP_AS_PROBE, REVIEW_LATER

## Philosophy

This system flags risks. It does not eliminate factors.
Diagnostic probes are expected to have warnings — that's why they're probes.
The goal is awareness, not optimization.

## Next Steps

1. Use these flags as context when reviewing factor results
2. Do NOT tune thresholds to make current factors pass
3. Build new factors from the skeleton (FACTOR_LIBRARY_SKELETON.md)
4. Let the warning system evolve as the library grows
