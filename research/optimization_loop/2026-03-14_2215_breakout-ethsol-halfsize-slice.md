# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把 Top 3 里 pending 的那一刀真正交出来——在 `avoid_fluctuating` 已落地前提下，不再继续诊断 weak pair，而是对已经锁定的 residual pair/context 直接做一版**最小条件化 sizing**，看看能不能在不盲目砍并发的前提下给 breakout 线带来净改善。

## 为什么选这个

这一棒是当前最自然、也最该做的结果导向动作：
1. `confirm_1` 是否抢位已经看清；
2. `avoid_fluctuating` 也已经证明自己只是部分修复；
3. `2` 仓弱小时的 pair/context 诊断已经把 residual pocket 收窄到 `ETH+SOL` 一带；
4. 所以现在最值钱的小步，不是再写 gate / protocol / closure-copy，而是直接验证：**如果只动这块 residual pair 口袋，会不会比继续泛化地换分支更有效。**

## 这轮做了什么

### 1) 在 `scripts/build_support_breakout_v0_reports.py` 里补了最小条件化 sizing helper

新增：
- `apply_hourly_pair_sizing_policy(...)`
- `summarize_hourly_pair_sizing_compare(...)`

实现的是一个很克制的 first-pass 规则：
- 不动 raw 主原型定义；
- 不重跑下载；
- 不砍所有 2 仓；
- 只在 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时上，把组合 hourly return 缩成 `0.5x`。

### 2) 新增 durable artifacts

生成并落盘：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

### 3) 把结果同步到网页入口

更新并重建：
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- `docs/TODO.md`

所以这轮不是“只在日志里说做了什么”，而是把结果真正挂回了 breakout 主页、closure board、以及 plans 入口。

## 核心结果

### 1) 这刀最小条件化 sizing 确实有净改善

对比 `gate-only` vs `ETH+SOL pair-conditioned halfsize`（同样是 `20bps hourly mark-to-market`）：

- `gate-only`：
  - cumulative hourly path 约 `15.46%`
  - max drawdown 约 `-9.97%`
- `ETH+SOL pair-conditioned halfsize`：
  - cumulative hourly path 约 `19.90%`
  - max drawdown 约 `-9.04%`

也就是说：
- 路径累计约提升了 `+4.44pp`
- 回撤约再收窄了 `0.93pp`

这已经不是“方向模糊的微改善”，而是一个值得认真看待的小结果。

### 2) 它影响的范围其实很窄

这刀不是粗暴砍仓，而只是动：
- `44/398` 个活跃小时
- 占 gate-only active hours 约 `11.06%`

所以它更像：
- **针对 residual weak pair 的小型 sizing honesty 修补**
而不是：
- “把 breakout 线整体改成另一个分支”
- 或“简单粗暴限制所有并发”

### 3) 被压的 residual pair pocket 本身也明显收窄了

`ETH+SOL` 两仓口袋的条件累计：
- 原本约 `-7.17%`
- 半仓后约 `-3.61%`

主要还是长在这几块：
- `test + validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

这说明当前“最值得动”的并不是所有 2 仓，而确实是 `ETH+SOL` 这一块 residual pair 结构。

## 这轮后的项目级读法

这轮之后 breakout 线的读法又更收了一层：

1. `raw` 仍是 breakout-short 主原型；
2. `confirm_1` 仍没有在更现实口径下翻盘；
3. `avoid_fluctuating` 是有帮助的最小 gate，但不是万能开关；
4. 在此基础上，再对 `ETH+SOL` residual pair 做一刀最小 halfsize，已经能进一步改善路径与回撤；
5. 所以下一步更像该继续做 **targeted sizing honesty / holdout 复核**，而不是继续做变体排序或继续泛化诊断 weak pair。

## 验证

已验证：
- `support_breakout_v0_h24/report.html` 出现新段：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
- 页面中已出现关键数值：
  - `44/398`
  - `11.06%`
  - `15.46% -> 19.90%`
  - `-9.97% -> -9.04%`
  - `-7.17% -> -3.61%`
- `alpha_closure_board` 已同步更新成：
  - breakout 线不再停留在“应该做最小条件化 sizing”，而是明确写成“已经做出 first-pass 改善，下一步该进更严格 holdout / walk-forward honesty”。
- `docs/TODO.md` 与 `plans/momentum_todo.html` 已同步将这刀结果写回 Top 3/主入口。

## 风险 / 边界

1. 这仍是 **first-pass 条件化 sizing 切片**，不是正式 portfolio engine；
2. 当前半仓规则是 pair-level heuristic，不是从完整优化流程里学出来的通用 sizing policy；
3. 因此它证明的是“这块 residual pocket 不是完全不可动”，还没有证明“这就是 breakout 主原型应默认采用的 sizing 规则”。

## 下一步建议

如果继续这条线，最值得做的是：
1. 把 `ETH+SOL pair-conditioned halfsize` 推到更严格的 `holdout / walk-forward / portfolio honesty` 里复核；
2. 再决定它是可迁移改进，还是当前样本里的 lucky patch；
3. 若还想更克制一点，再补一刀更窄的 `context-conditioned sizing`（例如只动 `test+validate × up`），看看能不能保住大部分改善、同时减少动作范围。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 等路径在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
