# PM-33: Unified Profile Page Integration

**Date:** 2026-06-22
**Follows:** PM-32C (evidence truthfulness)

---

## Summary Verdict

**`UNIFIED_PROFILE_PAGE_INTEGRATION_PASS`**

## 1. Files Changed

- `scripts/_build_factor_eval_html.py`
- `reports/site/factor-library/factor-evaluation.html`
- `docs/factor_library/audits/pm33_unified_profile_page_workflow_readiness.md`

## 2. Sections Added

1. **Unified Factor Evaluation Workflow / 统一因子评价工作流** — top-level overview with distributions
2. **Unified Factor Profile / 统一因子画像** — per-factor detail with badges, strength/risk, summary
3. **Component Scores** — 10 component bars + profile_score
4. **Evidence Matrix** — 16 has_* badges (pass/warn/missing)
5. **Source Lineage** — artifact count + list

## 3. Existing Sections Preserved

- ✅ Factor Quality Scorecard
- ✅ Redundancy & novelty
- ✅ Single-Factor Paper Portfolio
- ✅ BTC / Market Regime Diagnostics
- ✅ Quantile Shape & Rolling Stability
- ✅ Direction-aware Decile Shape Diagnostics
- ✅ Capacity / Liquidity Proxy Diagnostics

## 4. Caveats

✅ Bilingual disclaimers:
- "research diagnostics... not select signals, not construct portfolios, not recommend trading"
- "研究性诊断汇总... 不选择信号、不构建组合，也不构成交易建议"

## 5. HTML Size

2.84MB (< 4.5MB limit)

## 6. Validation

All 19 checks PASS

## 7. Limitations

None

## 8. Non-Change Statement

No factors, formulas, factor_values, signal panel modified.

## 9. Recommended Next PM

**PM-34:** Factor expansion backlog and intake-readiness test.
