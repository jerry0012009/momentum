# breakout pure-test context-conditioned honesty

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把更窄的 `ETH+SOL @ validate/test × up` context-conditioned sizing 再推进到真正的 `pure-test honesty`，直接回答这条分支到底能不能继续和默认 `pair-conditioned sizing` 并列，还是应该先 park。

## 为什么选这个

这轮严格遵循当前硬约束：
1. 不能再重复写 `ETH+SOL pair-conditioned halfsize` 那组 headline 数字；
2. 若继续 breakout 线，只能做：
   - 更严格 holdout / walk-forward / portfolio honesty；或
   - 更窄的 context-conditioned sizing。

当前 `docs/TODO.md` 的第 2 条刚好就是：把更窄的 `ETH+SOL @ validate/test × up` context-conditioned sizing 推到更严格的 `walk-forward / pure-test honesty`。因此本轮选这个点，属于顺着已定义 next step 交真实结果，而不是继续补 wording。

## 本轮做了什么

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 在已有两档 sizing 候选基础上，再补一档更严格的 candidate：
     - `avoid_fluctuating_eth_sol_test_up_halfsize`
   - 规则非常克制：
     - 先保留 `avoid_fluctuating` gate；
     - 再只对 `ETH-USD + SOL-USD`
     - 且仅 `split = test`
     - 且仅 `regime = up`
     - 的 `active_positions = 2` 小时做 `0.5x` 半仓。
   - 新增 artifacts：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_up_halfsize_hourly_path_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_up_halfsize_hourly_summary_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_up_halfsize_affected_hours_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_test_up_halfsize_compare_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_up_halfsize_holdout_split_20bps.csv`
   - 同时把它加入 `avoid_fluctuating_sizing_candidate_compare_20bps.csv`，与：
     - `pair-conditioned halfsize`
     - `test+validate × up context halfsize`
     - 一起并排比较。
2. 更新 `support_breakout_v0_h24` 页面
   - 新增一段：**如果把它继续收窄到“只动 pure test × up”呢？**
   - 直接回答：
     - 这刀影响面有多小；
     - overall 改善有多薄；
     - 这是否足够支持它继续占一个主资源位。
3. 更新 `alpha_closure_board`
   - breakout 卡片现已同步最新结论：
     - `pair-conditioned sizing` 仍是默认候选；
     - 更窄 context halfsize 在 pure-test 眼光下证据太薄，更像应先 park 的诊断型分支。
4. 更新 `docs/TODO.md`
   - 将：
     - `breakout：把更窄的 ETH+SOL @ validate/test × up context-conditioned sizing 推到更严格的 walk-forward / pure-test honesty`
     标记为完成；
   - 并把当前正式结论写回 TODO 与 plans 镜像。

## 关键结果

### 1) pure-test-only 版本的影响面非常薄

来自 `raw_gate_eth_sol_test_up_halfsize_compare_20bps.csv`：
- `avoid_fluctuating` gate-only：
  - active hours：`398`
  - cumulative net return：约 `15.46%`
  - max drawdown：约 `-9.97%`
- `avoid_fluctuating_eth_sol_test_up_halfsize`：
  - 只影响约 `3/398` 个活跃小时（约 `0.75%`）
  - cumulative net return：约 `15.56%`
  - max drawdown：仍约 `-9.97%`

也就是说，继续收窄到真正的 pure `test × up` 后，overall 只多了约 `+0.09pp`，回撤几乎没动。

### 2) pure-test pocket 本身改善方向对，但量级极小

来自 `avoid_fluctuating_eth_sol_test_up_halfsize_holdout_split_20bps.csv`：
- `test` 小时数：`3`
- conditional cumulative before：约 `-0.16%`
- conditional cumulative after：约 `-0.08%`
- delta：约 `+0.08pp`

这说明：
- 更窄的 context-conditioned sizing 不是完全无效；
- 但它现在更像“把一个已经很小的 residual pocket 再磨平一点”；
- 还远远不够支撑“继续跟默认候选并列消耗主资源”。

### 3) breakout 线当前资源顺序进一步收敛

这轮之后，breakout 线的更诚实排序是：
1. `raw` 仍是 breakout-short 主原型；
2. `avoid_fluctuating + ETH+SOL pair-conditioned halfsize` 仍是默认 sizing candidate；
3. 更窄的 `validate/test × up` 乃至 `pure test × up` context halfsize，现阶段更适合 park 成诊断型分支。

换句话说：
- 这轮不是证明 context branch 没用；
- 而是证明它在更严格 pure-test 眼光下**还不够厚**，不足以继续抢主资源位。

## 验证

已执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `只动 pure test × up`
  - `3/398`
  - `15.46% -> 15.56%`
  - `park 成诊断型分支`
- `reports/site/factors/alpha_closure_board/report.html` 已同步 breakout 卡片的新结论；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步将该任务标记为完成。

## 当前结论

本轮最重要的不是多赚了多少，而是把一个“看上去 promising 的更窄分支”推进到了更严格的 honest check，并确认：
- 它目前还不值得与默认候选并列；
- breakout 线的主资源应该回到 `pair-conditioned halfsize` 的更严格 holdout / walk-forward / portfolio honesty。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然包含多条在途改动；`docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py` 及多份已生成页面/产物在本轮前就已处于 dirty 状态。此时做 selective commit 无法保证只打包本轮改动。
