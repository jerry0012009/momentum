# Fibonacci 第二刀本地验证：补跑 retest_hold，发现它是当前最不差的一档

## 为什么这次选这个

这轮继续严格沿上一轮刚跑出的 Fibonacci 本地验证切片往前走，仍然坚持 Jerry 刚刚强调的方向：**少做流程，多做真验证。**

上一轮已经证明：
- `confirm_1bar / confirm_2of3` 能明显降低快速被打脸比例；
- 但还没把净收益救正。

所以最自然的下一小步，不是再去补文档，而是把 mini brief 里最后一个紧邻关键变体 `retest_hold` 真跑出来，看它会不会在“确认太慢”和“假信号太多”之间给出更好的折中。

这轮最值得复用/借鉴的点是：**`retest_hold` 这类结构确认，并不一定把“失效比例”压到最低，但可能在“别太容易被打脸”和“别因为太晚进场而亏得更多”之间给出更好的折中。**

## 核心结论（中文摘要）

核心结论：**在 BTC/ETH/SOL 的 15m / 60d 第二刀本地切片里，`retest_hold` 是当前四档 (`baseline / confirm_1bar / confirm_2of3 / retest_hold`) 中整体最不差的一档：它没有像 `confirm_2of3` 那样把 invalidation 压到最低，但在净收益、胜率和失效率之间给出了更均衡的 trade-off。**

证据如何支持这个结论：**聚合结果里，`retest_hold` 的 `mean_net_return ≈ -0.024%`，优于 `baseline ≈ -0.042%`、`confirm_1bar ≈ -0.068%`、`confirm_2of3 ≈ -0.029%`；同时它的 `win_ratio ≈ 45.6%` 也是四档里最高。虽然它的 `12-bar invalidation ratio ≈ 37.1%` 高于 `confirm_2of3 ≈ 31.0%`，但仍显著低于 `baseline ≈ 51.3%`。这说明 retest-hold 目前更像“更均衡的 confirmation/filter 候选”，而不是已经成立的独立 alpha。**

## 本轮做了什么改动

本轮只做一个主点：**在上一轮 Fibonacci 本地切片的基础上，补跑 `retest_hold` 变体。**

具体动作：

1. 继续使用相同的最小实验口径
   - 数据：Binance `BTCUSDT / ETHUSDT / SOLUSDT`
   - 周期：`15m`
   - 窗口：`60d`
   - `causal swing protocol v1`
   - 成本：`10bps round-trip`
   - 持有：`24 bars`
   - 额外评估：`12-bar invalidation ratio`

2. 新增 `retest_hold` 规则（最小版）
   - 先发生一次 touch；
   - 再先回到有利方向（long: close 回到 `fib38` 上方；short: close 回到 `fib38` 下方）；
   - 然后在接下来最多 `6` 根 bar 内，再次回踩 `38.2/50` zone；
   - 若回踩当根仍收在有利方向，则下一根 open 入场。

3. 产物
   - `reports/artifacts/fibonacci_confirmation_slice_v2/summary.json`
   - `reports/artifacts/fibonacci_confirmation_slice_v2/summary_by_variant.csv`
   - `reports/artifacts/fibonacci_confirmation_slice_v2/summary_by_asset.csv`
   - `reports/artifacts/fibonacci_confirmation_slice_v2/events.csv`

4. 更新 `docs/TODO.md`
   - 在 Fibonacci mini brief 的最新进度说明中追加 `retest_hold` 结果；
   - 并同步重建 `plans/momentum_todo.html` 镜像页。

## 验证 / 证据

### 1) 四档聚合结果

- `baseline`
  - `trade_count = 1962`
  - `mean_net_return ≈ -0.042%`
  - `win_ratio ≈ 45.4%`
  - `invalidation_ratio_12b ≈ 51.3%`
  - `mean_entry_lag_bars = 1.0`

- `confirm_1bar`
  - `trade_count = 842`
  - `mean_net_return ≈ -0.068%`
  - `win_ratio ≈ 42.8%`
  - `invalidation_ratio_12b ≈ 32.2%`
  - `mean_entry_lag_bars = 2.0`

- `confirm_2of3`
  - `trade_count = 849`
  - `mean_net_return ≈ -0.029%`
  - `win_ratio ≈ 44.1%`
  - `invalidation_ratio_12b ≈ 31.0%`
  - `mean_entry_lag_bars = 4.0`

- `retest_hold`
  - `trade_count = 649`
  - `mean_net_return ≈ -0.024%`
  - `win_ratio ≈ 45.6%`
  - `invalidation_ratio_12b ≈ 37.1%`
  - `mean_entry_lag_bars ≈ 4.8`

### 2) 怎么解读

- 如果只看“尽量别被快速打脸”，`confirm_2of3` 仍是最强；
- 如果看“总体别亏太多 + 胜率别太差 + 失效率也别太高”，`retest_hold` 更均衡；
- 但最重要的是：**四档在 10bps 成本下仍都没有转成清晰正收益。**

所以当前最合理的解释是：
- Fibonacci confirmation 这条线确实在“过滤假信号”上有用；
- 但它更像 filter / confirmation layer，仍不是已成立的独立 alpha 主体。

### 3) 分资产观察

- `BTC`
  - `retest_hold ≈ +0.088%`，是 BTC 上最好的变体；
  - `win_ratio ≈ 51.7%`，也是四档里最好。
- `ETH`
  - `retest_hold ≈ -0.009%`，接近打平，但不如 `confirm_1bar` 的小幅正值；
- `SOL`
  - `retest_hold ≈ -0.140%`，仍明显为负，但比 `confirm_1bar` 好。

这说明：
- `retest_hold` 的优势并不是“每个币都最好”；
- 而是它在三币聚合里给出了更均衡的整体 trade-off。

## 风险 / 边界

- 这是第二刀最小切片，仍不是正式策略回测；
- `retest_hold` 当前实现只是 mini brief 对应的最小版，还没有比较更多 zone / retest 容忍度 / stop 定义；
- 成本仍只是一档 `10bps round-trip`；
- 当前 tradeoff 结论依赖这套 v1 定义，后续若 pair 失效规则或 zone 定义改变，结果可能会变化。

## 下一步建议

1. 如果继续沿这条线推进，最值得做的下一小步是：
   - 比较 `confirm_2of3` vs `retest_hold` 的更严格成本场景；
   - 或比较它们在更长持有期 / 更短持有期下的 trade-off 是否稳定。

2. 如果目标是尽快找更靠谱的 alpha，而不是继续雕这条线，那么当前最理性的定位是：
   - **保留 Fibonacci 作为 `confirmation / filter candidate`；**
   - **不要再把它当“可能独立成立的 alpha 主体”继续深挖太多轮。**

3. 也就是说，这条线已经基本回答了它最重要的问题：
   - confirmation 有用；
   - 但还不够强到升成 alpha candidate。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。