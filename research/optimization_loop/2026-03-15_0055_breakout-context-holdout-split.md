# breakout context-conditioned sizing：holdout split honesty

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：不再重复写 `ETH+SOL pair-conditioned halfsize` 的旧 headline，而是把**更窄的 `ETH+SOL @ validate/test × up` context-conditioned halfsize** 再按更严格的 holdout 眼光拆开，回答：这刀改善主要来自更晚段的哪一块，是否已经算得上 `pure-test proven`。

## 为什么选这个

这轮直接遵循当前硬约束：
1. 不再重复 `ETH+SOL pair-conditioned halfsize` 那组旧 headline 数字；
2. 若继续 breakout 线，只能做两类新轴：`holdout / walk-forward honesty` 或更窄的 `context-conditioned sizing`；
3. 上一轮更窄的 context-conditioned sizing（`ETH-USD + SOL-USD @ validate/test × up` 半仓）已经落页，所以这轮最自然的小而完整动作，就是把它再按 holdout 眼光拆开，而不是再换标题重复写 full-sample headline。

## 本轮做了什么

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `summarize_policy_affected_hours_by_split()`；
   - 基于 `avoid_fluctuating_eth_sol_test_validate_up_halfsize_affected_hours_20bps.csv`，自动汇总这刀 policy 受影响小时在 `split_mix` 维度上的 before/after 条件累计、均值与改善幅度；
   - 新增 artifact：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_holdout_split_20bps.csv`
2. 更新 `support_breakout_v0_h24` 主报告
   - 在 context-conditioned sizing 段后新增一小节：
     - **如果把这刀更窄 sizing 放到更严格的 holdout 眼光下看，改善主要来自 validate，还是 pure test？**
   - 让读者能直接看到：当前改善主要来自 `test + validate` overlap，pure `test` 证据仍然很薄。
3. 更新 `alpha_closure_board`
   - breakout 卡片的 evidence / not_yet / next 已同步这条新读法：
     - 这刀 sizing 方向是对的；
     - 但还属于 `late-segment promising, not yet pure-test proven`；
     - 因此下一步仍应是更严格的 holdout / walk-forward / portfolio honesty，而不是直接升成默认 sizing 规则。
4. 更新 `docs/TODO.md`
   - 在当前 breakout top-3 relay baton 的第 3 条下补充这次 holdout split 结果；
   - `reports/site/plans/momentum_todo.html` 也已同步。

## 关键结果

来自 `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_holdout_split_20bps.csv`：

### 1) 当前改善主要来自 `test + validate` overlap，不是 pure `test`

这刀 policy 一共只影响了 `28` 个小时：
- `test + validate`: `25` 小时（约 `89.29%`）
- `test`: `3` 小时（约 `10.71%`）

### 2) `test + validate` overlap 的改善是实质性的

- 条件累计从约 `-3.79%` 收窄到约 `-1.87%`
- 改善约 `+1.92pp`
- 平均小时收益也从约 `-0.1477%` 收窄到约 `-0.0739%`

### 3) pure `test` 的方向也对，但证据非常薄

- 条件累计只从约 `-0.16%` 收窄到约 `-0.08%`
- 改善约 `+0.08pp`
- 但总共只有 `3` 个小时

## 当前更诚实的项目级读法

这轮之后，关于 breakout 线的更窄 sizing，可以更诚实地写成：
- 这刀 **不是没用**，因为在更晚段里确实有改善；
- 但它现在更像 `late-segment promising`，还不够算 `pure-test proven`；
- 所以下一步不该把它直接升成默认 sizing 规则，而应继续做更严格的 `holdout / walk-forward / portfolio honesty` 复核。

## 可见产物 / 验证

已执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_holdout_split_20bps.csv` 已生成；
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果把这刀更窄 sizing 放到更严格的 holdout 眼光下看...`
  - `1.92pp`
  - `0.08pp`
  - `not yet pure-test proven`
- `reports/site/factors/alpha_closure_board/report.html` 已同步这条新口径；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然包含多条在途改动，且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、以及相关站点文件在本轮前就已处于 dirty 状态；此时做 selective commit 无法保证只打包本轮改动。
