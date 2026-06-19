# Phase 12D-H4-R：Fix Vectorized RankIC Parity Regression

## 背景

Phase 12D-H4 已完成向量化加速，但审阅发现一个 blocker：

commit message / quality checks 声称：

- Full harness: 24/24 PASS_ROUNDED_REFERENCE
- H3 gate OPEN_FULL_WRAPPER
- vectorized RankIC parity max diff 1.11e-16

但实际 diff 中，`phase12d_h2_t_signal_eval_parity_rankic.csv` 被改成大量：

- `NEEDS_INVESTIGATION`
- `INVESTIGATE`

例如：

- `signal_v0_core_only,4h` diff_mean_rank_ic ≈ 5.19e-06
- `signal_v0_pm_full_structured,4h` diff_mean_rank_ic ≈ 6.34e-06
- 多个 t_stat diff 也超过 rounding tolerance

这说明 H4 的向量化 RankIC 在 full data 上没有保持 H2-T 的 parity。

因此 H4 不能验收。必须先做 H4-R。

## 本轮目标

执行 Phase 12D-H4-R：修复 vectorized RankIC parity regression。

目标：

1. 找出 vectorized RankIC 与 reference / H2-T parity 结果不一致的原因；
2. 修复 vectorized RankIC；
3. 如果短期无法修复，则 public API 自动 fallback 到 reference RankIC，不能输出错误结果；
4. 保留 legacy spread vectorized fast path（如果其 parity 仍为 PASS）；
5. 质量表和文档必须与真实 output 一致；
6. 不启动 Phase 13，不接交易所，不做实盘。

## 允许修改

- `src/momentum/signal_evaluation/_vectorized.py`
- `src/momentum/signal_evaluation/rank_ic.py`
- `scripts/run_signal_evaluation_parity_harness.py`
- `docs/refactor/SIGNAL_EVALUATION_PERFORMANCE.md`
- `phase12d_h4_vectorized_evaluation_quality_checks.csv`
- 可新增 `docs/refactor/SIGNAL_EVALUATION_RANKIC_PARITY_REGRESSION.md`
- 可新增 / 更新 rankic vectorized tests
- 可新增 H4-R benchmark / parity outputs

## 不允许修改

- 不要恢复 active Phase 10 scripts
- 不要修改 archived legacy scripts
- 不要修改旧 Phase 10A outputs
- 不要修改 signal panel
- 不要修改 labels
- 不要改变研究结论
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化信号
- 不要为了通过而调宽 tolerance

## 一、先定位 RankIC regression 根因

请比较以下三组结果：

### A. H2-T reference parity output

H2-T 时 RankIC 应为：

- 12/12 `PASS_ROUNDED_REFERENCE`
- no `INVESTIGATE`

### B. H4 vectorized public API output

H4 后出现多行 `NEEDS_INVESTIGATION`。

### C. reference implementation on the same full input

请在 H4-R 中运行同一 input 上：

- reference RankIC implementation
- vectorized RankIC implementation
- public `compute_rank_ic`

比较每个 signal × horizon 的：

- mean_rank_ic
- t_stat
- n_periods
- max per-timestamp rank_ic diff
- count of timestamps with diff > 1e-12

输出：

```text
research/factor_runs/crypto_top50_factor_library/phase12d_h4_r_rankic_regression_diagnostics.csv
```

字段至少包括：

- signal_name
- horizon
- reference_mean_rank_ic
- vectorized_mean_rank_ic
- diff_mean_rank_ic
- reference_t_stat
- vectorized_t_stat
- diff_t_stat
- reference_n_periods
- vectorized_n_periods
- max_ts_rankic_diff
- n_ts_diff_gt_1e12
- suspected_cause

## 二、重点检查 tie / rank handling

最可能原因：vectorized rank 实现没有完全复现 pandas / scipy Spearman rank behavior。

请重点检查：

1. tie handling 是否使用 average rank；
2. NaN filtering 是否逐 timestamp 后再 rank；
3. constant row 是否和 reference 一样输出 NaN / dropped；
4. symbol alignment 是否一致；
5. pivot_table 是否引入排序或 aggfunc 差异；
6. timestamp inclusion/exclusion 是否一致；
7. t_stat 是否使用相同 n / std / ddof。

如果当前 `_rank_rows` 用 argsort ordinal rank，它不等价于 Spearman average-rank。必须修正。

## 三、修复要求

### 方案 A：修复 vectorized RankIC

如果可以修复：

- vectorized per-timestamp RankIC 与 reference implementation 的 max diff <= 1e-12；
- mean_rank_ic diff <= 1e-12；
- n_periods exact；
- t_stat diff <= 1e-9 或可解释为 floating precision；
- full old CSV parity 回到 12/12 PASS_ROUNDED_REFERENCE。

### 方案 B：RankIC 自动 fallback reference

如果短期无法安全修复 vectorized RankIC：

- `compute_rank_ic` 必须 fallback 到 reference implementation；
- quality check 中写清：RankIC vectorized disabled due to parity regression；
- benchmark 中分别记录：RankIC reference, spread vectorized；
- 不允许 public API 输出 INVESTIGATE 结果却声称 PASS。

正确性优先于速度。

## 四、不要调宽 tolerance

禁止为了让 H4 通过而修改：

- RankIC rounding tolerance
- t_stat tolerance
- n_periods tolerance

如果结果超过 tolerance，必须修算法或 fallback。

## 五、更新 H4 outputs

新增或更新：

```text
phase12d_h4_r_signal_eval_parity_rankic.csv
phase12d_h4_r_signal_eval_parity_spread_legacy.csv
phase12d_h4_r_signal_eval_parity_summary.csv
phase12d_h4_r_rankic_regression_diagnostics.csv
phase12d_h4_r_benchmark.csv
```

要求：

- RankIC parity: 12/12 PASS_ROUNDED_REFERENCE 或 EXACT；
- no INVESTIGATE；
- Spread legacy parity remains PASS_ROUNDED_REFERENCE / EXACT；
- H3 gate remains OPEN_FULL_WRAPPER only if both pass；
- 如果 RankIC fallback reference，仍可 pass，但 benchmark 应诚实记录。

## 六、更新文档

更新：

```text
docs/refactor/SIGNAL_EVALUATION_PERFORMANCE.md
```

必须写清：

- H4 出现过 RankIC parity regression；
- H4-R 如何修复；
- 是否继续启用 vectorized RankIC；
- benchmark 真实结果；
- no Phase 13。

如果 fallback reference：明确写：

```text
RankIC vectorized path disabled until exact parity is proven.
```

## 七、测试

新增 / 更新 tests：

1. vectorized RankIC equals reference on toy data with ties；
2. vectorized RankIC equals reference on toy data with NaNs；
3. vectorized RankIC handles constant row exactly like reference；
4. vectorized RankIC preserves n_periods; 
5. public compute_rank_ic output equals reference on test dataset;
6. full parity summary has no INVESTIGATE rows;
7. quality checks fail if parity output contains INVESTIGATE but says PASS.

## 八、质量检查

更新：

```text
phase12d_h4_vectorized_evaluation_quality_checks.csv
```

必须包括：

- H4 RankIC regression diagnosed
- vectorized RankIC fixed OR safely disabled
- public compute_rank_ic parity restored
- no INVESTIGATE in RankIC parity output
- spread legacy parity remains pass
- H3 gate truthfully computed from actual outputs
- quality table matches actual output files
- benchmark CSV updated
- old outputs not modified
- signal panel not modified
- labels not modified
- no real execution
- no alpha claim
- no production claim
- Phase 13 NOT STARTED

## 九、完成标准

完成后提交 commit。

commit message 建议：

```text
Phase 12D-H4-R: fix vectorized RankIC parity regression
```

完成后输出：

- commit hash
- root cause
- whether vectorized RankIC is enabled or disabled
- RankIC parity status
- Spread parity status
- benchmark elapsed seconds
- whether H3 gate remains open
- whether Phase 13 remains not started
