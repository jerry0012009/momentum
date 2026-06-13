# Documentation Index

> This is the entry point for all project documentation.
>
> Last updated: 2026-06-13 (Phase 2D start)

---

## How to Read This Project

**New reader?** Start here:

1. `docs/FACTOR_LIBRARY_ROADMAP.md` — where the project is going (Phase 0–10)
2. `docs/FACTOR_LIBRARY_SKELETON.md` — how the factor library works
3. `docs/FACTOR_REGISTRY.md` — what factors exist and their status
4. This file (`DOCS_INDEX.md`) — find anything else you need

**Current mainline:** Phase 2D (External Factor Priors). The project is building a crypto factor library, not a trading strategy.

---

## A. Start Here / 当前主线入口

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/FACTOR_LIBRARY_ROADMAP.md` | ACTIVE | Phase 0–10 roadmap; current status of each phase | **First.** Understand where the project is and where it's going. |
| `docs/FACTOR_LIBRARY_SKELETON.md` | ACTIVE | Factor catalog schema, implementation interface, evaluation protocol, test requirements, promotion rules | **Second.** Understand how factors enter the library. |
| `docs/FACTOR_REGISTRY.md` | ACTIVE | Factor definitions, status enum, universe spec | **Third.** See what factors exist and their status. |
| `docs/FACTOR_LIBRARY_DESIGN.md` | ACTIVE | Original design doc: what the library is, universe, labels, data policy | When you need the design rationale. |
| `docs/DOCS_INDEX.md` | ACTIVE | This file — documentation navigation | When you need to find a specific doc. |

---

## B. Factor Library Core / 因子库核心

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/FACTOR_LIBRARY_ROADMAP.md` | ACTIVE | Phase 0–10 roadmap | Always read first. |
| `docs/FACTOR_LIBRARY_SKELETON.md` | ACTIVE | Batch onboarding scaffold: schema, interface, protocol | When adding or reviewing factors. |
| `docs/FACTOR_REGISTRY.md` | ACTIVE | Factor definitions and status table | When checking factor status. |
| `docs/FACTOR_LIBRARY_DESIGN.md` | ACTIVE | Design rationale, universe, labels, data policy | When understanding design decisions. |
| `docs/FACTOR_EVALUATION_STANDARD.md` | ACTIVE | Evaluation criteria and thresholds | When reviewing evaluation results. |
| `docs/FACTOR_BACKLOG.md` | SUPPORTING | Factor research queue and priorities | When planning future factor work. |
| `docs/CANDIDATE_FACTOR_POOL.md` | SUPPORTING | Candidate factor ideas pool | When brainstorming new factors. |
| `docs/CRYPTO_FACTOR_PIPELINE_RUNBOOK.md` | ACTIVE | Step-by-step pipeline execution guide | When running the pipeline. |
| `docs/EXTERNAL_FACTOR_PRIORS.md` | ACTIVE | External factor prior families: WQ101, GTJA191, Alpha158, technical, crypto-native | When exploring factor sources for Phase 2D+. |
| `docs/CRYPTO_FACTOR_PRIOR_MAPPING.md` | ACTIVE | Maps external factors to crypto availability buckets (A–G) | When assessing which external factors are implementable. |

---

## C. Audit and Quality Control / 审计与质量控制

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/AUDITABLE_FACTOR_RESEARCH_SKILL.md` | ACTIVE | Minimum standard for auditable research assets | Before starting any research. |
| `docs/RESEARCH_LIFECYCLE.md` | ACTIVE | Research asset lifecycle: from idea to deployment | When understanding research workflow. |
| `docs/CODE_TRUST_MAP.md` | ACTIVE | File-level code trust classification | When assessing code reliability. |
| `docs/BACKTEST_HONESTY_CHECKLIST.md` | ACTIVE | Checklist for backtest integrity | Before claiming any backtest result. |
| `docs/FACTOR_EVALUATION_STANDARD.md` | ACTIVE | Evaluation criteria and metric definitions | When interpreting evaluation results. |
| `docs/DATA_CONTRACT.md` | SUPPORTING | Data schema and quality requirements | When working with data pipelines. |

---

## D. Current Research Dossier / 当前研究卷宗

These documents belong to the active `crypto_top50_factor_library` research run.

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `research/.../PHASE_2C_CLOSEOUT.md` | CURRENT_RUN | Phase 2C closeout report | Reviewing Phase 2C deliverables. |
| `research/.../PHASE_2C_PLAN.md` | CURRENT_RUN | Phase 2C scope, allowed/forbidden actions | Understanding Phase 2C boundaries. |
| `research/.../PHASE_2B_CLOSEOUT.md` | CURRENT_RUN | Phase 2B closeout (lightweight quality gate) | Reviewing Phase 2B audit results. |
| `research/.../result_summary.md` | CURRENT_RUN | Master evaluation summary (5 factors × 4 labels) | Checking evaluation metrics. |
| `research/.../data_validation_report.md` | CURRENT_RUN | Data validation: symbols, bars, missing rates | Checking data quality. |
| `research/.../pipeline_plan.md` | CURRENT_RUN | Pipeline planning and Phase 2B fix log | Understanding pipeline evolution. |
| `research/.../factor_catalog_v0_1.csv` | CURRENT_RUN | Official 5-factor catalog (12-column schema) | Reference for factor definitions. |
| `research/.../experimental_catalog_v0_1.csv` | CURRENT_RUN | 19 exploratory factors (NOT official) | When reviewing experimental factors. |
| `research/.../local_artifact_index.md` | CURRENT_RUN | Local artifact file index | Finding generated artifacts. |
| `research/.../PHASE_2D_PLAN.md` | CURRENT_RUN | Phase 2D scope, allowed/forbidden actions | Understanding Phase 2D boundaries. |
| `research/.../external_factor_prior_table.csv` | CURRENT_RUN | 56 prior records across 5 source families | Reference for external factor candidates. |
| `research/.../PHASE_2D_REVIEW.md` | CURRENT_RUN | Phase 2D review: shortlist, park, skip decisions | Reviewing Phase 2D deliverables. |
| `research/.../phase_2e_candidate_shortlist.csv` | CURRENT_RUN | 16 shortlisted candidates for Phase 2E | Planning Phase 2E implementation. |
| `research/.../PHASE_2E_PLAN.md` | CURRENT_RUN | Phase 2E scope, batch definitions, status policy | Understanding Phase 2E structure. |
| `research/.../phase_2e_batch1_spec.md` | CURRENT_RUN | Batch 1 formula specs (6 direct_formula factors) | Implementing Batch 1 factors. |
| `research/.../phase_2e_batch1_candidates.csv` | CURRENT_RUN | Batch 1 candidate table (6 factors, PLANNED_ONLY) | Reference for Batch 1 scope. |
| `research/.../PHASE_2E1_A_IMPLEMENTATION.md` | CURRENT_RUN | Batch 1 impl closeout: 6 functions, 30 tests | Review implementation quality |
| `research/.../PHASE_2E_BATCH1_EVALUATION.md` | CURRENT_RUN | Batch 1 evaluation: 11 factors, metrics, status decisions | Review evaluation results |
| `research/.../PHASE_2E_CLOSEOUT.md` | CURRENT_RUN | Phase 2E closeout: 11 factors evaluated, all DIAGNOSTIC_PROBE | Review Phase 2E completion |
| `research/.../PHASE_3_PLAN.md` | CURRENT_RUN | Phase 3 V1 Long-window Baseline plan | Planning Phase 3 data extension |
| `research/.../PHASE_3_DATA_VALIDATION.md` | CURRENT_RUN | Long-window data validation: 50 symbols, 721K rows, 2yr | Review data quality before Phase 3 pipeline |

Path prefix: `research/factor_runs/crypto_top50_factor_library/`

---

## E. Legacy Strategy and Signal Docs / 旧策略与信号参考

These documents relate to older strategy/signal work. They are NOT part of the current factor library mainline.

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/STRATEGY_SPEC.md` | LEGACY_REFERENCE | M1 strategy specification | Reference for old strategy design. |
| `docs/SIGNAL_PIPELINE.md` | LEGACY_REFERENCE | Signal pipeline maintenance guide | Reference for old signal flow. |
| `docs/SIGNALS_BOX_CONSOLIDATION.md` | LEGACY_REFERENCE | Box consolidation signal design | Reference for old signal. |
| `docs/SIGNALS_EMA_DONCHIAN_BREAKOUT.md` | LEGACY_REFERENCE | EMA Donchian breakout signal | Reference for old signal. |
| `docs/SIGNALS_MARKET_RISK_ON_OFF_FILTER.md` | LEGACY_REFERENCE | Market risk on/off filter | Reference for old signal. |
| `docs/SIGNALS_MULTI_TF_MOMENTUM.md` | LEGACY_REFERENCE | Multi-timeframe momentum signal | Reference for old signal. |
| `docs/SIGNALS_PRICE_VOLUME_DIVERGENCE.md` | LEGACY_REFERENCE | Price-volume divergence signal | Reference for old signal. |
| `docs/SIGNALS_PULLBACK_RECOVERY_CONFIRMATION.md` | LEGACY_REFERENCE | Pullback recovery signal | Reference for old signal. |
| `docs/SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md` | LEGACY_REFERENCE | Trendline breakout navigator | Reference for old signal. |
| `docs/SIGNALS_TREND_REGIME_FILTER.md` | LEGACY_REFERENCE | Trend regime filter | Reference for old signal. |
| `docs/SIGNALS_UP_DOWN_WAVE.md` | LEGACY_REFERENCE | Up/down wave signal | Reference for old signal. |
| `docs/MAINLINE1_STRATEGY_FACTOR_MAP.md` | LEGACY_REFERENCE | Mainline1 strategy-factor mapping | Reference for old strategy. |
| `docs/BACKTEST_WAVE_HOLD.md` | LEGACY_REFERENCE | Wave hold backtest design | Reference for old backtest. |
| `docs/BACKTEST_VS_LIVE_EXPLAINER.md` | LEGACY_REFERENCE | Backtest vs live differences | When understanding old backtest caveats. |
| `docs/SINGLE_FACTOR_REPORT_TEMPLATE.md` | LEGACY_REFERENCE | Single factor report template | When generating factor reports. |
| `docs/FOUNDATION_KERNEL_EXTREMA.md` | LEGACY_REFERENCE | Kernel extrema foundation research | Reference for old research. |
| `docs/RESEARCH_PYTRENDLINE.md` | LEGACY_REFERENCE | PyTrendline research notes | Reference for old research. |
| `docs/RESEARCH_TRENDLINE_EVENT.md` | LEGACY_REFERENCE | Trendline event research | Reference for old research. |
| `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` | LEGACY_REFERENCE | Trendline confirmation protocol | Reference for old research. |
| `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` | LEGACY_REFERENCE | Literature trendline signal mapping | Reference for old research. |
| `docs/CHIP_DISTRIBUTION.md` | LEGACY_REFERENCE | Chip distribution analysis | Reference for old research. |

---

## F. Historical or Supporting Docs / 历史与支持文档

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/ARCHITECTURE.md` | HISTORICAL | Project architecture overview | When understanding project structure. |
| `docs/ROADMAP.md` | HISTORICAL | Early engineering roadmap (M1–M5) | Historical reference only; superseded by `FACTOR_LIBRARY_ROADMAP.md`. |
| `docs/LEARNING_TRACK.md` | HISTORICAL | Learning notes and track record | When reviewing learning history. |
| `docs/TODO.md` | SUPPORTING | Current human-readable project board | When checking current tasks. |
| `docs/TODO_ARCHIVE_2026-03-24.md` | HISTORICAL | Archived TODO from March 2026 | Historical reference. |
| `docs/PHASE2A_CHANGELOG.md` | HISTORICAL | Phase 2a V4 Trail parameter change log | When reviewing old parameter changes. |
| `docs/PHASE2A_PAPER_TRADING_PLAN.md` | HISTORICAL | Phase 2a paper trading plan | When reviewing old paper trading design. |
| `docs/MANUAL_NARROW_PAPER_LANES.md` | HISTORICAL | Manual narrow paper lanes design | When reviewing old paper lane design. |
| `docs/RECENT_PAPER_SEEDS.md` | HISTORICAL | Paper seed list for research tasks | When looking for research seeds. |
| `docs/REPORTING_WEB.md` | SUPPORTING | Report web publishing guide | When publishing reports. |
| `docs/REPORT_PIPELINE_REFACTOR.md` | SUPPORTING | Report pipeline refactoring notes | When working on report pipeline. |
| `docs/RESEARCH_AUTOMATION_BRIEF.md` | SUPPORTING | Research automation brief | When setting up automation. |
| `docs/AUTO_OPTIMIZATION_LOOP.md` | SUPPORTING | Auto-optimization loop design | When working on optimization. |
| `docs/MAINTENANCE.md` | SUPPORTING | Maintenance procedures | When doing maintenance. |
| `docs/CROSS_ENGINE_MAPPING.md` | SUPPORTING | Cross-engine mapping reference | When mapping across engines. |
| `docs/DATASET_XIAOMI_HK.md` | HISTORICAL | Xiaomi HK dataset notes | When referencing old dataset. |

---

## G. Do Not Read First / 不建议优先阅读

These are operational docs for specific bots, canary phases, or archived rank closeouts. Only read if you need specific operational context.

| File | Status | Purpose | Read when |
|------|--------|---------|-----------|
| `docs/BOT2_BOT3_OPERATING_CARD.md` | DO_NOT_READ_FIRST | Bot2/Bot3 operating card | Only if working with bot2/bot3. |
| `docs/BOT2_BOT3_POLICY.md` | DO_NOT_READ_FIRST | Bot2/Bot3 policy | Only if working with bot2/bot3. |
| `docs/BOT2_BOT3_STATE.md` | DO_NOT_READ_FIRST | Bot2/Bot3 state | Only if working with bot2/bot3. |
| `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` | DO_NOT_READ_FIRST | Bot2 strategy review brief | Only if reviewing bot2 strategy. |
| `docs/BOT6_PARK_REFRAME_BRIEF.md` | DO_NOT_READ_FIRST | Bot6 park reframe brief | Only if working with bot6. |
| `docs/CANARY_32B_PHASE1.md` through `PHASE6.md` | DO_NOT_READ_FIRST | Canary 32B phase docs | Only if working on canary 32B. |
| `docs/CANARY_32B_TODO.md` | DO_NOT_READ_FIRST | Canary 32B TODO | Only if working on canary 32B. |
| `docs/PARK_REFRAME_QUEUE.md` | DO_NOT_READ_FIRST | Park reframe queue | Only if managing park queue. |
| `docs/RANK154_ARCHIVE_CLOSEOUT.md` | DO_NOT_READ_FIRST | Rank154 archive closeout | Only if referencing rank154. |
| `docs/RANK154_DAILY_PAPER_RUNNER.md` | DO_NOT_READ_FIRST | Rank154 daily paper runner | Only if referencing rank154. |
| `docs/RANK213_ARCHIVE_CLOSEOUT.md` | DO_NOT_READ_FIRST | Rank213 archive closeout | Only if referencing rank213. |
| `docs/RANK213_EVIDENCE_MAP.md` | DO_NOT_READ_FIRST | Rank213 evidence map | Only if referencing rank213. |
| `docs/RANK29_POSTMORTEM_2026-04.md` | DO_NOT_READ_FIRST | Rank29 postmortem | Only if referencing rank29. |
| `docs/RANK29_SHADOWS.md` | DO_NOT_READ_FIRST | Rank29 shadows | Only if referencing rank29. |
| `docs/RANK32B_WARMUP_CAUSAL_AUDIT_2026-04-07.md` | DO_NOT_READ_FIRST | Rank32B warmup causal audit | Only if referencing rank32B. |
| `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt` | DO_NOT_READ_FIRST | Auto-optimization cron prompt | Only if configuring cron. |
| `docs/BOT7_QUANT_DIGEST_CRON_PROMPT.txt` | DO_NOT_READ_FIRST | Bot7 quant digest cron prompt | Only if configuring cron. |

---

## Status Legend

| Status | Meaning |
|--------|---------|
| `ACTIVE` | Part of current mainline. Read for understanding the project. |
| `SUPPORTING` | Useful reference, not core path. Read as needed. |
| `CURRENT_RUN` | Belongs to the active `crypto_top50_factor_library` research run. |
| `LEGACY_REFERENCE` | Old strategy/signal work. Not current mainline. Useful for historical context. |
| `HISTORICAL` | Superseded by newer docs. Kept for record. |
| `DO_NOT_READ_FIRST` | Operational docs for specific bots/ranks. Only read if you need that context. |
