# PM-59A: Overlapping Sleeve Strategy Diagnostics

## 1. Problem Statement

Monthly edge diagnostics (PM-58A) and period-level window diagnostics (PM-58C) cannot answer:
- What is the real hourly strategy return path if best_horizon = 72h?
- What is the real annualized vol, Sharpe, max drawdown at hourly frequency?
- How do these differ from monthly edge estimates?

PM-59A adds a **single-factor overlapping sleeve strategy diagnostic** that computes
realized hourly returns using overlapping sleeves held for each factor's best horizon.

## 2. Methodology: Overlapping Sleeve Portfolio

For each factor with best_horizon = h:

1. **Every hour** `t`: cross-sectional rank of factor values within dynamic universe
2. **Direction handling:**
   - Registry positive/negative → direct alignment
   - Registry conditional → empirical direction from RankIC (primary) or LS spread (fallback)
     - `direction_source = empirical_rankic_at_selected_horizon` or `empirical_ls_at_selected_horizon`
     - If both missing: default positive with `direction_confidence = low`
     - This does NOT modify registry expected_direction
3. **Basket formation:** long top 20%, short bottom 20%, equal-weight per leg
4. **Sleeve holds h hours**, contributing realized 1h returns each hour
5. **Strategy hourly return** at τ = mean of all active sleeves' returns at τ
6. **NOT** using h-hour forward label as strategy return
7. **NOT** using monthly edge as strategy path

## 3. Return Timestamp Convention

```
realized_1h_return[return_start_ts, symbol] = close[return_start_ts + 1h] / close[return_start_ts] - 1
```

- `return_start_ts = entry_ts + (holding_offset - 1) hours`
- `holding_offset` ranges from 1 to h
- First hour's return uses `return_start_ts = entry_ts`

## 4. Spread Convention

```
sleeve_hourly_return = mean(long_leg_returns) - mean(short_leg_returns)
```

NOT symbol-level contribution mean (which would halve the spread).

## 5. Universe Source

`universe_snapshots.parquet` (monthly volume top 50 eligible symbols).
Factor values are joined with universe snapshots by month to filter eligible symbols.
Consistent with `evaluate_factors.py` and `build_factor_values.py`.

## 6. Factor Discovery

**Source:** `factor_library_state.json` → `computed_factor_ids` (currently 84 factors).

No hardcoded factor list. New factors registered through intake automatically enter PM-59A.

**Eligibility filter:** only requires `factor_values.parquet` to exist and be non-empty.

**Direction derivation:**
- 50 factors: registry positive/negative → direct
- 29 factors: registry conditional → empirical RankIC/LS direction
- 5 factors: missing best_horizon → derived from abs RankIC/LS

**Horizon derivation:**
- 79 factors: from `factor_level_coverage_summary.csv` (best_adj_ic_horizon)
- 5 factors: derived from max abs RankIC across horizons

## 7. Workflow Integration

**Stage:** `overlapping-sleeve-strategy` in `run_factor_library_refresh.py`
**Position:** after `diagnostics`, before `metadata`
**Marked as:** EXPENSIVE, OPTIONAL-BUT-STANDARD

Supports parameter passthrough:
- `--factor-ids` (subset mode)
- `--only-missing` (incremental)
- `--max-factors` (debug)
- `--overwrite` (recompute)

## 8. Output Files

```
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
├── factor_overlapping_sleeve_strategy_summary.csv
├── factor_overlapping_sleeve_strategy_summary.json
├── factor_overlapping_sleeve_strategy_manifest.json
├── overlapping_sleeve_strategy_returns/
│   └── <factor_id>__<horizon>.parquet
├── overlapping_sleeve_strategy_qa_report.csv
└── overlapping_sleeve_strategy_qa_report.json
```

Per-factor parquet columns: `timestamp`, `strategy_hourly_return`, `active_sleeve_count`,
`cumulative_gross_return`, `drawdown`.

## 9. Resource Controls

- Factor-by-factor streaming (single factor ~5-30s)
- Pre-loads universe + returns panel once (~80MB)
- Per-factor: loads factor_values (~240MB), merges, computes, writes, frees
- Total runtime for 84 factors: ~20 minutes
- Supports `--only-missing` for incremental runs

## 10. QA Results

23/23 checks PASS:
- Coverage: 84/84 computed factors have rows
- Conditional direction: 29 factors use empirical direction (not registry)
- Default horizon: 5 factors use derived horizon
- No duplicates, no prohibited language, no hardcoded factor list
- Active sleeve count bounds verified per horizon
- Return alignment spot check: PASS
- All metrics in valid ranges

## 11. No Unauthorized Changes

PM-59A does NOT modify:
- Factor formulas
- Registry expected_direction
- Factor values computation
- Best horizon canonical selection
- Scorecard / quality score
- RankIC / LS / robust RankIC / robust LS values
- `src/momentum/strategies/`
- Broker / execution / exchange API
- Live signal / portfolio allocation

## 12. Remaining Limitations

1. **Fixed quantile:** top/bottom 20% (10 symbols each in 50-symbol universe)
2. **Equal-weight baskets:** no volatility weighting or risk parity
3. **Gross only:** no fees, slippage, or transaction costs
4. **Warmup period:** first h hours have fewer active sleeves (expected behavior)
5. **Arithmetic annualization:** `mean_hourly × 8760`, not geometric CAGR
6. **Conditional direction:** empirical in-sample, not prior alpha direction
7. **Default horizon rows:** diagnostic fallback, not canonical best_horizon
8. **No PM-59B:** non-overlap offset ensemble not yet implemented
9. **No HTML deep integration:** basic metric grid only, no hourly return charts

## Verdict

`PM59A_OVERLAPPING_SLEEVE_STRATEGY_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
