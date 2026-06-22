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
| `docs/factor_library/REGENERATION_CONTRACT.md` | Canonical pipeline & refresh contract |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | File status register |
| `docs/factor_library/ORPHAN_WORK_AUDIT.md` | Orphan audit |

---

## Do Not Use / Historical Only

These files were deleted in PM-03 (git history preserves them). Do not recreate.

| Former path | Status |
|-------------|--------|
| `scripts/evaluate_factors_dynamic_universe.py` | DELETED (was DEPRECATED_STALE) |
| `scripts/compare_static_dynamic_factor_evals.py` | DELETED (was ORPHAN) |
| `scripts/export_alphalens_factor_data.py` | DELETED (was HISTORICAL_ARCHIVE) |
| `scripts/run_alphalens_smoke_check.py` | DELETED (was HISTORICAL_ARCHIVE) |
| `scripts/audit_dynamic_universe_*.py` (3 files) | DELETED (was ORPHAN) |
| `scripts/build_crypto_native_factor_values.py` | DELETED (was ORPHAN) |
| `scripts/build_factor_values_batch.py` | DELETED (was ORPHAN) |
| Root-level `PHASE_12D_*.md` (8 files) | MOVED to `docs/factor_library/archive/phase12d/` |
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

## Resource-Aware Post-Intake Workflow / 资源感知的入库后工作流

After PM-35 through PM-37, the factor library supports incremental diagnostics. **Future factor intake should prefer incremental/missing-only diagnostics over a blind full refresh**, especially on the 15GB development server (no swap).

After running `run_factor_intake.py`, complete the remaining evidence with:

1. **Post-Intake Workflow Runbook** — `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` — step-by-step guide for completing 12/12 evidence after a controlled intake batch
2. **Resource-Aware Refresh Guide** — `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` — how to avoid OOM, use `--factor-ids` / `--only-missing`, and merge paper portfolio outputs safely
3. **Page Completeness QA** — `scripts/check_factor_evaluation_page_completeness.py` — verifies the public HTML page has all expected factors, sections, and disclaimers

**Key rule:** Do not run a full library refresh (`--stage all --expensive-ok`) as the default after adding a small batch of 3–5 new factors. Use the resource-aware runbook instead.

---

## Current Numbers / 当前数据

- Registered factors / computed / missing: see `factor_library_state.json` / `factor_library_state.md` (auto-generated)
- Missing factor_values: see `factor_library_state.json` (auto-generated)
- Signal panel factors: **10**
- Signal variants: **3** (core_only, pm_full_structured, family_balanced_diagnostic)
- Horizons: **4** (1h, 4h, 24h, 72h)
- Public pages: **4** (index, code structure, factor evaluation, signal evaluation)

## Lessons Learned: Data Source Hierarchy for Page Builder

**PM-40 教训（2026-06-23）：** 新因子在公开页面显示空白指标。

**根因：** HTML builder 只从旧诊断文件（`factor_diagnostics_summary.csv`）读数据。新因子的 horizon metrics 在旧文件中是 NaN，但 factor-level evaluation 文件有完整数据。builder 没有 merge 两个来源。

**修复：** builder 现在同时加载旧诊断 + 新 factor-level evaluation 数据，用 `(factor_name, horizon)` 做 lookup，旧数据为空时 fallback 到新数据。

**预防规则（必须遵守）：**
1. 新增因子 intake batch 后，必须检查 `_build_factor_eval_html.py` 是否有该因子的数据源
2. `check_factor_evaluation_page_completeness.py` 现在有 `new_factor_metrics` 检查：验证有 `ev_has_factor_level_evaluation=True` 的因子必须有 `rankic_mean`
3. 详细数据源映射见 `POST_INTAKE_WORKFLOW_RUNBOOK.md §9`

**数据源层级：**

| 数据 | 旧来源（可能为空） | 新来源（始终完整） |
|------|-------------------|-------------------|
| rankic_mean, t_stat | factor_diagnostics_summary.csv | factor_level_rankic_summary.csv |
| long_short_mean, sharpe | factor_diagnostics_summary.csv | factor_level_long_short_summary.csv |
| best_horizon | factor_diagnostics_summary.csv | factor_level_coverage_summary.csv |
| Monthly IC 系列 | factor_monthly_ic_series.csv | factor_level_period_ic_summary.csv |
| Monthly LS 系列 | factor_monthly_long_short_series.csv | factor_level_period_long_short_summary.csv |

## PM-40B 教训：Redundancy 与 Unified Profile 的数据来源冲突

**问题：** 页面旧 Redundancy section 读 `factor_redundancy_summary.csv`（PM-18/PM-19），新因子在该 CSV 中是 None。Unified Profile 有真实数据（cluster_id, cluster_role, marginal_class）。两个 section 显示矛盾信息。

**根因：** 旧 redundancy 计算只覆盖了有足够 pairwise overlap 的因子。新因子因为入池时间短，pairwise 覆盖不足，结果是 `INSUFFICIENT_OVERLAP`。但 Unified Profile 的 cluster/marginal 评估使用了不同的方法（基于 factor profile），可以给出结果。

**修复模式：** HTML builder 在 merge 所有数据源后，做 reconciliation post-processing：
- 旧 redundancy 为空 → 用 profile 数据 fallback
- cluster_id = -1 → 用 profile_cluster_id
- novelty_assessment = INSUFFICIENT_OVERLAP → 从 cluster_member_role 推导

**预防规则：**
1. 新增因子后，必须检查旧 section（redundancy, scorecard, shape）是否与 Unified Profile 一致
2. QA 脚本 `pm40b_display_consistency` 检查：WORKFLOW_READY 因子不应有 source_warning、cluster_id 不应是 -1
3. 当两个数据源冲突时，以 Unified Profile 为准（它是最新的综合评估）

## PM-40B 教训：Monthly IC 数据缺口

**问题：** `factor_level_period_ic_summary.csv` 只有 71 个因子，5 个 PM-35 新因子没有 period IC 数据。导致 Monthly RankIC 图表为空。

**根因：** factor-level evaluation 的 period IC 计算没有覆盖所有因子。rankic/LS 汇总有（76 个），但 period-level 没有。

**修复：** Monthly IC 为空时，显示解释性说明（summary RankIC 值 + 月度序列不可用），而不是裸 "No data"。

**预防规则：**
1. 新增因子 batch 后，验证 `factor_level_period_ic_summary.csv` 包含所有新因子
2. 如果 period IC 缺失，至少确保 rankic 汇总有数据（作为 fallback 展示）

## PM-40B 完整教训：6 层修复经验（2026-06-22）

**核心教训：** 新因子 12/12 evidence complete 不等于页面所有 legacy sections 自动完整。

**三层根因：**
1. **数据层：** period IC 数据在 batch 文件中，未合并到 canonical CSV → Monthly RankIC 为空
2. **Payload 层：** paper payload 未重新生成 → Paper section 显示 N/A
3. **Builder 层：** 字段映射错误（key 维度不匹配）、redundancy fallback 缺失

**必须遵守的 post-intake 检查清单：**
1. ✅ 合并 period IC batch 数据到 canonical CSV
2. ✅ 运行 `build_single_factor_paper_page_payload.py` 重新生成 paper payload
3. ✅ 验证 `rankic_std` / `rankic_ir` 从 period IC 数据计算
4. ✅ 检查 redundancy section 与 Unified Profile 一致性
5. ✅ 运行 `check_factor_evaluation_page_completeness.py`（22 项检查）
6. ✅ 部署后 `curl -I` 验证 HTTP 200

**关键脚本依赖：**
- `evaluate_factors.py --factor-ids` → 生成 period IC（但 canonical CSV 需手动合并）
- `build_single_factor_paper_page_payload.py` → 生成 paper payload（需手动运行）
- `_build_factor_eval_html.py` → 构建 HTML（需手动运行）

## PM-40C 教训：Scorecard 过期检测与 Redundancy 数据来源统一（2026-06-22）

**核心教训：** scorecard 数据可能在 factor-level evaluation 之前计算，导致所有底层指标为 0。页面需要检测并覆盖过期 scorecard。

**三个修复：**
1. **Scorecard 过期检测：** 检查 `rankic_mean=0 且 coverage_rate=0`，用 unified profile 数据覆盖
2. **Redundancy 来源统一：** 当 cluster/marginal 来自 PM-37 时，隐藏旧 pairwise 字段，显示 profile 字段
3. **空字段解释：** LS Std/Ann Return/Ann Vol/Max DD 为空时显示 "not available from factor-level summary; see paper portfolio diagnostics"

**QA 检查：** `pm40c_consistency` 验证 scorecard 不与 profile 冲突、redundancy 不与 cluster 冲突

## PM-41 教训：LS aggregate metrics 是 canonical 输出，不是 page-only fallback（2026-06-22）

**核心教训：** LS 聚合统计量（std, ann_return, ann_vol, max_dd, positive_period_rate）应该在 `evaluate_factors.py` 中作为 canonical 输出计算，而不是让 HTML builder 承担计算职责。

**修复：**
1. `evaluate_factors.py` 新增 7 个字段到 `factor_level_long_short_summary.csv`
2. `_build_factor_eval_html.py` 从 canonical LS summary 读取这些字段作为 fallback

**年化规则：** monthly × 12 (return), monthly × √12 (vol), `annualization_method = "monthly_x12"`

**新字段：** `long_short_spread_std`, `long_short_spread_annualized_return`, `long_short_spread_annualized_vol`, `long_short_spread_max_drawdown`, `long_short_spread_positive_period_rate`, `n_monthly_periods`, `annualization_method`

## PM-42 教训：Market Regime / BTC Diagnostics 已有脚本，只需重新整合（2026-06-23）

**核心教训：** `build_factor_market_regime_diagnostics.py`（PM-23/PM-24）已计算所有 regime/BTC 字段。PM-35 因子显示 `INSUFFICIENT_REGIME_DATA` 的根因是 `factor_monthly_ic_series.csv` 缺少这 5 个因子。

**修复：** 将 PM-35 的 monthly IC 数据从 canonical `factor_level_period_ic_summary.csv` 合并到 `factor_monthly_ic_series.csv`，然后重新运行 regime 脚本。

**关键字段：** `paper_return_btc_corr`, `paper_return_btc_beta`, `long_short_btc_corr`, `long_short_btc_beta`, `ic_btc_return_corr`, `bull_minus_bear_paper_return`, `highvol_minus_lowvol_paper_return`, `drawdown_minus_normal_paper_return`, `regime_dependency_class`

**重要澄清：**
- Regime labels 是 ex-post diagnostics，不是交易时机信号
- BTC correlation/beta 是 research diagnostics，不是执行信号
- `INSUFFICIENT_REGIME_DATA` 会在数据不足时明确显示

**Workflow 要求：** 新因子 intake 后，必须确保 `factor_monthly_ic_series.csv` 包含新因子，然后重新运行 `build_factor_market_regime_diagnostics.py`。

## PM-43A 教训：Post-Intake Workflow 必须完整执行（2026-06-23）

**核心教训：** 新因子不是跑完 intake 就结束。必须完成 post-intake workflow completion，包括：
1. Factor-level evaluation (evaluate_factors.py)
2. Paper portfolio diagnostics
3. Pairwise redundancy (build_factor_pairwise_redundancy_matrix.py --factor-ids)
4. Redundancy cluster + marginal information
5. Regime/BTC diagnostics (build_factor_market_regime_diagnostics.py --canonical-ic-path)
6. Scorecard refresh (build_factor_quality_scorecard.py — now has canonical fallback)
7. Unified profile refresh
8. Page build + QA

**关键修复：**
- Scorecard 现在从 canonical factor-level evaluation 读取 RankIC/LS 数据，不再依赖 stale diagnostics summary
- Regime 脚本支持 `--canonical-ic-path` 自动合并缺失因子的 monthly IC
- Pairwise redundancy 支持 `--factor-ids` 增量计算

**自动化工具：**
- `scripts/run_post_intake_workflow_completion.py --factor-ids fid1,fid2` — 自动跑完所有步骤
- `scripts/check_post_intake_workflow_integrity.py --factor-ids fid1,fid2` — 检查 11 个完整性维度

**Page builder fallback 只是防御，不是 canonical source。** Canonical 数据来自 evaluate_factors.py、paper payload、regime script、scorecard 等 pipeline 输出。

**新因子必须通过 post-intake workflow integrity checker 才能进入 interpretation。**
