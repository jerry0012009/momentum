# Phase 12D-H4：Vectorized Signal Evaluation Fast Path

## 背景

Phase 12D-H3-R 已经完成 active pipeline cleanup：

- `scripts/evaluate_signals.py` 成为 active canonical entrypoint；
- 旧 Phase 10A / 10A-R / 10B / 10D 脚本已从 active `scripts/` 删除；
- 旧脚本只保留在 `archive/legacy_phase_scripts/phase10/`；
- actual-script-map 已更新 active entrypoint 和 archive refs。

现在 active path 已经清楚。下一步处理性能。

当前问题：

- H2-R / H2-T full parity 曾耗时约 30–35 分钟；
- 原因是 `compute_rank_ic` / `compute_quantile_spread` 按 timestamp 做 Python groupby loop；
- 未来如果每次新增信号或跑 regression 都要等 30 分钟，开发体验不可接受。

## 本轮目标

执行 Phase 12D-H4：Vectorized Signal Evaluation Fast Path。

目标：

1. 加速 active `signal_evaluation` 计算；
2. 不改变 public API 的用户使用方式；
3. 不新增一堆用户可见 mode；
4. 保持结果与当前 reference implementation 一致；
5. 将 3 signals × 4 horizons 的 active evaluation runtime 从约 30–35 分钟降到可接受范围；
6. 不启动 Phase 13，不接交易所，不做实盘。

## 设计原则

### 1. 不增加用户心智负担

用户不应该在日常使用里看到：

```python
compute_rank_ic(..., fast=True)
compute_rank_ic(..., engine="vectorized")
compute_rank_ic(..., engine="slow")
```

公共 API 应保持简单：

```python
compute_rank_ic(signal_df, label_df)
compute_quantile_spread(signal_df, label_df)
```

如果需要 reference implementation，请使用 private/internal function，例如：

```python
_compute_rank_ic_reference(...)
_compute_quantile_spread_reference(...)
```

不要让日常用户手动选择 fast/slow。

### 2. 速度优化不能改变结果语义

必须验证：

- RankIC 与当前 reference implementation 一致；
- Quantile Spread standard mode 与当前 qcut/reference implementation 一致；
- Quantile Spread legacy_phase10a mode 与旧 Phase 10A parity 一致；
- n_periods 不变；
- spread sign 不变；
- no silent dropping of timestamps/symbols。

### 3. 先做 active path 优化，不做新研究

不要新增因子。
不要新增信号。
不要启动 Phase 13。
不要连接交易所。
不要做真实 paper trading。

## 允许修改

- `src/momentum/signal_evaluation/rank_ic.py`
- `src/momentum/signal_evaluation/quantile_spread.py`
- `src/momentum/signal_evaluation/README.md`
- `scripts/evaluate_signals.py`
- 可新增 `src/momentum/signal_evaluation/_vectorized.py`
- 可新增 `tests/unit/test_signal_evaluation_vectorized_rank_ic.py`
- 可新增 `tests/unit/test_signal_evaluation_vectorized_spread.py`
- 可新增 `tests/unit/test_evaluate_signals_performance_contract.py`
- 可新增 `docs/refactor/SIGNAL_EVALUATION_PERFORMANCE.md`
- 可新增 `phase12d_h4_vectorized_evaluation_quality_checks.csv`
- 可新增 benchmark output：`research/factor_runs/crypto_top50_factor_library/phase12d_h4_signal_evaluation_benchmark.csv`

## 不允许修改

- 不要修改 archived legacy phase scripts
- 不要恢复 active Phase 10 scripts
- 不要修改旧 Phase 10A outputs
- 不要修改 signal panel
- 不要修改 labels
- 不要改研究结论
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化或选择信号
- 不要覆盖旧 historical outputs

## 一、优化 RankIC

当前 RankIC 很慢的主要原因：

- 每个 timestamp groupby；
- 每组 `.corr(method="spearman")`；
- 大量 Python loop。

建议实现：

1. 将 merged DataFrame pivot 为 timestamp × symbol 矩阵；
2. 对 signal matrix 和 return matrix 分别按 row rank；
3. 对 rank 后矩阵按 row 做 Pearson correlation；
4. 保留 NaN mask；
5. 输出与当前 `compute_rank_ic` 相同 schema：
   - timestamp
   - rank_ic
   - n_symbols

必须处理：

- missing symbol；
- constant signal row；
- constant return row；
- insufficient symbols；
- NaN。

## 二、优化 Quantile Spread

### standard / qcut mode

如果完全 vectorized qcut 难以精确复现 pandas qcut，可以先保留 reference path，但要避免不必要重复。

可接受方案：

- legacy_phase10a mode 先向量化；
- standard mode 保持 reference implementation，但文档说明标准 qcut 暂未完全 vectorized；
- active evaluator默认如果使用 standard 仍可运行，但 benchmark 分别记录 standard 与 legacy runtime。

### legacy_phase10a mode

legacy mode 可以更容易优化：

1. pivot 为 timestamp × symbol 矩阵；
2. 对每行按 signal descending argsort；
3. 取 top n_q 和 bottom n_q；
4. 计算 return mean difference；
5. 输出与当前 `compute_quantile_spread(..., mode="legacy_phase10a")` 相同 schema。

必须保证与当前 legacy reference implementation parity：

- mean_spread diff <= 1e-12 on toy tests；
- n_top/n_bottom same；
- n_periods same。

## 三、evaluate_signals.py 性能路径

`scripts/evaluate_signals.py` 应避免重复读文件和重复转换。

要求：

- labels 每个 horizon 只 select 一次；
- signal panel 只加载一次；
- 尽量避免每个 signal × horizon 重新做昂贵 merge；
- 仍然输出同样 canonical files：
  - `signal_evaluation_rankic_summary.csv`
  - `signal_evaluation_quantile_spread_summary.csv`
  - `signal_evaluation_consistency_summary.csv`
  - `signal_evaluation_manifest.json`

如果需要新增 internal batch helper，可以新增：

```python
_evaluate_signal_horizon_fast(...)
```

但不要把它作为用户主入口。

## 四、benchmark

不要反复跑 30 分钟 baseline。baseline 可引用 H2-R/H2-T 记录：约 30–35 分钟。

本轮只需要：

1. 跑一次 current optimized active evaluation；
2. 记录 wall-clock seconds；
3. 输出 benchmark CSV。

Benchmark CSV 字段：

- run_id
- timestamp
- signal_count
- horizon_count
- spread_mode
- rows_signal_panel
- rows_labels
- elapsed_seconds
- baseline_elapsed_seconds_estimate
- speedup_estimate
- notes

目标：

- full 3 signals × 4 horizons should be significantly faster than 30 min；
- 理想目标 < 5 min；
- 如果没有达到，必须解释 bottleneck。

## 五、测试

新增测试：

1. vectorized RankIC equals reference on toy data；
2. vectorized RankIC handles NaN；
3. vectorized RankIC handles constant row；
4. vectorized legacy spread equals reference on toy data；
5. vectorized legacy spread keeps n_top/n_bottom；
6. standard spread behavior unchanged；
7. evaluate_signals CLI still parses arguments；
8. no active Phase 10 scripts restored；
9. Phase 13 NOT STARTED。

## 六、文档

新增或更新：

```text
docs/refactor/SIGNAL_EVALUATION_PERFORMANCE.md
```

必须写：

- previous bottleneck；
- new vectorized approach；
- what is optimized；
- what is not optimized；
- benchmark result；
- correctness/parity status；
- no trading / no production / no Phase 13。

## 七、质量检查

新增：

```text
phase12d_h4_vectorized_evaluation_quality_checks.csv
```

至少包括：

- rank_ic vectorized path implemented
- rank_ic parity tests pass
- legacy spread vectorized path implemented
- legacy spread parity tests pass
- standard spread behavior unchanged
- evaluate_signals still canonical active entrypoint
- no active Phase 10 scripts restored
- benchmark CSV produced
- benchmark runtime recorded
- no old outputs modified
- no signal panel modified
- no labels modified
- no real execution
- no alpha claim
- no production claim
- Phase 13 NOT STARTED

## 八、完成标准

完成后提交 commit。

commit message 建议：

```text
Phase 12D-H4: vectorized signal evaluation fast path
```

完成后输出：

- commit hash
- benchmark elapsed seconds
- speedup estimate vs 30–35 min baseline
- RankIC parity status
- Spread parity status
- whether active pipeline remains clean
- whether Phase 13 remains not started
