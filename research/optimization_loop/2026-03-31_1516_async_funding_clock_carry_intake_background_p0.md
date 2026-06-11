# asynchronous funding clock × net-hour hurdle — fresh intake 首判（background/P0）

- 时间：2026-03-31 15:16 UTC
- 执行者：bot3 auto 13m loop
- Source digest: `research/quant_digests/2026-03-31_1302_async-funding-clock-carry-alpha.md`
- Object: `asynchronous funding clock × net-hour hurdle`
- Verdict: `background/P0`

## 本轮回答的唯一问题
这条对象是否足够区别于已收口的 cross-venue funding carry 家族旧对象，值得作为新的 fresh intake survivor 留在前排；还是应承认它主要是在旧 funding carry 骨架上补了一层更诚实的异步 funding 时钟计价，因此不该再单独占用前排预算？

本轮结论是：**它不进入前排，直接回 background/P0。**

## 为什么这次不该再给新的前排名额
1. **alpha 主体没有换，换的是 admission 计价方式。**  
   digest 里最有价值的新点，是把 `Hyperliquid 1h` 对 `Bybit 8h` 的 funding carry 改写成“未来持有窗口里实际会收几次、付几次 funding”的 `expected_net_carry(H)`。这很重要，但它修正的是 **同一条 cross-venue funding carry** 的 entry/accounting honesty，而不是产生一个新的独立 raw alpha 主体。

2. **repo 给的是 execution OS + clock-aware valuation，不是新的收益来源。**  
   本次对象当然比“静态 funding diff 排名表”更完整：它多了 tranche、orphan leg 处理、linked protection、grace period、clock risk。但这些都属于把旧 carry 家族写得更诚实，而不是把收益来源从 funding carry 之外挖出新的结构性边。

3. **家族里最近两条更接近的对象已经把可保留空间基本收口完了。**  
   - `Rank 168` 保留过的，是“`venue tier + duration gate` 下也许仍成立的窄版 funding carry skeleton”；
   - `Rank 260` 则把 same-underlier perp-perp funding diff 明确收口成“极低频 dislocation pocket”，并已退出前排。

   当前这条 `asynchronous funding clock × net-hour hurdle` 更像对前述家族结论的**进一步诚实化**：告诉我们不能只看静态 diff，而要按异步 funding settlement clock 去算未来窗口 carry。它提高了我们对旧家族的理解精度，但没有强到足以重新开一条新的前排对象。

4. **digest 自己给的 live quick check 也更支持“pocket carry accounting refinement”，不支持“新 front-slot alpha”。**  
   当前快照里：
   - `AVAX` 最佳 gross carry 约 `4.60 bps/day`
   - `WIF` 约 `3.79 bps/day`
   - `ETH` 约 `0.88 bps/day`
   - `BTC` 几乎为零

   这说明它仍然更像少数币、少数窗口的 pocket carry；而且 repo 的关键改进是“持有窗计价 + clock-aware admission”，不是证明这里出现了一个足够宽、足够独立的新 alpha 家族。

## 为什么不是 keep_P1
若给 `keep_P1`，等于默认承认它是一个应继续占用 survivor 预算的**新对象**。但当前最诚实的描述应是：

> `asynchronous funding clock × net-hour hurdle` 是对 cross-venue funding carry 家族的关键 accounting / admission 修正，不是足够独立的新 raw alpha；它应并回 funding carry evidence pool，而不是单开新的前排 rank。

也就是说，这条 digest 有研究价值，但价值主要在于**修正 family-level reading**，而不是开启一个新候选的前排推进链。

## 改变系统认知的一句话
**`asynchronous funding clock × net-hour hurdle` 不应被当作新的 front-slot raw alpha；它更像对旧 cross-venue funding carry 家族的关键诚实化修正——把静态 funding diff 改写为按异步 settlement clock 计价的 `expected_net_carry(H)`，因此本轮最诚实结论是直接并回 background/P0。**

## 最终 verdict
- 不分配新 Rank
- 不进入 survivor slot
- `Fresh intake` 首判：`background/P0`
- 后续若再用到这条材料，应作为 funding carry 家族的 admission/accounting 参考，而不是自动 reopen 成新的前排对象
