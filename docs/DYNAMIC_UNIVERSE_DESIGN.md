# Dynamic Universe Design

> Phase 6B — Monthly-Volume Dynamic Universe Builder

---

## 1. Goal

Replace the static `static_current_top50_by_24h_quote_volume` universe with a
monthly-rolling universe that uses previous-month data for selection, eliminating
one source of look-ahead bias.

## 2. Universe Mode

**Mode:** `dynamic_from_current_listed_pool`

For each calendar month M:
- Use only previous full calendar month M-1
- Sum Binance UM perpetual 1d `quote_volume`
- Sort descending, select top N symbols
- Universe is active for month M

**Known at:** month_start UTC (no look-ahead)

## 3. Candidate Pool

Source: Binance `fapi/v1/exchangeInfo`

Filters:
- `quoteAsset = USDT`
- `contractType = PERPETUAL`
- `status = TRADING`

**Critical limitation:** This is current-listed only. Delisted historical symbols
are NOT included. Therefore this universe is NOT true point-in-time.

## 4. What This Fixes

- Static-top-N bias: same 50 symbols used for entire history
- Look-ahead bias: current-month volume used for current-month selection

## 5. What This Does NOT Fix

- Survivorship bias: delisted symbols missing from history
- Delisting timing: symbols delisted mid-history are absent from all months
- Not true PIT: candidate pool is snapshot at build time, not historical

## 6. Output Structure

```
data/universe/<universe_id>/
    universe_snapshots.parquet      # per-month, per-symbol selection
    universe_manifest.json          # metadata + limitations
    candidate_symbols.parquet       # Binance exchangeInfo filtered
    monthly_selection_detail.parquet # per-month summary
```

## 7. Schema: universe_snapshots.parquet

| Column | Type | Description |
|--------|------|-------------|
| universe_id | str | Universe identifier |
| asof_time | str (ISO) | Month start UTC |
| selection_time_start | str (ISO) | Previous month start UTC |
| selection_time_end | str (ISO) | Current month start UTC |
| symbol | str | Selected symbol |
| rank | int | Rank by rank_metric (1=top) |
| rank_metric | str | `prev_full_month_quote_volume_sum` |
| rank_metric_value | float | Metric value |
| eligible | bool | Always True for selected |
| known_at | str (ISO) | Month start UTC |
| source | str | `binance_um_perp_1d_klines` |
| universe_mode | str | `dynamic_from_current_listed_pool` |
| notes | str | Additional notes |

## 8. Schema: candidate_symbols.parquet

| Column | Type | Description |
|--------|------|-------------|
| symbol | str | Binance symbol (e.g., BTCUSDT) |
| base_asset | str | Base asset (e.g., BTC) |
| normalized_base | str | Lowercase, stripped numeric prefix |
| contract_multiplier | float | Numeric prefix or 1.0 |
| onboard_utc | str (ISO) | Listing timestamp |
| onboard_ms | int | Listing timestamp in ms |
| quote_asset | str | Always USDT |
| contract_type | str | Always PERPETUAL |
| status | str | Always TRADING |
| source | str | `binance_fapi_exchangeInfo` |

## 9. Schema: monthly_selection_detail.parquet

| Column | Type | Description |
|--------|------|-------------|
| month | str | YYYY-MM |
| month_start_utc | str (ISO) | Month start UTC |
| selection_basis | str | `prev_full_month_quote_volume_sum_usdt` |
| selection_time_start | str (ISO) | Previous month start |
| selection_time_end | str (ISO) | Current month start |
| candidate_count | int | Eligible candidates |
| selected_count | int | Selected symbols |
| selected_symbols | str | Comma-separated |
| entered_symbols | str | New this month |
| exited_symbols | str | Left this month |

## 10. Comparison with rank213

| Aspect | rank213 | Factor library |
|--------|---------|----------------|
| Universe size | 30 | 50 (configurable) |
| Selection metric | quote_volume | quote_volume (configurable) |
| Selection freq | monthly | monthly |
| Candidate pool | current-listed | current-listed |
| Strategy logic | 15m rank, veto, gate | None — factor eval only |
| Output | HTML reports | Parquet + JSON |

rank213 code was used as design reference only. No strategy logic was imported.

## 11. Integration with Factor Library

Phase 6C+ will integrate this universe into the factor evaluation pipeline:
- Replace static universe with dynamic universe in `evaluate_factors.py`
- Each evaluation uses the month's universe from `universe_snapshots.parquet`
- Factor values computed only for symbols in the month's universe

## 12. Status

- Phase 6B: COMPLETE — dynamic universe builder (524 candidates, 25 months)
- Phase 6C: COMPLETE — data coverage audit (16.2% global coverage → new dataset needed)
- Phase 6D: COMPLETE — dynamic-universe 1h bars dataset (266 symbols, 3.3M rows)
- Phase 6D-QA: COMPLETE — membership-aware coverage (0 zero-bar months, labels build ALLOWED)
- Phase 6E: COMPLETE — forward-return labels (3.3M rows, membership-aware missing <0.5%)
- Phase 6F: COMPLETE — factor values (11 factors, all selected_missing <0.2%)
- Phase 6G: COMPLETE — factor evaluation (best RankIC volatility_20h -0.043)
- Phase 6H: COMPLETE — static-vs-dynamic comparison (19 robust candidates, 0 weakened, 0 sign-flipped)
- Phase 6: COMPLETE — all sub-phases finished
- Phase 7: ALLOWED — large-scale factor mining can proceed
- Phase 7: NOT YET — blocked on Phase 6 completion
