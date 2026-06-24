# CAP Data Source Contract

**Status:** `CAP_POINT_IN_TIME_APPROXIMATE`
**Last reviewed:** PM-58 (2026-06-24)

---

## 1. Source Definition

Cap = underlying coin USD market capitalization, used as a conditional input for cap-based factors (volume-cap regression family).

**NOT:**
- Not futures quote_volume
- Not liquidity
- Not tradable capacity
- Not open interest

## 2. Construction Method

1. **Supply proxy:** CoinGecko current circulating supply snapshot × Binance price at nearest month-start
2. **Hourly alignment:** Monthly supply proxy forward-filled to 1h bars, multiplied by hourly close price
3. **Output:** `market_cap_1h_aligned.parquet` — one column per symbol, aligned to the same 1h bar index as other OHLCV data

## 3. Timestamp Convention

- Supply snapshot: current (not historical)
- Price: month-start nearest available Binance close
- Hourly cap: supply_proxy × hourly_close
- **Point-in-time status:** APPROXIMATE — supply changes (token burns, unlocks) are NOT reflected retroactively

## 4. Null Coverage

- Symbols not in CoinGecko top universe at snapshot time have NaN cap
- Early bars before first price observation are NaN
- Cap is only computed for symbols in the active universe

## 5. Symbol Mapping Caveat

- CoinGecko symbol ≠ Binance symbol (e.g., `USDT` vs `BUSD` edge cases)
- Mapping uses uppercase ticker matching
- Stablecoins and wrapped tokens may have inflated/deflated cap

## 6. Circulating Supply Snapshot Caveat

- CoinGecko circulating supply is a current snapshot, not historical
- For backtesting, this introduces look-ahead bias in supply data
- Token unlocks, burns, and minting events are NOT captured retroactively
- This is a KNOWN LIMITATION documented in FactorSpec notes

## 7. Allowed Use

- Volume-cap regression factors (alpha101 volume_cap_alpha family)
- Cap-relative diagnostics (cap-aware shape, decile)
- Universe construction (rank213 monthly marketcap universe)

## 8. Disallowed Use

- Signal construction (cap is not a signal input)
- Trading capacity estimation
- Liquidity estimation
- Open interest proxy

## 9. Active Cap Factors

| Factor ID | Family | Formula |
|-----------|--------|---------|
| a101_volume_cap_alpha_min_80_80 | alpha101_curated_volume_cap_regression | rolling_min(ts_alpha(volume, cap, 80), 80) |
| a101_volume_cap_alpha_min_56_84 | alpha101_curated_volume_cap_regression | rolling_min(ts_alpha(volume, cap, 56), 84) |

## 10. QA Commands

```bash
# Verify cap data exists
ls -la data/processed/market_cap_1h_aligned.parquet

# Verify cap factors have values
python -c "
import pandas as pd
fv = pd.read_csv('research/factor_runs/crypto_top50_factor_library/factor_values/factor_values_panel.csv')
for fid in ['a101_volume_cap_alpha_min_80_80', 'a101_volume_cap_alpha_min_56_84']:
    sub = fv[fv['factor_id']==fid]
    print(f'{fid}: {len(sub)} rows, null_rate={sub[\"factor_value\"].isna().mean():.3f}')
"

# Verify cap factors pass consistency check
python scripts/check_active_factor_workflow_consistency.py
```

---

## Caveat Summary

> Cap data uses current circulating supply snapshot applied retroactively. This is APPROXIMATE, not true point-in-time. Known look-ahead bias in supply data. Use cap factors with this caveat in mind. Cap is NOT liquidity, NOT tradable capacity, NOT open interest.
