# closure board 回挂 breakout v0 的现实约束读法

## 为什么这次选这个

这轮没有再开新验证，而是把最近几轮已经补完的 `breakout v0` first-pass 现实约束结果，正式回挂到最上层的 `alpha_closure_board`。

原因很直接：
1. 最近几轮已经把 `cost / overlap / 1-slot global / equal-weight concurrent(entry)` 都补出来了；
2. 但 `closure board` 顶层口径还停留在“这条线还没吃进成本与资金约束”的旧读法，已经不够诚实；
3. 这是一刀很小、但对 Jerry 判断“breakout-short follow-up 现在还值不值得排在 #2”非常有帮助的总览收口动作。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 把 breakout-short 这张卡的 `当前最强证据` 改成更贴近最新现实约束结果的版本；
   - 明确写回三组最关键数字：
     - `20bps + per-asset independent` 累计约 `75.03%`
     - `20bps + equal-weight concurrent(entry)` 累计约 `19.40%`
     - `20bps + 1-slot global` 累计约 `13.83%`
   - 同时把 `当前不能过度解读什么` 与 `下一步最值得做什么` 一并更新：
     - 不再说“还没吃进成本与资金约束”；
     - 改成“已经补了 first-pass，但还缺正式组合级资金曲线 / sizing honesty，以及 confirm_1 的同框对照”。
2. 更新 `docs/TODO.md`
   - 在 `comparison / decision board` 那条已完成任务下，补一条最新进度说明；
   - 正式写死当前 top-level 读法：这条线仍值得继续，但应按 `conditional alpha` 理解，而且不能再按独立记账累计收益去想象执行空间。
3. 重建可见产物：
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) closure board 已回挂 breakout 的现实约束数字

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已明确出现：
  - `75.03%`
  - `19.40%`
  - `13.83%`
- 同页 breakout 卡片的 `当前不能过度解读什么` 已改成：
  - 仍缺正式组合级资金曲线、rolling OOS honesty、以及 `confirm_1` 在同约束下的并排对照。

这说明最上层决策页现在终于和最近几轮 breakout follow-up 的结果对齐了。

### 2) 当前 breakout 的 top-level 读法更诚实了

这轮之后，顶层口径不再是：
- “这条线还没吃进成本与资金约束，所以先别多想。”

而是更具体地变成：
- 它 **不是** 一加现实约束就归零；
- 但也 **不能** 再把 `per-asset independent` 下的高累计收益，当作统一资金约束下也差不多能拿到；
- 因此它现在更像：**仍值得继续的 `conditional alpha / strategy-facing follow-up`，但下一步必须补正式组合级资金曲线 / sizing honesty。**

### 3) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 已追加 breakout realism 的总览口径说明；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样内容。

## 风险 / 边界

1. 这轮是 **总览页刷新**，不是新回测；
2. 没有新增收益、成本或 OOS 数据；
3. 但它确实修正了一个会误导顶层判断的旧口径：现在 closure board 对 breakout 线的描述终于和最近几轮 first-pass honesty 结果一致了。

## 下一步建议

下一步最值得接的是：
1. breakout v0 的正式组合级资金曲线 / sizing honesty；
2. 或把 `support_breakout_confirm_1` 放进同一套成本 / 执行 / 环境约束框架，看它是否比 raw 更稳。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
