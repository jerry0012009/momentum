# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把上一轮已经锁定的 residual weak pocket 真正推进到“最小动作验证”——不再继续只做诊断，而是在 `avoid_fluctuating` 已落地前提下，交一版克制的 `pair-conditioned sizing` 对照切片，看能否在不盲目砍并发的前提下改善 breakout 的组合路径。

## 为什么选这个

当前 `docs/TODO.md` 的 breakout baton 已明确收窄到这里：
1. `confirm_1` 是否抢位，已经基本看清；
2. `avoid_fluctuating` 也已经证明自己只是部分修复；
3. pair/context 诊断已经把残余问题锁到 `ETH+SOL` 一带。

所以这轮最值得做的，不是再补 wording，也不是继续泛化找 weak pocket，而是直接交一个最小、可复核、能落页的 sizing 切片。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
   - 在 `avoid_fluctuating` 的 `20bps hourly path` 上，新增一刀最小 policy：
     - 若当前小时属于 `ETH-USD + SOL-USD` 的两仓并发口袋，则该小时组合收益只记 `0.5x`
   - 这不是全局砍所有 `2` 仓，也不是停掉整条 pair，只是对已经被诊断出来的 residual weak pair 做克制的半仓。
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新网页 / 总入口
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 将这条 breakout 最小条件化 sizing 任务标记为完成；
   - 同时把下一棒明确收窄到：`pair-conditioned halfsize` 是否能通过更严格的 holdout / walk-forward 复核。

## 核心结果（20bps，同框架）

### 1) 这刀 policy 很克制：只动了 44/398 个活跃小时

来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：
- 受影响活跃小时：`44/398`
- 影响占比：约 `11.06%`

这说明它不是“全局收杠杆”，而是真正基于 residual pair 做的定点半仓。

### 2) overall hourly path 有实质改善

对比 `avoid_fluctuating` gate-only：
- gate-only hourly path：约 `15.46%`
- `ETH+SOL pair halfsize` 后：约 `19.90%`
- 增量：约 `+4.44pp`

同时：
- gate-only max drawdown：约 `-9.97%`
- halfsize 后：约 `-9.04%`
- 改善：约 `+0.93pp`

也就是说，这刀不是靠牺牲路径换一点漂亮单点，而是整体路径和回撤都向更好方向移动。

### 3) 被压的 residual pocket 本身也明显收窄

同一张对照表里：
- `avoid_fluctuating` 下 `ETH+SOL` pocket 的条件累计：约 `-7.17%`
- 做成 `0.5x` 半仓后：约 `-3.61%`

并且这个 residual pair 主要还是长在已经诊断出的 4 块：
- `validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

说明这不是随机改善，而是正好打在之前已经识别出的弱口袋上。

## 这轮后的项目级读法

这轮之后，breakout 线的当前口径可以再收紧一层：
- `raw` 仍是主原型；
- `confirm_1` 不再值得继续抢位；
- `avoid_fluctuating` 是有帮助的最小 gate；
- 而且在 gate 之上，`ETH+SOL` residual pair 的最小半仓切片已经证明：**有针对性的 sizing honesty，确实比继续换 breakout 分支更值钱。**

因此下一步如果继续 breakout，更该问的是：
- 这刀 `pair-conditioned halfsize` 在更严格 holdout / walk-forward 下能不能站住；
- 而不是继续做新的 breakout 变体排序。

## 验证

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - `44/398`
  - `15.46% -> 19.90%`
  - `-9.97% -> -9.04%`
  - `-7.17% -> -3.61%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步 breakout 卡片 evidence / next；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步新的 breakout baton。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应 site 输出与 artifact 路径在本轮前就已存在在途改动；此时做 selective commit 仍无法稳定保证只打包本轮变更。
