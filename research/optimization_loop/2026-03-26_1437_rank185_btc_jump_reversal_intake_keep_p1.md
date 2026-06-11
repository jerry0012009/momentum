# Rank 185 / BTC 4h 3σ shock-reversal sleeve — fresh intake keep_P1

- 时间：2026-03-26 14:37 UTC
- Executor：bot3 auto 13m loop
- Source digest：`research/quant_digests/2026-03-26_1428_btc-jump-reversal-tail-fade.md`
- Object：`BTC extreme-bar next-bar reversal`
- Verdict：`keep_P1`
- Assigned rank：`Rank 185`

## 本轮只回答一个问题
`BTC extreme-bar next-bar reversal` 这条 raw alpha，当前是否值得进入 survivor？

回答：**值得，但只保留 `4h 3σ` 冲击回摆这一个 exact pocket；不把 `5m 6σ` 尾部反打一并保留。**

## 为什么不是直接 park
这轮 digest 已经给出足够明确、会改变系统认知的正面信息：

1. **对象边界是清楚的。**
   这不是泛泛的“BTC 会均值回归”，而是非常具体的 `上一根极端 bar -> 下一根反向 -> 持有 1 根同周期 bar` 事件驱动 raw alpha。
2. **当前 transfer check 里确实还有一个成本后可活 pocket。**
   `4h, 3σ` 在 Binance BTCUSDT perp 近样本里是 `89` 笔、毛收益约 `10.08 bps/trade`，按 `4 bps` round-trip 仍有约 `+6.08 bps/trade`，即便到 `10 bps` 也基本打平；这已经不是“看起来像反转、但一加成本就全灭”的空框架。
3. **后续唯一便宜 follow-up 很明确。**
   survivor 那一轮不需要再泛讲均值回归，只需诚实回答：`4h 3σ` 这条 pocket 在更细的事件分层、成交口径与时间稳定性下，是否仍能保住 `shock-reversal sleeve` 的 admission 价值。

## 为什么保留的是 4h 3σ，而不是 5m 6σ
`5m 6σ` 虽然也还活着，但当前证据显示它更像**执行极敏感的薄 edge**，不适合作为这轮唯一 survivor：

- `5m, 6σ` 毛收益约 `4.59 bps/trade`；
- 到 `4 bps` round-trip 后只剩约 `+0.59 bps/trade`；
- 一旦把滑点、next-close 假设误差、尾部事件时的 spread 扩张带进去，就很容易从正值掉回负值。

所以本轮最诚实的首判，不是把 `5m + 4h` 两个 pocket 一起打包保留，而是：

> **只把 `BTC 4h 3σ shock-reversal sleeve` 留在前排；`5m 6σ` 先不作为 survivor 身份保留。**

## 本轮改变的系统认知
**Rank 185：`BTC extreme-bar next-bar reversal` 目前唯一值得进入 survivor 的，不是泛化的 BTC 反打框架，也不是执行极薄的 `5m 6σ` 尾部反打，而是成本后仍有余量的 `4h 3σ shock-reversal sleeve`。**

## Reader-facing conclusion
`Rank 185 / BTC 4h 3σ shock-reversal sleeve` 首判为 `keep_P1`：当前公开证据已足够把 `BTC extreme-bar next-bar reversal` 缩到一个可继续跟进的 exact raw alpha pocket；后续 survivor 唯一值得做的 follow-up，应只回答这条 `4h 3σ` 冲击回摆在更真实的事件分层、成交口径与时间稳定性下是否还能诚实保留，而不是再把它泛化回“BTC 大涨大跌后都该反着做”。
