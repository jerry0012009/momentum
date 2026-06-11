# breakout v0 补做 cross-asset overlap first-pass

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，但不再补纯文案，而是补一个真正更接近策略执行层的小验证：**当前这个 v0 一旦跨资产一起跑，仓位会不会明显扎堆，导致“看起来不错的 per-asset prototype”其实并不等于“可直接照搬的组合级结果”。**

之所以选这个点：
1. breakout v0 这条线最近已经把成本、split/regime honesty、环境 gate 都收得比较清楚；
2. 当前还缺一个与 `non-overlap / capital allocation` 直接相关、但足够小的 first-pass 事实层；
3. 现有 `trades.csv` 已经足够回答这个问题，不需要重跑下载或新开重回测。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `overlap_summary_table()`；
   - 基于已有 `reports/artifacts/support_breakout_v0_h24/trades.csv` 统计 cross-asset 并发持仓情况；
   - 新增两个 durable artifacts：
     - `reports/artifacts/support_breakout_v0_h24/cross_asset_overlap_summary.csv`
     - `reports/artifacts/support_breakout_v0_h24/cross_asset_overlap_profile.csv`
2. 更新 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增专门一段：`cross-asset overlap first-pass：这条线一旦跨资产一起跑，会不会被并发仓位放大成另一回事？`
   - 页面现在会直接告诉 Jerry：
     - 有多少入场其实发生在已经有别的仓位开着的时候；
     - 最大并发仓位到几笔；
     - 活跃持仓时间里，高并发状态占比多少。
3. 更新 `docs/TODO.md`
   - 在 breakout follow-up 那条收窄任务下补上最新进度说明；
   - 当前固定口径是：`non-overlap / capital allocation` 已不能再只停留在口头提醒，而该尽快做最小组合约束对照。
4. 重建可见产物：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 关键 overlap 数字

基于现有 `support_breakout_v0_h24/trades.csv`：

- 总交易数：`48`
- 资产数：`4`
- **约 `50.00%` 的入场**发生时已经有至少 `1` 笔别的仓位开着
- **约 `25.00%` 的入场**发生时已经有至少 `2` 笔别的仓位开着
- 最大并发仓位：`4`
- 活跃持仓时间里，约 **`34.80%`** 处在 `4` 笔并发
- 活跃持仓时间里，约 **`74.71%`** 处在至少 `2` 笔并发

这说明：这条线虽然还是一个有意思的 v0 原型，但它已经不是那种“默认只有一笔仓位、顺手就能照搬”的轻量对象。

### 2) 当前更诚实的策略层读法

这轮之后，关于 breakout v0 的 next-step framing 更清楚了：
- 当前页的收益，更像是 **per-asset independent prototype** 的读法；
- 还不是带统一资金上限的组合级结果；
- 所以下一步如果继续往策略层推进，应该优先比较：
  - `per-asset independent`
  - `1-slot global`
  - `equal-weight concurrent`

也就是说，`non-overlap / capital allocation` 现在已经从“以后可能要看”升级成“应优先补的最小 honesty 对照”。

### 3) 页面与计划镜像已同步

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `cross-asset overlap first-pass`
- `docs/TODO.md` 已出现新的 overlap 进度说明
- `reports/site/plans/momentum_todo.html` 已同步更新

## 风险 / 边界

1. 这轮仍是 **first-pass overlap 审计**，不是正式组合级资金模拟；
2. 它回答的是“仓位会不会扎堆”，还没有回答“若统一资金分配后净值会掉多少”；
3. 但它已经足够证明：若忽略 cross-asset 并发与资金分摊，就会把 breakout v0 读得比真实执行更轻松。

## 下一步建议

下一步最值得接的是：
1. 做一个最小 `capital allocation honesty` 对照，至少比较 `per-asset independent` vs `1-slot global / equal-weight concurrent`；
2. 若仍保持极小步，则先只做 `20bps` 口径下的 `1-slot global` first-pass 对照。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
