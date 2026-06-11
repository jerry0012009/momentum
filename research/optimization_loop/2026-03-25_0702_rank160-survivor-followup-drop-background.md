# Rank 160 survivor follow-up — bucket 成本后直接打回 background

- 时间：2026-03-25 07:02 UTC
- 轮次角色：bot3 survivor follow-up 执行
- 对象：`Rank 160 / rolling LASSO sparse next-minute raw alpha`
- 对应 cycle_plan 小点：`Surviving candidate slot`（唯一一次 decisive follow-up；回答 `promote_P2` 或 `drop_to_background`）

## 本轮只做的事
把现有最小 proxy 结果收紧成 survivor 级 yes/no 问题：
- bucket 划分：
  - `high-liquidity = BTCUSDT / ETHUSDT / SOLUSDT`
  - `retail-beta = DOGEUSDT / XRPUSDT / LTCUSDT`
- 成本口径：统一按 **`6 bps round-trip`** 的保守 taker/spread 成本判断（与本周分钟级 survivor follow-up 的统一诚实口径一致）
- 使用产物：`reports/artifacts/quant_digests/sparse_lasso_intraday_probe_20260325/symbol_summary.csv`

## 关键证据
按每个 symbol 在 long/short 两侧里取**最慷慨**的一侧毛收益上界，结果依然远低于保守成本：

### high-liquidity bucket
- `BTCUSDT`：最好一侧毛收益仅 **`+0.217 bps/trigger`**，扣 `6 bps` 后约 **`-5.783 bps`**
- `ETHUSDT`：最好一侧毛收益仅 **`+0.031 bps/trigger`**，扣 `6 bps` 后约 **`-5.969 bps`**
- `SOLUSDT`：连最好一侧也只有 **`-0.375 bps/trigger`**，扣成本后约 **`-6.375 bps`**
- 即使做最宽松的 trigger-weighted generous 上界，bucket 也只有 **`-6.052 bps/trigger`**

### retail-beta bucket
- `DOGEUSDT`：最好一侧是 short，毛收益仅 **`+0.605 bps/trigger`**，扣 `6 bps` 后约 **`-5.395 bps`**
- `XRPUSDT`：最好一侧毛收益仅 **`+0.251 bps/trigger`**，扣成本后约 **`-5.749 bps`**
- `LTCUSDT`：最好一侧毛收益仅 **`+0.128 bps/trigger`**，扣成本后约 **`-5.872 bps`**
- 即使做最宽松的 trigger-weighted generous 上界，bucket 也只有 **`-5.767 bps/trigger`**

## 这意味着什么
这次 survivor blocker 问的不是“有没有一点分钟级预测毛边”，而是：

> 在 `high-liquidity` 与 `retail-beta` 两个 bucket 中，这条 sparse minute alpha 在保守 taker/spread 成本后，是否还能保留稳定正的 `post-cost avg bps/trigger`？

答案已经足够明确：**不能。**

原因不是 bucket 方向找错，而是更根本：当前 public-data proxy 留下的毛边量级只有 **`0.0x ~ 0.6 bps/trigger`**，距离 desk 可接受的分钟级 taker/spread 成本还有整整一个数量级差距。换句话说，`Rank 160` 证明了“分钟级 sparse predictor 叙事成立”，却没有证明“在可交易 bucket 里还能活成成本后正收益 pocket”。

## verdict
**结论：`drop_to_background`。**

它不该升 `P2`，因为 survivor 级唯一 blocker 已经被直接回答为否；继续把它留在前排只会把“有研究味道的分钟级 ML 骨架”误判成“有 desk 成本后 pocket 的 pre-paper 候选”。

## runtime 变化
- `Rank 160` 用完 survivor 唯一一次 follow-up 预算
- `Fresh intake slot` 释放为 `open / none`
- `Surviving candidate slot` 清空
- `Active P2 slot` 继续保持 `none`
- `Background pool.latest_parked` 更新为 `Rank 160`
- `cycle_plan[1]` 应写成 `done`
- `cycle_plan[2]` 因第 1 项否决 `promote_P2` 前提而应写成 `blocked`
- 下一条合法 pending 动作应顺延到 conditional fresh intake

## 一句话结果
`Rank 160 / rolling LASSO sparse next-minute raw alpha` 在 `high-liquidity` 与 `retail-beta` 两个 bucket 中最慷慨的一侧毛收益上界也只有 `0.605 bps/trigger`，被统一 `6 bps round-trip` 保守成本完全吞没，因此 survivor follow-up 直接收口为 `drop_to_background`，不升 `P2`。
