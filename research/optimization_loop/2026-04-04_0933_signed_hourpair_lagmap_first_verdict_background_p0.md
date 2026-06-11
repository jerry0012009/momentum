# signed hour-pair lag map fresh intake — background/P0

- 时间：2026-04-04 09:33 UTC
- 轮次动作：`cycle_plan` 第 2 项（fresh intake）
- 对象：`research/quant_digests/2026-04-04_0756_signed-hourpair-lagmap-alpha.md`
- 结论：**不分配新 Rank，直接记为 `background/P0`**

## 本轮只回答什么
只回答这条 `UTC hour-pair signed lag map × continuation/fade` digest，是否提供了一个**独立于现有 time-of-day / hour-pair 主线**的新 raw alpha 壳，足以作为新的 front-slot intake 对象进入 `keep_P1`。

## first verdict
这条材料**不形成新的独立前排对象**，本轮应直接记为 `background/P0`：它虽然把 2022 NAJEF 论文 desk 化得更完整，写出了 `1H pocket discovery -> 15m execution -> jump/FOMC/liquidity veto` 的研究壳，但对象主语仍与已 intake 过的 `Rank 251 / intraday hour-pair momentum / reversal within pseudo trading day` 基本同构，且 `Rank 251` 的唯一 survivor follow-up 已经用 `BTC 近 90 天 × UTC 00/08/16 锚点 × 30d train / 7d OOS` 诚实证明：hour-pair pocket 会跨窗漂移、重复 pair 也缺乏稳定 post-cost 正边，因此这次新增价值主要是表述更清楚，不是带来新的独立 alpha lane。

## 为什么不能给 keep_P1
### 1) 主体对象与 `Rank 251` 同构，不是新 family
本条 digest 的核心主语仍然是：
- 同一 UTC 日内；
- earlier/source hour 的收益；
- 去预测 later/target hour 的收益；
- 不同 hour-pair 允许 continuation 或 reversal。

这与 `Rank 251` 的 `pseudo trading day × earlier hour -> later hour hour-pair mapping` 是同一对象族；把 `pseudo trading day` 改写成 `UTC hour-pair signed lag map`，并没有把对象边界推进成新的独立 family。

### 2) 已有对象不只“类似”，而是已经做过 cheap decisive falsification
`Rank 251` 的 survivor follow-up 不是停在 paper wording，而是已经回答过最关键问题：
- 限定 `UTC 00/08/16` 三个锚点；
- 近 90 天 BTC；
- `30d train / 7d OOS`；
- 允许滚动挑选当窗最强 pair；
- 结果仍是三种锚点 OOS 平均净收益都为负，最佳 pair 高频漂移，重复 pair 也不稳定。

所以这次不能再把同一主语当 fresh intake 重新排一次，只因为 digest 写得更 desk-friendly。

### 3) 它也没有形成能明显区别于 `Rank 201` 的新 lane
即便不拿 `Rank 251` 比，只看存活到 P3 的 `Rank 201 / UTC clock seasonality low-switch schedule`，当前 digest 也仍然属于更广义的 time-of-day intraday pocket 家族；它没有给出新的执行假设、独立数据源、或能绕开旧 falsification 的唯一 decisive blocker，因此不值得占一个新的前排 rank。

## 系统认知更新
系统现在应把这条 2026-04-04 digest 视为：
- 对旧 `hour-pair / time-of-day` 论文主线的**更清楚重述**；
- 可作为背景参考材料；
- 但**不是**新的 fresh intake front-slot 对象。

因此本轮不分配新 Rank，不进入 `Surviving candidate slot`，直接落回 `background/P0`。

## 本轮结果句
`2026-04-04_0756_signed-hourpair-lagmap-alpha.md` 没有带来独立于既有 `hour-pair / UTC clock` 主线的新 alpha lane；由于同构对象 `Rank 251` 已完成 survivor falsification 且未留下稳定 post-cost pocket，本轮 fresh intake first verdict 直接记为 `background/P0`。
