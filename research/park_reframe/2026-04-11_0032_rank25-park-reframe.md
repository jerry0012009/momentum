# 2026-04-11 00:32 UTC · Rank 25 park reframe

## 本轮对象
- `source_rank`: `Rank 25`
- 原题：`EMA + Donchian breakout`
- 本轮结论：`keep_park`
- 原 `park` verdict：**保留，不推翻**

## 这轮为什么重新看 Rank 25
- 距离上一次 `Rank 25` 的 park-reframe 低频复盘（`2026-04-01 23:32 UTC`）已超过 7 天；
- 过去几天又新增了两类与 breakout 主题相关的新证据：
  1. `2026-04-08` 的 `ATR-switched price-velocity × volume-expansion breakout shell`；
  2. `2026-04-10` 的 `venue liquidity fragility × breakout / fade router`；
- 需要判断这些新增证据，是否足以从旧 `Rank 25` 再诚实派生一条新的窄 reframe，而不是重复既有 `Rank 25b / 25c`。

## 原 rank 为什么 park
原 `Rank 25` 并不是因为 breakout 主题彻底失效才 park。

已读材料显示：
- `2026-03-17` 的 clean replication 里，`l30_c3` 在低成本下仍留有正 aggregate，跨 `BTC/ETH/SOL` 也并非先在 cross-asset 上整体塌掉；
- 真正把它压回 park 的 blocker 很集中：**时间结构不稳**。
- 具体表现是参数邻域反复出现：`bucket_1 负 / bucket_2 正 / bucket_3 负`，说明这条 `EMA + Donchian` 同层 co-trigger 写法更像只在中段时窗偶然成立，而不是一条跨时间段都诚实站得住的 continuation pocket。

所以原 rank 被 park，主因不是“成本一上就死”或“跨资产全灭”，而是：
**把 EMA 和 Donchian breakout 绑成同层共触发后，时间稳定性不足。**

## 这更像 hard park 还是 soft park
结论：**仍是 soft park，但比 4 月初更接近 hard park。**

原因分两层：
1. 原始失败结构仍然是 `soft-park` 型：
   - breakout 主题本身没被完全证伪；
   - 真正出问题的是职责分工与时间结构，而不是整个 family 在成本/参数/跨资产上同步归零。
2. 但到今天，它已经**明显向 hard 靠**：
   - `Rank 25b`（30m regime allow/deny）和 `Rank 25c`（EMA 降级为 HTF context gate）这两条最自然、最诚实的单轴残余，都已经被显式提出来了；
   - 其中 `Rank 25c` 还进一步被 fresh intake 成 `Rank 245`，随后在 `2026-03-30` survivor follow-up 里回到 `background / P0`；
   - `2026-04-09` 的 `Rank 25c fresh intake first verdict` 也已经把这条 residual 说死：它仍更像旧 breakout family 的岗位重写提案，而不是一条已站住的新 raw alpha。

因此，`Rank 25` 现在仍不能算真正的 hard park，但它的**可救残余已经被消费得很深**。

## 有没有“可救信号”
有，但只剩两类，而且都**不足以支持新的 Rank 25d**。

### 1) 已被消费过的可救信号
最强、也最诚实的可救信号，仍是旧结论里已经识别出的那条：
- **EMA 不该和 Donchian breakout 平级共触发；EMA 更像 HTF context gate。**

这条信号已经：
- 在 `2026-03-23` 被写成 `Rank 25c`；
- 在 `2026-03-30` 被 fresh intake 成 `Rank 245`；
- 又在后续 first verdict / follow-up 中被压回 `background / P0`。

也就是说，**它不是不存在，而是已经被认真消费过了。**

### 2) 新增 breakout 证据留下的“主题未死”信号
`2026-04-08` 与 `2026-04-10` 的新增 digest 确实说明：
- breakout / continuation 主题仍然有信息量；
- 但更诚实的写法越来越像：
  - `ATR-switched velocity × volume-expansion breakout shell` 这样的**新 raw-alpha 宿主**；
  - 或 `liquidity fragility × breakout / fade router` 这样的**shared regime/router 宿主**。

这两条都说明“breakout family 没死”，但它们不再对着旧 `Rank 25` 的唯一 blocker 下刀；
它们是在把 breakout 主题**抬升到新的 shell / router family**，而不是把旧 `EMA + Donchian` 这条写法救回来。

## 最值得改的唯一一刀是什么
如果硬要说还有唯一值得保留的一刀，**答案仍然不是新的一刀，而是旧的一刀**：

> **把 EMA 从同层 co-trigger 降级成 HTF context-only gate，保留 Donchian breakout 为唯一主触发。**

但这条轴：
- 已经被 `Rank 25c` 明确起草；
- 也已经通过 `Rank 245` 的 fresh intake / follow-up 被实际消费；
- 并没有留下足够强的新增 after-cost / time-structure 事实，支持今天再包装成新的 `Rank 25d`。

因此，本轮最诚实的结论不是再提一刀，而是：
**旧的一刀已经试过、也已经消耗完当前证据预算。**

## 是否值得形成新的 derived hypothesis
结论：**不值得。**

### 为什么不值得新增 `Rank 25d`
1. **最自然的残余轴已被既有 `25b / 25c` 吸收。**
   - `25b` 解决环境许可层；
   - `25c` 解决 EMA 岗位错位；
   - 再往下切，很容易变成只是对旧 `25c` 做 wording 变体。

2. **`25c -> Rank 245` 已经实际走过一轮“fresh intake -> background”闭环。**
   - 这说明旧 residual 不是没被试，而是已经被 honest 地推进过；
   - 当前没有新 desk-facing 事实，能证明这条 residual 今天值得重新排回前排。

3. **4 月新增证据把 breakout 主题推向了新宿主，而不是旧 Rank 25 的窄派生。**
   - `ATR-switched velocity-volume breakout shell` 更像新的 breakout raw-alpha；
   - `liquidity fragility router` 更像 breakout / fade 的 shared regime；
   - 它们都不是旧 `EMA + Donchian` 这条线的单轴窄修补。

## bot6 本轮最终判断
- 保留原 `Rank 25 = park` 的审计意义；
- 维持它是 **soft park，但继续向 hard park 靠** 的判断；
- 本轮**不新增** `Rank 25d`、`Rank 25 reframe` 或其他新派生；
- 若未来还有 reopen 理由，也仍应优先来自：
  - 已有 `Rank 25c / Rank 245` 的新 decisve evidence，或
  - 一个与 `25b / 25c` 明显不同、且能直接回答原 `time red-watch` blocker 的新单轴证据；
- 在此之前，更诚实的写法是：
  **旧 Rank 25 保持 park，breakout 主题的新增价值应去新的 shell / router family 承载，而不是继续从 Rank 25 再切出一个 `25d`。**

## 一句话结论
`Rank 25` 仍是 soft park，但 residual 已被 `25b / 25c / Rank 245` 基本消费；4 月新增 breakout 证据继续把主题抬升到新的 shell / router family，而不是支持从旧 `EMA + Donchian` 再诚实派生一个 `Rank 25d`，因此本轮结论为 `keep_park`。
