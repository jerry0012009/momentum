# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 任务：把上一轮已经锁定的 residual pocket（`ETH+SOL` 两仓小时）从“诊断”推进到“最小动作验证”，交一版真正可对照的条件化 sizing 切片。

## 为什么选这个

当前 `docs/TODO.md` 的 Top 3 里，breakout 第 3 条还停在待完成：
- 已知道 `avoid_fluctuating` 能改善 overall / up / drawdown；
- 已知道残余弱点主要收窄在 `ETH+SOL` 两仓小时，尤其 `validate × up` 与更窄的 `test` pockets；
- 但还没做出真正的 sizing 动作验证。

所以这轮不再补 wording，而是直接回答：**如果只对这一个 residual pair 做最小半仓，会不会比 gate-only 更像样？**

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `apply_hourly_pair_sizing_policy(...)`
   - 新增 `summarize_hourly_pair_sizing_compare(...)`
   - 在现有 `avoid_fluctuating` hourly path 基础上，补出一版极小动作：
     - 只对 `ETH-USD + SOL-USD` 的 `2` 仓小时做 `0.5x` 半仓；
     - 不碰其他 pair；
     - 不改 trade 定义、不改持有期、不额外新增 gate。
2. 新增 durable artifacts
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
   - `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`
3. 更新站点可见产物
   - `reports/site/factors/support_breakout_v0_h24/report.html`
     - 新增一段：**如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
   - `reports/site/factors/alpha_closure_board/report.html`
     - breakout 卡片从“该做最小 sizing”更新成“最小 sizing 已交付 first-pass 结果”；
   - `reports/site/plans/momentum_todo.html`
4. 更新 `docs/TODO.md`
   - 将 Top 3 里的 breakout 第 3 条标记为完成 `[x]`；
   - 同步补入结果口径；
   - 并把下一棒收窄成更严格的 holdout / walk-forward 复核，以及更克制的 context-conditioned sizing 对照。

## 核心结果

### 1) 这刀很克制：只动了 `44/398` 个活跃小时

当前 rule 不是“把所有 2 仓都砍掉”，而是：
- 在 `avoid_fluctuating` 已经落地的前提下；
- 只对仍出现的 `ETH-USD + SOL-USD` 两仓小时做 `0.5x` 半仓；
- 共影响约 `44/398` 个活跃小时（约 `11.06%`）。

这意味着它是个相当克制的 first-pass sizing slice，而不是全局大改。

### 2) overall hourly path 明显改善

来自 `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`：

- `raw_v0`
  - hourly path 累计约 `14.04%`
  - max drawdown 约 `-12.03%`
- `avoid_fluctuating`
  - hourly path 累计约 `15.46%`
  - max drawdown 约 `-9.97%`
- `avoid_fluctuating_eth_sol_pair_halfsize`
  - hourly path 累计约 `19.90%`
  - max drawdown 约 `-9.04%`

对比 gate-only：
- 累计再提升约 `+4.44pp`
- max drawdown 再收窄约 `0.93pp`

因此，这不是“只改了一点点、结果几乎没差”的那类动作；它在同框架下给出了可见增益。

### 3) 被压的 residual pair pocket 本身也明显收窄

同一份对照里：
- gate-only 下，`ETH+SOL` 这块被打中的 residual pair pocket 条件累计约 `-7.17%`
- 做成 `0.5x` 半仓后，约收窄到 `-3.61%`

也就是说，这刀并不是只在 overall 上“碰巧变好”，它确实先把当前最明确的 weak pocket 压窄了。

### 4) 当前 breakout 线的项目级读法进一步收紧

这轮之后，breakout 线最诚实的读法变成：
- `raw` 仍是主原型；
- `confirm_1` 没有在更正式口径下抢位；
- `avoid_fluctuating` 是有帮助的最小 gate；
- 而且在此基础上，**pair-conditioned sizing 已经开始显示增益**；
- 因此下一步最值得做的，不再是继续换 breakout 分支，而是把这类 sizing 改进放进更严格的 holdout / walk-forward / portfolio honesty 里复核。

## 验证

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - `44/398`
  - `11.06%`
  - `15.46% -> 19.90%`
  - `-9.97% -> -9.04%`
  - `-7.17% -> -3.61%`
- `reports/site/factors/alpha_closure_board/report.html` 已同步 breakout 新口径；
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步更新；
- 新 artifacts 已落盘：
  - `avoid_fluctuating_eth_sol_pair_halfsize_*`
  - `raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、以及对应 site / artifact 输出路径，在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
