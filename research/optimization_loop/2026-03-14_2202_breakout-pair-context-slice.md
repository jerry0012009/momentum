# breakout 2仓弱 pair 的 split/regime 口袋正式锁定

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 任务：把已经确认偏弱的 `2` 仓并发 pair，继续拆到 `pair × split/regime`，回答它们到底更像“后段问题”还是“特定环境问题”，并把结果同步到主报告、TODO 入口和 closure board。

## 为什么选这个

当前 Top 3 里，breakout 线最自然的下一棒就是第 2 条：
- 已知道 `2` 仓小时比 `4` 仓更像弱点；
- 已知道弱点集中在 `BTC+SOL`、`ETH+SOL`、`BNB+ETH` 这类 pair；
- 但还不知道这些拖累到底更偏 `test`、还是更偏某类 regime。

这轮把这件事补完后，下一棒就能从“继续诊断”切到“最小条件化 sizing 动作验证”。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `summarize_hourly_active_position_pair_context(...)`；
   - 在现有 `active_positions=2` 明细基础上，把 weak pair 进一步聚合到：
     - `symbol_pair`
     - `split_mix`
     - `regime_mix`
   - 生成新 artifact：
     - `reports/artifacts/support_breakout_v0_h24/hourly_active_position_2_pair_context_compare_20bps.csv`
2. 更新 `support_breakout_v0_h24` 页面
   - 新增一段：**再把这些弱 pair 拆到 split / regime，它们更像后段问题还是环境问题？**
   - 让页面直接回答：
     - 哪些 broad drag 并不主要长在 `test`
     - 哪些才更像真正的后段尾部
     - `avoid_fluctuating` 修掉了什么、还剩什么
3. 更新 `scripts/build_alpha_closure_board_report.py`
   - 同步 breakout 卡片 evidence / next step：
     - 不再停留在“要继续查 pair 在哪”
     - 而是明确进入“基于 residual pockets 做最小条件化 sizing”的动作阶段
4. 更新 `docs/TODO.md`
   - 将 Top 3 第 2 条正式标为完成 `[x]`
   - 补入同样的结果口径；
   - 同步 `reports/site/plans/momentum_todo.html`

## 核心结果

### 1) 最大 broad drag 并不主要长在 test

来自 `hourly_active_position_2_pair_context_compare_20bps.csv`：

- `BNB+ETH @ train × flat`
  - 约 `20` 小时
  - mean hourly return 约 `-0.25%`
- `BTC+SOL @ train × up`
  - 约 `20` 小时
  - mean hourly return 约 `-0.12%`
- `BTC+SOL @ train × flat`
  - 约 `13` 小时
  - mean hourly return 约 `-0.20%`

这说明 2 仓弱点并不只是“后段突然坏掉”，有一块本来就长在训练阶段的特定环境里。

### 2) 真正像后段尾部的，是更窄的 ETH+SOL test pocket

- `ETH+SOL @ test × down+flat`
  - 约 `2` 小时
  - mean hourly return 约 `-0.69%`
- `ETH+SOL @ test × up`
  - 约 `3` 小时
  - mean hourly return 约 `-0.05%`

也就是说，`test` 的问题不是“大面积 pair 都在后段崩”，而更像集中在更窄的 `ETH+SOL` 口袋上。

### 3) avoid_fluctuating 先压掉了 broad drag，但 residual weakness 还在

gate 后最值得盯的残余弱 context 变成：

- `ETH+SOL @ test+validate × up`
  - 约 `25` 小时
  - mean hourly return 约 `-0.15%`

同时：
- `BTC+SOL` 在 gate 后几乎被压到只剩 `3` 小时；
- 新出现的 `BNB+SOL @ train × flat` 约 `24` 小时，mean hourly return 约 `+0.11%`，说明 gate 更像是把坏 pair 结构换掉了一部分，而不是把所有 2 仓小时都修好。

## 本轮后的项目级读法

现在 breakout 线的结论更清楚了：
- `raw` 仍是主原型；
- `confirm_1` 没有在更正式口径下抢位；
- `avoid_fluctuating` 也只是部分修复；
- 当前真正该做的，已经不是继续问“pair 到底在哪”，而是基于这些 residual pockets（尤其 `ETH+SOL @ test+validate × up`）去做一版**最小条件化 sizing**切片。

## 可见产物验证

已验证：
- `reports/site/factors/support_breakout_v0_h24/report.html`
  - 出现：`再把这些弱 pair 拆到 split / regime...`
- `reports/site/factors/alpha_closure_board/report.html`
  - breakout 卡片已同步 residual pocket 口径
- `reports/site/plans/momentum_todo.html`
  - Top 3 第 2 条已同步为完成
- 新 artifact：
  - `reports/artifacts/support_breakout_v0_h24/hourly_active_position_2_pair_context_compare_20bps.csv`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然很脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、对应站点输出文件在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
