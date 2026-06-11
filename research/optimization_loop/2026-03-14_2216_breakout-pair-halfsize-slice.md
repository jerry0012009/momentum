# breakout：最小条件化 sizing 切片（ETH+SOL residual pair 半仓）

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 任务：把 Top 3 第 3 条（最小条件化 sizing 对照切片）从“待做”推进到真实结果，并同步主报告 / closure board / plans。

## 为什么这次选这个

上一轮已经把 breakout 的弱口袋收窄到很具体：
- gate 后 residual weakness 主要集中在 `ETH+SOL` 两仓上下文；
- 其中覆盖最大的残余是 `test+validate × up`。

所以这轮不再继续写诊断文案，而是按 TODO 的要求直接交“动作切片”：
- 在不盲目砍并发的前提下，只对这一类 residual pair 小范围降风险，看看同框架下是否有净改善。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
     - 对指定 `symbol_pair` 的活跃小时应用 size multiplier（本轮用 `0.5x`）；
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
     - 把 `raw_v0 / avoid_fluctuating / avoid_fluctuating_eth_sol_pair_halfsize` 放进同一张 hourly path 对照表；
   - 在 `support_breakout_v0_h24` 主报告新增可见段：
     - **如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新入口页
   - `scripts/build_alpha_closure_board_report.py`：同步 breakout 卡片 evidence/next，把“最小条件化 sizing 已交付 + 下一步转严格 holdout/walk-forward 复核”写回总决策页；
   - `docs/TODO.md`：Top 3 第 3 条改为 `[x]`，并补入具体数字结论；
   - 重建：
     - `reports/site/factors/support_breakout_v0_h24/report.html`
     - `reports/site/factors/alpha_closure_board/report.html`
     - `reports/site/plans/momentum_todo.html`

## 核心结果（20bps，同框架）

本轮策略动作很克制：
- 仅在 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时做 `0.5x` 半仓；
- 受影响约 `44/398` 个活跃小时（约 `11.06%`）。

对照结果：
- `raw_v0` hourly path：累计约 `14.04%`，max drawdown 约 `-12.03%`
- `avoid_fluctuating`（gate-only）：累计约 `15.46%`，max drawdown 约 `-9.97%`
- `avoid_fluctuating_eth_sol_pair_halfsize`：累计约 `19.90%`，max drawdown 约 `-9.04%`

并且被处理的 residual pair pocket 本身：
- 条件累计从约 `-7.17%` 收窄到约 `-3.61%`

当前项目级读法：
- 这条 breakout 线确实已经从“继续找弱口袋”进入“最小动作验证”阶段；
- 下一步更该问这刀改进在更严格 holdout / walk-forward 下是否还能成立，而不是回头继续做变体排序。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

命中：
- `support_breakout_v0_h24/report.html` 已出现新节与关键数值：`11.06% / 15.46% -> 19.90% / -9.97% -> -9.04%`；
- `alpha_closure_board/report.html` breakout 卡片已同步 `+4.44pp` 提升与 `0.93pp` 回撤收窄的口径；
- `docs/TODO.md` 与 `plans/momentum_todo.html` 已把 Top 3 第 3 条标记完成并同步结论。

## Commit

本轮**未提交**。

原因：当前 repo worktree 持续高脏，且本轮涉及路径（`docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应 site 输出）在本轮前已处于 dirty 状态；此时 selective commit 仍无法保证只打包本轮改动。
