# PM-33: Unified Profile Workflow Readiness → Factor Evaluation Page

**Status:** COMPLETE  
**Date:** 2026-06-22  
**Commit:** (pending)

## Summary

Added unified factor evaluation workflow readiness and per-factor unified profile sections to the factor-evaluation.html page. The page now displays:

1. **Workflow-level summary** — workflow version, stage count, evidence status distribution, workflow-ready distribution, profile class distribution, recommended research action distribution, component weights, and bilingual not-production disclaimer.

2. **Per-factor unified profile detail** — profile score, profile class, profile confidence, workflow-ready status, evidence status, evidence completeness rate, registry/data status, recommended research action, bilingual strength/risk/summary, missing/stale blocks.

3. **Component score bar chart** — 10 component scores (standalone_quality, paper, cost, regime, shape, stability, capacity, redundancy, marginal_info, evidence_completeness) + profile_score as compact horizontal bars.

4. **Evidence matrix badges** — 15 has_* evidence blocks displayed as pass (green ✓) / missing (red ✗) badges.

5. **Source lineage** — source_artifact_count and source_artifacts displayed as compact badges.

6. **Bilingual caveats** — Research diagnostics disclaimer in both Chinese and English at both summary and per-factor levels.

## Data Sources Consumed

| Source | Type | Description |
|--------|------|-------------|
| `factor_profile_payload.json` | JSON | Unified profile per-factor data + top-level distributions + component weights |
| `factor_unified_profile_summary.json` | JSON/CSV | Per-factor unified profile summary (71 factors) |
| `factor_evaluation_evidence_matrix.csv` | CSV | Per-factor evidence matrix (15 has_* columns) |
| `factor_evaluation_evidence_matrix.json` | JSON | Evidence status distribution summary |
| `factor_profile_component_scores.csv` | CSV | Per-factor 10-component scores |
| `factor_profile_manifest.json` | JSON | Workflow manifest with source/output artifacts |
| `factor_evaluation_workflow_contract.json` | JSON | Workflow contract with stage_order (20 stages) |

## Sections Added to Page

1. **Unified Factor Evaluation Workflow / 统一因子评价工作流** — top-level summary section between cap/liquidity summary and caveats
2. **Unified Factor Profile / 统一因子画像** — per-factor detail section after capacity/liquidity in the detail panel

## Preserved Existing Sections

- Factor Scoreboard / 因子排行榜
- Factor Quality Scorecard Summary / 因子质量记分卡概要
- Single-Factor Paper Portfolio Summary / 单因子纸面组合概要
- BTC / Market Regime Diagnostics Summary / BTC / 市场状态诊断概要
- Capacity / Liquidity Proxy Summary / 容量 / 流动性代理概要
- Scorecard Interpretation / 记分卡解读
- All per-factor detail sections (formula, metrics, redundancy, charts, paper, regime, shape, capacity)

## Validation Results

All 19 string checks pass:
- `Unified Factor Evaluation Workflow` ✓
- `统一因子评价工作流` ✓
- `Unified Factor Profile` ✓
- `统一因子画像` ✓
- `workflow_ready_status` ✓
- `evidence_status` ✓
- `profile_class` ✓
- `recommended_research_action` ✓
- `has_factor_values` ✓
- `has_factor_level_evaluation` ✓
- `has_unified_profile` ✓
- `source_artifacts` ✓
- `research diagnostics` ✓
- `不选择信号` ✓
- `Single-Factor Paper Portfolio` ✓
- `Capacity / Liquidity Proxy Diagnostics` ✓
- `Quantile Shape & Rolling Stability` ✓
- `BTC / Market Regime Diagnostics` ✓
- `不是交易策略` ✓

## HTML Size

- **Before:** 2,704,496 bytes (2.70 MB)
- **After:** 2,839,007 bytes (2.84 MB)
- **Delta:** +134,511 bytes (+134 KB)
- **Limit:** 4,500,000 bytes (4.50 MB) — **PASS**

## Files Modified

- `scripts/_build_factor_eval_html.py` — Added data loading, lookup maps, per-factor merging, summary stats, CSS badges, HTML section divs, JS label maps, JS summary IIFE, JS detail rendering
- `reports/site/factor-library/factor-evaluation.html` — Rebuilt with unified profile sections

## Files Created

- `docs/factor_library/audits/pm33_unified_profile_page_workflow_readiness.md` — This audit

## Limitations

1. Evidence matrix shows 15 has_* blocks (not 16 as originally estimated — the data has 15 distinct evidence block fields).
2. Component weights are displayed as percentage badges, not as a weighted-average decomposition chart (kept compact for size).
3. Source lineage uses pipe-delimited string from the profile summary CSV rather than a nested list (compact encoding).

## Recommended Next PM

**PM-34:** Add interactive profile class filter to the factor scoreboard table, allowing users to filter by BROAD_WATCHLIST / PROMISING_BUT_REGIME_DEPENDENT / UNIQUE_BUT_WEAK and by workflow_ready_status / evidence_status columns.
