# breakout：ETH+SOL residual pair-conditioned halfsize 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把上一轮已经锁定的 residual weak pair/context，真正推进成一刀最小条件化 sizing 对照，而不是继续停在诊断层。

## 为什么选这个

这轮直接承接 `docs/TODO.md` 顶部 Top 3 的 breakout 第 3 条：

- 前面已经知道 `avoid_fluctuating` 是当前最像样的最小环境 gate；
- 也已经知道 gate 后残余弱点主要收窄到 `ETH+SOL` 这类 `2` 仓小时；
- 当前最值钱的一步，不是再重复证明“哪里弱”，而是验证：**如果只对这个 residual pair 做一刀克制的 sizing，会不会比 gate-only 更像样。**

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
   - 在 `support_breakout_v0_h24` 这条线里补出一版最小 sizing policy：
     - 对 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时，只做 `0.5x` 半仓；
     - 不动其它 pair，也不动单仓 / 三仓 / 四仓小时；
     - 保持同一套 `20bps hourly mark-to-market` 口径。
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新网页 / 入口
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 将 breakout Top 3 里的“最小条件化 sizing 切片”标记为完成；
   - 在详细收口段补入正式结果口径；
   - 同时把 breakout 下一棒明确收窄成：**把这刀 pair-conditioned halfsize 放进更严格 holdout / walk-forward honesty 里复核。**

## 核心结果

### 1) 这刀 sizing 很克制，只动了一个 residual pair

当前 policy 不是“所有 2 仓都砍半”，而只是：
- 在 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时上做 `0.5x` 半仓；
- 受影响约 `44/398` 个活跃小时，约占 `11.06%` active hours。

所以这是一刀非常具体、可解释的 pair-conditioned sizing，而不是粗暴去杠杆。

### 2) 同框架结果确实有净改善

来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：

- **raw_v0 / 20bps hourly path**
  - 累计约 `14.04%`
  - max drawdown 约 `-12.03%`
- **avoid_fluctuating / gate-only**
  - 累计约 `15.46%`
  - max drawdown 约 `-9.97%`
- **avoid_fluctuating + ETH/SOL pair halfsize**
  - 累计约 `19.90%`
  - max drawdown 约 `-9.04%`

也就是说，相比 gate-only：
- hourly path 累计再提升约 `+4.44pp`
- max drawdown 再收窄约 `0.93pp`

### 3) 被压的 residual pair pocket 本身也明显收窄

同一张 compare 表里：
- gate-only 的 `ETH+SOL` 两仓 pocket 条件累计约 `-7.17%`
- 半仓后约收窄到 `-3.61%`

说明这不是“overall 巧合变好、但目标口袋没变”，而是被针对的 residual pocket 自己也被压窄了。

### 4) 这刀 sizing 对准的 context 是清晰的，不是拍脑袋

来自 `support_breakout_v0_h24` 页里的 context 表：
- `validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

所以当前更诚实的项目级读法是：
- `avoid_fluctuating` 已经把 broad drag 压掉一部分；
- `ETH+SOL` 是剩下最值得动手的 residual pair；
- 而这刀 pair-conditioned halfsize 确实交出了 first-pass 正向结果。

## 对项目决策的含义

这轮之后，breakout 线的默认下一步更收紧了：

1. **不再优先回头做 confirm_1 排位**
   - 这件事在更正式口径下已经基本看清。
2. **不再优先继续泛化诊断 weak pair**
   - 现在已经有一个最小动作切片交出了净改善。
3. **若继续 breakout 线，更该做的是更严格 honesty**
   - 把这刀 `ETH+SOL pair-conditioned halfsize` 放进更严格的 holdout / walk-forward / portfolio honesty 里复核，确认这约 `+4.44pp` 的 path 改善到底是不是可迁移改进。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - `44/398`
  - `19.90%`
  - `-9.04%`
  - `-7.17% -> -3.61%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步出现：
  - `avoid_fluctuating + ETH/SOL pair-conditioned halfsize`
  - `+4.44pp`
  - `0.93pp`
- `reports/site/plans/momentum_todo.html` 已同步。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍非常脏，而且本轮涉及的 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应 site 页面，以及大量 `support_breakout_v0_h24` artifacts 都与此前未提交状态混在一起；此时做 selective commit 仍无法保证只打包本轮改动。
