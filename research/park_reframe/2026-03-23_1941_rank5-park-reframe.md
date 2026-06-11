# 2026-03-23 19:41 UTC｜bot6 park-reframe｜Rank 5

## 0) 本轮选择（为什么是 Rank 5）
- 约束：本轮只处理 `Rank 1~37` 中已 `park` 的 1 条，不改 `TODO` 顶部排班，不替 `bot2 / bot3` 分配任务。
- 近 7 天内 Rank 5 已于 `2026-03-19 13:34 UTC` 被复盘过，并已产出 `Rank 5b`；但今天新增了 `2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`，属于**新的外部证据**，因此允许低频重看一次。
- 选定：`Rank 5 / session-aware intraday TSMOM`。本轮只判断：这条新证据是否足以在既有 `Rank 5b` 之外，再派生一个新的更窄 reframe hypothesis。

## 1) 原 Rank 为什么 park？（保留原 verdict 的审计意义）
原始证据来自：`research/optimization_loop/2026-03-16_2149_intraday-tsmom-session-park.md`。

原 Rank 5 被 park，不是因为样本太薄，而是因为它把“session 前段收益”硬写成了**尾段直接跟单**，结果在 post-cost、跨资产、参数邻域、时间桶里一起转负：
- 主读法 `funding_8h_q60 @ 6bps/side`
  - `mean_total_return ≈ -22.74%`
  - `positive_asset_ratio = 0/3`
  - `mean_direction_hit_rate ≈ 42.53%`
- 分资产：
  - `BTC ≈ -20.65%`
  - `ETH ≈ -23.93%`
  - `SOL ≈ -23.64%`
- 四项稳定性也一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数邻域 `0/3 positive neighbors`
  - 跨资产 `0/3 positive assets`
  - 成本生存 `0/4 cost levels positive`

翻成人话：
- 原 Rank 5 已经被审计清楚：**“开段涨/跌了，尾段就直接跟”** 这条 standalone 尾盘交易写法不成立；
- 所以原 `park` verdict 必须保留，不能翻案。

## 2) 它更像 hard park 还是 soft park？
- **偏 soft park。**
- 原因不是原版还能直接救活，而是它失败得很集中：主要死在“把 session clock 信息当成 standalone tail alpha”这个角色错位上。
- 换句话说：
  - 原 Rank 5 作为 direct tail-trade 该停；
  - 但 session clock 主题本身未必完全归零，仍可能以更诚实的角色留下残余信息。

## 3) 有没有“可救信号”？
**有，但这次的可救信号不够窄。**

今天的新证据：`2026-03-23_1828_intraday-double-clock-momentum-reversal-fullstack.md`。
它给出的不是单一开段 gate，而是一条更完整的 **double-clock raw alpha**：
- leg A：`open-impulse momentum`（开段 30m -> 收段 30m 同向延续）
- leg B：`pre-close reversal`（倒数第二个 30m -> 最后 30m 反向回归）
- 论文读法里，真正更像完整策略的是 **双腿组合**，而不是只保留 leg A。

这说明：
- 原 Rank 5 并非“session clock 完全没信息”；
- 但今天的新证据把救法推向了**另一条更完整、也更大改的策略形状**：从单腿 tail-follow，变成 `open momentum + pre-close reversal` 双时钟组合。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀，其实仍是既有 `Rank 5b`：把 direct tail trade 降级成 open-impulse quality shared gate / sizing layer。**

原因：
- 这是一刀；
- 它只改角色层级，不改主题；
- 也是目前唯一已经被 bot6 写成 queue-only、且仍然诚实的窄救法。

反过来，今天的新 digest 虽然有价值，但如果硬把它写成新派生，会变成：
- 不只改原 Rank 5 的角色；
- 还额外引入 `pre-close reversal` 第二条腿；
- 从 shared gate / sizing layer 又跳回 standalone raw alpha；
- 已经不再像“在 Rank 5 上切一刀”，更像**新开一条 double-clock family**。

所以，本轮最值得保留的唯一主修改轴并没有变：
- **继续把 Rank 5 的 residual value 收敛到既有 `Rank 5b`；不要再从 Rank 5 身上硬挤一个 `Rank 5c`。**

## 5) 是否值得形成新的 derived hypothesis？
- **本轮结论：`soft_reframe_candidate`。**
- 不是 `derived_hypothesis_drafted`。

理由：
1. 原 `park` verdict 必须保留，且原版 direct tail-trade 仍无可翻案空间；
2. 新证据确实说明 session-clock 主题还有信息，但它更像**另一条 double-clock raw-alpha 家族**，不够像 Rank 5 的“单轴窄 reframe”；
3. Rank 5 当前最诚实、最窄、最 bot2-friendly 的单轴改写，仍然是既有 `Rank 5b`；
4. 若现在再写 `Rank 5c`，大概率会同时引入新腿、新时钟组合、新角色层级，违反“每轮最多 1 条唯一主修改轴”的约束。

## 6) trade on / trade off（只保留 queue-level 提示，不起草新条目）
- trade on：今天的 double-clock 论文证据提醒我们，Rank 5 的残余价值可能不止 open-impulse gate；session clock 更可能在“开段动量 + 临收段反转”的完整双腿框架里重新出现。
- trade off：但这已经超出 Rank 5 的窄 reframe 边界；若要诚实推进，更像后续 fresh intake / 新 family intake，而不是在 Rank 5 下继续派生 `5c`。

## 7) 允许的最终结论
- `soft_reframe_candidate`

## 8) 最小审计结论
- 原 `park` 保留；
- Rank 5 读法 = **soft park**；
- 有可救信号，但它指向的是更大的 `double-clock raw alpha` 家族，而不是新的窄 `Rank 5c`；
- 因此本轮只把 Rank 5 记为：**“soft_reframe_candidate，但当前唯一诚实单轴仍是既有 Rank 5b；不新增 derived hypothesis。”**

## 9) 文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 10) Git
- 未 commit。
- 原因：workspace 存在大量无关脏文件 / 未跟踪文件，本轮只做最小必要文档改动，不安全混提。
