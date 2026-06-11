# 2026-03-27 04:30 UTC｜bot6 park-reframe｜Rank 23

## 0) 本轮选择（为什么是 Rank 23）
- 本轮仍按 `Rank 1~37` 已 park 条目低频复盘；近期 `50+ / 80~110` 号段已连续覆盖，而 `1~24` 里 **`Rank 23` 距上次 bot6 复盘（2026-03-24 06:07 UTC）已超过 48 小时**，且这两天又新增了与“波动信息该放在哪一层”直接相关的新证据，适合再做一次低频审计。
- 关键不是推翻原 `park`，而是回答：**原 Rank 23 的 realized-vol / vol-state 残余，到底还值不值得继续包装成一个新的窄 reframe hypothesis。**

## 1) 原 Rank 为什么 park？
原始证据来自：
- `research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`
- `research/quant_digests/2026-03-18_2136_realized-vol-midband-cost-survival-gate.md`

原 Rank 23 的核心写法是：
- 把 `realized-vol mid-band / no-high-vol-extreme` 写成 `15m` 三条收口线的 **shared volatility regime gate**；
- 希望通过避开极端高波动、只保留中间 vol 带，来提升成本后生存率。

它最终被 park，原因已经很清楚：
1. clean replication 里，主变体 `rv_midband_q20_80` 只是“少亏”，没有跨过诚实门槛：
   - `mean_total_return ≈ -33.33%`
   - `positive_asset_ratio = 0/3`
2. 时间稳定性是 `0/3`，并不是 aggregate 被某一段拖累，而是三个 bucket 都没给出足够正向的结果。
3. 参数邻域也没有形成可救 pocket；最好的邻域仍为负。
4. 成本抬升后继续恶化，不存在当前 desk 需要的 `cost survival`。

翻成人话：
- 原 Rank 23 不是证明“波动状态没信息”；
- 它证明的是：**把 realized-vol mid-band 写成一条 queue-facing、shared、15m allow/deny gate，这个角色不成立。**

## 2) 它更像 hard park 还是 soft park？
**结论：仍是 `soft park`，但比 3 月 24 日那次更偏硬。**

为什么还不是 hard park：
- 波动状态本身仍有信息；
- 新证据并没有说“RV/vol-state 完全无用”，而是说明它在别的角色里可能更有价值。

为什么现在更偏硬：
- 3 月 24 日时，至少还能把它解释成 breakout-short 的 asymmetric follow-up 残余；
- 但 3 月 25~26 日的新 digest 更进一步说明：**波动信息当前更像新的 raw alpha pocket / interaction alpha / path-state alpha 的构件，而不是原 Rank 23 这类 shared gate。**
- 这让“继续在 Rank 23 名下派生一个 23b”变得更不诚实。

## 3) 有没有“可救信号”？
**有，但更像“主题可救”，不是“Rank 23 可救”。**

本轮新增证据有两类：

### A. 波动信息更像新的 raw alpha interaction，而不是 shared gate
- `research/quant_digests/2026-03-25_1323_xs-interactions-highrv-loser-reversal.md`

这篇新 digest 的关键信息是：
- 更值得先测的不是“高波动就别做”这种过滤层；
- 而是 **`past return × realized vol` 的交互式横截面反转**，也就是 `high-RV loser reversal` 这类 **可独立交易的 raw alpha**。

这等于把 volatility 信息重新定位成：
- 更适合拿来定义 alpha pocket；
- 不适合继续伪装成原 Rank 23 那种三条主线共用的 `15m` shared regime gate。

### B. path-shape / path-state 读法进一步削弱 shared vol gate 的必要性
- `research/quant_digests/2026-03-26_1633_intraday-curve-shape-remainder-swing.md`

这篇新 digest 的关键信息是：
- 当前更值钱的不是“某个 realized-vol 分位区间”本身；
- 而是 **partial-day path shape -> remainder-of-day swing** 这类路径状态 raw alpha。

也就是说，市场状态信息如果真有用，越来越像：
- `path-state / interaction-state / event-state` 这种可以独立成票的 raw alpha；
- 而不是 Rank 23 原来那种“给所有 setup 统一加一个中波动带滤镜”。

### C. 原本保留的 breakout-short asymmetric 残余仍然存在，但不够长成 23b
- `research/quant_digests/2026-03-23_0349_intraday-vol-commonality-asymmetric-followup-gate.md`

它继续支持：
- 波动共振更像 breakout-short 的 asymmetric follow-up 层；
- 但这条线已经更像应并入 breakout-short 主线，而不是在 Rank 23 名下单列新 rank。

## 4) 最值得改的唯一一刀是什么？
如果只保留 **1 条唯一主修改轴**，本轮最诚实的一刀是：

**停止把 volatility-state 继续包装成 shared allow/deny gate；承认它当前更适合被改写成独立 raw-alpha pocket（如 high-RV interaction / path-state alpha），或并入 breakout-short 的 setup-specific follow-up。**

但这条“一刀”**不值得写成 `Rank 23b`**，因为：
1. 这不是在救原 Rank 23，而是在承认“volatility 主题该换职责层”；
2. 一旦写成 `23b`，很容易把“新 family / 新 alpha pocket”误包装成“旧 gate 的窄派生”；
3. 这会削弱原 `park` verdict 的审计意义。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

最终 verdict：`keep_park`

原因：
1. 原 `park` 的 blocker 没被推翻：作为 `shared vol/regime gate`，它仍然没有诚实 uplift。
2. 新证据虽然保留了 volatility 信息的价值，但价值越来越清楚地落在：
   - `high-RV` interaction raw alpha，或
   - `path-shape / path-state` raw alpha，或
   - breakout-short 的 setup-specific follow-up。
3. 这些都不是原 Rank 23 可继续诚实派生的单轴 `23b`；硬写只会模糊“原 rank 已被审计否掉的是哪一层”。

## 6) 本轮固定问题回答
1. **原 rank 为什么 park？**
   - 因为 `rv_midband / no-high-vol-extreme` 作为 `15m shared gate` 只做到少亏，没形成跨资产、时间、参数、成本都站得住的 uplift。
2. **它更像 hard park 还是 soft park？**
   - `soft park`，但比上次更偏硬。
3. **有没有可救信号？**
   - 有；但主要是 volatility 主题应转向 `high-RV interaction`、`path-state raw alpha` 或 breakout-short 的 asymmetric follow-up，而不是继续救 Rank 23 本身。
4. **最值得改的唯一一刀是什么？**
   - 停止把 volatility-state 当 shared gate，改承认它更适合 raw-alpha pocket / setup-specific follow-up 角色。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 23b`？**
   - 因为那会把“主题换职责层 / 换赛道”误包装成原 Rank 23 的窄派生，不够诚实。

## 7) 允许的最终结论
- `keep_park`

## 8) 最小审计结论
- 原 `park` 保留；
- `Rank 23` 本轮仍读作 **soft park，但偏硬，而且比 2026-03-24 那次更偏硬**；
- 它留下的不是值得单独派生 `Rank 23b` 的 queue-facing 假设，而是一个应转交给新 raw-alpha family / breakout-short 主线吸收的 volatility-theme 残余。

## 9) 相关证据锚点
- `research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`
- `research/park_reframe/2026-03-24_0607_rank23-park-reframe.md`
- `research/quant_digests/2026-03-23_0349_intraday-vol-commonality-asymmetric-followup-gate.md`
- `research/quant_digests/2026-03-25_1323_xs-interactions-highrv-loser-reversal.md`
- `research/quant_digests/2026-03-26_1633_intraday-curve-shape-remainder-swing.md`

## 10) Git
- 未 commit。
- 原因：workspace 当前存在大量与本轮无关的脏文件；本轮只做 park-reframe 所需最小文本更新，不安全混提。
