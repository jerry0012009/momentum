# breakout：ETH+SOL residual pair 的最小条件化 sizing 切片

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把上一轮已经锁定的 residual weak pocket（`avoid_fluctuating` 后仍残留的 `ETH-USD + SOL-USD` 两仓小时）从“诊断”推进到一刀真正的动作验证：**不盲目砍所有并发，只对这一个 residual pair 做最小 half-size，对照 `raw / gate-only` 看净改善是否成立。**

## 为什么选这个

当前 `docs/TODO.md` 的 Top 3 里，这条就是明确挂着的下一棒：
- 不是再做 breakout 分支排序；
- 不是再补 wording；
- 而是基于已经识别出的弱 pair/context，交一版最小条件化 sizing 切片。

这轮选它的原因也很直接：
1. 上一轮已经把 residual pockets 缩到了 `ETH+SOL` 这一带；
2. 现在最值钱的不是继续解释“它弱在哪”，而是回答“动它一下有没有净改善”；
3. 这件事可以直接落到页面、artifact、closure board 和 plans 入口，不会只停留在日志里。

## 做了什么改动

### 1) 更新 `scripts/build_support_breakout_v0_reports.py`

新增两类 helper：
- `apply_hourly_pair_sizing_policy(...)`
  - 对已经生成好的 `hourly portfolio path` 做 pair-conditioned half-size；
- `summarize_hourly_pair_sizing_compare(...)`
  - 把 `raw / avoid_fluctuating / avoid_fluctuating_eth_sol_pair_halfsize` 放进同一张对照表。

本轮采用的最小策略是：
- 先保留 `avoid_fluctuating` gate；
- 只对 gate 后仍出现的 `ETH-USD + SOL-USD` 两仓小时做 `0.5x` 半仓；
- 不动别的 pair，不盲目砍掉所有 `2` 仓或高并发。

### 2) 新增 durable artifacts

写出以下新产物：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_path_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_hourly_summary_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_affected_hours_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

### 3) 更新网页可见产物

- `reports/site/factors/support_breakout_v0_h24/report.html`
  - 新增专门一段：
    - **如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？**
- `reports/site/factors/alpha_closure_board/report.html`
  - breakout 卡片现已同步写入：
    - residual sizing 已从“应该做”推进到“已经做了，而且 first-pass 有改善”；
- `reports/site/plans/momentum_todo.html`
  - Top 3 与 breakout 详细段已同步更新。

### 4) 更新 `docs/TODO.md`

- 将 Top 3 里的：
  - `breakout：在 gate 已落地前提下，补一刀“最小条件化 sizing”对照切片`
  - 正式标记为完成 `[x]`；
- 同时在 breakout 详细收口段补入这一刀的正式结果口径；
- 并把新的下一棒收窄成：
  - `把 ETH+SOL pair-conditioned halfsize 推到更严格的 holdout / walk-forward 复核`；
  - 以及 `比较“整个 ETH+SOL 两仓都半仓” vs “只动更窄 residual context”`。

## 核心结果

### 1) 这刀最小 sizing 是真有改善的，不只是“看起来更安全”

来自：
- `reports/artifacts/support_breakout_v0_h24/raw_gate_eth_sol_pair_halfsize_compare_20bps.csv`

同框架对照：

- **raw_v0**
  - `20bps hourly path` 累计约 `14.04%`
  - max drawdown 约 `-12.03%`
- **avoid_fluctuating**
  - 累计约 `15.46%`
  - max drawdown 约 `-9.97%`
- **avoid_fluctuating_eth_sol_pair_halfsize**
  - 累计约 `19.90%`
  - max drawdown 约 `-9.04%`

也就是说，只在这一个 residual pair 上做半仓：
- 相比 gate-only，累计约 **再提升 `+4.44pp`**；
- 同时 max drawdown 约 **再收窄 `0.93pp`**。

### 2) 它影响的不是大面积路径，而只是很窄的一块 hour bucket

- 受影响约 `44/398` 个活跃小时
- 约占 active hours 的 `11.06%`

这说明它确实是一刀**克制**的 conditional sizing，而不是靠“大面积砍仓位”换出来的改善。

### 3) 被压的 residual pair pocket 本身也确实收窄了

- `ETH+SOL` 两仓 pocket 原本条件累计约 `-7.17%`
- 做成 `0.5x` 后约收窄到 `-3.61%`

它主要长在这些 context：
- `validate × up`：约 `25` 小时
- `train × flat`：约 `14` 小时
- `test × up`：约 `3` 小时
- `test × down+flat`：约 `2` 小时

所以这刀并不是瞎砍，而是正中前面已经诊断出来的 residual weak pair。

## 这轮后的项目级读法

这轮之后，breakout 线可以更清楚地这样读：

1. `raw` 仍是主原型；
2. `confirm_1` 已经不值得继续抢位；
3. `avoid_fluctuating` 是有帮助的最小 gate；
4. 而在 gate 已落地之后，**pair-conditioned sizing** 现在也已经有了 first-pass 正证据：
   - 至少在当前样本里，动 `ETH+SOL` 这块 residual pocket，比继续做变体排序更值钱。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

验证命中：
- `support_breakout_v0_h24/report.html` 已出现：
  - `如果只做一刀最小条件化 sizing：把 gate 后的 ETH+SOL 两仓残余口袋降到半仓，会发生什么？`
  - `19.90%`
  - `-9.04%`
  - `-7.17%`
  - `-3.61%`
- `alpha_closure_board/report.html` 已同步写入这刀 sizing 的结果与下一步口径；
- `plans/momentum_todo.html` 与 `docs/TODO.md` 已同步更新。

## 风险 / 边界

1. 这仍是 **first-pass 条件化 sizing 切片**，不是正式 portfolio engine；
2. 当前 improved 结果仍可能部分来自当前样本 lucky patch；
3. 所以下一棒最该做的已经不是继续“找弱 pair”，而是把这刀 half-size 推到更严格的 holdout / walk-forward / portfolio honesty 里复核。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`scripts/build_alpha_closure_board_report.py`、站点页面和 artifact 路径里已有大量在途改动；此时做 selective commit 仍无法保证只打包本轮这一刀。
