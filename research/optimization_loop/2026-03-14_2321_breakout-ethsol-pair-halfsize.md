# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把已经锁定的 `ETH+SOL` residual weak pocket，真正推进成一刀**最小条件化 sizing**结果页，而不再停留在“诊断已经很清楚”的状态。

## 为什么选这个

当前 `docs/TODO.md` 的 breakout Top 3 已经明确收窄到这一步：
1. `avoid_fluctuating` 已经证明自己有帮助，但不万能；
2. `2` 仓弱小时已经被拆到 `pair × split/regime`，残余弱点集中在 `ETH+SOL` 一带；
3. 该从“继续诊断”进入“最小动作验证”了。

所以这轮不再补 wording，也不再继续查 weak pocket 在哪，而是直接问：**如果只对 gate 后仍出现的 `ETH+SOL` 两仓小时做一刀很克制的半仓，会不会带来净改善？**

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
   - 在现有 `avoid_fluctuating` 的 `20bps hourly portfolio path` 基础上，新增一个最小 policy：
     - 当活跃小时属于 `ETH-USD + SOL-USD` 两仓组合时，组合回报只记 `0.5x`
   - 生成新 artifacts：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
2. 更新 `support_breakout_v0_h24` 主报告
   - 新增一节：
     - **如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - breakout 卡片 evidence / next 同步到最新动作层结果；
   - 让总决策页不再停在“下一步去做条件化 sizing”，而是明确写成“这刀已经做完，下一步该做更严格 holdout / walk-forward 复核”。
4. 更新 `docs/TODO.md`
   - 把原先那条 pending 的“最小条件化 sizing 切片”视为完成；
   - 并把 breakout 当前 Top 3 刷新成新的下一棒：
     - `ETH+SOL pair-conditioned halfsize` 的更严格 holdout / walk-forward 复核
     - 以及更克制的 context-conditioned sizing 对照
5. 重建可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果

### 1) 这刀很克制：只动了 44/398 个活跃小时

当前 policy 不是“把所有 2 仓都砍掉”，也不是全局再降杠杆，而只是：
- 在 `avoid_fluctuating` 已落地后；
- 对仍出现的 `ETH-USD + SOL-USD` 两仓小时；
- 把当小时组合回报缩到 `0.5x`。

受影响约：
- `44 / 398` 个活跃小时
- 约占 `11.06%` active hours

这符合“最小动作验证”的要求：动作足够窄，不是大开大合地重写整个策略。

### 2) 同框架结果是正向的：overall path 与回撤都继续改善

来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：

- `raw_v0` hourly path（20bps）
  - 累计约 `14.04%`
  - max drawdown 约 `-12.03%`
- `avoid_fluctuating` gate-only
  - 累计约 `15.46%`
  - max drawdown 约 `-9.97%`
- `avoid_fluctuating_eth_sol_pair_halfsize`
  - 累计约 `19.90%`
  - max drawdown 约 `-9.04%`

也就是说，相比 gate-only：
- hourly path 约再提升 `+4.44pp`
- max drawdown 约再收窄 `0.93pp`

这说明当前这刀 pair-conditioned sizing **不是只是把坏 pocket 砍掉而顺便把 overall 做钝**；至少在当前样本里，它给出了“收益更高、回撤更小”的同向改进。

### 3) 被压的 residual pair pocket 本身也明显收窄

同一张 compare 表显示：
- `avoid_fluctuating` 下，这个 `ETH+SOL` residual pair pocket 的条件累计约 `-7.17%`
- 做成 `0.5x` 半仓后，约收窄到 `-3.61%`

而这些被压的小时主要集中在：
- `validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

所以这刀动作并不是拍脑袋乱砍，而是确实打在前面已经定位过的 residual weak pair 上。

## 本轮后的项目级读法

这轮之后，breakout 线的读法可以再往前推进半步：
- `raw` 仍是 breakout-short 主原型；
- `confirm_1` 继续不值得抢位；
- `avoid_fluctuating` 是有帮助的最小 gate；
- 而在 gate 已落地的前提下，**pair-conditioned sizing 也开始交出 first-pass 正结果**。

因此 breakout 线接下来最值得继续的问题，已经不再是：
- “还要不要继续找 weak pocket？”
- “要不要再换 breakout 分支？”

而更像是：
1. 这刀 `ETH+SOL pair-conditioned halfsize` 是否能在更严格 holdout / walk-forward 下站住；
2. 是否存在一版更克制的 `context-conditioned sizing`，能保住大部分改进、同时比“整个 ETH+SOL 两仓都半仓”动作更小。

## 验证

### 页面验证

已验证：
- `reports/site/factors/support_breakout_v0_h24/report.html`
  - 出现新段：`如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - 已出现关键数：`44/398`、`11.06%`、`15.46% -> 19.90%`、`-9.97% -> -9.04%`
- `reports/site/factors/alpha_closure_board/report.html`
  - breakout 卡片已同步成“条件化 sizing 已落地，下一步做 holdout/walk-forward 复核”
- `reports/site/plans/momentum_todo.html`
  - 已同步新的 breakout Top 3 接力棒

### Artifact 验证

已生成：
- `avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
- `avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
- `avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
- `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、以及对应站点输出文件在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
