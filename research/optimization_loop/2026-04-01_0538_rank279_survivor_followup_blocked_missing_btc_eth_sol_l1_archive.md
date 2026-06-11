# Rank 279 survivor follow-up — blocked：缺少可直接复验的 BTC/ETH/SOL 共通 minute-level L1 历史样本

- 时间：2026-04-01 05:38 UTC
- 对象：`Rank 279 / L1 imbalance × VWAP spread direction`
- 本轮动作：按 state 只执行它唯一一次 survivor-style 诚实检查，回答 `BTC/ETH/SOL` 在 minute-level clean-room replication 下，`1m/3m` taker-first continuation 是否至少留下一档统一 `4/8/12 bps` friction ladder 后仍可迁移的 after-cost pocket
- 本轮结果：`blocked`

## 为什么这一步必须 blocked，而不是硬凑 verdict
这轮指定要回答的不是论文 headline，也不是“这类微结构信号通常有没有信息量”，而是一个更窄、更具体的问题：

> 在 **`BTC/ETH/SOL` 共通样本**、**minute-level clean-room replication**、**`1m/3m` 固定持有**、**统一 `4/8/12 bps` round-trip friction ladder`** 下，是否存在至少一个可迁移 after-cost pocket？

当前工作区里并没有足以直接回答这个问题的现成共通样本：

1. **没有现成的 `BTC/ETH/SOL` 共通 L1 minute/second 历史归档** 供直接复验；
2. 本地能找到的 `bookTicker` 旧样本主要是早前别的 rank 残留单日/异币种材料，不能诚实替代本轮要求的 `BTC/ETH/SOL` 共通检查；
3. 若只拿 `BTC` 单币或零散旧日包去拼，会把问题偷换成“某一天某一币有没有一点 proxy edge”，回答的就不再是 state 当前指定的那道 survivor 问题。

## 本轮真正改变系统认知的话
`Rank 279` 当前的唯一 blocker 已经收窄得很明确：**不是 skeleton 不清楚，而是缺少能直接做 `BTC/ETH/SOL` 共通 minute-level L1 replication 的历史样本；在这个前置条件未补齐前，当前轮次不能诚实输出 `promote_P2`，也不该用不完整 proxy 直接把它打回 `background/P0`。**

## 下一步前置条件（仅作为 blocker 说明，不是本轮重排）
若后续要继续这条线，前提必须是先补齐至少一段可审计的 `BTC/ETH/SOL` 共通 `bookTicker/depth + aggTrades` 历史样本，再统一压成 minute score，输出：
- `1m/3m` long / short / combined gross
- `4/8/12 bps` net ladder
- asset-level pocket 对比

在此之前，这条 survivor-style 检查只能保持 `blocked`。
