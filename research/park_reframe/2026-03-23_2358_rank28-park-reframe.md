# 2026-03-23 23:58 UTC｜bot6 park-reframe｜Rank 28

## 0) 本轮选择（为什么是 Rank 28）
- 约束：本轮只处理 `Rank 1~37` 中已 `park` 的 1 条，不改 `TODO` 顶部排班，不替 `bot2 / bot3` 分配任务。
- 轮转上，`Rank 1~37` 里大多数 parked rank 最近 7 天都已被 bot6 扫过；本轮优先找**不是今天刚复盘**、且有**新旁证**的对象。
- 选定：`Rank 28 / cross-market intraday leader-laggard TSMOM`。
- 允许重看的新证据：
  - `research/quant_digests/2026-03-23_2008_same-clock-crosssectional-momrev-marketneutral-raw-alpha.md`
- 本轮只回答一件事：这条新证据，是否足以在既有 `Rank 28b` 之外，再诚实派生一个新的窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？（保留原 verdict 的审计意义）
原始证据来自：
- `research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`
- `research/park_reframe/2026-03-19_0433_rank28-park-reframe.md`

原 Rank 28 被 park，不是因为“跨市场 / 跨币相对强弱”完全没信息，而是因为它被写成了一个**同 session 里 leader 先动、laggard 尾段跟随**的直接交易模型，而这条 direct lag-trade 在最小 clean replication 里持续为负：
- primary `funding_8h_q60 @ 6bps/side`
  - `mean_total_return ≈ -16.58%`
  - `positive_asset_ratio = 0/3`
  - `mean_false_follow_ratio ≈ 66.42%`
  - `mean_trades ≈ 124`
- 相对最不差的 `utc_day_q70 @ 6bps/side` 也仍约 `-5.28%`、`0/3` 资产为正
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3`
  - 参数稳定性 `0/3`
  - 跨标的稳定性 `0/3`
  - 成本稳定性 `0/4`

翻成人话：
- 原 Rank 28 不是没样本；
- 是**有样本，但“谁先动就追谁的 laggard”这条交易形状不赚钱**；
- 所以原 `park` verdict 必须保留，不能翻案。

## 2) 它更像 hard park 还是 soft park？
- **偏 soft park。**

原因：
- `hard` 的部分：direct `leader -> laggard follow-through` 这条 standalone 交易写法已经被 clean replication 审计清楚，应该停；
- `soft` 的部分：cross-market relative-strength / breadth 主题本身未必彻底没信息，更可能是**角色放错了**。

也正因如此，3 月 19 日已经形成过一条足够窄的派生：
- `Rank 28b = 把 cross-market intraday leader-laggard 从 direct lag-trade，降级成 alt-vs-BTC RS breadth shared regime gate`

## 3) 有没有“可救信号”？
- **有，但这次的新信号更像另一条 raw-alpha 家族，不够像 Rank 28 的第二条窄 reframe。**

今天的新旁证 `2026-03-23_2008_same-clock-crosssectional-momrev-marketneutral-raw-alpha.md` 给出的关键信息是：
1. 主题仍然和 intraday clock / 横截面相对表现有关；
2. 但真正更像可交易对象的，不是“leader 先动、laggard 尾段补涨/补跌”，而是**same-clock 横截面短反转 + 长动量**的 market-neutral raw alpha；
3. 它要求的交易形状、组合方式、风险预算都已经明显变成**一条独立的横截面相对价值策略骨架**。

这说明：
- 原 Rank 28 并非“cross-market clock 信息完全无效”；
- 但今天的新证据并没有指向 Rank 28 内部的另一条小修小补；
- 它更像在说：**如果要继续做这类信息，应该去开一条 same-clock cross-sectional market-neutral 新家族，而不是在 Rank 28 下继续挤一个 `28c`。**

## 4) 最值得改的唯一一刀是什么？
- **本轮最值得保留的唯一一刀仍然是既有 `Rank 28b`：把 direct lag-trade 降级成 alt-vs-BTC RS breadth shared regime gate。**

原因：
- 这仍是最窄、最诚实、最符合 bot6 单轴纪律的改写；
- 它只改角色层级，不改主题；
- 今天的新 digest 虽然重要，但它把问题推向了另一条更完整的 market-neutral raw alpha 骨架，已经超出“在 Rank 28 上切一刀”的边界。

换句话说：
- 现在若硬写 `Rank 28c`，大概率会同时引入：
  - same-clock 横截面排序
  - market-neutral 组合加权
  - 短反转 + 长动量双腿
  - 新的执行与容量约束
- 这已经不是窄 reframe，而是**新 family intake**。

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`soft_reframe_candidate`。**
- 不是 `derived_hypothesis_drafted`。

理由：
1. 原 `park` verdict 必须保留，direct lag-trade 仍无翻案空间；
2. 新证据确实说明 intraday cross-market / cross-sectional clock 信息还有价值；
3. 但这份价值更像另一条 `same-clock market-neutral raw alpha` 新家族，而不是 Rank 28 的第二条窄 reframe；
4. Rank 28 当前最诚实、最窄、最 bot2-friendly 的单轴改写，仍然是既有 `Rank 28b`；
5. 若现在再写 `Rank 28c`，会越过“唯一主修改轴”边界，变成在旧 rank 名下偷开新主线。

## 6) trade on / trade off（只保留 queue-level 提示，不起草新条目）
- trade on：今天的 same-clock 横截面证据提醒我们，Rank 28 失败后留下来的残余价值，可能不止 breadth/context；跨币 intraday clock 信息更可能在 **market-neutral 横截面短反转 + 长动量** 框架里重新出现。
- trade off：但这已经超出 Rank 28 的窄 reframe 边界；若要诚实推进，更像后续 fresh intake / 新 family intake，而不是在 Rank 28 下继续派生 `28c`。

## 7) 允许的最终结论
- `soft_reframe_candidate`

## 8) 最小审计结论
- 原 `park` 保留；
- Rank 28 读法 = **soft park**；
- 有可救信号，但它指向的是更大的 `same-clock cross-sectional market-neutral` 新家族，而不是新的窄 `Rank 28c`；
- 因此本轮只把 Rank 28 记为：**soft_reframe_candidate，但当前唯一诚实单轴仍是既有 Rank 28b；不新增 derived hypothesis。**

## 9) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) Git
- 未 commit。
- 原因：workspace 存在无关脏文件 / 未跟踪文件；本轮只做最小必要文档改动，不安全混提。
