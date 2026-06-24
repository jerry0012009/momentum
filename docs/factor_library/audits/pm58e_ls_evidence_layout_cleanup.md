# PM-58E: LS Evidence Layout Cleanup

**Date:** 2026-06-24
**Verdict:** PM58E_LS_EVIDENCE_LAYOUT_CLEANUP_PASS

## Summary

Restructured the factor detail page LS evidence sections to eliminate the perception of
redundant metrics and establish a clear reading order. No numerical changes.

## Problem Statement

After PM-58C/58D, three LS evidence sections appeared adjacent without clear differentiation:
1. Edge Diagnostics Summary
2. Period-Level Window Diagnostics
3. Robust LS Diagnostics

Users perceived "the same metric repeated multiple times" because the page didn't explain
the distinct purpose of each section.

## Before Layout

```
Edge Diagnostics Summary
Period-Level Window Diagnostics    ← primary, no disclaimers
Robust LS Diagnostics              ← unexplained duplicate
```

## After Layout

```
📖 LS Evidence Reading Order (open by default)
  1. Edge Diagnostics Summary
  2. Robust LS Diagnostics
  3. Period-Level Window Diagnostics (secondary)

Edge Diagnostics Summary           ← primary
Robust LS Diagnostics              ← primary, with explanation
Period-Level Window Diagnostics    ← collapsed <details>, secondary
```

## Files Changed

| File | Change |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Reordered sections, added reading order guide, collapsed Window Diagnostics, added caution badges |
| `reports/.../factor-evaluation.html` | Rebuilt |
| `docs/audits/pm58e_*.md` | Audit document |

## Section Order

1. **Edge Diagnostics Summary** — 看因子是否有正向 LS edge，以及这个 edge 在月份之间是否稳定。
   *Check whether the factor has a positive LS edge and whether that edge is stable across months.*

2. **Robust LS Diagnostics** — 看这个 LS edge 在 Newey-West / bootstrap 修正后是否仍然稳健。
   *Check whether the LS edge remains statistically robust after Newey-West / bootstrap correction.*
   - Added explanatory text: "用于检验 LS edge 在 Newey-West / bootstrap 修正后是否仍然稳健。它不是又一张原始收益表。"
   - Renamed "LS Mean Return" → "Robust-tested LS Mean"

3. **Period-Level Window Diagnostics** — 月度 period-level 描述统计，只作为补充。
   *Monthly period-level descriptive statistics only. Not true per-bar investment-window data.*
   - Wrapped in `<details class="secondary-diagnostics">` (collapsed by default)
   - Added caution badges: "DESCRIPTIVE ONLY", "Not portfolio Sharpe", "Descriptive only"
   - Added warning text: "不是真正逐 K 线投资窗口数据，也不是独立交易胜率"

## What is Edge Diagnostics

Monthly per-bar LS edge stability metrics. Shows whether the factor's LS edge is positive
and stable across months. Primary evidence.

## What is Robust LS Diagnostics

Statistical robustness tests on LS returns. Uses Newey-West corrected t-stat and block
bootstrap CI to check if the LS edge survives overlap and autocorrelation correction.
Not a raw return table — it's a robustness test.

## What is Period-Level Window Diagnostics

Descriptive statistics computed from monthly period LS records. Each monthly period is
treated as one "window". This is NOT:
- True per-bar investment-window data
- Independent trade win rate
- Portfolio Sharpe

## Why Period-Level Window Diagnostics is Secondary

It's descriptive statistics without robustness correction. The same information (monthly LS
positive rate) is already available in Edge Diagnostics. Window LS Sharpe and Window LS Ann Vol
can produce misleadingly high values (e.g., +28) because they multiply monthly Sharpe by √12,
which amplifies noise when the monthly series is short or volatile.

## QA Results

- ✅ LS Evidence Reading Order present and visible
- ✅ Period-Level Window Diagnostics is `<details>` with secondary-diagnostics class
- ✅ Period-Level Window Diagnostics has monthly period LS / not true per-bar / not independent trade win rate disclaimers
- ✅ Robust LS section has Newey-West / bootstrap / statistical robustness explanation
- ✅ Window LS Sharpe has "Not portfolio Sharpe" caution
- ✅ Period-Level Window Diagnostics not in primary reading position
- ✅ No signal construction
- ✅ No trading recommendation

## No Numerical Recomputation

Pure layout/UX changes. No metric values changed.

## No Unauthorized Changes

- ✅ No new factors
- ✅ No factor formula changes
- ✅ No expected_direction / factor_values changes
- ✅ No scorecard / best_horizon changes

## Remaining Limitations

1. Window LS Sharpe/Ann Vol still computed and displayed (just with caution badges).
2. True per-bar window diagnostics still not implemented.
3. "Robust-tested LS Mean" label may need user education.

## Recommended Next PM

**PM-59:** True per-bar investment-window diagnostics — compute from raw factor values.
