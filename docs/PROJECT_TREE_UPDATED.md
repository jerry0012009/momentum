# Project Tree — Updated for Phase 12D

**Last Updated:** 2026-06-17
**Phase:** 12D-A (Repository Map & File Ownership Audit)

> This replaces the old Phase 2C `PROJECT_TREE.md`. That file is preserved for historical reference.

```text
jerry/momentum/
│
├─ config/                              # Pipeline configuration (human-editable, git-tracked)
│  ├─ base.yaml                         # Base config
│  ├─ env/                              # Environment configs
│  │  ├─ backtest.yaml
│  │  ├─ paper.yaml
│  │  └─ live.yaml
│  ├─ execution/                        # Execution configs (slippage, spread, cost models)
│  ├─ features/                         # Feature computation configs
│  │  └─ chip_distribution.yaml
│  ├─ markets/                          # Market universe configs
│  │  ├─ crypto.yaml
│  │  ├─ a_share.yaml
│  │  ├─ us_equity.yaml
│  │  └─ gold.yaml
│  ├─ private/                          # Private/API configs (not committed)
│  ├─ signals/                          # Signal construction configs
│  │  └─ up_down_wave.yaml
│  └─ strategies/                       # Strategy configs
│     └─ trend_momentum_v1.yaml
│
├─ data/                                # Generated/cached data (do NOT edit manually)
│  ├─ binance_funding_rate/             # Funding rate data (538 symbol dirs)
│  ├─ binance_vision_1h_sample/         # Sample OHLCV data
│  ├─ binance_vision_1h_v1_6/           # v1.6 OHLCV dataset
│  ├─ binance_vision_rank154/           # Rank154 specific data
│  ├─ bronze/                           # Cleaning intermediate
│  ├─ cache/                            # Universe data cache (bars, manifest)
│  │  └─ crypto_top50_usdt_perp_1h/
│  │     ├─ bars_1h.parquet
│  │     ├─ manifest.json
│  │     └─ universe_membership.parquet
│  ├─ features/                         # Factor values and labels (generated)
│  │  └─ crypto_top50_usdt_perp_1h/
│  │     ├─ labels.parquet
│  │     ├─ atr_14h/factor_values.parquet
│  │     ├─ bb_zscore_20h/factor_values.parquet
│  │     ├─ mom_20h/factor_values.parquet
│  │     ├─ reversal_5h/factor_values.parquet
│  │     ├─ rsi_14h/factor_values.parquet
│  │     └─ volatility_20h/factor_values.parquet
│  ├─ paper_snapshots/                  # Paper trading snapshots
│  ├─ raw/                              # Raw data (not committed)
│  ├─ silver/                           # Standardized data
│  └─ universe/                         # Universe definitions (generated)
│
├─ docs/                                # Human-readable documentation (git-tracked)
│  │
│  │  # ── Factor Library Entry Point ──
│  ├─ FACTOR_LIBRARY_HOME.md            # ← NEW: Factor library navigation hub
│  │
│  │  # ── Navigation & Roadmap ──
│  ├─ DOCS_INDEX.md                     # Documentation entry point
│  ├─ FACTOR_LIBRARY_ROADMAP.md         # Phase 0–10 roadmap (authoritative)
│  ├─ TODO.md                           # Current project board
│  ├─ ARCHITECTURE.md                   # Project architecture overview
│  ├─ PROJECT_TREE.md                   # Old Phase 2C tree (historical)
│  ├─ PROJECT_TREE_UPDATED.md           # ← NEW: This file (Phase 12D)
│  │
│  │  # ── Factor Library Core ──
│  ├─ FACTOR_LIBRARY_SKELETON.md        # Factor schema, interface, protocol
│  ├─ FACTOR_LIBRARY_DESIGN.md          # Design rationale, universe, labels
│  ├─ FACTOR_REGISTRY.md                # Factor definitions and status
│  ├─ FACTOR_EVALUATION_STANDARD.md     # Evaluation criteria
│  ├─ FACTOR_BACKLOG.md                 # Factor research queue
│  ├─ CANDIDATE_FACTOR_POOL.md          # Candidate factor ideas
│  ├─ CRYPTO_FACTOR_PIPELINE_RUNBOOK.md # Pipeline execution guide
│  │
│  │  # ── Audit & Quality Control ──
│  ├─ AUDITABLE_FACTOR_RESEARCH_SKILL.md
│  ├─ RESEARCH_LIFECYCLE.md
│  ├─ CODE_TRUST_MAP.md
│  ├─ BACKTEST_HONESTY_CHECKLIST.md
│  ├─ DATA_CONTRACT.md
│  │
│  │  # ── Transparency Documentation (Phase 12C) ──
│  ├─ factor_library_transparency/      # ← Phase 12C transparency docs
│  │  ├─ README.md                      # Overview and navigation
│  │  ├─ index.html                     # HTML entry point
│  │  ├─ factor_handbook.md             # Factor definitions and families
│  │  ├─ signal_construction_handbook.md # Signal building from factors
│  │  ├─ evaluation_methodology.md      # Evaluation methodology
│  │  ├─ data_lineage.md               # Data source and flow
│  │  ├─ workflow_map.md               # End-to-end workflow
│  │  ├─ phase_decision_log.md         # PM decisions across phases
│  │  ├─ phase_summary_table.csv       # Phase summary data
│  │  ├─ pm_decision_memo_phase13_readiness.md  # Phase 13 readiness
│  │  ├─ phase13_readiness_checklist.csv
│  │  └─ risk_register.csv             # Known risks
│  │
│  │  # ── Legacy Strategy & Signal Docs ──
│  ├─ STRATEGY_SPEC.md
│  ├─ SIGNAL_PIPELINE.md
│  ├─ SIGNALS_*.md                      # (10 signal docs)
│  ├─ MAINLINE1_STRATEGY_FACTOR_MAP.md
│  ├─ BACKTEST_WAVE_HOLD.md
│  ├─ BACKTEST_VS_LIVE_EXPLAINER.md
│  ├─ SINGLE_FACTOR_REPORT_TEMPLATE.md
│  ├─ FOUNDATION_KERNEL_EXTREMA.md
│  ├─ RESEARCH_PYTRENDLINE.md
│  ├─ CHIP_DISTRIBUTION.md
│  │
│  │  # ── Historical & Supporting ──
│  ├─ ROADMAP.md                        # Early M1-M5 roadmap (superseded)
│  ├─ LEARNING_TRACK.md
│  ├─ PHASE2A_CHANGELOG.md
│  ├─ PHASE2A_PAPER_TRADING_PLAN.md
│  ├─ REPORTING_WEB.md
│  ├─ AUTO_OPTIMIZATION_LOOP.md
│  │
│  │  # ── Bot / Rank Operational Docs ──
│  ├─ BOT2_BOT3_OPERATING_CARD.md
│  ├─ BOT2_BOT3_POLICY.md
│  ├─ BOT2_BOT3_STATE.md
│  ├─ CANARY_32B_PHASE*.md
│  ├─ RANK154_ARCHIVE_CLOSEOUT.md
│  ├─ RANK213_ARCHIVE_CLOSEOUT.md
│  └─ RANK213_EVIDENCE_MAP.md
│
├─ research/                            # Research artifacts
│  ├─ factor_runs/
│  │  ├─ _TEMPLATE/                     # Standard audit dossier template
│  │  └─ crypto_top50_factor_library/   # ← PRIMARY: Current active run (273 files)
│  │     │
│  │     │  # ── Phase Plans & Closeouts ──
│  │     ├─ PHASE_2B_CLOSEOUT.md
│  │     ├─ PHASE_2C_PLAN.md / PHASE_2C_CLOSEOUT.md
│  │     ├─ PHASE_2D_PLAN.md / PHASE_2D_REVIEW.md
│  │     ├─ PHASE_2E_PLAN.md / PHASE_2E_CLOSEOUT.md
│  │     ├─ PHASE_3_PLAN.md / PHASE_3_DATA_VALIDATION.md
│  │     ├─ PHASE_4_FACTOR_FACTORY_V1.md
│  │     ├─ PHASE_5_ALPHALENS_EXPORT.md / PHASE_5B_*.md
│  │     ├─ PHASE_6*_*.md               # Dynamic universe phases
│  │     ├─ PHASE_7*_*.md               # Factor mining & curation
│  │     ├─ PHASE_8*_*.md               # Human review
│  │     ├─ PHASE_9*_*.md               # Signal design
│  │     ├─ PHASE_10*_*.md              # Diagnostics & tail-aware
│  │     ├─ PHASE_11*_*.md              # Cost & liquidity
│  │     ├─ PHASE_12A_*.md              # Paper signal harness
│  │     ├─ PHASE_12B_*.md              # Paper monitoring diagnostic
│  │     ├─ PHASE_12C_*.md              # Grand transparency closeout
│  │     │
│  │     │  # ── Generated Evaluation Data ──
│  │     ├─ phase*_*.csv                # Evaluation CSVs (generated)
│  │     ├─ phase9b_signal_panel.parquet # Signal panel (generated)
│  │     │
│  │     │  # ── Audit Artifacts ──
│  │     ├─ alphalens_exports/          # Alphalens tear sheets
│  │     ├─ audit_v0/ audit_v0_1/      # Audit outputs
│  │     ├─ batch_v0_1/                 # Batch evaluation
│  │     ├─ warning_flags/              # Factor warning flags
│  │     │
│  │     │  # ── Summaries ──
│  │     ├─ result_summary.md
│  │     ├─ pipeline_plan.md
│  │     └─ result_summary_*.md
│  │
│  ├─ deep_dives/                       # Deep dive research
│  ├─ optimization_loop/                # Optimization experiments
│  ├─ park_reframe/                     # Park/reframe queue
│  ├─ quant_digests/                    # Quant digests
│  └─ strategy_review/                  # Strategy reviews
│
├─ scripts/                             # Reproducible generation logic (601 files, git-tracked)
│  ├─ README.md
│  ├─ fetch_crypto_top50_bars.py        # Fetch OHLCV from Binance
│  ├─ build_crypto_top50_universe.py    # Build universe definition
│  ├─ build_labels.py                   # Calendar-time forward returns
│  ├─ build_factor_values.py            # Compute all registered factors
│  ├─ evaluate_factors.py               # IC/spread/turnover evaluation
│  ├─ audit_crypto_factor_results.py    # Audit factor results
│  ├─ analyze_factor_redundancy.py      # Factor redundancy analysis
│  ├─ apply_factor_warning_flags.py     # Apply warning flags
│  ├─ build_showcase_workflow_page.py   # Generate showcase pages
│  ├─ build_interview_showcase.py       # Interview showcase
│  └─ ... (590+ more scripts)
│
├─ src/momentum/                        # Reusable Python package (git-tracked)
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ analytics/                        # Analytics modules
│  ├─ data/                             # Data handling
│  ├─ domain/                           # Domain models
│  ├─ engines/                          # Backtest engines
│  ├─ execution/                        # Execution logic
│  ├─ factors/                          # Factor computation modules
│  ├─ html_render.py                    # HTML report rendering
│  ├─ portfolio/                        # Portfolio construction
│  ├─ risk/                             # Risk management
│  ├─ signals/                          # Signal construction
│  ├─ strategies/                       # Strategy implementations
│  └─ utils/                            # Utilities
│
├─ tests/                               # Test suite (git-tracked)
│  ├─ unit/                             # Unit tests (65+ test files)
│  │  ├─ test_phase7*.py                # Factor library tests (14 files)
│  │  ├─ test_phase8*.py                # Review tests (2 files)
│  │  ├─ test_phase9*.py                # Signal tests (2 files)
│  │  ├─ test_phase10*.py               # Diagnostics tests (5 files)
│  │  ├─ test_phase11*.py               # Cost/liquidity tests (2 files)
│  │  ├─ test_phase12*.py               # Paper/transparency tests (3 files)
│  │  ├─ test_crypto_factor_*.py        # Core factor tests
│  │  └─ test_*_backtest.py             # Backtest tests
│  ├─ integration/                      # Integration tests
│  └─ regression/                       # Regression tests
│
├─ reports/                             # Generated reports and site output
│  ├─ artifacts/                        # Evaluation artifacts (generated)
│  │  └─ factor_eval/
│  │     └─ crypto_top50_usdt_perp_1h/
│  │        ├─ mom_20h/
│  │        ├─ reversal_5h/
│  │        └─ ...
│  ├─ archive/                          # Archived reports
│  ├─ reports/                          # Other reports
│  └─ site/                             # Static website root
│     ├─ index.html                     # Main site entry
│     ├─ factors/                       # Per-rank factor reports (247 dirs)
│     ├─ factor_research_library/       # Factor research library
│     ├─ factor-library/                # ← NEW: Factor library showcase
│     │  ├─ index.html                  # Showcase homepage
│     │  ├─ repository-map.html         # ← NEW: Repository map page
│     │  ├─ file-ownership.html         # ← NEW: File ownership page
│     │  └─ assets/
│     │     └─ repo_map.json            # ← NEW: Repo map data
│     ├─ paper/                         # Paper trading reports
│     ├─ phases/                        # Phase reports
│     ├─ plans/                         # Plan reports
│     └─ reading/                       # Reading/research reports
│
├─ pm_prompts/                          # PM review prompts (git-tracked)
│  └─ phase10d_tail_aware_signal_variant_evaluation_prompt.txt
│
├─ notebooks/                           # Jupyter notebooks
├─ diary/                               # Research diary
├─ logs/                                # Execution logs
├─ ops/                                 # Operations (cron, systemd, mobile-ui)
├─ outputs/                             # Output artifacts
└─ tmp/                                 # Temporary working dirs
```

---

## Key Differences from Old PROJECT_TREE.md

| Aspect | Old (Phase 2C) | New (Phase 12D) |
|--------|----------------|-----------------|
| Factor library | 5 factors, DIAGNOSTIC_PROBE | Candidate frozen, 273 research files |
| Research phases | Phase 2C | Phase 12D-A |
| Transparency docs | None | `docs/factor_library_transparency/` (12 files) |
| Showcase site | None | `reports/site/factor-library/` |
| Test files | 3 | 65+ |
| Scripts | ~10 | 601 |
| Signal design | None | Phase 9 signal basket |
| Paper monitoring | None | Phase 12A-B harness |

---

## Navigation

- **Factor library entry:** `docs/FACTOR_LIBRARY_HOME.md`
- **Full doc index:** `docs/DOCS_INDEX.md`
- **Factor registry:** `docs/FACTOR_REGISTRY.md`
- **Research dossier:** `research/factor_runs/crypto_top50_factor_library/`
- **Showcase website:** `reports/site/factor-library/`
