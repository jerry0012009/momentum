# breakout：把 avoid_fluctuating gate 再拆到 split / regime，确认它还卡在哪

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：不再重复证明 `avoid_fluctuating` 比 `confirm_1` 更像样，而是把它已经落地的 `20bps hourly mark-to-market` 结果再拆到 `split / regime`，直接回答：**这个 gate 到底修好了什么、又还没修好什么。**

## 为什么选这个

这轮选这个点，是因为上一轮已经交出了 gate 的整体结果：
- `avoid_fluctuating` 比 raw 有小幅改善；
- 也比“换成 confirm_1”更像样；
- 但 `test` 仍为负。

真正还缺的一刀，是把这条结论继续拆细，不然“有改善但不万能”仍然太笼统。最值得补的不是再开新变体，而是把 gate 后的 `hourly path` 继续拆到 `split / regime`，看问题现在究竟集中在哪些口袋。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 给 `support_breakout_v0_h24` 主报告新增一段：
     - **把 gate 后的 hourly path 再拆开看：它到底还卡在哪？**
   - 复用已落盘的：
     - `avoid_fluctuating_capital_allocation_equal_weight_hourly_by_split_20bps.csv`
     - `avoid_fluctuating_capital_allocation_equal_weight_hourly_by_regime_20bps.csv`
   - 把 `split / regime` 两张表正式挂回页面，而不是只留 artifact。
2. 更新 `docs/TODO.md`
   - 在 breakout 详细收口段补入更细一层的正式读法：
     - `train / validate` 仍为正；
     - `test` 仍为负；
     - `up` 已被磨平到小正；
     - `down` 仍为小负；
     - 真正最像样的仍是 `flat`。
3. 重建可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) gate 最明显修的是 `up`，不是整个后段稳定性

在 `20bps hourly mark-to-market` 下：
- raw 的 `up` 约 `-1.99%`
- `avoid_fluctuating` 的 `up` 约 `+0.95%`

这说明 gate 的第一价值很清楚：它确实把原来最刺眼的 `up` 弱口袋，至少先从负值磨到了小正。

### 2) 但 `test` 依然没被修好

`avoid_fluctuating` 的 `split` 拆分结果：
- `train`：约 `+8.16%`
- `validate`：约 `+5.52%`
- `test`：约 `-2.67%`

这说明 gate 并没有把 breakout 线变成“后段也稳定”的版本；它只是把伤口缝小了一点，但没有缝好。

### 3) 现在更该盯的是 `down/test` 尾部风险，而不是确认变体排序

`avoid_fluctuating` 的 `regime` 拆分结果：
- `up`：约 `+0.95%`
- `down`：约 `-1.52%`
- `flat`：约 `+16.79%`

因此这轮之后更诚实的项目级读法是：
- gate 的确有用；
- 但它主要修的是 `up`，而不是把所有弱口袋都修掉；
- breakout 线后续若继续补组合层 honesty，更该盯 `test/down` 的尾部风险，而不是再回头纠结 `confirm_1` 会不会抢位。

## 验证

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `把 gate 后的 hourly path 再拆开看：它到底还卡在哪？`
  - `+8.16% / +5.52% / -2.67%`
  - `+0.95% / -1.52% / +16.79%`
- `docs/TODO.md` 已补入同样口径；
- `reports/site/plans/momentum_todo.html` 已同步。

## 当前更诚实的读法

当前 breakout 线的口径可以进一步收紧成：
- `raw` 仍是主原型；
- `confirm_1` 不值得继续抢位；
- `avoid_fluctuating` 是有帮助的最小环境 gate；
- 但它主要只修了 `up`，并没有把 `test/down` 尾部风险洗掉。

所以，如果下一轮还继续往策略层推进，更值得花资源的方向是：**在保住这点 gate 改进的前提下，继续压低 `test/down` 风险。**

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
