# breakout v0 补做 1-slot global first-pass

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，而且直接接上上一轮 overlap 审计留下的最自然下一步：**如果不再允许跨资产并发摊开，而是全局任何时刻只允许 1 笔仓位，这条线还剩多少。**

之所以选这个点：
1. 上一轮已经证明当前页面的结果明显带着 cross-asset 并发读法；
2. 在 13 分钟节奏下，先补一个最朴素的 `1-slot global` first-pass，比仓促做完整资金曲线更诚实；
3. 这一步能直接帮助 Jerry 判断：这条 breakout v0 到底是“加一点组合约束就没了”，还是“收窄后仍值得继续补更正式的组合级 honesty”。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `capital_allocation_first_pass()`；
   - 基于已有 `support_breakout_v0_h24/trades.csv` 做最朴素的 `1-slot global` greedy 对照：按入场时间顺序，只要上一笔全局仓位还没平掉，后续重叠候选就跳过；
   - 新增两个 durable artifacts：
     - `reports/artifacts/support_breakout_v0_h24/capital_allocation_first_pass.csv`
     - `reports/artifacts/support_breakout_v0_h24/capital_allocation_1slot_selected_trades.csv`
2. 更新 `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增专门一段：`1-slot global first-pass：如果全局一次只允许一笔仓位，这条线还剩多少？`
   - 页面现在会直接回答：
     - 全局只开一笔时还能保留多少交易；
     - `20bps` 下还剩多少平均单笔 / 累计收益；
     - 这是否足以说明该线仍值得继续做组合层 honesty check。
3. 更新 `docs/TODO.md`
   - 在 breakout follow-up 这条收窄任务下补上最新进度说明；
   - 当前固定口径是：这条线并不是“一加组合约束就归零”，但当前页面的漂亮累计收益，确实明显依赖跨资产并发展开后的读法。
4. 重建可见产物：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 关键 1-slot global 数字

基于已有 `support_breakout_v0_h24/trades.csv`：

- `per-asset independent + 20bps`：`48` 笔、平均单笔约 `1.24%`、累计约 `75.03%`
- `1-slot global + 20bps`：只保留 `14/48` 笔（约 `29.17%`）
- `1-slot global + 20bps`：平均单笔仍约 `0.97%`
- `1-slot global + 20bps`：累计仍约 `13.83%`
- 因 overlap 被跳过的交易数：`34`

这说明：
- 这条线并不是“统一资金只开一笔就彻底没了”；
- 但当前网页上的高累计收益，确实很大程度依赖 cross-asset 并发摊开的读法，而不是更保守的组合级执行口径。

### 2) 当前更诚实的组合层读法

这轮之后，关于 breakout v0 的策略层 framing 更清楚了：
- 它仍可保留为 `conditional alpha / v0 prototype`；
- 但已经不能再把当前累计收益直接读成“统一资金也差不多能拿到”；
- 下一步若继续往策略层推进，最值得补的就是：
  - `1-slot global` vs `equal-weight concurrent`
  - 再叠加 `20bps` / `split` / `regime` 的更正式组合级 honesty 对照。

### 3) 页面与计划镜像已同步

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现 `1-slot global first-pass`
- 页面已明确出现 `14/48` 与 `13.83%`
- `docs/TODO.md` 已出现新的 capital-allocation 进度说明
- `reports/site/plans/momentum_todo.html` 已同步更新

## 风险 / 边界

1. 这轮仍是 **capital allocation first-pass**，不是正式组合回测；
2. `1-slot global` 使用的是最朴素的 greedy 先来先做规则，不是最优调度，也不是最终资金模型；
3. 但它已经足够回答一个关键问题：这条线在保守很多的组合约束下，是否仍留有继续研究的空间。答案是：**有，但明显更窄。**

## 下一步建议

下一步最值得接的是：
1. 做一个更正式的 `1-slot global vs equal-weight concurrent` 组合级对照；
2. 如果仍保持极小步，则先只补 `equal-weight concurrent` 的 first-pass 近似页，把 `13.83%` 与并发分摊后的口径放在一起比较。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
