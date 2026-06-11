# breakout v0 补做 equal-weight concurrent first-pass

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，而且直接接上上一轮 `1-slot global` first-pass 留下的最自然下一步：**如果不把并发交易全部砍掉，而是允许同时持有、但资金必须在入场时按并发仓位均分，这条 breakout v0 大概还剩多少。**

之所以选这个点：
1. 最近几轮已经把 `cost / split-regime honesty / overlap / 1-slot global` 都补过了；
2. 当前最缺的正是 `1-slot global` 与 `per-asset independent` 之间的中间口径，不然组合层读法会只剩两个极端；
3. 在 13 分钟节奏下，这是一刀很小、但确实能帮助 Jerry 判断“这条线是不是主要靠跨资产并发摊开后的漂亮累计收益撑起来”的真实推进。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 扩展 `capital_allocation_first_pass()`，新增 `equal_weight_concurrent_entry` 模式；
   - 规则很克制：不是逐小时重平衡，只按 **入场时** 的并发仓位数给每笔交易分配有效权重（例如 4 笔并发时，每笔先按 `25%` 权重计）；
   - 新增 durable artifact：
     - `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_entry_first_pass.csv`
   - 同时把 `capital_allocation_first_pass.csv` 扩成三种口径并排：
     - `per_asset_independent`
     - `equal_weight_concurrent_entry`
     - `1_slot_global`
2. 更新 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 原本只写 `1-slot global` 的那段，现在升级成：
     - `capital allocation first-pass：1-slot global / equal-weight concurrent 会把这条线压窄多少？`
   - 页面现在会直接回答：
     - 全保留但均分资金时，收益大概落在哪个量级；
     - 它与 `1-slot global`、`per-asset independent` 之间的关系；
     - 为什么这条线现在仍值得继续做组合层 honesty check，但已经不该再按独立记账累计收益去想象实盘空间。
3. 更新 `docs/TODO.md`
   - 在 breakout follow-up 的 capital-allocation 进度链上补上 `equal-weight concurrent(entry)` first-pass 的正式读法；
   - 并同步更新 `reports/site/plans/momentum_todo.html`。

## 验证 / 证据

### 1) 关键三组 20bps 读法现在齐了

基于现有 `support_breakout_v0_h24/trades.csv`：

- `per-asset independent + 20bps`：`48` 笔、累计约 `75.03%`
- `equal-weight concurrent(entry) + 20bps`：`48` 笔全保留、平均有效仓位权重约 `42.36%`、累计约 `19.40%`
- `1-slot global + 20bps`：只保留 `14/48` 笔（约 `29.17%`）、累计约 `13.83%`

这组对照最有用的一点是：
- breakout v0 不是“一加组合约束就没了”；
- 但也确实不能再把 `75.03%` 直接读成“统一资金下差不多也能拿到”的结果；
- 更诚实的 first-pass 组合层空间，目前大约落在 `13.83% ~ 19.40%` 这个量级，而不是 `75.03%`。

### 2) 页面现在能直接看见这个中间口径

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `equal-weight concurrent(entry)`
  - `42.36%`
  - `19.40%`
- `reports/artifacts/support_breakout_v0_h24/capital_allocation_equal_weight_entry_first_pass.csv` 已生成
- `reports/site/plans/momentum_todo.html` 已同步这条新进度

### 3) 当前更诚实的项目级读法

这轮之后，关于 breakout v0 的组合层口径更清楚了：
- 它仍可继续保留为 `conditional alpha / v0 prototype`；
- 但更像是在“允许并发、但必须分摊资金”时仍有一定空间，而不是能直接照搬 `per-asset independent` 的高累计收益；
- 因此下一步最值得补的，已经不是继续找新 breakout 变体，而是更正式的组合级资金曲线 / sizing honesty。

## 风险 / 边界

1. 这轮仍是 **capital allocation first-pass**，不是正式组合级回测；
2. `equal-weight concurrent(entry)` 是一个刻意保守但仍简化的近似：只按入场时并发仓位均分资金，还没有做逐小时重平衡；
3. 所以它更适合回答“量级大概会被压到哪里”，而不是替代正式 portfolio backtest。

## 下一步建议

下一步最值得接的是：
1. 做一个更正式的组合级资金曲线对照：至少比较 `equal-weight concurrent (hourly / bar-level portfolio path)` 与当前 `entry-only` 近似；
2. 或者把 `support_breakout_confirm_1` 也放进同一套最小 capital-allocation honesty 框架，看确认变体在组合层是否比 raw 更稳。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
