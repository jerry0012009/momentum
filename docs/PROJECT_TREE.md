# Project Tree

```text
jerry/momentum/
├─ config/
│  ├─ base.yaml
│  ├─ env/
│  │  ├─ backtest.yaml
│  │  ├─ paper.yaml
│  │  └─ live.yaml
│  ├─ markets/
│  │  ├─ crypto.yaml
│  │  ├─ a_share.yaml
│  │  ├─ us_equity.yaml
│  │  └─ gold.yaml
│  ├─ strategies/
│  │  └─ trend_momentum_v1.yaml
│  ├─ features/
│  │  └─ chip_distribution.yaml
│  └─ signals/
│     ├─ up_down_wave.yaml
│     └─ box_consolidation.yaml
├─ data/
│  ├─ cache/                # universe data cache (bars, manifest)
│  │  └─ crypto_top50_usdt_perp_1h/
│  │     ├─ bars_1h.parquet
│  │     └─ manifest.json
│  ├─ features/             # factor values and labels
│  │  └─ crypto_top50_usdt_perp_1h/
│  │     ├─ labels.parquet
│  │     ├─ mom_20h/factor_values.parquet
│  │     ├─ reversal_5h/factor_values.parquet
│  │     ├─ volatility_20h/factor_values.parquet
│  │     ├─ rsi_14h/factor_values.parquet
│  │     └─ bb_zscore_20h/factor_values.parquet
│  ├─ raw/                  # raw data (not committed)
│  ├─ bronze/               # cleaning intermediate
│  └─ silver/               # standardized data
├─ docs/
│  │
│  │  # ── Navigation & Roadmap ──
│  ├─ DOCS_INDEX.md              # documentation entry point
│  ├─ FACTOR_LIBRARY_ROADMAP.md  # Phase 0–10 roadmap (authoritative)
│  ├─ TODO.md                    # current project board
│  ├─ ARCHITECTURE.md            # project architecture overview
│  │
│  │  # ── Factor Library Core ──
│  ├─ FACTOR_LIBRARY_SKELETON.md # factor schema, interface, protocol
│  ├─ FACTOR_LIBRARY_DESIGN.md   # design rationale, universe, labels
│  ├─ FACTOR_REGISTRY.md         # factor definitions and status
│  ├─ FACTOR_EVALUATION_STANDARD.md # evaluation criteria
│  ├─ FACTOR_BACKLOG.md          # factor research queue
│  ├─ CANDIDATE_FACTOR_POOL.md   # candidate factor ideas
│  ├─ CRYPTO_FACTOR_PIPELINE_RUNBOOK.md # pipeline execution guide
│  │
│  │  # ── Audit & Quality Control ──
│  ├─ AUDITABLE_FACTOR_RESEARCH_SKILL.md
│  ├─ RESEARCH_LIFECYCLE.md
│  ├─ CODE_TRUST_MAP.md
│  ├─ BACKTEST_HONESTY_CHECKLIST.md
│  ├─ DATA_CONTRACT.md
│  │
│  │  # ── Legacy Strategy & Signal Docs ──
│  ├─ STRATEGY_SPEC.md
│  ├─ SIGNAL_PIPELINE.md
│  ├─ SIGNALS_*.md               # (10 signal docs)
│  ├─ MAINLINE1_STRATEGY_FACTOR_MAP.md
│  ├─ BACKTEST_WAVE_HOLD.md
│  ├─ BACKTEST_VS_LIVE_EXPLAINER.md
│  ├─ SINGLE_FACTOR_REPORT_TEMPLATE.md
│  ├─ FOUNDATION_KERNEL_EXTREMA.md
│  ├─ RESEARCH_PYTRENDLINE.md
│  ├─ RESEARCH_TRENDLINE_EVENT.md
│  ├─ TRENDLINE_CONFIRMATION_PROTOCOL.md
│  ├─ LITERATURE_TRENDLINE_SIGNAL_MAP.md
│  ├─ CHIP_DISTRIBUTION.md
│  │
│  │  # ── Historical & Supporting ──
│  ├─ ROADMAP.md                 # early M1-M5 roadmap (superseded)
│  ├─ LEARNING_TRACK.md
│  ├─ PHASE2A_CHANGELOG.md
│  ├─ PHASE2A_PAPER_TRADING_PLAN.md
│  ├─ MANUAL_NARROW_PAPER_LANES.md
│  ├─ RECENT_PAPER_SEEDS.md
│  ├─ REPORTING_WEB.md
│  ├─ REPORT_PIPELINE_REFACTOR.md
│  ├─ RESEARCH_AUTOMATION_BRIEF.md
│  ├─ AUTO_OPTIMIZATION_LOOP.md
│  ├─ MAINTENANCE.md
│  ├─ CROSS_ENGINE_MAPPING.md
│  ├─ DATASET_XIAOMI_HK.md
│  │
│  │  # ── Bot / Rank Operational Docs ──
│  ├─ BOT2_BOT3_OPERATING_CARD.md
│  ├─ BOT2_BOT3_POLICY.md
│  ├─ BOT2_BOT3_STATE.md
│  ├─ BOT2_STRATEGY_REVIEW_BRIEF.md
│  ├─ BOT6_PARK_REFRAME_BRIEF.md
│  ├─ BOT7_QUANT_DIGEST_CRON_PROMPT.txt
│  ├─ CANARY_32B_PHASE*.md
│  ├─ CANARY_32B_TODO.md
│  ├─ PARK_REFRAME_QUEUE.md
│  ├─ RANK154_ARCHIVE_CLOSEOUT.md
│  ├─ RANK154_DAILY_PAPER_RUNNER.md
│  ├─ RANK213_ARCHIVE_CLOSEOUT.md
│  ├─ RANK213_EVIDENCE_MAP.md
│  ├─ RANK29_POSTMORTEM_2026-04.md
│  ├─ RANK29_SHADOWS.md
│  ├─ RANK32B_WARMUP_CAUSAL_AUDIT_2026-04-07.md
│  └─ PROJECT_TREE.md
│
├─ reports/
│  ├─ artifacts/
│  │  └─ factor_eval/
│  │     └─ crypto_top50_usdt_perp_1h/
│  │        ├─ mom_20h/         # metrics.json, result_summary.md
│  │        ├─ reversal_5h/
│  │        ├─ volatility_20h/
│  │        ├─ rsi_14h/
│  │        └─ bb_zscore_20h/
│  └─ site/
│
├─ research/
│  ├─ factor_runs/
│  │  ├─ _TEMPLATE/             # standard audit dossier template
│  │  ├─ rank444_rsi_bb_v0/    # legacy rank444 dossier
│  │  └─ crypto_top50_factor_library/  # ← current active run
│  │     ├─ PHASE_2B_CLOSEOUT.md
│  │     ├─ PHASE_2C_PLAN.md
│  │     ├─ PHASE_2C_CLOSEOUT.md
│  │     ├─ result_summary.md
│  │     ├─ data_validation_report.md
│  │     ├─ pipeline_plan.md
│  │     ├─ factor_catalog_v0_1.csv
│  │     ├─ experimental_catalog_v0_1.csv
│  │     └─ local_artifact_index.md
│  └─ quant_digests/
│
├─ scripts/
│  ├─ fetch_crypto_top50_bars.py      # fetch OHLCV from Binance
│  ├─ build_crypto_top50_universe.py  # build universe definition
│  ├─ build_labels.py                 # calendar-time forward returns
│  ├─ build_factor_values.py          # compute all registered factors
│  ├─ evaluate_factors.py             # IC/spread/turnover evaluation
│  └─ publish_report_site.sh          # publish static report site
│
├─ src/momentum/
│  ├─ domain/ data/ factors/ signals/ risk/
│  ├─ portfolio/ engines/ execution/ analytics/ utils/
│  └─ cli.py
│
├─ tests/
│  └─ unit/
│     ├─ test_crypto_labels.py            # calendar-time join, gap handling
│     ├─ test_crypto_factor_values.py     # schema, known_at
│     └─ test_crypto_factor_eval_smoke.py # IC, direction, gap exclusion
│
├─ notebooks/
└─ requirements-m1.txt
```

## Key Navigation

- **Current mainline:** Factor library (Phase 2C closeout). See `docs/FACTOR_LIBRARY_ROADMAP.md`.
- **Doc entry point:** `docs/DOCS_INDEX.md` — categorized index of all documentation.
- **Factor registry:** `docs/FACTOR_REGISTRY.md` — 5 DIAGNOSTIC_PROBE factors, no alpha.
- **Pipeline scripts:** `scripts/fetch → build_labels → build_factor_values → evaluate_factors`
- **Tests:** `pytest tests/unit/test_crypto_*.py` (33 tests, all passing)

## Data Note

`data/cache/`, `data/features/`, `reports/artifacts/` contain generated artifacts.
These are in `.gitignore` (or should be) — regenerate by running the pipeline.
