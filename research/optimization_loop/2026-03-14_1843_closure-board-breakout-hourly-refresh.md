# closure board 补回 breakout 的 hourly portfolio path 结果

## 为什么这次选这个

这轮没有再开新验证，而是把 breakout 线刚刚补出来的 `hourly portfolio path` 真实结果，正式同步回 `alpha_closure_board`。

原因很直接：
1. `support_breakout_v0_h24` 页已经从 `equal-weight concurrent(entry)` 往前推进到更正式的 `hourly mark-to-market` 统一资金曲线；
2. 但总决策页 `alpha_closure_board` 还停留在旧口径，只提到 `entry-only equal-weight / 1-slot`，没有反映最新的组合级结果；
3. 现在最值钱的小步，就是把总入口刷新成和最新 breakout 证据一致，这样 Jerry 不用自己跨页拼“到底还剩多少执行空间”。

## 做了什么改动

1. 更新 `scripts/build_alpha_closure_board_report.py`
   - 把 breakout 卡片的 `当前最强证据` 改成包含最新组合级现实约束：
     - `20bps` 下 raw 的 per-asset 累计约 `75.03%`
     - `equal-weight concurrent(entry)` 约 `19.40%`
     - 更正式的 `equal-weight hourly portfolio path` 约 `14.04%`
     - `1-slot global` 约 `13.83%`
   - 把 breakout 卡的 `not_yet / next` 也同步收紧成最新读法：
     - 不再只泛泛说“还缺 portfolio path”；
     - 明确下一步更该把 `confirm_1` 放进同一套 hourly portfolio path / sizing honesty 里复核，而不是继续扩 breakout 变体。
2. 更新 `docs/TODO.md`
   - 在 `comparison / decision board` 的 latest supplement 链里补上这条 closure-board 级别的 breakout 结果；
   - 让 `reports/site/plans/momentum_todo.html` 也同步带出同样口径。
3. 重建可见产物
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键更新内容

### 1) closure board 现在明确承认：entry-only 口径偏乐观

总决策页现在正式写入：
- `20bps` 下 raw 的：
  - per-asset independent 约 `75.03%`
  - `equal-weight concurrent(entry)` 约 `19.40%`
  - `equal-weight hourly portfolio path` 约 `14.04%`
  - `1-slot global` 约 `13.83%`

这意味着 breakout v0 虽然还没被统一资金曲线直接抹掉，但把 equal-weight 从 entry-only 推到 hourly path 后，结果已经几乎贴近最保守的 `1-slot global`。因此当前更诚实的读法，已经不能再停留在 entry-only 近似。

### 2) closure board 的 breakout 下一步也因此变了

刷新后，`alpha_closure_board` 对 breakout 线给出的 next step 已改成：
- 若继续这条线，优先把 `confirm_1` 放进同一套 `hourly portfolio path / sizing honesty` 里复核；
- 如果 `confirm_1` 在更正式组合约束下也没有更稳，就继续把 `raw` 当 breakout-short 主原型；
- 而不是再开新的 breakout 变体。

## 验证 / 证据

验证命中：
- `reports/site/factors/alpha_closure_board/report.html` 已出现：
  - `equal-weight hourly portfolio path`
  - `14.04%`
  - `优先把 confirm_1 放进同一套 hourly portfolio path / sizing honesty 里复核`
- `docs/TODO.md` 已补入同样口径；
- `reports/site/plans/momentum_todo.html` 也已同步。

## 这轮后的项目级读法

这轮之后，breakout 线在总决策页上的口径终于和子页一致：
- 这条线仍值得继续；
- 但继续时必须按统一资金曲线来理解执行空间，不能再把 entry-only equal-weight 当成够真实的组合结果；
- 最值得接的紧邻小步，就是把 `confirm_1` 也放进同一套 hourly portfolio path 里，看它会不会在更正式组合约束下比 raw 更稳。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
