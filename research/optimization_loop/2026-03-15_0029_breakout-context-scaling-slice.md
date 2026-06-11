# breakout 更窄 context-conditioned sizing 切片（ETH+SOL @ validate/test × up）

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：在已经交付的 `ETH+SOL pair-conditioned halfsize` 之外，再把动作收窄一层，直接验证：**如果只对 `ETH-USD + SOL-USD @ validate/test × up` 这块 residual context 做 `0.5x` 半仓，而不是对整块 `ETH+SOL` 两仓都动手，会不会仍有净改善？**

## 为什么选这个

这一刀是当前最自然、也最符合新约束的下一步：
1. `pair-conditioned halfsize` 那刀 first-pass 已经交付，不能再重复换标题讲同一组 headline 数字；
2. breakout 线若继续，只允许走两类新轴：
   - 更严格 holdout / walk-forward / portfolio honesty；
   - 或更窄的 context-conditioned sizing；
3. 当前已有 pair/context 诊断清楚指向：残余弱点并不是均匀噪声，而是更集中在 `ETH+SOL @ test+validate × up` 这类 residual pocket。

所以本轮直接交这条更窄的新轴，而不是重复 general pair halfsize。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 扩展 `apply_hourly_pair_sizing_policy(...)`，允许对指定 `pair × split_mix × regime_mix` 的更窄上下文做 sizing；
   - 新增一版更窄的策略切片：
     - 只在 `avoid_fluctuating` 后仍出现的
       - `symbol_pair = ETH-USD + SOL-USD`
       - `split_mix ∈ {test, test + validate, validate}`
       - `regime_mix = up`
       的 `active_positions = 2` 小时上做 `0.5x` 半仓；
   - 生成新 artifacts：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_path_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_summary_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_test_validate_up_halfsize_affected_hours_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_test_validate_up_halfsize_compare_20bps.csv`
2. 更新 `support_breakout_v0_h24` 主报告
   - 新增一段：
     - **如果把动作收得更窄：只对 ETH+SOL 的 `test+validate × up` 残余口袋做半仓，会发生什么？**
   - 让页面直接回答：
     - 这刀更窄动作影响了多少小时；
     - 对 hourly path 的净改善有多大；
     - 它与 gate-only 相比到底有没有意义。
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - 将 breakout 卡片 evidence / next step 同步成最新状态：
     - breakout 线现在不只是“知道 residual pocket 在哪”；
     - 还已经交出一刀更窄的 context-conditioned sizing first-pass 结果；
     - 因此下一步该问的是 holdout / walk-forward 可迁移性，而不是继续泛化地诊断 weak pair。
4. 更新 `docs/TODO.md`
   - 将 `Current relay baton` 的第 3 条正式标记为完成 `[x]`；
   - 补入这次更窄 context-conditioned sizing 的正式读法；
   - 同步 `reports/site/plans/momentum_todo.html`。

## 核心结果

### 1) 这刀更窄的动作仍然有净改善

来自 `raw_gate_eth_sol_test_validate_up_halfsize_compare_20bps.csv`：

- **gate-only / 20bps hourly path**
  - cumulative net return：约 `15.46%`
  - max drawdown：约 `-9.97%`
- **只对 ETH+SOL @ validate/test × up 做 0.5x 半仓**
  - cumulative net return：约 `17.86%`
  - max drawdown：约 `-9.97%`

也就是说：
- 这刀更窄的动作没有像 general pair halfsize 那样继续压低 drawdown；
- 但它仍把同框架 hourly path 额外抬高了约 `+2.40pp`；
- 说明 residual context 不是“看起来弱、但动了也没用”的假口袋，而是一个仍有真实改善空间的局部弱点。

### 2) 动作范围确实明显更小

受影响的是：
- `ETH-USD + SOL-USD`
- 且只在 `validate/test × up`
- 且只在 `active_positions = 2` 的小时

当前影响约：
- `28 / 398` 个活跃小时
- 约占 `7.04%`

这比“整块 ETH+SOL 两仓都半仓”更克制，也更符合现在对 breakout 线的推进方式：**先收窄到最像样的 residual pocket，再看它是否值得升成默认 sizing 候选。**

### 3) 被压的 residual context 本身也确实被磨钝了

来自同一份 compare artifact：
- 这块 residual context 的 conditional cumulative return：
  - gate-only：约 `-3.94%`
  - context-conditioned halfsize：约 `-1.95%`

这说明这刀更窄动作不是只在 overall path 上“看起来改善”，它对目标弱口袋本身也真的起到了缓冲作用。

## 本轮后的项目级读法

breakout 线现在更清楚地进入了下一阶段：
- `raw` 仍是主原型；
- `confirm_1` 没在更正式口径下反超 raw；
- `avoid_fluctuating` 证明了 broad gate 有价值；
- 在此基础上，更窄的 `ETH+SOL @ validate/test × up` context-conditioned sizing 也交出了 first-pass 改善；
- 所以下一步最值得做的，已经不是继续找 weak pocket，而是把这类更窄 sizing 放进更严格的 **holdout / walk-forward / portfolio honesty** 里复核，判断它到底是可迁移改进，还是当前样本的局部 lucky patch。

## 可见产物验证

已验证：
- `reports/site/factors/support_breakout_v0_h24/report.html`
  - 出现：`如果把动作收得更窄：只对 ETH+SOL 的 test+validate × up 残余口袋做半仓，会发生什么？`
  - 页面已显示：`28/398`、`17.86%`、`-1.95%`
- `reports/site/factors/alpha_closure_board/report.html`
  - breakout 卡片已同步成更窄的 context-conditioned sizing 口径
- `reports/site/plans/momentum_todo.html`
  - Top 3 第 3 条已同步为完成
- 新 artifacts 已落盘：
  - `avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_path_20bps.csv`
  - `avoid_fluctuating_eth_sol_test_validate_up_halfsize_hourly_summary_20bps.csv`
  - `avoid_fluctuating_eth_sol_test_validate_up_halfsize_affected_hours_20bps.csv`
  - `raw_gate_eth_sol_test_validate_up_halfsize_compare_20bps.csv`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应站点输出文件在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
