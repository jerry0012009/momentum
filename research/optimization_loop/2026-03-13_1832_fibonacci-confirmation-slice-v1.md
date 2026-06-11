# Fibonacci 第一个本地验证切片：确认能降假信号，但还没把 alpha 救正

## 为什么这次选这个

这轮刻意响应 Jerry 刚刚的担心：**不再继续补流程页，不再继续做只停留在 reading/brief 层的事务，而是直接做一个最小、可验证的本地实验切片。**

我选择的是最近几轮已经连续铺垫过的 `Gurrib et al. (2022)` / Fibonacci 这条线，但这次不再补来源卡或 protocol，而是直接拿它的 mini brief 去跑一个最小验证：

- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 数据窗：`60d`
- 口径：`causal swing protocol v1`
- 变体：`baseline / confirm_1bar / confirm_2of3`

这轮最值得复用/借鉴的点是：**确认层有可能明显降低“快速被打脸”的比例，但这不等于已经救活 alpha；降低假信号和做出正收益，是两回事。**

## 核心结论（中文摘要）

核心结论：**在 BTC/ETH/SOL 的 15m / 60d 第一个本地切片上，Fibonacci 的 `confirm_1bar` 和 `confirm_2of3` 都明显降低了 12 bar 内的快速失效比例，但整体净收益仍未转正；其中 `confirm_2of3` 是三者里最不差的一档，因此当前更像 `confirmation / filter candidate`，还不能当独立 alpha 成立。**

证据如何支持这个结论：**本轮共生成 3653 条事件；`baseline` 的 `invalidation_ratio_12b` 约为 `51.3%`，而 `confirm_1bar` / `confirm_2of3` 分别压到约 `32.3% / 31.0%`。但净收益方面，三组在 10bps round-trip cost 下都仍为负：`baseline ≈ -0.043%`、`confirm_1bar ≈ -0.070%`、`confirm_2of3 ≈ -0.031%`；也就是说，确认层确实减少了假信号，但还没有把这条线变成稳健正 alpha。**

## 本轮做了什么改动

本轮只做一个主点：**对 Fibonacci mini brief 做第一刀本地验证切片。**

具体动作：

1. 直接用 Python ad-hoc 实验跑了最小切片
   - 数据：Binance `BTCUSDT / ETHUSDT / SOLUSDT`
   - 周期：`15m`
   - 窗口：`60d`
   - 使用 `causal swing protocol v1`：
     - pivot 需 `2-bar right confirmation`；
     - pair 只能由最近一对已确认 opposite swings 生成；
     - 不允许 retroactive rewrite。

2. 变体设置
   - `baseline`：触及 `38.2 / 50` 区间后，下一根开盘入场
   - `confirm_1bar`：触位后下一根 close 仍在有利方向，再入场
   - `confirm_2of3`：触位后 3 根里至少 2 根 close 仍在有利方向，再入场

3. 评估口径
   - 持有：`24 bars`
   - 成本：`10bps round-trip`
   - 额外记录：`12 bar invalidation ratio`
     - long：12 bar 内是否跌破 swing low
     - short：12 bar 内是否升破 swing high

4. 产物
   - `reports/artifacts/fibonacci_confirmation_slice_v1/summary.json`
   - `reports/artifacts/fibonacci_confirmation_slice_v1/summary_by_variant.csv`
   - `reports/artifacts/fibonacci_confirmation_slice_v1/summary_by_asset.csv`
   - `reports/artifacts/fibonacci_confirmation_slice_v1/events.csv`

5. 更新 `docs/TODO.md`
   - 在 Fibonacci mini brief 的进度说明下补入这一轮最小实验结论；
   - 并同步重建 `plans/momentum_todo.html` 镜像页。

## 验证 / 证据

### 1) 总体结果（3 币聚合）

- `baseline`
  - `trade_count = 1961`
  - `mean_net_return ≈ -0.043%`
  - `win_ratio ≈ 45.3%`
  - `invalidation_ratio_12b ≈ 51.3%`
  - `mean_entry_lag_bars = 1.0`

- `confirm_1bar`
  - `trade_count = 843`
  - `mean_net_return ≈ -0.070%`
  - `win_ratio ≈ 42.7%`
  - `invalidation_ratio_12b ≈ 32.3%`
  - `mean_entry_lag_bars = 2.0`

- `confirm_2of3`
  - `trade_count = 849`
  - `mean_net_return ≈ -0.031%`
  - `win_ratio ≈ 43.9%`
  - `invalidation_ratio_12b ≈ 31.0%`
  - `mean_entry_lag_bars = 4.0`

### 2) 怎么解读

- `confirm_1bar / confirm_2of3` 都显著减少了“快速被打脸”的比例；
- 但它们也带来了更晚的入场，尤其 `confirm_2of3` 平均会晚 `4` 根 bar；
- 所以这条线目前最合理的解释是：
  - **confirmation 有助于过滤假信号；**
  - **但过滤掉假信号，不自动等于净收益转正。**

### 3) 分资产观察

- `BTC`
  - `baseline ≈ +0.019%`
  - `confirm_1bar ≈ -0.039%`
  - `confirm_2of3 ≈ +0.033%`
- `ETH`
  - `baseline ≈ -0.032%`
  - `confirm_1bar ≈ +0.016%`
  - `confirm_2of3 ≈ -0.009%`
- `SOL`
  - 三组都为负，且 `confirm_1bar` 最差；`confirm_2of3` 只是比它略好

这说明：
- 目前没有跨三币都一致转正的证据；
- `confirm_2of3` 只是“最不差”，还不是“已成立”。

## 风险 / 边界

- 这是**第一刀最小验证切片**，不是正式策略回测；
- 变体只覆盖了 `baseline / confirm_1bar / confirm_2of3`，还没跑 `retest_hold`；
- 成本只用了单一 `10bps round-trip`，还没做更严格成本或资金费率；
- 当前 swing / pair / touch 的工程定义仍是 v1，未来可能还要审计：
  - zone 定义是否过宽
  - pair 失效规则是否该更严格
  - 以及 `1bar / 2of3 / retest` 对 lag 的 tradeoff。

## 下一步建议

1. 如果继续沿这条线推进，下一步最值得做的是：
   - 补 `retest_hold` 变体；
   - 看它是否能在保持较低 invalidation ratio 的同时，改善净收益。

2. 另一条更稳的路线是：
   - 不把 Fibonacci 当独立 alpha；
   - 而是把它并入已有 breakout / pullback 主线里，作为上层 confirmation/filter 特征。

3. 当前最诚实的临时判断：
   - `Fibonacci` 可以保留为 `confirmation / filter candidate`；
   - 还不该升级成 `alpha candidate`。

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史重建产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成日志、邮件、artifact 落盘与 TODO 镜像同步，不做提交。