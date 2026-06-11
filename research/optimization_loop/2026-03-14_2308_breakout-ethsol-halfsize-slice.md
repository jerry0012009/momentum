# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把 Top 3 第 3 条真正落成结果——在 `avoid_fluctuating` 已经落地的前提下，不再继续诊断 weak pair，而是直接交一版**克制的最小条件化 sizing** 切片，看能不能在不盲目砍并发的前提下改善 breakout 的组合级路径。

## 为什么选这个

当前 breakout 线最自然的下一棒已经很明确：
1. `confirm_1` 是否抢位已经基本看清；
2. `avoid_fluctuating` 虽有帮助，但 `test/down` 弱口袋还在；
3. `2` 仓弱小时也已拆到 `pair × split/regime`，残余弱点已收窄成 `ETH+SOL` 一带。

所以这轮不该再补 wording，而该从“诊断”真正跨到“动作验证”：**如果只动一个最像问题来源的 residual pair，结果会不会更诚实地改善？**

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`；
   - 新增 `summarize_hourly_pair_sizing_compare(...)`；
   - 在现有 `avoid_fluctuating` 的 `20bps hourly mark-to-market` 路径上，新增一个最小策略化切片：
     - 仅当 `active_positions = 2`
     - 且 pair 为 `ETH-USD + SOL-USD`
     - 时，将该小时组合暴露降到 `0.5x` 半仓；
   - 生成新 artifacts：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
2. 更新 `support_breakout_v0_h24` 页面
   - 新增一节：**如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
   - 让页面直接回答：
     - 受影响小时占比有多大；
     - overall hourly path 是否更好；
     - 被压的 residual pair pocket 本身是否明显收窄；
     - 这意味着下一步更像该继续做 sizing honesty，而不是继续换 breakout 分支。
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - breakout 卡片 evidence / next 已同步到最新动作层结论：
     - 现在不只是“知道 residual weakness 在哪”；
     - 而是已经交出一版 first-pass pair-conditioned sizing；
     - 下一步应把它放进更严格的 holdout / walk-forward / portfolio honesty 去复核，而不是继续找 weak pocket。
4. 更新 `docs/TODO.md`
   - Top 3 第 3 条正式标为完成 `[x]`；
   - 同时把 breakout 的下一棒改写成更窄的新问题：
     - 先验证这刀 `ETH+SOL pair-conditioned halfsize` 是否只是 lucky patch；
     - 再决定要不要继续做更克制的 `context-conditioned` sizing。
5. 重建可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) 这刀动作很克制：只影响约 11% 的活跃小时

来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：
- 受影响小时：`44 / 398`
- affected hour share：约 `11.06%`

也就是说，这不是“把所有 2 仓都砍掉”，而只是对 gate 后仍残余的 `ETH+SOL` 两仓小时做半仓处理。

### 2) overall hourly path 确实继续改善了

同样在 `20bps` 同框架下：
- `raw_v0` hourly path：约 `14.04%`，max drawdown 约 `-12.03%`
- `avoid_fluctuating`：约 `15.46%`，max drawdown 约 `-9.97%`
- `avoid_fluctuating_eth_sol_pair_halfsize`：约 `19.90%`，max drawdown 约 `-9.04%`

相对 gate-only：
- 累计路径再提升约 `+4.44pp`
- 最大回撤再收窄约 `0.93pp`

这说明最小条件化 sizing 不是纯表述层优化，而是已经能在同框架下交出明显的 first-pass 改善。

### 3) 被针对的 residual pair pocket 本身也明显收窄了

这批 `ETH+SOL` 两仓小时原本的条件累计约：
- `-7.17%`

做成 `0.5x` 半仓后约收窄到：
- `-3.61%`

其主要 context 仍是页面已经锁定的四块：
- `validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

所以这轮至少证明：**当前 residual weakness 不是“动不了”的黑箱，而是可以通过很克制的 pair-conditioned sizing 被部分压窄。**

## 本轮后的项目级读法

这轮之后，breakout 线的顺序进一步清楚了：
- `raw` 仍是主原型；
- `confirm_1` 不值得继续抢主线位；
- `avoid_fluctuating` 是有效但不万能的最小环境 gate；
- 而真正值得继续往前补的，已经不是“继续查 weak pair 在哪”，而是：
  1. 这刀 `ETH+SOL pair-conditioned halfsize` 在更严格 holdout / walk-forward 下是否仍成立；
  2. 是否还有更克制的 `context-conditioned` 动作，能保住大部分改进、同时减少不必要的动作范围。

## 验证

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - `11.06%`
  - `19.90%`
  - `-9.04%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步：
  - breakout 卡片不再停留在 residual pair 诊断，而是已进入 pair-conditioned sizing 的动作层读法；
- `reports/site/plans/momentum_todo.html` 已同步新的 breakout 下一棒；
- 新 artifacts 已落盘：
  - `avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
  - `avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
  - `avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
  - `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应站点输出文件在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
