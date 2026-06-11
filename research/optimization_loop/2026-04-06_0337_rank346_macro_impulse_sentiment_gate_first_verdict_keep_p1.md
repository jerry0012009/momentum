# 2026-04-06 03:37 UTC · Rank 346 / scheduled-macro impulse × pre-event sentiment gate / first verdict keep_P1

## 本轮对象
- Target: `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`
- Frozen name: `Rank 346 / scheduled-macro impulse × pre-event sentiment gate`
- 当前层级动作：`fresh intake -> keep_P1`

## 这轮要回答的问题
这条材料到底是不是新的前排对象：它是否已经把 `scheduled macro announcement -> post-event first-reaction continuation` 说成一个独立 raw alpha 壳，并把 `pre-event sentiment` 诚实地压在 admission / sizing gate 角色；还是说它本质仍只是旧的 `FOMC/CPI blackout / macro gate` 家族换包装？

## 结论
回答：**值得保留为新的 `P1 / surviving candidate`，但暂时只到 `keep_P1`，还不够直接升 `P2`。**

一句话原因：**这条线的主语已经从“事件来了先别做”切成“事件后第一反应是否存在可跟随的短窗 alpha，而 sentiment 只决定值不值得参与”，它和既有 `FOMC event-clock veto` / `Fed-CPI repricing vol gate` 不是同一个对象；但当前可移植证据仍主要停在 `FOMC-only reaction magnitude split`，尚未把 `FOMC/CPI/NFP/PCE` 分类别的 `1m/3m/5m/15m after-cost follow-through` 压实。**

## 为什么这次不是旧 overlay 的重复
1. **对象主语不同。**
   - `Rank 175 / FOMC event-clock veto + size-down overlay` 的主语是：scheduled macro release 会破坏常态执行假设，所以该 veto / size-down。
   - `Rank 306 / Fed/CPI repricing × shared volatility regime gate` 的主语是：宏观赔率重定价能给现有策略一个上层 volatility regime gate。
   - 这次 digest 的主语则是：**announcement-time impulse 本身可能形成 event-driven raw alpha 壳；pre-event sentiment 只是 admission / amplitude gate。**
   这不是旧 gate 的 wording 升级，而是从“别做”转成“何时可以 selective participation”。

2. **方向生成机制也不同。**
   digest 明确把方向绑定在 `post-event first reaction`，不是用 sentiment 或事件类别去 pre-event 盲猜 sign。也就是说，这条线不是宏观解释层，更像：
   - `raw alpha`：release 后第一段真实冲击是否有 follow-through；
   - `gate`：pre-event sentiment 决定 admission threshold / size。

3. **它补的是当前研究池里稀缺的外生 event-time alpha 壳。**
   现有池子里已有不少 `FOMC/CPI` veto / blackout / macro gate；但把 scheduled macro event 直接写成 `event-driven continuation shell` 的材料还没有正式前排身份。仅从对象独立性看，它值得拿一个新 `Rank`。

## 为什么这轮还不能直接升 P2
当前证据还缺 3 个 admission 必需件：

1. **effectiveness / expected return 还没压成 after-cost pocket。**
   digest 目前最硬的 portability 只做到：`18` 次 FOMC 上，Fear & Greed bucket 会改变 `post-event 1h absolute return / volume ratio`。这证明了 reaction magnitude 被 sentiment 调节，但**还没证明 `sign(r0) * r1` 在 taker 成本后稳定大于 0**。

2. **cross-event portability 还没过。**
   论文摘要说 announcement category 不同会系统变化，但本地快检仍基本停在 `FOMC-only`。在没把 `CPI / NFP / PCE` 拆开前，不能把这条线写成已经具备 admission 资格的 event sleeve。

3. **honesty 角色虽然讲清，但 execution shell 还没压实。**
   digest 已经很诚实地避免了 `pre-event sentiment -> sign` 的过拟合叙事，这点是优点；但真正 desk 需要的是：
   - `1m/3m/5m/15m` 哪个窗口能跟；
   - `delay 0 / delay 1 bar` 后净值是否仍活；
   - 事件后第一分钟冲击成本会不会把 gross 全吃掉。
   这些还没给答案。

## 这轮最合理的 first verdict
因此，本轮 first verdict 不该把它打回 background：
- 若打回去，会把“raw alpha 主语已独立”与“admission 证据还没补完”混成一回事；
- 更诚实的写法是：**承认它是一个 distinct 的新对象，但只配先留在 `P1`。**

## 唯一 survivor follow-up 应该测什么
下一次唯一 follow-up 不该再重复证明“它不是 overlay”，而该直接收口成一个 decisive admission check：

**按事件类别拆桶，测 `BTC/ETH × FOMC/CPI/NFP/PCE × 1m/3m/5m/15m` 上的 `post-event first-reaction continuation` 是否在 taker / delay 口径下仍保留净跟随空间；同时只把 sentiment 当 threshold / size gate，不让它承担 sign 预测。**

如果这一步压不出 `after-cost` 跟随口袋，它就应诚实退回 `background / P0`；若能压出至少一条窄而诚实的 event sleeve，再讨论升 `P2`。

## 本轮落地结论
- 分配新正式身份：`Rank 346`
- 层级：`fresh intake -> keep_P1`
- 进入：`Surviving candidate slot`
- 不进入 `P2` 的原因：缺少按事件类别拆开的 `after-cost follow-through` 证据

## 会改变系统认知的一句话
`Rank 346 / scheduled-macro impulse × pre-event sentiment gate` 不是旧的 `FOMC/CPI blackout` 或 `macro vol gate` 改写，而是一条独立的 event-driven raw alpha 壳；但当前本地证据仍主要停在 `FOMC-only reaction magnitude split`，尚未压实分事件类别的 `1m/3m/5m/15m after-cost follow-through`，因此 first verdict = `keep_P1`，进入 survivor。