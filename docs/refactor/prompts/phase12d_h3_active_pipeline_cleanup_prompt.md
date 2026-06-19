# Phase 12D-H3：Active Signal Evaluation Pipeline Cleanup

## 背景

当前 H2-T 已经证明：

- 新 `signal_evaluation` public API 能复现旧 Phase 10A RankIC；
- 新增 `legacy_phase10a` spread mode 后，也能复现旧 Phase 10A spread；
- H3 gate 已经显示 `OPEN_FULL_WRAPPER`。

但是项目目标不是长期保留一堆 Phase 10A / 10B / 10D 脚本和多个 mode 到处切换。最终目标是：

> 代码仓库干净、可读、可维护；active path 明确；历史阶段脚本集中归档或移出 active scripts。

因此 H3 不应该只是把旧 `run_phase10a_signal_backtest.py` 改成 wrapper。那会继续保留阶段编号和旧命名，依然难读。

本阶段目标改为：建立 clean active signal evaluation pipeline，并把旧 phase scripts 从 active scripts 目录中降级为 archived legacy references。

## 本轮目标

执行 Phase 12D-H3：Active Signal Evaluation Pipeline Cleanup。

目标：

1. 建立一个新的 canonical active entrypoint：
   - `scripts/evaluate_signals.py`
2. 让未来所有规则信号、ML 信号、ensemble 信号都走这个入口；
3. 将旧 Phase 10A/10A-R/10B/10D 脚本集中归档，不再作为 active scripts；
4. 更新文档和网站说明：active pipeline 用语替代 Phase 10A/10B/10D；
5. 不启动 Phase 13，不接交易所，不做真实执行。

## 核心设计原则

### 1. Active code 只保留一个主入口

未来不要让用户看到：

- run_phase10a_signal_backtest.py
- run_phase10a_r_diagnostics.py
- run_phase10b_tail_diagnostics.py
- run_phase10d_tail_aware_variants.py

作为 active pipeline。

未来 active entrypoint 应该是：

```bash
python scripts/evaluate_signals.py \
  --signal-panel <path> \
  --labels <path> \
  --signals signal_v0_core_only signal_v0_pm_full_structured signal_v0_family_balanced_diagnostic \
  --horizons 1h 4h 24h 72h \
  --output-dir <dir>
```

### 2. 旧 phase scripts 可以归档，但不要散落在 active scripts

建议创建：

```text
archive/legacy_phase_scripts/phase10/
```

移动或复制旧脚本到：

- `archive/legacy_phase_scripts/phase10/run_phase10a_signal_backtest.py`
- `archive/legacy_phase_scripts/phase10/run_phase10a_r_diagnostics.py`
- `archive/legacy_phase_scripts/phase10/run_phase10b_tail_diagnostics.py`
- `archive/legacy_phase_scripts/phase10/run_phase10d_tail_aware_variants.py`

并在 active `scripts/` 中移除这些旧 phase scripts，或至少加 deprecated stub 指向新入口。

推荐：

- 若项目当前没有外部依赖这些旧脚本，直接 move 到 archive；
- 如果担心断链，则保留 very thin deprecated stub，但 stub 只能提示使用 `scripts/evaluate_signals.py`，不能继续执行旧逻辑。

### 3. 不要让 legacy mode 污染日常使用

`legacy_phase10a` mode 的用途是历史可复现，不是未来默认研究接口。

建议：

- `compute_quantile_spread(..., mode="standard")` 作为默认；
- `mode="legacy_phase10a"` 只在 parity / archived reproduction 场景使用；
- README 中明确：日常新研究不需要选择 legacy mode。

不要在 active pipeline 中要求用户手动来回切换一堆模式。

### 4. 历史输出不改

旧 Phase 10A 输出文件仍然作为 historical artifacts 存在，不要修改。

新的 active evaluator 应输出新命名文件，例如：

- `signal_evaluation_rankic_summary.csv`
- `signal_evaluation_quantile_spread_summary.csv`
- `signal_evaluation_consistency_summary.csv`
- `signal_evaluation_manifest.json`

不要覆盖旧：

- `phase10a_signal_rankic_summary.csv`
- `phase10a_signal_quantile_spread_summary.csv`

## 允许新增或修改

- `scripts/evaluate_signals.py`
- `archive/legacy_phase_scripts/phase10/README.md`
- 移动或归档旧 Phase 10 scripts
- `src/momentum/signal_evaluation/README.md`
- `docs/refactor/SIGNAL_EVALUATION_REFACTOR_PLAN.md`
- `docs/refactor/ACTIVE_SIGNAL_EVALUATION_PIPELINE.md`
- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/assets/actual_script_map.json`
- `docs/factor_library_transparency/actual_script_map.md`
- tests for CLI / schema / no active phase-script clutter
- quality check csv, e.g. `phase12d_h3_active_pipeline_quality_checks.csv`

## 不允许

- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化信号
- 不要改历史研究结果
- 不要覆盖旧 Phase 10A 输出
- 不要删除 Git 历史不可恢复的信息
- 不要新开一堆网页

## 一、建立 canonical active evaluator

新增：

```text
scripts/evaluate_signals.py
```

功能：

- 读取 signal panel；
- 读取 labels；
- 支持 signals 列表；
- 支持 horizons 列表；
- 调用 `select_forward_return`；
- 调用 `compute_rank_ic` / `summarize_rank_ic`；
- 调用 `compute_quantile_spread` / `summarize_quantile_spread`；
- 调用 `check_rankic_spread_consistency`；
- 输出 canonical active files。

建议输出：

```text
<output_dir>/signal_evaluation_rankic_summary.csv
<output_dir>/signal_evaluation_quantile_spread_summary.csv
<output_dir>/signal_evaluation_consistency_summary.csv
<output_dir>/signal_evaluation_manifest.json
```

manifest 至少包含：

- input signal panel path
- input labels path
- signals evaluated
- horizons evaluated
- spread_mode used
- timestamp generated
- package version
- no real execution statement

## 二、active evaluator 默认 spread mode

默认使用：

```text
spread_mode = standard
```

但 CLI 可显式设置：

```bash
--spread-mode standard
--spread-mode legacy_phase10a
```

README 必须写清楚：

- `standard` 是未来 active research 默认；
- `legacy_phase10a` 只用于历史 Phase 10A 复现；
- 日常用户不需要频繁切 mode。

如果你认为 CLI 暴露 legacy 会增加心智负担，可以只在 parity harness 暴露 legacy，不在 active evaluator 暴露 legacy。二选一，但要在文档中说清。

## 三、归档旧 phase scripts

将旧 Phase 10 scripts 归档到：

```text
archive/legacy_phase_scripts/phase10/
```

归档 README 必须写清：

- 这些脚本是 historical research scripts；
- 不再是 active pipeline；
- 新入口是 `scripts/evaluate_signals.py`；
- 旧结果仍可通过 Git history 和 archived scripts 理解；
- 不建议未来新信号调用这些脚本。

如果旧脚本必须暂时留在 `scripts/`，则改成 deprecated stub，内容只能提示：

```text
This script is archived. Use scripts/evaluate_signals.py instead.
```

不要让旧脚本继续承担 active evaluation。

## 四、更新 actual-script-map

更新 `actual-script-map.html` 第 7 节：

必须从“10A/10B/10D 是当前入口”改成：

```text
Active entrypoint: scripts/evaluate_signals.py
Legacy phase scripts: archived under archive/legacy_phase_scripts/phase10/
```

保留解释：

- Phase 10A/10B/10D 是历史阶段；
- active code 不再以阶段编号作为主接口；
- Signal Evaluation Framework 是未来主路径。

不要新开页面。

## 五、测试

新增 tests：

1. `scripts/evaluate_signals.py --help` runs
2. CLI argument parser recognizes:
   - `--signal-panel`
   - `--labels`
   - `--signals`
   - `--horizons`
   - `--output-dir`
   - optional `--spread-mode`
3. active evaluator imports public API from `momentum.signal_evaluation`
4. active evaluator does not import old Phase 10 scripts
5. old Phase 10 scripts are absent from active `scripts/` or are deprecated stubs
6. archive README exists
7. actual-script-map mentions active entrypoint and archive location
8. no real execution / no alpha / no production / Phase 13 not started statements remain

## 六、质量检查

新增：

```text
phase12d_h3_active_pipeline_quality_checks.csv
```

至少包括：

- canonical evaluator exists
- evaluator uses public signal_evaluation API
- evaluator supports 3 signals and 4 horizons
- evaluator writes canonical outputs
- evaluator writes manifest
- old Phase 10 scripts archived or deprecated
- actual-script-map updated with active entrypoint
- archive README exists
- no old Phase 10 outputs overwritten
- no signal panel modified
- no labels modified
- no real execution
- no alpha claim
- no production claim
- Phase 13 NOT STARTED

## 七、性能说明

不要在本阶段做大规模向量化优化。

但文档中要写清楚：

- 当前 public API 正确性已验证；
- 大规模全量 parity 可能较慢；
- 性能优化作为后续 H4：vectorized signal evaluation。

## 完成标准

完成后提交 commit。

commit message 建议：

```text
Phase 12D-H3: active signal evaluation pipeline cleanup
```

完成后输出：

- commit hash
- active evaluator path
- old scripts archive/deprecation status
- whether actual-script-map updated
- whether Phase 13 remains not started
