# closure board 补回 breakout 的 confirm_1 同框架证据

## 为什么这次选这个

这轮没有再开新验证，而是把刚刚得到的 `raw vs confirm_1 same-frame compare` 正式补回 `alpha_closure_board`。

原因很直接：
1. breakout 主线刚新增了一个对资源顺序非常关键的结果——`confirm_1` 在同一套 `cost / equal-weight / 1-slot` first-pass 下并没有反超 `raw`；
2. 这个结论如果只留在 breakout 子页里，Jerry 还得自己跳页拼；
3. 现在最值得做的小步，就是把它写回总决策页，让 closure board 继续反映“今天资源该怎么排”。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 在 breakout 这张卡的 `当前最强证据` 段里，补上 `raw vs confirm_1` 的同框架结果：
     - raw `20bps` per-asset / equal-weight / 1-slot 约 `75.03% / 19.40% / 13.83%`
     - confirm_1 对应约 `59.38% / 12.04% / 5.06%`
   - 因此把 breakout 卡的固定读法进一步收紧为：
     - 当前更值得继续押注的主原型仍是 `raw`
     - `confirm_1` 只作为紧邻确认变体继续跟
2. 同步更新 `docs/TODO.md`
   - 在 `comparison / decision board` 的最新补充链里，加上这条 closure-board 级别的结论说明；
   - 让 plans 镜像也一起带出这条新口径。
3. 重建可见产物
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) closure board 已补回 confirm_1 同框架结果

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 的 breakout 卡里已出现：
  - `confirm_1 在同框架下约为 59.38% / 12.04% / 5.06%`
  - `当前更值得继续押注的主原型仍是 raw，而不是 confirm_1`

这说明 breakout 的资源顺序不再只靠 breakout 子页自己解释，而是已经正式回到总决策页。

### 2) TODO / plans 镜像已同步

当前 `comparison / decision board` 的 latest progress 也已补充：
- raw 约 `75.03% / 19.40% / 13.83%`
- confirm_1 约 `59.38% / 12.04% / 5.06%`
- 固定资源顺序不变：`raw` 继续作为 breakout-short 主原型，`confirm_1` 只作为紧邻确认变体跟进。

## 当前更清楚的项目级读法

这轮之后，closure board 对 breakout 线回答得更完整了：
- 这条线仍是 `#2`、值得继续；
- 但继续的对象现在讲得更清楚：**先继续 `raw` 的正式组合级资金曲线 / sizing honesty**；
- `confirm_1` 并不是不能继续，而是当前没有证据支持它抢掉主原型位置。

## 风险 / 边界

1. 这轮是 **总决策页刷新**，不是新回测；
2. 没有新增收益数据，只是把上一轮刚得到的 breakout 证据正式挂回 closure board；
3. 但这正是当前最值钱的小步：让站点总入口和最新资源顺序保持一致。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
