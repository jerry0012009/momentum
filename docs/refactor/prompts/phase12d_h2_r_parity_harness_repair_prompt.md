# Phase 12D-H2-R：Parity Harness Must Call Public Signal Evaluation API

## 背景

Phase 12D-H2 已完成，但审阅发现一个 blocker：

质量表写：

- `uses compute_rank_ic,PASS,inline fast_rank_ic equivalent`
- `uses compute_quantile_spread,PASS,inline fast_quantile_spread equivalent`

这不符合 H2 的核心目的。

H2 的目的不是写一套“等价的快速实现”，而是验证新模块 `src/momentum/signal_evaluation/` 的公开 API 是否能复现旧 Phase 10A 输出。

如果 parity harness 使用 inline fast implementation，那么它验证的是临时脚本逻辑，不是新模块本身。

因此当前 H2 不能作为 wrapper refactor 的依据。

## 本轮目标

执行 Phase 12D-H2-R：修复 parity harness，使它真正调用 public signal_evaluation API。

必须直接使用：

- `select_forward_return`
- `compute_rank_ic`
- `summarize_rank_ic`
- `compute_quantile_spread`
- `summarize_quantile_spread`
- `check_rankic_spread_consistency`

不要使用 inline fast_rank_ic。
不要使用 inline fast_quantile_spread。
不要复制旧 Phase 10A 的计算逻辑。
不要直接读取旧结果填充新结果。

## 允许修改

- `scripts/run_signal_evaluation_parity_harness.py`
- `docs/refactor/SIGNAL_EVALUATION_PARITY_HARNESS.md`
- `phase12d_h2_signal_evaluation_parity_quality_checks.csv`
- `tests/unit/test_signal_evaluation_parity_schema.py`
- 可新增 `tests/unit/test_signal_evaluation_parity_harness_imports.py`
- 可新增新的 H2-R parity 输出文件，或覆盖 H2 输出文件，但必须明确这是 H2-R rerun

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

## 一、删除 inline fast implementation

在 `scripts/run_signal_evaluation_parity_harness.py` 中删除或停止使用：

- `fast_rank_ic`
- `fast_quantile_spread`
- 任何手写的与 `compute_rank_ic` / `compute_quantile_spread` 重复的指标计算函数

如果出于性能原因保留辅助函数，也不得参与 H2-R parity_status 计算。H2-R 的 parity_status 必须来自 public API 结果。

## 二、直接调用 public API

对每个 `signal_name × horizon`：

1. 从 wide signal panel 转成统一格式：
   - `timestamp`
   - `symbol`
   - `signal_name`
   - `signal_value`

2. 用：

```python
label_h = select_forward_return(labels, horizon=horizon)
```

3. 用：

```python
rankic_ts = compute_rank_ic(signal_df, label_h)
rankic_summary = summarize_rank_ic(rankic_ts)
```

4. 用：

```python
spread_ts = compute_quantile_spread(signal_df, label_h)
spread_summary = summarize_quantile_spread(spread_ts)
```

5. 用：

```python
consistency_status = check_rankic_spread_consistency(rankic_summary, spread_summary)
```

必须在代码里直接 import：

```python
from momentum.signal_evaluation import (
    select_forward_return,
    compute_rank_ic,
    summarize_rank_ic,
    compute_quantile_spread,
    summarize_quantile_spread,
    check_rankic_spread_consistency,
)
```

## 三、调整 tolerance 表述

H2 原 tolerance 过宽，尤其：

- spread tolerance = 2e-3
- positive_fraction tolerance = 1e-2
- n_periods ±2

H2-R 必须区分两类状态：

### 1. Exact/strict parity

用于 RankIC：

- mean_rank_ic tolerance = 1e-9
- t_stat tolerance = 1e-6
- n_periods exact match

如果不能 exact match，标记为 `NEEDS_INVESTIGATION`，不要用宽 tolerance 硬判 PASS。

### 2. Behavioral compatibility

用于 Quantile Spread，如果 public API 与旧 Phase 10A 因 bucket 细节不同无法精确一致，可以标记为：

- `PASS_EXACT`
- `PASS_BEHAVIORAL`
- `NEEDS_INVESTIGATION`
- `FAIL`

其中 `PASS_BEHAVIORAL` 必须满足：

- spread direction 一致；
- order of magnitude 一致；
- 差异原因在文档中解释；
- 不能声称 exact parity。

不要把 behavioral compatibility 写成 plain PASS。

## 四、输出字段调整

RankIC parity 输出至少包含：

- `signal_name`
- `horizon`
- `new_mean_rank_ic`
- `old_mean_rank_ic`
- `diff_mean_rank_ic`
- `new_t_stat`
- `old_t_stat`
- `diff_t_stat`
- `new_n_periods`
- `old_n_periods`
- `parity_status`
- `parity_level`，例如 `EXACT` / `INVESTIGATE`

Quantile spread parity 输出至少包含：

- `signal_name`
- `horizon`
- `new_mean_spread`
- `old_mean_spread`
- `diff_mean_spread`
- `new_median_spread`
- `old_median_spread`
- `new_positive_fraction`
- `old_positive_fraction`
- `new_n_periods`
- `old_n_periods`
- `parity_status`
- `parity_level`，例如 `EXACT` / `BEHAVIORAL` / `INVESTIGATE`
- `difference_reason`

## 五、文档必须诚实

更新 `docs/refactor/SIGNAL_EVALUATION_PARITY_HARNESS.md`：

必须写清楚：

- H2-R 使用 public API，不再使用 inline fast implementation；
- RankIC 是否 exact parity；
- Quantile Spread 是 exact parity 还是 behavioral compatibility；
- 如果 spread 只达到 behavioral compatibility，不得说“新模块完全复现旧 Phase 10A”；
- 下一步 H3 wrapper refactor 的前提是：RankIC exact parity + Spread 至少 behavioral compatibility；
- 如果有任何 fail，应停止 H3。

## 六、质量检查

更新 `phase12d_h2_signal_evaluation_parity_quality_checks.csv`。

必须包含：

- `uses public compute_rank_ic API`
- `does not use inline fast_rank_ic for parity status`
- `uses public compute_quantile_spread API`
- `does not use inline fast_quantile_spread for parity status`
- `uses summarize_rank_ic`
- `uses summarize_quantile_spread`
- `uses check_rankic_spread_consistency`
- `rankic exact parity status reported`
- `quantile spread exact/behavioral status reported`
- `old phase scripts not modified`
- `old Phase 10A outputs not modified`
- `signal panel not modified`
- `labels not modified`
- `no real execution`
- `no alpha claim`
- `no production claim`
- `Phase 13 NOT STARTED`

不要把 “inline equivalent” 标成 PASS。

## 七、测试

新增或更新测试：

1. 检查 parity harness 源码中直接 import public API：
   - `compute_rank_ic`
   - `compute_quantile_spread`
   - `select_forward_return`

2. 检查源码中不包含：
   - `fast_rank_ic`
   - `fast_quantile_spread`
   - `inline fast`

3. 检查 parity output 中有：
   - `parity_level`
   - `difference_reason`（至少 spread 文件需要）

## 八、完成标准

本轮完成后提交 commit。

commit message 建议：

`Phase 12D-H2-R: parity harness uses public signal_evaluation API`

完成后请输出：

- commit hash
- RankIC parity status
- Quantile Spread parity status
- 是否仍允许进入 H3
