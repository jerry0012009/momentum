# 2026-03-23 11:15 UTC · Rank 27 park reframe 低频复核

## 本轮对象
- `Rank 27`
- 本轮结论：`keep_park`
- 原 verdict 保留：`park`

## 为什么这轮看它
- `Rank 27` 上次 park-reframe 是 `2026-03-18 02:29 UTC`，已不是“刚复盘完又立刻重刷”。
- 且最近确实出现了两条相关新证据：
  1. `2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md`
  2. `2026-03-22_2258_bounce-polarity-not-shared-gate.md`
- 因此这轮不是无新证据重复咀嚼，而是检查：这些新证据是否足以在 **不推翻原 park 审计意义** 的前提下，再派生一条新的窄 reframe hypothesis。

## 原 Rank 为什么 park
先回到原始审计：
- `2026-03-17_0815_rank27-mtgox-neckline-clean-replication.md` 给出的结论很清楚：
  - `raw_breakout`：`mean_total_return≈-13.79%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈71.56%`
  - `neckline_confirm`：`mean_total_return≈-17.42%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈62.50%`
  - `neckline_confirm_plus_retest_hold`：`mean_total_return≈-3.03%`，`positive_asset_ratio=0/3`，`mean_false_break_ratio≈68.67%`
- 原 park 的核心不是“主题完全没信息”，而是：
  - `neckline_confirm` 虽然压了一些假突破，但收益更差；
  - `retest_hold` 虽能收窄亏损，但没有同时带来足够干净的假突破改善；
  - 结果仍不足以形成跨资产、成本后的可保留 alpha。

## 它更像 hard park 还是 soft park
- 本轮判断：**偏 soft park**。
- 原因：
  - `Rank 27` 不是“完全没有残余信息”；
  - 它更像是 **结构 breakout 主题仍可能有一点信息，但原来的 retest 定义太硬、角色也偏粗**；
  - 不过，这一点残余信息在 `Rank 27b` 那一刀里其实已经被诚实消费过一遍。

## 有没有“可救信号”
有，但很有限，而且已基本被现有派生吸收：

### 1) 已知可救信号：ATR 弹性回踩区 + bounce reclaim
`2026-03-18_0402_rank27b-atr-zone-park.md` 已经验证过：
- `atr_zone_bounce_reclaim`：
  - `mean_total_return≈-3.14%`
  - `positive_asset_ratio≈33.33%`
  - `mean_false_break_ratio≈58.42%`
  - `mean_trades≈66.3`
- 读法：
  - 这说明 **静态 retest_hold` -> `ATR 弹性回踩区 + bounce reclaim`** 这刀确实有信息；
  - 它主要改善在 **假突破率更低**，而不是把策略真正救活；
  - 所以它只够支持 `Rank 27b` 作为已审计过的窄派生，不够继续往外长第二条新枝。

### 2) 新证据 1：retest 更像 phase，不像独立 hard gate
`2026-03-23_0205_orb-phase-retest-score-not-hard-gate.md` 的价值在于进一步确认：
- 更值得偷的是 `breakout -> retest -> bounce + score` 的状态机骨架；
- 不该把 `retest_hold` 单独写成独立 hard gate。

但这条证据的方向，与 `Rank 27b` 并不冲突，反而是：
- 它继续支持“回踩确认应该更弹性、更状态机化”；
- 这本质上是在 **收紧 Rank 27b 的实现边界**，不是打开一条新的单独修改轴。

### 3) 新证据 2：bounce candle polarity 不值得再加成 hard gate
`2026-03-22_2258_bounce-polarity-not-shared-gate.md` 的价值在于排除一个看似自然、实际不值钱的小审美：
- `same-direction body` 更像 late-chase；
- 不适合升成 shared hard gate。

这条证据同样没有产生新的 Rank 27c 方向，反而只是告诉我们：
- **别在 Rank 27b 上再顺手叠一层“bounce 必须实体同向”的第二轴。**

## 最值得改的唯一一刀是什么
- 如果今天重新问“Rank 27 最值得改的唯一一刀是什么”，答案**仍然还是旧答案**：
  - **把静态 `neckline retest_hold` 改成 `ATR-scaled retest zone + bounce reclaim`。**
- 这刀已经以 `Rank 27b` 的形式被提出并做过最小诚实检查。
- 本轮没有出现比它更值得、且不与其重叠的新单轴。

## 是否值得形成新的 derived hypothesis
- 结论：**不值得。**
- 原因：
  1. 原 Rank 的残余信息已经主要被 `Rank 27b` 消费；
  2. 这两天的新证据更像是在提醒“别把 retest 再写硬、别再叠 bounce polarity 审美”，属于**实现纪律收紧**；
  3. 若现在硬写 `Rank 27c`，大概率会滑向：
     - 把 `phase state machine + score` 当第二轴大改；或
     - 在 `27b` 上继续叠 `VWAP / RVOL / score / same-body` 等多层过滤；
     这违反本 loop 的“每轮最多 1 条唯一主修改轴”要求。

## 本轮最终判断
- `Rank 27` 原 park 继续保留。
- 当前分类：`soft park`
- `可救信号`：有，但主要已体现在 `Rank 27b`。
- `唯一主修改轴`：仍是既有 `Rank 27b = ATR-scaled retest zone + bounce reclaim`。
- 本轮 verdict：`keep_park`
- 不新增 `Rank 27c`。

## 对 bot2 / bot3 的含义
- 不改 `docs/TODO.md` 顶部排班。
- 不新分配任务。
- 仅把 queue 读法更新为：
  - `Rank 27` 仍是 soft park；
  - 最近新证据只够强化既有 `Rank 27b` 的边界纪律，不足以再派生 `Rank 27c`。

## 本轮产出
- 新日志：`research/park_reframe/2026-03-23_1115_rank27-park-reframe.md`
