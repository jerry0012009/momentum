# Phase 12B Closeout — Paper Signal Monitoring Backfill & Rolling Diagnostics

> Date: 2026-06-15
> Previous: Phase 12A COMPLETE
> Scope: Rolling paper signal monitoring over 30-day window

---

## Status

Phase 12B: COMPLETE, pending PM review.

---

## 1. Did rolling paper signal generation work?

**Yes.** 721 hourly timestamps over 30 calendar days (2026-05-14 to 2026-06-13). 31,003 paper signal log rows. 43 symbols with liquidity data at each timestamp. Signal ranking, side assignment, and weighting applied consistently.

## 2. How stable are the upper/lower symbol sets?

- Mean upper-side churn: 0.326 (32.6% of symbols change per hour)
- Mean lower-side churn: 0.326
- Mean rank change: moderate (symbols shift ranks within the cross-section)
- The signal is not static — it responds to evolving market conditions. Churn is moderate but not extreme.

## 3. How high is turnover in rolling paper monitoring?

| Metric | Value |
|--------|-------|
| Median hourly turnover | 12.5% |
| Mean hourly turnover | 14.9% |
| 95th percentile | 25.0% |
| Maximum | 43.8% |

Turnover is moderate for a 1h cross-sectional momentum signal. One turnover spike detected (2026-05-18, turnover=43.8%).

## 4. Does the signal survive low-cost assumptions in rolling paper tracking?

**Yes.** Cumulative low-cost net spread (fee=2bps + slip=5bps = 7bps, turnover-adjusted): **+0.295** over 30 days. Positive and survives.

## 5. Does it survive mid-cost assumptions?

**Yes.** Cumulative mid-cost net spread (fee=5bps + slip=10bps = 15bps, turnover-adjusted): **+0.209** over 30 days. Still positive.

**Key insight:** Phase 11A used a per-rebalance full-cost model (cost × full turnover every period), which was overly pessimistic. Rolling monitoring uses actual per-timestamp turnover, giving a more realistic cost picture. The signal survives mid-cost when costs are properly scaled by actual turnover.

## 6. Are liquidity and freshness sufficient?

- 43/43 liquidity-available symbols at every timestamp
- No zero-volume weighted symbols
- Liquidity data covers the full monitoring window
- Data freshness: OK (lag within acceptable range)

## 7. Were any alerts triggered?

**1 alert:** TURNOVER_SPIKE on 2026-05-18 20:00 (turnover=43.8%, severity=WARNING). This is a single-hour spike, likely caused by a sudden cross-sectional reordering. No persistent issue.

No alerts for: DATA_STALE, LIQUIDITY_MISSING, ZERO_VOLUME_WEIGHTED_SYMBOL, NET_EXPOSURE_DRIFT, GROSS_EXPOSURE_DRIFT, COST_FAILURE, or CAPACITY_WARNING.

## 8. Is Phase 12C transparency/learning closeout appropriate now?

**Yes.** Phase 12B confirms the paper signal harness works, generates consistent signals, survives cost assumptions, and has adequate liquidity coverage. A Phase 12C transparency closeout would document lessons learned and prepare for PM decision on Phase 13.

## 9. Is Phase 13 still blocked?

**Yes.** Phase 13 (live paper execution or real execution) remains blocked until PM explicitly approves. Phase 12B provides the diagnostic evidence needed for that decision.

## 10. Should the project continue, return to signal redesign, or pause?

**Recommendation: Continue to Phase 12C transparency closeout, then PM decision on Phase 13.**

Evidence supporting continuation:
- Signal survives both low-cost and mid-cost scenarios (turnover-adjusted)
- Turnover is manageable (median 12.5%)
- Liquidity is sufficient for the 43-symbol universe
- No critical alerts
- Cross-sectional momentum signal is working as designed

Evidence requiring caution:
- Gross spread is thin (mean 0.051% per timestamp)
- Mid-cost net spread is positive but slim (+0.209 over 30 days)
- Only 43 symbols (limited universe)
- Phase 11A's per-rebalance cost model flagged concerns (though rolling monitoring is more favorable)

---

## Negative Declarations

- No real execution
- No exchange connection
- No order placement
- No credentials
- No final model selected
- No production claim
- No Phase 13

---

## Artifacts

| File | Rows | Description |
|------|------|-------------|
| `phase12b_paper_signal_log.csv` | 31,003 | Rolling paper signals |
| `phase12b_signal_stability_summary.csv` | 721 | Per-timestamp stability |
| `phase12b_turnover_monitoring.csv` | 721 | Per-timestamp turnover |
| `phase12b_exposure_monitoring.csv` | 721 | Per-timestamp exposure |
| `phase12b_liquidity_monitoring.csv` | 721 | Per-timestamp liquidity |
| `phase12b_data_freshness_monitoring.csv` | 1 | Freshness summary |
| `phase12b_realized_paper_return_tracking.csv` | 721 | Per-timestamp returns |
| `phase12b_realized_return_summary.csv` | 1 | Return summary |
| `phase12b_monitoring_alerts.csv` | 1 | Alerts |
| `phase12b_quality_checks.csv` | 15 | All PASS |
| `PHASE_12B_PAPER_MONITORING_DIAGNOSTIC.md` | — | This closeout |
| `scripts/run_phase12b_paper_monitoring.py` | — | Script |
| `tests/unit/test_phase12b_paper_monitoring.py` | — | Tests |
