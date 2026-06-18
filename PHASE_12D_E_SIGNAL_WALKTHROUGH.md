# PHASE 12D-E: Signal Walkthrough

**Status:** COMPLETE
**Date:** 2026-06-18

## Deliverables

### New Pages
- reports/site/factor-library/signal-walkthrough.html
- reports/site/factor-library/assets/signal_walkthrough.json
- docs/factor_library_transparency/signal_walkthrough.md

### Updated Pages
- reports/site/factor-library/index.html (added signal-walkthrough nav card)

### Data Sources
- research/factor_runs/crypto_top50_factor_library/phase12a_latest_signal_snapshot.csv
- data/features/crypto_top50_usdt_perp_1h/{factor}/factor_values.parquet

### Walkthrough Timestamp
- Signal snapshot: 2026-06-13 00:00:00 UTC
- Factor values: 2026-06-13 08:00:00 UTC
- 43 available symbols, 16 in paper signal (8 long + 8 short)

### Sample Symbols
- LONG: BCHUSDT (signal=+1.087, rank #1, weight=+0.0625)
- SHORT: HUSDT (signal=-4.695, rank #43, weight=-0.0625)
- NEUTRAL: DOGEUSDT (signal=+0.387, rank #21, weight=0.0)

### Constraints
- Phase 13 NOT STARTED
- No real execution, no alpha claim, no production claim
- Forward returns at latest timestamp: N/A
- Raw bar data (close/high/low/volume): not available at per-symbol level in local data
