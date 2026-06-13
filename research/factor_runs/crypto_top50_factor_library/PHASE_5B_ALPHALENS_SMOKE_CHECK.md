# Phase 5C — Alphalens Smoke Check Report (Sample-Aligned)

> Generated: 2026-06-13T17:34:05.579465+00:00
> Dataset: crypto_top50_usdt_perp_1h_long_v1
> Alphalens: v0.4.6

---

## 1. Dependency Status

- alphalens-reloaded: **True** (v0.4.6)

## 2. Sample Alignment

### mom_20h

| Metric | Value |
|--------|-------|
| Pre-filter rows | 713,572 |
| Post-filter rows | 560,386 |
| Pre-filter symbols | 50 |
| Post-filter symbols (evaluation universe) | 32 |
| Excluded symbols | 18 |
| Excluded list | AIOUSDT, ALLOUSDT, BEATUSDT, EPICUSDT, ESPORTSUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, LABUSDT, PAXGUSDT, PLAYUSDT, SIRENUSDT, SKYAIUSDT, SPACEUSDT, TRUMPUSDT, VELVETUSDT, XPLUSDT |

### wq101_alpha53

| Metric | Value |
|--------|-------|
| Pre-filter rows | 713,572 |
| Post-filter rows | 560,738 |
| Pre-filter symbols | 50 |
| Post-filter symbols (evaluation universe) | 32 |
| Excluded symbols | 18 |
| Excluded list | AIOUSDT, ALLOUSDT, BEATUSDT, EPICUSDT, ESPORTSUSDT, HMSTRUSDT, HOMEUSDT, HUSDT, HYPEUSDT, LABUSDT, PAXGUSDT, PLAYUSDT, SIRENUSDT, SKYAIUSDT, SPACEUSDT, TRUMPUSDT, VELVETUSDT, XPLUSDT |

## 3. IC Comparison (Sample-Aligned, Hourly Freq)

**Primary:** Alphalens Spearman IC vs Direct Hourly Spearman IC (same data, same hourly freq).

| Factor | Horizon | Local Summary RankIC | Direct Spearman IC | Alphalens Spearman IC | Primary Abs Diff | Status |
|--------|---------|---------------------|-------------------|----------------------|-----------------|--------|
| mom_20h | 1h | -0.025049 | -0.025049 | -0.025107 | 0.000059 | near_match |
| mom_20h | 4h | -0.033273 | -0.033273 | -0.033332 | 0.000059 | near_match |
| mom_20h | 24h | -0.020934 | -0.020934 | -0.020993 | 0.000058 | near_match |
| mom_20h | 72h | -0.015305 | -0.015305 | -0.015363 | 0.000058 | near_match |
| wq101_alpha53 | 1h | 0.017332 | 0.017332 | 0.017276 | 0.000056 | near_match |
| wq101_alpha53 | 4h | 0.010504 | 0.010504 | 0.010448 | 0.000056 | near_match |
| wq101_alpha53 | 24h | 0.004492 | 0.004492 | 0.004550 | 0.000057 | near_match |
| wq101_alpha53 | 72h | 0.003269 | 0.003269 | 0.003327 | 0.000057 | near_match |

**Summary:** match=0, near_match=8, mismatch=0
## 4. Comparison Methodology

- **Primary comparison:** Alphalens Spearman IC vs Direct Hourly Spearman IC.
  Both use the same sample-aligned factor_data with hourly freq (freq='h' set on MultiIndex).
  Without freq='h', Alphalens's asfreq(None) collapses hourly rows into daily, causing false mismatches.
- **Local Summary RankIC:** From `result_summary_*.md` (different NaN handling, different sample period).
- Sample alignment: excluded 18 symbols with missing_bar_rate > 5%, matching local evaluation universe.

## 5. Limitations

- Alphalens IC = Spearman rank correlation; direct Spearman computed from same aligned data.
- freq='h' set on MultiIndex to prevent Alphalens asfreq(None) from collapsing hourly → daily.
- Local summary RankIC shown for reference only (different NaN handling, different sample period).
- get_clean_factor_and_forward_returns() skipped — hourly frequency not supported.
- No factor status upgrade can be based solely on Alphalens output.

## 6. Conclusion

- **Overall status: PASS**
- Factors tested: 2
- Comparison rows: 8

All primary comparisons are match or near_match.
- Phase 5 (Alphalens export + smoke check): **COMPLETE**
- Phase 6 (Dynamic Universe): **READY — requires human approval**
