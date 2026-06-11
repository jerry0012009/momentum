# Fresh intake：dynamic formation coint pairs first verdict = background / P0

- 时间：2026-04-08 18:32 UTC
- 对象：`research/quant_digests/2026-04-08_1751_dynamic-formation-coint-pairs-alpha.md`
- 槽位：Fresh intake
- 动作：fresh intake first verdict
- 结论：`background / P0`

## 为什么这轮直接收口
这篇 2021 arXiv 论文不是水货，最有价值的点也确实不是“crypto 也能做 pairs”，而是把 `formation / admission / pair-basket dynamic reselection` 说成了完整交易壳的一部分。

但按当前 bot3 的问题定义，本轮不是要判断“这篇论文有没有研究价值”，而是要判断它是否已经压成一个**不会被现有 plain pairs / static coint spread MR 家族吸收的独立 raw alpha 主语**。更诚实的答案仍然是否定的。

## 改变系统认知的证据
1. **alpha 本体仍是老的 coint spread fade，不是新的价格形成机制**  
   digest 自己的策略拆解已经写得很清楚：核心仍是 `cointegrated spread deviation -> mean reversion fade`，只是把 formation lookback、pair 重选、basket 版本、cost-aware admission 做得更系统。新增价值主要发生在 **pair selection / admission layer**，不是 raw alpha 本体换了一种新机制。

2. **这篇最值钱的是“formation / admission 影响成败”，不是新 queue-facing 主语**  
   `rolling formation window + dynamic reselection` 当然重要，但它更像告诉我们：plain pairs 不能只盯 z-score，要把 formation 做成 admission gate。它增强的是现有 coint-pairs 家族的筛选与治理逻辑，而不是生成一个和现有 pairs family 并列的新前排主语。

3. **当前证据仍停留在论文历史样本高 Sharpe 叙事，缺少对现有 pairs family 的独立增量证明**  
   digest 引用的亮眼结果来自 `2018-2019 BitMEX` 历史样本，虽然带 bid/ask 与 fee-aware backtest，但当前并没有额外 portability probe 去证明：
   - `dynamic formation / daily-weekly reselection` 相比固定 pair + 固定 lookback，
   - 在今天的 Binance/OKX `5m/15m`、
   - 成本后仍然形成可独立排序的新 admission edge。  
   目前能确认的是“这篇论文值得影响后续 pairs admission 设计”，还不能确认“它值得作为独立 intake 主语进入前排”。

4. **现有素材池里已经有更直接的 plain-pairs / coint-family 主语**  
   当前项目里已存在多条更直接的 pairs baseline / coint-family digest，例如：
   - `2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`
   - `2026-04-01_2105_dualtest-coint-zscore-pairs-alpha.md`
   - `2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`

   相比之下，这篇论文当前更适合作为 **pairs admission / formation design reference**，而不是新的 queue-facing raw alpha 身份。

## 诚实 verdict
- 不升 `keep_P1`
- 不分配新 Rank
- fresh intake first verdict 直接收口为：`background / P0`

## 一句话 result
`dynamic formation lookback × coint spread fade` 当前证明的是 pairs 家族的 formation/admission 设计很关键，但新增价值主要停留在动态重选与治理层，尚未证明它已脱离现有 plain pairs / static coint spread MR family 成为独立 queue-facing raw alpha，因此本轮 fresh intake 收口为 `background / P0`。
