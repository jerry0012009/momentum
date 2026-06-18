# PHASE 12D-C-R: Factor Source Map & Phase 9B Factor Lineage Repair

**Status:** COMPLETE
**Date:** 2026-06-18
**Previous:** Phase 12D-C

## Problem

Phase 12D-C factor-source-map contained severe lineage errors:
- Listed mom_20h, reversal_5h, volatility_20h, rsi_14h, bb_zscore_20h, wq101_alpha101 as Phase 9B surviving candidate factors
- These are historical/experimental factors, NOT the actual Phase 9B signal panel factors
- Real authority: `scripts/build_phase9b_signal_panel.py`

## Corrected Factor List

Phase 9B signal panel uses 10 FACTOR_IDS from build_phase9b_signal_panel.py:

**RISK_PRESSURE (4):** vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h
**TECHNICAL_REVERSION (2):** rsi_7h, rsi_28h
**LIQUIDITY_GATE (1):** xs_rank_vol
**RANGE_POSITION (3):** range_1h, range_4h, price_pos_24h

## Surviving Candidate

signal_v0_core_only__1h__original_no_guard uses 6 core factors:
- risk_pressure = mean(vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h) — each 25%
- oscillator = mean(rsi_7h, rsi_28h) — each 50%
- raw_core = 0.60 × risk + 0.40 × oscillator
- signal = xs_zscore(raw_core)

## Files Updated

- reports/site/factor-library/factor-source-map.html — full rewrite with correct factors
- reports/site/factor-library/assets/factor_source_map.json — full rewrite with correct factors
- docs/factor_library_transparency/factor_source_map.md — full rewrite

## Files Created

- PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md (this file)
- phase12d_c_r_quality_checks.csv
- tests/unit/test_phase12d_c_r_factor_lineage.py

## Disclaimers

- Phase 13 NOT STARTED
- No real execution
- No alpha claim
- No production claim
- No research results changed
