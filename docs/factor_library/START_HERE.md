# START HERE — Factor Library

**Status:** Active factor-library entry point | **Language:** 中文 + English

---

## 这是什么项目？

Crypto USDT perpetual cross-sectional momentum factor library research system.

这是一个**加密永续合约截面动量因子库研究系统**。目标是：从原始K线数据出发，通过因子计算、因子评价、信号构建、信号评价的完整流水线，寻找可诊断的横截面排序信息。

**不是实盘。不是交易建议。不是 alpha 验证。**

**当前状态 / Current state:** 自动生成于 `factor_library_state.json` / `factor_library_state.md`。不要手写计数，从此文件读取。

---

## Pipeline Map / 流水线地图

```
raw bars / 原始K线
  → dynamic universe / 动态样本池
  → labels / 未来收益标签
  → factor registry / 因子注册表
  → factor values / 因子值计算
  → factor-level evaluation / 因子层评价
  → factor catalog & direction audit / 因子目录与方向审计
  → signal panel / 信号面板
  → signal-level evaluation / 信号层评价
  → cost/liquidity/paper diagnostics / 成本、流动性与纸面诊断
  → public summary pages / 公开报告页
```

---

## Canonical Files / 核心文件

| File | Role / 角色 |
|------|-------------|
| `scripts/factor_formula_registry.py` | Factor spec registry (see factor_library_state.md) |
| `scripts/factor_specs.py` | FactorSpec dataclass |
| `scripts/factor_ops.py` | Factor building-block operators |
| `scripts/build_factor_values.py` | Compute factor values from registry |
| `scripts/evaluate_factors.py` | Factor-level RankIC evaluation (H8/H8-R) |
| `scripts/run_factor_intake.py` | Standard isolated intake runner for new factors |
| `scripts/build_factor_redundancy.py` | Intake-vs-library redundancy diagnostics |
| `scripts/build_factor_conclusion_cards.py` | Conservative per-factor diagnostic cards |
| `scripts/generate_intake_report.py` | Human-readable intake run report |
| `scripts/build_factor_library_state.py` | Generated JSON/MD state; single source for current counts |
| `scripts/promote_factor_intake.py` | Guard only; no automatic signal promotion |
| `scripts/check_factor_ic_parity.py` | Factor IC parity guard (10/10 PASS) |
| `scripts/check_factor_registry_integrity.py` | Registry integrity linter |
| `scripts/build_factor_catalog.py` | Build factor catalog CSV/JSON |
| `scripts/check_factor_catalog_integrity.py` | Catalog integrity self-check |
| `scripts/audit_factor_direction_semantics.py` | Direction semantics audit |
| `scripts/build_labels.py` | Forward-return labels (1h/4h/24h/72h) |
| scripts/build_dynamic_universe_monthly_volume.py | Universe construction (monthly volume Top50) |
| `scripts/download_full_binance_1h_universe.py` | Data download |
| `scripts/build_phase9b_signal_panel.py` | Signal panel construction |
| `scripts/evaluate_signals.py` | Signal-level RankIC/Spread evaluation |
| `src/momentum/signal_evaluation/` | Public API: compute_rank_ic, compute_quantile_spread |
| `src/momentum/factors/` | Reusable factor modules |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Governance center |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | File status register |
| `docs/factor_library/ORPHAN_WORK_AUDIT.md` | Orphan audit |

---

## Do Not Use / Historical Only

| File | Status |
|------|--------|
| `scripts/evaluate_factors_dynamic_universe.py` | DEPRECATED_STALE — broken, cannot run |
| `scripts/compare_static_dynamic_factor_evals.py` | ORPHAN_REVIEW_REQUIRED |
| `scripts/export_alphalens_factor_data.py` | HISTORICAL_ARCHIVE (Phase 5B) |
| `scripts/run_alphalens_smoke_check.py` | HISTORICAL_ARCHIVE (Phase 5B) |
| `scripts/audit_dynamic_universe_*.py` (3 files) | ORPHAN_REVIEW_REQUIRED |
| `scripts/build_crypto_native_factor_values.py` | ORPHAN_REVIEW_REQUIRED |
| Root-level `PHASE_12D_*.md` files | HISTORICAL_ARCHIVE |
| `reports/site/factor-library/_archive/` | 21 old pages, not in public navigation |

---

## How to Add a New Factor / 如何新增因子

Default route: **use factor intake**. Do not create a parallel factor pipeline, a one-off evaluator, or a new report format unless the existing intake contract cannot support the factor.

Read first:

1. `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
2. `scripts/factor_formula_registry.py`
3. `scripts/factor_specs.py`
4. `scripts/factor_ops.py`
5. `scripts/run_factor_intake.py`
6. `reports/site/factor-library/actual-script-map.html` (click `Factor Intake / 因子入库`)
7. `docs/factor_library/FILE_STATUS_REGISTER.csv` if you are unsure whether a file is active, archived, or orphaned

Reuse existing code:

- Reuse `FactorSpec` from `scripts/factor_specs.py`.
- Reuse operators in `scripts/factor_ops.py` when possible.
- Reuse `scripts/build_factor_values.py` for `factor_values.parquet`.
- Reuse `scripts/evaluate_factors.py` through the intake runner for partial evaluation.
- Reuse `scripts/build_factor_redundancy.py`, `scripts/build_factor_conclusion_cards.py`, and `scripts/generate_intake_report.py` for diagnostics and reporting.

Write new code only when needed:

- Add new factor definitions in `scripts/factor_formula_registry.py`.
- Add small reusable operators to `scripts/factor_ops.py` only if the formula cannot be expressed with existing operators.
- Add tests only for new behavior, schema guards, or bug fixes.
- Do not create a new standalone factor-evaluation script, new signal builder, or separate intake report format.

Run:

```bash
python scripts/run_factor_intake.py --factor-ids <factor_id...> --run-id <run_id>
python scripts/build_factor_library_state.py
```

Review:

- `research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/manifest.json`
- `command_log.json`
- `outputs_index.json`
- `quality_checks.csv`
- `factor_conclusion_cards.csv/json`
- `report.md`
- `factor_library_state.md`

Rules:

- One or many new factors use the same `--factor-ids <factor_id...>` interface.
- New factors start as diagnostic research assets.
- Do not add intake factors to `scripts/build_phase9b_signal_panel.py`.
- Do not modify live trading, execution, broker, strategy-live, or exchange API code.
- Do not make production, tradeability, or alpha claims.

---

## How to Add a New Signal / 如何新增信号

1. Modify `scripts/build_phase9b_signal_panel.py` to add a new variant
2. Output must follow: `timestamp / symbol / signal_value`
3. Run `scripts/evaluate_signals.py` for signal-level RankIC/Spread
4. Run cost/liquidity diagnostics before any paper diagnostic claim

---

## Current Numbers / 当前数据

- Registered factors / computed / missing: see `factor_library_state.json` / `factor_library_state.md` (auto-generated)
- Missing factor_values: **6** (taker/funding — data source lacks taker fields)
- Signal panel factors: **10**
- Signal variants: **3** (core_only, pm_full_structured, family_balanced_diagnostic)
- Horizons: **4** (1h, 4h, 24h, 72h)
- Public pages: **4** (index, code structure, factor evaluation, signal evaluation)
