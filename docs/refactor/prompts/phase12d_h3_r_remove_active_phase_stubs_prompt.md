# Phase 12D-H3-R：Remove Deprecated Phase Stubs from Active Scripts

## 背景

Phase 12D-H3 已完成：

- 新增 `scripts/evaluate_signals.py` 作为 canonical active signal evaluation entrypoint；
- 旧 Phase 10 scripts 已归档到 `archive/legacy_phase_scripts/phase10/`；
- active `scripts/` 中保留了 deprecated stubs，指向新入口。

这个方向正确，但仍不够干净。

用户的目标是：

> active code path 干净、可读、可维护；不要在 active scripts 目录里继续出现 run_phase10a / run_phase10b / run_phase10d 这种历史阶段名。

因此 H3-R 的目标是：从 active `scripts/` 目录移除 deprecated phase stubs，让旧 phase 名称只存在于 archive 中。

## 本轮目标

执行 Phase 12D-H3-R：Remove Deprecated Phase Stubs from Active Scripts。

目标：

1. active `scripts/` 中只保留真正 active 的 pipeline entrypoints；
2. 旧 Phase 10A / 10A-R / 10B / 10D 脚本只存在于 `archive/legacy_phase_scripts/phase10/`；
3. 新入口为 `scripts/evaluate_signals.py`；
4. 文档和 actual-script-map 明确 active vs archive；
5. 不运行全量 evaluation；
6. 不做性能优化；
7. 不启动 Phase 13。

## 允许修改

- 删除 active `scripts/` 中 deprecated phase stubs：
  - `scripts/run_phase10a_signal_backtest.py`
  - `scripts/run_phase10a_r_diagnostics.py`
  - `scripts/run_phase10b_tail_diagnostics.py`
  - `scripts/run_phase10d_tail_aware_variants.py`
- `archive/legacy_phase_scripts/phase10/README.md`
- `docs/refactor/ACTIVE_SIGNAL_EVALUATION_PIPELINE.md`
- `docs/refactor/SIGNAL_EVALUATION_REFACTOR_PLAN.md`
- `reports/site/factor-library/actual-script-map.html`
- `reports/site/factor-library/assets/actual_script_map.json`
- `docs/factor_library_transparency/actual_script_map.md`
- tests checking active scripts cleanliness
- quality check csv, e.g. `phase12d_h3_r_active_scripts_cleanup_quality_checks.csv`

## 不允许修改

- 不要删除 archive 中的 legacy phase scripts
- 不要删除旧 historical output files
- 不要修改 old Phase 10 outputs
- 不要修改 signal panel
- 不要修改 labels
- 不要运行全量 evaluation
- 不要做向量化性能优化
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化信号

## 一、删除 active deprecated stubs

如果以下文件仍存在于 active `scripts/` 中，请删除：

```text
scripts/run_phase10a_signal_backtest.py
scripts/run_phase10a_r_diagnostics.py
scripts/run_phase10b_tail_diagnostics.py
scripts/run_phase10d_tail_aware_variants.py
```

这些文件的历史版本已经在 archive 中保留，不应再污染 active scripts。

## 二、确认 archive 中保留完整历史脚本

确认以下文件存在：

```text
archive/legacy_phase_scripts/phase10/run_phase10a_signal_backtest.py
archive/legacy_phase_scripts/phase10/run_phase10a_r_diagnostics.py
archive/legacy_phase_scripts/phase10/run_phase10b_tail_diagnostics.py
archive/legacy_phase_scripts/phase10/run_phase10d_tail_aware_variants.py
archive/legacy_phase_scripts/phase10/README.md
```

archive README 必须明确：

- these scripts are inactive historical references；
- active entrypoint is `scripts/evaluate_signals.py`；
- do not use archived scripts for new research；
- historical outputs remain untouched。

## 三、更新 active pipeline 文档

更新或新增：

```text
docs/refactor/ACTIVE_SIGNAL_EVALUATION_PIPELINE.md
```

必须写清：

- active entrypoint: `scripts/evaluate_signals.py`
- active module: `src/momentum/signal_evaluation/`
- active outputs: `signal_evaluation_*.csv`
- legacy scripts archive location
- old Phase 10 outputs are historical artifacts, not active pipeline outputs

## 四、更新 actual-script-map

更新 actual-script-map 第 7 节。

要求：

- active entrypoint 显示为 `scripts/evaluate_signals.py`；
- Phase 10A/10B/10D 标为 archived historical scripts；
- 不要把旧 phase scripts 作为 current active runner；
- 不新增页面；
- 不改变研究结论。

## 五、测试

新增或更新 tests：

1. active `scripts/` does not contain:
   - `run_phase10a_signal_backtest.py`
   - `run_phase10a_r_diagnostics.py`
   - `run_phase10b_tail_diagnostics.py`
   - `run_phase10d_tail_aware_variants.py`

2. archive contains all four legacy files

3. `scripts/evaluate_signals.py` exists

4. `scripts/evaluate_signals.py --help` works or parser test passes

5. actual-script-map mentions:
   - active entrypoint
   - archive location
   - Phase 13 NOT STARTED

## 六、质量检查

新增：

```text
phase12d_h3_r_active_scripts_cleanup_quality_checks.csv
```

至少包括：

- evaluate_signals.py exists
- no active Phase 10A script in scripts/
- no active Phase 10A-R script in scripts/
- no active Phase 10B script in scripts/
- no active Phase 10D script in scripts/
- archive contains all four legacy scripts
- archive README exists
- actual-script-map updated
- active pipeline doc exists
- no old outputs modified
- no signal panel modified
- no labels modified
- no full evaluation run
- no real execution
- no alpha claim
- no production claim
- Phase 13 NOT STARTED

## 七、完成标准

完成后提交 commit。

commit message 建议：

```text
Phase 12D-H3-R: remove deprecated phase stubs from active scripts
```

完成后输出：

- commit hash
- deleted active stubs list
- archive verification
- active entrypoint path
- whether actual-script-map updated
- whether Phase 13 remains not started
