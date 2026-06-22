# PM-39 Audit — Public Factor Page Deployment Availability

## Verdict

`PUBLIC_FACTOR_PAGE_DEPLOYMENT_PASS`

## Why PM-39 was required

After PM-38B aligned entrypoint docs, Jerry reported the public page at `https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html` threw a JavaScript error:

```
Uncaught SyntaxError: Unexpected token 'N', ..."nth_rate":NaN,"recen"... is not valid JSON
    at JSON.parse (<anonymous>)
    at factor-evaluation.html:279:19
```

## Root cause

Python's `json.dumps()` serializes `float('nan')` as `NaN`, which is not valid JSON. JavaScript's `JSON.parse()` rejects it.

The NaN values came from `build_factor_shape_stability_diagnostics.py` — 3 fields (`ic_positive_month_rate`, `recent_vs_full_ic_delta`, `recent_vs_full_ls_delta`) lacked NaN guards for factors with insufficient history (empty monthly IC series but `n_months > 0` from LS data).

60 NaN occurrences across multiple factors/horizons in `factor_shape_stability_payload.json`.

## Local file checks

- `reports/site/factor-library/factor-evaluation.html`: exists, 2,851,836 bytes
- Page completeness QA: 19/19 PASS

## Public URL check before repair

- `https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html`: HTTP 200 (served) but JS error on load — page unusable

## Server configuration

- Apache 2.4.58 on Ubuntu
- Port 443: Alias `/momentum/` → `/var/www/momentum-report/`
- Port 24443: Alias `/momentum/factor-library/` → `/root/clawd/jerry/momentum/reports/site/factor-library/`
- Both return 200

## Repairs applied

1. **Source fix:** `scripts/build_factor_shape_stability_diagnostics.py` — added NaN guards for `ic_positive_month_rate`, `ls_positive_month_rate`, `recent_vs_full_ic_delta`, `recent_vs_full_ls_delta`

2. **Defense in depth:** `scripts/_build_factor_eval_html.py` — added `_sanitize_nan()` function that recursively replaces NaN/inf with null in all loaded JSON data before embedding in HTML

3. **Existing page fix:** Replaced 60 NaN occurrences with null in the deployed HTML

4. **Page regeneration:** Rebuilt page with fixed script — 0 NaN, JSON valid, 76 factors

5. **Deployed:** Copied to `/var/www/momentum-report/factor-library/`

## Runbook/resource guide updates

- Added §8 "NaN in JSON payload — critical pitfall" to `POST_INTAKE_WORKFLOW_RUNBOOK.md` — documents root cause, prevention (source guard, builder defense, post-build validation), and known vulnerable fields
- Added §8 "Post-rebuild JSON validity check" to `RESOURCE_AWARE_REFRESH_GUIDE.md`

## Public URL check after repair

- `https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html`: HTTP 200, JSON valid, 76 factors, page loads correctly

## Files changed

| File | Change |
|------|--------|
| `scripts/build_factor_shape_stability_diagnostics.py` | Added NaN guards for 4 fields |
| `scripts/_build_factor_eval_html.py` | Added `_sanitize_nan()` defense |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt (NaN-free) |
| `/var/www/momentum-report/factor-library/factor-evaluation.html` | Deployed |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Added §8 NaN pitfall |
| `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` | Added §8 JSON validation |

## Confirmation

- ✅ No factor formulas changed
- ✅ No factor_values changed
- ✅ No signal/strategy code changed
- ✅ No diagnostics CSV/JSON output changed (only the build script logic)
- ✅ Public page now loads correctly

## Remaining limitations

- None. Page is fully functional.

## Recommended next PM

PM-40: post-intake factor interpretation and direction-semantics review (deferred from PM-38).
