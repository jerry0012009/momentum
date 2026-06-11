# Rank 303 survivor follow-up（clean-room）

- 时间：2026-04-03 05:15 UTC
- 轮次：bot3 auto optimization
- 对象：`Rank 303 / realized-skewness cross-section fade`
- 动作：执行 survivor 唯一一次 clean-room follow-up
- 结论：`background/P0`

## 本轮要回答的问题
仅回答一个问题：`realized skewness` 相对当前已在池中的 `ret_24h` 横截面 reversal 与 `MAX / lottery-fade` 家族，是否仍保有足以单独 admission 到 `P2` 的新增主语；如果没有，就按 policy 诚实收口。

## clean-room 对照结论
1. **对 `ret_24h` 的增量主语不够硬。**
   `Rank 303` 真正想表达的是“右尾更肥 / 更彩票化的币后续更容易回吐”，但在当前 digest 能支持的最小 desk 口径里，它还没有拿出一条已经完成的 liquid-perp clean-room 结果，去证明自己在同窗长、同持有、同成本下能稳定胜过或补充 `-rank(ret_24h)`。在 survivor 轮里，如果这一步回答不出来，就不能继续把它当作独立 sleeve 往前推。

2. **对 `MAX` 的 distinctness 停在概念层，不足以升到 admission。**
   fresh intake 那轮已经说明：`realized skewness` 看的确实不是单根极值，而是整段收益分布的右偏形状；这足以支持它先进 `P1`。但 survivor 轮要求的是更高一档的问题——不是“统计对象是否不同”，而是“在 liquid perp / 15m 壳里是否还有可交易的独立增量”。目前能确认的仍只是它比 `MAX` 更平滑、故事更完整；还不能确认它在交易层面不是 `MAX + lagged-return reversal` 的连续化重写。

3. **当前最诚实的系统判断，是把它并回既有 lottery/reversal 家族，而不是继续单列。**
   这条线最可能留下来的价值，是作为多因子横截面排序里的一个 distribution-shape feature，或作为 `MAX` / `ret_24h` 的 companion descriptor；但按当前证据，还不够把它当成需要单独占用 `P2` 资源的 raw-alpha sleeve。

## 出口决策
`Rank 303` 的 survivor follow-up 结论为：

> 在本轮 clean-room 对照下，`realized-skewness cross-section fade` 对 `ret_24h` 与 `MAX` 的独立增量仍未被证明到足以单独 admission 的程度；它目前更像既有 `lagged-return reversal / lottery-fade` 家族的分布形状 companion feature，而不是需要继续前排推进的独立对象，因此按 policy 收口为 `background/P0`。

## runtime 回写要点
- `Surviving candidate slot`：消耗唯一 follow-up 预算并收口（不再保留当前目标）。
- `Background pool`：登记 `Rank 303` 为最新 parked。
- `cycle_plan[1]`：`status=done`，并写入本轮改变系统认知的结果句。
