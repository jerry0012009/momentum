# Phase 6D — Dynamic Universe 1h Bars Dataset Closeout

> Date: 2026-06-13
>
> Status: COMPLETE — READY FOR REVIEW

---

## 1. Goal

Build a new Binance USDT-M perpetual 1h OHLCV dataset for all symbols selected
by the dynamic universe (`crypto_usdt_perp_monthly_volume_top50_current_listed_v1`).

This replaces the static top50 dataset for future evaluation with the dynamic universe.

## 2. Parameters

| Parameter | Value |
|-----------|-------|
| universe_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` |
| dataset_id | `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` |
| Date range | 2024-06-13 → 2026-06-13 |
| Timeframe | 1h |
| Source | data.binance.vision |

## 3. Results

| Metric | Value |
|--------|-------|
| Symbols requested | 266 |
| Symbols with data | 266 |
| Total rows | 3,316,259 |
| Date range (actual) | 2024-06-01 → 2026-06-13 |
| Symbols with zero rows | 0 |
| Symbols with >5% missing bars | 158 |
| Median missing_bar_rate | 26.1% |
| Max missing_bar_rate | 95.0% |
| Download errors (404) | 63,306 |

## 4. Output Files

```
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/
    bars_1h.parquet           3,316,259 rows × 15 columns
    symbol_availability.parquet  266 rows
    download_log.csv          63,306 entries
    manifest.json
    data_quality_report.md
```

## 5. Schema

Matches existing pipeline schema exactly:

```
timestamp, bar_open_time, bar_close_time, symbol,
open, high, low, close, volume, quote_volume, trade_count,
source, market, instrument_type, timeframe
```

Timestamp convention:
- `bar_open_time` = Binance kline `open_time`
- `bar_close_time` = `bar_open_time` + 1h
- `timestamp` = `bar_close_time`

## 6. Missing Bar Analysis

158 symbols have >5% missing bars. This is expected because:
- Many symbols were listed partway through the 2-year period
- Earlier months have no data for recently listed symbols
- This is NOT a data quality issue — it reflects actual listing history

## 7. Known Limitations

1. Universe is `dynamic_from_current_listed_pool`, not true PIT.
2. Candidate pool excludes delisted historical symbols.
3. This dataset is built only for symbols selected by the dynamic universe snapshots.
4. 63,306 download 404s — expected for symbols not yet listed in those months.

## 8. Tests

15/15 pass:
- kline zip parser schema
- timestamp == bar_open_time + 1h
- bar_close_time == timestamp
- numeric columns parsed correctly
- download 404 recorded not fatal
- duplicate timestamp-symbol rows removed
- manifest contains timestamp_convention
- symbol_availability missing_bar_rate computed correctly

## 9. Status

- Phase 6D: **COMPLETE**
- Phase 6E (labels build): **NOT YET** — needs human approval
- Phase 7: **NOT YET** — blocked on Phase 6 completion
