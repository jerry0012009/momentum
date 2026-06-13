# Phase 6B — Dynamic Universe Monthly Volume Closeout

> Date: 2026-06-13
>
> Status: COMPLETE — READY FOR REVIEW

---

## 1. Goal

Build a monthly-volume dynamic universe builder for the factor library, abstracted
from rank213's monthly-volume causal universe design. This provides a dynamic
alternative to `static_current_top50_by_24h_quote_volume`; it is not integrated
into evaluation yet (Phase 6C audit pending).

## 2. rank213 Reference

rank213 code (`scripts/build_rank213_monthly_volume_universe_rebuild.py`) was used
as **design reference only**. No strategy logic was imported:
- ❌ No FORMATION_BARS, HOLD_BARS, TOP_N/BOTTOM_N strategy ranking
- ❌ No longs/shorts, veto, gate, cost model
- ❌ No HTML reports, performance comparison
- ✅ Candidate pool logic (exchangeInfo filter) — abstracted
- ✅ Daily 1d kline download — rewritten as neutral functions
- ✅ Monthly previous-month selection — abstracted

## 3. New Files

| File | Lines | Description |
|------|-------|-------------|
| `scripts/build_dynamic_universe_monthly_volume.py` | ~520 | CLI universe builder |
| `tests/unit/test_dynamic_universe_monthly_volume.py` | ~280 | 13 unit tests |
| `docs/DYNAMIC_UNIVERSE_DESIGN.md` | ~140 | Design doc |

## 4. Output Files

```
data/universe/crypto_usdt_perp_monthly_volume_top50_current_listed_v1/
    universe_snapshots.parquet        1250 rows (50 symbols × 25 months)
    candidate_symbols.parquet         524 rows
    monthly_selection_detail.parquet  25 rows
    universe_manifest.json
```

## 5. Parameters

| Parameter | Value |
|-----------|-------|
| universe_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` |
| Date range | 2024-06-13 → 2026-06-13 |
| Top N | 50 |
| Rank metric | quote_volume |
| Selection frequency | monthly |
| Universe mode | `dynamic_from_current_listed_pool` |

## 6. Selection Logic

For each calendar month M:
1. Use only previous full calendar month M-1
2. Sum Binance UM perpetual 1d `quote_volume` for each candidate
3. Sort descending, select top 50
4. Universe active for month M

`known_at = month_start UTC` — no look-ahead.

## 7. Candidate Pool

Source: Binance `fapi/v1/exchangeInfo`
Filters: quoteAsset=USDT, contractType=PERPETUAL, status=TRADING
Total candidates: 524

**Critical limitation:** Current-listed only. Delisted historical symbols are NOT included.

## 8. Months Generated

| Month | Candidates | Selected | Entered | Exited |
|-------|-----------|----------|---------|--------|
| 2024-06 | 206 | 50 | 50 | 0 |
| 2024-07 | 211 | 50 | ... | ... |
| ... | ... | ... | ... | ... |
| 2026-06 | 521 | 50 | ... | ... |

25 months total.

## 9. Known Limitations

1. **Candidate pool is current-listed only.** Delisted historical symbols are not included.
2. **This is `dynamic_from_current_listed_pool`, not `true_point_in_time_universe`.**
3. **It reduces static-current-top50 bias but does NOT eliminate delisted-symbol survivorship bias.**
4. **Symbols delisted between their listing month and now are missing from all months.**

## 10. Tests

13/13 pass:
- previous-month selection only
- no current-month quote_volume used
- top_n selection correct
- known_at == month_start
- asof_time == month_start
- candidate status filter works
- onboardDate eligibility works
- output schema exact
- manifest includes current-listed limitation
- universe_mode == dynamic_from_current_listed_pool

## 11. Status

- Phase 6B: **COMPLETE**
- Phase 6C (integrate with factor eval): **NOT YET** — needs human approval
- Phase 7: **NOT YET** — blocked on Phase 6 completion
