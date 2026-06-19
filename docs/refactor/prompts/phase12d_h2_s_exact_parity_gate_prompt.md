# Phase 12D-H2-S：Exact Parity Gate Clarification & Spread Root-Cause Investigation

## 背景

Phase 12D-H2-R 已经修复了 H2 的主要 blocker：parity harness 现在直接调用 public `momentum.signal_evaluation` API，而不是 inline `fast_rank_ic` / `fast_quantile_spread`。

但是审阅发现 H2-R 仍不能直接放行 H3 wrapper refactor，原因有两个：

1. **Gate 逻辑不一致**

文档写：

- H3 conditionally open

但脚本逻辑中：

```python
ric_ok = ric_exact == len(ric_df)
sp_ok = (sp_exact + sp_behavioral) == len(spread_df)
overall = "PASS" if ric_ok and sp_ok else "NEEDS_INVESTIGATION"
print(f"H3 gate: {'OPEN' if ric_ok and sp_ok else 'BLOCKED — investigate before H3'}")
```

由于 RankIC 是 12/12 INVESTIGATE，`ric_ok` 为 False，因此脚本实际会输出 H3 gate BLOCKED。

文档和代码不能冲突。

2. **Quantile Spread 只有 BEHAVIORAL parity**

当前 spread 是：

- direction 一致
- order of magnitude 一致
- 但不是 exact parity
- mean_spread diff 可达约 1e-3

这说明新 public API 还不能直接替代旧 Phase 10A 的 spread 计算。如果现在把旧 `run_phase10a_signal_backtest.py` 改成 wrapper，历史输出可能改变。

因此 H3 full wrapper refactor 不能直接开始。

## 本轮目标

执行 Phase 12D-H2-S：

- 统一 gate 逻辑；
- 把 RankIC 的 “INVESTIGATE due to rounded reference” 改成清晰状态；
- 对 Quantile Spread 做 exact parity root-cause investigation；
- 明确 H3 是否可开放、开放范围是什么。

## 允许修改

- `scripts/run_signal_evaluation_parity_harness.py`
- `docs/refactor/SIGNAL_EVALUATION_PARITY_HARNESS.md`
- `phase12d_h2_signal_evaluation_parity_quality_checks.csv`
- 可新增：`docs/refactor/SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md`
- 可新增：`research/factor_runs/crypto_top50_factor_library/phase12d_h2_s_spread_root_cause.csv`
- 可新增或更新相关 unit tests

## 不允许修改

- 不要修改 `scripts/run_phase10a_signal_backtest.py`
- 不要修改 `scripts/run_phase10a_r_diagnostics.py`
- 不要修改 `scripts/run_phase10b_tail_diagnostics.py`
- 不要修改 `scripts/run_phase10d_tail_aware_variants.py`
- 不要修改旧 Phase 10A 输出文件
- 不要修改 signal panel
- 不要修改 labels
- 不要修改研究结果
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化信号

## 一、修正 RankIC parity 状态

当前 RankIC 的 diff 约为 1e-7，根因是旧参考 CSV 只存 6 位小数。

请不要继续用笼统的 `INVESTIGATE` 表达已解释的参考精度限制。

新增状态：

- `PASS_EXACT`：diff <= strict tolerance
- `PASS_ROUNDED_REFERENCE`：diff 超过 strict tolerance，但可由旧 CSV rounding precision 解释
- `NEEDS_INVESTIGATION`：无法由 reference rounding 解释
- `MISSING`

对 RankIC：

- 如果 old value 只有 6 位小数，则 rounding tolerance 应为 `0.5e-6` 或更严格；
- 如果 diff <= rounding tolerance，则 status = `PASS_ROUNDED_REFERENCE`；
- 不要把它继续写成普通 INVESTIGATE。

输出中增加字段：

- `reference_precision_digits`
- `rounding_tolerance`
- `precision_status`
- `parity_level`

## 二、修正 H3 gate 逻辑

H3 gate 必须明确区分：

### 1. `OPEN_FOR_RANKIC_WRAPPER_ONLY`

条件：

- RankIC 为 `PASS_EXACT` 或 `PASS_ROUNDED_REFERENCE`
- Spread 仍为 `BEHAVIORAL`

含义：

- 可以考虑只把 RankIC 相关逻辑 wrapper 化；
- 不允许 full Phase 10A wrapper。

### 2. `BLOCK_FULL_WRAPPER_UNTIL_SPREAD_EXACT`

条件：

- Spread 不是 exact parity，仅 behavioral compatibility。

含义：

- 不能把整个旧 Phase 10A 脚本替换成新模块；
- 必须先调查 spread 差异。

### 3. `OPEN_FULL_WRAPPER`

条件：

- RankIC exact or rounded-reference pass；
- Spread exact parity pass；
- n_periods exact match；
- no missing.

### 4. `BLOCKED`

条件：

- RankIC 有 unexplained investigate；
- Spread direction mismatch；
- missing input；
- n_periods mismatch not explained.

## 三、Spread exact parity root-cause investigation

请新增一个小型诊断，不要修改旧输出。

目标：解释为什么 new public `compute_quantile_spread` 和旧 Phase 10A spread 不是 exact parity。

必须比较以下可能原因：

1. 旧脚本使用的是几分位？5 quantiles 还是其他？
2. 旧脚本 top-bottom 方向是否与新模块一致？
3. 旧脚本是否做了 winsorization / trimming？
4. 旧脚本是否按 timestamp 单独 qcut？
5. 旧脚本是否使用 `duplicates="drop"`？
6. 旧脚本是否在不同 symbol universe 上计算？
7. 旧脚本是否先过滤 NaN，再分桶？
8. 旧脚本是否对 bucket 数不足的 timestamp 做了不同处理？
9. 旧脚本是否按 label symbols 50 个币过滤，而不是 signal panel 全 266 个币？
10. 旧脚本是否使用 Alphalens forward_returns_long，而非当前 labels.parquet？

请读取旧脚本 `scripts/run_phase10a_signal_backtest.py`，找出真实逻辑，不要猜。

输出文档：

`docs/refactor/SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md`

必须包含：

- old Phase 10A spread algorithm
- new compute_quantile_spread algorithm
- exact differences
- whether public API should add legacy-compatible mode
- whether wrapper refactor is safe

## 四、如果需要 legacy-compatible mode，只写设计，不要实现

如果发现旧 Phase 10A spread algorithm 与当前 public API 不同，请不要立刻改 public API。

先在文档中建议：

```python
compute_quantile_spread(..., mode="standard" | "legacy_phase10a")
```

但本轮不要实现，除非差异非常小且可安全参数化。

## 五、更新 summary 输出

更新 H2-R/S summary，使 overall_status 不再含糊。

建议字段：

- `check_group`
- `total_checks`
- `exact_count`
- `rounded_reference_count`
- `behavioral_count`
- `investigate_count`
- `missing_count`
- `h3_gate_status`
- `overall_status`

如果当前状态是 RankIC rounded-reference pass + Spread behavioral pass，则：

- `overall_status = PARTIAL_PASS`
- `h3_gate_status = BLOCK_FULL_WRAPPER_UNTIL_SPREAD_EXACT`

## 六、质量检查

更新 quality checks，必须包括：

- RankIC rounded reference status implemented
- RankIC no longer mislabeled as raw INVESTIGATE when explained by reference precision
- H3 gate status explicit
- H3 full wrapper blocked while spread only behavioral
- Spread root-cause investigation document exists
- Old Phase 10A spread algorithm inspected
- No old phase scripts modified
- No old outputs modified
- No signal panel modified
- No labels modified
- No real execution
- No alpha claim
- No production claim
- Phase 13 NOT STARTED

## 七、完成标准

完成后提交 commit。

commit message 建议：

`Phase 12D-H2-S: clarify parity gate and spread exact-parity blocker`

完成后输出：

- commit hash
- RankIC final parity level
- Spread final parity level
- H3 gate status
- Whether full wrapper refactor is allowed
