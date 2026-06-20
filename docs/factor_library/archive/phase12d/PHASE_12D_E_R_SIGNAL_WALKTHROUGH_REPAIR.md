# PHASE 12D-E-R: Signal Walkthrough Repair

**Status:** COMPLETE
**Date:** 2026-06-18

## Fixes

### 1. rsi_28h Direction Fix
- rsi_28h is NEGATIVE in build_phase9b_signal_panel.py
- All 6 factors (vol_5h, vol_40h, downside_vol_20h, vol_of_vol_20h, rsi_7h, rsi_28h) are sign-flipped
- oscillator_exhaustion = mean(flipped(rsi_7h), flipped(rsi_28h))

### 2. Timestamp Consistency
- Signal snapshot, factor values, and signal components all from 2026-06-13 00:00:00 UTC
- Component values (risk_pressure, oscillator_exhaustion, raw_core_score) from phase9b_signal_panel.parquet

### 3. Real Component Values
- BCHUSDT: risk=0.587, osc=0.900, raw_core=0.712, signal=+1.087
- HUSDT: risk=-4.000, osc=-1.696, raw_core=-3.078, signal=-4.695
- DOGEUSDT: risk=-0.047, osc=0.704, raw_core=0.254, signal=+0.387

## Deliverables
- signal-walkthrough.html (repaired)
- signal_walkthrough.json (repaired)
- signal_walkthrough.md (repaired)
- PHASE_12D_E_R_SIGNAL_WALKTHROUGH_REPAIR.md
- phase12d_e_r_quality_checks.csv
- tests/unit/test_phase12d_e_r_signal_walkthrough.py
