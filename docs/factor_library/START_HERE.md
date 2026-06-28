# START HERE — Factor Library

**Status / 状态:** 唯一可信开发入口。
**Scope:** Crypto USDT perpetual cross-sectional factor library research.
**范围:** 加密永续合约截面因子库研究。
**Not in scope / 不属于当前范围:** production trading, exchange execution, investment advice, or alpha claims.

This file is the control surface for factor-library development. Other docs can provide detail or history, but they do not replace this entry point.

这是因子库开发的控制入口。其它文档可以提供细节或历史，但不能替代这个入口。

---

## Current Goal / 当前目标

Build a reproducible, extensible, explainable factor library:

1. define factors in one registry;
2. compute factor values from a known universe and label set;
3. evaluate factors with standard metrics and schemas;
4. produce auditable outputs and readable display pages;
5. keep the path clear enough to add more factors and later test signal construction.

中文概括：先把因子定义、因子值计算、因子评价、诊断输出和展示页面做成一条可复现、可拓展、可解释的主线。后续再扩充因子、替换 universe、做信号合成和回测。

The current generated state is:

- `research/factor_runs/crypto_top50_factor_library/factor_library_state.md`
- `research/factor_runs/crypto_top50_factor_library/factor_library_state.json`

Do not hand-write factor counts. Read them from the generated state files.

不要手写因子数量。当前数量以自动生成的 state 文件为准。

---

## Main Pipeline / 主流程

```text
raw bars
  -> universe
  -> labels / forward returns
  -> factor registry
  -> factor values
  -> factor-level evaluation
  -> factor diagnostics / profile / reports
  -> signal panel
  -> signal-level evaluation
  -> display pages
```

Current canonical dataset:

```text
crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
```

Universe changes should be handled through dataset/universe inputs and supported CLI arguments where available. Do not hardcode a new universe by copying scripts.

更换 universe 时，应优先通过 dataset/universe 输入和现有 CLI 参数处理；不要复制脚本硬编码一套新 universe。

---

## Source Files To Edit / 可以编辑的源码

These are source files. Edit them when changing behavior.

这些是行为来源。要改变流程或逻辑，改这里。

| File | Purpose |
|------|---------|
| `scripts/factor_formula_registry.py` | FactorSpec registry and current factor definitions |
| `scripts/factor_specs.py` | FactorSpec dataclass |
| `scripts/factor_ops.py` | Reusable factor operators |
| `scripts/build_factor_values.py` | Builds factor values from registered factors |
| `scripts/evaluate_factors.py` | Canonical factor-level evaluation |
| `scripts/run_factor_intake.py` | Isolated new-factor intake workflow |
| `scripts/run_post_intake_workflow_completion.py` | Completes standard post-intake diagnostics |
| `scripts/check_post_intake_workflow_integrity.py` | Post-intake integrity checker |
| `scripts/build_factor_library_state.py` | Regenerates current state JSON/MD |
| `scripts/build_labels.py` | Forward-return labels |
| `scripts/build_dynamic_universe_monthly_volume.py` | Current universe construction |
| `scripts/build_phase9b_signal_panel.py` | Current signal panel construction |
| `scripts/evaluate_signals.py` | Canonical signal-level evaluation |
| `src/momentum/signal_evaluation/` | Public signal-evaluation API |
| `src/momentum/factors/` | Reusable factor modules |

Rules:

- Prefer extending existing source files over creating new entry points.
- Do not add `*_v2.py`, `new_*`, `fixed_*`, or one-off evaluator scripts.
- If a new file is truly needed, it must replace or consolidate an existing responsibility.

规则：优先扩展现有源码，不新建平行入口；不要新增 `*_v2.py`、`new_*`、`fixed_*` 或一次性评价脚本；如果确实要新增文件，必须替代或合并已有职责。

---

## Generated Outputs / 自动生成产物

These are outputs. Read and audit them, but do not hand-edit them.

这些是运行结果。可以阅读、审计、发布，但不要手工修改。

| Path | Meaning |
|------|---------|
| `data/features/.../<factor_id>/factor_values.parquet` | Computed factor values |
| `research/factor_runs/crypto_top50_factor_library/factor_library_state.*` | Generated current counts/state |
| `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/` | Factor evaluation outputs |
| `research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/` | Isolated intake run evidence |
| `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/` | Diagnostic/profile outputs |
| `research/factor_runs/crypto_top50_factor_library/*.csv` | Research outputs and historical evidence |
| `reports/site/factor-library/` | Display pages and page assets |

If a generated file is wrong, fix the script or input that generates it, then regenerate.

生成结果错了，就改生成它的脚本或输入，然后重新生成。

---

## Add A New Factor / 新增因子

Default route: use factor intake. Do not create a parallel pipeline.

默认走 factor intake，不要另起一套流程。

For public factor-library expansion, use the compact manifest first:

- `docs/factor_library/public_factor_candidate_manifest.csv`
- `python scripts/check_public_factor_integration_status.py`

For Alpha101 / Alpha158 intake, every candidate should record formula source, field mapping, required operators, compute scope, timeframe mapping, expected direction, implementation status, and skip reason when blocked.

公开因子库扩展先看这个紧凑 manifest。Alpha101 / Alpha158 候选必须记录公式来源、字段映射、所需 operator、计算范围、时间尺度映射、方向语义、实现状态，以及无法实现原因。

Alpha101 formulas that require `IndNeutralize(..., IndClass.*)` are blocked
until the industry-neutralization data contract is satisfied:

- `docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md`
- `data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.template.csv`
- `python scripts/init_crypto_industry_taxonomy_review.py --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet --output-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --known-at 2026-06-28T00:00:00Z --taxonomy-version reviewed_v1 --source manual_review`
- `python scripts/build_crypto_industry_taxonomy_review_priority.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet`
- `python scripts/check_crypto_industry_taxonomy_review_source.py --source-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv`
- `python scripts/build_crypto_industry_taxonomy_artifact.py --input-csv data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.csv --output data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet`
- `python scripts/check_crypto_industry_taxonomy_contract.py --path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet`
- `python scripts/check_crypto_industry_taxonomy_coverage.py --bars-path data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet --taxonomy-path data/cache/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.parquet --min-full-coverage 0.98`

需要 `IndNeutralize(..., IndClass.*)` 的 Alpha101 公式，在行业/板块中性化数据契约满足前保持 skipped，不要用临时 crypto 分桶或时间序列去均值替代。
`build_crypto_industry_taxonomy_review_priority.py` 只按 bars 里的 quote_volume 排人工审核优先级，不推断或填充 sector/industry/subindustry。

Manifest status rules:

- Implemented rows use `implemented_batch_*`, `existing_*_backfill_*`, or `already_registered`; they must have a registry `FactorSpec`, no `skip_reason`, and are included in factor-value / intake / post-intake QA factor ID lists.
- Skipped rows use `skipped_*`, keep a non-empty `skip_reason`, use a `_skipped` factor ID suffix, and are not registry entries. They document duplicate formulas, unavailable fields, or blocked operators without creating parallel aliases.
- When running QA from the manifest, filter out skipped rows before calling `run_factor_intake.py`, `run_post_intake_workflow_completion.py`, or `check_post_intake_workflow_integrity.py`.

Manifest 状态规则：已实现行必须对应 registry；跳过行必须写明原因、使用 `_skipped` 后缀，并且不进入 factor_values / intake / post-intake QA 的 factor-id 列表。

1. Add or adjust a `FactorSpec` in `scripts/factor_formula_registry.py`.
2. Reuse `scripts/factor_ops.py` where possible.
3. Add a small operator only if the formula cannot be expressed with existing operators.
4. Run:

```bash
python scripts/run_factor_intake.py --factor-ids <factor_id_1> <factor_id_2> --run-id <run_id>
python scripts/build_factor_library_state.py
```

5. Review the isolated run:

```text
research/factor_runs/crypto_top50_factor_library/factor_intake/<run_id>/
```

Key files to inspect:

- `manifest.json`
- `command_log.json`
- `outputs_index.json`
- `quality_checks.csv`
- `factor_rankic_summary.csv`
- `factor_long_short_summary.csv`
- `factor_conclusion_cards.csv`
- `report.md`

Rules:

- New factors start as diagnostic research assets.
- Do not add intake factors directly to `scripts/build_phase9b_signal_panel.py`.
- Do not modify live trading, broker, exchange, or execution code for factor intake.
- Do not make production, tradeability, or alpha claims.

规则：新因子先是诊断研究资产；不要直接塞进 signal panel；不要碰实盘、broker、交易所或执行代码；不要做生产、可交易或 alpha 声明。

---

## Complete Post-Intake Evaluation / 完成全套入库后评价

For a factor that needs the full evaluation layer, use the existing workflow:

如果新因子需要完整评价层，继续使用已有 workflow：

```bash
python scripts/run_post_intake_workflow_completion.py --factor-ids <factor_id_1>,<factor_id_2>
python scripts/check_post_intake_workflow_integrity.py --factor-ids <factor_id_1>,<factor_id_2>
python scripts/check_factor_evaluation_page_completeness.py
python scripts/build_factor_library_state.py
```

Resource rule:

- Prefer incremental or missing-only diagnostics after small factor batches.
- Do not default to a blind full refresh on the 15GB development server.
- To continue incomplete work without naming factors manually, use `python scripts/run_post_intake_workflow_completion.py --only-missing`.
- See `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` and `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` for detailed recovery and OOM-safe procedures.

资源规则：小批量新增因子优先增量/补缺，不默认全量刷新；15GB 机器上尤其不要盲跑完整昂贵流程。

---

## Run Factor Evaluation Directly / 直接运行因子评价

Use the canonical evaluator:

```bash
python scripts/evaluate_factors.py
```

For a subset:

```bash
python scripts/evaluate_factors.py --factor-ids <factor_id...> --output-suffix <suffix> --output-dir <output_dir>
```

Do not create another factor-level evaluator unless this file is being deliberately replaced and parity is proven.

不要新建另一个因子评价器，除非是在明确替换当前评价器，并且已经证明数值一致。

---

## Add A New Signal / 新增信号

Signals are downstream of factor research.

信号是因子研究之后的下游工作。

1. Modify `scripts/build_phase9b_signal_panel.py`.
2. Preserve output columns: `timestamp`, `symbol`, `signal_value`.
3. Run `scripts/evaluate_signals.py`.
4. Run cost, liquidity, and paper diagnostics before making any paper diagnostic claim.

Do not mix signal-promotion work into factor intake.

不要把信号晋升工作混进因子入库流程。

---

## Display Pages / 展示页面

`reports/site/factor-library/` is display-only.

`reports/site/factor-library/` 只是展示层，不是开发入口。

Use these pages to read results:

- `reports/site/factor-library/index.html`
- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/factor-evaluation.html`
- `reports/site/factor-library/signal-evaluation-summary.html`

Do not hand-edit display pages to fix a result. Fix the data source or page builder, then rebuild.

不要手改页面来“修结果”。要改数据源或页面生成器，然后重建页面。

### HTML / Page Interpretation Source Files

These files generate or validate the factor-evaluation display layer. Edit these sources or their input data, not generated HTML.

这些文件属于展示解释层源码。页面显示错了，优先改这些文件或它们的输入数据，不要手改生成后的 HTML。

| File | Purpose |
|------|---------|
| `scripts/_build_factor_eval_html.py` | Builds `reports/site/factor-library/factor-evaluation.html` |
| `scripts/factor_metric_glossary.json` | Metric glossary and tooltip source |
| `scripts/check_factor_evaluation_page_completeness.py` | Page QA and completeness checks |
| `scripts/build_single_factor_paper_page_payload.py` | Paper diagnostics payload |
| `scripts/build_unified_factor_profile.py` | Unified factor profile payload |

---

## Supporting References / 支持参考

These files are supporting references, not alternate entry points:

这些文件是支持参考，不是第二入口。

| File | Use |
|------|-----|
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Snapshot of active scripts and pipeline status |
| `docs/factor_library/REGENERATION_CONTRACT.md` | Full refresh order and expensive-stage notes |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Detailed post-intake workflow |
| `docs/factor_library/RESOURCE_AWARE_REFRESH_GUIDE.md` | Memory-aware refresh guidance |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | File status reference when uncertain |
| `docs/factor_library/ORPHAN_WORK_AUDIT.md` | Orphan/stale file audit |

Historical or superseded material:

- `docs/factor_library/audits/`
- `docs/factor_library/prompts/`
- `docs/factor_library/archive/`
- `docs/factor_library_transparency/`
- `reports/site/factor-library/_archive/`
- `docs/refactor/`

Use historical material for audit traceability only. Do not use it to decide how to add factors or which counts are current.

历史材料只用于审计追溯，不用于判断如何新增因子，也不用于判断当前因子数量。
