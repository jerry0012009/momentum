# Rank 180 / network-peripheral-pairs-book intake -> keep_P1

- 时间：2026-03-26 07:06 UTC
- 对象：`research/quant_digests/2026-03-26_0617_network-peripheral-pairs-book.md`
- 执行动作：fresh intake 最小首判
- 结论：`keep_P1`
- 正式 Rank：`180`

## 本轮只回答一个问题
`peripheral same-community pair book construction` 这条对象，是否值得作为前排 survivor 保留？

答案：**值得，保留为 `keep_P1`。**

但要保留的不是泛化的“network science helps trading”，也不是把 network 当独立 alpha 本体；本轮保留的是一条更具体的骨架：

> **pairs raw alpha + peripheral same-community book construction**

也就是：底层仍然是 `cointegrated / stable spread mean reversion` 的 pairs raw alpha；network 这一层只是用来决定 **哪些 pair 更适合一起放进同一本 book**，尤其优先考虑 **same-community 且 peripheral** 的 pair，默认回避跨社区 weak-tie。

## 为什么不是直接 park
1. digest 已经把对象边界说得足够清楚：它不是模糊的“网络有帮助”，而是非常具体的 **pairs 配书规则**。
2. 论文主结论与本地代理快检方向一致：
   - 经典 top-pairs 在小样本 liquid majors 上仍更强；
   - 但 `peripheral_same_community` 至少优于 `central_same_community` 的持仓效率/隐藏共振风险画像；
   - `weak-tie cross-community` 缺乏保留价值。
3. 这条线补的是 pairs desk 里常见但经常被低估的问题：**单对能回归，不等于放成一本 book 后不会一起共振出事。** 这足以支撑一次 survivor 级 follow-up。

## 为什么还不到 P2
1. 当前证据更像 **portfolio-construction / book overlay**，不是已经能独立证明净边更厚的全新 alpha 家族。
2. 本地快检没有复现出 “peripheral > classic top-pairs” 的更强结论，只能说明它可能改善 risk-adjusted / contagion honesty。
3. 现阶段最诚实的下一步，不是继续写更大的故事，而是做一次便宜但 decisive 的 follow-up：
   - 把 network 只放在配书层，不改 base pairs alpha score；
   - 与 classic top-pairs 做 rolling book 对照；
   - 重点看 overlap / contagion / CVaR / 社区集中度，而不只是均值收益。

## 对系统认知的更新
**Rank 180：`pairs raw alpha + peripheral same-community book construction` 首判成立，保留为唯一一次 survivor follow-up 对象；当前保留的是更诚实的 pairs 配书骨架，不是新的独立 network alpha。**
