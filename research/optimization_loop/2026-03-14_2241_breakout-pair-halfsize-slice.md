# breakout：ETH+SOL residual pair halfsize 切片正式落页

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把上一轮已经诊断出来的 residual weak pocket 真正推进到一刀最小动作验证——**在 `avoid_fluctuating` 已落地前提下，只对 gate 后仍出现的 `ETH-USD + SOL-USD` 两仓小时做 `0.5x` 半仓，看能不能在不盲目砍并发的前提下带来净改善。**

## 为什么选这个

这轮没有再去补 wording，而是沿着 breakout 线当前最明确的 next step 直接交结果：
1. `2` 仓弱小时已经拆到 `pair × split/regime`，知道 residual weakness 主要集中在 `ETH+SOL`；
2. `avoid_fluctuating` gate 已经证明自己有帮助，但还没修好 `test/down` 尾部；
3. 当前最自然的一刀，不是再回头诊断，而是做一个**克制的 pair-conditioned sizing**，看它是否真能带来净改善。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`：
     - 可在已生成的 hourly portfolio path 上，对指定 `symbol_pair` 的小时应用 size multiplier；
   - 新增 `summarize_hourly_pair_sizing_compare(...)`：
     - 用同一套口径并排比较 `raw_v0 / avoid_fluctuating / avoid_fluctuating_eth_sol_pair_halfsize`；
   - 在 `support_breakout_v0_h24` 主报告新增一段：
     - **如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新决策入口
   - `docs/TODO.md`
   - `reports/site/plans/momentum_todo.html`
   - `reports/site/factors/alpha_closure_board/report.html`

## 关键结果

### 1) 这刀 sizing 确实带来净改善，而且动作很克制

当前规则不是“把所有 2 仓都砍掉”，而只是：
- 在 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时上做 `0.5x` 半仓；
- 受影响约 `44/398` 个活跃小时（约 `11.06%`）。

同框架结果来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：
- `raw_v0` hourly path：约 `14.04%`，max drawdown 约 `-12.03%`
- `avoid_fluctuating`：约 `15.46%`，max drawdown 约 `-9.97%`
- `avoid_fluctuating_eth_sol_pair_halfsize`：约 `19.90%`，max drawdown 约 `-9.04%`

也就是说，相对 gate-only：
- 累计再提升约 `+4.44pp`
- 最大回撤再收窄约 `0.93pp`

### 2) 被压的 residual pair pocket 也明显收窄了

同样来自 compare artifact：
- `avoid_fluctuating` 下，该 residual pair pocket 的条件累计约 `-7.17%`
- 做成 `0.5x` 后约收窄到 `-3.61%`

这说明当前动作不是“靠别处补偿把 overall 抬起来”，而是它真正打到了当前最明确的弱 pocket。

### 3) 这条线的下一步由“诊断”正式进入“更严格复核”

这轮之后，breakout 线更诚实的项目级读法已经变成：
- `raw` 仍是主原型；
- `confirm_1` 不再值得继续抢位；
- `avoid_fluctuating` 是有帮助的最小环境 gate；
- 而在此基础上，`ETH+SOL pair-conditioned halfsize` 已经交出 first-pass 改善。

因此下一步最值得做的，不是继续找 weak pocket，而是把这刀 sizing 放进更严格的：
- `holdout / walk-forward honesty`
- 或更正式的 `portfolio-level sizing` 里复核，确认这约 `+4.44pp` / `0.93pp` 的改善是不是可迁移，而不是当前样本 lucky patch。

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
  - `-3.61%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步这条 breakout 线的最新总览口径；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步成“当前下一棒是更严格 holdout / walk-forward 复核”。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/factors/alpha_closure_board/report.html`、`reports/site/plans/momentum_todo.html` 等路径在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
