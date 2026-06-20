# PM-02B Canonical Universe Builder Patch

**Date:** 2026-06-21
**Follows:** PM-01, PM-02A

## Summary

Deleted the stale universe builder `scripts/build_crypto_top50_universe.py` and promoted `scripts/build_dynamic_universe_monthly_volume.py` as the canonical universe builder across all governance docs, site metadata, and the public script map.

## Why the stale builder was deleted

`scripts/build_crypto_top50_universe.py` was proven stale and unused by active code:

| Evidence | Detail |
|----------|--------|
| Volume logic | Uses 24h snapshot volume (line 69-72 docstring: "This is a 24h snapshot, NOT a trailing 30-day rolling volume") |
| Misleading field name | Column named `trailing_30d_dollar_volume` but populated from `dollar_volume_24h` (line 197) |
| Hardcoded absolute path | `REPO_ROOT = Path("/root/clawd/jerry/momentum")` (line 22) |
| No active imports | `grep -RIn "build_crypto_top50_universe" scripts/ src/` returned only the script's own self-reference |
| No subprocess calls | No other script calls it via subprocess |

## Canonical universe builder after this patch

**`scripts/build_dynamic_universe_monthly_volume.py`**

Description (honest, not exaggerated):
- Monthly dynamic universe
- Top50 by previous full calendar month's Binance UM perpetual 1d `quote_volume` sum
- Current-listed candidate pool only
- Not true point-in-time universe
- Survivorship bias remains because delisted symbols are absent from the candidate pool

## Exact universe limitation statement

1. Candidate pool is current-listed only. Delisted historical symbols are NOT included.
2. This universe is `dynamic_from_current_listed_pool`, not `true_point_in_time_universe`.
3. It reduces static-current-top50 bias but does NOT eliminate delisted-symbol survivorship bias.
4. Symbols that were delisted between their listing month and now are missing from all months.

## Files changed

| File | Change |
|------|--------|
| `scripts/build_crypto_top50_universe.py` | **DELETED** (git rm) |
| `docs/factor_library/START_HERE.md` | Universe row → `build_dynamic_universe_monthly_volume.py` |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Pipeline diagram + table → canonical builder |
| `docs/factor_library/factor_library_manifest.json` | `active_mainline_scripts` → canonical builder |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | Stale script → `DELETED_STALE`; added canonical script as `ACTIVE_MAINLINE` |
| `reports/site/factor-library/assets/actual_script_map.json` | Universe node → canonical builder |
| `reports/site/factor-library/actual-script-map.html` | SVG text, JS nodes object, HTML detail panel → canonical builder |

## Validation commands run

```bash
python -m py_compile scripts/build_dynamic_universe_monthly_volume.py
# OK

grep -RIn "build_crypto_top50_universe" scripts/ src/
# Only self-reference in deleted script (now removed)

grep -RIn "build_dynamic_universe_monthly_volume" README.md docs/ scripts/ reports/
# All active governance/site references now point to canonical builder
```

## Explicit non-change statement

No universe parquet files, bars, labels, factor values, evaluations, signal panels, or public factor/signal result pages were regenerated.

## Remaining stale references

Historical audit/prompt references to `build_crypto_top50_universe.py` remain in:
- `docs/factor_library/audits/pm01_canonical_pipeline_reality_audit.md` (historical audit record)
- `docs/factor_library/prompts/PM01_CANONICAL_PIPELINE_REALITY_AUDIT_PROMPT_20260621.md` (historical prompt)
- `docs/factor_library/prompts/PM02B_CANONICAL_UNIVERSE_BUILDER_PRUNE_PROMPT_20260621.md` (this task's prompt)
- `docs/PROJECT_TREE.md` (project tree snapshot)

These are historical records and should not be edited.
