# Phase 12D-H2-T：Legacy-Compatible Quantile Spread Mode

## 背景

Phase 12D-H2-S 已经完成：

- RankIC 状态从 INVESTIGATE 修正为 PASS_ROUNDED_REFERENCE；
- Spread 差异根因已找到：旧 Phase 10A 使用 rank-based head/tail；当前 public API 使用 pd.qcut quintile boundaries；
- Spread 目前只有 BEHAVIORAL parity，差异约 4–8%。

但是 H2-S 的结论“qcut 更正确，所以不做 legacy mode，behavioral parity 足够进入 H3”不应接受。

原因：

H3 的目标是把旧 Phase 10A 脚本改成 wrapper。wrapper 的基本要求是**不改变旧 Phase 10A 输出语义**。如果 public API 只有 qcut 模式，那么旧脚本一旦 wrapper 化，spread 输出会发生 4–8% 差异。即使方向一致，也不是历史可复现。

因此必须新增 legacy-compatible spread mode。

## 本轮目标

执行 Phase 12D-H2-T：为 `compute_quantile_spread` 增加 legacy-compatible rank head/tail 模式，并使用该模式复现旧 Phase 10A spread 输出。

目标不是判断 qcut 和 rank-head-tail 谁更“正确”。目标是：

- `mode="qcut"` 或 `mode="standard"`：保留当前标准方法；
- `mode="rank_head_tail"` 或 `mode="legacy_phase10a"`：精确复现旧 Phase 10A spread 算法；
- parity harness 对旧 Phase 10A 输出必须使用 legacy mode；
- 未来新研究可以选择 standard mode，但历史 wrapper 必须用 legacy mode。

## 允许修改

- `src/momentum/signal_evaluation/quantile_spread.py`
- `src/momentum/signal_evaluation/README.md`
- `scripts/run_signal_evaluation_parity_harness.py`
- `docs/refactor/SIGNAL_EVALUATION_PARITY_HARNESS.md`
- `docs/refactor/SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md`
- `phase12d_h2_signal_evaluation_parity_quality_checks.csv`
- `tests/unit/test_signal_evaluation_quantile_spread.py`
- 可新增 `tests/unit/test_signal_evaluation_legacy_spread.py`

## 不允许修改

- 不要修改 `scripts/run_phase10a_signal_backtest.py`
- 不要修改 `scripts/run_phase10a_r_diagnostics.py`
- 不要修改 `scripts/run_phase10b_tail_diagnostics.py`
- 不要修改 `scripts/run_phase10d_tail_aware_variants.py`
- 不要修改旧 Phase 10A 输出文件
- 不要修改 signal panel
- 不要修改 labels
- 不要改研究结果
- 不要启动 Phase 13
- 不要连接交易所 API
- 不要新增实盘、下单、交易逻辑
- 不要优化信号

## 一、扩展 compute_quantile_spread

在 `src/momentum/signal_evaluation/quantile_spread.py` 中扩展：

```python
compute_quantile_spread(
    signal_df,
    label_df,
    signal_col="signal_value",
    return_col="forward_return",
    group_col="timestamp",
    n_quantiles=5,
    mode="qcut",
    quantile_frac=0.20,
    min_cross_section=None,
)
```

支持至少两个 mode：

### mode="qcut" / mode="standard"

保留当前实现：

- 每个 timestamp 用 `pd.qcut` 分桶；
- top bucket = max bucket；
- bottom bucket = min bucket；
- spread = top_mean - bottom_mean。

### mode="rank_head_tail" / mode="legacy_phase10a"

实现旧 Phase 10A 算法：

```python
QUANTILE_FRAC = 0.20
MIN_CROSS_SECTION = 10

for ts, group in merged.groupby(group_col):
    valid = group[[signal_col, return_col]].dropna()
    n = len(valid)
    if n < min_cross_section:
        continue or append NaN according to existing convention
    n_q = max(int(n * quantile_frac), 1)
    ranked = valid.sort_values(signal_col, ascending=False)
    top = ranked.head(n_q)
    bottom = ranked.tail(n_q)
    spread = top[return_col].mean() - bottom[return_col].mean()
```

必须输出同一 schema：

- timestamp
- top_mean
- bottom_mean
- spread
- n_top
- n_bottom

对于 legacy mode，`n_top` 和 `n_bottom` 应等于 n_q。

## 二、不要改变默认行为，除非明确决定

为了不破坏 H1/H1-R 已有语义，建议默认仍为：

```python
mode="qcut"
```

但 parity harness 中比较旧 Phase 10A 时必须显式传：

```python
compute_quantile_spread(..., mode="legacy_phase10a")
```

## 三、更新 parity harness

在 `scripts/run_signal_evaluation_parity_harness.py` 中：

- RankIC 保持 public API 计算；
- Spread parity 使用：

```python
compute_quantile_spread(sig_df, label_h, n_quantiles=5, mode="legacy_phase10a")
```

目标：Spread 由 BEHAVIORAL 提升为 EXACT 或 PASS_ROUNDED_REFERENCE。

如果仍不 exact：

- 不要调宽 tolerance；
- 输出 NEEDS_INVESTIGATION；
- 记录真实差异；
- 继续调查旧脚本细节。

## 四、更新文档

更新：

- `docs/refactor/SIGNAL_EVALUATION_PARITY_HARNESS.md`
- `docs/refactor/SIGNAL_EVALUATION_SPREAD_PARITY_INVESTIGATION.md`
- `src/momentum/signal_evaluation/README.md`

必须写清楚：

- qcut/standard mode 与 legacy_phase10a mode 的区别；
- standard mode 不等于旧 Phase 10A；
- legacy_phase10a mode 是为了历史可复现；
- H3 wrapper 如果要保持旧 Phase 10A 输出，应使用 legacy_phase10a；
- 未来新研究可选择 standard mode，但必须明确记录 mode。

不要再写“qcut 更正确，所以 legacy 不需要”。这种判断可以作为讨论，但不能作为 wrapper refactor 的依据。

## 五、更新 gate

H3 gate 应改为：

### OPEN_FULL_WRAPPER

条件：

- RankIC = EXACT 或 PASS_ROUNDED_REFERENCE；
- Spread using legacy_phase10a = EXACT 或 PASS_ROUNDED_REFERENCE；
- n_periods exact；
- no missing；
- old outputs not modified。

### OPEN_STANDARD_V2_ONLY

条件：

- qcut standard mode 只有 behavioral；
- legacy mode 未实现或未 exact；
- 只能生成新版本 V2 outputs，不能替换旧 Phase 10A wrapper。

### BLOCKED

条件：

- RankIC unexplained mismatch；
- Spread legacy mode mismatch；
- missing data；
- old outputs modified。

## 六、测试

新增或更新 tests：

1. legacy mode with 10 symbols and quantile_frac=0.2:
   - top = top 2 by rank
   - bottom = bottom 2 by rank
   - spread expected exactly

2. legacy mode uses fixed n_q:
   - if n=50, n_q=10
   - n_top=10, n_bottom=10

3. qcut mode and legacy mode can produce different spreads on tied/boundary values

4. invalid mode raises ValueError

5. parity harness explicitly uses mode="legacy_phase10a" for old Phase 10A spread comparison

6. H3 gate opens only if legacy spread parity is exact / rounded-reference pass

## 七、质量检查

更新 quality checks，必须包含：

- compute_quantile_spread supports qcut/standard mode
- compute_quantile_spread supports legacy_phase10a mode
- legacy mode matches rank_head_tail algorithm
- parity harness uses legacy_phase10a mode for old Phase 10A spread comparison
- spread exact parity reported
- H3 OPEN_FULL_WRAPPER only if legacy spread exact/rounded pass
- qcut behavioral mode not used as full wrapper gate
- old Phase 10A scripts not modified
- old Phase 10A outputs not modified
- signal panel not modified
- labels not modified
- no real execution
- no alpha claim
- no production claim
- Phase 13 NOT STARTED

## 八、完成标准

完成后提交 commit。

commit message 建议：

`Phase 12D-H2-T: add legacy_phase10a spread mode for exact parity`

完成后输出：

- commit hash
- RankIC parity level
- Spread standard/qcut parity level
- Spread legacy_phase10a parity level
- H3 gate status
- 是否允许 full wrapper refactor
